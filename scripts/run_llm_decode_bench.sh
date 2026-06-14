#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
LLM_DECODE_BENCH_VARIANT="${LLM_DECODE_BENCH_VARIANT:-manual}"
LLM_DECODE_BENCH_LABEL="${LLM_DECODE_BENCH_LABEL:-llm_decode_bench}"
LLM_DECODE_BENCH_SOURCE_URL="${LLM_DECODE_BENCH_SOURCE_URL:-https://raw.githubusercontent.com/local-inference-lab/llm-inference-bench/main/llm_decode_bench.py}"
LLM_DECODE_BENCH_SCRIPT="${LLM_DECODE_BENCH_SCRIPT:-}"
LLM_DECODE_BENCH_CONCURRENCY="${LLM_DECODE_BENCH_CONCURRENCY:-1,2,4,8,16,32,64,128}"
# Keep the default long context at 124k so 124k + 4096 output fits
# DeepSeek V4 Flash's 131072 token model window.
LLM_DECODE_BENCH_CONTEXTS="${LLM_DECODE_BENCH_CONTEXTS:-0,16k,32k,64k,124k}"
LLM_DECODE_BENCH_PREFILL_CONTEXTS="${LLM_DECODE_BENCH_PREFILL_CONTEXTS:-8k,64k,124k}"
LLM_DECODE_BENCH_MAX_TOKENS="${LLM_DECODE_BENCH_MAX_TOKENS:-4096}"
LLM_DECODE_BENCH_DURATION="${LLM_DECODE_BENCH_DURATION:-30}"
LLM_DECODE_BENCH_TOKEN_TARGETING="${LLM_DECODE_BENCH_TOKEN_TARGETING:-estimate}"
LLM_DECODE_BENCH_DISPLAY_MODE="${LLM_DECODE_BENCH_DISPLAY_MODE:-plain}"
LLM_DECODE_BENCH_KV_BUDGET="${LLM_DECODE_BENCH_KV_BUDGET:-}"
LLM_DECODE_BENCH_MAX_TOTAL_TOKENS="${LLM_DECODE_BENCH_MAX_TOTAL_TOKENS:-}"
LLM_DECODE_BENCH_DCP_SIZE="${LLM_DECODE_BENCH_DCP_SIZE:-}"
LLM_DECODE_BENCH_SKIP_PREFILL="${LLM_DECODE_BENCH_SKIP_PREFILL:-0}"
LLM_DECODE_BENCH_STANDALONE_PREFILL="${LLM_DECODE_BENCH_STANDALONE_PREFILL:-0}"
LLM_DECODE_BENCH_RUN_BURST="${LLM_DECODE_BENCH_RUN_BURST:-0}"
LLM_DECODE_BENCH_NO_HW_MONITOR="${LLM_DECODE_BENCH_NO_HW_MONITOR:-1}"
LLM_DECODE_BENCH_EXTRA_ARGS="${LLM_DECODE_BENCH_EXTRA_ARGS:-}"
LLM_DECODE_BENCH_TIMEOUT="${LLM_DECODE_BENCH_TIMEOUT:-7200}"
SERVE_LOG="${SERVE_LOG:-}"
SERVER_GUARD="${SERVER_GUARD:-1}"
SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT:-1800}"
SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS:-15}"
SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT:-10}"
SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT:-300}"
SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS:-10}"
SERVER_RECOVERY_CMD="${SERVER_RECOVERY_CMD:-}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${LLM_DECODE_BENCH_LABEL}/${RUN_TIMESTAMP}}"

