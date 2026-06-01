#!/usr/bin/env bash
# Run the fixed SM12x C=2 fairness + prefill/decode interference protocol.
#
# This protocol intentionally keeps two signals together:
#   1. C=2 long-context fairness metrics from normal harness phases.
#   2. Nsight Systems traces for the same serve profile and representative
#      prefill/decode interference cases.
#
# The first phase launches vLLM through run_b200_baseline.sh. The second phase
# reuses the generated serve_command.sh, so the profile trace cannot silently
# drift from the fairness matrix.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8080}"
B200_VLLM_REPO="${B200_VLLM_REPO:-/workspace/vllm}"
B200_VLLM_VENV="${B200_VLLM_VENV:-${B200_VLLM_REPO}/.venv}"
PYTHON="${PYTHON:-${B200_VLLM_VENV}/bin/python}"
VLLM_BIN="${VLLM_BIN:-${B200_VLLM_VENV}/bin/vllm}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
SM12X_C2_PROTOCOL_LABEL="${SM12X_C2_PROTOCOL_LABEL:-sm12x_c2_fairness_interference_protocol}"
SM12X_C2_PROTOCOL_ROOT="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${SM12X_C2_PROTOCOL_LABEL}/${RUN_TIMESTAMP}}"

SM12X_C2_RUN_FAIRNESS="${SM12X_C2_RUN_FAIRNESS:-1}"
SM12X_C2_RUN_NSYS="${SM12X_C2_RUN_NSYS:-1}"
SM12X_C2_VARIANT="${SM12X_C2_VARIANT:-mtp}"
SM12X_C2_FAIRNESS_OUT_DIR="${SM12X_C2_FAIRNESS_OUT_DIR:-${SM12X_C2_PROTOCOL_ROOT}/fairness_matrix}"
SM12X_C2_NSYS_OUT_DIR="${SM12X_C2_NSYS_OUT_DIR:-${SM12X_C2_PROTOCOL_ROOT}/interference_profiles}"

SM12X_C2_GPU_MEMORY_UTILIZATION="${SM12X_C2_GPU_MEMORY_UTILIZATION:-0.975}"
SM12X_C2_MAX_NUM_BATCHED_TOKENS="${SM12X_C2_MAX_NUM_BATCHED_TOKENS:-4096}"
SM12X_C2_MAX_NUM_SEQS="${SM12X_C2_MAX_NUM_SEQS:-4}"
_DEFAULT_SM12X_C2_EXTRA_SERVE_ARGS="--gpu-memory-utilization ${SM12X_C2_GPU_MEMORY_UTILIZATION} --max-num-batched-tokens ${SM12X_C2_MAX_NUM_BATCHED_TOKENS} --max-num-seqs ${SM12X_C2_MAX_NUM_SEQS} --enable-expert-parallel --compilation-config '{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}'"
B200_EXTRA_SERVE_ARGS="${B200_EXTRA_SERVE_ARGS:-${_DEFAULT_SM12X_C2_EXTRA_SERVE_ARGS}}"

