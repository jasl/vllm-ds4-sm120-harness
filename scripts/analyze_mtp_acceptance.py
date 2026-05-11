#!/usr/bin/env python3
"""Optional harness tool: distill MTP speculative-decoding acceptance data from
one or more `bench.json` files into a comparable cross-shape table.

Useful when chasing decode-rate ceilings: the per-position acceptance trace
shows whether MTP's gains are limited by draft quality (low position-0
acceptance), by drift after the first draft (high position-0 but collapsing
position-1), or by the configured `num_speculative_tokens` itself.

Usage:
    python3 scripts/analyze_mtp_acceptance.py \
        artifacts/.../bench_random_isl1024_osl512/bench.json \
        artifacts/.../bench_random_isl4096_osl512/bench.json \
        --label sm120_mtp2 \
        --output artifacts/.../mtp_acceptance_summary.md

Or as a one-shot directory recurse:
    python3 scripts/analyze_mtp_acceptance.py --recurse artifacts/...
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Iterable


def find_bench_files(roots: Iterable[Path]) -> list[Path]:
    out = []
    for r in roots:
        if r.is_file():
            out.append(r)
        elif r.is_dir():
            out.extend(sorted(r.rglob("bench.json")))
    return out


def parse_runs(path: Path):
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        print(f"skip {path}: {e}", file=sys.stderr)
        return []
    if isinstance(data, dict) and "runs" in data:
        runs = data["runs"]
    elif isinstance(data, list):
        runs = data
    else:
        runs = [data]
    return runs


def shape_label(path: Path, run: dict) -> str:
    parent = path.parent.name  # e.g. bench_random_isl4096_osl512
    cfg = run.get("config", {})
    isl = cfg.get("random_input_len") or "?"
    osl = cfg.get("random_output_len") or "?"
    ds = cfg.get("dataset_name") or "?"
    c = run.get("concurrency")
    if ds == "random":
        return f"random ISL={isl} OSL={osl} c={c}"
    return f"{ds} c={c} ({parent})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument(
        "--recurse",
        action="store_true",
        help="treat positional paths as roots and discover all bench.json under them",
    )
    ap.add_argument("--label", default="mtp")
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()

    if args.recurse:
        files = find_bench_files(args.paths)
    else:
        files = [p for p in args.paths if p.suffix == ".json"]

    lines = []
    lines.append(f"# MTP acceptance summary — {args.label}")
    lines.append("")
    lines.append(
        "| shape | accept_rate % | accept_len | pos0 % | pos1 % | drafts | accepted | TPOT ms |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    counts = {"total_runs": 0, "with_spec": 0}

    for f in files:
        for run in parse_runs(f):
            counts["total_runs"] += 1
            m = run.get("metrics", {}) or {}
            ar = m.get("spec_acceptance_rate_percent")
            if ar is None:
                continue  # not an MTP run
            counts["with_spec"] += 1
            alen = m.get("spec_acceptance_length", 0)
            per_pos = m.get("spec_per_position_acceptance_percent") or []
            pos0 = per_pos[0] if len(per_pos) > 0 else None
            pos1 = per_pos[1] if len(per_pos) > 1 else None
            drafts = m.get("spec_drafts", 0)
            acc_tokens = m.get("spec_accepted_tokens", 0)
            tpot = m.get("mean_tpot_ms", 0)
            shape = shape_label(f, run)
            p0 = f"{pos0:.1f}" if pos0 is not None else "—"
            p1 = f"{pos1:.1f}" if pos1 is not None else "—"
            lines.append(
                f"| {shape} | {ar:.1f} | {alen:.2f} | {p0} | {p1} | {drafts} | {acc_tokens} | {tpot:.2f} |"
            )

    if counts["with_spec"] == 0:
        lines.append("")
        lines.append("_No MTP bench rows found in the supplied files._")

    lines.append("")
    lines.append(
        f"_processed {counts['total_runs']} runs, {counts['with_spec']} with MTP spec metrics_"
    )

    # quick observations
    if counts["with_spec"]:
        lines.append("")
        lines.append("## Observations")
        lines.append("")
        lines.append(
            "- `pos0 %` is the share of first-position draft tokens accepted: high "
            "values (>70 %) suggest the draft head is well-tuned for the workload; "
            "low values (<50 %) flag a draft-quality ceiling."
        )
        lines.append(
            "- `pos1 %` is the second-position acceptance: a steep drop from pos0 "
            "to pos1 is the typical MTP pattern (the draft has less context to work "
            "with). If pos1 stays >50 %, raising `num_speculative_tokens` to 3 may "
            "be worth trying."
        )
        lines.append(
            "- `accept_len` ≈ 1 + (sum of per-position fractions) when "
            "`num_speculative_tokens=2`. Values close to 2.0 mean MTP is fully "
            "amortising the draft cost; values <1.7 mean MTP overhead is eating "
            "into the gain and the no-MTP path may be competitive."
        )

    out_text = "\n".join(lines) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out_text)
        print(f"wrote {args.output}")
    else:
        sys.stdout.write(out_text)


if __name__ == "__main__":
    main()
