# GB10 2×SM121 DeepSeek-V4-Flash baseline — `832775efd1` (2026-07-21)

Merge of upstream/main `fbfe58133d` (79 commits) onto our `d15fad8acf`. Supersedes
`2026-07-17-upstream-merge-3b6c96a101-baseline`. Motivating change: **upstream merged
PR #48911** (2026-07-20), so our earlier cherry-pick of it is dropped in favor of
upstream's reviewed version; our #48959 fix is retained (its upstream PR #49052 is
still open).

## Build / environment
| | |
|---|---|
| vLLM head | `832775efd1` (merge `562e79714c` + one stale-test fix) |
| merge | 79 upstream commits; 4 conflicts hand-resolved, 0 fork features dropped, 0 behind upstream |
| torch | 2.11.0+cu130 |
| flashinfer | 0.6.14 (python + cubin) |
| nvidia-cutlass-dsl | 4.6.0 · quack-kernels 0.6.1 · nvidia-nccl-cu13 2.30.7 |
| GPUs | 2× GB10 (SM121a), TP=2, RoCE CRS804 (192.168.100.116/.119) |
| serve | boot 403s, healthy through all gates, 0 IMA |

## What this merge changed for us
- **#48911 (offload SWA reachable-tails)**: our cherry-pick `738e712288` dropped;
  now carry upstream's merged version (`is_store_reachable_swa_chunk` byte-identical to
  upstream). Net delta in `offloading/scheduler.py` vs upstream = **only our #48959 fix**.
- **#48959 (offload SWA unaligned pending-bound)**: retained as a fork delta
  (`max_pending_gpu_blocks_for_group`); upstream PR #49052 still OPEN. Drop when it lands.
- **Conflicts (4), hand-resolved:**
  1. `offloading/scheduler.py` — upstream #48911 + our #48959.
  2. `offloading_connector/test_scheduler.py` — both import sets.
  3. `mla/indexer.py` — `treat_short_extends_as_decodes`: our DSv4 ubatch guard
     (`not has_prefilling_rows`, e1d6dc859b) AND upstream's new PCP feature
     (`not self.use_pcp`, #46570) combined as the **conjunction**
     `not has_prefilling_rows and not self.use_pcp`. For GB10 (PCP off) this reduces
     to exactly our fork's behavior; for PCP users to exactly upstream's.
  4. `sparse_attn_indexer.py` — our SM120 deep_gemm guard
     (`_sparse_indexer_requires_deep_gemm(use_fp4_cache)`) + upstream's new `use_pcp` line.

## Perf — llama-benchy STANDARD (pinned `@b220b7c9`, pp2048 tg128, C=1, 3 runs, prefix-cache; 2 full runs)
vs the current baseline of record (07-17 `f63bfd3d7b`, 2-run means):

| depth | ctx_pp | vs base | pp2048 | vs base | tg128 | vs base |
|---|---|---|---|---|---|---|
| 8192  | 1830.7 | −0.5% | 1397.5 | +0.4% | 40.6 | +4.2% |
| 16384 | 1800.1 | +0.3% | 1313.4 | −1.3% | 42.1 | +13.4% |
| 32768 | 1721.8 | +1.1% | 1208.2 | −0.2% | 36.1 | −7.7% |

**Verdict: flat vs the last shipped baseline — no regression.** Prefill and pp2048 are
within noise. Decode `tg128` swings by depth (+4/+13/−7%) with the same run-to-run
instability as always: d32768 read **32.8 on run 1 and 39.4 on run 2 (20% swing)**, so
the −7.7% is noise, not signal — a single benchy run cannot resolve decode below ~8% at
C=1 (`project_decode_hostbound_not_ar_wall`). Prefill gains from the 07-17 merge held
(ctx_pp still +4.2/+1.5/+1.3% vs older 5e43b2cfa7).

## Correctness / functional (all GREEN)
- **GSM8K** (full 1319q, 8-shot): **0.9500 strict / 0.9492 flexible**, IMA-clean. In band.
- **Coherence** (arthur ~28k): **c=1 2/2** (deterministic recall discriminator); **c=12 24/24** (perfect).
- **#19 instruction-following**: PASS.
- **Tool-calling** (135 cases, 3 thinking modes, temp 1.0): 86% content (231/270),
  **engine-clean (0×500, 0 IMA)**. Same band as prior (sampling noise; engine is the merge criterion).
- **Unit suite**: offloading_connector 162 passed (up from 143 — upstream added tests);
  core prefix/scheduler 223 passed + 1 environmental (needs 2 GPUs/node); DSv4 SWA + ubatch pass.

## Review (79 commits, 3-lens workflow + adversarial verify)
0 confirmed findings, 1 refuted. The refuted candidate — upstream #48660 (dsv4 routing
specialized kernel) bypassing hash-MoE routing — was disproven with a concrete mechanism:
the dsv4_topk fast-path requires `correction_bias is not None`, but DSv4-Flash hash-MoE
layers set `e_score_correction_bias=None` (mutually exclusive with the correction-bias
branch), so it cannot fire on our path.

## ★ Merge-validation catch (unit suite, again)
`test_indexer_builder_keeps_short_prefill_continuations_as_prefills` failed — traced to a
**pre-existing stale test**: its `object.__new__` mock set `reorder_batch_threshold`, but
`build()` reads `self.decode_threshold` (renamed by an earlier upstream merge — already red
on `d15fad8acf`). Our PCP conflict resolution additionally made `build()` read `self.use_pcp`.
Fixed the mock (set both; `use_pcp=False`), which makes the test now actually **validate the
conjunction resolution** (treat_short_extends_as_decodes == not has_prefilling_rows on our path).

## Reproduce
```bash
VLLM_ROOT=/home/jasl/tmp/vllm-merge-20260711 \
VLLM_VENV=/home/jasl/tmp/ds4-sm120-harness/vllm/.venv \
  scripts/run_gb10_llama_benchy_standard.sh
```
