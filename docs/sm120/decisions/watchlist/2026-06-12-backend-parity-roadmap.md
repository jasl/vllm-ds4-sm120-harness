# SM12x Backend Parity Roadmap

Status: watchlist
Last reviewed: 2026-06-14
Applies to: SM120 RTX PRO 6000, SM121 GB10, vLLM PR stable preview and
external backend branches
Profile sensitivity: EP-off is the current default comparison profile; EP-on,
prefix-cache-on, and prefix-cache-off results must be reported separately.

## Decision

The next phase is a backend-parity program, not a PR-branch rewrite. Keep the
validated PR stable preview as the user-facing base and run optimization work on
separate research branches that can be discarded if they fail the matrix.

Use the current PR branch as the base for new vLLM development. The current
code-bearing development branch is
`codex/ds4-sm120-pr3395-packed-dev-20260613` at `741ea24c46`, which descends
from the PR stable preview `f32247a5a6`, the backend-parity diagnostic stack at
`591b71bed0`, and the default-off indexed D512 multi-prefill prototype. When
the PR branch is later rebased on upstream/main, rebase or recreate the dev
branch on top of the new PR tip. Any dev-branch fix that belongs in the PR must
be split out and replayed onto the PR branch as a reviewable commit before it
becomes user-facing baseline behavior.

Freeze external references for this phase instead of following remote heads on
every run. Refresh them only during an explicit upstream-change review, or when
a rerun trigger below fires and the new upstream commit is relevant to SM12x
coverage, FlashInfer/b12x backend capability, or black-benediction parity.

Integrate the active routes in this order:

- First optimize the current EP-off sparse MLA accumulate bottleneck on dual
  RTX PRO 6000. The first valid stage-timing pass shows `sparse_accumulate` at
  `93.33%` of sparse prefill stage time for 16K and `96.61%` for 65K. Slow
  non-indexed `mla_prefill_chunk` groups remain the first concrete
  fork-independent backup target after the grouped-SWA endpoint prototype was
  rejected. GB10 should confirm narrowed candidates, not absorb every
  exploratory run.
- Watch upstream CUDA arch coverage work in `vllm-project/vllm#45277`. Rebase
  only when the merged upstream changes affect SM12x build/runtime coverage or
  conflict with our stack. After that rebase, drop any local build workaround
  that upstream has replaced and run targeted build/import/kernel smokes before
  performance gates.
- Treat upstream `vllm-project/vllm#42667` as the next meaningful upstream
  rebase item to review. It merged on 2026-06-12 and changes default Model
  Runner v2 selection for MoE architectures by adding DeepseekV2/Qwen2Moe
  coverage, removing the generic `is_moe` exclusion, keeping quantized models
  excluded, and marking elastic EP unsupported for V2. Any rebase containing it
  must record the active runner path before performance comparisons.
- Keep breakable CUDA graph as a separate, gated candidate to replace
  `FULL_AND_PIECEWISE`, not as routine default behavior. The route may have more
  optimization headroom, but previous GB10 / SM121 testing produced a semantic
  correctness failure on a trivial arithmetic prompt. It needs same-runner
  endpoint A/B plus RTX and GB10 semantic/lifecycle gates before promotion.
- Revalidate FlashInfer and b12x experiments under the current EP-off serving
  profile. The older EP-on dependency notes are no longer sufficient evidence
  because EP-off now wins the routine profile. Use upstream/main or released
  package capabilities where possible, and keep fork-only code behind
  experiment branches until endpoint evidence justifies promotion. The 2026-06-13
  RTX refresh makes public `b12x==0.20.0` usable as a no-deps component-probe
  dependency, but direct public b12x compressed MLA still loses to current D512
  split+finish on the refreshed `real_c128` component shape. Official
  FlashInfer `0.6.13rc1` plus matching `flashinfer-jit-cache==0.6.13rc1+cu130`
  is usable in the RTX dev venv and imports without the version-check bypass;
  it is not expected to include the unmerged packed SM120 sparse-MLA module.
