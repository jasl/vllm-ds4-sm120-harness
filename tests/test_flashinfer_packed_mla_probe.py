import json

import pytest

from ds4_harness import flashinfer_packed_mla_probe as probe


def test_build_config_uses_c128a_defaults():
    cfg = probe.build_config(case="c128a_prefill")

    assert cfg.num_tokens == 256
    assert cfg.num_heads == 64
    assert cfg.compress_ratio == 128
    assert cfg.extra_page_block_size == 2


def test_prefill_length_rows_match_ds4_c4a_semantics():
    rows = probe.prefill_length_rows(
        num_tokens=6,
        window_size=4,
        compress_ratio=2,
        topk=8,
    )

    assert rows == [
        {"token": 0, "main_len": 1, "extra_len": 0, "total_len": 1},
        {"token": 1, "main_len": 2, "extra_len": 1, "total_len": 3},
        {"token": 2, "main_len": 3, "extra_len": 1, "total_len": 4},
        {"token": 3, "main_len": 4, "extra_len": 2, "total_len": 6},
        {"token": 4, "main_len": 4, "extra_len": 2, "total_len": 6},
        {"token": 5, "main_len": 4, "extra_len": 3, "total_len": 7},
    ]
    assert probe.summarize_length_rows(rows) == {
        "num_tokens": 6,
        "main_len_min": 1,
        "main_len_max": 4,
        "extra_len_min": 0,
        "extra_len_max": 3,
        "total_len_min": 1,
        "total_len_max": 7,
    }


def test_build_config_rejects_decode_sized_probe():
    with pytest.raises(ValueError, match="num_tokens must be >64"):
        probe.build_config(case="c4a_prefill", num_tokens=64)


def test_write_markdown_includes_index_semantics(tmp_path):
    result = {
        "ok": True,
        "case": "c4a_prefill",
        "config": {
            "num_tokens": 128,
            "num_heads": 64,
            "window_size": 128,
            "compress_ratio": 4,
            "topk": 512,
        },
        "cache": {"main_page_block_size": 64, "extra_page_block_size": 64},
        "indices": {
            "combined_shape": [128, 640],
            "main_shape": [128, 128],
            "extra_shape": [128, 512],
            "helper_lens_match": True,
            "main_past_len_ok": True,
            "extra_past_len_ok": True,
        },
        "run": {
            "elapsed_ms": 1.25,
            "output_absmax": 0.0,
            "lse_error_max": 0.0,
        },
    }
    path = tmp_path / "probe.md"

    probe.write_markdown(path, result)

    text = path.read_text(encoding="utf-8")
    assert "# FlashInfer Packed SM120 Sparse MLA Probe" in text
    assert "Helper lens match: `True`" in text
    assert "Past-length invalid: main `True`, extra `True`" in text


def test_cli_writes_failure_json_for_missing_runtime(monkeypatch, tmp_path):
    def fake_run(_config):
        raise ModuleNotFoundError("flashinfer.sparse_mla_sm120")

    monkeypatch.setattr(probe, "run_packed_mla_probe", fake_run)
    json_path = tmp_path / "probe.json"

    monkeypatch.setattr(
        probe,
        "_parse_args",
        lambda: type(
            "Args",
            (),
            {
                "case": "c4a_prefill",
                "num_tokens": None,
                "num_heads": None,
                "window_size": None,
                "compress_ratio": None,
                "topk": None,
                "extra_page_block_size": None,
                "seed": 0,
                "device": "cuda",
                "json_output": json_path,
                "markdown_output": None,
            },
        )(),
    )

    assert probe.main() == 1
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["ok"] is False
    assert data["error"]["type"] == "ModuleNotFoundError"


def test_cli_can_attach_layout_variant_results(monkeypatch, tmp_path):
    monkeypatch.setattr(
        probe,
        "run_packed_mla_probe",
        lambda _config: {"ok": True, "case": "c4a_prefill"},
    )
    monkeypatch.setattr(
        probe,
        "run_packed_mla_layout_variants",
        lambda _config: [
            {"label": "contiguous", "ok": True},
            {"label": "noncontiguous_indices", "ok": False},
        ],
    )
    json_path = tmp_path / "probe.json"

    monkeypatch.setattr(
        probe,
        "_parse_args",
        lambda: type(
            "Args",
            (),
            {
                "case": "c4a_prefill",
                "num_tokens": None,
                "num_heads": None,
                "window_size": None,
                "compress_ratio": None,
                "topk": None,
                "extra_page_block_size": None,
                "seed": 0,
                "device": "cuda",
                "layout_variants": True,
                "json_output": json_path,
                "markdown_output": None,
            },
        )(),
    )

    assert probe.main() == 0
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["layout_variants"] == [
        {"label": "contiguous", "ok": True},
        {"label": "noncontiguous_indices", "ok": False},
    ]
