import json

from ds4_harness import cli
from ds4_harness.long_context_latency import (
    run_long_context_latency_matrix,
    write_long_context_latency_markdown,
)


def test_long_context_latency_matrix_records_cold_and_warm_streaming_rows():
    calls = []

    def fake_stream(base_url, path, payload, timeout, **kwargs):
        metadata = kwargs["probe_metadata"]
        calls.append((metadata, payload))
        cached_tokens = 0 if metadata["cache_mode"] == "cold" else 39000
        return {
            "response": {
                "id": f"chatcmpl-{metadata['cache_mode']}-{metadata['request_index']}",
                "choices": [
                    {
                        "message": {
                            "content": (
                                "alpha-cobalt-17 beta-quartz-29 gamma-onyx-43"
                            )
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 42000,
                    "completion_tokens": 9,
                    "total_tokens": 42009,
                    "prompt_tokens_details": {"cached_tokens": cached_tokens},
                },
            },
            "assistant_text": "alpha-cobalt-17 beta-quartz-29 gamma-onyx-43",
            "ttft_seconds": 0.2 if metadata["cache_mode"] == "warm" else 1.0,
            "elapsed_seconds": 0.8 if metadata["cache_mode"] == "warm" else 2.0,
            "chunks": 2,
            "time_to_last_token_seconds": 0.7
            if metadata["cache_mode"] == "warm"
            else 1.9,
            "inter_chunk_seconds": [0.1, 0.2, 0.5]
            if metadata["cache_mode"] == "warm"
            else [0.4, 0.8, 1.2],
        }

    row = run_long_context_latency_matrix(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp",
        line_counts=[128],
        concurrencies=[1, 2],
        cache_modes=["cold", "warm"],
        stream_func=fake_stream,
    )

    assert row["ok"] is True
    assert {item["cache_mode"] for item in row["summary"]} == {"cold", "warm"}
    assert {item["concurrency"] for item in row["summary"]} == {1, 2}
    assert any(item["phase"] == "warmup" for item in row["requests"])
    warm_c2 = next(
        item
        for item in row["summary"]
        if item["cache_mode"] == "warm" and item["concurrency"] == 2
    )
    assert warm_c2["cached_prompt_tokens_mean"] == 39000
    assert warm_c2["decode_tokens_per_second_mean"] == 15.0
    assert warm_c2["decode_tps_vs_c1_ratio"] == 1.0
    assert warm_c2["p95_inter_chunk_seconds"] == 0.5
    assert warm_c2["p99_inter_chunk_seconds"] == 0.5
    assert warm_c2["max_inter_chunk_seconds"] == 0.5
    assert warm_c2["decode_tps_min_to_max_ratio"] == 1.0
    cold_payloads = [
        payload
        for metadata, payload in calls
        if metadata["cache_mode"] == "cold" and metadata["phase"] == "measure"
    ]
    assert len({json.dumps(payload["messages"]) for payload in cold_payloads}) == 3
    first_request = row["requests"][0]
    assert first_request["response_id"]
    assert first_request["assistant_text_sha256"]
    assert first_request["assistant_text_length"] == len(
        "alpha-cobalt-17 beta-quartz-29 gamma-onyx-43"
    )
    assert "beta-quartz-29" in first_request["assistant_text_excerpt"]
    assert first_request["time_to_last_token_seconds"] == 1.9
    assert first_request["inter_chunk_seconds"] == [0.4, 0.8, 1.2]
    assert first_request["p95_inter_chunk_seconds"] == 1.2
    assert first_request["p99_inter_chunk_seconds"] == 1.2


def test_long_context_latency_matrix_quantifies_decode_collapse_vs_c1():
    def fake_stream(base_url, path, payload, timeout, **kwargs):
        metadata = kwargs["probe_metadata"]
        concurrency = int(metadata["concurrency"])
        request_index = int(metadata["request_index"])
        elapsed = 6.0 if concurrency == 1 else (11.0 if request_index == 1 else 101.0)
        return {
            "response": {
                "choices": [
                    {
                        "message": {"content": "ok"},
                        "finish_reason": "length",
                    }
                ],
                "usage": {
                    "prompt_tokens": 120000,
                    "completion_tokens": 100,
                    "total_tokens": 120100,
                },
            },
            "assistant_text": "ok",
            "ttft_seconds": 1.0,
            "elapsed_seconds": elapsed,
            "chunks": 5,
        }

    row = run_long_context_latency_matrix(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp1",
        line_counts=[128],
        concurrencies=[1, 2],
        cache_modes=["cold"],
        stream_func=fake_stream,
    )

    c1 = next(item for item in row["summary"] if item["concurrency"] == 1)
    c2 = next(item for item in row["summary"] if item["concurrency"] == 2)

    assert c1["decode_tokens_per_second_mean"] == 20.0
    assert c2["decode_tokens_per_second_mean"] == 5.5
    assert c2["decode_tps_vs_c1_ratio"] == 0.275
    assert c2["decode_tps_min_to_max_ratio"] == 0.1


def test_long_context_latency_matrix_supports_prompt_files(tmp_path):
    prompt_file = tmp_path / "long_case.txt"
    prompt_file.write_text("A local long-context case.\n" * 128, encoding="utf-8")

    def fake_stream(base_url, path, payload, timeout, **kwargs):
        assert payload["messages"] == [
            {"role": "user", "content": prompt_file.read_text(encoding="utf-8")}
        ]
        return {
            "response": {
                "choices": [
                    {
                        "message": {"content": "original prompt answer"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 2000, "completion_tokens": 4},
            },
            "assistant_text": "original prompt answer",
            "ttft_seconds": 0.1,
            "elapsed_seconds": 0.3,
            "chunks": 1,
        }

    row = run_long_context_latency_matrix(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="nomtp",
        line_counts=[],
        prompt_files=[prompt_file],
        cache_modes=["warm"],
        stream_func=fake_stream,
    )

    assert row["ok"] is True
    assert row["prompts"][0]["source"] == "file"
    assert row["prompts"][0]["prompt_file"] == str(prompt_file)
    assert "assistant_text_sha256" in row["requests"][0]
    assert "assistant_text_excerpt" not in row["requests"][0]


def test_long_context_latency_markdown_includes_summary(tmp_path):
    row = {
        "ok": True,
        "case": "latency",
        "variant": "mtp",
        "model": "model",
        "thinking_mode": "non-thinking",
        "max_tokens": 64,
        "repeat_count": 1,
        "concurrencies": [1],
        "cache_modes": ["warm"],
        "summary": [
            {
                "prompt": "synthetic_128_lines",
                "cache_mode": "warm",
                "concurrency": 1,
                "request_count": 1,
                "failure_count": 0,
                "ttft_seconds_mean": 0.2,
                "ttft_seconds_max": 0.2,
                "elapsed_seconds_mean": 1.0,
                "prompt_tokens_mean": 1000,
                "cached_prompt_tokens_mean": 900,
                "completion_tokens_mean": 4,
                "decode_tokens_per_second_mean": 12.5,
                "decode_tps_vs_c1_ratio": 1.0,
                "decode_tps_min_to_max_ratio": 1.0,
                "p95_inter_chunk_seconds": 0.2,
                "p99_inter_chunk_seconds": 0.2,
                "max_inter_chunk_seconds": 0.2,
            }
        ],
        "prompts": [],
        "requests": [],
    }

    output = tmp_path / "latency.md"
    write_long_context_latency_markdown(output, row)

    report = output.read_text(encoding="utf-8")
    assert "# Long Context Latency Matrix" in report
    assert "TTFT mean s" in report
    assert "Decode tok/s mean" in report
    assert "synthetic_128_lines" in report


def test_long_context_latency_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    def fake_run_long_context_latency_matrix(**kwargs):
        return {
            "case": kwargs["case_name"],
            "variant": kwargs["variant"],
            "model": kwargs["model"],
            "ok": True,
            "summary": [{"failure_count": 0}],
            "requests": [],
            "prompts": [],
        }

    monkeypatch.setattr(
        cli, "run_long_context_latency_matrix", fake_run_long_context_latency_matrix
    )
    json_output = tmp_path / "latency.json"
    markdown_output = tmp_path / "latency.md"

    rc = cli.main(
        [
            "long-context-latency-matrix",
            "--model",
            "model",
            "--variant",
            "mtp",
            "--line-counts",
            "128,256",
            "--concurrency",
            "1,2",
            "--cache-modes",
            "cold,warm",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["variant"] == "mtp"
    assert "Long Context Latency Matrix" in markdown_output.read_text(
        encoding="utf-8"
    )
