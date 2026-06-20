#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

required_vars=(
  HEAD_HOST
  WORKER_HOST
  HEAD_ROCE_IP
  WORKER_ROCE_IP
  ROCE_IFACE
  NCCL_IB_HCA
  VLLM_ROOT
  VLLM_VENV
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    printf 'missing required environment variable: %s\n' "${var}" >&2
    exit 2
  fi
done

shell_quote() {
  printf '%q' "$1"
}

append_env_allowlist() {
  local current="$1"
  local var="$2"
  local normalized=" ${current//,/ } "

  if [[ -z "${!var:-}" || "${normalized}" == *" ${var} "* ]]; then
    printf '%s' "${current}"
    return
  fi
  if [[ -n "${current}" ]]; then
    printf '%s,%s' "${current}" "${var}"
  else
    printf '%s' "${var}"
  fi
}

run_remote() {
  local host="$1"
  shift
  # SSH_OPTS is intentionally a user-provided word list.
  # shellcheck disable=SC2086
  ssh ${SSH_OPTS:-} "${host}" "$@"
}

stop_remote_vllm() {
  local host="$1"
  run_remote "${host}" \
    "pkill -TERM -f '[v]llm.entrypoints.cli.main|[V]LLM::|[v]llm serve' >/dev/null 2>&1 || true; sleep 3; pkill -KILL -f '[v]llm.entrypoints.cli.main|[V]LLM::|[v]llm serve' >/dev/null 2>&1 || true"
}

fetch_remote_file() {
  local remote_path="$1"
  local local_path="$2"

  mkdir -p "$(dirname -- "${local_path}")"
  if run_remote "${HEAD_HOST}" "test -f $(shell_quote "${remote_path}")"; then
    run_remote "${HEAD_HOST}" "cat $(shell_quote "${remote_path}")" > "${local_path}"
  fi
}

capture_remote_driver_health() {
  local host="$1"
  local label="$2"
  local out_dir="$3"
  local host_dir="${out_dir}/${label}"
  local signal_pattern
  signal_pattern='NVRM:.*(Out of memory|NV_ERR_NO_MEMORY)|Xid|UVM|lost from the bus|fallen off|GPU lost|unspecified launch failure|illegal memory access|device-side assert|global fatal'

  mkdir -p "${host_dir}"
  run_remote "${host}" \
    "date -Ins; hostname; uname -a; uptime" \
    > "${host_dir}/system.txt" 2>&1 || true
  run_remote "${host}" \
    "nvidia-smi; nvidia-smi pmon -c 1 || true" \
    > "${host_dir}/nvidia_smi.txt" 2>&1 || true
  run_remote "${host}" \
    "journalctl -b -k --no-pager | grep -Ei $(shell_quote "${signal_pattern}") | tail -n 200 || true" \
    > "${host_dir}/kernel_gpu_signals.log" 2>&1 || true
}

run_remote_streaming_matrix() {
  local remote_out_dir="$1"
  local variant="$2"
  local max_batched_tokens="$3"

  run_remote "${HEAD_HOST}" \
    "cd $(shell_quote "${REMOTE_HARNESS_ROOT}") && env \
      PYTHON=$(shell_quote "${VLLM_VENV}/bin/python") \
      VLLM_ROOT=$(shell_quote "${VLLM_ROOT}") \
      BASE_URL=$(shell_quote "http://127.0.0.1:${API_PORT}") \
      MODEL=$(shell_quote "${MODEL_ID}") \
      GPU_TOPOLOGY_SLUG=$(shell_quote "${GPU_TOPOLOGY_SLUG}") \
      BRANCH_NAME=$(shell_quote "${BRANCH_NAME}") \
      OUT_DIR=$(shell_quote "${remote_out_dir}") \
      STREAMING_PRESSURE_MATRIX_VARIANT=$(shell_quote "${variant}-mbt${max_batched_tokens}") \
      STREAMING_PRESSURE_MATRIX_CASE_NAME=$(shell_quote "${GB10_FORUM53_CASE_NAME}") \
      STREAMING_PRESSURE_MATRIX_CASE_SPECS=$(shell_quote "${GB10_FORUM53_CASE_SPECS}") \
      STREAMING_PRESSURE_MATRIX_TIMEOUT=$(shell_quote "${GB10_FORUM53_TIMEOUT}") \
      STREAMING_PRESSURE_MATRIX_TEMPERATURE=$(shell_quote "${GB10_FORUM53_TEMPERATURE}") \
      STREAMING_PRESSURE_MATRIX_MAX_TTFT_SECONDS=$(shell_quote "${GB10_FORUM53_MAX_TTFT_SECONDS}") \
      STREAMING_PRESSURE_MATRIX_MAX_ELAPSED_SECONDS=$(shell_quote "${GB10_FORUM53_MAX_ELAPSED_SECONDS}") \
      STREAMING_PRESSURE_MATRIX_FAIL_ON_SLOW=$(shell_quote "${GB10_FORUM53_FAIL_ON_SLOW}") \
      SERVER_STARTUP_TIMEOUT=$(shell_quote "${GB10_FORUM53_SERVER_STARTUP_TIMEOUT}") \
      $(shell_quote "${REMOTE_HARNESS_ROOT}/scripts/run_streaming_pressure_matrix.sh")"
}

variant_speculative_config() {
  local variant="$1"
  case "${variant}" in
    nomtp)
      printf ''
      ;;
    mtp|mtp2)
      printf '{"method":"mtp","num_speculative_tokens":2}'
      ;;
    *)
      printf 'unsupported GB10_FORUM53 variant: %s\n' "${variant}" >&2
      return 2
      ;;
  esac
}

BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-2x_gb10_sm121}"
GB10_FORUM53_PROFILE="${GB10_FORUM53_PROFILE:-safe_default}"
case "${GB10_FORUM53_PROFILE}" in
  safe_default|default)
    ;;
  c4_prefix_cache_pressure)
    GB10_FORUM53_LABEL="${GB10_FORUM53_LABEL:-gb10_forum53_c4_prefix_cache_pressure}"
    GB10_FORUM53_CASE_NAME="${GB10_FORUM53_CASE_NAME:-forum53_c4_prefix_cache_pressure}"
    GB10_FORUM53_CASE_SPECS="${GB10_FORUM53_CASE_SPECS:-forum53_c2:2:2:3200:256,forum53_c4:4:2:3200:256}"
    GB10_FORUM53_MAX_NUM_SEQS="${GB10_FORUM53_MAX_NUM_SEQS:-4}"
    ;;
  long_prefix_400k_c6c8)
    GB10_FORUM53_LABEL="${GB10_FORUM53_LABEL:-gb10_forum53_long_prefix_400k_pressure}"
    GB10_FORUM53_CASE_NAME="${GB10_FORUM53_CASE_NAME:-forum53_long_prefix_400k_pressure}"
    GB10_FORUM53_CASE_SPECS="${GB10_FORUM53_CASE_SPECS:-forum53_c6_400k:6:2:16000:64:1800:7200,forum53_c8_400k:8:2:16000:64:1800:7200}"
    GB10_FORUM53_TIMEOUT="${GB10_FORUM53_TIMEOUT:-7200}"
    GB10_FORUM53_MAX_TTFT_SECONDS="${GB10_FORUM53_MAX_TTFT_SECONDS:-1800}"
    GB10_FORUM53_MAX_ELAPSED_SECONDS="${GB10_FORUM53_MAX_ELAPSED_SECONDS:-7200}"
    GB10_FORUM53_SERVER_STARTUP_TIMEOUT="${GB10_FORUM53_SERVER_STARTUP_TIMEOUT:-180}"
    GB10_FORUM53_MAX_MODEL_LEN="${GB10_FORUM53_MAX_MODEL_LEN:-458752}"
    GB10_FORUM53_MAX_NUM_SEQS="${GB10_FORUM53_MAX_NUM_SEQS:-8}"
    GB10_FORUM53_MIN_AVAILABLE_MEM_GIB="${GB10_FORUM53_MIN_AVAILABLE_MEM_GIB:-112}"
    ;;
  *)
    printf 'unsupported GB10_FORUM53_PROFILE: %s\n' "${GB10_FORUM53_PROFILE}" >&2
    printf 'supported profiles: safe_default, c4_prefix_cache_pressure, long_prefix_400k_c6c8\n' >&2
    exit 2
    ;;
esac
GB10_FORUM53_LABEL="${GB10_FORUM53_LABEL:-gb10_forum53_multi_user_gate}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${GB10_FORUM53_LABEL}/${RUN_TIMESTAMP}}"

REMOTE_HARNESS_ROOT="${GB10_FORUM53_REMOTE_HARNESS_ROOT:-$(dirname -- "${VLLM_ROOT}")}"
REMOTE_RUN_ROOT="${GB10_FORUM53_REMOTE_RUN_ROOT:-${REMOTE_HARNESS_ROOT}/artifacts/${GB10_FORUM53_LABEL}/${RUN_TIMESTAMP}}"

GB10_FORUM53_VARIANTS="${GB10_FORUM53_VARIANTS:-nomtp}"
GB10_FORUM53_OPTIONAL_MTP2="${GB10_FORUM53_OPTIONAL_MTP2:-0}"
if [[ "${GB10_FORUM53_OPTIONAL_MTP2}" == "1" || "${GB10_FORUM53_OPTIONAL_MTP2}" == "true" ]]; then
  normalized_variants=" ${GB10_FORUM53_VARIANTS//,/ } "
  if [[ "${normalized_variants}" != *" mtp2 "* ]]; then
    GB10_FORUM53_VARIANTS="${GB10_FORUM53_VARIANTS},mtp2"
  fi
