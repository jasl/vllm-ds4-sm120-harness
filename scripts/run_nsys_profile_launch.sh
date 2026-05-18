#!/usr/bin/env bash
# Optional harness tool: launch a fresh vLLM serve under `nsys profile`, drive
# a few decode steps with the bench client, then tear down. Outputs a
# top-kernels-by-total-time CSV/MD digest suited to critical-path analysis.
#
# This is the launch-mode replacement for run_nsys_profile.sh (which targeted
# attach mode that newer nsys versions no longer support).
#
# Required env:
#   SERVE_COMMAND       The full vllm serve command (as a single string). Each
#                       arg will be word-split. JSON values must already be
#                       single-quoted internally.
#   OUT_DIR             Where to write nsys_profile.nsys-rep, kernel summary,
#                       and serve.log.
#
# Optional env:
#   NSYS_BIN            Default `nsys`. Set to /usr/local/cuda/bin/nsys for
#                       CUDA 13 hosts.
#   BASE_URL            Default http://127.0.0.1:8000.
#   PROFILE_MODEL       Default deepseek-ai/DeepSeek-V4-Flash.
#   PROFILE_PROMPT      Default a short paragraph prompt.
#   PROFILE_MAX_TOKENS  Default 128. Number of decode steps captured.
#   PROFILE_WARMUP_TOKENS  Default 32. Sent before the captured request to
#                       force cudagraph warm + first batch JIT.
#   STARTUP_TIMEOUT_S   Default 600.
#   NSYS_CAPTURE_MODE   `bench_window` (default) | `full`.
#                       `bench_window` uses `nsys launch --session-new=NAME`
#                       to start the serve dormantly, runs warmup with nsys
#                       still dormant, then `nsys start` to begin capture,
#                       sends the bench request, and `nsys stop` writes the
#                       single `.nsys-rep`. Result: a tight trace of just
#                       the bench window (model load + cudagraph compile +
#                       JIT warmup are excluded). Typical size ~5-15 MiB.
#                       `full` keeps the legacy behavior — captures the
#                       whole serve lifecycle (spawn → SIGTERM), producing
#                       a ~120 MiB file. Useful when you want to see model
#                       load / JIT warmup as part of the trace.
#
# History / why not `--capture-range`:
#   * `--capture-range=cudaProfilerApi`: never worked here. The bench
#     client lives in a separate process tree from the nsys-wrapped serve,
#     so its `cudaProfilerStart` runs inside an empty CUDA context that
#     nsys does not observe. Result: "No reports were generated."
#   * `--capture-range=nvtx --nvtx-capture='gpu_model_runner: forward'
#      --capture-range-end=repeat`: works in the sense that nsys emits a
#     report per range fire, but a single bench request triggers ~140
#     forwards (warmup + bench), producing ~140 separate .nsys-rep files,
#     ~1 MB each, totaling ~145 MB. Worse UX than the 120 MB single-file
#     full-lifecycle trace.
#   * `--capture-range=nvtx ... --capture-range-end=stop`: captures only
#     the FIRST range fire, which is the warmup's first (prefill) forward
#     — not a steady-state decode step.
# The `nsys launch / start / stop` external-session flow used by
# `bench_window` here is the canonically correct way to scope nsys to a
# specific application phase.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

NSYS_BIN="${NSYS_BIN:-nsys}"
SERVE_COMMAND="${SERVE_COMMAND:?set SERVE_COMMAND}"
OUT_DIR="${OUT_DIR:?set OUT_DIR}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PROFILE_MODEL="${PROFILE_MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PROFILE_PROMPT="${PROFILE_PROMPT:-Write a short paragraph about distributed inference systems.}"
PROFILE_MAX_TOKENS="${PROFILE_MAX_TOKENS:-128}"
PROFILE_WARMUP_TOKENS="${PROFILE_WARMUP_TOKENS:-32}"
PROFILE_TEMPERATURE="${PROFILE_TEMPERATURE:-1.0}"
PROFILE_LABEL="${PROFILE_LABEL:-decode_short}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-600}"
NSYS_TRACE="${NSYS_TRACE:-cuda,nvtx}"
NSYS_CAPTURE_MODE="${NSYS_CAPTURE_MODE:-bench_window}"
NSYS_SESSION_NAME="${NSYS_SESSION_NAME:-harness_$$}"

case "${NSYS_CAPTURE_MODE}" in
  bench_window|full) ;;
  *)
    echo "NSYS_CAPTURE_MODE must be 'bench_window' or 'full' (got '${NSYS_CAPTURE_MODE}')" >&2
    exit 2
    ;;
