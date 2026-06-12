# DeepSeek V4 SM12x Handoff

Last updated: 2026-06-12

This harness is the repo-independent validation and evidence workspace for
DeepSeek V4 SM12x work. Keep this handoff public-safe: do not record private
hostnames, IP addresses, usernames, local absolute paths, tokens, or model
cache locations here. Put those details in ignored files such as
`HANDOFF.local.md` or `.env`.

## Start Here

Read these files in order before changing either the harness or a vLLM branch:

1. `AGENTS.md` for repository rules and public-safety constraints.
2. `docs/sm120_current_state.md` for the current technical posture and next
   target.
3. `docs/sm120/README.md` for the framework-era note structure.
4. `docs/sm120/index.md` for new decisions and experiment packages.
5. `docs/vllm_correctness_gates.md` for promotion and regression gates.
6. `docs/dgx_spark_bare_metal_cluster.md` for GB10 / SM121 setup, cache
   hygiene, distributed startup, and driver-health checks.
7. `docs/sm120_experiment_index.md` to find pre-framework historical evidence
   in the long notes.
8. `docs/sm120_optimization_notes.md` only when the detailed legacy artifact
   trail or rejected-route rationale is needed.

The long optimization notes are a legacy evidence archive, not the primary
entrypoint. New experiment details should go under `docs/sm120/experiments/`,
and durable conclusions should go under `docs/sm120/decisions/`. If legacy
notes conflict with `docs/sm120_current_state.md`, refresh the compact current
state first.

## Source Of Truth

The control-machine checkout is the source of truth for both this harness and
the associated vLLM checkout. Remote SM120 / SM121 hosts are execution targets,
not independent development sources.

- Commit tracked changes on the control machine first.
- Push or otherwise sync the known-good commit to remote hosts.
- If a remote checkout is dirty, inspect the diff before resetting it. Preserve
  useful diagnostics, but do not let temporary remote edits become a fork.
- Keep concrete remote paths and access commands only in `HANDOFF.local.md`.

`HANDOFF.local.md` should also record the current aligned harness and vLLM commit
hashes for each machine.

## Active Hardware Scope

- Dual RTX PRO 6000 / SM120 remains the primary development target and the
  strongest local source for 59K / 124K latency, short throughput, GSM8K,
  prefix/KV lifecycle, and sparse-MLA profiling evidence.
- Two-node DGX Spark / GB10 / SM121 is now a persistent development and test
  environment. Use it for reduced long-C2 availability, prefix-cache
  multi-user reports, MTP=2 MoE TP liveness, 512K / 1M frontier availability,
  Docker/Aiden recipe parity, and SM121-specific driver-health work.
- GB10 performance is not automatically extrapolated from SM120. Treat GB10 as
  a capacity and stability target first because its unified-memory and bandwidth
  envelope is much tighter.
- Four-card and 1M customer commitments still require target-topology evidence.
  Dual-card RTX and two-node GB10 results are useful development evidence, not
  proof for every larger deployment.

Supported CUDA targets for this effort are SM120 and SM121. Prefer specific
arch values for local builds to keep compile time down:

- SM120: `CUDA_ARCH_LIST=120a`, `TORCH_CUDA_ARCH_LIST=12.0a`
- SM121: `CUDA_ARCH_LIST=121a`, `TORCH_CUDA_ARCH_LIST=12.1a`

Do not widen the support matrix without a new explicit requirement.

## Branch Posture

- `ds4-sm120-preview-dev` is the active vLLM development branch.
- The public PR branch for `vllm-project/vllm#41834` receives only promoted
  changes that have passed the relevant smoke, correctness, performance, and
  user-feedback gates.
- Experimental, diagnostic, or env-gated work stays on dev until it passes the
  promotion matrix. If a route is rejected, remove the code path and record the
  result in the notes.
- vLLM commits require DCO sign-off. Use `git commit -s` or preserve a valid
  `Signed-off-by:` trailer when rebasing, squashing, cherry-picking, or
  force-pushing vLLM branches.

Every upstream rebase is a semantic integration gate. Read the upstream
DeepSeek / MoE / CUDA-graph / scheduler changes in the conflict area, drop
obsolete local patches that upstream replaced, and run targeted tests before
claiming the branch is healthy.

