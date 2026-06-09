#!/usr/bin/env bash
# Run a focused long-prefill attribution matrix on a two-node GB10 cluster.
#
# This is a development observation gate. It starts the public no-Ray MP
# TP=2/PP=1 serve profile, enables DeepSeek V4 sparse MLA prefill stats, runs
# random long-prefill sweeps, and reports endpoint latency/decode metrics beside
# sparse compressed/SWA candidate work and backend evidence from serve logs.

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
  local host="$1"
  local remote_path="$2"
  local local_path="$3"

  mkdir -p "$(dirname -- "${local_path}")"
  if run_remote "${host}" "test -f $(shell_quote "${remote_path}")"; then
    run_remote "${host}" "cat $(shell_quote "${remote_path}")" > "${local_path}"
  fi
}

fetch_remote_stats_dir() {
  local host="$1"
  local node_label="$2"
  local remote_dir="$3"
  local local_dir="$4"

  mkdir -p "${local_dir}"
  while IFS= read -r name; do
    [[ -n "${name}" ]] || continue
    fetch_remote_file \
      "${host}" \
      "${remote_dir}/${name}" \
      "${local_dir}/${node_label}_${name}"
  done < <(
    run_remote "${host}" \
      "if test -d $(shell_quote "${remote_dir}"); then find $(shell_quote "${remote_dir}") -maxdepth 1 -type f -name '*.jsonl' -printf '%f\n'; fi"
  )
}

fetch_remote_serve_logs() {
  local remote_serve_dir="$1"
  local case_dir="$2"

  fetch_remote_file "${HEAD_HOST}" "${remote_serve_dir}/head.log" \
    "${case_dir}/serve_head.log"
  fetch_remote_file "${WORKER_HOST}" "${remote_serve_dir}/worker.log" \
    "${case_dir}/serve_worker.log"
  fetch_remote_file "${HEAD_HOST}" "${remote_serve_dir}/prewarm.log" \
    "${case_dir}/serve_prewarm.log"
  fetch_remote_file "${HEAD_HOST}" "${remote_serve_dir}/health.out" \
    "${case_dir}/serve_health.out"
  fetch_remote_file "${HEAD_HOST}" "${remote_serve_dir}/health.err" \
    "${case_dir}/serve_health.err"
}

run_remote_prefill_sweep() {
  local remote_out_dir="$1"
  local input_len="$2"

  run_remote "${HEAD_HOST}" \
    "cd $(shell_quote "${REMOTE_HARNESS_ROOT}") && env \
      PYTHON=$(shell_quote "${VLLM_VENV}/bin/python") \
      VLLM_BIN=$(shell_quote "${VLLM_VENV}/bin/vllm") \
      MODEL=$(shell_quote "${MODEL_ID}") \
      HOST=127.0.0.1 \
      PORT=$(shell_quote "${API_PORT}") \
      BASE_URL=$(shell_quote "http://127.0.0.1:${API_PORT}") \
      GPU_TOPOLOGY_SLUG=$(shell_quote "${GPU_TOPOLOGY_SLUG}") \
      BRANCH_NAME=$(shell_quote "${BRANCH_NAME}") \
      OUT_DIR=$(shell_quote "${remote_out_dir}") \
      RANDOM_PREFILL_INPUT_LENS=$(shell_quote "${input_len}") \
      RANDOM_PREFILL_OUTPUT_LEN=$(shell_quote "${GB10_PREFILL_GAP_OUTPUT_LEN}") \
      RANDOM_PREFILL_CONCURRENCY=$(shell_quote "${GB10_PREFILL_GAP_CONCURRENCY}") \
      RANDOM_PREFILL_NUM_PROMPTS=$(shell_quote "${GB10_PREFILL_GAP_NUM_PROMPTS}") \
      RANDOM_PREFILL_BENCH_TIMEOUT=$(shell_quote "${GB10_PREFILL_GAP_BENCH_TIMEOUT}") \
      RANDOM_PREFILL_TEMPERATURE=0.0 \
      RANDOM_PREFILL_IGNORE_EOS=1 \
      TOKENIZER_MODE=deepseek_v4 \
      $(shell_quote "${REMOTE_HARNESS_ROOT}/scripts/run_random_prefill_sweep.sh")"
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
      printf 'unsupported GB10_PREFILL_GAP variant: %s\n' "${variant}" >&2
      return 2
      ;;
  esac
}

