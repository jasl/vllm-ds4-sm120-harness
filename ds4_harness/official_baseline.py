from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ds4_harness.reference_bundle import (
    _sanitize_json,
    _sanitize_string,
    scan_public_bundle,
)


Json = dict[str, Any]


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[Json]:
    rows: list[Json] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_sanitize_json(data), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _copy_text(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    lines = _sanitize_string(
        src.read_text(encoding="utf-8", errors="replace")
    ).splitlines()
    dst.write_text(
        "\n".join(line.rstrip() for line in lines).rstrip() + "\n",
        encoding="utf-8",
    )


def _copy_tree_contents(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        target = dst / path.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".md":
            _copy_text(path, target)
        else:
            shutil.copyfile(path, target)


def _exit_code(path: Path) -> int | str | None:
    if not path.exists():
        return None
    value = path.read_text(encoding="utf-8").strip()
    try:
        return int(value)
    except ValueError:
        return value or None


def _usage_total(row: Json) -> dict[str, int]:
    usage = row.get("usage")
    if not isinstance(usage, dict):
        response = row.get("response")
        usage = response.get("usage") if isinstance(response, dict) else {}
    return {
        "prompt_tokens": int(usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("completion_tokens") or 0),
        "total_tokens": int(usage.get("total_tokens") or 0),
    }


def _generation_summary(rows: list[Json]) -> Json:
    cases = {
        (row.get("language"), row.get("case"))
        for row in rows
        if row.get("language") and row.get("case")
    }
    summary: Json = {
        "rows": len(rows),
        "cases": len(cases),
        "ok": sum(1 for row in rows if row.get("ok") is True),
        "failures": sum(1 for row in rows if row.get("ok") is not True),
        "by_thinking_mode": {},
        "by_workload": {},
        "temperatures": {},
        "top_ps": {},
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
    by_thinking = summary["by_thinking_mode"]
    by_workload = summary["by_workload"]
    temperatures = summary["temperatures"]
    top_ps = summary["top_ps"]
    usage_totals = summary["usage"]
    for row in rows:
        thinking = str(row.get("thinking_mode") or "unknown")
        workload = str(row.get("workload") or "generation")
        temperature = str(row.get("temperature", "n/a"))
        top_p = str(row.get("top_p", "n/a"))
        by_thinking[thinking] = by_thinking.get(thinking, 0) + 1
        by_workload[workload] = by_workload.get(workload, 0) + 1
        temperatures[temperature] = temperatures.get(temperature, 0) + 1
        top_ps[top_p] = top_ps.get(top_p, 0) + 1
        usage = _usage_total(row)
        for key, value in usage.items():
            usage_totals[key] += value
    return summary


def _smoke_summary(rows: list[Json]) -> Json:
    return {
        "cases": len(rows),
        "ok": sum(1 for row in rows if row.get("ok") is True),
        "case_names": [
            row.get("case") for row in rows if isinstance(row.get("case"), str)
        ],
    }


def _toolcall_summary(data: Any) -> Json:
    if not isinstance(data, dict):
        return {}
    summary = data.get("summary")
    return summary if isinstance(summary, dict) else {}


def _inline_counts(values: Any) -> str:
    if not isinstance(values, dict) or not values:
        return "n/a"
    return ", ".join(f"`{key}`={value}" for key, value in sorted(values.items()))


def _write_report(
    path: Path,
    *,
    label: str,
    date: str | None,
    model: str,
    phase_exit_codes: Json,
    generation_rows: list[Json],
    smoke_rows: list[Json],
    toolcall_data: Any,
) -> None:
    generation_summary = _generation_summary(generation_rows)
    smoke_summary = _smoke_summary(smoke_rows)
    toolcall_summary = _toolcall_summary(toolcall_data)
    failures = []
    if isinstance(toolcall_data, dict):
        for row in toolcall_data.get("results", []):
            if isinstance(row, dict) and (
                row.get("ok") is False or row.get("status") not in (None, "pass")
            ):
                failures.append(row)

    lines = [
        "# DeepSeek Official API Baseline",
        "",
        f"- Label: `{label}`",
        f"- Date: `{date or 'n/a'}`",
        f"- Model: `{model}`",
        "",
        "## Phase Exit Codes",
        "",
        "| Phase | Exit |",
        "| --- | ---: |",
    ]
    for phase, code in phase_exit_codes.items():
        lines.append(f"| `{phase}` | `{code if code is not None else 'n/a'}` |")

    lines.extend(
        [
            "",
            "## Smoke Checks",
            "",
            f"- Passed: `{smoke_summary['ok']}/{smoke_summary['cases']}`",
            "- Cases: "
            f"{', '.join(f'`{name}`' for name in smoke_summary['case_names']) or 'n/a'}",
            "",
            "## Generation",
            "",
            f"- Passed: `{generation_summary['ok']}/{generation_summary['rows']}`",
            f"- Unique cases: `{generation_summary['cases']}`",
            f"- Failures: `{generation_summary['failures']}`",
            f"- Thinking modes: {_inline_counts(generation_summary['by_thinking_mode'])}",
            f"- Workloads: {_inline_counts(generation_summary['by_workload'])}",
            f"- Temperature: {_inline_counts(generation_summary['temperatures'])}",
            f"- Top P: {_inline_counts(generation_summary['top_ps'])}",
            f"- Prompt tokens: `{generation_summary['usage']['prompt_tokens']}`",
            f"- Completion tokens: `{generation_summary['usage']['completion_tokens']}`",
            f"- Total tokens: `{generation_summary['usage']['total_tokens']}`",
            "",
            "| Case | Workload | Language | Thinking | Round | Temp | Top P | OK | Detail |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in generation_rows:
        lines.append(
            "| "
            f"`{row.get('case')}` | "
            f"`{row.get('workload')}` | "
            f"`{row.get('language')}` | "
            f"`{row.get('thinking_mode')}` | "
            f"{row.get('round', 'n/a')} | "
            f"{row.get('temperature', 'n/a')} | "
            f"{row.get('top_p', 'n/a')} | "
            f"`{row.get('ok')}` | "
            f"{row.get('detail') or ''} |"
        )

    lines.extend(
        [
            "",
            "## ToolCall-15",
            "",
            "- Score: "
            f"`{toolcall_summary.get('points', 'n/a')}/"
            f"{toolcall_summary.get('max_points', 'n/a')}`",
            "- Total cases: "
            f"`{toolcall_summary.get('total_cases', toolcall_summary.get('cases', 'n/a'))}`",
            "- Scenario sets: "
            f"`{', '.join(toolcall_summary.get('scenario_sets', [])) or 'n/a'}`",
            "- Thinking modes: "
            f"`{', '.join(toolcall_summary.get('thinking_modes', [])) or 'n/a'}`",
            "- Rounds: "
            f"`{toolcall_summary.get('rounds', 'n/a')}`",
            "- Failures: "
            f"`{toolcall_summary.get('failures', len(failures) if failures else 0)}`",
            "",
        ]
    )
    if failures:
        lines.extend(["### Notable Failures", ""])
        for row in failures:
            lines.append(
                f"- `{row.get('id', row.get('case', 'unknown'))}` "
                f"{row.get('status', 'fail')}: "
                f"{row.get('summary', row.get('detail', ''))}"
            )
        lines.append("")

    lines.extend(
        [
            "## Contents",
            "",
            "- `generation/official_api.json`: structured generation rows.",
            "- `generation/<group>/*.md`: human-readable generation transcripts.",
            "- `smoke/official_api.json` and `smoke/official_api.md`: "
            "small runnable comparison checks.",
            "- `toolcall15/official_api.json`: ToolCall-15 trace and score.",
            "",
        ]
    )
    path.write_text(
        _sanitize_string("\n".join(lines).rstrip() + "\n"),
        encoding="utf-8",
    )


def build_official_api_baseline(
    *,
    artifact_dir: Path,
    output_dir: Path,
    label: str,
    date: str | None = None,
    fail_on_sensitive: bool = True,
) -> list[str]:
    generation_rows = _read_jsonl(artifact_dir / "official_generation.jsonl")
    smoke_rows = _read_jsonl(artifact_dir / "official_smoke.jsonl")
    toolcall_data = _load_json(artifact_dir / "official_toolcall15.json")
    model = "deepseek-v4-flash"
    for row in generation_rows:
        payload = row.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("model"), str):
            model = payload["model"]
            break

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "label": label,
        "date": date,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": {
            "artifact_run": artifact_dir.name,
            "raw_artifacts_are_not_required": True,
        },
        "model": model,
        "contents": {
            "report": "Readable official API reference report.",
            "generation": "Official API generation rows and Markdown transcripts.",
            "smoke": "Small official API comparison checks.",
            "toolcall15": "Official API ToolCall-15 trace and score.",
        },
    }
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "generation" / "official_api.json", generation_rows)
    _copy_tree_contents(artifact_dir / "generation", output_dir / "generation")
    _write_json(output_dir / "smoke" / "official_api.json", smoke_rows)
    _copy_text(
        artifact_dir / "official_smoke.md",
        output_dir / "smoke" / "official_api.md",
    )
    if isinstance(toolcall_data, dict):
        _write_json(output_dir / "toolcall15" / "official_api.json", toolcall_data)

    phase_exit_codes = {
        "smoke": _exit_code(artifact_dir / "official_smoke.exit_code"),
        "generation": _exit_code(artifact_dir / "official_generation.exit_code"),
        "toolcall15": _exit_code(artifact_dir / "official_toolcall15.exit_code"),
    }
    _write_report(
        output_dir / "report.md",
        label=label,
        date=date,
        model=model,
        phase_exit_codes=phase_exit_codes,
        generation_rows=generation_rows,
        smoke_rows=smoke_rows,
        toolcall_data=toolcall_data,
    )

    findings = scan_public_bundle(output_dir)
    if findings and fail_on_sensitive:
        raise ValueError(
            "official API baseline contains non-public data:\n"
            + "\n".join(findings)
        )
    return findings
