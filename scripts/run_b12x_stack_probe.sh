#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date -u +%Y%m%d%H%M%S)}"
BRANCH_SLUG="${BRANCH_SLUG:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/ ' '__')}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-unknown_topology}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/b12x_stack_probe/${RUN_TIMESTAMP}}"
PYTHON="${PYTHON:-python3}"

mkdir -p "${OUT_DIR}"

"${PYTHON}" -m ds4_harness.b12x_stack_probe \
  --json-output "${OUT_DIR}/b12x_stack_probe.json" \
  --markdown-output "${OUT_DIR}/b12x_stack_probe.md"
code=$?
printf '%s\n' "${code}" > "${OUT_DIR}/b12x_stack_probe.exit_code"
exit "${code}"
