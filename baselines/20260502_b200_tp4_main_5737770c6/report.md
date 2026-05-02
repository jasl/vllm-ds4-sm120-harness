# B200 TP=4 vLLM Main DeepSeek V4 Flash Baseline

- Label: `b200_tp4_main_5737770c6`
- Artifact generated at UTC: `2026-05-02T08:04:27.682118+00:00`
- Primary artifact: `artifacts/main/4x_nvidia_b200/b200_tp4_main_5737770c6/20260502064850`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Branch: `main`
- GPU: 4x NVIDIA B200 (179.1 GiB each)
- Dataset: `hf` / `philschmid/mt-bench`

## Run Health

- vLLM collect_env: 10/10 phase captures exited 0
- Server unresponsive markers: none

## Provenance

| Field | Value |
| --- | --- |
| vLLM | `0.20.1rc1.dev144+g5737770c6` |
| vLLM git sha | `5737770c6` |
| vLLM CUDA archs | `Not Set` |
| PyTorch | `2.11.0+cu130` |
| PyTorch CUDA build | `13.0` |
| CUDA runtime | `13.0.88` |
| NVIDIA driver | `595.58.03` |
| Transformers | `5.7.0` |
| Triton | `3.6.0` |

## Serve Shape

| Variant | KV dtype | Block size | Max model len | TP | Max seqs | Max batched tokens | GPU memory util | Speculative config | MoE backend | Async scheduling | Enforce eager | Reasoning parser | Tokenizer mode | Tool parser | Auto tool | FP4 index cache | FlashInfer autotune disabled |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `nomtp` | `fp8` | 256 | 393216 | 4 | n/a | n/a | n/a | `n/a` | `n/a` | no | no | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | yes | yes |
| `mtp` | `fp8` | 256 | 393216 | 4 | n/a | n/a | n/a | `{"method":"mtp","num_speculative_tokens":2}` | `n/a` | no | no | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | yes | yes |

## Quick Performance Summary

### Real Scenario OP Cost Estimate

These rows use translation, writing, coding, and ToolCall-15 wall-clock samples. They are request-style operation estimates, not benchmark throughput prices.

#### Purchase / Amortized

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | translation | 90 | 100.00 | 5.49 | 138.71 | 809 | 762 | $0.0103 | $10.26 | $12.67 | $13.47 | $2.53 | $6.72 |
| `nomtp` | writing | 90 | 100.00 | 9.85 | 140.48 | 167 | 1383 | $0.0184 | $18.39 | $110.27 | $13.30 | $22.05 | $6.72 |
| `nomtp` | coding | 90 | 100.00 | 28.95 | 139.38 | 252 | 4035 | $0.0541 | $54.08 | $215.02 | $13.40 | $43.00 | $6.72 |
| `nomtp` | agentic | 135 | 86.67 | 1.49 | 124.68 | 3152 | 186 | $0.0028 | $2.79 | $0.88 | $14.98 | $0.18 | $6.72 |
| `nomtp` | reading_summary | 45 | 100.00 | 4.65 | 136.45 | 1699 | 635 | $0.0087 | $8.69 | $5.12 | $13.69 | $1.02 | $6.72 |
| `mtp` | translation | 90 | 100.00 | 3.31 | 226.47 | 809 | 749 | $0.0062 | $6.18 | $7.64 | $8.25 | $1.53 | $6.73 |
| `mtp` | writing | 90 | 100.00 | 6.90 | 204.20 | 167 | 1409 | $0.0129 | $12.90 | $77.35 | $9.15 | $15.47 | $6.73 |
| `mtp` | coding | 90 | 100.00 | 14.63 | 273.21 | 252 | 3996 | $0.0273 | $27.34 | $108.71 | $6.84 | $21.74 | $6.73 |
| `mtp` | agentic | 135 | 80.00 | 0.82 | 219.38 | 3150 | 179 | $0.0015 | $1.53 | $0.49 | $8.52 | $0.10 | $6.73 |
| `mtp` | reading_summary | 45 | 100.00 | 2.78 | 220.80 | 1699 | 615 | $0.0052 | $5.20 | $3.06 | $8.47 | $0.61 | $6.73 |

