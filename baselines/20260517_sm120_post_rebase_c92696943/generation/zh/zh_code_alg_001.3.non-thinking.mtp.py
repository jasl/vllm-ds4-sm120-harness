#!/usr/bin/env python3
"""
log_analyzer.py - 访问日志分析工具

Usage:
    python log_analyzer.py < input.log
    python log_analyzer.py --test
"""

import sys
import json
import re
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


def parse_log_line(line: str) -> Optional[Dict]:
    """解析单行日志，返回字段字典或None（如果解析失败）"""
    pattern = (
        r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+'
        r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+'
        r'(\S+)\s+'
        r'(\d{3})\s+'
        r'(\d+)ms\s+'
        r'tenant=(\S+)$'
    )

    match = re.match(pattern, line.strip())
    if not match:
        return None

    return {
        'timestamp': match.group(1),
        'method': match.group(2),
        'raw_path': match.group(3),
        'status_code': int(match.group(4)),
        'latency_ms': int(match.group(5)),
        'tenant': match.group(6)
    }


def strip_query_params(path: str) -> str:
    """去除路径中的查询参数"""
    return path.split('?')[0]


def calculate_p95(sorted_values: List[int]) -> int:
    """计算P95值，使用向上取整位置"""
    if not sorted_values:
        return 0
    n = len(sorted_values)
    index = int((95 * n) / 100)
    if index >= n:
        index = n - 1
    return sorted_values[index]


def analyze_logs(lines: List[str]) -> Dict:
    """分析日志行，返回统计结果"""
    total_requests = 0
    malformed_lines = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    slow_requests = []
    tenant_errors = defaultdict(lambda: {'total': 0, 'errors': 0})

    for line in lines:
        parsed = parse_log_line(line)
        if not parsed:
            malformed_lines += 1
            continue

        total_requests += 1
        status_code = parsed['status_code']
        raw_path = parsed['raw_path']
        path = strip_query_params(raw_path)
        latency = parsed['latency_ms']
        tenant = parsed['tenant']

        # 状态码统计
        status_counts[str(status_code)] += 1

        # 路径统计
        path_counts[path] += 1

        # 延迟收集
        path_latencies[path].append(latency)

        # 慢请求
        if latency > 1000:
            slow_requests.append({
                'original_line': line.strip(),
                'path': path,
                'latency_ms': latency
            })

        # 租户错误率
        tenant_errors[tenant]['total'] += 1
        if 400 <= status_code < 600:
            tenant_errors[tenant]['errors'] += 1

    # 排序慢请求并取前10
    slow_requests.sort(key=lambda x: x['latency_ms'], reverse=True)
    slow_requests = slow_requests[:10]

    # 计算每个路径的P95延迟
    p95_latency_by_path = {}
    for path, latencies in path_latencies.items():
        sorted_latencies = sorted(latencies)
        p95_latency_by_path[path] = calculate_p95(sorted_latencies)

    # 获取前5热门路径
    top_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_paths_list = [{'path': path, 'count': count} for path, count in top_paths]

    # 计算租户错误率
    tenant_error_rates = {}
    for tenant, data in tenant_errors.items():
        if data['total'] > 0:
            error_rate = data['errors'] / data['total']
            tenant_error_rates[tenant] = round(error_rate, 3)
        else:
            tenant_error_rates[tenant] = 0.0

    return {
        'total_requests': total_requests,
        'status_counts': dict(status_counts),
        'top_paths': top_paths_list,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }


# ========== 测试函数 ==========

def test_parse_log_line():
    """测试日志行解析"""
    valid_line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    result = parse_log_line(valid_line)
    assert result is not None
    assert result['timestamp'] == "2026-05-01T12:03:18Z"
    assert result['method'] == "GET"
    assert result['raw_path'] == "/api/orders"
    assert result['status_code'] == 200
    assert result['latency_ms'] == 123
    assert result['tenant'] == "a1"

    # 带查询参数的路径
    line_with_params = "2026-05-01T12:03:18Z POST /api/users?page=2 201 456ms tenant=b2"
    result2 = parse_log_line(line_with_params)
    assert result2 is not None
    assert result2['raw_path'] == "/api/users?page=2"

    # 无效行
    invalid_line = "this is not a valid log line"
    assert parse_log_line(invalid_line) is None

    print("✓ test_parse_log_line passed")


def test_strip_query_params():
    """测试去除查询参数"""
    assert strip_query_params("/api/orders") == "/api/orders"
    assert strip_query_params("/api/orders?page=2") == "/api/orders"
    assert strip_query_params("/api/users?filter=active&sort=name") == "/api/users"
    print("✓ test_strip_query_params passed")


