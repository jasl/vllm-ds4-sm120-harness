from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


MetricSeries = dict[tuple[str, str], list[float]]


def _to_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def _maximum(values: list[float]) -> float | None:
    if not values:
        return None
    return round(max(values), 2)


def _counter_delta(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    delta = values[-1] - values[0]
    return round(delta if delta >= 0 else values[-1], 2)


def _scale_percent(values: list[float]) -> list[float]:
    if values and max(values) <= 1.0:
        return [value * 100 for value in values]
    return values


def _metric_name_matches(name: str, needles: tuple[str, ...]) -> bool:
    normalized = name.casefold().replace(":", "_")
    return any(needle in normalized for needle in needles)


def _parse_prometheus_metrics(text: str) -> tuple[MetricSeries, int]:
    series: MetricSeries = defaultdict(list)
    snapshots = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if line.startswith("# DS4_HARNESS_SNAPSHOT"):
                snapshots += 1
            continue
        match = re.match(
            r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{([^}]*)\})?\s+([-+0-9.eE]+)\s*$",
            line,
        )
        if not match:
            continue
        name, labels, raw_value = match.groups()
        value = _to_float(raw_value)
        if value is None:
            continue
        series[(name, labels or "")].append(value)
    if snapshots == 0 and series:
        snapshots = max(len(values) for values in series.values())
    return series, snapshots


def _series_values(series: MetricSeries, needles: tuple[str, ...]) -> list[list[float]]:
    return [values for (name, _labels), values in series.items() if _metric_name_matches(name, needles)]


def _counter_delta_sum(series: MetricSeries, needles: tuple[str, ...]) -> float | None:
    matches = _series_values(series, needles)
    if not matches:
        return None
    return round(sum(_counter_delta(values) for values in matches), 2)


def _flatten_values(series: MetricSeries, needles: tuple[str, ...]) -> list[float]:
    values: list[float] = []
    for matched in _series_values(series, needles):
        values.extend(matched)
    return values


def summarize_metrics_file(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"available": False, "reason": "no metrics input"}
    if not path.exists() or path.stat().st_size == 0:
        return {"available": False, "reason": f"missing or empty metrics file: {path}"}

    series, snapshots = _parse_prometheus_metrics(path.read_text(encoding="utf-8"))
    if not series:
        return {"available": False, "reason": f"no Prometheus samples parsed from: {path}"}

    summary: dict[str, Any] = {
        "available": True,
        "sample_count": snapshots,
    }
    counter_specs = {
        "prefill_tokens_delta": ("prompt_tokens_total", "prefill_tokens_total"),
        "decode_tokens_delta": ("generation_tokens_total", "decode_tokens_total"),
        "successful_requests_delta": ("request_success_total", "requests_success_total"),
    }
    for output_key, needles in counter_specs.items():
        value = _counter_delta_sum(series, needles)
        if value is not None:
            summary[output_key] = value

    gauge_specs = {
        "running_requests": ("num_requests_running", "requests_running"),
        "waiting_requests": ("num_requests_waiting", "requests_waiting"),
        "prefill_throughput_tok_s": ("prompt_throughput", "prefill_throughput"),
        "decode_throughput_tok_s": ("generation_throughput", "decode_throughput"),
    }
    for output_key, needles in gauge_specs.items():
        values = _flatten_values(series, needles)
        maximum = _maximum(values)
        average = _average(values)
        if maximum is not None:
            summary[f"{output_key}_max"] = maximum
        if average is not None:
            summary[f"{output_key}_avg"] = average

    cache_values = _scale_percent(
        _flatten_values(series, ("gpu_cache_usage_perc", "gpu_kv_cache_usage"))
    )
    if cache_values:
        summary["gpu_kv_cache_usage_percent_max"] = _maximum(cache_values)
        summary["gpu_kv_cache_usage_percent_avg"] = _average(cache_values)

    return summary