profile_extra_args() {
  local profile="$1"
  case "${profile}" in
    dev_default)
      printf '%s' "${GB10_PREFILL_GAP_DEV_DEFAULT_EXTRA_ARGS}"
      ;;
    flashinfer_sparse_dsv4)
      printf '%s' "--attention-backend FLASHINFER_MLA_SPARSE_DSV4 ${GB10_PREFILL_GAP_FLASHINFER_EXTRA_ARGS}"
      ;;
    reddit_style)
      printf '%s' "${GB10_PREFILL_GAP_REDDIT_EXTRA_ARGS}"
      ;;
    *)
      printf 'unsupported GB10_PREFILL_GAP profile: %s\n' "${profile}" >&2
      return 2
      ;;
  esac
}

profile_max_num_batched_tokens() {
  local profile="$1"
  case "${profile}" in
    reddit_style)
      printf '%s' "${GB10_PREFILL_GAP_REDDIT_MAX_NUM_BATCHED_TOKENS}"
      ;;
    dev_default|flashinfer_sparse_dsv4)
      printf '%s' "${MAX_NUM_BATCHED_TOKENS}"
      ;;
    *)
      printf 'unsupported GB10_PREFILL_GAP profile: %s\n' "${profile}" >&2
      return 2
      ;;
  esac
}

profile_description() {
  local profile="$1"
  case "${profile}" in
    dev_default)
      printf 'current dev default attention path'
      ;;
    flashinfer_sparse_dsv4)
      printf 'explicit upstream FLASHINFER_MLA_SPARSE_DSV4 attention backend'
      ;;
    reddit_style)
      printf 'Reddit-style serve budget and caller-provided extra flags'
      ;;
    *)
      printf 'unsupported GB10_PREFILL_GAP profile: %s\n' "${profile}" >&2
      return 2
      ;;
  esac
}

profile_expected_attention_marker() {
  local profile="$1"
  case "${profile}" in
    dev_default)
      printf ''
      ;;
    flashinfer_sparse_dsv4)
      printf 'FLASHINFER_MLA_SPARSE_DSV4'
      ;;
    reddit_style)
      printf ''
      ;;
    *)
      printf 'unsupported GB10_PREFILL_GAP profile: %s\n' "${profile}" >&2
      return 2
      ;;
  esac
}

append_remote_env_var() {
  local current="$1"
  local name="$2"
  if [[ -n "${current}" ]]; then
    printf '%s,%s' "${current}" "${name}"
  else
    printf '%s' "${name}"
  fi
}

BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-2x_gb10_sm121}"
GB10_PREFILL_GAP_LABEL="${GB10_PREFILL_GAP_LABEL:-gb10_prefill_gap_attribution}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${GB10_PREFILL_GAP_LABEL}/${RUN_TIMESTAMP}}"

REMOTE_HARNESS_ROOT="${GB10_PREFILL_GAP_REMOTE_HARNESS_ROOT:-$(dirname -- "${VLLM_ROOT}")}"
REMOTE_RUN_ROOT="${GB10_PREFILL_GAP_REMOTE_RUN_ROOT:-${REMOTE_HARNESS_ROOT}/artifacts/${GB10_PREFILL_GAP_LABEL}/${RUN_TIMESTAMP}}"

