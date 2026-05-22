from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


Json = dict[str, Any]


def _load_json(path: Path) -> Json | list[Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _phase_exit_codes(run_root: Path) -> list[Json]:
    path = run_root / "phase_exit_codes.tsv"
    if not path.exists():
        return []
    rows: list[Json] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            try:
                exit_code = int(row.get("exit_code", "1"))
            except ValueError:
                exit_code = 1
            rows.append(
                {
                    "variant": row.get("variant", ""),
                    "phase": row.get("phase", ""),
                    "exit_code": exit_code,
                    "artifact_dir": row.get("artifact_dir", ""),
                }
            )
    return rows


def _variant_dirs(run_root: Path) -> list[Path]:
    phase_rows = _phase_exit_codes(run_root)
    variants = sorted({row["variant"] for row in phase_rows if row.get("variant")})
    dirs = [run_root / variant for variant in variants if (run_root / variant).is_dir()]
    if dirs:
        return dirs
    return sorted(path for path in run_root.iterdir() if path.is_dir())


def _round_float(value: Any, digits: int = 3) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def _summary_rows(payload: Json | list[Any] | None) -> list[Json]:
    if isinstance(payload, dict) and isinstance(payload.get("summary"), list):
        return [row for row in payload["summary"] if isinstance(row, dict)]
    return []


def _collect_latency_rows(run_label: str, variant: str, phase: str, payload: Any) -> list[Json]:
    rows: list[Json] = []
    for row in _summary_rows(payload):
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "phase": phase,
                "prompt": row.get("prompt"),
                "cache_mode": row.get("cache_mode"),
                "concurrency": row.get("concurrency"),
                "requests": row.get("request_count"),
                "failures": row.get("failure_count"),
                "ttft_mean_s": _round_float(row.get("ttft_seconds_mean")),
                "ttft_max_s": _round_float(row.get("ttft_seconds_max")),
                "decode_mean_tps": _round_float(row.get("decode_tokens_per_second_mean")),
                "decode_min_tps": _round_float(row.get("decode_tokens_per_second_min")),
                "decode_max_tps": _round_float(row.get("decode_tokens_per_second_max")),
                "decode_min_max_ratio": _round_float(row.get("decode_tps_min_to_max_ratio")),
                "itl_p95_s": _round_float(row.get("p95_inter_chunk_seconds")),
                "itl_p99_s": _round_float(row.get("p99_inter_chunk_seconds")),
                "itl_max_s": _round_float(row.get("max_inter_chunk_seconds")),
                "prompt_tokens": _round_float(row.get("prompt_tokens_mean"), 0),
            }
        )
    return rows


def _collect_mixed_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    rows: list[Json] = []
    for row in _summary_rows(payload):
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "case": row.get("case"),
                "requests": row.get("request_count"),
                "failures": row.get("failure_count"),
                "primary_ttft_mean_s": _round_float(row.get("primary_ttft_seconds_mean")),
                "secondary_ttft_mean_s": _round_float(row.get("secondary_ttft_seconds_mean")),
                "decode_min_max_ratio": _round_float(row.get("decode_tps_min_to_max_ratio")),
                "secondary_itl_p95_s": _round_float(row.get("secondary_p95_inter_chunk_seconds")),
                "secondary_itl_p99_s": _round_float(row.get("secondary_p99_inter_chunk_seconds")),
                "secondary_start_vs_primary_ttft_s": _round_float(
                    row.get("secondary_start_after_primary_ttft_seconds")
                ),
            }
        )
    return rows


def _collect_streaming_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, dict) or not isinstance(payload.get("summary"), dict):
        return []
    summary = payload["summary"]
    return [
        {
            "run": run_label,
            "variant": variant,
            "cases": summary.get("case_count"),
            "requests": summary.get("request_count"),
            "failures": summary.get("failure_count"),
            "slow_cases": summary.get("slow_case_count"),
            "max_ttft_s": _round_float(summary.get("max_ttft_seconds")),
            "max_elapsed_s": _round_float(summary.get("max_elapsed_seconds")),
            "itl_p95_s": _round_float(summary.get("p95_inter_chunk_seconds")),
            "itl_p99_s": _round_float(summary.get("p99_inter_chunk_seconds")),
            "itl_max_s": _round_float(summary.get("max_inter_chunk_seconds")),
        }
    ]


