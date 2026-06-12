# EP-Off Bottleneck Map

Status: watchlist
Date: 2026-06-12
Owner/context: next-stage SM120/SM121 performance parity work

## Question

Under the current EP-off serving profile, which subsystem explains the gap
between the validated PR stable preview and the strongest external
black-benediction / unholy-fusion line: sparse-MLA dataflow, b12x/FlashInfer
backend availability, MoE kernels, decode/speculative pipeline balance, or
scheduler/KV admission behavior?

## Profile

- Hardware: dual RTX PRO 6000 / SM120 for development and profiling first;
  two-node GB10 / SM121 for final confirmation and user-feedback gates.
- vLLM branch/commit: PR stable preview `f32247a5a6` as the control;
  backend-parity diagnostic base `591b71bed0`; current code-bearing dev branch
  `codex/ds4-sm120-pr3395-packed-dev-20260613` at `741ea24c46` for the
  default-off indexed D512 multi-prefill prototype.
- Dependency or image identity: vLLM upstream/main `b7f9b6a`,
  FlashInfer upstream/main `d65c3eb`,
  `flashinfer-ai/flashinfer#3395` head `88539d03`, b12x master `fabb087`,
  `local-inference-lab/vllm dev/black-benediction` `c6b2a7b`, and
  `vllm-project/vllm#45277` head `e57d3b78` as checked on 2026-06-12.
- TP / PP / EP: TP=2, PP=1, EP disabled by default. EP-on is a comparison
  dimension only.
- MTP: MTP=2 for production-path profiling. Disable MTP only to isolate a
  pipeline or MoE bottleneck.
- FP8 KV: enabled.
- Prefix cache: disabled for cold-prefill attribution; enabled only for
  user-feedback and multi-user gates.
- CUDA graph mode: `FULL_AND_PIECEWISE`.
- `max_model_len`: 131072 on dual RTX routine gates; GB10 uses guarded script
  defaults unless a profile explicitly overrides it.
- `max_num_seqs`: 4 on RTX long-context gates; GB10 forum53 default is 2.
- `max_num_batched_tokens`: 4096 default; 8192 only as explicit A/B.
- Other route flags: record all sparse-MLA, FlashInfer, b12x, DFlash, and MoE
  env vars in `artifacts.md` for every run.

## Result

First RTX EP-off attribution and stage-timing evidence captured. This package
does not promote a new backend.

Latest RTX attribution artifact:
`artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_bottleneck_attribution/20260613000055`.

Summary:

- vLLM dev commit: `591b71bed0`.
- EP: off; MTP=2; prefix cache disabled; stage timing disabled.
- Exit: OK; every `4096/16384/65536/124000` input length passed
  server startup and C=`1/2/4` random prefill sweep.
- Sparse stats are present for all lengths: row counts
  `2370 / 8706 / 34050 / 64850`.
- 124K C=4 is reliable in this shape but slow: mean TTFT `66063.01 ms`,
  p99 TTFT `81513.1 ms`.

Latest RTX stage-timing artifact:
`artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_stage_timing_attribution/20260613_stage_timing_epoff_16k_65k`.

Stage timing keeps the bottleneck squarely in sparse MLA accumulate:

- 16K: `sparse_accumulate` is `19310.6 ms` of `20689.5 ms` (`93.33%`),
  with `2.789438 ms` per million effective visits.
- 65K: `sparse_accumulate` is `51343.7 ms` of `53144.1 ms` (`96.61%`),
  with `1.519574 ms` per million effective visits.
- Non-indexed `mla_prefill_chunk` groups are much slower than indexed D512
  groups. At 65K, chunk groups are about `1.79e8-2.12e8` visits/s while
  indexed D512 groups are about `1.09e9-1.28e9` visits/s.

The first NCU microbench artifact is
`artifacts/main/2x_rtx_pro_6000_sm120/sm120_sparse_mla_ncu_first/20260613_sparse_mla_ncu_first`.
For `tokens=1024`, `candidates=640`, staggered lens, the profiled kernel used
`118` registers/thread, reached `32.60%` achieved occupancy, `61.91%` SM
throughput, `6.17%` DRAM throughput, and reported `46.36%` no-eligible cycles.
Treat this as a kernel-shape clue, not endpoint proof by itself.

The first RTX target venv route probe is
`artifacts/main/2x_rtx_pro_6000_sm120/b12x_stack_probe/20260613_route_probe_sm120`.
It showed `b12x` package `0.15.2`, FlashInfer packages `0.6.12`, and only these
relevant runtime routes as immediately available:
`runtime_flashinfer_mla_sparse_dsv4_plain` and
`runtime_flashinfer_b12x_moe`.

