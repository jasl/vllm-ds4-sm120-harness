# Shelved diagnostic drivers — 2026-06-20 PR audit archive

These are one-off diagnostic / A-B drivers from investigations that are now
**closed or refuted**. They are archived here (not under `scripts/`) so the
top-level gate set stays limited to durable, re-runnable gates. They are kept
for provenance and for re-running the underlying experiment if a question
re-opens. Most depend on env levers or branch state that are **not** in the
shipped PR head (`codex/ds4-sm120-min-enable` @ `88ec87e1e0`), so they will not
run as-is against the current build without restoring those.

## arthur decode-concurrency cliff (REFUTED indexer-amplifier hypothesis)

The long-context × concurrency decode cliff was re-diagnosed by measurement as
**MoE-Marlin GEMM (~28%) + NCCL all-reduce (~27.5%) + dense FP8 GEMM (~18%)
bound** — NOT an eager-indexer amplifier and NOT scheduler-fixable. The
`WIDTH_CAP` / `TIME_INDEXER` probe envs these drivers toggle live only on the
discarded experimental commit `f5a52a9c7a` (indexer width-cap, never promoted,
not on origin), so they cannot probe the shipped build.

- `run_gb10_arthur_cliff_attrib.sh` — reproduce + attribute the cliff on GB10.
- `run_gb10_arthur_decode_profile.sh` — torch-profile a clean decode window.
- `run_gb10_arthur_decode_sweep.sh` — depth × concurrency decode sweep (2-node).
- `run_gb10_arthur_indexer_time_ab.sh` — eager indexer per-step CUDA-event A/B.
- `run_sm120_arthur_mtp_probe.sh` — MTP on/off isolation of the gibberish.

## breakable cudagraph (decision FLIPPED — DSv4 now out of auto-enable)

DSv4 was re-enabled on breakable cudagraph on 2026-06-18, then **flipped back**
to `FULL_AND_PIECEWISE` (DSv4 dropped from auto-enable) for the 1.5-3.8× MTP
decode win; upstream's #45972 revert of the #45309 garbage bug is already in the
rebase base, so breakable is no longer needed for correctness. The audit
inlined the gate to MiniMax-only.

- `run_gb10_breakable_ab.sh` — breakable vs FULL_AND_PIECEWISE A/B on GB10.
- `run_gb10_reenable_validate.sh` — **asserts the now-removed auto-enable path**;
  it would false-FAIL against the current build. Kept only as a record of the
  06-18 re-enable validation.

## NVFP4 MoE backend A/Bs (concluded)

NVFP4 serves on SM12x and is GSM8K-correct, but is not a memory or perf win over
MXFP4 on SM120 (−8%). The `flashinfer-b12x` NVFP4 GEMM lever
(`VLLM_NVFP4_GEMM_BACKEND`) was **moved out of the PR** (commit `99a9f10e7a`
reverted on the audit-cleanup branch; preserved on
`backup/min-enable-88ec-pre-audit-20260620` in the vllm repo). b12x is only
reachable via that env — `--linear-backend flashinfer_b12x` is filtered out of
auto-selection — so to re-run these, restore the env+map from that backup
commit first.

- `run_sm120_nvfp4_vs_mxfp4_ab.sh` — NVFP4 vs MXFP4 prefill/decode/memory A/B.
- `run_sm120_nvfp4_b12x_moe_ab.sh` — NVFP4 MoE backend (b12x vs cutlass) A/B.
  NOTE: mutates a vLLM oracle file via an escape hatch — do not promote to a
  top-level gate.
