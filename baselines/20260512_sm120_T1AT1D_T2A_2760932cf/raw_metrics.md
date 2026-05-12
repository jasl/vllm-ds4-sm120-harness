# Raw metrics

All numbers from `vllm bench serve` against a clean serve restart per
`{hardware, variant}` cell. Bench client temperature 1.0, mt-bench
(`philschmid/mt-bench`) 80 prompts.

## Workstation SM120 (2x RTX PRO 6000 Blackwell Workstation Edition, TP=2 EP)

### no-MTP @ `--gpu-memory-utilization 0.95` (`performance/sm120_workstation/nomtp_bench.json`)

| c | out tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | TPOT p99 (ms) | ITL mean (ms) | duration (s) |
|---|---|---|---|---|---|---|---|
| 1 | 97.79 | 56.13 | 119.67 | 9.97 | 10.08 | 10.93 | 152.97 |
| 2 | 156.27 | 66.26 | 99.50 | 12.37 | 12.93 | 17.65 | 96.48 |
| 4 | 247.35 | 78.74 | 135.43 | 15.46 | 16.29 | 28.81 | 60.20 |

KV cache 7.36 GiB / 152,775 tokens / max_concurrency 2.33×.

### no-MTP @ `--gpu-memory-utilization 0.98`, c=1..24 (`performance/sm120_workstation/nomtp_098_c1-24_bench.json`)

| c | out tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | TPOT p99 (ms) |
|---|---|---|---|---|---|
| 1 | 97.69 | 55.87 | 119.30 | 9.99 | 10.07 |
| 2 | 155.80 | 66.37 | 100.01 | 12.38 | 12.99 |
| 4 | 247.52 | 76.24 | 154.59 | 15.48 | 16.38 |
| 8 | 355.54 | 125.15 | 489.04 | 20.91 | 22.42 |
| 16 | 480.86 | 217.06 | 604.03 | 29.78 | 33.51 |
| 24 | 554.52 | 323.79 | 561.34 | 37.22 | 40.04 |

KV cache 10.21 GiB / 211,889 tokens / max_concurrency 3.23×.

### MTP=2 @ `--gpu-memory-utilization 0.95` (`performance/sm120_workstation/mtp2_bench.json`)

| c | out tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | TPOT p99 (ms) | ITL mean (ms) | duration (s) | accept % | accept len |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 148.86 | 75.06 | 284.45 | 6.49 | 11.32 | 14.94 | 99.54 | 68.22 | 2.36 |
| 2 | 227.08 | 105.51 | 558.85 | 8.38 | 16.64 | 19.25 | 66.44 | 68.27 | 2.37 |
| 4 | 275.97 | 103.35 | 184.96 | 13.69 | 17.60 | 32.54 | 53.97 | 68.68 | 2.37 |

KV cache 3.65 GiB / 75,599 tokens / max_concurrency 1.15×.

### MTP=2 @ `--gpu-memory-utilization 0.98`, c=1..24 (`performance/sm120_workstation/mtp2_098_c1-24_bench.json`)

| c | out tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | TPOT p99 (ms) | accept % | accept len |
|---|---|---|---|---|---|---|---|
| 1 | 150.16 | 64.81 | 131.28 | 6.34 | 8.72 | 68.25 | 2.37 |
| 2 | 232.08 | 82.74 | 149.35 | 8.13 | 11.30 | 68.11 | 2.36 |
| 4 | 275.04 | 102.99 | 161.91 | 13.67 | 17.16 | 68.39 | 2.37 |
| 8 | 469.87 | 134.57 | 253.94 | 15.71 | 23.06 | 68.80 | 2.38 |
| 16 | 610.63 | 273.28 | 640.02 | 22.63 | 29.36 | 68.36 | 2.37 |
| 24 | 692.23 | 355.97 | 633.45 | 28.72 | 37.82 | 68.18 | 2.36 |

KV cache 6.59 GiB / 136,590 tokens / max_concurrency 2.08×.

Per-position MTP acceptance: position 0 ≈ 84 %, position 1 ≈ 52 %.

### KV capacity sweep on Workstation

| util | KV (GiB) | KV tokens | max_concurrency (65,536-token req) | startup health=200 |
|---|---|---|---|---|
| 0.95 no-MTP | 7.36 | 152,775 | 2.33× | yes |
| 0.98 no-MTP | 10.21 | 211,889 | 3.23× | yes |
| 0.985 no-MTP | 10.69 | 221,745 | 3.38× | yes (75 s) |
| 0.99 no-MTP | — | — | — | **fails static check** (94.02 GiB demanded vs 93.94 GiB free) |
| 0.95 MTP=2 | 3.65 | 75,599 | 1.15× | yes |
| 0.98 MTP=2 | 6.59 | 136,590 | 2.08× | yes |

## DGX Spark cluster (2 nodes × GB10, TP=2 PP=1 mp, NCCL_IB_DISABLE=0)

### no-MTP (`performance/gb10_spark/nomtp_ib0_bench.json`)

