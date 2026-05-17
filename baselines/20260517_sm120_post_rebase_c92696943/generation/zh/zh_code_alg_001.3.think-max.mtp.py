#!/usr/bin/env python3
"""
log_analyzer.py - Analyze access logs from stdin and output statistics as JSON.

Usage:
  python log_analyzer.py < logfile.txt     # output JSON stats
  python log_analyzer.py --test            # run built-in tests
"""

import sys
import json
import math
from collections import Counter, defaultdict


def parse_line(line):
    """Parse a single log line. Return a dict of fields or None if malformed."""
    raw = line.rstrip('\n')          # keep original line (without newline)
    stripped = raw.strip()
    if not stripped:
        return None
    parts = stripped.split()
    if len(parts) != 6:
        return None
    try:
        # fields are: timestamp method path status latency tenant
        timestamp = parts[0]
        method = parts[1]
        path_full = parts[2]
        status_code = int(parts[3])
        latency_str = parts[4]
        # latency must end with 'ms'
        if not latency_str.endswith('ms'):
            return None
        latency = int(latency_str[:-2])
        tenant_part = parts[5]
        if not tenant_part.startswith('tenant='):
            return None
        tenant = tenant_part[7:]
        # remove query string from path (everything after '?')
        path = path_full.split('?')[0]
    except (ValueError, IndexError):
        return None
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status_code,
        'latency': latency,
        'tenant': tenant,
        'raw': raw
    }


def compute_p95(latencies):
    """Compute the 95th percentile latency (integer)."""
    if not latencies:
        return 0
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    # index = ceil(n * 0.95) - 1  (1-based position -> 0-based index)
    idx = math.ceil(n * 0.95) - 1
    # clamp to valid range
    if idx < 0:
        idx = 0
    if idx >= n:
        idx = n - 1
    return sorted_lat[idx]


def analyze_logs(lines):
    """
    Process an iterable of log lines and return a statistics dictionary.
    """
    total_requests = 0
    malformed_lines = 0
    status_counts = Counter()
    path_counts = Counter()
    path_latencies = defaultdict(list)
    tenant_requests = Counter()
    tenant_errors = Counter()
    slow_requests = []

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue

        total_requests += 1
        status_counts[parsed['status']] += 1
        path = parsed['path']
        path_counts[path] += 1
        path_latencies[path].append(parsed['latency'])

        tenant = parsed['tenant']
        tenant_requests[tenant] += 1
        # 4xx or 5xx are considered errors
        if 400 <= parsed['status'] < 600:
            tenant_errors[tenant] += 1

        if parsed['latency'] > 1000:
            slow_requests.append({
                'raw_line': parsed['raw'],
                'path': path,
                'latency': parsed['latency']
            })

    # Top 5 paths by request count (tie-break by path name)
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # P95 latency per path
    p95_by_path = {path: compute_p95(lats) for path, lats in path_latencies.items()}

    # Slow requests: sort descending by latency, keep top 10
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_requests[:10]

    # Error rate per tenant
    tenant_error_rates = {}
    for tenant in tenant_requests:
        total = tenant_requests[tenant]
        errors = tenant_errors.get(tenant, 0)
        rate = round(errors / total, 3) if total > 0 else 0.0
        tenant_error_rates[tenant] = rate

    return {
        'total_requests': total_requests,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }


