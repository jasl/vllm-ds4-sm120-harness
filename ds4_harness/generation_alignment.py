from __future__ import annotations

import json
from pathlib import Path
from typing import Any

Json = dict[str, Any]
KEY_FIELDS = ("language", "case", "thinking_mode", "round")


def load_generation_rows(path: Path) -> list[Json]:
    if path.suffix == ".jsonl":
        rows: list[Json] = []
        with path.open(encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError(f"{path}:{line_number} is not a JSON object")
                rows.append(item)
        return rows

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        if not all(isinstance(item, dict) for item in data):
            raise ValueError(f"{path} contains a non-object generation row")
        return data
    if isinstance(data, dict) and isinstance(data.get("results"), list):
        results = data["results"]
        if not all(isinstance(item, dict) for item in results):
            raise ValueError(f"{path} results contain a non-object generation row")
        return results
    raise ValueError(f"{path} is not a generation JSON list or JSONL file")


def compare_generation_rows(reference_rows: list[Json], actual_rows: list[Json]) -> Json:
    reference_index = _index_rows(reference_rows)
    actual_index = _index_rows(actual_rows)
    reference_keys = set(reference_index["rows"])
    actual_keys = set(actual_index["rows"])
    common_keys = sorted(reference_keys & actual_keys)

    ok_regressions = []
    ok_improvements = []
    finish_reason_mismatches = []
    usage_mismatches = []

    for key in common_keys:
        reference = reference_index["rows"][key]
        actual = actual_index["rows"][key]
        key_json = _key_json(key)
        if reference.get("ok") is True and actual.get("ok") is not True:
            ok_regressions.append(
                {
                    "key": key_json,
                    "reference_detail": reference.get("detail"),
                    "actual_detail": actual.get("detail"),
                }
            )
        if reference.get("ok") is not True and actual.get("ok") is True:
            ok_improvements.append(
                {
                    "key": key_json,
                    "reference_detail": reference.get("detail"),
                    "actual_detail": actual.get("detail"),
                }
            )
        if reference.get("finish_reason") != actual.get("finish_reason"):
            finish_reason_mismatches.append(
                {
                    "key": key_json,
                    "reference": reference.get("finish_reason"),
                    "actual": actual.get("finish_reason"),
                }
            )
        usage_mismatch = _usage_mismatch(key_json, reference, actual)
        if usage_mismatch is not None:
            usage_mismatches.append(usage_mismatch)

    missing_actual = [_key_json(key) for key in sorted(reference_keys - actual_keys)]
    unexpected_actual = [_key_json(key) for key in sorted(actual_keys - reference_keys)]
    actual_failures = [_failure_summary(row) for row in actual_rows if row.get("ok") is not True]
    reference_failures = [
        _failure_summary(row) for row in reference_rows if row.get("ok") is not True
    ]

    summary = {
        "reference_rows": len(reference_rows),
        "actual_rows": len(actual_rows),
        "common_rows": len(common_keys),
        "missing_actual_rows": len(missing_actual),
        "unexpected_actual_rows": len(unexpected_actual),
        "reference_duplicate_keys": len(reference_index["duplicates"]),
        "actual_duplicate_keys": len(actual_index["duplicates"]),
        "reference_failures": len(reference_failures),
        "actual_failures": len(actual_failures),
        "ok_regressions": len(ok_regressions),
        "ok_improvements": len(ok_improvements),
        "finish_reason_mismatches": len(finish_reason_mismatches),
        "usage_mismatches": len(usage_mismatches),
    }
    ok = (
        summary["missing_actual_rows"] == 0
        and summary["unexpected_actual_rows"] == 0
        and summary["reference_duplicate_keys"] == 0
        and summary["actual_duplicate_keys"] == 0
        and summary["actual_failures"] == 0
        and summary["ok_regressions"] == 0
    )

    return {
        "ok": ok,
        "summary": summary,
        "missing_actual": missing_actual,
        "unexpected_actual": unexpected_actual,
        "reference_duplicate_keys": reference_index["duplicates"],
        "actual_duplicate_keys": actual_index["duplicates"],
        "reference_failures": reference_failures,
        "actual_failures": actual_failures,
        "ok_regressions": ok_regressions,
        "ok_improvements": ok_improvements,
        "finish_reason_mismatches": finish_reason_mismatches,
        "usage_mismatches": usage_mismatches,
    }


def write_generation_alignment_markdown(path: Path, report: Json) -> None:
    summary = report["summary"]
    lines = [
        "# Generation Alignment",
        "",
        f"- Status: {'PASS' if report.get('ok') else 'FAIL'}",
        f"- Reference rows: `{summary['reference_rows']}`",
        f"- Actual rows: `{summary['actual_rows']}`",
        f"- Common rows: `{summary['common_rows']}`",
        f"- Missing actual rows: `{summary['missing_actual_rows']}`",
        f"- Unexpected actual rows: `{summary['unexpected_actual_rows']}`",
        f"- Actual failures: `{summary['actual_failures']}`",
        f"- OK regressions: `{summary['ok_regressions']}`",
        f"- Finish reason mismatches: `{summary['finish_reason_mismatches']}`",
        f"- Usage mismatches: `{summary['usage_mismatches']}`",
        "",
    ]
    _extend_table(lines, "OK Regressions", report["ok_regressions"])
    _extend_table(lines, "Actual Failures", report["actual_failures"])
    _extend_table(lines, "Missing Actual Rows", report["missing_actual"])
    _extend_table(lines, "Unexpected Actual Rows", report["unexpected_actual"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _index_rows(rows: list[Json]) -> dict[str, Any]:
    indexed: dict[tuple[Any, ...], Json] = {}
    counts: dict[tuple[Any, ...], int] = {}
    for row in rows:
        key = _row_key(row)
        counts[key] = counts.get(key, 0) + 1
        indexed.setdefault(key, row)
    duplicates = [
        {**_key_json(key), "count": count}
        for key, count in sorted(counts.items())
        if count > 1
    ]
    return {"rows": indexed, "duplicates": duplicates}


def _row_key(row: Json) -> tuple[Any, ...]:
    return tuple(row.get(field) for field in KEY_FIELDS)


def _key_json(key: tuple[Any, ...]) -> Json:
    return dict(zip(KEY_FIELDS, key, strict=True))


def _usage_mismatch(key: Json, reference: Json, actual: Json) -> Json | None:
    reference_usage = reference.get("usage")
    actual_usage = actual.get("usage")
    if not isinstance(reference_usage, dict) or not isinstance(actual_usage, dict):
        return None
    fields = ("prompt_tokens", "completion_tokens", "total_tokens")
    deltas = {}
    for field in fields:
        reference_value = reference_usage.get(field)
        actual_value = actual_usage.get(field)
        if isinstance(reference_value, int) and isinstance(actual_value, int):
            if reference_value != actual_value:
                deltas[f"{field}_delta"] = actual_value - reference_value
    if not deltas:
        return None
    return {"key": key, **deltas}


def _failure_summary(row: Json) -> Json:
    key = _key_json(_row_key(row))
    return {
        **key,
        "detail": row.get("detail"),
        "finish_reason": row.get("finish_reason"),
    }


def _extend_table(lines: list[str], title: str, rows: list[Json]) -> None:
    if not rows:
        return
    lines.extend([f"## {title}", ""])
    for row in rows[:20]:
        lines.append(f"- `{json.dumps(row, ensure_ascii=False)}`")
    if len(rows) > 20:
        lines.append(f"- ... {len(rows) - 20} more")
    lines.append("")
