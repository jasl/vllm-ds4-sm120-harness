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
- Single-run long-context matrices are sensitive to runtime and Triton compile
  cache state. A follow-up same-service `autotune_on` first/second matrix did
  not show the second run getting faster, but both runs were materially faster
  than an earlier one-shot matrix in the same session. Treat repeat-count-1
  latency as a development signal, not a publishable number.

## Successful Optimization Notes

### Sparse SWA MTP Reorder Correctness Fix

The 64K-class MTP=2 C=3/C=4 retrieval miss was traced to a metadata split
mismatch rather than to unchecked draft acceptance. DeepSeek V4 sparse SWA
internally used `decode_threshold = 1 + num_speculative_tokens`, but still
reported `reorder_batch_threshold = 1` to the model runner. Because the runner
uses the minimum threshold across attention groups, a 3-token MTP verification
step could be ordered after a long chunked-prefill request. Sparse SWA then
assumed decodes were at the front of the batch and treated the MTP verification
tokens as prefill tokens.

The captured failing request showed the exact divergence: after `beta` was
accepted, the draft second token was `-qu`, but target verification's second
row preferred `-c`, producing `beta-cobalt-29` instead of
`beta-quartz-29`. The retained fix initializes sparse SWA's runner-facing
reorder threshold with `supports_spec_as_decode=True` and reuses that value for
the internal decode/prefill split. vLLM commit: `24db5ed89`.

Regression test:

| Test | Result |
| --- | --- |
| `tests/v1/attention/test_deepseek_v4_sparse_swa.py::test_sparse_swa_reorder_threshold_matches_mtp_decode_threshold` | failed before fix, passed after fix |
| `tests/v1/attention/test_deepseek_v4_sparse_swa.py tests/v1/attention/test_batch_reordering.py tests/v1/attention/test_attention_splitting.py` | 38 passed |

Targeted long-context gate, prefix cache disabled, 131K max-model-len, 4096
max-num-batched-tokens, TP=2, MTP=2, synthetic 2000-line prompt,
`max_tokens=128`, repeat count 3, artifact label
`sparse_swa_reorder_fix_c3_c4_62k/20260519090417`:

| Prompt Shape | Concurrency | Requests | Failures | Mean TTFT | Max TTFT |
| --- | ---: | ---: | ---: | ---: | ---: |
| 62K synthetic | 3 | 9 | 0 | 27.017 s | 40.346 s |
| 62K synthetic | 4 | 12 | 0 | 34.400 s | 54.593 s |

Correctness gate, artifact label
`sparse_swa_reorder_fix_gsm8k_limit200/20260519091147`: GSM8K limit-200
5-shot `exact_match_flexible` was 0.960 versus the fixed current-branch
baseline of 0.955, so the gate passed with delta +0.005.

Short-context smoke, artifact label
`sparse_swa_reorder_fix_short_smoke/20260519091743`, MTP=2, MT-Bench HF
dataset, 16 prompts:

| Concurrency | Successful Requests | Output Tok/s | Mean TTFT | Acceptance Rate |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 16/16 | 129.44 | 319.58 ms | 65.51% |
| 2 | 16/16 | 170.78 | 424.36 ms | 63.81% |
| 4 | 16/16 | 197.55 | 507.05 ms | 62.15% |

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

### Long-Context Matrix Warmup Sensitivity

A same-service follow-up ran the default `autotune_on` configuration twice
without restarting vLLM. The first pass included the usual 4K prewarm; the
second pass reused the same service process and skipped that prewarm.

| Prompt Shape | Concurrency | Earlier `autotune_on` | Same-Service First | Same-Service Second |
| --- | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 13.911 s | 12.054 s | 12.522 s |
| 64K synthetic | 2 | 19.876 s | 18.633 s | 19.386 s |
| 64K synthetic | 4 | 33.492 s | 32.540 s | 33.793 s |
| 128K synthetic | 1 | 33.590 s | 29.866 s | 29.941 s |
| 128K synthetic | 2 | 48.265 s | 45.358 s | 45.541 s |
| 128K synthetic | 4 | 81.556 s | 76.016 s | 78.073 s |

The same-service second pass was not faster than the first, so this is not
evidence that prefix reuse or repeated prompt cache effects are driving the
result. It is evidence that one-shot long-context latency is sensitive to
process, compile-cache, or system state. The serve logs still reported first
inference-time JIT events for the FP8 MQA logits, rowwise logits, top-k
combiner, FP8 einsum, and prefill metadata kernels.

Decision: use repeated measurements, preferably reporting min/median and
failures, before putting 64K/128K numbers in the PR body. Separately evaluate a
startup warmup plan that deliberately covers the late-context kernel shapes
instead of relying only on the current 4K prewarm.

### Long-Context MTP Correctness Recheck

A repeat-count-3 long-context gate was run after the same-service warmup
finding, still using the active default: prefix cache disabled, 131K
max-model-len, 4096 max-num-batched-tokens, TP=2, MTP=2, and 64-token
synthetic completions. Artifact label:
`repeat_gate_20260519032549`.

