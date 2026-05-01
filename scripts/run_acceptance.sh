#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
OUT_DIR="${OUT_DIR:-/tmp/ds4-sm120-harness-$(date +%Y%m%d-%H%M%S)}"
ORACLE_DIR="${ORACLE_DIR:-}"
RUN_TOOLCALL15="${RUN_TOOLCALL15:-1}"
PYTHON="${PYTHON:-python}"

mkdir -p "${OUT_DIR}"

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
  --jsonl-output "${OUT_DIR}/smoke_quick.jsonl"

"${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag quality \
  --jsonl-output "${OUT_DIR}/smoke_quality.jsonl"

"${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag coding \
  --timeout "${CODING_TIMEOUT:-900}" \
  --jsonl-output "${OUT_DIR}/smoke_coding.jsonl"

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
