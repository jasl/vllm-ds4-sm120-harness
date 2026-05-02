import json

from ds4_harness import cli
from ds4_harness.run_environment import (
    gpu_topology_slug,
    parse_nvidia_smi_gpu_csv,
    summarize_run_environment,
    write_run_environment_markdown,
)


def test_parse_nvidia_smi_gpu_csv_counts_models_without_uuids():
    gpus = parse_nvidia_smi_gpu_csv(
        "\n".join(
            [
                "0, NVIDIA RTX PRO 6000 Blackwell Workstation Edition, 97887",
                "1, NVIDIA RTX PRO 6000 Blackwell Workstation Edition, 97887",
                "2, NVIDIA B200, 183456",
            ]
        )
        + "\n"
    )

    assert len(gpus) == 3
    assert gpus[0]["name"] == "NVIDIA RTX PRO 6000 Blackwell Workstation Edition"
    assert gpus[0]["memory_total_mib"] == 97887.0
    assert "uuid" not in gpus[0]


def test_gpu_topology_slug_includes_count_and_model():
    gpus = parse_nvidia_smi_gpu_csv(
        "\n".join(
            [
                "0, NVIDIA RTX PRO 6000 Blackwell Workstation Edition, 97887",
                "1, NVIDIA RTX PRO 6000 Blackwell Workstation Edition, 97887",
            ]
        )
        + "\n"
    )

    assert (
        gpu_topology_slug(gpus)
        == "2x_nvidia_rtx_pro_6000_blackwell_workstation_edition"
    )


def test_summarize_run_environment_redacts_api_key_and_records_gpu_inventory():
    env = {
        "DEEPSEEK_API_KEY": "secret",
        "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
        "DEEPSEEK_BETA_BASE_URL": "https://api.deepseek.com/beta",
        "DEEPSEEK_MODEL": "deepseek-v4-flash",
        "DEEPSEEK_FLASH_MODEL": "deepseek-v4-flash",
        "DEEPSEEK_PRO_MODEL": "deepseek-v4-pro",
        "DEEPSEEK_THINKING_TYPE": "enabled",
        "DEEPSEEK_REASONING_EFFORT": "high",
        "DEEPSEEK_PRESERVE_REASONING_CONTENT": "1",
        "MODEL": "deepseek-ai/DeepSeek-V4-Flash",
        "BASE_URL": "http://127.0.0.1:8000",
        "GPU_TOPOLOGY_SLUG": "2x_test_gpu",
        "OUT_DIR": "artifacts/main/2x_test_gpu/run",
    }
    summary = summarize_run_environment(
        env=env,
        nvidia_smi_output="0, Test GPU, 49152\n1, Test GPU, 49152\n",
    )

    assert summary["official_api"]["api_key_present"] is True
    assert "secret" not in json.dumps(summary)
    assert summary["official_api"]["base_url"] == "https://api.deepseek.com"
    assert summary["official_api"]["beta_base_url"] == "https://api.deepseek.com/beta"
    assert summary["official_api"]["model"] == "deepseek-v4-flash"
    assert summary["official_api"]["flash_model"] == "deepseek-v4-flash"
    assert summary["official_api"]["pro_model"] == "deepseek-v4-pro"
    assert summary["official_api"]["thinking_type"] == "enabled"
    assert summary["official_api"]["reasoning_effort"] == "high"
    assert summary["official_api"]["preserve_reasoning_content"] == "1"
    assert summary["gpu"]["count"] == 2
    assert summary["artifact"]["gpu_topology_slug"] == "2x_test_gpu"
    assert summary["gpu"]["topology_slug"] == "2x_test_gpu"
    assert summary["gpu"]["models"][0]["count"] == 2


def test_summarize_run_environment_separates_configured_and_effective_gpu_topology():
    env = {
        "GPU_TOPOLOGY_SLUG": "4x_nvidia_b200",
        "CUDA_VISIBLE_DEVICES": "2,3",
    }
    summary = summarize_run_environment(
        env=env,
        nvidia_smi_output="2, NVIDIA B200, 183359\n3, NVIDIA B200, 183359\n",
    )

    assert summary["artifact"]["gpu_topology_slug"] == "4x_nvidia_b200"
    assert summary["gpu"]["count"] == 2
    assert summary["gpu"]["topology_slug"] == "2x_nvidia_b200"
    assert summary["gpu"]["configured_topology_slug"] == "4x_nvidia_b200"


def test_summarize_run_environment_queries_only_visible_devices(monkeypatch):
    captured = {}

    def fake_query(device_ids=None):
        captured["device_ids"] = device_ids
        return "2, NVIDIA B200, 183359\n3, NVIDIA B200, 183359\n"

    monkeypatch.setattr("ds4_harness.run_environment.query_nvidia_smi_gpu_csv", fake_query)

    summary = summarize_run_environment(env={"CUDA_VISIBLE_DEVICES": "2,3"})

    assert captured["device_ids"] == "2,3"
    assert summary["gpu"]["count"] == 2


def test_env_summary_cli_writes_json_and_markdown(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "ds4_harness.run_environment.query_nvidia_smi_gpu_csv",
        lambda device_ids=None: "0, Test GPU, 49152\n",
    )
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    monkeypatch.setenv("DEEPSEEK_BETA_BASE_URL", "https://api.deepseek.com/beta")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    monkeypatch.setenv("DEEPSEEK_PRESERVE_REASONING_CONTENT", "1")
    json_output = tmp_path / "run_environment.json"
    markdown_output = tmp_path / "run_environment.md"

    rc = cli.main(
        [
            "env-summary",
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    data = json.loads(json_output.read_text(encoding="utf-8"))
    assert data["official_api"]["api_key_present"] is True
    report = markdown_output.read_text(encoding="utf-8")
    assert "# Run Environment" in report
    assert "Test GPU" in report
    assert "deepseek-v4-flash" in report
    assert "Preserve reasoning_content" in report
    assert "secret" not in report


def test_write_run_environment_markdown_handles_no_gpu(tmp_path):
    output = tmp_path / "run_environment.md"

    write_run_environment_markdown(
        output,
        {
            "official_api": {"api_key_present": False},
            "gpu": {"available": False, "reason": "nvidia-smi unavailable"},
            "artifact": {"out_dir": "artifacts/main/unknown-gpu/run"},
        },
    )

    report = output.read_text(encoding="utf-8")
    assert "nvidia-smi unavailable" in report
