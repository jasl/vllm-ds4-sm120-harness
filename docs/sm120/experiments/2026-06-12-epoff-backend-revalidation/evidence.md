# Evidence

## 2026-06-12 External Checkpoints

Checked with public GitHub pages and `git ls-remote` on 2026-06-12:

| Route | Status | Head |
| --- | --- | --- |
| vLLM upstream/main | upstream baseline reference | `b7f9b6a` |
| `vllm-project/vllm#45277` | open PR for CUDA arch build/runtime coverage gaps | `e57d3b78` |
| `local-inference-lab/vllm dev/black-benediction` | external performance target branch | `c6b2a7b` |
| FlashInfer upstream/main | upstream dependency reference | `d65c3eb` |
| `flashinfer-ai/flashinfer#3395` | unmerged packed SM120 sparse-MLA reference | `88539d03` |
| b12x master | local checkout aligned | `fabb087` |

Local vLLM stable preview baseline:

| Item | Value |
| --- | --- |
| Stable preview tag | `sm120-pr-41834-stable-preview-20260612075245` |
| Stable preview commit | `f32247a5a6` |
| Fallback tag | `sm120-pr-41834-fallback-before-replacement-20260612053720` |
| Backend-parity dev branch | `codex/ds4-sm120-backend-parity-dev-20260612` at `7224e68417` |
| Previous dev checkout during note creation | `codex/ds4-sm120-glm51-experimental-20260612` at `7224e68417` |

## Baseline Extracts

RTX PR stable preview, cold OSL=1 random prefill, EP-off, MTP:

| Input tokens | Requests | Input tok/s | Mean TTFT ms | P99 TTFT ms |
| ---: | ---: | ---: | ---: | ---: |
| 1024 | 8 | 6606.45 | 155.03 | 158.67 |
| 4096 | 8 | 6206.06 | 659.39 | 661.41 |
| 16384 | 8 | 8056.05 | 2033.11 | 2039.00 |
| 65536 | 8 | 7540.46 | 8691.55 | 8770.28 |

RTX PR stable preview, OSL=128 supplement, EP-off, MTP:

| Input tokens | Requests | Input tok/s | Output tok/s | Mean TTFT ms | P99 ITL ms |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4096 | 8 | 3123.74 | 97.60 | 660.21 | 13.29 |
| 16384 | 8 | 6209.00 | 48.51 | 2030.49 | 13.37 |
| 65536 | 8 | 7049.72 | 13.77 | 8715.51 | 14.65 |

RTX GSM8K:

| Task | Fewshot | Limit | Flexible EM | Strict EM | Exit |
| --- | ---: | ---: | ---: | ---: | ---: |
| GSM8K | 5 | 200 | 0.965 | 0.940 | 0 |

GB10 forum53 MTP2 EP-off C=2 prefix-cache gate:

| Requests | Failures | Max TTFT s | ITL p99 s | Prefix hits | Driver health |
| ---: | ---: | ---: | ---: | ---: | --- |
| 4 | 0 | 124.045698 | 0.144954 | 79872 | clean |

## Revalidation Matrix

Run each candidate route as a same-host A/B against the stable preview baseline:

| Gate | RTX / SM120 | GB10 / SM121 |
| --- | --- | --- |
| Cold short prefill | 1024, 4096, 16384, 65536 OSL=1 | 4096, 16384, 32768, 65536 OSL=1 |
| Short throughput | 4096, 16384, 65536 OSL=128 | reduced profile if capacity allows |
| Long-context latency | 59K and 124K C=1/C=2 | guarded long-C2 profile |
| Sparse attribution | candidate/value visits and effective visits/s | same, plus driver health |
| Correctness | GSM8K limit-200, focused vLLM tests | reduced correctness and liveness gates |
| User feedback | prefix-cache, KV lifecycle, mixed/decode pressure | forum53 and MTP2 MoE TP gates |

Accept a route for promotion only when the endpoint A/B explains the gain:
reduced real sparse-MLA work, improved effective visits/s, lower memory
pressure, or a measurable MoE/decode-pipeline fix. A startup-only or
microbench-only improvement is not enough.
