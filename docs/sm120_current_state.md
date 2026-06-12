# SM120 Current State

Start here before reading the longer historical notes. This file is the compact
working entrypoint for DeepSeek V4 SM12x optimization status, current gates, and
next-step decisions. New experiment notes and durable decisions should use the
framework in `docs/sm120/`. Treat `docs/sm120_optimization_notes.md` as the
legacy evidence archive.

Last updated: 2026-06-12.

## Read Order

1. Read this file for the current branch posture and next target.
2. Read `docs/sm120/README.md` for the new note structure and writing rules.
3. Read `docs/sm120/index.md` for framework-era decisions and experiment
   packages.
4. Read `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/README.md`
   before starting the next optimization branch.
5. Read `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/preflight.md`
   before running RTX or GB10 experiments.
6. Read
   `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/preflight-results.md`
   for the latest sanitized readiness snapshot before deciding whether to
   rerun preflight.
7. Read `docs/sm120/experiments/2026-06-12-black-benediction-map/README.md`
   before porting or imitating the external black-benediction line.
8. Read `docs/vllm_correctness_gates.md` for promotion requirements.
9. Read `docs/sm12x_triton_sparse_mla_rewrite_plan.md` before starting the
   next fork-independent sparse-MLA prefill kernel/backend iteration.
10. Read `docs/dgx_spark_bare_metal_cluster.md` for GB10 / SM121 setup and
   reduced long-context gates.
11. Use `docs/sm120_experiment_index.md` to jump into pre-framework historical
   experiments.
12. Use `docs/sm120_optimization_notes.md` only when you need the detailed
   legacy artifact trail or rejected-route rationale.

## Current Posture

- PR-ready work: the D512 sparse-MLA prefill stack plus the supporting
  scheduling, workspace warmup, prefix/KV lifecycle, and correctness fixes that
  already passed promotion gates. This is the current defensible customer
  baseline for dual RTX PRO 6000 / SM120 and the reduced GB10 / SM121 envelope.
- GB10 recommended serve shape: use the MP executor with expert parallel
  disabled by default, FlashInfer autotune left on the current vLLM default,
  FP8 KV, MTP=2 when exercising the production path, and
  `FULL_AND_PIECEWISE`. Keep EP as an environment-controlled fallback A/B
  dimension only.
- Active next task: run the EP-off backend-parity program described in
  `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/README.md` and
  `docs/sm120/experiments/2026-06-12-black-benediction-map/README.md`. Develop
  and profile on dual RTX PRO 6000 / SM120 first, then confirm promising
  candidates on GB10 / SM121. The next integration should be a conservative,
  easy-to-deploy branch based on explained bottleneck evidence and public
  upstream dependency capabilities where possible. The Triton sparse-MLA
  rewrite plan remains a candidate route if attribution shows sparse dataflow
  or cost-per-effective-visit is the bottleneck.
- Branch posture: keep `codex/ds4-sm120-min-enable` as the PR/user-facing
  base. Use `codex/ds4-sm120-backend-parity-dev-20260612` at `7224e68417` as
  the next dev starting point; it is based on PR stable preview `f32247a5a6`
  plus one signed SM12x sparse-MLA selector diagnostic commit. When the PR
  branch is rebased later, recreate or rebase dev on the new PR tip and split
  any PR-worthy dev fix into reviewable PR-branch commits.
- Naming posture: use SM120 for RTX PRO 6000 work and SM121 for GB10 work.
  B200 is an older SM10x baseline name and should appear only in historical
  notes or as a compatibility variable for older harness scripts.
- Upstream reference posture: this phase is frozen to vLLM upstream/main
  `b7f9b6a`, vLLM PR `#45277` `e57d3b78`, black-benediction `c6b2a7b`,
  FlashInfer upstream/main `d65c3eb`, FlashInfer PR `#3395` `88539d03`, and
  b12x master `fabb087`. Do not chase remote heads during routine candidate
  runs; refresh only during an explicit upstream-change review or when a
  dependency change is likely to affect SM12x behavior.
- Newly promoted work: exact chunked D512 online merge for
  `combined_topk > 1152`. It is now default-on because the RTX promotion subset,
  GSM8K limit-200, prefix/KV lifecycle checks, and GB10 reduced long-C2 gate are
  green. `VLLM_DEEPSEEK_V4_INDEXED_D512_CHUNKED_PREFILL=0` remains available as
  an emergency rollback switch.
- Dev-only work: D512 empty-tail skip, exact C128A active-width metadata
  narrowing, and sparse MLA candidate-region attribution. Empty-tail skip has
  small endpoint gains, but it must keep GSM8K limit-200 and the full promotion
  matrix green before becoming PR-branch behavior. C128A active-width narrowing
  has a positive 512K-under-1M endpoint signal and does not drop candidates, but
  it is a bounded dead-tail reduction rather than a true 1M work reduction.
  Candidate-region reporting and MQA top-k elapsed/work reporting are
  diagnostic infrastructure, not claimed performance optimizations.
