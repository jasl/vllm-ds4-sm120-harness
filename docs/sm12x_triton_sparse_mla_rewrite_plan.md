# SM12x Triton Sparse-MLA Rewrite Task

> **For agentic workers:** this is the active task entrypoint for the next
> fork-independent sparse-MLA prefill optimization. Read
> `docs/sm120_current_state.md` first, then this file, then use
> `docs/sm120_experiment_index.md` only to jump into older evidence.

**Goal:** build a maintainable Triton sparse-MLA prefill backend for DeepSeek
V4 SM12x that captures the dataflow advantage observed in the unmerged packed
FlashInfer SM120 backend without depending on that fork.

**Primary target:** lower sparse-MLA prefill cost per effective candidate visit
for DS4 mixed compressed-plus-SWA metadata. The first implementation target is
same semantic candidate work with lower per-visit cost. Candidate reduction is
a later step unless a prototype proves it without correctness risk.

**Non-goals:**

- Do not default-enable or PR-promote the unmerged FlashInfer packed backend.
- Do not add another long-lived user-facing tuning switch.
- Do not restart generic chunk-size, head-block, launch-count, or scheduler
  sweeps that keep the same memory traffic and dependency depth.
- Do not use prefix-cache hits as evidence for cold-prefill gains.
- Do not disable `FULL_AND_PIECEWISE` CUDA graphs to make a route pass.

## Why This Exists

The current promoted D512 sparse-MLA path is the best defensible PR baseline,
but it does not close the GB10 raw-prefill gap. The dev-only packed FlashInfer
prototype is the first endpoint-shaped route that improves GB10 prefill at
4K, 8K, 32K, and 128K with prefix cache both disabled and enabled. That route
still depends on an unmerged backend, so it should be treated as a performance
reference, not as the production dependency.

The key lesson is dataflow, not the dependency:

- Split the DS4 prefill metadata into physically meaningful streams:
  main/SWA and extra/compressed.
- Consume the packed DS4 KV page layout directly when possible.
- Keep score, online softmax state, and value accumulation close together.
- Avoid materializing large score or value workspaces unless they are reused
  enough to pay for the traffic.
- Preserve graph-stable workspace allocation and fail closed when a shape does
  not match the backend contract.

## Evidence Index

Use these current evidence anchors before writing code:

- `docs/sm120_current_state.md`
  - `Current Posture`
  - `Current Performance Snapshot`
  - `Persistent TODO`
- `docs/sm120_experiment_index.md`
  - `FlashInfer packed SM120 endpoint promotion subset`
  - `Rejected fused / lower-live-state D512 microbench`
  - `Current-shape C128A D512 NCU`
  - `Public b12x 0.20 KV-layout compatibility`
- `docs/vllm_correctness_gates.md`
  - `Sparse-MLA raw-prefill candidate rule`
  - `Prefill/decode promotion gate`
- `docs/dgx_spark_bare_metal_cluster.md`
  - GB10 dependency, driver-health, and optional-kernel notes.

## Current Source Map

Current vLLM worktree state to audit before implementation:

- `vllm/envs.py`
  - Current dev and PR branches should not contain the archived FlashInfer
    packed prefill env gate. Remove or keep only gates with an active
    experiment owner and matching notes.
- `vllm/models/deepseek_v4/nvidia/flashmla.py`
  - Current D512 path, exact chunked D512 merge, and sparse attribution live
    here today. The FlashInfer packed endpoint adapter is a reference-only
    archived branch unless it is explicitly restored for comparison.
- `vllm/models/deepseek_v4/common/ops/cache_utils.py`
  - Builds mixed sparse indices and is the current shared bridge between vLLM
    metadata and external packed-backend probes.
- `tests/model_executor/test_deepseek_v4_flashinfer_packed_prefill.py`
  - Development-only coverage for the packed FlashInfer adapter. It belongs
    with the archived reference branch unless the dependency route is restored
    for comparison; do not move it to the PR branch unless that route is
    promoted.

The next Triton backend should either be placed behind an internal developer
gate in the existing sparse-MLA module or be split into a small dedicated
helper module if that reduces `flashmla.py` size. Do not leave both a stale
FlashInfer packed route and a new Triton rewrite active by default.

## Design Target

### Dataflow Contract

The first Triton prototype should satisfy this contract:

- Input metadata is DS4 mixed sparse prefill metadata after vLLM's existing
  top-k/index construction.
