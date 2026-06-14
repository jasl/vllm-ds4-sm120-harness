# Evidence

## Public Source

- NVIDIA Developer Forums thread:
  <https://forums.developer.nvidia.com/t/deepseek-v4-flash-aiden-recipe-from-reddit-1m-token-session-operational-cuda-12-1-tailored-for-dgx-spark-gb10/372268>
- Page 2 community validation:
  <https://forums.developer.nvidia.com/t/deepseek-v4-flash-aiden-recipe-from-reddit-1m-token-session-operational-cuda-12-1-tailored-for-dgx-spark-gb10/372268?page=2>
- Page 3 deployment / NCCL / cache discussion:
  <https://forums.developer.nvidia.com/t/deepseek-v4-flash-aiden-recipe-from-reddit-1m-token-session-operational-cuda-12-1-tailored-for-dgx-spark-gb10/372268?page=3>
- Page 4 long-running KV-cache discussion:
  <https://forums.developer.nvidia.com/t/deepseek-v4-flash-aiden-recipe-from-reddit-1m-token-session-operational-cuda-12-1-tailored-for-dgx-spark-gb10/372268?page=4>

## Public Claims To Reproduce

From the initial public recipe:

- Image: `aidendle94/sparkrun-vllm-ds4-gb10:production-ready`.
- Hardware: two DGX Spark / GB10-class nodes with ConnectX-7 200Gbps RoCE.
- Serve shape: TP=2, PP=1, MP executor, FP8 KV, MTP=2, prefix cache enabled,
  `max_model_len=1000000`, `max_num_seqs=6`,
  `max_num_batched_tokens=8192`, `gpu_memory_utilization=0.82`.
- Reported long-context single-request prefill/decode samples:

| Context | Prefill tok/s | Decode tok/s | TTFT |
| ---: | ---: | ---: | ---: |
| 0 | 1188 | 45.7 | 1s |
| 240K | 1710 | 39.4 | 2.4m |
| 384K | 1510 | 36.4 | 4.3m |
| 512K | 1374 | 36.1 | 6.2m |
| 720K | 1187 | 35.0 | 10.1m |
| 980K | 986 | 30.4 | 16.6m |

From a later community measurement in the same thread:

| Test | Reported tok/s or latency |
| --- | ---: |
| Prefill depth 0, C=1 | 1574 tok/s |
| Prefill depth 8192, C=1 | 1586 tok/s |
| Generation depth 0, C=1 | 35.6 tok/s |
| Generation depth 0, C=4 | 63.9 tok/s |
| Generation depth 4096, C=4 | 30.8 tok/s |
| Generation depth 8192, C=4 | 23.5 tok/s |
| TTFT depth 0, C=1 | 1276 ms |

## Reliability Signals

The thread is not uniformly positive:

- Users discuss needing upgraded NCCL and correct RDMA/NIC configuration.
- There are reports of long-running KV-cache bloat and decode slowdown after
  extended agent sessions.
- One public diagnosis points at a vLLM block-pool cached-block eviction bug
  that can leave stale hashes and hurt prefix-cache behavior.
- The image maintainer indicated a KV-cache reliability fix was planned, so
  image digest and update time must be recorded for every comparison.

## Local Relation

This source should be compared against existing local notes, not treated as a
new baseline by itself:

- current GB10 Dev prefix-off versus Aiden prefix-off parity numbers already
  show Aiden about `1.3-1.5x` faster in 4K/16K/32K/65K raw prefill.
- a B12X-MoE-off Aiden run still beat current Dev by about `1.26-1.42x`,
  so the gap is not explained by B12X MoE alone.
- exposed sparse-indexer-only env toggling did not explain the gap either.
- public b12x direct compressed MLA and sparse-indexer routes remain
  insufficient on our normal stack.

Conclusion: study the integrated image overlay and packed sparse-MLA dataflow,
not isolated serving flags.
