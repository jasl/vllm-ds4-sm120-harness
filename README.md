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
  - supports representative Hugging Face datasets such as
    `philschmid/mt-bench`
  - keeps random synthetic prompts for controlled short/long context pressure
  - parses common throughput and latency metrics
  - stores raw logs per concurrency
- vLLM runtime telemetry:
  - samples `/metrics` during wrapper runs
  - summarizes prefill/decode token counters, request pressure, and KV-cache
    usage
  - can parse serve logs for prompt/generation throughput and MTP acceptance
    metrics

## Coverage Model

Use the harness as a layered gate, not as one monolithic command:

- Correctness: deterministic quick chat, ToolCall-15, and optional logprobs
  oracle comparison catch parser, CUDA graph, and token-level regressions.
- Production-like behavior: quality and coding smoke cases cover writing,
  translation, tool use, agent-like OpenClaw reads, and long HTML generation.
- Realistic throughput: benchmark with `--dataset-name hf --dataset-path
  philschmid/mt-bench` to avoid pure random prompts when judging user-visible
  progress.
- Synthetic pressure: benchmark with `--dataset-name random` for controlled
  short/long context shapes such as 1024/1024 decode or 8192/512 prefill.
- Serving variants: run no-MTP and MTP as separate server configurations. MTP
  changes generation trajectories, so compare it against a no-MTP baseline
  with the same harness profile.

The full matrix can be expensive. For daily iteration, run the smallest profile
that targets the risk in the change, then run the broader real-scenario matrix
before promoting to a community branch.

MTP can also hit hard memory limits before no-MTP, especially at higher
concurrency. Treat MTP failures at concurrency 8 or above as acceptable capacity
limits when the logs point to VRAM/KV-cache/CUDA-graph pressure; record the
highest passing concurrency and the failure evidence instead of blocking a
change solely on that tier.

`scripts/run_bench_matrix.sh` defaults to the HF/MT-Bench profile. Set
`DATASET_NAME=random IGNORE_EOS=1` when intentionally running random shape
stress tests.

## Artifact Output

The shell wrappers write run output under the repo-local ignored directory
`artifacts/<branch>/<timestamp>/` by default. Override `ARTIFACT_ROOT`,
`BRANCH_NAME`, `RUN_TIMESTAMP`, or `OUT_DIR` when you need an explicit location.

`chat-smoke` can also write Markdown reports with `--markdown-output`. Use this
for writing, translation, math, and other cases that need subjective review; the
JSONL remains available for machine comparison.

The shell wrappers also sample GPU telemetry with `nvidia-smi` when available.
Each run writes `gpu_stats.csv`, `gpu_stats_summary.json`, and
`gpu_stats_summary.md` next to the other artifacts. The summary includes per-GPU
peak/average memory usage, power draw, and utilization. Set `GPU_STATS=0` to
disable sampling, or `GPU_STATS_INTERVAL_SECONDS=2` to change the sample
interval.

The wrappers also sample vLLM runtime metrics from `/metrics` by default. Each
run writes `vllm_metrics.prom`, `runtime_stats_summary.json`, and
`runtime_stats_summary.md` when metrics are available. The summary includes
prefill/decode token deltas, request pressure, and KV-cache usage. Set
`RUNTIME_STATS=0` to disable sampling, or `RUNTIME_STATS_INTERVAL_SECONDS=10`
to reduce polling. If you have the server log path, pass
`SERVE_LOG=/path/to/serve.log`; the summary will also include vLLM log-derived
prompt/generation throughput and speculative decoding acceptance metrics.

## Expected Workflow

Run these after every SM12x kernel optimization before pushing to
`ds4-sm120` or `ds4-sm120-full`:

```bash
cd /path/to/ds4-sm120-harness
python -m pytest -q tests
```

If the harness should run with a specific interpreter or vLLM virtualenv, pass
`PYTHON=/path/to/vllm/.venv/bin/python` to the shell scripts.

```bash
python -m ds4_harness.cli health --base-url http://127.0.0.1:8000

python -m ds4_harness.cli chat-smoke \
  --base-url http://127.0.0.1:8000 \
  --tag quick \
  --jsonl-output artifacts/manual/smoke_quick.jsonl \
  --markdown-output artifacts/manual/smoke_quick.md

python -m ds4_harness.cli chat-smoke \
  --base-url http://127.0.0.1:8000 \
  --tag coding \
  --timeout 900 \
  --jsonl-output artifacts/manual/smoke_coding.jsonl \
  --markdown-output artifacts/manual/smoke_coding.md

python -m ds4_harness.cli toolcall15 \
  --base-url http://127.0.0.1:8000 \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --json-output artifacts/manual/toolcall15.json
```

Use the B200/SM100 or H100 HTTP oracle bundle when you need stricter kernel
correctness checks. Chat exports are covered by `chat-smoke`; `oracle-compare`
only consumes `/v1/completions` logprobs cases.

```bash
python -m ds4_harness.cli oracle-compare \
  --base-url http://127.0.0.1:8000 \
  --oracle-dir /path/to/b200_or_h100_oracle_bundle \
  --top-n 20 \
  --require-prompt-ids \
  --min-top1-match-rate 0.80 \
  --json-output artifacts/manual/oracle_compare.json
```

For realistic throughput checks, run no-MTP and MTP as separate server
configurations, then run the same HF dataset matrix against each:

```bash
VLLM_BIN=/path/to/vllm/.venv/bin/vllm \
SERVE_LOG=/path/to/serve.log \
CONCURRENCY=1,2,4,8,16,24 \
scripts/run_bench_matrix.sh
```

Use random prompts when you need a controlled shape rather than a representative
conversation dataset:

```bash
VLLM_BIN=/path/to/vllm/.venv/bin/vllm \
CONCURRENCY=1,2 \
DATASET_NAME=random \
RANDOM_INPUT_LEN=1024 \
RANDOM_OUTPUT_LEN=1024 \
NUM_PROMPTS=16 \
IGNORE_EOS=1 \
scripts/run_bench_matrix.sh
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
- Real-scenario benchmark on `philschmid/mt-bench` does not regress more than
  the explicitly accepted threshold. Random-shape benchmark regressions are
  useful diagnostics, but should not be the only performance signal.

## Notes

- Do not set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` for TP=2
  CUDA graph runs; it has caused custom all-reduce graph registration failures.
- For agent-like tests, prefer production-like serving flags:
  `--enable-auto-tool-choice`, `--tool-call-parser deepseek_v4`,
  `--reasoning-parser deepseek_v4`, and prefix cache when testing production
  deployment behavior.
- MTP should be tested separately from no-MTP. MTP changes generation behavior
  and can expose scheduler/CUDA graph bugs that are not present in the normal
  decode path. High-concurrency MTP failures can also be plain capacity limits;
  distinguish OOM/KV-cache/CUDA-graph reservation failures from correctness or
  scheduler bugs before treating them as regressions.
