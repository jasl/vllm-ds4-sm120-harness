from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ds4_harness.checks import assistant_text


SUBJECTIVE_CASE_ORDER = (
    "writing_follow_instructions",
    "writing_quality_user_report_zh",
    "translation_quality_en_to_zh",
    "translation_quality_zh_to_en",
    "aquarium_html_zh",
    "clock_html_zh",
    "aquarium_html",
    "clock_html",
)

SOURCE_LABELS = {
    "b200_nomtp": "B200 no-MTP",
    "b200_mtp": "B200 MTP",
    "official_api": "DeepSeek official API",
}

AGENTIC_SOURCE_LABELS = {
    "b200_nomtp": "B200 no-MTP",
    "b200_mtp": "B200 MTP",
    "official_api": "DeepSeek official API",
}


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        data = json.loads(text)
        return [row for row in data if isinstance(row, dict)]
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        row = json.loads(stripped)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _load_smoke_rows(baseline_dir: Path) -> dict[str, list[dict[str, Any]]]:
    smoke_dir = baseline_dir / "smoke"
    return {
        "b200_nomtp": _load_rows(smoke_dir / "nomtp_quality.json")
        + _load_rows(smoke_dir / "nomtp_coding.json"),
        "b200_mtp": _load_rows(smoke_dir / "mtp_quality.json")
        + _load_rows(smoke_dir / "mtp_coding.json"),
    }


