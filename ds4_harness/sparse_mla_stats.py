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


def _row_mqa_topk_work(row: Json) -> list[Json]:
    work = row.get("mqa_topk_work")
    if isinstance(work, dict):
        work = [work]
    if not isinstance(work, list):
        return []

    items: list[Json] = []
    for values in work:
        if not isinstance(values, dict):
            continue
        item: Json = {
            "path": _str_key(values.get("path")) or "unknown",
            "query_tokens": _int_value(values.get("query_tokens")) or 0,
            "kv_tokens": _int_value(values.get("kv_tokens")) or 0,
            "topk_tokens": _int_value(values.get("topk_tokens")) or 0,
            "valid_kv_visits": _int_value(values.get("valid_kv_visits")) or 0,
            "logits_elements": _int_value(values.get("logits_elements")) or 0,
            "logits_padding_elements": (
                _int_value(values.get("logits_padding_elements")) or 0
            ),
            "materialized_logits_bytes": (
                _int_value(values.get("materialized_logits_bytes")) or 0
            ),
            "peak_logits_bytes": _int_value(values.get("peak_logits_bytes")) or 0,
            "estimated_temp_bytes": (
                _int_value(values.get("estimated_temp_bytes")) or 0
            ),
            "mqa_logits_launches": (
                _int_value(values.get("mqa_logits_launches")) or 0
            ),
            "topk_merge_count": _int_value(values.get("topk_merge_count")) or 0,
        }
        elapsed_ms = _float_value(values.get("elapsed_ms"))
        if elapsed_ms is not None:
            item["elapsed_ms"] = elapsed_ms
        logits_elements = int(item["logits_elements"])
        valid_kv_visits = int(item["valid_kv_visits"])
        if not item["logits_padding_elements"]:
            item["logits_padding_elements"] = max(
                0,
                logits_elements - valid_kv_visits,
            )
        item["logits_valid_ratio"] = (
            _float_value(values.get("logits_valid_ratio"))
            if values.get("logits_valid_ratio") is not None
            else (
                float(valid_kv_visits) / float(logits_elements)
                if logits_elements
                else None
            )
        )
        item["logits_padding_ratio"] = (
            _float_value(values.get("logits_padding_ratio"))
            if values.get("logits_padding_ratio") is not None
            else (
                float(item["logits_padding_elements"]) / float(logits_elements)
                if logits_elements
                else None
            )
        )
        kv_span = values.get("kv_span")
        if isinstance(kv_span, dict):
            item["kv_span_count"] = _int_value(kv_span.get("count")) or 0
            item["kv_span_sum"] = _int_value(kv_span.get("sum")) or 0
            item["kv_span_min"] = _int_value(kv_span.get("min"))
            item["kv_span_max"] = _int_value(kv_span.get("max"))
        weight_sign = values.get("weight_sign")
        if isinstance(weight_sign, dict):
            item["weight_sign"] = {
                "count": _int_value(weight_sign.get("count")) or 0,
                "positive": _int_value(weight_sign.get("positive")) or 0,
                "negative": _int_value(weight_sign.get("negative")) or 0,
                "zero": _int_value(weight_sign.get("zero")) or 0,
                "min": _float_value(weight_sign.get("min")),
                "max": _float_value(weight_sign.get("max")),
                "abs_max": _float_value(weight_sign.get("abs_max")),
            }
        chunk_size = _int_value(values.get("chunk_size"))
        if chunk_size is not None:
            item["chunk_size"] = chunk_size
        torch_matmul_tiles = _int_value(values.get("torch_matmul_tiles"))
        if torch_matmul_tiles is not None:
            item["torch_matmul_tiles"] = torch_matmul_tiles
        items.append(item)
    return items


def _summarize_mqa_weight_signs(items: list[Json]) -> Json:
    count = 0
    positive = 0
    negative = 0
    zero = 0
    mins: list[float] = []
    maxes: list[float] = []
    abs_maxes: list[float] = []
    for item in items:
        weight_sign = item.get("weight_sign")
        if not isinstance(weight_sign, dict):
            continue
        item_count = _int_value(weight_sign.get("count")) or 0
        if item_count <= 0:
            continue
        count += item_count
        positive += _int_value(weight_sign.get("positive")) or 0
        negative += _int_value(weight_sign.get("negative")) or 0
        zero += _int_value(weight_sign.get("zero")) or 0
        item_min = _float_value(weight_sign.get("min"))
        item_max = _float_value(weight_sign.get("max"))
        item_abs_max = _float_value(weight_sign.get("abs_max"))
        if item_min is not None:
            mins.append(item_min)
        if item_max is not None:
            maxes.append(item_max)
        if item_abs_max is not None:
            abs_maxes.append(item_abs_max)
    if count == 0:
        return {}
    return {
        "count": count,
        "positive": positive,
        "negative": negative,
        "zero": zero,
        "positive_ratio": _round_float(positive / count),
        "negative_ratio": _round_float(negative / count),
        "zero_ratio": _round_float(zero / count),
        "min": min(mins) if mins else None,
        "max": max(maxes) if maxes else None,
        "abs_max": max(abs_maxes) if abs_maxes else None,
    }


