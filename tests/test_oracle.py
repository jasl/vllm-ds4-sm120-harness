import json

from ds4_harness.oracle import compare_response, load_oracle_cases


def _response(tokens, top_logprobs):
    token_ids = [int(token.split(":", 1)[1]) for token in tokens]
    return {
        "choices": [
            {
                "text": "",
                "logprobs": {
                    "tokens": tokens,
                    "token_logprobs": [-0.1 * (i + 1) for i in range(len(tokens))],
                    "top_logprobs": top_logprobs,
                },
                "token_ids": token_ids,
                "prompt_token_ids": [1, 2, 3],
            }
        ]
    }


def test_compare_response_accepts_identical_top_logprobs():
    top_logprobs = [
        {"token_id:10": -0.1, "token_id:20": -1.0},
        {"token_id:11": -0.2, "token_id:21": -1.2},
    ]

    report = compare_response(
        "case0",
        _response(["token_id:10", "token_id:11"], top_logprobs),
        _response(["token_id:10", "token_id:11"], top_logprobs),
        top_n=2,
    )

    assert report["tokens_match"] is True
    assert report["top1_match_rate"] == 1.0
    assert report["topk_overlap_mean"] == 1.0
    assert report["max_common_logprob_abs_error"] == 0.0


def test_compare_response_reports_first_token_divergence():
    report = compare_response(
        "case0",
        _response(
            ["token_id:10", "token_id:11"],
            [
                {"token_id:10": -0.1, "token_id:20": -1.0},
                {"token_id:11": -0.2, "token_id:21": -1.2},
            ],
        ),
        _response(
            ["token_id:10", "token_id:99"],
            [
                {"token_id:10": -0.1, "token_id:20": -1.0},
                {"token_id:99": -0.2, "token_id:21": -1.2},
            ],
        ),
        top_n=2,
    )

    assert report["tokens_match"] is False
    assert report["first_token_mismatch"] == {
        "step": 1,
        "oracle": "token_id:11",
        "actual": "token_id:99",
    }
    assert report["matching_prefix_tokens"] == 1


def test_compare_response_marks_prompt_token_mismatch():
    oracle = _response(["token_id:10"], [{"token_id:10": -0.1}])
    actual = _response(["token_id:10"], [{"token_id:10": -0.1}])
    actual["choices"][0]["prompt_token_ids"] = [1, 9, 3]

    report = compare_response("case0", oracle, actual, top_n=1)

    assert report["tokens_match"] is True
    assert report["prompt_token_ids_match"] is False


def test_load_oracle_cases_supports_request_response_pairs(tmp_path):
    request = {"model": "m", "prompt": "p", "logprobs": 50}
    response = _response(["token_id:10"], [{"token_id:10": -0.1}])
    (tmp_path / "request_short.json").write_text(json.dumps(request))
    (tmp_path / "response_short.json").write_text(json.dumps(response))

    cases = load_oracle_cases(tmp_path)

    assert len(cases) == 1
    assert cases[0].name == "short"
    assert cases[0].path == "/v1/completions"
    assert cases[0].request == request
    assert cases[0].response == response


def test_load_oracle_cases_supports_wrapped_completion_exports(tmp_path):
    request = {"model": "m", "prompt": "p", "logprobs": 50}
    response = _response(["token_id:10"], [{"token_id:10": -0.1}])
    wrapped = {
        "name": "completion_probe",
        "path": "/v1/completions",
        "status": 200,
        "request": request,
        "response": response,
    }
    chat_wrapped = {
        "name": "chat_probe",
        "path": "/v1/chat/completions",
        "request": {"messages": []},
        "response": {"choices": []},
    }
    (tmp_path / "completion_probe.json").write_text(json.dumps(wrapped))
    (tmp_path / "chat_probe.json").write_text(json.dumps(chat_wrapped))

    cases = load_oracle_cases(tmp_path)

    assert len(cases) == 1
    assert cases[0].name == "completion_probe"
    assert cases[0].path == "/v1/completions"
