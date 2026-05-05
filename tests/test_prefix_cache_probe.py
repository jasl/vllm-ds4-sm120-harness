import json

from ds4_harness import cli
from ds4_harness.prefix_cache_probe import (
    build_prefix_cache_request,
    run_prefix_cache_probe,
    write_prefix_cache_probe_markdown,
)


def test_prefix_cache_requests_share_session_prefix_but_not_session_body():
    cold = build_prefix_cache_request(session="a", turn=1, line_count=128)
    warm = build_prefix_cache_request(session="a", turn=2, line_count=128)
    other = build_prefix_cache_request(session="b", turn=1, line_count=128)

    cold_messages = cold["payload"]["messages"]
    warm_messages = warm["payload"]["messages"]
    other_messages = other["payload"]["messages"]

    assert cold["prompt_sha256"] == warm["prompt_sha256"]
    assert cold["prompt_sha256"] != other["prompt_sha256"]
    assert cold_messages[:-1] == warm_messages[:-1]
    assert cold_messages[:-1] != other_messages[:-1]
    assert cold_messages[-1] != warm_messages[-1]
    assert "SESSION-A-CODE-17" in cold["required_terms"]
    assert "SESSION-B-CODE-17" in other["required_terms"]


def test_run_prefix_cache_probe_records_solo_and_interleaved_requests():
    calls = []

    def fake_stream(base_url, path, payload, timeout, **kwargs):
        metadata = kwargs["probe_metadata"]
        label = metadata["probe_label"]
        calls.append(label)
        ttft = {
            "cold_a": 1.0,
            "warm_a_solo": 0.2,
            "cold_b": 1.1,
            "warm_a_after_b_solo": 0.25,
            "warm_a_after_rebuild": 0.2,
            "warm_a_interleaved_after_rebuild": 0.28,
            "warm_b_interleaved": 0.3,
        }[label]
        cached_tokens = 0 if label.startswith("cold") else 39000
        session = metadata["session"]
        return {
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": f"SESSION-{session.upper()}-CODE-17"
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 42000,
                    "completion_tokens": 8,
                    "total_tokens": 42008,
                    "prompt_tokens_details": {"cached_tokens": cached_tokens},
                },
            },
            "assistant_text": f"SESSION-{session.upper()}-CODE-17",
            "ttft_seconds": ttft,
            "elapsed_seconds": ttft + 0.5,
            "chunks": 3,
        }

    row = run_prefix_cache_probe(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp",
        line_count=128,
        stream_func=fake_stream,
    )

    assert row["ok"] is True
    assert row["summary"]["request_count"] == 7
    assert row["summary"]["cached_tokens_total"] == 195000
    assert row["summary"]["warm_a_after_b_vs_solo_ttft_ratio"] == 1.25
    assert (
        row["summary"]["warm_a_interleaved_after_rebuild_vs_solo_ttft_ratio"]
        == 1.4
    )
    assert row["summary"]["suspect_prefix_reuse_regression"] is False
    assert {request["phase"] for request in row["requests"]} == {
        "cold_a",
        "warm_a_solo",
        "cold_b",
        "warm_a_after_b_solo",
        "warm_a_after_rebuild",
        "warm_a_interleaved_after_rebuild",
        "warm_b_interleaved",
    }
    assert calls[:5] == [
        "cold_a",
        "warm_a_solo",
        "cold_b",
        "warm_a_after_b_solo",
        "warm_a_after_rebuild",
    ]
    assert set(calls[5:]) == {
        "warm_a_interleaved_after_rebuild",
        "warm_b_interleaved",
    }


def test_prefix_cache_probe_markdown_includes_kv_cache_guidance(tmp_path):
    row = {
        "case": "prefix_cache_interleaved_long_conversation",
        "variant": "mtp",
        "ok": True,
        "summary": {
            "request_count": 2,
            "failure_count": 0,
            "cached_tokens_total": 39000,
            "warm_a_after_b_vs_solo_ttft_ratio": 1.2,
            "suspect_prefix_reuse_regression": False,
        },
        "requests": [
            {
                "phase": "warm_a_solo",
                "session": "a",
                "ok": True,
                "ttft_seconds": 0.2,
                "elapsed_seconds": 0.7,
                "prompt_tokens": 42000,
                "cached_prompt_tokens": 39000,
                "detail": "matched required session term",
            }
        ],
    }
    output = tmp_path / "prefix.md"

    write_prefix_cache_probe_markdown(output, row)

    report = output.read_text(encoding="utf-8")
    assert "# Prefix Cache Probe" in report
    assert "KV/runtime stats" in report
    assert "cached_prompt_tokens" in report


def test_prefix_cache_probe_flags_sequential_a_after_b_regression():
    def fake_stream(base_url, path, payload, timeout, **kwargs):
        metadata = kwargs["probe_metadata"]
        label = metadata["probe_label"]
        session = metadata["session"]
        ttft = 6.0 if label == "warm_a_after_b_solo" else 1.0
        if label in {"warm_a_solo", "warm_a_after_rebuild"}:
            ttft = 0.2
        return {
            "response": {
                "choices": [
                    {
                        "message": {
                            "content": f"SESSION-{session.upper()}-CODE-17"
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 42000, "completion_tokens": 8},
            },
            "assistant_text": f"SESSION-{session.upper()}-CODE-17",
            "ttft_seconds": ttft,
            "elapsed_seconds": ttft + 0.1,
            "chunks": 1,
        }

    row = run_prefix_cache_probe(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="nomtp",
        line_count=128,
        stream_func=fake_stream,
    )

    assert row["summary"]["warm_a_after_b_vs_solo_ttft_ratio"] == 30.0
    assert row["summary"]["suspect_prefix_reuse_regression"] is True
    assert row["ok"] is True


def test_prefix_cache_probe_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    def fake_run_prefix_cache_probe(**kwargs):
        return {
            "case": "prefix_cache_interleaved_long_conversation",
            "variant": kwargs["variant"],
            "model": kwargs["model"],
            "ok": True,
            "summary": {"request_count": 5, "failure_count": 0},
            "requests": [],
        }

    monkeypatch.setattr(cli, "run_prefix_cache_probe", fake_run_prefix_cache_probe)
    json_output = tmp_path / "prefix.json"
    markdown_output = tmp_path / "prefix.md"

    rc = cli.main(
        [
            "prefix-cache-probe",
            "--model",
            "model",
            "--variant",
            "mtp",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["variant"] == "mtp"
    assert "Prefix Cache Probe" in markdown_output.read_text(encoding="utf-8")
