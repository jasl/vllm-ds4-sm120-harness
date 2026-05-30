from __future__ import annotations

import re
import json
import subprocess
from pathlib import Path
from typing import Any


_METRIC_KEYS = {
    "Successful requests": "successful_requests",
    "Benchmark duration (s)": "benchmark_duration_s",
    "Total input tokens": "total_input_tokens",
    "Total generated tokens": "total_generated_tokens",
    "Request throughput (req/s)": "request_throughput_req_s",
    "Output token throughput (tok/s)": "output_token_throughput_tok_s",
    "Total Token throughput (tok/s)": "total_token_throughput_tok_s",
    "Mean TPOT (ms)": "mean_tpot_ms",
    "Median TPOT (ms)": "median_tpot_ms",
    "P99 TPOT (ms)": "p99_tpot_ms",
    "Mean ITL (ms)": "mean_itl_ms",
    "Median ITL (ms)": "median_itl_ms",
    "P99 ITL (ms)": "p99_itl_ms",
    "Mean TTFT (ms)": "mean_ttft_ms",
    "Median TTFT (ms)": "median_ttft_ms",
    "P99 TTFT (ms)": "p99_ttft_ms",
    "Acceptance rate (%)": "spec_acceptance_rate_percent",
    "Acceptance length": "spec_acceptance_length",
    "Drafts": "spec_drafts",
    "Draft tokens": "spec_draft_tokens",
    "Accepted tokens": "spec_accepted_tokens",
}


def _coerce_number(value: str) -> int | float:
    number = float(value.replace(",", ""))
    return int(number) if number.is_integer() else number


def parse_bench_output(output: str) -> dict[str, Any]:
    report: dict[str, Any] = {}
    per_position_acceptance: dict[int, int | float] = {}
    for line in output.splitlines():
        position_match = re.match(
            r"^\s*Position\s+(\d+):\s+([-+]?\d[\d,.]*)\s*$",
            line,
        )
        if position_match:
            raw_position, raw_value = position_match.groups()
            per_position_acceptance[int(raw_position)] = _coerce_number(raw_value)
            continue
        match = re.match(r"^([^:]+):\s+([-+]?\d[\d,.]*)\s*$", line.strip())
        if not match:
            continue
        raw_key, raw_value = match.groups()
        key = _METRIC_KEYS.get(raw_key.strip())
        if key is not None:
            report[key] = _coerce_number(raw_value)
    if per_position_acceptance:
        report["spec_per_position_acceptance_percent"] = [
            value for _, value in sorted(per_position_acceptance.items())
        ]
    return report


def run_bench_command(command: list[str], timeout: float | None = None) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        stdout = completed.stdout
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout_parts = []
        if exc.stdout:
            stdout_parts.append(
                exc.stdout.decode("utf-8", errors="replace")
                if isinstance(exc.stdout, bytes)
                else exc.stdout
            )
        if exc.stderr:
            stdout_parts.append(
                exc.stderr.decode("utf-8", errors="replace")
                if isinstance(exc.stderr, bytes)
                else exc.stderr
            )
        stdout_parts.append(f"\nTIMEOUT after {timeout} seconds\n")
        stdout = "".join(stdout_parts)
        returncode = -1
    except OSError as exc:
        stdout = f"{type(exc).__name__}: {exc}\n"
        returncode = -2
    return {
        "returncode": returncode,
        "metrics": parse_bench_output(stdout),
        "stdout": stdout,
        "command": command,
    }


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _round_or_none(value: float | None, digits: int = 2) -> float | None:
    return None if value is None else round(value, digits)


