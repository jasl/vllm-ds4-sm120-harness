# B200 vLLM Main DeepSeek V4 Flash Baseline

- Label: `b200_main_51295793a`
- Artifact generated at UTC: `2026-05-01T21:37:44.032012+00:00`
- Primary artifact: `artifacts/main/4x_nvidia_b200/b200_main_51295793a/20260501212604`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Branch: `main`
- GPU: 4x NVIDIA B200 (179.1 GiB each)
- Dataset: `hf` / `philschmid/mt-bench`

## Run Health

- vLLM collect_env: 8/8 phase captures exited 0
- Server unresponsive markers: none

## Provenance

| Field | Value |
| --- | --- |
| vLLM | `0.20.1rc1.dev138+g51295793a` |
| vLLM git sha | `51295793a` |
| vLLM CUDA archs | `Not Set` |
| PyTorch | `2.11.0+cu130` |
| PyTorch CUDA build | `13.0` |
| CUDA runtime | `13.0.88` |
| NVIDIA driver | `595.58.03` |
| Transformers | `5.7.0` |
| Triton | `3.6.0` |

## Serve Shape

| Variant | KV dtype | Block size | TP | Speculative config | Reasoning parser | Tokenizer mode | Tool parser | Auto tool | FP4 index cache | FlashInfer autotune disabled |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `nomtp` | `fp8` | 256 | 4 | `n/a` | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | yes | yes |
| `mtp` | `fp8` | 256 | 4 | `{"method":"mtp","num_speculative_tokens":2}` | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | yes | yes |

## Quick Performance Summary

### Real Scenario OP Cost Estimate

These rows use translation, writing, coding, and ToolCall-15 wall-clock samples. They are request-style operation estimates, not benchmark throughput prices.

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | translation | 6 | 100.00 | 0.57 | 112.17 | 86 | 64 | $0.0011 | $1.06 | $12.25 | $16.65 | $2.45 | $6.72 |
| `nomtp` | writing | 6 | 100.00 | 4.92 | 130.82 | 74 | 644 | $0.0092 | $9.19 | $124.24 | $14.27 | $24.85 | $6.72 |
| `nomtp` | coding | 12 | 100.00 | 32.64 | 135.77 | 190 | 4432 | $0.0610 | $60.95 | $320.80 | $13.75 | $64.16 | $6.72 |
| `nomtp` | agentic | 90 | 81.11 | 1.39 | 126.08 | 3132 | 175 | $0.0026 | $2.60 | $0.83 | $14.81 | $0.17 | $6.72 |
| `mtp` | translation | 6 | 100.00 | 0.31 | 206.33 | 86 | 63 | $0.0006 | $0.57 | $6.64 | $9.06 | $1.33 | $6.73 |
| `mtp` | writing | 6 | 100.00 | 3.25 | 204.86 | 74 | 665 | $0.0061 | $6.07 | $82.05 | $9.13 | $16.41 | $6.73 |
| `mtp` | coding | 12 | 100.00 | 16.05 | 286.18 | 190 | 4593 | $0.0300 | $30.01 | $157.95 | $6.53 | $31.59 | $6.73 |
| `mtp` | agentic | 90 | 80.00 | 0.81 | 227.69 | 3233 | 185 | $0.0015 | $1.52 | $0.47 | $8.21 | $0.09 | $6.73 |

### Reference Cost Model

- Hardware prices: B200: `$30,000/GPU`; RTX PRO 6000: `$8,565/GPU`; RTX 5090: `$1,999/GPU`; DGX Spark / GB10: `$3,999/GPU`.
- Amortization: 3 years at 70% useful utilization.
- Power: sampled average GPU power multiplied by PUE 1.25 and $0.12/kWh.
- Cache read price is a synthetic 20% of the input break-even price.
- Input and output prices each allocate the full hourly cost to that token class; do not add them together.

### Best Benchmark Throughput

| Source | Variant | Phase | C | Output tok/s | tok/s/GPU | Mean TTFT ms | Mean TPOT ms |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Primary | `nomtp` | HF/MT-Bench | 24 | 1338.55 | 334.64 | 236.35 | 14.50 |
| Primary | `nomtp` | Random 8192/512 | 2 | 252.53 | 63.13 | 161.44 | 7.59 |
| Primary | `mtp` | HF/MT-Bench | 24 | 1783.49 | 445.87 | 219.09 | 11.14 |
| Primary | `mtp` | Random 8192/512 | 2 | 224.60 | 56.15 | 164.50 | 8.51 |

### Runtime Prefill/Decode Averages

These are phase-local averages parsed from vLLM server logs.