- Upstream comparison point: upstream now exposes an optional
  `FLASHINFER_MLA_SPARSE_DSV4` backend. In the current branch this is the
  FlashInfer `flashinfer.mla.trtllm_batch_decode_sparse_mla_dsv4` route, which
  targets the plain BF16 / per-tensor-FP8 KV layout. It is not the newer packed
  `584B/token` SM120 sparse-MLA route from the unmerged FlashInfer SM120 work.
  The current official FlashInfer `0.6.12` wheel still does not expose
  `flashinfer.sparse_mla_sm120`, and the earlier plain-route startup/API probes
  fail in `TllmGenFmhaRunner` with `Unsupported architecture`. An isolated GB10
  build of the unmerged packed SM120 sparse-MLA backend now passes direct DSV4
  packed single-cache prefill, dual-cache prefill, and decode correctness
  smokes. The adapter question is now narrower: the tested packed backend
  requires a main `page_block_size=64` and only supports secondary
  `page_block_size=64` or `2`. Current code audit shows the actual vLLM
  physical cache shapes are compatible in principle: SWA uses `64`, C4A
  compressed cache uses `64`, and C128A compressed cache uses `2`; the old
  `256` reading was the global scheduler/cache block preference, not the
  packed wrapper's physical page size. A GB10 endpoint-shaped component probe
  validated the next adapter assumption: vLLM's
  `build_flashinfer_mixed_sparse_indices` output can be split into the packed
  wrapper's main SWA stream and extra compressed stream for both C4A and C128A,
  with correct per-stream lengths and zero-KV LSE. The endpoint adapter was
  archived as a local reference branch after the 2026-06-08 GB10 subset because
  it depends on an unmerged FlashInfer packed backend and has not passed the
  full RTX + GSM8K + lifecycle promotion matrix. Current dev and PR branches
  should not contain a `VLLM_DEEPSEEK_V4_FLASHINFER_PACKED_PREFILL` runtime
  path. The current FlashInfer PR `#3395` head is `88539d03`; keep it as a
  reference candidate because the old GB10 subset showed about `10-23%` TTFT
  improvement, but revalidate it under EP-off before promotion.
- Blocked or rejected as current endpoint backends, in the specific forms that
  were tested: public b12x / FlashInfer wheels as a direct DS4 endpoint
  backend, upstream `FLASHINFER_MLA_SPARSE_DSV4` with the current official
  wheel, standalone C128 grouped-compressed prefill, generic D512
  selector/tile/chunk sweeps, BF16 score workspace, SWA-only routing through
  the current D512 helper, grouped-query local-SWA tiling that keeps the same
  candidate work, and the grouped-SWA-final D512 endpoint route. The last route
  was rejected after route stats corrected the real C4A shape to
  `512 compressed + 128 SWA`: it regressed RTX C=1 TTFT and was slower in the
  same shape on GB10. A fused-stats/value D512 prototype and a lower-live-state
  value-tile prototype were also rejected because they did not improve GB10 and
  did not reduce real candidate/value visits. This is not a rejection of the
  newer local-inference-lab B12X backend stack; that line must be tested as a
  separate backend/dataflow candidate.
- A separate leavelet DeepGEMM `sm120` recheck found strong isolated FP8 MQA
  logits speedups, but the vLLM endpoint route is not viable in the current
  production profile: full top-k microbench was flat, and enabling the route
  caused startup failure during FULL_AND_PIECEWISE CUDA graph memory profiling
  with custom all-reduce. Do not add a DeepGEMM MQA env switch to Dev/PR unless
  that startup failure and full top-k cost are solved.

## Promotion Matrix

Any sparse-MLA, scheduler, workspace, or backend change that affects serving
behavior must preserve:

- GSM8K limit-200 correctness.
- DFlash or speculative-decode changes must clear GSM8K limit-200 before their
  performance numbers are used for promotion, because this class of change can
  alter task correctness even when latency improves.
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
- GB10 MTP=2 MoE TP deadlock sustained gate for the latest two-node GB10
  report. This is separate from forum53: use
  `scripts/run_gb10_mtp2_moe_tp_deadlock_gate.sh` to cover prefix cache enabled,
  MTP=2, FP8 KV, `max_model_len=200000`, `max_num_seqs=8`, and
  `FULL_AND_PIECEWISE`, with a no-token-progress watchdog and rank stack
  capture. Current clean sustained evidence uses `gpu_memory_utilization=0.80`;
  higher `0.90+` GB10 startup probes have produced current-boot NVIDIA driver
  OOM signals around CUDA graph profiling, so driver health is a first-class
  gate result rather than a post-hoc note.
- GB10 forum53 multi-user prefix-cache admission gate for scheduler/KV changes:
  use `scripts/run_gb10_forum53_multi_user_gate.sh`. The default gate is now a
  guarded two-round C=2 profile with prefix cache enabled, `max_num_seqs=2`,
  `max_model_len=81920`, `gpu_memory_utilization=0.685`, and
  `max_num_batched_tokens=4096`. The script computes a preflight safe
  context limit from `2048898 * 0.70 / max_num_seqs` and refuses larger
  `max_model_len` values unless `GB10_FORUM53_SKIP_CONTEXT_GUARD=1` is set.
  That guard is a capacity ceiling only; larger C=2 shapes still need clean
  startup and post-run driver-health evidence before they can be treated as
  review baselines.
  Use explicit `GB10_FORUM53_BATCHED_TOKEN_SWEEP` runs for 2048/8192 tuning.
  Real-user C=4+ long-context agent shapes should use
  `GB10_FORUM53_PROFILE=c4_prefix_cache_pressure` or the larger long-prefix
  profile as development observation gates because they are too costly and too
  high-risk for every PR refresh, but they should be run before claiming
  improvement for prefix-cache-heavy multi-agent workloads.

Prefix-cache hits must be reported separately from cold-prefill performance.
Do not use prefix-cache-enabled numbers as cold-prefill gains.

## Current Performance Snapshot

Latest RTX PRO 6000 / SM120 PR stable-preview evidence is the 2026-06-12
EP-off, MTP, prefix-cache-disabled refresh under
`artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/`.
Use these as the current short-prefill and correctness baseline before looking
back at the 2026-06-10 EP A/B data.

- Cold OSL=1 random prefill, input lengths `1024/4096/16384/65536`:
  `6606.45 / 6206.06 / 8056.05 / 7540.46` input tok/s, with all phase exits
  `0`.
- OSL=128 short-throughput supplement, input lengths `4096/16384/65536`:
  `3123.74 / 6209.00 / 7049.72` input tok/s and
  `97.60 / 48.51 / 13.77` output tok/s, with all phase exits `0`.
- GSM8K 5-shot limit-200 exact match: flexible `0.965`, strict `0.940`,
  exit `0`.

