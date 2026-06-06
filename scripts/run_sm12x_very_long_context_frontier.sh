#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
VERY_LONG_CONTEXT_VARIANT="${VERY_LONG_CONTEXT_VARIANT:-manual}"
VERY_LONG_CONTEXT_CASE_NAME="${VERY_LONG_CONTEXT_CASE_NAME:-very_long_context_capacity}"
VERY_LONG_CONTEXT_TARGETS="${VERY_LONG_CONTEXT_TARGETS:-524288,786432,1048576}"
VERY_LONG_CONTEXT_MAX_TOKENS="${VERY_LONG_CONTEXT_MAX_TOKENS:-16}"
VERY_LONG_CONTEXT_TEMPERATURE="${VERY_LONG_CONTEXT_TEMPERATURE:-0.0}"
VERY_LONG_CONTEXT_TOP_P="${VERY_LONG_CONTEXT_TOP_P:-1.0}"
VERY_LONG_CONTEXT_THINKING_MODE="${VERY_LONG_CONTEXT_THINKING_MODE:-non-thinking}"
VERY_LONG_CONTEXT_EVALUATION_MODE="${VERY_LONG_CONTEXT_EVALUATION_MODE:-ttft-only}"
VERY_LONG_CONTEXT_CACHE_MODES="${VERY_LONG_CONTEXT_CACHE_MODES:-cold,warm}"
VERY_LONG_CONTEXT_REPEAT_COUNT="${VERY_LONG_CONTEXT_REPEAT_COUNT:-1}"
VERY_LONG_CONTEXT_TIMEOUT="${VERY_LONG_CONTEXT_TIMEOUT:-7200}"
VERY_LONG_CONTEXT_MATERIALIZE_TIMEOUT="${VERY_LONG_CONTEXT_MATERIALIZE_TIMEOUT:-2400}"
VERY_LONG_CONTEXT_SALT_RESERVATION_TOKENS="${VERY_LONG_CONTEXT_SALT_RESERVATION_TOKENS:-48}"
VERY_LONG_CONTEXT_TOKENIZER_MODE="${VERY_LONG_CONTEXT_TOKENIZER_MODE:-deepseek_v4}"
VERY_LONG_CONTEXT_RUN_LATENCY="${VERY_LONG_CONTEXT_RUN_LATENCY:-1}"
VERY_LONG_CONTEXT_RUN_LATENCY_ON_CAPACITY_FAIL="${VERY_LONG_CONTEXT_RUN_LATENCY_ON_CAPACITY_FAIL:-0}"
SERVE_LOG="${SERVE_LOG:-}"
SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT:-1800}"
SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS:-15}"
SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT:-10}"
SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT:-300}"
SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS:-10}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/very_long_context_capacity/${RUN_TIMESTAMP}}"
TARGET_PYTHON="${TARGET_PYTHON:-${PYTHON}}"

# The serve wrapper must keep full decode and piecewise graphs enabled. The
# literal also lets static tests catch accidental removal from this gate.
REQUIRED_CUDAGRAPH_MODE="FULL_AND_PIECEWISE"

