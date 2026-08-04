# Production topology, max_model_len capacity, and cold prefill

Status: **complete** — 2x TP=2 wins throughput at every point measured; `max_model_len`
turns out to be a capacity *lever*, not a capacity *cost*
Date: 2026-08-04
Head: **`0f59188db1`** (tag `sm120-pr-41834-stable-preview-20260804`)

Hardware: 4x GB10 / DGX Spark (sm_121), RoCE via MikroTik CRS804,
`deepseek-ai/DeepSeek-V4-Flash-0731`, DSpark nst=5 probabilistic, fp8 KV,
prefix cache on, util 0.85, mnbt 8192, max-num-seqs 64.

## Question

Four machines are available for a personal production deployment. Redundancy is
explicitly not a requirement. Which layout serves a *small* number of concurrent
users best:

- **A** — one 4-node TP=4 replica, or
- **B** — two 2-node TP=2 replicas run side by side?

and, once that is known, what should `max_model_len` be set to?

## Method

Matched **total** concurrency, not per-replica concurrency: TP=4 at c=8 is compared
against 2x TP=2 at c=4+4. The two TP=2 replicas are always benchmarked
**simultaneously** — running them one at a time would hand each the whole CRS804
fabric and flatter option B.

Three arms, in order:

| script | what it establishes |
|---|---|
| `topology_kv.sh` | KV capacity per topology |
| `topo_throughput.sh <sha> tp4\|tp2` | throughput at matched total concurrency |
| `mml_sweep.sh <sha>` | capacity vs `max_model_len`, plus **cold** prefill |

Cold prefill is probed with **random token IDs** rather than text: the length is then
exact, and a prefix-cache hit is impossible. A warmup request precedes each series so
JIT/cudagraph compilation stays out of the measurement.

### Two hygiene failures worth recording

**1. A silently failing checkout.** The first two arms ran

```sh
git checkout -q -f "$SHA" 2>/dev/null
```

into a worktree whose fetch was stale. `0f59188db1` was not present, checkout failed
with `pathspec did not match any file(s)`, the redirect ate the error, and the run
proceeded at whatever `HEAD` already was — `b1ef3033f4`, three commits back. The log
then printed `$(git rev-parse --short HEAD)`, which *looks* like confirmation but only
echoes reality back.

> **Printing the SHA is not verifying it.** Fetch, checkout with stderr visible, then
> assert `rev-parse HEAD` equals the SHA that was asked for, and assert some symbol
> from the delta is present in the tree.

Fifth instance on this branch of a pipe or redirect swallowing a failure. Consequence
here was contained — both arms were equally affected, so the comparison held — but the
absolute numbers predate PR #38's E8M0 hoist, and the capacity numbers had to be
re-measured before the mml question could be answered at all.

**2. `flock` fd inherited by background children.** The lock is taken with
`exec 9>lockfile; flock -n 9`. The two replica-start subshells are backgrounded, inherit
fd 9, and *outlive a kill of the parent* — so after killing the driver the lock was still
held by two orphans and the relaunch blocked on itself. Fixed by closing the fd in the
children (`... &` -> `... 9>&- &`). Note `pkill` reported success regardless; its exit
code was never checked.

## Results

### 1. KV capacity scales with `max_model_len`

Same commit, same memory budget, `max_model_len` the only variable:

| mml | TP=2 (1 replica) | TP=4 | TP=4/TP=2 |
|---|---|---|---|
| 49,152 | 129,901 tok | 418,335 tok | 3.22x |
| 131,072 | 287,086 tok | 1,065,210 tok | 3.71x |
| 262,144 | **605,013 tok** | **1,985,436 tok** | 3.28x |

KV memory is essentially constant across all six cells (17.2–17.6 GiB at TP=2,
54.6–54.9 GiB at TP=4). **mml x5.33 buys capacity x4.66 for free.**

This was initially confounded — the 49,152 points came from `b1ef3033f4` and the
131,072 points from `0f59188db1`, so mml and commit moved together. Re-measuring 49,152
on `0f59188db1` reads 129,901 against the old 128,378 (1.2% apart, inside the known ~1
GiB run-to-run KV noise), which kills the commit hypothesis outright.

