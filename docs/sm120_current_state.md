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
  behavior. Candidate-region reporting and MQA top-k elapsed/work reporting are
  diagnostic infrastructure, not claimed performance optimizations.
- Upstream comparison point: upstream now exposes an optional
  `FLASHINFER_MLA_SPARSE_DSV4` backend, but the current official FlashInfer
  `0.6.12` wheel is not a runnable SM120/SM121 backend in this setup. The
  backend marker is selected, but both a GB10 endpoint startup smoke and a
  direct minimal FlashInfer DSV4 API call on SM120/SM121 fail in
  `TllmGenFmhaRunner` with `Unsupported architecture`.
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
is still materially ahead in GB10 prefill. Repeated startup/API probes say the
official `FLASHINFER_MLA_SPARSE_DSV4` route is blocked on the current
FlashInfer wheel, and both SM120 and SM121 direct API calls show the same
`Unsupported architecture` failure.

The current-default versus Reddit-style GB10 matrix covered 4K, 16K, 32K, 64K,
and 128K cold prefill with prefix cache disabled, MTP=2, EP enabled, FP8 KV,
and `FULL_AND_PIECEWISE`. `max_num_batched_tokens=8192` is a narrow latency
tradeoff, not a default profile: it was flat at 4K, about `3%` better at 16K,
about `6-8%` better at 32K/64K, and effectively flat again at 128K while
worsening p99 ITL. It also cut 131K KV-cache concurrency from roughly
`3.0x` to roughly `1.35-1.46x`. This does not explain the public
Reddit-scale prefill gap.

## Active Direction

The next high-value target is split into two measurement tracks before more
production code is added:

1. Establish a 512K / 768K / 1M context frontier baseline on SM120 and GB10.
   This is a development observation gate, not a normal PR hard gate. Use
   `scripts/run_sm12x_very_long_context_frontier.sh` or the
   `very_long_context_capacity` baseline phase to record startup capacity,
   KV-cache bytes/token, C=1 cold/warm TTFT, input tok/s, decode tok/s, ITL
   p95/p99, runtime health, and GPU stats with prefix cache disabled and
   `FULL_AND_PIECEWISE` CUDA graphs still enabled.
   The first 2026-06-06 frontier baseline shows dual RTX PRO 6000 can admit and
   complete 1M C=1 with positive KV margin, but 1M cold TTFT is about `845s`.
   GB10 can admit and complete 1M C=1 only after raising the current MTP=2
   profile from `gpu_memory_utilization=0.70` to `0.75`, and measured 1M cold
   TTFT is about `3504s`, so GB10 1M is currently an availability probe rather
   than an interactive-latency claim.
   The first RTX 512K/1M Nsys attribution pass confirms the very-long TTFT
   problem is prefill kernel work rather than host/scheduler idle: 512K had max
   CUDA idle gap `0.103s`, and the partial 1M trace had max idle gap `0.018s`.
   `_accumulate_indexed_attention_chunk_multihead_kernel` and
   `_fp8_mqa_logits_kernel` dominated the trace, reaching about `75%` of 512K
   CUDA kernel time and about `83%` of the partial 1M trace. The 1M Nsys run
   failed before first token in the FP8 MQA logits/top-k path with CUDA OOM
   under profiler memory pressure, so use it as attribution evidence, not as a
   completed 1M latency sample.
2. Continue the GB10 long-prefill performance gap work, measured before more
   production code is added:

- The apples-to-apples GB10 C=1 default-versus-Reddit-style serving-flag matrix
  is now recorded for 4K / 16K / 32K / 64K / 128K. Do not promote the 8192
  chunk profile by default; keep it as an opt-in latency/capacity tradeoff.
- Do not spend more endpoint time on explicit upstream
  `FLASHINFER_MLA_SPARSE_DSV4` until the public FlashInfer stack advertises and
  passes an SM120/SM121 DS4 sparse MLA direct-API smoke first, then an endpoint
  startup smoke.
