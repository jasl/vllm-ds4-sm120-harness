from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


Json = dict[str, Any]
RequestFunc = Callable[[str, Json, float], Json]
MetricsFunc = Callable[[str, float], str]

DEFAULT_CASE_NAME = "decode_throughput_sequential_probe"
DEFAULT_VARIANT = "manual"
DEFAULT_MAX_TOKENS = 512
DEFAULT_TOP_P = 1.0
DEFAULT_TIMEOUT = 300.0
DEFAULT_SLOW_TOK_S_THRESHOLD = 36.0
DEFAULT_PROMPTS = (
    "Write exactly 512 tokens of concise technical notes about GPU inference "
    "scheduling. Use numbered clauses. Do not stop early.",
    "Write exactly 512 tokens of Python performance debugging advice. Use "
    "numbered clauses. Do not stop early.",
    "Write exactly 512 tokens of deployment runbook notes for a local LLM "
    "server. Use numbered clauses. Do not stop early.",
)
DEFAULT_SERIES_SPECS = (
    "fixed_temp1:fixed:1.0:20",
    "cycle3_temp1:cycle3:1.0:20",
    "fixed_temp0:fixed:0.0:20",
)


@dataclass(frozen=True)
class DecodeProbeSeriesSpec:
    name: str
    prompt_group: str
    temperature: float
    request_count: int


def _round_or_none(value: float | None, digits: int = 6) -> float | None:
    return None if value is None else round(value, digits)


def _mean(values: list[float]) -> float | None:
    return None if not values else sum(values) / len(values)


def _safe_ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return numerator / denominator


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_name(value: str, field: str) -> str:
    if not value:
        raise ValueError(f"{field} must not be empty")
    if any(not (char.isalnum() or char in "._-") for char in value):
        raise ValueError(
            f"{field} may only contain letters, numbers, '.', '_', or '-'"
        )
    return value


def parse_decode_probe_series_spec(text: str) -> DecodeProbeSeriesSpec:
    parts = [part.strip() for part in text.split(":")]
    if len(parts) != 4:
        raise ValueError(
            "decode throughput series spec must be "
            "name:prompt_group:temperature:request_count"
        )
    try:
        temperature = float(parts[2])
    except ValueError as exc:
        raise ValueError(f"temperature must be a number: {parts[2]!r}") from exc
    try:
        request_count = int(parts[3])
    except ValueError as exc:
        raise ValueError(f"request_count must be an integer: {parts[3]!r}") from exc
    if request_count < 1:
        raise ValueError("request_count must be >= 1")
    return DecodeProbeSeriesSpec(
        name=_validate_name(parts[0], "series name"),
        prompt_group=_validate_name(parts[1], "prompt group"),
        temperature=temperature,
        request_count=request_count,
    )


def parse_decode_probe_series_specs(
    values: str | list[str] | tuple[str, ...] | None,
) -> list[DecodeProbeSeriesSpec]:
    if values is None:
        values = list(DEFAULT_SERIES_SPECS)
    elif isinstance(values, str):
        values = [values]

    specs: list[DecodeProbeSeriesSpec] = []
    for value in values:
        for raw_item in value.split(","):
            item = raw_item.strip()
            if item:
                specs.append(parse_decode_probe_series_spec(item))
    if not specs:
        raise ValueError("at least one decode throughput series is required")
    names = [spec.name for spec in specs]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError("duplicate decode throughput series names: " + ", ".join(duplicates))
    return specs


def _prompts_for_group(prompt_group: str) -> tuple[str, ...]:
    if prompt_group == "fixed":
        return (DEFAULT_PROMPTS[0],)
    if prompt_group == "cycle3":
        return DEFAULT_PROMPTS
    raise ValueError(f"unknown prompt group: {prompt_group}")


_COUNTER_PATTERNS = {
    "drafts": re.compile(r"^vllm:spec_decode_num_drafts_total\{.*\}\s+([0-9.eE+-]+)$"),
    "draft_tokens": re.compile(
        r"^vllm:spec_decode_num_draft_tokens_total\{.*\}\s+([0-9.eE+-]+)$"
    ),
    "accepted": re.compile(
        r"^vllm:spec_decode_num_accepted_tokens_total\{.*\}\s+([0-9.eE+-]+)$"
    ),
    "accepted_pos0": re.compile(
        r'^vllm:spec_decode_num_accepted_tokens_per_pos_total\{.*position="0".*\}\s+([0-9.eE+-]+)$'
    ),
    "accepted_pos1": re.compile(
        r'^vllm:spec_decode_num_accepted_tokens_per_pos_total\{.*position="1".*\}\s+([0-9.eE+-]+)$'
    ),
}


