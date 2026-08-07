# Baseline of record — 2026-08-08, tree `4ebd1fb698`

Supersedes [`2026-08-07-baseline-of-record-db8f836e8b.md`](2026-08-07-baseline-of-record-db8f836e8b.md),
which was one wave behind the branch. `4ebd1fb698` is the current head of
**both** `codex/ds4-sm120-min-enable` and `ds4-sm120-preview-dev` (SHA-equal on
the remote), and adds to the previous baseline: upstream merge #2
(fastsafetensors), the C128A stride GPU repro test, and four fixes — drafter
layout-cache invalidation `264942766e`, expert-map gather bounds, the SM120
sparse-MLA gate version-half, and `num_global_experts` on the non-pad-aware
`moe_sum` launches.

All four node trees verified at `4ebd1fb698` with clean tracked state before
the run; results dir `/home/jasl/tmp/baseline_20260808_4ebd1fb698/` on `.116`.

## Environment

- Model `deepseek-ai/DeepSeek-V4-Flash-0731`, 2× GB10 TP=2 (`.116` head /
  `.119` worker), fp8 KV, prefix cache on, util 0.85, mnbt 8192.
- FlashInfer 0.6.16 (python + cubin + jit-cache wheel);
  `apache-tvm-ffi==0.1.11` + `tilelang==0.1.12`.
- **Two different serve shapes**, which the previous doc did not distinguish:
  benchy runs the pinned standard at **mml 49152**; the correctness gates run at
  **mml 131072**. Do not compare a benchy number to a gate-serve number.

## Perf — llama-benchy pinned standard (mml 49152, DSpark spec on)

| depth | pp2048 t/s | tg128 mean t/s | tg128 peak t/s |
|---|---|---|---|
| d8192 | 1406.89 ± 16.32 | 36.98 ± 0.86 | 46.33 ± 3.09 |
| d16384 | 1333.16 ± 0.91 | 38.81 ± 1.18 | 52.67 ± 2.05 |
| d32768 | 1218.93 ± 8.81 | 38.65 ± 3.74 | 48.67 ± 1.70 |

Context-phase rows from the same run, for completeness:

| depth | ctx_pp t/s | ctx_tg mean | ctx_tg peak | e2e_ttft (ms) |
|---|---|---|---|---|
| d8192 | 1800.31 ± 16.17 | 34.85 ± 1.26 | 48.67 ± 5.25 | 4552.21 ± 41.00 |
| d16384 | 1813.17 ± 7.72 | 38.76 ± 1.90 | 49.00 ± 2.16 | 9039.68 ± 38.34 |
| d32768 | 1739.03 ± 1.07 | 36.70 ± 3.29 | 46.00 ± 4.90 | 18847.45 ± 11.58 |

**⚠ Column-label correction.** The previous doc labelled the two tg128 columns
`tg128 base` and `tg128 spec (dspark5)`, as if they were two arms. They are
not: both baselines start exactly **one** serve, and the pinned standard has
DSpark spec on throughout. The columns are the **mean** and **peak** t/s of that
single spec arm. There is no no-spec arm in this suite, and any past
base-vs-spec reasoning drawn from those two columns is comparing a mean to a
peak.

### Versus the previous baseline — no resolvable change

| metric @ d8192 / d16384 / d32768 | db8f836e8b | 4ebd1fb698 |
|---|---|---|
| pp2048 t/s | 1432.27 / 1364.01 / 1225.19 | 1406.89 / 1333.16 / 1218.93 |
| tg128 mean | 46.31 / 38.63 / 44.64 | 36.98 / 38.81 / 38.65 |
| tg128 peak | 54.33 / 47.67 / 55.33 | 46.33 / 52.67 / 48.67 |

pp2048 moves −1.8% / −2.3% / −0.5%, at or below what benchy can resolve.
tg128 moves −20% / +0.5% / −13% on the mean — **mixed in sign, which is the
signature of noise, not regression.** The empirical envelope from the 08-03
repeated-measures set (V1, tg128 @ d8192, n=10 blocks) is mean 41.0, sd 4.1,
observed range [32.48, 46.03]: today's 36.98 sits at −0.97 sd and the previous
baseline's 46.31 at +1.28 sd. The apparent 20% drop is a top-of-envelope sample
being compared with a below-median one. pp2048 is far tighter in that same set
(mean 1420.9, sd 8.6), so its −1.8% is worth a repeat before any claim, but it
is not actionable on one run.

## Correctness (mml 131072, DSpark nst=5 probabilistic)

| gate | result |
|---|---|
| issue19 instruction-following (JSON-only) | **PASS** |
| arthur c=12, ×3 on one serve | **19 / 22 / 21** (mean 20.67) |
| arthur c=1 | **2/2** |
| GSM8K 8-shot strict | **0.9333** ± 0.0069 |
| GSM8K 8-shot flexible | **0.9371** ± 0.0067 |
| multi-needle @ ~42K (8 needles + 8 distractors, ×3) | **24/24**, 0 leaks |
| multi-needle @ ~80K (×3) | **24/24**, 0 leaks |
| scheduler preemptions during the gate serve | **0** |

GSM8K is −1.06 pp strict / −1.13 pp flexible against the previous baseline,
which is exactly the documented single-run spread (~1.1 pp). Multi-needle is
48/48 with zero leaks, identical to the previous baseline.

**arthur c=12 is recorded as a band, not a row.** The previous baseline logged a
single 23/24, which is the top of the range; three samples on one serve give
19/22/21. Treat 23/24 and 19/24 as the same result. Note also that the band is
*tight within a serve and moves across serves* — a separate V1 serve on this
same tree returned 22/22/22 (see the prefix-reuse factorial), so serve instance
is a real source of variance for V1 too, not only for the V2 runner.

## Known open items carried into this baseline

- The V1/V2 runner recall gap is **not** settled; see
  [`2026-08-07-v2-runner-recall-reclassification/`](2026-08-07-v2-runner-recall-reclassification/README.md).
  With V1 now measured on this tree at 19/22/21 and 22/22/22, the earlier "V2 is
  3.9 needles behind (p=0.024)" used a V1 reference (22.25) assembled from four
  heterogeneous runs and is very likely overstated.
- The reason *any* runner loses needles at c=12 is open. Capacity and
  preemption are excluded (0 preemptions, KV peak 36.2%). Requests do queue at
  admission (waiting peaks at 11 of 12) but are never preempted.
- Drafter step-1 NaN rows on `rows>0` in mixed batches: output-correct, costs
  draft slots; ragged first-pass slot-mapping audit still pending.
- TP=4 has no c=12 band on this tree.
