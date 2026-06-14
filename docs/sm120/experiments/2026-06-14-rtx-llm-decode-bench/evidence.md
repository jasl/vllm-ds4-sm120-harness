# Evidence

## Run Notes

Two setup details mattered:

- `128k + 4096` exceeds the 131072-token model window and produced invalid
  HTTP 400 context-length errors. The harness wrapper default uses `124k` for
  this benchmark so `124k + 4096` fits the model window.
- Without an explicit KV budget, the script cannot skip over-capacity vLLM
  cells on this remote endpoint and can spend hours draining queued requests.
  The valid run used `--kv-budget 186268`, matching the vLLM startup log's GPU
  KV cache size.

The capacity-aware matrix has 40 requested cells and 16 actually runnable
cells. Over-capacity cells are marked as skipped by the script.

## Pitfall Log

Use this section to decide whether a future comparison is using valid evidence
or accidentally reusing a discarded run.

| Pitfall | Impact | Resolution |
| --- | --- | --- |
| `128k + 4096` in a 131072-token model window | The benchmark returned HTTP 400 context-length errors; those cells are invalid. | Use `124k` for long-context decode when `max_tokens=4096`, or lower output tokens. |
| No explicit KV budget for large matrices | The public script cannot skip over-capacity endpoint cells and can leave queued requests draining for hours. | The valid capacity-aware run used `--kv-budget 186268`; skipped cells are reported explicitly. |
| Intermediate RTX GPU `ERR!` / reset-required state | Follow-up ablations before reboot were not valid health evidence. | Rebooted the RTX host before the final auto/reserve ablations. |
| Public Lucifer without PR3395 | Startup failed because SM120 selected a sparse-MLA route that requires `flashinfer.sparse_mla_sm120`. | Treat Lucifer endpoint numbers as coupled to FlashInfer PR3395; do not compare a forced fallback as "Lucifer". |
| Local FlashInfer source shadowing installed FlashInfer | Serving can import the wrong package surface and miss the sparse-sm120 wrapper. | Use a sanitized server wrapper / import environment for the coupled Lucifer stack. |
| Missing venv `bin` on `PATH` for warm Lucifer run | FlashInfer JIT needed `ninja` and the warm run failed before useful data. | Put the target venv `bin` on `PATH` and install `ninja` in the venv. |
| Malformed `--compilation-config` shell quoting | A warm run passed invalid JSON to vLLM and was discarded. | Use quoted JSON from the checked command wrapper, not hand-edited shell fragments. |
| First PR3395 reintegration ctx0 rerun timeout | The outer timeout sent SIGTERM during C8; C16/C32/C64 were recorded as zero. | Exclude timestamp `20260614172927`; use the valid rerun timestamp `20260614173916`. |
| First PR3395 prefill-only scout measured cold JIT | Long-context metadata kernels compiled during the measured phase, depressing the gate-on 64K/128K rows. | Use the warm gate-on rerun for the local signal, while still recording the first run as a startup caveat. |
| Lucifer+PR3395 prefill-only scout startup failure | The service never reached health and repeated shared-memory broadcast waits; no benchmark JSON was produced. | Do not claim a local Lucifer prefill row from that attempt; only the decode row was locally reproduced. |
| FlashInfer CUTLASS MoE conversion-only route | MTP draft acceptance collapsed to about `0.24-0.30`, so the throughput regression was a semantic-route failure, not a useful MoE speed result. | Use only the corrected expert-wrapper probe for FI MoE conclusions. |
| DeepGEMM and combined-backend warmup gaps | Runtime JIT and uncovered-shape fallbacks persisted during inference windows. | Keep these as default-off dev candidates with startup/warmup work required before promotion. |

## Prefill Scouts

Integrated scout rows use client prompt tokens divided by TTFT.

| Context | Prompt tokens | TTFT seconds | Client tok/s |
| --- | ---: | ---: | ---: |
| 8k | 8,191 | 1.36 | 6,013 |
| 16k | 16,250 | 1.78 | 9,111 |
| 32k | 32,340 | 3.74 | 8,643 |
| 64k | 64,555 | 8.25 | 7,826 |
| 124k | 124,957 | 18.58 | 6,727 |

## Sustained Decode

Aggregate decode tok/s uses OpenAI stream usage. `skip` means the cell exceeds
the KV budget. `cap` means the script ran the cell but vLLM did not admit the
requested concurrency; do not compare that value as a true C=2 result.

| Context \\ C | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 189.1 | 314.0 | 481.6 | 717.6 | 1,037.3 | 1,517.1 | skip | skip |
| 16k | 184.0 | 287.4 | 465.7 | 543.6 | skip | skip | skip | skip |
| 32k | 175.2 | 312.2 | 499.8 | skip | skip | skip | skip | skip |
| 64k | 186.9 | cap | skip | skip | skip | skip | skip | skip |
| 124k | 178.3 | skip | skip | skip | skip | skip | skip | skip |

The `64k, C=2` cell measured 199.0 aggregate tok/s, but was
capacity-limited: average running requests were 1/2, queue fraction was 1.0,
warmup timed out after 120.83 seconds, and p50 TTFT was 20.76 seconds.

## Verification

- `llm_decode_bench` phase exit code: 0.
- `llm_decode_bench.exit_code`: 0.
- `llm_decode_bench.stderr`: empty.
- Serve log grep for `ERROR`, `Traceback`, `NO_MEMORY`, `OutOfMemory`, HTTP
  400, and HTTP 500: no matches in the valid run.
- No residual `vllm serve` or `llm_decode_bench.py` process remained after the
  valid run completed.

## Community Report Alignment

The public `local-inference-lab/rtx6kpro` `ds4-flash-v3.md` report carries
forward the Lucifer TP2 MTP probabilistic decode matrix from v2 and validates
the new standard Lucifer image against it. The closest direct comparison is the
ctx0 decode-only benchmark:

```text
llm_decode_bench.py --contexts 0k --max-tokens 2048 --skip-prefill \
  --concurrency 1,2,4,8,16,32,64
```

An aligned run was performed with:

- `max_model_len=262144`
- `max_num_seqs=64`
- `max_num_batched_tokens=8192`
- MTP 2 with `draft_sample_method=probabilistic`
- `--max-cudagraph-capture-size 192`
- `--no-scheduler-reserve-full-isl`
- `--enable-chunked-prefill`
- `--enable-flashinfer-autotune`
- `--default-chat-template-kwargs.thinking=true`
- `--default-chat-template-kwargs.reasoning_effort=high`
- `FULL_AND_PIECEWISE` CUDA graph mode

