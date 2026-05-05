import json

from ds4_harness import cli
from ds4_harness.runtime_stats import summarize_runtime_stats, write_runtime_markdown


def test_summarize_runtime_stats_reads_vllm_metrics_and_serve_log(tmp_path):
    metrics = tmp_path / "vllm_metrics.prom"
    metrics.write_text(
        "\n".join(
            [
                "# DS4_HARNESS_SNAPSHOT 2026-05-01T22:00:00Z status=200",
                "vllm:prompt_tokens_total{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 100",
                "vllm:generation_tokens_total{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 25",
                "vllm:num_requests_running{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 1",
                "vllm:kv_cache_usage_perc{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 0.12",
                "vllm:prefix_cache_queries{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 100",
                "vllm:prefix_cache_hits{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 20",
                "vllm:num_preemptions{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 0",
                "# DS4_HARNESS_SNAPSHOT 2026-05-01T22:00:05Z status=200",
                "vllm:prompt_tokens_total{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 340",
                "vllm:generation_tokens_total{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 145",
                "vllm:num_requests_running{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 3",
                "vllm:kv_cache_usage_perc{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 0.35",
                "vllm:prefix_cache_queries{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 500",
                "vllm:prefix_cache_hits{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 270",
                "vllm:num_preemptions{model_name=\"deepseek-ai/DeepSeek-V4-Flash\"} 2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    serve_log = tmp_path / "serve.log"
    serve_log.write_text(
        "\n".join(
            [
                (
                    "INFO Engine 000: Avg prompt throughput: 35.3 tokens/s, "
                    "Avg generation throughput: 96.0 tokens/s, Running: 1 reqs, "
                    "Waiting: 0 reqs, GPU KV cache usage: 0.2%, Prefix cache hit rate: 0.0%"
                ),
                (
                    "INFO SpecDecoding metrics: Mean acceptance length: 2.37, "
                    "Accepted throughput: 77.90 tokens/s, Drafted throughput: 113.40 tokens/s, "
                    "Accepted: 779 tokens, Drafted: 1134 tokens, "
                    "Per-position acceptance rate: 0.854, 0.520, Avg Draft acceptance rate: 68.7%"
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = summarize_runtime_stats(metrics, serve_log)

    assert summary["metrics"]["available"] is True
    assert summary["metrics"]["prefill_tokens_delta"] == 240.0
    assert summary["metrics"]["decode_tokens_delta"] == 120.0
    assert summary["metrics"]["running_requests_max"] == 3.0
    assert summary["metrics"]["gpu_kv_cache_usage_percent_max"] == 35.0
    assert summary["metrics"]["prefix_cache_queries_delta"] == 400.0
    assert summary["metrics"]["prefix_cache_hits_delta"] == 250.0
    assert summary["metrics"]["prefix_cache_hit_rate_percent_delta"] == 62.5
    assert summary["metrics"]["preemptions_delta"] == 2.0
    assert summary["serve_log"]["prefill_throughput_tok_s_avg"] == 35.3
    assert summary["serve_log"]["decode_throughput_tok_s_avg"] == 96.0
    assert summary["serve_log"]["prefix_cache_hit_rate_percent_avg"] == 0.0
    assert summary["serve_log"]["spec_decode"]["mean_acceptance_length_avg"] == 2.37
    assert summary["serve_log"]["spec_decode"]["per_position_acceptance_rate_avg"] == [
        0.854,
        0.52,
    ]


def test_runtime_summary_cli_writes_json_and_markdown(tmp_path):
    metrics = tmp_path / "vllm_metrics.prom"
    metrics.write_text(
        "\n".join(
            [
                "vllm:prompt_tokens_total 10",
                "vllm:prompt_tokens_total 30",
                "vllm:generation_tokens_total 3",
                "vllm:generation_tokens_total 13",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    json_output = tmp_path / "runtime_stats_summary.json"
    markdown_output = tmp_path / "runtime_stats_summary.md"

    rc = cli.main(
        [
            "runtime-summary",
            "--metrics-input",
            str(metrics),
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["metrics"]["prefill_tokens_delta"] == 20.0
    assert data["metrics"]["decode_tokens_delta"] == 10.0
    report = markdown_output.read_text(encoding="utf-8")
    assert "# vLLM Runtime Stats Summary" in report
    assert "Prefill tokens delta" in report
    assert "Decode tokens delta" in report
    assert "Prefix cache hit rate" in report


def test_write_runtime_markdown_reports_unavailable_inputs(tmp_path):
    output = tmp_path / "runtime_stats_summary.md"

    write_runtime_markdown(
        output,
        {
            "metrics": {"available": False, "reason": "missing metrics"},
            "serve_log": {"available": False, "reason": "missing serve log"},
        },
    )

    report = output.read_text(encoding="utf-8")
    assert "missing metrics" in report
    assert "missing serve log" in report
