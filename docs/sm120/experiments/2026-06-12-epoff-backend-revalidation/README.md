# EP-Off Backend Revalidation

Status: watchlist
Date: 2026-06-12
Owner/context: next-stage SM120/SM121 backend parity work

## Question

Under the current EP-off default profile, which backend route can close the gap
to the strongest external implementation without regressing the validated PR
stable preview?

## Profile

- Hardware: dual RTX PRO 6000 / SM120 first, two-node GB10 / SM121 second.
- vLLM branch/commit: stable preview `f32247a5a6` for baseline; research
  branches must state their exact commit.
- Dependency or image identity: vLLM upstream/main `b7f9b6a`,
  FlashInfer upstream/main `d65c3eb`,
  `flashinfer-ai/flashinfer#3395` head `88539d03`, b12x master `fabb087`,
  `local-inference-lab/vllm dev/black-benediction` `c6b2a7b`, and
  `vllm-project/vllm#45277` head `e57d3b78` as checked on 2026-06-12.
- TP / PP / EP: TP=2, PP=1, EP disabled by default; EP enabled only as an
  explicit A/B dimension.
- MTP: MTP=2 for production-path checks; no-MTP only for isolated diagnosis.
- FP8 KV: enabled.
- Prefix cache: disabled for cold-prefill/backend attribution; enabled for
  user-feedback and multi-user gates.
- CUDA graph mode: `FULL_AND_PIECEWISE`.
- `max_model_len`: 131072 on dual RTX routine gates; GB10 gates use the
  guarded script defaults unless a profile says otherwise.
- `max_num_seqs`: 4 for RTX routine long/throughput checks unless the gate
  specifies otherwise; GB10 forum53 default is 2.
- `max_num_batched_tokens`: 4096 default; 8192 only as explicit tuning A/B.
- Other route flags: record all FlashInfer/b12x/backend env vars in
  `artifacts.md` for every run.

## Result

Pending. The accepted baseline for this package is the 2026-06-12 PR stable
preview, not the older 2026-06-10 EP-on/off notes.

Known baseline anchors:

- RTX PR stable preview, cold OSL=1 prefill, EP-off, MTP:
  1024/4096/16384/65536 input tokens measured
  `6606.45 / 6206.06 / 8056.05 / 7540.46` input tok/s with all phase exits
  `0`.
- RTX PR stable preview, OSL=128 short-throughput supplement, EP-off, MTP:
  4096/16384/65536 input tokens measured
  `3123.74 / 6209.00 / 7049.72` input tok/s with all phase exits `0`.
- RTX GSM8K 5-shot limit-200 exact match:
  flexible `0.965`, strict `0.940`, exit `0`.
- GB10 forum53 MTP2 EP-off C=2 prefix-cache gate:
  OK `True`, driver health OK `True`, 4/4 requests, 0 failures,
  max TTFT `124.045698 s`, ITL p99 `0.144954 s`, prefix hits `79872`.

## Interpretation

Old EP-on dependency results are now route-screening hints only. A revived
FlashInfer or b12x route must be tested against the EP-off baseline above and
must keep prefix-cache-on user gates separate from cold-prefill claims.

The FlashInfer `#3395` packed SM120 route is a reference candidate because the
old GB10 endpoint-shaped subset improved TTFT by about `10-23%`. It is not a
drop-in dependency for the PR branch until its current head is revalidated with
the EP-off matrix, GSM8K, and lifecycle gates.

The black-benediction branch is an external target, not a drop-in patch queue.
The first useful output is a mechanism map: sparse MLA/dataflow, sparse indexer,
MoE kernel path, WO/mHC helpers, scheduler/admission behavior, dependency
requirements, and which pieces are already on public dependency heads.

## Follow-Up

- Create or update decision:
  `docs/sm120/decisions/watchlist/2026-06-12-backend-parity-roadmap.md`.
- Active next packages:
  `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/README.md` and
  `docs/sm120/experiments/2026-06-12-black-benediction-map/README.md`.
- Rerun trigger: a relevant dependency head change found during explicit
  upstream review, upstream merge of CUDA arch coverage work, or new external
  black-benediction performance claim.
- Next command: start with a same-host EP-off baseline/control plus one route
  variant at a time, then run sparse attribution before promotion gates.