The latest GB10 / SM121 PR stable-preview user-feedback gate is
`artifacts/codex_pr_stable_preview_f32247a/2x_gb10_sm121/gb10_forum53_mtp2_epoff_c2_gmem0685_mml81920/20260612074113`:
EP-off, MTP=2, prefix cache enabled, C=2, 4/4 requests, 0 failures, max TTFT
`124.045698 s`, ITL p99 `0.144954 s`, prefix hits `79872`, and clean driver
health.

Earlier RTX PRO 6000 / SM120 long-context dev evidence for the current D512
path is in the low-instrumentation promotion and attribution runs recorded in
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
official plain `FLASHINFER_MLA_SPARSE_DSV4` route is blocked on the current
FlashInfer wheel, and both SM120 and SM121 direct API calls show the same
`Unsupported architecture` failure. Keep that distinct from the unmerged packed
SM120 sparse-MLA route, which is not available in the current wheel. A direct
GB10 component smoke against an isolated build passed DSV4 packed
prefill/decode correctness, so the remaining work is proving an endpoint
adapter can reduce real sparse-MLA work without regressions.
The first endpoint-shaped adapter prototype for that packed route produced a
positive GB10 attribution signal at every tested input length, with prefix cache
both disabled and enabled. `4096/8192/32768/128000` improved input tok/s by
roughly `1.11-1.15x` and TTFT by roughly `10-23%` against the same-day env-off
control, while preserving the same effective candidate-visit counts. This
proves the 4K/8K gap can be affected by sparse-MLA prefill backend/dataflow,
not only by very-long-context C128 candidate growth. The route also passed a
GB10 reduced long-C2 gate and a reduced MTP=2 MoE TP soak with clean driver
health. It remains a reference implementation only: the endpoint gain is not
enough to explain the full Aiden/unholy gap, the dependency is not an official
wheel path, and RTX + GSM8K + prefix/KV lifecycle promotion is still pending.

External feedback on 2026-06-07 strengthens the GB10 prefill-gap concern: a
NVIDIA Developer Forums report for the local-inference-lab / unholy-fusion
line lists C=1/C=2/C=4 prefill around `1.9k tok/s` and decode sweet spot around
`52 tok/s`, while calling the B12X FP8 variant the winner. Treat that as an
external target, not as locally reproduced evidence. The current local finding
is that the gap is backend/dataflow-shaped, not explained by serving flags
alone.
The latest current-Dev GB10 EP-off A/B reinforces that reading: with TP=2,
prefix cache disabled, MTP=2, FP8 KV, `max_num_batched_tokens=4096`, and
`FULL_AND_PIECEWISE`, disabling expert parallel produced `776/1310/1331/1290`
input tok/s at `4K/16K/32K/64K`, still well below Aiden prefix-off
`1128/1875/1920/1913`. Do not treat EP-off as the path to close the raw
prefill gap.

The current-default versus Reddit-style GB10 matrix covered 4K, 16K, 32K, 64K,
and 128K cold prefill with prefix cache disabled, MTP=2, EP enabled, FP8 KV,
and `FULL_AND_PIECEWISE`. `max_num_batched_tokens=8192` is a narrow latency
tradeoff, not a default profile: it was flat at 4K, about `3%` better at 16K,
about `6-8%` better at 32K/64K, and effectively flat again at 128K while
worsening p99 ITL. It also cut 131K KV-cache concurrency from roughly
`3.0x` to roughly `1.35-1.46x`. This does not explain the public
Reddit-scale prefill gap.

The latest public b12x recheck changes the dependency picture but not the
endpoint decision yet. b12x `0.20.0` or newer now exposes DS4 compressed-MLA, compressed
indexer, sparse-indexer extend top-k, native FP4 MoE, FP8 block-linear, fused
WO projection, mHC residual, and PCIe all-reduce APIs, and the compressed-MLA
microbench compiles on RTX PRO 6000 SM120 and both GB10 nodes.
In endpoint-like real-C128 microbench shapes, b12x is much faster than the
older packed online helper, but still slower than the current D512
split+finish kernel-only timing. A follow-up runtime probe separates package
availability from vLLM integration: current Dev exposes the upstream
FlashInfer B12X MoE runtime path, but not Aiden's B12X sparse indexer, native
MXFP4 B12X MoE runtime plumbing, DS4 B12X WO projection / mHC hooks, or a
DS4-specific compressed-MLA runtime adapter. The Aiden production image does
expose the sparse indexer and native MXFP4 B12X MoE runtime hooks, but still not
a runtime-importable DS4 compressed-MLA adapter in its installed vLLM package.
Public b12x mHC was slower than the current TileLang fused path in standalone
GB10 microbenching, and public b12x WO projection plus public b12x FP8
block-linear are both blocked on the missing Cutlass DSL MXFP8 MMA symbol.
The direct b12x `0.20.0+` `block_fp8_linear_mxfp8` smoke on the current
vLLM/Torch stack still fails at compile time because public
`nvidia-cutlass-dsl==4.5.2` has no `cutlass.cute.nvgpu.warp.MmaMXF8Op`.
FlashInfer `#3489` adds MXFP8 GEMM plumbing, but the installed `0.6.12` SM121
wheel does not yet unblock this route: `mm_mxfp8` `auto/cutlass` fails the
SM120 kernel's mat2 layout check and explicit `cudnn` is not supported for
capability 121. Neither mHC, WO, nor B12X FP8 block-linear should be the next
endpoint port under the public package stack.
The public b12x sparse-indexer prefill `extend_tiled_topk` route also failed a
direct GB10 component smoke during TMA partitioning, so do not port the
unholy/Aiden sparse-indexer prefill branch directly under the released b12x
stack.
Public b12x native MXFP4 MoE is dependency-unblocked in a standalone GB10
smoke, including a full `E=256` synthetic DS4-shaped call, but the
Aiden/unholy implementation is non-EP only and prior MoE-off endpoint A/B says
it is a small positive component rather than the main prefill-gap source.