_LOGGER_RE = re.compile(
    r"Avg prompt throughput:\s*([0-9.]+)\s*tokens/s,\s*"
    r"Avg generation throughput:\s*([0-9.]+)\s*tokens/s,\s*"
    r"Running:\s*([0-9.]+)\s*reqs,\s*Waiting:\s*([0-9.]+)\s*reqs,\s*"
    r"GPU KV cache usage:\s*([0-9.]+)%,\s*Prefix cache hit rate:\s*([0-9.]+)%",
)
_SPEC_RE = re.compile(
    r"Mean acceptance length:\s*([0-9.]+),\s*"
    r"Accepted throughput:\s*([0-9.]+)\s*tokens/s,\s*"
    r"Drafted throughput:\s*([0-9.]+)\s*tokens/s,\s*"
    r"Accepted:\s*([0-9.]+)\s*tokens,\s*Drafted:\s*([0-9.]+)\s*tokens,\s*"
    r"Per-position acceptance rate:\s*([^,]+(?:,\s*[^,]+)*),\s*"
    r"Avg Draft acceptance rate:\s*([0-9.]+)%",
)


def summarize_serve_log(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"available": False, "reason": "no serve log input"}
    if not path.exists() or path.stat().st_size == 0:
        return {"available": False, "reason": f"missing or empty serve log: {path}"}

    prefill: list[float] = []
    decode: list[float] = []
    running: list[float] = []
    waiting: list[float] = []
    kv_cache: list[float] = []
    prefix_cache: list[float] = []
    mean_acceptance_length: list[float] = []
    accepted_throughput: list[float] = []
    drafted_throughput: list[float] = []
    accepted_tokens: list[float] = []
    drafted_tokens: list[float] = []
    avg_draft_acceptance_rate: list[float] = []
    per_position_values: list[list[float]] = []

    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        logger_match = _LOGGER_RE.search(line)
        if logger_match:
            values = [float(value) for value in logger_match.groups()]
            prefill.append(values[0])
            decode.append(values[1])
            running.append(values[2])
            waiting.append(values[3])
            kv_cache.append(values[4])
            prefix_cache.append(values[5])
            continue

        spec_match = _SPEC_RE.search(line)
        if spec_match:
            (
                raw_mean_acceptance,
                raw_accepted_throughput,
                raw_drafted_throughput,
                raw_accepted_tokens,
                raw_drafted_tokens,
                raw_per_position,
                raw_avg_draft_acceptance,
            ) = spec_match.groups()
            mean_acceptance_length.append(float(raw_mean_acceptance))
            accepted_throughput.append(float(raw_accepted_throughput))
            drafted_throughput.append(float(raw_drafted_throughput))
            accepted_tokens.append(float(raw_accepted_tokens))
            drafted_tokens.append(float(raw_drafted_tokens))
            avg_draft_acceptance_rate.append(float(raw_avg_draft_acceptance))
            per_position_values.append(
                [float(value.strip()) for value in raw_per_position.split(",") if value.strip()]
            )

    if not prefill and not mean_acceptance_length:
        return {"available": False, "reason": f"no vLLM runtime log lines parsed from: {path}"}

    summary: dict[str, Any] = {
        "available": True,
        "samples": len(prefill),
    }
    metric_lists = {
        "prefill_throughput_tok_s": prefill,
        "decode_throughput_tok_s": decode,
        "running_requests": running,
        "waiting_requests": waiting,
        "gpu_kv_cache_usage_percent": kv_cache,
        "prefix_cache_hit_rate_percent": prefix_cache,
    }
    for key, values in metric_lists.items():
        maximum = _maximum(values)
        average = _average(values)
        if maximum is not None:
            summary[f"{key}_max"] = maximum
        if average is not None:
            summary[f"{key}_avg"] = average

    if mean_acceptance_length:
        position_count = max(len(values) for values in per_position_values)
        per_position_average = []
        for index in range(position_count):
            values = [row[index] for row in per_position_values if index < len(row)]
            if values:
                per_position_average.append(round(sum(values) / len(values), 3))
        summary["spec_decode"] = {
            "samples": len(mean_acceptance_length),
            "mean_acceptance_length_avg": _average(mean_acceptance_length),
            "mean_acceptance_length_max": _maximum(mean_acceptance_length),
            "accepted_throughput_tok_s_avg": _average(accepted_throughput),
            "accepted_throughput_tok_s_max": _maximum(accepted_throughput),
            "drafted_throughput_tok_s_avg": _average(drafted_throughput),
            "drafted_throughput_tok_s_max": _maximum(drafted_throughput),
            "accepted_tokens_observed": round(sum(accepted_tokens), 2),
            "drafted_tokens_observed": round(sum(drafted_tokens), 2),
            "avg_draft_acceptance_rate_percent_avg": _average(avg_draft_acceptance_rate),
            "per_position_acceptance_rate_avg": per_position_average,
        }

    return summary


