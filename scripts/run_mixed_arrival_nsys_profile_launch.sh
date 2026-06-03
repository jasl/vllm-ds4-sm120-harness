#!/usr/bin/env bash
# Optional harness tool: launch a fresh vLLM serve under Nsight Systems and
# capture a mixed-arrival scheduling window. This is for prefill/decode
# interference analysis, especially decode-then-long and long-then-short cases.
#
# Required env:
#   SERVE_COMMAND       Full vLLM serve command as a single shell string.
#   OUT_DIR             Output directory for nsys report, logs, and summaries.
#
# Optional env:
#   PYTHON              Python interpreter for the client (default python).
#   NSYS_BIN            Nsight Systems binary (default nsys).
#   BASE_URL            Default http://127.0.0.1:8000.
#   PROFILE_MODEL       Default deepseek-ai/DeepSeek-V4-Flash.
#   PROFILE_LABEL       Default mixed_arrival_nsys.
#   PROFILE_CASE_NAME   Default mixed_arrival_nsys.
#   PROFILE_MIXED_ARRIVAL_CASE_SPECS
#                       Default captures decode_then_124k only. Override with
#                       one mixed-arrival spec to keep traces small.
#   PROFILE_REPEAT_COUNT Default 1.
#   PROFILE_TEMPERATURE Default 0.0.
#   PROFILE_TOP_P       Default 1.0.
#   PROFILE_THINKING_MODE default non-thinking.
#   PROFILE_TIMEOUT     Per-request timeout seconds (default 3600).
#   PROFILE_PREWARM     1 runs prewarm_serve before capture (default 1).
#   STARTUP_TIMEOUT_S   Default 900.
#   NSYS_CAPTURE_MODE   bench_window (default) | full.
#
# Output:
#   serve.log
#   serve_command.txt
#   nsys_profile.nsys-rep
#   nsys_kernel_summary.csv
#   nsys_kernel_summary.md
#   nsys_cuda_gpu_trace.csv
#   nsys_timeline_summary.json
#   nsys_timeline_summary.md
#   mixed_arrival/long_context_mixed_arrival.json
#   mixed_arrival/long_context_mixed_arrival.md
#   mixed_arrival_client.stdout

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

PYTHON="${PYTHON:-python}"
VLLM_ROOT="${VLLM_ROOT:-${REPO_ROOT}/vllm}"
PYTHONPATH="$(harness_pythonpath)"
export VLLM_ROOT PYTHONPATH
NSYS_BIN="${NSYS_BIN:-nsys}"
SERVE_COMMAND="${SERVE_COMMAND:?set SERVE_COMMAND}"
OUT_DIR="${OUT_DIR:?set OUT_DIR}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PROFILE_MODEL="${PROFILE_MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PROFILE_LABEL="${PROFILE_LABEL:-mixed_arrival_nsys}"
PROFILE_CASE_NAME="${PROFILE_CASE_NAME:-mixed_arrival_nsys}"
PROFILE_MIXED_ARRIVAL_CASE_SPECS="${PROFILE_MIXED_ARRIVAL_CASE_SPECS:-decode_then_124k:4000:4000:after_first_token:0:256:128}"
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
NSYS_SESSION_NAME="${NSYS_SESSION_NAME:-harness_mixed_arrival_$$}"

case "${NSYS_CAPTURE_MODE}" in
  bench_window|full) ;;
  *)
    echo "NSYS_CAPTURE_MODE must be bench_window or full (got '${NSYS_CAPTURE_MODE}')" >&2
    exit 2
    ;;
esac

case "${PROFILE_PREWARM}" in
  0|1|false|true) ;;
  *)
    echo "PROFILE_PREWARM must be 0/1/false/true (got '${PROFILE_PREWARM}')" >&2
    exit 2
    ;;
esac

mkdir -p "${OUT_DIR}"
nsys_rep="${OUT_DIR}/nsys_profile.nsys-rep"
nsys_log="${OUT_DIR}/nsys_run.log"
serve_log="${OUT_DIR}/serve.log"
client_stdout="${OUT_DIR}/mixed_arrival_client.stdout"
mixed_out_dir="${OUT_DIR}/mixed_arrival"

if ! command -v "${NSYS_BIN}" >/dev/null 2>&1; then
  echo "nsys not on PATH; set NSYS_BIN" >&2
  exit 2
fi

printf '%s\n' "${SERVE_COMMAND}" > "${OUT_DIR}/serve_command.txt"
printf '%s\n' "${PROFILE_MIXED_ARRIVAL_CASE_SPECS}" > "${OUT_DIR}/case_specs.txt"

echo "starting nsys-wrapped serve, mode=${NSYS_CAPTURE_MODE}, output=${nsys_rep}"
if [[ "${NSYS_CAPTURE_MODE}" == "bench_window" ]]; then
  setsid "${NSYS_BIN}" launch \
    --session-new="${NSYS_SESSION_NAME}" \
    --trace "${NSYS_TRACE}" \
    --cuda-flush-interval 1000 \
    -- bash -c "${SERVE_COMMAND}" > "${serve_log}" 2>&1 &
  NSYS_PGID=$!
  echo "nsys launch pgid=${NSYS_PGID}, session=${NSYS_SESSION_NAME}, waiting for /health..."
