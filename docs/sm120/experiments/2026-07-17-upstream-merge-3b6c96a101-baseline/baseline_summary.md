# GB10 2×SM121 DeepSeek-V4-Flash baseline — `f63bfd3d7b` (2026-07-17)

**New baseline of record** after merging upstream/main `3b6c96a101` (195 commits on
top of `cfddacbc47`) into the SM12x fork. Supersedes
`2026-07-11-upstream-merge-5e43b2cfa7-baseline`.

## Build / environment
| | |
|---|---|
| vLLM head | `f63bfd3d7b` (merge of `cfddacbc47` + upstream `3b6c96a101`) |
| merge | 195 upstream commits; 11 conflicts hand-resolved, 0 fork features dropped, 180 fork commits retained, 0 behind upstream |
| torch | 2.11.0+cu130 |
| flashinfer | 0.6.14 (pin held through the merge) |
| nvidia-cutlass-dsl | **4.6.0** (upstream bump, was 4.5.2) |
| quack-kernels | **0.6.1** (floor raised 0.4.0 → 0.6.0, see below) |
| nvidia-nccl-cu13 | 2.30.7 |
| GPUs | 2× GB10 (SM121a), TP=2, RoCE switched CRS804 (192.168.100.116/.119) |
| serve | KV 179,225 tokens @ util 0.85; boot ~510s; `ll_bf16` router-GEMM warmup clean |

## Serve config (pinned standard — unchanged)
MTP2, fp8 KV (`fp8_ds_mla`), prefix-cache ON, `cudagraph_mode=FULL_AND_PIECEWISE`,
`max-model-len 49152`, `gpu-mem-util 0.85`, `max-num-seqs 64`,
`max-num-batched-tokens 8192`.

## Perf — llama-benchy STANDARD (pinned `@b220b7c9`, pp2048 tg128, C=1, 3 runs, prefix-cache)
**Two independent full runs** (fresh serve each) — the repeat was run specifically to
establish run-to-run variance before interpreting decode.

| depth | ctx_pp (mean of 2) | vs `5e43b2cfa7` | pp2048 (mean of 2) | vs base | tg128 (mean of 2) | vs base |
|---|---|---|---|---|---|---|
| 8192  | 1839.2 | **+4.7%** | 1391.4 | −0.0% | 39.0 | −6.8% |
| 16384 | 1794.8 | +1.2% | 1331.3 | +0.7% | 37.1 | −6.3% |
| 32768 | 1703.8 | +0.3% | 1210.6 | +0.9% | 39.1 | +5.4% |

Per-run detail:

| depth | ctx_pp r1 / r2 | pp2048 r1 / r2 | tg128 r1 / r2 |
|---|---|---|---|
| 8192  | 1847.5 ± 14.7 / 1830.8 ± 2.0 | 1390.2 ± 39.2 / 1392.6 ± 9.8 | 37.5 ± 2.0 / **40.5 ± 3.0** |
| 16384 | 1792.4 ± 25.9 / 1797.2 ± 3.9 | 1344.7 ± 10.4 / 1317.8 ± 4.8 | 38.1 ± 2.6 / 36.2 ± 3.7 |
| 32768 | 1697.3 ± 8.2 / 1710.3 ± 3.5  | 1211.8 ± 1.4 / 1209.5 ± 14.3 | 39.5 ± 1.7 / 38.8 ± 1.1 |

**Verdict: prefill flat-to-up, decode flat within measurement resolution.**

- **Prefill is a real gain.** `ctx_pp` +4.7% at d8192, ~flat deeper. This metric is
  tight (σ ≈ 2–26 across both runs), so the delta is resolvable and real.
- **Decode is NOT resolvable at this precision.** `tg128` run-to-run swing is up to
  **±3 t/s (~8%)** on identical code/config — d8192 read 37.5 on run 1 and 40.5 on
  run 2. The 2-run mean is −2.8% averaged across depths, with the sign flipping by
  depth (−6.8 / −6.3 / **+5.4**). That is the signature of noise, not a systematic
  regression, and is consistent with decode being host-CPU-bound
  (`project_decode_hostbound_not_ar_wall`). **A single benchy run cannot support any
  decode claim below ~8%** — do not report one-run decode deltas as regressions.

## Correctness / functional (this head, this serve — all GREEN)
- **GSM8K** (full 1319q, 8-shot, max_gen 2048): **0.9545 strict / 0.9538 flexible**
  (stderr 0.0057); IMA-clean through the long-gen run. In the historical 0.945–0.965
  band. NB: prior baselines quoted 200q runs — not directly comparable; this is the
  full set.