GB10_PREFILL_GAP_PROFILES="${GB10_PREFILL_GAP_PROFILES:-dev_default,flashinfer_sparse_dsv4,reddit_style}"
GB10_PREFILL_GAP_VARIANTS="${GB10_PREFILL_GAP_VARIANTS:-mtp2}"
GB10_PREFILL_GAP_PREFIX_CACHE_MODES="${GB10_PREFILL_GAP_PREFIX_CACHE_MODES:-disabled,enabled}"
GB10_PREFILL_GAP_INPUT_LENS="${GB10_PREFILL_GAP_INPUT_LENS:-4096,16384,32768,65536,128000}"
GB10_PREFILL_GAP_CONCURRENCY="${GB10_PREFILL_GAP_CONCURRENCY:-1}"
GB10_PREFILL_GAP_OUTPUT_LEN="${GB10_PREFILL_GAP_OUTPUT_LEN:-128}"
GB10_PREFILL_GAP_NUM_PROMPTS="${GB10_PREFILL_GAP_NUM_PROMPTS:-2}"
GB10_PREFILL_GAP_BENCH_TIMEOUT="${GB10_PREFILL_GAP_BENCH_TIMEOUT:-1800}"
GB10_PREFILL_GAP_ENABLE_EXPERT_PARALLEL="${GB10_PREFILL_GAP_ENABLE_EXPERT_PARALLEL:-0}"
GB10_PREFILL_GAP_STATS_OVERLAP_ROWS="${GB10_PREFILL_GAP_STATS_OVERLAP_ROWS:-0}"
GB10_PREFILL_GAP_STAGE_TIMING="${GB10_PREFILL_GAP_STAGE_TIMING:-1}"
GB10_PREFILL_GAP_DEV_DEFAULT_EXTRA_ARGS="${GB10_PREFILL_GAP_DEV_DEFAULT_EXTRA_ARGS:-}"
GB10_PREFILL_GAP_FLASHINFER_EXTRA_ARGS="${GB10_PREFILL_GAP_FLASHINFER_EXTRA_ARGS:-}"
GB10_PREFILL_GAP_REDDIT_EXTRA_ARGS="${GB10_PREFILL_GAP_REDDIT_EXTRA_ARGS:-}"
GB10_PREFILL_GAP_REDDIT_MAX_NUM_BATCHED_TOKENS="${GB10_PREFILL_GAP_REDDIT_MAX_NUM_BATCHED_TOKENS:-8192}"

MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
API_PORT="${API_PORT:-8000}"
TP_SIZE="${GB10_PREFILL_GAP_TP_SIZE:-2}"
PP_SIZE="${GB10_PREFILL_GAP_PP_SIZE:-1}"
MAX_MODEL_LEN="${GB10_PREFILL_GAP_MAX_MODEL_LEN:-131072}"
GPU_MEMORY_UTILIZATION="${GB10_PREFILL_GAP_GPU_MEMORY_UTILIZATION:-0.70}"
MAX_NUM_SEQS="${GB10_PREFILL_GAP_MAX_NUM_SEQS:-2}"
MAX_NUM_BATCHED_TOKENS="${GB10_PREFILL_GAP_MAX_NUM_BATCHED_TOKENS:-4176}"
BLOCK_SIZE="${GB10_PREFILL_GAP_BLOCK_SIZE:-256}"
KV_CACHE_DTYPE="${GB10_PREFILL_GAP_KV_CACHE_DTYPE:-fp8}"
MIN_AVAILABLE_MEM_GIB="${GB10_PREFILL_GAP_MIN_AVAILABLE_MEM_GIB:-96}"
SERVE_COMPILATION_CONFIG="${GB10_PREFILL_GAP_COMPILATION_CONFIG:-{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}}"

LOCAL_PYTHON="${LOCAL_PYTHON:-python3}"
mkdir -p "${OUT_DIR}"
printf '%s\n' "${REMOTE_RUN_ROOT}" > "${OUT_DIR}/remote_run_root.txt"

