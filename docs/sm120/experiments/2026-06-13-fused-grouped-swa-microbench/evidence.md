# Evidence

## Artifacts

All paths are relative to the harness repository.

| Run | Scope | Artifact |
| --- | --- | --- |
| group32/block32 paired | RTX old grouped-SWA plus fused grouped-SWA | `artifacts/main/2x_rtx_pro_6000_sm120/indexed_d512_grouped_swa_fused_merge_microbench/formal_20260613_group32_block32` |
| group32/block32 fused-only | RTX fused candidate without old grouped-SWA warmup/timing | `artifacts/main/2x_rtx_pro_6000_sm120/indexed_d512_grouped_swa_fused_merge_microbench/formal_20260613_group32_block32_fused_only` |
| group16/block32 paired | RTX parameter sweep | `artifacts/main/2x_rtx_pro_6000_sm120/indexed_d512_grouped_swa_fused_merge_microbench/formal_20260613_g16_b32` |
| group16/block64 paired | RTX parameter sweep | `artifacts/main/2x_rtx_pro_6000_sm120/indexed_d512_grouped_swa_fused_merge_microbench/formal_20260613_g16_b64` |
| endpoint control off | RTX 16K/C=1 endpoint A/B control | `artifacts/codex_ds4_sm120_fused_swa_endpoint_dev_20260613/2x_rtx_pro_6000_sm120/fused_grouped_swa_endpoint_ab_control_off_16k/20260613195706` |
| endpoint grouped-SWA on | RTX 16K/C=1 endpoint route-hit candidate | `artifacts/codex_ds4_sm120_fused_swa_endpoint_dev_20260613/2x_rtx_pro_6000_sm120/fused_grouped_swa_endpoint_smoke_on_16k_routehit/20260613195455` |

## Best Fused-Only Run

Command shape:

- candidate lens: `640,1152`
- tokens / heads / dim: `512 / 64 / 512`
- compressed candidates: `128`
- index pattern: `mixed-c128-swa`
- group size: `32`
- grouped-SWA block-C: `32`
- warmup / iterations: `5 / 20`

| Candidates | Current chunk ms | Split total ms | Fused ms | Split/fused speedup | Current/fused speedup | Max abs diff |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 640 | 2.383 | 0.630 | 0.498 | 1.264x | 4.780x | 0.002607 |
| 1152 | 4.253 | 1.383 | 0.743 | 1.860x | 5.720x | 0.000953 |

## Paired Old Versus Fused

| Group/block-C | Candidates | Split ms | Old grouped-SWA ms | Fused grouped-SWA ms | Fused vs old | Max abs diff |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 32 / 32 | 640 | 0.627 | 0.576 | 0.520 | 1.106x | 0.002607 |
| 32 / 32 | 1152 | 1.383 | 0.823 | 0.768 | 1.071x | 0.000953 |
| 16 / 32 | 640 | 0.626 | 0.668 | 0.601 | 1.111x | 0.002607 |
| 16 / 32 | 1152 | 1.385 | 1.011 | 0.925 | 1.093x | 0.000953 |
| 16 / 64 | 640 | 0.627 | 0.601 | 0.542 | 1.109x | 0.002584 |
| 16 / 64 | 1152 | 1.383 | 0.872 | 0.813 | 1.073x | 0.000975 |

Group32/block32 remains the best component point in this sweep. Group16/block64
is a viable fallback shape if endpoint integration exposes shared-memory or
occupancy pressure, but it is slower on both candidate counts.

## Script Validation

Local harness checks:

```bash
python -m py_compile scripts/run_sm12x_indexed_d512_split_microbench.py
python -m pytest tests/test_indexed_d512_microbench.py -q
python -m pytest tests/test_scripts.py::test_indexed_d512_split_microbench_targets_current_chunk_path -q
```

Results: all passed.

Remote RTX smoke before the formal sweep compiled the fused kernel and matched
the split reference within `0.000761` max abs diff on the small 32-token shape.

## Endpoint Route-Hit A/B

The endpoint prototype added
`VLLM_DEEPSEEK_V4_INDEXED_D512_GROUPED_SWA_PREFILL` as a default-off route.
The first successful route-hit smoke showed that the env propagated through the
harness and that C128 rows reached `mla_prefill_indexed_d512_grouped_swa`.

Before the route-hit smoke, a focused CUDA probe compared the new fused
grouped-SWA wrapper against the combined-index reference with nonzero
`swa_token_start` and nonzero `swa_gather_start`. Result:

| Max abs diff | Mean abs diff | Ref norm | New norm |
| ---: | ---: | ---: | ---: |
| 0.0078125 | 0.0001973 | 156.2222 | 156.2212 |

The endpoint A/B was still negative:

| Case | OK | Input tok/s | Mean TTFT ms | Layer counts | Total sparse ms | Sparse accumulate ms |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| grouped-SWA off | true | 8051.11 | 2036.33 | `chunk=388,indexed_d512=574` | 3971.983 | 2697.948 |
| grouped-SWA on | true | 8031.37 | 2040.99 | `chunk=388,indexed_d512=294,grouped_swa=280` | 5040.047 | 3691.097 |

C128-only group:

| Case | C128 route | Rows | Total ms | Sparse accumulate ms | Effective visits/s |
| --- | --- | ---: | ---: | ---: | ---: |
| grouped-SWA off | `mla_prefill_indexed_d512` | 280 | 299.005 | 289.962 | 8.027e8 |
| grouped-SWA on | `mla_prefill_indexed_d512_grouped_swa` | 280 | 1348.412 | 1283.237 | 1.814e8 |

Route-debug rows showed why the original attempt did not hit the route: the
16K request is internally served as 4096-token chunks. The first chunk has
`max_prefill_seq_len=4096`, below the indexed-D512 minimum, while later chunks
carry `has_cached_prefix=true` because earlier chunks are already in KV. The
prototype was corrected to pass absolute `swa_token_start` and `swa_gather_start`
before accepting internal chunk-prefix rows. That made the route reachable but
did not make it fast.
