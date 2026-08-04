#!/usr/bin/env bash
# Run the standard SM12x prefill/decode interference trace set.
#
# This is a thin orchestrator around run_mixed_arrival_nsys_profile_launch.sh.
# It intentionally does not introduce new serve knobs; pass the exact serve
# command through SERVE_COMMAND so the same profile can be used on SM120 and
# SM121 after the target host has been made stable.
#
# Required env:
#   SERVE_COMMAND       Full vLLM serve command as a single shell string.
#   OUT_DIR             Output directory for per-case nsys artifacts.
#
# Optional env:
#   PYTHON              Python interpreter for the client and summary.
#   VLLM_VENV           vLLM virtualenv. If unset and PYTHON looks like
#                       <venv>/bin/python, derive it from PYTHON.
#   NSYS_BIN            Nsight Systems binary.
#   BASE_URL            Default http://127.0.0.1:8000.
#   PROFILE_MODEL       Default deepseek-ai/DeepSeek-V4-Flash-0731.
#   PREFILL_DECODE_PROFILE_LABEL
#                       Default sm12x_prefill_decode_interference.
#   PREFILL_DECODE_PROFILE_CASE_SPECS
#                       Semicolon-separated mixed-arrival case specs. Defaults:
#                       long_long_c2, decode_then_59k, decode_then_124k,
#                       long_decode_then_short, short_decode_then_124k, and
#                       long_then_short.
#   PROFILE_REPEAT_COUNT, PROFILE_TEMPERATURE, PROFILE_TOP_P,
#   PROFILE_THINKING_MODE, PROFILE_TIMEOUT, PROFILE_PREWARM,
#   STARTUP_TIMEOUT_S, NSYS_TRACE, NSYS_CAPTURE_MODE
#                       Forwarded to run_mixed_arrival_nsys_profile_launch.sh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

PYTHON="${PYTHON:-python}"
VLLM_VENV="${VLLM_VENV:-}"
if [[ -z "${VLLM_VENV}" && "${PYTHON}" == */bin/python ]]; then
  VLLM_VENV="$(cd "$(dirname "${PYTHON}")/.." && pwd)"
fi
VLLM_ROOT="${VLLM_ROOT:-${REPO_ROOT}/vllm}"
PYTHONPATH="$(harness_pythonpath)"
export VLLM_ROOT PYTHONPATH
NSYS_BIN="${NSYS_BIN:-nsys}"
SERVE_COMMAND="${SERVE_COMMAND:?set SERVE_COMMAND}"
OUT_DIR="${OUT_DIR:?set OUT_DIR}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PROFILE_MODEL="${PROFILE_MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}"
PREFILL_DECODE_PROFILE_LABEL="${PREFILL_DECODE_PROFILE_LABEL:-sm12x_prefill_decode_interference}"
PREFILL_DECODE_PROFILE_CASE_SPECS="${PREFILL_DECODE_PROFILE_CASE_SPECS:-long_long_c2:4000:4000:fixed_delay:0:128:128;decode_then_59k:1900:1900:after_first_token:0:256:128;decode_then_124k:4000:4000:after_first_token:0:256:128;long_decode_then_short:4000:192:after_first_token:0:256:64;short_decode_then_124k:192:4000:after_first_token:0:256:128;long_then_short:4000:192:fixed_delay:2:128:64}"
PROFILE_REPEAT_COUNT="${PROFILE_REPEAT_COUNT:-1}"
PROFILE_TEMPERATURE="${PROFILE_TEMPERATURE:-0.0}"
PROFILE_TOP_P="${PROFILE_TOP_P:-1.0}"
PROFILE_THINKING_MODE="${PROFILE_THINKING_MODE:-non-thinking}"
PROFILE_EVALUATION_MODE="${PROFILE_EVALUATION_MODE:-ttft-only}"
PROFILE_TIMEOUT="${PROFILE_TIMEOUT:-3600}"
PROFILE_PREWARM="${PROFILE_PREWARM:-1}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-900}"
NSYS_TRACE="${NSYS_TRACE:-cuda,nvtx}"
NSYS_CAPTURE_MODE="${NSYS_CAPTURE_MODE:-bench_window}"

