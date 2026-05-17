#!/usr/bin/env python3
"""
Log Analyzer
Reads multi-line access logs from stdin, computes statistics,
and outputs a JSON object.

Usage:
    python log_analyzer.py < input.log          # normal run
    python log_analyzer.py --test               # run built-in tests
"""

import re
import sys
import json
import math

# ----------------------------------------------------------------------
# Log line pattern
# Format: ISOtimestamp METHOD path status latency_ms tenant=value
# Example: 2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1
LINE_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) '
    r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) '
    r'(\S+) '
    r'(\d{3}) '
    r'(\d+)ms '
    r'tenant=(\S+)$'
)


def parse_line(line: str):
    """
    Parse a single log line.

    Args:
        line: the log line (without trailing newline)

    Returns:
        A dictionary with keys: timestamp, method, path, status,
        latency, tenant, original_line.
        If the line cannot be parsed, returns None.
    """
    match = LINE_PATTERN.match(line)
    if not match:
        return None
    timestamp, method, path, status_str, latency_str, tenant = match.groups()

    # Remove query parameters from the path
    path = path.split('?')[0]

    status = int(status_str)
    latency = int(latency_str)

    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status,
        'latency': latency,
        'tenant': tenant,
        'original_line': line,
    }


def process_input(lines):
    """
    Process an iterable of lines (each optionally ending with newline)
    and produce the required statistics.

    Returns:
        A dictionary suitable for JSON serialization.
    """
    parsed_entries = []
    malformed_count = 0

    for raw_line in lines:
        # Remove trailing newline / carriage return characters
        line = raw_line.rstrip('\r\n')
        # Skip completely empty lines (do not count as malformed)
        if not line:
            continue

        entry = parse_line(line)
        if entry is None:
            malformed_count += 1
        else:
            parsed_entries.append(entry)

    total_requests = len(parsed_entries)

    # Collectors
    status_counts = {}                # status_code -> count
    path_counts = {}                  # path -> count
    latencies_by_path = {}            # path -> list of latencies
    tenant_stats = {}                 # tenant -> {'total': , 'errors': }
    slow_candidates = []              # entries with latency > 1000 ms

    for entry in parsed_entries:
        path = entry['path']
        status = entry['status']
        latency = entry['latency']
        tenant = entry['tenant']

        # Status counts (store as string for JSON)
        status_key = str(status)
        status_counts[status_key] = status_counts.get(status_key, 0) + 1

        # Path counts
        path_counts[path] = path_counts.get(path, 0) + 1

        # Latencies per path
        latencies_by_path.setdefault(path, []).append(latency)

        # Tenant statistics
        if tenant not in tenant_stats:
            tenant_stats[tenant] = {'total': 0, 'errors': 0}
        tenant_stats[tenant]['total'] += 1
        if status >= 400:   # 4xx or 5xx
            tenant_stats[tenant]['errors'] += 1

        # Slow requests (latency > 1000 ms)
        if latency > 1000:
            slow_candidates.append({
                'original_line': entry['original_line'],
                'path': path,
                'latency': latency,
            })

    # Slow requests: sort descending by latency, keep top 10
    slow_candidates.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_candidates[:10]

    # Top 5 paths: primary by count descending, secondary by path alphabetically
    sorted_paths = sorted(path_counts.items(),
                          key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # P95 latency per path
    p95_latency_by_path = {}
    for path, lat_list in latencies_by_path.items():
        lat_list.sort()
        n = len(lat_list)
        pos = math.ceil(0.95 * n)    # 1‑based index of the P95 value
        p95_latency_by_path[path] = lat_list[pos - 1]

    # Tenant error rates (rounded to three decimal places)
    tenant_error_rates = {}
    for tenant, st in tenant_stats.items():
        total = st['total']
        errors = st['errors']
        rate = errors / total if total > 0 else 0.0
        tenant_error_rates[tenant] = round(rate, 3)

    # Compose output dictionary with stable order
    output = {
        'total_requests': total_requests,
        'status_counts': dict(sorted(status_counts.items(),
                                     key=lambda x: int(x[0]))),
        'top_paths': top_paths,
        'p95_latency_by_path': dict(sorted(p95_latency_by_path.items())),
        'slow_requests': slow_requests,
        'tenant_error_rates': dict(sorted(tenant_error_rates.items())),
        'malformed_lines': malformed_count,
    }
    return output


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_parse_line():
    """Exercise parse_line with valid and invalid inputs."""
    # Valid line
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    res = parse_line(line)
    assert res is not None
    assert res['path'] == '/api/orders'
    assert res['method'] == 'GET'
    assert res['status'] == 200
    assert res['latency'] == 123
    assert res['tenant'] == 'a1'
    assert res['original_line'] == line

    # Path with query parameters
    line2 = "2026-05-01T12:03:18Z POST /api/orders?page=2 201 456ms tenant=abc"
    res2 = parse_line(line2)
    assert res2 is not None
    assert res2['path'] == '/api/orders'
    assert res2['method'] == 'POST'
    assert res2['latency'] == 456
    assert res2['tenant'] == 'abc'

    # Different HTTP method
    line3 = "2026-05-01T12:03:18Z PUT /api/item 202 789ms tenant=t1"
    assert parse_line(line3) is not None

    # Malformed lines (should return None)
    assert parse_line("") is None
    assert parse_line("   ") is None
    assert parse_line("invalid line") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 abcms tenant=a1") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 2000 123ms tenant=a1") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 20 123ms tenant=a1") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1 extra") is None
    print("test_parse_line passed")


