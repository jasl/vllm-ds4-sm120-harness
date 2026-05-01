from ds4_harness import cli


def test_chat_smoke_writes_human_markdown_report(monkeypatch, tmp_path):
    def fake_post_json(base_url, path, payload, timeout):
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "7 * 8 = 56"},
                }
            ]
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)
    markdown_output = tmp_path / "smoke_quick.md"
    jsonl_output = tmp_path / "smoke_quick.jsonl"

    rc = cli.main(
        [
            "chat-smoke",
            "--case",
            "math_7_times_8",
            "--jsonl-output",
            str(jsonl_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    report = markdown_output.read_text(encoding="utf-8")
    assert "# Chat Smoke Report" in report
    assert "## math_7_times_8" in report
    assert "- Status: PASS" in report
    assert "- Tags: quick, basic, deterministic" in report
    assert "What is 7*8?" in report
    assert "7 * 8 = 56" in report


def test_chat_smoke_markdown_preserves_subjective_translation_output(
    monkeypatch, tmp_path
):
    answer = (
        "本地运行大语言模型可以提升隐私性并降低延迟，但也会把运维责任转移给团队。"
        "实际问题不在于本地推理是否令人惊叹，而在于组织能否维护硬件、监控质量，"
        "并承担迭代变慢带来的成本。"
    )

    def fake_post_json(base_url, path, payload, timeout):
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": answer},
                }
            ]
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)
    markdown_output = tmp_path / "smoke_quality.md"

    rc = cli.main(
        [
            "chat-smoke",
            "--case",
            "translation_quality_en_to_zh",
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    report = markdown_output.read_text(encoding="utf-8")
    assert "## translation_quality_en_to_zh" in report
    assert "- Tags: quality, translation, subjective, user-report" in report
    assert "Translate the following paragraph" in report
    assert answer in report