The follow-up dependency refresh is recorded under
`artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/`.
Default `b12x==0.20.0` resolution is not usable for this dev venv because it
moved Torch/Triton/CUDA runtime packages, downgraded NCCL, and made `vllm._C`
fail with a Torch ABI symbol error. Restoring the original runtime packages and
installing `b12x==0.20.0` as a no-deps experiment variable gives a healthy
target venv: `vllm._C` imports, focused SM120 fallback tests pass, and public
b12x DS4 compressed-MLA / sparse-indexer-extend / native MXFP4 MoE helper APIs
are importable. Current vLLM still lacks runtime hooks for those routes.
The first FlashInfer `0.6.13rc1` no-deps probe only showed that the installed
`flashinfer-jit-cache==0.6.12+cu130` tripped FlashInfer's version check; the
correct bypass variable is `FLASHINFER_DISABLE_VERSION_CHECK=1`. Installing the
matching `flashinfer-jit-cache==0.6.13rc1+cu130` makes the rc wheel pair import
without a bypass, and the RTX dev venv now keeps that matched rc1 state for
component probing. Official rc1 is not expected to expose
`flashinfer.sparse_mla_sm120`; that module lives in the unmerged PR3395 fork
branch, currently `lucifer1004/flashinfer:sparse-mla-sm120`. The matched rc1
state is therefore a healthy official-wheel baseline, while the packed SM120
sparse-MLA route remains a separate fork dependency.

The refreshed component probes do not make public b12x compressed MLA the next
endpoint route. On RTX `real_c128`, b12x compressed MLA measured `0.432 ms`
versus current D512 split+finish `0.209 ms`. The stronger fork-independent
signal remains the grouped stream family: grouped-SWA D512 was `0.824 ms`
versus split `1.382 ms` at `1152` candidates, and the high-reuse grouped-stream
probe was `0.600 ms` versus split `1.320 ms`. Because the older separate-launch
grouped-SWA endpoint regressed, the next prototype must fuse stream processing
with merge/finish or otherwise avoid the extra launch/workspace traffic.

The first fork-independent endpoint prototype is the env-gated
`VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` expansion. It does not depend
on FlashInfer PR3395. On RTX, the same-profile stage-timing A/B moved more
work from the slow non-indexed `mla_prefill_chunk` path onto the indexed D512
path:

- 16K: `mla_prefill_chunk` rows `2432 -> 1284`,
  `mla_prefill_indexed_d512` rows `2050 -> 3198`,
  `sparse_accumulate` `21219.8 ms -> 11843.0 ms` (`-44.19%`).
- 65K: `mla_prefill_chunk` rows `3788 -> 1820`,
  `mla_prefill_indexed_d512` rows `13366 -> 15334`, and the
  `num_prefills_not_1` gate reason `1968 -> 0`,
  `sparse_accumulate` `54004.1 ms -> 34165.9 ms` (`-36.73%`).
- Endpoint input tok/s improved at 16K by C=`1/2/4`
  `+5.16% / +19.52% / +29.78%`, and at 65K by
  `+6.53% / +13.03% / +12.72%`.

The first RTX lifecycle gate for that prototype passed `prefix_cache_probe`
and `kv_lifecycle_probe`. Its initial GSM8K slice accidentally inherited the
baseline driver's 8-shot default, so correctness comparison uses the later
paired 5-shot limit-200 runs instead: multi-prefill on scored
flexible/strict `0.965 / 0.960`, while the same-environment multi-prefill-off
control scored `0.950 / 0.930`. Both passed the fixed floors, and the
prototype does not show a correctness regression against the paired control or
the 2026-06-12 stable-preview anchor `0.965 / 0.940`.

GB10 reduced confirmation is positive for 16K and 65K when run as one case per
boot. On SM121 GB10 x2, the 16K C=`1/2` paired run reduced
`sparse_accumulate` `53976.9 ms -> 42695.2 ms` (`-20.90%`) and improved C=2
input tok/s `1299.03 -> 1495.23` (`+15.10%`). The 65K paired run reduced
`sparse_accumulate` `172870.3 ms -> 138329.5 ms` (`-19.98%`) and improved C=2
input tok/s `1277.57 -> 1393.42` (`+9.07%`) while leaving C=1 effectively
flat.

The same prototype does not pass the GB10 forum53 MTP2 prefix-cache gate. Two
initial env-on runs produced 1 marker failure out of 4 requests and dirty
post-run driver health. A same-branch env-off control completed the matrix
itself with 4/4 requests and 0 failures, but also produced post-run
driver-health signals. Follow-up response-capture runs then showed RTX C2
env-on/off passing 4/4, while GB10 env-on remained nondeterministic: one
capture pass was green and the repeat failed 1/4. The failed GB10 response was
not empty or truncated; it stopped after emitting the previous assistant status
body without the current marker. Treat this as a GB10 prefix-cache/current
suffix context-mapping bug in the env-on route and as a promotion blocker for
this prototype. Treat the driver-health signals as a separate GB10
memory-margin problem that must be understood before using these forum53 reruns
as clean positive evidence. Keep using reboot-safe single-case GB10 attribution
runs until the post-run NVRM OOM state is understood or avoided.

