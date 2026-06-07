# SM120 Current State

Start here before reading the longer historical notes. This file is the compact
working entrypoint for DeepSeek V4 SM12x optimization status, current gates, and
next-step decisions. Treat `docs/sm120_optimization_notes.md` as the append-only
evidence archive.

Last updated: 2026-06-07.

## Read Order

1. Read this file for the current branch posture and next target.
2. Read `docs/vllm_correctness_gates.md` for promotion requirements.
3. Read `docs/dgx_spark_bare_metal_cluster.md` for GB10 / SM121 setup and
   reduced long-context gates.
4. Use `docs/sm120_experiment_index.md` to jump into historical experiments.
5. Use `docs/sm120_optimization_notes.md` only when you need the detailed
   artifact trail or rejected-route rationale.

## Current Posture

- PR-ready work: the D512 sparse-MLA prefill stack plus the supporting
  scheduling, workspace warmup, prefix/KV lifecycle, and correctness fixes that
  already passed promotion gates. This is the current defensible customer
  baseline for dual RTX PRO 6000 / SM120 and the reduced GB10 / SM121 envelope.
- Newly promoted work: exact chunked D512 online merge for
  `combined_topk > 1152`. It is now default-on because the RTX promotion subset,
  GSM8K limit-200, prefix/KV lifecycle checks, and GB10 reduced long-C2 gate are
  green. `VLLM_DEEPSEEK_V4_INDEXED_D512_CHUNKED_PREFILL=0` remains available as
  an emergency rollback switch.
- Dev-only work: D512 empty-tail skip, exact C128A active-width metadata
  narrowing, and sparse MLA candidate-region attribution. Empty-tail skip has
  small endpoint gains, but it must keep GSM8K limit-200 and the full promotion
  matrix green before becoming PR-branch behavior. C128A active-width narrowing
  has a positive 512K-under-1M endpoint signal and does not drop candidates, but
  it is a bounded dead-tail reduction rather than a true 1M work reduction.
  Candidate-region reporting and MQA top-k elapsed/work reporting are
  diagnostic infrastructure, not claimed performance optimizations.
- Upstream comparison point: upstream now exposes an optional
  `FLASHINFER_MLA_SPARSE_DSV4` backend, but the current official FlashInfer
  `0.6.12` wheel is not a runnable SM120/SM121 backend in this setup. The
  backend marker is selected, but both a GB10 endpoint startup smoke and a
  direct minimal FlashInfer DSV4 API call on SM120/SM121 fail in
  `TllmGenFmhaRunner` with `Unsupported architecture`.
- Blocked or rejected as current endpoint backends, in the specific forms that
  were tested: public b12x / FlashInfer wheels as a direct DS4 endpoint
  backend, upstream `FLASHINFER_MLA_SPARSE_DSV4` with the current official
  wheel, standalone C128 grouped-compressed prefill, generic D512
  selector/tile/chunk sweeps, BF16 score workspace, SWA-only routing through
  the current D512 helper, and grouped-query local-SWA tiling that keeps the
  same candidate work. A fused-stats/value D512 prototype and a
  lower-live-state value-tile prototype were also rejected because they did not
  improve GB10 and did not reduce real candidate/value visits. This is not a
  rejection of the newer local-inference-lab B12X backend stack; that line must
  be tested as a separate backend/dataflow candidate.

## Promotion Matrix

Any sparse-MLA, scheduler, workspace, or backend change that affects serving
behavior must preserve:

- GSM8K limit-200 correctness.
- CUDA graph mode `FULL_AND_PIECEWISE`; do not hide correctness issues by
  disabling full decode graph capture.
- Prefix-cache stress and KV lifecycle recoverability.
- Short throughput and 8K/1K throughput regression checks.
- 59K / 124K long-context C=1 and C=2 TTFT, decode, ITL p95/p99, and fairness.
- Mixed-arrival prefill/decode interference and streaming pressure.
- GB10 reduced long-C2 availability/cadence when the change could affect GB10,
  scheduler behavior, or sparse-MLA prefill.
