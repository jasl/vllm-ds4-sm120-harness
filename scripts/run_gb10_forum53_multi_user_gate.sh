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

run_remote_streaming_matrix() {
  local remote_out_dir="$1"
  local variant="$2"
  local max_batched_tokens="$3"

  run_remote "${HEAD_HOST}" \
    "cd $(shell_quote "${REMOTE_HARNESS_ROOT}") && env \
      PYTHON=$(shell_quote "${VLLM_VENV}/bin/python") \
      BASE_URL=$(shell_quote "http://127.0.0.1:${API_PORT}") \
      MODEL=$(shell_quote "${MODEL_ID}") \
      GPU_TOPOLOGY_SLUG=$(shell_quote "${GPU_TOPOLOGY_SLUG}") \
      BRANCH_NAME=$(shell_quote "${BRANCH_NAME}") \
      OUT_DIR=$(shell_quote "${remote_out_dir}") \
      STREAMING_PRESSURE_MATRIX_VARIANT=$(shell_quote "${variant}-mbt${max_batched_tokens}") \
      STREAMING_PRESSURE_MATRIX_CASE_NAME=$(shell_quote "${GB10_FORUM53_CASE_NAME}") \
      STREAMING_PRESSURE_MATRIX_CASE_SPECS=$(shell_quote "${GB10_FORUM53_CASE_SPECS}") \
      STREAMING_PRESSURE_MATRIX_TIMEOUT=$(shell_quote "${GB10_FORUM53_TIMEOUT}") \
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
GB10_FORUM53_BATCHED_TOKEN_SWEEP="${GB10_FORUM53_BATCHED_TOKEN_SWEEP:-2048,3072,4096,6144,8192}"
GB10_FORUM53_CASE_NAME="${GB10_FORUM53_CASE_NAME:-forum53_multi_user_prefix_cache}"
GB10_FORUM53_CASE_SPECS="${GB10_FORUM53_CASE_SPECS:-forum53_c6:6:1:3200:128,forum53_c8:8:1:3200:128}"
GB10_FORUM53_TIMEOUT="${GB10_FORUM53_TIMEOUT:-1800}"
GB10_FORUM53_MAX_TTFT_SECONDS="${GB10_FORUM53_MAX_TTFT_SECONDS:-600}"
GB10_FORUM53_MAX_ELAPSED_SECONDS="${GB10_FORUM53_MAX_ELAPSED_SECONDS:-1800}"
GB10_FORUM53_FAIL_ON_SLOW="${GB10_FORUM53_FAIL_ON_SLOW:-0}"
GB10_FORUM53_SERVER_STARTUP_TIMEOUT="${GB10_FORUM53_SERVER_STARTUP_TIMEOUT:-45}"

MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
API_PORT="${API_PORT:-8000}"
TP_SIZE="${GB10_FORUM53_TP_SIZE:-2}"
PP_SIZE="${GB10_FORUM53_PP_SIZE:-1}"
MAX_MODEL_LEN="${GB10_FORUM53_MAX_MODEL_LEN:-262144}"
GPU_MEMORY_UTILIZATION="${GB10_FORUM53_GPU_MEMORY_UTILIZATION:-0.90}"
MAX_NUM_SEQS="${GB10_FORUM53_MAX_NUM_SEQS:-8}"
BLOCK_SIZE="${GB10_FORUM53_BLOCK_SIZE:-256}"
KV_CACHE_DTYPE="${GB10_FORUM53_KV_CACHE_DTYPE:-fp8}"
MIN_AVAILABLE_MEM_GIB="${GB10_FORUM53_MIN_AVAILABLE_MEM_GIB:-96}"
SERVE_COMPILATION_CONFIG="${GB10_FORUM53_COMPILATION_CONFIG:-{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}}"

mkdir -p "${OUT_DIR}"
printf '%s\n' "${REMOTE_RUN_ROOT}" > "${OUT_DIR}/remote_run_root.txt"

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
    serve_remote_env_vars="${SERVE_REMOTE_ENV_VARS:-}"
    serve_remote_env_vars="$(
      append_env_allowlist \
        "${serve_remote_env_vars}" \
        VLLM_DEEPSEEK_V4_INDEXED_D512_CHUNKED_PREFILL
    )"

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
      SERVE_ENABLE_EXPERT_PARALLEL=1 \
      SERVE_PREFIX_CACHE_MODE=enabled \
      SERVE_SPECULATIVE_CONFIG="${speculative_config}" \
      SERVE_COMPILATION_CONFIG="${SERVE_COMPILATION_CONFIG}" \
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

    stop_remote_vllm "${WORKER_HOST}"
    stop_remote_vllm "${HEAD_HOST}"

    if [[ "${start_code}" != "0" || "${matrix_code}" != "0" ]]; then
      failures=1
    fi
  done
done

SUMMARY_ROOT="${OUT_DIR}" LOCAL_PYTHON="${LOCAL_PYTHON:-python3}" "${LOCAL_PYTHON:-python3}" - <<'PY'
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
rows = []
for variant_dir in sorted(path for path in root.iterdir() if path.is_dir()):
    variant = read_text(variant_dir / "variant.txt") or variant_dir.name
    max_batched_tokens = read_text(variant_dir / "max_num_batched_tokens.txt")
    matrix = read_json(variant_dir / "streaming_pressure_matrix.json")
    runtime = read_json(variant_dir / "runtime_stats_summary.json")
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
    }
    rows.append(row)

payload = {
    "ok": all(
        row.get("serve_start_exit_code") == "0"
        and row.get("streaming_pressure_exit_code") == "0"
        and row.get("ok") is not False
        for row in rows
    ),
    "profile": {
        "max_model_len": 262144,
        "max_num_seqs": 8,
        "prefix_cache": "enabled",
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
    "- Profile: `TP=2`, `max_model_len=262144`, `max_num_seqs=8`, prefix cache enabled.",
    "",
    "| Variant | max_num_batched_tokens | Serve exit | Matrix exit | Requests | Failures | Max TTFT s | ITL P99 s | running max | waiting max | KV max % | Prefix hits | Preemptions | Remote artifact |",
    "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
]
for row in rows:
    summary = row.get("summary") or {}
    runtime_metrics = row.get("runtime_metrics") or {}
    lines.append(
        "| {variant} | {mbt} | {serve} | {matrix} | {requests} | {failures} | {ttft} | {p99} | {running} | {waiting} | {kv} | {prefix_hits} | {preemptions} | `{remote}` |".format(
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
            kv=runtime_metrics.get("gpu_kv_cache_usage_percent_max", ""),
            prefix_hits=runtime_metrics.get("prefix_cache_hits_delta", ""),
            preemptions=runtime_metrics.get("preemptions_delta", ""),
            remote=row.get("remote_variant_root", ""),
        )
    )
(root / "gb10_forum53_multi_user_gate_summary.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)
PY

echo "wrote ${OUT_DIR}"
exit "${failures}"
