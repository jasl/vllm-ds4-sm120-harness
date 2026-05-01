#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
ORACLE_DIR="${ORACLE_DIR:-}"
ORACLE_TOP_N="${ORACLE_TOP_N:-20}"
RUN_TOOLCALL15="${RUN_TOOLCALL15:-1}"
PYTHON="${PYTHON:-python}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${RUN_TIMESTAMP}}"
REAL_SCENARIO_REPEAT_COUNT="${REAL_SCENARIO_REPEAT_COUNT:-3}"
QUALITY_TAG="${QUALITY_TAG:-quality}"
CODING_TAG="${CODING_TAG:-coding}"
QUALITY_REPEAT_COUNT="${QUALITY_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT}}"
CODING_REPEAT_COUNT="${CODING_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT}}"
TOOLCALL15_SCENARIO_SET="${TOOLCALL15_SCENARIO_SET:-both}"
TOOLCALL15_REPEAT_COUNT="${TOOLCALL15_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT}}"
export BASE_URL MODEL ORACLE_DIR ORACLE_TOP_N RUN_TOOLCALL15 PYTHON
export SERVER_GUARD SERVER_STARTUP_TIMEOUT SERVER_STARTUP_INTERVAL_SECONDS
export SERVER_HEALTH_TIMEOUT SERVER_FAILURE_GRACE_TIMEOUT SERVER_FAILURE_GRACE_INTERVAL_SECONDS
export SERVER_RECOVERY_CMD
export ARTIFACT_ROOT RUN_TIMESTAMP BRANCH_NAME GPU_TOPOLOGY_SLUG OUT_DIR
export REAL_SCENARIO_REPEAT_COUNT QUALITY_REPEAT_COUNT CODING_REPEAT_COUNT
export QUALITY_TAG CODING_TAG TOOLCALL15_SCENARIO_SET TOOLCALL15_REPEAT_COUNT

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/vllm_collect_env.sh"
collect_vllm_env
source "${SCRIPT_DIR}/gpu_stats.sh"
source "${SCRIPT_DIR}/runtime_stats.sh"
start_gpu_stats
start_runtime_stats
trap 'stop_runtime_stats; stop_gpu_stats' EXIT

failures=0
server_failed=0

run_gate() {
  name="$1"
  shift
  set +e
  "$@"
  code="$?"
  set -e
  printf '%s\n' "${code}" > "${OUT_DIR}/${name}.exit_code"
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi
}

run_gate_capture() {
  name="$1"
  output="$2"
  shift 2
  set +e
  "$@" > "${output}"
  code="$?"
  set -e
  printf '%s\n' "${code}" > "${OUT_DIR}/${name}.exit_code"
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi
}

mark_gate_skipped() {
  name="$1"
  detail="$2"
  printf '%s\n' "124" > "${OUT_DIR}/${name}.exit_code"
  printf '%s\n' "${detail}" > "${OUT_DIR}/${name}.skipped"
  failures=1
}

run_live_gate() {
  name="$1"
  shift
  if [[ "${server_failed}" == "1" ]]; then
    mark_gate_skipped "${name}" "server already marked unresponsive; skipped"
    return
  fi
  if ! server_ready; then
    server_failed=1
    mark_gate_skipped "${name}" "server unresponsive before ${name}; skipped"
    mark_server_unresponsive "${name}" "server unresponsive before ${name}"
    return
  fi
  run_gate "${name}" "$@"
  if [[ "$(cat "${OUT_DIR}/${name}.exit_code")" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after ${name}"; then
    server_failed=1
    mark_server_unresponsive "${name}" "server unresponsive after ${name}"
  fi
}

run_live_gate_capture() {
  name="$1"
  output="$2"
  shift 2
  if [[ "${server_failed}" == "1" ]]; then
    mark_gate_skipped "${name}" "server already marked unresponsive; skipped"
    return
  fi
  run_gate_capture "${name}" "${output}" "$@"
  if [[ "$(cat "${OUT_DIR}/${name}.exit_code")" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after ${name}"; then
    server_failed=1
    mark_server_unresponsive "${name}" "server unresponsive after ${name}"
  fi
}

run_gate pytest "${PYTHON}" -m pytest -q tests
run_gate ruff "${PYTHON}" -m ruff check ds4_harness tests
run_gate compileall "${PYTHON}" -m compileall -q ds4_harness

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before acceptance"; then
  server_failed=1
  mark_server_unresponsive "startup" "server not ready after startup wait"
fi

run_live_gate_capture health "${OUT_DIR}/health.jsonl" \
  "${PYTHON}" -m ds4_harness.cli health \
  --base-url "${BASE_URL}"

run_live_gate smoke_quick "${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag quick \
  --jsonl-output "${OUT_DIR}/smoke_quick.jsonl" \
  --markdown-output "${OUT_DIR}/smoke_quick.md"

run_live_gate smoke_quality "${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag "${QUALITY_TAG}" \
  --repeat-count "${QUALITY_REPEAT_COUNT}" \
  --jsonl-output "${OUT_DIR}/smoke_quality.jsonl" \
  --markdown-output "${OUT_DIR}/smoke_quality.md"

run_live_gate smoke_coding "${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag "${CODING_TAG}" \
  --repeat-count "${CODING_REPEAT_COUNT}" \
  --timeout "${CODING_TIMEOUT:-900}" \
  --jsonl-output "${OUT_DIR}/smoke_coding.jsonl" \
  --markdown-output "${OUT_DIR}/smoke_coding.md"

if [[ "${RUN_TOOLCALL15}" == "1" ]]; then
  run_live_gate toolcall15 "${PYTHON}" -m ds4_harness.cli toolcall15 \
    --base-url "${BASE_URL}" \
    --model "${MODEL}" \
    --min-points "${TOOLCALL15_MIN_POINTS:-2}" \
    --scenario-set "${TOOLCALL15_SCENARIO_SET}" \
    --repeat-count "${TOOLCALL15_REPEAT_COUNT}" \
    --json-output "${OUT_DIR}/toolcall15.json"
fi

if [[ -n "${ORACLE_DIR}" ]]; then
  run_live_gate oracle_compare "${PYTHON}" -m ds4_harness.cli oracle-compare \
    --base-url "${BASE_URL}" \
    --oracle-dir "${ORACLE_DIR}" \
    --top-n "${ORACLE_TOP_N}" \
    --require-prompt-ids \
    --min-top1-match-rate "${MIN_TOP1_MATCH_RATE:-0.80}" \
    --json-output "${OUT_DIR}/oracle_compare.json"
fi

echo "wrote ${OUT_DIR}"
exit ${failures}
