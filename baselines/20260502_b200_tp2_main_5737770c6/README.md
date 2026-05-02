# 20260502_b200_tp2_main_5737770c6

This is a curated public reference bundle for DeepSeek V4 SM12x validation. It
is derived from raw harness artifacts, but intentionally excludes machine-local
paths, server logs, tokens, and private connection details.

## Known Non-Green Gates

This bundle is a current reference baseline, not necessarily a completely green acceptance run. Treat partial ToolCall-15 traces as current behavior references unless a later branch is explicitly trying to fix ToolCall policy quality.

- nomtp: `225/270`; failures `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`.
- mtp: `225/270`; failures `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`.

## Contents

- `manifest.json`: model, GPU topology, vLLM provenance, serve shape, and phase
  exit codes.
- `report.md`: readable baseline report with throughput, latency, correctness,
  runtime telemetry, and synthetic real-scenario OP cost metrics.
- `generation/`: no-MTP and MTP directory-driven generation transcripts and
  JSON rows when the source run used `generation-matrix`.
- `oracle/`: no-MTP deterministic `/v1/completions` compatibility entrypoint;
  `oracle/nomtp/` and `oracle/mtp/` contain variant-specific copies when
  present, including prompt token ids, generated tokens, token logprobs, top
  logprobs, and usage.
- `smoke/`: no-MTP and MTP chat smoke captures in JSON and Markdown.
- `toolcall15/`: no-MTP and MTP ToolCall-15 scores and traces.
- `long_context/`: long-context sentinel retrieval probes for cache-layout
  regressions. These diagnostic references do not change accuracy scores.
- `evals/`: optional `lm_eval` accuracy summaries such as GSM8K exact match
  when the source run included an eval phase.
- `performance/`: benchmark rows plus GPU/runtime telemetry summaries.

## Reuse

Run token-level comparison against a new local server:

```bash
python -m ds4_harness.cli oracle-compare \
  --base-url http://127.0.0.1:8000 \
  --oracle-dir baselines/20260502_b200_tp2_main_5737770c6/oracle \
  --top-n 20 \
  --require-prompt-ids \
  --json-output artifacts/manual/oracle_compare.json
```

For MTP, use the smoke and ToolCall-15 data as trajectory and behavior
references instead of requiring exact token equality.