else
  setsid "${NSYS_BIN}" profile \
    --output "${nsys_rep%.nsys-rep}" \
    --trace "${NSYS_TRACE}" \
    --sample none \
    --cpuctxsw none \
    --cuda-flush-interval 1000 \
    --kill=sigterm \
    --stop-on-exit true \
    -- bash -c "${SERVE_COMMAND}" > "${serve_log}" 2>&1 &
  NSYS_PGID=$!
  echo "nsys profile pgid=${NSYS_PGID}, waiting for /health..."
fi

cleanup() {
  kill -TERM "-${NSYS_PGID}" 2>/dev/null || true
  sleep 5
  kill -KILL "-${NSYS_PGID}" 2>/dev/null || true
  stop_nsys_agent
}
trap cleanup EXIT

stop_nsys_agent() {
  ps -eo pid=,args= \
    | awk -v session="${NSYS_SESSION_NAME}" \
        '$0 ~ /nsys --start-agent/ && index($0, session) { print $1 }' \
    | xargs -r kill 2>/dev/null || true
}

ready=0
elapsed=0
while (( elapsed < STARTUP_TIMEOUT_S )); do
  if ! kill -0 "${NSYS_PGID}" 2>/dev/null; then
    echo "nsys-wrapped serve exited before health; tail of serve.log:" >&2
    tail -40 "${serve_log}" >&2 || true
    exit 4
  fi
  code="$(curl -s --max-time 5 "${BASE_URL}/health" -o /dev/null -w '%{http_code}' || echo 000)"
  if [[ "${code}" == "200" ]]; then
    ready=1
    echo "serve healthy after ${elapsed}s"
    break
  fi
  sleep 10
  elapsed=$((elapsed + 10))
done
if (( ready == 0 )); then
  echo "serve never became healthy; tail of serve.log:" >&2
  tail -40 "${serve_log}" >&2 || true
  exit 4
fi

if [[ "${PROFILE_PREWARM}" == "1" || "${PROFILE_PREWARM}" == "true" ]]; then
  PREWARM_BASE_URL="${BASE_URL}" \
    MODEL_ID="${PROFILE_MODEL}" \
    VLLM_VENV="${VLLM_VENV:-}" \
    PREWARM_LOG="${OUT_DIR}/prewarm.log" \
    "${SCRIPT_DIR}/prewarm_serve.sh"
fi

if [[ "${NSYS_CAPTURE_MODE}" == "bench_window" ]]; then
  echo "starting nsys capture for session=${NSYS_SESSION_NAME}..."
  "${NSYS_BIN}" start \
    --session="${NSYS_SESSION_NAME}" \
    --output "${nsys_rep%.nsys-rep}" \
    --sample none \
    --cpuctxsw none \
    2>&1 | tail -3
fi

set +e
OUT_DIR="${mixed_out_dir}" \
  BASE_URL="${BASE_URL}" \
  MODEL="${PROFILE_MODEL}" \
  PYTHON="${PYTHON}" \
  LONG_CONTEXT_MIXED_ARRIVAL_VARIANT="${PROFILE_LABEL}" \
  LONG_CONTEXT_MIXED_ARRIVAL_CASE_NAME="${PROFILE_CASE_NAME}" \
  LONG_CONTEXT_MIXED_ARRIVAL_CASE_SPECS="${PROFILE_MIXED_ARRIVAL_CASE_SPECS}" \
  LONG_CONTEXT_MIXED_ARRIVAL_REPEAT_COUNT="${PROFILE_REPEAT_COUNT}" \
  LONG_CONTEXT_MIXED_ARRIVAL_TEMPERATURE="${PROFILE_TEMPERATURE}" \
  LONG_CONTEXT_MIXED_ARRIVAL_TOP_P="${PROFILE_TOP_P}" \
  LONG_CONTEXT_MIXED_ARRIVAL_THINKING_MODE="${PROFILE_THINKING_MODE}" \
  LONG_CONTEXT_MIXED_ARRIVAL_EVALUATION_MODE="${PROFILE_EVALUATION_MODE}" \
  LONG_CONTEXT_MIXED_ARRIVAL_TIMEOUT="${PROFILE_TIMEOUT}" \
  SERVE_LOG="${serve_log}" \
  "${SCRIPT_DIR}/run_long_context_mixed_arrival.sh" > "${client_stdout}" 2>&1
client_code="$?"
set -e
printf '%s\n' "${client_code}" > "${OUT_DIR}/mixed_arrival.exit_code"

if [[ "${NSYS_CAPTURE_MODE}" == "bench_window" ]]; then
  echo "stopping nsys capture for session=${NSYS_SESSION_NAME}..."
  "${NSYS_BIN}" stop --session="${NSYS_SESSION_NAME}" 2>&1 | tail -5
fi

echo "tearing down nsys+serve pgid=${NSYS_PGID}..."
kill -TERM "-${NSYS_PGID}" 2>/dev/null || true
sleep 15
kill -KILL "-${NSYS_PGID}" 2>/dev/null || true
stop_nsys_agent

