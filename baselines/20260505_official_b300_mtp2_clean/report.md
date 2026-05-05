# DeepSeek V4 Flash Official B300 MTP2 Baseline

- Label: `official_b300_mtp2_clean`
- Artifact generated at UTC: `2026-05-05T19:06:40.181566+00:00`
- Primary artifact: `artifacts/official_b300_mtp2_clean/20260505184836`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Branch: `official_b300_mtp2_clean`
- GPU: 8x NVIDIA B300 SXM6 AC (268.6 GiB each)
- Dataset: `random` / `philschmid/mt-bench`

## Run Health

- vLLM collect_env: 2/2 phase captures exited 0
- Server unresponsive markers: none

## Provenance

| Field | Value |
| --- | --- |
| vLLM | `0.20.2rc1.dev48+g628c43630` |
| vLLM git sha | `628c43630` |
| vLLM CUDA archs | `Not Set` |
| PyTorch | `2.11.0+cu130` |
| PyTorch CUDA build | `13.0` |
| CUDA runtime | `Could not collect` |
| NVIDIA driver | `595.58.03` |
| Transformers | `5.7.0` |
| Triton | `3.6.0` |

## Serve Shape

| Variant | KV dtype | Block size | Max model len | TP | Max seqs | Max batched tokens | GPU memory util | Speculative config | MoE backend | Async scheduling | Enforce eager | Reasoning parser | Tokenizer mode | Tool parser | Auto tool | FP4 index cache | FlashInfer autotune disabled |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `mtp` | `fp8` | 256 | n/a | 8 | n/a | n/a | n/a | `{"method":"mtp","num_speculative_tokens":2}` | `deep_gemm_mega_moe` | no | no | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | yes | no |

## Quick Performance Summary

### Real Scenario OP Cost Estimate

These rows use translation, writing, coding, and ToolCall-15 wall-clock samples. They are request-style operation estimates, not benchmark throughput prices.

#### Purchase / Amortized

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `mtp` | translation | 30 | 100.00 | 4.06 | 185.29 | 809 | 751 | n/a | n/a | n/a | n/a | n/a | n/a |
| `mtp` | writing | 30 | 100.00 | 8.39 | 164.45 | 167 | 1380 | n/a | n/a | n/a | n/a | n/a | n/a |
| `mtp` | coding | 30 | 100.00 | 19.21 | 222.42 | 252 | 4273 | n/a | n/a | n/a | n/a | n/a | n/a |
| `mtp` | agentic | 45 | 100.00 | 1.20 | 162.45 | 3277 | 194 | n/a | n/a | n/a | n/a | n/a | n/a |
| `mtp` | reading_summary | 15 | 100.00 | 3.57 | 177.65 | 1699 | 635 | n/a | n/a | n/a | n/a | n/a | n/a |

#### Rental / Cloud GPU-Hour

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `mtp` | translation | 30 | 100.00 | 4.06 | 185.29 | 809 | 751 | n/a | n/a | n/a | n/a | n/a | n/a |
| `mtp` | writing | 30 | 100.00 | 8.39 | 164.45 | 167 | 1380 | n/a | n/a | n/a | n/a | n/a | n/a |
| `mtp` | coding | 30 | 100.00 | 19.21 | 222.42 | 252 | 4273 | n/a | n/a | n/a | n/a | n/a | n/a |
| `mtp` | agentic | 45 | 100.00 | 1.20 | 162.45 | 3277 | 194 | n/a | n/a | n/a | n/a | n/a | n/a |
| `mtp` | reading_summary | 15 | 100.00 | 3.57 | 177.65 | 1699 | 635 | n/a | n/a | n/a | n/a | n/a | n/a |

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
| Primary | `mtp` | Random 8192/512 | 8 | 515.41 | 64.43 | 393.47 | 13.62 |

### Runtime Prefill/Decode Averages

These are phase-local averages parsed from vLLM server logs.

| Source | Variant | Phase | Prefill avg tok/s | Decode avg tok/s | Prefill tokens | Decode tokens | Max running | Max KV % | Prefix hit avg % | Preemptions |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Primary | `mtp` | Acceptance | 44.48 | 197.72 | 210283 | 210486 | 1 | 0.03 | 72.17 | 0 |
| Primary | `mtp` | Random 8192/512 | 78.01 | 155.95 | 1048576 | 64922 | 8 | 0.28 | 77.38 | 0 |

## Phase Exit Codes

