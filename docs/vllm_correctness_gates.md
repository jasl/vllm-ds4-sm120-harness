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
- `frontier-context-sweep` for ds4-style fixed prompt-file prefixes. It records
  the server-returned prompt token count, TTFT, input/prefill tok/s, decode
  tok/s, and ITL p95/p99 across context frontiers. Treat it as a development
  observation gate until a stable same-host baseline exists.

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
- Exact HTTP `/metrics` stress script proxy for
  [issuecomment-4507780873](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4507780873):
  run `prefix_cache_stress` through
  `scripts/run_sm120_mtp1_prefix_cache_stability.sh`. This keeps the reported
  TP=2, MTP=1, FP8 KV, prefix-cache-on, 16K max-model-len, block-size-256,
  non-streaming chat shape separate from the prefix-cache TTFT regression
  probe. Treat any trial exception, `/metrics` disconnect, or post-probe
  server unresponsiveness as a regression; do not fail this gate only because
  the prefix-cache hit rate differs from the reporter's machine.
- Multi-session decode pressure proxy for
  [issuecomment-4505504798](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4505504798):
  run `streaming_pressure_matrix` on the local TP=2 server with at least
  short C=4, issue #7 5K C=4, 124K-class C=2, and 59K-class C=4 cases. Treat
  per-request ITL p95/p99 and request failures as first-class gate outputs.
