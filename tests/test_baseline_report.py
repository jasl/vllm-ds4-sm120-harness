import json

from ds4_harness import cli
from ds4_harness.baseline_report import (
    _parse_serve_command,
    _reference_gpu_rental_hourly_usd,
    build_baseline_report,
)


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_fixture_phase(root, variant, phase, *, output_tok_s=1600.0):
    phase_dir = root / variant / phase
    phase_dir.mkdir(parents=True, exist_ok=True)
    (root / variant).mkdir(parents=True, exist_ok=True)
    serve_args = (
        "deepseek-ai/DeepSeek-V4-Flash --trust-remote-code --kv-cache-dtype fp8 "
        "--block-size 256 --max-model-len 393216 --tensor-parallel-size 4 "
        "--max-num-seqs 16 --max-num-batched-tokens 1024 "
        "--gpu-memory-utilization 0.35 --moe-backend triton_unfused "
        "--async-scheduling --enforce-eager "
        "--host 127.0.0.1 --port 8080 "
        "--no-enable-flashinfer-autotune --attention_config.use_fp4_indexer_cache=True "
        "--reasoning-parser deepseek_v4 --tokenizer-mode deepseek_v4 "
        "--tool-call-parser deepseek_v4 --enable-auto-tool-choice"
    )
    if variant == "mtp":
        serve_args += " --speculative_config '{\"method\":\"mtp\",\"num_speculative_tokens\":2}'"
    (root / variant / "serve_command.sh").write_text(
        "#!/usr/bin/env bash\n"
        "export VLLM_ENGINE_READY_TIMEOUT_S=3600\n"
        f"/workspace/vllm/.venv/bin/vllm serve {serve_args}\n",
        encoding="utf-8",
    )
    (phase_dir / "vllm_collect_env.txt").write_text(
        "\n".join(
            [
                "PyTorch version              : 2.11.0+cu130",
                "CUDA runtime version         : 13.0.88",
                "Nvidia driver version        : 595.58.03",
                "vLLM Version                 : 0.20.1rc1.dev138+g51295793a (git sha: 51295793a)",
                "  CUDA Archs: 12.0f; ROCm: Disabled; XPU: Disabled",
                "[pip3] transformers==5.7.0",
                "[pip3] triton==3.6.0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_json(
        phase_dir / "run_environment.json",
        {
            "generated_at_utc": "2026-05-01T18:45:14+00:00",
            "artifact": {
                "branch_name": "main",
                "gpu_topology_slug": "4x_nvidia_b200",
                "run_timestamp": "20260501184103",
            },
            "harness": {
                "model": "deepseek-ai/DeepSeek-V4-Flash",
                "dataset_name": "hf",
                "dataset_path": "philschmid/mt-bench",
                "concurrency": "1,2,4,8,16,24",
            },
            "gpu": {
                "available": True,
                "count": 4,
                "topology_slug": "4x_nvidia_b200",
                "models": [
                    {
                        "name": "NVIDIA B200",
                        "count": 4,
                        "memory_total_mib_each": 183359.0,
                    }
                ],
            },
        },
    )
    _write_json(
        phase_dir / "gpu_stats_summary.json",
        {
            "available": True,
            "sample_count": 16,
            "overall": {
                "power_draw_w_avg": 320.0,
                "power_draw_w_max": 410.0,
                "gpu_utilization_percent_avg": 70.0,
                "memory_used_mib_max": 170884.0,
            },
            "gpus": {
                str(index): {
                    "name": "NVIDIA B200",
                    "memory_total_mib_max": 183359.0,
                    "memory_used_mib_max": 170884.0,
                    "power_draw_w_avg": 320.0,
                    "power_draw_w_max": 410.0,
                    "gpu_utilization_percent_avg": 70.0,
                }
                for index in range(4)
            },
        },
    )
    _write_json(
        phase_dir / "bench.json",
        [
            {
                "concurrency": 1,
                "ok": True,
                "detail": "successful_requests 80/80",
                "metrics": {
                    "successful_requests": 80,
                    "benchmark_duration_s": 10.0,
                    "total_input_tokens": 20000,
                    "total_generated_tokens": 16000,
                    "request_throughput_req_s": 8.0,
                    "output_token_throughput_tok_s": output_tok_s,
                    "mean_ttft_ms": 100.0,
                    "mean_tpot_ms": 5.5,
                    "mean_itl_ms": 7.5,
                },
            }
        ],
    )
    return phase_dir


def _write_fixture_run(tmp_path):
    root = tmp_path / "baseline"
    eval_dir = root / "nomtp" / "eval_gsm8k"
    long_context_dir = root / "nomtp" / "long_context_probe"
    _write_json(
        eval_dir / "lm_eval_summary.json",
        {
            "ok": True,
            "tasks": [
                {
                    "task": "gsm8k",
                    "version": 3,
                    "exact_match_flexible": 0.9439,
                    "exact_match_strict": 0.9431,
                    "exact_match_flexible_stderr": 0.0063,
                }
            ],
            "config": {
                "num_fewshot": 8,
                "num_concurrent": 4,
                "max_gen_toks": 2048,
            },
        },
    )
    phase_rows = [
        ("nomtp", "server_startup", 0, root / "nomtp" / "server_startup"),
        ("nomtp", "acceptance", 1, root / "nomtp" / "acceptance"),
        ("nomtp", "long_context_probe", 0, long_context_dir),
        ("nomtp", "bench_hf_mt_bench", 0, _write_fixture_phase(root, "nomtp", "bench_hf_mt_bench")),
        ("nomtp", "eval_gsm8k", 0, eval_dir),
        ("mtp", "server_startup", 0, root / "mtp" / "server_startup"),
        ("mtp", "acceptance", 1, root / "mtp" / "acceptance"),
        ("mtp", "bench_hf_mt_bench", 0, _write_fixture_phase(root, "mtp", "bench_hf_mt_bench", output_tok_s=2000.0)),
    ]
    acceptance_dir = root / "nomtp" / "acceptance"
    _write_json(
        acceptance_dir / "run_environment.json",
        {
            "generated_at_utc": "2026-05-01T18:45:14+00:00",
            "artifact": {
                "branch_name": "main",
                "gpu_topology_slug": "4x_nvidia_b200",
                "run_timestamp": "20260501184103",
            },
            "harness": {
                "model": "deepseek-ai/DeepSeek-V4-Flash",
                "dataset_name": "hf",
                "dataset_path": "philschmid/mt-bench",
            },
            "gpu": {
                "available": True,
                "count": 4,
                "topology_slug": "4x_nvidia_b200",
                "models": [
                    {
                        "name": "NVIDIA B200",
                        "count": 4,
                        "memory_total_mib_each": 183359.0,
                    }
                ],
            },
        },
    )
    _write_json(
        acceptance_dir / "gpu_stats_summary.json",
        {
            "available": True,
            "overall": {"power_draw_w_avg": 320.0},
            "gpus": {
                str(index): {
                    "name": "NVIDIA B200",
                    "power_draw_w_avg": 320.0,
                }
                for index in range(4)
            },
        },
    )
    _write_json(
        long_context_dir / "long_context_probe.json",
        {
            "case": "kv_indexer_long_context",
            "variant": "nomtp",
            "ok": True,
            "detail": "matched long-context sentinel terms",
            "elapsed_seconds": 3.5,
            "usage": {
                "prompt_tokens": 47000,
                "completion_tokens": 20,
                "total_tokens": 47020,
            },
            "prompt": {
                "line_count": 2400,
                "sha256": "abc123",
            },
            "missing_terms": [],
        },
    )
    (acceptance_dir / "generation.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "case": "translation_en_to_zh",
                        "language": "en",
                        "workload": "translation",
                        "tags": ["translation", "subjective"],
                        "round": 1,
                        "thinking_mode": "think-high",
                        "variant": "nomtp",
                        "ok": True,
                        "elapsed_seconds": 1.0,
                        "usage": {
                            "prompt_tokens": 50,
                            "completion_tokens": 60,
                            "total_tokens": 110,
                        },
                    }
                ),
                json.dumps(
                    {
                        "case": "writing_local_inference_tradeoffs",
                        "language": "en",
                        "workload": "writing",
                        "tags": ["writing", "subjective"],
                        "round": 1,
                        "thinking_mode": "think-high",
                        "variant": "nomtp",
                        "ok": True,
                        "elapsed_seconds": 2.0,
                        "usage": {
                            "prompt_tokens": 100,
                            "completion_tokens": 200,
                            "total_tokens": 300,
                        },
                    }
                ),
                json.dumps(
                    {
                        "case": "aquarium_html",
                        "language": "en",
                        "workload": "coding",
                        "tags": ["coding", "html", "subjective"],
                        "round": 1,
                        "thinking_mode": "think-high",
                        "variant": "nomtp",
                        "ok": True,
                        "elapsed_seconds": 10.0,
                        "usage": {
                            "prompt_tokens": 200,
                            "completion_tokens": 800,
                            "total_tokens": 1000,
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_json(
        acceptance_dir / "toolcall15.json",
        {
            "summary": {
                "cases": 15,
                "points": 24,
                "max_points": 30,
                "score_percent": 80,
                "failures": 1,
            },
            "results": [
                {
                    "id": "TC-06",
                    "status": "fail",
                    "points": 0,
                    "summary": "Did not split the translation request into two valid calls.",
                    "ok": False,
                    "elapsed_seconds": 3.0,
                    "usage_totals": {
                        "prompt_tokens": 300,
                        "completion_tokens": 100,
                        "total_tokens": 400,
                    },
                }
            ],
        },
    )
    lines = ["variant\tphase\texit_code\tartifact_dir"]
    lines.extend(
        f"{variant}\t{phase}\t{exit_code}\t{phase_dir}"
        for variant, phase, exit_code, phase_dir in phase_rows
    )
    root.mkdir(parents=True, exist_ok=True)
    (root / "phase_exit_codes.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return root


def test_reference_rental_hourly_costs_cover_sm12x_dev_hosts():
    assert (
        _reference_gpu_rental_hourly_usd(
            {
                "gpu": {
                    "models": [
                        {
                            "name": "NVIDIA RTX PRO 6000 Blackwell Workstation Edition",
                            "count": 2,
                        }
                    ]
                }
            }
        )
        == 1.92
    )
    assert (
        _reference_gpu_rental_hourly_usd(
            {
                "gpu": {
                    "models": [
                        {
                            "name": "NVIDIA DGX Spark",
                            "count": 2,
                        }
                    ]
                }
            }
        )
        == 0.96
    )


def test_parse_serve_command_handles_multiline_shell_continuations():
    row = _parse_serve_command(
        """#!/usr/bin/env bash
export VLLM_ENGINE_READY_TIMEOUT_S=3600
HF_HOME=/workspace/.hf_home /workspace/vllm/.venv/bin/vllm serve deepseek-ai/DeepSeek-V4-Flash \\
  --trust-remote-code \\
  --kv-cache-dtype fp8 \\
  --block-size 256 \\
  --max-model-len 393216 \\
  --tensor-parallel-size 4 \\
  --max-num-seqs 16 \\
  --max-num-batched-tokens 1024 \\
  --gpu-memory-utilization 0.35 \\
  --moe-backend triton_unfused \\
  --async-scheduling \\
  --enforce-eager \\
  --reasoning-parser deepseek_v4 \\
  --tokenizer-mode deepseek_v4 \\
  --tool-call-parser deepseek_v4 \\
  --enable-auto-tool-choice
"""
    )

    assert row["model"] == "deepseek-ai/DeepSeek-V4-Flash"
    assert row["kv_cache_dtype"] == "fp8"
    assert row["max_model_len"] == "393216"
    assert row["max_num_seqs"] == "16"
    assert row["max_num_batched_tokens"] == "1024"
    assert row["gpu_memory_utilization"] == "0.35"
    assert row["moe_backend"] == "triton_unfused"
    assert row["async_scheduling"] is True
    assert row["enforce_eager"] is True
    assert row["auto_tool_choice"] is True


def test_build_baseline_report_includes_normalized_efficiency_and_accuracy(tmp_path):
    run_dir = _write_fixture_run(tmp_path)

    report = build_baseline_report(
        run_dir,
        title="Unit B200 Baseline",
        label="unit_b200",
    )

    assert "# Unit B200 Baseline" in report
    assert "## Provenance" in report
    assert "0.20.1rc1.dev138+g51295793a" in report
    assert "51295793a" in report
    assert "2.11.0+cu130" in report
    assert "13.0.88" in report
    assert "595.58.03" in report
    assert "## Serve Shape" in report
    assert "| `nomtp` | `fp8` | 256 | 393216 | 4 | 16 | 1024 | 0.35 | `n/a` | `triton_unfused` | yes | yes | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | yes | yes |" in report
    assert '| `mtp` | `fp8` | 256 | 393216 | 4 | 16 | 1024 | 0.35 | `{"method":"mtp","num_speculative_tokens":2}` | `triton_unfused` | yes | yes | `deepseek_v4` | `deepseek_v4` | `deepseek_v4` | yes | yes | yes |' in report
    assert "## Quick Performance Summary" in report
    assert "### Real Scenario OP Cost Estimate" in report
    assert (
        "| `nomtp` | writing | 1 | 100.00 | 2.00 | 100.00 | 100 | 200 | "
        "$0.0037 | $3.73 | $37.31 | $18.65 | $7.46 | $6.72 |"
    ) in report
    assert "#### Rental / Cloud GPU-Hour" in report
    assert (
        "| `nomtp` | writing | 1 | 100.00 | 2.00 | 100.00 | 100 | 200 | "
        "$0.0084 | $8.44 | $84.44 | $42.22 | $16.89 | $15.20 |"
    ) in report
    assert "### Best Benchmark Throughput" in report
    assert "| Primary | `nomtp` | HF/MT-Bench | 1 | 1600.00 | 400.00 | 100.00 | 5.50 |" in report
    assert "B200: `$30,000/GPU`" in report
    assert "B200: `$3.80/GPU-hour`" in report
    assert "## Normalized Efficiency" in report
    assert "tok/s/GPU" in report
    assert "tok/J" in report
    assert (
        "| `nomtp` | HF/MT-Bench | 1 | 80/80 | 1600.00 | 400.00 | "
        "2.23 | 2.40 | 1.25 | 1250.00 |"
    ) in report
    assert "## ToolCall-15" in report
    assert "`TC-06`" in report
    assert "Did not split the translation request" in report
    assert "## Long Context Probes" in report
    assert (
        "| `nomtp` | `kv_indexer_long_context` | yes | 2400 | 47000 | "
        "20 | 3.50 | matched long-context sentinel terms |"
    ) in report
    assert "## Accuracy Evals" in report
    assert "| `nomtp` | GSM8K | 3 | yes | 8 | 4 | 2048 | 94.39 | 94.31 | 0.0063 |" in report


def test_baseline_report_cli_writes_markdown_and_reads_supplement_runtime(tmp_path):
    run_dir = _write_fixture_run(tmp_path)
    supplement_dir = tmp_path / "supplement"
    phase_dir = _write_fixture_phase(
        supplement_dir,
        "mtp",
        "bench_hf_mt_bench",
        output_tok_s=2100.0,
    )
    _write_json(
        phase_dir / "runtime_stats_summary.json",
        {
            "metrics": {
                "available": True,
                "prefill_tokens_delta": 1234.0,
                "decode_tokens_delta": 5678.0,
                "running_requests_max": 24.0,
            },
            "serve_log": {
                "available": True,
                "prefill_throughput_tok_s_avg": 111.0,
                "decode_throughput_tok_s_avg": 222.0,
                "spec_decode": {
                    "samples": 4,
                    "mean_acceptance_length_avg": 2.1,
                    "avg_draft_acceptance_rate_percent_avg": 67.5,
                    "per_position_acceptance_rate_avg": [0.81, 0.54],
                    "accepted_tokens_observed": 1200.0,
                    "drafted_tokens_observed": 1800.0,
                },
            },
        },
    )
    (supplement_dir / "phase_exit_codes.tsv").write_text(
        "\n".join(
            [
                "variant\tphase\texit_code\tartifact_dir",
                f"mtp\tbench_hf_mt_bench\t0\t{phase_dir}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "report.md"

    rc = cli.main(
        [
            "baseline-report",
            "--run-dir",
            str(run_dir),
            "--supplement-dir",
            str(supplement_dir),
            "--title",
            "Unit Report",
            "--label",
            "unit",
            "--output",
            str(output),
        ]
    )

    assert rc == 0
    report = output.read_text(encoding="utf-8")
    assert "# Unit Report" in report
    assert "### Runtime Prefill/Decode Averages" in report
    assert "| Supplement | `mtp` | HF/MT-Bench | 111.00 | 222.00 | 1234 | 5678 | 24 |" in report
    assert "## Supplement Runtime Stats" in report
    assert "## MTP Speculative Decoding" in report
    assert "`[0.810, 0.540]`" in report
    assert str(tmp_path) not in report
