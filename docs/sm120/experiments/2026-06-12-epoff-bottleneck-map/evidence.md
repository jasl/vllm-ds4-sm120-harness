# Evidence

## Working Assumptions

| Assumption | Current handling |
| --- | --- |
| EP-off is the default profile for new work | Treat EP-on as A/B only. Do not reuse EP-on-only wins as promotion evidence. |
| RTX PRO 6000 is the development platform | Profile and iterate on RTX first because it is faster and cheaper to rerun. |
| GB10 performance is the weak point | Confirm final candidates on GB10 with driver-health evidence and guarded memory profiles. |
| DFlash can hurt correctness | Run GSM8K and semantic gates before treating any DFlash/speculative change as usable. |
| Microbench wins are insufficient | Require endpoint attribution, serve logs, and promotion gates before PR branch changes. |

## Bottleneck Classifier

| Candidate bottleneck | Primary signal | First RTX probe | GB10 confirmation |
| --- | --- | --- | --- |
| Sparse-MLA dataflow | Lower sparse ms per effective visit, or fewer real visits at same semantics | `scripts/run_sm12x_prefill_gap_attribution.sh` | `scripts/run_gb10_prefill_gap_attribution.sh` |
| Sparse-MLA kernel shape | NCU shows memory/occupancy/launch limit in the sparse accumulate path | `scripts/run_sm12x_sparse_mla_ncu_microbench.sh` | GB10 attribution only after RTX endpoint signal |
| MoE / EP imbalance | EP-off beats EP-on while sparse work is unchanged | same attribution command with `SM12X_PREFILL_GAP_ENABLE_EXPERT_PARALLEL=0/1` | GB10 forum53 and MTP2 MoE TP sustained gate |
| Decode/speculative pipeline | MTP/no-MTP or DFlash changes alter decode throughput or acceptance | `scripts/run_decode_profile.sh` and GSM8K | GB10 decode probe plus forum53 if scheduler pressure changes |
| Scheduler/KV admission | Mixed-arrival or prefix-cache pressure changes TTFT/fairness | `scripts/run_sm12x_prefill_decode_interference_profiles.sh` | `scripts/run_gb10_forum53_multi_user_gate.sh` |
| Public dependency route | Stack probe says route is importable and serve logs prove dispatch | `scripts/run_b12x_stack_probe.sh` plus route-specific smoke | same probe in GB10 venv before endpoint A/B |

## Current RTX Observations

The 2026-06-13 stage-timing pass makes sparse MLA accumulate the first
optimization target for the EP-off cold-prefill profile.

| Signal | 16K | 65K | Interpretation |
| --- | ---: | ---: | --- |
| `sparse_accumulate` share of sparse prefill stage time | `93.33%` | `96.61%` | Gather/combine and scheduler/KV admission are not the first-order cold-prefill bottleneck. |
| Sparse accumulate ms per million effective visits | `2.789438` | `1.519574` | Endpoint work is dominated by effective candidate/value visits and their kernel efficiency. |
| Compressed padding ratio | `0.151421` | `0.098817` | Padding exists, but long-context waste is not high enough to explain the full gap by itself. |
| SWA padding ratio | `0.004085` | `0.001052` | SWA candidate padding is negligible in these shapes. |

At 65K, the group breakdown is the most actionable clue:

| Layer type | Compress | Effective visits | Stage total ms | Sparse visits/s |
| --- | ---: | ---: | ---: | ---: |
| `mla_prefill_chunk` | 1 | 607556768 | 3853.09 | 1.79215e8 |
| `mla_prefill_chunk` | 128 | 1951493440 | 10345.7 | 1.97086e8 |
| `mla_prefill_chunk` | 4 | 3122141442 | 15185.3 | 2.1181e8 |
| `mla_prefill_indexed_d512` | 128 | 10160664320 | 9542.22 | 1.09188e9 |
| `mla_prefill_indexed_d512` | 4 | 17946378240 | 14217.8 | 1.28134e9 |

