#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8080}"
BASE_URL="${BASE_URL:-http://${HOST}:${PORT}}"
B200_VLLM_REPO="${B200_VLLM_REPO:-/workspace/vllm}"
B200_VLLM_VENV="${B200_VLLM_VENV:-${B200_VLLM_REPO}/.venv}"
PYTHON="${PYTHON:-${B200_VLLM_VENV}/bin/python}"
VLLM_BIN="${VLLM_BIN:-${B200_VLLM_VENV}/bin/vllm}"
B200_TENSOR_PARALLEL_SIZE="${B200_TENSOR_PARALLEL_SIZE:-4}"
B200_BLOCK_SIZE="${B200_BLOCK_SIZE:-256}"
B200_KV_CACHE_DTYPE="${B200_KV_CACHE_DTYPE:-fp8}"
SERVE_MAX_MODEL_LEN="${SERVE_MAX_MODEL_LEN:-393216}"
B200_BASELINE_LABEL="${B200_BASELINE_LABEL:-b200_official}"
B200_BASELINE_VARIANTS="${B200_BASELINE_VARIANTS:-nomtp,mtp}"
B200_BASELINE_PHASES="${B200_BASELINE_PHASES:-all}"
B200_VARIANT_PARALLEL="${B200_VARIANT_PARALLEL:-0}"
B200_PARALLEL_GPU_GROUPS="${B200_PARALLEL_GPU_GROUPS:-nomtp=0,1;mtp=2,3}"
B200_PARALLEL_TENSOR_PARALLEL_SIZE="${B200_PARALLEL_TENSOR_PARALLEL_SIZE:-2}"
B200_PARALLEL_PORTS="${B200_PARALLEL_PORTS:-}"
B200_CUDA_VISIBLE_DEVICES="${B200_CUDA_VISIBLE_DEVICES:-}"
ARTIFACT_ARCHIVE_PREVIOUS="${ARTIFACT_ARCHIVE_PREVIOUS:-${B200_ARCHIVE_PREVIOUS:-1}}"
ARTIFACT_ARCHIVE_PREFIX="${ARTIFACT_ARCHIVE_PREFIX:-${B200_ARCHIVE_PREFIX:-${B200_BASELINE_LABEL}}}"
NO_MTP_CONCURRENCY="${NO_MTP_CONCURRENCY:-1,2,4,8,16,24}"
MTP_CONCURRENCY="${MTP_CONCURRENCY:-1,2,4,8,16,24}"
NUM_PROMPTS="${NUM_PROMPTS:-80}"
BENCH_TIMEOUT="${BENCH_TIMEOUT:-1800}"
TEMPERATURE="${TEMPERATURE:-1.0}"
RUN_RANDOM_LONG="${RUN_RANDOM_LONG:-1}"
RUN_LONG_CONTEXT_PROBE="${RUN_LONG_CONTEXT_PROBE:-1}"
RUN_ACCEPTANCE="${RUN_ACCEPTANCE:-1}"
RUN_BENCH_HF="${RUN_BENCH_HF:-1}"
RUN_LM_EVAL="${RUN_LM_EVAL:-1}"
LM_EVAL_BIN="${LM_EVAL_BIN:-${B200_VLLM_VENV}/bin/lm_eval}"
LM_EVAL_TASKS="${LM_EVAL_TASKS:-gsm8k}"
LM_EVAL_NUM_FEWSHOT="${LM_EVAL_NUM_FEWSHOT:-8}"
LM_EVAL_NUM_CONCURRENT="${LM_EVAL_NUM_CONCURRENT:-4}"
MTP_LM_EVAL_NUM_CONCURRENT="${MTP_LM_EVAL_NUM_CONCURRENT:-1}"
LM_EVAL_MAX_RETRIES="${LM_EVAL_MAX_RETRIES:-10}"
LM_EVAL_MAX_GEN_TOKS="${LM_EVAL_MAX_GEN_TOKS:-2048}"
LM_EVAL_TIMEOUT_MS="${LM_EVAL_TIMEOUT_MS:-60000}"
LM_EVAL_TOKENIZER_BACKEND="${LM_EVAL_TOKENIZER_BACKEND:-none}"
LM_EVAL_BATCH_SIZE="${LM_EVAL_BATCH_SIZE:-auto}"
LM_EVAL_COMMAND_TIMEOUT="${LM_EVAL_COMMAND_TIMEOUT:-7200}"
LM_EVAL_EXTRA_ARGS="${LM_EVAL_EXTRA_ARGS:-}"
RANDOM_LONG_CONCURRENCY="${RANDOM_LONG_CONCURRENCY:-1,2}"
RANDOM_LONG_NUM_PROMPTS="${RANDOM_LONG_NUM_PROMPTS:-8}"
RANDOM_LONG_INPUT_LEN="${RANDOM_LONG_INPUT_LEN:-8192}"
RANDOM_LONG_OUTPUT_LEN="${RANDOM_LONG_OUTPUT_LEN:-512}"
RANDOM_LONG_BENCH_TIMEOUT="${RANDOM_LONG_BENCH_TIMEOUT:-1800}"
RUN_ORACLE_EXPORT="${RUN_ORACLE_EXPORT:-1}"
ORACLE_LOGPROBS="${ORACLE_LOGPROBS:-20}"
ORACLE_TIMEOUT="${ORACLE_TIMEOUT:-300}"
RUN_TOOLCALL15="${RUN_TOOLCALL15:-1}"
VLLM_ENGINE_READY_TIMEOUT_S="${VLLM_ENGINE_READY_TIMEOUT_S:-3600}"
SERVER_GUARD="${SERVER_GUARD:-1}"
SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT:-3600}"
SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS:-15}"
SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT:-10}"
SERVER_FAILURE_PROBE_TIMEOUT="${SERVER_FAILURE_PROBE_TIMEOUT:-30}"
SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT:-300}"
SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS:-10}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
ARTIFACT_PARENT="${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}"
RUN_ROOT="${OUT_DIR:-${ARTIFACT_PARENT}/${B200_BASELINE_LABEL}/${RUN_TIMESTAMP}}"
export MODEL HOST PORT BASE_URL PYTHON VLLM_BIN RUN_TIMESTAMP BRANCH_NAME
export B200_VARIANT_PARALLEL B200_PARALLEL_GPU_GROUPS B200_PARALLEL_TENSOR_PARALLEL_SIZE
export B200_PARALLEL_PORTS B200_CUDA_VISIBLE_DEVICES
export SERVER_GUARD SERVER_STARTUP_TIMEOUT SERVER_STARTUP_INTERVAL_SECONDS
export SERVER_HEALTH_TIMEOUT SERVER_FAILURE_PROBE_TIMEOUT SERVER_FAILURE_GRACE_TIMEOUT
export SERVER_FAILURE_GRACE_INTERVAL_SECONDS ARTIFACT_ROOT GPU_TOPOLOGY_SLUG
export VLLM_ENGINE_READY_TIMEOUT_S SERVE_MAX_MODEL_LEN
export REAL_SCENARIO_REPEAT_COUNT GENERATION_PROMPT_ROOT GENERATION_LANGUAGES
export GENERATION_THINKING_MODES GENERATION_REPEAT_COUNT GENERATION_TIMEOUT
export GENERATION_MAX_CASE_TOKENS TOOLCALL15_SCENARIO_SET
export TOOLCALL15_REPEAT_COUNT
export RUN_LM_EVAL LM_EVAL_BIN LM_EVAL_TASKS LM_EVAL_NUM_FEWSHOT
export LM_EVAL_NUM_CONCURRENT MTP_LM_EVAL_NUM_CONCURRENT LM_EVAL_MAX_RETRIES
export LM_EVAL_MAX_GEN_TOKS LM_EVAL_TIMEOUT_MS LM_EVAL_TOKENIZER_BACKEND LM_EVAL_BATCH_SIZE
export LM_EVAL_COMMAND_TIMEOUT LM_EVAL_EXTRA_ARGS
export RUN_LONG_CONTEXT_PROBE LONG_CONTEXT_CASE_NAME LONG_CONTEXT_LINE_COUNT
export LONG_CONTEXT_MAX_TOKENS LONG_CONTEXT_TEMPERATURE LONG_CONTEXT_TOP_P
export LONG_CONTEXT_THINKING_MODE LONG_CONTEXT_TIMEOUT LONG_CONTEXT_REQUEST_RETRIES

