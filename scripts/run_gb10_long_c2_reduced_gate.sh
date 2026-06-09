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

  run_remote "${HEAD_HOST}" \
    "cd $(shell_quote "${REMOTE_HARNESS_ROOT}") && env \
      PYTHON=$(shell_quote "${VLLM_VENV}/bin/python") \
      BASE_URL=$(shell_quote "http://127.0.0.1:${API_PORT}") \
      MODEL=$(shell_quote "${MODEL_ID}") \
      GPU_TOPOLOGY_SLUG=$(shell_quote "${GPU_TOPOLOGY_SLUG}") \
      BRANCH_NAME=$(shell_quote "${BRANCH_NAME}") \
      OUT_DIR=$(shell_quote "${remote_out_dir}") \
      STREAMING_PRESSURE_MATRIX_VARIANT=$(shell_quote "${variant}") \
      STREAMING_PRESSURE_MATRIX_CASE_NAME=$(shell_quote "${GB10_LONG_C2_CASE_NAME}") \
      STREAMING_PRESSURE_MATRIX_CASE_SPECS=$(shell_quote "${GB10_LONG_C2_CASE_SPECS}") \
      STREAMING_PRESSURE_MATRIX_TIMEOUT=$(shell_quote "${GB10_LONG_C2_TIMEOUT}") \
      STREAMING_PRESSURE_MATRIX_MAX_TTFT_SECONDS=$(shell_quote "${GB10_LONG_C2_MAX_TTFT_SECONDS}") \
      STREAMING_PRESSURE_MATRIX_MAX_ELAPSED_SECONDS=$(shell_quote "${GB10_LONG_C2_MAX_ELAPSED_SECONDS}") \
      STREAMING_PRESSURE_MATRIX_FAIL_ON_SLOW=$(shell_quote "${GB10_LONG_C2_FAIL_ON_SLOW}") \
      SERVER_STARTUP_TIMEOUT=$(shell_quote "${GB10_LONG_C2_SERVER_STARTUP_TIMEOUT}") \
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
      printf 'unsupported GB10_LONG_C2 variant: %s\n' "${variant}" >&2
      return 2
      ;;
  esac
}

BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-2x_gb10_sm121}"
GB10_LONG_C2_LABEL="${GB10_LONG_C2_LABEL:-gb10_long_c2_reduced_gate}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${GB10_LONG_C2_LABEL}/${RUN_TIMESTAMP}}"

REMOTE_HARNESS_ROOT="${GB10_LONG_C2_REMOTE_HARNESS_ROOT:-$(dirname -- "${VLLM_ROOT}")}"
REMOTE_RUN_ROOT="${GB10_LONG_C2_REMOTE_RUN_ROOT:-${REMOTE_HARNESS_ROOT}/artifacts/${GB10_LONG_C2_LABEL}/${RUN_TIMESTAMP}}"

GB10_LONG_C2_VARIANTS="${GB10_LONG_C2_VARIANTS:-nomtp,mtp2}"
GB10_LONG_C2_CASE_NAME="${GB10_LONG_C2_CASE_NAME:-gb10_long_c2_reduced_gate}"
GB10_LONG_C2_CASE_SPECS="${GB10_LONG_C2_CASE_SPECS:-long_c2:2:2:4000:128}"
GB10_LONG_C2_TIMEOUT="${GB10_LONG_C2_TIMEOUT:-900}"
GB10_LONG_C2_MAX_TTFT_SECONDS="${GB10_LONG_C2_MAX_TTFT_SECONDS:-360}"
GB10_LONG_C2_MAX_ELAPSED_SECONDS="${GB10_LONG_C2_MAX_ELAPSED_SECONDS:-900}"
GB10_LONG_C2_FAIL_ON_SLOW="${GB10_LONG_C2_FAIL_ON_SLOW:-0}"
GB10_LONG_C2_SERVER_STARTUP_TIMEOUT="${GB10_LONG_C2_SERVER_STARTUP_TIMEOUT:-30}"
GB10_LONG_C2_SCHEDULER_TRACE="${GB10_LONG_C2_SCHEDULER_TRACE:-0}"
GB10_LONG_C2_ENABLE_EXPERT_PARALLEL="${GB10_LONG_C2_ENABLE_EXPERT_PARALLEL:-0}"
GB10_LONG_C2_ALLOW_DRIVER_SIGNALS="${GB10_LONG_C2_ALLOW_DRIVER_SIGNALS:-0}"

case "${GB10_LONG_C2_ENABLE_EXPERT_PARALLEL}" in
  1|true|TRUE|yes|YES)
    gb10_long_c2_enable_expert_parallel=1
    ;;
  0|false|FALSE|no|NO)
    gb10_long_c2_enable_expert_parallel=0
    ;;
  *)
    printf 'GB10_LONG_C2_ENABLE_EXPERT_PARALLEL must be 0/1 or true/false; got %s\n' \
      "${GB10_LONG_C2_ENABLE_EXPERT_PARALLEL}" >&2
    exit 2
    ;;
