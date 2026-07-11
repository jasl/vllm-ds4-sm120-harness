# GB10 2×SM121 tokenspeed DSv4-Flash — torch-2.13 baseline of record + sm12x-stable cut (2026-07-11)

**Supersedes the 07-10 baseline (`39d09d3`).** This head is the first cut of the
`sm12x-stable` / `sm12x-preview` channels (dev = `feat/sm12x-engine`). Nodes .117/.118.

## Build / environment
| | |
|---|---|
| tokenspeed | `sm12x-stable` = `sm12x-preview` = **`e97fa2b`** (= 07-10 `39d09d3` stack + `3cc3517` monolithic-decode opt-in + `a1ecfc7` plan gate + `bb2f17a`/`8e70f2f` multichunk fixes + `e97fa2b` grammar piecewise fix) |
| torch | **2.13.0+cu130** (upgraded from 2.11.0 this round) |
| NCCL | **nvidia-nccl-cu13==2.30.4 — MANDATORY PIN.** 2-D interaction matrix via `run_gb10_nccl_graph_replay_gate.sh`: 2.30.7 wedges under torch 2.11 AND (presumed) 2.13; **2.29.7 (torch 2.13's own pin) passes under 2.11 but WEDGES under 2.13's capture path**; 2.30.4 passes 5000 max-rate replays under both. Root cause: NCCL proxy-progress-thread death on host-staged RoCE (upstream issue draft ready). |
| triton | tokenspeed-triton **3.8.10.post20260709** (#636, validated pre-merge) + stock triton 3.7.1 (torch dep; runtime kernels) |
| FlashInfer | 0.6.14 (re-JITs cleanly under torch 2.13) |
| GPUs | 2× GB10 (SM121a), TP=2, CRS804 switched RoCE |

## Serve config (pinned standard, unchanged from 07-10)
2-node TP=2, MTP2, fp8 KV, prefix-cache ON, piecewise decode (BreakableCapture),
mml 40960, util 0.85, MAXTOK=4000000, bf16 state cache, MXFP4 indexer cache.
Tool-calling workloads additionally need `--grammar-backend xgrammar`
(default `none` → json_schema requests 500).

## Gates (this stack, one deploy)
- long-gen GSM8K (limit 50): **PASS 0.96, 0 IMA**
- arthur coherence (conc 12, 900 lines): **24/24**
- 30-wave bursty gate (C=1/2/4, drain gaps): **ALL SURVIVED, 0 failed requests**
- NCCL graph-replay gate (native libs): **PASS** (5000 max-rate replays)
- **toolcall-15 (en × non-thinking/think-high/think-max): 45/45 requests engine-clean —
  0 HTTP errors, 0×500** (vs vLLM upstream's known MTP+tool_choice intermittent-500 bug);
  content score 94% (85/90 pts; 3 misses are temp-1.0 judge variance, not engine faults).
  Required the `e97fa2b` grammar fix: xgrammar + piecewise capture previously died at
  first capture (`cudaErrorStreamCaptureUnjoined`, side-stream fork spanning segments).

## Perf — llama-benchy STANDARD (pinned patched @b220b7c9, pp2048 tg128, C=1, runs 3, prefix-cache)
| depth | ctx_pp t/s | pp2048 t/s | tg128 t/s |
|---|---|---|---|
| 8192  | **1833.3 ± 1.4** | 1314.1 ± 1.6 | **38.7 ± 3.0** |
| 16384 | **1813.1 ± 3.9** | 1240.8 ± 15.8 | **37.3 ± 3.8** |
| 32768 | **1750.3 ± 4.8** | 1079.5 ± 2.3 | **34.0 ± 3.7** |

vs 07-10 torch-2.11 baseline: ctx_pp +0.5/+1.2/**+4.0%** (new highs at every depth),
pp2048 +0.4/+3.5/+5.5%, **tg128 +18.6/+4.1/+13.7% — the torch-2.13 host-side gain
lands squarely on our host-bound piecewise decode**. vs vLLM fork (43.1/36.6/37.0):
decode gap narrows from 76–81% to **90–102%** (d16384 ahead).

## Decode ceiling (settled this round)
Monolithic in-graph decode (opt-in `TOKENSPEED_DECODE_MONOLITHIC=1`, requires
NCCL≤2.30.4) measures **equal** to piecewise at every depth: the overlap scheduler
already hides the eager-break host tax; both modes sit on the serial per-layer
small-allreduce NIC RTT (~93/step, host-staged RoCE) — the same wall vLLM sits on.
Future levers: fused/fewer ARs, small-msg NCCL tuning, GPUDirect RDMA (dmabuf).

## KV capacity
| config | KV pool |
|---|---|
| mml 40960, util 0.85, MAXTOK=4M | ~3.91M tok (15,259 pages) — unchanged from 07-10 |
| mml 131072, util 0.85, MAXTOK=4M | **1.90M tok (7,414 pages)** — same-config vs brianmiller's vLLM `d71b9aaa9e` 1.52M = **+25%** (larger mml shrinks the pool via mml-scaled state/workspace reservations; the 3.91M row above is the small-mml ceiling) |

## Community scenarios (07-10 runs, tokenspeed `a906988`/`39d09d3`-era heads, recorded here for the reply package)
- **Scenario B (brianmiller, 2-node 121K-class)**: cold prefill 116,726 tok in 90.6 s =
  **1288 t/s** (his vLLM `d71b9aaa9e`: ~96 s ≈ 1260); short-ctx decode C=1/2/4 =
  33.9/46.9/58.1 t/s (81–84% of his 41.6/55.8/70.7 — pre-torch-2.13 numbers); 121K
  cached decode 26.1 t/s. Multichunk-prefill admission fixes (`8e70f2f`+`bb2f17a`)
  landed en route (49K/88K/117K ladders green, 0 refusals).
- **Scenario W (wingcomm, first 4-node TP=4 serve, .116–.119)**: 234K cold prefill
  @ **1103 t/s**; 629K cold @ **525 t/s**; 0 IMA, 0 refusals, no wedge.
