# GB10 2×SM121 DeepSeek-V4-Flash baseline — `1ee1ec7930` (2026-07-27, PR #27 + 34 upstream)

Second shipping round of 2026-07-27, on top of `520c25949c` (PR #33, DSpark shared-expert fix).

| | |
|---|---|
| head | `1ee1ec7930` — **0 behind upstream/main** |
| lands | `1a2e039039` PR #27 (alexbi29) → `2dfeed68e2` +31 upstream → `1ee1ec7930` +3 upstream |
| gated at | `2dfeed68e2` (full battery) + `1ee1ec7930` (GSM8K + arthur c=1) |
| serve | 2-node TP=2, MTP2, mml 49152, util 0.85, fp8 KV, prefix-cache on |

## What landed

**PR #27 — "reduce DSpark/V2 working VRAM"**, far larger than its title: 1533 insertions
across 23 files. It rewrites the DSv4 MHC aux-hidden tail, adds four fused tilelang kernels,
merges the C128A decode/prefill topk buffers, and caches the C128A local→global index mapping
across layers instead of recomputing (and re-allocating ~128 MiB) per layer.

**+34 upstream commits.** The last three are inert for us: ROCm quickreduce (`quick_reduce.h`),
CPU fused-MoE, and a tokenizers-registry refactor whose behaviour change is gated on
`tokenizer_cls_ is CachedHfTokenizer` — DSv4 uses `DeepseekV4Tokenizer`, so it takes the
unchanged `config_format="auto"` path; the rest of that commit hoists `tokenizer_cls_`
resolution earlier with the same final value in all three branches.

## Review — the parts that could have bitten us

PR #27 mutates shared per-step metadata in place, which is the failure class this branch has
hit repeatedly. Each concern was closed against code or the checkpoint, not by reasoning:

- **In-place C128A local→global rewrite, cached across layers.** Safe. The Triton kernel reads
  and writes the *same element* of each row (`ptr + token_idx*stride + offset`) with no
  cross-row reads, so aliasing input to output is sound. The `super()._forward_prefill`
  fallback — whose parent at `flashmla.py:952` reads the same field expecting *local* indices —
  is gated on the **global** env `VLLM_DEEPSEEK_V4_FLASHINFER_SM120_PREFILL`, so the whole model
  takes one path or the other and layers never mix readers. The metadata object is rebuilt each
  step, so the cache starts empty per step.
- **Decode and prefill now share one `c128a_topk_buffer`.** Partition is exact:
  `is_decode = token_idx < num_decode_tokens`, prefill writes the view starting at that row.
- **Shared lens buffer carries stale values into the prefill tail.** Harmless — the consuming
  kernel stores `topk_lens[token_idx]` unconditionally for every token, so it is write-only.
- **`_mtp_hidden_buffer` became conditional** on the draft `hf_config` exposing both
  `compress_ratios` and `hc_mult`. DSv4-Flash `inference/config.json` has both (`hc_mult: 4`),
  so our MTP path still allocates it. That config also shows `compress_ratios` uses only 4 and
  128, which is what makes the single-C128A-ratio caching assumption hold.
- **Only one of PR #27's four new kernels runs on our default path.**
  `mhc_post_mean_tilelang` and `mhc_post_mean_hc_head_tilelang` require
  `aux_hidden_state_layers`, populated only when `use_aux_hidden_state_outputs` is set (EAGLE3,
  not MTP); `mhc_post_hc_head_tilelang` requires `_mtp_hidden_buffer is None` (DSpark/DFlash).
  Under MTP those are dead code. The one live kernel,
  `mhc_fused_post_pre_tilelang_reuse_residual`, runs twice per decoder layer and is validated
  end-to-end by the gates below.

### Noted, not fixed
`mhc_fused_post_pre_tilelang_reuse_residual` is **not** `direct_register_custom_op`'d and is
absent from `__all__`, unlike the `mhc_fused_post_pre_tilelang` it replaced on the hot path.
Measured effect: none (0 graph breaks, CUDA-graph capture 24 s). It is also arguably the safer
side — an unregistered plain function leaves its in-place mutation visible to the tracer,
whereas registering it under this file's uniform `mutates_args=[]` would declare a mutation that
does happen as absent. **Do not "fix" this by registering it with `mutates_args=[]`.**

## Correctness — all GREEN

Full battery at `2dfeed68e2`:

| gate | result | vs history |
|---|---|---|
| #19 instruction-following (JSON-only) | PASS | ✓ |
| arthur coherence **c=1** (recall discriminator) | **2/2** | ✓ |
| arthur coherence c=12 | 23/24 | known 22–23/24 band |
| toolcall15 (en × 3 modes, rounds=3) | **86%** | 82/87/89 → 86% at torch 2.13 |
| GSM8K | **0.9568** | identical to `70a33886bd` |
| IMA / assert in serve log | 0 | ✓ |

Unit suite at `2dfeed68e2`: core prefix-cache + scheduler 232 passed (1 known 2-GPU-per-node
environmental failure), offload + kv_offload **795 passed**, DSv4 fork sparse-SWA/ubatch/indexer
**6 passed** — including upstream's new `test_indexer_warmup_normalizes_zero_compress_ratios`
running alongside ours, which validates the 31-merge conflict resolution — rejection sampler
**35 passed**.

DSpark serve at `2dfeed68e2` answers correctly (17×23 → 391, Paris, primes 2/3/5).

Re-gated at `1ee1ec7930` after the +3: arthur c=1 **2/2**, IMA/assert 0, and GSM8K **×3**.

### ★ GSM8K single-run spread is ~1.1pp — wider than our whole historical range

The first re-gate run returned **0.9469**, below every recorded value, and the tokenizers-registry
commit was the one plausible suspect, so it was repeated rather than explained away:

| run at `1ee1ec7930` | GSM8K (flexible) |
|---|---|
| #1 | 0.9469 |
| #2 | 0.9507 |
| #3 | **0.9583** |

Range **0.9469 – 0.9583** on one unchanged build. Historical single-run values span
[0.9500, 0.9560, 0.9545, 0.9568, 0.9568, 0.96] — so the metric's own run-to-run spread is wider
than the entire build-to-build history, and run #3 lands above the `2dfeed68e2` reading. **No
regression; the +3 upstream commits are clean.**

The consequence is bigger than this merge: every historical GSM8K figure in these baselines is a
single run carrying ~1pp of uncertainty, so past readings we have treated as distinguishable
(0.9568 vs 0.9500) were inside noise. GSM8K discriminates *gross* correctness breakage, not
sub-1pp quality deltas. Repeat ×3 and compare ranges. This is the fourth measurement-resolution
limit found on this branch, after toolcall-15 (±6pp single-run), tg128 (9–12% per-run), and the
serve-reported KV figure (~1 GiB / 9%).

## PR #27 kernel-test A/B — no new failure modes

Both legs on one node, same environment (`.118`, natively built at `520c25949c`):

| `tests/kernels/test_mhc_kernels.py` | `520c25949c` | `2dfeed68e2` |
|---|---|---|
| failed | 13 | 11 |
| passed | 31 | 53 |
| skipped | 8 | 8 |

`tests/v1/spec_decode/test_rejection_sampler_utils.py`: 29 → **31 passed** (PR #27 adds two,
both pass). Every failure sampled on that node is the same
`ImportError: … requires the CUDA flash attention extensions (_vllm_fa2_C or _vllm_fa3_C)` —
a build gap on that freshly-provisioned node, present on both legs. The only AFTER-only failure,
`test_mhc_fused_post_pre_reuses_dead_buffers[128]`, is the `[128]` parametrization that already
fails for the pre-existing `test_mhc_fused_post_pre[*-128]` without the reuse variant, so it
inherits an existing failure rather than introducing one.

## ★ The serve-reported KV figure is too noisy to A/B — retracted claim

Same serve script and config at four points:

| SHA | Available KV memory | GPU KV cache |
|---|---|---|
| `520c25949c` (pre-PR #27) | 20.33 GiB | 155,729 tokens |
| `1a2e039039` (PR #27 only) | 19.91 GiB | 150,373 tokens |
| `2dfeed68e2` (PR #27 + 31 upstream) | 19.92 GiB | 142,364 tokens |
| `1ee1ec7930` (+3 **inert** upstream) | **20.89 GiB** | **155,371 tokens** |

The first three rows were initially read as "PR #27 costs ~0.42 GiB on the default MTP path" and
recorded as an open regression. **That reading is withdrawn.** The fourth row settles it:
`2dfeed68e2` → `1ee1ec7930` differs only by ROCm quickreduce, CPU fused-MoE and a tokenizers
refactor — none of which can free a gigabyte — yet available KV moved 19.92 → 20.89 GiB and the
token count 142,364 → 155,371 (+9%). The metric's own run-to-run spread swamps the effect being
attributed to PR #27, so **no VRAM claim about PR #27, in either direction, is supported by
single runs.**

The figure derives from a memory-profiling run — peak activation during a dummy forward — so it
tracks allocator state, fragmentation and JIT/warmup cache warmth rather than a static property
of the build. Any future VRAM A/B needs ≥3 repeats per SHA compared as ranges, the same
discipline the 2026-07-27 torch-2.13 baseline adopted for tg128.

Separately, and still true: the `142,364` reading is **not** lost memory. Available KV is flat
across `1a2e039039` → `2dfeed68e2`; what changed is upstream's **per-token** KV cost (+5.6%).

PR #27's actual claim — skipping the ~470 MiB `_mtp_hidden_buffer`, which only DSpark/DFlash do —
remains unmeasured. The first attempt produced a bogus number: `serve_dspark.sh` writes
`ROOT=/home/jasl/tmp/dspark_test` while the A/B script hardcoded `merge_test_20260711`, so it
re-read the previous MTP leg's `head.log` and reported byte-identical figures. Redo against
`dspark_test/serve/head.log`, capturing each value before the next serve overwrites it.

**Still unmeasured: the DSpark-side VRAM A/B**, i.e. PR #27's actual claim. The first attempt
produced a bogus number — `serve_dspark.sh` writes `ROOT=/home/jasl/tmp/dspark_test` while the
A/B script hardcoded `merge_test_20260711`, so it re-read the previous MTP leg's `head.log` and
reported byte-identical figures. Redo against `dspark_test/serve/head.log`, capturing each value
before the next serve overwrites it.

## ★ Method — three false results before one real one

Classifying PR #27's kernel tests produced three wrong answers in a row, none of them about the
code:

1. The first run was summarised with `tail -6`, so `55 failed` scrolled past as two visible test
   names. That nearly became a reported finding.
2. The re-run used the wrong venv (`$H/.venv`; the real one is **`$H/vllm/.venv`**) against a
   clone that had never fetched the merge SHA.
3. The corrected run reported 43-vs-63 failures — every one a
   `tilelang_callback_cuda_compile` RuntimeError, because **non-interactive ssh has no `nvcc` on
   PATH and no `CUDA_HOME`**. With `export PATH=/usr/local/cuda/bin:$PATH; export
   CUDA_HOME=/usr/local/cuda` the same test passes immediately.

Rules taken from this: for any remote pytest that JIT-compiles, export the CUDA environment the
serve scripts already carry and use `$H/vllm/.venv/bin/python`; capture the whole `-q` summary,
never a tail; and when a suite goes red all at once, read one traceback before theorising —
mass-red is an environment signature, not a code signature.

## Node provisioning — `.117` / `.118`

Both provisioned with the full torch-2.13 stack (torch 2.13.0+cu130, triton 3.7.1,
FlashInfer 0.6.15.post1, quack 0.6.1, tilelang 0.1.9) and build `rc=0`, usable for serving.
**Known gap:** `_vllm_fa2_C` / `_vllm_fa3_C` are present on disk under `vllm/vllm_flash_attn/`
but not importable, so the full kernel test suite does not run there yet. `.116` is unaffected.

## Follow-on — `d64074e6f0`: bound the block-table gather

Shipped after this baseline (tag `sm120-pr-41834-stable-preview-20260727d`).
`_compute_global_topk_indices_and_lens_kernel` validated only `local_idx >= 0` before indexing
`block_table[req_idx, local_idx // block_size]`. Those indices are data — they come from the
indexer's top-k, which writes into a `torch.empty` buffer shared by every layer — so an unwritten
or corrupted slot could gather past the end of the table and take down every TP rank. Added
`& (block_indices < block_table_stride)`; out-of-range entries fall out as `-1` and are excluded
from `topk_lens`.

The path is unreachable on GB10 and this is insurance, not a live fix: `use_fp4_indexer_cache` is
hard-asserted off outside Blackwell datacenter parts and nothing in the tree assigns it, so
`q_scale` is always None and prefill always takes the fused DeepGEMM top-k path, which never
materializes logits. That holds for the NVFP4 checkpoint too — NVFP4 is model weights, not the
FP4 *indexer cache*. Upstream hit this on stock vLLM (#49896 root cause 3).

Validation: arthur **c=1 2/2** — the right discriminator, since a wrongly-rejected legitimate
index drops needles and GSM8K cannot resolve that — plus c=12 23/24, GSM8K 0.9538, IMA 0. The
unit test is bug-encoding: it passes with the bound and fails with the bound reverted in place.

## Node provisioning follow-up — `.117` / `.118` fully rebuilt

The `_vllm_fa2_C` / `_vllm_fa3_C` import failure was not a build gap in the extensions: the first
provisioning pass built only the *worktree* and left the main clone's `.so` from the torch-2.11
era, and cd-ing into the main clone shadows the editable install, so the stale ABI won. A full
rebuild (fresh venv, both trees, every `.so` purged) brings both nodes to parity with `.116`:
`vllm_flash_attn` imports from both trees, and `tests/kernels/test_mhc_kernels.py` +
`test_flashmla_sparse.py` run **67 passed / 11 skipped** on each, against 63 failed / 1 passed
before. Test deps are not installed by `pip install -e .` — `.116` needs only pytest, tblib
(`tests/conftest.py` imports it) and lm_eval. `deep_gemm` and `b12x` are deliberately absent:
the SM12x fallbacks are pure Triton, and `_sparse_indexer_requires_deep_gemm` returns
`use_fp4_cache` (False) on capability family 120.

## Reproduce

```bash
bash /home/jasl/tmp/serve_merge_20260711.sh   # 2-node TP=2 MTP2, pinned standard config
bash /home/jasl/tmp/gates_0727.sh             # #19, arthur c=1/c=12, toolcall15, GSM8K
bash scripts/run_gb10_llama_benchy_standard.sh 1ee1ec7930
```
