#!/usr/bin/env python3
"""
log_analyzer.py - 访问日志分析器

从标准输入读取访问日志，输出JSON格式的分析结果。
"""

import sys
import json
import re
from collections import defaultdict, Counter

# ============================================================
# 日志解析模块
# ============================================================

def parse_log_line(line):
    """
    解析单行日志

    格式: 2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1

    返回: (成功标志, 解析结果或错误信息)
    """
    line = line.rstrip('\n\r')
    if not line:
        return False, None

    # 正则匹配日志行
    pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\s+(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(\S+)\s+(\d{3})\s+(\d+)ms\s+tenant=(\S+)$'
    match = re.match(pattern, line)

    if not match:
        return False, None

    timestamp = match.group(1)
    method = match.group(2)
    raw_path = match.group(3)
    status_code = int(match.group(4))
    latency = int(match.group(5))
    tenant = match.group(6)

    # 去除查询参数
    path = raw_path.split('?')[0]

    return True, {
        'timestamp': timestamp,
        'method': method,
        'raw_path': raw_path,
        'path': path,
        'status_code': status_code,
        'latency': latency,
        'tenant': tenant,
        'original_line': line
    }


def parse_logs(lines):
    """
    解析多行日志

    返回: (解析结果列表, 解析失败数量)
    """
    parsed = []
    malformed = 0

    for line in lines:
        success, result = parse_log_line(line)
        if success:
            parsed.append(result)
        else:
            malformed += 1

    return parsed, malformed


# ============================================================
# 统计分析模块
# ============================================================

def compute_p95(values):
    """
    计算p95耗时（向上取整）

    p95定义为排序后向上取整位置的值
    """
    if not values:
        return 0

    sorted_values = sorted(values)
    n = len(sorted_values)

    # p95位置（1-based），向上取整
    # 例如n=100时，位置=95（取第95个元素）
    # 例如n=10时，位置=ceil(10*0.95)=10（取第10个元素）
    index = max(0, int(n * 0.95 + 0.999999) - 1)  # 确保向上取整
    if index >= n:
        index = n - 1

    return sorted_values[index]


def compute_statistics(parsed_logs):
    """
    计算所有统计指标
    """
    total_requests = len(parsed_logs)

    # 1. 状态码统计
    status_counts = Counter(log['status_code'] for log in parsed_logs)

    # 2. 路径统计
    path_counts = Counter(log['path'] for log in parsed_logs)
    top_paths = [{'path': path, 'count': count}
                 for path, count in path_counts.most_common(5)]

    # 3. p95延迟按路径统计
    latency_by_path = defaultdict(list)
    for log in parsed_logs:
        latency_by_path[log['path']].append(log['latency'])

    p95_latency_by_path = {}
    for path, latencies in latency_by_path.items():
        p95_latency_by_path[path] = compute_p95(latencies)

    # 4. 慢请求（大于1000ms，前10条按耗时降序）
    slow_requests_list = [log for log in parsed_logs if log['latency'] > 1000]
    slow_requests_list.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = []
    for log in slow_requests_list[:10]:
        slow_requests.append({
            'line': log['original_line'],
            'path': log['path'],
            'latency_ms': log['latency']
        })

    # 5. 租户错误率
    tenant_data = defaultdict(lambda: {'total': 0, 'errors': 0})
    for log in parsed_logs:
        tenant = log['tenant']
        status = log['status_code']
        tenant_data[tenant]['total'] += 1
        if 400 <= status < 600:
            tenant_data[tenant]['errors'] += 1

    tenant_error_rates = {}
    for tenant, data in tenant_data.items():
        if data['total'] > 0:
            rate = round(data['errors'] / data['total'], 3)
        else:
            rate = 0.0
        tenant_error_rates[tenant] = rate

    return {
        'total_requests': total_requests,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates
    }


# ============================================================
# 主程序
# ============================================================

def main():
    """主函数"""
    # 读取所有行
    lines = sys.stdin.readlines()

    # 解析日志
    parsed_logs, malformed_count = parse_logs(lines)

    # 计算统计
    stats = compute_statistics(parsed_logs)

    # 添加异常行数
    stats['malformed_lines'] = malformed_count

    # 输出JSON
    json_output = json.dumps(stats, ensure_ascii=False, indent=2)
    print(json_output)


# ============================================================
# 测试模块
# ============================================================

def test_parse_log_line():
    """测试日志行解析"""
    # 正常日志行
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    success, result = parse_log_line(line)
    assert success, "正常行应该解析成功"
    assert result['timestamp'] == "2026-05-01T12:03:18Z"
    assert result['method'] == "GET"
    assert result['path'] == "/api/orders"
    assert result['status_code'] == 200
    assert result['latency'] == 123
    assert result['tenant'] == "a1"

    # 带查询参数的行
    line = "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1"
    success, result = parse_log_line(line)
    assert success, "带查询参数的行应该解析成功"
    assert result['path'] == "/api/orders", "路径应去除查询参数"

    # 其他HTTP方法
    line = "2026-05-01T12:03:18Z POST /api/users 201 50ms tenant=b2"
    success, result = parse_log_line(line)
    assert success
    assert result['method'] == "POST"
    assert result['status_code'] == 201

    # 错误状态码
    line = "2026-05-01T12:03:18Z GET /api/orders 404 50ms tenant=c3"
    success, result = parse_log_line(line)
    assert success
    assert result['status_code'] == 404

    # 空行
    success, result = parse_log_line("")
    assert not success, "空行应解析失败"

    # 格式不正确的行
    success, result = parse_log_line("this is not a valid log line")
    assert not success, "格式不正确的行应解析失败"

    # 缺少字段的行
    success, result = parse_log_line("2026-05-01T12:03:18Z GET /api/orders")
    assert not success, "缺少字段的行应解析失败"

    print("✓ test_parse_log_line 通过")


def test_p95_calculation():
    """测试p95计算"""
    # 简单测试
    values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    # 20 * 0.95 = 19，向上取整为19，位置18（0-based）
    assert compute_p95(values) == 19, "20个元素的p95应为19"

    # 5个元素的测试
    values = [1, 2, 3, 4, 5]
    # 5 * 0.95 = 4.75，向上取整为5，位置4（0-based）
    assert compute_p95(values) == 5

    # 空列表
    assert compute_p95([]) == 0

    # 有重复值
    values = [100, 100, 100, 100, 200, 200, 200, 300, 300, 400]
    result = compute_p95(values)
    assert result > 0, "应有有效值"

    print("✓ test_p95_calculation 通过")


def test_statistics():
    """测试统计功能"""
    parsed_logs = [
        {'path': '/api/orders', 'status_code': 200, 'latency': 100, 'tenant': 'a1'},
        {'path': '/api/orders', 'status_code': 200, 'latency': 200, 'tenant': 'a1'},
        {'path': '/api/users', 'status_code': 404, 'latency': 50, 'tenant': 'b2'},
        {'path': '/api/users', 'status_code': 500, 'latency': 1500, 'tenant': 'b2'},
        {'path': '/api/products', 'status_code': 200, 'latency': 300, 'tenant': 'a1'},
        {'path': '/api/orders', 'status_code': 200, 'latency': 150, 'tenant': 'c3'},
    ]

    stats = compute_statistics(parsed_logs)

    # 总请求数
    assert stats['total_requests'] == 6

    # 状态码统计
    assert stats['status_counts'][200] == 4
    assert stats['status_counts'][404] == 1
    assert stats['status_counts'][500] == 1

    # 路径统计（前5）
    assert len(stats['top_paths']) == 3  # 只有3个不同路径
    assert stats['top_paths'][0]['path'] == '/api/orders'
    assert stats['top_paths'][0]['count'] == 3

    # p95延迟
    assert '/api/orders' in stats['p95_latency_by_path']
    assert '/api/users' in stats['p95_latency_by_path']

    # 慢请求
    assert len(stats['slow_requests']) == 1  # 只有1个大于1000ms
    assert stats['slow_requests'][0]['latency_ms'] == 1500

    # 租户错误率
    assert 'a1' in stats['tenant_error_rates']
    assert 'b2' in stats['tenant_error_rates']
    # a1: 3请求，0错误，错误率0.0
    assert stats['tenant_error_rates']['a1'] == 0.0
    # b2: 2请求，2错误（404和500），错误率1.0
    assert stats['tenant_error_rates']['b2'] == 1.0
    # c3: 1请求，0错误，错误率0.0
    assert stats['tenant_error_rates']['c3'] == 0.0

    print("✓ test_statistics 通过")


def test_integration():
    """集成测试"""
    test_input = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "2026-05-01T12:03:19Z GET /api/users 404 50ms tenant=b2\n",
        "2026-05-01T12:03:20Z POST /api/orders 201 1500ms tenant=a1\n",
        "invalid line\n",
        "2026-05-01T12:03:21Z GET /api/products?page=2 200 200ms tenant=c3\n",
        "2026-05-01T12:03:22Z GET /api/orders 500 800ms tenant=b2\n",
        "2026-05-01T12:03:23Z PUT /api/users/123 200 50ms tenant=a1\n",
    ]

    parsed_logs, malformed = parse_logs(test_input)

    assert malformed == 1, "应检测到1条格式错误行"
    assert len(parsed_logs) == 6, "应成功解析6条日志"

    stats = compute_statistics(parsed_logs)
    stats['malformed_lines'] = malformed

    # 验证JSON可序列化
    try:
        json.dumps(stats)
    except (TypeError, ValueError) as e:
        assert False, f"JSON序列化失败: {e}"

    print("✓ test_integration 通过")


def run_tests():
    """运行所有测试"""
    print("运行测试...")
    test_parse_log_line()
    test_p95_calculation()
    test_statistics()
    test_integration()
    print("\n所有测试通过！")


# ============================================================
# 程序入口
# ============================================================

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        main()
