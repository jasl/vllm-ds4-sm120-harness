# Upstream merge (41 commits): DSv4 sequence parallelism + workspace reuse

Status: accepted
Date: 2026-08-02
Owner/context: merge `affa4b85a5` + cleanup `4450216c9e` on `wip/merge-234`.

## Question

Upstream landed two DSv4 changes that collide with this branch's own work:
`38a466e7b6` (#46789, sequence parallelism) and `df71917cf1` (#49236, workspace
reuse for eager break). Both touch files we have rewritten. What survives from
each side, and does the result still serve correctly on SM12x?

## Profile

- Hardware: 2x GB10 / DGX Spark (sm_121), RoCE `.116`/`.119`; units on `.117`
- Commits: merge `affa4b85a5`, cleanup `4450216c9e`
- Model: `deepseek-ai/DeepSeek-V4-Flash-0731`, DSpark `num_speculative_tokens=5`
- TP 2 / PP 1 / EP off, fp8 KV, prefix cache on, `FULL_AND_PIECEWISE`
- `max_model_len` 49152, `max_num_seqs` 64, `max_num_batched_tokens` 8192,
  `--block-size 256`, util 0.85
- Dependencies unchanged by this merge (torch 2.13.0, FlashInfer 0.6.15.post1,
  tilelang 0.1.12, nccl 2.30.7) — only test/TPU requirements moved.

## Result

### Conflicts: 20 hunks across 6 files

| file | resolution |
| --- | --- |
| `csrc/.../fused_deepseek_v4_qnorm_rope_kv_insert_kernel.cu` | upstream verbatim |
| `csrc/libtorch_stable/torch_bindings.cpp` | upstream's two `ops.def` |
| `csrc/libtorch_stable/ops.h` | hand-fixed (auto-merged into a broken hybrid) |
| `vllm/models/deepseek_v4/attention.py` | combine |
| `vllm/models/deepseek_v4/common/ops/cache_utils.py` | combine |
| `vllm/models/deepseek_v4/nvidia/dspark.py` | ours, byte-for-byte |
| `vllm/models/deepseek_v4/nvidia/model.py` | combine + 3 SP correctness edits |

**Sequence parallelism is inert on SM12x** but wired correctly anyway.
`_use_sequence_parallel` (model.py) requires expert-parallel AND
(`deep_gemm_mega_moe` OR DP>1); the SM12x MoE backend is Marlin MXFP4 and DP=1,
so it is False even at 4-node TP=4 with `--enable-expert-parallel`. It is still
resolved properly because this branch serves multi-node users whose configs can
reach it, and a half-applied SP is worse than none.

`nvidia/dspark.py` keeps our side entirely. PR #27 replaced the two-kernel
`mhc_post` + `hc_head` sequence with the fused `mhc_post_hc_head_tilelang`, which
never materializes the `[T, hc_mult, H]` intermediate — and that intermediate is
exactly what upstream's `sp_all_gather` needs between the two kernels. Upstream's
`ModuleList`/`DeepseekV4DecoderLayer` shape is also incompatible with our
`DSparkLayer`, and `sp_shard` on dim 0 would split DSpark blocks across ranks,
breaking the `batch_size = num_input_rows // block_size` geometry.

**Three SP correctness edits the merge did not produce on its own.** The
auto-merged `sp_all_gather(hidden_states)` sits ahead of tail consumers that still
take a sharded residual, so under SP the deferred `mhc_post` path is now disabled
and materialization is forced before the gather. Upstream's `if layer is not None:`
was *not* adopted — it is an unbound local when a PP rank owns no layers.

### The op split: we adopted upstream's shape and retired ours

Upstream split the fused qnorm-rope-kv-insert op into an allocating `..._insert`
and a caller-buffered `..._insert_out` with an explicit `q_head_padded` argument.
We took that wholesale and retired our local `53b6d1110c` variant.

Why, given ours worked: upstream's split is a strict superset, the merged tree was
already half-way there (`ops.impl` registered both, `attention.py` auto-merged to
call `_out`), and keeping ours would mean reverting an upstream change on a file
upstream actively develops — the same reason we retired #48304 / #48911 / #48959.

★ `ops.h` had auto-merged into a **broken hybrid**, carrying our `void`/`q_out`
declaration of the base name alongside upstream's `_out`. Taking upstream's `.cu`
without fixing it is an ODR mismatch at link time, not a compile error.
`torch_bindings.cpp`'s base schema had likewise auto-merged to our `Tensor! q_out`
text. Neither shows a conflict marker.

★ Side effect: `amd/dspark.py:243` already called the 9-argument allocating form,
which was **broken** against our out-form schema. Adopting upstream's shape fixes
that pre-existing ROCm break.

PR #27's value is kept: `attention.py` writes Q in place whenever
`padded_heads == n_local_heads` (true on SM12x TP=2), falling back to upstream's
eager-scratch pool and then to our class scratch.

### Cleanup: five of six candidate dead paths were live

Every candidate was audited for reachability before anything was deleted. The
useful output was mostly *what not to delete*:

| candidate | verdict |
| --- | --- |
| pool `q_out` / `_q` | **live** — `padded_heads == n_local_heads` is a property of ONE attention class; FlashMLA pads everything to 64, so at TP=2 it needs the buffer every forward |
| our `_q_padded_scratch` (53b6d1110c) | **live** — covers exactly the ubatching case upstream punts on ("TODO: support dbo if needed") |
| `reserve_profile_scratch` | **live**, and the obvious cleanup would have been a bug — see below |
| XPU / AMD parallel implementations | **live** and consistent |
| discarded-upstream residue in `dspark.py` | **live** |
| leftovers of retired `53b6d1110c` | **live** |

