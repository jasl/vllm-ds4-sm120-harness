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

For two-node DGX Spark bare-metal Ray/vLLM bring-up, see
[`docs/dgx_spark_bare_metal_cluster.md`](docs/dgx_spark_bare_metal_cluster.md).
That document uses placeholders only; keep private hostnames, IP addresses, and
local paths in ignored local notes.

Machine-independent CUDA profile snippets live under `configs/`. Source the
matching file before building or running GPU-path validation on the target host:

```bash
source configs/sm120_tp2_serve.env.example
source configs/gb10_sm121_serve.env.example
```

The GB10 profile records the current SM121 shape: one `NVIDIA GB10` device,
CUDA 13.2 tools under `/usr/local/cuda-13.2`, `CUDA_ARCH_LIST=121a`, and
`TORCH_CUDA_ARCH_LIST=12.1a`. Keep private SSH targets and checkout paths in
ignored local files, not in these public profile snippets.

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
  - top-1 logprob margin for reference and actual choices
  - repeated-request token stability for low-margin cases
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
  - summarizes prefill/decode token counters, request pressure, KV-cache usage,
    prefix-cache hit rate, and preemption counters
  - can parse serve logs for prompt/generation throughput, prefix-cache hit
    rate, KV-cache usage, and MTP acceptance metrics
- Long-context KV/indexer probe:
  - sends a deterministic long prompt with early, middle, and late sentinel
    codes
  - records prompt shape, prompt hash, excerpts, usage, assistant output,
    runtime stats, and GPU stats
  - is diagnostic evidence for cache-layout regressions; it does not change
    accuracy scores
- Prefix-cache reuse probe:
  - warms one deterministic long conversation, introduces a second long
    conversation, checks sequential A-after-B reuse, then sends interleaved
    warm A/B requests
  - records streaming TTFT, elapsed time, prompt usage, cached prompt tokens,
    runtime stats, and GPU stats
  - is diagnostic evidence for concurrent prefix/KV reuse regressions; use
    `runtime_stats_summary.json` for phase-local KV usage, prefix hit rate, and
    preemption counters
- Optional streaming-pressure soak:
  - sends concurrent streaming chat completions over deterministic long
    conversations that grow across several short rounds
  - records request-level TTFT, elapsed time, chunk counts, cached prompt
    tokens, runtime stats, and GPU stats
  - is disabled by default; enable it with `RUN_STREAMING_PRESSURE_SOAK=1`
    when you want a short release-gate check for streaming responsiveness

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
- Long-context retrieval: run `long-context-probe` when a change may affect
  KV cache, indexer cache, chunking, or long-prefill behavior. It validates
  end-to-end sentinel retrieval rather than dumping raw KV tensors.
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

`scripts/run_bench_matrix.sh` defaults to the HF/MT-Bench profile and retries
one transient infrastructure failure per concurrency tier, such as a Hugging
Face dataset `ReadTimeout`. Set `BENCH_TRANSIENT_FAILURE_RETRIES=0` to disable
that behavior. Set `DATASET_NAME=random IGNORE_EOS=1` when intentionally
running random shape stress tests.

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
GPU count/model inventory, selected CUDA env vars, benchmark settings, source
provenance, and official API configuration state. GPU UUIDs and API key values
are not written.

Source provenance is best-effort and non-blocking. The harness records the
harness source and vLLM source label/path basename, and records branch, commit,
dirty count, and upstream tracking only when that source is a Git worktree.
Tarball, copied, or otherwise non-Git source directories are valid; the report
marks Git as unavailable with a reason instead of failing the run. Use
`HARNESS_SOURCE_LABEL`, `VLLM_SOURCE_LABEL`, and `VLLM_REPO` when you want a
clearer report label or when vLLM cannot be inferred from `VLLM_BIN`/`PYTHON`.

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
coding cases also write the assistant's code next to the transcript with the
same basename and the inferred source extension, such as `.html`, `.py`, or
`.js`, so reviewers can open runnable artifacts directly.
defaults use `temperature=1.0` and `top_p=1.0`, matching the DeepSeek V4
sampling recommendation used for quality-oriented comparisons.

