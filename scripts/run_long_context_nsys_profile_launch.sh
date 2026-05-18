#!/usr/bin/env bash
# Optional harness tool: launch a fresh vLLM serve under Nsight Systems and
# capture one long-context request window. This is for prefill critical-path
# analysis; it excludes model load and CUDA graph warmup by default.
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
#   PROFILE_LINE_COUNT  Synthetic long-context line count (default 4096).
#   PROFILE_PROMPT_FILE Prompt file path. When set, overrides line count.
#   PROFILE_CONCURRENCY Concurrent captured requests (default 1).
#   PROFILE_MAX_TOKENS  Completion token cap (default 64).
#   PROFILE_TEMPERATURE Default 0.0.
#   PROFILE_TOP_P       Default 1.0.
#   PROFILE_THINKING_MODE default non-thinking.
#   PROFILE_TIMEOUT     Per-request timeout seconds (default 3600).
#   PROFILE_WARMUP_MODE none | short | same (default none).
#   PROFILE_WARMUP_TOKENS Completion tokens for warmup requests (default 8).
#   STARTUP_TIMEOUT_S   Default 900.
#   NSYS_CAPTURE_MODE   bench_window (default) | full.
#
# Output:
#   serve.log
#   serve_command.txt
#   nsys_profile.nsys-rep
#   nsys_kernel_summary.csv
#   nsys_kernel_summary.md
#   profile_request.json
#   profile_client_stdout.log

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

PYTHON="${PYTHON:-python}"
NSYS_BIN="${NSYS_BIN:-nsys}"
SERVE_COMMAND="${SERVE_COMMAND:?set SERVE_COMMAND}"
OUT_DIR="${OUT_DIR:?set OUT_DIR}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
PROFILE_MODEL="${PROFILE_MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PROFILE_LINE_COUNT="${PROFILE_LINE_COUNT:-4096}"
PROFILE_PROMPT_FILE="${PROFILE_PROMPT_FILE:-}"
PROFILE_CONCURRENCY="${PROFILE_CONCURRENCY:-1}"
PROFILE_MAX_TOKENS="${PROFILE_MAX_TOKENS:-64}"
PROFILE_TEMPERATURE="${PROFILE_TEMPERATURE:-0.0}"
PROFILE_TOP_P="${PROFILE_TOP_P:-1.0}"
PROFILE_THINKING_MODE="${PROFILE_THINKING_MODE:-non-thinking}"
PROFILE_TIMEOUT="${PROFILE_TIMEOUT:-3600}"
PROFILE_WARMUP_MODE="${PROFILE_WARMUP_MODE:-none}"
PROFILE_WARMUP_TOKENS="${PROFILE_WARMUP_TOKENS:-8}"
PROFILE_LABEL="${PROFILE_LABEL:-long_context_prefill}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-900}"
NSYS_TRACE="${NSYS_TRACE:-cuda,nvtx}"
NSYS_CAPTURE_MODE="${NSYS_CAPTURE_MODE:-bench_window}"
NSYS_SESSION_NAME="${NSYS_SESSION_NAME:-harness_longctx_$$}"

case "${PROFILE_WARMUP_MODE}" in
  none|short|same) ;;
  *)
    echo "PROFILE_WARMUP_MODE must be none, short, or same (got '${PROFILE_WARMUP_MODE}')" >&2
    exit 2
    ;;
esac

case "${NSYS_CAPTURE_MODE}" in
  bench_window|full) ;;
  *)
    echo "NSYS_CAPTURE_MODE must be bench_window or full (got '${NSYS_CAPTURE_MODE}')" >&2
    exit 2
    ;;
esac

mkdir -p "${OUT_DIR}"
nsys_rep="${OUT_DIR}/nsys_profile.nsys-rep"
nsys_log="${OUT_DIR}/nsys_run.log"
serve_log="${OUT_DIR}/serve.log"
client_log="${OUT_DIR}/profile_request.json"
client_stdout="${OUT_DIR}/profile_client_stdout.log"

