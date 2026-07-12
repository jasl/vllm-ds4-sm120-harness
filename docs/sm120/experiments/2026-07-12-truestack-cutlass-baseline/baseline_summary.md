# GB10 2×SM121 tokenspeed DSv4-Flash — TRUE-STACK baseline (2026-07-12): torch 2.13 × CUTLASS MoE

**The stable/preview promotion target and the community-invite baseline.** First full validation of the complete stack (torch 2.13 + FlashInfer CUTLASS MXFP4 MoE + CuTeDSL 4.6 + rebased upstream), after clearing the torch-bump ABI minefield.

## Build / environment
| | |
|---|---|
| tokenspeed | `feat/sm12x-engine` @ **`d73ee96`** (52-commit SM12x stack on upstream, incl #644/#645/#646 FI-CUTLASS-MoE picks, CuTeDSL 4.6, torch-2.13 pin, deep_gemm gate waiver) |
| torch | **2.13.0+cu130** |
| NCCL | **nvidia-nccl-cu13==2.30.4** (mandatory; `--no-deps` post-kernel-build) |
| CuTeDSL | 4.6.0 · FlashInfer 0.6.14 + **flashinfer-jit-cache 0.6.14+cu130** (skips 10-30min cold MoE JIT) |
| triton | tokenspeed-triton 3.8.10 + stock 3.7.1 |
| MoE backend | **`--moe-backend flashinfer_cutlass`** (registry auto-picks triton; must force) |
| GPUs | 2× GB10 (SM121a), TP=2, CRS804 switched RoCE |

## torch-2.13 ABI minefield (all fixed; see build-recipe memory)
Every torch-linked .so needed rebuild or removal, else crash at first lazy import (`undefined symbol: c10::...cow::materialize_cow_storage`): tokenspeed-kernel (rm objs), scheduler (rm build), **fast_hadamard_transform** (git-source rebuild — PyPI sdist broken), **torchvision/torchaudio** (uninstall — torchvision::nms breaks transformers import), **deep_gemm** (retired: gate waived in d73ee96, not in the sm12x serving path). The repo now pins torch==2.13.0 so kernel rebuilds can't silently revert it.

## Gates (this stack, one deploy)
- GSM8K longgen (limit 50): **PASS 0.96, 0 IMA**
- arthur coherence (conc 12, 900 lines): **24/24**

## Perf — llama-benchy STANDARD (pinned @b220b7c9, C=1, runs 3, prefix-cache)
| depth | ctx_pp t/s | pp2048 t/s | tg128 peak t/s |
|---|---|---|---|
| 8192  | **2056.5 ± 3.7** | 1403.8 ± 1.2 | 30.3 ± 4.7 |
| 16384 | **2062.0 ± 5.4** | 1329.5 ± 6.5 | 28.7 ± 3.8 |
| 32768 | **1979.2 ± 7.0** | 1149.3 ± 4.7 | 33.3 ± 0.5 |

## vs vLLM fork `5e43b2cfa7` (07-11 refresh, same fabric/tool)
| metric | d8192 | d16384 | d32768 |
|---|---|---|---|
| ctx_pp | **117.0%** | **116.2%** | **116.5%** |
| pp2048 | 100.9% | 100.6% | 95.7% |
| tg128 peak | 62.7% | 63.8% | 81.8% |

**Verdict: prefill DOMINATES (+16-17%), pp2048 parity, decode BEHIND (63-82%).**

## The mutual-exclusion finding (drives the roadmap)
The torch-2.13 decode gain (tg128 ~38 on the triton MoE) and the CUTLASS prefill
gain do NOT stack: CUTLASS grouped-GEMM decode (small-M) is weak and eats the
2.13 host-side win. The single-residency **hybrid MoE** (prefill→CUTLASS,
decode→triton; StridedLayout zero-copy weight sharing GO-confirmed by microbench,
bitwise-identical, parity at all decode M) is the fix — DEFERRED per the 07-12
ship decision. Shipping now with CUTLASS default: prefill is the community's #1
pain point (wingcomm 1M, brianmiller 121K), decode gap is honestly disclosed.
