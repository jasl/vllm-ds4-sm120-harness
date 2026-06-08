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

BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-2x_gb10_sm121}"
GB10_DECODE_LABEL="${GB10_DECODE_LABEL:-gb10_decode_throughput_probe}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${GB10_DECODE_LABEL}/${RUN_TIMESTAMP}}"
REMOTE_HARNESS_ROOT="${GB10_DECODE_REMOTE_HARNESS_ROOT:-$(dirname -- "${VLLM_ROOT}")}"
REMOTE_RUN_ROOT="${GB10_DECODE_REMOTE_RUN_ROOT:-${REMOTE_HARNESS_ROOT}/artifacts/${GB10_DECODE_LABEL}/${RUN_TIMESTAMP}}"

MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
API_PORT="${API_PORT:-8000}"
TP_SIZE="${GB10_DECODE_TP_SIZE:-2}"
PP_SIZE="${GB10_DECODE_PP_SIZE:-1}"
GB10_DECODE_ENABLE_MTP="${GB10_DECODE_ENABLE_MTP:-0}"
GB10_DECODE_PREFIX_CACHE_MODE="${GB10_DECODE_PREFIX_CACHE_MODE:-disabled}"
MAX_MODEL_LEN="${GB10_DECODE_MAX_MODEL_LEN:-32768}"
GPU_MEMORY_UTILIZATION="${GB10_DECODE_GPU_MEMORY_UTILIZATION:-0.55}"
MAX_NUM_SEQS="${GB10_DECODE_MAX_NUM_SEQS:-1}"
MAX_NUM_BATCHED_TOKENS="${GB10_DECODE_MAX_NUM_BATCHED_TOKENS:-1024}"
BLOCK_SIZE="${GB10_DECODE_BLOCK_SIZE:-256}"
KV_CACHE_DTYPE="${GB10_DECODE_KV_CACHE_DTYPE:-fp8}"
MIN_AVAILABLE_MEM_GIB="${GB10_DECODE_MIN_AVAILABLE_MEM_GIB:-64}"
SERVE_COMPILATION_CONFIG="${GB10_DECODE_COMPILATION_CONFIG:-{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}}"
# Default speculative config: {"method":"mtp","num_speculative_tokens":2}
MTP2_SPECULATIVE_CONFIG="{\"method\":\"mtp\",\"num_speculative_tokens\":2}"
SERVE_SPECULATIVE_CONFIG="${GB10_DECODE_SPECULATIVE_CONFIG:-}"
PROBE_VARIANT="${GB10_DECODE_VARIANT:-nomtp}"
if [[ "${GB10_DECODE_ENABLE_MTP}" == "1" ]]; then
  SERVE_SPECULATIVE_CONFIG="${GB10_DECODE_SPECULATIVE_CONFIG:-${MTP2_SPECULATIVE_CONFIG}}"
  PROBE_VARIANT="${GB10_DECODE_VARIANT:-mtp2}"
fi
DECODE_THROUGHPUT_SERIES_SPECS="${GB10_DECODE_SERIES_SPECS:-cycle3_temp1:cycle3:1.0:3}"
DECODE_THROUGHPUT_SLOW_TOK_S_THRESHOLD="${GB10_DECODE_SLOW_TOK_S_THRESHOLD:-0}"
DECODE_THROUGHPUT_MAX_TOKENS="${GB10_DECODE_MAX_TOKENS:-512}"
DECODE_THROUGHPUT_TIMEOUT="${GB10_DECODE_TIMEOUT:-300}"
SERVER_STARTUP_TIMEOUT="${GB10_DECODE_SERVER_STARTUP_TIMEOUT:-600}"

mkdir -p "${OUT_DIR}"
printf '%s\n' "${REMOTE_RUN_ROOT}" > "${OUT_DIR}/remote_run_root.txt"

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
  MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS}" \
  BLOCK_SIZE="${BLOCK_SIZE}" \
  KV_CACHE_DTYPE="${KV_CACHE_DTYPE}" \
  MIN_AVAILABLE_MEM_GIB="${MIN_AVAILABLE_MEM_GIB}" \
  API_PORT="${API_PORT}" \
  RUN_DIR="${REMOTE_RUN_ROOT}/serve" \
  PREWARM_AFTER_HEALTH=0 \
  SERVE_ENABLE_EXPERT_PARALLEL=1 \
  SERVE_PREFIX_CACHE_MODE="${GB10_DECODE_PREFIX_CACHE_MODE}" \
  SERVE_SPECULATIVE_CONFIG="${SERVE_SPECULATIVE_CONFIG}" \
  SERVE_COMPILATION_CONFIG="${SERVE_COMPILATION_CONFIG}" \
  SSH_OPTS="${SSH_OPTS:-}" \
  "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" \
    > "${OUT_DIR}/serve_start.stdout.log" \
    2> "${OUT_DIR}/serve_start.stderr.log"
