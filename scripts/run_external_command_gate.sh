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
EXTERNAL_COMMAND="${EXTERNAL_COMMAND:-}"
EXTERNAL_COMMAND_LABEL="${EXTERNAL_COMMAND_LABEL:-external_command}"
EXTERNAL_COMMAND_TIMEOUT="${EXTERNAL_COMMAND_TIMEOUT:-7200}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/external_command/${RUN_TIMESTAMP}}"

if [[ -z "${EXTERNAL_COMMAND}" ]]; then
  printf '%s\n' "EXTERNAL_COMMAND must be set" >&2
  exit 2
fi

export BASE_URL HOST PORT MODEL PYTHON EXTERNAL_COMMAND EXTERNAL_COMMAND_LABEL
export EXTERNAL_COMMAND_TIMEOUT SERVE_LOG SERVER_GUARD SERVER_STARTUP_TIMEOUT
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

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before external command"; then
  printf '%s\n' "124" > "${OUT_DIR}/external_command.exit_code"
  mark_server_unresponsive "external_command" "server not ready before external command"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

printf '%s\n' "${EXTERNAL_COMMAND}" > "${OUT_DIR}/external_command.sh"
chmod +x "${OUT_DIR}/external_command.sh"

set +e
if command -v timeout >/dev/null 2>&1; then
  timeout "${EXTERNAL_COMMAND_TIMEOUT}" bash -lc "${EXTERNAL_COMMAND}" \
    > "${OUT_DIR}/external_command.stdout" \
    2> "${OUT_DIR}/external_command.stderr"
else
  bash -lc "${EXTERNAL_COMMAND}" \
    > "${OUT_DIR}/external_command.stdout" \
    2> "${OUT_DIR}/external_command.stderr"
fi
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/external_command.exit_code"

"${PYTHON}" - <<'PY' \
  "${OUT_DIR}" "${EXTERNAL_COMMAND_LABEL}" "${EXTERNAL_COMMAND_TIMEOUT}" "${code}" \
  "${BASE_URL}" "${MODEL}" "${EXTERNAL_COMMAND}"
import json
import pathlib
import sys

out_dir = pathlib.Path(sys.argv[1])
label = sys.argv[2]
timeout = sys.argv[3]
exit_code = int(sys.argv[4])
base_url = sys.argv[5]
model = sys.argv[6]
command = sys.argv[7]

summary = {
    "label": label,
    "exit_code": exit_code,
    "timeout_seconds": int(timeout) if timeout.isdigit() else timeout,
    "base_url": base_url,
    "model": model,
    "command": command,
    "stdout": "external_command.stdout",
    "stderr": "external_command.stderr",
}
(out_dir / "external_command_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
(out_dir / "external_command_summary.md").write_text(
    "\n".join(
        [
            "# External Command Gate",
            "",
            f"- label: `{label}`",
            f"- exit_code: `{exit_code}`",
            f"- timeout_seconds: `{timeout}`",
            f"- base_url: `{base_url}`",
            f"- model: `{model}`",
            "- stdout: `external_command.stdout`",
            "- stderr: `external_command.stderr`",
            "",
        ]
    ),
    encoding="utf-8",
)
PY

if [[ "${code}" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after external command"; then
  mark_server_unresponsive "external_command" "server unresponsive after external command"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
