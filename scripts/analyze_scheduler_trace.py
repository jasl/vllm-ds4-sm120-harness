#!/usr/bin/env python3
"""Summarize a vLLM scheduler trace JSONL artifact."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ds4_harness.scheduler_trace import (  # noqa: E402
    build_scheduler_trace_report,
    write_scheduler_trace_report_json,
    write_scheduler_trace_report_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path, help="scheduler_trace.jsonl path")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    report = build_scheduler_trace_report(args.trace)
    if args.json_output is not None:
        write_scheduler_trace_report_json(args.json_output, report)
    if args.markdown_output is not None:
        write_scheduler_trace_report_markdown(args.markdown_output, report)
    if args.json_output is None and args.markdown_output is None:
        write_scheduler_trace_report_markdown(Path("-"), report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
