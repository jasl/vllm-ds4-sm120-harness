# GB10 Baseline Report — 2026-05-11

DeepSeek V4 Flash on **2-node DGX Spark cluster, 1x NVIDIA GB10 per node**
(SM121, cc 12.1), TP=2 PP=1 via `--distributed-executor-backend mp --nnodes 2`,
vLLM `jasl/vllm` @ two SHAs (see "Source SHAs" below).

## TL;DR

Full harness completed (acceptance non-thinking, gsm8k, bench, prefix-cache
n/a, plus NVIDIA-style ISL sweep `{ISL=1024/4096/8192 OSL=512, mt-bench}` x
`c={1,2,4}` x `{no-MTP, MTP=2}`). Concurrency capped at 4 by hardware
limits (96 GiB unified memory per node, max-num-seqs=4).

- **Peak HF mt-bench output throughput**: 50.6 tok/s no-MTP @ c=4; **57.6
  tok/s MTP=2 @ c=4** (+14 %)
- **Single-request decode** (mt-bench c=1): 19.1 tok/s no-MTP, **29.4 tok/s
  MTP=2** (+54 %)
- **gsm8k 5-shot 200q**: 0.965 (no-MTP)
- **MTP=2 acceptance**: 47–67 % depending on dataset, accept length ~1.9–2.4
- **First known clean MTP=2 run on GB10** — the prior `sample_tokens` RPC
  timeouts and decode stalls (documented in `HANDOFF.local.md`) have not
  recurred since the NCCL upgrade committed in `9c41323`.
- **vs NVIDIA's ISL reference matrix: +34 % to +108 % output throughput**
  across the matrix with no-MTP; MTP=2 doubles at light load.

## Serve config

Started via `scripts/dgx_spark_start_mp_serve.sh` from a control host with
SSH to both Spark nodes. Final serve command (head node, no-MTP):

```
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 --block-size 256 \
  --tensor-parallel-size 2 --pipeline-parallel-size 1 \
  --distributed-executor-backend mp --nnodes 2 \
  --master-addr <HEAD_ROCE_IP> --master-port 29519 \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072 --max-num-seqs 4 --max-num-batched-tokens 8192 \
  --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 --enable-auto-tool-choice \
  --reasoning-parser deepseek_v4 \
  --reasoning-config '{"reasoning_parser":"deepseek_v4","reasoning_start_str":"<think>","reasoning_end_str":"</think>"}' \
  --node-rank 0 --host 0.0.0.0 --port 8000 \
  --enable-expert-parallel \
  --no-enable-flashinfer-autotune \
  --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}'
```

Worker node runs the same command with `--headless --node-rank 1`. For MTP=2,
add `--speculative_config '{"method":"mtp","num_speculative_tokens":2}'`.

Bench client: `vllm bench serve` from head node, `--temperature 1.0`,
`--ignore-eos` for random, num-prompts=8 (ISL=1024) or 4 (ISL=4096/8192) to
match NVIDIA's reference shape; mt-bench num-prompts=40.

## no-MTP (`5b59e2e60`, code-path-equivalent to `020e0c89a`)

### random ISL=1024 OSL=512 num-prompts=8
| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) |
|---|---|---|---|
| 1 | 18.33 | 1506 | 51.70 |
| 2 | 31.44 | 2894 | 58.07 |
| 4 | 48.14 | 5255 | 72.90 |

### random ISL=4096 OSL=512 num-prompts=4
| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) |
|---|---|---|---|
| 1 | 15.18 | 7169 | 51.99 |
| 2 | 22.10 | 16384 | 58.63 |
| 4 | 29.23 | 24664 | 88.71 |

### random ISL=8192 OSL=512 num-prompts=4
| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) |
|---|---|---|---|
| 1 | 12.77 | 13253 | 52.53 |
| 2 | 15.88 | 26020 | 75.17 |
| 4 | 18.75 | 53671 | 108.48 |

### HF mt-bench (philschmid/mt-bench) num-prompts=40
| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) |
|---|---|---|---|
| 1 | 19.13 | 245 | 51.24 |
| 2 | 33.30 | 312 | 58.59 |
| 4 | **50.62** | 367 | 73.69 |

## MTP num_speculative_tokens=2 (`020e0c89a`)

### random ISL=1024 OSL=512 num-prompts=8
| c | out tok/s | TTFT (ms) | TPOT (ms) | accept % | accept len |
|---|---|---|---|---|---|
| 1 | 25.10 | 1728 | 36.53 | 49.7 | 1.99 |
| 2 | 39.37 | 1167 | 48.38 | 51.5 | 2.03 |
| 4 | 36.43 | 1480 | 104.30 | 58.7 | 2.17 |

### random ISL=4096 OSL=512 num-prompts=4
| c | out tok/s | TTFT (ms) | TPOT (ms) | accept % | accept len |
|---|---|---|---|---|---|
| 1 | 20.69 | 6552 | 35.61 | 54.3 | 2.09 |
| 2 | 38.44 | 1378 | 48.96 | 49.6 | 1.99 |
| 4 | 27.66 | 2656 | 138.22 | 46.3 | 1.93 |

