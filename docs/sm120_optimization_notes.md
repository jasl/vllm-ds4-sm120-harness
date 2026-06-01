# SM120 Optimization Notes

These notes are the current working assumptions for DeepSeek V4 SM120
performance work. They are intentionally separate from historical baseline
reports so later tuning does not accidentally inherit outdated architecture
assumptions.

For the current short-form profiling and experiment sequence across SM120 and
SM121, start with `docs/sm12x_best_effort_profiling_plan.md`.

## Hardware Assumptions

- Target hardware: NVIDIA RTX PRO 6000 Blackwell Workstation Edition,
  SM120 / compute capability 12.0.
- Memory subsystem: GDDR7. Do not describe SM120 workstation results as HBM
  bandwidth results.
- Do not assume SM100/B200/B300-only paths are portable to SM120. In
  particular, do not base a vLLM optimization on TMEM, `tcgen05`, or TMA unless
  it has been independently verified on the SM120 target and is guarded behind
  the correct architecture checks.
- Primary product target: single-stream and small-concurrency interactive
  latency. Treat concurrency 24 or 32 as the practical upper bound for this
  workstream; larger concurrency is a regression check, not the first
  optimization target.

## Current Bottleneck Shape

The active long-context target is 128K-130K context reliability and TTFT on the
dual-SM120 development setup, with the expectation that validated low-level
improvements should scale to four-card users even though four-card hardware is
not currently available for local validation.

Measured work so far points at the sparse-MLA indexer / FP8 MQA logits path,
not at a simple GDDR7 bandwidth ceiling:

- The large step change came from avoiding the slow fallback around FP8 MQA
  logits and top-k. The 127K C=1 cold-prefill mean moved from roughly 60.8 s to
  the high-36 s range after the direct Triton logits plus row-top-k path, then
  into the high-20 s range for the current 124K C=1 repeat gate after the
  retained FP8 MQA logits tile updates.
- Widening the direct FP8 MQA logits Triton tile from `BLOCK_N=64` to
  `BLOCK_N=128` was a small positive step and is currently kept.
- NCU observations for late-context FP8 MQA logits show register / occupancy /
  eligible-warp / long-scoreboard pressure. Treat memory throughput counters as
  GDDR7 memory-subsystem evidence, not HBM evidence.
- Single-run long-context matrices are sensitive to runtime and Triton compile
  cache state. A follow-up same-service `autotune_on` first/second matrix did
  not show the second run getting faster, but both runs were materially faster
  than an earlier one-shot matrix in the same session. Treat repeat-count-1
  latency as a development signal, not a publishable number.

## Successful Optimization Notes

### Hybrid Prefix-Cache Tail Blocks

User-reported prefix-cache stress showed a mid-filler hit-rate cliff around
the 400-800 filler-word shape on TP=2, MTP=1, FP8 KV, prefix cache enabled,
block size 256, and `FULL_AND_PIECEWISE`. The active-prefix protection logic
was already present after the rebase, so the remaining loss came from
`HybridKVCacheCoordinator.cache_blocks()` flooring `num_computed_tokens` to
`lcm_block_size` before writing cached blocks. That floor dropped complete
tail blocks that a later chat turn could use to complete a future
LCM-aligned hit.

The retained fix keeps lookup semantics unchanged: hybrid
`find_longest_cache_hit()` still returns only LCM-aligned hits, and SWA
managers still receive `alignment_tokens` for cache masking. Only the cache
write side now keeps complete tail blocks instead of permanently discarding
them.

Same-host prefix-cache filler sweep, TP=2, MTP=1, FP8 KV, prefix cache
enabled, block size 256, `FULL_AND_PIECEWISE`, 3 trials per filler:

| Filler Words | Before Concurrent Hit Rate | After Concurrent Hit Rate | Delta |
| ---: | ---: | ---: | ---: |
| 100 | 0.000 | 0.137 | +13.67 pp |
| 400 | 0.344 | 0.466 | +12.17 pp |
| 800 | 0.654 | 0.727 | +7.28 pp |
| 1600 | 0.766 | 0.808 | +4.25 pp |
| 3200 | 0.901 | 0.927 | +2.57 pp |

All post-fix sweep points had zero stress failures. The 800-filler A/B with
5 trials confirmed the same direction: keeping `alignment_tokens` but removing
only the LCM floor produced concurrent hit-rate mean `0.7269`, while removing
both floor and alignment was `0.7302`. Therefore the retained change is the
narrower no-floor fix, not a broad mask bypass.

Artifact labels:
`post_recovery_99b82a_prefix_filler_sweep_default`,
`ab_no_lcm_floor_keep_alignment_99b82a`,
`ab_no_lcm_cache_write_99b82a`, and
`post_fix_no_lcm_floor_prefix_filler_sweep`.

After adding the prefix-cache sweep to the user-feedback matrix, the same
post-fix profile was rerun with 5 trials per filler. All points passed with
zero failures and the service exited cleanly:

| Filler Words | Trials | Failures | Solo Hit Rate | Concurrent Hit Rate |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 5 | 0 | 0.2923 | 0.2861 |
| 400 | 5 | 0 | 0.5284 | 0.6100 |
| 800 | 5 | 0 | 0.7634 | 0.8236 |
| 1600 | 5 | 0 | 0.8261 | 0.8691 |
| 3200 | 5 | 0 | 0.8917 | 0.9593 |

Artifact label:
`post_fix_user_feedback_prefix_cache_matrix/20260523_post_fix_user_feedback_prefix_cache_matrix`.

### Historical Mixed Decode / Long Prefill 3/4 Cap

The user-reported multi-long-context cliff is now understood as a narrower
scheduler shape: one request has already reached decode, then another long
prefill is admitted behind it. The paged-MQA decode kernel is not the only
suspect in that shape; the active decoder can be starved by the following long
prefill chunks.

The initial scheduler change was intentionally internal and conservative. It
does not add a public knob. When chunked prefill is enabled, at least one
decode request has already been scheduled in the current step, and the next
request still has more than one full scheduling step of prefill remaining, the
long-prefill chunk is capped at 3/4 of `max_num_batched_tokens`. C=1, pure
prefill, pure decode, and short prefills that fit within one normal step are
not capped.

Mixed-arrival gate, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2, repeat count 3:

| Case | Variant | Primary TTFT | Secondary TTFT | Decode Min | Fairness | ITL P95 | ITL P99 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| decode then 59K long | baseline | 11.036 s | 12.882 s | 3.821 tok/s | 0.029 | 0.955 s | 1.048 s |
| decode then 59K long | 3/4 cap | 10.957 s | 11.566 s | 5.822 tok/s | 0.044 | 0.655 s | 0.835 s |
| 124K long then short | baseline | 28.436 s | 27.124 s | 39.358 tok/s | 0.448 | 0.031 s | 0.525 s |
| 124K long then short | 3/4 cap | 28.441 s | 26.964 s | 54.715 tok/s | 0.585 | 0.032 s | 0.524 s |

Artifact labels:
`codex_mixed_arrival_baseline_20260521` and
`codex_mixed_arrival_decode_prefill_cap_3q_20260521`.

Fixed 59K/124K C=1/C=2 cold gate, repeat count 3:

| Prompt Shape | C | Baseline TTFT | 3/4 Cap TTFT | Baseline ITL P95 | 3/4 Cap ITL P95 | Baseline ITL P99 | 3/4 Cap ITL P99 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 59K synthetic | 1 | 11.686 s | 11.013 s | 0.021 s | 0.021 s | 0.024 s | 0.024 s |
| 59K synthetic | 2 | 17.798 s | 18.020 s | 1.014 s | 0.850 s | 1.152 s | 0.889 s |
| 124K synthetic | 1 | 30.522 s | 28.420 s | 0.027 s | 0.028 s | 0.029 s | 0.029 s |
| 124K synthetic | 2 | 44.607 s | 44.184 s | 1.494 s | 0.911 s | 1.593 s | 0.985 s |

Artifact labels:
`codex_regression_recheck_20260521064045` and
`codex_mixed_arrival_decode_prefill_cap_3q_20260521`.

Short-context and correctness gates on the retained 3/4 candidate:

| Gate | Result |
| --- | --- |
| Short C=4 streaming-pressure smoke, artifact `codex_decode_prefill_cap_3q_final_gate_20260521/short_c4_round2` | 8/8 successful, max TTFT 6.421 s, max elapsed 6.786 s |
| GSM8K 5-shot limit-50, artifact `codex_decode_prefill_cap_3q_final_gate_20260521/gsm8k_limit50` | `exact_match_flexible=0.960` versus baseline `0.940`; compare passed |

Decision at the time: this was useful as the first narrow scheduler fix, but it
is now historical. Later gates showed the slow-request tail needed a tighter
decode-overlap cap for 124K-class and issue #8-like C=2 shapes.

### Very-Long Mixed Decode / Prefill Half Cap

The retained 3/4 mixed decode/prefill cap still left a visible slow-request
tail at 124K C=2. A narrower follow-up keeps the 3/4 cap for ordinary long
prefills but uses a 1/2 cap only when the remaining prefill is more than 16
full scheduler steps. With the current 4096-token scheduler profile, that
means 59K-class prompts stay on the 3/4 path while 124K-class prompts get a
tighter chunk during the earliest, highest-interference prefill steps.

Fixed-gate A/B, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2, prewarm enabled, repeat count 3:

| Prompt Shape | C | Metric | 3/4 Cap | Very-Long 1/2 Cap | Delta |
| --- | ---: | --- | ---: | ---: | ---: |
| 59K synthetic | 1 | TTFT mean | 11.991 s | 12.025 s | +0.3% |
| 59K synthetic | 2 | TTFT mean | 18.692 s | 18.746 s | +0.3% |
| 59K synthetic | 2 | Decode min | 5.237 tok/s | 5.197 tok/s | -0.8% |
| 59K synthetic | 2 | ITL P99 | 0.750 s | 0.753 s | +0.3% |
| 124K synthetic | 1 | TTFT mean | 30.796 s | 30.911 s | +0.4% |
| 124K synthetic | 2 | TTFT mean | 47.167 s | 47.408 s | +0.5% |
| 124K synthetic | 2 | TTFT max | 62.838 s | 63.211 s | +0.6% |
| 124K synthetic | 2 | Decode min | 3.988 tok/s | 6.137 tok/s | +53.9% |
| 124K synthetic | 2 | ITL P95 | 0.800 s | 0.496 s | -38.0% |
| 124K synthetic | 2 | ITL P99 | 0.825 s | 0.510 s | -38.2% |

Short-context and correctness gates on the follow-up candidate:

| Gate | Result |
| --- | --- |
| Short HF/MT-Bench C=1/2/4, 16 prompts, artifact `codex_very_long_prefill_half_cap_final_gate_20260521/mtp/bench_hf_mt_bench` | all 16/16 successful; output tok/s `147.76 / 230.34 / 313.66` |
| GSM8K 5-shot limit-50, C=4, artifact `codex_very_long_prefill_half_cap_gsm8k_c4_20260521/mtp/eval_gsm8k` | `exact_match_flexible=0.960`, `exact_match_strict=0.960` |
| GSM8K 5-shot limit-200, C=4, artifact `codex_very_long_prefill_half_cap_gsm8k_limit200_20260521/mtp/eval_gsm8k` | `exact_match_flexible=0.950`, `exact_match_strict=0.940`; same-protocol 3/4 cap baseline `0.940 / 0.930` |

Decision at the time: keep this follow-up. It improved the 124K C=2
slow-request tail without moving 59K or C=1 materially and without adding a
public scheduler knob. It is now superseded by the issue #8 decode-concurrency
guard below, which uses a tighter decode-overlap cap and keeps the broader
waiting-request behavior conservative. The result is still dual-card
128K-class evidence; repeat on four-card hardware before making longer-context
commitments.

### Issue #8 Decode-Concurrency 1/8 Decode-Overlap Cap