failures=0
case_dirs=()
IFS=',' read -r -a profiles <<< "${GB10_PREFILL_GAP_PROFILES}"
IFS=',' read -r -a variants <<< "${GB10_PREFILL_GAP_VARIANTS}"
IFS=',' read -r -a prefix_cache_modes <<< "${GB10_PREFILL_GAP_PREFIX_CACHE_MODES}"
IFS=',' read -r -a input_lens <<< "${GB10_PREFILL_GAP_INPUT_LENS}"
for raw_profile in "${profiles[@]}"; do
  profile="$(printf '%s' "${raw_profile}" | xargs)"
  [[ -n "${profile}" ]] || continue
  profile_extra="$(profile_extra_args "${profile}")" || exit 2
  profile_description_text="$(profile_description "${profile}")" || exit 2
  expected_attention_marker="$(profile_expected_attention_marker "${profile}")" || exit 2
  profile_max_batched_tokens="$(profile_max_num_batched_tokens "${profile}")" || exit 2

  for raw_prefix_cache_mode in "${prefix_cache_modes[@]}"; do
    prefix_cache_mode="$(printf '%s' "${raw_prefix_cache_mode}" | xargs)"
    [[ -n "${prefix_cache_mode}" ]] || continue

    for raw_variant in "${variants[@]}"; do
      variant="$(printf '%s' "${raw_variant}" | xargs)"
      [[ -n "${variant}" ]] || continue
      speculative_config="$(variant_speculative_config "${variant}")" || exit 2

      for raw_input_len in "${input_lens[@]}"; do
        input_len="$(printf '%s' "${raw_input_len}" | tr -d '[:space:]')"
        [[ -n "${input_len}" ]] || continue

        case_name="${profile}_prefix-${prefix_cache_mode}_${variant}_isl${input_len}"
        case_dir="${OUT_DIR}/${case_name}"
        remote_case_root="${REMOTE_RUN_ROOT}/${case_name}"
        remote_serve_dir="${remote_case_root}/serve"
        remote_bench_dir="${remote_case_root}/random_prefill_sweep"
        remote_stats_dir="${remote_case_root}/sparse_mla_stats_raw"
        local_stats_dir="${case_dir}/sparse_mla_stats_raw"
        case_dirs+=("${case_dir}")
        mkdir -p "${case_dir}" "${local_stats_dir}"
        printf '%s\n' "${remote_case_root}" > "${case_dir}/remote_case_root.txt"
        CASE_METADATA_PATH="${case_dir}/case_metadata.json" \
        CASE_PROFILE="${profile}" \
        CASE_PROFILE_DESCRIPTION="${profile_description_text}" \
        CASE_PREFIX_CACHE_MODE="${prefix_cache_mode}" \
        CASE_VARIANT="${variant}" \
        CASE_INPUT_LEN="${input_len}" \
        CASE_OUTPUT_LEN="${GB10_PREFILL_GAP_OUTPUT_LEN}" \
        CASE_CONCURRENCY="${GB10_PREFILL_GAP_CONCURRENCY}" \
        CASE_MAX_NUM_BATCHED_TOKENS="${profile_max_batched_tokens}" \
        CASE_SERVE_EXTRA_ARGS="${profile_extra}" \
        CASE_EXPECTED_ATTENTION_MARKER="${expected_attention_marker}" \
        "${LOCAL_PYTHON}" - <<'PY'
import json
import os
from pathlib import Path