export BASE_URL MODEL PYTHON VERY_LONG_CONTEXT_VARIANT
export VERY_LONG_CONTEXT_CASE_NAME VERY_LONG_CONTEXT_TARGETS
export VERY_LONG_CONTEXT_MAX_TOKENS VERY_LONG_CONTEXT_TEMPERATURE
export VERY_LONG_CONTEXT_TOP_P VERY_LONG_CONTEXT_THINKING_MODE
export VERY_LONG_CONTEXT_EVALUATION_MODE VERY_LONG_CONTEXT_CACHE_MODES
export VERY_LONG_CONTEXT_REPEAT_COUNT VERY_LONG_CONTEXT_TIMEOUT
export VERY_LONG_CONTEXT_MATERIALIZE_TIMEOUT
export VERY_LONG_CONTEXT_SALT_RESERVATION_TOKENS
export VERY_LONG_CONTEXT_TOKENIZER_MODE
export VERY_LONG_CONTEXT_RUN_LATENCY VERY_LONG_CONTEXT_RUN_LATENCY_ON_CAPACITY_FAIL
export SERVE_LOG SERVER_STARTUP_TIMEOUT SERVER_STARTUP_INTERVAL_SECONDS
export SERVER_HEALTH_TIMEOUT SERVER_FAILURE_GRACE_TIMEOUT
export SERVER_FAILURE_GRACE_INTERVAL_SECONDS ARTIFACT_ROOT RUN_TIMESTAMP
export BRANCH_NAME GPU_TOPOLOGY_SLUG OUT_DIR TARGET_PYTHON REQUIRED_CUDAGRAPH_MODE

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/vllm_collect_env.sh"
collect_vllm_env
source "${SCRIPT_DIR}/gpu_stats.sh"
source "${SCRIPT_DIR}/runtime_stats.sh"
start_gpu_stats
start_runtime_stats
trap 'stop_runtime_stats; stop_gpu_stats' EXIT

failures=0

if [[ -z "${SERVE_LOG}" || ! -f "${SERVE_LOG}" ]]; then
  printf 'SERVE_LOG must point to the active vLLM serve log for very-long capacity parsing\n' >&2
  printf '%s\n' "2" > "${OUT_DIR}/very_long_context_capacity.exit_code"
  failures=1
else
  if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before very-long context frontier"; then
    printf '%s\n' "124" > "${OUT_DIR}/server_ready.exit_code"
    mark_server_unresponsive "very_long_context_capacity" "server not ready after startup wait"
    failures=1
  fi
fi

capacity_code=125
if [[ "${failures}" == "0" ]]; then
  set +e
  "${PYTHON}" -m ds4_harness.cli very-long-context-capacity \
    --serve-log "${SERVE_LOG}" \
    --variant "${VERY_LONG_CONTEXT_VARIANT}" \
    --case-name "${VERY_LONG_CONTEXT_CASE_NAME}" \
    --targets "${VERY_LONG_CONTEXT_TARGETS}" \
    --json-output "${OUT_DIR}/very_long_context_capacity.json" \
    --markdown-output "${OUT_DIR}/very_long_context_capacity.md"
  capacity_code="$?"
  set -e
  printf '%s\n' "${capacity_code}" > "${OUT_DIR}/very_long_context_capacity.exit_code"
  if [[ "${capacity_code}" != "0" ]]; then
    failures=1
  fi
fi

latency_code=125
manifest_code=125
if { [[ "${capacity_code}" == "0" || "${VERY_LONG_CONTEXT_RUN_LATENCY_ON_CAPACITY_FAIL}" == "1" ]]; } \
    && [[ "${VERY_LONG_CONTEXT_RUN_LATENCY}" == "1" ]]; then
  set +e
  "${PYTHON}" -m ds4_harness.cli materialize-token-frontier-prompts \
    --target-python "${TARGET_PYTHON}" \
    --model "${MODEL}" \
    --tokenizer-mode "${VERY_LONG_CONTEXT_TOKENIZER_MODE}" \
    --output-dir "${OUT_DIR}/prompts" \
    --targets "${VERY_LONG_CONTEXT_TARGETS}" \
    --max-tokens "${VERY_LONG_CONTEXT_MAX_TOKENS}" \
    --salt-reservation-tokens "${VERY_LONG_CONTEXT_SALT_RESERVATION_TOKENS}" \
    --timeout "${VERY_LONG_CONTEXT_MATERIALIZE_TIMEOUT}" \
    --json-output "${OUT_DIR}/token_frontier_prompts.json" \
    --markdown-output "${OUT_DIR}/token_frontier_prompts.md"
  manifest_code="$?"
  set -e
  printf '%s\n' "${manifest_code}" > "${OUT_DIR}/token_frontier_prompts.exit_code"
  if [[ "${manifest_code}" != "0" ]]; then
    failures=1
  fi
