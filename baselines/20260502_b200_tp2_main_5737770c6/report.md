# B200 TP=2 vLLM Main DeepSeek V4 Flash Baseline

- Label: `b200_tp2_main_5737770c6`
- Artifact generated at UTC: `2026-05-02T06:28:29.545946+00:00`
- Primary artifact: `artifacts/main/4x_nvidia_b200/b200_tp2_main_5737770c6/20260502045726`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Branch: `main`
- GPU: 2x NVIDIA B200 (179.1 GiB each)
- Dataset: `hf` / `philschmid/mt-bench`

## Run Health

- vLLM collect_env: 12/12 phase captures exited 0
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
| `nomtp` | `fp8` | 256 | 393216 | 2 | n/a | n/a | n/a | `n/a` | `n/a` | no | no | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | yes | yes |
| `mtp` | `fp8` | 256 | 393216 | 2 | n/a | n/a | n/a | `{"method":"mtp","num_speculative_tokens":2}` | `n/a` | no | no | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | yes | yes |

## Quick Performance Summary

### Real Scenario OP Cost Estimate

These rows use translation, writing, coding, and ToolCall-15 wall-clock samples. They are request-style operation estimates, not benchmark throughput prices.

#### Purchase / Amortized

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | translation | 90 | 100.00 | 6.54 | 114.16 | 809 | 747 | $0.0061 | $6.15 | $7.60 | $8.23 | $1.52 | $3.38 |
| `nomtp` | writing | 90 | 100.00 | 12.16 | 112.94 | 167 | 1374 | $0.0114 | $11.43 | $68.52 | $8.32 | $13.70 | $3.38 |
| `nomtp` | coding | 90 | 100.00 | 34.86 | 114.70 | 252 | 3999 | $0.0328 | $32.76 | $130.25 | $8.19 | $26.05 | $3.38 |
| `nomtp` | agentic | 135 | 80.00 | 1.70 | 107.84 | 3154 | 184 | $0.0016 | $1.60 | $0.51 | $8.71 | $0.10 | $3.38 |
| `nomtp` | reading_summary | 45 | 100.00 | 5.66 | 110.07 | 1699 | 623 | $0.0053 | $5.32 | $3.13 | $8.54 | $0.63 | $3.38 |
| `mtp` | translation | 90 | 100.00 | 3.34 | 228.27 | 809 | 762 | $0.0031 | $3.14 | $3.87 | $4.12 | $0.77 | $3.38 |
| `mtp` | writing | 90 | 100.00 | 6.58 | 205.23 | 167 | 1349 | $0.0062 | $6.18 | $37.03 | $4.58 | $7.41 | $3.38 |
| `mtp` | coding | 90 | 100.00 | 14.76 | 271.88 | 252 | 4013 | $0.0139 | $13.87 | $55.13 | $3.46 | $11.03 | $3.38 |
| `mtp` | agentic | 135 | 80.00 | 0.81 | 218.57 | 3148 | 177 | $0.0008 | $0.76 | $0.24 | $4.30 | $0.05 | $3.38 |
| `mtp` | reading_summary | 45 | 100.00 | 2.85 | 218.76 | 1699 | 623 | $0.0027 | $2.67 | $1.57 | $4.29 | $0.31 | $3.38 |

#### Rental / Cloud GPU-Hour

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | translation | 90 | 100.00 | 6.54 | 114.16 | 809 | 747 | $0.0138 | $13.82 | $17.07 | $18.49 | $3.41 | $7.60 |
| `nomtp` | writing | 90 | 100.00 | 12.16 | 112.94 | 167 | 1374 | $0.0257 | $25.68 | $153.97 | $18.69 | $30.79 | $7.60 |
| `nomtp` | coding | 90 | 100.00 | 34.86 | 114.70 | 252 | 3999 | $0.0736 | $73.60 | $292.66 | $18.41 | $58.53 | $7.60 |
| `nomtp` | agentic | 135 | 80.00 | 1.70 | 107.84 | 3154 | 184 | $0.0036 | $3.60 | $1.14 | $19.58 | $0.23 | $7.60 |
| `nomtp` | reading_summary | 45 | 100.00 | 5.66 | 110.07 | 1699 | 623 | $0.0119 | $11.95 | $7.03 | $19.18 | $1.41 | $7.60 |
| `mtp` | translation | 90 | 100.00 | 3.34 | 228.27 | 809 | 762 | $0.0070 | $7.05 | $8.71 | $9.25 | $1.74 | $7.60 |
| `mtp` | writing | 90 | 100.00 | 6.58 | 205.23 | 167 | 1349 | $0.0139 | $13.88 | $83.22 | $10.29 | $16.64 | $7.60 |
| `mtp` | coding | 90 | 100.00 | 14.76 | 271.88 | 252 | 4013 | $0.0312 | $31.16 | $123.89 | $7.76 | $24.78 | $7.60 |
| `mtp` | agentic | 135 | 80.00 | 0.81 | 218.57 | 3148 | 177 | $0.0017 | $1.71 | $0.54 | $9.66 | $0.11 | $7.60 |
| `mtp` | reading_summary | 45 | 100.00 | 2.85 | 218.76 | 1699 | 623 | $0.0060 | $6.01 | $3.54 | $9.65 | $0.71 | $7.60 |

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
| Primary | `nomtp` | HF/MT-Bench | 24 | 1130.50 | 565.25 | 197.29 | 17.96 |
| Primary | `nomtp` | Random 8192/512 | 2 | 214.54 | 107.27 | 318.66 | 8.72 |
| Primary | `mtp` | HF/MT-Bench | 24 | 1690.53 | 845.26 | 214.00 | 11.33 |
| Primary | `mtp` | Random 8192/512 | 2 | 195.55 | 97.78 | 183.95 | 9.46 |