def parse_spec_decode_counters(metrics_text: str) -> dict[str, float]:
    counters = {name: 0.0 for name in _COUNTER_PATTERNS}
    for raw_line in metrics_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        for name, pattern in _COUNTER_PATTERNS.items():
            match = pattern.match(line)
            if match:
                counters[name] += float(match.group(1))
                break
    return counters


def _counter_delta(before: dict[str, float], after: dict[str, float]) -> dict[str, float]:
    return {name: after.get(name, 0.0) - before.get(name, 0.0) for name in _COUNTER_PATTERNS}


def _request_text(response: Json) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    choice = choices[0]
    if not isinstance(choice, dict):
        return ""
    message = choice.get("message")
    if not isinstance(message, dict):
        return ""
    parts = []
    for key in ("content", "reasoning_content"):
        value = message.get(key)
        if isinstance(value, str):
            parts.append(value)
    return "\n".join(parts)


def _finish_reason(response: Json) -> str | None:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    choice = choices[0]
    if not isinstance(choice, dict):
        return None
    value = choice.get("finish_reason")
    return None if value is None else str(value)


def _post_chat_completion(base_url: str, payload: Json, timeout: float) -> Json:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
    return {
        "elapsed_seconds": time.perf_counter() - started,
        "response": json.loads(body.decode("utf-8")),
    }


def _fetch_metrics(base_url: str, timeout: float) -> str:
    with urllib.request.urlopen(base_url.rstrip("/") + "/metrics", timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _build_payload(
    *,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    top_p: float,
) -> Json:
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stream": False,
    }


