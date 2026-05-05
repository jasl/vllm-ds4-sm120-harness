import json

from ds4_harness import cli
from ds4_harness.bench import parse_bench_output
from ds4_harness.bench import run_bench_command


def test_parse_bench_output_extracts_common_vllm_metrics():
    report = parse_bench_output(
        """
============ Serving Benchmark Result ============
Successful requests:                     48
Benchmark duration (s):                  98.12
Total input tokens:                      49152
Total generated tokens:                  49152
Request throughput (req/s):              0.49
Output token throughput (tok/s):         500.91
Total Token throughput (tok/s):          1001.82
Mean TPOT (ms):                          15.25
Mean ITL (ms):                           15.20
Mean TTFT (ms):                          1210.50
==================================================
"""
    )

    assert report["successful_requests"] == 48
    assert report["output_token_throughput_tok_s"] == 500.91
    assert report["mean_tpot_ms"] == 15.25


def test_parse_bench_output_extracts_latency_percentiles_and_spec_decode_metrics():
    report = parse_bench_output(
        """
Median TTFT (ms):                        371.19
P99 TTFT (ms):                           395.08
Mean TPOT (ms):                          10.14
Median TPOT (ms):                        10.87
P99 TPOT (ms):                           12.02
Mean ITL (ms):                           11.59
Median ITL (ms):                         11.27
P99 ITL (ms):                            18.14
---------------Speculative Decoding---------------
Acceptance rate (%):                     7.11
Acceptance length:                       1.14
Drafts:                                  14319
Draft tokens:                            28638
Accepted tokens:                         2037
Per-position acceptance (%):
  Position 0:                            10.01
  Position 1:                            4.21
==================================================
"""
    )

    assert report["median_ttft_ms"] == 371.19
    assert report["p99_ttft_ms"] == 395.08
    assert report["median_tpot_ms"] == 10.87
    assert report["p99_tpot_ms"] == 12.02
    assert report["median_itl_ms"] == 11.27
    assert report["p99_itl_ms"] == 18.14
    assert report["spec_acceptance_rate_percent"] == 7.11
    assert report["spec_acceptance_length"] == 1.14
    assert report["spec_drafts"] == 14319
    assert report["spec_draft_tokens"] == 28638
    assert report["spec_accepted_tokens"] == 2037
    assert report["spec_per_position_acceptance_percent"] == [10.01, 4.21]


def test_run_bench_command_records_launch_errors():
    result = run_bench_command(["/path/does/not/exist/vllm"])

    assert result["returncode"] == -2
    assert result["metrics"] == {}
    assert "FileNotFoundError" in result["stdout"]


def test_bench_matrix_builds_hf_dataset_commands(monkeypatch, tmp_path):
    captured = []

    def fake_run(command, timeout=None):
        captured.append((command, timeout))
        return {
            "returncode": 0,
            "metrics": {"successful_requests": 80},
            "stdout": "ok\n",
            "command": command,
        }

    monkeypatch.setattr(cli, "run_bench_command", fake_run)

    rc = cli.main(
        [
            "bench-matrix",
            "--vllm-bin",
            "vllm",
            "--model",
            "deepseek-ai/DeepSeek-V4-Flash",
            "--concurrency",
            "1,2",
            "--dataset-name",
            "hf",
            "--dataset-path",
            "philschmid/mt-bench",
            "--tokenizer-mode",
            "deepseek_v4",
            "--num-prompts",
            "80",
            "--temperature",
            "1.0",
            "--timeout",
            "30",
            "--log-dir",
            str(tmp_path),
        ]
    )

    assert rc == 0
    assert len(captured) == 2
    first_command, first_timeout = captured[0]
    assert first_timeout == 30
    assert "--dataset-name" in first_command
    assert first_command[first_command.index("--dataset-name") + 1] == "hf"
    assert "--dataset-path" in first_command
    assert first_command[first_command.index("--dataset-path") + 1] == "philschmid/mt-bench"
    assert "--tokenizer-mode" in first_command
    assert first_command[first_command.index("--tokenizer-mode") + 1] == "deepseek_v4"
    assert "--max-concurrency" in first_command
    assert first_command[first_command.index("--max-concurrency") + 1] == "1"
    assert "--temperature" in first_command
    assert first_command[first_command.index("--temperature") + 1] == "1.0"
    assert "--random-input-len" not in first_command
    assert "--random-output-len" not in first_command


def test_bench_matrix_passes_base_url_to_vllm_bench(monkeypatch):
    captured = []

    def fake_run(command, timeout=None):
        captured.append(command)
        return {
            "returncode": 0,
            "metrics": {"successful_requests": 1},
            "stdout": "",
            "command": command,
        }

    monkeypatch.setattr(cli, "run_bench_command", fake_run)

    rc = cli.main(
        [
            "bench-matrix",
            "--base-url",
            "http://192.0.2.10:8000",
            "--concurrency",
            "1",
            "--num-prompts",
            "1",
        ]
    )

    assert rc == 0
    command = captured[0]
    assert "--base-url" in command
    assert command[command.index("--base-url") + 1] == "http://192.0.2.10:8000"
    assert "--host" not in command
    assert "--port" not in command


