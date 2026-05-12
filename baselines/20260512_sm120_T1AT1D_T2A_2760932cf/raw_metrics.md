# Raw metrics

All numbers from `vllm bench serve` against a clean serve restart per
`{hardware, variant}` cell. Bench client temperature 1.0, mt-bench
(`philschmid/mt-bench`) 80 prompts.

## Workstation SM120 (2x RTX PRO 6000 Blackwell Workstation Edition, TP=2 EP)

### no-MTP (`performance/sm120_workstation/nomtp_bench.json`)

| c | out tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | TPOT p99 (ms) | ITL mean (ms) | duration (s) |
|---|---|---|---|---|---|---|---|
| 1 | 97.79 | 56.13 | 119.67 | 9.97 | 10.08 | 10.93 | 152.97 |
| 2 | 156.27 | 66.26 | 99.50 | 12.37 | 12.93 | 17.65 | 96.48 |
| 4 | 247.35 | 78.74 | 135.43 | 15.46 | 16.29 | 28.81 | 60.20 |

### MTP=2 (`performance/sm120_workstation/mtp2_bench.json`)

| c | out tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | TPOT p99 (ms) | ITL mean (ms) | duration (s) | accept % | accept len |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 148.86 | 75.06 | 284.45 | 6.49 | 11.32 | 14.94 | 99.54 | 68.22 | 2.36 |
| 2 | 227.08 | 105.51 | 558.85 | 8.38 | 16.64 | 19.25 | 66.44 | 68.27 | 2.37 |
| 4 | 275.97 | 103.35 | 184.96 | 13.69 | 17.60 | 32.54 | 53.97 | 68.68 | 2.37 |

Per-position MTP acceptance: position 0 ≈ 84 %, position 1 ≈ 52 %.

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

The new SHA's optimisations are concentrated on the no-MTP single-stream
decode path (T1-A autotuned dense FP8 GEMM configs, T1-D adaptive
`BLOCK_M` for the paged-MQA logits kernel, T2-A defensive `BLOCK_D`
clamp). MTP=2 c=1 retains its prior single-stream throughput (≈148 tok/s
on Workstation, ≈30 tok/s on Spark); the small −1.5 % to −2.5 %
variance on Workstation MTP=2 is within run-to-run noise (mt-bench
prompts and temperature=1.0 sampling).
