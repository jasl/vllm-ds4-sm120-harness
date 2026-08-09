# LLM gateway — smg behind Caddy

Templates for putting the 4-node GB10 deployment behind one OpenAI-compatible
endpoint. Nothing here contains a hostname or a key; `gateway.env` and
`caddy/Caddyfile` are gitignored, and the `.example` files are what you copy.

```
        internet ──▶ [ DDNS front end, terminates TLS ]
                              │
                     [ Caddy :8443 ]      ◀── authentication + path allowlist
                              │
                       [ smg :3000 ]      ◀── no host port; load balancing only
                        ╱           ╲
             replica A :8000     replica B :8000
             head + worker       head + worker
             (2-node TP=2)       (2-node TP=2)
```

## Bring-up

```bash
cp gateway.env.example gateway.env
cp caddy/Caddyfile.example caddy/Caddyfile
# fill in the two replica URLs, and one token per person:
#   openssl rand -hex 32
docker compose --env-file gateway.env up -d
./verify_gateway.sh          # every check must PASS
```

## The three decisions that are not obvious

### Caddy holds the authentication, because smg has none for inference

Checked against the binary, not the docs
(`docker run --rm lightseekorg/smg:1.9.0 --help`):

| flag | what it actually does |
|---|---|
| `--api-key` | "authorization with the **worker**" — upstream, not clients |
| `--control-plane-api-keys` | management API only, not inference |
| `--jwt-issuer` / `--jwt-jwks-uri` | full OIDC; needs an identity provider |

There is no "give each friend a key" option. **Anything that can reach smg's
port can run inference on it**, so smg publishes no host port and Caddy is the
credential boundary. The upstream vLLM replicas are unauthenticated too — they
are safe only because nothing but smg can route to them.

A consequence worth stating plainly: **`ports:` on the smg service would
bypass every access control in this design.**

### Active health checking is off, and that is what makes downtime survivable

smg's health checker has a terminal state. Its own documentation:

> `Failed` is terminal: Successful probes do not recover a `Failed` worker.

A worker reaches it after `3 × --health-failure-threshold` consecutive failures
— 9 probes at a 60 s interval, so about **9 minutes**. Taking the GPUs back for
development always exceeds that, so with the default the gateway would need a
restart after *every* development session.

`--disable-health-check` hands liveness to the circuit breaker instead, which is
traffic-driven and self-heals: 10 consecutive failures opens it, 60 s later it
half-opens, 3 successes close it. The cost is that the first request or two
after a replica returns pays a connect timeout. That is the right trade when
planned downtime is routine.

### Every timeout is sized for silent cold prefill

A cold prefill sends **nothing** on the wire until the engine yields its first
token — measured 89 s at 131K context and 214 s at 260K. Any default of 30 s or
60 s anywhere in the chain cuts a perfectly healthy request.

| layer | setting | value |
|---|---|---|
| smg | `--request-timeout-secs` | 1800 |
| smg | `--queue-timeout-secs` | 600 |
| Caddy | `read`/`write`/`response_header` | 7200s |

Caddy's are deliberately the longest: smg knows what the request is doing and
should be the component that gives up, with Caddy only as a backstop.

## Adding or removing a person

Three places, all on the gateway host:

1. `gateway.env` — `TOKEN_<NAME>=$(openssl rand -hex 32)`
2. `caddy/Caddyfile` — a line in the `map` block
3. `docker-compose.yml` — forward the variable into the caddy service

Then `docker compose --env-file gateway.env up -d`. Revoking is deleting the
three lines.

The third step is easy to forget and its failure mode is bad: Caddy's `{$VAR}`
reads the **Caddy process** environment, so a token that is not forwarded
expands to a bare `"Bearer "`. With several people that collides and Caddy
refuses to start; with one person **it starts and authenticates anyone who
sends an empty bearer token**. The compose file uses `${TOKEN_...:?}` so an
unset token fails the deploy instead, and `verify_gateway.sh` probes the empty
and missing cases directly.

## Verification

`verify_gateway.sh` prints evidence rather than verdicts, so a broken check
looks different from an absent condition. It covers:

- `/healthz`, and that management paths return 404
- **that unauthenticated requests are rejected** — no header, empty bearer,
  bare `Bearer`, wrong token, empty header
- that smg is not directly reachable (pass `SMG_DIRECT_URL`)
- a chat completion, and that SSE arrives incrementally rather than buffered
- that both replicas take traffic
- **recovery after an outage longer than 9 minutes, without restarting smg** —
  the check the liveness configuration exists for. It needs
  `REPLICA_STOP_CMD`/`REPLICA_START_CMD`; without them it SKIPs loudly rather
  than passing silently.

## Sizing, and why these numbers

From `docs/sm120/reference-configs/gb10-production-2x-tp2-smg.md`, which derives
them from measurements in
`docs/sm120/experiments/2026-08-04-production-topology-mml-sweep/`.

- **Two replicas, not one TP=4 instance** — ~66% more prefill and ~40% more
  decode at this concurrency, with 31% lower TTFT. TP=4 wins only a single
  long cold prompt with no concurrency.
- **`--max-concurrent-requests 8`** — measured saturation. At 16 the hardware
  accepts the load and makes everyone slower: aggregate decode 112.0 → 97.9
  t/s, per-request 20.2 → 11.6 t/s, TTFT 4.3 → 7.8 s.
- **`--policy cache_aware`** — the replicas share no KV. A follow-up turn that
  lands on the wrong one re-pays the cold prefill, and nothing recovers it.
