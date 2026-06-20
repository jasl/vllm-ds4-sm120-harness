#!/usr/bin/env bash
# Absorb FlashInfer-main #3615 (fix: eliminate multi-CTA radix top-k stream hangs
# on SM120/SM121) into our pinned build, and validate it integrates cleanly.
#
# WHY this is lightweight (no flashinfer rebuild): top-k sampling is JIT-compiled
# from the shipped header `include/flashinfer/topk.cuh` (data/include -> include
# symlink), and #3615 touches ONLY that header. Verified offline that the #3615
# commit (49f2abf) applies cleanly to our b41aa8d topk.cuh. So absorbing = patch
# the header + clear the topk JIT cache; the decode/attention kernels are untouched.
# This is tracking an upstream-merged commit, NOT forking. (For shipping, the
# recommendation becomes: use flashinfer main >= 9c5ed7c, which contains #3615.)
#
# We use flashinfer top-k sampling via flashinfer.sampling.top_k_sampling_from_probs
# (vllm/v1/sample/ops/topk_topp_sampler.py), so this fix matters for production
# top-k-sampling serving on SM120/SM121. Our greedy gates don't exercise it.
#
# Validation:
#   (1) apply #3615 to the active topk.cuh (backup first), clear topk JIT cache
#   (2) serve DSv4 (MXFP4 default) with the decode opt ON
#   (3) top-k-sampling concurrency smoke: N concurrent completions with top_k+temp
#       -> the FIRST one triggers the topk JIT recompile with the new header
#          (proves it compiles); all must return promptly (no multi-CTA hang)
#   (4) GSM8K greedy regression (limit 100) -> unchanged (~0.96); topk.cuh is
#       orthogonal to the greedy decode/attention path
#   (5) report. Leaves the patch applied (= the absorption); backup at $BAK for revert.
#
# Low wedge risk: normal serving + sampling, no IMA-prone kernels.
# Usage: run_sm120_flashinfer_3615_topk_absorb.sh [WORKTREE] [GSM8K_LIMIT] [REVERT]
#   REVERT=revert -> just restore the original topk.cuh from backup and exit.
set -uo pipefail

WT="${1:-/home/jasl/tmp/vllm-rebased-dev-20260614}"
GLIM="${2:-100}"
MODE="${3:-apply}"

VENV=/home/jasl/tmp/vllm-lucifer-pr3395-venv-20260614
HARNESS=/home/jasl/tmp/ds4-sm120-harness
FI=/home/jasl/tmp/flashinfer-pr3395-b41aa8d-20260614     # active flashinfer source (b41aa8d, source-shadowed)
FIMAIN=/home/jasl/tmp/flashinfer-main-src                # has commit 49f2abf (#3615)
TOPK="$FI/include/flashinfer/topk.cuh"                   # JIT header (data/include -> include symlink)
BAK="$TOPK.pre3615.bak"
JITCACHE="$HOME/.cache/flashinfer"
MODEL=deepseek-ai/DeepSeek-V4-Flash; SERVED=DS4
HOST=127.0.0.1; PORT=8000
ROOT=/home/jasl/tmp/fi3615_absorb/$(date +%Y%m%d%H%M%S); mkdir -p "$ROOT"

