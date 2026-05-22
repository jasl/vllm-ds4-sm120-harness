from __future__ import annotations

import json
from pathlib import Path

from ds4_harness.user_feedback_matrix_summary import (
    summarize_runs,
    write_summary_markdown,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_user_feedback_matrix_summary_collects_tradeoff_metrics(tmp_path):
    primary = tmp_path / "primary"
    prefix = tmp_path / "prefix_cache"
    primary.mkdir()
    prefix.mkdir()
    (primary / "phase_exit_codes.tsv").write_text(
        "variant\tphase\texit_code\tartifact_dir\n"
        "mtp\tlong_context_latency_matrix\t0\t/a\n"
        "mtp\tlong_context_decode_concurrency\t0\t/b\n"
        "mtp\tlong_context_mixed_arrival\t0\t/c\n"
        "mtp\tstreaming_pressure_matrix\t0\t/d\n"
        "mtp\tbench_hf_mt_bench\t0\t/e\n"
        "mtp\teval_gsm8k\t0\t/f\n"
        "mtp\tbench_random_prefill_sweep\t0\t/g\n",
        encoding="utf-8",
    )
    (prefix / "phase_exit_codes.tsv").write_text(
        "variant\tphase\texit_code\tartifact_dir\n"
        "mtp1\tprefix_cache_stress\t0\t/h\n",
        encoding="utf-8",
    )

    latency_row = {
        "prompt": "synthetic_4000_lines",
        "cache_mode": "cold",
        "concurrency": 2,
        "request_count": 6,
        "failure_count": 0,
        "ttft_seconds_mean": 47.994,
        "ttft_seconds_max": 64.595,
        "decode_tokens_per_second_mean": 61.947,
        "decode_tokens_per_second_min": 20.741,
        "decode_tokens_per_second_max": 108.273,
        "decode_tps_min_to_max_ratio": 0.192,
        "p95_inter_chunk_seconds": 0.139,
        "p99_inter_chunk_seconds": 0.142,
        "max_inter_chunk_seconds": 0.142,
        "prompt_tokens_mean": 124080,
    }
    write_json(
        primary / "mtp/long_context_latency_matrix/long_context_latency_matrix.json",
        {"summary": [latency_row]},
    )
    write_json(
        primary
        / "mtp/long_context_decode_concurrency/long_context_decode_concurrency.json",
        {"summary": [latency_row | {"decode_tokens_per_second_min": 18.834}]},
    )
    write_json(
        primary / "mtp/long_context_mixed_arrival/long_context_mixed_arrival.json",
        {
            "summary": [
                {
                    "case": "decode_then_59k",
                    "request_count": 6,
                    "failure_count": 0,
                    "primary_ttft_seconds_mean": 12.57,
                    "secondary_ttft_seconds_mean": 14.18,
                    "decode_tps_min_to_max_ratio": 0.102,
                    "secondary_p95_inter_chunk_seconds": 0.022,
                    "secondary_p99_inter_chunk_seconds": 0.024,
                    "secondary_start_after_primary_ttft_seconds": 0.001,
                }
            ]
        },
    )
    write_json(
        primary / "mtp/streaming_pressure_matrix/streaming_pressure_matrix.json",
        {
            "summary": {
                "case_count": 4,
                "request_count": 36,
                "failure_count": 0,
                "slow_case_count": 0,
                "max_ttft_seconds": 64.5,
                "max_elapsed_seconds": 64.7,
                "p95_inter_chunk_seconds": 0.7,
                "p99_inter_chunk_seconds": 1.1,
                "max_inter_chunk_seconds": 1.4,
            }
        },
    )
    write_json(
        primary / "mtp/bench_hf_mt_bench/bench.json",
        [
            {
                "concurrency": 4,
                "metrics": {
                    "successful_requests": 80,
                    "output_token_throughput_tok_s": 392.73,
                    "mean_ttft_ms": 100.93,
                    "p99_ttft_ms": 304.99,
                    "p99_itl_ms": 44.68,
                    "spec_acceptance_rate_percent": 68.74,
                },
            }
        ],
    )
    write_json(
        primary / "mtp/eval_gsm8k/lm_eval_summary.json",
        {
            "tasks": [
                {
                    "task": "gsm8k",
                    "exact_match_flexible": 0.965,
                    "exact_match_strict": 0.935,
                }
            ]
        },
    )
    write_json(
        primary / "mtp/bench_random_prefill_sweep/prefill_sweep_summary.json",
        {
            "rows": [
                {
                    "case": "isl65536_osl1",
                    "ok": True,
                    "input_token_throughput_tok_s": 4577.34,
                    "mean_ttft_ms": 14317.64,
                    "p99_ttft_ms": 14400.01,
                    "successful_requests": 8,
                }
            ]
        },
    )
    write_json(
        prefix / "mtp1/prefix_cache_stress/prefix_cache_stress.json",
        {
            "ok": True,
            "health_status": 200,
            "summary": {
                "trial_count": 5,
                "failure_count": 0,
                "solo_hit_rate_mean": 0.8,
                "concurrent_hit_rate_mean": 0.75,
            },
        },
    )

    summary = summarize_runs([("primary", primary), ("prefix_cache", prefix)])

    assert summary["ok"] is True
    primary_summary = summary["runs"][0]
    assert primary_summary["latency"][0]["ttft_mean_s"] == 47.994
    assert primary_summary["decode_concurrency"][0]["decode_min_tps"] == 18.834
    assert primary_summary["short_bench"][0]["output_tps"] == 392.73
    assert summary["runs"][1]["prefix_cache_stress"][0]["concurrent_hit_rate_mean"] == 0.75

    markdown_path = tmp_path / "summary.md"
    write_summary_markdown(markdown_path, summary)
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Decode-Concurrency" in markdown
    assert "Prefix Cache Stress" in markdown
    assert "already-started decode stream fairness" in markdown