def _request_row(
    *,
    base_url: str,
    model: str,
    series: DecodeProbeSeriesSpec,
    series_index: int,
    prompt_slot: int,
    prompt: str,
    max_tokens: int,
    top_p: float,
    timeout: float,
    request_func: RequestFunc,
    metrics_func: MetricsFunc,
) -> Json:
    metrics_timeout = min(timeout, 15.0)
    before = parse_spec_decode_counters(metrics_func(base_url, metrics_timeout))
    started = time.perf_counter()
    result = request_func(
        base_url,
        _build_payload(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=series.temperature,
            top_p=top_p,
        ),
        timeout,
    )
    elapsed = float(result.get("elapsed_seconds") or (time.perf_counter() - started))
    after = parse_spec_decode_counters(metrics_func(base_url, metrics_timeout))
    response = result.get("response") if isinstance(result.get("response"), dict) else {}
    usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    completion_tokens = int(usage.get("completion_tokens") or 0)
    delta = _counter_delta(before, after)
    text = _request_text(response)
    return {
        "series": series.name,
        "series_index": series_index,
        "prompt_group": series.prompt_group,
        "prompt_slot": prompt_slot,
        "temperature": series.temperature,
        "max_tokens": max_tokens,
        "elapsed_ms": round(elapsed * 1000.0, 3),
        "completion_tokens": completion_tokens,
        "tok_s": _round_or_none(
            completion_tokens / elapsed if elapsed > 0 else None,
            digits=3,
        ),
        "prompt_tokens": usage.get("prompt_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "finish_reason": _finish_reason(response),
        "text_sha256": _sha256(text),
        "text_prefix": text[:120].replace("\n", " "),
        "mtp_delta": delta,
        "acceptance_ratio": _round_or_none(
            _safe_ratio(delta.get("accepted"), delta.get("draft_tokens")),
            digits=4,
        ),
        "pos0_acceptance": _round_or_none(
            _safe_ratio(delta.get("accepted_pos0"), delta.get("drafts")),
            digits=4,
        ),
        "pos1_acceptance": _round_or_none(
            _safe_ratio(delta.get("accepted_pos1"), delta.get("drafts")),
            digits=4,
        ),
    }


def _float_values(rows: list[Json], key: str) -> list[float]:
    values = []
    for row in rows:
        value = row.get(key)
        if isinstance(value, int | float):
            values.append(float(value))
    return values


def _row_ratio_from_delta(row: Json, numerator: str, denominator: str) -> float | None:
    value = row.get(
        {
            ("accepted", "draft_tokens"): "acceptance_ratio",
            ("accepted_pos0", "drafts"): "pos0_acceptance",
            ("accepted_pos1", "drafts"): "pos1_acceptance",
        }[(numerator, denominator)]
    )
    if isinstance(value, int | float):
        return float(value)
    delta = row.get("mtp_delta")
    if not isinstance(delta, dict):
        return None
    try:
        return _safe_ratio(float(delta[numerator]), float(delta[denominator]))
    except (KeyError, TypeError, ValueError):
        return None


def _row_ratios(rows: list[Json], numerator: str, denominator: str) -> list[float]:
    values = []
    for row in rows:
        value = _row_ratio_from_delta(row, numerator, denominator)
        if value is not None:
            values.append(value)
    return values


def _series_summary(
    series: str,
    rows: list[Json],
    *,
    slow_tok_s_threshold: float,
) -> Json:
    tok_s = _float_values(rows, "tok_s")
    acceptance = _row_ratios(rows, "accepted", "draft_tokens")
    pos0 = _row_ratios(rows, "accepted_pos0", "drafts")
    pos1 = _row_ratios(rows, "accepted_pos1", "drafts")
    slots = []
    for slot in sorted({int(row.get("prompt_slot", 0)) for row in rows}):
        slot_rows = [row for row in rows if int(row.get("prompt_slot", 0)) == slot]
        slot_tok_s = _float_values(slot_rows, "tok_s")
        slot_acceptance = _row_ratios(slot_rows, "accepted", "draft_tokens")
        slot_pos0 = _row_ratios(slot_rows, "accepted_pos0", "drafts")
        slot_pos1 = _row_ratios(slot_rows, "accepted_pos1", "drafts")
        slots.append(
            {
                "prompt_slot": slot,
                "request_count": len(slot_rows),
                "mean_tok_s": _round_or_none(_mean(slot_tok_s)),
                "min_tok_s": _round_or_none(min(slot_tok_s) if slot_tok_s else None),
                "max_tok_s": _round_or_none(max(slot_tok_s) if slot_tok_s else None),
                "mean_acceptance_ratio": _round_or_none(_mean(slot_acceptance)),
                "mean_pos0_acceptance": _round_or_none(_mean(slot_pos0)),
                "mean_pos1_acceptance": _round_or_none(_mean(slot_pos1)),
            }
        )
    return {
        "series": series,
        "request_count": len(rows),
        "mean_tok_s": _round_or_none(_mean(tok_s)),
        "min_tok_s": _round_or_none(min(tok_s) if tok_s else None),
        "max_tok_s": _round_or_none(max(tok_s) if tok_s else None),
        "mean_acceptance_ratio": _round_or_none(_mean(acceptance)),
        "mean_pos0_acceptance": _round_or_none(_mean(pos0)),
        "mean_pos1_acceptance": _round_or_none(_mean(pos1)),
        "slow_request_indices": [
            int(row.get("series_index", index))
            for index, row in enumerate(rows, start=1)
            if isinstance(row.get("tok_s"), int | float)
            and float(row["tok_s"]) < slow_tok_s_threshold
        ],
        "slots": slots,
    }


def summarize_decode_throughput_probe(
    rows: list[Json],
    *,
    slow_tok_s_threshold: float = DEFAULT_SLOW_TOK_S_THRESHOLD,
) -> Json:
    series_names = []
    for row in rows:
        series = str(row.get("series"))
        if series not in series_names:
            series_names.append(series)
    return {
        "request_count": len(rows),
        "slow_tok_s_threshold": slow_tok_s_threshold,
        "slow_request_count": sum(
            1
            for row in rows
            if isinstance(row.get("tok_s"), int | float)
            and float(row["tok_s"]) < slow_tok_s_threshold
        ),
        "series": [
            _series_summary(
                series,
                [row for row in rows if row.get("series") == series],
                slow_tok_s_threshold=slow_tok_s_threshold,
            )
            for series in series_names
        ],
    }


def run_decode_throughput_probe(
    *,
    base_url: str,
    model: str,
    variant: str = DEFAULT_VARIANT,
    case_name: str = DEFAULT_CASE_NAME,
    series_specs: list[DecodeProbeSeriesSpec] | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    top_p: float = DEFAULT_TOP_P,
    timeout: float = DEFAULT_TIMEOUT,
    slow_tok_s_threshold: float = DEFAULT_SLOW_TOK_S_THRESHOLD,
    request_func: RequestFunc = _post_chat_completion,
    metrics_func: MetricsFunc = _fetch_metrics,
) -> Json:
    if max_tokens < 1:
        raise ValueError("max_tokens must be >= 1")
    specs = list(series_specs or parse_decode_probe_series_specs(None))
    rows: list[Json] = []
    for spec in specs:
        prompts = _prompts_for_group(spec.prompt_group)
        for index in range(1, spec.request_count + 1):
            prompt_slot = (index - 1) % len(prompts)
            rows.append(
                _request_row(
                    base_url=base_url,
                    model=model,
                    series=spec,
                    series_index=index,
                    prompt_slot=prompt_slot,
                    prompt=prompts[prompt_slot],
                    max_tokens=max_tokens,
                    top_p=top_p,
                    timeout=timeout,
                    request_func=request_func,
                    metrics_func=metrics_func,
                )
            )
    return {
        "case": case_name,
        "variant": variant,
        "ok": True,
        "profile": {
            "model": model,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "series_specs": [spec.__dict__ for spec in specs],
            "slow_tok_s_threshold": slow_tok_s_threshold,
        },
        "summary": summarize_decode_throughput_probe(
            rows,
            slow_tok_s_threshold=slow_tok_s_threshold,
        ),
        "requests": rows,
    }


def write_decode_throughput_probe_markdown(path: Path, row: Json) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    lines = [
        "# Decode Throughput Sequential Probe",
        "",
        f"- OK: `{json.dumps(row.get('ok'))}`",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Requests: `{summary.get('request_count', 'n/a')}`",
        f"- Slow threshold tok/s: `{summary.get('slow_tok_s_threshold', 'n/a')}`",
        f"- Slow requests: `{summary.get('slow_request_count', 'n/a')}`",
        "",
        "## Series",
        "",
        "| Series | Requests | Mean tok/s | Min tok/s | Max tok/s | Mean acceptance | Slow request indices |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in summary.get("series", []):
        lines.append(
            "| {series} | {count} | {mean} | {minv} | {maxv} | {accept} | {slow} |".format(
                series=item.get("series"),
                count=item.get("request_count"),
                mean=item.get("mean_tok_s"),
                minv=item.get("min_tok_s"),
                maxv=item.get("max_tok_s"),
                accept=item.get("mean_acceptance_ratio"),
                slow=", ".join(str(v) for v in item.get("slow_request_indices", [])),
            )
        )
    lines.extend(
        [
            "",
            "## Prompt Slots",
            "",
            "| Series | Slot | Requests | Mean tok/s | Mean acceptance | Pos0 | Pos1 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in summary.get("series", []):
        for slot in item.get("slots", []):
            lines.append(
                "| {series} | {slot} | {count} | {mean} | {accept} | {pos0} | {pos1} |".format(
                    series=item.get("series"),
                    slot=slot.get("prompt_slot"),
                    count=slot.get("request_count"),
                    mean=slot.get("mean_tok_s"),
                    accept=slot.get("mean_acceptance_ratio"),
                    pos0=slot.get("mean_pos0_acceptance"),
                    pos1=slot.get("mean_pos1_acceptance"),
                )
            )
    lines.extend(
        [
            "",
            "## Requests",
            "",
            "| Series | Index | Slot | Tok/s | Acceptance | Pos0 | Pos1 | Completion tokens | Finish |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for request in row.get("requests", []):
        lines.append(
            "| {series} | {index} | {slot} | {tok_s} | {accept} | {pos0} | {pos1} | {tokens} | {finish} |".format(
                series=request.get("series"),
                index=request.get("series_index"),
                slot=request.get("prompt_slot"),
                tok_s=request.get("tok_s"),
                accept=request.get("acceptance_ratio"),
                pos0=request.get("pos0_acceptance"),
                pos1=request.get("pos1_acceptance"),
                tokens=request.get("completion_tokens"),
                finish=request.get("finish_reason"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
