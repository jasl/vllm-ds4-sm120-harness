#!/usr/bin/env bash
# Exercise the DeepSeek-V4 thinking/effort matrix against a live serve.
#
#   BASE_URL=http://127.0.0.1:8000 MODEL=deepseek-ai/DeepSeek-V4-Flash-0731 \
#     ./reasoning_effort_matrix.sh
#
# Prints CHECK lines with evidence and tallies non-PASS as blockers. Hits the
# engine directly by default: a gateway in the path can strip request fields
# (smg drops `chat_template_kwargs`), which silently changes what is under test.
#
# What it is really asking, per endpoint:
#   * silence  -> thinking ON, reasoning separated, no `</think>` in the answer
#   * none     -> thinking OFF
#   * each tier accepted, and reasoning still separated
#   * effort actually moves reasoning depth (low < high)

set -uo pipefail

BASE_URL="${BASE_URL:?set BASE_URL, e.g. http://127.0.0.1:8000}"
MODEL="${MODEL:?set MODEL}"
API_KEY="${API_KEY:-}"
PROMPT_FILE="${PROMPT_FILE:-}"
# Must be large enough that reasoning COMPLETES and an answer follows. At 900
# every tier truncated mid-thought at the same ceiling: reasoning ~4000 chars,
# answer 0 chars. Every leak check then passed vacuously -- there was no answer
# for anything to leak into -- and low-vs-high was a comparison of two
# identical budgets.
MAXTOK="${MAXTOK:-3000}"

auth=(); [ -n "$API_KEY" ] && auth=(-H "Authorization: Bearer $API_KEY")
pass=0; nonpass=0

check() { printf 'CHECK %-52s :: %-4s :: %s\n' "$1" "$2" "$3"; [ "$2" = PASS ] && pass=$((pass+1)) || nonpass=$((nonpass+1)); }

# A prompt that actually rewards deliberation, so effort tiers separate.
if [ -n "$PROMPT_FILE" ] && [ -f "$PROMPT_FILE" ]; then
  PROMPT=$(sed '1,/^---$/d;1,/^---$/d' "$PROMPT_FILE" | head -c 1200)
  [ -z "${PROMPT// }" ] && PROMPT=$(head -c 1200 "$PROMPT_FILE")
else
  PROMPT='一个池塘里的睡莲每天数量翻倍，第30天铺满整个池塘。第几天铺满一半？请解释你的推理。'
fi

