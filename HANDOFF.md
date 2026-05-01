# DeepSeek V4 SM12x Handoff Notes

Last updated: 2026-05-01

This directory is the repo-independent validation harness for the SM12x
DeepSeek V4 work. It is meant to survive context switches and should be copied
alongside branch work on `ds4-sm120`, `ds4-sm120-full`, and internal tuning
branches.

## Canonical Locations

- Local harness: clone this repository wherever local editing is convenient.
- Remote harness: copy the checkout to the primary SM120 host before running
  live acceptance.
- Main vLLM remote venv: use the venv for the target vLLM checkout.
- Main vLLM remote checkout: use the target branch checkout, or a
  benchmark-specific worktree under the remote scratch directory.

## Active Hardware Scope

- Primary development and test host: dual RTX PRO 6000. Run DeepSeek V4 Flash
  serve, correctness, harness acceptance, and benchmark gates there unless a
  task explicitly says otherwise.
- Secondary validation host: GB10. Single GB10 is not currently a DeepSeek V4
  Flash runtime gate; use it for environment, build, architecture, and log
  comparison data until a second GB10 is available for cluster testing.
- Supported CUDA targets for this effort are only SM120 and SM121, the CUDA
  arch `12.0f` / `120f` family. Do not widen the support matrix without a new
  explicit requirement.
- The local macOS machine is for code review, harness edits, docs, and artifact
  organization only. Do not treat local results as GPU-path validation.

## Branch Roles

- `ds4-sm120`: public PR branch. Keep focused on changes directly required for
  SM12x support, and treat it as frozen by default. Only promote fixes that are
  needed for correctness, review, or rebase health.
- `ds4-sm120-experimental`: active development branch based on `ds4-sm120`.
  Put unmerged upstream optimizations, local follow-ups, performance work, and
  accuracy fixes here first. This is the main branch for ongoing iteration.
- `ds4-sm120-full`: community evaluation branch based on `ds4-sm120`. Promote
  only validated optimizations and fixes from experimental work, and keep it
  stable enough for outside users to test.
- `ds4-sm120-perf-120`: temporary profiling branch. It may contain profiling
  instrumentation or throwaway measurement code and should not be treated as a
  promotion source without review.
- `ds4-sm120-official-api-compat`: historical branch for DeepSeek official API
  alignment. Its useful semantics have been absorbed into experimental/full;
  keep it only for archaeology unless a new API-compat follow-up is explicitly
  requested.
- `fix-mtp-draft-probs-sampling`: generic MTP correctness PR branch. Treat as
  frozen unless reviewer feedback requires changes.

When upstream `main` has DeepSeek V4 related changes, rebase `ds4-sm120` onto
the new `main` first. Then rebase `ds4-sm120-experimental` and `ds4-sm120-full`
onto the updated `ds4-sm120`.

When in doubt, do not push exploratory changes directly to `ds4-sm120`.

## Environment Notes

Use these on the RTX PRO 6000 / SM120 host unless a branch-specific test says
otherwise:

```bash
source /path/to/vllm/.venv/bin/activate
export PATH="/usr/local/cuda/bin:$PATH"
export CUDA_HOME="/usr/local/cuda"
export TRITON_PTXAS_PATH="/usr/local/cuda/bin/ptxas"
export CUDA_ARCH_LIST="120a"
export TORCH_CUDA_ARCH_LIST="12.0a"
unset PYTORCH_CUDA_ALLOC_CONF
```

Do not set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` for TP=2 CUDA
graph runs. It has caused custom all-reduce graph registration failures.

If using a vLLM console script from a checkout that is not installed into the
venv, set:

```bash
export PYTHONPATH=/path/to/vllm-worktree
```

## Baseline Serve Command

```bash
/path/to/vllm/.venv/bin/vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --host 127.0.0.1 --port 8000 \
  --trust-remote-code \
  --kv-cache-dtype fp8 \
  --block-size 256 \
  --tensor-parallel-size 2 \
  --enable-expert-parallel \
  --gpu-memory-utilization 0.98 \
  --max-model-len 65536 \
  --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE", "custom_ops":["all"]}' \
  --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 \
  --enable-auto-tool-choice \
  --reasoning-parser deepseek_v4
```

MTP variant:

```bash
--speculative-config '{"method":"mtp","num_speculative_tokens":2}'
```

## Acceptance Gates

Run from the harness directory against an already-started vLLM server:

```bash
cd /path/to/ds4-sm120-harness
source /path/to/vllm/.venv/bin/activate

python -m pytest -q tests
python -m ruff check ds4_harness tests
python -m compileall -q ds4_harness

python -m ds4_harness.cli health --base-url http://127.0.0.1:8000
python -m ds4_harness.cli chat-smoke --tag quick \
  --jsonl-output /tmp/ds4-sm120-smoke-quick.jsonl