Cross-check: TP=4 @ mml=262144 reads 1.985M tokens against the 1.87M ceiling measured
independently in the 2026-06-23 frontier run — two different paths, consistent answer.

### 2. Throughput at matched total concurrency: 2x TP=2 wins everywhere

At mml=49152, depth 8192:

| total conc | topology | pp2048 t/s | tg128 t/s | per-req decode | TTFT |
|---|---|---|---|---|---|
| 8 | **2x TP=2** | **2930** | **112.0** | **20.2** | **4.3 s** |
| 8 | TP=4 | 1822 | 62.1 | 17.3 | 6.5 s |
| 16 | **2x TP=2** | **2967** | **97.9** | **11.6** | **7.8 s** |
| 16 | TP=4 | 1864 | 75.2 | 9.55 | 10.9 s |

At mml=131072, total concurrency 8, zero preemptions anywhere:

| depth | metric | 2x TP=2 | TP=4 | |
|---|---|---|---|---|
| 16384 | pp2048 t/s | **2838.2** | 1704.8 | +66% |
| 16384 | tg128 t/s | **93.3** | 63.0 | +48% |
| 16384 | TTFT | **4.71 s** | 6.82 s | -31% |
| 32768 | pp2048 t/s | **2757.8** | 1664.9 | +66% |
| 32768 | tg128 t/s | **84.3** | 60.5 | +39% |
| 32768 | TTFT | **4.87 s** | 7.02 s | -31% |

The margin is stable across two mml values and two depths — prefill ~+66%, decode
~+40%, TTFT ~-31%. Consistent in direction with the 2-node all-reduce profile, where
NCCL AR was already 27.5% of the c=5/16k decode cliff; four nodes costs ~40% of
throughput.

**Both topologies saturate at total concurrency ~8.** Going 8 -> 16, 2x TP=2 decode
*falls* 112.0 -> 97.9 while per-request drops 20.2 -> 11.6 and TTFT nearly doubles. The
extra concurrency becomes queueing, not throughput.

### 3. Cold prefill — the numbers that did not previously exist

Every `llama-benchy --depth` TTFT is **prefix-cached**: "TTFT 2031 ms @ d122880" is 2048
fresh tokens against a warm 123k context, not a cold 123k prefill. Uncached, exact-length:

| prompt | TP=2 | TP=4 | TP=4 faster by |
|---|---|---|---|
| 8,192 | 4.42 s (1855 t/s) | 3.56 s (2304 t/s) | +24% |
| 32,768 | 19.17 s (1709 t/s) | 16.81 s (1950 t/s) | +14% |
| 131,072 | 89.40 s (1466 t/s) | 74.88 s (1750 t/s) | +19% |
| 260,000 | 214.37 s (1213 t/s) | 184.69 s (1408 t/s) | +16% |

Fits **T ∝ N^1.12 (TP=2) / N^1.14 (TP=4)** — near-linear. Length x31.7 costs only
35–39% of throughput, so the indexer's O(N²) does **not** dominate below ~260K.

This does *not* supersede the O(N^1.4) recorded on 2026-06-23, which fits the 256K–1M
range this sweep never entered; super-linearity normally worsens with length and both
can hold in their own ranges. The one overlapping point is comparable and did improve:
**256K was 392.6 s then, 260K is 214.4 s now — 1.83x faster** — though config differs on
several axes besides the commit, so the gain is not cleanly attributable.

Extrapolated 400K cold prefill: **~302 s (TP=4) / ~348 s (TP=2)**, i.e. 5–6 minutes to
first token.

## What this implies for future optimisation work

**1. `max_model_len` is a lever, and the intuitive tradeoff is inverted.** "Cap the
context to buy concurrency" is a net loss here: mml is not a per-request reservation
(short requests do not cost more KV because mml is high), it is a structural parameter
of the KV pool, and raising it lowers the amortised per-token cost. Set mml to the
highest value **quality** allows, not the highest **capacity** allows. Mechanism is not
yet pinned down; the lead is `vllm/models/deepseek_v4/nvidia/flashmla.py:218`,
`compressed_region_size = max_model_len // compress_ratio`. **Worth understanding
properly** — if per-token KV cost is genuinely tunable through a compression-region
parameter, that parameter may be worth exposing directly rather than reaching it
sideways through mml.

