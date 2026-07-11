# GB10 2×SM121 DeepSeek-V4-Flash baseline — `5e43b2cfa7` (2026-07-11)

**New baseline of record** after merging upstream/main `3d99b0499a` (181 commits on
top of the 07-07 base `86db6c3070`) into the SM12x fork, absorbing PR #48304 (MTP
unscaled-draft-rope), and 3 fork-tidy comment fixes. Supersedes
`2026-07-07-advmerge-f41d6c6919-baseline`.

## Build / environment
| | |
|---|---|
| vLLM head | `5e43b2cfa7` (merge `45a7d671cd` + #48304 `b9980bdf79` + tidy) |
| merge | advance-delta merge of `86db6c3070..3d99b0499a` (181 upstream commits); 7 conflicts hand-resolved, 0 fork features dropped |
| torch | 2.11.0+cu130 |
| flashinfer | 0.6.14 (python + cubin; `_sparse_mla_sm120` BPT 584) |
| nvidia-nccl-cu13 | 2.30.7 (RoCE-fabric pin; `--override` during build + verified) |
| custom ops | migrated to libtorch-stable ABI (`_C_stable_libtorch`, `_moe_C_stable_libtorch`) by upstream |
| GPUs | 2× GB10 (SM121a), TP=2, RoCE switched CRS804 fabric (192.168.100.116/.119) |

## Serve config (pinned standard — unchanged from f41d6c6919)
`MTP2` (`{"method":"mtp","num_speculative_tokens":2}`), fp8 KV (`fp8_ds_mla`),
prefix-cache ON, `cudagraph_mode=FULL_AND_PIECEWISE`, `max-model-len 49152`,
`gpu-mem-util 0.85`, `max-num-seqs 64`, `max-num-batched-tokens 8192`.

## Perf — llama-benchy STANDARD (pinned `@b220b7c9`, pp2048 tg128, C=1, 3 runs, prefix-cache; fresh serve)
| depth | ctx_pp t/s | pp2048 t/s | tg128 peak t/s | vs f41d6c6919 |
|---|---|---|---|---|
| 8192  | 1757.2 ± 64.8 | 1391.7 ± 7.7 | 48.3 (mean 41.9) | ctx_pp −2.9%, pp2048 −0.3%, tg +2.2% |
| 16384 | 1773.9 ± 15.0 | 1321.8 ± 5.4 | 45.0 (mean 39.6) | ctx_pp +0.2%, pp2048 +1.0%, tg +9.0% |
| 32768 | 1699.3 ± 12.5 | 1200.4 ± 0.6 | 40.7 (mean 37.1) | ctx_pp **+6.5%**, pp2048 **+10.2%**, tg −2.5% |

Net: **prefill flat-to-up, decode healthy at all depths** (the deep-context prefill
gain tracks #47474 dsv4 token_to_req caching + the packed-page/KV work). No
regressions. Prefix-cache hit 43.1% (baseline 45.2%). Raw:
[`llama_benchy.out`](./llama_benchy.out).

## Correctness / functional (this head, this serve — all GREEN)
- **GSM8K** (200q, 8-shot, max_gen 2048): **0.96 strict/flexible** (baseline 0.945); IMA-clean throughout the long-gen run.
- **Tool-calling** (MTP + forced `tool_choice` + thinking, 42 reqs @ c=6): **42/42 tool_calls, 0×500** — #44297 reasoning-boundary fix holds post-merge.
- **Coherence/recall** (arthur, ~28k ctx): **c=1 4/4 (deterministic, perfect recall)**; **c=12 22-23/24** (IMA=0, coherent output). The marginal *earliest* needle occasionally flips under concurrency-12 batch numerics (greedy+MTP: batch composition changes FP reduction order) — this is a pre-existing concurrency-stress sensitivity, **not** recall corruption. Confirmed by: c=1 perfect; GSM8K 0.96; the KV-alignment change resolves to 576 for our fp8_ds_mla path (unchanged); the cache_utils packed-page remap (#44577) is on the non-SM12x FlashInfer path we bypass; no indexer pruning at 28k (topk 512 ≫ ~110 blocks). Not a merge regression.
- **#19 instruction-following** (JSON-only): **PASS**.
- **MTP acceptance**: mean length 2.4, avg draft accept 67–75%, per-position 0.94 / 0.40–0.55.

## ⚠ KV capacity change (behavior, tunable — NOT a regression)
GPU KV cache = **171,546 tokens** at util 0.85, vs baseline's 284,246. Cause:
upstream's **CUDA-graph memory profiler** (default since v0.21.0) now reserves
cudagraph + peak-activation memory upfront (the old build effectively
over-allocated KV). The serve log's own guidance: raise `--gpu-memory-utilization`
to ~0.876, or set `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0`, to restore the
prior effective KV size. No effect on the C=1 benchmarked perf or correctness;
only high-concurrency long-context capacity is affected.

## Review outcome (3-agent audit, this session)
- **Integrity**: 0 fork features silently dropped by the 181-commit merge; all SM12x mechanisms intact (crash-guard, `is_dsv4_sm120_fi_prefill_active`, int64 recall casts, 31 fork envs, DSpark wiring, warmup fns).
- **Upstream adoption**: no fork workaround obviated (all still needed). A1 (#47408 routed-scale moved into the topk kernel) verified — our DSv4 passes `routed_scaling_factor` to the shared `fused_topk_bias` exactly once, no double-apply (GSM8K 0.96 confirms). A2 (#47785 moe_align padding) inherited via the csrc rebuild.
- **Fork tidy**: delta clean; deferred cleanups (≈1095 lines verified-dead Triton kernels in `sparse_mla_kernels.py`, DSpark dead stores) tracked separately (zero-runtime-effect).

## Reproduce
```bash
# from a GB10 head node; benches the built merge worktree without touching the main checkout
VLLM_ROOT=/home/jasl/tmp/vllm-merge-20260711 \
VLLM_VENV=/home/jasl/tmp/ds4-sm120-harness/vllm/.venv \
  scripts/run_gb10_llama_benchy_standard.sh
```
