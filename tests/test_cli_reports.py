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