- Keep prefix-cache-on and prefix-cache-off results separate.
- Record backend selection, MoE path, NCCL/all-reduce path, sparse candidate /
  value attribution, TTFT, input tok/s, decode tok/s, and ITL p95/p99.

If a maintainable upstream or official backend wins and passes the promotion
matrix, prefer that route over carrying fork-specific kernel code. If no public
backend wins, the next production-worthy experiment must reduce real
sparse-MLA candidate/value/logits work, live state, memory pressure, or
dependency depth for the DS4 mixed compressed-plus-SWA metadata shape. Do not
prioritize scheduler-idle fixes or `_combine_topk_swa_indices_kernel` for the
512K-to-1M TTFT nonlinearity unless future profiling contradicts the current
Nsys attribution.

Upstream DeepSeek backlog triage should run before adding more local sparse-MLA
code. The current order is:

1. Check stability and semantic fixes that overlap known user reports:
   DeepSeek V4 DBO prefill metadata preservation, prefix-cache retention /
   KV lifecycle behavior, CUDA graph / MLA metadata correctness, and SM12x
   crash workarounds.
2. Follow upstream simplification and KV-cache layout work when rebasing:
   DeepSeek V4 attention refactors, NVIDIA-only cleanup, model-specific
   KV-cache planning, and contiguous KV packing. Prefer aligning with these
   designs over preserving local compatibility shims.
3. Treat upstream official FlashInfer / TRTLLM sparse-MLA work as blocked for
   SM120 / SM121 until a direct DS4 sparse-MLA FlashInfer API smoke passes on
   the target architecture. Do not re-enter endpoint tests first.
4. Keep PCP / DCP / context-parallel prefill as a four-card or larger-topology
   research track, not a dual-card default-optimization path.
5. Only after the above checks are clean, return to new candidate/value-work
   reduction experiments.

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

Persistent TODO: the next production-class prefill improvement must reduce
long-prefill sparse-MLA real work or memory pressure, especially in
`_accumulate_indexed_attention_chunk_multihead_kernel` and the FP8 MQA
logits/top-k path. Scheduler shaping and chunk-size tuning remain fallback
controls, not the main route to close the 512K/1M TTFT and GB10 prefill gap.
The rejected 2026-06-06 C128 metadata-stage cap confirms this boundary: C128
sparse accumulate improves, but 512K/1M MQA top-k work remains in the C4A
indexed D512 path. The cap deliberately drops C128 candidates, does not reduce
MQA top-k, and has been removed from the code path. The next attribution target
is C4A MQA/logits/top-k and sparse-accumulate value traffic reduction rather
than more C128 metadata slicing.

The first no-cap work-only attribution after removing the C128 cap keeps that
direction. On RTX PRO 6000, 59K / 124K / 512K C=1 showed effective sparse
visits per prompt token rising from about `41.6K` to `51.9K` to `114.6K`,
while MQA logits elements per prompt token rose from about `340K` to `677K`
to `2.78M`. The 512K run materialized about `5.82TB` of MQA logits and
estimated about `61.5TB` of sparse-accumulate value reads. That means the
512K/1M problem is real work growth, not a scheduler-idle artifact. A quick
full-logits versus chunked-MQA microbench also showed the existing chunked path
is slower (`1.4-1.5x` at 32K-131K KV for the endpoint-like 256-query,
32-head, topk-512 shape), so do not re-enter simple MQA chunking. A useful MQA
experiment must fuse logits generation with top-k selection or otherwise
avoid writing/reading the logits matrix without adding extra merge launches.
The 512K MQA stats were also reprocessed with explicit valid/logits accounting:
valid KV visits were `1.443T` out of `1.455T` logits elements, so logits
padding was only about `0.79%`. Do not prioritize simple valid-span clipping or
row-block mask early-exit as a primary 512K optimization route.
The first Triton exact tile-local topK feasibility probe also does not justify
endpoint work: `tl.topk` returns values but not indices, the threshold+cumsum
index recovery path hits shared-memory limits at the useful `M=16,N=1024` and
`M=8,N=2048` shapes, and wide-N MQA logits tiles either exceed shared memory or
run slower than the current `M=64,N=128` logits kernel. Treat Triton tile-local
fused MQA topK as blocked until there is an indexed selection primitive or a
backend that keeps current tensor-core tiling while avoiding full logits
materialization.
The follow-up vLLM top-k primitive audit keeps the same boundary: existing
`top_k_per_row_prefill`, `persistent_topk`, and the FlashInfer-derived
`FilteredTopKRaggedTransform` are selectors over an already materialized
float32 logits matrix. They can improve selection behavior, but they cannot
remove the 512K-scale MQA logits write/read by themselves. Do not start a new
optimization by swapping only the selector. A useful MQA route must fuse FP8
MQA score generation with indexed top-k selection, or use an official backend
that does the equivalent for the DS4 sparse metadata shape.

