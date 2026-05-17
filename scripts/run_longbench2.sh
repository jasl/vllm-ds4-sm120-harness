#!/usr/bin/env bash
# Run the lm-evaluation-harness `longbench2` task against a fresh vllm serve
# launched at a user-specified max-model-len. LongBench-v2 prompts span
# 8K-2M tokens; the production baseline serve runs at 65K which is too
# small, so this phase tears down whatever the caller had running and
# launches its own serve at LONGBENCH2_MAX_MODEL_LEN before running lm-eval.
#
# Required env:
#   SERVE_COMMAND               Base vllm serve command (single string,
#                               word-split). The caller is expected to have
#                               already torn down any prior serve on the
#                               same host:port — we do not stop it here.
#   OUT_DIR                     Output directory.
#   LONGBENCH2_MAX_MODEL_LEN    Override max-model-len in SERVE_COMMAND.
#
# Optional env:
#   BASE_URL                    Default http://127.0.0.1:8000
#   LONGBENCH2_TASKS            Comma-separated lm-eval task names
#                               (default: longbench2 — the aggregate task).
#                               Available: longbench2, longbench2_single,
#                               longbench2_multi, longbench2_code,
#                               longbench2_legal_{single,multi},
#                               longbench2_history, longbench2_incontext, ...
#                               Run `lm-eval --tasks list | grep longbench2`
#                               on this host for the full list.
#   LONGBENCH2_LIMIT            --limit passed to lm_eval; default empty
#                               (run the whole task). Filtering by sample
#                               count is intentional: there is no
#                               server-side filter for prompt-token length,
#                               so very long Long-tier prompts will simply
#                               error if they exceed --max-model-len.
#   LONGBENCH2_BATCH_SIZE       Default auto.
#   LONGBENCH2_NUM_CONCURRENT   Default 1. LongBench-v2 prompts are large;
#                               more concurrency mostly stresses the KV
#                               cache without finishing faster.
#   LONGBENCH2_TIMEOUT_MS       Per-request timeout passed to lm-eval's
#                               model_args timeout. Default 1800000 (30 min)
#                               because 256K-context generation is slow.
#   LONGBENCH2_COMMAND_TIMEOUT  Wall-clock cap for the whole lm-eval run.
#                               Default 14400 (4 hours). Bump if running the
#                               full aggregate at 256K.
#   STARTUP_TIMEOUT_S           Default 1800.
#   LM_EVAL_BIN                 Default lm_eval.
#   LM_EVAL_TOKENIZER_BACKEND   Default none (so lm-eval relies on the
#                               server tokenizer; consistent with our other
#                               lm-eval phases).
#
# Output:
#   serve.log                   vLLM serve stdout/stderr
#   serve_command.txt           recorded command line
#   longbench2.exit_code        non-zero if lm-eval or serve fails
#   longbench2/raw/...          lm-eval raw results
#   longbench2.log              lm-eval stdout/stderr
#
# Notes
# -----
# We deliberately do NOT cap LongBench-v2 prompts by length client-side.
# The user controls reach via LONGBENCH2_MAX_MODEL_LEN — if you want only
# the "Short" tier (≤32K), set LONGBENCH2_MAX_MODEL_LEN=32768 and any
# longer prompts will receive HTTP 400 from the serve. That noise gets
# recorded in the raw results so a port team can see which prompts the
# server rejected.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

SERVE_COMMAND="${SERVE_COMMAND:?set SERVE_COMMAND}"
OUT_DIR="${OUT_DIR:?set OUT_DIR}"
LONGBENCH2_MAX_MODEL_LEN="${LONGBENCH2_MAX_MODEL_LEN:?set LONGBENCH2_MAX_MODEL_LEN}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
LONGBENCH2_TASKS="${LONGBENCH2_TASKS:-longbench2}"
LONGBENCH2_LIMIT="${LONGBENCH2_LIMIT:-}"
LONGBENCH2_BATCH_SIZE="${LONGBENCH2_BATCH_SIZE:-auto}"
LONGBENCH2_NUM_CONCURRENT="${LONGBENCH2_NUM_CONCURRENT:-1}"
LONGBENCH2_TIMEOUT_MS="${LONGBENCH2_TIMEOUT_MS:-1800000}"
LONGBENCH2_COMMAND_TIMEOUT="${LONGBENCH2_COMMAND_TIMEOUT:-14400}"
STARTUP_TIMEOUT_S="${STARTUP_TIMEOUT_S:-1800}"
LM_EVAL_BIN="${LM_EVAL_BIN:-lm_eval}"
LM_EVAL_TOKENIZER_BACKEND="${LM_EVAL_TOKENIZER_BACKEND:-none}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
MODEL_NAME_FOR_LM_EVAL="${MODEL_NAME_FOR_LM_EVAL:-${MODEL}}"

mkdir -p "${OUT_DIR}"
serve_log="${OUT_DIR}/serve.log"
raw_dir="${OUT_DIR}/longbench2/raw"
mkdir -p "${raw_dir}"