#### Rental / Cloud GPU-Hour

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | translation | 90 | 100.00 | 5.49 | 138.71 | 809 | 762 | $0.0232 | $23.19 | $28.65 | $30.44 | $5.73 | $15.20 |
| `nomtp` | writing | 90 | 100.00 | 9.85 | 140.48 | 167 | 1383 | $0.0416 | $41.58 | $249.26 | $30.06 | $49.85 | $15.20 |
| `nomtp` | coding | 90 | 100.00 | 28.95 | 139.38 | 252 | 4035 | $0.1222 | $122.24 | $486.04 | $30.29 | $97.21 | $15.20 |
| `nomtp` | agentic | 135 | 86.67 | 1.49 | 124.68 | 3152 | 186 | $0.0063 | $6.30 | $2.00 | $33.86 | $0.40 | $15.20 |
| `nomtp` | reading_summary | 45 | 100.00 | 4.65 | 136.45 | 1699 | 635 | $0.0196 | $19.64 | $11.56 | $30.94 | $2.31 | $15.20 |
| `mtp` | translation | 90 | 100.00 | 3.31 | 226.47 | 809 | 749 | $0.0140 | $13.97 | $17.26 | $18.64 | $3.45 | $15.20 |
| `mtp` | writing | 90 | 100.00 | 6.90 | 204.20 | 167 | 1409 | $0.0291 | $29.14 | $174.72 | $20.68 | $34.94 | $15.20 |
| `mtp` | coding | 90 | 100.00 | 14.63 | 273.21 | 252 | 3996 | $0.0618 | $61.76 | $245.55 | $15.45 | $49.11 | $15.20 |
| `mtp` | agentic | 135 | 80.00 | 0.82 | 219.38 | 3150 | 179 | $0.0035 | $3.45 | $1.10 | $19.25 | $0.22 | $15.20 |
| `mtp` | reading_summary | 45 | 100.00 | 2.78 | 220.80 | 1699 | 615 | $0.0118 | $11.75 | $6.92 | $19.12 | $1.38 | $15.20 |

### Reference Cost Model

- Hardware prices: B200: `$30,000/GPU`; RTX PRO 6000: `$8,565/GPU`; RTX 5090: `$1,999/GPU`; DGX Spark / GB10: `$3,999/GPU`.
- Rental prices: B200: `$3.80/GPU-hour`; RTX PRO 6000 WS: `$0.96/GPU-hour`; DGX Spark / GB10: `$0.48/unit-hour`.
- Amortization: 3 years at 70% useful utilization.
- Power: sampled average GPU power multiplied by PUE 1.25 and $0.12/kWh.
- Purchase cost/h adds amortized hardware and power; rental cost/h uses the quoted rental rate without adding separate power.
- Cache read price is a synthetic 20% of the input break-even price.
- Input and output prices each allocate the full hourly cost to that token class; do not add them together.

### Best Benchmark Throughput

| Source | Variant | Phase | C | Output tok/s | tok/s/GPU | Mean TTFT ms | Mean TPOT ms |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Primary | `nomtp` | HF/MT-Bench | 16 | 1138.36 | 284.59 | 139.63 | 12.22 |
| Primary | `nomtp` | Random 8192/512 | 2 | 252.98 | 63.24 | 185.06 | 7.55 |
| Primary | `mtp` | HF/MT-Bench | 24 | 1786.78 | 446.69 | 244.26 | 11.29 |
| Primary | `mtp` | Random 8192/512 | 2 | 220.18 | 55.05 | 170.94 | 7.95 |

### Runtime Prefill/Decode Averages

These are phase-local averages parsed from vLLM server logs.

| Source | Variant | Phase | Prefill avg tok/s | Decode avg tok/s | Prefill tokens | Decode tokens | Max running |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Primary | `nomtp` | HF/MT-Bench | 91.63 | 272.85 | 33210 | 89998 | 24 |
| Primary | `nomtp` | Random 8192/512 | 958.09 | 92.61 | 131072 | 7680 | 2 |
| Primary | `mtp` | HF/MT-Bench | 124.08 | 340.38 | 33210 | 86658 | 24 |
| Primary | `mtp` | Random 8192/512 | 844.62 | 96.85 | 131072 | 8192 | 2 |

## Phase Exit Codes