For any harness gate that enables DeepSeek V4 thinking mode, use the model-card
local-deployment preset: `temperature=1.0`, `top_p=1.0`, and for `think-max`
run the server with a context window of at least 384K tokens. Local generation
acceptance applies a generation-only `GENERATION_THINK_HIGH_TOKEN_BUDGET`
preset for `think-high`. `think-max` defaults to no explicit hidden-reasoning
budget and instead uses `GENERATION_THINK_MAX_REQUEST_MAX_TOKENS` to give the
request a larger completion ceiling. These presets are not applied to
ToolCall-15 by default because tool-call policy scoring should remain
comparable across thinking modes. We have seen unexpected behavior when
thinking-mode captures
are taken outside this request shape, so baseline extraction treats this shape
as part of the test contract. Non-thinking checks may deliberately choose a
different sampling policy when the test is meant to be deterministic.

Prompt front matter wins over CLI `--temperature` and `--top-p` by default so
checked-in quality prompts keep their intended request shape. For deterministic
debug localization, pass `--override-prompt-sampling` to force the CLI sampling
values for that run.

`oracle-compare` keeps raw full-trajectory top-1/top-k diagnostics, but strict
threshold gates are low-margin fork aware. If the first token divergence is a
low-margin branch, `--min-top1-match-rate` and `--min-topk-overlap-mean` score
only the shared prefix before that branch; the full-trajectory values remain in
the JSON output for analysis.

Sparse MLA runtime tensor dumps are a separate opt-in diagnostic path for
kernel/KV-cache investigations. They are not enabled by the harness by default;
summarize captured metadata with `sparse-mla-dump-report` and keep raw tensor
payloads in the run artifact directory. Keep B200/reference captures narrow
unless raw tensors are explicitly needed; larger exploratory dumps belong on
storage-rich development hosts. See `docs/sparse_mla_debug_dumps.md`.

The shell wrappers also sample GPU telemetry with `nvidia-smi` when available.
Each run writes `gpu_stats.csv`, `gpu_stats_summary.json`, and
`gpu_stats_summary.md` next to the other artifacts. The summary includes per-GPU
peak/average memory usage, power draw, and utilization. Set `GPU_STATS=0` to
disable sampling, or `GPU_STATS_INTERVAL_SECONDS=2` to change the sample
interval.

The wrappers also sample vLLM runtime metrics from `/metrics` by default. Each
run writes `vllm_metrics.prom`, `runtime_stats_summary.json`, and
`runtime_stats_summary.md` when metrics are available. The summary includes
prefill/decode token deltas, request pressure, KV-cache usage, prefix-cache hit
rate, and preemption deltas. Set `RUNTIME_STATS=0` to disable sampling, or
`RUNTIME_STATS_INTERVAL_SECONDS=10` to reduce polling. If you have the server
log path, pass `SERVE_LOG=/path/to/serve.log`; the summary will also include
vLLM log-derived prompt/generation throughput, KV-cache usage, prefix-cache hit
rate, and speculative decoding acceptance metrics. The wrapper records
`serve_log_offset.txt` when a phase starts and parses only the appended lines
into `serve_log_phase.log`, so log-derived MTP acceptance metrics remain
phase-local even when multiple harness phases share one vLLM server log.

Each wrapper also downloads and runs the official vLLM `collect_env.py` script
by default. It stores `vllm_collect_env.py`, `vllm_collect_env.sha256`,
`vllm_collect_env.txt`, `vllm_collect_env.err`, and
`vllm_collect_env.exit_code` in the run artifact directory. Set
`VLLM_COLLECT_ENV=0` when running offline or when you want to inspect the
downloaded script manually before execution. Override `VLLM_COLLECT_ENV_URL`
only for a pinned or locally mirrored copy.

