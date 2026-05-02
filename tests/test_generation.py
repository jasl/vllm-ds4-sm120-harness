import json

from ds4_harness import cli
from ds4_harness.generation import load_generation_prompts


def _write_prompt(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_load_generation_prompts_reads_markdown_metadata(tmp_path):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "en" / "local_llm.md",
        """---
tags: writing, subjective
max_tokens: 1024
temperature: 0.7
top_p: 0.9
min_chars: 20
all_terms: Context, Recommendation
forbidden_terms: as an ai
---
Write a short article with Context and Recommendation sections.
""",
    )

    prompts = load_generation_prompts(prompt_root)

    assert len(prompts) == 1
    prompt = prompts[0]
    assert prompt.name == "local_llm"
    assert prompt.language == "en"
    assert prompt.workload == "writing"
    assert prompt.max_tokens == 1024
    assert prompt.temperature == 0.7
    assert prompt.top_p == 0.9
    assert prompt.expectation.all_terms == ("Context", "Recommendation")
    assert prompt.expectation.forbidden_terms == ("as an ai",)
    assert prompt.prompt.startswith("Write a short article")


def test_generation_matrix_writes_transcript_files_and_jsonl(monkeypatch, tmp_path):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "zh" / "translation_probe.md",
        """---
tags: translation, subjective
max_tokens: 512
all_terms: privacy, latency
min_chars: 20
---
Translate this sentence into English: 隐私和延迟都很重要。
""",
    )
    captured_payloads = []

    def fake_post_json(base_url, path, payload, timeout):
        captured_payloads.append(payload)
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "reasoning_content": "Reasoning line.  \nNext reasoning.  ",
                        "content": "Privacy and latency are both important.  ",
                    },
                }
            ],
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 7,
                "total_tokens": 19,
            },
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)
    jsonl_output = tmp_path / "generation.jsonl"
    transcript_dir = tmp_path / "generation"

    rc = cli.main(
        [
            "generation-matrix",
            "--prompt-root",
            str(prompt_root),
            "--language",
            "zh",
            "--thinking-mode",
            "non-thinking",
            "--variant",
            "mtp",
            "--repeat-count",
            "2",
            "--jsonl-output",
            str(jsonl_output),
            "--markdown-output-dir",
            str(transcript_dir),
        ]
    )

    assert rc == 0
    assert [payload["thinking"] for payload in captured_payloads] == [
        {"type": "disabled"},
        {"type": "disabled"},
    ]
    rows = [json.loads(line) for line in jsonl_output.read_text().splitlines()]
    assert [row["round"] for row in rows] == [1, 2]
    assert rows[0]["language"] == "zh"
    assert rows[0]["workload"] == "translation"
    assert rows[0]["model"] == "deepseek-ai/DeepSeek-V4-Flash"
    assert rows[0]["thinking_mode"] == "non-thinking"
    assert rows[0]["thinking_strength"] == "disabled"
    assert rows[0]["temperature"] == 1.0
    assert rows[0]["top_p"] == 1.0
    assert rows[0]["variant"] == "mtp"
    transcript = (
        transcript_dir / "zh" / "translation_probe.1.non-thinking.mtp.md"
    ).read_text(encoding="utf-8")
    assert "# Generation Transcript" in transcript
    assert "- OK: `True`" in transcript
    assert "- Detail: `matched expectation`" in transcript
    assert "- Model: `deepseek-ai/DeepSeek-V4-Flash`" in transcript
    assert "- Thinking mode: `non-thinking`" in transcript
    assert "- Thinking strength: `disabled`" in transcript
    assert "- Temperature: `1.0`" in transcript
    assert "- Top P: `1.0`" in transcript
    assert (
        '- Usage: `{"prompt_tokens": 12, "completion_tokens": 7, "total_tokens": 19}`'
        in transcript
    )
    assert "Translate this sentence into English" in transcript
    assert "Privacy and latency are both important." in transcript
    lines = transcript.splitlines()
    assert lines
    assert all(line == line.rstrip() for line in lines)


def test_generation_matrix_applies_think_max_body(monkeypatch, tmp_path):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "en" / "writing_probe.md",
        """---
tags: writing
---
Write one sentence about local inference.
""",
    )
    captured = {}

    def fake_post_json(base_url, path, payload, timeout):
        captured["payload"] = payload
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "Local inference is useful."},
                }
            ]
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)

    rc = cli.main(
        [
            "generation-matrix",
            "--prompt-root",
            str(prompt_root),
            "--thinking-mode",
            "think-max",
            "--max-tokens",
            "128",
        ]
    )

    assert rc == 0
    assert captured["payload"]["thinking"] == {"type": "enabled"}
    assert captured["payload"]["reasoning_effort"] == "max"
