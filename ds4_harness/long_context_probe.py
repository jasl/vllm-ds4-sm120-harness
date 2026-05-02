from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ds4_harness.checks import assistant_text
from ds4_harness.client import post_json, post_json_with_retries
from ds4_harness.generation import thinking_extra_body


Json = dict[str, Any]


DEFAULT_CASE_NAME = "kv_indexer_long_context"
DEFAULT_LINE_COUNT = 2400
DEFAULT_REQUIRED_TERMS = (
    "alpha-cobalt-17",
    "beta-quartz-29",
    "gamma-onyx-43",
)


@dataclass(frozen=True)
class LongContextPrompt:
    name: str
    text: str
    line_count: int
    required_terms: tuple[str, ...]

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def build_long_context_prompt(
    *,
    name: str = DEFAULT_CASE_NAME,
    line_count: int = DEFAULT_LINE_COUNT,
) -> LongContextPrompt:
    if line_count < 128:
        raise ValueError("line_count must be at least 128")

    required = DEFAULT_REQUIRED_TERMS
    first_line = 17
    middle_line = max(64, line_count // 2)
    last_line = line_count - 13
    sentinel_lines = {
        first_line: (
            f"CHECKPOINT_BEGIN: the first indexer validation code is {required[0]}."
        ),
        middle_line: (
            f"CHECKPOINT_MIDDLE: the middle indexer validation code is {required[1]}."
        ),
        last_line: (
            f"CHECKPOINT_END: the final indexer validation code is {required[2]}."
        ),
    }

    rows = [
        "You are validating long-context retrieval for DeepSeek V4.",
        "Read the full context. The final answer must use only facts found in it.",
        "Do not claim that the source article or context is missing.",
        "",
    ]
    for index in range(1, line_count + 1):
        if index in sentinel_lines:
            rows.append(f"Line {index:04d}: {sentinel_lines[index]}")
            continue
        rows.append(
            f"Line {index:04d}: subsystem={index % 17:02d}; "
            f"shard={index % 29:02d}; checksum={(index * 37) % 1009:04d}; "
            "stable filler for long-context cache-layout validation."
        )

    rows.extend(
        [
            "",
            "Final task:",
            "In one concise paragraph, list the first, middle, and final indexer "
            "validation codes from the context. Use the exact code strings.",
        ]
    )
    return LongContextPrompt(
        name=name,
        text="\n".join(rows),
        line_count=line_count,
        required_terms=required,
    )


def _usage_tokens(response: Json) -> Json:
    usage = response.get("usage")
    return usage if isinstance(usage, dict) else {}


def _prompt_excerpt(prompt: str) -> Json:
    lines = prompt.splitlines()
    return {
        "head": "\n".join(lines[:8]),
        "tail": "\n".join(lines[-8:]),
    }


def evaluate_long_context_response(
    response: Json,
    required_terms: tuple[str, ...] = DEFAULT_REQUIRED_TERMS,
) -> tuple[bool, str, list[str]]:
    text = assistant_text(response)
    lowered = text.lower()
    missing = [term for term in required_terms if term.lower() not in lowered]
    if missing:
        return False, "missing required terms: " + ", ".join(missing), missing
    if "没有提供" in text or ("missing" in lowered and "context" in lowered):
        return False, "response suggests the context was missing", []
    return True, "matched long-context sentinel terms", []


def run_long_context_probe(
    *,
    base_url: str,
    model: str,
    variant: str,
    case_name: str = DEFAULT_CASE_NAME,
    line_count: int = DEFAULT_LINE_COUNT,
    max_tokens: int = 128,
    temperature: float = 0.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    timeout: float = 1800.0,
    request_retries: int = 1,
    headers: dict[str, str] | None = None,
    extra_body: Json | None = None,
    post_func: Callable[..., Json] = post_json,
) -> Json:
    prompt = build_long_context_prompt(name=case_name, line_count=line_count)
    payload: Json = {
        "model": model,
        "messages": [{"role": "user", "content": prompt.text}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    payload.update(thinking_extra_body(thinking_mode))
    if extra_body:
        payload.update(extra_body)

    started = time.monotonic()
    try:
        response = post_json_with_retries(
            base_url,
            "/v1/chat/completions",
            payload,
            timeout,
            headers=headers,
            request_retries=request_retries,
            post_func=post_func,
        )
        ok, detail, missing = evaluate_long_context_response(response)
    except Exception as exc:
        response = {"error": repr(exc)}
        ok = False
        detail = f"request failed: {exc!r}"
        missing = list(prompt.required_terms)
    elapsed_seconds = time.monotonic() - started
    usage = _usage_tokens(response)
    request_shape = {
        key: value
        for key, value in payload.items()
        if key not in {"messages"}
    }
    return {
        "case": prompt.name,
        "variant": variant,
        "model": model,
        "ok": ok,
        "detail": detail,
        "missing_terms": missing,
        "required_terms": list(prompt.required_terms),
        "elapsed_seconds": elapsed_seconds,
        "usage": usage,
        "assistant_text": assistant_text(response),
        "finish_reason": _finish_reason(response),
        "thinking_mode": thinking_mode,
        "thinking_strength": _thinking_strength(thinking_mode),
        "temperature": temperature,
        "top_p": top_p,
        "prompt": {
            "generator": "ds4_harness.long_context_probe.build_long_context_prompt",
            "line_count": prompt.line_count,
            "sha256": prompt.sha256,
            "excerpt": _prompt_excerpt(prompt.text),
        },
        "request_shape": request_shape,
        "response": response,
    }


def _finish_reason(response: Json) -> str | None:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    choice = choices[0]
    if not isinstance(choice, dict):
        return None
    reason = choice.get("finish_reason")
    return str(reason) if reason is not None else None


def _thinking_strength(thinking_mode: str) -> str:
    if thinking_mode == "non-thinking":
        return "disabled"
    if thinking_mode == "think-high":
        return "high"
    if thinking_mode == "think-max":
        return "max"
    return thinking_mode


def write_long_context_markdown(path: Path, row: Json) -> None:
    usage = row.get("usage") if isinstance(row.get("usage"), dict) else {}
    prompt = row.get("prompt") if isinstance(row.get("prompt"), dict) else {}
    excerpt = prompt.get("excerpt") if isinstance(prompt.get("excerpt"), dict) else {}
    lines = [
        "# Long Context Probe",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Detail: {row.get('detail')}",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Model: `{row.get('model')}`",
        f"- Thinking mode: `{row.get('thinking_mode')}`",
        f"- Thinking strength: `{row.get('thinking_strength')}`",
        f"- Temperature: `{row.get('temperature')}`",
        f"- Top P: `{row.get('top_p')}`",
        f"- Prompt lines: `{prompt.get('line_count')}`",
        f"- Prompt SHA256: `{prompt.get('sha256')}`",
        f"- Prompt tokens: `{usage.get('prompt_tokens', 'n/a')}`",
        f"- Completion tokens: `{usage.get('completion_tokens', 'n/a')}`",
        f"- Total tokens: `{usage.get('total_tokens', 'n/a')}`",
        f"- Finish reason: `{row.get('finish_reason')}`",
        f"- Required terms: `{', '.join(row.get('required_terms', []))}`",
        "",
        "## Assistant",
        "",
        str(row.get("assistant_text") or "").rstrip() or "<empty>",
        "",
        "## Prompt Excerpt",
        "",
        "### Head",
        "",
        "```text",
        str(excerpt.get("head") or "").rstrip(),
        "```",
        "",
        "### Tail",
        "",
        "```text",
        str(excerpt.get("tail") or "").rstrip(),
        "```",
        "",
        "## Usage JSON",
        "",
        "```json",
        json.dumps(usage, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
