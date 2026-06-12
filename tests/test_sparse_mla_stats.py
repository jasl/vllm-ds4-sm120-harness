import json

from ds4_harness import cli
from ds4_harness.sparse_mla_stats import (
    build_sparse_mla_stats_report,
    write_sparse_mla_stats_markdown,
)


def _write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _stats_row(**overrides):
    row = {
        "kind": "deepseek_v4_sparse_mla_prefill_stats",
        "version": 1,
        "rank": 0,
        "cuda_device": 0,
        "layer_type": "mla_prefill_chunk",
        "layer_prefix": "model.layers.3.self_attn",
        "compress_ratio": 128,
        "num_prefills": 2,
        "query_tokens": 256,
        "combined_topk": 1152,
        "candidate_slots": 294912,
        "effective_candidate_visits": 196608,
        "padding_candidate_visits": 98304,
        "combined_lens": {
            "count": 256,
            "min": 512,
            "p50": 768,
            "p95": 1024,
            "p99": 1152,
            "max": 1152,
            "sum": 196608,
        },
        "stage_timings_ms": {
            "gather_compressed_kv": 1.5,
            "gather_swa_kv": 2.5,
            "combine_indices": 3.0,
            "sparse_accumulate": 14.0,
        },
        "candidate_overlap": {
            "sample_rows": 4,
            "groups": {
                "2": {
                    "groups": 2,
                    "valid_candidates": 20,
                    "unique_candidates": 12,
                    "unique_to_valid_ratio": 0.6,
                },
                "4": {
                    "groups": 1,
                    "valid_candidates": 20,
                    "unique_candidates": 7,
                    "unique_to_valid_ratio": 0.35,
                },
            },
        },
        "candidate_region_overlap": {
            "sample_rows": 4,
            "compressed": {
                "2": {
                    "groups": 2,
                    "valid_candidates": 8,
                    "unique_candidates": 4,
                    "unique_to_valid_ratio": 0.5,
                },
            },
            "swa": {
                "2": {
                    "groups": 2,
                    "valid_candidates": 12,
                    "unique_candidates": 8,
                    "unique_to_valid_ratio": 0.666667,
                },
            },
        },
        "candidate_region_work": {
            "compressed": {
                "candidate_slots": 32768,
                "effective_candidate_visits": 8192,
                "padding_candidate_visits": 24576,
                "padding_ratio": 0.75,
            },
            "swa": {
                "candidate_slots": 262144,
                "effective_candidate_visits": 188416,
                "padding_candidate_visits": 73728,
                "padding_ratio": 0.28125,
            },
        },
        "accumulate_work": {
            "path": "triton_chunked",
            "query_tokens": 256,
            "effective_candidate_visits": 196608,
            "head_dim": 512,
            "local_heads": 64,
            "query_chunk_size": 128,
            "topk_chunk_size": 384,
            "query_chunk_count": 2,
            "topk_chunk_count": 3,
            "accumulate_kernel_launches": 6,
            "candidate_score_elements": 12582912,
            "candidate_value_read_bytes_estimate": 201326592,
            "q_read_bytes_estimate": 50331648,
            "output_write_bytes_estimate": 16777216,
            "state_workspace_bytes": 16842752,
            "score_workspace_bytes": 0,
        },
        "mqa_topk_work": [
            {
                "path": "triton_full",
                "query_tokens": 256,
                "kv_tokens": 32768,
                "topk_tokens": 1152,
                "valid_kv_visits": 8_388_608,
                "logits_elements": 8_388_608,
                "logits_padding_elements": 0,
                "logits_valid_ratio": 1.0,
                "logits_padding_ratio": 0.0,
                "materialized_logits_bytes": 33_554_432,
                "peak_logits_bytes": 33_554_432,
                "estimated_temp_bytes": 34_734_080,
                "mqa_logits_launches": 1,
                "topk_merge_count": 1,
                "elapsed_ms": 1.25,
                "weight_sign": {
                    "count": 512,
                    "positive": 300,
                    "negative": 200,
                    "zero": 12,
                    "positive_ratio": 0.5859375,
                    "negative_ratio": 0.390625,
                    "zero_ratio": 0.0234375,
                    "min": -3.5,
                    "max": 4.0,
                    "abs_max": 4.0,
                },
                "kv_span": {
                    "count": 256,
                    "min": 32768,
                    "p50": 32768,
                    "p95": 32768,
                    "p99": 32768,
                    "max": 32768,
                    "sum": 8_388_608,
                },
            }
        ],
        "candidate_row_duplicates": {
            "sample_rows": 4,
            "valid_candidates": 20,
            "unique_candidates": 18,
            "duplicate_candidate_visits": 2,
            "duplicate_visit_ratio": 0.1,
            "rows_with_duplicates": 1,
            "row_duplicate_ratio": 0.25,
            "regions": {
                "compressed": {
                    "sample_rows": 4,
                    "valid_candidates": 8,
                    "unique_candidates": 7,
                    "duplicate_candidate_visits": 1,
                    "duplicate_visit_ratio": 0.125,
                    "rows_with_duplicates": 1,
                    "row_duplicate_ratio": 0.25,
                },
                "swa": {
                    "sample_rows": 4,
                    "valid_candidates": 12,
                    "unique_candidates": 11,
                    "duplicate_candidate_visits": 1,
                    "duplicate_visit_ratio": 0.083333,
                    "rows_with_duplicates": 1,
                    "row_duplicate_ratio": 0.25,
                },
            },
        },
    }
    row.update(overrides)
    return row


