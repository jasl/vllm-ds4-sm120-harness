#!/usr/bin/env bash
# NVFP4 vs MXFP4 matched A/B on RTX SM120 (2x RTX PRO 6000, TP=2): prefill, decode, memory.
#
# Both models served with IDENTICAL config (TP2, fp8 KV, block 256, max-len 16384,
# gpu-util 0.90, FULL_AND_PIECEWISE cudagraph, --moe-backend auto). The only
# variable is the model/quant: MXFP4 = deepseek-ai/DeepSeek-V4-Flash (mature path),
# NVFP4 = nvidia/DeepSeek-V4-Flash-NVFP4 (auto-selects flashinfer_cutlass MoE).
#
# Per arm captures:
#   MEMORY  : "Model loading took X GiB" (weights/GPU) + "Available KV cache memory: X GiB"
#             + "GPU KV cache size: N tokens" + peak GPU MiB during decode
#   PREFILL : llm_decode_bench --prefill-only --prefill-contexts 8k,64k (client tok/s, TTFT)
#   DECODE  : llm_decode_bench ctx0 concurrency sweep (aggregate tok/s) -> raw saved for parse
# (correctness already known: NVFP4 GSM8K 0.965, MXFP4 ~0.96; not re-run here)
#
# Usage: run_sm120_nvfp4_vs_mxfp4_ab.sh [WORKTREE] [ARMS]
#   ARMS subset of: mxfp4 nvfp4 (default both)
set -uo pipefail

WT="${1:-/home/jasl/tmp/vllm-rebased-dev-20260614}"
ARMS_IN="${2:-mxfp4 nvfp4}"; ARMS_IN="${ARMS_IN//,/ }"

VENV=/home/jasl/tmp/vllm-lucifer-pr3395-venv-20260614
NVFP4=/home/jasl/.cache/huggingface/hub/models--nvidia--DeepSeek-V4-Flash-NVFP4/snapshots/7fc18be2b215ae48260383d4a228ec8a033046f7
MXFP4=deepseek-ai/DeepSeek-V4-Flash
HOST=127.0.0.1; PORT=8000
LMBENCH=/home/jasl/tmp/llm_decode_bench.py
ROOT=/home/jasl/tmp/nvfp4_vs_mxfp4/$(date +%Y%m%d%H%M%S); mkdir -p "$ROOT"

echo "=== NVFP4 vs MXFP4 matched A/B (prefill/decode/memory)  arms=[$ARMS_IN] -> $ROOT ==="
cd "$WT" || { echo "FATAL: $WT missing"; exit 2; }
echo "checkout: $(git rev-parse --short HEAD 2>/dev/null)"

stop_vllm(){ pkill -TERM -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 8; pkill -KILL -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 3; rm -f /dev/shm/psm_* 2>/dev/null || true; }
trap stop_vllm EXIT INT TERM

