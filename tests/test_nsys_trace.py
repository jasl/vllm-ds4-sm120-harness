import json

from ds4_harness.nsys_trace import (
    build_nsys_cuda_trace_report,
    classify_cuda_gpu_trace_name,
    write_nsys_cuda_trace_report_markdown,
)


def test_classify_cuda_gpu_trace_name_groups_sm12x_kernels():
    assert (
        classify_cuda_gpu_trace_name(
            "void _accumulate_indexed_attention_chunk_multihead_kernel<...>"
        )
        == "sparse_mla_chunk"
    )
    assert (
        classify_cuda_gpu_trace_name(
            "void _accumulate_indexed_attention_partial_states_multihead_kernel<...>"
        )
        == "sparse_mla_partial"
    )
    assert classify_cuda_gpu_trace_name("void _fp8_mqa_logits_kernel<...>") == (
        "fp8_mqa_logits"
    )
    assert classify_cuda_gpu_trace_name("void _combine_topk_swa_indices_kernel") == (
        "combine_topk_swa"
    )
    assert classify_cuda_gpu_trace_name("[CUDA memcpy Host-to-Device]") == (
        "cuda_memcpy"
    )


def test_nsys_cuda_trace_report_finds_decode_gap_dominant_work(tmp_path):
    trace_csv = tmp_path / "cuda_gpu_trace.csv"
    trace_csv.write_text(
        "\n".join(
            [
                (
                    "Start (ns),Duration (ns),CorrId,GrdX,GrdY,GrdZ,BlkX,BlkY,"
                    "BlkZ,Reg/Trd,StcSMem (MB),DymSMem (MB),Bytes (MB),"
                    "Throughput (MB/s),SrcMemKd,DstMemKd,Device,Ctx,GreenCtx,"
                    "Strm,Name"
                ),
                "1000,100,1,,,,,,,,,,,,,,GPU0,1,,7,void _fp8_mqa_logits_kernel",
                (
                    "2000,500000000,2,,,,,,,,,,,,,,GPU0,1,,7,"
                    "void _accumulate_indexed_attention_partial_states_multihead_kernel"
                ),
                (
                    "500002000,200000000,3,,,,,,,,,,,,,,GPU0,1,,7,"
                    "void _accumulate_indexed_attention_partial_states_multihead_kernel"
                ),
                "900000000,100,4,,,,,,,,,,,,,,GPU0,1,,7,void _fp8_mqa_logits_kernel",
                "900001000,100,5,,,,,,,,,,,,,,GPU0,1,,7,[CUDA memcpy Host-to-Device]",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    mixed_json = tmp_path / "mixed.json"
    mixed_json.write_text(
        json.dumps(
            {
                "case": "mixed",
                "variant": "mtp",
                "requests": [
                    {
                        "arrival_case": "long_then_short",
                        "request_role": "secondary",
                        "decode_tokens_per_second": 2.5,
                        "p99_inter_chunk_seconds": 25.0,
                    },
                    {
                        "arrival_case": "long_then_short",
                        "request_role": "primary",
                        "decode_tokens_per_second": 80.0,
                        "p99_inter_chunk_seconds": 0.1,
                    },
                ],
                "summary": [{"case": "long_then_short"}],
            }
        ),
        encoding="utf-8",
    )

    report = build_nsys_cuda_trace_report(trace_csv, mixed_arrival_json=mixed_json)

    assert report["row_count"] == 5
    assert report["decode_kernel_gaps"]["decode_kernel_count"] == 2
    assert report["decode_kernel_gaps"]["max_start_gap_seconds"] == 0.899999
    top_gap = report["decode_kernel_gaps"]["top_gaps"][0]
    assert top_gap["duration_by_class"][0]["class"] == "sparse_mla_partial"
    assert report["mixed_arrival"]["slowest_decode_request"] == {
        "arrival_case": "long_then_short",
        "request_role": "secondary",
        "decode_tokens_per_second": 2.5,
        "p99_inter_chunk_seconds": 25.0,
        "max_inter_chunk_seconds": None,
    }
    assert report["slow_request_gap_interpretation"]["classification"] == (
        "per_request_starvation_while_global_decode_continues"
    )


def test_nsys_cuda_trace_markdown_is_path_safe(tmp_path):
    trace_csv = tmp_path / "cuda_gpu_trace.csv"
    trace_csv.write_text(
        "\n".join(
            [
                "Start (ns),Duration (ns),Name",
                "1000,100,void _fp8_mqa_logits_kernel",
                (
                    "2000,500,"
                    "void _accumulate_indexed_attention_chunk_multihead_kernel"
                ),
                "3000,100,void _fp8_mqa_logits_kernel",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    markdown = tmp_path / "summary.md"

    report = build_nsys_cuda_trace_report(trace_csv)
    write_nsys_cuda_trace_report_markdown(markdown, report)

    text = markdown.read_text(encoding="utf-8")
    assert "# Nsys CUDA Trace Timeline Summary" in text
    assert "Slow-request gap interpretation" in text
    assert "cuda_gpu_trace.csv" in text
    assert str(tmp_path) not in text
