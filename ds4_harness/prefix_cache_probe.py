from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from ds4_harness.checks import assistant_text
from ds4_harness.generation import thinking_extra_body


Json = dict[str, Any]
StreamFunc = Callable[..., Json]

DEFAULT_CASE_NAME = "prefix_cache_interleaved_long_conversation"
DEFAULT_LINE_COUNT = 2400
DEFAULT_MAX_TOKENS = 64
DEFAULT_REGRESSION_TTFT_RATIO = 3.0


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _session_name(session: str) -> str:
    value = session.strip().lower()
    if value not in {"a", "b"}:
        raise ValueError("session must be 'a' or 'b'")
    return value


def _session_required_term(session: str) -> str:
    return f"SESSION-{session.upper()}-CODE-17"


def _session_document(session: str, line_count: int) -> str:
    if line_count < 128:
        raise ValueError("line_count must be at least 128")

    session = _session_name(session)
    required = _session_required_term(session)
    middle = max(64, line_count // 2)
    last = line_count - 11
    rows = [
        f"Conversation session {session.upper()} reference packet.",
        "This packet is intentionally long and deterministic.",
        "Later requests in the same session share this exact prefix.",
        "",
    ]
    for index in range(1, line_count + 1):
        if index == 17:
            rows.append(
                f"Line {index:04d}: primary session validation term is {required}."
            )
            continue
        if index == middle:
            rows.append(
                f"Line {index:04d}: middle checkpoint for session {session.upper()}."
            )
            continue
        if index == last:
            rows.append(
                f"Line {index:04d}: final checkpoint for session {session.upper()}."
            )
            continue
        rows.append(
            f"Line {index:04d}: session={session.upper()}; "
            f"shard={index % 31:02d}; checksum={(index * 53) % 997:03d}; "
            "stable filler for prefix-cache reuse validation."
        )
    return "\n".join(rows)


def build_prefix_cache_request(
    *,
    session: str,
    turn: int,
    line_count: int = DEFAULT_LINE_COUNT,
    model: str = "model",
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    probe_label: str | None = None,
) -> Json:
    session = _session_name(session)
    if turn < 1:
        raise ValueError("turn must be >= 1")

    document = _session_document(session, line_count)
    required = _session_required_term(session)
    messages = [
        {
            "role": "system",
            "content": (
                "You are validating vLLM prefix-cache reuse. Answer with the "
                "exact session validation term and no extra prose."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Store this deterministic long context for session {session.upper()}.\n\n"
                f"{document}"
            ),
        },
        {
            "role": "assistant",
            "content": (
                f"Session {session.upper()} context received. "
                f"The validation term is {required}."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Turn {turn}: return only the exact validation term for "
                f"session {session.upper()}."
            ),
        },
    ]
    payload: Json = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    payload.update(thinking_extra_body(thinking_mode))
    prefix_json = json.dumps(messages[:-1], ensure_ascii=False, sort_keys=True)
    return {
        "payload": payload,
        "session": session,
        "turn": turn,
        "probe_label": probe_label or f"{session}_turn_{turn}",
        "required_terms": [required],
        "line_count": line_count,
        "prompt_sha256": _sha256(prefix_json),
    }


def _content_from_delta(delta: Json) -> str:
    parts = []
    for key in ("content", "reasoning_content"):
        value = delta.get(key)
        if isinstance(value, str) and value:
            parts.append(value)
    tool_calls = delta.get("tool_calls")
    if isinstance(tool_calls, list) and tool_calls:
        parts.append(json.dumps(tool_calls, ensure_ascii=False))
    return "".join(parts)


def stream_chat_completion(
    base_url: str,
    path: str,
    payload: Json,
    timeout: float,
    *,
    headers: dict[str, str] | None = None,
    probe_metadata: Json | None = None,
) -> Json:
    del probe_metadata
    url = base_url.rstrip("/") + path
    request_payload = dict(payload)
    request_payload["stream"] = True
    request_payload.setdefault("stream_options", {"include_usage": True})
    encoded = json.dumps(request_payload).encode("utf-8")
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(
        url,
        data=encoded,
        headers=request_headers,
        method="POST",
    )

    started = time.monotonic()
    first_token_at: float | None = None
    text_parts: list[str] = []
    usage: Json = {}
    finish_reason: str | None = None
    chunks = 0
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line or not line.startswith("data:"):
                    continue
                data = line.removeprefix("data:").strip()
                if data == "[DONE]":
                    break
                event = json.loads(data)
                if not isinstance(event, dict):
                    continue
                event_usage = event.get("usage")
                if isinstance(event_usage, dict):
                    usage = event_usage
                choices = event.get("choices")
                if not isinstance(choices, list) or not choices:
                    continue
                choice = choices[0]
                if not isinstance(choice, dict):
                    continue
                reason = choice.get("finish_reason")
                if reason is not None:
                    finish_reason = str(reason)
                delta = choice.get("delta")
                if not isinstance(delta, dict):
                    continue
                piece = _content_from_delta(delta)
                if not piece:
                    continue
                chunks += 1
                if first_token_at is None:
                    first_token_at = time.monotonic()
                text_parts.append(piece)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{url} returned HTTP {exc.code}: {body}") from exc

    elapsed = time.monotonic() - started
    assistant = "".join(text_parts)
    response_json: Json = {
        "choices": [
            {
                "message": {"role": "assistant", "content": assistant},
                "finish_reason": finish_reason,
            }
        ],
        "usage": usage,
    }
    return {
        "response": response_json,
        "assistant_text": assistant,
        "ttft_seconds": None
        if first_token_at is None
        else round(first_token_at - started, 6),
        "elapsed_seconds": round(elapsed, 6),
        "chunks": chunks,
    }


def _stream_with_retries(
    stream_func: StreamFunc,
    base_url: str,
    path: str,
    payload: Json,
    timeout: float,
    *,
    headers: dict[str, str] | None,
    request_retries: int,
    probe_metadata: Json,
) -> Json:
    attempts = max(0, request_retries) + 1
    last_exc: Exception | None = None
    for _ in range(attempts):
        try:
            return stream_func(
                base_url,
                path,
                payload,
                timeout,
                headers=headers,
                probe_metadata=probe_metadata,
            )
        except Exception as exc:
            last_exc = exc
    assert last_exc is not None
    if attempts > 1:
        raise RuntimeError(f"request failed after {attempts} attempts: {last_exc!r}")
    raise last_exc


def _usage_tokens(response: Json) -> Json:
    usage = response.get("usage")
    return usage if isinstance(usage, dict) else {}


def _cached_prompt_tokens(usage: Json) -> int | None:
    details = usage.get("prompt_tokens_details")
    if not isinstance(details, dict):
        return None
    value = details.get("cached_tokens")
    try:
        return None if value is None else int(value)
    except (TypeError, ValueError):
        return None


def _request_ok(text: str, required_terms: list[str]) -> tuple[bool, str]:
    lowered = text.lower()
    missing = [term for term in required_terms if term.lower() not in lowered]
    if missing:
        return False, "missing required terms: " + ", ".join(missing)
    return True, "matched required session term"


def _run_request(
    request: Json,
    *,
    base_url: str,
    timeout: float,
    headers: dict[str, str] | None,
    request_retries: int,
    stream_func: StreamFunc,
    concurrent_group: str | None = None,
) -> Json:
    started = time.monotonic()
    phase = str(request["probe_label"])
    try:
        result = _stream_with_retries(
            stream_func,
            base_url,
            "/v1/chat/completions",
            request["payload"],
            timeout,
            headers=headers,
            request_retries=request_retries,
            probe_metadata={
                "probe_label": phase,
                "session": request["session"],
                "turn": request["turn"],
            },
        )
        response = result.get("response") if isinstance(result.get("response"), dict) else {}
        text = str(result.get("assistant_text") or assistant_text(response))
        ok, detail = _request_ok(text, list(request["required_terms"]))
        usage = _usage_tokens(response)
        elapsed = result.get("elapsed_seconds")
        if not isinstance(elapsed, int | float):
            elapsed = time.monotonic() - started
        return {
            "phase": phase,
            "session": request["session"],
            "turn": request["turn"],
            "concurrent_group": concurrent_group,
            "ok": ok,
            "detail": detail,
            "ttft_seconds": result.get("ttft_seconds"),
            "elapsed_seconds": round(float(elapsed), 6),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "cached_prompt_tokens": _cached_prompt_tokens(usage),
            "chunks": result.get("chunks"),
            "finish_reason": _finish_reason(response),
            "prompt_sha256": request["prompt_sha256"],
            "line_count": request["line_count"],
            "required_terms": list(request["required_terms"]),
        }
    except Exception as exc:
        return {
            "phase": phase,
            "session": request["session"],
            "turn": request["turn"],
            "concurrent_group": concurrent_group,
            "ok": False,
            "detail": f"request failed: {exc!r}",
            "ttft_seconds": None,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "cached_prompt_tokens": None,
            "chunks": 0,
            "finish_reason": None,
            "prompt_sha256": request["prompt_sha256"],
            "line_count": request["line_count"],
            "required_terms": list(request["required_terms"]),
        }


def _as_float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _phase_row(rows: list[Json], phase: str) -> Json | None:
    return next((row for row in rows if row.get("phase") == phase), None)


def _ratio(numerator: Any, denominator: Any) -> float | None:
    num = _as_float(numerator)
    den = _as_float(denominator)
    if num is None or den is None or den <= 0:
        return None
    return round(num / den, 3)


def _summarize_requests(
    rows: list[Json],
    *,
    regression_ttft_ratio: float,
) -> Json:
    warm_a_solo = _phase_row(rows, "warm_a_solo")
    warm_a_after_b_solo = _phase_row(rows, "warm_a_after_b_solo")
    warm_a_interleaved = _phase_row(rows, "warm_a_interleaved_after_rebuild")
    sequential_ratio = _ratio(
        None
        if warm_a_after_b_solo is None
        else warm_a_after_b_solo.get("ttft_seconds"),
        None if warm_a_solo is None else warm_a_solo.get("ttft_seconds"),
    )
    interleaved_ratio = _ratio(
        None
        if warm_a_interleaved is None
        else warm_a_interleaved.get("ttft_seconds"),
        None if warm_a_solo is None else warm_a_solo.get("ttft_seconds"),
    )
    cached_total = sum(
        int(row.get("cached_prompt_tokens") or 0)
        for row in rows
        if row.get("cached_prompt_tokens") is not None
    )
    failure_count = sum(0 if row.get("ok") else 1 for row in rows)
    suspect = any(
        ratio is not None and ratio >= regression_ttft_ratio
        for ratio in (sequential_ratio, interleaved_ratio)
    )
    return {
        "request_count": len(rows),
        "failure_count": failure_count,
        "cached_tokens_total": cached_total,
        "warm_a_solo_ttft_seconds": None
        if warm_a_solo is None
        else warm_a_solo.get("ttft_seconds"),
        "warm_a_after_b_solo_ttft_seconds": None
        if warm_a_after_b_solo is None
        else warm_a_after_b_solo.get("ttft_seconds"),
        "warm_a_after_b_solo_vs_solo_ttft_ratio": sequential_ratio,
        "warm_a_interleaved_after_rebuild_ttft_seconds": None
        if warm_a_interleaved is None
        else warm_a_interleaved.get("ttft_seconds"),
        "warm_a_interleaved_after_rebuild_vs_solo_ttft_ratio": interleaved_ratio,
        "warm_a_after_b_ttft_seconds": None
        if warm_a_after_b_solo is None
        else warm_a_after_b_solo.get("ttft_seconds"),
        "warm_a_after_b_vs_solo_ttft_ratio": sequential_ratio,
        "regression_ttft_ratio_threshold": regression_ttft_ratio,
        "suspect_prefix_reuse_regression": suspect,
    }


def run_prefix_cache_probe(
    *,
    base_url: str,
    model: str,
    variant: str,
    case_name: str = DEFAULT_CASE_NAME,
    line_count: int = DEFAULT_LINE_COUNT,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    timeout: float = 1800.0,
    request_retries: int = 1,
    headers: dict[str, str] | None = None,
    extra_body: Json | None = None,
    regression_ttft_ratio: float = DEFAULT_REGRESSION_TTFT_RATIO,
    fail_on_regression: bool = False,
    stream_func: StreamFunc = stream_chat_completion,
) -> Json:
    request_specs = [
        ("cold_a", "a", 1),
        ("warm_a_solo", "a", 2),
        ("cold_b", "b", 1),
        ("warm_a_after_b_solo", "a", 3),
        ("warm_a_after_rebuild", "a", 4),
        ("warm_a_interleaved_after_rebuild", "a", 5),
        ("warm_b_interleaved", "b", 2),
    ]
    requests = [
        build_prefix_cache_request(
            session=session,
            turn=turn,
            line_count=line_count,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            thinking_mode=thinking_mode,
            probe_label=label,
        )
        for label, session, turn in request_specs
    ]
    if extra_body:
        for request in requests:
            request["payload"].update(extra_body)

    rows: list[Json] = []
    for request in requests[:5]:
        rows.append(
            _run_request(
                request,
                base_url=base_url,
                timeout=timeout,
                headers=headers,
                request_retries=request_retries,
                stream_func=stream_func,
            )
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_request = {
            executor.submit(
                _run_request,
                request,
                base_url=base_url,
                timeout=timeout,
                headers=headers,
                request_retries=request_retries,
                stream_func=stream_func,
                concurrent_group="warm_a_b",
            ): request
            for request in requests[5:]
        }
        concurrent_rows = [future.result() for future in as_completed(future_to_request)]
    order = {label: index for index, (label, _, _) in enumerate(request_specs)}
    rows.extend(sorted(concurrent_rows, key=lambda row: order[str(row["phase"])]))

    summary = _summarize_requests(rows, regression_ttft_ratio=regression_ttft_ratio)
    ok = summary["failure_count"] == 0 and (
        not fail_on_regression or not summary["suspect_prefix_reuse_regression"]
    )
    return {
        "case": case_name,
        "variant": variant,
        "model": model,
        "ok": ok,
        "thinking_mode": thinking_mode,
        "temperature": temperature,
        "top_p": top_p,
        "line_count": line_count,
        "max_tokens": max_tokens,
        "summary": summary,
        "requests": rows,
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


def _fmt(value: Any, digits: int = 3) -> str:
    number = _as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.{digits}f}"


def _fmt_int(value: Any) -> str:
    number = _as_float(value)
    if number is None:
        return "n/a"
    return str(int(round(number)))


def write_prefix_cache_probe_markdown(path: Path, row: Json) -> None:
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    lines = [
        "# Prefix Cache Probe",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Model: `{row.get('model')}`",
        f"- Thinking mode: `{row.get('thinking_mode', 'n/a')}`",
        f"- Temperature: `{row.get('temperature', 'n/a')}`",
        f"- Top P: `{row.get('top_p', 'n/a')}`",
        f"- Prompt lines per session: `{row.get('line_count', 'n/a')}`",
        f"- Requests: `{summary.get('request_count', 'n/a')}`",
        f"- Failures: `{summary.get('failure_count', 'n/a')}`",
        f"- Cached prompt tokens total: `{summary.get('cached_tokens_total', 'n/a')}`",
        (
            "- Sequential warm A after B / warm A solo TTFT ratio: "
            f"`{_fmt(summary.get('warm_a_after_b_vs_solo_ttft_ratio'))}`"
        ),
        (
            "- Interleaved warm A after rebuild / warm A solo TTFT ratio: "
            f"`{_fmt(summary.get('warm_a_interleaved_after_rebuild_vs_solo_ttft_ratio'))}`"
        ),
        (
            "- Suspect prefix reuse regression: "
            f"`{summary.get('suspect_prefix_reuse_regression', 'n/a')}`"
        ),
        "",
        "## KV/runtime stats",
        "",
        (
            "Use the sibling `runtime_stats_summary.json` for phase-local "
            "`gpu_kv_cache_usage_percent_*`, `prefix_cache_hit_rate_percent_delta`, "
            "and `preemptions_delta`. This probe records request-level "
            "`cached_prompt_tokens`, elapsed time, and streaming TTFT."
        ),
        "",
        "## Requests",
        "",
        "| Phase | Session | OK | TTFT s | Elapsed s | Prompt tokens | cached_prompt_tokens | Detail |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for request in row.get("requests", []):
        if not isinstance(request, dict):
            continue
        lines.append(
            f"| `{request.get('phase')}` | `{request.get('session')}` | "
            f"{'yes' if request.get('ok') else 'no'} | "
            f"{_fmt(request.get('ttft_seconds'))} | "
            f"{_fmt(request.get('elapsed_seconds'))} | "
            f"{_fmt_int(request.get('prompt_tokens'))} | "
            f"{_fmt_int(request.get('cached_prompt_tokens'))} | "
            f"{request.get('detail') or 'n/a'} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
