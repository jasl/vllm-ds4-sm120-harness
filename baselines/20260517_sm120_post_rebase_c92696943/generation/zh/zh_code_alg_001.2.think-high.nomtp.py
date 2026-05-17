#!/usr/bin/env python3
"""
log_analyzer.py - 单文件命令行日志分析器
无第三方依赖，代码少于1000行。

用法:
    python log_analyzer.py < 日志文件
    python log_analyzer.py --test
"""

import sys
import json
import math
import re
from collections import defaultdict


# ---------- 解析单行日志 ----------
def parse_line(line: str):
    """
    解析一行日志，成功返回字典，失败返回 None。
    日志格式: ISO时间 HTTP方法 路径 状态码 耗时ms 租户
    """
    parts = line.strip().split()
    if len(parts) != 6:
        return None

    time_str, method, path, status_str, latency_str, tenant_str = parts

    # 验证时间格式: ISO 8601 且结尾为 'Z'
    if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', time_str):
        return None

    # 验证 HTTP 方法 (常见大写动词)
    if not re.match(r'^[A-Z]{1,10}$', method):
        return None

    # 路径必须以 '/' 开头
    if not path.startswith('/'):
        return None

    # 验证状态码
    if not status_str.isdigit():
        return None
    status = int(status_str)

    # 验证耗时
    if not re.match(r'^\d+ms$', latency_str):
        return None
    latency = int(latency_str[:-2])

    # 验证租户
    if not tenant_str.startswith('tenant=') or len(tenant_str) <= 7:
        return None
    tenant = tenant_str[7:]

    # 去掉路径中的查询参数
    path = path.split('?')[0]

    return {
        'time': time_str,
        'method': method,
        'path': path,
        'status': status,
        'latency': latency,
        'tenant': tenant
    }


# ---------- 核心分析函数 ----------
def analyze(lines):
    """
    接收行迭代器，返回统计结果字典。
    """
    total_requests = 0
    malformed_lines = 0
    status_counts = defaultdict(int)          # {status: count}
    path_counts = defaultdict(int)            # {path: count}
    p95_data = defaultdict(list)              # {path: [latency, ...]}
    slow_requests = []                        # [{line, path, latency}]
    tenant_stats = defaultdict(lambda: {'total': 0, 'errors': 0})  # {tenant: stats}

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue

        total_requests += 1
        status = parsed['status']
        path = parsed['path']
        latency = parsed['latency']
        tenant = parsed['tenant']

        status_counts[status] += 1
        path_counts[path] += 1
        p95_data[path].append(latency)

        if latency > 1000:
            slow_requests.append({
                'line': line.strip(),
                'path': path,
                'latency': latency
            })

        ts = tenant_stats[tenant]
        ts['total'] += 1
        if 400 <= status < 600:
            ts['errors'] += 1

    # ---- 计算 top_paths ----
    sorted_paths = sorted(path_counts.items(),
                          key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # ---- 计算 p95_latency_by_path ----
    p95_latency_by_path = {}
    for path, latencies in p95_data.items():
        latencies.sort()
        n = len(latencies)
        # p95 向上取整位置 (1-indexed)
        idx = math.ceil(0.95 * n) - 1
        if idx < 0:
            idx = 0
        p95_latency_by_path[path] = latencies[idx]

    # ---- 格式化 slow_requests ----
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_requests[:10]

    # ---- 计算 tenant_error_rates ----
    tenant_error_rates = {}
    for tenant, stats in tenant_stats.items():
        rate = round(stats['errors'] / stats['total'], 3)
        tenant_error_rates[tenant] = rate

    # ---- 组合结果 ----
    result = {
        'total_requests': total_requests,
        'status_counts': {str(k): v for k, v in status_counts.items()},
        'top_paths': top_paths,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }
    return result


# ---------- 测试函数 ----------
def test_parse_valid():
    """测试正常解析"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed is not None
    assert parsed['time'] == "2026-05-01T12:03:18Z"
    assert parsed['method'] == "GET"
    assert parsed['path'] == "/api/orders"
    assert parsed['status'] == 200
    assert parsed['latency'] == 123
    assert parsed['tenant'] == "a1"

def test_parse_query_removal():
    """路径查询参数应被移除"""
    line = "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed['path'] == "/api/orders"

def test_parse_missing_fields():
    """字段不足应返回 None"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms"
    assert parse_line(line) is None

def test_parse_bad_time():
    """错误时间格式"""
    line = "2026/05/01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    assert parse_line(line) is None

def test_parse_bad_latency():
    """耗时格式错误"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123msx tenant=a1"
    assert parse_line(line) is None

def test_parse_bad_status():
    """状态码非数字"""
    line = "2026-05-01T12:03:18Z GET /api/orders twohundred 123ms tenant=a1"
    assert parse_line(line) is None

def test_parse_invalid_tenant():
    """租户前缀错误"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant"
    assert parse_line(line) is None

def test_analyze_simple():
    """基本分析功能"""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 100ms tenant=a1\n",
        "2026-05-01T12:03:19Z POST /api/users 201 200ms tenant=b2\n",
        "2026-05-01T12:03:20Z DELETE /api/orders 400 300ms tenant=c3\n",
        "2026-05-01T12:03:21Z PUT /api/items 500 1500ms tenant=a1\n",
    ]
    result = analyze(lines)
    assert result['total_requests'] == 4
    assert result['status_counts'] == {"200": 1, "201": 1, "400": 1, "500": 1}
    assert result['malformed_lines'] == 0
    # top_paths: 4条不同路径，取5个，所以全部出现
    assert len(result['top_paths']) == 4
    # p95 (4个，0.95*4=3.8 ceil=4, idx=3 最大值)
    assert result['p95_latency_by_path']['/api/orders'] == 100
    # slow: 只有1500>1000
    assert len(result['slow_requests']) == 1
    assert result['slow_requests'][0]['latency'] == 1500
    # error rates
    assert result['tenant_error_rates']['a1'] == round(1/2, 3)  # 500 是错误
    assert result['tenant_error_rates']['b2'] == 0.0
    assert result['tenant_error_rates']['c3'] == 1.0

