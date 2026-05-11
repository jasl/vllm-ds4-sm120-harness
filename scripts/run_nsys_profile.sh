#!/usr/bin/env bash
# Optional harness tool: capture an nsys trace of N decode steps from a vLLM
# serve, then extract a kernel-time-by-name summary CSV ready for
# critical-path analysis.
#
# *** STATUS: attach-mode (--target-pid) does NOT work on Nsight Systems
# 2025.5.2 and newer — that flag was removed. To profile an already-running
# serve, restart it under `nsys profile` directly (launch mode). A wrapper
# launcher in scripts/run_nsys_profile_launch.sh is the proper replacement;
# this script remains the historical reference.
#
# Pre-conditions:
#   * vLLM serve already up on BASE_URL (default http://127.0.0.1:8000).
#   * nsys binary on PATH (or NSYS_BIN exported). On CUDA 13 hosts that means
#     PATH=/usr/local/cuda/bin:$PATH or /usr/local/cuda-13.2/bin:$PATH.
#   * The serve was started with --enable-prefix-caching if possible, so
#     repeated profiling runs amortise prefill.
#
# Output (under OUT_DIR):
#   * nsys_profile.nsys-rep  raw report
#   * nsys_kernel_summary.csv  top kernels sorted by total time
#   * nsys_kernel_summary.md   human-readable digest
#   * nsys_run.json            client-side timing and request shape
#   * nsys_run.log             stdout/stderr from nsys
#
# The capture window is the bench client run only. We use --capture-range=none
# and let the bench client drive a single short prompt followed by N decode
# steps, so the trace covers exactly one fully-warm decode batch shape (no
# server startup, no graph capture).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
BASE_URL="${BASE_URL:-http://${HOST}:${PORT}}"
TOKENIZER_MODE="${TOKENIZER_MODE:-deepseek_v4}"
NSYS_BIN="${NSYS_BIN:-nsys}"
PROFILE_LABEL="${PROFILE_LABEL:-decode_short}"
PROFILE_PROMPT="${PROFILE_PROMPT:-Write a short paragraph about distributed inference systems.}"
PROFILE_MAX_TOKENS="${PROFILE_MAX_TOKENS:-256}"
PROFILE_TEMPERATURE="${PROFILE_TEMPERATURE:-1.0}"
PROFILE_WARMUP_TOKENS="${PROFILE_WARMUP_TOKENS:-32}"
PROFILE_SERVER_PID="${PROFILE_SERVER_PID:-}"
PROFILE_TARGET_MODE="${PROFILE_TARGET_MODE:-server-attach}"
OUT_DIR="${OUT_DIR:?set OUT_DIR}"
NSYS_SAMPLE_RATE="${NSYS_SAMPLE_RATE:-100}"
NSYS_TRACE="${NSYS_TRACE:-cuda,nvtx}"

mkdir -p "${OUT_DIR}"
nsys_rep="${OUT_DIR}/nsys_profile.nsys-rep"
nsys_log="${OUT_DIR}/nsys_run.log"
client_log="${OUT_DIR}/nsys_run.json"

if ! command -v "${NSYS_BIN}" >/dev/null 2>&1; then
  echo "nsys not on PATH; set NSYS_BIN=/usr/local/cuda/bin/nsys or similar" >&2
  exit 2
fi

# Resolve the serve PID. Prefer the explicit override, fall back to the
# default port match. We need a PID so nsys can attach to the right process.
if [[ -z "${PROFILE_SERVER_PID}" ]]; then
  PROFILE_SERVER_PID="$(pgrep -fa 'vllm.entrypoints.cli.main serve' | head -1 | awk '{print $1}' || true)"
fi
if [[ -z "${PROFILE_SERVER_PID}" ]]; then
  PROFILE_SERVER_PID="$(pgrep -fa 'vllm serve' | head -1 | awk '{print $1}' || true)"
fi
if [[ -z "${PROFILE_SERVER_PID}" ]]; then
  echo "could not locate vllm serve PID; set PROFILE_SERVER_PID explicitly" >&2
  exit 3
fi

echo "profile target pid=${PROFILE_SERVER_PID}, output=${nsys_rep}"

# Phase 1: short warmup request so the bench loop hits a fully-warm decode
# path. We don't capture this.
python3 - <<PYEOF
import json, urllib.request, time
url = "${BASE_URL}/v1/chat/completions"
req = {
    "model": "${MODEL}",
    "messages": [{"role": "user", "content": "${PROFILE_PROMPT}"}],
    "max_tokens": int("${PROFILE_WARMUP_TOKENS}"),
    "temperature": float("${PROFILE_TEMPERATURE}"),
    "top_p": 1.0,
}
data = json.dumps(req).encode()
hdr = {"content-type": "application/json"}
t0 = time.time()
urllib.request.urlopen(urllib.request.Request(url, data=data, headers=hdr), timeout=120).read()
print(f"warmup completed in {time.time()-t0:.2f}s")
PYEOF

