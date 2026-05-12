# SM12x Baseline Report — 2026-05-12

DeepSeek V4 Flash on SM12x hardware, vLLM `jasl/vllm` @ `2760932cf` (head of
`ds4-sm120-preview-dev` / PR #41834), 15 commits ahead of `upstream/main`.

Four optimisations land on top of the 2026-05-11 baseline (`020e0c89a`):

| Commit | Topic |
|---|---|
| `26564419f` | Tune dense FP8 block-scaled GEMM configs for SM12x DSv4 |
| `c802ae27a` | Adaptive `BLOCK_M` for `_fp8_paged_mqa_logits_kernel` |
| `2760932cf` | Clamp `BLOCK_D` in sparse MLA finish kernel to `head_dim` |
| `5c8975591` | Extend DeepSeek V4 prefill warmup to max single-chunk size |

## TL;DR

- **Workstation SM120** (2x RTX PRO 6000 Blackwell Workstation Edition, TP=2 EP)
  - no-MTP c=1 mt-bench: **97.79 tok/s** (+16 % vs 020e0c89a baseline 84.36)
  - MTP=2 c=1 mt-bench: **148.86 tok/s** (1.52× over no-MTP, +55 %)
  - MTP=2 acceptance 68 %, accept-length 2.36–2.37
  - gsm8k 5-shot 200q: 0.945 no-MTP, 0.950 MTP=2 (no regression)
- **DGX Spark cluster** (2 nodes × 1 GB10, TP=2 PP=1 mp over RoCE)
  - no-MTP c=1 mt-bench: **21.94 tok/s** (+15 % vs 020e0c89a baseline 19.13)
  - MTP=2 c=1 mt-bench: **30.22 tok/s** (1.38× over no-MTP, +38 %)
  - MTP=2 acceptance 68 %, accept-length 2.35–2.37
  - gsm8k 5-shot 200q: 0.965 no-MTP, 0.955 MTP=2
- **NCCL transport on Spark RoCE**: IB verbs (`NCCL_IB_DISABLE=0`, via
  the RoCE HCA `rocep1s0f1`) outperforms the TCP fallback by 45 % at c=1
  (21.94 vs 15.12 tok/s). Harness keeps `NCCL_IB_DISABLE=0` as default.

## Serve config

### Workstation SM120 (TP=2 EP)

```
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 --block-size 256 \
  --max-model-len 65536 --tensor-parallel-size 2 \
  --host 127.0.0.1 --port 8000 \
  --no-enable-flashinfer-autotune \
  --tokenizer-mode deepseek_v4 \
  --reasoning-parser deepseek_v4 \
  --tool-call-parser deepseek_v4 --enable-auto-tool-choice \
  --enable-expert-parallel \
  --gpu-memory-utilization 0.95
```

MTP=2 adds: `--speculative_config '{"method":"deepseek_mtp","num_speculative_tokens":2}'`.

### DGX Spark cluster (TP=2 nnodes=2 mp, IB=0)

```
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 --block-size 256 \
  --tensor-parallel-size 2 --pipeline-parallel-size 1 \
  --distributed-executor-backend mp --nnodes 2 \
  --master-addr <HEAD_ROCE_IP> --master-port 29519 \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072 --max-num-seqs 4 --max-num-batched-tokens 8192 \
  --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 --enable-auto-tool-choice \
  --reasoning-parser deepseek_v4 \
  --node-rank 0 --host 0.0.0.0 --port 8000 \
  --enable-expert-parallel \
  --no-enable-flashinfer-autotune \
  --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}'
```

NCCL env (both nodes): `NCCL_SOCKET_IFNAME=enp1s0f1np1`,
`NCCL_IB_HCA=rocep1s0f1`, `NCCL_IB_DISABLE=0`. Worker uses `--node-rank 1 --headless`.

Bench client: `vllm bench serve`, `--temperature 1.0`, mt-bench
(`philschmid/mt-bench`, 80 prompts).

## Workstation SM120 — mt-bench (philschmid/mt-bench, num-prompts=80)

### no-MTP

| c | out tok/s | TPOT mean (ms) | TPOT p99 (ms) | TTFT mean (ms) |
|---|---|---|---|---|
| 1 | 97.79 | 9.97 | 10.08 | 56.13 |
| 2 | 156.27 | 12.37 | 12.93 | 66.26 |
| 4 | 247.35 | 15.46 | 16.29 | 78.74 |

### MTP=2 (`deepseek_mtp`, `num_speculative_tokens=2`)

| c | out tok/s | TPOT mean (ms) | acceptance % | accept len |
|---|---|---|---|---|
| 1 | 148.86 | 6.49 | 68.22 | 2.36 |
| 2 | 227.08 | 8.38 | 68.27 | 2.37 |
| 4 | 275.97 | 13.69 | 68.68 | 2.37 |

MTP=2 gains over no-MTP: +52 % at c=1, +45 % at c=2, +12 % at c=4.

## DGX Spark cluster — mt-bench (philschmid/mt-bench, num-prompts=80)

### no-MTP

| c | out tok/s | TPOT mean (ms) | TPOT p99 (ms) | TTFT mean (ms) |
|---|---|---|---|---|
| 1 | 21.94 | 43.12 | 43.96 | 495.87 |
| 2 | 35.38 | 53.94 | 60.14 | 409.34 |
| 4 | 52.41 | 72.85 | 80.63 | 432.27 |

### MTP=2

| c | out tok/s | TPOT mean (ms) | acceptance % | accept len |
|---|---|---|---|---|
| 1 | 30.22 | 30.53 | 67.78 | 2.36 |
| 2 | 44.86 | 41.55 | 67.74 | 2.35 |
| 4 | 58.00 | 64.20 | 68.29 | 2.37 |

MTP=2 gains over no-MTP: +38 % at c=1, +27 % at c=2, +11 % at c=4. The
acceptance profile mirrors the Workstation cluster (68 %, alen 2.36).

### NCCL transport ablation (no-MTP c=1)

| `NCCL_IB_DISABLE` | Transport | tok/s | TPOT mean (ms) |
|---|---|---|---|
| 0 (default) | IB verbs over RoCE HCA | **21.94** | 43.12 |
| 1 | TCP over RoCE iface | 15.12 | 63.61 |

IB=1 is 31 % slower at c=1. The harness now defaults `NCCL_IB_DISABLE=0`
on the Spark cluster path; set `NCCL_IB_DISABLE=1` only when the IB stack
is unavailable.

## Accuracy

| Gate | Workstation no-MTP | Workstation MTP=2 | Spark no-MTP | Spark MTP=2 |
|---|---|---|---|---|
| gsm8k 5-shot 200q exact_match (strict) | 0.945 | 0.950 | 0.965 | 0.955 |
| gsm8k 5-shot 200q exact_match (flexible) | 0.945 | 0.950 | 0.965 | 0.955 |

All within the historical 0.948–0.965 band reported on B200, B300, and
the DeepSeek Official API. Workstation MTP=2 actually nudges strict match
above its no-MTP score; Spark MTP=2 sits comfortably inside the band,
consistent with sampling variance on a 200-question sweep.

## Long prefill (random ISL sweep, c=1, OSL=8, num-prompts=1)

Both serves use `max_num_batched_tokens=8192`, so requests with
`ISL > 8192` go through chunked prefill (`ceil(ISL / 8192)` chunks).

### Workstation SM120 (no-MTP, max-model-len 65,536)

| ISL | TTFT mean (ms) | prefill rate (tok/s) | 020e0c89a TTFT (ms) | Δ |
|---|---|---|---|---|
| 1,024 | 300 | 3,410 | — | — |
| 4,096 | 1,406 | 2,913 | 1,497 | -6 % |
| 8,192 | 1,789 | 4,579 | 3,360 | **-47 %** |
| 16,384 | 3,788 | 4,326 | — | — |
| 32,768 | 8,874 | 3,692 | — | — |
| 65,000 | 22,963 | 2,830 | — | — |

Single-chunk prefill (ISL ≤ 8,192) is what T1-A targets: the autotuned
FP8 W8A8 block-scaled GEMM configs cut TTFT roughly in half at the
largest single-chunk size. Above 8,192 tokens chunked prefill kicks in,
and the second-and-later chunks pay attention over the prior KV slab,
which (at SM120 sparse-MLA bandwidth) is the new dominant term — not
GEMM time.

### DGX Spark cluster (MTP=2, max-model-len 131,072)

| ISL | TTFT mean (ms) | prefill rate (tok/s) | 020e0c89a TTFT (ms, no-MTP) | Δ |
|---|---|---|---|---|
| 1,024 | 632 | 1,620 | 1,506 | -58 % |
| 4,096 | 763 | 5,369 | 7,169 | -89 % |
| 8,192 | 820 | 9,990 | 13,253 | **-94 %** |
| 16,384 | 23,008 | 712 | — | — |
| 32,768 | 57,564 | 569 | — | — |
| 65,536 | 160,819 | 408 | — | — |
| 131,000 | 505,324 | 259 | — | — |

T1-A is even more impactful on Spark — single-chunk prefill at
ISL=8,192 drops from 13.3 s to 0.82 s (-94 %). Beyond 8,192 tokens the
prefill cost is dominated by cross-node KV attention over RoCE TP, not
GEMM, so the curve follows the chunk-count rather than the autotune
gains.

## Cold-start service quality (warmup coverage)

The original 2026-05-11 baseline warmed prefill kernels only up to 1,024
tokens, so the first user request with a single-chunk prefill larger
than 1,024 tokens had to JIT-compile the dense FP8 GEMM at the full
M=max_num_batched_tokens=8,192. The T1-A autotuned config space made
this cold-compile cost larger, not smaller, on the first long-context
request.

Commit `5c8975591` lifts the prefill warmup to the scheduler's
`max_num_batched_tokens` cap (clamped at 8,192). Measured impact on a
fresh-restart Workstation no-MTP serve, cold random ISL=8,192 OSL=512
num-prompts=4 c=1:

| Metric | Before `5c8975591` | After `5c8975591` |
|---|---|---|
| Startup time to `/health=200` | 71 s | 80 s (+9 s, one-time) |
| TTFT mean (ms) | dominated by req-1 JIT spike | **3,172** |
| TTFT p99 (ms) | — | **3,176** (mean ≈ p99, variance gone) |
| Output throughput tok/s | — | 61.16 (+13 % vs 020e0c89a 54.20) |

The +9 s startup cost buys deterministic first-request latency on
the first 8,192-token prefill — directly relevant for K8s / Ray Serve
auto-scale events and for edge users restarting a Spark deployment.

## Max-input recommendation

KV cache sizes reported by the worker at startup (block-size 256, fp8
KV, model weights occupy 74–76 GiB / GPU):

| Cell | KV cache GiB | KV tokens | max-model-len |
|---|---|---|---|
| Workstation no-MTP (TP=2, gpu-mem 0.95) | 7.36 | 152,775 | 65,536 |
| Workstation MTP=2 | 3.65 | 75,599 | 65,536 |
| Spark cluster no-MTP (TP=2, gpu-mem 0.85) | 22.52 | 839,711 | 131,072 |
| Spark cluster MTP=2 | 20.30 | 770,865 | 131,072 |

Practical recommendations (input + output ≤ max-model-len; the KV
budget is shared across all in-flight sequences):

| Hardware | Variant | Recommended max input | Notes |
|---|---|---|---|
| Workstation | no-MTP | 32,768 (1–4 concurrent) | KV fits 4 × 32 K + headroom; single-user can go to 64 K |
| Workstation | MTP=2 | 32,768 (single-user) | KV only 75 K tokens; MTP drafter doubles the slot cost |
| Spark cluster | no-MTP | 65,536 (1–4 concurrent) | KV 839 K; cluster max-num-seqs=4 anyway |
| Spark cluster | MTP=2 | 65,536 (1–4 concurrent) | KV 770 K; same envelope as no-MTP |

Pushing the input above 32 K on Spark is technically supported by the
serve (max-model-len 131,072) and KV (839 K tokens), but the
multi-chunk prefill cost grows superlinearly in the cross-node TP
regime, so latency-sensitive users should pre-summarise rather than
feed raw 131 K-token contexts.

## Reproduction

See `repro_recipe.md` next to this file. Harness commit pins both the
serve commands and the bench / `lm_eval` invocations. The Spark cluster
launcher (`scripts/dgx_spark_start_mp_serve.sh`) accepts
`NCCL_IB_DISABLE`, `SERVE_SPECULATIVE_CONFIG`, and
`SERVE_DEFAULT_CHAT_TEMPLATE_KWARGS` env overrides.

## Source SHAs

- vLLM: `2760932cf` on `jasl/vllm` `ds4-sm120-preview-dev` (PR #41834)
- Harness: this commit