export BASE_URL HOST PORT MODEL PYTHON LLM_DECODE_BENCH_VARIANT
export LLM_DECODE_BENCH_LABEL LLM_DECODE_BENCH_SOURCE_URL
export LLM_DECODE_BENCH_SCRIPT LLM_DECODE_BENCH_CONCURRENCY
export LLM_DECODE_BENCH_CONTEXTS LLM_DECODE_BENCH_PREFILL_CONTEXTS
export LLM_DECODE_BENCH_MAX_TOKENS LLM_DECODE_BENCH_DURATION
export LLM_DECODE_BENCH_TOKEN_TARGETING LLM_DECODE_BENCH_DISPLAY_MODE
export LLM_DECODE_BENCH_KV_BUDGET LLM_DECODE_BENCH_MAX_TOTAL_TOKENS
export LLM_DECODE_BENCH_DCP_SIZE
export LLM_DECODE_BENCH_SKIP_PREFILL LLM_DECODE_BENCH_STANDALONE_PREFILL
export LLM_DECODE_BENCH_RUN_BURST LLM_DECODE_BENCH_NO_HW_MONITOR
export LLM_DECODE_BENCH_EXTRA_ARGS LLM_DECODE_BENCH_TIMEOUT
export SERVE_LOG SERVER_GUARD SERVER_STARTUP_TIMEOUT
export SERVER_STARTUP_INTERVAL_SECONDS SERVER_HEALTH_TIMEOUT
export SERVER_FAILURE_GRACE_TIMEOUT SERVER_FAILURE_GRACE_INTERVAL_SECONDS
export SERVER_RECOVERY_CMD ARTIFACT_ROOT RUN_TIMESTAMP BRANCH_NAME
export GPU_TOPOLOGY_SLUG OUT_DIR

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/vllm_collect_env.sh"
collect_vllm_env
source "${SCRIPT_DIR}/gpu_stats.sh"
source "${SCRIPT_DIR}/runtime_stats.sh"

cleanup() {
  stop_runtime_stats || true
  stop_gpu_stats || true
}
trap cleanup EXIT

start_gpu_stats
start_runtime_stats

if ! wait_for_server_ready \
    "${SERVER_STARTUP_TIMEOUT}" \
    "${SERVER_STARTUP_INTERVAL_SECONDS}" \
    "server startup before llm-decode-bench"; then
  printf '%s\n' "124" > "${OUT_DIR}/llm_decode_bench.exit_code"
  mark_server_unresponsive "llm_decode_bench" "server not ready before llm-decode-bench"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

bench_script="${LLM_DECODE_BENCH_SCRIPT}"
if [[ -z "${bench_script}" ]]; then
  bench_script="${OUT_DIR}/llm_decode_bench.py"
  "${PYTHON}" - <<'PY' "${LLM_DECODE_BENCH_SOURCE_URL}" "${bench_script}"
import pathlib
import sys
import urllib.request

url = sys.argv[1]
path = pathlib.Path(sys.argv[2])
with urllib.request.urlopen(url, timeout=60) as response:
    path.write_bytes(response.read())
PY
fi

if [[ ! -f "${bench_script}" ]]; then
  printf 'llm_decode_bench script not found: %s\n' "${bench_script}" >&2
  exit 2
fi

bench_args=(
  --host "${HOST}"
  --port "${PORT}"
  --model "${MODEL}"
  --concurrency "${LLM_DECODE_BENCH_CONCURRENCY}"
  --contexts "${LLM_DECODE_BENCH_CONTEXTS}"
  --prefill-contexts "${LLM_DECODE_BENCH_PREFILL_CONTEXTS}"
  --max-tokens "${LLM_DECODE_BENCH_MAX_TOKENS}"
  --duration "${LLM_DECODE_BENCH_DURATION}"
  --token-targeting "${LLM_DECODE_BENCH_TOKEN_TARGETING}"
  --display-mode "${LLM_DECODE_BENCH_DISPLAY_MODE}"
  --output "${OUT_DIR}/llm_decode_bench.json"
)
if [[ -n "${LLM_DECODE_BENCH_KV_BUDGET}" ]]; then
  bench_args+=(--kv-budget "${LLM_DECODE_BENCH_KV_BUDGET}")
fi
if [[ -n "${LLM_DECODE_BENCH_MAX_TOTAL_TOKENS}" ]]; then
  bench_args+=(--max-total-tokens "${LLM_DECODE_BENCH_MAX_TOTAL_TOKENS}")
fi
if [[ -n "${LLM_DECODE_BENCH_DCP_SIZE}" ]]; then
  bench_args+=(--dcp-size "${LLM_DECODE_BENCH_DCP_SIZE}")
fi
if [[ "${LLM_DECODE_BENCH_SKIP_PREFILL}" == "1" ]]; then
  bench_args+=(--skip-prefill)
fi
if [[ "${LLM_DECODE_BENCH_STANDALONE_PREFILL}" == "1" ]]; then
  bench_args+=(--standalone-prefill)
fi
if [[ "${LLM_DECODE_BENCH_RUN_BURST}" == "1" ]]; then
  bench_args+=(--run-burst)
