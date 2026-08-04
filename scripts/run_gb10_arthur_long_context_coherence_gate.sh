#!/usr/bin/env bash
set -euo pipefail

# Standalone re-runnable gate for https://github.com/vllm-project/vllm/pull/41834
# (reporter arthur): under long-context concurrent traffic the DeepSeek-V4 SM12x
# serve produced mixed-script gibberish. Shares the root cause of jasl/vllm#19
# (the SM12x indexer non-contiguous-topk bug dropping compressed context for the
# early queries of a long prompt), fixed by jasl/vllm c0a489242.
#
# Fires several long-context requests concurrently and fails if any response
# loses the planted needle codes (context following) or is incoherent
# (replacement chars / non-Latin gibberish / degenerate repetition).
#
# It does not manage the serve (like run_lm_eval.sh with SERVER_GUARD=0): point
# BASE_URL at a live DeepSeek-V4 serve. Defaults suit a dual-GB10 long-context
# serve; lower LINE_COUNT for a smaller max-model-len (e.g. 280 fits 32768).

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}"
PYTHON="${PYTHON:-python}"
COHERENCE_LINE_COUNT="${COHERENCE_LINE_COUNT:-900}"
COHERENCE_CONCURRENCY="${COHERENCE_CONCURRENCY:-12}"
COHERENCE_REPEAT_COUNT="${COHERENCE_REPEAT_COUNT:-2}"
COHERENCE_MAX_TOKENS="${COHERENCE_MAX_TOKENS:-384}"
COHERENCE_MAX_NON_LATIN_FRACTION="${COHERENCE_MAX_NON_LATIN_FRACTION:-0.15}"
COHERENCE_TIMEOUT="${COHERENCE_TIMEOUT:-900}"
API_REQUEST_RETRIES="${API_REQUEST_RETRIES:-1}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/gb10_arthur_long_context_coherence/${RUN_TIMESTAMP}}"
mkdir -p "${OUT_DIR}"

exec "${PYTHON}" -m ds4_harness.cli long-context-coherence-gate \
  --base-url "${BASE_URL}" \
  --model "${MODEL}" \
  --line-count "${COHERENCE_LINE_COUNT}" \
  --concurrency "${COHERENCE_CONCURRENCY}" \
  --repeat-count "${COHERENCE_REPEAT_COUNT}" \
  --max-tokens "${COHERENCE_MAX_TOKENS}" \
  --max-non-latin-fraction "${COHERENCE_MAX_NON_LATIN_FRACTION}" \
  --request-retries "${API_REQUEST_RETRIES}" \
  --timeout "${COHERENCE_TIMEOUT}" \
  --json-output "${OUT_DIR}/long_context_coherence.json"
