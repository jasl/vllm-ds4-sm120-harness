#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
KV_LIFECYCLE_VARIANT="${KV_LIFECYCLE_VARIANT:-manual}"
KV_LIFECYCLE_CASE_NAME="${KV_LIFECYCLE_CASE_NAME:-kv_lifecycle_idle_recovery}"
KV_LIFECYCLE_CACHE_MODE="${KV_LIFECYCLE_CACHE_MODE:-disabled}"
KV_LIFECYCLE_SESSION_COUNT="${KV_LIFECYCLE_SESSION_COUNT:-3}"
KV_LIFECYCLE_LINE_COUNT="${KV_LIFECYCLE_LINE_COUNT:-1900}"
KV_LIFECYCLE_MAX_TOKENS="${KV_LIFECYCLE_MAX_TOKENS:-64}"
KV_LIFECYCLE_TEMPERATURE="${KV_LIFECYCLE_TEMPERATURE:-0.0}"
KV_LIFECYCLE_TOP_P="${KV_LIFECYCLE_TOP_P:-1.0}"
KV_LIFECYCLE_THINKING_MODE="${KV_LIFECYCLE_THINKING_MODE:-non-thinking}"
KV_LIFECYCLE_TIMEOUT="${KV_LIFECYCLE_TIMEOUT:-1800}"
KV_LIFECYCLE_METRICS_TIMEOUT="${KV_LIFECYCLE_METRICS_TIMEOUT:-10}"
KV_LIFECYCLE_SETTLE_TIMEOUT="${KV_LIFECYCLE_SETTLE_TIMEOUT:-60}"
KV_LIFECYCLE_SETTLE_INTERVAL="${KV_LIFECYCLE_SETTLE_INTERVAL:-2}"
KV_LIFECYCLE_MAX_IDLE_KV_PERCENT="${KV_LIFECYCLE_MAX_IDLE_KV_PERCENT:-}"
KV_LIFECYCLE_INCLUDE_ABORT="${KV_LIFECYCLE_INCLUDE_ABORT:-1}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/kv_lifecycle_probe/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON KV_LIFECYCLE_VARIANT KV_LIFECYCLE_CASE_NAME
export KV_LIFECYCLE_CACHE_MODE KV_LIFECYCLE_SESSION_COUNT KV_LIFECYCLE_LINE_COUNT
export KV_LIFECYCLE_MAX_TOKENS KV_LIFECYCLE_TEMPERATURE KV_LIFECYCLE_TOP_P
export KV_LIFECYCLE_THINKING_MODE KV_LIFECYCLE_TIMEOUT KV_LIFECYCLE_METRICS_TIMEOUT
export KV_LIFECYCLE_SETTLE_TIMEOUT KV_LIFECYCLE_SETTLE_INTERVAL
export KV_LIFECYCLE_MAX_IDLE_KV_PERCENT KV_LIFECYCLE_INCLUDE_ABORT
export SERVE_LOG SERVER_GUARD SERVER_STARTUP_TIMEOUT SERVER_STARTUP_INTERVAL_SECONDS
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

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before KV lifecycle probe"; then
  printf '%s\n' "124" > "${OUT_DIR}/kv_lifecycle_probe.exit_code"
  mark_server_unresponsive "kv_lifecycle_probe" "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

optional_args=()
if [[ -n "${KV_LIFECYCLE_MAX_IDLE_KV_PERCENT}" ]]; then
  optional_args+=(--max-idle-kv-usage-percent "${KV_LIFECYCLE_MAX_IDLE_KV_PERCENT}")
fi
if [[ "${KV_LIFECYCLE_INCLUDE_ABORT}" == "1" || "${KV_LIFECYCLE_INCLUDE_ABORT}" == "true" ]]; then
  optional_args+=(--include-abort)
fi

set +e
"${PYTHON}" -m ds4_harness.cli kv-lifecycle-probe \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --variant "${KV_LIFECYCLE_VARIANT}" \
  --case-name "${KV_LIFECYCLE_CASE_NAME}" \
  --cache-mode "${KV_LIFECYCLE_CACHE_MODE}" \
  --session-count "${KV_LIFECYCLE_SESSION_COUNT}" \
  --line-count "${KV_LIFECYCLE_LINE_COUNT}" \
  --max-tokens "${KV_LIFECYCLE_MAX_TOKENS}" \
  --temperature "${KV_LIFECYCLE_TEMPERATURE}" \
  --top-p "${KV_LIFECYCLE_TOP_P}" \
  --thinking-mode "${KV_LIFECYCLE_THINKING_MODE}" \
  --timeout "${KV_LIFECYCLE_TIMEOUT}" \
  --metrics-timeout "${KV_LIFECYCLE_METRICS_TIMEOUT}" \
  --settle-timeout "${KV_LIFECYCLE_SETTLE_TIMEOUT}" \
  --settle-interval "${KV_LIFECYCLE_SETTLE_INTERVAL}" \
  ${optional_args[@]+"${optional_args[@]}"} \
  --json-output "${OUT_DIR}/kv_lifecycle_probe.json" \
  --markdown-output "${OUT_DIR}/kv_lifecycle_probe.md"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/kv_lifecycle_probe.exit_code"
if [[ "${code}" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after KV lifecycle probe"; then
  mark_server_unresponsive "kv_lifecycle_probe" "server unresponsive after KV lifecycle probe"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
