# GB10 2×SM121 tokenspeed DeepSeek-V4-Flash — baseline of record (2026-07-10)

**Supersedes the 2026-07-09 deep-longctx Tier-A baseline** (`8bf20a7d`). Nodes .117/.118
(tokenspeed pair; vLLM baseline .116/.119 untouched).

## Build / environment
| | |
|---|---|
| tokenspeed | `feat/sm12x-engine` @ `5472e2f` — rebased onto upstream tip (incl **#614** sanitize-SWA-slot-mapping, which also fixed the latent MTP long-gen IMA), + noncoop persistent_topk `adc4d3d`, + **prefill-gap fixes**: FI 32-head prefill tile (orchestrator-only, `9b4c8c1`/`5472e2f`) and Triton split-K mHC prenorm (`edc85a8`) |
| torch / FI / NCCL | 2.11.0 · flashinfer 0.6.14 · nvidia-nccl-cu13 2.30.7 |
| GPUs | 2× GB10 (SM121a), TP=2, CRS804 switched RoCE |

## Serve config (pinned standard, unchanged)
2-node TP=2, MTP2, fp8 KV, prefix-cache ON, decode on BreakableCapture (piecewise
collectives), prefill graph OFF, mml 40960, chunked-prefill 40960, util 0.85,
MAXTOK=4000000, bf16 state cache. `num_device_pages=14894` (~3.81M KV tokens).

## Gates (all on this exact serve life)
- **GSM8K 200 (8-shot, completions, conc 4, max_gen 2048): 0.96 strict / 0.96 flexible, 0 IMA** —
  first post-rebase tree to survive the long-generation load (see the 07-09/10 latent-IMA
  hunt: unsanitized ragged-MTP SWA slot mapping, fixed upstream by #614; trigger row =
  the smg health-probe 1-token request).
- **arthur long-context coherence (conc 12, 900 lines): 24/24.**

## Perf — llama-benchy STANDARD (pinned patched @b220b7c9, pp2048 tg128, C=1, runs 3, prefix-cache)
| depth | ctx_pp t/s | pp2048 t/s | tg128 t/s |
|---|---|---|---|
| 8192  | **1706.3 ± 3.2** | **1235.5 ± 0.8** | 36.8 ± 5.2 |
| 16384 | 1647.6 ± 2.9 | 1104.5 ± 0.9 | 36.2 ± 4.5 |
| 32768 | 1425.3 ± 99.7 | 953.1 ± 5.9 | 32.5 ± 2.0 |

vs the 07-09 pre-fix baseline (1282/967/33.9 @d8192): **ctx_pp +33%, pp2048 +28%**.
vs vLLM same-tool overlap: d8192 ctx_pp **98.9%** of vLLM's 1726 (was 74%); d32768
ctx_pp 0.89×, pp2048 0.88× (was 0.72×/0.73×).

## Provenance of the gains (30.5K cold-prefill nsys decomposition, 07-09)
1.44× GPU-time gap to vLLM decomposed into: mHC prenorm fallback glue (−3.6s, Triton
split-K port), FI sparse-MLA 64-pad waste (−2.1s, 32-head orchestrator tile), with MoE /
dense-GEMM / einsum / NCCL at parity or ahead. Remaining identified tails: indexer
scoring-shape forensics, PR#563 Q-prep, MoE epilogue fusion.

## ⚠ Gate-coverage lesson (permanent)
Long-generation loads (GSM8K-class) MUST be part of any regression battery: arthur
(384-tok gens) and benchy (128-tok) cannot reach ragged-MTP decode shapes; the latent
slot-mapping IMA survived every prior gate for a full rebase cycle. Health probes are
real traffic (1-token requests) and participate in batch shaping.
