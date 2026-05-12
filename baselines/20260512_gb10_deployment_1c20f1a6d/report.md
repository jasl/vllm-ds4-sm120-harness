# GB10 Spark Deployment Baseline — 2026-05-12

DeepSeek V4 Flash on a **2-node NVIDIA DGX Spark cluster** (1× GB10
per node, compute capability 12.1, 128 GiB unified memory per node).
TP=2 PP=1 mp distributed via RoCE; vLLM `jasl/vllm` @ `1c20f1a6d`
(head of `ds4-sm120-preview-dev` / PR #41834, 17 commits ahead of
`upstream/main`).

This bundle is the reference for edge / DGX Spark deployments. The
RTX PRO 6000 Workstation counterpart lives in
`../20260512_sm120_deployment_1c20f1a6d/`.

## TL;DR

- **Conversation profile** (`max_model_len=32768`, `max_num_seqs=8`,
  `gpu-mem 0.85`, `NCCL_IB_DISABLE=0`)
  - no-MTP c=1: **21.24 tok/s**, c=8 saturation: **75.89 tok/s**
  - MTP=2 c=1: **29.79 tok/s**, c=8 saturation: **94.72 tok/s**
- **Agent profile** (`max_model_len=65536`, `max_num_seqs=4`)
  - no-MTP c=1: 21.14 tok/s, c=4 saturation: 55.53 tok/s
  - MTP=2 c=1: 28.51 tok/s, c=4 saturation: 59.66 tok/s
- max_concurrency: Conv no-MTP 7.31× / MTP=2 6.51×; Agent no-MTP
  7.12× / MTP=2 6.26×
- MTP=2 acceptance: 67.4–68.8 %, accept-length 2.35–2.39 across
  every concurrency tier
- gsm8k 5-shot 200q: **0.955** no-MTP, **0.960** MTP=2 (top of the
  historical 0.948–0.965 band)

## Recommended deployment commands

The cluster is launched via `scripts/dgx_spark_start_mp_serve.sh`
from a control host with SSH to both Spark nodes. The script expects
the RoCE env (`HEAD_ROCE_IP`, `WORKER_ROCE_IP`, `ROCE_IFACE`,
`NCCL_IB_HCA`) and the cluster topology (`HEAD_HOST`, `WORKER_HOST`).

### Conversation (short prompts, multi-user up to 8)

```bash
HEAD_HOST=10.0.0.116 WORKER_HOST=10.0.0.118 \
HEAD_ROCE_IP=169.254.116.28 WORKER_ROCE_IP=169.254.117.143 \
ROCE_IFACE=enp1s0f1np1 NCCL_IB_HCA=rocep1s0f1 \
VLLM_ROOT=/home/jasl/Workspace/vllm \
VLLM_VENV=/home/jasl/Workspace/vllm/.venv \
TP_SIZE=2 PP_SIZE=1 \
MAX_MODEL_LEN=32768 MAX_NUM_SEQS=8 \
MAX_NUM_BATCHED_TOKENS=8192 \
GPU_MEMORY_UTILIZATION=0.85 \
BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8 \
SERVE_ENABLE_EXPERT_PARALLEL=1 \
SERVE_DISABLE_FLASHINFER_AUTOTUNE=1 \
SERVE_COMPILATION_CONFIG='{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
SERVE_SPECULATIVE_CONFIG='{"method":"deepseek_mtp","num_speculative_tokens":2}' \
NCCL_IB_DISABLE=0 NCCL_DEBUG=WARN \
RUN_DIR=/tmp/spark_tp2_serve \
scripts/dgx_spark_start_mp_serve.sh
```

Drop `SERVE_SPECULATIVE_CONFIG` for the no-MTP variant. Add
`SERVE_DEFAULT_CHAT_TEMPLATE_KWARGS='{"thinking":true}'` to enable
DSv4's `<think>` block.

### Agent (long context, 1–4 parallel agents)

Same as Conversation, with:
```
MAX_MODEL_LEN=65536 MAX_NUM_SEQS=4
```

### NCCL transport — keep IB verbs on (`NCCL_IB_DISABLE=0`)

Measured on this cluster, at single-user decode (no-MTP c=1):

| `NCCL_IB_DISABLE` | Transport | tok/s |
|---|---|---|
| **0** (default) | IB verbs over the RoCE HCA | **21.24** |
| 1 | TCP fallback over the RoCE iface | 15.12 (−29 %) |

`NCCL_IB_DISABLE=1` is only worth setting if the IB stack itself is
unavailable on the host.

## Performance — mt-bench (`philschmid/mt-bench`, 80 prompts, `temperature=1.0`)

### Conversation profile