jq_get() { python3 -c "
import json,sys
try: d=json.load(sys.stdin)
except Exception as e: print('PARSE_ERROR'); sys.exit()
$1
"; }

echo "=== reasoning effort matrix  $(date -Is) ==="
echo "    base=$BASE_URL"
echo "    model=$MODEL"
echo "    prompt=${PROMPT_FILE:-builtin} (${#PROMPT} chars)"

# ---------------------------------------------------------------- chat
chat() { # chat <json-extra>  -> "<reasoning_len> <content_len> <leaked> <err>"
  local extra="$1" body
  body=$(python3 -c "
import json,sys
b={'model':sys.argv[1],'messages':[{'role':'user','content':sys.argv[2]}],
   'max_tokens':int(sys.argv[3]),'temperature':0}
b.update(json.loads(sys.argv[4]) if sys.argv[4] else {})
print(json.dumps(b))" "$MODEL" "$PROMPT" "$MAXTOK" "$extra")
  curl -s -m 600 "${auth[@]}" -H 'Content-Type: application/json' -d "$body" \
    "$BASE_URL/v1/chat/completions" | jq_get "
if 'error' in d:
    print('ERR', str(d['error'])[:70].replace(' ','_')); sys.exit()
m = d['choices'][0]['message']
r = m.get('reasoning_content') or ''
c = m.get('content') or ''
print(len(r), len(c), '</think>' in c or '<think>' in c, 'OK')
"
}

# ------------------------------------------------------------ responses
resp() { # resp <json-extra> -> "<reasoning_len> <msg_len> <leaked> <types>"
  local extra="$1" body
  # temperature MUST be set here. ResponsesRequest.temperature defaults to 1.0,
  # so without it this arm sampled while the chat arm ran greedy -- the two
  # endpoints were never compared under the same regime, and every resp result
  # was one draw from a distribution rather than a measurement.
  body=$(python3 -c "
import json,sys
b={'model':sys.argv[1],'input':sys.argv[2],'max_output_tokens':int(sys.argv[3]),
   'temperature':0}
b.update(json.loads(sys.argv[4]) if sys.argv[4] else {})
print(json.dumps(b))" "$MODEL" "$PROMPT" "$MAXTOK" "$extra")
  curl -s -m 600 "${auth[@]}" -H 'Content-Type: application/json' -d "$body" \
    "$BASE_URL/v1/responses" | jq_get "
if 'error' in d:
    print('ERR', str(d.get('error'))[:70].replace(' ','_')); sys.exit()
out = d.get('output', [])
rl = sum(len(c.get('text','')) for o in out if o.get('type')=='reasoning' for c in o.get('content',[]))
ml = sum(len(c.get('text','')) for o in out if o.get('type')=='message' for c in o.get('content',[]))
leak = any('</think>' in c.get('text','') or '<think>' in c.get('text','')
           for o in out for c in o.get('content',[]))
print(rl, ml, leak, ','.join(o.get('type','?') for o in out) or 'EMPTY')
"
}

# --- 1. the default path: no thinking hint anywhere ------------------------
# This is what a stock SDK sends, and where the leak lived.
for ep in chat resp; do
  read -r rl ml leak extra <<< "$($ep '')"
  if [ "$rl" = ERR ]; then
    check "$ep silence: no error" FAIL "$ml"
  else
    if [ "${ml:-0}" -eq 0 ]; then
      # No answer means the generation budget ran out inside the reasoning, and
      # a leak check against an empty answer proves nothing.
      check "$ep silence: no </think> in the answer" FAIL "VACUOUS — answer empty, raise MAXTOK (reasoning=${rl}c)"
    elif [ "$leak" = False ]; then
      check "$ep silence: no </think> in the answer" PASS "reasoning=${rl}c answer=${ml}c"
    else
      check "$ep silence: no </think> in the answer" FAIL "LEAKED — reasoning=${rl}c answer=${ml}c ($extra)"
    fi
    [ "${rl:-0}" -gt 0 ] \
      && check "$ep silence: reasoning separated" PASS "${rl} chars in its own field" \
      || check "$ep silence: reasoning separated" FAIL "reasoning field empty ($extra)"
  fi
done

# --- 2. thinking explicitly off -------------------------------------------
read -r rl ml leak extra <<< "$(chat '{"reasoning_effort":"none"}')"
{ [ "$rl" != ERR ] && [ "${rl:-1}" = 0 ] && [ "$leak" = False ]; } \
  && check "chat effort=none: thinking off, nothing leaked" PASS "reasoning=0 answer=${ml}c" \
  || check "chat effort=none: thinking off, nothing leaked" FAIL "reasoning=${rl} leak=${leak} ${ml}"

read -r rl ml leak extra <<< "$(resp '{"reasoning":{"effort":"none"}}')"
{ [ "$rl" != ERR ] && [ "${rl:-1}" = 0 ] && [ "$leak" = False ]; } \
  && check "resp effort=none: thinking off, nothing leaked" PASS "types=${extra} answer=${ml}c" \
  || check "resp effort=none: thinking off, nothing leaked" FAIL "reasoning=${rl} leak=${leak} types=${extra}"

# --- 3. every spelling is accepted, on both endpoints ----------------------
declare -A CHAT_R RESP_R
for e in minimal low medium high xhigh max; do
  read -r rl ml leak extra <<< "$(chat "{\"reasoning_effort\":\"$e\"}")"
  if [ "$rl" = ERR ]; then check "chat effort=$e accepted" FAIL "$ml"
  elif [ "$leak" != False ]; then check "chat effort=$e accepted" FAIL "leaked </think>"
  elif [ "${ml:-0}" -eq 0 ]; then check "chat effort=$e accepted" FAIL "VACUOUS — answer empty (reasoning=${rl}c)"
  else CHAT_R[$e]=$rl; check "chat effort=$e accepted" PASS "reasoning=${rl}c answer=${ml}c"; fi

  read -r rl ml leak extra <<< "$(resp "{\"reasoning\":{\"effort\":\"$e\"}}")"
  if [ "$rl" = ERR ]; then check "resp effort=$e accepted" FAIL "$ml"
  elif [ "$leak" != False ]; then check "resp effort=$e accepted" FAIL "leaked </think> (types=$extra)"
  elif [ "${ml:-0}" -eq 0 ]; then check "resp effort=$e accepted" FAIL "VACUOUS — answer empty (reasoning=${rl}c)"
  else RESP_R[$e]=$rl; check "resp effort=$e accepted" PASS "reasoning=${rl}c msg=${ml}c types=${extra}"; fi
done

# --- 4. effort actually changes depth --------------------------------------
# `low` injects no effort prompt at all; `high` injects the original
# checkpoint's maximum ("Absolute maximum with no shortcuts permitted"). The
# gap should be visible -- but only on work that rewards deliberation, and only
# across several problems.
#
# Two things make a naive version of this check useless. An easy prompt leaves
# nothing to deliberate about: on "when is the pond half full", tiers landed
# between 131 and 528 characters in no order at all. Hence: several DIFFERENT
# problems, summed.
#
# ★ AND THIS MEASUREMENT IS NOISY, WHICH AN EARLIER VERSION OF THIS COMMENT
# DENIED. It claimed temperature 0 makes repeats identical, so repetition adds
# no information. That is false. Measured on the base checkpoint, two identical
# greedy repeats against one serve:
#
#     chat  rep1 low=6524c  rep2 low=4540c     (-30%)
#     resp  rep1 low=6002c  rep2 low=8902c     (+48%)
#
# Prefix-cache state differs between repeats, that shifts attention numerics
# enough to flip a token, and in a long generation one flipped token changes the
# length by tens of percent. So the noise floor is roughly +/-45%, and a
# threshold below that measures the cache, not the effort tier.
#
# The tiers are also not equally spaced across checkpoints: 0731 shifted them
# down one, so `high` is 0731's top tier but NOT the base checkpoint's (`max`
# is). On 0731 the margin is +113%/+164% and clears the noise easily; on base it
# is ~+20-30% and does not. A check that FAILs there reports its own resolution,
# not a defect -- which is exactly what happened: it passed pre-merge and failed
# post-merge on runs whose serve configs also differed.
DEPTH_PROMPTS=(
  '一个农夫要带狼、羊、白菜过河，船每次只能载一样。给出完整方案并说明为什么每一步都是必要的。'
  '有三个开关在楼下，控制楼上三盏灯。你只能上楼一次。如何确定每个开关对应哪盏灯？解释原理。'
  'A、B、C 三人中恰有一人说谎。A说"B说谎"，B说"C说谎"，C说"A和B都说谎"。谁在说谎？给出推理过程。'
)

depth_total() { # depth_total <endpoint> <effort> -> "<chars> <measured> <lost>"
  local ep="$1" e="$2" total=0 n=0 bad=0 saved="$PROMPT"
  for p in "${DEPTH_PROMPTS[@]}"; do
    PROMPT="$p"
    if [ "$ep" = chat ]; then
      read -r rl _ _ _ <<< "$(chat "{\"reasoning_effort\":\"$e\"}")"
    else
      read -r rl _ _ _ <<< "$(resp "{\"reasoning\":{\"effort\":\"$e\"}}")"
    fi
    # A dropped sample must not be scored as ZERO REASONING. Scoring it 0 makes
    # the arm that lost a request look shallower, which flatters `low` and
    # inflates the ratio into a PASS -- while the evidence string still claims
    # "over 3 problems". `ERR` is jq_get's transport/HTTP sentinel and
    # `PARSE_ERROR` its JSON sentinel; both mean no measurement, not a small one.
    case "$rl" in
      ERR|PARSE_ERROR|"") bad=$((bad + 1)) ;;
      *[!0-9]*)           bad=$((bad + 1)) ;;
      *)                  total=$((total + rl)); n=$((n + 1)) ;;
    esac
  done
  PROMPT="$saved"
  # "<summed chars> <problems measured> <problems lost>" -- the caller decides
  # what an incomplete set means rather than being handed a number that hides it.
  echo "$total $n $bad"
}