The follow-up b12x page-view probe corrected the earlier cache-layout reading:
vLLM exposes a logical 3D `fp8_ds_mla` tensor with `584` byte token stride, but
the physical CUDA page can be exported as a zero-copy 2D
`[num_pages, page_nbytes]` page-byte view that matches public b12x compressed
MLA. Direct CUDA component smokes passed for SWA-only `page_size=64` and
SWA+indexed `page_size=2` with `max_abs_diff=3.0517578125e-05`. That removes
the layout blocker, but it does not make b12x compressed MLA an endpoint
optimization: the endpoint-like `real_c128` microbench measured public b12x at
`3.951 ms` versus current D512 split+finish at `1.443 ms`. Do not add a
production endpoint adapter for this direct route unless a newer backend or a
different sparse-MLA dataflow changes that performance result and then passes
the promotion matrix.

The same 2026-06-08 GB10 recheck also tested public b12x
`compressed_indexer.index_topk_fp8` on the shared-prefill path. The API is
runnable and correct against the reference on small shapes, including
row-shared page tables. It is not a better endpoint candidate by itself:
current SM12x `fp8_fp4_mqa_topk_indices` is about `3.4-3.8x` faster on the
same linear-KV top-k work, and `cp_gather_indexer_k_quant_cache` measured only
about `0.013 ms` at 32K tokens and `0.135 ms` at 131K tokens. Avoiding that
gather copy does not offset the slower public b12x top-k route. Do not port the
public compressed-indexer route into vLLM unless a future b12x/FlashInfer
release changes those component timings.

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
- Do not spend more endpoint time on env-only selection of upstream
  `FLASHINFER_MLA_SPARSE_DSV4`: the current route is the plain FlashInfer DSV4
  path and is already blocked in this environment. The unmerged packed SM120
  sparse-MLA backend has now passed direct DS4 packed prefill/decode component
  smokes on GB10, so the next FlashInfer work is a Dev-only adapter/prototype
  that measures endpoint TTFT/input tok/s and promotion-matrix risk.
- Re-audit and A/B the latest local-inference-lab `main` and
  `dev/unholy-fusion` before the next GB10 backend experiment. The promising
  pieces are B12X sparse MLA, B12X sparse indexer / compressed-indexer copy
  avoidance, native B12X MoE, plus the inherited PR 43477 scratch fixes. The
  public Aiden image currently exposes the older unholy-style B12X switches;
  it does not recognize the Aiden repository's newer
  `VLLM_USE_B12X_DEEPSEEK_V4*` switches. The public-b12x `0.20.0+` mHC route
  has now been rechecked with a standalone GB10 microbench and is rejected for
  current Dev: `b12x_mhc_post_pre` is slower than the existing TileLang fused
  MHC path with and without fused norm. The public-b12x `0.20.0` WO projection
  route is dependency-blocked in the current public stack: DS4-shaped weight
  packing succeeds, but the first fused WO call fails because public
  `nvidia-cutlass-dsl==4.5.2` lacks `cutlass.cute.nvgpu.warp.MmaMXF8Op`. The
  public-b12x sparse-indexer prefill route is likewise blocked for endpoint
  use: a direct `extend_tiled_topk` smoke failed during TMA partitioning on
  GB10, and the unholy branch's prefill path still materializes temporary
  gathered KV tensors outside the current workspace manager. The
  Model Runner V2 enablement alone is unlikely to explain the prefill gap, but
  it may be required for that stack's warmup/scratch compatibility.
- Use `scripts/run_gb10_b12x_backend_ab_matrix.sh` for that comparison. It
  wraps the existing GB10 prefill-gap gate and takes semicolon-separated
  `GB10_B12X_AB_TARGETS` entries in
  `label|vllm_root|vllm_venv|profiles|variants|env_file` form, so fork-specific
  backend flags can live in ignored local env files instead of tracked docs.
- The first controlled GB10 smoke against the refreshed local-inference-lab
  stack did not complete a request with public dependencies. It progressed far
  enough to prove that B12X FP8 linear, B12X MoE, the sparse indexer, and
  `B12X_MLA_SPARSE` can be selected, but failed on public dependency/backend
  gaps: released b12x before `0.20.0` lacks the expected FP8 linear module,
  the full B12X FP8 linear path needs a CUTLASS DSL MMA symbol not present in
  public `4.5.2`, and the tested fallback scaled-mm paths were not usable on
  GB10. Keep this route as blocked/recheck, not rejected, until the dependency
  stack can pass a small endpoint smoke.
- A later public recipe for the Aiden image explains why the above smoke is not
  equivalent to the reported working stack. The image is an offline micromamba
  build with a local FlashInfer wheel, an installed vLLM overlay, and a bundled
  b12x source tree that includes the compressed indexer / sparse MLA / FP8
  linear modules missing from earlier public-wheel probes. Treat this as a
  separate "Aiden image parity" route. Before any port, first reproduce the
  image recipe on GB10 with `scripts/run_gb10_aiden_image_parity.sh`, record
  backend evidence, post-run driver health, and the same random-prefill subset,
  then diff the overlay against upstream/current Dev. This is an
  external-backend comparison, not a promotion gate for our vLLM branch. The
  helper keeps the request model alias separate from the real DS4 tokenizer so
  a valid server is not misclassified by a client-side tokenizer lookup.
  The clean-reboot GB10 Aiden image parity runs after the alias/tokenizer fix
  are now valid. They selected B12X MXFP4 MoE plus FlashInfer sparse-MLA decode
  autotune markers, kept driver signal count `0`, and completed the reduced
  random-prefill curve at `4096`, `16384`, `32768`, and `65536` input tokens.
  Keep the two Aiden modes separate:

  | ISL | Current Dev prefix-off tok/s | Aiden prefix-off tok/s | Prefix-off speedup | Aiden recipe prefix-on tok/s | Prefix-on speedup |
  | ---: | ---: | ---: | ---: | ---: | ---: |
  | `4096` | `842.80` | `1128.37` | `1.34x` | `1018.91` | `1.21x` |
  | `16384` | `1301.35` | `1874.60` | `1.44x` | `2275.56` | `1.75x` |
  | `32768` | `1354.05` | `1919.63` | `1.42x` | `3449.26` | `2.55x` |
  | `65536` | `1313.08` | `1913.46` | `1.46x` | `3458.36` | `2.63x` |

  The prefix-off result is the useful raw-prefill comparison: Aiden is still
  about `1.3-1.5x` faster, so there is a real backend/dataflow gap. The
  prefix-on public recipe widens the observed 32K/64K gap to about `2.6x`, but
  that path had prefix-cache hits and should not be treated as pure kernel
  evidence.
