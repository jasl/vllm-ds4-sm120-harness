# FlashInfer SM120 Packed Prefill — Lucifer Parity

Status: in-progress (autonomous)

## Goal

Close, match, then surpass the Lucifer fork's DeepSeek-V4-Flash **prefill**
throughput on SM120 / SM121. Decode is already solved and ahead (gated
FlashInfer SM120 packed sparse-MLA decode, promoted to the PR). This phase
optimizes the prefill path only.

## Baseline gap (prior controlled measurement)

Holding MoE = MARLIN and swapping only the prefill kernel (same host / tool /
config), client tok/s at 8k / 64k:

- our FlashMLA default prefill: 9,409 / 7,666
- Lucifer sparse-sm120 prefill: 11,978 / 11,278  (**+27% / +47%**)

The sparse-sm120 prefill kernel is the dominant lever (recovers ~85–90% of the
gap); `--moe-backend flashinfer_cutlass` is a separate, additive ~+7–8%.

## Starting point — v1 packed-prefill port (VALIDATED)

Branch `codex/ds4-sm120-flashinfer-prefill-dev-20260617` @ `8d83cd9d9`
(based on PR head `73e99c165`). v1 = a `_forward_prefill` override on
`DeepseekV4FlashInferSM120Attention` that drives the FlashInfer
`_SparseMLAPagedAttentionRunner` packed prefill kernel (auto-dispatched for
>64-token batches), gated by `VLLM_DEEPSEEK_V4_FLASHINFER_SM120_PREFILL`
(default off → FlashMLA indexed-D512 prefill byte-for-byte).

Revalidation 2026-06-17 (RTX / SM120, A/B gate-OFF vs gate-ON; pure-Python
source-shadow onto the built decode worktree + flashinfer-main 0.6.13;
TP=2 / MTP2 / fp8 KV / max_model_len 131072 / gpu-mem 0.90):

| metric | gate-OFF (FlashMLA) | gate-ON (v1) | delta |
|---|---|---|---|
| prefill 8k client tok/s (N=10) | 9,336 | 10,033 | **+7.5%** |
| prefill 64k client tok/s (N=1/2, low-conf) | 6,516 | 8,700 | positive |
| GSM8K 5-shot limit-100 flexible / strict | 0.92 / 0.91 | 0.91 / 0.89 | within ~1σ |

Serve clean (UP ~75s, packed-decode path active, no errors / no GPU wedge,
clean teardown). v1 captures ~1/4 of the available prefill gain.

Known overhead (hypothesis): the per-token SWA window indices are
**recomputed per-layer (~60×)** inside `_forward_prefill`.

## Plan

1. **SWA → metadata** — compute the prefill SWA window indices once in the
   metadata builder (mirror the decode path), consume them in `_forward_prefill`.
   ⚠️ A prior attempt (v2) hung warmup: the SWA kernel (grid = num_tokens) went
   OOB on the warmup prefill-dummy block_table. Re-do with a validated
   warmup-dummy guard before re-serving.
2. If insufficient — adopt Lucifer's single unified top-k decomposition (drop
   the separate large SWA window).
3. Profile to confirm the actual bottleneck.
4. Bundle FI-CUTLASS MoE (`--moe-backend flashinfer_cutlass`) — additive +7–8%.

## Methodology

- Standard harness tools: GSM8K via `lm_eval` (gsm8k, 5-shot); prefill via
  `llm_decode_bench.py --prefill-only --prefill-contexts 8k,64k`.
- A/B every change: gate-OFF (FlashMLA default) vs gate-ON (port).
- Raise the 64k prefill sample count (v1 revalidation had N=1/2 at 64k → the
  64k delta is currently low-confidence; the 8k N=10 +7.5% is the solid signal).
- Freeze-safe GPU ops (user away): one serve at a time, robust teardown,
  startup-only death-check, NEVER reset/reboot a wedged GPU (physical
  power-cycle only). Minimize serve churn; front-load offline analysis.

## Results log

Chronological — successes AND failures.

### 2026-06-17 — v1 revalidation on the new base: PASS
8k +7.5% (N=10, matches the historical +7.3%), 64k positive (low-N),
GSM8K correctness-neutral, serve clean / no wedge. Starting point confirmed;
`8d83cd9d9` pushed to origin. (Recovered from a Mac staging copy after the
RTX worktree copy was lost — uncommitted work nearly went missing; reinforces
commit-before-churn.)

