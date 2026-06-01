# SM12x Best-Effort Profiling Plan

This is the short working plan for DeepSeek V4 Flash on RTX PRO 6000
Blackwell and DGX Spark / GB10. It is intentionally separate from the longer
historical optimization notes so the next experiment starts from the current
evidence rather than from old hypotheses.

## Hardware Split

Use the same workload names across both targets, but do not tune them as if
they were the same GPU.

| Target | Public hardware facts | What this implies for profiling |
| --- | --- | --- |
| RTX PRO 6000 Blackwell Workstation Edition, SM120 | 96GB GDDR7 ECC, 512-bit memory interface, 1792 GB/s memory bandwidth, PCIe 5.0 x16, 600W board power. | Primary kernel-development target. Prefer Nsys/NCU on sparse MLA prefill and FP8 MQA logits. Watch register pressure, eligible warps, scheduler stalls, scratch memory, and C=1/C=2 repeatability more than raw memory bandwidth. |
| DGX Spark / GB10, SM121 | 128GB LPDDR5x coherent unified memory, 256-bit memory interface, 273 GB/s memory bandwidth, ConnectX-7 200Gbps, 240W power supply, 140W GB10 TDP. | Capacity and stability target first. Expect bandwidth and power headroom to be much tighter than SM120. Gate startup, NCCL runtime, KV lifecycle, prefix-cache reclaimability, and driver health before treating performance numbers as tuning evidence. |

The useful scaling claim is therefore narrow: a code path that improves SM120
without increasing scratch pressure or changing public semantics is a good
candidate for GB10, but it still needs GB10 stability evidence. A code path
that relies on extra scratch buffers, more launches, or more KV transfer must
be revalidated on GB10 before promotion.

## Current Evidence

The current SM120 traces separate three problems that should stay linked in
experiments but separate in interpretation:

1. **Long-context prefill / TTFT.** 59K and 124K C=1/C=2 remain the promotion
   floor. Partial-state sparse MLA helped end-to-end enough for Dev absorption,
   but the standalone microbench shows it is not a universal kernel-speed win.
   The cross-device indexed-accumulate microbench now also shows that GB10 is
   far more fragile for this path: for the same synthetic sparse-MLA accumulate
   work, SM121 delivers roughly 20-35% of the SM120 candidate-visit rate across
   small and large token/candidate shapes.
2. **C=2 fairness.** The user-visible failure mode is a slow request while its
   paired request remains healthy. Track per-request decode tok/s min/max and
   ITL p95/p99, not just mean throughput.
3. **Prefill/decode interference.** `decode_then_long` shows real interference
   while the existing request is already decoding. `long_then_short` is a
   different shape: the short request reaches first token quickly and then can
   wait behind the leading long prefill.

The current kernel evidence does not support more launch-only sweeps. Nsys and
NCU have repeatedly pointed at sparse MLA prefill accumulate as the largest
attention-side cost and FP8 MQA logits as the second attention-side cost, with
low DRAM throughput and stronger signals from dependency stalls, eligible
warps, and register pressure.

The latest fixed-protocol RTX PRO 6000 run,
`20260601_c2_fairness_interference_protocol/20260601105746`, strengthens that
interpretation because the C=2 fairness matrix and Nsys cases used the same
generated serve command. C=1 remained healthy (`59K` decode mean
`143.827 tok/s`, `124K` decode mean `106.355 tok/s`), while C=2 remained the
visible failure mode (`59K` decode min/max `0.127`, `124K` decode min/max
`0.128`). The same run showed the two interference subproblems: simultaneous
`long_long_c2` is dominated by
`_accumulate_indexed_attention_chunk_multihead_kernel`, while staggered
mixed-arrival cases are dominated by
`_accumulate_indexed_attention_partial_states_multihead_kernel`. The worst
tail remains `long_then_short`, where the short request reaches TTFT quickly
but then sees a `25.639 s` ITL p99 after first token. Treat C=2 fairness as the
acceptance metric and prefill/decode interference as the mechanism to profile;
do not collapse them into one number.

The cross-device microbenches reinforce that ordering. On RTX PRO 6000 the
131K FP8 MQA direct top-k shape is `2.721 ms`; on GB10 the same shape is
`12.221 ms` (`4.49x` slower). That is the same broad device split as sparse
MLA accumulate, but FP8 MQA is still only the second attention-side kernel in
the mixed-arrival traces, so it should remain the secondary kernel experiment.