| Variant | Phase | Exit | Artifact |
| --- | --- | ---: | --- |
| `nomtp` | `server_startup` | 0 | `nomtp/server_startup` |
| `nomtp` | `acceptance` | 1 | `nomtp/acceptance` |
| `nomtp` | `bench_hf_mt_bench` | 0 | `nomtp/bench_hf_mt_bench` |
| `nomtp` | `eval_gsm8k` | 0 | `nomtp/eval_gsm8k` |
| `nomtp` | `bench_random_8192x512` | 0 | `nomtp/bench_random_8192x512` |
| `nomtp` | `oracle_export` | 0 | `nomtp/oracle_export` |
| `mtp` | `server_startup` | 0 | `mtp/server_startup` |
| `mtp` | `acceptance` | 1 | `mtp/acceptance` |
| `mtp` | `bench_hf_mt_bench` | 0 | `mtp/bench_hf_mt_bench` |
| `mtp` | `eval_gsm8k` | 0 | `mtp/eval_gsm8k` |
| `mtp` | `bench_random_8192x512` | 0 | `mtp/bench_random_8192x512` |
| `mtp` | `oracle_export` | 0 | `mtp/oracle_export` |

## Acceptance Gates

| Variant | Gate | Exit |
| --- | --- | ---: |
| `nomtp` | `compileall` | 0 |
| `nomtp` | `generation` | 0 |
| `nomtp` | `health` | 0 |
| `nomtp` | `pytest` | 0 |
| `nomtp` | `ruff` | 0 |
| `nomtp` | `smoke_quick` | 0 |
| `nomtp` | `toolcall15` | 1 |
| `nomtp` | `vllm_collect_env` | 0 |
| `mtp` | `compileall` | 0 |
| `mtp` | `generation` | 0 |
| `mtp` | `health` | 0 |
| `mtp` | `pytest` | 0 |
| `mtp` | `ruff` | 0 |
| `mtp` | `smoke_quick` | 0 |
| `mtp` | `toolcall15` | 1 |
| `mtp` | `vllm_collect_env` | 0 |

## Benchmark Throughput

| Variant | Phase | C | Requests | Req/s | Output tok/s | Avg GPU util % | Max power/GPU W |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 0.72 | 135.66 | 75.63 | 471.85 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 1.32 | 246.41 | 75.63 | 471.85 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 2.28 | 431.34 | 75.63 | 471.85 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 3.77 | 702.09 | 75.63 | 471.85 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 6.18 | 1138.36 | 75.63 | 471.85 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 4.16 | 792.10 | 75.63 | 471.85 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 0.25 | 129.54 | 70.58 | 415.46 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 0.49 | 252.98 | 70.58 | 415.46 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 1.17 | 220.92 | 65.92 | 475.70 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 2.01 | 362.31 | 65.92 | 475.70 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 3.32 | 619.00 | 65.92 | 475.70 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 5.29 | 975.72 | 65.92 | 475.70 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 7.84 | 1444.72 | 65.92 | 475.70 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 9.83 | 1786.78 | 65.92 | 475.70 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 0.21 | 109.05 | 73.61 | 428.19 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 0.43 | 220.18 | 73.61 | 428.19 |

## Normalized Efficiency

Power efficiency uses sampled average GPU power for the whole phase. It is GPU-side power, not wall-plug power.

| Variant | Phase | C | Requests | Output tok/s | tok/s/GPU | tok/s/total GiB | tok/s/used GiB | tok/J | tok/s/kW |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 135.66 | 33.91 | 0.19 | 0.21 | 0.11 | 106.36 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 246.41 | 61.60 | 0.34 | 0.37 | 0.19 | 193.18 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 431.34 | 107.83 | 0.60 | 0.65 | 0.34 | 338.17 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 702.09 | 175.52 | 0.98 | 1.06 | 0.55 | 550.43 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 1138.36 | 284.59 | 1.59 | 1.72 | 0.89 | 892.46 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 792.10 | 198.03 | 1.11 | 1.20 | 0.62 | 621.00 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 129.54 | 32.38 | 0.18 | 0.19 | 0.11 | 106.15 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 252.98 | 63.24 | 0.35 | 0.38 | 0.21 | 207.30 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 220.92 | 55.23 | 0.31 | 0.33 | 0.17 | 172.99 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 362.31 | 90.58 | 0.51 | 0.55 | 0.28 | 283.70 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 619.00 | 154.75 | 0.86 | 0.94 | 0.48 | 484.69 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 975.72 | 243.93 | 1.36 | 1.47 | 0.76 | 764.01 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 1444.72 | 361.18 | 2.02 | 2.18 | 1.13 | 1131.25 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 1786.78 | 446.69 | 2.49 | 2.70 | 1.40 | 1399.09 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 109.05 | 27.26 | 0.15 | 0.16 | 0.09 | 85.26 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 220.18 | 55.05 | 0.31 | 0.33 | 0.17 | 172.15 |