def _collect_bench_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, list):
        return []
    rows: list[Json] = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "concurrency": row.get("concurrency"),
                "successful_requests": metrics.get("successful_requests"),
                "output_tps": _round_float(metrics.get("output_token_throughput_tok_s")),
                "ttft_mean_ms": _round_float(metrics.get("mean_ttft_ms")),
                "ttft_p99_ms": _round_float(metrics.get("p99_ttft_ms")),
                "itl_p99_ms": _round_float(metrics.get("p99_itl_ms")),
                "spec_acceptance_percent": _round_float(
                    metrics.get("spec_acceptance_rate_percent")
                ),
            }
        )
    return rows


def _collect_gsm8k_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        return []
    rows: list[Json] = []
    for task in payload["tasks"]:
        if not isinstance(task, dict):
            continue
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "task": task.get("task"),
                "exact_match_flexible": _round_float(task.get("exact_match_flexible"), 4),
                "exact_match_strict": _round_float(task.get("exact_match_strict"), 4),
            }
        )
    return rows


def _collect_prefill_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
        return []
    rows: list[Json] = []
    for row in payload["rows"]:
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "case": row.get("case"),
                "ok": row.get("ok"),
                "input_tps": _round_float(row.get("input_token_throughput_tok_s")),
                "ttft_mean_ms": _round_float(row.get("mean_ttft_ms")),
                "ttft_p99_ms": _round_float(row.get("p99_ttft_ms")),
                "successful_requests": row.get("successful_requests"),
            }
        )
    return rows


def _collect_prefix_cache_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, dict) or not isinstance(payload.get("summary"), dict):
        return []
    summary = payload["summary"]
    return [
        {
            "run": run_label,
            "variant": variant,
            "ok": payload.get("ok"),
            "health_status": payload.get("health_status"),
            "trials": summary.get("trial_count"),
            "failures": summary.get("failure_count"),
            "solo_hit_rate_mean": _round_float(summary.get("solo_hit_rate_mean"), 4),
            "concurrent_hit_rate_mean": _round_float(
                summary.get("concurrent_hit_rate_mean"), 4
            ),
        }
    ]


def summarize_run(label: str, run_root: Path) -> Json:
    run_root = run_root.resolve()
    result: Json = {
        "label": label,
        "run_root": str(run_root),
        "phase_exit_codes": _phase_exit_codes(run_root),
        "latency": [],
        "decode_concurrency": [],
        "mixed_arrival": [],
        "streaming_pressure": [],
        "short_bench": [],
        "gsm8k": [],
        "prefill_sweep": [],
        "prefix_cache_stress": [],
    }
    for variant_dir in _variant_dirs(run_root):
        variant = variant_dir.name
        latency = _load_json(
            variant_dir / "long_context_latency_matrix" / "long_context_latency_matrix.json"
        )
        result["latency"].extend(
            _collect_latency_rows(label, variant, "long_context_latency_matrix", latency)
        )

        decode = _load_json(
            variant_dir
            / "long_context_decode_concurrency"
            / "long_context_decode_concurrency.json"
        )
        result["decode_concurrency"].extend(
            _collect_latency_rows(label, variant, "long_context_decode_concurrency", decode)
        )

        mixed = _load_json(
            variant_dir / "long_context_mixed_arrival" / "long_context_mixed_arrival.json"
        )
        result["mixed_arrival"].extend(_collect_mixed_rows(label, variant, mixed))

        streaming = _load_json(
            variant_dir / "streaming_pressure_matrix" / "streaming_pressure_matrix.json"
        )
        result["streaming_pressure"].extend(
            _collect_streaming_rows(label, variant, streaming)
        )

        bench = _load_json(variant_dir / "bench_hf_mt_bench" / "bench.json")
        result["short_bench"].extend(_collect_bench_rows(label, variant, bench))

        gsm8k = _load_json(variant_dir / "eval_gsm8k" / "lm_eval_summary.json")
        result["gsm8k"].extend(_collect_gsm8k_rows(label, variant, gsm8k))

        prefill = _load_json(
            variant_dir / "bench_random_prefill_sweep" / "prefill_sweep_summary.json"
        )
        result["prefill_sweep"].extend(_collect_prefill_rows(label, variant, prefill))

        prefix = _load_json(variant_dir / "prefix_cache_stress" / "prefix_cache_stress.json")
        result["prefix_cache_stress"].extend(
            _collect_prefix_cache_rows(label, variant, prefix)
        )
    phase_codes = [row["exit_code"] for row in result["phase_exit_codes"]]
    result["ok"] = bool(phase_codes) and all(code == 0 for code in phase_codes)
    return result


