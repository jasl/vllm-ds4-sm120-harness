# Baseline of record — 2026-08-07, tree `db8f836e8b`

Reference set for future optimisation work. Everything below ran on the pushed
tree after the 08-06/07 fix wave (upstream merge `6d1358ebd3` + BOS-leak fix
`d8885a3335` + DSpark aux `+1` fix `71096d3f72` + `#35`/`#31`/`#30` fixes +
drafter-gate sentinel `db8f836e8b`), with clean tracked trees fingerprint-
matched on all four nodes.

## Environment

- Model: `deepseek-ai/DeepSeek-V4-Flash-0731`, serve shape 2× GB10 TP=2
  (.116 head / .119 worker), mml 131072, KV fp8, prefix cache on,
  DSpark nst=5 probabilistic (spec arms), gpu-mem-util 0.85, mnbt 8192.
- FlashInfer 0.6.16 (python + cubin + jit-cache wheel).
- `apache-tvm-ffi==0.1.11` + `tilelang==0.1.12` operational combo
  (production-proven; note: the jit-cache × tilelang × tvm-ffi dependency
  triangle makes NVFP4 unserveable until the next FlashInfer release — see
  memory `project_fi_kernel_provenance_trap`).
- Results dir on .116: `/home/jasl/tmp/baseline_20260807_db8f836e8b/`.

## Perf — llama-benchy standard (TP=2)

| depth | pp2048 (tok/s) | tg128 base | tg128 spec (dspark5) |
|---|---|---|---|
| d8192 | 1432.27 ± 20.50 | 46.31 ± 1.83 | 54.33 ± 2.49 |
| d16384 | 1364.01 ± 14.56 | 38.63 ± 2.67 | 47.67 ± 2.49 |
| d32768 | 1225.19 ± 2.65 | 44.64 ± 5.73 | 55.33 ± 5.19 |

tg128 spec at d8192/d32768 runs 12–19% above the same-night pre-baseline
gate run — direction consistent with the aux `+1` fix lifting DSpark
acceptance, but within benchy's documented 9–12% single-run spread; treat as
a lead, not a conclusion, until repeated.

## Correctness anchors (TP=2 dspark5 serve)

| gate | result |
|---|---|
| issue19 instruction-following (JSON-only) | PASS |
| arthur long-context coherence c=1 (~123K) | 2/2 |
| arthur long-context coherence c=12 (~123K) | 23/24 (band top; post-aux-fix TP=2 samples 22/24/23, historical band 20–24 mean 22.25) |
| GSM8K 8-shot strict | **0.9439** (±0.0063) |
| GSM8K 8-shot flexible | 0.9484 (±0.0061) |
| multi-needle (8 needles + 8 distractors, seed 20260807) @ ~42K tok | 24/24 needles, 0 leaks (3 repeats) |
| multi-needle @ ~80K tok | 24/24 needles, 0 leaks (3 repeats) |

## Known open items baked into this baseline

- Drafter step-1 NaN rows (rows>0 in mixed batches): output-correct (the
  recovered-sampling fix rejects and recovers from target) but costs draft
  slots; ragged first-pass slot-mapping audit pending (dossier in memory
  `project_bos_leak_recovered_sampling_fix`). Fixing it should only IMPROVE
  spec throughput vs this baseline.
- TP=4 c=12 arthur has no historical band; the 08-06 sample was 21/24 with a
  clean c=1 discriminator (2/2) — concurrency-batch numerics, not corruption.
- The deep long-context Tier-A standard (`run_gb10_deep_long_context_standard.sh`)
  is a tokenspeed-side suite and refuses vLLM baseline hosts by design; the
  vLLM long-context legs here are arthur (~123K) + the multi-needle probe.
