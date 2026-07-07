# GB10 2×SM121 tokenspeed DeepSeek-V4-Flash — deep long-context baseline (2026-07-07)

First **tokenspeed** (not vLLM) long-context baseline-of-record, and the debut of the
canonical deep-long-context suite `scripts/run_gb10_deep_long_context_standard.sh`
(recall across a depth ladder + KV-pool capacity assertion + a watchdog-armed deep
climb). Nodes **.117/.118** (the tokenspeed pair; the vLLM baseline is .116/.119).

## Build / environment
| | |
|---|---|
| tokenspeed | `feat/sm12x-engine` @ `e4dc5a9` (misa_fast `f85c8e0` + draft-pool profiler `ccd05ca` + bf16 states `e4dc5a9`) |
| torch | 2.11.0 · flashinfer 0.6.14 · nvidia-nccl-cu13 2.30.7 |
| GPUs | 2× GB10 (SM121a), TP=2, RoCE switched CRS804 (192.168.100.117/.118) |

## Serve config (this run)
2-node TP=2, **MTP2**, fp8 KV (`fp8_e4m3`), prefix-cache ON, piecewise-decode-cudagraph,
`max-model-len 40960`, `chunked-prefill 40960`, util **0.85**, `max-num-seqs 8`,
`MAXTOK=4000000`, **`TOKENSPEED_DSV4_STATE_CACHE_DTYPE=bf16`** (the F3 opt-in).

## KV-pool capacity — the F1/F3 result (the headline)
`num_device_pages=15344 × page_size 256 = ` **3.93M KV tokens** (MTP2). Progression on
the SAME config: **1.88M** (baseline) → **2.22M** (F1 draft-pool profiler) → **3.93M**
(F1 + F3 bf16 states) = **~98% of the vLLM ~4M capacity target** (was ~47%). The earlier
37K–200K pools were the `MAXTOK=200000` launch default + MTP2 overhead, not a leak.

## Recall — Tier-A (freeze-safe, the committed standard)
`long-context-coherence-gate`, sentinels at absolute lines 17 / n//2 / n-13, thinking
OFF, temp 0, concurrency 8, repeat 1.
| depth (line_count) | ~tokens | recall (all 3 needles) | coherent | status |
|---|---|---|---|---|
| 8 192 (265) | ~8 215 | 8/8 | 8/8 | **PASS** |
| 16 384 (528) | ~16 368 | 8/8 | 8/8 | **PASS** |
| 32 768 (1055) | ~32 705 | 8/8 | 8/8 | **PASS** |

Also validated earlier this session on the same serve: arthur 900-line conc8 16/16 +
1200-line (~37K) conc2 4/4; GSM8K (CoT) Natalia=72/Weng=10; 17×23=391. **bf16 states are
recall-clean** (the states are per-token windowed residual, not a compounding accumulator).

## Perf — llama-benchy STANDARD (pinned `@b220b7c9`, pp2048 tg128, C=1, runs 3, prefix-cache)
| depth | ctx_pp | pp2048 | tg128 | ctx_tg |
|---|---|---|---|---|
| 8 192 | 1278.3 ± 3.0 | 963.8 ± 4.2 | 32.7 ± 4.6 | 31.7 ± 1.2 |
| 16 384 | 1254.0 ± 0.3 | 902.9 ± 2.8 | 29.7 ± 2.4 | 37.6 ± 4.4 |
| 32 768 | 1179.0 ± 5.3 | 793.8 ± 14.9 | 35.4 ± 3.8 | 34.2 ± 4.2 |

**vLLM overlap A/B — depth 32768 (the ONLY comparable row; vLLM caps at mml 49152).**
vLLM baseline-of-record `f41d6c6919` d32768: ctx_pp **1595.9** / pp2048 **1089.1** / tg128 **37.0**.
tokenspeed / vLLM = **ctx_pp 0.74× · pp2048 0.73× · tg128 0.96×**.

⚠ **Prefill regression vs vLLM is a vLLM GAIN, not a tokenspeed loss.** tokenspeed prefill
is ~unchanged from @9b1aeb1 (ctx_pp ~1278); vLLM's new prefill optimization leapfrogged it
(d8192 pinned-tool ctx_pp 943 → 1810, ~1.9×). The 3 memory commits do **not** regress perf
(bf16 states ≈ fp32). So: **capacity gap CLOSED (98%), prefill-SPEED gap OPENED (~74%)** —
separate axes. Decode near-parity (96% @32K).

## Deferred — Tier-B (deep climb 49K→128K) + Tier-C (512K–1M capacity/TTFT)
NOT run this session (freeze safety). No proven-safe deep-prefill path on 2-node: a 75K
single-chunk prefill at util 0.88 OOM-froze both nodes; multi-chunk stalls after chunk 1.
Tier-B is wired behind `DEEP_CLIMB=1` + `scripts/gb10_mem_watchdog.sh` (abort <8 GiB
MemAvailable), climbs one rung at a time, records the ceiling reached. Prereqs before the
climb (per the design workflow): validate `--deepseek-v4-indexer-prefill-max-logits-mb 128`
(shrinks the per-chunk fp32 indexer transient — the named deep-prefill lever) + per-request
`drop_caches` + prove the watchdog aborts-not-freezes on a deliberate low-mem trip. Real
128K+ serving belongs on 4-node TP=4.

## Reproduce
```bash
# from GB10 head .117, tokenspeed serve live (bf16 states, MTP2, MAXTOK=4M):
BASE_URL=http://127.0.0.1:8000 PYTHON=~/tokenspeed-sm12x/.venv-ts/bin/python \
  SERVE_LOG=~/tokenspeed-sm12x/serve_gb10.log DEEP_CLIMB=0 \
  bash scripts/run_gb10_deep_long_context_standard.sh
# Tier-B deep climb (next session, after the watchdog is proven): DEEP_CLIMB=1
```
