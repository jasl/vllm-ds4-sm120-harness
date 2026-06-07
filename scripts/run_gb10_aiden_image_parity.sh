#!/usr/bin/env bash
# Run the public Aiden GB10 Docker image as an external backend parity probe.
#
# This is a development observation gate, not a PR hard gate. It intentionally
# keeps external-image testing separate from the current bare-metal vLLM gates:
# start the public two-node Docker recipe, capture backend evidence from logs,
# run the same random prefill sweep subset, and write local artifact summaries.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

shell_quote() {
  printf '%q' "$1"
}

run_remote() {
  local host="$1"
  shift
  # SSH_OPTS is intentionally a user-provided word list.
  # shellcheck disable=SC2086
  ssh ${SSH_OPTS:-} "${host}" "$@"
}

run_remote_script() {
  local host="$1"
  local extra_env="$2"
  shift 2
  # SSH_OPTS is intentionally a user-provided word list.
  # shellcheck disable=SC2086
  ssh ${SSH_OPTS:-} "${host}" "$(remote_env_prefix) ${extra_env} bash -s" "$@"
}

remote_env_optional() {
  local var="$1"
  if [[ -n "${!var:-}" ]]; then
    printf '%s=%s ' "${var}" "$(shell_quote "${!var}")"
  fi
}

remote_env_prefix() {
  printf 'GB10_AIDEN_IMAGE=%s ' "$(shell_quote "${GB10_AIDEN_IMAGE}")"
  printf 'GB10_AIDEN_CONTAINER_NAME=%s ' "$(shell_quote "${GB10_AIDEN_CONTAINER_NAME}")"
  printf 'GB10_AIDEN_HF_CACHE_REMOTE=%s ' "$(shell_quote "${GB10_AIDEN_HF_CACHE_REMOTE}")"
  printf 'GB10_AIDEN_HF_HUB_OFFLINE=%s ' "$(shell_quote "${GB10_AIDEN_HF_HUB_OFFLINE}")"
  printf 'GB10_AIDEN_API_PORT=%s ' "$(shell_quote "${GB10_AIDEN_API_PORT}")"
  printf 'GB10_AIDEN_MASTER_ADDR=%s ' "$(shell_quote "${GB10_AIDEN_MASTER_ADDR}")"
  printf 'GB10_AIDEN_MASTER_PORT=%s ' "$(shell_quote "${GB10_AIDEN_MASTER_PORT}")"
  printf 'GB10_AIDEN_MAX_MODEL_LEN=%s ' "$(shell_quote "${GB10_AIDEN_MAX_MODEL_LEN}")"
  printf 'GB10_AIDEN_MAX_NUM_SEQS=%s ' "$(shell_quote "${GB10_AIDEN_MAX_NUM_SEQS}")"
  printf 'GB10_AIDEN_MAX_NUM_BATCHED_TOKENS=%s ' "$(shell_quote "${GB10_AIDEN_MAX_NUM_BATCHED_TOKENS}")"
  printf 'GB10_AIDEN_GPU_MEMORY_UTILIZATION=%s ' "$(shell_quote "${GB10_AIDEN_GPU_MEMORY_UTILIZATION}")"
  printf 'GB10_AIDEN_BLOCK_SIZE=%s ' "$(shell_quote "${GB10_AIDEN_BLOCK_SIZE}")"
  printf 'GB10_AIDEN_KV_CACHE_DTYPE=%s ' "$(shell_quote "${GB10_AIDEN_KV_CACHE_DTYPE}")"
  printf 'GB10_AIDEN_PREFIX_CACHE_MODE=%s ' "$(shell_quote "${GB10_AIDEN_PREFIX_CACHE_MODE}")"
  printf 'GB10_AIDEN_SPECULATIVE_CONFIG=%s ' "$(shell_quote "${GB10_AIDEN_SPECULATIVE_CONFIG}")"
  printf 'GB10_AIDEN_SERVED_MODEL_NAME=%s ' "$(shell_quote "${GB10_AIDEN_SERVED_MODEL_NAME}")"
  printf 'GB10_AIDEN_MODEL_ID=%s ' "$(shell_quote "${GB10_AIDEN_MODEL_ID}")"
  printf 'GB10_AIDEN_TP_SIZE=%s ' "$(shell_quote "${GB10_AIDEN_TP_SIZE}")"
  printf 'GB10_AIDEN_PP_SIZE=%s ' "$(shell_quote "${GB10_AIDEN_PP_SIZE}")"
  printf 'GB10_AIDEN_NNODES=%s ' "$(shell_quote "${GB10_AIDEN_NNODES}")"
  printf 'GB10_AIDEN_SHM_SIZE=%s ' "$(shell_quote "${GB10_AIDEN_SHM_SIZE}")"
  printf 'GB10_AIDEN_RUNTIME=%s ' "$(shell_quote "${GB10_AIDEN_RUNTIME}")"
  printf 'GB10_AIDEN_DOCKER_PULL=%s ' "$(shell_quote "${GB10_AIDEN_DOCKER_PULL}")"
  printf 'GB10_AIDEN_REQUIRE_DROP_CACHES=%s ' "$(shell_quote "${GB10_AIDEN_REQUIRE_DROP_CACHES}")"
  printf 'GB10_AIDEN_ALLOW_CURRENT_BOOT_NVRM_OOM=%s ' "$(shell_quote "${GB10_AIDEN_ALLOW_CURRENT_BOOT_NVRM_OOM}")"
  printf 'GB10_AIDEN_ALLOW_DRIVER_SIGNALS=%s ' "$(shell_quote "${GB10_AIDEN_ALLOW_DRIVER_SIGNALS}")"
  printf 'GB10_AIDEN_DOCKER_EXTRA_ARGS=%s ' "$(shell_quote "${GB10_AIDEN_DOCKER_EXTRA_ARGS}")"
  printf 'GB10_AIDEN_SERVE_EXTRA_ARGS=%s ' "$(shell_quote "${GB10_AIDEN_SERVE_EXTRA_ARGS}")"
  printf 'GB10_AIDEN_NCCL_SO_PATH=%s ' "$(shell_quote "${GB10_AIDEN_NCCL_SO_PATH}")"
  printf 'ROCE_IFACE=%s ' "$(shell_quote "${ROCE_IFACE}")"
  printf 'NCCL_IB_HCA=%s ' "$(shell_quote "${NCCL_IB_HCA}")"
  remote_env_optional GB10_AIDEN_DOCKER_ENV_FILE
}

