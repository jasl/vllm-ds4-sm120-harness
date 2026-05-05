import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_acceptance_script_runs_generation_gate():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert 'GENERATION_PROMPT_ROOT="${GENERATION_PROMPT_ROOT:-${REPO_ROOT}/prompts}"' in script
    assert "generation-matrix" in script
    assert '--jsonl-output "${OUT_DIR}/generation.jsonl"' in script
    assert '--markdown-output-dir "${OUT_DIR}/generation"' in script
    assert 'GENERATION_THINK_HIGH_TOKEN_BUDGET="${GENERATION_THINK_HIGH_TOKEN_BUDGET-4096}"' in script
    assert '--think-high-token-budget "${GENERATION_THINK_HIGH_TOKEN_BUDGET}"' in script
    assert 'GENERATION_THINK_MAX_TOKEN_BUDGET="${GENERATION_THINK_MAX_TOKEN_BUDGET-}"' in script
    assert '--think-max-token-budget "${GENERATION_THINK_MAX_TOKEN_BUDGET}"' in script
    assert 'GENERATION_THINK_MAX_REQUEST_MAX_TOKENS="${GENERATION_THINK_MAX_REQUEST_MAX_TOKENS:-65536}"' in script
    assert '--think-max-request-max-tokens "${GENERATION_THINK_MAX_REQUEST_MAX_TOKENS}"' in script


def test_acceptance_script_runs_static_harness_gates():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert 'run_static_gate pytest "${PYTHON}" -m pytest -q tests' in script
    assert 'run_static_gate ruff "${PYTHON}" -m ruff check ds4_harness tests' in script
    assert 'run_static_gate compileall "${PYTHON}" -m compileall -q ds4_harness' in script


def test_acceptance_static_gates_do_not_inherit_live_artifact_context():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert 'STATIC_GATE_ARTIFACT_ROOT="${OUT_DIR}/_static_gate_artifacts"' in script
    assert 'local static_gate_path="${PATH}"' in script
    assert 'static_gate_path="$(cd -- "$(dirname -- "${PYTHON}")" && pwd):${static_gate_path}"' in script
    assert 'static_env_args+=("-i")' in script
    assert 'static_env_args+=("PATH=${static_gate_path}")' in script
    assert 'static_env_args+=("HOME=${HOME:-}")' in script
    assert 'static_env_args+=("TMPDIR=${TMPDIR:-/tmp}")' in script
    assert 'static_env_args+=("ARTIFACT_ROOT=${STATIC_GATE_ARTIFACT_ROOT}")' in script
    assert 'rm -rf "${STATIC_GATE_ARTIFACT_ROOT}"' in script


def test_scripts_allow_explicit_python_interpreter():
    for script_name in (
        "run_acceptance.sh",
        "run_bench_matrix.sh",
        "run_lm_eval.sh",
        "run_kv_layout_probe.sh",
        "run_prefix_cache_probe.sh",
        "run_streaming_pressure_soak.sh",
    ):
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


def test_prefix_cache_probe_wrapper_records_kv_runtime_artifacts():
    script = (ROOT / "scripts" / "run_prefix_cache_probe.sh").read_text(
        encoding="utf-8"
    )

    assert "prefix-cache-probe" in script
    assert '--json-output "${OUT_DIR}/prefix_cache_probe.json"' in script
    assert '--markdown-output "${OUT_DIR}/prefix_cache_probe.md"' in script
    assert 'source "${SCRIPT_DIR}/gpu_stats.sh"' in script
    assert "start_gpu_stats" in script
    assert 'source "${SCRIPT_DIR}/runtime_stats.sh"' in script
    assert "start_runtime_stats" in script
    assert 'SERVE_LOG="${SERVE_LOG:-}"' in script


def test_streaming_pressure_soak_wrapper_records_kv_runtime_artifacts():
    script = (ROOT / "scripts" / "run_streaming_pressure_soak.sh").read_text(
        encoding="utf-8"
    )

    assert "streaming-pressure-soak" in script
    assert '--json-output "${OUT_DIR}/streaming_pressure_soak.json"' in script
    assert '--markdown-output "${OUT_DIR}/streaming_pressure_soak.md"' in script
    assert 'source "${SCRIPT_DIR}/gpu_stats.sh"' in script
    assert "start_gpu_stats" in script
    assert 'source "${SCRIPT_DIR}/runtime_stats.sh"' in script
    assert "start_runtime_stats" in script
    assert 'SERVE_LOG="${SERVE_LOG:-}"' in script


def test_acceptance_streaming_pressure_soak_is_opt_in():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")
    sample = (ROOT / "env.sample").read_text(encoding="utf-8")

    assert "RUN_STREAMING_PRESSURE_SOAK=0" in sample
    assert 'RUN_STREAMING_PRESSURE_SOAK="${RUN_STREAMING_PRESSURE_SOAK:-0}"' in script
    assert 'if [[ "${RUN_STREAMING_PRESSURE_SOAK}" == "1"' in script
    assert "streaming-pressure-soak" in script
    assert '"${OUT_DIR}/streaming_pressure_soak.json"' in script


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


def _env_sample_values():
    values = {}
    for line in (ROOT / "env.sample").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