def test_sparse_mla_stats_report_summarizes_candidate_work(tmp_path):
    stats_path = tmp_path / "stats.jsonl"
    _write_jsonl(
        stats_path,
        [
            _stats_row(),
            _stats_row(
                rank=1,
                cuda_device=1,
                layer_type="mla_prefill_partial",
                compress_ratio=256,
                query_tokens=128,
                combined_topk=640,
                candidate_slots=81920,
                effective_candidate_visits=40960,
                padding_candidate_visits=40960,
                combined_lens={
                    "count": 128,
                    "min": 128,
                    "p50": 320,
                    "p95": 512,
                    "p99": 640,
                    "max": 640,
                    "sum": 40960,
                },
                stage_timings_ms={
                    "gather_compressed_kv": 0.5,
                    "gather_swa_kv": 1.5,
                    "combine_indices": 2.0,
                    "sparse_accumulate": 8.0,
                },
                accumulate_work={
                    "path": "triton_chunked",
                    "query_tokens": 128,
                    "effective_candidate_visits": 40960,
                    "head_dim": 512,
                    "local_heads": 64,
                    "query_chunk_size": 128,
                    "topk_chunk_size": 320,
                    "query_chunk_count": 1,
                    "topk_chunk_count": 2,
                    "accumulate_kernel_launches": 2,
                    "candidate_score_elements": 2621440,
                    "candidate_value_read_bytes_estimate": 41943040,
                    "q_read_bytes_estimate": 16777216,
                    "output_write_bytes_estimate": 8388608,
                    "state_workspace_bytes": 16842752,
                    "score_workspace_bytes": 0,
                },
            ),
        ],
    )

    report = build_sparse_mla_stats_report(stats_path)

    assert report["stats_path"] == "stats.jsonl"
    assert report["row_count"] == 2
    assert report["skipped_line_count"] == 0
    assert report["counts_by_stats_file"] == {"stats.jsonl": 2}
    assert report["counts_by_rank"] == {"0": 1, "1": 1}
    assert report["counts_by_cuda_device"] == {"0": 1, "1": 1}
    assert report["counts_by_layer_type"] == {
        "mla_prefill_chunk": 1,
        "mla_prefill_partial": 1,
    }
    assert report["counts_by_compress_ratio"] == {"128": 1, "256": 1}
    summary = report["candidate_work"]
    assert summary["candidate_slots"] == 376832
    assert summary["effective_candidate_visits"] == 237568
    assert summary["padding_candidate_visits"] == 139264
    assert summary["padding_ratio"] == 0.369565
    assert summary["combined_lens_count"] == 384
    assert summary["combined_lens_mean"] == 618.666667
    assert summary["combined_lens_max"] == 1152
    timings = report["stage_timings_ms"]
    assert timings["total"] == 33.0
    assert timings["stages"]["gather_compressed_kv"]["total"] == 2.0
    assert timings["stages"]["gather_compressed_kv"]["ratio"] == 0.060606
    assert timings["stages"]["gather_swa_kv"]["total"] == 4.0
    assert timings["stages"]["combine_indices"]["total"] == 5.0
    assert timings["stages"]["sparse_accumulate"]["total"] == 22.0
    assert timings["dominant_stage"] == "sparse_accumulate"
    efficiency = report["stage_efficiency"]
    assert efficiency["effective_candidate_visits_per_s"] == 7199030.30303
    assert efficiency["sparse_accumulate_effective_candidate_visits_per_s"] == (
        10798545.454545
    )
    assert efficiency["sparse_accumulate_ms_per_million_effective_visits"] == (
        92.605065
    )
    assert efficiency["candidate_slots_per_s"] == 11419151.515152
    overlap = report["candidate_overlap"]
    assert overlap["sample_rows"] == 8
    assert overlap["groups"]["2"]["groups"] == 4
    assert overlap["groups"]["2"]["valid_candidates"] == 40
    assert overlap["groups"]["2"]["unique_candidates"] == 24
    assert overlap["groups"]["2"]["unique_to_valid_ratio"] == 0.6
    assert overlap["regions"]["compressed"]["2"]["valid_candidates"] == 16
    assert overlap["regions"]["compressed"]["2"]["unique_to_valid_ratio"] == 0.5
    assert overlap["regions"]["swa"]["2"]["valid_candidates"] == 24
    assert overlap["regions"]["swa"]["2"]["unique_to_valid_ratio"] == 0.666667
    reuse = report["cross_query_reuse_potential"]
    assert reuse["sample_rows"] == 8
    assert reuse["regions"]["all"]["2"]["sampled_valid_candidate_visits"] == 40
    assert reuse["regions"]["all"]["2"]["sampled_union_candidate_visits"] == 24
    assert reuse["regions"]["all"]["2"]["sampled_reusable_candidate_visits"] == 16
    assert reuse["regions"]["all"]["2"]["sampled_reuse_ratio"] == 0.4
    assert reuse["regions"]["compressed"]["2"]["sampled_reuse_ratio"] == 0.5
    assert reuse["regions"]["compressed"]["2"]["effective_visit_share"] == 0.041667
    assert reuse["regions"]["swa"]["2"]["sampled_reuse_ratio"] == 0.333333
    assert reuse["regions"]["swa"]["2"]["effective_visit_share"] == 0.958333
    duplicates = report["candidate_row_duplicates"]
    assert duplicates["sample_rows"] == 8
    assert duplicates["valid_candidates"] == 40
    assert duplicates["unique_candidates"] == 36
    assert duplicates["duplicate_candidate_visits"] == 4
    assert duplicates["duplicate_visit_ratio"] == 0.1
    assert duplicates["rows_with_duplicates"] == 2
    assert duplicates["row_duplicate_ratio"] == 0.25
    assert duplicates["regions"]["compressed"]["duplicate_candidate_visits"] == 2
    assert duplicates["regions"]["swa"]["duplicate_candidate_visits"] == 2
    region_work = report["candidate_region_work"]
    assert region_work["compressed"]["candidate_slots"] == 65536
    assert region_work["compressed"]["effective_candidate_visits"] == 16384
    assert region_work["compressed"]["padding_candidate_visits"] == 49152
    assert region_work["compressed"]["padding_ratio"] == 0.75
    assert region_work["swa"]["candidate_slots"] == 524288
    assert region_work["swa"]["effective_candidate_visits"] == 376832
    assert region_work["swa"]["padding_candidate_visits"] == 147456
    assert region_work["swa"]["padding_ratio"] == 0.28125
    assert report["groups"][0]["layer_type"] == "mla_prefill_chunk"
    assert report["groups"][0]["padding_ratio"] == 0.333333
    assert report["groups"][0]["stage_timings_ms"]["total"] == 21.0
    assert report["groups"][0]["stage_timings_ms"]["dominant_stage"] == (
        "sparse_accumulate"
    )
    assert report["groups"][0]["stage_efficiency"][
        "sparse_accumulate_effective_candidate_visits_per_s"
    ] == 14043428.571429
    assert report["groups"][0]["candidate_overlap"]["groups"]["4"][
        "unique_to_valid_ratio"
    ] == 0.35
    assert report["groups"][0]["candidate_overlap"]["regions"]["compressed"]["2"][
        "unique_to_valid_ratio"
    ] == 0.5
    assert report["groups"][0]["candidate_region_work"]["swa"][
        "effective_candidate_visits"
    ] == 188416
    assert report["groups"][0]["candidate_row_duplicates"][
        "duplicate_candidate_visits"
    ] == 2
    accumulate_work = report["accumulate_work"]
    assert accumulate_work["query_tokens"] == 384
    assert accumulate_work["effective_candidate_visits"] == 237568
    assert accumulate_work["candidate_score_elements"] == 15204352
    assert accumulate_work["candidate_value_read_bytes_estimate"] == 243269632
    assert accumulate_work["q_read_bytes_estimate"] == 67108864
    assert accumulate_work["output_write_bytes_estimate"] == 25165824
    assert accumulate_work["state_workspace_bytes"] == 16842752
    assert accumulate_work["score_workspace_bytes"] == 0
    assert accumulate_work["accumulate_kernel_launches"] == 8
    assert accumulate_work["query_chunk_count"] == 3
    assert accumulate_work["topk_chunk_count"] == 5
    assert accumulate_work["query_chunk_size_max"] == 128
    assert accumulate_work["topk_chunk_sizes"] == [320, 384]
    assert accumulate_work["counts_by_path"] == {"triton_chunked": 2}
    assert report["groups"][0]["accumulate_work"][
        "candidate_value_read_bytes_estimate"
    ] == 201326592
    mqa_topk = report["mqa_topk_work"]
    assert mqa_topk["query_tokens"] == 512
    assert mqa_topk["valid_kv_visits"] == 16_777_216
    assert mqa_topk["logits_elements"] == 16_777_216
    assert mqa_topk["logits_padding_elements"] == 0
    assert mqa_topk["logits_valid_ratio"] == 1.0
    assert mqa_topk["logits_padding_ratio"] == 0.0
    assert mqa_topk["kv_span_count"] == 512
    assert mqa_topk["kv_span_sum"] == 16_777_216
    assert mqa_topk["kv_span_mean"] == 32768.0
    assert mqa_topk["kv_span_max"] == 32768
    assert mqa_topk["materialized_logits_bytes"] == 67_108_864
    assert mqa_topk["peak_logits_bytes"] == 33_554_432
    assert mqa_topk["estimated_temp_bytes"] == 34_734_080
    assert mqa_topk["mqa_logits_launches"] == 2
    assert mqa_topk["counts_by_path"] == {"triton_full": 2}
    assert mqa_topk["elapsed_ms"] == 2.5
    assert mqa_topk["weight_sign"] == {
        "count": 1024,
        "positive": 600,
        "negative": 400,
        "zero": 24,
        "positive_ratio": 0.585938,
        "negative_ratio": 0.390625,
        "zero_ratio": 0.023438,
        "min": -3.5,
        "max": 4.0,
        "abs_max": 4.0,
    }
    assert report["groups"][0]["mqa_topk_work"]["valid_kv_visits"] == 8_388_608