- Main/SWA stream and extra/compressed stream are explicit. Do not flatten them
  into one generic path unless the generated kernel still preserves stream-
  specific page addressing and value accumulation.
- Output must be numerically equivalent to the existing exact D512 path under
  the same candidate set.
- The route must use preallocated workspace and must not allocate after CUDA
  graph workspace lock.
- The route must emit sparse attribution counters compatible with the current
  harness summaries: stage name, effective candidate visits, elapsed time, and
  prefix-cache mode.

### First Performance Target

The first retained prototype must improve at least one endpoint-shaped
prefill class while not regressing the rest:

| Class | Purpose | Minimum useful signal |
| --- | --- | --- |
| 4K / 8K C=1 | Short and mid prompt fixed overhead plus SWA tail | Better TTFT or input tok/s without worse decode or correctness |
| 32K / 64K C=1 | Mixed fixed overhead and sparse-value pressure | Better input tok/s and sparse ms per effective visit |
| 124K / 128K C=1 | Current local long-context ceiling | Better TTFT and no driver/runtime warnings |
| 59K / 124K C=2 | Fairness regression guard | No worse decode min/max or ITL p99 |
| GB10 reduced long-C2 | Availability and cadence guard | Same pass/fail result and clean driver health |

For a first component microbench, a `5%` win is only a triage signal. Endpoint
promotion should aim for a clear same-host improvement, preferably at least
`8-10%` TTFT or input tok/s on one target class with no measured regressions.

## 2026-06-08 Checkpoint: D512 Fused Sink Finish

Status: active dev candidate, default off behind
`VLLM_DEEPSEEK_V4_INDEXED_D512_FUSED_SINK_PREFILL=0`.

This candidate does not reduce sparse candidate visits and does not change the
score/stats dataflow. It fuses the current D512 split value stage with sink
finish so the D512 split route can write normalized output directly and skip
one `acc` workspace read/write plus the separate finish launch.

Measured component signal:

| Host | Candidates | Split+finish | Fused sink | Speedup | Max diff |
| --- | ---: | ---: | ---: | ---: | ---: |
| RTX PRO 6000 x2 | 640 | 1.102 ms | 0.953 ms | 1.157x | 0 |
| RTX PRO 6000 x2 | 1152 | 1.878 ms | 1.737 ms | 1.082x | 0 |
| GB10 node 1 | 640 | 9.653 ms | 8.441 ms | 1.144x | 0 |
| GB10 node 1 | 1152 | 16.095 ms | 14.889 ms | 1.081x | 0 |
| GB10 node 2 | 640 | 9.684 ms | 8.458 ms | 1.145x | 0 |
| GB10 node 2 | 1152 | 16.095 ms | 14.958 ms | 1.076x | 0 |

Measured RTX endpoint smoke with TP=2, MTP=2, EP enabled, FP8 KV, prefix cache
disabled, `FULL_AND_PIECEWISE`, `max_num_batched_tokens=4096`, C=1, two random
requests per input length:

| Shape | Old TTFT | Fused TTFT | TTFT delta | Old input tok/s | Fused input tok/s | Throughput delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 65K / O=1 | 9.786 s | 9.694 s | -0.94% | 6697.6 | 6759.8 | +0.93% |
| 124K / O=1 | 19.451 s | 18.810 s | -3.30% | 6375.3 | 6592.2 | +3.40% |

Interpretation: this is worth keeping on the dev branch and promoting through
the matrix because it is exact, graph-compatible, and wins on both RTX and
GB10 component shapes. It is not enough to close the raw prefill gap. The main
route remains reducing true sparse MLA candidate/value work and memory
pressure, especially the SWA tail/value traffic.

## 2026-06-08 Checkpoint: Cross-Query Reuse Attribution

Artifact label:
`artifacts/main/2x_nvidia_rtx_pro_6000_blackwell_workstation_edition/20260608_reuse_attribution_smoke/20260608210317`.

This was a diagnostic attribution smoke, not a customer-facing latency
baseline. It used current default behavior, prefix cache disabled, MTP=2, EP
enabled, FP8 KV, `FULL_AND_PIECEWISE`, overlap sampling enabled, stage timing
enabled, C=1, and one request per input length.

| Input | Sparse stage total | Sparse visits/s | Compressed effective visits | SWA effective visits | Compressed group16 reuse | SWA group16 reuse |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4K | 563.596 ms | 203.119M/s | 68.580M | 45.422M | 0.919 | 0.923 |
| 32K | 2877.888 ms | 426.360M/s | 849.729M | 368.383M | 0.855 | 0.930 |

