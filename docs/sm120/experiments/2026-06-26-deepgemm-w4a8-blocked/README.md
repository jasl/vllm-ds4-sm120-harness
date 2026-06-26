# DeepGEMM W4A8 (nv_dev) on SM12x — blocked by o_proj einsum / UE8M0 conflict

Status: blocked
Date: 2026-06-26
Owner/context: Auto-detect nv_dev DeepGEMM and route the DSv4 MoE to the DeepGEMM
W4A8 (`DEEPGEMM_MXFP4`) path with a Marlin (W4A16) fallback, for an A/B vs the
current Marlin production path. Motivated by the lmxxf "DSv4 needs W4A8" article.

## Question

Can DeepSeek-V4-Flash serve on SM12x with the DeepGEMM W4A8 MoE path (the nv_dev
`sm120_fp8_fp4` kernels, DeepGEMM PR #324), auto-enabled when an nv_dev-built
DeepGEMM is present and falling back to Marlin otherwise? And is W4A8 faster?

## Profile

- Hardware: 2x GB10 (SM121, family-120), nodes 10.0.0.116 + 10.0.0.118.
- vLLM branch/commit: `c766cbc6ff` + the (now-reverted) global-flip patch
  `c273246bd1` (backed up at branch
  `experiment/deepgemm-sm120-w4a8-blocked-20260626` in the vllm-pr-rebase repo).
- Dependency identity: external `deep_gemm 2.5.0+aced12c` already installed in
  the serve venv on BOTH nodes (nv_dev lineage; ships all 9 `sm120_*.cuh` JIT
  headers incl. `sm120_fp8_fp4_gemm_1d1d.cuh`). No DeepGEMM build was needed.
- TP / PP / EP: TP=2 / PP=1 / EP off.
- MTP: num_speculative_tokens=2.
- FP8 KV: yes.
- Prefix cache: on.
- CUDA graph mode: FULL_AND_PIECEWISE.
- `max_model_len`: 49152. `max_num_seqs`: 64. `max_num_batched_tokens`: 8192.
- Route flags: `VLLM_DEEPGEMM_SM120_ENABLE=auto` (the patch's lever);
  `VLLM_USE_DEEP_GEMM_E8M0` toggled both ways (see Result).

## Result

The gate flip itself is correct on real hardware: `support_deep_gemm()` returns
True, `is_deep_gemm_supported()` resolves auto→True / off→False / on→True, and
the MoE oracle selects `DEEPGEMM_MXFP4` (W4A8) over Marlin. But the serve
**crashes during startup** for every E8M0 setting — the model never reaches a
healthy state, so no GSM8K / #19 / arthur / llama-benchy numbers were collected.

- `VLLM_USE_DEEP_GEMM_E8M0=1` (default): crash in the DSv4 **attention o_proj**
  `fp8_einsum` during warmup. With E8M0 on, weight scales pack to int32, so the
  SM12x triton einsum fallback condition
  (`_use_deepseek_v4_sm12x_triton_fp8_einsum`, needs `float32`/`e8m0fnu`) is
  false → falls through to the DeepGEMM einsum → `Assertion (layout.hpp:97):
  sf.size(-2) == ceil_div(mn, gran_mn)`.
- `VLLM_USE_DEEP_GEMM_E8M0=0`: crash earlier, at **weight load**, in the MoE
  W4A8 scale packing (`_pack_deepgemm_mxfp4_scales` →
  `deepgemm_post_process_weight_scale_block` → `transform_sf_into_required_layout`)
  → `Assertion (layout.hpp:49): not disable_ue8m0_cast` — the W4A8 packing
  *requires* UE8M0.

## Interpretation

The two DeepGEMM consumers DSv4 activates on SM12x have **mutually exclusive**
scale-format requirements, and UE8M0 is a single global weight-scale-format
decision:

- MoE W4A8 (`DEEPGEMM_MXFP4`) scale packing **requires UE8M0** (E8M0 on).
- DSv4 attention o_proj `fp8_einsum` **requires float32** scales (E8M0 off) so it
  takes its validated SM12x triton path; the DeepGEMM einsum has no working
  SM120 kernel for the `bhr,hdr->bhd` / `(1,128,128)` recipe.

So a global `is_deep_gemm_supported()` flip cannot serve DSv4 on SM12x — it
drags the o_proj einsum onto DeepGEMM, and no E8M0 setting satisfies both paths.
This vindicates the pre-implementation blast-radius concern (the global lever is
too coarse). The W4A8 MoE kernel is real and selectable, but W4A8-vs-Marlin perf
remains **unmeasured** because the model cannot serve. Marlin (W4A16) remains the
correct, fast production path on SM12x — unchanged and unaffected (the patch is
safe-by-default: stock/old-pin builds have no nv_dev marker → Marlin).

Does NOT prove anything about prefix-cache or EP sensitivity (never reached
inference). Does NOT prove the W4A8 MoE kernel is numerically wrong — only that
the surrounding integration cannot bring the model up.

## Follow-Up

- Decision: the global-flip approach is rejected; if W4A8 is pursued it needs a
  narrower lever PLUS o_proj einsum work (not a gate change). Candidate fixes:
  (a) make the SM12x triton einsum accept UE8M0/int32 scales so the o_proj
  survives E8M0-on; (b) per-weight scale format (o_proj `wo_a` float32 while MoE
  experts UE8M0); (c) a working DeepGEMM SM120 einsum for `bhr,hdr->bhd`
  (upstream DeepGEMM). All are model-kernel changes with unproven payoff.
- Backup of the rejected attempt: branch
  `experiment/deepgemm-sm120-w4a8-blocked-20260626` (commit `c273246bd1`,
  vllm-pr-rebase repo). Drivers: `/home/jasl/tmp/gb10_dgemm_ab_serve.sh` +
  `gb10_dgemm_ab_gates.sh` (scratchpad).
- Rerun trigger: an nv_dev DeepGEMM SM120 einsum kernel for the o_proj shape, or
  a vLLM change decoupling o_proj scale format from the global UE8M0 decision.
- PR branch hygiene: the flip is kept OUT of `codex/ds4-sm120-min-enable` /
  `ds4-sm120-preview-dev` / `reconcile/upstream-sync-20260626` (all reset to
  `8a911d2e10`).