def test_env_sample_and_local_env_are_configured():
    values = _env_sample_values()
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    required_keys = {
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_BASE_URL",
        "DEEPSEEK_BETA_BASE_URL",
        "DEEPSEEK_MODEL",
        "DEEPSEEK_FLASH_MODEL",
        "DEEPSEEK_PRO_MODEL",
        "DEEPSEEK_PRESERVE_REASONING_CONTENT",
        "OFFICIAL_BASELINE_DATE",
        "OFFICIAL_BASELINE_LABEL",
        "OFFICIAL_BASELINE_DIR",
        "OFFICIAL_GENERATION_PROMPTS",
        "OFFICIAL_THINKING_MODES",
        "OFFICIAL_SMOKE_CASES",
        "OFFICIAL_TOOLCALL15_THINKING_MODES",
        "OFFICIAL_TOOLCALL15_TEMPERATURE",
        "OFFICIAL_TOOLCALL15_TOP_P",
        "BASELINE_LABEL",
        "ORACLE_LOGPROBS",
        "ORACLE_TIMEOUT",
        "ORACLE_REQUEST_RETRIES",
        "ARTIFACT_ARCHIVE_PREVIOUS",
        "ARTIFACT_ARCHIVE_PREFIX",
        "B200_BASELINE_LABEL",
        "B200_BASELINE_PHASES",
        "B200_PARALLEL_GPU_GROUPS",
        "SERVE_MAX_MODEL_LEN",
        "SERVE_USE_FP4_INDEXER_CACHE",
        "RUN_STREAMING_PRESSURE_SOAK",
        "STREAMING_PRESSURE_CONCURRENCY",
        "STREAMING_PRESSURE_ROUND_COUNT",
        "STREAMING_PRESSURE_LINE_COUNT",
        "STREAMING_PRESSURE_THINKING_MODE",
        "GENERATION_PROMPT_ROOT",
        "GENERATION_LANGUAGES",
        "GENERATION_THINKING_MODES",
        "GENERATION_TEMPERATURE",
        "GENERATION_TOP_P",
        "TOOLCALL15_SCENARIO_SET",
        "TOOLCALL15_THINKING_MODES",
        "TOOLCALL15_TEMPERATURE",
        "TOOLCALL15_TOP_P",
        "RUN_LM_EVAL",
        "LM_EVAL_BIN",
        "LM_EVAL_TASKS",
        "SERVER_GUARD",
        "SERVER_STARTUP_TIMEOUT",
        "SERVER_HEALTH_TIMEOUT",
        "SERVER_FAILURE_GRACE_TIMEOUT",
        "SERVER_RECOVERY_CMD",
        "GPU_TOPOLOGY_SLUG",
    }
    assert required_keys <= set(values)
    assert {
        "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
        "DEEPSEEK_BETA_BASE_URL": "https://api.deepseek.com/beta",
        "DEEPSEEK_MODEL": "deepseek-v4-flash",
        "DEEPSEEK_FLASH_MODEL": "deepseek-v4-flash",
        "DEEPSEEK_PRO_MODEL": "deepseek-v4-pro",
        "OFFICIAL_TEMPERATURE": "1.0",
        "OFFICIAL_TOP_P": "1.0",
        "OFFICIAL_TOOLCALL15_TEMPERATURE": "1.0",
        "OFFICIAL_TOOLCALL15_TOP_P": "1.0",
        "GENERATION_TEMPERATURE": "1.0",
        "GENERATION_TOP_P": "1.0",
        "TOOLCALL15_TEMPERATURE": "1.0",
        "TOOLCALL15_TOP_P": "1.0",
        "SERVE_MAX_MODEL_LEN": "393216",
        "SERVE_USE_FP4_INDEXER_CACHE": "auto",
        "RUN_STREAMING_PRESSURE_SOAK": "0",
        "STREAMING_PRESSURE_TEMPERATURE": "1.0",
        "STREAMING_PRESSURE_TOP_P": "1.0",
    }.items() <= values.items()
    assert "B200_ARCHIVE_PREVIOUS" not in values
    assert "B200_ARCHIVE_PREFIX" not in values
    assert ".env" in gitignore


def test_gb10_sm121_profile_uses_public_machine_independent_settings():
    profile = (
        ROOT / "configs" / "gb10_sm121_serve.env.example"
    ).read_text(encoding="utf-8")

    assert 'CUDA_HOME="/usr/local/cuda-13.2"' in profile
    assert 'TRITON_PTXAS_PATH="/usr/local/cuda-13.2/bin/ptxas"' in profile
    assert 'CUDA_ARCH_LIST="121a"' in profile
    assert 'TORCH_CUDA_ARCH_LIST="12.1a"' in profile
    assert 'GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-1x_nvidia_gb10}"' in profile
    assert 'SERVE_USE_FP4_INDEXER_CACHE="${SERVE_USE_FP4_INDEXER_CACHE:-0}"' in profile
    assert "PYTORCH_CUDA_ALLOC_CONF" in profile
    assert "10.0.0." not in profile
    assert "/home/" not in profile
    assert "/Users/" not in profile


def test_acceptance_script_writes_human_markdown_smoke_reports():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert '--markdown-output "${OUT_DIR}/smoke_quick.md"' in script
    assert '--markdown-output-dir "${OUT_DIR}/generation"' in script


def test_acceptance_script_repeats_real_scenario_gates_three_times():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert 'REAL_SCENARIO_REPEAT_COUNT="${REAL_SCENARIO_REPEAT_COUNT:-3}"' in script
    assert 'GENERATION_REPEAT_COUNT="${GENERATION_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT}}"' in script
    assert 'GENERATION_THINKING_MODES="${GENERATION_THINKING_MODES:-non-thinking,think-high,think-max}"' in script
    assert 'TOOLCALL15_THINKING_MODES="${TOOLCALL15_THINKING_MODES:-${GENERATION_THINKING_MODES}}"' in script
    assert 'API_REQUEST_RETRIES="${API_REQUEST_RETRIES:-1}"' in script
    assert 'TOOLCALL15_SCENARIO_SET="${TOOLCALL15_SCENARIO_SET:-en}"' in script
    assert 'TOOLCALL15_REPEAT_COUNT="${TOOLCALL15_REPEAT_COUNT:-${REAL_SCENARIO_REPEAT_COUNT}}"' in script
    assert 'TOOLCALL15_TEMPERATURE="${TOOLCALL15_TEMPERATURE:-1.0}"' in script
    assert 'TOOLCALL15_TOP_P="${TOOLCALL15_TOP_P:-1.0}"' in script
    assert '--prompt-root "${GENERATION_PROMPT_ROOT}"' in script
    assert '--temperature "${GENERATION_TEMPERATURE}"' in script
    assert '--top-p "${GENERATION_TOP_P}"' in script
    assert '--scenario-set "${TOOLCALL15_SCENARIO_SET}"' in script
    assert '--temperature "${TOOLCALL15_TEMPERATURE}"' in script
    assert '--top-p "${TOOLCALL15_TOP_P}"' in script
    assert '--request-retries "${API_REQUEST_RETRIES}"' in script
    assert '--thinking-mode "${thinking_mode}"' in script
    assert '--repeat-count "${GENERATION_REPEAT_COUNT}"' in script
    assert '--repeat-count "${TOOLCALL15_REPEAT_COUNT}"' in script