if [[ ! -f "${nsys_rep}" ]]; then
  echo "no nsys-rep file at ${nsys_rep}; serve.log tail:" >&2
  tail -40 "${serve_log}" >&2 || true
  exit 5
fi

"${NSYS_BIN}" stats --report cuda_gpu_kern_sum --format csv \
  --output "${OUT_DIR}/nsys_kernel_summary" \
  "${nsys_rep}" > "${nsys_log}" 2>&1 || {
  echo "nsys stats failed; see ${nsys_log}" >&2
  exit 6
}
mv -f "${OUT_DIR}/nsys_kernel_summary_cuda_gpu_kern_sum.csv" "${OUT_DIR}/nsys_kernel_summary.csv" 2>/dev/null || true

if "${NSYS_BIN}" stats --report cuda_gpu_trace --format csv \
  --output "${OUT_DIR}/nsys_cuda_gpu_trace" \
  "${nsys_rep}" >> "${nsys_log}" 2>&1; then
  mv -f "${OUT_DIR}/nsys_cuda_gpu_trace_cuda_gpu_trace.csv" "${OUT_DIR}/nsys_cuda_gpu_trace.csv" 2>/dev/null || true
else
  echo "nsys cuda_gpu_trace export failed; continuing without timeline summary" >&2
fi

if [[ -f "${OUT_DIR}/nsys_cuda_gpu_trace.csv" ]]; then
  OUT_DIR="${OUT_DIR}" "${PYTHON}" - <<'PYEOF'
import os
from pathlib import Path

from ds4_harness.nsys_trace import (
    build_nsys_cuda_trace_report,
    write_nsys_cuda_trace_report_json,
    write_nsys_cuda_trace_report_markdown,
)

out_dir = Path(os.environ["OUT_DIR"])
report = build_nsys_cuda_trace_report(
    out_dir / "nsys_cuda_gpu_trace.csv",
    mixed_arrival_json=out_dir / "mixed_arrival" / "long_context_mixed_arrival.json",
)
write_nsys_cuda_trace_report_json(out_dir / "nsys_timeline_summary.json", report)
write_nsys_cuda_trace_report_markdown(out_dir / "nsys_timeline_summary.md", report)
PYEOF
fi

OUT_DIR="${OUT_DIR}" PROFILE_LABEL="${PROFILE_LABEL}" \
  "${PYTHON}" - <<'PYEOF' > "${OUT_DIR}/nsys_kernel_summary.md"
import csv
import json
import os
from pathlib import Path

out_dir = Path(os.environ["OUT_DIR"])
mixed_json = out_dir / "mixed_arrival" / "long_context_mixed_arrival.json"
print("# nsys mixed-arrival kernel summary")
print()
print(f"Profile label: {os.environ['PROFILE_LABEL']}")
print()
print("Mixed-arrival result: `mixed_arrival/long_context_mixed_arrival.json`")
if mixed_json.exists():
    try:
        payload = json.loads(mixed_json.read_text(encoding="utf-8"))
        rows = payload.get("requests", payload.get("rows", []))
        print()
        print(f"Requests: {len(rows)}")
        for summary in payload.get("summary", [])[:4]:
            case_name = summary.get("case")
            primary_ttft = summary.get("primary_ttft_seconds_mean")
            secondary_ttft = summary.get("secondary_ttft_seconds_mean")
            ratio = summary.get("decode_tps_min_to_max_ratio")
            itl_p99 = summary.get("p99_inter_chunk_seconds")
            print(
                f"- {case_name}: primary_ttft={primary_ttft}, "
                f"secondary_ttft={secondary_ttft}, decode_min_max={ratio}, "
                f"itl_p99={itl_p99}"
            )
        for row in rows[:4]:
            case_name = row.get("case_name")
            print(
                f"- request {row.get('arrival_case', case_name)} "
                f"{row.get('request_role')}: ttft={row.get('ttft_seconds')}, "
                f"decode_tps={row.get('decode_tokens_per_second')}, "
                f"itl_p95={row.get('p95_inter_chunk_seconds')}"
            )
    except Exception as exc:
        print()
        print(f"Could not parse mixed-arrival JSON: {exc}")
print()
rows = []
with open(out_dir / "nsys_kernel_summary.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append(r)
print("| rank | time % | total ms | instances | avg us | kernel |")
print("|---|---|---|---|---|---|")
for i, r in enumerate(rows[:30], 1):
    name = r.get("Name", "").strip()
    short = (name[:96] + "...") if len(name) > 99 else name
    pct = r.get("Time (%)", "0").strip()
    total_ns = float(r.get("Total Time (ns)", 0) or 0)
    inst = r.get("Instances", "0").strip()
    avg_ns = float(r.get("Avg (ns)", 0) or 0)
    print(
        f"| {i} | {pct} | {total_ns / 1e6:.2f} | {inst} | "
        f"{avg_ns / 1e3:.2f} | `{short}` |"
    )
PYEOF

echo "wrote ${OUT_DIR}/nsys_kernel_summary.md"
exit "${client_code}"
