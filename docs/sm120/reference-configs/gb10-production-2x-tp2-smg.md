# GB10 4-node production deployment — 2x TP=2 behind smg

Derived entirely from measurements in
[`docs/sm120/experiments/2026-08-04-production-topology-mml-sweep/`](../experiments/2026-08-04-production-topology-mml-sweep/README.md).
Every number quoted below was measured on `0f59188db1` (tag
`sm120-pr-41834-stable-preview-20260804`) on the four local GB10 nodes.

Target: a personal/shared deployment for a **small** number of concurrent users.
Redundancy is explicitly not a goal — this layout has none, and losing one replica
halves capacity rather than degrading gracefully.

## Layout

```
                         internet
                            |
                    [ TLS reverse proxy ]        <- not smg; see "Exposure"
                            |
                    [ smg  :3000 ]               <- separate machine, e.g. 10.0.0.110
                       /          \
        replica A :8000            replica B :8000
        head  10.0.0.116           head  10.0.0.117
        worker 10.0.0.119          worker 10.0.0.118
        (2-node TP=2)              (2-node TP=2)
```

**Put the gateway on a machine that is not serving.** Decode on this stack is
host-CPU-bound (a diffuse Python scheduler cost, no single graphable forward), so a
gateway competing for CPU on a head node taxes exactly the resource decode is short of.
smg is a small Rust binary; the RTX workstation at 10.0.0.110, or any spare box, is
enough.

## Why 2x TP=2 rather than one TP=4

| | 2x TP=2 | TP=4 |
|---|---|---|
| pp2048 @ total c=8 | **2838 t/s** | 1705 t/s |
| tg128 @ total c=8 | **93.3 t/s** | 63.0 t/s |
| TTFT @ total c=8 | **4.71 s** | 6.82 s |
| cold prefill, 131K, single request | 89.4 s | **74.9 s** |
| KV capacity @ mml 262144 | 605,013 /replica | **1,985,436** |

2x TP=2 wins the concurrent case by ~66% prefill / ~40% decode / -31% TTFT, stable
across two mml values and two depths. TP=4 wins exactly one thing — a **single**
long cold prompt, by 14–24% — because one request can use all four nodes while at
concurrency the 4-node all-reduce overhead dominates.

**Choose TP=4 instead if** the real workload is one person pasting very long documents
with little concurrency: it saves 15–30 s per cold long prompt and holds 3.3x the KV.

## vLLM serve — both replicas

Launched with `scripts/dgx_spark_start_mp_serve.sh`. Identical settings on both
replicas; only the host/RoCE pairs differ.

```sh
# --- replica A ---
env MODEL_ID=deepseek-ai/DeepSeek-V4-Flash-0731 \
    VLLM_ROOT=/path/to/vllm VLLM_VENV=/path/to/.venv \
    TP_SIZE=2 \
    HEAD_HOST=10.0.0.116  WORKER_HOST=10.0.0.119 \
    HEAD_ROCE_IP=192.168.100.116 WORKER_ROCE_IP=192.168.100.119 \
    ROCE_IFACE=enp1s0f0np0 NCCL_IB_HCA=rocep1s0f0 \
    HEAD_ROCE_IFACE=enp1s0f0np0 HEAD_NCCL_IB_HCA=rocep1s0f0 \
    WORKER_ROCE_IFACE=enp1s0f0np0 WORKER_NCCL_IB_HCA=rocep1s0f0 \
    MAX_MODEL_LEN=262144 \
    KV_CACHE_DTYPE=fp8 \
    GPU_MEMORY_UTILIZATION=0.85 \
    MAX_NUM_SEQS=64 \
    MAX_NUM_BATCHED_TOKENS=8192 \
    SERVE_PREFIX_CACHE_MODE=on \
    SERVE_SPECULATIVE_CONFIG='{"method":"dspark","num_speculative_tokens":5,"draft_sample_method":"probabilistic"}' \
    ALLOW_CURRENT_BOOT_NVRM_OOM=1 STARTUP_TIMEOUT=2400 \
    RUN_DIR=/var/lib/ds4/replicaA \
    bash scripts/dgx_spark_start_mp_serve.sh

# --- replica B: HEAD_HOST=10.0.0.117 WORKER_HOST=10.0.0.118
#                HEAD_ROCE_IP=192.168.100.117 WORKER_ROCE_IP=192.168.100.118
```