fi

if [[ "${manifest_code}" == "0" ]]; then
  prompt_files="$("${PYTHON}" - <<'PY'
import json
import os
from pathlib import Path

manifest = Path(os.environ["OUT_DIR"]) / "token_frontier_prompts.json"
data = json.loads(manifest.read_text(encoding="utf-8"))
print(",".join(str(item["path"]) for item in data.get("prompts", [])))
PY
)"
  set +e
  OUT_DIR="${OUT_DIR}/long_context_latency_matrix" \
    BASE_URL="${BASE_URL}" MODEL="${MODEL}" PYTHON="${PYTHON}" SERVE_LOG="${SERVE_LOG}" \
    LONG_CONTEXT_LATENCY_VARIANT="${VERY_LONG_CONTEXT_VARIANT}" \
    LONG_CONTEXT_LATENCY_CASE_NAME="${VERY_LONG_CONTEXT_CASE_NAME}_frontier" \
    LONG_CONTEXT_LATENCY_LINE_COUNTS="" \
    LONG_CONTEXT_LATENCY_PROMPT_FILES="${prompt_files}" \
    LONG_CONTEXT_LATENCY_CONCURRENCY=1 \
    LONG_CONTEXT_LATENCY_CACHE_MODES="${VERY_LONG_CONTEXT_CACHE_MODES}" \
    LONG_CONTEXT_LATENCY_REPEAT_COUNT="${VERY_LONG_CONTEXT_REPEAT_COUNT}" \
    LONG_CONTEXT_LATENCY_MAX_TOKENS="${VERY_LONG_CONTEXT_MAX_TOKENS}" \
    LONG_CONTEXT_LATENCY_TEMPERATURE="${VERY_LONG_CONTEXT_TEMPERATURE}" \
    LONG_CONTEXT_LATENCY_TOP_P="${VERY_LONG_CONTEXT_TOP_P}" \
    LONG_CONTEXT_LATENCY_THINKING_MODE="${VERY_LONG_CONTEXT_THINKING_MODE}" \
    LONG_CONTEXT_LATENCY_EVALUATION_MODE="${VERY_LONG_CONTEXT_EVALUATION_MODE}" \
    LONG_CONTEXT_LATENCY_TIMEOUT="${VERY_LONG_CONTEXT_TIMEOUT}" \
    LONG_CONTEXT_LATENCY_PREWARM=0 \
    SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT}" \
    SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS}" \
    SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT}" \
    SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT}" \
    SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
    "${SCRIPT_DIR}/run_long_context_latency_matrix.sh"
  latency_code="$?"
  set -e
  printf '%s\n' "${latency_code}" > "${OUT_DIR}/long_context_latency_matrix.exit_code"
  if [[ "${latency_code}" != "0" ]]; then
    failures=1
  fi
fi

stop_runtime_stats
stop_gpu_stats
trap - EXIT

"${PYTHON}" - <<'PY'
import json
import os
from pathlib import Path

from ds4_harness.very_long_context import (
    build_frontier_summary,
    write_frontier_summary_markdown,
    write_json,
)

out_dir = Path(os.environ["OUT_DIR"])


def load(name):
    path = out_dir / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


summary = build_frontier_summary(
    capacity=load("very_long_context_capacity.json"),
    prompt_manifest=load("token_frontier_prompts.json"),
    latency_matrix=load("long_context_latency_matrix/long_context_latency_matrix.json"),
    runtime_stats=load("runtime_stats_summary.json"),
    gpu_stats=load("gpu_stats_summary.json"),
)
write_json(out_dir / "very_long_context_frontier_summary.json", summary)
write_frontier_summary_markdown(
    out_dir / "very_long_context_frontier_summary.md",
    summary,
)
PY

printf '%s\n' "${failures}" > "${OUT_DIR}/very_long_context_frontier.exit_code"
echo "wrote ${OUT_DIR}"
exit "${failures}"
