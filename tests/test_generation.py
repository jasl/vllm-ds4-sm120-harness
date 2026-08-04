import json

import pytest

from ds4_harness import cli
from ds4_harness.generation import (
    DEFAULT_THINKING_MODES,
    NESTED_THINKING_MODE_EXTRA_BODY,
    THINKING_MODE_EXTRA_BODY,
    load_generation_prompts,
    thinking_extra_body,
)


def _write_prompt(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_thinking_extra_body_pins_both_wire_shapes():
    """Lock the exact request shape of every thinking mode.

    The canonical shapes were already asserted indirectly, through the CLI, by
    test_generation_matrix_* and test_toolcall15_cli_runs_requested_thinking_matrix --
    but those went red at 79be5f1 and stayed red, so in practice nothing guarded them.
    The nested modes had no coverage at all: `non-thinking-nested` is byte-identical to
    what scripts/run_dspark_acceptance_probe.sh sends, and this is still the only place
    that shape is asserted -- see the note in generation.py on why it is not "legacy".
    """
    assert thinking_extra_body("non-thinking") == {"thinking": {"type": "disabled"}}
    assert thinking_extra_body("think-high") == {
        "thinking": {"type": "enabled"},
        "reasoning_effort": "high",
    }
    assert thinking_extra_body("think-max") == {
        "thinking": {"type": "enabled"},
        "reasoning_effort": "max",
    }

    assert thinking_extra_body("non-thinking-nested") == {
        "chat_template_kwargs": {"thinking": False}
    }
    assert thinking_extra_body("think-high-nested") == {
        "chat_template_kwargs": {"thinking": True},
        "reasoning_effort": "high",
    }

    # The default battery must stay canonical-only: nested modes are opt-in, and
    # silently reintroducing one would change what every baseline run measures.
    assert set(DEFAULT_THINKING_MODES).isdisjoint(NESTED_THINKING_MODE_EXTRA_BODY)
    assert all("-nested" not in mode for mode in DEFAULT_THINKING_MODES)

    with pytest.raises(KeyError):
        thinking_extra_body("no-such-mode")


def test_thinking_strength_resolvers_agree_across_every_mode():
    """All three thinking-strength entry points must not drift apart.

    They already had, in two different ways:
      * cli._thinking_strength_from_extra_body read only the top-level `thinking` key,
        so every nested-shape request was recorded as "default" not "disabled";
      * long_context_probe._thinking_strength keyed off the mode NAME through a
        three-entry allowlist, so it returned the raw mode string for anything 79be5f1
        added -- `non-thinking-nested` was recorded as "non-thinking-nested".

    Nothing caught either, because each was only exercised through its own entry point
    and only with the canonical modes. All three now delegate to
    generation.thinking_strength; this test is what keeps them delegating.
    """
    from ds4_harness.cli import _thinking_strength_from_extra_body
    from ds4_harness.generation import thinking_strength
    from ds4_harness.long_context_probe import _thinking_strength as probe_strength

    for mode in THINKING_MODE_EXTRA_BODY:
        extra_body = thinking_extra_body(mode)
        expected = thinking_strength(extra_body)
        assert (
            _thinking_strength_from_extra_body(extra_body) == expected
        ), f"cli resolver disagrees on {mode}: {extra_body}"
        assert (
            probe_strength(mode) == expected
        ), f"long_context_probe resolver disagrees on {mode}: {extra_body}"

    # Agreement alone would also be satisfied by all three being wrong the same way, so
    # pin the actual values too -- in BOTH wire shapes.
    assert thinking_strength(thinking_extra_body("non-thinking")) == "disabled"
    assert thinking_strength(thinking_extra_body("non-thinking-nested")) == "disabled"
    assert thinking_strength(thinking_extra_body("think-high-nested")) == "high"
    assert thinking_strength(thinking_extra_body("think-max")) == "max"


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
any_terms: setInterval, requestAnimationFrame
any_terms_timezone: Asia/Shanghai, UTC+8
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
    assert prompt.expectation.any_terms == ("setInterval", "requestAnimationFrame")
    assert prompt.expectation.any_term_groups == (("Asia/Shanghai", "UTC+8"),)
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
    # Canonical (official DeepSeek) shape since 79be5f1: thinking is a TOP-LEVEL
    # field. The nested `chat_template_kwargs` shape still works and is covered by
    # test_thinking_extra_body_pins_both_wire_shapes via the opt-in `*-nested` modes.
    assert [payload["thinking"] for payload in captured_payloads] == [
        {"type": "disabled"},
        {"type": "disabled"},
    ]
    assert not any("chat_template_kwargs" in payload for payload in captured_payloads)
    rows = [json.loads(line) for line in jsonl_output.read_text().splitlines()]
    assert [row["round"] for row in rows] == [1, 2]
    assert rows[0]["language"] == "zh"
    assert rows[0]["workload"] == "translation"
    # No --model was passed, so this asserts that the DEFAULT reaches the row. Compare
    # against the constant rather than a literal: `cli.DEFAULT_MODEL` is resolved at
    # import time from `os.environ["MODEL"]`, so a hardcoded name makes the outcome
    # depend on whether the developer happens to export MODEL (or on .env, which
    # pytest does not load). That is how this assertion silently went stale.
    assert rows[0]["model"] == cli.DEFAULT_MODEL
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
    assert f"- Model: `{cli.DEFAULT_MODEL}`" in transcript
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


def test_generation_matrix_writes_code_artifacts_for_coding_prompts(
    monkeypatch,
    tmp_path,
):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "en" / "html_probe.md",
        """---
tags: coding, frontend_single_file
min_chars: 20
require_html_artifact: true
---
Output only a complete index.html file.
""",
    )

    def fake_post_json(base_url, path, payload, timeout):
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": (
                            "```html\n<!doctype html><html><head><style>body{color:#111}</style>   \n"
                            "</head><body>ok<script>console.log('ok')</script></body></html>  \n```"
                        ),
                    },
                }
            ],
            "usage": {"prompt_tokens": 4, "completion_tokens": 8, "total_tokens": 12},
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)
    transcript_dir = tmp_path / "generation"

    rc = cli.main(
        [
            "generation-matrix",
            "--prompt-root",
            str(prompt_root),
            "--thinking-mode",
            "non-thinking",
            "--variant",
            "mtp",
            "--repeat-count",
            "1",
            "--markdown-output-dir",
            str(transcript_dir),
        ]
    )

    assert rc == 0
    assert (transcript_dir / "en" / "html_probe.1.non-thinking.mtp.md").exists()
    html = (transcript_dir / "en" / "html_probe.1.non-thinking.mtp.html").read_text(
        encoding="utf-8"
    )
    assert html == (
        "<!doctype html><html><head><style>body{color:#111}</style>\n"
        "</head><body>ok<script>console.log('ok')</script></body></html>\n"
    )