python -m ds4_harness.cli chat-smoke --tag quality \
  --jsonl-output /tmp/ds4-sm120-smoke-quality.jsonl
python -m ds4_harness.cli chat-smoke --tag coding --timeout 900 \
  --jsonl-output /tmp/ds4-sm120-smoke-coding.jsonl
python -m ds4_harness.cli toolcall15 \
  --json-output /tmp/ds4-sm120-toolcall15.json
```

For stricter kernel correctness, compare against a B200/SM100 or H100 HTTP
oracle bundle:

```bash
python -m ds4_harness.cli oracle-compare \
  --base-url http://127.0.0.1:8000 \
  --oracle-dir /path/to/b200_or_h100_oracle_bundle \
  --require-prompt-ids \
  --min-top1-match-rate 0.80 \
  --json-output /tmp/ds4-sm120-oracle.json
```

Keep machine-local oracle bundle paths in ignored local notes, not in the public
repository.

## Benchmark Gate

Run no-MTP and MTP as separate server configurations, then use the same bench
profile for both. Prefer a representative HF dataset when judging user-visible
progress:

```bash
python -m ds4_harness.cli bench-matrix \
  --vllm-bin /path/to/vllm/.venv/bin/vllm \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --host localhost \
  --port 8000 \
  --concurrency 1,2,4,8,16,24 \
  --dataset-name hf \
  --dataset-path philschmid/mt-bench \
  --num-prompts 80 \
  --temperature 1.0 \
  --json-output /tmp/ds4-sm120-mt-bench.json \
  --log-dir /tmp/ds4-sm120-mt-bench-logs
```

You do not need to run the full matrix for every edit. Use `1,2` or `1,2,4`
for quick iteration, then widen to `1,2,4,8,16,24` before promoting a change.
For MTP, concurrency 8 and above may exceed available VRAM on endpoint-class
hardware. That is an acceptable physical-limit failure when the logs show
memory pressure; preserve the highest passing concurrency and the failure
snippet, and continue optimizing only if the change is likely to reduce real
memory use.

Use random prompts for controlled shape tests rather than final user-visible
throughput claims. For long-prefill stability, use smaller concurrency first:

```bash
python -m ds4_harness.cli bench-matrix \
  --vllm-bin /path/to/vllm/.venv/bin/vllm \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --host localhost \
  --port 8000 \
  --concurrency 1,2 \
  --dataset-name random \
  --random-input-len 8192 \
  --random-output-len 512 \
  --num-prompts 8 \
  --ignore-eos \
  --json-output /tmp/ds4-sm120-longprefill-bench.json \
  --log-dir /tmp/ds4-sm120-longprefill-logs
```

## Current Smoke Coverage

The harness currently includes:

- deterministic sanity: math, France capital, Spanish greeting
- OpenClaw-style `read` tool-call smoke
- subjective writing quality in Chinese
- English-to-Chinese and Chinese-to-English translation quality smoke
- long HTML coding prompts: aquarium animation and wall clock
- ToolCall-15 multi-turn tool-call loop with mocked tool responses
- logprobs oracle comparison for completion-style B200/H100 bundles
- vLLM `bench serve` matrix wrapper for both HF datasets and random shapes

This is not a full semantic eval. Treat subjective cases as regression smoke:
they catch obvious degradation, not subtle quality differences.

## Known Risks And Watchpoints

- CUDA graph correctness is accuracy-critical. If simple prompts produce
  garbage under compile/CUDA graph but pass under eager, stop and investigate
  graph safety before benchmarking.
- MTP is useful only after correctness and stability gates pass. It may alter
  generation trajectories and can expose scheduler or graph bugs. MTP
  high-concurrency failures can also be capacity limits, especially when C >= 8;
  do not block promotion solely on those tiers if lower-concurrency real
  workload gates pass and the failure is clearly memory-bound.
- Long-prompt prefill is a separate stability axis from 1024/1024 decode
  benchmarks. Always test it before recommending a branch to agent users.
- DGX Spark dual-node failures during safetensors loading are likely load-time
  host/unified-memory pressure until proven otherwise. Isolate branch vs loader
  vs recipe before blaming sparse MLA kernels.
- The harness does not start vLLM. A clean harness run requires a separately
  started server with the intended branch and flags.

## Suggested Next Work

1. Run the full harness against `ds4-sm120-full` after every promoted kernel
   change.
2. Add a recorded multi-turn agent transcript once a representative production
   workload is available.
3. If writing quality remains a complaint, add paired official-API/vLLM sample
   captures and compare structure/following, not only keyword smoke.
4. Continue SM120 tuning only after a baseline correctness run is archived with
   paths to logs and JSON outputs.
