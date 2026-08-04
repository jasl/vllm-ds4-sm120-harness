#!/usr/bin/env bash
# Promotion validation Phase A (correctness + perf) for the rebased PR head on RTX SM120.
# Config A = the shipped default: MXFP4, MTP2 on, decode-opt OFF, FULL_AND_PIECEWISE
# (breakable cudagraph auto-enables for DSv4 -> exercises the #45309 fix), fp8 KV.
# One serve; all gates attach via BASE_URL. Gates:
#   - trivial-prompt arithmetic (2+2 / 7*8 / capital-of-France) = breakable-cudagraph correctness
#   - GSM8K 5-shot limit-200 (run_lm_eval.sh)          = accuracy gate
#   - jasl/vllm#19 instruction-following (JSON-only)   = user-report regression gate
#   - arthur long-context coherence (LINE_COUNT 280)   = user-report regression gate
#   - prefill 8k + decode ctx0 sweep                   = perf snapshot (regression check)
set -uo pipefail
WT="${1:-/home/jasl/tmp/vllm-rebased-dev-20260614}"
GLIM="${2:-200}"
VENV=/home/jasl/tmp/vllm-lucifer-pr3395-venv-20260614
HARNESS=/home/jasl/tmp/ds4-sm120-harness
MODEL=deepseek-ai/DeepSeek-V4-Flash-0731; SERVED=DS4
HOST=127.0.0.1; PORT=8000
LMBENCH=/home/jasl/tmp/llm_decode_bench.py
ROOT=/home/jasl/tmp/promotion_phaseA/$(date +%Y%m%d%H%M%S); mkdir -p "$ROOT"
echo "=== PROMOTION Phase A (config A: MXFP4 MTP2 decode-opt-off FULL_AND_PIECEWISE)  wt=$(basename "$WT") -> $ROOT ==="
cd "$WT"; echo "checkout: $(git rev-parse --short HEAD) $(git log -1 --format=%s | cut -c1-46)"
PASS=1; note(){ echo "  [$1] $2"; [ "$1" = FAIL ] && PASS=0; return 0; }

stop_vllm(){ pkill -TERM -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 8; pkill -KILL -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 3; rm -f /dev/shm/psm_* 2>/dev/null || true; }
trap stop_vllm EXIT INT TERM
stop_vllm
echo "--- serve config A ---"
( PATH=/usr/local/cuda/bin:$VENV/bin:$PATH PYTHONPATH=$WT PYTHONSAFEPATH=1 \
  VLLM_LOGGING_LEVEL=INFO VLLM_ENGINE_READY_TIMEOUT_S=3600 CUDA_VISIBLE_DEVICES=0,1 \
  VLLM_FLASHINFER_BYPASS_VERSION_CHECK=1 FLASHINFER_DISABLE_VERSION_CHECK=1 VLLM_USE_FLASHINFER_SAMPLER=1 \
  nohup "$VENV/bin/vllm" serve "$MODEL" --served-model-name "$SERVED" \
    --trust-remote-code --host "$HOST" --port "$PORT" --tensor-parallel-size 2 \
    --kv-cache-dtype fp8 --block-size 256 --gpu-memory-utilization 0.90 --max-model-len 32768 \
    --max-num-seqs 64 --max-num-batched-tokens 8192 --max-cudagraph-capture-size 64 \
    --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
    --async-scheduling --enable-chunked-prefill --enable-flashinfer-autotune \
    --speculative-config.method mtp --speculative-config.num_speculative_tokens 2 \
    --tokenizer-mode deepseek_v4 > "$ROOT/serve.log" 2>&1 & echo $! > "$ROOT/pid" )
sp=$(cat "$ROOT/pid"); ok=0
for i in $(seq 1 240); do
  kill -0 "$sp" 2>/dev/null || { echo "SERVE DIED"; tail -25 "$ROOT/serve.log"; break; }
  [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HOST:$PORT/health 2>/dev/null)" = 200 ] && { ok=1; echo "serve UP ~$((i*10))s"; break; }
  grep -qaE 'Engine core initialization failed|CUDA error|No available memory|died unexpectedly' "$ROOT/serve.log" 2>/dev/null && { echo "SERVE ERROR"; grep -aiE 'error|No module|assert' "$ROOT/serve.log"|tail -8; break; }
  sleep 10
done
[ "$ok" = 1 ] || { note FAIL "config-A serve failed to come up"; exit 92; }
echo "  breakable cudagraph: $(grep -aoiE 'Breakable CUDA graph enabled|Auto-enabling VLLM_USE_BREAKABLE_CUDAGRAPH' "$ROOT/serve.log" | head -1)"
echo "  MTP: $(grep -aoiE 'Speculative|num_speculative|mtp' "$ROOT/serve.log" | head -1)"

