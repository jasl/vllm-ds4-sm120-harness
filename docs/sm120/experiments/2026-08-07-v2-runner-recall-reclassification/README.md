# Model Runner V2 recall — reclassified from "defect" to "thinner concurrency margin"

> ## ⛔ TWO CENTRAL CLAIMS BELOW ARE REFUTED (2026-08-08)
>
> Kept in full, unedited, because how they failed is the useful part. See
> [`../2026-08-08-prefix-cache-writer-race/`](../2026-08-08-prefix-cache-writer-race/README.md)
> for what replaced them.
>
> 1. **"The catastrophic low mode is gone."** It is not. A V2 serve on the same
>    tree returned **3 / 4 / 5 out of 24** — tight within the serve, which is the
>    historical low-mode signature exactly. Six clean serves did not show it;
>    that bounds the *rate*, not the existence. The honest claim was always
>    "the rate fell", and P(0 of 6) only looked decisive because it was computed
>    against the *old* rate.
> 2. **"Gamma-only partial recall ⇒ batch numerics."** Wrong on both halves.
>    Failing requests lose **all three sentinels**, not the last one, and they
>    answer *coherently* with the filler checksums at the document's first /
>    middle / final lines — i.e. they saw a document with no sentinels in it.
>    Every failure falls in request index 0–11 (the first concurrent wave);
>    index ≥12 has never failed. This was visible in the per-request JSON the
>    whole time; the summary line `passed=N/24` was read instead.
>
> The reclassification headline — "not a V2 structural defect, just thinner
> margin" — is therefore **withdrawn**. There is a real, reproducible defect,
> it is in the prefix-cache path, and V1 is exposed to it too (22/24 rather
> than 24/24).

Status: ~~V1 remains the default — but for a much weaker reason than before.~~
**Superseded — see the banner above.**
Date: 2026-08-07 (evening), superseding the 2026-08-03 revert rationale.
Tree: `4ebd1fb698` (current head of both `codex/ds4-sm120-min-enable` and
`ds4-sm120-preview-dev`), i.e. the post-08-06/07-fix-wave pushed tree.
Predecessor: [`../2026-08-02-v2-model-runner-ab/`](../2026-08-02-v2-model-runner-ab/README.md).

## Question

The 08-02/08-03 A/B rejected V2 because its arthur c=12 long-context recall
collapsed to a mean of 10.5 (range [6,13]) against V1's 22.25. The 08-04
follow-up reframed that as **bimodal by serve instance** — a serve landed in a
~22 mode or a ~7 mode at startup and stayed there, at a rate of 60–75% over 14
serves, with startup logs structurally identical between modes.

