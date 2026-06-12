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
- vLLM branch/commit: PR stable preview `f32247a5a6` as the control; current
  backend-parity dev branch `codex/ds4-sm120-backend-parity-dev-20260612` at
  `7224e68417` only for opt-in diagnostics.
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

Pending. This package starts the bottleneck phase; it does not promote a new
backend.

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
are not enough. The first phase should classify the bottleneck before porting
code:

- Sparse-MLA/dataflow bottleneck: endpoint throughput improves only when real
  candidate/value visits fall or effective visits/s improves at the same work.
- MoE/pipeline bottleneck: EP-off vs EP-on, no-MTP vs MTP, and decode
  interference change endpoint behavior without changing sparse-MLA work.
- Scheduler/KV bottleneck: prefill/decode interference, prefix-cache admission,
  or CUDA graph memory pressure explains the gap.
- Dependency bottleneck: released FlashInfer or b12x cannot expose the needed
  route under the current public package stack, so the route must remain
  research-only.

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
- Next command: run RTX EP-off attribution and correctness gates first; use
  GB10 only after a candidate has an explained RTX signal.
