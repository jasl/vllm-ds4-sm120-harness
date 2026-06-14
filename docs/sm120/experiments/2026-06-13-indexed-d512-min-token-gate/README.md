# Indexed D512 Min-Token Gate

Status: observation
Date: 2026-06-13
Owner/context: EP-off sparse-prefill route tuning on the new rebased dev base

## Question

Can the existing indexed D512 sparse-MLA prefill route safely handle the 4K
prefill chunks that are currently blocked by the hard-coded 8192-token minimum,
without depending on FlashInfer PR3395 or external fork kernels?

## Profile

- Hardware: dual RTX PRO 6000 / SM120.
- vLLM branch/commit: `codex/ds4-sm120-epoff-sparse-prefill-dev-20260613`,
  commit `eb0fe5899`.
- Dependency stack: current dev venv, FlashInfer `0.6.12` without jit-cache on
  RTX, b12x unchanged for this test.
- TP / PP / EP: TP=2, PP=1, EP disabled.
- MTP: MTP=2.
- FP8 KV: enabled.
- Prefix cache: disabled.
- CUDA graph mode: `FULL_AND_PIECEWISE`.
- `max_model_len`: 131072.
- `max_num_seqs`: 4.
- `max_num_batched_tokens`: 4096.
- Candidate env: `VLLM_DEEPSEEK_V4_INDEXED_D512_SPLIT_PREFILL_MIN_TOKENS=4096`.

## Artifacts

- Same-commit default 8192 control:
  `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_new_dev_min_tokens_default_16k65k_c1c2/20260613_mintok_default_16k65k_c1c2_235330`.
- Same-commit 4096 candidate:
  `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_new_dev_min_tokens_4096_16k65k_c1c2/20260613_mintok_4096_16k65k_c1c2_234541`.
- 16K C=1 default/4096/0 sanity set:
  `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_new_dev_min_tokens_default_sanity/20260613_mintok_default_234058`,
  `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_new_dev_min_tokens_4096_sanity/20260613_mintok_4096_234245`,
  `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_new_dev_min_tokens_0_sanity/20260613_mintok_0_235123`.
- RTX GSM8K 5-shot limit-200 guard:
  `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_new_dev_min_tokens_4096_gsm8k5/20260613_mintok_4096_gsm8k5_000341`.

## Result

The 4096 threshold is a real RTX performance candidate for cold prefill and
does not regress the GSM8K 5-shot limit-200 guard. It is not enough to explain
the full remaining gap, because the larger C=2 bottleneck is now dominated by
multi-prefill rows blocked by `num_prefills_not_1`.

Same-commit 8192 -> 4096 A/B:

| Case | C | Input tok/s | Mean TTFT | P99 TTFT | Stage total | Sparse visits/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 16K | 1 | `7895.90 -> 8844.26` (`+12.01%`) | `2074.75 -> 1852.63 ms` (`-10.71%`) | `2094.71 -> 1870.08 ms` (`-10.72%`) | `12256.79 -> 9780.65 ms` (`-20.20%`) | `4.31e8 -> 5.57e8` (`+29.44%`) |
| 16K | 2 | `7009.20 -> 7108.03` (`+1.41%`) | `4331.03 -> 4265.10 ms` (`-1.52%`) | `4694.20 -> 4772.28 ms` (`+1.66%`) | `12256.79 -> 9780.65 ms` (`-20.20%`) | `4.31e8 -> 5.57e8` (`+29.44%`) |
| 65K | 1 | `7515.60 -> 7710.12` (`+2.59%`) | `8718.66 -> 8499.86 ms` (`-2.51%`) | `8764.40 -> 8534.40 ms` (`-2.62%`) | `33658.06 -> 31031.95 ms` (`-7.80%`) | `7.06e8 -> 7.69e8` (`+8.96%`) |
| 65K | 2 | `6725.09 -> 6770.25` (`+0.67%`) | `17482.49 -> 17355.96 ms` (`-0.72%`) | `20913.34 -> 20674.09 ms` (`-1.14%`) | `33658.06 -> 31031.95 ms` (`-7.80%`) | `7.06e8 -> 7.69e8` (`+8.96%`) |

