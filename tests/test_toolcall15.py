from ds4_harness.toolcall15 import (
    SYSTEM_PROMPT,
    ToolCallRecord,
    ToolCallState,
    evaluate_scenario,
    handle_tool_call,
    scenarios,
)


def test_toolcall15_has_fifteen_stable_scenarios():
    loaded = scenarios()

    assert [scenario.id for scenario in loaded] == [
        f"TC-{index:02d}" for index in range(1, 16)
    ]
    assert {scenario.category for scenario in loaded} == {"A", "B", "C", "D", "E"}


def test_toolcall15_system_prompt_pins_relative_date_context():
    assert "2026-03-20" in SYSTEM_PROMPT
    assert "Friday" in SYSTEM_PROMPT


def test_toolcall15_weather_specialist_passes_only_with_right_tool():
    state = ToolCallState(
        tool_calls=[
            ToolCallRecord(
                id="call_1",
                name="get_weather",
                arguments={"location": "Berlin"},
                turn=1,
            )
        ],
        tool_results=[],
        assistant_messages=[],
        final_answer="It is overcast in Berlin.",
    )

    result = evaluate_scenario("TC-01", state)

    assert result.status == "pass"
    assert result.points == 2


def test_toolcall15_translation_requires_two_separate_targets():
    state = ToolCallState(
        tool_calls=[
            ToolCallRecord(
                id="call_1",
                name="translate_text",
                arguments={
                    "text": "Where is the nearest hospital?",
                    "source_language": "English",
                    "target_language": "Spanish",
                },
                turn=1,
            ),
            ToolCallRecord(
                id="call_2",
                name="translate_text",
                arguments={
                    "text": "Where is the nearest hospital?",
                    "source_language": "English",
                    "target_language": "Japanese",
                },
                turn=1,
            ),
        ],
        tool_results=[],
        assistant_messages=[],
        final_answer="Spanish and Japanese translations are ready.",
    )

    result = evaluate_scenario("TC-06", state)

    assert result.status == "pass"
    assert result.points == 2


def test_toolcall15_mock_tools_return_expected_payloads():
    weather = handle_tool_call(
        "TC-01",
        ToolCallState(),
        ToolCallRecord(
            id="call_1",
            name="get_weather",
            arguments={"location": "Berlin"},
            turn=1,
        ),
    )
    search_empty = handle_tool_call(
        "TC-13",
        ToolCallState(),
        ToolCallRecord(
            id="call_2",
            name="search_files",
            arguments={"query": "Johnson proposal"},
            turn=1,
        ),
    )

    assert weather["location"] == "Berlin"
    assert search_empty == {"results": []}
