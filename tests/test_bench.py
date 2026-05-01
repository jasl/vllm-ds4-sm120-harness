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
