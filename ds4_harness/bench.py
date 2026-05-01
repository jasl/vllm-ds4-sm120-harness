from __future__ import annotations

import re
import subprocess
from typing import Any


_METRIC_KEYS = {
    "Successful requests": "successful_requests",
    "Benchmark duration (s)": "benchmark_duration_s",
    "Total input tokens": "total_input_tokens",
    "Total generated tokens": "total_generated_tokens",
    "Request throughput (req/s)": "request_throughput_req_s",
    "Output token throughput (tok/s)": "output_token_throughput_tok_s",
    "Total Token throughput (tok/s)": "total_token_throughput_tok_s",
    "Mean TPOT (ms)": "mean_tpot_ms",
    "Mean ITL (ms)": "mean_itl_ms",
    "Mean TTFT (ms)": "mean_ttft_ms",
}


def _coerce_number(value: str) -> int | float:
    number = float(value.replace(",", ""))
    return int(number) if number.is_integer() else number


def parse_bench_output(output: str) -> dict[str, int | float]:
    report: dict[str, int | float] = {}
    for line in output.splitlines():
        match = re.match(r"^([^:]+):\s+([-+]?\d[\d,.]*)\s*$", line.strip())
        if not match:
            continue
        raw_key, raw_value = match.groups()
        key = _METRIC_KEYS.get(raw_key.strip())
        if key is not None:
            report[key] = _coerce_number(raw_value)
    return report


def run_bench_command(command: list[str], timeout: float | None = None) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        stdout = completed.stdout
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout_parts = []
        if exc.stdout:
            stdout_parts.append(
                exc.stdout.decode("utf-8", errors="replace")
                if isinstance(exc.stdout, bytes)
                else exc.stdout
            )
        if exc.stderr:
            stdout_parts.append(
                exc.stderr.decode("utf-8", errors="replace")
                if isinstance(exc.stderr, bytes)
                else exc.stderr
            )
        stdout_parts.append(f"\nTIMEOUT after {timeout} seconds\n")
        stdout = "".join(stdout_parts)
        returncode = -1
    except OSError as exc:
        stdout = f"{type(exc).__name__}: {exc}\n"
        returncode = -2
    return {
        "returncode": returncode,
        "metrics": parse_bench_output(stdout),
        "stdout": stdout,
        "command": command,
    }
