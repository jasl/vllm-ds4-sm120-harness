#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PYTHON:-python3}"

source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

OFFICIAL_BASE_URL="${DEEPSEEK_BASE_URL:-https://api.deepseek.com}"
OFFICIAL_MODEL="${DEEPSEEK_MODEL:-deepseek-v4-flash}"
OFFICIAL_TIMEOUT="${OFFICIAL_TIMEOUT:-900}"
OFFICIAL_REPEAT_COUNT="${OFFICIAL_REPEAT_COUNT:-1}"
OFFICIAL_PROMPT_ROOT="${OFFICIAL_PROMPT_ROOT:-${REPO_ROOT}/prompts}"
OFFICIAL_GENERATION_PROMPTS="${OFFICIAL_GENERATION_PROMPTS:-translation_en_to_zh,translation_zh_to_en,writing_follow_instructions,writing_local_llm_tradeoffs}"
OFFICIAL_THINKING_MODES="${OFFICIAL_THINKING_MODES:-non-thinking,think-high,think-max}"
OFFICIAL_MAX_CASE_TOKENS="${OFFICIAL_MAX_CASE_TOKENS:-4096}"
OFFICIAL_SMOKE_CASES="${OFFICIAL_SMOKE_CASES:-math_7_times_8,capital_of_france,spanish_greeting}"
OFFICIAL_SMOKE_REPEAT_COUNT="${OFFICIAL_SMOKE_REPEAT_COUNT:-1}"
OFFICIAL_SMOKE_TIMEOUT="${OFFICIAL_SMOKE_TIMEOUT:-300}"
OFFICIAL_RUN_TOOLCALL15="${OFFICIAL_RUN_TOOLCALL15:-1}"
OFFICIAL_TOOLCALL15_SCENARIO_SET="${OFFICIAL_TOOLCALL15_SCENARIO_SET:-en}"
OFFICIAL_TOOLCALL15_REPEAT_COUNT="${OFFICIAL_TOOLCALL15_REPEAT_COUNT:-1}"
OFFICIAL_TOOLCALL15_MIN_POINTS="${OFFICIAL_TOOLCALL15_MIN_POINTS:-2}"
OFFICIAL_TOOLCALL15_TIMEOUT="${OFFICIAL_TOOLCALL15_TIMEOUT:-120}"
OFFICIAL_EXTRA_BODY_JSON="${OFFICIAL_EXTRA_BODY_JSON:-}"
OFFICIAL_STRICT="${OFFICIAL_STRICT:-0}"
OFFICIAL_BASELINE_DATE="${OFFICIAL_BASELINE_DATE:-$(date -u +%Y%m%d)}"

model_slug="$(printf '%s' "${OFFICIAL_MODEL}" | sed -E 's#[^A-Za-z0-9]+#_#g; s#^_+##; s#_+$##' | tr '[:upper:]' '[:lower:]')"
OFFICIAL_BASELINE_LABEL="${OFFICIAL_BASELINE_LABEL:-deepseek_official_api_${model_slug}}"
OFFICIAL_BASELINE_DIR="${OFFICIAL_BASELINE_DIR:-${REPO_ROOT}/baselines/${OFFICIAL_BASELINE_DATE}_${OFFICIAL_BASELINE_LABEL}}"

if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  printf '%s\n' "DEEPSEEK_API_KEY is not set" >&2
  exit 2
fi

timestamp="$(date -u +%Y%m%d%H%M%S)"
OFFICIAL_ARTIFACT_DIR="${OFFICIAL_ARTIFACT_DIR:-${REPO_ROOT}/artifacts/official_api/${OFFICIAL_MODEL}/${timestamp}}"
mkdir -p "${OFFICIAL_ARTIFACT_DIR}"

smoke_args=()
IFS=',' read -r -a smoke_cases <<< "${OFFICIAL_SMOKE_CASES}"
for smoke_case in "${smoke_cases[@]}"; do
  if [[ -n "${smoke_case}" ]]; then
    smoke_args+=(--case "${smoke_case}")
  fi
done

generation_args=()
IFS=',' read -r -a generation_prompts <<< "${OFFICIAL_GENERATION_PROMPTS}"
for prompt_name in "${generation_prompts[@]}"; do
  if [[ -n "${prompt_name}" ]]; then
    generation_args+=(--prompt "${prompt_name}")
  fi
done
IFS=',' read -r -a official_thinking_modes <<< "${OFFICIAL_THINKING_MODES}"
for thinking_mode in "${official_thinking_modes[@]}"; do
  if [[ -n "${thinking_mode}" ]]; then
    generation_args+=(--thinking-mode "${thinking_mode}")
  fi
done

extra_body_args=()
if [[ -n "${OFFICIAL_EXTRA_BODY_JSON}" ]]; then
  extra_body_args+=(--extra-body-json "${OFFICIAL_EXTRA_BODY_JSON}")
fi