if [[ -z "${MTP_SPECULATIVE_CONFIG+x}" ]]; then
  MTP_SPECULATIVE_CONFIG='{"method":"mtp","num_speculative_tokens":2}'
fi

ACTIVE_SERVER_PID=""
failures=0
VALID_BASELINE_PHASES=(
  acceptance
  long_context_probe
  bench_hf_mt_bench
  eval_gsm8k
  bench_random_8192x512
  oracle_export
)

validate_requested_phases() {
  local item
  local known
  local matched
  local -a requested_phases

  if [[ "${B200_BASELINE_PHASES}" == "all" ]]; then
    return 0
  fi

  IFS=',' read -r -a requested_phases <<< "${B200_BASELINE_PHASES}"
  for item in "${requested_phases[@]}"; do
    matched=0
    for known in "${VALID_BASELINE_PHASES[@]}"; do
      if [[ "${item}" == "${known}" ]]; then
        matched=1
        break
      fi
    done
    if [[ "${matched}" != "1" ]]; then
      printf 'unsupported B200 baseline phase: %s\n' "${item}" >&2
      printf '%s\n' \
        'valid phases: all,acceptance,long_context_probe,bench_hf_mt_bench,eval_gsm8k,bench_random_8192x512,oracle_export' >&2
      return 2
    fi
  done
}

archive_previous_runs() {
  if [[ "${ARTIFACT_ARCHIVE_PREVIOUS}" != "1" && "${ARTIFACT_ARCHIVE_PREVIOUS}" != "true" ]]; then
    return 0
  fi
  if [[ -n "${OUT_DIR:-}" ]]; then
    return 0
  fi
  if [[ ! -d "${ARTIFACT_PARENT}" ]]; then
    return 0
  fi

  local archive_dir="${ARTIFACT_PARENT}/_archive_before_${RUN_TIMESTAMP}"
  local manifest="${archive_dir}/archive_manifest.tsv"
  local moved=0
  local candidate name target suffix

  shopt -s nullglob
  for candidate in "${ARTIFACT_PARENT}/${ARTIFACT_ARCHIVE_PREFIX}"*; do
    if [[ ! -d "${candidate}" ]]; then
      continue
    fi
    name="$(basename -- "${candidate}")"
    if [[ "${name}" == _archive_before_* ]]; then
      continue
    fi

    mkdir -p "${archive_dir}"
    if [[ "${moved}" == "0" ]]; then
      printf '%s\t%s\n' "source" "target" > "${manifest}"
    fi

    target="${archive_dir}/${name}"
    suffix=1
    while [[ -e "${target}" ]]; do
      target="${archive_dir}/${name}.${suffix}"
      suffix=$((suffix + 1))
    done

    mv "${candidate}" "${target}"
    printf '%s\t%s\n' "${candidate}" "${target}" >> "${manifest}"
    moved=1
  done
  shopt -u nullglob

  if [[ "${moved}" == "1" ]]; then
    printf 'archived previous B200 artifacts to %s\n' "${archive_dir}"
  fi
}

