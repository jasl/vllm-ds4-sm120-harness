# Evidence

## External Ref Check

Remote heads checked on 2026-06-13:

| Ref | Head | Notes |
| --- | --- | --- |
| `local-inference-lab/vllm main` | `183726aaa8e7bda60e4717051ed7de8fd8b13a30` | Baseline worktree commit. |
| `local-inference-lab/vllm dev/black-benediction` | `5fcd00c3d797e3e8b132eda5eabf80168b4aca47` | Newer black-benediction head, but mostly DFlash/spec-decode and Triton MLA decode work relative to the earlier freeze point. |
| `local-inference-lab/vllm dev/unholy-fusion` | `d037f7a61af2f04beef39b2216d79e574249cbd9` | Historical reference line, not used for this run. |

The benchmark worktree was detached at `183726aaa8e7bda60e4717051ed7de8fd8b13a30`
and had one temporary local modification:
`vllm/v1/core/kv_cache_utils.py`.

## Startup Findings

The unmodified fork `main` did not provide a usable 131K MTP baseline in the
current profile:

| Attempt | Outcome |
| --- | --- |
| Default b12x package before refresh | Startup failed because the expected b12x sparse/indexer API surface was incomplete for this fork route. |
| b12x git-master refresh | Startup advanced, then failed in KV cache sizing because mixed page-size groups reached uniform-page accounting code. |
| `--disable-hybrid-kv-cache-manager` | Startup could estimate capacity, but could not serve the 131K profile because available KV capacity was too small. |
| Temporary mixed page-size KV accounting patch | Startup succeeded, with GPU KV cache size around `355859` tokens and maximum concurrency `2.71x` for 131072-token requests. |

The temporary patch adds mixed page-size handling to `_pool_bytes_per_block()`
and `_max_memory_usage_bytes_from_groups()` by reusing the allocator's bucketed
page-size model instead of forcing `get_uniform_page_size()` on collapsed
representative cache groups.

## Route Confirmation

The serve logs confirm the intended external fork route:

- `load_format=instanttensor`
- `attention_backend=B12X_MLA_SPARSE`
- `moe_backend=b12x`
- `linear_backend=b12x`
- `enable_chunked_prefill=True`
- `scheduler_reserve_full_isl=False`
- `async_scheduling=True`
- `enable_flashinfer_autotune=True`
- `kv_cache_dtype=fp8`
- `enable_prefix_caching=False`
- `DeepSeek V4 b12x mHC enabled for token counts <= 16384`
- `Using 'B12X' Mxfp4 MoE backend`

b12x PCIe oneshot allreduce was requested, but the extension build failed in
the runtime environment and vLLM fell back to PyNCCL for TP/EP communication.
Therefore this baseline should be interpreted as B12X compute/sparse/MoE path
plus PyNCCL allreduce fallback.

## RTX Prefill C1 Matrix

Command shape:

```bash
SM12X_PREFILL_GAP_INPUT_LENS=4096,8192,16384,32768,65536,124000 \
SM12X_PREFILL_GAP_CONCURRENCY=1 \
SM12X_PREFILL_GAP_OUTPUT_LEN=1 \
SM12X_PREFILL_GAP_NUM_PROMPTS=4 \
scripts/run_sm12x_prefill_gap_attribution.sh
```

The attribution wrapper's overall status is `OK=False` because sparse stats are
missing from this external B12X path. The benchmark phase status is still valid:
each input length had `server_startup=0`, `bench_random_prefill_sweep=0`, and
the per-case prefill sweep summary reported `ok=true`.

| Input length | Phase exits | Successful requests | Input tok/s | Mean TTFT ms | P99 TTFT ms |
| ---: | --- | ---: | ---: | ---: | ---: |
| 4096 | `0 / 0` | 4 | 1352.93 | 3027.34 | 10020.45 |
| 8192 | `0 / 0` | 4 | 6687.35 | 1224.88 | 1232.17 |
| 16384 | `0 / 0` | 4 | 6579.92 | 2490.90 | 2493.83 |
| 32768 | `0 / 0` | 4 | 6425.10 | 5098.65 | 5119.41 |
| 65536 | `0 / 0` | 4 | 6149.28 | 10656.28 | 10760.92 |
| 124000 | `0 / 0` | 4 | 5709.02 | 21720.46 | 22024.65 |

The 4K row includes a cold first-request outlier. Use 8K-124K for the primary
gap comparison unless a future rerun isolates warmup effects.

## Correctness Guard

Command shape:

```bash
B200_BASELINE_PHASES=eval_gsm8k \
LM_EVAL_LIMIT=200 \
LM_EVAL_NUM_FEWSHOT=8 \
MTP_LM_EVAL_NUM_CONCURRENT=1 \
scripts/run_b200_baseline.sh
```

Result:

| Task | Fewshot | Limit | Exact flexible | Exact strict | Stderr | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GSM8K | 8 | 200 | 0.965 | 0.965 | 0.01302780173668803 | 0 |

Runtime stats during the GSM8K phase:

| Metric | Value |
| --- | ---: |
| Mean acceptance length avg | 2.65 |
| Per-position acceptance avg | `[0.95, 0.702]` |
| Max running requests | 1 |
| Preemptions delta | 0 |
| Driver errors | 0 |
| CUDA errors | 0 |
| NCCL errors | 0 |

The log parser reported generic error-signal matches from serve text, but no
CUDA/NCCL/driver/engine error class was present.

## First Gap Reading

This run gives us a concrete external mechanism reference, but not a higher RTX
C=1 performance target:

- Current PR-line stage timing identifies sparse accumulate as the first
  bottleneck: `93.33%` of sparse prefill stage time at 16K and `96.61%` at
  65K.
- The current RTX attribution control reaches `8080.89` tok/s at 16K and
  `7576.42` tok/s at 65K C=1, while the external fork reaches `6579.92` and
  `6149.28` tok/s on those same input lengths.
- The 124K C=1 attribution control reaches `6835.25` tok/s, and the later
  fused sink-finish prototype reaches `7037.46` tok/s. The external fork's
  124K row is `5709.02` tok/s.
- Because the external route did not emit compatible sparse stats, the next
  step is mechanism isolation rather than declaring a kernel-level explanation
  from this endpoint run alone.

Practical first mechanisms to isolate:

1. The B12X sparse MLA backend dispatch and page/index representation.
2. B12X sparse indexer planning and whether it avoids the slow non-indexed
   chunk groups observed in the current bottleneck map.
3. B12X MXFP4/MoE routing under EP-off, after separating prefill attention
   gain from MoE throughput.
4. The mixed page-size KV cache accounting fix as a standalone upstreamable
   startup/capacity correction.
