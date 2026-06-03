"""Utilities for summarizing vLLM scheduler trace JSONL files."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

Json = dict[str, Any]


def _round_float(value: float | None, digits: int = 6) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _read_events(path: Path) -> list[Json]:
    events: list[Json] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if not isinstance(item, dict):
            raise ValueError(f"scheduler trace row is not an object: {line[:80]}")
        events.append(item)
    return events


def _request_suffix(request_id: str) -> str:
    return request_id.rsplit("-", 1)[-1] if "-" in request_id else request_id


def _segment_signature(event: Json) -> tuple[tuple[tuple[str, int], ...], tuple[tuple]]:
    phase_counts: Counter[str] = Counter()
    scheduled_sig = []
    for row in event.get("scheduled_requests", []):
        phase = str(row.get("phase") or "")
        phase_counts[phase] += 1
        scheduled_sig.append(
            (
                _request_suffix(str(row.get("request_id") or "")),
                phase,
                int(row.get("scheduled_tokens") or 0),
                bool(row.get("crosses_prefill_boundary") or False),
            )
        )
    return tuple(sorted(phase_counts.items())), tuple(scheduled_sig)


def build_scheduler_trace_report(path: Path) -> Json:
    """Build a compact summary for one scheduler trace JSONL file."""

    events = _read_events(path)
    if not events:
        return {
            "trace_path": str(path),
            "event_count": 0,
            "span_seconds": 0.0,
            "requests": [],
            "segments": [],
            "overlap": {},
        }

    first_ts = float(events[0].get("timestamp", 0.0))
    last_ts = float(events[-1].get("timestamp", first_ts))
    request_rows: dict[str, Json] = defaultdict(
        lambda: {
            "request_id": "",
            "request_suffix": "",
            "step_count": 0,
            "scheduled_tokens": 0,
            "phases": Counter(),
            "tokens_by_phase": Counter(),
            "first_step": None,
            "last_step": None,
            "first_timestamp": None,
            "last_timestamp": None,
        }
    )
    overlap_steps = 0
    overlap_decode_tokens = 0
    overlap_prefill_tokens = 0
    overlap_prefill_chunk_sizes: Counter[int] = Counter()
    isolated_decode_steps = 0

    segments: list[Json] = []
    active_signature: tuple[tuple[tuple[str, int], ...], tuple[tuple]] | None = None
    active_start_event: Json | None = None
    previous_event: Json | None = None

    for event in events:
        step = int(event.get("step", 0))
        timestamp = float(event.get("timestamp", first_ts))
        phase_counts: Counter[str] = Counter()
        token_counts: Counter[str] = Counter()
        for row in event.get("scheduled_requests", []):
            request_id = str(row.get("request_id") or "")
            phase = str(row.get("phase") or "")
            tokens = int(row.get("scheduled_tokens") or 0)
            phase_counts[phase] += 1
            token_counts[phase] += tokens

            req = request_rows[request_id]
            req["request_id"] = request_id
            req["request_suffix"] = _request_suffix(request_id)
            req["step_count"] += 1
            req["scheduled_tokens"] += tokens
            req["phases"][phase] += 1
            req["tokens_by_phase"][phase] += tokens
            req["first_step"] = step if req["first_step"] is None else req["first_step"]
            req["last_step"] = step
            req["first_timestamp"] = (
                timestamp if req["first_timestamp"] is None else req["first_timestamp"]
            )
            req["last_timestamp"] = timestamp

        has_decode = phase_counts["decode"] > 0
        has_prefill = phase_counts["prefill"] > 0
        if has_decode and has_prefill:
            overlap_steps += 1
            overlap_decode_tokens += token_counts["decode"]
            overlap_prefill_tokens += token_counts["prefill"]
            for row in event.get("scheduled_requests", []):
                if row.get("phase") == "prefill":
                    overlap_prefill_chunk_sizes[int(row.get("scheduled_tokens") or 0)] += 1
        elif has_decode:
            isolated_decode_steps += 1

        signature = _segment_signature(event)
        if signature != active_signature:
            if active_signature is not None and active_start_event is not None:
                assert previous_event is not None
                segments.append(
                    _build_segment(
                        active_start_event,
                        previous_event,
                        active_signature,
                        first_ts,
                    )
                )
            active_signature = signature
            active_start_event = event
        previous_event = event

    if active_signature is not None and active_start_event is not None:
        assert previous_event is not None
        segments.append(
            _build_segment(active_start_event, previous_event, active_signature, first_ts)
        )

    requests = []
    for request_id, row in sorted(
        request_rows.items(), key=lambda item: (item[1]["first_timestamp"], item[0])
    ):
        if not request_id:
            continue
        first_request_ts = row["first_timestamp"]
        last_request_ts = row["last_timestamp"]
        requests.append(
            {
                "request_id": request_id,
                "request_suffix": row["request_suffix"],
                "step_count": row["step_count"],
                "scheduled_tokens": row["scheduled_tokens"],
                "phases": dict(row["phases"]),
                "tokens_by_phase": dict(row["tokens_by_phase"]),
                "first_step": row["first_step"],
                "last_step": row["last_step"],
                "first_offset_seconds": _round_float(first_request_ts - first_ts),
                "last_offset_seconds": _round_float(last_request_ts - first_ts),
                "span_seconds": _round_float(last_request_ts - first_request_ts),
            }
        )

    return {
        "trace_path": str(path),
        "event_count": len(events),
        "span_seconds": _round_float(last_ts - first_ts),
        "token_budget_max": max(
            int(event.get("token_budget_before_schedule") or 0) for event in events
        ),
        "total_scheduled_tokens_max": max(
            int(event.get("total_num_scheduled_tokens") or 0) for event in events
        ),
        "requests": requests,
        "segments": segments,
        "overlap": {
            "decode_prefill_overlap_steps": overlap_steps,
            "overlap_decode_tokens": overlap_decode_tokens,
            "overlap_prefill_tokens": overlap_prefill_tokens,
            "overlap_prefill_chunk_sizes": dict(
                sorted(overlap_prefill_chunk_sizes.items())
            ),
            "isolated_decode_steps": isolated_decode_steps,
        },
    }


def _build_segment(
    start_event: Json,
    end_event: Json,
    signature: tuple[tuple[tuple[str, int], ...], tuple[tuple]],
    first_ts: float,
) -> Json:
    phase_counts, scheduled_sig = signature
    start_ts = float(start_event.get("timestamp", first_ts))
    end_ts = float(end_event.get("timestamp", start_ts))
    return {
        "start_step": int(start_event.get("step", 0)),
        "end_step": int(end_event.get("step", 0)),
        "start_offset_seconds": _round_float(start_ts - first_ts),
        "end_offset_seconds": _round_float(end_ts - first_ts),
        "duration_seconds": _round_float(end_ts - start_ts),
        "phase_counts": dict(phase_counts),
        "scheduled_signature": [
            {
                "request_suffix": row[0],
                "phase": row[1],
                "scheduled_tokens": row[2],
                "crosses_prefill_boundary": row[3],
            }
            for row in scheduled_sig
        ],
    }


def write_scheduler_trace_report_json(path: Path, report: Json) -> None:
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if str(path) == "-":
        sys.stdout.write(text)
        return
    path.write_text(text, encoding="utf-8")


def write_scheduler_trace_report_markdown(path: Path, report: Json) -> None:
    lines = [
        "# Scheduler Trace Summary",
        "",
        f"- Trace: `{Path(str(report.get('trace_path', ''))).name}`",
        f"- Events: `{report.get('event_count', 0)}`",
        f"- Span seconds: `{report.get('span_seconds', 0)}`",
        f"- Max token budget: `{report.get('token_budget_max', 0)}`",
        f"- Max scheduled tokens: `{report.get('total_scheduled_tokens_max', 0)}`",
        "",
        "## Requests",
        "",
        "| Request | Steps | Tokens | Phases | Span s |",
        "| --- | ---: | ---: | --- | ---: |",
    ]
    for row in report.get("requests", []):
        lines.append(
            "| {request} | {steps} | {tokens} | {phases} | {span} |".format(
                request=row.get("request_suffix", ""),
                steps=row.get("step_count", ""),
                tokens=row.get("scheduled_tokens", ""),
                phases=json.dumps(row.get("tokens_by_phase", {}), sort_keys=True),
                span=row.get("span_seconds", ""),
            )
        )

    overlap = report.get("overlap", {})
    lines.extend(
        [
            "",
            "## Decode/Prefill Overlap",
            "",
            f"- overlap steps: `{overlap.get('decode_prefill_overlap_steps', 0)}`",
            f"- overlap decode tokens: `{overlap.get('overlap_decode_tokens', 0)}`",
            f"- overlap prefill tokens: `{overlap.get('overlap_prefill_tokens', 0)}`",
            "- overlap prefill chunk sizes: "
            f"`{json.dumps(overlap.get('overlap_prefill_chunk_sizes', {}), sort_keys=True)}`",
            f"- isolated decode steps: `{overlap.get('isolated_decode_steps', 0)}`",
            "",
            "## Segments",
            "",
            "| Steps | Duration s | Phase Counts | Scheduled Signature |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for segment in report.get("segments", []):
        lines.append(
            "| {start}-{end} | {duration} | {phases} | {sig} |".format(
                start=segment.get("start_step", ""),
                end=segment.get("end_step", ""),
                duration=segment.get("duration_seconds", ""),
                phases=json.dumps(segment.get("phase_counts", {}), sort_keys=True),
                sig=json.dumps(segment.get("scheduled_signature", []), sort_keys=True),
            )
        )
    text = "\n".join(lines) + "\n"
    if str(path) == "-":
        sys.stdout.write(text)
        return
    path.write_text(text, encoding="utf-8")
