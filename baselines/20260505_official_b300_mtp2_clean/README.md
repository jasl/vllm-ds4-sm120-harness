# 20260505_official_b300_mtp2_clean

This is a curated public reference bundle for DeepSeek V4 SM12x validation. It
is derived from raw harness artifacts, but intentionally excludes machine-local
paths, server logs, tokens, and private connection details.

## Known Non-Green Gates

This bundle is a current reference baseline, not necessarily a completely green acceptance run. Treat partial ToolCall-15 traces as current behavior references unless a later branch is explicitly trying to fix ToolCall policy quality.

- mtp: `74/90`; failures `TC-06`, `TC-11`, `TC-12`, `TC-14`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-07`, `TC-11`.

## Contents

- `manifest.json`: model, GPU topology, vLLM provenance, serve shape, and phase
  exit codes.
- `report.md`: readable baseline report with throughput, latency, correctness,
  runtime telemetry, and synthetic real-scenario OP cost metrics.
- `generation/`: no-MTP and MTP directory-driven generation transcripts and
  JSON rows when the source run used `generation-matrix`; coding cases also
  include same-basename `.html`, `.py`, or `.js` source sidecars.
- This bundle does not include an oracle export; use `generation/`,
  `toolcall15/`, and `performance/` as trajectory and performance references.
- `smoke/`: no-MTP and MTP chat smoke captures in JSON and Markdown.
- `toolcall15/`: no-MTP and MTP ToolCall-15 scores and traces.
- `kv_layout/`: synthetic packed KV byte-layout snapshots for indexer-cache
  regressions. Raw binary captures stay in the run artifact tree.
- `long_context/`: long-context sentinel retrieval probes for cache-layout
  regressions. These diagnostic references do not change accuracy scores.
- `prefix_cache/`: concurrent long-prefix cache reuse probes with request-level
  TTFT/elapsed timing plus KV cache, prefix hit, and preemption telemetry.
- `streaming_pressure/`: optional short concurrent streaming-pressure soak
  captures with request timing, chunk counts, and KV/runtime telemetry.
- `evals/`: optional `lm_eval` accuracy summaries such as GSM8K exact match
  when the source run included an eval phase.
- `performance/`: benchmark rows plus GPU/runtime telemetry summaries.

## Reuse

This bundle does not include an oracle export, so it is not a token-level
correctness oracle. Use its generation transcripts, ToolCall-15 traces,
performance rows, GPU telemetry, and runtime telemetry as the archived reference
for this run.