| Variant | Phase | Exit | Artifact |
| --- | --- | ---: | --- |
| `mtp` | `static_compileall` | 0 | `mtp/static_compileall` |
| `mtp` | `static_pytest` | 0 | `mtp/static_pytest` |
| `mtp` | `static_ruff` | 0 | `mtp/static_ruff` |
| `mtp` | `acceptance` | 0 | `mtp/acceptance` |
| `mtp` | `bench_random_8192x512` | 0 | `mtp/bench_random_8192x512` |

## Acceptance Gates

| Variant | Gate | Exit |
| --- | --- | ---: |
| `mtp` | `generation` | 0 |
| `mtp` | `health` | 0 |
| `mtp` | `smoke_quick` | 0 |
| `mtp` | `toolcall15` | 0 |
| `mtp` | `vllm_collect_env` | 0 |

## Benchmark Throughput

| Variant | Phase | C | Requests | Req/s | Output tok/s | Avg GPU util % | Max power/GPU W |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `mtp` | Random 8192/512 | 1 | 32/32 | 0.19 | 96.34 | 79.88 | 367.38 |
| `mtp` | Random 8192/512 | 2 | 32/32 | 0.36 | 185.52 | 79.88 | 367.38 |
| `mtp` | Random 8192/512 | 4 | 32/32 | 0.51 | 258.78 | 79.88 | 367.38 |
| `mtp` | Random 8192/512 | 8 | 32/32 | 1.01 | 515.41 | 79.88 | 367.38 |

## Normalized Efficiency

Power efficiency uses sampled average GPU power for the whole phase. It is GPU-side power, not wall-plug power.

| Variant | Phase | C | Requests | Output tok/s | tok/s/GPU | tok/s/total GiB | tok/s/used GiB | tok/J | tok/s/kW |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `mtp` | Random 8192/512 | 1 | 32/32 | 96.34 | 12.04 | 0.04 | 0.05 | 0.04 | 41.04 |
| `mtp` | Random 8192/512 | 2 | 32/32 | 185.52 | 23.19 | 0.09 | 0.09 | 0.08 | 79.02 |
| `mtp` | Random 8192/512 | 4 | 32/32 | 258.78 | 32.35 | 0.12 | 0.13 | 0.11 | 110.23 |
| `mtp` | Random 8192/512 | 8 | 32/32 | 515.41 | 64.43 | 0.24 | 0.26 | 0.22 | 219.54 |

## Benchmark Latency

| Variant | Phase | C | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |
| --- | --- | ---: | ---: | ---: | ---: |
| `mtp` | Random 8192/512 | 1 | 211.86 | 9.98 | 11.37 |
| `mtp` | Random 8192/512 | 2 | 231.37 | 10.02 | 12.16 |
| `mtp` | Random 8192/512 | 4 | 1419.80 | 12.13 | 14.61 |
| `mtp` | Random 8192/512 | 8 | 393.47 | 13.62 | 15.39 |

## ToolCall-15

| Variant | Score | Total runs | Unique cases | Failures |
| --- | ---: | ---: | ---: | ---: |
| `mtp` | 74/90 (82%) | 45 | 45 | 0 |

### `mtp` Failures

- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-07` partial (1 points): Completed most of the chain.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.

## Runtime Stats

| Variant | Phase | Prefill delta | Decode delta | Successful delta | Max running | Max KV % | Prefix hit % | Preemptions | Log prefill tok/s | Log decode tok/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `mtp` | Acceptance | 210283 | 210486 | 220 | 1 | 0.03 | 76.33 | 0 | 44.48 | 197.72 |
| `mtp` | Random 8192/512 | 1048576 | 64922 | 123 | 8 | 0.28 | 96.88 | 0 | 78.01 | 155.95 |

## MTP Speculative Decoding

| Variant | Phase | Samples | Mean acceptance length | Avg draft acceptance % | Per-position acceptance | Accepted tokens | Drafted tokens |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| `mtp` | Acceptance | 106 | 2.34 | 66.77 | `[0.822, 0.513]` | 119766 | 179737 |
| `mtp` | Random 8192/512 | 39 | 1.15 | 7.62 | `[0.108, 0.044]` | 9540 | 111758 |

## Notes

- `tok/s/GPU` divides output token throughput by detected GPU count.
- `tok/s/total GiB` divides output token throughput by installed GPU VRAM.
- `tok/s/used GiB` divides output token throughput by sampled peak used GPU VRAM.
- `tok/J` and `tok/s/kW` use sampled average GPU power for the phase.
- Benchmark power and VRAM denominators are phase-level samples, not per-concurrency samples.
