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
3. Keep b12x `0.20.0` no-deps as the current public-b12x component-probe
   state, but do not add a DS4 compressed-MLA endpoint adapter unless a newer
   backend/dataflow beats current D512 split+finish.
4. Treat FlashInfer PR3395 packed SM120 sparse MLA as a valuable fork route,
   not as an official-wheel blocker. Earlier endpoint-shaped probes showed
   about `10-23%` TTFT improvement, so a new attempt is worth doing, but it
   must stay behind `VLLM_DEEPSEEK_V4_FLASHINFER_PACKED_PREFILL=1` until the
   current EP-off correctness and performance matrix passes.
5. Treat `flashinfer-jit-cache` as optional for PR3395/source builds. Missing
   jit-cache mainly affects startup/warmup cost; if a source build conflicts
   with the cache package, omit it and warm up sufficiently before recording
   performance.
6. Keep black-benediction DFlash/decode changes as a second-stage reference.
   They may help decode/speculative throughput, but they are high-correctness
   risk and are not the first response to this cold-prefill bottleneck.
7. The next code-bearing experiment should be a fused dual-stream sparse-MLA
   component or endpoint prototype that avoids the extra merge/finish launches
   that made the archived grouped-SWA endpoint regress.

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
LM_EVAL_GATE_FLOORS=exact_match_flexible:0.94,exact_match_strict:0.925 \
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