def test_sparse_mla_stats_report_classifies_indexed_d512_gate_reasons(tmp_path):
    stats_path = tmp_path / "stats.jsonl"
    _write_jsonl(
        stats_path,
        [
            _stats_row(
                layer_type="mla_prefill_chunk",
                compress_ratio=4,
                num_prefills=2,
                query_tokens=32768,
                combined_topk=640,
                effective_candidate_visits=2_000_000,
                stage_timings_ms={"sparse_accumulate": 20.0},
            ),
            _stats_row(
                layer_type="mla_prefill_chunk",
                compress_ratio=1,
                num_prefills=1,
                query_tokens=32768,
                combined_topk=128,
                effective_candidate_visits=1_000_000,
                stage_timings_ms={"sparse_accumulate": 10.0},
            ),
            _stats_row(
                layer_type="mla_prefill_indexed_d512",
                compress_ratio=128,
                num_prefills=1,
                query_tokens=32768,
                combined_topk=256,
                effective_candidate_visits=500_000,
                stage_timings_ms={"sparse_accumulate": 1.0},
            ),
            _stats_row(
                layer_type="mla_prefill_chunk",
                compress_ratio=128,
                num_prefills=1,
                query_tokens=32768,
                combined_topk=256,
                effective_candidate_visits=250_000,
                stage_timings_ms={"sparse_accumulate": 5.0},
            ),
            _stats_row(
                layer_type="mla_prefill_chunk",
                compress_ratio=4,
                num_prefills=1,
                query_tokens=4096,
                combined_topk=640,
                effective_candidate_visits=125_000,
                stage_timings_ms={"sparse_accumulate": 2.0},
            ),
            _stats_row(
                layer_type="mla_prefill_chunk",
                compress_ratio=128,
                num_prefills=1,
                max_prefill_seq_len=4096,
                query_tokens=4096,
                combined_topk=256,
                effective_candidate_visits=64_000,
                stage_timings_ms={"sparse_accumulate": 1.0},
            ),
        ],
    )

    report = build_sparse_mla_stats_report(stats_path)

    gate = report["indexed_d512_gate"]
    assert gate["counts_by_status"] == {
        "already_indexed_d512": 1,
        "chunk_blocked": 3,
        "chunk_unexplained": 2,
    }
    assert gate["primary_reason_counts"] == {
        "num_prefills_not_1": 1,
        "prefill_seq_len_below_min": 1,
        "swa_only": 1,
        "unknown_or_env_disabled": 2,
    }
    reasons = {row["reason"]: row for row in gate["primary_reasons"]}
    assert reasons["num_prefills_not_1"]["row_count"] == 1
    assert reasons["num_prefills_not_1"]["effective_candidate_visits"] == 2_000_000
    assert reasons["num_prefills_not_1"]["sparse_accumulate_ms"] == 20.0
    assert (
        reasons["num_prefills_not_1"][
            "sparse_accumulate_ms_per_million_effective_visits"
        ]
        == 10.0
    )
    assert reasons["prefill_seq_len_below_min"]["row_count"] == 1
    assert reasons["unknown_or_env_disabled"]["row_count"] == 2
    assert reasons["unknown_or_env_disabled"]["effective_candidate_visits"] == 375_000
    group_by_ratio = {row["compress_ratio"]: row for row in report["groups"]}
    assert group_by_ratio["4"]["indexed_d512_gate"]["primary_reason"] == (
        "num_prefills_not_1"
    )