run_arm(){
  local TAG="$1" MODEL="$2" SERVED="$3"
  local OUT="$ROOT/$TAG"; mkdir -p "$OUT"
  echo ""
  echo "############ ARM=$TAG  model=$SERVED ############"
  stop_vllm
  echo "  pre-GPU MiB: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr '\n' ',')"
  ( PATH=/usr/local/cuda/bin:$VENV/bin:$PATH PYTHONPATH=$WT PYTHONSAFEPATH=1 \
    VLLM_LOGGING_LEVEL=INFO VLLM_ENGINE_READY_TIMEOUT_S=3600 CUDA_VISIBLE_DEVICES=0,1 \
    VLLM_FLASHINFER_BYPASS_VERSION_CHECK=1 FLASHINFER_DISABLE_VERSION_CHECK=1 VLLM_USE_FLASHINFER_SAMPLER=1 \
    nohup "$VENV/bin/vllm" serve "$MODEL" --served-model-name "$SERVED" \
      --trust-remote-code --host "$HOST" --port "$PORT" --tensor-parallel-size 2 \
      --kv-cache-dtype fp8 --block-size 256 --gpu-memory-utilization 0.90 --max-model-len 16384 \
      --max-num-seqs 64 --max-num-batched-tokens 8192 --max-cudagraph-capture-size 64 \
      --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
      --async-scheduling --enable-chunked-prefill --enable-flashinfer-autotune \
      --tokenizer-mode deepseek_v4 > "$OUT/serve.log" 2>&1 & echo $! > "$OUT/pid" )
  local sp ok=0; sp=$(cat "$OUT/pid")
  for i in $(seq 1 240); do
    kill -0 "$sp" 2>/dev/null || { echo "  [$TAG] SERVE DIED"; tail -25 "$OUT/serve.log"; break; }
    [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HOST:$PORT/health 2>/dev/null)" = 200 ] && { ok=1; echo "  [$TAG] health 200 ~$((i*10))s"; break; }
    grep -qaE 'Engine core initialization failed|CUDA error|No available memory|IllegalInstruction|died unexpectedly' "$OUT/serve.log" 2>/dev/null && { echo "  [$TAG] SERVE ERROR"; grep -aiE 'error|No module|assert' "$OUT/serve.log" | tail -8; break; }
    sleep 10
  done
  if [ "$ok" != 1 ]; then echo "  [$TAG] HEALTH FAIL"; echo FAILED > "$OUT/status"; stop_vllm; return 0; fi
  echo OK > "$OUT/status"

  # --- MEMORY ---
  echo "  --- [$TAG] memory ---"
  grep -aoiE "Model loading took [0-9.]+ GiB" "$OUT/serve.log" 2>/dev/null | head -1 | sed 's/^/    weights: /'
  grep -aoiE "Available KV cache memory: [0-9.]+ GiB" "$OUT/serve.log" 2>/dev/null | head -1 | sed 's/^/    /'
  grep -aoiE "GPU KV cache size: [0-9,]+ tokens" "$OUT/serve.log" 2>/dev/null | head -1 | sed 's/^/    /'
  grep -aoiE "Maximum concurrency for [0-9,]+ tokens per request: [0-9.]+x" "$OUT/serve.log" 2>/dev/null | head -1 | sed 's/^/    /'
  echo "    peak GPU MiB (loaded, pre-bench): $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr '\n' ',')"

  # --- PREFILL ---
  echo "  --- [$TAG] prefill (8k,64k) ---"
  PATH=$VENV/bin:$PATH "$VENV/bin/python" "$LMBENCH" \
    --prefill-only --prefill-contexts 8k,64k --port $PORT --model "$SERVED" --display-mode plain \
    > "$OUT/prefill.txt" 2>&1
  grep -iE "^\s*(8k|64k)\b" "$OUT/prefill.txt" 2>/dev/null | head -6 | sed 's/^/    /'

  # --- DECODE ---
  echo "  --- [$TAG] decode (ctx0 concurrency sweep) ---"
  PATH=$VENV/bin:$PATH "$VENV/bin/python" "$LMBENCH" \
    --contexts 0 --concurrency 1,2,4,8,16,32,64 --port $PORT --model "$SERVED" --display-mode plain \
    > "$OUT/decode.txt" 2>&1
  # extract the ctx=0 aggregate tok/s row (best-effort; raw saved for parse)
  grep -iE "^\s*\|?\s*0\b|aggregate|tok/s" "$OUT/decode.txt" 2>/dev/null | head -8 | sed 's/^/    /'
  echo "    peak GPU MiB (during decode): $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr '\n' ',')"
  stop_vllm
}

for arm in $ARMS_IN; do
  case "$arm" in
    mxfp4) run_arm mxfp4 "$MXFP4" DS4-MXFP4 ;;
    nvfp4) run_arm nvfp4 "$NVFP4" DS4-NVFP4 ;;
    *) echo "unknown arm $arm";;
  esac
done

echo ""
echo "=========== NVFP4 vs MXFP4 SUMMARY -> $ROOT ==========="
for arm in $ARMS_IN; do
  OUT="$ROOT/$arm"; [ -d "$OUT" ] || continue
  echo "--- $arm [$(cat "$OUT/status" 2>/dev/null)] ---"
  echo "    weights : $(grep -aoiE 'Model loading took [0-9.]+ GiB' "$OUT/serve.log" 2>/dev/null | head -1)"
  echo "    kv cache: $(grep -aoiE 'Available KV cache memory: [0-9.]+ GiB' "$OUT/serve.log" 2>/dev/null | head -1) / $(grep -aoiE 'GPU KV cache size: [0-9,]+ tokens' "$OUT/serve.log" 2>/dev/null | head -1)"
  echo "    prefill : $(grep -iE '^\s*8k\b' "$OUT/prefill.txt" 2>/dev/null | head -1 | tr -s ' ') | $(grep -iE '^\s*64k\b' "$OUT/prefill.txt" 2>/dev/null | head -1 | tr -s ' ')"
done
echo "(raw decode tables in <arm>/decode.txt for the concurrency sweep)"
echo "=== DONE -> $ROOT ==="