required_vars=(
  HEAD_HOST
  WORKER_HOST
  HEAD_ROCE_IP
  WORKER_ROCE_IP
  ROCE_IFACE
  NCCL_IB_HCA
  GB10_AIDEN_HF_CACHE_REMOTE
  GB10_AIDEN_REMOTE_HARNESS_ROOT
  GB10_AIDEN_BENCH_PYTHON
  GB10_AIDEN_BENCH_VLLM_BIN
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    printf 'missing required environment variable: %s\n' "${var}" >&2
    exit 2
  fi
done

RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-2x_gb10_sm121}"
GB10_AIDEN_LABEL="${GB10_AIDEN_LABEL:-gb10_aiden_image_parity}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${GB10_AIDEN_LABEL}/${RUN_TIMESTAMP}}"

GB10_AIDEN_IMAGE="${GB10_AIDEN_IMAGE:-aidendle94/sparkrun-vllm-ds4-gb10:production-ready}"
GB10_AIDEN_CONTAINER_NAME="${GB10_AIDEN_CONTAINER_NAME:-ds4_aiden_vllm}"
GB10_AIDEN_MODEL_ID="${GB10_AIDEN_MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
GB10_AIDEN_SERVED_MODEL_NAME="${GB10_AIDEN_SERVED_MODEL_NAME:-deepseek-v4-flash}"
GB10_AIDEN_API_PORT="${GB10_AIDEN_API_PORT:-8000}"
GB10_AIDEN_MASTER_ADDR="${GB10_AIDEN_MASTER_ADDR:-${HEAD_ROCE_IP}}"
GB10_AIDEN_MASTER_PORT="${GB10_AIDEN_MASTER_PORT:-25000}"
GB10_AIDEN_TP_SIZE="${GB10_AIDEN_TP_SIZE:-2}"
GB10_AIDEN_PP_SIZE="${GB10_AIDEN_PP_SIZE:-1}"
GB10_AIDEN_NNODES="${GB10_AIDEN_NNODES:-2}"
GB10_AIDEN_MAX_MODEL_LEN="${GB10_AIDEN_MAX_MODEL_LEN:-1000000}"
GB10_AIDEN_MAX_NUM_SEQS="${GB10_AIDEN_MAX_NUM_SEQS:-6}"
GB10_AIDEN_MAX_NUM_BATCHED_TOKENS="${GB10_AIDEN_MAX_NUM_BATCHED_TOKENS:-8192}"
GB10_AIDEN_GPU_MEMORY_UTILIZATION="${GB10_AIDEN_GPU_MEMORY_UTILIZATION:-0.82}"
GB10_AIDEN_BLOCK_SIZE="${GB10_AIDEN_BLOCK_SIZE:-256}"
GB10_AIDEN_KV_CACHE_DTYPE="${GB10_AIDEN_KV_CACHE_DTYPE:-fp8}"
GB10_AIDEN_PREFIX_CACHE_MODE="${GB10_AIDEN_PREFIX_CACHE_MODE:-enabled}"
GB10_AIDEN_SPECULATIVE_CONFIG="${GB10_AIDEN_SPECULATIVE_CONFIG:-{\"method\":\"mtp\",\"num_speculative_tokens\":2}}"
GB10_AIDEN_SHM_SIZE="${GB10_AIDEN_SHM_SIZE:-64g}"
GB10_AIDEN_RUNTIME="${GB10_AIDEN_RUNTIME:-}"
GB10_AIDEN_DOCKER_PULL="${GB10_AIDEN_DOCKER_PULL:-0}"
GB10_AIDEN_REQUIRE_DROP_CACHES="${GB10_AIDEN_REQUIRE_DROP_CACHES:-1}"
GB10_AIDEN_ALLOW_CURRENT_BOOT_NVRM_OOM="${GB10_AIDEN_ALLOW_CURRENT_BOOT_NVRM_OOM:-0}"
GB10_AIDEN_ALLOW_DRIVER_SIGNALS="${GB10_AIDEN_ALLOW_DRIVER_SIGNALS:-0}"
GB10_AIDEN_HF_HUB_OFFLINE="${GB10_AIDEN_HF_HUB_OFFLINE:-1}"
GB10_AIDEN_DOCKER_EXTRA_ARGS="${GB10_AIDEN_DOCKER_EXTRA_ARGS:-}"
GB10_AIDEN_SERVE_EXTRA_ARGS="${GB10_AIDEN_SERVE_EXTRA_ARGS:-}"
GB10_AIDEN_NCCL_SO_PATH="${GB10_AIDEN_NCCL_SO_PATH:-/opt/env/lib/python3.12/site-packages/nvidia/nccl/lib/libnccl.so.2}"
GB10_AIDEN_INPUT_LENS="${GB10_AIDEN_INPUT_LENS:-4096,16384,32768,65536,128000}"
GB10_AIDEN_OUTPUT_LEN="${GB10_AIDEN_OUTPUT_LEN:-128}"
GB10_AIDEN_CONCURRENCY="${GB10_AIDEN_CONCURRENCY:-1}"
GB10_AIDEN_NUM_PROMPTS="${GB10_AIDEN_NUM_PROMPTS:-2}"
GB10_AIDEN_BENCH_TIMEOUT="${GB10_AIDEN_BENCH_TIMEOUT:-1800}"
GB10_AIDEN_STARTUP_TIMEOUT="${GB10_AIDEN_STARTUP_TIMEOUT:-3600}"
GB10_AIDEN_STARTUP_INTERVAL_SECONDS="${GB10_AIDEN_STARTUP_INTERVAL_SECONDS:-15}"
GB10_AIDEN_SERVER_HEALTH_TIMEOUT="${GB10_AIDEN_SERVER_HEALTH_TIMEOUT:-10}"
GB10_AIDEN_STOP_AFTER_RUN="${GB10_AIDEN_STOP_AFTER_RUN:-1}"
GB10_AIDEN_DRY_RUN="${GB10_AIDEN_DRY_RUN:-0}"

