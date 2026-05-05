import json

from ds4_harness import cli
from ds4_harness.streaming_pressure_soak import (
    build_streaming_pressure_request,
    run_streaming_pressure_soak,
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