## Benchmark Latency

| Variant | Phase | C | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |
| --- | --- | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 73.23 | 7.02 | 7.02 |
| `nomtp` | HF/MT-Bench | 2 | 82.63 | 7.66 | 7.61 |
| `nomtp` | HF/MT-Bench | 4 | 86.05 | 8.65 | 8.61 |
| `nomtp` | HF/MT-Bench | 8 | 106.35 | 10.25 | 10.24 |
| `nomtp` | HF/MT-Bench | 16 | 139.63 | 12.22 | 12.28 |
| `nomtp` | HF/MT-Bench | 24 | 982.80 | 23.24 | 23.16 |
| `nomtp` | Random 8192/512 | 1 | 271.94 | 7.20 | 7.20 |
| `nomtp` | Random 8192/512 | 2 | 185.06 | 7.55 | 7.56 |
| `mtp` | HF/MT-Bench | 1 | 79.57 | 4.06 | 9.32 |
| `mtp` | HF/MT-Bench | 2 | 131.64 | 7.00 | 10.77 |
| `mtp` | HF/MT-Bench | 4 | 107.83 | 6.00 | 12.99 |
| `mtp` | HF/MT-Bench | 8 | 141.47 | 7.38 | 16.09 |
| `mtp` | HF/MT-Bench | 16 | 199.83 | 9.72 | 20.87 |
| `mtp` | HF/MT-Bench | 24 | 244.26 | 11.29 | 24.30 |
| `mtp` | Random 8192/512 | 1 | 269.05 | 8.66 | 9.32 |
| `mtp` | Random 8192/512 | 2 | 170.94 | 7.95 | 9.53 |

## ToolCall-15

| Variant | Score | Total runs | Unique cases | Failures |
| --- | ---: | ---: | ---: | ---: |
| `nomtp` | 243/270 (90%) | 135 | 45 | 18 |
| `mtp` | 225/270 (83%) | 135 | 45 | 27 |

### `nomtp` Failures

- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.

### `mtp` Failures

- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.

## Oracle Export

| Variant | Cases | Success | Model |
| --- | ---: | ---: | --- |
| `nomtp` | 5 | 5 | `deepseek-ai/DeepSeek-V4-Flash` |
| `mtp` | 5 | 5 | `deepseek-ai/DeepSeek-V4-Flash` |

## Accuracy Evals

These rows are optional public accuracy gates, intended for expensive reference captures and branch-promotion checks.

| Variant | Task | Version | OK | Fewshot | Concurrent | Max gen toks | EM flexible % | EM strict % | EM flex stderr |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | GSM8K | 3.0 | yes | 8 | 4 | 2048 | 94.77 | 94.84 | 0.0061 |
| `mtp` | GSM8K | 3.0 | yes | 8 | 1 | 2048 | 95.15 | 95.22 | 0.0059 |

## Runtime Stats

| Variant | Phase | Prefill delta | Decode delta | Successful delta | Max running | Log prefill tok/s | Log decode tok/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 33210 | 89998 | 480 | 24 | 91.63 | 272.85 |
| `nomtp` | Random 8192/512 | 131072 | 7680 | 14 | 2 | 958.09 | 92.61 |
| `mtp` | HF/MT-Bench | 33210 | 86658 | 459 | 24 | 124.08 | 340.38 |
| `mtp` | Random 8192/512 | 131072 | 8192 | 16 | 2 | 844.62 | 96.85 |

## MTP Speculative Decoding

| Variant | Phase | Samples | Mean acceptance length | Avg draft acceptance % | Per-position acceptance | Accepted tokens | Drafted tokens |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| `mtp` | HF/MT-Bench | 23 | 2.26 | 62.87 | `[0.789, 0.468]` | 43818 | 68754 |
| `mtp` | Random 8192/512 | 7 | 1.12 | 6.03 | `[0.088, 0.032]` | 966 | 13544 |

## Notes

- `tok/s/GPU` divides output token throughput by detected GPU count.
- `tok/s/total GiB` divides output token throughput by installed GPU VRAM.
- `tok/s/used GiB` divides output token throughput by sampled peak used GPU VRAM.
- `tok/J` and `tok/s/kW` use sampled average GPU power for the phase.
- Benchmark power and VRAM denominators are phase-level samples, not per-concurrency samples.
- Quick runtime prefill/decode averages use supplement rows when a supplement artifact is provided.
