# vLLM Correctness Gates For DeepSeek V4 SM12x

This harness stays repo-independent. Put vLLM kernel and model tests in the
vLLM checkout, after reading that checkout's `AGENTS.md`. Use this document as
the public checklist for which vLLM-side gates should accompany SM120/SM121
changes.

The checklist is informed by the ROCm DeepSeek V4 support work in
vllm-project/vllm PRs #41451, #40871, and #41217. The important lesson is to
combine a public accuracy scalar with small reference-backed math tests and the
harness-level oracle/benchmark phases.

## Public Accuracy Gate

Run GSM8K through OpenAI-compatible completions when a reference host is
available or before promoting a risky branch. The target vLLM venv must have
the API-capable harness extra installed:

```bash
python -m pip install "lm-eval[api]"
```

For public preview claims, capture both 0-shot and 5-shot 200-question slices:

```bash
VLLM_VENV=<vllm-venv> \
PYTHON="${VLLM_VENV}/bin/python" \
LM_EVAL_BIN="${VLLM_VENV}/bin/lm_eval" \
LM_EVAL_TASKS=gsm8k \
LM_EVAL_NUM_FEWSHOT=0 \
LM_EVAL_LIMIT=200 \
LM_EVAL_TOKENIZER_BACKEND=none \
LM_EVAL_NUM_CONCURRENT=4 \
scripts/run_lm_eval.sh

VLLM_VENV=<vllm-venv> \
PYTHON="${VLLM_VENV}/bin/python" \
LM_EVAL_BIN="${VLLM_VENV}/bin/lm_eval" \
LM_EVAL_TASKS=gsm8k \
LM_EVAL_NUM_FEWSHOT=5 \
LM_EVAL_LIMIT=200 \
LM_EVAL_TOKENIZER_BACKEND=none \
LM_EVAL_NUM_CONCURRENT=4 \
scripts/run_lm_eval.sh
```

For MTP accuracy captures, prefer correctness over speed. Lower
`MTP_LM_EVAL_NUM_CONCURRENT` or `LM_EVAL_NUM_CONCURRENT` if a pinned runtime
shows C>1 MTP instability. The report keeps the concurrency and generation
settings beside the exact-match result. `LM_EVAL_TOKENIZER_BACKEND=none` avoids
lm-evaluation-harness trying to load a Hugging Face tokenizer that may not yet
recognize `deepseek_v4`; requests are sent as strings with
`tokenized_requests=False`.

## vLLM-Side Micro Gates

Add or run focused vLLM tests when the touched code can affect these paths:

- RoPE / inverse RoPE: compare q/k after the accelerated path against a torch
  reference and assert the transformed tensors are actually consumed by the
  attention path. This catches bugs where a helper returns transformed values
  but callers continue using the original tensors.
- Sparse MLA prefill and decode: compare indexed sparse attention outputs
  against a reference implementation across short context, long prefill, and
  decode-with-cache shapes.
- FP8 cache encode/decode: cover the active FP8 format, blocked cache layout,
  prompt token ids, and logprobs-sensitive deterministic cases.
- TopK softplus/sqrt routing: run the CUDA-alike MoE routing test on SM120 and
  SM121 instead of only CUDA-specific platforms.
- MTP scheduler health: run no-MTP and MTP as separate server lifecycles and
  keep a guarded C>1 benchmark or eval shape to detect server hangs, shared
  memory broadcast stalls, or zero generation throughput.
- Long-context MTP reliability: keep the synthetic 64K-class latency matrix at
  least at C=3 and C=4. C=3 is the current smallest reproduced failure
  boundary; C=4 preserves the existing pressure point for regression checks.

Reference or fallback implementations are useful in tests. Do not leave slow
Python loops or fallback paths as the intended production path unless the vLLM
change explicitly accepts that performance tradeoff.

## Harness-Level Gates

Use this harness to capture behavior around the vLLM-side tests:

