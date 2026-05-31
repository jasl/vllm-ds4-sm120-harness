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

## Profiling Matrix

Run the matrix in this order. Stop early only when the failure itself is the
artifact to debug.

| Phase | SM120 purpose | GB10 purpose | Required outputs |
| --- | --- | --- | --- |
| Health preflight | Confirm CUDA/NCCL/Triton/vLLM versions and graph mode before comparing numbers. | Confirm both nodes use the intended NCCL runtime and no current-boot driver OOM/Xid state exists. | collect-env, loaded NCCL library path when available, serve command, graph mode, driver-health scan. |
| Baseline user matrix | Fix the performance floor before profiling. | Establish no-MTP 128K stability first; MTP remains exploratory until it survives the same shape. | 59K/124K C=1/C=2, decode-concurrency, mixed-arrival, random prefill, streaming pressure, story recall, GSM8K limit-200, KV lifecycle. |
| Three-case Nsys | Explain the difference between `decode_then_59k`, `decode_then_124k`, and `long_then_short`. | Run only after stability gates pass; use shorter or no-MTP shapes if needed. | Per-request TTFT/decode/ITL plus top CUDA kernels and launch order. Use `scripts/run_sm12x_prefill_decode_interference_profiles.sh`. |
| Focused NCU | Decide whether a kernel change can plausibly help. | Optional and lower priority; GB10 NCU is for regressions, not for deriving SM120 launch parameters. | Duration, registers/thread, occupancy, eligible warps/scheduler, long scoreboard, DRAM throughput for sparse MLA accumulate and FP8 MQA logits. |
| Microbench | Prove a kernel hypothesis before endpoint runs. | Check scratch-sensitive candidates for obvious GB10 risk. | Synthetic parity, mean/p95, scratch bytes, launch count. Use the sparse MLA accumulate and MQA top-k microbench scripts. |
| Deployment probe | Decide if single-instance best effort is enough. | More important for long contexts once there are enough nodes to isolate roles. | Tail ITL, TTFT overhead, KV-transfer overhead, connector errors, and driver health. Do not claim throughput gains from prefill/decode disaggregation. |

## Experiment Order

1. **Keep partial-state sparse MLA as the current Dev baseline.**
   It has passed the SM120 promotion matrix and no-MTP GB10 smoke, but it
   should not become a broad SM121 performance claim until GB10 MTP and
   prefix-cache-enabled lifecycle gates pass.

2. **Run the three-case interference profile before the next kernel change.**
   Use the existing wrapper and compare against the latest Dev artifacts. The
   decision question is whether partial-state accumulate is still the largest
   active-window cost and whether FP8 MQA logits is still second.

3. **Try algorithmic sparse MLA work only if it reduces live state or total
   work.**
   More local chunk/part/warp sweeps are exhausted. A retained candidate needs
   endpoint improvement on 59K/124K C=1/C=2 plus mixed-arrival, and it must not
   increase GB10 instability through scratch pressure.

4. **Keep direct FP8 MQA streaming top-k as a secondary experiment.**
   The current decomposition shows top-k selection itself is small, so the only
   useful version is one that reduces FP8 MQA logits live state or register
   pressure. A top-k-only speedup is not enough.

5. **Treat scheduler-only fixes as high risk.**
   The successful scheduler experiments improved one tail shape but regressed
   other C=2 shapes or hit graph/runtime assumptions. Do not promote another
   scheduler policy unless it passes the full user-feedback matrix.

6. **Evaluate prefill/decode isolation only as a deployment fallback.**
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