### The settings that are load-bearing

**`MAX_MODEL_LEN=262144`.** Counter-intuitive and measured: raising mml *increases* KV
capacity at constant memory, because mml is not a per-request reservation but a
structural parameter of the KV pool.

| mml | capacity/replica | prefill speed |
|---|---|---|
| 49,152 | 129,901 tok | 1718 t/s @ 8K |
| 262,144 | **605,013 tok** | 1855 t/s @ 8K |

5.33x the window, 4.66x the capacity, prefill unchanged (difference is inside noise).
**Do not lower mml to "save memory for concurrency" — that loses on both axes.** The cap
at 262144 is a *quality* bound, not a capacity one: DSv4-Flash degrades past ~400K
(YaRN 16x extrapolation from a 64K native window, plus `index_topk: 512` — a fixed
attention budget covering only 0.128% of a 400K context), independently observed on the
official DeepSeek API. A 400K cold prefill would also cost ~6 minutes.

**`MAX_NUM_SEQS=64`** is the value every capacity number above was measured at. The
gateway caps real concurrency at 8, so this is headroom rather than a target; lowering
it is safe but invalidates the measured capacity figures.

**`ALLOW_CURRENT_BOOT_NVRM_OOM=1`** — an NVRM `NV_ERR_NO_MEMORY` during model load or
NCCL init on GB10 unified memory is a benign JIT spike, not a real OOM.

## smg gateway

Verified against the smg CLI reference; defaults quoted are smg's own.

```sh
smg launch \
  --worker-urls http://10.0.0.116:8000 http://10.0.0.117:8000 \
  --policy cache_aware \
  --max-concurrent-requests 8 \
  --queue-size 32 \
  --queue-timeout-secs 600 \
  --request-timeout-secs 1800 \
  --retry-max-retries 2 \
  --max-idle-secs 14400 \
  --api-key "$VLLM_UPSTREAM_KEY" \
  --control-plane-api-keys "u1:jasl:admin:$ADMIN_KEY"
```

### `--policy cache_aware` is a correctness-of-experience requirement, not tuning

A cold 131K prefill costs **89 seconds**; the same context on a warm cache costs ~2
seconds. Agentic and chat workloads reuse their prefix at 95–98%. If a follow-up turn
lands on the *other* replica, that 89 seconds is paid again — and unlike a single TP=4
pool, **the two replicas share no KV**, so nothing recovers it. Session affinity is what
makes long context usable here.

`cache_aware` is smg's default policy; it is named explicitly because losing it silently
would be expensive and hard to diagnose.

**A default that happens to work in our favour:** smg overrides cache affinity for load
balance only when the worker load gap exceeds `--balance-abs-threshold` (64) *and*
`--balance-rel-threshold` (1.5). With `--max-concurrent-requests 8`, the gap can never
exceed 8, so balancing never preempts cache locality. That is the behaviour we want and
it needs no flag — but it also means **raising `--max-concurrent-requests` above ~64
would silently start trading cache hits for balance.**

### `--max-concurrent-requests` — CORRECTED 2026-08-10: use `-1`

**The value below is wrong and the flag was misread.** It is not a concurrency
cap. smg's own help: *"Maximum number of concurrent requests allowed (for rate
limiting). Set to -1 to disable rate limiting"*, and
`--rate-limit-tokens-per-second` defaults to it. It is a token bucket, and above
the limit it **rejects** rather than queues.

