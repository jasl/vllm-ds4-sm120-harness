from ds4_harness.bench import parse_bench_output


def test_parse_bench_output_extracts_common_vllm_metrics():
    report = parse_bench_output(
        """
============ Serving Benchmark Result ============
Successful requests:                     48
Benchmark duration (s):                  98.12
Total input tokens:                      49152
Total generated tokens:                  49152
Request throughput (req/s):              0.49
Output token throughput (tok/s):         500.91
Total Token throughput (tok/s):          1001.82
Mean TPOT (ms):                          15.25
Mean ITL (ms):                           15.20
Mean TTFT (ms):                          1210.50
==================================================
"""
    )

    assert report["successful_requests"] == 48
    assert report["output_token_throughput_tok_s"] == 500.91
    assert report["mean_tpot_ms"] == 15.25
