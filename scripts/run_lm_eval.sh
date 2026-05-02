#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
LM_EVAL_BIN="${LM_EVAL_BIN:-lm_eval}"
LM_EVAL_TASKS="${LM_EVAL_TASKS:-gsm8k}"
LM_EVAL_NUM_FEWSHOT="${LM_EVAL_NUM_FEWSHOT:-8}"
LM_EVAL_NUM_CONCURRENT="${LM_EVAL_NUM_CONCURRENT:-4}"
LM_EVAL_MAX_RETRIES="${LM_EVAL_MAX_RETRIES:-10}"
LM_EVAL_MAX_GEN_TOKS="${LM_EVAL_MAX_GEN_TOKS:-2048}"
LM_EVAL_TIMEOUT_MS="${LM_EVAL_TIMEOUT_MS:-60000}"
LM_EVAL_TOKENIZER_BACKEND="${LM_EVAL_TOKENIZER_BACKEND:-none}"
LM_EVAL_BATCH_SIZE="${LM_EVAL_BATCH_SIZE:-auto}"
LM_EVAL_COMMAND_TIMEOUT="${LM_EVAL_COMMAND_TIMEOUT:-7200}"
LM_EVAL_EXTRA_ARGS="${LM_EVAL_EXTRA_ARGS:-}"
SERVER_GUARD="${SERVER_GUARD:-1}"
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
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${RUN_TIMESTAMP}}"
export BASE_URL MODEL PYTHON LM_EVAL_BIN LM_EVAL_TASKS
export LM_EVAL_NUM_FEWSHOT LM_EVAL_NUM_CONCURRENT LM_EVAL_MAX_RETRIES
export LM_EVAL_MAX_GEN_TOKS LM_EVAL_TIMEOUT_MS LM_EVAL_TOKENIZER_BACKEND LM_EVAL_BATCH_SIZE
export LM_EVAL_COMMAND_TIMEOUT LM_EVAL_EXTRA_ARGS
export SERVER_GUARD SERVER_STARTUP_TIMEOUT SERVER_STARTUP_INTERVAL_SECONDS
export SERVER_HEALTH_TIMEOUT SERVER_FAILURE_GRACE_TIMEOUT SERVER_FAILURE_GRACE_INTERVAL_SECONDS
export ARTIFACT_ROOT RUN_TIMESTAMP BRANCH_NAME GPU_TOPOLOGY_SLUG OUT_DIR

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/vllm_collect_env.sh"
collect_vllm_env
source "${SCRIPT_DIR}/gpu_stats.sh"
source "${SCRIPT_DIR}/runtime_stats.sh"
start_gpu_stats
start_runtime_stats
trap 'stop_runtime_stats; stop_gpu_stats' EXIT

if ! wait_for_server_ready "${SERVER_STARTUP_TIMEOUT}" "${SERVER_STARTUP_INTERVAL_SECONDS}" "server startup before lm_eval"; then
  printf '%s\n' "124" > "${OUT_DIR}/lm_eval.exit_code"
  mark_server_unresponsive "lm_eval" "server not ready after startup wait"
  echo "wrote ${OUT_DIR}"
  exit 1
fi

task_args=()
IFS=',' read -r -a lm_eval_tasks <<< "${LM_EVAL_TASKS}"
for task in "${lm_eval_tasks[@]}"; do
  if [[ -n "${task}" ]]; then
    task_args+=(--task "${task}")
  fi
done

extra_args=()
if [[ -n "${LM_EVAL_EXTRA_ARGS}" ]]; then
  # shellcheck disable=SC2206
  extra_args=(${LM_EVAL_EXTRA_ARGS})
fi
cli_extra_args=()
for arg in "${extra_args[@]}"; do
  cli_extra_args+=("--extra-lm-eval-arg=${arg}")
done

set +e
"${PYTHON}" -m ds4_harness.cli lm-eval \
  --lm-eval-bin "${LM_EVAL_BIN}" \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  "${task_args[@]}" \
  --num-fewshot "${LM_EVAL_NUM_FEWSHOT}" \
  --num-concurrent "${LM_EVAL_NUM_CONCURRENT}" \
  --max-retries "${LM_EVAL_MAX_RETRIES}" \
  --max-gen-toks "${LM_EVAL_MAX_GEN_TOKS}" \
  --eval-timeout-ms "${LM_EVAL_TIMEOUT_MS}" \
  --tokenizer-backend "${LM_EVAL_TOKENIZER_BACKEND}" \
  --batch-size "${LM_EVAL_BATCH_SIZE}" \
  --command-timeout "${LM_EVAL_COMMAND_TIMEOUT}" \
  --output-dir "${OUT_DIR}" \
  --json-output "${OUT_DIR}/lm_eval_summary.json" \
  "${cli_extra_args[@]}"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/lm_eval.exit_code"
if [[ "${code}" != "0" ]] && ! wait_for_server_ready "${SERVER_FAILURE_GRACE_TIMEOUT}" "${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" "server after lm_eval"; then
  mark_server_unresponsive "lm_eval" "server unresponsive after lm_eval"
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
