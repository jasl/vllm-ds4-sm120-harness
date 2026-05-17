#!/usr/bin/env python3
"""
log_analyzer.py - Analyze access logs and produce JSON statistics.

Usage:
    python log_analyzer.py < access.log
    python log_analyzer.py --test
"""

import sys
import json
import math
from collections import defaultdict, Counter


# ------------------------------------------------------------
# Parsing
# ------------------------------------------------------------

def parse_line(line):
    """Parse a single log line.

    Returns a tuple (timestamp, method, path, status, latency, tenant)
    if the line is valid, otherwise None.
    """
    if not line.strip():
        return None
    parts = line.split()
    if len(parts) != 6:
        return None

    timestamp, method, path, status_str, latency_str, tenant_raw = parts

    # Validate timestamp: ISO 8601 with trailing Z, length 20
    if len(timestamp) != 20:
        return None
    if (timestamp[4] != '-' or timestamp[7] != '-' or timestamp[10] != 'T' or
            timestamp[13] != ':' or timestamp[16] != ':' or timestamp[19] != 'Z'):
        return None
    # Verify digits at correct positions
    if not (timestamp[:4].isdigit() and timestamp[5:7].isdigit() and
            timestamp[8:10].isdigit() and timestamp[11:13].isdigit() and
            timestamp[14:16].isdigit() and timestamp[17:19].isdigit()):
        return None

    # Method: must be all uppercase alphabetic
    if not method.isalpha() or not method.isupper():
        return None

    # Path: must start with '/'
    if not path.startswith('/'):
        return None

    # Status code: three‑digit integer
    if not (status_str.isdigit() and len(status_str) == 3):
        return None
    status = int(status_str)

    # Latency: digits followed by 'ms'
    if not latency_str.endswith('ms'):
        return None
    lat_digits = latency_str[:-2]
    if not lat_digits.isdigit():
        return None
    latency = int(lat_digits)

    # Tenant: must contain '=' and have a non‑empty value
    if '=' not in tenant_raw:
        return None
    _, tenant_val = tenant_raw.split('=', 1)
    if not tenant_val:
        return None

    # Clean path: strip query parameters
    path_clean = path.split('?')[0]

    return (timestamp, method, path_clean, status, latency, tenant_val)


# ------------------------------------------------------------
# Percentile calculation
# ------------------------------------------------------------

def compute_p95(latencies):
    """Compute the 95th percentile of a list of latencies.

    The percentile is taken as the value at the ceiling(0.95 * N) position
    (1‑indexed) after sorting.
    """
    if not latencies:
        return 0
    sorted_lats = sorted(latencies)
    n = len(sorted_lats)
    # 0‑based index for the ceil(0.95 * n)‑th element (1‑indexed)
    pos = math.ceil(0.95 * n) - 1
    if pos < 0:
        pos = 0
    return sorted_lats[pos]


# ------------------------------------------------------------
# Core processing
# ------------------------------------------------------------

