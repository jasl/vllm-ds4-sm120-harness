# Nsight Systems Long Trace

System-wide nsys trace of vLLM nomtp serve over its full lifecycle (startup
→ warmup → captured request → teardown) on 2× RTX PRO 6000 Blackwell
Workstation Edition. 125 MiB `.nsys-rep`, complementary to the per-phase
torch-profiler captures in the primary `v6b` baseline (which are
kernel-summary tables only, not raw timelines).

## Files

- `nsys_profile.nsys-rep` (~120 MiB) — **NOT tracked in git** (see
  `.gitignore`; binary profiling artefacts are local-only). The binary
  trace is preserved on the host that produced this bundle; ask the
  bundle maintainer or rerun the capture yourself (see "Reproducing"
  below).
- `nsys_run.json` — captured request elapsed + token usage (tracked)
- `serve_command.txt` / `nomtp_serve.sh` — exact serve invocation (tracked)

## Workload

- Serve: nomtp at TP=2, EP=on, KV fp8, block=256, max_model_len=65536
- Warmup: 32-token chat completion
- Captured request: 128-token chat completion, "Write a short paragraph
  about distributed inference systems." (`elapsed_s=1.14, completion_tokens=101`)

Trace covers the full serve process tree from spawn through SIGTERM teardown
(~150 seconds total). The first 80 seconds are model-load + cudagraph + JIT
compilation warmup; bench activity is in the last ~5 seconds.

## What to use this for

- Per-kernel timeline (which CUDA streams overlap, where the gaps are)
- NVTX-annotated phase boundaries inside vLLM (`compute_logits`, `forward`,
  etc.)
- Identifying serialisation points where multi-GPU collectives stall
- Comparing against B200 SM10x trace under the same workload (which is the
  primary motivation for shipping this on SM12x)

For the GUI-free kernel-time top-N, see also `v6b/nomtp/decode_profile/torch_kernel_summary.md`
and `v6b/mtp/decode_profile/torch_kernel_summary.md` in this same bundle —
those tables are computed offline from torch profiler chrome traces, not
nsys.

## Reproducing

```bash
NSYS_BIN=/usr/local/cuda/bin/nsys \
SERVE_COMMAND='bash /path/nomtp_serve.sh' \
OUT_DIR=/path/out \
bash scripts/run_nsys_profile_launch.sh
```

Note: as of this revision the harness script's `--capture-range=cudaProfilerApi`
mode is broken (client-side `cudaProfilerStart` doesn't affect the wrapped
serve process). This trace was captured by manually dropping the
capture-range flags and letting nsys run for the serve's full lifetime. A
patch to the wrapper to make this the default is a planned followup.
