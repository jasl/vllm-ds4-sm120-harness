from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field, replace
from typing import Any

from ds4_harness.client import post_json


Json = dict[str, Any]

SYSTEM_PROMPT = """You are a helpful assistant with access to the tools provided.

Rules:
- Use a tool ONLY when it is necessary to fulfill the user's request.
- If you can answer directly from your own knowledge, do so without calling a tool.
- If a tool call fails, explain the failure and suggest an alternative approach.
- Never invent information that a tool should provide."""
BENCHMARK_CONTEXT = (
    "Benchmark context: today is 2026-03-20 (Friday). "
    "Use this date for any relative time request."
)


@dataclass(frozen=True)
class ToolCallRecord:
    id: str
    name: str
    arguments: Json
    turn: int


@dataclass(frozen=True)
class ToolResultRecord:
    call_id: str
    name: str
    result: Json


@dataclass
class ToolCallState:
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    tool_results: list[ToolResultRecord] = field(default_factory=list)
    assistant_messages: list[str] = field(default_factory=list)
    final_answer: str = ""
    meta: Json = field(default_factory=dict)


@dataclass(frozen=True)
class Evaluation:
    status: str
    points: int
    summary: str
    note: str | None = None


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    category: str
    user_message: str
    description: str


def _tool(name: str, description: str, properties: Json, required: list[str]) -> Json:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }


def universal_tools() -> list[Json]:
    return [
        _tool(
            "web_search",
            "Search the web for current information",
            {"query": {"type": "string"}, "max_results": {"type": "integer"}},
            ["query"],
        ),
        _tool(
            "get_weather",
            "Get current weather for a specific location",
            {
                "location": {"type": "string"},
                "units": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            ["location"],
        ),
        _tool(
            "calculator",
            "Perform mathematical calculations",
            {"expression": {"type": "string"}},
            ["expression"],
        ),
        _tool(
            "send_email",
            "Send an email to a recipient",
            {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "attachments": {"type": "array", "items": {"type": "string"}},
            },
            ["to", "subject", "body"],
        ),
        _tool(
            "search_files",
            "Search for files by name or content",
            {
                "query": {"type": "string"},
                "file_type": {
                    "type": "string",
                    "enum": ["pdf", "docx", "xlsx", "any"],
                },
            },
            ["query"],
        ),
        _tool(
            "read_file",
            "Read the contents of a specific file",
            {"file_id": {"type": "string"}},
            ["file_id"],
        ),
        _tool(
            "create_calendar_event",
            "Create a new calendar event",
            {
                "title": {"type": "string"},
                "date": {"type": "string"},
                "time": {"type": "string"},
                "duration_minutes": {"type": "integer"},
                "attendees": {"type": "array", "items": {"type": "string"}},
            },
            ["title", "date", "time"],
        ),
        _tool(
            "get_contacts",
            "Look up contacts by name or group",
            {"query": {"type": "string"}},
            ["query"],
        ),
        _tool(
            "translate_text",
            "Translate text from one language to another",
            {
                "text": {"type": "string"},
                "source_language": {"type": "string"},
                "target_language": {"type": "string"},
            },
            ["text", "source_language", "target_language"],
        ),
        _tool(
            "get_stock_price",
            "Get the current stock price for a ticker symbol",
            {"ticker": {"type": "string"}},
            ["ticker"],
        ),
        _tool(
            "set_reminder",
            "Set a reminder for a future time",
            {
                "message": {"type": "string"},
                "datetime": {"type": "string"},
            },
            ["message", "datetime"],
        ),
        _tool(
            "run_code",
            "Execute a code snippet and return the output",
            {
                "language": {"type": "string", "enum": ["python", "javascript"]},
                "code": {"type": "string"},
            },
            ["language", "code"],
        ),
    ]


def scenarios() -> list[Scenario]:
    english = [
        Scenario(
            "TC-01",
            "Direct Specialist Match",
            "A",
            "What's the weather like in Berlin right now?",
            "Use get_weather instead of web_search.",
        ),
        Scenario(
            "TC-02",
            "Distractor Resistance",
            "A",
            "What is the current price of AAPL stock?",
            "Use get_stock_price without extra tools.",
        ),
        Scenario(
            "TC-03",
            "Implicit Tool Need",
            "A",
            "I need to let Sarah know the meeting moved to 3pm.",
            "Look up Sarah before sending the email.",
        ),
        Scenario(
            "TC-04",
            "Unit Handling",
            "B",
            "What's the temperature in Tokyo in Fahrenheit?",
            "Preserve the requested units parameter.",
        ),
        Scenario(
            "TC-05",
            "Date and Time Parsing",
            "B",
            (
                "Schedule a team standup for next Monday at 9:30am, "
                "30 minutes, with Alex and Jamie."
            ),
            "Parse the relative date from 2026-03-20 Friday.",
        ),
        Scenario(
            "TC-06",
            "Multi-Value Extraction",
            "B",
            (
                "Translate 'Where is the nearest hospital?' from English to "
                "both Spanish and Japanese."
            ),
            "Split one-to-many translation into two tool calls.",
        ),
        Scenario(
            "TC-07",
            "Search Read Act",
            "C",
            "Find the Q3 budget report and email the total to my manager.",
            "Carry file and contact data across a multi-step chain.",
        ),
        Scenario(
            "TC-08",
            "Conditional Branching",
            "C",
            (
                "Check the weather in Paris. If it's raining, remind me to "
                "bring an umbrella tomorrow at 8am."
            ),
            "Branch after observing the weather result.",
        ),
        Scenario(
            "TC-09",
            "Parallel Independence",
            "C",
            "What's the weather in London and the stock price of MSFT?",
            "Handle two independent current-information requests.",
        ),
        Scenario(
            "TC-10",
            "Trivial Knowledge",
            "D",
            "What year did World War II end?",
            "Avoid tools for basic knowledge.",
        ),
        Scenario(
            "TC-11",
            "Simple Math",
            "D",
            "What is 15% of 200?",
            "Avoid tools for easy arithmetic.",
        ),
        Scenario(
            "TC-12",
            "Impossible Request",
            "D",
            "Delete all my emails from last month.",
            "Refuse when no suitable tool exists.",
        ),
        Scenario(
            "TC-13",
            "Empty Results",
            "E",
            "Find the Johnson proposal document.",
            "Recover after an empty file search.",
        ),
        Scenario(
            "TC-14",
            "Malformed Response",
            "E",
            "What's Apple's stock price?",
            "Surface tool errors instead of hallucinating a price.",
        ),
        Scenario(
            "TC-15",
            "Conflicting Information",
            "E",
            "Search for the population of Iceland and calculate what 2% of it would be.",
            "Carry the searched value into calculator.",
        ),
    ]
    return english


ZH_USER_MESSAGES = {
    "TC-01": "请查一下柏林现在的天气怎么样？",
    "TC-02": "AAPL 股票现在的价格是多少？",
    "TC-03": "我需要通知 Sarah，会议改到下午 3 点了。",
    "TC-04": "请告诉我东京现在的温度，用华氏度表示。",
    "TC-05": "帮我把团队站会安排到下周一上午 9:30，30 分钟，参会人是 Alex 和 Jamie。",
    "TC-06": "请把 'Where is the nearest hospital?' 从英语分别翻译成西班牙语和日语。",
    "TC-07": "找到 Q3 预算报告，然后把总金额发邮件告诉我的经理。",
    "TC-08": "查一下巴黎的天气。如果下雨，提醒我明天早上 8 点带伞。",
    "TC-09": "请同时告诉我伦敦天气和 MSFT 股票价格。",
    "TC-10": "第二次世界大战是哪一年结束的？",
    "TC-11": "200 的 15% 是多少？",
    "TC-12": "帮我删除上个月的所有邮件。",
    "TC-13": "帮我找 Johnson proposal 文档。",
    "TC-14": "苹果公司的股票价格是多少？",
    "TC-15": "搜索冰岛的人口，然后计算其中 2% 是多少。",
}


def localized_scenarios(scenario_set: str = "en") -> list[Scenario]:
    if scenario_set == "en":
        return scenarios()
    if scenario_set != "zh":
        raise KeyError(f"unknown ToolCall-15 scenario set {scenario_set!r}")
    return [
        replace(scenario, user_message=ZH_USER_MESSAGES.get(scenario.id, scenario.user_message))
        for scenario in scenarios()
    ]


def _scenario_map() -> dict[str, Scenario]:
    return {scenario.id: scenario for scenario in scenarios()}


def _norm(value: Any) -> str:
    return str(value or "").strip().casefold()


def _contains(value: Any, expected: str) -> bool:
    return expected.casefold() in str(value or "").casefold()


def _contains_any(value: Any, *expected: str) -> bool:
    return any(_contains(value, item) for item in expected)


def _is_march_21_8am(value: Any) -> bool:
    text = str(value or "").strip()
    return text.startswith(("2026-03-21T08:00:00", "2026-03-21 08:00"))


def _array(value: Any) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _answer_has(answer: str, value: str) -> bool:
    return value.replace(",", "").casefold() in answer.replace(",", "").casefold()


def _calls(state: ToolCallState, name: str) -> list[ToolCallRecord]:
    return [call for call in state.tool_calls if call.name == name]


def _first(state: ToolCallState, name: str) -> ToolCallRecord | None:
    calls = _calls(state, name)
    return calls[0] if calls else None


def _has(
    state: ToolCallState,
    name: str,
    predicate: Any | None = None,
) -> bool:
    return any(predicate(call) if predicate else True for call in _calls(state, name))


def _assistant_transcript(state: ToolCallState) -> str:
    return "\n".join(state.assistant_messages + [state.final_answer])


def _asks_for_clarification(text: str) -> bool:
    lowered = text.casefold()
    return "which" in lowered or "clarify" in lowered or "could you" in lowered


def _contains_refusal(text: str) -> bool:
    lowered = text.casefold()
    return any(
        term in lowered
        for term in ("cannot", "can't", "do not have", "don't have", "not able")
    ) or any(term in text for term in ("不能", "无法", "没有权限", "不具备"))


def _parse_math_expression(expression: str) -> float | None:
    sanitized = expression.replace(",", "").strip()
    if not re.fullmatch(r"[\d\s()+\-*/.%]+", sanitized):
        return None
    try:
        result = eval(sanitized, {"__builtins__": {}}, {})  # noqa: S307
    except Exception:
        return None
    return float(result) if isinstance(result, int | float) else None


def _generic_tool_fallback(call: ToolCallRecord) -> Json:
    if call.name == "calculator":
        result = _parse_math_expression(str(call.arguments.get("expression", "")))
        return {"error": "Invalid expression."} if result is None else {"result": result}
    if call.name == "web_search":
        return {"results": [{"snippet": f"Search results for {call.arguments.get('query', '')}"}]}
    if call.name == "run_code":
        return {"error": "Code execution is disabled in benchmark mocks."}
    return {"error": f"Tool {call.name} is not relevant for this scenario."}


def handle_tool_call(scenario_id: str, state: ToolCallState, call: ToolCallRecord) -> Json:
    if scenario_id == "TC-01":
        if call.name == "get_weather":
            return {
                "location": "Berlin",
                "temperature": 8,
                "units": "celsius",
                "condition": "Overcast",
                "humidity": 72,
            }
        if call.name == "web_search":
            return {"results": [{"snippet": "Berlin weather right now: 8C and overcast."}]}

    if scenario_id == "TC-02":
        if call.name == "get_stock_price":
            return {
                "ticker": "AAPL",
                "price": 187.42,
                "currency": "USD",
                "change": "+1.23",
                "change_percent": "+0.66%",
            }
        if call.name == "web_search":
            return {"results": [{"snippet": "AAPL is trading around $187.42."}]}

    if scenario_id == "TC-03":
        if call.name == "get_contacts":
            return {"results": [{"name": "Sarah Chen", "email": "sarah.chen@company.com"}]}
        if call.name == "send_email":
            return {"status": "sent", "message_id": "msg_8821"}

    if scenario_id == "TC-04" and call.name == "get_weather":
        if _norm(call.arguments.get("units")) == "fahrenheit":
            return {"location": "Tokyo", "temperature": 64, "units": "fahrenheit"}
        return {"location": "Tokyo", "temperature": 18, "units": "celsius"}

    if scenario_id == "TC-05":
        if call.name == "get_contacts":
            return {
                "results": [
                    {"name": "Alex Stone", "email": "alex.stone@company.com"},
                    {"name": "Jamie Liu", "email": "jamie.liu@company.com"},
                ]
            }
        if call.name == "create_calendar_event":
            return {"event_id": "evt_4412", "status": "created"}

    if scenario_id == "TC-06" and call.name == "translate_text":
        target = _norm(call.arguments.get("target_language"))
        if target == "spanish" or "西班牙" in target:
            return {"translated": "¿Dónde está el hospital más cercano?"}
        if target == "japanese" or "日语" in target or "日文" in target:
            return {"translated": "最寄りの病院はどこですか？"}
        return {"error": f"Unsupported target language {target}."}

    if scenario_id == "TC-07":
        if call.name == "search_files":
            return {"results": [{"file_id": "file_091", "name": "Q3_Budget_Report_2025.xlsx"}]}
        if call.name == "read_file":
            return {
                "content": (
                    "Department budgets: Engineering $2.1M, Marketing $800K, "
                    "Sales $1.5M. Total: $4.4M"
                )
            }
        if call.name == "get_contacts":
            return {
                "results": [
                    {
                        "name": "Jordan Park",
                        "email": "jordan.park@company.com",
                        "role": "manager",
                    }
                ]
            }
        if call.name == "send_email":
            return {"status": "sent"}

    if scenario_id == "TC-08":
        if call.name == "get_weather":
            return {"location": "Paris", "temperature": 11, "condition": "Light rain"}
        if call.name == "set_reminder":
            return {"reminder_id": "rem_553", "status": "set"}

    if scenario_id == "TC-09":
        if call.name == "get_weather":
            return {"location": "London", "temperature": 12, "condition": "Cloudy"}
        if call.name == "get_stock_price":
            return {"ticker": "MSFT", "price": 412.78, "currency": "USD"}
        if call.name == "web_search":
            return {"results": [{"snippet": "London is cloudy and MSFT is $412.78."}]}

    if scenario_id == "TC-13" and call.name == "search_files":
        query = _norm(call.arguments.get("query"))
        state.meta["search_attempts"] = int(state.meta.get("search_attempts", 0)) + 1
        if "johnson proposal" in query and state.meta["search_attempts"] == 1:
            return {"results": []}
        if "johnson" in query:
            return {"results": [{"file_id": "file_117", "name": "Johnson_Project_Proposal_v2.docx"}]}

    if scenario_id == "TC-14":
        if call.name == "get_stock_price":
            return {"error": "Service temporarily unavailable. Rate limit exceeded."}
        if call.name == "web_search":
            return {"results": [{"snippet": "Apple (AAPL) is trading around $187.42."}]}

    if scenario_id == "TC-15":
        if call.name == "web_search":
            return {
                "results": [
                    {"snippet": "Iceland has a population of approximately 372,520 as of 2025."}
                ]
            }
        if call.name == "calculator":
            return _generic_tool_fallback(call)

    return _generic_tool_fallback(call)


def evaluate_scenario(scenario_id: str, state: ToolCallState) -> Evaluation:
    answer = state.final_answer

    if scenario_id == "TC-01":
        used_weather = _has(
            state,
            "get_weather",
            lambda c: _contains_any(c.arguments.get("location"), "berlin", "柏林"),
        )
        used_web = _has(state, "web_search")
        if used_weather and not used_web and len(state.tool_calls) == 1:
            return Evaluation("pass", 2, "Used get_weather with Berlin only.")
        if used_web and not used_weather and all(c.name == "web_search" for c in state.tool_calls):
            return Evaluation("partial", 1, "Used web_search instead of the specialist weather tool.")
        return Evaluation("fail", 0, "Did not route the request cleanly to get_weather.")

    if scenario_id == "TC-02":
        stock = _has(state, "get_stock_price", lambda c: _norm(c.arguments.get("ticker")) == "aapl")
        web = _has(state, "web_search")
        if stock and not web and len(state.tool_calls) == 1:
            return Evaluation("pass", 2, "Used only get_stock_price for AAPL.")
        if stock and web:
            return Evaluation("partial", 1, "Used the right tool plus unnecessary web_search.")
        return Evaluation("fail", 0, "Did not isolate the request to get_stock_price.")

    if scenario_id == "TC-03":
        contact = _first(state, "get_contacts")
        email = _first(state, "send_email")
        if contact and email and contact.turn < email.turn:
            if _contains(contact.arguments.get("query"), "sarah") and _norm(
                email.arguments.get("to")
            ) == "sarah.chen@company.com":
                return Evaluation("pass", 2, "Looked up Sarah before sending the email.")
        if not contact and not email and "?" in answer and "email" in _norm(answer):
            return Evaluation("partial", 1, "Asked for Sarah's email instead of fabricating it.")
        return Evaluation("fail", 0, "Did not complete the contact lookup to email chain.")

    if scenario_id == "TC-04":
        weather = _first(state, "get_weather")
        if weather and _contains_any(weather.arguments.get("location"), "tokyo", "东京"):
            if _norm(weather.arguments.get("units")) == "fahrenheit":
                return Evaluation("pass", 2, "Requested Tokyo weather in Fahrenheit.")
            if not weather.arguments.get("units") and ("fahrenheit" in _norm(answer) or "64" in answer):
                return Evaluation("partial", 1, "Omitted units but converted manually.")
        return Evaluation("fail", 0, "Did not preserve the Fahrenheit instruction.")

    if scenario_id == "TC-05":
        event = _first(state, "create_calendar_event")
        if not event:
            return Evaluation("fail", 0, "Did not create the calendar event.")
        attendees = _array(event.arguments.get("attendees"))
        has_attendees = any(_contains(item, "alex") for item in attendees) and any(
            _contains(item, "jamie") for item in attendees
        )
        date_ok = event.arguments.get("date") == "2026-03-23"
        time_ok = event.arguments.get("time") == "09:30"
        duration_ok = event.arguments.get("duration_minutes") == 30
        if date_ok and time_ok and duration_ok and has_attendees:
            return Evaluation("pass", 2, "Parsed the relative date and meeting structure.")
        if date_ok and time_ok:
            return Evaluation("partial", 1, "Date and time are right, optional structure is incomplete.")
        return Evaluation("fail", 0, "Relative date or time parsing was incorrect.")

    if scenario_id == "TC-06":
        calls = _calls(state, "translate_text")
        has_spanish = any(
            (
                _norm(call.arguments.get("source_language")) == "english"
                or "英语" in _norm(call.arguments.get("source_language"))
            )
            and (
                _norm(call.arguments.get("target_language")) == "spanish"
                or "西班牙" in _norm(call.arguments.get("target_language"))
            )
            and call.arguments.get("text") == "Where is the nearest hospital?"
            for call in calls
        )
        has_japanese = any(
            (
                _norm(call.arguments.get("source_language")) == "english"
                or "英语" in _norm(call.arguments.get("source_language"))
            )
            and (
                _norm(call.arguments.get("target_language")) == "japanese"
                or "日语" in _norm(call.arguments.get("target_language"))
                or "日文" in _norm(call.arguments.get("target_language"))
            )
            and call.arguments.get("text") == "Where is the nearest hospital?"
            for call in calls
        )
        bundled = any(
            "spanish" in _norm(call.arguments.get("target_language"))
            and "japanese" in _norm(call.arguments.get("target_language"))
            for call in calls
        )
        if len(calls) >= 2 and has_spanish and has_japanese and not bundled:
            return Evaluation("pass", 2, "Issued separate translation calls for both languages.")
        return Evaluation("fail", 0, "Did not split the translation request into two valid calls.")

    if scenario_id == "TC-07":
        completed = 0
        completed += int(
            _has(
                state,
                "search_files",
                lambda c: _contains_any(c.arguments.get("query"), "q3 budget", "q3", "预算"),
            )
        )
        completed += int(_has(state, "read_file", lambda c: c.arguments.get("file_id") == "file_091"))
        completed += int(
            _has(
                state,
                "get_contacts",
                lambda c: _contains_any(c.arguments.get("query"), "manager", "经理"),
            )
        )
        completed += int(
            _has(
                state,
                "send_email",
                lambda c: _norm(c.arguments.get("to")) == "jordan.park@company.com"
                and _contains(c.arguments.get("body"), "4.4m"),
            )
        )
        if completed == 4:
            return Evaluation("pass", 2, "Completed the full four-step chain.")
        if completed >= 3:
            return Evaluation("partial", 1, "Completed most of the chain.")
        return Evaluation("fail", 0, "Did not carry file/contact data across the chain.")

    if scenario_id == "TC-08":
        weather = _first(state, "get_weather")
        reminder = _first(state, "set_reminder")
        if weather and reminder and weather.turn < reminder.turn:
            if _contains_any(
                reminder.arguments.get("message"), "umbrella", "伞"
            ) and _is_march_21_8am(reminder.arguments.get("datetime")):
                return Evaluation("pass", 2, "Checked weather first, then set the reminder.")
        if weather and not reminder and _asks_for_clarification(answer):
            return Evaluation("partial", 1, "Checked weather but stopped short of setting reminder.")
        return Evaluation("fail", 0, "Did not respect the weather-first conditional flow.")

    if scenario_id == "TC-09":
        weather = _has(
            state,
            "get_weather",
            lambda c: _contains_any(c.arguments.get("location"), "london", "伦敦"),
        )
        stock = _has(state, "get_stock_price", lambda c: _norm(c.arguments.get("ticker")) == "msft")
        if weather and stock:
            return Evaluation("pass", 2, "Handled both independent tasks.")
        if _has(state, "web_search"):
            return Evaluation("partial", 1, "Covered the request via web_search.")
        return Evaluation("fail", 0, "Missed one side of the two-part request.")

    if scenario_id == "TC-10":
        if not state.tool_calls and _answer_has(answer, "1945"):
            return Evaluation("pass", 2, "Answered directly without tools.")
        return Evaluation("fail", 0, "Used tools or missed the basic fact.")

    if scenario_id == "TC-11":
        correct = _answer_has(answer, "30")
        if not state.tool_calls and correct:
            return Evaluation("pass", 2, "Answered easy arithmetic directly.")
        if _has(state, "calculator") and correct and not _has(state, "web_search"):
            return Evaluation("partial", 1, "Used calculator correctly but unnecessarily.")
        return Evaluation("fail", 0, "Failed easy-arithmetic restraint.")

    if scenario_id == "TC-12":
        if (
            not state.tool_calls
            and _contains_refusal(answer)
            and _contains_any(answer, "delete", "删除")
        ):
            return Evaluation("pass", 2, "Refused because no delete-email tool exists.")
        return Evaluation("fail", 0, "Did not refuse the unsupported email deletion request.")

    if scenario_id == "TC-13":
        searches = _calls(state, "search_files")
        if len(searches) >= 2:
            return Evaluation("pass", 2, "Recovered after the empty result.")
        if len(searches) == 1 and _asks_for_clarification(answer):
            return Evaluation("pass", 2, "Asked for clarification after the empty result.")
        return Evaluation("fail", 0, "Did not adapt after the empty search response.")

    if scenario_id == "TC-14":
        stock_calls = _calls(state, "get_stock_price")
        transcript = _assistant_transcript(state)
        acknowledged = bool(
            re.search(
                r"temporarily unavailable|rate limit|service|暂时不可用|限流|服务",
                transcript,
                re.I,
            )
        )
        retry_later = "try again" in _norm(transcript) or _contains_any(transcript, "稍后", "再试")
        if stock_calls and acknowledged and (_has(state, "web_search") or retry_later):
            return Evaluation("pass", 2, "Acknowledged the tool failure and handled it.")
        if stock_calls and _has(state, "web_search"):
            return Evaluation("partial", 1, "Recovered with web_search but did not surface the error.")
        return Evaluation("fail", 0, "Did not handle the stock tool error with integrity.")

    if scenario_id == "TC-15":
        search = _first(state, "web_search")
        calculator = _first(state, "calculator")
        if search and calculator:
            expression = str(calculator.arguments.get("expression", "")).replace(",", "")
            if _contains_any(search.arguments.get("query"), "iceland", "冰岛") and "372520" in expression:
                return Evaluation("pass", 2, "Used the searched value in calculator.")
        if search and not calculator and _answer_has(answer, "7450.4"):
            return Evaluation("partial", 1, "Computed the right answer after searching.")
        return Evaluation("fail", 0, "Did not preserve the exact searched value.")

    raise KeyError(f"unknown ToolCall-15 scenario {scenario_id}")


def _parse_arguments(raw: Any) -> Json:
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return {}
    try:
        parsed = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _message_from_choice(response: Json) -> Json:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("response has no choices[0]")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        raise ValueError("response choices[0].message is not an object")
    return message


def _assistant_content(message: Json) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            str(part.get("text", ""))
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return ""


def _numeric_usage(usage: Any) -> Json:
    if not isinstance(usage, dict):
        return {}
    result: Json = {}
    for key, value in usage.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            result[key] = value
    prompt_details = usage.get("prompt_tokens_details")
    if isinstance(prompt_details, dict):
        cached = prompt_details.get("cached_tokens")
        if isinstance(cached, int | float):
            result.setdefault("cached_tokens", cached)
    return result


def _add_usage_totals(total: Json, usage: Json) -> None:
    for key, value in usage.items():
        if isinstance(value, int | float):
            total[key] = total.get(key, 0) + value


def run_scenario(
    base_url: str,
    model: str,
    scenario: Scenario,
    *,
    temperature: float,
    timeout: float,
    max_turns: int,
    headers: dict[str, str] | None = None,
    extra_body: Json | None = None,
    preserve_reasoning_content: bool = True,
) -> Json:
    state = ToolCallState()
    messages: list[Json] = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{BENCHMARK_CONTEXT}"},
        {"role": "user", "content": scenario.user_message},
    ]
    trace: list[Json] = []
    usage_totals: Json = {}
    scenario_started = time.monotonic()

    for turn in range(1, max_turns + 1):
        request_started = time.monotonic()
        payload: Json = {
            "model": model,
            "messages": messages,
            "tools": universal_tools(),
            "tool_choice": "auto",
            "temperature": temperature,
            "max_tokens": 1024,
        }
        if extra_body:
            payload.update(extra_body)
        if headers:
            response = post_json(
                base_url,
                "/v1/chat/completions",
                payload,
                timeout,
                headers=headers,
            )
        else:
            response = post_json(
                base_url,
                "/v1/chat/completions",
                payload,
                timeout,
            )
        elapsed_seconds = round(time.monotonic() - request_started, 6)
        usage = _numeric_usage(response.get("usage"))
        _add_usage_totals(usage_totals, usage)
        message = _message_from_choice(response)
        content = _assistant_content(message)
        tool_calls = message.get("tool_calls") or []
        if not isinstance(tool_calls, list):
            tool_calls = []
        state.assistant_messages.append(content)
        trace.append(
            {
                "turn": turn,
                "assistant": message,
                "elapsed_seconds": elapsed_seconds,
                "usage": usage,
            }
        )

        if not tool_calls:
            state.final_answer = content
            break

        assistant_message = {
            "role": "assistant",
            "content": content,
            "tool_calls": tool_calls,
        }
        if preserve_reasoning_content and "reasoning_content" in message:
            assistant_message["reasoning_content"] = message["reasoning_content"]
        messages.append(assistant_message)

        for index, raw_call in enumerate(tool_calls):
            if not isinstance(raw_call, dict):
                continue
            function = raw_call.get("function") if isinstance(raw_call.get("function"), dict) else {}
            call = ToolCallRecord(
                id=str(raw_call.get("id") or f"call_{turn}_{index}"),
                name=str(function.get("name") or "unknown_tool"),
                arguments=_parse_arguments(function.get("arguments")),
                turn=turn,
            )
            state.tool_calls.append(call)
            result = handle_tool_call(scenario.id, state, call)
            state.tool_results.append(
                ToolResultRecord(call_id=call.id, name=call.name, result=result)
            )
            trace.append({"turn": turn, "tool": call.name, "arguments": call.arguments, "result": result})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    evaluation = evaluate_scenario(scenario.id, state)
    return {
        "id": scenario.id,
        "title": scenario.title,
        "category": scenario.category,
        "status": evaluation.status,
        "points": evaluation.points,
        "summary": evaluation.summary,
        "note": evaluation.note,
        "tool_calls": [
            {
                "id": call.id,
                "name": call.name,
                "arguments": call.arguments,
                "turn": call.turn,
            }
            for call in state.tool_calls
        ],
        "final_answer": state.final_answer,
        "elapsed_seconds": round(time.monotonic() - scenario_started, 6),
        "usage_totals": usage_totals,
        "trace": trace,
    }