So the immediate route is not "make all of prefill a little faster"; it is to
either move more work onto the indexed D512-style path, replace the slow
non-indexed chunk path, or reduce its real visits without changing semantics.

The first NCU microbench, `tokens=1024` and `candidates=640`, is consistent
with an occupancy / issue-efficiency problem rather than a raw DRAM bandwidth
wall: the profiled kernel reported `118` registers/thread, `32.60%` achieved
occupancy, `61.91%` SM throughput, `6.17%` DRAM throughput, and `46.36%`
no-eligible cycles. This is a kernel-shape clue only; endpoint A/B still has
priority over microbench wins.

The first 2026-06-13 route probe narrowed what could be tested immediately in
the then-current RTX target venv:

- available now: plain FlashInfer DS4 sparse MLA route and FlashInfer B12X MoE
  route;
- source/reference only until dependency work: PR3395 packed SM120 FlashInfer
  sparse MLA, public b12x paged sparse indexer, DS4 b12x compressed MLA
  adapter, DS4 b12x WO, and native MXFP4 MoE.

The follow-up dependency refresh changes the b12x read but not the endpoint
decision:

| Probe | Result | Interpretation |
| --- | --- | --- |
| `b12x==0.20.0` default resolver | Pulls a Torch/Triton/CUDA runtime set that breaks current `vllm._C`; also downgrades NCCL. | Do not use the default resolver for this dev venv. |
| `b12x==0.20.0` no-deps | Keeps the current vLLM runtime healthy and exposes DS4 compressed-MLA, sparse-indexer-extend, native MXFP4 MoE helper APIs, WO, mHC, FP8 linear, and PCIe all-reduce imports. | The public API blocker is gone for component probes; vLLM runtime hooks are still absent. |
| FlashInfer `0.6.13rc1` matched jit-cache | `flashinfer-python/cubin==0.6.13rc1` imports after either `FLASHINFER_DISABLE_VERSION_CHECK=1` bypasses the older jit-cache mismatch or `flashinfer-jit-cache==0.6.13rc1+cu130` is installed. | Official rc1 is usable in the RTX dev venv. Packed SM120 sparse MLA requires the PR3395 fork branch, not the official wheel. |
| b12x compressed MLA `real_c128` | b12x `0.432 ms`, old online packed `5.923 ms`, D512 split+finish `0.209 ms`. | Do not port public b12x compressed MLA directly as the next endpoint path. |
| grouped-SWA D512, `1152` candidates | split `1.382 ms`, grouped-SWA `0.824 ms`. | Component signal is still real, but the older separate-launch endpoint form regressed. |
| grouped-stream, `1152` candidates | split `1.320 ms`, grouped stream `0.600 ms`. | Strongest fork-independent signal points to fused dual-stream online processing, not to a direct dependency swap. |

## First D512 Multi-Prefill Endpoint Prototype

The first conservative fork-independent prototype expands the existing indexed
D512 prefill path to multi-prefill batches behind
`VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1`. It does not require
FlashInfer PR3395 or a source FlashInfer fork.

Same-profile RTX stage-timing A/B:

| Input length | Metric | Current gate | Multi-prefill D512 | Delta |
| ---: | --- | ---: | ---: | ---: |
| 16384 | `mla_prefill_chunk` rows | 2432 | 1284 | `-47.20%` |
| 16384 | `mla_prefill_indexed_d512` rows | 2050 | 3198 | `+56.00%` |
| 16384 | `num_prefills_not_1` gate rows | 1558 | 328 | `-78.95%` |
| 16384 | `sparse_accumulate` ms | 21219.778 | 11843.018 | `-44.19%` |
| 16384 | sparse ms/M effective visit | 3.065 | 1.711 | `-44.19%` |
| 65536 | `mla_prefill_chunk` rows | 3788 | 1820 | `-51.95%` |
| 65536 | `mla_prefill_indexed_d512` rows | 13366 | 15334 | `+14.72%` |
| 65536 | `num_prefills_not_1` gate rows | 1968 | 0 | `-100.00%` |
| 65536 | `sparse_accumulate` ms | 54004.115 | 34165.937 | `-36.73%` |
| 65536 | sparse ms/M effective visit | 1.598 | 1.011 | `-36.73%` |

