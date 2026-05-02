from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ds4_harness.checks import (
    CheckResult,
    Expectation,
    assistant_message,
    assistant_text,
    check_chat_response,
    tool_call_names,
)


Json = dict[str, Any]

THINKING_MODE_EXTRA_BODY: dict[str, Json] = {
    "non-thinking": {"thinking": {"type": "disabled"}},
    "think-high": {"thinking": {"type": "enabled"}, "reasoning_effort": "high"},
    "think-max": {"thinking": {"type": "enabled"}, "reasoning_effort": "max"},
}

DEFAULT_THINKING_MODES = tuple(THINKING_MODE_EXTRA_BODY)


@dataclass(frozen=True)
class GenerationPrompt:
    name: str
    language: str
    path: Path
    prompt: str
    tags: tuple[str, ...]
    expectation: Expectation
    max_tokens: int | None = None
    temperature: float | None = None

    @property
    def workload(self) -> str:
        normalized = {tag.casefold() for tag in self.tags}
        if "translation" in normalized:
            return "translation"
        if "writing" in normalized:
            return "writing"
        if "coding" in normalized:
            return "coding"
        return "generation"

    def to_payload(
        self,
        *,
        model: str,
        default_max_tokens: int,
        default_temperature: float,
        max_case_tokens: int | None = None,
    ) -> Json:
        max_tokens = self.max_tokens or default_max_tokens
        if max_case_tokens is not None and max_tokens > max_case_tokens:
            max_tokens = max_case_tokens
        return {
            "model": model,
            "messages": [{"role": "user", "content": self.prompt}],
            "max_tokens": max_tokens,
            "temperature": (
                self.temperature
                if self.temperature is not None
                else default_temperature
            ),
        }


def thinking_extra_body(mode: str) -> Json:
    try:
        return json.loads(json.dumps(THINKING_MODE_EXTRA_BODY[mode]))
    except KeyError as exc:
        raise KeyError(f"unknown thinking mode {mode!r}") from exc