fi
GB10_FORUM53_D512_MULTI_PREFILL_ENV="${GB10_FORUM53_D512_MULTI_PREFILL_ENV:-0}"
case "${GB10_FORUM53_D512_MULTI_PREFILL_ENV}" in
  0|1|default) ;;
  *)
    printf 'GB10_FORUM53_D512_MULTI_PREFILL_ENV must be 0, 1, or default; got %s\n' \
      "${GB10_FORUM53_D512_MULTI_PREFILL_ENV}" >&2
    exit 2
    ;;
esac
GB10_FORUM53_BATCHED_TOKEN_SWEEP="${GB10_FORUM53_BATCHED_TOKEN_SWEEP:-4096}"
GB10_FORUM53_CASE_NAME="${GB10_FORUM53_CASE_NAME:-forum53_multi_user_prefix_cache}"
GB10_FORUM53_CASE_SPECS="${GB10_FORUM53_CASE_SPECS:-forum53_c2:2:2:3200:256}"
GB10_FORUM53_TIMEOUT="${GB10_FORUM53_TIMEOUT:-1800}"
GB10_FORUM53_MAX_TTFT_SECONDS="${GB10_FORUM53_MAX_TTFT_SECONDS:-600}"
GB10_FORUM53_MAX_ELAPSED_SECONDS="${GB10_FORUM53_MAX_ELAPSED_SECONDS:-1800}"
GB10_FORUM53_FAIL_ON_SLOW="${GB10_FORUM53_FAIL_ON_SLOW:-0}"
GB10_FORUM53_TEMPERATURE="${GB10_FORUM53_TEMPERATURE:-0}"
GB10_FORUM53_SERVER_STARTUP_TIMEOUT="${GB10_FORUM53_SERVER_STARTUP_TIMEOUT:-45}"
GB10_FORUM53_ENABLE_EXPERT_PARALLEL="${GB10_FORUM53_ENABLE_EXPERT_PARALLEL:-0}"
GB10_FORUM53_ALLOW_DRIVER_SIGNALS="${GB10_FORUM53_ALLOW_DRIVER_SIGNALS:-0}"
# Known-benign driver signals to allowlist: excluded from the fail count but still
# recorded/reported (NOT silently masked). Default = the non-fatal NCCL 2.30.7
# communicator-init cuMem descriptor OOM on GB10 (NV_ERR_NO_MEMORY from
# _memdescAllocInternal). That is the irreducible cost of the REQUIRED NCCL >=2.30.7
# upgrade (only 2.30.7 runs; see docs/dgx_spark_bare_metal_cluster.md), reproduced and
# exhaustively root-caused 2026-06-15 -- it is NOT a quality regression. Real signals
# (Xid, illegal access, device-side assert, GPU lost, other-site OOMs) do NOT match this
# pattern and still count + fail the gate. Set to empty to disable the allowlist.
GB10_FORUM53_DRIVER_SIGNAL_ALLOWLIST="${GB10_FORUM53_DRIVER_SIGNAL_ALLOWLIST:-NV_ERR_NO_MEMORY.*_memdescAllocInternal}"
GB10_FORUM53_SAFE_TOTAL_KV_TOKENS="${GB10_FORUM53_SAFE_TOTAL_KV_TOKENS:-2048898}"
GB10_FORUM53_CONTEXT_SAFETY_PERCENT="${GB10_FORUM53_CONTEXT_SAFETY_PERCENT:-70}"
GB10_FORUM53_SKIP_CONTEXT_GUARD="${GB10_FORUM53_SKIP_CONTEXT_GUARD:-0}"

case "${GB10_FORUM53_ENABLE_EXPERT_PARALLEL}" in
  1|true)
    gb10_forum53_enable_expert_parallel=1
    ;;
  0|false)
    gb10_forum53_enable_expert_parallel=0
    ;;
  *)
    printf 'GB10_FORUM53_ENABLE_EXPERT_PARALLEL must be 0/1 or true/false; got %s\n' \
      "${GB10_FORUM53_ENABLE_EXPERT_PARALLEL}" >&2
    exit 2
    ;;
esac

MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
API_PORT="${API_PORT:-8000}"
TP_SIZE="${GB10_FORUM53_TP_SIZE:-2}"
PP_SIZE="${GB10_FORUM53_PP_SIZE:-1}"
MAX_MODEL_LEN="${GB10_FORUM53_MAX_MODEL_LEN:-81920}"
GPU_MEMORY_UTILIZATION="${GB10_FORUM53_GPU_MEMORY_UTILIZATION:-0.685}"
MAX_NUM_SEQS="${GB10_FORUM53_MAX_NUM_SEQS:-2}"
BLOCK_SIZE="${GB10_FORUM53_BLOCK_SIZE:-256}"
KV_CACHE_DTYPE="${GB10_FORUM53_KV_CACHE_DTYPE:-fp8}"
MIN_AVAILABLE_MEM_GIB="${GB10_FORUM53_MIN_AVAILABLE_MEM_GIB:-96}"
SERVE_COMPILATION_CONFIG="${GB10_FORUM53_COMPILATION_CONFIG:-{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}}"

