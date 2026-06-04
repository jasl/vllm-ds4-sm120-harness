#!/usr/bin/env bash
# Run the lightweight SM12x prefill/decode fairness promotion gate.
#
# This gate is intended for routine no-regression checks after vLLM inference
# experiments. It reuses the existing baseline phases and does not collect Nsys
# traces; use run_sm12x_c2_fairness_interference_protocol.sh when profiling is
# needed.

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
SM12X_PREFILL_DECODE_LABEL="${SM12X_PREFILL_DECODE_LABEL:-sm12x_prefill_decode_promotion_gate}"
SM12X_PREFILL_DECODE_ROOT="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${SM12X_PREFILL_DECODE_LABEL}/${RUN_TIMESTAMP}}"
SM12X_PREFILL_DECODE_BASELINE_DIR="${SM12X_PREFILL_DECODE_BASELINE_DIR:-${SM12X_PREFILL_DECODE_ROOT}/baseline}"

SM12X_PREFILL_DECODE_VARIANT="${SM12X_PREFILL_DECODE_VARIANT:-mtp}"
SM12X_PREFILL_DECODE_PHASES="${SM12X_PREFILL_DECODE_PHASES:-long_context_latency_matrix,long_context_decode_concurrency,long_context_mixed_arrival,streaming_pressure_matrix}"
SM12X_PREFILL_DECODE_GPU_MEMORY_UTILIZATION="${SM12X_PREFILL_DECODE_GPU_MEMORY_UTILIZATION:-0.975}"
SM12X_PREFILL_DECODE_MAX_NUM_BATCHED_TOKENS="${SM12X_PREFILL_DECODE_MAX_NUM_BATCHED_TOKENS:-4096}"
SM12X_PREFILL_DECODE_MAX_NUM_SEQS="${SM12X_PREFILL_DECODE_MAX_NUM_SEQS:-4}"
SM12X_PREFILL_DECODE_MAX_MODEL_LEN="${SM12X_PREFILL_DECODE_MAX_MODEL_LEN:-131072}"
_DEFAULT_SM12X_PREFILL_DECODE_EXTRA_SERVE_ARGS="--gpu-memory-utilization ${SM12X_PREFILL_DECODE_GPU_MEMORY_UTILIZATION} --max-num-batched-tokens ${SM12X_PREFILL_DECODE_MAX_NUM_BATCHED_TOKENS} --max-num-seqs ${SM12X_PREFILL_DECODE_MAX_NUM_SEQS} --enable-expert-parallel --compilation-config '{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}'"
B200_EXTRA_SERVE_ARGS="${B200_EXTRA_SERVE_ARGS:-${_DEFAULT_SM12X_PREFILL_DECODE_EXTRA_SERVE_ARGS}}"

SM12X_PREFILL_DECODE_LINE_COUNTS="${SM12X_PREFILL_DECODE_LINE_COUNTS:-1900,4000}"
SM12X_PREFILL_DECODE_CONCURRENCY="${SM12X_PREFILL_DECODE_CONCURRENCY:-1,2}"
SM12X_PREFILL_DECODE_REPEAT_COUNT="${SM12X_PREFILL_DECODE_REPEAT_COUNT:-3}"
SM12X_PREFILL_DECODE_LATENCY_MAX_TOKENS="${SM12X_PREFILL_DECODE_LATENCY_MAX_TOKENS:-64}"
SM12X_PREFILL_DECODE_DECODE_LINE_COUNTS="${SM12X_PREFILL_DECODE_DECODE_LINE_COUNTS:-4000}"
SM12X_PREFILL_DECODE_DECODE_MAX_TOKENS="${SM12X_PREFILL_DECODE_DECODE_MAX_TOKENS:-256}"
SM12X_PREFILL_DECODE_MIXED_CASE_SPECS="${SM12X_PREFILL_DECODE_MIXED_CASE_SPECS:-long_long_c2:4000:4000:fixed_delay:0:128:128,decode_then_59k:1900:1900:after_first_token:0:256:128,decode_then_124k:4000:4000:after_first_token:0:256:128,long_decode_then_short:4000:192:after_first_token:0:256:64,short_decode_then_124k:192:4000:after_first_token:0:256:128,long_then_short:4000:192:fixed_delay:2:128:64}"
SM12X_PREFILL_DECODE_STREAMING_CASE_SPECS="${SM12X_PREFILL_DECODE_STREAMING_CASE_SPECS:-short_c4:4:3:1200:128,issue7_5k_c4:4:3:192:128,long_c2:2:2:4000:128,long_c4:4:2:2400:128}"
SM12X_PREFILL_DECODE_STREAMING_FAIL_ON_SLOW="${SM12X_PREFILL_DECODE_STREAMING_FAIL_ON_SLOW:-0}"
PREFILL_DECODE_GATE_MIN_LONG_C2_DECODE_MIN_MAX_RATIO="${PREFILL_DECODE_GATE_MIN_LONG_C2_DECODE_MIN_MAX_RATIO:-0.5}"
PREFILL_DECODE_GATE_MAX_LONG_C2_ITL_P99_SECONDS="${PREFILL_DECODE_GATE_MAX_LONG_C2_ITL_P99_SECONDS:-1.0}"
PREFILL_DECODE_GATE_MAX_MIXED_SECONDARY_ITL_P99_SECONDS="${PREFILL_DECODE_GATE_MAX_MIXED_SECONDARY_ITL_P99_SECONDS:-1.0}"
PREFILL_DECODE_GATE_MAX_STREAMING_ITL_P99_SECONDS="${PREFILL_DECODE_GATE_MAX_STREAMING_ITL_P99_SECONDS:-2.0}"

