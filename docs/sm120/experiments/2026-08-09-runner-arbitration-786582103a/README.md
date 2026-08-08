# Runner arbitration on `786582103a`: can V2 be the default?

Date: 2026-08-09. Tree `786582103a` = upstream/main merged (70 commits) +
the ported ghost-block guard (upstream PR #42359, adapted).
Prerequisite finding: [`../2026-08-08-prefix-reuse-defect/`](../2026-08-08-prefix-reuse-defect/README.md).

## Why this was re-opened

V1 has been the default since 2026-08-03 because V2's long-context recall could
collapse — c=12 landing at 3–5 of 24 with nothing predicting which serves would
be affected. That collapse is now understood and fixed: it was a prefix-cache
ghost-block race, not a property of the runner. With the fix in place the
comparison has to be made again, because the reason V1 was chosen no longer
holds.

## The fix works — this is the evidence the arbitration rests on

Same binary, same serve config, `VLLM_ALLOW_SPEC_DEC_SAME_STEP_PREFIX_HIT`
the only variable, cache populated by the real gate, 4 fresh serves per arm
(poisoning is ~50% per serve, so a single clean serve proves nothing):

| | serve 1 | serve 2 | serve 3 | serve 4 | mean | min |
|---|---|---|---|---|---|---|
| guard **off** (0/5 managers) | 22/23/24 | **6/5/3** | **14/9/10** | **7/8/7** | 11.5 | 3 |
| guard **on** (5/5 managers) | 23/22/21 | 20/22/20 | 22/23/23 | 23/22/23 | 22.0 | 20 |

Mann-Whitney U, p = 0.0043. Three of four unguarded serves degrade, two into
single digits; no guarded serve does. Every serve's runner and guard state was
read back from the serve log rather than assumed.

**The guard also helps V1**, which was not expected: V1's arthur c=12 was 20.7
without it (2026-08-08 baseline), 24.0 with prefix caching off entirely, and
23.0 with the guard on. So V1's own 2–4 needle shortfall was the same defect,
not an inherent concurrency margin — correcting what this investigation
concluded earlier in the day.

## Head-to-head, full suite

Both arms are the same tree, same guard mode, same phases; **the runner is the
only variable**. (benchy manages its own serves and ran guard-off in both arms,
so that row compares runners only.)

| metric | V1 | V2 | verdict |
|---|---|---|---|
| pp2048 d8192 / d16384 / d32768 | 1427.1 / 1363.0 / 1216.1 | **1471.8 / 1420.8 / 1302.6** | **V2 +3.1% / +4.2% / +7.1%** |
| tg128 mean | 39.95 / 41.16 / 35.25 | **41.56 / 49.61 / 45.18** | **V2 +4% / +20% / +28%** |
| e2e TTFT (ms) | 1437 / 1506 / 1689 | **1393 / 1444 / 1576** | V2 lower at every depth |
| GPU KV cache | 339,194 tok | **423,752 tok** | **V2 +24.9%** |
| issue19 instruction-following | PASS | PASS | tie |
| arthur c=1 | 2/2 | 2/2 | tie |
| GSM8K strict / flexible | 0.9378 / 0.9401 | 0.9401 / 0.9439 | tie (<0.4 pp, noise is ~1.1 pp) |
| multi-needle @42K/@80K | 48/48, 0 leaks | 48/48, 0 leaks (faster) | tie on correctness |
| draft acceptance length | 2.772 (n=253) | 2.710 (n=253) | tie — **and see below** |
| arthur c=12 | *4-serve arm below* | 22.0 (4 serves) | *see below* |

All six benchy numbers move the same way. pp2048's run-to-run sd is ~0.6% on
this rig, so +3.1/+4.2/+7.1% is well clear of resolution; tg128's sd is ~10%, so
its individual deltas are softer, but three-for-three in the same direction is
not what noise looks like.

### The `+6.6% draft acceptance` claim does not survive

Measured on the same formula over the same sample size, V1 is 2.772 and V2 is
2.710 — V2 slightly *lower*, not 6.6% higher. The original figure comes from the
2026-08-02 A/B, when V2 was very likely running poisoned; that comparison had no
clean basis. Treat acceptance as a tie and drop the claim.

## Arbitration criteria, fixed before the runs

1. **Recall not behind** — arthur c=12 bands overlap, and no single-digit serve.
2. **Quality not behind** — GSM8K within single-run noise, issue19 PASS,
   multi-needle 48/48 with zero leaks.
3. **Performance not behind** — pp2048 at least equal within benchy resolution.
4. **Claimed advantages real** — KV and acceptance measured, not quoted.

Criteria 2, 3 and 4 are settled: **2 tie, 3 is a clear V2 win, 4 is half-real**
(KV +24.9% confirmed; acceptance retracted).

## Criterion 1: settled by a dedicated 4-serve arm

The full suite gives 3 arthur samples per runner **from a single serve each**,
and the dominant variance axis is *across* serves. Its V1 23.0 vs V2 21.7 was a
1.3-needle gap measured below that design's resolution and could not decide
anything, so a dedicated 4-serve V1 arm was run, mirroring the guard A/B's V2
arm exactly:

| | serve means | gate mean | min | single-digit serves |
|---|---|---|---|---|
| V1 | 22.3 / 21.7 / 21.7 / 21.0 | **21.67** | 19 | 0 of 4 |
| V2 | 22.0 / 20.7 / 22.7 / 22.7 | **22.00** | 20 | 0 of 4 |

Mann-Whitney U (two-sided) **p = 0.697**; V2 is 0.33 needles *ahead*, which is
noise. The bands overlap almost completely. **Criterion 1 is met.**

## Verdict: V2 becomes the default

All four criteria are satisfied — recall indistinguishable, quality tied,
performance a clear V2 win, and one of the two claimed advantages confirmed
(KV +24.9%) while the other is retracted (acceptance). Landed as
`c054feedac`, tagged `sm120-pr-41834-stable-preview-20260809`.

**V1 stays supported.** `VLLM_USE_V2_MODEL_RUNNER=0` forces it and the env check
precedes every routing rule; a test pins both the default and the escape hatch.

### The guard is a deployment setting, not a shipped default

Defaulting `VLLM_ALLOW_SPEC_DEC_SAME_STEP_PREFIX_HIT` to 2 in `envs.py` was tried
and reverted after measuring it: `tests/v1/core` goes from 1 failure to 12,
because `test_prefix_caching.py` calls `allocate_slots` repeatedly to represent
*successive* scheduling steps while calling `new_step_starts()` once in the whole
file. With the guard on those look like one step and are correctly deferred. The
tests are step-agnostic rather than wrong, but flipping the default would fork 11
upstream tests and break every future test written the same way, for no benefit
that setting the variable in the deployment does not already give. The harness
serve script sets it (and forwards it to worker ranks) instead.

## Method notes

★ **Two arms that look identical can differ in one uncontrolled place.** The V1
arm's benchy phase ran guard-off (the guard env was only added to the gate
serves, and benchy manages its own), while the V2 arm's initially had it on.
Caught before the V2 arm started; both now run benchy guard-off so the runner is
the sole variable in that row.

★ **A silent `sed` miss nearly inverted the recall arm.** The V1 recall script
was patched from a stale local copy whose anchor text no longer matched, so the
runner substitution didn't apply while the loop rename did — it would have run
**V2 with the guard off** and reported it as V1's recall. Now patched from the
node's authoritative copy with an assert per replacement.

★ **The monitor stream is not authoritative.** `tail -F` re-emitted lines with
different values four times during these runs (e.g. a gate reported as both 22
and 24). Every number in this document was read from `SUMMARY.txt`.