def test_generation_matrix_writes_code_artifacts_for_unlabeled_code_fence(
    monkeypatch,
    tmp_path,
):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "en" / "html_probe.md",
        """---
tags: coding, frontend_single_file
min_chars: 20
require_html_artifact: true
---
Output only a complete index.html file.
""",
    )

    def fake_post_json(base_url, path, payload, timeout):
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": (
                            "```   \n"
                            "<!doctype html><html><head><style>body{color:#111}</style></head>"
                            "<body>ok<script>console.log('ok')</script></body></html>\n"
                            "```"
                        ),
                    },
                }
            ],
            "usage": {"prompt_tokens": 4, "completion_tokens": 8, "total_tokens": 12},
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)
    transcript_dir = tmp_path / "generation"

    rc = cli.main(
        [
            "generation-matrix",
            "--prompt-root",
            str(prompt_root),
            "--thinking-mode",
            "non-thinking",
            "--variant",
            "mtp",
            "--repeat-count",
            "1",
            "--markdown-output-dir",
            str(transcript_dir),
        ]
    )

    assert rc == 0
    html = (transcript_dir / "en" / "html_probe.1.non-thinking.mtp.html").read_text(
        encoding="utf-8"
    )
    assert html == (
        "<!doctype html><html><head><style>body{color:#111}</style></head>"
        "<body>ok<script>console.log('ok')</script></body></html>\n"
    )