case "${SM12X_PREFILL_DECODE_VARIANT}" in
  *","*|*" "*)
    echo "SM12X_PREFILL_DECODE_VARIANT must be a single baseline variant; got '${SM12X_PREFILL_DECODE_VARIANT}'" >&2
    exit 2
    ;;
esac

mkdir -p "${SM12X_PREFILL_DECODE_ROOT}" "${SM12X_PREFILL_DECODE_BASELINE_DIR}"

set +e
env \
  OUT_DIR="${SM12X_PREFILL_DECODE_BASELINE_DIR}" \
  MODEL="${MODEL}" HOST="${HOST}" PORT="${PORT}" \
  B200_VLLM_REPO="${B200_VLLM_REPO}" B200_VLLM_VENV="${B200_VLLM_VENV}" \
  PYTHON="${PYTHON}" VLLM_BIN="${VLLM_BIN}" \
  B200_BASELINE_LABEL="${SM12X_PREFILL_DECODE_LABEL}_baseline" \
  ARTIFACT_ARCHIVE_PREVIOUS=0 \
  B200_BASELINE_VARIANTS="${SM12X_PREFILL_DECODE_VARIANT}" \
  B200_BASELINE_PHASES="${SM12X_PREFILL_DECODE_PHASES}" \
  B200_TENSOR_PARALLEL_SIZE="${B200_TENSOR_PARALLEL_SIZE:-2}" \
  B200_BLOCK_SIZE="${B200_BLOCK_SIZE:-256}" \
  B200_KV_CACHE_DTYPE="${B200_KV_CACHE_DTYPE:-fp8}" \
  SERVE_MAX_MODEL_LEN="${SERVE_MAX_MODEL_LEN:-${SM12X_PREFILL_DECODE_MAX_MODEL_LEN}}" \
  SERVE_PREFIX_CACHE_MODE="${SERVE_PREFIX_CACHE_MODE:-disabled}" \
  SERVE_USE_FP4_INDEXER_CACHE="${SERVE_USE_FP4_INDEXER_CACHE:-0}" \
  B200_EXTRA_SERVE_ARGS="${B200_EXTRA_SERVE_ARGS}" \
  RUN_LONG_CONTEXT_LATENCY_MATRIX=1 \
  LONG_CONTEXT_LATENCY_CASE_NAME="${LONG_CONTEXT_LATENCY_CASE_NAME:-sm12x_prefill_decode_latency_fairness}" \
  LONG_CONTEXT_LATENCY_LINE_COUNTS="${LONG_CONTEXT_LATENCY_LINE_COUNTS:-${SM12X_PREFILL_DECODE_LINE_COUNTS}}" \
  LONG_CONTEXT_LATENCY_CONCURRENCY="${LONG_CONTEXT_LATENCY_CONCURRENCY:-${SM12X_PREFILL_DECODE_CONCURRENCY}}" \
  LONG_CONTEXT_LATENCY_CACHE_MODES="${LONG_CONTEXT_LATENCY_CACHE_MODES:-cold}" \
  LONG_CONTEXT_LATENCY_REPEAT_COUNT="${LONG_CONTEXT_LATENCY_REPEAT_COUNT:-${SM12X_PREFILL_DECODE_REPEAT_COUNT}}" \
  LONG_CONTEXT_LATENCY_MAX_TOKENS="${LONG_CONTEXT_LATENCY_MAX_TOKENS:-${SM12X_PREFILL_DECODE_LATENCY_MAX_TOKENS}}" \
  LONG_CONTEXT_LATENCY_PREWARM="${LONG_CONTEXT_LATENCY_PREWARM:-1}" \
  RUN_LONG_CONTEXT_DECODE_CONCURRENCY=1 \
  LONG_CONTEXT_DECODE_CASE_NAME="${LONG_CONTEXT_DECODE_CASE_NAME:-sm12x_prefill_decode_decode_fairness}" \
  LONG_CONTEXT_DECODE_LINE_COUNTS="${LONG_CONTEXT_DECODE_LINE_COUNTS:-${SM12X_PREFILL_DECODE_DECODE_LINE_COUNTS}}" \
  LONG_CONTEXT_DECODE_CONCURRENCY="${LONG_CONTEXT_DECODE_CONCURRENCY:-${SM12X_PREFILL_DECODE_CONCURRENCY}}" \
  LONG_CONTEXT_DECODE_CACHE_MODES="${LONG_CONTEXT_DECODE_CACHE_MODES:-cold}" \
  LONG_CONTEXT_DECODE_REPEAT_COUNT="${LONG_CONTEXT_DECODE_REPEAT_COUNT:-1}" \
  LONG_CONTEXT_DECODE_MAX_TOKENS="${LONG_CONTEXT_DECODE_MAX_TOKENS:-${SM12X_PREFILL_DECODE_DECODE_MAX_TOKENS}}" \
  LONG_CONTEXT_DECODE_PREWARM="${LONG_CONTEXT_DECODE_PREWARM:-1}" \
  RUN_LONG_CONTEXT_MIXED_ARRIVAL=1 \
  LONG_CONTEXT_MIXED_ARRIVAL_CASE_NAME="${LONG_CONTEXT_MIXED_ARRIVAL_CASE_NAME:-sm12x_prefill_decode_interference}" \
  LONG_CONTEXT_MIXED_ARRIVAL_CASE_SPECS="${LONG_CONTEXT_MIXED_ARRIVAL_CASE_SPECS:-${SM12X_PREFILL_DECODE_MIXED_CASE_SPECS}}" \
  LONG_CONTEXT_MIXED_ARRIVAL_REPEAT_COUNT="${LONG_CONTEXT_MIXED_ARRIVAL_REPEAT_COUNT:-${SM12X_PREFILL_DECODE_REPEAT_COUNT}}" \
  RUN_STREAMING_PRESSURE_MATRIX=1 \
  STREAMING_PRESSURE_MATRIX_CASE_NAME="${STREAMING_PRESSURE_MATRIX_CASE_NAME:-sm12x_prefill_decode_streaming_pressure}" \
  STREAMING_PRESSURE_MATRIX_CASE_SPECS="${STREAMING_PRESSURE_MATRIX_CASE_SPECS:-${SM12X_PREFILL_DECODE_STREAMING_CASE_SPECS}}" \
  STREAMING_PRESSURE_MATRIX_FAIL_ON_SLOW="${STREAMING_PRESSURE_MATRIX_FAIL_ON_SLOW:-${SM12X_PREFILL_DECODE_STREAMING_FAIL_ON_SLOW}}" \
  "${SCRIPT_DIR}/run_b200_baseline.sh" \
  >"${SM12X_PREFILL_DECODE_ROOT}/baseline.stdout.log" \
  2>"${SM12X_PREFILL_DECODE_ROOT}/baseline.stderr.log"
