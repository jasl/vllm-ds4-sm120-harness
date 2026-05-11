#!/usr/bin/env bash
# Optional harness tool: autotune dense FP8 W8A8 block-scaled GEMM configs
# for SM12x DeepSeek V4 Flash on the local host. Wraps vLLM's
# `benchmarks/kernels/benchmark_w8a8_block_fp8.py` so we don't fork the
# upstream tuner.
#
# Required env:
#   OUT_DIR             Output directory.
#
# Optional env:
#   VLLM_REPO           Path to local vllm checkout (default
#                       /home/jasl/Workspace/vllm).
#   BATCH_SIZES         Comma-separated M values (default 1,2,4,8,16,32,64,128).
#   SHAPES              Override shapes spec, e.g. "1536,4096:16384,1024"
#                       (default: 6 SM12x DSv4 shapes from
#                       tests/quantization/test_sm12x_tuned_config_lookup.py).
#   GPU_ID              CUDA device index (default 0).
#   BLOCK_N, BLOCK_K    FP8 block shape (defaults 128, 128).
#   OUT_DTYPE           bfloat16 (default) or float16.
#   DRY_RUN             1 to print plan and exit.
#
# Two-GPU parallel split: launch two instances with different GPU_ID and
# disjoint BATCH_SIZES, then merge JSON files (each instance writes its own
# JSON; the *latter* run will overwrite if both touch the same M-key, so
# split by M values, not by N/K).
#
# Output:
#   ${OUT_DIR}/N=*,K=*,device_name=*,dtype=fp8_w8a8,block_shape=[Bn,Bk].json
#   ${OUT_DIR}/tuning_summary.json
#   ${OUT_DIR}/tune.log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

OUT_DIR="${OUT_DIR:?set OUT_DIR}"
VLLM_REPO="${VLLM_REPO:-/home/jasl/Workspace/vllm}"
BATCH_SIZES="${BATCH_SIZES:-1,2,4,8,16,32,64,128}"
SHAPES="${SHAPES:-}"
GPU_ID="${GPU_ID:-0}"
BLOCK_N="${BLOCK_N:-128}"
BLOCK_K="${BLOCK_K:-128}"
OUT_DTYPE="${OUT_DTYPE:-bfloat16}"
DRY_RUN="${DRY_RUN:-0}"

mkdir -p "${OUT_DIR}"

# Sanity: make sure we're on an SM12x GPU.
if command -v nvidia-smi >/dev/null 2>&1; then
  gpu_cc="$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader -i "${GPU_ID}" 2>/dev/null | head -1 || true)"
  case "${gpu_cc}" in
    12.*) echo "[harness] confirmed SM12x device (cc=${gpu_cc})" ;;
    *)
      echo "[harness] WARNING: GPU ${GPU_ID} reports compute_cap=${gpu_cc} (expected 12.x for SM12x). Continuing anyway." >&2
      ;;
  esac
fi

driver_args=(
  --vllm-repo "${VLLM_REPO}"
  --out-dir "${OUT_DIR}"
  --batch-sizes "${BATCH_SIZES}"
  --block-n "${BLOCK_N}"
  --block-k "${BLOCK_K}"
  --out-dtype "${OUT_DTYPE}"
  --gpu-id "${GPU_ID}"
)
if [[ -n "${SHAPES}" ]]; then
  driver_args+=(--shapes "${SHAPES}")
fi
if [[ "${DRY_RUN}" == "1" ]]; then
  driver_args+=(--dry-run)
fi

echo "[harness] OUT_DIR=${OUT_DIR}"
echo "[harness] VLLM_REPO=${VLLM_REPO}"
echo "[harness] GPU_ID=${GPU_ID} BATCH_SIZES=${BATCH_SIZES} BLOCK=(${BLOCK_N},${BLOCK_K}) OUT_DTYPE=${OUT_DTYPE}"
[[ -n "${SHAPES}" ]] && echo "[harness] SHAPES=${SHAPES}"

log="${OUT_DIR}/tune.log"
echo "[harness] streaming log to ${log}"
python3 "${SCRIPT_DIR}/_fp8_block_tune_driver.py" "${driver_args[@]}" 2>&1 | tee "${log}"

echo "[harness] tuning complete. JSON outputs in ${OUT_DIR}:"
ls -la "${OUT_DIR}" | grep -E '\.json$|tuning_summary' || true

echo
echo "[harness] next steps:"
echo "  1. Inspect ${OUT_DIR}/tuning_summary.json"
echo "  2. Copy *.json into \${VLLM_REPO}/vllm/model_executor/layers/quantization/utils/configs/"
echo "  3. Restart vLLM serve"
echo "  4. Re-run scripts/run_decode_profile.sh and compare top-kernel times"
