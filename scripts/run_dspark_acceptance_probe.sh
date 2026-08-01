#!/usr/bin/env bash
# DSpark draft-acceptance probe against a live serve.
#
# Why this exists: DSpark shipped for months without any gate covering draft
# quality. Two users independently reported acceptance problems on 2026-08-01
# that none of our gates could have caught -- serve comes up, output is correct,
# only the speculative throughput is destroyed. This probe makes that visible.
#
# ★ Prose only, on purpose. On counting or repeated sequences the Markov head
#   alone reaches 68-98% acceptance even when the neural draft path is fully
#   degraded, so predictable text hides exactly the failure we are looking for.
#
# Usage:
#   run_dspark_acceptance_probe.sh --serve-log PATH [--label NAME]
#                                  [--base-url URL] [--model ID]
#                                  [--max-tokens N] [--rounds N]
#
# Reads the per-position acceptance that vLLM logs as "SpecDecoding metrics"
# into the serve log; there is no HTTP endpoint for it.
set -uo pipefail

LABEL=run
BASE_URL=${BASE_URL:-http://127.0.0.1:8000}
MODEL=${MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}
SERVE_LOG=""
MAX_TOKENS=400
ROUNDS=2

while [ $# -gt 0 ]; do
  case "$1" in
    --serve-log) SERVE_LOG="$2"; shift 2 ;;
    --label)     LABEL="$2"; shift 2 ;;
    --base-url)  BASE_URL="$2"; shift 2 ;;
    --model)     MODEL="$2"; shift 2 ;;
    --max-tokens) MAX_TOKENS="$2"; shift 2 ;;
    --rounds)    ROUNDS="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$SERVE_LOG" ] || [ ! -f "$SERVE_LOG" ]; then
  echo "FAIL dspark_acceptance: --serve-log must point at the engine log (got '${SERVE_LOG:-<unset>}')" >&2
  exit 2
fi

# Callers grep this script's stdout for results. Emit the label up front so a
# caller that only looks at output can still tell the probe ran at all -- an
# earlier matrix run invoked a path that did not exist, printed nothing, and
# was scored as a pass because only the metric lines were checked.
echo "dspark_acceptance[$LABEL] starting against $SERVE_LOG"

# Only count metrics emitted from here on.
mark=$(wc -l < "$SERVE_LOG")

python3 - "$BASE_URL" "$MODEL" "$MAX_TOKENS" "$ROUNDS" <<'PY'
import concurrent.futures, json, sys, urllib.request

base, model, max_tokens, rounds = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
PROMPTS = [
    "Write four paragraphs of ordinary prose about how a small coastal town changes "
    "between the end of the tourist season and the first winter storms. Avoid lists.",
    "Explain, in flowing prose without bullet points, why reproducing a performance "
    "regression is often harder than fixing it, drawing on systems engineering examples.",
    "Describe a long walk through an unfamiliar city at dusk, in continuous narrative "
    "prose, paying attention to sound and light rather than landmarks.",
    "Discuss in essay form the tension between measurement precision and decision speed "
    "when operating a production system, without using headings or lists.",
]

def ask(prompt):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens, "temperature": 0.7, "top_p": 0.95,
        "chat_template_kwargs": {"thinking": False},
    }).encode()
    req = urllib.request.Request(
        base + "/v1/chat/completions", data=body,
        headers={"Content-Type": "application/json"})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=300))
        return len(r["choices"][0]["message"]["content"])
    except Exception as exc:
        return f"ERR {type(exc).__name__}: {exc}"

ok = 0
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    for res in pool.map(ask, PROMPTS * rounds):
        if isinstance(res, int):
            ok += 1
        else:
            print(f"  {res}", file=sys.stderr)
print(f"  completions ok: {ok}/{len(PROMPTS) * rounds}")
sys.exit(0 if ok == len(PROMPTS) * rounds else 1)
PY
gen_rc=$?

# vLLM flushes SpecDecoding metrics on its own cadence; give it a beat.
sleep 10

metrics=$(tail -n "+$mark" "$SERVE_LOG" 2>/dev/null \
  | grep -aoE "Mean acceptance length: [0-9.]+|Per-position acceptance rate:[^|]*|Avg Draft acceptance rate: [0-9.]+%")

if [ -z "$metrics" ]; then
  echo "FAIL dspark_acceptance[$LABEL]: no SpecDecoding metrics appeared in the serve log."
  echo "  Is speculative decoding actually enabled on this serve?"
  exit 1
fi
echo "=== dspark_acceptance[$LABEL] ==="
echo "$metrics" | sed 's/^/  /'

# vLLM flushes SpecDecoding metrics on its own cadence, so the window contains
# ramp-up and ramp-down fragments alongside the steady-state prose load. Taking
# the LAST line -- the first version of this script did -- reports whichever
# fragment happened to close the window, which on a real run was the worst of
# three (mean 1.39 next to a steady-state 2.08). Report the best sample: draft
# acceptance is bounded above by the drafter's real quality, so a low fragment
# means "not enough steady traffic in that slice", not "the drafter is worse".
best_mean=$(echo "$metrics" | grep -aoE "Mean acceptance length: [0-9.]+" \
  | grep -oE "[0-9.]+$" | sort -g | tail -1)
best_avg=$(echo "$metrics" | grep -aoE "Avg Draft acceptance rate: [0-9.]+%" \
  | grep -oE "[0-9.]+" | sort -g | tail -1)
samples=$(echo "$metrics" | grep -ac "Mean acceptance length")
# Trailing all-zero draft positions are structural (nst > the drafter's block
# size), so read them off the richest sample rather than the last one.
tail_zero=$(echo "$metrics" | grep -aoE "Per-position acceptance rate:[^|]*" \
  | tail -1 | grep -oE "(, )?0\.000" | wc -l | tr -d ' ')
echo "  summary: best_mean_len=${best_mean:-?} best_avg_rate=${best_avg:-?}%" \
     "samples=${samples} trailing_zero_positions=${tail_zero}"
[ "$gen_rc" = 0 ] || echo "  NOTE: some completions failed; acceptance figures may be based on fewer tokens"
echo "DSPARK_ACCEPTANCE_DONE"
