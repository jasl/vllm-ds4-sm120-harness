# SM120 Baseline Report — 2026-05-11

DeepSeek V4 Flash on **2x RTX Pro 6000 Blackwell Workstation Edition**
(SM120, cc 12.0), TP=2 EP, vLLM `jasl/vllm` @ `020e0c89a` (head of
`ds4-sm120-preview-dev` / PR #41834).

## TL;DR

Full harness completed (acceptance, gsm8k, bench, prefix-cache, plus
NVIDIA-style ISL sweep `{ISL=1024/4096/8192 OSL=512, mt-bench}` x
`c={1,2,4,8,16,24}` x `{no-MTP, MTP=2}`).

- **Peak HF mt-bench output throughput**: 557 tok/s no-MTP @ c=24; **706 tok/s
  MTP=2 @ c=24** (+27%)
- **Single-request decode** (mt-bench c=1): 84 tok/s no-MTP, **151 tok/s MTP=2**
- **gsm8k 5-shot 200q**: 0.955 no-MTP, 0.965 MTP=2 (historical band 0.948–0.965)
- **MTP=2 acceptance**: 47–69 % depending on dataset, accept length ~2.0–2.4
- vs SGLang PR #24303 same hardware: **~3.0x faster no-MTP, ~5.4x with MTP=2**
- Cross-platform quality audit vs B200 TP=2/TP=4, B300, DeepSeek Official API:
  **identical-class** semantically

## Serve config

```
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 --block-size 256 \
  --max-model-len 65536 --tensor-parallel-size 2 \
  --host 127.0.0.1 --port 8000 \
  --no-enable-flashinfer-autotune \
  --tokenizer-mode deepseek_v4 \
  --reasoning-parser deepseek_v4 \
  --tool-call-parser deepseek_v4 --enable-auto-tool-choice \
  --reasoning-config '{"reasoning_parser":"deepseek_v4","reasoning_start_str":"<think>","reasoning_end_str":"</think>"}' \
  --enable-expert-parallel \
  --gpu-memory-utilization 0.95 \
  --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}'
```

For MTP=2: append `--speculative_config '{"method":"mtp","num_speculative_tokens":2}'`.

Bench client: `vllm bench serve`, `--temperature 1.0`, `--ignore-eos` for
random shapes, `num-prompts=24` for random, `num-prompts=80` for mt-bench.

## no-MTP (`020e0c89a`)

### random ISL=1024 OSL=512
| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) |
|---|---|---|---|
| 1 | 81.41 | 304 | 11.71 |
| 2 | 148.72 | 181 | 13.12 |
| 4 | 245.42 | 411 | 15.52 |
| 8 | 325.55 | 2157 | 20.40 |
| 16 | 382.31 | 3227 | 27.70 |
| 24 | 474.56 | 5013 | 40.81 |

### random ISL=4096 OSL=512
| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) |
|---|---|---|---|
| 1 | 67.69 | 1497 | 11.87 |
| 2 | 105.60 | 2249 | 14.57 |
| 4 | 144.47 | 4295 | 19.33 |
| 8 | 177.61 | 7177 | 31.05 |
| 16 | 190.80 | 12798 | 48.89 |
| 24 | 212.01 | 22375 | 69.38 |

### random ISL=8192 OSL=512
| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) |
|---|---|---|---|
| 1 | 54.20 | 3360 | 11.91 |
| 2 | 76.42 | 5040 | 16.36 |
| 4 | 95.01 | 9555 | 23.47 |
| 8 | 105.17 | 14737 | 47.34 |
| 16 | 110.60 | 26379 | 85.87 |
| 24 | 115.69 | 48647 | 112.14 |

### HF mt-bench (philschmid/mt-bench, ~69 in / ~190 out)
| c | out tok/s | TTFT mean (ms) | TPOT mean (ms) |
|---|---|---|---|
| 1 | 84.36 | 59 | 11.60 |
| 2 | 147.24 | 69 | 13.08 |
| 4 | 244.05 | 76 | 15.62 |
| 8 | 356.67 | 111 | 20.79 |
| 16 | 479.98 | 167 | 29.94 |
| 24 | **557.24** | 330 | 36.81 |

## MTP num_speculative_tokens=2 (`020e0c89a`)

### random ISL=1024 OSL=512
| c | out tok/s | TTFT (ms) | TPOT (ms) | accept % | accept len |
|---|---|---|---|---|---|
| 1 | 125.47 | 314 | 7.37 | 52.4 | 2.05 |
| 2 | 196.90 | 400 | 9.23 | 58.5 | 2.17 |
| 4 | 215.65 | 677 | 17.16 | 54.2 | 2.08 |
| 8 | 340.29 | 1204 | 20.47 | 57.3 | 2.15 |
| 16 | 405.82 | 2845 | 27.72 | 59.3 | 2.19 |
| 24 | 497.67 | 4707 | 36.52 | 56.6 | 2.13 |

### random ISL=4096 OSL=512
| c | out tok/s | TTFT (ms) | TPOT (ms) | accept % | accept len |
|---|---|---|---|---|---|
| 1 | 93.71 | 1529 | 7.70 | 49.7 | 1.99 |
| 2 | 126.94 | 1789 | 12.26 | 49.5 | 1.99 |
| 4 | 138.12 | 2210 | 24.41 | 50.0 | 2.00 |
| 8 | 184.50 | 4084 | 34.87 | 52.8 | 2.06 |
| 16 | 198.48 | 10959 | 53.45 | 52.1 | 2.04 |
| 24 | 210.52 | 21372 | 67.72 | 51.7 | 2.03 |

