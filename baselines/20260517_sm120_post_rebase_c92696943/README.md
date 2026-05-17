# 20260517_sm120_post_rebase_c92696943

This is a curated public reference bundle for DeepSeek V4 SM12x validation. It
is derived from raw harness artifacts, but intentionally excludes machine-local
paths, server logs, tokens, and private connection details.

## Known Non-Green Gates

This bundle is a current reference baseline, not necessarily a completely green acceptance run. Treat partial ToolCall-15 traces as current behavior references unless a later branch is explicitly trying to fix ToolCall policy quality.

- nomtp: `247/270`; failures `TC-06`, `TC-11`, `TC-06`, `TC-11`, `TC-06`, `TC-11`, `TC-14`, `TC-06`, `TC-06`, `TC-06`, `TC-15`, `TC-06`, `TC-14`.
- mtp: `248/270`; failures `TC-06`, `TC-11`, `TC-06`, `TC-12`, `TC-06`, `TC-06`, `TC-14`, `TC-06`, `TC-15`, `TC-06`, `TC-06`, `TC-15`.

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
- `mtp1_stability_followup/`: side study confirming the MTP=1 NCCL allgather
  hang persists on `nvidia-nccl-cu13 2.30.4`. **Not part of the regression
  matrix above.** See `mtp1_stability_followup/README.md` for full context;
  `report.md` has a summary section.
- `port_reference/kernel_reference_v2/`: synthetic (input, expected_output)
  reference for the three SM12x-specific kernels. `manifest.json` (with
  per-kernel SHA-256 + atol/rtol tolerances) is tracked; the six `.npz`
  blobs (~71 MiB) are local-only — see `kernel_reference_v2/README.md`
  for how to reproduce or request them.
- `port_reference/moe_configs/`: tuned fused-MoE FP8 Triton config for the
  production shape (`E=128, N=2048, block=[128,128]`) at TP=2+EP. This shape
  had no prior tuning in the vLLM tree.
- `port_reference/tokenizer_parity/`: tokenizer token-ID + SHA-256 reference
  for 12 prompts × 4 chat modes.
- `oracle/`: token-level top-20 logprob captures for 5 deterministic probe
  cases on the nomtp variant (cross-platform alignment audit reference).
- `nsys_profile/`: 125 MiB system-wide nsys trace of nomtp serve full
  lifecycle. Open in `nsys-ui` for the timeline.

## Pending follow-up (next run)

Three additional MoE shapes (TP=4+EP, TP=8+EP, TP=2 no-EP) were intentionally
not finished in this round — the tune was terminated after the production
shape landed. Same driver (`scripts/run_fp8_moe_tune.sh`) can finish them
later. GB10-tagged MoE configs will be produced separately on GB10 hardware.

## Reuse

This bundle does not include an oracle export, so it is not a token-level
correctness oracle. Use its generation transcripts, ToolCall-15 traces,
performance rows, GPU telemetry, and runtime telemetry as the archived reference
for this run.