The live wrappers guard against unresponsive vLLM workers, without treating
slow model load or first-request warmup as a runtime failure. They wait up to
`SERVER_STARTUP_TIMEOUT=1800` seconds before the live gate sequence, then use
short health probes before expensive live gates. After a failed live gate or
benchmark, they wait up to `SERVER_FAILURE_GRACE_TIMEOUT=300` seconds before
recording `server_unresponsive.txt`, `*.server_unresponsive`, or `*.skipped`
artifacts. Benchmark recovery checks also run a tiny `/v1/completions` probe
with `SERVER_FAILURE_PROBE_TIMEOUT=30`, so a live `/health` endpoint does not
mask a wedged generation path. Keep
`SERVER_GUARD=1` for B200/SM12x reference runs. Set `SERVER_HEALTH_TIMEOUT=10`
to tune the health probe timeout, and set `SERVER_RECOVERY_CMD` only when you
explicitly want the wrapper to run a local recovery command after detecting an
unresponsive server.

To turn a finished artifact tree into a checked-in baseline bundle, run:

```bash
BASELINE_RUN_DIR=artifacts/main/4x_nvidia_b200/b200_tp4_main_5737770c6/20260502064850 \
BASELINE_REPORT_TITLE="B200 vLLM Main DeepSeek V4 Flash Baseline" \
BASELINE_REPORT_LABEL=b200_tp4_main_5737770c6 \
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
present, `long_context_probe.json` when present, and each variant's
`serve_command.sh`. It
writes stable Markdown tables for raw
throughput/latency, ToolCall-15, optional accuracy evals, oracle export,
long-context probe results, phase-local runtime stats, MTP speculative
decoding, structured provenance, serve-shape parameters, and normalized
efficiency. It also places a quick
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
synthetic KV layout probes, GPU/runtime telemetry summaries, and public
provenance. Raw KV layout `.bin` captures remain in ignored run artifacts; raw
server logs, machine-local paths, private addresses, and secrets are
deliberately excluded.
The script generates into a temporary directory, verifies that the bundle has
loadable oracle cases, a complete generation matrix by
variant/language/thinking mode/round, matching transcript Markdown files, and no
non-public data, then replaces the final `baselines/...` directory only after
validation passes.
For runs that intentionally did not include an oracle export, set
`BASELINE_REQUIRE_ORACLE=0`; the bundle still archives sanitized generation,
smoke, ToolCall-15, performance, telemetry, manifest, README, and report data,
but it must not be used as a token-level correctness oracle.
Coding generation rows keep the same sidecar source files as live artifacts,
with transcript basenames converted from `.md` to the target language extension.
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
Generation and ToolCall-15 requests use `OFFICIAL_TEMPERATURE=1.0` and
`OFFICIAL_TOP_P=1.0`; ToolCall-15 can be overridden separately with
`OFFICIAL_TOOLCALL15_TEMPERATURE` and `OFFICIAL_TOOLCALL15_TOP_P`.
Official API generation runs default to `OFFICIAL_GENERATION_EXPECTATION_CHECKS=0`:
they record successful chat-completion responses without applying the prompt
metadata's content sanity checks such as minimum length or complete HTML
artifact detection. This keeps the hosted API bundle as behavior/sample
evidence rather than a strict harness-quality gate. Set
`OFFICIAL_GENERATION_EXPECTATION_CHECKS=1` when you deliberately want to apply
the same prompt expectation checks used by local vLLM generation runs. Each
OpenAI-compatible API request gets one retry for transient call failures;
HTTP/API failures that remain after retry, or responses without chat choices,
are recorded as failed rows. Override `OFFICIAL_GENERATION_PROMPTS`,
`OFFICIAL_SMOKE_CASES`, `OFFICIAL_REPEAT_COUNT`, `OFFICIAL_TEMPERATURE`,
`OFFICIAL_TOP_P`, `OFFICIAL_TOOLCALL15_TEMPERATURE`,
`OFFICIAL_TOOLCALL15_TOP_P`,
`OFFICIAL_TOOLCALL15_THINKING_MODES`, `OFFICIAL_TOOLCALL15_REPEAT_COUNT`, or
`OFFICIAL_REQUEST_RETRIES` for broader or narrower reference captures.
Set `OFFICIAL_STRICT=1` only when non-green generation or ToolCall-15 checks
should make the script exit non-zero; by default the report is still generated
for subjective and policy comparison.

## Current Archived Baselines

As of 2026-05-02, the checked-in long-term reference bundles are:

- `baselines/20260502_b200_tp2_main_5737770c6`: B200 split topology, TP=2,
  no-MTP and MTP.
- `baselines/20260502_b200_tp4_main_5737770c6`: B200 full topology, TP=4,
  no-MTP and MTP.
- `baselines/20260502_deepseek_official_api_deepseek_v4_flash`: hosted
  DeepSeek official API comparison sample.

The B200 TP=2 and TP=4 bundles are complete public bundles: each serving
variant has 315 generation rows and matching Markdown transcripts
(`35 prompts * 3 thinking modes * 3 rounds`), ToolCall-15 traces, GSM8K
summaries, HF and random benchmark summaries, GPU/runtime telemetry,
parsed `collect_env.py` environment summary, oracle export data, and a
generated `report.md`. Their
phase tables intentionally preserve the current acceptance gate status; other
benchmark, eval, oracle, telemetry, and bundle-generation artifacts are still
usable for performance and correctness comparison.

The official API bundle is a smaller reference sample, not a hardware
benchmark. It has 72 generation rows and transcripts from 8 selected prompts
(`8 prompts * 3 thinking modes * 3 rounds`), 3 smoke checks, and one
ToolCall-15 pass over the English scenario set. It records `temperature=1.0`
and `top_p=1.0` for generation rows and future ToolCall-15 captures so hosted
API behavior can be compared against vLLM samples with the same sampling shape.

For the 8 generation cases shared by the official API bundle, both B200
topologies and both serving variants have 72/72 passing rows. The official API
sample has 72/72 passing rows under the relaxed generation scoring described
above; all 72 rows contain successful chat-completion choices. For
ToolCall-15, compare percentages rather than raw points because the B200 runs
use three repeats while the official API sample uses one repeat: official API is
81/90 (90%), B200 TP=4 no-MTP is 243/270 (90%), and B200 TP=2 no-MTP, TP=2
MTP, and TP=4 MTP are 225/270 (83%).

Future RTX Pro 6000, RTX 5090, GB10, or other reference captures should follow
the same topology-in-label convention and publish sanitized bundles under
`baselines/<YYYYMMDD>_<topology>_<source>_<short-sha-or-label>/`.

### Correctness Reference Selection

The current alignment reference choice is recorded in
`baselines/20260502_correctness_reference_selection.json`. It intentionally
stores the full baseline directory names, not shorthand labels, because future
baseline refreshes may add or remove checked-in bundles.

For token-level correctness, use
`baselines/20260502_b200_tp4_main_5737770c6/oracle/nomtp` as the primary
no-MTP oracle and
`baselines/20260502_b200_tp4_main_5737770c6/oracle/mtp` only for MTP runs. The
top-level `baselines/20260502_b200_tp4_main_5737770c6/oracle` path remains a
no-MTP compatibility entrypoint for existing commands.

Do not treat the archived B200 topologies as interchangeable token oracles:
the 2026-05-02 alignment found matching prompt token ids for TP2 vs TP4
no-MTP, but only 1 of 5 generated token sequences matched exactly. The hosted
`baselines/20260502_deepseek_official_api_deepseek_v4_flash` bundle is
behavior-level evidence only; it has no archived logprobs oracle.

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
  --temperature 1.0 \
  --top-p 1.0 \
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

Compare a development run against the selected behavior reference after each
generation-matrix capture:

```bash
python -m ds4_harness.cli generation-compare \
  --reference baselines/20260502_b200_tp4_main_5737770c6/generation/nomtp.json \
  --actual artifacts/manual/generation.jsonl \
  --json-output artifacts/manual/generation_compare.json \
  --markdown-output artifacts/manual/generation_compare.md
