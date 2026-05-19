#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
LONG_CONTEXT_LATENCY_VARIANT="${LONG_CONTEXT_LATENCY_VARIANT:-manual}"
LONG_CONTEXT_LATENCY_CASE_NAME="${LONG_CONTEXT_LATENCY_CASE_NAME:-long_context_interactive_latency}"
LONG_CONTEXT_LATENCY_LINE_COUNTS="${LONG_CONTEXT_LATENCY_LINE_COUNTS-1900}"
LONG_CONTEXT_LATENCY_PROMPT_FILES="${LONG_CONTEXT_LATENCY_PROMPT_FILES:-}"
LONG_CONTEXT_LATENCY_CONCURRENCY="${LONG_CONTEXT_LATENCY_CONCURRENCY:-1,2,3,4}"
LONG_CONTEXT_LATENCY_CACHE_MODES="${LONG_CONTEXT_LATENCY_CACHE_MODES:-cold,warm}"
LONG_CONTEXT_LATENCY_REPEAT_COUNT="${LONG_CONTEXT_LATENCY_REPEAT_COUNT:-1}"
LONG_CONTEXT_LATENCY_MAX_TOKENS="${LONG_CONTEXT_LATENCY_MAX_TOKENS:-64}"
LONG_CONTEXT_LATENCY_TEMPERATURE="${LONG_CONTEXT_LATENCY_TEMPERATURE:-0.0}"
LONG_CONTEXT_LATENCY_TOP_P="${LONG_CONTEXT_LATENCY_TOP_P:-1.0}"
LONG_CONTEXT_LATENCY_THINKING_MODE="${LONG_CONTEXT_LATENCY_THINKING_MODE:-non-thinking}"
LONG_CONTEXT_LATENCY_TIMEOUT="${LONG_CONTEXT_LATENCY_TIMEOUT:-1800}"
LONG_CONTEXT_LATENCY_PREWARM="${LONG_CONTEXT_LATENCY_PREWARM:-0}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/long_context_latency_matrix/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON LONG_CONTEXT_LATENCY_VARIANT
export LONG_CONTEXT_LATENCY_CASE_NAME LONG_CONTEXT_LATENCY_LINE_COUNTS
export LONG_CONTEXT_LATENCY_PROMPT_FILES LONG_CONTEXT_LATENCY_CONCURRENCY
export LONG_CONTEXT_LATENCY_CACHE_MODES LONG_CONTEXT_LATENCY_REPEAT_COUNT
export LONG_CONTEXT_LATENCY_MAX_TOKENS LONG_CONTEXT_LATENCY_TEMPERATURE
export LONG_CONTEXT_LATENCY_TOP_P LONG_CONTEXT_LATENCY_THINKING_MODE
export LONG_CONTEXT_LATENCY_TIMEOUT LONG_CONTEXT_LATENCY_PREWARM
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

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before long-context latency matrix"; then
  printf '%s\n' "124" > "${OUT_DIR}/long_context_latency_matrix.exit_code"
  mark_server_unresponsive "long_context_latency_matrix" "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

run_long_context_latency_prewarm() {
  case "${LONG_CONTEXT_LATENCY_PREWARM}" in
    0)
      return 0
      ;;
    1)
      ;;
    *)
      printf 'invalid LONG_CONTEXT_LATENCY_PREWARM=%s; expected 0 or 1\n' \
        "${LONG_CONTEXT_LATENCY_PREWARM}" >&2
      return 2
      ;;
  esac

  set +e
  PREWARM_BASE_URL="${BASE_URL}" \
    MODEL_ID="${MODEL}" \
    VLLM_VENV="${VLLM_VENV:-}" \
    PREWARM_LOG="${OUT_DIR}/prewarm.log" \
    "${SCRIPT_DIR}/prewarm_serve.sh"
  prewarm_code="$?"
  set -e
  printf '%s\n' "${prewarm_code}" > "${OUT_DIR}/prewarm.exit_code"
  return "${prewarm_code}"
}

if ! run_long_context_latency_prewarm; then
  mark_server_unresponsive "long_context_latency_prewarm" "prewarm failed"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

prompt_file_args=()
if [[ -n "${LONG_CONTEXT_LATENCY_PROMPT_FILES}" ]]; then
  IFS=',' read -r -a prompt_files <<< "${LONG_CONTEXT_LATENCY_PROMPT_FILES}"
  for prompt_file in "${prompt_files[@]}"; do
    [[ -n "${prompt_file}" ]] || continue
    prompt_file_args+=(--prompt-file "${prompt_file}")
  done
fi

set +e
"${PYTHON}" -m ds4_harness.cli long-context-latency-matrix \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --variant "${LONG_CONTEXT_LATENCY_VARIANT}" \
  --case-name "${LONG_CONTEXT_LATENCY_CASE_NAME}" \
  --line-counts "${LONG_CONTEXT_LATENCY_LINE_COUNTS}" \
  ${prompt_file_args[@]+"${prompt_file_args[@]}"} \
  --concurrency "${LONG_CONTEXT_LATENCY_CONCURRENCY}" \
  --cache-modes "${LONG_CONTEXT_LATENCY_CACHE_MODES}" \
  --repeat-count "${LONG_CONTEXT_LATENCY_REPEAT_COUNT}" \
  --max-tokens "${LONG_CONTEXT_LATENCY_MAX_TOKENS}" \
  --temperature "${LONG_CONTEXT_LATENCY_TEMPERATURE}" \
  --top-p "${LONG_CONTEXT_LATENCY_TOP_P}" \
  --thinking-mode "${LONG_CONTEXT_LATENCY_THINKING_MODE}" \
  --timeout "${LONG_CONTEXT_LATENCY_TIMEOUT}" \
  --json-output "${OUT_DIR}/long_context_latency_matrix.json" \
  --markdown-output "${OUT_DIR}/long_context_latency_matrix.md"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/long_context_latency_matrix.exit_code"
if [[ "${code}" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after long-context latency matrix"; then
  mark_server_unresponsive "long_context_latency_matrix" "server unresponsive after long-context latency matrix"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
