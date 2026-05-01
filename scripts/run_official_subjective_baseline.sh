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
OFFICIAL_QUALITY_TAG="${OFFICIAL_QUALITY_TAG:-quality}"
OFFICIAL_CODING_TAG="${OFFICIAL_CODING_TAG:-coding}"
OFFICIAL_REPEAT_COUNT="${OFFICIAL_REPEAT_COUNT:-3}"
OFFICIAL_RUN_TOOLCALL15="${OFFICIAL_RUN_TOOLCALL15:-1}"
OFFICIAL_TOOLCALL15_SCENARIO_SET="${OFFICIAL_TOOLCALL15_SCENARIO_SET:-both}"
OFFICIAL_TOOLCALL15_REPEAT_COUNT="${OFFICIAL_TOOLCALL15_REPEAT_COUNT:-${OFFICIAL_REPEAT_COUNT}}"
OFFICIAL_TOOLCALL15_MIN_POINTS="${OFFICIAL_TOOLCALL15_MIN_POINTS:-2}"
OFFICIAL_TOOLCALL15_TIMEOUT="${OFFICIAL_TOOLCALL15_TIMEOUT:-120}"
OFFICIAL_THINKING_TYPE="${DEEPSEEK_THINKING_TYPE:-enabled}"
OFFICIAL_REASONING_EFFORT="${DEEPSEEK_REASONING_EFFORT:-high}"
OFFICIAL_EXTRA_BODY_JSON="${OFFICIAL_EXTRA_BODY_JSON:-{\"thinking\":{\"type\":\"${OFFICIAL_THINKING_TYPE}\"},\"reasoning_effort\":\"${OFFICIAL_REASONING_EFFORT}\"}}"

if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  printf '%s\n' "DEEPSEEK_API_KEY is not set" >&2
  exit 2
fi

timestamp="$(date -u +%Y%m%d%H%M%S)"
OFFICIAL_ARTIFACT_DIR="${OFFICIAL_ARTIFACT_DIR:-${REPO_ROOT}/artifacts/official_api/${OFFICIAL_MODEL}/${timestamp}}"
mkdir -p "${OFFICIAL_ARTIFACT_DIR}"

run_smoke() {
  local name="$1"
  local tag="$2"
  local rc
  set +e
  "${PYTHON}" -m ds4_harness.cli chat-smoke \
    --base-url "${OFFICIAL_BASE_URL}" \
    --model "${OFFICIAL_MODEL}" \
    --tag "${tag}" \
    --repeat-count "${OFFICIAL_REPEAT_COUNT}" \
    --api-key-env DEEPSEEK_API_KEY \
    --max-case-tokens "${OFFICIAL_MAX_CASE_TOKENS}" \
    --extra-body-json "${OFFICIAL_EXTRA_BODY_JSON}" \
    --timeout "${OFFICIAL_TIMEOUT}" \
    --jsonl-output "${OFFICIAL_ARTIFACT_DIR}/${name}.jsonl" \
    --markdown-output "${OFFICIAL_ARTIFACT_DIR}/${name}.md"
  rc="$?"
  set -e
  printf '%s\n' "${rc}" > "${OFFICIAL_ARTIFACT_DIR}/${name}.exit_code"
}

run_smoke official_quality "${OFFICIAL_QUALITY_TAG}"
run_smoke official_coding "${OFFICIAL_CODING_TAG}"

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

subjective_args=(
  --baseline-dir "${BASELINE_DIR}"
  --official-input "${OFFICIAL_ARTIFACT_DIR}/official_quality.jsonl"
  --official-input "${OFFICIAL_ARTIFACT_DIR}/official_coding.jsonl"
  --output-dir "${SUBJECTIVE_OUTPUT_DIR}"
  --label "$(basename "${BASELINE_DIR}")"
)

if [[ -f "${OFFICIAL_ARTIFACT_DIR}/official_toolcall15.json" ]]; then
  subjective_args+=(--official-toolcall-input "${OFFICIAL_ARTIFACT_DIR}/official_toolcall15.json")
fi

"${PYTHON}" -m ds4_harness.cli subjective-comparison \
  "${subjective_args[@]}"

printf 'official_artifact_dir=%s\n' "${OFFICIAL_ARTIFACT_DIR}"
printf 'subjective_output_dir=%s\n' "${SUBJECTIVE_OUTPUT_DIR}"