mkdir -p "${OUT_DIR}"
printf '%s\n' "${REMOTE_RUN_ROOT}" > "${OUT_DIR}/remote_run_root.txt"
printf '%s\n' "${GB10_FORUM53_PROFILE}" > "${OUT_DIR}/profile.txt"

positive_integer() {
  local value="$1"
  local name="$2"
  if ! [[ "${value}" =~ ^[0-9]+$ ]] || (( value < 1 )); then
    printf '%s must be a positive integer: %s\n' "${name}" "${value}" >&2
    exit 2
  fi
}

positive_integer "${GB10_FORUM53_SAFE_TOTAL_KV_TOKENS}" \
  "GB10_FORUM53_SAFE_TOTAL_KV_TOKENS"
positive_integer "${GB10_FORUM53_CONTEXT_SAFETY_PERCENT}" \
  "GB10_FORUM53_CONTEXT_SAFETY_PERCENT"
positive_integer "${MAX_NUM_SEQS}" "GB10_FORUM53_MAX_NUM_SEQS"
positive_integer "${MAX_MODEL_LEN}" "GB10_FORUM53_MAX_MODEL_LEN"

safe_context_limit() {
  local max_num_seqs="$1"
  printf '%s\n' \
    "$(( GB10_FORUM53_SAFE_TOTAL_KV_TOKENS * GB10_FORUM53_CONTEXT_SAFETY_PERCENT / 100 / max_num_seqs ))"
}

SAFE_CONTEXT_LIMIT="$(safe_context_limit "${MAX_NUM_SEQS}")"
{
  printf 'max_num_seqs,safe_max_model_len\n'
  for seqs in 1 2 4 6 8; do
    printf '%s,%s\n' "${seqs}" "$(safe_context_limit "${seqs}")"
  done
} > "${OUT_DIR}/forum53_context_safety.csv"
{
  printf 'safe_total_kv_tokens=%s\n' "${GB10_FORUM53_SAFE_TOTAL_KV_TOKENS}"
  printf 'context_safety_percent=%s\n' "${GB10_FORUM53_CONTEXT_SAFETY_PERCENT}"
  printf 'configured_max_num_seqs=%s\n' "${MAX_NUM_SEQS}"
  printf 'configured_max_model_len=%s\n' "${MAX_MODEL_LEN}"
  printf 'configured_gpu_memory_utilization=%s\n' "${GPU_MEMORY_UTILIZATION}"
  printf 'safe_context_limit=%s\n' "${SAFE_CONTEXT_LIMIT}"
} > "${OUT_DIR}/forum53_context_safety.txt"

if [[ "${GB10_FORUM53_SKIP_CONTEXT_GUARD}" != "1" \
    && "${GB10_FORUM53_SKIP_CONTEXT_GUARD}" != "true" \
    && "${MAX_MODEL_LEN}" -gt "${SAFE_CONTEXT_LIMIT}" ]]; then
  {
    printf 'unsafe GB10 forum53 profile: max_model_len=%s exceeds safe limit %s for max_num_seqs=%s\n' \
      "${MAX_MODEL_LEN}" "${SAFE_CONTEXT_LIMIT}" "${MAX_NUM_SEQS}"
    printf 'safe_total_kv_tokens=%s, safety_percent=%s\n' \
      "${GB10_FORUM53_SAFE_TOTAL_KV_TOKENS}" \
      "${GB10_FORUM53_CONTEXT_SAFETY_PERCENT}"
    printf 'Override only for deliberate destructive pressure with GB10_FORUM53_SKIP_CONTEXT_GUARD=1.\n'
    printf 'Safe context table written to %s/forum53_context_safety.csv\n' \
      "${OUT_DIR}"
  } >&2
  exit 2
fi