baseline_code="$?"
set -e
printf '%s\n' "${baseline_code}" > "${SM12X_PREFILL_DECODE_ROOT}/baseline.exit_code"

set +e
"${PYTHON}" -m ds4_harness.cli prefill-decode-gate \
  --baseline-dir "${SM12X_PREFILL_DECODE_BASELINE_DIR}" \
  --variant "${SM12X_PREFILL_DECODE_VARIANT}" \
  --min-long-c2-decode-min-max-ratio "${PREFILL_DECODE_GATE_MIN_LONG_C2_DECODE_MIN_MAX_RATIO}" \
  --max-long-c2-itl-p99-seconds "${PREFILL_DECODE_GATE_MAX_LONG_C2_ITL_P99_SECONDS}" \
  --max-mixed-secondary-itl-p99-seconds "${PREFILL_DECODE_GATE_MAX_MIXED_SECONDARY_ITL_P99_SECONDS}" \
  --max-streaming-itl-p99-seconds "${PREFILL_DECODE_GATE_MAX_STREAMING_ITL_P99_SECONDS}" \
  --json-output "${SM12X_PREFILL_DECODE_ROOT}/prefill_decode_regression_gate.json" \
  --markdown-output "${SM12X_PREFILL_DECODE_ROOT}/prefill_decode_regression_gate.md" \
  >"${SM12X_PREFILL_DECODE_ROOT}/prefill_decode_regression_gate.stdout.log" \
  2>"${SM12X_PREFILL_DECODE_ROOT}/prefill_decode_regression_gate.stderr.log"
