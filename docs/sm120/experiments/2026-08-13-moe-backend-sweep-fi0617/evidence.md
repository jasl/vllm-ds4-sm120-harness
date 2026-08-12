# Evidence — MXFP4 MoE backend sweep on FlashInfer 0.6.17

## Command

```bash
TREE=<built vLLM tree at 195c4ce7d1> \
VENV=<venv with that tree installed> \
HARNESS=<harness checkout> \
STOP_CMD=<path to stop_replica.sh on the nodes> \
HEAD_HOST=<head> WORKER_HOST=<worker> \
HEAD_ROCE_IP=<head RoCE> WORKER_ROCE_IP=<worker RoCE> \
  scripts/run_sm12x_moe_backend_sweep.sh
```

Production replicas stopped for the duration; restored afterwards.

## Sweep run — 2026-08-12 21:05 → 22:51

```
=== MoE backend sweep  2026-08-12T21:05:55+08:00 ===
    tree=195c4ce7d1  flashinfer=0.6.17
    pp2048/d256 c=8, 3 repeats per arm, mml 49152

  --- auto ---
    engine selected: MarlinExperts,
    rep1  decode=56.63 tok/s  ttft=3805.32 ms
    rep2  decode=61.19 tok/s  ttft=4118.47 ms
    rep3  decode=56.56 tok/s  ttft=3713.17 ms
    SUMMARY auto        decode 58.13 +/- 2.65 (n=3)   ttft 3878.99 +/- 212.45 (n=3)
  --- flashinfer_cutlass ---
    START FAILED
  --- flashinfer_trtllm ---
    START FAILED
  --- flashinfer_b12x ---
    START FAILED

=== sweep done 2026-08-12T22:51:52+08:00 ===
```

Acceptance for the `auto` arm, read back from the bench logs (the sweep's
acceptance capture was added after this run — it is in the committed script):

```
auto rep1  Acceptance length: 1.78
auto rep2  Acceptance length: 1.99
auto rep3  Acceptance length: 1.75
           mean 1.84  sd 0.13
```

## Why each arm refused to start

The head log ends at `Engine core initialization failed. See root cause above.`
The root cause is on the **worker**:

```
flashinfer_trtllm
  ValueError: Mxfp4 MoE backend 'FLASHINFER_TRTLLM_MXFP4_MXFP8' does not support
  the deployment configuration since kernel does not support current device cuda.

flashinfer_b12x
  ValueError: moe_backend='flashinfer_b12x' is not supported for MXFP4 MoE.
  Expected one of ['deep_gemm', 'flashinfer_trtllm', 'flashinfer_trtllm_afp8',
  'flashinfer_cutlass', 'flashinfer_cutlass_afp8', 'triton', 'triton_unfused',
  'humming', 'marlin', 'aiter', 'aiter_mxfp4_fp8', 'aiter_mxfp4_mxfp4', 'xpu',
  'cpu']

flashinfer_cutlass
  RuntimeError: Ninja build failed. Ninja output: ...
```

Only the first two are backend verdicts. The third is a build that ran out of
memory: 97 CUTLASS grouped-GEMM units for `fused_moe_120`, ninja at `-j nproc`
(20), an nvcc taken by the OOM killer. Nothing in the head log distinguishes
this from an unsupported backend — which is why it was initially recorded as
one.

## CUTLASS retry, with the JIT build capped and pre-warmed

```
=== flashinfer_cutlass retry 2026-08-12T22:52:47+08:00 ===
  --- pre-warm the JIT cache, capped (-j 6) ---
    <head>   built 57178856 bytes
    <worker> already built
  --- serve with --moe-backend flashinfer_cutlass ---
  engine selected: FlashInferExperts,
  rep1  decode=43.26 tok/s  ttft=4025.41 ms  accept=1.22
  rep2  decode=43.20 tok/s  ttft=4434.61 ms  accept=1.22
  rep3  decode=42.91 tok/s  ttft=4089.79 ms  accept=1.21
  SUMMARY flashinfer_cutlass  decode 43.12 +/- 0.19 (n=3)  ttft 4183.27 +/- 220.03 (n=3)  accept 1.22 +/- 0.01 (n=3)
RETRY_DONE
```

`engine selected: FlashInferExperts` — not `MarlinExperts`. The arm measured the
CUTLASS path, not the baseline a second time.

## Derived

`decode tok/s = acceptance × decode steps/s`

| | acceptance | decode steps/s | decode tok/s |
|---|---|---|---|
| Marlin | 1.84 | 31.59 | 58.13 |
| CUTLASS | 1.22 | 35.34 | 43.12 |
| delta | −33.7% | **+11.9%** | −25.8% |

TTFT 3879 ± 212 vs 4183 ± 220 — the difference is inside the combined spread.

## Prior measurement

2026-07-12, FlashInfer 0.6.14, same route pair: decode dipped and acceptance
fell 2.40 → 2.18. Different absolute acceptance, same direction and same cause.
Two releases apart, the CUTLASS path costs acceptance.