def test_analyze_malformed():
    """malformed line 计数"""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 100ms tenant=a1\n",
        "bad line here\n",
        "2026-05-01T12:03:19Z POST /api/users 201 200ms tenant=b2\n",
    ]
    result = analyze(lines)
    assert result['total_requests'] == 2
    assert result['malformed_lines'] == 1

def test_analyze_p95_exact():
    """p95 计算验证 (N=10)"""
    lines = []
    for i in range(1, 11):
        lines.append(f"2026-05-01T12:03:18Z GET /path {i*10} {i*100}ms tenant=t\n")
    result = analyze(lines)
    latencies = [i*100 for i in range(1,11)]
    latencies.sort()
    idx = math.ceil(0.95 * 10) - 1  # 10 -> idx=9
    expected = latencies[idx]
    assert result['p95_latency_by_path']['/path'] == expected

def test_analyze_slow_ordering():
    """慢请求排序与截取前10"""
    base = "2026-05-01T12:00:00Z GET /path 200 {}ms tenant=t\n"
    lines = [base.format(1000 + i*10) for i in range(20)]
    result = analyze(lines)
    assert len(result['slow_requests']) == 10
    # 检查降序
    lats = [r['latency'] for r in result['slow_requests']]
    assert lats == sorted(lats, reverse=True)
    # 检查最小的是第11个值？前10个最大的是 1000+190=1190 到 1000+10=1010? 注意i从0开始: 1000到1190，最大1190
    assert lats[0] == 1190
    assert lats[-1] == 1100  # 第10个应该是i=10:1000+100=1100

def test_analyze_empty():
    """空输入"""
    result = analyze([])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 0
    assert result['top_paths'] == []
    assert result['p95_latency_by_path'] == {}
    assert result['slow_requests'] == []
    assert result['tenant_error_rates'] == {}

def run_all_tests():
    """执行所有测试"""
    test_parse_valid()
    test_parse_query_removal()
    test_parse_missing_fields()
    test_parse_bad_time()
    test_parse_bad_latency()
    test_parse_bad_status()
    test_parse_invalid_tenant()
    test_analyze_simple()
    test_analyze_malformed()
    test_analyze_p95_exact()
    test_analyze_slow_ordering()
    test_analyze_empty()
    print("所有测试通过。")


# ---------- 主入口 ----------
if __name__ == '__main__':
    if '--test' in sys.argv:
        run_all_tests()
    else:
        try:
            lines = sys.stdin.readlines()
        except KeyboardInterrupt:
            sys.exit(1)
        result = analyze(lines)
        print(json.dumps(result, ensure_ascii=False, indent=2))
