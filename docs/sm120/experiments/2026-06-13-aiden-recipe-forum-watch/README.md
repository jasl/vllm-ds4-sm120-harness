# Aiden Recipe Forum Watch

Status: watchlist
Date: 2026-06-13
Owner/context: external GB10 / SM121 unholy-fusion continuation study

## Question

The NVIDIA Developer Forums Aiden recipe thread reports a public community
deployment that looks like an `unholy-fusion` continuation and is validated by
multiple users. What should we learn from it, and how do we avoid repeating the
previous failure mode where unholy-fusion showed a large gain but isolated
ports into our branch did not reproduce it?

## Profile

- Hardware: two-node GB10 / SM121 is the primary target; RTX / SM120 is useful
  only for mechanism isolation.
- vLLM branch/image: public Aiden image
  `aidendle94/sparkrun-vllm-ds4-gb10:production-ready` and its installed vLLM
  overlay; do not assume `local-inference-lab/vllm main` or
  `dev/black-benediction` contains the same deployed code.
- Dependency or image identity: record Docker image digest, bundled b12x,
  FlashInfer wheels, NCCL, CUDA, and installed vLLM commit/overlay before
  using any performance number.
- TP / PP / EP: TP=2, PP=1. EP status must be recorded explicitly.
- MTP: MTP=2 unless a profile says otherwise.
- FP8 KV: enabled in the public recipe.
- Prefix cache: keep prefix-cache-off raw-prefill numbers separate from
  prefix-cache-on operational/session numbers.
- CUDA graph mode: keep `FULL_AND_PIECEWISE` unless reproducing the image
  exactly requires otherwise.
- `max_model_len`: public recipe advertises 1M context; routine parity should
  also include 4K/16K/32K/65K/128K.
- `max_num_batched_tokens`: public recipe uses 8192; compare against our 4096
  default as a capacity/latency tradeoff, not as a free default.

## Current Reading

Treat the forum thread as a real external target, not as direct PR evidence.
It combines an image recipe, deployment settings, bundled backend libraries,
and operational prefix-cache behavior. That makes it materially different from
our earlier public-stack `black-benediction` reproduction.

The strongest public signals from the thread are:

- The initial post claims a working dual-GB10 1M-context DS4 deployment with
  b12x MoE, CUDA 12.1, vLLM 0.21.1, TP=2, MTP, FP8 KV, prefix caching, and
  30-45 tok/s decode.
- A second user posted measured llama-benchy results on two GB10 nodes:
  prefill about `1574-1586 tok/s`, generation `35.6 tok/s` at C=1 and
  `63.9 tok/s` at shallow C=4.
- Other users reported successful practical usage and 40-45 tok/s generation,
  but later discussion also reports long-running KV-cache bloat / decode
  slowdown and a possible vLLM block-pool eviction bug.

## Interpretation

The prior unholy-fusion work likely stalled because we tried to explain a full
image/overlay effect by porting isolated knobs. The public evidence points to
a coupled stack:

- bundled FlashInfer sparse-MLA SM120/SM121 wrapper behavior;
- b12x sparse/indexer/MoE runtime hooks;
- NCCL / RDMA / all-reduce setup;
- prefix-cache and long-running KV lifecycle behavior;
- model-runner and warmup/scratch details.

Our prior failed ports are still useful negative evidence for individual
public-wheel routes, but they do not reject the Aiden image as an integrated
backend/dataflow target.

## Follow-Up

- Keep slow non-indexed `mla_prefill_chunk` as the fork-independent local
  optimization backup. It remains the most concrete in-branch sparse-prefill
  bottleneck after the grouped-SWA endpoint rejection.
- Reproduce Aiden image parity only as an external comparison first:
  prefix-cache-off random-prefill curve, prefix-cache-on operational curve,
  decode C=1/C=2/C=4, forum/user gate, and driver health.
- Before porting, diff the installed image overlay and classify each mechanism:
  packed sparse-MLA wrapper, sparse indexer, native MXFP4 MoE, all-reduce,
  model-runner/warmup, prefix-cache/KV fixes.
- Do not port DFlash/speculative changes without GSM8K and semantic gates.
- Do not treat public `local-inference-lab/vllm dev/black-benediction`
  public-stack RTX results as a rejection of the Aiden image; the image recipe
  has a different dependency and overlay contract.