- `generation-matrix` for subjective writing, translation, and coding quality.
  For DeepSeek V4 `think-max`, run at least one targeted long-context quality
  probe with the model-card serving shape: `--max-model-len` at or above
  `393216`, `temperature=1.0`, `top_p=1.0`, and enough request `max_tokens` for
  reasoning plus final content. Short-window or low-output-cap failures should
  be labeled as budget diagnostics before they are used as correctness
  evidence. This `think-max` gate does not apply to the current GB10 profile:
  GB10 required acceptance is no-thinking with the 128K-class sentinel until
  384K+ context is reliable.
- `toolcall15` for OpenAI-compatible tool-call loop behavior. When running the
  thinking-mode matrix, keep `temperature=1.0` and `top_p=1.0`; treat those
  model-card sampling settings as part of the baseline contract.
- `oracle-export` on an expensive reference host, then `oracle-compare` on
  SM120/SM121 for token-level divergence. Use prompt-id matching, top-k
  overlap, top-1 margin, and repeated-request stability to separate
  high-margin correctness failures from low-margin trajectory differences.
  The strict top-1/top-k trajectory thresholds intentionally score the shared
  prefix before a low-margin fork; use the raw full-trajectory metrics as
  diagnostics after the sampled context has diverged.
- `bench-matrix` on `philschmid/mt-bench` for representative throughput. One
  transient infrastructure failure per concurrency tier is retried by default,
  so a recovered Hugging Face dataset timeout is recorded as run context rather
  than as a model-quality failure.
- `lm-eval` / `scripts/run_lm_eval.sh` for public GSM8K exact-match reporting.

## SM120 Refresh Promotion Gates

For SM120 branch promotion, carry the current refresh watchlist as explicit
quality gates instead of relying on a sales-refresh narrative:

- Short-context same-profile smoke: compare short-context C=1/2/4 throughput
  against the latest accepted same-host baseline. Treat it as a regression
  gate for scheduler, CUDA graph, MTP, and decode-kernel changes even when the
  active optimization targets long context.
- Long-context fixed-order latency: repeat 59K and 124K cold C=1/C=2 with the
  same warmup, run order, prefix-cache mode, request `max_tokens`,
  `--max-model-len`, and `--max-num-batched-tokens`. Report TTFT mean/max and
  elapsed time before deciding whether a TTFT movement is real or run-order
  variance.
- Mixed long-context C=2 fairness: report per-request decode min/max,
  decode min/max ratio, and ITL p95/p99/max. A slow-request path with high ITL
  p95/p99 remains an engineering follow-up even if the mean decode throughput
  or request success rate looks acceptable.
- GSM8K correctness: keep an explicit-venv `lm_eval` invocation in the refresh
  path. A limit-50 5-shot run is acceptable as a quick iteration smoke; public
  preview and branch-promotion evidence should still use the 0-shot and 5-shot
  200-question slices above when runtime budget allows.
- Long-context claim boundary: treat 256K/512K/1M behavior as estimates until
  the same gates run on four-card RTX PRO 6000 hardware at the target context
  length. Do not turn dual-card 128K-130K evidence into customer commitments
  beyond 128K.

### Development Feedback Gates

Keep these user-feedback shapes in the dual-card development loop because they
fit the local 128K-130K ceiling and directly cover the latest PR feedback:

- Short prefill sweep for the reported `BLOCK_M=16 -> 64` regression in
  [issuecomment-4504312139](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4504312139):
  run `bench_random_prefill_sweep` with `RANDOM_PREFILL_INPUT_LENS=1024,4096,16384,65536`,
  `RANDOM_PREFILL_OUTPUT_LEN=1`, `RANDOM_PREFILL_CONCURRENCY=1`, and prefix
  cache disabled. Compare input-token throughput and TTFT against the latest
  same-host accepted baseline before promoting FP8 MQA prefill kernel changes.
