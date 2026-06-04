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


def _float_value(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
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


def _row_candidate_region_work(row: Json) -> dict[str, Json]:
    work = row.get("candidate_region_work")
    if not isinstance(work, dict):
        return {}
    regions: dict[str, Json] = {}
    for region_name, values in work.items():
        region_key = _str_key(region_name)
        if region_key is None or not isinstance(values, dict):
            continue
        regions[region_key] = {
            "candidate_slots": _int_value(values.get("candidate_slots")) or 0,
            "effective_candidate_visits": (
                _int_value(values.get("effective_candidate_visits")) or 0
            ),
            "padding_candidate_visits": (
                _int_value(values.get("padding_candidate_visits")) or 0
            ),
        }
    return regions


def _summarize_candidate_region_work(rows: list[Json]) -> Json:
    totals: dict[str, Json] = {}
    for row in rows:
        for region, values in _row_candidate_region_work(row).items():
            region_totals = totals.setdefault(
                region,
                {
                    "candidate_slots": 0,
                    "effective_candidate_visits": 0,
                    "padding_candidate_visits": 0,
                },
            )
            region_totals["candidate_slots"] += int(values["candidate_slots"])
            region_totals["effective_candidate_visits"] += int(
                values["effective_candidate_visits"]
            )
            region_totals["padding_candidate_visits"] += int(
                values["padding_candidate_visits"]
            )

    summary: Json = {}
    for region, values in sorted(totals.items()):
        candidate_slots = int(values["candidate_slots"])
        padding = int(values["padding_candidate_visits"])
        summary[region] = {
            "candidate_slots": candidate_slots,
            "effective_candidate_visits": int(
                values["effective_candidate_visits"]
            ),
            "padding_candidate_visits": padding,
            "padding_ratio": _round_float(padding / candidate_slots)
            if candidate_slots
            else None,
        }
    return summary


def _summarize_stage_timings(rows: list[Json]) -> Json:
    stage_totals: Counter[str] = Counter()
    for row in rows:
        timings = row.get("stage_timings_ms")
        if not isinstance(timings, dict):
            continue
        for name, value in timings.items():
            stage_name = _str_key(name)
            stage_value = _float_value(value)
            if stage_name is None or stage_value is None:
                continue
            stage_totals[stage_name] += stage_value

    total = float(sum(stage_totals.values()))
    stages: Json = {}
    for name, value in sorted(stage_totals.items()):
        stages[name] = {
            "total": _round_float(float(value)),
            "ratio": _round_float(float(value) / total) if total else None,
        }
    dominant_stage = None
    if stage_totals:
        dominant_stage = max(stage_totals.items(), key=lambda item: item[1])[0]
    return {
        "total": _round_float(total) if stage_totals else None,
        "dominant_stage": dominant_stage,
        "stages": stages,
    }


def _stage_total_ms(timings: Json, stage_name: str) -> float | None:
    stages = timings.get("stages")
    if not isinstance(stages, dict):
        return None
    stage = stages.get(stage_name)
    if not isinstance(stage, dict):
        return None
    return _float_value(stage.get("total"))


def _summarize_stage_efficiency(work: Json, timings: Json) -> Json:
    effective = _int_value(work.get("effective_candidate_visits")) or 0
    slots = _int_value(work.get("candidate_slots")) or 0
    total_ms = _float_value(timings.get("total"))
    sparse_ms = _stage_total_ms(timings, "sparse_accumulate")

    def visits_per_s(visits: int, elapsed_ms: float | None) -> float | None:
        if not visits or elapsed_ms is None or elapsed_ms <= 0:
            return None
        return _round_float(float(visits) / (elapsed_ms / 1000.0))

    sparse_ms_per_million = None
    if effective and sparse_ms is not None and sparse_ms > 0:
        sparse_ms_per_million = _round_float(sparse_ms / (effective / 1_000_000.0))

    return {
        "effective_candidate_visits_per_s": visits_per_s(effective, total_ms),
        "sparse_accumulate_effective_candidate_visits_per_s": visits_per_s(
            effective,
            sparse_ms,
        ),
        "sparse_accumulate_ms_per_million_effective_visits": (
            sparse_ms_per_million
        ),
        "candidate_slots_per_s": visits_per_s(slots, total_ms),
    }


def _summarize_overlap_group_values(group_values: list[Json]) -> Json:
    groups = 0
    valid_candidates = 0
    unique_candidates = 0
    for values in group_values:
        if not isinstance(values, dict):
            continue
        groups += _int_value(values.get("groups")) or 0
        valid_candidates += _int_value(values.get("valid_candidates")) or 0
        unique_candidates += _int_value(values.get("unique_candidates")) or 0
    return {
        "groups": groups,
        "valid_candidates": valid_candidates,
        "unique_candidates": unique_candidates,
        "unique_to_valid_ratio": _round_float(
            unique_candidates / valid_candidates
        )
        if valid_candidates
        else None,
    }


def _summarize_overlap_groups(rows: list[Json], field: str) -> Json:
    grouped: dict[str, list[Json]] = {}
    for row in rows:
        overlap = row.get(field)
        if not isinstance(overlap, dict):
            continue
        groups = overlap.get("groups")
        if not isinstance(groups, dict):
            continue
        for group_size, values in groups.items():
            group_key = _str_key(group_size)
            if group_key is None or not isinstance(values, dict):
                continue
            grouped.setdefault(group_key, []).append(values)
    return {
        group_size: _summarize_overlap_group_values(values)
        for group_size, values in sorted(grouped.items(), key=lambda item: int(item[0]))
    }


def _summarize_overlap_region_groups(rows: list[Json]) -> Json:
    regions: dict[str, dict[str, list[Json]]] = {}
    for row in rows:
        overlap = row.get("candidate_region_overlap")
        if not isinstance(overlap, dict):
            continue
        for region_name, region_groups in overlap.items():
            if region_name == "sample_rows" or not isinstance(region_groups, dict):
                continue
            region_key = _str_key(region_name)
            if region_key is None:
                continue
            for group_size, values in region_groups.items():
                group_key = _str_key(group_size)
                if group_key is None or not isinstance(values, dict):
                    continue
                regions.setdefault(region_key, {}).setdefault(group_key, []).append(
                    values
                )
    return {
        region: {
            group_size: _summarize_overlap_group_values(values)
            for group_size, values in sorted(
                group_values.items(), key=lambda item: int(item[0])
            )
        }
        for region, group_values in sorted(regions.items())
    }


def _summarize_candidate_overlap(rows: list[Json]) -> Json:
    sample_rows = 0
    for row in rows:
        overlap = row.get("candidate_overlap")
        if isinstance(overlap, dict):
            sample_rows += _int_value(overlap.get("sample_rows")) or 0
    if sample_rows == 0:
        for row in rows:
            overlap = row.get("candidate_region_overlap")
            if isinstance(overlap, dict):
                sample_rows += _int_value(overlap.get("sample_rows")) or 0
    return {
        "sample_rows": sample_rows,
        "groups": _summarize_overlap_groups(rows, "candidate_overlap"),
        "regions": _summarize_overlap_region_groups(rows),
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
        timings = _summarize_stage_timings(group_rows)
        overlap = _summarize_candidate_overlap(group_rows)
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
                "stage_timings_ms": timings,
                "stage_efficiency": _summarize_stage_efficiency(work, timings),
                "candidate_overlap": overlap,
                "candidate_region_work": _summarize_candidate_region_work(
                    group_rows
                ),
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
    work = _summarize_candidate_work(rows)
    timings = _summarize_stage_timings(rows)
    return {
        "stats_path": stats_path.name,
        "row_count": len(rows),
        "skipped_line_count": skipped,
        "counts_by_stats_file": dict(sorted(stats_file_counts.items())),
        "counts_by_rank": dict(sorted(rank_counts.items())),
        "counts_by_cuda_device": dict(sorted(cuda_device_counts.items())),
        "counts_by_layer_type": dict(sorted(layer_type_counts.items())),
        "counts_by_compress_ratio": dict(sorted(ratio_counts.items())),
        "candidate_work": work,
        "stage_timings_ms": timings,
        "stage_efficiency": _summarize_stage_efficiency(work, timings),
        "candidate_overlap": _summarize_candidate_overlap(rows),
        "candidate_region_work": _summarize_candidate_region_work(rows),
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


def _format_stage_breakdown(timings: Any) -> str:
    if not isinstance(timings, dict):
        return "n/a"
    stages = timings.get("stages")
    if not isinstance(stages, dict) or not stages:
        return "n/a"
    parts = []
    for name, values in stages.items():
        if not isinstance(values, dict):
            continue
        total = _format_number(values.get("total"))
        ratio = values.get("ratio")
        if isinstance(ratio, float):
            parts.append(f"`{name}`={total}ms/{ratio:.2%}")
        else:
            parts.append(f"`{name}`={total}ms")
    return ", ".join(parts) if parts else "n/a"


def _candidate_overlap_rows(overlap: Any) -> list[tuple[str, str, Json]]:
    if not isinstance(overlap, dict):
        return []
    rows: list[tuple[str, str, Json]] = []
    groups = overlap.get("groups")
    if isinstance(groups, dict):
        for group_size, values in sorted(groups.items(), key=lambda item: int(item[0])):
            if isinstance(values, dict):
                rows.append(("all", str(group_size), values))
    regions = overlap.get("regions")
    if isinstance(regions, dict):
        for region, region_groups in sorted(regions.items()):
            if not isinstance(region_groups, dict):
                continue
            for group_size, values in sorted(
                region_groups.items(), key=lambda item: int(item[0])
            ):
                if isinstance(values, dict):
                    rows.append((str(region), str(group_size), values))
    return rows


def _candidate_region_work_rows(work: Any) -> list[tuple[str, Json]]:
    if not isinstance(work, dict):
        return []
    return [
        (str(region), values)
        for region, values in sorted(work.items())
        if isinstance(values, dict)
    ]


def write_sparse_mla_stats_markdown(path: Path, report: Json) -> None:
    work = report.get("candidate_work", {})
    timings = report.get("stage_timings_ms", {})
    efficiency = report.get("stage_efficiency", {})
    overlap = report.get("candidate_overlap", {})
    region_work = report.get("candidate_region_work", {})
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
        (
            "- Stage timing total/dominant: "
            f"`{_format_number(timings.get('total'))}` ms / "
            f"`{_format_number(timings.get('dominant_stage'))}`"
        ),
        f"- Stage timing breakdown: {_format_stage_breakdown(timings)}",
        (
            "- Effective visits/s total/sparse-accumulate: "
            f"`{_format_number(efficiency.get('effective_candidate_visits_per_s'))}` / "
            f"`{_format_number(efficiency.get('sparse_accumulate_effective_candidate_visits_per_s'))}`"
        ),
        (
            "- Sparse accumulate ms per million effective visits: "
            f"`{_format_number(efficiency.get('sparse_accumulate_ms_per_million_effective_visits'))}`"
        ),
        "",
        "Only artifact file names and sanitized layer prefixes are reported.",
        "",
        "## Candidate Overlap",
        "",
        f"- Sample rows: `{_format_number(overlap.get('sample_rows'))}`",
        "",
        (
            "| Region | Group size | Groups | Valid candidates | Unique candidates | "
            "Unique/valid |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    overlap_rows = _candidate_overlap_rows(overlap)
    for region, group_size, values in overlap_rows:
        lines.append(
            "| "
            f"{region} | "
            f"{group_size} | "
            f"`{_format_number(values.get('groups'))}` | "
            f"`{_format_number(values.get('valid_candidates'))}` | "
            f"`{_format_number(values.get('unique_candidates'))}` | "
            f"`{_format_number(values.get('unique_to_valid_ratio'))}` |"
        )
    if not overlap_rows:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a |")
    lines.extend(
        [
            "",
            "## Candidate Region Work",
            "",
            (
                "| Region | Candidate slots | Effective visits | "
                "Padding visits | Padding ratio |"
            ),
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    region_work_rows = _candidate_region_work_rows(region_work)
    for region, values in region_work_rows:
        lines.append(
            "| "
            f"{region} | "
            f"`{_format_number(values.get('candidate_slots'))}` | "
            f"`{_format_number(values.get('effective_candidate_visits'))}` | "
            f"`{_format_number(values.get('padding_candidate_visits'))}` | "
            f"`{_format_number(values.get('padding_ratio'))}` |"
        )
    if not region_work_rows:
        lines.append("| n/a | n/a | n/a | n/a | n/a |")
    lines.extend(
        [
            "",
            "## Groups",
            "",
            (
                "| Layer type | Compress | Rows | Candidate slots | Effective visits | "
                "Padding ratio | Lens mean | Lens max | Stage total ms | "
                "Sparse visits/s | Dominant stage | Prefixes |"
            ),
            (
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | "
                "---: | --- | --- |"
            ),
        ]
    )
    for group in report.get("groups", []):
        group_timings = group.get("stage_timings_ms", {})
        group_efficiency = group.get("stage_efficiency", {})
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
            f"`{_format_number(group_timings.get('total'))}` | "
            f"`{_format_number(group_efficiency.get('sparse_accumulate_effective_candidate_visits_per_s'))}` | "
            f"`{_format_number(group_timings.get('dominant_stage'))}` | "
            f"{_format_prefixes(group.get('layer_prefixes'))} |"
        )
    if not report.get("groups"):
        lines.append(
            "| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
