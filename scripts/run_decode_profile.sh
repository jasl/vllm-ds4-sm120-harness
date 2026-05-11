#!/usr/bin/env bash
# Optional harness tool: capture a decode-step kernel profile via vLLM's
# built-in torch profiler. Produces a chrome-trace JSON plus a top-kernels
# summary suitable for critical-path analysis. Does NOT require nsys.
#
# Required env:
#   SERVE_COMMAND       Full vllm serve command (single string, word-split).
#                       MUST be launched fresh from this script — torch
#                       profiler hooks are installed at server startup when
#                       VLLM_TORCH_PROFILER_DIR is set.
#   OUT_DIR             Output directory.
#
# Optional env:
#   BASE_URL            Default http://127.0.0.1:8000
#   PROFILE_MODEL       Default deepseek-ai/DeepSeek-V4-Flash
#   PROFILE_PROMPT      Default short paragraph
#   PROFILE_MAX_TOKENS  Default 128 (decode-step count)
#   PROFILE_WARMUP_TOKENS  Default 32
#   STARTUP_TIMEOUT_S   Default 600
#
# Output:
#   serve.log                  vLLM serve stdout/stderr
#   serve_command.txt          recorded command line
#   profile_request.json       client-side timing + token usage
#   torch_trace/*.trace.json   raw kineto chrome trace (one file per worker)
#   torch_kernel_summary.csv   aggregated top kernels by total CUDA time
#   torch_kernel_summary.md    human-readable digest

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

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

mkdir -p "${OUT_DIR}"
trace_dir="${OUT_DIR}/torch_trace"
mkdir -p "${trace_dir}"

serve_log="${OUT_DIR}/serve.log"
client_log="${OUT_DIR}/profile_request.json"
echo "${SERVE_COMMAND}" > "${OUT_DIR}/serve_command.txt"

# Launch the serve with torch profiler hooks enabled.
# Modern vLLM uses --profiler-config CLI args (not the old VLLM_TORCH_PROFILER_DIR
# env var) to enable /start_profile and /stop_profile endpoints and write
# chrome traces into the configured directory.
profiler_flags="--profiler-config '{\"profiler\":\"torch\",\"torch_profiler_dir\":\"${trace_dir}\"}'"
setsid bash -c "${SERVE_COMMAND} ${profiler_flags}" > "${serve_log}" 2>&1 &
SERVE_PGID=$!
echo "serve pgid=${SERVE_PGID} (torch profiler dir=${trace_dir}); waiting for /health..."

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
  echo "serve never healthy; tail of serve.log:" >&2
  tail -30 "${serve_log}" >&2 || true
  kill -TERM "-${SERVE_PGID}" 2>/dev/null || true
  exit 4
fi

# Warmup (NOT inside profile range)
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

# Start profile, run captured request, stop profile.
python3 - <<PYEOF > "${client_log}.client_stdout"
import json, time, urllib.request

def post(path, data=None, timeout=60):
    url = "${BASE_URL}" + path
    req = urllib.request.Request(
        url,
        data=(json.dumps(data).encode() if data is not None else b""),
        headers={"content-type": "application/json"},
        method="POST",
    )
    return urllib.request.urlopen(req, timeout=timeout).read()

print("starting torch profiler...")
post("/start_profile")
time.sleep(0.2)

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
usage = body.get("usage", {})

print("stopping torch profiler (may flush traces for a few seconds)...")
post("/stop_profile", timeout=300)

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

# Give torch profiler time to flush traces (it writes asynchronously)
sleep 20

# Tear down serve
echo "tearing down serve..."
kill -TERM "-${SERVE_PGID}" 2>/dev/null || true
sleep 5
pkill -KILL -f "vllm.entrypoints" 2>/dev/null || true
pkill -KILL -f "VLLM::Worker" 2>/dev/null || true
sleep 3

# Inventory trace files
echo "trace files in ${trace_dir}:"
ls -lh "${trace_dir}/" | tail -5

# Build kernel summary from the trace JSON. Aggregate "cat == kernel" events
# by name across all workers. We use a quoted heredoc + env vars to keep bash
# from mangling Python f-string `${var}` interpolations.
TRACE_DIR="${trace_dir}" OUT_DIR_PY="${OUT_DIR}" CLIENT_LOG_PY="${client_log}" \
PROFILE_LABEL_PY="${PROFILE_LABEL}" python3 - <<'PYEOF' > "${OUT_DIR}/torch_kernel_summary.md"
import json, csv, glob, os
from collections import defaultdict

trace_dir = os.environ["TRACE_DIR"]
out_dir = os.environ["OUT_DIR_PY"]
client_log = os.environ["CLIENT_LOG_PY"]
profile_label = os.environ["PROFILE_LABEL_PY"]

trace_files = sorted(glob.glob(f"{trace_dir}/*.json")) + sorted(glob.glob(f"{trace_dir}/*.json.gz"))
if not trace_files:
    print("# torch profiler trace: NO FILES FOUND")
    print()
    print(f"trace dir: {trace_dir}")
    print()
    print("Common causes: (1) /stop_profile was not called, (2) profiler-config")
    print("was not set at serve startup, (3) flush window too short.")
    raise SystemExit(1)

agg = defaultdict(lambda: {"total_us": 0.0, "count": 0})
for path in trace_files:
    opener = open
    mode = "r"
    if path.endswith(".gz"):
        import gzip
        opener = gzip.open
        mode = "rt"
    try:
        with opener(path, mode) as f:
            data = json.load(f)
    except Exception as e:
        print(f"# skip {path}: {e}")
        continue
    events = data.get("traceEvents", []) if isinstance(data, dict) else []
    for ev in events:
        if ev.get("cat") != "kernel":
            continue
        name = ev.get("name") or ev.get("args", {}).get("name") or "?"
        dur_us = float(ev.get("dur") or 0)
        agg[name]["total_us"] += dur_us
        agg[name]["count"] += 1

rows = sorted(agg.items(), key=lambda kv: kv[1]["total_us"], reverse=True)
total_us = sum(v["total_us"] for v in agg.values()) or 1.0

with open(f"{out_dir}/torch_kernel_summary.csv", "w") as f:
    w = csv.writer(f)
    w.writerow(["rank", "time_pct", "total_ms", "instances", "avg_us", "kernel"])
    for i, (name, v) in enumerate(rows, 1):
        w.writerow([
            i,
            f"{100*v['total_us']/total_us:.2f}",
            f"{v['total_us']/1000:.2f}",
            v["count"],
            f"{(v['total_us']/v['count']) if v['count'] else 0:.2f}",
            name,
        ])

print(f"# torch profiler kernel summary — {profile_label}")
print()
try:
    meta = json.load(open(client_log))
    print(f"Capture window: {meta['elapsed_s']:.2f}s, completion_tokens={meta['usage'].get('completion_tokens')}, max_tokens={meta['max_tokens']}")
    print()
except Exception:
    pass
print(f"Trace files: {len(trace_files)}, total kernel time aggregated: {total_us/1000:.1f} ms")
print()
print("| rank | time % | total ms | instances | avg us | kernel |")
print("|---|---|---|---|---|---|")
for i, (name, v) in enumerate(rows[:30], 1):
    pct = 100 * v["total_us"] / total_us
    avg_us = v["total_us"] / v["count"] if v["count"] else 0
    short = (name[:96] + "...") if len(name) > 99 else name
    print(f"| {i} | {pct:.2f} | {v['total_us']/1000:.2f} | {v['count']} | {avg_us:.2f} | `{short}` |")
PYEOF

echo "wrote ${OUT_DIR}/torch_kernel_summary.md"
