from __future__ import annotations

import json
from pathlib import Path

from ds4_harness import cli
from ds4_harness.prefill_decode_gate import evaluate_prefill_decode_gate


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_prefill_decode_artifacts(root: Path, *, bad_fairness: bool = False) -> None:
    variant = "mtp"
    root.mkdir(parents=True, exist_ok=True)
    (root / "phase_exit_codes.tsv").write_text(
        "variant\tphase\texit_code\tartifact_dir\n"
        f"{variant}\tlong_context_latency_matrix\t0\t{variant}/long_context_latency_matrix\n"
        f"{variant}\tlong_context_decode_concurrency\t0\t{variant}/long_context_decode_concurrency\n"
        f"{variant}\tlong_context_mixed_arrival\t0\t{variant}/long_context_mixed_arrival\n"
        f"{variant}\tstreaming_pressure_matrix\t0\t{variant}/streaming_pressure_matrix\n",
        encoding="utf-8",
    )
    c2_ratio = 0.09 if bad_fairness else 0.91
    c2_itl = 1.28 if bad_fairness else 0.03
    latency_summary = [
        {
            "prompt": "synthetic_4000_lines",
            "cache_mode": "cold",
            "concurrency": 2,
            "failure_count": 0,
            "decode_tps_min_to_max_ratio": c2_ratio,
            "p99_inter_chunk_seconds": c2_itl,
        }
    ]
    _write_json(
        root / variant / "long_context_latency_matrix" / "long_context_latency_matrix.json",
        {"ok": True, "summary": latency_summary},
    )
    _write_json(
        root
        / variant
        / "long_context_decode_concurrency"
        / "long_context_decode_concurrency.json",
        {"ok": True, "summary": latency_summary},
    )
    _write_json(
        root / variant / "long_context_mixed_arrival" / "long_context_mixed_arrival.json",
        {
            "ok": True,
            "summary": [
                {
                    "case": "decode_then_124k",
                    "failure_count": 0,
                    "secondary_p99_inter_chunk_seconds": 0.72,
                    "decode_tps_min_to_max_ratio": 0.88,
                }
            ],
        },
    )
    _write_json(
        root / variant / "streaming_pressure_matrix" / "streaming_pressure_matrix.json",
        {
            "ok": True,
            "summary": {
                "case_count": 1,
                "request_count": 8,
                "failure_count": 0,
                "slow_case_count": 0,
                "p99_inter_chunk_seconds": 1.1,
            },
        },
    )


def test_prefill_decode_gate_accepts_healthy_artifacts(tmp_path):
    baseline = tmp_path / "baseline"
    _write_prefill_decode_artifacts(baseline)

    gate = evaluate_prefill_decode_gate(baseline_dir=baseline, variant="mtp")

    assert gate["ok"] is True
    assert gate["regression_count"] == 0
    assert {item["phase"] for item in gate["checks"]} == {
        "long_context_latency_matrix",
        "long_context_decode_concurrency",
        "long_context_mixed_arrival",
        "streaming_pressure_matrix",
    }


def test_prefill_decode_gate_rejects_c2_fairness_and_itl_regressions(tmp_path):
    baseline = tmp_path / "baseline"
    _write_prefill_decode_artifacts(baseline, bad_fairness=True)

    gate = evaluate_prefill_decode_gate(baseline_dir=baseline, variant="mtp")

    assert gate["ok"] is False
    assert gate["regression_count"] == 4
    reasons = {item["reason"] for item in gate["regressions"]}
    assert reasons == {
        "long-c2-decode-min-max-ratio-below-floor",
        "long-c2-itl-p99-above-ceiling",
    }