validate_requested_phases
archive_previous_runs
mkdir -p "${RUN_ROOT}"
PHASE_LOG="${RUN_ROOT}/phase_exit_codes.tsv"
SUMMARY_MD="${RUN_ROOT}/baseline_summary.md"
printf '%s\t%s\t%s\t%s\n' "variant" "phase" "exit_code" "artifact_dir" > "${PHASE_LOG}"

clear_inherited_launch_env() {
  unset VLLM_ARGS
  unset VLLM_CACHE_ROOT
  unset VLLM_ENABLE_CUDA_COMPATIBILITY
  unset VLLM_MODEL
  unset VLLM_TEST_ENDPOINT
  unset VLLM_USAGE_SOURCE
  unset TORCH_CUDA_ARCH_LIST
  unset CUDA_VISIBLE_DEVICES
}

official_serve_args() {
  local variant="$1"
  OFFICIAL_SERVE_ARGS=(
    serve "${MODEL}"
    --trust-remote-code
    --kv-cache-dtype "${B200_KV_CACHE_DTYPE}"
    --block-size "${B200_BLOCK_SIZE}"
    --max-model-len "${SERVE_MAX_MODEL_LEN}"
    --tensor-parallel-size "${B200_TENSOR_PARALLEL_SIZE}"
    --host "${HOST}"
    --port "${PORT}"
    --no-enable-flashinfer-autotune
    --attention_config.use_fp4_indexer_cache=True
    --reasoning-parser deepseek_v4
    --tokenizer-mode deepseek_v4
    --tool-call-parser deepseek_v4
    --enable-auto-tool-choice
  )

  if [[ "${variant}" == "mtp" ]]; then
    OFFICIAL_SERVE_ARGS+=(--speculative_config "${MTP_SPECULATIVE_CONFIG}")
  fi

  if [[ -n "${B200_EXTRA_SERVE_ARGS:-}" ]]; then
    local extra_args=()
    # shellcheck disable=SC2206
    extra_args=(${B200_EXTRA_SERVE_ARGS})
    OFFICIAL_SERVE_ARGS+=("${extra_args[@]}")
  fi
}

write_command_file() {
  local command_file="$1"
  shift
  {
    printf '#!/usr/bin/env bash\n'
    printf 'export VLLM_ENGINE_READY_TIMEOUT_S=%q\n' "${VLLM_ENGINE_READY_TIMEOUT_S}"
    if [[ -n "${B200_CUDA_VISIBLE_DEVICES}" ]]; then
      local visible_devices="${B200_CUDA_VISIBLE_DEVICES//\\/\\\\}"
      visible_devices="${visible_devices//\"/\\\"}"
      printf 'export CUDA_VISIBLE_DEVICES="%s"\n' "${visible_devices}"
    fi
    printf '%q ' "$@"
    printf '\n'
  } > "${command_file}"
  chmod +x "${command_file}"
}

stop_active_server() {
  if [[ -z "${ACTIVE_SERVER_PID}" ]]; then
    return 0
  fi

  if kill -0 "${ACTIVE_SERVER_PID}" 2>/dev/null; then
    kill -- "-${ACTIVE_SERVER_PID}" 2>/dev/null || kill "${ACTIVE_SERVER_PID}" 2>/dev/null || true
    local attempt
    for attempt in {1..60}; do
      if ! kill -0 "${ACTIVE_SERVER_PID}" 2>/dev/null; then
        ACTIVE_SERVER_PID=""
        return 0
      fi
      sleep 1
    done
    kill -9 -- "-${ACTIVE_SERVER_PID}" 2>/dev/null || kill -9 "${ACTIVE_SERVER_PID}" 2>/dev/null || true
  fi

  ACTIVE_SERVER_PID=""
}

cleanup_and_exit() {
  stop_active_server
}
trap cleanup_and_exit EXIT INT TERM

start_server() {
  local variant="$1"
  local variant_dir="$2"
  local serve_log="$3"
  local command_file="${variant_dir}/serve_command.sh"

  official_serve_args "${variant}"
  write_command_file "${command_file}" "${VLLM_BIN}" "${OFFICIAL_SERVE_ARGS[@]}"
  printf '%s\n' "${VLLM_ENGINE_READY_TIMEOUT_S}" > "${variant_dir}/vllm_engine_ready_timeout_s.txt"

  clear_inherited_launch_env
  if [[ -n "${B200_CUDA_VISIBLE_DEVICES}" ]]; then
    export CUDA_VISIBLE_DEVICES="${B200_CUDA_VISIBLE_DEVICES}"
  fi
  if command -v setsid >/dev/null 2>&1; then
    setsid "${VLLM_BIN}" "${OFFICIAL_SERVE_ARGS[@]}" > "${serve_log}" 2>&1 &
  else
    "${VLLM_BIN}" "${OFFICIAL_SERVE_ARGS[@]}" > "${serve_log}" 2>&1 &
  fi
  ACTIVE_SERVER_PID="$!"
  printf '%s\n' "${ACTIVE_SERVER_PID}" > "${variant_dir}/server.pid"
}

