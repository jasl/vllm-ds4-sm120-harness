#!/usr/bin/env bash
set -euo pipefail

VLLM_BIN="${VLLM_BIN:-vllm}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
HOST="${HOST:-localhost}"
PORT="${PORT:-8000}"
CONCURRENCY="${CONCURRENCY:-1,4,8}"
NUM_PROMPTS="${NUM_PROMPTS:-48}"
RANDOM_INPUT_LEN="${RANDOM_INPUT_LEN:-1024}"
RANDOM_OUTPUT_LEN="${RANDOM_OUTPUT_LEN:-1024}"
OUT_DIR="${OUT_DIR:-/tmp/ds4-sm120-bench-$(date +%Y%m%d-%H%M%S)}"
PYTHON="${PYTHON:-python}"

mkdir -p "${OUT_DIR}"

"${PYTHON}" -m ds4_harness.cli bench-matrix \
  --vllm-bin "${VLLM_BIN}" \
  --model "${MODEL}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --concurrency "${CONCURRENCY}" \
  --random-input-len "${RANDOM_INPUT_LEN}" \
  --random-output-len "${RANDOM_OUTPUT_LEN}" \
  --num-prompts "${NUM_PROMPTS}" \
  --ignore-eos \
  --json-output "${OUT_DIR}/bench.json" \
  --log-dir "${OUT_DIR}/logs"

echo "wrote ${OUT_DIR}"
