#!/usr/bin/env bash
# Isolate the arthur long-context-coherence gibberish: serve config A with MTP on/off
# and run the arthur gate (repeat 2 = more requests for a stable pass-rate signal).
# Usage: run_sm120_arthur_mtp_probe.sh <MTP 0|1> [WT] [REPEAT] [LINE_COUNT] [CONC]
set -uo pipefail
MTP="${1:?MTP 0|1}"; WT="${2:-/home/jasl/tmp/vllm-rebased-dev-20260614}"
REPEAT="${3:-2}"; LINES="${4:-280}"; CONC="${5:-8}"; EAGER="${6:-0}"
EAGERARG=""; [ "$EAGER" = 1 ] && EAGERARG="--enforce-eager"
VENV=/home/jasl/tmp/vllm-lucifer-pr3395-venv-20260614; HARNESS=/home/jasl/tmp/ds4-sm120-harness
MODEL=deepseek-ai/DeepSeek-V4-Flash; SERVED=DS4; HOST=127.0.0.1; PORT=8000
ROOT=/home/jasl/tmp/arthur_probe/mtp${MTP}_$(date +%Y%m%d%H%M%S); mkdir -p "$ROOT"
MTPARG=""; [ "$MTP" = 1 ] && MTPARG="--speculative-config.method mtp --speculative-config.num_speculative_tokens 2"
echo "=== arthur MTP-probe MTP=$MTP lines=$LINES conc=$CONC repeat=$REPEAT -> $ROOT ==="
cd "$WT"; echo "checkout: $(git rev-parse --short HEAD)"
stop_vllm(){ pkill -TERM -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1||true; sleep 8; pkill -KILL -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1||true; sleep 3; rm -f /dev/shm/psm_* 2>/dev/null||true; }
trap stop_vllm EXIT INT TERM; stop_vllm
( PATH=/usr/local/cuda/bin:$VENV/bin:$PATH PYTHONPATH=$WT PYTHONSAFEPATH=1 \
  VLLM_ENGINE_READY_TIMEOUT_S=3600 CUDA_VISIBLE_DEVICES=0,1 VLLM_FLASHINFER_BYPASS_VERSION_CHECK=1 FLASHINFER_DISABLE_VERSION_CHECK=1 VLLM_USE_FLASHINFER_SAMPLER=1 \
  nohup "$VENV/bin/vllm" serve "$MODEL" --served-model-name "$SERVED" --trust-remote-code --host "$HOST" --port "$PORT" --tensor-parallel-size 2 \
    --kv-cache-dtype fp8 --block-size 256 --gpu-memory-utilization 0.90 --max-model-len 32768 \
    --max-num-seqs 64 --max-num-batched-tokens 8192 --max-cudagraph-capture-size 64 \
    --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
    --async-scheduling --enable-chunked-prefill --enable-flashinfer-autotune $MTPARG $EAGERARG \
    --tokenizer-mode deepseek_v4 > "$ROOT/serve.log" 2>&1 & echo $! > "$ROOT/pid" )
sp=$(cat "$ROOT/pid"); ok=0
for i in $(seq 1 240); do kill -0 "$sp" 2>/dev/null||{ echo "SERVE DIED";tail -20 "$ROOT/serve.log";break;}
  [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HOST:$PORT/health 2>/dev/null)" = 200 ]&&{ ok=1;echo "serve UP ~$((i*10))s";break;};sleep 10;done
[ "$ok" = 1 ]||{ echo "HEALTH FAIL"; exit 92; }
echo "  MTP in serve: $(grep -aoiE 'num_speculative|Speculative config|method.*mtp' "$ROOT/serve.log" | head -1)"
for run in 1 2; do
  echo "--- arthur run $run (MTP=$MTP) ---"
  ( cd "$HARNESS"; PYTHON="$VENV/bin/python" MODEL="$SERVED" BASE_URL="http://$HOST:$PORT" \
     COHERENCE_LINE_COUNT=$LINES COHERENCE_CONCURRENCY=$CONC COHERENCE_REPEAT_COUNT=$REPEAT \
     OUT_DIR="$ROOT/run$run" bash scripts/run_gb10_arthur_long_context_coherence_gate.sh > "$ROOT/arthur$run.out" 2>&1 )
  grep -aE "passed=|PASS arthur|FAIL arthur" "$ROOT/arthur$run.out" | tail -1 | sed 's/^/    /'
done
stop_vllm
echo "=== arthur MTP-probe MTP=$MTP DONE -> $ROOT ==="