mkdir -p "${OUT_DIR}"

stop_containers() {
  run_remote "${WORKER_HOST}" \
    "docker rm -f $(shell_quote "${GB10_AIDEN_CONTAINER_NAME}") >/dev/null 2>&1 || true"
  run_remote "${HEAD_HOST}" \
    "docker rm -f $(shell_quote "${GB10_AIDEN_CONTAINER_NAME}") >/dev/null 2>&1 || true"
}

reclaim_and_preflight_node() {
  local host="$1"
  local label="$2"
  local out_file="${OUT_DIR}/${label}_preflight.log"

  run_remote_script "${host}" "NODE_LABEL=$(shell_quote "${label}")" <<'REMOTE' \
    > "${out_file}" 2>&1
set -euo pipefail

print_mem_available() {
  local phase="$1"
  awk -v phase="${phase}" '/MemAvailable/ { printf "%s MemAvailable=%.1f GiB\n", phase, $2 / 1024 / 1024 }' /proc/meminfo
}

print_mem_available before_drop_caches
if sudo -n true >/dev/null 2>&1; then
  sudo -n sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
  printf 'drop_caches=ok on %s\n' "${NODE_LABEL}"
  print_mem_available after_drop_caches
elif [[ "${GB10_AIDEN_REQUIRE_DROP_CACHES}" != "0" ]]; then
  printf 'drop_caches required on %s; passwordless sudo unavailable; set GB10_AIDEN_REQUIRE_DROP_CACHES=0 to skip\n' \
    "${NODE_LABEL}" >&2
  exit 7
else
  printf 'warning: skipped drop_caches on %s\n' "${NODE_LABEL}" >&2
fi

if [[ "${GB10_AIDEN_ALLOW_CURRENT_BOOT_NVRM_OOM}" != "1" ]] \
    && journalctl -b -k --no-pager 2>/dev/null \
      | grep -E 'NVRM:.*(Out of memory|NV_ERR_NO_MEMORY)' >/dev/null; then
  printf 'current boot already has NVIDIA driver OOM on %s; reboot before retrying\n' \
    "${NODE_LABEL}" >&2
  exit 5
fi

docker version --format 'docker={{.Server.Version}}'
docker system df || true
REMOTE
}