esac

mkdir -p "${OUT_DIR}"
nsys_rep="${OUT_DIR}/nsys_profile.nsys-rep"
nsys_log="${OUT_DIR}/nsys_run.log"
serve_log="${OUT_DIR}/serve.log"
client_log="${OUT_DIR}/nsys_run.json"

if ! command -v "${NSYS_BIN}" >/dev/null 2>&1; then
  echo "nsys not on PATH; set NSYS_BIN" >&2
  exit 2
fi

# Persist the serve command for reproducibility.
printf '%s\n' "${SERVE_COMMAND}" > "${OUT_DIR}/serve_command.txt"

echo "starting nsys-wrapped serve, mode=${NSYS_CAPTURE_MODE}, output=${nsys_rep}"

if [[ "${NSYS_CAPTURE_MODE}" == "bench_window" ]]; then
  # Use `nsys launch --session-new=NAME` so the serve starts dormantly
  # (no profile data collected yet). After warmup we'll `nsys start` to
  # begin capture, run the bench, then `nsys stop` to write the report.
  setsid "${NSYS_BIN}" launch \
    --session-new="${NSYS_SESSION_NAME}" \
    --trace "${NSYS_TRACE}" \
    --sample none \
    --cpuctxsw none \
    --cuda-flush-interval 1000 \
    --gpu-metrics-device=none \
    -- bash -c "${SERVE_COMMAND}" > "${serve_log}" 2>&1 &
  NSYS_PGID=$!
  echo "nsys launch pgid=${NSYS_PGID}, session=${NSYS_SESSION_NAME}, waiting for /health..."
else
  # full mode: profile from spawn through SIGTERM teardown.
  setsid "${NSYS_BIN}" profile \
    --output "${nsys_rep%.nsys-rep}" \
    --trace "${NSYS_TRACE}" \
    --sample none \
    --cpuctxsw none \
    --cuda-flush-interval 1000 \
    --gpu-metrics-device=none \
    --kill=sigterm \
    --stop-on-exit true \
    -- bash -c "${SERVE_COMMAND}" > "${serve_log}" 2>&1 &
  NSYS_PGID=$!
  echo "nsys profile pgid=${NSYS_PGID}, waiting for /health..."
fi

# Wait for serve readiness.
ready=0
elapsed=0
while (( elapsed < STARTUP_TIMEOUT_S )); do
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
  tail -30 "${serve_log}" >&2 || true
  kill -TERM "-${NSYS_PGID}" 2>/dev/null || true
  exit 4
fi

# Warmup (NOT inside capture range).
python3 - <<PYEOF
import json, urllib.request, time
url = "${BASE_URL}/v1/chat/completions"
req = {
    "model": "${PROFILE_MODEL}",
    "messages": [{"role": "user", "content": "${PROFILE_PROMPT}"}],
    "max_tokens": int("${PROFILE_WARMUP_TOKENS}"),
    "temperature": float("${PROFILE_TEMPERATURE}"),
    "top_p": 1.0,
}
hdr = {"content-type": "application/json"}
t0 = time.time()
urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(req).encode(), headers=hdr), timeout=120).read()
print(f"warmup done in {time.time()-t0:.2f}s")
PYEOF

# In bench_window mode, this is where we explicitly turn capture ON for
# just the captured request, so the trace is scoped to exactly that window.
# In full mode, capture is already active from spawn.
if [[ "${NSYS_CAPTURE_MODE}" == "bench_window" ]]; then
  echo "starting nsys capture for session=${NSYS_SESSION_NAME}..."
  "${NSYS_BIN}" start --session="${NSYS_SESSION_NAME}" 2>&1 | tail -3
fi