★ The near-miss: adding `if self.eager_scratch_pool is not None: return` to
`reserve_profile_scratch` looks obviously correct and is not. The scratch cache is
class-level and keyed on `(device, ubatch_id, dtype, padded_heads, head_dim)` —
**not** on layer identity — so the MAIN layers' profile reservation is what
pre-warms the buffer the DRAFT layers later consume. Removing it moves that
allocation past the profile run, reintroducing the OOM jasl/vllm#26 fixed.

The one change made: an `allocate_q` gate. `padded_heads` **is** model-wide
(`get_padded_num_q_heads` is a pure classmethod of the single attention class a
process selects; `n_local_heads` depends only on head count and TP size), so the
caller can decide once whether the buffer can ever be read. On the default SM12x
path it cannot — the FlashInfer-SM120 decode class pads to {16,32,64,128}, so 64/TP
maps to itself. That is **256 MiB** at TP=2 with `max_num_batched_tokens=8192`,
against 36 MiB for every aux view in the pool combined, held for the process
lifetime and charged against KV headroom. `q_out()` now raises rather than
returning a `None` slice if the decision was ever wrong — so a serve that comes up
and stays up *is* the evidence the gate is right.

★ Do not try to A/B this with the serve-log KV figure; it is ~1 GiB noisy. The
justification is the allocation arithmetic (verified from the real checkpoint:
`n_heads` 64, `head_dim` 512, `n_layers` 43).

Also fixed, all found by the audit rather than by review:
- a latent dtype-key mismatch — `reserve_profile_scratch` reserves under
  `model_config.dtype`, `_get_q_padded_scratch` reads under runtime `q.dtype`, and
  dtype is part of the cache key. Now an assert.
- `_op_available()` gated on the allocating op's name while the helpers call the
  `_out` form, so it proved nothing about what runs.
- `assert returned.data_ptr() == q_out.data_ptr()` was a tautology: the helper
  returns the very object it was handed.
- `fix_functionalization.py` registered only the old op name, so our hot path
  (now `_out`) would have silently lost its copy elision.

## Validation

Unit suite at `4450216c9e` (`units_4450216c9e.log`, `.117`):

| section | result |
| --- | --- |
| A. DSv4 kernels | 229 passed, 12 skipped |
| B. DSv4 attention backends | 6 passed |
| C. spec decode / dspark config | 40 passed |
| D. kv offload | 715 passed, 1 skipped |
| E. core scheduler + prefix cache | 232 passed, 1 failed |
| F. kernel warmup | 2 passed |
| G. DSv4 tokenizer / prompt encoding | 44 passed |
| H. functionalization pass | 16 passed |

E's single failure needs 2 GPUs in one node; GB10 has one each, so it cannot pass
here and failed identically at the previous head. A is +2 over the merge head —
the two new coverage tests, confirmed by name as PASSED, not skipped.

GB10 2-node gates at `4450216c9e`, DSpark nst=5 (`gates_driver.log`):

| gate | result |
| --- | --- |
| serve | rc=0, KV 17.06 GiB / 130,652 tokens |
| #19 instruction-following (JSON-only) | PASS |
| long-context recall (arthur), c=1 | 2/2 |
| DSpark draft acceptance (prose) | steady-state samples 1.32 / 1.68 / 2.07 |
| GSM8K 8-shot, flexible / strict | 0.9462 / 0.9424 |
| illegal-access / assertion lines in serve log | 0 |

GSM8K is +0.68 pp flexible over the 0731 DSpark baseline (0.9394). The measured
single-run spread on this gate is ~1.1 pp, so that is **inside noise** and is not
evidence of anything.

★ Acceptance is **not** comparable to the baseline's headline figure. This probe
collected `samples=9` against the baseline's 3, and "best of 9" is a different
order statistic from "best of 3" — the probe reports the best sample by design.
Compare the steady-state samples instead: 1.32 / 1.68 / 2.07 brackets the
baseline's 2.08, i.e. unchanged.

## Interpretation

The merge is safe to ship. Sequence parallelism is inert here but correctly wired
for the multi-node users of this branch; the workspace-reuse op split is adopted in
upstream's shape, which also repairs a pre-existing ROCm break; PR #27's in-place Q
path survives untouched.

## Harness defects fixed

- Ad-hoc `units_*.sh` did not put `$VR/.venv/bin` on PATH, where `ninja` lives.
  Every `tests/compile/` case then dies with `FileNotFoundError: 'ninja'` — 8
  failures that read as a code regression and are not one. With the PATH fixed it
  is 16/16. The canonical `scripts/run_acceptance.sh` already handles this
  (`run_static_gate` prepends `dirname $PYTHON`); only the hand-rolled script was
  wrong. Same shape as the 07-27 nvcc/`CUDA_HOME` incident, different tool.
- Two new tests were added to the working tree but not committed before the nodes
  checked out the merge SHA, so the first unit run did not contain them at all
  while still reporting a plausible count. Confirm new tests by NAME, not by a
  delta in the pass total.

## Open

- benchy at this head (running at time of writing) — for gross regressions only;
  this branch's own history spans 31% on tg128 and 4–10% on ctx_pp.
- FlashInfer 0.6.16 upgrade (0.6.15.post1 pinned today). Relevant contents: SM120/
  SM121 sparse-attention support, unified MoE with SM12x B12x NVFP4 / W4A16
  backends, and on-disk JIT caching (cold start 3–30 ms, −1.6 GB installed). The
  release notes claim no breaking API changes — verify `_sparse_mla_sm120` and
  `trtllm_batch_decode_sparse_mla_dsv4` directly rather than trusting that.
- GSM8K 3x per cell to settle the DSpark/nospec difference.
- V2 model runner and breakable-cudagraph experiments.
