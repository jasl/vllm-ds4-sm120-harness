import json

from ds4_harness.scheduler_trace import (
    build_scheduler_trace_report,
    write_scheduler_trace_report_markdown,
)


def _write_trace(path, rows):
    path.write_text(
        "\n".join(json.dumps(row, separators=(",", ":")) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_scheduler_trace_report_groups_decode_prefill_overlap(tmp_path):
    trace = tmp_path / "scheduler_trace.jsonl"
    _write_trace(
        trace,
        [
            {
                "step": 0,
                "timestamp": 10.0,
                "token_budget_before_schedule": 4096,
                "total_num_scheduled_tokens": 4096,
                "scheduled_requests": [
                    {
                        "request_id": "chatcmpl-primary-a",
                        "phase": "prefill",
                        "scheduled_tokens": 4096,
                    }
                ],
            },
            {
                "step": 1,
                "timestamp": 11.0,
                "token_budget_before_schedule": 4096,
                "total_num_scheduled_tokens": 259,
                "scheduled_requests": [
                    {
                        "request_id": "chatcmpl-primary-a",
                        "phase": "decode",
                        "scheduled_tokens": 3,
                    },
                    {
                        "request_id": "chatcmpl-secondary-b",
                        "phase": "prefill",
                        "scheduled_tokens": 256,
                    },
                ],
            },
            {
                "step": 2,
                "timestamp": 11.1,
                "token_budget_before_schedule": 4096,
                "total_num_scheduled_tokens": 259,
                "scheduled_requests": [
                    {
                        "request_id": "chatcmpl-primary-a",
                        "phase": "decode",
                        "scheduled_tokens": 3,
                    },
                    {
                        "request_id": "chatcmpl-secondary-b",
                        "phase": "prefill",
                        "scheduled_tokens": 256,
                    },
                ],
            },
            {
                "step": 3,
                "timestamp": 12.0,
                "token_budget_before_schedule": 4096,
                "total_num_scheduled_tokens": 3,
                "scheduled_requests": [
                    {
                        "request_id": "chatcmpl-secondary-b",
                        "phase": "decode",
                        "scheduled_tokens": 3,
                    }
                ],
            },
        ],
    )

    report = build_scheduler_trace_report(trace)

    assert report["event_count"] == 4
    assert report["span_seconds"] == 2.0
    assert report["overlap"] == {
        "decode_prefill_overlap_steps": 2,
        "overlap_decode_tokens": 6,
        "overlap_prefill_tokens": 512,
        "overlap_prefill_chunk_sizes": {256: 2},
        "isolated_decode_steps": 1,
    }
    assert report["requests"][0]["tokens_by_phase"] == {"decode": 6, "prefill": 4096}
    assert report["requests"][1]["tokens_by_phase"] == {"decode": 3, "prefill": 512}
    assert [segment["start_step"] for segment in report["segments"]] == [0, 1, 3]


def test_scheduler_trace_markdown_includes_overlap_summary(tmp_path):
    trace = tmp_path / "scheduler_trace.jsonl"
    markdown = tmp_path / "scheduler_trace.md"
    _write_trace(
        trace,
        [
            {
                "step": 0,
                "timestamp": 1.0,
                "token_budget_before_schedule": 4,
                "total_num_scheduled_tokens": 3,
                "scheduled_requests": [
                    {
                        "request_id": "req-a",
                        "phase": "decode",
                        "scheduled_tokens": 1,
                    },
                    {
                        "request_id": "req-b",
                        "phase": "prefill",
                        "scheduled_tokens": 2,
                    },
                ],
            }
        ],
    )

    report = build_scheduler_trace_report(trace)
    write_scheduler_trace_report_markdown(markdown, report)

    text = markdown.read_text(encoding="utf-8")
    assert "Scheduler Trace Summary" in text
    assert "overlap steps" in text
    assert '"2": 1' in text
