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
