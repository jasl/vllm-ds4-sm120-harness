#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8080}"
configure_sm120_vllm_env
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
DS4_ABSORPTION_STRESS_LABEL="${DS4_ABSORPTION_STRESS_LABEL:-ds4_absorption_stress_matrix}"
RUN_ROOT="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${DS4_ABSORPTION_STRESS_LABEL}/${RUN_TIMESTAMP}}"

RUN_DS4_STRESS_USER_FEEDBACK="${RUN_DS4_STRESS_USER_FEEDBACK:-1}"
RUN_DS4_STRESS_ISSUE10_SAFE="${RUN_DS4_STRESS_ISSUE10_SAFE:-1}"
RUN_DS4_STRESS_ISSUE8_RECHECK="${RUN_DS4_STRESS_ISSUE8_RECHECK:-0}"
RUN_DS4_STRESS_ISSUE10_HIGH_RISK="${RUN_DS4_STRESS_ISSUE10_HIGH_RISK:-0}"

ISSUE8_ALLOW_HOST_REBOOT_RISK="${ISSUE8_ALLOW_HOST_REBOOT_RISK:-0}"
ISSUE10_ALLOW_HOST_REBOOT_RISK="${ISSUE10_ALLOW_HOST_REBOOT_RISK:-0}"

mkdir -p "${RUN_ROOT}"
printf 'phase\texit_code\n' > "${RUN_ROOT}/phase_exit_codes.tsv"