def process_data(lines):
    """Process an iterable of log lines (without trailing newlines) and
    return a dictionary containing all required statistics.
    """
    total_requests = 0
    malformed_lines = 0
    status_counts = Counter()
    path_counts = Counter()
    path_latencies = defaultdict(list)
    slow_requests = []
    tenant_total = Counter()
    tenant_error = Counter()

    for line in lines:
        # Skip completely empty lines
        if not line.strip():
            continue

        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue

        total_requests += 1
        _, _, path, status, latency, tenant = parsed

        status_counts[str(status)] += 1
        path_counts[path] += 1
        path_latencies[path].append(latency)

        if latency > 1000:
            slow_requests.append({
                'line': line,
                'path': path,
                'latency': latency
            })

        tenant_total[tenant] += 1
        if status >= 400:          # 4xx and 5xx are errors
            tenant_error[tenant] += 1

    # Top 5 paths
    top_paths = [
        {'path': p, 'count': c}
        for p, c in path_counts.most_common(5)
    ]

    # P95 latency per path
    p95_by_path = {
        path: compute_p95(lats)
        for path, lats in path_latencies.items()
    }

    # Slow requests: latency > 1000ms, top 10 by latency descending
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests_top10 = slow_requests[:10]

    # Tenant error rates (rounded to three decimal places)
    tenant_error_rates = {}
    for tenant in tenant_total:
        total = tenant_total[tenant]
        err = tenant_error.get(tenant, 0)
        rate = round(err / total, 3) if total else 0.0
        tenant_error_rates[tenant] = rate

    return {
        'total_requests': total_requests,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests_top10,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------

def test_parse_line():
    """Unit tests for parse_line."""
    # Valid full line
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed is not None
    ts, method, path, status, latency, tenant = parsed
    assert ts == "2026-05-01T12:03:18Z"
    assert method == "GET"
    assert path == "/api/orders"
    assert status == 200
    assert latency == 123
    assert tenant == "a1"

    # Line with query parameters (should be stripped)
    line2 = "2026-05-01T12:03:18Z POST /api/orders?page=2&foo=bar 201 200ms tenant=a1"
    parsed2 = parse_line(line2)
    assert parsed2 is not None
    assert parsed2[2] == "/api/orders"
    assert parsed2[3] == 201
    assert parsed2[4] == 200

    # Malformed lines
    assert parse_line("") is None                           # empty
    assert parse_line("garbage line") is None               # junk
    # missing tenant
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=") is None  # empty tenant
    # extra field
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms extra tenant=a1") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 2000 123ms tenant=a1") is None   # 4‑digit status
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123msx tenant=a1") is None   # bad latency
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders abc 123ms tenant=a1") is None    # non‑digit status
    # method must be uppercase
    assert parse_line("2026-05-01T12:03:18Z get /api/orders 200 123ms tenant=a1") is None

    print("test_parse_line OK")


def test_p95():
    """Unit tests for compute_p95."""
    assert compute_p95([10, 20, 30]) == 30          # ceil(0.95*3)=3 --> index 2
    assert compute_p95([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 10   # ceil(9.5)=10
    assert compute_p95([100, 200]) == 200           # ceil(1.9)=2
    assert compute_p95([50]) == 50
    assert compute_p95([]) == 0                     # edge case
    print("test_p95 OK")


def test_integration():
    """Integration test with sample data."""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
        "2026-05-01T12:03:19Z GET /api/users 404 50ms tenant=a2",
        "2026-05-01T12:03:20Z POST /api/orders 500 200ms tenant=a1",
        "2026-05-01T12:03:21Z GET /api/orders?page=2 200 150ms tenant=a1",
        "2026-05-01T12:03:22Z GET /api/orders 200 1300ms tenant=a2",
    ]
    result = process_data(lines)

    # Basic counts
    assert result['total_requests'] == 5
    assert result['status_counts'] == {"200": 3, "404": 1, "500": 1}
    assert result['malformed_lines'] == 0

    # Top paths
    assert len(result['top_paths']) == 2
    assert result['top_paths'][0] == {'path': '/api/orders', 'count': 4}
    assert result['top_paths'][1] == {'path': '/api/users', 'count': 1}

    # P95 latency
    assert result['p95_latency_by_path'] == {'/api/orders': 1300, '/api/users': 50}

    # Slow requests
    assert len(result['slow_requests']) == 1
    slow = result['slow_requests'][0]
    assert slow['latency'] == 1300
    assert slow['path'] == '/api/orders'
    assert slow['line'] == "2026-05-01T12:03:22Z GET /api/orders 200 1300ms tenant=a2"

    # Tenant error rates
    assert abs(result['tenant_error_rates']['a1'] - 0.333) < 0.001
    assert abs(result['tenant_error_rates']['a2'] - 0.5) < 0.001

    # Test with malformed and empty lines
    lines2 = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
        "invalid line",
        "2026-05-01T12:03:19Z GET /api/test 200 123ms tenant=a1",
        "",            # empty line – skipped
    ]
    result2 = process_data(lines2)
    assert result2['total_requests'] == 2
    assert result2['malformed_lines'] == 1   # only "invalid line"

    print("test_integration OK")


def test():
    """Run all tests."""
    test_parse_line()
    test_p95()
    test_integration()
    print("All tests passed.")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test()
        return

    # Read lines from stdin, removing trailing newline characters
    lines = (line.rstrip('\r\n') for line in sys.stdin)
    result = process_data(lines)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
