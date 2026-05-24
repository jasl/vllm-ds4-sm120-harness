import json

import pytest

from ds4_harness import cli
from ds4_harness.frontier_context_sweep import (
    parse_frontiers,
    run_frontier_context_sweep,
    write_frontier_context_sweep_markdown,
)


def test_parse_frontiers_requires_positive_integers():
    assert parse_frontiers("2048,4096,8192") == [2048, 4096, 8192]

    with pytest.raises(ValueError, match="frontiers"):
        parse_frontiers("2048,0")

    with pytest.raises(ValueError, match="at least one"):
        parse_frontiers("")


def test_frontier_context_sweep_records_prompt_tokens_and_latency(tmp_path):
    prompt_file = tmp_path / "story.txt"
    prompt_file.write_text("\n".join(f"line {idx}" for idx in range(128)), encoding="utf-8")
    seen_lengths = []

    def fake_stream(base_url, path, payload, timeout, **kwargs):
        metadata = kwargs["probe_metadata"]
        prompt_text = payload["messages"][0]["content"]
        seen_lengths.append(len(prompt_text))
        target = int(metadata["target_frontier_tokens"])
        prompt_tokens = target + 11
        return {
            "response": {
                "id": f"chatcmpl-frontier-{target}",
                "choices": [
                    {
                        "message": {"content": "frontier response"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": 10,
                    "total_tokens": prompt_tokens + 10,
                },
            },
            "assistant_text": "frontier response",
            "ttft_seconds": 2.0 if target == 4096 else 4.0,
            "elapsed_seconds": 4.0 if target == 4096 else 9.0,
            "chunks": 3,
            "time_to_last_token_seconds": 3.8,
            "inter_chunk_seconds": [0.1, 0.3, 0.9],
        }

    row = run_frontier_context_sweep(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp",
        case_name="frontier",
        prompt_files=[prompt_file],
        frontiers=[4096, 8192],
        repeat_count=1,
        max_tokens=32,
        stream_func=fake_stream,
    )

    assert row["ok"] is True
    assert row["frontiers"] == [4096, 8192]
    assert len(row["requests"]) == 2
    assert seen_lengths == sorted(seen_lengths)

    first = next(item for item in row["summary"] if item["target_frontier_tokens"] == 4096)
    assert first["prompt_tokens_mean"] == 4107
    assert first["input_tokens_per_second_mean"] == 2053.5
    assert first["decode_tokens_per_second_mean"] == 5.0
    assert first["p99_inter_chunk_seconds"] == 0.9
    assert first["failure_count"] == 0


def test_frontier_context_sweep_markdown_includes_frontier_metrics(tmp_path):
    row = {
        "ok": True,
        "case": "frontier",
        "variant": "mtp",
        "model": "model",
        "thinking_mode": "non-thinking",
        "max_tokens": 32,
        "repeat_count": 1,
        "frontiers": [4096],
        "summary": [
            {
                "prompt": "story",
                "target_frontier_tokens": 4096,
                "request_count": 1,
                "failure_count": 0,
                "prompt_tokens_mean": 4107,
                "ttft_seconds_mean": 2.0,
                "ttft_seconds_max": 2.0,
                "input_tokens_per_second_mean": 2053.5,
                "decode_tokens_per_second_mean": 5.0,
                "p95_inter_chunk_seconds": 0.9,
                "p99_inter_chunk_seconds": 0.9,
                "max_inter_chunk_seconds": 0.9,
            }
        ],
        "requests": [],
        "prompts": [],
    }

    output = tmp_path / "frontier.md"
    write_frontier_context_sweep_markdown(output, row)

    text = output.read_text(encoding="utf-8")
    assert "# Frontier Context Sweep" in text
    assert "Target frontier tokens" in text
    assert "Input tok/s mean" in text


def test_frontier_context_sweep_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    def fake_run_frontier_context_sweep(**kwargs):
        assert kwargs["frontiers"] == [4096, 8192]
        assert kwargs["prompt_files"] == [tmp_path / "story.txt"]
        return {
            "case": kwargs["case_name"],
            "variant": kwargs["variant"],
            "model": kwargs["model"],
            "ok": True,
            "summary": [{"failure_count": 0}],
            "requests": [],
            "prompts": [],
        }

    (tmp_path / "story.txt").write_text("story", encoding="utf-8")
    monkeypatch.setattr(cli, "run_frontier_context_sweep", fake_run_frontier_context_sweep)
    json_output = tmp_path / "frontier.json"
    markdown_output = tmp_path / "frontier.md"

    rc = cli.main(
        [
            "frontier-context-sweep",
            "--model",
            "model",
            "--variant",
            "mtp",
            "--prompt-file",
            str(tmp_path / "story.txt"),
            "--frontiers",
            "4096,8192",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["variant"] == "mtp"
    assert "Frontier Context Sweep" in markdown_output.read_text(encoding="utf-8")
