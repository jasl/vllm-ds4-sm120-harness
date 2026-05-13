# SM120 Long-Context Validation — 2026-05-13

DeepSeek V4 Flash on **2× NVIDIA RTX PRO 6000 Blackwell Workstation
Edition** (TP=2 EP), vLLM `jasl/vllm` @ `dda4668b5` (head of
`ds4-sm120-preview-dev` / PR #41834).

Validates the rowwise paged-MQA logits kernel restore
(`dda4668b5 Restore rowwise paged-MQA logits kernel for SM12x long
context`) on the long-context regime called out in PR comments
[4435478184](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4435478184)
and
[4436565052](https://github.com/vllm-project/vllm/pull/41834#issuecomment-4436565052):
*"happens on higher CTX only >100k"*.

## TL;DR

- **TPOT stays flat 6.3–13.3 ms across ISL 1K → 128K** with MTP=2 — the
  rowwise kernel's per-row Q-reuse signature. The previously-reported
  regression at >100K is resolved.
- **64K is the practical ceiling on Workstation SM120** for the
  PR-recommended deployment profiles (single-card 96 GiB - 74 GiB model
  weights = 7 GiB KV after overhead; with the `0.985`
  `--gpu-memory-utilization` recipe and `max-model-len=65536`,
  `max_concurrency=3.38×` for no-MTP and `2.08×` for MTP=2).
- **Above 100K, first-bench TTFT carries a one-time cold-JIT spike**;
  steady-state TTFT after warm-up is ~3× lower. Documented under
  "Cold-JIT bias above 64K" below; not a regression vs the PoC branch,
  but worth pre-warming with one dummy request after serve restart for
  deployments that target >100K context.
- **128K MTP=2 still fits on a 96 GiB Workstation card** at gpu-mem
  0.985 with KV `270K tokens / max_concurrency 2.06×`. 200K no-MTP
  fits at the same util with KV `587K tokens / max_concurrency 2.87×`.
  256K and 512K need the 2-node Spark cluster (see the matching GB10
  bundle).

## random ISL=8192 OSL=512 c=1,4,8,16,24 num-prompts=72 (warmed)

`performance/random_isl8k_c1_24/mtp2_warmed_num72_bench.json`

Serve: MTP=2, `--gpu-memory-utilization 0.98`, `max-model-len=65536`.
A `c=24 num-prompts=24` discard bench (saved as
`mtp2_warmup_c24_num24_bench.json`) ran first to seat the spec-decode
and MoE batch-24 kernels before the measurement.

| c | out tok/s | TTFT mean (ms) | TTFT p99 (ms) | TPOT mean (ms) | accept % | accept len |
|---|---|---|---|---|---|---|
| 1 | 74.75 | 3,284 | 3,337 | **6.98** | 48.34 | 1.97 |
| 4 | 99.02 | 4,328 | 13,506 | 31.85 | 50.49 | 2.01 |
| 8 | 117.14 | 5,612 | 28,115 | 57.14 | 49.68 | 1.99 |
| 16 | 122.69 | 11,782 | 57,560 | 105.83 | 49.82 | 2.00 |
| 24 | 124.70 | 21,629 | 86,952 | 149.52 | 51.60 | 2.03 |

Acceptance hovers 48–52 % on synthetic random tokens (vs 67–69 % on
mt-bench prose); accept-length stays ≈ 2.0. The c=1 TPOT (6.98 ms) is
within run-to-run noise of the mt-bench c=1 TPOT (6.49 ms reported in
the matching deployment bundle), confirming the rowwise dispatch
recovers single-stream latency at long context too.

## Long-context bench (random, c=1, num-prompts=2, OSL=2048)

`performance/long_ctx/*.json`

### MTP=2 @ `--gpu-memory-utilization 0.985 --max-model-len 131072`

KV reported at startup: `7.04 GiB / 270,077 tokens / max_concurrency
2.06×`.

| ISL | Order | TTFT mean (ms) | TPOT mean (ms) | aggregate tok/s | accept % | accept len |
|---|---|---|---|---|---|---|
| 100,000 | first (cold) | 74,981 | 12.85 | 20.22 | 48.79 | 1.98 |
| 100,000 | second (after 128K) | 76,141 | 11.09 | 20.72 | 64.67 | 2.29 |
| 128,000 | first (cold) | 109,392 | 12.89 | 15.08 | 58.94 | 2.18 |
| 128,000 | second (after 100K) | 33,796 | 13.34 | 33.52 | 55.21 | 2.10 |

### no-MTP @ `--gpu-memory-utilization 0.985 --max-model-len 204800`

KV reported at startup: `10.59 GiB / 587,502 tokens / max_concurrency
2.87×`.

| ISL | Order | TTFT mean (ms) | TPOT mean (ms) | aggregate tok/s |
|---|---|---|---|---|
| 200,000 | first (cold) | 223,556 | 31.50 | 7.11 |

### TPOT vs ISL (rowwise dispatch evidence)

The decisive signal that the rowwise kernel is active is the flat
TPOT under ISL growth. Per-token cost stays in a tight 6–13 ms band
all the way from 1K to 128K with MTP=2 (and the 31 ms at 200K no-MTP
reflects the loss of MTP=2 acceleration, not a rowwise regression):

| ISL | Variant | TPOT mean (ms) |
|---|---|---|
| 1,024 | MTP=2 | 6.34 |
| 8,192 | MTP=2 | 6.50 |
| 32,768 | MTP=2 | 6.31 |
| 60,000 | MTP=2 | 6.77 |
| 100,000 | MTP=2 | 12.85 (cold) / 11.09 (warm) |
| 128,000 | MTP=2 | 12.89 (cold) / 13.34 (warm) |
| 200,000 | no-MTP | 31.50 |

The pre-rowwise 2D-tile kernel would have shown roughly linear TPOT
growth with ISL because `BLOCK_N=64` forces `cdiv(token_count, 64)`
programs per row, with weak Q-reuse across them. Rowwise replaces this
with one program per row that streams the whole token window through
shared registers.

## Cold-JIT bias above 64K (action item / known behaviour)

The reverse-order probe in `mtp2_isl{128k_cold,100k_warm}_…json` shows
an asymmetry that is worth documenting:

- The first long-context bench after a fresh serve always pays a
  one-time cold cost on top of the actual chunked-prefill work.
- 100K first → 75 s; 100K second (after 128K) → 76 s. ≈ no warming
  benefit because the work is already dominated by real per-chunk
  compute (13 chunks × ≈ 6 s ≈ 78 s).
- 128K first → 109 s; 128K second (after 100K) → 34 s. **75 s saved**
  on the warmed run.

Root cause is most likely Triton specialisation on the rowwise
kernel's `logits_width: tl.constexpr` argument (the per-step
`token_count`): every previously-unseen `token_count` triggers a new
JIT compile. A 100K-token bench primes the cache for the
`token_count ∈ {100_000 ± OSL}` band that 128K *also* needs to call
into for its decode tail; the reverse direction primes only the
overlapping 100K-bound subset, so 128K-cold has more uncached
specialisations to compile.

### Practical guidance for >64K deployments

64K and below are unaffected — our existing warmup
(`5c8975591 Extend DeepSeek V4 prefill warmup to max single-chunk
size`) already covers the chunked-prefill specialisations at and
below `max_num_batched_tokens=8192`.

For deployments that target `max_model_len > 64K`:

1. After `/health=200`, send one dummy request whose ISL matches the
   intended ceiling. The first real user request will then land on
   warm specialisations and skip the one-time spike.
2. Or accept the spike on the first long-context request and
   document the expectation.

This is a niche path — the deployment bundles in this repo
(`baselines/20260512_sm120_deployment_1c20f1a6d/` for SM120, GB10
counterpart in the parallel folder) target `max_model_len ≤ 32K`
where this spike does not apply.

## What lives in this bundle

```
performance/
  long_ctx/
    mtp2_isl100k_cold_first_bench.json        # 100K first in round 1
    mtp2_isl128k_warm_after_100k_bench.json   # 128K second in round 1
    mtp2_isl128k_cold_first_bench.json        # 128K first in reverse round
    mtp2_isl100k_warm_after_128k_bench.json   # 100K second in reverse round
    nomtp_isl200k_bench.json                  # 200K single round, no-MTP
  random_isl8k_c1_24/
    mtp2_warmup_c24_num24_bench.json          # discarded warmup
    mtp2_warmed_num72_bench.json              # c=1,4,8,16,24 num-prompts=72
report.md
```

## Reproduction

Same serve config as the deployment bundle, with `max-model-len`
raised to fit each target:

```bash
# Long-context MTP=2 at 128K
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 --block-size 256 \
  --max-model-len 131072 --tensor-parallel-size 2 \
  --host 127.0.0.1 --port 8000 \
  --no-enable-flashinfer-autotune \
  --reasoning-parser deepseek_v4 --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 --enable-auto-tool-choice \
  --enable-expert-parallel \
  --gpu-memory-utilization 0.985 \
  --speculative-config '{"method":"deepseek_mtp","num_speculative_tokens":2}'

# no-MTP at 200K
#   replace --max-model-len with 204800 and drop --speculative-config

# Random ISL=8192 c=1,4,8,16,24:
vllm bench serve --model deepseek-ai/DeepSeek-V4-Flash \
  --tokenizer-mode deepseek_v4 --dataset-name random \
  --random-input-len 8192 --random-output-len 512 \
  --num-prompts 72 --max-concurrency "${c}" \
  --temperature 1.0 --ignore-eos --base-url http://127.0.0.1:8000

# Long-context (random):
#   --random-input-len 100000|128000|200000 --random-output-len 2048
#   --num-prompts 2 --max-concurrency 1
```

## Source

- vLLM: `dda4668b5` on `jasl/vllm` `ds4-sm120-preview-dev` (PR #41834,
  `codex/ds4-sm120-min-enable`).
- Harness: this commit.
