#!/usr/bin/env python3
import sys
import json
from collections import defaultdict

def parse_line(raw_line):
    """Parse a single log line.  Return a dict with fields or None if malformed."""
    stripped = raw_line.strip()
    if not stripped:                     # empty line
        return None

    parts = stripped.split()
    if len(parts) != 6:                  # wrong number of columns
        return None

    timestamp, method, raw_path, status_str, duration_str, tenant_field = parts

    # status code must be integer
    try:
        status = int(status_str)
    except ValueError:
        return None

    # duration must end with "ms"
    if not duration_str.endswith('ms'):
        return None
    try:
        duration = int(duration_str[:-2])
    except ValueError:
        return None

    # tenant must be of the form "tenant=..."
    if not tenant_field.startswith('tenant='):
        return None
    tenant = tenant_field.split('=', 1)[1]

    # remove query parameters and fragment from the path
    path = raw_path.split('?', 1)[0].split('#', 1)[0]

    return {
        'timestamp': timestamp,
        'method': method,
        'raw_path': raw_path,
        'path': path,
        'status': status,
        'duration': duration,
        'tenant': tenant,
        'original_line': raw_line
    }


def compute_stats(lines):
    """Read log lines (iterable) and compute the required statistics.

    Returns a dictionary with all the fields required by the problem.
    """
    total = 0
    malformed = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    tenant_total = defaultdict(int)
    tenant_errors = defaultdict(int)
    slow_data = []                     # (duration, original_line, path)

    for line in lines:
        raw_line = line.rstrip('\n')
        parsed = parse_line(raw_line)
        if parsed is None:
            malformed += 1
            continue

        total += 1

        # status
        status_counts[str(parsed['status'])] += 1

        # path (without query/fragment)
        path = parsed['path']
        path_counts[path] += 1
        path_latencies[path].append(parsed['duration'])

        # tenant
        tenant = parsed['tenant']
        tenant_total[tenant] += 1
        if 400 <= parsed['status'] <= 599:       # 4xx or 5xx -> error
            tenant_errors[tenant] += 1

        # slow requests (duration > 1000ms)
        if parsed['duration'] > 1000:
            slow_data.append((parsed['duration'], parsed['original_line'], parsed['path']))

    # 1) Top 5 paths
    sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths]

    # 2) P95 latency per path (integer milliseconds)
    p95_by_path = {}
    for path, latencies in path_latencies.items():
        if not latencies:
            continue
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        # index = ceil(0.95 * n) - 1  (0‑based) with integer arithmetic
        idx = (95 * n + 99) // 100 - 1
        p95_by_path[path] = sorted_lat[idx]

    # 3) Top 10 slow requests
    slow_data.sort(key=lambda x: x[0], reverse=True)
    slow_requests = []
    for dur, line, path in slow_data[:10]:
        slow_requests.append({
            'original_line': line,
            'path': path,
            'duration': dur
        })

    # 4) Error rate per tenant
    error_rates = {}
    for tenant, tot in tenant_total.items():
        err = tenant_errors.get(tenant, 0)
        rate = err / tot if tot > 0 else 0.0
        error_rates[tenant] = round(rate, 3)

    result = {
        'total_requests': total,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': error_rates,
        'malformed_lines': malformed
    }
    return result