wait_for_started_server() {
  local variant="$1"
  local startup_dir="$2"

  mkdir -p "${startup_dir}"
  OUT_DIR="${startup_dir}"
  export OUT_DIR
  source "${SCRIPT_DIR}/gpu_stats.sh"
  start_gpu_stats

  local started elapsed
  started="$(date +%s)"
  while true; do
    if server_ready; then
      stop_gpu_stats
      printf '%s\n' "0" > "${startup_dir}/server_startup.exit_code"
      printf '[%s] %s ready after %ss\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${variant}" "$(( $(date +%s) - started ))" \
        >> "${startup_dir}/server_wait.log"
      return 0
    fi

    if [[ -n "${ACTIVE_SERVER_PID}" ]] && ! kill -0 "${ACTIVE_SERVER_PID}" 2>/dev/null; then
      stop_gpu_stats
      printf '%s\n' "1" > "${startup_dir}/server_startup.exit_code"
      printf '%s\n' "vLLM process exited before readiness" > "${startup_dir}/server_startup.failed"
      return 1
    fi

    elapsed="$(($(date +%s) - started))"
    if (( elapsed >= SERVER_STARTUP_TIMEOUT )); then
      stop_gpu_stats
      printf '%s\n' "124" > "${startup_dir}/server_startup.exit_code"
      mark_server_unresponsive "server_startup" "server not ready after startup wait"
      return 1
    fi

    printf '[%s] waiting for %s startup: elapsed=%ss timeout=%ss\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${variant}" "${elapsed}" "${SERVER_STARTUP_TIMEOUT}" \
      >> "${startup_dir}/server_wait.log"
    sleep "${SERVER_STARTUP_INTERVAL_SECONDS}"
  done
}

record_phase() {
  local variant="$1"
  local phase="$2"
  local code="$3"
  local artifact_dir="$4"

  printf '%s\t%s\t%s\t%s\n' "${variant}" "${phase}" "${code}" "${artifact_dir}" >> "${PHASE_LOG}"
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi
}

run_phase() {
  local variant="$1"
  local phase="$2"
  local artifact_dir="$3"
  shift 3

  mkdir -p "${artifact_dir}"
  set +e
  "$@"
  local code="$?"
  set -e
  record_phase "${variant}" "${phase}" "${code}" "${artifact_dir}"
}

phase_enabled() {
  local phase="$1"
  local item
  local -a requested_phases

  if [[ "${B200_BASELINE_PHASES}" == "all" ]]; then
    return 0
  fi

  IFS=',' read -r -a requested_phases <<< "${B200_BASELINE_PHASES}"
  for item in "${requested_phases[@]}"; do
    if [[ "${item}" == "${phase}" ]]; then
      return 0
    fi
  done
  return 1
}

lm_eval_phase_enabled() {
  if [[ "${RUN_LM_EVAL}" != "1" && "${RUN_LM_EVAL}" != "true" ]]; then
    return 1
  fi
  phase_enabled "eval_gsm8k"
}