def run_tests():
    """Execute built-in tests."""
    # --- Test parse_line ---
    # Normal line
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed is not None
    assert parsed['timestamp'] == "2026-05-01T12:03:18Z"
    assert parsed['method'] == "GET"
    assert parsed['path'] == "/api/orders"
    assert parsed['status'] == 200
    assert parsed['latency'] == 123
    assert parsed['tenant'] == "a1"
    assert parsed['raw'] == line

    # Path with query parameters
    line2 = "2026-05-01T12:03:19Z POST /api/orders?page=2&sort=asc 201 456ms tenant=b2"
    parsed2 = parse_line(line2)
    assert parsed2 is not None
    assert parsed2['path'] == "/api/orders"
    assert parsed2['latency'] == 456
    assert parsed2['tenant'] == "b2"

    # Various malformed lines
    assert parse_line("") is None                     # empty
    assert parse_line("   ") is None                  # whitespace only
    assert parse_line("a b c 200 123abc tenant=x") is None   # wrong latency format
    assert parse_line("a b c 200 123ms no_tenant") is None    # last field not tenant=
    assert parse_line("a b c abc 123ms tenant=x") is None     # status not int

    # Trailing newline handling
    parsed_nl = parse_line(line + "\n")
    assert parsed_nl is not None
    assert parsed_nl['raw'] == line

    # --- Test compute_p95 ---
    assert compute_p95([]) == 0
    assert compute_p95([42]) == 42
    assert compute_p95([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 10
    assert compute_p95([1, 2, 3, 4, 5, 6, 7, 8, 9]) == 9
    assert compute_p95([5, 5, 5, 5, 5]) == 5

    # Random verification
    import random
    random.seed(42)
    for n in range(1, 101):
        lats = [random.randint(100, 500) for _ in range(n)]
        sorted_lats = sorted(lats)
        k = math.ceil(n * 0.95) - 1
        expected = sorted_lats[max(0, min(k, n - 1))]
        assert compute_p95(lats) == expected

    # --- Test analyze_logs ---
    # Empty input
    result = analyze_logs([])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 0
    assert result['status_counts'] == {}
    assert result['top_paths'] == []
    assert result['p95_latency_by_path'] == {}
    assert result['slow_requests'] == []
    assert result['tenant_error_rates'] == {}

    # All malformed
    result = analyze_logs(["bad1\n", "bad2\n"])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 2

    # Mixed valid and invalid lines
    test_lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2\n",
        "2026-05-01T12:03:20Z GET /api/users 404 50ms tenant=a1\n",
        "2026-05-01T12:03:21Z GET /api/orders 200 1500ms tenant=a1\n",
        "malformed line\n",
        "2026-05-01T12:03:22Z PUT /api/items 500 200ms tenant=c3\n",
        "2026-05-01T12:03:23Z DELETE /api/items 200 800ms tenant=b2\n",
        "\n",
    ]
    result = analyze_logs(test_lines)
    assert result['total_requests'] == 6
    assert result['malformed_lines'] == 2
    assert result['status_counts'] == {200: 3, 201: 1, 404: 1, 500: 1}
    assert len(result['top_paths']) == 3
    assert result['top_paths'][0] == {'path': '/api/orders', 'count': 3}
    assert result['top_paths'][1] == {'path': '/api/items', 'count': 2}
    assert result['top_paths'][2] == {'path': '/api/users', 'count': 1}
    assert result['p95_latency_by_path']['/api/orders'] == 1500
    assert result['p95_latency_by_path']['/api/items'] == 800
    assert result['p95_latency_by_path']['/api/users'] == 50
    assert len(result['slow_requests']) == 1
    slow = result['slow_requests'][0]
    assert slow['latency'] == 1500
    assert slow['path'] == '/api/orders'
    assert slow['raw_line'] == "2026-05-01T12:03:21Z GET /api/orders 200 1500ms tenant=a1"
    assert result['tenant_error_rates'] == {'a1': 0.333, 'b2': 0.0, 'c3': 1.0}

    # Less than 5 distinct paths
    result2 = analyze_logs([
        "2026-01-01T00:00:00Z GET /a 200 1ms tenant=t1\n",
        "2026-01-01T00:00:01Z GET /a 200 2ms tenant=t1\n",
    ])
    assert len(result2['top_paths']) == 1
    assert result2['top_paths'][0] == {'path': '/a', 'count': 2}

    # Slow request ordering and limit
    lines_slow = []
    for i in range(15):
        lines_slow.append(f"2026-01-01T00:00:0{i}Z GET /path 200 {1000 + i * 10}ms tenant=t{i%3}\n")
    result3 = analyze_logs(lines_slow)
    assert len(result3['slow_requests']) == 10
    # Latencies: 1140, 1130, ..., 1050 (first 10 of sorted 15)
    assert result3['slow_requests'][0]['latency'] == 1140
    assert result3['slow_requests'][-1]['latency'] == 1050

    # Boundary: latency exactly 1000 not included
    result4 = analyze_logs(["... GET /path 200 1000ms tenant=t\n"])
    assert len(result4['slow_requests']) == 0

    print("All tests passed.")


def main():
    if '--test' in sys.argv[1:]:
        run_tests()
        return
    # Normal operation: read stdin, produce JSON
    result = analyze_logs(sys.stdin)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