## Environment Rules

Use the profile snippets under `configs/` for machine-independent defaults:

```bash
source configs/sm120_tp2_serve.env.example
source configs/gb10_sm121_serve.env.example
```

Keep private paths, hostnames, SSH targets, and artifact roots in ignored local
notes. Copy `env.sample` to `.env` for local overrides; `.env` is ignored and
must not be committed.

For editable vLLM installs, preserve the build-cache-friendly command shape:

```bash
CCACHE_NOHASHDIR=true pip install --verbose --no-build-isolation -e .
```

After reinstalling or rebasing vLLM, update environment-side packages that are
known to affect stability, especially the CUDA 13 NCCL wheel/package. Keep
FlashInfer JIT cache and b12x as optional environment-side research
dependencies unless a validated upstream path makes them official.

Do not add public defaults that disable CUDA graph. `FULL_AND_PIECEWISE` remains
the required graph mode for correctness and promotion; eager-mode success is a
debugging clue, not a fix.

## Current Gate Model

For a vLLM change that affects serving behavior, preserve:

- GSM8K limit-200 correctness.
- `FULL_AND_PIECEWISE` CUDA graphs.
- Prefix-cache stress and KV lifecycle recoverability.
- Short throughput, including high-concurrency short profiles where applicable.
- 59K / 124K long-context C=1 and C=2 TTFT, decode, ITL p95/p99, and fairness.
- Mixed-arrival prefill/decode interference and streaming pressure.
- GB10 reduced long-C2 when the change can affect SM121, sparse MLA, scheduler,
  CUDA graph, or distributed runtime behavior.
- User-reported gates in `docs/vllm_correctness_gates.md` when a change touches
  the same reported surface.

The 512K / 768K / 1M frontier gate is a development observation gate, not a
routine PR hard gate. It separates capacity/admission, latency, and correctness
before any 1M claim is made.

## GB10 Watchpoints

- Reclaim file cache before GB10 large-context or Docker launches. The startup
  helpers do this by default and should fail closed when required cache reclaim
  cannot run.
- Current-boot NVIDIA driver signals are first-class gate outputs. `NVRM`,
  `Xid`, `UVM`, lost-GPU, illegal-access, or `NV_ERR_NO_MEMORY` signals make a
  run diagnostic unless explicitly allowed by that gate.
- Docker and bare metal are separate capacity profiles. After building or
  loading large images, reclaim file cache and re-record `MemAvailable`,
  KV-cache capacity lines, and driver health before comparing performance.
- Aiden / unholy-fusion image parity is an external-backend comparison route,
  not a promotion gate for this vLLM branch. It must keep the request model
  alias separate from the real DS4 tokenizer and must pass driver-health checks
  before its performance is compared.

## Active Technical Direction

The promoted baseline is the current D512 sparse-MLA path plus supporting
scheduling, workspace, prefix/KV lifecycle, and correctness fixes already
recorded in the current-state document.

The next production-class performance work is not another chunk-size sweep. It
must reduce real long-prefill sparse-MLA and FP8 MQA work or memory pressure:

- `_accumulate_indexed_attention_chunk_multihead_kernel`
- FP8 MQA logits / top-k paths
- candidate/value visits, live state, dependency depth, or score/logits traffic

Scheduler controls remain useful safety rails, especially for GB10 availability
and mixed workloads, but they are not expected to close the 512K / 1M TTFT and
GB10 raw-prefill gap by themselves.

## Remote Hygiene Checklist

Before a long run on a remote target:

1. Confirm the remote harness and vLLM commits match the control-machine
   intended commits.
2. Confirm the remote checkout is clean or that dirty diagnostics are preserved
   and understood.
3. Confirm the vLLM venv imports `torch`, `vllm`, `ninja`, and any optional
   research dependency being tested.
4. Confirm NCCL and CUDA toolkit paths are the intended ones for that host.
5. On GB10, reclaim file cache and scan current-boot driver logs before launch.
6. Save serve command, serve log, runtime metrics, GPU stats, driver-health
   summary, and phase exit codes with the artifact.

Do not use partial artifacts as a full baseline. If a phase fails, keep the
partial output and label the failing phase explicitly.
