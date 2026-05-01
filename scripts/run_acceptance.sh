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
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${RUN_TIMESTAMP}}"
export BASE_URL MODEL ORACLE_DIR ORACLE_TOP_N RUN_TOOLCALL15 PYTHON
export ARTIFACT_ROOT RUN_TIMESTAMP BRANCH_NAME GPU_TOPOLOGY_SLUG OUT_DIR

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/gpu_stats.sh"
source "${SCRIPT_DIR}/runtime_stats.sh"
start_gpu_stats
start_runtime_stats
trap 'stop_runtime_stats; stop_gpu_stats' EXIT

failures=0

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

run_gate pytest "${PYTHON}" -m pytest -q tests
run_gate ruff "${PYTHON}" -m ruff check ds4_harness tests
run_gate compileall "${PYTHON}" -m compileall -q ds4_harness

run_gate_capture health "${OUT_DIR}/health.jsonl" \
  "${PYTHON}" -m ds4_harness.cli health \
  --base-url "${BASE_URL}"

run_gate smoke_quick "${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag quick \
  --jsonl-output "${OUT_DIR}/smoke_quick.jsonl" \
  --markdown-output "${OUT_DIR}/smoke_quick.md"

run_gate smoke_quality "${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag quality \
  --jsonl-output "${OUT_DIR}/smoke_quality.jsonl" \
  --markdown-output "${OUT_DIR}/smoke_quality.md"

run_gate smoke_coding "${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag coding \
  --timeout "${CODING_TIMEOUT:-900}" \
  --jsonl-output "${OUT_DIR}/smoke_coding.jsonl" \
  --markdown-output "${OUT_DIR}/smoke_coding.md"

if [[ "${RUN_TOOLCALL15}" == "1" ]]; then
  run_gate toolcall15 "${PYTHON}" -m ds4_harness.cli toolcall15 \
    --base-url "${BASE_URL}" \
    --model "${MODEL}" \
    --min-points "${TOOLCALL15_MIN_POINTS:-2}" \
    --json-output "${OUT_DIR}/toolcall15.json"
fi

if [[ -n "${ORACLE_DIR}" ]]; then
  run_gate oracle_compare "${PYTHON}" -m ds4_harness.cli oracle-compare \
    --base-url "${BASE_URL}" \
    --oracle-dir "${ORACLE_DIR}" \
    --top-n "${ORACLE_TOP_N}" \
    --require-prompt-ids \
    --min-top1-match-rate "${MIN_TOP1_MATCH_RATE:-0.80}" \
    --json-output "${OUT_DIR}/oracle_compare.json"
fi

echo "wrote ${OUT_DIR}"
exit ${failures}