- User-feedback reduced gates when the change touches the reported failure
  surface. `scripts/run_sm12x_dp_ep_oom_reduced_gate.sh` tracks the external
  DP/EP long-context JIT/OOM/worker-crash shape with reduced local defaults.
  A local pass is useful regression evidence, not proof that the full
  DP=3/256K external topology is solved.
- GB10 MTP=2 MoE TP deadlock sustained gate for the latest two-node GB10
  report. This is separate from forum53: use
  `scripts/run_gb10_mtp2_moe_tp_deadlock_gate.sh` to cover prefix cache enabled,
  MTP=2, FP8 KV, `max_model_len=200000`, `max_num_seqs=8`, and
  `FULL_AND_PIECEWISE`, with a no-token-progress watchdog and rank stack
  capture. Current clean sustained evidence uses `gpu_memory_utilization=0.80`;
  higher `0.90+` GB10 startup probes have produced current-boot NVIDIA driver
  OOM signals around CUDA graph profiling, so driver health is a first-class
  gate result rather than a post-hoc note.

Prefix-cache hits must be reported separately from cold-prefill performance.
Do not use prefix-cache-enabled numbers as cold-prefill gains.

## Current Performance Snapshot

Latest RTX PRO 6000 / SM120 dev evidence for the current D512 path is in the
low-instrumentation promotion and attribution runs recorded in
`docs/sm120_optimization_notes.md`.

- 59K C=1: about `7458 tok/s`, `7.9 s` TTFT.
- 59K C=2: about `7430 tok/s`, `12.0 s` TTFT.
- 124K C=1: about `6735 tok/s`, `18.4 s` TTFT.
- 124K C=2: about `6739 tok/s`, `27.6 s` TTFT.

The D512 retune produced a useful but bounded improvement: roughly `+6%`
input tok/s / `-6%` TTFT over the prior stable default, with dev-only
empty-tail skip adding another small endpoint gain in some 59K/124K shapes.
This did not close the GB10 raw-prefill gap.

GB10 / SM121 remains the main uncertainty. Current GB10 attribution shows much
lower effective sparse visits/s than RTX, and the Reddit / unholy-fusion report
is still materially ahead in GB10 prefill. Repeated startup/API probes say the
official `FLASHINFER_MLA_SPARSE_DSV4` route is blocked on the current
FlashInfer wheel, and both SM120 and SM121 direct API calls show the same
`Unsupported architecture` failure.

External feedback on 2026-06-07 strengthens the GB10 prefill-gap concern: a
NVIDIA Developer Forums report for the local-inference-lab / unholy-fusion
line lists C=1/C=2/C=4 prefill around `1.9k tok/s` and decode sweet spot around
`52 tok/s`, while calling the B12X FP8 variant the winner. Treat that as an
external target, not as locally reproduced evidence. The current local finding
is that the gap is backend/dataflow-shaped, not explained by serving flags
alone.

The current-default versus Reddit-style GB10 matrix covered 4K, 16K, 32K, 64K,
and 128K cold prefill with prefix cache disabled, MTP=2, EP enabled, FP8 KV,
and `FULL_AND_PIECEWISE`. `max_num_batched_tokens=8192` is a narrow latency
tradeoff, not a default profile: it was flat at 4K, about `3%` better at 16K,
about `6-8%` better at 32K/64K, and effectively flat again at 128K while
worsening p99 ITL. It also cut 131K KV-cache concurrency from roughly
`3.0x` to roughly `1.35-1.46x`. This does not explain the public
Reddit-scale prefill gap.

## Active Direction

The next high-value target is split into two measurement tracks before more
production code is added:

1. Establish a 512K / 768K / 1M context frontier baseline on SM120 and GB10.
   This is a development observation gate, not a normal PR hard gate. Use
   `scripts/run_sm12x_very_long_context_frontier.sh` or the
   `very_long_context_capacity` baseline phase to record startup capacity,
   KV-cache bytes/token, C=1 cold/warm TTFT, input tok/s, decode tok/s, ITL
   p95/p99, runtime health, and GPU stats with prefix cache disabled and
   `FULL_AND_PIECEWISE` CUDA graphs still enabled.
   The first 2026-06-06 frontier baseline shows dual RTX PRO 6000 can admit and
   complete 1M C=1 with positive KV margin, but 1M cold TTFT is about `845s`.
   GB10 can admit and complete 1M C=1 only after raising the current MTP=2
   profile from `gpu_memory_utilization=0.70` to `0.75`, and measured 1M cold
   TTFT is about `3504s`, so GB10 1M is currently an availability probe rather
   than an interactive-latency claim.
   The first RTX 512K/1M Nsys attribution pass confirms the very-long TTFT
   problem is prefill kernel work rather than host/scheduler idle: 512K had max
   CUDA idle gap `0.103s`, and the partial 1M trace had max idle gap `0.018s`.
   `_accumulate_indexed_attention_chunk_multihead_kernel` and
   `_fp8_mqa_logits_kernel` dominated the trace, reaching about `75%` of 512K
   CUDA kernel time and about `83%` of the partial 1M trace. The 1M Nsys run
   failed before first token in the FP8 MQA logits/top-k path with CUDA OOM
   under profiler memory pressure, so use it as attribution evidence, not as a
   completed 1M latency sample.
2. Continue the GB10 long-prefill performance gap work, measured before more
   production code is added:

- The apples-to-apples GB10 C=1 default-versus-Reddit-style serving-flag matrix
  is now recorded for 4K / 16K / 32K / 64K / 128K. Do not promote the 8192
  chunk profile by default; keep it as an opt-in latency/capacity tradeoff.
- Do not spend more endpoint time on explicit upstream
  `FLASHINFER_MLA_SPARSE_DSV4` until the public FlashInfer stack advertises and
  passes an SM120/SM121 DS4 sparse MLA direct-API smoke first, then an endpoint
  startup smoke.
- Re-audit and A/B the latest local-inference-lab `main` and
  `dev/unholy-fusion` before the next GB10 backend experiment. The promising
  pieces are B12X sparse MLA, B12X sparse indexer / compressed-indexer copy
  avoidance, native B12X MoE and mHC routing, plus the inherited PR 43477
  scratch fixes. The Model Runner V2 enablement alone is unlikely to explain
  the prefill gap, but it may be required for that stack's warmup/scratch
  compatibility.
- Use `scripts/run_gb10_b12x_backend_ab_matrix.sh` for that comparison. It
  wraps the existing GB10 prefill-gap gate and takes semicolon-separated
  `GB10_B12X_AB_TARGETS` entries in
  `label|vllm_root|vllm_venv|profiles|variants|env_file` form, so fork-specific
  backend flags can live in ignored local env files instead of tracked docs.
- The first controlled GB10 smoke against the refreshed local-inference-lab
  stack did not complete a request with public dependencies. It progressed far
  enough to prove that B12X FP8 linear, B12X MoE, the sparse indexer, and
  `B12X_MLA_SPARSE` can be selected, but failed on public dependency/backend
  gaps: released b12x before `0.20.0` lacks the expected FP8 linear module,
  the full B12X FP8 linear path needs a CUTLASS DSL MMA symbol not present in
  public `4.5.2`, and the tested fallback scaled-mm paths were not usable on
  GB10. Keep this route as blocked/recheck, not rejected, until the dependency
  stack can pass a small endpoint smoke.
- A later public recipe for the Aiden image explains why the above smoke is not
  equivalent to the reported working stack. The image is an offline micromamba
  build with a local FlashInfer wheel, an installed vLLM overlay, and a bundled
  b12x source tree that includes the compressed indexer / sparse MLA / FP8
  linear modules missing from earlier public-wheel probes. Treat this as a
  separate "Aiden image parity" route. Before any port, first reproduce the
  image recipe on GB10 and diff the overlay against upstream/current Dev.
- Revisit older rejected-note wording when using it to guide new work. The
  prior negative results remain valid for public-wheel direct API probes,
  simple serving-flag changes, selector-only swaps, and local split-launch
  grouped-query prototypes. They do not prove that local-inference-lab's custom
  B12X sparse MLA/indexer/MoE/mHC dataflow cannot win.