def summarize_runs(runs: list[tuple[str, Path]]) -> Json:
    run_summaries = [summarize_run(label, path) for label, path in runs]
    return {
        "ok": all(run.get("ok") for run in run_summaries),
        "runs": run_summaries,
        "tradeoff_policy": {
            "primary": [
                "correctness and server stability must not regress",
                "C=1/C=2/C=4 latency and ITL are prioritized for edge deployment",
                "already-started decode stream fairness beats second cold-prefill TTFT",
            ],
            "secondary": [
                "large-concurrency throughput is tracked but does not dominate the tradeoff",
                "256K+ and four-card claims require external gates",
            ],
        },
    }


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    return str(value)


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    if not rows:
        return ["_No data._"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_fmt(value) for value in row) + " |")
    return lines


def write_summary_markdown(path: Path, summary: Json) -> None:
    lines = [
        "# SM120 User Feedback Matrix Summary",
        "",
        f"- OK: `{summary.get('ok')}`",
        "",
        "## Tradeoff Policy",
        "",
    ]
    for item in summary["tradeoff_policy"]["primary"]:
        lines.append(f"- Primary: {item}.")
    for item in summary["tradeoff_policy"]["secondary"]:
        lines.append(f"- Secondary: {item}.")
    lines.append("")

    phase_rows: list[list[Any]] = []
    latency_rows: list[list[Any]] = []
    decode_rows: list[list[Any]] = []
    mixed_rows: list[list[Any]] = []
    streaming_rows: list[list[Any]] = []
    bench_rows: list[list[Any]] = []
    gsm_rows: list[list[Any]] = []
    prefill_rows: list[list[Any]] = []
    prefix_rows: list[list[Any]] = []

    for run in summary["runs"]:
        for phase in run["phase_exit_codes"]:
            phase_rows.append(
                [run["label"], phase["variant"], phase["phase"], phase["exit_code"]]
            )
        for row in run["latency"]:
            latency_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["prompt"],
                    row["cache_mode"],
                    row["concurrency"],
                    row["failures"],
                    row["ttft_mean_s"],
                    row["ttft_max_s"],
                    row["decode_mean_tps"],
                    row["decode_min_max_ratio"],
                    row["itl_p99_s"],
                ]
            )
        for row in run["decode_concurrency"]:
            decode_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["prompt"],
                    row["cache_mode"],
                    row["concurrency"],
                    row["failures"],
                    row["ttft_mean_s"],
                    row["ttft_max_s"],
                    row["decode_mean_tps"],
                    row["decode_min_tps"],
                    row["decode_min_max_ratio"],
                    row["itl_p99_s"],
                ]
            )
        for row in run["mixed_arrival"]:
            mixed_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["case"],
                    row["failures"],
                    row["primary_ttft_mean_s"],
                    row["secondary_ttft_mean_s"],
                    row["decode_min_max_ratio"],
                    row["secondary_itl_p99_s"],
                ]
            )
        for row in run["streaming_pressure"]:
            streaming_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["requests"],
                    row["failures"],
                    row["slow_cases"],
                    row["max_ttft_s"],
                    row["itl_p99_s"],
                    row["itl_max_s"],
                ]
            )
        for row in run["short_bench"]:
            bench_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["concurrency"],
                    row["successful_requests"],
                    row["output_tps"],
                    row["ttft_p99_ms"],
                    row["itl_p99_ms"],
                    row["spec_acceptance_percent"],
                ]
            )
        for row in run["gsm8k"]:
            gsm_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["task"],
                    row["exact_match_flexible"],
                    row["exact_match_strict"],
                ]
            )
        for row in run["prefill_sweep"]:
            prefill_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["case"],
                    row["ok"],
                    row["input_tps"],
                    row["ttft_mean_ms"],
                    row["ttft_p99_ms"],
                ]
            )
        for row in run["prefix_cache_stress"]:
            prefix_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["ok"],
                    row["health_status"],
                    row["trials"],
                    row["failures"],
                    row["solo_hit_rate_mean"],
                    row["concurrent_hit_rate_mean"],
                ]
            )

    sections = [
        ("Phase Exit Codes", ["Run", "Variant", "Phase", "Exit"], phase_rows),
        (
            "Long-Context Latency",
            [
                "Run",
                "Variant",
                "Prompt",
                "Cache",
                "C",
                "Failures",
                "TTFT Mean s",
                "TTFT Max s",
                "Decode tok/s",
                "Decode Min/Max",
                "ITL P99 s",
            ],
            latency_rows,
        ),
        (
            "Decode-Concurrency",
            [
                "Run",
                "Variant",
                "Prompt",
                "Cache",
                "C",
                "Failures",
                "TTFT Mean s",
                "TTFT Max s",
                "Decode tok/s",
                "Decode Min tok/s",
                "Decode Min/Max",
                "ITL P99 s",
            ],
            decode_rows,
        ),
        (
            "Mixed Arrival",
            [
                "Run",
                "Variant",
                "Case",
                "Failures",
                "Primary TTFT s",
                "Secondary TTFT s",
                "Decode Min/Max",
                "Secondary ITL P99 s",
            ],
            mixed_rows,
        ),
        (
            "Streaming Pressure",
            [
                "Run",
                "Variant",
                "Requests",
                "Failures",
                "Slow Cases",
                "Max TTFT s",
                "ITL P99 s",
                "ITL Max s",
            ],
            streaming_rows,
        ),
        (
            "Short Bench",
            [
                "Run",
                "Variant",
                "C",
                "Successful",
                "Output tok/s",
                "TTFT P99 ms",
                "ITL P99 ms",
                "Spec Accept %",
            ],
            bench_rows,
        ),
        (
            "GSM8K",
            ["Run", "Variant", "Task", "Flexible EM", "Strict EM"],
            gsm_rows,
        ),
        (
            "Random Prefill Sweep",
            ["Run", "Variant", "Case", "OK", "Input tok/s", "TTFT Mean ms", "TTFT P99 ms"],
            prefill_rows,
        ),
        (
            "Prefix Cache Stress",
            [
                "Run",
                "Variant",
                "OK",
                "Health",
                "Trials",
                "Failures",
                "Solo Hit Rate",
                "Concurrent Hit Rate",
            ],
            prefix_rows,
        ),
    ]
    for title, headers, rows in sections:
        lines.extend(["", f"## {title}", ""])
        lines.extend(_markdown_table(headers, rows))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_run(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--run must use label=path")
    label, raw_path = value.split("=", 1)
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError("run label must not be empty")
    return label, Path(raw_path).expanduser()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", type=_parse_run, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args(argv)

    summary = summarize_runs(args.run)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_summary_markdown(args.markdown_output, summary)
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
