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
    assert 'IGNORE_EOS="${IGNORE_EOS:-0}"' in script
    assert '--dataset-name "${DATASET_NAME}"' in script
    assert '--dataset-path "${DATASET_PATH}"' in script
    assert 'EXTRA_ARGS+=(--ignore-eos)' in script
    assert '"${EXTRA_ARGS[@]}"' in script


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
