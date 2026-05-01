import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_acceptance_script_runs_coding_smoke_gate():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert 'CODING_TAG="${CODING_TAG:-coding}"' in script
    assert '--tag "${CODING_TAG}"' in script
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
        assert 'RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"' in script
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
    assert "OFFICIAL_RUN_TOOLCALL15=1" in sample
    assert "OFFICIAL_TOOLCALL15_SCENARIO_SET=both" in sample
    assert "OFFICIAL_TOOLCALL15_REPEAT_COUNT=3" in sample
    assert "REAL_SCENARIO_REPEAT_COUNT=3" in sample
    assert "QUALITY_TAG=quality" in sample
    assert "QUALITY_REPEAT_COUNT=3" in sample
    assert "CODING_TAG=coding" in sample
    assert "CODING_REPEAT_COUNT=3" in sample
    assert "TOOLCALL15_SCENARIO_SET=both" in sample
    assert "TOOLCALL15_REPEAT_COUNT=3" in sample
    assert "SERVER_GUARD=1" in sample
    assert "SERVER_STARTUP_TIMEOUT=1800" in sample
    assert "SERVER_STARTUP_INTERVAL_SECONDS=15" in sample
    assert "SERVER_HEALTH_TIMEOUT=10" in sample
    assert "SERVER_FAILURE_PROBE_TIMEOUT=30" in sample
    assert "SERVER_FAILURE_GRACE_TIMEOUT=300" in sample
    assert "SERVER_RECOVERY_CMD=" in sample
    assert "GPU_TOPOLOGY_SLUG=" in sample
    assert ".env" in gitignore


def test_acceptance_script_writes_human_markdown_smoke_reports():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert '--markdown-output "${OUT_DIR}/smoke_quick.md"' in script
    assert '--markdown-output "${OUT_DIR}/smoke_quality.md"' in script
    assert '--markdown-output "${OUT_DIR}/smoke_coding.md"' in script


def test_acceptance_script_repeats_real_scenario_gates_three_times():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert 'REAL_SCENARIO_REPEAT_COUNT="${REAL_SCENARIO_REPEAT_COUNT:-3}"' in script
    assert 'QUALITY_TAG="${QUALITY_TAG:-quality}"' in script
    assert 'QUALITY_REPEAT_COUNT="${QUALITY_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT}}"' in script
    assert 'CODING_TAG="${CODING_TAG:-coding}"' in script
    assert 'CODING_REPEAT_COUNT="${CODING_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT}}"' in script
    assert 'TOOLCALL15_SCENARIO_SET="${TOOLCALL15_SCENARIO_SET:-both}"' in script
    assert 'TOOLCALL15_REPEAT_COUNT="${TOOLCALL15_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT}}"' in script
    assert '--tag "${QUALITY_TAG}"' in script
    assert '--tag "${CODING_TAG}"' in script
    assert '--scenario-set "${TOOLCALL15_SCENARIO_SET}"' in script
    assert '--repeat-count "${QUALITY_REPEAT_COUNT}"' in script
    assert '--repeat-count "${CODING_REPEAT_COUNT}"' in script
    assert '--repeat-count "${TOOLCALL15_REPEAT_COUNT}"' in script


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

    for script_name in ("run_acceptance.sh", "run_bench_matrix.sh", "run_oracle_export.sh"):
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
    assert '"${OUT_DIR}/serve_log_phase.log"' in helper
    assert '"${OUT_DIR}/serve_log_offset.txt"' in helper

    for script_name in ("run_acceptance.sh", "run_bench_matrix.sh", "run_oracle_export.sh"):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

        assert 'source "${SCRIPT_DIR}/runtime_stats.sh"' in script
        assert "start_runtime_stats" in script
        assert "stop_runtime_stats" in script