- Keep prefix-cache-on and prefix-cache-off results separate.
- Record backend selection, MoE path, NCCL/all-reduce path, sparse candidate /
  value attribution, TTFT, input tok/s, decode tok/s, and ITL p95/p99.

If a maintainable upstream or official backend wins and passes the promotion
matrix, prefer that route over carrying fork-specific kernel code. If no public
backend wins, the next production-worthy experiment must reduce real
sparse-MLA candidate/value/logits work, live state, memory pressure, or
dependency depth for the DS4 mixed compressed-plus-SWA metadata shape. Do not
prioritize scheduler-idle fixes or `_combine_topk_swa_indices_kernel` for the
512K-to-1M TTFT nonlinearity unless future profiling contradicts the current
Nsys attribution.

Upstream DeepSeek backlog triage should run before adding more local sparse-MLA
code. The current order is:

1. Check stability and semantic fixes that overlap known user reports:
   DeepSeek V4 DBO prefill metadata preservation, prefix-cache retention /
   KV lifecycle behavior, CUDA graph / MLA metadata correctness, and SM12x
   crash workarounds.
2. Follow upstream simplification and KV-cache layout work when rebasing:
   DeepSeek V4 attention refactors, NVIDIA-only cleanup, model-specific
   KV-cache planning, and contiguous KV packing. Prefer aligning with these
   designs over preserving local compatibility shims.
3. Treat upstream official FlashInfer / TRTLLM sparse-MLA work as blocked for
   SM120 / SM121 until a direct DS4 sparse-MLA FlashInfer API smoke passes on
   the target architecture. Do not re-enter endpoint tests first.
4. Keep PCP / DCP / context-parallel prefill as a four-card or larger-topology
   research track, not a dual-card default-optimization path.
5. Only after the above checks are clean, return to new candidate/value-work
   reduction experiments.

Latest focused microbench / NCU follow-up keeps this direction intact. On RTX
PRO 6000, the D512 score kernel for the mixed C128/SWA shape is limited by low
eligible-warps / long-scoreboard behavior and shared-memory-limited occupancy,
while the value kernel is already near the GDDR7 DRAM roof. On GB10, `sudo ncu`
shows both score and value are dominated by low eligible-warps and L1TEX
long-scoreboard stalls rather than peak bandwidth. Candidate-length scaling is
close to linear on both systems. This means a grouped launch or index-generation
shortcut that keeps the same semantic candidates is unlikely to close the gap;
the useful work must reduce effective score/value visits or use a backend with
real cross-query KV reuse for the DS4 layout. The latest fused-stats/value and
lower-live-state D512 microbench confirmed this: RTX saw at most a small
microbench-only fused win, while GB10 regressed.

The current research hypothesis is therefore cross-query KV reuse for the C128A
DS4 sparse-MLA metadata layout. Harness stats reporting now derives
`cross_query_reuse_potential` from sampled candidate overlap so prototype work
can first prove reusable candidate mass before any endpoint code is added. Treat
that field as an upper-bound signal only: it is not a performance claim until a
microbench and then the endpoint promotion matrix show an actual win.

Latest dev-only C128A active-width result: for a 1M `max_model_len` profile with
an actual 512K prompt, narrowing the returned C128A top-k metadata view to the
current compressed-position width reduced cold TTFT from the no-cap reference
`234.965s` to `221.435s` and improved input throughput from `2231.30` to
`2365.15 tok/s` on dual RTX PRO 6000. This is exact-preserving because the width
is aligned to cover every current token's compressed candidate range. It should
help prompts materially below the configured model-length ceiling, but it cannot
help a true 1M prompt where the effective width equals the full configured
width. The first RTX prefill/decode promotion subset passed with zero
regressions across 59K/124K C=1/C=2, decode concurrency, mixed arrival, and
streaming pressure. Keep it behind the full promotion matrix until short
throughput, prefix/KV lifecycle, GSM8K, and GB10 reduced long-C2 are rechecked.

