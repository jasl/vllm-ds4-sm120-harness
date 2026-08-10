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
# Overridable: the DSpark drafter config below belongs to the -0731 checkpoint.
# The base DeepSeek-V4-Flash lacks the fields it needs and the worker dies with
# "Model config must specify `dflash_config.mask_token_id`". Set SPEC='' to
# serve a checkpoint without a compatible drafter.
SPEC_DEFAULT='{"method":"dspark","num_speculative_tokens":5,"draft_sample_method":"probabilistic"}'
# `${SPEC-...}` not `${SPEC:-...}`: SPEC='' must mean "no drafter", while unset
# means "use the default". Assigned in two steps because a JSON literal inside
# a `${...}` default loses its double quotes.
SPEC="${SPEC-$SPEC_DEFAULT}"
if [ -n "$SPEC" ]; then
  python3 -c 'import json,sys; json.loads(sys.argv[1])' "$SPEC" ||
    { echo "SPEC is not valid JSON: $SPEC"; exit 2; }
fi

# Empty by default. This used to carry '{"thinking":true}' as a workaround for
# /v1/responses returning the model's reasoning, and a bare </think>, inside
# output_text whenever a request omitted `reasoning` -- which is what a stock
# OpenAI SDK does. That is fixed in the engine now: ResponsesRequest normalises
# thinking state at the protocol boundary exactly as ChatCompletionRequest
# does, so the tokenizer and the reasoning parser can no longer disagree.
#
# Verified with this empty, on both checkpoints, 21/21 each:
# reasoning arrives in its own field, nothing leaks, `effort: none` still
# disables thinking, and high reasons 85-110% deeper than low (0731).
DEFAULT_CT_KWARGS="${DEFAULT_CT_KWARGS-}"
if [ -n "$DEFAULT_CT_KWARGS" ]; then
  python3 -c 'import json,sys; json.loads(sys.argv[1])' "$DEFAULT_CT_KWARGS" ||
    { echo "DEFAULT_CT_KWARGS is not valid JSON: $DEFAULT_CT_KWARGS"; exit 2; }
fi

OUT="$PROD/run/$LABEL"
mkdir -p "$OUT"

SHA=$(git -C "$PROD/vllm" rev-parse --short=10 HEAD)
echo "=== $LABEL  head=$HEAD_HOST worker=$WORKER_HOST  sha=$SHA  $(date -Is) ==="

ct_args=()
[ -n "$DEFAULT_CT_KWARGS" ] && ct_args=(SERVE_DEFAULT_CHAT_TEMPLATE_KWARGS="$DEFAULT_CT_KWARGS")

env "${ct_args[@]}" MODEL_ID="$MODEL_ID" VLLM_ROOT="$PROD/vllm" VLLM_VENV="$PROD/venv" TP_SIZE=2 \
  HEAD_HOST="$HEAD_HOST" WORKER_HOST="$WORKER_HOST" \
  HEAD_ROCE_IP="$HEAD_ROCE_IP" WORKER_ROCE_IP="$WORKER_ROCE_IP" \
  ROCE_IFACE="$ROCE_IFACE" NCCL_IB_HCA="$NCCL_IB_HCA" \
  HEAD_ROCE_IFACE="$ROCE_IFACE" HEAD_NCCL_IB_HCA="$NCCL_IB_HCA" \
  WORKER_ROCE_IFACE="$ROCE_IFACE" WORKER_NCCL_IB_HCA="$NCCL_IB_HCA" \
  SERVE_PREFIX_CACHE_MODE=on KV_CACHE_DTYPE=fp8 GPU_MEMORY_UTILIZATION=0.85 \
  MAX_MODEL_LEN="$MAX_MODEL_LEN" MAX_NUM_SEQS="$MAX_NUM_SEQS" \
  MAX_NUM_BATCHED_TOKENS="$MAX_NUM_BATCHED_TOKENS" \
  SERVE_SPECULATIVE_CONFIG="$SPEC" \
  ALLOW_CURRENT_BOOT_NVRM_OOM=1 STARTUP_TIMEOUT=2400 RUN_DIR="$OUT/serve" \
  bash "$HARNESS/scripts/dgx_spark_start_mp_serve.sh" > "$OUT/start.log" 2>&1

rc=$?
if curl -sf -m 10 http://127.0.0.1:8000/health >/dev/null 2>&1; then
  echo "REPLICA_UP label=$LABEL sha=$SHA"
else
  echo "REPLICA_FAILED label=$LABEL rc=$rc"
  tail -25 "$OUT/start.log"
fi
