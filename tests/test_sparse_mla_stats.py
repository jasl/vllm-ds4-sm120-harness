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
    assert "## Candidate Region Work" in text
    assert "| compressed | `32768` | `8192` | `24576` | `0.75` |" in text
    assert "| swa | `262144` | `188416` | `73728` | `0.28125` |" in text
    assert "| all | 2 |" in text
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