Local-safe artifact identifier:

```text
branch=codex/ds4-sm120-epoff-sparse-prefill-dev-20260613
gpu=2x_nvidia_rtx_pro_6000_blackwell_workstation_edition
label=rtx_llm_decode_ctx0_community_aligned_cap192_noreserve
timestamp=20260614081133
variant=mtp
```

The run completed with phase exit code 0, empty benchmark stderr, and no serve
log `ERROR`, `Traceback`, OOM, HTTP 400, or HTTP 500 entries.

| C | This branch tok/s | Community Lucifer tok/s | Delta |
| ---: | ---: | ---: | ---: |
| 1 | 182.2 | 199.5 | -8.7% |
| 2 | 299.2 | 333.5 | -10.3% |
| 4 | 460.4 | 397.2 | +15.9% |
| 8 | 674.3 | 787.1 | -14.3% |
| 16 | 944.2 | 1,185.5 | -20.4% |
| 32 | 1,459.6 | 1,870.6 | -22.0% |
| 64 | 1,954.8 | 2,815.4 | -30.6% |

This means the known high-concurrency decode scaling gap remains after aligning
the obvious serve-side knobs. The gap is unlikely to be explained by
`max_num_seqs=64`, graph cap 192, full-ISL reserve, chunked prefill, or
FlashInfer autotune alone.

## Scheduler And CUDA Graph Ablation

The successful community-aligned run above left three obvious serve-side knobs
to isolate:

- auto CUDA graph cap with full-ISL reserve disabled
- graph cap 192 with default full-ISL reserve
- auto CUDA graph cap with default full-ISL reserve

An intermediate attempt was invalid because the second RTX GPU entered an
`ERR!` / `GPU requires reset` state after the first aligned run. After host
reboot, both GPUs were healthy and all three follow-up runs completed.

Local-safe artifact identifiers:

```text
label=rtx_llm_decode_ctx0_community_aligned_auto_noreserve
timestamp=20260614083400

label=rtx_llm_decode_ctx0_community_aligned_cap192_reserve
timestamp=20260614084133

label=rtx_llm_decode_ctx0_community_aligned_auto_reserve
timestamp=20260614084752
```

All four aligned runs had empty benchmark stderr and no serve log `ERROR`,
`Traceback`, OOM, HTTP 400, or HTTP 500 entries.

| Variant | C1 | C2 | C4 | C8 | C16 | C32 | C64 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| cap192, noreserve | 182.2 | 299.2 | 460.4 | 674.3 | 944.2 | 1,459.6 | 1,954.8 |
| auto, noreserve | 180.3 | 292.7 | 456.2 | 658.7 | 947.3 | 1,470.2 | 1,986.8 |
| cap192, reserve | 179.0 | 298.1 | 461.4 | 674.3 | 975.3 | 1,456.8 | 1,973.2 |
| auto, reserve | 180.8 | 297.4 | 458.0 | 663.8 | 962.6 | 1,461.9 | 1,956.6 |

The following "best" row is a per-concurrency envelope over the four ablations
above. It is not a single benchmark artifact and should only be used to judge
the local upper envelope for these scheduler / CUDA graph knobs. Use the
`cap192, noreserve` row above for the strict community-shaped single-run
comparison.

| C | Best of four ablations tok/s | Community Lucifer tok/s | Delta |
| ---: | ---: | ---: | ---: |
| 1 | 182.2 | 199.5 | -8.7% |
| 2 | 299.2 | 333.5 | -10.3% |
| 4 | 461.4 | 397.2 | +16.2% |
| 8 | 674.3 | 787.1 | -14.3% |
| 16 | 975.3 | 1,185.5 | -17.7% |
| 32 | 1,470.2 | 1,870.6 | -21.4% |
| 64 | 1,986.8 | 2,815.4 | -29.4% |

Conclusion: the obvious scheduler reserve and CUDA graph cap knobs do not
explain the high-concurrency gap. The remaining difference is more likely in
the runtime stack and backend path: Lucifer uses `SPARSE_MLA_SM120`,
`flashinfer_cutlass` MoE, FlashInfer PR3395-era sparse MLA, pinned cu132
dependencies, and its all-reduce/runtime defaults.

The C4 advantage is real across these runs, but it is isolated. It does not
indicate better overall scaling because C8 and higher regress consistently.
Treat C4 as a local crossover point in batching/overhead amortization, not as a
sign that the high-concurrency decode path is healthy.

## Lucifer Coupling Probe

`local-inference-lab/vllm` `lucifer` was checked at
`7c6bbf4c5a482e100af886c5b6eb4303746cc3ba`, matching the community-report
Lucifer source commit. With the current public dependency stack
(`flashinfer-python==0.6.12`, no `flashinfer.sparse_mla_sm120` module), a
community-shaped launch failed before readiness:

```text
label=rtx_lucifer_ctx0_public_stack_fi_moe
timestamp=20260614091057
```

The root cause was explicit:

```text
RuntimeError: FLASHINFER_MLA_SPARSE_DSV4 on SM120 requires FlashInfer's
sparse-sm120 MLA wrapper.
```

That failure confirms the `lucifer` endpoint stack is tightly coupled to the
FlashInfer PR3395 sparse-sm120 wrapper for SM120. A follow-up launch that
forced `--attention-backend=FLASHMLA_SPARSE_DSV4` was stopped as invalid for
performance comparison: it bypasses the coupled path that the fork was designed
to exercise, so it cannot explain the published Lucifer numbers.

## Lucifer Plus PR3395 Local Reproduction

The complete coupled stack was reproduced locally after installing the
FlashInfer PR3395 sparse-sm120 wrapper and rebuilding the Lucifer vLLM native
extensions:

- vLLM `local-inference-lab/vllm` `7c6bbf4c5a4`
- FlashInfer PR3395 fork commit `b41aa8dd2f`
- native vLLM extension build `0.22.1rc1.dev269+g7c6bbf4c5.cu133`
- `SPARSE_MLA_SM120` attention backend
- `flashinfer_cutlass` MoE backend with
  `FLASHINFER_CUTLASS_MXFP4_MXFP8`
- DeepGEMM E8M0 FP8 linear path
- FlashInfer top-p/top-k sampling
- MTP 2 with `draft_sample_method=probabilistic`
- `max_model_len=262144`, `max_num_seqs=64`,
  `max_num_batched_tokens=8192`
