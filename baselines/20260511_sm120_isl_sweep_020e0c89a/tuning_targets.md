# SM120 Decode Tuning Targets — 2026-05-12

Goal: **single-stream no-MTP decode ≥ 120 tok/s** on SM120 TP=2 EP, up from
**86 tok/s** (mt-bench c=1, TPOT 11.60 ms) at vLLM `eeb57e2f2`.

To hit 120 tok/s we need TPOT ≤ 8.33 ms — a **28% reduction**. The torch
profiler snapshot (`performance/profile/sm120_nomtp_decode_64tok/`) of a
fully-warm 64-token decode window tells us where the time goes; the MTP
acceptance trace (`performance/mtp_acceptance/sm120_mtp2.md`) tells us
whether changing `num_speculative_tokens` could help (it likely cannot for
this target).

## Baseline kernel-time breakdown (SM120 nomtp, TP=2, single stream)

Capture: 0.87 s wall, 64 generated tokens, 1872 ms aggregate kernel time
across 3 trace files (2 TP workers + API server). Top consumers:

| rank | time % | kernel | category |
|---|---|---|---|
| 1 | 23.33 | `_w8a8_triton_block_scaled_mm` | MoE FP8 block GEMM |
| 2 | 12.89 | `marlin_moe_wna16::Marlin<...>` | MoE WNA16 Marlin |
| 3 | 11.91 | `_fp8_paged_mqa_logits_kernel` | Sparse-MLA indexer |
| 4 | 5.89 | `vllm::cross_device_reduce_1stage<bf16, 2>` | TP all-reduce |
| 5 | 4.93 | `_finish_materialized_scores_with_sink_candidate_block_kernel` | Our SM12x sparse-MLA finish |
| 6 | 4.48 | `_deepseek_v4_sm12x_fp8_einsum_kernel` | Our SM12x FP8 einsum |
| 7 | 3.99 | `internal::gemvx::kernel<bf16,...,7,...>` | cuBLAS bf16 gemvx (attn proj) |
| 8 | 2.93 | `at::native::unrolled_elementwise_kernel<direct_copy_kernel_cuda>` | Copy/cast |
| 9 | 2.88 | `internal::gemvx::kernel<bf16,...,8,...>` | cuBLAS bf16 gemvx |
| 10 | 2.60 | `per_token_group_quant_8bit_kernel<BF16→FP8_e4m3>` | FP8 input quant |
| 11 | 2.25 | `mhc_pre_big_fuse_tilelang_kernel` | mHC pre |
| 12 | 2.23 | `internal::gemvx::kernel<bf16,...>` | cuBLAS bf16 gemvx |
| 13 | 1.84 | `mhc_fused_tilelang_kernel` | mHC fused |

(Full top-30 in `performance/profile/sm120_nomtp_decode_64tok/torch_kernel_summary.md`)

