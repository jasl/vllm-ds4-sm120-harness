#!/usr/bin/env python3
# log_analyzer.py
import sys
import json
import math
import re
from collections import defaultdict, Counter

# ----------------------------------------------------------------------
# Log line parsing
# ----------------------------------------------------------------------
LOG_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+'
    r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+'
    r'(\S+)\s+'
    r'(\d{3})\s+'
    r'(\d+)ms\s+'
    r'(\S+)$'
)


def parse_line(line):
    """Parse a single log line.
    Returns a dict with keys: time, method, path_raw, status, latency, tenant
    or None if malformed.
    """
    line_stripped = line.rstrip('\n\r')
    m = LOG_PATTERN.match(line_stripped)
    if not m:
        return None
    timestamp = m.group(1)
    method = m.group(2)
    raw_path = m.group(3)
    status = int(m.group(4))
    latency = int(m.group(5))
    tenant = m.group(6)
    # Remove query parameters from path
    path_clean = raw_path.split('?')[0] if '?' in raw_path else raw_path
    return {
        "time": timestamp,
        "method": method,
        "path_raw": raw_path,
        "path_clean": path_clean,
        "status": status,
        "latency": latency,
        "tenant": tenant,
        "original": line_stripped,
    }


# ----------------------------------------------------------------------
# Statistics helpers
# ----------------------------------------------------------------------
def compute_p95(sorted_values):
    """Given a sorted list of numbers (ascending),
    return the P95 value as integer (ceil of the element at the computed index).
    P95 definition: 95% of values lie below this value.
    Index = ceil(0.95 * len) - 1  (0-based), then take value at that index.
    """
    if not sorted_values:
        return 0
    n = len(sorted_values)
    pos = math.ceil(0.95 * n) - 1
    pos = max(0, min(pos, n - 1))
    return sorted_values[pos]


def is_error_status(status):
    """4xx or 5xx considered error."""
    return 400 <= status <= 599


# ----------------------------------------------------------------------
# Main analysis
# ----------------------------------------------------------------------
def analyze(lines):
    """
    Takes an iterable of lines (strings).
    Returns a dict with the required JSON output.
    """
    total_requests = 0
    malformed_lines = 0
    status_counts = Counter()
    path_counter = Counter()
    # For p95_by_path: store list of latencies per clean path
    path_latencies = defaultdict(list)
    slow_requests = []
    # For tenant_error_rates: store total and error counts per tenant
    tenant_total = Counter()
    tenant_error = Counter()

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue

        total_requests += 1
        status_counts[parsed["status"]] += 1
        path_counter[parsed["path_clean"]] += 1
        path_latencies[parsed["path_clean"]].append(parsed["latency"])

        tenant_total[parsed["tenant"]] += 1
        if is_error_status(parsed["status"]):
            tenant_error[parsed["tenant"]] += 1

        # slow requests: latency > 1000 ms
        if parsed["latency"] > 1000:
            slow_requests.append({
                "original": parsed["original"],
                "path": parsed["path_clean"],
                "latency": parsed["latency"]
            })

    # Sort slow_requests by latency descending, take top 10
    slow_requests.sort(key=lambda x: x["latency"], reverse=True)
    slow_requests = slow_requests[:10]

    # Top 5 paths
    top_paths = [{"path": p, "count": c} for p, c in path_counter.most_common(5)]

    # P95 per path (sorted latencies)
    p95_by_path = {}
    for path, lat_list in path_latencies.items():
        sorted_lat = sorted(lat_list)
        p95_by_path[path] = compute_p95(sorted_lat)

    # Tenant error rates: error_count / total_count, 3 decimal places
    tenant_error_rates = {}
    for tenant in tenant_total:
        total = tenant_total[tenant]
        errors = tenant_error.get(tenant, 0)
        rate = round(errors / total, 3) if total > 0 else 0.0
        # ensure 3 decimals formatting but keep float type (OK for JSON)
        tenant_error_rates[tenant] = rate

    result = {
        "total_requests": total_requests,
        "malformed_lines": malformed_lines,
        "status_counts": dict(status_counts),
        "top_paths": top_paths,
        "p95_latency_by_path": p95_by_path,
        "slow_requests": slow_requests,
        "tenant_error_rates": tenant_error_rates
    }
    return result


