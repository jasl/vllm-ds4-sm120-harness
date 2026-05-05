#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
PREFIX_CACHE_VARIANT="${PREFIX_CACHE_VARIANT:-manual}"
PREFIX_CACHE_CASE_NAME="${PREFIX_CACHE_CASE_NAME:-prefix_cache_interleaved_long_conversation}"
PREFIX_CACHE_LINE_COUNT="${PREFIX_CACHE_LINE_COUNT:-2400}"
PREFIX_CACHE_MAX_TOKENS="${PREFIX_CACHE_MAX_TOKENS:-64}"
PREFIX_CACHE_TEMPERATURE="${PREFIX_CACHE_TEMPERATURE:-0.0}"
PREFIX_CACHE_TOP_P="${PREFIX_CACHE_TOP_P:-1.0}"
PREFIX_CACHE_THINKING_MODE="${PREFIX_CACHE_THINKING_MODE:-non-thinking}"
PREFIX_CACHE_TIMEOUT="${PREFIX_CACHE_TIMEOUT:-1800}"
PREFIX_CACHE_REQUEST_RETRIES="${PREFIX_CACHE_REQUEST_RETRIES:-${API_REQUEST_RETRIES:-1}}"
PREFIX_CACHE_REGRESSION_TTFT_RATIO="${PREFIX_CACHE_REGRESSION_TTFT_RATIO:-3.0}"
PREFIX_CACHE_FAIL_ON_REGRESSION="${PREFIX_CACHE_FAIL_ON_REGRESSION:-0}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/prefix_cache_probe/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON PREFIX_CACHE_VARIANT PREFIX_CACHE_CASE_NAME
export PREFIX_CACHE_LINE_COUNT PREFIX_CACHE_MAX_TOKENS PREFIX_CACHE_TEMPERATURE
export PREFIX_CACHE_TOP_P PREFIX_CACHE_THINKING_MODE PREFIX_CACHE_TIMEOUT
export PREFIX_CACHE_REQUEST_RETRIES PREFIX_CACHE_REGRESSION_TTFT_RATIO
export PREFIX_CACHE_FAIL_ON_REGRESSION SERVE_LOG SERVER_GUARD SERVER_STARTUP_TIMEOUT
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

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before prefix-cache probe"; then
  printf '%s\n' "124" > "${OUT_DIR}/prefix_cache_probe.exit_code"
  mark_server_unresponsive "prefix_cache_probe" "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

regression_args=()
if [[ "${PREFIX_CACHE_FAIL_ON_REGRESSION}" == "1" || "${PREFIX_CACHE_FAIL_ON_REGRESSION}" == "true" ]]; then
  regression_args+=(--fail-on-regression)
fi

set +e
"${PYTHON}" -m ds4_harness.cli prefix-cache-probe \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --variant "${PREFIX_CACHE_VARIANT}" \
  --case-name "${PREFIX_CACHE_CASE_NAME}" \
  --line-count "${PREFIX_CACHE_LINE_COUNT}" \
  --max-tokens "${PREFIX_CACHE_MAX_TOKENS}" \
  --temperature "${PREFIX_CACHE_TEMPERATURE}" \
  --top-p "${PREFIX_CACHE_TOP_P}" \
  --thinking-mode "${PREFIX_CACHE_THINKING_MODE}" \
  --timeout "${PREFIX_CACHE_TIMEOUT}" \
  --request-retries "${PREFIX_CACHE_REQUEST_RETRIES}" \
  --regression-ttft-ratio "${PREFIX_CACHE_REGRESSION_TTFT_RATIO}" \
  ${regression_args[@]+"${regression_args[@]}"} \
  --json-output "${OUT_DIR}/prefix_cache_probe.json" \
  --markdown-output "${OUT_DIR}/prefix_cache_probe.md"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/prefix_cache_probe.exit_code"
if [[ "${code}" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after prefix-cache probe"; then
  mark_server_unresponsive "prefix_cache_probe" "server unresponsive after prefix-cache probe"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
