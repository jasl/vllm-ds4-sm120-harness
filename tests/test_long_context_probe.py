import json

from ds4_harness import cli
from ds4_harness.long_context_probe import (
    DEFAULT_REQUIRED_TERMS,
    build_long_context_prompt,
    run_long_context_probe,
)


def test_long_context_prompt_is_deterministic_and_contains_sentinels():
    prompt = build_long_context_prompt(line_count=128)
    again = build_long_context_prompt(line_count=128)

    assert prompt.sha256 == again.sha256
    assert prompt.line_count == 128
    for term in DEFAULT_REQUIRED_TERMS:
        assert term in prompt.text
    assert "Final task:" in prompt.text


def test_run_long_context_probe_records_shape_without_full_prompt():
    captured = {}

    def fake_post(base_url, path, payload, timeout, **kwargs):
        captured.update(
            {
                "base_url": base_url,
                "path": path,
                "payload": payload,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return {
            "choices": [
                {
                    "message": {
                        "content": "alpha-cobalt-17 beta-quartz-29 gamma-onyx-43"
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 42000,
                "completion_tokens": 12,
                "total_tokens": 42012,
            },
        }

    row = run_long_context_probe(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="nomtp",
        line_count=128,
        post_func=fake_post,
    )

    assert row["ok"] is True
    assert row["usage"]["prompt_tokens"] == 42000
    assert row["prompt"]["line_count"] == 128
    assert "messages" not in row["request_shape"]
    assert "messages" in captured["payload"]
    assert captured["path"] == "/v1/chat/completions"


def test_long_context_probe_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    def fake_run_long_context_probe(**kwargs):
        return {
            "case": "kv_indexer_long_context",
            "variant": kwargs["variant"],
            "model": kwargs["model"],
            "ok": True,
            "detail": "matched long-context sentinel terms",
            "required_terms": list(DEFAULT_REQUIRED_TERMS),
            "missing_terms": [],
            "thinking_mode": "non-thinking",
            "thinking_strength": "disabled",
            "temperature": 0.0,
            "top_p": 1.0,
            "usage": {"prompt_tokens": 10, "completion_tokens": 2},
            "prompt": {
                "line_count": 128,
                "sha256": "abc",
                "excerpt": {"head": "head", "tail": "tail"},
            },
            "assistant_text": "alpha-cobalt-17 beta-quartz-29 gamma-onyx-43",
            "finish_reason": "stop",
        }

    monkeypatch.setattr(cli, "run_long_context_probe", fake_run_long_context_probe)
    json_output = tmp_path / "probe.json"
    markdown_output = tmp_path / "probe.md"

    rc = cli.main(
        [
            "long-context-probe",
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
    assert "Prompt SHA256" in markdown_output.read_text(encoding="utf-8")