payload = {
    "profile": os.environ["CASE_PROFILE"],
    "profile_description": os.environ["CASE_PROFILE_DESCRIPTION"],
    "prefix_cache_mode": os.environ["CASE_PREFIX_CACHE_MODE"],
    "variant": os.environ["CASE_VARIANT"],
    "input_len": int(os.environ["CASE_INPUT_LEN"]),
    "output_len": int(os.environ["CASE_OUTPUT_LEN"]),
    "concurrency": os.environ["CASE_CONCURRENCY"],
    "max_num_batched_tokens": int(os.environ["CASE_MAX_NUM_BATCHED_TOKENS"]),
    "serve_extra_args": os.environ["CASE_SERVE_EXTRA_ARGS"],
    "expected_attention_marker": os.environ["CASE_EXPECTED_ATTENTION_MARKER"],
}
Path(os.environ["CASE_METADATA_PATH"]).write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

        serve_remote_env_vars="${SERVE_REMOTE_ENV_VARS:-}"
        for env_name in \
            VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_PATH \
            VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_OVERLAP_ROWS \
            VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_STAGE_TIMING; do
          serve_remote_env_vars="$(append_remote_env_var "${serve_remote_env_vars}" "${env_name}")"
        done

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
          MAX_NUM_BATCHED_TOKENS="${profile_max_batched_tokens}" \
          BLOCK_SIZE="${BLOCK_SIZE}" \
          KV_CACHE_DTYPE="${KV_CACHE_DTYPE}" \
          MIN_AVAILABLE_MEM_GIB="${MIN_AVAILABLE_MEM_GIB}" \
          API_PORT="${API_PORT}" \
          RUN_DIR="${remote_serve_dir}" \
          PREWARM_AFTER_HEALTH=0 \
          SERVE_ENABLE_EXPERT_PARALLEL="${GB10_PREFILL_GAP_ENABLE_EXPERT_PARALLEL}" \
          SERVE_PREFIX_CACHE_MODE="${prefix_cache_mode}" \
          SERVE_SPECULATIVE_CONFIG="${speculative_config}" \
          SERVE_COMPILATION_CONFIG="${SERVE_COMPILATION_CONFIG}" \
          SERVE_EXTRA_ARGS="${profile_extra}" \
          VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_PATH="${remote_stats_dir}" \
          VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_OVERLAP_ROWS="${GB10_PREFILL_GAP_STATS_OVERLAP_ROWS}" \
          VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_STAGE_TIMING="${GB10_PREFILL_GAP_STAGE_TIMING}" \
          SERVE_REMOTE_ENV_VARS="${serve_remote_env_vars}" \
          SSH_OPTS="${SSH_OPTS:-}" \
          "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" \
            > "${case_dir}/serve_start.stdout.log" \
            2> "${case_dir}/serve_start.stderr.log"
        start_code="$?"
        set -e
        printf '%s\n' "${start_code}" > "${case_dir}/serve_start.exit_code"

        bench_code=125
        if [[ "${start_code}" == "0" ]]; then
          set +e
          run_remote_prefill_sweep "${remote_bench_dir}" "${input_len}" \
            > "${case_dir}/prefill_sweep.stdout.log" \
            2> "${case_dir}/prefill_sweep.stderr.log"
          bench_code="$?"
          set -e
        fi
        printf '%s\n' "${bench_code}" > "${case_dir}/prefill_sweep.exit_code"

        fetch_remote_file \
          "${HEAD_HOST}" \
          "${remote_bench_dir}/prefill_sweep_summary.json" \
          "${case_dir}/prefill_sweep_summary.json"
        fetch_remote_file \
          "${HEAD_HOST}" \
          "${remote_bench_dir}/prefill_sweep_summary.md" \
          "${case_dir}/prefill_sweep_summary.md"
        fetch_remote_serve_logs "${remote_serve_dir}" "${case_dir}"
        fetch_remote_stats_dir "${HEAD_HOST}" "head" "${remote_stats_dir}" "${local_stats_dir}"
        fetch_remote_stats_dir "${WORKER_HOST}" "worker" "${remote_stats_dir}" "${local_stats_dir}"

        PYTHONPATH="${REPO_ROOT}" "${LOCAL_PYTHON}" -m ds4_harness.cli \
          sparse-mla-stats-report \
          --stats-path "${local_stats_dir}" \
          --json-output "${case_dir}/sparse_mla_stats_summary.json" \
          --markdown-output "${case_dir}/sparse_mla_stats_summary.md"

        stop_remote_vllm "${WORKER_HOST}"
        stop_remote_vllm "${HEAD_HOST}"

        if [[ "${start_code}" != "0" || "${bench_code}" != "0" ]]; then
          failures=1
        fi
      done
    done
  done
done

case_dir_list="$(IFS=:; printf '%s' "${case_dirs[*]}")"
GB10_PREFILL_GAP_CASE_DIRS="${case_dir_list}" \
GB10_PREFILL_GAP_ROOT="${OUT_DIR}" \
"${LOCAL_PYTHON}" - <<'PY'
import json
import os
import re
from pathlib import Path
from typing import Any

root = Path(os.environ["GB10_PREFILL_GAP_ROOT"])
case_dirs = [
    Path(item)
    for item in os.environ.get("GB10_PREFILL_GAP_CASE_DIRS", "").split(":")
    if item
]


def _load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def _read_exit(path: Path) -> int:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 1


def _load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _uniq_limited(values: list[str], limit: int = 8) -> list[str]:
    seen = set()
    out = []
    for value in values:
        clean = _redact_evidence_line(" ".join(value.strip().split()))
        if not clean or clean in seen:
            continue
        seen.add(clean)
        out.append(clean)
        if len(out) >= limit:
            break
    return out


