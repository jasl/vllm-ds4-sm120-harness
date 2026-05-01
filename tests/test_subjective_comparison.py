import json

from ds4_harness.subjective_comparison import build_subjective_comparison


def _response(text, *, model="model", finish_reason="stop"):
    return {
        "model": model,
        "choices": [
            {
                "finish_reason": finish_reason,
                "message": {"role": "assistant", "content": text},
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    }


def _row(case, text, *, model="model"):
    return {
        "case": case,
        "tags": ["quality", "writing", "subjective"],
        "ok": True,
        "detail": "matched expectation",
        "payload": {
            "model": model,
            "messages": [{"role": "user", "content": f"Prompt for {case}"}],
            "max_tokens": 1024,
            "temperature": 1.0,
        },
        "response": _response(text, model=model),
    }


def test_subjective_comparison_writes_b200_and_official_side_by_side(tmp_path):
    baseline = tmp_path / "baseline"
    generation = baseline / "generation"
    generation.mkdir(parents=True)
    (generation / "nomtp.json").write_text(
        json.dumps([_row("translation_quality_en_to_zh", "B200 no-MTP answer")]),
        encoding="utf-8",
    )
    (generation / "mtp.json").write_text(
        json.dumps([_row("translation_quality_en_to_zh", "B200 MTP answer")]),
        encoding="utf-8",
    )
    official = tmp_path / "official.jsonl"
    official.write_text(
        json.dumps(
            _row(
                "translation_quality_en_to_zh",
                "Official API answer",
                model="deepseek-v4-flash",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    toolcall = baseline / "toolcall15"
    toolcall.mkdir(parents=True)
    (toolcall / "nomtp.json").write_text(
        json.dumps({"summary": {"points": 10, "max_points": 20, "total_cases": 10}}),
        encoding="utf-8",
    )
    (toolcall / "mtp.json").write_text(
        json.dumps({"summary": {"points": 12, "max_points": 20, "total_cases": 10}}),
        encoding="utf-8",
    )
    official_toolcall = tmp_path / "official_toolcall.json"
    official_toolcall.write_text(
        json.dumps({"summary": {"points": 14, "max_points": 20, "total_cases": 10}}),
        encoding="utf-8",
    )

    out_dir = tmp_path / "subjective"

    build_subjective_comparison(
        baseline_dir=baseline,
        official_paths=[official],
        official_toolcall_paths=[official_toolcall],
        output_dir=out_dir,
        label="unit",
    )

    report = (out_dir / "comparison.md").read_text(encoding="utf-8")
    data = json.loads((out_dir / "comparison.json").read_text(encoding="utf-8"))
    readme = (out_dir / "README.md").read_text(encoding="utf-8")

    assert "# Subjective Quality Comparison" in report
    assert "| `translation_quality_en_to_zh` | True | True | True |" in report
    assert "## translation_quality_en_to_zh" in report
    assert "B200 no-MTP answer" in report
    assert "B200 MTP answer" in report
    assert "Official API answer" in report
    assert data["label"] == "unit"
    assert data["cases"][0]["outputs"]["official_api"]["model"] == "deepseek-v4-flash"
    assert "comparison.md" in readme
    assert (out_dir / "agentic" / "b200_nomtp.json").exists()
    assert (out_dir / "agentic" / "b200_mtp.json").exists()
    assert (out_dir / "agentic" / "official_api.json").exists()
    assert "DeepSeek official API" in (
        out_dir / "agentic" / "summary.md"
    ).read_text(encoding="utf-8")