Interpretation:

- Cross-query reuse exists at short and mid prompts, not only at very long
  contexts.
- SWA is smaller than compressed work in these shapes, but it still accounts
  for about `30-40%` of effective visits and has high sampled reuse.
- A compressed-only grouped path repeats the already rejected failure mode:
  it leaves enough SWA/value traffic that endpoint gains are small or erased.
- The next retained prototype must preserve the current D512 head-block score
  reuse while reducing candidate/value work across both compressed and SWA
  streams. Score-only grouped reuse, split-launch grouped-combined reuse, and
  two-pass grouped-union replay remain rejected routes.

## 2026-06-08 Checkpoint: Grouped Stream Online Component

Status: active component prototype, not wired to vLLM endpoint.

This prototype tests a single grouped-query online attention kernel for the
`c128a-current` component shape. It processes compressed and SWA streams through
a shared per-group union and does not materialize a score workspace. Unlike the
earlier rejected compressed-only and score-only grouped probes, this one
reduces score/value work for both streams in the same kernel. The current
prototype intentionally uses one head per program with a full D512 accumulator,
so it still needs endpoint-oriented engineering before it can replace the
current D512 path.

Component results with `512` query tokens, `64` heads, D=`512`,
`128` compressed candidates, `group_size=32`, and grouped block-C=`32`:

| Host | Candidates | Current split | Grouped stream online | Speedup | Max diff |
| --- | ---: | ---: | ---: | ---: | ---: |
| RTX PRO 6000 x2 | 640 | 0.555 ms | 0.353 ms | 1.572x | 0.001577 |
| RTX PRO 6000 x2 | 1152 | 1.057 ms | 0.591 ms | 1.788x | 0.001028 |
| GB10 node 1 | 640 | 4.373 ms | 1.484 ms | 2.948x | 0.001377 |
| GB10 node 1 | 1152 | 7.405 ms | 2.353 ms | 3.147x | 0.001030 |

Rejected boundary from the same component family: group32/block-C64 exceeds
SM12x shared-memory limits (`106496` bytes required versus a `101376` byte
limit). Group16/block-C64 works and is positive, but slower than
group32/block-C32 on the target shape.

Interpretation:

- This is the first fork-independent Triton component direction in this cycle
  that wins strongly on both RTX PRO 6000 / SM120 and GB10 / SM121 while
  touching the real compressed+SWA candidate shape.
- The result supports moving toward an endpoint candidate, but not by directly
  dropping this synthetic kernel into production. Endpoint work must add
  graph-stable workspace sizing, conservative shape gating, sparse
  attribution, and `FULL_AND_PIECEWISE` validation. It also needs to prove
  that one-head program granularity does not erase the component win after
  integration.
- A follow-up stream-shape probe showed the endpoint contract differs by path:
  the real C4A/D512 indexed path has almost no compressed same-position reuse
  (`~0.7%`) but perfect SWA shifted-window reuse, while C128A chunk rows have
  high compressed and SWA stream reuse. Therefore the first endpoint candidate
  should not assume compressed candidates are shared for the D512 path. It
  should either keep compressed work on the current exact path and group only
  the SWA stream, or introduce a real union/membership representation for
  compressed candidates.
- Immediate next step: build a component candidate for the real D512 endpoint
  contract: current/random compressed top-k plus grouped SWA union, with exact
  online merge against the current D512 state. Only after that wins should it
  be wired as a default-off endpoint path.

## 2026-06-08 Checkpoint: Real-D512 Grouped-SWA Component

Status: active component prototype, not wired to vLLM endpoint.

This component keeps the D512 compressed top-k stream on the current exact
per-token split path and only groups the shifted SWA stream. It then merges the
compressed and SWA online softmax states exactly. This matches the stream-shape
probe result: the real C4A/D512 indexed path has almost no compressed
same-position reuse, but the SWA shifted window is shared across neighboring
query rows.

Component target shape: `512` query tokens, `64` heads, D=`512`,
`mixed-c128-swa`, `128` compressed candidates, group size `32`,
grouped-SWA block-C `32`.

