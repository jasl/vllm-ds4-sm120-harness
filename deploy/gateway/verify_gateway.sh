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
  # curl's %{http_code} already prints 000 when the connection fails, so a
  # `|| echo 000` fallback would concatenate into 000000 and never compare
  # equal — the check would report FAIL on the very outcome it wants.
  c=$(curl -s -o /dev/null -w '%{http_code}' -m 8 "$SMG_DIRECT_URL/v1/models" 2>/dev/null)
  [ "${c:-000}" = 000 ] && check "smg not directly reachable" PASS "connection refused at $SMG_DIRECT_URL" \
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

# --- 4. both replicas are in rotation --------------------------------------
# Asked of smg's own /workers, which reports each worker's health and status.
#
# Two earlier versions of this check asserted the wrong thing and reported FAIL
# on a healthy deployment. The first grepped smg's log for worker URLs, which
# smg does not emit per request. The second counted vLLM's own request counter
# across a burst -- reliable numbers, but the wrong property: `cache_aware`
# routing deliberately concentrates by prefix, so one burst went 6/6 and the
# next went 8/0 on the same healthy pair. Load spread on a small burst is not
# a property this deployment has, and asserting it produces noise.
#
# What actually matters is that neither worker has silently dropped out -- a
# stuck-open circuit breaker, say. smg answers that directly.
workers_json=$(docker exec gateway-caddy wget -q -O- -T 8 http://smg:3000/workers 2>/dev/null)
if [ -z "$workers_json" ]; then
  check "both replicas in rotation" SKIP "could not reach smg /workers from the caddy container"
else
  ready=$(printf '%s' "$workers_json" | python3 -c "
import json,sys
ws = json.load(sys.stdin).get('workers', [])
ok = [w for w in ws if w.get('is_healthy') and w.get('status') == 'ready']
print(f\"{len(ok)}/{len(ws)} \" + ' '.join(f\"{w.get('url')}={w.get('status')}\" for w in ws))
" 2>/dev/null)
  n_ready=${ready%%/*}
  [ "${n_ready:-0}" -ge 2 ] && check "both replicas in rotation" PASS "$ready" \
    || check "both replicas in rotation" FAIL "$ready"
fi

# --- 4b. the context window a client actually gets --------------------------
# Probed behaviourally, not read from /v1/models: smg rewrites that payload
# into its own minimal form and drops max_model_len entirely, so reading the
# field through the gateway returns nothing even when the engine is correct.
# The same is true of any gateway that re-serialises responses.
#
# What matters to a client is the ceiling it hits, so ask for one token past it
# and read the number out of the refusal. A window that silently reverted shows
# up here as the wrong number rather than as a 400 someone reports next week.
if [ -n "${EXPECT_MAX_MODEL_LEN:-}" ]; then
  # One token past the ceiling. Written to a file: argv cannot carry ~1 MB.
  python3 -c "open('/tmp/_over.txt','w').write('x ' * $(( ${EXPECT_MAX_MODEL_LEN} + 4096 )))"
  msg=$(python3 - "$GATEWAY_URL" "$MODEL" "${API_KEY:-}" <<'PYW'
import json, sys, urllib.request, urllib.error
url, model, key = sys.argv[1], sys.argv[2], sys.argv[3]
body = json.dumps({"model": model,
                   "messages": [{"role": "user", "content": open('/tmp/_over.txt').read()}],
                   "max_tokens": 8}).encode()
h = {"Content-Type": "application/json"}
if key:
    h["Authorization"] = f"Bearer {key}"
try:
    urllib.request.urlopen(urllib.request.Request(url + "/v1/chat/completions", data=body, headers=h), timeout=300)
    print("ACCEPTED")
except urllib.error.HTTPError as e:
    print(e.read().decode()[:400].replace("\n", " "))
except Exception as e:
    print(f"{type(e).__name__}: {e}")
PYW
)
  if printf '%s' "$msg" | grep -q "$EXPECT_MAX_MODEL_LEN"; then
    check "context window is $EXPECT_MAX_MODEL_LEN" PASS "over-limit request refused naming $EXPECT_MAX_MODEL_LEN"
  else
    check "context window is $EXPECT_MAX_MODEL_LEN" FAIL "$(printf '%s' "$msg" | head -c 150)"
  fi
fi

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