- Long-context decode-concurrency proxy for
  [jasl/vllm issue #8](https://github.com/jasl/vllm/issues/8):
  run `long_context_decode_concurrency` with a 124K-class prompt, C=1/C=2,
  and a long enough output budget to expose decode collapse after prefill.
  Use cold cache for the local prefix-cache-disabled development profile; use
  warm cache only in a separate prefix-cache-enabled serve when isolating pure
  decode behavior.
- Mixed long/short arrival pressure: run `long_context_mixed_arrival` with
  one case where a long request arrives after an existing decode stream starts
  and one case where a short request arrives behind a long prefill. This is the
  local proxy for deciding whether best-effort single-instance scheduling is
  still enough, or whether a deployment needs stronger prefill/decode
  isolation.
- DS4 prompt-file frontier and semantic gates: include
  `frontier_context_sweep` and `ds4_story_recall_semantic` in the development
  matrix. The story gate uses the full `ds4_story_recall.txt` prompt with its
  own 128-token answer budget so it does not change the 59K/124K latency
  phase's 64-token measurement shape. The story gate requires all sixteen
  `Name=number` assignments; the security-audit prompt remains
  latency/streaming observation only. Initial baseline label:
  `20260524_ds4_harness_frontier_semantic_baseline`.

The convenience profile `scripts/run_sm120_local_quality_gates.sh` wires the
prefix-cache-disabled development gates together with the existing
long-context, MT-Bench, and GSM8K checks for dual RTX PRO 6000 development
runs. The MTP=1 prefix-cache proxy intentionally stays outside that default
profile because it needs `SERVE_PREFIX_CACHE_MODE=enabled` and a separate
`mtp1` serve.

For branch-promotion tradeoff decisions, prefer
`scripts/run_sm120_user_feedback_matrix.sh` over running one reported shape at
a time. It executes the prefix-cache-disabled local matrix first, then runs the
MTP=1 prefix-cache stress shape in a separate prefix-cache-enabled serve, and
writes one `user_feedback_matrix_summary.md` plus JSON summary. Use that
combined summary to choose the tradeoff across C=1/2/4 short latency, 59K/124K
long latency, issue #8 decode fairness, mixed-arrival pressure, issue #7
streaming pressure, GSM8K, prefill throughput, ds4-style frontier latency,
ds4 story-recall semantic status, and prefix-cache stability. The
profile hard-gates GSM8K limit-200 at `exact_match_flexible >= 0.94` and
`exact_match_strict >= 0.925`, so any further correctness drop blocks the
matrix rather than becoming a narrative footnote.

For DS4-inspired follow-up work, use
`scripts/run_sm120_ds4_absorption_stress.sh` as the combined validation wrapper
after a candidate has passed a narrower probe. Its default path runs the
user-feedback matrix plus the safe 59K-class issue #10 proxy and captures
`nvidia-smi` and boot-kernel GPU signal snapshots before and after each phase.
Known crash shapes stay opt-in:

- `RUN_DS4_STRESS_ISSUE8_RECHECK=1 ISSUE8_ALLOW_HOST_REBOOT_RISK=1` replays the
  2026-05-25 issue #8 128K-class no-MTP, prefix-cache-enabled, C=1/C=2,
  1024-output-token proxy.
- `RUN_DS4_STRESS_ISSUE10_HIGH_RISK=1 ISSUE10_ALLOW_HOST_REBOOT_RISK=1` enables
  the issue #10 128K-class startup proxy path.

Do not mix those opt-in crash probes into a promotion baseline unless the host
can be rebooted afterward and partial artifacts are clearly labeled.

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
- TP=2 GB10 recipe and benchmark gap tracking from the
  [NVIDIA Developer Forums thread](https://forums.developer.nvidia.com/t/deepseek-v4-flash-official-fp8-running-across-2x-dgx-spark-tp-2-mtp-200k-ctx-recipe-numbers/370309):
  keep `long_context_decode_concurrency` in the external profile alongside
  `bench_random_prefill_sweep`. When comparing forum-style `llama-benchy`
  `pp2048` / `tg128` numbers, record the exact serve command, tokenizer,
  `max_num_batched_tokens`, `max_num_seqs`, prefix-cache mode, sampler/all-reduce
  flags, and NCCL/network environment before treating a 20-40% delta as a vLLM
  kernel regression.
- TP=2 GB10 startup/crash proxy for
  [jasl/vllm issue #10](https://github.com/jasl/vllm/issues/10): until the
  GB10 cluster is available, run `scripts/run_sm120_issue10_startup_gate.sh`
  on the dual-card RTX PRO 6000 host. This is a best-effort SM120 proxy, not a
  full reproduction of the SM121 dual-node failure. It preserves the risky
  serve knobs from the report where the 96GB memory budget allows it: MTP=2,
  prefix cache enabled, chunked prefill, FP8 KV, block size 256,
  `max_num_seqs=4`, `--disable-custom-all-reduce`, and FULL_AND_PIECEWISE CUDA
  graph. The report used `--gpu-memory-utilization 0.83` and
  `--max-num-batched-tokens 16384`; the RTX PRO 6000 proxy defaults to
  `SERVE_MAX_MODEL_LEN=65536`, `ISSUE10_GPU_MEMORY_UTILIZATION=0.977`, and
  `ISSUE10_MAX_NUM_BATCHED_TOKENS=4096` so the public script is safe enough for
  regular startup, prefix-cache, and 59K-class streaming checks. For exact
  low-context recipe replay,
  set `ISSUE10_MAX_NUM_BATCHED_TOKENS=16384`; for exact memory replay on hosts
  with enough headroom, also set `ISSUE10_GPU_MEMORY_UTILIZATION=0.83`. The
  128K-class proxy is an isolation/debug run, not a default gate: set
  `SERVE_MAX_MODEL_LEN=131072`, matching line-count overrides, and
  `ISSUE10_ALLOW_HOST_REBOOT_RISK=1` only on a host where an OS reboot is
  acceptable, because this shape has produced NVRM/UVM fatal driver state on
  dual-card SM120. The first observed Python-side failure in that 128K proxy was
  `Triton Error [CUDA]: unspecified launch failure` from sparse MLA prefill
  (`accumulate_indexed_sparse_mla_attention_chunk` /
  `_accumulate_indexed_attention_chunk_multihead_kernel`), followed by NCCL
  heartbeat disconnects and NVRM/UVM fatal state. Next isolation knobs should
  keep FULL_AND_PIECEWISE CUDA graph enabled and compare
  `VLLM_TRITON_MLA_SPARSE=1` versus `0`, then vary MTP and prefix cache
  independently. Treat
  startup timeout, server exit before readiness, post-probe unresponsiveness,
  Xid/driver errors, or repeated health disconnects as evidence for further
  isolation. If the proxy passes, keep the wording narrow: the SM120
  scaled-down path stayed healthy; the original GB10 393K dual-node report
  still needs GB10 validation.
  Keep this proxy out of the default user-feedback matrix. Run it with
  `RUN_USER_FEEDBACK_ISSUE10=1` only when the host can be rebooted afterward,
  and keep partial artifacts separate from promotion baselines.
  The crash backlog now includes both the SM120 128K-class proxy fatal-driver
  state and the reporter's GB10 dual-node reboot-only reproduction at
  `a937d4b287`; resolve those separately from ordinary promotion baselines.
  A post-reboot 59K-class MTP startup and prefix-cache proxy passed under
  `20260525_issue10_safe_59k_mtp_prefix_proxy`; keep citing that only as SM120
  scaled-down evidence. The 128K-class SM120 proxy and the 393K GB10 dual-node
  report remain separate crash-backlog items.
- TP=4 W4A16 + Marlin MoE concurrent thinking-mode gate for
  [jasl/vllm issue #12](https://github.com/jasl/vllm/issues/12): run
  `scripts/run_sm120_issue12_w4a16_marlin_gate.sh` only when the external
  W4A16 model artifact and AIME runner are available. Set
  `ISSUE12_W4A16_MODEL` to the artifact and `ISSUE12_AIME_RUNNER_COMMAND` to a
  command that drives the reported AIME 2024, C=4, thinking/high,
  32K-output-token workload against `BASE_URL`. The profile preserves the
  reported vLLM shape: TP=4, MTP=1, prefix cache disabled, FP8 KV, block size
  256, `max_model_len=65536`, `max_num_seqs=8`,
  `max_num_batched_tokens=8192`, sparse MLA with head block size 4,
  `VLLM_USE_FLASHINFER_SAMPLER=0`, disabled custom all-reduce, safetensors load
  format, and FULL_AND_PIECEWISE CUDA graph. Treat token-stream corruption,
  CUDA illegal memory access, server unresponsiveness, Xid/NVRM/UVM driver
  errors, or host reboot requirements as failures. This is an external
  user-reported gate, not a local default or promotion baseline, until a
  four-card SM120 environment and the required W4A16/AIME assets are available.

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
