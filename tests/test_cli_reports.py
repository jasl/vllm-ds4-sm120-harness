import json

from ds4_harness import cli
from ds4_harness.oracle import OracleCase


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


def test_chat_smoke_can_use_bearer_token_from_env(monkeypatch):
    captured = {}

    def fake_post_json(base_url, path, payload, timeout, *, headers=None):
        captured["headers"] = headers
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "7 * 8 = 56"},
                }
            ]
        }

    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-secret")
    monkeypatch.setattr(cli, "post_json", fake_post_json)

    rc = cli.main(
        [
            "chat-smoke",
            "--case",
            "math_7_times_8",
            "--api-key-env",
            "DEEPSEEK_API_KEY",
        ]
    )

    assert rc == 0
    assert captured["headers"] == {"Authorization": "Bearer test-secret"}


def test_chat_smoke_can_cap_case_max_tokens(monkeypatch):
    captured = {}

    def fake_post_json(base_url, path, payload, timeout):
        captured["payload"] = payload
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": "7 * 8 = 56",
                    },
                }
            ]
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)

    rc = cli.main(
        [
            "chat-smoke",
            "--case",
            "math_7_times_8",
            "--max-case-tokens",
            "128",
        ]
    )

    assert rc == 0
    assert captured["payload"]["max_tokens"] == 128


def test_chat_smoke_merges_extra_body_json(monkeypatch):
    captured = {}

    def fake_post_json(base_url, path, payload, timeout):
        captured["payload"] = payload
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "7 * 8 = 56"},
                }
            ]
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)

    rc = cli.main(
        [
            "chat-smoke",
            "--case",
            "math_7_times_8",
            "--extra-body-json",
            '{"thinking":{"type":"enabled"},"reasoning_effort":"high"}',
        ]
    )

    assert rc == 0
    assert captured["payload"]["thinking"] == {"type": "enabled"}
    assert captured["payload"]["reasoning_effort"] == "high"


