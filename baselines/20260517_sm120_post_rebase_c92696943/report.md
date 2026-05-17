# SM120 DeepSeek V4 Flash Post-Rebase Baseline (c92696943)

- Label: `sm120_post_rebase_c92696943`
- Artifact generated at UTC: `2026-05-17T05:02:33.281187+00:00`
- Primary artifact: `v6b`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Branch: `unknown-branch`
- GPU: 2x NVIDIA RTX PRO 6000 Blackwell Workstation Edition (95.6 GiB each)
- Dataset: `hf` / `philschmid/mt-bench`

## Run Health

- vLLM collect_env: 8/8 phase captures exited 0
- Server unresponsive markers: none

## Provenance

| Field | Value |
| --- | --- |
| vLLM | `0.1.dev16678+gd99ffa034` |
| vLLM git sha | `d99ffa034` |
| vLLM CUDA archs | `Not Set` |
| PyTorch | `2.11.0+cu130` |
| PyTorch CUDA build | `13.0` |
| CUDA runtime | `13.1.115` |
| NVIDIA driver | `595.58.03` |
| Transformers | `5.8.0` |
| Triton | `3.6.0` |

## Serve Shape

| Variant | KV dtype | Block size | Max model len | TP | Max seqs | Max batched tokens | GPU memory util | Speculative config | MoE backend | Async scheduling | Enforce eager | Reasoning parser | Tokenizer mode | Tool parser | Auto tool | FP4 index cache | FlashInfer autotune disabled |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `nomtp` | `fp8` | 256 | 65536 | 2 | n/a | n/a | 0.98 | `n/a` | `n/a` | no | no | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | no | yes |
| `mtp` | `fp8` | 256 | 65536 | 2 | n/a | n/a | 0.98 | `{"method":"mtp","num_speculative_tokens":2}` | `n/a` | no | no | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | no | yes |

## Quick Performance Summary

### Real Scenario OP Cost Estimate

These rows use translation, writing, coding, and ToolCall-15 wall-clock samples. They are request-style operation estimates, not benchmark throughput prices.

#### Purchase / Amortized

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | translation | 90 | 100.00 | 26.24 | 98.19 | 836 | 2577 | $0.0076 | $7.58 | $9.07 | $2.94 | $1.81 | $1.04 |
| `nomtp` | writing | 90 | 100.00 | 37.02 | 98.95 | 193 | 3663 | $0.0107 | $10.69 | $55.35 | $2.92 | $11.07 | $1.04 |
| `nomtp` | coding | 90 | 100.00 | 115.95 | 98.46 | 278 | 11415 | $0.0335 | $33.48 | $120.49 | $2.93 | $24.10 | $1.04 |
| `nomtp` | agentic | 135 | 90.37 | 3.65 | 76.64 | 3522 | 280 | $0.0011 | $1.05 | $0.30 | $3.77 | $0.06 | $1.04 |
| `nomtp` | reading_summary | 45 | 100.00 | 24.79 | 97.27 | 1725 | 2412 | $0.0072 | $7.16 | $4.15 | $2.97 | $0.83 | $1.04 |
| `mtp` | translation | 90 | 100.00 | 17.07 | 169.92 | 836 | 2900 | $0.0050 | $4.95 | $5.93 | $1.71 | $1.19 | $1.04 |
| `mtp` | writing | 90 | 100.00 | 23.82 | 158.65 | 193 | 3779 | $0.0069 | $6.91 | $35.79 | $1.83 | $7.16 | $1.04 |
| `mtp` | coding | 90 | 100.00 | 65.73 | 176.72 | 278 | 11615 | $0.0191 | $19.07 | $68.64 | $1.64 | $13.73 | $1.04 |
| `mtp` | agentic | 135 | 91.11 | 2.47 | 116.77 | 3514 | 288 | $0.0007 | $0.72 | $0.20 | $2.48 | $0.04 | $1.04 |
| `mtp` | reading_summary | 45 | 100.00 | 14.06 | 161.34 | 1725 | 2269 | $0.0041 | $4.08 | $2.37 | $1.80 | $0.47 | $1.04 |

#### Rental / Cloud GPU-Hour