def _safe_divide(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return numerator / denominator


def _rows_by_concurrency(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    indexed: dict[int, dict[str, Any]] = {}
    for row in rows:
        try:
            concurrency = int(row.get("concurrency"))
        except (TypeError, ValueError):
            continue
        indexed[concurrency] = row
    return indexed


def compare_bench_rows(
    baseline_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    *,
    baseline_label: str,
    candidate_label: str,
) -> dict[str, Any]:
    """Build a concurrency-aligned TPOT/tok/s comparison.

    The naming is intentionally generic: callers can compare CUDA graph off/on,
    two branches, two kernels, or two hardware routes. The `batch_size` field is
    the vLLM `bench serve` max-concurrency value, matching the common serving
    benchmark shorthand used in SM120 reports.
    """
    baseline_by_c = _rows_by_concurrency(baseline_rows)
    candidate_by_c = _rows_by_concurrency(candidate_rows)
    rows = []
    for concurrency in sorted(set(baseline_by_c) | set(candidate_by_c)):
        baseline = baseline_by_c.get(concurrency, {})
        candidate = candidate_by_c.get(concurrency, {})
        baseline_metrics = baseline.get("metrics") or {}
        candidate_metrics = candidate.get("metrics") or {}
        baseline_tpot = _to_float(baseline_metrics.get("mean_tpot_ms"))
        candidate_tpot = _to_float(candidate_metrics.get("mean_tpot_ms"))
        baseline_output = _to_float(
            baseline_metrics.get("output_token_throughput_tok_s")
        )
        candidate_output = _to_float(
            candidate_metrics.get("output_token_throughput_tok_s")
        )
        baseline_spec_acceptance = _to_float(
            baseline_metrics.get("spec_acceptance_rate_percent")
        )
        candidate_spec_acceptance = _to_float(
            candidate_metrics.get("spec_acceptance_rate_percent")
        )
        rows.append(
            {
                "batch_size": concurrency,
                "concurrency": concurrency,
                "baseline_ok": baseline.get("ok"),
                "candidate_ok": candidate.get("ok"),
                "baseline_output_token_throughput_tok_s": baseline_output,
                "candidate_output_token_throughput_tok_s": candidate_output,
                "output_tok_s_speedup": _round_or_none(
                    _safe_divide(candidate_output, baseline_output)
                ),
                "baseline_mean_tpot_ms": baseline_tpot,
                "candidate_mean_tpot_ms": candidate_tpot,
                "tpot_speedup": _round_or_none(
                    _safe_divide(baseline_tpot, candidate_tpot)
                ),
                "baseline_mean_ttft_ms": _to_float(
                    baseline_metrics.get("mean_ttft_ms")
                ),
                "candidate_mean_ttft_ms": _to_float(
                    candidate_metrics.get("mean_ttft_ms")
                ),
                "baseline_spec_acceptance_rate_percent": baseline_spec_acceptance,
                "candidate_spec_acceptance_rate_percent": candidate_spec_acceptance,
                "spec_acceptance_ratio": _round_or_none(
                    _safe_divide(
                        candidate_spec_acceptance,
                        baseline_spec_acceptance,
                    ),
                    digits=4,
                ),
            }
        )
    return {
        "baseline_label": baseline_label,
        "candidate_label": candidate_label,
        "rows": rows,
    }


def find_bench_regressions(
    comparison: dict[str, Any],
    *,
    min_output_speedup: float,
    min_tpot_speedup: float,
    min_spec_acceptance_ratio: float | None = None,
    min_spec_acceptance_percent: float | None = None,
) -> list[dict[str, Any]]:
    regressions: list[dict[str, Any]] = []
    for row in comparison.get("rows", []):
        concurrency = row.get("concurrency")
        if row.get("baseline_ok") is not True:
            regressions.append(
                {
                    "concurrency": concurrency,
                    "metric": "baseline_ok",
                    "value": row.get("baseline_ok"),
                    "threshold": True,
                }
            )
        if row.get("candidate_ok") is not True:
            regressions.append(
                {
                    "concurrency": concurrency,
                    "metric": "candidate_ok",
                    "value": row.get("candidate_ok"),
                    "threshold": True,
                }
            )

        output_speedup = _to_float(row.get("output_tok_s_speedup"))
        if output_speedup is None or output_speedup < min_output_speedup:
            regressions.append(
                {
                    "concurrency": concurrency,
                    "metric": "output_tok_s_speedup",
                    "value": output_speedup,
                    "threshold": min_output_speedup,
                }
            )

        tpot_speedup = _to_float(row.get("tpot_speedup"))
        if tpot_speedup is None or tpot_speedup < min_tpot_speedup:
            regressions.append(
                {
                    "concurrency": concurrency,
                    "metric": "tpot_speedup",
                    "value": tpot_speedup,
                    "threshold": min_tpot_speedup,
                }
            )

        if min_spec_acceptance_ratio is not None:
            spec_acceptance_ratio = _to_float(row.get("spec_acceptance_ratio"))
            if (
                spec_acceptance_ratio is None
                or spec_acceptance_ratio < min_spec_acceptance_ratio
            ):
                regressions.append(
                    {
                        "concurrency": concurrency,
                        "metric": "spec_acceptance_ratio",
                        "value": spec_acceptance_ratio,
                        "threshold": min_spec_acceptance_ratio,
                    }
                )

        if min_spec_acceptance_percent is not None:
            candidate_spec_acceptance = _to_float(
                row.get("candidate_spec_acceptance_rate_percent")
            )
            if (
                candidate_spec_acceptance is None
                or candidate_spec_acceptance < min_spec_acceptance_percent
            ):
                regressions.append(
                    {
                        "concurrency": concurrency,
                        "metric": "spec_acceptance_rate_percent",
                        "value": candidate_spec_acceptance,
                        "threshold": min_spec_acceptance_percent,
                    }
                )
    return regressions


def add_bench_performance_gate(
    comparison: dict[str, Any],
    *,
    min_output_speedup: float,
    min_tpot_speedup: float,
    min_spec_acceptance_ratio: float | None = None,
    min_spec_acceptance_percent: float | None = None,
) -> dict[str, Any]:
    regressions = find_bench_regressions(
        comparison,
        min_output_speedup=min_output_speedup,
        min_tpot_speedup=min_tpot_speedup,
        min_spec_acceptance_ratio=min_spec_acceptance_ratio,
        min_spec_acceptance_percent=min_spec_acceptance_percent,
    )
    comparison["performance_gate"] = {
        "ok": len(regressions) == 0,
        "min_output_speedup": min_output_speedup,
        "min_tpot_speedup": min_tpot_speedup,
        "min_spec_acceptance_ratio": min_spec_acceptance_ratio,
        "min_spec_acceptance_percent": min_spec_acceptance_percent,
        "regressions": regressions,
    }
    return comparison


def load_bench_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"bench JSON must be a list: {path}")
    return [row for row in data if isinstance(row, dict)]


def write_bench_comparison_markdown(path: Path, comparison: dict[str, Any]) -> None:
    baseline_label = str(comparison.get("baseline_label") or "baseline")
    candidate_label = str(comparison.get("candidate_label") or "candidate")
    lines = [
        "# Bench Comparison",
        "",
        (
            "Concurrency is reported as batch size for compatibility with "
            "serving benchmark summaries."
        ),
        "",
        "| BS/C | "
        f"{baseline_label} tok/s | {candidate_label} tok/s | tok/s speedup | "
        f"{baseline_label} TPOT ms | {candidate_label} TPOT ms | TPOT speedup | "
        f"{baseline_label} TTFT ms | {candidate_label} TTFT ms | "
        f"{baseline_label} spec acc % | {candidate_label} spec acc % | "
        "spec acc ratio |",
        (
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: "
            "| ---: | ---: | ---: |"
        ),
    ]
    for row in comparison.get("rows", []):
        lines.append(
            f"| {row.get('batch_size')} | "
            f"{_format_number(row.get('baseline_output_token_throughput_tok_s'))} | "
            f"{_format_number(row.get('candidate_output_token_throughput_tok_s'))} | "
            f"{_format_number(row.get('output_tok_s_speedup'))} | "
            f"{_format_number(row.get('baseline_mean_tpot_ms'))} | "
            f"{_format_number(row.get('candidate_mean_tpot_ms'))} | "
            f"{_format_number(row.get('tpot_speedup'))} | "
            f"{_format_number(row.get('baseline_mean_ttft_ms'))} | "
            f"{_format_number(row.get('candidate_mean_ttft_ms'))} | "
            f"{_format_number(row.get('baseline_spec_acceptance_rate_percent'))} | "
            f"{_format_number(row.get('candidate_spec_acceptance_rate_percent'))} | "
            f"{_format_number(row.get('spec_acceptance_ratio'))} |"
        )
    gate = comparison.get("performance_gate")
    if isinstance(gate, dict):
        lines.extend(
            [
                "",
                "## Performance Gate",
                "",
                f"- OK: `{gate.get('ok')}`",
                f"- Minimum tok/s speedup: `{_format_number(gate.get('min_output_speedup'))}`",
                f"- Minimum TPOT speedup: `{_format_number(gate.get('min_tpot_speedup'))}`",
                (
                    "- Minimum speculative acceptance ratio: "
                    f"`{_format_number(gate.get('min_spec_acceptance_ratio'))}`"
                ),
                (
                    "- Minimum speculative acceptance percent: "
                    f"`{_format_number(gate.get('min_spec_acceptance_percent'))}`"
                ),
            ]
        )
        regressions = gate.get("regressions")
        if isinstance(regressions, list) and regressions:
            lines.extend(
                [
                    "",
                    "| C | Metric | Value | Threshold |",
                    "| ---: | --- | ---: | ---: |",
                ]
            )
            for regression in regressions:
                if not isinstance(regression, dict):
                    continue
                lines.append(
                    f"| {regression.get('concurrency')} | "
                    f"{regression.get('metric')} | "
                    f"{_format_number(regression.get('value'))} | "
                    f"{_format_number(regression.get('threshold'))} |"
                )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _format_number(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return "n/a"
    return f"{number:.2f}"
