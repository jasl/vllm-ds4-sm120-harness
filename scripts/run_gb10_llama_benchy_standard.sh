#!/usr/bin/env bash
# CANONICAL GB10 (SM121) llama-benchy standard — the FIXED reference bench for
# comparing any DeepSeek-V4-Flash code change over time. Every knob is pinned;
# do NOT change them, or historical comparability breaks. To bench a new head,
# pass its git SHA as $1 (it is checked out + the serve restarted; no other change).
#
# Pinned standard (rationale in comments):
#   - 2-node TP=2, fp8 KV, prefix-cache ON, FULL_AND_PIECEWISE (default)
#   - speculator: DSpark nst=5 by default (0731 dropped the MTP heads); the
#     historical rows before 2026-08 are MTP2. Override with
#     SERVE_SPECULATIVE_CONFIG; the banner below prints what actually runs.
#   - max-model-len 49152: fits the d32768 depth sweep (32768+2048) with headroom,
#     small enough workspace that the depth context reliably prefix-caches (stable ctx_pp)
#   - util 0.85, max-num-seqs 64, max-num-batched-tokens 8192
#   - llama-benchy: pp2048 tg128, depth 8192/16384/32768, concurrency 1, runs 3,
#     --enable-prefix-caching (the eugr-format prefix-cache measurement)
set -uo pipefail
TARGET_HEAD="${1:-}"            # optional: git SHA to checkout+bench; empty = bench current head
H=/home/jasl/tmp/ds4-sm120-harness
# VLLM_ROOT overridable so a prebuilt worktree can be benched WITHOUT a
# git-checkout of the main tree (avoids clobbering local kernel WIP). The venv
# is the shared main-tree venv (a worktree shares it via PYTHONPATH).
VLLM_ROOT="${VLLM_ROOT:-$H/vllm}"
VENV="${VLLM_VENV:-$H/vllm/.venv}"
# 0731 folded DSpark into the checkpoint and dropped the MTP heads, so both
# the model and the speculative config must be overridable from the caller.
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}"
DEFAULT_SPEC='{"method":"dspark","num_speculative_tokens":5,"draft_sample_method":"probabilistic"}'
SPEC_CONFIG="${SERVE_SPECULATIVE_CONFIG:-$DEFAULT_SPEC}"
PORT=8000
export SSH_OPTS="-o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o BatchMode=yes"
export PATH="$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
LB="uvx --from git+https://github.com/eugr/llama-benchy@b220b7c9cae7af2d6bd9ebf6bfa9ac066cb40780 llama-benchy"

# --- current GB10 RoCE topology (SWITCHED CRS804 fabric, rail-0; override via env) ---
# NOTE: the old 169.254 direct-attach cabling (.116/.118) is dead; the switched
# fabric uses 192.168.100.x on enp1s0f0np0/rocep1s0f0 for BOTH nodes (.116/.119).
GB10_HEAD_HOST="${GB10_HEAD_HOST:-10.0.0.116}"; GB10_WORKER_HOST="${GB10_WORKER_HOST:-10.0.0.119}"
HEAD_ROCE_IP="${HEAD_ROCE_IP:-192.168.100.116}"; WORKER_ROCE_IP="${WORKER_ROCE_IP:-192.168.100.119}"
HEAD_ROCE_IFACE="${HEAD_ROCE_IFACE:-enp1s0f0np0}"; HEAD_NCCL_IB_HCA="${HEAD_NCCL_IB_HCA:-rocep1s0f0}"
WORKER_ROCE_IFACE="${WORKER_ROCE_IFACE:-enp1s0f0np0}"; WORKER_NCCL_IB_HCA="${WORKER_NCCL_IB_HCA:-rocep1s0f0}"

ROOT=/home/jasl/tmp/gb10_lb_standard/$(date +%Y%m%d%H%M%S); mkdir -p "$ROOT"
echo "=== GB10 llama-benchy STANDARD -> $ROOT ==="
if [ -n "$TARGET_HEAD" ]; then
  git -C "$VLLM_ROOT" fetch origin reconcile/43477-merge >/dev/null 2>&1 || true
  git -C "$VLLM_ROOT" checkout -f "$TARGET_HEAD" >/dev/null 2>&1 || { echo "checkout $TARGET_HEAD FAILED"; exit 1; }
fi
HEAD_SHA=$(git -C "$VLLM_ROOT" rev-parse --short HEAD)
echo "head=$HEAD_SHA"

