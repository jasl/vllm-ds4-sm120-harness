# 20260503_sm120_nomtp_ds4_sm120_6e1e7ecad_diagnostic

This is a curated public reference bundle for DeepSeek V4 SM12x validation. It
is derived from raw harness artifacts, but intentionally excludes machine-local
paths, server logs, tokens, and private connection details.

## Known Non-Green Gates

This bundle is a current no-MTP diagnostic reference, not a completely green
acceptance run or a full no-MTP/MTP release baseline. Treat partial ToolCall-15
traces as current behavior references unless a later branch is explicitly trying
to fix ToolCall policy quality.

- nomtp: `224/270`; failures `TC-06`, `TC-14`, `TC-06`, `TC-11`, `TC-12`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-12`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-12`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-11`, `TC-14`.
- generation: `313/315` rows passed; `clock_html` missed the required
  `Asia/Shanghai` term for `en/non-thinking` and `zh/think-max`.
- HF/MT-Bench: concurrency `4` exited non-zero and has no metrics row; other
  captured concurrencies (`1`, `2`, `8`, `16`, `24`) completed `80/80`.

## Contents

- `manifest.json`: model, GPU topology, vLLM provenance, serve shape, and phase
  exit codes.
- `report.md`: readable baseline report with throughput, latency, correctness,
  runtime telemetry, and synthetic real-scenario OP cost metrics.
- `generation/`: no-MTP directory-driven generation transcripts and JSON rows.
- `oracle/`: no-MTP deterministic `/v1/completions` compatibility entrypoint;
  `oracle/nomtp/` contains the variant-specific copies, including prompt token
  ids, generated tokens, token logprobs, top logprobs, and usage.
- `smoke/`: no-MTP chat smoke captures in JSON and Markdown.
- `toolcall15/`: no-MTP ToolCall-15 scores and traces.
- `kv_layout/`: synthetic packed KV byte-layout snapshots for indexer-cache
  regressions. Raw binary captures stay in the run artifact tree.
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
  --oracle-dir baselines/20260503_sm120_nomtp_ds4_sm120_6e1e7ecad_diagnostic/oracle \
  --top-n 20 \
  --require-prompt-ids \
  --low-margin-threshold 0.5 \
  --require-high-margin-token-match \
  --min-top1-match-rate 0.80 \
  --min-topk-overlap-mean 0.80 \
  --stability-json-output artifacts/manual/oracle_stability.json \
  --json-output artifacts/manual/oracle_compare.json
```

This bundle has no MTP variant. Use later MTP-specific bundles for MTP behavior
references instead of treating this no-MTP token oracle as interchangeable.