write_summary() {
  {
    printf '# B200 Baseline Summary\n\n'
    printf -- '- label: `%s`\n' "${B200_BASELINE_LABEL}"
    printf -- '- archive_previous: `%s`, prefix `%s`\n' "${ARTIFACT_ARCHIVE_PREVIOUS}" "${ARTIFACT_ARCHIVE_PREFIX}"
    printf -- '- model: `%s`\n' "${MODEL}"
    printf -- '- base_url: `%s`\n' "${BASE_URL}"
    printf -- '- variants: `%s`\n' "${B200_BASELINE_VARIANTS}"
    printf -- '- phases: `%s`\n' "${B200_BASELINE_PHASES}"
    printf -- '- variant_parallel: `%s`\n' "${B200_VARIANT_PARALLEL}"
    if [[ "${B200_VARIANT_PARALLEL}" == "1" || "${B200_VARIANT_PARALLEL}" == "true" ]]; then
      printf -- '- parallel_gpu_groups: `%s`\n' "${B200_PARALLEL_GPU_GROUPS}"
      printf -- '- parallel_ports: `%s`\n' "${B200_PARALLEL_PORTS:-nomtp=${PORT};mtp=$(default_parallel_mtp_port)}"
      printf -- '- parallel_tensor_parallel_size: `%s`\n' "${B200_PARALLEL_TENSOR_PARALLEL_SIZE}"
    fi
    printf -- '- serve_max_model_len: `%s`\n' "${SERVE_MAX_MODEL_LEN}"
    printf -- '- no_mtp_concurrency: `%s`\n' "${NO_MTP_CONCURRENCY}"
    printf -- '- mtp_concurrency: `%s`\n' "${MTP_CONCURRENCY}"
    printf -- '- num_prompts: `%s`\n' "${NUM_PROMPTS}"
    printf -- '- acceptance: `%s`\n' "${RUN_ACCEPTANCE}"
    printf -- '- long_context_probe: `%s`, lines `%s`, max tokens `%s`, thinking `%s`\n' \
      "${RUN_LONG_CONTEXT_PROBE}" "${LONG_CONTEXT_LINE_COUNT:-2400}" \
      "${LONG_CONTEXT_MAX_TOKENS:-128}" "${LONG_CONTEXT_THINKING_MODE:-non-thinking}"
    printf -- '- hf_benchmark: `%s`\n' "${RUN_BENCH_HF}"
    printf -- '- lm_eval: `%s`, tasks `%s`, fewshot `%s`, no-MTP concurrency `%s`, MTP concurrency `%s`\n' \
      "${RUN_LM_EVAL}" "${LM_EVAL_TASKS}" "${LM_EVAL_NUM_FEWSHOT}" \
      "${LM_EVAL_NUM_CONCURRENT}" "${MTP_LM_EVAL_NUM_CONCURRENT}"
    printf -- '- lm_eval_tokenizer_backend: `%s`\n' "${LM_EVAL_TOKENIZER_BACKEND}"
    printf -- '- random_long: `%s`, concurrency `%s`, shape `%s/%s`, prompts `%s`\n' \
      "${RUN_RANDOM_LONG}" "${RANDOM_LONG_CONCURRENCY}" "${RANDOM_LONG_INPUT_LEN}" \
      "${RANDOM_LONG_OUTPUT_LEN}" "${RANDOM_LONG_NUM_PROMPTS}"
    printf -- '- oracle_export: `%s`\n' "${RUN_ORACLE_EXPORT}"
    printf -- '- real_scenario_repeat_count: `%s`\n' "${REAL_SCENARIO_REPEAT_COUNT:-3}"
    printf -- '- api_request_retries: `%s`\n' "${API_REQUEST_RETRIES:-1}"
    printf -- '- generation_prompt_root: `%s`\n' "${GENERATION_PROMPT_ROOT:-${REPO_ROOT}/prompts}"
    printf -- '- generation_languages: `%s`\n' "${GENERATION_LANGUAGES:-en,zh}"
    printf -- '- generation_thinking_modes: `%s`\n' "${GENERATION_THINKING_MODES:-non-thinking,think-high,think-max}"
    printf -- '- generation_repeat_count: `%s`\n' "${GENERATION_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT:-3}}"
    printf -- '- generation_temperature: `%s`\n' "${GENERATION_TEMPERATURE:-1.0}"
    printf -- '- generation_top_p: `%s`\n' "${GENERATION_TOP_P:-1.0}"
    printf -- '- toolcall15_scenario_set: `%s`\n' "${TOOLCALL15_SCENARIO_SET:-en}"
    printf -- '- toolcall15_thinking_modes: `%s`\n' "${TOOLCALL15_THINKING_MODES:-${GENERATION_THINKING_MODES:-non-thinking,think-high,think-max}}"
    printf -- '- toolcall15_repeat_count: `%s`\n' "${TOOLCALL15_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT:-3}}"
    printf -- '- run_root: `%s`\n\n' "${RUN_ROOT}"
    printf '## Phase Exit Codes\n\n'
    printf '| Variant | Phase | Exit | Artifact Dir |\n'
    printf '| --- | --- | ---: | --- |\n'
    tail -n +2 "${PHASE_LOG}" | while IFS="$(printf '\t')" read -r variant phase code artifact_dir; do
      printf '| `%s` | `%s` | `%s` | `%s` |\n' "${variant}" "${phase}" "${code}" "${artifact_dir}"
    done
  } > "${SUMMARY_MD}"
}

variant_setting() {
  local mapping="$1"
  local variant="$2"
  local default_value="$3"
  local entry key value
  local -a entries

  IFS=';' read -r -a entries <<< "${mapping}"
  for entry in "${entries[@]}"; do
    if [[ -z "${entry}" || "${entry}" != *=* ]]; then
      continue
    fi
    key="${entry%%=*}"
    value="${entry#*=}"
    if [[ "${key}" == "${variant}" ]]; then
      printf '%s\n' "${value}"
      return 0
    fi
  done
  printf '%s\n' "${default_value}"
}

default_parallel_mtp_port() {
  if [[ "${PORT}" =~ ^[0-9]+$ ]]; then
    printf '%s\n' "$((PORT + 1))"
  else
    printf '%s\n' "8081"
  fi
}

parallel_mode_enabled() {
  [[ "${B200_VARIANT_PARALLEL}" == "1" || "${B200_VARIANT_PARALLEL}" == "true" ]]
}

validate_parallel_variants() {
  local item
  local count=0
  local has_nomtp=0
  local has_mtp=0
  local -a requested_variants

  IFS=',' read -r -a requested_variants <<< "${B200_BASELINE_VARIANTS}"
  for item in "${requested_variants[@]}"; do
    count=$((count + 1))
    if [[ "${item}" == "nomtp" ]]; then
      has_nomtp=1
    elif [[ "${item}" == "mtp" ]]; then
      has_mtp=1
    else
      printf 'parallel variant mode only supports nomtp,mtp; got %s\n' "${item}" >&2
      return 2
    fi
  done

  if [[ "${count}" != "2" || "${has_nomtp}" != "1" || "${has_mtp}" != "1" ]]; then
    printf 'parallel variant mode requires B200_BASELINE_VARIANTS=nomtp,mtp\n' >&2
    return 2
  fi
}

merge_parallel_child() {
  local variant="$1"
  local child_root="$2"
  local child_code="$3"
  local child_phase_log="${child_root}/phase_exit_codes.tsv"
  local child_variant_dir="${child_root}/${variant}"
  local target_variant_dir="${RUN_ROOT}/${variant}"
  local row_variant phase code artifact_dir

  if [[ -f "${child_phase_log}" ]]; then
    while IFS="$(printf '\t')" read -r row_variant phase code artifact_dir; do
      if [[ -z "${row_variant}" || -z "${phase}" ]]; then
        continue
      fi
      printf '%s\t%s\t%s\t%s\n' \
        "${row_variant}" "${phase}" "${code}" "${RUN_ROOT}/${row_variant}/${phase}" \
        >> "${PHASE_LOG}"
      if [[ "${code}" != "0" ]]; then
        failures=1
      fi
    done < <(tail -n +2 "${child_phase_log}")
  else
    record_phase "${variant}" "parallel_child" "${child_code}" "${child_root}"
  fi

  if [[ -d "${child_variant_dir}" ]]; then
    rm -rf "${target_variant_dir}"
    mv "${child_variant_dir}" "${target_variant_dir}"
  fi

  if [[ "${child_code}" == "0" ]]; then
    rm -rf "${child_root}"
  fi
}