def test_acceptance_script_runs_all_gates_and_records_exit_codes():
    script = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")

    assert "failures=0" in script
    assert "run_static_gate pytest" in script
    assert "run_live_gate smoke_quick" in script
    assert "run_live_gate generation" in script
    assert "live_env_args()" in script
    assert 'run_gate "${name}" env "${env_args[@]}" "$@"' in script
    assert 'run_gate_capture "${name}" "${output}" env "${env_args[@]}" "$@"' in script
    assert "run_live_gate toolcall15" in script
    assert "run_live_gate oracle_compare" in script
    assert 'ORACLE_TOP_N="${ORACLE_TOP_N:-20}"' in script
    assert 'ORACLE_LOW_MARGIN_THRESHOLD="${ORACLE_LOW_MARGIN_THRESHOLD:-0.5}"' in script
    assert 'MIN_TOP1_MATCH_RATE="${MIN_TOP1_MATCH_RATE:-0.80}"' in script
    assert 'MIN_TOPK_OVERLAP_MEAN="${MIN_TOPK_OVERLAP_MEAN:-0.80}"' in script
    assert '--top-n "${ORACLE_TOP_N}"' in script
    assert '--low-margin-threshold "${ORACLE_LOW_MARGIN_THRESHOLD}"' in script
    assert "--require-high-margin-token-match" in script
    assert '--min-top1-match-rate "${MIN_TOP1_MATCH_RATE}"' in script
    assert '--min-topk-overlap-mean "${MIN_TOPK_OVERLAP_MEAN}"' in script
    assert '--stability-json-output "${OUT_DIR}/oracle_stability.json"' in script
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

    for script_name in (
        "run_acceptance.sh",
        "run_bench_matrix.sh",
        "run_oracle_export.sh",
        "run_lm_eval.sh",
        "run_prefix_cache_probe.sh",
        "run_streaming_pressure_soak.sh",
    ):
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

    for script_name in (
        "run_acceptance.sh",
        "run_bench_matrix.sh",
        "run_oracle_export.sh",
        "run_lm_eval.sh",
        "run_prefix_cache_probe.sh",
        "run_streaming_pressure_soak.sh",
    ):
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
        "run_lm_eval.sh",
        "run_kv_layout_probe.sh",
        "run_prefix_cache_probe.sh",
        "run_streaming_pressure_soak.sh",
    ):
        script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

        assert 'source "${SCRIPT_DIR}/vllm_collect_env.sh"' in script
        assert "collect_vllm_env" in script


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
    assert 'B200_BASELINE_PHASES="${B200_BASELINE_PHASES:-all}"' in script
    assert 'B200_VARIANT_PARALLEL="${B200_VARIANT_PARALLEL:-0}"' in script
    assert 'B200_PARALLEL_GPU_GROUPS="${B200_PARALLEL_GPU_GROUPS:-nomtp=0,1;mtp=2,3}"' in script
    assert "run_parallel_variants" in script
    assert "B200_CUDA_VISIBLE_DEVICES" in script
    assert 'NO_MTP_CONCURRENCY="${NO_MTP_CONCURRENCY:-1,2,4,8,16,24}"' in script
    assert 'MTP_CONCURRENCY="${MTP_CONCURRENCY:-1,2,4,8,16,24}"' in script
    assert 'RUN_ACCEPTANCE="${RUN_ACCEPTANCE:-1}"' in script
    assert 'RUN_KV_LAYOUT_PROBE="${RUN_KV_LAYOUT_PROBE:-1}"' in script
    assert 'RUN_LONG_CONTEXT_PROBE="${RUN_LONG_CONTEXT_PROBE:-1}"' in script
    assert 'RUN_PREFIX_CACHE_PROBE="${RUN_PREFIX_CACHE_PROBE:-1}"' in script
    assert 'RUN_STREAMING_PRESSURE_SOAK="${RUN_STREAMING_PRESSURE_SOAK:-0}"' in script
    assert 'RUN_BENCH_HF="${RUN_BENCH_HF:-1}"' in script
    assert 'TOOLCALL15_TEMPERATURE="${TOOLCALL15_TEMPERATURE:-1.0}"' in script
    assert 'TOOLCALL15_TOP_P="${TOOLCALL15_TOP_P:-1.0}"' in script
    assert 'ARTIFACT_ARCHIVE_PREVIOUS="${ARTIFACT_ARCHIVE_PREVIOUS:-1}"' in script
    assert 'ARTIFACT_ARCHIVE_PREFIX="${ARTIFACT_ARCHIVE_PREFIX:-${B200_BASELINE_LABEL}}"' in script
    assert "archive_previous_runs" in script
    assert "_archive_before_${RUN_TIMESTAMP}" in script
    assert 'ARTIFACT_PARENT="${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}"' in script
    assert 'RUN_ROOT="${OUT_DIR:-${ARTIFACT_PARENT}/${B200_BASELINE_LABEL}/${RUN_TIMESTAMP}}"' in script
    assert "phase_enabled" in script
    assert '"${variant_dir}/acceptance"' in script
    assert '"${variant_dir}/kv_layout_probe"' in script
    assert '"${variant_dir}/long_context_probe"' in script
    assert '"${variant_dir}/prefix_cache_probe"' in script
    assert '"${variant_dir}/streaming_pressure_soak"' in script
    assert '"${variant_dir}/bench_hf_mt_bench"' in script
    assert '"${variant_dir}/bench_random_8192x512"' in script
    assert '"${variant_dir}/eval_gsm8k"' in script
    assert '"${variant_dir}/oracle_export"' in script
    assert 'toolcall15_temperature: `%s`' in script
    assert 'toolcall15_top_p: `%s`' in script
    assert "run_acceptance.sh" in script
    assert "run_kv_layout_probe.sh" in script
    assert "run_long_context_probe.sh" in script
    assert "run_prefix_cache_probe.sh" in script
    assert "run_streaming_pressure_soak.sh" in script
    assert "run_bench_matrix.sh" in script
    assert "run_lm_eval.sh" in script
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
    assert 'ORACLE_REQUEST_RETRIES="${ORACLE_REQUEST_RETRIES:-${API_REQUEST_RETRIES:-1}}"' in script
    assert '--request-retries "${ORACLE_REQUEST_RETRIES}"' in script
    assert 'BASELINE_LABEL="${BASELINE_LABEL:-b200_oracle}"' in script
    assert '--output-dir "${OUT_DIR}"' in script
    assert "--stop-on-error" in script