def summarize_runtime_stats(
    metrics_input: Path | None = None,
    serve_log: Path | None = None,
) -> dict[str, Any]:
    return {
        "metrics": summarize_metrics_file(metrics_input),
        "serve_log": summarize_serve_log(serve_log),
    }


def write_runtime_json(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def _format_value(value: Any, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        if value.is_integer():
            return f"{value:.1f}{suffix}"
        return f"{value:.2f}{suffix}"
    return f"{value}{suffix}"


def write_runtime_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = ["# vLLM Runtime Stats Summary", ""]
    metrics = summary.get("metrics", {})
    lines.extend(["## Prometheus Metrics", ""])
    if not metrics.get("available"):
        lines.extend(["- Available: no", f"- Reason: {metrics.get('reason', 'no samples')}", ""])
    else:
        lines.extend(
            [
                "- Available: yes",
                f"- Samples: {metrics.get('sample_count', 0)}",
                f"- Prefill tokens delta: {_format_value(metrics.get('prefill_tokens_delta'))}",
                f"- Decode tokens delta: {_format_value(metrics.get('decode_tokens_delta'))}",
                f"- Max running requests: {_format_value(metrics.get('running_requests_max'))}",
                f"- Max waiting requests: {_format_value(metrics.get('waiting_requests_max'))}",
                (
                    "- Max GPU KV cache usage: "
                    f"{_format_value(metrics.get('gpu_kv_cache_usage_percent_max'), '%')}"
                ),
                "",
            ]
        )

    serve_log = summary.get("serve_log", {})
    lines.extend(["## Serve Log", ""])
    if not serve_log.get("available"):
        lines.extend(
            ["- Available: no", f"- Reason: {serve_log.get('reason', 'no samples')}", ""]
        )
    else:
        lines.extend(
            [
                "- Available: yes",
                f"- Samples: {serve_log.get('samples', 0)}",
                (
                    "- Avg prefill throughput: "
                    f"{_format_value(serve_log.get('prefill_throughput_tok_s_avg'), ' tok/s')}"
                ),
                (
                    "- Avg decode throughput: "
                    f"{_format_value(serve_log.get('decode_throughput_tok_s_avg'), ' tok/s')}"
                ),
                (
                    "- Max GPU KV cache usage: "
                    f"{_format_value(serve_log.get('gpu_kv_cache_usage_percent_max'), '%')}"
                ),
            ]
        )
        spec = serve_log.get("spec_decode")
        if isinstance(spec, dict):
            lines.extend(
                [
                    "",
                    "### Speculative Decoding",
                    "",
                    (
                        "- Mean acceptance length avg: "
                        f"{_format_value(spec.get('mean_acceptance_length_avg'))}"
                    ),
                    (
                        "- Accepted throughput avg: "
                        f"{_format_value(spec.get('accepted_throughput_tok_s_avg'), ' tok/s')}"
                    ),
                    (
                        "- Drafted throughput avg: "
                        f"{_format_value(spec.get('drafted_throughput_tok_s_avg'), ' tok/s')}"
                    ),
                    (
                        "- Per-position acceptance avg: "
                        f"{spec.get('per_position_acceptance_rate_avg', [])}"
                    ),
                ]
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
