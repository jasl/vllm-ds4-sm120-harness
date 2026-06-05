# SM120 Current State

Start here before reading the longer historical notes. This file is the compact
working entrypoint for DeepSeek V4 SM12x optimization status, current gates, and
next-step decisions. Treat `docs/sm120_optimization_notes.md` as the append-only
evidence archive.

Last updated: 2026-06-06.

## Read Order

1. Read this file for the current branch posture and next target.
2. Read `docs/vllm_correctness_gates.md` for promotion requirements.
3. Read `docs/dgx_spark_bare_metal_cluster.md` for GB10 / SM121 setup and
   reduced long-context gates.
4. Use `docs/sm120_experiment_index.md` to jump into historical experiments.
5. Use `docs/sm120_optimization_notes.md` only when you need the detailed
   artifact trail or rejected-route rationale.

## Current Posture

- PR-ready work: the D512 sparse-MLA prefill stack plus the supporting
  scheduling, workspace warmup, prefix/KV lifecycle, and correctness fixes that
  already passed promotion gates. This is the current defensible customer
  baseline for dual RTX PRO 6000 / SM120 and the reduced GB10 / SM121 envelope.
- Dev-only work: D512 empty-tail skip and sparse MLA candidate-region
  attribution. Empty-tail skip has small endpoint gains, but it must keep
  GSM8K limit-200 and the full promotion matrix green before becoming PR-branch
  behavior. Candidate-region reporting is diagnostic infrastructure, not a
  claimed performance optimization.
- Upstream comparison point: upstream now exposes an optional
  `FLASHINFER_MLA_SPARSE_DSV4` backend, but the current official FlashInfer
  `0.6.12` wheel is not a runnable SM120/SM121 endpoint backend in this setup.
  The backend marker is selected, but the FlashInfer TRTLLM sparse MLA decode
  runner fails during startup with `Unsupported architecture`.
- Blocked or rejected as current endpoint backends: public b12x compressed MLA
  as a direct DS4 endpoint backend, upstream
  `FLASHINFER_MLA_SPARSE_DSV4` with the current official wheel, standalone C128
  grouped-compressed prefill, generic D512 selector/tile/chunk sweeps, BF16
  score workspace, SWA-only routing through the current D512 helper, and
  grouped-query local-SWA tiling that keeps the same candidate work. A
  fused-stats/value D512 prototype and a lower-live-state value-tile prototype
  were also rejected because they did not improve GB10 and did not reduce real
  candidate/value visits.

## Promotion Matrix

Any sparse-MLA, scheduler, workspace, or backend change that affects serving
behavior must preserve:

- GSM8K limit-200 correctness.
- CUDA graph mode `FULL_AND_PIECEWISE`; do not hide correctness issues by
  disabling full decode graph capture.
- Prefix-cache stress and KV lifecycle recoverability.
- Short throughput and 8K/1K throughput regression checks.
- 59K / 124K long-context C=1 and C=2 TTFT, decode, ITL p95/p99, and fairness.
- Mixed-arrival prefill/decode interference and streaming pressure.
- GB10 reduced long-C2 availability/cadence when the change could affect GB10,
  scheduler behavior, or sparse-MLA prefill.
- User-feedback reduced gates when the change touches the reported failure
  surface. `scripts/run_sm12x_dp_ep_oom_reduced_gate.sh` tracks the external
  DP/EP long-context JIT/OOM/worker-crash shape with reduced local defaults.
  A local pass is useful regression evidence, not proof that the full
  DP=3/256K external topology is solved.

Prefix-cache hits must be reported separately from cold-prefill performance.
Do not use prefix-cache-enabled numbers as cold-prefill gains.

## Current Performance Snapshot

Latest RTX PRO 6000 / SM120 dev evidence for the current D512 path is in the
low-instrumentation promotion and attribution runs recorded in
`docs/sm120_optimization_notes.md`.

- 59K C=1: about `7458 tok/s`, `7.9 s` TTFT.
- 59K C=2: about `7430 tok/s`, `12.0 s` TTFT.
- 124K C=1: about `6735 tok/s`, `18.4 s` TTFT.
- 124K C=2: about `6739 tok/s`, `27.6 s` TTFT.