gate_code="$?"
set -e
printf '%s\n' "${gate_code}" > "${SM12X_PREFILL_DECODE_ROOT}/prefill_decode_regression_gate.exit_code"

SM12X_PREFILL_DECODE_ROOT="${SM12X_PREFILL_DECODE_ROOT}" \
SM12X_PREFILL_DECODE_LABEL="${SM12X_PREFILL_DECODE_LABEL}" \
SM12X_PREFILL_DECODE_BASELINE_DIR="${SM12X_PREFILL_DECODE_BASELINE_DIR}" \
SM12X_PREFILL_DECODE_VARIANT="${SM12X_PREFILL_DECODE_VARIANT}" \
"${PYTHON}" - <<'PYEOF'
import json
import os
from pathlib import Path


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _read_exit(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return None


root = Path(os.environ["SM12X_PREFILL_DECODE_ROOT"])
label = os.environ["SM12X_PREFILL_DECODE_LABEL"]
baseline_dir = Path(os.environ["SM12X_PREFILL_DECODE_BASELINE_DIR"])
variant = os.environ["SM12X_PREFILL_DECODE_VARIANT"]
phase_rows = []
for line in _read_text(baseline_dir / "phase_exit_codes.tsv").splitlines():
    if not line.strip():
        continue
    columns = line.split("\t")
    if len(columns) >= 3:
        phase_rows.append(
            {
                "variant": columns[0],
                "phase": columns[1],
                "exit_code": columns[2],
            }
        )

variant_dir = baseline_dir / variant
phase_artifacts = {
    "long_context_latency_matrix": variant_dir / "long_context_latency_matrix",
    "long_context_decode_concurrency": variant_dir / "long_context_decode_concurrency",
    "long_context_mixed_arrival": variant_dir / "long_context_mixed_arrival",
    "streaming_pressure_matrix": variant_dir / "streaming_pressure_matrix",
}
payload = {
    "label": label,
    "baseline_dir": str(baseline_dir),
    "variant": variant,
    "baseline_exit_code": _read_exit(root / "baseline.exit_code"),
    "prefill_decode_regression_gate_exit_code": _read_exit(
        root / "prefill_decode_regression_gate.exit_code"
    ),
    "prefill_decode_regression_gate_json": str(
        root / "prefill_decode_regression_gate.json"
    ),
    "prefill_decode_regression_gate_markdown": str(
        root / "prefill_decode_regression_gate.md"
    ),
    "phase_exit_codes": phase_rows,
    "phase_artifacts": {
        name: str(path) for name, path in phase_artifacts.items()
    },
    "companion_gb10_gate": "scripts/run_gb10_long_c2_reduced_gate.sh",
}
(root / "prefill_decode_promotion_gate_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

lines = [
    "# SM12x Prefill/Decode Promotion Gate",
    "",
    f"Label: `{label}`",
    "",
    f"- baseline dir: `{baseline_dir}`",
    f"- variant: `{variant}`",
    f"- baseline exit: `{payload['baseline_exit_code']}`",
    "- prefill/decode regression gate exit: "
    f"`{payload['prefill_decode_regression_gate_exit_code']}`",
    "- prefill/decode regression gate: "
    f"`{payload['prefill_decode_regression_gate_markdown']}`",
    "- companion GB10 reduced long-C2 gate: "
    "`scripts/run_gb10_long_c2_reduced_gate.sh`",
    "",
    "## Phase Exit Codes",
    "",
    "| Variant | Phase | Exit | Artifact |",
    "| --- | --- | ---: | --- |",
]
artifact_by_phase = payload["phase_artifacts"]
for row in phase_rows:
    artifact = artifact_by_phase.get(row["phase"], "")
    lines.append(
        "| {variant} | {phase} | {exit_code} | `{artifact}` |".format(
            variant=row["variant"],
            phase=row["phase"],
            exit_code=row["exit_code"],
            artifact=artifact,
        )
    )
if not phase_rows:
    lines.append("| missing | missing |  |  |")
lines.extend(
    [
        "",
        "This gate is a functional and telemetry promotion check. Compare TTFT, "
        "decode min/max, and ITL p95/p99 against the current baseline before "
        "promoting a new prefill or scheduler experiment.",
        "",
    ]
)
(root / "prefill_decode_promotion_gate_summary.md").write_text(
    "\n".join(lines),
    encoding="utf-8",
)
PYEOF

echo "wrote ${SM12X_PREFILL_DECODE_ROOT}"
if [[ "${baseline_code}" != "0" ]]; then
  exit "${baseline_code}"
fi
exit "${gate_code}"
