# Generation Transcript

- Case: `zh_code_alg_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 46.686734
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 338, "total_tokens": 3307, "completion_tokens": 2969, "prompt_tokens_details": null}`
- Prompt tokens: 338
- Completion tokens: 2969
- Total tokens: 3307

## Prompt

```markdown
请使用 Python 3 编写一个单文件命令行程序，文件名假定为 `log_analyzer.py`，不使用第三方库，总代码不超过1000行。

输入：从标准输入读取多行访问日志，每行格式如下：
`2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1`
字段依次为：ISO时间、HTTP方法、路径、状态码、耗时毫秒、租户。路径可能包含查询参数，例如 `/api/orders?page=2`，统计时应去掉查询参数。

任务：输出一个 JSON 对象，包含：
1. `total_requests`：总请求数。
2. `status_counts`：按状态码统计。
3. `top_paths`：请求量最高的前5个路径，含 `path` 和 `count`。
4. `p95_latency_by_path`：每个路径的 p95 耗时，毫秒整数。p95定义为排序后向上取整位置。
5. `slow_requests`：耗时大于1000ms的前10条，按耗时降序，保留原始行、路径、耗时。
6. `tenant_error_rates`：每个租户的错误率，4xx/5xx 算错误，保留三位小数。

要求：
- 跳过无法解析的行，并在输出中给出 `malformed_lines` 数量。
- 代码结构清晰，包含若干内置测试函数；当使用 `--test` 参数运行时执行测试。
- 正常运行时只输出 JSON，不输出解释文字。
```

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""
log_analyzer.py - A simple log analyzer for access logs.

Usage:
    cat log.txt | python log_analyzer.py
    python log_analyzer.py --test
