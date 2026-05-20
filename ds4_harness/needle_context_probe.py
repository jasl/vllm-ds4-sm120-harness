from __future__ import annotations

import hashlib
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ds4_harness.checks import assistant_text
from ds4_harness.generation import thinking_extra_body
from ds4_harness.prefix_cache_probe import stream_chat_completion


Json = dict[str, Any]
StreamFunc = Callable[..., Json]

DEFAULT_CASE_NAME = "needle_position_matrix"
DEFAULT_LINE_COUNTS = (4000,)
DEFAULT_POSITIONS = (0, 7, 14, 21, 28, 35, 42, 50, 57, 64, 71, 78, 85, 92, 100)
DEFAULT_MAX_TOKENS = 64
DEFAULT_NEEDLE_ANSWER = "Virtual Rocket Band"


@dataclass(frozen=True)
class NeedleContextPrompt:
    name: str
    text: str
    line_count: int
    position_percent: int
    needle_line: int
    required_answer: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _needle_line(line_count: int, position_percent: int) -> int:
    if not 0 <= position_percent <= 100:
        raise ValueError("positions must be between 0 and 100")
    if position_percent == 0:
        return 1
    if position_percent == 100:
        return line_count
    return max(1, min(line_count, round(1 + (line_count - 1) * position_percent / 100)))


def _prompt_excerpt(prompt: str) -> Json:
    lines = prompt.splitlines()
    return {
        "head": "\n".join(lines[:8]),
        "tail": "\n".join(lines[-8:]),
    }


def build_needle_context_prompt(
    *,
    line_count: int,
    position_percent: int,
    answer: str = DEFAULT_NEEDLE_ANSWER,
    case_name: str = DEFAULT_CASE_NAME,
) -> NeedleContextPrompt:
    if line_count < 128:
        raise ValueError("line_count must be at least 128")
    if not answer.strip():
        raise ValueError("answer must not be empty")

    needle_line = _needle_line(line_count, position_percent)
    rows = [
        "You are solving a needle-in-a-haystack retrieval task.",
        "Use only facts found in the provided context.",
        "Do not say the context is missing if the answer appears in it.",
        "",
    ]
    for index in range(1, line_count + 1):
        if index == needle_line:
            rows.append(
                f"Line {index:04d}: The first band to perform on the Moon was "
                f"the {answer}."
            )
            continue
        rows.append(
            f"Line {index:04d}: archive={index % 31:02d}; "
            f"section={index % 47:02d}; checksum={(index * 131) % 9973:04d}; "
            "stable filler for long-context needle retrieval."
        )

    rows.extend(
        [
            "",
            "Question: Which band was the first to perform on the Moon?",
            "Please answer in the format "
            "'The first band to perform on the Moon was________.'",
            "Do not give information outside the context or repeat your findings.",
        ]
    )
    return NeedleContextPrompt(
        name=f"{case_name}_{line_count}_lines_pos{position_percent}",
        text="\n".join(rows),
        line_count=line_count,
        position_percent=position_percent,
        needle_line=needle_line,
        required_answer=answer,
    )


def _finish_reason(response: Json) -> str | None:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    choice = choices[0]
    if not isinstance(choice, dict):
        return None
    reason = choice.get("finish_reason")
    return str(reason) if reason is not None else None


def _usage_tokens(response: Json) -> Json:
    usage = response.get("usage")
    return usage if isinstance(usage, dict) else {}


def _assistant_text_artifact(text: str) -> Json:
    return {
        "assistant_text_sha256": _sha256(text),
        "assistant_text_length": len(text),
        "assistant_text_excerpt": text[:512],
    }


def _request_ok(text: str, answer: str) -> tuple[bool, str]:
    if answer.lower() not in text.lower():
        return False, f"missing answer: {answer}"
    lowered = text.lower()
    if "context does not contain" in lowered or (
        "missing" in lowered and "context" in lowered
    ):
        return False, "response claims the context is missing"
    return True, "matched needle answer"


