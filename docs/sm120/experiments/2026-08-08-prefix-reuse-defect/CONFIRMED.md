# Concurrent writers can poison the prefix cache, and the damage persists

Date: 2026-08-08. Tree `4ebd1fb698` (branch head). Runner: V2 unless stated.
Companion to [`README.md`](README.md), which narrowed the fault to the reuse
path; this file identifies **which half of reuse** is broken.

> ## ⚠ The poisoning is STOCHASTIC — corrected 2026-08-08, later the same night
>
> This file was first titled "Confirmed: … persistently" and written as if a
> concurrent cold batch *always* poisons the cache. It does not. Two later runs
> of the same procedure did **not** poison, one of them with a cold-batch score
> of 4/12 — identical to the run that *did* poison. **How badly the cold batch
> goes does not determine whether the cache ends up poisoned.**
>
> Tally so far — poisoned in **6** observations, not poisoned in **2**:
>
> | poisoned | not poisoned |
> |---|---|
> | `conc_first` (cold 4/12 → serial FAIL → 1/12) | `pread` run 1 (cold 11/12 → serial pass) |
> | V2 gate ×3 (wave 2 loses 11 of 12) | `pread` run 2 (cold 4/12 → serial pass) |
> | prewarm V2 c=12 (SOLO 0/1, WARM 1/12) | |
> | prewarm V2 c=5 (SOLO 0/1, WARM 0/5) | |
>
> What survives unchanged: the paired comparison below (1/12 versus 12/12), the
> wave structure across six V1 and three V2 gate runs, and the fact that once
> poisoning happens it persists until the blocks are evicted. What was
> overstated: that a concurrent cold batch reliably reproduces it. It is
> frequent, not certain — which is also why this defect survived months of
> investigation as an unexplained "per-serve bimodality": it cannot be
> reproduced on demand in a single run.

## The result

Two V2 serves, identical in every respect except **who writes the prefix cache
first**. Both then do the same thing: send 12 concurrent copies of the gate
prompt at a populated cache.

| step | `conc_first` — cache written by racing writers | `serial_first` — cache written by one serial request |
|---|---|---|
| 1 | 12 concurrent, empty cache → **4/12** | 1 serial request → **pass** |
| 2 | 1 serial request → **FAIL** | 12 concurrent → **10/12** |
| 3 | 12 concurrent → **1/12** | 12 concurrent → **12/12** |

**Step 3 against step 3 is the whole finding: the same operation returns 1/12
or 12/12 depending only on how the cache was populated.**

So: reuse is not the defect. **Concurrent population of the cache writes bad
blocks, and the damage stays in the cache.** Every later reader gets it,
including a lone serial request — which is exactly why a serial failure earlier
looked like it refuted the write race. It did not; that request was reading an
already-poisoned cache.

`serial_first` going 10/12 → 12/12 fits the same mechanism: at step 2 each
request still writes its own uncached tail block, so a small race remains; by
step 3 everything is written and concurrent reuse is *perfect*.

## Why V2 looks broken and V1 does not

Neither runner is individually at fault — they differ in **exposure**.

| | V1 | V2 |
|---|---|---|
| KV pool | 349,762 tok | 416,810 tok (+19%) |
| peak `Waiting` at c=12 | **11** | **0** |
| admission | staggered — the pool cannot hold 12 at once | all twelve admitted together |
| result | cache mostly written correctly, 22/24 | cache poisoned, 3–5/24 |

V2's larger KV lets the scheduler admit all twelve simultaneously, which
maximises the number of racing writers. V1 is forced to stagger, so later
requests find blocks already written and the cache survives.

This also explains the long-standing "V2 recall is bimodal by serve instance":
serve KV varies ~1 GiB run to run, which straddles the point where all twelve
fit at once — so a serve appeared to "land in a mode at startup".

## Independent cross-checks

Three measurements taken **before this hypothesis existed** agree with it:

- **Wave structure.** Across all six V1 gate runs, failures fall *exclusively*
  in request indices 0–11 (the first concurrent wave); wave 2 never fails. On
  V2, both waves fail and wave 2 loses 11 of 12. Clean cache versus poisoned
  cache, exactly.
- **The number 1/12.** V2 wave 2 (11 of 12 failing), the prewarm `WARM` arm, and
  `conc_first` step 3 independently return 1/12.
- **Prefix cache off** removes shared blocks entirely, and both runners return
  24/24/24.

## Failure shape

Never partial recall. A poisoned read loses **all three** sentinels and answers
*coherently*, reporting filler content — the checksums decode (line `i` carries
`(i*37)%1009`) to real line numbers near the sentinels. When told a line number
outright, even a poisoned V2 quotes that line correctly, which is why an early
probe that asked by position saw nothing wrong.

## Candidate code site — not yet verified

`KVCacheManager.allocate_slots` publishes blocks into
`cached_block_hash_to_block` at **scheduling** time, counting
`total_computed_tokens + num_new_tokens` — i.e. including the tokens this step
has not computed yet:

```python
num_tokens_to_cache = min(total_computed_tokens + num_new_tokens,
                          request.num_tokens)
self.coordinator.cache_blocks(request, num_tokens_to_cache)
```

That is publish-before-write by construction, and it predicts the observed
pattern. **It has not been verified** — the next step is instrumentation
(count same-step hits on just-published blocks; dump the reused span's block
table), not more black-box probing. Both known prefix-cache race fixes are
already in this tree (upstream #50432, fork `c601168d0f`), so this is not a
missing patch.

## Consequences

- **This is a production defect on the default runner too.** V1 in the default
  configuration returns 22/24, not 24/24, and its failures are all in the first
  concurrent wave. Any deployment that takes concurrent traffic on a cold cache
  is exposed.
- **A workaround exists today**: warm the prefix cache with a single serial
  request before admitting concurrency. `serial_first` step 3 shows a correctly
  populated cache is then perfect under concurrency.
- **Fixing it likely unblocks V2**, and with it KV +19%, draft acceptance +6.6%,
  prefill ctx_pp +1.1–1.6% / pp2048 +4.2%.

## Method notes

★★★ **The same observation supported opposite conclusions under an unexamined
assumption.** A lone serial request failing against a warm cache was read as
"concurrency is not required, so the write race is refuted". That inference
silently assumed the race's damage was *transient*. Once damage can persist,
the identical datum becomes the race's strongest evidence. The assumption was
never stated, so it was never checked.

★★ **A probe that stops reproducing the failure proves nothing.** Two probes
passed every arm and nearly produced the conclusion "V2 is fine under reuse":
one ran with thinking ON (the harness's own comment says thinking-OFF is the
fragile path and thinking-ON masks the loss); the other reconstructed the gate
prompt by hand and added a newline. Both were caught by comparing payloads
against the gate rather than by interpreting the pretty result.

★★ **Do not mutate a file a running experiment depends on.** Overwriting the
probe mid-run silently made one arm answer a different question, and its data
had to be discarded.

★ **Read the telemetry before booking GPU time.** Two hypotheses
(capacity/preemption, the V1-only resumed resync) died for free from
`preempt_lines=0` and a 36% KV peak.