def _summarize_mqa_topk_work(rows: list[Json]) -> Json:
    items: list[Json] = []
    for row in rows:
        items.extend(_row_mqa_topk_work(row))
    if not items:
        return {}

    path_counts: Counter[str] = Counter(str(item["path"]) for item in items)
    summary: Json = {
        "query_tokens": sum(int(item["query_tokens"]) for item in items),
        "valid_kv_visits": sum(int(item["valid_kv_visits"]) for item in items),
        "logits_elements": sum(int(item["logits_elements"]) for item in items),
        "logits_padding_elements": sum(
            int(item["logits_padding_elements"]) for item in items
        ),
        "materialized_logits_bytes": sum(
            int(item["materialized_logits_bytes"]) for item in items
        ),
        "peak_logits_bytes": max(int(item["peak_logits_bytes"]) for item in items),
        "estimated_temp_bytes": max(
            int(item["estimated_temp_bytes"]) for item in items
        ),
        "mqa_logits_launches": sum(
            int(item["mqa_logits_launches"]) for item in items
        ),
        "topk_merge_count": sum(int(item["topk_merge_count"]) for item in items),
        "kv_tokens_max": max(int(item["kv_tokens"]) for item in items),
        "topk_tokens_max": max(int(item["topk_tokens"]) for item in items),
        "counts_by_path": dict(sorted(path_counts.items())),
    }
    logits_elements = int(summary["logits_elements"])
    if logits_elements:
        summary["logits_valid_ratio"] = _round_float(
            int(summary["valid_kv_visits"]) / logits_elements
        )
        summary["logits_padding_ratio"] = _round_float(
            int(summary["logits_padding_elements"]) / logits_elements
        )
    kv_span_counts = [
        int(item.get("kv_span_count", 0))
        for item in items
        if int(item.get("kv_span_count", 0)) > 0
    ]
    if kv_span_counts:
        kv_span_sum = sum(int(item.get("kv_span_sum", 0)) for item in items)
        kv_span_count = sum(kv_span_counts)
        kv_span_mins = [
            int(item["kv_span_min"])
            for item in items
            if item.get("kv_span_min") is not None
        ]
        kv_span_maxes = [
            int(item["kv_span_max"])
            for item in items
            if item.get("kv_span_max") is not None
        ]
        summary["kv_span_count"] = kv_span_count
        summary["kv_span_sum"] = kv_span_sum
        summary["kv_span_mean"] = _round_float(kv_span_sum / kv_span_count)
        summary["kv_span_min"] = min(kv_span_mins) if kv_span_mins else None
        summary["kv_span_max"] = max(kv_span_maxes) if kv_span_maxes else None
    torch_tiles = sum(int(item.get("torch_matmul_tiles", 0)) for item in items)
    if torch_tiles:
        summary["torch_matmul_tiles"] = torch_tiles
    chunk_sizes = sorted(
        {
            int(item["chunk_size"])
            for item in items
            if item.get("chunk_size") is not None
        }
    )
    if chunk_sizes:
        summary["chunk_sizes"] = chunk_sizes
    elapsed_ms = sum(float(item.get("elapsed_ms", 0.0)) for item in items)
    if elapsed_ms:
        summary["elapsed_ms"] = _round_float(elapsed_ms)
    weight_sign = _summarize_mqa_weight_signs(items)
    if weight_sign:
        summary["weight_sign"] = weight_sign
    return summary


