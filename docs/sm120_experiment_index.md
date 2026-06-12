# SM120 Experiment Index

Use this index to find the relevant pre-framework historical evidence in
`docs/sm120_optimization_notes.md` without rereading the whole archive. Start
with `docs/sm120_current_state.md` for the live decision state.

For new work from 2026-06-12 onward, use `docs/sm120/README.md` and
`docs/sm120/index.md`. New experiments should live under
`docs/sm120/experiments/`, and durable conclusions should live under
`docs/sm120/decisions/`.

## Current Checkpoints

- Current state and next direction:
  `docs/sm120_current_state.md`.
- Active fork-independent sparse-MLA rewrite task:
  `docs/sm12x_triton_sparse_mla_rewrite_plan.md`.
- Upstream DeepSeek backlog watchlist:
  open `docs/sm120_optimization_notes.md` and search
  `Upstream DeepSeek backlog triage`.
- Promotion and research checkpoint: open
  `docs/sm120_optimization_notes.md` and search
  `Promotion/research checkpoint, 2026-06-05`.
- Rebase after upstream DeepSeek V4 attention refactor:
  open `docs/sm120_optimization_notes.md` and search
  `Rebase after upstream DeepSeek V4 attention refactor`.
- Direction reset after b12x and D512 decomposition:
  open `docs/sm120_optimization_notes.md` and search
  `Direction reset after the b12x and D512 decomposition rechecks`.
- Public b12x 0.20 dependency/API and microbench recheck:
  open `docs/sm120_optimization_notes.md` and search
  `Public b12x recheck, 2026-06-08`.
- B12X package/API versus vLLM runtime-path probe:
  open `docs/sm120_optimization_notes.md` and search
  `B12X runtime-path probe, 2026-06-08`.
- FlashInfer SM120 packed sparse-MLA prefill prototype:
  open `docs/sm120_optimization_notes.md` and search
  `FlashInfer packed sparse-MLA prefill prototype`.

## Promotion Gates

- Full correctness and performance gates:
  `docs/vllm_correctness_gates.md`.
- Prefill/decode promotion gate:
  open `docs/vllm_correctness_gates.md` and search
  `Prefill/decode promotion gate`.
- Sparse-MLA raw-prefill candidate rule:
  open `docs/vllm_correctness_gates.md` and search
  `Sparse-MLA raw-prefill candidate rule`.
- User-reported / external workload gates:
  open `docs/vllm_correctness_gates.md` and search
  `User-Reported External Gates`.
- GB10 reduced long-C2 gate:
  open `docs/dgx_spark_bare_metal_cluster.md` and search
  `GB10_LONG_C2_VARIANTS`.
- 512K / 768K / 1M context frontier gate:
  open `docs/sm120_current_state.md` and search
  `512K / 768K / 1M context frontier baseline`; for GB10 setup details, open
  `docs/dgx_spark_bare_metal_cluster.md` and search
  `512K / 768K / 1M frontier work`. For the first measured baseline, open
  `docs/sm120_optimization_notes.md` and search
  `First baseline artifacts`.
- 512K-to-1M TTFT Nsys attribution:
  open `docs/sm120_optimization_notes.md` and search
  `512K / 1M very-long TTFT Nsys attribution`.

## Prefill And Sparse MLA

- Successful D512 sparse-MLA prefill retune:
  open `docs/sm120_optimization_notes.md` and search
  `Narrow D512 split tile retune candidate`.
- Post-rebase default-D512 raw-prefill attribution:
  open `docs/sm120_optimization_notes.md` and search
  `Post-rebase default-D512 raw-prefill attribution`.
- D512 empty-tail block skip experiment:
  open `docs/sm120_optimization_notes.md` and search
  `D512 empty-tail block skip experiment`.
- RTX / GB10 region-split attribution:
  open `docs/sm120_optimization_notes.md` and search
  `RTX/GB10 region-split attribution follow-up`.
- GB10 reduced sparse-efficiency follow-up:
  open `docs/sm120_optimization_notes.md` and search
  `GB10 reduced sparse-efficiency follow-up`.
- D512 component decomposition:
  open `docs/sm120_optimization_notes.md` and search
  `D512 component-decomposition recheck`.
- Mixed C128/SWA D512 NCU follow-up:
  open `docs/sm120_optimization_notes.md` and search
  `Mixed C128/SWA D512 NCU follow-up`.
