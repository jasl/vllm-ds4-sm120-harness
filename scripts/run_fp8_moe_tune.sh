#!/usr/bin/env bash
# Optional harness tool: autotune fused-MoE FP8 W8A8 block-scaled configs for
# SM12x DeepSeek V4 Flash on the local host. Wraps the in-process driver
# `_fp8_moe_tune_driver.py` which in turn imports vLLM's
# `benchmarks/kernels/benchmark_moe.py` (`benchmark_config`, `save_configs`,
# `get_configs_compute_bound`).
#
# Why we need this:
#   * Upstream `benchmark_moe.py` derives (E, N, hidden, topk) from `--model`
#     via `get_model_params(config)` which does NOT include
#     `DeepseekV4ForCausalLM`. Direct invocation lets us specify those four
#     numbers explicitly per topology.
#   * The shape we deploy with (`--tensor-parallel-size 2
#     --enable-expert-parallel`) resolves to E=128, N=2048 on DSv4-Flash and
#     has **no tuned config in the tree today** — we've been on Triton's
#     default heuristic for the fused-MoE kernel that dominates MoE wall time
#     in our serve. This script is what closes that gap.
#
# Required env:
#   OUT_DIR             Output directory.
#
# Optional env:
#   VLLM_REPO           Path to local vllm checkout
#                       (default /home/jasl/Workspace/vllm).
#   BATCH_SIZES         Comma-separated M values
#                       (default 1,2,4,8,16,32,64,128,256,512).
#   SHAPES              Override shape spec, e.g.
#                       "128,4096,4096,6:64,4096,4096,6" — each chunk is
#                       "E,shard_int_size,hidden,topk". Default: 4 DSv4-Flash
#                       shapes covering TP=2/4/8 with EP plus TP=2 no-EP
#                       (typical 2/4/8-card RTX PRO 6000 and 2/4-node GB10
#                       deployments).
#   GPU_ID              CUDA device index (default 0).
#   BLOCK_N, BLOCK_K    FP8 block shape (defaults 128, 128).
#   NUM_ITERS           Base timing iters per config (default 20, matches
#                       upstream tune()).
#                       Auto-reduced for large M (M>=256→10, M>=64→15) unless
#                       NO_AUTO_ITERS=1.
#   NO_AUTO_ITERS       1 disables M-aware iter reduction.
#   ABORT_SECONDS       Per-(label, M) wall-clock cap (default 1200, i.e.
#                       20 min). 0 disables.
#   DRY_RUN             1 to print plan and exit.
#
# Two-GPU parallel split: launch two instances with different GPU_ID and
# disjoint BATCH_SIZES. Each writes its own JSON per shape; the *latter* will
# overwrite if both touch the same (E, N, block) combination — so split by M,
# never split a shape across GPUs.
#
# Output:
#   ${OUT_DIR}/E=*,N=*,device_name=*,dtype=fp8_w8a8,block_shape=[Bn,Bk].json
#   ${OUT_DIR}/tuning_summary.json
#   ${OUT_DIR}/tune.log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

OUT_DIR="${OUT_DIR:?set OUT_DIR}"
VLLM_REPO="${VLLM_REPO:-/home/jasl/Workspace/vllm}"
BATCH_SIZES="${BATCH_SIZES:-1,2,4,8,16,32,64,128,256,512}"
SHAPES="${SHAPES:-}"
GPU_ID="${GPU_ID:-0}"
BLOCK_N="${BLOCK_N:-128}"
BLOCK_K="${BLOCK_K:-128}"
NUM_ITERS="${NUM_ITERS:-20}"
NO_AUTO_ITERS="${NO_AUTO_ITERS:-0}"
ABORT_SECONDS="${ABORT_SECONDS:-1200}"
DRY_RUN="${DRY_RUN:-0}"

# Default Python is the vLLM venv if it exists (driver needs torch + vllm
# imports). Honor a user-provided PYTHON env override.
if [[ -z "${PYTHON:-}" ]]; then
  if [[ -x "${VLLM_REPO}/.venv/bin/python" ]]; then
    PYTHON="${VLLM_REPO}/.venv/bin/python"
  else
    PYTHON="python3"
  fi
fi

mkdir -p "${OUT_DIR}"

# Sanity: confirm we're on an SM12x GPU. Issue a warning otherwise but don't
# refuse — the driver itself doesn't depend on SM12x, only the resulting
# device_name in the file does.
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
  --gpu-id "${GPU_ID}"
  --num-iters "${NUM_ITERS}"
  --abort-seconds "${ABORT_SECONDS}"
)
if [[ -n "${SHAPES}" ]]; then
  driver_args+=(--shapes "${SHAPES}")
fi
if [[ "${NO_AUTO_ITERS}" == "1" ]]; then
  driver_args+=(--no-auto-iters)
fi
if [[ "${DRY_RUN}" == "1" ]]; then
  driver_args+=(--dry-run)
fi

echo "[harness] OUT_DIR=${OUT_DIR}"
echo "[harness] VLLM_REPO=${VLLM_REPO}"
echo "[harness] GPU_ID=${GPU_ID} BATCH_SIZES=${BATCH_SIZES} BLOCK=(${BLOCK_N},${BLOCK_K})"
echo "[harness] NUM_ITERS=${NUM_ITERS} NO_AUTO_ITERS=${NO_AUTO_ITERS} ABORT_SECONDS=${ABORT_SECONDS}"
echo "[harness] PYTHON=${PYTHON}"
[[ -n "${SHAPES}" ]] && echo "[harness] SHAPES=${SHAPES}"

log="${OUT_DIR}/tune.log"
echo "[harness] streaming log to ${log}"
"${PYTHON}" "${SCRIPT_DIR}/_fp8_moe_tune_driver.py" "${driver_args[@]}" 2>&1 | tee "${log}"

echo "[harness] tuning complete. JSON outputs in ${OUT_DIR}:"
ls -la "${OUT_DIR}" | grep -E 'E=.*\.json$|tuning_summary' || true

echo
echo "[harness] next steps:"
echo "  1. Inspect ${OUT_DIR}/tuning_summary.json"
echo "  2. Copy each E=...json into \${VLLM_REPO}/vllm/model_executor/layers/fused_moe/configs/"
echo "  3. (Optional) Alias to other Blackwell device names if you want the file"
echo "     picked up on RTX_PRO_6000_Blackwell_Server_Edition,"
echo "     RTX_PRO_6000_Blackwell_Max-Q_Workstation_Edition, NVIDIA_GB10 etc."
echo "  4. Restart vLLM serve and re-run a small mt-bench (c=1 + c=24) sweep to"
echo "     confirm the new configs are picked up; expect TPOT improvement at"
echo "     larger c on the MoE-bottlenecked path."