fi
if [[ "${LLM_DECODE_BENCH_NO_HW_MONITOR}" == "1" ]]; then
  bench_args+=(--no-hw-monitor)
fi
if [[ -n "${LLM_DECODE_BENCH_EXTRA_ARGS}" ]]; then
  extra_args=()
  eval "extra_args=(${LLM_DECODE_BENCH_EXTRA_ARGS})"
  bench_args+=("${extra_args[@]}")
fi

{
  printf '#!/usr/bin/env bash\n'
  printf '%q ' "${PYTHON}" "${bench_script}" "${bench_args[@]}"
  printf '\n'
} > "${OUT_DIR}/llm_decode_bench_command.sh"
chmod +x "${OUT_DIR}/llm_decode_bench_command.sh"

set +e
if command -v timeout >/dev/null 2>&1; then
  timeout "${LLM_DECODE_BENCH_TIMEOUT}" \
    "${PYTHON}" "${bench_script}" "${bench_args[@]}" \
    > "${OUT_DIR}/llm_decode_bench.stdout" \
    2> "${OUT_DIR}/llm_decode_bench.stderr"
else
  "${PYTHON}" "${bench_script}" "${bench_args[@]}" \
    > "${OUT_DIR}/llm_decode_bench.stdout" \
    2> "${OUT_DIR}/llm_decode_bench.stderr"
fi
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/llm_decode_bench.exit_code"

"${PYTHON}" - <<'PY' \
  "${OUT_DIR}" "${LLM_DECODE_BENCH_LABEL}" "${LLM_DECODE_BENCH_VARIANT}" \
  "${LLM_DECODE_BENCH_TIMEOUT}" "${code}" "${BASE_URL}" "${HOST}" "${PORT}" \
  "${MODEL}" "${bench_script}" "${LLM_DECODE_BENCH_SOURCE_URL}" \
  "${LLM_DECODE_BENCH_CONCURRENCY}" "${LLM_DECODE_BENCH_CONTEXTS}" \
  "${LLM_DECODE_BENCH_MAX_TOKENS}" "${LLM_DECODE_BENCH_DURATION}"
import hashlib
import json
import pathlib
import sys

out_dir = pathlib.Path(sys.argv[1])
script_path = pathlib.Path(sys.argv[10])
summary = {
    "label": sys.argv[2],
    "variant": sys.argv[3],
    "timeout_seconds": int(sys.argv[4]) if sys.argv[4].isdigit() else sys.argv[4],
    "exit_code": int(sys.argv[5]),
    "base_url": sys.argv[6],
    "host": sys.argv[7],
    "port": int(sys.argv[8]),
    "model": sys.argv[9],
    "script": str(script_path),
    "source_url": sys.argv[11],
    "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
    "concurrency": sys.argv[12],
    "contexts": sys.argv[13],
    "max_tokens": int(sys.argv[14]),
    "duration_seconds": float(sys.argv[15]),
    "json_output": "llm_decode_bench.json",
    "stdout": "llm_decode_bench.stdout",
    "stderr": "llm_decode_bench.stderr",
}
(out_dir / "llm_decode_bench_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
(out_dir / "llm_decode_bench_summary.md").write_text(
    "\n".join(
        [
            "# LLM Decode Bench",
            "",
            f"- label: `{summary['label']}`",
            f"- variant: `{summary['variant']}`",
            f"- exit_code: `{summary['exit_code']}`",
            f"- model: `{summary['model']}`",
            f"- concurrency: `{summary['concurrency']}`",
            f"- contexts: `{summary['contexts']}`",
            f"- max_tokens: `{summary['max_tokens']}`",
            f"- duration_seconds: `{summary['duration_seconds']}`",
            f"- script_sha256: `{summary['script_sha256']}`",
            "- output: `llm_decode_bench.json`",
            "- stdout: `llm_decode_bench.stdout`",
            "- stderr: `llm_decode_bench.stderr`",
            "",
        ]
    ),
    encoding="utf-8",
)
PY

if [[ "${code}" != "0" ]] && ! wait_for_server_ready \
    "${SERVER_FAILURE_GRACE_TIMEOUT}" \
    "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
    "server after llm-decode-bench"; then
  mark_server_unresponsive "llm_decode_bench" "server unresponsive after llm-decode-bench"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