```

The `lm-eval` command is optional and requires the target vLLM venv to have the
API-capable lm-evaluation-harness extra installed, for example
`python -m pip install "lm-eval[api]"`. The shell wrapper
`scripts/run_lm_eval.sh` adds the same artifact layout, GPU/runtime telemetry,
`collect_env.py`, server responsiveness guard, and unresponsive-server marker
behavior used by the benchmark wrapper.

Use the B200/SM100 or H100 HTTP oracle bundle when you need stricter kernel
correctness checks. Chat exports are covered by `chat-smoke`; `oracle-compare`
only consumes `/v1/completions` logprobs cases. For no-MTP comparisons, the
baseline `oracle/` path is the default. For MTP-specific checks, use the
variant directory such as `oracle/mtp/`.

Baseline directories are immutable result snapshots. If a checked-in baseline
becomes stale after upstream or prompt changes, select a newer baseline or
record the stale reference explicitly in the consuming analysis; the harness
does not rewrite old baseline content or add format-compatibility handling for
retired exports.

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
The wrapper uses `ORACLE_STOP_ON_ERROR=1` by default so an unresponsive
reference server consumes only one request timeout before stopping the export.

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
The `--attention_config.use_fp4_indexer_cache=True` flag is currently SM100/B200
specific. Do not use it on SM12x hosts such as RTX Pro 6000, RTX 5090, or GB10;
those runs should leave `SERVE_USE_FP4_INDEXER_CACHE=auto` or set it to `0`.

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
B200_BASELINE_LABEL=b200_tp4_main_5737770c6 \
scripts/run_b200_baseline.sh
```