The later pending-decode scheduler guard should now be treated as part of the
SM120 Dev baseline, not as an open hypothesis. Full user-feedback artifact
`20260601_pending_decode_guard_user_feedback_matrix/20260601123745` passed the
primary, prefix-cache, and KV-lifecycle phases. It changed the proven
`long_then_short` starvation tail from secondary ITL p99 `25.615 s` to
`0.089 s`, and decode min/max from `0.025` to `0.298`, while GSM8K,
streaming pressure, prefix-cache stress, and KV lifecycle stayed green. It did
not solve simultaneous long+long C=2 fairness: 59K C=2 ITL p99 moved from
`0.301 s` to `0.831 s`, and 124K C=2 decode min/max moved from `0.131` to
`0.094`. Therefore keep C=2 fairness and prefill/decode interference in the
same profiling protocol, but score them separately.

The fixed repeat
`20260601_c2_fixed_protocol_repeat/20260601150253` confirmed the same split
under one protocol: `long_then_short` stayed fixed with secondary TTFT
`3.327 s` and ITL p99 `0.088 s`, while long+long stayed weak (`59K` C=2 ITL
p99 `0.824 s`, `124K` C=2 ITL p99 `1.112 s`). Nsys from the same serve profile
put `_accumulate_indexed_attention_chunk_multihead_kernel` at `37.1%` of
captured CUDA time for `long_long_59k_c2` and `44.7%` for
`long_long_124k_c2`; focused NCU showed low DRAM throughput and high
register/dependency pressure. A `HEAD_BLOCK=4` probe reduced registers and
raised occupancy, but regressed real duration (`1.080 ms -> 1.246 ms` for the
target chunk microbench), so simple live-state shrinkage without reducing work
is rejected.

## Profiling Matrix

Run the matrix in this order. Stop early only when the failure itself is the
artifact to debug.

| Phase | SM120 purpose | GB10 purpose | Required outputs |
| --- | --- | --- | --- |
| Health preflight | Confirm CUDA/NCCL/Triton/vLLM versions and graph mode before comparing numbers. | Confirm both nodes use the intended NCCL runtime and no current-boot driver OOM/Xid state exists. | collect-env, loaded NCCL library path when available, serve command, graph mode, driver-health scan. |
| Baseline user matrix | Fix the performance floor before profiling. | Establish no-MTP 128K stability first; MTP remains exploratory until it survives the same shape. | 59K/124K C=1/C=2, decode-concurrency, mixed-arrival, random prefill, streaming pressure, story recall, GSM8K limit-200, KV lifecycle. |
| C=2 fairness + interference protocol | Keep the user-visible fairness metric and the kernel trace under the same serve profile. | Run after stability gates pass; on GB10 use no-MTP or conservative `max_num_seqs=1` controls when MTP long-C2 is unstable. | Per-request TTFT/decode/ITL, phase exit codes, top CUDA kernels, and launch-order trace. Use `scripts/run_sm12x_c2_fairness_interference_protocol.sh`; it reuses the fairness run's `serve_command.sh` for Nsys. |
| Interference Nsys | Explain the difference between simultaneous long C=2, decode-then-long, decode-then-short, short-decode-then-long, and long-prefill-then-short when a fairness matrix already exists. | Run only after stability gates pass; use shorter or no-MTP shapes if needed. | Per-request TTFT/decode/ITL plus top CUDA kernels and launch order. Use `scripts/run_sm12x_prefill_decode_interference_profiles.sh` for trace-only reruns. |
| Focused NCU | Decide whether a kernel change can plausibly help. | Optional and lower priority; GB10 NCU is for regressions, not for deriving SM120 launch parameters. | Duration, registers/thread, occupancy, eligible warps/scheduler, long scoreboard, DRAM throughput for sparse MLA accumulate and FP8 MQA logits. |
| Microbench | Prove a kernel hypothesis before endpoint runs. | Check scratch-sensitive candidates for obvious GB10 risk. | Synthetic parity, mean/p95, scratch bytes, launch count. Use `scripts/run_sm12x_sparse_mla_ncu_microbench.sh` for the fixed sparse-MLA chunk/partial path, plus the MQA top-k microbench scripts for secondary FP8 MQA work. |
| Deployment probe | Decide if single-instance best effort is enough. | More important for long contexts once there are enough nodes to isolate roles. | Tail ITL, TTFT overhead, KV-transfer overhead, connector errors, and driver health. Do not claim throughput gains from prefill/decode disaggregation. |

