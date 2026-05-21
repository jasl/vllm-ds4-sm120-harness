from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable


Json = dict[str, Any]
MetricsFunc = Callable[..., dict[str, int]]
HealthFunc = Callable[..., int]
ChatFunc = Callable[..., Json]

DEFAULT_CASE_NAME = "user_report_prefix_cache_http_metrics_stress"
DEFAULT_FILLER_WORDS = 800
DEFAULT_TURNS = 3
DEFAULT_TRIALS = 5
DEFAULT_MAX_TOKENS = 256


def parse_prefix_metrics(text: str) -> dict[str, int]:
    hits = 0
    queries = 0
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([a-zA-Z_:]+)(?:\{[^}]*\})?\s+([0-9.eE+-]+)$", line)
        if not match:
            continue
        metric = match.group(1)
        value = int(float(match.group(2)))
        if metric.endswith("prefix_cache_hits") or metric.endswith(
            "prefix_cache_hits_total"
        ):
            hits += value
        elif metric.endswith("prefix_cache_queries") or metric.endswith(
            "prefix_cache_queries_total"
        ):
            queries += value
    return {"hits": hits, "queries": queries}


def get_prefix_metrics(
    base_url: str,
    timeout: float,
    headers: dict[str, str] | None = None,
) -> dict[str, int]:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", "metrics")
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to read /metrics: {exc}") from exc
    return parse_prefix_metrics(text)


def get_health_status(
    base_url: str,
    timeout: float,
    headers: dict[str, str] | None = None,
) -> int:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", "health")
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to read /health: {exc}") from exc


def build_long_prompt(filler_words: int, session_idx: int) -> str:
    if filler_words < 1:
        raise ValueError("filler_words must be >= 1")
    base = (
        "You are analyzing a research manuscript. Below is the section text. "
        "After it, answer the question at the end concisely.\n\n<SECTION>\n"
    )
    words = (
        "the quick brown fox jumps over the lazy dog while the researcher "
        "observes carefully and records each experimental iteration with "
        "precision across the multi-step protocol"
    ).split()
    body = " ".join(words[index % len(words)] for index in range(filler_words))
    tail = (
        "\n</SECTION>\n\nQuestion: In one paragraph, summarize the primary "
        "claim of the section and identify one methodological limitation."
    )
    return base + body + tail + f"\n\n[session_hint: session_{session_idx}_distinct_seed]"


def chat_completion(
    base_url: str,
    model: str,
    conversation: list[Json],
    user_msg: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 1.0,
    top_p: float = 1.0,
    timeout: float = 180.0,
    headers: dict[str, str] | None = None,
) -> Json:
    messages = conversation + [{"role": "user", "content": user_msg}]
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stream": False,
    }
    encoded = json.dumps(body).encode("utf-8")
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
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"chat completion failed: {exc}") from exc
    elapsed = time.monotonic() - started
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("chat completion response did not include choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise RuntimeError("chat completion response did not include a message")
    return {"message": message, "elapsed_seconds": elapsed, "response": payload}


def _assistant_text(message: Json) -> str:
    parts = []
    for key in ("content", "reasoning", "reasoning_content"):
        value = message.get(key)
        if isinstance(value, str) and value:
            parts.append(value)
    return "\n".join(parts)


def run_session(
    *,
    base_url: str,
    model: str,
    session_idx: int,
    turns: int,
    filler_words: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    timeout: float,
    headers: dict[str, str] | None,
    chat_func: ChatFunc,
) -> list[Json]:
    if turns < 1:
        raise ValueError("turns must be >= 1")
    followups = [
        "Good - now list two counter-examples that would complicate the methodology.",
        "Finally, summarize the exchange so far in two sentences.",
    ]
    user_msgs = [build_long_prompt(filler_words, session_idx)] + followups[: turns - 1]

    conversation: list[Json] = []
    stats: list[Json] = []
    for turn_idx, user_msg in enumerate(user_msgs):
        result = chat_func(
            base_url,
            model,
            conversation,
            user_msg,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            timeout=timeout,
            headers=headers,
        )
        message = result["message"]
        conversation.append({"role": "user", "content": user_msg})
        conversation.append({"role": "assistant", "content": _assistant_text(message)})
        stats.append(
            {
                "turn": turn_idx,
                "elapsed_seconds": round(float(result["elapsed_seconds"]), 3),
            }
        )
    return stats


def _rate(hits: int, queries: int) -> float:
    return hits / queries if queries else 0.0


def _run_trial(
    *,
    base_url: str,
    model: str,
    trial: int,
    filler_words: int,
    turns: int,
    max_tokens: int,
    temperature: float,
    top_p: float,
    timeout: float,
    metrics_timeout: float,
    headers: dict[str, str] | None,
    metrics_func: MetricsFunc,
    chat_func: ChatFunc,
) -> Json:
    m0 = metrics_func(base_url, metrics_timeout, headers=headers)

    started = time.monotonic()
    solo_turns = run_session(
        base_url=base_url,
        model=model,
        session_idx=1,
        turns=turns,
        filler_words=filler_words,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        timeout=timeout,
        headers=headers,
        chat_func=chat_func,
    )
    solo_elapsed = time.monotonic() - started

    m1 = metrics_func(base_url, metrics_timeout, headers=headers)
    solo_hits = m1["hits"] - m0["hits"]
    solo_queries = m1["queries"] - m0["queries"]

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                run_session,
                base_url=base_url,
                model=model,
                session_idx=session_idx,
                turns=turns,
                filler_words=filler_words,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                timeout=timeout,
                headers=headers,
                chat_func=chat_func,
            )
            for session_idx in (1, 2)
        ]
        concurrent_sessions = [future.result() for future in futures]
    concurrent_elapsed = time.monotonic() - started

    m2 = metrics_func(base_url, metrics_timeout, headers=headers)
    concurrent_hits = m2["hits"] - m1["hits"]
    concurrent_queries = m2["queries"] - m1["queries"]

    return {
        "ok": True,
        "trial": trial,
        "solo_hits": solo_hits,
        "solo_queries": solo_queries,
        "solo_hit_rate": _rate(solo_hits, solo_queries),
        "solo_elapsed_seconds": round(solo_elapsed, 3),
        "solo_turns": solo_turns,
        "concurrent_hits": concurrent_hits,
        "concurrent_queries": concurrent_queries,
        "concurrent_hit_rate": _rate(concurrent_hits, concurrent_queries),
        "concurrent_elapsed_seconds": round(concurrent_elapsed, 3),
        "concurrent_sessions": concurrent_sessions,
    }