def test_kv_layout_probe_script_exports_structured_and_raw_artifacts(tmp_path):
    script = (ROOT / "scripts" / "run_kv_layout_probe.sh").read_text(
        encoding="utf-8"
    )
    assert "kv-layout-probe" in script
    assert '--target-python "${PYTHON}"' in script
    assert '--raw-output "${OUT_DIR}/kv_layout_probe_packed_cache.bin"' in script
    assert "server_ready" not in script

    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "#!/usr/bin/env sh\n"
        "write_arg_file() {\n"
        "  flag=\"$1\"\n"
        "  content=\"$2\"\n"
        "  shift 2\n"
        "  while [ \"$#\" -gt 0 ]; do\n"
        "    if [ \"$1\" = \"$flag\" ]; then\n"
        "      shift\n"
        "      mkdir -p \"$(dirname \"$1\")\"\n"
        "      printf '%s\\n' \"$content\" > \"$1\"\n"
        "      return 0\n"
        "    fi\n"
        "    shift\n"
        "  done\n"
        "}\n"
        "case \"$*\" in\n"
        "  *' env-summary '*) exit 0 ;;\n"
        "  *' kv-layout-probe '*)\n"
        "    write_arg_file --json-output '{\"ok\": true}' \"$@\"\n"
        "    write_arg_file --markdown-output '# KV Layout Probe' \"$@\"\n"
        "    while [ \"$#\" -gt 0 ]; do\n"
        "      if [ \"$1\" = '--raw-output' ]; then shift; mkdir -p \"$(dirname \"$1\")\"; printf '\\000\\001' > \"$1\"; fi\n"
        "      shift\n"
        "    done\n"
        "    exit 0 ;;\n"
        "esac\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_python.chmod(fake_python.stat().st_mode | 0o111)
    out_dir = tmp_path / "kv-layout"
    env = os.environ | {
        "PYTHON": str(fake_python),
        "OUT_DIR": str(out_dir),
        "VLLM_COLLECT_ENV": "0",
        "GPU_TOPOLOGY_SLUG": "test_gpu",
    }

    subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_kv_layout_probe.sh")],
        check=True,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert (out_dir / "kv_layout_probe.exit_code").read_text(
        encoding="utf-8"
    ).strip() == "0"
    assert (out_dir / "kv_layout_probe.json").exists()
    assert (out_dir / "kv_layout_probe.md").exists()
    assert (out_dir / "kv_layout_probe_packed_cache.bin").read_bytes() == b"\x00\x01"


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
    assert "scan_public_bundle" in script
    assert "load_oracle_cases" in script
    assert 'BASELINE_REQUIRE_ORACLE="${BASELINE_REQUIRE_ORACLE:-1}"' in script
    assert 'BASELINE_REQUIRE_GENERATION="${BASELINE_REQUIRE_GENERATION:-1}"' in script
    assert 'BASELINE_EXPECT_VARIANTS="${BASELINE_EXPECT_VARIANTS:-nomtp,mtp}"' in script
    assert "BASELINE_EXPECT_GENERATION_CASES_PER_VARIANT" in script
    assert "expected_case_count * len(expected_modes) * repeat_count" in script
    assert "_validate_generation_matrix" in script
    assert 'mv "${tmp_dir}" "${BASELINE_OUTPUT_DIR}"' in script