## Experiment Order

1. **Keep partial-state sparse MLA as the current Dev baseline.**
   It has passed the SM120 promotion matrix, no-MTP GB10 smoke,
   prefix-cache-enabled GB10 lifecycle, and a guarded GB10 MTP=2 128K-class
   smoke. Keep the pending-decode guard with it on Dev because the full SM120
   user-feedback matrix proved the short-after-long starvation fix without
   correctness or stability fallout. The first GB10 long C=2 pressure gate
   reproduced a high-SM, no-token-progress stall in both MTP=2 and no-MTP
   profiles, so broad SM121 performance claims should wait for the reduced
   long-C=2 repro and fix.

2. **Use the GB10 long C=2 Nsys trace to guide the next kernel change.**
   The pressure matrix now gives a concrete failure: the first two C=2 phases
   complete, then the long-C=2 phase can keep both GPUs at high SM utilization
   while prompt/decode counters stop. The reduced no-MTP 2048-token trace shows
   both ranks spending the largest share of GPU time in
   `_accumulate_indexed_attention_chunk_multihead_kernel`, with MXFP4 MoE,
   FP8 MQA logits, and NCCL behind it. The next experiment should reduce or
   restructure sparse-MLA prefill work for this shape before adding another
   scheduler policy. A `VLLM_TRITON_MLA_SPARSE_TOPK_CHUNK_SIZE=128` probe still
   timed out with zero prefill/decode progress, so do not spend more time on
   simply shrinking the candidate chunk. A temporary `PREFILL_CHUNK_SIZE=1`
   probe changed the failure from no-progress to one very slow completed
   request plus one timed-out peer, which is useful evidence but not a
   retention-quality fix. The no-code `max_num_seqs=1` control completed both
   100K-class requests with ITL p99 around `80 ms`, at the expected cost of
   queuing one request and max TTFT around `238 s`. The same safety profile
   also completed with MTP=2 enabled: `gb10_mtp2_maxseq1_control` had zero
   request failures, max TTFT `231.239 s`, ITL p99 `0.086 s`,
   `max running = 1`, `max waiting = 1`, and no CUDA/NCCL/driver/engine error
   signals. Treat `max_num_seqs=1` as the current GB10 conservative safety
   profile for 100K-class long-prefill concurrency until sparse-MLA prefill is
   fixed. This protects availability and token cadence; it does not solve long
   C=2 throughput.

   Cross-device indexed sparse-MLA accumulate microbench artifact
   `sparse_mla_accumulate_microbench_20260601` confirms why GB10 needs that
   conservative profile. At small endpoint-like shapes, SM120 completed
   256-token / 256-candidate accumulate in `0.497 ms` while GB10 took
   `2.159 ms` (`4.35x` slower). At large 2048-token / 1152-candidate shape,
   SM120 took `16.393 ms` while GB10 took `71.925 ms` (`4.39x` slower).
   Partial-state mode did not change the device ratio: 2048-token /
   1152-candidate partial-state was `16.052 ms` on SM120 and `71.838 ms` on
   GB10 (`4.48x` slower). Treat this as evidence that GB10 long-C=2 issues are
   not just endpoint scheduling noise; the sparse-MLA prefill kernel itself has
   much less latency headroom on SM121.