def _row_accumulate_work(row: Json) -> Json | None:
    work = row.get("accumulate_work")
    if not isinstance(work, dict):
        return None

    return {
        "path": _str_key(work.get("path")) or "unknown",
        "query_tokens": _int_value(work.get("query_tokens")) or 0,
        "effective_candidate_visits": (
            _int_value(work.get("effective_candidate_visits")) or 0
        ),
        "head_dim": _int_value(work.get("head_dim")) or 0,
        "local_heads": _int_value(work.get("local_heads")) or 0,
        "query_chunk_size": _int_value(work.get("query_chunk_size")) or 0,
        "topk_chunk_size": _int_value(work.get("topk_chunk_size")) or 0,
        "query_chunk_count": _int_value(work.get("query_chunk_count")) or 0,
        "topk_chunk_count": _int_value(work.get("topk_chunk_count")) or 0,
        "accumulate_kernel_launches": (
            _int_value(work.get("accumulate_kernel_launches")) or 0
        ),
        "candidate_score_elements": (
            _int_value(work.get("candidate_score_elements")) or 0
        ),
        "candidate_value_read_bytes_estimate": (
            _int_value(work.get("candidate_value_read_bytes_estimate")) or 0
        ),
        "q_read_bytes_estimate": (
            _int_value(work.get("q_read_bytes_estimate")) or 0
        ),
        "output_write_bytes_estimate": (
            _int_value(work.get("output_write_bytes_estimate")) or 0
        ),
        "state_workspace_bytes": (
            _int_value(work.get("state_workspace_bytes")) or 0
        ),
        "score_workspace_bytes": (
            _int_value(work.get("score_workspace_bytes")) or 0
        ),
    }


