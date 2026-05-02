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

Thinking controls follow the official OpenAI-compatible request shape:
`thinking` is a top-level object such as `{"type":"enabled"}` or
`{"type":"disabled"}`, and `reasoning_effort` is a top-level string such as
`high` or `max`. Do not send tokenizer-internal aliases such as
`enable_thinking` from this harness.

When replaying or capturing official API tool-call conversations in thinking
mode, preserve the assistant message `reasoning_content` field in later
requests after a tool call. Preserve it even when the value is an empty string;
some clients drop empty fields, which can make the official API reject the next
tool-call turn.

## What It Covers

- Live chat smoke cases:
  - basic deterministic math and language checks
  - tool-call routing with the collected OpenClaw `read` case
- Directory-driven generation scenarios:
  - Markdown prompts under `prompts/en/` and `prompts/zh/`
  - `en` and `zh` are organizational groups; the requested output language is
    defined by each prompt
  - writing, translation, and long HTML coding prompts for human review
  - default matrix of `non-thinking`, `think-high`, and `think-max`
- ToolCall-15 multi-turn tool-call loop:
  - 15 deterministic scenarios across tool selection, parameter precision,
    multi-step chains, restraint/refusal, and error recovery
  - follows the upstream
    [`stevibe/ToolCall-15`](https://github.com/stevibe/ToolCall-15) English
    scenario set and scoring model
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
- Optional `lm_eval` accuracy gate:
  - defaults to GSM8K with OpenAI-compatible `local-completions`
  - records exact-match metrics, command shape, stdout/stderr, and raw
    `lm_eval` JSON output
  - intended for expensive reference captures and branch-promotion checks, not
    every local edit
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
- Production-like behavior: default generation prompts cover English-group and
  Chinese-group writing, translation, and long HTML generation. ToolCall-15 is
  a separate authoritative agentic/tool-use suite.
- Realistic throughput: benchmark with `--dataset-name hf --dataset-path
  philschmid/mt-bench` to avoid pure random prompts when judging user-visible
  progress.
- Synthetic pressure: benchmark with `--dataset-name random` for controlled
  short/long context shapes such as 1024/1024 decode or 8192/512 prefill.
- Public accuracy: run the optional `lm_eval` GSM8K phase on reference hosts
  and promotion candidates. This provides a public scalar correctness signal
  similar to the ROCm DeepSeek V4 support PRs, while oracle comparison remains
  the stricter token-level kernel gate.
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

## Generation Prompts

Human-review generation cases live as Markdown files under `prompts/en/` and
`prompts/zh/`. Add a new file to either directory to include it in the default
matrix. The directory name is only a grouping label; the prompt text controls
the requested output language.

Optional front matter is parsed with the stdlib-only harness parser:

```markdown
---
tags: writing, subjective, user-report
max_tokens: 2048
temperature: 1.0
top_p: 1.0
min_chars: 400
all_terms: Context:, Recommendation:
any_terms: privacy, latency
forbidden_terms: as an ai
require_html_artifact: false
---
Write the actual user prompt here.
```

Use `tags` to classify the workload as `writing`, `translation`, `coding`, or
`reading_summary`. The checked-in benchmark suite uses prompts converted from
`tmp/llm_benchmark_prompt_suite/llm_benchmark_prompt_suite_api.jsonl`; the
HTML animation/clock prompts are retained as user-reported cases. The
expectation fields are lightweight sanity checks; the Markdown transcript is
still the source for subjective quality review.

## Artifact Output

The shell wrappers write run output under the repo-local ignored directory
`artifacts/<branch>/<gpu-topology>/<timestamp>/` by default. The default
timestamp format is `YYYYMMDDHHMMSS`. The GPU topology slug is derived from
`nvidia-smi`, for example
`2x_nvidia_rtx_pro_6000_blackwell_workstation_edition` or `4x_nvidia_b200`.
Override `GPU_TOPOLOGY_SLUG` when running on a host where `nvidia-smi` is not
available or when you need a shorter label. Override `ARTIFACT_ROOT`,
`BRANCH_NAME`, `RUN_TIMESTAMP`, or `OUT_DIR` when you need an explicit location.

Each wrapper run writes `run_environment.json` and `run_environment.md` with
GPU count/model inventory, selected CUDA env vars, benchmark settings, and
official API configuration state. GPU UUIDs and API key values are not written.

`chat-smoke` can also write Markdown reports with `--markdown-output` and can
repeat selected deterministic cases with `--repeat-count`.

`generation-matrix` reads Markdown prompts from `prompts/<group>/*.md`, writes
one transcript per prompt/round/thinking-mode/serving-variant under
`generation/<group>/`, and writes machine-readable rows to `generation.jsonl`.
Transcript filenames use
`<prompt-name>.<round>.<thinking-mode>.<variant>.md`, for example
`generation/zh/zh2en_tech_001.2.think-max.mtp.md`. Each transcript keeps
the prompt, assistant answer, `OK`, detail, model, finish reason, full usage
JSON, thinking mode, thinking strength, `temperature`, and `top_p` so
subjective review can be tied back to the exact request shape. Generation
defaults use `temperature=1.0` and `top_p=1.0`, matching the DeepSeek V4
sampling recommendation used for quality-oriented comparisons.

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
prompt/generation throughput and speculative decoding acceptance metrics. The
wrapper records `serve_log_offset.txt` when a phase starts and parses only the
appended lines into `serve_log_phase.log`, so log-derived MTP acceptance metrics
remain phase-local even when multiple harness phases share one vLLM server log.

Each wrapper also downloads and runs the official vLLM `collect_env.py` script
by default. It stores `vllm_collect_env.py`, `vllm_collect_env.sha256`,
`vllm_collect_env.txt`, `vllm_collect_env.err`, and
`vllm_collect_env.exit_code` in the run artifact directory. Set
`VLLM_COLLECT_ENV=0` when running offline or when you want to inspect the
downloaded script manually before execution. Override `VLLM_COLLECT_ENV_URL`
only for a pinned or locally mirrored copy.

The live wrappers guard against server deadlocks or unresponsive vLLM workers,
without treating slow model load or first-request warmup as a deadlock. They
wait up to `SERVER_STARTUP_TIMEOUT=1800` seconds before the live gate sequence,
then use short health probes before expensive live gates. After a failed live
gate or benchmark, they wait up to `SERVER_FAILURE_GRACE_TIMEOUT=300` seconds
before recording `server_unresponsive.txt`, `*.server_unresponsive`, or
`*.skipped` artifacts. Benchmark recovery checks also run a tiny
`/v1/completions` probe with `SERVER_FAILURE_PROBE_TIMEOUT=30`, so a live
`/health` endpoint does not mask a wedged generation path. Keep
`SERVER_GUARD=1` for B200/SM12x reference runs. Set `SERVER_HEALTH_TIMEOUT=10`
to tune the health probe timeout, and set `SERVER_RECOVERY_CMD` only when you
explicitly want the wrapper to run a local recovery command after detecting an
unresponsive server.

To turn a finished artifact tree into a checked-in baseline bundle, run:

```bash
BASELINE_RUN_DIR=artifacts/main/4x_nvidia_b200/b200_main_51295793a/20260501184103 \
BASELINE_REPORT_TITLE="B200 vLLM Main DeepSeek V4 Flash Baseline" \
BASELINE_REPORT_LABEL=b200_main_51295793a \
scripts/generate_baseline_bundle.sh
```

The baseline bundle is written to
`baselines/<YYYYMMDD>_<label>/`. It contains `report.md` plus sanitized
reference data for fresh environments where raw `artifacts/` and prior chat
context are not available. The top-level `oracle/` directory remains the
no-MTP compatibility entrypoint for existing compare commands; variant-specific
copies live under `oracle/nomtp/` and `oracle/mtp/` when both exports are
available.

The report generator reads `phase_exit_codes.tsv`, `bench.json`,
`toolcall15.json`, `lm_eval_summary.json`, `oracle_export_summary.json`,
`gpu_stats_summary.json`, `runtime_stats_summary.json`,
`run_environment.json`, `vllm_collect_env.txt`, `generation.jsonl` when
present, and each variant's `serve_command.sh`. It
writes stable Markdown tables for raw
throughput/latency, ToolCall-15, optional accuracy evals, oracle export,
phase-local runtime stats, MTP speculative decoding, structured provenance,
serve-shape parameters, and normalized efficiency. It also places a quick
performance summary near the top with real-scenario operation cost estimates,
best benchmark output throughput, and phase-local prefill/decode average
`tok/s` values. The operation-cost overview is based on translation, writing,
coding, and ToolCall-15 wall-clock samples, not benchmark rows. It is intended
for OpenRouter/provider-style request costing. Benchmark rows remain useful for
throughput and stress-shape tracking, but they are not used as the OP cost
source. The default acceptance wrapper uses `GENERATION_LANGUAGES=en,zh`,
`GENERATION_THINKING_MODES=non-thinking,think-high,think-max`, three repeats,
`TOOLCALL15_THINKING_MODES=non-thinking,think-high,think-max`,
`TOOLCALL15_SCENARIO_SET=en`, and one retry for transient API call failures.

The normalized columns include `tok/s/GPU`, `tok/s/total GiB`,
`tok/s/used GiB`, `tok/J`, and `tok/s/kW`, which are intended for comparing
different GPU counts and classes such as B200, RTX Pro 6000, RTX 5090, and
GB10. Power efficiency uses sampled GPU-side average power for the whole phase,
not wall-plug power. The real-scenario OP price columns are synthetic
break-even reference numbers for internal comparison only. The report writes
two cost views: a purchase/amortized view that combines 3-year GPU amortization
at 70% useful utilization with `$0.12/kWh` and PUE `1.25`, and a rental view
that uses fixed GPU-hour reference rates without adding separate power. The
current rental reference rates are B200 `$3.80/GPU-hour`, RTX Pro 6000 WS
`$0.96/GPU-hour`, and DGX Spark / GB10 `$0.48/unit-hour`. The purchase view
still uses reference hardware prices for B200, RTX Pro 6000, RTX 5090, and DGX
Spark / GB10.

The same script also publishes a sanitized reference bundle in that directory.
It keeps the data needed to resume work in a fresh environment
without raw `artifacts/`: deterministic no-MTP logprobs oracle cases,
no-MTP/MTP smoke captures, ToolCall-15 traces, benchmark summaries,
GPU/runtime telemetry summaries, and public provenance. Raw server logs,
machine-local paths, private addresses, and secrets are deliberately excluded.
The script generates into a temporary directory, verifies that the bundle has
loadable oracle cases, a complete generation matrix by
variant/language/thinking mode/round, matching transcript Markdown files, and no
non-public data, then replaces the final `baselines/...` directory only after
validation passes.
For archival runs, set `BASELINE_EXPECT_GENERATION_CASES_PER_VARIANT` to the
number of prompt files selected by the run. With the checked-in `en,zh` prompt
suite today, that value is `35`, so each no-MTP/MTP variant must contain
`35 * 3 thinking modes * 3 rounds = 315` generation rows and transcripts.

To capture a separate DeepSeek official API reference directory, put
`DEEPSEEK_API_KEY` in ignored `.env`, then run:

```bash
scripts/run_official_api_baseline.sh
```

The script writes raw run artifacts under ignored `artifacts/official_api/...`
and publishes a sanitized checked-in directory at
`baselines/<YYYYMMDD>_deepseek_official_api_<model>/`. This official API
baseline is not a hardware benchmark; it contains only the comparison material
that is useful across platforms:

- `report.md`: readable summary of smoke, generation, and ToolCall-15 results.
- `generation/`: selected Markdown prompt transcripts plus
  `official_api.json`.
- `smoke/`: a few small runnable chat checks for API-shape comparison.
- `toolcall15/`: official API ToolCall-15 trace and score.

By default it runs three generation rounds over a compact slice of the
checked-in writing, coding, translation, and reading-summary benchmark suite,
`non-thinking`, `think-high`, and `think-max`, one round of three basic smoke
checks, and the English ToolCall-15 set under the same thinking-mode matrix.
Generation requests use `OFFICIAL_TEMPERATURE=1.0` and `OFFICIAL_TOP_P=1.0`.
Each OpenAI-compatible API request gets one retry for transient call failures;
HTTP/API failures that remain after retry are recorded as failed rows. Override
`OFFICIAL_GENERATION_PROMPTS`,
`OFFICIAL_SMOKE_CASES`, `OFFICIAL_REPEAT_COUNT`, `OFFICIAL_TEMPERATURE`,
`OFFICIAL_TOP_P`,
`OFFICIAL_TOOLCALL15_THINKING_MODES`, `OFFICIAL_TOOLCALL15_REPEAT_COUNT`, or
`OFFICIAL_REQUEST_RETRIES` for broader or narrower reference captures.
Set `OFFICIAL_STRICT=1` only when non-green generation or ToolCall-15 checks
should make the script exit non-zero; by default the report is still generated
for subjective and policy comparison.

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

python -m ds4_harness.cli generation-matrix \
  --base-url http://127.0.0.1:8000 \
  --prompt-root prompts \
  --language en \
  --language zh \
  --thinking-mode non-thinking \
  --thinking-mode think-high \
  --thinking-mode think-max \
  --variant nomtp \
  --repeat-count 3 \
  --temperature 1.0 \
  --top-p 1.0 \
  --timeout 900 \
  --jsonl-output artifacts/manual/generation.jsonl \
  --markdown-output-dir artifacts/manual/generation

python -m ds4_harness.cli toolcall15 \
  --base-url http://127.0.0.1:8000 \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --scenario-set en \
  --thinking-mode non-thinking \
  --thinking-mode think-high \
  --thinking-mode think-max \
  --repeat-count 3 \
  --request-retries 1 \
  --json-output artifacts/manual/toolcall15.json

python -m ds4_harness.cli lm-eval \
  --base-url http://127.0.0.1:8000 \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --task gsm8k \
  --num-fewshot 8 \
  --num-concurrent 4 \
  --max-retries 10 \
  --max-gen-toks 2048 \
  --eval-timeout-ms 60000 \
  --tokenizer-backend none \
  --output-dir artifacts/manual/eval_gsm8k \
  --json-output artifacts/manual/eval_gsm8k/lm_eval_summary.json
```

Use the Markdown outputs for human review of writing, translation, and coding
quality. Use the JSON/JSONL outputs for archiving and comparison against the
checked-in `baselines/.../generation/` samples.

The `lm-eval` command is optional and requires the target vLLM venv to have the
API-capable lm-evaluation-harness extra installed, for example
`python -m pip install "lm-eval[api]"`. The shell wrapper
`scripts/run_lm_eval.sh` adds the same artifact layout, GPU/runtime telemetry,
`collect_env.py`, server guard, and deadlock marker behavior used by the
benchmark wrapper.

Use the B200/SM100 or H100 HTTP oracle bundle when you need stricter kernel
correctness checks. Chat exports are covered by `chat-smoke`; `oracle-compare`
only consumes `/v1/completions` logprobs cases. For no-MTP comparisons, the
baseline `oracle/` path is the default. For MTP-specific checks, use the
variant directory such as `oracle/mtp/`.

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

### B200 Official Serve Command

For B200 reference baselines, prefer the official DeepSeek V4 Flash deployment
shape. Clear any image-provided `VLLM_*` launch defaults before starting vLLM if
they conflict with the explicit command.

```bash
export VLLM_ENGINE_READY_TIMEOUT_S=3600

vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 \
  --block-size 256 \
  --max-model-len 393216 \
  --tensor-parallel-size 4 \
  --no-enable-flashinfer-autotune \
  --attention_config.use_fp4_indexer_cache=True \
  --reasoning-parser deepseek_v4 \
  --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 \
  --enable-auto-tool-choice \
  --speculative_config '{"method":"mtp","num_speculative_tokens":2}'
```

The final `--speculative_config` line enables MTP. Remove it for the no-MTP
baseline, and keep the rest of the serve command the same when comparing MTP
against no-MTP. `--max-model-len 393216` follows the DeepSeek recommendation
to keep Think Max quality tests on a context window of at least 384K tokens.

The reusable B200 baseline driver starts this serve shape itself, runs no-MTP
and MTP as separate server lifecycles, and reuses the acceptance, benchmark,
oracle-export, GPU telemetry, runtime metrics, and official `collect_env.py`
wrappers:

```bash
cd /path/to/ds4-sm120-harness

B200_VLLM_REPO=/workspace/vllm \
B200_VLLM_VENV=/workspace/vllm/.venv \
HF_HOME=/workspace/.hf_home \
BRANCH_NAME=main \
GPU_TOPOLOGY_SLUG=4x_nvidia_b200 \
B200_BASELINE_LABEL=b200_tp4_official_main \
scripts/run_b200_baseline.sh
```

Run this script on the reference host, not on a laptop. It defaults to
`HOST=127.0.0.1 PORT=8080`, `B200_BASELINE_VARIANTS=nomtp,mtp`,
`B200_VARIANT_PARALLEL=0`,
`NO_MTP_CONCURRENCY=1,2,4,8,16,24`, `MTP_CONCURRENCY=1,2,4,8,16,24`,
`SERVE_MAX_MODEL_LEN=393216`, `NUM_PROMPTS=80`, `REAL_SCENARIO_REPEAT_COUNT=3`,
`API_REQUEST_RETRIES=1`,
`GENERATION_LANGUAGES=en,zh`,
`GENERATION_THINKING_MODES=non-thinking,think-high,think-max`,
`GENERATION_TEMPERATURE=1.0`, `GENERATION_TOP_P=1.0`,
`TOOLCALL15_THINKING_MODES=non-thinking,think-high,think-max`,
`TOOLCALL15_SCENARIO_SET=en`, `RUN_LM_EVAL=1`,
`LM_EVAL_TASKS=gsm8k`, `LM_EVAL_NUM_FEWSHOT=8`,
`LM_EVAL_NUM_CONCURRENT=4`, `MTP_LM_EVAL_NUM_CONCURRENT=1`,
`LM_EVAL_MAX_GEN_TOKS=2048`, `LM_EVAL_TOKENIZER_BACKEND=none`,
`LM_EVAL_COMMAND_TIMEOUT=7200`, and a controlled random
long-context bench with
`RANDOM_LONG_INPUT_LEN=8192 RANDOM_LONG_OUTPUT_LEN=512
RANDOM_LONG_CONCURRENCY=1,2`.

Set `B200_BASELINE_PHASES` to rerun only selected phases while still starting
the requested server variant. Valid phase names are `acceptance`,
`bench_hf_mt_bench`, `eval_gsm8k`, `bench_random_8192x512`, and
`oracle_export`; the default is `all`. For example:

```bash
B200_BASELINE_VARIANTS=mtp \
B200_BASELINE_PHASES=acceptance \
scripts/run_b200_baseline.sh
```

On a four-GPU reference host, optional parallel variant mode can run no-MTP and
MTP at the same time by assigning disjoint GPU groups and ports:

```bash
B200_VARIANT_PARALLEL=1 \
B200_BASELINE_VARIANTS=nomtp,mtp \
B200_PARALLEL_GPU_GROUPS='nomtp=0,1;mtp=2,3' \
B200_PARALLEL_TENSOR_PARALLEL_SIZE=2 \
B200_PARALLEL_PORTS='nomtp=8080;mtp=8081' \
scripts/run_b200_baseline.sh
```

This mode is useful for intermediate smoke or correctness sampling. It changes
the serve shape from the default four-GPU TP=4 reference run to two independent
two-GPU TP=2 servers, and both servers still share host CPU, storage, network,
and scheduler resources. Do not treat its throughput as directly comparable to
the sequential four-GPU baseline unless that split topology is itself the target
being evaluated. The coordinator writes temporary child runs, then merges the
results back into the normal `nomtp/` and `mtp/` artifact layout before report
or bundle generation. Use a label that makes the effective serve topology
explicit, for example `b200_tp2_main_<sha>`. In split mode, run-environment
inventory and GPU telemetry are filtered to the child process's
`CUDA_VISIBLE_DEVICES`, so normalized columns such as `tok/s/GPU`, `tok/J`, and
rental cost use the two-GPU denominator for each child service.

The older `RUN_ACCEPTANCE=0`, `RUN_BENCH_HF=0`, `RUN_RANDOM_LONG=0`, and
`RUN_ORACLE_EXPORT=0` toggles remain available for disabling phases inside the
selected phase set. The oracle export phase runs for each requested variant so
no-MTP and MTP both produce logprobs reference material. Before creating a new
managed run directory, the script moves existing sibling artifact directories
matching
`${ARTIFACT_ARCHIVE_PREFIX:-$B200_BASELINE_LABEL}*` into
`artifacts/<branch>/<gpu-topology>/_archive_before_<timestamp>/`; set
`ARTIFACT_ARCHIVE_PREVIOUS=0` to keep older runs in place, or set
`ARTIFACT_ARCHIVE_PREFIX` when the cleanup prefix should differ from the
baseline label. Explicit `OUT_DIR=...` runs skip this archive step. The script
clears inherited
`VLLM_*`, `TORCH_CUDA_ARCH_LIST`, and `CUDA_VISIBLE_DEVICES` launch defaults
before starting vLLM, then sets `CUDA_VISIBLE_DEVICES` only when the driver has
an explicit split-GPU assignment. It stores phase exit codes in
`phase_exit_codes.tsv` and a human summary in `baseline_summary.md`. It keeps
running later phases after an earlier phase fails, then exits non-zero if any
phase failed; the artifact tree is still valid for partial-baseline analysis.

The reference venv must include the packages needed by `vllm bench serve` and
the harness self-checks. At minimum, confirm `python -m pip check` is clean and
that `pytest`, `ruff`, `lm-eval[api]`, and the Hugging Face `datasets` package
are available in the vLLM venv. If FlashInfer is installed, keep `flashinfer-python`,
`flashinfer-cubin`, and `flashinfer-jit-cache` on matching versions.

```bash
python -m ds4_harness.cli oracle-compare \
  --base-url http://127.0.0.1:8000 \
  --oracle-dir baselines/20260501_b200_main_51295793a/oracle \
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

`BASE_URL` is passed through to `vllm bench serve`; use `HOST` and `PORT` only
when you intentionally want the wrapper to construct a local target URL.
For the older official vLLM 0.20.0 B200 path, cap MTP benchmark runs at
`CONCURRENCY=1` unless intentionally reproducing its known MTP C>1 hang. For
newer main-based reference builds, run the guarded MTP C>1 matrix and record
whether the server remains generation-responsive after each concurrency tier.

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
- `generation-matrix --repeat-count 3` has no regression versus the previous
  branch for the relevant no-MTP or MTP serving variant.
- `toolcall15 --scenario-set en --thinking-mode non-thinking --thinking-mode
  think-high --thinking-mode think-max --repeat-count 3` passes, or any
  partial/fail scenario is explained with trace evidence.
- `lm-eval --task gsm8k --num-fewshot 8` is captured for expensive reference
  baselines and before promoting a branch whose correctness could have changed.
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
- On the older official vLLM 0.20.0 B200 path, the known stable hang is MTP
  with benchmark concurrency greater than 1. Treat that as a runtime
  unresponsive-server case. For newer main-based reference builds, keep running
  the guarded MTP C>1 matrix and record the observed result.
- For vLLM-side micro correctness checks inspired by the ROCm DeepSeek V4
  support PRs, see `docs/vllm_correctness_gates.md`. Keep those tests in the
  vLLM checkout; this repo records and orchestrates the gate commands.
