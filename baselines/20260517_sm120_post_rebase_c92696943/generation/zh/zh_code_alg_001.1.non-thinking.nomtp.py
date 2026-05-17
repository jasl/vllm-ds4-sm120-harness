#!/usr/bin/env python3
"""
log_analyzer.py - 访问日志分析器

用法：
    python log_analyzer.py < input.log
    python log_analyzer.py --test
"""

import sys
import json
import re
from collections import defaultdict


def parse_log_line(line):
    """
    解析单行日志
    返回: (时间, 方法, 路径, 状态码, 耗时ms, 租户) 或 None
    """
    line = line.strip()
    if not line:
        return None

    # 使用正则表达式解析日志行
    pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+(\w+)\s+(\S+)\s+(\d{3})\s+(\d+)ms\s+tenant=(\w+)$'
    match = re.match(pattern, line)

    if not match:
        return None

    timestamp = match.group(1)
    method = match.group(2)
    path = match.group(3)
    status_code = int(match.group(4))
    latency = int(match.group(5))
    tenant = match.group(6)

    # 移除路径中的查询参数
    path = path.split('?')[0]

    return (timestamp, method, path, status_code, latency, tenant, line)


def calculate_p95(sorted_values):
    """
    计算p95耗时
    p95定义为排序后向上取整位置的值
    """
    if not sorted_values:
        return 0

    n = len(sorted_values)
    # 向上取整位置 (1-indexed)
    index = max(1, int(n * 0.95 + 0.999))  # 向上取整
    index = min(index, n)  # 确保不超过数组长度
    return sorted_values[index - 1]


def analyze_logs(log_lines):
    """
    分析日志数据
    返回分析结果字典
    """
    # 统计变量
    total_requests = 0
    malformed_lines = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    slow_requests = []
    tenant_stats = defaultdict(lambda: {'total': 0, 'errors': 0})

    for line in log_lines:
        parsed = parse_log_line(line)

        if parsed is None:
            malformed_lines += 1
            continue

        timestamp, method, path, status_code, latency, tenant, original_line = parsed

        # 更新总请求数
        total_requests += 1

        # 更新状态码统计
        status_counts[str(status_code)] += 1

        # 更新路径统计
        path_counts[path] += 1

        # 收集路径耗时
        path_latencies[path].append(latency)

        # 收集慢请求
        if latency > 1000:
            slow_requests.append({
                'line': original_line,
                'path': path,
                'latency': latency
            })

        # 更新租户统计
        tenant_stats[tenant]['total'] += 1
        if 400 <= status_code < 600:
            tenant_stats[tenant]['errors'] += 1

    # 计算top路径
    top_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))[:5]
    top_paths_list = [{'path': path, 'count': count} for path, count in top_paths]

    # 计算p95耗时
    p95_latency_by_path = {}
    for path, latencies in path_latencies.items():
        sorted_latencies = sorted(latencies)
        p95_latency_by_path[path] = calculate_p95(sorted_latencies)

    # 排序慢请求
    slow_requests.sort(key=lambda x: (-x['latency'], x['path']))
    slow_requests = slow_requests[:10]

    # 计算租户错误率
    tenant_error_rates = {}
    for tenant, stats in tenant_stats.items():
        if stats['total'] > 0:
            error_rate = round(stats['errors'] / stats['total'], 3)
        else:
            error_rate = 0.0
        tenant_error_rates[tenant] = error_rate

    # 构建结果
    result = {
        'total_requests': total_requests,
        'status_counts': dict(status_counts),
        'top_paths': top_paths_list,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }

    return result


def test_parse_log_line():
    """测试解析日志行"""
    # 测试正常行
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    result = parse_log_line(line)
    assert result is not None
    assert result[0] == "2026-05-01T12:03:18Z"
    assert result[1] == "GET"
    assert result[2] == "/api/orders"
    assert result[3] == 200
    assert result[4] == 123
    assert result[5] == "a1"

    # 测试带查询参数的路径
    line = "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1"
    result = parse_log_line(line)
    assert result is not None
    assert result[2] == "/api/orders"  # 查询参数被移除

    # 测试错误行
    assert parse_log_line("") is None
    assert parse_log_line("invalid log line") is None

    print("test_parse_log_line: PASSED")