### 2026-06-17 — v2 design (multi-agent) + implementation: validation in progress
**Design** (8-agent analysis + 3 adversarial verifiers, all held): the only
portable difference vs Lucifer is *amortization* — Lucifer is not structurally
cheaper, it just builds the SWA window indices once per step instead of
per-layer. Chosen approach: **widen the existing decode-SWA Triton launch** in
`DeepseekSparseSWAMetadataBuilder.build()` from `grid(num_decode_tokens)` to
`grid(num_tokens)` (the kernel is already keyed by the global token index and
the `decode_swa_*` buffers are already sized `max_num_batched_tokens`), expose
`prefill_swa_indices`/`prefill_swa_lens` views, and have `_forward_prefill`
read them with a per-layer fallback.

**Warmup-safety** (the v2-hang fix): gate the widened launch on
`gate_on AND num_prefill_tokens>0 AND not is_current_stream_capturing()
AND is_valid_token[prefill].any()`. The warmup/profile dummy fills
`slot_mapping` with -1, so `is_valid_token` over the prefill tail is all-False
→ the widened launch is skipped (exactly the OOB that hung the earlier
attempt) → fields are None → `_forward_prefill` self-computes as before.
Adversarially verified: warmup-safe, inert gate-off, bit-identical indices.

**Implementation**: commits `3edda0638` (hoist) + `671008935` (one-shot
`info_once` so the serve log confirms the hoist engaged), pushed to origin.
Pure-Python, source-shadowed onto the built `ee1a079e6` worktree (no rebuild).

Validation (single gate-ON serve, GSM8K limit-100 + prefill 8k/64k at
`--prefill-duration 90` for reliable 64k N) on RTX/SM120.

### 2026-06-17 — v2 SWA→metadata hoist: CORRECT + WARMUP-SAFE, but PERF-NEUTRAL (hypothesis refuted)
| prefill client tok/s | gate-OFF | v1 gate-ON (N=10) | **v2 gate-ON** | v2 N |
|---|---|---|---|---|
| 8k | 9,336 | 10,033 | **10,006** | 89 |
| 64k | 6,516 (N=1) | 8,700 (N=2) | **8,465** | 12 |

- Hoist confirmed engaged (`info_once` fired); serve clean (UP ~70s); **no warmup hang — the warmup-safety guard works** (the prior v2 blocker is solved); no GPU wedge; clean teardown.
- GSM8K limit-100: flexible **0.91** (stable vs OFF 0.92 / v1 0.91), strict **0.87** (OFF 0.91 / v1 0.89; within ~1.3σ — flexible stability + the bit-identical-indices proof → vLLM batch-nondeterminism, not a regression).
- **8k 10,006 ≈ v1 10,033 → the SWA→metadata hoist gives ~0% throughput.** The per-token SWA recompute was NOT the prefill bottleneck (~59 extra cheap launches ≈ <1% of an 820 ms TTFT — never a real lever).

**Verdict: the design premise ("Lucifer is faster only via SWA amortization") is REFUTED.** Our sparse-sm120 *port* (10,006 @ 8k) is still ~19% behind Lucifer's use of the **same** packed kernel (11,978). The gap lives elsewhere — index construction (`compute_global_topk_indices_and_lens` / c128a), the runner invocation, or cache layout — not amortization. v2 is kept as a correct, warmup-safe, perf-neutral refactor (`3edda0638`+`671008935`); decide keep/drop at promotion. The 64k figure is now reliable (N=12): **8,465**.

**Lesson:** code-read design agents identified SWA recompute as redundant (true) but did not *quantify* its cost vs the attention compute (it was always <1%). Next: stop guessing — **profile** the prefill to ground the real bottleneck, and bank the orthogonal FI-CUTLASS MoE win (+7–8%, flag-only).