"""

import sys
import json
import math
from collections import defaultdict

# ------------------------------------------------------------
# Parsing
# ------------------------------------------------------------

def parse_line(line):
    """
    Parse a single log line.
    Expected format:
    2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1

    Returns a dict with keys: timestamp, method, path, status, latency_ms, tenant
    or None if line is malformed.
    """
    line = line.strip()
    if not line:
        return None

    parts = line.split()
    if len(parts) < 6:
        return None

    # Timestamp (ISO format, we just check it contains 'T' and ends with 'Z')
    timestamp = parts[0]
    if 'T' not in timestamp or not timestamp.endswith('Z'):
        return None

    # HTTP method
    method = parts[1]
    if method not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'):
        return None

    # Path (may contain query string)
    raw_path = parts[2]
    # Remove query string (everything after first '?')
    path = raw_path.split('?')[0] if '?' in raw_path else raw_path

    # Status code
    try:
        status = int(parts[3])
        if status < 100 or status > 599:
            return None
    except ValueError:
        return None

    # Latency (ms) - ends with "ms"
    latency_str = parts[4]
    if not latency_str.endswith('ms'):
        return None
    try:
        latency_ms = int(latency_str[:-2])
    except ValueError:
        return None

    # Tenant (key=value form, typically tenant=xxx)
    tenant = parts[5]
    if '=' not in tenant:
        return None
    tenant_key, tenant_value = tenant.split('=', 1)
    if tenant_key != 'tenant':
        return None
    tenant = tenant_value

    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status,
        'latency_ms': latency_ms,
        'tenant': tenant,
        'raw_line': line.strip()
    }


# ------------------------------------------------------------
# Statistics
# ------------------------------------------------------------

def compute_p95(values):
    """
    Compute the 95th percentile (p95) of a list of integers.
    p95 is defined as the value at the ceiling index (1-indexed) after sorting.
    If list is empty, return 0.
    """
    if not values:
        return 0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    # Index (1-based) = ceil(0.95 * n)
    idx = math.ceil(0.95 * n) - 1  # convert to 0-based
    if idx < 0:
        idx = 0
    return sorted_vals[idx]


def compute_statistics(records):
    """
    Given a list of parsed records (dicts), compute all required statistics.
    Returns a dict with keys:
        total_requests, status_counts, top_paths, p95_latency_by_path,
        slow_requests, tenant_error_rates, malformed_lines
    """
    total = len(records)

    # Status counts
    status_counts = defaultdict(int)
    # Path counts
    path_counts = defaultdict(int)
    # Latency lists per path
    latency_by_path = defaultdict(list)
    # Slow requests (latency > 1000ms)
    slow_requests = []
    # Tenant error tracking: total and error counts
    tenant_total = defaultdict(int)
    tenant_errors = defaultdict(int)

    for rec in records:
        status = rec['status']
        path = rec['path']
        latency = rec['latency_ms']
        tenant = rec['tenant']

        status_counts[status] += 1
        path_counts[path] += 1
        latency_by_path[path].append(latency)

        # Slow requests
        if latency > 1000:
            slow_requests.append({
                'raw_line': rec['raw_line'],
                'path': path,
                'latency_ms': latency
            })

        # Tenant errors (4xx or 5xx)
        tenant_total[tenant] += 1
        if 400 <= status <= 599:
            tenant_errors[tenant] += 1

    # Top 5 paths by count
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # p95 latency per path
    p95_by_path = {}
    for path, lat_list in latency_by_path.items():
        p95_by_path[path] = compute_p95(lat_list)

    # Top 10 slow requests sorted by latency desc
    slow_requests.sort(key=lambda x: -x['latency_ms'])
    slow_requests = slow_requests[:10]

    # Tenant error rates
    tenant_error_rates = {}
    for tenant, total_cnt in sorted(tenant_total.items()):
        err_cnt = tenant_errors.get(tenant, 0)
        rate = round(err_cnt / total_cnt, 3) if total_cnt > 0 else 0.0
        tenant_error_rates[tenant] = rate

    # Build result
    result = {
        'total_requests': total,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates
    }
    return result


# ------------------------------------------------------------
# Main processing
# ------------------------------------------------------------

def process_input(lines):
    """
    Process lines from an iterable (e.g., sys.stdin).
    Returns (records, malformed_count).
    """
    records = []
    malformed = 0
    for line in lines:
        rec = parse_line(line)
        if rec is None:
            malformed += 1
        else:
            records.append(rec)
    return records, malformed


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    lines = sys.stdin.readlines()
    records, malformed = process_input(lines)
    stats = compute_statistics(records)
    stats['malformed_lines'] = malformed
    print(json.dumps(stats, ensure_ascii=False, indent=4))


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------

def test_parse_line_valid():
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    rec = parse_line(line)
    assert rec is not None
    assert rec['timestamp'] == '2026-05-01T12:03:18Z'
    assert rec['method'] == 'GET'
    assert rec['path'] == '/api/orders'
    assert rec['status'] == 200
    assert rec['latency_ms'] == 123
    assert rec['tenant'] == 'a1'
    print("test_parse_line_valid OK")


def test_parse_line_with_query():
    line = "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1"
    rec = parse_line(line)
    assert rec is not None
    assert rec['path'] == '/api/orders'
    print("test_parse_line_with_query OK")


def test_parse_line_malformed():
    assert parse_line("") is None
    assert parse_line("garbage") is None
    assert parse_line("2026-05-01T12:03:18Z GET 200 123ms tenant=a1") is None  # missing path
    assert parse_line("2026-05-01T12:03:18Z GET /api 20 123ms tenant=a1") is None  # status 20
    assert parse_line("2026-05-01T12:03:18Z GET /api 200 123 tenant=a1") is None  # no ms
    assert parse_line("2026-05-01T12:03:18Z GET /api 200 123ms foo=bar") is None  # tenant key missing
    print("test_parse_line_malformed OK")


def test_p95():
    # Empty
    assert compute_p95([]) == 0
    # Single element
    assert compute_p95([100]) == 100
    # Simple list: [1,2,3,4,5,6,7,8,9,10] -> n=10, ceil(0.95*10)=10 -> idx=9 -> value=10
    vals = list(range(1, 11))
    assert compute_p95(vals) == 10
    # [1,2,3,4] -> n=4, ceil(0.95*4)=ceil(3.8)=4 -> idx=3 -> value=4
    assert compute_p95([1,2,3,4]) == 4
    # [10,20,30] -> n=3, ceil(0.95*3)=ceil(2.85)=3 -> idx=2 -> value=30
    assert compute_p95([10,20,30]) == 30
    print("test_p95 OK")


def test_compute_statistics():
    records = [
        {'timestamp': 't', 'method': 'GET', 'path': '/a', 'status': 200, 'latency_ms': 100, 'tenant': 't1', 'raw_line': '...'},
        {'timestamp': 't', 'method': 'GET', 'path': '/a', 'status': 404, 'latency_ms': 200, 'tenant': 't1', 'raw_line': '...'},
        {'timestamp': 't', 'method': 'GET', 'path': '/b', 'status': 500, 'latency_ms': 1500, 'tenant': 't2', 'raw_line': '...'},
        {'timestamp': 't', 'method': 'GET', 'path': '/b', 'status': 200, 'latency_ms': 50, 'tenant': 't2', 'raw_line': '...'},
    ]
    stats = compute_statistics(records)
    assert stats['total_requests'] == 4
    assert stats['status_counts'] == {200: 2, 404: 1, 500: 1}
    assert len(stats['top_paths']) == 2
    assert stats['top_paths'][0]['path'] == '/a'
    assert stats['top_paths'][0]['count'] == 2
    # p95 for /a: [100,200] -> ceil(0.95*2)=2 -> idx=1 -> 200
    assert stats['p95_latency_by_path']['/a'] == 200
    # p95 for /b: [50,1500] -> ceil(0.95*2)=2 -> idx=1 -> 1500
    assert stats['p95_latency_by_path']['/b'] == 1500
    # slow requests: only /b with 1500
    assert len(stats['slow_requests']) == 1
    assert stats['slow_requests'][0]['latency_ms'] == 1500
    # tenant error rates: t1: 1 error / 2 total = 0.5; t2: 1 error / 2 total = 0.5
    assert stats['tenant_error_rates']['t1'] == 0.5
    assert stats['tenant_error_rates']['t2'] == 0.5
    print("test_compute_statistics OK")


def test_process_input():
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "bad line\n",
        "2026-05-01T12:03:19Z POST /api/users 404 45ms tenant=a2\n",
        ""
    ]
    records, malformed = process_input(lines)
    assert malformed == 1  # "bad line" and empty line? empty line returns None so malformed
    # Actually empty line returns None, so malformed counts empty lines too.
    # Let's check: lines has 3 non-empty? Actually lines[3] is empty string -> malformed
    # But we have 2 good lines, 2 bad? Let's recalc:
    # line0: good, line1: bad, line2: good, line3: empty -> bad
    assert len(records) == 2
    assert malformed == 2  # bad line + empty line
    print("test_process_input OK")


def run_tests():
    test_parse_line_valid()
    test_parse_line_with_query()
    test_parse_line_malformed()
    test_p95()
    test_compute_statistics()
    test_process_input()
    print("All tests passed!")


if __name__ == "__main__":
    main()
```
````
