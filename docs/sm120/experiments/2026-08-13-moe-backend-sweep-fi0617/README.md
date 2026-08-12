# MXFP4 MoE backend sweep on FlashInfer 0.6.17

Status: accepted
Date: 2026-08-13
Owner/context: after the 0.6.17 upgrade (`195c4ce7d1`), re-ask whether upstream's
refreshed SM12x MoE kernels now beat the Marlin path we default to.

## Question

FlashInfer 0.6.17 ships reworked SM12x MoE kernels. Our serve never enters
FlashInfer for MoE — `auto` selects Marlin W4A16 — so a same-config A/B across
FlashInfer versions is guaranteed to show nothing.

The question worth fleet time is the other one: **is an upstream kernel now
better than the path we chose instead?** That is a comparison between routes,
not between versions, and it is answerable.

## Profile

- Hardware: 2× GB10 (SM121), TP=2 over RoCE
- vLLM branch/commit: `195c4ce7d1` (upstream merge 08-11 + FlashInfer 0.6.17)
- Dependency identity: flashinfer-python 0.6.17, apache-tvm-ffi 0.1.11
- TP / PP / EP: TP=2 / PP=1 / EP off
- MTP: DSpark, `num_speculative_tokens=5`, probabilistic draft sampling
- FP8 KV: on
- Prefix cache: on
- CUDA graph mode: default (FULL_AND_PIECEWISE)
- `max_model_len`: 49152
- `max_num_seqs`: 64
- `max_num_batched_tokens`: 8192
- Workload: `bench serve` random pp2048/d256, c=8, 24 prompts, 3 repeats/arm

## Result

| arm | engine actually selected | decode tok/s | acceptance | TTFT ms |
|---|---|---|---|---|
| `auto` | `MarlinExperts` | **58.13 ± 2.65** | **1.84 ± 0.13** | 3879 ± 212 |
| `flashinfer_cutlass` | `FlashInferExperts` | 43.12 ± 0.19 | 1.22 ± 0.01 | 4183 ± 220 |
| `flashinfer_trtllm` | — | start refused | — | — |
| `flashinfer_b12x` | — | start refused | — | — |

`flashinfer_cutlass`: decode **−25.8%**, acceptance **−33.7%**, TTFT +7.8%
(within the spread, not a signal).

**Marlin stays.** No route change from this upgrade.

## Interpretation

The interesting part is that **the CUTLASS kernel is not slower — it is faster.**
Decode throughput factors as `acceptance × decode steps per second`:

| | acceptance | decode steps/s | decode tok/s |
|---|---|---|---|
| Marlin | 1.84 | 31.59 | 58.13 |
| CUTLASS | 1.22 | **35.34 (+11.9%)** | 43.12 |

CUTLASS runs ~12% more decode steps per second and still loses by 26%, because
the drafter accepts 34% fewer tokens per step. A sweep that recorded only tok/s
would have concluded "the CUTLASS kernel is 26% slower" — the opposite of what
happened, and it would have sent the next person to profile a kernel that is not
the problem.

The same directional effect appeared in the 2026-07-12 A/B on FlashInfer 0.6.14
(acceptance 2.40 → 2.18), so it reproduces across two FlashInfer releases and
two absolute acceptance levels. The mechanism is inferred, not measured: the
DSpark drafter runs through the same MoE weights, so a different kernel means
different rounding, and the draft distribution diverges from the target's
slightly more. **What is measured is the effect; the mechanism is a hypothesis
that would need a numerics comparison to confirm.**

Consequence for anything with a speculative drafter: **a MoE kernel change is a
numerics change, and a numerics change is an acceptance change.** Kernel-level
microbenchmarks cannot see this — the cost lands entirely in the accept rate.

### What closed the other routes

Read from the **worker** log; the head log only says "see root cause above".

- `flashinfer_trtllm` — `kernel does not support current device cuda`. No SM121
  kernel. (Matches the standing note that `trtllm_*` MoE is DC-Blackwell only.)
- `flashinfer_b12x` — `not supported for MXFP4 MoE`. It is an NVFP4-class path;
  the model's experts are MXFP4.
- `flashinfer_cutlass` — **first attempt failed for an unrelated reason**: the
  JIT build ran out of memory (see below). Retried with a cap; that is the row
  in the table.

The engine's own rejection message enumerates every backend legal for MXFP4:
`deep_gemm`, `flashinfer_trtllm`, `flashinfer_trtllm_afp8`, `flashinfer_cutlass`,
`flashinfer_cutlass_afp8`, `triton`, `triton_unfused`, `humming`, `marlin`,
`aiter*`, `xpu`, `cpu`.

### What this sweep does not cover

- `deep_gemm` — **not attemptable here**: the package is not installed, and the
  SM120 W4A8 kernels live in DeepGEMM's `nv_dev` branch rather than any release.
- `triton`, `triton_unfused`, `humming`, `*_afp8` — **untested.** Portable enough
  that they would probably start; none of them is new in 0.6.17, so none was in
  scope for "did upstream's refresh change the answer". Recording the gap rather
  than implying coverage.
- `aiter*` is ROCm, `xpu`/`cpu` are other devices — not applicable.
- One workload shape only (pp2048/d256, c=8). A long-context or high-concurrency
  shape could shift the kernel-speed term, though it would have to overcome a
  34% acceptance deficit.

## Method notes worth reusing

Three things the sweep script does that a naive version does not. Each one
produced a wrong answer here first.

1. **Read back the kernel the engine actually selected.** `--moe-backend X`
   being accepted is not evidence X ran. A silent fallback makes an arm measure
   the baseline twice, and "no difference" then looks like a real null result.
   The `engine selected:` line is what makes the CUTLASS row trustworthy.
2. **Capture acceptance length next to throughput.** See above — without it the
   headline conclusion inverts.
3. **Cap JIT parallelism, and propagate the cap to the worker node.** FlashInfer
   JIT-builds 97 CUTLASS grouped-GEMM units for `fused_moe_120`; ninja defaults
   to `-j nproc` = 20 on GB10, memory is exhausted, the OOM killer takes an nvcc,
   ninja returns non-zero, and the serve dies with *"Engine core initialization
   failed"* — which reads exactly like an unsupported backend. That misreading
   cost this arm a start. A head-only cap is not enough: the worker builds too,
   so it needs `SERVE_REMOTE_ENV_VARS="MAX_JOBS NVCC_THREADS"`.

Point 3 generalises past MoE: **on this fleet a JIT-compiled backend can fail for
lack of memory and report it as lack of support.** Pre-warm deliberately, capped,
where no startup timeout is watching.

## Follow-Up

- Decision: `docs/sm120/decisions/accepted/mxfp4-moe-backend-sm12x.md`
- Script: `scripts/run_sm12x_moe_backend_sweep.sh`
- Rerun trigger: any FlashInfer release touching SM12x MoE, a DeepGEMM release
  carrying SM120 kernels, or a change to the drafter.
- Raw numbers: `evidence.md`