Follow-up commit `d85821b8c4` narrows the risky surface by rejecting indexed
D512 multi-prefill for multi-request cached-prefix extend rows while preserving
single-request D512 and true cold multi-prefill. On the same GB10 forum53 C2
MTP2 prefix-cache shape, the guard produced two matrix passes with 4/4
requests and 0 failures. This is positive correctness-guard evidence for the
prefix-cache marker failure. It is not a clean GB10 promotion gate: the worker
still logged NVRM OOM during full-model load, including after reducing GPU
memory utilization from `0.685` to `0.678`. The next GB10 reliability task is
to separate nonfatal full-model-load NVRM OOM from actual inference failure, or
find a launch profile that keeps driver health clean without falling below the
80K forum53 context requirement.

The earlier artifact
`artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_bottleneck_attribution/20260612233142`
is performance-only evidence. Do not use it for sparse-MLA attribution because
the dev branch was missing the sparse stats diagnostics and wrote zero stats
rows.

Baseline anchors are inherited from
`docs/sm120/experiments/2026-06-12-epoff-backend-revalidation/`:

- RTX EP-off MTP cold OSL=1 prefill input tok/s for
  `1024/4096/16384/65536`: `6606.45 / 6206.06 / 8056.05 / 7540.46`.
- RTX EP-off MTP OSL=128 supplement input tok/s for `4096/16384/65536`:
  `3123.74 / 6209.00 / 7049.72`; output tok/s:
  `97.60 / 48.51 / 13.77`.
- RTX GSM8K 5-shot limit-200: flexible `0.965`, strict `0.940`, exit `0`.
- GB10 forum53 MTP2 EP-off C=2 prefix-cache gate: 4/4 requests, 0 failures,
  max TTFT `124.045698 s`, ITL p99 `0.144954 s`, clean driver health.

## Interpretation

EP-off currently wins the routine profile, so old EP-on dependency conclusions
are not enough. The first stage-timing pass classifies the immediate
bottleneck as sparse MLA accumulate rather than scheduler/KV admission:

- Sparse-MLA/dataflow is the first optimization route. A candidate should
  either reduce real candidate/value visits or improve effective visits/s at
  the same semantic work.
- The env-gated D512 multi-prefill expansion is still useful as a
  fork-independent performance candidate, but it is blocked for promotion by
  the GB10 forum53 MTP2 prefix-cache and driver-health gates. Commit
  `d85821b8c4` fixes the observed marker-failure shape by excluding
  multi-request cached-prefix extend rows, but the route remains default-off
  until paired correctness, prefix-cache-enabled lifecycle, and clean GB10
  user/promotion gates are green.
- Public b12x readiness has moved from "missing APIs" to "not yet integrated
  or not fast enough as a direct endpoint route." Keep b12x `0.20.0` no-deps
  available for component probes, but do not port public compressed MLA
  directly while it loses to current D512 split+finish.
- Official FlashInfer `0.6.13rc1` plus matching
  `flashinfer-jit-cache==0.6.13rc1+cu130` is usable in the RTX dev venv and
  imports without `FLASHINFER_DISABLE_VERSION_CHECK=1`. It exposes the plain
  DSV4 sparse-MLA and B12X MoE routes; the PR3395-style packed SM120 sparse-MLA
  module belongs to the `lucifer1004/flashinfer:sparse-mla-sm120` fork branch
  until that work merges upstream.
- Treat `flashinfer-jit-cache` as optional for source/git FlashInfer
  experiments. If a git checkout conflicts with the installed jit-cache
  package, prefer removing the cache package and running enough warmup before
  reading performance rather than forcing a mismatched cache into the venv.
- MoE/pipeline and scheduler/KV remain comparison dimensions, but the current
  EP-off cold-prefill evidence does not make them first-order bottlenecks.

Correctness is a hard constraint, not a final polish step. DFlash-style
speculative/decode optimizations are treated as high-risk until GSM8K
limit-200 and semantic/user gates stay green. A speed gain that lowers GSM8K
below the gate is rejected for PR promotion.

## Follow-Up

- Create or update decision:
  `docs/sm120/decisions/watchlist/2026-06-12-backend-parity-roadmap.md`.
- Preflight:
  `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/preflight.md`.
- Latest sanitized preflight result:
  `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/preflight-results.md`.
- Rerun trigger: upstream CUDA arch coverage merge, relevant FlashInfer/b12x or
  black-benediction head change found during explicit upstream review, or any
  endpoint candidate that changes sparse-MLA, MoE, DFlash, scheduler, KV, or
  CUDA graph behavior.
- Next command: treat `d85821b8c4` as the current correctness-guard candidate
  and decide whether the worker full-model-load NVRM OOM is a launch-profile
  problem or a harness driver-health accounting problem. Do not promote the
  route on GB10 until a clean forum53/user gate exists. In parallel on RTX,
  prototype or microbench a fused dual-stream sparse-MLA path that preserves
  the grouped-stream component signal without reintroducing the
  separate-launch merge/finish overhead that made the earlier endpoint form
  regress.
