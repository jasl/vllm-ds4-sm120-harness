#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PYTHON:-python3}"

source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASELINE_RUN_DIR="${BASELINE_RUN_DIR:-}"
BASELINE_SUPPLEMENT_DIR="${BASELINE_SUPPLEMENT_DIR:-}"
BASELINE_REPORT_OUTPUT="${BASELINE_REPORT_OUTPUT:-reports/baselines/baseline.md}"
BASELINE_REPORT_TITLE="${BASELINE_REPORT_TITLE:-DeepSeek V4 Baseline Report}"
BASELINE_REPORT_LABEL="${BASELINE_REPORT_LABEL:-}"

if [[ -z "${BASELINE_RUN_DIR}" ]]; then
  printf '%s\n' "BASELINE_RUN_DIR is required" >&2
  exit 2
fi

args=(
  baseline-report
  --run-dir "${BASELINE_RUN_DIR}"
  --title "${BASELINE_REPORT_TITLE}"
  --output "${BASELINE_REPORT_OUTPUT}"
)

if [[ -n "${BASELINE_SUPPLEMENT_DIR}" ]]; then
  args+=(--supplement-dir "${BASELINE_SUPPLEMENT_DIR}")
fi

if [[ -n "${BASELINE_REPORT_LABEL}" ]]; then
  args+=(--label "${BASELINE_REPORT_LABEL}")
fi

cd "${REPO_ROOT}"
"${PYTHON}" -m ds4_harness.cli "${args[@]}"