Endpoint prefill sweep A/B:

| Input length | Concurrency | Input tok/s current -> prototype | Mean TTFT current -> prototype | P99 TTFT current -> prototype |
| ---: | ---: | --- | --- | --- |
| 16384 | 1 | `7656.07 -> 8051.11` (`+5.16%`) | `2139.13 -> 2035.67 ms` (`-4.84%`) | `2437.91 -> 2045.78 ms` (`-16.08%`) |
| 16384 | 2 | `6905.80 -> 8253.90` (`+19.52%`) | `4403.76 -> 3630.80 ms` (`-17.55%`) | `4781.85 -> 4123.95 ms` (`-13.76%`) |
| 16384 | 4 | `6265.39 -> 8131.02` (`+29.78%`) | `7281.53 -> 5503.94 ms` (`-24.41%`) | `10416.96 -> 8013.27 ms` (`-23.07%`) |
| 65536 | 1 | `7140.94 -> 7607.20` (`+6.53%`) | `9178.19 -> 8615.16 ms` (`-6.13%`) | `10808.87 -> 8670.99 ms` (`-19.78%`) |
| 65536 | 2 | `6775.50 -> 7658.31` (`+13.03%`) | `17364.65 -> 15130.20 ms` (`-12.87%`) | `20795.07 -> 17794.23 ms` (`-14.43%`) |
| 65536 | 4 | `6752.81 -> 7611.61` (`+12.72%`) | `25287.98 -> 22015.59 ms` (`-12.94%`) | `38576.61 -> 34201.24 ms` (`-11.34%`) |

Correctness and lifecycle guard:

| Run | Env | Phases | Result |
| --- | --- | --- | --- |
| prototype lifecycle guard | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | `prefix_cache_probe`, `kv_lifecycle_probe` | both phase exit codes `0`; marker checks and idle KV threshold passed |
| prototype GSM8K 5-shot | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | `eval_gsm8k` | exit `0`; GSM8K flexible/strict `0.965 / 0.960`; floor gate passed |
| paired GSM8K 5-shot control | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=0` | `eval_gsm8k` | exit `0`; GSM8K flexible/strict `0.950 / 0.930`; floor gate passed |

The first lifecycle run also included an accidental 8-shot GSM8K slice because
the baseline driver defaulted to `LM_EVAL_NUM_FEWSHOT=8`; keep that as a
diagnostic only, not as the 5-shot stable-preview comparison. The paired 5-shot
runs show no correctness regression from multi-prefill D512: the prototype
matches the 2026-06-12 stable-preview flexible score `0.965` and improves over
the same-environment multi-prefill-off control.

GB10 reduced confirmation:

| Input length | Metric | Multi-prefill off | Multi-prefill on | Delta |
| ---: | --- | ---: | ---: | ---: |
| 16384 | `mla_prefill_chunk` rows | 1516 | 942 | `-37.86%` |
| 16384 | `mla_prefill_indexed_d512` rows | 1558 | 2132 | `+36.84%` |
| 16384 | `num_prefills_not_1` gate rows | 738 | 164 | `-77.78%` |
| 16384 | `sparse_accumulate` ms | 53976.852 | 42695.228 | `-20.90%` |
| 16384 | sparse ms/M effective visit | 11.471 | 9.074 | `-20.90%` |
| 65536 | `mla_prefill_chunk` rows | 2578 | 1430 | `-44.53%` |
| 65536 | `mla_prefill_indexed_d512` rows | 8856 | 10004 | `+12.96%` |
| 65536 | `num_prefills_not_1` gate rows | 1148 | 0 | `-100.00%` |
| 65536 | `sparse_accumulate` ms | 172870.259 | 138329.454 | `-19.98%` |
| 65536 | sparse ms/M effective visit | 7.644 | 6.117 | `-19.98%` |

| Input length | Concurrency | Input tok/s off -> on | Mean TTFT off -> on | P99 TTFT off -> on |
| ---: | ---: | --- | --- | --- |
| 16384 | 1 | `1515.63 -> 1523.38` (`+0.51%`) | `10809.88 -> 10755.20 ms` (`-0.51%`) | `11279.77 -> 11517.51 ms` (`+2.11%`) |
| 16384 | 2 | `1299.03 -> 1495.23` (`+15.10%`) | `23356.20 -> 20062.23 ms` (`-14.10%`) | `26162.13 -> 22527.41 ms` (`-13.89%`) |
| 65536 | 1 | `1424.54 -> 1422.45` (`-0.15%`) | `46005.07 -> 46071.38 ms` (`+0.14%`) | `48097.74 -> 48249.73 ms` (`+0.32%`) |
| 65536 | 2 | `1277.57 -> 1393.42` (`+9.07%`) | `91291.83 -> 82717.21 ms` (`-9.39%`) | `109641.26 -> 97377.85 ms` (`-11.19%`) |

The GB10 result confirms the same mechanism as RTX at 16K and 65K: more rows
move onto indexed D512 and the multi-prefill slow gate shrinks. The 65K
confirmation had to be run as one case per boot because earlier 16K runs left a
current-boot NVRM OOM record and the safety preflight correctly refused the
next case until reboot. After the 65K prototype, both nodes were rebooted and
the new boot had no NVRM OOM/Xid records. Continue GB10 validation as
single-case runs with reboot between cases, or first investigate why
teardown/serving leaves the worker boot in that state.

GB10 forum53 MTP2 prefix-cache gate:

| Run | Env | Matrix result | Max TTFT s | ITL p99 s | Driver health | Artifact |
| --- | --- | --- | ---: | ---: | --- | --- |
| first env-on | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 1 marker failure, matrix exit `1` | `124.970255` | `0.223721` | dirty, 1 signal | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_multi_prefill_20260613045800/20260613045800` |
| clean-boot env-on retry | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 1 marker failure, matrix exit `1` | `124.697034` | `0.099339` | dirty, 2 signals | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_multi_prefill_retry_20260613051100/20260613051042` |
| same-branch env-off control | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=0` | 4 requests, 0 failures, matrix exit `0` | `124.265379` | `0.150068` | dirty, 2 signals | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_multi_prefill_control_20260613052200/20260613052137` |

Interpretation: the matrix correctness failure is specific to the env-on runs
in this sample, because the same-branch env-off control produced 4/4 marker
successes. The driver-health failure is not env-specific, because it also
appeared in the env-off control after a clean-boot start. Do not promote the
D512 multi-prefill expansion, and do not use these forum53 runs as clean
positive GB10 evidence until both the marker failure and the startup/post-run
driver-health signals are understood.

Follow-up response-capture runs added `assistant_text_length`,
`assistant_text_sha256`, and failure-only `assistant_text_excerpt` to the
streaming-pressure rows:

| Run | Env | Matrix result | Max TTFT s | ITL p99 s | Artifact |
| --- | --- | --- | ---: | ---: | --- |
| RTX C2 env-on | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 0 failures | `27.212879` | `0.180494` | `artifacts/main/2x_rtx_pro_6000_sm120/rtx_forum53_mtp2_epoff_d512_on/20260613055203` |
| RTX C2 env-off | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=0` | 4 requests, 0 failures | `26.497937` | `0.049509` | `artifacts/main/2x_rtx_pro_6000_sm120/rtx_forum53_mtp2_epoff_d512_off/20260613055203` |
| GB10 C2 env-on capture | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 0 failures | `124.279151` | `0.122834` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_on_capture/20260613055729` |
| GB10 C2 env-on capture repeat | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 1 marker failure | `122.356447` | `0.395746` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_on_capture_repeat/20260613060731` |
| GB10 C2 env-off capture control | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=0` | serve preflight blocked by current-boot driver OOM | n/a | n/a | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_off_capture_control/20260613061702` |