failures=0
IFS=',' read -r -a variants <<< "${GB10_FORUM53_VARIANTS}"
IFS=',' read -r -a batched_tokens_values <<< "${GB10_FORUM53_BATCHED_TOKEN_SWEEP}"
for variant in "${variants[@]}"; do
  variant="$(printf '%s' "${variant}" | xargs)"
  if [[ -z "${variant}" ]]; then
    continue
  fi
  speculative_config="$(variant_speculative_config "${variant}")" || exit 2

  for max_batched_tokens in "${batched_tokens_values[@]}"; do
    max_batched_tokens="$(printf '%s' "${max_batched_tokens}" | xargs)"
    if [[ -z "${max_batched_tokens}" ]]; then
      continue
    fi
    if ! [[ "${max_batched_tokens}" =~ ^[0-9]+$ ]]; then
      printf 'invalid max_num_batched_tokens: %s\n' "${max_batched_tokens}" >&2
      exit 2
    fi

    sweep_name="${variant}_mbt${max_batched_tokens}"
    variant_dir="${OUT_DIR}/${sweep_name}"
    remote_variant_root="${REMOTE_RUN_ROOT}/${sweep_name}"
    remote_serve_dir="${remote_variant_root}/serve"
    remote_matrix_dir="${remote_variant_root}/streaming_pressure_forum53"
    scheduler_trace_path="${remote_serve_dir}/scheduler_trace.jsonl"
    VLLM_SCHEDULER_TRACE_PATH="${scheduler_trace_path}"
    serve_remote_env_vars="${SERVE_REMOTE_ENV_VARS:-}"
    serve_remote_env_vars="$(
      append_env_allowlist \
        "${serve_remote_env_vars}" \
        VLLM_DEEPSEEK_V4_INDEXED_D512_SPLIT_PREFILL_MIN_TOKENS \
        VLLM_DEEPSEEK_V4_INDEXED_D512_CHUNKED_PREFILL
    )"
    serve_remote_env_vars="$(
      append_env_allowlist \
        "${serve_remote_env_vars}" \
        VLLM_SCHEDULER_TRACE_PATH
    )"
    if [[ "${GB10_FORUM53_D512_MULTI_PREFILL_ENV}" != "default" ]]; then
      serve_remote_env_vars="$(
        append_env_allowlist \
          "${serve_remote_env_vars}" \
          VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL
      )"
    fi

    mkdir -p "${variant_dir}"
    printf '%s\n' "${remote_variant_root}" > "${variant_dir}/remote_variant_root.txt"
    printf '%s\n' "${remote_matrix_dir}" > "${variant_dir}/remote_streaming_pressure_dir.txt"
    printf '%s\n' "${variant}" > "${variant_dir}/variant.txt"
    printf '%s\n' "${max_batched_tokens}" > "${variant_dir}/max_num_batched_tokens.txt"

    stop_remote_vllm "${WORKER_HOST}"
    stop_remote_vllm "${HEAD_HOST}"

    set +e
    env \
      HEAD_HOST="${HEAD_HOST}" \
      WORKER_HOST="${WORKER_HOST}" \
      HEAD_ROCE_IP="${HEAD_ROCE_IP}" \
      WORKER_ROCE_IP="${WORKER_ROCE_IP}" \
      ROCE_IFACE="${ROCE_IFACE}" \
      NCCL_IB_HCA="${NCCL_IB_HCA}" \
      VLLM_ROOT="${VLLM_ROOT}" \
      VLLM_VENV="${VLLM_VENV}" \
      MODEL_ID="${MODEL_ID}" \
      TP_SIZE="${TP_SIZE}" \
      PP_SIZE="${PP_SIZE}" \
      MAX_MODEL_LEN="${MAX_MODEL_LEN}" \
      GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION}" \
      MAX_NUM_SEQS="${MAX_NUM_SEQS}" \
      MAX_NUM_BATCHED_TOKENS="${max_batched_tokens}" \
      BLOCK_SIZE="${BLOCK_SIZE}" \
      KV_CACHE_DTYPE="${KV_CACHE_DTYPE}" \
      MIN_AVAILABLE_MEM_GIB="${MIN_AVAILABLE_MEM_GIB}" \
      API_PORT="${API_PORT}" \
      RUN_DIR="${remote_serve_dir}" \
      PREWARM_AFTER_HEALTH=0 \
      SERVE_ENABLE_EXPERT_PARALLEL="${gb10_forum53_enable_expert_parallel}" \
      SERVE_PREFIX_CACHE_MODE=enabled \
      SERVE_SPECULATIVE_CONFIG="${speculative_config}" \
      SERVE_COMPILATION_CONFIG="${SERVE_COMPILATION_CONFIG}" \
      SERVE_REMOTE_ENV_VARS="${serve_remote_env_vars}" \
      VLLM_SCHEDULER_TRACE_PATH="${scheduler_trace_path}" \
      VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL="${GB10_FORUM53_D512_MULTI_PREFILL_ENV}" \
      SSH_OPTS="${SSH_OPTS:-}" \
      /bin/bash "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" \
        > "${variant_dir}/serve_start.stdout.log" \
        2> "${variant_dir}/serve_start.stderr.log"
    start_code="$?"
    set -e
    printf '%s\n' "${start_code}" > "${variant_dir}/serve_start.exit_code"

    matrix_code=125
    if [[ "${start_code}" == "0" ]]; then
      set +e
      run_remote_streaming_matrix \
        "${remote_matrix_dir}" \
        "${variant}" \
        "${max_batched_tokens}" \
        > "${variant_dir}/streaming_pressure.stdout.log" \
        2> "${variant_dir}/streaming_pressure.stderr.log"
      matrix_code="$?"
      set -e
    fi
    printf '%s\n' "${matrix_code}" > "${variant_dir}/streaming_pressure.exit_code"

    for name in \
        streaming_pressure_matrix.json \
        streaming_pressure_matrix.md \
        runtime_stats_summary.json \
        gpu_stats_summary.json \
        server_unresponsive.json; do
      fetch_remote_file "${remote_matrix_dir}/${name}" "${variant_dir}/${name}"
    done
    fetch_remote_file "${scheduler_trace_path}" \
      "${variant_dir}/scheduler_trace.jsonl"
    if [[ -s "${variant_dir}/scheduler_trace.jsonl" ]]; then
      "${LOCAL_PYTHON:-python3}" "${SCRIPT_DIR}/analyze_scheduler_trace.py" \
        "${variant_dir}/scheduler_trace.jsonl" \
        --json-output "${variant_dir}/scheduler_trace_summary.json" \
        --markdown-output "${variant_dir}/scheduler_trace_summary.md"
    fi

    stop_remote_vllm "${WORKER_HOST}"
    stop_remote_vllm "${HEAD_HOST}"

    if [[ "${start_code}" != "0" || "${matrix_code}" != "0" ]]; then
      failures=1
    fi
  done
