import json

from ds4_harness import cli
from ds4_harness.generation_alignment import compare_generation_rows


def _row(
    *,
    case: str = "case-a",
    language: str = "en",
    thinking_mode: str = "non-thinking",
    round_index: int = 1,
    ok: bool = True,
    detail: str = "matched expectation",
    finish_reason: str = "stop",
    prompt_tokens: int = 10,
    completion_tokens: int = 20,
) -> dict:
    return {
        "case": case,
        "language": language,
        "thinking_mode": thinking_mode,
        "round": round_index,
        "ok": ok,
        "detail": detail,
        "finish_reason": finish_reason,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def test_compare_generation_rows_reports_status_regressions_and_missing_rows():
    reference = [
        _row(case="ok-row"),
        _row(case="regressed-row"),
        _row(case="missing-row"),
    ]
    actual = [
        _row(case="ok-row"),
        _row(case="regressed-row", ok=False, detail="response too short"),
        _row(case="extra-row"),
    ]

    report = compare_generation_rows(reference, actual)

    assert report["ok"] is False
    assert report["summary"]["reference_rows"] == 3
    assert report["summary"]["actual_rows"] == 3
    assert report["summary"]["common_rows"] == 2
    assert report["summary"]["ok_regressions"] == 1
    assert report["summary"]["missing_actual_rows"] == 1
    assert report["summary"]["unexpected_actual_rows"] == 1
    assert report["ok_regressions"][0]["key"]["case"] == "regressed-row"
    assert report["missing_actual"][0]["case"] == "missing-row"
    assert report["unexpected_actual"][0]["case"] == "extra-row"


def test_compare_generation_rows_records_finish_reason_and_usage_drift():
    report = compare_generation_rows(
        [
            _row(
                case="drift-row",
                finish_reason="stop",
                prompt_tokens=10,
                completion_tokens=20,
            )
        ],
        [
            _row(
                case="drift-row",
                finish_reason="length",
                prompt_tokens=10,
                completion_tokens=25,
            )
        ],
    )

    assert report["ok"] is True
    assert report["summary"]["finish_reason_mismatches"] == 1
    assert report["summary"]["usage_mismatches"] == 1
    assert report["finish_reason_mismatches"][0]["reference"] == "stop"
    assert report["finish_reason_mismatches"][0]["actual"] == "length"
    assert report["usage_mismatches"][0]["completion_tokens_delta"] == 5


def test_generation_compare_cli_writes_report_outputs(tmp_path):
    reference = tmp_path / "reference.json"
    actual = tmp_path / "actual.jsonl"
    json_output = tmp_path / "report.json"
    markdown_output = tmp_path / "report.md"
    reference.write_text(json.dumps([_row()]), encoding="utf-8")
    actual.write_text(json.dumps(_row()) + "\n", encoding="utf-8")

    rc = cli.main(
        [
            "generation-compare",
            "--reference",
            str(reference),
            "--actual",
            str(actual),
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    assert json.loads(json_output.read_text(encoding="utf-8"))["ok"] is True
    assert "- Status: PASS" in markdown_output.read_text(encoding="utf-8")


def test_generation_compare_cli_is_registered(tmp_path):
    args = cli.build_parser().parse_args(
        [
            "generation-compare",
            "--reference",
            str(tmp_path / "reference.json"),
            "--actual",
            str(tmp_path / "actual.jsonl"),
        ]
    )

    assert args.command == "generation-compare"
