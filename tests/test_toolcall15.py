import json

from ds4_harness.toolcall15 import (
    SYSTEM_PROMPT,
    ToolCallRecord,
    ToolCallState,
    evaluate_scenario,
    handle_tool_call,
    localized_scenarios,
    run_scenario,
    scenarios,
)
from ds4_harness import cli


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


def test_toolcall15_chinese_scenario_set_and_aliases():
    loaded = localized_scenarios("zh")

    assert [scenario.id for scenario in loaded] == [
        f"TC-{index:02d}" for index in range(1, 16)
    ]
    assert "柏林" in loaded[0].user_message

    weather_state = ToolCallState(
        tool_calls=[
            ToolCallRecord(
                id="call_1",
                name="get_weather",
                arguments={"location": "柏林"},
                turn=1,
            )
        ],
        tool_results=[],
        assistant_messages=[],
        final_answer="柏林现在是阴天。",
    )
    assert evaluate_scenario("TC-01", weather_state).status == "pass"

    translation_state = ToolCallState(
        tool_calls=[
            ToolCallRecord(
                id="call_1",
                name="translate_text",
                arguments={
                    "text": "Where is the nearest hospital?",
                    "source_language": "英语",
                    "target_language": "西班牙语",
                },
                turn=1,
            ),
            ToolCallRecord(
                id="call_2",
                name="translate_text",
                arguments={
                    "text": "Where is the nearest hospital?",
                    "source_language": "英语",
                    "target_language": "日语",
                },
                turn=1,
            ),
        ],
        tool_results=[],
        assistant_messages=[],
        final_answer="已分别翻译成西班牙语和日语。",
    )
    assert evaluate_scenario("TC-06", translation_state).status == "pass"

    chain_state = ToolCallState(
        tool_calls=[
            ToolCallRecord(
                id="call_1",
                name="search_files",
                arguments={"query": "Q3 预算报告", "file_type": "any"},
                turn=1,
            ),
            ToolCallRecord(
                id="call_2",
                name="read_file",
                arguments={"file_id": "file_091"},
                turn=2,
            ),
            ToolCallRecord(
                id="call_3",
                name="get_contacts",
                arguments={"query": "经理"},
                turn=3,
            ),
            ToolCallRecord(
                id="call_4",
                name="send_email",
                arguments={
                    "to": "jordan.park@company.com",
                    "body": "Q3 总金额是 $4.4M。",
                },
                turn=4,
            ),
        ],
        tool_results=[],
        assistant_messages=[],
        final_answer="已把 Q3 总金额发给经理。",
    )
    assert evaluate_scenario("TC-07", chain_state).status == "pass"

    reminder_state = ToolCallState(
        tool_calls=[
            ToolCallRecord(
                id="call_1",
                name="get_weather",
                arguments={"location": "巴黎"},
                turn=1,
            ),
            ToolCallRecord(
                id="call_2",
                name="set_reminder",
                arguments={"message": "明早带伞", "datetime": "2026-03-21 08:00"},
                turn=2,
            ),
        ],
        tool_results=[],
        assistant_messages=[],
        final_answer="已设置提醒。",
    )
    assert evaluate_scenario("TC-08", reminder_state).status == "pass"

    refusal_state = ToolCallState(
        tool_calls=[],
        tool_results=[],
        assistant_messages=[],
        final_answer="抱歉，我没有删除邮件的工具，无法删除上个月的邮件。",
    )
    assert evaluate_scenario("TC-12", refusal_state).status == "pass"

    error_recovery_state = ToolCallState(
        tool_calls=[
            ToolCallRecord(
                id="call_1",
                name="get_stock_price",
                arguments={"ticker": "AAPL"},
                turn=1,
            )
        ],
        tool_results=[],
        assistant_messages=["股票服务暂时不可用，因为出现限流，请稍后再试。"],
        final_answer="股票服务暂时不可用，请稍后再试。",
    )
    assert evaluate_scenario("TC-14", error_recovery_state).status == "pass"


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


def test_toolcall15_cli_writes_failure_artifact_on_request_error(monkeypatch, tmp_path):
    def fake_post_json(base_url, path, payload, timeout):
        raise RuntimeError("connection refused")

    monkeypatch.setattr("ds4_harness.toolcall15.post_json", fake_post_json)
    output = tmp_path / "toolcall15.json"

    rc = cli.main(
        [
            "toolcall15",
            "--scenario",
            "TC-01",
            "--json-output",
            str(output),
        ]
    )

    assert rc == 1
    report = output.read_text(encoding="utf-8")
    assert "TC-01" in report
    assert "connection refused" in report
    assert '"failures": 1' in report