# Outside the +/-45% noise floor in either direction is a real signal; inside it
# the check cannot tell, and says so. INCONCLUSIVE is reported loudly and does
# NOT block: blocking on a measurement this instrument cannot resolve is how a
# clean build got reported as a regression.
DEPTH_MARGIN_PCT="${DEPTH_MARGIN_PCT:-50}"
inconclusive=0

for ep in chat resp; do
  read -r lo lo_n lo_bad <<< "$(depth_total "$ep" low)"
  read -r hi hi_n hi_bad <<< "$(depth_total "$ep" high)"
  name="$ep high reasons deeper than low"
  if [ "${lo:-0}" -le 0 ] || [ "${hi:-0}" -le 0 ]; then
    check "$name" FAIL "no samples low=${lo} high=${hi}"
    continue
  fi
  # An unequal number of problems on the two sides is not a depth comparison at
  # all -- the smaller sum is smaller because it has fewer terms.
  if [ "${lo_bad:-0}" -ne 0 ] || [ "${hi_bad:-0}" -ne 0 ] || [ "${lo_n:-0}" -ne "${hi_n:-0}" ]; then
    check "$name" FAIL "incomparable: low measured ${lo_n}/${#DEPTH_PROMPTS[@]} (lost ${lo_bad}), high measured ${hi_n}/${#DEPTH_PROMPTS[@]} (lost ${hi_bad})"
    continue
  fi
  pct=$(( (hi - lo) * 100 / lo ))
  ev="low=${lo}c high=${hi}c (${pct}%) over ${lo_n} problems"
  if [ "$pct" -ge "$DEPTH_MARGIN_PCT" ]; then
    check "$name" PASS "$ev"
  elif [ "$pct" -le $(( -DEPTH_MARGIN_PCT )) ]; then
    check "$name" FAIL "$ev — high reliably reasons LESS than low"
  else
    printf 'CHECK %-52s :: %-4s :: %s\n' "$name" "INCO" \
      "$ev — inside the +/-${DEPTH_MARGIN_PCT}% noise floor, cannot resolve"
    inconclusive=$((inconclusive + 1))
  fi
done

# --- 5. an explicit off via chat_template_kwargs still wins ----------------
read -r rl ml leak extra <<< "$(resp '{"chat_template_kwargs":{"thinking":false}}')"
{ [ "$rl" != ERR ] && [ "${rl:-1}" = 0 ]; } \
  && check "resp chat_template_kwargs thinking=false honoured" PASS "types=${extra}" \
  || check "resp chat_template_kwargs thinking=false honoured" FAIL "reasoning=${rl} types=${extra}"

echo "---"
echo "RESULT: $pass PASS, $nonpass not-PASS, $inconclusive inconclusive"
[ "$inconclusive" -gt 0 ] && echo "    ^ $inconclusive depth check(s) NOT VERIFIED — the margin was inside the noise floor"
[ "$nonpass" -eq 0 ] && echo "MATRIX ACCEPTED" || echo "MATRIX NOT ACCEPTED"
exit $((nonpass > 0))
