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
OFFICIAL_THINKING_TYPE="${DEEPSEEK_THINKING_TYPE:-enabled}"
OFFICIAL_REASONING_EFFORT="${DEEPSEEK_REASONING_EFFORT:-high}"
OFFICIAL_EXTRA_BODY_JSON="${OFFICIAL_EXTRA_BODY_JSON:-{\"thinking\":{\"type\":\"${OFFICIAL_THINKING_TYPE}\"},\"reasoning_effort\":\"${OFFICIAL_REASONING_EFFORT}\"}}"

if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  printf '%s\n' "DEEPSEEK_API_KEY is not set" >&2
  exit 2
fi

timestamp="$(date -u +%Y%m%d-%H%M%S)"
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

run_smoke official_quality quality
run_smoke official_coding coding

"${PYTHON}" -m ds4_harness.cli subjective-comparison \
  --baseline-dir "${BASELINE_DIR}" \
  --official-input "${OFFICIAL_ARTIFACT_DIR}/official_quality.jsonl" \
  --official-input "${OFFICIAL_ARTIFACT_DIR}/official_coding.jsonl" \
  --output-dir "${SUBJECTIVE_OUTPUT_DIR}" \
  --label "$(basename "${BASELINE_DIR}")"

printf 'official_artifact_dir=%s\n' "${OFFICIAL_ARTIFACT_DIR}"
printf 'subjective_output_dir=%s\n' "${SUBJECTIVE_OUTPUT_DIR}"
