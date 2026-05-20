#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
NEEDLE_POSITION_MATRIX_VARIANT="${NEEDLE_POSITION_MATRIX_VARIANT:-manual}"
NEEDLE_POSITION_MATRIX_CASE_NAME="${NEEDLE_POSITION_MATRIX_CASE_NAME:-needle_position_matrix}"
NEEDLE_POSITION_MATRIX_LINE_COUNTS="${NEEDLE_POSITION_MATRIX_LINE_COUNTS:-4000}"
NEEDLE_POSITION_MATRIX_POSITIONS="${NEEDLE_POSITION_MATRIX_POSITIONS:-0,7,14,21,28,35,42,50,57,64,71,78,85,92,100}"
NEEDLE_POSITION_MATRIX_REPEAT_COUNT="${NEEDLE_POSITION_MATRIX_REPEAT_COUNT:-1}"
NEEDLE_POSITION_MATRIX_MAX_TOKENS="${NEEDLE_POSITION_MATRIX_MAX_TOKENS:-64}"
NEEDLE_POSITION_MATRIX_TEMPERATURE="${NEEDLE_POSITION_MATRIX_TEMPERATURE:-0.0}"
NEEDLE_POSITION_MATRIX_TOP_P="${NEEDLE_POSITION_MATRIX_TOP_P:-1.0}"
NEEDLE_POSITION_MATRIX_THINKING_MODE="${NEEDLE_POSITION_MATRIX_THINKING_MODE:-non-thinking}"
NEEDLE_POSITION_MATRIX_TIMEOUT="${NEEDLE_POSITION_MATRIX_TIMEOUT:-3600}"
SERVE_LOG="${SERVE_LOG:-}"
SERVER_GUARD="${SERVER_GUARD:-1}"
SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT:-1800}"
SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS:-15}"
SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT:-10}"
SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT:-300}"
SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS:-10}"
SERVER_RECOVERY_CMD="${SERVER_RECOVERY_CMD:-}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/needle_position_matrix/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON NEEDLE_POSITION_MATRIX_VARIANT
export NEEDLE_POSITION_MATRIX_CASE_NAME NEEDLE_POSITION_MATRIX_LINE_COUNTS
export NEEDLE_POSITION_MATRIX_POSITIONS NEEDLE_POSITION_MATRIX_REPEAT_COUNT
export NEEDLE_POSITION_MATRIX_MAX_TOKENS NEEDLE_POSITION_MATRIX_TEMPERATURE
export NEEDLE_POSITION_MATRIX_TOP_P NEEDLE_POSITION_MATRIX_THINKING_MODE
export NEEDLE_POSITION_MATRIX_TIMEOUT
export SERVE_LOG SERVER_GUARD SERVER_STARTUP_TIMEOUT
export SERVER_STARTUP_INTERVAL_SECONDS SERVER_HEALTH_TIMEOUT
export SERVER_FAILURE_GRACE_TIMEOUT SERVER_FAILURE_GRACE_INTERVAL_SECONDS
export SERVER_RECOVERY_CMD ARTIFACT_ROOT RUN_TIMESTAMP BRANCH_NAME GPU_TOPOLOGY_SLUG OUT_DIR

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/vllm_collect_env.sh"
collect_vllm_env
source "${SCRIPT_DIR}/gpu_stats.sh"
source "${SCRIPT_DIR}/runtime_stats.sh"
start_gpu_stats
start_runtime_stats
trap 'stop_runtime_stats; stop_gpu_stats' EXIT

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before needle position matrix"; then
  printf '%s\n' "124" > "${OUT_DIR}/needle_position_matrix.exit_code"
  mark_server_unresponsive "needle_position_matrix" "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

set +e
"${PYTHON}" -m ds4_harness.cli needle-position-matrix \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --variant "${NEEDLE_POSITION_MATRIX_VARIANT}" \
  --case-name "${NEEDLE_POSITION_MATRIX_CASE_NAME}" \
  --line-counts "${NEEDLE_POSITION_MATRIX_LINE_COUNTS}" \
  --positions "${NEEDLE_POSITION_MATRIX_POSITIONS}" \
  --repeat-count "${NEEDLE_POSITION_MATRIX_REPEAT_COUNT}" \
  --max-tokens "${NEEDLE_POSITION_MATRIX_MAX_TOKENS}" \
  --temperature "${NEEDLE_POSITION_MATRIX_TEMPERATURE}" \
  --top-p "${NEEDLE_POSITION_MATRIX_TOP_P}" \
  --thinking-mode "${NEEDLE_POSITION_MATRIX_THINKING_MODE}" \
  --timeout "${NEEDLE_POSITION_MATRIX_TIMEOUT}" \
  --json-output "${OUT_DIR}/needle_position_matrix.json" \
  --markdown-output "${OUT_DIR}/needle_position_matrix.md"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/needle_position_matrix.exit_code"
if [[ "${code}" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after needle position matrix"; then
  mark_server_unresponsive "needle_position_matrix" "server unresponsive after needle position matrix"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