run_parallel_variants() {
  validate_parallel_variants

  local nomtp_child="${RUN_ROOT}/_parallel_nomtp"
  local mtp_child="${RUN_ROOT}/_parallel_mtp"
  local nomtp_gpu mtp_gpu nomtp_port mtp_port
  local nomtp_pid mtp_pid nomtp_code mtp_code

  nomtp_gpu="$(variant_setting "${B200_PARALLEL_GPU_GROUPS}" "nomtp" "0,1")"
  mtp_gpu="$(variant_setting "${B200_PARALLEL_GPU_GROUPS}" "mtp" "2,3")"
  nomtp_port="$(variant_setting "${B200_PARALLEL_PORTS}" "nomtp" "${PORT}")"
  mtp_port="$(variant_setting "${B200_PARALLEL_PORTS}" "mtp" "$(default_parallel_mtp_port)")"

  rm -rf "${nomtp_child}" "${mtp_child}" "${RUN_ROOT}/nomtp" "${RUN_ROOT}/mtp"
  mkdir -p "${nomtp_child}" "${mtp_child}"

  env OUT_DIR="${nomtp_child}" \
    B200_VARIANT_PARALLEL=0 B200_BASELINE_VARIANTS=nomtp \
    B200_BASELINE_LABEL="${B200_BASELINE_LABEL}_nomtp" \
    B200_TENSOR_PARALLEL_SIZE="${B200_PARALLEL_TENSOR_PARALLEL_SIZE}" \
    B200_CUDA_VISIBLE_DEVICES="${nomtp_gpu}" \
    HOST="${HOST}" PORT="${nomtp_port}" BASE_URL="http://${HOST}:${nomtp_port}" \
    ARTIFACT_ARCHIVE_PREVIOUS=0 \
    "${SCRIPT_DIR}/run_b200_baseline.sh" \
    > "${nomtp_child}/driver.log" 2>&1 &
  nomtp_pid="$!"

  env OUT_DIR="${mtp_child}" \
    B200_VARIANT_PARALLEL=0 B200_BASELINE_VARIANTS=mtp \
    B200_BASELINE_LABEL="${B200_BASELINE_LABEL}_mtp" \
    B200_TENSOR_PARALLEL_SIZE="${B200_PARALLEL_TENSOR_PARALLEL_SIZE}" \
    B200_CUDA_VISIBLE_DEVICES="${mtp_gpu}" \
    HOST="${HOST}" PORT="${mtp_port}" BASE_URL="http://${HOST}:${mtp_port}" \
    ARTIFACT_ARCHIVE_PREVIOUS=0 \
    "${SCRIPT_DIR}/run_b200_baseline.sh" \
    > "${mtp_child}/driver.log" 2>&1 &
  mtp_pid="$!"

  set +e
  wait "${nomtp_pid}"
  nomtp_code="$?"
  wait "${mtp_pid}"
  mtp_code="$?"
  set -e

  merge_parallel_child "nomtp" "${nomtp_child}" "${nomtp_code}"
  merge_parallel_child "mtp" "${mtp_child}" "${mtp_code}"

  if [[ "${nomtp_code}" != "0" || "${mtp_code}" != "0" ]]; then
    failures=1
  fi
  write_summary
  echo "wrote ${RUN_ROOT}"
  exit "${failures}"
}

if [[ ! -x "${PYTHON}" ]]; then
  printf 'PYTHON is not executable: %s\n' "${PYTHON}" >&2
  exit 2
fi
if [[ ! -x "${VLLM_BIN}" ]]; then
  printf 'VLLM_BIN is not executable: %s\n' "${VLLM_BIN}" >&2
  exit 2