def run_suite(
    base_url: str,
    model: str,
    *,
    scenario_ids: list[str] | None = None,
    scenario_set: str = "en",
    temperature: float = 0.0,
    timeout: float = 120.0,
    max_turns: int = 8,
    headers: dict[str, str] | None = None,
    extra_body: Json | None = None,
    preserve_reasoning_content: bool = True,
) -> list[Json]:
    available = localized_scenarios(scenario_set)
    by_id = {scenario.id: scenario for scenario in available}
    selected_ids = scenario_ids or [scenario.id for scenario in available]
    selected = []
    for scenario_id in selected_ids:
        if scenario_id not in by_id:
            raise KeyError(f"unknown ToolCall-15 scenario {scenario_id}")
        selected.append(by_id[scenario_id])
    rows: list[Json] = []
    for scenario in selected:
        try:
            rows.append(
                run_scenario(
                    base_url,
                    model,
                    scenario,
                    temperature=temperature,
                    timeout=timeout,
                    max_turns=max_turns,
                    headers=headers,
                    extra_body=extra_body,
                    preserve_reasoning_content=preserve_reasoning_content,
                )
            )
        except Exception as exc:
            rows.append(
                {
                    "id": scenario.id,
                    "title": scenario.title,
                    "category": scenario.category,
                    "status": "error",
                    "points": 0,
                    "summary": f"scenario failed: {exc!r}",
                    "note": None,
                    "tool_calls": [],
                    "final_answer": "",
                    "trace": [{"error": repr(exc)}],
                }
            )
    return rows
