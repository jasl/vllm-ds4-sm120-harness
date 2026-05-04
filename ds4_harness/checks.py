from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Expectation:
    all_terms: tuple[str, ...] = ()
    any_terms: tuple[str, ...] = ()
    any_term_groups: tuple[tuple[str, ...], ...] = ()
    forbidden_terms: tuple[str, ...] = ()
    min_chars: int = 0
    require_html_artifact: bool = False
    tool_name: str | None = None
    finish_reason: str | None = None


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    detail: str


def assistant_message(response: dict[str, Any]) -> dict[str, Any]:
    choices = response.get("choices")
    choice = choices[0] if isinstance(choices, list) and choices else {}
    message = choice.get("message")
    if isinstance(message, dict):
        return message
    return {"content": choice.get("text") or ""}


def assistant_text(response: dict[str, Any]) -> str:
    content = assistant_message(response).get("content")
    return content if isinstance(content, str) else ""


def tool_call_names(response: dict[str, Any]) -> list[str]:
    names: list[str] = []
    tool_calls = assistant_message(response).get("tool_calls") or []
    for call in tool_calls:
        if not isinstance(call, dict):
            continue
        function = call.get("function") or {}
        if isinstance(function, dict) and isinstance(function.get("name"), str):
            names.append(function["name"])
    return names


def _has_html_artifact(text: str) -> bool:
    lowered = text.casefold()
    has_root = "<html" in lowered or "<!doctype html" in lowered
    has_style = "<style" in lowered or "style=" in lowered
    has_runtime = "<script" in lowered or "canvas" in lowered
    has_closed_document = "</body>" in lowered and "</html>" in lowered
    has_closed_style = "<style" not in lowered or "</style>" in lowered
    has_closed_script = "<script" not in lowered or "</script>" in lowered
    return (
        has_root
        and has_style
        and has_runtime
        and has_closed_document
        and has_closed_style
        and has_closed_script
    )


def check_chat_response(
    expectation: Expectation,
    response: dict[str, Any],
) -> CheckResult:
    choices = response.get("choices")
    choice = choices[0] if isinstance(choices, list) and choices else {}
    text = assistant_text(response)
    lowered = text.casefold()

    if expectation.finish_reason is not None:
        finish_reason = choice.get("finish_reason")
        if finish_reason != expectation.finish_reason:
            return CheckResult(
                False,
                f"finish_reason={finish_reason!r}, expected {expectation.finish_reason!r}",
            )

    if expectation.tool_name is not None:
        names = tool_call_names(response)
        if expectation.tool_name not in names:
            return CheckResult(
                False,
                f"missing tool call {expectation.tool_name!r}; got {names!r}",
            )

    missing = [term for term in expectation.all_terms if term.casefold() not in lowered]
    if missing:
        return CheckResult(False, f"missing required terms: {', '.join(missing)}")

    if expectation.any_terms and not any(
        term.casefold() in lowered for term in expectation.any_terms
    ):
        return CheckResult(
            False,
            "missing any expected term: " + ", ".join(expectation.any_terms),
        )

    for term_group in expectation.any_term_groups:
        if term_group and not any(term.casefold() in lowered for term in term_group):
            return CheckResult(
                False,
                "missing any expected term group: " + ", ".join(term_group),
            )

    forbidden = [
        term for term in expectation.forbidden_terms if term.casefold() in lowered
    ]
    if forbidden:
        return CheckResult(False, f"found forbidden terms: {', '.join(forbidden)}")

    if len(text) < expectation.min_chars:
        return CheckResult(
            False,
            f"response too short: {len(text)} chars, expected >= {expectation.min_chars}",
        )

    if expectation.require_html_artifact and not _has_html_artifact(text):
        return CheckResult(False, "missing complete HTML artifact")

    return CheckResult(True, "matched expectation")
