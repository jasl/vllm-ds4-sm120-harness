#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PYTHON:-python3}"

source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASELINE_RUN_DIR="${BASELINE_RUN_DIR:-}"
BASELINE_REPORT_OUTPUT="${BASELINE_REPORT_OUTPUT:-}"
BASELINE_REPORT_TITLE="${BASELINE_REPORT_TITLE:-DeepSeek V4 Baseline Report}"
BASELINE_REPORT_LABEL="${BASELINE_REPORT_LABEL:-}"
BASELINE_REPORT_DATE="${BASELINE_REPORT_DATE:-}"

if [[ -z "${BASELINE_RUN_DIR}" ]]; then
  printf '%s\n' "BASELINE_RUN_DIR is required" >&2
  exit 2
fi

if [[ -z "${BASELINE_REPORT_DATE}" ]]; then
  run_basename="$(basename "${BASELINE_RUN_DIR}")"
  if [[ "${run_basename}" =~ ^([0-9]{8}) ]]; then
    BASELINE_REPORT_DATE="${BASH_REMATCH[1]}"
  else
    BASELINE_REPORT_DATE="$(date -u +%Y%m%d)"
  fi
fi

if [[ -z "${BASELINE_REPORT_OUTPUT}" ]]; then
  output_label="${BASELINE_REPORT_LABEL:-baseline}"
  output_label="$(slugify_context_value "${output_label}")"
  BASELINE_REPORT_OUTPUT="baselines/${BASELINE_REPORT_DATE}_${output_label}/report.md"
fi

args=(
  baseline-report
  --run-dir "${BASELINE_RUN_DIR}"
  --title "${BASELINE_REPORT_TITLE}"
  --output "${BASELINE_REPORT_OUTPUT}"
)

if [[ -n "${BASELINE_REPORT_LABEL}" ]]; then
  args+=(--label "${BASELINE_REPORT_LABEL}")
fi

cd "${REPO_ROOT}"
"${PYTHON}" -m ds4_harness.cli "${args[@]}"
