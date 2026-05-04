import json
from pathlib import Path

from ds4_harness.cases import build_cases, select_cases
from ds4_harness.checks import Expectation, check_chat_response
from ds4_harness.generation import load_generation_prompts


ROOT = Path(__file__).resolve().parents[1]


def _chat_response(content="", finish_reason="stop", tool_calls=None):
    message = {"role": "assistant", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return {"choices": [{"finish_reason": finish_reason, "message": message}]}


def test_text_expectation_is_case_insensitive():
    result = check_chat_response(
        Expectation(all_terms=("Paris", "France")),
        _chat_response("the capital of france is paris."),
    )

    assert result.ok


def test_tool_expectation_requires_finish_reason_and_function_name():
    tool_calls = [
        {"type": "function", "function": {"name": "read", "arguments": "{}"}}
    ]
    expectation = Expectation(tool_name="read", finish_reason="tool_calls")

    assert check_chat_response(
        expectation,
        _chat_response(finish_reason="tool_calls", tool_calls=tool_calls),
    ).ok
    assert not check_chat_response(
        expectation,
        _chat_response("I should read first.", finish_reason="stop", tool_calls=[]),
    ).ok


def test_html_expectation_rejects_reasoning_without_artifact():
    expectation = Expectation(
        all_terms=("aquarium", "fish", "food"),
        require_html_artifact=True,
    )

    result = check_chat_response(
        expectation,
        _chat_response("I will build an aquarium with fish and food."),
    )

    assert not result.ok


def test_html_expectation_rejects_unclosed_artifact():
    result = check_chat_response(
        Expectation(require_html_artifact=True),
        _chat_response(
            """```html
<!doctype html>
<html>
<head><style>body { color: black; }</style></head>
<body><script>const value = 1;"""
        ),
    )

    assert not result.ok
    assert result.detail == "missing complete HTML artifact"


def test_malformed_empty_choices_response_is_failed_check():
    result = check_chat_response(Expectation(all_terms=("anything",)), {"choices": []})

    assert not result.ok
    assert "missing required terms" in result.detail


def test_case_selection_by_tag_and_name():
    cases = build_cases("deepseek-ai/DeepSeek-V4-Flash")

    quick = select_cases(cases, names=None, tags=["quick"], exclude_tags=None)
    named = select_cases(cases, names=["math_7_times_8"], tags=None, exclude_tags=None)
    no_long = select_cases(cases, names=None, tags=None, exclude_tags=["long"])

    assert {case.name for case in quick} >= {"math_7_times_8", "openclaw_read_tool"}
    assert [case.name for case in named] == ["math_7_times_8"]
    assert {case.name for case in no_long} == {case.name for case in cases}


def test_case_payload_round_trips_as_json():
    case = next(
        case
        for case in build_cases("deepseek-ai/DeepSeek-V4-Flash")
        if case.name == "openclaw_read_tool"
    )
    payload = case.to_payload(default_max_tokens=128, default_temperature=0.0)

    encoded = json.dumps(payload)

    assert json.loads(encoded)["tools"][0]["function"]["name"] == "read"
    assert payload["tool_choice"] == "auto"


def test_benchmark_prompt_suite_covers_core_real_scenario_prompts():
    prompts = load_generation_prompts(ROOT / "prompts")
    names = {prompt.name: prompt for prompt in prompts}

    for name in ("zh_wr_news_001", "en_wr_tech_001", "zh2en_bus_001", "en2zh_child_001"):
        assert name in names
        assert "subjective" in names[name].tags
        assert "benchmark-suite" in names[name].tags
        assert names[name].temperature == 1.0
        assert names[name].top_p == 1.0

    for preserved in ("aquarium_html", "clock_html"):
        assert preserved in names
        assert "user-report" in names[preserved].tags


def test_chinese_real_scenario_prompts_are_available_by_default_group():
    prompts = load_generation_prompts(ROOT / "prompts", languages=["zh"])
    benchmark_cn = [prompt for prompt in prompts if "benchmark-suite" in prompt.tags]
    coding_cn = [prompt for prompt in prompts if "coding" in prompt.tags]

    assert len(benchmark_cn) == 15
    assert {prompt.workload for prompt in benchmark_cn} == {
        "coding",
        "reading_summary",
        "translation",
        "writing",
    }
    assert [prompt.name for prompt in coding_cn if "user-report" in prompt.tags] == [
        "aquarium_html",
        "clock_html",
    ]
    assert all("subjective" in prompt.tags for prompt in benchmark_cn + coding_cn)


def test_english_real_scenario_prompts_include_coding_writing_translation():
    prompts = load_generation_prompts(ROOT / "prompts", languages=["en"])

    benchmark_en = [prompt for prompt in prompts if "benchmark-suite" in prompt.tags]
    assert len(benchmark_en) == 16
    assert {prompt.workload for prompt in benchmark_en} == {
        "coding",
        "reading_summary",
        "translation",
        "writing",
    }
    assert [prompt.name for prompt in prompts if "user-report" in prompt.tags] == [
        "aquarium_html",
        "clock_html",
    ]


def test_basic_quick_cases_allow_reasoning_token_budget():
    cases = build_cases("deepseek-ai/DeepSeek-V4-Flash")
    names = {case.name: case for case in cases}

    for name in ("math_7_times_8", "capital_of_france", "spanish_greeting"):
        assert names[name].max_tokens >= 256


def test_english_to_chinese_translation_accepts_concise_complete_translation():
    prompt = next(
        prompt
        for prompt in load_generation_prompts(ROOT / "prompts")
        if prompt.name == "en2zh_tech_001"
    )
    response = _chat_response(
        "本地运行大语言模型可以提升隐私性并降低延迟，但也会把运维责任转移到团队身上。"
        "真正需要评估的不是本地推理本身是否令人印象深刻，而是组织能否长期维护硬件、"
        "监控质量、处理升级风险，并承受迭代速度放缓带来的成本。对于工程管理者而言，"
        "这是一项关于控制权、可靠性和团队能力边界的综合判断，而不是一次简单的模型部署。"
        "如果缺少明确的容量规划、故障响应机制和质量评估流程，本地化带来的优势很容易被"
        "持续投入和复杂性抵消。"
    )

    result = check_chat_response(prompt.expectation, response)

    assert result.ok


def test_check_chat_response_requires_each_any_term_group():
    expectation = Expectation(
        any_terms=("setInterval", "requestAnimationFrame"),
        any_term_groups=(("Asia/Shanghai", "UTC+8", "Beijing Time"),),
    )
    response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Use requestAnimationFrame and UTC+8 for the clock.",
                }
            }
        ]
    }

    result = check_chat_response(expectation, response)

    assert result.ok


def test_check_chat_response_fails_missing_any_term_group():
    expectation = Expectation(
        any_terms=("setInterval", "requestAnimationFrame"),
        any_term_groups=(("Asia/Shanghai", "UTC+8", "Beijing Time"),),
    )
    response = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Use requestAnimationFrame for the clock.",
                }
            }
        ]
    }

    result = check_chat_response(expectation, response)

    assert not result.ok
    assert "missing any expected term group" in result.detail