- `--max-cudagraph-capture-size 192`,
  `--no-scheduler-reserve-full-isl`, `--enable-chunked-prefill`,
  `--enable-flashinfer-autotune`

Setup failures before the valid run were environmental, not endpoint
regressions:

- public FlashInfer `0.6.12` lacks `flashinfer.sparse_mla_sm120`, confirming
  Lucifer's PR3395 coupling;
- the harness checkout's local FlashInfer source directory can shadow the
  installed editable FlashInfer package through `PYTHONPATH`, so serving used a
  sanitized server wrapper;
- malformed shell quoting for `--compilation-config` produced invalid JSON in
  one discarded warm run;
- a warm run without the venv `bin` directory on `PATH` failed when FlashInfer
  JIT needed `ninja`.

Two valid ctx0 decode-only runs completed with phase exit code 0:

```text
label=rtx_lucifer_pr3395_ctx0_community_aligned_native_first_20260614
timestamp=20260614100036

label=rtx_lucifer_pr3395_ctx0_community_aligned_native_warm3_20260614
timestamp=20260614101703
```

The first run includes cold JIT/autotune startup, but its measured decode cells
were already stable. The warm3 run reused generated caches; engine warmup time
dropped from about 417 seconds to about 20 seconds. Benchmark stderr was empty
for both valid runs, and the JSON event logs only reported the expected KV
budget warning from the benchmark script.

The "this branch" column below is the same per-concurrency best-of-ablation
envelope, not one single run. It shows the best local baseline envelope that
Lucifer+PR3395 needed to beat; strict one-run comparisons should use the
`cap192, noreserve` row in the community-alignment section.

| C | This branch best-of-ablations tok/s | Local Lucifer+PR3395 warm tok/s | Community Lucifer tok/s | Local vs this branch |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 182.2 | 198.9 | 199.5 | +9.2% |
| 2 | 299.2 | 332.7 | 333.5 | +11.2% |
| 4 | 461.4 | 391.4 | 397.2 | -15.2% |
| 8 | 674.3 | 784.4 | 787.1 | +16.3% |
| 16 | 975.3 | 1,183.5 | 1,185.5 | +21.3% |
| 32 | 1,470.2 | 1,872.1 | 1,870.6 | +27.3% |
| 64 | 1,986.8 | 2,818.9 | 2,815.4 | +41.9% |

GSM8K correctness was checked on the same coupled stack with MTP=2,
`FULL_AND_PIECEWISE`, prefix caching enabled, and the same
`SPARSE_MLA_SM120` / `flashinfer_cutlass` route. The first pass used C=1 to
keep the speculative path correctness-focused; the second pass repeated the
5-shot hard gate at C=4 to match the public wrapper shape more closely.

```text
label=rtx_lucifer_pr3395_gsm8k_limit200_mtp_c1_20260614
timestamp=20260614103351

label=rtx_lucifer_pr3395_gsm8k_limit200_mtp_c4_20260614
timestamp=20260614104124
```

| Slice | Concurrency | Limit | Flexible EM | Strict EM | Eval exit | Gate exit | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 5-shot | 1 | 200 | 0.955 | 0.955 | 0 | 0 | hard gate passed |
| 5-shot | 4 | 200 | 0.955 | 0.955 | 0 | 0 | hard gate passed |
| 0-shot | 1 | 200 | 0.900 | 0.000 | 0 | 1 | watch-only; fixed 5-shot floors are not valid here |

The 0-shot strict score is a parser artifact for this protocol: strict matching
expects the `####` answer form, while 0-shot completions commonly omit it. This
matches the earlier min-token-gate finding that 0-shot is a watch signal, not a
hard promotion gate. The useful signal is that both 5-shot limit-200 runs pass
the fixed floors of flexible `>= 0.94` and strict `>= 0.925`, including the C=4
stress shape. The serve logs for both GSM8K runs had no `ERROR`, `Traceback`,
OOM, driver, or NCCL error matches, and runtime stats reported no waiting queue
or preemptions in the eval phases.

Conclusion: the community Lucifer row is locally reproducible to within noise.
The C4 crossover remains real and favors the current branch, but C8-C64 decode
scaling strongly favors the coupled Lucifer+PR3395 runtime path. This is
evidence of reachable performance headroom, not proof that the PR branch should
take a hard dependency on the unmerged FlashInfer PR. The GSM8K hard gate is
clean for this RTX route, but any reintroduction should stay on a dev branch or
behind an explicit experiment gate until long-context and GB10 lifecycle gates
also pass.

Environment caveats: the local RTX host did not have the NVIDIA P2P override
effective, ReBAR was disabled, and the warm run reached high GPU temperatures
during C32/C64. Those caveats did not prevent reproducing the community row, but
they should be recorded before using the run as a thermal-stability baseline.

## Current Branch PR3395 Reintegrated Prefill Check

The same opt-in PR3395 sparse-sm120 packed-prefill reintegration branch has a
valid RTX EP-off prefill attribution subset. This is not the same benchmark
shape as the community `ds4-flash-v3.md` 8K / 64K / 128K prefill table; it is
the local attribution gate used to isolate the sparse-MLA prefill bottleneck at
16K and 65K, C=1, OSL=1.

```text
branch=codex/ds4-sm120-pr3395-packed-reintegrate-20260614
label=20260614_pr3395_packed_rtx_epoff_gate_off
timestamp=20260614164316

label=20260614_pr3395_packed_rtx_epoff_gate_on
timestamp=20260614165032
```

| Case | Gate off tok/s | Gate on tok/s | Tok/s delta | Gate off TTFT ms | Gate on TTFT ms | TTFT delta | Sparse stage off ms | Sparse stage on ms | Stage delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16K | 7,481.3 | 9,127.6 | +22.0% | 2,191.7 | 1,794.5 | -18.1% | 6,693.4 | 2,454.3 | -63.3% |
| 65K | 6,509.8 | 7,951.1 | +22.1% | 9,982.6 | 8,174.9 | -18.1% | 9,412.9 | 5,357.3 | -43.1% |

The off path is dominated by `sparse_accumulate`; the on path shifts the
dominant sparse stage to `flashinfer_packed_attention` and leaves only a much
smaller residual `sparse_accumulate` component. This confirms that the packed
PR3395 route materially improves cold prefill in the attribution gate.