def test_chat_smoke_repeat_records_round_and_elapsed(monkeypatch, tmp_path):
    def fake_post_json(base_url, path, payload, timeout):
        return {
            "model": payload["model"],
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "7 * 8 = 56"},
                }
            ],
            "usage": {
                "prompt_tokens": 5,
                "completion_tokens": 4,
                "total_tokens": 9,
            },
        }

    monkeypatch.setattr(cli, "post_json", fake_post_json)
    jsonl_output = tmp_path / "smoke.jsonl"
    markdown_output = tmp_path / "smoke.md"

    rc = cli.main(
        [
            "chat-smoke",
            "--case",
            "math_7_times_8",
            "--repeat-count",
            "2",
            "--jsonl-output",
            str(jsonl_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    rows = [json.loads(line) for line in jsonl_output.read_text().splitlines()]
    assert [row["round"] for row in rows] == [1, 2]
    assert all(row["elapsed_seconds"] >= 0 for row in rows)
    report = markdown_output.read_text(encoding="utf-8")
    assert "- Repeat count: 2" in report
    assert "- Round: 2" in report


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

    prompt_root = tmp_path / "prompts"
    (prompt_root / "en").mkdir(parents=True)
    (prompt_root / "en" / "translation_quality_en_to_zh.md").write_text(
        """---
tags: translation, subjective
all_terms: 隐私, 延迟, 运维
min_chars: 80
---
Translate the following paragraph into natural, polished Simplified Chinese.
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "post_json", fake_post_json)
    markdown_output_dir = tmp_path / "generation"
    rc = cli.main(
        [
            "generation-matrix",
            "--prompt-root",
            str(prompt_root),
            "--thinking-mode",
            "non-thinking",
            "--variant",
            "nomtp",
            "--markdown-output-dir",
            str(markdown_output_dir),
        ]
    )

    assert rc == 0
    report = (
        markdown_output_dir
        / "en"
        / "translation_quality_en_to_zh.1.non-thinking.nomtp.md"
    ).read_text(encoding="utf-8")
    assert "- Case: `translation_quality_en_to_zh`" in report
    assert "- Workload: `translation`" in report
    assert "Translate the following paragraph" in report
    assert answer in report


def test_oracle_compare_default_top_n_stays_within_vllm_http_limit(tmp_path):
    parser = cli.build_parser()

    args = parser.parse_args(["oracle-compare", "--oracle-dir", str(tmp_path)])

    assert args.top_n == 20


def test_oracle_compare_records_request_errors(monkeypatch, tmp_path):
    response = {
        "choices": [
            {
                "text": "",
                "logprobs": {
                    "tokens": ["token_id:10"],
                    "token_logprobs": [-0.1],
                    "top_logprobs": [{"token_id:10": -0.1}],
                },
                "token_ids": [10],
                "prompt_token_ids": [1, 2, 3],
            }
        ]
    }
    case = OracleCase(
        name="bad_request",
        path="/v1/completions",
        request={"prompt": "x", "logprobs": 50},
        response=response,
    )

    monkeypatch.setattr(cli, "load_oracle_cases", lambda oracle_dir: [case])

    def fake_post_json(base_url, path, payload, timeout):
        raise RuntimeError("HTTP 400")

    monkeypatch.setattr(cli, "post_json", fake_post_json)
    json_output = tmp_path / "oracle_compare.json"

    rc = cli.main(
        [
            "oracle-compare",
            "--oracle-dir",
            str(tmp_path),
            "--json-output",
            str(json_output),
        ]
    )

    assert rc == 1
    rows = json.loads(json_output.read_text(encoding="utf-8"))
    assert rows[0]["name"] == "bad_request"
    assert rows[0]["ok"] is False
    assert "HTTP 400" in rows[0]["error"]


def test_oracle_compare_clamps_request_logprobs_to_top_n(monkeypatch, tmp_path):
    response = {
        "choices": [
            {
                "text": "",
                "logprobs": {
                    "tokens": ["token_id:10"],
                    "token_logprobs": [-0.1],
                    "top_logprobs": [{"token_id:10": -0.1}],
                },
                "token_ids": [10],
                "prompt_token_ids": [1, 2, 3],
            }
        ]
    }
    case = OracleCase(
        name="logprobs_limit",
        path="/v1/completions",
        request={"prompt": "x", "logprobs": 50},
        response=response,
    )
    captured_payloads = []

    monkeypatch.setattr(cli, "load_oracle_cases", lambda oracle_dir: [case])

    def fake_post_json(base_url, path, payload, timeout):
        captured_payloads.append(payload)
        return response

    monkeypatch.setattr(cli, "post_json", fake_post_json)

    rc = cli.main(["oracle-compare", "--oracle-dir", str(tmp_path)])

    assert rc == 0
    assert captured_payloads[0]["logprobs"] == 20


def test_oracle_compare_requires_prompt_ids_by_tokenizing_actual_prompt(
    monkeypatch, tmp_path
):
    response = {
        "choices": [
            {
                "text": "",
                "logprobs": {
                    "tokens": ["token_id:10"],
                    "token_logprobs": [-0.1],
                    "top_logprobs": [{"token_id:10": -0.1}],
                },
                "token_ids": [10],
                "prompt_token_ids": [1, 2, 3],
            }
        ]
    }
    case = OracleCase(
        name="prompt_ids",
        path="/v1/completions",
        request={"model": "m", "prompt": "x", "logprobs": 20},
        response=response,
    )
    paths = []

    monkeypatch.setattr(cli, "load_oracle_cases", lambda oracle_dir: [case])

    def fake_post_json(base_url, path, payload, timeout):
        paths.append(path)
        if path == "/tokenize":
            return {"tokens": [1, 2, 3]}
        actual = json.loads(json.dumps(response))
        actual["choices"][0]["prompt_token_ids"] = None
        return actual

    monkeypatch.setattr(cli, "post_json", fake_post_json)

    rc = cli.main(
        [
            "oracle-compare",
            "--oracle-dir",
            str(tmp_path),
            "--require-prompt-ids",
        ]
    )

    assert rc == 0
    assert paths == ["/v1/completions", "/tokenize"]


def test_oracle_export_cli_writes_bundle(monkeypatch, tmp_path):
    captured = {}

    def fake_export_completion_oracles(**kwargs):
        captured.update(kwargs)
        return [{"name": "completion_short_math_logprobs20", "ok": True}]

    monkeypatch.setattr(cli, "export_completion_oracles", fake_export_completion_oracles)

    rc = cli.main(
        [
            "oracle-export",
            "--base-url",
            "http://127.0.0.1:8000",
            "--model",
            "deepseek-ai/DeepSeek-V4-Flash",
            "--output-dir",
            str(tmp_path),
            "--case",
            "completion_short_math_logprobs20",
            "--logprobs",
            "10",
            "--timeout",
            "12",
        ]
    )

    assert rc == 0
    assert captured["base_url"] == "http://127.0.0.1:8000"
    assert captured["model"] == "deepseek-ai/DeepSeek-V4-Flash"
    assert captured["output_dir"] == tmp_path
    assert captured["case_names"] == ["completion_short_math_logprobs20"]
    assert captured["logprobs"] == 10
    assert captured["timeout"] == 12