| Host | Candidates | Current split | Grouped SWA | Speedup vs split | Speedup vs current chunk | Max diff |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RTX PRO 6000 x2 | 640 | 0.620 ms | 0.572 ms | 1.084x | 4.166x | 0.002607 |
| RTX PRO 6000 x2 | 1152 | 1.375 ms | 0.814 ms | 1.689x | 5.194x | 0.000953 |
| GB10 node 1 | 640 | 7.742 ms | 4.917 ms | 1.575x | 2.286x | 0.001639 |
| GB10 node 1 | 1152 | 12.674 ms | 5.772 ms | 2.196x | 3.718x | 0.001243 |

Parameter sweep for the `1152`-candidate target:

| Host | Group/block-C | Grouped SWA | Speedup vs split |
| --- | --- | ---: | ---: |
| RTX PRO 6000 x2 | 8 / 32 | 1.252 ms | 1.100x |
| RTX PRO 6000 x2 | 16 / 32 | 0.998 ms | 1.380x |
| RTX PRO 6000 x2 | 16 / 64 | 0.859 ms | 1.602x |
| RTX PRO 6000 x2 | 32 / 32 | 0.814 ms | 1.713x |
| GB10 node 1 | 8 / 32 | 7.709 ms | 1.604x |
| GB10 node 1 | 16 / 32 | 6.807 ms | 1.831x |
| GB10 node 1 | 16 / 64 | 6.174 ms | 2.028x |
| GB10 node 1 | 32 / 32 | 5.773 ms | 2.208x |

Interpretation:

- This is the first fork-independent component result that respects the real
  D512 stream contract and wins strongly on both RTX PRO 6000 / SM120 and
  GB10 / SM121.
- The win scales with SWA candidate count because the compressed stream is
  deliberately left ungrouped. That is the correct tradeoff for D512 C4A
  shapes where compressed candidates are mostly per-token.
- Group size `32` with block-C `32` is the current component default. It avoids
  the shared-memory pressure seen in prior group32/block-C64 probes while
  giving the best measured result in this sweep.
- Next endpoint candidate should use this as the dataflow target, but still
  needs graph-stable workspace sizing, route attribution, conservative shape
  gating, and full promotion validation before it can become PR branch
  behavior.

### Endpoint Probe Result

A default-off vLLM endpoint prototype was archived on local branch
`codex/backup-grouped-swa-endpoint-20260608` and removed from the active work
tree. It routed only full-row C4A/D512 chunks through compressed-current plus
grouped-SWA state merge and failed closed to the existing split path for early
rows.

RTX C=1 smoke with TP=2, EP enabled, MTP=2, FP8 KV, prefix cache disabled,
`FULL_AND_PIECEWISE`, 59K/124K synthetic prompts, and
`max_num_batched_tokens=4096` showed endpoint regression:

| Shape | Env off TTFT | Env on TTFT | Delta |
| --- | ---: | ---: | ---: |
| 59K | 13.028 s | 13.200 s | +1.3% |
| 124K | 29.840 s | 30.212 s | +1.2% |

Sparse stats confirmed the route was active:
`mla_prefill_indexed_d512_grouped_swa` appeared for mature chunks, while early
chunks still used `mla_prefill_indexed_d512`. The total sparse-accumulate time
increased because the naive endpoint shape added separate compressed, grouped
SWA, merge-state, merge-acc, and finish launches. Therefore do not reintroduce
this endpoint form.

Updated direction:

- Keep the component result as evidence that SWA value work can be reduced.
- Do not wire grouped-SWA as separate compressed + grouped-SWA + merge launches.
- A future endpoint must fuse grouped-SWA with the finish/merge path or
  otherwise remove enough launch/workspace traffic to preserve the component
  win.

## 2026-06-13 Checkpoint: Dependency And Component Refresh

Status: current same-host triage evidence on RTX PRO 6000 / SM120, using the
backend-parity dev branch at `591b71bed0`.

The dependency refresh changes the b12x integration question from "public APIs
missing" to "public APIs available, endpoint value still unproven":

- Default `b12x==0.20.0` resolver is rejected for this dev venv. It moved the
  Torch/Triton/CUDA runtime package set, downgraded NCCL, and made `vllm._C`
  fail with a Torch ABI symbol error.
- `b12x==0.20.0` installed as a no-deps experiment variable is healthy on the
  current runtime stack. `vllm._C` imports and
  `tests/v1/attention/test_sm120_deepgemm_fallbacks.py -q` passed.