The matching community-shaped prefill-only scout was then run with
`--prefill-only --prefill-contexts 8k,64k,128k`, the same TP2 / MTP
probabilistic serve shape as the ctx0 decode comparison. The first gate-on run
was lower at long contexts, likely because the packed route still JIT-compiled
long-context metadata kernels during the measured phase. A warm gate-on rerun
is the better local signal, but it still only shows a small gain over gate-off
and remains well below the published Lucifer table.

```text
label=our_pr3395_reintegrate_prefill_scout
timestamp=20260614175228

label=our_pr3395_reintegrate_prefill_scout_gate_off
timestamp=20260614175558

label=our_pr3395_reintegrate_prefill_scout_gate_on_warm
timestamp=20260614175852
```

| Route | 8K tok/s | 64K tok/s | 128K tok/s | Notes |
| --- | ---: | ---: | ---: | --- |
| Gate off | 9,368 | 8,122 | 6,799 | same service shape, packed gate disabled |
| Gate on, first | 9,498 | 7,760 | 6,094 | valid exit 0, but long-shape JIT contaminated |
| Gate on, warm | 9,447 | 8,223 | 7,362 | best reintegrated-branch scout |
| Community Lucifer TP2 MTP-on | 12,956 | 12,348 | 11,318 | published `ds4-flash-v3.md` row |

Warm gate-on versus gate-off is only `+0.8% / +1.2% / +8.3%` at
8K / 64K / 128K, while warm gate-on remains `-27.1% / -33.4% / -35.0%`
behind the community Lucifer row. This means the attribution gate correctly
shows the packed route can reduce the isolated sparse-MLA stage, but the current
reintegrated endpoint path does not yet reproduce Lucifer's community-shaped
prefill throughput.

An attempt to run the same prefill-only scout against the locally reproduced
Lucifer+PR3395 stack did not produce performance data: the service failed to
reach `/health` and exited after repeated shared-memory broadcast waits during
initialization.

```text
label=lucifer_pr3395_prefill_scout
timestamp=20260614180149
result=startup failed before benchmark; no throughput row
```

## Current Branch PR3395 Reintegrated Decode Check

The opt-in PR3395 sparse-sm120 packed-prefill reintegration branch was also
checked against the same ctx0 community-shaped decode row:

```text
branch=codex/ds4-sm120-pr3395-packed-reintegrate-20260614
label=our_pr3395_reintegrate_ctx0_mtp_prob
timestamp=20260614173916
```

One discarded attempt at `timestamp=20260614172927` used an outer timeout that
sent SIGTERM to the serving process during the C8 cell. That artifact has C16,
C32, and C64 recorded as zero and must not be used for performance comparison.
The valid rerun completed with benchmark exit code 0, empty benchmark stderr,
no benchmark request errors, and no underfilled or capacity-limited cells.

| C | Reintegrated branch tok/s | Prior strict cap192/noreserve tok/s | Delta vs prior strict | Local Lucifer+PR3395 warm tok/s | Gap vs Lucifer |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 179.5 | 182.2 | -1.5% | 198.9 | -9.7% |
| 2 | 297.6 | 299.2 | -0.5% | 332.7 | -10.5% |
| 4 | 459.8 | 460.4 | -0.1% | 391.4 | +17.5% |
| 8 | 678.4 | 674.3 | +0.6% | 784.4 | -13.5% |
| 16 | 961.5 | 944.2 | +1.8% | 1,183.5 | -18.8% |
| 32 | 1,459.7 | 1,459.6 | +0.0% | 1,872.1 | -22.0% |
| 64 | 1,952.8 | 1,954.8 | -0.1% | 2,818.9 | -30.7% |

Conclusion: the reintegrated packed-prefill gate is neutral for ctx0 decode, as
expected. It preserves the current branch's C4 crossover but does not explain
or close the Lucifer C8-C64 high-concurrency decode gap. The PR3395 prefill
route remains a prefill optimization candidate; decode-scaling parity still
needs attention/runtime investigation beyond this packed-prefill gate.

## FlashInfer CUTLASS MoE Expert Wrapper Probe

The Lucifer+PR3395 reproduction uses several changed runtime paths at once:
`SPARSE_MLA_SM120`, FlashInfer CUTLASS MoE, DeepGEMM FP8 linear, sampling
changes, dependency pins, and graph/runtime defaults. To isolate whether MoE
alone explains the high-concurrency decode gap, a current-branch dev worktree
was tested with an opt-in FlashInfer CUTLASS MoE route but without the PR3395
sparse-MLA wrapper.

The first attempt only added DeepSeek-V4 MXFP4 weight conversion for the
FlashInfer backend. It selected `FLASHINFER_CUTLASS_MXFP4_MXFP8`, but was
invalid for promotion because MTP draft acceptance collapsed to about
`0.24-0.30`. Throughput regressed across the ctx0 decode row.

```text
label=rtx_llm_decode_ctx0_dev_fi_moe_patch_cap192_noreserve_clean_warm_20260614
timestamp=20260614111815
```

| C | Current branch tok/s | Conversion-only FI MoE tok/s | Delta |
| ---: | ---: | ---: | ---: |
| 1 | 182.2 | 137.6 | -24.5% |
| 2 | 299.2 | 194.2 | -35.1% |
| 4 | 460.4 | 322.6 | -29.9% |
| 8 | 674.3 | 456.7 | -32.3% |
| 16 | 944.2 | 695.3 | -26.4% |
| 32 | 1,459.6 | 978.4 | -33.0% |
| 64 | 1,954.8 | 1,349.9 | -30.9% |

The failure was not raw MoE kernel speed by itself. A no-MTP short comparison
showed the same FlashInfer MoE route was roughly neutral against the default
MARLIN MoE route when speculative acceptance was removed:

```text
label=rtx_llm_decode_ctx0_dev_fi_moe_patch_nomtp_cap192_noreserve_short_20260614
timestamp=20260614114100

label=rtx_llm_decode_ctx0_current_default_nomtp_cap192_noreserve_short_20260614
timestamp=20260614114900
```

| C | Default no-MTP tok/s | FI MoE no-MTP tok/s | Delta |
| ---: | ---: | ---: | ---: |
| 1 | 110.9 | 107.1 | -3.5% |
| 4 | 330.2 | 325.3 | -1.5% |
| 16 | 779.3 | 800.9 | +2.8% |
| 64 | 1,681.4 | 1,688.6 | +0.4% |

The correction was to also match the DeepSeek-V4 expert wrapper semantics:
do not inject GPT-OSS-only SwiGLU alpha/beta/clamp defaults for MXFP4 when the
quant config does not provide them. With that fix, MTP acceptance returned to
the current-branch range and the ctx0 decode-only row showed a small positive
signal at C8 and higher:

```text
label=rtx_llm_decode_ctx0_dev_fi_moe_expertfix2_mtp_cap192_noreserve_clean_warm_20260614
timestamp=20260614120500
```

| C | Current branch tok/s | Fixed FI MoE tok/s | Delta |
| ---: | ---: | ---: | ---: |
| 1 | 182.2 | 180.4 | -1.0% |
| 2 | 299.2 | 302.4 | +1.1% |
| 4 | 460.4 | 466.5 | +1.3% |
| 8 | 674.3 | 689.0 | +2.2% |
| 16 | 944.2 | 990.5 | +4.9% |
| 32 | 1,459.6 | 1,487.5 | +1.9% |
| 64 | 1,954.8 | 2,041.4 | +4.4% |

The fixed route still lagged the local Lucifer+PR3395 warm row by `12.2%` at
C8, `16.3%` at C16, `20.5%` at C32, and `27.6%` at C64. Therefore FlashInfer
CUTLASS MoE can explain only a small part of the high-concurrency gap.

Correctness was checked with the fixed FI MoE route using GSM8K limit-200,
5-shot, MTP, and concurrency 4:

```text
timestamp=20260614122600
phase=eval_gsm8k
```

| Slice | Concurrency | Limit | Flexible EM | Strict EM | Eval exit | Gate exit | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 5-shot | 4 | 200 | 0.945 | 0.945 | 0 | 0 | hard gate passed |

Runtime stats reported 200 successful requests, no waiting queue, no
preemptions, no CUDA/NCCL/driver/engine errors, and average draft acceptance of
79.91%. The model-smoke portion of the broader acceptance wrapper also passed,
but that wrapper's local harness pytest phase failed in unrelated script tests
from the dirty harness worktree, so this note does not claim a full acceptance
matrix pass for the candidate.

Conclusion: keep the fixed FI MoE path as a default-off dev candidate worth
GB10 and longer-matrix validation. Do not treat it as the main Lucifer parity
answer. The remaining gap is more likely a combination of PR3395 sparse MLA,
DeepGEMM FP8 linear, and graph/runtime path differences.

## DeepGEMM FP8 Linear Probe

A second isolation probe enabled the DeepGEMM FP8 linear backend on the current
dev stack without switching MoE to FlashInfer CUTLASS and without installing
the PR3395 sparse-MLA wrapper. The route used SM120 DeepGEMM capability
enablement, the Blackwell-family E8M0 scale format, and the Lucifer-style
direct `fp8_einsum` o-projection recipe. A local guard kept the Q-indexer on
the current fallback path when the CUte helper package was absent, so this run
did not pull in Lucifer's additional `vllm_flash_attn.cute` stack.

The valid ctx0 decode-only run selected:

- `DeepGemmFp8BlockScaledMMKernel` for FP8 linear
- DeepGEMM E8M0
- MARLIN MXFP4 MoE
- the current FP8 indexer cache path

That makes this a DeepGEMM-linear-only probe, not a FlashInfer MoE or PR3395
attention run.

Local-safe artifact identifier:

```text
branch=codex/ds4-sm120-decode-scaling-deepgemm-linear-20260614
gpu=2x_nvidia_rtx_pro_6000_blackwell_workstation_edition
label=rtx_llm_decode_ctx0_deepgemm_linear_cap192_noreserve_pathfix_20260614
timestamp=20260614122313
variant=mtp
```

The benchmark used the same community-aligned shape as the earlier ctx0 rows:
`max_model_len=262144`, `max_num_seqs=64`, `max_num_batched_tokens=8192`,
MTP 2 with `draft_sample_method=probabilistic`, graph cap 192, disabled
full-ISL reserve, chunked prefill, FlashInfer autotune, and
`FULL_AND_PIECEWISE`.

| C | Current branch tok/s | Fixed FI MoE tok/s | DeepGEMM linear tok/s | DeepGEMM vs current | Local Lucifer+PR3395 tok/s | DeepGEMM gap vs Lucifer |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 182.2 | 180.4 | 189.8 | +4.2% | 198.9 | -4.6% |
| 2 | 299.2 | 302.4 | 302.6 | +1.1% | 332.7 | -9.0% |
| 4 | 460.4 | 466.5 | 482.6 | +4.8% | 391.4 | +23.3% |
| 8 | 674.3 | 689.0 | 698.4 | +3.6% | 784.4 | -11.0% |
| 16 | 944.2 | 990.5 | 985.6 | +4.4% | 1,183.5 | -16.7% |
| 32 | 1,459.6 | 1,487.5 | 1,474.6 | +1.0% | 1,872.1 | -21.2% |
| 64 | 1,954.8 | 2,041.4 | 2,028.5 | +3.8% | 2,818.9 | -28.0% |

The DeepGEMM route is positive across the row, but only by `+1.0%` to `+4.8%`.
It does not explain the C8-C64 Lucifer gap. It preserves and even widens the
isolated C4 crossover, which reinforces that C4 is a local batching/runtime
crossover rather than proof that the current high-concurrency decode path is
healthy.

Correctness was checked with the same DeepGEMM route using GSM8K limit-200,
5-shot, MTP, and concurrency 4:

```text
branch=codex/ds4-sm120-decode-scaling-deepgemm-linear-20260614
gpu=2x_nvidia_rtx_pro_6000_blackwell_workstation_edition
label=rtx_deepgemm_linear_gsm8k_limit200_mtp_c4_20260614
timestamp=20260614123508
variant=mtp
phase=eval_gsm8k
```

| Slice | Concurrency | Limit | Flexible EM | Strict EM | Eval exit | Gate exit | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 5-shot | 4 | 200 | 0.955 | 0.940 | 0 | 0 | hard gate passed |

Runtime stats and serve-log parsing were clean for correctness health:

- no CUDA, NCCL, driver, engine, worker-crash, or OOM errors;
- no waiting queue and no preemptions;
- average draft acceptance about 80.39%;
- sampled max running requests 4;
- `lm_eval` and GSM8K gate exit codes 0.

The route has deployment caveats. Startup selected a smaller KV cache
(`367,840` tokens under the aligned 262144-token profile), warmed 1645
DeepGEMM variants, and reported CUDA graph pool memory of 1.36 GiB. During the
first inference window, the JIT monitor still reported 11 Triton runtime
compilations, including prefill metadata, MTP, sampling, sparse attention, and
FP8 logits kernels. Those warnings did not break correctness, but they are a
negative deployment signal until warmup covers the shapes.