def test_calculate_p95():
    """测试p95计算"""
    # 测试正常情况
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert calculate_p95(sorted(values)) == 10  # 10 * 0.95 = 9.5, 向上取整=10

    # 测试单个元素
    assert calculate_p95([100]) == 100

    # 测试空列表
    assert calculate_p95([]) == 0

    print("test_calculate_p95: PASSED")


def test_analyze_logs():
    """测试日志分析"""
    test_logs = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
        "2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=b2",
        "2026-05-01T12:03:20Z GET /api/orders 404 789ms tenant=a1",
        "2026-05-01T12:03:21Z GET /api/users 500 1500ms tenant=c3",
        "invalid line",
        "2026-05-01T12:03:22Z GET /api/items 200 100ms tenant=b2",
        "2026-05-01T12:03:23Z POST /api/login 401 50ms tenant=a1",
    ]

    result = analyze_logs(test_logs)

    assert result['total_requests'] == 6
    assert result['malformed_lines'] == 1
    assert result['status_counts']['200'] == 2
    assert result['status_counts']['201'] == 1
    assert result['status_counts']['404'] == 1
    assert result['status_counts']['500'] == 1
    assert result['status_counts']['401'] == 1

    assert len(result['top_paths']) == 4  # 4个不同路径
    assert result['top_paths'][0]['path'] == '/api/orders'
    assert result['top_paths'][0]['count'] == 2

    assert len(result['slow_requests']) == 1  # 只有1个慢请求
    assert result['slow_requests'][0]['latency'] == 1500

    assert result['tenant_error_rates']['a1'] == 0.333  # 1/3 = 0.333
    assert result['tenant_error_rates']['b2'] == 0.0
    assert result['tenant_error_rates']['c3'] == 1.0

    print("test_analyze_logs: PASSED")


def test_complex_scenario():
    """测试复杂场景"""
    test_logs = [
        # 同一路径多次访问
        "2026-05-01T12:03:18Z GET /api/test 200 50ms tenant=a1",
        "2026-05-01T12:03:19Z GET /api/test 200 60ms tenant=a1",
        "2026-05-01T12:03:20Z GET /api/test 200 100ms tenant=a1",
        "2026-05-01T12:03:21Z GET /api/test 200 200ms tenant=a1",
        "2026-05-01T12:03:22Z GET /api/test 200 300ms tenant=a1",
        # 慢请求测试
        "2026-05-01T12:03:23Z POST /api/slow 200 1001ms tenant=b2",
        "2026-05-01T12:03:24Z POST /api/slow 200 2000ms tenant=b2",
        "2026-05-01T12:03:25Z POST /api/slow 200 5000ms tenant=b2",
        # 错误请求
        "2026-05-01T12:03:26Z GET /api/error 404 30ms tenant=c3",
        "2026-05-01T12:03:27Z GET /api/error 500 30ms tenant=c3",
        "2026-05-01T12:03:28Z GET /api/error 200 30ms tenant=c3",
        # 无效行
        "invalid log line 1",
        "invalid log line 2",
    ]

    result = analyze_logs(test_logs)

    # 验证p95计算
    test_latencies = [50, 60, 100, 200, 300]
    p95 = calculate_p95(sorted(test_latencies))
    assert result['p95_latency_by_path']['/api/test'] == p95

    # 验证慢请求排序（降序）
    assert len(result['slow_requests']) == 3
    assert result['slow_requests'][0]['latency'] == 5000
    assert result['slow_requests'][1]['latency'] == 2000
    assert result['slow_requests'][2]['latency'] == 1001

    # 验证错误率
    assert result['tenant_error_rates']['c3'] == round(2/3, 3)  # 2个错误/3个请求

    print("test_complex_scenario: PASSED")


def run_all_tests():
    """运行所有测试"""
    print("Running tests...")
    print("-" * 40)
    test_parse_log_line()
    test_calculate_p95()
    test_analyze_logs()
    test_complex_scenario()
    print("-" * 40)
    print("All tests passed!")


def main():
    """主函数"""
    # 检查是否运行测试
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_all_tests()
        return

    # 读取标准输入
    log_lines = sys.stdin.readlines()

    # 分析日志
    result = analyze_logs(log_lines)

    # 输出JSON
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
