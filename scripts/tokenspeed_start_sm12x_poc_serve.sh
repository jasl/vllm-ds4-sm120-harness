#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

TOKENSPEED_ROOT="${TOKENSPEED_ROOT:-}"
TOKENSPEED_VENV="${TOKENSPEED_VENV:-${TOKENSPEED_ROOT}/.venv}"
TOKENSPEED_MODEL_ID="${TOKENSPEED_MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
TOKENSPEED_API_HOST="${TOKENSPEED_API_HOST:-127.0.0.1}"
TOKENSPEED_API_PORT="${TOKENSPEED_API_PORT:-8000}"
TOKENSPEED_PYTHON="${TOKENSPEED_PYTHON:-${TOKENSPEED_VENV}/bin/python}"
TOKENSPEED_ATTN_TP_SIZE="${TOKENSPEED_ATTN_TP_SIZE:-2}"
TOKENSPEED_ENABLE_EXPERT_PARALLEL="${TOKENSPEED_ENABLE_EXPERT_PARALLEL:-1}"
TOKENSPEED_KV_CACHE_DTYPE="${TOKENSPEED_KV_CACHE_DTYPE:-fp8}"
TOKENSPEED_BLOCK_SIZE="${TOKENSPEED_BLOCK_SIZE:-256}"
TOKENSPEED_GPU_MEMORY_UTILIZATION="${TOKENSPEED_GPU_MEMORY_UTILIZATION:-0.98}"
TOKENSPEED_MAX_MODEL_LEN="${TOKENSPEED_MAX_MODEL_LEN:-65536}"
TOKENSPEED_MAX_NUM_SEQS="${TOKENSPEED_MAX_NUM_SEQS:-2}"
TOKENSPEED_ENFORCE_EAGER="${TOKENSPEED_ENFORCE_EAGER:-1}"
TOKENSPEED_DISABLE_KVSTORE="${TOKENSPEED_DISABLE_KVSTORE:-1}"

if [[ -z "${TOKENSPEED_ROOT}" ]]; then
  printf 'missing TOKENSPEED_ROOT; source configs/tokenspeed_sm12x_poc_serve.env.example or set it in .env\n' >&2
  exit 2
fi

if [[ ! -x "${TOKENSPEED_PYTHON}" ]]; then
  printf 'TOKENSPEED_PYTHON is not executable: %s\n' "${TOKENSPEED_PYTHON}" >&2
  exit 2
fi

export PATH="${TOKENSPEED_VENV}/bin:${CUDA_HOME:-/usr/local/cuda}/bin:${PATH}"
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}"
export TRITON_PTXAS_PATH="${TRITON_PTXAS_PATH:-${CUDA_HOME}/bin/ptxas}"
export TOKENSPEED_KERNEL_BACKEND="${TOKENSPEED_KERNEL_BACKEND:-cuda}"
export TOKENSPEED_CUDA_ARCH_LIST="${TOKENSPEED_CUDA_ARCH_LIST:-120f}"
export TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST:-12.0a}"

if [[ "${TOKENSPEED_USE_SOURCE_PATH:-0}" == "1" ]]; then
  export PYTHONPATH="${TOKENSPEED_ROOT}/python:${PYTHONPATH:-}"
fi

if [[ "${TOKENSPEED_USE_KERNEL_SOURCE_PATH:-0}" == "1" ]]; then
  export PYTHONPATH="${TOKENSPEED_ROOT}/tokenspeed-kernel/python:${PYTHONPATH:-}"
fi

serve_args=(
  -m tokenspeed.cli
  serve
  "${TOKENSPEED_MODEL_ID}"
  --host "${TOKENSPEED_API_HOST}"
  --port "${TOKENSPEED_API_PORT}"
  --trust-remote-code
  --kv-cache-dtype "${TOKENSPEED_KV_CACHE_DTYPE}"
  --block-size "${TOKENSPEED_BLOCK_SIZE}"
  --attn-tp-size "${TOKENSPEED_ATTN_TP_SIZE}"
  --gpu-memory-utilization "${TOKENSPEED_GPU_MEMORY_UTILIZATION}"
  --max-model-len "${TOKENSPEED_MAX_MODEL_LEN}"
  --max-num-seqs "${TOKENSPEED_MAX_NUM_SEQS}"
  --tokenizer-mode deepseek_v4
  --tool-call-parser deepseek_v4
  --reasoning-parser deepseek_v4
)

if [[ "${TOKENSPEED_ENABLE_EXPERT_PARALLEL}" == "1" ]]; then
  serve_args+=(--enable-expert-parallel)
fi

if [[ "${TOKENSPEED_ENFORCE_EAGER}" == "1" ]]; then
  serve_args+=(--enforce-eager)
fi

if [[ "${TOKENSPEED_DISABLE_KVSTORE}" == "1" ]]; then
  serve_args+=(--disable-kvstore)
fi

if [[ -n "${TOKENSPEED_MAX_TOTAL_TOKENS:-}" ]]; then
  serve_args+=(--max-total-tokens "${TOKENSPEED_MAX_TOTAL_TOKENS}")
fi

if [[ -n "${TOKENSPEED_QUANTIZATION:-}" ]]; then
  serve_args+=(--quantization "${TOKENSPEED_QUANTIZATION}")
fi

if [[ -n "${TOKENSPEED_EXTRA_ARGS:-}" ]]; then
  # shellcheck disable=SC2206
  extra_args=(${TOKENSPEED_EXTRA_ARGS})
  serve_args+=("${extra_args[@]}")
fi

printf 'Starting TokenSpeed DeepSeek V4 SM12x PoC server on %s:%s\n' \
  "${TOKENSPEED_API_HOST}" "${TOKENSPEED_API_PORT}" >&2
exec "${TOKENSPEED_PYTHON}" "${serve_args[@]}"