set +e
"${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${OFFICIAL_BASE_URL}" \
  --model "${OFFICIAL_MODEL}" \
  --api-key-env DEEPSEEK_API_KEY \
  --repeat-count "${OFFICIAL_SMOKE_REPEAT_COUNT}" \
  --timeout "${OFFICIAL_SMOKE_TIMEOUT}" \
  --jsonl-output "${OFFICIAL_ARTIFACT_DIR}/official_smoke.jsonl" \
  --markdown-output "${OFFICIAL_ARTIFACT_DIR}/official_smoke.md" \
  ${extra_body_args[@]+"${extra_body_args[@]}"} \
  "${smoke_args[@]}"
smoke_rc="$?"
set -e
printf '%s\n' "${smoke_rc}" > "${OFFICIAL_ARTIFACT_DIR}/official_smoke.exit_code"

set +e
"${PYTHON}" -m ds4_harness.cli generation-matrix \
  --base-url "${OFFICIAL_BASE_URL}" \
  --model "${OFFICIAL_MODEL}" \
  --prompt-root "${OFFICIAL_PROMPT_ROOT}" \
  --variant official-api \
  --repeat-count "${OFFICIAL_REPEAT_COUNT}" \
  --api-key-env DEEPSEEK_API_KEY \
  --max-case-tokens "${OFFICIAL_MAX_CASE_TOKENS}" \
  --timeout "${OFFICIAL_TIMEOUT}" \
  --jsonl-output "${OFFICIAL_ARTIFACT_DIR}/official_generation.jsonl" \
  --markdown-output-dir "${OFFICIAL_ARTIFACT_DIR}/generation" \
  ${extra_body_args[@]+"${extra_body_args[@]}"} \
  "${generation_args[@]}"
generation_rc="$?"
set -e
printf '%s\n' "${generation_rc}" > "${OFFICIAL_ARTIFACT_DIR}/official_generation.exit_code"

toolcall_rc=0
if [[ "${OFFICIAL_RUN_TOOLCALL15}" == "1" || "${OFFICIAL_RUN_TOOLCALL15}" == "true" ]]; then
  set +e
  "${PYTHON}" -m ds4_harness.cli toolcall15 \
    --base-url "${OFFICIAL_BASE_URL}" \
    --model "${OFFICIAL_MODEL}" \
    --api-key-env DEEPSEEK_API_KEY \
    --extra-body-json "${OFFICIAL_EXTRA_BODY_JSON:-{}}" \
    --scenario-set "${OFFICIAL_TOOLCALL15_SCENARIO_SET}" \
    --repeat-count "${OFFICIAL_TOOLCALL15_REPEAT_COUNT}" \
    --min-points "${OFFICIAL_TOOLCALL15_MIN_POINTS}" \
    --timeout "${OFFICIAL_TOOLCALL15_TIMEOUT}" \
    --json-output "${OFFICIAL_ARTIFACT_DIR}/official_toolcall15.json"
  toolcall_rc="$?"
  set -e
  printf '%s\n' "${toolcall_rc}" > "${OFFICIAL_ARTIFACT_DIR}/official_toolcall15.exit_code"
fi

baseline_parent="$(dirname "${OFFICIAL_BASELINE_DIR}")"
baseline_name="$(basename "${OFFICIAL_BASELINE_DIR}")"
mkdir -p "${baseline_parent}"
tmp_baseline_dir="$(mktemp -d "${baseline_parent}/.${baseline_name}.tmp.XXXXXX")"
cleanup_tmp_baseline() {
  rm -rf "${tmp_baseline_dir}"
}
trap cleanup_tmp_baseline EXIT

set +e
"${PYTHON}" -m ds4_harness.cli official-baseline \
  --artifact-dir "${OFFICIAL_ARTIFACT_DIR}" \
  --output-dir "${tmp_baseline_dir}" \
  --label "${OFFICIAL_BASELINE_LABEL}" \
  --date "${OFFICIAL_BASELINE_DATE}" \
  >/dev/null
bundle_rc="$?"
set -e
if [[ "${bundle_rc}" == "0" ]]; then
  rm -rf "${OFFICIAL_BASELINE_DIR}"
  mv "${tmp_baseline_dir}" "${OFFICIAL_BASELINE_DIR}"
  trap - EXIT
fi

printf 'official_artifact_dir=%s\n' "${OFFICIAL_ARTIFACT_DIR}"
printf 'official_baseline_dir=%s\n' "${OFFICIAL_BASELINE_DIR}"
printf 'report=%s\n' "${OFFICIAL_BASELINE_DIR}/report.md"

if [[ "${bundle_rc}" != "0" ]]; then
  exit "${bundle_rc}"
fi
if [[ "${OFFICIAL_STRICT}" == "1" || "${OFFICIAL_STRICT}" == "true" ]]; then
  if [[ "${smoke_rc}" != "0" || "${generation_rc}" != "0" || "${toolcall_rc}" != "0" ]]; then
    exit 1
  fi
fi
exit 0