- D512 candidate-scaling and RTX NCU follow-up:
  open `docs/sm120_optimization_notes.md` and search
  `D512 candidate-scaling and RTX NCU follow-up`.
- GB10 D512 score/value NCU after counter unlock:
  open `docs/sm120_optimization_notes.md` and search
  `GB10 sparse-MLA candidate/value work recheck after counter unlock`.
- Current C128A shape correction:
  open `docs/sm120_optimization_notes.md` and search
  `Current-shape correction after re-reading the latest sparse-MLA stats`.
- Rejected current-shape grouped-compressed microbench:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected current-shape grouped-compressed microbench`.
- Current-shape C128A D512 NCU:
  open `docs/sm120_optimization_notes.md` and search
  `Current-shape C128A D512 NCU`.
- Rejected fused / lower-live-state D512 microbench:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected fused / lower-live-state D512 microbench`.
- Cross-query KV reuse observation:
  open `docs/sm120_optimization_notes.md` and search
  `Cross-query KV reuse observation infrastructure`.
- C128A active-width metadata narrowing:
  open `docs/sm120_optimization_notes.md` and search
  `C128A active-width metadata narrowing`.
- Exact chunked D512 online merge:
  open `docs/sm120_optimization_notes.md` and search
  `Exact chunked D512 online-merge prototype`.
- Forum #53 GB10 multi-user prefix-cache gate:
  open `docs/sm120_current_state.md` and search
  `Forum #53 GB10 multi-user prefix-cache smoke`.
- Rejected grouped-combined C128A reuse microbench:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected grouped-combined C128A reuse microbench`.
- Rejected single-launch grouped full-score probe:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected single-launch grouped full-score probe`.
- Rejected two-pass grouped-union replay probe:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected two-pass grouped-union replay probe`.
- Candidate row duplicate diagnostic:
  open `docs/sm120_optimization_notes.md` and search
  `Candidate row duplicate diagnostic`.
- MQA valid-span clipping rejection:
  open `docs/sm120_optimization_notes.md` and search
  `MQA valid-span accounting follow-up`.
- vLLM top-k selector audit:
  open `docs/sm120_optimization_notes.md` and search
  `Existing vLLM top-k primitives audit`.
- MQA weight-sign diagnostic / pruning boundary:
  open `docs/sm120_optimization_notes.md` and search
  `MQA weight-sign diagnostic and pruning boundary`.
- Rejected positive-score MQA pruning bound:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected positive-score MQA pruning bound`.
- Rejected MQA head-split lower-live-state probe:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected MQA head-split lower-live-state probe`.

## Rejected Or Blocked Prefill Routes

These entries are specific to the tested route shape. They should not be read
as a blanket rejection of local-inference-lab's newer B12X backend stack; for
that thread, search `External unholy-fusion feedback refresh`.

- Official b12x compressed MLA endpoint route:
  open `docs/sm120_optimization_notes.md` and search
  `Official FlashInfer 0.6.12 DS4 sparse-MLA API recheck`.
- Direct-view FlashInfer packed sparse-MLA adapter:
  open `docs/sm120_optimization_notes.md` and search
  `FlashInfer packed sparse-MLA layout contract`.
- leavelet DeepGEMM SM120 MQA route:
  open `docs/sm120_optimization_notes.md` and search
  `leavelet DeepGEMM SM120 MQA route recheck`.
- Standalone C128 grouped-compressed route:
  open `docs/sm120_optimization_notes.md` and search
  `Standalone C128 grouped-compressed prefill should not be promoted`.
- BF16 D512 score workspace:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected BF16 D512 score-workspace route`.
- SWA-only D512 selector:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected SWA-only D512 selector route`.
- Grouped-query local-SWA tiled route:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected grouped-query local-SWA tiled route`.
- Grouped-SWA-final D512 endpoint route:
  open `docs/sm120_optimization_notes.md` and search
  `Current-shape correction and final rejection`.
- SWA range candidate / gather-only style routes:
  open `docs/sm120_optimization_notes.md` and search
  `range-SWA D512 microbench candidate`.
- D512 head-block and split score/value tile retune rejects:
  open `docs/sm120_optimization_notes.md` and search
  `value-traffic route, 2026-06-04` or
  `Rejected D512 split score/value tile retune sweep`.
- D512 fused stats+value / lower-live-state reject:
  open `docs/sm120_optimization_notes.md` and search
  `Rejected fused / lower-live-state D512 microbench`.

