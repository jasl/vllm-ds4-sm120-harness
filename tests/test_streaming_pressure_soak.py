import json

from ds4_harness import cli
from ds4_harness.streaming_pressure_soak import (
    build_streaming_pressure_request,
    parse_streaming_pressure_case_spec,
    run_streaming_pressure_matrix,
    run_streaming_pressure_soak,
    write_streaming_pressure_matrix_markdown,
    write_streaming_pressure_soak_markdown,
)


def test_streaming_pressure_requests_grow_a_long_conversation():
    first = build_streaming_pressure_request(
        worker_index=0,
        round_index=1,
        line_count=128,
    )
    second = build_streaming_pressure_request(
        worker_index=0,
        round_index=2,
        line_count=128,
    )
    other_worker = build_streaming_pressure_request(
        worker_index=1,
        round_index=1,
        line_count=128,
    )

    assert first["required_terms"] == ["STREAM-W00-R01-CHECK"]
    assert second["required_terms"] == ["STREAM-W00-R02-CHECK"]
    assert other_worker["required_terms"] == ["STREAM-W01-R01-CHECK"]
    assert first["prompt_sha256"] != second["prompt_sha256"]
    assert first["prompt_sha256"] != other_worker["prompt_sha256"]
    assert len(second["payload"]["messages"]) > len(first["payload"]["messages"])
    assert "STREAM-W00-R01-CHECK" in json.dumps(
        second["payload"]["messages"],
        ensure_ascii=False,
    )


