import json
import subprocess

import pytest

from ds4_harness import cli


SERVE_LOG = """
INFO Model loading took 75.62 GiB
INFO Available KV cache memory: 14.45 GiB
INFO GPU KV cache size: 2,765,705 tokens
INFO Maximum concurrency for 1,048,576 tokens per request: 2.64x
INFO Graph capturing finished in 12 secs, took 0.06 GiB
"""


def test_parse_capacity_log_estimates_context_margins():
    from ds4_harness.very_long_context import parse_capacity_log

    row = parse_capacity_log(
        SERVE_LOG,
        targets=[524288, 786432, 1048576],
        case_name="very_long_context_capacity",
        variant="mtp",
    )

    assert row["ok"] is True
    assert row["capacity"]["model_loading_gib"] == 75.62
    assert row["capacity"]["available_kv_cache_gib"] == 14.45
    assert row["capacity"]["gpu_kv_cache_size_tokens"] == 2765705
    assert row["capacity"]["maximum_concurrency_context_tokens"] == 1048576
    assert row["capacity"]["maximum_concurrency"] == 2.64
    assert row["capacity"]["cuda_graph_memory_gib"] == 0.06
    assert row["capacity"]["bytes_per_token"] == pytest.approx(5609.99, abs=0.1)

    one_m = next(
        item for item in row["estimates"] if item["target_context_tokens"] == 1048576
    )
    assert one_m["c1_ok"] is True
    assert one_m["c2_ok"] is True
    assert one_m["estimated_concurrency"] == pytest.approx(2.637, abs=0.001)


def test_capacity_parser_reports_missing_fields_and_runtime_errors():
    from ds4_harness.very_long_context import parse_capacity_log

    row = parse_capacity_log(
        "INFO Available KV cache memory: 2.0 GiB\n"
        "Triton Error [CUDA]: unspecified launch failure\n"
        "NVRM: Xid 62\n",
        targets=[1048576],
        case_name="capacity",
        variant="mtp",
    )

    assert row["ok"] is False
    assert "gpu_kv_cache_size_tokens" in row["missing_fields"]
    assert row["runtime_health"]["cuda_error_count"] == 1
    assert row["runtime_health"]["driver_error_count"] == 1


def test_materialize_token_frontier_prompts_uses_target_python(tmp_path, monkeypatch):
    from ds4_harness import very_long_context

    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["request"] = json.loads(kwargs["input"])
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps(
                {
                    "ok": True,
                    "prompts": [
                        {
                            "target_context_tokens": 1048576,
                            "target_prompt_tokens": 1048512,
                            "actual_prompt_tokens": 1048464,
                            "filename": "frontier_1048576.txt",
                            "sha256": "abc",
                            "bytes": 123,
                        }
                    ],
                }
            )
            + "\n",
            "",
        )

    monkeypatch.setattr(very_long_context.subprocess, "run", fake_run)

    row = very_long_context.materialize_token_frontier_prompts(
        target_python="/workspace/vllm/.venv/bin/python",
        model="deepseek-ai/DeepSeek-V4-Flash",
        tokenizer_mode="deepseek_v4",
        output_dir=tmp_path / "prompts",
        targets=[1048576],
        max_tokens=16,
        salt_reservation_tokens=48,
        timeout=10,
    )

    assert captured["command"][:2] == ["/workspace/vllm/.venv/bin/python", "-c"]
    assert captured["request"]["targets"] == [1048576]
    assert captured["request"]["max_tokens"] == 16
    assert row["ok"] is True
    assert row["prompts"][0]["path"] == str(tmp_path / "prompts" / "frontier_1048576.txt")


def test_very_long_context_capacity_cli_writes_json_and_markdown(tmp_path):
    serve_log = tmp_path / "serve.log"
    serve_log.write_text(SERVE_LOG, encoding="utf-8")
    json_output = tmp_path / "capacity.json"
    markdown_output = tmp_path / "capacity.md"

    rc = cli.main(
        [
            "very-long-context-capacity",
            "--serve-log",
            str(serve_log),
            "--targets",
            "524288,1048576",
            "--variant",
            "mtp",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["capacity"]["gpu_kv_cache_size_tokens"] == 2765705
    text = markdown_output.read_text(encoding="utf-8")
    assert "# Very Long Context Capacity" in text
    assert "Bytes/token" in text
    assert "1048576" in text


def test_materialize_token_frontier_cli_writes_manifest(monkeypatch, tmp_path):
    def fake_materialize_token_frontier_prompts(**kwargs):
        output_dir = kwargs["output_dir"]
        output_dir.mkdir(parents=True)
        prompt = output_dir / "frontier_524288.txt"
        prompt.write_text("prompt", encoding="utf-8")
        return {
            "ok": True,
            "model": kwargs["model"],
            "targets": kwargs["targets"],
            "prompts": [
                {
                    "target_context_tokens": 524288,
                    "target_prompt_tokens": 523712,
                    "actual_prompt_tokens": 523700,
                    "filename": prompt.name,
                    "path": str(prompt),
                    "sha256": "abc",
                    "bytes": prompt.stat().st_size,
                }
            ],
        }

    monkeypatch.setattr(
        cli,
        "materialize_token_frontier_prompts",
        fake_materialize_token_frontier_prompts,
    )
    json_output = tmp_path / "manifest.json"
    markdown_output = tmp_path / "manifest.md"

    rc = cli.main(
        [
            "materialize-token-frontier-prompts",
            "--target-python",
            "python",
            "--model",
            "model",
            "--targets",
            "524288",
            "--output-dir",
            str(tmp_path / "prompts"),
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["prompts"][0]["actual_prompt_tokens"] == 523700
    assert "Token Frontier Prompts" in markdown_output.read_text(encoding="utf-8")
