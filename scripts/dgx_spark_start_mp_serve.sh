#!/usr/bin/env bash
set -euo pipefail

required_vars=(
  HEAD_HOST
  WORKER_HOST
  HEAD_ROCE_IP
  WORKER_ROCE_IP
  ROCE_IFACE
  NCCL_IB_HCA
  VLLM_ROOT
  VLLM_VENV
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    printf 'missing required environment variable: %s\n' "${var}" >&2
    exit 2
  fi
done

MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
CUDA_HOME_REMOTE="${CUDA_HOME_REMOTE:-/usr/local/cuda}"
MASTER_PORT="${MASTER_PORT:-29519}"
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
TP_SIZE="${TP_SIZE:-2}"
PP_SIZE="${PP_SIZE:-1}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-393216}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.70}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-2}"
MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS:-4176}"
BLOCK_SIZE="${BLOCK_SIZE:-256}"
KV_CACHE_DTYPE="${KV_CACHE_DTYPE:-fp8}"
MIN_AVAILABLE_MEM_GIB="${MIN_AVAILABLE_MEM_GIB:-96}"
ALLOW_CURRENT_BOOT_NVRM_OOM="${ALLOW_CURRENT_BOOT_NVRM_OOM:-0}"
ALLOW_EXISTING_VLLM="${ALLOW_EXISTING_VLLM:-0}"
RUN_DIR="${RUN_DIR:-/tmp/dgx_spark_mp_serve_$(date +%Y%m%d%H%M%S)}"
STARTUP_TIMEOUT="${STARTUP_TIMEOUT:-600}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-5}"
SSH_OPTS="${SSH_OPTS:-}"

shell_quote() {
  printf '%q' "$1"
}

remote_env_prefix() {
  printf 'VLLM_ROOT=%s ' "$(shell_quote "${VLLM_ROOT}")"
  printf 'VLLM_VENV=%s ' "$(shell_quote "${VLLM_VENV}")"
  printf 'MODEL_ID=%s ' "$(shell_quote "${MODEL_ID}")"
  printf 'CUDA_HOME_REMOTE=%s ' "$(shell_quote "${CUDA_HOME_REMOTE}")"
  printf 'ROCE_IFACE=%s ' "$(shell_quote "${ROCE_IFACE}")"
  printf 'NCCL_IB_HCA=%s ' "$(shell_quote "${NCCL_IB_HCA}")"
  printf 'HEAD_ROCE_IP=%s ' "$(shell_quote "${HEAD_ROCE_IP}")"
  printf 'WORKER_ROCE_IP=%s ' "$(shell_quote "${WORKER_ROCE_IP}")"
  printf 'MASTER_PORT=%s ' "$(shell_quote "${MASTER_PORT}")"
  printf 'API_HOST=%s ' "$(shell_quote "${API_HOST}")"
  printf 'API_PORT=%s ' "$(shell_quote "${API_PORT}")"
  printf 'TP_SIZE=%s ' "$(shell_quote "${TP_SIZE}")"
  printf 'PP_SIZE=%s ' "$(shell_quote "${PP_SIZE}")"
  printf 'MAX_MODEL_LEN=%s ' "$(shell_quote "${MAX_MODEL_LEN}")"
  printf 'GPU_MEMORY_UTILIZATION=%s ' "$(shell_quote "${GPU_MEMORY_UTILIZATION}")"
  printf 'MAX_NUM_SEQS=%s ' "$(shell_quote "${MAX_NUM_SEQS}")"
  printf 'MAX_NUM_BATCHED_TOKENS=%s ' "$(shell_quote "${MAX_NUM_BATCHED_TOKENS}")"
  printf 'BLOCK_SIZE=%s ' "$(shell_quote "${BLOCK_SIZE}")"
  printf 'KV_CACHE_DTYPE=%s ' "$(shell_quote "${KV_CACHE_DTYPE}")"
  printf 'MIN_AVAILABLE_MEM_GIB=%s ' "$(shell_quote "${MIN_AVAILABLE_MEM_GIB}")"
  printf 'ALLOW_CURRENT_BOOT_NVRM_OOM=%s ' "$(shell_quote "${ALLOW_CURRENT_BOOT_NVRM_OOM}")"
  printf 'ALLOW_EXISTING_VLLM=%s ' "$(shell_quote "${ALLOW_EXISTING_VLLM}")"
  printf 'RUN_DIR=%s ' "$(shell_quote "${RUN_DIR}")"
  printf 'STARTUP_TIMEOUT=%s ' "$(shell_quote "${STARTUP_TIMEOUT}")"
  printf 'HEALTH_TIMEOUT=%s ' "$(shell_quote "${HEALTH_TIMEOUT}")"
}

run_remote_script() {
  local host="$1"
  local extra_env="$2"
  shift 2
  # SSH_OPTS is intentionally a user-provided word list, for example
  # '-o BatchMode=yes -o ConnectTimeout=10'.
  # shellcheck disable=SC2086
  ssh ${SSH_OPTS} "${host}" "$(remote_env_prefix) ${extra_env} bash -s" "$@"
}