def test_calculate_p95():
    """测试P95计算"""
    values = list(range(1, 101))
    assert calculate_p95(values) == 95
    assert calculate_p95([1, 2, 3]) == 3
    assert calculate_p95([]) == 0
    assert calculate_p95([100]) == 100
    print("✓ test_calculate_p95 passed")


def test_analyze_logs_basic():
    """测试基本日志分析"""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 50ms tenant=a1",
        "2026-05-01T12:03:19Z POST /api/users 201 100ms tenant=b2",
        "2026-05-01T12:03:20Z GET /api/orders 404 200ms tenant=a1",
        "2026-05-01T12:03:21Z PUT /api/products 500 1500ms tenant=c3",
        "invalid line",
    ]

    result = analyze_logs(lines)
    assert result['total_requests'] == 4
    assert result['malformed_lines'] == 1
    assert result['status_counts'] == {"200": 1, "201": 1, "404": 1, "500": 1}
    assert len(result['top_paths']) == 3
    assert result['slow_requests'] == [
        {'original_line': lines[3], 'path': '/api/products', 'latency_ms': 1500}
    ]
    assert result['tenant_error_rates'] == {'a1': 0.5, 'b2': 0.0, 'c3': 1.0}
    print("✓ test_analyze_logs_basic passed")


def test_analyze_logs_with_query_params():
    """测试带查询参数的路径统计"""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders?page=1 200 50ms tenant=a1",
        "2026-05-01T12:03:19Z GET /api/orders?page=2 200 60ms tenant=a1",
        "2026-05-01T12:03:20Z GET /api/orders?filter=active 200 70ms tenant=b2",
    ]

    result = analyze_logs(lines)
    assert result['total_requests'] == 3
    top_path = result['top_paths'][0]
    assert top_path['path'] == '/api/orders'
    assert top_path['count'] == 3
    print("✓ test_analyze_logs_with_query_params passed")


def test_analyze_logs_p95():
    """测试P95延迟计算"""
    lines = [
        f"2026-05-01T12:03:18Z GET /api/test {200 if i % 2 == 0 else 404} {i*10}ms tenant=t{i}"
        for i in range(1, 21)
    ]

    result = analyze_logs(lines)
    p95 = result['p95_latency_by_path']['/api/test']
    assert p95 == 190  # 第19个值（1-indexed）是190
    print("✓ test_analyze_logs_p95 passed")


def test_malformed_lines():
    """测试异常行处理"""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 50ms tenant=a1",
        "invalid line 1",
        "",
        "2026-05-01T12:03:19Z POST /api/users 201 100ms tenant=b2",
        "another invalid line",
    ]

    result = analyze_logs(lines)
    assert result['total_requests'] == 2
    assert result['malformed_lines'] == 3
    print("✓ test_malformed_lines passed")


def test_slow_requests_ordering():
    """测试慢请求排序和限制"""
    lines = [
        f"2026-05-01T12:03:18Z GET /api/test 200 {i*100}ms tenant=t{i}"
        for i in range(1, 15)
    ]

    result = analyze_logs(lines)
    assert len(result['slow_requests']) == 10
    for i in range(len(result['slow_requests']) - 1):
        assert result['slow_requests'][i]['latency_ms'] >= result['slow_requests'][i+1]['latency_ms']
    print("✓ test_slow_requests_ordering passed")


def test_empty_input():
    """测试空输入"""
    result = analyze_logs([])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 0
    assert result['status_counts'] == {}
    assert result['top_paths'] == []
    assert result['p95_latency_by_path'] == {}
    assert result['slow_requests'] == []
    assert result['tenant_error_rates'] == {}
    print("✓ test_empty_input passed")


def test_tenant_error_rates():
    """测试租户错误率计算"""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 50ms tenant=a1",
        "2026-05-01T12:03:19Z GET /api/orders 404 100ms tenant=a1",
        "2026-05-01T12:03:20Z GET /api/orders 500 150ms tenant=a1",
        "2026-05-01T12:03:21Z GET /api/orders 201 50ms tenant=b2",
        "2026-05-01T12:03:22Z GET /api/orders 302 50ms tenant=b2",
    ]

    result = analyze_logs(lines)
    assert result['tenant_error_rates']['a1'] == round(2/3, 3)
    assert result['tenant_error_rates']['b2'] == 0.0
    print("✓ test_tenant_error_rates passed")


def run_tests():
    """运行所有测试"""
    print("Running tests...\n")
    test_parse_log_line()
    test_strip_query_params()
    test_calculate_p95()
    test_analyze_logs_basic()
    test_analyze_logs_with_query_params()
    test_analyze_logs_p95()
    test_malformed_lines()
    test_slow_requests_ordering()
    test_empty_input()
    test_tenant_error_rates()
    print("\nAll tests passed!")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    # 从标准输入读取所有行
    lines = sys.stdin.readlines()

    # 分析日志
    result = analyze_logs(lines)

    # 输出JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