def test():
    """Built‑in tests.  Run with --test ."""
    # ------------------------------------------------------------------
    # Test 1 : basic correct input
    lines1 = [
        '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=b2',
    ]
    res1 = compute_stats(lines1)
    assert res1['total_requests'] == 2
    assert res1['status_counts'] == {'200': 1, '201': 1}
    assert len(res1['top_paths']) == 2
    assert res1['top_paths'][0] == {'path': '/api/orders', 'count': 1}
    assert res1['top_paths'][1] == {'path': '/api/users', 'count': 1}
    assert res1['p95_latency_by_path'] == {'/api/orders': 123, '/api/users': 456}
    assert res1['slow_requests'] == []
    assert res1['tenant_error_rates'] == {'a1': 0.0, 'b2': 0.0}
    assert res1['malformed_lines'] == 0

    # ------------------------------------------------------------------
    # Test 2 : query parameters removal
    lines2 = [
        '2026-05-01T12:03:18Z GET /api/orders?page=2&sort=asc 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=a1',
    ]
    res2 = compute_stats(lines2)
    assert res2['total_requests'] == 2
    assert res2['p95_latency_by_path'] == {'/api/orders': 123, '/api/users': 456}
    assert res2['malformed_lines'] == 0

    # ------------------------------------------------------------------
    # Test 3 : malformed lines
    lines3 = [
        '',
        'bad line without enough fields',
        '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z GET /api/orders 200 abcms tenant=a1',      # bad duration
        '2026-05-01T12:03:20Z GET /api/orders 200 100ms tenant=a1',      # valid
        '2026-05-01T12:03:21Z GET /api/orders 200 100ms invalidtenant',  # bad tenant
    ]
    res3 = compute_stats(lines3)
    assert res3['total_requests'] == 2          # indices 2 and 4
    assert res3['malformed_lines'] == 4         # indices 0,1,3,5
    assert res3['p95_latency_by_path']['/api/orders'] == 123   # sorted [100,123] -> idx=1
    assert len(res3['top_paths']) == 1
    assert res3['top_paths'][0]['path'] == '/api/orders'
    assert res3['top_paths'][0]['count'] == 2

    # ------------------------------------------------------------------
    # Test 4 : slow requests order and limits
    lines4 = [
        'slow1 GET /path1 200 1200ms tenant=t1',
        'slow2 GET /path2 200 800ms tenant=t1',
        'slow3 GET /path3 200 1500ms tenant=t1',
        'slow4 GET /path4 200 900ms tenant=t1',
        'fast1 GET /fast 200 100ms tenant=t2',
    ]
    res4 = compute_stats(lines4)
    assert len(res4['slow_requests']) == 2
    assert res4['slow_requests'][0]['duration'] == 1500
    assert res4['slow_requests'][0]['path'] == '/path3'
    assert res4['slow_requests'][0]['original_line'] == lines4[2]
    assert res4['slow_requests'][1]['duration'] == 1200
    assert res4['slow_requests'][1]['path'] == '/path1'
    assert res4['slow_requests'][1]['original_line'] == lines4[0]

    # ------------------------------------------------------------------
    # Test 5 : error rates (4xx/5xx)
    lines5 = [
        'GET /a 200 100ms tenant=t1',
        'GET /b 404 50ms  tenant=t1',
        'GET /c 500 200ms tenant=t2',
        'GET /d 300 150ms tenant=t1',          # 300 is not an error
    ]
    res5 = compute_stats(lines5)
    assert res5['tenant_error_rates']['t1'] == 0.333   # 1/3 ≈ 0.333
    assert res5['tenant_error_rates']['t2'] == 1.0

    # ------------------------------------------------------------------
    # Test 6 : P95 computation (integer arithmetic)
    lines6a = [f'GET /x 200 {i}ms tenant=t1' for i in [100,200,300,400,500]]
    res6a = compute_stats(lines6a)
    assert res6a['p95_latency_by_path']['/x'] == 500

    lines6b = ['GET /y 200 100ms tenant=t1', 'GET /y 200 200ms tenant=t1', 'GET /y 200 300ms tenant=t1']
    res6b = compute_stats(lines6b)
    assert res6b['p95_latency_by_path']['/y'] == 300

    lines6c = ['GET /z 200 250ms tenant=t1', 'GET /z 200 150ms tenant=t1']
    res6c = compute_stats(lines6c)
    assert res6c['p95_latency_by_path']['/z'] == 250

    # ------------------------------------------------------------------
    # Test 7 : top_paths limit to 5
    paths7 = ['/api/orders', '/api/users', '/api/products', '/api/cart', '/api/checkout', '/api/admin']
    lines7 = [f'GET {p} 200 100ms tenant=t1' for p in paths7]
    res7 = compute_stats(lines7)
    assert len(res7['top_paths']) == 5
    # all counts are 1, order is insertion order (stable sort)
    for i, tp in enumerate(res7['top_paths']):
        assert tp['path'] == paths7[i]
        assert tp['count'] == 1

    # ------------------------------------------------------------------
    # Test 8 : status code recording
    lines8 = [
        'GET /a 201 100ms tenant=t1',
        'POST /b 404 50ms tenant=t1',
        'PUT /c 500 200ms tenant=t2',
        'DELETE /d 301 150ms tenant=t1',
    ]
    res8 = compute_stats(lines8)
    assert res8['status_counts'] == {'201': 1, '404': 1, '500': 1, '301': 1}
    assert res8['total_requests'] == 4

    # ------------------------------------------------------------------
    # Test 9 : empty input
    lines9 = []
    res9 = compute_stats(lines9)
    assert res9['total_requests'] == 0
    assert res9['malformed_lines'] == 0
    assert res9['top_paths'] == []
    assert res9['p95_latency_by_path'] == {}
    assert res9['slow_requests'] == []
    assert res9['tenant_error_rates'] == {}

    # ------------------------------------------------------------------
    # Test 10 : many slow requests (top 10)
    lines10 = [f'GET /path 200 {i}ms tenant=t1' for i in range(1100, 1120)]   # 20 entries
    res10 = compute_stats(lines10)
    assert len(res10['slow_requests']) == 10
    expected_durations = list(range(1119, 1109, -1))
    for i, sr in enumerate(res10['slow_requests']):
        assert sr['duration'] == expected_durations[i]

    # ------------------------------------------------------------------
    # Test 11 : fragment removal (#)
    lines11 = ['GET /api/orders#section 200 100ms tenant=t1']
    res11 = compute_stats(lines11)
    assert '/api/orders' in res11['p95_latency_by_path']

    print("All tests passed.")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test()
    else:
        result = compute_stats(sys.stdin)
        # output compact JSON
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
