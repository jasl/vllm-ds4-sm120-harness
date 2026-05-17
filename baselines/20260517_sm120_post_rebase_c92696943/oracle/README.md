# Oracle Top-K Logprobs Export

Token-level top-20 logprob captures for 5 deterministic probe cases, taken
against the **nomtp** variant at this revision (`vllm@c92696943` on 2× RTX PRO
6000 Blackwell Workstation Edition). Intended for cross-platform alignment
audits — a port team can replay the same prompts on their reimplementation
and compare top-K logprob lists position-by-position against this reference.

## Cases (all `temperature=0.0, logprobs=20`)

| Case | Prompt theme | max_tokens | Workload signature |
| --- | --- | ---: | --- |
| `completion_short_math_logprobs20` | `7*8?` | 16 | short decode |
| `completion_raw_intro_logprobs20` | local LLM intro | 96 | short prefill + decode |
| `completion_translation_logprobs20` | EN→ZH translation | 128 | mixed multilingual |
| `completion_code_probe_logprobs20` | Python function | 160 | code generation |
| `completion_long_prefill_2048_logprobs20` | 260-line context retrieval | 64 | **long prefill (~6280 prompt tokens)** |

Each case has two files:

- `completion_<name>.json` — the response with token-level `top_logprobs` lists
- `tokenize_<name>.json` — the prompt's token id breakdown (for byte-exact
  prompt-tokenization comparison)

Plus aggregate summaries: `oracle_export_summary.json` / `.md`.

## Why nomtp only

Speculative decoding (MTP=2 production) produces an acceptance-filtered token
stream; the top-K logprobs from the verifier model aren't identical to the
greedy-decode logprobs a port team would replicate. Oracle parity is most
useful with MTP off so the token stream is a deterministic argmax sequence.

## Reproducing

Launch a nomtp serve at `:8000`, then:

```bash
PYTHON=/path/.venv/bin/python \
OUT_DIR=/path/out \
BASE_URL=http://127.0.0.1:8000 \
MODEL=deepseek-ai/DeepSeek-V4-Flash \
ORACLE_LOGPROBS=20 \
BASELINE_LABEL=oracle_nomtp_c92696943 \
bash scripts/run_oracle_export.sh
```

Captured here in ~25 seconds end-to-end.