Run this script on the reference host, not on a laptop. It defaults to
`HOST=127.0.0.1 PORT=8080`, `B200_BASELINE_VARIANTS=nomtp,mtp`,
`B200_VARIANT_PARALLEL=0`,
`NO_MTP_CONCURRENCY=1,2,4,8,16,24`, `MTP_CONCURRENCY=1,2,4,8,16,24`,
`SERVE_MAX_MODEL_LEN=393216`, `NUM_PROMPTS=80`, `REAL_SCENARIO_REPEAT_COUNT=3`,
`API_REQUEST_RETRIES=1`, `SERVE_USE_FP4_INDEXER_CACHE=auto`,
`GENERATION_LANGUAGES=en,zh`,
`GENERATION_THINKING_MODES=non-thinking,think-high,think-max`,
`GENERATION_TEMPERATURE=1.0`, `GENERATION_TOP_P=1.0`,
`GENERATION_MAX_CASE_TOKENS=65536`,
`GENERATION_THINK_HIGH_TOKEN_BUDGET=4096`,
`GENERATION_THINK_MAX_TOKEN_BUDGET=` (unset by default),
`GENERATION_THINK_MAX_REQUEST_MAX_TOKENS=65536`,
`TOOLCALL15_THINKING_MODES=non-thinking,think-high,think-max`,
`TOOLCALL15_TEMPERATURE=1.0`, `TOOLCALL15_TOP_P=1.0`,
`TOOLCALL15_SCENARIO_SET=en`, `RUN_LM_EVAL=1`,
`LM_EVAL_TASKS=gsm8k`, `LM_EVAL_NUM_FEWSHOT=8`,
`LM_EVAL_NUM_CONCURRENT=4`, `MTP_LM_EVAL_NUM_CONCURRENT=1`,
`LM_EVAL_MAX_GEN_TOKS=2048`, `LM_EVAL_TOKENIZER_BACKEND=none`,
`LM_EVAL_COMMAND_TIMEOUT=7200`, and a controlled random
long-context bench with
`RANDOM_LONG_INPUT_LEN=8192 RANDOM_LONG_OUTPUT_LEN=512
RANDOM_LONG_CONCURRENCY=1,2`.
The default long-context probe uses `LONG_CONTEXT_LINE_COUNT=2400`,
`LONG_CONTEXT_MAX_TOKENS=128`, `LONG_CONTEXT_TEMPERATURE=0.0`,
`LONG_CONTEXT_TOP_P=1.0`, and `LONG_CONTEXT_THINKING_MODE=non-thinking`.
When changing the long-context probe to `think-high` or `think-max`, also set
`LONG_CONTEXT_TEMPERATURE=1.0`; for `think-max`, keep
`SERVE_MAX_MODEL_LEN=393216` or larger.
The default prefix-cache probe uses `PREFIX_CACHE_LINE_COUNT=2400`,
`PREFIX_CACHE_MAX_TOKENS=64`, `PREFIX_CACHE_TEMPERATURE=0.0`,
`PREFIX_CACHE_TOP_P=1.0`, `PREFIX_CACHE_THINKING_MODE=non-thinking`, and
`PREFIX_CACHE_FAIL_ON_REGRESSION=0`. It records a warning flag by default
instead of failing the run on noisy TTFT ratios; set
`PREFIX_CACHE_FAIL_ON_REGRESSION=1` when using a stable dedicated host and you
want the probe to be a hard gate.
The optional streaming-pressure soak is disabled by default with
`RUN_STREAMING_PRESSURE_SOAK=0`. When enabled, it defaults to
`STREAMING_PRESSURE_CONCURRENCY=4`, `STREAMING_PRESSURE_ROUND_COUNT=3`,
`STREAMING_PRESSURE_LINE_COUNT=1200`,
`STREAMING_PRESSURE_MAX_TOKENS=128`,
`STREAMING_PRESSURE_TEMPERATURE=1.0`,
`STREAMING_PRESSURE_TOP_P=1.0`,
`STREAMING_PRESSURE_THINKING_MODE=non-thinking`, and
`STREAMING_PRESSURE_FAIL_ON_SLOW=0`. It records slow-TTFT/elapsed warning
flags by default; set `STREAMING_PRESSURE_FAIL_ON_SLOW=1` only on a stable
host where you want those warnings to fail the gate.
The default KV layout probe uses a synthetic packed FP8 indexer cache with
`KV_LAYOUT_NUM_BLOCKS=2`, `KV_LAYOUT_BLOCK_SIZE=256`,
`KV_LAYOUT_HEAD_DIM=448`, `KV_LAYOUT_SCALE_BYTES=8`, and
`KV_LAYOUT_REQUIRE_HELPER_MATCH=1`. It writes JSON, Markdown, and a raw
`kv_layout_probe_packed_cache.bin` under the run artifact tree before the live
server starts.

