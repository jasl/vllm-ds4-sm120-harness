from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


Json = dict[str, Any]


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _round_float(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 6)


def classify_cuda_gpu_trace_name(name: str) -> str:
    if name.startswith("[CUDA memcpy"):
        return "cuda_memcpy"
    if "_accumulate_indexed_attention_chunk_multihead_kernel" in name:
        return "sparse_mla_chunk"
    if "_accumulate_indexed_attention_partial_states_multihead_kernel" in name:
        return "sparse_mla_partial"
    if "_fp8_mqa_logits" in name or "_fp8_paged_mqa_logits" in name:
        return "fp8_mqa_logits"
    if "_combine_topk_swa_indices" in name:
        return "combine_topk_swa"
    if "_deepseek_v4_sm12x_fp8_einsum" in name:
        return "fp8_mhc_einsum"
    if "cutlass" in name.lower() or "gemm" in name.lower():
        return "gemm"
    return "other_cuda"


def _read_cuda_gpu_trace_rows(path: Path) -> list[Json]:
    rows: list[Json] = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            start_ns = _float_or_none(row.get("Start (ns)"))
            duration_ns = _float_or_none(row.get("Duration (ns)"))
            name = str(row.get("Name") or "").strip()
            if start_ns is None or duration_ns is None or not name:
                continue
            rows.append(
                {
                    "start_ns": start_ns,
                    "duration_ns": duration_ns,
                    "end_ns": start_ns + duration_ns,
                    "name": name,
                    "class": classify_cuda_gpu_trace_name(name),
                    "device": row.get("Device"),
                    "stream": row.get("Strm"),
                    "grid": "x".join(
                        str(row.get(key) or "")
                        for key in ("GrdX", "GrdY", "GrdZ")
                    ).strip("x"),
                    "block": "x".join(
                        str(row.get(key) or "")
                        for key in ("BlkX", "BlkY", "BlkZ")
                    ).strip("x"),
                }
            )
    rows.sort(key=lambda item: (float(item["start_ns"]), float(item["duration_ns"])))
    return rows


def _summarize_duration_by_key(rows: list[Json], key: str) -> list[Json]:
    duration_by_key: dict[str, float] = defaultdict(float)
    instances_by_key: Counter[str] = Counter()
    for row in rows:
        value = str(row.get(key) or "")
        if not value:
            continue
        duration_by_key[value] += float(row["duration_ns"])
        instances_by_key[value] += 1
    return [
        {
            key: value,
            "duration_seconds": _round_float(duration_ns / 1e9),
            "instances": instances_by_key[value],
        }
        for value, duration_ns in sorted(
            duration_by_key.items(), key=lambda item: (-item[1], item[0])
        )
    ]


def _top_interval_rows(rows: list[Json], start_ns: float, end_ns: float) -> list[Json]:
    interval_rows = [
        row
        for row in rows
        if float(row["start_ns"]) >= start_ns and float(row["start_ns"]) < end_ns
    ]
    by_class = _summarize_duration_by_key(interval_rows, "class")[:6]
    by_name = _summarize_duration_by_key(interval_rows, "name")[:5]
    return [
        {
            "start_seconds": _round_float((start_ns - rows[0]["start_ns"]) / 1e9)
            if rows
            else None,
            "end_seconds": _round_float((end_ns - rows[0]["start_ns"]) / 1e9)
            if rows
            else None,
            "gap_seconds": _round_float((end_ns - start_ns) / 1e9),
            "cuda_row_count": len(interval_rows),
            "duration_by_class": by_class,
            "top_kernels": by_name,
        }
    ]


def _summarize_decode_kernel_gaps(rows: list[Json]) -> Json:
    decode_rows = [row for row in rows if row.get("class") == "fp8_mqa_logits"]
    if len(decode_rows) < 2:
        return {
            "decode_kernel_count": len(decode_rows),
            "max_start_gap_seconds": None,
            "top_gaps": [],
        }
    gaps: list[tuple[float, Json, Json]] = []
    for previous, current in zip(decode_rows, decode_rows[1:]):
        gap_ns = float(current["start_ns"]) - float(previous["start_ns"])
        gaps.append((gap_ns, previous, current))
    gaps.sort(key=lambda item: item[0], reverse=True)
    top_gaps: list[Json] = []
    for gap_ns, previous, current in gaps[:5]:
        top_gaps.extend(
            _top_interval_rows(
                rows,
                float(previous["start_ns"]),
                float(current["start_ns"]),
            )
        )
        top_gaps[-1]["previous_decode_kernel"] = previous["name"]
        top_gaps[-1]["next_decode_kernel"] = current["name"]
    return {
        "decode_kernel_count": len(decode_rows),
        "max_start_gap_seconds": _round_float(gaps[0][0] / 1e9),
        "top_gaps": top_gaps,
    }