fi
if lm_eval_phase_enabled; then
  if [[ "${LM_EVAL_BIN}" == */* ]]; then
    if [[ ! -x "${LM_EVAL_BIN}" ]]; then
      printf 'LM_EVAL_BIN is not executable: %s\n' "${LM_EVAL_BIN}" >&2
      exit 2
    fi
  elif ! command -v "${LM_EVAL_BIN}" >/dev/null 2>&1; then
    printf 'LM_EVAL_BIN was not found on PATH: %s\n' "${LM_EVAL_BIN}" >&2
    exit 2
  fi
  if ! "${PYTHON}" - <<'PY' >/dev/null 2>&1
import importlib.util
import sys

missing = [
    name for name in ("lm_eval", "tenacity") if importlib.util.find_spec(name) is None
]
if missing:
    raise SystemExit(",".join(missing))
PY
  then
    printf 'lm_eval API dependencies are missing; install lm-eval[api] in the target venv\n' >&2
    exit 2
  fi
fi

write_summary

if parallel_mode_enabled; then
  run_parallel_variants
fi

variant_list="${B200_BASELINE_VARIANTS//,/ }"
for variant in ${variant_list}; do
  if [[ "${variant}" != "nomtp" && "${variant}" != "mtp" ]]; then
    printf 'unsupported B200 baseline variant: %s\n' "${variant}" >&2
    failures=1
    continue
  fi

  variant_dir="${RUN_ROOT}/${variant}"
  serve_log="${variant_dir}/serve.log"
  startup_dir="${variant_dir}/server_startup"
  mkdir -p "${variant_dir}"

  start_server "${variant}" "${variant_dir}" "${serve_log}"
  if wait_for_started_server "${variant}" "${startup_dir}"; then
    record_phase "${variant}" "server_startup" "0" "${startup_dir}"
  else
    code="$(cat "${startup_dir}/server_startup.exit_code" 2>/dev/null || printf '1')"
    record_phase "${variant}" "server_startup" "${code}" "${startup_dir}"
    stop_active_server
    write_summary
    continue
  fi

  if phase_enabled "acceptance" && { [[ "${RUN_ACCEPTANCE}" == "1" ]] || [[ "${RUN_ACCEPTANCE}" == "true" ]]; }; then
    run_phase "${variant}" "acceptance" "${variant_dir}/acceptance" \
      env OUT_DIR="${variant_dir}/acceptance" \
        BASE_URL="${BASE_URL}" MODEL="${MODEL}" PYTHON="${PYTHON}" \
        RUN_TOOLCALL15="${RUN_TOOLCALL15}" SERVE_LOG="${serve_log}" \
        REAL_SCENARIO_REPEAT_COUNT="${REAL_SCENARIO_REPEAT_COUNT:-3}" \
        API_REQUEST_RETRIES="${API_REQUEST_RETRIES:-1}" \
        GENERATION_PROMPT_ROOT="${GENERATION_PROMPT_ROOT:-${REPO_ROOT}/prompts}" \
        GENERATION_LANGUAGES="${GENERATION_LANGUAGES:-en,zh}" \
        GENERATION_THINKING_MODES="${GENERATION_THINKING_MODES:-non-thinking,think-high,think-max}" \
        GENERATION_VARIANT="${variant}" \
        GENERATION_REPEAT_COUNT="${GENERATION_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT:-3}}" \
        GENERATION_TEMPERATURE="${GENERATION_TEMPERATURE:-1.0}" \
        GENERATION_TOP_P="${GENERATION_TOP_P:-1.0}" \
        GENERATION_TIMEOUT="${GENERATION_TIMEOUT:-900}" \
        GENERATION_MAX_CASE_TOKENS="${GENERATION_MAX_CASE_TOKENS:-12000}" \
        TOOLCALL15_SCENARIO_SET="${TOOLCALL15_SCENARIO_SET:-en}" \
        TOOLCALL15_THINKING_MODES="${TOOLCALL15_THINKING_MODES:-${GENERATION_THINKING_MODES:-non-thinking,think-high,think-max}}" \
        TOOLCALL15_REPEAT_COUNT="${TOOLCALL15_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT:-3}}" \
        SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT}" \
        SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS}" \
        SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT}" \
        SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT}" \
        SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
        "${SCRIPT_DIR}/run_acceptance.sh"
  fi

  if [[ "${variant}" == "mtp" ]]; then
    bench_concurrency="${MTP_CONCURRENCY}"
    lm_eval_concurrency="${MTP_LM_EVAL_NUM_CONCURRENT}"
  else
    bench_concurrency="${NO_MTP_CONCURRENCY}"
    lm_eval_concurrency="${LM_EVAL_NUM_CONCURRENT}"
  fi

  if phase_enabled "long_context_probe" && { [[ "${RUN_LONG_CONTEXT_PROBE}" == "1" ]] || [[ "${RUN_LONG_CONTEXT_PROBE}" == "true" ]]; }; then
    run_phase "${variant}" "long_context_probe" "${variant_dir}/long_context_probe" \
      env OUT_DIR="${variant_dir}/long_context_probe" \
        BASE_URL="${BASE_URL}" MODEL="${MODEL}" PYTHON="${PYTHON}" SERVE_LOG="${serve_log}" \
        LONG_CONTEXT_VARIANT="${variant}" \
        LONG_CONTEXT_CASE_NAME="${LONG_CONTEXT_CASE_NAME:-kv_indexer_long_context}" \
        LONG_CONTEXT_LINE_COUNT="${LONG_CONTEXT_LINE_COUNT:-2400}" \
        LONG_CONTEXT_MAX_TOKENS="${LONG_CONTEXT_MAX_TOKENS:-128}" \
        LONG_CONTEXT_TEMPERATURE="${LONG_CONTEXT_TEMPERATURE:-0.0}" \
        LONG_CONTEXT_TOP_P="${LONG_CONTEXT_TOP_P:-1.0}" \
        LONG_CONTEXT_THINKING_MODE="${LONG_CONTEXT_THINKING_MODE:-non-thinking}" \
        LONG_CONTEXT_TIMEOUT="${LONG_CONTEXT_TIMEOUT:-1800}" \
        LONG_CONTEXT_REQUEST_RETRIES="${LONG_CONTEXT_REQUEST_RETRIES:-${API_REQUEST_RETRIES:-1}}" \
        SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT}" \
        SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS}" \
        SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT}" \
        SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT}" \
        SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
        "${SCRIPT_DIR}/run_long_context_probe.sh"
  fi

  if phase_enabled "bench_hf_mt_bench" && { [[ "${RUN_BENCH_HF}" == "1" ]] || [[ "${RUN_BENCH_HF}" == "true" ]]; }; then
    run_phase "${variant}" "bench_hf_mt_bench" "${variant_dir}/bench_hf_mt_bench" \
      env OUT_DIR="${variant_dir}/bench_hf_mt_bench" \
        BASE_URL="${BASE_URL}" MODEL="${MODEL}" PYTHON="${PYTHON}" VLLM_BIN="${VLLM_BIN}" \
        SERVE_LOG="${serve_log}" CONCURRENCY="${bench_concurrency}" \
        DATASET_NAME=hf DATASET_PATH=philschmid/mt-bench TOKENIZER_MODE=deepseek_v4 \
        NUM_PROMPTS="${NUM_PROMPTS}" TEMPERATURE="${TEMPERATURE}" BENCH_TIMEOUT="${BENCH_TIMEOUT}" \
        SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT}" \
        SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS}" \
        SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT}" \
        SERVER_FAILURE_PROBE_TIMEOUT="${SERVER_FAILURE_PROBE_TIMEOUT}" \
        SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT}" \
        SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
        "${SCRIPT_DIR}/run_bench_matrix.sh"
  fi

  if phase_enabled "eval_gsm8k" && { [[ "${RUN_LM_EVAL}" == "1" ]] || [[ "${RUN_LM_EVAL}" == "true" ]]; }; then
    run_phase "${variant}" "eval_gsm8k" "${variant_dir}/eval_gsm8k" \
      env OUT_DIR="${variant_dir}/eval_gsm8k" \
        BASE_URL="${BASE_URL}" MODEL="${MODEL}" PYTHON="${PYTHON}" \
        SERVE_LOG="${serve_log}" LM_EVAL_BIN="${LM_EVAL_BIN}" \
        LM_EVAL_TASKS="${LM_EVAL_TASKS}" \
        LM_EVAL_NUM_FEWSHOT="${LM_EVAL_NUM_FEWSHOT}" \
        LM_EVAL_NUM_CONCURRENT="${lm_eval_concurrency}" \
        LM_EVAL_MAX_RETRIES="${LM_EVAL_MAX_RETRIES}" \
        LM_EVAL_MAX_GEN_TOKS="${LM_EVAL_MAX_GEN_TOKS}" \
        LM_EVAL_TIMEOUT_MS="${LM_EVAL_TIMEOUT_MS}" \
        LM_EVAL_TOKENIZER_BACKEND="${LM_EVAL_TOKENIZER_BACKEND}" \
        LM_EVAL_BATCH_SIZE="${LM_EVAL_BATCH_SIZE}" \
        LM_EVAL_COMMAND_TIMEOUT="${LM_EVAL_COMMAND_TIMEOUT}" \
        LM_EVAL_EXTRA_ARGS="${LM_EVAL_EXTRA_ARGS}" \
        SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT}" \
        SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS}" \
        SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT}" \
        SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT}" \
        SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
        "${SCRIPT_DIR}/run_lm_eval.sh"
  fi

  if phase_enabled "bench_random_8192x512" && { [[ "${RUN_RANDOM_LONG}" == "1" ]] || [[ "${RUN_RANDOM_LONG}" == "true" ]]; }; then
    run_phase "${variant}" "bench_random_8192x512" "${variant_dir}/bench_random_8192x512" \
      env OUT_DIR="${variant_dir}/bench_random_8192x512" \
        BASE_URL="${BASE_URL}" MODEL="${MODEL}" PYTHON="${PYTHON}" VLLM_BIN="${VLLM_BIN}" \
        SERVE_LOG="${serve_log}" CONCURRENCY="${RANDOM_LONG_CONCURRENCY}" \
        DATASET_NAME=random TOKENIZER_MODE=deepseek_v4 \
        RANDOM_INPUT_LEN="${RANDOM_LONG_INPUT_LEN}" \
        RANDOM_OUTPUT_LEN="${RANDOM_LONG_OUTPUT_LEN}" \
        NUM_PROMPTS="${RANDOM_LONG_NUM_PROMPTS}" TEMPERATURE="${TEMPERATURE}" \
        BENCH_TIMEOUT="${RANDOM_LONG_BENCH_TIMEOUT}" IGNORE_EOS=1 \
        SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT}" \
        SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS}" \
        SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT}" \
        SERVER_FAILURE_PROBE_TIMEOUT="${SERVER_FAILURE_PROBE_TIMEOUT}" \
        SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT}" \
        SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
        "${SCRIPT_DIR}/run_bench_matrix.sh"
  fi

  if phase_enabled "oracle_export" && { [[ "${RUN_ORACLE_EXPORT}" == "1" ]] || [[ "${RUN_ORACLE_EXPORT}" == "true" ]]; }; then
    run_phase "${variant}" "oracle_export" "${variant_dir}/oracle_export" \
      env OUT_DIR="${variant_dir}/oracle_export" \
        BASE_URL="${BASE_URL}" MODEL="${MODEL}" PYTHON="${PYTHON}" SERVE_LOG="${serve_log}" \
        BASELINE_LABEL="${B200_BASELINE_LABEL}_${variant}_oracle" \
        ORACLE_LOGPROBS="${ORACLE_LOGPROBS}" ORACLE_TIMEOUT="${ORACLE_TIMEOUT}" \
        SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT}" \
        SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS}" \
        SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT}" \
        SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT}" \
        SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
        "${SCRIPT_DIR}/run_oracle_export.sh"
  fi

  stop_active_server
  write_summary
done

write_summary
echo "wrote ${RUN_ROOT}"
exit "${failures}"
