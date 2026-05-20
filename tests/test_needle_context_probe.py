import json

from ds4_harness import cli
from ds4_harness.needle_context_probe import (
    build_needle_context_prompt,
    run_needle_position_matrix,
    write_needle_position_matrix_markdown,
)


def test_needle_prompt_places_needle_at_requested_positions():
    head = build_needle_context_prompt(line_count=128, position_percent=0)
    tail = build_needle_context_prompt(line_count=128, position_percent=100)

    assert head.needle_line == 1
    assert tail.needle_line == 128
    assert "Virtual Rocket Band" in head.text
    assert "Virtual Rocket Band" in tail.text
    assert head.sha256 != tail.sha256


def test_needle_position_matrix_records_tail_correctness_rows():
    calls = []

    def fake_stream(base_url, path, payload, timeout, **kwargs):
        metadata = kwargs["probe_metadata"]
        calls.append((metadata["line_count"], metadata["position_percent"]))
        return {
            "response": {
                "id": f"chatcmpl-{metadata['position_percent']}",
                "choices": [
                    {
                        "message": {
                            "content": (
                                "The first band to perform on the Moon was "
                                "the Virtual Rocket Band."
                            )
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 4096 + metadata["position_percent"],
                    "completion_tokens": 12,
                    "total_tokens": 4108 + metadata["position_percent"],
                },
            },
            "assistant_text": (
                "The first band to perform on the Moon was the Virtual Rocket Band."
            ),
            "ttft_seconds": 0.5,
            "elapsed_seconds": 1.0,
            "chunks": 2,
        }

    row = run_needle_position_matrix(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp",
        line_counts=[128],
        positions=[92, 100],
        max_tokens=32,
        stream_func=fake_stream,
    )

    assert row["ok"] is True
    assert row["summary"]["request_count"] == 2
    assert row["summary"]["failure_count"] == 0
    assert row["summary"]["positions"] == [92, 100]
    assert {request["position_percent"] for request in row["requests"]} == {92, 100}
    assert calls == [(128, 92), (128, 100)]


def test_needle_position_matrix_marks_missing_answer_as_failure():
    def fake_stream(base_url, path, payload, timeout, **kwargs):
        return {
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": "The context does not contain this information."
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 4096, "completion_tokens": 8},
            },
            "assistant_text": "The context does not contain this information.",
            "ttft_seconds": 0.5,
            "elapsed_seconds": 1.0,
            "chunks": 1,
        }

    row = run_needle_position_matrix(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp",
        line_counts=[128],
        positions=[100],
        stream_func=fake_stream,
    )

    assert row["ok"] is False
    assert row["summary"]["failure_count"] == 1
    assert "missing answer" in row["requests"][0]["detail"]


def test_needle_position_matrix_markdown_includes_tail_table(tmp_path):
    row = {
        "case": "needle_position_matrix",
        "variant": "mtp",
        "model": "model",
        "ok": True,
        "summary": {
            "request_count": 1,
            "failure_count": 0,
            "positions": [100],
            "line_counts": [128],
            "max_ttft_seconds": 0.5,
            "max_elapsed_seconds": 1.0,
        },
        "requests": [
            {
                "line_count": 128,
                "position_percent": 100,
                "needle_line": 128,
                "ok": True,
                "ttft_seconds": 0.5,
                "elapsed_seconds": 1.0,
                "prompt_tokens": 4096,
                "detail": "matched needle answer",
            }
        ],
    }
    output = tmp_path / "needle.md"

    write_needle_position_matrix_markdown(output, row)

    report = output.read_text(encoding="utf-8")
    assert "# Needle Position Matrix" in report
    assert "| 128 | 100 | 128 | yes |" in report


def test_needle_position_matrix_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    def fake_run_needle_position_matrix(**kwargs):
        return {
            "case": kwargs["case_name"],
            "variant": kwargs["variant"],
            "model": kwargs["model"],
            "ok": True,
            "summary": {"request_count": 1, "failure_count": 0},
            "requests": [],
        }

    monkeypatch.setattr(
        cli, "run_needle_position_matrix", fake_run_needle_position_matrix
    )
    json_output = tmp_path / "needle.json"
    markdown_output = tmp_path / "needle.md"

    rc = cli.main(
        [
            "needle-position-matrix",
            "--model",
            "model",
            "--variant",
            "mtp",
            "--line-counts",
            "128",
            "--positions",
            "92,100",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["variant"] == "mtp"
    assert "Needle Position Matrix" in markdown_output.read_text(encoding="utf-8")
