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
    assert 'BENCH_TIMEOUT="${BENCH_TIMEOUT:-1800}"' in script
    assert 'IGNORE_EOS="${IGNORE_EOS:-0}"' in script
    assert '--dataset-name "${DATASET_NAME}"' in script
    assert '--dataset-path "${DATASET_PATH}"' in script
    assert '--tokenizer-mode "${TOKENIZER_MODE}"' in script
    assert '--timeout "${BENCH_TIMEOUT}"' in script
    assert 'EXTRA_ARGS+=(--ignore-eos)' in script
    assert '${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}' in script


def test_scripts_default_to_branch_timestamped_artifacts_dir():
    for script_name in ("run_acceptance.sh", "run_bench_matrix.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

        assert 'REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"' in script
        assert 'source "${SCRIPT_DIR}/run_context.sh"' in script
        assert "load_harness_env" in script
        assert "detect_gpu_topology_slug" in script
        assert 'ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"' in script
        assert 'RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d-%H%M%S)}"' in script
        assert 'git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD' in script
        assert 'GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"' in script
        assert (
            'OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${RUN_TIMESTAMP}}"'
            in script
        )
        assert "/tmp/ds4-sm120" not in script


def test_env_sample_and_local_env_are_configured():
    sample = (ROOT / "env.sample").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "DEEPSEEK_API_KEY=" in sample
    assert "DEEPSEEK_BASE_URL=https://api.deepseek.com" in sample
    assert "DEEPSEEK_BETA_BASE_URL=https://api.deepseek.com/beta" in sample
    assert "DEEPSEEK_MODEL=deepseek-v4-flash" in sample
    assert "DEEPSEEK_FLASH_MODEL=deepseek-v4-flash" in sample
    assert "DEEPSEEK_PRO_MODEL=deepseek-v4-pro" in sample
    assert "DEEPSEEK_THINKING_TYPE=enabled" in sample
    assert "DEEPSEEK_REASONING_EFFORT=high" in sample
    assert "DEEPSEEK_PRESERVE_REASONING_CONTENT=1" in sample
    assert "BASELINE_LABEL=b200_oracle" in sample
    assert "ORACLE_LOGPROBS=20" in sample
    assert "ORACLE_TIMEOUT=300" in sample
    assert "ORACLE_CASES=" in sample
    assert "SERVER_GUARD=1" in sample
    assert "SERVER_STARTUP_TIMEOUT=1800" in sample
    assert "SERVER_STARTUP_INTERVAL_SECONDS=15" in sample
    assert "SERVER_HEALTH_TIMEOUT=10" in sample
    assert "SERVER_FAILURE_GRACE_TIMEOUT=300" in sample
    assert "SERVER_RECOVERY_CMD=" in sample
    assert "GPU_TOPOLOGY_SLUG=" in sample
    assert ".env" in gitignore


def test_acceptance_script_writes_human_markdown_smoke_reports():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert '--markdown-output "${OUT_DIR}/smoke_quick.md"' in script
    assert '--markdown-output "${OUT_DIR}/smoke_quality.md"' in script
    assert '--markdown-output "${OUT_DIR}/smoke_coding.md"' in script


def test_acceptance_script_runs_all_gates_and_records_exit_codes():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert "failures=0" in script
    assert "run_gate pytest" in script
    assert "run_live_gate smoke_quick" in script
    assert "run_live_gate smoke_quality" in script
    assert "run_live_gate smoke_coding" in script
    assert "run_live_gate toolcall15" in script
    assert "run_live_gate oracle_compare" in script
    assert 'ORACLE_TOP_N="${ORACLE_TOP_N:-20}"' in script
    assert '--top-n "${ORACLE_TOP_N}"' in script
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
        assert "stop_gpu_stats" in script


def test_scripts_capture_vllm_runtime_stats_to_artifacts():
    helper = (ROOT / "scripts" / "runtime_stats.sh").read_text(encoding="utf-8")

    assert 'RUNTIME_STATS="${RUNTIME_STATS:-1}"' in helper
    assert "curl" in helper
    assert "/metrics" in helper
    assert '"${OUT_DIR}/vllm_metrics.prom"' in helper
    assert "runtime-summary" in helper
    assert '"${OUT_DIR}/runtime_stats_summary.json"' in helper
    assert '"${OUT_DIR}/runtime_stats_summary.md"' in helper

    for script_name in ("run_acceptance.sh", "run_bench_matrix.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

        assert 'source "${SCRIPT_DIR}/runtime_stats.sh"' in script
        assert "start_runtime_stats" in script
        assert "stop_runtime_stats" in script


def test_oracle_export_script_is_b200_ready():
    script = (ROOT / "scripts" / "run_oracle_export.sh").read_text(encoding="utf-8")

    assert "load_harness_env" in script
    assert "detect_gpu_topology_slug" in script
    assert "write_run_environment" in script
    assert "start_gpu_stats" in script
    assert "start_runtime_stats" in script
    assert "server_ready" in script
    assert "mark_server_unresponsive" in script
    assert "oracle-export" in script
    assert 'ORACLE_LOGPROBS="${ORACLE_LOGPROBS:-20}"' in script
    assert 'BASELINE_LABEL="${BASELINE_LABEL:-b200_oracle}"' in script
    assert '--output-dir "${OUT_DIR}"' in script
    assert "--stop-on-error" in script


def test_live_scripts_guard_against_unresponsive_servers():
    helper = (ROOT / "scripts" / "run_context.sh").read_text(encoding="utf-8")

    assert "server_ready()" in helper
    assert "wait_for_server_ready()" in helper
    assert "mark_server_unresponsive()" in helper
    assert "SERVER_RECOVERY_CMD" in helper
    assert "SERVER_STARTUP_TIMEOUT" in helper
    assert "server_unresponsive.txt" in helper

    acceptance = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")
    bench = (ROOT / "scripts" / "run_bench_matrix.sh").read_text(encoding="utf-8")

    assert "run_live_gate" in acceptance
    assert "run_live_gate_capture" in acceptance
    assert "mark_gate_skipped" in acceptance
    assert "SERVER_HEALTH_TIMEOUT" in acceptance
    assert "SERVER_STARTUP_TIMEOUT" in acceptance
    assert "--stop-on-unresponsive" in bench
    assert "--health-timeout" in bench
    assert "--failure-grace-timeout" in bench


def test_wait_for_server_ready_allows_slow_startup(tmp_path):
    script = f"""
set -euo pipefail
REPO_ROOT="{ROOT}"
OUT_DIR="{tmp_path}"
PYTHON=python
BASE_URL=http://127.0.0.1:9
SERVER_GUARD=1
SERVER_STARTUP_TIMEOUT=5
SERVER_STARTUP_INTERVAL_SECONDS=0
source "{ROOT / "scripts" / "run_context.sh"}"
count=0
server_ready() {{
  count=$((count + 1))
  [[ "${{count}}" -ge 2 ]]
}}
wait_for_server_ready "${{SERVER_STARTUP_TIMEOUT}}" "${{SERVER_STARTUP_INTERVAL_SECONDS}}" "test startup"
printf 'count=%s\\n' "${{count}}"
"""
    result = subprocess.run(
        ["bash", "-c", script],
        check=True,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert "count=2" in result.stdout
    assert (tmp_path / "server_wait.log").exists()


def test_scripts_write_run_environment_artifacts():
    helper = (ROOT / "scripts" / "run_context.sh").read_text(encoding="utf-8")

    assert '"${OUT_DIR}/run_environment.json"' in helper
    assert '"${OUT_DIR}/run_environment.md"' in helper
    for script_name in ("run_acceptance.sh", "run_bench_matrix.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

        assert "write_run_environment" in script


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
    for script_name in (
        "run_acceptance.sh",
        "run_bench_matrix.sh",
        "run_oracle_export.sh",
        "gpu_stats.sh",
        "runtime_stats.sh",
        "run_context.sh",
    ):
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
        "RUNTIME_STATS": "0",
        "GPU_TOPOLOGY_SLUG": "test_gpu",
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