| Variant | Workload | Samples | Pass % | Avg latency s | Output tok/s | Prompt tok/op | Output tok/op | Cost/op | Cost/1k ops | Input $/M | Output $/M | Cache read $/M | Cost/h |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | translation | 90 | 100.00 | 26.24 | 98.19 | 836 | 2577 | $0.0140 | $14.00 | $16.75 | $5.43 | $3.35 | $1.92 |
| `nomtp` | writing | 90 | 100.00 | 37.02 | 98.95 | 193 | 3663 | $0.0197 | $19.74 | $102.23 | $5.39 | $20.45 | $1.92 |
| `nomtp` | coding | 90 | 100.00 | 115.95 | 98.46 | 278 | 11415 | $0.0618 | $61.84 | $222.57 | $5.42 | $44.51 | $1.92 |
| `nomtp` | agentic | 135 | 90.37 | 3.65 | 76.64 | 3522 | 280 | $0.0019 | $1.95 | $0.55 | $6.96 | $0.11 | $1.92 |
| `nomtp` | reading_summary | 45 | 100.00 | 24.79 | 97.27 | 1725 | 2412 | $0.0132 | $13.22 | $7.67 | $5.48 | $1.53 | $1.92 |
| `mtp` | translation | 90 | 100.00 | 17.07 | 169.92 | 836 | 2900 | $0.0091 | $9.10 | $10.89 | $3.14 | $2.18 | $1.92 |
| `mtp` | writing | 90 | 100.00 | 23.82 | 158.65 | 193 | 3779 | $0.0127 | $12.70 | $65.78 | $3.36 | $13.16 | $1.92 |
| `mtp` | coding | 90 | 100.00 | 65.73 | 176.72 | 278 | 11615 | $0.0351 | $35.05 | $126.17 | $3.02 | $25.23 | $1.92 |
| `mtp` | agentic | 135 | 91.11 | 2.47 | 116.77 | 3514 | 288 | $0.0013 | $1.32 | $0.37 | $4.57 | $0.07 | $1.92 |
| `mtp` | reading_summary | 45 | 100.00 | 14.06 | 161.34 | 1725 | 2269 | $0.0075 | $7.50 | $4.35 | $3.31 | $0.87 | $1.92 |

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
| Primary | `nomtp` | HF/MT-Bench | 24 | 607.36 | 303.68 | 365.49 | 32.64 |
| Primary | `mtp` | HF/MT-Bench | 24 | 846.34 | 423.17 | 330.24 | 23.20 |

### Runtime Prefill/Decode Averages

These are phase-local averages parsed from vLLM server logs.

| Source | Variant | Phase | Prefill avg tok/s | Decode avg tok/s | Prefill tokens | Decode tokens | Max running | Max KV % | Prefix hit avg % | Preemptions |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Primary | `nomtp` | Acceptance | 37.52 | 97.80 | 668295 | 1735175 | 1 | 8.25 | 0.00 | 0 |
| Primary | `nomtp` | HF/MT-Bench | 196.09 | 189.28 | 33210 | 87774 | 24 | 7.35 | 0.00 | 0 |
| Primary | `nomtp` | GSM8K | 1094.72 | 116.81 | 178489 | 19133 | 4 | 5.18 | 0.00 | 0 |
| Primary | `nomtp` | Long Context Probe | 0.00 | 0.00 | 0 | 0 | 1 | 33.09 | 0.00 | 0 |
| Primary | `mtp` | Acceptance | 62.45 | 169.21 | 662598 | 1787145 | 1 | 14.13 | 0.00 | 0 |
| Primary | `mtp` | HF/MT-Bench | 270.29 | 254.76 | 33210 | 88019 | 24 | 9.58 | 0.00 | 0 |
| Primary | `mtp` | GSM8K | 963.48 | 117.64 | 175833 | 18821 | 1 | 6.79 | 0.00 | 0 |
| Primary | `mtp` | Long Context Probe | 0.00 | 0.00 | 0 | 0 | 1 | 51.56 | 0.00 | 0 |

## Phase Exit Codes