def test_sparse_mla_stats_report_skips_invalid_lines_and_unknown_kinds(tmp_path):
    stats_path = tmp_path / "stats.jsonl"
    stats_path.write_text(
        "\n".join(
            [
                json.dumps(_stats_row()),
                "{not json",
                json.dumps({"kind": "some_other_debug_record"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = build_sparse_mla_stats_report(stats_path)

    assert report["row_count"] == 1
    assert report["skipped_line_count"] == 2
    assert report["candidate_work"]["candidate_slots"] == 294912


def test_sparse_mla_stats_markdown_does_not_leak_absolute_paths(tmp_path):
    stats_path = tmp_path / "stats.jsonl"
    _write_jsonl(
        stats_path,
        [_stats_row(layer_prefix="/home/private/model.layers.3.self_attn")],
    )
    markdown_path = tmp_path / "stats.md"

    report = build_sparse_mla_stats_report(stats_path)
    write_sparse_mla_stats_markdown(markdown_path, report)

    text = markdown_path.read_text(encoding="utf-8")
    assert "# Sparse MLA Prefill Stats Report" in text
    assert "stats.jsonl" in text
    assert "## Candidate Overlap" in text
    assert "## Cross-Query Reuse Potential" in text
    assert "## Candidate Row Duplicates" in text
    assert "## Candidate Region Work" in text
    assert "## Indexed D512 Gate" in text
    assert "`num_prefills_not_1`" in text
    assert "## Sparse Accumulate Work" in text
    assert "- Accumulate paths: `triton_chunked`=1" in text
    assert "- Accumulate value-read bytes estimate: `201326592`" in text
    assert "## MQA Top-K Work" in text
    assert "- MQA top-k paths: `triton_full`=1" in text
    assert (
        "- MQA top-k logits padding elements / valid ratio / padding ratio: "
        "`0` / `1` / `0`"
    ) in text
    assert "- MQA top-k KV span count / mean / max: `256` / `32768` / `32768`" in text
    assert "- MQA top-k materialized logits bytes: `33554432`" in text
    assert "- MQA top-k elapsed ms: `1.25`" in text
    assert (
        "- MQA top-k weight signs positive / negative / zero: "
        "`300` / `200` / `12`"
    ) in text
    assert (
        "- MQA top-k weight sign ratios positive / negative / zero: "
        "`0.585938` / `0.390625` / `0.023438`"
    ) in text
    assert "| compressed | `32768` | `8192` | `24576` | `0.75` |" in text
    assert "| swa | `262144` | `188416` | `73728` | `0.28125` |" in text
    assert "| all | 2 |" in text
    assert "| swa | 2 | 12 | 8 | 4 | 0.333333 | 0.958333 |" in text
    assert "| compressed | 2 |" in text
    assert "/home/private" not in text
    assert "model.layers.3.self_attn" in text


def test_sparse_mla_stats_report_cli_writes_json_and_markdown(tmp_path):
    stats_path = tmp_path / "stats.jsonl"
    _write_jsonl(stats_path, [_stats_row()])
    json_output = tmp_path / "summary.json"
    markdown_output = tmp_path / "summary.md"

    rc = cli.main(
        [
            "sparse-mla-stats-report",
            "--stats-path",
            str(stats_path),
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    assert json.loads(json_output.read_text(encoding="utf-8"))["row_count"] == 1
    assert "# Sparse MLA Prefill Stats Report" in markdown_output.read_text(
        encoding="utf-8"
    )