| Source | Variant | Phase | Prefill avg tok/s | Decode avg tok/s | Prefill tokens | Decode tokens | Max running |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Primary | `nomtp` | HF/MT-Bench | 88.74 | 263.73 | 32294 | 84663 | 24 |
| Primary | `nomtp` | Random 8192/512 | 1109.33 | 97.72 | 131072 | 8192 | 2 |
| Primary | `mtp` | HF/MT-Bench | 134.30 | 369.05 | 33210 | 90264 | 24 |
| Primary | `mtp` | Random 8192/512 | 965.33 | 107.74 | 131072 | 8049 | 2 |

## Phase Exit Codes

| Variant | Phase | Exit | Artifact |
| --- | --- | ---: | --- |
| `nomtp` | `server_startup` | 0 | `nomtp/server_startup` |
| `nomtp` | `acceptance` | 1 | `nomtp/acceptance` |
| `nomtp` | `bench_hf_mt_bench` | 0 | `nomtp/bench_hf_mt_bench` |
| `nomtp` | `bench_random_8192x512` | 0 | `nomtp/bench_random_8192x512` |
| `nomtp` | `oracle_export` | 0 | `nomtp/oracle_export` |
| `mtp` | `server_startup` | 0 | `mtp/server_startup` |
| `mtp` | `acceptance` | 1 | `mtp/acceptance` |
| `mtp` | `bench_hf_mt_bench` | 0 | `mtp/bench_hf_mt_bench` |
| `mtp` | `bench_random_8192x512` | 0 | `mtp/bench_random_8192x512` |
| `mtp` | `oracle_export` | 0 | `mtp/oracle_export` |

## Acceptance Gates

| Variant | Gate | Exit |
| --- | --- | ---: |
| `nomtp` | `compileall` | 0 |
| `nomtp` | `health` | 0 |
| `nomtp` | `pytest` | 0 |
| `nomtp` | `ruff` | 0 |
| `nomtp` | `smoke_coding` | 0 |
| `nomtp` | `smoke_quality` | 0 |
| `nomtp` | `smoke_quick` | 0 |
| `nomtp` | `toolcall15` | 1 |
| `nomtp` | `vllm_collect_env` | 0 |
| `mtp` | `compileall` | 0 |
| `mtp` | `health` | 0 |
| `mtp` | `pytest` | 0 |
| `mtp` | `ruff` | 0 |
| `mtp` | `smoke_coding` | 0 |
| `mtp` | `smoke_quality` | 0 |
| `mtp` | `smoke_quick` | 0 |
| `mtp` | `toolcall15` | 1 |
| `mtp` | `vllm_collect_env` | 0 |

## Benchmark Throughput

| Variant | Phase | C | Requests | Req/s | Output tok/s | Avg GPU util % | Max power/GPU W |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 0.74 | 137.99 | 77.90 | 447.49 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 1.34 | 247.79 | 77.90 | 447.49 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 2.26 | 428.46 | 77.90 | 447.49 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 3.66 | 698.03 | 77.90 | 447.49 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 5.85 | 1071.10 | 77.90 | 447.49 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 7.23 | 1338.55 | 77.90 | 447.49 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 0.26 | 131.59 | 70.39 | 415.60 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 0.49 | 252.53 | 70.39 | 415.60 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 1.32 | 243.15 | 65.22 | 469.74 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 2.12 | 403.30 | 65.22 | 469.74 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 3.29 | 624.85 | 65.22 | 469.74 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 5.27 | 989.89 | 65.22 | 469.74 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 7.67 | 1445.66 | 65.22 | 469.74 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 9.49 | 1783.49 | 65.22 | 469.74 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 0.23 | 115.29 | 73.67 | 431.51 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 0.44 | 224.60 | 73.67 | 431.51 |

## Normalized Efficiency

Power efficiency uses sampled average GPU power for the whole phase. It is GPU-side power, not wall-plug power.

| Variant | Phase | C | Requests | Output tok/s | tok/s/GPU | tok/s/total GiB | tok/s/used GiB | tok/J | tok/s/kW |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 137.99 | 34.50 | 0.19 | 0.21 | 0.11 | 106.48 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 247.79 | 61.95 | 0.35 | 0.37 | 0.19 | 191.21 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 428.46 | 107.11 | 0.60 | 0.64 | 0.33 | 330.63 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 698.03 | 174.51 | 0.97 | 1.05 | 0.54 | 538.65 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 1071.10 | 267.77 | 1.50 | 1.61 | 0.83 | 826.54 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 1338.55 | 334.64 | 1.87 | 2.01 | 1.03 | 1032.93 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 131.59 | 32.90 | 0.18 | 0.20 | 0.11 | 106.90 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 252.53 | 63.13 | 0.35 | 0.38 | 0.21 | 205.15 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 243.15 | 60.79 | 0.34 | 0.36 | 0.19 | 190.32 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 403.30 | 100.83 | 0.56 | 0.60 | 0.32 | 315.68 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 624.85 | 156.21 | 0.87 | 0.94 | 0.49 | 489.09 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 989.89 | 247.47 | 1.38 | 1.48 | 0.77 | 774.82 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 1445.66 | 361.42 | 2.02 | 2.17 | 1.13 | 1131.57 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 1783.49 | 445.87 | 2.49 | 2.67 | 1.40 | 1396.00 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 115.29 | 28.82 | 0.16 | 0.17 | 0.09 | 88.94 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 224.60 | 56.15 | 0.31 | 0.33 | 0.17 | 173.26 |