- Follow-up import and component probes narrowed the most promising Aiden
  dependency route. The public Aiden image wheelhouse contains a patched
  `flashinfer_python-0.6.12` plus `flashinfer_cubin-0.6.11.post3` combination
  that exposes `flashinfer.sparse_mla_sm120.BatchSparseMLAPagedAttentionWrapper`.
  Installing only the cubin wheel into the normal official
  FlashInfer `0.6.12` venv does not expose the wrapper. Installing both
  image wheels into an isolated GB10 venv does expose it, with the same
  `run(q, kv_cache, indices, output, sm_scale, ..., extra_kv_cache=...)`
  signature observed inside the Aiden image. Small GB10 component smokes passed
  for single-cache and dual-cache DSV4 prefill with `num_heads=16`,
  `topk=128`, main `page_block_size=64`, and secondary `page_block_size=64`.
  A follow-up vLLM-shaped probe with `scripts/run_flashinfer_packed_mla_probe.sh`
  passed C4A and C128A split-index cases against the wrapper. This makes the
  next route concrete: prototype a Dev-only adapter around the packed
  FlashInfer SM120 sparse-MLA wrapper, then measure endpoint TTFT/input tok/s
  against current D512 before any default switch. The remaining integration
  risk is endpoint workspace/graph/performance, not wrapper availability or
  cache page shape.
- Use `scripts/run_b12x_stack_probe.sh` before any new B12X endpoint
  experiment to classify the target venv/image as public b12x,
  Aiden/unholy bundled b12x, FlashInfer-b12x NVFP4, or missing. Public
  b12x `0.15.2` historically exposed only the generic MLA front door, but
  public b12x `0.20.0+` now exposes the DS4-relevant compressed MLA scratch,
  compressed indexer, sparse-indexer extend top-k, native FP4 MoE preparation,
  FP8 block-linear, fused WO projection, mHC residual, and PCIe all-reduce APIs
  in RTX PRO 6000 and GB10
  import-only probes. This removes the old "private/bundled API only" blocker.
  It does not prove endpoint readiness:
  vLLM still needs explicit DS4 metadata wiring, GB10 runtime import
  confirmation in the actual vLLM venv, and promotion-matrix performance /
  correctness gates before any default route change.
- A follow-up Aiden image A/B disabled B12X MoE with
  `VLLM_USE_B12X_MOE=0`, leaving the same prefix-cache-off profile, FP8
  indexer cache, FlashInfer sparse-MLA decode autotune, NCCL version, and
  `FULL_AND_PIECEWISE` graph mode. That run still beat current Dev by about
  `1.26-1.42x`, while B12X-MoE-on was only `1.02-1.06x` faster than MoE-off:

  | ISL | Current Dev prefix-off tok/s | Aiden B12X-MoE tok/s | Aiden MoE-off tok/s | MoE-off speedup vs Dev | B12X-MoE speedup vs MoE-off |
  | ---: | ---: | ---: | ---: | ---: | ---: |
  | `4096` | `842.80` | `1128.37` | `1063.90` | `1.26x` | `1.06x` |
  | `16384` | `1301.35` | `1874.60` | `1814.40` | `1.39x` | `1.03x` |
  | `32768` | `1354.05` | `1919.63` | `1875.67` | `1.39x` | `1.02x` |
  | `65536` | `1313.08` | `1913.46` | `1859.70` | `1.42x` | `1.03x` |

  This shifts the immediate investigation away from "B12X MoE alone" and
  toward the wider Aiden/unholy overlay: sparse indexer / compressed-indexer
  movement, model-runner integration, all-reduce path, and sparse-MLA
  dataflow. A later diagnostic run proved that the public image ignores the
  Aiden repository's `VLLM_USE_B12X_DEEPSEEK_V4*` knobs, so do not use those
  envs for public-image component attribution.
- A sparse-indexer-only follow-up forced
  `VLLM_USE_B12X_SPARSE_INDEXER=1` while keeping prefix cache disabled and B12X
  MoE enabled. The valid CLI benchmark run completed with driver signal count
  `0`, but it did not beat the Aiden prefix-off base:

  | ISL | Current Dev prefix-off tok/s | Aiden prefix-off tok/s | Aiden sparse-indexer tok/s | Sparse/base | Sparse/current |
  | ---: | ---: | ---: | ---: | ---: | ---: |
  | `4096` | `842.80` | `1128.37` | `945.96` | `0.84x` | `1.12x` |
  | `16384` | `1301.35` | `1874.60` | `446.92` | `0.24x` | `0.34x` |
  | `32768` | `1354.05` | `1919.63` | `1845.05` | `0.96x` | `1.36x` |
  | `65536` | `1313.08` | `1913.46` | `1800.44` | `0.94x` | `1.37x` |

  This makes the exposed sparse-indexer env a weak/rejected route for now. It
  does not explain Aiden's base advantage; the useful next target remains the
  wider overlay and sparse-MLA dataflow, not this single env switch.
