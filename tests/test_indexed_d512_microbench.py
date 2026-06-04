import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_microbench_module():
    path = ROOT / "scripts" / "run_sm12x_indexed_d512_split_microbench.py"
    spec = importlib.util.spec_from_file_location("indexed_d512_microbench", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sliding_window_index_pattern_requires_window_room():
    module = _load_microbench_module()

    module._validate_sliding_window_index_shape(
        num_tokens=4,
        num_candidates=8,
        kv_tokens=11,
    )

    try:
        module._validate_sliding_window_index_shape(
            num_tokens=4,
            num_candidates=8,
            kv_tokens=10,
        )
    except ValueError as exc:
        assert "kv_tokens" in str(exc)
        assert "sliding-window" in str(exc)
    else:
        raise AssertionError("expected sliding-window shape validation to fail")


def test_indexed_d512_microbench_exposes_sliding_window_pattern():
    script = (ROOT / "scripts" / "run_sm12x_indexed_d512_split_microbench.py").read_text(
        encoding="utf-8"
    )

    assert 'choices=("per-token", "shared", "sliding-window")' in script
    assert 'elif args.index_pattern == "sliding-window":' in script
