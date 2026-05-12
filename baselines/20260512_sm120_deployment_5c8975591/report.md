# SM12x Deployment Baseline — 2026-05-12

DeepSeek V4 Flash on SM12x hardware, vLLM `jasl/vllm` @ `5c8975591`
(head of `ds4-sm120-preview-dev` / PR #41834, 16 commits ahead of
`upstream/main`). This baseline measures the **recommended deployment
profiles** for two use cases — short-prompt chat (Conversation) and
long-context agentic work (Agent) — on both supported targets, and is
the reference point for the next round of optimisation.

The 2026-05-12 `_T1AT1D_T2A_2760932cf` bundle remains the apples-to-apples
"kernel optimisation" reference. This bundle adds a final layer:
production-shaped serve configs, real per-profile throughput up to the
serving cap, and one decision per `{hardware, profile, variant}` cell.

## TL;DR

- **Workstation SM120** (2× RTX PRO 6000 Blackwell Workstation Edition,
  TP=2 EP, gpu-mem 0.985)
  - Conv MTP=2 c=1 chat: **137.23 tok/s**, c=8 saturation: **442.56 tok/s**
  - Agent MTP=2 c=1 chat: 130.01 tok/s, c=4 saturation: 250.62 tok/s
  - max_concurrency: Conv 3.49× (no-MTP 4.11×), Agent 3.45× (no-MTP 4.03×)
  - gsm8k 5-shot 200q: 0.95 no-MTP, 0.95 MTP=2
- **DGX Spark cluster** (2 nodes × GB10, TP=2 PP=1 mp over RoCE, gpu-mem
  0.85, NCCL_IB_DISABLE=0)
  - Conv MTP=2 c=1 chat: **29.79 tok/s**, c=8 saturation: **94.72 tok/s**
  - Agent MTP=2 c=1 chat: 28.51 tok/s, c=4 saturation: 59.66 tok/s
  - max_concurrency: Conv 6.51× (no-MTP 7.31×), Agent 6.26× (no-MTP 7.12×)
  - gsm8k 5-shot 200q: 0.955 no-MTP, **0.96 MTP=2** (highest band score)
- MTP=2 acceptance is steady at **68% with accept-length 2.36–2.39**
  across every profile / concurrency tier.

## Deployment recipes

Pick the recipe that matches your traffic shape. All four use mt-bench
prose latencies as the validating workload (`philschmid/mt-bench`,
80 prompts, temperature 1.0).

### Workstation SM120 — Conversation profile (short prompts, multi-user)

Best for chat UIs: max 8 in-flight requests, each ≤16 K tokens of context.

```
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 --block-size 256 \
  --max-model-len 16384 --max-num-seqs 8 \
  --tensor-parallel-size 2 \
  --host 127.0.0.1 --port 8000 \
  --no-enable-flashinfer-autotune \
  --reasoning-parser deepseek_v4 \
  --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 --enable-auto-tool-choice \
  --enable-expert-parallel \
  --gpu-memory-utilization 0.985 \
  --speculative_config '{"method":"deepseek_mtp","num_speculative_tokens":2}'
```

Add `--default-chat-template-kwargs '{"thinking":true}'` if you want
the DSv4 `<think>` block in responses (impacts mt-bench throughput;
see `_T1AT1D_T2A_2760932cf/` for non-thinking apples-to-apples data).

### Workstation SM120 — Agent profile (long context, fewer streams)

Best for code assistants and tool-using agents: ≤4 in-flight requests,
each up to 32 K tokens (tool history + reflection + planning).

```
# Same as Conversation but:
  --max-model-len 32768 --max-num-seqs 4
```

### DGX Spark cluster — Conversation profile

Edge multi-user (e.g. household assistants). Same env layout as the
Conversation baseline, served through `dgx_spark_start_mp_serve.sh`:

```
MAX_MODEL_LEN=32768 MAX_NUM_SEQS=8 \
GPU_MEMORY_UTILIZATION=0.85 \
SERVE_SPECULATIVE_CONFIG='{"method":"deepseek_mtp","num_speculative_tokens":2}' \
SERVE_COMPILATION_CONFIG='{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
scripts/dgx_spark_start_mp_serve.sh
```

(plus the usual `HEAD_HOST`/`HEAD_ROCE_IP`/`NCCL_IB_HCA`/... cluster env.)

### DGX Spark cluster — Agent profile

```
# Same as Spark Conversation but:
MAX_MODEL_LEN=65536 MAX_NUM_SEQS=4
```

## Workstation SM120 (TP=2 EP, gpu-mem 0.985)

### Conversation profile (`max_model_len=16384`, `max_num_seqs=8`)

| c | no-MTP tok/s | no-MTP TPOT (ms) | MTP=2 tok/s | MTP=2 TPOT (ms) | MTP accept % |
|---|---|---|---|---|---|
| 1 | 89.14 | 9.71 | 137.23 | 6.42 | 67.58 |
| 2 | 142.37 | 12.75 | 217.68 | 9.16 | 68.50 |
| 4 | 225.43 | 16.44 | 273.65 | 13.20 | 68.46 |
| 8 | **318.23** | 22.45 | **442.56** | 15.83 | 69.57 |

KV: no-MTP 12.20 GiB / 67,280 tokens / max_concurrency **4.11×**.
MTP=2 10.38 GiB / 57,122 tokens / **3.49×**. The capped capture-size
(max_num_seqs=8 → cudagraph budget shrinks) buys us ≈ 2 GiB of extra
KV vs the open-ended workstation baseline.

### Agent profile (`max_model_len=32768`, `max_num_seqs=4`)

