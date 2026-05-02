# Generation Transcript

- Case: `zh_code_alg_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 20.029367
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 338, "total_tokens": 3136, "completion_tokens": 2798, "prompt_tokens_details": null}`
- Prompt tokens: 338
- Completion tokens: 2798
- Total tokens: 3136

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
Here's a single-file Python command-line program `log_analyzer.py` that meets your spec:

```python
#!/usr/bin/env python3
"""
log_analyzer.py - Analyze web access logs from stdin and output JSON statistics.

Usage:
  python log_analyzer.py < logfile.txt
  python log_analyzer.py --test
"""

import sys
import json
import math
import re
from collections import defaultdict

# ------------------------------------------------------------------
# Parsing
# ------------------------------------------------------------------
LINE_RE = re.compile(
    r'^'
    r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+'      # timestamp
    r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+'      # method
    r'(\S+)\s+'                                         # path (with possible query)
    r'(\d{3})\s+'                                       # status code
    r'(\d+)ms\s+'                                       # latency in ms
    r'tenant=(\S+)'                                     # tenant
    r'$'
)


def parse_line(line):
    """Parse a single log line. Returns dict or None."""
    m = LINE_RE.match(line.rstrip('\n'))
    if not m:
        return None
    timestamp, method, path_with_query, status, latency, tenant = m.groups()
    # Remove query parameters from path
    path = path_with_query.split('?')[0] if '?' in path_with_query else path_with_query
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': int(status),
        'latency': int(latency),
        'tenant': tenant,
        'original': line.rstrip('\n')
    }


# ------------------------------------------------------------------
# Analysis
# ------------------------------------------------------------------
def analyze(lines):
    stats = {
        'total_requests': 0,
        'malformed_lines': 0,
        'status_counts': defaultdict(int),
        'paths': defaultdict(int),
        'latency_by_path': defaultdict(list),
        'slow_requests': [],
        'tenant_errors': defaultdict(lambda: {'total': 0, 'errors': 0})
    }

    for line in lines:
        record = parse_line(line)
        if record is None:
            stats['malformed_lines'] += 1
            continue

        stats['total_requests'] += 1
        stats['status_counts'][record['status']] += 1
        stats['paths'][record['path']] += 1
        stats['latency_by_path'][record['path']].append(record['latency'])

        if record['latency'] > 1000:
            stats['slow_requests'].append(record)

        tenant = record['tenant']
        stats['tenant_errors'][tenant]['total'] += 1
        if 400 <= record['status'] < 600:
            stats['tenant_errors'][tenant]['errors'] += 1

    return stats


# ------------------------------------------------------------------
# Output formatting
# ------------------------------------------------------------------
def compute_p95(sorted_latencies):
    n = len(sorted_latencies)
    if n == 0:
        return 0
    # p95 index (upward rounding, 1-based)
    k = math.ceil(0.95 * n) - 1  # 0-based index
    if k >= n:
        k = n - 1
    return sorted_latencies[k]


def build_result(stats):
    # 1. total_requests
    result = {}
    result['total_requests'] = stats['total_requests']

    # 2. status_counts
    result['status_counts'] = dict(stats['status_counts'])

    # 3. top_paths
    sorted_paths = sorted(stats['paths'].items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]
    result['top_paths'] = top_paths

    # 4. p95_latency_by_path
    p95_by_path = {}
    for path, latencies in stats['latency_by_path'].items():
        sorted_lat = sorted(latencies)
        p95_by_path[path] = compute_p95(sorted_lat)
    result['p95_latency_by_path'] = p95_by_path

    # 5. slow_requests (top 10 by latency descending)
    slow_sorted = sorted(stats['slow_requests'], key=lambda r: -r['latency'])[:10]
    slow_list = []
    for rec in slow_sorted:
        slow_list.append({
            'line': rec['original'],
            'path': rec['path'],
            'latency_ms': rec['latency']
        })
    result['slow_requests'] = slow_list

    # 6. tenant_error_rates
    tenant_rates = {}
    for tenant, data in stats['tenant_errors'].items():
        total = data['total']
        errors = data['errors']
        rate = round(errors / total, 3) if total > 0 else 0.0
        tenant_rates[tenant] = rate
    result['tenant_error_rates'] = tenant_rates

    # malformed_lines attached to result (not required but useful)
    result['malformed_lines'] = stats['malformed_lines']

    return result


# ------------------------------------------------------------------
# Testing
# ------------------------------------------------------------------
def test_parse_line():
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    rec = parse_line(line)
    assert rec is not None
    assert rec['timestamp'] == "2026-05-01T12:03:18Z"
    assert rec['method'] == "GET"
    assert rec['path'] == "/api/orders"
    assert rec['status'] == 200
    assert rec['latency'] == 123
    assert rec['tenant'] == "a1"
    print("test_parse_line: OK")

def test_parse_line_with_query():
    line = "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1"
    rec = parse_line(line)
    assert rec is not None
    assert rec['path'] == "/api/orders"
    print("test_parse_line_with_query: OK")

def test_parse_malformed():
    lines = [
        "",
        "something invalid",
        "2026-05-01T12:03:18Z GET /api/orders 200 abcms tenant=a1",  # bad latency
    ]
    for line in lines:
        assert parse_line(line) is None
    print("test_parse_malformed: OK")

def test_p95():
    # p95 for a list of 20 items: ceil(0.95*20)=19th element (1-based) => index 18 in 0-based
    l = list(range(1, 21))  # 1..20
    val = compute_p95(l)
    # 95% of 20 = 19 (ceiled), so value at position 19 (1-based) = 19
    assert val == 19, f"Expected 19, got {val}"
    # even number
    l2 = list(range(1, 101))  # 1..100
    val2 = compute_p95(l2)
    # ceil(95) = 95, so index 94 -> value 95
    assert val2 == 95, f"Expected 95, got {val2}"
    # single element
    assert compute_p95([42]) == 42
    print("test_p95: OK")

def test_full_sample():
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
        "2026-05-01T12:03:19Z POST /api/login 401 50ms tenant=b2",
        "2026-05-01T12:03:20Z GET /api/users 500 2000ms tenant=a1",
        "2026-05-01T12:03:21Z GET /api/orders?page=2 200 150ms tenant=c3",
        "malformed line here",
        "2026-05-01T12:03:22Z GET /api/orders 404 30ms tenant=a1",
        "2026-05-01T12:03:23Z GET /api/users 200 80ms tenant=a1",
        "2026-05-01T12:03:24Z GET /api/users 200 90ms tenant=b2",
        "2026-05-01T12:03:25Z POST /api/login 500 1200ms tenant=c3",
    ]
    stats = analyze(lines)
    result = build_result(stats)
    # total (8 valid, 1 malformed)
    assert result['total_requests'] == 8
    assert result['malformed_lines'] == 1
    # status counts
    assert result['status_counts'][200] == 3  # /api/orders (x2), /api/users (x2)
    # Actually re-check:
    # 200: lines 0,3,6 => 3
    # 401: line1 =>1
    # 500: lines2,7 =>2
    # 404: line5 =>1
    assert result['status_counts'] == {200: 3, 401: 1, 500: 2, 404: 1}
    # top paths: /api/orders (2+1?), let's compute:
    # /api/orders appears in lines 0,3,5 -> 3 times
    # /api/users appears lines 2,6,7 -> 3 times (with or without query? line2 /api/users, line6 /api/users, line7 /api/users)
    # /api/login appears lines 1,8 -> 2 times
    # So top 5: /api/orders (3), /api/users (3), /api/login (2)
    assert result['top_paths'][0]['path'] in ('/api/orders', '/api/users')
    # slow requests > 1000ms: lines2 (2000ms), line8 (1200ms) => 2 entries
    assert len(result['slow_requests']) == 2
    assert result['slow_requests'][0]['latency_ms'] == 2000
    assert result['slow_requests'][1]['latency_ms'] == 1200
    # p95 by path: for path with few entries should be straightforward
    # Check that p95 for /api/login (2 values: 50,1200) => ceil(0.95*2)=2 => 1200
    assert result['p95_latency_by_path']['/api/login'] == 1200
    # tenant error rates: a1: errors: 404 (line5) + 500 (line2)=2, total=4 => 0.5
    # b2: errors: 401 =>1, total=2 => 0.5
    # c3: errors: 500 =>1, total=2 => 0.5
    assert result['tenant_error_rates']['a1'] == 0.5
    assert result['tenant_error_rates']['b2'] == 0.5
    assert result['tenant_error_rates']['c3'] == 0.5
    print("test_full_sample: OK")

def run_tests():
    test_parse_line()
    test_parse_line_with_query()
    test_parse_malformed()
    test_p95()
    test_full_sample()
    print("All tests passed!")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        lines = sys.stdin.readlines()
        stats = analyze(lines)
        result = build_result(stats)
        # Output pure JSON
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write('\n')


if __name__ == '__main__':
    main()
```

### How to use

1. Save the code as `log_analyzer.py`.
2. To run a test:
   ```bash
   python log_analyzer.py --test
   ```
3. To analyze a log file:
   ```bash
   python log_analyzer.py < sample.log
   ```

The output is pure JSON with the requested structure. The code includes all required fields, skips malformed lines, and computes p95 with ceiling rounding.
````