start_container() {
  local host="$1"
  local rank="$2"
  local headless="$3"
  local label="$4"
  local stdout_log="${OUT_DIR}/${label}_docker_start.stdout.log"
  local stderr_log="${OUT_DIR}/${label}_docker_start.stderr.log"

  set +e
  run_remote_script "${host}" \
    "GB10_AIDEN_NODE_RANK=$(shell_quote "${rank}") GB10_AIDEN_HEADLESS=$(shell_quote "${headless}")" <<'REMOTE' \
    > "${stdout_log}" 2> "${stderr_log}"
set -euo pipefail

append_env_arg() {
  local name="$1"
  local value="$2"
  docker_args+=("-e" "${name}=${value}")
}

if [[ "${GB10_AIDEN_DOCKER_PULL}" == "1" ]]; then
  docker pull "${GB10_AIDEN_IMAGE}"
fi

docker rm -f "${GB10_AIDEN_CONTAINER_NAME}" >/dev/null 2>&1 || true

serve_cmd=(
  /usr/local/bin/dsv4-vllm-entrypoint
  serve
  "${GB10_AIDEN_MODEL_ID}"
  --served-model-name "${GB10_AIDEN_SERVED_MODEL_NAME}"
  --host 0.0.0.0
  --port "${GB10_AIDEN_API_PORT}"
  --trust-remote-code
  --tensor-parallel-size "${GB10_AIDEN_TP_SIZE}"
  --pipeline-parallel-size "${GB10_AIDEN_PP_SIZE}"
  --distributed-executor-backend mp
  --nnodes 2
  --node-rank "${GB10_AIDEN_NODE_RANK}"
  --master-addr "${GB10_AIDEN_MASTER_ADDR}"
  --master-port "${GB10_AIDEN_MASTER_PORT}"
  --kv-cache-dtype "${GB10_AIDEN_KV_CACHE_DTYPE}"
  --block-size "${GB10_AIDEN_BLOCK_SIZE}"
  --max-model-len "${GB10_AIDEN_MAX_MODEL_LEN}"
  --max-num-seqs "${GB10_AIDEN_MAX_NUM_SEQS}"
  --max-num-batched-tokens "${GB10_AIDEN_MAX_NUM_BATCHED_TOKENS}"
  --gpu-memory-utilization "${GB10_AIDEN_GPU_MEMORY_UTILIZATION}"
  --enable-flashinfer-autotune
  --speculative-config "${GB10_AIDEN_SPECULATIVE_CONFIG}"
  --tokenizer-mode deepseek_v4
  --tool-call-parser deepseek_v4
  --enable-auto-tool-choice
  --reasoning-parser deepseek_v4
  --reasoning-config '{"reasoning_parser":"deepseek_v4","reasoning_start_str":"","reasoning_end_str":""}'
  --default-chat-template-kwargs.thinking=true
  --default-chat-template-kwargs.reasoning_effort=high
)

case "${GB10_AIDEN_PREFIX_CACHE_MODE}" in
  enabled)
    serve_cmd+=(--enable-prefix-caching)
    ;;
  disabled)
    serve_cmd+=(--no-enable-prefix-caching)
    ;;
  auto)
    ;;
  *)
    printf 'invalid GB10_AIDEN_PREFIX_CACHE_MODE=%s\n' \
      "${GB10_AIDEN_PREFIX_CACHE_MODE}" >&2
    exit 2
    ;;
esac

if [[ "${GB10_AIDEN_HEADLESS}" == "1" ]]; then
  serve_cmd+=(--headless)
fi

docker_args=(
  run
  -d
  --rm
  --name "${GB10_AIDEN_CONTAINER_NAME}"
  --network host
  --ipc host
  --shm-size "${GB10_AIDEN_SHM_SIZE}"
  --ulimit memlock=-1
  --ulimit stack=67108864
  --gpus all
  --device=/dev/infiniband:/dev/infiniband
  -v "${GB10_AIDEN_HF_CACHE_REMOTE}:/cache/huggingface"
  -v /etc/passwd:/etc/passwd:ro
  -v /etc/group:/etc/group:ro
)

if [[ -n "${GB10_AIDEN_RUNTIME}" ]]; then
  docker_args+=(--runtime "${GB10_AIDEN_RUNTIME}")
fi

if [[ -n "${GB10_AIDEN_DOCKER_ENV_FILE:-}" ]]; then
  docker_args+=(--env-file "${GB10_AIDEN_DOCKER_ENV_FILE}")
fi

append_env_arg HF_HOME /cache/huggingface
append_env_arg HF_HUB_CACHE /cache/huggingface/hub
append_env_arg HF_HUB_OFFLINE "${GB10_AIDEN_HF_HUB_OFFLINE}"
append_env_arg VLLM_CACHE_ROOT /cache/huggingface/vllm-cache
append_env_arg TORCH_CUDA_ARCH_LIST 12.1a
append_env_arg FLASHINFER_CUDA_ARCH_LIST 12.1a
append_env_arg VLLM_ALLOW_LONG_MAX_MODEL_LEN 1
append_env_arg VLLM_USE_B12X_MOE 1
append_env_arg VLLM_SPARSE_INDEXER_MAX_LOGITS_MB 256
append_env_arg VLLM_NCCL_SO_PATH "${GB10_AIDEN_NCCL_SO_PATH}"
append_env_arg NCCL_NET IB
append_env_arg NCCL_SOCKET_IFNAME "${ROCE_IFACE}"
append_env_arg NCCL_IB_HCA "${NCCL_IB_HCA}"
append_env_arg NCCL_IB_DISABLE 0
append_env_arg NCCL_IB_GID_INDEX 3
append_env_arg NCCL_CROSS_NIC 1
append_env_arg NCCL_CUMEM_ENABLE 0
append_env_arg NCCL_IGNORE_CPU_AFFINITY 1
append_env_arg NCCL_DEBUG WARN
append_env_arg GLOO_SOCKET_IFNAME "${ROCE_IFACE}"
append_env_arg TP_SOCKET_IFNAME "${ROCE_IFACE}"
append_env_arg MN_IF_NAME "${ROCE_IFACE}"
append_env_arg OMPI_MCA_btl_tcp_if_include "${ROCE_IFACE}"

if [[ -n "${GB10_AIDEN_DOCKER_EXTRA_ARGS}" ]]; then
  # User-controlled passthrough for local-only experiments.
  # shellcheck disable=SC2206
  extra_docker_args=(${GB10_AIDEN_DOCKER_EXTRA_ARGS})
  docker_args+=("${extra_docker_args[@]}")