| Prompt Shape | Concurrency | Requests | Failures | Mean TTFT | Min TTFT | Max TTFT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 64K synthetic | 1 | 3 | 0 | 12.106 s | 12.065 s | 12.166 s |
| 64K synthetic | 2 | 6 | 0 | 19.015 s | 12.923 s | 25.191 s |
| 64K synthetic | 4 | 12 | 2 | 32.321 s | 13.385 s | 51.614 s |
| 128K synthetic | 1 | 3 | 0 | 30.063 s | 30.024 s | 30.119 s |
| 128K synthetic | 2 | 6 | 0 | 45.732 s | 30.588 s | 61.830 s |
| 128K synthetic | 4 | 12 | 0 | 77.252 s | 30.997 s | 129.329 s |

The two failures were both 64K C=4 retrieval misses for the middle sentinel.
Because those completions hit the 64-token output cap, a targeted 64K C=4
rerun increased the completion cap to 128 tokens. Artifact label:
`target_64k_c4_max128_20260519034448`. It still failed 2 of 12 requests.
The failed responses ended normally and had enough room to answer, but returned
`beta-epsilon-29` for the middle indexer instead of the expected
`beta-quartz-29`. That makes this a correctness miss, not an output-budget
artifact.

The same targeted 64K C=4 shape without MTP passed 12 of 12 requests at
`max_tokens=128` (`target_64k_c4_nomtp_max128_20260519034951`), although
elapsed time was slower because there was no speculative decode speedup.
Trying MTP=1 as a conservative fallback was not usable:
`target_64k_c4_mtp1_max128_20260519035535` failed all matrix requests after
EngineCore hit `RPC call to sample_tokens timed out`. The scheduler snapshot in
the failure log showed concurrent cached requests with
`scheduled_spec_decode_tokens` values of `[-1]`.

Decision: do not promote MTP=2 long-context C=4 as correctness-clean yet, and
do not use MTP=1 as the fallback. Keep no-MTP as the correctness control while
investigating whether the C=4 miss is in speculative acceptance, draft logits,
or scheduler interaction. PR-facing 64K/128K numbers should include repeated
failure counts or be limited to configurations that pass the fixed correctness
gate.

### Long-Context MTP Acceptance Isolation

Follow-up A/B runs kept the same targeted shape unless noted otherwise:
synthetic 64K prompt, C=4, repeat count 3, `max_tokens=128`, prefix cache
disabled, 131K max-model-len, 4096 max-num-batched-tokens, TP=2, MTP=2.

| Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Default MTP=2 | 12 | 2 | 32.069 s | 46.355 s | reject |
| No MTP | 12 | 0 | 32.648 s | 52.765 s | correctness control |
| MTP=2, CUDA graph disabled, GPU memory util 0.95 | 12 | 2 | 33.796 s | 48.885 s | reject |
| MTP=2, `disable_padded_drafter_batch=true` | 12 | 2 | 33.879 s | 49.023 s | reject |
| MTP=2, synthetic rejection, acceptance rates `[0.0, 0.0]` | 12 | 0 | 33.403 s | 54.542 s | diagnostic only |

The failed CUDA-graph-disabled run returned middle-marker variants such as
`основним` and `beta-tungsten-29`; the failed padded-drafter-disabled run
again returned `beta-epsilon-29`. Both still missed `beta-quartz-29`, so
CUDA graph capture, async scheduling, and the padded drafter batch are not
sufficient root causes.

The synthetic-rejection run is the important narrowing result. It forced a
zero acceptance rate while still running MTP=2 target verification, and it
passed all 12 requests. That means the first target verification position is
correct for this shape; the correctness miss appears only when later draft
tokens are accepted and the request advances along the multi-token MTP
verification trajectory. Do not promote synthetic rejection as an optimization:
it removes the MTP speedup and exists only as a diagnostic control.

Additional 62K-token runs narrowed the active failure boundary:

| Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| MTP=2, C=1 | 3 | 0 | 13.083 s | 13.616 s | pass |
| MTP=2, C=2 | 6 | 0 | 20.237 s | 27.011 s | pass |
| MTP=2, C=3 | 9 | 1 | 27.586 s | 39.729 s | fail |

This confirms the active bug is not single-stream long-context retrieval. It
starts once the small-concurrency batch reaches about three concurrent
long-context requests.

One targeted code experiment forced DeepSeek V4 sparse indexer decode away
from the native `(B, next_n)` path and into the flattened decode path for
multi-token spec decode. It did not fix the correctness miss:

| Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Flattened indexer decode, C=3 | 9 | 2 | 27.228 s | 39.204 s | reject |
| Flattened indexer decode, C=4 | 12 | 1 | 34.497 s | 49.254 s | reject |

The code change was removed. The failure is therefore not explained solely by
the native sparse-indexer multi-token decode layout.