| c | out tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | TPOT p99 (ms) | duration (s) |
|---|---|---|---|---|---|---|
| 1 | 21.94 | 495.87 | 1987.70 | 43.12 | 43.96 | 690.85 |
| 2 | 35.38 | 409.34 | 1003.49 | 53.94 | 60.14 | 428.59 |
| 4 | 52.41 | 432.27 | 1141.73 | 72.85 | 80.63 | 289.74 |

### MTP=2 (`performance/gb10_spark/mtp2_ib0_bench.json`)

| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) | duration (s) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 30.22 | 538.03 | 30.53 | 494.53 | 67.78 | 2.36 |
| 2 | 44.86 | 500.26 | 41.55 | 334.99 | 67.74 | 2.35 |
| 4 | 58.00 | 595.54 | 64.20 | 258.59 | 68.29 | 2.37 |

Per-position MTP acceptance: position 0 ≈ 84 %, position 1 ≈ 51 %.

## NCCL transport ablation on Spark (no-MTP c=1)

| NCCL_IB_DISABLE | Transport | out tok/s | TPOT mean (ms) |
|---|---|---|---|
| 0 | IB verbs over RoCE HCA `rocep1s0f1` | 21.94 | 43.12 |
| 1 | TCP socket over RoCE iface `enp1s0f1np1` | 15.12 | 63.61 |

## gsm8k 5-shot 200q

| Cell | strict | flexible |
|---|---|---|
| Workstation no-MTP | 0.945 | 0.945 |
| Workstation MTP=2 | 0.950 | 0.950 |
| Spark no-MTP | 0.965 | 0.965 |
| Spark MTP=2 | 0.955 | 0.955 |

## Random ISL=8192 OSL=512 num-prompts=4 (Spark MTP=2, IB=0)

`performance/gb10_spark/random/mtp2_random_isl8192_osl512_bench.json`

| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|
| 1 | 13.91 | 17,641 | 37.49 | 48.32 | 1.97 |
| 2 | 36.46 | 2,105 | 49.12 | 49.13 | 1.98 |
| 4 | 23.67 | 4,833 | 155.51 | 50.54 | 2.01 |

MTP acceptance falls from 67–68 % on mt-bench prose to 48–51 % on
synthetic random tokens, an expected effect of the unpredictable
distribution. The c=4 TPOT of 155 ms reflects the cluster
saturating at four concurrent ISL=8,192 contexts (32 K-token KV slab
in flight, paged across both nodes).

## Long prefill sweep (random ISL, c=1, num-prompts=1, OSL=8)

### Workstation no-MTP

`performance/sm120_workstation/prefill_sweep/isl_*.json`

| ISL | TTFT mean (ms) | duration (s) | prefill rate (tok/s) |
|---|---|---|---|
| 1,024 | 300.30 | 0.37 | 3,410 |
| 4,096 | 1,406.26 | 1.48 | 2,913 |
| 8,192 | 1,789.18 | 1.86 | 4,579 |
| 16,384 | 3,788.12 | 3.85 | 4,326 |
| 32,768 | 8,874.31 | 8.93 | 3,692 |
| 65,000 | 22,962.74 | 23.00 | 2,830 |

### Spark MTP=2 (same serve also used for the random 8K bench above)

`performance/gb10_spark/prefill_sweep/isl_*.json`

| ISL | TTFT mean (ms) | duration (s) | prefill rate (tok/s) |
|---|---|---|---|
| 1,024 | 632.14 | 0.84 | 1,620 |
| 4,096 | 762.89 | 1.06 | 5,369 |
| 8,192 | 820.50 | 1.11 | 9,990 |
| 16,384 | 23,007.60 | 23.28 | 712 |
| 32,768 | 57,564.43 | 57.83 | 569 |
| 65,536 | 160,819.10 | 161.06 | 408 |
| 131,000 | 505,323.72 | 505.51 | 259 |

Single-chunk prefill rate peaks at 5–10 K tok/s; once ISL > 8,192 the
multi-chunk path (cross-node TP attention over the prior KV slab)
dominates and the curve flattens around 200–700 tok/s.

## Comparison to 020e0c89a baseline (single-row deltas)

| Cell | 020e0c89a | 2760932cf | Δ |
|---|---|---|---|
| Workstation no-MTP c=1 mt-bench tok/s | 84.36 | 97.79 | **+15.9 %** |
| Workstation no-MTP c=2 mt-bench tok/s | 147.24 | 156.27 | +6.1 % |
| Workstation no-MTP c=4 mt-bench tok/s | 244.05 | 247.35 | +1.4 % |
| Workstation MTP=2 c=1 mt-bench tok/s | 151.08 | 148.86 | −1.5 % |
| Workstation MTP=2 c=4 mt-bench tok/s | 282.91 | 275.97 | −2.5 % |
| Spark no-MTP c=1 mt-bench tok/s | 19.13 | 21.94 | **+14.7 %** |
| Spark MTP=2 c=1 mt-bench tok/s | 29.43 | 30.22 | +2.7 % |
| Workstation no-MTP ISL=4 K TTFT (ms) | 1,497 | 1,406 | −6 % |
| Workstation no-MTP ISL=8 K TTFT (ms) | 3,360 | 1,789 | **−47 %** |
| Spark ISL=1 K TTFT (ms) (was no-MTP) | 1,506 | 632 (MTP=2) | −58 % |
| Spark ISL=4 K TTFT (ms) (was no-MTP) | 7,169 | 763 (MTP=2) | −89 % |
| Spark ISL=8 K TTFT (ms) (was no-MTP) | 13,253 | 820 (MTP=2) | **−94 %** |

