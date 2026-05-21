from __future__ import annotations

import hashlib
import statistics
import threading
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
SleepFunc = Callable[[float], None]

DEFAULT_CASE_NAME = "long_context_interactive_latency"
DEFAULT_LINE_COUNTS = (DEFAULT_LINE_COUNT,)
DEFAULT_CONCURRENCY = (1,)
DEFAULT_CACHE_MODES = ("cold", "warm")
DEFAULT_MAX_TOKENS = 64
DEFAULT_MIXED_ARRIVAL_CASE_NAME = "long_context_mixed_arrival"
DEFAULT_MIXED_ARRIVAL_CASE_SPECS = (
    "decode_then_long:1900:1900:after_first_token:0:256:128",
    "long_then_short:4000:192:fixed_delay:2:128:64",
)
MIXED_ARRIVAL_START_TRIGGERS = ("after_first_token", "fixed_delay")


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


@dataclass(frozen=True)
class MixedArrivalCaseSpec:
    name: str
    primary_line_count: int
    secondary_line_count: int
    start_trigger: str
    secondary_start_delay_seconds: float
    primary_max_tokens: int
    secondary_max_tokens: int

    def to_json(self) -> Json:
        return {
            "name": self.name,
            "primary_line_count": self.primary_line_count,
            "secondary_line_count": self.secondary_line_count,
            "start_trigger": self.start_trigger,
            "secondary_start_delay_seconds": self.secondary_start_delay_seconds,
            "primary_max_tokens": self.primary_max_tokens,
            "secondary_max_tokens": self.secondary_max_tokens,
        }


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


def _validate_case_name(name: str) -> str:
    if not name:
        raise ValueError("mixed arrival case name must not be empty")
    if any(not (char.isalnum() or char in "._-") for char in name):
        raise ValueError(
            "mixed arrival case name may only contain letters, numbers, '.', '_', or '-'"
        )
    return name


def _parse_positive_int(value: str, field: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be an integer: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field} must be >= 1")
    return parsed