### random ISL=8192 OSL=512
| c | out tok/s | TTFT (ms) | TPOT (ms) | accept % | accept len |
|---|---|---|---|---|---|
| 1 | 69.15 | 3416 | 7.80 | 48.3 | 1.97 |
| 2 | 87.09 | 3807 | 15.55 | 49.2 | 1.98 |
| 4 | 91.22 | 5334 | 33.33 | 47.7 | 1.95 |
| 8 | 108.42 | 9734 | 54.46 | 49.3 | 1.99 |
| 16 | 107.80 | 38027 | 56.26 | 47.8 | 1.96 |
| 24 | 107.92 | 55266 | 54.09 | 49.6 | 1.99 |

### HF mt-bench
| c | out tok/s | TTFT (ms) | TPOT (ms) | accept % | accept len |
|---|---|---|---|---|---|
| 1 | 151.08 | 66 | 6.26 | 68.8 | 2.38 |
| 2 | 237.22 | 81 | 7.92 | 68.6 | 2.37 |
| 4 | 282.91 | 104 | 13.25 | 68.7 | 2.37 |
| 8 | 462.11 | 172 | 15.57 | 69.0 | 2.38 |
| 16 | 617.07 | 220 | 22.94 | 68.0 | 2.36 |
| 24 | **705.94** | 297 | 28.38 | 67.6 | 2.35 |

## Comparison vs SGLang PR #24303 (same hardware, TP=2)

[Comment 4412004317](https://github.com/sgl-project/sglang/pull/24303#issuecomment-4412004317)
reports curl-based bench on 2x RTX Pro 6000:

| Metric | SGLang #24303 | Ours no-MTP | Ours MTP=2 |
|---|---|---|---|
| Single-request decode (mt-bench c=1) | ~27.7–28.5 tok/s | **84.36** tok/s | **151.08** tok/s |
| 4-concurrent per-stream (mt-bench c=4) | ~18.5 tok/s | **~61** tok/s | **~71** tok/s |
| Prefill rate ~3500 tokens | ~180–200 tok/s | ~2680 tok/s (ISL=4096 1.5s TTFT) | similar |

Speedup: **~3.0x no-MTP, ~5.4x MTP=2** at single-request decode. Sources of
gap: vLLM `cudagraph_mode=FULL_AND_PIECEWISE` (5 mixed + 3 full-decode graphs
vs SGLang's single `--cuda-graph-bs 1`), `custom_ops=["all"]` fused
norm+quant/act+quant kernels, fp8 fused MoE routing via
`Route SM12x DeepGEMM fallbacks`, portable sparse MLA Triton kernels, and
startup warmup eliminating first-batch JIT.

## Accuracy and correctness gates

| Gate | no-MTP | MTP=2 |
|---|---|---|
| gsm8k 5-shot 200q exact_match | 0.955 | 0.965 |
| Real-scenario generation (en+zh, non-thinking/think-high/think-max, 3 rounds) | PASS | PASS |
| Prefix-cache probe | PASS | PASS |
| Long-context probe | known config overflow (see below) | same |
| Cross-platform quality audit | identical-class vs B200/B300/Official API | identical-class |

### Quality audit summary

Cross-platform audit (9 representative cases across HTML, code, write, sum,
zh↔en translation; non-thinking round 1) compared SM120 nomtp/mtp against
B200 TP=2/TP=4 (production reference), B300 mtp=2, and DeepSeek Official API.
All sources structurally and semantically equivalent; token variance ±5–20 %
within temperature=1.0 sampling. One sampled case (`zh_code_alg_001.1.non-thinking`)
showed B200 TP=4 producing English where Chinese was required; SM120 nomtp/mtp
correctly produced Chinese — not a regression in our port.

## Known issues / non-regressions

1. **Long-context probe** uses `LONG_CONTEXT_LINE_COUNT=4226` →
   65409 input + 128 output = 65537 tokens, **1 token over the 65536
   max-model-len**. Lower line count to 4225 (or raise max-model-len) — server
   side is fine.
2. **KV layout probe** expects packed FP8 indexer-cache helper which is
   B200/B300 (SM10x) only. The probe correctly reports "packed helper was
   unavailable" and the harness continues; treat exit-code 1 as informational.
3. **Acceptance phase exit-code 1** when think-max generation hits the 32768
   token gate cap on a few long cases. Raise `GENERATION_MAX_CASE_TOKENS` if
   strict think-max gating is needed.

## Reproduction

See `repro_recipe.md` next to this file.

## Source SHAs

- vLLM: `jasl/vllm` `020e0c89a` (head of `ds4-sm120-preview-dev` / PR #41834)
- Harness: `59beb40` (this repo, commit `scripts: pass --reasoning-config so
  thinking_token_budget works`)

The vLLM SHA includes a fixup absorbed into
`Stabilize DeepSeek V4 MTP scheduling` that adapts the MTP draft path to
upstream PR #41536's new `DeepseekV4DecoderLayer.forward()` signature.
Without it, MTP serve startup fails with
`TypeError: missing required positional argument: post_mix` during
`profile_run`. no-MTP path is unaffected.
