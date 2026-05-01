import json

from ds4_harness.oracle import load_oracle_cases
from ds4_harness.reference_bundle import (
    build_reference_bundle,
    scan_public_bundle,
)


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _minimal_completion(name):
    return {
        "name": name,
        "path": "/v1/completions",
        "status": 200,
        "elapsed_seconds": 0.1,
        "request": {
            "model": "deepseek-ai/DeepSeek-V4-Flash",
            "prompt": "Question: What is 7*8?\nAnswer:",
            "max_tokens": 16,
            "temperature": 0.0,
            "logprobs": 20,
        },
        "tokenize_response": {"tokens": [1, 2, 3]},
        "response": {
            "choices": [
                {
                    "text": " 56",
                    "logprobs": {
                        "tokens": [" ", "56"],
                        "token_logprobs": [-0.1, -0.2],
                        "top_logprobs": [{" ": -0.1}, {"56": -0.2}],
                    },
                    "prompt_token_ids": [1, 2, 3],
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 3, "completion_tokens": 2},
        },
    }


def test_reference_bundle_writes_sanitized_oracle_and_smoke_data(tmp_path):
    run_dir = tmp_path / "artifacts" / "main" / "4x_nvidia_b200" / "label" / "run"
    oracle_dir = run_dir / "nomtp" / "oracle_export"
    mtp_oracle_dir = run_dir / "mtp" / "oracle_export"
    _write_json(
        oracle_dir / "completion_short_math_logprobs20.json",
        _minimal_completion("completion_short_math_logprobs20"),
    )
    _write_json(
        oracle_dir / "oracle_export_summary.json",
        {
            "base_url": "http://127.0.0.1:8080",
            "model": "deepseek-ai/DeepSeek-V4-Flash",
            "results": [],
            "files": [
                "completion_short_math_logprobs20.json",
                "run_environment.json",
            ],
        },
    )
    (oracle_dir / "oracle_export_summary.md").write_text(
        "# Oracle Export Summary\n", encoding="utf-8"
    )
    _write_json(
        mtp_oracle_dir / "completion_short_math_logprobs20.json",
        _minimal_completion("completion_short_math_logprobs20"),
    )
    _write_json(
        mtp_oracle_dir / "oracle_export_summary.json",
        {
            "base_url": "http://127.0.0.1:8080",
            "model": "deepseek-ai/DeepSeek-V4-Flash",
            "results": [],
            "files": ["completion_short_math_logprobs20.json"],
        },
    )
    (mtp_oracle_dir / "oracle_export_summary.md").write_text(
        "# MTP Oracle Export Summary\n", encoding="utf-8"
    )

    smoke_dir = run_dir / "nomtp" / "acceptance"
    smoke_dir.mkdir(parents=True)
    (smoke_dir / "smoke_quick.jsonl").write_text(
        json.dumps(
            {
                "case": "openclaw_read",
                "payload": {"messages": [{"content": "read /home/user/state.md"}]},
                "response": {
                    "choices": [
                        {
                            "message": {
                                "tool_calls": [
                                    {
                                        "function": {
                                            "name": "read",
                                            "arguments": '{"path": "/home/user/state.md"}',
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                },
                "ok": True,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (smoke_dir / "smoke_quick.md").write_text(
        "assistant used /home/user/state.md  \nsecond line\n", encoding="utf-8"
    )
    (smoke_dir / "generation.jsonl").write_text(
        json.dumps(
            {
                "case": "translation_en_to_zh",
                "language": "en",
                "thinking_mode": "think-high",
                "variant": "nomtp",
                "payload": {"model": "m", "messages": [{"content": "/workspace/leak"}]},
                "response": {"usage": {"prompt_tokens": 1}},
                "ok": True,
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (smoke_dir / "generation" / "en").mkdir(parents=True)
    (smoke_dir / "generation" / "en" / "translation_en_to_zh.1.think-high.nomtp.md").write_text(
        "Prompt from /workspace/leak\n", encoding="utf-8"
    )
    _write_json(
        smoke_dir / "toolcall15.json",
        {"summary": {"cases": 1}, "results": [{"final_answer": "/workspace/leak"}]},
    )

    bench_dir = run_dir / "nomtp" / "bench_hf_mt_bench"
    _write_json(
        bench_dir / "bench.json",
        [
            {
                "concurrency": 1,
                "metrics": {"output_token_throughput_tok_s": 123.4},
                "command": ["/workspace/vllm/.venv/bin/vllm", "bench", "serve"],
            }
        ],
    )
    _write_json(
        bench_dir / "gpu_stats_summary.json",
        {"overall": {"gpu_utilization_percent_avg": 70.0}, "gpus": {}},
    )
    _write_json(
        bench_dir / "runtime_stats_summary.json",
        {"serve_log": {"decode_throughput_tok_s_avg": 200.0}},
    )
    _write_json(
        bench_dir / "run_environment.json",
        {
            "harness": {
                "vllm_bin": "/workspace/vllm/.venv/bin/vllm",
                "python": "/workspace/vllm/.venv/bin/python",
                "model": "deepseek-ai/DeepSeek-V4-Flash",
            },
            "gpu": {
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
    (bench_dir / "vllm_collect_env.txt").write_text(
        "vLLM Version                 : 0.20.1 (git sha: 51295793a)\n"
        "Nvidia driver version        : 595.58.03\n"
        "CUDA runtime version         : 13.0.88\n",
        encoding="utf-8",
    )

    out_dir = tmp_path / "reference"
    build_reference_bundle(
        run_dir=run_dir,
        output_dir=out_dir,
        label="b200_test",
        date="20260501",
    )

    assert (out_dir / "README.md").exists()
    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "oracle" / "completion_short_math_logprobs20.json").exists()
    assert (
        out_dir / "oracle" / "nomtp" / "completion_short_math_logprobs20.json"
    ).exists()
    assert (
        out_dir / "oracle" / "mtp" / "completion_short_math_logprobs20.json"
    ).exists()
    assert (out_dir / "smoke" / "nomtp_quick.json").exists()
    assert (out_dir / "generation" / "nomtp.json").exists()
    assert (
        out_dir
        / "generation"
        / "en"
        / "translation_en_to_zh.1.think-high.nomtp.md"
    ).exists()
    assert (out_dir / "toolcall15" / "nomtp.json").exists()
    assert (out_dir / "performance" / "primary.json").exists()

    assert not scan_public_bundle(out_dir)
    manifest = json.loads((out_dir / "manifest.json").read_text())
    assert "subjective_quality" in manifest["contents"]
    assert "Known Non-Green Gates" in (out_dir / "README.md").read_text()
    assert load_oracle_cases(out_dir / "oracle")[0].name == (
        "completion_short_math_logprobs20"
    )
    oracle_summary = json.loads(
        (out_dir / "oracle" / "oracle_export_summary.json").read_text()
    )
    assert oracle_summary["files"] == ["completion_short_math_logprobs20.json"]

    smoke = json.loads((out_dir / "smoke" / "nomtp_quick.json").read_text())
    assert smoke[0]["payload"]["messages"][0]["content"] == (
        "read <synthetic-home>/state.md"
    )
    generation = json.loads((out_dir / "generation" / "nomtp.json").read_text())
    assert generation[0]["payload"]["messages"][0]["content"] == "<workspace>/leak"
    assert "  \n" not in (out_dir / "smoke" / "nomtp_quick.md").read_text()
    assert "<workspace>/leak" in (
        out_dir / "generation" / "en" / "translation_en_to_zh.1.think-high.nomtp.md"
    ).read_text()
    toolcall = json.loads((out_dir / "toolcall15" / "nomtp.json").read_text())
    assert toolcall["results"][0]["final_answer"] == "<workspace>/leak"
    perf = json.loads((out_dir / "performance" / "primary.json").read_text())
    assert perf["phases"][0]["bench"][0]["command"][0] == "vllm"


def test_reference_bundle_cli_is_registered():
    from ds4_harness import cli

    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "reference-bundle",
            "--run-dir",
            "artifacts/main/4x_nvidia_b200/b200_main/20260501000000",
            "--output-dir",
            "baselines/20260501_b200_main",
            "--label",
            "b200_main",
        ]
    )

    assert args.command == "reference-bundle"
    assert str(args.output_dir).endswith("baselines/20260501_b200_main")