fi

serve_payload="$(printf '%q ' "${serve_cmd[@]}")"
if [[ -n "${GB10_AIDEN_SERVE_EXTRA_ARGS}" ]]; then
  serve_payload+="${GB10_AIDEN_SERVE_EXTRA_ARGS}"
fi

printf 'docker image: %s\n' "${GB10_AIDEN_IMAGE}"
printf 'serve command: %s\n' "${serve_payload}"
docker "${docker_args[@]}" "${GB10_AIDEN_IMAGE}" bash -lc "exec ${serve_payload}"
REMOTE
  local code="$?"
  set -e
  printf '%s\n' "${code}" > "${OUT_DIR}/${label}_docker_start.exit_code"
  return "${code}"
}

wait_for_container_server() {
  local started now elapsed
  started="$(date +%s)"
  while true; do
    if run_remote "${HEAD_HOST}" \
      "curl -fsS --max-time $(shell_quote "${GB10_AIDEN_SERVER_HEALTH_TIMEOUT}") http://127.0.0.1:$(shell_quote "${GB10_AIDEN_API_PORT}")/v1/models >/dev/null"; then
      printf '[%s] Aiden image server ready after %ss\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(( $(date +%s) - started ))" \
        >> "${OUT_DIR}/server_wait.log"
      return 0
    fi

    now="$(date +%s)"
    elapsed="$((now - started))"
    if (( elapsed >= GB10_AIDEN_STARTUP_TIMEOUT )); then
      printf '[%s] Aiden image server not ready after %ss\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${elapsed}" \
        >> "${OUT_DIR}/server_wait.log"
      return 1
    fi
    printf '[%s] waiting for Aiden image server: elapsed=%ss timeout=%ss\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${elapsed}" "${GB10_AIDEN_STARTUP_TIMEOUT}" \
      >> "${OUT_DIR}/server_wait.log"
    sleep "${GB10_AIDEN_STARTUP_INTERVAL_SECONDS}"
  done
}

run_remote_prefill_sweep() {
  local remote_out_dir="$1"
  run_remote "${HEAD_HOST}" \
    "cd $(shell_quote "${GB10_AIDEN_REMOTE_HARNESS_ROOT}") && env \
      PYTHON=$(shell_quote "${GB10_AIDEN_BENCH_PYTHON}") \
      VLLM_BIN=$(shell_quote "${GB10_AIDEN_BENCH_VLLM_BIN}") \
      MODEL=$(shell_quote "${GB10_AIDEN_SERVED_MODEL_NAME}") \
      HOST=127.0.0.1 \
      PORT=$(shell_quote "${GB10_AIDEN_API_PORT}") \
      BASE_URL=$(shell_quote "http://127.0.0.1:${GB10_AIDEN_API_PORT}") \
      GPU_TOPOLOGY_SLUG=$(shell_quote "${GPU_TOPOLOGY_SLUG}") \
      BRANCH_NAME=$(shell_quote "${GB10_AIDEN_LABEL}") \
      OUT_DIR=$(shell_quote "${remote_out_dir}") \
      RANDOM_PREFILL_BENCH_MODEL=$(shell_quote "${GB10_AIDEN_SERVED_MODEL_NAME}") \
      RANDOM_PREFILL_BENCH_TOKENIZER=$(shell_quote "${GB10_AIDEN_MODEL_ID}") \
      RANDOM_PREFILL_INPUT_LENS=$(shell_quote "${GB10_AIDEN_INPUT_LENS}") \
      RANDOM_PREFILL_OUTPUT_LEN=$(shell_quote "${GB10_AIDEN_OUTPUT_LEN}") \
      RANDOM_PREFILL_CONCURRENCY=$(shell_quote "${GB10_AIDEN_CONCURRENCY}") \
      RANDOM_PREFILL_NUM_PROMPTS=$(shell_quote "${GB10_AIDEN_NUM_PROMPTS}") \
      RANDOM_PREFILL_BENCH_TIMEOUT=$(shell_quote "${GB10_AIDEN_BENCH_TIMEOUT}") \
      RANDOM_PREFILL_TEMPERATURE=0.0 \
      RANDOM_PREFILL_IGNORE_EOS=1 \
      TOKENIZER_MODE=deepseek_v4 \
      $(shell_quote "${GB10_AIDEN_REMOTE_HARNESS_ROOT}/scripts/run_random_prefill_sweep.sh")"
}

fetch_remote_file() {
  local host="$1"
  local remote_path="$2"
  local local_path="$3"
  mkdir -p "$(dirname -- "${local_path}")"
  if run_remote "${host}" "test -f $(shell_quote "${remote_path}")"; then
    run_remote "${host}" "cat $(shell_quote "${remote_path}")" > "${local_path}"
  fi
}

fetch_remote_tree() {
  local host="$1"
  local remote_dir="$2"
  local local_dir="$3"
  local remote_parent remote_base
  remote_parent="$(dirname -- "${remote_dir}")"
  remote_base="$(basename -- "${remote_dir}")"
  mkdir -p "${local_dir}"
  if run_remote "${host}" "test -d $(shell_quote "${remote_dir}")"; then
    run_remote "${host}" \
      "cd $(shell_quote "${remote_parent}") && tar -cf - $(shell_quote "${remote_base}")" \
      | tar -C "${local_dir}" -xf -
  fi
}