Latest promoted exact chunked D512 result: for wide indexed D512 sparse-MLA
prefill shapes with `combined_topk > 1152`,
`VLLM_DEEPSEEK_V4_INDEXED_D512_CHUNKED_PREFILL=1` is now the default. It chunks
candidate lists through the existing D512 split primitive and performs exact
online softmax-state merge. On dual RTX PRO 6000, with TP=2, MTP=2, EP enabled,
FP8 KV, prefix cache disabled, `FULL_AND_PIECEWISE`,
`max_model_len=1048576`, and `max_num_batched_tokens=4096`, it improved:

- 512K C=1 cold TTFT from `237.183s` to `147.144s`
  (`-38.0%`), input throughput from `2210.51` to `3563.19 tok/s`.
- 768K C=1 cold TTFT from `490.869s` to `315.884s`
  (`-35.6%`), input throughput from `1602.12` to `2489.65 tok/s`.
- 1.04M C=1 completed at `496.200s` TTFT and `2095.93 tok/s`; same-protocol
  control was not rerun in this pass.

The reduced RTX promotion evidence is encouraging: GSM8K limit-200 passed
with flexible/strict `0.955` / `0.935`, story recall matched all 16 semantic
assignments, prefix-cache stress passed, prefix-disabled KV lifecycle returned
to `0.0%` idle KV after complete and aborted requests, and reduced
59K/124K/mixed-arrival/streaming gates reported zero regressions. A
prefix-cache-enabled lifecycle run failed an absolute `5%` idle-KV threshold
after a prior prefix-stress phase; treat that as a threshold composition issue
for retained prefix-cache blocks, not as a leak signal.

GB10 / SM121 reduced long-C2 passed on an aligned checkout. The first aligned
run explicitly forwarded the chunked D512 env into both vLLM processes, and the
follow-up default-on run confirmed the same route works without setting the env:

- `mtp2`: 4/4 requests, max TTFT `155.023s`, ITL p99 `0.073877s`,
  zero failures, zero preemptions, prefix hits `0`.
- `nomtp`: 4/4 requests, max TTFT `149.993s`, ITL p99 `0.052599s`,
  zero failures, zero preemptions, prefix hits `0`.
- Final default-on rerun after workspace reservation and zero-lens merge
  guard: `mtp2` 4/4 requests, max TTFT `154.555s`, ITL p99 `0.075123s`;
  `nomtp` 4/4 requests, max TTFT `149.155s`, ITL p99 `0.052108s`; zero
  failures, zero preemptions, prefix hits `0`.

This is also materially better than the 2026-06-01 GB10 wrapper reference
(`mtp2` `229.923s` / `0.479s`, `nomtp` `229.434s` / `0.596s`). Continue to keep
GB10 reduced long-C2 in the promotion matrix for future sparse-MLA changes.

Forum #53 GB10 multi-user prefix-cache smoke, 2026-06-07: the reported
multi-user admission/fairness problem is reproducible on the current PR branch.
With TP=2, no-MTP, prefix cache enabled, `max_model_len=262144`,
`max_num_seqs=8`, `max_num_batched_tokens=6144`, and a C=6 streaming-pressure
shape, all six requests completed, but runtime metrics showed
`running_requests_max=1`, `waiting_requests_max=5`, max TTFT `356.230s`, and
ITL p99 `0.052558s`. That points at scheduler/KV admission and long-prefill
queueing rather than decode cadence. The dedicated harness entry is
`scripts/run_gb10_forum53_multi_user_gate.sh`; use it to sweep
`max_num_batched_tokens=2048,3072,4096,6144,8192` and compare C=6/C=8 before
changing vLLM scheduling behavior.

The first C=6 no-MTP sweep completed after rebooting once to clear a driver OOM
log left by an earlier combined sweep attempt. Final clean-boot C=6 data:

| max_num_batched_tokens | Requests | Failures | Max TTFT | ITL p99 | running max | waiting max | KV max |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `2048` | `6` | `0` | `370.940s` | `0.052921s` | `1.0` | `5.0` | `8.58%` |
| `3072` | `6` | `0` | `361.843s` | `0.042915s` | `1.0` | `5.0` | `9.99%` |
| `4096` | `6` | `0` | `350.376s` | `0.051967s` | `1.0` | `5.0` | `11.20%` |
| `6144` | `6` | `0` | `356.230s` | `0.052558s` | `1.0` | `5.0` | `14.12%` |
| `8192` | `6` | `0` | `352.118s` | `0.051635s` | `1.0` | `5.0` | `17.18%` |

Lowering `max_num_batched_tokens` did not restore active concurrency. Treat
this as a scheduler/admission or KV-budgeting investigation, not as another
chunk-size tuning problem.

Persistent TODO: the next production-class prefill improvement must reduce
long-prefill sparse-MLA real work or memory pressure, especially in
`_accumulate_indexed_attention_chunk_multihead_kernel` and the FP8 MQA
logits/top-k path. Scheduler shaping and chunk-size tuning remain fallback
controls, not the main route to close the 512K/1M TTFT and GB10 prefill gap.
The rejected 2026-06-06 C128 metadata-stage cap confirms this boundary: C128
sparse accumulate improves, but 512K/1M MQA top-k work remains in the C4A
indexed D512 path. The cap deliberately drops C128 candidates, does not reduce
MQA top-k, and has been removed from the code path. The next attribution target
is C4A MQA/logits/top-k and sparse-accumulate value traffic reduction rather
than more C128 metadata slicing.

The first no-cap work-only attribution after removing the C128 cap keeps that
direction. On RTX PRO 6000, 59K / 124K / 512K C=1 showed effective sparse
visits per prompt token rising from about `41.6K` to `51.9K` to `114.6K`,
while MQA logits elements per prompt token rose from about `340K` to `677K`
to `2.78M`. The 512K run materialized about `5.82TB` of MQA logits and
estimated about `61.5TB` of sparse-accumulate value reads. That means the
512K/1M problem is real work growth, not a scheduler-idle artifact. A quick
full-logits versus chunked-MQA microbench also showed the existing chunked path
is slower (`1.4-1.5x` at 32K-131K KV for the endpoint-like 256-query,
32-head, topk-512 shape), so do not re-enter simple MQA chunking. A useful MQA
experiment must fuse logits generation with top-k selection or otherwise
avoid writing/reading the logits matrix without adding extra merge launches.
The 512K MQA stats were also reprocessed with explicit valid/logits accounting:
valid KV visits were `1.443T` out of `1.455T` logits elements, so logits
padding was only about `0.79%`. Do not prioritize simple valid-span clipping or
row-block mask early-exit as a primary 512K optimization route.
The first Triton exact tile-local topK feasibility probe also does not justify
endpoint work: `tl.topk` returns values but not indices, the threshold+cumsum
index recovery path hits shared-memory limits at the useful `M=16,N=1024` and
`M=8,N=2048` shapes, and wide-N MQA logits tiles either exceed shared memory or
run slower than the current `M=64,N=128` logits kernel. Treat Triton tile-local
fused MQA topK as blocked until there is an indexed selection primitive or a
backend that keeps current tensor-core tiling while avoiding full logits
materialization.
The follow-up vLLM top-k primitive audit keeps the same boundary: existing
`top_k_per_row_prefill`, `persistent_topk`, and the FlashInfer-derived
`FilteredTopKRaggedTransform` are selectors over an already materialized
float32 logits matrix. They can improve selection behavior, but they cannot
remove the 512K-scale MQA logits write/read by themselves. Do not start a new
optimization by swapping only the selector. A useful MQA route must fuse FP8
MQA score generation with indexed top-k selection, or use an official backend
that does the equivalent for the DS4 sparse metadata shape.
A scratch no-store MQA logits probe also limits this route: keeping the same
QK/ReLU/weighted score work but replacing the full logits store with per-tile
checksums was only about `0.8%` faster at 32K KV and `2.3%` faster at 131K KV
on the endpoint-like 256-query, 32-head, topk-512 shape. Avoiding the logits
matrix write/read is not enough by itself. A useful fused MQA producer must
reduce real score work, candidate/value visits, live state, or dependency
depth, not merely move the same score work into a different output format.
The first real-model weight-sign diagnostic also rules out a tempting exact
pruning shortcut: C4A MQA scores accumulate `ReLU(q*k)*weight_h`, and
`weight_h` is an unconstrained linear projection output folded with q-scale and
softmax/head scales. A 4K RTX attribution smoke found about `44.1%` negative
MQA top-k weights, so head-wise early-stop or monotonic upper-bound pruning
that assumes non-negative weights is not correctness-safe.
A follow-up positive-score upper-bound diagnostic tested the safer signed
variant: first compute positive-weight heads for all candidates, then use the
positive score as an upper bound before evaluating negative heads. Under a
tie-safe exact top-k rule, 4K retained every sampled candidate and 32K retained
nearly every sampled candidate; the optimistic work ratio was about `0.997x`
at 32K before counting the extra pass overhead. Do not pursue this pruning
route as a production kernel.
A scratch head-split MQA logits probe also failed to justify endpoint work:
splitting 64 heads into multiple launches preserved exact logits but made the
32K/131K KV microbench slower even at the coarsest two-launch split. Extra
logits read/write traffic and launch overhead outweighed any live-state relief.