- Keep the unmerged FlashInfer packed SM120 sparse-MLA route
  `flashinfer-ai/flashinfer#3395` / `lucifer1004/flashinfer:sparse-mla-sm120`
  as an important candidate path. The earlier GB10 endpoint-shaped prototype
  showed about `10-23%` TTFT improvement, but the vLLM adapter must stay behind
  `VLLM_DEEPSEEK_V4_FLASHINFER_PACKED_PREFILL=1` and must be revalidated under
  the current EP-off correctness and performance matrix before any PR
  promotion. The GB10 subset artifacts are
  `artifacts/main/2x_gb10_sm121/20260608_packed_fi_promotion_prefill_gap_valid/20260608180541`,
  `artifacts/main/2x_gb10_sm121/20260608_packed_fi_promotion_long_c2_mtp2/20260608185801`,
  and
  `artifacts/main/2x_gb10_sm121/20260608_packed_fi_promotion_mtp2_moe_soak_reduced/20260608190816`.
- Keep FlashInfer CUTLASS MoE for DeepSeek-V4 as a smaller default-off dev
  candidate, not as the main Lucifer parity answer. A conversion-only route is
  invalid because GPT-OSS-only MXFP4 alpha/beta/clamp defaults collapse MTP
  draft acceptance. Matching the DeepSeek-V4 expert-wrapper semantics restores
  correctness and gives a modest RTX ctx0 decode signal of roughly `-1%` to
  `+5%`, but it still leaves most of the C8-C64 gap versus Lucifer+PR3395.
  Require GB10 and longer promotion coverage before considering PR-default
  behavior.
- Treat `local-inference-lab/vllm` `dev/black-benediction` as the external
  performance target and reference implementation. The public remote moved from
  the 2026-06-12 freeze point `c6b2a7b187` to `5fcd00c3d7` on 2026-06-13; the
  new commits are DFlash/spec-decode and Triton MLA decode work, so they are a
  second-stage reference rather than the first sparse-prefill route. Reproduce
  any chosen mechanism with the harness before porting ideas.
- Reproduced `local-inference-lab/vllm main` `183726aaa8e7` as the first
  external endpoint baseline on RTX / SM120. With a temporary mixed page-size
  KV cache accounting patch, EP-off MTP=2 prefill C=1 reached
  `6687.35 / 6579.92 / 6425.10 / 6149.28 / 5709.02` input tok/s for
  `8K / 16K / 32K / 65K / 124K`, and GSM8K limit-200 8-shot scored
  `0.965 / 0.965` flexible/strict. This is below our current RTX C=1 baseline
  at the overlapping 16K/65K/124K points, so study the B12X sparse
  MLA/indexer/MoE mechanisms as portability and workload references before
  spending effort on black-benediction's DFlash-specific line.
- Reproduced `local-inference-lab/vllm dev/black-benediction`
  `5fcd00c3d7` on RTX / SM120 with the public dependency stack and working
  B12X PCIe oneshot allreduce. In the clean same-server no-prefix OSL=128
  comparison, C=1 input tok/s was `5407.26` at 16K and `5867.14` at 65K,
  below the current RTX PR stable preview anchor `6209.00` and `7049.72`.
  C=2 completed but showed poor ITL tail (`1200.29 ms` at 16K and
  `1418.34 ms` at 65K). Do not port the black-benediction endpoint stack as a
  whole; isolate lower-risk decode commits and keep DFlash/spec-decode behind
  correctness gates.
- Keep the NVIDIA Developer Forums Aiden recipe thread as a separate
  GB10 / SM121 integrated-image watchlist item. It reports a two-node GB10
  Aiden image with b12x MoE, FP8 KV, MTP=2, prefix caching, 1M context, and
  multiple community success reports. It is plausibly an `unholy-fusion`
  continuation, but it is not equivalent to the public-stack
  `dev/black-benediction` RTX reproduction above. Previous unholy-fusion
  research likely stalled because isolated knobs did not capture the full
  image/overlay stack: bundled FlashInfer sparse-MLA wrapper, b12x sparse
  indexer / MoE hooks, NCCL/RDMA/all-reduce setup, model-runner warmup, and
  prefix-cache/KV lifecycle behavior. Treat it as an external comparison and
  mechanism map before porting code. The forum thread also reports long-running
  KV-cache bloat / decode slowdown and possible block-pool eviction issues, so
  correctness, lifecycle, and driver-health gates are mandatory.
