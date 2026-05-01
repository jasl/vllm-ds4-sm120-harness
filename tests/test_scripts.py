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
