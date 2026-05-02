import importlib
import json
import subprocess

from ds4_harness import cli


def test_run_kv_layout_probe_writes_raw_cache_and_sanitizes_target_path(
    monkeypatch, tmp_path
):
    kv_layout_probe = importlib.import_module("ds4_harness.kv_layout_probe")
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["request"] = json.loads(kwargs["input"])
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps(
                {
                    "schema_version": 1,
                    "case": "packed_fp8_indexer_cache_layout",
                    "variant": "nomtp",
                    "ok": True,
                    "detail": "packed helper matched expected byte layout",
                    "parameters": {
                        "num_blocks": 2,
                        "block_size": 4,
                        "head_dim": 16,
                        "scale_bytes": 4,
                    },
                    "target": {
                        "python_executable": "/workspace/vllm/.venv/bin/python",
                        "torch_version": "test-torch",
                    },
                    "raw_cache": {
                        "bytes": 4,
                        "sha256": "dummy",
                    },
                    "raw_cache_hex": "000102ff",
                }
            )
            + "\n",
            "",
        )

    monkeypatch.setattr(kv_layout_probe.subprocess, "run", fake_run)
    raw_output = tmp_path / "kv_layout_probe_packed_cache.bin"

    row = kv_layout_probe.run_kv_layout_probe(
        target_python="/workspace/vllm/.venv/bin/python",
        variant="nomtp",
        num_blocks=2,
        block_size=4,
        head_dim=16,
        scale_bytes=4,
        raw_output=raw_output,
        timeout=12.0,
    )

    assert captured["command"][:2] == ["/workspace/vllm/.venv/bin/python", "-c"]
    assert captured["request"]["variant"] == "nomtp"
    assert captured["request"]["parameters"]["head_dim"] == 16
    assert captured["request"]["emit_raw_cache_hex"] is True
    assert row["ok"] is True
    assert row["target"]["python_executable"] == "python"
    assert row["raw_cache"]["filename"] == "kv_layout_probe_packed_cache.bin"
    assert "raw_cache_hex" not in row
    assert raw_output.read_bytes() == b"\x00\x01\x02\xff"


def test_kv_layout_probe_cli_writes_json_markdown_and_raw(monkeypatch, tmp_path):
    def fake_run_kv_layout_probe(**kwargs):
        kwargs["raw_output"].write_bytes(b"\x00\x01")
        return {
            "schema_version": 1,
            "case": kwargs["case_name"],
            "variant": kwargs["variant"],
            "ok": True,
            "detail": "packed helper matched expected byte layout",
            "parameters": {
                "num_blocks": kwargs["num_blocks"],
                "block_size": kwargs["block_size"],
                "head_dim": kwargs["head_dim"],
                "scale_bytes": kwargs["scale_bytes"],
            },
            "raw_cache": {
                "filename": kwargs["raw_output"].name,
                "bytes": 2,
                "sha256": "abc",
            },
            "helper": {"available": True, "matches_expected": True},
            "interleaved_legacy_view": {"diff_count": 8},
        }

    monkeypatch.setattr(cli, "run_kv_layout_probe", fake_run_kv_layout_probe)
    json_output = tmp_path / "probe.json"
    markdown_output = tmp_path / "probe.md"
    raw_output = tmp_path / "packed_cache.bin"

    rc = cli.main(
        [
            "kv-layout-probe",
            "--target-python",
            "python",
            "--variant",
            "mtp",
            "--case-name",
            "packed_fp8_indexer_cache_layout",
            "--num-blocks",
            "2",
            "--block-size",
            "4",
            "--head-dim",
            "16",
            "--scale-bytes",
            "4",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
            "--raw-output",
            str(raw_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["variant"] == "mtp"
    assert data["raw_cache"]["filename"] == "packed_cache.bin"
    assert "Raw cache" in markdown_output.read_text(encoding="utf-8")
    assert raw_output.read_bytes() == b"\x00\x01"