Set `B200_BASELINE_PHASES` to rerun only selected phases while still starting
the requested server variant. Valid phase names are `kv_layout_probe`,
`acceptance`, `long_context_probe`, `prefix_cache_probe`,
`streaming_pressure_soak`, `bench_hf_mt_bench`, `eval_gsm8k`,
`bench_random_8192x512`, and `oracle_export`; the default is `all`. The
`streaming_pressure_soak` phase still requires `RUN_STREAMING_PRESSURE_SOAK=1`
because it is intentionally opt-in. For example:

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

The `RUN_ACCEPTANCE=0`, `RUN_BENCH_HF=0`, `RUN_RANDOM_LONG=0`, and
`RUN_ORACLE_EXPORT=0` toggles disable phases inside the selected phase set.
`RUN_STREAMING_PRESSURE_SOAK=1` enables the optional streaming-pressure soak in
acceptance and baseline runs.
The oracle export phase runs for each requested variant so
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
  --oracle-dir baselines/20260502_b200_tp4_main_5737770c6/oracle \
  --top-n 20 \
  --require-prompt-ids \
  --repeat-count 5 \
  --low-margin-threshold 0.5 \
  --require-high-margin-token-match \
  --min-top1-match-rate 0.80 \
  --min-topk-overlap-mean 0.80 \
  --stability-json-output artifacts/manual/oracle_stability.json \
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
when you intentionally want the wrapper to construct a local target URL. Run
the guarded MTP C>1 matrix for reference builds and record whether the server
remains generation-responsive after each concurrency tier. If a pinned runtime
does become unresponsive, keep the marker artifacts and treat that tier as a
runtime stability failure rather than a completed throughput point.

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
  branch for the relevant no-MTP or MTP serving variant, and
  `generation-compare` has no missing rows or behavior regressions versus the
  selected full-directory baseline reference.