if ! command -v "${NSYS_BIN}" >/dev/null 2>&1; then
  echo "nsys not on PATH; set NSYS_BIN" >&2
  exit 2
fi

printf '%s\n' "${SERVE_COMMAND}" > "${OUT_DIR}/serve_command.txt"

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

run_client() {
  local phase="$1"
  PROFILE_PHASE="${phase}" \
    BASE_URL="${BASE_URL}" \
    PROFILE_MODEL="${PROFILE_MODEL}" \
    PROFILE_LINE_COUNT="${PROFILE_LINE_COUNT}" \
    PROFILE_PROMPT_FILE="${PROFILE_PROMPT_FILE}" \
    PROFILE_CONCURRENCY="${PROFILE_CONCURRENCY}" \
    PROFILE_MAX_TOKENS="${PROFILE_MAX_TOKENS}" \
    PROFILE_TEMPERATURE="${PROFILE_TEMPERATURE}" \
    PROFILE_TOP_P="${PROFILE_TOP_P}" \
    PROFILE_THINKING_MODE="${PROFILE_THINKING_MODE}" \
    PROFILE_TIMEOUT="${PROFILE_TIMEOUT}" \
    PROFILE_WARMUP_MODE="${PROFILE_WARMUP_MODE}" \
    PROFILE_WARMUP_TOKENS="${PROFILE_WARMUP_TOKENS}" \
    PROFILE_LABEL="${PROFILE_LABEL}" \
    CLIENT_LOG="${client_log}" \
    "${PYTHON}" - <<'PYEOF'
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ds4_harness.generation import thinking_extra_body
from ds4_harness.long_context_latency import (
    build_file_latency_prompt,
    build_synthetic_latency_prompt,
)
from ds4_harness.prefix_cache_probe import stream_chat_completion


def build_prompt():
    prompt_file = os.environ["PROFILE_PROMPT_FILE"]
    if prompt_file:
        return build_file_latency_prompt(Path(prompt_file))
    return build_synthetic_latency_prompt(line_count=int(os.environ["PROFILE_LINE_COUNT"]))


def build_payload(text: str, max_tokens: int) -> dict:
    payload = {
        "model": os.environ["PROFILE_MODEL"],
        "messages": [{"role": "user", "content": text}],
        "max_tokens": max_tokens,
        "temperature": float(os.environ["PROFILE_TEMPERATURE"]),
        "top_p": float(os.environ["PROFILE_TOP_P"]),
        "stream": True,
    }
    payload.update(thinking_extra_body(os.environ["PROFILE_THINKING_MODE"]))
    return payload


def run_one(index: int, prompt, *, max_tokens: int, phase: str) -> dict:
    result = stream_chat_completion(
        os.environ["BASE_URL"],
        "/v1/chat/completions",
        build_payload(prompt.text, max_tokens),
        float(os.environ["PROFILE_TIMEOUT"]),
        probe_metadata={
            "case": "long_context_nsys_profile",
            "variant": os.environ["PROFILE_LABEL"],
            "phase": phase,
            "request_index": index,
        },
    )
    response = result.get("response") if isinstance(result.get("response"), dict) else {}
    usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    return {
        "phase": phase,
        "request_index": index,
        "ttft_seconds": result.get("ttft_seconds"),
        "elapsed_seconds": result.get("elapsed_seconds"),
        "chunks": result.get("chunks"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }


phase = os.environ["PROFILE_PHASE"]
prompt = build_prompt()
concurrency = int(os.environ["PROFILE_CONCURRENCY"])
if phase == "warmup":
    mode = os.environ["PROFILE_WARMUP_MODE"]
    if mode == "none":
        print("warmup skipped")
        raise SystemExit(0)
    max_tokens = int(os.environ["PROFILE_WARMUP_TOKENS"])
    if mode == "short":
        prompt = build_synthetic_latency_prompt(line_count=128)
        concurrency = 1
else:
    max_tokens = int(os.environ["PROFILE_MAX_TOKENS"])

if concurrency == 1:
    rows = [run_one(1, prompt, max_tokens=max_tokens, phase=phase)]
else:
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(run_one, index, prompt, max_tokens=max_tokens, phase=phase)
            for index in range(1, concurrency + 1)
        ]
        rows = [future.result() for future in as_completed(futures)]
    rows.sort(key=lambda row: row["request_index"])

payload = {
    "label": os.environ["PROFILE_LABEL"],
    "phase": phase,
    "prompt": {
        "name": prompt.name,
        "source": prompt.source,
        "line_count": prompt.line_count,
        "prompt_file": prompt.prompt_file,
        "sha256": prompt.sha256,
    },
    "concurrency": concurrency,
    "max_tokens": max_tokens,
    "requests": rows,
}
print(json.dumps(payload, indent=2))
if phase == "capture":
    Path(os.environ["CLIENT_LOG"]).write_text(json.dumps(payload, indent=2), encoding="utf-8")
PYEOF
}