if [ "$MODE" = revert ]; then
  [ -f "$BAK" ] && { cp -f "$BAK" "$TOPK"; rm -f "$BAK"; echo "reverted topk.cuh from backup (backup removed)"; rm -rf "$JITCACHE"/*topk* 2>/dev/null; } || echo "no backup at $BAK"
  exit 0
fi

echo "=== FlashInfer #3615 topk absorb+validate  wt=$(basename "$WT")  gsm8k=$GLIM -> $ROOT ==="

# ---- (1) apply #3615 to topk.cuh (idempotent via backup, -p1 in $FI) + clear topk JIT cache ----
P="$ROOT/p3615.diff"
git -C "$FIMAIN" show 49f2abf -- include/flashinfer/topk.cuh > "$P" 2>/dev/null
[ -s "$P" ] || { echo "  FATAL: could not extract #3615 diff from $FIMAIN"; exit 3; }
if [ ! -f "$BAK" ]; then
  cp -f "$TOPK" "$BAK"; echo "  backed up topk.cuh -> $BAK"
  if patch -p1 -d "$FI" --dry-run < "$P" >/dev/null 2>&1; then
    patch -p1 -d "$FI" < "$P" && echo "  applied #3615 to $TOPK"
  else
    echo "  PATCH DOES NOT APPLY -- restoring + aborting"; cp -f "$BAK" "$TOPK"; rm -f "$BAK"; exit 3
  fi
else
  echo "  #3615 already applied (backup exists) -- skipping patch"
fi
echo "  active topk.cuh md5: $(md5sum "$TOPK" | awk '{print $1}')  (#3615 hunks applied; differs from 9c5ed7c only by b41aa8d divergence elsewhere)"
echo "  clearing sampling JIT module (the topk.cuh consumer) -> forces clean recompile with #3615; decode kernel cache untouched"
for d in "$JITCACHE"/*/120f/cached_ops/sampling; do [ -d "$d" ] && { echo "    rm $d"; rm -rf "$d"; }; done

stop_vllm(){ pkill -TERM -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 8; pkill -KILL -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 3; rm -f /dev/shm/psm_* 2>/dev/null || true; }
trap stop_vllm EXIT INT TERM

# ---- (2) serve DSv4-MXFP4 (DEFAULT path; uses flashinfer top-k sampling = the #3615 surface).
#         Decode opt is irrelevant to #3615 and is left OFF (it needs flashinfer.mla._sparse_mla_sm120). ----
echo "--- serve $MODEL (default path; flashinfer top-k sampling active) ---"
stop_vllm
( PATH=/usr/local/cuda/bin:$VENV/bin:$PATH PYTHONPATH=$WT PYTHONSAFEPATH=1 \
  VLLM_LOGGING_LEVEL=INFO VLLM_ENGINE_READY_TIMEOUT_S=3600 CUDA_VISIBLE_DEVICES=0,1 \
  VLLM_FLASHINFER_BYPASS_VERSION_CHECK=1 FLASHINFER_DISABLE_VERSION_CHECK=1 VLLM_USE_FLASHINFER_SAMPLER=1 \
  nohup "$VENV/bin/vllm" serve "$MODEL" --served-model-name "$SERVED" \
    --trust-remote-code --host "$HOST" --port "$PORT" --tensor-parallel-size 2 \
    --kv-cache-dtype fp8 --block-size 256 --gpu-memory-utilization 0.90 --max-model-len 16384 \
    --max-num-seqs 64 --max-num-batched-tokens 8192 --max-cudagraph-capture-size 64 \
    --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
    --async-scheduling --enable-chunked-prefill --enable-flashinfer-autotune \
    --tokenizer-mode deepseek_v4 > "$ROOT/serve.log" 2>&1 & echo $! > "$ROOT/pid" )
sp=$(cat "$ROOT/pid"); ok=0
for i in $(seq 1 240); do
  kill -0 "$sp" 2>/dev/null || { echo "SERVE DIED"; tail -25 "$ROOT/serve.log"; break; }
  [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HOST:$PORT/health 2>/dev/null)" = 200 ] && { ok=1; echo "serve UP ~$((i*10))s"; break; }
  grep -qaE 'Engine core initialization failed|CUDA error|IllegalInstruction|nvcc|compile.*error|topk' "$ROOT/serve.log" 2>/dev/null && grep -qaiE 'error|fail' "$ROOT/serve.log" && { echo "SERVE ERROR"; grep -aiE 'error|topk|nvcc|compile' "$ROOT/serve.log" | tail -10; break; }
  sleep 10
done
[ "$ok" = 1 ] || { echo "HEALTH FAIL"; tail -30 "$ROOT/serve.log"; exit 92; }

# ---- (3) top-k-sampling concurrency smoke (triggers topk JIT recompile + no-hang check) ----
echo "--- top-k sampling smoke: 16 concurrent completions (top_k=50, temp=0.8) ---"
smoke_one(){ curl -s --max-time 120 http://$HOST:$PORT/v1/completions -H 'Content-Type: application/json' \
  -d "{\"model\":\"$SERVED\",\"prompt\":\"Write one sentence about GPU $1:\",\"max_tokens\":48,\"temperature\":0.8,\"top_k\":50,\"seed\":$1}" \
  -o "$ROOT/smoke_$1.json" -w "%{http_code}"; }
t0=$(date +%s); pids=""
for n in $(seq 1 16); do smoke_one "$n" > "$ROOT/code_$n" & pids="$pids $!"; done
wait $pids; t1=$(date +%s)
nok=0; ntext=0
for n in $(seq 1 16); do
  [ "$(cat "$ROOT/code_$n" 2>/dev/null)" = 200 ] && nok=$((nok+1))
  grep -qaE '"text"' "$ROOT/smoke_$n.json" 2>/dev/null && [ -n "$(grep -aoE '"text":"[^"]+' "$ROOT/smoke_$n.json" 2>/dev/null)" ] && ntext=$((ntext+1))
done
echo "  top-k smoke: $nok/16 HTTP-200, $ntext/16 non-empty, wall=$((t1-t0))s (no-hang = all return well under 120s)"
echo "  topk JIT compiled? $(grep -aciE 'topk|sampling' "$ROOT/serve.log" 2>/dev/null) topk/sampling log lines; sample output:"
grep -aoE '"text":"[^"]{0,80}' "$ROOT/smoke_1.json" 2>/dev/null | head -1 | sed 's/^/    /'

# ---- (4) GSM8K greedy regression ----
echo "--- GSM8K 5-shot greedy limit=$GLIM (regression; topk.cuh orthogonal) ---"
( cd "$HARNESS"
  PYTHON="$VENV/bin/python" LM_EVAL_BIN="$VENV/bin/lm_eval" \
    MODEL="$SERVED" BASE_URL="http://$HOST:$PORT" HOST="$HOST" PORT="$PORT" \
    LM_EVAL_TASKS=gsm8k LM_EVAL_NUM_FEWSHOT=5 LM_EVAL_LIMIT="$GLIM" LM_EVAL_NUM_CONCURRENT=8 \
    LM_EVAL_MAX_GEN_TOKS=2048 SERVER_GUARD=1 OUT_DIR="$ROOT/lm_eval" \
    bash scripts/run_lm_eval.sh > "$ROOT/lm_eval.stdout" 2> "$ROOT/lm_eval.stderr" )
grep -aiE 'exact_match' "$ROOT/lm_eval.stdout" 2>/dev/null | grep -aiE 'flexible|strict' | tail -2 | sed 's/^/    /'

echo "  post health=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HOST:$PORT/health) errs=$(grep -aci 'Traceback\|CUDA error\|IllegalInstruction' "$ROOT/serve.log")"
stop_vllm
echo ""
echo "=== #3615 ABSORB SUMMARY -> $ROOT ==="
echo "  patch applied + topk JIT recompiled cleanly if the smoke returned 200s with text."
echo "  top-k smoke: $nok/16 ok, $ntext/16 non-empty; GSM8K above should be ~0.96 (no regression)."
echo "  topk.cuh backup: $BAK  (revert: run with 3rd arg 'revert')"
echo "  PASS = smoke all-200 + non-empty + no-hang AND GSM8K within noise of baseline."
echo "=== DONE ==="
