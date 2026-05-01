#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
ORACLE_LOGPROBS="${ORACLE_LOGPROBS:-20}"
ORACLE_TIMEOUT="${ORACLE_TIMEOUT:-300}"
BASELINE_LABEL="${BASELINE_LABEL:-b200_oracle}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${BASELINE_LABEL}/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON ORACLE_LOGPROBS ORACLE_TIMEOUT BASELINE_LABEL
export ARTIFACT_ROOT RUN_TIMESTAMP BRANCH_NAME GPU_TOPOLOGY_SLUG OUT_DIR

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/gpu_stats.sh"
source "${SCRIPT_DIR}/runtime_stats.sh"
start_gpu_stats
start_runtime_stats
trap 'stop_runtime_stats; stop_gpu_stats' EXIT

ARGS=()
if [[ -n "${ORACLE_CASES:-}" ]]; then
  IFS=',' read -r -a CASES <<< "${ORACLE_CASES}"
  for case_name in "${CASES[@]}"; do
    [[ -n "${case_name}" ]] && ARGS+=(--case "${case_name}")
  done
fi

"${PYTHON}" -m ds4_harness.cli oracle-export \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --output-dir "${OUT_DIR}" \
  --logprobs "${ORACLE_LOGPROBS}" \
  --timeout "${ORACLE_TIMEOUT}" \
  ${ARGS[@]+"${ARGS[@]}"}

echo "wrote ${OUT_DIR}"