stop_existing_and_reclaim() {
  local host="$1"

  run_remote_script "${host}" "" <<'REMOTE'
set -euo pipefail

if [[ "${ALLOW_EXISTING_VLLM}" != "1" ]] \
    && pgrep -af '[V]LLM::|[p]ython -m vllm.entrypoints.cli.main|[v]llm serve' >/dev/null 2>&1; then
  printf 'existing vLLM process found; stop it or set ALLOW_EXISTING_VLLM=1\n' >&2
  pgrep -af '[V]LLM::|[p]ython -m vllm.entrypoints.cli.main|[v]llm serve' >&2 || true
  exit 3
fi

pkill -TERM -f '[d]s4_drop_cache_loop' >/dev/null 2>&1 || true

if sudo -n true >/dev/null 2>&1; then
  sudo -n sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
else
  printf 'warning: passwordless sudo unavailable; skipped drop_caches\n' >&2
fi
REMOTE
}

preflight_node() {
  local host="$1"
  local node_ip="$2"
  local peer_ip="$3"

  run_remote_script "${host}" \
    "NODE_IP=$(shell_quote "${node_ip}") PEER_IP=$(shell_quote "${peer_ip}")" <<'REMOTE'
set -euo pipefail

test -d "${VLLM_ROOT}"
test -x "${VLLM_VENV}/bin/python"

env PATH="${VLLM_VENV}/bin:${CUDA_HOME_REMOTE}/bin:${PATH}" \
  PYTHONPATH="${VLLM_ROOT}:${PYTHONPATH:-}" \
  "${VLLM_VENV}/bin/python" - <<'PY'
import shutil
import sys

import torch
import vllm

print(f"python={sys.executable}")
print(f"torch={torch.__version__} {torch.__file__}")
print(f"vllm={vllm.__file__}")
print(f"ninja={shutil.which('ninja')}")
if shutil.which("ninja") is None:
    raise SystemExit("ninja is not on PATH; include the vLLM venv bin directory")
PY

available_gib="$(awk '/MemAvailable/ { printf "%d", $2 / 1024 / 1024 }' /proc/meminfo)"
printf 'MemAvailable=%s GiB on %s\n' "${available_gib}" "${NODE_IP}"
if (( available_gib < MIN_AVAILABLE_MEM_GIB )); then
  printf 'MemAvailable below MIN_AVAILABLE_MEM_GIB=%s on %s\n' \
    "${MIN_AVAILABLE_MEM_GIB}" "${NODE_IP}" >&2
  exit 4
fi

if [[ "${ALLOW_CURRENT_BOOT_NVRM_OOM}" != "1" ]] \
    && journalctl -b -k --no-pager 2>/dev/null \
      | grep -E 'NVRM:.*(Out of memory|NV_ERR_NO_MEMORY)' >/dev/null; then
  printf 'current boot already has NVIDIA driver OOM on %s; reboot before retrying\n' "${NODE_IP}" >&2
  exit 5
fi

ping -c 1 -W 2 "${PEER_IP}" >/dev/null
REMOTE
}

start_worker() {
  run_remote_script "${WORKER_HOST}" \
    "NODE_RANK=1 NODE_IP=$(shell_quote "${WORKER_ROCE_IP}")" <<'REMOTE'
set -euo pipefail
mkdir -p "${RUN_DIR}"
cd "${VLLM_ROOT}"
nohup env \
  PATH="${VLLM_VENV}/bin:${CUDA_HOME_REMOTE}/bin:${PATH}" \
  CUDA_HOME="${CUDA_HOME_REMOTE}" \
  TRITON_PTXAS_PATH="${CUDA_HOME_REMOTE}/bin/ptxas" \
  PYTHONPATH="${VLLM_ROOT}:${PYTHONPATH:-}" \
  CUDA_VISIBLE_DEVICES="0" \
  VLLM_HOST_IP="${NODE_IP}" \
  NCCL_SOCKET_IFNAME="${ROCE_IFACE}" \
  GLOO_SOCKET_IFNAME="${ROCE_IFACE}" \
  NCCL_IB_HCA="${NCCL_IB_HCA}" \
  NCCL_IB_DISABLE="0" \
  NCCL_DEBUG="WARN" \
  PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True" \
  VLLM_MARLIN_USE_ATOMIC_ADD="1" \
  "${VLLM_VENV}/bin/python" -m vllm.entrypoints.cli.main \
    serve "${MODEL_ID}" \
    --trust-remote-code \
    --kv-cache-dtype "${KV_CACHE_DTYPE}" \
    --block-size "${BLOCK_SIZE}" \
    --tensor-parallel-size "${TP_SIZE}" \
    --pipeline-parallel-size "${PP_SIZE}" \
    --distributed-executor-backend mp \
    --nnodes 2 \
    --master-addr "${HEAD_ROCE_IP}" \
    --master-port "${MASTER_PORT}" \
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
    --max-model-len "${MAX_MODEL_LEN}" \
    --max-num-seqs "${MAX_NUM_SEQS}" \
    --max-num-batched-tokens "${MAX_NUM_BATCHED_TOKENS}" \
    --tokenizer-mode deepseek_v4 \
    --tool-call-parser deepseek_v4 \
    --enable-auto-tool-choice \
    --reasoning-parser deepseek_v4 \
    --node-rank "${NODE_RANK}" \
    --headless \
  > "${RUN_DIR}/worker.log" 2>&1 < /dev/null &
echo "$!" > "${RUN_DIR}/worker.pid"
printf 'worker_run_dir=%s\nworker_pid=%s\n' "${RUN_DIR}" "$(cat "${RUN_DIR}/worker.pid")"
REMOTE
}

