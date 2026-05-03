import json

from ds4_harness import cli
from ds4_harness.attention_dump import (
    build_attention_dump_report,
    write_attention_dump_markdown,
)


def _write_dump(path, **overrides):
    data = {
        "kind": "deepseek_v4_sparse_mla_compressed_decode_dump",
        "tensor_file": path.with_suffix(".pt").name,
        "prefix": "model.layers.2.attn",
        "layer_id": 2,
        "branch": "matmul",
        "step": 3,
        "tensor_model_parallel_rank": 0,
        "tensor_model_parallel_world_size": 2,
        "compress_ratio": 4,
        "num_heads": 32,
        "compressed_topk": 512,
        "max_swa_len": 128,
        "max_abs_diff": 0.015625,
        "mean_abs_diff": 0.00042,
    }
    data.update(overrides)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_attention_dump_report_summarizes_worst_diffs(tmp_path):
    dump_dir = tmp_path / "dumps"
    dump_dir.mkdir()
    _write_dump(dump_dir / "rank0.json")
    _write_dump(
        dump_dir / "rank1.json",
        layer_id=3,
        prefix="model.layers.3.attn",
        branch="direct",
        step=4,
        tensor_model_parallel_rank=1,
        compress_ratio=128,
        max_abs_diff=0.25,
        mean_abs_diff=0.01,
    )

    report = build_attention_dump_report(dump_dir)

    assert report["dump_count"] == 2
    assert report["counts_by_branch"] == {"direct": 1, "matmul": 1}
    assert report["counts_by_compress_ratio"] == {"4": 1, "128": 1}
    assert report["max_abs_diff"] == 0.25
    assert report["dump_dir"] == "dumps"
    assert report["worst_dumps"][0]["file"] == "rank1.json"
    assert report["worst_dumps"][0]["tensor_file"] == "rank1.pt"


def test_attention_dump_markdown_keeps_raw_tensor_files_out_of_report(tmp_path):
    dump_dir = tmp_path / "dumps"
    dump_dir.mkdir()
    _write_dump(dump_dir / "rank0.json")
    markdown_path = tmp_path / "report.md"

    report = build_attention_dump_report(dump_dir)
    write_attention_dump_markdown(markdown_path, report)

    text = markdown_path.read_text(encoding="utf-8")
    assert "# Sparse MLA Dump Report" in text
    assert "| `rank0.json` | `rank0.pt` |" in text
    assert "Raw tensor files are referenced by name only" in text


def test_attention_dump_report_strips_tensor_file_paths(tmp_path):
    dump_dir = tmp_path / "dumps"
    dump_dir.mkdir()
    _write_dump(dump_dir / "rank0.json", tensor_file="/remote/private/rank0.pt")

    report = build_attention_dump_report(dump_dir)

    assert report["worst_dumps"][0]["tensor_file"] == "rank0.pt"


def test_sparse_mla_dump_report_cli_writes_json_and_markdown(tmp_path):
    dump_dir = tmp_path / "dumps"
    dump_dir.mkdir()
    _write_dump(dump_dir / "rank0.json")
    json_output = tmp_path / "summary.json"
    markdown_output = tmp_path / "summary.md"

    rc = cli.main(
        [
            "sparse-mla-dump-report",
            "--dump-dir",
            str(dump_dir),
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert rc == 0
    assert json.loads(json_output.read_text(encoding="utf-8"))["dump_count"] == 1
    assert "# Sparse MLA Dump Report" in markdown_output.read_text(encoding="utf-8")
