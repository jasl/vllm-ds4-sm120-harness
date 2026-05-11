## GB10 (DGX Spark 2-node mp TP=2, vLLM 5b59e2e60) — no-MTP

### random ISL=1024 OSL=512
| c | n | out tok/s | TTFT mean (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 8 | 18.33 | 1506 | 51.70 | — | — |
| 2 | 8 | 31.44 | 2894 | 58.07 | — | — |
| 4 | 8 | 48.14 | 5255 | 72.90 | — | — |

### random ISL=4096 OSL=512
| c | n | out tok/s | TTFT mean (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 4 | 15.18 | 7169 | 51.99 | — | — |
| 2 | 4 | 22.10 | 16384 | 58.63 | — | — |
| 4 | 4 | 29.23 | 24664 | 88.71 | — | — |

### random ISL=8192 OSL=512
| c | n | out tok/s | TTFT mean (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 4 | 12.77 | 13253 | 52.53 | — | — |
| 2 | 4 | 15.88 | 26020 | 75.17 | — | — |
| 4 | 4 | 18.75 | 53671 | 108.48 | — | — |

### HF mt-bench
| c | n | out tok/s | TTFT mean (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 40 | 19.13 | 245 | 51.24 | — | — |
| 2 | 40 | 33.30 | 312 | 58.59 | — | — |
| 4 | 40 | 50.62 | 367 | 73.69 | — | — |

## GB10 — MTP num_speculative_tokens=2 (vLLM 020e0c89a)

### random ISL=1024 OSL=512
| c | n | out tok/s | TTFT mean (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 8 | 25.10 | 1728 | 36.53 | 49.7 | 1.99 |
| 2 | 8 | 39.37 | 1167 | 48.38 | 51.5 | 2.03 |
| 4 | 8 | 36.43 | 1480 | 104.30 | 58.7 | 2.17 |

### random ISL=4096 OSL=512
| c | n | out tok/s | TTFT mean (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 4 | 20.69 | 6552 | 35.61 | 54.3 | 2.09 |
| 2 | 4 | 38.44 | 1378 | 48.96 | 49.6 | 1.99 |
| 4 | 4 | 27.66 | 2656 | 138.22 | 46.3 | 1.93 |

### random ISL=8192 OSL=512
| c | n | out tok/s | TTFT mean (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 4 | 18.43 | 9935 | 34.91 | 55.7 | 2.11 |
| 2 | 4 | 41.65 | 1374 | 44.82 | 59.5 | 2.19 |
| 4 | 4 | 27.00 | 2902 | 141.38 | 47.9 | 1.96 |

### HF mt-bench
| c | n | out tok/s | TTFT mean (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 40 | 29.43 | 551 | 31.14 | 66.7 | 2.33 |
| 2 | 40 | 44.12 | 520 | 41.81 | 67.3 | 2.35 |
| 4 | 40 | 57.61 | 645 | 63.04 | 66.6 | 2.33 |