Route attribution matches the hypothesis:

- 16K indexed D512 rows increased from `1722` to `2214`; rows blocked by
  `prefill_seq_len_below_min` fell from `574` to `82`.
- 65K indexed D512 rows increased from `9184` to `9676`; rows blocked by
  `prefill_seq_len_below_min` again fell from `574` to `82`.
- The remaining blocked rows are mostly `num_prefills_not_1`
  (`574` at 16K, `984` at 65K) plus SWA-only rows.

The `MIN_TOKENS=0` sanity moved the very short rows onto indexed D512 but did
not improve over 4096: input tok/s stayed `8808.60`, mean TTFT changed from
`1857.34 ms` to `1860.01 ms`, and stage total changed from `2672.10 ms` to
`2682.71 ms`. Treat 4096 as the safer threshold candidate.

GSM8K 5-shot limit-200 with `MIN_TOKENS=4096` passed:

- `eval_gsm8k` phase exit `0`.
- `exact_match_flexible=0.955` against floor `0.94`.
- `exact_match_strict=0.930` against floor `0.925`.
- `serve_command.sh` recorded
  `VLLM_DEEPSEEK_V4_INDEXED_D512_SPLIT_PREFILL_MIN_TOKENS=4096`.

## Interpretation

Lowering the min-token gate is a low-risk, fork-independent improvement because
it reuses the existing exact indexed D512 path and only changes which eligible
single-prefill chunks are admitted. The win is strongest for cold C=1 prefill,
which matches the route attribution.

Do not promote this as a default change yet. Before making 4096 the default,
run the RTX prefix/KV lifecycle guard, mixed arrival guard, GB10 reduced
long-C2 guard, and GB10 forum53/user-feedback guard.

The next performance target is not another min-token sweep. The dominant
remaining blocked class is `num_prefills_not_1`, so the next prototype should
distinguish true cold multi-prefill rows from cached-prefix/chunked-prefill
rows before expanding indexed D512 admission.

## Converged Promotion Matrix

Freeze the code at `eb0fe5899` for this confirmation pass. Do not add
`num_prefills_not_1` changes until this matrix has a clear promote/reject
result for `MIN_TOKENS=4096`.

Required confirmation:

1. RTX same-commit performance A/B:
   `16K / 65K / 124K x C=1/C=2`, default 8192 versus candidate 4096, stage
   timing enabled.
2. RTX correctness and lifecycle:
   GSM8K 0-shot and 5-shot limit-200, prefix/KV lifecycle, and mixed-arrival or
   prefill/decode fairness guard under candidate 4096.
3. GB10 reduced/user gates:
   reduced long-C2 and forum53 MTP2 EP-off C=2 prefix-cache guard under
   candidate 4096; run the MTP2 MoE TP soak if the GB10 run touches scheduler,
   KV admission, or MTP liveness-sensitive behavior.

Promotion bar:

- no RTX performance regression in the low-concurrency long-prefill slice;
- GSM8K stays above fixed floors;
- prefix/KV lifecycle and mixed-arrival guards do not expose correctness or
  fairness regressions;
- GB10 user-feedback gates complete without marker failures or new unexplained
  driver-health signals.

Deferred direction after this matrix:

- investigate `num_prefills_not_1` as the next sparse-prefill admission target;
- first separate true cold multi-prefill rows from cached-prefix/chunked-prefill
  rows in route context and stats;
- only then prototype a guarded indexed D512 expansion for multi-prefill rows,
  with GB10 forum53 as the early correctness gate.

## Converged Matrix Result, 2026-06-14

Do not promote `MIN_TOKENS=4096` as the default yet. The RTX performance and
correctness signal is good enough to keep the change as the leading candidate,
but the GB10 MTP2 driver-health hard gate is not clean on the current dev stack.