def _summarize_accumulate_work(rows: list[Json]) -> Json:
    items = [item for row in rows if (item := _row_accumulate_work(row))]
    if not items:
        return {}

    path_counts: Counter[str] = Counter(str(item["path"]) for item in items)
    topk_chunk_sizes = sorted(
        {
            int(item["topk_chunk_size"])
            for item in items
            if int(item["topk_chunk_size"]) > 0
        }
    )
    return {
        "query_tokens": sum(int(item["query_tokens"]) for item in items),
        "effective_candidate_visits": sum(
            int(item["effective_candidate_visits"]) for item in items
        ),
        "candidate_score_elements": sum(
            int(item["candidate_score_elements"]) for item in items
        ),
        "candidate_value_read_bytes_estimate": sum(
            int(item["candidate_value_read_bytes_estimate"]) for item in items
        ),
        "q_read_bytes_estimate": sum(
            int(item["q_read_bytes_estimate"]) for item in items
        ),
        "output_write_bytes_estimate": sum(
            int(item["output_write_bytes_estimate"]) for item in items
        ),
        "state_workspace_bytes": max(
            int(item["state_workspace_bytes"]) for item in items
        ),
        "score_workspace_bytes": max(
            int(item["score_workspace_bytes"]) for item in items
        ),
        "accumulate_kernel_launches": sum(
            int(item["accumulate_kernel_launches"]) for item in items
        ),
        "query_chunk_count": sum(int(item["query_chunk_count"]) for item in items),
        "topk_chunk_count": sum(int(item["topk_chunk_count"]) for item in items),
        "query_chunk_size_max": max(
            int(item["query_chunk_size"]) for item in items
        ),
        "topk_chunk_sizes": topk_chunk_sizes,
        "head_dim_max": max(int(item["head_dim"]) for item in items),
        "local_heads_max": max(int(item["local_heads"]) for item in items),
        "counts_by_path": dict(sorted(path_counts.items())),
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


def _summarize_duplicate_values(values_list: list[Json]) -> Json:
    sample_rows = 0
    valid_candidates = 0
    unique_candidates = 0
    duplicate_candidate_visits = 0
    rows_with_duplicates = 0
    for values in values_list:
        if not isinstance(values, dict):
            continue
        sample_rows += _int_value(values.get("sample_rows")) or 0
        valid_candidates += _int_value(values.get("valid_candidates")) or 0
        unique_candidates += _int_value(values.get("unique_candidates")) or 0
        duplicate_candidate_visits += (
            _int_value(values.get("duplicate_candidate_visits")) or 0
        )
        rows_with_duplicates += _int_value(values.get("rows_with_duplicates")) or 0
    return {
        "sample_rows": sample_rows,
        "valid_candidates": valid_candidates,
        "unique_candidates": unique_candidates,
        "duplicate_candidate_visits": duplicate_candidate_visits,
        "duplicate_visit_ratio": _round_float(
            duplicate_candidate_visits / valid_candidates
        )
        if valid_candidates
        else None,
        "rows_with_duplicates": rows_with_duplicates,
        "row_duplicate_ratio": _round_float(rows_with_duplicates / sample_rows)
        if sample_rows
        else None,
    }


def _summarize_candidate_row_duplicates(rows: list[Json]) -> Json:
    values_list: list[Json] = []
    regions: dict[str, list[Json]] = {}
    for row in rows:
        duplicates = row.get("candidate_row_duplicates")
        if not isinstance(duplicates, dict):
            continue
        values_list.append(duplicates)
        duplicate_regions = duplicates.get("regions")
        if not isinstance(duplicate_regions, dict):
            continue
        for region, values in duplicate_regions.items():
            region_key = _str_key(region)
            if region_key is None or not isinstance(values, dict):
                continue
            regions.setdefault(region_key, []).append(values)
    if not values_list:
        return {}
    summary = _summarize_duplicate_values(values_list)
    summary["regions"] = {
        region: _summarize_duplicate_values(values)
        for region, values in sorted(regions.items())
    }
    return summary


def _reuse_potential_row(values: Json, effective_visit_share: float | None) -> Json:
    valid = _int_value(values.get("valid_candidates")) or 0
    unique = _int_value(values.get("unique_candidates")) or 0
    reusable = max(0, valid - unique)
    return {
        "groups": _int_value(values.get("groups")) or 0,
        "sampled_valid_candidate_visits": valid,
        "sampled_union_candidate_visits": unique,
        "sampled_reusable_candidate_visits": reusable,
        "sampled_reuse_ratio": _round_float(reusable / valid) if valid else None,
        "unique_to_valid_ratio": _round_float(unique / valid) if valid else None,
        "effective_visit_share": _round_float(effective_visit_share),
    }


def _region_effective_visit_shares(region_work: Json) -> dict[str, float]:
    if not isinstance(region_work, dict):
        return {}
    effective_by_region: dict[str, int] = {}
    for region, values in region_work.items():
        if not isinstance(values, dict):
            continue
        region_key = _str_key(region)
        if region_key is None:
            continue
        effective_by_region[region_key] = (
            _int_value(values.get("effective_candidate_visits")) or 0
        )
    total = sum(effective_by_region.values())
    if not total:
        return {}
    return {
        region: effective / total
        for region, effective in effective_by_region.items()
        if effective
    }


def _summarize_cross_query_reuse_potential(
    overlap: Json,
    region_work: Json,
) -> Json:
    if not isinstance(overlap, dict):
        overlap = {}
    shares = _region_effective_visit_shares(region_work)
    regions: dict[str, Json] = {}

    groups = overlap.get("groups")
    if isinstance(groups, dict):
        regions["all"] = {
            str(group_size): _reuse_potential_row(values, 1.0)
            for group_size, values in sorted(
                groups.items(), key=lambda item: int(item[0])
            )
            if isinstance(values, dict)
        }

    overlap_regions = overlap.get("regions")
    if isinstance(overlap_regions, dict):
        for region, region_groups in sorted(overlap_regions.items()):
            if not isinstance(region_groups, dict):
                continue
            region_key = str(region)
            regions[region_key] = {
                str(group_size): _reuse_potential_row(
                    values,
                    shares.get(region_key),
                )
                for group_size, values in sorted(
                    region_groups.items(), key=lambda item: int(item[0])
                )
                if isinstance(values, dict)
            }

    return {
        "sample_rows": _int_value(overlap.get("sample_rows")) or 0,
        "regions": regions,
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
        region_work = _summarize_candidate_region_work(group_rows)
        row_duplicates = _summarize_candidate_row_duplicates(group_rows)
        accumulate_work = _summarize_accumulate_work(group_rows)
        mqa_topk_work = _summarize_mqa_topk_work(group_rows)
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
                "candidate_row_duplicates": row_duplicates,
                "accumulate_work": accumulate_work,
                "mqa_topk_work": mqa_topk_work,
                "cross_query_reuse_potential": (
                    _summarize_cross_query_reuse_potential(
                        overlap,
                        region_work,
                    )
                ),
                "candidate_region_work": region_work,
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
    overlap = _summarize_candidate_overlap(rows)
    region_work = _summarize_candidate_region_work(rows)
    row_duplicates = _summarize_candidate_row_duplicates(rows)
    accumulate_work = _summarize_accumulate_work(rows)
    mqa_topk_work = _summarize_mqa_topk_work(rows)
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
        "candidate_overlap": overlap,
        "candidate_row_duplicates": row_duplicates,
        "accumulate_work": accumulate_work,
        "mqa_topk_work": mqa_topk_work,
        "cross_query_reuse_potential": _summarize_cross_query_reuse_potential(
            overlap,
            region_work,
        ),
        "candidate_region_work": region_work,
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


def _cross_query_reuse_rows(reuse: Any) -> list[tuple[str, str, Json]]:
    if not isinstance(reuse, dict):
        return []
    regions = reuse.get("regions")
    if not isinstance(regions, dict):
        return []
    rows: list[tuple[str, str, Json]] = []
    for region, groups in sorted(regions.items()):
        if not isinstance(groups, dict):
            continue
        for group_size, values in sorted(groups.items(), key=lambda item: int(item[0])):
            if isinstance(values, dict):
                rows.append((str(region), str(group_size), values))
    return rows


def _candidate_row_duplicate_rows(duplicates: Any) -> list[tuple[str, Json]]:
    if not isinstance(duplicates, dict):
        return []
    rows: list[tuple[str, Json]] = [("all", duplicates)]
    regions = duplicates.get("regions")
    if isinstance(regions, dict):
        for region, values in sorted(regions.items()):
            if isinstance(values, dict):
                rows.append((str(region), values))
    return rows


def write_sparse_mla_stats_markdown(path: Path, report: Json) -> None:
    work = report.get("candidate_work", {})
    timings = report.get("stage_timings_ms", {})
    efficiency = report.get("stage_efficiency", {})
    overlap = report.get("candidate_overlap", {})
    reuse = report.get("cross_query_reuse_potential", {})
    row_duplicates = report.get("candidate_row_duplicates", {})
    region_work = report.get("candidate_region_work", {})
    accumulate_work = report.get("accumulate_work", {})
    mqa_topk_work = report.get("mqa_topk_work", {})
    mqa_weight_sign = mqa_topk_work.get("weight_sign", {})
    if not isinstance(mqa_weight_sign, dict):
        mqa_weight_sign = {}
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
            "## Cross-Query Reuse Potential",
            "",
            f"- Sample rows: `{_format_number(reuse.get('sample_rows'))}`",
            "",
            (
                "| Region | Group size | Sampled valid visits | Sampled union visits | "
                "Sampled reusable visits | Sampled reuse ratio | Effective visit share |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    reuse_rows = _cross_query_reuse_rows(reuse)
    for region, group_size, values in reuse_rows:
        lines.append(
            "| "
            f"{region} | "
            f"{group_size} | "
            f"{_format_number(values.get('sampled_valid_candidate_visits'))} | "
            f"{_format_number(values.get('sampled_union_candidate_visits'))} | "
            f"{_format_number(values.get('sampled_reusable_candidate_visits'))} | "
            f"{_format_number(values.get('sampled_reuse_ratio'))} | "
            f"{_format_number(values.get('effective_visit_share'))} |"
        )
    if not reuse_rows:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    lines.extend(
        [
            "",
            "## Candidate Row Duplicates",
            "",
            (
                "| Region | Sample rows | Valid candidates | Unique candidates | "
                "Duplicate visits | Duplicate visit ratio | Rows with duplicates | "
                "Row duplicate ratio |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    duplicate_rows = _candidate_row_duplicate_rows(row_duplicates)
    for region, values in duplicate_rows:
        lines.append(
            "| "
            f"{region} | "
            f"{_format_number(values.get('sample_rows'))} | "
            f"{_format_number(values.get('valid_candidates'))} | "
            f"{_format_number(values.get('unique_candidates'))} | "
            f"{_format_number(values.get('duplicate_candidate_visits'))} | "
            f"{_format_number(values.get('duplicate_visit_ratio'))} | "
            f"{_format_number(values.get('rows_with_duplicates'))} | "
            f"{_format_number(values.get('row_duplicate_ratio'))} |"
        )
    if not duplicate_rows:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
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
            "## Sparse Accumulate Work",
            "",
            (
                "- Accumulate paths: "
                f"{_format_counts(accumulate_work.get('counts_by_path', {}))}"
            ),
            (
                "- Accumulate query tokens / effective visits: "
                f"`{_format_number(accumulate_work.get('query_tokens'))}` / "
                f"`{_format_number(accumulate_work.get('effective_candidate_visits'))}`"
            ),
            (
                "- Accumulate score elements: "
                f"`{_format_number(accumulate_work.get('candidate_score_elements'))}`"
            ),
            (
                "- Accumulate value-read bytes estimate: "
                f"`{_format_number(accumulate_work.get('candidate_value_read_bytes_estimate'))}`"
            ),
            (
                "- Accumulate q-read / output-write bytes estimate: "
                f"`{_format_number(accumulate_work.get('q_read_bytes_estimate'))}` / "
                f"`{_format_number(accumulate_work.get('output_write_bytes_estimate'))}`"
            ),
            (
                "- Accumulate state / score workspace bytes: "
                f"`{_format_number(accumulate_work.get('state_workspace_bytes'))}` / "
                f"`{_format_number(accumulate_work.get('score_workspace_bytes'))}`"
            ),
            (
                "- Accumulate launches / query chunks / top-k chunks: "
                f"`{_format_number(accumulate_work.get('accumulate_kernel_launches'))}` / "
                f"`{_format_number(accumulate_work.get('query_chunk_count'))}` / "
                f"`{_format_number(accumulate_work.get('topk_chunk_count'))}`"
            ),
            (
                "- Accumulate max query chunk / top-k chunk sizes: "
                f"`{_format_number(accumulate_work.get('query_chunk_size_max'))}` / "
                f"`{_format_number(accumulate_work.get('topk_chunk_sizes'))}`"
            ),
        ]
    )
    lines.extend(
        [
            "",
            "## MQA Top-K Work",
            "",
            (
                "- MQA top-k paths: "
                f"{_format_counts(mqa_topk_work.get('counts_by_path', {}))}"
            ),
            (
                "- MQA top-k query tokens / max KV tokens / max top-k: "
                f"`{_format_number(mqa_topk_work.get('query_tokens'))}` / "
                f"`{_format_number(mqa_topk_work.get('kv_tokens_max'))}` / "
                f"`{_format_number(mqa_topk_work.get('topk_tokens_max'))}`"
            ),
            (
                "- MQA top-k valid KV visits / logits elements: "
                f"`{_format_number(mqa_topk_work.get('valid_kv_visits'))}` / "
                f"`{_format_number(mqa_topk_work.get('logits_elements'))}`"
            ),
            (
                "- MQA top-k logits padding elements / valid ratio / padding ratio: "
                f"`{_format_number(mqa_topk_work.get('logits_padding_elements'))}` / "
                f"`{_format_number(mqa_topk_work.get('logits_valid_ratio'))}` / "
                f"`{_format_number(mqa_topk_work.get('logits_padding_ratio'))}`"
            ),
            (
                "- MQA top-k KV span count / mean / max: "
                f"`{_format_number(mqa_topk_work.get('kv_span_count'))}` / "
                f"`{_format_number(mqa_topk_work.get('kv_span_mean'))}` / "
                f"`{_format_number(mqa_topk_work.get('kv_span_max'))}`"
            ),
            (
                "- MQA top-k materialized logits bytes: "
                f"`{_format_number(mqa_topk_work.get('materialized_logits_bytes'))}`"
            ),
            (
                "- MQA top-k peak logits / estimated temp bytes: "
                f"`{_format_number(mqa_topk_work.get('peak_logits_bytes'))}` / "
                f"`{_format_number(mqa_topk_work.get('estimated_temp_bytes'))}`"
            ),
            (
                "- MQA logits launches / top-k merge count: "
                f"`{_format_number(mqa_topk_work.get('mqa_logits_launches'))}` / "
                f"`{_format_number(mqa_topk_work.get('topk_merge_count'))}`"
            ),
            (
                "- MQA top-k elapsed ms: "
                f"`{_format_number(mqa_topk_work.get('elapsed_ms'))}`"
            ),
            (
                "- MQA top-k weight signs positive / negative / zero: "
                f"`{_format_number(mqa_weight_sign.get('positive'))}` / "
                f"`{_format_number(mqa_weight_sign.get('negative'))}` / "
                f"`{_format_number(mqa_weight_sign.get('zero'))}`"
            ),
            (
                "- MQA top-k weight sign ratios positive / negative / zero: "
                f"`{_format_number(mqa_weight_sign.get('positive_ratio'))}` / "
                f"`{_format_number(mqa_weight_sign.get('negative_ratio'))}` / "
                f"`{_format_number(mqa_weight_sign.get('zero_ratio'))}`"
            ),
            (
                "- MQA top-k weight min / max / abs max: "
                f"`{_format_number(mqa_weight_sign.get('min'))}` / "
                f"`{_format_number(mqa_weight_sign.get('max'))}` / "
                f"`{_format_number(mqa_weight_sign.get('abs_max'))}`"
            ),
        ]
    )
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
