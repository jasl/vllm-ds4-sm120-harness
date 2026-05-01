# B200 vLLM Main DeepSeek V4 Flash Baseline

- Label: `b200_main_51295793a`
- Artifact generated at UTC: `2026-05-01T18:45:14.032341+00:00`
- Primary artifact: `artifacts/main/4x_nvidia_b200/b200_main_51295793a/20260501-184103`
- Supplement artifact: `artifacts/main/4x_nvidia_b200/b200_main_51295793a_logsliced_bench/20260501-190608`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Branch: `main`
- GPU: 4x NVIDIA B200 (179.1 GiB each)
- Dataset: `hf` / `philschmid/mt-bench`

## Run Health

- vLLM collect_env: 7/7 phase captures exited 0
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

### Best Benchmark Throughput

| Source | Variant | Phase | C | Output tok/s | tok/s/GPU | Mean TTFT ms | Mean TPOT ms |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Primary | `nomtp` | HF/MT-Bench | 24 | 686.52 | 171.63 | 3309.09 | 25.12 |
| Primary | `nomtp` | Random 8192/512 | 2 | 253.20 | 63.30 | 171.32 | 7.55 |
| Primary | `mtp` | HF/MT-Bench | 24 | 1756.57 | 439.14 | 217.51 | 11.33 |
| Primary | `mtp` | Random 8192/512 | 2 | 208.90 | 52.23 | 176.59 | 9.16 |
| Supplement | `nomtp` | HF/MT-Bench | 16 | 1092.18 | 273.05 | 155.88 | 12.72 |
| Supplement | `nomtp` | Random 8192/512 | 2 | 254.47 | 63.62 | 170.13 | 7.54 |
| Supplement | `mtp` | HF/MT-Bench | 24 | 1711.24 | 427.81 | 228.85 | 11.82 |
| Supplement | `mtp` | Random 8192/512 | 2 | 217.73 | 54.43 | 182.96 | 8.42 |

### Runtime Prefill/Decode Averages

These are phase-local averages parsed from vLLM server logs.

| Source | Variant | Phase | Prefill avg tok/s | Decode avg tok/s | Prefill tokens | Decode tokens | Max running |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Supplement | `nomtp` | HF/MT-Bench | 91.00 | 271.34 | 33210 | 89636 | 24 |
| Supplement | `nomtp` | Random 8192/512 | 1117.77 | 111.40 | 131072 | 8192 | 2 |
| Supplement | `mtp` | HF/MT-Bench | 145.93 | 415.88 | 31707 | 82130 | 23 |
| Supplement | `mtp` | Random 8192/512 | 844.64 | 129.10 | 131072 | 7803 | 2 |

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
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 0.74 | 137.76 | 70.87 | 459.63 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 1.31 | 241.59 | 70.87 | 459.63 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 2.27 | 418.45 | 70.87 | 459.63 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 2.44 | 460.08 | 70.87 | 459.63 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 2.95 | 553.26 | 70.87 | 459.63 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 3.65 | 686.52 | 70.87 | 459.63 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 0.26 | 131.61 | 69.94 | 414.84 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 0.49 | 253.20 | 69.94 | 414.84 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 1.29 | 241.23 | 65.57 | 479.86 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 2.14 | 397.98 | 65.57 | 479.86 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 3.35 | 626.98 | 65.57 | 479.86 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 5.34 | 980.73 | 65.57 | 479.86 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 3.81 | 716.86 | 65.57 | 479.86 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 9.43 | 1756.57 | 65.57 | 479.86 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 0.22 | 110.79 | 72.56 | 429.06 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 0.41 | 208.90 | 72.56 | 429.06 |

## Normalized Efficiency

Power efficiency uses sampled average GPU power for the whole phase. It is GPU-side power, not wall-plug power.

| Variant | Phase | C | Requests | Output tok/s | tok/s/GPU | tok/s/total GiB | tok/s/used GiB | tok/J | tok/s/kW |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 137.76 | 34.44 | 0.19 | 0.21 | 0.11 | 111.03 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 241.59 | 60.40 | 0.34 | 0.36 | 0.19 | 194.71 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 418.45 | 104.61 | 0.58 | 0.63 | 0.34 | 337.25 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 460.08 | 115.02 | 0.64 | 0.69 | 0.37 | 370.80 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 553.26 | 138.31 | 0.77 | 0.83 | 0.45 | 445.90 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 686.52 | 171.63 | 0.96 | 1.03 | 0.55 | 553.31 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 131.61 | 32.90 | 0.18 | 0.20 | 0.11 | 107.47 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 253.20 | 63.30 | 0.35 | 0.38 | 0.21 | 206.76 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 241.23 | 60.31 | 0.34 | 0.36 | 0.19 | 188.92 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 397.98 | 99.50 | 0.56 | 0.60 | 0.31 | 311.68 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 626.98 | 156.75 | 0.88 | 0.94 | 0.49 | 491.02 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 980.73 | 245.18 | 1.37 | 1.47 | 0.77 | 768.07 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 716.86 | 179.22 | 1.00 | 1.07 | 0.56 | 561.42 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 1756.57 | 439.14 | 2.45 | 2.63 | 1.38 | 1375.67 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 110.79 | 27.70 | 0.15 | 0.16 | 0.09 | 85.36 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 208.90 | 52.23 | 0.29 | 0.31 | 0.16 | 160.95 |

