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
OUT_DIR="${OUT_DIR:-/tmp/ds4-sm120-bench-$(date +%Y%m%d-%H%M%S)}"
PYTHON="${PYTHON:-python}"

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