The repeated GB10 env-on failure was `round_02_worker_01`, finish reason
`stop`, TTFT `9.155373s`, 10 streamed chunks, 22 completion tokens. The
captured assistant excerpt was only the previous assistant status body:
`status: previous streaming response completed. status: content remained
readable. status: worker context was preserved.` It did not contain the
current required marker `STREAM-W01-R02-CHECK`. This rules out an empty
response or simple length truncation and points at a prefix-cache/current-suffix
context mix-up in the env-on path on GB10. The RTX C2 probe did not reproduce
the marker miss. GB10 serve logs also showed only about `129800-134895` KV
tokens available for an `81920` max-model-len, or `1.58-1.65x` maximum
concurrency for one full-length request, so this profile is near the GB10
capacity boundary; that explains the serialized TTFT shape but not the wrong
assistant text.

## Historical PR3395 GB10 Subset

The 2026-06-08 GB10 packed FlashInfer promotion subset is the strongest
endpoint-shaped evidence for the PR3395 route so far. It used the default-off
`VLLM_DEEPSEEK_V4_FLASHINFER_PACKED_PREFILL=1` adapter and completed:

- prefill matrix:
  `artifacts/main/2x_gb10_sm121/20260608_packed_fi_promotion_prefill_gap_valid/20260608180541`;
- reduced long-C2:
  `artifacts/main/2x_gb10_sm121/20260608_packed_fi_promotion_long_c2_mtp2/20260608185801`;
- reduced MTP=2 MoE TP soak:
  `artifacts/main/2x_gb10_sm121/20260608_packed_fi_promotion_mtp2_moe_soak_reduced/20260608190816`.

| ISL | Env-off input tok/s | Packed input tok/s | TTFT env-off -> packed | Sparse ms/M effective visit |
| ---: | ---: | ---: | --- | --- |
| 4096 | `593.62` | `664.94` | `3.613s -> 2.767s` | `19.56 -> 0.639` |
| 8192 | `892.37` | `1012.61` | `6.576s -> 5.165s` | `13.61 -> 0.577` |
| 32768 | `1198.32` | `1368.76` | `24.561s -> 21.004s` | `10.50 -> 0.485` |
| 128000 | `1185.68` | `1315.45` | `105.030s -> 94.386s` | `6.88 -> 0.345` |

Sparse work moved from `sparse_accumulate` to `flashinfer_packed_attention`.
The GB10 reduced long-C2 gate passed with 4 requests, 0 failures, max TTFT
`147.820s`, p99 ITL `0.079s`, and driver signal `0`. The reduced MTP=2 MoE TP
soak passed with 16 requests, 0 failures, no no-progress watchdog, p99 ITL
`0.0739s`, and driver signal `0`.

This evidence makes PR3395 worth reviving, but it still does not promote the
route by itself. Missing gates remain RTX 59K/124K C=1/C=2, short throughput,
mixed arrival, prefix/KV lifecycle, GSM8K limit-200, and a full GB10 soak.

## Current Direction

1. Keep the stable PR branch and current dev branch pinned. Do not chase
   upstream/main or black-benediction head unless a specific mechanism is being
   reviewed.
2. First candidate family: sparse MLA accumulate/backend. Prefer a conservative
   route that improves or replaces the slow non-indexed chunk groups while
   preserving `FULL_AND_PIECEWISE` graphs and DS4 correctness.
3. Keep the D512 multi-prefill expansion default-off. GB10 16K/65K single-case
   confirmation is positive, but forum53 MTP2 prefix-cache failed twice with
   marker misses under env-on. Response-capture follow-up reproduced the GB10
   failure as the previous assistant status body being returned without the
   current marker, while RTX C2 env-on/off did not reproduce it. Full GB10
   still needs a prefix-cache/current-suffix mapping fix, a clean env-off
   response-capture control after reboot, sustained soak, and a fix or
   operating rule for the post-run NVRM OOM state before this route can be
   promoted.
4. Keep b12x `0.20.0` no-deps as the current public-b12x component-probe
   state, but do not add a DS4 compressed-MLA endpoint adapter unless a newer
   backend/dataflow beats current D512 split+finish.