| Variant | Phase | Exit | Artifact |
| --- | --- | ---: | --- |
| `nomtp` | `server_startup` | 0 | `nomtp/server_startup` |
| `nomtp` | `acceptance` | 1 | `nomtp/acceptance` |
| `nomtp` | `long_context_probe` | 0 | `nomtp/long_context_probe` |
| `nomtp` | `bench_hf_mt_bench` | 0 | `nomtp/bench_hf_mt_bench` |
| `nomtp` | `eval_gsm8k` | 0 | `nomtp/eval_gsm8k` |
| `nomtp` | `decode_profile` | 0 | `nomtp/decode_profile` |
| `mtp` | `server_startup` | 0 | `mtp/server_startup` |
| `mtp` | `acceptance` | 1 | `mtp/acceptance` |
| `mtp` | `long_context_probe` | 0 | `mtp/long_context_probe` |
| `mtp` | `bench_hf_mt_bench` | 0 | `mtp/bench_hf_mt_bench` |
| `mtp` | `eval_gsm8k` | 0 | `mtp/eval_gsm8k` |
| `mtp` | `decode_profile` | 0 | `mtp/decode_profile` |

## Acceptance Gates

| Variant | Gate | Exit |
| --- | --- | ---: |
| `nomtp` | `compileall` | 0 |
| `nomtp` | `generation` | 0 |
| `nomtp` | `health` | 0 |
| `nomtp` | `pytest` | 1 |
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
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 0.53 | 98.35 | 79.63 | 523.27 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 0.88 | 163.18 | 79.63 | 523.27 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 1.44 | 266.11 | 79.63 | 523.27 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 2.04 | 380.18 | 79.63 | 523.27 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 2.76 | 519.93 | 79.63 | 523.27 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 3.31 | 607.36 | 79.63 | 523.27 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 0.89 | 165.45 | 74.20 | 548.51 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 1.33 | 248.49 | 74.20 | 548.51 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 1.68 | 315.89 | 74.20 | 548.51 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 2.81 | 529.89 | 74.20 | 548.51 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 3.85 | 721.09 | 74.20 | 548.51 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 4.71 | 846.34 | 74.20 | 548.51 |

## Normalized Efficiency

Power efficiency uses sampled average GPU power for the whole phase. It is GPU-side power, not wall-plug power.

| Variant | Phase | C | Requests | Output tok/s | tok/s/GPU | tok/s/total GiB | tok/s/used GiB | tok/J | tok/s/kW |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 80/80 | 98.35 | 49.17 | 0.51 | 0.52 | 0.15 | 145.86 |
| `nomtp` | HF/MT-Bench | 2 | 80/80 | 163.18 | 81.59 | 0.85 | 0.86 | 0.24 | 242.00 |
| `nomtp` | HF/MT-Bench | 4 | 80/80 | 266.11 | 133.06 | 1.39 | 1.40 | 0.39 | 394.65 |
| `nomtp` | HF/MT-Bench | 8 | 80/80 | 380.18 | 190.09 | 1.99 | 2.01 | 0.56 | 563.82 |
| `nomtp` | HF/MT-Bench | 16 | 80/80 | 519.93 | 259.96 | 2.72 | 2.74 | 0.77 | 771.08 |
| `nomtp` | HF/MT-Bench | 24 | 80/80 | 607.36 | 303.68 | 3.18 | 3.21 | 0.90 | 900.74 |
| `mtp` | HF/MT-Bench | 1 | 80/80 | 165.45 | 82.72 | 0.87 | 0.89 | 0.24 | 235.21 |
| `mtp` | HF/MT-Bench | 2 | 80/80 | 248.49 | 124.25 | 1.30 | 1.33 | 0.35 | 353.27 |
| `mtp` | HF/MT-Bench | 4 | 80/80 | 315.89 | 157.94 | 1.65 | 1.69 | 0.45 | 449.09 |
| `mtp` | HF/MT-Bench | 8 | 80/80 | 529.89 | 264.94 | 2.77 | 2.84 | 0.75 | 753.33 |
| `mtp` | HF/MT-Bench | 16 | 80/80 | 721.09 | 360.55 | 3.77 | 3.86 | 1.03 | 1025.15 |
| `mtp` | HF/MT-Bench | 24 | 80/80 | 846.34 | 423.17 | 4.43 | 4.54 | 1.20 | 1203.21 |

