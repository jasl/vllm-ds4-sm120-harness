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

metric_sum() {
  local metrics_file="$1"
  local pattern="$2"
  awk -v re="${pattern}" '
    /^[[:space:]]*#/ { next }
    NF >= 2 {
      name = $1
      sub(/\{.*/, "", name)
      if (name ~ re) {
        sum += $2
      }
    }
    END { printf "%.0f", sum + 0 }
  ' "${metrics_file}"
}

metric_max() {
  local metrics_file="$1"
  local pattern="$2"
  awk -v re="${pattern}" '
    /^[[:space:]]*#/ { next }
    NF >= 2 {
      name = $1
      sub(/\{.*/, "", name)
      if (name ~ re && $2 > max) {
        max = $2
      }
    }
    END { printf "%.0f", max + 0 }
  ' "${metrics_file}"
}

capture_remote_debug_bundle() {
  local host="$1"
  local label="$2"
  local out_dir="$3"
  local host_dir="${out_dir}/${label}"

  mkdir -p "${host_dir}"
  run_remote "${host}" \
    "date -Ins; hostname; uname -a; uptime; ps -eo pid,ppid,stat,comm,args | grep -E '[v]llm|[p]ython|[r]ay|VLLM::' || true" \
    > "${host_dir}/processes.txt" 2>&1 || true
  run_remote "${host}" \
    "nvidia-smi; nvidia-smi pmon -c 1 || true" \
    > "${host_dir}/nvidia_smi.txt" 2>&1 || true
  run_remote "${host}" \
    "journalctl -b -k --no-pager | grep -Ei 'NVRM|Xid|UVM|lost from the bus|fallen off|NV_ERR' | tail -n 200 || true" \
    > "${host_dir}/kernel_gpu_tail.txt" 2>&1 || true
  run_remote "${host}" \
    "if command -v py-spy >/dev/null 2>&1; then for pid in \$(pgrep -f '[v]llm.entrypoints.cli.main|[p]ython.*vllm|VLLM::' || true); do echo '===== py-spy pid' \"\$pid\" '====='; timeout 45 py-spy dump --native --threads -p \"\$pid\" || true; done; else echo 'py-spy not found'; fi" \
    > "${host_dir}/py_spy_dump.txt" 2>&1 || true
  run_remote "${host}" \
    "if command -v gdb >/dev/null 2>&1; then for pid in \$(pgrep -f '[v]llm.entrypoints.cli.main|[p]ython.*vllm|VLLM::' || true); do echo '===== gdb pid' \"\$pid\" '====='; timeout 45 gdb -batch -ex 'thread apply all bt' -p \"\$pid\" || true; done; else echo 'gdb not found'; fi" \
    > "${host_dir}/gdb_bt.txt" 2>&1 || true
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

watchdog_no_progress_loop() {
  local out_dir="$1"
  local stop_file="${out_dir}/watchdog.stop"
  local no_progress_file="${out_dir}/no_progress_detected.txt"
  local metrics_file="${out_dir}/metrics_poll.prom"
  local rows_file="${out_dir}/metrics_poll.jsonl"
  local last_decode_tokens=""
  local last_progress_ts
  last_progress_ts="$(date +%s)"

  mkdir -p "${out_dir}"
  : > "${rows_file}"
  while [[ ! -f "${stop_file}" ]]; do
    local snapshot="${out_dir}/metrics_snapshot.prom"
    local now decode_tokens running_requests waiting_requests idle_seconds
    now="$(date +%s)"
    if run_remote "${HEAD_HOST}" \
        "curl -fsS --max-time 5 http://127.0.0.1:${API_PORT}/metrics" \
        > "${snapshot}" 2> "${out_dir}/metrics_poll.err"; then
      {
        printf '# DS4_HARNESS_WATCHDOG_SNAPSHOT %s\n' "$(date -Ins)"
        cat "${snapshot}"
      } >> "${metrics_file}"
      decode_tokens="$(
        metric_sum "${snapshot}" \
          'generation_tokens_total|decode_tokens_total'
      )"
      running_requests="$(
        metric_max "${snapshot}" \
          'num_requests_running|requests_running'
      )"
      waiting_requests="$(
        metric_max "${snapshot}" \
          'num_requests_waiting|requests_waiting'
      )"
      if [[ "${running_requests}" == "0" ]]; then
        last_progress_ts="${now}"
        last_decode_tokens="${decode_tokens}"
      elif [[ "${decode_tokens}" != "${last_decode_tokens}" ]]; then
        last_progress_ts="${now}"
        last_decode_tokens="${decode_tokens}"
      fi
      idle_seconds="$(( now - last_progress_ts ))"
      printf '{"ts":%s,"decode_tokens":%s,"running_requests":%s,"waiting_requests":%s,"idle_seconds":%s}\n' \
        "${now}" "${decode_tokens}" "${running_requests}" "${waiting_requests}" \
        "${idle_seconds}" >> "${rows_file}"
      if [[ "${running_requests}" != "0" ]] \
          && (( idle_seconds >= GB10_MTP2_MOE_NO_PROGRESS_SECONDS )); then
        {
          printf 'no token progress for %ss with running_requests=%s waiting_requests=%s decode_tokens=%s\n' \
            "${idle_seconds}" "${running_requests}" "${waiting_requests}" \
            "${decode_tokens}"
          date -Ins
        } > "${no_progress_file}"
        capture_remote_debug_bundle "${HEAD_HOST}" head "${out_dir}/debug"
        capture_remote_debug_bundle "${WORKER_HOST}" worker "${out_dir}/debug"
        if [[ "${GB10_MTP2_MOE_ABORT_ON_NO_PROGRESS}" == "1" \
            || "${GB10_MTP2_MOE_ABORT_ON_NO_PROGRESS}" == "true" ]]; then
          stop_remote_vllm "${WORKER_HOST}"
          stop_remote_vllm "${HEAD_HOST}"
        fi
        break
      fi
    else
      printf '{"ts":%s,"metrics_error":true}\n' "${now}" >> "${rows_file}"
    fi
    sleep "${GB10_MTP2_MOE_WATCHDOG_INTERVAL_SECONDS}"
  done
}