5. Treat FlashInfer PR3395 packed SM120 sparse MLA as a valuable fork route,
   not as an official-wheel blocker. Earlier endpoint-shaped probes showed
   about `10-23%` TTFT improvement, so a new attempt is worth doing, but it
   must stay behind `VLLM_DEEPSEEK_V4_FLASHINFER_PACKED_PREFILL=1` until the
   current EP-off correctness and performance matrix passes.
6. Treat `flashinfer-jit-cache` as optional for PR3395/source builds. Missing
   jit-cache mainly affects startup/warmup cost; if a source build conflicts
   with the cache package, omit it and warm up sufficiently before recording
   performance.
7. Keep black-benediction DFlash/decode changes as a second-stage reference.
   They may help decode/speculative throughput, but they are high-correctness
   risk and are not the first response to this cold-prefill bottleneck.
8. The next code-bearing experiment after D512 multi-prefill validation should
   be a fused dual-stream sparse-MLA component or endpoint prototype that
   avoids the extra merge/finish launches that made the archived grouped-SWA
   endpoint regress.

## First RTX Commands

Run these on an SM120 host with the target vLLM venv. Keep all machine-specific
paths in the local shell environment or ignored local notes.
Run the preflight in `preflight.md` first, then start with the EP-off control.
Prefer the narrow wrapper for routine starts:

```bash
scripts/run_sm120_epoff_bottleneck_attribution.sh
```

Set `SM120_EPOFF_BOTTLENECK_RUN_EPON_COMPARISON=1` only when separating
MoE/EP imbalance from sparse-MLA work. The expanded commands below are kept for
manual reproduction or one-off overrides.

### 1. Stable EP-Off Sparse Attribution Control

```bash
SM120_VLLM_REPO=./vllm \
SM120_VLLM_VENV=./vllm/.venv \
SM120_PYTHON=./vllm/.venv/bin/python \
VLLM_ROOT=./vllm \
SM12X_PREFILL_GAP_LABEL=epoff_stable_preview_control \
SM12X_PREFILL_GAP_VARIANT=mtp \
SM12X_PREFILL_GAP_ENABLE_EXPERT_PARALLEL=0 \
SM12X_PREFILL_GAP_INPUT_LENS=4096,16384,65536,124000 \
SM12X_PREFILL_GAP_CONCURRENCY=1,2,4 \
SM12X_PREFILL_GAP_OUTPUT_LEN=1 \
SM12X_PREFILL_GAP_NUM_PROMPTS=8 \
SM12X_PREFILL_GAP_D512_ENV=default \
SERVE_PREFIX_CACHE_MODE=disabled \
scripts/run_sm12x_prefill_gap_attribution.sh
```

Expected use: establish endpoint TTFT/input tok/s beside sparse candidate/value
work for the same run. This is the control for all route variants.

### 2. EP-On Comparison

```bash
SM120_VLLM_REPO=./vllm \
SM120_VLLM_VENV=./vllm/.venv \
SM120_PYTHON=./vllm/.venv/bin/python \
VLLM_ROOT=./vllm \
SM12X_PREFILL_GAP_LABEL=epon_comparison_control \
SM12X_PREFILL_GAP_VARIANT=mtp \
SM12X_PREFILL_GAP_ENABLE_EXPERT_PARALLEL=1 \
SM12X_PREFILL_GAP_INPUT_LENS=4096,16384,65536 \
SM12X_PREFILL_GAP_CONCURRENCY=1,2,4 \
SM12X_PREFILL_GAP_OUTPUT_LEN=1 \
SM12X_PREFILL_GAP_NUM_PROMPTS=8 \
SM12X_PREFILL_GAP_D512_ENV=default \
SERVE_PREFIX_CACHE_MODE=disabled \
scripts/run_sm12x_prefill_gap_attribution.sh
```

Expected use: separate MoE/EP imbalance from sparse-MLA dataflow. If sparse
work is unchanged but endpoint throughput drops, investigate MoE and pipeline
overlap before kernel rewrites.

### 3. Correctness Guard

