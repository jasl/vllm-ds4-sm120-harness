#!/usr/bin/env bash
# Promotion validation Phase B (production-representative) for the rebased PR head on RTX SM120.
# Config B = MXFP4, MTP2 on, decode-opt ON (FlashInfer SM120 packed sparse-MLA decode),
# long max-model-len for 64k prefill. This config uses MORE memory (MTP draft + decode
# workspace + long KV), so 64k may not fit at 0.90 util -> we bump util + keep seqs low and
# note any test that cannot run (memory-bound, as expected).
#
# decode-opt needs flashinfer.mla._sparse_mla_sm120, which is absent from the default
# b41aa8d flashinfer but PRESENT in flashinfer-main-built -> source-shadow it for this serve
# (FLASHINFER_DISABLE_VERSION_CHECK=1 bypasses the cubin 0.6.12 vs 0.6.13 mismatch).
#
# Tests: memory report (weights/KV) + confirm decode-opt engaged + 64k prefill C=1 +
# GSM8K-100 (correctness w/ MTP2+decode-opt) + decode ctx0 low-concurrency.
#
# Usage: run_sm120_promotion_phaseB.sh [WT] [MAX_LEN] [DECODE_OPT] [GPU_UTIL]
set -uo pipefail
WT="${1:-/home/jasl/tmp/vllm-rebased-dev-20260614}"
MAX_LEN="${2:-65536}"
DECODE_OPT="${3:-1}"
GUTIL="${4:-0.93}"
VENV=/home/jasl/tmp/vllm-lucifer-pr3395-venv-20260614
HARNESS=/home/jasl/tmp/ds4-sm120-harness
FIMAIN=/home/jasl/tmp/flashinfer-main-built
MODEL=deepseek-ai/DeepSeek-V4-Flash-0731; SERVED=DS4
HOST=127.0.0.1; PORT=8000
LMBENCH=/home/jasl/tmp/llm_decode_bench.py
ROOT=/home/jasl/tmp/promotion_phaseB/$(date +%Y%m%d%H%M%S); mkdir -p "$ROOT"
echo "=== PROMOTION Phase B (config B: MXFP4 MTP2 decode-opt=$DECODE_OPT max-len=$MAX_LEN util=$GUTIL) -> $ROOT ==="
cd "$WT"; echo "checkout: $(git rev-parse --short HEAD) $(git log -1 --format=%s | cut -c1-46)"
PASS=1; note(){ echo "  [$1] $2"; [ "$1" = FAIL ] && PASS=0; return 0; }

# decode-opt env (source-shadow flashinfer-main-built)
DOPT_PY=""; DOPT_ENV=""
if [ "$DECODE_OPT" = 1 ]; then
  [ -f "$FIMAIN/flashinfer/mla/_sparse_mla_sm120.py" ] || { echo "FATAL: flashinfer-main-built lacks _sparse_mla_sm120"; exit 2; }
  DOPT_PY="$FIMAIN:"; DOPT_ENV="VLLM_DEEPSEEK_V4_FLASHINFER_SM120_DECODE=1"
fi

stop_vllm(){ pkill -TERM -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 8; pkill -KILL -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 3; rm -f /dev/shm/psm_* 2>/dev/null || true; }
trap stop_vllm EXIT INT TERM
stop_vllm
echo "--- serve config B ---"
( PATH=/usr/local/cuda/bin:$VENV/bin:$PATH PYTHONPATH=${DOPT_PY}$WT PYTHONSAFEPATH=1 \
  VLLM_LOGGING_LEVEL=INFO VLLM_ENGINE_READY_TIMEOUT_S=3600 CUDA_VISIBLE_DEVICES=0,1 \
  VLLM_FLASHINFER_BYPASS_VERSION_CHECK=1 FLASHINFER_DISABLE_VERSION_CHECK=1 VLLM_USE_FLASHINFER_SAMPLER=1 \
  env $DOPT_ENV \
  nohup "$VENV/bin/vllm" serve "$MODEL" --served-model-name "$SERVED" \
    --trust-remote-code --host "$HOST" --port "$PORT" --tensor-parallel-size 2 \
    --kv-cache-dtype fp8 --block-size 256 --gpu-memory-utilization "$GUTIL" --max-model-len "$MAX_LEN" \
    --max-num-seqs 8 --max-num-batched-tokens 8192 --max-cudagraph-capture-size 32 \
    --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
    --async-scheduling --enable-chunked-prefill --enable-flashinfer-autotune \
    --speculative-config.method mtp --speculative-config.num_speculative_tokens 2 \
    --tokenizer-mode deepseek_v4 > "$ROOT/serve.log" 2>&1 & echo $! > "$ROOT/pid" )