3. **Run the interference profile before the next retained kernel change.**
   Use `scripts/run_sm12x_c2_fairness_interference_protocol.sh` and compare
   against the latest Dev artifacts. This wrapper first runs
   `long_context_latency_matrix`, `long_context_decode_concurrency`, and
   `long_context_mixed_arrival`, then reuses the generated `serve_command.sh`
   for the Nsys trace set. That keeps the user-visible C=2 fairness numbers and
   the kernel timeline on the same serve profile. The default trace set covers
   simultaneous long+long C=2, long decode then long prefill, long decode then
   short prefill, short decode then long prefill, and long prefill then short
   request. The decision question is whether partial-state accumulate is still
   the largest active-window cost, whether FP8 MQA logits is still second, and
   whether a candidate helps the interference class that actually regressed.

   RTX PRO 6000 artifact
   `20260601_prefill_decode_interference_profiles_expanded/20260601084525`
   completed that trace set on the current Dev branch. It split the problem
   into two concrete work items:

   - pure long+long C=2 fairness remains the worst long-context case
     (`long_long_c2` decode min/max `0.140`, ITL p99 `1.762 s`) and is the
     shape where the non-partial
     `_accumulate_indexed_attention_chunk_multihead_kernel` dominates;
   - staggered mixed-arrival cases are dominated by
     `_accumulate_indexed_attention_partial_states_multihead_kernel`, with
     `long_then_short` still showing a separate scheduler/admission tail
     (`3.249 s` secondary TTFT, but `25.387 s` ITL p99 after first token).

   Therefore the next kernel experiment should not be a global launch retune.
   Profile `long_long_c2` and `decode_then_124k` separately with NCU: the
   former targets the chunk sparse-MLA accumulate path, while the latter
   targets the partial-state sparse-MLA path. Keep a scheduler/admission track
   open for `long_then_short`, but do not mix it into the first kernel patch.

   Follow-up NCU artifact
   `20260601_ncu_sparse_mla_expanded_shapes_seq` profiled chunk and
   partial-state sparse-MLA accumulate sequentially on q `256x64x512`,
   candidates `1152`. Both kernels showed low DRAM throughput (`1.41%` chunk,
   `1.90%` partial), low eligible warps per scheduler (`1.05` and `1.15`),
   similar register pressure (`118` and `116` registers/thread), and similar
   scoreboard/wait stall shape. That means partial-state's endpoint cost is
   more about launch count and total candidate work than an obviously worse
   per-launch kernel. Keep the next experiment focused on reducing total
   sparse-MLA work or dependency depth.

   Latest fixed-protocol RTX PRO 6000 artifact
   `20260601_c2_fairness_interference_protocol/20260601105746` confirms that
   this remains the right split under the normal fairness serve profile:

   | Case | Decode Min/Max | ITL P99 | Top Kernel |
   | --- | ---: | ---: | --- |
   | `long_long_c2` | `0.139` | `1.222 s` | `_accumulate_indexed_attention_chunk_multihead_kernel` `44.5%` |
   | `decode_then_59k` | `0.247` | `0.205 s` | `_accumulate_indexed_attention_partial_states_multihead_kernel` `40.5%` |
   | `decode_then_124k` | `0.387` | `0.205 s` | `_accumulate_indexed_attention_partial_states_multihead_kernel` `43.7%` |
   | `long_decode_then_short` | `0.427` | `0.701 s` | `_accumulate_indexed_attention_partial_states_multihead_kernel` `44.0%` |
   | `short_decode_then_124k` | `0.359` | `0.435 s` | `_accumulate_indexed_attention_partial_states_multihead_kernel` `43.3%` |
   | `long_then_short` | `0.028` | `25.639 s` | `_accumulate_indexed_attention_partial_states_multihead_kernel` `41.3%` |

   Driver health stayed clean for this run. The next retained experiment
   should therefore report two scores: (a) pure long+long C=2 fairness and
   TTFT, and (b) staggered mixed-arrival ITL p99/fairness. A change that only
   helps one while regressing the other is not a promotion candidate.

   The mixed-arrival Nsys wrapper now also exports `cuda_gpu_trace` and writes
   `nsys_timeline_summary.json` / `.md`. Use the top-kernel table to decide
   which family dominates the whole trace, then use the timeline summary to
   inspect global FP8-MQA-logits gaps, CUDA idle gaps, and the dominant class
   inside those windows. If a request has a huge ITL tail while global FP8-MQA
   gaps stay small, treat that as per-request scheduling starvation rather
   than a full decode-kernel stoppage.

   Backfilling the timeline parser over the fixed-protocol `long_then_short`
   trace produced exactly that signal: the secondary request had `25.639 s`
   max ITL, while the global max FP8-MQA-logits start gap was only `0.167 s`.
   That confirms the short request is starved at the request/scheduler level
   while decode kernels continue globally. The retained pending-decode guard is
   the current Dev answer for this one starvation class; do not use it as
   evidence that simultaneous long+long C=2 fairness is solved.

   Before endpoint A/B, run
   `scripts/run_sm12x_sparse_mla_ncu_microbench.sh` on SM120, and then on GB10
   if the candidate changes scratch, launch count, or live state. The default
   staggered-lens microbench is the promotion-relevant prefilter; full-lens
   control is optional and should not override a staggered regression. Enable
   `SM12X_SPARSE_MLA_RUN_NCU=1` only for focused counter collection.

   The first formal run with that wrapper reinforces the same constraint.
   Artifact labels: RTX PRO 6000
   `20260601_sparse_mla_formal_timing/20260601114303`, GB10
   `20260601_sparse_mla_formal_timing/20260601114428`, and focused RTX NCU
   `20260601_sparse_mla_focused_ncu/20260601114516`.

   | Shape | RTX chunk | GB10 chunk | GB10/RTX | RTX partial/chunk | GB10 partial/chunk |
   | --- | ---: | ---: | ---: | ---: | ---: |
   | `256 x 1152` | `1.076 ms` | `4.660 ms` | `4.33x` | `0.956` | `0.994` |
   | `1024 x 1152` | `5.048 ms` | `21.918 ms` | `4.34x` | `0.982` | `1.021` |
   | `2048 x 1152` | `10.059 ms` | `43.632 ms` | `4.34x` | `0.995` | `1.023` |

   Focused RTX NCU on `256 x 1152` showed chunk at `1.17 ms`, SM throughput
   `60.10%`, DRAM throughput `2.82%`, eligible warps/scheduler `1.04`, and
   `118` registers/thread; partial-state was `1.12 ms`, SM throughput
   `62.89%`, DRAM throughput `3.77%`, eligible warps/scheduler `1.14`, and
   `116` registers/thread. Partial-state is slightly healthier per isolated
   launch, but the large-shape GB10 timing and endpoint traces show that
   switching paths is not enough. The next candidate must remove candidate
   visits, reduce live state, or alter admission/scheduling for the
   `long_then_short` tail; another part-size or launch-only sweep is not a
   promotion candidate.

