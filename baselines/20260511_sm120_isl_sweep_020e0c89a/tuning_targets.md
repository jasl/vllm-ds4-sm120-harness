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

**T1-B. Adopt PR #40392 `fuse_rope_kvcache_cat_mla`** *(est. −0.5 to −1.0 ms TPOT)*

Upstream merged a compile pass that fuses RoPE + KV-cache update + q_concat
for MLA. The flag is `enable_qk_norm_rope_fusion`-adjacent. Currently it's
auto-enabled on `current_platform.is_cuda_alike()`, which includes SM120, but
no one has confirmed it actually fires there. Verify by:
1. Run `run_decode_profile.sh` again with `VLLM_LOG_LEVEL=INFO` and look for
   the pass-application log line.
2. Compare elementwise-copy time before/after — direct_copy at #8 (2.93%) is
   exactly the kind of op this pass should eliminate.

Risk: low. Pass is upstream-default.

**T1-C. Investigate why Marlin MoE WNA16 (#2) is running** *(est. up to −1.5 ms if avoidable)*

DSv4 Flash uses FP8 weights — `marlin_moe_wna16` is a WNA16 (4-bit weight,
16-bit activation) kernel. Either:
- A subset of experts (shared experts, gate, e_proj?) is unintentionally on
  the WNA16 path. → Force them onto the FP8 path.
- It's the gating/router. → Check that the gating layer isn't accidentally
  routed through a quantized path.

The 562949953487106 / 1125899906909960 template literals encode shape — they
should reveal which projection. Risk: medium (correctness must be preserved).

**T1-D. Reduce decode-step kernel-launch count** *(est. −0.3 to −0.8 ms TPOT)*

The profile shows several **30 k+-instance** kernels at ≤ 2 μs avg:
- `direct_copy_kernel_cuda` (#8): 36 522 inst × 1.50 μs = launch-overhead bound
- `vectorized_elementwise_kernel<BUnaryFunctor<...>>` (#14): 35 712 inst × 0.95 μs
- `per_token_group_quant_8bit_kernel` (#10): 30 208 inst × 1.61 μs

The 30 208 count exactly matches the FP8 GEMM count — so quant happens once
per GEMM per layer. Fusing the per-token quant into the GEMM prologue (or
pulling more layers into the same cudagraph) would amortise launch overhead.

Risk: low-medium. cudagraph_mode is already `FULL_AND_PIECEWISE`; gain is from
adding more graph shapes or fewer split points.

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

1. **T1-A** (autotune w8a8 fp8 block GEMM): mostly mechanical, low risk, biggest
   single-kernel surface. Re-run `run_decode_profile.sh` after to confirm.
2. **T1-C** (investigate Marlin WNA16): cheap to investigate, possibly free
   win if a routing bug.
3. **T1-B** (verify fuse_rope_kvcache_cat_mla actually fires): cheap diagnostic.
4. **T1-D** (cudagraph deeper coverage): may bundle naturally with T1-A
   verification.
5. **T2-A / T2-B** (tune our SM12x kernels): take MoE / sparse MLA delta from
   step 1 then iterate.
6. **T2-C** (Cutlass FP8 batch invariance): try last — high risk of
   compatibility issues on SM12x but huge potential upside.

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
