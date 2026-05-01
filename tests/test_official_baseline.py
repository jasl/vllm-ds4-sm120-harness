import json

from ds4_harness.official_baseline import build_official_api_baseline
from ds4_harness.reference_bundle import scan_public_bundle


def test_official_api_baseline_writes_report_and_public_outputs(tmp_path):
    artifact_dir = (
        tmp_path
        / "artifacts"
        / "official_api"
        / "deepseek-v4-flash"
        / "20260502120000"
    )
    artifact_dir.mkdir(parents=True)
    generation_row = {
        "case": "translation_en_to_zh",
        "language": "en",
        "workload": "translation",
        "thinking_mode": "think-high",
        "thinking_strength": "high",
        "variant": "official-api",
        "ok": True,
        "detail": "matched expectation",
        "elapsed_seconds": 1.25,
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        "payload": {
            "model": "deepseek-v4-flash",
            "messages": [{"content": "Translate."}],
        },
        "response": {"model": "deepseek-v4-flash", "choices": []},
    }
    (artifact_dir / "official_generation.jsonl").write_text(
        json.dumps(generation_row, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    transcript = (
        artifact_dir
        / "generation"
        / "en"
        / "translation_en_to_zh.1.think-high.official-api.md"
    )
    transcript.parent.mkdir(parents=True)
    transcript.write_text("# Generation Transcript\n", encoding="utf-8")
    (artifact_dir / "official_smoke.jsonl").write_text(
        json.dumps(
            {
                "case": "math_7_times_8",
                "ok": True,
                "detail": "matched expectation",
                "response": {"usage": {"total_tokens": 12}},
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (artifact_dir / "official_smoke.md").write_text("# Smoke\n", encoding="utf-8")
    (artifact_dir / "official_toolcall15.json").write_text(
        json.dumps(
            {
                "summary": {
                    "points": 28,
                    "max_points": 30,
                    "total_cases": 15,
                    "failures": 1,
                },
                "results": [{"id": "TC-06", "status": "fail", "summary": "miss"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (artifact_dir / "official_generation.exit_code").write_text("0\n", encoding="utf-8")
    (artifact_dir / "official_smoke.exit_code").write_text("0\n", encoding="utf-8")
    (artifact_dir / "official_toolcall15.exit_code").write_text("1\n", encoding="utf-8")

    output_dir = tmp_path / "baselines" / "20260502_deepseek_official_api_flash"
    build_official_api_baseline(
        artifact_dir=artifact_dir,
        output_dir=output_dir,
        label="deepseek_official_api_flash",
        date="20260502",
    )

    report = (output_dir / "report.md").read_text(encoding="utf-8")
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    generation = json.loads(
        (output_dir / "generation" / "official_api.json").read_text(
            encoding="utf-8"
        )
    )
    smoke = json.loads(
        (output_dir / "smoke" / "official_api.json").read_text(encoding="utf-8")
    )

    assert "# DeepSeek Official API Baseline" in report
    assert "translation_en_to_zh" in report
    assert "28/30" in report
    assert "TC-06" in report
    assert manifest["source"]["artifact_run"] == "20260502120000"
    assert manifest["model"] == "deepseek-v4-flash"
    assert generation[0]["variant"] == "official-api"
    assert smoke[0]["case"] == "math_7_times_8"
    assert (output_dir / "generation" / "en" / transcript.name).exists()
    assert (output_dir / "toolcall15" / "official_api.json").exists()
    assert not scan_public_bundle(output_dir)


def test_official_api_baseline_cli_is_registered():
    from ds4_harness import cli

    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "official-baseline",
            "--artifact-dir",
            "artifacts/official_api/deepseek-v4-flash/20260502120000",
            "--output-dir",
            "baselines/20260502_deepseek_official_api_flash",
            "--label",
            "deepseek_official_api_flash",
            "--date",
            "20260502",
        ]
    )

    assert args.command == "official-baseline"
    assert str(args.output_dir).endswith(
        "baselines/20260502_deepseek_official_api_flash"
    )
