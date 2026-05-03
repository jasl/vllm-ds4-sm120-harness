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

```bash
VLLM_VENV=<vllm-venv> \
PYTHON="${VLLM_VENV}/bin/python" \
LM_EVAL_BIN="${VLLM_VENV}/bin/lm_eval" \
LM_EVAL_TASKS=gsm8k \
LM_EVAL_NUM_FEWSHOT=8 \
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
  evidence.
- `toolcall15` for OpenAI-compatible tool-call loop behavior.
- `oracle-export` on an expensive reference host, then `oracle-compare` on
  SM120/SM121 for token-level divergence. Use prompt-id matching, top-k
  overlap, top-1 margin, and repeated-request stability to separate
  high-margin correctness failures from low-margin trajectory differences.
- `bench-matrix` on `philschmid/mt-bench` for representative throughput.
- `lm-eval` / `scripts/run_lm_eval.sh` for public GSM8K exact-match reporting.

Checked-in baselines are final result artifacts. This harness should consume
them as-is and write new analysis artifacts when they become stale; do not
backfill old baselines or add compatibility layers for retired baseline
content.

The baseline report parses serve-shape flags such as TP, max model length,
max sequences, max batched tokens, GPU memory utilization, MoE backend,
async scheduling, eager mode, parser choices, MTP speculative config, and
DeepSeek tokenizer/tool-call settings. Keep the serve command files in the
artifact tree so future reports can compare like with like.