### 2026-06-17 — prefill-gap attribution (read Lucifer's `flashinfer_sparse.py` + flashinfer-main runner)
Direct source comparison of Lucifer's prefill forward vs ours, and of the
flashinfer-main low-level runner internals:
- **Lucifer also hoists SWA to the metadata** (`flashinfer_sparse.py:640` asserts `prefill_swa_indices`/`prefill_swa_lens`) → our v2 matches its architecture.
- **Index construction is identical**: SWA window + `compute_global_topk_indices_and_lens` (cr4) + `c128a_prefill_topk_indices` (cr128) — same decomposition, same args.
- Lucifer's per-request `PREFILL_CHUNK_SIZE` loop is a **single iteration at C=1** (1 request → 1 chunk), so it is not the lever for the 8k/64k single-stream bench.
- **The ONE real difference: the kernel-driving API.** Lucifer calls the fork's `self._sm120_wrapper.run_sparse_mla(...)`; we call the official `_SparseMLAPagedAttentionRunner.run(...)`. The runner's `mid_out/mid_lse=None` for >64-token prefill is **correct** — prefill routes to the "shared orchestrator" (`_sparse_mla_sm120.py:31-33`), not the decode split-K scratch path (`_decode_scratch_views` is decode-only, line 262), so there is **no fresh-alloc bug** for prefill. The prefill branch calls the C++ `sparse_mla_sm120_paged_attention` directly with no Python-level tiling/autotune.

**Conclusion: the vLLM side is at parity with Lucifer; the residual ~19% (our port 10,006 @ 8k vs Lucifer 11,978) is in the FlashInfer prefill *kernel*** — the official `sparse_mla_sm120_paged_attention` orchestrator vs the fork's hand-tuned `run_sparse_mla` prefill kernel (dropped from flashinfer-main). This is a flashinfer-level gap, not closable by vLLM index/scheduling changes.

**Open vLLM-side lever to test:** the fork's `run_sparse_mla` autotunes (`sparse_mla_sm120_*_autotune`); our official-runner prefill path does **not** autotune. Wrapping the prefill `runner.run` in `flashinfer.autotuner.autotune(tune_mode=True)` (or a prefill-shaped warmup autotune pass) may recover part of the gap entirely within the official stack. The decode autotune attempt added 0% (decode), but prefill shapes differ — worth one gated experiment. Definitive confirmation = profiling the kernel time (our orchestrator vs the fork kernel) on the same 8k prefill.

**Realistic banked parity gains (official flashinfer):** v1 port +7% (8k) + FI-CUTLASS MoE +7–8% (orthogonal) ≈ +14–15% over the FlashMLA default; full Lucifer parity (+27%) additionally needs the kernel-level gap closed (autotune experiment, else flashinfer upstream).

### 2026-06-17 — v3 FI-CUTLASS MoE bundle + latest-FI-main check + autotune feasibility
**MoE bundle** (gate-ON decode+prefill + `--moe-backend flashinfer_cutlass`), N=89/12:
| prefill client tok/s | gate-OFF | gate-ON (v2) | **gate-ON + MoE (v3)** |
|---|---|---|---|
| 8k | 9,336 | 10,006 | **10,543** (+5.4% over v2) |
| 64k | 6,516 (N=1) | 8,465 | **8,753** (+3.4% over v2) |
Combined port+MoE vs FlashMLA default: **8k +12.9%**. ⚠️ GSM8K limit-100 0.87/0.84 (vs OFF 0.92/0.91) — yellow flag; re-verifying at limit-300 before banking MoE.

**Latest FlashInfer main check (user-suggested):** fetched `flashinfer-ai/flashinfer` origin/main (4 commits ahead of our ~06-14 build). `flashinfer/mla/_sparse_mla_sm120.py` is **byte-identical to our build** → our build already has the latest prefill orchestrator. The 4 new commits are #3615 (SM120/121 topk-hang *stability* fix — worth adopting later), #3417 rmsnorm, #3504 MXFP8 MoE, #3646 FP4 gemm — **none touch the sparse-MLA prefill attention kernel**. Web: SM120 sparse-MLA prefill is a recognized upstream gap (SGLang routes to an unsupported TllmGen path); our PR#41834 is cited as the closest existing SM12x kernel work. So **no newer prefill kernel exists to pull.**

**Autotune feasibility:** the FlashInfer sparse-MLA AutoTuner is **decode-only** (`_sparse_mla_sm120.py:728-993` tunes `chunks_per_block` for decode; the prefill orchestrator registers **no tactics**). So there is no Python/autotune lever for prefill.

