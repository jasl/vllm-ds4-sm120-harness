import json

from ds4_harness import cli
from ds4_harness.kv_lifecycle_probe import (
    MetricSnapshot,
    parse_metrics_snapshot,
    run_kv_lifecycle_probe,
    write_kv_lifecycle_probe_markdown,
)


def test_parse_metrics_snapshot_scales_kv_fraction_and_sums_request_gauges():
    snapshot = parse_metrics_snapshot(
        """
# HELP vllm:gpu_cache_usage_perc GPU KV cache usage.
vllm:gpu_cache_usage_perc{gpu="0"} 0.125
vllm:gpu_cache_usage_perc{gpu="1"} 0.250
vllm:num_requests_running{model_name="m"} 0
vllm:num_requests_waiting{model_name="m"} 2
vllm:prefix_cache_hits_total 11
vllm:prefix_cache_queries_total 17
"""
    )

    assert snapshot.gpu_kv_cache_usage_percent == 25.0
    assert snapshot.running_requests == 0.0
    assert snapshot.waiting_requests == 2.0
    assert snapshot.prefix_cache_hits == 11
    assert snapshot.prefix_cache_queries == 17


def test_kv_lifecycle_probe_fails_when_prefix_disabled_keeps_idle_kv():
    metric_values = iter(
        [
            MetricSnapshot(gpu_kv_cache_usage_percent=0.0, running_requests=0, waiting_requests=0),
            MetricSnapshot(gpu_kv_cache_usage_percent=8.5, running_requests=0, waiting_requests=0),
        ]
    )

    def fake_metrics(**kwargs):
        return next(metric_values)

    def fake_request(**kwargs):
        return {
            "ok": True,
            "phase": kwargs["phase"],
            "ttft_seconds": 0.5,
            "elapsed_seconds": 1.0,
            "chunks": 2,
            "detail": "matched marker",
        }

    row = run_kv_lifecycle_probe(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp",
        cache_mode="disabled",
        session_count=1,
        line_count=128,
        max_idle_kv_usage_percent=2.0,
        settle_timeout=1.0,
        settle_interval=0.0,
        include_abort=False,
        metrics_func=fake_metrics,
        request_func=fake_request,
    )

    assert row["ok"] is False
    assert row["summary"]["max_idle_kv_usage_percent"] == 8.5
    assert row["summary"]["idle_kv_within_threshold"] is False


def test_kv_lifecycle_probe_accepts_prefix_enabled_cached_but_bounded_kv():
    metric_values = iter(
        [
            MetricSnapshot(gpu_kv_cache_usage_percent=0.0, running_requests=0, waiting_requests=0),
            MetricSnapshot(
                gpu_kv_cache_usage_percent=18.0,
                running_requests=0,
                waiting_requests=0,
                prefix_cache_hits=4,
                prefix_cache_queries=8,
            ),
            MetricSnapshot(
                gpu_kv_cache_usage_percent=31.0,
                running_requests=0,
                waiting_requests=0,
                prefix_cache_hits=10,
                prefix_cache_queries=16,
            ),
        ]
    )

    def fake_metrics(**kwargs):
        return next(metric_values)

    def fake_request(**kwargs):
        return {
            "ok": True,
            "phase": kwargs["phase"],
            "ttft_seconds": 0.5,
            "elapsed_seconds": 1.0,
            "chunks": 2,
            "detail": "matched marker",
        }

    row = run_kv_lifecycle_probe(
        base_url="http://127.0.0.1:8000",
        model="model",
        variant="mtp",
        cache_mode="enabled",
        session_count=2,
        line_count=128,
        max_idle_kv_usage_percent=90.0,
        settle_timeout=1.0,
        settle_interval=0.0,
        include_abort=False,
        metrics_func=fake_metrics,
        request_func=fake_request,
    )

    assert row["ok"] is True
    assert row["summary"]["final_idle_kv_usage_percent"] == 31.0
    assert row["summary"]["prefix_cache_queries_delta"] == 16
    assert row["summary"]["prefix_cache_hits_delta"] == 10


def test_kv_lifecycle_probe_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    def fake_run_kv_lifecycle_probe(**kwargs):
        return {
            "case": kwargs["case_name"],
            "variant": kwargs["variant"],
            "model": kwargs["model"],
            "cache_mode": kwargs["cache_mode"],
            "ok": True,
            "summary": {
                "request_count": 1,
                "failure_count": 0,
                "max_idle_kv_usage_percent": 0.0,
            },
            "requests": [],
            "snapshots": [],
        }

    monkeypatch.setattr(cli, "run_kv_lifecycle_probe", fake_run_kv_lifecycle_probe)
    json_output = tmp_path / "kv.json"
    markdown_output = tmp_path / "kv.md"

    rc = cli.main(
        [
            "kv-lifecycle-probe",
            "--model",
            "model",
            "--variant",
            "mtp",
            "--cache-mode",
            "disabled",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["cache_mode"] == "disabled"
    assert "KV Lifecycle Probe" in markdown_output.read_text(encoding="utf-8")


def test_kv_lifecycle_probe_markdown_records_c2_prefill_followup(tmp_path):
    row = {
        "case": "kv_lifecycle_probe",
        "variant": "mtp",
        "cache_mode": "enabled",
        "ok": True,
        "summary": {
            "request_count": 2,
            "failure_count": 0,
            "max_idle_kv_usage_percent": 31.0,
            "idle_kv_within_threshold": True,
        },
        "requests": [
            {
                "phase": "session_1",
                "ok": True,
                "ttft_seconds": 0.5,
                "elapsed_seconds": 1.0,
                "idle_kv_usage_percent_after_request": 18.0,
                "detail": "matched marker",
            }
        ],
        "snapshots": [],
    }
    output = tmp_path / "kv.md"

    write_kv_lifecycle_probe_markdown(output, row)

    report = output.read_text(encoding="utf-8")
    assert "KV Lifecycle Probe" in report
    assert "C=2 long-prefill scheduling remains a separate follow-up" in report
