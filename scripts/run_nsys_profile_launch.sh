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
#
# Capture window: between cudaProfilerStart/Stop in the bench client. We use
# `--capture-range=cudaProfilerApi --capture-range-end=stop`, so only the
# tagged request is in the trace; serve startup + warmup are excluded.

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

echo "starting nsys-wrapped serve, output=${nsys_rep}"
# Launch serve under nsys with cudaProfilerApi capture range. The serve runs
# until killed; we kill it after the bench window closes.
setsid "${NSYS_BIN}" profile \
  --output "${nsys_rep%.nsys-rep}" \
  --trace "${NSYS_TRACE}" \
  --sample none \
  --cpuctxsw none \
  --cuda-flush-interval 1000 \
  --capture-range=cudaProfilerApi \
  --capture-range-end=stop-shutdown \
  --gpu-metrics-device=none \
  --kill=sigterm \
  --stop-on-exit true \
  -- bash -c "${SERVE_COMMAND}" > "${serve_log}" 2>&1 &
NSYS_PGID=$!
echo "nsys+serve pgid=${NSYS_PGID}, waiting for /health..."

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

# Captured request: bracket with cudaProfilerStart/Stop.
python3 - <<PYEOF > "${client_log}.client_stdout"
import ctypes, json, time, urllib.request
cu = ctypes.CDLL('libcudart.so')
try:
    cu.cudaProfilerStart()
except Exception as e:
    print('cudaProfilerStart failed:', e)
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
try:
    cu.cudaProfilerStop()
except Exception:
    pass
body = json.loads(r)
usage = body.get('usage', {})
with open("${client_log}", "w") as f:
    json.dump({
        "elapsed_s": t1 - t0,
        "usage": usage,
        "prompt": "${PROFILE_PROMPT}",
        "max_tokens": int("${PROFILE_MAX_TOKENS}"),
        "label": "${PROFILE_LABEL}",
    }, f, indent=2)
print(f"captured: elapsed={t1-t0:.2f}s prompt_tokens={usage.get('prompt_tokens')} completion_tokens={usage.get('completion_tokens')}")
PYEOF
cat "${client_log}.client_stdout"

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