def test_bench_matrix_keeps_random_dataset_length_controls(monkeypatch):
    captured = []

    def fake_run(command, timeout=None):
        captured.append(command)
        return {
            "returncode": 0,
            "metrics": {"successful_requests": 80},
            "stdout": "",
            "command": command,
        }

    monkeypatch.setattr(cli, "run_bench_command", fake_run)

    rc = cli.main(
        [
            "bench-matrix",
            "--dataset-name",
            "random",
            "--random-input-len",
            "8192",
            "--random-output-len",
            "512",
            "--concurrency",
            "1",
            "--ignore-eos",
        ]
    )

    assert rc == 0
    command = captured[0]
    assert command[command.index("--dataset-name") + 1] == "random"
    assert command[command.index("--random-input-len") + 1] == "8192"
    assert command[command.index("--random-output-len") + 1] == "512"
    assert "--ignore-eos" in command


def test_bench_matrix_marks_partial_successful_requests_as_failed(monkeypatch):
    def fake_run(command, timeout=None):
        return {
            "returncode": 0,
            "metrics": {"successful_requests": 4},
            "stdout": "",
            "command": command,
        }

    monkeypatch.setattr(cli, "run_bench_command", fake_run)

    rc = cli.main(
        [
            "bench-matrix",
            "--dataset-name",
            "hf",
            "--dataset-path",
            "philschmid/mt-bench",
            "--num-prompts",
            "80",
            "--concurrency",
            "4",
        ]
    )

    assert rc == 1


def test_bench_matrix_retries_transient_hf_dataset_failure_once(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, timeout=None):
        calls.append(command)
        if len(calls) == 1:
            return {
                "returncode": 1,
                "metrics": {},
                "stdout": "huggingface_hub.utils.ReadTimeout: dataset download timed out\n",
                "command": command,
            }
        return {
            "returncode": 0,
            "metrics": {"successful_requests": 80},
            "stdout": "ok\n",
            "command": command,
        }

    monkeypatch.setattr(cli, "run_bench_command", fake_run)
    output = tmp_path / "bench.json"

    rc = cli.main(
        [
            "bench-matrix",
            "--dataset-name",
            "hf",
            "--dataset-path",
            "philschmid/mt-bench",
            "--num-prompts",
            "80",
            "--concurrency",
            "4",
            "--json-output",
            str(output),
        ]
    )

    rows = json.loads(output.read_text(encoding="utf-8"))
    assert rc == 0
    assert len(calls) == 2
    assert len(rows) == 1
    assert rows[0]["ok"] is True
    assert rows[0]["attempts"] == 2
    assert rows[0]["retry_failures"] == [
        "attempt 1: vllm bench exited 1 (transient infrastructure failure)"
    ]


def test_bench_matrix_does_not_retry_quality_or_metric_failures(monkeypatch):
    calls = []

    def fake_run(command, timeout=None):
        calls.append(command)
        return {
            "returncode": 0,
            "metrics": {"successful_requests": 4},
            "stdout": "",
            "command": command,
        }

    monkeypatch.setattr(cli, "run_bench_command", fake_run)

    rc = cli.main(
        [
            "bench-matrix",
            "--dataset-name",
            "hf",
            "--dataset-path",
            "philschmid/mt-bench",
            "--num-prompts",
            "80",
            "--concurrency",
            "4",
        ]
    )

    assert rc == 1
    assert len(calls) == 1


def test_bench_matrix_stops_after_unresponsive_server(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, timeout=None):
        calls.append(command)
        return {
            "returncode": -1,
            "metrics": {},
            "stdout": "TIMEOUT after 5 seconds",
            "command": command,
        }

    monkeypatch.setattr(cli, "run_bench_command", fake_run)
    monkeypatch.setattr(
        cli,
        "get_status",
        lambda base_url, path, timeout: {"status_code": 599, "body": "timeout"},
    )
    output = tmp_path / "bench.json"

    rc = cli.main(
        [
            "bench-matrix",
            "--concurrency",
            "1,2",
            "--num-prompts",
            "1",
            "--timeout",
            "5",
            "--stop-on-unresponsive",
            "--health-timeout",
            "1",
            "--json-output",
            str(output),
        ]
    )

    rows = json.loads(output.read_text(encoding="utf-8"))
    assert rc == 1
    assert len(calls) == 1
    assert rows[0]["concurrency"] == 1
    assert rows[0]["ok"] is False
    assert rows[1]["concurrency"] == 2
    assert rows[1]["skipped"] is True
    assert "server unresponsive" in rows[1]["detail"]


def test_bench_matrix_stops_when_health_passes_but_generation_is_wedged(
    monkeypatch, tmp_path
):
    calls = []

    def fake_run(command, timeout=None):
        calls.append(command)
        return {
            "returncode": -1,
            "metrics": {},
            "stdout": "TIMEOUT after 5 seconds",
            "command": command,
        }

    def fake_post_json(base_url, path, payload, timeout):
        raise TimeoutError("generation probe timed out")

    monkeypatch.setattr(cli, "run_bench_command", fake_run)
    monkeypatch.setattr(
        cli,
        "get_status",
        lambda base_url, path, timeout: {"status_code": 200, "body": "ok"},
    )
    monkeypatch.setattr(cli, "post_json", fake_post_json)
    output = tmp_path / "bench.json"

    rc = cli.main(
        [
            "bench-matrix",
            "--concurrency",
            "1,2",
            "--num-prompts",
            "1",
            "--timeout",
            "5",
            "--stop-on-unresponsive",
            "--health-timeout",
            "1",
            "--failure-probe-timeout",
            "1",
            "--json-output",
            str(output),
        ]
    )

    rows = json.loads(output.read_text(encoding="utf-8"))
    assert rc == 1
    assert len(calls) == 1
    assert rows[1]["concurrency"] == 2
    assert rows[1]["skipped"] is True