def _split_front_matter(text: str) -> tuple[Json, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text.strip()

    metadata_lines: list[str] = []
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return _parse_metadata(metadata_lines), "\n".join(lines[index + 1 :]).strip()
        metadata_lines.append(line)
    return {}, text.strip()


def _parse_metadata(lines: list[str]) -> Json:
    metadata: Json = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, raw_value = stripped.split(":", 1)
        metadata[key.strip()] = raw_value.strip()
    return metadata


def _csv(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return tuple(item.strip() for item in str(value).split(",") if item.strip())


def _int_value(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(str(value))
    except ValueError:
        return None


def _float_value(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value))
    except ValueError:
        return None


def _bool_value(value: Any) -> bool:
    return str(value or "").strip().casefold() in {"1", "true", "yes", "on"}


def load_generation_prompts(
    prompt_root: Path,
    *,
    languages: list[str] | None = None,
    names: list[str] | None = None,
    tags: list[str] | None = None,
) -> list[GenerationPrompt]:
    selected_languages = set(languages or [])
    selected_names = set(names or [])
    selected_tags = {tag.casefold() for tag in tags or []}
    prompts: list[GenerationPrompt] = []

    for language_dir in sorted(path for path in prompt_root.iterdir() if path.is_dir()):
        language = language_dir.name
        if selected_languages and language not in selected_languages:
            continue
        for path in sorted(language_dir.glob("*.md")):
            name = path.stem
            if selected_names and name not in selected_names:
                continue
            metadata, prompt = _split_front_matter(
                path.read_text(encoding="utf-8")
            )
            prompt_tags = _csv(metadata.get("tags"))
            if selected_tags and not selected_tags.intersection(
                tag.casefold() for tag in prompt_tags
            ):
                continue
            expectation = Expectation(
                all_terms=_csv(metadata.get("all_terms")),
                any_terms=_csv(metadata.get("any_terms")),
                forbidden_terms=_csv(metadata.get("forbidden_terms")),
                min_chars=_int_value(metadata.get("min_chars")) or 0,
                require_html_artifact=_bool_value(
                    metadata.get("require_html_artifact")
                ),
            )
            prompts.append(
                GenerationPrompt(
                    name=name,
                    language=language,
                    path=path,
                    prompt=prompt,
                    tags=prompt_tags,
                    expectation=expectation,
                    max_tokens=_int_value(metadata.get("max_tokens")),
                    temperature=_float_value(metadata.get("temperature")),
                )
            )
    return prompts


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n\n".join(
            str(item.get("text", "")) if isinstance(item, dict) else str(item)
            for item in content
        ).strip()
    if content is None:
        return ""
    return json.dumps(content, ensure_ascii=False, indent=2)


def _fenced_block(text: str, language: str = "text") -> str:
    fence = "```"
    while fence in text:
        fence += "`"
    return f"{fence}{language}\n{text.rstrip()}\n{fence}"


def transcript_filename(
    prompt: GenerationPrompt,
    *,
    round_index: int,
    thinking_mode: str,
    variant: str,
) -> str:
    safe_variant = _safe_slug(variant)
    safe_mode = _safe_slug(thinking_mode)
    return f"{prompt.name}.{round_index}.{safe_mode}.{safe_variant}.md"


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    return slug.strip("-") or "unknown"


def generation_result_row(
    *,
    prompt: GenerationPrompt,
    round_index: int,
    thinking_mode: str,
    variant: str,
    payload: Json,
    response: Json,
    result: CheckResult,
    elapsed_seconds: float,
) -> Json:
    usage = response.get("usage") if isinstance(response, dict) else None
    choice = (
        response.get("choices", [{}])[0]
        if isinstance(response.get("choices"), list) and response.get("choices")
        else {}
    )
    return {
        "case": prompt.name,
        "language": prompt.language,
        "workload": prompt.workload,
        "tags": list(prompt.tags),
        "model": payload.get("model"),
        "round": round_index,
        "thinking_mode": thinking_mode,
        "thinking_strength": _thinking_strength(payload),
        "variant": variant,
        "ok": result.ok,
        "detail": result.detail,
        "elapsed_seconds": round(elapsed_seconds, 6),
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
        "usage": usage if isinstance(usage, dict) else {},
        "payload": payload,
        "response": response,
    }


def _thinking_strength(payload: Json) -> str:
    thinking = payload.get("thinking")
    if isinstance(thinking, dict) and thinking.get("type") == "disabled":
        return "disabled"
    effort = payload.get("reasoning_effort")
    return str(effort) if effort else "default"


def write_generation_transcript(path: Path, row: Json) -> None:
    prompt_text = ""
    payload = row.get("payload")
    if isinstance(payload, dict):
        messages = payload.get("messages")
        if isinstance(messages, list) and messages:
            first = messages[0]
            if isinstance(first, dict):
                prompt_text = _content_text(first.get("content"))

    response = row.get("response") if isinstance(row.get("response"), dict) else {}
    message = assistant_message(response)
    text = assistant_text(response)
    reasoning = message.get("reasoning_content")
    usage = row.get("usage") if isinstance(row.get("usage"), dict) else {}

    lines = [
        "# Generation Transcript",
        "",
        f"- Case: `{row.get('case')}`",
        f"- Language group: `{row.get('language')}`",
        f"- Workload: `{row.get('workload')}`",
        f"- Model: `{row.get('model')}`",
        f"- Round: `{row.get('round')}`",
        f"- Thinking mode: `{row.get('thinking_mode')}`",
        f"- Thinking strength: `{row.get('thinking_strength')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- OK: `{row.get('ok')}`",
        f"- Status: {'PASS' if row.get('ok') else 'FAIL'}",
        f"- Check: {row.get('detail')}",
        f"- Detail: `{row.get('detail')}`",
        f"- Elapsed seconds: {row.get('elapsed_seconds')}",
        f"- Finish reason: `{row.get('finish_reason')}`",
        f"- Usage: `{json.dumps(usage, ensure_ascii=False)}`",
        f"- Prompt tokens: {usage.get('prompt_tokens', 'n/a')}",
        f"- Completion tokens: {usage.get('completion_tokens', 'n/a')}",
        f"- Total tokens: {usage.get('total_tokens', 'n/a')}",
        "",
        "## Prompt",
        "",
        _fenced_block(prompt_text, "markdown"),
        "",
    ]
    if isinstance(reasoning, str) and reasoning:
        lines.extend(["## Reasoning Content", "", _fenced_block(reasoning), ""])
    if text:
        lines.extend(["## Assistant", "", _fenced_block(text, "markdown"), ""])
    names = tool_call_names(response)
    if names:
        lines.extend(["## Tool Calls", ""])
        lines.extend(f"- `{name}`" for name in names)
        lines.append("")
    if "error" in response:
        lines.extend(["## Error", "", _fenced_block(str(response["error"])), ""])

    path.parent.mkdir(parents=True, exist_ok=True)
    transcript = "\n".join(line.rstrip() for line in "\n".join(lines).splitlines())
    path.write_text(transcript.rstrip() + "\n", encoding="utf-8")


def evaluate_generation_response(
    prompt: GenerationPrompt,
    response: Json,
) -> CheckResult:
    return check_chat_response(prompt.expectation, response)