esac

MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
API_PORT="${API_PORT:-8000}"
TP_SIZE="${GB10_LONG_C2_TP_SIZE:-2}"
PP_SIZE="${GB10_LONG_C2_PP_SIZE:-1}"
MAX_MODEL_LEN="${GB10_LONG_C2_MAX_MODEL_LEN:-131072}"
GPU_MEMORY_UTILIZATION="${GB10_LONG_C2_GPU_MEMORY_UTILIZATION:-0.70}"
MAX_NUM_SEQS="${GB10_LONG_C2_MAX_NUM_SEQS:-2}"
MAX_NUM_BATCHED_TOKENS="${GB10_LONG_C2_MAX_NUM_BATCHED_TOKENS:-4176}"
BLOCK_SIZE="${GB10_LONG_C2_BLOCK_SIZE:-256}"
KV_CACHE_DTYPE="${GB10_LONG_C2_KV_CACHE_DTYPE:-fp8}"
MIN_AVAILABLE_MEM_GIB="${GB10_LONG_C2_MIN_AVAILABLE_MEM_GIB:-96}"
SERVE_COMPILATION_CONFIG="${GB10_LONG_C2_COMPILATION_CONFIG:-{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}}"

mkdir -p "${OUT_DIR}"
printf '%s\n' "${REMOTE_RUN_ROOT}" > "${OUT_DIR}/remote_run_root.txt"

failures=0
IFS=',' read -r -a variants <<< "${GB10_LONG_C2_VARIANTS}"
for variant in "${variants[@]}"; do
  variant="$(printf '%s' "${variant}" | xargs)"
  if [[ -z "${variant}" ]]; then
    continue
  fi

  variant_dir="${OUT_DIR}/${variant}"
  remote_variant_root="${REMOTE_RUN_ROOT}/${variant}"
  remote_serve_dir="${remote_variant_root}/serve"
  remote_matrix_dir="${remote_variant_root}/streaming_pressure_longc2"
  speculative_config="$(variant_speculative_config "${variant}")" || exit 2
  scheduler_trace_path="${remote_serve_dir}/scheduler_trace.jsonl"
  serve_remote_env_vars="${SERVE_REMOTE_ENV_VARS:-}"
  serve_remote_env_vars="$(
    append_env_allowlist \
      "${serve_remote_env_vars}" \
      VLLM_DEEPSEEK_V4_INDEXED_D512_CHUNKED_PREFILL
  )"
  if [[ "${GB10_LONG_C2_SCHEDULER_TRACE}" == "1" || "${GB10_LONG_C2_SCHEDULER_TRACE}" == "true" ]]; then
    if [[ -n "${serve_remote_env_vars}" ]]; then
      serve_remote_env_vars="${serve_remote_env_vars},VLLM_SCHEDULER_TRACE_PATH"
    else
      serve_remote_env_vars="VLLM_SCHEDULER_TRACE_PATH"
    fi
  fi

  mkdir -p "${variant_dir}"
  printf '%s\n' "${remote_variant_root}" > "${variant_dir}/remote_variant_root.txt"
  printf '%s\n' "${remote_matrix_dir}" > "${variant_dir}/remote_streaming_pressure_dir.txt"

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
    SERVE_ENABLE_EXPERT_PARALLEL="${gb10_long_c2_enable_expert_parallel}" \
    SERVE_PREFIX_CACHE_MODE=disabled \
    SERVE_SPECULATIVE_CONFIG="${speculative_config}" \
    SERVE_COMPILATION_CONFIG="${SERVE_COMPILATION_CONFIG}" \
    VLLM_SCHEDULER_TRACE_PATH="${scheduler_trace_path}" \
    SERVE_REMOTE_ENV_VARS="${serve_remote_env_vars}" \
    SSH_OPTS="${SSH_OPTS:-}" \
    "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" \
      > "${variant_dir}/serve_start.stdout.log" \
      2> "${variant_dir}/serve_start.stderr.log"
  start_code="$?"
  set -e
  printf '%s\n' "${start_code}" > "${variant_dir}/serve_start.exit_code"

  matrix_code=125
  if [[ "${start_code}" == "0" ]]; then
    set +e
    run_remote_streaming_matrix "${remote_matrix_dir}" "${variant}" \
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
  if [[ "${GB10_LONG_C2_SCHEDULER_TRACE}" == "1" || "${GB10_LONG_C2_SCHEDULER_TRACE}" == "true" ]]; then
    fetch_remote_file "${scheduler_trace_path}" "${variant_dir}/scheduler_trace.jsonl"
    if [[ -s "${variant_dir}/scheduler_trace.jsonl" ]]; then
      "${LOCAL_PYTHON:-python3}" "${SCRIPT_DIR}/analyze_scheduler_trace.py" \
        "${variant_dir}/scheduler_trace.jsonl" \
        --json-output "${variant_dir}/scheduler_trace_summary.json" \
        --markdown-output "${variant_dir}/scheduler_trace_summary.md"
    fi
  fi

  stop_remote_vllm "${WORKER_HOST}"
  stop_remote_vllm "${HEAD_HOST}"

  if [[ "${start_code}" != "0" || "${matrix_code}" != "0" ]]; then
    failures=1
  fi