def test_run_streaming_pressure_soak_records_concurrent_rounds():
    calls = []

    def fake_stream(base_url, path, payload, timeout, **kwargs):
        metadata = kwargs["probe_metadata"]
        calls.append((metadata["round_index"], metadata["worker_index"]))
        required = metadata["required_terms"][0]
        round_index = metadata["round_index"]
        return {
            "response": {
                "choices": [
                    {
                        "message": {"content": required},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 1000 + round_index,
                    "completion_tokens": 8,
                    "total_tokens": 1008 + round_index,
                    "prompt_tokens_details": {
                        "cached_tokens": 0 if round_index == 1 else 700
                    },
                },
            },
            "assistant_text": required,
            "ttft_seconds": 0.1 * round_index,
            "elapsed_seconds": 0.5 + round_index,
            "chunks": round_index + 1,
        }

    row = run_streaming_pressure_soak(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp",
        concurrency=3,
        round_count=2,
        line_count=128,
        stream_func=fake_stream,
    )

    assert row["ok"] is True
    assert row["summary"]["request_count"] == 6
    assert row["summary"]["failure_count"] == 0
    assert row["summary"]["cached_tokens_total"] == 2100
    assert row["summary"]["max_ttft_seconds"] == 0.2
    assert row["summary"]["total_chunks"] == 15
    assert set(calls) == {
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    }


def test_streaming_pressure_soak_can_hard_fail_slow_ttft():
    def fake_stream(base_url, path, payload, timeout, **kwargs):
        metadata = kwargs["probe_metadata"]
        required = metadata["required_terms"][0]
        return {
            "response": {
                "choices": [
                    {
                        "message": {"content": required},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 1000, "completion_tokens": 8},
            },
            "assistant_text": required,
            "ttft_seconds": 4.0,
            "elapsed_seconds": 4.5,
            "chunks": 1,
        }

    row = run_streaming_pressure_soak(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="nomtp",
        concurrency=1,
        round_count=1,
        line_count=128,
        max_ttft_seconds=1.0,
        fail_on_slow=True,
        stream_func=fake_stream,
    )

    assert row["summary"]["suspect_slow_ttft"] is True
    assert row["ok"] is False


def test_streaming_pressure_soak_markdown_includes_runtime_guidance(tmp_path):
    row = {
        "case": "streaming_pressure_short_soak",
        "variant": "mtp",
        "ok": True,
        "summary": {
            "request_count": 2,
            "failure_count": 0,
            "max_ttft_seconds": 0.2,
            "max_elapsed_seconds": 1.5,
            "cached_tokens_total": 700,
            "suspect_slow_ttft": False,
            "suspect_slow_elapsed": False,
        },
        "requests": [
            {
                "phase": "round_01_worker_00",
                "round": 1,
                "worker": 0,
                "ok": True,
                "ttft_seconds": 0.2,
                "elapsed_seconds": 1.5,
                "prompt_tokens": 1000,
                "cached_prompt_tokens": 700,
                "chunks": 2,
                "detail": "matched required streaming term",
            }
        ],
    }
    output = tmp_path / "streaming.md"

    write_streaming_pressure_soak_markdown(output, row)

    report = output.read_text(encoding="utf-8")
    assert "# Streaming Pressure Soak" in report
    assert "KV/runtime stats" in report
    assert "cached_prompt_tokens" in report


def test_streaming_pressure_soak_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    def fake_run_streaming_pressure_soak(**kwargs):
        return {
            "case": "streaming_pressure_short_soak",
            "variant": kwargs["variant"],
            "model": kwargs["model"],
            "ok": True,
            "summary": {"request_count": 2, "failure_count": 0},
            "requests": [],
        }

    monkeypatch.setattr(cli, "run_streaming_pressure_soak", fake_run_streaming_pressure_soak)
    json_output = tmp_path / "streaming.json"
    markdown_output = tmp_path / "streaming.md"

    rc = cli.main(
        [
            "streaming-pressure-soak",
            "--model",
            "model",
            "--variant",
            "mtp",
            "--concurrency",
            "2",
            "--round-count",
            "1",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["variant"] == "mtp"
    assert "Streaming Pressure Soak" in markdown_output.read_text(encoding="utf-8")


def test_streaming_pressure_matrix_runs_multiple_case_specs():
    calls = []

    def fake_stream(base_url, path, payload, timeout, **kwargs):
        metadata = kwargs["probe_metadata"]
        calls.append((metadata["matrix_case"], metadata["round_index"], metadata["worker_index"]))
        required = metadata["required_terms"][0]
        return {
            "response": {
                "choices": [
                    {
                        "message": {"content": required},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 1000 + metadata["round_index"],
                    "completion_tokens": 8,
                    "total_tokens": 1008 + metadata["round_index"],
                    "prompt_tokens_details": {"cached_tokens": 512},
                },
            },
            "assistant_text": required,
            "ttft_seconds": 0.5,
            "elapsed_seconds": 2.0,
            "chunks": 3,
        }

    row = run_streaming_pressure_matrix(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp",
        case_name="continuous_pressure",
        case_specs=[
            "short_c2:2:2:128:16",
            "long_c1:1:1:256:8:2.0:10.0",
        ],
        stream_func=fake_stream,
    )

    assert row["ok"] is True
    assert row["summary"]["case_count"] == 2
    assert row["summary"]["request_count"] == 5
    assert row["summary"]["failure_count"] == 0
    assert row["summary"]["slow_case_count"] == 0
    assert [case["matrix_case"]["name"] for case in row["cases"]] == [
        "short_c2",
        "long_c1",
    ]
    assert set(calls) == {
        ("short_c2", 1, 0),
        ("short_c2", 1, 1),
        ("short_c2", 2, 0),
        ("short_c2", 2, 1),
        ("long_c1", 1, 0),
    }


def test_streaming_pressure_matrix_rejects_invalid_case_spec():
    try:
        parse_streaming_pressure_case_spec("bad:2:0:128:16")
    except ValueError as exc:
        assert "round_count must be >= 1" in str(exc)
    else:
        raise AssertionError("expected invalid matrix case spec to fail")


def test_streaming_pressure_matrix_markdown_includes_case_table(tmp_path):
    row = {
        "case": "continuous_pressure",
        "variant": "mtp",
        "ok": True,
        "summary": {
            "case_count": 1,
            "request_count": 2,
            "failure_count": 0,
            "slow_case_count": 0,
            "max_ttft_seconds": 0.5,
            "max_elapsed_seconds": 2.0,
        },
        "cases": [
            {
                "case": "continuous_pressure.short_c2",
                "ok": True,
                "matrix_case": {
                    "name": "short_c2",
                    "concurrency": 2,
                    "round_count": 1,
                    "line_count": 128,
                    "max_tokens": 16,
                },
                "summary": {
                    "request_count": 2,
                    "failure_count": 0,
                    "suspect_slow_ttft": False,
                    "suspect_slow_elapsed": False,
                    "max_ttft_seconds": 0.5,
                    "max_elapsed_seconds": 2.0,
                },
            }
        ],
    }
    output = tmp_path / "matrix.md"

    write_streaming_pressure_matrix_markdown(output, row)

    report = output.read_text(encoding="utf-8")
    assert "# Streaming Pressure Matrix" in report
    assert "| short_c2 | 2 | 1 | 128 | 16 | yes |" in report


def test_streaming_pressure_matrix_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    def fake_run_streaming_pressure_matrix(**kwargs):
        return {
            "case": kwargs["case_name"],
            "variant": kwargs["variant"],
            "model": kwargs["model"],
            "ok": True,
            "summary": {"case_count": 1, "request_count": 2, "failure_count": 0},
            "cases": [],
        }

    monkeypatch.setattr(
        cli, "run_streaming_pressure_matrix", fake_run_streaming_pressure_matrix
    )
    json_output = tmp_path / "matrix.json"
    markdown_output = tmp_path / "matrix.md"

    rc = cli.main(
        [
            "streaming-pressure-matrix",
            "--model",
            "model",
            "--variant",
            "mtp",
            "--case-name",
            "continuous_pressure",
            "--case-spec",
            "short_c2:2:1:128:16",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["case"] == "continuous_pressure"
    assert "Streaming Pressure Matrix" in markdown_output.read_text(encoding="utf-8")
