import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_acceptance_script_runs_coding_smoke_gate():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert "--tag coding" in script
    assert "smoke_coding.jsonl" in script


def test_acceptance_script_runs_static_harness_gates():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert '"${PYTHON}" -m ruff check ds4_harness tests' in script
    assert '"${PYTHON}" -m compileall -q ds4_harness' in script


def test_scripts_allow_explicit_python_interpreter():
    for script_name in ("run_acceptance.sh", "run_bench_matrix.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

        assert 'PYTHON="${PYTHON:-python}"' in script
        assert '"${PYTHON}" -m ds4_harness.cli' in script


def test_bench_script_defaults_to_representative_hf_dataset():
    script = (ROOT / "scripts" / "run_bench_matrix.sh").read_text(encoding="utf-8")

    assert 'CONCURRENCY="${CONCURRENCY:-1,2,4,8,16,24}"' in script
    assert 'DATASET_NAME="${DATASET_NAME:-hf}"' in script
    assert 'DATASET_PATH="${DATASET_PATH:-philschmid/mt-bench}"' in script
    assert 'TOKENIZER_MODE="${TOKENIZER_MODE:-deepseek_v4}"' in script
    assert 'IGNORE_EOS="${IGNORE_EOS:-0}"' in script
    assert '--dataset-name "${DATASET_NAME}"' in script
    assert '--dataset-path "${DATASET_PATH}"' in script
    assert '--tokenizer-mode "${TOKENIZER_MODE}"' in script
    assert 'EXTRA_ARGS+=(--ignore-eos)' in script
    assert '${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}' in script


def test_scripts_default_to_branch_timestamped_artifacts_dir():
    for script_name in ("run_acceptance.sh", "run_bench_matrix.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

        assert 'REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"' in script
        assert 'ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"' in script
        assert 'RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"' in script
        assert 'git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD' in script
        assert 'OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${RUN_TIMESTAMP}}"' in script
        assert "/tmp/ds4-sm120" not in script


def test_acceptance_script_writes_human_markdown_smoke_reports():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert '--markdown-output "${OUT_DIR}/smoke_quick.md"' in script
    assert '--markdown-output "${OUT_DIR}/smoke_quality.md"' in script
    assert '--markdown-output "${OUT_DIR}/smoke_coding.md"' in script


def test_acceptance_script_runs_all_gates_and_records_exit_codes():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert "failures=0" in script
    assert "run_gate pytest" in script
    assert "run_gate smoke_quick" in script
    assert "run_gate smoke_quality" in script
    assert "run_gate smoke_coding" in script
    assert "run_gate toolcall15" in script
    assert "run_gate oracle_compare" in script
    assert '"${OUT_DIR}/${name}.exit_code"' in script
    assert "exit ${failures}" in script


def test_scripts_capture_gpu_stats_to_artifacts():
    helper = (ROOT / "scripts" / "gpu_stats.sh").read_text(encoding="utf-8")

    assert 'GPU_STATS="${GPU_STATS:-1}"' in helper
    assert "nvidia-smi" in helper
    assert "memory.used" in helper
    assert "power.draw" in helper
    assert "uuid" not in helper
    assert '"${OUT_DIR}/gpu_stats.csv"' in helper
    assert "gpu-summary" in helper
    assert '"${OUT_DIR}/gpu_stats_summary.json"' in helper
    assert '"${OUT_DIR}/gpu_stats_summary.md"' in helper

    for script_name in ("run_acceptance.sh", "run_bench_matrix.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

        assert 'source "${SCRIPT_DIR}/gpu_stats.sh"' in script
        assert "start_gpu_stats" in script
        assert "trap stop_gpu_stats EXIT" in script


def test_sm12x_env_examples_use_requested_cuda_arch_family():
    handoff = (ROOT / "HANDOFF.md").read_text(encoding="utf-8")
    env_example = (ROOT / "configs" / "sm120_tp2_serve.env.example").read_text(
        encoding="utf-8"
    )

    assert "12.0f" in handoff
    assert "120f" in handoff
    assert "12.0a" in handoff
    assert "120a" in handoff
    assert "12.1a" in handoff
    assert "121a" in handoff
    assert 'CUDA_ARCH_LIST="120a"' in env_example
    assert 'TORCH_CUDA_ARCH_LIST="12.0a"' in env_example


def test_scripts_have_valid_bash_syntax():
    for script_name in ("run_acceptance.sh", "run_bench_matrix.sh", "gpu_stats.sh"):
        subprocess.run(
            ["bash", "-n", str(ROOT / "scripts" / script_name)],
            check=True,
            cwd=ROOT,
        )


def test_bench_wrapper_can_run_with_mocked_python(tmp_path):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "#!/usr/bin/env sh\n"
        "mkdir -p \"$OUT_DIR\"\n"
        "printf '%s\\n' \"$@\" > \"$OUT_DIR/fake_python_args.txt\"\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_python.chmod(fake_python.stat().st_mode | 0o111)
    out_dir = tmp_path / "out"
    env = os.environ | {
        "PYTHON": str(fake_python),
        "OUT_DIR": str(out_dir),
        "GPU_STATS": "0",
        "VLLM_BIN": "fake-vllm",
        "CONCURRENCY": "1",
        "NUM_PROMPTS": "1",
    }

    subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_bench_matrix.sh")],
        check=True,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    args = (out_dir / "fake_python_args.txt").read_text(encoding="utf-8")
    assert "ds4_harness.cli" in args
    assert "bench-matrix" in args
    assert "--json-output" in args
