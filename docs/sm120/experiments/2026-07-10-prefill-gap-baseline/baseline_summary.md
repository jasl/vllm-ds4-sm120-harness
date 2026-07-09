# GB10 2×SM121 tokenspeed DeepSeek-V4-Flash — baseline of record (2026-07-10, final)

**The optimization benchmark for future rounds.** Supersedes the 07-09 Tier-A baseline
(`8bf20a7d`) and the interim 07-10 entry (`5472e2f`). Nodes .117/.118 (tokenspeed pair;
vLLM baseline .116/.119 untouched).

## Build / environment
| | |
|---|---|
| tokenspeed | `feat/sm12x-engine` @ **`a906988`** — upstream tip (incl #614 sanitize-SWA-slot-mapping) + our SM12x stack, with this round's perf fixes: **FI 32-head prefill tile** (orchestrator-only, `9b4c8c1`+`5472e2f`), **Triton split-K mHC prenorm** (`edc85a8`), **TRT-LLM indexer Q-prep chain** (#563 picks `5248cb8`+`1c1a9f0` + sm12x delta `a906988`: arch→(12,9), 4096-token cap + exact token-local slice routing) |
| torch / FI / NCCL | 2.11.0 · flashinfer 0.6.14 · nvidia-nccl-cu13 2.30.7 · TOKENSPEED_CUDA_ARCH=121a |
| GPUs | 2× GB10 (SM121a), TP=2, CRS804 switched RoCE |

## Serve config (pinned standard, unchanged)
2-node TP=2, MTP2, fp8 KV, prefix-cache ON, decode on BreakableCapture (piecewise
collectives), prefill graph OFF, mml 40960, chunked-prefill 40960, util 0.85,
MAXTOK=4000000, bf16 state cache, MXFP4 indexer cache. `num_device_pages=15259`
(~3.91M KV tokens).

## Gates (this exact serve life, one boot)
- **long-gen GSM8K gate (limit 50): PASS acc=0.96, 0 IMA** (`run_gb10_longgen_gsm8k_gate.sh`)
- **arthur coherence (conc 12, 900 lines): 24/24**
- engine alive, zero illegal-memory-access across the full battery

## Perf — llama-benchy STANDARD (pinned patched @b220b7c9, pp2048 tg128, C=1, runs 3, prefix-cache)
| depth | ctx_pp t/s | pp2048 t/s | tg128 t/s |
|---|---|---|---|
| 8192  | **1801.7 ± 2.9** | **1284.5 ± 3.6** | 36.3 ± 5.3 |
| 16384 | **1735.2 ± 4.6** | 1138.3 ± 52.3 | 29.3 ± 2.3 |
| 32768 | **1634.8 ± 1.5** | 996.2 ± 2.9 | 32.6 ± 4.9 |

**vs the vLLM fork (same pinned tool, same fabric): ctx_pp d8192 = 104.4% of vLLM's
1726, d32768 = 102.4% of vLLM's 1595.9 — tokenspeed cold prefill now LEADS at every
measured depth.** (Campaign start, 07-09: 74%/72%.)

Progression this campaign (ctx_pp d8192): 1282 → 1706 (32-tile + mHC prenorm) →
**1802** (+ Q-prep chain) = **+40.5% total**.

## Provenance
30.5K cold-prefill nsys decomposition (07-09) attributed the 1.44× gap to: mHC prenorm
fallback glue (fixed: Triton split-K port), FI sparse-MLA 64-pad waste (fixed: 32-head
orchestrator tile), indexer Q-prep (fixed: TRT-LLM chain, 7× at T=9473, exact sliced),
with MoE / dense-GEMM / einsum / NCCL at parity or ahead. Remaining known tails:
indexer scoring-shape forensics (our MXFP4 scorer already 4× vLLM's kernel per unit
work — the residual serve-profile delta needs per-call-shape forensics), MoE epilogue
(re-measure on RTX; GB10 is BW-bound there), #555 mixed-forward split (scheduler
rebuild), aa2b057 host-sync removal (conflicts with our wrapper rework — take via
upstream merge).

## Safety notes carried forward
- FI split-K decode kernels (num_tokens ≤ 64 dispatch) are broken at 32 padded heads —
  the guard in `_forward_deepseek_v4_prefill_chunk` must stay until fixed in FlashInfer.
- Long-gen loads are a permanent gate (the #614-class latent bug survived every
  short-gen gate for a full rebase cycle); health probes are real 1-token traffic.