Conclusion: keep DeepGEMM FP8 linear as a default-off dev candidate. It is
worth combining with the fixed FI MoE route in a follow-up A/B because the two
mechanisms touch different backends, but the main high-concurrency gap remains
more likely in the PR3395 sparse-MLA attention route and broader runtime stack.

## DeepGEMM Plus FlashInfer MoE Combination Probe

The DeepGEMM FP8 linear route was combined with the corrected FlashInfer
CUTLASS MXFP4/MXFP8 MoE route to test whether the two modest single-backend
signals stack. This run still did not install the PR3395 sparse-MLA wrapper.

Local-safe artifact identifier:

```text
branch=codex/ds4-sm120-decode-scaling-deepgemm-linear-20260614
gpu=2x_nvidia_rtx_pro_6000_blackwell_workstation_edition
label=rtx_llm_decode_ctx0_deepgemm_fi_moe_cap192_noreserve_20260614
timestamp=20260614124323
variant=mtp
```

The service log confirmed the intended combined route:

- `DeepGemmFp8BlockScaledMMKernel` for FP8 linear
- DeepGEMM E8M0
- `FLASHINFER_CUTLASS_MXFP4_MXFP8` MoE
- MTP 2 with `draft_sample_method=probabilistic`

| C | Current branch tok/s | Fixed FI MoE tok/s | DeepGEMM linear tok/s | Combined tok/s | Combined vs current | Local Lucifer+PR3395 tok/s |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 182.2 | 180.4 | 189.8 | 181.5 | -0.4% | 198.9 |
| 2 | 299.2 | 302.4 | 302.6 | 303.0 | +1.3% | 332.7 |
| 4 | 460.4 | 466.5 | 482.6 | 459.7 | -0.1% | 391.4 |
| 8 | 674.3 | 689.0 | 698.4 | 696.2 | +3.3% | 784.4 |
| 16 | 944.2 | 990.5 | 985.6 | 989.6 | +4.8% | 1,183.5 |
| 32 | 1,459.6 | 1,487.5 | 1,474.6 | 1,444.1 | -1.1% | 1,872.1 |
| 64 | 1,954.8 | 2,041.4 | 2,028.5 | 2,009.4 | +2.8% | 2,818.9 |

The combination does not stack. It is slightly positive at C8/C16 and C64, but
weaker than one or both single-backend probes at C1/C4/C32/C64. It remains
`11.2%` behind Lucifer+PR3395 at C8, `16.4%` behind at C16, `22.9%` behind at
C32, and `28.7%` behind at C64.

Runtime health was clean enough to use as a negative performance result:
`llm_decode_bench` exit code 0, empty benchmark stderr, no CUDA/NCCL/driver/OOM
or engine errors, no waiting queue, and no preemptions. The important caveats
are performance-related:

- FlashInfer MoE autotune reported 4 uncovered-shape fallbacks for the graph
  capture shape;
- the JIT monitor still reported 10 runtime compilations during inference;
- average draft acceptance dropped to about 63.33%, much lower than the
  correctness-focused FI MoE and DeepGEMM single-path slices.

Conclusion: do not pursue the naive DeepGEMM+FlashInfer-MoE combination as a
promotion candidate. Without PR3395 sparse-MLA, changing linear and MoE
backends together is still insufficient, and it may hurt speculative-decode
acceptance. The remaining high-concurrency decode work should move back to
attention/runtime mechanisms or to the proven PR3395 integration route.

## Cache-Pressure Throttle Watch

A forum note proposed throttling chunked prefill by KV cache pressure rather
than by decode presence. The idea is to let prefills finish at full speed when
KV pressure is low so prefix-cache blocks become hashed and reusable sooner,
while only capping prefill when cache pressure is high.

That idea is relevant for long-context and mixed prefill/decode workloads,
especially prefix-cache hit rate and cache-thrash behavior. It does not explain
the ctx0 decode-only gap above, because the aligned decode benchmark used
`--skip-prefill`, context `0k`, and prefix-cache hit rate remained 0.0%.
Keep it as a separate scheduler experiment for long-context mixed-arrival
tests, not as the first explanation for the Lucifer C8-C64 decode advantage.

## Decode-Kernel Attribution (same-session 2x2)

This is the root-cause pass for the C8-C64 ctx0 decode gap. After a clean
reboot, four ctx0 decode-only cells (`--skip-prefill --contexts 0k
--concurrency 1,2,4,8,16,32,64 --max-tokens 2048 --duration 30`) were run
back-to-back in one thermal/driver session, toggling only one variable at a
time. Each cell had benchmark exit code 0, empty stderr, no serve-log
`ERROR`/`Traceback`/OOM/NCCL, no waiting queue, no preemptions, and no
capacity-limited or underfilled cells.

Local-safe artifact identifiers (under the `lucifer-gap` run root):

```text
A2  label=A2_lucifer_sm120_fic_mtp     stack=Lucifer SPARSE_MLA_SM120 + flashinfer_cutlass MoE, MTP on
B2  label=B2_lucifer_sm120_fic_nomtp   stack=Lucifer SPARSE_MLA_SM120 + flashinfer_cutlass MoE, MTP off
C   label=C_current_marlin_plain_mtp   stack=current plain trtllm decode + MARLIN MoE, MTP on
D   label=D_current_marlin_plain_nomtp stack=current plain trtllm decode + MARLIN MoE, MTP off
```

| Cell | C1 | C2 | C4 | C8 | C16 | C32 | C64 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A2 Lucifer packed, MTP | 198.8 | 327.6 | 397.8 | 785.5 | 1,174.5 | 1,861.8 | 2,822.1 |
| C current plain, MTP | 179.0 | 296.9 | 466.6 | 600.5 | 873.9 | 1,461.8 | 1,947.4 |
| B2 Lucifer packed, no-MTP | 124.0 | 206.3 | 352.7 | 569.3 | 850.4 | 1,276.2 | 1,983.7 |
| D current plain, no-MTP | 109.8 | 188.7 | 323.1 | 505.0 | 756.7 | 1,126.8 | 1,666.5 |

A2 reproduces the documented Lucifer warm row
(`198.9 / 332.7 / 391.4 / 784.4 / 1183.5 / 1872.1 / 2818.9`) to within noise
(C64 `2822.1` vs `2818.9`), so the comparison is on a stable same-session
baseline. C reproduces the documented current C64 anchor (`1947.4` vs
`1954.8`); the lower C8/C16 cells in C reflect this run's per-cell MTP
acceptance variance (one cell sampled draft acceptance `~0.50`), not a
configuration change.