- Public/official b12x MoE is still not a direct current-Dev solution for
  DeepSeek V4 Flash. `VLLM_USE_B12X_MOE=1` is not a recognized vLLM env on the
  current branch, and explicit `--moe-backend flashinfer_b12x` fails closed
  because that backend is wired through the NVFP4 oracle, while DS4 Flash uses
  MXFP4 experts. The Aiden/unholy route therefore depends on a native MXFP4
  B12X integration that is not the same as the current upstream
  `flashinfer_b12x` NVFP4 path. Public b12x `0.20.0+` now exposes
  `prepare_b12x_fp4_moe_weights`, so the dependency/API blocker has moved from
  "not public" to "not integrated or endpoint-validated in current Dev". Treat
  this as an explicit vLLM backend integration task, not a serving-flag issue.
  Future NVIDIA NVFP4 support should stay a separate quantization route: do not
  make MXFP4 DS4 Flash code depend on NVFP4 oracle assumptions, but keep the
  MoE backend boundary explicit enough that a later NVFP4 backend can share
  scheduling, warmup, graph, and quality gates without reworking the DS4 MXFP4
  path.
- Revisit older rejected-note wording when using it to guide new work. The
  prior negative results remain valid for public-wheel direct API probes,
  simple serving-flag changes, selector-only swaps, and local split-launch
  grouped-query prototypes. They do not prove that local-inference-lab's custom
  B12X sparse MLA/indexer/MoE dataflow cannot win.
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
3. Recheck official FlashInfer / TRTLLM sparse-MLA and public b12x routes after
   dependency updates. FlashInfer `#3395` is still unmerged, but public
   b12x `0.20.0+` now exposes the previously missing DS4 helper APIs. Start
   with direct import/API smokes. Direct public compressed-MLA and
   compressed-indexer routes are currently below the endpoint promotion bar, so
   only revisit them after a dependency/runtime update or a broader dataflow
   change.
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

Latest dev-only C128A active-width result: for a 1M `max_model_len` profile with
an actual 512K prompt, narrowing the returned C128A top-k metadata view to the
current compressed-position width reduced cold TTFT from the no-cap reference
`234.965s` to `221.435s` and improved input throughput from `2231.30` to
`2365.15 tok/s` on dual RTX PRO 6000. This is exact-preserving because the width
is aligned to cover every current token's compressed candidate range. It should
help prompts materially below the configured model-length ceiling, but it cannot
help a true 1M prompt where the effective width equals the full configured
width. The first RTX prefill/decode promotion subset passed with zero
regressions across 59K/124K C=1/C=2, decode concurrency, mixed arrival, and
streaming pressure. Keep it behind the full promotion matrix until short
throughput, prefix/KV lifecycle, GSM8K, and GB10 reduced long-C2 are rechecked.

Latest promoted exact chunked D512 result: for wide indexed D512 sparse-MLA
prefill shapes with `combined_topk > 1152`,
`VLLM_DEEPSEEK_V4_INDEXED_D512_CHUNKED_PREFILL=1` is now the default. It chunks
candidate lists through the existing D512 split primitive and performs exact
online softmax-state merge. On dual RTX PRO 6000, with TP=2, MTP=2, EP enabled,
FP8 KV, prefix cache disabled, `FULL_AND_PIECEWISE`,
`max_model_len=1048576`, and `max_num_batched_tokens=4096`, it improved:

- 512K C=1 cold TTFT from `237.183s` to `147.144s`
  (`-38.0%`), input throughput from `2210.51` to `3563.19 tok/s`.
- 768K C=1 cold TTFT from `490.869s` to `315.884s`
  (`-35.6%`), input throughput from `1602.12` to `2489.65 tok/s`.
- 1.04M C=1 completed at `496.200s` TTFT and `2095.93 tok/s`; same-protocol
  control was not rerun in this pass.

The reduced RTX promotion evidence is encouraging: GSM8K limit-200 passed
with flexible/strict `0.955` / `0.935`, story recall matched all 16 semantic
assignments, prefix-cache stress passed, prefix-disabled KV lifecycle returned
to `0.0%` idle KV after complete and aborted requests, and reduced
59K/124K/mixed-arrival/streaming gates reported zero regressions. A
prefix-cache-enabled lifecycle run failed an absolute `5%` idle-KV threshold
after a prior prefix-stress phase; treat that as a threshold composition issue
for retained prefix-cache blocks, not as a leak signal.

GB10 / SM121 reduced long-C2 passed on an aligned checkout. The first aligned
run explicitly forwarded the chunked D512 env into both vLLM processes, and the
follow-up default-on run confirmed the same route works without setting the env:

- `mtp2`: 4/4 requests, max TTFT `155.023s`, ITL p99 `0.073877s`,
  zero failures, zero preemptions, prefix hits `0`.
- `nomtp`: 4/4 requests, max TTFT `149.993s`, ITL p99 `0.052599s`,
  zero failures, zero preemptions, prefix hits `0`.
- Final default-on rerun after workspace reservation and zero-lens merge
  guard: `mtp2` 4/4 requests, max TTFT `154.555s`, ITL p99 `0.075123s`;
  `nomtp` 4/4 requests, max TTFT `149.155s`, ITL p99 `0.052108s`; zero
  failures, zero preemptions, prefix hits `0`.

This is also materially better than the 2026-06-01 GB10 wrapper reference
(`mtp2` `229.923s` / `0.479s`, `nomtp` `229.434s` / `0.596s`). Continue to keep
GB10 reduced long-C2 in the promotion matrix for future sparse-MLA changes.

Forum #53 GB10 multi-user prefix-cache smoke, 2026-06-07: the reported
multi-user admission/fairness problem is reproducible on the current PR branch.
With TP=2, no-MTP, prefix cache enabled, `max_model_len=262144`,
`max_num_seqs=8`, `max_num_batched_tokens=6144`, and a C=6 streaming-pressure
shape, all six requests completed, but runtime metrics showed
`running_requests_max=1`, `waiting_requests_max=5`, max TTFT `356.230s`, and
ITL p99 `0.052558s`. That points at scheduler/KV admission and long-prefill
queueing rather than decode cadence. The dedicated harness entry is
`scripts/run_gb10_forum53_multi_user_gate.sh`; use it to sweep
`max_num_batched_tokens=2048,3072,4096,6144,8192` and compare C=6/C=8 before
changing vLLM scheduling behavior.

