#!/usr/bin/env bash
# Send representative warm-up requests to a vLLM serve to populate the
# Triton kernel cache for shapes the in-process kernel_warmup hook does
# not cover. Run this once after the serve reports `/health=200`.
#
# Why this is necessary: vLLM's in-process warmup
# (`vllm/model_executor/warmup/kernel_warmup.py`) issues `_dummy_run`
# calls with synthesised tensors. Triton's specialization key includes
# tensor pointer 16-byte alignment, so kernels invoked from the real
# inference pipeline (sampler / spec-decode / indexer) hit a different
# cache key than the warmup helper and JIT-compile during the first
# user request. vLLM ships a `jit_monitor` that flags every uncovered
# kernel in `head.log` as a warning; on the SM12x DSv4-Flash MTP=2
# build we see nine kernels JIT during the first random-prefill cold
# bench (eagle_*, _build_prefill_chunk_metadata_kernel,
# _w8a8_triton_block_scaled_mm at alt shapes, _fp8_paged_mqa_logits_kernel
# at alt BLOCK_M, etc.), adding ~17 s to the first c=1 long-prefill
# request.
#
# This script issues two `vllm bench serve` rounds against the local
# API. Because `vllm bench serve` goes through the real OpenAI-style
# request path, it walks the full sampler / spec-decode / indexer
# pipeline and triggers exactly the Triton specializations the first
# real user would. The second user request after this script returns
# hits a fully warm kernel cache.
#
# Required env:
#   MODEL_ID          model identifier (e.g. deepseek-ai/DeepSeek-V4-Flash)
#   VLLM_VENV         path to the vLLM venv (must contain bin/vllm)
#
# Optional env:
#   API_HOST          API host (default 127.0.0.1)
#   API_PORT          API port (default 8000)
#   PREWARM_ISL       prefill length per request (default 8192;
#                     set to your scheduler's max_num_batched_tokens)
#   PREWARM_OSL       output tokens per request (default 8;
#                     keeps the prewarm short — only prefill matters)
#   PREWARM_PROMPTS   total prompts per round (default 4)
#   PREWARM_C_HIGH    high-concurrency batch size (default 4;
#                     should equal scheduler max_num_seqs to warm the
#                     largest in-flight decode the server will issue)
#   PREWARM_TIMEOUT   per-round timeout seconds (default 600)
#   PREWARM_TOKENIZER_MODE  tokenizer mode (default deepseek_v4)
#   PREWARM_LOG       optional file path to capture vllm bench output
set -euo pipefail

API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
MODEL_ID="${MODEL_ID:?set MODEL_ID}"
VLLM_VENV="${VLLM_VENV:?set VLLM_VENV}"
PREWARM_ISL="${PREWARM_ISL:-8192}"
PREWARM_OSL="${PREWARM_OSL:-8}"
PREWARM_PROMPTS="${PREWARM_PROMPTS:-4}"
PREWARM_C_HIGH="${PREWARM_C_HIGH:-4}"
PREWARM_TIMEOUT="${PREWARM_TIMEOUT:-600}"
PREWARM_TOKENIZER_MODE="${PREWARM_TOKENIZER_MODE:-deepseek_v4}"
PREWARM_LOG="${PREWARM_LOG:-}"

VLLM_BIN="${VLLM_VENV}/bin/vllm"
test -x "${VLLM_BIN}" || { echo "[prewarm] ${VLLM_BIN} not executable" >&2; exit 1; }

bench_round() {
  local label="$1"
  local concurrency="$2"
  echo "[prewarm] ${label} c=${concurrency} ISL=${PREWARM_ISL} OSL=${PREWARM_OSL} prompts=${PREWARM_PROMPTS}"
  local args=(
    bench serve
    --model "${MODEL_ID}"
    --tokenizer-mode "${PREWARM_TOKENIZER_MODE}"
    --dataset-name random
    --num-prompts "${PREWARM_PROMPTS}"
    --max-concurrency "${concurrency}"
    --base-url "http://${API_HOST}:${API_PORT}"
    --random-input-len "${PREWARM_ISL}"
    --random-output-len "${PREWARM_OSL}"
    --temperature 1.0
    --ignore-eos
  )
  if [[ -n "${PREWARM_LOG}" ]]; then
    timeout "${PREWARM_TIMEOUT}" "${VLLM_BIN}" "${args[@]}" >> "${PREWARM_LOG}" 2>&1
  else
    timeout "${PREWARM_TIMEOUT}" "${VLLM_BIN}" "${args[@]}" > /dev/null 2>&1
  fi
}

t0=$(date +%s)
# Round 1: c=1 single-stream burst — warms the eagle / spec-decode
# kernels at the 1-request shape that real low-concurrency users hit.
bench_round "single-stream burst" 1
# Round 2: c=PREWARM_C_HIGH multi-request burst — warms the
# multi-prefill indexer path, the chunked-prefill metadata, and the
# decode-time _fp8_paged_mqa_logits_kernel at BLOCK_M for the largest
# in-flight batch.
bench_round "multi-stream burst" "${PREWARM_C_HIGH}"
t1=$(date +%s)
echo "[prewarm] done in $((t1-t0))s"