def test_scripts_collect_vllm_official_env_to_artifacts():
    sample = (ROOT / "env.sample").read_text(encoding="utf-8")
    helper = (ROOT / "scripts" / "vllm_collect_env.sh").read_text(encoding="utf-8")

    assert "VLLM_COLLECT_ENV=1" in sample
    assert "raw.githubusercontent.com/vllm-project/vllm/main/vllm/collect_env.py" in sample
    assert "vllm_collect_env.py" in helper
    assert "vllm_collect_env.txt" in helper
    assert "vllm_collect_env.sha256" in helper
    assert "vllm_collect_env.exit_code" in helper

    for script_name in (
        "run_acceptance.sh",
        "run_bench_matrix.sh",
        "run_oracle_export.sh",
    ):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

        assert 'source "${SCRIPT_DIR}/vllm_collect_env.sh"' in script
        assert "collect_vllm_env" in script


def test_b200_baseline_script_uses_official_serve_shape():
    script = (ROOT / "scripts" / "run_b200_baseline.sh").read_text(encoding="utf-8")

    assert 'VLLM_ENGINE_READY_TIMEOUT_S="${VLLM_ENGINE_READY_TIMEOUT_S:-3600}"' in script
    assert "deepseek-ai/DeepSeek-V4-Flash" in script
    assert "--trust-remote-code" in script
    assert "--kv-cache-dtype" in script
    assert "fp8" in script
    assert "--block-size" in script
    assert "256" in script
    assert "--tensor-parallel-size" in script
    assert "4" in script
    assert "--no-enable-flashinfer-autotune" in script
    assert "--attention_config.use_fp4_indexer_cache=True" in script
    assert "--reasoning-parser" in script
    assert "deepseek_v4" in script
    assert "--tokenizer-mode" in script
    assert "--tool-call-parser" in script
    assert "--enable-auto-tool-choice" in script
    assert "--speculative_config" in script
    assert '"method":"mtp","num_speculative_tokens":2' in script


def test_b200_baseline_script_clears_inherited_vllm_launch_defaults():
    script = (ROOT / "scripts" / "run_b200_baseline.sh").read_text(encoding="utf-8")

    assert "clear_inherited_launch_env" in script
    for name in (
        "VLLM_ARGS",
        "VLLM_MODEL",
        "VLLM_TEST_ENDPOINT",
        "VLLM_USAGE_SOURCE",
        "TORCH_CUDA_ARCH_LIST",
        "CUDA_VISIBLE_DEVICES",
    ):
        assert f"unset {name}" in script


def test_b200_baseline_script_reuses_wrappers_and_keeps_variant_artifacts():
    script = (ROOT / "scripts" / "run_b200_baseline.sh").read_text(encoding="utf-8")

    assert 'B200_BASELINE_VARIANTS="${B200_BASELINE_VARIANTS:-nomtp,mtp}"' in script
    assert 'NO_MTP_CONCURRENCY="${NO_MTP_CONCURRENCY:-1,2,4,8,16,24}"' in script
    assert 'MTP_CONCURRENCY="${MTP_CONCURRENCY:-1,2,4,8,16,24}"' in script
    assert 'RUN_ACCEPTANCE="${RUN_ACCEPTANCE:-1}"' in script
    assert 'RUN_BENCH_HF="${RUN_BENCH_HF:-1}"' in script
    assert 'RUN_ROOT="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${B200_BASELINE_LABEL}/${RUN_TIMESTAMP}}"' in script
    assert '"${variant_dir}/acceptance"' in script
    assert '"${variant_dir}/bench_hf_mt_bench"' in script
    assert '"${variant_dir}/bench_random_8192x512"' in script
    assert '"${variant_dir}/oracle_export"' in script
    assert "run_acceptance.sh" in script
    assert "run_bench_matrix.sh" in script
    assert "run_oracle_export.sh" in script
    assert 'SERVE_LOG="${serve_log}"' in script
    assert "baseline_summary.md" in script
    assert "phase_exit_codes.tsv" in script