| c | no-MTP tok/s | no-MTP TPOT (ms) | MTP=2 tok/s | MTP=2 TPOT (ms) | MTP accept % |
|---|---|---|---|---|---|
| 1 | 21.24 | 58.13 | 29.79 | 28.97 | 68.75 |
| 2 | 37.92 | 50.11 | 51.73 | 35.82 | 68.43 |
| 4 | 56.26 | 67.47 | 57.95 | 64.65 | 68.66 |
| 8 | **75.89** | 98.49 | **94.72** | 76.71 | 67.95 |

KV: no-MTP 23.04 GiB / 239,617 tokens / max_concurrency 7.31×.
MTP=2 20.73 GiB / 213,425 tokens / 6.51×.

### Agent profile

| c | no-MTP tok/s | no-MTP TPOT (ms) | MTP=2 tok/s | MTP=2 TPOT (ms) | MTP accept % |
|---|---|---|---|---|---|
| 1 | 21.14 | 65.52 | 28.51 | 46.39 | 68.34 |
| 2 | 37.42 | 50.97 | 49.55 | 37.49 | 67.42 |
| 4 | 55.53 | 68.90 | 59.66 | 63.08 | 67.88 |

KV: no-MTP 22.50 GiB / 466,819 tokens / 7.12× at 65 K-token requests.
MTP=2 20.31 GiB / 409,934 tokens / 6.26×. Each request can stretch
to a 65 K-token context (tool history + thinking) without forcing the
cluster into single-user mode.

c=1 single-stream throughput is statistically identical between Conv
and Agent profiles (compute-bound at low concurrency); the Agent
profile's value is the 65 K-token context allowance per stream.

## Accuracy

`lm_eval` `gsm8k` 5-shot, 200 questions, `temperature=0`,
`max_gen_toks=2048`, via `/v1/completions` (chat-template-independent).

| Variant | strict | flexible |
|---|---|---|
| no-MTP | 0.955 | 0.955 |
| **MTP=2** | **0.960** | **0.960** |

Both sit at or above the historical 0.948–0.965 band measured on
B200, B300, and the DeepSeek Official API. MTP=2 lands at the top of
the band — long-context attention and MTP draft acceptance both
favour the math-reasoning prompts here.

## Generation reference (Conv profile, MTP=2, non-thinking)

Three representative prompts run on a fresh Conv-profile MTP=2
cluster. Each `.md` is a self-contained prompt+response transcript;
`aquarium_html` also yields an `.html` artifact you can open in a
browser to confirm the rendered interactive aquarium.

| Case | Lang | Tokens out | Elapsed |
|---|---|---|---|
| aquarium_html | en | ~3,900 | ~135 s |
| aquarium_html | zh | ~3,800 | ~130 s |
| en2zh_news_001 | en | ~700 | ~25 s |
| zh_sum_tech_001 | zh | ~1,200 | ~45 s |

`results.jsonl` has the full metadata.

## Use-case decision matrix

| Workload | Recommended cell | Expected throughput |
|---|---|---|
| Single chat user, short prompts | Conv c=1 MTP=2 | **30 tok/s** decode |
| 4–8 chat users (e.g. family / small office) | Conv c=8 MTP=2 | **95 tok/s** aggregate |
| 1 agent, ≤ 32 K context | Conv c=1 MTP=2 | 30 tok/s decode |
| 1 agent, ≤ 65 K context | Agent c=1 MTP=2 | 29 tok/s decode |
| 2–4 parallel agents, 65 K each | Agent c=4 MTP=2 | 60 tok/s aggregate |
| 1 request at the 131 K cap | Agent with `MAX_MODEL_LEN=131072` | TTFT minutes-scale at long ISL (>16 K → chunked-prefill cost dominates) |

MTP=2 is the practical operating point for single-stream chat — the
+40 % gain at c=1 (21 → 30 tok/s) is the difference between "feels
laggy" and "comfortable" on the typical edge use case.

## Cold-start considerations

vLLM `1c20f1a6d` extends prefill warmup to
`max_num_batched_tokens=8192`, so the first long single-chunk
prefill no longer pays a full Triton JIT spike. The first request
after a fresh cluster may still see a few-second TTFT spike if the
shape is outside the warmup envelope; subsequent requests run from
the warm Triton cache (~0.5 s TTFT at ISL=8 K). For production
clusters the cost is one-time per process.

Cluster startup itself is the dominant time cost: model load takes
~140 s (74 GiB partitioned across 2 nodes over RoCE), cudagraph
capture another ~10 s, then warmup ~30 s — total ~3 min to
`/health=200` on a freshly dropped page cache.

## Reproduction

See `repro_recipe.md`. Bench JSONs are in `performance/`, gsm8k raw
trees in `evals/`, generation transcripts in `generation/`.

## Source SHAs

- vLLM: `1c20f1a6d` on `jasl/vllm` `ds4-sm120-preview-dev` (PR
  #41834; data collected at `8f0d8b630`, rebased to add
  `Signed-off-by` trailers — no code changes)
- Harness: this commit
