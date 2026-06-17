#!/usr/bin/env bash
set -euo pipefail

# Standalone re-runnable gate for https://github.com/jasl/vllm/issues/19
# (reporter aqua001): with thinking disabled the SM12x DeepSeek-V4 serve must
# return ONLY the requested JSON array, not a prose preamble. The regression was
# the SM12x indexer non-contiguous-topk bug (fixed by jasl/vllm c0a489242); this
# gate runs aqua001's verbatim request against an ALREADY-RUNNING serve and fails
# if the response is not JSON-only.
#
# It does not manage the serve (like run_lm_eval.sh with SERVER_GUARD=0): point
# BASE_URL at a live DeepSeek-V4 serve. The same case also runs automatically as
# the `smoke_regression` gate inside run_acceptance.sh.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
PYTHON="${PYTHON:-python}"
API_REQUEST_RETRIES="${API_REQUEST_RETRIES:-2}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/sm120_issue19_instruction_following/${RUN_TIMESTAMP}}"
mkdir -p "${OUT_DIR}"

exec "${PYTHON}" -m ds4_harness.cli chat-smoke \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --tag issue19 \
  --temperature 0 \
  --request-retries "${API_REQUEST_RETRIES}" \
  --jsonl-output "${OUT_DIR}/issue19_instruction_following.jsonl" \
  --markdown-output "${OUT_DIR}/issue19_instruction_following.md"
