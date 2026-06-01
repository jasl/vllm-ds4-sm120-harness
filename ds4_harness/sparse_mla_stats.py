from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


Json = dict[str, Any]

EXPECTED_KIND = "deepseek_v4_sparse_mla_prefill_stats"


def _round_float(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 6)


def _int_value(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _str_key(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _safe_prefix(value: Any) -> str:
    text = str(value or "")
    if not text:
        return ""
    return Path(text).name


def _stats_files(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(path.glob("*.jsonl"))
    return [path]


def _load_sparse_mla_stats_rows(path: Path) -> tuple[list[Json], int]:
    rows: list[Json] = []
    skipped = 0
    for item in _stats_files(path):
        try:
            lines = item.read_text(encoding="utf-8").splitlines()
        except OSError:
            skipped += 1
            continue
        for line in lines:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue
            if not isinstance(data, dict) or data.get("kind") != EXPECTED_KIND:
                skipped += 1
                continue
            data = dict(data)
            data["_stats_file"] = item.name
            rows.append(data)
    return rows, skipped


def _row_candidate_work(row: Json) -> Json:
    query_tokens = _int_value(row.get("query_tokens")) or 0
    combined_topk = _int_value(row.get("combined_topk")) or 0
    combined_lens = row.get("combined_lens")
    combined_lens_sum = None
    combined_lens_count = None
    combined_lens_min = None
    combined_lens_max = None
    if isinstance(combined_lens, dict):
        combined_lens_sum = _int_value(combined_lens.get("sum"))
        combined_lens_count = _int_value(combined_lens.get("count"))
        combined_lens_min = _int_value(combined_lens.get("min"))
        combined_lens_max = _int_value(combined_lens.get("max"))

    candidate_slots = _int_value(row.get("candidate_slots"))
    if candidate_slots is None:
        candidate_slots = query_tokens * combined_topk

    effective_candidate_visits = _int_value(row.get("effective_candidate_visits"))
    if effective_candidate_visits is None:
        effective_candidate_visits = combined_lens_sum or 0

    padding_candidate_visits = _int_value(row.get("padding_candidate_visits"))
    if padding_candidate_visits is None:
        padding_candidate_visits = max(0, candidate_slots - effective_candidate_visits)

    return {
        "candidate_slots": candidate_slots,
        "effective_candidate_visits": effective_candidate_visits,
        "padding_candidate_visits": padding_candidate_visits,
        "combined_lens_count": combined_lens_count or 0,
        "combined_lens_sum": combined_lens_sum or 0,
        "combined_lens_min": combined_lens_min,
        "combined_lens_max": combined_lens_max,
    }


def _summarize_candidate_work(rows: list[Json]) -> Json:
    work_items = [_row_candidate_work(row) for row in rows]
    candidate_slots = sum(int(item["candidate_slots"]) for item in work_items)
    effective = sum(int(item["effective_candidate_visits"]) for item in work_items)
    padding = sum(int(item["padding_candidate_visits"]) for item in work_items)
    lens_count = sum(int(item["combined_lens_count"]) for item in work_items)
    lens_sum = sum(int(item["combined_lens_sum"]) for item in work_items)
    lens_mins = [
        int(item["combined_lens_min"])
        for item in work_items
        if item.get("combined_lens_min") is not None
    ]
    lens_maxes = [
        int(item["combined_lens_max"])
        for item in work_items
        if item.get("combined_lens_max") is not None
    ]
    return {
        "candidate_slots": candidate_slots,
        "effective_candidate_visits": effective,
        "padding_candidate_visits": padding,
        "padding_ratio": _round_float(padding / candidate_slots)
        if candidate_slots
        else None,
        "combined_lens_count": lens_count,
        "combined_lens_sum": lens_sum,
        "combined_lens_mean": _round_float(lens_sum / lens_count)
        if lens_count
        else None,
        "combined_lens_min": min(lens_mins) if lens_mins else None,
        "combined_lens_max": max(lens_maxes) if lens_maxes else None,
    }


def _group_sparse_mla_stats(rows: list[Json]) -> list[Json]:
    grouped: dict[tuple[str, str], list[Json]] = {}
    for row in rows:
        layer_type = _str_key(row.get("layer_type")) or "unknown"
        compress_ratio = _str_key(row.get("compress_ratio")) or "unknown"
        grouped.setdefault((layer_type, compress_ratio), []).append(row)

    groups: list[Json] = []
    for (layer_type, compress_ratio), group_rows in sorted(grouped.items()):
        work = _summarize_candidate_work(group_rows)
        groups.append(
            {
                "layer_type": layer_type,
                "compress_ratio": compress_ratio,
                "row_count": len(group_rows),
                "candidate_slots": work["candidate_slots"],
                "effective_candidate_visits": work["effective_candidate_visits"],
                "padding_candidate_visits": work["padding_candidate_visits"],
                "padding_ratio": work["padding_ratio"],
                "combined_lens_mean": work["combined_lens_mean"],
                "combined_lens_max": work["combined_lens_max"],
                "layer_prefixes": sorted(
                    {
                        _safe_prefix(row.get("layer_prefix"))
                        for row in group_rows
                        if _safe_prefix(row.get("layer_prefix"))
                    }
                ),
            }
        )
    return groups


def build_sparse_mla_stats_report(stats_path: Path) -> Json:
    rows, skipped = _load_sparse_mla_stats_rows(stats_path)
    rank_counts = Counter(
        str(rank)
        for row in rows
        if (rank := _str_key(row.get("rank"))) is not None
    )
    stats_file_counts = Counter(
        str(stats_file)
        for row in rows
        if (stats_file := _str_key(row.get("_stats_file"))) is not None
    )
    cuda_device_counts = Counter(
        str(cuda_device)
        for row in rows
        if (cuda_device := _str_key(row.get("cuda_device"))) is not None
    )
    layer_type_counts = Counter(
        str(layer_type)
        for row in rows
        if (layer_type := _str_key(row.get("layer_type"))) is not None
    )
    ratio_counts = Counter(
        str(ratio)
        for row in rows
        if (ratio := _str_key(row.get("compress_ratio"))) is not None
    )
    return {
        "stats_path": stats_path.name,
        "row_count": len(rows),
        "skipped_line_count": skipped,
        "counts_by_stats_file": dict(sorted(stats_file_counts.items())),
        "counts_by_rank": dict(sorted(rank_counts.items())),
        "counts_by_cuda_device": dict(sorted(cuda_device_counts.items())),
        "counts_by_layer_type": dict(sorted(layer_type_counts.items())),
        "counts_by_compress_ratio": dict(sorted(ratio_counts.items())),
        "candidate_work": _summarize_candidate_work(rows),
        "groups": _group_sparse_mla_stats(rows),
    }


def write_sparse_mla_stats_json(path: Path, report: Json) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


def _format_number(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _format_counts(counts: Json) -> str:
    if not counts:
        return "none"
    return ", ".join(f"`{key}`={value}" for key, value in counts.items())


def _format_prefixes(prefixes: Any) -> str:
    if not isinstance(prefixes, list) or not prefixes:
        return "n/a"
    return ", ".join(f"`{prefix}`" for prefix in prefixes[:4])


def write_sparse_mla_stats_markdown(path: Path, report: Json) -> None:
    work = report.get("candidate_work", {})
    lines = [
        "# Sparse MLA Prefill Stats Report",
        "",
        f"- Stats path: `{report.get('stats_path', '')}`",
        f"- Rows: `{report.get('row_count', 0)}`",
        f"- Skipped lines: `{report.get('skipped_line_count', 0)}`",
        f"- Stats files: {_format_counts(report.get('counts_by_stats_file', {}))}",
        f"- Ranks: {_format_counts(report.get('counts_by_rank', {}))}",
        f"- CUDA devices: {_format_counts(report.get('counts_by_cuda_device', {}))}",
        (
            "- Layer types: "
            f"{_format_counts(report.get('counts_by_layer_type', {}))}"
        ),
        (
            "- Compress ratios: "
            f"{_format_counts(report.get('counts_by_compress_ratio', {}))}"
        ),
        (
            "- Candidate slots: "
            f"`{_format_number(work.get('candidate_slots'))}`"
        ),
        (
            "- Effective candidate visits: "
            f"`{_format_number(work.get('effective_candidate_visits'))}`"
        ),
        (
            "- Padding candidate visits: "
            f"`{_format_number(work.get('padding_candidate_visits'))}`"
        ),
        f"- Padding ratio: `{_format_number(work.get('padding_ratio'))}`",
        (
            "- Combined lens mean/max: "
            f"`{_format_number(work.get('combined_lens_mean'))}` / "
            f"`{_format_number(work.get('combined_lens_max'))}`"
        ),
        "",
        "Only artifact file names and sanitized layer prefixes are reported.",
        "",
        "## Groups",
        "",
        (
            "| Layer type | Compress | Rows | Candidate slots | Effective visits | "
            "Padding ratio | Lens mean | Lens max | Prefixes |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for group in report.get("groups", []):
        lines.append(
            "| "
            f"`{group.get('layer_type', '')}` | "
            f"`{group.get('compress_ratio', '')}` | "
            f"`{group.get('row_count', '')}` | "
            f"`{_format_number(group.get('candidate_slots'))}` | "
            f"`{_format_number(group.get('effective_candidate_visits'))}` | "
            f"`{_format_number(group.get('padding_ratio'))}` | "
            f"`{_format_number(group.get('combined_lens_mean'))}` | "
            f"`{_format_number(group.get('combined_lens_max'))}` | "
            f"{_format_prefixes(group.get('layer_prefixes'))} |"
        )
    if not report.get("groups"):
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
