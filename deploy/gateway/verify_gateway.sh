#!/usr/bin/env bash
# Verify a deployed gateway actually behaves the way the configuration claims.
#
# Every check prints its EVIDENCE, not a verdict, so a check that is itself
# broken looks different from a condition that is absent. Anything that is not
# PASS is a blocker.
#
#   GATEWAY_URL=http://127.0.0.1:8443 \
#   MODEL=deepseek-ai/DeepSeek-V4-Flash-0731 \
#   API_KEY=sk-... \
#   ./verify_gateway.sh
#
# The recovery check needs to take a replica down and bring it back, which this
# script cannot do on its own. Give it REPLICA_STOP_CMD/REPLICA_START_CMD to
# run that phase, or omit them and it will SKIP it loudly rather than silently
# passing.

set -uo pipefail

GATEWAY_URL="${GATEWAY_URL:-http://127.0.0.1:8443}"
MODEL="${MODEL:?set MODEL to the served model id}"
API_KEY="${API_KEY:-}"
REPLICA_STOP_CMD="${REPLICA_STOP_CMD:-}"
REPLICA_START_CMD="${REPLICA_START_CMD:-}"
RECOVERY_WAIT_SECS="${RECOVERY_WAIT_SECS:-660}" # > 9 min, past the terminal-Failed window

pass=0
nonpass=0
auth=(); [ -n "$API_KEY" ] && auth=(-H "Authorization: Bearer $API_KEY")

check() { # check <name> <PASS|FAIL|SKIP> <evidence>
  printf 'CHECK %-48s :: %-4s :: %s\n' "$1" "$2" "$3"
  [ "$2" = PASS ] && pass=$((pass + 1)) || nonpass=$((nonpass + 1))
}

echo "=== gateway verification $(date -Is) ==="
echo "    gateway=$GATEWAY_URL model=$MODEL auth=$([ -n "$API_KEY" ] && echo yes || echo no)"

# --- 1. the allowlist actually blocks -------------------------------------
code=$(curl -s -o /dev/null -w '%{http_code}' -m 10 "$GATEWAY_URL/healthz")
[ "$code" = 200 ] && check "healthz responds" PASS "HTTP $code" \
  || check "healthz responds" FAIL "HTTP $code (expected 200)"

# Management surfaces must not be reachable. A 404 means Caddy swallowed it;
# anything else means the allowlist has a hole.
holes=""
for p in /workers /workers/list /v1/../workers /metrics /admin; do
  c=$(curl -s -o /dev/null -w '%{http_code}' -m 10 "$GATEWAY_URL$p")
  [ "$c" = 404 ] || holes="$holes $p=$c"
done
[ -z "$holes" ] && check "management paths blocked" PASS "all 404" \
  || check "management paths blocked" FAIL "reachable:$holes"

# --- 1b. authentication actually rejects -----------------------------------
# A gateway that answers without a credential is the failure this whole
# arrangement exists to prevent, and it is invisible from a successful request:
# every check below would pass just as well on a wide-open gateway. So probe
# the negative cases explicitly.
#
# The empty-bearer case is not hypothetical. Caddy's {$VAR} reads the Caddy
# process environment; if a token is not forwarded into the container it
# expands to a bare "Bearer ", and a single-user config would come up
# authenticating anyone who sends exactly that.
authfail=""
probe() { # probe <label> <curl-args...>
  local label="$1"; shift
  local c
  c=$(curl -s -o /dev/null -w '%{http_code}' -m 20 -X POST \
    -H 'Content-Type: application/json' -d "$body_probe" "$@" \
    "$GATEWAY_URL/v1/chat/completions")
  # 404 is what the Caddyfile returns for unauthenticated callers.
  [ "$c" = 404 ] || authfail="$authfail $label=$c"
}
body_probe=$(printf '{"model":"%s","messages":[{"role":"user","content":"hi"}],"max_tokens":1}' "$MODEL")
probe "no-header"
probe "empty-bearer" -H "Authorization: Bearer "
probe "bearer-only" -H "Authorization: Bearer"
# Not a credential: a deliberately invalid literal, here to prove a wrong token
# is refused. A secret scanner will flag the shape; this is what it is.
probe "wrong-token" -H "Authorization: Bearer deadbeefdeadbeefdeadbeefdeadbeef"
probe "empty-header" -H "Authorization: "
[ -z "$authfail" ] && check "unauthenticated requests rejected" PASS "all 5 probes got 404" \
  || check "unauthenticated requests rejected" FAIL "GOT THROUGH:$authfail"

# smg itself must not be reachable directly — it has no client auth at all, so
# an exposed port would bypass every check above.
if [ -n "${SMG_DIRECT_URL:-}" ]; then
  c=$(curl -s -o /dev/null -w '%{http_code}' -m 8 "$SMG_DIRECT_URL/v1/models" 2>/dev/null || echo 000)
  [ "$c" = 000 ] && check "smg not directly reachable" PASS "connection refused at $SMG_DIRECT_URL" \
    || check "smg not directly reachable" FAIL "HTTP $c — smg is exposed and has NO client auth"
fi

# --- 2. inference works ----------------------------------------------------
body=$(printf '{"model":"%s","messages":[{"role":"user","content":"Reply with exactly: OK"}],"max_tokens":10,"temperature":0}' "$MODEL")
resp=$(curl -s -m 300 "${auth[@]}" -H 'Content-Type: application/json' \
  -d "$body" "$GATEWAY_URL/v1/chat/completions" 2>&1)
if echo "$resp" | grep -q '"choices"'; then
  check "chat completion" PASS "$(echo "$resp" | head -c 90 | tr -d '\n')"