start_code="$?"
set -e
printf '%s\n' "${start_code}" > "${OUT_DIR}/serve_start.exit_code"

probe_code=125
remote_probe_dir="${REMOTE_RUN_ROOT}/decode_throughput_probe"
if [[ "${start_code}" == "0" ]]; then
  set +e
  run_remote "${HEAD_HOST}" \
    "cd $(shell_quote "${REMOTE_HARNESS_ROOT}") && env \
      PYTHON=$(shell_quote "${VLLM_VENV}/bin/python") \
      BASE_URL=$(shell_quote "http://127.0.0.1:${API_PORT}") \
      MODEL=$(shell_quote "${MODEL_ID}") \
      GPU_TOPOLOGY_SLUG=$(shell_quote "${GPU_TOPOLOGY_SLUG}") \
      BRANCH_NAME=$(shell_quote "${BRANCH_NAME}") \
      OUT_DIR=$(shell_quote "${remote_probe_dir}") \
      DECODE_THROUGHPUT_VARIANT=$(shell_quote "${PROBE_VARIANT}") \
      DECODE_THROUGHPUT_CASE_NAME=gb10_decode_throughput_user_report \
      DECODE_THROUGHPUT_SERIES_SPECS=$(shell_quote "${DECODE_THROUGHPUT_SERIES_SPECS}") \
      DECODE_THROUGHPUT_MAX_TOKENS=$(shell_quote "${DECODE_THROUGHPUT_MAX_TOKENS}") \
      DECODE_THROUGHPUT_TIMEOUT=$(shell_quote "${DECODE_THROUGHPUT_TIMEOUT}") \
      DECODE_THROUGHPUT_SLOW_TOK_S_THRESHOLD=$(shell_quote "${DECODE_THROUGHPUT_SLOW_TOK_S_THRESHOLD}") \
      SERVER_STARTUP_TIMEOUT=$(shell_quote "${SERVER_STARTUP_TIMEOUT}") \
      $(shell_quote "${REMOTE_HARNESS_ROOT}/scripts/run_decode_throughput_probe.sh")" \
      > "${OUT_DIR}/decode_throughput_probe.stdout.log" \
      2> "${OUT_DIR}/decode_throughput_probe.stderr.log"
  probe_code="$?"
  set -e
fi
printf '%s\n' "${probe_code}" > "${OUT_DIR}/decode_throughput_probe.exit_code"

for name in \
    decode_throughput_probe.json \
    decode_throughput_probe.md \
    runtime_stats_summary.json \
    gpu_stats_summary.json \
    server_unresponsive.json; do
  fetch_remote_file "${remote_probe_dir}/${name}" "${OUT_DIR}/${name}"
done
fetch_remote_file "${REMOTE_RUN_ROOT}/serve/head.log" "${OUT_DIR}/serve_head.log"

stop_remote_vllm "${WORKER_HOST}"
stop_remote_vllm "${HEAD_HOST}"

SUMMARY_ROOT="${OUT_DIR}" \
SUMMARY_MAX_MODEL_LEN="${MAX_MODEL_LEN}" \
SUMMARY_MAX_NUM_SEQS="${MAX_NUM_SEQS}" \
SUMMARY_MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS}" \
SUMMARY_SPECULATIVE_CONFIG="${SERVE_SPECULATIVE_CONFIG}" \
LOCAL_PYTHON="${LOCAL_PYTHON:-python3}" \
"${LOCAL_PYTHON:-python3}" - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["SUMMARY_ROOT"])
probe = {}
probe_path = root / "decode_throughput_probe.json"
if probe_path.exists():
    probe = json.loads(probe_path.read_text(encoding="utf-8"))

payload = {
    "ok": (
        (root / "serve_start.exit_code").read_text(encoding="utf-8").strip() == "0"
        and (root / "decode_throughput_probe.exit_code").read_text(
            encoding="utf-8"
        ).strip()
        == "0"
        and probe.get("ok") is not False
    ),
    "profile": {
        "max_model_len": int(os.environ["SUMMARY_MAX_MODEL_LEN"]),
        "max_num_seqs": int(os.environ["SUMMARY_MAX_NUM_SEQS"]),
        "max_num_batched_tokens": int(os.environ["SUMMARY_MAX_NUM_BATCHED_TOKENS"]),
        "speculative_config": os.environ["SUMMARY_SPECULATIVE_CONFIG"],
    },
    "probe_summary": probe.get("summary", {}),
}
(root / "gb10_decode_throughput_probe_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

echo "wrote ${OUT_DIR}"
if [[ "${start_code}" == "0" && "${probe_code}" == "0" ]]; then
  exit 0
fi
exit 1
