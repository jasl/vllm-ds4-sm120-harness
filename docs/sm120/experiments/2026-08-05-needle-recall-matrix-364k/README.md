# Needle recall vs context length and needle position, to 364K

Status: **complete** — 50/50, no degradation anywhere. A clean negative result, and a
narrow one: it bounds single-needle retrieval, not the failure it was chasing.
Date: 2026-08-05
Head: **`0f59188db1`** (tag `sm120-pr-41834-stable-preview-20260804`)

4x GB10 (sm_121) TP=4, `deepseek-ai/DeepSeek-V4-Flash-0731`, mml 524288, fp8 KV,
prefix cache on, DSpark nst=5 probabilistic, util 0.85, `ds4_harness.cli
needle-position-matrix`, repeat 2, temperature 0.

## Question

A third party reports DSv4-Flash going incoherent past ~400K **on the official DeepSeek
API** — hallucination plus forgetting context. The official API rules out any serving
stack as the cause, so it should reproduce here. Two model-level mechanisms predict it,
and they are separable by SHAPE rather than by argument:

| mechanism | predicted signature |
|---|---|
| `index_topk: 512` — a FIXED per-query attention budget that does not grow with context (0.78% of a native 64K window, 0.2% of 256K, 0.128% of 400K) | degrades with **length**, all needle positions falling together |
| YaRN extrapolation — trained window 65,536, reaching 1M via factor 16 | degrades with **position**, not merely with total length |

mml=524288 rather than the 262144 used for the topology work: the reported knee is
~400K and a sweep that stops at 256K cannot find it. Capacity is not the constraint —
capacity rises with mml on this model.

## Results

| line_count | prompt tokens | 512-token coverage | pos 0 | 25 | 50 | 75 | 100 | total |
|---|---|---|---|---|---|---|---|---|
| 1,100 | 30,873 | 1.66% | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | **10/10** |
| 2,200 | 61,673 | 0.83% | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | **10/10** |
| 4,400 | 123,273 | 0.42% | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | **10/10** |
| 8,800 | 246,473 | 0.21% | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | **10/10** |
| 13,000 | 364,073 | **0.14%** | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | **10/10** |

**50/50.** Filler lines measure 28.07 tokens each, so the row labels above are the
measured `prompt_tokens`, not an estimate.

At 364,073 tokens the top-512 budget covers 0.14% of the context — effectively the same
coverage as at the reported 400K knee (0.128%) — and retrieval is still perfect at every
needle position.

### Provenance defect found after publication, and re-validation

Discovered 2026-08-05: the four nodes' vllm worktrees were at THREE different SHAs
during this matrix (.116 `0f59188db1`, .117 `d42b8d9f55`, .118/.119 `54e0ebf330` —
a 10-commit skew including `mla_attention.py` and `fp8.py`), so the TP=4 serve ran
four ranks on three code versions while only the head node's SHA was asserted. The
"on `0f59188db1`" claim above originally held for one rank of four.

Re-validated the same day on trees verified identical (`assert_vllm_tree_parity`,
all four nodes clean at `0f59188db1`): the 4,400-line row reproduces exactly —
`prompt_tokens` 123,273 (token-identical filler), **2/2 at every position, 10/10**,
and boot KV capacity 3,614,884 tokens vs 3,593,684 recorded (+0.6%, inside the known
~1 GiB serve-to-serve noise). One row re-run rather than all five: the row at 0.42%
budget coverage sits mid-matrix, and the mixed-code concern is uniform across rows.

## What this does and does not establish

**Establishes:** single-needle retrieval on this stack is intact to at least 364K. No
length effect, and no position gradient, so neither predicted signature appears. Also
useful as a deployment fact: the 256K cap recommended in
[`2026-08-04-production-topology-mml-sweep`](../2026-08-04-production-topology-mml-sweep/README.md)
now has a measured clean recall point at 246,473 tokens under it rather than only an
argument from the degradation knee.

**Does NOT establish that the reported failure is absent.** The probe is too easy for
the claim it was aimed at, and that limitation was recorded before the results came in
rather than after:

* A single needle is exact-match retrieval. The filler is
  `Line 0042: archive=11; section=42; checksum=5502; stable filler...` and the needle is
  a natural-language sentence, so the indexer can find it by novelty detection — the
  scoring function never has to *discriminate*, only notice that one line is unlike the
  others.
* The reported failure is hallucination, forgetting, and degraded task execution. That
  requires holding many weak signals simultaneously across a long context. Different
  task, much harder.

A ceiling result on an easy probe is not evidence the system is healthy; it is evidence
the probe lacks resolution. Reading these 50/50s as "no long-context problem" would be
the error this section exists to prevent.

## Consequence for the `index_topk` experiment

FlashInfer 0.6.16's `_DECODE_DSV4_DISPATCH` carries `topk in {128, 512, 1024}` for every
head count, so **`index_topk=1024` is an already-instantiated kernel path**, reachable
from vLLM with `--hf-overrides '{"index_topk": 1024}'` since the value is read from
`hf_config` at runtime. (2048 exists only in `_DECODE_DSV3_2_DISPATCH`, so 1024 is the
ceiling for DSv4.) It is an attractive lever on this hardware specifically: decode here
is host-CPU-bound and dominated by MoE GEMM plus the NCCL all-reduce, and decode is
nearly flat with depth, so doubling the attention budget spends a share that is small to
begin with.

**But running that comparison against this probe would be wasted GPU time** — the
baseline is at ceiling, so both arms would read 50/50 and the result would be
uninformative in both directions.

The probe must first be made hard enough to fail. Two changes attack the budget directly:

1. **Multiple needles.** N needles must enter the top 512 *simultaneously*, competing
   with each other as well as with the filler. Difficulty then scales against the budget,
   and it yields a falsifiable quantitative prediction: doubling the budget should
   roughly double the number of needles retrievable before failure.
2. **Distractor needles** — same surface form, wrong content. These force genuine
   semantic discrimination rather than novelty detection.

Only once the baseline fails does the 1024 arm carry information.

## Reproduce

```sh
python -m ds4_harness.cli needle-position-matrix \
  --base-url http://127.0.0.1:8000 --model deepseek-ai/DeepSeek-V4-Flash-0731 \
  --line-counts 1100,2200,4400,8800,13000 --positions 0,25,50,75,100 \
  --repeat-count 2 --temperature 0
```

Serve as in the topology reference config, with `MAX_MODEL_LEN=524288`. Boot reported
`GPU KV cache size: 3,593,684 tokens` (55.96 GiB), which extends the mml/capacity series
and shows it **tapering**: tokens-per-mml runs 8.51 / 8.13 / 7.57 / 6.85 across mml
49152 / 131072 / 262144 / 524288, so capacity rises sublinearly with mml and the
relation must not be extrapolated further.