def _md_cell(value: Any) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def _redact_evidence_line(value: str) -> str:
    value = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip>", value)
    value = re.sub(r"(?<![\w.-])/(?:home|Users)/[^\s,'\")]+", "<path>", value)
    return value


def extract_backend_evidence(case_dir: Path) -> dict[str, list[str]]:
    logs = {
        "head": _load_text(case_dir / "serve_head.log"),
        "worker": _load_text(case_dir / "serve_worker.log"),
    }
    patterns = {
        "attention": (
            "FLASHINFER_MLA_SPARSE_DSV4",
            "FLASHMLA_SPARSE_DSV4",
            "Using DeepSeek's fp8_ds_mla KV cache format",
            "Using FP8 indexer cache for Lightning Indexer",
            "Warming up DeepSeek V4 sparse MLA attention",
        ),
        "moe": (
            "Mxfp4 MoE backend",
            "MoEPrepareAndFinalize",
            "FLASHINFER_CUTLASS_MXFP4",
            "FLASHINFER_TRTLLM_MXFP4",
        ),
        "nccl": (
            "vLLM is using nccl==",
            "PYNCCL",
            "Using ['PYNCCL'] all-reduce",
            "distributed_init_method=",
        ),
        "spec_decode": (
            "DeepSeekV4MTPModel",
            "num_speculative_tokens",
            "MTP draft model loaded",
            "Warming up DeepSeek V4 MTP",
        ),
    }
    evidence: dict[str, list[str]] = {}
    for name, needles in patterns.items():
        matches = []
        for node, text in logs.items():
            for line in text.splitlines():
                if any(needle in line for needle in needles):
                    matches.append(f"{node}: {line}")
        evidence[name] = _uniq_limited(matches)
    return evidence


def attention_marker_present(case_dir: Path, marker: str) -> bool:
    if not marker:
        return True
    logs = (
        _load_text(case_dir / "serve_head.log"),
        _load_text(case_dir / "serve_worker.log"),
    )
    return any(marker in text for text in logs)


def _overlap_ratio(sparse: dict[str, Any], region: str, group_size: str = "16") -> Any:
    overlap = sparse.get("candidate_overlap", {})
    if not isinstance(overlap, dict):
        return "n/a"
    if region == "all":
        groups = overlap.get("groups", {})
    else:
        regions = overlap.get("regions", {})
        groups = regions.get(region, {}) if isinstance(regions, dict) else {}
    if not isinstance(groups, dict):
        return "n/a"
    values = groups.get(group_size)
    if not isinstance(values, dict):
        return "n/a"
    return values.get("unique_to_valid_ratio", "n/a")


def _reuse_ratio(sparse: dict[str, Any], region: str, group_size: str = "16") -> Any:
    reuse = sparse.get("cross_query_reuse_potential", {})
    if not isinstance(reuse, dict):
        return "n/a"
    regions = reuse.get("regions", {})
    if not isinstance(regions, dict):
        return "n/a"
    groups = regions.get(region, {})
    if not isinstance(groups, dict):
        return "n/a"
    values = groups.get(group_size)
    if not isinstance(values, dict):
        return "n/a"
    return values.get("sampled_reuse_ratio", "n/a")