### Runtime Prefill/Decode Averages

These are phase-local averages parsed from vLLM server logs.

| Source | Variant | Phase | Prefill avg tok/s | Decode avg tok/s | Prefill tokens | Decode tokens | Max running |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Primary | `nomtp` | HF/MT-Bench | 91.51 | 350.06 | 45080 | 126050 | 25 |
| Primary | `nomtp` | Random 8192/512 | 856.23 | 215.69 | 131651 | 15643 | 3 |
| Primary | `mtp` | HF/MT-Bench | 126.93 | 338.36 | 33210 | 87088 | 24 |
| Primary | `mtp` | Random 8192/512 | 844.66 | 92.54 | 131072 | 7840 | 2 |

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
| `nomtp` | `long_context_probe` | 0 | `nomtp/long_context_probe` |
| `mtp` | `long_context_probe` | 0 | `mtp/long_context_probe` |

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
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 0.64 | 117.40 | 96.82 | 594.27 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 1.14 | 209.16 | 96.82 | 594.27 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 1.94 | 361.55 | 96.82 | 594.27 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 3.04 | 560.53 | 96.82 | 594.27 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 4.96 | 938.97 | 96.82 | 594.27 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 6.18 | 1130.50 | 96.82 | 594.27 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 0.22 | 114.27 | 99.91 | 503.14 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 0.42 | 214.54 | 99.91 | 503.14 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 1.22 | 226.76 | 67.26 | 587.98 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 2.05 | 377.75 | 67.26 | 587.98 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 3.09 | 568.62 | 67.26 | 587.98 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 4.99 | 921.82 | 67.26 | 587.98 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 7.27 | 1383.56 | 67.26 | 587.98 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 9.17 | 1690.53 | 67.26 | 587.98 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 0.21 | 109.02 | 72.87 | 499.17 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 0.38 | 195.55 | 72.87 | 499.17 |

## Normalized Efficiency

Power efficiency uses sampled average GPU power for the whole phase. It is GPU-side power, not wall-plug power.

| Variant | Phase | C | Requests | Output tok/s | tok/s/GPU | tok/s/total GiB | tok/s/used GiB | tok/J | tok/s/kW |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 117.40 | 58.70 | 0.33 | 0.35 | 0.14 | 137.91 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 209.16 | 104.58 | 0.58 | 0.62 | 0.25 | 245.69 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 361.55 | 180.78 | 1.01 | 1.08 | 0.42 | 424.70 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 560.53 | 280.26 | 1.57 | 1.67 | 0.66 | 658.43 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 938.97 | 469.49 | 2.62 | 2.80 | 1.10 | 1102.97 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 1130.50 | 565.25 | 3.16 | 3.38 | 1.33 | 1327.95 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 114.27 | 57.13 | 0.32 | 0.34 | 0.14 | 140.32 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 214.54 | 107.27 | 0.60 | 0.64 | 0.26 | 263.46 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 226.76 | 113.38 | 0.63 | 0.68 | 0.30 | 300.86 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 377.75 | 188.88 | 1.05 | 1.14 | 0.50 | 501.19 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 568.62 | 284.31 | 1.59 | 1.71 | 0.75 | 754.44 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 921.82 | 460.91 | 2.57 | 2.77 | 1.22 | 1223.06 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 1383.56 | 691.78 | 3.86 | 4.16 | 1.84 | 1835.69 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 1690.53 | 845.26 | 4.72 | 5.09 | 2.24 | 2242.97 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 109.02 | 54.51 | 0.30 | 0.32 | 0.15 | 148.87 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 195.55 | 97.78 | 0.55 | 0.58 | 0.27 | 267.03 |

## Benchmark Latency