run_remote_streaming_soak() {
  local remote_out_dir="$1"

  run_remote "${HEAD_HOST}" \
    "cd $(shell_quote "${REMOTE_HARNESS_ROOT}") && env \
      PYTHON=$(shell_quote "${VLLM_VENV}/bin/python") \
      BASE_URL=$(shell_quote "http://127.0.0.1:${API_PORT}") \
      MODEL=$(shell_quote "${MODEL_ID}") \
      GPU_TOPOLOGY_SLUG=$(shell_quote "${GPU_TOPOLOGY_SLUG}") \
      BRANCH_NAME=$(shell_quote "${BRANCH_NAME}") \
      OUT_DIR=$(shell_quote "${remote_out_dir}") \
      STREAMING_PRESSURE_VARIANT=$(shell_quote "${GB10_MTP2_MOE_VARIANT}") \
      STREAMING_PRESSURE_CASE_NAME=$(shell_quote "${GB10_MTP2_MOE_CASE_NAME}") \
      STREAMING_PRESSURE_CONCURRENCY=$(shell_quote "${GB10_MTP2_MOE_CONCURRENCY}") \
      STREAMING_PRESSURE_ROUND_COUNT=$(shell_quote "${GB10_MTP2_MOE_ROUND_COUNT}") \
      STREAMING_PRESSURE_LINE_COUNT=$(shell_quote "${GB10_MTP2_MOE_LINE_COUNT}") \
      STREAMING_PRESSURE_MAX_TOKENS=$(shell_quote "${GB10_MTP2_MOE_MAX_TOKENS}") \
      STREAMING_PRESSURE_TEMPERATURE=$(shell_quote "${GB10_MTP2_MOE_TEMPERATURE}") \
      STREAMING_PRESSURE_TOP_P=$(shell_quote "${GB10_MTP2_MOE_TOP_P}") \
      STREAMING_PRESSURE_THINKING_MODE=$(shell_quote "${GB10_MTP2_MOE_THINKING_MODE}") \
      STREAMING_PRESSURE_TIMEOUT=$(shell_quote "${GB10_MTP2_MOE_TIMEOUT}") \
      STREAMING_PRESSURE_REQUEST_RETRIES=$(shell_quote "${GB10_MTP2_MOE_REQUEST_RETRIES}") \
      STREAMING_PRESSURE_MAX_TTFT_SECONDS=$(shell_quote "${GB10_MTP2_MOE_MAX_TTFT_SECONDS}") \
      STREAMING_PRESSURE_MAX_ELAPSED_SECONDS=$(shell_quote "${GB10_MTP2_MOE_MAX_ELAPSED_SECONDS}") \
      STREAMING_PRESSURE_FAIL_ON_SLOW=$(shell_quote "${GB10_MTP2_MOE_FAIL_ON_SLOW}") \
      SERVER_STARTUP_TIMEOUT=$(shell_quote "${GB10_MTP2_MOE_SERVER_STARTUP_TIMEOUT}") \
      $(shell_quote "${REMOTE_HARNESS_ROOT}/scripts/run_streaming_pressure_soak.sh")"
}

BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-2x_gb10_sm121}"
GB10_MTP2_MOE_LABEL="${GB10_MTP2_MOE_LABEL:-gb10_mtp2_moe_tp_deadlock_gate}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${GB10_MTP2_MOE_LABEL}/${RUN_TIMESTAMP}}"

REMOTE_HARNESS_ROOT="${GB10_MTP2_MOE_REMOTE_HARNESS_ROOT:-$(dirname -- "${VLLM_ROOT}")}"
REMOTE_RUN_ROOT="${GB10_MTP2_MOE_REMOTE_RUN_ROOT:-${REMOTE_HARNESS_ROOT}/artifacts/${GB10_MTP2_MOE_LABEL}/${RUN_TIMESTAMP}}"

GB10_MTP2_MOE_VARIANT="${GB10_MTP2_MOE_VARIANT:-mtp2}"
GB10_MTP2_MOE_CASE_NAME="${GB10_MTP2_MOE_CASE_NAME:-gb10_mtp2_moe_tp_deadlock_sustained}"
GB10_MTP2_MOE_CONCURRENCY="${GB10_MTP2_MOE_CONCURRENCY:-8}"
GB10_MTP2_MOE_ROUND_COUNT="${GB10_MTP2_MOE_ROUND_COUNT:-16}"
GB10_MTP2_MOE_LINE_COUNT="${GB10_MTP2_MOE_LINE_COUNT:-1600}"
GB10_MTP2_MOE_MAX_TOKENS="${GB10_MTP2_MOE_MAX_TOKENS:-128}"
GB10_MTP2_MOE_TEMPERATURE="${GB10_MTP2_MOE_TEMPERATURE:-1.0}"
GB10_MTP2_MOE_TOP_P="${GB10_MTP2_MOE_TOP_P:-1.0}"
GB10_MTP2_MOE_THINKING_MODE="${GB10_MTP2_MOE_THINKING_MODE:-non-thinking}"
GB10_MTP2_MOE_TIMEOUT="${GB10_MTP2_MOE_TIMEOUT:-5400}"
GB10_MTP2_MOE_REQUEST_RETRIES="${GB10_MTP2_MOE_REQUEST_RETRIES:-0}"
GB10_MTP2_MOE_MAX_TTFT_SECONDS="${GB10_MTP2_MOE_MAX_TTFT_SECONDS:-900}"
GB10_MTP2_MOE_MAX_ELAPSED_SECONDS="${GB10_MTP2_MOE_MAX_ELAPSED_SECONDS:-5400}"
GB10_MTP2_MOE_FAIL_ON_SLOW="${GB10_MTP2_MOE_FAIL_ON_SLOW:-0}"
GB10_MTP2_MOE_SERVER_STARTUP_TIMEOUT="${GB10_MTP2_MOE_SERVER_STARTUP_TIMEOUT:-60}"
GB10_MTP2_MOE_WATCHDOG_INTERVAL_SECONDS="${GB10_MTP2_MOE_WATCHDOG_INTERVAL_SECONDS:-15}"
GB10_MTP2_MOE_NO_PROGRESS_SECONDS="${GB10_MTP2_MOE_NO_PROGRESS_SECONDS:-600}"
GB10_MTP2_MOE_ABORT_ON_NO_PROGRESS="${GB10_MTP2_MOE_ABORT_ON_NO_PROGRESS:-1}"

MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
API_PORT="${API_PORT:-8000}"
TP_SIZE="${GB10_MTP2_MOE_TP_SIZE:-2}"
PP_SIZE="${GB10_MTP2_MOE_PP_SIZE:-1}"
MAX_MODEL_LEN="${GB10_MTP2_MOE_MAX_MODEL_LEN:-200000}"
GPU_MEMORY_UTILIZATION="${GB10_MTP2_MOE_GPU_MEMORY_UTILIZATION:-0.80}"
MAX_NUM_SEQS="${GB10_MTP2_MOE_MAX_NUM_SEQS:-8}"
MAX_NUM_BATCHED_TOKENS="${GB10_MTP2_MOE_MAX_NUM_BATCHED_TOKENS:-4096}"
BLOCK_SIZE="${GB10_MTP2_MOE_BLOCK_SIZE:-256}"
KV_CACHE_DTYPE="${GB10_MTP2_MOE_KV_CACHE_DTYPE:-fp8}"
MIN_AVAILABLE_MEM_GIB="${GB10_MTP2_MOE_MIN_AVAILABLE_MEM_GIB:-96}"
SERVE_COMPILATION_CONFIG="${GB10_MTP2_MOE_COMPILATION_CONFIG:-{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}}"
GB10_MTP2_MOE_SPEC_METHOD="${GB10_MTP2_MOE_SPEC_METHOD:-deepseek_mtp}"
if [[ "${GB10_MTP2_MOE_SPEC_METHOD}" == *[!A-Za-z0-9_:-]* ]]; then
  printf 'GB10_MTP2_MOE_SPEC_METHOD contains unsupported characters: %s\n' \
    "${GB10_MTP2_MOE_SPEC_METHOD}" >&2
  exit 2
fi
MTP2_SPECULATIVE_CONFIG="{\"method\":\"${GB10_MTP2_MOE_SPEC_METHOD}\",\"num_speculative_tokens\":2}"
SCHEDULER_TRACE_PATH="${REMOTE_RUN_ROOT}/serve/scheduler_trace.jsonl"
VLLM_SCHEDULER_TRACE_PATH="${SCHEDULER_TRACE_PATH}"

mkdir -p "${OUT_DIR}"
printf '%s\n' "${REMOTE_RUN_ROOT}" > "${OUT_DIR}/remote_run_root.txt"

serve_remote_env_vars="${SERVE_REMOTE_ENV_VARS:-}"
serve_remote_env_vars="$(
  append_env_allowlist \
    "${serve_remote_env_vars}" \
    VLLM_DEEPSEEK_V4_INDEXED_D512_CHUNKED_PREFILL
)"
serve_remote_env_vars="$(
  append_env_allowlist "${serve_remote_env_vars}" VLLM_SCHEDULER_TRACE_PATH
)"