def _parse_non_negative_float(value: str, field: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a number: {value!r}") from exc
    if parsed < 0:
        raise ValueError(f"{field} must be >= 0")
    return parsed


def parse_mixed_arrival_case_spec(text: str) -> MixedArrivalCaseSpec:
    parts = [part.strip() for part in text.split(":")]
    if len(parts) != 7:
        raise ValueError(
            "mixed arrival case spec must be "
            "name:primary_line_count:secondary_line_count:start_trigger:"
            "secondary_start_delay_seconds:primary_max_tokens:secondary_max_tokens"
        )
    start_trigger = parts[3]
    if start_trigger not in MIXED_ARRIVAL_START_TRIGGERS:
        raise ValueError(
            "mixed arrival start_trigger must be one of: "
            + ", ".join(MIXED_ARRIVAL_START_TRIGGERS)
        )
    return MixedArrivalCaseSpec(
        name=_validate_case_name(parts[0]),
        primary_line_count=_parse_positive_int(parts[1], "primary_line_count"),
        secondary_line_count=_parse_positive_int(parts[2], "secondary_line_count"),
        start_trigger=start_trigger,
        secondary_start_delay_seconds=_parse_non_negative_float(
            parts[4], "secondary_start_delay_seconds"
        ),
        primary_max_tokens=_parse_positive_int(parts[5], "primary_max_tokens"),
        secondary_max_tokens=_parse_positive_int(parts[6], "secondary_max_tokens"),
    )


def parse_mixed_arrival_case_specs(
    values: str | list[str] | tuple[str, ...] | None,
) -> list[MixedArrivalCaseSpec]:
    if values is None:
        values = list(DEFAULT_MIXED_ARRIVAL_CASE_SPECS)
    elif isinstance(values, str):
        values = [values]

    specs: list[MixedArrivalCaseSpec] = []
    for value in values:
        for raw_item in value.split(","):
            item = raw_item.strip()
            if item:
                specs.append(parse_mixed_arrival_case_spec(item))
    if not specs:
        raise ValueError("at least one mixed arrival case is required")
    names = [spec.name for spec in specs]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError("duplicate mixed arrival case names: " + ", ".join(duplicates))
    return specs


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


def _decode_tokens_per_second(
    *,
    completion_tokens: Any,
    ttft_seconds: Any,
    elapsed_seconds: Any,
) -> float | None:
    tokens = _as_int(completion_tokens)
    ttft = _as_float(ttft_seconds)
    elapsed = _as_float(elapsed_seconds)
    if tokens is None or tokens <= 0 or ttft is None or elapsed is None:
        return None
    decode_seconds = elapsed - ttft
    if decode_seconds <= 0:
        return None
    return round(tokens / decode_seconds, 6)


def _round_or_none(value: float | None) -> float | None:
    return None if value is None else round(value, 6)


def _numeric_sequence(value: Any) -> list[float]:
    if not isinstance(value, list | tuple):
        return []
    parsed: list[float] = []
    for item in value:
        number = _as_float(item)
        if number is not None:
            parsed.append(number)
    return parsed


def _percentile_nearest_rank(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    if not 0 < percentile <= 1:
        raise ValueError("percentile must be > 0 and <= 1")
    ordered = sorted(values)
    index = max(
        0,
        min(len(ordered) - 1, int(len(ordered) * percentile + 0.999999) - 1),
    )
    return ordered[index]


def _inter_chunk_stats(samples: list[float]) -> Json:
    return {
        "inter_chunk_sample_count": len(samples),
        "avg_inter_chunk_seconds": _round_or_none(
            sum(samples) / len(samples) if samples else None
        ),
        "p95_inter_chunk_seconds": _round_or_none(
            _percentile_nearest_rank(samples, 0.95)
        ),
        "p99_inter_chunk_seconds": _round_or_none(
            _percentile_nearest_rank(samples, 0.99)
        ),
        "max_inter_chunk_seconds": _round_or_none(max(samples) if samples else None),
    }


def _min_to_max_ratio(values: list[float]) -> float | None:
    if not values:
        return None
    maximum = max(values)
    if maximum <= 0:
        return None
    return round(min(values) / maximum, 6)


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
    probe_metadata_extra: dict[str, Any] | None = None,
    row_extra: Json | None = None,
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
    probe_metadata = {
        "case": case_name,
        "variant": variant,
        "prompt": prompt.name,
        "cache_mode": cache_mode,
        "concurrency": concurrency,
        "repeat": repeat_index,
        "request_index": request_index,
        "phase": phase,
    }
    if probe_metadata_extra:
        probe_metadata.update(probe_metadata_extra)
    try:
        result = stream_func(
            base_url,
            "/v1/chat/completions",
            payload,
            timeout,
            headers=headers,
            probe_metadata=probe_metadata,
        )
        response = result.get("response") if isinstance(result.get("response"), dict) else {}
        text = str(result.get("assistant_text") or assistant_text(response))
        ok, detail = _request_ok(text, prompt.required_terms)
        usage = _usage_tokens(response)
        elapsed = result.get("elapsed_seconds")
        if not isinstance(elapsed, int | float):
            elapsed = time.monotonic() - started
        ttft = result.get("ttft_seconds")
        completion_tokens = usage.get("completion_tokens")
        decode_tps = _decode_tokens_per_second(
            completion_tokens=completion_tokens,
            ttft_seconds=ttft,
            elapsed_seconds=elapsed,
        )
        inter_chunk_seconds = _numeric_sequence(result.get("inter_chunk_seconds"))
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
            "ttft_seconds": ttft,
            "elapsed_seconds": round(float(elapsed), 6),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": completion_tokens,
            "total_tokens": usage.get("total_tokens"),
            "cached_prompt_tokens": _cached_prompt_tokens(usage),
            "decode_tokens_per_second": decode_tps,
            "chunks": result.get("chunks"),
            "time_to_last_token_seconds": result.get("time_to_last_token_seconds"),
            "inter_chunk_seconds": inter_chunk_seconds,
            **_inter_chunk_stats(inter_chunk_seconds),
            "finish_reason": _finish_reason(response),
            "response_id": response.get("id") if response.get("id") else None,
            "prompt_sha256": prompt.sha256,
            "line_count": prompt.line_count,
            "prompt_file": prompt.prompt_file,
        }
        if row_extra:
            row.update(row_extra)
        row.update(_assistant_text_artifact(prompt, text))
        return row
    except Exception as exc:
        row = {
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
            "decode_tokens_per_second": None,
            "chunks": 0,
            "time_to_last_token_seconds": None,
            "inter_chunk_seconds": [],
            **_inter_chunk_stats([]),
            "finish_reason": None,
            "prompt_sha256": prompt.sha256,
            "line_count": prompt.line_count,
            "prompt_file": prompt.prompt_file,
        }
        if row_extra:
            row.update(row_extra)
        return row


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
        decode_tps = _numeric_values(group_rows, "decode_tokens_per_second")
        inter_chunk_samples = [
            sample
            for row in group_rows
            for sample in _numeric_sequence(row.get("inter_chunk_seconds"))
        ]
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
                "decode_tokens_per_second_mean": _mean(decode_tps),
                "decode_tokens_per_second_min": _min(decode_tps),
                "decode_tokens_per_second_max": _max(decode_tps),
                "decode_tps_min_to_max_ratio": _min_to_max_ratio(decode_tps),
                **_inter_chunk_stats(inter_chunk_samples),
            }
        )
    c1_by_prompt_cache = {
        (str(item.get("prompt")), str(item.get("cache_mode"))): item.get(
            "decode_tokens_per_second_mean"
        )
        for item in summary
        if item.get("concurrency") == 1
    }
    for item in summary:
        c1_tps = _as_float(
            c1_by_prompt_cache.get((str(item.get("prompt")), str(item.get("cache_mode"))))
        )
        current_tps = _as_float(item.get("decode_tokens_per_second_mean"))
        item["decode_tps_vs_c1_ratio"] = (
            None
            if c1_tps is None or c1_tps <= 0 or current_tps is None
            else round(current_tps / c1_tps, 6)
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


def _role_rows(rows: list[Json], role: str) -> list[Json]:
    return [row for row in rows if row.get("request_role") == role]


def _summarize_mixed_arrival_rows(rows: list[Json]) -> list[Json]:
    groups: dict[str, list[Json]] = {}
    for row in rows:
        groups.setdefault(str(row.get("arrival_case")), []).append(row)

    summaries: list[Json] = []
    for case_name, case_rows in sorted(groups.items()):
        decode_tps = _numeric_values(case_rows, "decode_tokens_per_second")
        inter_chunk_samples = [
            sample
            for row in case_rows
            for sample in _numeric_sequence(row.get("inter_chunk_seconds"))
        ]
        summary: Json = {
            "case": case_name,
            "request_count": len(case_rows),
            "failure_count": sum(0 if row.get("ok") else 1 for row in case_rows),
            "decode_tokens_per_second_mean": _mean(decode_tps),
            "decode_tokens_per_second_min": _min(decode_tps),
            "decode_tokens_per_second_max": _max(decode_tps),
            "decode_tps_min_to_max_ratio": _min_to_max_ratio(decode_tps),
            **_inter_chunk_stats(inter_chunk_samples),
        }
        for role in ("primary", "secondary"):
            role_group = _role_rows(case_rows, role)
            ttfts = _numeric_values(role_group, "ttft_seconds")
            elapsed = _numeric_values(role_group, "elapsed_seconds")
            prompt_tokens = _numeric_values(role_group, "prompt_tokens")
            role_inter_chunks = [
                sample
                for row in role_group
                for sample in _numeric_sequence(row.get("inter_chunk_seconds"))
            ]
            summary.update(
                {
                    f"{role}_request_count": len(role_group),
                    f"{role}_failure_count": sum(
                        0 if row.get("ok") else 1 for row in role_group
                    ),
                    f"{role}_ttft_seconds_mean": _mean(ttfts),
                    f"{role}_max_ttft_seconds": _max(ttfts),
                    f"{role}_elapsed_seconds_mean": _mean(elapsed),
                    f"{role}_max_elapsed_seconds": _max(elapsed),
                    f"{role}_prompt_tokens_mean": _mean(prompt_tokens),
                    f"{role}_p95_inter_chunk_seconds": _round_or_none(
                        _percentile_nearest_rank(role_inter_chunks, 0.95)
                    ),
                    f"{role}_p99_inter_chunk_seconds": _round_or_none(
                        _percentile_nearest_rank(role_inter_chunks, 0.99)
                    ),
                    f"{role}_max_inter_chunk_seconds": _round_or_none(
                        max(role_inter_chunks) if role_inter_chunks else None
                    ),
                }
            )
        start_after_primary_ttft = []
        repeats = sorted({int(row.get("repeat") or 0) for row in case_rows})
        for repeat_index in repeats:
            repeat_rows = [
                row for row in case_rows if int(row.get("repeat") or 0) == repeat_index
            ]
            primary = next(
                (row for row in repeat_rows if row.get("request_role") == "primary"),
                None,
            )
            secondary = next(
                (row for row in repeat_rows if row.get("request_role") == "secondary"),
                None,
            )
            if not primary or not secondary:
                continue
            primary_start = _as_float(primary.get("actual_start_offset_seconds"))
            primary_ttft = _as_float(primary.get("ttft_seconds"))
            secondary_start = _as_float(secondary.get("actual_start_offset_seconds"))
            if (
                primary_start is None
                or primary_ttft is None
                or secondary_start is None
            ):
                continue
            start_after_primary_ttft.append(
                secondary_start - (primary_start + primary_ttft)
            )
        summary["secondary_start_after_primary_ttft_seconds"] = _mean(
            start_after_primary_ttft
        )
        summary["secondary_start_after_primary_ttft_seconds_min"] = _min(
            start_after_primary_ttft
        )
        summary["secondary_start_after_primary_ttft_seconds_max"] = _max(
            start_after_primary_ttft
        )
        summaries.append(summary)
    return summaries


def run_long_context_mixed_arrival_matrix(
    *,
    base_url: str,
    model: str,
    variant: str,
    case_name: str = DEFAULT_MIXED_ARRIVAL_CASE_NAME,
    case_specs: list[str] | None = None,
    repeat_count: int = 1,
    temperature: float = 0.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    timeout: float = 3600.0,
    headers: dict[str, str] | None = None,
    extra_body: Json | None = None,
    stream_func: StreamFunc = stream_chat_completion,
    sleep_func: SleepFunc = time.sleep,
) -> Json:
    if repeat_count < 1:
        raise ValueError("repeat_count must be >= 1")
    specs = parse_mixed_arrival_case_specs(case_specs)
    for spec in specs:
        if spec.primary_line_count < 128 or spec.secondary_line_count < 128:
            raise ValueError("line counts must be at least 128")

    rows: list[Json] = []
    prompt_manifests: list[Json] = []
    for spec in specs:
        for repeat_index in range(1, repeat_count + 1):
            primary_prompt = build_synthetic_latency_prompt(
                line_count=spec.primary_line_count,
                salt=f"{spec.name}:primary:{repeat_index}:{time.monotonic_ns()}",
            )
            secondary_prompt = build_synthetic_latency_prompt(
                line_count=spec.secondary_line_count,
                salt=f"{spec.name}:secondary:{repeat_index}:{time.monotonic_ns()}",
            )
            prompt_manifests.extend(
                [
                    {
                        "case": spec.name,
                        "request_role": "primary",
                        "name": primary_prompt.name,
                        "source": primary_prompt.source,
                        "line_count": primary_prompt.line_count,
                        "sha256": primary_prompt.sha256,
                        "excerpt": _prompt_excerpt(primary_prompt.text),
                        "required_terms": list(primary_prompt.required_terms),
                    },
                    {
                        "case": spec.name,
                        "request_role": "secondary",
                        "name": secondary_prompt.name,
                        "source": secondary_prompt.source,
                        "line_count": secondary_prompt.line_count,
                        "sha256": secondary_prompt.sha256,
                        "excerpt": _prompt_excerpt(secondary_prompt.text),
                        "required_terms": list(secondary_prompt.required_terms),
                    },
                ]
            )

            case_started = time.monotonic()
            primary_first_token = threading.Event()

            def mark_primary_first_token() -> None:
                primary_first_token.set()

            def run_role(
                *,
                role: str,
                request_index: int,
                prompt: LatencyPrompt,
                max_tokens: int,
                probe_extra: dict[str, Any] | None = None,
            ) -> Json:
                actual_start = time.monotonic() - case_started
                return _run_stream_request(
                    base_url=base_url,
                    model=model,
                    variant=variant,
                    case_name=case_name,
                    prompt=prompt,
                    cache_mode="cold",
                    concurrency=2,
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
                    phase="measure",
                    probe_metadata_extra={
                        "arrival_case": spec.name,
                        "request_role": role,
                        "start_trigger": spec.start_trigger,
                        **(probe_extra or {}),
                    },
                    row_extra={
                        "arrival_case": spec.name,
                        "request_role": role,
                        "start_trigger": spec.start_trigger,
                        "planned_start_after_seconds": (
                            0.0
                            if role == "primary"
                            else spec.secondary_start_delay_seconds
                        ),
                        "actual_start_offset_seconds": round(actual_start, 6),
                    },
                )

            with ThreadPoolExecutor(max_workers=2) as executor:
                primary_future = executor.submit(
                    run_role,
                    role="primary",
                    request_index=1,
                    prompt=primary_prompt,
                    max_tokens=spec.primary_max_tokens,
                    probe_extra={"on_first_token": mark_primary_first_token},
                )
                if spec.start_trigger == "after_first_token":
                    while not primary_first_token.wait(timeout=0.1):
                        if primary_future.done():
                            break
                if spec.secondary_start_delay_seconds > 0:
                    sleep_func(spec.secondary_start_delay_seconds)
                secondary_future = executor.submit(
                    run_role,
                    role="secondary",
                    request_index=2,
                    prompt=secondary_prompt,
                    max_tokens=spec.secondary_max_tokens,
                )
                rows.extend([primary_future.result(), secondary_future.result()])

    rows.sort(
        key=lambda row: (
            str(row.get("arrival_case")),
            int(row.get("repeat") or 0),
            int(row.get("request_index") or 0),
        )
    )
    summary = _summarize_mixed_arrival_rows(rows)
    return {
        "case": case_name,
        "variant": variant,
        "model": model,
        "ok": all(row.get("ok") for row in rows),
        "thinking_mode": thinking_mode,
        "temperature": temperature,
        "top_p": top_p,
        "repeat_count": repeat_count,
        "cases": [spec.to_json() for spec in specs],
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
        "| Prompt | Cache | C | Requests | Failures | TTFT mean s | TTFT max s | Elapsed mean s | Decode tok/s mean | Decode/C1 | Decode min/max | ITL p95 s | ITL p99 s | ITL max s | Prompt tok | Cached tok | Completion tok |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in row.get("summary", []):
        if not isinstance(item, dict):
            continue
        lines.append(
            "| {prompt} | {cache} | {concurrency} | {requests} | {failures} | "
            "{ttft_mean} | {ttft_max} | {elapsed_mean} | {decode_tps} | "
            "{decode_ratio} | {decode_fairness} | {itl_p95} | {itl_p99} | "
            "{itl_max} | {prompt_tokens} | {cached_tokens} | "
            "{completion_tokens} |".format(
                prompt=item.get("prompt"),
                cache=item.get("cache_mode"),
                concurrency=item.get("concurrency"),
                requests=item.get("request_count"),
                failures=item.get("failure_count"),
                ttft_mean=_fmt(item.get("ttft_seconds_mean")),
                ttft_max=_fmt(item.get("ttft_seconds_max")),
                elapsed_mean=_fmt(item.get("elapsed_seconds_mean")),
                decode_tps=_fmt(item.get("decode_tokens_per_second_mean")),
                decode_ratio=_fmt(item.get("decode_tps_vs_c1_ratio")),
                decode_fairness=_fmt(item.get("decode_tps_min_to_max_ratio")),
                itl_p95=_fmt(item.get("p95_inter_chunk_seconds")),
                itl_p99=_fmt(item.get("p99_inter_chunk_seconds")),
                itl_max=_fmt(item.get("max_inter_chunk_seconds")),
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
            "| Phase | Prompt | Cache | C | Repeat | Request | OK | TTFT s | Elapsed s | Decode tok/s | ITL p95 s | ITL p99 s | ITL max s | Prompt tok | Cached tok | Detail |",
            "| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for request in row.get("requests", []):
        if not isinstance(request, dict):
            continue
        lines.append(
            "| {phase} | {prompt} | {cache} | {concurrency} | {repeat} | {request} | "
            "{ok} | {ttft} | {elapsed} | {decode_tps} | {itl_p95} | {itl_p99} | "
            "{itl_max} | {prompt_tokens} | {cached_tokens} | {detail} |".format(
                phase=request.get("phase"),
                prompt=request.get("prompt"),
                cache=request.get("cache_mode"),
                concurrency=request.get("concurrency"),
                repeat=request.get("repeat"),
                request=request.get("request_index"),
                ok="yes" if request.get("ok") else "no",
                ttft=_fmt(request.get("ttft_seconds")),
                elapsed=_fmt(request.get("elapsed_seconds")),
                decode_tps=_fmt(request.get("decode_tokens_per_second")),
                itl_p95=_fmt(request.get("p95_inter_chunk_seconds")),
                itl_p99=_fmt(request.get("p99_inter_chunk_seconds")),
                itl_max=_fmt(request.get("max_inter_chunk_seconds")),
                prompt_tokens=_fmt_int(request.get("prompt_tokens")),
                cached_tokens=_fmt_int(request.get("cached_prompt_tokens")),
                detail=str(request.get("detail", "")).replace("|", "\\|"),
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_long_context_mixed_arrival_markdown(path: Path, row: Json) -> None:
    lines = [
        "# Long Context Mixed Arrival Matrix",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Model: `{row.get('model')}`",
        f"- Thinking mode: `{row.get('thinking_mode')}`",
        f"- Repeat count: `{row.get('repeat_count')}`",
        "",
        "## Cases",
        "",
        "| Case | Trigger | Delay s | Primary lines | Secondary lines | Primary max tokens | Secondary max tokens |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in row.get("cases", []):
        if not isinstance(item, dict):
            continue
        lines.append(
            "| {name} | {trigger} | {delay} | {primary_lines} | {secondary_lines} | "
            "{primary_tokens} | {secondary_tokens} |".format(
                name=item.get("name"),
                trigger=item.get("start_trigger"),
                delay=_fmt(item.get("secondary_start_delay_seconds")),
                primary_lines=item.get("primary_line_count"),
                secondary_lines=item.get("secondary_line_count"),
                primary_tokens=item.get("primary_max_tokens", "n/a"),
                secondary_tokens=item.get("secondary_max_tokens", "n/a"),
            )
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            "| Case | Requests | Failures | Primary TTFT mean s | Secondary TTFT mean s | Secondary ITL p95 s | Decode min/max | Secondary start vs primary TTFT s |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in row.get("summary", []):
        if not isinstance(item, dict):
            continue
        lines.append(
            "| {case} | {requests} | {failures} | {primary_ttft} | "
            "{secondary_ttft} | {secondary_itl} | {decode_fairness} | "
            "{start_after_ttft} |".format(
                case=item.get("case"),
                requests=item.get("request_count"),
                failures=item.get("failure_count"),
                primary_ttft=_fmt(item.get("primary_ttft_seconds_mean")),
                secondary_ttft=_fmt(item.get("secondary_ttft_seconds_mean")),
                secondary_itl=_fmt(item.get("secondary_p95_inter_chunk_seconds")),
                decode_fairness=_fmt(item.get("decode_tps_min_to_max_ratio")),
                start_after_ttft=_fmt(
                    item.get("secondary_start_after_primary_ttft_seconds")
                ),
            )
        )

    lines.extend(
        [
            "",
            "## Request Rows",
            "",
            "| Case | Role | OK | Start offset s | TTFT s | Elapsed s | Decode tok/s | ITL p95 s | Detail |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for request in row.get("requests", []):
        if not isinstance(request, dict):
            continue
        lines.append(
            "| {case} | {role} | {ok} | {start} | {ttft} | {elapsed} | "
            "{decode_tps} | {itl_p95} | {detail} |".format(
                case=request.get("arrival_case"),
                role=request.get("request_role"),
                ok="yes" if request.get("ok") else "no",
                start=_fmt(request.get("actual_start_offset_seconds")),
                ttft=_fmt(request.get("ttft_seconds")),
                elapsed=_fmt(request.get("elapsed_seconds")),
                decode_tps=_fmt(request.get("decode_tokens_per_second")),
                itl_p95=_fmt(request.get("p95_inter_chunk_seconds")),
                detail=str(request.get("detail", "")).replace("|", "\\|"),
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