## Scheduler, Fairness, And Interference

- Prefill/decode gate requirements:
  open `docs/vllm_correctness_gates.md` and search
  `Prefill/decode promotion gate`.
- Mixed-arrival Nsys trace guidance:
  open `docs/vllm_correctness_gates.md` and search
  `Mixed-arrival Nsight Systems trace`.
- GB10 long C=2 pressure stall reproduction:
  open `docs/sm120_optimization_notes.md` and search
  `GB10 Long C=2 Pressure Stall Reproduction`.
- Multi-prefill partial-state rejected route:
  open `docs/sm120_optimization_notes.md` and search
  `Extend partial-state sparse MLA prefill`.

## Prefix Cache, KV Lifecycle, And Workspace

- KV lifecycle and prefix-cache recoverability gates:
  open `docs/vllm_correctness_gates.md` and search
  `KV lifecycle and prefix-cache recoverability`.
- Upstream DBO / prefix-cache / KV-layout watchlist:
  open `docs/sm120_optimization_notes.md` and search
  `Upstream DeepSeek backlog triage`.
- Workspace high-concurrency gate:
  open `docs/vllm_correctness_gates.md` and search
  `workspace high-concurrency stress`.
- Runtime-M TF32 MHC prenorm GEMM stability fix:
  open `docs/sm120_optimization_notes.md` and search
  `Runtime-M TF32 MHC Prenorm GEMM`.
- Prefix-cache user-feedback shapes:
  open `docs/vllm_correctness_gates.md` and search
  `prefix-cache`.
- GB10 C=1 MTP short-decode slow/fast user report:
  open `docs/dgx_spark_bare_metal_cluster.md` and search
  `GB10 C=1 MTP Decode Throughput Probe`.

## GB10 / SM121 Environment

- GB10 setup, package overrides, NCCL, FlashInfer JIT cache, and b12x notes:
  `docs/dgx_spark_bare_metal_cluster.md`.
- GB10 conservative long-context profile:
  open `docs/dgx_spark_bare_metal_cluster.md` and search
  `For 100K-class or larger long-prefill validation`.
- Docker caveats:
  open `docs/dgx_spark_bare_metal_cluster.md` and search
  `Docker adds another capacity variable`.
- GB10 startup/crash proxy gates:
  open `docs/vllm_correctness_gates.md` and search
  `GB10 startup/crash proxy`.

## External Comparisons

- GB10 Reddit / unholy-fusion performance comparison:
  `docs/sm120_current_state.md`.
- Aiden/unholy runtime path comparison:
  open `docs/sm120_optimization_notes.md` and search
  `B12X runtime-path probe, 2026-06-08`.
- NVIDIA forum #59 / local-inference-lab latest B12X feedback:
  open `docs/sm120_optimization_notes.md` and search
  `External unholy-fusion feedback refresh`.
- GB10 current-default versus Reddit-style prefill matrix:
  open `docs/sm120_optimization_notes.md` and search
  `GB10 current-default versus Reddit-style long matrix`.
- Upstream `FLASHINFER_MLA_SPARSE_DSV4` endpoint/API startup probe:
  open `docs/sm120_optimization_notes.md` and search
  `Upstream FlashInfer MLA sparse DSV4 endpoint probe`.
- FlashInfer packed SM120 sparse-MLA route split:
  open `docs/sm120_optimization_notes.md` and search
  `FlashInfer packed SM120 sparse-MLA route split`. Current conclusion: the
  official `flashinfer.mla` DSV4 route is the plain-KV path, while the unmerged
  `flashinfer.sparse_mla_sm120` packed `584B/token` path is not present in the
  current wheel. A copied GB10 route venv with the unmerged backend now passes
  direct packed DSV4 prefill/decode smokes. Current vLLM cache shapes appear
  compatible in principle (`SWA=64`, `C4A=64`, `C128A=2`); the earlier
  `SWA=256` note confused global scheduler/cache preference with the physical
  page size passed to the wrapper. The development probe
  `scripts/run_flashinfer_packed_mla_probe.sh` now validates vLLM helper output
  split into packed-wrapper C4A and C128A index streams on GB10. It is still
  not a direct vLLM endpoint backend until workspace reservation, CUDA graph
  capture, and endpoint performance are adapter-tested; search
  `FlashInfer packed SM120 component smoke`,
  `FlashInfer packed SM120 vLLM-layout constraint`, and
  `FlashInfer packed SM120 vLLM-shaped component probe` before adapter work.