## Phase conclusion (prefill)
- **vLLM side: at parity with Lucifer** (identical index construction + SWA hoist; per-request chunking is a no-op at C=1).
- **Banked (official flashinfer): ~+12.9% @ 8k** over the FlashMLA default = v1 packed-prefill port (+7%) + FI-CUTLASS MoE (+5.4%) [MoE pending GSM8K limit-300].
- **Residual ~12% to Lucifer's 11,978 is the FlashInfer prefill *orchestrator kernel*** — not improved in latest main, not autotunable, not closable from vLLM. **Full parity/surpass requires a flashinfer prefill-kernel contribution** (upstream a faster sparse-MLA SM120 prefill kernel, analogous to how PR3395 upstreamed the decode kernel that gave us the decode win).

### 2026-06-17 — b12x lead investigated (user-suggested) → dead end for MXFP4 prefill
b12x (`lukealonso/b12x` v0.20.0) is a full Blackwell SM12x stack (MLA decode + **extend/prefill** + indexer + MoE + GEMM + MHC + W_O), installed in the serve venv; vLLM has hooks (`VLLM_USE_B12X_*`, `DeepseekV4B12xMLASparseBackend`) — but only on a **May-1 experimental branch** (`backup/ds4-sm120-experimental-b12x`), not the current line. Findings:
- **The b12x reachable *via FlashInfer* (`--moe-backend flashinfer_b12x`, `--linear-backend flashinfer_b12x`) is NVFP4-only** (registered under `NvFp4MoeBackend`; W4A16-NVFP4 checkpoints). Our served model is **MXFP4** → not applicable. The NVFP4 variant is itself −8% on SM120 ([[project_nvfp4_sm12x_blocked]]).
- **The b12x MLA route (`B12X_MLA_SPARSE`) was already measured SLOWER** than our baseline by prior harness work (16K C=1 ~5,407 input tok/s; "public b12x compressed MLA loses to current D512"; decision: "do not port the black-benediction endpoint stack") — see `docs/sm120/experiments/2026-06-13-black-benediction-rtx-public-stack/` + `decisions/watchlist/2026-06-12-backend-parity-roadmap.md`.
- **Lucifer's fast prefill (11,978) is the `FLASHINFER_MLA_SPARSE` route (fork flashinfer's `run_sparse_mla`), NOT b12x.** The b12x route is the *slow* one.

So b12x is not the lever for MXFP4 prefill. And the prefill **kernel source is identical** between upstream/main and Lucifer's branch (git diff empty), with Lucifer's 11,978 measured on **forced-MARLIN MoE** (same MoE as ours) — so the residual ~19% (our 10,006 vs 11,978) is **neither the kernel source, nor the MoE, nor b12x**. It is the fork-flashinfer *build/invocation* (fork 0.6.12 `run_sparse_mla` wrapper vs official-main 0.6.13 `_SparseMLAPagedAttentionRunner.run`, per-layer ×60). **Only a profile can localize it** (per-call/dispatch/build overhead) — the next definitive step, deeper than code-reading.

### 2026-06-17 — v3b correctness re-verify (limit-300) + RTX wedge
**GSM8K limit-300, gate-ON (packed decode+prefill) + FI-CUTLASS MoE: flexible 0.8967 / strict 0.8600** (σ≈0.018). This is a **real ~5–7 pt drop** vs the decode-only baseline (0.9533/0.9267) — not limit-100 noise. FI-CUTLASS MoE with *FlashMLA* prefill was clean in the prior 2×2 (0.96/0.94), so the regression points at the **gate-ON packed-prefill path** (the +7% prefill may cost a little accuracy). ⚠️ Attribution (packed-prefill alone vs +MoE, at limit-300) is unfinished — needs another serve.
**RTX GPU0 wedged a 2nd time today** (`Unknown Error`, GPU1 stuck 100%/P0) during v3b's prefill re-measure (that lmbench row is garbage). All RTX GPU work halted; needs a physical power-cycle. Reinforces: minimize sustained-serve churn on this box.

