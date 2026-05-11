# MTP acceptance summary — sm120_mtp2_isl_sweep

| shape | accept_rate % | accept_len | pos0 % | pos1 % | drafts | accepted | TPOT ms |
|---|---|---|---|---|---|---|---|
| ? c=1 (bench_hf_mt_bench) | 68.8 | 2.38 | 85.6 | 52.0 | 6393 | 8797 | 6.26 |
| ? c=2 (bench_hf_mt_bench) | 68.6 | 2.37 | 85.0 | 52.2 | 6208 | 8520 | 7.92 |
| ? c=4 (bench_hf_mt_bench) | 68.7 | 2.37 | 84.7 | 52.6 | 6340 | 8709 | 13.25 |
| ? c=8 (bench_hf_mt_bench) | 69.0 | 2.38 | 85.3 | 52.7 | 6422 | 8863 | 15.57 |
| ? c=16 (bench_hf_mt_bench) | 68.0 | 2.36 | 84.8 | 51.1 | 6308 | 8572 | 22.94 |
| ? c=24 (bench_hf_mt_bench) | 67.6 | 2.35 | 84.3 | 51.0 | 6262 | 8470 | 28.38 |
| ? c=1 (bench_random_isl1024_osl512) | 52.4 | 2.05 | 73.5 | 31.2 | 6000 | 6286 | 7.37 |
| ? c=2 (bench_random_isl1024_osl512) | 58.5 | 2.17 | 78.6 | 38.4 | 5661 | 6620 | 9.23 |
| ? c=4 (bench_random_isl1024_osl512) | 54.2 | 2.08 | 74.1 | 34.2 | 5895 | 6386 | 17.16 |
| ? c=8 (bench_random_isl1024_osl512) | 57.3 | 2.15 | 77.3 | 37.2 | 5723 | 6557 | 20.47 |
| ? c=16 (bench_random_isl1024_osl512) | 59.3 | 2.19 | 78.3 | 40.3 | 5620 | 6667 | 27.72 |
| ? c=24 (bench_random_isl1024_osl512) | 56.6 | 2.13 | 76.3 | 36.9 | 5766 | 6527 | 36.52 |
| ? c=1 (bench_random_isl4096_osl512) | 49.7 | 1.99 | 71.0 | 28.3 | 6161 | 6119 | 7.70 |
| ? c=2 (bench_random_isl4096_osl512) | 49.5 | 1.99 | 71.2 | 27.8 | 6172 | 6108 | 12.26 |
| ? c=4 (bench_random_isl4096_osl512) | 50.0 | 2.00 | 72.5 | 27.5 | 6137 | 6140 | 24.41 |
| ? c=8 (bench_random_isl4096_osl512) | 52.8 | 2.06 | 72.8 | 32.7 | 5976 | 6305 | 34.87 |
| ? c=16 (bench_random_isl4096_osl512) | 52.1 | 2.04 | 73.7 | 30.6 | 6012 | 6271 | 53.45 |
| ? c=24 (bench_random_isl4096_osl512) | 51.7 | 2.03 | 72.0 | 31.5 | 6035 | 6244 | 67.72 |
| ? c=1 (bench_random_isl8192_osl512) | 48.3 | 1.97 | 71.2 | 25.4 | 6248 | 6031 | 7.80 |
| ? c=2 (bench_random_isl8192_osl512) | 49.2 | 1.98 | 70.8 | 27.6 | 6193 | 6091 | 15.55 |
| ? c=4 (bench_random_isl8192_osl512) | 47.7 | 1.95 | 71.1 | 24.3 | 6283 | 5992 | 33.33 |
| ? c=8 (bench_random_isl8192_osl512) | 49.3 | 1.99 | 71.8 | 26.8 | 6182 | 6096 | 54.46 |
| ? c=16 (bench_random_isl8192_osl512) | 47.8 | 1.96 | 69.5 | 26.2 | 6277 | 6006 | 56.26 |
| ? c=24 (bench_random_isl8192_osl512) | 49.6 | 1.99 | 71.1 | 28.1 | 6166 | 6118 | 54.09 |

_processed 24 runs, 24 with MTP spec metrics_

## Observations

- `pos0 %` is the share of first-position draft tokens accepted: high values (>70 %) suggest the draft head is well-tuned for the workload; low values (<50 %) flag a draft-quality ceiling.
- `pos1 %` is the second-position acceptance: a steep drop from pos0 to pos1 is the typical MTP pattern (the draft has less context to work with). If pos1 stays >50 %, raising `num_speculative_tokens` to 3 may be worth trying.
- `accept_len` ≈ 1 + (sum of per-position fractions) when `num_speculative_tokens=2`. Values close to 2.0 mean MTP is fully amortising the draft cost; values <1.7 mean MTP overhead is eating into the gain and the no-MTP path may be competitive.
