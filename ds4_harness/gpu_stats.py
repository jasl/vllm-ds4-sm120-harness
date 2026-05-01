from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


def _normalize_key(key: str) -> str:
    key = re.sub(r"\s*\[[^\]]+\]", "", key.strip().casefold())
    key = key.replace(".", "_")
    return re.sub(r"[^a-z0-9]+", "_", key).strip("_")


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.casefold() in {"n/a", "na", "not supported", "[not supported]"}:
        return None
    text = re.sub(r"\s*(mib|w|%)\s*$", "", text, flags=re.IGNORECASE)
    try:
        return float(text)
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


def _percent(value: float | None, total: float | None) -> float | None:
    if value is None or total is None or total <= 0:
        return None
    return round((value / total) * 100, 2)


def _set_metric(
    output: dict[str, Any],
    name: str,
    values: list[float],
    *,
    include_avg: bool = True,
) -> None:
    maximum = _maximum(values)
    if maximum is not None:
        output[f"{name}_max"] = maximum
    average = _average(values) if include_avg else None
    if average is not None:
        output[f"{name}_avg"] = average


def summarize_gpu_csv(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {
            "available": False,
            "reason": f"missing or empty CSV: {path}",
            "sample_count": 0,
            "overall": {},
            "gpus": {},
        }

    raw_by_gpu: dict[str, dict[str, Any]] = {}
    sample_count = 0
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            normalized = {_normalize_key(key): value for key, value in row.items()}
            index = str(normalized.get("index") or "unknown").strip()
            data = raw_by_gpu.setdefault(
                index,
                {
                    "name": "",
                    "uuid": "",
                    "timestamps": [],
                    "memory_used_mib": [],
                    "memory_total_mib": [],
                    "memory_used_percent": [],
                    "power_draw_w": [],
                    "power_limit_w": [],
                    "gpu_utilization_percent": [],
                },
            )
            sample_count += 1
            if normalized.get("name"):
                data["name"] = str(normalized["name"]).strip()
            if normalized.get("uuid"):
                data["uuid"] = str(normalized["uuid"]).strip()
            if normalized.get("timestamp"):
                data["timestamps"].append(str(normalized["timestamp"]).strip())

            memory_used = _to_float(normalized.get("memory_used"))
            memory_total = _to_float(normalized.get("memory_total"))
            power_draw = _to_float(normalized.get("power_draw"))
            power_limit = _to_float(normalized.get("power_limit"))
            gpu_utilization = _to_float(normalized.get("utilization_gpu"))

            if memory_used is not None:
                data["memory_used_mib"].append(memory_used)
            if memory_total is not None:
                data["memory_total_mib"].append(memory_total)
            used_percent = _percent(memory_used, memory_total)
            if used_percent is not None:
                data["memory_used_percent"].append(used_percent)
            if power_draw is not None:
                data["power_draw_w"].append(power_draw)
            if power_limit is not None:
                data["power_limit_w"].append(power_limit)
            if gpu_utilization is not None:
                data["gpu_utilization_percent"].append(gpu_utilization)

    gpus: dict[str, dict[str, Any]] = {}
    for index, data in raw_by_gpu.items():
        timestamps = data["timestamps"]
        gpu_summary: dict[str, Any] = {
            "index": index,
            "name": data["name"],
            "uuid": data["uuid"],
            "samples": len(timestamps)
            or max(
                len(data["memory_used_mib"]),
                len(data["power_draw_w"]),
                len(data["gpu_utilization_percent"]),
            ),
        }
        if timestamps:
            gpu_summary["timestamp_start"] = timestamps[0]
            gpu_summary["timestamp_end"] = timestamps[-1]
        _set_metric(gpu_summary, "memory_used_mib", data["memory_used_mib"])
        _set_metric(gpu_summary, "memory_total_mib", data["memory_total_mib"], include_avg=False)
        _set_metric(gpu_summary, "memory_used_percent", data["memory_used_percent"])
        _set_metric(gpu_summary, "power_draw_w", data["power_draw_w"])
        _set_metric(gpu_summary, "power_limit_w", data["power_limit_w"], include_avg=False)
        _set_metric(
            gpu_summary,
            "gpu_utilization_percent",
            data["gpu_utilization_percent"],
        )
        gpus[index] = gpu_summary

    overall_values: dict[str, list[float]] = {
        "memory_used_mib": [],
        "memory_used_percent": [],
        "power_draw_w": [],
        "gpu_utilization_percent": [],
    }
    for data in raw_by_gpu.values():
        for key in overall_values:
            overall_values[key].extend(data[key])

    overall: dict[str, Any] = {}
    for key, values in overall_values.items():
        _set_metric(overall, key, values)

    return {
        "available": bool(sample_count),
        "sample_count": sample_count,
        "overall": overall,
        "gpus": gpus,
    }


def write_gpu_json(path: Path, summary: dict[str, Any]) -> None:
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


def write_gpu_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = ["# GPU Stats Summary", ""]
    if not summary.get("available"):
        lines.extend(
            [
                "- Available: no",
                f"- Reason: {summary.get('reason', 'no samples')}",
                "",
            ]
        )
    else:
        overall = summary.get("overall", {})
        lines.extend(
            [
                "- Available: yes",
                f"- Samples: {summary.get('sample_count', 0)}",
                f"- Max memory used: {_format_value(overall.get('memory_used_mib_max'), ' MiB')}",
                f"- Max power draw: {_format_value(overall.get('power_draw_w_max'), ' W')}",
                "",
                "| GPU | Samples | Max memory | Max memory % | Avg power | Max power | Max util |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for index, gpu in sorted(summary.get("gpus", {}).items()):
            label = gpu.get("name") or f"GPU {index}"
            if gpu.get("uuid"):
                label = f"{label} ({gpu['uuid']})"
            lines.append(
                " | ".join(
                    [
                        f"| {label}",
                        str(gpu.get("samples", 0)),
                        _format_value(gpu.get("memory_used_mib_max"), " MiB"),
                        _format_value(gpu.get("memory_used_percent_max"), "%"),
                        _format_value(gpu.get("power_draw_w_avg"), " W"),
                        _format_value(gpu.get("power_draw_w_max"), " W"),
                        _format_value(gpu.get("gpu_utilization_percent_max"), "%"),
                    ]
                )
                + " |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