capture_driver_health() {
  local label="${1:?label required}"
  local out_dir="${RUN_ROOT}/driver_health/${label}"
  mkdir -p "${out_dir}"

  {
    printf 'label=%s\n' "${label}"
    printf 'timestamp_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "${out_dir}/metadata.txt"

  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi > "${out_dir}/nvidia_smi.txt" 2>&1 || true
    nvidia-smi \
      --query-gpu=name,pci.bus_id,memory.used,utilization.gpu,temperature.gpu,power.draw \
      --format=csv,noheader \
      > "${out_dir}/nvidia_smi_query.csv" 2>&1 || true
  else
    printf '%s\n' "nvidia-smi unavailable" > "${out_dir}/nvidia_smi.txt"
  fi

  if command -v journalctl >/dev/null 2>&1; then
    journalctl -b -k --no-pager > "${out_dir}/kernel.log" 2>&1 || true
    grep -Ei 'NVRM|Xid|UVM|GPU lost|fatal|unspecified launch failure|shared memory broadcast' \
      "${out_dir}/kernel.log" > "${out_dir}/kernel_gpu_signals.log" 2>/dev/null || true
  else
    printf '%s\n' "journalctl unavailable" > "${out_dir}/kernel.log"
  fi
}

record_phase_exit() {
  local phase="${1:?phase required}"
  local code="${2:?exit code required}"
  printf '%s\t%s\n' "${phase}" "${code}" >> "${RUN_ROOT}/phase_exit_codes.tsv"
}

run_phase() {
  local phase="${1:?phase required}"
  shift

  capture_driver_health "before_${phase}"
  set +e
  "$@"
  local code="$?"
  set -e
  record_phase_exit "${phase}" "${code}"
  capture_driver_health "after_${phase}"
  return "${code}"
}

failures=0
run_child_phase() {
  local phase="${1:?phase required}"
  shift
  set +e
  run_phase "${phase}" "$@"
  local code="$?"
  set -e
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi
}

capture_driver_health "start"

if [[ "${RUN_DS4_STRESS_USER_FEEDBACK}" == "1" || "${RUN_DS4_STRESS_USER_FEEDBACK}" == "true" ]]; then
  run_child_phase user_feedback_matrix env \
    OUT_DIR="${RUN_ROOT}/user_feedback" \
    MODEL="${MODEL}" HOST="${HOST}" PORT="${PORT}" \
    SM120_VLLM_REPO="${SM120_VLLM_REPO}" SM120_VLLM_VENV="${SM120_VLLM_VENV}" \
    SM120_PYTHON="${SM120_PYTHON}" SM120_VLLM_BIN="${SM120_VLLM_BIN}" \
    B200_VLLM_REPO="${B200_VLLM_REPO}" B200_VLLM_VENV="${B200_VLLM_VENV}" \
    PYTHON="${PYTHON}" VLLM_BIN="${VLLM_BIN}" \
    USER_FEEDBACK_MATRIX_LABEL="${DS4_ABSORPTION_STRESS_LABEL}_user_feedback" \
    RUN_USER_FEEDBACK_ISSUE10=0 \
    "${SCRIPT_DIR}/run_sm120_user_feedback_matrix.sh"
fi

if [[ "${RUN_DS4_STRESS_ISSUE10_SAFE}" == "1" || "${RUN_DS4_STRESS_ISSUE10_SAFE}" == "true" ]]; then
  run_child_phase issue10_safe_proxy env \
    OUT_DIR="${RUN_ROOT}/issue10_safe" \
    MODEL="${MODEL}" HOST="${HOST}" PORT="$((PORT + 2))" \
    SM120_VLLM_REPO="${SM120_VLLM_REPO}" SM120_VLLM_VENV="${SM120_VLLM_VENV}" \
    SM120_PYTHON="${SM120_PYTHON}" SM120_VLLM_BIN="${SM120_VLLM_BIN}" \
    B200_VLLM_REPO="${B200_VLLM_REPO}" B200_VLLM_VENV="${B200_VLLM_VENV}" \
    PYTHON="${PYTHON}" VLLM_BIN="${VLLM_BIN}" \
    B200_BASELINE_LABEL="${DS4_ABSORPTION_STRESS_LABEL}_issue10_safe" \
    SERVE_MAX_MODEL_LEN=65536 \
    ISSUE10_ALLOW_HOST_REBOOT_RISK=0 \
    "${SCRIPT_DIR}/run_sm120_issue10_startup_gate.sh"
fi

if [[ "${RUN_DS4_STRESS_ISSUE8_RECHECK}" == "1" || "${RUN_DS4_STRESS_ISSUE8_RECHECK}" == "true" ]]; then
  if [[ "${ISSUE8_ALLOW_HOST_REBOOT_RISK}" != "1" ]]; then
    cat >&2 <<'EOF'
Refusing to run the issue #8 128K-class crash recheck by default.

The prior artifact 20260525_issue8_local_proxy_124k_c2_decode1024 left the GPU
driver in a fatal state once. Set ISSUE8_ALLOW_HOST_REBOOT_RISK=1 only when a
host reboot is acceptable.
EOF
    record_phase_exit issue8_crash_recheck_refused 2
    failures=1
  else
    run_child_phase issue8_crash_recheck env \
      OUT_DIR="${RUN_ROOT}/issue8_crash_recheck" \
      MODEL="${MODEL}" HOST="${HOST}" PORT="$((PORT + 3))" \
      SM120_VLLM_REPO="${SM120_VLLM_REPO}" SM120_VLLM_VENV="${SM120_VLLM_VENV}" \
      SM120_PYTHON="${SM120_PYTHON}" SM120_VLLM_BIN="${SM120_VLLM_BIN}" \
      B200_VLLM_REPO="${B200_VLLM_REPO}" B200_VLLM_VENV="${B200_VLLM_VENV}" \
      PYTHON="${PYTHON}" VLLM_BIN="${VLLM_BIN}" \
      B200_BASELINE_LABEL="${DS4_ABSORPTION_STRESS_LABEL}_issue8_recheck" \
      B200_BASELINE_VARIANTS=nomtp \
      B200_BASELINE_PHASES=long_context_decode_concurrency \
      B200_TENSOR_PARALLEL_SIZE=2 \
      B200_BLOCK_SIZE=256 \
      B200_KV_CACHE_DTYPE=fp8 \
      SERVE_MAX_MODEL_LEN=131072 \
      SERVE_PREFIX_CACHE_MODE=enabled \
      SERVE_USE_FP4_INDEXER_CACHE=0 \
      RUN_LONG_CONTEXT_DECODE_CONCURRENCY=1 \
      LONG_CONTEXT_DECODE_CASE_NAME=issue8_20260525_crash_recheck \
      LONG_CONTEXT_DECODE_LINE_COUNTS=4000 \
      LONG_CONTEXT_DECODE_CONCURRENCY=1,2 \
      LONG_CONTEXT_DECODE_CACHE_MODES=cold \
      LONG_CONTEXT_DECODE_REPEAT_COUNT=1 \
      LONG_CONTEXT_DECODE_MAX_TOKENS=1024 \
      LONG_CONTEXT_DECODE_PREWARM=0 \
      B200_EXTRA_SERVE_ARGS="--gpu-memory-utilization 0.977 --max-num-batched-tokens 4176 --max-num-seqs 8 --load-format safetensors --tokenizer ${MODEL} --enable-chunked-prefill --disable-custom-all-reduce --default-chat-template-kwargs '{\"thinking\": true}' --compilation-config '{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}' --override-generation-config '{\"temperature\": 1.0, \"top_p\": 1.0}'" \
      "${SCRIPT_DIR}/run_b200_baseline.sh"
  fi
fi

if [[ "${RUN_DS4_STRESS_ISSUE10_HIGH_RISK}" == "1" || "${RUN_DS4_STRESS_ISSUE10_HIGH_RISK}" == "true" ]]; then
  run_child_phase issue10_high_risk_proxy env \
    OUT_DIR="${RUN_ROOT}/issue10_high_risk" \
    MODEL="${MODEL}" HOST="${HOST}" PORT="$((PORT + 4))" \
    SM120_VLLM_REPO="${SM120_VLLM_REPO}" SM120_VLLM_VENV="${SM120_VLLM_VENV}" \
    SM120_PYTHON="${SM120_PYTHON}" SM120_VLLM_BIN="${SM120_VLLM_BIN}" \
    B200_VLLM_REPO="${B200_VLLM_REPO}" B200_VLLM_VENV="${B200_VLLM_VENV}" \
    PYTHON="${PYTHON}" VLLM_BIN="${VLLM_BIN}" \
    B200_BASELINE_LABEL="${DS4_ABSORPTION_STRESS_LABEL}_issue10_high_risk" \
    SERVE_MAX_MODEL_LEN="${ISSUE10_HIGH_RISK_MAX_MODEL_LEN:-131072}" \
    STREAMING_PRESSURE_MATRIX_CASE_SPECS="issue10_c2_124k:2:1:4000:64,issue10_c4_59k:4:1:1900:128" \
    ISSUE10_ALLOW_HOST_REBOOT_RISK="${ISSUE10_ALLOW_HOST_REBOOT_RISK}" \
    "${SCRIPT_DIR}/run_sm120_issue10_startup_gate.sh"
fi

capture_driver_health "end"
echo "wrote ${RUN_ROOT}"
exit "${failures}"
