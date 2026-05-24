from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from ds4_harness.long_context_latency import (
    LatencyPrompt,
    StreamFunc,
    _as_float,
    _decode_tokens_per_second,
    _inter_chunk_stats,
    _max,
    _mean,
    _min,
    _numeric_sequence,
    _numeric_values,
    _prompt_excerpt,
    _run_stream_request,
    _sha256,
    _slug,
)
from ds4_harness.prefix_cache_probe import stream_chat_completion


Json = dict[str, Any]

DEFAULT_CASE_NAME = "frontier_context_sweep"
DEFAULT_FRONTIERS = (8192, 16384, 32768, 65536, 98304, 124000)
DEFAULT_MAX_SWEEP_TOKENS = 128


def parse_frontiers(value: str | list[int] | tuple[int, ...]) -> list[int]:
    if isinstance(value, str):
        raw_items = [item.strip() for item in value.split(",") if item.strip()]
    else:
        raw_items = [str(item) for item in value]
    if not raw_items:
        raise ValueError("at least one frontier is required")

    frontiers: list[int] = []
    for item in raw_items:
        try:
            frontier = int(item)
        except ValueError as exc:
            raise ValueError(f"frontiers must be positive integers: {item!r}") from exc
        if frontier < 1:
            raise ValueError("frontiers must be positive integers")
        if frontier in frontiers:
            raise ValueError(f"duplicate frontier: {frontier}")
        frontiers.append(frontier)
    return frontiers