SM12X_C2_FAIRNESS_PHASES="${SM12X_C2_FAIRNESS_PHASES:-long_context_latency_matrix,long_context_decode_concurrency,long_context_mixed_arrival}"
SM12X_C2_LINE_COUNTS="${SM12X_C2_LINE_COUNTS:-1900,4000}"
SM12X_C2_CONCURRENCY="${SM12X_C2_CONCURRENCY:-1,2}"
SM12X_C2_REPEAT_COUNT="${SM12X_C2_REPEAT_COUNT:-3}"
SM12X_C2_LATENCY_MAX_TOKENS="${SM12X_C2_LATENCY_MAX_TOKENS:-64}"
SM12X_C2_DECODE_MAX_TOKENS="${SM12X_C2_DECODE_MAX_TOKENS:-256}"
SM12X_C2_MIXED_ARRIVAL_CASE_SPECS="${SM12X_C2_MIXED_ARRIVAL_CASE_SPECS:-long_long_c2:4000:4000:fixed_delay:0:128:128,decode_then_59k:1900:1900:after_first_token:0:256:128,decode_then_124k:4000:4000:after_first_token:0:256:128,long_decode_then_short:4000:192:after_first_token:0:256:64,short_decode_then_124k:192:4000:after_first_token:0:256:128,long_then_short:4000:192:fixed_delay:2:128:64}"
SM12X_C2_NSYS_CASE_SPECS="${SM12X_C2_NSYS_CASE_SPECS:-long_long_c2:4000:4000:fixed_delay:0:128:128;decode_then_59k:1900:1900:after_first_token:0:256:128;decode_then_124k:4000:4000:after_first_token:0:256:128;long_decode_then_short:4000:192:after_first_token:0:256:64;short_decode_then_124k:192:4000:after_first_token:0:256:128;long_then_short:4000:192:fixed_delay:2:128:64}"
SM12X_C2_PROFILE_REPEAT_COUNT="${SM12X_C2_PROFILE_REPEAT_COUNT:-1}"
SM12X_C2_PROFILE_PREWARM="${SM12X_C2_PROFILE_PREWARM:-1}"
NSYS_CAPTURE_MODE="${NSYS_CAPTURE_MODE:-bench_window}"

mkdir -p "${SM12X_C2_PROTOCOL_ROOT}"

failures=0
run_child() {
  local child_out="$1"
  shift

  mkdir -p "${child_out}"
  set +e
  "$@" >"${child_out}/child.stdout.log" 2>"${child_out}/child.stderr.log"
  local code="$?"
  set -e
  printf '%s\n' "${code}" > "${child_out}/child.exit_code"
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi
}

case "${SM12X_C2_VARIANT}" in
  *","*|*" "*)
    echo "SM12X_C2_VARIANT must be a single baseline variant; got '${SM12X_C2_VARIANT}'" >&2
    exit 2
    ;;
esac

