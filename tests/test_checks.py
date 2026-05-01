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


def test_subjective_writing_and_translation_prompts_are_available():
    prompts = load_generation_prompts(ROOT / "prompts")
    names = {prompt.name: prompt for prompt in prompts}

    for name in (
        "writing_local_llm_tradeoffs",
        "translation_en_to_zh",
        "translation_zh_to_en",
    ):
        assert name in names
        assert "subjective" in names[name].tags
        assert names[name].temperature == 1.0


def test_chinese_real_scenario_prompts_are_available_by_default_group():
    prompts = load_generation_prompts(ROOT / "prompts", languages=["zh"])
    quality_cn = [prompt for prompt in prompts if "translation" in prompt.tags or "writing" in prompt.tags]
    coding_cn = [prompt for prompt in prompts if "coding" in prompt.tags]

    assert [prompt.name for prompt in quality_cn] == [
        "translation_zh_to_en",
        "writing_local_llm_tradeoffs",
    ]
    assert [prompt.name for prompt in coding_cn] == [
        "aquarium_html",
        "clock_html",
    ]
    assert all("subjective" in prompt.tags for prompt in quality_cn + coding_cn)


def test_english_real_scenario_prompts_include_coding_writing_translation():
    prompts = load_generation_prompts(ROOT / "prompts", languages=["en"])

    assert [prompt.name for prompt in prompts] == [
        "aquarium_html",
        "clock_html",
        "translation_en_to_zh",
        "writing_follow_instructions",
    ]
    assert {prompt.workload for prompt in prompts} == {
        "coding",
        "translation",
        "writing",
    }


def test_basic_quick_cases_allow_reasoning_token_budget():
    cases = build_cases("deepseek-ai/DeepSeek-V4-Flash")
    names = {case.name: case for case in cases}

    for name in ("math_7_times_8", "capital_of_france", "spanish_greeting"):
        assert names[name].max_tokens >= 256


def test_english_to_chinese_translation_accepts_concise_complete_translation():
    prompt = next(
        prompt
        for prompt in load_generation_prompts(ROOT / "prompts")
        if prompt.name == "translation_en_to_zh"
    )
    response = _chat_response(
        "本地运行大语言模型可以提升隐私性并降低延迟，但也将运维责任转移到了团队身上。"
        "实际的问题不在于本地推理是否令人惊叹，而在于该组织能否维护硬件、监控质量，"
        "并承担迭代速度放缓带来的成本。"
    )

    result = check_chat_response(prompt.expectation, response)

    assert result.ok
