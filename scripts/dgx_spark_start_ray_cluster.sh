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

CUDA_HOME_REMOTE="${CUDA_HOME_REMOTE:-/usr/local/cuda}"
RAY_PORT="${RAY_PORT:-6379}"
RAY_OBJECT_STORE_MEMORY="${RAY_OBJECT_STORE_MEMORY:-1073741824}"
RAY_STATUS_TIMEOUT="${RAY_STATUS_TIMEOUT:-60}"
MIN_AVAILABLE_MEM_GIB="${MIN_AVAILABLE_MEM_GIB:-96}"
ALLOW_CURRENT_BOOT_NVRM_OOM="${ALLOW_CURRENT_BOOT_NVRM_OOM:-0}"
ALLOW_EXISTING_VLLM="${ALLOW_EXISTING_VLLM:-0}"
SSH_OPTS="${SSH_OPTS:-}"

shell_quote() {
  printf '%q' "$1"
}

remote_env_prefix() {
  printf 'VLLM_ROOT=%s ' "$(shell_quote "${VLLM_ROOT}")"
  printf 'VLLM_VENV=%s ' "$(shell_quote "${VLLM_VENV}")"
  printf 'CUDA_HOME_REMOTE=%s ' "$(shell_quote "${CUDA_HOME_REMOTE}")"
  printf 'ROCE_IFACE=%s ' "$(shell_quote "${ROCE_IFACE}")"
  printf 'NCCL_IB_HCA=%s ' "$(shell_quote "${NCCL_IB_HCA}")"
  printf 'RAY_PORT=%s ' "$(shell_quote "${RAY_PORT}")"
  printf 'RAY_OBJECT_STORE_MEMORY=%s ' "$(shell_quote "${RAY_OBJECT_STORE_MEMORY}")"
  printf 'RAY_STATUS_TIMEOUT=%s ' "$(shell_quote "${RAY_STATUS_TIMEOUT}")"
  printf 'MIN_AVAILABLE_MEM_GIB=%s ' "$(shell_quote "${MIN_AVAILABLE_MEM_GIB}")"
  printf 'ALLOW_CURRENT_BOOT_NVRM_OOM=%s ' "$(shell_quote "${ALLOW_CURRENT_BOOT_NVRM_OOM}")"
  printf 'ALLOW_EXISTING_VLLM=%s ' "$(shell_quote "${ALLOW_EXISTING_VLLM}")"
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

stop_ray_and_reclaim() {
  local host="$1"
  local node_ip="$2"

  run_remote_script "${host}" "NODE_IP=$(shell_quote "${node_ip}")" <<'REMOTE'
set -euo pipefail

if [[ "${ALLOW_EXISTING_VLLM}" != "1" ]] \
    && pgrep -af 'vllm.entrypoints|vllm serve|python .* -m vllm' >/dev/null 2>&1; then
  printf 'existing vLLM process found on %s; stop it or set ALLOW_EXISTING_VLLM=1\n' "${NODE_IP}" >&2
  pgrep -af 'vllm.entrypoints|vllm serve|python .* -m vllm' >&2 || true
  exit 3
fi

"${VLLM_VENV}/bin/python" -m ray.scripts.scripts stop --force >/dev/null 2>&1 || true

if sudo -n true >/dev/null 2>&1; then
  sudo -n sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
else
  printf 'warning: passwordless sudo unavailable; skipped drop_caches on %s\n' "${NODE_IP}" >&2
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

PYTHONPATH="${VLLM_ROOT}:${PYTHONPATH:-}" "${VLLM_VENV}/bin/python" - <<'PY'
import sys
import torch
import ray
import vllm

print(f"python={sys.executable}")
print(f"torch={torch.__version__} {torch.__file__}")
print(f"ray={ray.__version__} {ray.__file__}")
print(f"vllm={vllm.__file__}")
PY

"${VLLM_VENV}/bin/python" -m ray.scripts.scripts --help >/dev/null

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

start_head() {
  run_remote_script "${HEAD_HOST}" \
    "NODE_IP=$(shell_quote "${HEAD_ROCE_IP}")" <<'REMOTE'
set -euo pipefail

env \
  PATH="${CUDA_HOME_REMOTE}/bin:${PATH}" \
  CUDA_HOME="${CUDA_HOME_REMOTE}" \
  TRITON_PTXAS_PATH="${CUDA_HOME_REMOTE}/bin/ptxas" \
  PYTHONPATH="${VLLM_ROOT}" \
  CUDA_VISIBLE_DEVICES="0" \
  VLLM_HOST_IP="${NODE_IP}" \
  RAY_NODE_IP_ADDRESS="${NODE_IP}" \
  RAY_OVERRIDE_NODE_IP_ADDRESS="${NODE_IP}" \
  NCCL_SOCKET_IFNAME="${ROCE_IFACE}" \
  GLOO_SOCKET_IFNAME="${ROCE_IFACE}" \
  NCCL_IB_HCA="${NCCL_IB_HCA}" \
  NCCL_IB_DISABLE="0" \
  RAY_memory_monitor_refresh_ms="0" \
  RAY_num_prestart_python_workers="0" \
  RAY_object_store_memory="${RAY_OBJECT_STORE_MEMORY}" \
  "${VLLM_VENV}/bin/python" -m ray.scripts.scripts start \
    --head \
    --node-ip-address="${NODE_IP}" \
    --port="${RAY_PORT}" \
    --num-cpus=2 \
    --num-gpus=1 \
    --object-store-memory="${RAY_OBJECT_STORE_MEMORY}" \
    --disable-usage-stats
REMOTE
}

start_worker() {
  run_remote_script "${WORKER_HOST}" \
    "NODE_IP=$(shell_quote "${WORKER_ROCE_IP}") HEAD_IP=$(shell_quote "${HEAD_ROCE_IP}")" <<'REMOTE'
set -euo pipefail

env \
  PATH="${CUDA_HOME_REMOTE}/bin:${PATH}" \
  CUDA_HOME="${CUDA_HOME_REMOTE}" \
  TRITON_PTXAS_PATH="${CUDA_HOME_REMOTE}/bin/ptxas" \
  PYTHONPATH="${VLLM_ROOT}" \
  CUDA_VISIBLE_DEVICES="0" \
  VLLM_HOST_IP="${NODE_IP}" \
  RAY_NODE_IP_ADDRESS="${NODE_IP}" \
  RAY_OVERRIDE_NODE_IP_ADDRESS="${NODE_IP}" \
  NCCL_SOCKET_IFNAME="${ROCE_IFACE}" \
  GLOO_SOCKET_IFNAME="${ROCE_IFACE}" \
  NCCL_IB_HCA="${NCCL_IB_HCA}" \
  NCCL_IB_DISABLE="0" \
  RAY_memory_monitor_refresh_ms="0" \
  RAY_num_prestart_python_workers="0" \
  RAY_object_store_memory="${RAY_OBJECT_STORE_MEMORY}" \
  "${VLLM_VENV}/bin/python" -m ray.scripts.scripts start \
    --address="${HEAD_IP}:${RAY_PORT}" \
    --node-ip-address="${NODE_IP}" \
    --num-cpus=2 \
    --num-gpus=1 \
    --object-store-memory="${RAY_OBJECT_STORE_MEMORY}" \
    --disable-usage-stats
REMOTE
}

show_status() {
  run_remote_script "${HEAD_HOST}" \
    "HEAD_IP=$(shell_quote "${HEAD_ROCE_IP}")" <<'REMOTE'
set -euo pipefail
PYTHONPATH="${VLLM_ROOT}:${PYTHONPATH:-}" "${VLLM_VENV}/bin/python" - <<'PY'
import os
import sys
import time

import ray

head_ip = os.environ["HEAD_IP"]
ray_port = os.environ["RAY_PORT"]
deadline = time.monotonic() + int(os.environ["RAY_STATUS_TIMEOUT"])
ray.init(address=f"{head_ip}:{ray_port}")
try:
    while True:
        nodes = [node for node in ray.nodes() if node.get("Alive")]
        gpu_total = sum(float(node.get("Resources", {}).get("GPU", 0)) for node in nodes)
        if len(nodes) >= 2 and gpu_total >= 2:
            print(f"cluster_ready nodes={len(nodes)} gpus={gpu_total:g}")
            break
        if time.monotonic() >= deadline:
            print(f"cluster_not_ready nodes={len(nodes)} gpus={gpu_total:g}", file=sys.stderr)
            sys.exit(6)
        time.sleep(2)
finally:
    ray.shutdown()
PY
"${VLLM_VENV}/bin/python" -m ray.scripts.scripts status --address="${HEAD_IP}:${RAY_PORT}"
REMOTE
}

printf 'stopping Ray and reclaiming file cache...\n'
stop_ray_and_reclaim "${WORKER_HOST}" "${WORKER_ROCE_IP}"
stop_ray_and_reclaim "${HEAD_HOST}" "${HEAD_ROCE_IP}"

printf 'running node preflight...\n'
preflight_node "${HEAD_HOST}" "${HEAD_ROCE_IP}" "${WORKER_ROCE_IP}"
preflight_node "${WORKER_HOST}" "${WORKER_ROCE_IP}" "${HEAD_ROCE_IP}"

printf 'starting Ray head and worker with the vLLM Python executable...\n'
start_head
start_worker
show_status
