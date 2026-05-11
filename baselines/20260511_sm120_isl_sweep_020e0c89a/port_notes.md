# SM12x DeepSeek V4 Port Notes — Lessons for a New Inference Stack

Distilled from the vLLM ds4-sm120 port. Useful as a checklist when porting
DeepSeek V4 Flash (or V4-class architectures) to SM12x consumer Blackwell on
a different inference stack.

## SM12x capability matrix vs SM10x datacenter

| Feature | SM10x (B200/B300) | SM12x (RTX Pro 6000, GB10) | Implication |
|---|---|---|---|
| TMEM (tensor memory, 256 KB/SM) | yes | **no** | All `tcgen05` instructions unavailable |
| `tcgen05` MMA instructions | yes | **no** | DeepGEMM, Cutlass kernels that use tcgen05 fail |
| Packed FP8 indexer cache layout | yes | **no** | Sparse-MLA indexer needs alternate Triton path |
| FP4 indexer cache | yes (SM100) | **no** | Disable via `SERVE_USE_FP4_INDEXER_CACHE=0` |
| FP8 fused MoE backend (datacenter Cutlass) | yes | **no** | Route to Triton block-scaled fp8 GEMM |
| PDL (programmatic dependent launch) | yes | **yes** (SM90+) | Common confusion; PDL is supported on SM12x |
| TMA (tensor memory accelerator) | yes | **yes** | But some tilelang/Triton configs default off |
| Unified memory (GB10 only) | n/a | yes (GB10) | Reclaim file cache (`echo 3 > drop_caches`) before launch |

## Must-do engineering work for a new stack

These are the categories of code our vLLM PR added. The new stack will hit
the same forks-in-the-road:

### 1. DeepGEMM / Cutlass fp8 fallback routing
DeepGEMM uses `tcgen05` → fails on SM12x. Required path:
- Detect SM12x (CUDA cap family == 120).
- Block the `deep_gemm` import / `sys.modules` stub.
- Route to Triton block-scaled FP8 GEMM
  (`_w8a8_triton_block_scaled_mm`-equivalent in your stack).
- Add device-tuned config JSONs for SM120 / SM121 (block_m, block_n, block_k,
  num_warps, num_stages).

### 2. Sparse MLA portable Triton kernels
DSv4 sparse MLA decode in our PR is implemented as portable Triton
(`_finish_materialized_scores_with_sink_candidate_block_kernel`,
`accumulate_fp8ds_global_slots_sparse_mla_attention_chunk_multihead`,
`accumulate_fp8ds_paged_sparse_mla_attention_chunk_multihead`,
`matmul_sparse_mla_attention_with_sink`,
`fp8ds_global_paged_sparse_mla_attention_with_sink_multihead`).
Each replaces a B200/B300 `flash_mla_sparse_fwd` call.

The new stack needs an equivalent dispatch:
- Detect SM12x.
- Provide Triton implementations for: SWA decode, compressed-decode, prefill.
- Avoid recomputing dequantization in attention kernels (use
  `dequantize_combined_sparse_mla_decode_kv` as a model — fuses compressed
  + SWA slots into one buffer).

### 3. MoE FP8 backend selection
Default datacenter FP8 GEMM backend uses Cutlass / DeepGEMM and won't work.
Must explicitly select Triton:
- vLLM equivalent: `--compilation-config '{"custom_ops":["all"]}'`, plus the
  routing in `Route SM12x DeepGEMM fallbacks` commit.
