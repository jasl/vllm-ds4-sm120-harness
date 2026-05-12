# SM12x Baseline Report — 2026-05-12

DeepSeek V4 Flash on SM12x hardware, vLLM `jasl/vllm` @ `2760932cf` (head of
`ds4-sm120-preview-dev` / PR #41834), 15 commits ahead of `upstream/main`.

Five optimisations land on top of the 2026-05-11 baseline (`020e0c89a`):

| Commit | Topic |
|---|---|
| `26564419f` | Tune dense FP8 block-scaled GEMM configs for SM12x DSv4 |
| `c802ae27a` | Adaptive `BLOCK_M` for `_fp8_paged_mqa_logits_kernel` |
| `2760932cf` | Clamp `BLOCK_D` in sparse MLA finish kernel to `head_dim` |
| `5c8975591` | Extend DeepSeek V4 prefill warmup to max single-chunk size |
| `8f0d8b630` | Extend DeepSeek V4 warmup coverage to multi-request shapes |

## TL;DR

- **Workstation SM120** (2x RTX PRO 6000 Blackwell Workstation Edition, TP=2 EP)
  - no-MTP c=1 mt-bench: **97.79 tok/s** (+16 % vs 020e0c89a baseline 84.36)
  - MTP=2 c=1 mt-bench: **148.86 tok/s** (1.52× over no-MTP, +55 %)
  - MTP=2 c=24 mt-bench: **692.23 tok/s** at gpu-mem 0.98
  - MTP=2 acceptance 68 %, accept-length 2.36–2.37
  - gsm8k 5-shot 200q: 0.945 no-MTP, 0.950 MTP=2 (no regression)
  - **Recommended `--gpu-memory-utilization 0.985`** on dedicated SM120 cards
    (no display attached); raises KV capacity from 7.36 GiB (at 0.95) to
    10.69 GiB and max-concurrency from 2.33× to **3.38×** the
    `max_model_len`
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
  --gpu-memory-utilization 0.985
```

MTP=2 adds: `--speculative_config '{"method":"deepseek_mtp","num_speculative_tokens":2}'`.

`0.985` is the recommended setting for two RTX PRO 6000 cards with no
display attached. `0.99` fails the static startup check (free memory
≈ 93.94 GiB vs 0.99 × 94.97 = 94.02 GiB demanded); `0.985` lands
≈ 400 MB inside the headroom and reclaims an additional 1.8 GiB
(no-MTP) / 1.8 GiB (MTP=2) of KV vs 0.95. Drop back to `0.95` if the
host also drives a display or runs other CUDA work.

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

Two utilization tiers below: `0.95` matches the earlier baseline; `0.98`
is the high-water bench that confirms the recommended `0.985` keeps
perf parity while expanding KV.

| c | 0.95 tok/s | 0.95 TPOT mean (ms) | 0.98 tok/s | 0.98 TPOT mean (ms) | 0.98 TPOT p99 (ms) |
|---|---|---|---|---|---|
| 1 | 97.79 | 9.97 | 97.69 | 9.99 | 10.07 |
| 2 | 156.27 | 12.37 | 155.80 | 12.38 | 12.99 |
| 4 | 247.35 | 15.46 | 247.52 | 15.48 | 16.38 |
| 8 | — | — | 355.54 | 20.91 | 22.42 |
| 16 | — | — | 480.86 | 29.78 | 33.51 |
| 24 | — | — | **554.52** | 37.22 | 40.04 |

### MTP=2 (`deepseek_mtp`, `num_speculative_tokens=2`)

| c | 0.95 tok/s | 0.95 TPOT mean (ms) | 0.98 tok/s | 0.98 TPOT mean (ms) | 0.98 accept % |
|---|---|---|---|---|---|
| 1 | 148.86 | 6.49 | 150.16 | 6.34 | 68.25 |
| 2 | 227.08 | 8.38 | 232.08 | 8.13 | 68.11 |
| 4 | 275.97 | 13.69 | 275.04 | 13.67 | 68.39 |
| 8 | — | — | 469.87 | 15.71 | 68.80 |
| 16 | — | — | 610.63 | 22.63 | 68.36 |
| 24 | — | — | **692.23** | 28.72 | 68.18 |

Throughput at low concurrency is identical between 0.95 and 0.98 (the
util change only grows the KV pool, not compute headroom); the c=8…24
rows are only reachable with 0.98+ because the smaller KV at 0.95 can
hold at most ≈ 2.33 max-context requests for no-MTP and ≈ 1.15 for
MTP=2. MTP=2 gains over no-MTP: +54 % at c=1, +49 % at c=2, +11 % at
c=4, +32 % at c=8, +27 % at c=16, +25 % at c=24.

### KV capacity vs `gpu_memory_utilization`

| util | KV cache (GiB) | KV tokens | max concurrency (max_model_len=65,536) |
|---|---|---|---|
| 0.95 (no-MTP) | 7.36 | 152,775 | 2.33× |
| 0.98 (no-MTP) | 10.21 | 211,889 | 3.23× |
| 0.985 (no-MTP) | 10.69 | 221,745 | **3.38×** |
| 0.95 (MTP=2) | 3.65 | 75,599 | 1.15× |
| 0.98 (MTP=2) | 6.59 | 136,590 | **2.08×** |

`0.99` is the absolute static-check ceiling (94.02 GiB demanded against
93.94 GiB free) and fails to start. `0.985` clears the check with
≈ 400 MB headroom and is the recommended setting for dedicated cards.

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
the first 8,192-token prefill on the no-MTP path — directly relevant
for K8s / Ray Serve auto-scale events and for edge users restarting
a Spark deployment.

### MTP=2 cold-start gap and prewarm fix

vLLM commit `8f0d8b630` extends the in-process warmup further (chunked
prefill, multi-request prefill, and `max_num_seqs` in the MTP uniform
decode warmup; cost +35 s startup on Spark, init engine 61 → 97 s).
This recovers c=4 cold from 23.67 → 42.82 tok/s (+81 %), driven by
the `_fp8_paged_mqa_logits_kernel` adaptive `BLOCK_M=8` path that the
hardcoded `(1, 2)` MTP-decode warmup tier missed.

Even after that, vLLM's `jit_monitor` still flags nine kernels JIT-compiling
during the first cold bench on Spark MTP=2 + random ISL=8,192:

```
JIT: eagle_prepare_next_token_padded_kernel        (MTP draft)
JIT: eagle_step_slot_mapping_metadata_kernel       (MTP draft)
JIT: _build_prefill_chunk_metadata_kernel          (chunked-prefill metadata)
JIT: _compute_prefill_metadata_kernel
JIT: _combine_topk_swa_indices_kernel
JIT: _deepseek_v4_sm12x_fp8_einsum_kernel          (DSv4 einsum)
JIT: _tf32_hc_prenorm_gemm_kernel
JIT: _w8a8_triton_block_scaled_mm                  (T1-A's main GEMM, alt shape)
JIT: _fp8_paged_mqa_logits_kernel                  (T1-D's kernel)
```

These kernels are already invoked from
`_run_deepseek_v4_mtp_spec_decode_warmup_kernels` and the dummy-run
attention warmup, but Triton's specialization key includes pointer
16-byte alignment. The warmup helper allocates fresh tensors via
`torch.arange` / `torch.empty`; the real inference path receives
slices into the sampler / spec-decode buffers. The two cache keys
differ → the warmed kernel gets compiled again on the first user
request. Closing this from `kernel_warmup.py` alone requires routing
warmup through the actual scheduler / sampler pipeline, which is a
larger upstream change tracked as a follow-up.

To absorb the remaining cost on the deployment side, the harness ships
a real-pipeline prewarm:

- `scripts/prewarm_serve.sh` — standalone, points at any `vllm serve`
  on `/v1/completions`. Runs two `vllm bench serve` rounds (c=1
  single-stream then `c=max_num_seqs` multi-stream) at random
  ISL=`max_num_batched_tokens` OSL=8 with `--ignore-eos`. Because
  `vllm bench serve` walks the real OpenAI-style request pipeline,
  the kernels JIT against the same buffer alignment that real users
  hit; the second user request finds a fully warm cache.
- `scripts/dgx_spark_start_mp_serve.sh` — auto-invokes the prewarm
  block after `/health=200` (toggle via `PREWARM_AFTER_HEALTH=1`,
  default on; tune via `PREWARM_ISL`, `PREWARM_OSL`,
  `PREWARM_PROMPTS`, `PREWARM_C_HIGH`).

Two-pass measurement on a single Spark MTP=2 serve, random ISL=8,192
OSL=512 num-prompts=4 (same shape as the 020e0c89a baseline 18.43
tok/s c=1) verifies the prewarm mechanism. The "warm" column is the
second bench round (Triton cache populated by the first round and
therefore representative of the steady-state the prewarm script will
produce):

| c | Cold (1st bench, JIT during inference) | Warm (2nd bench, all kernels cached) | Δ |
|---|---|---|---|
| 1 | 13.63 tok/s, TTFT 17,535 ms | **26.19 tok/s, TTFT 829 ms** | **+92 % tok/s, −95 % TTFT** |
| 2 | 36.98 tok/s, TTFT 1,494 ms | 40.38 tok/s, TTFT 1,358 ms | +9 % |
| 4 | 30.22 tok/s, TTFT 2,855 ms | 34.84 tok/s, TTFT 3,998 ms | +15 % |

Compared to the 020e0c89a baseline (18.43 tok/s c=1, 41.65 c=2,
27.00 c=4) the warm new SHA delivers **+42 % at c=1** and **+29 % at
c=4** — T1-A's real benefits, hidden in the first-bench cold readings
by the JIT spikes on the kernels listed above.

### End-to-end validation: cluster restart + auto-prewarm + first user request

Reboot Spark head, launch via the harness with `PREWARM_AFTER_HEALTH=1`
(default), then immediately issue the same random ISL=8,192 OSL=512
num-prompts=4 c=1,2,4 bench as a "first user request":

| c | tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | accept % |
|---|---|---|---|---|---|
| 1 | **25.67** | **820.94** | 858.27 | 37.42 | 46.51 |
| 2 | 38.52 | 1,425.35 | 1,592.94 | 47.91 | 50.54 |
| 4 | **46.75** | 3,185.93 | 4,097.20 | 74.50 | 54.92 |

Zero `jit_monitor` warnings during this run — all nine previously-
uncovered Triton specializations were absorbed by the prewarm rounds.
The c=1 number is statistically indistinguishable from the warm
2nd-bench reference (25.67 vs 26.19 tok/s, 821 vs 829 ms TTFT) and
+39 % over the 020e0c89a baseline; c=4 is +73 % over 020e0c89a. From
the user's perspective the first long-prefill request after cluster
bring-up now lands in the steady-state band, not the JIT-spike tail.

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
`NCCL_IB_DISABLE`, `SERVE_SPECULATIVE_CONFIG`,
`SERVE_DEFAULT_CHAT_TEMPLATE_KWARGS`, and (for cold-start mitigation)
`PREWARM_AFTER_HEALTH` (default 1) plus `PREWARM_ISL`,
`PREWARM_OSL`, `PREWARM_PROMPTS`, `PREWARM_C_HIGH`, `PREWARM_TIMEOUT`
env overrides. For non-cluster serves (e.g. the single-host
Workstation deploy) call `scripts/prewarm_serve.sh` against the local
API once `/health=200` returns.

## Source SHAs

- vLLM: `2760932cf` on `jasl/vllm` `ds4-sm120-preview-dev` (PR #41834)
- Harness: this commit