remote_serve_dir="${REMOTE_RUN_ROOT}/serve"
remote_soak_dir="${REMOTE_RUN_ROOT}/streaming_pressure_soak"

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
  RUN_DIR="${remote_serve_dir}" \
  PREWARM_AFTER_HEALTH=0 \
  SERVE_ENABLE_EXPERT_PARALLEL=1 \
  SERVE_PREFIX_CACHE_MODE=enabled \
  SERVE_SPECULATIVE_CONFIG="${MTP2_SPECULATIVE_CONFIG}" \
  SERVE_COMPILATION_CONFIG="${SERVE_COMPILATION_CONFIG}" \
  SERVE_REMOTE_ENV_VARS="${serve_remote_env_vars}" \
  VLLM_SCHEDULER_TRACE_PATH="${VLLM_SCHEDULER_TRACE_PATH}" \
  NCCL_DEBUG="${NCCL_DEBUG:-WARN}" \
  NCCL_DEBUG_SUBSYS="${NCCL_DEBUG_SUBSYS:-}" \
  SSH_OPTS="${SSH_OPTS:-}" \
  "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" \
    > "${OUT_DIR}/serve_start.stdout.log" \
    2> "${OUT_DIR}/serve_start.stderr.log"
start_code="$?"
set -e
printf '%s\n' "${start_code}" > "${OUT_DIR}/serve_start.exit_code"

soak_code=125
watchdog_pid=""
if [[ "${start_code}" == "0" ]]; then
  watchdog_no_progress_loop "${OUT_DIR}/watchdog" &
  watchdog_pid="$!"
  set +e
  run_remote_streaming_soak "${remote_soak_dir}" \
    > "${OUT_DIR}/streaming_pressure_soak.stdout.log" \
    2> "${OUT_DIR}/streaming_pressure_soak.stderr.log"
  soak_code="$?"
  set -e
  touch "${OUT_DIR}/watchdog/watchdog.stop"
  if [[ -n "${watchdog_pid}" ]]; then
    wait "${watchdog_pid}" || true
  fi
fi
printf '%s\n' "${soak_code}" > "${OUT_DIR}/streaming_pressure_soak.exit_code"

for name in \
    streaming_pressure_soak.json \
    streaming_pressure_soak.md \
    runtime_stats_summary.json \
    gpu_stats_summary.json \
    server_unresponsive.json; do
  fetch_remote_file "${remote_soak_dir}/${name}" "${OUT_DIR}/${name}"
done
fetch_remote_file "${remote_serve_dir}/head.log" "${OUT_DIR}/head.log"
fetch_remote_file "${remote_serve_dir}/worker.log" "${OUT_DIR}/worker.log"
fetch_remote_file "${SCHEDULER_TRACE_PATH}" "${OUT_DIR}/scheduler_trace.jsonl"
if [[ -s "${OUT_DIR}/scheduler_trace.jsonl" ]]; then
  "${LOCAL_PYTHON:-python3}" "${SCRIPT_DIR}/analyze_scheduler_trace.py" \
    "${OUT_DIR}/scheduler_trace.jsonl" \
    --json-output "${OUT_DIR}/scheduler_trace_summary.json" \
    --markdown-output "${OUT_DIR}/scheduler_trace_summary.md"
fi

stop_remote_vllm "${WORKER_HOST}"
stop_remote_vllm "${HEAD_HOST}"

driver_health_dir="${OUT_DIR}/driver_health"
capture_remote_driver_health "${HEAD_HOST}" head "${driver_health_dir}"
capture_remote_driver_health "${WORKER_HOST}" worker "${driver_health_dir}"

driver_health_signal_count=0
for signal_file in \
    "${driver_health_dir}/head/kernel_gpu_signals.log" \
    "${driver_health_dir}/worker/kernel_gpu_signals.log"; do
  if [[ -s "${signal_file}" ]]; then
    file_count="$(wc -l < "${signal_file}" | tr -d '[:space:]')"
    driver_health_signal_count="$((driver_health_signal_count + file_count))"
  fi
done

GB10_MTP2_MOE_ALLOW_DRIVER_SIGNALS="${GB10_MTP2_MOE_ALLOW_DRIVER_SIGNALS:-0}"
if [[ "${driver_health_signal_count}" == "0" \
    || "${GB10_MTP2_MOE_ALLOW_DRIVER_SIGNALS}" == "1" ]]; then
  driver_health_ok=1
else
  driver_health_ok=0