- Rejected the first direct-paged sparse-prefill prototype on RTX / SM120.
  `codex/ds4-sm120-sparse-prefill-dev-20260613` at `620c651203d` successfully
  routes compressed non-indexed rows through a default-off
  `mla_prefill_direct_paged` path without FlashInfer PR3395, but the current
  serial per-candidate paged kernel regresses the paired smoke from `4096.00`
  to `1796.49` input tok/s and from `248.58 ms` to `571.11 ms` mean TTFT.
  Direct rows reached only about `4.0e7` sparse visits/s, below both existing
  chunk rows and indexed-D512 rows. The next fork-independent prototype should
  preserve indexed-D512-style parallel scoring/value reduction while loading
  selected candidates from page tables.
- Kept the grouped-SWA dataflow only as component evidence. The 2026-06-13 RTX
  fused grouped-SWA microbench folds grouped-SWA online accumulation and
  compressed/SWA merge into one component kernel. Group32/block-C32 fused-only
  measured `0.498 ms` at 640 candidates and `0.743 ms` at 1152 candidates,
  versus split `0.630 ms` and `1.383 ms`. The default-off endpoint prototype
  did reach `mla_prefill_indexed_d512_grouped_swa` after fixing internal chunk
  position handling, but regressed C128 sparse accumulate from `289.962 ms` to
  `1283.237 ms` in the 16K/C=1 route-hit A/B. Do not promote the current
  manual grouped-SWA endpoint form.
- Keep DeepGEMM `33a715e3d9634b64a351855c74ad64e2d9359c7e` as a separate
  alternate MoE / EP-decode candidate, not as part of the first sparse-prefill
  route. The commit title is `SM120: fp4-A x fp8-B mixed GEMM (kAIsFP4,
  swapAB orientation)` and it updates six SM120 mixed-GEMM files plus tests.
  An external author recommendation says this commit is worth switching to for
  better MoE EP performance, especially decode, with a claimed `2x` kernel
  speedup from the commit bump and an optional swapAB add-on around `6%`.
  Treat that as a same-host reproduction target, not as evidence yet. The
  commit note itself says the swapAB orientation is only about `3-6%` faster
  for MoE decode and that empty-tile skip is the more important EP-decode
  lever, so the follow-up should measure both component kernels and endpoint
  decode / mixed-arrival behavior before considering any vLLM route.

## Evidence

- `docs/sm120/experiments/2026-06-12-epoff-backend-revalidation/README.md`
- `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/README.md`
- `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/preflight.md`
- `docs/sm120/experiments/2026-06-12-black-benediction-map/README.md`
- `docs/sm120/experiments/2026-06-13-local-inference-main-baseline/README.md`
- `docs/sm120/experiments/2026-06-13-black-benediction-rtx-public-stack/README.md`
- `docs/sm120/experiments/2026-06-13-aiden-recipe-forum-watch/README.md`
- `docs/sm120/experiments/2026-06-13-direct-paged-prefill-prototype/README.md`
- `docs/sm120/experiments/2026-06-13-fused-grouped-swa-microbench/README.md`
- `docs/sm120/experiments/2026-06-14-rtx-llm-decode-bench/README.md`
- `docs/sm120/decisions/watchlist/2026-06-13-upstream-mrv2-cudagraph-watch.md`
- Local PR stable preview tag:
  `sm120-pr-41834-stable-preview-20260612075245`
- Local fallback tag:
  `sm120-pr-41834-fallback-before-replacement-20260612053720`
- External heads checked on 2026-06-12:
  vLLM upstream/main `b7f9b6a`, `vllm-project/vllm#45277` head `e57d3b78`,
  `local-inference-lab/vllm dev/black-benediction` head `c6b2a7b`,
  FlashInfer upstream/main `d65c3eb`,
  `flashinfer-ai/flashinfer#3395` head `88539d03`, b12x master `fabb087`.
