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
        "mtp\tbench_random_8000x1000\t0\t/k\n"
        "mtp\tbench_random_256x256\t0\t/l\n"
        "mtp\teval_gsm8k\t0\t/f\n"
        "mtp\tbench_random_prefill_sweep\t0\t/g\n"
        "mtp\tfrontier_context_sweep\t0\t/i\n"
        "mtp\tds4_story_recall_semantic\t0\t/j\n",
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
                    "spec_acceptance_length": 1.42,
                    "spec_per_position_acceptance_percent": {"0": 81.2, "1": 56.3},
                },
            }
        ],
    )
    write_json(
        primary / "mtp/bench_random_8000x1000/bench.json",
        [
            {
                "concurrency": 4,
                "metrics": {
                    "successful_requests": 80,
                    "output_token_throughput_tok_s": 198.62,
                    "mean_ttft_ms": 2207.44,
                    "p99_ttft_ms": 3707.22,
                    "p99_itl_ms": 85.42,
                    "spec_acceptance_rate_percent": 70.11,
                    "spec_acceptance_length": 1.38,
                    "spec_per_position_acceptance_percent": {"0": 82.0, "1": 52.0},
                },
            }
        ],
    )
    write_json(
        primary / "mtp/bench_random_256x256/bench.json",
        [
            {
                "concurrency": 16,
                "metrics": {
                    "successful_requests": 80,
                    "output_token_throughput_tok_s": 360.51,
                    "mean_ttft_ms": 187.44,
                    "p99_ttft_ms": 407.22,
                    "p99_itl_ms": 35.42,
                    "spec_acceptance_rate_percent": 72.11,
                    "spec_acceptance_length": 1.51,
                    "spec_per_position_acceptance_percent": {"0": 84.2, "1": 58.4},
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
        primary / "mtp/frontier_context_sweep/frontier_context_sweep.json",
        {
            "summary": [
                {
                    "prompt": "ds4_story_recall",
                    "target_frontier_tokens": 65536,
                    "request_count": 1,
                    "failure_count": 0,
                    "prompt_tokens_mean": 64200,
                    "ttft_seconds_mean": 12.5,
                    "ttft_seconds_max": 12.7,
                    "input_tokens_per_second_mean": 5136.0,
                    "decode_tokens_per_second_mean": 41.2,
                    "p95_inter_chunk_seconds": 0.2,
                    "p99_inter_chunk_seconds": 0.3,
                    "max_inter_chunk_seconds": 0.4,
                }
            ]
        },
    )
    write_json(
        primary / "mtp/ds4_story_recall_semantic/long_context_latency_matrix.json",
        {
            "summary": [
                {
                    "prompt": "ds4_story_recall",
                    "cache_mode": "cold",
                    "concurrency": 1,
                    "request_count": 1,
                    "failure_count": 0,
                    "ttft_seconds_mean": 6.1,
                    "ttft_seconds_max": 6.1,
                    "decode_tokens_per_second_mean": 84.0,
                    "p99_inter_chunk_seconds": 0.02,
                    "prompt_tokens_mean": 30478,
                }
            ],
            "requests": [
                {
                    "phase": "measure",
                    "prompt": "ds4_story_recall",
                    "ok": True,
                    "semantic_check": "ds4_story_recall",
                    "story_recall_matched_count": 16,
                    "story_recall_missing": [],
                    "finish_reason": "stop",
                }
            ],
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
    write_json(
        primary / "prefill_decode_gate/prefill_decode_regression_gate.json",
        {
            "ok": True,
            "variant": "mtp",
            "regression_count": 0,
            "thresholds": {
                "min_long_c2_decode_min_max_ratio": 0.2,
                "max_long_c2_itl_p99_seconds": 1.0,
                "max_mixed_secondary_itl_p99_seconds": 1.0,
                "max_streaming_itl_p99_seconds": 2.0,
            },
        },
    )

    summary = summarize_runs([("primary", primary), ("prefix_cache", prefix)])

    assert summary["ok"] is True
    primary_summary = summary["runs"][0]
    assert primary_summary["latency"][0]["ttft_mean_s"] == 47.994
    assert primary_summary["decode_concurrency"][0]["decode_min_tps"] == 18.834
    assert primary_summary["short_bench"][0]["output_tps"] == 392.73
    assert primary_summary["short_bench"][0]["spec_acceptance_length"] == 1.42
    assert primary_summary["short_bench"][0]["spec_per_position_acceptance_percent"] == {
        "0": 81.2,
        "1": 56.3,
    }
    assert primary_summary["random_8000x1000_bench"][0]["output_tps"] == 198.62
    assert primary_summary["random_256x256_bench"][0]["output_tps"] == 360.51
    assert primary_summary["random_256x256_bench"][0]["spec_acceptance_length"] == 1.51
    assert primary_summary["frontier_context_sweep"][0]["input_tps"] == 5136.0
    assert primary_summary["story_recall_semantic"][0]["matched_min"] == 16
    assert primary_summary["monitoring"][0]["gpu_utilization_avg"] == 91.4
    assert primary_summary["monitoring"][0]["serve_log_error_signals"] == 0
    assert primary_summary["monitoring"][0]["runtime_running_requests_max"] == 2.0
    assert primary_summary["prefill_decode_gate"] == [
        {
            "run": "primary",
            "variant": "mtp",
            "ok": True,
            "regression_count": 0,
            "min_long_c2_decode_min_max_ratio": 0.2,
            "max_long_c2_itl_p99_seconds": 1.0,
            "max_mixed_secondary_itl_p99_seconds": 1.0,
            "max_streaming_itl_p99_seconds": 2.0,
        }
    ]
    assert summary["runs"][1]["prefix_cache_stress"][0]["concurrent_hit_rate_mean"] == 0.75

    markdown_path = tmp_path / "summary.md"
    write_summary_markdown(markdown_path, summary)
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Decode-Concurrency" in markdown
    assert "Runtime Monitoring" in markdown
    assert "GPU Util Avg" in markdown
    assert "CUDA Errors" in markdown
    assert "Prefix Cache Stress" in markdown
    assert "Random 8000/1000 Bench" in markdown
    assert "Random 256/256 Bench" in markdown
    assert "Spec Accept Len" in markdown
    assert "Spec Accept Pos %" in markdown
    assert "0:84.2, 1:58.4" in markdown
    assert "Frontier Context Sweep" in markdown
    assert "Target Frontier" in markdown
    assert "DS4 Story Recall Semantic" in markdown
    assert "Matched Min" in markdown
    assert "Prefill/Decode Gate" in markdown
    assert "Regression Count" in markdown
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
