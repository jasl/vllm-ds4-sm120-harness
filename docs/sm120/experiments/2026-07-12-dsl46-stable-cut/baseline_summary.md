# GB10 2×SM121 tokenspeed DSv4-Flash — baseline of record (2026-07-12): rebased base + CuTeDSL 4.6.0

**Supersedes the 07-11 torch-2.13 cut.** Channel promotion target: `sm12x-stable` = `sm12x-preview` = **`732769b`**.

## Build / environment
| | |
|---|---|
| tokenspeed | `732769b` = 52-commit SM12x stack rebased onto upstream `4ebfc41` (#447 KV unified block pool, #544 spec-decode refactor, #636 triton 3.8.10) + CuTeDSL 4.6.0 squash (#640) + NCCL-pin enforcement fixes |
| torch / NCCL | 2.13.0+cu130 · **nvidia-nccl-cu13==2.30.4 (mandatory — see pin saga below)** |
| CuTeDSL | **4.6.0** (nvidia-cutlass-dsl + libs; #640 pre-merge squash) |
| triton | tokenspeed-triton 3.8.10.post20260709 + stock 3.7.1 |
| FlashInfer | 0.6.14 |
| GPUs | 2× GB10 (SM121a), TP=2, CRS804 switched RoCE |

## NCCL pin enforcement (the 07-12 trap, 3 layers deep)
Editable installs of tokenspeed-kernel silently re-resolve torch's `==2.29.7`/`==2.28.9`
NCCL — both wedge graph-replayed collectives (2.28.9 at ~7k replays: presented as
late-wave client timeouts with a healthy-looking engine). A cuda.txt pin is
ResolutionImpossible against torch's pin; a setup.py post-step is dead code on the
editable path. **Working guard: NCCL-PREFLIGHT in every node serve script — refuses
boot unless both nodes report 2.30.4.** Operational rule: re-run
`pip install --no-deps nvidia-nccl-cu13==2.30.4` after ANY kernel editable install.

## Gates (one serve life, this stack)
- GSM8K longgen (limit 50): **PASS 0.96, 0 IMA**
- arthur coherence (conc 12, 900 lines): **24/24**
- 30-wave bursty gate: **ALL SURVIVED, 0 failed requests**
- xgrammar + piecewise capture: 0 StreamCaptureUnjoined
- toolcall-15 (en × 3 thinking modes): **45/45 engine-clean, 96% content (86/90)** — best to date

## Perf — llama-benchy STANDARD (pinned @b220b7c9, C=1, runs 3, prefix-cache)
| depth | ctx_pp t/s | pp2048 t/s | tg128 t/s |
|---|---|---|---|
| 8192  | **1833.9 ± 3.0** | 1314.8 ± 6.7 | 33.4 ± 6.6 |
| 16384 | **1818.4 ± 9.5** | 1231.6 ± 10.3 | 34.5 ± 4.4 |
| 32768 | **1757.9 ± 6.6** | 1087.7 ± 2.3 | 29.5 ± 8.3 |

ctx_pp: new highs at every depth (d16384/d32768 records).

## vs vLLM fork `5e43b2cfa7` (07-11 refresh, same fabric/tool)
| metric | d8192 | d16384 | d32768 |
|---|---|---|---|
| ctx_pp | **104.4%** | **102.5%** | **103.4%** |
| pp2048 | 94.5% | 93.2% | 90.6% |
| tg128 (mean) | ~80% | ~87% | ~80% |

Verdict vs the try-it bar: prefill LEADS, pp2048 close, **decode not yet at parity**
(tg128 swings ±6-8 across serve lives; vLLM's 07-11 merge lifted their means to
41.9/39.6/37.1). Open decode levers: FI CUTLASS MXFP4 MoE (vLLM #48303 wiring study,
now with CuTeDSL 4.6 IKET profiler), MTP acceptance under benchy-class content
(our greedy-essay accept is 2.85; vLLM's #48304-era draft-rope fixes lifted their
peaks to 48.3).

## Single-stream reference (greedy, 2048-tok essay, completions)
42.4 t/s @ accept_len 2.85–2.90 (best recorded; #544 refactor improved acceptance).