def _rows_by_case(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed = {}
    for row in rows:
        name = row.get("case")
        if isinstance(name, str):
            indexed[name] = row
    return indexed


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            else:
                parts.append(json.dumps(item, ensure_ascii=False, indent=2))
        return "\n\n".join(parts)
    if content is None:
        return ""
    return json.dumps(content, ensure_ascii=False, indent=2)


def _prompt_from_row(row: dict[str, Any] | None) -> str:
    if not row:
        return ""
    messages = row.get("payload", {}).get("messages", [])
    if not isinstance(messages, list):
        return ""
    rendered = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role", "unknown")
        rendered.append(f"{role}: {_message_text(message.get('content'))}")
    return "\n\n".join(rendered)


def _finish_reason(response: dict[str, Any]) -> str | None:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    choice = choices[0]
    return choice.get("finish_reason") if isinstance(choice, dict) else None


def _usage(response: dict[str, Any]) -> dict[str, Any] | None:
    usage = response.get("usage")
    return usage if isinstance(usage, dict) else None


def _summarize_output(row: dict[str, Any]) -> dict[str, Any]:
    response = row.get("response", {})
    if not isinstance(response, dict):
        response = {}
    payload = row.get("payload", {})
    if not isinstance(payload, dict):
        payload = {}
    text = assistant_text(response)
    error = response.get("error")
    return {
        "ok": row.get("ok"),
        "detail": row.get("detail"),
        "model": response.get("model") or payload.get("model"),
        "finish_reason": _finish_reason(response),
        "usage": _usage(response),
        "error": error if isinstance(error, str) else None,
        "content": text,
    }


def _fenced(text: str, language: str = "text") -> str:
    fence = "```"
    while fence in text:
        fence += "`"
    clean_text = "\n".join(line.rstrip() for line in text.rstrip().splitlines())
    return f"{fence}{language}\n{clean_text}\n{fence}"


def _write_markdown(path: Path, data: dict[str, Any]) -> None:
    lines = [
        "# Subjective Quality Comparison",
        "",
        f"- Label: `{data['label']}`",
        f"- Cases: {len(data['cases'])}",
        "",
        "## Sources",
        "",
    ]
    for key, label in SOURCE_LABELS.items():
        lines.append(f"- `{key}`: {label}")
    lines.append("")

    lines.extend(
        [
            "## Summary",
            "",
            "| Case | B200 no-MTP | B200 MTP | Official API |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for case in data["cases"]:
        cells = []
        for source_key in SOURCE_LABELS:
            output = case["outputs"].get(source_key)
            cells.append("n/a" if output is None else str(output.get("ok")))
        lines.append(f"| `{case['case']}` | {cells[0]} | {cells[1]} | {cells[2]} |")
    lines.append("")

    for case in data["cases"]:
        lines.extend(
            [
                f"## {case['case']}",
                "",
                f"- Tags: {', '.join(case.get('tags') or [])}",
                "",
                "### Prompt",
                "",
                _fenced(case.get("prompt") or ""),
                "",
            ]
        )
        for source_key, source_label in SOURCE_LABELS.items():
            output = case["outputs"].get(source_key)
            if output is None:
                lines.extend([f"### {source_label}", "", "_No sample captured._", ""])
                continue
            lines.extend(
                [
                    f"### {source_label}",
                    "",
                    f"- OK: `{output.get('ok')}`",
                    f"- Detail: `{output.get('detail')}`",
                    f"- Model: `{output.get('model')}`",
                    f"- Finish reason: `{output.get('finish_reason')}`",
                ]
            )
            usage = output.get("usage")
            if usage:
                lines.append(f"- Usage: `{json.dumps(usage, ensure_ascii=False)}`")
            if output.get("error"):
                lines.extend(["", "#### Error", "", _fenced(output["error"]), ""])
            content = output.get("content") or ""
            if content:
                lines.extend(["", "#### Assistant", "", _fenced(content), ""])
            elif not output.get("error"):
                lines.extend(["", "_No assistant content captured._", ""])
            else:
                lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_readme(path: Path) -> None:
    path.write_text(
        """# Subjective Quality Samples

This directory contains side-by-side subjective samples for B200 no-MTP, B200
MTP, and the DeepSeek official API. It is intended for human review of
English and Chinese-user translation, writing, coding, and agentic behavior.

- `comparison.md`: human-readable prompts and outputs.
- `comparison.json`: structured version of the same data.
- `agentic/`: ToolCall-15 traces and score summary when official API agentic
  samples were captured.

These samples are quality references, not deterministic correctness or
performance measurements.
""",
        encoding="utf-8",
    )


def _copy_agentic_samples(
    *,
    baseline_dir: Path,
    official_toolcall_paths: list[Path],
    output_dir: Path,
) -> None:
    sources: dict[str, dict[str, Any]] = {}
    for source_key, path in {
        "b200_nomtp": baseline_dir / "toolcall15" / "nomtp.json",
        "b200_mtp": baseline_dir / "toolcall15" / "mtp.json",
    }.items():
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            sources[source_key] = data

    for index, path in enumerate(official_toolcall_paths, start=1):
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            key = (
                "official_api"
                if len(official_toolcall_paths) == 1
                else f"official_api_{index}"
            )
            sources[key] = data

    if not sources:
        return

    agentic_dir = output_dir / "agentic"
    for source_key, data in sources.items():
        _write_json(agentic_dir / f"{source_key}.json", data)

    lines = [
        "# Agentic ToolCall-15 Samples",
        "",
        "| Source | Score | Total cases | Failures | Scenario sets | Rounds |",
        "| --- | ---: | ---: | ---: | --- | ---: |",
    ]
    for source_key, data in sources.items():
        summary = data.get("summary")
        summary = summary if isinstance(summary, dict) else {}
        scenario_sets = summary.get("scenario_sets", [])
        if isinstance(scenario_sets, list):
            scenario_sets_text = ", ".join(str(item) for item in scenario_sets)
        else:
            scenario_sets_text = str(scenario_sets)
        lines.append(
            f"| {AGENTIC_SOURCE_LABELS.get(source_key, source_key)} | "
            f"{summary.get('points', 'n/a')}/{summary.get('max_points', 'n/a')} | "
            f"{summary.get('total_cases', summary.get('cases', 'n/a'))} | "
            f"{summary.get('failures', 'n/a')} | {scenario_sets_text} | "
            f"{summary.get('rounds', 'n/a')} |"
        )

    (agentic_dir / "summary.md").write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )


def build_subjective_comparison(
    *,
    baseline_dir: Path,
    official_paths: list[Path],
    official_toolcall_paths: list[Path] | None = None,
    output_dir: Path,
    label: str,
) -> dict[str, Any]:
    source_rows = _load_smoke_rows(baseline_dir)
    source_rows["official_api"] = []
    for path in official_paths:
        source_rows["official_api"].extend(_load_rows(path))

    indexed = {source: _rows_by_case(rows) for source, rows in source_rows.items()}
    all_cases = set(SUBJECTIVE_CASE_ORDER)
    for rows in indexed.values():
        all_cases.update(rows.keys())
    ordered_cases = [
        *[case for case in SUBJECTIVE_CASE_ORDER if case in all_cases],
        *sorted(all_cases.difference(SUBJECTIVE_CASE_ORDER)),
    ]

    cases = []
    for case_name in ordered_cases:
        rows_for_case = {
            source: rows.get(case_name) for source, rows in indexed.items()
        }
        present_rows = [row for row in rows_for_case.values() if row is not None]
        if not present_rows:
            continue
        first = present_rows[0]
        tags = first.get("tags") if isinstance(first.get("tags"), list) else []
        prompt = ""
        for source in ("b200_nomtp", "b200_mtp", "official_api"):
            prompt = _prompt_from_row(rows_for_case.get(source))
            if prompt:
                break
        cases.append(
            {
                "case": case_name,
                "tags": tags,
                "prompt": prompt,
                "outputs": {
                    source: _summarize_output(row)
                    for source, row in rows_for_case.items()
                    if row is not None
                },
            }
        )

    data = {
        "schema_version": 1,
        "label": label,
        "sources": SOURCE_LABELS,
        "cases": cases,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "comparison.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_markdown(output_dir / "comparison.md", data)
    _write_readme(output_dir / "README.md")
    _copy_agentic_samples(
        baseline_dir=baseline_dir,
        official_toolcall_paths=official_toolcall_paths or [],
        output_dir=output_dir,
    )
    return data
