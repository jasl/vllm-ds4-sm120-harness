import argparse
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_microbench_module():
    path = ROOT / "scripts" / "run_sm12x_b12x_mhc_microbench.py"
    spec = importlib.util.spec_from_file_location("b12x_mhc_microbench", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_b12x_mhc_microbench_parse_int_list():
    module = _load_microbench_module()

    assert module._parse_int_list("1, 4,16") == [1, 4, 16]

    for value in ("", "0", "-1", "1,nope"):
        try:
            module._parse_int_list(value)
        except argparse.ArgumentTypeError:
            pass
        else:
            raise AssertionError("expected invalid integer list to fail")


def test_b12x_mhc_microbench_markdown_records_speedup(tmp_path: Path):
    module = _load_microbench_module()
    output = tmp_path / "mhc.md"
    payload = {
        "device_name": "fake-gpu",
        "compute_capability": [12, 1],
        "hidden_size": 4096,
        "hc_mult": 4,
        "split_k": 64,
        "block_k": 256,
        "use_norm_weight": True,
        "warmup": 1,
        "iterations": 2,
        "rows": [
            {
                "num_tokens": 256,
                "tilelang_fused_mean_ms": 1.0,
                "b12x_fused_mean_ms": 0.5,
                "b12x_fused_speedup": 2.0,
                "max_abs_diff_residual": 0.0,
                "max_abs_diff_post": 0.0,
                "max_abs_diff_comb": 0.0,
                "max_abs_diff_y": 0.0,
            }
        ],
    }

    module._write_markdown(output, payload)

    text = output.read_text(encoding="utf-8")
    assert "# SM12x b12x mHC microbench" in text
    assert "| 256 | 1.000 | 0.500 | 2.000x |" in text


def test_b12x_mhc_microbench_uses_fused_b12x_and_tilelang_paths():
    script = (ROOT / "scripts" / "run_sm12x_b12x_mhc_microbench.py").read_text(
        encoding="utf-8"
    )

    assert "b12x_mhc_post_pre" in script
    assert "empty_mhc_workspace" in script
    assert "mhc_fused_post_pre_tilelang" in script
    assert "--no-norm-weight" in script
