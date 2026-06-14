# Evidence

## Artifacts

| Artifact | Purpose | Notes |
| --- | --- | --- |
| `artifacts/main/2x_rtx_pro_6000_sm120/black_benediction_rtx_full_native_startup_smoke_pcie_ready/20260613175133` | Startup smoke after native build and B12X PCIe extension preparation | `server_startup=0`, `bench_random_prefill_sweep=0`; TP allreduce used `B12X_PCIE_ONESHOT` before `PYNCCL`. |
| `artifacts/main/2x_rtx_pro_6000_sm120/black_benediction_rtx_measure_16k65k_osl128_c1c2/20260613180251` | First B200 harness 16K/65K OSL=128 run | Passed, but process-separated warmup still allowed inference-time Triton JIT warnings, so it is secondary evidence. |
| `artifacts/main/2x_rtx_pro_6000_sm120/black_benediction_rtx_same_server_16k65k_osl128_c1c2/20260613181033` | Same-server warmup plus measurement with prefix cache left on | Passed, but prefix-cache hit rate became non-zero, so it is not valid for no-prefix prefill comparison. |
| `artifacts/main/2x_rtx_pro_6000_sm120/black_benediction_rtx_same_server_nopc_16k65k_osl128_c1c2/20260613181753` | Same-server warmup plus measurement with prefix cache disabled | Primary comparison artifact. |

## Primary No-Prefix Measurement

The primary comparison uses the `measurement/prefill_sweep_summary.json` from
`black_benediction_rtx_same_server_nopc_16k65k_osl128_c1c2/20260613181753`.

| Case | C | OK | Successful requests | Input tok/s | Output tok/s | Mean TTFT ms | P99 TTFT ms | Mean TPOT ms | P99 ITL ms |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `isl16384_osl128` | 1 | true | 8 | 5407.26 | 42.24 | 2446.82 | 2459.53 | 4.59 | 35.61 |
| `isl16384_osl128` | 2 | true | 8 | 5696.31 | 44.50 | 3471.63 | 5043.06 | 17.84 | 1200.29 |
| `isl65536_osl128` | 1 | true | 8 | 5867.14 | 11.46 | 10607.91 | 10706.52 | 4.42 | 21.70 |
| `isl65536_osl128` | 2 | true | 8 | 5945.66 | 11.61 | 16089.54 | 21570.63 | 46.81 | 1418.34 |

Speculative decoding acceptance in the same run:

| Case | C | Acceptance % | Acceptance length |
| --- | ---: | ---: | ---: |
| `isl16384_osl128` | 1 | 77.82 | 2.56 |
| `isl16384_osl128` | 2 | 72.72 | 2.45 |
| `isl65536_osl128` | 1 | 82.73 | 2.65 |
| `isl65536_osl128` | 2 | 88.96 | 2.78 |

Runtime summary:

| Case | Prefix hits | Preemptions | Waiting max | GPU memory max | GPU util avg | Temp max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `isl16384_osl128` | 0 | 0 | 0 | 93.51% | 72.62% | 91 C |
| `isl65536_osl128` | 0 | 0 | 1 | 93.52% | 89.39% | 94 C |

## Backend Markers

The startup smoke and primary no-prefix run both reported the B12X PCIe path
as active:

```text
Using b12x PCIe oneshot allreduce backend (world_size=2, max_size=65536, single_channel=True).
Using ['B12X_PCIE_ONESHOT', 'PYNCCL'] all-reduce backends ... for group 'tp:0'
```

The same logs also show that large prefill tensors are above the PCIe oneshot
`max_size` and fall back through the backend list, while decode-sized tensors
are accepted. That makes this path primarily relevant to decode/small allreduce
behavior, not the large sparse-prefill bottleneck.

## Invalid Or Secondary Runs

- The process-separated B200 measurement passed but still produced
  inference-time Triton JIT warnings. It is useful as a route check, not as the
  clean comparison.
- The same-server run with prefix cache enabled produced non-zero prefix-cache
  hit rate after warmup. Because the random benchmark is deterministic enough
  for warmup to populate reusable prefixes, those rows are excluded from the
  performance comparison.

## Comparison Anchors

Current RTX PR stable preview OSL=128 C=1 evidence:

| Input tokens | Requests | Input tok/s | Output tok/s | Mean TTFT ms | P99 ITL ms |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4096 | 8 | 3123.74 | 97.60 | 660.21 | 13.29 |
| 16384 | 8 | 6209.00 | 48.51 | 2030.49 | 13.37 |
| 65536 | 8 | 7049.72 | 13.77 | 8715.51 | 14.65 |

The black-benediction C=1 deltas against this anchor are `-12.9%` at 16K and
`-16.8%` at 65K for input tok/s, with worse mean TTFT on both shapes.
