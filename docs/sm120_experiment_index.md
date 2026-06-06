# SM120 Experiment Index

Use this index to find the relevant historical evidence in
`docs/sm120_optimization_notes.md` without rereading the whole archive. Start
with `docs/sm120_current_state.md` for the live decision state.

## Current Checkpoints

- Current state and next direction:
  `docs/sm120_current_state.md`.
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

- Official b12x compressed MLA endpoint route:
  open `docs/sm120_optimization_notes.md` and search
  `Official FlashInfer 0.6.12 DS4 sparse-MLA API recheck`.
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
- GB10 current-default versus Reddit-style prefill matrix:
  open `docs/sm120_optimization_notes.md` and search
  `GB10 current-default versus Reddit-style long matrix`.
- Upstream `FLASHINFER_MLA_SPARSE_DSV4` endpoint/API startup probe:
  open `docs/sm120_optimization_notes.md` and search
  `Upstream FlashInfer MLA sparse DSV4 endpoint probe`.
- vLLM PR #43477 8K/1K comparison shape:
  open `docs/vllm_correctness_gates.md` and search
  `FlashInfer sparse-MLA comparison tracking`.
- NVIDIA Developer Forums GB10 recipe tracking:
  open `docs/vllm_correctness_gates.md` and search
  `NVIDIA Developer Forums thread`.

## Correctness

- GSM8K gate and score floors:
  `docs/vllm_correctness_gates.md`.
- Story recall and semantic long-context gates:
  `docs/vllm_correctness_gates.md`.
- FULL_AND_PIECEWISE CUDA graph rule:
  `docs/vllm_correctness_gates.md` and `docs/sm120_current_state.md`.
