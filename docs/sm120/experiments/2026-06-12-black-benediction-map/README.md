# Black-Benediction Mechanism Map

Status: watchlist
Date: 2026-06-12
Owner/context: external performance target analysis

## Question

Which ideas from `local-inference-lab/vllm` `dev/black-benediction` can help
the SM120/SM121 PR line close the performance gap while preserving correctness,
public dependency deployability, and reviewable branch history?

## Profile

- Hardware: dual RTX PRO 6000 / SM120 for local development and reproduction;
  two-node GB10 / SM121 for final confirmation.
- vLLM branch/commit: external reference `dev/black-benediction`
  `c6b2a7b18747ba467d25dd6d72be3559aaf7a341`; local PR stable preview
  `f32247a5a6` is the control.
- Dependency or image identity: record exact b12x, FlashInfer, CUDA, and image
  identity for every reproduction. Do not infer public-package viability from
  black-benediction source alone.
- TP / PP / EP: TP=2, PP=1, EP disabled by default for DS4 comparisons.
- MTP: MTP=2 for production-path checks; DFlash/speculative routes are
  high-risk and must carry separate correctness evidence.
- FP8 KV: enabled for DS4 baseline comparisons.
- Prefix cache: disabled for cold-prefill/backend attribution; enabled for
  forum53 and user-feedback gates.
- CUDA graph mode: `FULL_AND_PIECEWISE`.
- `max_model_len`: 131072 on RTX routine gates; GB10 uses guarded script
  defaults unless a profile says otherwise.
- `max_num_seqs`: 4 on RTX routine long-context gates; GB10 forum53 default is
  2.
- `max_num_batched_tokens`: 4096 default; 8192 only as an explicit A/B.
- Other route flags: record DFlash, B12X, FlashInfer, sparse indexer, MoE, and
  CUDA graph env vars in `artifacts.md`.

## Result

Pending. Local refs were confirmed at `c6b2a7b187` on 2026-06-12. On
2026-06-13, the public remote moved to `5fcd00c3d7`, but the new commits are
still concentrated in DFlash/spec-decode and Triton MLA decode rather than the
DS4 sparse prefill accumulate path. The branch is not a clean patch queue for
our PR line:

- Compared with the PR stable preview, the full diff spans hundreds of files
  and includes unrelated upstream drift, model support, parser/tooling churn,
  KV/scheduler changes, and deleted local PR tests.
- Compared with `local-inference/main`, the black-benediction-specific stack is
  narrower and currently centers on B12X indexer/MLA/MoE updates plus
  DFlash/SWA/spec-decode fixes.
- The 2026-06-13 latest commit,
  `5fcd00c3d7 Support DFlash on the V2 model runner`, touches DFlash runtime
  plumbing. The most relevant intermediate commit is
  `39e25654f8 Port tuned TRITON_MLA decode from glm51-v6 branch`, which is a
  decode MLA route with per-bucket tuning, not a cold-prefill sparse accumulate
  replacement.

## Interpretation

Use black-benediction as a performance target and design reference, not as a
merge source. The safe workflow is:

1. Reproduce endpoint behavior with the harness.
2. Map a mechanism to a measurable bottleneck from the EP-off bottleneck map.
3. Prefer public upstream/main dependency capabilities.
4. Port only isolated, default-controllable pieces with a clear correctness and
   maintenance story.

DFlash-related changes are correctness-sensitive. The user explicitly observed
that DFlash-style optimizations can damage GSM8K correctness. Any DFlash,
speculative decode, or Triton attention helper change must pass GSM8K
limit-200, semantic gates, and the standard vLLM focused tests before it can be
used as a basis for performance claims.

The current EP-off stage-timing evidence points first to sparse MLA accumulate,
especially slow non-indexed chunk groups. Therefore black-benediction's
DFlash/decode changes are a second-stage reference after the sparse-prefill
backend route is explored.

## Follow-Up

- Create or update decision:
  `docs/sm120/decisions/watchlist/2026-06-12-backend-parity-roadmap.md`.
- Preflight:
  `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/preflight.md`.
- Rerun trigger: `dev/black-benediction` head change, public b12x/FlashInfer
  head change, or new external performance claim.
- Next command: compare mechanisms against
  `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/evidence.md` and
  reproduce the smallest endpoint A/B on RTX before any GB10 run.
