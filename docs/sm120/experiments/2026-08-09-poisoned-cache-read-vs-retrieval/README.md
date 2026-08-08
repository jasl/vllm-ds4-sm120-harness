# What a poisoned prefix cache actually breaks: retrieval, not the KV

Date: 2026-08-09. Tree `c054feedac`, V2 runner, guard **deliberately off**
(`VLLM_ALLOW_SPEC_DEC_SAME_STEP_PREFIX_HIT=0`) — this run needs the defect
present. Closes the last question left open by
[`../2026-08-08-prefix-reuse-defect/`](../2026-08-08-prefix-reuse-defect/README.md).

## The question

The ghost-block race is understood and fixed. But *what* does a poisoned cache
serve? Two possibilities with very different implications:

- the cached KV holds wrong values, so anything read from it is corrupt; or
- the KV is fine and something about finding the right tokens in it fails.

The observation that made this worth answering: responses from a poisoned serve
are **fluent and coherent**. They do not garble. They just cannot find things.

## Why every earlier attempt failed

The cache state was classified with **one** gate request. In the poisoned state
the per-request failure rate is high but not 1; in the clean state it is not 0.
A single sample cannot tell those apart. One earlier run had gate #1 fail and
gate #2 pass with a single request between them, which reads as "the cache
healed" — and is equally consistent with two draws from one distribution. Every
conclusion built on that was withdrawn.

Here each state check is **6 serial requests**, and a read arm is only
interpretable when the checks on *both* sides of it say POISONED.

## Result

Poisoned by the real gate (which scored 10/24 on this serve):

| step | result |
|---|---|
| STATE #0 (after the poisoning gate) | **1/6 pass → POISONED** |
| FILL — quote lines 100/300/500/700 **by position** | **4/4 exact**, delta +0 on every line |
| STATE #1 | **1/6 pass → POISONED** |
| QUOTE — the three sentinel lines **by position** | **3/3 codes returned** |
| STATE #2 | **1/6 pass → POISONED** |
| HASH-BUST — one early char changed, **serial**, no reuse | **6/6 clean** |

Three independent 6-sample checks, all 1/6. The cache never left the poisoned
state while the read arms ran.

## What this establishes

**1. The damage is block-resident.** Changing one character early in the
document re-hashes block 0 and every chained block after it, so nothing is
reused. Serial, same process, same serve: **6/6**. The byte-identical document
keeps failing. So it is not process-wide state — it is the cached blocks.

The hash-bust arm was originally written to run 12-concurrent, which proved
nothing: that satisfies "no reuse" *and* "concurrent cold prefill" at once, and
the second is the original fault. Serial isolates the one variable.

**2. The KV content is intact.** On a cache confirmed poisoned by three checks,
asking for line 700 returns line 700 — verbatim, checksum-verified, delta 0.
Even the three sentinel lines the gate cannot find come back **3/3 when asked by
position**.

**3. What breaks is content-addressed retrieval.** Same cache, same request
shape, same serve: "what is on line 700" succeeds; "what is the first / middle /
final validation code" fails. The gate asks by content, and that is the query
form that dies.

This is why poisoned output reads as coherent. The model is not reading
corrupted values — it is reading correct values from the wrong places.

## What this does NOT establish

The natural mechanism is the sparse-attention **indexer**: DSv4 selects which
distant tokens to attend to, and a position-anchored query carries enough
positional signal that the needed blocks get selected regardless, while a
content search depends entirely on the indexer scoring the right far-away
tokens. Poisoning the indexer's own cached state would produce exactly this
split.

That is a hypothesis consistent with the data, **not** a demonstrated mechanism.
Establishing it needs direct observation of what the indexer selects on a
poisoned cache versus a clean one. Nothing here measures that.

## Method notes

★ **A dead serve read as a maximally poisoned cache.** A smoke test against a
stopped server produced six failed requests → verdict POISONED → the read arms
then crashed. "The serve did not answer" and "the cache is poisoned" were the
same reading. The probe now raises `Unreachable` on transport failure and exits
4, distinct from 3 (clean serve) and 0 (poisoned and interpretable). Found by
smoke-testing before the real run; on a real run it would only have shown up if
a serve happened to die mid-probe, and then as a very convincing "extreme
poisoning" result.

★ **The runner read a probe crash as a clean serve.** `ds4_harness` was not on
the import path, so the probe died at its first import and the caller counted it
as "this serve was not poisoned, try another" — which would have burned all six
serves and reported nothing found. Exit codes are now distinguished, and the
runner aborts on an unexpected one rather than treating it as a result.