def test_vllm_collect_env_helper_downloads_and_runs_official_script(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_curl = fake_bin / "curl"
    fake_curl.write_text(
        "#!/usr/bin/env sh\n"
        "out=''\n"
        "while [ \"$#\" -gt 0 ]; do\n"
        "  if [ \"$1\" = '-o' ]; then shift; out=\"$1\"; fi\n"
        "  shift\n"
        "done\n"
        "cat > \"$out\" <<'PY'\n"
        "print('vLLM official collect env output')\n"
        "PY\n",
        encoding="utf-8",
    )
    fake_curl.chmod(fake_curl.stat().st_mode | 0o111)
    out_dir = tmp_path / "out"
    script = f"""
set -euo pipefail
OUT_DIR="{out_dir}"
PYTHON=python
VLLM_COLLECT_ENV=1
VLLM_COLLECT_ENV_URL=https://example.invalid/collect_env.py
PATH="{fake_bin}:$PATH"
source "{ROOT / "scripts" / "vllm_collect_env.sh"}"
mkdir -p "${{OUT_DIR}}"
collect_vllm_env
"""

    subprocess.run(
        ["bash", "-c", script],
        check=True,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert (out_dir / "vllm_collect_env.py").exists()
    assert "official collect env output" in (
        out_dir / "vllm_collect_env.txt"
    ).read_text(encoding="utf-8")
    assert (out_dir / "vllm_collect_env.sha256").exists()
    assert (out_dir / "vllm_collect_env.exit_code").read_text(
        encoding="utf-8"
    ).strip() == "0"


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


def test_baseline_bundle_script_generates_report_and_public_data():
    script = (ROOT / "scripts" / "generate_baseline_bundle.sh").read_text(
        encoding="utf-8"
    )

    assert 'BASELINE_RUN_DIR="${BASELINE_RUN_DIR:?set BASELINE_RUN_DIR}"' in script
    assert 'BASELINE_OUTPUT_DIR="${BASELINE_OUTPUT_DIR:-${REPO_ROOT}/baselines/${BASELINE_DATE}_${BASELINE_BUNDLE_LABEL}}"' in script
    assert "reference-bundle" in script
    assert "baseline-report" in script
    assert '--run-dir "${BASELINE_RUN_DIR}"' in script
    assert '--output-dir "${tmp_dir}"' in script
    assert '--output "${tmp_dir}/report.md"' in script
    assert "--fail-on-sensitive" in script
    assert "scan_public_bundle" in script
    assert "load_oracle_cases" in script
    assert 'mv "${tmp_dir}" "${BASELINE_OUTPUT_DIR}"' in script


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
    assert "--failure-probe-timeout" in bench
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
        "run_b200_baseline.sh",
        "generate_baseline_bundle.sh",
        "gpu_stats.sh",
        "runtime_stats.sh",
        "run_context.sh",
        "vllm_collect_env.sh",
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
        "VLLM_COLLECT_ENV": "0",
        "GPU_TOPOLOGY_SLUG": "test_gpu",
        "VLLM_BIN": "fake-vllm",
        "CONCURRENCY": "1",
        "NUM_PROMPTS": "1",
        "SERVE_LOG": "",
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


def test_bench_wrapper_records_exit_code_on_bench_failure(tmp_path):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "#!/usr/bin/env sh\n"
        "case \"$*\" in\n"
        "  *' env-summary '*) exit 0 ;;\n"
        "  *' health'*) printf '%s\\n' '{\"ok\":true}'; exit 0 ;;\n"
        "  *' bench-matrix '*) printf '%s\\n' '[]' > \"$OUT_DIR/bench.json\"; exit 1 ;;\n"
        "esac\n"
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
        "VLLM_COLLECT_ENV": "0",
        "GPU_TOPOLOGY_SLUG": "test_gpu",
        "VLLM_BIN": "fake-vllm",
        "CONCURRENCY": "1",
        "NUM_PROMPTS": "1",
        "SERVER_STARTUP_INTERVAL_SECONDS": "0",
        "SERVE_LOG": "",
    }

    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_bench_matrix.sh")],
        check=False,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert result.returncode == 1
    assert (out_dir / "bench.exit_code").read_text(encoding="utf-8").strip() == "1"
    assert f"wrote {out_dir}" in result.stdout


def test_b200_baseline_driver_can_run_with_mocked_tools(tmp_path):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "#!/usr/bin/env sh\n"
        "args=\"$*\"\n"
        "write_arg_file() {\n"
        "  flag=\"$1\"\n"
        "  shift\n"
        "  while [ \"$#\" -gt 0 ]; do\n"
        "    if [ \"$1\" = \"$flag\" ]; then\n"
        "      shift\n"
        "      mkdir -p \"$(dirname \"$1\")\"\n"
        "      printf '%s\\n' '{}' > \"$1\"\n"
        "      return 0\n"
        "    fi\n"
        "    shift\n"
        "  done\n"
        "}\n"
        "case \"$args\" in\n"
        "  *' env-summary '*) write_arg_file --json-output \"$@\"; write_arg_file --markdown-output \"$@\"; exit 0 ;;\n"
        "  *' health'*) printf '%s\\n' '{\"ok\":true}'; exit 0 ;;\n"
        "  *' chat-smoke '*) write_arg_file --jsonl-output \"$@\"; write_arg_file --markdown-output \"$@\"; exit 0 ;;\n"
        "  *' toolcall15 '*) write_arg_file --json-output \"$@\"; exit 0 ;;\n"
        "  *' bench-matrix '*) write_arg_file --json-output \"$@\"; exit 0 ;;\n"
        "  *' oracle-export '*) exit 0 ;;\n"
        "  *' pytest'*) exit 0 ;;\n"
        "  *' ruff check'*) exit 0 ;;\n"
        "  *' compileall '*) exit 0 ;;\n"
        "esac\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_python.chmod(fake_python.stat().st_mode | 0o111)
    fake_vllm = tmp_path / "fake-vllm"
    fake_vllm.write_text(
        "#!/usr/bin/env sh\n"
        "trap 'exit 0' TERM INT\n"
        "while :; do sleep 1; done\n",
        encoding="utf-8",
    )
    fake_vllm.chmod(fake_vllm.stat().st_mode | 0o111)
    out_dir = tmp_path / "baseline"
    env = os.environ | {
        "PYTHON": str(fake_python),
        "VLLM_BIN": str(fake_vllm),
        "OUT_DIR": str(out_dir),
        "GPU_STATS": "0",
        "RUNTIME_STATS": "0",
        "VLLM_COLLECT_ENV": "0",
        "B200_BASELINE_VARIANTS": "nomtp,mtp",
        "NO_MTP_CONCURRENCY": "1",
        "MTP_CONCURRENCY": "2",
        "NUM_PROMPTS": "1",
        "RUN_RANDOM_LONG": "1",
        "RANDOM_LONG_CONCURRENCY": "1",
        "RANDOM_LONG_NUM_PROMPTS": "1",
        "RUN_ORACLE_EXPORT": "1",
        "SERVER_STARTUP_TIMEOUT": "5",
        "SERVER_STARTUP_INTERVAL_SECONDS": "0",
    }

    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_b200_baseline.sh")],
        check=True,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )

    phase_log = (out_dir / "phase_exit_codes.tsv").read_text(encoding="utf-8")
    assert "nomtp\tacceptance\t0" in phase_log
    assert "nomtp\tbench_hf_mt_bench\t0" in phase_log
    assert "nomtp\toracle_export\t0" in phase_log
    assert "mtp\tacceptance\t0" in phase_log
    assert "mtp\tbench_hf_mt_bench\t0" in phase_log
    assert "mtp\toracle_export\t0" in phase_log
    assert (out_dir / "baseline_summary.md").exists()
    assert "--speculative_config" in (out_dir / "mtp" / "serve_command.sh").read_text(
        encoding="utf-8"
    )
    assert "wrote" in result.stdout


