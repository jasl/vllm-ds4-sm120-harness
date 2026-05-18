# SM120 Optimization Notes

These notes are the current working assumptions for DeepSeek V4 SM120
performance work. They are intentionally separate from historical baseline
reports so later tuning does not accidentally inherit outdated architecture
assumptions.

## Hardware Assumptions

- Target hardware: NVIDIA RTX PRO 6000 Blackwell Workstation Edition,
  SM120 / compute capability 12.0.
- Memory subsystem: GDDR7. Do not describe SM120 workstation results as HBM
  bandwidth results.
- Do not assume SM100/B200/B300-only paths are portable to SM120. In
  particular, do not base a vLLM optimization on TMEM, `tcgen05`, or TMA unless
  it has been independently verified on the SM120 target and is guarded behind
  the correct architecture checks.
- Primary product target: single-stream and small-concurrency interactive
  latency. Treat concurrency 24 or 32 as the practical upper bound for this
  workstream; larger concurrency is a regression check, not the first
  optimization target.

## Current Bottleneck Shape

The active long-context target is 128K-130K context reliability and TTFT on the
dual-SM120 development setup, with the expectation that validated low-level
improvements should scale to four-card users even though four-card hardware is
not currently available for local validation.

Measured work so far points at the sparse-MLA indexer / FP8 MQA logits path,
not at a simple GDDR7 bandwidth ceiling:

- The large step change came from avoiding the slow fallback around FP8 MQA
  logits and top-k. The 127K C=1 cold-prefill mean moved from roughly 60.8 s to
  the high-36 s range after the direct Triton logits plus row-top-k path.
- Widening the direct FP8 MQA logits Triton tile from `BLOCK_N=64` to
  `BLOCK_N=128` was a small positive step and is currently kept.
- NCU observations for late-context FP8 MQA logits show register / occupancy /
  eligible-warp / long-scoreboard pressure. Treat memory throughput counters as
  GDDR7 memory-subsystem evidence, not HBM evidence.

## External Reference: DeepGEMM PR 324

DeepGEMM PR
[`deepseek-ai/DeepGEMM#324`](https://github.com/deepseek-ai/DeepGEMM/pull/324)
is useful as a design reference, but it should not be treated as a dependency
for the vLLM PR branch. The upstream DeepGEMM project may not accept the PR, and
vLLM may not accept relying on a DeepGEMM fork.

Useful ideas to study:

- FP8 MQA logits: `BLOCK_KV` / `BLOCK_N` around 128, Q/KV reuse, explicit
  register budgeting, and avoiding unnecessary epilogue work.
- Paged MQA: split-KV and scheduler choices for long-context decode and
  multi-turn reuse.
- Small-M GEMM / BMM: the A/B-swap idea for `M <= 32` is aligned with
  small-concurrency decode, but it is not the first lever for 128K cold prefill.

Ideas to avoid carrying over blindly:

- Full DeepGEMM fork integration.
- SM100/B200/B300 assumptions around TMEM, `tcgen05`, TMA, or datacenter HBM.
- Large C++/JIT kernel ports unless a small, measured vLLM-owned variant is the
  only way to remove a proven bottleneck.

## Experiment Discipline

- Keep measured-effective code changes in the active branch.
- Record effective changes in successful optimization notes.
- Record ineffective experiments, then remove their code. Do not leave A/B
  switches, dead paths, or temporary probes in the production branch.
- If a negative or ambiguous experiment may be worth revisiting, preserve a
  backup branch before reverting it.
- Fixed gates for promotion:
  - short-context latency must not regress,
  - 64K/128K long-context latency at C=1/2/4 must not regress,
  - GSM8K `exact_match_flexible` must not drop below the fixed baseline,
  - correctness/unit smoke for the touched vLLM path must pass.

## Near-Term Work Queue

1. Profile the active FP8 MQA logits Triton path with NCU on representative
   late-context 128K launches.
2. Sweep small tile/register-pressure changes around `BLOCK_M`, `BLOCK_N`,
   `BLOCK_H`, and `num_warps`, keeping each candidate small enough to revert.
3. Gate candidates with the short + 64K/128K + GSM8K matrix before promotion.
4. After prefill is stable, move to paged MQA decode and small-M GEMM/BMM
   experiments for long-context multi-turn latency.