**2. ~70% of cold prefill does not scale with node count.** Doubling nodes (TP=2 ->
TP=4) doubles compute but buys only ~18% on cold prefill (1.14–1.24x across four
lengths). Solving Amdahl for the parallel fraction gives **p ≈ 0.30**. The added
all-reduce traffic is inside that 70%, so the genuinely serial part is smaller than 70%
— but either way, **throwing nodes at long-prompt latency is close to a dead end, and
the payoff is in whatever occupies the non-scaling majority.** This is the single most
actionable number in the sweep and nothing here identifies *what* that majority is; a
profile of a single cold 131K prefill at TP=2 vs TP=4 is the obvious follow-up.

**3. Below ~260K, the indexer O(N²) is not where the time goes.** Cold prefill is
N^1.12. Optimisation effort aimed at the quadratic indexer scoring pays off at
frontier lengths (256K–1M, where N^1.4 was measured) and very little below that.
Previous work treated the residual quadratic as *the* long-context prefill problem;
this bounds where that is true.

**4. The concurrency ceiling is ~8 and is not a KV limit.** Zero preemptions at every
point, including 2x TP=2 at depth 32768 where 4 requests x ~33k only fills 132k of a
285k pool. Whatever saturates at c=8 is compute or host-side, consistent with the
decode-is-host-CPU-bound finding. Raising KV will not raise this ceiling.

**5. Methodology: `--depth` TTFT is not TTFT.** Any latency claim about long prompts
made from benchy `--depth` numbers is a claim about *incremental* prefill on a warm
cache, and understates cold TTFT by more than an order of magnitude at 123K (2.0 s vs
89.4 s). The random-token-ID probe in `mml_sweep.sh` is the right instrument and should
be reused.

## Model-level context ceiling (not measured here, but it bounds the above)

`config.json` reports `max_position_embeddings: 1048576` with
`rope_scaling: {type: yarn, factor: 16, original_max_position_embeddings: 65536}` and
**`index_topk: 512`**. Two implementation-independent mechanisms degrade long context:

1. YaRN extrapolation — the trained window is 64K; 400K is 6.1x beyond it.
2. The sparse-attention budget is **fixed at 512 tokens per query** and does not grow
   with context: 0.78% of a native 64K context, 0.128% of 400K, 0.05% of 1M.

A third party independently reports DSv4-Flash going incoherent past ~400K
(hallucination plus recall loss) **on the official DeepSeek API**, which rules out any
serving stack as the cause and means it will reproduce here. An implementation can only
make this worse — an inexact top-k compounds it — never better than the design allows.

Combined with the ~6 minute cold prefill at 400K, two independent arguments put the
usable ceiling well below it. **256K is the recommended cap.**

## Open

- **Locate our own recall knee.** `ds4_harness.cli needle-position-matrix` sweeps
  `--line-counts` x `--positions` (0–100). Filler lines are ~30 tokens, so ~4,400 lines
  ≈ 128K and ~8,800 ≈ 256K. The two mechanisms are separable by shape: a fixed-budget
  exhaustion degrades with **length** at all needle positions together, while YaRN
  extrapolation degrades with **position**. Predicted: a knee, not a slow slide.
- **Profile the non-scaling 70%** of cold prefill (finding 2).
- **Understand the mml -> per-token-KV mechanism** (finding 1).

## Reproduce

```sh
scripts/run_mml_capacity_sweep.sh 0f59188db1     # capacity + cold prefill
scripts/run_topology_throughput_compare.sh 0f59188db1 tp4
scripts/run_topology_throughput_compare.sh 0f59188db1 tp2
```

Deployment configuration derived from these results:
[`docs/sm120/reference-configs/gb10-production-2x-tp2-smg.md`](../../reference-configs/gb10-production-2x-tp2-smg.md).