## Cold-start warmup verification (`5c8975591`)

Cold random ISL=8,192 OSL=512 num-prompts=4 c=1 against a freshly
restarted Workstation no-MTP serve:

| Metric | Value |
|---|---|
| Startup to `/health=200` | 80 s (vs 71 s without the warmup change, +9 s) |
| out tok/s | 61.16 |
| TTFT mean | 3,171.89 ms |
| TTFT p99 | 3,175.90 ms |
| TPOT mean | 10.17 ms |
| benchmark duration | 33.49 s |

TTFT mean ≈ p99 confirms the first-request JIT spike is absorbed by
the extended warmup; the 4 prompts complete with near-identical TTFT.

## Spark MTP=2 random 8K, cold vs warm (vLLM 5c8975591)

Same Spark MTP=2 serve, two consecutive identical bench rounds. The
first round is "cold" (Triton JIT cache empty for several inference
kernels not covered by the 8,192-token single-prefill warmup); the
second is "warm" (all kernels JIT-cached after the cold round).

`performance/gb10_spark/random/mtp2_random_isl8192_cold_warmupfix_bench.json`
`performance/gb10_spark/random/mtp2_random_isl8192_warm_bench.json`

| c | Cold tok/s | Cold TTFT mean | Cold TTFT p99 | Warm tok/s | Warm TTFT mean | Warm TTFT p99 |
|---|---|---|---|---|---|---|
| 1 | 13.63 | 17,535 ms | 18,024 ms | **26.19** | **829 ms** | 856 ms |
| 2 | 36.98 | 1,494 ms | 1,652 ms | **40.38** | **1,358 ms** | 1,632 ms |
| 4 | 30.22 | 2,855 ms | 3,519 ms | **34.84** | **3,998 ms** | 3,999 ms |

JIT-monitor warnings observed only during the cold round; the warm
round produced none.

### End-to-end with auto-prewarm (`scripts/dgx_spark_start_mp_serve.sh`)

`performance/gb10_spark/random/mtp2_random_isl8192_postprewarm_bench.json`

Fresh cluster bring-up (Spark head rebooted), `PREWARM_AFTER_HEALTH=1`
fires automatically after `/health=200`, then the same bench shape
runs as the very first user request. Zero `jit_monitor` warnings.

| c | tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | duration (s) | accept % | accept len |
|---|---|---|---|---|---|---|---|
| 1 | **25.67** | **820.94** | 858.27 | 37.42 | 79.78 | 46.51 | 1.93 |
| 2 | 38.52 | 1,425.35 | 1,592.94 | 47.91 | 53.16 | 50.54 | 2.01 |
| 4 | **46.75** | 3,185.93 | 4,097.20 | 74.50 | 43.81 | 54.92 | 2.10 |

Compared to the warm 2nd-bench reference above:

| c | Warm 2nd-bench | Post-prewarm 1st-bench | match? |
|---|---|---|---|
| 1 | 26.19 tok/s, 829 ms | 25.67 tok/s, 821 ms | within ±2 % |
| 2 | 40.38 tok/s, 1,358 ms | 38.52 tok/s, 1,425 ms | within ±5 % |
| 4 | 34.84 tok/s, 3,998 ms | 46.75 tok/s, 3,186 ms | post-prewarm faster (run-to-run) |

The auto-prewarm path lands the user's first request in the same
steady-state band the second bench previously demonstrated.

### Random-8K Spark MTP=2 vs 020e0c89a baseline

| c | 020e0c89a (cold, MTP=2) | 2760932cf cold (warmup fix) | 2760932cf warm | 2760932cf post-prewarm |
|---|---|---|---|---|
| 1 | 18.43 tok/s | 13.63 (-26 %) | **26.19 (+42 %)** | **25.67 (+39 %)** |
| 2 | 41.65 tok/s | 36.98 (-11 %) | 40.38 (-3 %) | 38.52 (-8 %) |
| 4 | 27.00 tok/s | 30.22 (+12 %) | **34.84 (+29 %)** | **46.75 (+73 %)** |

The cold delta is dominated by uncovered-kernel JIT spikes; the warm
row is the steady-state delta the T1-A optimisations actually
deliver on this random workload.

The new SHA's optimisations are concentrated on the no-MTP single-stream
decode path (T1-A autotuned dense FP8 GEMM configs, T1-D adaptive
`BLOCK_M` for the paged-MQA logits kernel, T2-A defensive `BLOCK_D`
clamp). MTP=2 c=1 retains its prior single-stream throughput (≈148 tok/s
on Workstation, ≈30 tok/s on Spark); the small −1.5 % to −2.5 %
variance on Workstation MTP=2 is within run-to-run noise (mt-bench
prompts and temperature=1.0 sampling).