The first follow-up grouped-combined microbench did not win. It removed the
old separate compressed/SWA state merge by writing grouped-compressed and SWA
scores into one combined score workspace, then using one full stats pass and
separate compressed/SWA value passes into one output. The extra split launches
and loss of current head-block reuse still outweighed the compressed KV reuse
on both RTX PRO 6000 and GB10, and a wider grouped score tile exceeded GB10
shared memory. Do not reintroduce this split-launch grouped-combined route.
Future cross-query reuse work must be tighter: fewer effective score/value
visits, less value traffic, or a single/fused backend that preserves current
head reuse and avoids extra merge or split value launches.

A narrower single-launch grouped full-score probe also did not win. It kept
the current stats/value path and only replaced score materialization, reusing
compressed KV across query rows inside one score launch and conservatively
falling back for the small SWA tail. On RTX PRO 6000, the corrected
`1024 compressed + 128 SWA` C128A shape regressed from about `0.797-0.798 ms`
split total to `0.891-1.522 ms` across token/head group tiles. The best tile
still made score slower (`0.321 -> 0.414 ms`) and did not touch value traffic.
Do not continue grouped-score-only work unless it also reduces value traffic
or preserves current head-block reuse without losing occupancy.

A two-pass grouped-union replay probe also did not win. It traversed a
group-level union of C128A candidates, computed per-row grouped stats without
writing the full score workspace, then replayed the same union for value
accumulation. The shape had high theoretical reuse, but the value pass had to
recompute QK scores and use smaller grouped tiles to fit shared memory. On RTX
PRO 6000 it reached only about `0.33x` of the current D512 split path at the
target `1024 compressed + 128 SWA` shape; on GB10 the best reduced probe was
about `0.74x`. Do not continue two-pass grouped replay. Future fused C128A
work must avoid score replay and preserve the current split path's head reuse,
or reduce effective value traffic inside a single backend.

A follow-up exact row-dedup diagnostic also found no current opportunity: the
new opt-in `candidate_row_duplicates` stats field reported `0` duplicate
candidate visits across `1408` sampled rows in a 4K RTX attribution smoke, both
overall and within compressed/SWA regions. Do not spend kernel time on
same-row duplicate elimination unless a future stats run shows non-zero
duplicate visits.

## Known Limits

- GB10 reduced long-C2 validates availability and token cadence only. It is not
  a 256K / 512K / 1M throughput claim.
- Dual RTX PRO 6000 covers roughly the 128K / 131K development envelope. Larger
  context and four-card claims require target-topology gates.
- Long+long C=2 fairness remains a promotion gate. It is not the current raw
  prefill research target, but regressions must block promotion.
- Ineffective experiments should be removed from vLLM code and recorded in the
  rejected notes rather than left as switches or dormant code paths.
