# V1 vs V2 model runner on 0731 + DSpark

Status: **rejected** — V1 remains the default. Switched in `7e2914ed40`,
reverted in `2fb22567c5` after deeper sampling of the c=12 cell.
Date: 2026-08-02, revised 2026-08-03
Owner/context: `67f0057da4`. Unblocked by jasl/vllm PR #36 — before that, V2 +
folded DSpark could not boot under an explicitly-named draft at all.

## Question

The decision rule set for this experiment was **parity**: if V2 matches V1,
switch to it, on the grounds that upstream keeps improving V2 while V1 is the
legacy path. So the experiment had to be able to *detect* non-parity — the first
pass could not, being one sample per gate, and it left the acceptance comparison
sitting at "not significant".

## Profile

2x GB10 (sm_121) TP=2, `deepseek-ai/DeepSeek-V4-Flash-0731`, DSpark nst=5
probabilistic, fp8 KV, prefix cache on, mml 49152, util 0.85, mnbt 8192,
block-size 256. Same head and serve config in both arms; the runner is the only
variable, and each arm asserts from the serve log which runner is actually live
rather than trusting the env var.

## Result

| | V1 (default) | V2 | verdict |
| --- | --- | --- | --- |
| available KV | 17.08 GiB | **21.78 GiB** | **V2 +4.70 GiB (+27.5%)** |
| KV tokens | 127,177 | **162,035** | V2 +34,858 |
| draft acceptance, mean | 1.967 (n=26) | **2.097 (n=24)** | **V2 +6.6%, p<0.05** |
| GSM8K flexible x3 | 0.9447 – 0.9500 | 0.9462 – 0.9500 | parity (overlap) |
| GSM8K strict x3 | 0.9416 – 0.9477 | 0.9424 – 0.9439 | parity (overlap) |
| tool-calling, 135 cases | 97% (263/270) | 97% (262/270) | parity |
| #19 instruction-following | PASS | PASS | parity |
| arthur recall, c=1 | PASS 2/2 | PASS 2/2 | parity |
| arthur recall, c=12 (n=1) | 23/24 | 22/24 | **misleading — see below** |
| arthur recall, c=12 (n=8) | 22.25 mean [20, 24] | **10.50 mean [6, 13]** | **V1, U=0** |
| illegal-access / assert lines | 0 | 0 | parity |
| serve boot wall | 402 s | 413 s | parity |

### Acceptance: the earlier "not significant" is now settled

The first pass gave Mann-Whitney U=17 against a critical 15 at n=9,8 — suggestive
and no more. With 3 probe rounds per arm (n=26 vs 24 after de-duplicating the
samples that rounds share at their boundaries) the same comparison gives
**U=186, z=-2.45, p<0.05**. V2's mean acceptance length is 2.097 against V1's
1.967.

So the branch's long-standing claim that V2's DSpark speculator accepts more per
step is **confirmed**, and it took adequate sampling rather than a better
argument to get there.

### KV: +4.70 GiB, measured twice

The first pass gave +4.74 GiB, this one +4.70 GiB, on separate serve pairs of
runs. Against a measured ~1.3 GiB run-to-run noise on this figure, two
independent agreeing measurements settle it. On GB10, KV headroom is the binding
constraint.

Why V2's footprint is smaller is still **not attributed**. It is recorded as a
result, not explained.

### arthur c=12: this row was read wrong, and it decides the experiment

The single-sample reading below is what I originally wrote:

> Both "fail" the gate's threshold, and both sit inside the 22–24/24 band this
> branch has recorded for c=12 since the beginning — concurrency-dependent
> reduction order under greedy + speculative decode, not a recall loss. V2 being
> one needle lower is inside that band and one sample.

Two things are wrong with it. The 22–24 band was recorded for **MTP2 on V1**, so
it is not the reference distribution for either arm here. And one sample per
runner cannot distinguish "inside a band" from "the top of a much worse
distribution" — with n=1 there is no distribution to be inside of.

Eight samples per arm, same serve, same head, DSpark on both:

```
V1  20 23 21 23 24 23 23 21     mean 22.25, range [20, 24]
V2  13 12  8 13 11  6 12  9     mean 10.50, range [ 6, 13]
```

Completely separated — V1's worst run beats V2's best — so Mann-Whitney gives
**U=0 at n=8,8**. V2 drops more than half the needles. c=1 stays exact (2/2) on
both, so this is specifically a **concurrency** failure, which is exactly what
the routing-site comment claimed.

The 22/24 in the table above was V2's tail, not V2's centre.

### 2026-08-04: this sampling is itself on the wrong axis

Kept above as written, because the correction is more useful than a rewrite.

