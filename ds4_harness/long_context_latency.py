from __future__ import annotations

import hashlib
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ds4_harness.checks import assistant_text
from ds4_harness.generation import thinking_extra_body
from ds4_harness.long_context_probe import (
    DEFAULT_LINE_COUNT,
    DEFAULT_REQUIRED_TERMS,
    build_long_context_prompt,
)
from ds4_harness.prefix_cache_probe import stream_chat_completion


Json = dict[str, Any]
StreamFunc = Callable[..., Json]

DEFAULT_CASE_NAME = "long_context_interactive_latency"
DEFAULT_LINE_COUNTS = (DEFAULT_LINE_COUNT,)
DEFAULT_CONCURRENCY = (1,)
DEFAULT_CACHE_MODES = ("cold", "warm")
DEFAULT_MAX_TOKENS = 64


@dataclass(frozen=True)
class LatencyPrompt:
    name: str
    source: str
    text: str
    required_terms: tuple[str, ...]
    line_count: int | None = None
    prompt_file: str | None = None

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")
    return "".join(chars).strip("_") or "prompt"


def _prompt_excerpt(prompt: str) -> Json:
    lines = prompt.splitlines()
    return {
        "head": "\n".join(lines[:8]),
        "tail": "\n".join(lines[-8:]),
    }


def _with_salt(text: str, salt: str | None) -> str:
    if not salt:
        return text
    lines = text.splitlines()
    if not lines:
        return f"Probe nonce: {salt}"
    return "\n".join([lines[0], f"Probe nonce: {salt}", *lines[1:]])


def build_synthetic_latency_prompt(
    *,
    line_count: int,
    salt: str | None = None,
) -> LatencyPrompt:
    prompt = build_long_context_prompt(line_count=line_count)
    text = _with_salt(prompt.text, salt)
    return LatencyPrompt(
        name=f"synthetic_{line_count}_lines",
        source="synthetic",
        text=text,
        required_terms=DEFAULT_REQUIRED_TERMS,
        line_count=line_count,
    )