| c | no-MTP tok/s | no-MTP TPOT (ms) | MTP=2 tok/s | MTP=2 TPOT (ms) | MTP accept % |
|---|---|---|---|---|---|
| 1 | 88.99 | 9.74 | 130.01 | 6.46 | 67.78 |
| 2 | 142.43 | 12.75 | 210.94 | 8.76 | 69.51 |
| 4 | 225.02 | 16.53 | 250.62 | 14.39 | 68.69 |

KV: no-MTP 12.23 GiB / 132,045 tokens / **4.03×** for 32K-token requests.
MTP=2 10.48 GiB / 112,966 tokens / **3.45×**. Per-request KV doubles
vs Conversation; the cluster still fits 3–4 max-context streams.

c=1..4 single-stream throughput is statistically identical between the
two profiles (compute-bound at low concurrency); the value of the Agent
profile is "I can attach a 32 K-token context per stream without
falling off the KV cliff."

## DGX Spark cluster (TP=2 PP=1 mp, gpu-mem 0.85)

### Conversation profile (`max_model_len=32768`, `max_num_seqs=8`)

| c | no-MTP tok/s | no-MTP TPOT (ms) | MTP=2 tok/s | MTP=2 TPOT (ms) | MTP accept % |
|---|---|---|---|---|---|
| 1 | 21.24 | 58.13 | 29.79 | 28.97 | 68.75 |
| 2 | 37.92 | 50.11 | 51.73 | 35.82 | 68.43 |
| 4 | 56.26 | 67.47 | 57.95 | 64.65 | 68.66 |
| 8 | **75.89** | 98.49 | **94.72** | 76.71 | 67.95 |

KV: no-MTP 23.04 GiB / 239,617 / **7.31×**. MTP=2 20.73 GiB / 213,425
/ **6.51×**.

### Agent profile (`max_model_len=65536`, `max_num_seqs=4`)

| c | no-MTP tok/s | no-MTP TPOT (ms) | MTP=2 tok/s | MTP=2 TPOT (ms) | MTP accept % |
|---|---|---|---|---|---|
| 1 | 21.14 | 65.52 | 28.51 | 46.39 | 68.34 |
| 2 | 37.42 | 50.97 | 49.55 | 37.49 | 67.42 |
| 4 | 55.53 | 68.90 | 59.66 | 63.08 | 67.88 |

KV: no-MTP 22.50 GiB / 466,819 / **7.12×**. MTP=2 20.31 GiB / 409,934
/ **6.26×**. Each request can stretch to 65 K tokens of context (tool
history + thinking) without forcing the cluster into single-user mode.

## Accuracy

`lm_eval` `gsm8k` 5-shot, 200 questions, `temperature=0`,
`max_gen_toks=2048`, against `/v1/completions` (no chat template — gsm8k
results are unaffected by the thinking flag).

| Cell | strict | flexible |
|---|---|---|
| Workstation no-MTP | 0.950 | 0.950 |
| Workstation MTP=2 | 0.950 | 0.950 |
| Spark no-MTP | 0.955 | 0.955 |
| **Spark MTP=2** | **0.960** | **0.960** |

All four cells sit at or above the historical 0.948–0.965 band recorded
on B200, B300, and the DeepSeek Official API. Spark MTP=2 lands at the
top of the band — the long-context attention budget and the MTP draft
acceptance both work in its favour on math reasoning prompts.

## Use-case decision matrix

Read this as "for use case X, the recommended config and the
throughput you should expect":

| Use case | Workstation | Spark |
|---|---|---|
| Single chat user, short prompts | Conv c=1 MTP=2 → **137 tok/s** | Conv c=1 MTP=2 → 30 tok/s |
| 4–8 chat users, short prompts | Conv c=8 MTP=2 → **442 tok/s** aggregate | Conv c=8 MTP=2 → 95 tok/s aggregate |
| 1 agent, 32 K context | Agent c=1 MTP=2 → **130 tok/s** | Agent c=1 MTP=2 → 29 tok/s |
| 2–4 parallel agents, 32 K each | Agent c=4 MTP=2 → 251 tok/s aggregate | Agent c=4 MTP=2 → 60 tok/s aggregate |
| 1 agent, 65 K context | Use Workstation Agent profile (max-model-len=65K, `_T1AT1D_T2A_2760932cf` numbers); Spark Agent at 65 K works but per-request TTFT scales with chunk count | Spark Agent c=1 → 29 tok/s at 65 K (see `_T1AT1D_T2A_2760932cf` for the long prefill cost curve) |

For Conv on Workstation we still hit 60 % gpu-mem util at c=8 — there is
headroom for a `--max-num-seqs 16` or `--max-num-seqs 24` upgrade if the
deployment really needs >8 simultaneous chats. The Agent profile is more
KV-constrained (32 K per request × 4 streams = 128 K tokens), but still
runs with ≈ 1 max-context stream of safety margin.

## Cold-start considerations

After commit `5c8975591` extended prefill warmup to
`max_num_batched_tokens=8192`, the first request in each new serve
still incurs Triton JIT for any kernel shape *not* covered by the
warmup hook. The TTFT p99 columns in the raw bench JSONs reflect this
(`Spark Conv MTP=2 c=1 TTFT p99 = 15.4 s` is one cold first request
out of 80; the warm steady-state is ~0.8 s). For production servers
the cost is one-time per process; for benchmarks make sure to discard
the first 1–2 requests.

## Reproduction

See `repro_recipe.md` next to this file. Bench JSONs and `lm_eval`
result trees are checked in under `performance/` and `evals/`.

## Source SHAs

- vLLM: `5c8975591` on `jasl/vllm` `ds4-sm120-preview-dev` (PR #41834)
- Harness: this commit
