# GB10 2×SM121 DeepSeek-V4-Flash baseline — `f41d6c6919` (2026-07-07)

**Baseline of record** after the upstream merge to `86db6c3070` (incl. #47716 DSv4
fp8_ds_mla KV-reshape fix + #47474 dsv4 token_to_req_indices caching) and the
FlashInfer 0.6.14 pin. Use this as the fixed reference for future DeepSeek-V4-Flash
SM120 optimization on GB10.

## Build / environment
| | |
|---|---|
| vLLM head | `f41d6c6919` (codex/ds4-sm120-min-enable == dev; = merge→86db6c3070 + FI-0.6.14 pin) |
| vllm version | `20260621.dev696+gf41d6c691` |
| torch | 2.11.0+cu130 |
| flashinfer | 0.6.14 (python + cubin; `_sparse_mla_sm120` BPT 584) |
| nvidia-nccl-cu13 | 2.30.7 (RoCE-fabric pin; re-pinned post-build) |
| GPUs | 2× GB10 (SM121a), TP=2, RoCE switched CRS804 fabric (192.168.100.116/.119, rail-0) |

## Serve config (pinned standard)
`MTP2` (`{"method":"deepseek_mtp","num_speculative_tokens":2}`), fp8 KV
(`fp8_ds_mla`), prefix-cache ON, `cudagraph_mode=FULL_AND_PIECEWISE`,
`max-model-len 49152`, `gpu-mem-util 0.85`, `max-num-seqs 64`,
`max-num-batched-tokens 8192`. KV cache = 284,246 tokens. Steady prefix-cache hit
45.2%.

## Perf — llama-benchy STANDARD (pinned `@b220b7c9`, pp2048 tg128, C=1, 3 runs, prefix-cache)
| depth | ctx_pp t/s | pp2048 t/s | tg128 t/s (peak) | ctx_tg t/s |
|---|---|---|---|---|
| 8192  | 1810.5 ± 27.1 | 1396.1 ± 12.9 | 43.1 ± 1.5 (47.3) | 43.0 ± 1.6 |
| 16384 | 1769.9 ± 7.4  | 1308.8 ± 2.0  | 36.6 ± 3.2 (41.3) | 41.8 ± 1.2 |
| 32768 | 1595.9 ± 68.1 | 1089.1 ± 128  | 37.0 ± 0.8 (41.7) | 38.8 ± 2.0 |

Raw: [`llama_benchy.out`](./llama_benchy.out). (Comparable only to other runs on the
same pinned `@b220b7c9` tool — the pre-07-06 floating-benchy numbers are ~1.7× off
and NOT comparable.)

## Correctness / functional (this head, this serve)
- **GSM8K** (thinking on): **189/200 = 0.945** (150q run = 0.947); ~baseline. Most
  misses are answer-extraction/truncation artifacts, not model errors.
- **Tool-calling + reasoning** (MTP + forced `tool_choice` + thinking, 42 reqs @ c=10):
  **42/42 → 200, 0×500**, 0 grammar-reject — the #44297 reasoning-boundary fix holds
  post-merge (the original PR#41834 report).
- **fp8_ds_mla KV-reshape crash** (`kv_cache last dim must be 584, got 512`): **fixed**
  (was #42890-introduced in the prior upstream window; #47716 restores it). Serve
  starts clean, KV cache allocates.
- Coherence: 2+2→4, capital of France→Paris, 60km/1.5h→40 km/h.

## Reproduce
```bash
# from a GB10 head node; benches the built worktree without touching the main checkout
VLLM_ROOT=/home/jasl/tmp/vllm-merge-20260707 \
VLLM_VENV=/home/jasl/tmp/ds4-sm120-harness/vllm/.venv \
  scripts/run_gb10_llama_benchy_standard.sh
```
(The standard runner was updated this session: `VLLM_ROOT` is now overridable and
the topology defaults to the switched CRS804 fabric.)