start_head() {
  run_remote_script "${HEAD_HOST}" \
    "NODE_RANK=0 NODE_IP=$(shell_quote "${HEAD_ROCE_IP}")" <<'REMOTE'
set -euo pipefail
mkdir -p "${RUN_DIR}"
cd "${VLLM_ROOT}"
nohup env \
  PATH="${VLLM_VENV}/bin:${CUDA_HOME_REMOTE}/bin:${PATH}" \
  CUDA_HOME="${CUDA_HOME_REMOTE}" \
  TRITON_PTXAS_PATH="${CUDA_HOME_REMOTE}/bin/ptxas" \
  PYTHONPATH="${VLLM_ROOT}:${PYTHONPATH:-}" \
  CUDA_VISIBLE_DEVICES="0" \
  VLLM_HOST_IP="${NODE_IP}" \
  NCCL_SOCKET_IFNAME="${ROCE_IFACE}" \
  GLOO_SOCKET_IFNAME="${ROCE_IFACE}" \
  NCCL_IB_HCA="${NCCL_IB_HCA}" \
  NCCL_IB_DISABLE="0" \
  NCCL_DEBUG="WARN" \
  PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True" \
  VLLM_MARLIN_USE_ATOMIC_ADD="1" \
  "${VLLM_VENV}/bin/python" -m vllm.entrypoints.cli.main \
    serve "${MODEL_ID}" \
    --trust-remote-code \
    --kv-cache-dtype "${KV_CACHE_DTYPE}" \
    --block-size "${BLOCK_SIZE}" \
    --tensor-parallel-size "${TP_SIZE}" \
    --pipeline-parallel-size "${PP_SIZE}" \
    --distributed-executor-backend mp \
    --nnodes 2 \
    --master-addr "${HEAD_ROCE_IP}" \
    --master-port "${MASTER_PORT}" \
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}" \
    --max-model-len "${MAX_MODEL_LEN}" \
    --max-num-seqs "${MAX_NUM_SEQS}" \
    --max-num-batched-tokens "${MAX_NUM_BATCHED_TOKENS}" \
    --tokenizer-mode deepseek_v4 \
    --tool-call-parser deepseek_v4 \
    --enable-auto-tool-choice \
    --reasoning-parser deepseek_v4 \
    --node-rank "${NODE_RANK}" \
    --host "${API_HOST}" \
    --port "${API_PORT}" \
  > "${RUN_DIR}/head.log" 2>&1 < /dev/null &
echo "$!" > "${RUN_DIR}/head.pid"
printf 'head_run_dir=%s\nhead_pid=%s\n' "${RUN_DIR}" "$(cat "${RUN_DIR}/head.pid")"
REMOTE
}

wait_for_health() {
  run_remote_script "${HEAD_HOST}" "" <<'REMOTE'
set -euo pipefail

deadline="$(( $(date +%s) + STARTUP_TIMEOUT ))"
while true; do
  code="$(curl -sS -o "${RUN_DIR}/health.out" \
    -w '%{http_code}' --max-time "${HEALTH_TIMEOUT}" \
    "http://127.0.0.1:${API_PORT}/health" 2>"${RUN_DIR}/health.err" || true)"
  if [[ "${code}" == "200" ]]; then
    bytes="$(wc -c < "${RUN_DIR}/health.out" | tr -d '[:space:]')"
    printf 'health=200 bytes=%s\n' "${bytes}"
    break
  fi
  if (( $(date +%s) >= deadline )); then
    printf 'server did not become healthy; last_status=%s\n' "${code}" >&2
    tail -80 "${RUN_DIR}/head.log" >&2 || true
    exit 6
  fi
  sleep 5
done

grep -E 'GPU KV cache size|Available KV cache memory|Model loading took|Application startup complete' \
  "${RUN_DIR}/head.log" || true
REMOTE
}

printf 'stopping stale helpers and reclaiming file cache...\n'
stop_existing_and_reclaim "${WORKER_HOST}"
stop_existing_and_reclaim "${HEAD_HOST}"

printf 'running node preflight...\n'
preflight_node "${HEAD_HOST}" "${HEAD_ROCE_IP}" "${WORKER_ROCE_IP}"
preflight_node "${WORKER_HOST}" "${WORKER_ROCE_IP}" "${HEAD_ROCE_IP}"

printf 'starting vLLM mp worker and head...\n'
start_worker
start_head
wait_for_health