- Public b12x DS4 compressed-MLA, sparse-indexer-extend, native MXFP4 MoE
  helper, WO, mHC, FP8 linear, and PCIe all-reduce APIs import in this state.
  Current Dev still has no vLLM runtime hooks for DS4 b12x compressed MLA,
  native MXFP4 b12x MoE, b12x WO/mHC, or b12x sparse indexer selection.
- FlashInfer `0.6.13rc1` no-deps is rejected for the current venv because it
  mismatches the installed `flashinfer-jit-cache`; stable `0.6.12` remains the
  official-wheel route and still does not expose packed SM120 sparse MLA.

Refreshed RTX component results:

| Component | Shape | Current split / baseline | Candidate | Interpretation |
| --- | --- | ---: | ---: | --- |
| Public b12x compressed MLA | `real_c128` | D512 split+finish `0.209 ms` | b12x `0.432 ms` | Faster than old online packed, but still about `2.07x` slower than current D512. Do not port this direct route next. |
| Grouped-SWA D512 | `640` candidates | split `0.627 ms` | grouped-SWA `0.575 ms` | Small positive component signal. |
| Grouped-SWA D512 | `1152` candidates | split `1.382 ms` | grouped-SWA `0.824 ms` | Strong component signal, but the previous separate-launch endpoint form regressed. |
| Grouped stream online | `640` candidates | split `0.601 ms` | grouped stream `0.354 ms` | Strong signal for high-reuse C128A-style stream dataflow. |
| Grouped stream online | `1152` candidates | split `1.320 ms` | grouped stream `0.600 ms` | Strongest current fork-independent component signal. |

Interpretation:

- Do not spend the next implementation slice on a direct public b12x
  compressed-MLA endpoint adapter. The dependency is now importable, but the
  component timing does not beat current D512.
- Do not spend the next implementation slice on official FlashInfer rc/git
  unless a matching wheel/jit-cache state exposes packed SM120 sparse MLA.
- The next code-bearing experiment should preserve the grouped-stream dataflow
  win while avoiding the archived endpoint's failure mode: extra compressed,
  grouped-SWA, merge-state, merge-acc, and finish launches.
- A plausible first prototype is a component-level fused dual-stream online
  kernel that emits the final output directly for a conservative D512/C128A
  shape, then only moves endpointward if the fused component beats current
  split+finish with exact output and graph-stable workspace assumptions.

## Work Plan

### Task 1: Branch And Code Hygiene

**Files to inspect:**

- `vllm/envs.py`
- `vllm/models/deepseek_v4/nvidia/flashmla.py`
- `vllm/models/deepseek_v4/common/ops/cache_utils.py`
- `tests/model_executor/test_deepseek_v4_flashinfer_packed_prefill.py`
- `docs/sm120_current_state.md`
- `docs/sm120_experiment_index.md`
- `docs/sm120_optimization_notes.md`

**Steps:**

- [ ] Confirm the PR branch contains only promoted/default-safe vLLM behavior.
- [ ] Keep the dev-only packed FlashInfer route on the dev branch or a backup
      branch, but do not promote it while it depends on an unmerged backend.
- [ ] Remove diagnostic switches, probes, and tests that are no longer attached
      to an active experiment.
- [ ] Update rejected notes when code is removed, including the reason and the
      last artifact that supported the decision.
- [ ] Run the focused vLLM smoke for touched files before any rebase or push.

**Exit criteria:** the worktree has one clear default path, one clear active
experimental path at most, and no dormant env switch without a document owner.

### Task 2: Freeze A Same-Host Baseline

**Required outputs:**

- Endpoint attribution for current default path.
- Endpoint attribution for the packed FlashInfer reference path, if the
  dependency venv is available.
- Component microbench baseline for the current D512 split/finish path.
- GB10 reduced long-C2 result and driver-health summary.

**Recommended commands:**

```bash
scripts/run_sm12x_prefill_gap_attribution.sh
scripts/run_gb10_prefill_gap_attribution.sh
scripts/run_sm12x_sparse_mla_ncu_microbench.sh
scripts/run_sm12x_prefill_decode_promotion_gate.sh
```

Use the same workload labels and prefix-cache mode as the latest accepted
baseline. If a remote dependency route is unavailable, record that as a blocked
reference path instead of rebuilding the machine during the kernel iteration.

**Exit criteria:** a new prototype can be compared against current D512, not
against memory or an external screenshot.

### Task 3: Triton Component Prototype

**Implementation boundary:**