- MTP=1 prefix-cache stability proxy for
  [issuecomment-4497389943](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4497389943):
  run the `mtp1` variant with `SERVE_PREFIX_CACHE_MODE=enabled`,
  `SERVE_MAX_MODEL_LEN=16384`, `B200_BLOCK_SIZE=256`,
  `PREFIX_CACHE_LINE_COUNT=384`, `PREFIX_CACHE_FAIL_ON_REGRESSION=1`, and
  `cudagraph_mode=FULL_AND_PIECEWISE`. This is a stability gate: failures,
  `/metrics` disconnects, or post-probe server unresponsiveness are regressions
  even if request-level cached-token counters are noisy.
- Multi-session decode pressure proxy for
  [issuecomment-4505504798](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4505504798):
  run `streaming_pressure_matrix` on the local TP=2 server with at least
  short C=4, issue #7 5K C=4, 124K-class C=2, and 59K-class C=4 cases. Treat
  per-request ITL p95/p99 and request failures as first-class gate outputs.
- Mixed long/short arrival pressure: run `long_context_mixed_arrival` with
  one case where a long request arrives after an existing decode stream starts
  and one case where a short request arrives behind a long prefill. This is the
  local proxy for deciding whether best-effort single-instance scheduling is
  still enough, or whether a deployment needs stronger prefill/decode
  isolation.

The convenience profile `scripts/run_sm120_local_quality_gates.sh` wires the
prefix-cache-disabled development gates together with the existing
long-context, MT-Bench, and GSM8K checks for dual RTX PRO 6000 development
runs. The MTP=1 prefix-cache proxy intentionally stays outside that default
profile because it needs `SERVE_PREFIX_CACHE_MODE=enabled` and a separate
`mtp1` serve.

### User-Reported External Gates

Keep the following as external/user-reported gates until a local four-card
environment is available. They are required before public claims for the
reported four-card or 512K/1M shapes:

- TP=4, FP8 KV, prefix-cache-on 512K short-prefill sweep: use
  `EXTERNAL_GATE_MAX_MODEL_LEN=524288` with `bench_random_prefill_sweep` and
  the same 1K/4K/16K/64K input lengths from
  [issuecomment-4504312139](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4504312139).
- TP=4, FP8 KV, prefix-cache-on 1M multi-session decode pressure: use
  `EXTERNAL_GATE_MAX_MODEL_LEN=1048576`, `STREAMING_PRESSURE_MATRIX_CASE_SPECS`
  containing C=4 and C=6 long-session cases, and require runtime telemetry to
  show no decode collapse like the 2-3 tok/s report in
  [issuecomment-4505504798](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4505504798).
- TP=4 long/short mixed-arrival pressure: use
  `long_context_mixed_arrival` with the external profile defaults, then inspect
  per-request decode throughput and ITL p95/p99 before claiming that 512K/1M
  multi-session workloads are healthy.
- TP=2 MTP=1 prefix-cache crash/stability confirmation: when reproducing the
  exact user AM5/PHB shape from
  [issuecomment-4497389943](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4497389943),
  preserve their NCCL flags, `--disable-custom-all-reduce`, FP8 KV, block size
  256, and FULL_AND_PIECEWISE CUDA graph. Record both `/metrics` deltas and
  whether the server remains responsive after the probe.

The convenience profile `scripts/run_sm120_external_reported_gates.sh` refuses
to run unless `EXTERNAL_GATE_MAX_MODEL_LEN` is set, so 512K and 1M evidence is
never confused with the dual-card local development gate.

Checked-in baselines are final result artifacts. This harness should consume
them as-is and write new analysis artifacts when they become stale; do not
backfill old baselines or add compatibility layers for retired baseline
content.

The baseline report parses serve-shape flags such as TP, max model length,
max sequences, max batched tokens, GPU memory utilization, MoE backend,
async scheduling, eager mode, parser choices, MTP speculative config, and
DeepSeek tokenizer/tool-call settings. Keep the serve command files in the
artifact tree so future reports can compare like with like.
