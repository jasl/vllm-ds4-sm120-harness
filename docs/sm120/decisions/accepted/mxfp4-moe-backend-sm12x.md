# MXFP4 MoE backend on SM12x: keep Marlin

Status: accepted
Last reviewed: 2026-08-13
Applies to: DeepSeek-V4-Flash (MXFP4 experts) on GB10 / SM121, vLLM fork at
`195c4ce7d1`, FlashInfer 0.6.17
Profile sensitivity: EP-off, prefix-cache-on, **MTP on (DSpark)** — the MTP
condition is load-bearing, see Why

## Decision

Leave `--moe-backend` unset. `auto` selects Marlin W4A16 and that remains the
fastest route we have measured for MXFP4 experts on SM121.

`flashinfer_cutlass` is the only alternative **that was measured** — it accepts
MXFP4, has an SM121 kernel, and loses decode throughput by 26%. FlashInfer
0.6.17's reworked SM12x MoE kernels do not change that.

It is not the only *legal* alternative, and an earlier version of this line said
it was. `triton`, `triton_unfused`, `humming` and the `*_afp8` variants are also
accepted for MXFP4; none was tested, and being accepted by the config layer says
nothing about whether an SM121 kernel exists — `flashinfer_trtllm` is accepted
too and has none. See "Why" below for the full status of each.

## Evidence

- `docs/sm120/experiments/2026-08-13-moe-backend-sweep-fi0617/README.md`
- `docs/sm120/experiments/2026-08-13-moe-backend-sweep-fi0617/evidence.md`
- Reproduce with `scripts/run_sm12x_moe_backend_sweep.sh`
- Prior consistent measurement: 2026-07-12 A/B on FlashInfer 0.6.14

## Why

Measured at pp2048/d256, c=8, TP=2, 3 repeats per arm:

| arm | decode tok/s | acceptance | TTFT ms |
|---|---|---|---|
| `auto` → Marlin | **58.13 ± 2.65** | **1.84 ± 0.13** | 3879 ± 212 |
| `flashinfer_cutlass` | 43.12 ± 0.19 | 1.22 ± 0.01 | 4183 ± 220 |

**CUTLASS loses despite being the faster kernel.** Decode factors as
`acceptance × steps/s`: CUTLASS runs 11.9% more decode steps per second and
still ends 25.8% behind, because the DSpark drafter accepts 33.7% fewer tokens
per step.

This is why the decision is scoped to MTP-on. The kernel choice is not really a
kernel-speed question here — it is a numerics question, and the drafter is what
prices it. **Without a speculative drafter the ranking could invert**, and
nothing in this evidence says otherwise.

Everything else is closed rather than slower:

- `flashinfer_trtllm` — no SM121 kernel (DC-Blackwell only)
- `flashinfer_b12x` — NVFP4-class, rejected for MXFP4 experts
- `deep_gemm` — **MEASURED 2026-08-13, still unusable.** The earlier line here
  said "package not installed", which was wrong: DeepGEMM is vendored through
  CMake FetchContent, not pip, so `importlib.metadata` was the wrong instrument.
  It is present and importable (`vllm.third_party.deep_gemm`). What blocks it is
  our own `support_deep_gemm()` gate excluding capability family 120, and that
  gate is correct: with the pin now at deepseek-ai `nv_dev` tip `8b1392b9` —
  which carries 27 of DeepGEMM's own SM120 files, including
  `sm120_fp8_fp4_gemm_1d1d.cuh` and the `tf32_hc_prenorm` GEMM DSv4's mHC uses —
  re-admitting family 120 still aborts at
  `utils/layout.hpp:107: sf.size(-2) == ceil_div(mn, gran_mn)`, both under
  `--moe-backend deep_gemm` and under `auto`. Control arm in the same run
  selected `MarlinExperts` and served (60.15 tok/s, accept 1.98), so the probe
  discriminates. Scope: DSv4 MXFP4 MoE on SM121. Says nothing about other models
  or about SM120 RTX, where the scale-factor layout may differ.
- `triton`, `triton_unfused`, `humming`, `*_afp8` — legal for MXFP4, **untested**

## Reopen If

- A FlashInfer release touches SM12x MoE again. The 0.6.17 refresh was
  substantial and still did not change the answer, but the acceptance gap is the
  thing to re-measure, not the kernel time.
- DeepGEMM's `layout.hpp` scale-factor contract changes, or DSv4's MXFP4 scale
  tensors are reshaped to satisfy it. Merely shipping SM120 kernels is NOT the
  reopen condition — that already happened (nv_dev tip `8b1392b9`) and the abort
  is unchanged.
- The drafter changes — method, `num_speculative_tokens`, or draft sampling.
  The whole result hangs on acceptance.
- Someone wants the untested arms (`triton`, `humming`, `*_afp8`) ruled in or
  out. They would each need to beat a 34% acceptance deficit, but they are not
  ruled out by anything measured here.

## Operational note

A `flashinfer_*` arm that dies with *"Engine core initialization failed"* is not
necessarily unsupported. FlashInfer JIT-builds 97 CUTLASS units for
`fused_moe_120`; at ninja's default `-j nproc` (20 on GB10) memory is exhausted
and the build failure surfaces as a startup failure. Cap with `MAX_JOBS`, and
propagate it to the worker node via `SERVE_REMOTE_ENV_VARS`. Read the **worker**
log for the real reason — the head log only says "see root cause above".