4. **Try algorithmic sparse MLA work only if it reduces live state or total
   work.**
   More local chunk/part/warp sweeps are exhausted. A retained candidate needs
   endpoint improvement on 59K/124K C=1/C=2 plus mixed-arrival, and it must not
   increase GB10 instability through scratch pressure.

   The next useful kernel experiment should reduce candidate visits, reduce
   per-program dependency depth, or reduce live state. Another candidate-size
   or partial-state sweep without a total-work reduction is unlikely to improve
   either device, and it is especially unlikely to rescue GB10 long-C=2.
   The part-size sweep confirmed this: full-lens synthetic inputs can show tiny
   partial-state wins, but realistic staggered C128 inputs were flat or slower.
   Do not write another two-pass sparse-MLA kernel unless the design removes
   work rather than merely splitting it.

   A new debug-only stats hook can write sparse MLA prefill JSONL rows when
   `VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_PATH` is set. Summarize the resulting
   file or directory with `sparse-mla-stats-report` before changing another
   kernel. The first RTX smoke artifact,
   `20260601_sparse_mla_stats_smoke/20260601100102`, shows why this matters:
   even a small prefill had an overall sparse-MLA padding ratio of `0.585`;
   C128 partial prefill was the largest waste shape with padding ratio
   `0.866`, while C4 partial prefill was `0.118` and SWA-only was `0.010`.
   Treat that as a work-reduction target, not yet as proof of an endpoint win.

   The follow-up case-split artifact
   `20260601_sparse_mla_stats_case_split/20260601101443` separated the two
   mixed-arrival shapes. `long_long_c2` and `decode_then_124k` had nearly the
   same total sparse-MLA effective visits (`13.15B`) and the same rectangular
   candidate-slot padding ratio (`0.304`). The padding ratio is a shape-pressure
   signal, not full dot-product work, because the current kernel already caps
   the per-token loop with `combined_lens`. The layer-type split was different:
   `long_long_c2` spent most C128 work in the multi-prefill chunk path
   (C128 chunk padding ratio `0.484`, plus C128 partial padding ratio `0.462`)
   and decode fairness stayed poor with min/max ratio `0.126`. `decode_then_124k`
   spent the C128 work in the partial path (C128 partial padding ratio `0.481`)
   but fairness was better at min/max ratio `0.337`. Therefore the next retained
   kernel experiment should target the multi-prefill C128 chunk path first,
   especially its launch shape, live state, and request coupling. A C128-only
   `HEAD_BLOCK=4` probe regressed the target microbench, so do not retry simple
   head-block shrinkage. A per-request q-launch split for C128 multi-prefill
   chunks was also noise-level and slightly hurt `decode_then_124k`, so simple
   request isolation inside the same layer forward is not enough. Reusing the
   existing partial-state primitive as a two-pass split also failed the
   realistic staggered-length microbench on both RTX PRO 6000 and GB10. Treat
   the partial path as a secondary target unless a later trace shows it causing
   the user-visible slow-stream tail.