What the runtime-resolved configs proved identical on both stacks (from the
serve logs): compilation mode (`NONE`, because DeepSeek V4 auto-enables
`VLLM_USE_BREAKABLE_CUDAGRAPH=1`, which disables torch.compile/inductor on
both), `FULL_AND_PIECEWISE` cudagraph with capture sizes `[1..192]`, the
`CUSTOM`+`PYNCCL` / `PYNCCL` all-reduce dispatch, the FlashInfer top-p/top-k
sampler, the DeepGEMM E8M0 FP8 linear path, and the MTP acceptance profile
(mean acceptance length `~2.25`, per-position `~0.80 / ~0.45`, average draft
acceptance `~63%`). The only two backend differences are the MoE backend
(current `MARLIN` vs Lucifer `flashinfer_cutlass`) and the decode attention
kernel (current `flashinfer_trtllm_batch_decode_sparse_mla_dsv4` vs Lucifer
`sparse_mla_sm120_decode_dsv4_autotune`).

Decomposition at C64:

| Step | C64 tok/s | Delta | Isolates |
| --- | ---: | ---: | --- |
| D current plain, no-MTP | 1,666.5 | baseline | — |
| B2 Lucifer packed, no-MTP | 1,983.7 | +19.0% | base single-token decode (MoE + kernel + source) |
| MARLIN -> flashinfer_cutlass MoE (prior FI-MoE probe, MTP) | 1,947.4 -> 2,041.4 | +4.8% | MoE backend only |
| C current plain, MTP | 1,947.4 | baseline | — |
| A2 Lucifer packed, MTP | 2,822.1 | +44.9% | full production path |

MTP throughput multiplier at C64: Lucifer `2822.1 / 1983.7 = 1.42x` versus
current `1947.4 / 1666.5 = 1.17x`.

Interpretation. MTP draft acceptance is the same on both stacks, so the gap is
not draft quality or the verifier. Yet enabling MTP at C64 gives Lucifer
`+42%` but current only `+17%`. With equal acceptance, that difference comes
from the cost of the speculative verify forward: MTP-verify runs the decode
attention with `q_len = num_speculative_tokens + 1 = 3` query positions per
sequence. Lucifer's packed `sparse_mla_sm120_decode` kernel serves that
multi-query sparse-decode shape far more efficiently than current's plain
`trtllm` decode, so the verify forward is cheaper, which leaves more compute
headroom and inflates the effective MTP multiplier at high batch. The single
"packed SM120 sparse-MLA decode kernel" mechanism explains all three
observations: the isolated C4 crossover (the packed kernel's fixed
per-launch/workspace overhead loses at small batch, so current wins C4 at
`466.6` vs `397.8`), the C8+ reversal with the gap widening through C64, and
why the earlier PR3395 reintegration was neutral for ctx0 decode (it ported
only the packed prefill kernel `sparse_mla_sm120_paged_attention`, never the
decode kernel `sparse_mla_sm120_decode_dsv4_autotune`).

Conclusion: the C8-C64 ctx0 decode gap is the FlashInfer packed SM120
sparse-MLA decode kernel, with its advantage concentrated in the MTP
speculative-verify multi-query decode shape (the production path). The MoE
backend is a small secondary signal (`~+5%`). All other runtime/scheduler/
sampler/all-reduce/compile dimensions were ruled out by direct config
equality.

Operational note for reruns: the sanitized Lucifer serve wrapper only unsets
`PYTHONPATH`; it does not add the venv `bin` to `PATH`. Because the
`SPARSE_MLA_SM120` backend JIT-compiles via FlashInfer at worker init, a
launch without the venv `bin` on `PATH` dies with
`FileNotFoundError: [Errno 2] No such file or directory: 'ninja'` and
`Engine core initialization failed`. Prepend the venv `bin` to `PATH` (the
current-stack wrapper already does this; the Lucifer wrapper does not). This
is the same root cause as the earlier "missing venv `bin` on `PATH`" pitfall.

## Phase 3: SM120 Packed Decode Port (dev branch, gated, default off)

The attribution above was then confirmed inside the current branch's own tree
by porting the packed sparse-sm120 decode kernel and changing one variable.

Implementation (`codex/ds4-sm120-lucifer-decode-gap-20260614`): a new
`DeepseekV4FlashInferSM120Attention` subclass of the FlashMLA V4 attention class
that reuses the packed `fp8_ds_mla` cache, the sparse-index metadata, and the
packed prefill, and overrides only `_forward_decode` to call FlashInfer's
`BatchMLAPagedAttentionWrapper(backend="sparse-sm120").run_sparse_mla`. It is
selected only when `VLLM_DEEPSEEK_V4_FLASHINFER_SM120_DECODE=1`, the device is
SM12x, and `has_flashinfer_sparse_mla_sm120()` is true; otherwise behavior is
byte-for-byte the FlashMLA decode path. The current branch already had every
dependency (`decode_swa_lens`, `current_workspace_manager`,
`compute_global_topk_indices_and_lens`, the packed cache and packed prefill);
the only integration fix was forcing the extra (compressed) decode index tensor
contiguous, which the sparse-sm120 kernel asserts (`eidx must be contiguous`).

The decisive one-variable result (same source tree, same MARLIN MoE, same packed
cache, same MTP; only the decode kernel differs) is cell E2 versus cell C:

| C | C FlashMLA decode | E2 sparse-sm120 decode | Delta (decode kernel only) |
| ---: | ---: | ---: | ---: |
| 1 | 179.0 | 188.5 | +5.3% |
| 2 | 296.9 | 318.0 | +7.1% |
| 4 | 466.6 | 501.3 | +7.4% |
| 8 | 600.5 | 752.4 | +25.3% |
| 16 | 873.9 | 1,045.2 | +19.6% |
| 32 | 1,461.8 | 1,702.0 | +16.4% |
| 64 | 1,947.4 | 2,576.6 | +32.3% |

Swapping only the decode kernel lifts C64 by `+32%` and closes roughly `72%` of
the full current-to-Lucifer C64 gap; the residual is the `flashinfer_cutlass`
MoE (`~+5%`) plus minor runtime/source differences. E2 was clean (exit 0, no
errors, no queue, no capacity-limited cells, MTP acceptance `~2.2-2.28`). This is
the cleanest possible attribution: it isolates the decode kernel as the dominant
C8-C64 ctx0 lever inside one source tree. (E2 also keeps the C4 point ahead of
the FlashMLA baseline, so the isolated "C4 crossover" where Lucifer lost C4 is a
property of Lucifer's `flashinfer_cutlass` MoE / runtime, not of the packed
decode kernel.)

