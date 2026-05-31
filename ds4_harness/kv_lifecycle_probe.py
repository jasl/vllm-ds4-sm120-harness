from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from ds4_harness.generation import thinking_extra_body
from ds4_harness.prefix_cache_probe import stream_chat_completion


Json = dict[str, Any]
MetricsFunc = Callable[..., "MetricSnapshot"]
RequestFunc = Callable[..., Json]

DEFAULT_CASE_NAME = "kv_lifecycle_idle_recovery"
DEFAULT_LINE_COUNT = 1900
DEFAULT_MAX_TOKENS = 64
DEFAULT_SESSION_COUNT = 3
DEFAULT_DISABLED_MAX_IDLE_KV_PERCENT = 2.0
DEFAULT_ENABLED_MAX_IDLE_KV_PERCENT = 90.0
DEFAULT_SETTLE_TIMEOUT = 60.0
DEFAULT_SETTLE_INTERVAL = 2.0


@dataclass(frozen=True)
class MetricSnapshot:
    gpu_kv_cache_usage_percent: float | None = None
    running_requests: float | None = None
    waiting_requests: float | None = None
    prefix_cache_hits: int | None = None
    prefix_cache_queries: int | None = None

    def to_json(self) -> Json:
        return asdict(self)


def _metric_name(name: str) -> str:
    return name.casefold().replace(":", "_")


def _to_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def _sum_latest(samples: list[tuple[str, float]], names: tuple[str, ...]) -> float | None:
    normalized = {_metric_name(name) for name in names}
    values = [value for name, value in samples if _metric_name(name) in normalized]
    return sum(values) if values else None


def _max_latest(samples: list[tuple[str, float]], names: tuple[str, ...]) -> float | None:
    normalized = {_metric_name(name) for name in names}
    values = [value for name, value in samples if _metric_name(name) in normalized]
    if not values:
        return None
    if max(values) <= 1.0:
        values = [value * 100 for value in values]
    return max(values)


def parse_metrics_snapshot(text: str) -> MetricSnapshot:
    samples: list[tuple[str, float]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(
            r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{[^}]*\})?\s+([-+0-9.eE]+)\s*$",
            line,
        )
        if not match:
            continue
        value = _to_float(match.group(2))
        if value is not None:
            samples.append((match.group(1), value))

    return MetricSnapshot(
        gpu_kv_cache_usage_percent=_round_optional(
            _max_latest(
                samples,
                (
                    "vllm:kv_cache_usage_perc",
                    "kv_cache_usage_perc",
                    "vllm:gpu_cache_usage_perc",
                    "gpu_cache_usage_perc",
                    "vllm:gpu_kv_cache_usage",
                    "gpu_kv_cache_usage",
                ),
            )
        ),
        running_requests=_round_optional(
            _sum_latest(
                samples,
                (
                    "vllm:num_requests_running",
                    "num_requests_running",
                    "vllm:requests_running",
                    "requests_running",
                ),
            )
        ),
        waiting_requests=_round_optional(
            _sum_latest(
                samples,
                (
                    "vllm:num_requests_waiting",
                    "num_requests_waiting",
                    "vllm:requests_waiting",
                    "requests_waiting",
                ),
            )
        ),
        prefix_cache_hits=_int_optional(
            _sum_latest(
                samples,
                (
                    "vllm:prefix_cache_hits",
                    "prefix_cache_hits",
                    "vllm:prefix_cache_hits_total",
                    "prefix_cache_hits_total",
                ),
            )
        ),
        prefix_cache_queries=_int_optional(
            _sum_latest(
                samples,
                (
                    "vllm:prefix_cache_queries",
                    "prefix_cache_queries",
                    "vllm:prefix_cache_queries_total",
                    "prefix_cache_queries_total",
                ),
            )
        ),
    )


def get_metrics_snapshot(
    *,
    base_url: str,
    timeout: float,
    headers: dict[str, str] | None = None,
) -> MetricSnapshot:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", "metrics")
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to read /metrics: {exc}") from exc
    return parse_metrics_snapshot(text)


def _round_optional(value: float | None, digits: int = 3) -> float | None:
    return None if value is None else round(value, digits)


def _int_optional(value: float | None) -> int | None:
    return None if value is None else int(round(value))


def _marker(session_index: int) -> str:
    return f"KV-LIFECYCLE-SESSION-{session_index:03d}-CODE-731"