```bash
BASE_URL=http://localhost:8000 \
MODEL=deepseek-ai/DeepSeek-V4-Flash \
PYTHON=./vllm/.venv/bin/python \
VLLM_VENV=./vllm/.venv \
LM_EVAL_BIN=./vllm/.venv/bin/lm_eval \
LM_EVAL_NUM_FEWSHOT=5 \
LM_EVAL_LIMIT=200 \
LM_EVAL_GATE_FLOORS=exact_match_flexible=0.94,exact_match_strict=0.925 \
OUT_DIR=artifacts/local/epoff_bottleneck_gsm8k \
scripts/run_lm_eval.sh
```

Expected use: block promotion if correctness falls below the fixed floor.
For DFlash/speculative changes, run this before spending GB10 time.

### 4. Local Quality Expansion

```bash
SM120_VLLM_REPO=./vllm \
SM120_VLLM_VENV=./vllm/.venv \
SM120_PYTHON=./vllm/.venv/bin/python \
B200_BASELINE_LABEL=epoff_bottleneck_quality \
SM120_LOCAL_ENABLE_EXPERT_PARALLEL=0 \
SERVE_PREFIX_CACHE_MODE=disabled \
LM_EVAL_NUM_FEWSHOT=5 \
LM_EVAL_LIMIT=200 \
scripts/run_sm120_local_quality_gates.sh
```

Expected use: widen after a candidate has a clear attribution signal.

## GB10 Confirmation Commands

Run these only after a route has an explained RTX win and passes correctness.
The GB10 scripts require local environment variables for the target hosts and
RDMA/NCCL setup; keep those values outside tracked docs.

### 1. GB10 Attribution

```bash
GB10_PREFILL_GAP_LABEL=epoff_candidate_gb10_attribution \
GB10_PREFILL_GAP_VARIANT=mtp2 \
GB10_PREFILL_GAP_PROFILES=dev_default \
GB10_PREFILL_GAP_PREFIX_CACHE_MODES=disabled \
GB10_PREFILL_GAP_ENABLE_EXPERT_PARALLEL=0 \
GB10_PREFILL_GAP_INPUT_LENS=4096,16384,32768,65536 \
GB10_PREFILL_GAP_CONCURRENCY=1,2 \
GB10_PREFILL_GAP_OUTPUT_LEN=1 \
GB10_PREFILL_GAP_MAX_NUM_BATCHED_TOKENS=4096 \
scripts/run_gb10_prefill_gap_attribution.sh
```

Expected use: check whether the RTX signal transfers to SM121 without driver
health issues.

### 2. GB10 User-Feedback Gate

```bash
GB10_FORUM53_LABEL=epoff_candidate_forum53 \
GB10_FORUM53_VARIANTS=mtp2 \
GB10_FORUM53_ENABLE_EXPERT_PARALLEL=0 \
GB10_FORUM53_BATCHED_TOKEN_SWEEP=4096 \
GB10_FORUM53_MAX_MODEL_LEN=81920 \
GB10_FORUM53_MAX_NUM_SEQS=2 \
GB10_FORUM53_GPU_MEMORY_UTILIZATION=0.685 \
scripts/run_gb10_forum53_multi_user_gate.sh
```

Expected use: preserve the current user-feedback memory/admission envelope.

## Promotion Rules

| Rule | Required evidence |
| --- | --- |
| Correctness first | GSM8K limit-200 must stay at or above flexible `0.94` and strict `0.925`; semantic gates must not regress. |
| Endpoint before microbench | Endpoint A/B must show a gain that matches attribution counters or MoE/pipeline evidence. |
| RTX before GB10 | Iterate on RTX first, then confirm on GB10 once the hypothesis is narrow. |
| GB10 driver health | GB10 runs must record clean driver health, not only successful benchmark output. |
| Prefix-cache separation | Prefix-cache-enabled results can support user-feedback gates, not cold-prefill throughput claims. |
| No hidden graph downgrade | `FULL_AND_PIECEWISE` stays enabled; do not hide failures by changing graph mode. |
