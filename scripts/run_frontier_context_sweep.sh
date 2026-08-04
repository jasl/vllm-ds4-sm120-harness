#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}"
PYTHON="${PYTHON:-python}"
FRONTIER_CONTEXT_SWEEP_VARIANT="${FRONTIER_CONTEXT_SWEEP_VARIANT:-manual}"
FRONTIER_CONTEXT_SWEEP_CASE_NAME="${FRONTIER_CONTEXT_SWEEP_CASE_NAME:-ds4_frontier_context_sweep}"
FRONTIER_CONTEXT_SWEEP_PROMPT_FILES="${FRONTIER_CONTEXT_SWEEP_PROMPT_FILES:-${REPO_ROOT}/prompts/long_context/ds4_story_recall.txt,${REPO_ROOT}/prompts/long_context/ds4_security_audit.txt}"
FRONTIER_CONTEXT_SWEEP_FRONTIERS="${FRONTIER_CONTEXT_SWEEP_FRONTIERS:-8192,16384,32768,65536,98304,124000}"
FRONTIER_CONTEXT_SWEEP_REPEAT_COUNT="${FRONTIER_CONTEXT_SWEEP_REPEAT_COUNT:-1}"
FRONTIER_CONTEXT_SWEEP_MAX_TOKENS="${FRONTIER_CONTEXT_SWEEP_MAX_TOKENS:-128}"
FRONTIER_CONTEXT_SWEEP_TEMPERATURE="${FRONTIER_CONTEXT_SWEEP_TEMPERATURE:-0.0}"
FRONTIER_CONTEXT_SWEEP_TOP_P="${FRONTIER_CONTEXT_SWEEP_TOP_P:-1.0}"
FRONTIER_CONTEXT_SWEEP_THINKING_MODE="${FRONTIER_CONTEXT_SWEEP_THINKING_MODE:-non-thinking}"
FRONTIER_CONTEXT_SWEEP_TIMEOUT="${FRONTIER_CONTEXT_SWEEP_TIMEOUT:-1800}"
FRONTIER_CONTEXT_SWEEP_PREWARM="${FRONTIER_CONTEXT_SWEEP_PREWARM:-1}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/frontier_context_sweep/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON FRONTIER_CONTEXT_SWEEP_VARIANT
export FRONTIER_CONTEXT_SWEEP_CASE_NAME FRONTIER_CONTEXT_SWEEP_PROMPT_FILES
export FRONTIER_CONTEXT_SWEEP_FRONTIERS FRONTIER_CONTEXT_SWEEP_REPEAT_COUNT
export FRONTIER_CONTEXT_SWEEP_MAX_TOKENS FRONTIER_CONTEXT_SWEEP_TEMPERATURE
export FRONTIER_CONTEXT_SWEEP_TOP_P FRONTIER_CONTEXT_SWEEP_THINKING_MODE
export FRONTIER_CONTEXT_SWEEP_TIMEOUT FRONTIER_CONTEXT_SWEEP_PREWARM
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

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before frontier context sweep"; then
  printf '%s\n' "124" > "${OUT_DIR}/frontier_context_sweep.exit_code"
  mark_server_unresponsive "frontier_context_sweep" "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

run_frontier_context_sweep_prewarm() {
  case "${FRONTIER_CONTEXT_SWEEP_PREWARM}" in
    0)
      return 0
      ;;
    1)
      ;;
    *)
      printf 'invalid FRONTIER_CONTEXT_SWEEP_PREWARM=%s; expected 0 or 1\n' \
        "${FRONTIER_CONTEXT_SWEEP_PREWARM}" >&2
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

if ! run_frontier_context_sweep_prewarm; then
  mark_server_unresponsive "frontier_context_sweep_prewarm" "prewarm failed"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

prompt_file_args=()
IFS=',' read -r -a prompt_files <<< "${FRONTIER_CONTEXT_SWEEP_PROMPT_FILES}"
for prompt_file in "${prompt_files[@]}"; do
  [[ -n "${prompt_file}" ]] || continue
  prompt_file_args+=(--prompt-file "${prompt_file}")
done

set +e
"${PYTHON}" -m ds4_harness.cli frontier-context-sweep \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --variant "${FRONTIER_CONTEXT_SWEEP_VARIANT}" \
  --case-name "${FRONTIER_CONTEXT_SWEEP_CASE_NAME}" \
  ${prompt_file_args[@]+"${prompt_file_args[@]}"} \
  --frontiers "${FRONTIER_CONTEXT_SWEEP_FRONTIERS}" \
  --repeat-count "${FRONTIER_CONTEXT_SWEEP_REPEAT_COUNT}" \
  --max-tokens "${FRONTIER_CONTEXT_SWEEP_MAX_TOKENS}" \
  --temperature "${FRONTIER_CONTEXT_SWEEP_TEMPERATURE}" \
  --top-p "${FRONTIER_CONTEXT_SWEEP_TOP_P}" \
  --thinking-mode "${FRONTIER_CONTEXT_SWEEP_THINKING_MODE}" \
  --timeout "${FRONTIER_CONTEXT_SWEEP_TIMEOUT}" \
  --json-output "${OUT_DIR}/frontier_context_sweep.json" \
  --markdown-output "${OUT_DIR}/frontier_context_sweep.md"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/frontier_context_sweep.exit_code"
if [[ "${code}" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after frontier context sweep"; then
  mark_server_unresponsive "frontier_context_sweep" "server unresponsive after frontier context sweep"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