def test_generation_matrix_can_override_prompt_sampling(monkeypatch, tmp_path):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "en" / "writing_probe.md",
        """---
tags: writing
temperature: 1.0
top_p: 1.0
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
            "non-thinking",
            "--temperature",
            "0.0",
            "--top-p",
            "0.95",
            "--override-prompt-sampling",
        ]
    )

    assert rc == 0
    assert captured["payload"]["temperature"] == 0.0
    assert captured["payload"]["top_p"] == 0.95


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
    # Canonical (official DeepSeek) shape since 79be5f1: top-level `thinking` plus
    # `reasoning_effort`. Our fork's issue-#19 fix
    # (`ChatCompletionRequest.apply_chat_template_kwargs`) translates the top-level
    # field into the tokenizer's chat_template_kwargs, so both shapes reach the same
    # routing — the earlier comment here claimed the opposite and was stale.
    assert captured["payload"]["thinking"] == {"type": "enabled"}
    assert captured["payload"]["reasoning_effort"] == "max"
    assert "chat_template_kwargs" not in captured["payload"]


def test_generation_matrix_applies_thinking_token_budgets_to_matching_modes(
    monkeypatch,
    tmp_path,
):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "en" / "writing_probe.md",
        """---
tags: writing
---
Write one sentence about local inference.
""",
    )
    payloads = []

    def fake_post_json(base_url, path, payload, timeout):
        payloads.append(payload)
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
            "non-thinking",
            "--thinking-mode",
            "think-high",
            "--thinking-mode",
            "think-max",
            "--think-high-token-budget",
            "2048",
            "--think-max-token-budget",
            "4096",
            "--max-tokens",
            "128",
            "--max-case-tokens",
            "3000",
            "--repeat-count",
            "1",
        ]
    )

    assert rc == 0
    assert len(payloads) == 3
    assert "thinking_token_budget" not in payloads[0]
    assert payloads[1]["thinking_token_budget"] == 2048
    assert payloads[2]["thinking_token_budget"] == 4096
    assert [payload["max_tokens"] for payload in payloads] == [128, 2176, 3000]


def test_generation_matrix_can_expand_think_max_request_max_tokens(
    monkeypatch,
    tmp_path,
):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "en" / "coding_probe.md",
        """---
tags: coding
max_tokens: 2048
---
Write a small program.
""",
    )
    payloads = []

    def fake_post_json(base_url, path, payload, timeout):
        payloads.append(payload)
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "print('ok')"},
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
            "non-thinking",
            "--thinking-mode",
            "think-max",
            "--max-case-tokens",
            "65536",
            "--think-max-request-max-tokens",
            "65536",
            "--repeat-count",
            "1",
        ]
    )

    assert rc == 0
    assert [payload["max_tokens"] for payload in payloads] == [2048, 65536]
    assert "thinking_token_budget" not in payloads[1]


def test_generation_matrix_can_skip_prompt_expectation_checks(monkeypatch, tmp_path):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "zh" / "html_probe.md",
        """---
tags: coding
min_chars: 1000
require_html_artifact: true
---
Write a complete HTML file.
""",
    )

    def fake_post_json(base_url, path, payload, timeout):
        return {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {
                        "role": "assistant",
                        "content": "",
                        "reasoning_content": "Long reasoning consumed the budget.",
                    },
                }
            ],
            "usage": {"completion_tokens": 4096},
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)
    jsonl_output = tmp_path / "generation.jsonl"

    rc = cli.main(
        [
            "generation-matrix",
            "--prompt-root",
            str(prompt_root),
            "--prompt",
            "html_probe",
            "--thinking-mode",
            "think-max",
            "--repeat-count",
            "1",
            "--skip-expectation-checks",
            "--jsonl-output",
            str(jsonl_output),
        ]
    )

    assert rc == 0
    row = json.loads(jsonl_output.read_text(encoding="utf-8"))
    assert row["ok"] is True
    assert row["detail"] == "expectation checks skipped"
    assert row["finish_reason"] == "length"


def test_generation_matrix_skipping_expectations_still_requires_choices(
    monkeypatch,
    tmp_path,
):
    prompt_root = tmp_path / "prompts"
    _write_prompt(
        prompt_root / "en" / "writing_probe.md",
        """---
tags: writing
min_chars: 500
---
Write an article.
""",
    )

    def fake_post_json(base_url, path, payload, timeout):
        return {"id": "no-choices"}

    monkeypatch.setattr(cli, "post_json", fake_post_json)

    rc = cli.main(
        [
            "generation-matrix",
            "--prompt-root",
            str(prompt_root),
            "--prompt",
            "writing_probe",
            "--skip-expectation-checks",
        ]
    )

    assert rc == 1