def test_toolcall15_cli_repeats_and_preserves_rounds(monkeypatch, tmp_path):
    calls = []

    def fake_run_suite(*args, **kwargs):
        calls.append((args, kwargs))
        return [
            {
                "id": "TC-01",
                "title": "Direct Specialist Match",
                "category": "A",
                "status": "pass",
                "points": 2,
                "summary": "Used get_weather with Berlin only.",
                "note": None,
                "tool_calls": [],
                "final_answer": "Berlin is overcast.",
                "elapsed_seconds": 1.25,
                "usage_totals": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "trace": [],
            }
        ]

    monkeypatch.setattr(cli, "run_suite", fake_run_suite)
    output = tmp_path / "toolcall15.json"

    rc = cli.main(
        [
            "toolcall15",
            "--scenario",
            "TC-01",
            "--repeat-count",
            "2",
            "--json-output",
            str(output),
        ]
    )

    assert rc == 0
    assert len(calls) == 2
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["summary"]["rounds"] == 2
    assert data["summary"]["cases"] == 1
    assert data["summary"]["total_cases"] == 2
    assert data["summary"]["points"] == 4
    assert [round_data["round"] for round_data in data["rounds"]] == [1, 2]
    assert [round_data["results"][0]["round"] for round_data in data["rounds"]] == [
        1,
        2,
    ]


def test_toolcall15_cli_accepts_official_api_options(monkeypatch, tmp_path):
    calls = []

    def fake_run_suite(*args, **kwargs):
        calls.append((args, kwargs))
        return [
            {
                "id": "TC-01",
                "title": "Direct Specialist Match",
                "category": "A",
                "status": "pass",
                "points": 2,
                "summary": "ok",
                "note": None,
                "tool_calls": [],
                "final_answer": "",
                "elapsed_seconds": 1.0,
                "usage_totals": {},
                "trace": [],
            }
        ]

    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(cli, "run_suite", fake_run_suite)
    output = tmp_path / "toolcall15.json"

    rc = cli.main(
        [
            "toolcall15",
            "--api-key-env",
            "DEEPSEEK_API_KEY",
            "--extra-body-json",
            '{"thinking":{"type":"enabled"}}',
            "--json-output",
            str(output),
        ]
    )

    assert rc == 0
    kwargs = calls[0][1]
    assert kwargs["headers"] == {"Authorization": "Bearer test-key"}
    assert kwargs["extra_body"] == {"thinking": {"type": "enabled"}}
    assert kwargs["preserve_reasoning_content"] is True


def test_toolcall15_replays_empty_reasoning_content(monkeypatch):
    requests = []

    def fake_post_json(base_url, path, payload, timeout, *, headers=None):
        requests.append(payload)
        if len(requests) == 1:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "reasoning_content": "",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {
                                        "name": "get_weather",
                                        "arguments": '{"location":"Berlin"}',
                                    },
                                }
                            ],
                        }
                    }
                ],
                "usage": {},
            }
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Berlin is overcast and 8 C.",
                        "tool_calls": [],
                    }
                }
            ],
            "usage": {},
        }

    monkeypatch.setattr("ds4_harness.toolcall15.post_json", fake_post_json)

    run_scenario(
        "https://api.deepseek.com",
        "deepseek-v4-flash",
        localized_scenarios("en")[0],
        temperature=0.0,
        timeout=30,
        max_turns=2,
        headers={"Authorization": "Bearer test-key"},
        extra_body={"thinking": {"type": "enabled"}},
    )

    replayed_assistant = requests[1]["messages"][2]
    assert replayed_assistant["reasoning_content"] == ""
    assert requests[0]["thinking"] == {"type": "enabled"}


def test_toolcall15_cli_can_run_english_and_chinese_sets(monkeypatch, tmp_path):
    seen_sets = []

    def fake_run_suite(*args, **kwargs):
        scenario_set = kwargs["scenario_set"]
        seen_sets.append(scenario_set)
        return [
            {
                "id": "TC-01",
                "title": "Direct Specialist Match",
                "category": "A",
                "status": "pass",
                "points": 2,
                "summary": f"{scenario_set} passed",
                "note": None,
                "tool_calls": [],
                "final_answer": "",
                "elapsed_seconds": 1.0,
                "usage_totals": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "trace": [],
            }
        ]

    monkeypatch.setattr(cli, "run_suite", fake_run_suite)
    output = tmp_path / "toolcall15.json"

    rc = cli.main(
        [
            "toolcall15",
            "--scenario-set",
            "both",
            "--repeat-count",
            "3",
            "--json-output",
            str(output),
        ]
    )

    assert rc == 0
    assert seen_sets == ["en", "en", "en", "zh", "zh", "zh"]
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["summary"]["scenario_sets"] == ["en", "zh"]
    assert data["summary"]["rounds"] == 3
    assert data["summary"]["cases"] == 2
    assert data["summary"]["total_cases"] == 6
    assert {row["scenario_set"] for row in data["results"]} == {"en", "zh"}