mkdir -p "${OUT_DIR}"
cases_tsv="${OUT_DIR}/profile_cases.tsv"
: > "${cases_tsv}"

failures=0
IFS=';' read -r -a case_specs <<< "${PREFILL_DECODE_PROFILE_CASE_SPECS}"
for raw_case_spec in "${case_specs[@]}"; do
  case_spec="$(printf '%s' "${raw_case_spec}" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')"
  if [[ -z "${case_spec}" ]]; then
    continue
  fi

  case_name="${case_spec%%:*}"
  if [[ -z "${case_name}" || "${case_name}" == "${case_spec}" ]]; then
    echo "invalid mixed-arrival case spec: ${case_spec}" >&2
    failures=1
    continue
  fi

  case_slug="$(printf '%s' "${case_name}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
  case_out="${OUT_DIR}/${case_slug}"
  mkdir -p "${case_out}"
  printf '%s\t%s\t%s\n' "${case_slug}" "${case_spec}" "${case_out}" >> "${cases_tsv}"

  echo "[profile] case=${case_name} out=${case_out}"
  set +e
  OUT_DIR="${case_out}" \
    PYTHON="${PYTHON}" \
    PYTHONPATH="${PYTHONPATH}" \
    VLLM_VENV="${VLLM_VENV}" \
    NSYS_BIN="${NSYS_BIN}" \
    SERVE_COMMAND="${SERVE_COMMAND}" \
    BASE_URL="${BASE_URL}" \
    PROFILE_MODEL="${PROFILE_MODEL}" \
    PROFILE_LABEL="${PREFILL_DECODE_PROFILE_LABEL}_${case_slug}" \
    PROFILE_CASE_NAME="${case_name}" \
    PROFILE_MIXED_ARRIVAL_CASE_SPECS="${case_spec}" \
    PROFILE_REPEAT_COUNT="${PROFILE_REPEAT_COUNT}" \
    PROFILE_TEMPERATURE="${PROFILE_TEMPERATURE}" \
    PROFILE_TOP_P="${PROFILE_TOP_P}" \
    PROFILE_THINKING_MODE="${PROFILE_THINKING_MODE}" \
    PROFILE_EVALUATION_MODE="${PROFILE_EVALUATION_MODE}" \
    PROFILE_TIMEOUT="${PROFILE_TIMEOUT}" \
    PROFILE_PREWARM="${PROFILE_PREWARM}" \
    STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S}" \
    NSYS_TRACE="${NSYS_TRACE}" \
    NSYS_CAPTURE_MODE="${NSYS_CAPTURE_MODE}" \
    "${SCRIPT_DIR}/run_mixed_arrival_nsys_profile_launch.sh"
  code="$?"
  set -e
  printf '%s\n' "${code}" > "${case_out}/profile_case.exit_code"
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi
done

OUT_DIR="${OUT_DIR}" PREFILL_DECODE_PROFILE_LABEL="${PREFILL_DECODE_PROFILE_LABEL}" \
  "${PYTHON}" - <<'PYEOF'
import csv
import json
import os
from pathlib import Path


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        return {"parse_error": str(exc)}


