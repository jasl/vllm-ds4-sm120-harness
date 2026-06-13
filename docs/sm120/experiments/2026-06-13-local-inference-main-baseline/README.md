# Local-Inference Main RTX Baseline

Status: observation
Date: 2026-06-13
Owner/context: external fork baseline before porting backend ideas

## Question

How fast is the latest `local-inference-lab/vllm` `main` branch under the
current RTX / SM120 EP-off production-shaped profile, and how much of the
current gap is real before we port or reimplement any mechanism from that fork?

## Profile

- Hardware: dual RTX PRO 6000 / SM120.
- vLLM branch/commit: `local-inference-lab/vllm` `main`
  `183726aaa8e7bda60e4717051ed7de8fd8b13a30`, plus a temporary
  `vllm/v1/core/kv_cache_utils.py` mixed page-size accounting patch needed for
  131K MTP startup.
- Dependency or image identity: b12x git-master package metadata `0.20.0`
  with master head `fabb087a111ff3030b556c3c091ef018d158b6e4`;
  `flashinfer-python==0.6.13rc1`;
  `flashinfer-jit-cache==0.6.13rc1+cu130`; `instanttensor==0.1.9`;
  `nvidia-nccl-cu13==2.30.7`; `torch==2.11.0+cu130`;
  `triton==3.6.0`; `ninja==1.13.0`.
- TP / PP / EP: TP=2, PP=1, EP disabled.
- MTP: MTP=2 with `moe_backend=b12x`.
- FP8 KV: enabled.
- Prefix cache: disabled for the baseline prefill and GSM8K runs.
- CUDA graph mode: `FULL_AND_PIECEWISE`.
- `max_model_len`: 131072.
- `max_num_seqs`: 16.
- `max_num_batched_tokens`: 4096.
- Other route flags: `--load-format instanttensor`, `--moe-backend b12x`,
  `--linear-backend b12x`, `--attention-backend B12X_MLA_SPARSE`,
  `--async-scheduling`, `--no-scheduler-reserve-full-isl`,
  `--enable-chunked-prefill`, `--enable-flashinfer-autotune`,
  `--gpu-memory-utilization 0.875`, and b12x/FlashInfer env from the fork's
  DS4 serve profile.

## Result

The external `main` baseline is useful as a mechanism reference, but it is not
faster than the current local RTX baseline on the cold-prefill C=1 shape.
Stable non-cold rows are roughly `6.1k-6.7k` input tok/s from 8K through 65K
and `5.7k` input tok/s at 124K, which is below our current RTX PR-line and
dev-line C=1 evidence on the overlapping 16K/65K/124K points.

| Input length | Requests | Input tok/s | Mean TTFT ms | P99 TTFT ms |
| ---: | ---: | ---: | ---: | ---: |
| 4096 | 4 | 1352.93 | 3027.34 | 10020.45 |
| 8192 | 4 | 6687.35 | 1224.88 | 1232.17 |
| 16384 | 4 | 6579.92 | 2490.90 | 2493.83 |
| 32768 | 4 | 6425.10 | 5098.65 | 5119.41 |
| 65536 | 4 | 6149.28 | 10656.28 | 10760.92 |
| 124000 | 4 | 5709.02 | 21720.46 | 22024.65 |

Same-shape comparison against the latest RTX attribution control:

| Input length | Our C=1 input tok/s | External C=1 input tok/s | External delta | Our mean TTFT ms | External mean TTFT ms |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4096 | 6241.52 | 1352.93 | -78.3% | 656.46 | 3027.34 |
| 16384 | 8080.89 | 6579.92 | -18.6% | 2027.05 | 2490.90 |
| 65536 | 7576.42 | 6149.28 | -18.8% | 8649.86 | 10656.28 |
| 124000 | 6835.25 | 5709.02 | -16.5% | 18141.62 | 21720.46 |

GSM8K limit-200 also passed under the same serve profile:
`exact_match_flexible=0.965`, `exact_match_strict=0.965`, both with stderr
`0.01302780173668803`. This does not replace full correctness gates, but it is
enough to treat the fork baseline as a useful performance target rather than a
speed-only broken route.

## Interpretation

This baseline confirms that `local-inference/main` is not the RTX C=1 endpoint
performance bar we need to chase. The useful part is still the mechanism map:
the B12X sparse MLA/indexer/MoE stack may explain community or GB10 behavior,
and it is worth isolating, but on this RTX run our current D512 path is ahead.
The newer black-benediction-specific DFlash and decode work remains second-stage
because the current local bottleneck is cold-prefill sparse accumulation.

The result is not directly PR-promotable:

- The fork did not start on the 131K MTP profile until the temporary mixed
  page-size KV cache accounting patch was applied. That patch is a separate
  upstreamability item.
- b12x PCIe oneshot allreduce was requested, but the extension failed to build
  on this environment and runtime fell back to PyNCCL. The measured numbers are
  therefore not dependent on a working b12x PCIe allreduce extension.
- The attribution wrapper reports overall `OK=False` because the B12X route
  does not emit this harness's sparse MLA stats counters. Per-case
  `server_startup` and `bench_random_prefill_sweep` phases exited `0`, and the
  benchmark summaries report `ok=true`.
- The 4K row has a cold first-request outlier and should not be used as the
  stable hot-path comparison.

Profile sensitivity is explicit: this is EP-off, prefix-cache-off, MTP=2, FP8
KV, `FULL_AND_PIECEWISE`, RTX / SM120 evidence only. GB10 / SM121 and
prefix-cache-enabled user gates remain required before adopting any mechanism.

## Follow-Up

- Create or update decision:
  `docs/sm120/decisions/watchlist/2026-06-12-backend-parity-roadmap.md`.
- Rerun trigger: `local-inference-lab/vllm` `main` moves a DS4 B12X sparse MLA,
  sparse indexer, MoE, KV-cache, or scheduler mechanism; b12x exposes a new
  public DS4 route; or a GB10/user workload shows the fork route winning under
  the same profile.
- Next command or next owner: isolate whether any `local-inference/main`
  mechanism helps GB10, multi-user, MoE, decode, or prefix-cache shapes that
  are not explained by the RTX C=1 result, starting with the B12X MLA
  sparse/indexer path and the mixed page-size KV cache accounting fix.
