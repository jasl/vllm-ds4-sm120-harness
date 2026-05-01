# 20260501_b200_main_51295793a

This is a curated public reference bundle for DeepSeek V4 SM12x validation. It
is derived from raw harness artifacts, but intentionally excludes machine-local
paths, server logs, tokens, and private connection details.

## Contents

- `manifest.json`: model, GPU topology, vLLM provenance, serve shape, and phase
  exit codes.
- `oracle/`: no-MTP deterministic `/v1/completions` cases with prompt token ids,
  generated tokens, token logprobs, top logprobs, and usage.
- `smoke/`: no-MTP and MTP chat smoke captures in JSON and Markdown.
- `toolcall15/`: no-MTP and MTP ToolCall-15 scores and traces.
- `performance/`: benchmark rows plus GPU/runtime telemetry summaries.

## Reuse

Run token-level comparison against a new local server:

```bash
python -m ds4_harness.cli oracle-compare \
  --base-url http://127.0.0.1:8000 \
  --oracle-dir baselines/20260501_b200_main_51295793a/oracle \
  --top-n 20 \
  --require-prompt-ids \
  --json-output artifacts/manual/oracle_compare.json
```

For MTP, use the smoke and ToolCall-15 data as trajectory and behavior
references instead of requiring exact token equality.