## Benchmark Latency

| Variant | Phase | C | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |
| --- | --- | ---: | ---: | ---: | ---: |
| `nomtp` | HF/MT-Bench | 1 | 54.94 | 9.92 | 9.92 |
| `nomtp` | HF/MT-Bench | 2 | 85.69 | 11.75 | 11.70 |
| `nomtp` | HF/MT-Bench | 4 | 88.83 | 14.44 | 14.30 |
| `nomtp` | HF/MT-Bench | 8 | 134.73 | 19.37 | 19.37 |
| `nomtp` | HF/MT-Bench | 16 | 244.04 | 27.28 | 27.32 |
| `nomtp` | HF/MT-Bench | 24 | 365.49 | 32.64 | 32.63 |
| `mtp` | HF/MT-Bench | 1 | 60.80 | 5.72 | 13.55 |
| `mtp` | HF/MT-Bench | 2 | 108.53 | 7.48 | 17.40 |
| `mtp` | HF/MT-Bench | 4 | 103.27 | 11.82 | 27.84 |
| `mtp` | HF/MT-Bench | 8 | 163.78 | 13.73 | 32.13 |
| `mtp` | HF/MT-Bench | 16 | 255.07 | 19.28 | 45.03 |
| `mtp` | HF/MT-Bench | 24 | 330.24 | 23.20 | 55.01 |

## ToolCall-15

| Variant | Score | Total runs | Unique cases | Failures |
| --- | ---: | ---: | ---: | ---: |
| `nomtp` | 247/270 (91%) | 135 | 45 | 13 |
| `mtp` | 248/270 (92%) | 135 | 45 | 12 |

### `nomtp` Failures

- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-15` fail (0 points): Did not preserve the exact searched value.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-14` fail (0 points): Did not handle the stock tool error with integrity.

### `mtp` Failures

- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-11` partial (1 points): Used calculator correctly but unnecessarily.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-12` fail (0 points): Did not refuse the unsupported email deletion request.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-14` partial (1 points): Recovered with web_search but did not surface the error.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-15` fail (0 points): Did not preserve the exact searched value.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-06` fail (0 points): Did not split the translation request into two valid calls.
- `TC-15` fail (0 points): Did not preserve the exact searched value.

## Long Context Probes

These rows are diagnostic sentinel-retrieval checks for cache-layout regressions. They do not change accuracy scores.

| Variant | Case | OK | Prompt lines | Prompt tokens | Completion tokens | Elapsed s | Detail |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `nomtp` | `kv_indexer_long_context` | yes | 1900 | 58957 | 70 | 20.86 | matched long-context sentinel terms |
| `mtp` | `kv_indexer_long_context` | yes | 1900 | 58957 | 70 | 20.46 | matched long-context sentinel terms |

## Accuracy Evals

These rows are optional public accuracy gates, intended for expensive reference captures and branch-promotion checks.

| Variant | Task | Version | OK | Fewshot | Concurrent | Max gen toks | EM flexible % | EM strict % | EM flex stderr |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | GSM8K | 3.0 | yes | 5 | 4 | 2048 | 95.50 | 95.50 | 0.0147 |
| `mtp` | GSM8K | 3.0 | yes | 5 | 1 | 2048 | 95.00 | 95.00 | 0.0154 |

## Runtime Stats

| Variant | Phase | Prefill delta | Decode delta | Successful delta | Max running | Max KV % | Prefix hit % | Preemptions | Log prefill tok/s | Log decode tok/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `nomtp` | Acceptance | 668295 | 1735175 | 665 | 1 | 8.25 | n/a | 0 | 37.52 | 97.80 |
| `nomtp` | HF/MT-Bench | 33210 | 87774 | 466 | 24 | 7.35 | n/a | 0 | 196.09 | 189.28 |
| `nomtp` | GSM8K | 178489 | 19133 | 200 | 4 | 5.18 | n/a | 0 | 1094.72 | 116.81 |
| `nomtp` | Long Context Probe | 0 | 0 | 0 | 1 | 33.09 | n/a | 0 | 0.00 | 0.00 |
| `mtp` | Acceptance | 662598 | 1787145 | 662 | 1 | 14.13 | n/a | 0 | 62.45 | 169.21 |
| `mtp` | HF/MT-Bench | 33210 | 88019 | 466 | 24 | 9.58 | n/a | 0 | 270.29 | 254.76 |
| `mtp` | GSM8K | 175833 | 18821 | 196 | 1 | 6.79 | n/a | 0 | 963.48 | 117.64 |
| `mtp` | Long Context Probe | 0 | 0 | 0 | 1 | 51.56 | n/a | 0 | 0.00 | 0.00 |

## MTP Speculative Decoding

| Variant | Phase | Samples | Mean acceptance length | Avg draft acceptance % | Per-position acceptance | Accepted tokens | Drafted tokens |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| `mtp` | Acceptance | 1056 | 2.40 | 69.98 | `[0.869, 0.531]` | 1041188 | 1491301 |
| `mtp` | HF/MT-Bench | 33 | 2.36 | 68.02 | `[0.844, 0.516]` | 49894 | 73356 |
| `mtp` | GSM8K | 18 | 2.61 | 80.67 | `[0.941, 0.672]` | 12907 | 16196 |

## Supplementary: MTP=1 Stability Follow-up

Side study, **not part of the regression baseline matrix** above. Triggered by
the known MTP=1 NCCL allgather hang noted in earlier baselines; the goal was
to check whether `nvidia-nccl-cu13 2.30.4` (which fixed the GB10 reliability
issue) also closes this hang.

**Result: hang reproduced.** NCCL 2.30.4 does not fix this — the bug appears
to be on the vLLM side (spec-decode K=1 collective ordering or logits
allgather interaction), not pure NCCL. MTP=1 remains opt-in only;
production-recommended config is still **MTP=2** (the primary `mtp` variant
above).

| Phase | Exit | Notes |
| --- | ---: | --- |
| `server_startup` | 0 | OK |
| `acceptance` | 1 | 6/8 sub-gates OK (toolcall15 + pytest exit 1 — same pattern as nomtp/mtp2) |
| `long_context_probe` | 0 | Sentinel retrieval passed at 1900 lines / 58,957 tokens |
| `bench_hf_mt_bench` | 1 | **HANG @ c=4** |
| `eval_gsm8k` | 143 | SIGTERM (server already dead) |
| `decode_profile` | 0 | Wrapper restarted serve cleanly; single-stream profile captured |

MTP=1 mt-bench up to the hang:

| Concurrency | Output tok/s | TPOT ms | Accept rate | Status |
| ---: | ---: | ---: | ---: | --- |
| 1 | 148.85 | 6.44 | 86.76% | ok |
| 2 | 242.66 | 7.76 | 86.36% | ok |
| 4 | 0.22 | 10.13 | 96.88% | **hang** (4/80 completed in 300 s, NCCL `_ALLGATHER_BASE` watchdog 600 s) |
| 8/16/24 | — | — | — | skipped (server unresponsive) |

Hang signature in `tensor_model_parallel_all_gather` → `_gather_logits` →
`compute_logits` in `deepseek_v4.py:1682`. Full evidence chain:
`mtp1_stability_followup/nccl_hang_evidence/serve_log_excerpt.txt`.

All raw MTP=1 captures including `decode_profile/torch_kernel_summary.md`
(single-stream, comparable to the v6b primary) and
`long_context_probe/long_context_probe.md` (sentinel retrieval pass at 58k
tokens) live under `mtp1_stability_followup/`.

## Supplementary: Port-Team Kernel Reference (v2)

Synthetic-input/synthetic-output reference for three SM12x-specific kernels,
intended for port teams (SGLang, TokenSpeed, and downstream forks) to verify
their reimplementation matches the vLLM reference at this exact `vllm@c92696943`
revision.

Kernels:

1. **`accumulate_indexed_sparse_mla_attention_chunk_multihead`** — multi-head
   prefill accumulate from `jasl/vllm#6` (HEAD_BLOCK=8).
