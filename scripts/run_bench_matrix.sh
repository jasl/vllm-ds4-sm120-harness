#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

VLLM_BIN="${VLLM_BIN:-vllm}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
HOST="${HOST:-localhost}"
PORT="${PORT:-8000}"
BASE_URL="${BASE_URL:-http://${HOST}:${PORT}}"
CONCURRENCY="${CONCURRENCY:-1,2,4,8,16,24}"
DATASET_NAME="${DATASET_NAME:-hf}"
DATASET_PATH="${DATASET_PATH:-philschmid/mt-bench}"
TOKENIZER_MODE="${TOKENIZER_MODE:-deepseek_v4}"
NUM_PROMPTS="${NUM_PROMPTS:-80}"
BENCH_TIMEOUT="${BENCH_TIMEOUT:-1800}"
RANDOM_INPUT_LEN="${RANDOM_INPUT_LEN:-1024}"
RANDOM_OUTPUT_LEN="${RANDOM_OUTPUT_LEN:-1024}"
TEMPERATURE="${TEMPERATURE:-1.0}"
IGNORE_EOS="${IGNORE_EOS:-0}"
PYTHON="${PYTHON:-python}"
SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT:-1800}"
SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS:-15}"
SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT:-10}"
SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT:-300}"
SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS:-10}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${RUN_TIMESTAMP}}"
export VLLM_BIN MODEL HOST PORT BASE_URL CONCURRENCY DATASET_NAME DATASET_PATH
export TOKENIZER_MODE NUM_PROMPTS BENCH_TIMEOUT RANDOM_INPUT_LEN RANDOM_OUTPUT_LEN
export TEMPERATURE IGNORE_EOS PYTHON ARTIFACT_ROOT RUN_TIMESTAMP BRANCH_NAME
export SERVER_STARTUP_TIMEOUT SERVER_STARTUP_INTERVAL_SECONDS SERVER_HEALTH_TIMEOUT
export SERVER_FAILURE_GRACE_TIMEOUT SERVER_FAILURE_GRACE_INTERVAL_SECONDS
export GPU_TOPOLOGY_SLUG OUT_DIR

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/gpu_stats.sh"
source "${SCRIPT_DIR}/runtime_stats.sh"
start_gpu_stats
start_runtime_stats
trap 'stop_runtime_stats; stop_gpu_stats' EXIT

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before benchmark"; then
  printf '%s\n' "124" > "${OUT_DIR}/bench.exit_code"
  mark_server_unresponsive "bench" "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

EXTRA_ARGS=()
if [[ "${IGNORE_EOS}" == "1" || "${IGNORE_EOS}" == "true" ]]; then
  EXTRA_ARGS+=(--ignore-eos)
fi

"${PYTHON}" -m ds4_harness.cli bench-matrix \
  --vllm-bin "${VLLM_BIN}" \
  --model "${MODEL}" \
  --tokenizer-mode "${TOKENIZER_MODE}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --base-url "${BASE_URL}" \
  --concurrency "${CONCURRENCY}" \
  --dataset-name "${DATASET_NAME}" \
  --dataset-path "${DATASET_PATH}" \
  --random-input-len "${RANDOM_INPUT_LEN}" \
  --random-output-len "${RANDOM_OUTPUT_LEN}" \
  --num-prompts "${NUM_PROMPTS}" \
  --temperature "${TEMPERATURE}" \
  --timeout "${BENCH_TIMEOUT}" \
  --stop-on-unresponsive \
  --health-timeout "${SERVER_HEALTH_TIMEOUT}" \
  --failure-grace-timeout "${SERVER_FAILURE_GRACE_TIMEOUT}" \
  --failure-grace-interval "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
  ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"} \
  --json-output "${OUT_DIR}/bench.json" \
  --log-dir "${OUT_DIR}/logs"

echo "wrote ${OUT_DIR}"
