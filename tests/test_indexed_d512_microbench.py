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


def test_mixed_c128_swa_index_pattern_validates_compressed_split():
    module = _load_microbench_module()

    module._validate_mixed_c128_swa_index_shape(
        num_tokens=4,
        num_candidates=10,
        compressed_candidates=2,
        kv_tokens=11,
    )

    for compressed_candidates in (0, 10):
        try:
            module._validate_mixed_c128_swa_index_shape(
                num_tokens=4,
                num_candidates=10,
                compressed_candidates=compressed_candidates,
                kv_tokens=11,
            )
        except ValueError as exc:
            assert "compressed" in str(exc)
        else:
            raise AssertionError("expected mixed C128/SWA validation to fail")


def test_candidate_chunks_split_wide_candidate_lists():
    module = _load_microbench_module()

    assert module._candidate_chunks(4224, 1152) == [
        (0, 1152),
        (1152, 2304),
        (2304, 3456),
        (3456, 4224),
    ]
    assert module._candidate_chunks(1152, 1152) == [(0, 1152)]
    assert module._candidate_chunks(1153, 1152) == [(0, 1152), (1152, 1153)]

    for chunk_size in (0, -1):
        try:
            module._candidate_chunks(128, chunk_size)
        except ValueError as exc:
            assert "chunk_size" in str(exc)
        else:
            raise AssertionError("expected candidate chunk validation to fail")


def test_indexed_d512_microbench_exposes_sliding_window_pattern():
    script = (ROOT / "scripts" / "run_sm12x_indexed_d512_split_microbench.py").read_text(
        encoding="utf-8"
    )

    assert '"c128a-current"' in script
    assert '--compressed-candidates' in script
    assert 'elif args.index_pattern == "sliding-window":' in script
    assert 'elif args.index_pattern == "mixed-c128-swa":' in script
    assert 'elif args.index_pattern == "c128a-current":' in script
    assert "compressed_indices.repeat(args.num_tokens, 1)" in script


def test_indexed_d512_microbench_exposes_wide_chunked_split_mode():
    script = (ROOT / "scripts" / "run_sm12x_indexed_d512_split_microbench.py").read_text(
        encoding="utf-8"
    )

    assert "--wide-split-chunk-candidates" in script
    assert "_indexed_merge_normalized_chunk_kernel" in script
    assert "wide_split_speedup" in script
    assert "wide_score_workspace_mib" in script


def test_indexed_d512_microbench_compares_production_split_finish_with_sink():
    script = (ROOT / "scripts" / "run_sm12x_indexed_d512_split_microbench.py").read_text(
        encoding="utf-8"
    )

    assert "accumulate_indexed_d512_split_sparse_mla_attention" in script
    assert "accumulate_indexed_d512_split_sparse_mla_attention_with_sink" in script
    assert "finish_sparse_mla_attention_with_sink" in script
    assert "--production-with-sink" in script
    assert "production_split_finish_mean_ms" in script
    assert "production_fused_with_sink_mean_ms" in script
    assert "production_fused_with_sink_speedup" in script