2. **`deepseek_v4_sm12x_fp8_einsum`** — 3D mHC FP8 einsum `bhr,hdr->bhd`.
3. **`dequantize_and_gather_k_cache`** — packed FP8 KV-cache gather +
   dequant (`head_bytes = 520/576/584` depending on FlashMLA alignment).

Two shape buckets per kernel (`small` ≈ decode step, `medium` ≈ short-prefill
batch). Atol/rtol tolerances and capture metadata in
`port_reference/kernel_reference_v2/manifest.json`. ~71 MiB total. Reproducible
via `scripts/dump_kernel_reference.py --output-dir <out>` on any SM12x host.

## Supplementary: Production-Shape Fused-MoE Tune

Filled the previously-uncovered production shape `(E=128, N=2048,
block=[128,128])` for DSv4-Flash at `--tensor-parallel-size 2
--enable-expert-parallel`. Until this run, **no tuned config existed for
this shape in the vLLM tree** — Triton's default heuristic was in use for
the dominant MoE kernel.

| Field | Value |
| --- | --- |
| Device | `NVIDIA_RTX_PRO_6000_Blackwell_Workstation_Edition` |
| Shape | `E=128, N=2048, block=[128,128]` |
| dtype | `fp8_w8a8` |
| Triton version | `3.6.0` |
| M-buckets | 10 (1, 2, 4, 8, 16, 32, 64, 128, 256, 512) |
| Search space | 640 configs, M-aware filter |
| Source | `port_reference/moe_configs/E=128,N=2048,...json` |

To deploy: copy the JSON into `vllm/model_executor/layers/fused_moe/configs/`
in your vllm checkout and restart serve.

Three other typical-deployment shapes (TP=4+EP, TP=8+EP, TP=2 no-EP) are
NOT in this bundle — the sweep was terminated early after the production
shape landed. The driver lives at `scripts/run_fp8_moe_tune.sh` and can
finish the remaining shapes via a follow-up run.

## Supplementary: Tokenizer Parity Reference

Token-ID + SHA-256 snapshots for the DSv4 tokenizer applied to 12 prompts
across 4 chat-mode variants (`raw`, `chat_chat`, `chat_thinking`,
`chat_thinking_max`). Port teams (SGLang, TokenSpeed, downstream forks)
compare their tokenizer wrapping against these hashes to verify byte-exact
parity with `tokenizer_mode=deepseek_v4`.

Source: `port_reference/tokenizer_parity/{tokenizer_parity.json,tokenizer_parity.md}`.

## Supplementary: Oracle Top-K Logprobs Export

Token-level top-20 logprobs for 5 deterministic probe cases (`short_math`,
`raw_intro`, `translation`, `code_probe`, `long_prefill_2048`), captured
against the **nomtp** variant. Used for cross-platform alignment audits —
replay the same prompts on another implementation and compare top-K logprob
lists position-by-position.

Source: `oracle/` (5 × `completion_*.json` + 5 × `tokenize_*.json` +
`oracle_export_summary.{json,md}`). All cases `OK`, `exit 0`.

## Supplementary: Nsight Systems Long Trace

System-wide nsys trace of vLLM nomtp serve over its full lifecycle (~150 s):
spawn → 80 s model load + JIT warmup → captured 128-token request → SIGTERM
teardown. 125 MiB `.nsys-rep`, opens in `nsys-ui` for the per-kernel
timeline and NVTX-annotated phase boundaries.

Source: `nsys_profile/` (binary `.nsys-rep` file is NOT checked in — exceeds
GitHub's 100 MiB limit; only metadata and serve command are tracked. Ask
the bundle maintainer for the binary or rerun the capture). Complements the
kernel-summary tables in `v6b/{nomtp,mtp}/decode_profile/torch_kernel_summary.md`
— those are aggregate top-N tables, this is the raw timeline you'd want
for identifying serialisation points / collective stalls / stream overlap gaps.

## Notes

- `tok/s/GPU` divides output token throughput by detected GPU count.
- `tok/s/total GiB` divides output token throughput by installed GPU VRAM.
- `tok/s/used GiB` divides output token throughput by sampled peak used GPU VRAM.
- `tok/J` and `tok/s/kW` use sampled average GPU power for the phase.
- Benchmark power and VRAM denominators are phase-level samples, not per-concurrency samples.