def test_prefill_decode_gate_rejects_missing_c2_summary_rows(tmp_path):
    baseline = tmp_path / "baseline"
    _write_prefill_decode_artifacts(baseline)
    for phase in ("long_context_latency_matrix", "long_context_decode_concurrency"):
        path = baseline / "mtp" / phase / f"{phase}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["summary"] = [
            {
                "prompt": "synthetic_4000_lines",
                "cache_mode": "cold",
                "concurrency": 1,
                "failure_count": 0,
                "decode_tps_min_to_max_ratio": 1.0,
                "p99_inter_chunk_seconds": 0.02,
            }
        ]
        path.write_text(json.dumps(payload), encoding="utf-8")

    gate = evaluate_prefill_decode_gate(baseline_dir=baseline, variant="mtp")

    assert gate["ok"] is False
    reasons = {item["reason"] for item in gate["regressions"]}
    assert reasons == {"long-c2-summary-missing"}


def test_prefill_decode_gate_rejects_missing_or_failed_required_phase(tmp_path):
    baseline = tmp_path / "baseline"
    _write_prefill_decode_artifacts(baseline)
    (baseline / "phase_exit_codes.tsv").write_text(
        "variant\tphase\texit_code\tartifact_dir\n"
        "mtp\tlong_context_latency_matrix\t0\tmtp/long_context_latency_matrix\n"
        "mtp\tlong_context_decode_concurrency\t1\tmtp/long_context_decode_concurrency\n"
        "mtp\tlong_context_mixed_arrival\t0\tmtp/long_context_mixed_arrival\n",
        encoding="utf-8",
    )

    gate = evaluate_prefill_decode_gate(baseline_dir=baseline, variant="mtp")

    assert gate["ok"] is False
    failed = {
        (item["phase"], item["value"])
        for item in gate["regressions"]
        if item["reason"] == "phase-not-run-or-failed"
    }
    assert failed == {
        ("long_context_decode_concurrency", 1),
        ("streaming_pressure_matrix", None),
    }


def test_prefill_decode_gate_rejects_empty_mixed_arrival_summary(tmp_path):
    baseline = tmp_path / "baseline"
    _write_prefill_decode_artifacts(baseline)
    path = (
        baseline
        / "mtp"
        / "long_context_mixed_arrival"
        / "long_context_mixed_arrival.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["summary"] = []
    path.write_text(json.dumps(payload), encoding="utf-8")

    gate = evaluate_prefill_decode_gate(baseline_dir=baseline, variant="mtp")

    assert gate["ok"] is False
    reasons = {item["reason"] for item in gate["regressions"]}
    assert "mixed-summary-empty" in reasons


def test_prefill_decode_gate_rejects_empty_streaming_pressure_matrix(tmp_path):
    baseline = tmp_path / "baseline"
    _write_prefill_decode_artifacts(baseline)
    path = (
        baseline
        / "mtp"
        / "streaming_pressure_matrix"
        / "streaming_pressure_matrix.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["summary"] = {
        "case_count": 0,
        "request_count": 0,
        "failure_count": 0,
        "slow_case_count": 0,
        "p99_inter_chunk_seconds": 0.01,
    }
    payload["cases"] = []
    path.write_text(json.dumps(payload), encoding="utf-8")

    gate = evaluate_prefill_decode_gate(baseline_dir=baseline, variant="mtp")

    assert gate["ok"] is False
    reasons = {item["reason"] for item in gate["regressions"]}
    assert reasons == {"streaming-cases-missing", "streaming-requests-missing"}


def test_prefill_decode_gate_cli_writes_outputs_and_fails_on_regression(tmp_path):
    baseline = tmp_path / "baseline"
    json_output = tmp_path / "gate.json"
    markdown_output = tmp_path / "gate.md"
    _write_prefill_decode_artifacts(baseline, bad_fairness=True)

    rc = cli.main(
        [
            "prefill-decode-gate",
            "--baseline-dir",
            str(baseline),
            "--variant",
            "mtp",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 1
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["ok"] is False
    assert data["regression_count"] == 4
    assert "SM12x Prefill/Decode Regression Gate" in markdown_output.read_text(
        encoding="utf-8"
    )
