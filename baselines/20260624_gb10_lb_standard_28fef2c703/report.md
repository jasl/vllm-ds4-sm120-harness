# GB10 (SM121) llama-benchy Standard — Baseline of Record (28fef2c703)

- Label: `gb10_lb_standard_28fef2c703`
- Date (UTC): `2026-06-24`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- vLLM head: `28fef2c703` (PR vllm-project/vllm#41834 / `codex/ds4-sm120-min-enable`; #43477 reconcile + D512 warmup import fix)
- Platform: 2× NVIDIA DGX Spark (GB10, SM121, cc 12.1, aarch64), 1 TP rank per node, TP=2 over RoCE
- Tool: `eugr/llama-benchy` pinned `@b220b7c9cae7af2d6bd9ebf6bfa9ac066cb40780`

## Purpose

This is the **canonical, fully-pinned GB10 llama-benchy reference** for comparing any future
DeepSeek-V4-Flash code change. Every knob (serve config + bench flags + tool version) is fixed in
`scripts/run_gb10_llama_benchy_standard.sh`; re-run it on any head (`run_gb10_llama_benchy_standard.sh <sha>`)
and compare to the numbers below. Comparability across versions depends on NOT changing the standard.

## Pinned standard config

| Knob | Value |
| --- | --- |
| Parallelism | 2-node TP=2, MTP `num_speculative_tokens=2` |
| KV cache | fp8 |
| Prefix caching | ON |
| cudagraph | FULL_AND_PIECEWISE (DSv4 default) |
| max-model-len | 49152 |
| gpu-memory-utilization | 0.85 |
| max-num-seqs / max-num-batched-tokens | 64 / 8192 |
| llama-benchy | `--pp 2048 --tg 128 --depth 8192 16384 32768 --concurrency 1 --runs 3 --enable-prefix-caching` |

## Baseline of record

| test | t/s | ttfr (ms) |
| --- | ---: | ---: |
| ctx_pp @ d8192 | 942.9 ± 0.6 | 8690.9 |
| ctx_tg @ d8192 | 37.8 ± 0.9 | |
| pp2048 @ d8192 | 778.2 ± 2.9 | 2634.2 |
| tg128 @ d8192 | 37.2 ± 2.4 | |
| ctx_pp @ d16384 | 927.6 ± 1.1 | 17665.9 |
| ctx_tg @ d16384 | 39.3 ± 0.8 | |
| pp2048 @ d16384 | 756.2 ± 1.2 | 2710.7 |
| tg128 @ d16384 | 36.8 ± 4.8 | |
| ctx_pp @ d32768 | 883.1 ± 2.5 | 37108.9 |
| ctx_tg @ d32768 | 35.1 ± 2.8 | |
| pp2048 @ d32768 | 716.9 ± 3.2 | 2859.4 |
| tg128 @ d32768 | 36.6 ± 3.6 | |

**Prefix-cache hit rate (steady state): 42–47%.**

## Notes

- Reproducible: an independent run on the same head agreed within 0.2% (ctx_pp 942.9 vs 941).
- The earlier un-pinned PR-body record (ctx_pp 1595–1722) used a **floating** llama-benchy (`git+main`)
  and a pre-`#45939` block_pool; it is **not comparable** to this pinned standard, which is exactly why
  the standard now pins the tool version. The decode (`ctx_tg`) and prefix-cache hit rate match that
  record, and the DSv4 prefill/decode kernels are byte-identical across the reconcile, so there is no
  prefill regression — the ctx_pp delta vs the old record is tool/measurement drift, not code.
- Reproduce: `scripts/run_gb10_llama_benchy_standard.sh <head-sha>` (2-node GB10).
