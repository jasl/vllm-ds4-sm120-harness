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
  body=$(python3 -c "
import json,sys
b={'model':sys.argv[1],'input':sys.argv[2],'max_output_tokens':int(sys.argv[3])}
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
# between 131 and 528 characters in no order at all. And temperature is 0, so
# repeating one prompt returns the identical completion -- repetition adds
# samples but no information. Hence: several DIFFERENT problems, summed.
DEPTH_PROMPTS=(
  '一个农夫要带狼、羊、白菜过河，船每次只能载一样。给出完整方案并说明为什么每一步都是必要的。'
  '有三个开关在楼下，控制楼上三盏灯。你只能上楼一次。如何确定每个开关对应哪盏灯？解释原理。'
  'A、B、C 三人中恰有一人说谎。A说"B说谎"，B说"C说谎"，C说"A和B都说谎"。谁在说谎？给出推理过程。'
)

depth_total() { # depth_total <endpoint> <effort> -> summed reasoning chars
  local ep="$1" e="$2" total=0 saved="$PROMPT"
  for p in "${DEPTH_PROMPTS[@]}"; do
    PROMPT="$p"
    if [ "$ep" = chat ]; then
      read -r rl _ _ _ <<< "$(chat "{\"reasoning_effort\":\"$e\"}")"
    else
      read -r rl _ _ _ <<< "$(resp "{\"reasoning\":{\"effort\":\"$e\"}}")"
    fi
    [ "$rl" = ERR ] && rl=0
    total=$((total + rl))
  done
  PROMPT="$saved"
  echo "$total"
}

for ep in chat resp; do
  lo=$(depth_total "$ep" low)
  hi=$(depth_total "$ep" high)
  if [ "${lo:-0}" -gt 0 ] && [ "${hi:-0}" -gt 0 ]; then
    pct=$(( (hi - lo) * 100 / lo ))
    [ "$hi" -gt $(( lo + lo / 10 )) ] \
      && check "$ep high reasons deeper than low" PASS "low=${lo}c high=${hi}c (+${pct}%) over ${#DEPTH_PROMPTS[@]} problems" \
      || check "$ep high reasons deeper than low" FAIL "low=${lo}c high=${hi}c (${pct}%) — no clear margin"
  else
    check "$ep high reasons deeper than low" FAIL "no samples low=${lo} high=${hi}"
  fi
done

# --- 5. an explicit off via chat_template_kwargs still wins ----------------
read -r rl ml leak extra <<< "$(resp '{"chat_template_kwargs":{"thinking":false}}')"
{ [ "$rl" != ERR ] && [ "${rl:-1}" = 0 ]; } \
  && check "resp chat_template_kwargs thinking=false honoured" PASS "types=${extra}" \
  || check "resp chat_template_kwargs thinking=false honoured" FAIL "reasoning=${rl} types=${extra}"

echo "---"
echo "RESULT: $pass PASS, $nonpass not-PASS"
[ "$nonpass" -eq 0 ] && echo "MATRIX ACCEPTED" || echo "MATRIX NOT ACCEPTED"
exit $((nonpass > 0))