Request-level tracing of a failing C=3 run provided a more precise location.
The failed request answered `beta-cobalt-29` instead of `beta-quartz-29`. At
the divergence step, the draft proposed token ids for `beta-qu...`; target
verification accepted the first token `beta` but rejected the second draft
token and selected the token for `-c` instead. The next step then continued
with `obalt-29`.

That trace means the failure is not an unchecked draft-token acceptance. The
target verification logits are already wrong for the second verification
position after the first accepted draft token, in a small-concurrency
long-context batch. Keep the investigation on target multi-token verification:
positions, slot mapping, KV writes/reads, and sparse context selection for
query positions after the first accepted token.

Additional A/B checks on the current branch did not change the decision:

| Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `VLLM_TRITON_MLA_SPARSE_MATMUL_DECODE=0`, C=3 | 9 | 1 | 28.782 s | 41.508 s | reject |
| `--no-async-scheduling`, C=3 | 9 | 2 | 28.862 s | 41.764 s | reject |
| `--enforce-eager`, GPU memory util 0.90, C=3 | 9 | 2 | 29.053 s | 42.794 s | reject |

Forcing sparse MLA fully off was not a valid comparison on this checkout
because the required FlashMLA extension was not available. An eager run at the
normal 0.985 GPU-memory budget also failed startup with Triton out-of-memory
during warmup; the lower-memory eager run above did start and still reproduced
the retrieval miss. These results make the materialized-matmul sparse decode
path, async scheduling, and CUDA graph capture insufficient explanations.

One setup mistake is also recorded so it is not reused as evidence: a
CUDA-graph-disabled run with line count 1000 passed 12 of 12 requests, but the
prompt was only about 31K tokens, not the intended 64K shape.

### Long-Context MTP History Check

The 64K C=4 `max_tokens=128` correctness miss was checked against historical
vLLM points to avoid blaming the latest rebase or the later rowwise/logits
kernel work without evidence.

| Ref / Variant | Requests | Failures | Mean TTFT | Mean Elapsed | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| pre-rebase HEAD `055e9f43c` | 12 | 1 | 31.910 s | 45.563 s | fail, predates latest rebase |
| `5fb7de094` MTP scheduling, first run | 12 | 0 | 99.204 s | 141.632 s | insufficient sample |
| `5fb7de094` MTP scheduling, repeat count 6 | 24 | 3 | 99.554 s | 142.650 s | fail, earliest comparable bad point |
| `215dfa944` MTP warmup | 12 | 2 | 99.312 s | 142.238 s | fail |
| `f05821715` dense FP8 configs | 12 | 3 | 97.508 s | 139.426 s | fail |
| `d26d266c8` adaptive MQA logits `BLOCK_M` | 12 | 1 | 97.586 s | 139.013 s | fail |
| `b301fd8ae` multi-request warmup coverage | 12 | 1 | 97.400 s | 139.976 s | fail |
| `be62c58ed` rowwise paged-MQA restore | 12 | 1 | 97.288 s | 138.789 s | fail |
| current, sparse MLA warmup disabled | 12 | 2 | 33.879 s | 48.814 s | fail |

All failures had the same shape: the model answered the first and final
sentinels correctly but returned a nearby or unrelated middle sentinel instead
of `beta-quartz-29`. The historical run against the pre-rebase HEAD reproduces
the miss, so the latest rebase is not the root cause. The wider repeat on
`5fb7de094` also reproduces the miss, so later rowwise/top-k/logits commits are
not the sole cause, even if they may affect speed or failure rate.

The direct parent `1ed872206` is not a valid good/bad comparison for this
shape: it fails engine startup with an Inductor assertion while compiling the
MTP model (`LayerName` passed where a Tensor is expected). Treat
`5fb7de094` as the earliest comparable failing point currently available.

Disabling the DeepSeek V4 sparse MLA warmup on the current branch did not fix
the correctness miss. That makes startup warmup-state pollution an insufficient
explanation. Keep the investigation centered on the accepted multi-token MTP
scheduling/verification trajectory, using no-MTP and synthetic-reject-0 as
controls.

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
  - 64K/128K long-context latency at C=1/2/3/4 must not regress,
  - GSM8K `exact_match_flexible` must not drop below the fixed baseline,
  - correctness/unit smoke for the touched vLLM path must pass.

## Near-Term Work Queue

1. Treat the MTP=2 64K C=3/4 correctness miss as a bug rather than continuing
   broad history bisection. The next useful evidence is target-verification
   metadata at the failed second verification position: input token ids,
   positions, slot mapping, logits indices, KV cache slots, and sparse top-k
   context indices, with no-MTP and synthetic-reject-0 as controls.
2. Profile the active FP8 MQA logits Triton path with NCU on representative
   late-context 128K launches.
3. Sweep small tile/register-pressure changes around `BLOCK_M`, `BLOCK_N`,
   `BLOCK_H`, and `num_warps`, keeping each candidate small enough to revert.
4. Gate candidates with the short + 64K/128K + GSM8K matrix before promotion.
5. After prefill is stable, move to paged MQA decode and small-M GEMM/BMM
   experiments for long-context multi-turn latency.