def test_p95():
    """Verify the P95 calculation logic (ceil)."""
    assert math.ceil(0.95 * 10) == 10
    assert math.ceil(0.95 * 1) == 1
    assert math.ceil(0.95 * 2) == 2
    assert math.ceil(0.95 * 3) == 3
    assert math.ceil(0.95 * 11) == 11
    assert math.ceil(0.95 * 20) == 19
    print("test_p95 passed")


def test_process():
    """Full end-to-end test of process_input."""
    lines = [
        "2026-05-01T12:00:00Z GET /api/orders 200 100ms tenant=a1",
        "2026-05-01T12:00:01Z GET /api/users 200 200ms tenant=a1",
        "2026-05-01T12:00:02Z POST /api/orders 201 50ms tenant=b2",
        "2026-05-01T12:00:03Z GET /api/orders 500 2000ms tenant=a1",
        "2026-05-01T12:00:04Z GET /api/orders 404 150ms tenant=c3",
        "2026-05-01T12:00:05Z GET /api/somepath 200 5000ms tenant=b2",
        "malformed line",
        "2026-05-01T12:00:06Z GET /api/orders 200 120ms tenant=a1",
        "2026-05-01T12:00:07Z GET /api/orders 200 130ms tenant=a1",
        "2026-05-01T12:00:08Z GET /api/orders 200 140ms tenant=a1",
        "2026-05-01T12:00:09Z GET /api/users 200 300ms tenant=a1",
        "2026-05-01T12:00:10Z GET /api/users 200 310ms tenant=a1",
        "2026-05-01T12:00:11Z GET /api/orders 200 1000ms tenant=b2",
        "2026-05-01T12:00:12Z GET /api/items 200 500ms tenant=c3",
        "2026-05-01T12:00:13Z GET /api/items 200 600ms tenant=c3",
        "2026-05-01T12:00:14Z POST /api/login 401 100ms tenant=c3",
        "2026-05-01T12:00:15Z POST /api/login 500 200ms tenant=c3",
        "2026-05-01T12:00:16Z GET /api/slow 200 1500ms tenant=b2",
    ]
    result = process_input(lines)

    # Basic counts
    assert result['total_requests'] == 17
    assert result['malformed_lines'] == 1

    # Status counts
    sc = result['status_counts']
    assert sc['200'] == 12
    assert sc['201'] == 1
    assert sc['500'] == 2
    assert sc['404'] == 1
    assert sc['401'] == 1

    # Top 5 paths
    top = result['top_paths']
    assert len(top) == 5
    expected_top = [
        {'path': '/api/orders', 'count': 8},
        {'path': '/api/users', 'count': 3},
        {'path': '/api/items', 'count': 2},
        {'path': '/api/login', 'count': 2},
        {'path': '/api/slow', 'count': 1},
    ]
    for i, (exp, act) in enumerate(zip(expected_top, top)):
        assert exp == act, f"top_paths[{i}] mismatch: {exp} != {act}"

    # Slow requests
    slow = result['slow_requests']
    assert len(slow) == 3
    assert slow[0]['latency'] == 5000 and slow[0]['path'] == '/api/somepath'
    assert slow[1]['latency'] == 2000 and slow[1]['path'] == '/api/orders'
    assert slow[2]['latency'] == 1500 and slow[2]['path'] == '/api/slow'
    assert slow[0]['original_line'] == lines[5]
    assert slow[1]['original_line'] == lines[3]
    assert slow[2]['original_line'] == lines[17]

    # P95 latencies
    p95 = result['p95_latency_by_path']
    assert p95['/api/orders'] == 2000
    assert p95['/api/users'] == 310
    assert p95['/api/items'] == 600
    assert p95['/api/login'] == 200
    assert p95['/api/somepath'] == 5000
    assert p95['/api/slow'] == 1500

    # Tenant error rates
    rates = result['tenant_error_rates']
    assert rates['a1'] == 0.125
    assert rates['b2'] == 0.0
    assert rates['c3'] == 0.6

    print("test_process passed")


def test_all():
    """Run all test suites."""
    test_parse_line()
    test_p95()
    test_process()
    print("All tests passed.")


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------

def main():
    if '--test' in sys.argv:
        test_all()
        return

    # Read all lines from standard input
    lines = sys.stdin.readlines()
    result = process_input(lines)

    # Output JSON (compact, but with a trailing newline)
    json_output = json.dumps(result, ensure_ascii=False)
    sys.stdout.write(json_output + '\n')


if __name__ == '__main__':
    main()