- External deltas checked on 2026-06-13:
  `vllm-project/vllm#45277` remained open at `e57d3b78`,
  vLLM upstream/main moved to `053e7daa79`, FlashInfer upstream/main moved to
  `992848ad`, b12x master stayed at `fabb087`, and black-benediction moved to
  `5fcd00c3d7`.
- FlashInfer PR3395 checked on 2026-06-13:
  GitHub still shows the PR open from
  `lucifer1004/flashinfer:sparse-mla-sm120`, and the fork branch head is
  `b619f0c650`.
- Fixed vLLM packed-route dev branch created on 2026-06-13:
  `codex/ds4-sm120-pr3395-packed-dev-20260613`, with base tag
  `sm120-pr3395-packed-dev-base-20260613`. It is now at `741ea24c46` after the
  default-off indexed D512 multi-prefill prototype commit. Keep future PR3395
  packed FlashInfer commits on this branch or descendants so the route does not
  depend on unreferenced WIP commits.
- Historical vLLM adapter sources checked on 2026-06-13:
  `backup/ds4-sm120-preview-dev-before-stack-reorder-20260611190541` exists at
  `321eda45aa` and is useful pre-reorder stack context, but the exact
  `flashinfer.sparse_mla_sm120` env-gated adapter is anchored by
  `2b82185506`, `844ee31313`, and the fuller Lucifer support commit
  `d11b5a708b`.
- RTX dependency and component refresh on 2026-06-13:
  b12x `0.20.0` no-deps import/probe state is healthy, FlashInfer `0.6.13rc1`
  is healthy after installing the matching jit-cache; `flashinfer.sparse_mla_sm120`
  remains the PR3395 fork surface, public b12x compressed MLA
  measured `0.432 ms` versus current D512 split+finish `0.209 ms` on
  `real_c128`, and grouped-stream component probes remain the stronger
  fork-independent sparse-MLA direction.
- Lucifer coupling probe on 2026-06-14:
  `local-inference-lab/vllm lucifer` at `7c6bbf4c5a4` failed to start on the
  public FlashInfer `0.6.12` stack because SM120 defaulted to
  `FLASHINFER_MLA_SPARSE_DSV4` and raised
  `FLASHINFER_MLA_SPARSE_DSV4 on SM120 requires FlashInfer's sparse-sm120 MLA
  wrapper`. Treat Lucifer endpoint numbers as coupled to the FlashInfer PR3395
  sparse-sm120 wrapper. Do not compare a forced `FLASHMLA_SPARSE_DSV4` launch
  as "Lucifer" performance; use it only for code-mechanism inspection if
  needed.
- Lucifer plus PR3395 local reproduction on 2026-06-14:
  the complete coupled stack (`local-inference-lab/vllm` `7c6bbf4c5a4` plus
  FlashInfer PR3395 `b41aa8dd2f`) ran successfully on RTX / SM120 after
  rebuilding vLLM native extensions. The warm ctx0 decode-only row was
  `198.9 / 332.7 / 391.4 / 784.4 / 1183.5 / 1872.1 / 2818.9` tok/s for
  C1/C2/C4/C8/C16/C32/C64, which reproduces the community Lucifer row to
  within noise and beats the current branch by `16-42%` from C8 through C64
  while still losing the isolated C4 crossover. GSM8K 5-shot limit-200 passed
  at both C=1 and C=4 with flexible/strict `0.955 / 0.955`; 0-shot C=1 was
  `0.900 / 0.000` and remains watch-only because strict 0-shot parsing is not a
  hard gate for this protocol. Treat PR3395 as demonstrated headroom and a
  dev-branch candidate, not as a hard PR-branch dependency until long-context
  and GB10 lifecycle gates pass.