RTX same-commit 8192 -> 4096 A/B:

| Case | C | Input tok/s | Mean TTFT | P99 TTFT | Stage total | Sparse visits/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 16K | 1 | `7895.90 -> 8844.26` (`+12.01%`) | `2074.75 -> 1852.63 ms` (`-10.71%`) | `2094.71 -> 1870.08 ms` (`-10.72%`) | `12256.79 -> 9780.65 ms` (`-20.20%`) | `4.31e8 -> 5.57e8` (`+29.44%`) |
| 16K | 2 | `7009.20 -> 7108.03` (`+1.41%`) | `4331.03 -> 4265.10 ms` (`-1.52%`) | `4694.20 -> 4772.28 ms` (`+1.66%`) | `12256.79 -> 9780.65 ms` (`-20.20%`) | `4.31e8 -> 5.57e8` (`+29.44%`) |
| 65K | 1 | `7515.60 -> 7710.12` (`+2.59%`) | `8718.66 -> 8499.86 ms` (`-2.51%`) | `8764.40 -> 8534.40 ms` (`-2.62%`) | `33658.06 -> 31031.95 ms` (`-7.80%`) | `7.06e8 -> 7.69e8` (`+8.96%`) |
| 65K | 2 | `6725.09 -> 6770.25` (`+0.67%`) | `17482.49 -> 17355.96 ms` (`-0.72%`) | `20913.34 -> 20674.09 ms` (`-1.14%`) | `33658.06 -> 31031.95 ms` (`-7.80%`) | `7.06e8 -> 7.69e8` (`+8.96%`) |
| 124K | 1 | `6862.20 -> 6902.31` (`+0.58%`) | `-0.58%` | `-0.17%` | `64045.50 -> 61308.72 ms` (`-4.27%`) | `+4.43%` |
| 124K | 2 | `4567.64 -> 6224.90` (`+36.28%`) | `47624.51 -> 35440.75 ms` (`-25.58%`) | `58401.71 -> 41573.43 ms` (`-28.81%`) | `64045.50 -> 61308.72 ms` (`-4.27%`) | `+4.43%` |

The 124K absolute TTFT should be read with a warmup caveat: both runs logged
first-shape Triton JIT warnings. The route attribution still matches the
mechanism: at 124K, rows blocked by `prefill_seq_len_below_min` fell from `574`
to `82`, and indexed D512 rows increased by `492`.

RTX correctness and lifecycle:

- GSM8K 5-shot limit-200 passed with candidate 4096:
  `exact_match_flexible=0.955`, `exact_match_strict=0.930`.
- GSM8K 0-shot is a watch, not a hard gate for this route: two default runs
  averaged `0.9125` flexible exact match and two candidate runs averaged
  `0.9000`; strict 0-shot was effectively unusable on both sides.
- Fresh prefix-cache-only probes passed for both default and candidate. The
  combined candidate run after mixed-arrival had one `warm_b_interleaved`
  marker miss, while a fresh candidate prefix-only rerun passed. Treat this as
  a sequence-sensitive watch rather than a direct min-token regression.
- Mixed-arrival and KV lifecycle phases passed under candidate 4096.

GB10 / SM121:

| Gate | Result | Artifact |
| --- | --- | --- |
| Reduced long-C2, first run | `nomtp` and `mtp2` workload passed, but post-run driver health failed with `6` current-boot `NV_ERR_NO_MEMORY` signals. | `artifacts/main/2x_gb10_sm121/sm120_epoff_new_dev_min_tokens_4096_gb10_long_c2_reduced/20260614011834` |
| Forum53 MTP2 clean-boot attempt | Workload passed: 4 requests, 0 failures, max TTFT `123.094354s`, ITL p99 `0.171162s`, prefix hits `79872`; driver health failed with `1` worker-side `NV_ERR_NO_MEMORY`. | `artifacts/main/2x_gb10_sm121/sm120_epoff_new_dev_min_tokens_4096_gb10_forum53_mtp2_cleanboot/20260614014330` |
| Forum53 MTP2 clean-boot retry | Workload passed again: 4 requests, 0 failures, max TTFT `122.971001s`, ITL p99 `0.116106s`, prefix hits `79872`; driver health again failed with `1` worker-side `NV_ERR_NO_MEMORY`. | `artifacts/main/2x_gb10_sm121/sm120_epoff_new_dev_min_tokens_4096_gb10_forum53_mtp2_cleanboot_retry2/20260614015501` |