The [jasl/vllm issue #8](https://github.com/jasl/vllm/issues/8) and the
related NVIDIA forum reports narrowed the failure shape further: the pure
warm-cache C=2 decode path is healthy, but a cold C=2 run can let one request
emit its first token and then starve while the paired long prefill continues.
That matches the user-visible symptom better than a pure paged-MQA decode
kernel cliff.

Current retained policy:

- If a decode request has already been scheduled in the current step and the
  following request is still in prefill, cap ordinary long prefill chunks to
  1/4 of `max_num_batched_tokens`.
- If that remaining prefill is more than four full scheduler steps, cap it to
  1/8 of `max_num_batched_tokens`.
- If no decode has been scheduled and the goal is only to leave room for
  waiting requests, keep the less aggressive 1/2 or 3/4 caps.
- Do not expose a public scheduling knob; this is an internal latency/fairness
  policy for mixed decode+long-prefill steps.

Issue #8 local proxy, TP=2, no-MTP, prefix cache enabled, `max_num_seqs=2`,
`max_num_batched_tokens=4096`, FULL_AND_PIECEWISE graph, 124K synthetic prompt,
C=1/C=2, cold+warm, `max_tokens=128`:

| Candidate | Cold C=2 TTFT Mean | Cold C=2 TTFT Max | Cold C=2 Elapsed Mean | Slow Req Decode | Decode Min/Max | ITL P99 | Warm C=2 Decode Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Previous 1/2 very-long cap, artifact `codex_issue8_decode_concurrency_proxy_20260522` | 61.517 s | 83.697 s | 84.730 s | 1.566 tok/s | 0.039 | 1.698 s | 37.095 tok/s |
| 1/4 decode-overlap experiment, artifact `codex_issue8_decode_prefill_cap_1q_20260522` | 51.717 s | 72.607 s | 66.019 s | 2.600 tok/s | 0.062 | 0.531 s | 39.268 tok/s |
| Retained 1/8 decode-overlap cap, artifact `codex_issue8_decode_prefill_cap_1eighth_20260522` | 55.368 s | 79.868 s | 65.412 s | 3.804 tok/s | 0.092 | 0.298 s | 39.264 tok/s |

Decision: keep the 1/8 decode-overlap cap for the Dev branch. It gives the
best slow-request decode and ITL result in the direct issue #8 proxy while
leaving warm-cache C=2 decode essentially unchanged. The tradeoff is that the
second cold request's TTFT is a little worse than the 1/4 experiment; this is
accepted because the user-facing complaint is the already-started stream
stalling after first token. Revalidate with the local quality profile before
PR-branch promotion, and treat >128K / four-card behavior as an external gate.

Follow-up short-context and correctness checks:

| Gate | Result |
| --- | --- |
| Short MTP `bench_hf_mt_bench`, artifact `codex_issue8_1eighth_short_gsm8k_smoke_20260522/20260522101340` | C=1/2/4 output throughput `130.43 / 223.72 / 343.61` tok/s |
| GSM8K 5-shot limit-50, same artifact, MTP C=4 | `exact_match_flexible=0.920`, `exact_match_strict=0.920`; treated as too small/noisy for promotion |
| GSM8K 5-shot limit-200, artifact `codex_issue8_1eighth_gsm8k_limit200_repeat_20260522/20260522101953`, MTP C=4 | `exact_match_flexible=0.940`, `exact_match_strict=0.915`; flexible matches the fixed 0.94 floor, strict is an observation to keep monitoring |
| GSM8K 5-shot limit-200, artifact `codex_issue8_1eighth_gsm8k_isolation_20260522/20260522102518`, no-MTP C=4 | `exact_match_flexible=0.965`, `exact_match_strict=0.950` |
| GSM8K 5-shot limit-200, same isolation artifact, MTP C=1 | `exact_match_flexible=0.960`, `exact_match_strict=0.945` |

Interpretation: the retained scheduler policy does not show a general
short-context or GSM8K correctness regression. The weaker MTP C=4 strict score
appears tied to the MTP concurrent eval shape rather than the base model path;
keep reporting both the deterministic C=1 MTP accuracy gate and the C=4 stress
observation until the MTP concurrent correctness variance is better understood.

Performance/quality refresh after the prewarm wiring fix:

### GB10 Long C=2 Pressure Stall Reproduction

The first bounded GB10 pressure gate after the 128K-class MTP startup smoke
found a stronger failure shape than the earlier short deterministic and
single-long-context probes. The service does not crash and the driver remains
clean, but the long C=2 streaming-pressure phase can enter a high-SM,
no-token-progress state.

Common profile for both runs:

- two-node GB10 / SM121, TP=2, PP=1, EP enabled, FP8 KV, prefix cache disabled;
- `max_model_len=131072`, `max_num_batched_tokens=4176`,
  `max_num_seqs=2`, block size 256;
- `FULL_AND_PIECEWISE` graph mode remained enabled;
- matrix cases were `short_c2`, issue-7-like `5K_c2`, then `long_c2`.

MTP=2 pressure artifact label:
`20260601_gb10_mtp2_bounded_pressure/streaming_pressure_matrix_c2`.

| Signal | Result |
| --- | ---: |
| Successful requests before stop | 12 |
| Prefill tokens delta | 210,324 |
| Decode tokens delta | 399 |
| Runtime avg prefill throughput | 1,314.21 tok/s |
| Runtime avg decode throughput | 2.49 tok/s |
| Max running / waiting requests | 2 / 1 |
| Max KV usage from metrics | 39.42% |
| GPU util avg / max | 90.96% / 96.0% |
| Runtime CUDA/NCCL/driver/engine errors | 0 |

The MTP run reached `long_c2` after the first 12 requests, then stayed at
`running=2`, `waiting=0`, with prompt/decode/spec-decode counters flat while
GPU SM utilization remained around 95-96%. Interrupting the client released the
requests and returned the server to idle. Kernel-driver health logs showed no
Xid, UVM, launch-failure, or GPU-lost signal.

No-MTP control artifact label:
`20260601_gb10_nomtp_bounded_pressure_control/streaming_pressure_matrix_c2`.

| Signal | Result |
| --- | ---: |
| Successful requests before stop | 12 |
| Prefill tokens delta | 210,324 |
| Decode tokens delta | 388 |
| Runtime avg prefill throughput | 1,314.45 tok/s |
| Runtime avg decode throughput | 2.42 tok/s |
| Max running / waiting requests | 2 / 1 |
| Max KV usage from metrics | 30.23% |
| GPU util avg / max | 91.87% / 96.0% |
| Runtime CUDA/NCCL/driver/engine errors | 0 |

The no-MTP control reproduced the same high-SM, no-token-progress pattern in
the `long_c2` phase. This moves the root-cause hypothesis away from
speculative decoding alone and toward the long C=2 scheduler/attention
interaction. MTP is still relevant as extra overhead and capacity pressure, but
the base no-MTP path is sufficient to reproduce the stall.

No-MTP `max_num_batched_tokens=2048` single-`long_c2` probe artifact label:
`20260601_gb10_nomtp_longc2_chunk2048_probe/streaming_pressure_longc2`.

| Signal | Result |
| --- | ---: |
| Max running / waiting requests | 2 / 0 |
| Phase prefill tokens delta | 0 |
| Phase decode tokens delta | 0 |
| Runtime avg prefill throughput | 0.0 tok/s |
| Runtime avg decode throughput | 0.0 tok/s |
| Max KV usage from metrics | 17.58% |
| GPU util max | 96.0% |
| Runtime CUDA/NCCL/driver/engine errors | 0 |

This smaller-chunk single-pair probe stalled earlier than the 4176-token
matrix run, immediately after first seeing the long C=2 shape. It weakens the
hypothesis that the issue is only an oversized prefill chunk. The next trace
should therefore capture the first long-C=2 sparse-MLA prefill window, not only
late decode.

Follow-up Nsys window artifact label:
`20260601_gb10_nomtp_longc2_nsys_chunk2048/serve_20260601071049`.

This run launched both GB10 ranks under dormant Nsys sessions, started capture
only for the reduced `long_c2` request window, and stopped capture after the
same high-SM/no-token-progress state was observed. Both ranks showed the same
kernel mix:

| Rank | Top Kernel | Time Share | Total Time | Instances | Avg |
| --- | --- | ---: | ---: | ---: | ---: |
| head | `_accumulate_indexed_attention_chunk_multihead_kernel` | 35.1% | 21.557 s | 33,368 | 0.646 ms |
| worker | `_accumulate_indexed_attention_chunk_multihead_kernel` | 35.1% | 23.061 s | 35,592 | 0.648 ms |
| head | MXFP4 Marlin MoE | 18.2% | 11.136 s | 2,658 | 4.190 ms |
| worker | MXFP4 Marlin MoE | 17.8% | 11.666 s | 2,826 | 4.128 ms |
| head | `_fp8_mqa_logits_kernel` | 7.6% | 4.680 s | 649 | 7.211 ms |
| worker | `_fp8_mqa_logits_kernel` | 8.0% | 5.269 s | 690 | 7.636 ms |
| head | NCCL bf16 all-reduce | 6.4% | 3.898 s | 2,690 | 1.449 ms |
| worker | NCCL bf16 all-reduce | 7.0% | 4.601 s | 2,859 | 1.609 ms |

Interpretation: the stall window is not an idle scheduler wait. The GPUs are
actively executing a repeated sparse-MLA prefill/attention + MoE + collective
sequence while vLLM-visible prompt/decode counters do not advance. The next
kernel experiment should focus on reducing or restructuring
`_accumulate_indexed_attention_chunk_multihead_kernel` work for the GB10
long-C=2 shape before revisiting MTP-specific changes.

Rejected follow-up:

| Experiment | Artifact | Result | Decision |
| --- | --- | --- | --- |
| Force `VLLM_TRITON_MLA_SPARSE_TOPK_CHUNK_SIZE=128` for the same no-MTP long-C=2 shape | `gb10_topk128_probe/2x_gb10_sm121/streaming_pressure_longc2` | Both requests timed out at `120.433 s` with no TTFT. Runtime sampling saw `prefill tokens delta = 0`, `decode tokens delta = 0`, `max running = 2`, `max waiting = 0`, and KV usage around `16.41%`. | reject: simply halving the per-kernel candidate chunk does not restore progress |
| Temporary `PREFILL_CHUNK_SIZE=1` vLLM experiment branch | `gb10_prefillchunk1_probe/2x_gb10_sm121/streaming_pressure_longc2` | One request completed with `TTFT=220.354 s`, `elapsed=243.355 s`, `prompt_tokens=100079`, and ITL p99 `1.874 s`; the paired request timed out with no chunks. Runtime sampling saw `prefill tokens delta = 100079`, `decode tokens delta = 39`, `max running = 2`, `max waiting = 0`, and KV usage around `20.01%`. | reject for retention: single-request slicing changes the failure from no-progress to slow unfair progress, but still does not meet long-C=2 fairness or latency needs |

Conservative control:

| Experiment | Artifact | Result | Decision |
| --- | --- | --- | --- |
| Restore normal vLLM code and set `max_num_seqs=1` for the same two-client long-C=2 request shape | `gb10_maxseq1_control/2x_gb10_sm121/streaming_pressure_longc2` | Both requests completed: `failures=0`, max TTFT `238.383 s`, max elapsed `240.536 s`, ITL p95 `0.066 s`, ITL p99 `0.080 s`, with `max running = 1` and `max waiting = 1`. | accept as a GB10 best-effort safety profile for 100K-class long-prefill concurrency until sparse-MLA prefill can be fixed |
| Same conservative control with MTP=2 enabled | `gb10_mtp2_maxseq1_control/streaming_pressure_longc2` | Both requests completed: `failures=0`, max TTFT `231.239 s`, max elapsed `232.700 s`, ITL p95 `0.082 s`, ITL p99 `0.086 s`, with `max running = 1`, `max waiting = 1`, zero preemptions, and zero CUDA/NCCL/driver/engine error signals. | accept as evidence that MTP=2 can run under the GB10 conservative safety profile, but this is an availability profile, not a throughput fix |

Next debugging direction:

- build a reduced sparse-MLA prefill microbench or endpoint experiment that
  targets the `long_c2` shape seen in the Nsys window;
- use NCU on `_accumulate_indexed_attention_chunk_multihead_kernel` for this
  shape if counter permissions are available on the target node;
- keep `max_num_seqs=1` as the GB10 conservative long-context safety profile
  for 100K-class C=2 user-facing tests, and only relax it after a kernel-level
  fix shows both requests can make progress with low ITL tail;
- separate the cases where the server makes slow progress from cases where
  counters stop entirely;
- only after that, evaluate whether the fix belongs in scheduler chunking,
  sparse-MLA prefill, FP8 MQA logits, or graph replay shape handling.

The first full local-quality attempt
`codex_issue8_1eighth_local_quality_refresh_20260522/20260522103723` was stopped
after full acceptance generation at temperature 1.0 produced subjective
response-length failures unrelated to the scheduler path. Use it only as
evidence that full acceptance should be separated from performance promotion.

The performance-focused local refresh
`codex_issue8_1eighth_perf_quality_refresh_20260522/20260522111056` passed every
selected phase except `long_context_latency_matrix`; that failure was caused by
the harness not passing `B200_VLLM_VENV` to the prewarm child script. The harness
wiring was fixed and the same latency matrix was rerun as
`codex_issue8_1eighth_latency_matrix_rerun_20260522/20260522113432`, which
passed.

| Gate | Result |
| --- | --- |
| Corrected 59K/124K latency matrix, MTP, prefix cache disabled, cold cache, repeat 3 | 59K C=1 TTFT mean `12.357s`, C=2 `20.383s`; 124K C=1 `31.293s`, C=2 `47.994s`; failures `0` |
| 124K decode-concurrency gate, max tokens 256 | C=1 TTFT `30.464s`, decode `103.308 tok/s`; C=2 slow request `18.834 tok/s`, decode min/max `0.180`, ITL p99 `0.334s`; failures `0` |
| Mixed arrival gate | `decode_then_59k` and `long_then_short` both passed; secondary ITL p95 `0.022s` and `0.030s`; failures `0` |
| Streaming pressure matrix | 4 cases, 36 requests, failures `0`, slow cases `0`, max TTFT `64.503s`, p99 ITL `1.156s` |
| Short-context MTP bench, 80 prompts | C=1/2/4/8/16/24 output throughput `162.99 / 257.71 / 392.73 / 548.93 / 756.94 / 886.44 tok/s` |
| GSM8K 5-shot limit-200, MTP C=4 | `exact_match_flexible=0.965`, `exact_match_strict=0.935` |
| Random prefill sweep, C=1, OSL=1 | ISL 1K/4K/16K/64K input throughput `6350 / 6024 / 5530 / 4577 tok/s`; mean TTFT `0.161 / 0.680 / 2.962 / 14.318s` |

Decision: the 1/8 decode-overlap cap remains the active Dev-branch candidate.
It improves the issue #8-like cold C=2 slow-request path materially while the
refreshed short-context, GSM8K, streaming pressure, mixed-arrival, and prefill
gates remain healthy. The known residual limitation is not a crash or pure
decode-kernel cliff; it is fairness under simultaneous cold long-prefill where
one stream can still be slower than its pair.

Consolidated user-feedback matrix:

Use `scripts/run_sm120_user_feedback_matrix.sh` for the combined tradeoff view
instead of chasing one reported shape at a time. It runs the prefix-cache-off
local matrix first, then the MTP=1 prefix-cache HTTP `/metrics` stress in a
separate prefix-cache-on serve, and writes one
`user_feedback_matrix_summary.md/json` at the matrix root.

First complete run:
`codex_user_feedback_matrix_20260522/20260522155455`, topology
`2x_rtx_pro_6000_sm120_user_feedback`, summary
`user_feedback_matrix_summary.md`.

| Gate | Result |
| --- | --- |
| Phase exits | primary MTP all `0`; prefix-cache MTP=1 stress `0` |
| 59K latency, cold, repeat 3 | C=1 TTFT mean `12.233s`, C=2 `19.289s`; failures `0` |
| 124K latency, cold, repeat 3 | C=1 TTFT mean `31.123s`, C=2 `48.847s`; failures `0` |
| 124K decode-concurrency | C=1 decode `107.036 tok/s`; C=2 slow request `20.797 tok/s`, decode min/max `0.209`, ITL p99 `0.142s`; failures `0` |
| Mixed arrival | `decode_then_59k`, `decode_then_124k`, and `long_then_short` all passed; decode min/max `0.206 / 0.292 / 0.575` |
| Streaming pressure | 36 requests, failures `0`, slow cases `0`, max TTFT `59.434s`, ITL p99 `1.127s` |
| Short-context MTP bench | C=1/2/4/8/16/24 output throughput `160.68 / 256.59 / 389.43 / 551.89 / 784.14 / 922.80 tok/s` |
| GSM8K 5-shot limit-200, MTP C=4 | `exact_match_flexible=0.940`, `exact_match_strict=0.925`; flexible is at the fixed floor |
| Random prefill sweep, C=1, OSL=1 | ISL 1K/4K/16K/64K input throughput `6350 / 6012 / 5526 / 4570 tok/s` |
| MTP=1 prefix-cache HTTP metrics stress | health `200`, trials `5`, failures `0`, solo hit rate `0.6729`, concurrent hit rate `0.7507` |

Tradeoff read: this is the best current balanced point for the dual-card,
<=128K-class development target. The branch should optimize further around
long-context C=2 fairness, but not by sacrificing C=1/C=2/C=4 short latency,
GSM8K flexible correctness, prefix-cache stability, or server responsiveness.
The 256K+ / TP=4 path remains an external gate rather than a claim from this
matrix.

### DS4-Inspired Active Decode 1/16 Very-Long Prefill Cap

After adding the DS4-style frontier and semantic gates, the first retained
vLLM inference-side follow-up applied the DS4 serving principle that a live
local session should keep making progress while new long prompt work arrives.
The change is deliberately internal: no public knob is added, pure C=1 prefill
is unchanged, and the no-active-decode waiting-request caps remain unchanged.
Only the active-decode plus very-long-prefill branch tightens from 1/8 to 1/16
of `max_num_batched_tokens`.

Fixed user-feedback A/B, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2, `FULL_AND_PIECEWISE`:

| Shape | Metric | Baseline | Active-Decode 1/16 | Delta |
| --- | --- | ---: | ---: | ---: |
| 59K C=1 cold | TTFT mean | 12.844 s | 12.233 s | -4.8% |
| 59K C=2 cold | TTFT mean | 20.950 s | 20.149 s | -3.8% |
| 59K C=2 cold | Decode min/max | 0.073 | 0.103 | +41.1% |
| 59K C=2 cold | ITL P99 | 0.289 s | 0.215 s | -25.6% |
| 124K C=1 cold | TTFT mean | 33.496 s | 31.090 s | -7.2% |
| 124K C=2 cold | TTFT mean | 53.426 s | 48.404 s | -9.4% |
| 124K C=2 cold | Decode min/max | 0.095 | 0.120 | +26.3% |
| 124K C=2 cold | ITL P99 | 0.288 s | 0.239 s | -17.0% |
| 124K decode-concurrency C=2 | Decode min | 19.161 tok/s | 28.266 tok/s | +47.5% |
| 124K decode-concurrency C=2 | Decode min/max | 0.178 | 0.270 | +51.7% |
| 124K decode-concurrency C=2 | ITL P99 | 0.305 s | 0.237 s | -22.3% |
| Streaming pressure | Max TTFT | 66.714 s | 62.018 s | -7.0% |
| Streaming pressure | ITL P99 | 1.209 s | 0.725 s | -40.0% |

Mixed-arrival behavior confirms the intended tradeoff:

| Case | Metric | Baseline | Active-Decode 1/16 |
| --- | --- | ---: | ---: |
| decode then 59K long | Decode min/max | 0.099 | 0.136 |
| decode then 59K long | Secondary TTFT | 14.743 s | 14.871 s |
| decode then 124K long | Decode min/max | 0.300 | 0.390 |
| decode then 124K long | Secondary TTFT | 31.934 s | 37.951 s |
| long then short | Decode min/max | 0.466 | 0.573 |
| long then short | Secondary TTFT | 30.578 s | 30.248 s |

The only meaningful cost is `decode_then_124K` secondary TTFT, where the new
long request waits longer because the already-started decoder gets protected.
This matches the current tradeoff policy for edge/local deployments: already
streaming output smoothness is prioritized over a second cold long-prefill
request's TTFT.

Short-context and correctness gates on the retained candidate:

| Gate | Result |
| --- | --- |
| HF/MT-Bench short bench C=1/2/4/8/16/24 | all 80/80 successful; output tok/s `162.68 / 255.96 / 393.49 / 562.84 / 797.34 / 919.69` |
| GSM8K 5-shot limit-200, C=4 | `exact_match_flexible=0.965`, `exact_match_strict=0.950` |
| Random prefill sweep C=1, OSL=1 | 1K/4K/16K/64K all successful; mean TTFT `0.162 / 0.678 / 2.958 / 14.240 s` |
| Issue #10 safe proxy | startup latency, prefix-cache stress, and streaming pressure all passed; streaming max TTFT `23.459 s`; driver health showed no Xid/UVM/fatal signals |
| Issue #10 high-risk proxy | 131K max-model-len, prefix-cache on, MTP=2; startup latency, prefix-cache stress, and high-risk streaming pressure all passed; streaming max TTFT `60.050 s`; driver health showed no Xid/UVM/fatal signals |
| Issue #8 high-risk payload | no-MTP, prefix-cache on, 124K C=1/C=2 cold, `max_tokens=1024`; both groups passed, C=2 TTFT mean `56.991 s`, slow request decode `4.286 tok/s`, ITL p99 `0.273 s`; driver health after the run showed no Xid/UVM/fatal signals |

Artifact labels:
`20260525_ds4_absorption_safe_baseline_dev`,
`20260525_ds4_active_decode_prefill_cap_ab`, and
`20260525_ds4_active_decode_prefill_cap_short_correctness`,
`20260525_ds4_active_decode_prefill_cap_issue10_safe`,
`20260525_ds4_high_risk_crash_recheck_dev`, and
`20260525_issue8_high_risk_payload_recheck_dev`.

Full post-change safe baseline:
`20260525_active_decode_prefill_cap_full_baseline/20260525091003`.
This reran the complete safe DS4 absorption set after the harness guardrail:
primary user-feedback matrix, prefix-cache stress sweep, and issue #10 safe
proxy. Root phases were `user_feedback_matrix=0` and `issue10_safe_proxy=0`;
all primary phases and all prefix-cache filler cases exited `0`. Driver health
stayed clean: no Xid, UVM, fatal, GPU-lost, CUDA, or NCCL error signals were
reported, and both GPUs returned to idle after cleanup.

Compared with `20260525_ds4_absorption_safe_baseline_dev/20260525065224`:

| Shape | Metric | Safe baseline | Full post-change | Delta |
| --- | --- | ---: | ---: | ---: |
| 59K C=1 cold | TTFT mean | 12.844 s | 12.189 s | -5.1% |
| 59K C=2 cold | TTFT mean | 20.950 s | 19.614 s | -6.4% |
| 59K C=2 cold | Decode min/max | 0.073 | 0.221 | +202.7% |
| 59K C=2 cold | ITL P99 | 0.289 s | 0.092 s | -68.2% |
| 124K C=1 cold | TTFT mean | 33.496 s | 30.982 s | -7.5% |
| 124K C=2 cold | TTFT mean | 53.426 s | 49.110 s | -8.1% |
| 124K C=2 cold | Decode min/max | 0.095 | 0.276 | +190.5% |
| 124K C=2 cold | ITL P99 | 0.288 s | 0.099 s | -65.6% |
| 124K decode-concurrency C=2 | Decode min | 19.161 tok/s | 29.786 tok/s | +55.5% |
| 124K decode-concurrency C=2 | ITL P99 | 0.305 s | 0.098 s | -67.9% |
| Streaming pressure | Max TTFT | 66.714 s | 58.884 s | -11.7% |
| Streaming pressure | ITL P99 | 1.209 s | 0.726 s | -40.0% |

Mixed-arrival full-baseline results:

| Case | Baseline decode min/max | Full post-change decode min/max | Secondary TTFT |
| --- | ---: | ---: | ---: |
| decode then 124K long | 0.300 | 0.403 | 32.111 s |
| decode then 59K long | 0.099 | 0.304 | 13.426 s |
| long then short | 0.466 | 0.548 | 30.355 s |

No-regression gates in the full baseline:

| Gate | Result |
| --- | --- |
| HF/MT-Bench short bench C=1/2/4/8/16/24 | all 80/80 successful; output tok/s `162.57 / 255.43 / 396.98 / 566.99 / 802.14 / 920.38` |
| GSM8K 5-shot limit-200, C=4 | `exact_match_flexible=0.955`, `exact_match_strict=0.945` |
| Random prefill sweep C=1, OSL=1 | 1K/4K/16K/64K all successful; mean TTFT `0.161 / 0.678 / 2.958 / 14.250 s` |
| Frontier context sweep | both DS4 prompt files passed all 12 frontier cases, with zero failures |
| DS4 story recall semantic | all 16 required `Name=number` facts matched |
| Prefix-cache stress | fillers `100/400/800/1600/3200` all passed; concurrent hit rate rose from `0.283` to `0.956` across the sweep |
| Issue #10 safe proxy | startup latency, prefix-cache stress, and streaming pressure all passed; issue #10 streaming max TTFT `22.689 s` |

Decision: keep the 1/16 very-long active-decode cap on the Dev branch. It
improves the current user-feedback matrix and does not regress GSM8K,
short-context bench, random prefill, prefix-cache stress, issue #10 safe proxy,
or driver stability. Keep >128K/four-card behavior as an external gate. This
supersedes the earlier 1/8 decode-overlap cap as the active Dev candidate.

Harness follow-up: the first issue #8 high-risk wrapper run only reached
`server_startup` because `run_sm120_ds4_absorption_stress.sh` set
`B200_BASELINE_PHASES=long_context_decode_concurrency` but did not also set
`RUN_LONG_CONTEXT_DECODE_CONCURRENCY=1`, which `run_b200_baseline.sh` requires.
The wrapper was corrected, and the payload was rerun directly with the explicit
flag before recording the issue #8 high-risk result above.

Harness guardrail: `run_b200_baseline.sh` now rejects an explicitly listed
`B200_BASELINE_PHASES` entry before launch when the matching `RUN_*` flag is
disabled. This preserves the old `all` behavior, where disabled optional phases
stay skipped, but prevents another targeted high-risk gate from silently running
only `server_startup`.

### Running-Prefill Budget Pressure

The next C=2 fairness pass found a smaller scheduler hole after the active
decode caps: once a short prefill is admitted behind a long prefill, both
requests become RUNNING. On the following step, the leading long prefill could
consume the whole scheduler budget because the previous guard only considered
waiting requests. The retained development candidate treats a later unfinished
RUNNING prefill as the same budget-pressure signal, so the leading long
prefill continues to leave room for the already-admitted shorter prefill.

Narrow A/B, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2, `FULL_AND_PIECEWISE`, repeat count 3:

| Shape | Metric | Current 1/16 Policy | Running-Prefill Pressure | Delta |
| --- | --- | ---: | ---: | ---: |
| 59K C=2 cold | TTFT mean | 19.459 s | 19.256 s | -1.0% |
| 59K C=2 cold | TTFT max | 27.276 s | 25.860 s | -5.2% |
| 59K C=2 cold | Decode min | 31.665 tok/s | 31.797 tok/s | +0.4% |
| 59K C=2 cold | ITL P99 | 0.0887 s | 0.0866 s | -2.4% |
| 124K C=2 cold | TTFT mean | 47.826 s | 47.987 s | +0.3% |
| 124K C=2 cold | Decode min | 29.941 tok/s | 30.653 tok/s | +2.4% |
| 124K C=2 cold | Decode min/max | 0.292 | 0.300 | +2.6% |
| `decode_then_59K` | Decode min | 39.896 tok/s | 41.137 tok/s | +3.1% |
| `decode_then_124K` | Decode min | 42.495 tok/s | 44.918 tok/s | +5.7% |
| `long_then_short` | Secondary TTFT | 30.325 s | 30.374 s | +0.2% |

Artifact labels: `20260531_c2_fairness_current_a03c87c` and
`20260531_running_prefill_fairness_candidate`.

Full user-feedback matrix artifact:
`20260531_running_prefill_fairness_user_feedback/20260531184641`.

Promotion gate result: all primary, prefix-cache, and KV-lifecycle phases
exited `0`; GSM8K 5-shot limit-200 was `0.950` flexible / `0.935` strict;
short HF/MT C=1/2/4 output throughput was `153.72 / 241.55 / 357.55` tok/s;
124K C=2 decode-concurrency slow request was `30.848` tok/s with ITL p99
`0.096 s`; prefix-cache stress passed all filler sizes with zero failures;
prefix-disabled idle KV returned to `0.000%`; prefix-enabled idle KV stayed at
`5.894%`, below the `90%` recoverability threshold. Runtime monitoring showed
no server unresponsive, CUDA, NCCL, driver, or engine error signals.

Decision: keep and promote. The change fixes a real RUNNING-queue fairness
case and modestly improves C=2 / decode-then-long metrics without moving the
broader no-regression gates materially. It does not solve `long_then_short`;
that shape needs a different scheduling or admission mechanism.

### Later Running Decode Budget Pressure

The next trace separated two mixed-arrival problem classes that should not be
collapsed into one kernel bug:

1. `decode_then_long`: an existing decode stream has already emitted tokens,
   then a long prefill is admitted behind it. This is still the main
   kernel-boundary interference shape for sparse-MLA prefill work.
2. `long_then_short`: a long prefill has already started, then a short request
   arrives later. The short request can be admitted and can complete prefill,
   but its subsequent decode can sit behind the leading long prefill in the
   RUNNING queue.

Scheduler trace artifact
`20260531_sched_trace_mixed_arrival_synced/20260531215912` showed the second
shape directly. The short request entered RUNNING, received prefill budget,
and emitted its first token, but the following scheduler steps resumed the
leading long prefill with full 4096-token chunks. The result was a
`long_then_short` secondary elapsed time of `30.828 s` and a secondary
p99/max inter-chunk gap of `26.572 s`.

A first diagnostic fix treated the later decode exactly like an already
scheduled decode and applied the existing 1/16 very-long active-decode cap.
It fixed starvation but overshot the tradeoff: artifact
`20260531_later_decode_budget_experiment_trace/20260531220637` reduced the
secondary elapsed time to `8.796 s`, but regressed the primary long-prefill
TTFT to `43.399 s`.

Two narrower caps were then tested for the later-running-decode-only path:

| Candidate | Artifact | `long_then_short` Primary TTFT | Secondary Elapsed | Secondary ITL P95 | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| 1/4 cap | `20260531_later_decode_budget_quarter_trace/20260531221304` | 34.837 s | 11.202 s | 0.464 s | promising |
| 1/2 cap | `20260531_later_decode_budget_half_trace/20260531221715` | 33.538 s | 16.432 s | 0.649 s | reject as too weak |

The broad 1/4 cap was rerun without trace logging, repeat count 3:
`20260531_later_decode_budget_quarter_mixed_arrival_r3/20260531222109`.

| Case | Requests | Failures | Primary TTFT Mean | Secondary TTFT Mean | Secondary ITL P95 | Decode Min/Max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `decode_then_124k` | 6 | 0 | 30.549 s | 31.719 s | 0.029 s | 0.349 |
| `long_then_short` | 6 | 0 | 32.639 s | 3.355 s | 0.261 s | 0.111 |

Runtime monitoring for the repeat-3 run showed zero CUDA, NCCL, driver,
engine, or server error signals.

However, a follow-up 59K/124K C=1/C=2 latency smoke showed that applying the
later-decode cap to all later decoders is too broad for the long+long shape:
artifact `20260531_later_decode_budget_quarter_latency_smoke/20260531222935`
reported 124K C=2 TTFT mean `64.052 s`.

The implementation was narrowed to later short decoders only, where "short"
means the later request's prompt is no more than four scheduler steps. That
keeps the user-visible `long_then_short` fix while avoiding the long+long C=2
policy change. The narrowed policy is covered by two scheduler tests:

- a short later decode behind a leading long prefill receives budget in the
  same step;
- a long later decode behind a leading long prefill does not trigger this
  reserve path.

Validation artifact
`20260531_later_short_decode_budget_validation/20260531223629`:

| Gate | Result |
| --- | --- |
| `long_then_short`, repeat 3 | failures `0`; primary TTFT mean `32.581 s`; secondary TTFT mean `3.368 s`; secondary elapsed about `8.7-9.0 s`; secondary ITL p95 `0.259 s` |
| `decode_then_124k`, repeat 3 | failures `0`; primary TTFT mean `30.846 s`; secondary TTFT mean `31.777 s`; secondary ITL p95 `0.028 s` |
| 59K/124K C=1/C=2 latency smoke, repeat 1 | failures `0`; 59K C=1 `12.086 s`, 124K C=1 `30.435 s`, 124K C=2 `60.302 s` |
| Runtime monitoring | zero CUDA, NCCL, driver, engine, or server error signals |

Decision: keep this as a Dev-branch candidate only. It keeps the public surface
unchanged and preserves `FULL_AND_PIECEWISE`, but the current repeat-1 long+long
C=2 latency remains too high to promote. Before PR-branch promotion, rerun the
fixed-protocol repeat-3 user-feedback matrix and compare 59K/124K C=2 against
the latest accepted same-branch baseline.

### Open Follow-Up: Prefill/Decode Interference Trace

Future kernel work should continue to keep two interference classes separate:

1. `decode_then_long`: an existing decode stream has already emitted tokens,
   then a long prefill is admitted behind it. This is the most plausible
   kernel-boundary interference shape. Trace first before changing kernels:
   compare CUDA kernel duration, launch order, sparse-MLA prefill kernels, and
   paged-MQA decode kernels while the decode stream is active.
2. `long_then_short`: a long prefill has already started, then a short request
   arrives later. The latest trace points at RUNNING-queue budget pressure
   after the short request has completed prefill, not at initial admission or
   pure paged-MQA decode throughput.

Do not add a user-facing knob for either class. Keep `FULL_AND_PIECEWISE`
enabled. Experimental changes stay on development or temporary branches until
the same user-feedback matrix proves a no-regression result. Global
`max_num_batched_tokens=2048` was already rejected for this purpose because it
regressed the mixed long/short gate without improving fairness.

Nsight Systems traces on 2026-05-31 narrowed the kernel-side bottleneck:

| Trace | Key Metrics | Top Kernel Signal |
| --- | --- | --- |
| `20260531_decode_then_124k_nsys_trace/20260531210706` | primary TTFT `31.116 s`, secondary TTFT `32.238 s`, decode min/max `0.386`, p99 ITL `0.110 s` | `_accumulate_indexed_attention_chunk_multihead_kernel` `48.3%`, `_fp8_mqa_logits_kernel` `12.0%`, `_combine_topk_swa_indices_kernel` `0.1%` |
| `20260531_long_then_short_nsys_trace/20260531211134` | primary TTFT `31.282 s`, secondary TTFT `29.847 s`, decode min/max `0.580`, p99 ITL `0.566 s` | `_accumulate_indexed_attention_chunk_multihead_kernel` `49.1%`, `_fp8_mqa_logits_kernel` `11.8%`, `_combine_topk_swa_indices_kernel` `0.1%` |

The clean dev branch was re-profiled after removing the unpromoted scheduler
candidate:

| Trace | Key Metrics | Top Kernel Signal |
| --- | --- | --- |
| `20260601_decode_then_124k_nsys_clean_dev/20260531225627` | primary TTFT `30.384 s`, secondary TTFT `32.194 s`, decode min/max `0.329`, secondary ITL p95 `0.029 s` | `_accumulate_indexed_attention_chunk_multihead_kernel` `48.8%`, `_fp8_mqa_logits_kernel` `12.0%`, `_combine_topk_swa_indices_kernel` below top 30 |
| `20260601_long_then_short_nsys_clean_dev/20260531225952` | primary TTFT `31.671 s`, secondary TTFT `3.285 s`, secondary elapsed `30.358 s`, secondary ITL p99 `26.385 s`, decode min/max `0.028` | `_accumulate_indexed_attention_chunk_multihead_kernel` `49.3%`, `_fp8_mqa_logits_kernel` `11.9%`, `_combine_topk_swa_indices_kernel` `0.1%` |

Interpretation: the next kernel work should focus on the sparse MLA prefill
accumulate path and FP8 MQA logits path. The combine-topk kernel is visible in
the trace, but it is not currently large enough to be the first optimization
target for these mixed-arrival shapes.

Rejected experiments from the same trace cycle:

| Experiment | Artifact Label | Result | Decision |
| --- | --- | --- | --- |
| Force `VLLM_TRITON_MLA_SPARSE_TOPK_CHUNK_SIZE=256` | `20260531_sparse_topk256_mixed_arrival_probe/20260531211601` | `decode_then_124k` secondary TTFT regressed from same-protocol `31.769 s` to `34.294 s`; `long_then_short` decode min/max improved only slightly while secondary ITL p99 worsened `0.034 s` to `0.041 s` | reject |
| Lower `VLLM_SPARSE_INDEXER_MAX_LOGITS_MB=256` | `20260531_sparse_indexer_logits256_mixed_arrival_probe/20260531212235` | TTFT movement was noise-level; `decode_then_124k` decode min/max `0.332` to `0.356`, but `long_then_short` decode min/max `0.604` to `0.555` | reject |
| Change prefill indexed attention `HEAD_BLOCK` from `8` to `4` | `20260531_prefill_headblock4_mixed_arrival_probe/20260531213603` | `decode_then_124k` was effectively unchanged; `long_then_short` decode min/max regressed `0.604` to `0.568` | reject and revert code |
| Change prefill indexed attention multihead launch from `num_warps=4` to `8` | `20260601_prefill_accumulate_warps8_mixed_probe/20260531230321` | `decode_then_124k` stayed noise-level (`primary TTFT 30.408 s`, `secondary TTFT 31.865 s`, decode mean `64.746 tok/s`), while `long_then_short` worsened slightly (`primary TTFT 32.073 s`, `secondary TTFT 3.437 s`, secondary ITL p99 `26.636 s`) | reject and revert code |
| Change direct FP8 MQA logits launch from `num_warps=4` to `8` | `20260601_fp8_mqa_warps8_mixed_probe/20260531230927` | clear regression: `decode_then_124k` primary/secondary TTFT regressed to `35.926 s` / `39.824 s`, decode min/max fell to `0.183`, and `long_then_short` secondary ITL p99 worsened to `32.279 s` | reject and revert code |

NCU microbench evidence, artifact directory
`20260601_ncu_kernel_microbench`, supports stopping local launch/tile sweeps:

| Kernel | Shape | Duration | Compute Throughput | DRAM Throughput | Eligible Warps / Scheduler | Registers / Thread | Theoretical / Achieved Occupancy | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `_accumulate_indexed_attention_chunk_multihead_kernel` | q `256x64x128`, candidates `1024` | `707.97 us` | `74.30%` | `1.33%` | `1.31` | `40` | `100%` / `72.80%` | not GDDR7 bandwidth-bound; scheduler eligibility and dependency stalls dominate enough that `num_warps=8` was not a useful cut |
| `_fp8_mqa_logits_kernel` | q `256x64x128`, KV `131072x128` | `2.89 ms` | `76.55%` | `2.18%` | `0.35` | `255` | `16.67%` / `16.38%` | register-limited occupancy explains the `num_warps=8` regression; further launch-level tuning should not continue without reducing live state |

Direct FP8 MQA top-k microbench evidence was added as a reusable pre-endpoint
gate for the streaming-top-k experiment. The current implementation returns the
same top-k set across repeated calls and matches the full-logits torch
reference as a set, but the order is not stable and should not be used as a
parity criterion:

| Artifact Label | Shape | Mean | p95 | Repeat Set | Repeat Order | Reference Set | Reference Order |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| `20260601_mqa_topk_microbench_default` | q `256x64x128`, KV `4096x128`, top-k `2048` | `0.169 ms` | `0.181 ms` | pass | fail | pass | fail |
| `20260601_mqa_topk_microbench_default` | q `256x64x128`, KV `32768x128`, top-k `2048` | `0.778 ms` | `0.789 ms` | pass | fail | skipped | skipped |
| `20260601_mqa_topk_microbench_frontiers` | q `256x64x128`, KV `58957x128`, top-k `2048` | `1.272 ms` | `1.284 ms` | pass | fail | skipped | skipped |
| `20260601_mqa_topk_microbench_frontiers` | q `256x64x128`, KV `124000x128`, top-k `2048` | `2.599 ms` | `2.606 ms` | pass | fail | skipped | skipped |
| `20260601_mqa_topk_microbench_131k` | q `256x64x128`, KV `131072x128`, top-k `2048` | `2.719 ms` | `2.725 ms` | pass | fail | skipped | skipped |

The 131K direct top-k path was decomposed on the same shape. The `top_k`
selection stage is small; nearly all time is still in the FP8 MQA logits
kernel:

| Artifact Label | Stage | Mean | p95 |
| --- | --- | ---: | ---: |
| `20260601_mqa_topk_decompose_131k` | `fp8_mqa_logits_triton` | `2.575 ms` | `2.588 ms` |
| `20260601_mqa_topk_decompose_131k` | `top_k_per_row_prefill` on existing logits | `0.084 ms` | `0.089 ms` |
| `20260601_mqa_topk_decompose_131k` | full `fp8_fp4_mqa_topk_indices` | `2.718 ms` | `2.725 ms` |

Sparse MLA prefill accumulate now has a standalone microbench at
`scripts/run_sm120_sparse_mla_accumulate_microbench.py`. On the target
`q=256x64x128`, `kv=131072x128` shape, candidate chunking itself is not the
primary cost; the current online state update is nearly linear in candidates
and the 256-way multi-request chunking is close to the single-call baseline:

| Artifact Label | Candidates | Chunk Size | Calls | Mean | p95 |
| --- | ---: | --- | ---: | ---: | ---: |
| `20260601_sparse_mla_accumulate_microbench_default` | 512 | single | 1 | `0.348 ms` | `0.353 ms` |
| `20260601_sparse_mla_accumulate_microbench_default` | 512 | 256 | 2 | `0.346 ms` | `0.348 ms` |
| `20260601_sparse_mla_accumulate_microbench_default` | 1024 | single | 1 | `0.668 ms` | `0.673 ms` |
| `20260601_sparse_mla_accumulate_microbench_default` | 1024 | 256 | 4 | `0.689 ms` | `0.757 ms` |
| `20260601_sparse_mla_accumulate_microbench_default` | 1152 | single | 1 | `0.747 ms` | `0.754 ms` |
| `20260601_sparse_mla_accumulate_microbench_default` | 1152 | 256 | 5 | `0.753 ms` | `0.756 ms` |

Current stop condition for local kernel-launch tuning: the cheap "cut kernels
shorter" levers have now been tested across sparse-MLA query chunk, topk chunk,
head grouping, accumulate warps, and direct FP8 MQA tile/warp dimensions. The
profile still points at the same two kernels, but local launch/tile changes
either do not move the mixed-arrival metrics or regress them. The NCU evidence
shows low DRAM pressure and scheduler/register limits, so do not continue small
launch-parameter sweeps. A future kernel project would need an algorithmic
change that reduces live state or avoids materializing the large fp32 logits
matrix, but the direct top-k decomposition shows that simply fusing top-k
selection is unlikely to be enough; treat any streaming top-k work as a
register/live-state experiment, not as a top-k-selection experiment.

### Sparse SWA MTP Reorder Correctness Fix

The 64K-class MTP=2 C=3/C=4 retrieval miss was traced to a metadata split
mismatch rather than to unchecked draft acceptance. DeepSeek V4 sparse SWA
internally used `decode_threshold = 1 + num_speculative_tokens`, but still
reported `reorder_batch_threshold = 1` to the model runner. Because the runner
uses the minimum threshold across attention groups, a 3-token MTP verification
step could be ordered after a long chunked-prefill request. Sparse SWA then
assumed decodes were at the front of the batch and treated the MTP verification
tokens as prefill tokens.

The captured failing request showed the exact divergence: after `beta` was
accepted, the draft second token was `-qu`, but target verification's second
row preferred `-c`, producing `beta-cobalt-29` instead of
`beta-quartz-29`. The retained fix initializes sparse SWA's runner-facing
reorder threshold with `supports_spec_as_decode=True` and reuses that value for
the internal decode/prefill split. vLLM commit: `24db5ed89`.

Regression test:

| Test | Result |
| --- | --- |
| `tests/v1/attention/test_deepseek_v4_sparse_swa.py::test_sparse_swa_reorder_threshold_matches_mtp_decode_threshold` | failed before fix, passed after fix |
| `tests/v1/attention/test_deepseek_v4_sparse_swa.py tests/v1/attention/test_batch_reordering.py tests/v1/attention/test_attention_splitting.py` | 38 passed |

Targeted long-context gate, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2, synthetic 2000-line prompt,
`max_tokens=128`, repeat count 3, artifact label
`sparse_swa_reorder_fix_c3_c4_62k/20260519090417`:

| Prompt Shape | Concurrency | Requests | Failures | Mean TTFT | Max TTFT |
| --- | ---: | ---: | ---: | ---: | ---: |
| 62K synthetic | 3 | 9 | 0 | 27.017 s | 40.346 s |
| 62K synthetic | 4 | 12 | 0 | 34.400 s | 54.593 s |

Correctness gate, artifact label
`sparse_swa_reorder_fix_gsm8k_limit200/20260519091147`: GSM8K limit-200
5-shot `exact_match_flexible` was 0.960 versus the fixed current-branch
baseline of 0.955, so the gate passed with delta +0.005.

Short-context smoke, artifact label
`sparse_swa_reorder_fix_short_smoke/20260519091743`, MTP=2, MT-Bench HF
dataset, 16 prompts:

| Concurrency | Successful Requests | Output Tok/s | Mean TTFT | Acceptance Rate |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 16/16 | 129.44 | 319.58 ms | 65.51% |
| 2 | 16/16 | 170.78 | 424.36 ms | 63.81% |
| 4 | 16/16 | 197.55 | 507.05 ms | 62.15% |

### FP8 MQA Logits `BLOCK_M=16`

The direct FP8 MQA logits fallback originally launched the Triton kernel with
`BLOCK_M=8`, `BLOCK_N=128`, and 4 warps. A small tile sweep on a representative
late-context shape showed that widening the row tile to `BLOCK_M=16` roughly
halved the standalone kernel runtime while preserving output parity for the
sampled case. The promoted change keeps the scope narrow: only the wrapper grid
and `BLOCK_M` meta-parameter change.

Promotion gate, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2:

| Prompt Shape | Concurrency | Prior Mean TTFT | `BLOCK_M=16` Mean TTFT | Delta |
| --- | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 14.037 s | 13.394 s | -4.6% |
| 64K synthetic | 2 | 22.088 s | 19.798 s | -10.4% |
| 64K synthetic | 4 | 37.577 s | 34.065 s | -9.4% |
| 128K synthetic | 1 | 36.541 s | 33.264 s | -9.0% |
| 128K synthetic | 2 | 56.902 s | 49.199 s | -13.5% |
| 128K synthetic | 4 | 96.317 s | 82.181 s | -14.7% |

Correctness gate: GSM8K `exact_match_flexible` stayed at 0.95, matching the
fixed baseline.

Profiler note: NCU on the same FP8 MQA logits kernel showed higher SM
throughput and lower issued-instruction spacing despite lower theoretical
occupancy. The path still does not look GDDR7-bandwidth saturated; continue to
treat register pressure, eligible warps, and long-scoreboard stalls as the next
optimization surface.

Caveat: the short-context cold gate saw a first-request Triton compile spike
after the new specialization. The second short request was in the expected
steady-state range. Do not count the first-request compile spike as a model
latency regression, but keep startup warmup in mind before presenting
user-facing cold-start numbers.

### FP8 MQA Logits `BLOCK_M=64`

After the `BLOCK_M=32` variants were rejected, a narrower follow-up retested
only the direct FP8 MQA logits row tile while keeping `BLOCK_N=128`,
`BLOCK_D=64`, and `num_warps=4`. The promoted change widens the wrapper's
M tile from 16 to 64. The standalone 131K-KV microbench showed the same
direction across small and large query-row counts, with sampled outputs
matching the `BLOCK_M=16` result:

| Query Rows | `BLOCK_M=16` Mean | `BLOCK_M=64` Mean | Delta |
| ---: | ---: | ---: | ---: |
| 128 | 1.672 ms | 1.294 ms | -22.6% |
| 256 | 3.266 ms | 2.542 ms | -22.2% |
| 512 | 6.513 ms | 5.032 ms | -22.7% |
| 1024 | 13.022 ms | 10.020 ms | -23.0% |

Artifact labels: `codex_mqa_tile_sweep_20260520040025` and
`codex_mqa_blockm_followup_20260520040105`.

Because prior larger-row experiments had failed promotion despite good
microbench numbers, this variant was checked with a paired same-host C=1
repeat against the current `BLOCK_M=16` baseline:

| Prompt Shape | `BLOCK_M=16` Mean TTFT | `BLOCK_M=64` Mean TTFT | Delta |
| --- | ---: | ---: | ---: |
| 59K synthetic, C=1 repeat=3 | 11.413 s | 11.097 s | -2.8% |
| 124K synthetic, C=1 repeat=3 | 29.868 s | 28.042 s | -6.1% |

Artifact labels: `codex_blockm16_c1_repeat_baseline/20260520041627` and
`codex_blockm64_c1_repeat/20260520041210`.

Additional promotion gates passed:

| Gate | Result |
| --- | --- |
| Mixed 4K / 59K / 124K C=1/2/4 matrix | 9 groups, 0 failures, with FULL decode graph capture retained |
| Short HF/MT-Bench C=1/2/4, 16 prompts | all 16/16 successful; C=4 output tok/s 332.53, mean TTFT 158.92 ms |
| GSM8K limit-200, 5-shot, temperature 0 | `exact_match_flexible=0.965`, `exact_match_strict=0.940` |
| SM120 fallback tests | `tests/v1/attention/test_sm120_deepgemm_fallbacks.py` passed |

Promotion artifact labels: `codex_blockm64_latency_gate/20260520040358` and
`codex_blockm64_short_gsm8k_gate/20260520042117`.

### Adaptive FP8 MQA Logits `BLOCK_M`

User feedback on
[`issuecomment-4504312139`](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4504312139)
reported that the promoted `BLOCK_M=64` path regressed short prefill while
helping 64K-class prefill. A direct same-host recheck confirmed the shape is
real enough to fix: use `BLOCK_M=16` for `seq_len_kv <= 16K`, and keep
`BLOCK_M=64` for longer prefill.

Same-host A/B, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2, random input, output length 1,
concurrency 1, 8 prompts per shape:

| Input Shape | `BLOCK_M=64` Input tok/s | Adaptive Input tok/s | Input tok/s Delta | `BLOCK_M=64` TTFT | Adaptive TTFT | TTFT Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1K | 3385.12 | 5152.20 | +52.2% | 302.06 ms | 198.16 ms | -34.4% |
| 4K | 6159.40 | 6090.71 | -1.1% | 664.69 ms | 671.89 ms | +1.1% |
| 16K | 5539.81 | 5587.04 | +0.9% | 2957.02 ms | 2932.20 ms | -0.8% |
| 64K | 4643.00 | 4605.89 | -0.8% | 14115.16 ms | 14228.26 ms | +0.8% |

Artifact labels:
`codex_blockm64_prefill_sweep_fixed_20260521` and
`codex_adaptive_blockm_prefill_sweep_20260521`.

Decision: keep the adaptive tile selection. It directly addresses the reported
short-prefill regression while keeping 4K/16K/64K within run noise on the
dual-SM120 host.

### Mixed Arrival Long-Prefill Budget Guard

The first retained mixed scheduler cap improved the existing-decode +
new-long-prefill path, but the mixed-arrival gate still showed two gaps:
59K decode streams could see p99 inter-chunk gaps near two seconds, and a
short request arriving behind a 124K-class prefill still waited nearly the
entire long prefill before TTFT.

The retained follow-up remains internal and does not add a public scheduler
knob. It keeps the 3/4 cap for ordinary long prefills, uses the 1/2 cap once
remaining prefill exceeds four full scheduler steps, and applies the same
budget guard to an already-running long prefill when waiting requests exist.
Pure C=1 prefill, pure decode, and short prefills that fit within one full
step are unchanged.

Same-host A/B against the adaptive `BLOCK_M` candidate, prefix cache disabled,
131K max-model-len, 4096 max-num-batched-tokens, TP=2, MTP=2, repeat count 3:

| Case | Metric | Previous Candidate | Budget Guard | Delta |
| --- | --- | ---: | ---: | ---: |
| decode then 59K | Primary TTFT mean | 12.383 s | 12.289 s | -0.8% |
| decode then 59K | Primary elapsed mean | 26.554 s | 21.592 s | -18.7% |
| decode then 59K | Primary ITL p99 | 1.938 s | 0.625 s | -67.7% |
| decode then 59K | Decode tok/s mean | 65.489 | 74.237 | +13.4% |
| 124K long then short | Primary TTFT mean | 33.807 s | 31.925 s | -5.6% |
| 124K long then short | Secondary TTFT mean | 32.471 s | 30.564 s | -5.9% |
| 124K long then short | Decode min/max ratio | 0.467 | 0.505 | +8.3% |

Artifact labels:
`codex_adaptive_mixed_arrival_20260521` and
`codex_adaptive_scheduler_mixed_arrival_20260521`.

Decision: keep this follow-up. It improves the exact mixed long/short
interference gate without moving the tradeoff into a user-facing configuration
option. The remaining 30 s-class short-request TTFT behind a 124K prefill is
still a real single-instance limitation; for strict data-center SLAs, use this
gate as the point where prefill/decode separation or admission-control policy
becomes a deployment question.

Final combined gate, artifact `codex_adaptive_scheduler_final_gate_20260521`,
TP=2, MTP=2, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens:

| Gate | Result |
| --- | --- |
| 59K/124K long-context latency matrix | 4 groups, 0 failures; 59K C=1 TTFT 12.307 s, 124K C=1 TTFT 31.399 s; 59K C=2 ITL p99 0.888 s, 124K C=2 ITL p99 0.658 s |
| Mixed-arrival long/short matrix | 2 cases, 0 failures; decode-then-59K primary ITL p95 0.484 s, long-then-short secondary TTFT 30.583 s |
| Streaming pressure matrix | 4 cases, 36 requests, 0 failures, 0 slow cases; max TTFT 61.277 s, p99 ITL 1.247 s |
| Random short-prefill sweep | 1K/4K/16K/64K all successful; input tok/s 6350.39 / 6045.76 / 5532.80 / 4561.01 |
| HF/MT-Bench short-context bench | C=1/2/4/8/16/24 all 80/80 successful; output tok/s 138.33 / 229.19 / 332.32 / 353.06 / 362.89 / 359.11 |
| GSM8K 5-shot limit-50 | `exact_match_flexible=0.980`, `exact_match_strict=0.940` |

### DeepSeek V4 MTP C=4 FULL Graph Stability Fix

The short-context MTP C=4 blocker was reproduced after the rebase: no-MTP C=4
passed, while MTP=1 and MTP=2 C=4 both stalled in target verification. Turning
off async scheduling did not change the failure. Debug instrumentation narrowed
the stall to the speculative verification `_model_forward()` path after the
draft tokens had already been proposed and copied.

After reverting the diagnostic full-graph skip, the live C=4 repro with
`FULL_AND_PIECEWISE` stalled inside FULL CUDA graph replay. The failing runtime
shape was actual C=4 / 12 tokens padded to
`BatchDescriptor(num_tokens=18, num_reqs=6, uniform=True)`. A diagnostic run
that kept FULL graphs but added exact small spec-decode capture sizes passed
with C=4 hitting `BatchDescriptor(num_tokens=12, num_reqs=4, uniform=True)`.

The retained fixes are intentionally narrow:

- keep DeepSeek V4 MTP on `FULL_AND_PIECEWISE`; do not skip full decode CUDA
  graph capture;
- preserve exact small spec-decode uniform decode shapes for request counts
  1..32 so small-interactive FULL graph replay does not use padded virtual
  requests;
- bound DeepSeek V4 MTP uniform-decode warmup request counts to the small
  interactive range, capped at 32.

Regression tests:

| Test | Result |
| --- | --- |
| `tests/v1/cudagraph/test_cudagraph_dispatch.py::TestCudagraphDispatcher::test_deepseek_v4_mtp_spec_decode_keeps_full_and_piecewise_graphs` | guards against masking MTP issues by skipping full decode graphs |
| `tests/compile/test_config.py::test_spec_decode_cudagraph_sizes_keep_small_full_decode_batches_exact` | guards exact FULL graph shapes for request counts 1..32 |
| `tests/model_executor/test_deepseek_v4_kernel_warmup.py::test_deepseek_v4_mtp_uniform_decode_warmup_caps_large_max_num_seqs` | failed before fix, passed after fix |

Clean-code validation, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2:

| Gate | Result |
| --- | --- |
| FULL replay localization, label `codex_full_graph_mtp_c4_trace/20260520014805` | reproduced hang inside FULL graph replay after padding C=4/12 tokens to 18 tokens / 6 reqs |
| Exact-shape diagnostic, label `codex_full_graph_mtp_c4_exact_sizes/20260520015317` | 8/8 successful with `FULL_AND_PIECEWISE`, `PIECEWISE=11`, `FULL=11`, exact C=4 FULL replay |
| Default fixed C=4 smoke, label `codex_full_graph_mtp_c4_fix_smoke/20260520015929` | 8/8 successful with `FULL_AND_PIECEWISE`, `PIECEWISE=67`, `FULL=67`, output tok/s 316.99, mean TTFT 187.96 ms |
| Default fixed MTP C=1/2/4 matrix, label `codex_full_graph_mtp_c124_fix_short/20260520020327` | C=1/2/4 all 16/16 successful; C=4 output tok/s 360.67, mean TTFT 120.10 ms, acceptance 64.97% |
| GSM8K limit-200, 5-shot, temperature 0, label `codex_full_graph_mtp_gsm8k_fix_gate_temp0/20260520021808` | `exact_match_flexible=0.960`, `exact_match_strict=0.945` |
| 124K synthetic C=1 cold long-context smoke, label `codex_full_graph_mtp_124k_c1_fix_smoke/20260520022411` | 0 failures, TTFT 31.270 s, matched required terms |
| MTP C=4 short smoke, label `codex_c4_fix_clean_smoke16_jsonfix/20260519231919` | 16/16 successful, output tok/s 181.14, mean TTFT 620.55 ms, acceptance 64.53% |
| MTP C=1/2/4 short matrix, label `codex_mtp_c124_clean_short/20260519232237` | C=1/2/4 all 16/16 successful; C=4 output tok/s 225.48, mean TTFT 254.46 ms, acceptance 64.85% |
| no-MTP C=4 short smoke, label `codex_nomtp_c4_clean_short/20260519232622` | 16/16 successful, output tok/s 201.38, mean TTFT 425.40 ms |

Full promotion gate after the fix, label
`pr_gate_after_mtp_c4_fix/20260519233509`:

| Prompt Shape | Concurrency | Requests | Failures | Mean TTFT | Max TTFT |
| --- | ---: | ---: | ---: | ---: | ---: |
| 62K synthetic | 1 | 3 | 0 | 13.009 s | 13.036 s |
| 62K synthetic | 2 | 6 | 0 | 20.370 s | 26.906 s |
| 62K synthetic | 3 | 9 | 0 | 27.672 s | 41.810 s |
| 62K synthetic | 4 | 12 | 0 | 34.554 s | 54.625 s |
| 124K synthetic | 1 | 3 | 0 | 32.779 s | 32.797 s |
| 124K synthetic | 2 | 6 | 0 | 49.830 s | 67.093 s |
| 124K synthetic | 3 | 9 | 0 | 66.912 s | 104.247 s |
| 124K synthetic | 4 | 12 | 0 | 84.197 s | 138.497 s |

GSM8K limit-200, 5-shot, MTP concurrency 1, passed with
`exact_match_flexible=0.960` and `exact_match_strict=0.955`.
Repeating that gate without explicit generation kwargs produced
`exact_match_flexible=0.955` twice (`strict=0.950` then `0.935`), so use
`--gen_kwargs temperature=0` for deterministic correctness promotion gates.
The extra exact small FULL graphs increased capture from `PIECEWISE=49/FULL=49`
to `PIECEWISE=67/FULL=67`; on the 131K serve profile, actual CUDA graph pool
memory was 2.04 GiB and available KV cache was 491,927 tokens. That still
supports the dual-card 124K/128K single-stream path, but the graph-memory cost
should be watched in future wider gates.

The earlier C=4 validation was collected with only `PIECEWISE` CUDA graph
capture (`PIECEWISE=49`) and no full decode graph capture. That evidence is now
treated as a diagnostic workaround only, not as a promotable fix: any production
MTP repair must preserve `FULL_AND_PIECEWISE` and keep full decode CUDA graph
capture available. The current default C=4 smoke satisfies that rule and shows
both graph families captured.

## Ineffective Or Ambiguous Optimization Notes

### Prefix-Cache Stress Diagnostic Bypasses

Two related prefix-cache diagnostics were useful for localization but should
not be retained as fixes:

- Disabling sparse MLA matmul decode with
  `VLLM_TRITON_MLA_SPARSE_MATMUL_DECODE=0` did not explain the 800-filler
  prefix-cache behavior. After host recovery, both default decode and this
  diagnostic path passed the 800-filler stress shape; default was faster.
- Removing both the hybrid LCM cache-write floor and the `alignment_tokens`
  path raised the 800-filler concurrent hit-rate mean to `0.7302`, but keeping
  `alignment_tokens` while removing only the floor reached `0.7269`. The mask
  bypass adds more semantic risk for negligible gain, so it is not retained.

Decision: keep the narrower hybrid cache-write no-floor fix only. Keep the
diagnostic controls in the harness so future reports can quickly separate
runtime-kernel failures from prefix-cache accounting / cache-write behavior.

### Mixed Long Decode Internal Prefill Cap

A 2026-05-21 refresh appeared to regress 59K/124K C=1 TTFT, but that
artifact was collected from a dirty, out-of-date harness checkout and is not a
strict A/B point. A clean fixed-protocol repeat with prefix cache disabled,
131K max-model-len, 4096 max-num-batched-tokens, TP=2, MTP=2,
`FULL_AND_PIECEWISE`, and repeat count 3 did not reproduce the C=1 regression:

| Prompt Shape | C | TTFT Mean | TTFT Range | Decode tok/s Mean | ITL P95 | ITL P99 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 59K synthetic | 1 | 11.686 s | 11.006-12.975 s | 133.307 | 0.021 s | 0.024 s |
| 124K synthetic | 1 | 30.522 s | 27.902-35.545 s | 107.421 | 0.027 s | 0.029 s |

The same repeat confirmed that C=2 mixed long-context decode imbalance is
real. One request decodes while the paired long prefill is still active, so the
slow request sees second-scale inter-token gaps:

| Prompt Shape | C | TTFT Mean | TTFT Max | Decode tok/s Min | Decode tok/s Mean | Decode Min/Max | ITL P95 | ITL P99 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 59K synthetic | 2 | 17.798 s | 26.325 s | 4.689 | 63.640 | 0.037 | 1.014 s | 1.152 s |
| 124K synthetic | 2 | 44.607 s | 67.867 s | 2.258 | 54.965 | 0.021 | 1.494 s | 1.593 s |

Artifact label: `codex_regression_recheck_20260521064045`.

An internal scheduler experiment then capped long prefill chunks only after a
decode request had already been scheduled in the same step. The goal was to
reduce the one-sided decode starvation without adding a public user-facing
knob. Three cap fractions were tested:

| Prompt Shape | Variant | TTFT Mean Delta | TTFT Max Delta | Decode Min Delta | ITL P95 Delta | ITL P99 Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 59K C=2 | cap 1/4 | +7.31% | +17.67% | +36.24% | -55.72% | -59.12% |
| 59K C=2 | cap 1/3 | +5.12% | +18.13% | +9.74% | -48.80% | -50.56% |
| 59K C=2 | cap 1/2 | +4.30% | +12.96% | -8.56% | -33.66% | -39.50% |
| 124K C=2 | cap 1/4 | +2.34% | +7.68% | +168.24% | -68.52% | -69.63% |
| 124K C=2 | cap 1/3 | +2.20% | +6.50% | +130.44% | -62.85% | -64.45% |
| 124K C=2 | cap 1/2 | +1.61% | +4.59% | +86.47% | -54.72% | -54.00% |

Artifact labels:
`codex_adaptive_prefill_recheck_20260521065621`,
`codex_adaptive_prefill_third_recheck_20260521071645`, and
`codex_adaptive_prefill_half_recheck_20260521070700`.

Decision: do not retain those aggressive 1/4, 1/3, or 1/2 caps in the active
branch. The data validated the hypothesis that long prefill/decode overlap
causes the C=2 fairness cliff, but the tested fractions regressed C=2 TTFT.
The later 3/4 cap is tracked separately as a retained candidate because it is
narrower and had materially better fixed-gate behavior.

### Mixed Decode / Long Prefill 7/8 Cap

The 7/8 cap was tested as a more conservative alternative to the retained 3/4
cap. It reduced interference less than 3/4 while still not recovering the
fixed 59K C=2 decode-min proxy enough to change the tradeoff.

| Case | Variant | Decode Min | ITL P95 | ITL P99 |
| --- | --- | ---: | ---: | ---: |
| mixed-arrival decode then 59K long | 3/4 cap | 5.822 tok/s | 0.655 s | 0.835 s |
| mixed-arrival decode then 59K long | 7/8 cap | 4.610 tok/s | 0.895 s | 0.989 s |
| fixed 124K C=2 | 3/4 cap | 3.193 tok/s | 0.911 s | 0.985 s |
| fixed 124K C=2 | 7/8 cap | 2.704 tok/s | 1.065 s | 1.394 s |

Artifact label: `codex_mixed_arrival_decode_prefill_cap_7eighth_20260521`.
Decision: do not retain 7/8; it is too weak for the target interference shape.

### Short Prefill Reserve Scheduler Experiment

A separate experiment reserved token budget for short prefills while a long
prefill was already running. It improved the `long_then_short` TTFT shape but
hurt decode fairness and did not address the primary user report where an
existing decoder is interrupted by a new long prefill.

Decision: do not retain this code in the active branch. The experiment is
preserved on backup branch
`codex/short-prefill-reserve-experiment-20260521`.

### Mixed Decode/Prefill Scheduling Cap

This experiment tested whether a scheduler cap for mixed decode/prefill steps
could preserve decode smoothness while keeping the 8192-token prefill profile.
The experimental vLLM branch added an opt-in budget,
`--max-num-prefill-tokens-with-decode`, that only applied when active decode
work existed at the start of a scheduling step.

The data was positive for streaming smoothness. Same-current-code A/B, prefix
cache disabled, 131K max-model-len, TP=2, MTP=2, `FULL_AND_PIECEWISE`,
`max_num_seqs=4`, `max_num_batched_tokens=8192`, current CUDA graph memory
profiling enabled. Both services reported 4.36 GiB available KV memory and
167,242 KV tokens, so this comparison is not mixed with the older larger-KV
startup profile.

| Matrix | Cap | Max TTFT | P95 ITL | P99 ITL | Max ITL |
| --- | ---: | ---: | ---: | ---: | ---: |
| cold long C=2/C=4 | off | 51.430 s | 2.182 s | 2.459 s | 2.537 s |
| cold long C=2/C=4 | 4096 | 53.687 s | 1.141 s | 1.467 s | 1.856 s |
| warm long C=2/C=4 | off | 48.093 s | 1.882 s | 2.176 s | 2.234 s |
| warm long C=2/C=4 | 4096 | 47.534 s | 0.935 s | 1.300 s | 1.304 s |

Warm mixed-load streaming improved materially: P95 ITL dropped about 50%, P99
ITL about 40%, and max ITL about 42%, with no warm TTFT regression in this
matrix. However, the code was not retained because it exposes a new user-facing
scheduler knob with subtle semantics and no documentation-quality guidance for
when to enable it. It is also not validated on >128K, four-card, or GB10
cluster shapes. The conservative default remains to avoid adding this option to
the Dev branch for now.

Artifact labels: `codex_mixed_prefill_mbt8192_cap4096_20260520182630` and
`codex_mixed_prefill_mbt8192_nocap_20260520183653`. The experimental code is
preserved only on backup branch `codex/mixed-prefill-budget-experiment`.

### Long-Context C=2 Decode Cliff Recheck

An external report suggested that two simultaneous 120K-context decode
requests could collapse to roughly 0.1-0.2 tok/s per sequence and suspected
the SM120 paged-MQA rowwise logits kernel. A targeted gate was added via
`scripts/run_long_context_decode_concurrency.sh` to expose per-request decode
tokens/sec and C>1 ratios in the long-context latency artifact.

Current recheck, TP=2, MTP=1, 131K max-model-len, 4096
max-num-batched-tokens, 124K synthetic prompt, 64 generated tokens:

| Shape | Prefix Cache | Kernel Path | C | Mean Decode tok/s | Min Decode tok/s | C/C1 Ratio | Result |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| cold long prompt | disabled | rowwise | 1 | 81.935 | 81.935 | 1.000 | pass |
| cold long prompt | disabled | rowwise | 2 | 34.318 | 1.606 | 0.419 | pass, but mixed with second long prefill |
| warm long prompt, repeat 2 | enabled | rowwise | 1 | 81.796 | 81.796 | 1.000 | pass |
| warm long prompt, repeat 2 | enabled | rowwise | 2 | 68.687 | 63.218 | 0.840 | pass |
| warm long prompt, repeat 2 | enabled | generic fallback | 1 | 75.273 | 75.273 | 1.000 | pass |
| warm long prompt, repeat 2 | enabled | generic fallback | 2 | 65.816 | 60.446 | 0.874 | pass |

Artifact labels: `codex_long_decode_c1c2_mtp1_rowwise_20260520152213`,
`codex_long_decode_c1c2_mtp1_rowwise_prefix_20260520152814`, and
`codex_long_decode_c1c2_mtp1_generic_prefix_20260520153209`.

Decision: do not revert or disable `_fp8_paged_mqa_logits_rowwise_kernel`
based on this report alone. The cold C=2 run did show a very slow first
request, but that request was decoding while another 124K prompt was still
being prefetched; it is evidence of long-prefill/decode scheduler interference,
not pure decode-kernel collapse. The prefix-cache warm C=2 runs, which better
isolate decode after the long prompt is cached, did not reproduce the reported
0.1-0.2 tok/s cliff. The generic fallback was slightly slower in absolute
decode tokens/sec, so the current data does not support replacing rowwise with
generic fallback.

Keep this gate in future rowwise evaluations. If a user can still reproduce a
sub-1 tok/s C=2 cliff in prefix-cache warm mode, collect NCU/NSYS around the
paged-MQA logits kernel and scheduler traces before changing the kernel.

### Sparse MLA SplitKV Decode Experiment

A default-off SM120 experiment added a split-KV sparse MLA decode path behind
`VLLM_TRITON_MLA_SPARSE_SPLITKV_DECODE`. It was intended to explore whether
long-context decode could benefit from splitting the candidate dimension across
SMs before merging partial softmax state.

The experiment was removed from the active branch because it had no
promotion-quality end-to-end win for the current target. Keeping the code would
leave an undocumented A/B switch, extra Triton kernels, and additional
workspace sizing logic on the DeepSeek V4 path without a measured default
benefit. The simpler matmul decode path remains the active implementation.

Cleanup validation used the current TP=2, MTP=2, prefix-cache-disabled,
131K-capable serve profile and kept `FULL_AND_PIECEWISE` graph capture:

| Gate | Result |
| --- | --- |
| short-context streaming pressure C=4 | pass, 4/4 requests completed, max TTFT 6.940 s |
| 59K synthetic long-context C=1 | pass, TTFT 10.887 s, decode 135.659 tok/s |
| targeted vLLM tests | pass, 58 tests |
| touched-file static checks | pass, compileall, ruff, diff-check |

The splitKV code is preserved only on backup branch
`codex/sm120-splitkv-decode-experiment-backup-20260521054846`.

### Short-Context MTP C=4 Root-Cause Controls

The following controls were useful for locating the C=4 stall but were not kept
as production changes:

| Experiment | Result | Decision |
| --- | --- | --- |
| no-MTP C=4 control | passed | use as non-MTP stability control only |
| MTP=1 C=4 | stalled | not a safe fallback for this bug |
| MTP=2 C=4 with async scheduling disabled | stalled | async scheduling is not the root cause |
| CUDA graph disabled at 8K max-model-len and lower GPU memory utilization | passed | diagnostic only; not a 131K production fix |
| CUDA graph disabled at 131K with current memory target | startup OOM | not promotable |
| temporary per-stage debug logging around RPC, model forward, attention, and sampling | localized the stall | removed from code after the fix |
| manual exact small `cudagraph_capture_sizes` | passed with FULL graphs | diagnostic confirmation; replaced by default exact small spec-decode shapes |

The result points at padded full decode CUDA graph replay for DeepSeek V4 MTP
verification, not at sampler bookkeeping, prefix cache, custom all-reduce, or
async scheduler as the primary root cause. Do not reintroduce debug logging, a
global eager/no-cudagraph workaround, or a DS4 MTP full-graph skip. Keep
`FULL_AND_PIECEWISE` and preserve exact small uniform decode graph shapes.

### DeepSeek V4 mHC TileLang Warmup

The model-specific `deepseek_v4_mhc_warmup.py` path was tested after the MTP
C=4 fix because it looked like an isolated attempt to hide first-request JIT
rather than a root-cause optimization. Artifact label:
`codex_warmup_ablation_20260520033046`.

All variants used prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2, `FULL_AND_PIECEWISE`, and distinct
Triton/TileLang JIT cache directories.

| Variant | Startup | 127K C=1 Mean TTFT | 127K C=1 Max TTFT | 4K C=4 Mean TTFT | JIT Warnings |
| --- | ---: | ---: | ---: | ---: | ---: |
| mHC on, sparse warmup on | 140 s | 32.478 s | 35.180 s | 3.346 s | 13 |
| mHC off, sparse warmup on | 140 s | 32.775 s | 35.397 s | 3.324 s | 13 |
| mHC on, sparse warmup off | 130 s | 34.167 s | 38.069 s | 3.134 s | 16 |

Disabling mHC warmup did not change the first-request JIT warning set, startup
time, 127K TTFT, or short-context C=4 correctness. Even with it enabled, the
serve log still reported first-inference JIT for `_tf32_hc_prenorm_gemm_kernel`.

Decision: remove the mHC warmup code and env switches from the active branch.
Keep the sparse/request-prep/MTP warmup for now because disabling that group
added first-request long-context TTFT and more JIT misses, but continue to
treat it as an incomplete warmup mitigation rather than a root-cause fix.

### FP8 MQA Logits `BLOCK_M=32`, `BLOCK_N=256`

This tile looked better in the standalone late-context microbench than
`BLOCK_M=16`, `BLOCK_N=128`: the wrapper shape improved from roughly 14.65 ms
to roughly 11.43 ms, and sampled outputs matched. It was still rejected because
the end-to-end long-context gate did not preserve all latency targets.

| Prompt Shape | Concurrency | `BLOCK_M=16` Mean TTFT | `BLOCK_M=32`, `BLOCK_N=256` Mean TTFT | Decision |
| --- | ---: | ---: | ---: | --- |
| 64K synthetic | 1 | 13.394 s | 13.972 s | reject |
| 64K synthetic | 2 | 19.798 s | 19.846 s | reject |
| 64K synthetic | 4 | 34.065 s | 34.336 s | reject |
| 128K synthetic | 1 | 33.264 s | 33.691 s | reject |
| 128K synthetic | 2 | 49.199 s | 49.344 s | reject |
| 128K synthetic | 4 | 82.181 s | 80.187 s | positive but insufficient |

The C=4 128K result was positive, but the 64K and 128K C=1/C=2 regressions
violate the promotion rule for single-stream and small-concurrency latency.
The code change was removed; do not reintroduce this tile unless a later change
also fixes the lower-concurrency regressions.

### FP8 MQA Logits `BLOCK_M=32`, `BLOCK_N=128`

This tile was tested separately after the `BLOCK_M=32`, `BLOCK_N=256`
rejection because it was a more conservative variant: the standalone
late-context microbench had shown it faster than `BLOCK_M=16`,
`BLOCK_N=128`, while keeping the logits column tile at 128. It also passed a
127K C=1 smoke with a small mean TTFT improvement.

The full latency gate was mixed. Long-context latency improved across all
64K/128K C=1/2/4 rows:

| Prompt Shape | Concurrency | `BLOCK_M=16`, `BLOCK_N=128` Mean TTFT | `BLOCK_M=32`, `BLOCK_N=128` Mean TTFT | Delta |
| --- | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 13.394 s | 13.297 s | -0.7% |
| 64K synthetic | 2 | 19.798 s | 19.459 s | -1.7% |
| 64K synthetic | 4 | 34.065 s | 33.076 s | -2.9% |
| 128K synthetic | 1 | 33.264 s | 32.195 s | -3.2% |
| 128K synthetic | 2 | 49.199 s | 47.900 s | -2.6% |
| 128K synthetic | 4 | 82.181 s | 78.647 s | -4.3% |

It was still rejected because the fixed promotion gates did not hold:

| Gate | `BLOCK_M=16`, `BLOCK_N=128` | `BLOCK_M=32`, `BLOCK_N=128` | Decision |
| --- | ---: | ---: | --- |
| 4K synthetic C=1 mean TTFT | 2.766 s | 1.138 s | positive |
| 4K synthetic C=2 mean TTFT | 1.455 s | 1.472 s | reject |
| 4K synthetic C=4 mean TTFT | 1.932 s | 2.186 s | reject |
| GSM8K `exact_match_flexible` | 0.95 | 0.94 | reject |

The code change was removed. This result is worth keeping as evidence that
larger row tiles can help long-context prefill, but correctness and
short-context gates must be fixed before revisiting it.

### FP8 MQA Logits `BLOCK_D=128`

This variant kept the promoted `BLOCK_M=16`, `BLOCK_N=128` launch shape and
changed only the dot tile from `BLOCK_D=64` to `BLOCK_D=128`, covering the
full head dimension in one dot. It looked promising in isolation:

- late-context microbench improved from roughly 14.55 ms to 12.76 ms;
- a 127K C=1 smoke improved mean TTFT from the `BLOCK_M=16` smoke value of
  34.196 s to 32.763 s, with zero request failures.

It was still rejected by the first full-gate phase. The short-context 4K
C=1/C=2/C=4 latency means were positive, but the C=4 row had one failed
request: the response missed one required retrieval term. Because this is a
correctness failure in the fixed gate, the long-context and GSM8K phases were
not promoted as evidence for this candidate.

The code change was removed. Do not revisit this exact `BLOCK_D=128` variant
unless a later numerical/correctness analysis explains the short-context
retrieval miss.

### FlashInfer Autotune Recheck After vLLM PR 42857

After rebasing onto upstream with vLLM PR 42857, FlashInfer autotune can be
enabled again without the earlier startup failure. It was rechecked against the
same 131K long-context gate, prefix cache disabled, 4096 max-num-batched-tokens,
TP=2, MTP=2.

The long-context TTFT result was neutral to slightly negative for this
DeepSeek V4 SM120 path:

| Prompt Shape | Concurrency | Autotune Off Mean TTFT | Autotune On Mean TTFT | Delta |
| --- | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 13.957 s | 13.911 s | -0.3% |
| 64K synthetic | 2 | 20.077 s | 19.876 s | -1.0% |
| 64K synthetic | 4 | 33.279 s | 33.492 s | +0.6% |
| 128K synthetic | 1 | 33.298 s | 33.590 s | +0.9% |
| 128K synthetic | 2 | 48.198 s | 48.265 s | +0.1% |
| 128K synthetic | 4 | 80.107 s | 81.556 s | +1.8% |

Both runs reported the same KV budget, about 11.34 GiB available KV cache,
755,050 GPU KV-cache tokens, and 5.76x maximum concurrency at 131,072 tokens.
The autotune-on run logged that no FlashInfer autotune cache entries were found
and fell back to default tactics, so this is not a current optimization lever
for the active path. The autotune-off comparison run had one 64K C=4 retrieval
miss; the autotune-on run passed this one-shot matrix, but do not treat that as
proof of a correctness improvement without repeated correctness gates.

Decision: keep upstream's fixed autotune behavior available, but do not spend
more 128K prefill optimization time here unless a later profile shows this
path is actually on the critical path.

### Long-Context Matrix Warmup Sensitivity

A same-service follow-up ran the default `autotune_on` configuration twice
without restarting vLLM. The first pass included the usual 4K prewarm; the
second pass reused the same service process and skipped that prewarm.

| Prompt Shape | Concurrency | Earlier `autotune_on` | Same-Service First | Same-Service Second |
| --- | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 13.911 s | 12.054 s | 12.522 s |
| 64K synthetic | 2 | 19.876 s | 18.633 s | 19.386 s |
| 64K synthetic | 4 | 33.492 s | 32.540 s | 33.793 s |
| 128K synthetic | 1 | 33.590 s | 29.866 s | 29.941 s |
| 128K synthetic | 2 | 48.265 s | 45.358 s | 45.541 s |
| 128K synthetic | 4 | 81.556 s | 76.016 s | 78.073 s |

The same-service second pass was not faster than the first, so this is not
evidence that prefix reuse or repeated prompt cache effects are driving the
result. It is evidence that one-shot long-context latency is sensitive to
process, compile-cache, or system state. The serve logs still reported first
inference-time JIT events for the FP8 MQA logits, rowwise logits, top-k
combiner, FP8 einsum, and prefill metadata kernels.

Decision: use repeated measurements, preferably reporting min/median and
failures, before putting 64K/128K numbers in the PR body. Separately evaluate a
startup warmup plan that deliberately covers the late-context kernel shapes
instead of relying only on the current 4K prewarm.

### Long-Context MTP Correctness Recheck

A repeat-count-3 long-context gate was run after the same-service warmup
finding, still using the active default: prefix cache disabled, 131K
max-model-len, 4096 max-num-batched-tokens, TP=2, MTP=2, and 64-token
synthetic completions. Artifact label:
`repeat_gate_20260519032549`.

| Prompt Shape | Concurrency | Requests | Failures | Mean TTFT | Min TTFT | Max TTFT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 3 | 0 | 12.106 s | 12.065 s | 12.166 s |
| 64K synthetic | 2 | 6 | 0 | 19.015 s | 12.923 s | 25.191 s |
| 64K synthetic | 4 | 12 | 2 | 32.321 s | 13.385 s | 51.614 s |
| 128K synthetic | 1 | 3 | 0 | 30.063 s | 30.024 s | 30.119 s |
| 128K synthetic | 2 | 6 | 0 | 45.732 s | 30.588 s | 61.830 s |
| 128K synthetic | 4 | 12 | 0 | 77.252 s | 30.997 s | 129.329 s |

The two failures were both 64K C=4 retrieval misses for the middle sentinel.
Because those completions hit the 64-token output cap, a targeted 64K C=4
rerun increased the completion cap to 128 tokens. Artifact label:
`target_64k_c4_max128_20260519034448`. It still failed 2 of 12 requests.
The failed responses ended normally and had enough room to answer, but returned
`beta-epsilon-29` for the middle indexer instead of the expected
`beta-quartz-29`. That makes this a correctness miss, not an output-budget
artifact.

The same targeted 64K C=4 shape without MTP passed 12 of 12 requests at
`max_tokens=128` (`target_64k_c4_nomtp_max128_20260519034951`), although
elapsed time was slower because there was no speculative decode speedup.
Trying MTP=1 as a conservative fallback was not usable:
`target_64k_c4_mtp1_max128_20260519035535` failed all matrix requests after
EngineCore hit `RPC call to sample_tokens timed out`. The scheduler snapshot in
the failure log showed concurrent cached requests with
`scheduled_spec_decode_tokens` values of `[-1]`.

Decision: do not promote MTP=2 long-context C=4 as correctness-clean yet, and
do not use MTP=1 as the fallback. Keep no-MTP as the correctness control while
investigating whether the C=4 miss is in speculative acceptance, draft logits,
or scheduler interaction. PR-facing 64K/128K numbers should include repeated
failure counts or be limited to configurations that pass the fixed correctness
gate.

### Long-Context MTP Acceptance Isolation

Follow-up A/B runs kept the same targeted shape unless noted otherwise:
synthetic 64K prompt, C=4, repeat count 3, `max_tokens=128`, prefix cache
disabled, 131K max-model-len, 4096 max-num-batched-tokens, TP=2, MTP=2.

| Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Default MTP=2 | 12 | 2 | 32.069 s | 46.355 s | reject |
| No MTP | 12 | 0 | 32.648 s | 52.765 s | correctness control |
| MTP=2, CUDA graph disabled, GPU memory util 0.95 | 12 | 2 | 33.796 s | 48.885 s | reject |
| MTP=2, `disable_padded_drafter_batch=true` | 12 | 2 | 33.879 s | 49.023 s | reject |
| MTP=2, synthetic rejection, acceptance rates `[0.0, 0.0]` | 12 | 0 | 33.403 s | 54.542 s | diagnostic only |

The failed CUDA-graph-disabled run returned middle-marker variants such as
`основним` and `beta-tungsten-29`; the failed padded-drafter-disabled run
again returned `beta-epsilon-29`. Both still missed `beta-quartz-29`, so
CUDA graph capture, async scheduling, and the padded drafter batch are not
sufficient root causes.

The synthetic-rejection run is the important narrowing result. It forced a
zero acceptance rate while still running MTP=2 target verification, and it
passed all 12 requests. That means the first target verification position is
correct for this shape; the correctness miss appears only when later draft
tokens are accepted and the request advances along the multi-token MTP
verification trajectory. Do not promote synthetic rejection as an optimization:
it removes the MTP speedup and exists only as a diagnostic control.

Additional 62K-token runs narrowed the active failure boundary:

| Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| MTP=2, C=1 | 3 | 0 | 13.083 s | 13.616 s | pass |
| MTP=2, C=2 | 6 | 0 | 20.237 s | 27.011 s | pass |
| MTP=2, C=3 | 9 | 1 | 27.586 s | 39.729 s | fail |

This confirms the active bug is not single-stream long-context retrieval. It
starts once the small-concurrency batch reaches about three concurrent
long-context requests.

One targeted code experiment forced DeepSeek V4 sparse indexer decode away
from the native `(B, next_n)` path and into the flattened decode path for
multi-token spec decode. It did not fix the correctness miss:

| Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Flattened indexer decode, C=3 | 9 | 2 | 27.228 s | 39.204 s | reject |
| Flattened indexer decode, C=4 | 12 | 1 | 34.497 s | 49.254 s | reject |

The code change was removed. The failure is therefore not explained solely by
the native sparse-indexer multi-token decode layout.

Request-level tracing of a failing C=3 run provided a more precise location.
The failed request answered `beta-cobalt-29` instead of `beta-quartz-29`. At
the divergence step, the draft proposed token ids for `beta-qu...`; target
verification accepted the first token `beta` but rejected the second draft
token and selected the token for `-c` instead. The next step then continued
with `obalt-29`.

That trace means the failure is not an unchecked draft-token acceptance. The
target verification logits are already wrong for the second verification
position after the first accepted draft token, in a small-concurrency
long-context batch. Keep the investigation on target multi-token verification:
positions, slot mapping, KV writes/reads, and sparse context selection for
query positions after the first accepted token.

Additional A/B checks on the current branch did not change the decision:

| Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `VLLM_TRITON_MLA_SPARSE_MATMUL_DECODE=0`, C=3 | 9 | 1 | 28.782 s | 41.508 s | reject |
| `--no-async-scheduling`, C=3 | 9 | 2 | 28.862 s | 41.764 s | reject |
| `--enforce-eager`, GPU memory util 0.90, C=3 | 9 | 2 | 29.053 s | 42.794 s | reject |

Forcing sparse MLA fully off was not a valid comparison on this checkout
because the required FlashMLA extension was not available. An eager run at the
normal 0.985 GPU-memory budget also failed startup with Triton out-of-memory
during warmup; the lower-memory eager run above did start and still reproduced
the retrieval miss. These results make the materialized-matmul sparse decode
path, async scheduling, and CUDA graph capture insufficient explanations.

One setup mistake is also recorded so it is not reused as evidence: a
CUDA-graph-disabled run with line count 1000 passed 12 of 12 requests, but the
prompt was only about 31K tokens, not the intended 64K shape.

### Long-Context MTP History Check

The 64K C=4 `max_tokens=128` correctness miss was checked against historical
vLLM points to avoid blaming the latest rebase or the later rowwise/logits
kernel work without evidence.

| Ref / Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| pre-rebase HEAD `055e9f43c` | 12 | 1 | 31.910 s | 45.563 s | fail, predates latest rebase |
| `5fb7de094` MTP scheduling, first run | 12 | 0 | 99.204 s | 141.632 s | insufficient sample |
| `5fb7de094` MTP scheduling, repeat count 6 | 24 | 3 | 99.554 s | 142.650 s | fail, earliest comparable bad point |
| `215dfa944` MTP warmup | 12 | 2 | 99.312 s | 142.238 s | fail |
| `f05821715` dense FP8 configs | 12 | 3 | 97.508 s | 139.426 s | fail |
| `d26d266c8` adaptive MQA logits `BLOCK_M` | 12 | 1 | 97.586 s | 139.013 s | fail |
| `b301fd8ae` multi-request warmup coverage | 12 | 1 | 97.400 s | 139.976 s | fail |
| `be62c58ed` rowwise paged-MQA restore | 12 | 1 | 97.288 s | 138.789 s | fail |
| current, sparse MLA warmup disabled | 12 | 2 | 33.879 s | 48.814 s | fail |

All failures had the same shape: the model answered the first and final
sentinels correctly but returned a nearby or unrelated middle sentinel instead
of `beta-quartz-29`. The historical run against the pre-rebase HEAD reproduces
the miss, so the latest rebase is not the root cause. The wider repeat on
`5fb7de094` also reproduces the miss, so later rowwise/top-k/logits commits are
not the sole cause, even if they may affect speed or failure rate.

The direct parent `1ed872206` is not a valid good/bad comparison for this
shape: it fails engine startup with an Inductor assertion while compiling the
MTP model (`LayerName` passed where a Tensor is expected). Treat
`5fb7de094` as the earliest comparable failing point currently available.

Disabling the DeepSeek V4 sparse MLA warmup on the current branch did not fix
the correctness miss. That makes startup warmup-state pollution an insufficient
explanation. Keep the investigation centered on the accepted multi-token MTP
scheduling/verification trajectory, using no-MTP and synthetic-reject-0 as
controls.

## Latest Upstream Cleanup, 2026-05-19

After rebasing onto the upstream DeepSeek V4 module refactor, the active SM120
environment resolves the fused indexer Q path through Cutedsl first. The older
Triton `fused_indexer_q` `num_warps` autotune delta is therefore fallback-only
for this host and added review surface without affecting the measured path.
Decision: remove that autotune delta from the active branch; keep the upstream
fallback shape unchanged until a non-Cutedsl target needs it measured again.

The same cleanup pass replaced direct `vllm.third_party.deep_gemm` imports in
DeepSeek V4 MegaMoE with the existing `vllm.utils.deep_gemm` wrapper. This keeps
external `deep_gemm` installs and vendored fallbacks behind one import policy.
The retained regression test exercises `finalize_weights()` through the wrapper
without requiring the vendored package to exist.

The broader prefix-cache gate exposed a real MLA protection bug: hybrid
coordinators align cacheable tokens down to the LCM boundary, so a 35-token
prompt with a 32-token cacheable prefix did not satisfy the previous
`num_tokens >= request.num_prompt_tokens` protection condition. Under decode or
allocator pressure, SWA/MLA prompt blocks could then be evicted before a future
same-prompt reuse. Decision: keep the fix that protects blocks once the
aligned cache-hit prefix has been cached, not only after the entire prompt has
crossed the boundary.

Verification summary:

| Gate | Result |
| --- | --- |
| vLLM targeted unit/static group | `117 passed` for env/core prefix-cache/sparse-SWA, plus `18 passed` for MegaMoE/MTP/SM120 fallback/quant/disagg; ruff, compileall, and diff-check passed |
| Short HF/MT-Bench smoke | C=1/2/4 all `16/16` successful; C=4 output tok/s `197.08`, MTP acceptance `63.65%` |
| 64K/128K cold long-context smoke, hot service | 64K C=1 `13.561 s`, C=2 `20.904 s`; 128K C=1 `33.328 s`, C=2 `50.572 s`; zero failures |
| GSM8K correctness gate | 5-shot limit-200 `exact_match_flexible=0.965` versus baseline `0.950`; compare gate passed |

## User-Reported Prefix-Cache HTTP Stress, 2026-05-21

The reporter in
[`vllm-project/vllm#41834` comment 4507780873](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4507780873)
shared a compact reproducer for the earlier prefix-cache failure: non-streaming
OpenAI chat requests, one solo multi-turn session followed by two concurrent
multi-turn sessions, with `/metrics` deltas before and after each segment. The
original bad branch reset or disconnected while reading `/metrics`; newer
branches completed normally on the reporter's host.

Harness action: add `prefix_cache_stress` as a first-class phase and
`scripts/run_sm120_mtp1_prefix_cache_stability.sh` for the local TP=2, MTP=1,
FP8 KV, prefix-cache-on, 16K max-model-len, block-size-256,
FULL_AND_PIECEWISE shape. This gate is intentionally separate from
`prefix_cache_probe`: it checks server stability and `/metrics` continuity, not
whether prefix-cache TTFT ratios meet a performance threshold.

Validation on the current PR branch used artifact label
`codex_user4507780873_mtp1_prefix_stress_20260521`:

| Gate | Result |
| --- | --- |
| Server startup | pass |
| `prefix_cache_stress` | 5/5 trials passed, 0 failures |
| HTTP health | 200 |
| Solo prefix-cache hit rate mean | 60.1% |
| Concurrent prefix-cache hit rate mean | 67.0% |
| Runtime metrics | max running requests 2, max waiting 0, preemptions 0 |
| Serve log | avg prefill 269.40 tok/s, avg decode 156.22 tok/s |

Decision: the specific MTP=1 prefix-cache `/metrics` disconnect reported for
the older branch is not reproducible on the current PR branch under the
provided stress shape. Keep this as a user-reported stability gate for future
prefix-cache, scheduler, CUDA graph, and MTP changes.

## User-Reported Issue 10 Sparse MLA Prefill Stability, 2026-05-24

The issue reported in
[`jasl/vllm#10`](https://github.com/jasl/vllm/issues/10) is a 2x RTX PRO 6000
proxy for very long-context GB10 behavior. The local development host cannot
run beyond roughly 130K context, so the gate uses 131K max-model-len with
59K/124K synthetic prompts and C=1/C=2 cold requests. Earlier default
`VLLM_TRITON_MLA_SPARSE_TOPK_CHUNK_SIZE=512` reproduced a severe 124K C=2
failure: one request failed, the sparse MLA prefill
`_accumulate_indexed_attention_chunk_multihead_kernel` reported an unspecified
CUDA launch failure, and the driver entered a fatal state requiring a host
reboot.

Root-cause evidence from temporary shape instrumentation:

| Shape | 59K C=2 default | 124K C=2 |
| --- | ---: | ---: |
| C4A combined topk | 640, `lens_max=640` | 640, `lens_max=640` |
| C128A combined topk | 1152, `lens_max=588` | 1152, `lens_max=1097` |
| Batched request count in risky chunk | 2 | 2 |

The accepted change is deliberately narrow: when the user has not explicitly
set `VLLM_TRITON_MLA_SPARSE_TOPK_CHUNK_SIZE`, SM12x prefill uses topk chunk 256
only for C128A sparse MLA shapes with multiple requests in the same prefill
chunk and `combined_topk_size > 1024`. C=1, C4A, short-context, and explicit
environment overrides keep the existing 512 behavior.

Experiment outcomes:

| Experiment | Artifact label | Result | Decision |
| --- | --- | --- | --- |
| Disable Triton sparse MLA with `VLLM_TRITON_MLA_SPARSE=0` | `20260524_issue10_131k_sparse0_c2_cold` | invalid: current build does not provide the FlashMLA C++ extension path | reject |
| Force global topk chunk 256 | `20260524_issue10_topk256_59k_124k_c1c2_cold` | 124K C=2 passes, but 59K C=1/C=2 regresses versus 512 | reject |
| Keep default 512 for 59K | `20260524_issue10_topk512_59k_c1c2_cold_mlen131k` | 59K C=1 TTFT `12.325 s`, decode `132.09 tok/s`; C=2 TTFT `19.361 s`, decode `73.43 tok/s` | baseline |
| Adaptive C128A multi-prefill topk | `20260524_issue10_adaptive_59k_124k_c1c2_cold` | 4/4 groups pass, 0 failures; 59K C=1/C=2 stays at `12.319 s`/`19.213 s` TTFT and `133.70`/`74.16 tok/s`; 124K C=2 passes with TTFT `47.615 s`, decode `60.61 tok/s` | keep |
| Short-context and GSM8K smoke | `20260524_issue10_adaptive_short_gsm8k_smoke` | short C=1/2/4 output `149.24`/`248.76`/`392.97 tok/s`; GSM8K 5-shot limit-50 flexible `1.00`, strict `0.98` | keep |

Residual risk: this fixes the crash-prone sparse MLA prefill shape, not the
broader long-context C=2 fairness problem. Per-request decode can still be
imbalanced under mixed long-prefill pressure, so keep ITL p95/p99 and
per-request min/max decode in promotion gates.

## Sparse MLA Prefill Topk Follow-up, 2026-05-25

After the issue #10 guard, the high-risk C128A multi-request prefill shape uses
topk chunk 256, while C=1 kept the historical default 512. The follow-up tested
whether the lower-risk single-request C128A path could use a larger chunk to
reduce sparse-MLA prefill loop overhead without reintroducing the multi-request
crash risk.

Retained behavior:

- Explicit `VLLM_TRITON_MLA_SPARSE_TOPK_CHUNK_SIZE` overrides remain
  authoritative.
- SM120 C128A single-request prefill with `combined_topk_size > 1024` now uses
  topk chunk 1024.
- SM120 C128A multi-request prefill with `combined_topk_size > 1024` keeps the
  conservative topk chunk 256 guard.
- C4A, short-context, and other lower-risk shapes keep the existing default
  behavior.

Full user-feedback matrix comparison, baseline
`20260524_ds4_harness_frontier_semantic_baseline_r2` versus candidate
`20260525_single_c128a_topk1024_full_gate`:

| Metric | Baseline | Topk 1024 Candidate | Decision Signal |
| --- | ---: | ---: | --- |
| 59K C=1 TTFT | `12.280 s` | `12.307 s` | no material movement |
| 59K C=2 TTFT / ITL p99 | `19.366 s` / `0.133 s` | `19.659 s` / `0.134 s` | no material movement |
| 124K C=1 TTFT | `31.206 s` | `31.169 s` | no material movement |
| 124K C=2 TTFT / decode | `47.972 s` / `60.953 tok/s` | `47.691 s` / `62.615 tok/s` | small positive |
| Mixed `decode_then_124k` secondary TTFT | `32.199 s` | `31.959 s` | small positive |
| Streaming pressure failures / slow cases | `0 / 0` | `0 / 0` | stable |
| Short C=1/2/4 output | `162.39` / `256.62` / `391.27 tok/s` | `162.22` / `256.70` / `394.07 tok/s` | no regression |
| Random prefill 65K TTFT | `14305.93 ms` | `14223.71 ms` | small positive |
| DS4 story recall semantic | `16/16` | `16/16` | stable |
| GSM8K limit-200 flexible / strict | `0.960` / `0.940` | `0.955` / `0.945` | above floor |
| Prefix-cache stress fillers 100-3200 | all pass | all pass | stable |

Decision: keep the single-request C128A topk 1024 relaxation. Treat the
measured benefit as small, not a major latency breakthrough. The value is that
it preserves the issue #10 multi-request crash guard while recovering a little
headroom in the lower-risk C=1 and mixed matrix, with no observed correctness,
CUDA graph, prefix-cache, or short-context regression.

Rejected query chunk sweep:

| Experiment | Artifact label | Result | Decision |
| --- | --- | --- | --- |
| `VLLM_TRITON_MLA_SPARSE_QUERY_CHUNK_SIZE=128` | `20260525_query_chunk128_probe` | 59K C=2 TTFT `21.487 s`, decode min/max `0.076`, ITL p99 `0.290 s`; 124K C=2 TTFT `52.527 s` | reject |
| `VLLM_TRITON_MLA_SPARSE_QUERY_CHUNK_SIZE=384` | `20260525_query_chunk384_probe` | 59K C=2 TTFT `20.580 s`, decode min/max `0.070`, ITL p99 `0.290 s`; 124K C=2 TTFT `53.160 s` | reject |
| `VLLM_TRITON_MLA_SPARSE_QUERY_CHUNK_SIZE=512` | `20260525_query_chunk512_probe` | C=1/frontier looked acceptable, but 59K C=2 decode min/max fell to `0.073` and 124K C=2 to `0.097` | reject |

The rejected query-chunk experiments left no production code changes. Future
sparse-MLA prefill work should avoid broad query-chunk increases unless it is
paired with a shape-specific fairness and ITL improvement.

## DS4 Harness Absorption Baseline Plan, 2026-05-24

Baseline label: `20260524_ds4_harness_frontier_semantic_baseline`.

Scope: Phase A is harness-only. Do not change vLLM inference code before this
baseline is captured, and use the same matrix as the comparison point for later
prefill, decode-overlap, prefix-cache, or logprob-drift experiments.

Absorbed ideas from ds4:

- Context-frontier sweeps over fixed long prompt files, reporting the actual
  server `prompt_tokens` alongside TTFT and input/prefill throughput.
- Story-recall semantic scoring for `ds4_story_recall.txt`: all sixteen
  `Name=number` assignments must be present.
- A realistic security-audit prompt as a long agent/security latency and
  streaming sample, without making it a semantic correctness gate.

Formal gates remain unchanged:

- no server/CUDA/NCCL/driver regression,
- GSM8K limit-200 must not drop below the fixed floors,
- `FULL_AND_PIECEWISE` decode CUDA graph capture stays enabled,
- short-context and 59K/124K latency/fairness gates must not regress.

New development observations:

- `frontier_context_sweep` is included in local quality and user-feedback
  matrix summaries, but it is not a PR hard gate until the first stable
  same-host baseline is accepted.
- `ds4_story_recall_semantic` is a separate prompt-file correctness phase with
  a 128-token answer budget; keep it separate from the existing 59K/124K
  latency phase so that latency max-token settings remain comparable.
- Invalid inference experiments after this baseline must have their code
  removed and only be recorded in rejected notes.

DS4 inference audit follow-up:

- The DS4 native engine is single-session and serialized at the inference
  worker, so its implementation is not directly portable to vLLM's continuous
  batching scheduler.
- The parts worth absorbing are the engineering shape: fixed prompt frontier
  measurement, semantic long-prompt recall, exact KV/prefix-state thinking,
  and explicit safety around huge local model runs.
- `scripts/run_sm120_ds4_absorption_stress.sh` packages that safety shape for
  vLLM validation. By default it runs the user-feedback matrix and the safe
  issue #10 proxy, then records driver/GPU health snapshots around each phase.
  The known issue #8 128K-class crash proxy and the issue #10 128K-class proxy
  are opt-in only through their `*_ALLOW_HOST_REBOOT_RISK=1` guards.

## Must-Fix Crash Backlog, 2026-05-25

Keep these outside the default user-feedback matrix, but treat them as required
follow-up work before claiming the GB10 or high-risk issue #10 shapes are
stable:

- SM120 issue #8 long-decode proxy: a no-MTP, prefix-cache-enabled, TP=2,
  FP8 KV, block-size-256, chunked-prefill, `FULL_AND_PIECEWISE` local proxy
  with `SERVE_MAX_MODEL_LEN=131072`, `max_num_batched_tokens=4176`,
  `max_num_seqs=8`, disabled custom all-reduce, 124K synthetic prompt,
  C=1/C=2, and a 1024-token output budget reproduced a fatal driver state on
  the dual RTX PRO 6000 host. C=1 completed, but C=2 failed both requests
  during long prefill/decode pressure; the engine died through shared-memory
  broadcast cancellation after a worker failure, and the kernel log reported
  repeated NVRM assertions followed by `uvm encountered global fatal error
  0x60, requiring os reboot to recover` and `GPU lost from the bus`. The
  artifact label is `20260525_issue8_local_proxy_124k_c2_decode1024`.
  Post-reboot isolation did not make this a stable reproduction: the same
  C=1/C=2 cold shape with the 1024-token output budget passed under
  `20260525_issue8_recheck_original_124k_c1c2_mnbt4176_prefix_on_1024`, and
  narrower 124K C=2-only, C=1/C=2 256-token, and warm prefix-hit probes also
  passed without NVRM/Xid/UVM log signals. Keep the original fatal artifact in
  the crash backlog, but describe the RTX PRO 6000 issue #8 proxy as
  intermittent unless a future run reproduces it again.
- SM120 issue #10 proxy: the 128K-class dual-card proxy with prefix cache,
  chunked prefill, FP8 KV, MTP=2, block size 256, disabled custom all-reduce,
  and `FULL_AND_PIECEWISE` triggered a sparse MLA prefill CUDA launch failure
  and left one GPU in a fatal driver state requiring an OS reboot. The
  artifact label is `20260524_ds4_harness_frontier_semantic_baseline_r2`; the
  safe baseline summary excludes this diagnostic. The safer 59K-class MTP
  startup and prefix-cache proxy passed under
  `20260525_issue10_safe_59k_mtp_prefix_proxy`: long-context C=1/C=2 cold and
  warm latency had zero failures, prefix-cache stress had zero failures, and
  the follow-up kernel log check showed no NVRM/Xid/UVM signals. This supports
  the ordinary SM120 MTP/prefix path, not the 128K-class crash proxy or the
  GB10 dual-node 393K report.
- SM120 post-upstream-rebase startup/probe crash: after rebasing through
  upstream `f51bbc694`, the first full baseline attempt exposed a runtime
  dependency drift before measurement could begin. The newly restored
  `humming-kernels[cu13]` dependency pulled a CUDA 13.2 Python nvcc/CCCL stack
  into an environment otherwise pinned around CUDA 13.0, causing TileLang JIT
  startup failure with `CUDA compiler and CUDA toolkit headers are
  incompatible`. Downgrading the Python nvcc/CCCL stack to 13.0 instead hit the
  CUDA 13.0 `rsqrt`/glibc header conflict. Pointing TileLang at the system CUDA
  13.1 toolchain let the TP=2, MTP=2, FP8 KV, block-size-256,
  `SERVE_MAX_MODEL_LEN=131072`, `max_num_batched_tokens=4096`,
  prefix-cache-disabled, `FULL_AND_PIECEWISE` startup reach readiness, but the
  first long-context probe then failed at a 4096-token prefill slice with
  `Triton Error [CUDA]: unspecified launch failure` while loading/executing the
  generated Triton binary. The driver then reported repeated NVRM/UVM
  assertions and `GPU lost from the bus`, leaving one GPU unusable until reboot.
  The artifact label/run id is
  `20260526_post_upstream_f51bbc694_rebase_startup_smoke_cuda131/20260526233648`.
  Post-reboot rechecks on the same rebased code did not reproduce the fatal:
  59K-class startup/probe passed five consecutive default runs under
  `20260527_sm120_destructive_repro_loop_{1..5}`, 130K-class startup/probe
  passed twice under `20260527_sm120_130k_destructive_repro_loop_{1..2}_4200`,
  the issue #10 high-risk proxy passed under
  `20260527_issue10_high_risk_proxy_post_reboot`, and the issue #8 recheck
  passed under `20260527_issue8_recheck_post_reboot`. The host reported no
  NVRM/Xid/UVM signals after those runs. Keep this in the crash backlog as an
  intermittent or state-dependent fatal until a reduced reproduction identifies
  the first failing kernel; do not describe the reboot result as a fix.
  A later full local-quality baseline on the same rebased code,
  `20260527_post_rebase_f51bbc694_local_quality_full`, also did not reproduce
  the fatal: startup, long-context probe, 59K/124K latency matrix, frontier
  context sweep, story-recall semantic, 124K decode concurrency, mixed
  long/short arrival, streaming pressure matrix, short MT-Bench-style
  throughput, GSM8K limit-200, and random prefill sweep all completed without
  NVRM/Xid/UVM signals. The overall run still exited nonzero because
  acceptance bundled generation/tool-call/streaming checks had quality or
  per-case failures, not because the GPU or vLLM engine crashed. A follow-up
  exact `server_startup -> long_context_probe` replay passed three more fresh
  startup loops under
  `20260527_post_full_baseline_exact_startup_probe_loop_{1..3}`. This makes the
  original crash more likely to depend on boot/runtime state, cache/toolchain
  state, or a prior asynchronous CUDA error surfacing at Triton binary load,
  rather than a currently deterministic long-context shape on SM120.
- GB10 issue #10 report: the reporter rebuilt
  [`jasl/vllm#10`](https://github.com/jasl/vllm/issues/10#issuecomment-4529246012)
  at `a937d4b287` and still reproduced a reboot-only crash on a dual-node GB10
  cluster. The public repro shape is TP=2 across two nodes, `max_model_len`
  `393216`, `max_num_batched_tokens=16384`, `max_num_seqs=4`, prefix cache,
  chunked prefill, FP8 KV, block size 256, disabled custom all-reduce, MTP=2,
  and `FULL_AND_PIECEWISE`. The pasted log reaches checkpoint load and MoE
  prepare/finalize, but does not yet include the failing kernel or driver
  event.
- GB10 issue #13 report: a dual-node GB10 run against the PR branch produced
  [`CUBLAS_STATUS_INTERNAL_ERROR`](https://github.com/jasl/vllm/issues/13)
  during a 120K-class NIAH-style eval with `max_connections=2`. The successful
  samples scored correctly, but most requests failed with API connection errors
  after the engine died. The accompanying kernel log showed NVRM allocation
  failures followed by a GPU page-fault signal (`FAULT_PTE
  ACCESS_TYPE_VIRT_READ`), which makes this a high-priority GB10 driver/kernel
  crash-backlog item. Treat it as related to, but not proven identical with,
  issue #10 until a reduced replay isolates whether MTP, prefix cache, chunked
  prefill, sparse MLA, or the GB10 driver/runtime state is the first trigger.
- SM120 issue #12 W4A16 + Marlin MoE external gate: the reported four-card
  RTX PRO 6000 shape is outside the local two-card harness budget and depends
  on an external W4A16 artifact plus an AIME runner. Track it through
  `scripts/run_sm120_issue12_w4a16_marlin_gate.sh`, which fixes the serve
  shape to TP=4, MTP=1, FP8 KV, prefix cache disabled, block size 256,
  `max_model_len=65536`, `max_num_seqs=8`, `max_num_batched_tokens=8192`,
  sparse MLA head block size 4, `VLLM_USE_FLASHINFER_SAMPLER=0`, disabled
  custom all-reduce, safetensors load format, and `FULL_AND_PIECEWISE`. The
  reporter's first corruption symptom is plausibly covered by the upstream
  Marlin MoE SM12x arch-list fix already present in this branch, but their
  later CUDA illegal-memory-access result has not been validated here. Keep it
  in the external crash/correctness backlog until a four-card run proves both
  token correctness and post-run server/driver health.
- Accepted external SM120 fixes, 2026-05-27: absorb the small, dependency-free
  pieces from the recent community reports instead of switching to an unmerged
  FlashInfer/DeepGEMM stack. The branch now refuses block-FP8 layers in the
  Marlin FP8 kernel selector so DSv4 block-FP8 compressor layers fall through to
  the block-FP8-capable path even when operators force Marlin for W4A16/NVFP4
  MoE layers; DeepSeek V4 `wo_a` scale lookup accepts both the Marlin-renamed
  `weight_scale_inv` and the non-Marlin `weight_scale`; and Marlin MoE uses a
  graph-stable `c_tmp` upper bound plus per-launch shared-memory size while
  keeping the device maximum only for the CUDA function attribute. These map to
  the issues discussed in vLLM PRs
  [#43722](https://github.com/vllm-project/vllm/pull/43722),
  [#43723](https://github.com/vllm-project/vllm/pull/43723), and
  [#43730](https://github.com/vllm-project/vllm/pull/43730). They are targeted
  hardening for W4A16/NVFP4 and CUDA-graph Marlin MoE behavior, not a proven
  root-cause fix for the GB10 long-context crash reports.
- Harness note: the safe SM120 issue #10 proxy intentionally keeps streaming
  pressure at the 59K-class frontier. The 124K streaming shape belongs to the
  explicit high-risk path because it does not fit the safe
  `SERVE_MAX_MODEL_LEN=65536` budget once output tokens are included.

Next data to request or collect for the crash backlog: full serve log tail,
kernel/Xid or NVRM/UVM lines from the failing boot, whether the peer node also
enters a bad state, NCCL version and transport summary, PyTorch/CUDA/Cutlass
DSL/NCCL package versions, and a reduced replay matrix that varies only one of
MTP, prefix cache, chunked prefill, and sparse MLA per run. Do not run the
128K-class SM120 proxy again unless the host can be rebooted afterward.

## Rejected Scheduling Experiment: Extreme Long Prefill /16, 2026-05-24

Artifact label: `20260524_sched_extreme_long_prefill_probe`.

Experiment: keep the existing mixed decode/prefill policy for ordinary long
prefill chunks, but when an already-running decode was scheduled and a prefill
had more than 16 scheduling steps remaining, reduce that prefill chunk from
`max_num_batched_tokens / 8` to `/ 16`.

Decision: reject and remove the code. The experiment did not improve the
measured user-feedback workload, and it regressed multiple gates compared with
the prior healthy matrix `20260523_post_rebase_c8b85b7c_full3`:

| Metric | Prior healthy matrix | `/16` experiment |
| --- | ---: | ---: |
| 59K C=1 TTFT | `12.249 s` | `14.164 s` |
| 59K C=2 TTFT / ITL p99 | `19.335 s` / `0.132 s` | `23.457 s` / `0.553 s` |
| 124K C=1 TTFT | `31.157 s` | `38.082 s` |
| 124K C=2 TTFT / ITL p99 | `47.812 s` / `0.141 s` | `60.955 s` / `0.252 s` |
| mixed `decode_then_124k` decode min/max | `0.283` | `0.174` |
| streaming pressure ITL p99 | `0.855 s` | `1.184 s` |
| short bench C=1/C=2/C=4 output | `160.71` / `257.10` / `389.05 tok/s` | `144.21` / `252.15` / `382.50 tok/s` |
| GSM8K limit-50 flexible / strict | `0.955` / `0.925` | `0.94` / `0.92` |

Runtime monitoring was useful: all measured phases reported zero CUDA, NCCL,
driver, and engine error signals, so this was a performance/correctness gate
failure rather than a crash reproduction. The result argues against blindly
shrinking extreme prefill chunks. Future scheduling work should target a more
shape-aware policy, likely distinguishing active-decode protection from equal
long-prefill fairness, and must keep the same user-feedback matrix enabled.

## External Reference: DeepGEMM PR 324

DeepGEMM PR
[`deepseek-ai/DeepGEMM#324`](https://github.com/deepseek-ai/DeepGEMM/pull/324)
is useful as a design reference, but it should not be treated as a dependency
for the vLLM PR branch. The upstream DeepGEMM project may not accept the PR, and
vLLM may not accept relying on a DeepGEMM fork.

Useful ideas to study:

- FP8 MQA logits: `BLOCK_KV` / `BLOCK_N` around 128, Q/KV reuse, explicit
  register budgeting, and avoiding unnecessary epilogue work.
- Paged MQA: split-KV and scheduler choices for long-context decode and
  multi-turn reuse.
- Small-M GEMM / BMM: the A/B-swap idea for `M <= 32` is aligned with
  small-concurrency decode, but it is not the first lever for 128K cold prefill.

Ideas to avoid carrying over blindly:

- Full DeepGEMM fork integration.
- SM100/B200/B300 assumptions around TMEM, `tcgen05`, TMA, or datacenter HBM.
- Large C++/JIT kernel ports unless a small, measured vLLM-owned variant is the
  only way to remove a proven bottleneck.

## External Reference: vLLM PR 43477 / FlashInfer SM120 Sparse MLA

vLLM PR
[`vllm-project/vllm#43477`](https://github.com/vllm-project/vllm/pull/43477)
and its FlashInfer dependency
[`flashinfer-ai/flashinfer#3395`](https://github.com/flashinfer-ai/flashinfer/pull/3395)
are high-signal references for SM120 DS4 sparse MLA work. The route is not a
drop-in replacement for this branch yet: it depends on an unmerged FlashInfer
backend, an external DeepGEMM branch, and does not cover this branch's MTP,
GSM8K, prefix-cache, 59K/124K latency, mixed-arrival, or crash-stability gates.

As of the 2026-05-27 inspection, the PR is open and not draft. Its local diff
against upstream/main is roughly 23 files / 1751 insertions / 247 deletions.
The useful implementation ideas to study are:

- a new `SPARSE_MLA_SM120` FlashInfer backend built around
  `BatchSparseMLAPagedAttentionWrapper`,
- a `DSV4_SPARSE_MLA_SM120` model path that routes DeepSeek V4 sparse MLA
  through the same FlashInfer wrapper,
- DeepSeek V4 mHC and sparse-MLA warmup / autotune hooks, and
- DeepGEMM MXFP4 utility and CMake integration work.

Do not cherry-pick this route directly into the active Dev or PR branch. First
test it as a separate experiment branch because the current branch's customer
value is tied to validated NVFP4 / FP8-KV / MTP behavior, not only to the
alternate sparse-MLA backend.

Local no-MTP startup check, 2026-05-27:

- The PR head was tested as a separately built worktree against the same DS4
  TP=2, FP8-KV, `FULL_AND_PIECEWISE`, prefix-cache-disabled profile used by the
  active branch smoke.
- `20260527_pr43477_nomtp_post_install_smoke` failed before benchmark
  execution during worker startup. The first failure was
  `RuntimeError: Assertion error (csrc/apis/layout.hpp:59): Unknown SF
  transformation` from `deep_gemm.transform_sf_into_required_layout()` while
  post-processing FP8 block scales.
- `20260527_pr43477_nomtp_e8m0off_random256_smoke` repeated the startup with
  `VLLM_USE_DEEP_GEMM_E8M0=0`. The log confirmed DeepGEMM E8M0 was disabled,
  but startup still failed with the same assertion, now through the MXFP4 MoE
  scale packing path.
- Root cause hypothesis from the local evidence: this PR's attempted
  DeepGEMM MXFP4 scale pre-pack is not compatible with the current DeepGEMM
  layout transform on SM120. The DeepGEMM layout helper accepts the SM90 FP32
  layouts and SM100 packed-UE8M0 layouts, but the SM120/SM121 path falls
  through to `Unknown SF transformation` for the recipe used by the PR.
- `20260527_pr43477_nomtp_marlin_random256_smoke` forced
  `--moe-backend marlin`. That isolated the MoE path but still failed during
  FP8 linear weight post-processing through the PR's SM120 DeepGEMM linear
  route with the same scale-layout assertion.
- `20260527_pr43477_nomtp_marlin_tritonlin_random256_smoke` then forced both
  `--moe-backend marlin` and `--linear-backend triton`. That got past model
  loading, confirmed `MARLIN` for MXFP4 MoE, and reached the profile dummy run,
  but failed during `FULL_AND_PIECEWISE` torch.compile with
  `torch._inductor.exc.InductorError: AssertionError: auto_functionalized was
  not removed`. Do not treat eager mode or disabling graph capture as an
  acceptable fix for this branch.
- Keep the active branch's current SM120 backend selection and FP32-scale
  fallback behavior until a packed-scale DeepGEMM path is proven on
  SM120/SM121. This is a rejected experiment for now, not a performance
  regression caused by disabling MTP or CUDA Graph.

The
[`pasta-paul` comment](https://github.com/vllm-project/vllm/pull/43477#issuecomment-4531193899)
is a useful scope boundary:

- Treat NVFP4-FP8-MTP as the currently validated production route for
  `jasl/vllm@ds4-sm120-preview-dev`.
- Treat PR 43477's FlashInfer sparse-MLA + DeepGEMM MXFP4 route as
  complementary no-MTP work until MTP is wired and gated on the same matrix.
- Treat W4A16-FP8-MTP / Marlin wna16 as a separate backend-stability lane:
  native SM120 cubins such as
  [`vllm-project/vllm#40923`](https://github.com/vllm-project/vllm/pull/40923)
  can remove PTX-JIT corruption, but the reported `c_tmp` / workspace OOB
  issue still needs its own reproduction and fix. Do not mix that work into the
  NVFP4/MTP promotion branch.

The PR's most useful performance comparison shape is DS4 TP=2, FP8 KV,
`FULL_AND_PIECEWISE`, random ISL=8000 / OSL=1000, C=1/2/4/8/16/32. Track it
locally with the `bench_random_8000x1000` phase:

- `RUN_RANDOM_8K1K=1`
- `RANDOM_8K1K_INPUT_LEN=8000`
- `RANDOM_8K1K_OUTPUT_LEN=1000`
- `RANDOM_8K1K_CONCURRENCY=1,2,4,8,16,32`

This phase is now included in the SM120 local quality and user-feedback
profiles. Treat it as a diagnostic apples-to-apples comparison against the
FlashInfer sparse-MLA route, not as a promotion gate by itself.

Protocol calibration, 2026-05-29:

- The apparent MTP=2 C=1 gap (`~110-127 tok/s` versus PR 43477's `158.5 tok/s`)
  was mostly a benchmark-protocol mismatch. The local harness default used
  `temperature=1.0`; PR 43477's table should be compared against
  `temperature=0.0`.
- With the same TP=2, FP8 KV, prefix-cache-disabled, 65K max-model-len,
  `FULL_AND_PIECEWISE`, random 8000/1000, `temperature=0.0` protocol, the
  active branch matched PR 43477 on no-MTP and was comparable or faster on MTP=2
  for C=1/2/4:

| Variant | C | Active branch tok/s | PR 43477 tok/s | Ratio |
| --- | ---: | ---: | ---: | ---: |
| no-MTP | 1 | `90.51` | `88.1` | `1.03x` |
| no-MTP | 2 | `142.91` | `143.0` | `1.00x` |
| no-MTP | 4 | `211.03` | `211.5` | `1.00x` |
| MTP=2 | 1 | `153.47` | `158.5` | `0.97x` |
| MTP=2 | 2 | `220.51` | `205.5` | `1.07x` |
| MTP=2 | 4 | `275.58` | `197.4` | `1.40x` |

- MTP acceptance moved with temperature: `temperature=1.0` C=1 produced about
  `54%` acceptance and `127 tok/s`, while `temperature=0.0` produced
  `82-87%` acceptance and `153-158 tok/s`. Do not treat that difference as a
  sparse-MLA kernel regression.
- The currently installed official FlashInfer package still lacks
  `flashinfer.sparse_mla_sm120` / `BatchSparseMLAPagedAttentionWrapper`; enabling
  `--enable-flashinfer-autotune` alone does not activate PR 43477's custom
  SM120 sparse-MLA path.

External article reference:
[`22 轮才跑通：DeepSeek V4 MTP 番外`](https://mp.weixin.qq.com/s/qRk3sHeLz7ktHzaAshjDmg)
is valuable mostly as reproduction methodology, not as a direct benchmark
baseline. It independently describes the same split:

- `#41834` / this branch is the validated MTP-capable route on SM120.
- `#43477` is a second, more upstream-library-oriented FlashInfer + DeepGEMM
  route, but should be considered no-MTP until proven otherwise.
- CUDA 12.8 versus CUDA 13 can be the difference between MTP illegal-memory
  access and a clean run on this stack. Keep CUDA version, PyTorch CUDA build,
  `TORCH_CUDA_ARCH_LIST=12.0a`, `nvidia-cutlass-dsl`, expert parallel,
  `FULL_AND_PIECEWISE`, FP8 KV, and FlashInfer sampler state visible in
  artifacts and public recipes.
- Do not compare the article's random 1024/256 MTP numbers, PR 43477's 8000/1000
  no-MTP numbers, and this harness's 59K/124K long-context matrix directly.
  Use the same harness phase before making a promotion claim.
- MTP value is bounded by draft/target match quality. Always report acceptance
  rate, acceptance length, and, when available, per-position acceptance next to
  throughput so a dataset-driven acceptance change is not mistaken for a kernel
  improvement or regression.

Integration plan from these references:

1. Keep the current NVFP4-FP8-MTP branch as the stable line.
2. Use a separate experimental branch for PR 43477 / FlashInfer sparse MLA only
   if the dependency branch lands or a local fork experiment is explicitly
   requested.
3. Run `bench_random_8000x1000` first for the apples-to-apples shape, then the
   59K/124K, mixed-arrival, prefix-cache, crash-proxy, and GSM8K gates.
4. Do not prioritize PR 43477 absorption based only on the 8K/1K table; after
   protocol calibration the active branch already reaches that performance
   envelope.
5. Keep W4A16/Marlin wna16 reproduction and fixes in a separate branch and
   issue thread.

## External Reference: canada-quant NVFP4-FP8-MTP Harness

The
[`canada-quant/dsv4-flash-nvfp4-fp8-mtp`](https://github.com/canada-quant/dsv4-flash-nvfp4-fp8-mtp)
repo is a useful external user harness and artifact reproduction reference for
the
[`canada-quant/DeepSeek-V4-Flash-NVFP4-FP8-MTP`](https://huggingface.co/canada-quant/DeepSeek-V4-Flash-NVFP4-FP8-MTP)
model. Treat it as an external workload source, not as a direct source of
vLLM branch changes.

High-signal observations from the repo as of 2026-05-27:

- It separates the validated NVFP4-FP8-MTP route from the W4A16/Marlin wna16
  route. The W4A16 path carries separate SM120 Marlin correctness and
  workspace risks; do not mix those patches into the NVFP4/MTP branch without
  a dedicated reproduction.
- Its RTX PRO 6000 measurements use a four-GPU PCIe Server Edition host and
  MTP `num_speculative_tokens=1`. Those numbers are not directly comparable to
  this harness's two-GPU Workstation Edition, MTP=2, 59K/124K long-context
  gates.
- The reported TP=4 / C=8 thinking-mode collapse is consistent with the current
  product tradeoff: prioritize single-stream and small-concurrency latency, and
  treat high-concurrency TP-over-PCIe as a separate capacity / topology limit.
- Its methodology note on MTP acceptance is directly relevant: acceptance rate
  depends heavily on prompt shape and endpoint. Always pair acceptance with the
  exact prompt format, endpoint, output length, and throughput from the same
  run.

Useful workload shapes to consider absorbing into this harness:

- `vllm bench serve` random 256 input / 256 output, MTP on, concurrency
  `1,4,16`, with output tok/s, TPOT, and MTP acceptance from the same run.
- A small MTP acceptance smoke around 100 prompts, but rewritten to use the
  harness's artifact layout and metrics parser instead of ad hoc log parsing.
- GSM8K limit-50 as a quick smoke only; keep GSM8K limit-200 as the promotion
  floor for this branch.
- Optional AIME / thinking-mode concurrency sweeps only after the reasoning
  parser and MTP capture behavior are stable enough to avoid conflating parser
  drops with model or kernel correctness.

Ideas not to import blindly:

- One-line install scripts that patch arbitrary upstream revisions. This
  harness should keep the local vLLM checkout as the source of truth and record
  exact commits/artifacts.
- Canada-quant artifact-specific patches such as Marlin block-FP8 dispatch
  forcing, W4A16 workspace oversizing, or artifact key surgery unless the same
  failure is reproduced on the active branch and target artifact.
- Its published throughput numbers as branch baselines. Reproduce the same
  shapes locally before using them in PR-facing claims.

Immediate harness follow-ups from this review:

1. Done in harness after this review: extend the user-feedback summary for
   bench phases to include
   `spec_acceptance_length` and per-position acceptance, not only aggregate
   acceptance rate. The parser already extracts these fields; the summary now
   carries them through `user_feedback_matrix_summary.md/json`.
2. Done in harness after this review: add a short canada-quant-style random
   MTP bench phase, `bench_random_256x256`: random 256 input / 256 output,
   MTP on, concurrency `1,4,16`, with output tok/s, TPOT, TTFT, ITL p99,
   acceptance rate, acceptance length, and per-position acceptance. Keep it as
   a development observation first, not a hard PR gate.
3. Keep `bench_random_8000x1000` as the PR 43477 / FlashInfer no-MTP
   comparison shape. Do not replace it with the 256/256 shape; they answer
   different questions.
4. When publishing user-feedback matrix summaries, group external-user shapes
   separately from local development shapes so a single outside workload does
   not silently redefine the promotion criteria.
5. Add an artifact/environment check section that makes CUDA version, PyTorch
   CUDA build, `TORCH_CUDA_ARCH_LIST`, NCCL version, `FULL_AND_PIECEWISE`,
   prefix-cache mode, MTP `num_speculative_tokens`, and FlashInfer sampler
   state visible next to every promoted result.

Immediate vLLM experiment plan once the workstation is available:

1. Re-sync the workstation through the configured private SSH route, verify the
   harness commit and vLLM `ds4-sm120-preview-dev` commit, and confirm NCCL is
   still upgraded after any vLLM reinstall.
2. Run a lightweight current-branch smoke first: server startup, short MTP
   bench C=1/2/4, and GSM8K limit-50. This catches environment drift before
   long GPU jobs.
3. Sync the summary-only harness changes to the workstation and run a small
   phase smoke for the new 256/256 bench shape.
4. Run the balanced user-feedback matrix on the current Dev branch as the
   pre-experiment baseline, including 59K/124K, mixed arrival, streaming
   pressure, prefix-cache stress, issue10 proxy, GSM8K limit-200, random
   8000/1000, and the new 256/256 MTP observation.
5. Create a separate vLLM experiment branch for PR 43477 / FlashInfer sparse
   MLA. Start no-MTP only, because PR 43477 does not currently cover this
   branch's MTP path.
6. On that branch, run `bench_random_8000x1000` first. Continue to 59K/124K,
   mixed-arrival, prefix-cache, crash-proxy, and GSM8K only if the 8000/1000
   shape is stable and meaningfully better.
7. Only after a no-MTP FlashInfer route passes the same gates should MTP
   integration be attempted. If it does not pass, remove the code, keep only
   rejected notes, and do not pollute the active Dev branch.

Workstation follow-up on 2026-05-27:

- Current Dev branch and harness were rechecked on the two-card SM120
  workstation. vLLM was `0.21.1rc1.dev363+g27fd665bd`, NCCL was `2.30.4`,
  prefix cache was disabled, max model length was 65,536, and
  `FULL_AND_PIECEWISE` graph capture stayed enabled.
- Lightweight smoke `20260527_dev_light_smoke/20260527141628` passed
  `server_startup`, short MTP C=1/2/4, GSM8K limit-50, and random 256/256
  C=1/4/16 with zero serve, CUDA, NCCL, driver, or engine error signals.

| Shape | C | Output tok/s | ITL P99 | Spec Accept | Spec Accept Len |
| --- | ---: | ---: | ---: | ---: | ---: |
| Short MT-Bench MTP=2 | 1 | 144.77 | 13.04 ms | 63.55% | 2.27 |
| Short MT-Bench MTP=2 | 2 | 237.32 | 43.81 ms | 62.08% | 2.24 |
| Short MT-Bench MTP=2 | 4 | 369.05 | 45.46 ms | 63.03% | 2.26 |
| Random 256/256 MTP=2 | 1 | 154.65 | 13.16 ms | 52.76% | 2.06 |
| Random 256/256 MTP=2 | 4 | 344.64 | 67.41 ms | 53.34% | 2.07 |
| Random 256/256 MTP=2 | 16 | 664.81 | 40.96 ms | 52.61% | 2.05 |

GSM8K limit-50, 5-shot, MTP=2, C=4: flexible and strict exact match were both
`0.98`. Treat this only as a drift smoke; the promotion floor remains GSM8K
limit-200.

Because the canada-quant RTX PRO 6000 report uses MTP=1, a narrow same-host
MTP=1 256/256 comparison was also run under
`20260527_dev_mtp1_256x256_smoke/20260527142329`. It passed with zero serve,
CUDA, NCCL, driver, or engine error signals:

| Shape | C | Output tok/s | ITL P99 | Spec Accept | Spec Accept Len |
| --- | ---: | ---: | ---: | ---: | ---: |
| Random 256/256 MTP=1 | 1 | 148.43 | 11.57 ms | 73.44% | 1.73 |
| Random 256/256 MTP=1 | 4 | 370.36 | 66.72 ms | 76.39% | 1.76 |
| Random 256/256 MTP=1 | 16 | 702.76 | 33.64 ms | 73.15% | 1.73 |

Interpretation: MTP=1 is healthy on this short random external-user shape and
is slightly better than MTP=2 at C=4/C=16 in this small 16-prompt smoke, while
MTP=2 has a longer accepted-token step. This is useful for interpreting
canada-quant-style reports, but it is not enough to switch the Dev default:
the MTP=2 path remains the validated long-context/default branch until MTP=1
passes the same 59K/124K, mixed-arrival, GSM8K limit-200, prefix-cache, and
crash-proxy gates.

## Rejected Experiment: BF16 Torch MQA Top-K Fallback, 2026-05-30

A GB10 field report suggested changing
`_fp8_mqa_logits_topk_torch` from fp32 matmul inputs to bf16 tensor-core
matmul inputs and increasing `_SM120_MQA_LOGITS_MAX_SCORE_BYTES` from 64 MiB
to 1 GiB. The current Dev branch already differs from that report's older
commit because it has the SM120 direct Triton logits and custom row-top-k
fallbacks, so the hypothesis needed to be retested on the active branch.

Microbench evidence was mixed:

- DS4-like shape `m=1152, n=131072, h=128, d=512, topk=2048`:
  fp32 cap64 was `569.88 ms`; bf16 cap64 was `348.07 ms`.
- Raising the cap was not beneficial on the same shape: bf16 cap128/256/512/1024
  measured `465.18/478.79/483.15/505.91 ms`, with higher memory pressure.
- BF16 top-k selection was not bit-exact at this large shape. Average overlap
  versus fp32 cap64 was about `99.69%`, minimum about `99.32%`.

Endpoint A/B on the two-card SM120 workstation compared
`20260530_topk_prefill_current_local_gate` with
`20260530_topk_prefill_bf16_local_gate`, keeping TP=2, MTP=2, EP on, FP8 KV,
prefix cache disabled, `max_num_batched_tokens=4096`, and
`FULL_AND_PIECEWISE`.

| Shape | Metric | Current | BF16 top-k | Delta |
| --- | --- | ---: | ---: | ---: |
| 59K C=1 | TTFT | 12.097 s | 12.147 s | +0.4% |
| 59K C=1 | Decode | 139.55 tok/s | 132.48 tok/s | -5.1% |
| 59K C=2 | TTFT | 18.996 s | 19.047 s | +0.3% |
| 124K C=2 | TTFT | 46.989 s | 47.320 s | +0.7% |
| Mixed `long_then_short` | ITL proxy p99 | 0.601 s | 0.605 s | +0.7% |
| Streaming pressure | Max TTFT | 54.778 s | 55.917 s | +2.1% |
| Random 65K/1 C=1 | Mean TTFT | 14.360 s | 14.398 s | +0.3% |
| Random 65K/1 C=2 | Mean TTFT | 25.243 s | 25.367 s | +0.5% |
| Random 8K/1K C=1 | Output tok/s | 111.83 | 109.90 | -1.7% |
| Random 8K/1K C=2 | Output tok/s | 167.37 | 167.91 | +0.3% |
| Random 8K/1K C=4 | Output tok/s | 235.38 | 235.70 | +0.1% |

Decision: reject for the active Dev branch. The microbench shows bf16 can help
the isolated torch fallback, but the promoted endpoint shapes did not improve
and the large-shape top-k overlap is no longer exact. The 1 GiB cap should not
be copied blindly; on the DS4-like microbench it was slower and used more
memory than cap64. The temporary code change was removed. Revisit only if a
future profile proves the torch top-k fallback, not the current Triton/custom
top-k path or sparse prefill scheduling, is dominating an active workload.

## KV Lifecycle And Prefix-Cache Recoverability Gate, 2026-05-31

User feedback reported GPU KV cache usage carrying over across unrelated
sessions and climbing until repeated re-prefill. The new `kv_lifecycle_probe`
separates two cases:

- prefix cache disabled: idle KV usage should return near zero after completed
  and client-aborted long requests,
- prefix cache enabled: idle KV may retain cached blocks, but unrelated
  sessions must stay bounded and server/runtime health must remain clean.

Validation used TP=2, MTP=2, FP8 KV, `FULL_AND_PIECEWISE`, expert parallelism,
and 59K-class deterministic prompts.

| Topology | Prefix Cache | Requests | Final Idle KV | Max Idle KV | Runtime KV Peak | TTFT Shape | Errors |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 2x RTX PRO 6000 SM120 | disabled | 2 complete + 1 abort | 0.000% | 0.000% | 12.12% | ~10.2-10.6 s | 0 CUDA/NCCL/driver/engine |
| 2x RTX PRO 6000 SM120 | enabled | 3 complete + 1 abort | 5.894% | 5.894% | 16.43% | ~10.3-10.4 s | 0 CUDA/NCCL/driver/engine |
| 2x GB10 SM121 | disabled | 1 complete + 1 abort | 0.000% | 0.000% | 31.23% | ~67.8-68.6 s | 0 CUDA/NCCL/driver/engine |
| 2x GB10 SM121 | enabled | 2 complete + 1 abort | 10.869% | 10.869% | 37.62% | ~68.3-68.4 s | 0 CUDA/NCCL/driver/engine |

Decision: keep the gate in the user-feedback matrix. Current evidence does not
show a prefix-disabled KV lifetime leak on either tested SM12x topology. With
prefix cache enabled, KV retention is visible and expected, but stayed bounded
well below the 90% recoverability threshold in the tested shape. If future
reports show monotonic growth toward 95%, rerun this gate with larger
`KV_LIFECYCLE_SESSION_COUNT` or prompt line counts before changing vLLM code.

## Rejected Active-Decode 1/32 Very-Long Prefill Cap, 2026-05-31

After the KV lifecycle gate, the next narrow C=2 fairness question was whether
the retained active-decode plus very-long-prefill cap should tighten from
`max_num_batched_tokens // 16` to `// 32`. The hypothesis was that smaller
prefill chunks might raise the slow request's decode rate and further reduce
ITL tail latency. Same-host A/B used TP=2, MTP=2, FP8 KV, prefix cache
disabled, `FULL_AND_PIECEWISE`, 131K max-model-len, 4096
max-num-batched-tokens, max-num-seqs 4, and repeat count 3.

| Case | 1/16 Current | 1/32 Candidate | Decision Signal |
| --- | ---: | ---: | --- |
| 59K C=2 decode min | 31.665 tok/s | 31.936 tok/s | +0.9%, noise-level |
| 59K C=2 ITL p99 | 0.0887 s | 0.0877 s | -1.1%, noise-level |
| 124K C=2 TTFT mean | 47.826 s | 48.192 s | +0.8% regression |
| 124K C=2 decode min | 29.941 tok/s | 30.611 tok/s | +2.2%, too small |
| 124K C=2 decode min/max | 0.292 | 0.288 | slightly worse |
| `decode_then_124k` decode min | 42.495 tok/s | 42.377 tok/s | no improvement |
| `long_then_short` decode min/max | 0.568 | 0.551 | worse |

Artifact labels: `20260531_c2_fairness_current_a03c87c` and
`20260531_c2_fairness_cap32_experiment`.

Decision: reject and remove the 1/32 code. The retained 1/16 policy already
keeps 59K/124K C=2 ITL p99 around 0.09-0.10 s on the dual-card 128K shape.
Tightening further does not materially improve user-visible fairness and costs
TTFT or other mixed-arrival metrics. Future C=2 work should investigate a
different mechanism, such as admission/ordering or decode/prefill separation,
rather than only shrinking the active-decode prefill chunk again.

## Rejected No-Decode Very-Long 1/4 Waiting-Prefill Cap, 2026-05-31

A follow-up tested whether the no-active-decode very-long path should leave
more room for a waiting short prefill by tightening the cap from
`max_num_batched_tokens // 2` to `// 4`. The target was the `long_then_short`
shape, where a short prompt arrives while a 124K-class cold prefill is already
running.

The experiment did not materially help the target shape and regressed the
main C=2 long-context gate:

| Case | Current 1/2 Waiting Cap | 1/4 Waiting Candidate | Decision Signal |
| --- | ---: | ---: | --- |
| 124K C=2 TTFT mean | 47.826 s | 49.085 s | +2.6% regression |
| 124K C=2 TTFT max | 63.983 s | 71.381 s | +11.6% regression |
| 124K C=2 decode min | 29.941 tok/s | 29.376 tok/s | worse |
| 124K C=2 decode min/max | 0.292 | 0.287 | worse |
| `long_then_short` secondary TTFT | 30.325 s | 30.238 s | -0.3%, noise-level |
| `long_then_short` secondary ITL P99 | 0.0314 s | 0.0334 s | worse |

Artifact labels: `20260531_c2_fairness_current_a03c87c` and
`20260531_waiting_prefill_quarter_candidate`.

Decision: reject and remove the code and test. Do not tighten the
no-active-decode waiting-request cap for now. The target improvement is
noise-level, while the 124K C=2 TTFT max regression is too large.

## Rejected Mixed Long/Short Global 2048 Token Budget, 2026-05-31

After promoting the running-prefill fairness fix, a no-code scheduling probe
tested whether reducing the whole serve profile from 4096 to 2048
`max_num_batched_tokens` would help the `long_then_short` case. The hypothesis
was that smaller global prefill chunks might expose the short request to the
scheduler earlier.

The result was negative:

| Case | 4096 Current | 2048 Probe | Decision Signal |
| --- | ---: | ---: | --- |
| `long_then_short` primary TTFT mean | 31.539 s | 34.719 s | +10.1% regression |
| `long_then_short` secondary TTFT mean | 30.094 s | 33.894 s | +12.6% regression |
| `long_then_short` decode min/max | 0.585 | 0.274 | much worse |
| Runtime errors | 0 | 0 | stable but slower |

Artifact labels:
`20260531_running_prefill_fairness_user_feedback/20260531184641` and
`20260531_mixed_long_short_mbt2048_experiment/20260531202458`.

Decision: reject as a default or broad tuning direction. The mixed long/short
problem is not solved by globally lowering `max_num_batched_tokens`; it needs a
narrower admission, scheduling, or deployment-level strategy that does not
penalize normal 124K C=1/C=2 prefill.

## Accepted Direct MQA Chunked Top-K Fallback, 2026-06-01

The prior NCU evidence showed the direct FP8 MQA logits kernel at 128K-class
width was register/eligible-warp limited (`255` registers per thread and about
`16%` achieved occupancy), so small launch/tile changes were stopped. The next
algorithmic question was whether the SM120 direct-MQA top-k fallback could avoid
materializing one large `(num_q, seq_len_kv)` fp32 logits matrix.

The implemented candidate keeps the existing full-logits Triton path when the
matrix is below `_SM120_MQA_TRITON_TOPK_MAX_LOGITS_BYTES`, but when it would
previously fall through to the torch chunked path it now uses exact Triton
logits chunks plus per-row top-k merge. This is not a single fused streaming
top-k kernel, but it reduces live logits state for the large-fallback shape and
keeps the small/medium fast path unchanged.

Microbench artifacts are under `20260601_streaming_topk_probe`:

| Shape | Variant | Mean | Peak Allocated | Correctness Signal |
| --- | ---: | ---: | ---: | --- |
| `256 x 131072`, topk `2048` | current full-logits Triton | `2.77 ms` | `152 MiB` | reference |
| `256 x 131072`, topk `2048` | public dispatch after change | `2.73 ms` | `164 MiB` | exact vs full-logits |
| `256 x 131072`, topk `2048` | prototype chunked `32768` | `3.64 ms` | `125 MiB` | exact, but slower |
| `1152 x 131072`, topk `2048` | old torch chunked fallback | `129.10 ms` | `510 MiB` | `1151/1152` rows exact vs full Triton; one numerical boundary row |
| `1152 x 131072`, topk `2048` | forced full-logits Triton | `13.61 ms` | `675 MiB` | reference |
| `1152 x 131072`, topk `2048` | public dispatch after change | `14.70 ms` | `468 MiB` | exact vs forced full-logits |

Targeted endpoint gate
`20260601_streaming_topk_chunked_target_gate` passed server startup,
long-context latency matrix, GSM8K limit-50, random prefill sweep, and
random 256x256 (`exit 0` for every requested phase). Key smoke metrics:

| Gate | Result |
| --- | --- |
| GSM8K limit-50 | flexible/strict exact match `0.98` / `0.98` |
| Random prefill 65K/1 | input throughput `4623.76 tok/s`, mean TTFT `14.174 s` |
| Random 256x256 C=1/4/16 | output throughput `136.15` / `344.63` / `339.19 tok/s` |
| Runtime health | no CUDA/NCCL/driver/server error signals in requested phases |

The same run showed 59K/124K C=2 fairness still weak, so an A/B repeat-3
long-context gate compared the candidate with the old torch-fallback dispatch:

| Gate | Candidate | Old Dispatch | Interpretation |
| --- | ---: | ---: | --- |
| 59K C=1 TTFT mean | `12.169 s` | `12.209 s` | unchanged |
| 59K C=2 TTFT mean | `23.844 s` | `24.432 s` | unchanged/noise |
| 124K C=1 TTFT mean | `30.901 s` | `30.900 s` | unchanged |
| 124K C=2 TTFT mean | `60.903 s` | `60.848 s` | unchanged |
| 124K C=2 decode min/max | `0.124` | `0.124` | unchanged |

Decision: keep the chunked direct-MQA top-k fallback as a narrow large-logits
fallback improvement. It removes a severe torch fallback cliff for the
`>512 MiB` direct-MQA top-k shape without changing the normal full-logits
Triton fast path. Do not claim it fixes the current 59K/124K C=2 long-prefill
fairness problem; the old-path A/B reproduced the same slowdown, so that
belongs to the scheduler/admission workstream.

Further single-kernel fused streaming top-k should not be started as a quick
patch. Exact top-k with `topk=2048` would need either large per-row live state
or a more complex multi-stage selection design. The next kernel work should
only proceed with a concrete design that reduces live state beyond this chunked
merge and has gates for both long-context latency and semantic correctness.

## Active SM12x Prefill/Decode Profiling Plan, 2026-06-01

Current work is now explicitly split into three linked problems:

1. long-context prefill/TTFT and reliability;
2. 59K/124K C=2 fairness, measured by per-request decode min/max and ITL tail;
3. prefill/decode interference, which is the most likely mechanism behind the
   user-visible fairness problem but must be proven with traces before changing
   more kernels.

Hardware constraints matter enough that SM120 and SM121 should not share one
undifferentiated tuning story:

- RTX PRO 6000 Blackwell Workstation Edition is the SM120 target: 96GB GDDR7,
  about 1.8TB/s memory bandwidth, PCIe Gen 5, 600W power envelope, and no
  SM100-only TMA/TMEM/`tcgen05` assumptions. This is the right host for
  aggressive sparse-MLA kernel profiling, scheduler A/B, and 128K-class
  repeatability gates.
- DGX Spark / GB10 is the SM121 target: 128GB LPDDR5X UMA, 273GB/s memory
  bandwidth, 140W SoC envelope, integrated CPU/GPU, 10GbE plus ConnectX-7. It
  has much less memory bandwidth and power headroom than RTX PRO 6000, and UMA
  memory reporting can be misleading under pressure. Treat it first as a
  reliability and memory-lifetime target, then as a performance target.

Use two layers of evidence:

| Layer | Purpose | SM120 Default | SM121 / GB10 Default |
| --- | --- | --- | --- |
| End-to-end gate | User-visible acceptance and no-regression result | `run_sm120_user_feedback_matrix.sh`, repeat fixed 59K/124K C=1/C=2, mixed arrival, decode-concurrency, GSM8K | GB10 no-MTP 128K sentinel, KV lifecycle, decode-concurrency, then MTP as exploratory |
| Timeline trace | Explain whether prefill kernels interrupt decode cadence | `run_mixed_arrival_nsys_profile_launch.sh`, one mixed case per trace | Same tool only after startup/KV lifecycle is stable |
| Kernel microprofile | Decide whether kernel work is justified | NCU on `_accumulate_indexed_attention_chunk_multihead_kernel` and `_fp8_mqa_logits_kernel` | Optional only after crash risk is controlled; expect bandwidth/power limits sooner |
| Deployment probe | Decide whether single-instance best effort is enough | Simulate PD-style isolation only if C=2 ITL remains unacceptable after scheduler work | Consider PD/disagg earlier for long-context concurrent user testing, but do not claim throughput gains from it |

For repeatability, use
`scripts/run_sm12x_prefill_decode_interference_profiles.sh` to capture the
three standard mixed-arrival traces into one summary. It is only an
orchestrator around the existing per-case Nsight Systems launcher and does not
change the serve recipe or add any public tuning knob.

Immediate trace sequence:

1. `decode_then_124k`: an existing decode stream has emitted at least one token,
   then a 124K-class prefill arrives. This is the primary prefill/decode
   interference shape; compare top kernel time, launch order, and decode ITL.
2. `long_then_short`: a 124K-class prefill starts first, then a short request
   arrives. Previous scheduler traces showed the short request could complete
   prefill and emit a first token, then wait behind the leading long prefill.
   This should be kept separate from the kernel-boundary problem above.
3. `long+long C=2`: keep as the promotion fairness gate. Do not tune solely
   for `long_then_short` if it regresses 59K/124K C=2 TTFT or decode min/max.

Optimization candidates should be tried in this order:

1. Scheduler/admission changes that protect already-streaming decode without
   exposing a public user knob. Any candidate must keep
   `FULL_AND_PIECEWISE`, GSM8K, short C=1/2/4, and 59K/124K C=1/C=2 healthy.
2. Sparse-MLA prefill algorithm changes only if traces still show
   `_accumulate_indexed_attention_chunk_multihead_kernel` dominating while
   decode is active. Do not resume launch-only sweeps already rejected on
   2026-05-31.
3. FP8 MQA logits live-state work only for shapes that exceed the current
   full-logits threshold or regress the direct-MQA top-k fallback. The accepted
   chunked top-k fallback is a narrow large-shape fix, not a general fairness
   solution.
4. Deployment-level prefill/decode separation only if the best single-instance
   scheduler policy cannot control ITL p95/p99. vLLM's disaggregated prefill is
   a tail-ITL control tool, not a default throughput improvement, and it adds
   KV-transfer/TTFT overhead that is especially important on GB10.

### SM120 mixed-arrival trace evidence, 2026-06-01

The first Nsight Systems pass used the normal SM120 dev serve profile:
`TP=2`, `MTP=2`, FP8 KV, prefix cache disabled, block size 256,
`max_model_len=131072`, `max_num_batched_tokens=4096`, `max_num_seqs=4`,
expert parallel enabled, and `FULL_AND_PIECEWISE` CUDA graphs.

`decode_then_124k` completed cleanly. The existing decode stream had
TTFT 30.809s, decode 36.785 tok/s, and p99 inter-chunk 0.205s; the arriving
long request had TTFT 32.324s and decode 94.447 tok/s. The decode min/max
ratio was 0.389. Kernel time was dominated by
`_accumulate_indexed_attention_chunk_multihead_kernel` at 48.7%, followed by
`_fp8_mqa_logits_kernel` at 12.1%, Marlin MoE at 10.3%, NCCL all-reduce at
8.6%, and `_w8a8_triton_block_scaled_mm` at 5.0%.

`long_then_short` also completed cleanly but exposed a different problem. The
long request had TTFT 31.824s and decode 83.998 tok/s; the short request saw
TTFT 3.344s but then stretched to 30.506s elapsed, 2.319 tok/s, and a 26.480s
p99 inter-chunk gap. The kernel mix was similar:
`_accumulate_indexed_attention_chunk_multihead_kernel` at 49.2%,
`_fp8_mqa_logits_kernel` at 12.0%, Marlin MoE at 10.6%, NCCL at 9.1%, and
W8A8 matmul at 5.0%.

Interpretation: `decode_then_124k` is genuine prefill/decode interference with
sparse-MLA prefill and FP8 MQA logits dominating the captured window.
`long_then_short` is mostly RUNNING-queue/token-budget starvation: the short
request reaches first token quickly, but then waits behind the leading long
prefill. Keep these shapes separate when evaluating fixes.

The new three-case wrapper was validated after partial-state sparse MLA was
absorbed into Dev. Artifact
`20260601_prefill_decode_interference_profiles/20260601053228` used the same
SM120 serve recipe and all cases exited `0`; runtime summaries reported
CUDA errors `0` and NCCL errors `0`, and a post-run driver scan showed no new
Xid, UVM, GPU-lost, fatal, or launch-failure signals for the run window.

| Case | Primary TTFT | Secondary TTFT | Decode Min/Max | ITL P99 | Top Kernel |
| --- | ---: | ---: | ---: | ---: | --- |
| `decode_then_59k` | 12.002 s | 13.406 s | 0.264 | 0.201 s | `_accumulate_indexed_attention_partial_states_multihead_kernel` 40.9% |
| `decode_then_124k` | 29.379 s | 31.232 s | 0.323 | 0.211 s | `_accumulate_indexed_attention_partial_states_multihead_kernel` 43.7%, `_fp8_mqa_logits_kernel` 12.7% |
| `long_then_short` | 30.638 s | 3.263 s | 0.028 | 25.374 s | `_accumulate_indexed_attention_partial_states_multihead_kernel` 41.5%, `_fp8_mqa_logits_kernel` 12.6% |

Interpretation after partial-state remains the same. The `decode_then_*`
cases show bounded but real prefill/decode interference, with sparse-MLA
partial-state accumulate still dominating the capture and FP8 MQA logits still
the second attention-side target. `long_then_short` is not primarily a kernel
throughput problem: the short request reaches first token quickly, then hits a
25s-class inter-chunk gap. Continue to treat it as scheduler/admission or
deployment-isolation work, not as evidence that the decode kernel alone has
collapsed.

Rejected scheduler experiments from this pass:

- Later-short-decode prefill cap: focused scheduler tests passed, and the GPU
  gate exited cleanly, but changing the cap from 1/4 to 1/8 did not materially
  improve `long_then_short`. The short request still took 32.138s elapsed at
  about 2 tok/s with p99 1.961s, while the long request TTFT stayed around
  33.807s. Do not keep this code path.
- Full long-prefill deferral for a later short decode: the focused test proved
  the intended scheduling order, but the real SM120 gate failed with CUDA
  illegal memory access and NCCL watchdog termination. The failing scheduler
  output scheduled only the short decode while another long request remained
  running. Do not reintroduce this shape without a lower-level explanation of
  the CUDA graph/spec-decode/model-runner assumptions it violates.

### Next algorithm-level candidates

The current evidence rules out more cheap launch/tile tuning:

- Nsight Systems repeatedly puts `_accumulate_indexed_attention_chunk_multihead_kernel`
  at about half of captured CUDA kernel time and `_fp8_mqa_logits_kernel` at
  about 12% for the 124K mixed-arrival shapes.
- NCU showed low DRAM throughput on both kernels. SM120 is not simply GDDR7
  bandwidth-bound here; the dominant signals are low eligible warps, dependency
  stalls, and very high register pressure in FP8 MQA logits.
- Prior A/Bs rejected top-k chunk changes, query chunk reductions,
  `HEAD_BLOCK=4`, `num_warps=8`, direct MQA tile changes, BF16 torch top-k,
  and scheduler-only late-short-decode policies.

Therefore the next vLLM experiments should be algorithmic and narrow:

1. **Direct FP8 MQA streaming top-k prototype.**
   Replace the current large-shape path that repeatedly materializes
   `chunk_logits` and merges with `torch.topk` by a Triton prototype that
   computes scores and maintains per-row top-k candidates directly. The first
   version should cover only the existing SM120 FP8-Q / FP8-K direct prefill
   path: `q_scale is None`, `q_values.dim() == 3`, `k_values.dim() == 2`,
   DS4-compatible `head_dim`, and long `seq_len_kv`. Do not expose a user knob.
   Prove output parity against `fp8_fp4_mqa_topk_indices` on synthetic shapes
   before any endpoint run.

   Minimum evidence before keeping code:

   - unit/microbench parity for top-k indices on short, 32K, 64K, and 131K KV
     widths, with deterministic inputs that avoid ambiguous ties;
   - NCU confirming lower register pressure or shorter elapsed time than
     `_fp8_mqa_logits_kernel` plus merge-top-k, not just a different launch
     count;
   - endpoint gates: 59K/124K C=1/C=2, `decode_then_124k`,
     `long_then_short`, random prefill sweep, story-recall semantic, and
     GSM8K limit-200.

   Revert if the top-k set is not stable, if C=1 TTFT regresses, or if the
   59K/124K C=2 fairness floor worsens. This path is correctness-sensitive:
   a small top-k drift can later look like an attention or retrieval bug.

2. **Two-pass sparse-MLA prefill accumulate prototype.**
   The current accumulate kernel performs an online softmax over the candidate
   list inside one program for each token/head block. A two-pass variant would
   split large candidate lists into candidate tiles, write partial
   `(max_score, denom, acc)` states, then merge those partial states. The goal
   is not less arithmetic; it is shorter per-program dependency chains and
   better scheduler eligibility for long prefill chunks.

   Scope it tightly:

   - enable only when `combined_topk_size > 1024` and the scratch-state memory
     budget is acceptable;
   - keep the existing single-pass kernel for short prompts and small top-k;
   - start with a standalone microbench that reports scratch bytes, kernel
     count, elapsed time, eligible warps, registers/thread, and achieved
     occupancy;
   - then run only the same mixed-arrival and 59K/124K gates if the microbench
     is clearly positive.

   Revert if the extra launch and scratch traffic erase the shorter dependency
   chain, or if GB10/SM121 becomes less stable under UMA memory pressure. On
   GB10 this candidate is higher risk because LPDDR5X bandwidth and shared
   memory pressure are much tighter than RTX PRO 6000.

3. **Deployment-level prefill/decode isolation fallback.**
   If both kernel candidates fail or are too invasive, treat single-instance
   scheduling as best-effort and test a deployment policy instead: separate
   long-prefill admission from latency-sensitive decode, or use a PD/disagg
   style shape for customers who need multi-user 256K+ contexts. Record it as
   a tail-ITL control tradeoff, not as a raw throughput win; it adds KV transfer
   and TTFT overhead and is likely more important on GB10 than on RTX PRO 6000.

Current best-effort direction: do **not** promote another scheduler-only fix.
After the direct top-k decomposition, prioritize the two-pass sparse-MLA
accumulate design first because that kernel is about half of captured CUDA
kernel time in the mixed-arrival traces. Keep the direct FP8 MQA streaming
top-k prototype as a secondary experiment and require it to prove lower
register/live-state pressure in the logits computation itself; reducing the
`top_k_per_row_prefill` selection stage alone has too little headroom.

### Sparse-MLA Partial-State Accumulate Prototype, 2026-06-01

Branch: temporary vLLM branch `codex/sm120-sparse-mla-partial-state-experiment`.

This experiment implements the two-pass sparse-MLA accumulate idea for the
single-prefill SM120 Triton path only. The candidate writes per-candidate-tile
online-softmax states `(max_score, denom, acc)`, then merges those states before
the sink finish step. It intentionally does not change the multi-prefill path
because the first full-path probe made C=2 long-context TTFT worse.

Correctness coverage added on SM12x:

- partial-state merge equals the existing single-pass accumulate;
- partial-state accumulate plus merge equals single-pass accumulate;
- 3+ partial parts plus scratch-buffer swapping equals single-pass accumulate.

Remote targeted verification passed:

- `pytest tests/v1/attention/test_sparse_mla_backends.py -q -k partial_state`
  reported `3 passed`;
- `ruff check` on the touched sparse MLA files passed;
- `git diff --check` passed.

Same-protocol A/B against clean `ds4-sm120-preview-dev`:

| Gate | Clean | Candidate | Result |
| --- | ---: | ---: | --- |
| 59K C=1 TTFT mean | `12.146 s` | `11.790 s` | `-2.93%` |
| 124K C=1 TTFT mean | `30.835 s` | `29.788 s` | `-3.40%` |
| 59K C=2 TTFT mean | `23.741 s` | `23.849 s` | `+0.46%` |
| 124K C=2 TTFT mean | `60.773 s` | `60.601 s` | `-0.28%` |
| 59K C=2 ITL p99 | `0.854 s` | `0.842 s` | `-1.48%` |
| 124K C=2 ITL p99 | `1.148 s` | `1.082 s` | `-5.75%` |
| random prefill 1K input tok/s | `6068` | `6024` | `-0.74%` |
| random prefill 4K input tok/s | `6125` | `6302` | `+2.88%` |
| random prefill 16K input tok/s | `5611` | `5818` | `+3.68%` |
| random prefill 65K input tok/s | `4639` | `4807` | `+3.62%` |

Mixed-arrival repeat-3 result was mostly neutral-to-positive for long-prefill
TTFT, but not fully clean:

| Case | Metric | Clean | Candidate | Result |
| --- | ---: | ---: | ---: | --- |
| `decode_then_59k` | primary TTFT mean | `12.288 s` | `11.820 s` | `-3.81%` |
| `decode_then_59k` | secondary TTFT mean | `13.322 s` | `13.556 s` | `+1.75%` |
| `decode_then_59k` | ITL p99 | `0.137 s` | `0.167 s` | `+21.69%` |
| `long_then_short` | primary TTFT mean | `31.970 s` | `30.743 s` | `-3.84%` |
| `long_then_short` | secondary TTFT mean | `3.352 s` | `3.262 s` | `-2.67%` |
| `long_then_short` | secondary ITL p99 | `26.641 s` | `25.537 s` | `-4.14%` |

Initial decision: keep this as a candidate, not yet as promoted code. It gives
a repeatable C=1 and random-prefill TTFT/input-throughput improvement without
obvious C=2 long-context regression, but the `decode_then_59k` ITL p99 movement
needed another mixed-arrival repeat or trace before promotion. Revert if the
mixed decode-tail regression repeats or if GB10 shows higher stability risk
under the extra scratch-state workspace.

Follow-up trace and correctness gates:

| Gate | Clean | Candidate | Result |
| --- | ---: | ---: | --- |
| `decode_then_59k` nsys primary TTFT | `12.387 s` | `12.037 s` | candidate faster |
| `decode_then_59k` nsys p99 ITL | `0.207 s` | `0.204 s` | no trace-level regression |
| nsys sparse accumulate total | `22.596 s` single-pass | `20.144 s` partial-state + `0.897 s` merge | about `-6.9%` |
| GSM8K limit-200 5-shot | n/a | flexible `0.960`, strict `0.935` | passes fixed floor |
| prefix-cache disabled KV lifecycle | n/a | final idle KV `0.0%`, abort included | passes |
| MTP=1 prefix-cache stress | n/a | 5/5 trials, health `200`, concurrent hit rate mean `72.8%` | passes |
| prefix-cache enabled KV lifecycle | n/a | final idle KV `5.894%`, bounded under diagnostic `30%` threshold | passes |

The paired nsys run weakened the earlier mixed-arrival concern: both clean and
candidate showed about a 200 ms `decode_then_59k` p99 ITL under nsys overhead,
so the repeat-3 p99 movement was not evidence of a candidate-specific
regression.

After the three-case wrapper made the partial-state kernel visible as the top
mixed-arrival kernel, the sparse-MLA microbench gained a partial-state mode.
Target-shape smoke artifact
`20260601_partial_state_microbench_target/20260601054348`, on
`num_tokens=256`, `num_heads=64`, `head_dim=128`, `kv_tokens=131072`:

| Candidates | Mode | Calls/Parts | Mean | Accumulate | Merge | Interpretation |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 512 | single-pass | 1 | 0.374 ms | n/a | n/a | baseline |
| 512 | chunked 256 | 2 | 0.347 ms | n/a | n/a | slightly faster in isolation |
| 512 | partial-state 256 | 2 | 0.372 ms | 0.325 ms | 0.047 ms | no isolated speedup |
| 1024 | single-pass | 1 | 0.670 ms | n/a | n/a | baseline |
| 1024 | chunked 256 | 4 | 0.672 ms | n/a | n/a | same as baseline |
| 1024 | partial-state 256 | 4 | 0.682 ms | 0.588 ms | 0.094 ms | same to slightly slower in isolation |

Interpretation: the retained partial-state change should be treated as an
end-to-end scheduling/trace improvement for large prefill, not as proof that
the partial-state kernel is faster in a standalone microbench. Further
sparse-MLA work needs to reduce live state or total work; another local
chunk/part-size sweep is unlikely to buy much.

Full SM120 promotion matrix:
`20260601_partial_state_promotion_matrix/20260601030721`.

| Gate | Result |
| --- | --- |
| Matrix status | OK, all primary, prefix-cache, and KV-lifecycle phases exited `0` |
| 59K C=1 | TTFT mean `11.713 s`, decode `139.345 tok/s`, ITL p99 `0.022 s` |
| 59K C=2 | TTFT mean `23.535 s`, decode `70.112 tok/s`, decode min/max `0.113`, ITL p99 `0.301 s` |
| 124K C=1 | TTFT mean `29.687 s`, decode `105.038 tok/s`, ITL p99 `0.029 s` |
| 124K C=2 | TTFT mean `60.560 s`, decode `52.683 tok/s`, decode min/max `0.131`, ITL p99 `1.081 s` |
| Decode-concurrency 124K C=2 | TTFT mean `60.662 s`, decode min `13.629 tok/s`, decode min/max `0.143`, ITL p99 `1.099 s` |
| Mixed `decode_then_124k` | primary TTFT `29.907 s`, secondary TTFT `30.746 s`, decode min/max `0.404`, secondary ITL p99 `0.035 s` |
| Mixed `decode_then_59k` | primary TTFT `12.128 s`, secondary TTFT `12.983 s`, decode min/max `0.310`, secondary ITL p99 `0.022 s` |
| Mixed `long_then_short` | primary TTFT `30.903 s`, secondary TTFT `3.295 s`, decode min/max `0.025`, secondary ITL p99 `25.615 s` |
| Streaming pressure | 36 requests, 0 failures, 0 slow cases, max TTFT `56.683 s`, ITL p99 `0.971 s` |
| GSM8K limit-200 5-shot | flexible `0.955`, strict `0.940` |
| Random prefill sweep | 1K/4K/16K/65K input throughput `6159 / 6171 / 5736 / 4768 tok/s` |
| Prefix-cache stress | all filler sizes passed, 0 failures, concurrent hit rates `0.2709` to `0.9594` |
| KV lifecycle | prefix disabled final idle KV `0.0%`; prefix enabled final idle KV `5.894%` |
| Runtime health | no server unresponsive signal; CUDA/NCCL/driver/engine error counters all `0` |

Decision: the partial-state sparse-MLA candidate has enough SM120 evidence for
Dev-branch absorption. Final targeted rerun on the exact Dev commit passed:
`pytest tests/v1/attention/test_sparse_mla_backends.py -q -k partial_state`
reported `3 passed`, `ruff check` on the touched files passed, and
`git diff --check HEAD~1..HEAD` passed. The change is now on
`ds4-sm120-preview-dev` as `caea1cb55 Add SM120 sparse MLA partial-state
prefill`.

Do not promote it to the PR branch or use it for SM121 claims until GB10
startup, KV lifecycle, and a 128K-class long-context smoke pass. The remaining
`long_then_short` tail is not introduced by this candidate; it is the known
single-instance prefill/decode admission problem and stays in the separate
scheduler/deployment workstream.

GB10 no-MTP smoke after Dev absorption:

| Gate | Result |
| --- | --- |
| Serve startup | TP=2, PP=1, EP on, FP8 KV, prefix cache disabled, `max_model_len=131072`, `max_num_batched_tokens=4176`, `FULL_AND_PIECEWISE`; `/health=200` |
| Runtime NCCL | vLLM log reported `nccl==2.30.4` through PYNCCL; torch still reports compile-time `(2, 28, 9)` |
| Capacity | model load used `73.92 GiB`; available KV cache memory `8.35 GiB`; GPU KV cache size `502,989` tokens |
| Simple completion | service stayed responsive and answered the `2+2` smoke with `4` in the returned text |
| 128K-class sentinel | `LONG_CONTEXT_LINE_COUNT=4200`, `LONG_CONTEXT_MAX_TOKENS=128` passed; artifact label `gb10_sm121_partial_state_nomtp_128k_smoke/20260601045913_lc4200` |
| Overlength boundary | `4226` lines failed cleanly with HTTP 400 because prompt plus output budget exceeded 131072 by one token; this is a harness sizing issue, not a runtime crash |
| KV lifecycle | prefix-cache disabled, 1 complete + 1 abort, `max_idle_kv=0.0%`, threshold `2.0%`; artifact label `gb10_sm121_partial_state_nomtp_128k_smoke/20260601050201_kv_disabled` |
| Driver health | no Xid/UVM/GPU-lost/fatal driver signals in the current boot after the smoke |

Decision update: GB10 no-MTP startup, KV lifecycle, and 128K-class long-context
smoke are healthy on the Dev branch. This is still not a PR-promotion gate for
MTP or 393K-class GB10 reports; run MTP and prefix-cache-enabled GB10 profiles
as separate exploratory gates before making broader SM121 claims.

GB10 no-MTP prefix-cache-enabled lifecycle follow-up:

| Gate | Result |
| --- | --- |
| Initial startup attempt | failed during FlashInfer sampler helper JIT because the public profile pointed at a missing `/usr/local/cuda-13.2/bin/nvcc`; the current nodes expose the active toolkit through `/usr/local/cuda` |
| Corrected startup | TP=2, PP=1, EP on, FP8 KV, prefix cache enabled, `max_model_len=131072`, `max_num_batched_tokens=4176`, `max_num_seqs=2`, `FULL_AND_PIECEWISE`; `/health=200`; PYNCCL log reported `nccl==2.30.4` |
| Capacity | model load used `73.92 GiB`; available KV cache memory `7.31 GiB`; GPU KV cache size `477,766` tokens |
| Prefix-cache lifecycle | `KV_LIFECYCLE_LINE_COUNT=4200`, complete + complete + abort, `max_tokens=64`; artifact `20260601_gb10_prefix_cache_lifecycle_cuda130/kv_prefix_enabled_4200` |
| Result | `PASS`; requests `3`, failures `0`, idle failures `0`; initial idle KV `2.047%`, final idle KV `15.867%`, max idle KV `15.867%` under diagnostic threshold `30%` |
| Driver health | no Xid, UVM, GPU-lost, fatal, launch-failure, or NVIDIA driver OOM signals in the run window on either node |

Interpretation: the user-reported "old sessions keep filling GPU KV cache"
shape was not reproduced on the current GB10 no-MTP prefix-cache-enabled
profile. Cached blocks remain resident, as expected with prefix cache enabled,
but the lifecycle probe stayed bounded and became idle after complete and
client-aborted long requests. MTP remains a separate GB10 liveness gate.

GB10 MTP=2 startup and guarded 128K-class smoke:

| Gate | Result |
| --- | --- |
| Startup | TP=2, PP=1, EP on, FP8 KV, prefix cache disabled, MTP `num_speculative_tokens=2`, `max_model_len=131072`, `max_num_batched_tokens=4176`, `max_num_seqs=2`, `FULL_AND_PIECEWISE`; `/health=200`; PYNCCL log reported `nccl==2.30.4` |
| Capacity | model + drafter load used `75.62 GiB`; available KV cache memory `5.56 GiB`; GPU KV cache size `339,116` tokens; maximum concurrency for 131,072 tokens per request `2.59x` |
| Short deterministic | artifact `20260601_gb10_mtp2_startup_short/short_deterministic`; `2+2` returned `4`, HTTP `200`, elapsed `0.707 s` |
| 128K-class long-context probe | artifact `20260601_gb10_mtp2_startup_short/long_context_probe_4200`; `LONG_CONTEXT_LINE_COUNT=4200`, prompt tokens `130,257`, completion tokens `64`; matched `alpha-cobalt-17`, `beta-quartz-29`, and `gamma-onyx-43`; exit code `0` |
| Spec decode counters during probe | after the short and long probes, draft tokens `72`, accepted tokens `29`, accepted per position `21 / 8` |
| Driver health | no Xid, UVM, GPU-lost, fatal, launch-failure, or NVIDIA driver OOM signals in the run window on either node |

Interpretation: the current Dev branch no longer has an immediate GB10
MTP=2 startup or 128K-class correctness blocker under the guarded profile.
This is still a smoke, not a soak: the prior GB10 liveness failures were
cumulative/high-pressure shapes, so the next GB10 MTP work should be a bounded
streaming or ToolCall-style pressure gate with runtime counters, not a broad
performance claim.

Cross-device sparse-MLA accumulate microbench:

The harness now includes
`scripts/run_sparse_mla_accumulate_microbench.py`, a standalone CUDA microbench
for `accumulate_indexed_sparse_mla_attention_chunk` and the partial-state
variant. It imports the target vLLM checkout directly and emits JSON, CSV, and
Markdown artifacts with mean/p95 latency plus candidate visits per second.

Artifact label: `sparse_mla_accumulate_microbench_20260601`.

| Shape | RTX PRO 6000 SM120 Mean | GB10 SM121 Mean | GB10 / SM120 |
| --- | ---: | ---: | ---: |
| chunk, 64 tokens, 128 candidates | `0.102 ms` | `0.293 ms` | `2.88x` slower |
| chunk, 128 tokens, 256 candidates | `0.310 ms` | `1.105 ms` | `3.57x` slower |
| chunk, 256 tokens, 256 candidates | `0.497 ms` | `2.159 ms` | `4.35x` slower |
| chunk, 1024 tokens, 1152 candidates | `8.171 ms` | `36.066 ms` | `4.41x` slower |
| chunk, 2048 tokens, 1152 candidates | `16.393 ms` | `71.925 ms` | `4.39x` slower |
| partial, 2048 tokens, 1152 candidates | `16.052 ms` | `71.838 ms` | `4.48x` slower |

Throughput by candidate visits shows the same split: large-shape SM120 runs
cluster around `9.1e9` visits/s while GB10 runs around `2.1e9` visits/s; small
64-256 token shapes are lower on both devices, but GB10 remains materially
behind. Partial-state accumulate has roughly the same isolated throughput as
chunk mode at the large candidate shape, so the Dev partial-state win should
continue to be understood as an endpoint scheduling/trace improvement rather
than a standalone kernel throughput win.

Decision: use this microbench as the first filter for future sparse-MLA
experiments. A retained kernel candidate must either reduce total candidate
work, reduce live state/register pressure, or materially shorten the endpoint
mixed-arrival tail. Another chunk-size-only or partial-state-size-only sweep is
not enough. For GB10, keep `max_num_seqs=1` as the conservative safety profile
for 100K-class long-prefill concurrency until a kernel or deployment-isolation
change proves better under the same long-C=2 gate.

Cross-device FP8 MQA top-k microbench:

The existing `scripts/run_sm120_mqa_topk_microbench.py` was run with the same
shape on RTX PRO 6000 and GB10. It exercises the public
`fp8_fp4_mqa_topk_indices` dispatch with deterministic FP8-Q / FP8-K tensors
and checks repeat top-k set stability.

Artifact label: `mqa_topk_cross_device_20260601`.

| Shape | RTX PRO 6000 SM120 Mean | GB10 SM121 Mean | GB10 / SM120 | Repeat Set |
| --- | ---: | ---: | ---: | --- |
| q `256x64x128`, KV `32768x128`, top-k `2048` | `0.838 ms` | `3.415 ms` | `4.08x` slower | pass on both |
| q `256x64x128`, KV `131072x128`, top-k `2048` | `2.721 ms` | `12.221 ms` | `4.49x` slower | pass on both |

Interpretation: FP8 MQA logits/top-k also has much less latency headroom on
GB10, but it remains the second attention-side kernel in endpoint traces
behind sparse-MLA accumulate. Keep direct-MQA live-state reduction as a
secondary kernel experiment. Do not promote a top-k-selection-only optimization:
the prior decomposition showed the selection stage is small while logits
materialization dominates.

### Hardware-Informed Profiling Split

Do not assume RTX PRO 6000 SM120 and GB10 SM121 failures have the same root
cause. The optimization matrix should share workloads, but the profiling focus
differs.

RTX PRO 6000 Blackwell Workstation Edition is the primary kernel-development
platform: 188 SMs, 96 GB GDDR7 ECC, 512-bit memory interface, 1792 GB/s memory
bandwidth, and 600 W board power. NVIDIA's public RTX PRO 6000 page lists
96 GB GDDR7 ECC, 1792 GB/s memory bandwidth, and 600 W max power; the exact SM
count is kept from the local hardware inventory. For this target,
long-context prefill experiments should prioritize:

- SM occupancy, eligible warps, register pressure, and long-scoreboard stalls
  for sparse MLA prefill kernels;
- launch ordering and overlap between sparse prefill accumulate, FP8 MQA
  logits, top-k, and decode kernels;
- per-request ITL p95/p99 under `decode_then_long` and `long_then_short`
  rather than only aggregate input/output throughput;
- scratch-workspace size, because extra temporary state can still affect the
  128K/131K ceiling even when the GPU has enough nominal VRAM.

GB10/DGX Spark SM121 is a capacity-and-stability validation target: 128 GB
LPDDR5x coherent unified memory, 256-bit interface, 273 GB/s memory bandwidth,
and 140 W GB10 TDP. NVIDIA's public DGX Spark user guide lists the same memory
capacity, 256-bit LPDDR5x interface, 273 GB/s bandwidth, and 140 W SoC TDP. For
this target, the same vLLM changes need an additional stability and bandwidth
lens:

- run no-MTP 128K startup/KV lifecycle first, then MTP as exploratory;
- treat prefix-cache reclaimability and idle KV release as correctness gates,
  because unified memory pressure can hide as slowly rising KV usage;
- record driver/GPU health after each high-risk 128K+ probe, including Xid,
  UVM, and GPU-lost signals;
- compare scratch-heavy kernel prototypes against clean dev before promotion,
  because GB10 has far less memory bandwidth than RTX PRO 6000 and may regress
  even when SM120 improves.
- before collecting GB10 performance data, confirm that both nodes use the
  intended NCCL runtime. A preflight after Dev absorption found the venv package
  `nvidia-nccl-cu13==2.30.4` present, `/proc/<pid>/maps` loading the venv
  `libnccl.so.2`, and the library/header reporting `2.30.4+cuda13.2`, while
  `torch.cuda.nccl.version()` still reported `(2, 28, 9)`. Treat the torch value
  as a compile-time signal unless a distributed runtime test proves otherwise;
  record both the torch report and the loaded NCCL library path in GB10
  artifacts.

Profiling deliverables before a best-effort recommendation:

1. SM120 NCU for `fp8_mqa_logits`, sparse MLA prefill accumulate, and
   partial-state accumulate on 59K and 124K single-prefill shapes.
2. SM120 Nsight Systems trace for `decode_then_59k`, `decode_then_124k`, and
   `long_then_short`, with per-request TTFT and ITL p99 aligned to kernel
   ranges.
3. SM120 same-protocol A/B gates for 59K/124K C=1/C=2, random prefill sweep,
   mixed-arrival, streaming pressure, story recall, prefix-cache/KV lifecycle,
   and GSM8K limit-200.
4. GB10 startup/KV lifecycle/long-context smoke using the same workload names
   before claiming the SM120 best-effort choice scales to SM121.
5. A final decision note that separates three outcomes: keep in Dev only,
   promote to PR, or reject and preserve the branch as a backup experiment.

## Experiment Discipline

- Keep measured-effective code changes in the active branch.
- Record effective changes in successful optimization notes.
- Record ineffective experiments, then remove their code. Do not leave A/B
  switches, dead paths, or temporary probes in the production branch.
- If a negative or ambiguous experiment may be worth revisiting, preserve a
  backup branch before reverting it.
- Fixed gates for promotion:
  - short-context latency must not regress,
  - 64K/128K long-context latency at C=1/2/3/4 must not regress,
  - single-connection NIAH-style needle retrieval should include tail positions
    such as 92% and 100% when long-context correctness is in scope,
  - MTP small-context continuous pressure should include the issue #7-like
    5K prompt / 128 output / C=4 shape before treating the branch as stable,
  - SM120 sparse MLA changes must include the issue #10-like 131K max-model-len
    59K/124K C=1/C=2 cold matrix, including C=2 failure count and per-request
    decode fairness,
  - long-context pressure reports should include inter-chunk p95/p99 as an ITL
    proxy so prefill/decode scheduling stalls are visible beyond TTFT and
    elapsed time,
  - KV lifecycle correctness must be gated in both modes: with prefix cache
    disabled, idle GPU KV usage should return near zero after completed and
    client-aborted long requests; with prefix cache enabled, unrelated long
    sessions may leave cached blocks but must stay bounded and reclaimable under
    pressure,
  - deterministic GSM8K must not drop below the fixed lower bound: keep
    `exact_match_flexible >= 0.94` and `exact_match_strict >= 0.925` for the
    current 5-shot limit-200 MTP C=4 promotion gate; use
    `--gen_kwargs temperature=0`,
  - DeepSeek V4 MTP fixes must preserve `FULL_AND_PIECEWISE`; do not skip
    full decode CUDA graph capture as a workaround,
  - correctness/unit smoke for the touched vLLM path must pass.

## Near-Term Work Queue

1. Keep KV lifecycle and prefix-cache recoverability in the development and
   user-feedback matrices. This remains a reliability gate, not a performance
   optimization.
2. Treat C=2 long-prefill fairness as a promotion gate and diagnostic signal,
   not as a reason to add more scheduler-only hacks. The later-short-decode
   scheduler experiments above were rejected.
3. The partial-state sparse-MLA accumulate candidate has been absorbed into
   the Dev branch only as `caea1cb55`. The SM120 full promotion matrix has
   passed. GB10 no-MTP startup, prefix-cache-disabled lifecycle, 128K-class
   long-context smoke, prefix-cache-enabled lifecycle, MTP=2 startup, short
   deterministic generation, and guarded 128K-class MTP smoke have passed.
4. Run GB10 MTP bounded pressure next, for example a short streaming or
   ToolCall-style gate that watches `sample_tokens`, shared-memory broadcast,
   spec-decode counters, and KV usage over repeated requests. If GB10 regresses
   or crashes, leave the code out of PR and preserve the branch as the backup
   experiment.
5. Keep the direct FP8 MQA streaming top-k prototype as a secondary candidate.
   Its microbench must beat the full logits path itself, not just replace the
   already-small top-k selection stage.
6. If a kernel experiment is positive, run the fixed 59K/124K C=1/C=2,
   mixed-arrival, random prefill, story-recall, and GSM8K gates before keeping
   code. If it is negative or ambiguous, revert and record only the rejected
   note.
7. After single-instance kernel options are exhausted, evaluate deployment-level
   prefill/decode isolation as the best-effort answer for longer GB10 / 4-card
   contexts, explicitly trading TTFT/KV-transfer overhead for ITL tail control.