run_client warmup

if [[ "${NSYS_CAPTURE_MODE}" == "bench_window" ]]; then
  echo "starting nsys capture for session=${NSYS_SESSION_NAME}..."
  "${NSYS_BIN}" start \
    --session="${NSYS_SESSION_NAME}" \
    --output "${nsys_rep%.nsys-rep}" \
    --sample none \
    --cpuctxsw none \
    2>&1 | tail -3
fi

run_client capture > "${client_stdout}"
cat "${client_stdout}"

if [[ "${NSYS_CAPTURE_MODE}" == "bench_window" ]]; then
  echo "stopping nsys capture for session=${NSYS_SESSION_NAME}..."
  "${NSYS_BIN}" stop --session="${NSYS_SESSION_NAME}" 2>&1 | tail -5
fi

echo "tearing down nsys+serve pgid=${NSYS_PGID}..."
trap - EXIT
cleanup
stop_nsys_agent
sleep 10

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

python3 - <<PYEOF > "${OUT_DIR}/nsys_kernel_summary.md"
import csv
import json
from pathlib import Path

rows = []
with open("${OUT_DIR}/nsys_kernel_summary.csv", encoding="utf-8") as f:
    rows.extend(csv.DictReader(f))

print("# nsys kernel summary - ${PROFILE_LABEL}")
print()
try:
    meta = json.loads(Path("${client_log}").read_text(encoding="utf-8"))
    print(f"Capture requests: {len(meta.get('requests', []))}; concurrency={meta.get('concurrency')}; max_tokens={meta.get('max_tokens')}")
    for item in meta.get("requests", []):
        print(
            f"- request {item.get('request_index')}: "
            f"ttft={item.get('ttft_seconds')}s elapsed={item.get('elapsed_seconds')}s "
            f"prompt_tokens={item.get('prompt_tokens')} completion_tokens={item.get('completion_tokens')}"
        )
    print()
except Exception:
    pass

print("| rank | time % | total ms | instances | avg us | kernel |")
print("|---|---|---|---|---|---|")
for i, row in enumerate(rows[:30], 1):
    name = row.get("Name", "").strip()
    short = (name[:96] + "...") if len(name) > 99 else name
    pct = row.get("Time (%)", "0").strip()
    total_ns = float(row.get("Total Time (ns)", 0) or 0)
    inst = row.get("Instances", "0").strip()
    avg_ns = float(row.get("Avg (ns)", 0) or 0)
    print(f"| {i} | {pct} | {total_ns / 1e6:.2f} | {inst} | {avg_ns / 1e3:.2f} | {short} |")
PYEOF

echo "wrote ${OUT_DIR}/nsys_kernel_summary.md"