rows = []
for case_dir in case_dirs:
    metadata = _load_json(case_dir / "case_metadata.json", {})
    bench_summary = _load_json(case_dir / "prefill_sweep_summary.json", {})
    sparse_summary = _load_json(case_dir / "sparse_mla_stats_summary.json", {})
    backend_evidence = extract_backend_evidence(case_dir)
    expected_attention_marker = metadata.get("expected_attention_marker", "")
    attention_backend_match = attention_marker_present(
        case_dir, expected_attention_marker
    )
    start_exit = _read_exit(case_dir / "serve_start.exit_code")
    bench_exit = _read_exit(case_dir / "prefill_sweep.exit_code")
    rows.append(
        {
            "case": case_dir.name,
            "profile": metadata.get("profile", "unknown"),
            "profile_description": metadata.get("profile_description", ""),
            "prefix_cache_mode": metadata.get("prefix_cache_mode", "unknown"),
            "variant": metadata.get("variant", "unknown"),
            "input_len": metadata.get("input_len"),
            "output_len": metadata.get("output_len"),
            "max_num_batched_tokens": metadata.get("max_num_batched_tokens"),
            "serve_extra_args": metadata.get("serve_extra_args", ""),
            "expected_attention_marker": expected_attention_marker,
            "attention_backend_match": attention_backend_match,
            "artifact_dir": str(case_dir),
            "serve_start_exit_code": start_exit,
            "prefill_sweep_exit_code": bench_exit,
            "ok": start_exit == 0
            and bench_exit == 0
            and bool(bench_summary.get("ok"))
            and sparse_summary.get("row_count", 0) > 0
            and attention_backend_match,
            "bench_rows": bench_summary.get("rows", []),
            "backend_evidence": backend_evidence,
            "sparse_mla": {
                "row_count": sparse_summary.get("row_count", 0),
                "candidate_work": sparse_summary.get("candidate_work", {}),
                "candidate_region_work": sparse_summary.get(
                    "candidate_region_work", {}
                ),
                "stage_timings_ms": sparse_summary.get("stage_timings_ms", {}),
                "stage_efficiency": sparse_summary.get("stage_efficiency", {}),
                "candidate_overlap": sparse_summary.get("candidate_overlap", {}),
                "cross_query_reuse_potential": sparse_summary.get("cross_query_reuse_potential", {}),
                "candidate_row_duplicates": sparse_summary.get("candidate_row_duplicates", {}),
                "groups": sparse_summary.get("groups", []),
            },
        }
    )

