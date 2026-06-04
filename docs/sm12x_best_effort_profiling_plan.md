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
   floor. The indexed D512 split path is now the Dev default and has already
   moved RTX 59K/124K TTFT by roughly 30% versus the old path. The remaining
   raw-prefill gap is still sparse-MLA accumulate work, especially the real
   `128 compressed + large SWA tail` C128A shape and C4A D512 work.
2. **C=2 fairness.** Keep per-request decode tok/s min/max and ITL p95/p99 as
   promotion gates, not as the current active blocker on the latest Dev head.
   The latest fixed repeat on RTX has healthy long+long C=2 decode fairness.
3. **Prefill/decode interference.** `decode_then_long` shows real interference
   while the existing request is already decoding. `long_then_short` is a
   different shape: the short request reaches first token quickly and then can
   wait behind the leading long prefill.

The current kernel evidence does not support more launch-only sweeps. Nsys and
NCU have repeatedly pointed at sparse MLA prefill accumulate as the largest
attention-side cost and FP8 MQA logits as the second attention-side cost, with
low DRAM throughput and stronger signals from dependency stalls, eligible
warps, and register pressure.

The latest fixed-protocol RTX PRO 6000 repeat,
`20260604_c2_fairness_repeat3_eac9/20260604143419`, was run after aligning the
actual editable vLLM runtime to the same Dev head. All phases exited `0`.
59K C=2 decode min/max was `0.954` with ITL p99 `0.023 s`; 124K C=2
decode min/max was `0.982` with ITL p99 `0.030 s`; mixed `long_long_c2`
decode min/max was `0.931`. Treat C=2 fairness as a no-regression gate and run
Nsys only if the fixed protocol regresses again.

The active raw-prefill evidence is now the default D512 stage attribution:
`20260604_d512_default_stage_timing_rtx/20260604132616` shows 59K/124K
C=1/C=2 input-token throughput around `6.1K-6.9K tok/s` and sparse accumulate
near `99%` of the summed layer/chunk stage time. C=2 input throughput is
almost identical to C=1 while TTFT serializes, so the remaining work is kernel
efficiency rather than decode-cadence collapse.

The cross-device microbenches reinforce that ordering. On RTX PRO 6000 the
131K FP8 MQA direct top-k shape is `2.721 ms`; on GB10 the same shape is
`12.221 ms` (`4.49x` slower). That is the same broad device split as sparse
MLA accumulate, but FP8 MQA is still only the second attention-side kernel in
the mixed-arrival traces, so it should remain the secondary kernel experiment.

The latest C128/SWA follow-ups also narrow what not to do. Dense grouped-SWA
value matmul was rejected on both RTX and GB10: even the best group64 SWA1024
point was slower than the current value kernel (`0.491x` on RTX, `0.463x` on
GB10). FlashInfer 0.6.12 now exposes
`trtllm_batch_decode_sparse_mla_dsv4`, but its contract is a TRTLLM-GEN decode
path with a fixed 128-entry SWA tile and SWA-first sparse indices. It is not a
drop-in replacement for the raw-prefill `128 compressed + large SWA tail`
layout.

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

1. **Keep indexed D512 split prefill as the current Dev baseline.**
   It has passed the RTX promotion matrix, the prefill/decode promotion gate,
   and the GB10 reduced long-C2 availability gate as the default path. Keep
   `FULL_AND_PIECEWISE`, GSM8K, prefix/KV lifecycle, short-context throughput,
   and C=2 fairness in the promotion matrix. Do not re-open scheduler tuning
   unless those gates regress.