## Benchmark Latency

| Variant | Phase | C | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |
| --- | --- | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 72.46 | 6.89 | 6.90 |
| `nomtp` | HF/MT-Bench | 2 | 80.19 | 7.63 | 7.58 |
| `nomtp` | HF/MT-Bench | 4 | 84.26 | 8.76 | 8.70 |
| `nomtp` | HF/MT-Bench | 8 | 94.50 | 10.48 | 10.38 |
| `nomtp` | HF/MT-Bench | 16 | 153.75 | 13.20 | 13.02 |
| `nomtp` | HF/MT-Bench | 24 | 236.35 | 14.50 | 14.45 |
| `nomtp` | Random 8192/512 | 1 | 260.31 | 7.10 | 7.11 |
| `nomtp` | Random 8192/512 | 2 | 161.44 | 7.59 | 7.59 |
| `mtp` | HF/MT-Bench | 1 | 75.74 | 3.71 | 8.47 |
| `mtp` | HF/MT-Bench | 2 | 98.26 | 4.84 | 9.95 |
| `mtp` | HF/MT-Bench | 4 | 97.80 | 5.75 | 13.04 |
| `mtp` | HF/MT-Bench | 8 | 126.69 | 6.91 | 16.12 |
| `mtp` | HF/MT-Bench | 16 | 160.37 | 9.75 | 21.57 |
| `mtp` | HF/MT-Bench | 24 | 219.09 | 11.14 | 24.57 |
| `mtp` | Random 8192/512 | 1 | 269.91 | 8.16 | 8.72 |
| `mtp` | Random 8192/512 | 2 | 164.50 | 8.51 | 9.47 |

## ToolCall-15

| Variant | Score | Total runs | Unique cases | Failures |
| --- | ---: | ---: | ---: | ---: |
| `nomtp` | 149/180 (83%) | 90 | 30 | 17 |
| `mtp` | 147/180 (82%) | 90 | 30 | 18 |

### `nomtp` Failures

- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-07` partial (1 points): Completed most of the chain.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-07` partial (1 points): Completed most of the chain.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-07` partial (1 points): Completed most of the chain.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
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
- `TC-07` fail (0 points): Did not carry file/contact data across the chain.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-07` fail (0 points): Did not carry file/contact data across the chain.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-07` fail (0 points): Did not carry file/contact data across the chain.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.

## Oracle Export

| Variant | Cases | Success | Model |
| --- | ---: | ---: | --- |
| `nomtp` | 5 | 5 | `deepseek-ai/DeepSeek-V4-Flash` |
| `mtp` | 5 | 5 | `deepseek-ai/DeepSeek-V4-Flash` |

## Runtime Stats

| Variant | Phase | Prefill delta | Decode delta | Successful delta | Max running | Log prefill tok/s | Log decode tok/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 32294 | 84663 | 444 | 24 | 88.74 | 263.73 |
| `nomtp` | Random 8192/512 | 131072 | 8192 | 16 | 2 | 1109.33 | 97.72 |
| `mtp` | HF/MT-Bench | 33210 | 90264 | 479 | 24 | 134.30 | 369.05 |
| `mtp` | Random 8192/512 | 131072 | 8049 | 14 | 2 | 965.33 | 107.74 |

## MTP Speculative Decoding

| Variant | Phase | Samples | Mean acceptance length | Avg draft acceptance % | Per-position acceptance | Accepted tokens | Drafted tokens |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| `mtp` | HF/MT-Bench | 21 | 2.29 | 64.30 | `[0.799, 0.487]` | 45520 | 71152 |
| `mtp` | Random 8192/512 | 6 | 1.09 | 4.33 | `[0.065, 0.021]` | 676 | 13710 |

## Notes

- `tok/s/GPU` divides output token throughput by detected GPU count.
- `tok/s/total GiB` divides output token throughput by installed GPU VRAM.
- `tok/s/used GiB` divides output token throughput by sampled peak used GPU VRAM.
- `tok/J` and `tok/s/kW` use sampled average GPU power for the phase.
- Benchmark power and VRAM denominators are phase-level samples, not per-concurrency samples.
- Quick runtime prefill/decode averages use supplement rows when a supplement artifact is provided.
