#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
LONG_CONTEXT_VARIANT="${LONG_CONTEXT_VARIANT:-manual}"
LONG_CONTEXT_CASE_NAME="${LONG_CONTEXT_CASE_NAME:-kv_indexer_long_context}"
LONG_CONTEXT_LINE_COUNT="${LONG_CONTEXT_LINE_COUNT:-2400}"
LONG_CONTEXT_MAX_TOKENS="${LONG_CONTEXT_MAX_TOKENS:-128}"
LONG_CONTEXT_TEMPERATURE="${LONG_CONTEXT_TEMPERATURE:-0.0}"
LONG_CONTEXT_TOP_P="${LONG_CONTEXT_TOP_P:-1.0}"
LONG_CONTEXT_THINKING_MODE="${LONG_CONTEXT_THINKING_MODE:-non-thinking}"
LONG_CONTEXT_TIMEOUT="${LONG_CONTEXT_TIMEOUT:-1800}"
LONG_CONTEXT_REQUEST_RETRIES="${LONG_CONTEXT_REQUEST_RETRIES:-${API_REQUEST_RETRIES:-1}}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/long_context_probe/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON LONG_CONTEXT_VARIANT LONG_CONTEXT_CASE_NAME
export LONG_CONTEXT_LINE_COUNT LONG_CONTEXT_MAX_TOKENS LONG_CONTEXT_TEMPERATURE
export LONG_CONTEXT_TOP_P LONG_CONTEXT_THINKING_MODE LONG_CONTEXT_TIMEOUT
export LONG_CONTEXT_REQUEST_RETRIES SERVER_GUARD SERVER_STARTUP_TIMEOUT
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

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before long-context probe"; then
  printf '%s\n' "124" > "${OUT_DIR}/long_context_probe.exit_code"
  mark_server_unresponsive "long_context_probe" "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

set +e
"${PYTHON}" -m ds4_harness.cli long-context-probe \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --variant "${LONG_CONTEXT_VARIANT}" \
  --case-name "${LONG_CONTEXT_CASE_NAME}" \
  --line-count "${LONG_CONTEXT_LINE_COUNT}" \
  --max-tokens "${LONG_CONTEXT_MAX_TOKENS}" \
  --temperature "${LONG_CONTEXT_TEMPERATURE}" \
  --top-p "${LONG_CONTEXT_TOP_P}" \
  --thinking-mode "${LONG_CONTEXT_THINKING_MODE}" \
  --timeout "${LONG_CONTEXT_TIMEOUT}" \
  --request-retries "${LONG_CONTEXT_REQUEST_RETRIES}" \
  --json-output "${OUT_DIR}/long_context_probe.json" \
  --markdown-output "${OUT_DIR}/long_context_probe.md"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/long_context_probe.exit_code"
if [[ "${code}" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after long-context probe"; then
  mark_server_unresponsive "long_context_probe" "server unresponsive after long-context probe"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
