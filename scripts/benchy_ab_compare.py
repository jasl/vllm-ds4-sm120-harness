#!/usr/bin/env python3
"""Compare two llama-benchy arms against each other AND against the full history.

PRE-REGISTERED before any data was collected (commit this file first, then run
the arms). The point of writing it early is that the rule below cannot be
tuned after seeing which way the numbers fell -- which is the specific failure
that put a wrong default on two public branches on 2026-08-03.

The rule, per metric:

  DIFFERENT      the two arms' value ranges are DISJOINT *and* the gap between
                 them exceeds this metric's recorded historical spread. Both
                 conditions are required: benchy's own +/- is within-invocation
                 and runs 5-30x smaller than the build-to-build spread, so
                 disjoint ranges alone prove nothing at small n.
  NO DIFFERENCE  ranges overlap, AND each arm's spread is at most the historical
                 spread -- i.e. the measurement behaved normally and still saw
                 nothing.
  UNDERPOWERED   ranges overlap but at least one arm's own spread already
                 exceeds the historical spread. The run was too noisy to have
                 detected anything; this is NOT a null result and must not be
                 reported as one.

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


def verdict(a: list[float], b: list[float], hist_spread_pct: float) -> tuple[str, str]:
    """Apply the pre-registered rule. a=V1 values, b=V2 values."""
    if not a or not b:
        return "NO DATA", ""
    alo, ahi, blo, bhi = min(a), max(a), min(b), max(b)
    a_spread = 100 * (ahi - alo) / alo if len(a) > 1 else 0.0
    b_spread = 100 * (bhi - blo) / blo if len(b) > 1 else 0.0
    detail = f"V1 spread {a_spread:.1f}%, V2 spread {b_spread:.1f}%, hist {hist_spread_pct:.1f}%"

    disjoint = ahi < blo or bhi < alo
    if disjoint:
        gap = (blo - ahi) if ahi < blo else (alo - bhi)
        base = min(ahi, bhi)
        gap_pct = 100 * gap / base
        if gap_pct > hist_spread_pct:
            faster = "V2" if blo > ahi else "V1"
            return "DIFFERENT", f"{faster} higher, gap {gap_pct:.1f}% > hist {hist_spread_pct:.1f}%"
        return "UNDERPOWERED", f"disjoint but gap {gap_pct:.1f}% <= hist {hist_spread_pct:.1f}%"

    if max(a_spread, b_spread) > hist_spread_pct:
        return "UNDERPOWERED", detail + " -- an arm is noisier than history"
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

    history = collect_history(args.exclude)
    hist_spread = {}
    for k, entries in history.items():
        vals = [v for v, _ in entries]
        hist_spread[k] = 100 * (max(vals) - min(vals)) / min(vals)

    metrics = sorted(
        {k for _, m in v1 + v2 for k in m},
        key=lambda s: (ORDER.index(s.split(" @ ")[0]) if s.split(" @ ")[0] in ORDER else 9,
                       int(s.rsplit("d", 1)[-1])),
    )

    print(f"V1 runs: {len(v1)}  ({', '.join(p for p, _ in v1)})")
    print(f"V2 runs: {len(v2)}  ({', '.join(p for p, _ in v2)})")
    print()
    hdr = f"{'metric':<17} {'V1 range':>19} {'V2 range':>19} {'hist':>7}  verdict"
    print(hdr)
    print("-" * len(hdr))

    tally: dict[str, int] = defaultdict(int)
    for k in metrics:
        a = [m[k] for _, m in v1 if k in m]
        b = [m[k] for _, m in v2 if k in m]
        hs = hist_spread.get(k, 0.0)
        v, why = verdict(a, b, hs)
        tally[v] += 1
        fa = f"{min(a):.1f}-{max(a):.1f}" if a else "-"
        fb = f"{min(b):.1f}-{max(b):.1f}" if b else "-"
        print(f"{k:<17} {fa:>19} {fb:>19} {hs:>6.1f}%  {v}")
        if why:
            print(f"{'':<17} {'':>19} {'':>19} {'':>7}  ({why})")

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
                v, _ = verdict(a, b, hist_spread.get(k, 0.0))
                if v == "DIFFERENT":
                    bits.append(k)
            print(f"  {pair}: {'DIFFERENT on ' + ', '.join(bits) if bits else 'no metric differs'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