def _long_document(session_index: int, line_count: int) -> str:
    if line_count < 32:
        raise ValueError("line_count must be at least 32")
    marker = _marker(session_index)
    rows = [
        f"KV lifecycle validation packet for session {session_index}.",
        "The content is deterministic and unrelated to other sessions.",
    ]
    marker_line = max(4, line_count // 2)
    for index in range(1, line_count + 1):
        if index == marker_line:
            rows.append(f"Line {index:04d}: the required marker is {marker}.")
            continue
        rows.append(
            f"Line {index:04d}: session={session_index:03d}; "
            f"bucket={index % 37:02d}; checksum={(index * 97 + session_index) % 1009:04d}; "
            "stable filler for KV cache lifecycle validation."
        )
    return "\n".join(rows)


def build_kv_lifecycle_payload(
    *,
    model: str,
    session_index: int,
    line_count: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    thinking_mode: str,
) -> Json:
    marker = _marker(session_index)
    payload: Json = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are validating vLLM KV cache lifecycle behavior. "
                    "Return only the exact requested marker."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"{_long_document(session_index, line_count)}\n\n"
                    f"Question: Return only this marker: {marker}"
                ),
            },
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    payload.update(thinking_extra_body(thinking_mode))
    return payload


def _request_ok(text: str, marker: str) -> tuple[bool, str]:
    if marker.casefold() in text.casefold():
        return True, "matched marker"
    return False, f"missing marker {marker}"


def run_lifecycle_request(
    *,
    base_url: str,
    model: str,
    session_index: int,
    line_count: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    thinking_mode: str,
    timeout: float,
    headers: dict[str, str] | None = None,
    phase: str,
) -> Json:
    marker = _marker(session_index)
    started = time.monotonic()
    try:
        result = stream_chat_completion(
            base_url,
            "/v1/chat/completions",
            build_kv_lifecycle_payload(
                model=model,
                session_index=session_index,
                line_count=line_count,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                thinking_mode=thinking_mode,
            ),
            timeout,
            headers=headers,
        )
        text = str(result.get("assistant_text") or "")
        ok, detail = _request_ok(text, marker)
        return {
            "phase": phase,
            "session_index": session_index,
            "ok": ok,
            "detail": detail,
            "ttft_seconds": result.get("ttft_seconds"),
            "elapsed_seconds": result.get("elapsed_seconds"),
            "chunks": result.get("chunks"),
            "finish_reason": _finish_reason(result.get("response")),
            "marker": marker,
        }
    except Exception as exc:  # noqa: BLE001 - lifecycle gate records request failures.
        return {
            "phase": phase,
            "session_index": session_index,
            "ok": False,
            "detail": f"request failed: {exc!r}",
            "ttft_seconds": None,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "chunks": 0,
            "finish_reason": None,
            "marker": marker,
        }


def run_abort_lifecycle_request(
    *,
    base_url: str,
    model: str,
    session_index: int,
    line_count: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    thinking_mode: str,
    timeout: float,
    headers: dict[str, str] | None = None,
    phase: str,
) -> Json:
    payload = build_kv_lifecycle_payload(
        model=model,
        session_index=session_index,
        line_count=line_count,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        thinking_mode=thinking_mode,
    )
    payload["stream"] = True
    payload.setdefault("stream_options", {"include_usage": True})
    encoded = json.dumps(payload).encode("utf-8")
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(
        urllib.parse.urljoin(base_url.rstrip("/") + "/", "v1/chat/completions"),
        data=encoded,
        headers=request_headers,
        method="POST",
    )
    started = time.monotonic()
    chunks = 0
    first_token_at: float | None = None
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line.removeprefix("data:").strip()
                if data == "[DONE]":
                    break
                event = json.loads(data)
                choices = event.get("choices") if isinstance(event, dict) else None
                if not isinstance(choices, list) or not choices:
                    continue
                delta = choices[0].get("delta") if isinstance(choices[0], dict) else None
                if not isinstance(delta, dict):
                    continue
                if any(isinstance(delta.get(key), str) and delta.get(key) for key in ("content", "reasoning", "reasoning_content")):
                    chunks += 1
                    first_token_at = time.monotonic()
                    break
        ok = chunks > 0
        return {
            "phase": phase,
            "session_index": session_index,
            "ok": ok,
            "detail": "aborted after first content chunk" if ok else "no content chunk before abort",
            "ttft_seconds": None if first_token_at is None else round(first_token_at - started, 6),
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "chunks": chunks,
            "finish_reason": "client_abort",
            "marker": _marker(session_index),
        }
    except Exception as exc:  # noqa: BLE001 - lifecycle gate records abort failures.
        return {
            "phase": phase,
            "session_index": session_index,
            "ok": False,
            "detail": f"abort request failed: {exc!r}",
            "ttft_seconds": None,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "chunks": chunks,
            "finish_reason": "client_abort",
            "marker": _marker(session_index),
        }


def _finish_reason(response: Any) -> str | None:
    if not isinstance(response, dict):
        return None
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    choice = choices[0]
    if not isinstance(choice, dict):
        return None
    reason = choice.get("finish_reason")
    return str(reason) if reason is not None else None


