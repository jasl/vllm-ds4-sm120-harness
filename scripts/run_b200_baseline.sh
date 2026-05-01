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
B200_BASELINE_LABEL="${B200_BASELINE_LABEL:-b200_official}"
B200_BASELINE_VARIANTS="${B200_BASELINE_VARIANTS:-nomtp,mtp}"
ARTIFACT_ARCHIVE_PREVIOUS="${ARTIFACT_ARCHIVE_PREVIOUS:-${B200_ARCHIVE_PREVIOUS:-1}}"
ARTIFACT_ARCHIVE_PREFIX="${ARTIFACT_ARCHIVE_PREFIX:-${B200_ARCHIVE_PREFIX:-${B200_BASELINE_LABEL}}}"
NO_MTP_CONCURRENCY="${NO_MTP_CONCURRENCY:-1,2,4,8,16,24}"
MTP_CONCURRENCY="${MTP_CONCURRENCY:-1,2,4,8,16,24}"
NUM_PROMPTS="${NUM_PROMPTS:-80}"
BENCH_TIMEOUT="${BENCH_TIMEOUT:-1800}"
TEMPERATURE="${TEMPERATURE:-1.0}"
RUN_RANDOM_LONG="${RUN_RANDOM_LONG:-1}"
RUN_ACCEPTANCE="${RUN_ACCEPTANCE:-1}"
RUN_BENCH_HF="${RUN_BENCH_HF:-1}"
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
export SERVER_GUARD SERVER_STARTUP_TIMEOUT SERVER_STARTUP_INTERVAL_SECONDS
export SERVER_HEALTH_TIMEOUT SERVER_FAILURE_PROBE_TIMEOUT SERVER_FAILURE_GRACE_TIMEOUT
export SERVER_FAILURE_GRACE_INTERVAL_SECONDS ARTIFACT_ROOT GPU_TOPOLOGY_SLUG
export VLLM_ENGINE_READY_TIMEOUT_S
export REAL_SCENARIO_REPEAT_COUNT QUALITY_TAG QUALITY_REPEAT_COUNT
export CODING_TAG CODING_REPEAT_COUNT TOOLCALL15_SCENARIO_SET
export TOOLCALL15_REPEAT_COUNT

if [[ -z "${MTP_SPECULATIVE_CONFIG+x}" ]]; then
  MTP_SPECULATIVE_CONFIG='{"method":"mtp","num_speculative_tokens":2}'
fi

ACTIVE_SERVER_PID=""
failures=0

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

write_summary() {
  {
    printf '# B200 Baseline Summary\n\n'
    printf -- '- label: `%s`\n' "${B200_BASELINE_LABEL}"
    printf -- '- archive_previous: `%s`, prefix `%s`\n' "${ARTIFACT_ARCHIVE_PREVIOUS}" "${ARTIFACT_ARCHIVE_PREFIX}"
    printf -- '- model: `%s`\n' "${MODEL}"
    printf -- '- base_url: `%s`\n' "${BASE_URL}"
    printf -- '- variants: `%s`\n' "${B200_BASELINE_VARIANTS}"
    printf -- '- no_mtp_concurrency: `%s`\n' "${NO_MTP_CONCURRENCY}"
    printf -- '- mtp_concurrency: `%s`\n' "${MTP_CONCURRENCY}"
    printf -- '- num_prompts: `%s`\n' "${NUM_PROMPTS}"
    printf -- '- acceptance: `%s`\n' "${RUN_ACCEPTANCE}"
    printf -- '- hf_benchmark: `%s`\n' "${RUN_BENCH_HF}"
    printf -- '- random_long: `%s`, concurrency `%s`, shape `%s/%s`, prompts `%s`\n' \
      "${RUN_RANDOM_LONG}" "${RANDOM_LONG_CONCURRENCY}" "${RANDOM_LONG_INPUT_LEN}" \
      "${RANDOM_LONG_OUTPUT_LEN}" "${RANDOM_LONG_NUM_PROMPTS}"
    printf -- '- oracle_export: `%s`\n' "${RUN_ORACLE_EXPORT}"
    printf -- '- real_scenario_repeat_count: `%s`\n' "${REAL_SCENARIO_REPEAT_COUNT:-3}"
    printf -- '- quality_tag: `%s`\n' "${QUALITY_TAG:-quality}"
    printf -- '- quality_repeat_count: `%s`\n' "${QUALITY_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT:-3}}"
    printf -- '- coding_tag: `%s`\n' "${CODING_TAG:-coding}"
    printf -- '- coding_repeat_count: `%s`\n' "${CODING_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT:-3}}"
    printf -- '- toolcall15_scenario_set: `%s`\n' "${TOOLCALL15_SCENARIO_SET:-both}"
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

if [[ ! -x "${PYTHON}" ]]; then
  printf 'PYTHON is not executable: %s\n' "${PYTHON}" >&2
  exit 2
fi
if [[ ! -x "${VLLM_BIN}" ]]; then
  printf 'VLLM_BIN is not executable: %s\n' "${VLLM_BIN}" >&2
  exit 2
fi

write_summary

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

  if [[ "${RUN_ACCEPTANCE}" == "1" || "${RUN_ACCEPTANCE}" == "true" ]]; then
    run_phase "${variant}" "acceptance" "${variant_dir}/acceptance" \
      env OUT_DIR="${variant_dir}/acceptance" \
        BASE_URL="${BASE_URL}" MODEL="${MODEL}" PYTHON="${PYTHON}" \
        RUN_TOOLCALL15="${RUN_TOOLCALL15}" SERVE_LOG="${serve_log}" \
        REAL_SCENARIO_REPEAT_COUNT="${REAL_SCENARIO_REPEAT_COUNT:-3}" \
        QUALITY_TAG="${QUALITY_TAG:-quality}" \
        QUALITY_REPEAT_COUNT="${QUALITY_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT:-3}}" \
        CODING_TAG="${CODING_TAG:-coding}" \
        CODING_REPEAT_COUNT="${CODING_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT:-3}}" \
        TOOLCALL15_SCENARIO_SET="${TOOLCALL15_SCENARIO_SET:-both}" \
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
  else
    bench_concurrency="${NO_MTP_CONCURRENCY}"
  fi

  if [[ "${RUN_BENCH_HF}" == "1" || "${RUN_BENCH_HF}" == "true" ]]; then
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

  if [[ "${RUN_RANDOM_LONG}" == "1" || "${RUN_RANDOM_LONG}" == "true" ]]; then
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

  if [[ "${RUN_ORACLE_EXPORT}" == "1" || "${RUN_ORACLE_EXPORT}" == "true" ]]; then
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