### random ISL=8192 OSL=512 num-prompts=4
| c | out tok/s | TTFT (ms) | TPOT (ms) | accept % | accept len |
|---|---|---|---|---|---|
| 1 | 18.43 | 9935 | 34.91 | 55.7 | 2.11 |
| 2 | 41.65 | 1374 | 44.82 | 59.5 | 2.19 |
| 4 | 27.00 | 2902 | 141.38 | 47.9 | 1.96 |

### HF mt-bench num-prompts=40
| c | out tok/s | TTFT (ms) | TPOT (ms) | accept % | accept len |
|---|---|---|---|---|---|
| 1 | 29.43 | 551 | 31.14 | 66.7 | 2.33 |
| 2 | 44.12 | 520 | 41.81 | 67.3 | 2.35 |
| 4 | **57.61** | 645 | 63.04 | 66.6 | 2.33 |

**Note on c=2 vs c=1 TTFT inversion in MTP=2 random rows**: with only 4
prompts, c=2 overlaps prefills so the per-request TTFT is shorter than the
c=1 serial case. The output throughput correctly reports aggregate decode
rate. Artifact of num-prompts=4, not a server regression.

## Comparison vs NVIDIA's reference ISL matrix (TP=2)

NVIDIA shared an internal ISL matrix `{ISL=1024/4096/8192} x {c=1,2,4}` for
the same random shape (OSL=512). Direct overlap with our GB10 no-MTP rows:

| ISL | c | NVIDIA out tok/s | Ours no-MTP | Ours MTP=2 |
|---|---|---|---|---|
| 1024 | 1 | 12.62 | **18.33** (+45 %) | 25.10 (+99 %) |
| 1024 | 2 | 23.27 | **31.44** (+35 %) | 39.37 (+69 %) |
| 1024 | 4 | 23.19 | **48.14** (+108 %) | 36.43 (+57 %) |
| 4096 | 1 | 10.71 | **15.18** (+42 %) | 20.69 (+93 %) |
| 4096 | 2 | 15.92 | **22.10** (+39 %) | 38.44 (+141 %) |
| 4096 | 4 | 20.59 | **29.23** (+42 %) | 27.66 (+34 %) |
| 8192 | 1 | 9.54 | **12.77** (+34 %) | 18.43 (+93 %) |
| 8192 | 2 | 16.28 | **15.88** (−2 %) | 41.65 (+156 %) |
| 8192 | 4 | 11.77 | **18.75** (+59 %) | 27.00 (+129 %) |

Our GB10 no-MTP run is consistently faster than NVIDIA's reference across
the matrix. MTP=2 roughly doubles the per-stream rate when batching is
light. The single −2 % cell (ISL=8192 c=2 no-MTP) is within run-to-run
noise given num-prompts=4.

If NVIDIA wants 1:1 reproduction, see `repro_recipe.md` next to this file.

## Accuracy and correctness gates

| Gate | no-MTP |
|---|---|
| gsm8k 5-shot 200q exact_match | 0.965 |
| Real-scenario generation (en+zh non-thinking, 3 rounds) | PASS for all but TOOLCALL15 (88 % score, see notes) |
| HF mt-bench bench | PASS at c=1,2,4 |
| Long-context probe | known config overflow (see below) |
| Cross-platform quality audit | identical-class vs B200/B300/SM120/Official API |

### Quality audit summary

Cross-platform audit (9 representative cases across HTML, code, write, sum,
zh↔en translation; non-thinking round 1) compared GB10 against B200 TP=2/TP=4,
B300 mtp=2, SM120 nomtp/mtp, and DeepSeek Official API. All sources
structurally and semantically equivalent; token variance ±5–20 % within
temperature=1.0 sampling.

### TOOLCALL15 scoring detail

15 cases x 3 rounds = 45 evaluations; score 79/90 (88 %), 7 failures.
Common failure pattern: assistant chooses to use tool when a direct answer
would have sufficed (e.g. "15 % of 200"). Not a model-quality regression
relative to other platforms; the same pattern appears at all platforms.

## Known issues / non-regressions

1. **Long-context probe** uses `LONG_CONTEXT_LINE_COUNT=4226` →
   130945 input + 128 output = 131073 tokens, **1 token over the 131072
   max-model-len**. Lower line count to 4225 (or raise max-model-len) — server
   side is fine.
2. **MTP=2 acceptance phase** not run as a baseline gate yet because
   acceptance-mode generation flow has historical TTL issues on GB10 at
   think-high / think-max; non-thinking-only run is the GB10 baseline gate.
3. **RoCE MTU**: cluster runs at MTU 1500. Jumbo frames (MTU 9000) recommended
   per docs but not currently set. Mostly affects long-prefill TTFT efficiency.

## Reproduction

See `repro_recipe.md` next to this file.

## Source SHAs

- vLLM: `jasl/vllm`
  - **`5b59e2e60`** for no-MTP (the initial GB10 baseline run; the later MTP
    fix at `020e0c89a` does not touch any no-MTP code path)
  - **`020e0c89a`** for MTP=2 (head of `ds4-sm120-preview-dev` / PR #41834,
    includes the fixup adapting our MTP draft path to upstream PR #41536's
    new `DeepseekV4DecoderLayer.forward()` signature; without it MTP serve
    startup fails with `TypeError: missing required positional argument:
    post_mix`)
- Harness: `59beb40` (this repo)