Measured on the deployed gateway: 16 concurrent requests at `8` returned **9
completions and 7 x HTTP 408, all within 2 seconds** — so not queue timeouts
either, despite `--queue-size 32` and `--queue-timeout-secs 600`. At `-1` the
same burst is **16/16 in 2 s**.

The throughput measurement below stands; the conclusion drawn from it does not.
Peak throughput near concurrency 8 is a reason to let requests **wait**, which
vLLM's scheduler already does, not a reason to turn them away at the gateway.

The `--balance-abs-threshold` note below also assumed a cap that does not exist,
so it does not apply.

### The original text, kept for the record

### `--max-concurrent-requests 8`

Measured saturation, not a guess. Both topologies peak at total concurrency ~8; going to
16 makes every metric worse:

| total conc | decode t/s (2x TP=2) | per-request | TTFT |
|---|---|---|---|
| 8 | **112.0** | **20.2 t/s** | **4.3 s** |
| 16 | 97.9 | 11.6 t/s | 7.8 s |

The hardware accepts 16 and simply makes everyone slower. Note this ceiling is **not** a
KV limit — zero preemptions were observed at any point — so adding KV will not raise it.

### Timeouts and retries, adjusted for long context

- `--queue-timeout-secs 600` — the default 60 s is shorter than a single cold 131K
  prefill (89 s), so queued requests would be dropped while the system is working
  normally.
- `--retry-max-retries 2`, down from 5 — a retried long request costs another 89–214 s
  *and* may land on the other replica, losing its cache. Retries are much more expensive
  here than in a typical stateless service.
- `--request-timeout-secs 1800` (default) comfortably covers a 260K cold prefill
  (214 s) plus generation.

### Optional cache tuning — measure before changing

`--cache-threshold` (0.3), `--eviction-interval` (120 s), `--max-tree-size` (64 MiB) and
the router's `--block-size` (16) are left at defaults. The router's `--block-size` is its
radix-tree granularity; aligning it with the engine's KV block size would plausibly
sharpen hit estimation, but that is reasoning, not a measurement — **verify against
observed hit rate before changing it.** Watch the cold-prefill rate in practice: if
follow-up turns are missing cache, that is the knob group to investigate.

## Exposure

vLLM should not face the internet directly.

- **Bind vLLM to the internal network only.** The serve script listens on `:8000`;
  ensure that is not routable from outside. smg is the only process that talks to it,
  authenticated with `--api-key`.
- **smg does not terminate TLS** in the configuration above. Front it with a reverse
  proxy (Caddy, nginx) holding the certificate, or an equivalent tunnel.
- **Client auth** via `--control-plane-api-keys` (`id:name:role:key`). JWT is also
  supported (`--jwt-issuer`, `--jwt-audience`, `--jwt-jwks-uri`).
- Sharing with others means untrusted prompt content. That is a normal LLM risk rather
  than an infrastructure one, but note a single 256K request can occupy ~42% of one
  replica's KV pool and ~3.6 minutes of prefill — `--max-concurrent-requests` is the
  only thing bounding that, so keep it set.

## Expected behaviour

At the recommended settings, with 8 concurrent users at ~16K context:

| | |
|---|---|
| aggregate prefill | ~2840 t/s |
| aggregate decode | ~93 t/s |
| per-user decode | ~19.5 t/s |
| TTFT, warm cache | ~4.7 s |
| TTFT, cold 131K prompt | ~89 s |
| max context/request | 262,144 tok |
| concurrent full 256K windows | 2.3 per replica (4.6 total) |

## Operational notes

- After **any** GB10 rebuild, re-pin `nvidia-nccl-cu13==2.30.7` on both nodes of both
  replicas, and clear stale processes on port 29519.
- GB10 can hard-freeze after an OOM or wedge; never `reboot -f`. A wedged node needs a
  physical power-cycle.
- Single-instance protection for any batch job touching these nodes should use `flock`,
  never `pgrep -f` — the latter matches its own ssh cmdline.
