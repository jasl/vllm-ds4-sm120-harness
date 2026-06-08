#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
DECODE_THROUGHPUT_VARIANT="${DECODE_THROUGHPUT_VARIANT:-manual}"
DECODE_THROUGHPUT_CASE_NAME="${DECODE_THROUGHPUT_CASE_NAME:-decode_throughput_sequential_probe}"
DECODE_THROUGHPUT_SERIES_SPECS="${DECODE_THROUGHPUT_SERIES_SPECS:-fixed_temp1:fixed:1.0:20,cycle3_temp1:cycle3:1.0:20,fixed_temp0:fixed:0.0:20}"
DECODE_THROUGHPUT_MAX_TOKENS="${DECODE_THROUGHPUT_MAX_TOKENS:-512}"
DECODE_THROUGHPUT_TOP_P="${DECODE_THROUGHPUT_TOP_P:-1.0}"
DECODE_THROUGHPUT_TIMEOUT="${DECODE_THROUGHPUT_TIMEOUT:-300}"
DECODE_THROUGHPUT_SLOW_TOK_S_THRESHOLD="${DECODE_THROUGHPUT_SLOW_TOK_S_THRESHOLD:-36}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/decode_throughput_probe/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON DECODE_THROUGHPUT_VARIANT
export DECODE_THROUGHPUT_CASE_NAME DECODE_THROUGHPUT_SERIES_SPECS
export DECODE_THROUGHPUT_MAX_TOKENS DECODE_THROUGHPUT_TOP_P
export DECODE_THROUGHPUT_TIMEOUT DECODE_THROUGHPUT_SLOW_TOK_S_THRESHOLD
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
start_gpu_stats
start_runtime_stats
trap 'stop_runtime_stats; stop_gpu_stats' EXIT

if ! wait_for_server_ready \
    "${SERVER_STARTUP_TIMEOUT}" \
    "${SERVER_STARTUP_INTERVAL_SECONDS}" \
    "server startup before decode-throughput probe"; then
  printf '%s\n' "124" > "${OUT_DIR}/decode_throughput_probe.exit_code"
  mark_server_unresponsive \
    "decode_throughput_probe" \
    "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

set +e
"${PYTHON}" -m ds4_harness.cli decode-throughput-sequential-probe \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --variant "${DECODE_THROUGHPUT_VARIANT}" \
  --case-name "${DECODE_THROUGHPUT_CASE_NAME}" \
  --series-specs "${DECODE_THROUGHPUT_SERIES_SPECS}" \
  --max-tokens "${DECODE_THROUGHPUT_MAX_TOKENS}" \
  --top-p "${DECODE_THROUGHPUT_TOP_P}" \
  --timeout "${DECODE_THROUGHPUT_TIMEOUT}" \
  --slow-tok-s-threshold "${DECODE_THROUGHPUT_SLOW_TOK_S_THRESHOLD}" \
  --json-output "${OUT_DIR}/decode_throughput_probe.json" \
  --markdown-output "${OUT_DIR}/decode_throughput_probe.md"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/decode_throughput_probe.exit_code"
if [[ "${code}" != "0" ]] && ! wait_for_server_ready \
    "${SERVER_FAILURE_GRACE_TIMEOUT}" \
    "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
    "server after decode-throughput probe"; then
  mark_server_unresponsive \
    "decode_throughput_probe" \
    "server unresponsive after decode-throughput probe"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
