#!/usr/bin/env python3
"""Compare a llama-benchy run against the FULL recorded history, not a subset.

Why this exists: the recurring failure on this branch is quoting a "historical
range" assembled by hand from whichever prior baselines were in front of me. That
range is always too narrow, so in-band readings get reported as wins and the one
genuinely out-of-band metric gets missed. On 2026-08-02 that produced a published
claim that ctx_pp was above its band (it was inside at every depth) while ctx_tg
@ d16384 sat 10.7% below its band, unreported.

The band here is min..max over every archived benchy table under
docs/sm120/experiments/, one entry per independent run. It is a coverage floor,
not a confidence interval: benchy's own +/- is the spread within one invocation
and runs 5-30x smaller than the build-to-build spread.

Usage:
    scripts/benchy_history_band.py path/to/new_run.out
    scripts/benchy_history_band.py path/to/new_run.out --exclude 2026-08-02
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections import defaultdict

ROW = re.compile(r"\|\s*([a-z0-9_]+ @ d\d+)\s*\|\s*([0-9.]+)\s*±")
EXPERIMENTS = pathlib.Path("docs/sm120/experiments")


def parse(path: pathlib.Path) -> dict[str, float]:
    """Read one benchy table. Later rows win; a run records each metric once."""
    try:
        text = path.read_text(errors="ignore")
    except OSError as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc
    return {m.group(1): float(m.group(2))
            for line in text.splitlines()
            if (m := ROW.search(line))}


def collect_history(exclude: str | None) -> dict[str, list[tuple[float, str]]]:
    """Dedupe by measured values, not by file or by directory.

    Both naive rules are wrong and in opposite directions. Per-file over-counts:
    a benchy chain archives one run into three files, which would triple-weight
    it. Per-directory under-counts: an experiment with r1/r2/r3 holds three
    genuinely independent runs, and collapsing them discards the very spread the
    band is meant to capture. Identical value-sets are one run; differing ones
    are separate runs, wherever they live.
    """
    seen: dict[tuple[tuple[str, float], ...], str] = {}
    for path in sorted(EXPERIMENTS.rglob("*")):
        if path.suffix not in (".out", ".log"):
            continue
        rel = path.relative_to(EXPERIMENTS).parts[0]
        if exclude and exclude in rel:
            continue
        metrics = parse(path)
        if metrics:
            seen.setdefault(tuple(sorted(metrics.items())), rel)

    history: dict[str, list[tuple[float, str]]] = defaultdict(list)
    for key, rel in seen.items():
        for metric, value in key:
            history[metric].append((value, rel))
    return history


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("run", type=pathlib.Path, help="benchy .out/.log to evaluate")
    ap.add_argument("--exclude", help="skip experiment dirs containing this string")
    args = ap.parse_args()

    if not EXPERIMENTS.is_dir():
        print(f"run me from the harness root ({EXPERIMENTS} not found)", file=sys.stderr)
        return 2

    try:
        current = parse(args.run)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 2
    if not current:
        print(f"no benchy rows found in {args.run}", file=sys.stderr)
        return 2

    history = collect_history(args.exclude)
    print(f"{'metric':18s} {'n':>3s} {'low':>9s} {'high':>9s} {'this run':>9s}  verdict")
    outside = 0
    for metric in sorted(current, key=lambda s: (s.split(" @ ")[0], int(s.split("d")[-1]))):
        values = [v for v, _ in history.get(metric, [])]
        value = current[metric]
        if not values:
            print(f"{metric:18s} {'-':>3s} {'':>9s} {'':>9s} {value:9.2f}  no history")
            continue
        low, high = min(values), max(values)
        if value > high:
            verdict, delta = "ABOVE", (value / high - 1) * 100
        elif value < low:
            verdict, delta = "BELOW", (value / low - 1) * 100
        else:
            verdict, delta = "inside", 0.0
        if verdict != "inside":
            outside += 1
            verdict = f"{verdict} {delta:+.1f}%"
        print(f"{metric:18s} {len(values):3d} {low:9.2f} {high:9.2f} {value:9.2f}  {verdict}")

    print(f"\n{outside} metric(s) outside the recorded band.")
    print("Band = min..max over all archived runs. Report BELOW readings as openly "
          "as ABOVE ones;\nan out-of-band single run is unresolved, not yet a regression.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