# Captured request: send the bench prompt.
python3 - <<PYEOF > "${client_log}.client_stdout"
import json, time, urllib.request
url = "${BASE_URL}/v1/chat/completions"
req = {
    "model": "${PROFILE_MODEL}",
    "messages": [{"role": "user", "content": "${PROFILE_PROMPT}"}],
    "max_tokens": int("${PROFILE_MAX_TOKENS}"),
    "temperature": float("${PROFILE_TEMPERATURE}"),
    "top_p": 1.0,
}
hdr = {"content-type": "application/json"}
t0 = time.time()
r = urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(req).encode(), headers=hdr), timeout=300).read()
t1 = time.time()
body = json.loads(r)
usage = body.get('usage', {})
with open("${client_log}", "w") as f:
    json.dump({
        "elapsed_s": t1 - t0,
        "usage": usage,
        "prompt": "${PROFILE_PROMPT}",
        "max_tokens": int("${PROFILE_MAX_TOKENS}"),
        "label": "${PROFILE_LABEL}",
        "capture_mode": "${NSYS_CAPTURE_MODE}",
        "session_name": "${NSYS_SESSION_NAME}" if "${NSYS_CAPTURE_MODE}" == "bench_window" else None,
    }, f, indent=2)
print(f"captured: elapsed={t1-t0:.2f}s prompt_tokens={usage.get('prompt_tokens')} completion_tokens={usage.get('completion_tokens')}")
PYEOF
cat "${client_log}.client_stdout"

# bench_window mode: stop capture and write the report file.
if [[ "${NSYS_CAPTURE_MODE}" == "bench_window" ]]; then
  echo "stopping nsys capture for session=${NSYS_SESSION_NAME}..."
  "${NSYS_BIN}" stop --session="${NSYS_SESSION_NAME}" \
    --output "${nsys_rep%.nsys-rep}" 2>&1 | tail -5
fi

echo "tearing down nsys+serve pgid=${NSYS_PGID}..."
kill -TERM "-${NSYS_PGID}" 2>/dev/null || true
# Give nsys time to flush
sleep 15
# Force-kill any straggler vllm workers
pkill -KILL -f "vllm.entrypoints" 2>/dev/null || true
pkill -KILL -f "VLLM::Worker" 2>/dev/null || true
sleep 3

if [[ ! -f "${nsys_rep}" ]]; then
  echo "no nsys-rep file at ${nsys_rep}; serve.log tail:" >&2
  tail -30 "${serve_log}" >&2 || true
  exit 5
fi

# Extract kernel summary.
"${NSYS_BIN}" stats --report cuda_gpu_kern_sum --format csv \
  --output "${OUT_DIR}/nsys_kernel_summary" \
  "${nsys_rep}" > "${nsys_log}" 2>&1 || {
  echo "nsys stats failed; see ${nsys_log}" >&2
  exit 6
}
mv -f "${OUT_DIR}/nsys_kernel_summary_cuda_gpu_kern_sum.csv" "${OUT_DIR}/nsys_kernel_summary.csv" 2>/dev/null || true

python3 - <<PYEOF > "${OUT_DIR}/nsys_kernel_summary.md"
import csv, json
rows = []
with open("${OUT_DIR}/nsys_kernel_summary.csv") as f:
    for r in csv.DictReader(f):
        rows.append(r)
print(f"# nsys kernel summary — ${PROFILE_LABEL}")
print()
try:
    with open("${client_log}") as f:
        meta = json.load(f)
    print(f"Capture window: {meta['elapsed_s']:.2f}s; completion_tokens={meta['usage'].get('completion_tokens')}; max_tokens={meta['max_tokens']}")
    print()
except Exception:
    pass
print("| rank | time % | total ms | instances | avg us | kernel |")
print("|---|---|---|---|---|---|")
for i, r in enumerate(rows[:30], 1):
    name = r.get("Name", "").strip()
    short = (name[:96] + "...") if len(name) > 99 else name
    pct = r.get("Time (%)", "0").strip()
    total_ns = float(r.get("Total Time (ns)", 0) or 0)
    inst = r.get("Instances", "0").strip()
    avg_ns = float(r.get("Avg (ns)", 0) or 0)
    print(f"| {i} | {pct} | {total_ns/1e6:.2f} | {inst} | {avg_ns/1e3:.2f} | `{short}` |")
PYEOF

echo "wrote ${OUT_DIR}/nsys_kernel_summary.md"