def _snapshot_idle(snapshot: MetricSnapshot) -> bool:
    running = snapshot.running_requests
    waiting = snapshot.waiting_requests
    return (running is None or running <= 0) and (waiting is None or waiting <= 0)


def _wait_for_idle(
    *,
    base_url: str,
    timeout: float,
    interval: float,
    metrics_timeout: float,
    headers: dict[str, str] | None,
    metrics_func: MetricsFunc,
) -> tuple[MetricSnapshot, bool]:
    deadline = time.monotonic() + timeout
    last_snapshot: MetricSnapshot | None = None
    while True:
        last_snapshot = metrics_func(
            base_url=base_url,
            timeout=metrics_timeout,
            headers=headers,
        )
        if _snapshot_idle(last_snapshot):
            return last_snapshot, True
        if time.monotonic() >= deadline:
            return last_snapshot, False
        time.sleep(max(0.0, interval))


def _counter_delta(final: int | None, initial: int | None) -> int | None:
    if final is None:
        return None
    if initial is None:
        return final
    delta = final - initial
    return delta if delta >= 0 else final


def run_kv_lifecycle_probe(
    *,
    base_url: str,
    model: str,
    variant: str,
    cache_mode: str,
    case_name: str = DEFAULT_CASE_NAME,
    session_count: int = DEFAULT_SESSION_COUNT,
    line_count: int = DEFAULT_LINE_COUNT,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 0.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    timeout: float = 1800.0,
    metrics_timeout: float = 10.0,
    settle_timeout: float = DEFAULT_SETTLE_TIMEOUT,
    settle_interval: float = DEFAULT_SETTLE_INTERVAL,
    max_idle_kv_usage_percent: float | None = None,
    include_abort: bool = True,
    headers: dict[str, str] | None = None,
    metrics_func: MetricsFunc = get_metrics_snapshot,
    request_func: RequestFunc = run_lifecycle_request,
    abort_request_func: RequestFunc = run_abort_lifecycle_request,
) -> Json:
    normalized_cache_mode = cache_mode.strip().casefold()
    if normalized_cache_mode not in {"disabled", "enabled"}:
        raise ValueError("cache_mode must be 'disabled' or 'enabled'")
    if session_count < 1:
        raise ValueError("session_count must be >= 1")
    if max_idle_kv_usage_percent is None:
        max_idle_kv_usage_percent = (
            DEFAULT_DISABLED_MAX_IDLE_KV_PERCENT
            if normalized_cache_mode == "disabled"
            else DEFAULT_ENABLED_MAX_IDLE_KV_PERCENT
        )

    snapshots: list[Json] = []

    def capture_idle(label: str) -> MetricSnapshot:
        snapshot, idle = _wait_for_idle(
            base_url=base_url,
            timeout=settle_timeout,
            interval=settle_interval,
            metrics_timeout=metrics_timeout,
            headers=headers,
            metrics_func=metrics_func,
        )
        row = snapshot.to_json()
        row["label"] = label
        row["idle"] = idle
        snapshots.append(row)
        return snapshot

    initial = capture_idle("initial_idle")
    request_rows: list[Json] = []
    for session_index in range(1, session_count + 1):
        phase = f"session_{session_index}"
        request_row = request_func(
            base_url=base_url,
            model=model,
            session_index=session_index,
            line_count=line_count,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            thinking_mode=thinking_mode,
            timeout=timeout,
            headers=headers,
            phase=phase,
        )
        idle_snapshot = capture_idle(f"{phase}_idle")
        request_row["idle_kv_usage_percent_after_request"] = (
            idle_snapshot.gpu_kv_cache_usage_percent
        )
        request_rows.append(request_row)

    if include_abort:
        session_index = session_count + 1
        phase = f"abort_session_{session_index}"
        request_row = abort_request_func(
            base_url=base_url,
            model=model,
            session_index=session_index,
            line_count=line_count,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            thinking_mode=thinking_mode,
            timeout=timeout,
            headers=headers,
            phase=phase,
        )
        idle_snapshot = capture_idle(f"{phase}_idle")
        request_row["idle_kv_usage_percent_after_request"] = (
            idle_snapshot.gpu_kv_cache_usage_percent
        )
        request_rows.append(request_row)

    final_snapshot = MetricSnapshot(**{key: snapshots[-1].get(key) for key in MetricSnapshot.__dataclass_fields__})
    idle_kv_values = [
        float(value)
        for value in (
            row.get("gpu_kv_cache_usage_percent")
            for row in snapshots
            if row.get("label") != "initial_idle"
        )
        if value is not None
    ]
    max_idle_kv = max(idle_kv_values) if idle_kv_values else None
    final_idle_kv = final_snapshot.gpu_kv_cache_usage_percent
    kv_metric_available = max_idle_kv is not None
    idle_kv_within_threshold = (
        bool(kv_metric_available) and max_idle_kv <= max_idle_kv_usage_percent
    )
    failure_count = sum(0 if row.get("ok") else 1 for row in request_rows)
    idle_failure_count = sum(0 if row.get("idle") else 1 for row in snapshots)

    summary: Json = {
        "request_count": len(request_rows),
        "failure_count": failure_count,
        "idle_failure_count": idle_failure_count,
        "kv_metric_available": kv_metric_available,
        "initial_idle_kv_usage_percent": initial.gpu_kv_cache_usage_percent,
        "final_idle_kv_usage_percent": final_idle_kv,
        "max_idle_kv_usage_percent": _round_optional(max_idle_kv),
        "max_idle_kv_usage_percent_threshold": max_idle_kv_usage_percent,
        "idle_kv_within_threshold": idle_kv_within_threshold,
        "prefix_cache_hits_delta": _counter_delta(
            final_snapshot.prefix_cache_hits,
            initial.prefix_cache_hits,
        ),
        "prefix_cache_queries_delta": _counter_delta(
            final_snapshot.prefix_cache_queries,
            initial.prefix_cache_queries,
        ),
    }
    ok = failure_count == 0 and idle_failure_count == 0 and idle_kv_within_threshold
    return {
        "case": case_name,
        "variant": variant,
        "model": model,
        "cache_mode": normalized_cache_mode,
        "ok": ok,
        "line_count": line_count,
        "session_count": session_count,
        "include_abort": include_abort,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "thinking_mode": thinking_mode,
        "summary": summary,
        "requests": request_rows,
        "snapshots": snapshots,
    }


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def write_kv_lifecycle_probe_markdown(path: Path, row: Json) -> None:
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    lines = [
        "# KV Lifecycle Probe",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Cache mode under test: `{row.get('cache_mode')}`",
        f"- Prompt lines per session: `{row.get('line_count')}`",
        f"- Completed/aborted requests: `{summary.get('request_count', 'n/a')}`",
        f"- Request failures: `{summary.get('failure_count', 'n/a')}`",
        f"- Idle poll failures: `{summary.get('idle_failure_count', 'n/a')}`",
        f"- Initial idle KV usage %: `{_fmt(summary.get('initial_idle_kv_usage_percent'))}`",
        f"- Final idle KV usage %: `{_fmt(summary.get('final_idle_kv_usage_percent'))}`",
        f"- Max idle KV usage %: `{_fmt(summary.get('max_idle_kv_usage_percent'))}`",
        f"- Max idle KV threshold %: `{_fmt(summary.get('max_idle_kv_usage_percent_threshold'))}`",
        f"- Idle KV within threshold: `{summary.get('idle_kv_within_threshold')}`",
        f"- Prefix-cache hits delta: `{summary.get('prefix_cache_hits_delta', 'n/a')}`",
        f"- Prefix-cache queries delta: `{summary.get('prefix_cache_queries_delta', 'n/a')}`",
        "",
        "C=2 long-prefill scheduling remains a separate follow-up; this probe only "
        "guards KV lifecycle correctness and prefix-cache recoverability.",
        "",
        "## Requests",
        "",
        "| Phase | OK | TTFT s | Elapsed s | Idle KV % After Request | Detail |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for request in row.get("requests", []):
        if not isinstance(request, dict):
            continue
        lines.append(
            "| {phase} | {ok} | {ttft} | {elapsed} | {idle_kv} | {detail} |".format(
                phase=request.get("phase", "n/a"),
                ok=request.get("ok", "n/a"),
                ttft=_fmt(request.get("ttft_seconds")),
                elapsed=_fmt(request.get("elapsed_seconds")),
                idle_kv=_fmt(request.get("idle_kv_usage_percent_after_request")),
                detail=str(request.get("detail", "")).replace("|", "\\|"),
            )
        )

    lines.extend(
        [
            "",
            "## Idle Snapshots",
            "",
            "| Label | Idle | KV % | Running | Waiting | Prefix Hits | Prefix Queries |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for snapshot in row.get("snapshots", []):
        if not isinstance(snapshot, dict):
            continue
        lines.append(
            "| {label} | {idle} | {kv} | {running} | {waiting} | {hits} | {queries} |".format(
                label=snapshot.get("label", "n/a"),
                idle=snapshot.get("idle", "n/a"),
                kv=_fmt(snapshot.get("gpu_kv_cache_usage_percent")),
                running=_fmt(snapshot.get("running_requests")),
                waiting=_fmt(snapshot.get("waiting_requests")),
                hits=snapshot.get("prefix_cache_hits", "n/a"),
                queries=snapshot.get("prefix_cache_queries", "n/a"),
            )
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
