"""Long-context concurrent coherence gate (jasl/vllm PR#41834, reporter arthur).

arthur reported that, under long-context concurrent traffic on dual GB10, the
DeepSeek-V4 SM12x serve produced mixed-script gibberish, e.g.:

    Lambdaλθελόγ—— just查看 logs, let me check --result instead of polling我的猜测

That shares the root cause of jasl/vllm#19: the SM12x indexer non-contiguous-topk
bug drops the compressed (distant) context for the early queries of a long
prompt, so the prompt representation is corrupted and generation degrades into
incoherent, script-mixed output.

This gate fires several long-context requests concurrently and fails if any
response either (a) loses the planted needle codes (context following) or
(b) is incoherent: contains the Unicode replacement character, mixes in
unexpected non-Latin script for an English answer (Greek, Cyrillic, CJK, …), or
degenerates into repetition. The needle/context machinery is reused from
long_context_probe.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Callable

from ds4_harness.checks import assistant_text
from ds4_harness.client import post_json, post_json_with_retries
from ds4_harness.long_context_probe import (
    build_long_context_prompt,
    evaluate_long_context_response,
)

Json = dict[str, Any]


def _is_non_latin_letter(ch: str) -> bool:
    """True for an alphabetic character outside the Latin scripts.

    An English long-context answer should be essentially all Latin; arthur's
    gibberish injected Greek (λθελόγ), Cyrillic (внутрь) and CJK (查看). Measuring
    "non-Latin letters" (rather than CJK only) catches all of those at once.
    Accented Latin (Latin-1/Extended-A/B and Latin Extended Additional) stays
    "expected" so legitimate diacritics never trip the gate.
    """
    if not ch.isalpha():
        return False
    codepoint = ord(ch)
    if codepoint <= 0x024F:  # Basic Latin, Latin-1, Latin Extended-A/B
        return False
    if 0x1E00 <= codepoint <= 0x1EFF:  # Latin Extended Additional
        return False
    return True


@dataclass(frozen=True)
class CoherenceResult:
    ok: bool
    detail: str
    non_latin_fraction: float


_SPECIAL_TOKEN_RE = re.compile(r"<｜[^｜<>]{1,40}｜>")


def find_leaked_special_tokens(text: str) -> list[str]:
    """DeepSeek control tokens that escaped into decoded output.

    Reported by brianmiller (vllm-project/vllm#41834): under concurrent mixed
    prefill+decode, MTP speculative decode injected a spurious
    ``<｜begin▁of▁sentence｜>`` mid-generation, after which the continuation
    degraded. The text on either side of it stays fluent English, so every
    other signal here -- replacement characters, script mixing, degenerate
    repetition -- scores it coherent. A control token in decoded output is
    always a defect regardless of what surrounds it, which is why this is a
    separate check rather than another heuristic threshold.
    """
    return _SPECIAL_TOKEN_RE.findall(text)


def _looks_degenerate(text: str) -> bool:
    compact = "".join(text.split())
    if len(compact) < 24:
        return False
    if len(set(compact)) <= 2:
        return True
    longest = run = 1
    for previous, current in zip(compact, compact[1:]):
        run = run + 1 if current == previous else 1
        longest = max(longest, run)
    return longest >= max(20, len(compact) // 2)


def assess_english_coherence(
    text: str,
    *,
    max_non_latin_fraction: float = 0.15,
    min_chars: int = 1,
) -> CoherenceResult:
    """Heuristic coherence check for an English-expected response.

    Conservative on purpose so it does not false-fail the occasional proper noun
    or stray non-Latin token: only egregious gibberish (replacement chars, a
    response with a large fraction of non-Latin letters, or degenerate
    repetition) fails.
    """
    stripped = text.strip()
    if len(stripped) < min_chars:
        return CoherenceResult(False, f"response too short: {len(stripped)} chars", 0.0)
    leaked = find_leaked_special_tokens(text)
    if leaked:
        return CoherenceResult(
            False,
            f"leaked control token(s) into output: {sorted(set(leaked))}",
            0.0,
        )
    if "�" in text:
        return CoherenceResult(False, "contains U+FFFD replacement character", 0.0)
    letters = [ch for ch in text if ch.isalpha()]
    non_latin_fraction = (
        sum(1 for ch in letters if _is_non_latin_letter(ch)) / len(letters)
        if letters
        else 0.0
    )
    if non_latin_fraction > max_non_latin_fraction:
        return CoherenceResult(
            False,
            f"non-Latin script fraction {non_latin_fraction:.2f} "
            f"> {max_non_latin_fraction:.2f} (mixed-script gibberish)",
            non_latin_fraction,
        )
    if _looks_degenerate(stripped):
        return CoherenceResult(False, "degenerate repetition", non_latin_fraction)
    return CoherenceResult(True, "coherent", non_latin_fraction)


def _request_payload(
    model: str,
    prompt_text: str,
    max_tokens: int,
    temperature: float,
    extra_body: Json | None,
) -> Json:
    payload: Json = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        # Probe the thinking-OFF direct path: it is the fragile path the indexer
        # bug corrupts (thinking-ON can mask it by reasoning around the loss), and
        # it avoids reasoning consuming the whole token budget and emitting an
        # empty answer. Callers can override via --extra-body-json.
        "chat_template_kwargs": {"enable_thinking": False},
    }
    if extra_body:
        payload = {**payload, **extra_body}
    return payload


def run_long_context_coherence_gate(
    *,
    base_url: str,
    model: str,
    line_count: int = 280,
    concurrency: int = 8,
    repeat_count: int = 1,
    max_tokens: int = 384,
    temperature: float = 0.0,
    timeout: float = 900.0,
    request_retries: int = 1,
    max_non_latin_fraction: float = 0.15,
    extra_body: Json | None = None,
    post_func: Callable[..., Json] = post_json,
) -> Json:
    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")
    if repeat_count < 1:
        raise ValueError("repeat_count must be at least 1")

    prompt = build_long_context_prompt(
        name="arthur_long_context_coherence", line_count=line_count
    )
    payload = _request_payload(model, prompt.text, max_tokens, temperature, extra_body)
    total = concurrency * repeat_count

    def _run_one(index: int) -> Json:
        try:
            response = post_json_with_retries(
                base_url,
                "/v1/chat/completions",
                payload,
                timeout,
                request_retries=request_retries,
                post_func=post_func,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            return {
                "index": index,
                "ok": False,
                "recall_ok": False,
                "coherence_ok": False,
                "detail": f"request failed: {exc}",
            }
        text = assistant_text(response)
        recall_ok, recall_detail, _ = evaluate_long_context_response(
            response, prompt.required_terms
        )
        coherence = assess_english_coherence(
            text, max_non_latin_fraction=max_non_latin_fraction
        )
        return {
            "index": index,
            "ok": recall_ok and coherence.ok,
            "recall_ok": recall_ok,
            "coherence_ok": coherence.ok,
            "non_latin_fraction": round(coherence.non_latin_fraction, 4),
            "recall_detail": recall_detail,
            "coherence_detail": coherence.detail,
            "response_excerpt": text[:240],
        }

    rows: list[Json] = []
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_run_one, index) for index in range(total)]
        rows.extend(future.result() for future in as_completed(futures))
    rows.sort(key=lambda row: row["index"])

    failures = [row for row in rows if not row["ok"]]
    return {
        "case": prompt.name,
        "model": model,
        "line_count": line_count,
        "concurrency": concurrency,
        "repeat_count": repeat_count,
        "total_requests": total,
        "max_non_latin_fraction": max_non_latin_fraction,
        "passed": len(rows) - len(failures),
        "failures": len(failures),
        "ok": not failures,
        "prompt_sha256": prompt.sha256,
        "required_terms": list(prompt.required_terms),
        "rows": rows,
    }
