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

## Successful Optimization Notes

### FP8 MQA Logits `BLOCK_M=16`

The direct FP8 MQA logits fallback originally launched the Triton kernel with
`BLOCK_M=8`, `BLOCK_N=128`, and 4 warps. A small tile sweep on a representative
late-context shape showed that widening the row tile to `BLOCK_M=16` roughly
halved the standalone kernel runtime while preserving output parity for the
sampled case. The promoted change keeps the scope narrow: only the wrapper grid
and `BLOCK_M` meta-parameter change.

Promotion gate, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2:

| Prompt Shape | Concurrency | Prior Mean TTFT | `BLOCK_M=16` Mean TTFT | Delta |
| --- | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 14.037 s | 13.394 s | -4.6% |
| 64K synthetic | 2 | 22.088 s | 19.798 s | -10.4% |
| 64K synthetic | 4 | 37.577 s | 34.065 s | -9.4% |
| 128K synthetic | 1 | 36.541 s | 33.264 s | -9.0% |
| 128K synthetic | 2 | 56.902 s | 49.199 s | -13.5% |
| 128K synthetic | 4 | 96.317 s | 82.181 s | -14.7% |

Correctness gate: GSM8K `exact_match_flexible` stayed at 0.95, matching the
fixed baseline.

Profiler note: NCU on the same FP8 MQA logits kernel showed higher SM
throughput and lower issued-instruction spacing despite lower theoretical
occupancy. The path still does not look GDDR7-bandwidth saturated; continue to
treat register pressure, eligible warps, and long-scoreboard stalls as the next
optimization surface.

Caveat: the short-context cold gate saw a first-request Triton compile spike
after the new specialization. The second short request was in the expected
steady-state range. Do not count the first-request compile spike as a model
latency regression, but keep startup warmup in mind before presenting
user-facing cold-start numbers.

## Ineffective Or Ambiguous Optimization Notes

### FP8 MQA Logits `BLOCK_M=32`, `BLOCK_N=256`

This tile looked better in the standalone late-context microbench than
`BLOCK_M=16`, `BLOCK_N=128`: the wrapper shape improved from roughly 14.65 ms
to roughly 11.43 ms, and sampled outputs matched. It was still rejected because
the end-to-end long-context gate did not preserve all latency targets.

| Prompt Shape | Concurrency | `BLOCK_M=16` Mean TTFT | `BLOCK_M=32`, `BLOCK_N=256` Mean TTFT | Decision |
| --- | ---: | ---: | ---: | --- |
| 64K synthetic | 1 | 13.394 s | 13.972 s | reject |
| 64K synthetic | 2 | 19.798 s | 19.846 s | reject |
| 64K synthetic | 4 | 34.065 s | 34.336 s | reject |
| 128K synthetic | 1 | 33.264 s | 33.691 s | reject |
| 128K synthetic | 2 | 49.199 s | 49.344 s | reject |
| 128K synthetic | 4 | 82.181 s | 80.187 s | positive but insufficient |

The C=4 128K result was positive, but the 64K and 128K C=1/C=2 regressions
violate the promotion rule for single-stream and small-concurrency latency.
The code change was removed; do not reintroduce this tile unless a later change
also fixes the lower-concurrency regressions.

### FP8 MQA Logits `BLOCK_M=32`, `BLOCK_N=128`

This tile was tested separately after the `BLOCK_M=32`, `BLOCK_N=256`
rejection because it was a more conservative variant: the standalone
late-context microbench had shown it faster than `BLOCK_M=16`,
`BLOCK_N=128`, while keeping the logits column tile at 128. It also passed a
127K C=1 smoke with a small mean TTFT improvement.

The full latency gate was mixed. Long-context latency improved across all
64K/128K C=1/2/4 rows:

| Prompt Shape | Concurrency | `BLOCK_M=16`, `BLOCK_N=128` Mean TTFT | `BLOCK_M=32`, `BLOCK_N=128` Mean TTFT | Delta |
| --- | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 13.394 s | 13.297 s | -0.7% |
| 64K synthetic | 2 | 19.798 s | 19.459 s | -1.7% |
| 64K synthetic | 4 | 34.065 s | 33.076 s | -2.9% |
| 128K synthetic | 1 | 33.264 s | 32.195 s | -3.2% |
| 128K synthetic | 2 | 49.199 s | 47.900 s | -2.6% |
| 128K synthetic | 4 | 82.181 s | 78.647 s | -4.3% |

It was still rejected because the fixed promotion gates did not hold:

| Gate | `BLOCK_M=16`, `BLOCK_N=128` | `BLOCK_M=32`, `BLOCK_N=128` | Decision |
| --- | ---: | ---: | --- |
| 4K synthetic C=1 mean TTFT | 2.766 s | 1.138 s | positive |
| 4K synthetic C=2 mean TTFT | 1.455 s | 1.472 s | reject |
| 4K synthetic C=4 mean TTFT | 1.932 s | 2.186 s | reject |
| GSM8K `exact_match_flexible` | 0.95 | 0.94 | reject |

The code change was removed. This result is worth keeping as evidence that
larger row tiles can help long-context prefill, but correctness and
short-context gates must be fixed before revisiting it.

### FP8 MQA Logits `BLOCK_D=128`

This variant kept the promoted `BLOCK_M=16`, `BLOCK_N=128` launch shape and
changed only the dot tile from `BLOCK_D=64` to `BLOCK_D=128`, covering the
full head dimension in one dot. It looked promising in isolation:

- late-context microbench improved from roughly 14.55 ms to 12.76 ms;
- a 127K C=1 smoke improved mean TTFT from the `BLOCK_M=16` smoke value of
  34.196 s to 32.763 s, with zero request failures.

It was still rejected by the first full-gate phase. The short-context 4K
C=1/C=2/C=4 latency means were positive, but the C=4 row had one failed
request: the response missed one required retrieval term. Because this is a
correctness failure in the fixed gate, the long-context and GSM8K phases were
not promoted as evidence for this candidate.

The code change was removed. Do not revisit this exact `BLOCK_D=128` variant
unless a later numerical/correctness analysis explains the short-context
retrieval miss.

### FlashInfer Autotune Recheck After vLLM PR 42857

After rebasing onto upstream with vLLM PR 42857, FlashInfer autotune can be
enabled again without the earlier startup failure. It was rechecked against the
same 131K long-context gate, prefix cache disabled, 4096 max-num-batched-tokens,
TP=2, MTP=2.

The long-context TTFT result was neutral to slightly negative for this
DeepSeek V4 SM120 path:

| Prompt Shape | Concurrency | Autotune Off Mean TTFT | Autotune On Mean TTFT | Delta |
| --- | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 13.957 s | 13.911 s | -0.3% |
| 64K synthetic | 2 | 20.077 s | 19.876 s | -1.0% |
| 64K synthetic | 4 | 33.279 s | 33.492 s | +0.6% |
| 128K synthetic | 1 | 33.298 s | 33.590 s | +0.9% |
| 128K synthetic | 2 | 48.198 s | 48.265 s | +0.1% |
| 128K synthetic | 4 | 80.107 s | 81.556 s | +1.8% |

Both runs reported the same KV budget, about 11.34 GiB available KV cache,
755,050 GPU KV-cache tokens, and 5.76x maximum concurrency at 131,072 tokens.
The autotune-on run logged that no FlashInfer autotune cache entries were found
and fell back to default tactics, so this is not a current optimization lever
for the active path. The autotune-off comparison run had one 64K C=4 retrieval
miss; the autotune-on run passed this one-shot matrix, but do not treat that as
proof of a correctness improvement without repeated correctness gates.

Decision: keep upstream's fixed autotune behavior available, but do not spend
more 128K prefill optimization time here unless a later profile shows this
path is actually on the critical path.

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