## Net state (end of session segment)
- **Banked, deployable (official FI, MXFP4):** packed-prefill port +7% @ 8k; FI-CUTLASS MoE +5.4% → combined **~+12.9% @ 8k** over the FlashMLA default. v2 SWA→metadata hoist = correct/warmup-safe/neutral (kept).
- **Correctness attribution (v2c, limit-300, post-reboot, no wedge):** gate-ON packed prefill + **MARLIN** MoE = **0.913 / 0.897**. So the GSM8K drop splits: the **packed-prefill path** costs ~−0.04/−0.03 vs the decode-only/FlashMLA baseline (0.953/0.927; flexible ≈2.4σ, consistent with v1's limit-30 0.933/0.900 → real, small), and **FI-CUTLASS MoE adds a further −0.016/−0.037** (v3b 0.897/0.860). Both are **gated OFF by default**, so the default PR path stays clean (decode port 0.953/0.927); the prefill port + MoE ship as **opt-in** perf features with a documented small-accuracy tradeoff. Open question: is the packed-prefill cost a fixable index/fp8 bug (decode port is clean, so prefill-specific) or inherent — needs a numerical compare vs FlashMLA prefill.

### 2026-06-17 — ROOT-CAUSED: multi-request prefill batching bug (FIXABLE, not precision)
Isolation by `num_concurrent` (gate-ON packed prefill, MARLIN, GSM8K-300):
| | flexible | strict |
|---|---|---|
| **num_concurrent=1** (single-request prefills) | **0.9567** | **0.9367** |
| num_concurrent=8 (multi-request prefill batches) | 0.913 | 0.897 |
| baseline (FlashMLA prefill) | 0.953 | 0.927 |

**At nc=1 the packed prefill is CLEAN (0.957/0.937, ≥ baseline) — so the kernel + indices + fp8 are correct for single-request.** The drop appears only under multi-request batching. Our `_forward_prefill` drives `_SparseMLAPagedAttentionRunner.run` **once over the whole multi-request prefill batch**, whereas **both** the accurate baselines chunk per-request: FlashMLA via `get_prefill_chunk_plan` (flashmla.py:927), Lucifer via `PREFILL_CHUNK_SIZE` (flashinfer_sparse.py:657). The packed runner mis-handles a multi-request batch in one call (no per-request segmentation passed; the kernel takes only per-token q+indices). **FIX = wrap the runner call in a per-request chunk loop** (slice q / swa_indices / swa_lens / topk_indices / topk_lens / output by `query_start:query_end`, per-chunk mid_out/mid_lse). After the fix the prefill port should be **clean (~0.95/0.93) AND +7%** — a promotable win. (The C=1 prefill bench is one chunk, so no perf change there.)

### 2026-06-17 — chunk-to-4 fix REFUTED; re-isolating (chunk=1 test)
Implemented the per-request chunk loop (`PREFILL_CHUNK_SIZE=4`, commit `02f235bd6`) and re-ran nc=8 GSM8K-300: **0.8867/0.8733 — still broken** (≈ the unfixed 0.913/0.897, not the clean nc=1 0.957/0.937). So chunking prefill into 4-request groups does NOT fix it → the cause is **not** "whole-batch vs chunked." Remaining candidates: **(a)** strictly 1 request per runner call (chunk-to-4 still has up to 4/call) — testing chunk=1 now; **(b)** mixed decode+prefill batches (nc=8 interleaves decode tokens with prefill in a step, `num_decodes>0`; nc=1 prefill steps are pure `num_decodes=0`) — a `num_decodes>0` offset/slicing bug in `_forward_prefill` would break (b) and chunking wouldn't help. Decisive test in flight: chunk-size=1 at nc=8. If clean → (a), commit chunk=1; if still broken → (b)/deeper, revert `02f235bd6` and audit the mixed-batch prefill path. **Lesson: I jumped to a fix before fully isolating — chunk-to-4 was a guess; should have isolated requests-per-call vs mixed-batch first.**

### 2026-06-17 — control settles it; packed-prefill route FAILED (concurrency correctness)
chunk=1 nc=8 = 0.9033/0.8733 (still broken → not requests-per-call). The missing **control** (should have run first): FlashMLA prefill (PREFILL=0), MARLIN, **nc=8** GSM8K-300 = **0.95/0.92 — CLEAN**.

| GSM8K-300, MARLIN | nc=1 | nc=8 |
|---|---|---|
| FlashMLA prefill (baseline) | — | **0.95 / 0.92** ✓ |
| packed prefill (port), whole-batch | 0.957/0.937 ✓ | 0.913/0.897 ✗ |
| packed prefill, chunk=4 / chunk=1 | — | 0.887/0.873 · 0.903/0.873 ✗ |

So FlashMLA handles nc=8 correctly; **the packed prefill has a real concurrency correctness bug** (~5 pt below FlashMLA at nc=8), correct only single-stream (nc=1). Chunking the prefill (whole / 4 / 1 requests-per-call) does NOT fix it → the bug is in concurrent/mixed-batch handling (likely `num_decodes>0` mixed decode+prefill steps), not pinpointed. **DECISION (per user criterion: no concurrent shape passes + no confident lead → declare failed): the FlashInfer SM120 packed-prefill port is SHELVED.** It is correct only at concurrency=1, which is not production-viable, and the +7% single-stream gain is moot under real serving. The refuted chunk commit (`02f235bd6`) is reverted on the dev branch. **The decode port remains the clean, shipped win; the default FlashMLA/Triton prefill is the correct path.**

Untried-but-low-confidence lead (deferred): a numerical capture/compare of packed vs FlashMLA prefill output on a mixed (`num_decodes>0`) batch to pinpoint the bug — expensive, wedge-risky, uncertain payoff.
- **b12x: dead end for MXFP4** (NVFP4-only via FlashInfer; b12x-MLA route already slower; not Lucifer's fast path).
- **Full Lucifer parity** needs the fork-flashinfer build/kernel difference localized by profiling (not b12x, not a backend flag, not MXFP4-accessible). Bounded at ~+13% on the official stack until then.

### 2026-06-18 — RE-MEASURED on rebased base + ROOT CAUSE CORRECTED (gap IS vLLM-closable)
> ⚠️ **SUPERSEDED 2026-06-18 (LATER) — see the next entry.** This entry's "gap IS vLLM-closable / merged-single-pool lever / port Lucifer `d11b5a708bc`" conclusion was built on a **wrong-file comparison** and is retracted. The `FlashInferMLASparseSM120Impl` analyzed below is the DeepSeek-V3.2/DSA backend (decode-only), **not** Lucifer's DSv4-Flash path. Lucifer's actual DSv4 path is two-pool, identical to ours. Read the next entry for the corrected, source-verified conclusion.

**Prior "residual is a flashinfer-kernel gap, not vLLM-closable" conclusion is REFUTED.** Re-ran a clean same-day A/B with **both vLLMs on the SAME shared venv flashinfer 0.6.12** (`flashinfer-pr3395-b41aa8d`), same `llm_decode_bench --prefill-only`, matched config (TP2, fp8 KV, block-size 256, MTP2, async-sched, chunked-prefill, cudagraph FULL_AND_PIECEWISE, max-len 131072):

| prefill client tok/s | CUR = rebased vLLM default (indexed-D512) | LUC = Lucifer `--attention-backend FLASHINFER_MLA_SPARSE` | gap |
|---|---|---|---|
| 8k  | 9,576  | 12,444 | **+30%** |
| 64k | 8,193  | 11,637 | **+42%** |

Since the flashinfer kernel is **identical** (same install), the gap is purely **vLLM-side**.

**Root cause (corrected):** our `FlashInferMLASparseBackend.supports_compute_capability` returns `major==10` → it's **SM100 (B100/B200) + DeepSeek-V3.2 only** (TRTLLM-gen `trtllm_batch_decode_with_kv_cache_mla`); on **SM120 (major 12) it is rejected**, so our DSv4 falls to the FlashMLA/indexed-D512 or the packed-port path. **Lucifer ADDED the missing SM120 impl** (`flashinfer_mla_sparse_sm120.py`, `FlashInferMLASparseSM120Impl`): one `BatchMLAPagedAttentionWrapper(backend="sparse-sm120").run_sparse_mla()` over a **single unified `sparse_indices`** (the indexer `topk_indices_buffer` → global slots, no `extra_*` pool). `run_sparse_mla` is a thin wrapper over the **same** `_SparseMLAPagedAttentionRunner.run` our packed-port calls — but Lucifer passes **one merged pool** vs our **two pools** (separate SWA-window cache + compressed cr4/cr128 cache).

**This unified single-pool IS the architecturally-correct DSv4 attention** (confirmed vs the DeepSeek reference `inference/model.py:Attention.forward`): the reference does `topk_idxs = cat([get_window_topk_idxs(...), compress_topk_idxs])` then **one** `sparse_attn(q, kv, sink, topk_idxs, scale)`. Lucifer mirrors this (merged index, one call); our two-pool is a numerically-equivalent-but-slower decomposition forced by our **two-cache KV layout** (Lucifer uses one unified `fp8_ds_mla` cache; our serve `--kv-cache-dtype fp8` + separate `swa_cache`/`extra_cache`). A minimal "merge indices + single run() call" prototype is **blocked** by the two-cache layout → needs the unified-KV handling.

**THE LEVER / port surface = Lucifer commit `d11b5a708bc` "feat(dsv4): add Lucifer SM120 sparse MLA support"** (32-file squash, mostly unrelated MoE/MXFP4/deepgemm; sparse-SM120-prefill-relevant ≈8 files): `vllm/v1/attention/backends/mla/flashinfer_mla_sparse_sm120.py` (+187 impl), `.../flashinfer_mla_sparse.py` (+307 dispatch+metadata), `vllm/utils/flashinfer.py` (+20 `has_flashinfer_sparse_mla_sm120`), `vllm/platforms/cuda.py` (+68 SM120 selection), `vllm/v1/attention/backend.py` (+24), **`.../sparse_swa.py` (+189 merged-index pipeline)**, `vllm/models/deepseek_v4/attention.py`, `vllm/model_executor/warmup/flashinfer_sparse_mla_warmup.py` (+512 warmup). Deps already in our tree: `SparseMLAAttentionImpl` ✓, `triton_convert_req_index_to_global_index` ✓, `current_workspace_manager` ✓; missing only `has_flashinfer_sparse_mla_sm120`. Lucifer's impl copied to `/tmp/lucifer_analysis/lucifer_backend.py`; Lucifer worktree `/home/jasl/tmp/vllm-local-inference-lucifer-20260614@7c6bbf4c`.

**ASSESSMENT:** substantial port (~1000+ relevant lines onto a diverged base; merged-index pipeline + unified-KV + warmup + correctness risk — dropping/merging the SWA window must preserve GSM8K). Lucifer's own FLASHINFER_MLA_SPARSE GSM8K was **never measured** (all prior GSM8K = our portdev/baseline) → must validate Lucifer-correctness before/while porting. **Plan:** (1) GSM8K on the Lucifer serve to confirm the unified path is accuracy-equivalent on DSv4-Flash; (2) port the ~8 files into an ISOLATED worktree (NOT the PR branch); (3) validate GSM8K + #19/arthur regression gates + the prefill A/B; (4) promote env/backend-gated if clean. Decode port (shipped) stays the default win; this is an opt-in prefill perf path.

### 2026-06-18 (LATER) — DEFINITIVELY CLOSED: gap is a flashinfer-KERNEL gap, NOT vLLM-closable (the entry above is a wrong-file artifact)

Source-verified by a 6-agent port-surface analysis workflow (each dimension cross-checked against Lucifer's actual files on the box) **plus** direct reads of Lucifer's `vllm/models/deepseek_v4/nvidia/flashinfer_sparse.py`. The "+30% vLLM-side merged-pool lever" thesis is **refuted**:

1. **The merged-single-pool file is a decoy.** `FlashInferMLASparseSM120Impl` (one `topk_indices_buffer`, no `extra_*`) is Lucifer's **DeepSeek-V3.2 / DSA** backend — gated `index_topk==2048, compress_ratio==1`, **decode-only** (raises on non-decoder, no prefill). It is **not** the DeepSeek-V4-Flash C4A path.
2. **Lucifer's actual DSv4 SM120 attention is two-pool — identical to ours.** `_select_dsv4_attn_cls` (`model.py:729`) maps `major==12` → `DeepseekV4FlashInferSM120Attention` (`flashinfer_sparse.py`), whose `_forward_sm120_prefill`/`_forward_sm120_decode` (`:696` / `:566`) call `run_sparse_mla(sparse_indices=swa_indices, …, extra_kv_cache=extra_cache, extra_sparse_indices=…, extra_sparse_lengths=…)` — the **same swa + compressed two-pool, two-cache structure** our shipped `_sm120_runner.run` uses (only kwarg names differ; same shared `compute_global_topk_indices_and_lens` op).
3. **Indexer + `topk_indices_buffer` are byte-identical** between our tree and Lucifer (`deepseek_v2.py` md5 `96f94af5…`); compressed-only in both. **Both sides allocate two cache layers** (`swa_cache_layer.kv_cache` + compressed `kv_cache`) + the indexer pool. **Nothing to merge, no KV layout to collapse, no allocation change.**
4. **We already ship Lucifer's DSv4 prefill structure** as our env-gated `_forward_prefill` (`VLLM_DEEPSEEK_V4_FLASHINFER_SM120_PREFILL`). Re-tested twice (see the retest entries above): correct (nc=8 0.96) but **perf-neutral** (flat ±1% at 8k/16k/32k) — the rebased base's default indexed-D512 + upstream #45061 adaptive chunk planning already match it.
5. **`PREFILL_CHUNK_SIZE = 4`** (`deepseek_v4/attention.py:119`); Lucifer chunks prefill into 4-request groups. **But at C=1 — the single-stream prefill bench regime where the +30% was measured — chunking is a no-op** (1 request = `ceil(1/4)` = 1 chunk), so it cannot explain the single-stream gap.

**Why the "+30% on the same flashinfer" A/B was misleading:** CUR (our default, *official* flashinfer 0.6.12) ran the **indexed-D512** prefill kernel (the official packed `_sparse_mla_sm120` runner isn't in 0.6.12); LUC (Lucifer, the **fork** lucifer1004/flashinfer 0.6.12) ran the fork's **hand-tuned `run_sparse_mla` sparse-sm120 prefill kernel**. "Same flashinfer" is false — fork ≠ official. So it *was* a kernel/build gap. At C=1 our packed port (official orchestrator `sparse_mla_sm120_paged_attention`) ≈ our indexed-D512 default; the fork's hand-tuned prefill kernel beats both. **That fork kernel was dropped from flashinfer-main** (`run_sparse_mla` / `BatchMLAPagedAttentionWrapper(backend="sparse-sm120")` gone), so it can't be pulled onto the official stack.

**CONCLUSION:** Lucifer-parity **prefill is not vLLM-side-closable** on our base. The residual ~+30% lives in the fork's flashinfer sparse-MLA SM120 prefill **kernel**. The only path to parity is an **upstream flashinfer prefill-kernel contribution** — exactly how the shipped decode win arrived (PR3395 upstreamed the decode kernel). This restores the original 2026-06-17 "flashinfer-kernel gap" framing; the (now-superseded) 2026-06-18 "vLLM-closable" entry was the error. **Decode port (shipped) remains the win; default indexed-D512 prefill is correct.** The Lucifer-correctness go/no-go is moot (source answers it) and un-runnable (wedged RTX GPU0 3× — see `feedback_gb10_freeze_risk` / the RTX-Lucifer-wedge note).

### 2026-06-18 (LATER) — FlashInfer upstream/main scan: no new sparse-MLA SM120 prefill capability

Fetched `flashinfer-ai/flashinfer` origin/main (HEAD `9c5ed7c`, 2026-06-17) vs our installed base. New commits since ~06-14 that touch attention:
- **#3479** "sm120 delta rule dsl prefill" → `flashinfer/gdn_kernels/delta_rule_dsl/` — **Gated-Delta-Net (linear attention)** prefill, a different mechanism (Qwen-Next-style); not DeepSeek sparse-MLA.
- **#3640** "SM120 NVFP4 attention JIT" → new `nvfp4_attention_sm120` dense kernel — **NVFP4** (≠ our MXFP4; NVFP4 is −8% on SM120 here); not sparse-MLA.
- **#3615** "fix(topk): eliminate multi-CTA radix top-k stream hangs on SM120/SM121" — a stability fix worth adopting later (affects the indexer top-k); not a perf lever.
- MoE/GEMM ride-alongs (#3562 MXFP8 MoE, #3504 MXFP8 SwiGLU, #3646 b12x FP4) — orthogonal.

**The sparse-MLA SM120 kernel is byte-unchanged on main** (`flashinfer/mla/_sparse_mla_sm120.py` + `csrc/sparse_mla_sm120_prefill.cu` no diff since our base) → no new DSv4 prefill capability; the fork's hand-tuned prefill kernel is still not upstreamed. Cross-check: SGLang hits the identical wall (sglang#24633 — SM120 MLA prefill routes to the unsupported TllmGen path). **Signal to watch:** flashinfer IS actively adding SM120 attention kernels (delta-rule, NVFP4) → a sparse-MLA SM120 prefill improvement could plausibly land later. **Watch:** new commits to `flashinfer/mla/_sparse_mla_sm120.py` / `csrc/sparse_mla_sm120_prefill.cu` on flashinfer main, and any PR titled "sparse mla … sm120 … prefill". If one lands, re-run the prefill A/B (our env-gated packed path already wired to drive it).