2. **Treat GB10 long C=2 as an availability gate, not the next tuning source.**
   The earlier pressure matrix gave a concrete failure: the first two C=2
   phases completed, then the long-C=2 phase could keep both GPUs at high SM
   utilization while prompt/decode counters stopped. The no-code
   `max_num_seqs=1` control completed both 100K-class requests with ITL p99
   around `80 ms`, at the expected cost of queuing one request and max TTFT
   around `238 s`. The same safety profile also completed with MTP=2 enabled:
   `gb10_mtp2_maxseq1_control` had zero
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

   The first measured backend improvement from the third-party prefill
   comparison is the official FlashInfer CUTLASS MXFP4/MXFP8 MoE path, not
   b12x. Current Dev has an opt-in fix that lets DeepSeek V4 start with
   `--moe-backend flashinfer_cutlass` and
   `--quantization-config {"moe":{"activation":"mxfp8"}}` while keeping
   `FULL_AND_PIECEWISE` graph capture. A small same-protocol SM120 prefill
   screen improved 4K/16K C=1 input throughput by about `5.9-6.6%` and reduced
   TTFT by about `5.5-6.6%`. Treat this as the next promotion candidate to
   expand through the SM120 and GB10 matrices. Keep released-b12x sparse-MLA
   work isolated until a correct DS4 compressed extend/prefill contract exists
   in a public package.

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

   A 2026-06-02 GB10 candidate-linearity follow-up reinforced the same rule on
   the current public FlashInfer/b12x stack. Full-lens chunk mode scaled almost
   linearly with candidate visits and large shapes stabilized near `2.0e9`
   visits/s. Staggered valid lengths lowered elapsed time directly; the
   `2048 x 1152` shape moved from `71.743 ms` full-lens to `43.106 ms`
   staggered. Treat this as evidence that the next kernel/backend experiment
   needs to reduce effective candidate work or replace the main sparse-MLA
   attention backend, not just split the same work differently.

   A direct empty-tail loop skip was tested after that microbench evidence. It
   reduced isolated accumulate time for 32K/59K-like staggered shapes, but the
   fixed RTX PRO 6000 C=1 endpoint A/B was noise-level only (`59K` TTFT
   `11.726 s -> 11.693 s`, `124K` `28.844 s -> 28.916 s`). This is now
   rejected. Small loop pruning is insufficient unless it changes the larger
   sparse-MLA backend cost.

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

   The current public FlashInfer `0.6.12` package is also not a drop-in answer.
   It exposes `flashinfer.mla.trtllm_batch_decode_sparse_mla_dsv4`, but not the
   `BatchSparseMLAPagedAttentionWrapper` / `flashinfer.sparse_mla_sm120`
   symbols used by the third-party DS4 path. Synthetic q-len>1 smokes on both
   SM120 and SM121 fail at runtime with `Unsupported architecture`. Keep
   FlashInfer-source or newer-wheel research isolated until the required DS4
   sparse-MLA wrapper/API passes an explicit SM12x smoke.

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

   The 2026-06-02 clean frontier stats run,
   `20260602_sparse_mla_frontier_stats_rtx_no_prewarm`, makes the request-level
   pattern clearer. With TP=2, EP enabled, MTP=2, FP8 KV, prefix cache disabled,
   `max_num_batched_tokens=4096`, and `FULL_AND_PIECEWISE`, the measured 4K,
   16K, 32K, and 64K frontier requests completed successfully. The stats report
   recorded `8.70B` candidate slots and `4.14B` effective candidate visits.
   C128 partial prefill dominated rectangular pressure (`5.44B` slots,
   `1.05B` effective visits, padding ratio `0.806`), while C4 partial prefill
   dominated useful work (`3.17B` slots, `2.99B` effective visits, padding
   ratio `0.056`). Reconstructing requests from the 4096-token query chunks
   shows stable effective work of about `35K-36K` candidate visits per prompt
   token from 16K through 64K. Treat this as evidence that the current prefill
   path is bounded by the sparse-MLA backend contract, not by another simple
   chunk-size sweep.

   The optional `b12x==0.15.2` GB10 install is also not enough by itself.
   Current public FlashInfer `0.6.12` plus `flashinfer-jit-cache==0.6.12+cu130`
   imports on SM121 and `flashinfer show-config` succeeds, but the package still
   lacks `flashinfer.sparse_mla_sm120`,
   `BatchSparseMLAPagedAttentionWrapper`, and
   `sparse_mla_sm120_decode_dsv4_autotune`; released b12x imports
   `b12x.integration.mla` but not the fork's older
   `b12x.integration.compressed_indexer` API. Do not plan a Dev/PR sparse-MLA
   port around the Reddit/unholy-fusion wrapper until the required public
   FlashInfer API passes an explicit SM120/SM121 q-len>1 smoke.

   The retained Milestone-1 entrypoint is now
   `scripts/run_sm12x_prefill_gap_attribution.sh`. It keeps the serve profile
   fixed, runs random pure-prefill C=`1,2,3,4` at `58,957` and `124,000` input
   tokens, and enables `VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_PATH` so endpoint
   TTFT/input tok/s and sparse-MLA candidate work land in the same artifact.
   Use `4` prompts by default; the earlier `8`-prompt shape completed but
   mostly measured queueing for C=3/C=4. The first clean A/B showed grouped
   C128A improved 124K pure-prefill TTFT by about `7%` and input throughput by
   about `8%`, while 59K moved only about `1%`. That is a positive retained
   signal, but not enough for the `20-30%` near-term target. Continue by
   reducing candidate generation/combine duplication, score workspace traffic,
   or launch/merge dependency depth; do not spend another pass on simple
   tile-size retuning of the grouped accumulate helper.

   The stage-timed control artifact
   `20260602_prefill_gap_stage_control4` further narrows the root cause. With
   CUDA event timing enabled, both 59K and 124K fixed-protocol runs show
   `sparse_accumulate` at about `99.6%` of summed layer/chunk time; combine and
   gather are each below `0.3%`. This means the next kernel experiment should
   target the D=512 sparse-MLA accumulate contract directly: fewer duplicate
   candidate visits, less score workspace IO, lower value-dot live state, or a
   released backend that provides a fundamentally better grouped sparse MLA
   accumulate. Do not spend Milestone 2 on indexer/combine/gather unless a
   later trace contradicts this attribution. The full-layer CUDA-event mode is
   too heavy for routine gates, so add layer/type sampling before making it a
   recurring matrix step.

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

