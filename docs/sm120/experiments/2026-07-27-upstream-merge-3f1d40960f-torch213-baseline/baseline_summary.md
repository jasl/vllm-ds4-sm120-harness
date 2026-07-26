# GB10 2×SM121 DeepSeek-V4-Flash baseline — `88385a131c` (2026-07-27, torch 2.13)

Merge of upstream/main `3f1d40960f` (209 commits) onto `48d2749542`. Supersedes
`2026-07-21-upstream-merge-fbfe58133d-baseline`. **Runtime-generation change: upstream
moved to PyTorch 2.13.0 / Triton 3.7.1 (#48155) and FlashInfer 0.6.15.post1.**

Motivating trigger: upstream merged **PR #49052** (2026-07-26), the upstream fix for
issue #48959 — so our fork-local #48959 fix is retired in favour of upstream's.

## Build / environment
| | |
|---|---|
| vLLM head | `88385a131c` (merge of `48d2749542` + upstream `3f1d40960f`) |
| merge | 209 upstream commits; 13 conflicts hand-resolved, 0 fork features dropped, 0 behind |
| torch | **2.13.0** (was 2.11.0) · triton **3.7.1** (was 3.6.0) |
| flashinfer | **0.6.15.post1** python+cubin matched (was 0.6.14) |
| nvidia-nccl-cu13 | **2.30.7 held** (torch 2.13 wanted to downgrade to 2.29.7 — overridden) |
| nvidia-cutlass-dsl | 4.6.0 · quack-kernels 0.6.1 (upstream floor now `>=0.6.1`) |
| qutlass | `e74319e` (upstream #47879 bumped from `830d2c4` for stable-ABI/torch-2.13) |
| serve | boot 503s; **GPU KV cache 160,677 tokens** (was 179,225 → −10%) |

## What this merge changed for us
- **#48959 fork delta RETIRED.** Upstream #49052 landed (its commit carries
  `Co-authored-by: jasl` / `Claude Opus 4.8` — our analysis was folded into it). We dropped
  `max_pending_gpu_blocks_for_group`, the config field, the build site and 2 tests, and took
  upstream's one-line `+ 1` bound. `offloading/scheduler.py` is now **byte-identical to
  upstream** (delta = 0). Note upstream's naive `+1` also loosens the Mamba single-state
  bound; verified harmless (the assert is a pure sanity guard, not control flow) and we run
  no Mamba.
- **13 conflicts**, notably: `record_stats` kwarg removed upstream (refactored into
  `prefix_cache_lookup_enabled()` / `record_prefix_cache_stats()`) — our fork test
  `test_prefix_cache_peek_does_not_record_stats` passed that kwarg and was adapted to the new
  API, preserving its invariant. `dspark.py` (3 hunks) resolved to **ours**: our fork and
  upstream carry largely *different implementations* of DSpark (`DeepSeekV4DSpark` vs
  `DSparkDeepseekV4ForCausalLM`); upstream's #49415 shared-expert padding fix targets TP>8 and
  patches code our loader does not have, so it was deliberately not adopted.

## Correctness (all GREEN)
- **GSM8K** (full 1319q, 8-shot): **0.9568** strict/flexible — top of the historical band.
- **Coherence** (arthur ~28k): **c=1 2/2 PASS** (deterministic recall discriminator);
  c=12 23/24 (known 22–24 band).
- **#19 instruction-following**: PASS.
- **Tool-calling** (135 cases × **3 runs**): **82% / 87% / 89%**, mean **86%** — identical to
  the torch-2.11 baseline's 86%. 0 engine errors in every run. See the noise note below.
- **Unit**: core 232 passed + 1 environmental (needs 2 GPUs/node); offload + kv_offload
  **791 passed**; DSv4 fork (sparse-SWA, ubatch, indexer slot-mapping) 5 passed.

## ★ Measurement-resolution findings (both bit us this session)
- **toolcall-15 single-run resolution is ~±6pp, not ±2.6pp.** Identical build/config gave
  **82% → 87% → 89%** across three runs (mean 86%, exactly the torch-2.11 figure);
  `think-high` failures swung 10 → 2 between the first two. The 82% was a single-run
  outlier, NOT a regression. Failure *reasons* were identical across torch versions
  (multi-turn chaining, unnecessary tool use, error-handling style) with zero mechanical
  failures (no malformed tool_call JSON, no parser errors, no 500s) — the signature of
  sampling variance, not a functional break. **Never draw a toolcall conclusion from one run.**
- **tg128 per-run spread within one build is 9–12%** (wider than the ±8% previously assumed).
  Use a **range-overlap test across runs**, not mean deltas, to call a decode change real.

## Perf — llama-benchy STANDARD (pinned `@b220b7c9`, C=1, 3 runs each; **3 full passes**)
3-run means vs the torch-2.11 baseline (`832775efd1`):

| depth | ctx_pp | vs base | pp2048 | vs base | tg128 | vs base |
|---|---|---|---|---|---|---|
| 8192  | 1836.5 | +0.3% | 1381.8 | −1.1% | 38.4 | −1.6% |
| 16384 | 1799.8 | −0.0% | 1325.3 | +0.9% | 36.1 | **−14.3%** |
| 32768 | 1711.7 | −0.6% | 1197.2 | −0.9% | 40.1 | +11.0% |

**Prefill: flat.** ctx_pp and pp2048 are within ±1.1% at every depth, with tight σ.
**This settles the long-open question: torch 2.13 delivers NO prefill gain on vLLM/GB10.**
The >10% seen on tokenspeed does not transfer, and even the previously-hoped prefill +3–7%
does not appear. The upgrade is mandatory (upstream requires it), not a perf win.

**Decode: no regression — within the historical range.** The d16384 −14.3% against the
07-21 baseline is an artifact of comparing to a single anomalous prior reading.

d16384 `tg128` across every recorded baseline:

| baseline | d16384 tg128 |
|---|---|
| 07-11 torch213-stable-cut | 37.3 |
| 07-11 `5e43b2cfa7` | 39.6 |
| 07-17 `3b6c96a101` | 37.1 |
| **07-21 `fbfe58133d`** | **42.1** ← outlier |
| **07-27 this (torch 2.13)** | **36.1** |

Four of five baselines cluster at **36.1–39.6**; 07-21's 42.1 is the outlier (it was itself
recorded as "+13.4% vs 07-17, within noise"). This build's 36.1 is in line with 07-17 (37.1)
and the earlier torch-2.13 stable cut (37.3). **No decode regression.**