capture_logs() {
  run_remote "${HEAD_HOST}" \
    "docker logs $(shell_quote "${GB10_AIDEN_CONTAINER_NAME}")" \
    > "${OUT_DIR}/serve_head.log" 2> "${OUT_DIR}/serve_head.log.stderr" || true
  run_remote "${WORKER_HOST}" \
    "docker logs $(shell_quote "${GB10_AIDEN_CONTAINER_NAME}")" \
    > "${OUT_DIR}/serve_worker.log" 2> "${OUT_DIR}/serve_worker.log.stderr" || true
  run_remote "${HEAD_HOST}" \
    "docker inspect $(shell_quote "${GB10_AIDEN_CONTAINER_NAME}")" \
    > "${OUT_DIR}/docker_inspect_head.json" 2> "${OUT_DIR}/docker_inspect_head.stderr" || true
  run_remote "${WORKER_HOST}" \
    "docker inspect $(shell_quote "${GB10_AIDEN_CONTAINER_NAME}")" \
    > "${OUT_DIR}/docker_inspect_worker.json" 2> "${OUT_DIR}/docker_inspect_worker.stderr" || true
}

capture_remote_driver_health() {
  local host="$1"
  local label="$2"
  local out_dir="$3"
  local host_dir="${out_dir}/${label}"
  local signal_pattern
  signal_pattern='NVRM:.*(Out of memory|NV_ERR_NO_MEMORY)|Xid|UVM|lost from the bus|fallen off|GPU lost|unspecified launch failure|illegal memory access|device-side assert|global fatal'

  mkdir -p "${host_dir}"
  run_remote "${host}" \
    "date -Ins; hostname; uname -a; uptime" \
    > "${host_dir}/system.txt" 2>&1 || true
  run_remote "${host}" \
    "nvidia-smi; nvidia-smi pmon -c 1 || true" \
    > "${host_dir}/nvidia_smi.txt" 2>&1 || true
  run_remote "${host}" \
    "journalctl -b -k --no-pager | grep -Ei $(shell_quote "${signal_pattern}") | tail -n 200 || true" \
    > "${host_dir}/kernel_gpu_signals.log" 2>&1 || true
}

write_driver_health_summary() {
  local driver_health_dir="${OUT_DIR}/driver_health"
  local driver_health_signal_count=0
  local driver_health_ok
  local signal_file file_count

  capture_remote_driver_health "${HEAD_HOST}" head "${driver_health_dir}"
  capture_remote_driver_health "${WORKER_HOST}" worker "${driver_health_dir}"

  for signal_file in \
      "${driver_health_dir}/head/kernel_gpu_signals.log" \
      "${driver_health_dir}/worker/kernel_gpu_signals.log"; do
    if [[ -s "${signal_file}" ]]; then
      file_count="$(wc -l < "${signal_file}" | tr -d '[:space:]')"
      driver_health_signal_count="$((driver_health_signal_count + file_count))"
    fi
  done

  if [[ "${driver_health_signal_count}" == "0" \
      || "${GB10_AIDEN_ALLOW_DRIVER_SIGNALS}" == "1" ]]; then
    driver_health_ok=1
  else
    driver_health_ok=0
  fi
  printf '%s\n' "${driver_health_ok}" > "${OUT_DIR}/driver_health.ok"
  printf '%s\n' "${driver_health_signal_count}" \
    > "${OUT_DIR}/driver_health_signal_count.txt"

  DRIVER_HEALTH_ROOT="${driver_health_dir}" \
  DRIVER_HEALTH_OK="${driver_health_ok}" \
  DRIVER_HEALTH_SIGNAL_COUNT="${driver_health_signal_count}" \
  DRIVER_HEALTH_ALLOW="${GB10_AIDEN_ALLOW_DRIVER_SIGNALS}" \
  python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["DRIVER_HEALTH_ROOT"])
hosts = {}
for label in ("head", "worker"):
    signal_path = root / label / "kernel_gpu_signals.log"
    text = ""
    if signal_path.exists():
        text = signal_path.read_text(encoding="utf-8", errors="replace")
    lines = [line for line in text.splitlines() if line.strip()]
    hosts[label] = {
        "signal_count": len(lines),
        "signals_path": str(signal_path),
        "has_signals": bool(lines),
    }

payload = {
    "ok": os.environ["DRIVER_HEALTH_OK"] == "1",
    "allow_driver_signals": os.environ["DRIVER_HEALTH_ALLOW"] == "1",
    "signal_count": int(os.environ["DRIVER_HEALTH_SIGNAL_COUNT"]),
    "hosts": hosts,
}
(root.parent / "driver_health_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
}