## Benchmark Latency

| Variant | Phase | C | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |
| --- | --- | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 74.65 | 6.89 | 6.89 |
| `nomtp` | HF/MT-Bench | 2 | 94.76 | 8.45 | 7.68 |
| `nomtp` | HF/MT-Bench | 4 | 100.68 | 8.99 | 8.79 |
| `nomtp` | HF/MT-Bench | 8 | 1051.32 | 11.03 | 11.16 |
| `nomtp` | HF/MT-Bench | 16 | 988.07 | 23.90 | 22.45 |
| `nomtp` | HF/MT-Bench | 24 | 3309.09 | 25.12 | 15.36 |
| `nomtp` | Random 8192/512 | 1 | 266.99 | 7.09 | 7.09 |
| `nomtp` | Random 8192/512 | 2 | 171.32 | 7.55 | 7.56 |
| `mtp` | HF/MT-Bench | 1 | 78.70 | 3.70 | 8.47 |
| `mtp` | HF/MT-Bench | 2 | 106.41 | 6.11 | 10.12 |
| `mtp` | HF/MT-Bench | 4 | 96.39 | 5.74 | 13.03 |
| `mtp` | HF/MT-Bench | 8 | 126.97 | 7.06 | 15.99 |
| `mtp` | HF/MT-Bench | 16 | 2056.72 | 10.22 | 24.06 |
| `mtp` | HF/MT-Bench | 24 | 217.51 | 11.33 | 24.84 |
| `mtp` | Random 8192/512 | 1 | 283.45 | 8.49 | 8.71 |
| `mtp` | Random 8192/512 | 2 | 176.59 | 9.16 | 9.44 |

## ToolCall-15

| Variant | Score | Cases | Failures |
| --- | ---: | ---: | ---: |
| `nomtp` | 24/30 (80%) | 15 | 3 |
| `mtp` | 23/30 (77%) | 15 | 4 |

### `nomtp` Failures

- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-08` fail (0 points): Did not respect the weather-first conditional flow.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.

### `mtp` Failures

- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-08` fail (0 points): Did not respect the weather-first conditional flow.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.

## Oracle Export

| Variant | Cases | Success | Model |
| --- | ---: | ---: | --- |
| `nomtp` | 5 | 5 | `deepseek-ai/DeepSeek-V4-Flash` |

## Supplement Benchmark Throughput

| Variant | Phase | C | Requests | Req/s | Output tok/s | Avg GPU util % | Max power/GPU W |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 0.73 | 138.34 | 77.01 | 456.20 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 1.34 | 247.97 | 77.01 | 456.20 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 2.29 | 430.09 | 77.01 | 456.20 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 3.68 | 683.87 | 77.01 | 456.20 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 5.80 | 1092.18 | 77.01 | 456.20 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 4.06 | 762.13 | 77.01 | 456.20 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 0.26 | 131.74 | 70.37 | 415.92 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 0.50 | 254.47 | 70.37 | 415.92 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 1.28 | 237.06 | 69.22 | 464.64 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 2.10 | 401.70 | 69.22 | 464.64 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 3.39 | 626.04 | 69.22 | 464.64 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 5.11 | 942.88 | 69.22 | 464.64 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 7.49 | 1393.43 | 69.22 | 464.64 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 9.19 | 1711.24 | 69.22 | 464.64 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 0.22 | 113.18 | 71.79 | 426.52 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 0.43 | 217.73 | 71.79 | 426.52 |

## Supplement Normalized Efficiency

Power efficiency uses sampled average GPU power for the whole phase. It is GPU-side power, not wall-plug power.

