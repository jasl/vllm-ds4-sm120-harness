#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PYTHON:-python3}"

source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASELINE_DIR="${SUBJECTIVE_BASELINE_DIR:-${REPO_ROOT}/baselines/20260501_b200_main_51295793a}"
SUBJECTIVE_OUTPUT_DIR="${SUBJECTIVE_OUTPUT_DIR:-${BASELINE_DIR}/subjective_quality}"
OFFICIAL_BASE_URL="${DEEPSEEK_BASE_URL:-https://api.deepseek.com}"
OFFICIAL_MODEL="${DEEPSEEK_MODEL:-deepseek-v4-flash}"
OFFICIAL_TIMEOUT="${OFFICIAL_TIMEOUT:-900}"
OFFICIAL_MAX_CASE_TOKENS="${OFFICIAL_MAX_CASE_TOKENS:-8192}"
OFFICIAL_REPEAT_COUNT="${OFFICIAL_REPEAT_COUNT:-3}"
OFFICIAL_PROMPT_ROOT="${OFFICIAL_PROMPT_ROOT:-${REPO_ROOT}/prompts}"
OFFICIAL_LANGUAGES="${OFFICIAL_LANGUAGES:-en,zh}"
OFFICIAL_THINKING_MODES="${OFFICIAL_THINKING_MODES:-non-thinking,think-high,think-max}"
OFFICIAL_RUN_TOOLCALL15="${OFFICIAL_RUN_TOOLCALL15:-1}"
OFFICIAL_TOOLCALL15_SCENARIO_SET="${OFFICIAL_TOOLCALL15_SCENARIO_SET:-en}"
OFFICIAL_TOOLCALL15_REPEAT_COUNT="${OFFICIAL_TOOLCALL15_REPEAT_COUNT:-${OFFICIAL_REPEAT_COUNT}}"
OFFICIAL_TOOLCALL15_MIN_POINTS="${OFFICIAL_TOOLCALL15_MIN_POINTS:-2}"
OFFICIAL_TOOLCALL15_TIMEOUT="${OFFICIAL_TOOLCALL15_TIMEOUT:-120}"
OFFICIAL_EXTRA_BODY_JSON="${OFFICIAL_EXTRA_BODY_JSON:-}"

if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  printf '%s\n' "DEEPSEEK_API_KEY is not set" >&2
  exit 2
fi

timestamp="$(date -u +%Y%m%d%H%M%S)"
OFFICIAL_ARTIFACT_DIR="${OFFICIAL_ARTIFACT_DIR:-${REPO_ROOT}/artifacts/official_api/${OFFICIAL_MODEL}/${timestamp}}"
mkdir -p "${OFFICIAL_ARTIFACT_DIR}"

generation_args=()
IFS=',' read -r -a official_languages <<< "${OFFICIAL_LANGUAGES}"
for language in "${official_languages[@]}"; do
  if [[ -n "${language}" ]]; then
    generation_args+=(--language "${language}")
  fi
done
IFS=',' read -r -a official_thinking_modes <<< "${OFFICIAL_THINKING_MODES}"
for thinking_mode in "${official_thinking_modes[@]}"; do
  if [[ -n "${thinking_mode}" ]]; then
    generation_args+=(--thinking-mode "${thinking_mode}")
  fi
done
if [[ -n "${OFFICIAL_EXTRA_BODY_JSON}" ]]; then
  generation_args+=(--extra-body-json "${OFFICIAL_EXTRA_BODY_JSON}")
fi

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
  "${generation_args[@]}"
generation_rc="$?"
set -e
printf '%s\n' "${generation_rc}" > "${OFFICIAL_ARTIFACT_DIR}/official_generation.exit_code"

if [[ "${OFFICIAL_RUN_TOOLCALL15}" == "1" || "${OFFICIAL_RUN_TOOLCALL15}" == "true" ]]; then
  set +e
  "${PYTHON}" -m ds4_harness.cli toolcall15 \
    --base-url "${OFFICIAL_BASE_URL}" \
    --model "${OFFICIAL_MODEL}" \
    --api-key-env DEEPSEEK_API_KEY \
    --extra-body-json "${OFFICIAL_EXTRA_BODY_JSON}" \
    --scenario-set "${OFFICIAL_TOOLCALL15_SCENARIO_SET}" \
    --repeat-count "${OFFICIAL_TOOLCALL15_REPEAT_COUNT}" \
    --min-points "${OFFICIAL_TOOLCALL15_MIN_POINTS}" \
    --timeout "${OFFICIAL_TOOLCALL15_TIMEOUT}" \
    --json-output "${OFFICIAL_ARTIFACT_DIR}/official_toolcall15.json"
  toolcall_rc="$?"
  set -e
  printf '%s\n' "${toolcall_rc}" > "${OFFICIAL_ARTIFACT_DIR}/official_toolcall15.exit_code"
fi

mkdir -p "${SUBJECTIVE_OUTPUT_DIR}/generation"
cp -R "${OFFICIAL_ARTIFACT_DIR}/generation/." "${SUBJECTIVE_OUTPUT_DIR}/generation/"
cp "${OFFICIAL_ARTIFACT_DIR}/official_generation.jsonl" "${SUBJECTIVE_OUTPUT_DIR}/official_generation.jsonl"
if [[ -f "${OFFICIAL_ARTIFACT_DIR}/official_toolcall15.json" ]]; then
  mkdir -p "${SUBJECTIVE_OUTPUT_DIR}/agentic"
  cp "${OFFICIAL_ARTIFACT_DIR}/official_toolcall15.json" "${SUBJECTIVE_OUTPUT_DIR}/agentic/official_api.json"
fi

printf 'official_artifact_dir=%s\n' "${OFFICIAL_ARTIFACT_DIR}"
printf 'subjective_output_dir=%s\n' "${SUBJECTIVE_OUTPUT_DIR}"
