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
        "mtp\tlong_context_latency_matrix\t0\tmtp/long_context_latency_matrix\n"
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
        primary / "mtp/long_context_latency_matrix/gpu_stats_summary.json",
        {
            "available": True,
            "sample_count": 12,
            "overall": {
                "gpu_utilization_percent_avg": 91.4,
                "gpu_utilization_percent_max": 98.0,
                "memory_used_percent_max": 87.6,
                "temperature_gpu_c_max": 73.0,
                "temperature_memory_c_max": 82.0,
                "power_draw_w_max": 541.0,
            },
        },
    )
    write_json(
        primary / "mtp/long_context_latency_matrix/runtime_stats_summary.json",
        {
            "metrics": {
                "available": True,
                "sample_count": 6,
                "running_requests_max": 2.0,
                "waiting_requests_max": 1.0,
                "gpu_kv_cache_usage_percent_max": 86.0,
                "preemptions_delta": 0.0,
            },
            "serve_log": {
                "available": True,
                "samples": 3,
                "prefill_throughput_tok_s_avg": 1600.0,
                "decode_throughput_tok_s_avg": 72.0,
                "error_signal_count": 0,
                "cuda_error_count": 0,
                "nccl_error_count": 0,
                "driver_error_count": 0,
            },
        },
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
    assert primary_summary["monitoring"][0]["gpu_utilization_avg"] == 91.4
    assert primary_summary["monitoring"][0]["serve_log_error_signals"] == 0
    assert primary_summary["monitoring"][0]["runtime_running_requests_max"] == 2.0
    assert summary["runs"][1]["prefix_cache_stress"][0]["concurrent_hit_rate_mean"] == 0.75

    markdown_path = tmp_path / "summary.md"
    write_summary_markdown(markdown_path, summary)
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Decode-Concurrency" in markdown
    assert "Runtime Monitoring" in markdown
    assert "GPU Util Avg" in markdown
    assert "CUDA Errors" in markdown
    assert "Prefix Cache Stress" in markdown
    assert "already-started decode stream fairness" in markdown


def test_user_feedback_matrix_summary_collects_prefix_cache_diagnostic_sweep(tmp_path):
    prefix = tmp_path / "prefix_cache"
    prefix.mkdir()
    filler_400 = prefix / "default/filler_400"
    filler_800 = prefix / "default/filler_800"
    (prefix / "diagnostic_cases.tsv").write_text(
        "case\tfiller_words\texit_code\tartifact_dir\n"
        f"default\t400\t0\t{filler_400}\n"
        f"default\t800\t0\t{filler_800}\n",
        encoding="utf-8",
    )
    for filler, hit_rate, root in (
        (400, 0.466, filler_400),
        (800, 0.727, filler_800),
    ):
        write_json(
            root / "mtp1/prefix_cache_stress/prefix_cache_stress.json",
            {
                "ok": True,
                "case": "user_feedback_prefix_cache_http_metrics_stress",
                "health_status": 200,
                "summary": {
                    "trial_count": 5,
                    "failure_count": 0,
                    "solo_hit_rate_mean": 0.68,
                    "concurrent_hit_rate_mean": hit_rate,
                },
                "config": {"filler_words": filler},
            },
        )

    summary = summarize_runs([("prefix_cache", prefix)])

    assert summary["ok"] is True
    rows = summary["runs"][0]["prefix_cache_stress"]
    assert [(row["filler_words"], row["concurrent_hit_rate_mean"]) for row in rows] == [
        (400, 0.466),
        (800, 0.727),
    ]

    markdown_path = tmp_path / "summary.md"
    write_summary_markdown(markdown_path, summary)
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Filler Words" in markdown
    assert "400" in markdown
    assert "800" in markdown