def _summarize_trials(trials: list[Json]) -> Json:
    failures = [trial for trial in trials if not trial.get("ok")]
    concurrent_rates = [
        float(trial["concurrent_hit_rate"]) for trial in trials if trial.get("ok")
    ]
    solo_rates = [float(trial["solo_hit_rate"]) for trial in trials if trial.get("ok")]
    return {
        "trial_count": len(trials),
        "failure_count": len(failures),
        "solo_hit_rate_mean": sum(solo_rates) / len(solo_rates) if solo_rates else None,
        "concurrent_hit_rate_mean": (
            sum(concurrent_rates) / len(concurrent_rates) if concurrent_rates else None
        ),
    }


def run_prefix_cache_stress(
    *,
    base_url: str,
    model: str,
    case_name: str = DEFAULT_CASE_NAME,
    trials: int = DEFAULT_TRIALS,
    filler_words: int = DEFAULT_FILLER_WORDS,
    turns: int = DEFAULT_TURNS,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = 1.0,
    top_p: float = 1.0,
    timeout: float = 180.0,
    metrics_timeout: float = 10.0,
    health_timeout: float = 10.0,
    headers: dict[str, str] | None = None,
    metrics_func: MetricsFunc = get_prefix_metrics,
    health_func: HealthFunc = get_health_status,
    chat_func: ChatFunc = chat_completion,
) -> Json:
    if trials < 1:
        raise ValueError("trials must be >= 1")
    health_status = health_func(base_url, health_timeout, headers=headers)
    trial_rows: list[Json] = []
    for trial in range(1, trials + 1):
        try:
            trial_rows.append(
                _run_trial(
                    base_url=base_url,
                    model=model,
                    trial=trial,
                    filler_words=filler_words,
                    turns=turns,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    timeout=timeout,
                    metrics_timeout=metrics_timeout,
                    headers=headers,
                    metrics_func=metrics_func,
                    chat_func=chat_func,
                )
            )
        except Exception as exc:  # noqa: BLE001 - stress gate records failures.
            trial_rows.append({"ok": False, "trial": trial, "error": repr(exc)})
    summary = _summarize_trials(trial_rows)
    ok = health_status == 200 and summary["failure_count"] == 0
    return {
        "ok": ok,
        "case": case_name,
        "model": model,
        "base_url": base_url,
        "health_status": health_status,
        "trials": trial_rows,
        "summary": summary,
        "config": {
            "trials": trials,
            "filler_words": filler_words,
            "turns": turns,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        },
    }


def _fmt_percent(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def write_prefix_cache_stress_markdown(path: Path, row: Json) -> None:
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    lines = [
        "# Prefix Cache HTTP Metrics Stress",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Case: `{row.get('case')}`",
        f"- Model: `{row.get('model')}`",
        f"- Health status: `{row.get('health_status', 'n/a')}`",
        f"- Trials: `{summary.get('trial_count', 'n/a')}`",
        f"- Failures: `{summary.get('failure_count', 'n/a')}`",
        f"- Solo hit rate mean: `{_fmt_percent(summary.get('solo_hit_rate_mean'))}`",
        "- Concurrent hit rate mean: "
        f"`{_fmt_percent(summary.get('concurrent_hit_rate_mean'))}`",
        "",
        "| Trial | OK | Solo hit rate | Solo elapsed s | Concurrent hit rate | "
        "Concurrent elapsed s | Error |",
        "| ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for trial in row.get("trials", []):
        lines.append(
            "| {trial} | {ok} | {solo_rate} | {solo_elapsed} | {conc_rate} | "
            "{conc_elapsed} | {error} |".format(
                trial=trial.get("trial", "n/a"),
                ok="yes" if trial.get("ok") else "no",
                solo_rate=_fmt_percent(trial.get("solo_hit_rate")),
                solo_elapsed=trial.get("solo_elapsed_seconds", "n/a"),
                conc_rate=_fmt_percent(trial.get("concurrent_hit_rate")),
                conc_elapsed=trial.get("concurrent_elapsed_seconds", "n/a"),
                error=str(trial.get("error", "")),
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
