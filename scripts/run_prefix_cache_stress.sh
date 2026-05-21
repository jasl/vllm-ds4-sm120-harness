#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
PREFIX_CACHE_STRESS_CASE_NAME="${PREFIX_CACHE_STRESS_CASE_NAME:-user_report_prefix_cache_http_metrics_stress}"
PREFIX_CACHE_STRESS_TRIALS="${PREFIX_CACHE_STRESS_TRIALS:-5}"
PREFIX_CACHE_STRESS_FILLER_WORDS="${PREFIX_CACHE_STRESS_FILLER_WORDS:-800}"
PREFIX_CACHE_STRESS_TURNS="${PREFIX_CACHE_STRESS_TURNS:-3}"
PREFIX_CACHE_STRESS_MAX_TOKENS="${PREFIX_CACHE_STRESS_MAX_TOKENS:-256}"
PREFIX_CACHE_STRESS_TEMPERATURE="${PREFIX_CACHE_STRESS_TEMPERATURE:-1.0}"
PREFIX_CACHE_STRESS_TOP_P="${PREFIX_CACHE_STRESS_TOP_P:-1.0}"
PREFIX_CACHE_STRESS_TIMEOUT="${PREFIX_CACHE_STRESS_TIMEOUT:-180}"
PREFIX_CACHE_STRESS_METRICS_TIMEOUT="${PREFIX_CACHE_STRESS_METRICS_TIMEOUT:-10}"
PREFIX_CACHE_STRESS_HEALTH_TIMEOUT="${PREFIX_CACHE_STRESS_HEALTH_TIMEOUT:-10}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/prefix_cache_stress/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON PREFIX_CACHE_STRESS_CASE_NAME
export PREFIX_CACHE_STRESS_TRIALS PREFIX_CACHE_STRESS_FILLER_WORDS
export PREFIX_CACHE_STRESS_TURNS PREFIX_CACHE_STRESS_MAX_TOKENS
export PREFIX_CACHE_STRESS_TEMPERATURE PREFIX_CACHE_STRESS_TOP_P
export PREFIX_CACHE_STRESS_TIMEOUT PREFIX_CACHE_STRESS_METRICS_TIMEOUT
export PREFIX_CACHE_STRESS_HEALTH_TIMEOUT SERVE_LOG SERVER_GUARD
export SERVER_STARTUP_TIMEOUT SERVER_STARTUP_INTERVAL_SECONDS
export SERVER_HEALTH_TIMEOUT SERVER_FAILURE_GRACE_TIMEOUT
export SERVER_FAILURE_GRACE_INTERVAL_SECONDS SERVER_RECOVERY_CMD ARTIFACT_ROOT
export RUN_TIMESTAMP BRANCH_NAME GPU_TOPOLOGY_SLUG OUT_DIR

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/vllm_collect_env.sh"
collect_vllm_env
source "${SCRIPT_DIR}/gpu_stats.sh"
source "${SCRIPT_DIR}/runtime_stats.sh"
start_gpu_stats
start_runtime_stats
trap 'stop_runtime_stats; stop_gpu_stats' EXIT

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before prefix-cache stress"; then
  printf '%s\n' "124" > "${OUT_DIR}/prefix_cache_stress.exit_code"
  mark_server_unresponsive "prefix_cache_stress" "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

set +e
"${PYTHON}" -m ds4_harness.cli prefix-cache-stress \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --case-name "${PREFIX_CACHE_STRESS_CASE_NAME}" \
  --trials "${PREFIX_CACHE_STRESS_TRIALS}" \
  --filler-words "${PREFIX_CACHE_STRESS_FILLER_WORDS}" \
  --turns "${PREFIX_CACHE_STRESS_TURNS}" \
  --max-tokens "${PREFIX_CACHE_STRESS_MAX_TOKENS}" \
  --temperature "${PREFIX_CACHE_STRESS_TEMPERATURE}" \
  --top-p "${PREFIX_CACHE_STRESS_TOP_P}" \
  --timeout "${PREFIX_CACHE_STRESS_TIMEOUT}" \
  --metrics-timeout "${PREFIX_CACHE_STRESS_METRICS_TIMEOUT}" \
  --health-timeout "${PREFIX_CACHE_STRESS_HEALTH_TIMEOUT}" \
  --json-output "${OUT_DIR}/prefix_cache_stress.json" \
  --markdown-output "${OUT_DIR}/prefix_cache_stress.md"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/prefix_cache_stress.exit_code"
if [[ "${code}" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after prefix-cache stress"; then
  mark_server_unresponsive "prefix_cache_stress" "server unresponsive after prefix-cache stress"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
