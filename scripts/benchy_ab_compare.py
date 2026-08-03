#!/usr/bin/env python3
"""Compare two llama-benchy arms against each other AND against the full history.

PRE-REGISTERED before any data was collected (commit this file first, then run
the arms). The point of writing it early is that the rule below cannot be
tuned after seeing which way the numbers fell -- which is the specific failure
that put a wrong default on two public branches on 2026-08-03.

## Threshold correction, made 2026-08-03 after 2 of 16 runs, before ANY comparison

The first version of this file tested the gap against the 12-run HISTORICAL
spread (ctx_pp 4.1-10.0%, pp2048 3.7-14.8%). That is the wrong yardstick and it
was too conservative by 2-4x on exactly the metric this experiment is about.

Those 12 runs span different vLLM SHAs, a model change (pre-0731 -> 0731) and a
speculator change (MTP2 -> DSpark nst=5). Their spread is build + model + pair +
drift + repeat noise. This A/B holds all of those fixed -- same build, same
night, both arms inside one node pair -- so it only has to beat the BOOT-TO-BOOT
REPEAT term. Pooling the archive's three same-build repeat sets (07-17 x2,
07-21 x2, 07-27 x3; df=4) separates them:

  metric            within-build CV   12-run CV   blocking gain
  ctx_pp  @d8192          0.57%          1.58%        2.8x
  ctx_pp  @d16384         0.39%          1.07%        2.8x
  ctx_pp  @d32768         0.53%          2.33%        4.4x
  pp2048  @d8192          1.31%          1.79%        1.4x
  pp2048  @d16384         1.01%          1.22%        1.2x
  pp2048  @d32768         1.21%          3.39%        2.8x
  ctx_tg  @d8192          3.46%          3.39%        1.0x
  ctx_tg  @d16384         2.30%          8.28%        3.6x
  ctx_tg  @d32768         2.41%          5.25%        2.2x
  tg128   @d8192          4.93%          5.20%        1.1x
  tg128   @d16384         3.99%          6.54%        1.6x
  tg128   @d32768         7.85%          6.62%        0.8x

Timing matters for whether this rewrite is legitimate: it was made with one V1
arm and one V2 arm recorded, on two different pairs, and with no comparison
between them computed. The change follows from the archive's structure, not from
which way tonight's numbers fell. sigma has df=4, so every threshold below is
also reported against a 2.37x one-sided 95% upper bound; a verdict that survives
only at the point estimate is labelled as such.

tg128 is declared NOT RESOLVABLE up front, for either direction. Its
within-build CV equals its entire historical spread -- it is essentially pure
boot-to-boot noise with no structure for blocking to remove -- so no affordable
n rescues it. Reporting "V1 and V2 are at parity on tg128" would be a claim this
design cannot make.

The rule, per metric:

  NOT RESOLVABLE tg128, always. Numbers are printed for the record only.
  DIFFERENT      arm ranges DISJOINT *and* the gap exceeds the metric's
                 within-build CV x 2 (a ~2-sigma boot-to-boot separation).
                 Reported as ROBUST if it also clears the df=4 upper bound
                 (CV x 2 x 2.37), otherwise as MARGINAL.
  NO DIFFERENCE  ranges overlap AND both arms' own spreads are within the
                 within-build CV x 2 -- the measurement behaved as expected and
                 still saw nothing.
  UNDERPOWERED   ranges overlap but an arm is noisier than boot-to-boot repeat
                 noise predicts, or they are disjoint by less than the
                 threshold. NOT a null result.

Arms are also reported PER PAIR, because the two GB10 node pairs have disagreed
on an unrelated gate and their worktree binaries differ by a few bytes. If the
per-pair verdicts disagree, the cross-pair conclusion is withheld.

Usage:
    scripts/benchy_ab_compare.py --v1 a.out b.out --v2 c.out d.out
    scripts/benchy_ab_compare.py --v1 'out/lb_v1*' --v2 'out/lb_v2*'   (globbed by the shell)

File naming: a trailing "_<host>" in the stem is read as the pair label, e.g.
lb_v1_r1_jasl-spark-1.out -> pair "jasl-spark-1".
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from benchy_history_band import collect_history, parse  # noqa: E402

# Metric families in report order. Prefill first: it is the question, and it is
# the family benchy actually resolves (historical spread 3.7-14.8% vs 11.7-36.7%
# for decode).
ORDER = ["ctx_pp", "pp2048", "ctx_tg", "tg128"]

# Metrics with no structure for within-pair blocking to remove. Declared before
# the data, so a tg128 reading cannot be promoted to a finding after the fact.
UNRESOLVABLE = {"tg128"}

# df=4 one-sided 95% upper bound multiplier on the pooled within-build sigma.
SIGMA_HI = 2.37


def within_build_cv() -> dict[str, float]:
    """Pooled boot-to-boot CV, from experiment dirs holding >1 distinct run.

    A dir with several distinct measured value-sets is a same-build repeat set
    (the harness archives r1/r2/r3 of one head together), which is exactly the
    variance component this A/B has to beat.
    """
    import collections
    import statistics

    seen: dict[tuple, str] = {}
    for p in sorted(pathlib.Path("docs/sm120/experiments").rglob("*")):
        if p.suffix not in (".out", ".log"):
            continue
        metrics = parse(p)
        if metrics:
            seen.setdefault(tuple(sorted(metrics.items())),
                            p.relative_to("docs/sm120/experiments").parts[0])

    by_dir: dict[str, list[dict]] = collections.defaultdict(list)
    for key, d in seen.items():
        by_dir[d].append(dict(key))

    out: dict[str, float] = {}
    for k in {m for runs in by_dir.values() for r in runs for m in r}:
        num, df = 0.0, 0
        for runs in by_dir.values():
            vals = [r[k] for r in runs if k in r]
            if len(vals) > 1:
                mu = statistics.mean(vals)
                num += statistics.variance(vals) / mu**2 * (len(vals) - 1)
                df += len(vals) - 1
        if df:
            out[k] = (num / df) ** 0.5 * 100
    return out


def pair_of(path: pathlib.Path) -> str:
    stem = path.stem
    return stem.rsplit("_", 1)[-1] if "_" in stem else "?"


def load(paths: list[pathlib.Path]) -> list[tuple[str, dict[str, float]]]:
    out = []
    for p in paths:
        metrics = parse(p)
        if not metrics:
            print(f"  warning: no benchy rows in {p}, skipping", file=sys.stderr)
            continue
        out.append((pair_of(p), metrics))
    return out


def verdict(metric: str, a: list[float], b: list[float], cv: float) -> tuple[str, str]:
    """Apply the pre-registered rule. a=V1 values, b=V2 values, cv=within-build CV%."""
    if metric.split(" @ ")[0] in UNRESOLVABLE:
        return "NOT RESOLVABLE", f"within-build CV {cv:.1f}% ~ full historical spread"
    if not a or not b:
        return "NO DATA", ""

    thresh, thresh_hi = 2 * cv, 2 * cv * SIGMA_HI
    alo, ahi, blo, bhi = min(a), max(a), min(b), max(b)
    a_spread = 100 * (ahi - alo) / alo if len(a) > 1 else 0.0
    b_spread = 100 * (bhi - blo) / blo if len(b) > 1 else 0.0

    if ahi < blo or bhi < alo:
        gap = (blo - ahi) if ahi < blo else (alo - bhi)
        gap_pct = 100 * gap / min(ahi, bhi)
        higher = "V2" if blo > ahi else "V1"
        if gap_pct > thresh_hi:
            return "DIFFERENT (robust)", f"{higher} higher by >={gap_pct:.1f}%, clears {thresh_hi:.1f}% (sigma_hi)"
        if gap_pct > thresh:
            return "DIFFERENT (marginal)", f"{higher} higher by >={gap_pct:.1f}%, clears {thresh:.1f}% but not {thresh_hi:.1f}%"
        return "UNDERPOWERED", f"disjoint but gap {gap_pct:.1f}% <= 2xCV {thresh:.1f}%"

    detail = f"V1 spread {a_spread:.1f}%, V2 spread {b_spread:.1f}%, 2xCV {thresh:.1f}%"
    if max(a_spread, b_spread) > thresh:
        return "UNDERPOWERED", detail + " -- an arm exceeds boot-to-boot noise"
    return "NO DIFFERENCE", detail


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--v1", nargs="+", type=pathlib.Path, required=True)
    ap.add_argument("--v2", nargs="+", type=pathlib.Path, required=True)
    ap.add_argument("--exclude", help="skip history dirs containing this string")
    args = ap.parse_args()

    v1, v2 = load(args.v1), load(args.v2)
    if not v1 or not v2:
        print("need at least one usable run per arm", file=sys.stderr)
        return 2

    cvs = within_build_cv()
    if not cvs:
        print("no same-build repeat sets in the archive; cannot set a threshold",
              file=sys.stderr)
        return 2

    metrics = sorted(
        {k for _, m in v1 + v2 for k in m},
        key=lambda s: (ORDER.index(s.split(" @ ")[0]) if s.split(" @ ")[0] in ORDER else 9,
                       int(s.rsplit("d", 1)[-1])),
    )

    print(f"V1 runs: {len(v1)}  ({', '.join(p for p, _ in v1)})")
    print(f"V2 runs: {len(v2)}  ({', '.join(p for p, _ in v2)})")
    print()
    hdr = f"{'metric':<17} {'V1 range':>19} {'V2 range':>19} {'CV':>6}  verdict"
    print(hdr)
    print("-" * len(hdr))

    tally: dict[str, int] = defaultdict(int)
    for k in metrics:
        a = [m[k] for _, m in v1 if k in m]
        b = [m[k] for _, m in v2 if k in m]
        cv = cvs.get(k, 0.0)
        v, why = verdict(k, a, b, cv)
        tally[v] += 1
        fa = f"{min(a):.1f}-{max(a):.1f}" if a else "-"
        fb = f"{min(b):.1f}-{max(b):.1f}" if b else "-"
        print(f"{k:<17} {fa:>19} {fb:>19} {cv:>5.2f}%  {v}")
        if why:
            print(f"{'':<17} {'':>19} {'':>19} {'':>6}  ({why})")

    print()
    print("summary: " + ", ".join(f"{n}x {v}" for v, n in sorted(tally.items())))

    # Per-pair, so a pair effect cannot hide inside a pooled range.
    pairs = sorted({p for p, _ in v1 + v2})
    if len(pairs) > 1:
        print()
        print("per-pair (the pooled verdict above is only trustworthy if these agree):")
        for pair in pairs:
            pa = [m for p, m in v1 if p == pair]
            pb = [m for p, m in v2 if p == pair]
            if not pa or not pb:
                print(f"  {pair}: incomplete (V1 x{len(pa)}, V2 x{len(pb)})")
                continue
            bits = []
            for k in metrics:
                a = [m[k] for m in pa if k in m]
                b = [m[k] for m in pb if k in m]
                v, _ = verdict(k, a, b, cvs.get(k, 0.0))
                if v.startswith("DIFFERENT"):
                    bits.append(k)
            print(f"  {pair}: {'DIFFERENT on ' + ', '.join(bits) if bits else 'no metric differs'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
