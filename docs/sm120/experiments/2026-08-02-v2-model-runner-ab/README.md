# V1 vs V2 model runner on 0731 + DSpark

Status: accepted
Date: 2026-08-02
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
| arthur recall, c=12 | 23/24 | 22/24 | see below |
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

### arthur c=12: V1 23/24, V2 22/24

Both "fail" the gate's threshold, and both sit inside the 22–24/24 band this
branch has recorded for c=12 since the beginning — concurrency-dependent
reduction order under greedy + speculative decode, not a recall loss. The
discriminator for actual recall is c=1, where **both arms are exact at 2/2**.

V2 being one needle lower is inside that band and one sample. It is the softest
number in the table and it is not a blocker, but it is also not nothing: if V2
becomes the default, c=12 is worth watching across a few more runs.

## The one real functional regression, and it is silent

V2 **does not support the `thinking_token_budget` request parameter**, and the
way it does not support it matters:

```python
# vllm/config/vllm.py:2285-2289
if self.reasoning_config is not None:
    logger.warning_once(
        "Model Runner V2 does not yet support the thinking_token_budget "
        "request parameter. Set VLLM_USE_V2_MODEL_RUNNER=0 if this is required."
    )
```

That is a **startup `warning_once`**, not a per-request error. A request that
carries `thinking_token_budget` under V2 is accepted and the cap is silently
dropped — the client gets unbounded reasoning and no signal that its parameter
was ignored.

This does not affect our harness (nothing here sets it) but that is the wrong
test on a shared branch. `thinking_token_budget` is a public OpenAI-API sampling
parameter, DSv4 is a reasoning model, and this branch ships a DSv4 reasoning
parser — capping the thinking block is exactly what a downstream user of this
branch would reach for. An operator who misses one startup log line loses it on
every request thereafter.

## Interpretation

Measured against the stated bar, V2 does not merely reach parity — it is better
on the two axes that were in question (KV headroom, draft acceptance) and equal
on every correctness gate.

The argument against switching the default is therefore not about performance or
correctness. It is that the switch silently removes a public API parameter for
everyone else running this branch. That is a product decision rather than a
measurement one, and it was not part of the criterion set for this experiment,
so it is surfaced here rather than decided here.

If the default does move, the minimum accompanying change is to make the drop
loud — reject or warn per request when `thinking_token_budget` is set under V2 —
so that it fails visibly rather than quietly.

## Open

- Attribute the +4.70 GiB rather than only recording it.
- c=12 across more runs under V2, given 22/24 vs 23/24.
- Whether upstream has `thinking_token_budget` support for V2 in flight.