- Aiden wheelhouse FlashInfer SM120 sparse-MLA wrapper:
  open `docs/sm120_optimization_notes.md` and search
  `Aiden wheelhouse FlashInfer sparse-MLA wrapper probe`. Current conclusion:
  the public Aiden image's wheelhouse contains patched FlashInfer wheels that
  expose `BatchSparseMLAPagedAttentionWrapper`; installing only the cubin wheel
  over the official Python package does not. The wrapper passed small GB10
  single-cache and dual-cache DSV4 prefill component smokes, plus the
  vLLM-shaped C4A/C128A split-index probe. This is now the highest-signal
  adapter route, but it still needs endpoint workspace/CUDA-graph integration
  and endpoint A/B before promotion.
- vLLM PR #43477 8K/1K comparison shape:
  open `docs/vllm_correctness_gates.md` and search
  `FlashInfer sparse-MLA comparison tracking`.
- NVIDIA Developer Forums GB10 recipe tracking:
  open `docs/vllm_correctness_gates.md` and search
  `NVIDIA Developer Forums thread`.
- Aiden image recipe and parity harness:
  open `docs/dgx_spark_bare_metal_cluster.md` and search
  `Aiden Image Parity`; for the latest diagnostic notes, open
  `docs/sm120_optimization_notes.md` and search
  `Aiden Image Parity Recheck`, `Current-Dev EP-off A/B`,
  `Sparse-indexer-only A/B`, or
  `Public image control-plane correction`.
- RTX EP-off prefill attribution:
  open `docs/sm120_optimization_notes.md` and search
  `RTX EP-off prefill attribution, 2026-06-10`. Current conclusion: EP-off is
  not a universal raw-prefill multiplier on dual RTX PRO 6000, but it materially
  improved the 124K C=2 pure-prefill shape (`1.29x` input tok/s, `0.77x` mean
  TTFT) while short inputs moved only `1-4%`. The same section also records a
  same-protocol RTX prefill/decode promotion smoke: EP-off passed and was often
  slightly better for long/streaming TTFT, but EP-on still won a few cadence /
  fairness metrics, so EP mode remains a benchmark dimension rather than a
  default recommendation.
- B12X optional stack capability probe:
  `scripts/run_b12x_stack_probe.sh`; open `docs/sm120_optimization_notes.md`
  and search `B12X stack capability probe and route split` plus
  `Public b12x recheck, 2026-06-08`. Public `b12x==0.20.0` now exposes the
  DS4 compressed MLA / compressed-indexer / native FP4 MoE helper APIs that
  were missing from the older `0.15.2` notes. Endpoint validation is route
  dependent: mHC is slower than current TileLang, WO is blocked on public
  CUTLASS DSL MXFP8 MMA support, public B12X FP8 block-linear is blocked on the
  same missing `MmaMXF8Op` symbol even with `b12x==0.20.0`, and
  sparse-indexer prefill is blocked by a TMA-partition failure in direct GB10
  `extend_tiled_topk` smoke. The same probe now reports whether the current
  environment has the plain FlashInfer DSV4 TRTLLM-gen route versus the
  unmerged packed SM120 sparse-MLA route.
- FlashInfer #3489 MXFP8 GEMM check:
  open `docs/sm120_optimization_notes.md` and search
  `FlashInfer #3489 MXFP8 check`. Current conclusion: the local FlashInfer fork
  includes #3489, but the installed GB10 wheel still does not unblock WO/MXFP8:
  `mm_mxfp8` `auto/cutlass` fails the SM120 mat2 layout check and explicit
  `cudnn` is not supported for capability 121.
- Public b12x 0.20 KV-layout compatibility:
  open `docs/sm120_optimization_notes.md` and search
  `Public b12x 0.20 KV-layout probe`. Current conclusion: the old
  token-interleaved incompatibility reading was too strong. vLLM exposes a 3D
  logical cache tensor, but its physical CUDA page layout can match public
  b12x through a zero-copy 2D page-byte view. The follow-up component smoke
  passed, but endpoint-like microbenching kept direct public-b12x compressed
  MLA below the current D512 split+finish baseline.