- **RTX PRO 6000 / SM120:** use the current Dev branch with indexed D512 split
  sparse MLA prefill as the single-instance baseline. The supported
  optimization target remains edge-style C=1/C=2/C=4, FP8 KV, expert parallel,
  MTP=2, prefix cache disabled by default, `max_num_batched_tokens=4096`, and
  `FULL_AND_PIECEWISE` enabled. The latest fixed-protocol C=2 repeat is healthy
  enough to demote fairness back to a no-regression gate. Do not reopen
  scheduler-only tuning unless the promotion gate regresses.
- **GB10 / SM121:** use the same workload names, but keep GB10 as a
  stability/capacity target until long-C=2 sparse MLA behavior is fixed. The
  conservative 100K-class profile is `max_num_seqs=1` for concurrent long
  prefill pressure; it preserves availability and token cadence at the cost of
  queueing one request. MTP=2 is allowed only after startup, short deterministic
  generation, KV lifecycle, and bounded 128K-class smoke pass in the same boot.
- **Next retained experiment:** target raw long-prefill sparse-MLA accumulate,
  not another scheduler or chunk-size sweep. A candidate must reduce effective
  candidate visits, score/value workspace traffic, live state, dependency depth,
  or integrate a public FlashInfer/b12x path that matches the real DS4 prefill
  metadata. Keep the acceptance table split into long-context TTFT,
  long+long C=2 fairness, staggered mixed-arrival ITL, short C=1/C=2/C=4,
  GSM8K, prefix/KV lifecycle, GB10 reduced long-C2 availability, and driver
  health. Reject any candidate that improves one interference shape by hurting
  another, or that relies on a hidden user knob.

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