done

driver_health_dir="${OUT_DIR}/driver_health"
capture_remote_driver_health "${HEAD_HOST}" head "${driver_health_dir}"
capture_remote_driver_health "${WORKER_HOST}" worker "${driver_health_dir}"

driver_health_signal_count=0
driver_health_allowlisted_count=0
for signal_file in \
    "${driver_health_dir}/head/kernel_gpu_signals.log" \
    "${driver_health_dir}/worker/kernel_gpu_signals.log"; do
  if [[ -s "${signal_file}" ]]; then
    file_total="$(wc -l < "${signal_file}" | tr -d '[:space:]')"
    if [[ -n "${GB10_FORUM53_DRIVER_SIGNAL_ALLOWLIST}" ]]; then
      # count only signals NOT on the benign allowlist toward the fail count
      file_fail="$(grep -cvE "${GB10_FORUM53_DRIVER_SIGNAL_ALLOWLIST}" "${signal_file}" 2>/dev/null | tr -d '[:space:]')"
      [[ -z "${file_fail}" ]] && file_fail=0
    else
      file_fail="${file_total}"
    fi
    driver_health_signal_count="$((driver_health_signal_count + file_fail))"
    driver_health_allowlisted_count="$((driver_health_allowlisted_count + file_total - file_fail))"
  fi
done

if [[ "${driver_health_signal_count}" == "0" \
    || "${GB10_FORUM53_ALLOW_DRIVER_SIGNALS}" == "1" ]]; then
  driver_health_ok=1
else
  driver_health_ok=0
  failures=1
fi

DRIVER_HEALTH_ROOT="${driver_health_dir}" \
DRIVER_HEALTH_OK="${driver_health_ok}" \
DRIVER_HEALTH_SIGNAL_COUNT="${driver_health_signal_count}" \
DRIVER_HEALTH_ALLOWLISTED="${driver_health_allowlisted_count}" \
DRIVER_HEALTH_ALLOWLIST_PATTERN="${GB10_FORUM53_DRIVER_SIGNAL_ALLOWLIST}" \
DRIVER_HEALTH_ALLOW="${GB10_FORUM53_ALLOW_DRIVER_SIGNALS}" \
LOCAL_PYTHON="${LOCAL_PYTHON:-python3}" \
"${LOCAL_PYTHON:-python3}" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path


root = Path(os.environ["DRIVER_HEALTH_ROOT"])
hosts = {}
for label in ("head", "worker"):
    signal_path = root / label / "kernel_gpu_signals.log"
    text = ""
    if signal_path.exists():
        text = signal_path.read_text(encoding="utf-8", errors="replace")
    lines = [line for line in text.splitlines() if line.strip()]
    hosts[label] = {
        "signal_count": len(lines),
        "signals_path": str(signal_path),
        "has_signals": bool(lines),
    }