### ★ Method error this exposed — asymmetric skepticism
The 07-21 baseline's d16384 `tg128` came in **+13.4%** above 07-17 and was accepted as noise
*because it was favourable*. The return to the historical mean was then investigated as a
"−14.3% regression" *because it was unfavourable*. The range-overlap test was the right tool
but was applied against **one** (anomalous) prior baseline instead of the historical
distribution. **Always compare a noisy metric against the full baseline history, not the
single previous run — and apply the same scepticism to favourable moves as to unfavourable
ones.**

### Hypotheses tested and refuted along the way
- **MTP acceptance**: ruled out — now **76–84% draft acceptance**, *higher* than the recorded
  67–75%, so not the accept-length effect of `project_cutlass_mxfp8_moe_ab_sm121`.
- **JIT-during-inference**: refuted. The `jit_monitor` warnings (11 kernels, incl.
  `_fp8_paged_mqa_logits_rowwise_kernel`) came from the **gate-battery serve on a cold Triton
  cache** right after the 3.6 → 3.7.1 upgrade. All three benchy runs show **zero**
  JIT-during-inference warnings (Triton disk cache warm at 1.7 GB), so JIT does not touch the
  benchmark numbers. Worth noting separately: `_fp8_paged_mqa_logits_rowwise_kernel`,
  `_fp8_mqa_logits_kernel`, `_tf32_hc_prenorm_gemm_kernel` and
  `_compute_global_topk_indices_and_lens_kernel` have **no warmup registration**, so a
  cold-cache serve does pay first-use JIT latency spikes — a real (if minor) startup-quality
  item, now visible thanks to upstream's new monitor.

## Also changed
- **KV cache 179,225 → 160,677 tokens (−10%)** at the same util 0.85. Affects only
  high-concurrency long-context headroom, not the C=1 benchmarks above; tunable via
  `--gpu-memory-utilization`.

## Warmup added — SM12x paged-MQA rowwise decode logits (`70a33886bd`)
The decode warmup dummies run with `seq_lens == max_query_len` (3 under MTP2), so
`DeepseekV4Indexer.forward` short-circuits on `max_seq_len // compress_ratio <= topk_tokens`
and never reaches the paged-MQA path — `_fp8_paged_mqa_logits_rowwise_kernel` therefore
JIT-compiled inside the first request whose context exceeded `compress_ratio * index_topk`.
Now pre-compiled (6 reachable variants).

**Verified against ground truth**, not assumed: Triton cache cleared on both nodes → cold
serve → `jit_monitor` no longer reports the kernel.

★ **The load-bearing design choice**: strides are read off the **bound** `kv_cache` tensor,
not a synthetic one. The design analysis predicted `page_stride = 8640`; the real value is
**1,002,240**. A synthetic tensor built from the predicted stride would have compiled a
*different* cubin — warmup would look successful while the real kernel still JIT'd. Same trap
`_deepseek_v4_indexed_d512_split_prefill_warmup` documents.

**Deliberately not warmed** (recorded so the gap is explicit, not silent):
`_tf32_hc_prenorm_gemm_kernel` (~68 variants, SM-count-derived `NUM_SPLIT`) — warming it on
every boot costs minutes for a cold-cache-only benefit; `_compute_global_topk_indices_and_lens_kernel`
(6) — its warmup needs pointer-alignment-class construction resting on *assumed* Triton
specialization internals, which could silently warm the wrong variant or throw at startup.
Both still appear in `jit_monitor` on a cold cache.

## ★ Build notes — torch 2.13 upgrade took 4 attempts
1. `--no-build-isolation` compiles against the *installed* torch → must install torch 2.13
   **before** building (two-step), else cmake fails in ~70s against 2.11 headers.
2. `FAILED: [code=137]` = **OOM-killed `cicc`** — a stale serve held 112/121GB **and**
   `MAX_JOBS=10` is too high for GB10 unified memory. Kill stale serves; use `MAX_JOBS=4`.
3. FlashInfer python bumped to 0.6.15.post1 but **cubin stayed 0.6.14** → `flashinfer.mla`
   refused to import. Install the matched pair (uninstall jit-cache first).
4. **Stale `.deps/qutlass-src` at `830d2c4`** while upstream #47879 moved the pin to
   `e74319e` *precisely because* the old source "uses legacy ATen headers and cannot be built
   with TORCH_TARGET_VERSION". Delete `.deps/qutlass-*` to force re-fetch.

★ Items 3 and 4 are the **3rd and 4th instance this session** of the same trap: an upstream
pin moved, but a locally cached dependency did not, so new contracts compile against old
code (previously: quack 0.5.0, nccl). **After any upstream dep bump, clear the matching
local cache.**

## Reproduce
```bash
VLLM_ROOT=/home/jasl/tmp/vllm-merge-20260711 \
VLLM_VENV=/home/jasl/tmp/ds4-sm120-harness/vllm/.venv \
  scripts/run_gb10_llama_benchy_standard.sh
```