def _read_exit_code(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return None


def _top_kernels(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for index, row in enumerate(csv.DictReader(f)):
            if index >= 5:
                break
            rows.append(
                {
                    "rank": index + 1,
                    "time_percent": row.get("Time (%)"),
                    "total_ms": (
                        float(row.get("Total Time (ns)", 0) or 0) / 1e6
                    ),
                    "instances": row.get("Instances"),
                    "kernel": row.get("Name", "").strip(),
                }
            )
    return rows


def _timeline_summary(path: Path) -> dict:
    return _read_json(path)


def _dominant_decode_gap_class(timeline: dict) -> str:
    gaps = timeline.get("decode_kernel_gaps")
    if not isinstance(gaps, dict):
        return ""
    top_gaps = gaps.get("top_gaps")
    if not isinstance(top_gaps, list) or not top_gaps:
        return ""
    classes = top_gaps[0].get("duration_by_class")
    if not isinstance(classes, list) or not classes:
        return ""
    return str(classes[0].get("class") or "")


out_dir = Path(os.environ["OUT_DIR"])
label = os.environ["PREFILL_DECODE_PROFILE_LABEL"]
cases = []
case_file = out_dir / "profile_cases.tsv"
if case_file.exists():
    for line in case_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        slug, spec, case_out = line.split("\t", 2)
        case_dir = Path(case_out)
        mixed = _read_json(case_dir / "mixed_arrival" / "long_context_mixed_arrival.json")
        summary = mixed.get("summary", [])
        requests = mixed.get("requests", mixed.get("rows", []))
        timeline = _timeline_summary(case_dir / "nsys_timeline_summary.json")
        cases.append(
            {
                "case": slug,
                "spec": spec,
                "out_dir": str(case_dir),
                "exit_code": _read_exit_code(case_dir / "profile_case.exit_code"),
                "mixed_arrival_exit_code": _read_exit_code(
                    case_dir / "mixed_arrival.exit_code"
                ),
                "summary": summary,
                "request_count": len(requests),
                "top_kernels": _top_kernels(case_dir / "nsys_kernel_summary.csv"),
                "timeline": timeline,
            }
        )

payload = {"label": label, "cases": cases}
(out_dir / "prefill_decode_interference_profiles_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

lines = [
    "# SM12x prefill/decode interference profile summary",
    "",
    f"Label: `{label}`",
    "",
    "| Case | Exit | Requests | Primary TTFT | Secondary TTFT | Decode Min/Max | ITL P99 | Top kernel |",
    "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
]
for case in cases:
    row = case.get("summary", [{}])[0] if case.get("summary") else {}
    kernels = case.get("top_kernels") or []
    top = kernels[0]["kernel"] if kernels else ""
    if top and len(top) > 72:
        top = top[:69] + "..."
    lines.append(
        "| {case} | {exit_code} | {requests} | {primary} | {secondary} | {ratio} | {itl_p99} | `{top}` |".format(
            case=case["case"],
            exit_code=case.get("exit_code"),
            requests=case.get("request_count"),
            primary=row.get("primary_ttft_seconds_mean"),
            secondary=row.get("secondary_ttft_seconds_mean"),
            ratio=row.get("decode_tps_min_to_max_ratio"),
            itl_p99=row.get("p99_inter_chunk_seconds"),
            top=top,
        )
    )
lines.extend(
    [
        "",
        "## Decode Kernel Gap Timeline",
        "",
        "| Case | Max FP8 MQA gap | Dominant gap class | Max CUDA idle gap | Slow-request classification |",
        "| --- | ---: | --- | ---: | --- |",
    ]
)
for case in cases:
    timeline = case.get("timeline") or {}
    decode_gaps = timeline.get("decode_kernel_gaps") or {}
    idle_gaps = timeline.get("idle_gaps") or {}
    interpretation = timeline.get("slow_request_gap_interpretation") or {}
    lines.append(
        "| {case} | {decode_gap} | `{dominant}` | {idle_gap} | `{classification}` |".format(
            case=case["case"],
            decode_gap=decode_gaps.get("max_start_gap_seconds"),
            dominant=_dominant_decode_gap_class(timeline),
            idle_gap=idle_gaps.get("max_idle_gap_seconds"),
            classification=interpretation.get("classification", ""),
        )
    )
lines.append("")
lines.append(
    "Use this summary to decide whether the next change belongs in scheduler/admission, "
    "sparse-MLA prefill accumulate, FP8 MQA logits, or deployment-level isolation."
)
(out_dir / "prefill_decode_interference_profiles_summary.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)
PYEOF

echo "wrote ${OUT_DIR}/prefill_decode_interference_profiles_summary.md"
exit "${failures}"