payload = {
    "ok": os.environ["DRIVER_HEALTH_OK"] == "1",
    "allow_driver_signals": os.environ["DRIVER_HEALTH_ALLOW"] == "1",
    # signal_count = signals that COUNT toward fail (allowlisted ones excluded)
    "signal_count": int(os.environ["DRIVER_HEALTH_SIGNAL_COUNT"]),
    # allowlisted_signal_count = known-benign signals seen but NOT failing the gate
    # (default: NCCL 2.30.7 init cuMem OOM -- see driver_signal_allowlist)
    "allowlisted_signal_count": int(os.environ.get("DRIVER_HEALTH_ALLOWLISTED", "0")),
    "driver_signal_allowlist": os.environ.get("DRIVER_HEALTH_ALLOWLIST_PATTERN", ""),
    "hosts": hosts,
}
(root.parent / "driver_health_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

SUMMARY_ROOT="${OUT_DIR}" \
SUMMARY_PROFILE="${GB10_FORUM53_PROFILE}" \
SUMMARY_EXPERT_PARALLEL_ENABLED="${gb10_forum53_enable_expert_parallel}" \
SUMMARY_TP_SIZE="${TP_SIZE}" \
SUMMARY_PP_SIZE="${PP_SIZE}" \
SUMMARY_MAX_MODEL_LEN="${MAX_MODEL_LEN}" \
SUMMARY_MAX_NUM_SEQS="${MAX_NUM_SEQS}" \
SUMMARY_GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION}" \
SUMMARY_BLOCK_SIZE="${BLOCK_SIZE}" \
SUMMARY_KV_CACHE_DTYPE="${KV_CACHE_DTYPE}" \
SUMMARY_D512_MULTI_PREFILL_ENV="${GB10_FORUM53_D512_MULTI_PREFILL_ENV}" \
SUMMARY_SAFE_TOTAL_KV_TOKENS="${GB10_FORUM53_SAFE_TOTAL_KV_TOKENS}" \
SUMMARY_CONTEXT_SAFETY_PERCENT="${GB10_FORUM53_CONTEXT_SAFETY_PERCENT}" \
SUMMARY_SAFE_CONTEXT_LIMIT="${SAFE_CONTEXT_LIMIT}" \
SUMMARY_PREFIX_CACHE="enabled" \
SUMMARY_CASE_SPECS="${GB10_FORUM53_CASE_SPECS}" \
LOCAL_PYTHON="${LOCAL_PYTHON:-python3}" \
"${LOCAL_PYTHON:-python3}" - <<'PY'
from __future__ import annotations

import json
import os
from pathlib import Path


def read_text(path: Path) -> str | None:
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return None


def read_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


root = Path(os.environ["SUMMARY_ROOT"])
driver_health = {}
driver_health_path = root / "driver_health_summary.json"
if driver_health_path.exists():
    driver_health = json.loads(driver_health_path.read_text(encoding="utf-8"))
rows = []
for variant_dir in sorted(path for path in root.iterdir() if path.is_dir()):
    if variant_dir.name == "driver_health":
        continue
    variant = read_text(variant_dir / "variant.txt") or variant_dir.name
    max_batched_tokens = read_text(variant_dir / "max_num_batched_tokens.txt")
    matrix = read_json(variant_dir / "streaming_pressure_matrix.json")
    runtime = read_json(variant_dir / "runtime_stats_summary.json")
    scheduler_trace = read_json(variant_dir / "scheduler_trace_summary.json")
    runtime_metrics = runtime.get("metrics", {}) if isinstance(runtime, dict) else {}
    summary = matrix.get("summary", {}) if isinstance(matrix, dict) else {}
    row = {
        "variant": variant,
        "max_num_batched_tokens": (
            int(max_batched_tokens) if max_batched_tokens else None
        ),
        "serve_start_exit_code": read_text(variant_dir / "serve_start.exit_code"),
        "streaming_pressure_exit_code": read_text(
            variant_dir / "streaming_pressure.exit_code"
        ),
        "remote_variant_root": read_text(variant_dir / "remote_variant_root.txt"),
        "ok": matrix.get("ok") if isinstance(matrix, dict) else None,
        "summary": summary,
        "runtime_metrics": {
            name: runtime_metrics.get(name)
            for name in (
                "running_requests_max",
                "running_requests_avg",
                "waiting_requests_max",
                "waiting_requests_avg",
                "gpu_kv_cache_usage_percent_max",
                "gpu_kv_cache_usage_percent_avg",
                "prefix_cache_queries_delta",
                "prefix_cache_hits_delta",
                "preemptions_delta",
            )
        },
        "scheduler_trace_summary": scheduler_trace,
    }
    rows.append(row)

