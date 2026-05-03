# SM120 no-MTP DeepSeek V4 Flash Diagnostic Baseline

- Label: `sm120_nomtp_ds4_sm120_6e1e7ecad_diagnostic`
- Artifact generated at UTC: `2026-05-03T22:19:10.886752+00:00`
- Primary artifact: `artifacts/sm120_nomtp_ds4_sm120_6e1e7ecad_20260503193303`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Branch: `ds4-sm120`
- GPU: 2x NVIDIA RTX PRO 6000 Blackwell Workstation Edition (95.6 GiB each)
- Dataset: `hf` / `philschmid/mt-bench`

## Run Health

- vLLM collect_env: 7/7 phase captures exited 0
- Server unresponsive markers: none

## Provenance

| Field | Value |
| --- | --- |
| vLLM | `0.20.1rc1.dev183+g6e1e7ecad` |
| vLLM git sha | `6e1e7ecad` |
| vLLM CUDA archs | `Not Set` |
| PyTorch | `2.11.0+cu130` |
| PyTorch CUDA build | `13.0` |
| CUDA runtime | `Could not collect` |
| NVIDIA driver | `595.58.03` |
| Transformers | `4.57.6` |
| Triton | `3.6.0` |

## Serve Shape

| Variant | KV dtype | Block size | Max model len | TP | Max seqs | Max batched tokens | GPU memory util | Speculative config | MoE backend | Async scheduling | Enforce eager | Reasoning parser | Tokenizer mode | Tool parser | Auto tool | FP4 index cache | FlashInfer autotune disabled |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `nomtp` | `fp8` | 256 | 393216 | 2 | n/a | n/a | 0.985 | `n/a` | `n/a` | no | no | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | no | yes |

## Quick Performance Summary

### Real Scenario OP Cost Estimate

These rows use translation, writing, coding, and ToolCall-15 wall-clock samples. They are request-style operation estimates, not benchmark throughput prices.

#### Purchase / Amortized

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | translation | 90 | 100.00 | 12.12 | 62.57 | 809 | 758 | $0.0034 | $3.42 | $4.22 | $4.50 | $0.84 | $1.01 |
| `nomtp` | writing | 90 | 100.00 | 21.84 | 64.14 | 167 | 1401 | $0.0062 | $6.16 | $36.90 | $4.39 | $7.38 | $1.01 |
| `nomtp` | coding | 90 | 97.78 | 64.61 | 63.36 | 252 | 4094 | $0.0182 | $18.21 | $72.40 | $4.45 | $14.48 | $1.01 |
| `nomtp` | agentic | 135 | 80.00 | 3.25 | 58.35 | 3225 | 190 | $0.0009 | $0.92 | $0.28 | $4.83 | $0.06 | $1.01 |
| `nomtp` | reading_summary | 45 | 100.00 | 10.49 | 59.63 | 1699 | 626 | $0.0030 | $2.96 | $1.74 | $4.73 | $0.35 | $1.01 |

#### Rental / Cloud GPU-Hour

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | translation | 90 | 100.00 | 12.12 | 62.57 | 809 | 758 | $0.0065 | $6.46 | $7.99 | $8.52 | $1.60 | $1.92 |
| `nomtp` | writing | 90 | 100.00 | 21.84 | 64.14 | 167 | 1401 | $0.0116 | $11.65 | $69.83 | $8.32 | $13.97 | $1.92 |
| `nomtp` | coding | 90 | 97.78 | 64.61 | 63.36 | 252 | 4094 | $0.0345 | $34.46 | $137.01 | $8.42 | $27.40 | $1.92 |
| `nomtp` | agentic | 135 | 80.00 | 3.25 | 58.35 | 3225 | 190 | $0.0017 | $1.73 | $0.54 | $9.14 | $0.11 | $1.92 |
| `nomtp` | reading_summary | 45 | 100.00 | 10.49 | 59.63 | 1699 | 626 | $0.0056 | $5.60 | $3.30 | $8.94 | $0.66 | $1.92 |

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
| Primary | `nomtp` | HF/MT-Bench | 24 | 459.89 | 229.94 | 413.59 | 43.81 |
| Primary | `nomtp` | Random 8192/512 | 2 | 60.67 | 30.34 | 5845.57 | 21.58 |

### Runtime Prefill/Decode Averages

These are phase-local averages parsed from vLLM server logs.

| Source | Variant | Phase | Prefill avg tok/s | Decode avg tok/s | Prefill tokens | Decode tokens | Max running |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Primary | `nomtp` | HF/MT-Bench | 40.34 | 121.17 | 27682 | 75533 | 24 |
| Primary | `nomtp` | Random 8192/512 | 728.17 | 42.93 | 131072 | 7827 | 2 |

## Phase Exit Codes

| Variant | Phase | Exit | Artifact |
| --- | --- | ---: | --- |
| `nomtp` | `kv_layout_probe` | 0 | `nomtp/kv_layout_probe` |
| `nomtp` | `server_startup` | 0 | `nomtp/server_startup` |
| `nomtp` | `acceptance` | 1 | `nomtp/acceptance` |
| `nomtp` | `long_context_probe` | 0 | `nomtp/long_context_probe` |
| `nomtp` | `bench_hf_mt_bench` | 1 | `nomtp/bench_hf_mt_bench` |
| `nomtp` | `eval_gsm8k` | 0 | `nomtp/eval_gsm8k` |
| `nomtp` | `bench_random_8192x512` | 0 | `nomtp/bench_random_8192x512` |
| `nomtp` | `oracle_export` | 0 | `nomtp/oracle_export` |