- **Coherence/recall** (arthur, ~28k ctx): **c=1 2/2 PASS** (the deterministic recall
  discriminator — perfect); **c=12 23/24** (IMA=0, coherent). The single marginal
  needle under concurrency-12 is the known pre-existing batch-numerics sensitivity
  (greedy+MTP FP reduction order), not recall corruption. Matches the 22–23/24 band.
- **#19 instruction-following** (JSON-only): **PASS**.
- **Tool-calling** (toolcall-15, en × 3 thinking modes × 3 rounds = 135 cases,
  temp 1.0): **86.3% content (233/270), engine-clean — 0×500, 0 IMA**.
  Historical scores are 45-case runs: 87 / 90 / 90 / 93 / 96. At 135 cases (σ ≈ 2.6%)
  vs 45 cases (σ ≈ 4.5%), 86.3% is ~1.4σ from the ~90% central estimate — sampling
  noise. The engine criterion (what a merge can actually break) is clean.
- **Unit suite**: 224 passed, 1 environmental (`World size (2) > available GPUs (1)`
  — needs 2 GPUs/node). DSv4 fork tests: 20 passed.

## Defects found and fixed during this merge
1. **Dropped fork param (`alignment_tokens`)** — `FullAttentionManager.cache_blocks`
   lost the fork's `alignment_tokens`/`retention_interval` params in the merge, while
   `kv_cache_coordinator` still passes them → `TypeError` on the first cached request
   (41 unit failures). **Invisible to per-file conflict review** because the broken
   contract spans coordinator↔manager. All 6 `cache_blocks` overrides re-verified.
2. **quack 0.5.0 × cutlass-dsl 4.6.0** — upstream bumped the DSL to 4.6.0, which moved
   `ThrMma` out of `cute.core`; quack <0.6 annotates against the removed path and
   fails to import → engine start `AttributeError`. The open floor `quack-kernels>=0.4.0`
   was **satisfied by an already-cached 0.5.0**, so it never upgraded alongside the
   bump. Fixed: quack 0.6.1 on both nodes; floor raised to `>=0.6.0` in
   `requirements/cuda.txt` with the reasoning recorded. Same shape as the nccl re-pin
   trap: **open floor + stale venv = silently mismatched pair**. Arguably an upstream
   under-constraint worth reporting.

## Review outcome (4-lens workflow + adversarial verify)
8 findings raised, 1 confirmed, 2 high-severity refuted with hard evidence, rest low.

- **Confirmed (upstream's bug, NOT ours, NOT reachable for us)**: upstream restructured
  the sparse-MLA hierarchy — deleted `SparseMLAAttentionImpl` (whose hard
  `isinstance` bar previously made `forward_mha` unreachable for sparse impls),
  replaced it with a soft `is_sparse` gate that performs **no capability check**, moved
  its two CI'd datacenter backends onto `SparseMLACommonImpl` (which implements
  `forward_mha`), and left exactly the three **non-CI** platforms — **SM120, XPU,
  ROCm** — on `MLAAttentionImpl`, whose `forward_mha` is `raise NotImplementedError`.
  - **Not our regression**: dispatcher + impl are taken **upstream-verbatim**
    (`git diff 3b6c96a101 f63bfd3d7b` on those files is empty). Nothing dropped by our
    conflict resolution.
  - **Not reachable for DSv4-Flash**: our model uses its own attention module
    (`DeepseekV4FlashInferMLAAttention`), never the generic dispatcher. Verified
    empirically on the live serve: 8-word and 3072-word prompts both return 200; zero
    `forward_mha`/`NotImplementedError` in the log. This is why the #19 gate passes
    with short prompts.
  - **Still a real latent upstream bug** for other sparse DeepSeek models on
    SM120/XPU/ROCm via the generic path → worth an upstream report (SM120 is our
    platform). Out of scope for this merge.
- **Method note**: both the reviewer and its adversarial verifier were **partly wrong
  in opposite directions**. The reviewer cited `vllm/v1/attention/layers/mla_attention.py`
  — a path present in **none** of the three trees (real path:
  `vllm/model_executor/layers/attention/mla_attention.py`). The verifier's confident
  "critical correction" blamed our merge for deleting a fork guard that **upstream**
  deleted. Structured output + precise line numbers are not evidence; the trees are.

## Reproduce
```bash
# from a GB10 head node
VLLM_ROOT=/home/jasl/tmp/vllm-merge-20260711 \
VLLM_VENV=/home/jasl/tmp/ds4-sm120-harness/vllm/.venv \
  scripts/run_gb10_llama_benchy_standard.sh
```