# ----------------------------------------------------------------------
# Tests (run with --test)
# ----------------------------------------------------------------------
def run_tests():
    """Built-in tests for the analysis logic."""
    # Test parse_line
    good_line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n"
    parsed = parse_line(good_line)
    assert parsed is not None, "Good line should parse"
    assert parsed["time"] == "2026-05-01T12:03:18Z"
    assert parsed["method"] == "GET"
    assert parsed["path_raw"] == "/api/orders"
    assert parsed["path_clean"] == "/api/orders"
    assert parsed["status"] == 200
    assert parsed["latency"] == 123
    assert parsed["tenant"] == "tenant=a1"

    # Test with query parameter
    line2 = "2026-05-01T12:03:19Z POST /api/orders?page=2&size=10 201 456ms tenant=b2\n"
    parsed2 = parse_line(line2)
    assert parsed2 is not None
    assert parsed2["path_clean"] == "/api/orders"

    # Malformed line
    bad_line = "INVALID LINE\n"
    assert parse_line(bad_line) is None

    # Another bad line missing status
    bad_line2 = "2026-05-01T12:03:18Z GET /api/orders 200 tenant=a1\n"
    assert parse_line(bad_line2) is None

    # Test p95 computation
    # 1 element
    assert compute_p95([10]) == 10
    # 2 elements: ceil(0.95*2)=2 => pos=1 -> value 20
    assert compute_p95([10, 20]) == 20
    # 10 elements: index ceil(0.95*10)-1 = 9 -> value 100
    vals = list(range(1, 101))
    assert compute_p95(vals) == 95  # because 0-based: index = ceil(95) -1 = 95? Wait recalc

    # More careful: n=100, pos=ceil(0.95*100)-1 = 95-1=94? Actually ceil(95.0)=95, minus1 =94
    # sorted 0..99, index 94 -> value 95
    assert compute_p95(list(range(100))) == 94  # value at index 94 is 94 (0->0)

    # For n=100, list of 1..100 => sorted [1,2,...,100], index 94 -> value 95
    assert compute_p95(list(range(1, 101))) == 95

    # Test error status
    assert is_error_status(200) is False
    assert is_error_status(404) is True
    assert is_error_status(500) is True
    assert is_error_status(302) is False

    # Test full analysis
    test_lines = [
        "2026-05-01T12:00:00Z GET /api/users 200 50ms tenant=a1\n",
        "2026-05-01T12:00:01Z GET /api/orders 200 30ms tenant=b2\n",
        "2026-05-01T12:00:02Z POST /api/orders 201 200ms tenant=a1\n",
        "2026-05-01T12:00:03Z GET /api/users 500 300ms tenant=c3\n",
        "2026-05-01T12:00:04Z GET /api/orders?page=1 404 150ms tenant=a1\n",
        "MALFORMED LINE\n",
        "2026-05-01T12:00:05Z DELETE /api/items 200 1200ms tenant=b2\n",
    ]
    result = analyze(test_lines)
    assert result["total_requests"] == 6
    assert result["malformed_lines"] == 1
    assert result["status_counts"][200] == 3
    assert result["status_counts"][201] == 1
    assert result["status_counts"][500] == 1
    assert result["status_counts"][404] == 1

    # top_paths: /api/users (2), /api/orders (2), /api/items (1) but top 5 includes all
    top_paths = result["top_paths"]
    path_counts = {p['path']: p['count'] for p in top_paths}
    assert path_counts["/api/users"] == 2
    assert path_counts["/api/orders"] == 2
    assert path_counts["/api/items"] == 1

    # p95: for /api/orders: latencies [30,200,150] sorted [30,150,200] -> index ceil(0.95*3)-1 = ceil(2.85)-1=3-1=2 -> value 200
    assert result["p95_latency_by_path"]["/api/orders"] == 200
    # /api/users: [50,300] -> sorted [50,300] -> index ceil(0.95*2)-1=2-1=1 -> 300
    assert result["p95_latency_by_path"]["/api/users"] == 300

    # slow_requests: latency>1000: only delete 1200ms -> 1 item
    assert len(result["slow_requests"]) == 1
    assert result["slow_requests"][0]["latency"] == 1200

    # tenant_error_rates: a1: errors=404 ->1, total=3 => 0.333; b2: errors=0 =>0.0; c3: errors=500->1, total=1 =>1.0
    rates = result["tenant_error_rates"]
    assert rates["tenant=a1"] == 1/3  # 0.333333 -> round to 0.333
    assert rates["tenant=a1"] == 0.333
    assert rates["tenant=b2"] == 0.0
    assert rates["tenant=c3"] == 1.0

    # Output format check: make sure it can be serialized to JSON
    json.dumps(result)

    print("All tests passed.")


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    # Read all lines from stdin
    lines = sys.stdin.readlines()
    result = analyze(lines)
    # Output JSON, no extra text
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