fi
printf '%s\n' "${driver_health_ok}" > "${OUT_DIR}/driver_health.ok"
printf '%s\n' "${driver_health_signal_count}" \
  > "${OUT_DIR}/driver_health_signal_count.txt"

DRIVER_HEALTH_ROOT="${driver_health_dir}" \
DRIVER_HEALTH_OK="${driver_health_ok}" \
DRIVER_HEALTH_SIGNAL_COUNT="${driver_health_signal_count}" \
DRIVER_HEALTH_ALLOW="${GB10_MTP2_MOE_ALLOW_DRIVER_SIGNALS}" \
LOCAL_PYTHON="${LOCAL_PYTHON:-python3}" "${LOCAL_PYTHON:-python3}" - <<'PY'
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
    "signal_count": int(os.environ["DRIVER_HEALTH_SIGNAL_COUNT"]),
    "hosts": hosts,
}
(root.parent / "driver_health_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY

SUMMARY_ROOT="${OUT_DIR}" \
SUMMARY_MAX_MODEL_LEN="${MAX_MODEL_LEN}" \
SUMMARY_MAX_NUM_SEQS="${MAX_NUM_SEQS}" \
SUMMARY_MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS}" \
SUMMARY_GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION}" \
SUMMARY_MTP_METHOD="${GB10_MTP2_MOE_SPEC_METHOD}" \
SUMMARY_CONCURRENCY="${GB10_MTP2_MOE_CONCURRENCY}" \
SUMMARY_ROUND_COUNT="${GB10_MTP2_MOE_ROUND_COUNT}" \
SUMMARY_LINE_COUNT="${GB10_MTP2_MOE_LINE_COUNT}" \
SUMMARY_MAX_TOKENS="${GB10_MTP2_MOE_MAX_TOKENS}" \
LOCAL_PYTHON="${LOCAL_PYTHON:-python3}" "${LOCAL_PYTHON:-python3}" - <<'PY'
import json
import os
from pathlib import Path


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str | None:
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace").strip()
    return None