write_summary() {
  local startup_code="$1"
  local bench_code="$2"
  local remote_bench_dir="$3"
  local ok="$4"

  GB10_AIDEN_SUMMARY_ROOT="${OUT_DIR}" \
  GB10_AIDEN_STARTUP_CODE="${startup_code}" \
  GB10_AIDEN_BENCH_CODE="${bench_code}" \
  GB10_AIDEN_REMOTE_BENCH_DIR="${remote_bench_dir}" \
  GB10_AIDEN_OK="${ok}" \
  GB10_AIDEN_IMAGE="${GB10_AIDEN_IMAGE}" \
  GB10_AIDEN_MAX_MODEL_LEN="${GB10_AIDEN_MAX_MODEL_LEN}" \
  GB10_AIDEN_MAX_NUM_SEQS="${GB10_AIDEN_MAX_NUM_SEQS}" \
  GB10_AIDEN_MAX_NUM_BATCHED_TOKENS="${GB10_AIDEN_MAX_NUM_BATCHED_TOKENS}" \
  GB10_AIDEN_GPU_MEMORY_UTILIZATION="${GB10_AIDEN_GPU_MEMORY_UTILIZATION}" \
  GB10_AIDEN_PREFIX_CACHE_MODE="${GB10_AIDEN_PREFIX_CACHE_MODE}" \
  GB10_AIDEN_SPECULATIVE_CONFIG="${GB10_AIDEN_SPECULATIVE_CONFIG}" \
  GB10_AIDEN_INPUT_LENS="${GB10_AIDEN_INPUT_LENS}" \
  GB10_AIDEN_CONCURRENCY="${GB10_AIDEN_CONCURRENCY}" \
  GB10_AIDEN_OUTPUT_LEN="${GB10_AIDEN_OUTPUT_LEN}" \
  python3 - <<'PY'
import json
import os
import re
from pathlib import Path
from typing import Any

root = Path(os.environ["GB10_AIDEN_SUMMARY_ROOT"])


def load_json(path: Path, fallback: Any) -> Any:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback
    return value


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def redact(value: str) -> str:
    value = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip>", value)
    value = re.sub(r"(?<![\w.-])/(?:home|Users)/[^\s,'\")]+", "<path>", value)
    return value


def unique_limited(values: list[str], limit: int = 10) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in values:
        clean = redact(" ".join(raw.strip().split()))
        if not clean or clean in seen:
            continue
        seen.add(clean)
        out.append(clean)
        if len(out) >= limit:
            break
    return out


def extract_backend_evidence() -> dict[str, list[str]]:
    logs = {
        "head": load_text(root / "serve_head.log"),
        "worker": load_text(root / "serve_worker.log"),
    }
    patterns = {
        "b12x": (
            "B12X",
            "b12x",
            "compressed_indexer",
            "sparse_mla_scratch",
            "VLLM_USE_B12X_MOE",
        ),
        "flashinfer": (
            "FLASHINFER",
            "FlashInfer",
            "flashinfer",
            "enable-flashinfer-autotune",
        ),
        "sparse_mla": (
            "sparse MLA",
            "fp8_ds_mla",
            "Using FP8 indexer cache",
            "DeepSeek V4 sparse MLA",
        ),
        "moe": (
            "Mxfp4 MoE backend",
            "MoEPrepareAndFinalize",
            "MXFP4",
        ),
        "nccl": (
            "vLLM is using nccl==",
            "PYNCCL",
            "NCCL",
            "all-reduce",
        ),
        "mtp": (
            "speculative",
            "num_speculative_tokens",
            "DeepSeekV4MTP",
            "MTP",
        ),
    }
    evidence: dict[str, list[str]] = {}
    for key, needles in patterns.items():
        matches: list[str] = []
        for node, text in logs.items():
            for line in text.splitlines():
                if any(needle in line for needle in needles):
                    matches.append(f"{node}: {line}")
        evidence[key] = unique_limited(matches)
    return evidence


bench_summary = load_json(root / "prefill_sweep_summary.json", {})
driver_health = load_json(
    root / "driver_health_summary.json",
    {"available": False, "ok": True, "signal_count": 0, "hosts": {}},
)
backend_evidence = extract_backend_evidence()
startup_code = int(os.environ["GB10_AIDEN_STARTUP_CODE"])
bench_code = int(os.environ["GB10_AIDEN_BENCH_CODE"])
ok = os.environ["GB10_AIDEN_OK"] == "1"
summary = {
    "case": "gb10_aiden_image_parity",
    "ok": ok,
    "startup_exit_code": startup_code,
    "bench_exit_code": bench_code,
    "image": os.environ["GB10_AIDEN_IMAGE"],
    "serve_profile": {
        "max_model_len": int(os.environ["GB10_AIDEN_MAX_MODEL_LEN"]),
        "max_num_seqs": int(os.environ["GB10_AIDEN_MAX_NUM_SEQS"]),
        "max_num_batched_tokens": int(
            os.environ["GB10_AIDEN_MAX_NUM_BATCHED_TOKENS"]
        ),
        "gpu_memory_utilization": os.environ[
            "GB10_AIDEN_GPU_MEMORY_UTILIZATION"
        ],
        "prefix_cache_mode": os.environ["GB10_AIDEN_PREFIX_CACHE_MODE"],
        "speculative_config": os.environ["GB10_AIDEN_SPECULATIVE_CONFIG"],
    },
    "workload": {
        "input_lens": os.environ["GB10_AIDEN_INPUT_LENS"],
        "concurrency": os.environ["GB10_AIDEN_CONCURRENCY"],
        "output_len": os.environ["GB10_AIDEN_OUTPUT_LEN"],
    },
    "remote_bench_dir": os.environ["GB10_AIDEN_REMOTE_BENCH_DIR"],
    "prefill_sweep": bench_summary,
    "backend_evidence": backend_evidence,
    "driver_health": driver_health,
}
(root / "gb10_aiden_image_parity_summary.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

lines = [
    "# GB10 Aiden Image Parity",
    "",
    f"- OK: `{summary['ok']}`",
    f"- Image: `{summary['image']}`",
    f"- Startup exit: `{startup_code}`",
    f"- Benchmark exit: `{bench_code}`",
    f"- Driver health OK: `{driver_health.get('ok', True)}`",
    f"- Driver signal count: `{driver_health.get('signal_count', 0)}`",
    f"- Remote benchmark dir: `{summary['remote_bench_dir']}`",
    "",
    "## Serve Profile",
    "",
    "| max_model_len | max_num_seqs | max_num_batched_tokens | gpu_memory_utilization | prefix cache | speculative config |",
    "| ---: | ---: | ---: | ---: | --- | --- |",
    "| {max_model_len} | {max_num_seqs} | {max_num_batched_tokens} | {gpu_memory_utilization} | `{prefix_cache_mode}` | `{speculative_config}` |".format(
        **summary["serve_profile"]
    ),
    "",
    "## Prefill Sweep",
    "",
]
rows = bench_summary.get("rows", []) if isinstance(bench_summary, dict) else []
lines.extend(
    [
        "| Case | OK | C | Input tok/s | Decode tok/s | Mean TTFT ms | P99 ITL ms |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
)
for row in rows if isinstance(rows, list) else []:
    lines.append(
        "| `{case}` | {ok} | {concurrency} | {input_tps} | {decode_tps} | {ttft} | {itl} |".format(
            case=row.get("case", "n/a"),
            ok="yes" if row.get("ok") else "no",
            concurrency=row.get("concurrency", "n/a"),
            input_tps=row.get("input_token_throughput_tok_s", "n/a"),
            decode_tps=row.get("output_token_throughput_tok_s", "n/a"),
            ttft=row.get("mean_ttft_ms", "n/a"),
            itl=row.get("p99_itl_ms", "n/a"),
        )
    )
lines.extend(["", "## Backend Evidence", ""])
for key, values in backend_evidence.items():
    lines.append(f"### {key}")
    lines.append("")
    if values:
        lines.extend(f"- `{value}`" for value in values)
    else:
        lines.append("- n/a")
    lines.append("")

if not driver_health.get("ok", True):
    lines.extend(["## Driver Health", ""])
    for label, host in driver_health.get("hosts", {}).items():
        lines.append(
            f"- `{label}`: {host.get('signal_count', 0)} signal(s), "
            f"`{host.get('signals_path', '')}`"
        )
    lines.append("")

(root / "gb10_aiden_image_parity_summary.md").write_text(
    "\n".join(lines).rstrip() + "\n",
    encoding="utf-8",
)
PY
}

remote_bench_dir="${GB10_AIDEN_REMOTE_HARNESS_ROOT}/artifacts/${GB10_AIDEN_LABEL}/${RUN_TIMESTAMP}/random_prefill_sweep"
printf '%s\n' "${remote_bench_dir}" > "${OUT_DIR}/remote_bench_dir.txt"

startup_code=1
bench_code=125
ok=0

if [[ "${GB10_AIDEN_DRY_RUN}" == "1" ]]; then
  startup_code=0
  bench_code=0
  ok=1
  write_summary "${startup_code}" "${bench_code}" "${remote_bench_dir}" "${ok}"
  printf '%s\n' 0 > "${OUT_DIR}/gb10_aiden_image_parity.exit_code"
  echo "wrote ${OUT_DIR}"
  exit 0
fi

stop_containers
reclaim_and_preflight_node "${WORKER_HOST}" worker
reclaim_and_preflight_node "${HEAD_HOST}" head

if start_container "${WORKER_HOST}" 1 1 worker && start_container "${HEAD_HOST}" 0 0 head; then
  if wait_for_container_server; then
    startup_code=0
    set +e
    run_remote_prefill_sweep "${remote_bench_dir}" \
      > "${OUT_DIR}/prefill_sweep.stdout.log" \
      2> "${OUT_DIR}/prefill_sweep.stderr.log"
    bench_code="$?"
    set -e
  else
    startup_code=124
  fi
fi

fetch_remote_file "${HEAD_HOST}" \
  "${remote_bench_dir}/prefill_sweep_summary.json" \
  "${OUT_DIR}/prefill_sweep_summary.json"
fetch_remote_file "${HEAD_HOST}" \
  "${remote_bench_dir}/prefill_sweep_summary.md" \
  "${OUT_DIR}/prefill_sweep_summary.md"
fetch_remote_tree "${HEAD_HOST}" "${remote_bench_dir}" "${OUT_DIR}/remote_prefill_sweep"
capture_logs
write_driver_health_summary

if [[ "${GB10_AIDEN_STOP_AFTER_RUN}" == "1" ]]; then
  stop_containers
fi

driver_health_ok="$(cat "${OUT_DIR}/driver_health.ok" 2>/dev/null || printf '1')"
if [[ "${startup_code}" == "0" && "${bench_code}" == "0" \
    && "${driver_health_ok}" == "1" ]]; then
  ok=1
fi
write_summary "${startup_code}" "${bench_code}" "${remote_bench_dir}" "${ok}"
printf '%s\n' "$(( ok == 1 ? 0 : 1 ))" > "${OUT_DIR}/gb10_aiden_image_parity.exit_code"
echo "wrote ${OUT_DIR}"
exit "$(( ok == 1 ? 0 : 1 ))"
