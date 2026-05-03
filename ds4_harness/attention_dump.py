from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


Json = dict[str, Any]

EXPECTED_KIND = "deepseek_v4_sparse_mla_compressed_decode_dump"


def _load_dump_metadata(path: Path) -> Json | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get("kind") != EXPECTED_KIND:
        return None
    return data


def _float_value(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dump_row(path: Path, data: Json) -> Json:
    tensor_file = str(data.get("tensor_file", ""))
    return {
        "file": path.name,
        "tensor_file": Path(tensor_file).name if tensor_file else "",
        "prefix": str(data.get("prefix", "")),
        "layer_id": data.get("layer_id"),
        "branch": str(data.get("branch", "")),
        "step": data.get("step"),
        "tensor_model_parallel_rank": data.get("tensor_model_parallel_rank"),
        "compress_ratio": data.get("compress_ratio"),
        "compressed_topk": data.get("compressed_topk"),
        "max_swa_len": data.get("max_swa_len"),
        "max_abs_diff": _float_value(data.get("max_abs_diff")),
        "mean_abs_diff": _float_value(data.get("mean_abs_diff")),
    }


def build_attention_dump_report(dump_dir: Path, *, worst_limit: int = 20) -> Json:
    rows: list[Json] = []
    for path in sorted(dump_dir.glob("*.json")):
        data = _load_dump_metadata(path)
        if data is not None:
            rows.append(_dump_row(path, data))

    branch_counts = Counter(str(row["branch"]) for row in rows if row.get("branch"))
    ratio_counts = Counter(
        str(row["compress_ratio"])
        for row in rows
        if row.get("compress_ratio") is not None
    )
    rank_counts = Counter(
        str(row["tensor_model_parallel_rank"])
        for row in rows
        if row.get("tensor_model_parallel_rank") is not None
    )
    layer_counts = Counter(
        str(row["layer_id"]) for row in rows if row.get("layer_id") is not None
    )
    max_values = [
        row["max_abs_diff"] for row in rows if row.get("max_abs_diff") is not None
    ]
    mean_values = [
        row["mean_abs_diff"] for row in rows if row.get("mean_abs_diff") is not None
    ]
    worst_rows = sorted(
        rows,
        key=lambda row: (
            row["max_abs_diff"] is not None,
            row["max_abs_diff"] or 0.0,
        ),
        reverse=True,
    )[:worst_limit]

    return {
        "dump_dir": dump_dir.name,
        "dump_count": len(rows),
        "counts_by_branch": dict(sorted(branch_counts.items())),
        "counts_by_compress_ratio": dict(sorted(ratio_counts.items())),
        "counts_by_rank": dict(sorted(rank_counts.items())),
        "counts_by_layer": dict(sorted(layer_counts.items())),
        "max_abs_diff": max(max_values) if max_values else None,
        "mean_abs_diff_mean": (
            sum(mean_values) / len(mean_values) if mean_values else None
        ),
        "worst_dumps": worst_rows,
    }


def write_attention_dump_json(path: Path, report: Json) -> None:
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


def write_attention_dump_markdown(path: Path, report: Json) -> None:
    lines = [
        "# Sparse MLA Dump Report",
        "",
        f"- Dump count: `{report.get('dump_count', 0)}`",
        f"- Branches: {_format_counts(report.get('counts_by_branch', {}))}",
        (
            "- Compress ratios: "
            f"{_format_counts(report.get('counts_by_compress_ratio', {}))}"
        ),
        f"- Ranks: {_format_counts(report.get('counts_by_rank', {}))}",
        f"- Layers: {_format_counts(report.get('counts_by_layer', {}))}",
        f"- Max abs diff: `{_format_number(report.get('max_abs_diff'))}`",
        (
            "- Mean of mean abs diff: "
            f"`{_format_number(report.get('mean_abs_diff_mean'))}`"
        ),
        "",
        "Raw tensor files are referenced by name only; keep `.pt` payloads in the "
        "run artifact directory and copy them selectively.",
        "",
        "## Worst Dumps",
        "",
        (
            "| Metadata | Tensor | Layer | Branch | Step | Rank | Compress | "
            "Max abs diff | Mean abs diff |"
        ),
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report.get("worst_dumps", []):
        lines.append(
            "| "
            f"`{row.get('file', '')}` | "
            f"`{row.get('tensor_file', '')}` | "
            f"`{row.get('layer_id', '')}` | "
            f"`{row.get('branch', '')}` | "
            f"`{row.get('step', '')}` | "
            f"`{row.get('tensor_model_parallel_rank', '')}` | "
            f"`{row.get('compress_ratio', '')}` | "
            f"`{_format_number(row.get('max_abs_diff'))}` | "
            f"`{_format_number(row.get('mean_abs_diff'))}` |"
        )
    if not report.get("worst_dumps"):
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
