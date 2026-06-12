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
