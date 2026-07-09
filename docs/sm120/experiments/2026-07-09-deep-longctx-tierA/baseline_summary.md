# GB10 2×SM121 tokenspeed DeepSeek-V4-Flash — deep long-context Tier-A baseline (2026-07-09)

**Baseline of record** for the rebased head (upstream `febee1cc` + our 32-commit SM12x
stack + the #594 sentinel fix + the BreakableCapture decode unification). Supersedes the
2026-07-07 deep-longctx baseline for comparisons. Nodes **.117/.118** (tokenspeed pair;
the vLLM baseline is .116/.119 — never touched by this suite).

## Build / environment
| | |
|---|---|
| tokenspeed | `feat/sm12x-engine` @ `8bf20a7d` (rebase onto upstream `febee1cc`, #594 fix `9e5cd28`, decode-on-BreakableCapture `fe74329`, prefill comm-cut capability `42c88d7` **disabled**, #584 pick) |
| torch | 2.11.0 · flashinfer 0.6.14 · nvidia-nccl-cu13 2.30.7 (re-pinned post-rebuild) · smg post20260708 |
| GPUs | 2× GB10 (SM121a), TP=2, RoCE switched CRS804 (192.168.100.117/.118) |

## Serve config (pinned standard)
2-node TP=2, **MTP2**, fp8 KV (`fp8_e4m3`), prefix-cache ON, piecewise-decode-cudagraph
(now on the shared `BreakableCapture` machinery), **prefill graph OFF** (measured −4~5%
pp2048 on GB10 — see `2026-07-09` prefill-graph A/B below), `max-model-len 40960`,
`chunked-prefill 40960`, util **0.85**, `MAXTOK=4000000`,
`TOKENSPEED_DSV4_STATE_CACHE_DTYPE=bf16`.

## KV-pool capacity
`num_device_pages=14899 × 256 =` **3.81M KV tokens** (MTP2, this serve instance;
14899–15364 across boots ≈ 3.81–3.93M, ~96–98% of the vLLM ~4M target).

## Perf — llama-benchy STANDARD (pinned patched `@b220b7c9`, pp2048 tg128, C=1, runs 3, prefix-cache)
| depth | ctx_pp t/s | pp2048 t/s | tg128 t/s | ctx_tg t/s |
|---|---|---|---|---|
| 8192  | 1282.4 ± 2.2 | 966.5 ± 1.2 | 33.9 ± 0.5 | 35.8 ± 1.2 |
| 16384 | 1248.6 ± 6.4 | 905.3 ± 0.8 | 29.0 ± 2.0 | 34.6 ± 4.3 |
| 32768 | 1144.9 ± 36.0 | 790.3 ± 16.7 | 35.7 ± 2.2 | 33.9 ± 1.3 |

- **Zero regression vs pre-rebase** (1277/964/32.6 @d8192) → the rebase + #594 fix +
  BreakableCapture unification are perf-clean.
- **d32768 is measurable for the first time** (the old util-0.78/37K-pool config
  watchdog-aborted at this depth; the F1+F3 pool unblocked it).
- **vLLM overlap point (d32768, same pinned tool, vLLM baseline `f41d6c6919`)**:
  vLLM 1595.9 / 1089.1 / 37.0 → tokenspeed at **0.72× / 0.73× / 0.97×**. Only this row
  (and d8192/16384) is an A/B; vLLM caps at mml 49152 — everything deeper is
  tokenspeed-only territory.

## Recall — Tier-A ladder (freeze-safe, the committed standard)
`long-context-coherence-gate`, sentinels at absolute lines 17 / n//2 / n−13 (early
needle sinks with depth — the SM12x indexer distant-context failure mode), thinking OFF,
temp 0, **concurrency 4, repeat 2** (8 requests per rung).
| line_count | ~prompt tokens | recall (all 3 needles) | status |
|---|---|---|---|
| 265  | ~8.2K  | 8/8 | PASS |
| 528  | ~16.4K | 8/8 | PASS |
| 1055 | ~32.7K | 8/8 | PASS |

Additionally on this head: arthur 900-line conc8 **16/16 ×2** + conc1 2/2 (the #594-fix
validation runs), GSM8K CoT spot-checks correct.

## Operational lessons folded into the suite this round
- **Idle-settle heartbeat** (runner + `gb10_mem_watchdog.sh`): a healthy Tier-A gate
  transiently dips to ~4–6G right after a batch of long prefills and recovers within
  ~60s (caching-allocator retention, NOT a leak). Single-sample kill policies false-abort;
  the watchdog now requires two consecutive low samples ≥60s apart (immediate kill only
  below 3G panic floor).
- Prefill-graph verdict (separate experiment, same day): mechanically enabled on 2-node
  by the collective-cut capture mode (first working prefill CUDA graph on this fabric)
  but **−4~5% pp2048** end-to-end — GB10 prefill is compute-bound; bucket padding
  (pp2048 workloads arrive as **2303-token extends**: 2048 + 256-block cache remainder)
  plus per-break handoff copies outweigh launch savings. Capability kept, default OFF.

## Reproduce
```bash
# on node .117, harness checkout ~/tmp/ds4-sm120-harness, pinned serve running or not:
bash scripts/run_gb10_deep_long_context_standard.sh          # Tier-A
DEEP_CLIMB=1 bash scripts/run_gb10_deep_long_context_standard.sh  # + Tier-B (watchdog-armed research climb)
```
Raw artifacts: `artifacts/gb10_arthur_long_context_coherence/tierA_lc{265,528,1055}/` +
the benchy table above (`~/tmp/ts_lb_rebased_034836.out` on .117).