- Treat DeepSeek V4 `think-max` generation as an official-shape quality gate,
  not as a short-context smoke. The local server should use
  `--max-model-len` of at least `393216`. The checked-in long coding and HTML
  prompts reserve a larger completion budget so reasoning content does not
  truncate the final artifact. Keep
  `temperature=1.0`, `top_p=1.0`, and the generation-only
  `GENERATION_THINK_HIGH_TOKEN_BUDGET` and
  `GENERATION_THINK_MAX_REQUEST_MAX_TOKENS` presets. Avoid setting a small
  `GENERATION_THINK_MAX_TOKEN_BUDGET` unless the goal is specifically to test
  hidden-reasoning truncation. For targeted probes, override
  `GENERATION_MAX_CASE_TOKENS` or the request `max_tokens` rather than treating
  a length finish as a model-quality failure.
  A thinking-mode failure under a small context window or a 12K completion cap
  is a budget diagnostic until reproduced under the recommended long-context
  shape.
- `toolcall15 --scenario-set en --thinking-mode non-thinking --thinking-mode
  think-high --thinking-mode think-max --repeat-count 3 --temperature 1.0
  --top-p 1.0` passes, or any
  partial/fail scenario is explained with trace evidence.
- `lm-eval --task gsm8k --num-fewshot 8` is captured for expensive reference
  baselines and before promoting a branch whose correctness could have changed.
- `long-context-probe` passes when touching KV cache, FP4 indexer cache,
  chunked prefill, scheduler, or long-context serving behavior. For suspected
  KV/prefix-cache reuse regressions, preserve phase-local
  `runtime_stats_summary.json` and compare TTFT with
  `gpu_kv_cache_usage_percent_*`, `prefix_cache_hit_rate_percent_delta`, and
  `preemptions_delta`. Long-context probes and long-prefill random benchmarks
  are the most useful workloads because short prompts barely move KV usage.
- `prefix-cache-probe` is captured before promoting scheduler, prefix-cache, or
  KV-cache changes. Compare `warm_a_after_b_vs_solo_ttft_ratio`,
  `warm_a_interleaved_after_rebuild_vs_solo_ttft_ratio`,
  `cached_prompt_tokens`, `prefix_cache_hit_rate_percent_delta`,
  `gpu_kv_cache_usage_percent_max`, and `preemptions_delta`; a high ratio with
  low prefix hit and no preemption is evidence of reuse drift rather than
  capacity pressure.
- Enable `streaming-pressure-soak` with `RUN_STREAMING_PRESSURE_SOAK=1` before
  making streaming responsiveness a release gate. Compare `max_ttft_seconds`,
  `max_elapsed_seconds`, chunk counts, `running_requests_max`,
  `gpu_kv_cache_usage_percent_max`, prefix hit rate, and preemptions. Leave it
  disabled for routine local harness edits.
- `oracle-compare` has matching prompt token ids and no early token divergence
  on high-margin deterministic oracle cases. Low-margin divergence must be
  explained with top-k overlap, top-1 margin, and repeated-request stability
  evidence rather than treated as a strict token oracle failure by itself.
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
- Keep the server responsiveness guard enabled for MTP C>1 benchmark and eval
  shapes. If a serving process becomes unresponsive, preserve the marker
  artifacts and record the observed tier instead of special-casing the platform
  in the report narrative.
- For vLLM-side micro correctness checks inspired by the ROCm DeepSeek V4
  support PRs, see `docs/vllm_correctness_gates.md`. Keep those tests in the
  vLLM checkout; this repo records and orchestrates the gate commands.

## Third-Party Reference Code

`third_party/deepseek_v4_reference_inference/` contains a local MIT-licensed
snapshot of the DeepSeek V4 Flash reference inference files. It is reference
material only: the harness runtime, wrapper scripts, and test suite do not
import or execute it. Use the directory's `SOURCE.md` and `SHA256SUMS` when
checking provenance or refreshing the snapshot.

## License

This harness is released under the MIT License. See `LICENSE`.