def _summarize_idle_gaps(rows: list[Json]) -> Json:
    if len(rows) < 2:
        return {"max_idle_gap_seconds": None, "top_idle_gaps": []}
    gaps: list[Json] = []
    previous_end = float(rows[0]["end_ns"])
    first_start = float(rows[0]["start_ns"])
    for row in rows[1:]:
        start = float(row["start_ns"])
        gap_ns = start - previous_end
        if gap_ns > 0:
            gaps.append(
                {
                    "start_seconds": _round_float((previous_end - first_start) / 1e9),
                    "end_seconds": _round_float((start - first_start) / 1e9),
                    "gap_seconds": _round_float(gap_ns / 1e9),
                }
            )
        previous_end = max(previous_end, float(row["end_ns"]))
    gaps.sort(key=lambda item: float(item["gap_seconds"] or 0), reverse=True)
    return {
        "max_idle_gap_seconds": gaps[0]["gap_seconds"] if gaps else None,
        "top_idle_gaps": gaps[:5],
    }


def _mixed_arrival_summary(path: Path | None) -> Json:
    if path is None or not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"parse_error": str(exc)}
    requests = payload.get("requests", payload.get("rows", []))
    slowest_decode = None
    if isinstance(requests, list):
        decode_rows = [
            row
            for row in requests
            if isinstance(row, dict)
            and _float_or_none(row.get("decode_tokens_per_second")) is not None
        ]
        if decode_rows:
            slowest_decode = min(
                decode_rows,
                key=lambda row: float(row.get("decode_tokens_per_second") or 0),
            )
    result = {
        "case": payload.get("case"),
        "variant": payload.get("variant"),
        "request_count": len(requests) if isinstance(requests, list) else None,
        "summary": payload.get("summary", []),
    }
    if isinstance(slowest_decode, dict):
        result["slowest_decode_request"] = {
            "arrival_case": slowest_decode.get("arrival_case"),
            "request_role": slowest_decode.get("request_role"),
            "decode_tokens_per_second": slowest_decode.get(
                "decode_tokens_per_second"
            ),
            "p99_inter_chunk_seconds": slowest_decode.get("p99_inter_chunk_seconds"),
            "max_inter_chunk_seconds": slowest_decode.get("max_inter_chunk_seconds"),
        }
    return result


def _slow_request_gap_interpretation(mixed: Json, decode_gaps: Json) -> Json:
    slow = mixed.get("slowest_decode_request") if isinstance(mixed, dict) else None
    if not isinstance(slow, dict):
        return {}
    slow_tail = _float_or_none(slow.get("max_inter_chunk_seconds"))
    if slow_tail is None:
        slow_tail = _float_or_none(slow.get("p99_inter_chunk_seconds"))
    global_decode_gap = _float_or_none(decode_gaps.get("max_start_gap_seconds"))
    if slow_tail is None or global_decode_gap is None or global_decode_gap <= 0:
        return {
            "slow_request_tail_seconds": _round_float(slow_tail),
            "max_global_decode_kernel_gap_seconds": _round_float(global_decode_gap),
            "classification": "insufficient_timing_evidence",
        }
    ratio = slow_tail / global_decode_gap
    if slow_tail >= 1.0 and ratio >= 4.0:
        classification = "per_request_starvation_while_global_decode_continues"
    elif slow_tail >= 1.0:
        classification = "global_decode_gap_matches_slow_request_tail"
    else:
        classification = "no_large_slow_request_tail"
    return {
        "slow_request_tail_seconds": _round_float(slow_tail),
        "max_global_decode_kernel_gap_seconds": _round_float(global_decode_gap),
        "slow_request_tail_to_global_decode_gap_ratio": _round_float(ratio),
        "classification": classification,
    }