summary = {
    "case": "gb10_prefill_gap_attribution",
    "ok": all(row["ok"] for row in rows),
    "rows": rows,
}
root.mkdir(parents=True, exist_ok=True)
(root / "gb10_prefill_gap_attribution_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

lines = [
    "# GB10 Prefill Gap Attribution",
    "",
    f"- OK: `{summary['ok']}`",
    "",
    "| Profile | Prefix cache | Variant | ISL | OSL | Max batched | OK | Backend marker | Backend match | C | Input tok/s | Decode tok/s | Mean TTFT ms | P95 TTFT ms | P99 TTFT ms | P95 ITL ms | P99 ITL ms | Sparse rows | Candidate slots | Effective visits | Padding ratio | Compressed effective visits | Compressed padding ratio | SWA effective visits | SWA padding ratio | All group16 unique/valid | Compressed group16 unique/valid | SWA group16 unique/valid | All group16 reuse | Compressed group16 reuse | SWA group16 reuse | Stage total ms | Dominant stage | Accumulate ratio | Sparse visits/s | Sparse ms/Mvisit | Attention evidence | MoE evidence | NCCL/all-reduce evidence |",
    "| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- | --- | --- |",
]
for row in rows:
    sparse = row.get("sparse_mla", {})
    work = sparse.get("candidate_work", {})
    region_work = sparse.get("candidate_region_work", {})
    compressed_work = (
        region_work.get("compressed", {}) if isinstance(region_work, dict) else {}
    )
    swa_work = region_work.get("swa", {}) if isinstance(region_work, dict) else {}
    timings = sparse.get("stage_timings_ms", {})
    efficiency = sparse.get("stage_efficiency", {})
    timing_stages = timings.get("stages", {}) if isinstance(timings, dict) else {}
    sparse_accumulate = (
        timing_stages.get("sparse_accumulate", {})
        if isinstance(timing_stages, dict)
        else {}
    )
    bench_rows = row.get("bench_rows") or [{}]
    for bench_row in bench_rows:
        evidence = row.get("backend_evidence", {})
        lines.append(
            "| {profile} | {prefix_cache} | {variant} | {input_len} | {output_len} | {max_batched} | {ok} | {expected_attention_marker} | {attention_backend_match} | {concurrency} | {input_tps} | {decode_tps} | {mean_ttft} | {p95_ttft} | {p99_ttft} | {p95_itl} | {p99_itl} | {sparse_rows} | {slots} | {effective} | {padding} | {compressed_effective} | {compressed_padding} | {swa_effective} | {swa_padding} | {overlap_all_g16} | {overlap_compressed_g16} | {overlap_swa_g16} | {reuse_all_g16} | {reuse_compressed_g16} | {reuse_swa_g16} | {stage_total} | {dominant_stage} | {accumulate_ratio} | {sparse_visits_per_s} | {sparse_ms_per_mvisit} | {attention_evidence} | {moe_evidence} | {nccl_evidence} |".format(
                profile=f"`{row.get('profile')}`",
                prefix_cache=f"`{row.get('prefix_cache_mode')}`",
                variant=f"`{row.get('variant')}`",
                input_len=row.get("input_len", "n/a"),
                output_len=row.get("output_len", "n/a"),
                max_batched=row.get("max_num_batched_tokens", "n/a"),
                ok="yes" if row.get("ok") else "no",
                expected_attention_marker=f"`{row.get('expected_attention_marker')}`"
                if row.get("expected_attention_marker")
                else "n/a",
                attention_backend_match="yes"
                if row.get("attention_backend_match")
                else "no",
                concurrency=bench_row.get("concurrency", "n/a"),
                input_tps=bench_row.get("input_token_throughput_tok_s", "n/a"),
                decode_tps=bench_row.get("output_token_throughput_tok_s", "n/a"),
                mean_ttft=bench_row.get("mean_ttft_ms", "n/a"),
                p95_ttft=bench_row.get("p95_ttft_ms", "n/a"),
                p99_ttft=bench_row.get("p99_ttft_ms", "n/a"),
                p95_itl=bench_row.get("p95_itl_ms", "n/a"),
                p99_itl=bench_row.get("p99_itl_ms", "n/a"),
                sparse_rows=sparse.get("row_count", "n/a"),
                slots=work.get("candidate_slots", "n/a"),
                effective=work.get("effective_candidate_visits", "n/a"),
                padding=work.get("padding_ratio", "n/a"),
                compressed_effective=compressed_work.get(
                    "effective_candidate_visits", "n/a"
                )
                if isinstance(compressed_work, dict)
                else "n/a",
                compressed_padding=compressed_work.get("padding_ratio", "n/a")
                if isinstance(compressed_work, dict)
                else "n/a",
                swa_effective=swa_work.get("effective_candidate_visits", "n/a")
                if isinstance(swa_work, dict)
                else "n/a",
                swa_padding=swa_work.get("padding_ratio", "n/a")
                if isinstance(swa_work, dict)
                else "n/a",
                overlap_all_g16=_overlap_ratio(sparse, "all"),
                overlap_compressed_g16=_overlap_ratio(sparse, "compressed"),
                overlap_swa_g16=_overlap_ratio(sparse, "swa"),
                reuse_all_g16=_reuse_ratio(sparse, "all"),
                reuse_compressed_g16=_reuse_ratio(sparse, "compressed"),
                reuse_swa_g16=_reuse_ratio(sparse, "swa"),
                stage_total=timings.get("total", "n/a")
                if isinstance(timings, dict)
                else "n/a",
                dominant_stage=timings.get("dominant_stage", "n/a")
                if isinstance(timings, dict)
                else "n/a",
                accumulate_ratio=sparse_accumulate.get("ratio", "n/a")
                if isinstance(sparse_accumulate, dict)
                else "n/a",
                sparse_visits_per_s=efficiency.get(
                    "sparse_accumulate_effective_candidate_visits_per_s",
                    "n/a",
                )
                if isinstance(efficiency, dict)
                else "n/a",
                sparse_ms_per_mvisit=efficiency.get(
                    "sparse_accumulate_ms_per_million_effective_visits",
                    "n/a",
                )
                if isinstance(efficiency, dict)
                else "n/a",
                attention_evidence=_md_cell("<br>".join(
                    evidence.get("attention", [])[:2]
                ))
                or "n/a",
                moe_evidence=_md_cell("<br>".join(evidence.get("moe", [])[:2]))
                or "n/a",
                nccl_evidence=_md_cell("<br>".join(evidence.get("nccl", [])[:2]))
                or "n/a",
            )
        )
(root / "gb10_prefill_gap_attribution_summary.md").write_text(
    "\n".join(lines).rstrip() + "\n",
    encoding="utf-8",
)
PY

printf '%s\n' "${failures}" > "${OUT_DIR}/gb10_prefill_gap_attribution.exit_code"
echo "wrote ${OUT_DIR}"
exit "${failures}"
