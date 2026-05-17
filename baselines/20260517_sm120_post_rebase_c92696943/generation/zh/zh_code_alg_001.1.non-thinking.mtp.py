#!/usr/bin/env python3
"""
log_analyzer.py - 访问日志分析器

从标准输入读取多行访问日志，分析并输出JSON格式的统计结果。

用法：
    python log_analyzer.py < access.log
    python log_analyzer.py --test
"""

import sys
import json
import math


def parse_log_line(line):
    """
    解析单行日志。

    格式：2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1

    返回：
        dict：包含各字段的字典，如果解析失败返回None
    """
    line = line.strip()
    if not line:
        return None

    parts = line.split()

    if len(parts) != 6:
        return None

    try:
        timestamp = parts[0]
        method = parts[1]
        path_with_query = parts[2]
        status_code = int(parts[3])
        latency_str = parts[4]
        tenant = parts[5].split('=')[1] if '=' in parts[5] else parts[5]

        # 解析耗时
        if latency_str.endswith('ms'):
            latency = int(latency_str[:-2])
        else:
            latency = int(latency_str)

        # 去掉路径中的查询参数
        path = path_with_query.split('?')[0] if '?' in path_with_query else path_with_query

        # 从租户字符串中提取租户ID（可能格式为 tenant=a1）
        if 'tenant=' in parts[5]:
            tenant = parts[5].split('=')[1]
        else:
            tenant = parts[5]

        return {
            'timestamp': timestamp,
            'method': method,
            'path': path,
            'status_code': status_code,
            'latency': latency,
            'tenant': tenant,
            'original_line': line
        }
    except (ValueError, IndexError):
        return None


def calculate_p95(values):
    """
    计算P95百分位数。

    按照定义：排序后向上取整位置。

    参数：
        values：数值列表

    返回：
        P95值
    """
    if not values:
        return 0

    sorted_values = sorted(values)
    n = len(sorted_values)

    # P95位置：向上取整
    # 位置从1开始计数
    pos = math.ceil(n * 0.95)
    pos = min(pos, n)  # 确保不超过数组长度

    return sorted_values[pos - 1]


def analyze_logs(lines):
    """
    分析日志行，生成统计结果。

    参数：
        lines：日志行列表

    返回：
        dict：统计结果
    """
    parsed_entries = []
    malformed_lines = 0

    for line in lines:
        entry = parse_log_line(line)
        if entry is None:
            malformed_lines += 1
        else:
            parsed_entries.append(entry)

    total_requests = len(parsed_entries)

    # 按状态码统计
    status_counts = {}
    for entry in parsed_entries:
        status = entry['status_code']
        status_counts[status] = status_counts.get(status, 0) + 1

    # 按路径统计请求量
    path_counts = {}
    for entry in parsed_entries:
        path = entry['path']
        path_counts[path] = path_counts.get(path, 0) + 1

    # 请求量最高的前5个路径
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': path, 'count': count} for path, count in sorted_paths[:5]]

    # 每个路径的P95耗时
    path_latencies = {}
    for entry in parsed_entries:
        path = entry['path']
        if path not in path_latencies:
            path_latencies[path] = []
        path_latencies[path].append(entry['latency'])

    p95_latency_by_path = {}
    for path, latencies in path_latencies.items():
        p95_latency_by_path[path] = calculate_p95(latencies)

    # 慢请求（耗时大于1000ms的前10条）
    slow_entries = [entry for entry in parsed_entries if entry['latency'] > 1000]
    slow_entries.sort(key=lambda x: (-x['latency'], x['original_line']))
    slow_requests = [
        {
            'line': entry['original_line'],
            'path': entry['path'],
            'latency': entry['latency']
        }
        for entry in slow_entries[:10]
    ]

    # 每个租户的错误率
    tenant_requests = {}
    tenant_errors = {}
    for entry in parsed_entries:
        tenant = entry['tenant']
        tenant_requests[tenant] = tenant_requests.get(tenant, 0) + 1
        if 400 <= entry['status_code'] < 600:
            tenant_errors[tenant] = tenant_errors.get(tenant, 0) + 1

    tenant_error_rates = {}
    for tenant in tenant_requests:
        total = tenant_requests[tenant]
        errors = tenant_errors.get(tenant, 0)
        error_rate = round(errors / total, 3) if total > 0 else 0.0
        tenant_error_rates[tenant] = error_rate

    return {
        'total_requests': total_requests,
        'status_counts': status_counts,
        'top_paths': top_paths,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }


def run_tests():
    """
    运行内置测试函数。
    """
    passed = 0
    failed = 0

    def test_parse_log_line():
        """测试日志行解析"""
        # 正常行
        line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
        entry = parse_log_line(line)
        assert entry is not None
        assert entry['path'] == '/api/orders'
        assert entry['status_code'] == 200
        assert entry['latency'] == 123
        assert entry['tenant'] == 'a1'
        assert entry['method'] == 'GET'
        print("  ✓ 解析正常行")

        # 带查询参数的路径
        line = "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1"
        entry = parse_log_line(line)
        assert entry['path'] == '/api/orders'
        print("  ✓ 解析带查询参数的路径")

        # 错误行（字段不足）
        line = "2026-05-01T12:03:18Z GET /api/orders 200"
        entry = parse_log_line(line)
        assert entry is None
        print("  ✓ 拒绝字段不足的行")

        # 错误行（无效状态码）
        line = "2026-05-01T12:03:18Z GET /api/orders abc 123ms tenant=a1"
        entry = parse_log_line(line)
        assert entry is None
        print("  ✓ 拒绝无效状态码的行")

        # 空行
        assert parse_log_line("") is None
        print("  ✓ 拒绝空行")

        # 不同耗时格式
        line = "2026-05-01T12:03:18Z POST /api/login 401 1500ms tenant=b2"
        entry = parse_log_line(line)
        assert entry['latency'] == 1500
        assert entry['status_code'] == 401
        print("  ✓ 解析不同耗时格式")

        return True

    def test_calculate_p95():
        """测试P95计算"""
        # 简单情况
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        p95 = calculate_p95(values)
        expected_pos = math.ceil(20 * 0.95)  # 19
        assert p95 == values[expected_pos - 1] == 19
        print(f"  ✓ P95计算正确: {p95}")

        # 空列表
        assert calculate_p95([]) == 0
        print("  ✓ 空列表P95为0")

        # 单元素
        assert calculate_p95([42]) == 42
        print("  ✓ 单元素P95正确")

        # 向上取整
        values = [10, 20, 30]
        p95 = calculate_p95(values)
        pos = math.ceil(3 * 0.95)
        assert pos == 3
        assert p95 == values[2] == 30
        print(f"  ✓ 向上取整P95正确: {p95}")

        return True

    def test_analyze_logs():
        """测试整体分析逻辑"""
        test_lines = [
            "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
            "2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=b2",
            "2026-05-01T12:03:20Z GET /api/orders 200 789ms tenant=a1",
            "invalid line",
            "2026-05-01T12:03:21Z GET /api/products 404 100ms tenant=c3",
            "2026-05-01T12:03:22Z POST /api/orders 500 2000ms tenant=a1",
            "2026-05-01T12:03:23Z GET /api/orders 200 50ms tenant=b2",
        ]

        result = analyze_logs(test_lines)

        assert result['total_requests'] == 6
        assert result['malformed_lines'] == 1
        assert result['status_counts'][200] == 3
        assert result['status_counts'][201] == 1
        assert result['status_counts'][404] == 1
        assert result['status_counts'][500] == 1

        # 检查top_paths
        paths = [p['path'] for p in result['top_paths']]
        assert '/api/orders' in paths

        # 检查慢请求
        assert len(result['slow_requests']) == 1
        assert result['slow_requests'][0]['latency'] == 2000

        # 检查租户错误率
        assert result['tenant_error_rates']['a1'] == round(1/3, 3)
        assert result['tenant_error_rates']['b2'] == 0.0

        print("  ✓ 整体分析逻辑正确")
        return True

    def test_slow_requests_limit():
        """测试慢请求限制前10条"""
        lines = []
        for i in range(15):
            lines.append(f"2026-05-01T12:00:{i:02d}Z GET /api/test 200 {2000+i}ms tenant=a{i%3}")

        result = analyze_logs(lines)
        assert len(result['slow_requests']) == 10
        # 检查降序排列
        latencies = [r['latency'] for r in result['slow_requests']]
        assert all(latencies[i] >= latencies[i+1] for i in range(len(latencies)-1))
        print("  ✓ 慢请求限制和排序正确")
        return True

    def test_p95_calculation_integration():
        """测试P95在分析中的集成"""
        lines = []
        for i in range(1, 101):
            lines.append(f"2026-05-01T12:00:00Z GET /api/test 200 {i}ms tenant=test")

        result = analyze_logs(lines)
        # 100个请求，P95位置是95
        assert result['p95_latency_by_path']['/api/test'] == 95
        print("  ✓ P95集成测试正确")
        return True

    # 运行所有测试
    tests = [
        ("解析日志行", test_parse_log_line),
        ("计算P95", test_calculate_p95),
        ("整体分析", test_analyze_logs),
        ("慢请求限制", test_slow_requests_limit),
        ("P95集成", test_p95_calculation_integration),
    ]

    print("运行测试...")
    print("=" * 40)

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"  ✓ {name} 测试通过")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ {name} 测试失败: {e}")
        except Exception as e:
            failed += 1
            print(f"  ✗ {name} 测试异常: {e}")
        print("-" * 40)

    print(f"\n测试完成: {passed} 通过, {failed} 失败")
    return failed == 0


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        success = run_tests()
        sys.exit(0 if success else 1)

    # 从标准输入读取所有行
    lines = sys.stdin.readlines()

    # 分析日志
    result = analyze_logs(lines)

    # 输出JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
