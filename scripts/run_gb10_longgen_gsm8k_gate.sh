#!/usr/bin/env bash
# Long-generation regression gate for the GB10 tokenspeed serve.
#
# WHY THIS GATE EXISTS: the 2026-07-09 latent IMA (unsanitized ragged-MTP SWA
# slot mapping, fixed upstream by tokenspeed #614) survived every existing gate
# for a full rebase cycle — arthur caps generations at 384 tokens and
# llama-benchy at 128, so neither reaches the ragged MTP decode shapes that
# long generations (with stop strings + concurrent 1-token health probes)
# produce. GSM8K 8-shot completions at max_gen 2048 reaches them in ~3 minutes.
#
# Points at a LIVE serve (does not manage it). PASS requires BOTH a sane
# accuracy AND a clean engine (no IMA, engine alive) — the failure mode this
# hunts is an engine kill/wedge, and the gateway /health stays green through
# it, so the engine process + serve log are checked directly.
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
LIMIT="${LONGGEN_GSM8K_LIMIT:-50}"           # ~3-4 min on the standard serve
MIN_ACC="${LONGGEN_GSM8K_MIN_ACC:-0.90}"
SERVE_LOG="${SERVE_LOG:-$HOME/tokenspeed-sm12x/serve_gb10.log}"

ima_before=$(grep -c "illegal memory access" "${SERVE_LOG}" 2>/dev/null || echo 0)

acc=$(BASE_URL="${BASE_URL}" SERVER_GUARD=0 LM_EVAL_TASKS=gsm8k LM_EVAL_LIMIT="${LIMIT}" \
  timeout 1800 bash "${SCRIPT_DIR}/run_lm_eval.sh" 2>&1 \
  | grep -oE 'exact_match_strict"?: [0-9.]+' | grep -oE '[0-9.]+$' | head -1)

ima_after=$(grep -c "illegal memory access" "${SERVE_LOG}" 2>/dev/null || echo 0)
engine_alive=$(pgrep -fc "[t]okenspeed::" || echo 0)

echo "longgen_gsm8k: acc=${acc:-none} ima_delta=$((ima_after - ima_before)) engine=${engine_alive}"

if [ "${engine_alive}" -lt 1 ]; then
  echo "FAIL longgen_gsm8k: engine dead after long-generation load"; exit 1
fi
if [ $((ima_after - ima_before)) -gt 0 ]; then
  echo "FAIL longgen_gsm8k: illegal memory access during long-generation load"; exit 1
fi
if [ -z "${acc}" ]; then
  echo "FAIL longgen_gsm8k: no accuracy produced (stalled/timed-out eval = wedge-class)"; exit 1
fi
if awk -v a="${acc}" -v m="${MIN_ACC}" 'BEGIN{exit !(a < m)}'; then
  echo "FAIL longgen_gsm8k: accuracy ${acc} < ${MIN_ACC}"; exit 1
fi
echo "PASS longgen_gsm8k: acc=${acc} limit=${LIMIT}"