# 1) trivial-prompt arithmetic (breakable cudagraph correctness, the #45309 fix)
echo "--- gate: trivial-prompt arithmetic (chat endpoint, thinking off, greedy) ---"
ask(){ curl -s --max-time 60 http://$HOST:$PORT/v1/chat/completions -H 'Content-Type: application/json' \
  -d "{\"model\":\"$SERVED\",\"messages\":[{\"role\":\"user\",\"content\":\"$1\"}],\"max_tokens\":40,\"temperature\":0,\"chat_template_kwargs\":{\"thinking\":false}}" 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin)['choices'][0]['message']['content'].strip().replace(chr(10),' '))" 2>/dev/null; }
a1=$(ask "What is 2+2?"); a2=$(ask "What is 7 times 8?"); a3=$(ask "What is the capital of France? One word.")
echo "    2+2 -> [$a1] | 7*8 -> [$a2] | capital France -> [$a3]"
echo "$a1"|grep -q 4 && echo "$a2"|grep -q 56 && echo "$a3"|grep -qiE "paris" && note PASS "arithmetic correct (no #45309 garbage)" || note FAIL "arithmetic wrong (possible cudagraph garbage)"

# 2) GSM8K limit-200
echo "--- gate: GSM8K 5-shot limit-$GLIM ---"
( cd "$HARNESS"; PYTHON="$VENV/bin/python" LM_EVAL_BIN="$VENV/bin/lm_eval" \
   MODEL="$SERVED" BASE_URL="http://$HOST:$PORT" HOST="$HOST" PORT="$PORT" SERVER_GUARD=0 \
   LM_EVAL_TASKS=gsm8k LM_EVAL_NUM_FEWSHOT=5 LM_EVAL_LIMIT="$GLIM" LM_EVAL_NUM_CONCURRENT=8 \
   LM_EVAL_MAX_GEN_TOKS=2048 OUT_DIR="$ROOT/gsm8k" bash scripts/run_lm_eval.sh > "$ROOT/gsm8k.out" 2>&1 )
gs=$(grep -aoiE '"exact_match_strict": [0-9.]+' "$ROOT/gsm8k.out" | head -1 | grep -oE '[0-9.]+$')
echo "    GSM8K strict=$gs"; awk "BEGIN{exit !($gs>=0.90)}" 2>/dev/null && note PASS "GSM8K $gs >= 0.90" || note FAIL "GSM8K $gs < 0.90"

# 3) #19 instruction-following (JSON-only)
echo "--- gate: jasl/vllm#19 instruction-following ---"
( cd "$HARNESS"; PYTHON="$VENV/bin/python" MODEL="$SERVED" BASE_URL="http://$HOST:$PORT" \
   OUT_DIR="$ROOT/issue19" bash scripts/run_sm120_issue19_instruction_following_gate.sh > "$ROOT/issue19.out" 2>&1 )
[ $? -eq 0 ] && note PASS "#19 JSON-only" || { note FAIL "#19 failed"; tail -6 "$ROOT/issue19.out"; }

# 4) arthur long-context coherence (LINE_COUNT 280 fits 32k)
echo "--- gate: arthur long-context coherence ---"
( cd "$HARNESS"; PYTHON="$VENV/bin/python" MODEL="$SERVED" BASE_URL="http://$HOST:$PORT" \
   COHERENCE_LINE_COUNT=280 COHERENCE_CONCURRENCY=8 COHERENCE_REPEAT_COUNT=1 \
   OUT_DIR="$ROOT/arthur" bash scripts/run_gb10_arthur_long_context_coherence_gate.sh > "$ROOT/arthur.out" 2>&1 )
[ $? -eq 0 ] && note PASS "arthur coherent" || { note FAIL "arthur incoherent"; tail -8 "$ROOT/arthur.out"; }

# 5) perf snapshot
echo "--- perf: prefill 8k + decode ctx0 (regression snapshot) ---"
PATH=$VENV/bin:$PATH "$VENV/bin/python" "$LMBENCH" --prefill-only --prefill-contexts 8k --port $PORT --model "$SERVED" --display-mode plain > "$ROOT/prefill.txt" 2>&1
grep -aE "^[[:space:]]*8k[[:space:]]+[0-9,]+" "$ROOT/prefill.txt" | head -1 | sed 's/^/    prefill /'
PATH=$VENV/bin:$PATH "$VENV/bin/python" "$LMBENCH" --contexts 0 --concurrency 1,2,4,8,16,32 --port $PORT --model "$SERVED" --display-mode plain > "$ROOT/decode.txt" 2>&1
sed -n "/Aggregate tok/,/Per-Request/p" "$ROOT/decode.txt" | grep -aE "^. 0 " | head -1 | sed 's/^/    decode /'

stop_vllm
echo ""
echo "=========== PHASE A SUMMARY ($([ $PASS = 1 ] && echo ALL-PASS || echo HAS-FAILURES)) -> $ROOT ==========="
grep -aoiE "exact_match_strict.: [0-9.]+" "$ROOT/gsm8k.out" | head -1
echo "=== PHASE A DONE (PASS=$PASS) ==="
