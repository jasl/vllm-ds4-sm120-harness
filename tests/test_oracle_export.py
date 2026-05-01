import json

from ds4_harness.oracle import load_oracle_cases
from ds4_harness.oracle_export import (
    default_completion_oracle_cases,
    export_completion_oracles,
)


def _response(text="ok"):
    return {
        "choices": [
            {
                "text": text,
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


def test_default_completion_oracle_cases_cover_short_code_translation_and_long_prefill():
    cases = default_completion_oracle_cases()
    names = {case.name for case in cases}

    assert "completion_short_math_logprobs20" in names
    assert "completion_translation_logprobs20" in names
    assert "completion_code_probe_logprobs20" in names
    assert "completion_long_prefill_2048_logprobs20" in names
    assert all(case.temperature == 0.0 for case in cases)
    assert all(case.logprobs == 20 for case in cases)


def test_export_completion_oracles_writes_wrapped_bundle_and_summary(tmp_path):
    requests = []

    def fake_post_json(base_url, path, payload, timeout):
        requests.append((base_url, path, payload, timeout))
        if path == "/tokenize":
            return {"tokens": [1, 2, 3], "count": 3}
        return _response("56")

    rows = export_completion_oracles(
        "http://127.0.0.1:8000",
        "deepseek-ai/DeepSeek-V4-Flash",
        tmp_path,
        case_names=["completion_short_math_logprobs20"],
        post_json_func=fake_post_json,
        timeout=12,
        logprobs=10,
    )

    assert rows[0]["ok"] is True
    assert requests[0][1] == "/tokenize"
    assert requests[1][1] == "/v1/completions"
    assert requests[1][2]["temperature"] == 0.0
    assert requests[1][2]["logprobs"] == 10
    assert requests[0][3] == 12

    wrapped = json.loads(
        (tmp_path / "completion_short_math_logprobs20.json").read_text(
            encoding="utf-8"
        )
    )
    assert wrapped["path"] == "/v1/completions"
    assert wrapped["status"] == 200
    assert wrapped["request"]["model"] == "deepseek-ai/DeepSeek-V4-Flash"
    assert wrapped["tokenize_response"]["tokens"] == [1, 2, 3]
    assert wrapped["response"]["choices"][0]["prompt_token_ids"] == [1, 2, 3]
    assert wrapped["response"]["choices"][0]["text"] == "56"
    assert (tmp_path / "tokenize_completion_short_math_logprobs20.json").exists()
    assert (tmp_path / "oracle_export_summary.json").exists()
    assert (tmp_path / "oracle_export_summary.md").exists()

    loaded = load_oracle_cases(tmp_path)
    assert len(loaded) == 1
    assert loaded[0].name == "completion_short_math_logprobs20"


def test_export_completion_oracles_keeps_going_after_case_error(tmp_path):
    def fake_post_json(base_url, path, payload, timeout):
        if path == "/tokenize":
            return {"tokens": [1, 2, 3], "count": 3}
        if "7*8" in payload["prompt"]:
            raise RuntimeError("HTTP 500")
        return _response("ok")

    rows = export_completion_oracles(
        "http://127.0.0.1:8000",
        "deepseek-ai/DeepSeek-V4-Flash",
        tmp_path,
        case_names=[
            "completion_short_math_logprobs20",
            "completion_raw_intro_logprobs20",
        ],
        post_json_func=fake_post_json,
    )

    assert [row["ok"] for row in rows] == [False, True]
    failed = json.loads(
        (tmp_path / "completion_short_math_logprobs20.json").read_text(
            encoding="utf-8"
        )
    )
    assert failed["status"] == "error"
    assert "HTTP 500" in failed["error"]


def test_export_completion_oracles_can_stop_after_first_error(tmp_path):
    calls = []

    def fake_post_json(base_url, path, payload, timeout):
        calls.append(path)
        raise TimeoutError("server did not respond")

    rows = export_completion_oracles(
        "http://127.0.0.1:8000",
        "deepseek-ai/DeepSeek-V4-Flash",
        tmp_path,
        post_json_func=fake_post_json,
        stop_on_error=True,
    )

    assert len(rows) == 1
    assert rows[0]["ok"] is False
    assert calls == ["/tokenize"]
