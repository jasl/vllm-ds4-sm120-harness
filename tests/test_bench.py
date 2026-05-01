from ds4_harness.bench import parse_bench_output
from ds4_harness import cli


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
            "metrics": {},
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
