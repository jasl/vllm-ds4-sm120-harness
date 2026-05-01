#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PYTHON:-python3}"

REFERENCE_RUN_DIR="${REFERENCE_RUN_DIR:?set REFERENCE_RUN_DIR}"
REFERENCE_LABEL="${REFERENCE_LABEL:-$(basename "$(dirname "${REFERENCE_RUN_DIR}")")}"
REFERENCE_OUTPUT_DIR="${REFERENCE_OUTPUT_DIR:-${REPO_ROOT}/reference/baselines/${REFERENCE_LABEL}}"
REFERENCE_DATE="${REFERENCE_DATE:-}"
REFERENCE_SUPPLEMENT_DIR="${REFERENCE_SUPPLEMENT_DIR:-}"

ARGS=(
  -m ds4_harness.cli reference-bundle
  --run-dir "${REFERENCE_RUN_DIR}"
  --output-dir "${REFERENCE_OUTPUT_DIR}"
  --label "${REFERENCE_LABEL}"
  --fail-on-sensitive
)

if [[ -n "${REFERENCE_DATE}" ]]; then
  ARGS+=(--date "${REFERENCE_DATE}")
fi

if [[ -n "${REFERENCE_SUPPLEMENT_DIR}" ]]; then
  ARGS+=(--supplement-dir "${REFERENCE_SUPPLEMENT_DIR}")
fi

cd "${REPO_ROOT}"
"${PYTHON}" "${ARGS[@]}"
