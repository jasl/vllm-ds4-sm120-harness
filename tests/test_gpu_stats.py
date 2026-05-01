import json

from ds4_harness.gpu_stats import summarize_gpu_csv, write_gpu_markdown


def test_summarize_gpu_csv_reports_memory_and_power(tmp_path):
    csv_path = tmp_path / "gpu_stats.csv"
    csv_path.write_text(
        "\n".join(
            [
                (
                    "timestamp, index, name, uuid, memory.used [MiB], "
                    "memory.total [MiB], power.draw [W], power.limit [W], "
                    "utilization.gpu [%]"
                ),
                "2026/05/01 21:30:00.000, 0, RTX PRO 6000, GPU-0, 1024, 98304, 250.5, 600, 78",
                "2026/05/01 21:30:01.000, 0, RTX PRO 6000, GPU-0, 2048, 98304, 300.0, 600, 90",
                "2026/05/01 21:30:00.000, 1, RTX PRO 6000, GPU-1, 4096, 98304, 275.0, 600, 65",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = summarize_gpu_csv(csv_path)

    assert summary["available"] is True
    assert summary["sample_count"] == 3
    assert summary["overall"]["memory_used_mib_max"] == 4096.0
    assert summary["overall"]["power_draw_w_max"] == 300.0
    gpu0 = summary["gpus"]["0"]
    assert gpu0["samples"] == 2
    assert gpu0["memory_used_mib_max"] == 2048.0
    assert gpu0["memory_used_mib_avg"] == 1536.0
    assert gpu0["power_draw_w_avg"] == 275.25
    assert gpu0["gpu_utilization_percent_max"] == 90.0


def test_write_gpu_markdown_is_human_readable(tmp_path):
    summary = {
        "available": True,
        "sample_count": 2,
        "overall": {
            "memory_used_mib_max": 2048.0,
            "power_draw_w_max": 300.0,
        },
        "gpus": {
            "0": {
                "name": "RTX PRO 6000",
                "uuid": "GPU-0",
                "samples": 2,
                "memory_used_mib_max": 2048.0,
                "memory_used_percent_max": 2.08,
                "power_draw_w_max": 300.0,
                "power_draw_w_avg": 275.25,
                "gpu_utilization_percent_max": 90.0,
            }
        },
    }
    output = tmp_path / "gpu_stats_summary.md"

    write_gpu_markdown(output, summary)

    report = output.read_text(encoding="utf-8")
    assert "# GPU Stats Summary" in report
    assert "RTX PRO 6000" in report
    assert "2048.0 MiB" in report
    assert "300.0 W" in report


def test_gpu_summary_cli_writes_json_and_markdown(tmp_path):
    from ds4_harness import cli

    csv_path = tmp_path / "gpu_stats.csv"
    json_output = tmp_path / "summary.json"
    markdown_output = tmp_path / "summary.md"
    csv_path.write_text(
        "\n".join(
            [
                "timestamp, index, name, memory.used [MiB], memory.total [MiB], power.draw [W]",
                "2026/05/01 21:30:00.000, 0, RTX PRO 6000, 512, 98304, 200",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    rc = cli.main(
        [
            "gpu-summary",
            "--csv-input",
            str(csv_path),
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    assert json.loads(json_output.read_text(encoding="utf-8"))["sample_count"] == 1
    assert "RTX PRO 6000" in markdown_output.read_text(encoding="utf-8")