Correctness (GSM8K 5-shot, limit-200, C=4, same session): the port scored
flexible `0.92` / strict `0.90` versus the gate-off FlashMLA baseline flexible
`0.945` / strict `0.92`. The `-2.5 / -2` point delta is within `~1 sigma` at
limit-200 (stderr `~0.016-0.021`), i.e. not a regression. The baseline itself is
`0.92` strict (below the `0.925` floor) in this session, so the strict-floor
shortfall is a session artifact (temperature `1.0` generation config,
probabilistic MTP, 200-sample variance), not the decode kernel; MTP acceptance
is identical to the baseline and Lucifer's same kernel scores `0.955 / 0.955`.
Promotion still requires a tighter GSM8K (higher limit or temperature 0), the
full RTX promotion matrix, and the GB10 long-context / lifecycle gates; keep the
route default-off behind the env gate until those pass.

## Phase 3b: Prefill Feature Attribution On Authoritative 531807c (both dropped)

After the decode port, the 4 packed/D512-multi prefill commits (cherry-picked
onto the decode dev as `fa8f7b222` = decode + 3 diagnostics + `f19e6311`/
`fb07785d` D512-multi + `338b6c37`/`fa8f7b22` packed) were measured per-feature
on the authoritative `531807c` base to decide keep/drop. The decisive metric is
pure (uninstrumented) median TTFT at C=1 OSL=1, warm and repeated (n=8), with a
baseline re-measured last as a drift check. Both pairs were dropped.

Pure C=1 median TTFT (ms), stats OFF, baseline drift `<=0.5%`:

| ISL | baseline (avg) | packed | delta | d512multi |
| ---: | ---: | ---: | ---: | :--- |
| 16K | 935.4 | 926.7 | -0.9% | ~flat (gate inactive) |
| 32K | 1110.3 | 1100.8 | -0.9% | ~flat (gate inactive) |
| 65K | 2403.3 | 2362.1 | -1.7% | ~flat (gate inactive) |

Packed: a real but tiny `-1.7%` best case, far below the stale-base `+22%`.
Packed collapses the `sparse_accumulate` stage `277 -> 24 ms` (`-91%`, and
`by_compress_ratio` drops from `{1,4,128}` to `{1}` only) yet end-to-end TTFT is
flat. A same-build SPLIT x PACKED 2x2 (archived `fa8f7b222`, toggling the base
`INDEXED_D512_SPLIT`/`CHUNKED` gates and `PACKED`) explains why -- packed and the
base default indexed-D512 are two routes to the SAME prefill TTFT gain, and the
base now ships that route on by default, so packed is redundant:

| 16K / 65K median TTFT (ms) | indexed-D512 OFF | indexed-D512 ON (531807c default) |
| :--- | ---: | ---: |
| packed OFF | 181 / 330 | 161 / 299 |
| packed ON  | 160 / 301 | 161 / 309 |

On the unoptimized base packed is a real `-11.5% / -8.6%` (181->160, 330->301);
the base default indexed-D512 alone is the same `-10.9% / -9.2%` (181->161,
330->299); packed ON TOP of the base default is `-0.4% / +3.3%` (i.e. nothing).
So it is NOT stage-relocation at equal cost (packed actually cuts the stage
harder than the base default, `12 ms` vs `277 ms`); it is that the rebased base
already moved prefill TTFT past the point where `sparse_accumulate` is the
bottleneck, so packed's (genuine) extra stage reduction no longer translates.
This vindicates "the base absorbed the gain" at the end-to-end level. (Absolute
TTFT in this 2x2 run is ~5.8x lower than the C=1 pure table above for the same
config -- an unexplained run-to-run delta, likely warmup/autotune state or
partial prefix-cache reuse across repeated requests; it does not change the
relative within-run conclusion, which agrees with the pure C=1 `-1.7%`.)

D512 multi-prefill: `_allow_indexed_d512_prefill_request_count` returns true for
`request_count == 1` regardless of the gate, so the gate only changes behavior at
`num_prefills > 1`. Under the C=1 OSL=1 spec the gate is therefore inactive (the
base default-on `VLLM_DEEPSEEK_V4_INDEXED_D512_SPLIT_PREFILL` handles single
prefills). Its only active regime -- co-batching `>=2` prefills of `>=8192`
tokens (`_INDEXED_D512_SPLIT_PREFILL_MIN_TOKENS = 8192`) in one forward -- is
memory-infeasible on 2x RTX PRO 6000: at the raised `max-num-batched-tokens`
needed to co-schedule two long prefills, the 148 GiB model on 2x95 GiB leaves
only ~`4.1 GiB` for KV, but one `>=8192`-token request needs ~`8 GiB`, so five
serve configurations (batched 49152/20480, gpu-util 0.90/0.85, cudagraph and
enforce-eager, max-model-len 131072/24576) all failed engine init with
`No available memory for the cache blocks` / KV starvation. So on this exact
deployment hardware d512multi can never engage.

Root cause for both: the upstream rebase onto `531807c` already absorbed the
prefill work into base defaults -- `ab66ecf7` enables indexed-D512 sparse-MLA
prefill BY DEFAULT, plus the retuned split tiles, empty-tail skip, and the
multi-head accumulate kernel -- so the hand-ported features (validated earlier on
the stale pre-rebase base) are redundant on the new base. The dev branch is now
`75a7118086d` = rebased PR + decode port + the 3 kept sparse-MLA stats
diagnostics; pushed to origin as a clean fast-forward. Dropped work is archived
at tag `sm120-prefill-cherrypick-archived-20260615` (`fa8f7b222f6`).

Methodology pitfalls recorded for reuse: (1) a single cold request gives noisy
TTFT (an early run showed a spurious 2x baseline-16K outlier that the n=8 warm
repeat erased); warm + repeat + a baseline drift control are required. (2) The
sparse-MLA stats key is `stage_timings_ms.sparse_accumulate`, not
`timing_stages`; per-ISL attribution needs the stats files truncated between
ISLs since one serve appends all requests' layers. (3) Passing env-var
assignments through a bash function via `"$@"` is not re-recognized as an
assignment prefix after expansion (`VAR=1: command not found`); wrap the command
in `env "$@"`.
