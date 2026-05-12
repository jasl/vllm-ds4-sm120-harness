# SM120 Workstation Deployment Baseline — 2026-05-12

DeepSeek V4 Flash on **2× NVIDIA RTX PRO 6000 Blackwell Workstation
Edition** (compute capability 12.0, TP=2 EP), vLLM `jasl/vllm` @
`1c20f1a6d` (head of `ds4-sm120-preview-dev` / PR #41834, 17 commits
ahead of `upstream/main`).

This bundle is the reference for desktop / workstation deployments
(2× dedicated PRO 6000 cards, no display). The GB10 / DGX Spark
counterpart lives in `../20260512_gb10_deployment_1c20f1a6d/`.

## TL;DR

- **Conversation profile** (`max_model_len=16384`, `max_num_seqs=8`,
  `gpu-mem 0.985`)
  - no-MTP c=1: **89.14 tok/s**, c=8 saturation: **318.23 tok/s**
  - MTP=2 c=1: **137.23 tok/s**, c=8 saturation: **442.56 tok/s**
- **Agent profile** (`max_model_len=32768`, `max_num_seqs=4`,
  `gpu-mem 0.985`)
  - no-MTP c=1: 88.99 tok/s, c=4 saturation: 225.02 tok/s
  - MTP=2 c=1: 130.01 tok/s, c=4 saturation: 250.62 tok/s
- max_concurrency: Conv no-MTP 4.11× / MTP=2 3.49×; Agent no-MTP
  4.03× / MTP=2 3.45×
- MTP=2 acceptance: 67.6–69.6 %, accept-length 2.35–2.39 across all
  concurrency
- gsm8k 5-shot 200q: **0.950** no-MTP, **0.950** MTP=2

## Recommended deployment commands

### Conversation (short prompts, multi-user up to 8)

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

Append `--default-chat-template-kwargs '{"thinking":true}'` to enable
DSv4's `<think>` block.

### Agent (long context, 1–4 parallel agents)

Same command, with:
```
  --max-model-len 32768 --max-num-seqs 4
```

`gpu-memory-utilization 0.985` is the recommended ceiling on two
dedicated cards (no display). `0.99` fails the static startup check
(94.02 GiB demanded vs 93.94 GiB free on a 96 GiB card after CUDA
context). Drop to `0.95` if the host also drives a display.

## Performance — mt-bench (`philschmid/mt-bench`, 80 prompts, `temperature=1.0`)

### Conversation profile

| c | no-MTP tok/s | no-MTP TPOT (ms) | MTP=2 tok/s | MTP=2 TPOT (ms) | MTP accept % |
|---|---|---|---|---|---|
| 1 | 89.14 | 9.71 | 137.23 | 6.42 | 67.58 |
| 2 | 142.37 | 12.75 | 217.68 | 9.16 | 68.50 |
| 4 | 225.43 | 16.44 | 273.65 | 13.20 | 68.46 |
| 8 | **318.23** | 22.45 | **442.56** | 15.83 | 69.57 |

KV: no-MTP 12.20 GiB / 67,280 tokens / max_concurrency 4.11×.
MTP=2 10.38 GiB / 57,122 tokens / 3.49×. The capped `max_num_seqs=8`
shrinks the CUDA-graph workspace and reclaims ≈ 2 GiB of KV vs the
open-ended `max_num_seqs=256` workstation default.

### Agent profile

| c | no-MTP tok/s | no-MTP TPOT (ms) | MTP=2 tok/s | MTP=2 TPOT (ms) | MTP accept % |
|---|---|---|---|---|---|
| 1 | 88.99 | 9.74 | 130.01 | 6.46 | 67.78 |
| 2 | 142.43 | 12.75 | 210.94 | 8.76 | 69.51 |
| 4 | 225.02 | 16.53 | 250.62 | 14.39 | 68.69 |

KV: no-MTP 12.23 GiB / 132,045 tokens / max_concurrency 4.03× at
32 K-token requests. MTP=2 10.48 GiB / 112,966 tokens / 3.45×.

c=1..4 single-stream throughput is statistically identical between
Conv and Agent profiles (compute-bound at low concurrency); the
Agent profile's value is "I can attach a 32 K-token context per
stream without losing concurrency room."

## Accuracy

`lm_eval` `gsm8k` 5-shot, 200 questions, `temperature=0`,
`max_gen_toks=2048`, via `/v1/completions` (chat-template-independent).

| Variant | strict | flexible |
|---|---|---|
| no-MTP | 0.950 | 0.950 |
| MTP=2 | 0.950 | 0.950 |

Both within the historical 0.948–0.965 band measured on B200, B300,
and the DeepSeek Official API. MTP=2 does not regress strict match.

## Generation reference (Conv profile, MTP=2, non-thinking)

Three representative prompts run on a fresh Conv-profile MTP=2 serve.
`results.jsonl` has the full metadata (latency, token counts, finish
reason). Each `.md` is a self-contained prompt+response transcript;
`aquarium_html` also yields an `.html` artifact that opens in a
browser.

| Case | Lang | Tokens out | Elapsed |
|---|---|---|---|
| aquarium_html | en | ~4,200 | ~25 s |
| aquarium_html | zh | ~4,200 | ~25 s |
| en2zh_news_001 | en | ~700 | ~5 s |
| zh_sum_tech_001 | zh | ~1,200 | ~8 s |

## Use-case decision matrix

| Workload | Recommended cell | Expected throughput |
|---|---|---|
| Single chat user, short prompts | Conv c=1 MTP=2 | **137 tok/s** decode |
| 4–8 chat users, short prompts | Conv c=8 MTP=2 | **442 tok/s** aggregate |
| 1 agent, ≤ 32 K context | Agent c=1 MTP=2 | **130 tok/s** decode |
| 2–4 parallel agents, 32 K each | Agent c=4 MTP=2 | 251 tok/s aggregate |
| 1 agent, 65 K context | Agent profile with `--max-model-len 65536` | TTFT scales with chunk count (≈ 23 s at 65 K prefill) |

Conv at c=8 still leaves headroom — `--max-num-seqs 16` or `24` is
viable if you really need > 8 concurrent chats (see
`20260511_sm120_isl_sweep_020e0c89a/` for c=16/24 reference data on
the prior SHA).

## Cold-start considerations

vLLM `1c20f1a6d` extends the prefill warmup to
`max_num_batched_tokens=8192` (the canonical SM12x serve value), so
the first long-context request no longer pays a full Triton JIT
spike. Bench `TTFT p99` for c=1 is ~1 s; the first single request
out of 80 may still incur ~2–3 s if it hits a kernel shape outside
the warmup envelope. For production servers the cost is one-time per
process.

## Reproduction

See `repro_recipe.md`. Bench JSONs are in `performance/`, gsm8k raw
trees are in `evals/`, generation transcripts in `generation/`.

## Source SHAs

- vLLM: `1c20f1a6d` on `jasl/vllm` `ds4-sm120-preview-dev` (PR
  #41834; data collected at `8f0d8b630`, rebased to add
  `Signed-off-by` trailers — no code changes)
- Harness: this commit