## Acceptance Gates

| Variant | Gate | Exit |
| --- | --- | ---: |
| `nomtp` | `compileall` | 0 |
| `nomtp` | `generation` | 1 |
| `nomtp` | `health` | 0 |
| `nomtp` | `oracle_compare` | 0 |
| `nomtp` | `pytest` | 0 |
| `nomtp` | `ruff` | 0 |
| `nomtp` | `smoke_quick` | 0 |
| `nomtp` | `toolcall15` | 1 |
| `nomtp` | `vllm_collect_env` | 0 |

## Benchmark Throughput

| Variant | Phase | C | Requests | Req/s | Output tok/s | Avg GPU util % | Max power/GPU W |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 0.34 | 64.63 | 31.82 | 496.12 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 0.59 | 112.64 | 31.82 | 496.12 |
| `nomtp` | HF/MT-Bench | 4 | n/a | n/a | n/a | 31.82 | 496.12 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 1.48 | 277.54 | 31.82 | 496.12 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 2.05 | 390.17 | 31.82 | 496.12 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 2.42 | 459.89 | 31.82 | 496.12 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 0.08 | 41.77 | 89.48 | 605.68 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 0.12 | 60.67 | 89.48 | 605.68 |

## Normalized Efficiency

Power efficiency uses sampled average GPU power for the whole phase. It is GPU-side power, not wall-plug power.

| Variant | Phase | C | Requests | Output tok/s | tok/s/GPU | tok/s/total GiB | tok/s/used GiB | tok/J | tok/s/kW |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 64.63 | 32.31 | 0.34 | 0.34 | 0.27 | 274.03 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 112.64 | 56.32 | 0.59 | 0.59 | 0.48 | 477.59 |
| `nomtp` | HF/MT-Bench | 4 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 277.54 | 138.77 | 1.45 | 1.46 | 1.18 | 1176.76 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 390.17 | 195.09 | 2.04 | 2.06 | 1.65 | 1654.31 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 459.89 | 229.94 | 2.41 | 2.43 | 1.95 | 1949.93 |
| `nomtp` | Random 8192/512 | 1 | 8/8 | 41.77 | 20.89 | 0.22 | 0.22 | 0.06 | 55.75 |
| `nomtp` | Random 8192/512 | 2 | 8/8 | 60.67 | 30.34 | 0.32 | 0.32 | 0.08 | 80.98 |

## Benchmark Latency

| Variant | Phase | C | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |
| --- | --- | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 64.02 | 15.18 | 15.21 |
| `nomtp` | HF/MT-Bench | 2 | 91.35 | 17.14 | 17.14 |
| `nomtp` | HF/MT-Bench | 4 | n/a | n/a | n/a |
| `nomtp` | HF/MT-Bench | 8 | 151.89 | 26.67 | 26.64 |
| `nomtp` | HF/MT-Bench | 16 | 257.71 | 36.66 | 36.55 |
| `nomtp` | HF/MT-Bench | 24 | 413.59 | 43.81 | 43.66 |
| `nomtp` | Random 8192/512 | 1 | 3881.97 | 16.39 | 16.39 |
| `nomtp` | Random 8192/512 | 2 | 5845.57 | 21.58 | 21.58 |

## ToolCall-15

| Variant | Score | Total runs | Unique cases | Failures |
| --- | ---: | ---: | ---: | ---: |
| `nomtp` | 224/270 (83%) | 135 | 45 | 27 |

### `nomtp` Failures

- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
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
| `nomtp` | `kv_indexer_long_context` | yes | 2400 | 74457 | 70 | 55.02 | matched long-context sentinel terms |

## Oracle Export

| Variant | Cases | Success | Model |
| --- | ---: | ---: | --- |
| `nomtp` | 5 | 5 | `deepseek-ai/DeepSeek-V4-Flash` |

## Accuracy Evals

These rows are optional public accuracy gates, intended for expensive reference captures and branch-promotion checks.

| Variant | Task | Version | OK | Fewshot | Concurrent | Max gen toks | EM flexible % | EM strict % | EM flex stderr |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | GSM8K | 3.0 | yes | 8 | 4 | 2048 | 95.30 | 95.38 | 0.0058 |

## Runtime Stats

| Variant | Phase | Prefill delta | Decode delta | Successful delta | Max running | Log prefill tok/s | Log decode tok/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 27682 | 75533 | 401 | 24 | 40.34 | 121.17 |
| `nomtp` | Random 8192/512 | 131072 | 7827 | 14 | 2 | 728.17 | 42.93 |

## Notes

- `tok/s/GPU` divides output token throughput by detected GPU count.
- `tok/s/total GiB` divides output token throughput by installed GPU VRAM.
- `tok/s/used GiB` divides output token throughput by sampled peak used GPU VRAM.
- `tok/J` and `tok/s/kW` use sampled average GPU power for the phase.
- Benchmark power and VRAM denominators are phase-level samples, not per-concurrency samples.