| Variant | Phase | C | Requests | Output tok/s | tok/s/GPU | tok/s/total GiB | tok/s/used GiB | tok/J | tok/s/kW |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 138.34 | 34.59 | 0.19 | 0.21 | 0.11 | 108.33 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 247.97 | 61.99 | 0.35 | 0.37 | 0.19 | 194.17 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 430.09 | 107.52 | 0.60 | 0.65 | 0.34 | 336.78 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 683.87 | 170.97 | 0.95 | 1.03 | 0.54 | 535.50 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 1092.18 | 273.05 | 1.52 | 1.64 | 0.86 | 855.22 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 762.13 | 190.53 | 1.06 | 1.14 | 0.60 | 596.78 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 131.74 | 32.94 | 0.18 | 0.20 | 0.11 | 107.43 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 254.47 | 63.62 | 0.36 | 0.38 | 0.21 | 207.51 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 237.06 | 59.27 | 0.33 | 0.36 | 0.18 | 182.54 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 401.70 | 100.42 | 0.56 | 0.60 | 0.31 | 309.32 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 626.04 | 156.51 | 0.87 | 0.94 | 0.48 | 482.06 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 942.88 | 235.72 | 1.32 | 1.41 | 0.73 | 726.04 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 1393.43 | 348.36 | 1.95 | 2.09 | 1.07 | 1072.97 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 1711.24 | 427.81 | 2.39 | 2.56 | 1.32 | 1317.69 |
| `mtp` | Random 8192/512 | 1 | 8/8 | 113.18 | 28.30 | 0.16 | 0.17 | 0.09 | 87.69 |
| `mtp` | Random 8192/512 | 2 | 8/8 | 217.73 | 54.43 | 0.30 | 0.32 | 0.17 | 168.69 |

## Supplement Benchmark Latency

| Variant | Phase | C | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |
| --- | --- | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 70.44 | 6.89 | 6.89 |
| `nomtp` | HF/MT-Bench | 2 | 78.32 | 7.62 | 7.57 |
| `nomtp` | HF/MT-Bench | 4 | 86.34 | 8.75 | 8.69 |
| `nomtp` | HF/MT-Bench | 8 | 117.42 | 10.43 | 10.47 |
| `nomtp` | HF/MT-Bench | 16 | 155.88 | 12.72 | 12.68 |
| `nomtp` | HF/MT-Bench | 24 | 1645.51 | 21.28 | 20.64 |
| `nomtp` | Random 8192/512 | 1 | 263.09 | 7.09 | 7.09 |
| `nomtp` | Random 8192/512 | 2 | 170.13 | 7.54 | 7.54 |
| `mtp` | HF/MT-Bench | 1 | 83.18 | 3.83 | 8.54 |
| `mtp` | HF/MT-Bench | 2 | 103.67 | 4.86 | 9.99 |
| `mtp` | HF/MT-Bench | 4 | 95.09 | 5.92 | 13.15 |
| `mtp` | HF/MT-Bench | 8 | 138.24 | 7.29 | 16.63 |
| `mtp` | HF/MT-Bench | 16 | 187.26 | 9.74 | 22.24 |
| `mtp` | HF/MT-Bench | 24 | 228.85 | 11.82 | 25.62 |
| `mtp` | Random 8192/512 | 1 | 280.58 | 8.30 | 8.72 |
| `mtp` | Random 8192/512 | 2 | 182.96 | 8.42 | 9.47 |

## Supplement Runtime Stats

| Variant | Phase | Prefill delta | Decode delta | Successful delta | Max running | Log prefill tok/s | Log decode tok/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 33210 | 89636 | 473 | 24 | 91.00 | 271.34 |
| `nomtp` | Random 8192/512 | 131072 | 8192 | 16 | 2 | 1117.77 | 111.40 |
| `mtp` | HF/MT-Bench | 31707 | 82130 | 436 | 23 | 145.93 | 415.88 |
| `mtp` | Random 8192/512 | 131072 | 7803 | 14 | 2 | 844.64 | 129.10 |

## MTP Speculative Decoding

| Variant | Phase | Samples | Mean acceptance length | Avg draft acceptance % | Per-position acceptance | Accepted tokens | Drafted tokens |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| `mtp` | HF/MT-Bench | 21 | 2.26 | 62.98 | `[0.783, 0.477]` | 48997 | 76516 |
| `mtp` | Random 8192/512 | 8 | 1.23 | 11.56 | `[0.158, 0.073]` | 1852 | 16956 |

## Supplement Phase Exit Codes

| Variant | Phase | Exit | Artifact |
| --- | --- | ---: | --- |
| `nomtp` | `server_startup` | 0 | `nomtp/server_startup` |
| `nomtp` | `bench_hf_mt_bench` | 0 | `nomtp/bench_hf_mt_bench` |
| `nomtp` | `bench_random_8192x512` | 0 | `nomtp/bench_random_8192x512` |
| `mtp` | `server_startup` | 0 | `mtp/server_startup` |
| `mtp` | `bench_hf_mt_bench` | 0 | `mtp/bench_hf_mt_bench` |
| `mtp` | `bench_random_8192x512` | 0 | `mtp/bench_random_8192x512` |

## Notes

- `tok/s/GPU` divides output token throughput by detected GPU count.
- `tok/s/total GiB` divides output token throughput by installed GPU VRAM.
- `tok/s/used GiB` divides output token throughput by sampled peak used GPU VRAM.
- `tok/J` and `tok/s/kW` use sampled average GPU power for the phase.
- Benchmark power and VRAM denominators are phase-level samples, not per-concurrency samples.
- Quick runtime prefill/decode averages use supplement rows when a supplement artifact is provided.
