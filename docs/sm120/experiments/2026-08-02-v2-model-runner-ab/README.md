# V1 vs V2 model runner on 0731 + DSpark

Status: observation
Date: 2026-08-02
Owner/context: `67f0057da4`. Unblocked by jasl/vllm PR #36 — before that, V2 +
folded DSpark could not boot under an explicitly-named draft at all.

## Question

This branch defaults to the V1 runner and carries a standing claim that V2's
DSpark speculator "accepts more per step", with V1 kept as the default because
its long-context recall was the validated one. Both halves are worth re-testing:
the branch has moved a long way (41 upstream commits, the
`qnorm_rope_kv_insert` op split, FlashInfer 0.6.16), and MTP — the speculator
those claims were formed around — no longer exists on `0731`.

## Profile

2x GB10 (sm_121) TP=2, `deepseek-ai/DeepSeek-V4-Flash-0731`, DSpark nst=5
probabilistic, fp8 KV, prefix cache on, mml 49152, util 0.85, mnbt 8192,
block-size 256. Same head and serve config in both arms; the runner is the only
variable, and each arm asserts the runner actually in use from the serve log
rather than from the env var.

## Result

| | V1 (default) | V2 |
| --- | --- | --- |
| available KV | 17.24 GiB | **21.98 GiB** |
| KV tokens | 129,315 | **162,357** |
| draft acceptance, per-sample mean | 2.024 (n=9) | 2.125 (n=8) |
| draft acceptance, range | 1.82 – 2.19 | 1.93 – 2.22 |
| best sample / rate | 2.19 / 23.7% | 2.22 / 24.4% |
| arthur long-context recall, c=1 | PASS 2/2 | **PASS 2/2** |
| #19 instruction-following | PASS | PASS |

### KV capacity: +4.74 GiB, and this one is real

+27% KV, +33k tokens. This branch's measured noise on the available-KV figure is
~1.3 GiB (18.56 vs 17.29 GiB across two runs at one head, one version, one
config), so a 4.74 GiB gap is 3.6x the noise. On GB10, KV headroom is the binding
constraint, which makes this the most consequential number in the table.

Why it is larger is **not** established here. The plausible reading is that V2
carries a different set of persistent buffers, or profiles them differently, but
this experiment did not attribute it and should not be cited as if it had.

### Acceptance: direction supports the claim, statistics do not settle it

V2's mean is 0.10 higher (+5%) and its distribution is tighter and shifted up —
6 of V2's 8 samples are >= 2.15 against 1 of V1's 9. But a Mann-Whitney U on the
two samples gives U = 17 against a two-sided p=0.05 critical value of 15 for
n = 9, 8. **Not significant.** Suggestive, not shown.

To settle it would take more samples per arm, which is cheap (the probe is a few
minutes) and worth doing before anyone makes a routing decision on acceptance
alone. The KV difference does not need that treatment.

### Long-context recall no longer distinguishes the runners

V2 passes arthur c=1 at 2/2, exactly as V1 does. The historical reason for
keeping V1 as the default — "V1's recall is the validated one" — no longer
discriminates. Note this is c=1 only; concurrency-12 has separate
batch-numerics behaviour on this branch and was not re-run here.

## Interpretation

V2 looks better on the axis that matters most for GB10 (KV headroom), equal on
correctness, and possibly slightly better on acceptance. That is not yet a case
for switching the default: this is one run per arm on one config, and switching
the runner changes far more than the two things measured here. What it does say
is that the two historical reasons for preferring V1 — unvalidated recall, and
"V2 accepts more but we don't run it" — no longer describe the current tree.

## A defect in this experiment's own harness

The runner-identity guard was written as
`v2lines=$(grep -ac "Model Runner V2" "$hl" || echo 0)`. When grep matches
nothing it prints `0` **and** exits 1, so the fallback appends a second `0`; the
V1 arm's assertion then died with `[: 0\n0: integer expression expected` and did
not run. The measurement is still valid — the printed value confirms V1 saw zero
V2 log lines, which is what the guard was checking — but the guard itself was
inert on the arm where it mattered. Use `grep -ac ... | head -1` or
`$(( $(grep -ac ...) + 0 ))`, not `|| echo 0`.

## Open

- Attribute the +4.74 GiB rather than just recording it.
- More acceptance samples per arm to move the comparison off "suggestive".
- arthur at c=12 under V2; only c=1 was covered.
- V2 warns that it does not support `thinking_token_budget`; unexamined here.