if [[ "${SM12X_C2_RUN_FAIRNESS}" == "1" || "${SM12X_C2_RUN_FAIRNESS}" == "true" ]]; then
  run_child "${SM12X_C2_FAIRNESS_OUT_DIR}" env \
    OUT_DIR="${SM12X_C2_FAIRNESS_OUT_DIR}" \
    MODEL="${MODEL}" HOST="${HOST}" PORT="${PORT}" \
    B200_VLLM_REPO="${B200_VLLM_REPO}" B200_VLLM_VENV="${B200_VLLM_VENV}" \
    PYTHON="${PYTHON}" VLLM_BIN="${VLLM_BIN}" \
    B200_BASELINE_LABEL="${SM12X_C2_PROTOCOL_LABEL}_fairness" \
    ARTIFACT_ARCHIVE_PREVIOUS=0 \
    B200_BASELINE_VARIANTS="${SM12X_C2_VARIANT}" \
    B200_BASELINE_PHASES="${SM12X_C2_FAIRNESS_PHASES}" \
    B200_TENSOR_PARALLEL_SIZE="${B200_TENSOR_PARALLEL_SIZE:-2}" \
    B200_BLOCK_SIZE="${B200_BLOCK_SIZE:-256}" \
    B200_KV_CACHE_DTYPE="${B200_KV_CACHE_DTYPE:-fp8}" \
    SERVE_MAX_MODEL_LEN="${SERVE_MAX_MODEL_LEN:-131072}" \
    SERVE_PREFIX_CACHE_MODE="${SERVE_PREFIX_CACHE_MODE:-disabled}" \
    SERVE_USE_FP4_INDEXER_CACHE="${SERVE_USE_FP4_INDEXER_CACHE:-0}" \
    B200_EXTRA_SERVE_ARGS="${B200_EXTRA_SERVE_ARGS}" \
    LONG_CONTEXT_LATENCY_CASE_NAME="${LONG_CONTEXT_LATENCY_CASE_NAME:-sm12x_c2_latency_fairness}" \
    LONG_CONTEXT_LATENCY_LINE_COUNTS="${LONG_CONTEXT_LATENCY_LINE_COUNTS:-${SM12X_C2_LINE_COUNTS}}" \
    LONG_CONTEXT_LATENCY_CONCURRENCY="${LONG_CONTEXT_LATENCY_CONCURRENCY:-${SM12X_C2_CONCURRENCY}}" \
    LONG_CONTEXT_LATENCY_CACHE_MODES="${LONG_CONTEXT_LATENCY_CACHE_MODES:-cold}" \
    LONG_CONTEXT_LATENCY_REPEAT_COUNT="${LONG_CONTEXT_LATENCY_REPEAT_COUNT:-${SM12X_C2_REPEAT_COUNT}}" \
    LONG_CONTEXT_LATENCY_MAX_TOKENS="${LONG_CONTEXT_LATENCY_MAX_TOKENS:-${SM12X_C2_LATENCY_MAX_TOKENS}}" \
    LONG_CONTEXT_LATENCY_PREWARM="${LONG_CONTEXT_LATENCY_PREWARM:-1}" \
    RUN_LONG_CONTEXT_DECODE_CONCURRENCY=1 \
    LONG_CONTEXT_DECODE_CASE_NAME="${LONG_CONTEXT_DECODE_CASE_NAME:-sm12x_c2_decode_fairness}" \
    LONG_CONTEXT_DECODE_LINE_COUNTS="${LONG_CONTEXT_DECODE_LINE_COUNTS:-4000}" \
    LONG_CONTEXT_DECODE_CONCURRENCY="${LONG_CONTEXT_DECODE_CONCURRENCY:-${SM12X_C2_CONCURRENCY}}" \
    LONG_CONTEXT_DECODE_CACHE_MODES="${LONG_CONTEXT_DECODE_CACHE_MODES:-cold}" \
    LONG_CONTEXT_DECODE_REPEAT_COUNT="${LONG_CONTEXT_DECODE_REPEAT_COUNT:-1}" \
    LONG_CONTEXT_DECODE_MAX_TOKENS="${LONG_CONTEXT_DECODE_MAX_TOKENS:-${SM12X_C2_DECODE_MAX_TOKENS}}" \
    LONG_CONTEXT_DECODE_PREWARM="${LONG_CONTEXT_DECODE_PREWARM:-1}" \
    RUN_LONG_CONTEXT_MIXED_ARRIVAL=1 \
    LONG_CONTEXT_MIXED_ARRIVAL_CASE_NAME="${LONG_CONTEXT_MIXED_ARRIVAL_CASE_NAME:-sm12x_c2_prefill_decode_interference}" \
    LONG_CONTEXT_MIXED_ARRIVAL_CASE_SPECS="${LONG_CONTEXT_MIXED_ARRIVAL_CASE_SPECS:-${SM12X_C2_MIXED_ARRIVAL_CASE_SPECS}}" \
    LONG_CONTEXT_MIXED_ARRIVAL_REPEAT_COUNT="${LONG_CONTEXT_MIXED_ARRIVAL_REPEAT_COUNT:-${SM12X_C2_REPEAT_COUNT}}" \
    "${SCRIPT_DIR}/run_b200_baseline.sh"
fi

serve_command_file="${SM12X_C2_FAIRNESS_OUT_DIR}/${SM12X_C2_VARIANT}/serve_command.sh"
if [[ "${SM12X_C2_RUN_NSYS}" == "1" || "${SM12X_C2_RUN_NSYS}" == "true" ]]; then
  if [[ -z "${SERVE_COMMAND:-}" ]]; then
    if [[ ! -f "${serve_command_file}" ]]; then
      echo "SERVE_COMMAND is unset and serve command file is missing: ${serve_command_file}" >&2
      exit 2
    fi
    printf -v SERVE_COMMAND 'bash %q' "${serve_command_file}"
  fi

  run_child "${SM12X_C2_NSYS_OUT_DIR}" env \
    OUT_DIR="${SM12X_C2_NSYS_OUT_DIR}" \
    PYTHON="${PYTHON}" \
    VLLM_VENV="${B200_VLLM_VENV}" \
    NSYS_BIN="${NSYS_BIN:-nsys}" \
    SERVE_COMMAND="${SERVE_COMMAND}" \
    BASE_URL="http://${HOST}:${PORT}" \
    PROFILE_MODEL="${MODEL}" \
    PREFILL_DECODE_PROFILE_LABEL="${SM12X_C2_PROTOCOL_LABEL}_nsys" \
    PREFILL_DECODE_PROFILE_CASE_SPECS="${SM12X_C2_NSYS_CASE_SPECS}" \
    PROFILE_REPEAT_COUNT="${SM12X_C2_PROFILE_REPEAT_COUNT}" \
    PROFILE_PREWARM="${SM12X_C2_PROFILE_PREWARM}" \
    NSYS_CAPTURE_MODE="${NSYS_CAPTURE_MODE}" \
    "${SCRIPT_DIR}/run_sm12x_prefill_decode_interference_profiles.sh"
