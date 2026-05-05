from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from ds4_harness.checks import assistant_text
from ds4_harness.generation import thinking_extra_body
from ds4_harness.prefix_cache_probe import stream_chat_completion


Json = dict[str, Any]
StreamFunc = Callable[..., Json]

DEFAULT_CASE_NAME = "streaming_pressure_short_soak"
DEFAULT_CONCURRENCY = 4
DEFAULT_ROUND_COUNT = 3
DEFAULT_LINE_COUNT = 1200
DEFAULT_MAX_TOKENS = 128
DEFAULT_MAX_TTFT_SECONDS = 60.0
DEFAULT_MAX_ELAPSED_SECONDS = 300.0


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _check_term(worker_index: int, round_index: int) -> str:
    if worker_index < 0:
        raise ValueError("worker_index must be >= 0")
    if round_index < 1:
        raise ValueError("round_index must be >= 1")
    return f"STREAM-W{worker_index:02d}-R{round_index:02d}-CHECK"


def _worker_document(worker_index: int, line_count: int) -> str:
    if line_count < 128:
        raise ValueError("line_count must be at least 128")

    rows = [
        f"Streaming pressure reference packet for worker {worker_index:02d}.",
        "This packet is deterministic and intentionally long.",
        "Every round reuses the packet while the conversation grows.",
        "",
    ]
    middle = max(64, line_count // 2)
    tail = line_count - 7
    for index in range(1, line_count + 1):
        if index == 13:
            rows.append(
                f"Line {index:04d}: worker marker is WORKER-{worker_index:02d}."
            )
            continue
        if index == middle:
            rows.append(
                f"Line {index:04d}: middle checkpoint for worker {worker_index:02d}."
            )
            continue
        if index == tail:
            rows.append(
                f"Line {index:04d}: tail checkpoint for worker {worker_index:02d}."
            )
            continue
        rows.append(
            f"Line {index:04d}: worker={worker_index:02d}; "
            f"slot={index % 43:02d}; checksum={(index * 97 + worker_index) % 997:03d}; "
            "stable filler for streaming pressure validation."
        )
    return "\n".join(rows)


def build_streaming_pressure_request(
    *,
    worker_index: int,
    round_index: int,
    line_count: int = DEFAULT_LINE_COUNT,
    model: str = "model",
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 1.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    probe_label: str | None = None,
) -> Json:
    required = _check_term(worker_index, round_index)
    document = _worker_document(worker_index, line_count)
    messages: list[Json] = [
        {
            "role": "system",
            "content": (
                "You are validating streaming responses under concurrent load. "
                "Start with the exact requested check term, then give three "
                "short status lines. Do not omit the check term."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Store this deterministic long reference packet for worker "
                f"{worker_index:02d}.\n\n{document}"
            ),
        },
        {
            "role": "assistant",
            "content": (
                f"Worker {worker_index:02d} reference packet received. "
                "Streaming validation can continue."
            ),
        },
    ]
    for previous_round in range(1, round_index):
        previous_term = _check_term(worker_index, previous_round)
        messages.extend(
            [
                {
                    "role": "user",
                    "content": (
                        f"Round {previous_round}: repeat the check term and "
                        "confirm the stream is readable."
                    ),
                },
                {
                    "role": "assistant",
                    "content": (
                        f"{previous_term}\n"
                        "status: previous streaming response completed.\n"
                        "status: content remained readable.\n"
                        "status: worker context was preserved."
                    ),
                },
            ]
        )
    messages.append(
        {
            "role": "user",
            "content": (
                f"Round {round_index}: start with the exact check term "
                f"{required}, then emit three short status lines."
            ),
        }
    )

    payload: Json = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    payload.update(thinking_extra_body(thinking_mode))
    prompt_json = json.dumps(messages, ensure_ascii=False, sort_keys=True)
    return {
        "payload": payload,
        "worker": worker_index,
        "round": round_index,
        "probe_label": probe_label
        or f"round_{round_index:02d}_worker_{worker_index:02d}",
        "required_terms": [required],
        "line_count": line_count,
        "prompt_sha256": _sha256(prompt_json),
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


def _finish_reason(response: Json) -> str | None:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    choice = choices[0]
    if not isinstance(choice, dict):
        return None
    reason = choice.get("finish_reason")
    return str(reason) if reason is not None else None


def _request_ok(text: str, required_terms: list[str]) -> tuple[bool, str]:
    lowered = text.lower()
    missing = [term for term in required_terms if term.lower() not in lowered]
    if missing:
        return False, "missing required terms: " + ", ".join(missing)
    return True, "matched required streaming term"


def _run_request(
    request: Json,
    *,
    base_url: str,
    timeout: float,
    headers: dict[str, str] | None,
    request_retries: int,
    stream_func: StreamFunc,
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
                "worker_index": request["worker"],
                "round_index": request["round"],
                "required_terms": list(request["required_terms"]),
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
            "worker": request["worker"],
            "round": request["round"],
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
            "worker": request["worker"],
            "round": request["round"],
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


def _as_int(value: Any) -> int | None:
    try:
        return None if value is None else int(value)
    except (TypeError, ValueError):
        return None


def _round_or_none(value: float | None) -> float | None:
    return None if value is None else round(value, 6)


def _summarize_requests(
    rows: list[Json],
    *,
    max_ttft_seconds: float | None,
    max_elapsed_seconds: float | None,
) -> Json:
    ttfts = [
        value
        for value in (_as_float(row.get("ttft_seconds")) for row in rows)
        if value is not None
    ]
    elapsed = [
        value
        for value in (_as_float(row.get("elapsed_seconds")) for row in rows)
        if value is not None
    ]
    chunks = [_as_int(row.get("chunks")) or 0 for row in rows]
    prompt_tokens = [
        value
        for value in (_as_int(row.get("prompt_tokens")) for row in rows)
        if value is not None
    ]
    cached_total = sum(
        int(row.get("cached_prompt_tokens") or 0)
        for row in rows
        if row.get("cached_prompt_tokens") is not None
    )
    max_ttft = max(ttfts) if ttfts else None
    max_elapsed = max(elapsed) if elapsed else None
    failure_count = sum(0 if row.get("ok") else 1 for row in rows)
    suspect_slow_ttft = (
        max_ttft is not None
        and max_ttft_seconds is not None
        and max_ttft > max_ttft_seconds
    )
    suspect_slow_elapsed = (
        max_elapsed is not None
        and max_elapsed_seconds is not None
        and max_elapsed > max_elapsed_seconds
    )
    return {
        "request_count": len(rows),
        "completed_request_count": len(rows) - failure_count,
        "failure_count": failure_count,
        "cached_tokens_total": cached_total,
        "total_chunks": sum(chunks),
        "min_chunks": min(chunks) if chunks else None,
        "max_prompt_tokens": max(prompt_tokens) if prompt_tokens else None,
        "max_ttft_seconds": _round_or_none(max_ttft),
        "avg_ttft_seconds": _round_or_none(sum(ttfts) / len(ttfts) if ttfts else None),
        "max_elapsed_seconds": _round_or_none(max_elapsed),
        "avg_elapsed_seconds": _round_or_none(
            sum(elapsed) / len(elapsed) if elapsed else None
        ),
        "max_ttft_seconds_threshold": max_ttft_seconds,
        "max_elapsed_seconds_threshold": max_elapsed_seconds,
        "suspect_slow_ttft": suspect_slow_ttft,
        "suspect_slow_elapsed": suspect_slow_elapsed,
    }


def run_streaming_pressure_soak(
    *,
    base_url: str,
    model: str,
    variant: str,
    case_name: str = DEFAULT_CASE_NAME,
    concurrency: int = DEFAULT_CONCURRENCY,
    round_count: int = DEFAULT_ROUND_COUNT,
    line_count: int = DEFAULT_LINE_COUNT,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 1.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    timeout: float = 900.0,
    request_retries: int = 1,
    headers: dict[str, str] | None = None,
    extra_body: Json | None = None,
    max_ttft_seconds: float | None = DEFAULT_MAX_TTFT_SECONDS,
    max_elapsed_seconds: float | None = DEFAULT_MAX_ELAPSED_SECONDS,
    fail_on_slow: bool = False,
    stream_func: StreamFunc = stream_chat_completion,
) -> Json:
    if concurrency < 1:
        raise ValueError("concurrency must be >= 1")
    if round_count < 1:
        raise ValueError("round_count must be >= 1")

    rows: list[Json] = []
    for round_index in range(1, round_count + 1):
        requests = [
            build_streaming_pressure_request(
                worker_index=worker_index,
                round_index=round_index,
                line_count=line_count,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                thinking_mode=thinking_mode,
            )
            for worker_index in range(concurrency)
        ]
        if extra_body:
            for request in requests:
                request["payload"].update(extra_body)

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(
                    _run_request,
                    request,
                    base_url=base_url,
                    timeout=timeout,
                    headers=headers,
                    request_retries=request_retries,
                    stream_func=stream_func,
                )
                for request in requests
            ]
            round_rows = [future.result() for future in as_completed(futures)]
        rows.extend(sorted(round_rows, key=lambda row: int(row["worker"])))

    summary = _summarize_requests(
        rows,
        max_ttft_seconds=max_ttft_seconds,
        max_elapsed_seconds=max_elapsed_seconds,
    )
    ok = summary["failure_count"] == 0 and (
        not fail_on_slow
        or (
            not summary["suspect_slow_ttft"]
            and not summary["suspect_slow_elapsed"]
        )
    )
    return {
        "case": case_name,
        "variant": variant,
        "model": model,
        "ok": ok,
        "thinking_mode": thinking_mode,
        "temperature": temperature,
        "top_p": top_p,
        "concurrency": concurrency,
        "round_count": round_count,
        "line_count": line_count,
        "max_tokens": max_tokens,
        "summary": summary,
        "requests": rows,
    }


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


def write_streaming_pressure_soak_markdown(path: Path, row: Json) -> None:
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    lines = [
        "# Streaming Pressure Soak",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Model: `{row.get('model')}`",
        f"- Thinking mode: `{row.get('thinking_mode', 'n/a')}`",
        f"- Temperature: `{row.get('temperature', 'n/a')}`",
        f"- Top P: `{row.get('top_p', 'n/a')}`",
        f"- Concurrency: `{row.get('concurrency', 'n/a')}`",
        f"- Rounds: `{row.get('round_count', 'n/a')}`",
        f"- Prompt lines per worker: `{row.get('line_count', 'n/a')}`",
        f"- Requests: `{summary.get('request_count', 'n/a')}`",
        f"- Failures: `{summary.get('failure_count', 'n/a')}`",
        f"- Cached prompt tokens total: `{summary.get('cached_tokens_total', 'n/a')}`",
        f"- Max TTFT seconds: `{_fmt(summary.get('max_ttft_seconds'))}`",
        f"- Max elapsed seconds: `{_fmt(summary.get('max_elapsed_seconds'))}`",
        f"- Total chunks: `{summary.get('total_chunks', 'n/a')}`",
        f"- Suspect slow TTFT: `{summary.get('suspect_slow_ttft', 'n/a')}`",
        f"- Suspect slow elapsed: `{summary.get('suspect_slow_elapsed', 'n/a')}`",
        "",
        "## KV/runtime stats",
        "",
        (
            "Use the sibling `runtime_stats_summary.json` for phase-local "
            "`running_requests_max`, `gpu_kv_cache_usage_percent_*`, "
            "`prefix_cache_hit_rate_percent_delta`, and `preemptions_delta`. "
            "This soak records streaming TTFT, elapsed time, chunk counts, and "
            "`cached_prompt_tokens` for every concurrent request."
        ),
        "",
        "## Requests",
        "",
        "| Phase | Round | Worker | OK | TTFT s | Elapsed s | Prompt tokens | cached_prompt_tokens | Chunks | Detail |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for request in row.get("requests", []):
        if not isinstance(request, dict):
            continue
        lines.append(
            f"| `{request.get('phase')}` | "
            f"{_fmt_int(request.get('round'))} | "
            f"{_fmt_int(request.get('worker'))} | "
            f"{'yes' if request.get('ok') else 'no'} | "
            f"{_fmt(request.get('ttft_seconds'))} | "
            f"{_fmt(request.get('elapsed_seconds'))} | "
            f"{_fmt_int(request.get('prompt_tokens'))} | "
            f"{_fmt_int(request.get('cached_prompt_tokens'))} | "
            f"{_fmt_int(request.get('chunks'))} | "
            f"{request.get('detail') or 'n/a'} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
