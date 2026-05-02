from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from ds4_harness.client import post_json, post_json_with_retries
from ds4_harness.oracle import attach_prompt_token_ids, token_ids_from_tokenize_response


Json = dict[str, Any]
PostJson = Callable[[str, str, Json, float], Json]


@dataclass(frozen=True)
class CompletionOracleExportCase:
    name: str
    prompt: str
    max_tokens: int
    logprobs: int = 20
    temperature: float = 0.0

    def request(self, model: str, *, logprobs: int | None = None) -> Json:
        return {
            "model": model,
            "prompt": self.prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "logprobs": self.logprobs if logprobs is None else logprobs,
        }


def _long_prefill_prompt(lines: int = 260) -> str:
    rows = [
        "You are validating deterministic long-prefill behavior for DeepSeek V4.",
        "Read the numbered context and answer the final question in one sentence.",
        "",
    ]
    for index in range(1, lines + 1):
        rows.append(
            f"Line {index:03d}: subsystem={index % 7}, shard={index % 13}, "
            f"checksum={(index * 17) % 997}, note=stable validation context."
        )
    rows.extend(
        [
            "",
            "Question: Which validation context is being tested?",
            "Answer:",
        ]
    )
    return "\n".join(rows)


def default_completion_oracle_cases() -> list[CompletionOracleExportCase]:
    return [
        CompletionOracleExportCase(
            name="completion_short_math_logprobs20",
            prompt="Question: What is 7*8?\nAnswer:",
            max_tokens=16,
        ),
        CompletionOracleExportCase(
            name="completion_raw_intro_logprobs20",
            prompt=(
                "The following is a concise explanation of local LLM inference:\n"
            ),
            max_tokens=96,
        ),
        CompletionOracleExportCase(
            name="completion_translation_logprobs20",
            prompt=(
                "Translate to polished Simplified Chinese:\n"
                "Local inference can improve privacy and reduce latency, but it "
                "also shifts operational responsibility to the engineering team.\n"
                "Translation:"
            ),
            max_tokens=128,
        ),
        CompletionOracleExportCase(
            name="completion_code_probe_logprobs20",
            prompt=(
                "Write a Python function named normalize_slug that lowercases text, "
                "replaces non-alphanumeric runs with underscores, and strips leading "
                "or trailing underscores.\n"
            ),
            max_tokens=160,
        ),
        CompletionOracleExportCase(
            name="completion_long_prefill_2048_logprobs20",
            prompt=_long_prefill_prompt(),
            max_tokens=64,
        ),
    ]


def _case_map() -> dict[str, CompletionOracleExportCase]:
    return {case.name: case for case in default_completion_oracle_cases()}


def _selected_cases(
    case_names: list[str] | None,
) -> list[CompletionOracleExportCase]:
    if not case_names:
        return default_completion_oracle_cases()
    by_name = _case_map()
    missing = [name for name in case_names if name not in by_name]
    if missing:
        known = ", ".join(sorted(by_name))
        raise KeyError(f"unknown oracle export case(s): {missing}; known: {known}")
    return [by_name[name] for name in case_names]


def _write_json(path: Path, data: Json) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _summarize_response(response: Json) -> Json:
    choices = response.get("choices")
    choice = choices[0] if isinstance(choices, list) and choices else {}
    logprobs = choice.get("logprobs") if isinstance(choice, dict) else {}
    tokens = logprobs.get("tokens") if isinstance(logprobs, dict) else None
    top_logprobs = logprobs.get("top_logprobs") if isinstance(logprobs, dict) else None
    return {
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
        "generated_chars": len(str(choice.get("text") or ""))
        if isinstance(choice, dict)
        else 0,
        "generated_token_count": len(tokens) if isinstance(tokens, list) else None,
        "top_logprobs_steps": len(top_logprobs) if isinstance(top_logprobs, list) else None,
        "usage": response.get("usage"),
    }


def _write_summary_markdown(path: Path, rows: list[Json], model: str) -> None:
    passed = sum(1 for row in rows if row.get("ok"))
    lines = [
        "# Oracle Export Summary",
        "",
        f"- Model: `{model}`",
        f"- Cases: {len(rows)}",
        f"- Completed: {passed}/{len(rows)}",
        "",
        "| Case | Status | Tokens | Finish reason | Elapsed |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for row in rows:
        summary = row.get("response_summary") or {}
        lines.append(
            " | ".join(
                [
                    f"| `{row.get('name')}`",
                    "PASS" if row.get("ok") else "FAIL",
                    str(summary.get("generated_token_count") or "n/a"),
                    f"`{summary.get('finish_reason') or 'n/a'}`",
                    f"{row.get('elapsed_seconds', 0):.3f}s",
                ]
            )
            + " |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def export_completion_oracles(
    base_url: str,
    model: str,
    output_dir: Path,
    *,
    case_names: list[str] | None = None,
    timeout: float = 300.0,
    logprobs: int | None = None,
    stop_on_error: bool = False,
    request_retries: int = 0,
    post_json_func: PostJson = post_json,
) -> list[Json]:
    cases = _selected_cases(case_names)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[Json] = []

    for case in cases:
        request = case.request(model, logprobs=logprobs)
        started = time.time()
        row: Json = {
            "name": case.name,
            "path": "/v1/completions",
            "request": request,
        }
        try:
            tokenize_request = {"model": model, "prompt": case.prompt}
            tokenize_response = post_json_with_retries(
                base_url,
                "/tokenize",
                tokenize_request,
                timeout,
                request_retries=request_retries,
                post_func=post_json_func,
            )
            _write_json(
                output_dir / f"tokenize_{case.name}.json",
                tokenize_response,
            )
            response = post_json_with_retries(
                base_url,
                "/v1/completions",
                request,
                timeout,
                request_retries=request_retries,
                post_func=post_json_func,
            )
            response = attach_prompt_token_ids(
                response,
                token_ids_from_tokenize_response(tokenize_response),
            )
            elapsed = time.time() - started
            wrapped = {
                "name": case.name,
                "path": "/v1/completions",
                "status": 200,
                "elapsed_seconds": round(elapsed, 3),
                "request": request,
                "tokenize_request": tokenize_request,
                "tokenize_response": tokenize_response,
                "response": response,
            }
            row.update(
                {
                    "ok": True,
                    "status": 200,
                    "elapsed_seconds": round(elapsed, 3),
                    "response_summary": _summarize_response(response),
                }
            )
        except Exception as exc:
            elapsed = time.time() - started
            wrapped = {
                "name": case.name,
                "path": "/v1/completions",
                "status": "error",
                "elapsed_seconds": round(elapsed, 3),
                "request": request,
                "error": repr(exc),
            }
            row.update(
                {
                    "ok": False,
                    "status": "error",
                    "elapsed_seconds": round(elapsed, 3),
                    "error": repr(exc),
                }
            )
        _write_json(output_dir / f"{case.name}.json", wrapped)
        rows.append(row)
        if stop_on_error and not row.get("ok"):
            break

    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "model": model,
        "base_url": base_url,
        "case_count": len(rows),
        "success_count": sum(1 for row in rows if row.get("ok")),
        "results": rows,
        "files": sorted(path.name for path in output_dir.glob("*.json")),
    }
    _write_json(output_dir / "oracle_export_summary.json", summary)
    _write_summary_markdown(output_dir / "oracle_export_summary.md", rows, model)
    return rows
