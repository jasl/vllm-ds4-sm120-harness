#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
ORACLE_DIR="${ORACLE_DIR:-}"
RUN_TOOLCALL15="${RUN_TOOLCALL15:-1}"
PYTHON="${PYTHON:-python}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${RUN_TIMESTAMP}}"

mkdir -p "${OUT_DIR}"
source "${SCRIPT_DIR}/gpu_stats.sh"
start_gpu_stats
trap stop_gpu_stats EXIT

"${PYTHON}" -m pytest -q tests
"${PYTHON}" -m ruff check ds4_harness tests
"${PYTHON}" -m compileall -q ds4_harness

"${PYTHON}" -m ds4_harness.cli health \
  --base-url "${BASE_URL}" \
  > "${OUT_DIR}/health.jsonl"

"${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag quick \
  --jsonl-output "${OUT_DIR}/smoke_quick.jsonl" \
  --markdown-output "${OUT_DIR}/smoke_quick.md"

"${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag quality \
  --jsonl-output "${OUT_DIR}/smoke_quality.jsonl" \
  --markdown-output "${OUT_DIR}/smoke_quality.md"

"${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag coding \
  --timeout "${CODING_TIMEOUT:-900}" \
  --jsonl-output "${OUT_DIR}/smoke_coding.jsonl" \
  --markdown-output "${OUT_DIR}/smoke_coding.md"

if [[ "${RUN_TOOLCALL15}" == "1" ]]; then
  "${PYTHON}" -m ds4_harness.cli toolcall15 \
    --base-url "${BASE_URL}" \
    --model "${MODEL}" \
    --min-points "${TOOLCALL15_MIN_POINTS:-2}" \
    --json-output "${OUT_DIR}/toolcall15.json"
fi

if [[ -n "${ORACLE_DIR}" ]]; then
  "${PYTHON}" -m ds4_harness.cli oracle-compare \
    --base-url "${BASE_URL}" \
    --oracle-dir "${ORACLE_DIR}" \
    --require-prompt-ids \
    --min-top1-match-rate "${MIN_TOP1_MATCH_RATE:-0.80}" \
    --json-output "${OUT_DIR}/oracle_compare.json"
fi

echo "wrote ${OUT_DIR}"