- FlashInfer CUTLASS MoE isolation on 2026-06-14:
  current-branch dev probing showed that weight conversion alone selected
  `FLASHINFER_CUTLASS_MXFP4_MXFP8` but collapsed MTP draft acceptance to about
  `0.24-0.30` and regressed ctx0 decode. A corrected expert wrapper that does
  not inject GPT-OSS-only alpha/beta/clamp defaults restored MTP acceptance,
  passed GSM8K limit-200 5-shot at `0.945 / 0.945` flexible/strict, and moved
  ctx0 decode by `-1.0% / +1.1% / +1.3% / +2.2% / +4.9% / +1.9% / +4.4%` for
  C1/C2/C4/C8/C16/C32/C64. This is useful but insufficient to explain Lucifer
  high-concurrency scaling.
- DeepGEMM alternate checked on 2026-06-13 and probed on 2026-06-14:
  `deepseek-ai/DeepGEMM` commit `33a715e3d9634b64a351855c74ad64e2d9359c7e`
  remains a fixed reference for later MoE / EP-decode study. A current-branch
  DeepGEMM FP8-linear-only RTX probe selected `DeepGemmFp8BlockScaledMMKernel`
  and E8M0 scales while leaving MoE on MARLIN and attention off PR3395. The
  ctx0 decode row moved by `+4.2% / +1.1% / +4.8% / +3.6% / +4.4% / +1.0% /
  +3.8%` for C1/C2/C4/C8/C16/C32/C64, and GSM8K limit-200 5-shot C=4 passed
  at `0.955 / 0.940` flexible/strict. This is a real but modest default-off dev
  candidate. It does not explain the Lucifer C8-C64 gap, and it adds startup
  and runtime-JIT warmup caveats that must be solved before promotion.
- DeepGEMM plus FlashInfer CUTLASS MoE combination on 2026-06-14:
  the combined RTX ctx0 row was `181.5 / 303.0 / 459.7 / 696.2 / 989.6 /
  1444.1 / 2009.4` tok/s for C1/C2/C4/C8/C16/C32/C64. It did not stack with
  the single-backend probes and stayed `11-29%` behind Lucifer+PR3395 from C8
  through C64. The run was healthy enough for a negative result, but showed
  FlashInfer MoE autotune uncovered-shape fallbacks, runtime JIT warnings, and
  only about 63% average draft acceptance. Do not promote the naive
  linear-plus-MoE combination; move the next high-concurrency decode work back
  to attention/runtime mechanisms or the proven PR3395 route.
- Upstream Model Runner v2 check on 2026-06-13:
  `vllm-project/vllm#42667` was confirmed merged into upstream/main on
  2026-06-12 at merge commit `78739c1946cfa88fba8ccd4ca7d6c4230f816a3c`; the
  same remote check found upstream/main at
  `470229c37efaf69c86e8bc97482b0b1ff7551c65`.
- Local freeze tags:
  `sm120-freeze-vllm-upstream-main-20260612`,
  `sm120-freeze-vllm-pr45277-20260612`,
  `sm120-freeze-black-benediction-20260612`,
  `sm120-freeze-flashinfer-main-20260612`,
  `sm120-freeze-flashinfer-pr3395-20260612`,
  `sm120-freeze-b12x-master-20260612`.

## Why

EP-off beating the previous EP-on default changes the interpretation of the old
dependency experiments. A MoE or pipeline imbalance can make a backend look
neutral or bad under EP-on while still being useful under the current production
profile. The route needs fresh same-host EP-off endpoint A/B data before any old
conclusion is reused.

The stable PR branch already has broad user and harness coverage. Moving fast
on backend ideas is appropriate, but not on the PR branch itself. New code must
show one of these before promotion: fewer real sparse-MLA candidate/value
visits, better effective sparse visits/s at the same work, lower memory
pressure that expands a guarded workload, or a measurable MoE/decode-pipeline
gain without correctness or lifecycle regressions. After the 2026-06-13
stage-timing pass, the first promotion route should be sparse MLA accumulate
or backend replacement, not DFlash/decode.