sp=$(cat "$ROOT/pid"); ok=0
for i in $(seq 1 300); do
  kill -0 "$sp" 2>/dev/null || { echo "SERVE DIED"; tail -30 "$ROOT/serve.log"; break; }
  [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HOST:$PORT/health 2>/dev/null)" = 200 ] && { ok=1; echo "serve UP ~$((i*10))s"; break; }
  grep -qaE 'Engine core initialization failed|CUDA error|No available memory|free memory|less than|KV cache|died unexpectedly|ModuleNotFound' "$ROOT/serve.log" 2>/dev/null && grep -qaiE 'error|less than|No available|ModuleNotFound' "$ROOT/serve.log" && { echo "SERVE ERROR (likely memory at max-len=$MAX_LEN)"; grep -aiE 'error|less than|No available|KV cache|memory|ModuleNotFound' "$ROOT/serve.log"|tail -10; break; }
  sleep 10
done
if [ "$ok" != 1 ]; then note FAIL "config-B serve failed at max-len=$MAX_LEN util=$GUTIL (likely memory-bound; retry smaller MAX_LEN)"; echo "=== PHASE B DONE (PASS=0, serve-fail) ==="; exit 92; fi

# memory + decode-opt engagement
echo "--- memory + decode-opt engagement ---"
grep -aoiE "Model loading took [0-9.]+ GiB|Available KV cache memory: [0-9.]+ GiB|GPU KV cache size: [0-9,]+ tokens|Maximum concurrency for [0-9,]+ tokens per request: [0-9.]+x" "$ROOT/serve.log" | head -4 | sed 's/^/    /'
DENG=$(grep -aoiE "FLASHINFER_SM120|sparse_mla_sm120|packed sparse-MLA decode|_sm120_runner|FlashInferSM120" "$ROOT/serve.log" | head -1)
if [ "$DECODE_OPT" = 1 ]; then [ -n "$DENG" ] && note PASS "decode-opt engaged ($DENG)" || note FAIL "decode-opt NOT engaged (check flashinfer)"; fi

# 64k prefill C=1
echo "--- 64k prefill C=1 (the user-requested long-prefill) ---"
PATH=$VENV/bin:$PATH "$VENV/bin/python" "$LMBENCH" --prefill-only --prefill-contexts 8k,64k --port $PORT --model "$SERVED" --display-mode plain > "$ROOT/prefill.txt" 2>&1
p8=$(grep -aE "^[[:space:]]*8k[[:space:]]+[0-9,]+" "$ROOT/prefill.txt" | head -1)
p64=$(grep -aE "^[[:space:]]*64k[[:space:]]+[0-9,]+" "$ROOT/prefill.txt" | head -1)
echo "    8k:  ${p8:-<none>}"; echo "    64k: ${p64:-<none — did not fit/run>}"
[ -n "$p64" ] && note PASS "64k prefill ran" || note FAIL "64k prefill did NOT run (memory-bound at this config)"

# GSM8K-100 (correctness with MTP2 + decode-opt)
echo "--- GSM8K 5-shot limit-100 (correctness, MTP2+decode-opt) ---"
( cd "$HARNESS"; PYTHON="$VENV/bin/python" LM_EVAL_BIN="$VENV/bin/lm_eval" \
   MODEL="$SERVED" BASE_URL="http://$HOST:$PORT" HOST="$HOST" PORT="$PORT" SERVER_GUARD=0 \
   LM_EVAL_TASKS=gsm8k LM_EVAL_NUM_FEWSHOT=5 LM_EVAL_LIMIT=100 LM_EVAL_NUM_CONCURRENT=8 \
   LM_EVAL_MAX_GEN_TOKS=2048 OUT_DIR="$ROOT/gsm8k" bash scripts/run_lm_eval.sh > "$ROOT/gsm8k.out" 2>&1 )
gs=$(grep -aoiE '"exact_match_strict": [0-9.]+' "$ROOT/gsm8k.out" | head -1 | grep -oE '[0-9.]+$')
echo "    GSM8K strict=$gs"; awk "BEGIN{exit !($gs>=0.88)}" 2>/dev/null && note PASS "GSM8K $gs >= 0.88" || note FAIL "GSM8K $gs low"

# decode ctx0 low-concurrency (decode-opt benefit)
echo "--- decode ctx0 (concurrency 1,2,4) ---"
PATH=$VENV/bin:$PATH "$VENV/bin/python" "$LMBENCH" --contexts 0 --concurrency 1,2,4 --port $PORT --model "$SERVED" --display-mode plain > "$ROOT/decode.txt" 2>&1
sed -n "/Aggregate tok/,/Per-Request/p" "$ROOT/decode.txt" | grep -aE "^. 0 " | head -1 | sed 's/^/    decode /'

stop_vllm
echo ""
echo "=========== PHASE B SUMMARY ($([ $PASS = 1 ] && echo ALL-PASS || echo HAS-NOTES)) -> $ROOT ==========="
echo "=== PHASE B DONE (PASS=$PASS) ==="