def test_baseline_bundle_script_can_archive_runs_without_oracle(tmp_path):
    run_dir = tmp_path / "artifacts" / "official_b300_mtp2_clean" / "20260505184836"
    acceptance_dir = run_dir / "mtp" / "acceptance"
    generation_dir = acceptance_dir / "generation" / "en"
    generation_dir.mkdir(parents=True)
    generation_row = {
        "case": "en_sum_tech_001",
        "language": "en",
        "thinking_mode": "non-thinking",
        "variant": "mtp",
        "round": 1,
        "temperature": 1.0,
        "top_p": 1.0,
        "ok": True,
        "response": {"usage": {"prompt_tokens": 8, "completion_tokens": 13}},
    }
    (acceptance_dir / "generation.jsonl").write_text(
        json.dumps(generation_row, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (generation_dir / "en_sum_tech_001.1.non-thinking.mtp.md").write_text(
        "# en_sum_tech_001\n\nok\n",
        encoding="utf-8",
    )
    (acceptance_dir / "toolcall15.json").write_text(
        json.dumps({"summary": {"points": 2, "max_points": 2}, "results": []}),
        encoding="utf-8",
    )
    bench_dir = run_dir / "mtp" / "bench_random_8192x512"
    bench_dir.mkdir(parents=True)
    (bench_dir / "bench.json").write_text(
        json.dumps(
            [
                {
                    "concurrency": 1,
                    "metrics": {"output_token_throughput_tok_s": 123.4},
                    "command": ["/workspace/vllm/.venv/bin/vllm", "bench", "serve"],
                }
            ]
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "baselines" / "20260505_official_b300_mtp2_clean"
    env = os.environ | {
        "PYTHON": sys.executable,
        "BASELINE_RUN_DIR": str(run_dir),
        "BASELINE_OUTPUT_DIR": str(output_dir),
        "BASELINE_REPORT_TITLE": "B300 Baseline",
        "BASELINE_REPORT_LABEL": "official_b300_mtp2_clean",
        "BASELINE_DATE": "20260505",
        "BASELINE_REQUIRE_ORACLE": "0",
        "BASELINE_EXPECT_VARIANTS": "mtp",
        "BASELINE_EXPECT_LANGUAGES": "en",
        "BASELINE_EXPECT_THINKING_MODES": "non-thinking",
        "BASELINE_EXPECT_GENERATION_REPEAT_COUNT": "1",
        "BASELINE_EXPECT_GENERATION_CASES_PER_VARIANT": "1",
    }

    subprocess.run(
        ["bash", str(ROOT / "scripts" / "generate_baseline_bundle.sh")],
        check=True,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )

    assert (output_dir / "report.md").exists()
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "generation" / "mtp.json").exists()
    assert (
        output_dir / "generation" / "en" / "en_sum_tech_001.1.non-thinking.mtp.md"
    ).exists()
    assert (output_dir / "toolcall15" / "mtp.json").exists()
    assert (output_dir / "performance" / "primary.json").exists()
    assert not (output_dir / "oracle").exists()
    assert "does not include an oracle export" in (
        output_dir / "README.md"
    ).read_text(encoding="utf-8")


def test_gpu_stats_helper_limits_sampling_to_visible_devices():
    script = (ROOT / "scripts" / "gpu_stats.sh").read_text(encoding="utf-8")

    assert 'GPU_STATS_DEVICE_IDS="${GPU_STATS_DEVICE_IDS:-${CUDA_VISIBLE_DEVICES:-}}"' in script
    assert 'query_args+=("-i" "${GPU_STATS_DEVICE_IDS}")' in script
    assert '"${query_args[@]}"' in script


def test_live_scripts_guard_against_unresponsive_servers():
    helper = (ROOT / "scripts" / "run_context.sh").read_text(encoding="utf-8")

    assert "server_ready()" in helper
    assert "wait_for_server_ready()" in helper
    assert "mark_server_unresponsive()" in helper
    assert "SERVER_RECOVERY_CMD" in helper
    assert "SERVER_STARTUP_TIMEOUT" in helper
    assert "server_unresponsive.txt" in helper
    assert 'GPU_TOPOLOGY_DEVICE_IDS:-${CUDA_VISIBLE_DEVICES:-}' in helper

    acceptance = (ROOT / "scripts" / "run_acceptance.sh").read_text(encoding="utf-8")
    bench = (ROOT / "scripts" / "run_bench_matrix.sh").read_text(encoding="utf-8")

    assert "run_live_gate" in acceptance
    assert "run_live_gate_capture" in acceptance
    assert "mark_gate_skipped" in acceptance
    assert "SERVER_HEALTH_TIMEOUT" in acceptance
    assert "SERVER_STARTUP_TIMEOUT" in acceptance
    assert "BENCH_TRANSIENT_FAILURE_RETRIES" in bench
    assert "--stop-on-unresponsive" in bench
    assert "--transient-failure-retries" in bench
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
        "run_lm_eval.sh",
        "run_oracle_export.sh",
        "run_official_api_baseline.sh",
        "run_b200_baseline.sh",
        "run_prefix_cache_probe.sh",
        "run_streaming_pressure_soak.sh",
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
        "  *' generation-matrix '*) write_arg_file --jsonl-output \"$@\"; exit 0 ;;\n"
        "  *' toolcall15 '*) write_arg_file --json-output \"$@\"; exit 0 ;;\n"
        "  *' kv-layout-probe '*) write_arg_file --json-output \"$@\"; write_arg_file --markdown-output \"$@\"; exit 0 ;;\n"
        "  *' long-context-probe '*) write_arg_file --json-output \"$@\"; write_arg_file --markdown-output \"$@\"; exit 0 ;;\n"
        "  *' bench-matrix '*) write_arg_file --json-output \"$@\"; exit 0 ;;\n"
        "  *' lm-eval '*) write_arg_file --json-output \"$@\"; printf '%s\\n' \"$@\" > \"$OUT_DIR/lm_eval_args.txt\"; exit 0 ;;\n"
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
    fake_lm_eval = tmp_path / "lm_eval"
    fake_lm_eval.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    fake_lm_eval.chmod(fake_lm_eval.stat().st_mode | 0o111)
    out_dir = tmp_path / "baseline"
    env = os.environ | {
        "PYTHON": str(fake_python),
        "VLLM_BIN": str(fake_vllm),
        "LM_EVAL_BIN": str(fake_lm_eval),
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
        "LM_EVAL_EXTRA_ARGS": "--limit 1",
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
    assert "nomtp\tkv_layout_probe\t0" in phase_log
    assert "nomtp\tacceptance\t0" in phase_log
    assert "nomtp\tlong_context_probe\t0" in phase_log
    assert "nomtp\tprefix_cache_probe\t0" in phase_log
    assert "nomtp\tbench_hf_mt_bench\t0" in phase_log
    assert "nomtp\teval_gsm8k\t0" in phase_log
    assert "nomtp\toracle_export\t0" in phase_log
    assert "mtp\tkv_layout_probe\t0" in phase_log
    assert "mtp\tacceptance\t0" in phase_log
    assert "mtp\tlong_context_probe\t0" in phase_log
    assert "mtp\tprefix_cache_probe\t0" in phase_log
    assert "mtp\tbench_hf_mt_bench\t0" in phase_log
    assert "mtp\teval_gsm8k\t0" in phase_log
    assert "mtp\toracle_export\t0" in phase_log
    nomtp_lm_eval_args = (out_dir / "nomtp" / "eval_gsm8k" / "lm_eval_args.txt").read_text(
        encoding="utf-8"
    )
    assert "--extra-lm-eval-arg=--limit" in nomtp_lm_eval_args
    assert "--extra-lm-eval-arg=1" in nomtp_lm_eval_args
    assert (out_dir / "baseline_summary.md").exists()
    assert "--speculative_config" in (out_dir / "mtp" / "serve_command.sh").read_text(
        encoding="utf-8"
    )
    assert "--max-model-len 393216" in (
        out_dir / "nomtp" / "serve_command.sh"
    ).read_text(encoding="utf-8")
    assert "wrote" in result.stdout


def run_minimal_b200_baseline(tmp_path, gpu_topology_slug):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
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
        "GPU_TOPOLOGY_SLUG": gpu_topology_slug,
        "B200_BASELINE_VARIANTS": "nomtp",
        "RUN_ACCEPTANCE": "0",
        "RUN_KV_LAYOUT_PROBE": "0",
        "RUN_LONG_CONTEXT_PROBE": "0",
        "RUN_BENCH_HF": "0",
        "RUN_RANDOM_LONG": "0",
        "RUN_LM_EVAL": "0",
        "RUN_ORACLE_EXPORT": "0",
        "SERVER_GUARD": "0",
        "GPU_STATS": "0",
        "RUNTIME_STATS": "0",
        "VLLM_COLLECT_ENV": "0",
    }

    subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_b200_baseline.sh")],
        check=True,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )

    return out_dir


def test_b200_baseline_driver_omits_fp4_indexer_cache_for_sm12x_auto(tmp_path):
    out_dir = run_minimal_b200_baseline(tmp_path, "2x_nvidia_rtx_pro_6000")
    command = (out_dir / "nomtp" / "serve_command.sh").read_text(encoding="utf-8")
    assert "--attention_config.use_fp4_indexer_cache=True" not in command


def test_b200_baseline_driver_enables_fp4_indexer_cache_for_b200_auto(tmp_path):
    out_dir = run_minimal_b200_baseline(tmp_path, "4x_nvidia_b200")
    command = (out_dir / "nomtp" / "serve_command.sh").read_text(encoding="utf-8")
    for expected in (
        "deepseek-ai/DeepSeek-V4-Flash",
        "--trust-remote-code",
        "--kv-cache-dtype fp8",
        "--block-size 256",
        "--max-model-len 393216",
        "--tensor-parallel-size 4",
        "--no-enable-flashinfer-autotune",
        "--reasoning-parser deepseek_v4",
        "--tokenizer-mode deepseek_v4",
        "--tool-call-parser deepseek_v4",
        "--enable-auto-tool-choice",
    ):
        assert expected in command
    assert "--attention_config.use_fp4_indexer_cache=True" in command


def test_b200_baseline_driver_can_run_single_phase_with_mocked_tools(tmp_path):
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
        "  *' generation-matrix '*) write_arg_file --jsonl-output \"$@\"; exit 0 ;;\n"
        "  *' toolcall15 '*) write_arg_file --json-output \"$@\"; exit 0 ;;\n"
        "  *' bench-matrix '*) write_arg_file --json-output \"$@\"; exit 0 ;;\n"
        "  *' lm-eval '*) write_arg_file --json-output \"$@\"; exit 0 ;;\n"
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
        "B200_BASELINE_VARIANTS": "mtp",
        "B200_BASELINE_PHASES": "acceptance",
        "SERVER_STARTUP_TIMEOUT": "5",
        "SERVER_STARTUP_INTERVAL_SECONDS": "0",
    }

    subprocess.run(
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
    assert "mtp\tserver_startup\t0" in phase_log
    assert "mtp\tacceptance\t0" in phase_log
    assert "bench_hf_mt_bench" not in phase_log
    assert "bench_random_8192x512" not in phase_log
    assert "eval_gsm8k" not in phase_log
    assert "oracle_export" not in phase_log
    assert (out_dir / "mtp" / "acceptance").exists()
    assert not (out_dir / "mtp" / "bench_hf_mt_bench").exists()


def test_b200_baseline_driver_can_run_variants_in_parallel_with_gpu_splits(tmp_path):
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
        "  *' generation-matrix '*) write_arg_file --jsonl-output \"$@\"; exit 0 ;;\n"
        "  *' toolcall15 '*) write_arg_file --json-output \"$@\"; exit 0 ;;\n"
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
        "B200_BASELINE_PHASES": "acceptance",
        "B200_VARIANT_PARALLEL": "1",
        "B200_PARALLEL_GPU_GROUPS": "nomtp=0,1;mtp=2,3",
        "B200_PARALLEL_TENSOR_PARALLEL_SIZE": "2",
        "B200_PARALLEL_PORTS": "nomtp=18080;mtp=18081",
        "SERVER_STARTUP_TIMEOUT": "5",
        "SERVER_STARTUP_INTERVAL_SECONDS": "0",
    }

    subprocess.run(
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
    assert "nomtp\tserver_startup\t0" in phase_log
    assert "mtp\tserver_startup\t0" in phase_log
    assert "nomtp\tacceptance\t0" in phase_log
    assert "mtp\tacceptance\t0" in phase_log
    assert (out_dir / "nomtp" / "acceptance").exists()
    assert (out_dir / "mtp" / "acceptance").exists()
    assert not (out_dir / "_parallel_nomtp").exists()
    nomtp_command = (out_dir / "nomtp" / "serve_command.sh").read_text(
        encoding="utf-8"
    )
    mtp_command = (out_dir / "mtp" / "serve_command.sh").read_text(
        encoding="utf-8"
    )
    assert 'CUDA_VISIBLE_DEVICES="0,1"' in nomtp_command
    assert 'CUDA_VISIBLE_DEVICES="2,3"' in mtp_command
    assert "--tensor-parallel-size 2" in nomtp_command
    assert "--port 18080" in nomtp_command
    assert "--port 18081" in mtp_command


def test_b200_baseline_driver_rejects_unknown_phase_before_launch(tmp_path):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    fake_python.chmod(fake_python.stat().st_mode | 0o111)
    fake_vllm = tmp_path / "fake-vllm"
    launched = tmp_path / "launched"
    fake_vllm.write_text(
        "#!/usr/bin/env sh\n"
        f"printf launched > {launched}\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_vllm.chmod(fake_vllm.stat().st_mode | 0o111)
    out_dir = tmp_path / "baseline"
    env = os.environ | {
        "PYTHON": str(fake_python),
        "VLLM_BIN": str(fake_vllm),
        "OUT_DIR": str(out_dir),
        "B200_BASELINE_PHASES": "acceptnace",
    }

    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_b200_baseline.sh")],
        check=False,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )

    assert result.returncode == 2
    assert "unsupported B200 baseline phase" in result.stderr
    assert not launched.exists()


def test_b200_baseline_driver_preflights_lm_eval_before_launch(tmp_path):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    fake_python.chmod(fake_python.stat().st_mode | 0o111)
    fake_vllm = tmp_path / "fake-vllm"
    launched = tmp_path / "launched"
    fake_vllm.write_text(
        "#!/usr/bin/env sh\n"
        f"printf launched > {launched}\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_vllm.chmod(fake_vllm.stat().st_mode | 0o111)
    out_dir = tmp_path / "baseline"
    env = os.environ | {
        "PYTHON": str(fake_python),
        "VLLM_BIN": str(fake_vllm),
        "OUT_DIR": str(out_dir),
        "B200_BASELINE_PHASES": "eval_gsm8k",
        "RUN_LM_EVAL": "1",
        "LM_EVAL_BIN": str(tmp_path / "missing-lm-eval"),
    }

    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_b200_baseline.sh")],
        check=False,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )

    assert result.returncode == 2
    assert "LM_EVAL_BIN is not executable" in result.stderr
    assert not launched.exists()


def test_b200_baseline_driver_preflights_lm_eval_api_dependencies(tmp_path):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "#!/usr/bin/env sh\n"
        "if [ \"$1\" = '-' ]; then exit 1; fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_python.chmod(fake_python.stat().st_mode | 0o111)
    fake_vllm = tmp_path / "fake-vllm"
    launched = tmp_path / "launched"
    fake_vllm.write_text(
        "#!/usr/bin/env sh\n"
        f"printf launched > {launched}\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_vllm.chmod(fake_vllm.stat().st_mode | 0o111)
    fake_lm_eval = tmp_path / "lm_eval"
    fake_lm_eval.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    fake_lm_eval.chmod(fake_lm_eval.stat().st_mode | 0o111)
    out_dir = tmp_path / "baseline"
    env = os.environ | {
        "PYTHON": str(fake_python),
        "VLLM_BIN": str(fake_vllm),
        "OUT_DIR": str(out_dir),
        "B200_BASELINE_PHASES": "eval_gsm8k",
        "RUN_LM_EVAL": "1",
        "LM_EVAL_BIN": str(fake_lm_eval),
    }

    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_b200_baseline.sh")],
        check=False,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )

    assert result.returncode == 2
    assert "lm_eval API dependencies are missing" in result.stderr
    assert not launched.exists()


def test_lm_eval_wrapper_runs_gsm8k_eval_with_guarded_artifacts(tmp_path):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text(
        "#!/usr/bin/env sh\n"
        "case \"$*\" in\n"
        "  *' env-summary '*) exit 0 ;;\n"
        "  *' health'*) printf '%s\\n' '{\"ok\":true}'; exit 0 ;;\n"
        "  *' lm-eval '*) mkdir -p \"$OUT_DIR\"; printf '%s\\n' \"$@\" > \"$OUT_DIR/lm_eval_args.txt\"; printf '%s\\n' '{}' > \"$OUT_DIR/lm_eval_summary.json\"; exit 0 ;;\n"
        "esac\n"
        "exit 0\n",
        encoding="utf-8",
    )
    fake_python.chmod(fake_python.stat().st_mode | 0o111)
    out_dir = tmp_path / "eval"
    env = os.environ | {
        "PYTHON": str(fake_python),
        "OUT_DIR": str(out_dir),
        "GPU_STATS": "0",
        "RUNTIME_STATS": "0",
        "VLLM_COLLECT_ENV": "0",
        "GPU_TOPOLOGY_SLUG": "test_gpu",
        "LM_EVAL_TASKS": "gsm8k",
        "LM_EVAL_EXTRA_ARGS": "--limit 1",
        "SERVER_STARTUP_INTERVAL_SECONDS": "0",
        "SERVE_LOG": "",
    }

    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_lm_eval.sh")],
        check=True,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    assert (out_dir / "lm_eval.exit_code").read_text(encoding="utf-8").strip() == "0"
    assert (out_dir / "lm_eval_summary.json").exists()
    args = (out_dir / "lm_eval_args.txt").read_text(encoding="utf-8")
    assert "--extra-lm-eval-arg=--limit" in args
    assert "--extra-lm-eval-arg=1" in args
    assert "--tokenizer-backend" in args
    assert "none" in args
    assert f"wrote {out_dir}" in result.stdout


def test_b200_baseline_driver_archives_previous_managed_artifacts(tmp_path):
    fake_python = tmp_path / "fake-python"
    fake_python.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    fake_python.chmod(fake_python.stat().st_mode | 0o111)
    fake_vllm = tmp_path / "fake-vllm"
    fake_vllm.write_text(
        "#!/usr/bin/env sh\n"
        "trap 'exit 0' TERM INT\n"
        "while :; do sleep 1; done\n",
        encoding="utf-8",
    )
    fake_vllm.chmod(fake_vllm.stat().st_mode | 0o111)
    artifact_root = tmp_path / "artifacts"
    parent = artifact_root / "main" / "4x_b200"
    old_label_dir = parent / "b200_tp4_main_5737770c6"
    old_extra_dir = parent / "b200_tp4_main_5737770c6_extra"
    old_label_dir.mkdir(parents=True)
    old_extra_dir.mkdir()
    (old_label_dir / "old.txt").write_text("old", encoding="utf-8")
    (old_extra_dir / "old.txt").write_text("old", encoding="utf-8")

    env = os.environ | {
        "PYTHON": str(fake_python),
        "VLLM_BIN": str(fake_vllm),
        "ARTIFACT_ROOT": str(artifact_root),
        "BRANCH_NAME": "main",
        "GPU_TOPOLOGY_SLUG": "4x_b200",
        "B200_BASELINE_LABEL": "b200_tp4_main_5737770c6",
        "RUN_TIMESTAMP": "20260502010102",
        "B200_BASELINE_VARIANTS": "nomtp",
        "RUN_ACCEPTANCE": "0",
        "RUN_BENCH_HF": "0",
        "RUN_RANDOM_LONG": "0",
        "RUN_LM_EVAL": "0",
        "RUN_ORACLE_EXPORT": "0",
        "SERVER_GUARD": "0",
        "GPU_STATS": "0",
        "RUNTIME_STATS": "0",
        "VLLM_COLLECT_ENV": "0",
    }

    subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_b200_baseline.sh")],
        check=True,
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=30,
    )

    archive_dir = parent / "_archive_before_20260502010102"
    assert (archive_dir / "b200_tp4_main_5737770c6" / "old.txt").exists()
    assert (archive_dir / "b200_tp4_main_5737770c6_extra" / "old.txt").exists()
    assert (archive_dir / "archive_manifest.tsv").exists()
    assert (
        parent / "b200_tp4_main_5737770c6" / "20260502010102" / "baseline_summary.md"
    ).exists()


def test_generate_baseline_report_wrapper_uses_report_cli():
    script = (ROOT / "scripts" / "generate_baseline_report.sh").read_text(
        encoding="utf-8"
    )

    assert "load_harness_env" in script
    assert "baseline-report" in script
    assert "BASELINE_RUN_DIR" in script
    assert "BASELINE_REPORT_OUTPUT" in script
    assert "BASELINE_REPORT_DATE" in script
    assert 'baselines/${BASELINE_REPORT_DATE}_${output_label}/report.md' in script


def test_official_api_baseline_script_writes_separate_baseline_directory():
    script = (ROOT / "scripts" / "run_official_api_baseline.sh").read_text(
        encoding="utf-8"
    )

    assert "load_harness_env" in script
    assert 'OFFICIAL_BASELINE_DATE="${OFFICIAL_BASELINE_DATE:-$(date +%Y%m%d)}"' in script
    assert 'OFFICIAL_BASELINE_DIR="${OFFICIAL_BASELINE_DIR:-${REPO_ROOT}/baselines/${OFFICIAL_BASELINE_DATE}_${OFFICIAL_BASELINE_LABEL}}"' in script
    assert 'OFFICIAL_GENERATION_PROMPTS="${OFFICIAL_GENERATION_PROMPTS:-zh_wr_tech_001,en_wr_tech_001,zh_code_fe_001,en_code_be_001,zh2en_tech_001,en2zh_tech_001,zh_sum_tech_001,en_sum_tech_001}"' in script
    assert 'OFFICIAL_SMOKE_CASES="${OFFICIAL_SMOKE_CASES:-math_7_times_8,capital_of_france,spanish_greeting}"' in script
    assert 'OFFICIAL_REQUEST_RETRIES="${OFFICIAL_REQUEST_RETRIES:-1}"' in script
    assert 'OFFICIAL_TOOLCALL15_THINKING_MODES="${OFFICIAL_TOOLCALL15_THINKING_MODES:-${OFFICIAL_THINKING_MODES}}"' in script
    assert 'OFFICIAL_TOOLCALL15_TEMPERATURE="${OFFICIAL_TOOLCALL15_TEMPERATURE:-${OFFICIAL_TEMPERATURE}}"' in script
    assert 'OFFICIAL_TOOLCALL15_TOP_P="${OFFICIAL_TOOLCALL15_TOP_P:-${OFFICIAL_TOP_P}}"' in script
    assert 'OFFICIAL_GENERATION_EXPECTATION_CHECKS="${OFFICIAL_GENERATION_EXPECTATION_CHECKS:-0}"' in script
    assert "chat-smoke" in script
    assert "generation-matrix" in script
    assert "toolcall15" in script
    assert "official-baseline" in script
    assert "official_smoke.jsonl" in script
    assert "official_generation.jsonl" in script
    assert "official_toolcall15.json" in script
    assert "report.md" in script
    assert 'OFFICIAL_REPEAT_COUNT="${OFFICIAL_REPEAT_COUNT:-3}"' in script
    assert '--request-retries "${OFFICIAL_REQUEST_RETRIES}"' in script
    assert '--temperature "${OFFICIAL_TEMPERATURE}"' in script
    assert '--top-p "${OFFICIAL_TOP_P}"' in script
    assert '--temperature "${OFFICIAL_TOOLCALL15_TEMPERATURE}"' in script
    assert '--top-p "${OFFICIAL_TOOLCALL15_TOP_P}"' in script
    assert '--skip-expectation-checks' in script
    assert '--thinking-mode "${thinking_mode}"' in script


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