def test_generate_baseline_report_wrapper_uses_report_cli():
    script = (ROOT / "scripts" / "generate_baseline_report.sh").read_text(
        encoding="utf-8"
    )

    assert "load_harness_env" in script
    assert "baseline-report" in script
    assert "BASELINE_RUN_DIR" in script
    assert "BASELINE_SUPPLEMENT_DIR" in script
    assert "BASELINE_REPORT_OUTPUT" in script
    assert "BASELINE_REPORT_DATE" in script
    assert 'baselines/${BASELINE_REPORT_DATE}_${output_label}/report.md' in script


def test_official_subjective_baseline_script_uses_api_key_and_baseline_output():
    script = (ROOT / "scripts" / "run_official_subjective_baseline.sh").read_text(
        encoding="utf-8"
    )

    assert "load_harness_env" in script
    assert "--api-key-env DEEPSEEK_API_KEY" in script
    assert 'OFFICIAL_QUALITY_TAG="${OFFICIAL_QUALITY_TAG:-quality}"' in script
    assert 'OFFICIAL_CODING_TAG="${OFFICIAL_CODING_TAG:-coding}"' in script
    assert 'OFFICIAL_RUN_TOOLCALL15="${OFFICIAL_RUN_TOOLCALL15:-1}"' in script
    assert 'OFFICIAL_TOOLCALL15_SCENARIO_SET="${OFFICIAL_TOOLCALL15_SCENARIO_SET:-both}"' in script
    assert 'OFFICIAL_TOOLCALL15_REPEAT_COUNT="${OFFICIAL_TOOLCALL15_REPEAT_COUNT:-${OFFICIAL_REPEAT_COUNT}}"' in script
    assert "--repeat-count" in script
    assert "--max-case-tokens" in script
    assert "--extra-body-json" in script
    assert "--official-toolcall-input" in script
    assert "DEEPSEEK_THINKING_TYPE" in script
    assert "subjective-comparison" in script
    assert "baselines/20260501_b200_main_51295793a" in script
    assert "subjective_quality" in script