done

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

if [[ "${driver_health_signal_count}" == "0" \
    || "${GB10_LONG_C2_ALLOW_DRIVER_SIGNALS}" == "1" ]]; then
  driver_health_ok=1
else
  driver_health_ok=0
  failures=1
fi

DRIVER_HEALTH_ROOT="${driver_health_dir}" \
DRIVER_HEALTH_OK="${driver_health_ok}" \
DRIVER_HEALTH_SIGNAL_COUNT="${driver_health_signal_count}" \
DRIVER_HEALTH_ALLOW="${GB10_LONG_C2_ALLOW_DRIVER_SIGNALS}" \
LOCAL_PYTHON="${LOCAL_PYTHON:-python3}" \
"${LOCAL_PYTHON:-python3}" - <<'PY'
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
GB10_LONG_C2_ENABLE_EXPERT_PARALLEL="${gb10_long_c2_enable_expert_parallel}" \
LOCAL_PYTHON="${LOCAL_PYTHON:-python3}" \
"${LOCAL_PYTHON:-python3}" - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["SUMMARY_ROOT"])
driver_health = {}
driver_health_path = root / "driver_health_summary.json"
if driver_health_path.exists():
    driver_health = json.loads(driver_health_path.read_text(encoding="utf-8"))
rows = []
for variant_dir in sorted(path for path in root.iterdir() if path.is_dir()):
    if variant_dir.name == "driver_health":
        continue
    variant = variant_dir.name
    row = {
        "variant": variant,
        "serve_start_exit_code": (variant_dir / "serve_start.exit_code").read_text(
            encoding="utf-8"
        ).strip()
        if (variant_dir / "serve_start.exit_code").exists()
        else None,
        "streaming_pressure_exit_code": (
            variant_dir / "streaming_pressure.exit_code"
        ).read_text(encoding="utf-8").strip()
        if (variant_dir / "streaming_pressure.exit_code").exists()
        else None,
        "remote_variant_root": (variant_dir / "remote_variant_root.txt").read_text(
            encoding="utf-8"
        ).strip()
        if (variant_dir / "remote_variant_root.txt").exists()
        else None,
    }
    matrix_path = variant_dir / "streaming_pressure_matrix.json"
    if matrix_path.exists():
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        row["ok"] = matrix.get("ok")
        row["summary"] = matrix.get("summary", {})
    rows.append(row)

payload = {
    "ok": all(
        row.get("serve_start_exit_code") == "0"
        and row.get("streaming_pressure_exit_code") == "0"
        and row.get("ok") is not False
        for row in rows
    ) and driver_health.get("ok", True),
    "expert_parallel_enabled": os.environ["GB10_LONG_C2_ENABLE_EXPERT_PARALLEL"],
    "driver_health": driver_health,
    "variants": rows,
}
(root / "gb10_long_c2_reduced_gate_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

lines = [
    "# GB10 Long C=2 Reduced Gate",
    "",
    f"- OK: `{payload['ok']}`",
    f"- Expert parallel enabled: `{payload['expert_parallel_enabled']}`",
    f"- Driver health OK: `{payload['driver_health'].get('ok', True)}`",
    f"- Driver signal count: `{payload['driver_health'].get('signal_count', 0)}`",
    "",
    "| Variant | Serve exit | Matrix exit | Requests | Failures | Max TTFT s | ITL P99 s | Remote artifact |",
    "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
]
for row in rows:
    summary = row.get("summary") or {}
    lines.append(
        "| {variant} | {serve} | {matrix} | {requests} | {failures} | {ttft} | {p99} | `{remote}` |".format(
            variant=row.get("variant"),
            serve=row.get("serve_start_exit_code"),
            matrix=row.get("streaming_pressure_exit_code"),
            requests=summary.get("request_count", ""),
            failures=summary.get("failure_count", ""),
            ttft=summary.get("max_ttft_seconds", ""),
            p99=summary.get("p99_inter_chunk_seconds", ""),
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
(root / "gb10_long_c2_reduced_gate_summary.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)
PY

echo "wrote ${OUT_DIR}"
exit "${failures}"
