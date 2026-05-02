import json

from ds4_harness import cli


def test_lm_eval_cli_builds_local_completions_command_and_summarizes_results(
    monkeypatch,
    tmp_path,
):
    captured = []

    def fake_run(command, timeout=None):
        captured.append((command, timeout))
        output_dir = command[command.index("--output_path") + 1]
        raw_path = tmp_path / "eval" / "raw" / "results.json"
        assert str(raw_path.parent) == output_dir
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(
            json.dumps(
                {
                    "results": {
                        "gsm8k": {
                            "alias": "gsm8k",
                            "exact_match,flexible-extract": 0.9439,
                            "exact_match,strict-match": 0.9431,
                            "exact_match_stderr,flexible-extract": 0.0063,
                        }
                    },
                    "versions": {"gsm8k": 3},
                }
            ),
            encoding="utf-8",
        )
        return {
            "returncode": 0,
            "stdout": "lm_eval ok\n",
            "stderr": "",
            "command": command,
        }

    monkeypatch.setattr(cli, "run_lm_eval_command", fake_run)
    output_dir = tmp_path / "eval"
    summary_path = tmp_path / "lm_eval_summary.json"

    rc = cli.main(
        [
            "lm-eval",
            "--lm-eval-bin",
            "lm_eval",
            "--base-url",
            "http://127.0.0.1:8000",
            "--model",
            "deepseek-ai/DeepSeek-V4-Flash",
            "--task",
            "gsm8k",
            "--num-fewshot",
            "8",
            "--num-concurrent",
            "4",
            "--max-retries",
            "10",
            "--max-gen-toks",
            "2048",
            "--eval-timeout-ms",
            "60000",
            "--tokenizer-backend",
            "none",
            "--batch-size",
            "auto",
            "--command-timeout",
            "30",
            "--output-dir",
            str(output_dir),
            "--json-output",
            str(summary_path),
        ]
    )

    assert rc == 0
    command, timeout = captured[0]
    assert timeout == 30
    assert command[:4] == ["lm_eval", "--model", "local-completions", "--model_args"]
    model_args = command[command.index("--model_args") + 1]
    assert "model=deepseek-ai/DeepSeek-V4-Flash" in model_args
    assert "base_url=http://127.0.0.1:8000/v1/completions" in model_args
    assert "num_concurrent=4" in model_args
    assert "max_retries=10" in model_args
    assert "tokenizer_backend=none" in model_args
    assert "max_gen_toks=2048" in model_args
    assert "timeout=60000" in model_args
    assert command[command.index("--tasks") + 1] == "gsm8k"
    assert command[command.index("--num_fewshot") + 1] == "8"
    assert command[command.index("--batch_size") + 1] == "auto"
    assert (output_dir / "stdout.log").read_text(encoding="utf-8") == "lm_eval ok\n"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["ok"] is True
    assert summary["tasks"][0]["task"] == "gsm8k"
    assert summary["tasks"][0]["exact_match_flexible"] == 0.9439
    assert summary["tasks"][0]["exact_match_strict"] == 0.9431
    assert summary["tasks"][0]["exact_match_flexible_stderr"] == 0.0063


def test_lm_eval_cli_records_failed_launch(tmp_path):
    output_dir = tmp_path / "eval"
    summary_path = tmp_path / "lm_eval_summary.json"

    rc = cli.main(
        [
            "lm-eval",
            "--lm-eval-bin",
            str(tmp_path / "missing-lm-eval"),
            "--task",
            "gsm8k",
            "--output-dir",
            str(output_dir),
            "--json-output",
            str(summary_path),
        ]
    )

    assert rc == 1
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["ok"] is False
    assert summary["returncode"] == -2
    assert "FileNotFoundError" in (output_dir / "stdout.log").read_text(
        encoding="utf-8"
    )