# Patch --max-model-len in the SERVE_COMMAND. We replace the first
# occurrence with the LongBench-v2 override. Using sed -E for a robust
# substitution that tolerates either '--max-model-len 65536' or
# '--max-model-len=65536' shape and quoted/unquoted values.
patched_serve_command="$(printf '%s' "${SERVE_COMMAND}" | sed -E \
  -e "s|--max-model-len[= ]+[0-9]+|--max-model-len ${LONGBENCH2_MAX_MODEL_LEN}|")"
if [[ "${patched_serve_command}" == "${SERVE_COMMAND}" ]]; then
  printf 'error: could not find --max-model-len in SERVE_COMMAND; refusing to launch\n' >&2
  printf '%s\n' "1" > "${OUT_DIR}/longbench2.exit_code"
  exit 2
fi
echo "${patched_serve_command}" > "${OUT_DIR}/serve_command.txt"

# Launch the serve in its own process group so we can kill the whole tree
# at the end (vllm spawns workers + multiprocessing helpers; setsid keeps
# them together).
setsid bash -c "${patched_serve_command}" > "${serve_log}" 2>&1 &
SERVE_PGID="$!"
echo "serve pgid=${SERVE_PGID} (max-model-len=${LONGBENCH2_MAX_MODEL_LEN}); waiting for /health..."

cleanup() {
  if kill -0 "${SERVE_PGID}" 2>/dev/null; then
    kill -TERM -"${SERVE_PGID}" 2>/dev/null || true
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      sleep 1
      kill -0 "${SERVE_PGID}" 2>/dev/null || break
    done
    if kill -0 "${SERVE_PGID}" 2>/dev/null; then
      kill -KILL -"${SERVE_PGID}" 2>/dev/null || true
    fi
  fi
}
trap cleanup EXIT INT TERM

# Wait for /health to return 200, OR for serve to die early, OR for the
# startup timeout to expire.
started_at="$(date +%s)"
while true; do
  if ! kill -0 "${SERVE_PGID}" 2>/dev/null; then
    printf 'error: serve process exited before /health became ready\n' >&2
    tail -50 "${serve_log}" >&2 || true
    printf '%s\n' "1" > "${OUT_DIR}/longbench2.exit_code"
    exit 1
  fi
  health_code="$(curl -s --max-time 5 "${BASE_URL}/health" -o /dev/null -w '%{http_code}' || echo 000)"
  if [[ "${health_code}" == "200" ]]; then
    echo "serve ready (${health_code}) after $(( $(date +%s) - started_at ))s"
    break
  fi
  elapsed="$(( $(date +%s) - started_at ))"
  if (( elapsed >= STARTUP_TIMEOUT_S )); then
    printf 'error: serve did not become ready within %ss\n' "${STARTUP_TIMEOUT_S}" >&2
    printf '%s\n' "124" > "${OUT_DIR}/longbench2.exit_code"
    exit 1
  fi
  sleep 5
done

# Build the lm-eval invocation. We use the local-completions client so
# lm-eval routes its prompts through our /v1/completions endpoint with
# tokenizer parity guaranteed by the server side.
model_args="model=${MODEL_NAME_FOR_LM_EVAL},base_url=${BASE_URL}/v1/completions,"
model_args+="num_concurrent=${LONGBENCH2_NUM_CONCURRENT},"
model_args+="max_retries=2,tokenized_requests=False,"
model_args+="tokenizer_backend=${LM_EVAL_TOKENIZER_BACKEND},"
model_args+="timeout=${LONGBENCH2_TIMEOUT_MS}"

limit_args=()
if [[ -n "${LONGBENCH2_LIMIT}" ]]; then
  limit_args+=(--limit "${LONGBENCH2_LIMIT}")
fi

task_args=()
IFS=',' read -r -a longbench_tasks <<< "${LONGBENCH2_TASKS}"
for task in "${longbench_tasks[@]}"; do
  [[ -n "${task}" ]] && task_args+=(--tasks "${task}")
done

eval_log="${OUT_DIR}/longbench2.log"
echo "running lm-eval: tasks=${LONGBENCH2_TASKS} limit=${LONGBENCH2_LIMIT:-(none)} concurrent=${LONGBENCH2_NUM_CONCURRENT}"

set +e
timeout --signal=TERM --kill-after=30 "${LONGBENCH2_COMMAND_TIMEOUT}" \
  "${LM_EVAL_BIN}" \
    --model local-completions \
    --model_args "${model_args}" \
    "${task_args[@]}" \
    --batch_size "${LONGBENCH2_BATCH_SIZE}" \
    --output_path "${raw_dir}" \
    "${limit_args[@]}" \
    > "${eval_log}" 2>&1
code="$?"
set -e

printf '%s\n' "${code}" > "${OUT_DIR}/longbench2.exit_code"

echo "lm-eval exit ${code}"
if [[ "${code}" -ne 0 ]]; then
  tail -50 "${eval_log}" >&2 || true
fi

echo "wrote ${OUT_DIR}"
exit "${code}"
