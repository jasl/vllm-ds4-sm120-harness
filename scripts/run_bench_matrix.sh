#!/usr/bin/env bash
set -euo pipefail

VLLM_BIN="${VLLM_BIN:-vllm}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
HOST="${HOST:-localhost}"
PORT="${PORT:-8000}"
CONCURRENCY="${CONCURRENCY:-1,2,4,8,16,24}"
DATASET_NAME="${DATASET_NAME:-hf}"
DATASET_PATH="${DATASET_PATH:-philschmid/mt-bench}"
NUM_PROMPTS="${NUM_PROMPTS:-80}"
RANDOM_INPUT_LEN="${RANDOM_INPUT_LEN:-1024}"
RANDOM_OUTPUT_LEN="${RANDOM_OUTPUT_LEN:-1024}"
TEMPERATURE="${TEMPERATURE:-1.0}"
IGNORE_EOS="${IGNORE_EOS:-0}"
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

EXTRA_ARGS=()
if [[ "${IGNORE_EOS}" == "1" || "${IGNORE_EOS}" == "true" ]]; then
  EXTRA_ARGS+=(--ignore-eos)
fi

"${PYTHON}" -m ds4_harness.cli bench-matrix \
  --vllm-bin "${VLLM_BIN}" \
  --model "${MODEL}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --concurrency "${CONCURRENCY}" \
  --dataset-name "${DATASET_NAME}" \
  --dataset-path "${DATASET_PATH}" \
  --random-input-len "${RANDOM_INPUT_LEN}" \
  --random-output-len "${RANDOM_OUTPUT_LEN}" \
  --num-prompts "${NUM_PROMPTS}" \
  --temperature "${TEMPERATURE}" \
  "${EXTRA_ARGS[@]}" \
  --json-output "${OUT_DIR}/bench.json" \
  --log-dir "${OUT_DIR}/logs"

echo "wrote ${OUT_DIR}"