fi

SM12X_C2_PROTOCOL_ROOT="${SM12X_C2_PROTOCOL_ROOT}" \
SM12X_C2_PROTOCOL_LABEL="${SM12X_C2_PROTOCOL_LABEL}" \
SM12X_C2_FAIRNESS_OUT_DIR="${SM12X_C2_FAIRNESS_OUT_DIR}" \
SM12X_C2_NSYS_OUT_DIR="${SM12X_C2_NSYS_OUT_DIR}" \
"${PYTHON}" - <<'PYEOF'
import json
import os
from pathlib import Path


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


root = Path(os.environ["SM12X_C2_PROTOCOL_ROOT"])
label = os.environ["SM12X_C2_PROTOCOL_LABEL"]
fairness_dir = Path(os.environ["SM12X_C2_FAIRNESS_OUT_DIR"])
nsys_dir = Path(os.environ["SM12X_C2_NSYS_OUT_DIR"])
phase_exit_codes = _read_text(fairness_dir / "phase_exit_codes.tsv")
nsys_summary = _read_json(
    nsys_dir / "prefill_decode_interference_profiles_summary.json"
)

payload = {
    "label": label,
    "fairness_dir": str(fairness_dir),
    "nsys_dir": str(nsys_dir),
    "phase_exit_codes": [
        line.split("\t")
        for line in phase_exit_codes.splitlines()
        if line.strip()
    ],
    "nsys_summary": nsys_summary,
}
(root / "c2_fairness_interference_protocol_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

lines = [
    "# SM12x C=2 Fairness And Interference Protocol",
    "",
    f"Label: `{label}`",
    "",
    f"- fairness matrix: `{fairness_dir}`",
    f"- interference profiles: `{nsys_dir}`",
    "",
    "## Phase Exit Codes",
    "",
    "| Variant | Phase | Exit |",
    "| --- | --- | ---: |",
]
for row in payload["phase_exit_codes"]:
    if len(row) >= 3:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} |")
if not payload["phase_exit_codes"]:
    lines.append("| missing | missing |  |")

lines.extend(["", "## Interference Cases", ""])
if isinstance(nsys_summary, dict):
    lines.extend(
        [
            "| Case | Exit | Requests | Decode Min/Max | ITL P99 | Top Kernel |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for case in nsys_summary.get("cases", []):
        summary = (case.get("summary") or [{}])[0]
        kernels = case.get("top_kernels") or []
        top_kernel = kernels[0].get("kernel", "") if kernels else ""
        if len(top_kernel) > 72:
            top_kernel = top_kernel[:69] + "..."
        lines.append(
            "| {case} | {exit_code} | {requests} | {ratio} | {itl_p99} | `{kernel}` |".format(
                case=case.get("case"),
                exit_code=case.get("exit_code"),
                requests=case.get("request_count"),
                ratio=summary.get("decode_tps_min_to_max_ratio"),
                itl_p99=summary.get("p99_inter_chunk_seconds"),
                kernel=top_kernel,
            )
        )
else:
    lines.append("Interference summary is missing or unparsable.")
lines.append("")
(root / "c2_fairness_interference_protocol_summary.md").write_text(
    "\n".join(lines),
    encoding="utf-8",
)
PYEOF

echo "wrote ${SM12X_C2_PROTOCOL_ROOT}"
exit "${failures}"