def test_runtime_stats_helper_slices_serve_log_per_phase(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_curl = fake_bin / "curl"
    fake_curl.write_text(
        "#!/usr/bin/env sh\n"
        "printf '%s\\n' 'vllm:prompt_tokens_total 10'\n"
        "printf '%s\\n' 'vllm:generation_tokens_total 3'\n",
        encoding="utf-8",
    )
    fake_curl.chmod(fake_curl.stat().st_mode | 0o111)
    serve_log = tmp_path / "serve.log"
    serve_log.write_text(
        "INFO Engine 000: Avg prompt throughput: 10.0 tokens/s, "
        "Avg generation throughput: 20.0 tokens/s, Running: 9 reqs, "
        "Waiting: 0 reqs, GPU KV cache usage: 9.0%, Prefix cache hit rate: 0.0%\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"
    script = f"""
set -euo pipefail
cd "{ROOT}"
OUT_DIR="{out_dir}"
BASE_URL=http://127.0.0.1:9
PYTHON=python
SERVE_LOG="{serve_log}"
RUNTIME_STATS=1
RUNTIME_STATS_INTERVAL_SECONDS=1
PATH="{fake_bin}:$PATH"
source "{ROOT / "scripts" / "runtime_stats.sh"}"
mkdir -p "${{OUT_DIR}}"
start_runtime_stats
printf '%s\\n' 'INFO Engine 000: Avg prompt throughput: 100.0 tokens/s, Avg generation throughput: 200.0 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 1.0%, Prefix cache hit rate: 0.0%' >> "${{SERVE_LOG}}"
sleep 0.2
stop_runtime_stats
"""

    subprocess.run(
        ["bash", "-c", script],
        check=True,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    sliced = (out_dir / "serve_log_phase.log").read_text(encoding="utf-8")
    assert "100.0 tokens/s" in sliced
    assert "10.0 tokens/s" not in sliced
    data = json.loads((out_dir / "runtime_stats_summary.json").read_text(encoding="utf-8"))
    assert data["serve_log"]["prefill_throughput_tok_s_avg"] == 100.0
    assert (out_dir / "serve_log_offset.txt").exists()