payload = {
    "ok": all(
        row.get("serve_start_exit_code") == "0"
        and row.get("streaming_pressure_exit_code") == "0"
        and row.get("ok") is not False
        for row in rows
    ) and driver_health.get("ok", True),
    "expert_parallel_enabled": os.environ["SUMMARY_EXPERT_PARALLEL_ENABLED"],
    "driver_health": driver_health,
    "profile": {
        "name": os.environ["SUMMARY_PROFILE"],
        "tensor_parallel_size": int(os.environ["SUMMARY_TP_SIZE"]),
        "pipeline_parallel_size": int(os.environ["SUMMARY_PP_SIZE"]),
        "max_model_len": int(os.environ["SUMMARY_MAX_MODEL_LEN"]),
        "max_num_seqs": int(os.environ["SUMMARY_MAX_NUM_SEQS"]),
        "gpu_memory_utilization": os.environ["SUMMARY_GPU_MEMORY_UTILIZATION"],
        "block_size": int(os.environ["SUMMARY_BLOCK_SIZE"]),
        "kv_cache_dtype": os.environ["SUMMARY_KV_CACHE_DTYPE"],
        "prefix_cache": os.environ["SUMMARY_PREFIX_CACHE"],
        "d512_multi_prefill_env": os.environ["SUMMARY_D512_MULTI_PREFILL_ENV"],
        "case_specs": os.environ["SUMMARY_CASE_SPECS"],
        "safe_total_kv_tokens": int(os.environ["SUMMARY_SAFE_TOTAL_KV_TOKENS"]),
        "context_safety_percent": int(
            os.environ["SUMMARY_CONTEXT_SAFETY_PERCENT"]
        ),
        "safe_context_limit": int(os.environ["SUMMARY_SAFE_CONTEXT_LIMIT"]),
        "batched_token_sweep": sorted(
            {
                row["max_num_batched_tokens"]
                for row in rows
                if row["max_num_batched_tokens"] is not None
            }
        ),
    },
    "runs": rows,
}
(root / "gb10_forum53_multi_user_gate_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

lines = [
    "# GB10 Forum #53 Multi-User Prefix-Cache Gate",
    "",
    f"- OK: `{payload['ok']}`",
    f"- Expert parallel enabled: `{payload['expert_parallel_enabled']}`",
    f"- Driver health OK: `{payload['driver_health'].get('ok', True)}`",
    f"- Driver signal count: `{payload['driver_health'].get('signal_count', 0)}`",
    "- Profile `{}`: `TP={}`, `PP={}`, `max_model_len={}`, `max_num_seqs={}`, "
    "`gpu_memory_utilization={}`, KV `{}`, block size `{}`, prefix cache `{}`.".format(
        payload["profile"]["name"],
        payload["profile"]["tensor_parallel_size"],
        payload["profile"]["pipeline_parallel_size"],
        payload["profile"]["max_model_len"],
        payload["profile"]["max_num_seqs"],
        payload["profile"]["gpu_memory_utilization"],
        payload["profile"]["kv_cache_dtype"],
        payload["profile"]["block_size"],
        payload["profile"]["prefix_cache"],
    ),
    "- Safe context limit: `{}` tokens (`{}%` of `{}` observed KV tokens / `max_num_seqs`).".format(
        payload["profile"]["safe_context_limit"],
        payload["profile"]["context_safety_percent"],
        payload["profile"]["safe_total_kv_tokens"],
    ),
    f"- Case specs: `{payload['profile']['case_specs']}`",
    "",
    "| Variant | max_num_batched_tokens | Serve exit | Matrix exit | Requests | Failures | Max TTFT s | ITL P99 s | running max | waiting max | Trace events | Max scheduled tokens | Prefix hits | Preemptions | Remote artifact |",
    "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
]
for row in rows:
    summary = row.get("summary") or {}
    runtime_metrics = row.get("runtime_metrics") or {}
    scheduler_trace = row.get("scheduler_trace_summary") or {}
    lines.append(
        "| {variant} | {mbt} | {serve} | {matrix} | {requests} | {failures} | {ttft} | {p99} | {running} | {waiting} | {trace_events} | {max_sched} | {prefix_hits} | {preemptions} | `{remote}` |".format(
            variant=row.get("variant"),
            mbt=row.get("max_num_batched_tokens"),
            serve=row.get("serve_start_exit_code"),
            matrix=row.get("streaming_pressure_exit_code"),
            requests=summary.get("request_count", ""),
            failures=summary.get("failure_count", ""),
            ttft=summary.get("max_ttft_seconds", ""),
            p99=summary.get("p99_inter_chunk_seconds", ""),
            running=runtime_metrics.get("running_requests_max", ""),
            waiting=runtime_metrics.get("waiting_requests_max", ""),
            trace_events=scheduler_trace.get("event_count", ""),
            max_sched=scheduler_trace.get("total_scheduled_tokens_max", ""),
            prefix_hits=runtime_metrics.get("prefix_cache_hits_delta", ""),
            preemptions=runtime_metrics.get("preemptions_delta", ""),
            remote=row.get("remote_variant_root", ""),
        )
    )
if not payload["driver_health"].get("ok", True):
    lines.extend(["", "## Driver Health", ""])
    for label, host in payload["driver_health"].get("hosts", {}).items():
        lines.append(
            f"- `{label}`: {host.get('signal_count', 0)} signal(s), "
            f"`{host.get('signals_path', '')}`"
        )
(root / "gb10_forum53_multi_user_gate_summary.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)
PY

echo "wrote ${OUT_DIR}"
exit "${failures}"