- SGLang equivalent (per PR #24303): `--fp8-gemm-backend triton --moe-runner-backend triton`.

### 4. Indexer / MQA scheduler-metadata path
`get_paged_mqa_logits_metadata` is DeepGEMM-backed in upstream vLLM and fails
on SM12x. Our fix:
```python
def _uses_deep_gemm_scheduler_metadata() -> bool:
    return (
        current_platform.is_cuda()
        and has_deep_gemm()
        and not current_platform.is_device_capability_family(120)
    )
```
Need to provide an alternate scheduler-metadata generator (Triton kernel
`_prepare_uniform_decode_kernel` in our PR).

### 5. KV cache layouts
`packed_fp8_indexer_cache_layout` (B200/B300) doesn't apply on SM12x. Set
`SERVE_USE_FP4_INDEXER_CACHE=0` (or stack equivalent). KV cache stays
`fp8_ds_mla` format with `block_size=256` `kv-cache-dtype fp8`.

### 6. KV cache size budgeting for the indexer
SM12x has tighter logits-buffer headroom than SM10x:
```python
def sparse_indexer_max_logits_bytes(is_sm12x):
    if is_sm12x:
        return 256 * 1024 * 1024    # 256 MB
    return 512 * 1024 * 1024        # SM10x can afford more
```

### 7. Startup kernel warmup
Cold JIT on the first inference batch costs ~1 s. Warm explicitly:
- DeepSeek V4 mHC TileLang kernels (token_sizes covering all decode shapes).
- DeepSeek V4 sparse-MLA mixed tokens / prefill kernels.
- MTP spec-decode kernels (request counts × draft tokens).
- Request-preparation kernels.

(In our PR: `Warm DeepSeek V4 startup kernels` + `Warm DeepSeek V4 MTP
spec-decode kernels`.)

### 8. MTP draft head
DSv4 ships a Multi-Token Prediction head. Worth supporting from day one if
your stack has a speculative-decoding framework — gives 30-60 % decode
speedup on natural text at `num_speculative_tokens=2`.

Key fixup for adapting to upstream API churn: upstream PR #41536 changed
`DeepseekV4DecoderLayer.forward()` signature mid-cycle. Your MTP draft path
must mirror the same call shape (returns `(x, residual, post_mix, res_mix)`,
then call `layer.hc_post(...)` to materialise).

### 9. Reasoning parser configuration
DSv4 reasoning is `<think>`/`</think>` delimited. For thinking-budget support
(`thinking_token_budget` API), the parser MUST be initialised with explicit
`reasoning_start_str` / `reasoning_end_str`. Default initialisation has them
empty and rejects budget requests with HTTP 400.

In vLLM: `--reasoning-config '{"reasoning_parser":"deepseek_v4","reasoning_start_str":"<think>","reasoning_end_str":"</think>"}'`.

## NCCL dependency (GB10-specific)

GB10 cluster MTP path is sensitive to NCCL version. Pre-upgrade NCCL produces
intermittent `sample_tokens` RPC timeouts and decode stalls. Upgrade NCCL to
the latest NVIDIA build that matches the CUDA 13.x runtime BEFORE debugging
any DSv4 cluster issues — saves days of red herrings.

## Things upstream churns that will keep biting

These are the spots where upstream vLLM has had two breaking changes in
under a month; your stack will see equivalents:

1. **DSv4 attention layer signature** — upstream PR #41536 added `post_mix`,
   `res_mix`, `residual` positional args mid-cycle. The Model class was
   updated, but downstream MTP and warmup paths broke.
2. **MoE file layout** — upstream PR #41979 moved `fused_marlin_moe.py` → `experts/marlin_moe.py`.
   Any port that touches Marlin imports breaks.
3. **DSv4 attention dispatch** — upstream PR #41812 refactored ROCm DSv4 into
   a dedicated backend (`DeepseekV4ROCMAiterMLASparseBackend`). Inline
   `if current_platform.is_rocm()` branches in `deepseek_v4_attention.py` are
   removed. Be ready to re-pivot if SM12x branches end up similarly inline.

Lesson: keep platform-specific dispatch **behind an env flag**, not inline
platform checks. Our `is_triton_sparse_mla_enabled` env-gated approach
survived two upstream refactors without manual rework — would not have if we
had used `if current_platform.is_device_capability_family(120):` everywhere.

## Build flags

- `TORCH_CUDA_ARCH_LIST=12.0a` for SM120, `12.1a` for SM121 (specific,
  not the broader `12.0f`/`120f` family target).
- `CCACHE_NOHASHDIR=true` for ccache reuse across worktree paths.
- `PATH=/usr/local/cuda/bin:$PATH` (or `/usr/local/cuda-13.2/bin` for GB10).
- `TRITON_PTXAS_PATH=$CUDA_HOME/bin/ptxas`.

## PR #41834 commit walk-through

Twelve commits in order (bottom of the rebase first):

1. **Fix DeepSeek V4 MLA prefix cache reuse** — DSv4 prefix cache invariant
   fix (independent of SM12x).
2. **Add Blackwell tuning config aliases** — `device_name=*Blackwell*` JSON
   pointers to SM120/121 FP8 fused-MoE configs.
3. **Add portable sparse MLA Triton kernels** — the ~3 000-line core: SM12x
   Triton replacement for `flash_mla_sparse_fwd`.
4. **Add DeepSeek V4 SM12x fallback ops** — `fp8_einsum`, `cache_utils`,
   `sm12x_deep_gemm_fallbacks`, `sm12x_mqa`.
5. **Route SM12x DeepGEMM fallbacks** — `vllm.utils.deep_gemm` SM12x guards,
   `cutlass` linear fallback, `sparse_attn_indexer` SM12x branch.
6. **Wire SM12x sparse MLA into DeepSeek V4** — actual integration in
   `deepseek_v4_attention.py` + env switches (`sparse_mla_env.py`).
7. **Reduce DeepSeek V4 load overhead on GB10** — skip unused MTP tensors,
   fix MXFP4 cleanup, fp8_einsum custom-op registration.
8. **Apply weight filter to fast safetensors loading** — `default_loader` and
   `weight_utils` get a `skip_weight_name_before_load` hook (used by MTP).
9. **Warm DeepSeek V4 startup kernels** — TileLang mHC + sparse MLA warmup.
10. **Add SM12x sparse MLA direct decode kernels** — the
    `dequantize_global_slots_k_cache` + `dequantize_combined_sparse_mla_decode_kv`
    fast paths.
11. **Stabilize DeepSeek V4 MTP scheduling** — MTP scheduler fixes +
    `deepseek_v4_mtp.py` (the file that the upstream #41536 fixup absorbs into).
12. **Warm DeepSeek V4 MTP spec-decode kernels** — MTP-specific warmup.

When porting to a new stack, you can roughly group them as:
- **Core SM12x kernels & dispatch**: 3, 4, 5, 6, 10
- **Env / config / build hygiene**: 2, 8
- **DSv4 correctness fixes (not SM12x-specific)**: 1, 7
- **Startup warmup**: 9, 12
- **MTP path**: 11 (+ the layer-signature fixup amalgamated in)

## Quick decision tree for the new stack

```
Do you support DSv4 Flash on B200/B300 already?
├── No  → Start with the upstream vLLM DSv4 code as a reference. Add SM12x
│         from there using the buckets above.
└── Yes → For each B200-only path, ask:
    ├── Does it use tcgen05 / DeepGEMM / Cutlass FP8 fused MoE?
    │   └── Yes → Provide Triton SM12x alternative (bucket 1, 3).
    ├── Does it touch the sparse-MLA indexer or KV cache layout?
    │   └── Yes → SM12x fallback (bucket 4, 6).
    ├── Is it MTP-related?
    │   └── Yes → Watch for upstream signature drift (PR #41536 lesson).
    └── Otherwise it's likely portable as-is.
```

## Cross-stack performance reference

For sanity-checking your port:

| Metric (SM120 TP=2, mt-bench c=1) | This vLLM port | SGLang PR #24303 |
|---|---|---|
| Single-request decode | **84 tok/s** no-MTP / **151 tok/s** MTP=2 | ~28 tok/s no-MTP |
| Prefill (~3500 input tokens) | ~2680 tok/s | ~180-200 tok/s |
| gsm8k 5-shot 200q | 0.955 (no-MTP) / 0.965 (MTP) | n/a yet |

If your new stack lands within 20% of these numbers on the same hardware,
you're in the same league. If you're closer to SGLang's numbers, look first at
cudagraph coverage (`FULL_AND_PIECEWISE` vs single batch) and at FP8 fused
op routing.