root = Path(os.environ["SUMMARY_ROOT"])
soak = load_json(root / "streaming_pressure_soak.json")
runtime = load_json(root / "runtime_stats_summary.json")
driver_health = load_json(root / "driver_health_summary.json")
runtime_metrics = runtime.get("metrics", {}) if isinstance(runtime, dict) else {}
no_progress = root / "watchdog" / "no_progress_detected.txt"
payload = {
    "ok": (
        read_text(root / "serve_start.exit_code") == "0"
        and read_text(root / "streaming_pressure_soak.exit_code") == "0"
        and not no_progress.exists()
        and soak.get("ok") is not False
        and driver_health.get("ok", True)
    ),
    "profile": {
        "hardware": "2x GB10 / SM121",
        "tp": 2,
        "pp": 1,
        "expert_parallel": True,
        "prefix_cache": "enabled",
        "mtp": {
            "method": os.environ["SUMMARY_MTP_METHOD"],
            "num_speculative_tokens": 2,
        },
        "fp8_kv": True,
        "cuda_graph": "FULL_AND_PIECEWISE",
        "max_model_len": int(os.environ["SUMMARY_MAX_MODEL_LEN"]),
        "max_num_seqs": int(os.environ["SUMMARY_MAX_NUM_SEQS"]),
        "max_num_batched_tokens": int(
            os.environ["SUMMARY_MAX_NUM_BATCHED_TOKENS"]
        ),
        "gpu_memory_utilization": os.environ["SUMMARY_GPU_MEMORY_UTILIZATION"],
        "streaming_pressure": {
            "concurrency": int(os.environ["SUMMARY_CONCURRENCY"]),
            "round_count": int(os.environ["SUMMARY_ROUND_COUNT"]),
            "line_count": int(os.environ["SUMMARY_LINE_COUNT"]),
            "max_tokens": int(os.environ["SUMMARY_MAX_TOKENS"]),
        },
    },
    "serve_start_exit_code": read_text(root / "serve_start.exit_code"),
    "streaming_pressure_soak_exit_code": read_text(
        root / "streaming_pressure_soak.exit_code"
    ),
    "remote_run_root": read_text(root / "remote_run_root.txt"),
    "no_progress_detected": no_progress.exists(),
    "no_progress_detail": read_text(no_progress),
    "driver_health": driver_health,
    "streaming_pressure_summary": soak.get("summary", {}),
    "runtime_metrics": {
        name: runtime_metrics.get(name)
        for name in (
            "running_requests_max",
            "running_requests_avg",
            "waiting_requests_max",
            "waiting_requests_avg",
            "decode_tokens_delta",
            "prefill_tokens_delta",
            "decode_throughput_tok_s_max",
            "prefill_throughput_tok_s_max",
            "gpu_kv_cache_usage_percent_max",
            "prefix_cache_queries_delta",
            "prefix_cache_hits_delta",
            "preemptions_delta",
        )
    },
}
(root / "gb10_mtp2_moe_tp_deadlock_gate_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

summary = payload["streaming_pressure_summary"]
metrics = payload["runtime_metrics"]
lines = [
    "# GB10 MTP=2 MoE TP Deadlock Gate",
    "",
    f"- OK: `{payload['ok']}`",
    f"- No progress detected: `{payload['no_progress_detected']}`",
    f"- Driver health OK: `{payload['driver_health'].get('ok', True)}`",
    f"- Driver signal count: `{payload['driver_health'].get('signal_count', 0)}`",
    f"- Serve exit: `{payload['serve_start_exit_code']}`",
    f"- Soak exit: `{payload['streaming_pressure_soak_exit_code']}`",
    f"- Remote artifact: `{payload['remote_run_root']}`",
    "",
    "## Profile",
    "",
    "- `TP=2`, `PP=1`, expert parallel enabled.",
    "- Prefix cache enabled, FP8 KV, MTP=2.",
    "- `max_model_len={}`, `max_num_seqs={}`, `max_num_batched_tokens={}`.".format(
        payload["profile"]["max_model_len"],
        payload["profile"]["max_num_seqs"],
        payload["profile"]["max_num_batched_tokens"],
    ),
    "- CUDA graph mode `FULL_AND_PIECEWISE`.",
    "",
    "## Results",
    "",
    "| Requests | Failures | Max TTFT s | ITL P99 s | running max | waiting max | Decode tokens | Prefix hits | Preemptions |",
    "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    "| {requests} | {failures} | {ttft} | {p99} | {running} | {waiting} | {decode_tokens} | {prefix_hits} | {preemptions} |".format(
        requests=summary.get("request_count", ""),
        failures=summary.get("failure_count", ""),
        ttft=summary.get("max_ttft_seconds", ""),
        p99=summary.get("p99_inter_chunk_seconds", ""),
        running=metrics.get("running_requests_max", ""),
        waiting=metrics.get("waiting_requests_max", ""),
        decode_tokens=metrics.get("decode_tokens_delta", ""),
        prefix_hits=metrics.get("prefix_cache_hits_delta", ""),
        preemptions=metrics.get("preemptions_delta", ""),
    ),
]
if payload["no_progress_detail"]:
    lines.extend(["", "## No Progress Detail", "", payload["no_progress_detail"]])
if not payload["driver_health"].get("ok", True):
    lines.extend(["", "## Driver Health", ""])
    for label, host in payload["driver_health"].get("hosts", {}).items():
        lines.append(
            f"- `{label}`: {host.get('signal_count', 0)} signal(s), "
            f"`{host.get('signals_path', '')}`"
        )
(root / "gb10_mtp2_moe_tp_deadlock_gate_summary.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)
PY

echo "wrote ${OUT_DIR}"
if [[ "${start_code}" != "0" || "${soak_code}" != "0" \
    || -f "${OUT_DIR}/watchdog/no_progress_detected.txt" \
    || "${driver_health_ok}" != "1" ]]; then
  exit 1
fi
exit 0
