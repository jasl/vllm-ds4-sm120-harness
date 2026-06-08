import json

from ds4_harness.decode_throughput_probe import (
    DecodeProbeSeriesSpec,
    parse_spec_decode_counters,
    run_decode_throughput_probe,
    summarize_decode_throughput_probe,
    write_decode_throughput_probe_markdown,
)


METRICS_TEXT = """
# HELP vllm:spec_decode_num_drafts_total Number of spec decoding drafts.
vllm:spec_decode_num_drafts_total{engine="0",model_name="m"} 100
vllm:spec_decode_num_draft_tokens_total{engine="0",model_name="m"} 200
vllm:spec_decode_num_accepted_tokens_total{engine="0",model_name="m"} 130
vllm:spec_decode_num_accepted_tokens_per_pos_total{engine="0",model_name="m",position="0"} 80
vllm:spec_decode_num_accepted_tokens_per_pos_total{engine="0",model_name="m",position="1"} 50
"""


def test_parse_spec_decode_counters_extracts_mtp_metrics():
    counters = parse_spec_decode_counters(METRICS_TEXT)

    assert counters == {
        "drafts": 100.0,
        "draft_tokens": 200.0,
        "accepted": 130.0,
        "accepted_pos0": 80.0,
        "accepted_pos1": 50.0,
    }


def test_decode_throughput_summary_groups_by_series_and_slot():
    rows = [
        {
            "series": "cycle",
            "prompt_slot": 0,
            "tok_s": 34.0,
            "completion_tokens": 512,
            "elapsed_ms": 15000,
            "mtp_delta": {
                "drafts": 250,
                "draft_tokens": 500,
                "accepted": 260,
                "accepted_pos0": 175,
                "accepted_pos1": 85,
            },
        },
        {
            "series": "cycle",
            "prompt_slot": 1,
            "tok_s": 40.0,
            "completion_tokens": 512,
            "elapsed_ms": 12800,
            "mtp_delta": {
                "drafts": 210,
                "draft_tokens": 420,
                "accepted": 300,
                "accepted_pos0": 185,
                "accepted_pos1": 115,
            },
        },
        {
            "series": "cycle",
            "prompt_slot": 1,
            "tok_s": 38.0,
            "completion_tokens": 512,
            "elapsed_ms": 13473,
            "mtp_delta": {
                "drafts": 220,
                "draft_tokens": 440,
                "accepted": 290,
                "accepted_pos0": 180,
                "accepted_pos1": 110,
            },
        },
    ]

    summary = summarize_decode_throughput_probe(
        rows,
        slow_tok_s_threshold=36.0,
    )

    assert summary["request_count"] == 3
    assert summary["slow_request_count"] == 1
    assert summary["series"][0]["series"] == "cycle"
    assert summary["series"][0]["mean_tok_s"] == 37.333333
    assert summary["series"][0]["slow_request_indices"] == [1]
    by_slot = {row["prompt_slot"]: row for row in summary["series"][0]["slots"]}
    assert by_slot[0]["mean_tok_s"] == 34.0
    assert by_slot[0]["mean_acceptance_ratio"] == 0.52
    assert by_slot[1]["mean_tok_s"] == 39.0
    assert by_slot[1]["mean_acceptance_ratio"] == 0.686688


def test_run_decode_throughput_probe_records_per_request_mtp_delta():
    metric_snapshots = iter(
        [
            """
vllm:spec_decode_num_drafts_total{engine="0"} 10
vllm:spec_decode_num_draft_tokens_total{engine="0"} 20
vllm:spec_decode_num_accepted_tokens_total{engine="0"} 12
vllm:spec_decode_num_accepted_tokens_per_pos_total{engine="0",position="0"} 8
vllm:spec_decode_num_accepted_tokens_per_pos_total{engine="0",position="1"} 4
""",
            """
vllm:spec_decode_num_drafts_total{engine="0"} 110
vllm:spec_decode_num_draft_tokens_total{engine="0"} 220
vllm:spec_decode_num_accepted_tokens_total{engine="0"} 152
vllm:spec_decode_num_accepted_tokens_per_pos_total{engine="0",position="0"} 88
vllm:spec_decode_num_accepted_tokens_per_pos_total{engine="0",position="1"} 64
""",
        ]
    )

    def fake_metrics(base_url, timeout):
        return next(metric_snapshots)

    def fake_request(base_url, payload, timeout):
        assert payload["max_tokens"] == 512
        assert payload["temperature"] == 1.0
        return {
            "elapsed_seconds": 10.0,
            "response": {
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {"content": "done"},
                    }
                ],
                "usage": {
                    "prompt_tokens": 16,
                    "completion_tokens": 512,
                    "total_tokens": 528,
                },
            },
        }

    row = run_decode_throughput_probe(
        base_url="http://127.0.0.1:8000",
        model="model",
        series_specs=[DecodeProbeSeriesSpec("fixed", "fixed", 1.0, 1)],
        request_func=fake_request,
        metrics_func=fake_metrics,
    )

    request = row["requests"][0]
    assert request["tok_s"] == 51.2
    assert request["mtp_delta"] == {
        "drafts": 100.0,
        "draft_tokens": 200.0,
        "accepted": 140.0,
        "accepted_pos0": 80.0,
        "accepted_pos1": 60.0,
    }
    assert request["acceptance_ratio"] == 0.7
    assert request["pos0_acceptance"] == 0.8
    assert request["pos1_acceptance"] == 0.6
    assert row["summary"]["series"][0]["mean_tok_s"] == 51.2
    assert row["summary"]["series"][0]["mean_acceptance_ratio"] == 0.7


def test_decode_throughput_markdown_includes_acceptance_table(tmp_path):
    row = {
        "case": "gb10_seq_c1",
        "ok": True,
        "variant": "mtp2",
        "summary": {
            "request_count": 1,
            "slow_request_count": 0,
            "series": [
                {
                    "series": "fixed",
                    "request_count": 1,
                    "mean_tok_s": 40.0,
                    "min_tok_s": 40.0,
                    "max_tok_s": 40.0,
                    "mean_acceptance_ratio": 0.7,
                    "slow_request_indices": [],
                    "slots": [],
                }
            ],
        },
        "requests": [],
    }
    output = tmp_path / "decode.md"

    write_decode_throughput_probe_markdown(output, row)

    text = output.read_text(encoding="utf-8")
    assert "# Decode Throughput Sequential Probe" in text
    assert "| fixed | 1 | 40.0 | 40.0 | 40.0 | 0.7 |  |" in text
    assert json.dumps(row["ok"]).lower() in text