memavail(){ ssh -n $SSH_OPTS "$1" "awk '/MemAvailable/{printf \"%d\", \$2/1024/1024}' /proc/meminfo" </dev/null 2>/dev/null; }
stop_serve(){
  for n in "$GB10_HEAD_HOST" "$GB10_WORKER_HOST"; do
    ssh -n $SSH_OPTS "$n" "pkill -KILL -f '[V]LLM::' 2>/dev/null||true; pkill -KILL -f '[v]llm.entrypoints.cli.main' 2>/dev/null||true; pkill -KILL -f '[r]esource_tracker' 2>/dev/null||true; fuser -k 29519/tcp 2>/dev/null||true; rm -f /dev/shm/psm_* 2>/dev/null||true" </dev/null 2>/dev/null
  done
  for i in $(seq 1 24); do m1=$(memavail "$GB10_HEAD_HOST"); m2=$(memavail "$GB10_WORKER_HOST"); [ "${m1:-0}" -ge 100 ] && [ "${m2:-0}" -ge 100 ] && return 0; sleep 5; done
}
warm_arp(){ ssh -n $SSH_OPTS "$GB10_HEAD_HOST" "nohup ping -i 0.5 -c 300 $WORKER_ROCE_IP >/dev/null 2>&1 &" </dev/null 2>/dev/null; ssh -n $SSH_OPTS "$GB10_WORKER_HOST" "nohup ping -i 0.5 -c 300 $HEAD_ROCE_IP >/dev/null 2>&1 &" </dev/null 2>/dev/null; sleep 2; }
stop_serve; warm_arp

# Print the spec config that is actually about to be served, not a fixed
# string: the banner used to say "MTP2" long after the default became
# DSpark, which is exactly how a log comes to claim a config that never ran.
echo "--- start 2-node serve (PINNED STANDARD: mml 49152, util 0.85, fp8 KV, prefix-cache ON, spec=${SPEC_CONFIG:-<none>}) ---"
env \
  MODEL_ID="$MODEL" VLLM_ROOT="$VLLM_ROOT" VLLM_VENV="$VENV" \
  HEAD_HOST="$GB10_HEAD_HOST" WORKER_HOST="$GB10_WORKER_HOST" \
  HEAD_ROCE_IP="$HEAD_ROCE_IP" WORKER_ROCE_IP="$WORKER_ROCE_IP" \
  ROCE_IFACE=enp1s0f0np0 NCCL_IB_HCA=rocep1s0f0 \
  HEAD_ROCE_IFACE="$HEAD_ROCE_IFACE" HEAD_NCCL_IB_HCA="$HEAD_NCCL_IB_HCA" \
  WORKER_ROCE_IFACE="$WORKER_ROCE_IFACE" WORKER_NCCL_IB_HCA="$WORKER_NCCL_IB_HCA" \
  SERVE_SPECULATIVE_CONFIG="$SPEC_CONFIG" \
  SERVE_PREFIX_CACHE_MODE=on \
  KV_CACHE_DTYPE=fp8 GPU_MEMORY_UTILIZATION=0.85 MAX_MODEL_LEN=49152 \
  MAX_NUM_SEQS=64 MAX_NUM_BATCHED_TOKENS=8192 ALLOW_CURRENT_BOOT_NVRM_OOM=1 \
  RUN_DIR="$ROOT/serve" STARTUP_TIMEOUT=1500 \
  PREWARM_ISL=1024 PREWARM_OSL=8 PREWARM_PROMPTS=4 PREWARM_C_HIGH=4 PREWARM_TIMEOUT=1200 \
  SSH_OPTS="$SSH_OPTS" \
  /bin/bash "$H/scripts/dgx_spark_start_mp_serve.sh" > "$ROOT/start.log" 2>&1
rc=$?; echo "serve rc=$rc"
[ "$rc" != 0 ] && { echo "START FAILED"; tail -20 "$ROOT/serve/head.log" 2>/dev/null; stop_serve; exit 1; }
SERVED=$(curl -s -m 8 http://127.0.0.1:$PORT/v1/models 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['data'][0]['id'])" 2>/dev/null)
SERVED="${SERVED:-$MODEL}"

echo "--- llama-benchy STANDARD: pp2048 tg128, depth 8192/16384/32768, C=1, runs 3, --enable-prefix-caching ---"
$LB --base-url "http://127.0.0.1:$PORT/v1" --served-model-name "$SERVED" --tokenizer "$MODEL" \
    --pp 2048 --tg 128 --depth 8192 16384 32768 --concurrency 1 --runs 3 --enable-prefix-caching --skip-coherence \
    > "$ROOT/lb.out" 2>&1
echo "lb rc=$?"
echo "=== llama-benchy STANDARD table (head $HEAD_SHA) ==="
grep -aE 'model *\||@ d|pp2048|tg128|t/s' "$ROOT/lb.out" 2>/dev/null | tail -20
echo "=== prefix-cache hit rate (steady state) ==="
grep -aoE 'Prefix cache hit rate: [0-9.]+%' "$ROOT/serve/head.log" 2>/dev/null | tail -4
stop_serve
echo "GB10_LB_STANDARD_DONE head=$HEAD_SHA" > "$ROOT/done"
echo "=== DONE (head $HEAD_SHA) -> $ROOT ==="