Those eight samples per arm came from **one serve per arm**. On 2026-08-04 V2's
c=12 turned out to be **bimodal by serve instance** -- same build, same pair,
same gate config:

```
serve 1:  22 22 23          mean 22.3   (matches V1)
serve 2:   6  9  6  8  8    mean  7.4
serve 3:  23 23 24          mean 23.3
```

Tight within a serve, 3x apart across. So the n=8 above measured *within-serve*
variance while the quantity that actually varies is *across-serve*: n was raised
on the wrong axis, which is the original n=1 error one level up. V1 [20,24] vs
V2 [6,13] with U=0 is a comparison of two single serves that each landed
somewhere.

The **conclusion survives** -- V1 stays the default -- but for a stronger reason
than the one recorded here. It is not that V2 is uniformly worse; it is that
roughly half of V2 serves land in a state that loses two thirds of the needles,
with nothing predicting or detecting which. An unpredictable deficit is worse
operationally than a consistent one.

It probably also dissolves the pair disagreement in the Open list below: those
were likely different serves drawing different modes, not a property of the
hardware. See `2026-08-04` notes and the memory entry
`project_v2_recall_bimodal_per_serve`.

## A caveat I raised and then had to withdraw

I first reported `thinking_token_budget` as a **silent** functional regression
under V2, on the strength of this startup handler:

```python
# vllm/config/vllm.py:2285-2289
if self.reasoning_config is not None:
    logger.warning_once(
        "Model Runner V2 does not yet support the thinking_token_budget "
        "request parameter. Set VLLM_USE_V2_MODEL_RUNNER=0 if this is required."
    )
```

A `warning_once` at startup, plus a grep that found the only enforcement in
`vllm/v1/sample/thinking_budget_state.py` wired into the **V1** input batch,
looked like "accepted and quietly ignored". **That was wrong.** Upstream already
rejects the parameter per request, in the engine's shared input processor:

```python
# vllm/v1/engine/input_processor.py:121-126
if self.use_v2_model_runner:
    raise VLLMValidationError(
        "thinking_token_budget is not yet supported by the V2 "
        "model runner. Run vLLM with VLLM_USE_V2_MODEL_RUNNER=0 "
        "to use thinking_token_budget."
    )
```

A client that sets it under V2 gets a hard validation error naming the exact
remedy, not silently unbounded reasoning. The startup warning is an extra
operator-facing heads-up on top of that.

The parameter is genuinely unsupported under V2 — that part stands, and it is a
real reason a specific deployment might pin `VLLM_USE_V2_MODEL_RUNNER=0` — but it
fails loudly, so it is not the silent behaviour change I described and does not
weigh against a default switch. The lesson is narrow and repeatable: I searched
the worker for the enforcement site and stopped there, without checking the layer
above it that both runners share.

## Interpretation

**The default stays on V1.** It was moved to V2 in `7e2914ed40` and moved back
in `2fb22567c5` the same day, on the c=12 sampling above.

V2 is genuinely ahead on the two axes the experiment set out to test — KV
headroom (+4.70 GiB, +27.5%, measured twice) and draft acceptance (mean 2.097 vs
1.967, p<0.05) — and equal on GSM8K, tool-calling, #19, c=1 recall and engine
health. On a branch where KV headroom is the binding constraint, that is a real
pull. It is not worth losing half the needles under concurrency.

The routing-site comment this experiment was meant to overturn — "V2 collapses
under concurrency at long context" — **survives, and is now measured** rather
than asserted. V2 remains available with `VLLM_USE_V2_MODEL_RUNNER=1`, and is
worth retesting whenever upstream moves the runner, since the KV and acceptance
wins are real and would be worth having if the concurrency behaviour changes.

### What went wrong in the first pass

Not a bad measurement — a bad *comparison*. Every number in the Result table is
reproducible. The error was reading a single c=12 sample against a band recorded
on a different configuration, and treating "inside the band" as evidence when
n=1 admits no such statement. The two axes I sampled properly (acceptance, KV)
are the two that held up; the one I sampled once is the one that reversed the
conclusion.

Cost of the shortcut: a wrong default shipped to two public branches for a day.

## Open

- Attribute the +4.70 GiB rather than only recording it.
- Why V2 loses needles under concurrency at all — the failure is measured, not
  explained, and that is what an upstream report would need.
- The two node pairs disagree on the magnitude: `.116`/`.119` read 22/18/19
  where `.117`/`.118` read 6–13. Same commit, same config. Unexplained.
- Whether upstream has `thinking_token_budget` support for V2 in flight.
- No prefill/throughput comparison was run for either runner — benchy was never
  pointed at this A/B.
