#!/usr/bin/env bash
# Launch one production replica (2-node TP=2) from the isolated install.
# Run on the replica's HEAD node.
#
#   HEAD_HOST=... WORKER_HOST=... HEAD_ROCE_IP=... WORKER_ROCE_IP=... \
#     ./launch_replica.sh
#
# Reads only $PROD. Nothing under a development tree is touched, so a rebuild
# there cannot change what this serves.
set -uo pipefail

PROD="${PROD:-$HOME/prod}"
HARNESS="${HARNESS:?path to the harness checkout (scripts only, not code)}"
MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash-0731}"

HEAD_HOST="${HEAD_HOST:?head node address}"
WORKER_HOST="${WORKER_HOST:?worker node address}"
HEAD_ROCE_IP="${HEAD_ROCE_IP:?head RoCE address}"
WORKER_ROCE_IP="${WORKER_ROCE_IP:?worker RoCE address}"
ROCE_IFACE="${ROCE_IFACE:-enp1s0f0np0}"
NCCL_IB_HCA="${NCCL_IB_HCA:-rocep1s0f0}"
LABEL="${LABEL:-$(hostname)}"

# mml 262144 is measured, and counter-intuitive: raising it INCREASES KV
# capacity at constant memory (129,901 tok at 49,152 vs 605,013 at 262,144),
# because mml is a structural parameter of the KV pool, not a per-request
# reservation. The ceiling is a quality bound -- this model degrades past
# ~400K -- not a capacity one.
MAX_MODEL_LEN="${MAX_MODEL_LEN:-262144}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-64}"
MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS:-8192}"
SPEC='{"method":"dspark","num_speculative_tokens":5,"draft_sample_method":"probabilistic"}'

# MEASURED, and not optional. Without it, /v1/responses called WITHOUT a
# `reasoning` object -- which is what a stock OpenAI SDK does -- renders in
# non-thinking mode, while the model thinks regardless. The result is the
# model's internal monologue and a bare `</think>` inside output_text, looking
# like a normal answer.
#
# Side-by-side on the same request, one replica with this set and one without:
#   with     output=['reasoning','message']  reasoning='我们只需要回答数字。3+5=8。' message='8'
#   without  output=['message']              message='We need answer Chinese...</th…'
#
# /v1/chat/completions is unaffected either way; this aligns the two paths.
# Single-quoted and assigned in two steps: a `${VAR:-{"..."}}` default needs
# the inner brace escaped, and `\}` survives into the value, yielding invalid
# JSON that vLLM would reject at startup.
DEFAULT_CT_KWARGS_FALLBACK='{"thinking":true}'
DEFAULT_CT_KWARGS="${DEFAULT_CT_KWARGS:-$DEFAULT_CT_KWARGS_FALLBACK}"
python3 -c 'import json,sys; json.loads(sys.argv[1])' "$DEFAULT_CT_KWARGS" ||
  { echo "DEFAULT_CT_KWARGS is not valid JSON: $DEFAULT_CT_KWARGS"; exit 2; }

OUT="$PROD/run/$LABEL"
mkdir -p "$OUT"

SHA=$(git -C "$PROD/vllm" rev-parse --short=10 HEAD)
echo "=== $LABEL  head=$HEAD_HOST worker=$WORKER_HOST  sha=$SHA  $(date -Is) ==="

env MODEL_ID="$MODEL_ID" VLLM_ROOT="$PROD/vllm" VLLM_VENV="$PROD/venv" TP_SIZE=2 \
  HEAD_HOST="$HEAD_HOST" WORKER_HOST="$WORKER_HOST" \
  HEAD_ROCE_IP="$HEAD_ROCE_IP" WORKER_ROCE_IP="$WORKER_ROCE_IP" \
  ROCE_IFACE="$ROCE_IFACE" NCCL_IB_HCA="$NCCL_IB_HCA" \
  HEAD_ROCE_IFACE="$ROCE_IFACE" HEAD_NCCL_IB_HCA="$NCCL_IB_HCA" \
  WORKER_ROCE_IFACE="$ROCE_IFACE" WORKER_NCCL_IB_HCA="$NCCL_IB_HCA" \
  SERVE_PREFIX_CACHE_MODE=on KV_CACHE_DTYPE=fp8 GPU_MEMORY_UTILIZATION=0.85 \
  MAX_MODEL_LEN="$MAX_MODEL_LEN" MAX_NUM_SEQS="$MAX_NUM_SEQS" \
  MAX_NUM_BATCHED_TOKENS="$MAX_NUM_BATCHED_TOKENS" \
  SERVE_SPECULATIVE_CONFIG="$SPEC" \
  SERVE_DEFAULT_CHAT_TEMPLATE_KWARGS="$DEFAULT_CT_KWARGS" \
  ALLOW_CURRENT_BOOT_NVRM_OOM=1 STARTUP_TIMEOUT=2400 RUN_DIR="$OUT/serve" \
  bash "$HARNESS/scripts/dgx_spark_start_mp_serve.sh" > "$OUT/start.log" 2>&1

rc=$?
if curl -sf -m 10 http://127.0.0.1:8000/health >/dev/null 2>&1; then
  echo "REPLICA_UP label=$LABEL sha=$SHA"
else
  echo "REPLICA_FAILED label=$LABEL rc=$rc"
  tail -25 "$OUT/start.log"
fi
