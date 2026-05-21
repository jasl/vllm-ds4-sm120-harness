import json

from ds4_harness import cli
from ds4_harness.prefix_cache_stress import (
    parse_prefix_metrics,
    run_prefix_cache_stress,
    write_prefix_cache_stress_markdown,
)


def test_parse_prefix_metrics_accepts_vllm_counter_name_variants():
    metrics = parse_prefix_metrics(
        "\n".join(
            [
                "# HELP ignored ignored",
                'vllm:prefix_cache_hits{model_name="m"} 20',
                'vllm:prefix_cache_queries{model_name="m"} 50',
                'vllm:prefix_cache_hits_total{model_name="m"} 3',
                'vllm:prefix_cache_queries_total{model_name="m"} 7',
            ]
        )
    )

    assert metrics == {"hits": 23, "queries": 57}


def test_run_prefix_cache_stress_records_solo_and_concurrent_trials():
    metric_samples = iter(
        [
            {"hits": 100, "queries": 200},
            {"hits": 130, "queries": 260},
            {"hits": 190, "queries": 368},
        ]
    )
    chat_calls = []

    def fake_metrics(base_url, timeout, headers=None):
        return next(metric_samples)

    def fake_chat(base_url, model, conversation, user_msg, **kwargs):
        chat_calls.append((len(conversation), user_msg))
        return {"message": {"content": "ok"}, "elapsed_seconds": 1.25}

    result = run_prefix_cache_stress(
        base_url="http://127.0.0.1:8000",
        model="deepseek-v4-flash",
        trials=1,
        filler_words=32,
        turns=3,
        metrics_func=fake_metrics,
        chat_func=fake_chat,
        health_func=lambda base_url, timeout, headers=None: 200,
    )

    assert result["ok"] is True
    assert result["health_status"] == 200
    assert result["summary"]["trial_count"] == 1
    assert result["summary"]["failure_count"] == 0
    assert result["trials"][0]["solo_hits"] == 30
    assert result["trials"][0]["solo_queries"] == 60
    assert result["trials"][0]["solo_hit_rate"] == 0.5
    assert result["trials"][0]["concurrent_hits"] == 60
    assert result["trials"][0]["concurrent_queries"] == 108
    assert round(result["trials"][0]["concurrent_hit_rate"], 4) == 0.5556
    assert len(result["trials"][0]["solo_turns"]) == 3
    assert len(result["trials"][0]["concurrent_sessions"]) == 2
    assert len(chat_calls) == 9


def test_run_prefix_cache_stress_flags_metrics_disconnect():
    def failing_metrics(base_url, timeout, headers=None):
        raise RuntimeError("Server disconnected without sending a response")

    result = run_prefix_cache_stress(
        base_url="http://127.0.0.1:8000",
        model="deepseek-v4-flash",
        trials=1,
        metrics_func=failing_metrics,
        chat_func=lambda *args, **kwargs: {
            "message": {"content": "ok"},
            "elapsed_seconds": 0.1,
        },
        health_func=lambda base_url, timeout, headers=None: 200,
    )

    assert result["ok"] is False
    assert result["summary"]["failure_count"] == 1
    assert "Server disconnected" in result["trials"][0]["error"]


def test_prefix_cache_stress_markdown_includes_user_report_shape(tmp_path):
    row = {
        "ok": True,
        "case": "user_report_prefix_cache_http_metrics_stress",
        "model": "deepseek-v4-flash",
        "trials": [
            {
                "ok": True,
                "trial": 1,
                "solo_hit_rate": 0.5,
                "solo_elapsed_seconds": 3.0,
                "concurrent_hit_rate": 0.555,
                "concurrent_elapsed_seconds": 4.0,
            }
        ],
        "summary": {"trial_count": 1, "failure_count": 0},
    }
    output = tmp_path / "stress.md"

    write_prefix_cache_stress_markdown(output, row)

    text = output.read_text(encoding="utf-8")
    assert "Prefix Cache HTTP Metrics Stress" in text
    assert "user_report_prefix_cache_http_metrics_stress" in text
    assert "55.5%" in text


def test_prefix_cache_stress_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    def fake_run_prefix_cache_stress(**kwargs):
        return {
            "ok": True,
            "case": kwargs["case_name"],
            "summary": {"trial_count": kwargs["trials"], "failure_count": 0},
            "trials": [],
        }

    monkeypatch.setattr(cli, "run_prefix_cache_stress", fake_run_prefix_cache_stress)
    json_output = tmp_path / "stress.json"
    markdown_output = tmp_path / "stress.md"

    code = cli.main(
        [
            "prefix-cache-stress",
            "--base-url",
            "http://127.0.0.1:8000",
            "--model",
            "deepseek-v4-flash",
            "--case-name",
            "comment_4507780873",
            "--trials",
            "2",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert code == 0
    assert json.loads(json_output.read_text(encoding="utf-8"))["case"] == (
        "comment_4507780873"
    )
    assert markdown_output.exists()
