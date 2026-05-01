# DeepSeek V4 SM12x Validation Harness

This is a repo-independent harness for DeepSeek V4 SM12x bring-up. It is
intended to run against an already-started vLLM OpenAI-compatible server.

The harness is deliberately stdlib-only at runtime. Unit tests use `pytest`.

## What It Covers

- Live chat smoke cases:
  - basic deterministic math and language checks
  - tool-call routing with the collected OpenClaw `read` case
  - instruction-following writing check
  - subjective writing and translation checks for prior quality reports
  - long HTML coding prompts collected from user reports
- ToolCall-15 multi-turn tool-call loop:
  - 15 deterministic scenarios across tool selection, parameter precision,
    multi-step chains, restraint/refusal, and error recovery
  - mocked tool responses are returned through OpenAI-compatible `tool`
    messages
- HTTP logprobs oracle comparison:
  - token sequence divergence
  - prompt token id mismatch
  - top-1 match rate
  - top-k overlap
  - common-token logprob deltas
  - `request_*.json` / `response_*.json` bundles and wrapped
    `/v1/completions` export files
- vLLM `bench serve` matrix wrapper:
  - parses common throughput and latency metrics
  - stores raw logs per concurrency

## Expected Workflow

Run these after every SM12x kernel optimization before pushing to
`ds4-sm120` or `ds4-sm120-full`:

```bash
cd /path/to/ds4-sm120-harness
python -m pytest -q tests

If the harness should run with a specific interpreter or vLLM virtualenv, pass
`PYTHON=/path/to/vllm/.venv/bin/python` to the shell scripts.

python -m ds4_harness.cli health --base-url http://127.0.0.1:8000

python -m ds4_harness.cli chat-smoke \
  --base-url http://127.0.0.1:8000 \
  --tag quick \
  --jsonl-output /tmp/ds4-sm120-smoke-quick.jsonl

python -m ds4_harness.cli chat-smoke \
  --base-url http://127.0.0.1:8000 \
  --tag coding \
  --timeout 900 \
  --jsonl-output /tmp/ds4-sm120-smoke-coding.jsonl

python -m ds4_harness.cli toolcall15 \
  --base-url http://127.0.0.1:8000 \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --json-output /tmp/ds4-sm120-toolcall15.json
```

Use the B200/SM100 or H100 HTTP oracle bundle when you need stricter kernel
correctness checks. Chat exports are covered by `chat-smoke`; `oracle-compare`
only consumes `/v1/completions` logprobs cases.

```bash
python -m ds4_harness.cli oracle-compare \
  --base-url http://127.0.0.1:8000 \
  --oracle-dir /path/to/b200_or_h100_oracle_bundle \
  --require-prompt-ids \
  --min-top1-match-rate 0.80 \
  --json-output /tmp/ds4-sm120-oracle.json
```

For throughput checks, run no-MTP and MTP as separate server configurations,
then run the same matrix against each:

```bash
python -m ds4_harness.cli bench-matrix \
  --vllm-bin /path/to/vllm/.venv/bin/vllm \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --host localhost \
  --port 8000 \
  --concurrency 1,4,8 \
  --random-input-len 1024 \
  --random-output-len 1024 \
  --num-prompts 48 \
  --ignore-eos \
  --json-output /tmp/ds4-sm120-bench.json \
  --log-dir /tmp/ds4-sm120-bench-logs
```

## Recommended Gates

Before promoting an optimization:

- `pytest -q tests` passes.
- `chat-smoke --tag quick` passes.
- `chat-smoke --tag quality` and `chat-smoke --tag coding` have no regression
  versus the previous branch.
- `toolcall15` passes, or any partial/fail scenario is explained with trace
  evidence.
- `oracle-compare` has matching prompt token ids and no early token divergence
  on deterministic oracle cases, or any divergence is explained and recorded.
- Benchmark does not regress more than the explicitly accepted threshold.

## Notes

- Do not set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` for TP=2
  CUDA graph runs; it has caused custom all-reduce graph registration failures.
- For agent-like tests, prefer production-like serving flags:
  `--enable-auto-tool-choice`, `--tool-call-parser deepseek_v4`,
  `--reasoning-parser deepseek_v4`, and prefix cache when testing production
  deployment behavior.
- MTP should be tested separately from no-MTP. MTP changes generation behavior
  and can expose scheduler/CUDA graph bugs that are not present in the normal
  decode path.