The first endpoint-shaped sparse-MLA route is now the default-off indexed D512
multi-prefill expansion. On RTX it removes the 65K `num_prefills_not_1` gate
reason, reduces sparse accumulate time by `36.73%` at 65K and `44.19%` at 16K,
and improves EP-off cold-prefill C=`1/2/4` endpoint throughput. Reduced GB10
confirmation is also positive for 16K and 65K single-case runs with reboot
between cases: 16K improved `sparse_accumulate` by `-20.90%` and C=2 input
tok/s by `+15.10%`; 65K improved `sparse_accumulate` by `-19.98%` and C=2
input tok/s by `+9.07%`, with C=1 effectively flat. However, the GB10 forum53
MTP2 prefix-cache gate is not green: two initial env-on runs each had 1 marker
failure out of 4 requests, while a same-branch env-off control passed the
matrix with 4/4 requests. Response-capture follow-up did not reproduce the miss
on RTX C2, but did reproduce it on GB10 env-on. The captured failed GB10
response stopped after emitting the previous assistant status body and never
included the current marker, which points at a prefix-cache/current-suffix
context mapping bug in the env-on route rather than empty output or simple
truncation. Driver-health signals also appeared in the env-off control and
later blocked a fresh env-off capture control until reboot, so startup/post-run
GB10 memory margin is a separate open problem. Keep the route default-off until
paired/full correctness, prefix-cache-enabled lifecycle, and GB10
user/promotion gates are green. This is enough to continue debugging the route,
but not enough to make it PR-default behavior.

DFlash-style speculative/decode optimizations are treated as high-risk until
they clear GSM8K and semantic gates. RTX PRO 6000 is the development and
profiling target; GB10 validation remains mandatory before claiming a candidate
as the next user-facing baseline because GB10 is the weaker and more
memory-sensitive environment.

Breakable CUDA graph belongs in the same high-risk bucket until the GB10
semantic failure is explained. It can be evaluated as a `FULL_AND_PIECEWISE`
replacement candidate, but not while also changing sparse-prefill kernels,
dependency wheels, or the upstream runner route unless the comparison is
explicitly designed to isolate those dimensions.

Single GSM8K limit-200 runs are not sufficient as promotion proof. The first
D512 multi-prefill lifecycle run accidentally inherited the baseline driver's
8-shot default, so correctness comparison uses the paired 5-shot reruns:
multi-prefill on scored `0.965 / 0.960`, and multi-prefill off scored
`0.950 / 0.930`. That is positive relative evidence for the prototype and does
not regress the 2026-06-12 stable-preview anchor `0.965 / 0.940`, but the next
promotion step still needs paired/full correctness rather than relying on a
single limited slice.

## Reopen If

- `vllm-project/vllm#45277` merges or is replaced by another upstream SM12x
  build/runtime coverage change.
- `vllm-project/vllm#42667` or a successor changes the active DeepSeek runner
  path, CUDA graph compatibility, or EP support assumptions after rebase.
- FlashInfer exposes an official packed SM120 sparse-MLA route, PR3395 changes
  its public Python surface or build/dependency contract, or b12x exposes a
  faster DS4 compressed-MLA/indexer route that changes the prior component
  results.
- `flashinfer-ai/flashinfer#3395` changes in a way that removes the dependency
  gate or materially changes the packed SM120 sparse-MLA integration contract.
- `dev/black-benediction` publishes or moves a performance-critical mechanism
  that our local harness cannot explain.
- The Aiden image is refreshed with a KV-cache reliability fix, publishes a
  reproducible overlay diff, or changes bundled FlashInfer/b12x behavior in a
  way that could explain the GB10 prefill/decode gap.
- DeepGEMM `33a715e` or a successor becomes easy to route through the current
  vLLM MoE path, or same-host component evidence confirms the claimed EP-decode
  improvement without hurting correctness, memory margin, or GB10 stability.
- Breakable CUDA graph passes paired RTX / GB10 semantic, long-context,
  prefix-cache, lifecycle, and driver-health gates under the same runner and
  dependency stack as the `FULL_AND_PIECEWISE` control.
- A same-profile EP-off endpoint A/B contradicts the current route ordering.

## Supersedes

- This does not supersede the legacy evidence archive. It defines how to reuse
  that evidence after the EP-off default change.
