# DeepSeek V4 SM12x Validation Harness

This is a repo-independent harness for DeepSeek V4 SM12x bring-up. It is
intended to run against an already-started vLLM OpenAI-compatible server.

The harness is deliberately stdlib-only at runtime. Unit tests use `pytest`.

## Local Environment

Copy `env.sample` to `.env` for machine-local settings. `.env` is ignored by
git and is loaded by the wrapper scripts without overriding variables already
set in the shell.

```bash
cp env.sample .env
```

Use `.env` for local paths, benchmark defaults, and the optional DeepSeek
official API reference key:

```bash
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_BETA_BASE_URL=https://api.deepseek.com/beta
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_FLASH_MODEL=deepseek-v4-flash
DEEPSEEK_PRO_MODEL=deepseek-v4-pro
DEEPSEEK_THINKING_TYPE=enabled
DEEPSEEK_REASONING_EFFORT=high
DEEPSEEK_PRESERVE_REASONING_CONTENT=1
```

Never commit `.env`. The harness records only whether `DEEPSEEK_API_KEY` is
present; it does not write the key value into run artifacts.

## DeepSeek Official API Notes

Use these docs as the reference behavior when comparing local vLLM output with
the hosted API:

- [Thinking mode](https://api-docs.deepseek.com/zh-cn/guides/thinking_mode)
- [Chat prefix completion](https://api-docs.deepseek.com/zh-cn/guides/chat_prefix_completion)
- [Tool calls](https://api-docs.deepseek.com/zh-cn/guides/tool_calls)
- [Create chat completion](https://api-docs.deepseek.com/zh-cn/api/create-chat-completion)

The V4 model IDs used by the official API are `deepseek-v4-flash` and
`deepseek-v4-pro`. Prefix-completion probes should use
`DEEPSEEK_BETA_BASE_URL`.

When replaying or capturing official API tool-call conversations in thinking
mode, preserve the assistant message `reasoning_content` field in later
requests after a tool call. Preserve it even when the value is an empty string;
some clients drop empty fields, which can make the official API reject the next
tool-call turn.

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
- HTTP logprobs oracle export and comparison:
  - deterministic `/v1/completions` oracle export for B200/H100 reference runs
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
`artifacts/<branch>/<gpu-topology>/<timestamp>/` by default. The GPU topology
slug is derived from `nvidia-smi`, for example
`2x_nvidia_rtx_pro_6000_blackwell_workstation_edition` or `4x_nvidia_b200`.
Override `GPU_TOPOLOGY_SLUG` when running on a host where `nvidia-smi` is not
available or when you need a shorter label. Override `ARTIFACT_ROOT`,
`BRANCH_NAME`, `RUN_TIMESTAMP`, or `OUT_DIR` when you need an explicit location.

Each wrapper run writes `run_environment.json` and `run_environment.md` with
GPU count/model inventory, selected CUDA env vars, benchmark settings, and
official API configuration state. GPU UUIDs and API key values are not written.

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

The live wrappers guard against server deadlocks or unresponsive vLLM workers.
They run short health probes before expensive live gates and record
`server_unresponsive.txt`, `*.server_unresponsive`, or `*.skipped` artifacts
instead of continuing through every remaining test. Keep `SERVER_GUARD=1` for
B200/SM12x reference runs. Set `SERVER_HEALTH_TIMEOUT=10` to tune the probe
timeout, and set `SERVER_RECOVERY_CMD` only when you explicitly want the
wrapper to run a local recovery command after detecting an unresponsive server.

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

When you have access to an expensive reference host, first export the oracle
bundle from that host while the reference vLLM server is running:

```bash
BASELINE_LABEL=b200_oracle \
ORACLE_LOGPROBS=20 \
scripts/run_oracle_export.sh
```

This writes wrapped `/v1/completions` JSON files, `oracle_export_summary.*`,
`run_environment.*`, GPU telemetry, and runtime telemetry under
`artifacts/<branch>/<gpu-topology>/b200_oracle/<timestamp>/`. If the reference
server was started with a higher `--max-logprobs`, set `ORACLE_LOGPROBS=50`.
Use `ORACLE_CASES=case_a,case_b` only for a deliberately narrow re-run.
The exporter also calls `/tokenize` for each prompt and injects those prompt
token ids into the wrapped completion response, so later `--require-prompt-ids`
comparisons fail when tokenization diverges or token ids are unavailable.
The wrapper uses `ORACLE_STOP_ON_ERROR=1` by default so a deadlocked reference
server consumes only one request timeout before stopping the export.

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
