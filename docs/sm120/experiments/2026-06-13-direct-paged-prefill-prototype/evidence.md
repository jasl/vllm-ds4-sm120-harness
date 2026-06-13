# Evidence

## Paired RTX Smoke

Both runs used the same development branch, harness profile, and target venv.
The only intended route difference was
`VLLM_DEEPSEEK_V4_DIRECT_PAGED_PREFILL`.

| Metric | Direct off control | Direct paged on |
| --- | ---: | ---: |
| Benchmark OK | yes | yes |
| Successful requests | 1 | 1 |
| Input tok/s | 4096.00 | 1796.49 |
| Output tok/s | 4.02 | 1.75 |
| Mean TTFT ms | 248.58 | 571.11 |
| Stats rows | 346 | 346 |
| Stage timing total ms | 2069.72 | 4584.29 |
| Effective visits/s total | `1.30643e8` | `5.89827e7` |
| Effective visits/s sparse-accumulate | `3.47008e8` | `8.19683e7` |
| Sparse accumulate ms/M effective visit | 2.88178 | 12.1998 |

## Layer Routes

| Route | Direct off rows | Direct on rows |
| --- | ---: | ---: |
| `mla_prefill_chunk` | 264 | 100 |
| `mla_prefill_direct_paged` | 0 | 164 |
| `mla_prefill_indexed_d512` | 82 | 82 |

The candidate route therefore did not silently fall back to the old path. It
converted the target non-indexed compressed rows to
`mla_prefill_direct_paged`, while SWA-only and cached-prefix warmup rows stayed
on chunk routing.

## Group Throughput

| Run | Layer type | Compress | Rows | Effective visits | Stage total ms | Sparse visits/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| control | `mla_prefill_chunk` | 128 | 120 | 28,254,720 | 579.491 | `1.87223e8` |
| control | `mla_prefill_chunk` | 4 | 126 | 98,383,152 | 869.443 | `2.12444e8` |
| control | `mla_prefill_indexed_d512` | 128 | 40 | 28,755,200 | 41.1473 | `7.20515e8` |
| control | `mla_prefill_indexed_d512` | 4 | 42 | 110,100,480 | 94.1067 | `1.18449e9` |
| direct on | `mla_prefill_direct_paged` | 128 | 80 | 28,248,640 | 712.350 | `3.96556e7` |
| direct on | `mla_prefill_direct_paged` | 4 | 84 | 98,375,424 | 2407.410 | `4.08636e7` |
| direct on | `mla_prefill_indexed_d512` | 128 | 40 | 28,755,200 | 41.1586 | `7.20596e8` |
| direct on | `mla_prefill_indexed_d512` | 4 | 42 | 110,100,480 | 93.6862 | `1.18982e9` |

The comparison isolates the kernel shape issue. The indexed-D512 rows remain
healthy in the direct-on run, while only the new direct-paged rows are slow.

## Stage Breakdown

| Run | combine_indices | gather_compressed_kv | gather_swa_kv | sparse_accumulate |
| --- | ---: | ---: | ---: | ---: |
| control | 43.8926 ms / 2.12% | 797.461 ms / 38.53% | 449.152 ms / 21.70% | 779.214 ms / 37.65% |
| direct on | 14.7091 ms / 0.32% | 797.019 ms / 17.39% | 473.802 ms / 10.34% | 3298.76 ms / 71.96% |

The direct route reduces combine work, but total runtime increases because the
new sparse accumulate path is too slow.