The D512 retune produced a useful but bounded improvement: roughly `+6%`
input tok/s / `-6%` TTFT over the prior stable default, with dev-only
empty-tail skip adding another small endpoint gain in some 59K/124K shapes.
This did not close the GB10 raw-prefill gap.

GB10 / SM121 remains the main uncertainty. Current GB10 attribution shows much
lower effective sparse visits/s than RTX, and the Reddit / unholy-fusion report
is still materially ahead in GB10 prefill. A first same-shape startup probe says
the official `FLASHINFER_MLA_SPARSE_DSV4` route is blocked on the current
FlashInfer wheel, and a reduced dual RTX PRO 6000 / SM120 startup smoke shows
the same `Unsupported architecture` failure.

The current-default versus Reddit-style GB10 matrix covered 4K, 16K, 32K, 64K,
and 128K cold prefill with prefix cache disabled, MTP=2, EP enabled, FP8 KV,
and `FULL_AND_PIECEWISE`. `max_num_batched_tokens=8192` is a narrow latency
tradeoff, not a default profile: it was flat at 4K, about `3%` better at 16K,
about `6-8%` better at 32K/64K, and effectively flat again at 128K while
worsening p99 ITL. It also cut 131K KV-cache concurrency from roughly
`3.0x` to roughly `1.35-1.46x`. This does not explain the public
Reddit-scale prefill gap.

## Active Direction

The next high-value target is the GB10 long-prefill performance gap, measured
before more production code is added:

- The apples-to-apples GB10 C=1 default-versus-Reddit-style serving-flag matrix
  is now recorded for 4K / 16K / 32K / 64K / 128K. Do not promote the 8192
  chunk profile by default; keep it as an opt-in latency/capacity tradeoff.
- Do not spend more
  endpoint time on explicit upstream `FLASHINFER_MLA_SPARSE_DSV4` until the
  public FlashInfer stack advertises and passes an SM120/SM121 DS4 sparse MLA
  startup smoke.
- Keep prefix-cache-on and prefix-cache-off results separate.
- Record backend selection, MoE path, NCCL/all-reduce path, sparse candidate /
  value attribution, TTFT, input tok/s, decode tok/s, and ITL p95/p99.

If a maintainable upstream or official backend wins and passes the promotion
matrix, prefer that route over carrying fork-specific kernel code. If no public
backend wins, the next production-worthy experiment must reduce real
sparse-MLA candidate/value work, live state, or dependency depth for the DS4
mixed compressed-plus-SWA metadata shape.

Latest focused microbench / NCU follow-up keeps this direction intact. On RTX
PRO 6000, the D512 score kernel for the mixed C128/SWA shape is limited by low
eligible-warps / long-scoreboard behavior and shared-memory-limited occupancy,
while the value kernel is already near the GDDR7 DRAM roof. On GB10, `sudo ncu`
shows both score and value are dominated by low eligible-warps and L1TEX
long-scoreboard stalls rather than peak bandwidth. Candidate-length scaling is
close to linear on both systems. This means a grouped launch or index-generation
shortcut that keeps the same semantic candidates is unlikely to close the gap;
the useful work must reduce effective score/value visits or use a backend with
real cross-query KV reuse for the DS4 layout. The latest fused-stats/value and
lower-live-state D512 microbench confirmed this: RTX saw at most a small
microbench-only fused win, while GB10 regressed.

The current research hypothesis is therefore cross-query KV reuse for the C128A
DS4 sparse-MLA metadata layout. Harness stats reporting now derives
`cross_query_reuse_potential` from sampled candidate overlap so prototype work
can first prove reusable candidate mass before any endpoint code is added. Treat
that field as an upper-bound signal only: it is not a performance claim until a
microbench and then the endpoint promotion matrix show an actual win.

## Known Limits

- GB10 reduced long-C2 validates availability and token cadence only. It is not
  a 256K / 512K / 1M throughput claim.
- Dual RTX PRO 6000 covers roughly the 128K / 131K development envelope. Larger
  context and four-card claims require target-topology gates.
- Long+long C=2 fairness remains a promotion gate. It is not the current raw
  prefill research target, but regressions must block promotion.
- Ineffective experiments should be removed from vLLM code and recorded in the
  rejected notes rather than left as switches or dormant code paths.