- Start below the endpoint. Build a component microbench that uses real DS4-like
  stream lengths, main/SWA page layout, extra/compressed page layout, head dim
  `512`, and current C4A/C128A candidate shapes.
- First try to reduce cost per visit, not candidate count.
- Keep the reference comparison against the current exact D512 path in the test
  or microbench harness.

**Candidate designs to test first:**

- A single backend that handles main/SWA plus extra/compressed streams without
  an extra external merge launch.
- Online score/stat/value accumulation that avoids a large score workspace.
- A layout that preserves current head-block reuse while reducing value replay
  or score replay.
- Stream-specific page addressing for `SWA=64`, `C4A=64`, and `C128A=2`.

**Immediate rejection rules:**

- Slower than current D512 split+finish on GB10 component shapes.
- Faster only by reducing semantic candidates.
- Requires allocations after workspace lock.
- Requires disabling full CUDA graph capture.
- Needs a private or unmerged third-party package to run.

**Exit criteria:** component microbench is exact, faster than current D512 on a
representative shape, and does not introduce extra launch or workspace traffic
that obviously erases endpoint gains.

### Task 4: Endpoint Candidate

Only start this task after Task 3 wins.

**Endpoint requirements:**

- Default off until promotion.
- Internal developer gate only; no public user-facing tuning parameter.
- Sparse attribution must identify the new route separately.
- Shape gating must fail closed back to current D512.
- Workspace sizing must be captured during warmup and remain graph-stable.

**Focused validation:**

```bash
PYTHONPATH=. pytest \
  tests/model_executor/test_deepseek_v4_sparse_mla_metadata.py \
  tests/model_executor/test_deepseek_v4_sparse_mla_prefill_stats.py \
  tests/model_executor/test_deepseek_v4_flashmla_decode_dispatch.py \
  tests/v1/attention/test_sparse_mla_indexed_d512.py \
  -q

python -m ruff check \
  vllm/envs.py \
  vllm/models/deepseek_v4/common/ops/cache_utils.py \
  vllm/models/deepseek_v4/nvidia/flashmla.py \
  tests/model_executor/test_deepseek_v4_sparse_mla_metadata.py \
  tests/model_executor/test_deepseek_v4_sparse_mla_prefill_stats.py \
  tests/v1/attention/test_sparse_mla_indexed_d512.py
```

Then run a short endpoint smoke on SM120 and GB10 before any long benchmark.

**Exit criteria:** endpoint dispatch is proven by sparse stats, correctness
matches the existing path on focused tests, and first TTFT/input-token numbers
are positive enough to justify the promotion matrix.

### Task 5: Promotion Matrix

Run this only after a positive endpoint candidate exists:

- GSM8K limit-200.
- `FULL_AND_PIECEWISE` CUDA graph mode.
- Prefix-cache stress.
- Prefix-disabled and prefix-enabled KV lifecycle recoverability.
- Short throughput and 8K/1K throughput regression check.
- 59K / 124K C=1 and C=2 latency/fairness.
- Mixed-arrival and streaming-pressure gates.
- Story recall semantic gate.
- GB10 reduced long-C2.
- GB10 MTP=2 MoE TP sustained gate if the route affects GB10 or shared sparse
  MLA workspace behavior.

**Exit criteria:** no correctness drop, no user-feedback regression, and a
clear performance win in the target class. If the route is mixed, keep it in
dev and record why it is not PR-ready.

## Data To Collect Before Coding

No additional very-long 1M run is required before starting the rewrite design.
The existing 512K/1M results already show the problem is real work growth, not
just scheduling idle time.

Collect these only if the current artifact paths are stale after the next
rebase:

- A fresh short/mid/long C=1 attribution run with prefix cache disabled.
- A matching GB10 reduced attribution run.
- A component D512 baseline with the same CUDA, Triton, and vLLM commit as the
  prototype branch.
- A stack probe that records whether official FlashInfer, public b12x, or the
  packed FlashInfer reference route is actually available in the target venv.

## Stop Rules

- Stop and clean up if the prototype only moves launch count around.
- Stop and clean up if GSM8K falls below the hard gate.
- Stop and clean up if GB10 driver health worsens, even when SM120 improves.
- Stop and clean up if the code requires a fork-only runtime dependency.
- Stop and clean up if the only win comes from prefix-cache hits or from
  dropped candidates.

When stopping, remove the vLLM code, leave the smallest durable test only if it
guards a real bug, and record the rejected route in
`docs/sm120_optimization_notes.md`.