The first follow-up grouped-combined microbench did not win. It removed the
old separate compressed/SWA state merge by writing grouped-compressed and SWA
scores into one combined score workspace, then using one full stats pass and
separate compressed/SWA value passes into one output. The extra split launches
and loss of current head-block reuse still outweighed the compressed KV reuse
on both RTX PRO 6000 and GB10, and a wider grouped score tile exceeded GB10
shared memory. Do not reintroduce this split-launch grouped-combined route.
Future cross-query reuse work must be tighter: fewer effective score/value
visits, less value traffic, or a single/fused backend that preserves current
head reuse and avoids extra merge or split value launches.

A narrower single-launch grouped full-score probe also did not win. It kept
the current stats/value path and only replaced score materialization, reusing
compressed KV across query rows inside one score launch and conservatively
falling back for the small SWA tail. On RTX PRO 6000, the corrected
`1024 compressed + 128 SWA` C128A shape regressed from about `0.797-0.798 ms`
split total to `0.891-1.522 ms` across token/head group tiles. The best tile
still made score slower (`0.321 -> 0.414 ms`) and did not touch value traffic.
Do not continue grouped-score-only work unless it also reduces value traffic
or preserves current head-block reuse without losing occupancy.

A two-pass grouped-union replay probe also did not win. It traversed a
group-level union of C128A candidates, computed per-row grouped stats without
writing the full score workspace, then replayed the same union for value
accumulation. The shape had high theoretical reuse, but the value pass had to
recompute QK scores and use smaller grouped tiles to fit shared memory. On RTX
PRO 6000 it reached only about `0.33x` of the current D512 split path at the
target `1024 compressed + 128 SWA` shape; on GB10 the best reduced probe was
about `0.74x`. Do not continue two-pass grouped replay. Future fused C128A
work must avoid score replay and preserve the current split path's head reuse,
or reduce effective value traffic inside a single backend.

A follow-up exact row-dedup diagnostic also found no current opportunity: the
new opt-in `candidate_row_duplicates` stats field reported `0` duplicate
candidate visits across `1408` sampled rows in a 4K RTX attribution smoke, both
overall and within compressed/SWA regions. Do not spend kernel time on
same-row duplicate elimination unless a future stats run shows non-zero
duplicate visits.

## Known Limits

- GB10 reduced long-C2 validates availability and token cadence only. It is not
  a 256K / 512K / 1M throughput claim.
- Dual RTX PRO 6000 covers roughly the 128K / 131K development envelope. Larger
  context and four-card claims require target-topology gates.
- Long+long C=2 fairness remains a promotion gate. It is not the current raw
  prefill research target, but regressions must block promotion.
- Ineffective experiments should be removed from vLLM code and recorded in the
  rejected notes rather than left as switches or dormant code paths.