The GB10 driver-health failures happened during serve startup / model loading,
before user traffic. A follow-up same-commit default control showed that this
startup signal is tied to lowering the indexed D512 min-token gate, not merely
to the rebased dev stack or GB10 environment. The workload behavior itself
remains clean, but the startup driver signal blocks promotion.

Next action before any PR default change:

- keep the default gate at 8192 for now;
- change the 4096 candidate so startup/profile reservation does not select the
  indexed D512 split path for the exact `max_num_batched_tokens=4096` profile
  shape on GB10;
- do not run more `num_prefills_not_1` optimization work into this promotion
  branch until the GB10 startup driver-health question is fixed.

## GB10 Driver-Health Root-Cause Follow-Up, 2026-06-14

Question: why did forum53 pass before, while the 4096 candidate repeatedly
failed driver health?

Minimal controls:

| Run | Result | Artifact |
| --- | --- | --- |
| Rebased PR clean-boot forum53, default 8192 | Passed: driver signal count `0`; max TTFT `124.439667s`; ITL p99 `0.113827s`; prefix hits `79872`. | `artifacts/codex_ds4-sm120-min-enable-upstream-rebase-20260613/2x_gb10_sm121/rebased_pr_forum53_mtp2_epoff_c2_gmem0685_mml81920_cleanboot_20260613/20260613214002` |
| Same dev commit `eb0fe5899`, default 8192 | Passed: driver signal count `0`; max TTFT `125.799840s`; ITL p99 `0.155677s`; prefix hits `79872`. | `artifacts/main/2x_gb10_sm121/sm120_epoff_new_dev_min_tokens_default_gb10_forum53_mtp2_cleanboot_control/20260614021410` |
| Same dev commit `eb0fe5899`, candidate 4096 | Failed driver health twice with worker-side startup `NV_ERR_NO_MEMORY`, while the workload passed both times. | `artifacts/main/2x_gb10_sm121/sm120_epoff_new_dev_min_tokens_4096_gb10_forum53_mtp2_cleanboot/20260614014330`, `artifacts/main/2x_gb10_sm121/sm120_epoff_new_dev_min_tokens_4096_gb10_forum53_mtp2_cleanboot_retry2/20260614015501` |
| Same dev commit `eb0fe5899`, candidate 4096 with sparse-MLA warmup disabled | Not a workaround: the env reached the vLLM processes, but startup produced multiple worker-side `NV_ERR_NO_MEMORY` signals and left the service stuck before health. The machines were rebooted after this probe. | `artifacts/main/2x_gb10_sm121/sm120_epoff_new_dev_min_tokens_4096_gb10_forum53_mtp2_warmup_off_control/20260614022549` |

Interpretation:

- The old forum53 passes are not contradictory: default 8192 does not admit the
  4096-token startup/profile shape into indexed D512 split, while the 4096
  candidate does.
- The failure is not a request-time correctness failure. The successful 4096
  runs had 4 requests, 0 failures, no preemptions, and normal prefix hits.
- Disabling the explicit DeepSeek V4 sparse-MLA warmup did not help, so the
  likely trigger is profile/workspace/cudagraph initialization selecting the
  indexed D512 split path, not the separate kernel warmup helper.
- Promotion should require either a safer gate that excludes startup/profile
  shapes or a profile-aware reservation path that does not increase the GB10
  startup memory peak.
