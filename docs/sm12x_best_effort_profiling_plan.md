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

The cross-device microbenches reinforce that ordering. On RTX PRO 6000 the
131K FP8 MQA direct top-k shape is `2.721 ms`; on GB10 the same shape is
`12.221 ms` (`4.49x` slower). That is the same broad device split as sparse
MLA accumulate, but FP8 MQA is still only the second attention-side kernel in
the mixed-arrival traces, so it should remain the secondary kernel experiment.

## Profiling Matrix

Run the matrix in this order. Stop early only when the failure itself is the
artifact to debug.

| Phase | SM120 purpose | GB10 purpose | Required outputs |
| --- | --- | --- | --- |
| Health preflight | Confirm CUDA/NCCL/Triton/vLLM versions and graph mode before comparing numbers. | Confirm both nodes use the intended NCCL runtime and no current-boot driver OOM/Xid state exists. | collect-env, loaded NCCL library path when available, serve command, graph mode, driver-health scan. |
| Baseline user matrix | Fix the performance floor before profiling. | Establish no-MTP 128K stability first; MTP remains exploratory until it survives the same shape. | 59K/124K C=1/C=2, decode-concurrency, mixed-arrival, random prefill, streaming pressure, story recall, GSM8K limit-200, KV lifecycle. |
| Interference Nsys | Explain the difference between simultaneous long C=2, decode-then-long, decode-then-short, short-decode-then-long, and long-prefill-then-short. | Run only after stability gates pass; use shorter or no-MTP shapes if needed. | Per-request TTFT/decode/ITL plus top CUDA kernels and launch order. Use `scripts/run_sm12x_prefill_decode_interference_profiles.sh`. |
| Focused NCU | Decide whether a kernel change can plausibly help. | Optional and lower priority; GB10 NCU is for regressions, not for deriving SM120 launch parameters. | Duration, registers/thread, occupancy, eligible warps/scheduler, long scoreboard, DRAM throughput for sparse MLA accumulate and FP8 MQA logits. |
| Microbench | Prove a kernel hypothesis before endpoint runs. | Check scratch-sensitive candidates for obvious GB10 risk. | Synthetic parity, mean/p95, scratch bytes, launch count. Use `scripts/run_sparse_mla_accumulate_microbench.py` and the MQA top-k microbench scripts. |
| Deployment probe | Decide if single-instance best effort is enough. | More important for long contexts once there are enough nodes to isolate roles. | Tail ITL, TTFT overhead, KV-transfer overhead, connector errors, and driver health. Do not claim throughput gains from prefill/decode disaggregation. |

## Experiment Order

1. **Keep partial-state sparse MLA as the current Dev baseline.**
   It has passed the SM120 promotion matrix, no-MTP GB10 smoke,
   prefix-cache-enabled GB10 lifecycle, and a guarded GB10 MTP=2 128K-class
   smoke. The first GB10 long C=2 pressure gate reproduced a high-SM,
   no-token-progress stall in both MTP=2 and no-MTP profiles, so broad SM121
   performance claims should wait for the reduced long-C=2 repro and fix.

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
   Use the existing wrapper and compare against the latest Dev artifacts. The
   default trace set now covers the combined fairness/interference matrix:
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

4. **Try algorithmic sparse MLA work only if it reduces live state or total
   work.**
   More local chunk/part/warp sweeps are exhausted. A retained candidate needs
   endpoint improvement on 59K/124K C=1/C=2 plus mixed-arrival, and it must not
   increase GB10 instability through scratch pressure.

   The next useful kernel experiment should reduce candidate visits, reduce
   per-program dependency depth, or reduce live state. Another candidate-size
   or partial-state sweep without a total-work reduction is unlikely to improve
   either device, and it is especially unlikely to rescue GB10 long-C=2.

   A new debug-only stats hook can write sparse MLA prefill JSONL rows when
   `VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_PATH` is set. Summarize the resulting
   file or directory with `sparse-mla-stats-report` before changing another
   kernel. The first RTX smoke artifact,
   `20260601_sparse_mla_stats_smoke/20260601100102`, shows why this matters:
   even a small prefill had an overall sparse-MLA padding ratio of `0.585`;
   C128 partial prefill was the largest waste shape with padding ratio
   `0.866`, while C4 partial prefill was `0.118` and SWA-only was `0.010`.
   Treat that as a work-reduction target, not yet as proof of an endpoint win.

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