def _build_payload(
    prompt: NeedleContextPrompt,
    *,
    model: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
    thinking_mode: str,
    extra_body: Json | None,
) -> Json:
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
    return payload


def _run_request(
    *,
    base_url: str,
    model: str,
    variant: str,
    case_name: str,
    prompt: NeedleContextPrompt,
    repeat_index: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    thinking_mode: str,
    timeout: float,
    headers: dict[str, str] | None,
    extra_body: Json | None,
    stream_func: StreamFunc,
) -> Json:
    payload = _build_payload(
        prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        thinking_mode=thinking_mode,
        extra_body=extra_body,
    )
    started = time.monotonic()
    metadata = {
        "case": case_name,
        "variant": variant,
        "line_count": prompt.line_count,
        "position_percent": prompt.position_percent,
        "needle_line": prompt.needle_line,
        "repeat": repeat_index,
    }
    try:
        result = stream_func(
            base_url,
            "/v1/chat/completions",
            payload,
            timeout,
            headers=headers,
            probe_metadata=metadata,
        )
        response = result.get("response") if isinstance(result.get("response"), dict) else {}
        text = str(result.get("assistant_text") or assistant_text(response))
        ok, detail = _request_ok(text, prompt.required_answer)
        usage = _usage_tokens(response)
        elapsed = result.get("elapsed_seconds")
        if not isinstance(elapsed, int | float):
            elapsed = time.monotonic() - started
        row = {
            "case": case_name,
            "variant": variant,
            "line_count": prompt.line_count,
            "position_percent": prompt.position_percent,
            "needle_line": prompt.needle_line,
            "repeat": repeat_index,
            "ok": ok,
            "detail": detail,
            "ttft_seconds": result.get("ttft_seconds"),
            "elapsed_seconds": round(float(elapsed), 6),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "chunks": result.get("chunks"),
            "finish_reason": _finish_reason(response),
            "response_id": response.get("id") if response.get("id") else None,
            "prompt_sha256": prompt.sha256,
            "required_answer": prompt.required_answer,
        }
        row.update(_assistant_text_artifact(text))
        return row
    except Exception as exc:
        return {
            "case": case_name,
            "variant": variant,
            "line_count": prompt.line_count,
            "position_percent": prompt.position_percent,
            "needle_line": prompt.needle_line,
            "repeat": repeat_index,
            "ok": False,
            "detail": f"request failed: {exc!r}",
            "ttft_seconds": None,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "chunks": 0,
            "finish_reason": None,
            "prompt_sha256": prompt.sha256,
            "required_answer": prompt.required_answer,
        }


def _as_float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _numeric_values(rows: list[Json], key: str) -> list[float]:
    values = []
    for row in rows:
        value = _as_float(row.get(key))
        if value is not None:
            values.append(value)
    return values


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(statistics.fmean(values), 6)


def _max(values: list[float]) -> float | None:
    if not values:
        return None
    return round(max(values), 6)


def _summarize_requests(rows: list[Json]) -> Json:
    ttft = _numeric_values(rows, "ttft_seconds")
    elapsed = _numeric_values(rows, "elapsed_seconds")
    prompt_tokens = _numeric_values(rows, "prompt_tokens")
    return {
        "request_count": len(rows),
        "failure_count": sum(0 if row.get("ok") else 1 for row in rows),
        "line_counts": sorted({int(row["line_count"]) for row in rows}),
        "positions": sorted({int(row["position_percent"]) for row in rows}),
        "max_ttft_seconds": _max(ttft),
        "avg_ttft_seconds": _mean(ttft),
        "max_elapsed_seconds": _max(elapsed),
        "avg_elapsed_seconds": _mean(elapsed),
        "max_prompt_tokens": _max(prompt_tokens),
        "avg_prompt_tokens": _mean(prompt_tokens),
    }