**Rolled-up categories**:
- MoE compute (FP8 GEMM + Marlin WNA16): **36.2%**
- Sparse MLA + attention finish/einsum (idx logits + finish + einsum + mhc): **24.3%**
- TP all-reduce: **5.9%**
- Attention/projection cuBLAS gemvx (#7, #9, #12 combined): **9.1%**
- Elementwise + quant overhead (#8, #10, #14 etc.): **~9%**
- Everything else: **~15%**

## What MTP=2 tells us about the model's headroom

From `performance/mtp_acceptance/sm120_mtp2.md`:

| shape (c=1) | pos0 accept | pos1 accept | accept_len |
|---|---|---|---|
| mt-bench | 85.6 % | 52.0 % | 2.38 |
| random ISL=1024 | 73.5 % | 31.2 % | 2.05 |
| random ISL=8192 | 71.2 % | 25.4 % | 1.97 |

Implications for the **no-MTP** goal:
- pos1 acceptance on mt-bench (52 %) is high enough that `num_speculative_tokens=3`
  is worth trying — but only as a separate MTP track. Doesn't help no-MTP.
- The fact that mt-bench gets accept_len 2.38 while random struggles to reach 2.0
  is the standard MTP-prefers-natural-text pattern; not a SM12x-specific finding.

So the 120 tok/s push is purely a kernel-level no-MTP play.

## Optimization candidates, ranked

Each candidate lists: estimated TPOT delta, risk, work order. Round-numbered
percentages are best-case; real-world is typically half.

### Tier 1 — high-confidence wins (target: 86 → ~100 tok/s)

**T1-A. Autotune `_w8a8_triton_block_scaled_mm` for SM120** *(est. −0.8 to −1.5 ms TPOT)*

The kernel runs **30 208 times in 0.87 s** at an average of 14.46 μs — that's
the MoE expert FP8 GEMM doing single-token decode. Our current configs were
copied from the SM120 device-name JSON (`vllm/model_executor/layers/quantization/utils/configs/N=*,K=*,device_name=NVIDIA_RTX_PRO_6000_Blackwell_Workstation_Edition,dtype=fp8_w8a8,block_shape=[128,128].json`),
which were swept against a different shape distribution. Re-sweep with
`block_m ∈ {16, 32, 64}`, `block_n ∈ {64, 128}`, `block_k ∈ {64, 128, 256}`,
`num_warps ∈ {4, 8}`, `num_stages ∈ {2, 3, 4}` against the decode-shape
distribution (M = 1, N = 1536/4096/8192, K matching DeepSeek V4 hidden).

Risk: low. Worst case the new configs are equal; you keep the old ones.

**T1-B. ~~Adopt PR #40392 `fuse_rope_kvcache_cat_mla`~~ Status: Not applicable to DSv4-Flash** *(2026-05-12)*

**Tested** (2026-05-12 on SM120 TP=2): enabled via
`--compilation-config '{"pass_config":{"fuse_rope_kvcache_cat_mla":true}}'`.
Pass registers successfully (`Enabled custom fusions: norm_quant, act_quant,
rope_kvcache_cat_mla` in serve log) but produces **null result** on decode
profile:

| Metric | T1-A (no pass) | T1-B (pass on) | Delta |
|---|---|---|---|
| Throughput (single-stream decode) | 81.34 tok/s | 80.99 tok/s | noise |
| Total kernel time / token | 28.28 ms | 28.52 ms | +0.85% (noise) |
| Per-kernel µs/call (top 7) | — | — | all within ±1% |
| Diff > 0.05 ms/tok normalized | — | — | only 1 kernel (cross_device_reduce, +0.2 ms/tok from per-call slowdown 7.27→8.39 µs) |

**Root cause**: DSv4-Flash's MLA path **already source-level-fuses**
RoPE + KV-compress + norm + insert into custom kernels — visible in the
profile as `_fused_kv_compress_norm_rope_insert_sparse_attn`,
`_fused_q_kv_rmsnorm_kernel`, `_fused_kv_compress_norm_rope_insert_indexer_attn`,
`_fused_inv_rope_fp8_quant_per_head`, `_fused_indexer_q_rope_quant_kernel`.
The vLLM compiler pass is designed for **vanilla DSv2/V3** RoPE where these
are separate ops; on DSv4-Flash the pattern matcher finds nothing to fuse
because the pre-fused kernels don't expose the matched sub-graph.

The "Enabled custom fusions" log line registers the pass but does **not**
imply it matched anything. To see actual fusion counts you'd need to add
debug logging to `MLARoPEKVCacheCatFusionPass.__call__()`.

**Lesson**: Future stack ports should verify pass matched-count, not just
pass-enabled, when adapting from upstream-level fusion to source-level fusion
codebases. DSv4-Flash gets this benefit "for free" from our existing
`csrc/attention/deepseek_v4/...` and `vllm/v1/attention/ops/deepseek_v4_ops/`
custom kernels.

Risk now moot. Decision: **keep default OFF** for DSv4-Flash (avoids the
+0.2 ms/tok cross_device_reduce penalty seen in T1-B).

**T1-C. ~~Investigate~~ Status: Marlin is the only viable MXFP4 MoE backend on SM12x DSv4** *(estimated upside reduced; see below)*

**Diagnostic complete** (2026-05-12). The profile entry
`marlin_moe_wna16::Marlin<1125899906909960l, 562949953487106l, 1125899906909960l, 2814749767106568l, 128, 1, 8, 4, true, 4, 2, false>`
decodes via `vllm::ScalarType::id()` to:

| template arg | decoded value |
|---|---|
| a_type_id (activation) | `BFloat16` (e=8, m=7, signed, IEEE 754) |
| b_type_id (weight)     | `float4_e2m1f` / **MXFP4** (e=2, m=1, finite-only, no NaN) |
| c_type_id (output)     | `BFloat16` |
| s_type_id (B scale)    | **E8M0** (e=8, m=0, unsigned, finite-only, extended-NaN) — MXFP4 block scale |
| threads / m_blocks / n_blocks / k_blocks | 128 / 1 / 8 / 4 |
| m_block_size_8         | `true` → M tile = 8 (decode small-batch path) |
| stages / group_blocks  | 4 / 2 (group span 32 == MXFP4 sf_block_size ✓) |

So this is the **MoE expert w13/w2 GEMM in MXFP4** (BF16 act + MXFP4 weight + E8M0 scale)
— **not** the FP8 path, **not** a misrouted dense projection. DSv4-Flash's experts
are MXFP4 (`expert_dtype="fp4"` in HF config), and `Mxfp4MoEMethod` is the active
quant method.

**Why Marlin wins**: vLLM's `select_deepseek_v4_mxfp4_moe_backend` priority list for
non-ROCm platforms is:

```
[FLASHINFER_TRTLLM_MXFP4_MXFP8,   # rejected: is_device_capability_family(100) — SM10x only
 DEEPGEMM_MXFP4,                   # rejected: our SM12x DeepGEMM guards
 MARLIN,                           # accepted ✓
 BATCHED_MARLIN]
```

The Triton/CUTLASS MXFP4 alternatives are also unreachable on SM12x DSv4:

| Candidate | Blocker on SM12x DSv4 |
|---|---|
| `OAITritonMxfp4ExpertsMonolithic` (TRITON) | device cap range `(9,0) ≤ cap < (11,0)` excludes SM12x; routing limited to `Renormalize{,Naive}` (DSv4 uses `DeepseekV4`) |
| `UnfusedOAITritonExperts` (TRITON_UNFUSED) | same device-cap range; also flagged "bug with MTP support" in oracle comment |
| `FlashInferExperts` w/ `(kMxfp4Static, None)` (CUTLASS BF16) | `_supports_quant_scheme` allows BF16 act only on `is_device_capability(90)` — Hopper-strict, excludes SM12x |
| `FlashInferExperts` w/ `(kMxfp4Static, kMxfp8Dynamic)` (CUTLASS MXFP8) | **viable** on SM12x (`is_device_capability_family(120)` ✓, `has_device_capability(100)` ✓), but **not in the DSv4 priority list** |
| `TrtLlmMxfp4ExpertsMonolithic` (TRTLLM) | `is_device_capability_family(100)` only |

**Conclusion**: Marlin's 12.89% is **not a misrouting**; it is the only working
MXFP4 MoE kernel on SM12x DSv4 today. The "−1.5 ms if avoidable" estimate in
the original note assumed a routing bug — there is none. Downgrading expected
saving from "free fix" to "requires kernel/oracle work".

**Possible follow-up paths** (none cheap):

1. **T1-C(a). Enable `FLASHINFER_CUTLASS_MXFP4_MXFP8` for SM12x DSv4** —
   one-line oracle patch to add this backend to `_get_priority_backends()`,
   plus thread `kMxfp8Dynamic` activation key through. Adds an MXFP8 activation
   quantization pass per MoE call (extra kernel launches) but the CUTLASS GEMM
   should map better to SM120 5th-gen tensor cores than Marlin's pre-Blackwell
   layout. **Verdict**: experimental, uncertain win (could be net-positive or
   net-negative).
2. **T1-C(b). Tune Marlin compile-time variants** — the chosen tuple
   `(threads=128, m_blocks=1, n_blocks=8, k_blocks=4, stages=4)` is one of
   ~dozen pre-instantiated variants in `csrc/moe/marlin_moe_wna16/`. Marlin's
   dispatch (`marlin_moe.py:fused_marlin_moe`) picks per shape; check if a
   different `(n_blocks, k_blocks, stages)` variant is faster for the
   (M=8, N=∗, K=∗) decode shape. **Verdict**: low-medium win, requires
   recompile if no variant matches.
3. **T1-C(c). Write a Triton MXFP4 W4A16 MoE kernel for SM12x** — full control
   but ~2-3 weeks of work, and Marlin already does what we need. **Verdict**:
   defer — only if T1-A/B/D + T1-C(a/b) don't reach 120 tok/s.

Risk re-assessed: **medium-low** (no longer a free correctness fix). Recommend
deprioritising vs T1-A (autotune `_w8a8_triton_block_scaled_mm`, 23.33% — much
larger absolute hotspot) and T1-D (kernel-launch overhead).

**T1-D. ~~Reduce decode-step kernel-launch count~~ Implemented as: adaptive BLOCK_M for `_fp8_paged_mqa_logits_kernel`** *(2026-05-12)*

**Implemented and validated** (2026-05-12, commit `c802ae27a`). The original
T1-D framing was "fuse the 30 k+-instance launch-bound kernels". We pivoted
to a higher-ROI target — the **#3 kernel `_fp8_paged_mqa_logits_kernel`** in
the T1-A profile (12.61%, 84.87 µs/call) had a hardcoded `BLOCK_M=4`
regardless of `num_rows`. For the single-stream decode path
(num_rows = batch_size × next_n = 1) that wastes 75% of the M-axis work
(3 of every 4 rows masked off and discarded).

Fix: `vllm/v1/attention/ops/deepseek_v4_ops/sm12x_mqa.py:fp8_paged_mqa_logits_triton`
picks the smallest power-of-2 tile that still covers `num_rows`:

```
num_rows == 1  → BLOCK_M=1   (no-MTP decode, batch=1)
num_rows == 2  → BLOCK_M=2
num_rows ≤ 4   → BLOCK_M=4   (MTP=2 decode, batch=1, num_rows=3)
num_rows > 4   → BLOCK_M=8
```

Cost: 4 Triton specializations instead of 1 — cudagraph capture exercises
each; first-load Triton JIT adds a few seconds, then cache-hit.

**Measured impact** (SM120 TP=2 single-stream decode, no-MTP, 64-token
profile window):

| Metric | T1-A | T1-D | Delta |
|---|---|---|---|
| `_fp8_paged_mqa_logits_kernel` µs/call | 84.87 | 36.17 | **−57% (2.35× faster)** |
| That kernel's share of decode time | 12.61% | 5.81% | **−6.8 pp** |
| Total kernel time / token | 28.28 ms | 26.14 ms | **−7.6%** |
| Single-stream decode throughput | 81.34 tok/s | **89.44 tok/s** | **+10.0%** |

For MTP=2 (`num_rows=3`) the picked `BLOCK_M=4` is unchanged from baseline
(1 of 4 rows masked, same as before) — no regression on the MTP path.
Prefill (`num_rows ≥ 4`) picks `BLOCK_M=4` or `8` and benefits when
`num_rows == 4`/`8` exactly (no waste).

Remaining items from the original T1-D framing — the 30 k-instance launch-
overhead kernels (`direct_copy_kernel_cuda`, `vectorized_elementwise_kernel`,
`per_token_group_quant_8bit_kernel`) — are still candidates but deferred to
**T1-D'** (a follow-up): fusing `per_token_group_quant_8bit` into the GEMM
prologue is a multi-day Triton kernel project, not a small surgical change.

### Tier 2 — medium-confidence, may not all stack (target: 100 → 115 tok/s)

**T2-A. Tune our SM12x sparse-MLA finish kernel (#5)** *(est. −0.3 to −0.6 ms TPOT)*

`_finish_materialized_scores_with_sink_candidate_block_kernel` runs 5 166 times
at 17.87 μs (4.93%). The HANDOFF.local.md "Post-Baseline SM12x Kernel
Optimization Candidates" list flags this as a known tuning target. Current
block size and warp shape were chosen for correctness, not max throughput.

Approach: vary `BLOCK_*` constexprs and `num_warps` in the Triton kernel;
profile with the same harness. Risk: medium (the kernel has subtle masking
logic; correctness gate is the gsm8k 5-shot 200q exact_match ≥ 0.945 floor).

**T2-B. Tune our SM12x FP8 einsum kernel (#6)** *(est. −0.2 to −0.5 ms TPOT)*

`_deepseek_v4_sm12x_fp8_einsum_kernel` at 4.48% — same playbook as T2-A.

**T2-C. Adopt PR #40408 (Cutlass FP8 batch invariance)** *(est. unknown — upstream claim 28.9 % E2E)*

Upstream reported "28.9% E2E latency improvement" from Cutlass FP8 batch
invariance. We don't know if the underlying kernels compile for SM120. Action:
1. Run our baseline with `VLLM_BATCH_INVARIANT=1` (or whatever the upstream
   knob is; check the PR description).
2. Measure mt-bench c=1 TPOT.
3. If green, this is probably the biggest single win.

Risk: medium-high (Cutlass kernels are SM-version-sensitive; may not even
build on 12.0a).

**T2-D. Reduce TP all-reduce overhead (#4)** *(est. −0.2 to −0.5 ms TPOT)*

`cross_device_reduce_1stage` at 5.89% — that's TP=2 all-reduce for hidden
states + lm_head + MoE expert outputs (depending on EP layout). SM120 boxes
typically lack NVLink (PCIe-bridged), so this is bandwidth-bound on PCIe.

Possible wins:
- `--gpu-memory-utilization 0.97` (or higher) so KV cache is bigger → bigger
  decode batches amortise the all-reduce. Won't help c=1 though.
- Check if `--enable-expert-parallel` could be tuned (we already use it; the
  alternative is full TP for experts which adds all-reduce work elsewhere).
- Investigate if the all-reduce is BF16 (it is — see template params) and
  whether FP8 all-reduce in the upstream Cutlass batch invariance PR applies.

Risk: low to investigate, medium to ship.

### Tier 3 — exploratory, save for later

**T3-A. SM12x-specific PR #42236 Triton variant**

PR #42236 added a CuteDSL fast path for `dequantize_and_gather_k_cache` (SM10x
only). The Triton fallback is what we use. If profile after T1+T2 still
shows this kernel high, port the CuteDSL win to a hand-tuned SM12x Triton
version.

**T3-B. Try `num_speculative_tokens=3` (MTP track, not no-MTP target)**

mt-bench pos1 acceptance 52% suggests pos2 acceptance might land 30-40%,
making `num_speculative_tokens=3` slightly net positive for natural-text
workloads. This is for the MTP track separately, not the 120 tok/s no-MTP
target. Run `run_decode_profile.sh` with `--speculative_config '{"method":"mtp","num_speculative_tokens":3}'`
and compare.

**T3-C. Tokenizer fast-path**

`tokenizer-mode deepseek_v4` runs custom V4 logic; if the chat-template path
hits the slow tokenizer first, that adds TTFT but not TPOT. Out of scope for
decode-rate goal.

## Recommended execution order

1. ~~**T1-C** (investigate Marlin WNA16)~~ **DONE 2026-05-12**. Marlin is the
   only viable MXFP4 MoE backend on SM12x DSv4 — not a misrouting, not a free
   fix. See T1-C section for full diagnostic + downstream options
   T1-C(a/b/c). Expected savings revised down from "−1.5 ms" to "uncertain
   (medium-low)"; deprioritised vs T1-A.
2. **T1-A** (autotune w8a8 fp8 block GEMM): mostly mechanical, low risk, biggest
   single-kernel surface (23.33% — largest absolute hotspot). Re-run
   `run_decode_profile.sh` after to confirm.
3. **T1-B** (verify fuse_rope_kvcache_cat_mla actually fires): cheap diagnostic.
4. **T1-D** (cudagraph deeper coverage): may bundle naturally with T1-A
   verification.
5. **T2-A / T2-B** (tune our SM12x kernels): take MoE / sparse MLA delta from
   step 2 then iterate.
6. **T2-C** (Cutlass FP8 batch invariance): try last — high risk of
   compatibility issues on SM12x but huge potential upside.
7. (Optional) **T1-C(a)** — patch oracle to try `FLASHINFER_CUTLASS_MXFP4_MXFP8`
   on SM12x DSv4. Run only after T1-A/B/D land; needs MXFP8 activation
   quantization plumbing. Could be a 1-2% win or a regression.

After each step, re-run `scripts/run_decode_profile.sh` with the same config
to verify TPOT delta against this baseline.

## Verification protocol

For each change:
1. `git stash` any other WIP, apply only the candidate change.
2. Reset SM120 host to `git checkout origin/ds4-sm120-preview-dev` (or your
   patch branch), reinstall (`pip install --no-build-isolation -e .` if
   C++/CUDA touched).
3. Run `scripts/run_decode_profile.sh` with the SAME prompt/max_tokens/warmup
   shape used here. Compare `torch_kernel_summary.md` top-N rows.
4. Re-run mt-bench `c=1 num-prompts=80` for steady TPOT.
5. Run `bash scripts/run_lm_eval.sh` (gsm8k 5-shot 200q) — must stay ≥ 0.945.
6. Record numbers under a new `baselines/<date>_<label>/` and link from
   `tuning_targets.md` next-iteration section.

## Definition of done

Baseline rerun with the same matrix at SM120:
- `bench_hf_mt_bench c=1 num-prompts=80 → output_token_throughput_tok_s ≥ 120`
- `random ISL=1024 OSL=512 c=1 num-prompts=24 → output_token_throughput_tok_s ≥ 110`
- `gsm8k 5-shot 200q exact_match ≥ 0.945` (no correctness regression)
- Cross-platform generation quality audit (vs B200 / B300 / Official API)
  remains identical-class.

If we hit those three, we ship it as the next baseline.

## Related artifacts

- Profile snapshot: `performance/profile/sm120_nomtp_decode_64tok/torch_kernel_summary.md`
- MTP per-position trace: `performance/mtp_acceptance/sm120_mtp2.md`
- Bench JSON: `../../artifacts/ds4-sm120-preview-dev/2x_nvidia_rtx_pro_6000_blackwell_workstation_edition/sm120_tp2_ds4_sm120_preview_dev_020e0c89a/`
- Repro recipe: `repro_recipe.md`

## How to rerun the profile

```bash
ssh jasl@<sm120-host> 'cd /home/jasl/Workspace/ds4-sm120-harness && \
  OUT_DIR=/tmp/decode_profile_sm120_<label> \
  PROFILE_LABEL=sm120_nomtp_decode_<label> \
  PROFILE_MAX_TOKENS=64 \
  SERVE_COMMAND="/home/jasl/Workspace/vllm/.venv/bin/vllm serve deepseek-ai/DeepSeek-V4-Flash --trust-remote-code --kv-cache-dtype fp8 --block-size 256 --max-model-len 65536 --tensor-parallel-size 2 --host 127.0.0.1 --port 8000 --no-enable-flashinfer-autotune --reasoning-parser deepseek_v4 --tokenizer-mode deepseek_v4 --tool-call-parser deepseek_v4 --enable-auto-tool-choice --enable-expert-parallel --gpu-memory-utilization 0.95" \
  bash scripts/run_decode_profile.sh'
```

Pull `torch_kernel_summary.md` back to compare against this baseline.