5. **Keep direct FP8 MQA streaming top-k as a secondary experiment.**
   The current decomposition shows top-k selection itself is small, so the only
   useful version is one that reduces FP8 MQA logits live state or register
   pressure. A top-k-only speedup is not enough. Cross-device artifact
   `mqa_topk_cross_device_20260601` shows the 131K shape at `2.721 ms` on
   SM120 and `12.221 ms` on GB10, so GB10 would benefit from lower live state
   too, but the endpoint priority still stays behind sparse MLA accumulate
   because FP8 MQA logits is roughly one quarter of the sparse-MLA captured
   attention-side time in the current traces.

6. **Treat scheduler-only fixes as high risk.**
   The successful scheduler experiments improved one tail shape but regressed
   other C=2 shapes or hit graph/runtime assumptions. Do not promote another
   scheduler policy unless it passes the full user-feedback matrix.

7. **Evaluate prefill/decode isolation only as a deployment fallback.**
   vLLM disaggregated prefill is designed to control tail ITL by moving prefill
   and decode into separate instances with KV transfer. It is not a raw
   throughput optimization. On the current dual RTX PRO 6000 setup, the full
   DS4 TP=2 model already consumes both GPUs, so true prefill/decode isolation
   likely requires either a smaller model, more GPUs, or a separate cluster
   shape. The same caveat applies to a two-node GB10 TP=2 setup.

## Current Best-Effort Recommendation

- **RTX PRO 6000 / SM120:** use the current Dev branch with partial-state
  sparse MLA plus the pending-decode guard as the single-instance baseline.
  The supported optimization target remains edge-style C=1/C=2/C=4, FP8 KV,
  expert parallel, MTP=2, prefix cache disabled by default, and
  `FULL_AND_PIECEWISE` enabled. This profile is healthy for C=1 and fixes the
  short-after-long decode starvation tail. Treat simultaneous 59K/124K C=2 as
  the next performance blocker, not as a solved SLA.
- **GB10 / SM121:** use the same workload names, but keep GB10 as a
  stability/capacity target until long-C=2 sparse MLA behavior is fixed. The
  conservative 100K-class profile is `max_num_seqs=1` for concurrent long
  prefill pressure; it preserves availability and token cadence at the cost of
  queueing one request. MTP=2 is allowed only after startup, short deterministic
  generation, KV lifecycle, and bounded 128K-class smoke pass in the same boot.
- **Next retained experiment:** target simultaneous long+long C=2 first.
  Collect the C=2 fairness + interference protocol, then NCU the
  multi-prefill sparse-MLA accumulate window. Keep the acceptance table split
  into long-context TTFT, long+long C=2 fairness, staggered mixed-arrival ITL,
  short C=1/C=2/C=4, GSM8K, prefix/KV lifecycle, and driver health. Reject any
  candidate that improves `long_then_short` by hurting long+long C=2, or that
  relies on a hidden user knob.

## Promotion Rules

Keep code only when the same protocol shows a net win:

- no public user knob or hidden graph-disable workaround;
- `FULL_AND_PIECEWISE` remains enabled;
- short-context C=1/C=2/C=4 does not regress;
- 59K/124K C=1/C=2 TTFT and per-request decode fairness do not regress;
- mixed-arrival `decode_then_long` and `long_then_short` are reported
  separately;
- GSM8K limit-200 stays above the fixed floor;
- KV lifecycle passes with prefix cache disabled and enabled;
- driver health remains clean on high-risk SM120 and GB10 runs.

Reject and revert code when the improvement is only a microbench win, when it
requires a user-facing knob to be safe, or when it improves `long_then_short`
by hurting long+long C=2 fairness. Preserve only the note and, if the idea may
be worth revisiting, a backup branch.

## Public Sources

- NVIDIA RTX PRO 6000 Workstation Edition product page:
  <https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/>
- NVIDIA RTX PRO 6000 Workstation Edition datasheet:
  <https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf>
- NVIDIA DGX Spark product specifications:
  <https://www.nvidia.com/en-us/products/workstations/dgx-spark/>
- NVIDIA DGX Spark user guide:
  <https://docs.nvidia.com/dgx/dgx-spark/>