The first C=6 no-MTP sweep completed after rebooting once to clear a driver OOM
log left by an earlier combined sweep attempt. Final clean-boot C=6 data:

| max_num_batched_tokens | Requests | Failures | Max TTFT | ITL p99 | running max | waiting max | KV max |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2048` | `6` | `0` | `370.940s` | `0.052921s` | `1.0` | `5.0` | `8.58%` |
| `3072` | `6` | `0` | `361.843s` | `0.042915s` | `1.0` | `5.0` | `9.99%` |
| `4096` | `6` | `0` | `350.376s` | `0.051967s` | `1.0` | `5.0` | `11.20%` |
| `6144` | `6` | `0` | `356.230s` | `0.052558s` | `1.0` | `5.0` | `14.12%` |
| `8192` | `6` | `0` | `352.118s` | `0.051635s` | `1.0` | `5.0` | `17.18%` |

Lowering `max_num_batched_tokens` did not restore active concurrency. Treat
this as a scheduler/admission or KV-budgeting investigation, not as another
chunk-size tuning problem.

The original one-round forum53 proxy is incomplete for current user behavior:
with prefix cache enabled it only exercises cold first turns. The harness
default now uses two rounds for C=2/C=4, and scheduler experiments that target
multi-agent behavior must compare round-2 TTFT, prefix-cache hit deltas,
running/waiting request counts, and KV usage. For real C=4+ long-agent
sessions, run the same wrapper as a development observation with a larger
`max_model_len` and a C=4 two-round case before claiming improvement; do not
fold that expensive shape into every PR hard gate yet.

For the full forum #53 pressure shape, use the optional profile
`GB10_FORUM53_PROFILE=long_prefix_400k_c6c8`. It configures C=6 and C=8
two-round synthetic 400K-class prefix-cache cases and intentionally remains
outside the normal gate. Because it exceeds the safe context guard for
`max_num_seqs=8`, it still requires an explicit
`GB10_FORUM53_SKIP_CONTEXT_GUARD=1` operator override after a clean reboot.

Scheduler root-cause note: the current long-prefill safety guards were added to
avoid GB10 no-token-progress and decode starvation, but total prompt length is
not a valid work proxy after prefix cache hits are known. A long-context request
with a small cached-tail prefill should not be treated the same as a cold
long-context prefill. Scheduling guards should preserve cold very-long
protection while basing admission and budget pressure on remaining prefill
work.

2026-06-09 RTX reduced validation after making the scheduler guard
prefix-cache-aware:

- `prefix_cache_probe`, TP=2, MTP=2, EP, FP8 KV, prefix cache enabled,
  `max_model_len=131072`, `max_num_seqs=4`, `FULL_AND_PIECEWISE`: startup and
  probe exited `0`; 51K-token session prompts had cold TTFT about `7.6-7.9s`
  and warm-turn TTFT about `0.15-0.34s`; CUDA/NCCL/driver/engine/worker-crash
  counts were `0`.
- `prefix_cache_stress`, same serve profile, one trial with two concurrent
  sessions and three turns: exit `0`, health `200`, solo hit-rate mean
  `59.3%`, concurrent hit-rate mean `84.6%`, runtime
  `running_requests_max=2`, `waiting_requests_max=0`, preemptions `0`, and
  CUDA/NCCL/driver/engine/worker-crash counts `0`.
- A C=4 two-round streaming-pressure smoke also exited `0` with zero request
  failures and ITL p99 `0.020s`, but that harness path recorded zero
  prefix-cache hits. Treat it only as a C=4 pressure smoke, not as evidence for
  prefix-cache-heavy agent reuse.
- 2026-06-09 GB10 forum53 safe-default retry after the C=6/262K
  unsafe-profile capacity incident: artifact
  `artifacts/main/2x_gb10_sm121/20260609_forum53_safe_defaults_after_oom_guard/20260609013550`.
  `mbt=2048` and `4096` both exited `0` with 12/12 requests successful, no
  preemptions, no current-boot NVRM/Xid/UVM/GPU-lost signal, max TTFT
  `136.610s` / `130.811s`, and ITL p99 about `0.051s`. Runtime still showed
  `running_requests_max=1` and `waiting_requests_max=2`, so the safe profile is
  an availability default, not a fairness fix.
- 2026-06-09 GB10 forum53 C=4 two-round scheduler trace after making the
  very-long-prefill guard prefix-cache-aware:
  `artifacts/main/2x_gb10_sm121/20260609_forum53_c4_round2_cached_tail_fix_temp0/20260609032956`.
  Profile: TP=2, no-MTP, EP, prefix cache enabled, `FULL_AND_PIECEWISE`,
  `max_model_len=196608`, `max_num_seqs=4`,
  `max_num_batched_tokens=2048`, `temperature=0`. Result: wrapper exit `0`,
  8/8 requests successful, no current-boot driver errors, no preemptions,
  `running_requests_max=3`, `waiting_requests_max=3`, prefix-cache hit delta
  `2,875,392`, max TTFT `269.494s`, ITL p99 `0.075s`. The first cold round
  remains serialized by design; the second warm round had prefill chunks of
  only `255` tokens and TTFT `1.36-4.14s`, proving cached-tail requests are not
  blocked by the very-long-prefill guard.
- 2026-06-10 GB10 forum53 MTP=2 EP-mode A/B with post-run driver-health hard
  checks:
  EP-off artifact
  `artifacts/main/2x_gb10_sm121/20260610_forum53_mtp2_epoff_candidate_c2c4/20260610024217`;
  EP-on artifact
  `artifacts/main/2x_gb10_sm121/20260610_forum53_mtp2_epon_candidate_c2c4/20260610025323`.
  Profile: TP=2, MTP=2, prefix cache enabled, FP8 KV,
  `FULL_AND_PIECEWISE`, MP executor, `gpu_memory_utilization=0.85`,
  `max_model_len=131072`, `max_num_seqs=4`,
  `max_num_batched_tokens=4096`, C=2 and C=4 two-round cases around `80K`
  prompt tokens. Both runs exited `0`, 12/12 requests completed, preemptions
  were `0`, and driver signal count was `0`. EP-off was only slightly better:
  max TTFT `130.782s` versus EP-on `133.344s`, ITL p99 `0.1716s` versus
  `0.1792s`, waiting max `1` versus `2`. Treat EP-off as a GB10 performance
  candidate with mandatory driver-health and correctness gates, not as a
  default replacement for the conservative EP-on profile yet.
- 2026-06-10 post-rebase user-regression rerun:
  forum53 MTP=2, EP-off, prefix-cache enabled, MP executor,
  `FULL_AND_PIECEWISE`, `max_model_len=196608`, `max_num_seqs=4`,
  `max_num_batched_tokens=4096`, and C=2/C=4 two-round cases completed cleanly
  when the output budget was raised to `max_tokens=256`.
  Artifact:
  `artifacts/main/2x_gb10_sm121/20260610_rebase_user_regression_forum53_mtp2_clean256/20260610_rebase_user_regression_forum53_mtp2_clean256`.
  Result: wrapper exit `0`, 12/12 requests successful, no current-boot driver
  signals, preemptions `0`, max TTFT `127.021s`, ITL p99 `0.1166s`,
  `running_requests_max=2`, `waiting_requests_max=1`, and prefix-cache hit
  delta `2,715,648`. The same shape with `max_tokens=128` can fail the
  semantic sentinel check by truncating before the required marker, so treat
  the 128-token result as a gate false-negative risk rather than a runtime
  regression.
- 2026-06-12 final PR-head GB10 forum53 refresh:
  artifact
  `artifacts/codex_pr_stable_preview_f32247a/2x_gb10_sm121/gb10_forum53_mtp2_epoff_c2_gmem0685_mml81920/20260612074113`.
  Profile: MP/EP-off, MTP=2, prefix cache enabled, FP8 KV,
  `FULL_AND_PIECEWISE`, `max_model_len=81920`, `max_num_seqs=2`,
  `max_num_batched_tokens=4096`, and `gpu_memory_utilization=0.685`.
  Result: wrapper `ok=true`, serve exit `0`, matrix exit `0`, 4/4 requests,
  no preemptions, no current-boot driver signals, max TTFT `124.045698s`, ITL
  p99 `0.144954s`, GPU KV usage avg/max `65.81% / 86.40%`, and prefix hits
  `79,872`.
  Same-boot higher-memory probes are not clean evidence: `196608` and `131072`
  produced driver-health failures, while `98304` at lower memory utilization did
  not start cleanly. Treat those artifacts as capacity-probe failures unless
  they are rerun cleanly after a fresh reboot.
- 2026-06-10 post-rebase GB10 MTP=2 C=8 reduced soak:
  artifact
  `artifacts/main/2x_gb10_sm121/20260610_rebase_user_regression_gb10_mtp2_moe_c8_reduced/20260610_rebase_user_regression_gb10_mtp2_moe_c8_reduced`.
  Profile: TP=2, MTP=2, prefix cache enabled, EP-off, MP executor,
  `FULL_AND_PIECEWISE`, `gpu_memory_utilization=0.80`,
  `max_model_len=200000`, `max_num_seqs=8`,
  `max_num_batched_tokens=4096`, C=8, 8 rounds, 40K-token prompts. Result:
  no no-token-progress watchdog hit, decode tokens advanced throughout, p99
  inter-chunk `0.1545s`, preemptions `0`, `running_requests_max=7`, but the
  wrapper exit was `1` because 16/64 requests failed the output-content check
  at `max_tokens=128` and the worker logged one current-boot
  `NV_ERR_NO_MEMORY`. Treat this as evidence that C=8/MTP2 is not a clean GB10
  recommendation yet; it is a diagnostic pressure shape, not a production
  default.

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
A scratch no-store MQA logits probe also limits this route: keeping the same
QK/ReLU/weighted score work but replacing the full logits store with per-tile
checksums was only about `0.8%` faster at 32K KV and `2.3%` faster at 131K KV
on the endpoint-like 256-query, 32-head, topk-512 shape. Avoiding the logits
matrix write/read is not enough by itself. A useful fused MQA producer must
reduce real score work, candidate/value visits, live state, or dependency
depth, not merely move the same score work into a different output format.
The first real-model weight-sign diagnostic also rules out a tempting exact
pruning shortcut: C4A MQA scores accumulate `ReLU(q*k)*weight_h`, and
`weight_h` is an unconstrained linear projection output folded with q-scale and
softmax/head scales. A 4K RTX attribution smoke found about `44.1%` negative
MQA top-k weights, so head-wise early-stop or monotonic upper-bound pruning
that assumes non-negative weights is not correctness-safe.
A follow-up positive-score upper-bound diagnostic tested the safer signed
variant: first compute positive-weight heads for all candidates, then use the
positive score as an upper bound before evaluating negative heads. Under a
tie-safe exact top-k rule, 4K retained every sampled candidate and 32K retained
nearly every sampled candidate; the optimistic work ratio was about `0.997x`
at 32K before counting the extra pass overhead. Do not pursue this pruning
route as a production kernel.
A scratch head-split MQA logits probe also failed to justify endpoint work:
splitting 64 heads into multiple launches preserved exact logits but made the
32K/131K KV microbench slower even at the coarsest two-launch split. Extra
logits read/write traffic and launch overhead outweighed any live-state relief.

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