def build_nsys_cuda_trace_report(
    trace_csv: Path,
    *,
    mixed_arrival_json: Path | None = None,
) -> Json:
    rows = _read_cuda_gpu_trace_rows(trace_csv)
    if not rows:
        mixed = _mixed_arrival_summary(mixed_arrival_json)
        return {
            "trace_csv": trace_csv.name,
            "row_count": 0,
            "missing_or_empty": True,
            "mixed_arrival": mixed,
            "slow_request_gap_interpretation": {},
        }
    first_start = float(rows[0]["start_ns"])
    last_end = max(float(row["end_ns"]) for row in rows)
    total_duration_ns = sum(float(row["duration_ns"]) for row in rows)
    mixed = _mixed_arrival_summary(mixed_arrival_json)
    decode_gaps = _summarize_decode_kernel_gaps(rows)
    return {
        "trace_csv": trace_csv.name,
        "row_count": len(rows),
        "missing_or_empty": False,
        "trace_span_seconds": _round_float((last_end - first_start) / 1e9),
        "total_cuda_duration_seconds": _round_float(total_duration_ns / 1e9),
        "duration_by_class": _summarize_duration_by_key(rows, "class"),
        "top_kernels": _summarize_duration_by_key(rows, "name")[:20],
        "decode_kernel_gaps": decode_gaps,
        "idle_gaps": _summarize_idle_gaps(rows),
        "mixed_arrival": mixed,
        "slow_request_gap_interpretation": _slow_request_gap_interpretation(
            mixed, decode_gaps
        ),
    }


def write_nsys_cuda_trace_report_json(path: Path, report: Json) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


def _format_value(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _dominant_class(interval: Json) -> str:
    classes = interval.get("duration_by_class")
    if not isinstance(classes, list) or not classes:
        return "n/a"
    item = classes[0]
    return str(item.get("class") or "n/a")


def write_nsys_cuda_trace_report_markdown(path: Path, report: Json) -> None:
    gaps = report.get("decode_kernel_gaps", {})
    idle = report.get("idle_gaps", {})
    mixed = report.get("mixed_arrival", {})
    slow = mixed.get("slowest_decode_request") if isinstance(mixed, dict) else {}
    interpretation = report.get("slow_request_gap_interpretation", {})
    lines = [
        "# Nsys CUDA Trace Timeline Summary",
        "",
        f"- Trace CSV: `{report.get('trace_csv', '')}`",
        f"- CUDA rows: `{report.get('row_count', 0)}`",
        f"- Trace span seconds: `{_format_value(report.get('trace_span_seconds'))}`",
        (
            "- Total CUDA duration seconds: "
            f"`{_format_value(report.get('total_cuda_duration_seconds'))}`"
        ),
        (
            "- FP8 MQA logits kernel count: "
            f"`{_format_value(gaps.get('decode_kernel_count'))}`"
        ),
        (
            "- Max FP8 MQA logits start gap seconds: "
            f"`{_format_value(gaps.get('max_start_gap_seconds'))}`"
        ),
        (
            "- Max CUDA idle gap seconds: "
            f"`{_format_value(idle.get('max_idle_gap_seconds'))}`"
        ),
        (
            "- Slow-request gap interpretation: "
            f"`{_format_value(interpretation.get('classification'))}`"
        ),
    ]
    if isinstance(slow, dict) and slow:
        lines.extend(
            [
                (
                    "- Slowest decode request: "
                    f"`{slow.get('arrival_case')}`/{slow.get('request_role')} "
                    f"decode `{_format_value(slow.get('decode_tokens_per_second'))}` "
                    "tok/s, p99 ITL "
                    f"`{_format_value(slow.get('p99_inter_chunk_seconds'))}` s"
                ),
            ]
        )
    lines.extend(
        [
            "",
            "## Duration By Class",
            "",
            "| Class | Duration s | Instances |",
            "| --- | ---: | ---: |",
        ]
    )
    for item in report.get("duration_by_class", [])[:12]:
        lines.append(
            "| `{class_name}` | `{duration}` | `{instances}` |".format(
                class_name=item.get("class", ""),
                duration=_format_value(item.get("duration_seconds")),
                instances=_format_value(item.get("instances")),
            )
        )
    if not report.get("duration_by_class"):
        lines.append("| n/a | n/a | n/a |")

    lines.extend(
        [
            "",
            "## Largest FP8 MQA Logits Gaps",
            "",
            "| Start s | Gap s | Dominant class | CUDA rows | Top kernel |",
            "| ---: | ---: | --- | ---: | --- |",
        ]
    )
    for interval in gaps.get("top_gaps", [])[:5]:
        kernels = interval.get("top_kernels") or []
        top_kernel = kernels[0].get("name", "") if kernels else ""
        if len(top_kernel) > 88:
            top_kernel = top_kernel[:85] + "..."
        lines.append(
            "| `{start}` | `{gap}` | `{klass}` | `{rows}` | `{kernel}` |".format(
                start=_format_value(interval.get("start_seconds")),
                gap=_format_value(interval.get("gap_seconds")),
                klass=_dominant_class(interval),
                rows=_format_value(interval.get("cuda_row_count")),
                kernel=top_kernel,
            )
        )
    if not gaps.get("top_gaps"):
        lines.append("| n/a | n/a | n/a | n/a | n/a |")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