- Public b12x compressed-indexer recheck:
  open `docs/sm120_optimization_notes.md` and search
  `Public b12x compressed-indexer route recheck`. Current conclusion: public
  b12x `index_topk_fp8` is runnable and correct on shared-prefill shapes, but
  is about `3.4-3.8x` slower than the current SM12x top-k path; the gather copy
  it could avoid is only `0.013 ms` at 32K tokens and `0.135 ms` at 131K tokens
  on GB10. Do not port this direct substitution into vLLM unless a future
  dependency changes the component timing.
- local-inference B12X stack replay:
  open `docs/sm120_optimization_notes.md` and search
  `local-inference B12X stack replay blocker`. Current conclusion: replaying
  the local-inference B12X vLLM route is blocked with public dependencies.
  B12X WO projection expects a CUTLASS DSL `MmaMXF8Op` symbol absent from
  `nvidia-cutlass-dsl==4.5.2`; disabling WO projection falls back to DeepGEMM
  O-proj, whose current `fp8_einsum` API rejects the DS4 O-proj layout even in
  an eager microprobe. Do not copy this integration into Dev as-is.
- Public B12X / FlashInfer dense recheck:
  open `docs/sm120_optimization_notes.md` and search
  `public B12X / FlashInfer dense component recheck`. Current conclusion:
  public B12X MXFP8 dense and WO projection both remain blocked by the missing
  CUTLASS DSL `MmaMXF8Op` symbol. Public FlashInfer `mm_mxfp8` is runnable but
  is not faster than `gemm_fp8_nt_groupwise` for DS4-like `K=7168,N=1536`
  dense shapes, and it does not consume the native DS4 128x128 FP8 block-scale
  checkpoint format. The ignored FlashInfer checkout is the writable dependency
  source for future FI-side experiments; upstream #3489 is MXFP8 GEMM
  background, not a sparse-MLA prefill backend. Do not make dense/MoE
  replacement the next main route.
- FlashInfer packed SM120 layout contract:
  open `docs/sm120_optimization_notes.md` and search
  `FlashInfer packed SM120 layout contract recheck`. Current conclusion:
  PR3395's packed wrapper accepts vLLM-compatible packed KV cache strides, but
  still requires contiguous q/output and dense row-major main/extra indices.
  Do not retry a direct-view adapter; either add stride support in FlashInfer or
  keep graph-safe vLLM-side staging and measure its endpoint cost.
- FlashInfer packed SM120 endpoint promotion subset:
  open `docs/sm120_optimization_notes.md` and search
  `FlashInfer packed SM120 endpoint promotion subset`. Current conclusion:
  the archived `VLLM_DEEPSEEK_V4_FLASHINFER_PACKED_PREFILL=1` endpoint adapter
  passed GB10 prefill attribution with prefix cache disabled/enabled, reduced
  long-C2, and reduced MTP=2 MoE TP soak. It improved GB10 C=1 prefill by about
  `10-23%` TTFT versus the same-day env-off control and moved sparse work to
  `flashinfer_packed_attention`, but remains a reference-only route pending
  an official dependency path or a fork-independent Triton rewrite.
- GB10 EP-mode safety recheck:
  open `docs/sm120_optimization_notes.md` and search
  `GB10 backend/EP baseline smoke after forum53 follow-up`. Current conclusion:
  MP with expert parallel disabled is the GB10 recommendation. Keep EP as an
  environment-controlled fallback A/B dimension, and keep post-run driver
  health as part of every GB10 pressure gate.
- GB10 post-rebase user-regression rerun:
  open `docs/sm120_optimization_notes.md` and search
  `Post-rebase user-regression rerun, 2026-06-10`. Current conclusion: the
  earlier forum53 C=2/C=4 MTP=2 EP-off profile was clean with
  `max_tokens=256`, but the 2026-06-12 PR-head refresh narrowed the review-safe
  forum53 gate to C=2, `max_num_seqs=2`, `max_model_len=81920`, and
  `gpu_memory_utilization=0.685` for MTP=2. C=4 and larger C=2 context settings
  remain explicit pressure profiles until they are clean across fresh boots. The
  C=8/MTP=2 reduced soak shows no no-token-progress but still logs a worker
  `NV_ERR_NO_MEMORY`; keep C=8 as diagnostic pressure only.

## Correctness

- GSM8K gate and score floors:
  `docs/vllm_correctness_gates.md`.
- Story recall and semantic long-context gates:
  `docs/vllm_correctness_gates.md`.
- FULL_AND_PIECEWISE CUDA graph rule:
  `docs/vllm_correctness_gates.md` and `docs/sm120_current_state.md`.