That is a *catastrophic and undetectable* failure, which is why V1 stayed
default. Two things then changed: the 08-06/07 fix wave landed (notably the
C128A capture-baked stride fix, PR #41), and its recorded signature —
startup-fixed, no INFO trace, tight-within-serve / 3× across-serve — matches
the low mode exactly. So: **is the low mode gone, and if something remains,
what class of thing is it?**

## Profile

2× GB10 (sm_121) TP=2, `deepseek-ai/DeepSeek-V4-Flash-0731`, DSpark nst=5
probabilistic, fp8 KV, prefix cache on, mml 131072, util 0.85, mnbt 8192,
`.116` head / `.119` worker. Runner is the only variable; every arm reads back
`Model Runner V2` from the serve log rather than trusting the env var (but see
the method note — the first script's read-back was broken).

## Part 1 — the catastrophic low mode is gone

Pre-registered before running: the axis that varies is *across serves*, so
**one c=12 gate per serve, six fresh serves** (the 08-03 revert's n=8 came from
one serve — n raised on the wrong axis). Raw: [`v2_reeval.out`](v2_reeval.out).

| serve | 1 | 2 | 3 | 4 | 5 | 6 | mean |
|---|---|---|---|---|---|---|---|
| c=12 | 17 | 16 | 21 | 17 | 19 | 20 | **18.3** |
| c=1 | 2/2 | 1/2 | 2/2 | 0/2 | 2/2 | 2/2 | 9/12 |

| comparison | diff | exact p |
|---|---|---|
| vs historical LOW mode (7.4) | **+10.9** | **0.0022** |
| vs historical HIGH mode (22.3) | −4.0 | 0.024 |
| vs V1 on this tree (22.25, n=4) | −3.9 | 0.024 |

**0 of 6 serves landed anywhere near ~7**, where the historical rate was
60–75% — P(0 of 6 by chance) = 0.02–0.4%. The distribution is now *unimodal
and shifted down*, which is a different shape, not a lucky set of mode draws.

V1 on the same tree, post-wave, for reference: **24, 21, 23, 21** (mean 22.25)
— from `merge_gate.out`, `baseline_suite.out`, `final_gate.out` on `.116`.
Worth recording that V1 itself dipped to 16/18/18/19 in the 08-02→08-06 window
and the fix wave restored it; the V1 band is not a constant of nature either.

## Part 2 — 156 serial requests, zero failures

Every parameter of the gate was varied independently, on **both** runners, with
the condition verified in effect rather than assumed. Nothing reproduced.

| probe | conditions | requests | failures | raw |
|---|---|---|---|---|
| needle depth sweep | 6 distances from end (13→700 lines), spanning the final-8192-token chunk boundary | 36 | 0 | [`tail_sweep.out`](tail_sweep.out) |
| gate-verbatim prompt | exact gate text; uniform vs prose filler | 24 | 0 | [`gate_repro.out`](gate_repro.out) |
| thinking mode | non-thinking (gate's mode) vs default; `avg_reasoning_chars` 0 vs 364/396 confirms the arms differed | 32 | 0 | [`think_repro.out`](think_repro.out) |
| question shape | ask-all / ask-3rd-only / reversed order / 1-needle control | 32 | 0 | [`bisect.out`](bisect.out) |
| prefix cache | ~~cache on, hits confirmed~~ — **this arm is void, see below** | 16 | 0 | [`pfx_repro.out`](pfx_repro.out) |
| load-state phases 1+3 | see Part 3 | 16 | 0 | [`load_state.out`](load_state.out) |
| **total** | | **156** | **0** | |

**⚠ The prefix-cache arm did not test what it claimed.** Every one of its 16
requests — including repeats of a byte-identical payload — reports
`cached=0/27957`, so by its own readback it achieved *zero* prefix reuse and
therefore never exercised the condition. Whether that is a true 0% or a broken
readback cannot be told from the file, which is exactly the problem: **the arm
is uninterpretable and must not be counted as evidence.** The same applies, more
weakly, to every other serial probe here — none of them measured reuse at all.

Two things stand out. The depth sweep is **identical between runners** — 3/3 at
all six positions on both — so serially V1 and V2 are indistinguishable on the
exact quantity the gate measures. And the failing needle at c=12 is always the
same one (`gamma-onyx-43`, the last of three), with output always coherent and
**zero garble and zero leaked control tokens** across all runs, which rules out
the corruption class the fix wave addressed.

A parallel workflow ran 3 analysis angles over 10 candidate metadata-path
mechanisms with adversarial verification: **0 survived**; one was shown to run
in the opposite direction from its own claim.

## Part 3 — the decisive experiment: same serve, before and after

One V2 serve held constant throughout, so serve instance cannot vary:
[`load_state.out`](load_state.out).

```
PHASE 1  serial gate prompt x8, before any load ...... 8/8 PASS
PHASE 2  the real gate at c=12 ....................... 21/24  (3 misses)
PHASE 3  serial gate prompt x8, same serve, after .... 8/8 PASS
```

This single run excludes both remaining structural explanations at once:

- **not a bad serve instance** — the same serve passes serially, twice;
- **not persistent damage** — concurrency does not degrade the serve it ran on.

The deficit exists *only inside concurrent batches* and leaves nothing behind.

## Verdict

**Reclassified.** This is the already-documented concurrency-batch-numerics
class — the same family as V1's own c=12 [20,24] band — in which V2 simply has
less margin. It is **not** a V2 structural defect, and there is no
tail-specific, position-specific, or cache-specific bug to find. The
"gamma-only" signature is what partial recall looks like under batch numerics:
the last-retrieved item is the first to drop.

The practical stance changes accordingly:

| | before (08-03/08-04) | now |
|---|---|---|
| claim | V2 can land in a state that destroys recall, undetectably | V2 retrieves ~4 fewer needles at c=12 |
| class | catastrophic, startup-nondeterministic | margin, concurrency-only, no persistent damage |
| why V1 is default | **safety** | **margin** |

V2's advantages are unaffected and still real: KV +4.70 GiB (+27.5%), draft
acceptance +6.6%, prefill ctx_pp +1.1–1.6% / pp2048 +4.2% (Holm-corrected).

## Method notes

**★★ Put "before" and "after" on the same serve.** Six earlier experiments each
varied one factor across *different* serves and could never separate the factor
from the serve. The three-phase design settled in one run what those six could
not.

**★★ The pre-registered runner assertion was broken and nobody noticed.**
`v2_reeval.sh` printed `v2_markers=0` for all six serves. It looked like the
arms had silently run V1 — which would have invalidated the whole result. They
had not: the script grepped for `gpu/model_runner|ModelRunnerV2|V2 model runner`
while the actual log line is `Model Runner V2`, so the assertion could only ever
return 0. Re-checked against the retained `serve*/serve/head.log` with the
correct pattern: **3 markers in all six**, matching `gate_repro`'s V2 arm.
The conclusion stands, but an assertion that cannot fire is worse than none —
it reads as verification. Assert that the assertion *can* fail.

**This happened twice in one night.** The prefix-cache probe reported
`cached=0/27957` on sixteen consecutive requests, including byte-identical
repeats — i.e. it reported that its own experimental condition was never in
effect — and that readback was carried forward as "hits confirmed" anyway.
Both failures share a shape: a number was printed, nobody checked it was the
number that would appear if the setup were *wrong*, and a null result was
banked as a positive one. The countermeasure is the same in both cases — run
the check against the negative control and confirm it changes.

**★ 156 clean serial requests is the result, not a failed hunt.** It converts
"V2 has a mysterious recall bug" into "V2 has thinner margin under concurrency"
— a smaller, and much better-supported, claim.

**★ Pre-registered buckets must partition the outcome space.** The rule was
"[20,24] ⇒ gone, ≤13 ⇒ persists"; 14–19 was unbucketed and 5 of 6 serves landed
there. Registering a rule is not enough if it has a hole.

## Open — and one uncontrolled variable

Why V2 has less margin than V1 is **not** answered here, only bounded.

Two scheduler-level hypotheses were killed by reading the serve telemetry
rather than by running anything. At c=12 the engine logs:

```
Running: 12 reqs, Waiting: 0 reqs, GPU KV cache usage: 29.7%, Prefix cache hit rate: 83.8%
```

All twelve run concurrently, **nothing queues, and KV sits at 29.7%** of a
420,272-token pool (V1: 352,294; the 127K/162K figures in the 08-02 doc are
from the mml-49152 era). So there is no capacity pressure and no
preemption/recompute churn, and a planned 2×2 KV-capacity factorial was
cancelled before it burned an hour of GPU.

What that same line exposes is an **uncontrolled variable**. The gate builds
one prompt and sends the identical payload `concurrency × repeat_count` times,
so at c=12 the batch runs at **83.8% prefix-cache reuse** — while every serial
probe in Part 2 ran at a *reported* 0% reuse. The one condition that separates
passing from failing is the one never actually varied.

Next, in order:

1. **c=12 with prefix caching OFF, both runners.** If recall returns to ~24,
   the mechanism is prefix-block reuse, not batch numerics. Cheap and decisive.
2. **Serial with *verified* reuse** — same payload repeatedly, hit rate read
   from the serve log rather than from the response field. If that also fails,
   "concurrency-only" is wrong and the real variable is reuse, with concurrency
   merely being what creates it. Note phase 3 of Part 3 ran serially on a warm
   cache and passed 8/8, which argues reuse alone is not sufficient — but its
   readback is the same untrustworthy one, so it does not settle it.

Tracked in `project_v2_recall_bimodal_per_serve`.