def _cut_at_text_boundary(text: str, char_count: int) -> str:
    if char_count >= len(text):
        return text
    char_count = max(1, char_count)
    newline = text.rfind("\n", 0, char_count)
    if newline >= max(1, char_count // 2):
        return text[: newline + 1]
    whitespace = max(
        text.rfind(" ", 0, char_count),
        text.rfind("\t", 0, char_count),
    )
    if whitespace >= max(1, char_count // 2):
        return text[: whitespace + 1]
    return text[:char_count]


def _frontier_prompt_manifest(
    *,
    prompt_file: Path,
    prompt_name: str,
    prompt: LatencyPrompt,
    target_frontier_tokens: int,
    frontier_fraction: float,
) -> Json:
    return {
        "name": prompt_name,
        "source": "file_frontier",
        "prompt_file": str(prompt_file),
        "target_frontier_tokens": target_frontier_tokens,
        "frontier_fraction": round(frontier_fraction, 6),
        "sha256": prompt.sha256,
        "excerpt": _prompt_excerpt(prompt.text),
    }


def _build_frontier_prompts(prompt_file: Path, frontiers: list[int]) -> list[Json]:
    text = prompt_file.read_text(encoding="utf-8")
    prompt_name = _slug(prompt_file.stem)
    max_frontier = max(frontiers)
    prompts: list[Json] = []
    for frontier in frontiers:
        fraction = frontier / max_frontier
        char_count = len(text) if frontier == max_frontier else math.ceil(len(text) * fraction)
        prompt_text = _cut_at_text_boundary(text, char_count)
        prompt = LatencyPrompt(
            name=f"{prompt_name}_frontier_{frontier}",
            source="file_frontier",
            text=prompt_text,
            required_terms=(),
            prompt_file=str(prompt_file),
        )
        prompts.append(
            {
                "prompt": prompt,
                "prompt_name": prompt_name,
                "target_frontier_tokens": frontier,
                "frontier_fraction": fraction,
                "manifest": _frontier_prompt_manifest(
                    prompt_file=prompt_file,
                    prompt_name=prompt_name,
                    prompt=prompt,
                    target_frontier_tokens=frontier,
                    frontier_fraction=fraction,
                ),
            }
        )
    return prompts


def _input_tokens_per_second(*, prompt_tokens: Any, ttft_seconds: Any) -> float | None:
    tokens = _as_float(prompt_tokens)
    ttft = _as_float(ttft_seconds)
    if tokens is None or tokens <= 0 or ttft is None or ttft <= 0:
        return None
    return round(tokens / ttft, 6)


def _summarize_frontier_rows(rows: list[Json]) -> list[Json]:
    groups: dict[tuple[str, int], list[Json]] = {}
    for row in rows:
        if row.get("phase") != "measure":
            continue
        key = (
            str(row.get("prompt")),
            int(row.get("target_frontier_tokens") or 0),
        )
        groups.setdefault(key, []).append(row)

    summary: list[Json] = []
    for (prompt, target_frontier_tokens), group_rows in sorted(
        groups.items(), key=lambda item: (item[0][0], item[0][1])
    ):
        ttft = _numeric_values(group_rows, "ttft_seconds")
        elapsed = _numeric_values(group_rows, "elapsed_seconds")
        prompt_tokens = _numeric_values(group_rows, "prompt_tokens")
        completion_tokens = _numeric_values(group_rows, "completion_tokens")
        input_tps = _numeric_values(group_rows, "input_tokens_per_second")
        decode_tps = _numeric_values(group_rows, "decode_tokens_per_second")
        inter_chunk_samples = [
            sample
            for row in group_rows
            for sample in _numeric_sequence(row.get("inter_chunk_seconds"))
        ]
        summary.append(
            {
                "prompt": prompt,
                "target_frontier_tokens": target_frontier_tokens,
                "request_count": len(group_rows),
                "failure_count": sum(0 if row.get("ok") else 1 for row in group_rows),
                "ttft_seconds_min": _min(ttft),
                "ttft_seconds_mean": _mean(ttft),
                "ttft_seconds_max": _max(ttft),
                "elapsed_seconds_mean": _mean(elapsed),
                "elapsed_seconds_max": _max(elapsed),
                "prompt_tokens_mean": _mean(prompt_tokens),
                "completion_tokens_mean": _mean(completion_tokens),
                "input_tokens_per_second_mean": _mean(input_tps),
                "input_tokens_per_second_min": _min(input_tps),
                "input_tokens_per_second_max": _max(input_tps),
                "decode_tokens_per_second_mean": _mean(decode_tps),
                "decode_tokens_per_second_min": _min(decode_tps),
                "decode_tokens_per_second_max": _max(decode_tps),
                **_inter_chunk_stats(inter_chunk_samples),
            }
        )
    return summary


def run_frontier_context_sweep(
    *,
    base_url: str,
    model: str,
    variant: str,
    case_name: str = DEFAULT_CASE_NAME,
    prompt_files: list[Path] | None = None,
    frontiers: list[int] | None = None,
    repeat_count: int = 1,
    max_tokens: int = DEFAULT_MAX_SWEEP_TOKENS,
    temperature: float = 0.0,
    top_p: float = 1.0,
    thinking_mode: str = "non-thinking",
    timeout: float = 1800.0,
    headers: dict[str, str] | None = None,
    extra_body: Json | None = None,
    stream_func: StreamFunc = stream_chat_completion,
) -> Json:
    prompt_files = [] if prompt_files is None else list(prompt_files)
    frontiers = list(DEFAULT_FRONTIERS) if frontiers is None else parse_frontiers(frontiers)
    if repeat_count < 1:
        raise ValueError("repeat_count must be >= 1")
    if not prompt_files:
        raise ValueError("at least one prompt file is required")

    rows: list[Json] = []
    prompt_manifests: list[Json] = []
    for prompt_file in prompt_files:
        for item in _build_frontier_prompts(prompt_file, frontiers):
            prompt = item["prompt"]
            prompt_name = str(item["prompt_name"])
            target_frontier_tokens = int(item["target_frontier_tokens"])
            prompt_manifests.append(item["manifest"])
            for repeat_index in range(1, repeat_count + 1):
                row = _run_stream_request(
                    base_url=base_url,
                    model=model,
                    variant=variant,
                    case_name=case_name,
                    prompt=prompt,
                    cache_mode="cold",
                    concurrency=1,
                    repeat_index=repeat_index,
                    request_index=1,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    thinking_mode=thinking_mode,
                    timeout=timeout,
                    headers=headers,
                    extra_body=extra_body,
                    stream_func=stream_func,
                    probe_metadata_extra={
                        "target_frontier_tokens": target_frontier_tokens,
                        "frontier_fraction": item["frontier_fraction"],
                    },
                    row_extra={
                        "prompt": prompt_name,
                        "target_frontier_tokens": target_frontier_tokens,
                        "frontier_fraction": round(float(item["frontier_fraction"]), 6),
                        "prompt_sha256": _sha256(prompt.text),
                    },
                )
                row["input_tokens_per_second"] = _input_tokens_per_second(
                    prompt_tokens=row.get("prompt_tokens"),
                    ttft_seconds=row.get("ttft_seconds"),
                )
                if row.get("decode_tokens_per_second") is None:
                    row["decode_tokens_per_second"] = _decode_tokens_per_second(
                        completion_tokens=row.get("completion_tokens"),
                        ttft_seconds=row.get("ttft_seconds"),
                        elapsed_seconds=row.get("elapsed_seconds"),
                    )
                rows.append(row)

    rows.sort(
        key=lambda row: (
            str(row.get("prompt")),
            int(row.get("target_frontier_tokens") or 0),
            int(row.get("repeat") or 0),
        )
    )
    summary = _summarize_frontier_rows(rows)
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
        "frontiers": frontiers,
        "prompts": prompt_manifests,
        "summary": summary,
        "requests": rows,
    }


def write_frontier_context_sweep_markdown(path: Path, row: Json) -> None:
    lines = [
        "# Frontier Context Sweep",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- case: `{row.get('case')}`",
        f"- variant: `{row.get('variant')}`",
        f"- model: `{row.get('model')}`",
        f"- thinking_mode: `{row.get('thinking_mode')}`",
        f"- max_tokens: `{row.get('max_tokens')}`",
        f"- repeat_count: `{row.get('repeat_count')}`",
        "",
        "## Summary",
        "",
    ]
    headers = [
        "Prompt",
        "Target frontier tokens",
        "Requests",
        "Failures",
        "Prompt tokens mean",
        "TTFT mean s",
        "TTFT max s",
        "Input tok/s mean",
        "Decode tok/s mean",
        "ITL P95 s",
        "ITL P99 s",
        "ITL max s",
    ]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for item in row.get("summary", []):
        lines.append(
            "| "
            + " | ".join(
                str(value)
                for value in [
                    item.get("prompt"),
                    item.get("target_frontier_tokens"),
                    item.get("request_count"),
                    item.get("failure_count"),
                    item.get("prompt_tokens_mean"),
                    item.get("ttft_seconds_mean"),
                    item.get("ttft_seconds_max"),
                    item.get("input_tokens_per_second_mean"),
                    item.get("decode_tokens_per_second_mean"),
                    item.get("p95_inter_chunk_seconds"),
                    item.get("p99_inter_chunk_seconds"),
                    item.get("max_inter_chunk_seconds"),
                ]
            )
            + " |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