def build_file_latency_prompt(
    path: Path,
    *,
    salt: str | None = None,
) -> LatencyPrompt:
    text = path.read_text(encoding="utf-8")
    prompt_text = _with_salt(text, salt)
    return LatencyPrompt(
        name=_slug(path.stem),
        source="file",
        text=prompt_text,
        required_terms=(),
        line_count=None,
        prompt_file=str(path),
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


def _cached_prompt_tokens(usage: Json) -> int | None:
    details = usage.get("prompt_tokens_details")
    if not isinstance(details, dict):
        return None
    value = details.get("cached_tokens")
    try:
        return None if value is None else int(value)
    except (TypeError, ValueError):
        return None


def _request_ok(text: str, required_terms: tuple[str, ...]) -> tuple[bool, str]:
    if not required_terms:
        if text.strip():
            return True, "non-empty response"
        return False, "empty response"
    lowered = text.lower()
    missing = [term for term in required_terms if term.lower() not in lowered]
    if missing:
        return False, "missing required terms: " + ", ".join(missing)
    return True, "matched required terms"


def _assistant_text_artifact(prompt: LatencyPrompt, text: str) -> Json:
    artifact: Json = {
        "assistant_text_sha256": _sha256(text),
        "assistant_text_length": len(text),
    }
    if prompt.source == "synthetic":
        artifact["assistant_text_excerpt"] = text[:512]
    return artifact


def _build_payload(
    prompt: LatencyPrompt,
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


def _run_stream_request(
    *,
    base_url: str,
    model: str,
    variant: str,
    case_name: str,
    prompt: LatencyPrompt,
    cache_mode: str,
    concurrency: int,
    repeat_index: int,
    request_index: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    thinking_mode: str,
    timeout: float,
    headers: dict[str, str] | None,
    extra_body: Json | None,
    stream_func: StreamFunc,
    phase: str = "measure",
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
    try:
        result = stream_func(
            base_url,
            "/v1/chat/completions",
            payload,
            timeout,
            headers=headers,
            probe_metadata={
                "case": case_name,
                "variant": variant,
                "prompt": prompt.name,
                "cache_mode": cache_mode,
                "concurrency": concurrency,
                "repeat": repeat_index,
                "request_index": request_index,
                "phase": phase,
            },
        )
        response = result.get("response") if isinstance(result.get("response"), dict) else {}
        text = str(result.get("assistant_text") or assistant_text(response))
        ok, detail = _request_ok(text, prompt.required_terms)
        usage = _usage_tokens(response)
        elapsed = result.get("elapsed_seconds")
        if not isinstance(elapsed, int | float):
            elapsed = time.monotonic() - started
        row = {
            "phase": phase,
            "cache_mode": cache_mode,
            "prompt": prompt.name,
            "prompt_source": prompt.source,
            "variant": variant,
            "concurrency": concurrency,
            "repeat": repeat_index,
            "request_index": request_index,
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
            "response_id": response.get("id") if response.get("id") else None,
            "prompt_sha256": prompt.sha256,
            "line_count": prompt.line_count,
            "prompt_file": prompt.prompt_file,
        }
        row.update(_assistant_text_artifact(prompt, text))
        return row
    except Exception as exc:
        return {
            "phase": phase,
            "cache_mode": cache_mode,
            "prompt": prompt.name,
            "prompt_source": prompt.source,
            "variant": variant,
            "concurrency": concurrency,
            "repeat": repeat_index,
            "request_index": request_index,
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
            "prompt_sha256": prompt.sha256,
            "line_count": prompt.line_count,
            "prompt_file": prompt.prompt_file,
        }


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(statistics.fmean(values), 6)


def _max(values: list[float]) -> float | None:
    if not values:
        return None
    return round(max(values), 6)


def _min(values: list[float]) -> float | None:
    if not values:
        return None
    return round(min(values), 6)


def _numeric_values(rows: list[Json], key: str) -> list[float]:
    values = []
    for row in rows:
        value = row.get(key)
        if isinstance(value, int | float):
            values.append(float(value))
    return values


def _summarize_rows(rows: list[Json]) -> list[Json]:
    groups: dict[tuple[str, str, int], list[Json]] = {}
    for row in rows:
        if row.get("phase") != "measure":
            continue
        key = (
            str(row.get("prompt")),
            str(row.get("cache_mode")),
            int(row.get("concurrency") or 0),
        )
        groups.setdefault(key, []).append(row)

    summary = []
    for (prompt, cache_mode, concurrency), group_rows in sorted(groups.items()):
        ttft = _numeric_values(group_rows, "ttft_seconds")
        elapsed = _numeric_values(group_rows, "elapsed_seconds")
        prompt_tokens = _numeric_values(group_rows, "prompt_tokens")
        cached_tokens = _numeric_values(group_rows, "cached_prompt_tokens")
        completion_tokens = _numeric_values(group_rows, "completion_tokens")
        summary.append(
            {
                "prompt": prompt,
                "cache_mode": cache_mode,
                "concurrency": concurrency,
                "request_count": len(group_rows),
                "failure_count": sum(0 if row.get("ok") else 1 for row in group_rows),
                "ttft_seconds_min": _min(ttft),
                "ttft_seconds_mean": _mean(ttft),
                "ttft_seconds_max": _max(ttft),
                "elapsed_seconds_mean": _mean(elapsed),
                "elapsed_seconds_max": _max(elapsed),
                "prompt_tokens_mean": _mean(prompt_tokens),
                "completion_tokens_mean": _mean(completion_tokens),
                "cached_prompt_tokens_mean": _mean(cached_tokens),
            }
        )
    return summary


def _build_prompts(
    *,
    line_counts: list[int],
    prompt_files: list[Path],
    salt: str | None,
) -> list[LatencyPrompt]:
    prompts = [
        build_synthetic_latency_prompt(line_count=line_count, salt=salt)
        for line_count in line_counts
    ]
    prompts.extend(build_file_latency_prompt(path, salt=salt) for path in prompt_files)
    return prompts


def run_long_context_latency_matrix(
    *,
    base_url: str,
    model: str,
    variant: str,
    case_name: str = DEFAULT_CASE_NAME,
    line_counts: list[int] | None = None,
    prompt_files: list[Path] | None = None,
    concurrencies: list[int] | None = None,
    cache_modes: list[str] | None = None,
    repeat_count: int = 1,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    timeout: float = 1800.0,
    headers: dict[str, str] | None = None,
    extra_body: Json | None = None,
    stream_func: StreamFunc = stream_chat_completion,
) -> Json:
    line_counts = (
        list(DEFAULT_LINE_COUNTS) if line_counts is None else list(line_counts)
    )
    prompt_files = [] if prompt_files is None else list(prompt_files)
    concurrencies = (
        list(DEFAULT_CONCURRENCY) if concurrencies is None else list(concurrencies)
    )
    cache_modes = (
        list(DEFAULT_CACHE_MODES) if cache_modes is None else list(cache_modes)
    )
    if repeat_count < 1:
        raise ValueError("repeat_count must be >= 1")
    if any(value < 128 for value in line_counts):
        raise ValueError("line counts must be at least 128")
    if any(value < 1 for value in concurrencies):
        raise ValueError("concurrency values must be at least 1")
    invalid_modes = [mode for mode in cache_modes if mode not in {"cold", "warm"}]
    if invalid_modes:
        raise ValueError("unsupported cache modes: " + ", ".join(invalid_modes))
    if not line_counts and not prompt_files:
        raise ValueError("at least one line count or prompt file is required")

    rows: list[Json] = []
    prompt_manifests: list[Json] = []
    for base_prompt in _build_prompts(
        line_counts=line_counts,
        prompt_files=prompt_files,
        salt=None,
    ):
        prompt_manifests.append(
            {
                "name": base_prompt.name,
                "source": base_prompt.source,
                "line_count": base_prompt.line_count,
                "prompt_file": base_prompt.prompt_file,
                "sha256": base_prompt.sha256,
                "excerpt": _prompt_excerpt(base_prompt.text),
                "required_terms": list(base_prompt.required_terms),
            }
        )
        for cache_mode in cache_modes:
            if cache_mode == "warm":
                warmup = _run_stream_request(
                    base_url=base_url,
                    model=model,
                    variant=variant,
                    case_name=case_name,
                    prompt=base_prompt,
                    cache_mode=cache_mode,
                    concurrency=1,
                    repeat_index=0,
                    request_index=0,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    thinking_mode=thinking_mode,
                    timeout=timeout,
                    headers=headers,
                    extra_body=extra_body,
                    stream_func=stream_func,
                    phase="warmup",
                )
                rows.append(warmup)

            for concurrency in concurrencies:
                for repeat_index in range(1, repeat_count + 1):
                    requests = []
                    for request_index in range(1, concurrency + 1):
                        if cache_mode == "cold":
                            salt = (
                                f"{base_prompt.name}:{concurrency}:"
                                f"{repeat_index}:{request_index}:{time.monotonic_ns()}"
                            )
                            prompt = _build_prompts(
                                line_counts=[]
                                if base_prompt.source == "file"
                                else [int(base_prompt.line_count or 0)],
                                prompt_files=[]
                                if base_prompt.source == "synthetic"
                                else [Path(str(base_prompt.prompt_file))],
                                salt=salt,
                            )[0]
                        else:
                            prompt = base_prompt
                        requests.append((request_index, prompt))

                    if concurrency == 1:
                        request_index, prompt = requests[0]
                        rows.append(
                            _run_stream_request(
                                base_url=base_url,
                                model=model,
                                variant=variant,
                                case_name=case_name,
                                prompt=prompt,
                                cache_mode=cache_mode,
                                concurrency=concurrency,
                                repeat_index=repeat_index,
                                request_index=request_index,
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
                        continue

                    with ThreadPoolExecutor(max_workers=concurrency) as executor:
                        futures = [
                            executor.submit(
                                _run_stream_request,
                                base_url=base_url,
                                model=model,
                                variant=variant,
                                case_name=case_name,
                                prompt=prompt,
                                cache_mode=cache_mode,
                                concurrency=concurrency,
                                repeat_index=repeat_index,
                                request_index=request_index,
                                max_tokens=max_tokens,
                                temperature=temperature,
                                top_p=top_p,
                                thinking_mode=thinking_mode,
                                timeout=timeout,
                                headers=headers,
                                extra_body=extra_body,
                                stream_func=stream_func,
                            )
                            for request_index, prompt in requests
                        ]
                        rows.extend(future.result() for future in as_completed(futures))

    rows.sort(
        key=lambda row: (
            str(row.get("prompt")),
            str(row.get("cache_mode")),
            int(row.get("concurrency") or 0),
            int(row.get("repeat") or 0),
            int(row.get("request_index") or 0),
            str(row.get("phase")),
        )
    )
    summary = _summarize_rows(rows)
    return {
        "case": case_name,
        "variant": variant,
        "model": model,
        "ok": all(row.get("ok") for row in rows),
        "thinking_mode": thinking_mode,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "repeat_count": repeat_count,
        "concurrencies": concurrencies,
        "cache_modes": cache_modes,
        "prompts": prompt_manifests,
        "summary": summary,
        "requests": rows,
    }


def _fmt(value: Any, digits: int = 3) -> str:
    if not isinstance(value, int | float):
        return "n/a"
    return f"{float(value):.{digits}f}"


def _fmt_int(value: Any) -> str:
    if not isinstance(value, int | float):
        return "n/a"
    return str(int(round(float(value))))


def write_long_context_latency_markdown(path: Path, row: Json) -> None:
    lines = [
        "# Long Context Latency Matrix",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Model: `{row.get('model')}`",
        f"- Thinking mode: `{row.get('thinking_mode')}`",
        f"- Max tokens: `{row.get('max_tokens')}`",
        f"- Repeat count: `{row.get('repeat_count')}`",
        f"- Concurrency: `{', '.join(str(v) for v in row.get('concurrencies', []))}`",
        f"- Cache modes: `{', '.join(str(v) for v in row.get('cache_modes', []))}`",
        "",
        "## Summary",
        "",
        "| Prompt | Cache | C | Requests | Failures | TTFT mean s | TTFT max s | Elapsed mean s | Prompt tok | Cached tok | Completion tok |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in row.get("summary", []):
        if not isinstance(item, dict):
            continue
        lines.append(
            "| {prompt} | {cache} | {concurrency} | {requests} | {failures} | "
            "{ttft_mean} | {ttft_max} | {elapsed_mean} | {prompt_tokens} | "
            "{cached_tokens} | {completion_tokens} |".format(
                prompt=item.get("prompt"),
                cache=item.get("cache_mode"),
                concurrency=item.get("concurrency"),
                requests=item.get("request_count"),
                failures=item.get("failure_count"),
                ttft_mean=_fmt(item.get("ttft_seconds_mean")),
                ttft_max=_fmt(item.get("ttft_seconds_max")),
                elapsed_mean=_fmt(item.get("elapsed_seconds_mean")),
                prompt_tokens=_fmt_int(item.get("prompt_tokens_mean")),
                cached_tokens=_fmt_int(item.get("cached_prompt_tokens_mean")),
                completion_tokens=_fmt_int(item.get("completion_tokens_mean")),
            )
        )

    lines.extend(["", "## Prompts", ""])
    for prompt in row.get("prompts", []):
        if not isinstance(prompt, dict):
            continue
        lines.extend(
            [
                f"### {prompt.get('name')}",
                "",
                f"- Source: `{prompt.get('source')}`",
                f"- Line count: `{prompt.get('line_count', 'n/a')}`",
                f"- Prompt file: `{prompt.get('prompt_file', 'n/a')}`",
                f"- SHA256: `{prompt.get('sha256')}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Request Rows",
            "",
            "| Phase | Prompt | Cache | C | Repeat | Request | OK | TTFT s | Elapsed s | Prompt tok | Cached tok | Detail |",
            "| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for request in row.get("requests", []):
        if not isinstance(request, dict):
            continue
        lines.append(
            "| {phase} | {prompt} | {cache} | {concurrency} | {repeat} | {request} | "
            "{ok} | {ttft} | {elapsed} | {prompt_tokens} | {cached_tokens} | {detail} |".format(
                phase=request.get("phase"),
                prompt=request.get("prompt"),
                cache=request.get("cache_mode"),
                concurrency=request.get("concurrency"),
                repeat=request.get("repeat"),
                request=request.get("request_index"),
                ok="yes" if request.get("ok") else "no",
                ttft=_fmt(request.get("ttft_seconds")),
                elapsed=_fmt(request.get("elapsed_seconds")),
                prompt_tokens=_fmt_int(request.get("prompt_tokens")),
                cached_tokens=_fmt_int(request.get("cached_prompt_tokens")),
                detail=str(request.get("detail", "")).replace("|", "\\|"),
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