else
  check "chat completion" FAIL "$(echo "$resp" | head -c 160 | tr -d '\n')"
fi

# --- 3. streaming arrives incrementally, not as one lump -------------------
# A buffering proxy still produces correct output, so correctness alone does
# not prove streaming works. Timing the first chunk against the last is what
# distinguishes them.
sbody=$(printf '{"model":"%s","messages":[{"role":"user","content":"Count from 1 to 20, one number per line."}],"max_tokens":120,"temperature":0,"stream":true}' "$MODEL")
tmp=$(mktemp)
curl -s -N -m 300 "${auth[@]}" -H 'Content-Type: application/json' \
  -d "$sbody" "$GATEWAY_URL/v1/chat/completions" 2>/dev/null \
  | while IFS= read -r line; do printf '%s %s\n' "$(date +%s.%N)" "$line"; done > "$tmp"
chunks=$(grep -c '^[0-9.]* data: ' "$tmp" 2>/dev/null || echo 0)
if [ "$chunks" -ge 3 ]; then
  first=$(grep -m1 '^[0-9.]* data: ' "$tmp" | cut -d' ' -f1)
  last=$(grep '^[0-9.]* data: ' "$tmp" | tail -1 | cut -d' ' -f1)
  spread=$(awk -v a="$first" -v b="$last" 'BEGIN{printf "%.2f", b-a}')
  # If every chunk lands in the same instant, something buffered the whole
  # response and released it at once.
  ok=$(awk -v s="$spread" 'BEGIN{print (s>0.05)?"yes":"no"}')
  [ "$ok" = yes ] && check "SSE streams incrementally" PASS "$chunks chunks over ${spread}s" \
    || check "SSE streams incrementally" FAIL "$chunks chunks all within ${spread}s — buffered"
else
  check "SSE streams incrementally" FAIL "only $chunks data chunks"
fi
rm -f "$tmp"

# --- 4. both replicas are actually in rotation -----------------------------
# Distinct conversation prefixes so cache_aware spreads them; then read smg's
# own log for which worker served what.
for i in 1 2 3 4 5 6; do
  curl -s -o /dev/null -m 120 "${auth[@]}" -H 'Content-Type: application/json' \
    -d "$(printf '{"model":"%s","messages":[{"role":"user","content":"Unique probe %d — reply OK"}],"max_tokens":5,"temperature":0}' "$MODEL" "$i")" \
    "$GATEWAY_URL/v1/chat/completions" &
done
wait
seen=$(docker logs smg --since 3m 2>&1 | grep -oE 'http://[0-9a-zA-Z_.-]+:[0-9]+' | sort -u | wc -l | tr -d ' ')
[ "${seen:-0}" -ge 2 ] && check "both replicas in rotation" PASS "$seen distinct workers in smg log" \
  || check "both replicas in rotation" FAIL "only ${seen:-0} distinct worker(s) seen"

# --- 5. THE ONE THAT MATTERS: recovery after a long outage -----------------
# smg's active health checker has a terminal Failed state reached after
# 3 x --health-failure-threshold consecutive failures. With --disable-health-check
# the circuit breaker owns liveness instead, and it self-heals. This check is
# what proves that is true HERE, rather than merely documented.
if [ -z "$REPLICA_STOP_CMD" ] || [ -z "$REPLICA_START_CMD" ]; then
  check "recovery after >9min outage" SKIP "set REPLICA_STOP_CMD and REPLICA_START_CMD to run this"
  echo "    ^ NOT VERIFIED. This is the check the whole liveness configuration exists for."
else
  echo "    stopping replica B ..."
  eval "$REPLICA_STOP_CMD" >/dev/null 2>&1
  sleep 5
  # Serve while one replica is down: must still answer, via the survivor.
  d=$(curl -s -m 300 "${auth[@]}" -H 'Content-Type: application/json' -d "$body" \
    "$GATEWAY_URL/v1/chat/completions" 2>&1)
  echo "$d" | grep -q '"choices"' \
    && check "serves with one replica down" PASS "answered from the survivor" \
    || check "serves with one replica down" FAIL "$(echo "$d" | head -c 140 | tr -d '\n')"

  echo "    waiting ${RECOVERY_WAIT_SECS}s (past the ~9 min terminal-Failed window) ..."
  sleep "$RECOVERY_WAIT_SECS"
  echo "    restarting replica B ..."
  eval "$REPLICA_START_CMD" >/dev/null 2>&1

  # Give it time to load, then drive traffic: the circuit breaker is
  # traffic-driven, so it needs requests to notice recovery.
  sleep 120
  for i in $(seq 1 12); do
    curl -s -o /dev/null -m 120 "${auth[@]}" -H 'Content-Type: application/json' \
      -d "$(printf '{"model":"%s","messages":[{"role":"user","content":"recovery probe %d"}],"max_tokens":5,"temperature":0}' "$MODEL" "$i")" \
      "$GATEWAY_URL/v1/chat/completions"
    sleep 10
  done
  back=$(docker logs smg --since 4m 2>&1 | grep -oE 'http://[0-9a-zA-Z_.-]+:[0-9]+' | sort -u | wc -l | tr -d ' ')
  [ "${back:-0}" -ge 2 ] \
    && check "replica returns WITHOUT restarting smg" PASS "$back workers serving again" \
    || check "replica returns WITHOUT restarting smg" FAIL "still ${back:-0} worker(s) — it did NOT self-heal"
fi

echo "---"
echo "RESULT: $pass PASS, $nonpass not-PASS"
[ "$nonpass" -eq 0 ] && echo "GATEWAY ACCEPTED" || echo "GATEWAY NOT ACCEPTED: $nonpass non-PASS check(s)"
exit $((nonpass > 0))