# Phase 2: start nsys attached to the server PID, then drive a single
# capture-range-bracketed request from a client subprocess.
"${NSYS_BIN}" profile \
  --output "${nsys_rep%.nsys-rep}" \
  --trace "${NSYS_TRACE}" \
  --sample none \
  --cpuctxsw none \
  --cuda-flush-interval 1000 \
  --capture-range=cudaProfilerApi \
  --capture-range-end=stop-shutdown \
  --duration 60 \
  --gpu-metrics-device=none \
  --kill=none \
  --stop-on-exit true \
  --target-pid "${PROFILE_SERVER_PID}" \
  bash -c "set -euo pipefail
python3 - <<PYINNER
import json, time, urllib.request
try:
    import ctypes
    cu = ctypes.CDLL('libcudart.so')
    cu.cudaProfilerStart()
except Exception as e:
    print('cudaProfilerStart unavailable client-side, relying on server NVTX:', e)
url = '${BASE_URL}/v1/chat/completions'
req = {
    'model': '${MODEL}',
    'messages': [{'role': 'user', 'content': '${PROFILE_PROMPT}'}],
    'max_tokens': int('${PROFILE_MAX_TOKENS}'),
    'temperature': float('${PROFILE_TEMPERATURE}'),
    'top_p': 1.0,
    'stream': False,
}
hdr = {'content-type': 'application/json'}
t0 = time.time()
r = urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(req).encode(), headers=hdr), timeout=120).read()
t1 = time.time()
try:
    cu.cudaProfilerStop()
except Exception:
    pass
body = json.loads(r)
usage = body.get('usage', {})
metrics = {
    'elapsed_s': t1-t0,
    'usage': usage,
    'prompt': '${PROFILE_PROMPT}',
    'max_tokens': int('${PROFILE_MAX_TOKENS}'),
}
import os
with open('${client_log}', 'w') as f:
    json.dump(metrics, f, indent=2)
print('captured: elapsed=%.2fs prompt_tokens=%s completion_tokens=%s' % (t1-t0, usage.get('prompt_tokens'), usage.get('completion_tokens')))
PYINNER
" > "${nsys_log}" 2>&1 || {
  echo "nsys profile failed; see ${nsys_log}" >&2
  tail -40 "${nsys_log}" >&2 || true
  exit 4
}

echo "raw report at ${nsys_rep}"

# Phase 3: extract a kernel-time-by-name summary CSV. Use nsys stats with the
# cuda_gpu_kern_sum report.
"${NSYS_BIN}" stats --report cuda_gpu_kern_sum --format csv \
  --output "${OUT_DIR}/nsys_kernel_summary" \
  "${nsys_rep}" >> "${nsys_log}" 2>&1 || {
  echo "nsys stats failed; see ${nsys_log}" >&2
  exit 5
}

# nsys writes nsys_kernel_summary_cuda_gpu_kern_sum.csv; canonicalize the name
mv -f "${OUT_DIR}/nsys_kernel_summary_cuda_gpu_kern_sum.csv" "${OUT_DIR}/nsys_kernel_summary.csv" 2>/dev/null || true

# Phase 4: produce a human-readable digest of the top 25 kernels by total time.
python3 - <<PYEOF > "${OUT_DIR}/nsys_kernel_summary.md"
import csv, json
rows = []
with open("${OUT_DIR}/nsys_kernel_summary.csv") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)
# Typical headers: 'Time (%)', 'Total Time (ns)', 'Instances',
# 'Avg (ns)', 'Med (ns)', 'Min (ns)', 'Max (ns)', 'StdDev (ns)', 'Name'
print("# nsys kernel summary — top 25 by total time")
print()
print(f"Profile label: ${PROFILE_LABEL}")
import os
print()
try:
    with open("${client_log}") as f:
        meta = json.load(f)
    print(f"Bench window: {meta['elapsed_s']:.2f}s, completion_tokens={meta['usage'].get('completion_tokens')}")
    print()
except Exception:
    pass
print("| rank | time % | total ms | instances | avg us | kernel |")
print("|---|---|---|---|---|---|")
for i, r in enumerate(rows[:25], 1):
    name = r.get('Name', '').strip()
    pct = r.get('Time (%)', '0').strip()
    total_ns = float(r.get('Total Time (ns)', 0) or 0)
    inst = r.get('Instances', '0').strip()
    avg_ns = float(r.get('Avg (ns)', 0) or 0)
    short = (name[:90] + '...') if len(name) > 93 else name
    print(f"| {i} | {pct} | {total_ns/1e6:.2f} | {inst} | {avg_ns/1e3:.2f} | `{short}` |")
PYEOF

echo "kernel summary md: ${OUT_DIR}/nsys_kernel_summary.md"