def run_needle_position_matrix(
    *,
    base_url: str,
    model: str,
    variant: str,
    case_name: str = DEFAULT_CASE_NAME,
    line_counts: list[int] | None = None,
    positions: list[int] | None = None,
    repeat_count: int = 1,
    answer: str = DEFAULT_NEEDLE_ANSWER,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    timeout: float = 3600.0,
    headers: dict[str, str] | None = None,
    extra_body: Json | None = None,
    stream_func: StreamFunc = stream_chat_completion,
) -> Json:
    line_counts = list(DEFAULT_LINE_COUNTS) if line_counts is None else list(line_counts)
    positions = list(DEFAULT_POSITIONS) if positions is None else list(positions)
    if repeat_count < 1:
        raise ValueError("repeat_count must be >= 1")
    if any(value < 128 for value in line_counts):
        raise ValueError("line counts must be at least 128")
    if not line_counts:
        raise ValueError("at least one line count is required")
    if not positions:
        raise ValueError("at least one needle position is required")

    rows: list[Json] = []
    prompt_manifests: list[Json] = []
    for line_count in line_counts:
        for position_percent in positions:
            prompt = build_needle_context_prompt(
                line_count=line_count,
                position_percent=position_percent,
                answer=answer,
                case_name=case_name,
            )
            prompt_manifests.append(
                {
                    "name": prompt.name,
                    "line_count": prompt.line_count,
                    "position_percent": prompt.position_percent,
                    "needle_line": prompt.needle_line,
                    "sha256": prompt.sha256,
                    "required_answer": prompt.required_answer,
                    "excerpt": _prompt_excerpt(prompt.text),
                }
            )
            for repeat_index in range(1, repeat_count + 1):
                rows.append(
                    _run_request(
                        base_url=base_url,
                        model=model,
                        variant=variant,
                        case_name=case_name,
                        prompt=prompt,
                        repeat_index=repeat_index,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        thinking_mode=thinking_mode,
                        timeout=timeout,
                        headers=headers,
                        extra_body=extra_body,
                        stream_func=stream_func,
                    )
                )

    summary = _summarize_requests(rows)
    return {
        "case": case_name,
        "variant": variant,
        "model": model,
        "ok": summary["failure_count"] == 0,
        "thinking_mode": thinking_mode,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "repeat_count": repeat_count,
        "required_answer": answer,
        "summary": summary,
        "prompts": prompt_manifests,
        "requests": rows,
    }


def _fmt(value: Any, digits: int = 3) -> str:
    if not isinstance(value, int | float):
        return "n/a"
    return f"{float(value):.{digits}f}"


def write_needle_position_matrix_markdown(path: Path, row: Json) -> None:
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    lines = [
        "# Needle Position Matrix",
        "",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Model: `{row.get('model')}`",
        f"- Status: {'PASS' if row.get('ok') else 'FAIL'}",
        f"- Requests: `{summary.get('request_count', 'n/a')}`",
        f"- Failures: `{summary.get('failure_count', 'n/a')}`",
        f"- Positions: `{summary.get('positions', [])}`",
        "",
        "| Line count | Position % | Needle line | OK | TTFT s | Elapsed s | Prompt tokens | Detail |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for request in row.get("requests", []):
        lines.append(
            "| {line_count} | {position} | {needle_line} | {ok} | {ttft} | "
            "{elapsed} | {prompt_tokens} | {detail} |".format(
                line_count=request.get("line_count"),
                position=request.get("position_percent"),
                needle_line=request.get("needle_line"),
                ok="yes" if request.get("ok") else "no",
                ttft=_fmt(request.get("ttft_seconds")),
                elapsed=_fmt(request.get("elapsed_seconds")),
                prompt_tokens=request.get("prompt_tokens", "n/a"),
                detail=str(request.get("detail", "")).replace("|", "\\|"),
            )
        )
    lines.extend(
        [
            "",
            "This gate is a synthetic NIAH-style correctness probe. Use public "
            "Inspect Evals NIAH runs for broader dataset evidence; use this "
            "matrix for stable local tail-position regressions.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