| Variant | Phase | C | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |
| --- | --- | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 83.24 | 8.12 | 8.11 |
| `nomtp` | HF/MT-Bench | 2 | 81.73 | 9.02 | 9.03 |
| `nomtp` | HF/MT-Bench | 4 | 82.00 | 10.35 | 10.41 |
| `nomtp` | HF/MT-Bench | 8 | 111.65 | 12.99 | 12.97 |
| `nomtp` | HF/MT-Bench | 16 | 138.87 | 15.40 | 15.18 |
| `nomtp` | HF/MT-Bench | 24 | 197.29 | 17.96 | 17.36 |
| `nomtp` | Random 8192/512 | 1 | 294.22 | 8.19 | 8.19 |
| `nomtp` | Random 8192/512 | 2 | 318.66 | 8.72 | 8.72 |
| `mtp` | HF/MT-Bench | 1 | 73.75 | 3.99 | 9.18 |
| `mtp` | HF/MT-Bench | 2 | 98.87 | 5.30 | 10.75 |
| `mtp` | HF/MT-Bench | 4 | 94.14 | 6.50 | 14.51 |
| `mtp` | HF/MT-Bench | 8 | 122.03 | 7.70 | 17.37 |
| `mtp` | HF/MT-Bench | 16 | 167.51 | 10.18 | 22.36 |
| `mtp` | HF/MT-Bench | 24 | 214.00 | 11.33 | 25.96 |
| `mtp` | Random 8192/512 | 1 | 290.88 | 8.62 | 9.39 |
| `mtp` | Random 8192/512 | 2 | 183.95 | 9.46 | 10.20 |

## ToolCall-15

| Variant | Score | Total runs | Unique cases | Failures |
| --- | ---: | ---: | ---: | ---: |
| `nomtp` | 225/270 (83%) | 135 | 45 | 27 |
| `mtp` | 225/270 (83%) | 135 | 45 | 27 |

### `nomtp` Failures

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

## Long Context Probes

These rows are diagnostic sentinel-retrieval checks for cache-layout regressions. They do not change accuracy scores.

| Variant | Case | OK | Prompt lines | Prompt tokens | Completion tokens | Elapsed s | Detail |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `nomtp` | `kv_indexer_long_context` | yes | 2400 | 74457 | 70 | 3.25 | matched long-context sentinel terms |
| `mtp` | `kv_indexer_long_context` | yes | 2400 | 74457 | 45 | 3.14 | matched long-context sentinel terms |

## Oracle Export

| Variant | Cases | Success | Model |
| --- | ---: | ---: | --- |
| `nomtp` | 5 | 5 | `deepseek-ai/DeepSeek-V4-Flash` |
| `mtp` | 5 | 5 | `deepseek-ai/DeepSeek-V4-Flash` |

## Accuracy Evals

These rows are optional public accuracy gates, intended for expensive reference captures and branch-promotion checks.

| Variant | Task | Version | OK | Fewshot | Concurrent | Max gen toks | EM flexible % | EM strict % | EM flex stderr |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | GSM8K | 3.0 | yes | 8 | 4 | 2048 | 94.92 | 95.00 | 0.0060 |
| `mtp` | GSM8K | 3.0 | yes | 8 | 1 | 2048 | 95.38 | 95.45 | 0.0058 |

## Runtime Stats

| Variant | Phase | Prefill delta | Decode delta | Successful delta | Max running | Log prefill tok/s | Log decode tok/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 45080 | 126050 | 489 | 25 | 91.51 | 350.06 |
| `nomtp` | Random 8192/512 | 131651 | 15643 | 16 | 3 | 856.23 | 215.69 |
| `mtp` | HF/MT-Bench | 33210 | 87088 | 457 | 24 | 126.93 | 338.36 |
| `mtp` | Random 8192/512 | 131072 | 7840 | 14 | 2 | 844.66 | 92.54 |

## MTP Speculative Decoding

| Variant | Phase | Samples | Mean acceptance length | Avg draft acceptance % | Per-position acceptance | Accepted tokens | Drafted tokens |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| `mtp` | HF/MT-Bench | 23 | 2.27 | 63.51 | `[0.790, 0.480]` | 43765 | 67968 |
| `mtp` | Random 8192/512 | 7 | 1.08 | 4.00 | `[0.063, 0.017]` | 586 | 13606 |

## Notes

- `tok/s/GPU` divides output token throughput by detected GPU count.
- `tok/s/total GiB` divides output token throughput by installed GPU VRAM.
- `tok/s/used GiB` divides output token throughput by sampled peak used GPU VRAM.
- `tok/J` and `tok/s/kW` use sampled average GPU power for the phase.
- Benchmark power and VRAM denominators are phase-level samples, not per-concurrency samples.
