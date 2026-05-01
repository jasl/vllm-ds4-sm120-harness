#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PYTHON:-python3}"

source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASELINE_RUN_DIR="${BASELINE_RUN_DIR:?set BASELINE_RUN_DIR}"
BASELINE_SUPPLEMENT_DIR="${BASELINE_SUPPLEMENT_DIR:-}"
BASELINE_REPORT_TITLE="${BASELINE_REPORT_TITLE:-DeepSeek V4 Baseline Report}"
BASELINE_REPORT_LABEL="${BASELINE_REPORT_LABEL:-}"
BASELINE_DATE="${BASELINE_DATE:-}"

if [[ -z "${BASELINE_DATE}" ]]; then
  run_basename="$(basename "${BASELINE_RUN_DIR}")"
  if [[ "${run_basename}" =~ ^([0-9]{8}) ]]; then
    BASELINE_DATE="${BASH_REMATCH[1]}"
  else
    BASELINE_DATE="$(date -u +%Y%m%d)"
  fi
fi

if [[ -z "${BASELINE_REPORT_LABEL}" ]]; then
  BASELINE_REPORT_LABEL="$(basename "$(dirname "${BASELINE_RUN_DIR}")")"
fi

BASELINE_BUNDLE_LABEL="${BASELINE_BUNDLE_LABEL:-$(slugify_context_value "${BASELINE_REPORT_LABEL}")}"
BASELINE_OUTPUT_DIR="${BASELINE_OUTPUT_DIR:-${REPO_ROOT}/baselines/${BASELINE_DATE}_${BASELINE_BUNDLE_LABEL}}"
BASELINE_BUNDLE_NAME="$(basename "${BASELINE_OUTPUT_DIR}")"

output_parent="$(dirname "${BASELINE_OUTPUT_DIR}")"
output_name="$(basename "${BASELINE_OUTPUT_DIR}")"
mkdir -p "${output_parent}"
tmp_dir="$(mktemp -d "${output_parent}/.${output_name}.tmp.XXXXXX")"
cleanup() {
  rm -rf "${tmp_dir}"
}
trap cleanup EXIT

reference_args=(
  reference-bundle
  --run-dir "${BASELINE_RUN_DIR}"
  --output-dir "${tmp_dir}"
  --label "${BASELINE_BUNDLE_NAME}"
  --date "${BASELINE_DATE}"
  --fail-on-sensitive
)

report_args=(
  baseline-report
  --run-dir "${BASELINE_RUN_DIR}"
  --title "${BASELINE_REPORT_TITLE}"
  --label "${BASELINE_REPORT_LABEL}"
  --output "${tmp_dir}/report.md"
)

if [[ -n "${BASELINE_SUPPLEMENT_DIR}" ]]; then
  reference_args+=(--supplement-dir "${BASELINE_SUPPLEMENT_DIR}")
  report_args+=(--supplement-dir "${BASELINE_SUPPLEMENT_DIR}")
fi

cd "${REPO_ROOT}"
"${PYTHON}" -m ds4_harness.cli "${reference_args[@]}" >/dev/null
"${PYTHON}" -m ds4_harness.cli "${report_args[@]}" >/dev/null

"${PYTHON}" - "${tmp_dir}" <<'PY'
from pathlib import Path
import sys

from ds4_harness.oracle import load_oracle_cases
from ds4_harness.reference_bundle import scan_public_bundle

root = Path(sys.argv[1])
findings = scan_public_bundle(root)
if findings:
    raise SystemExit("baseline bundle contains non-public data:\n" + "\n".join(findings))

cases = load_oracle_cases(root / "oracle")
if not cases:
    raise SystemExit("baseline bundle has no oracle cases")

report = root / "report.md"
if not report.exists() or report.stat().st_size == 0:
    raise SystemExit("baseline bundle report.md was not generated")
PY

rm -rf "${BASELINE_OUTPUT_DIR}"
mv "${tmp_dir}" "${BASELINE_OUTPUT_DIR}"
trap - EXIT
printf '%s\n' "${BASELINE_OUTPUT_DIR}"
