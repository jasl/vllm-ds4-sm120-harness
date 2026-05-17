#!/usr/bin/env python3
"""
log_analyzer.py - 访问日志分析器

用法：
    python log_analyzer.py < input.log
    python log_analyzer.py --test
"""

import sys
import json
import math
from collections import OrderedDict

# ---------- 辅助函数 ----------

def parse_line(line):
    """
    解析单行日志，成功返回字典，失败返回 None。
    字典键：time, method, path, status, latency_ms, tenant
    """
    parts = line.strip().split()
    if len(parts) != 6:
        return None
    time_str, method, raw_path, status_str, latency_str, tenant_str = parts

    # 验证时间格式（简单检查总长度和结尾'Z'）
    if not (len(time_str) == 20 and time_str.endswith('Z')):
        return None

    # 验证方法
    if method not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'):
        return None

    # 验证状态码
    if not (status_str.isdigit() and len(status_str) == 3):
        return None
    status = int(status_str)

    # 验证耗时
    if not (latency_str.endswith('ms') and latency_str[:-2].isdigit()):
        return None
    latency_ms = int(latency_str[:-2])

    # 提取路径（去掉查询参数）
    path = raw_path.split('?')[0]

    # 提取租户
    # 格式 tenant=xxx，可能有多个等号？ 取第一个等号后的全部字符串
    if '=' not in tenant_str:
        return None
    tenant = tenant_str.split('=', 1)[1]

    return {
        'time': time_str,
        'method': method,
        'path': path,
        'status': status,
        'latency_ms': latency_ms,
        'tenant': tenant,
        'raw_line': line.rstrip('\n')
    }


def run_analysis(lines):
    """
    对日志行列表进行分析，返回结果字典。
    """
    total_requests = 0
    malformed_lines = 0
    status_counts = {}
    path_counts = {}
    # 存储每个路径的耗时列表
    path_latencies = {}
    # 慢请求列表（原始行，路径，耗时）
    slow_requests = []
    # 租户统计
    tenant_total = {}
    tenant_errors = {}

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue
        total_requests += 1

        # 状态码
        status = parsed['status']
        status_counts[status] = status_counts.get(status, 0) + 1

        # 路径
        path = parsed['path']
        path_counts[path] = path_counts.get(path, 0) + 1

        # 路径耗时
        if path not in path_latencies:
            path_latencies[path] = []
        path_latencies[path].append(parsed['latency_ms'])

        # 慢请求
        if parsed['latency_ms'] > 1000:
            slow_requests.append({
                'raw_line': parsed['raw_line'],
                'path': path,
                'latency_ms': parsed['latency_ms']
            })

        # 租户
        tenant = parsed['tenant']
        tenant_total[tenant] = tenant_total.get(tenant, 0) + 1
        if 400 <= status < 600:  # 4xx 或 5xx 算错误
            tenant_errors[tenant] = tenant_errors.get(tenant, 0) + 1

    # 1. total_requests
    result = OrderedDict()
    result['total_requests'] = total_requests

    # 2. status_counts
    result['status_counts'] = status_counts

    # 3. top_paths (前5)
    sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths]
    result['top_paths'] = top_paths

    # 4. p95_latency_by_path
    p95_by_path = {}
    for path, lats in path_latencies.items():
        n = len(lats)
        if n == 0:
            continue
        lats_sorted = sorted(lats)
        k = math.ceil(0.95 * n)  # 向上取整位置 (1-indexed)
        # k 最大为 n
        k = min(k, n)
        p95 = lats_sorted[k - 1]  # 转为0-indexed
        p95_by_path[path] = p95
    result['p95_latency_by_path'] = p95_by_path

    # 5. slow_requests (前10，按耗时降序)
    slow_requests.sort(key=lambda x: x['latency_ms'], reverse=True)
    result['slow_requests'] = slow_requests[:10]

    # 6. tenant_error_rates
    tenant_error_rates = {}
    for tenant, total in tenant_total.items():
        err = tenant_errors.get(tenant, 0)
        rate = round(err / total, 3) if total > 0 else 0.0
        tenant_error_rates[tenant] = rate
    result['tenant_error_rates'] = tenant_error_rates

    # 额外：malformed_lines
    result['malformed_lines'] = malformed_lines

    return result


# ---------- 测试 ----------

def test_parse_line():
    """测试 parse_line 函数"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed is not None
    assert parsed['time'] == '2026-05-01T12:03:18Z'
    assert parsed['method'] == 'GET'
    assert parsed['path'] == '/api/orders'
    assert parsed['status'] == 200
    assert parsed['latency_ms'] == 123
    assert parsed['tenant'] == 'a1'
    assert parsed['raw_line'] == line

    # 带查询参数
    line2 = "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2"
    parsed2 = parse_line(line2)
    assert parsed2['path'] == '/api/orders'
    assert parsed2['status'] == 201

    # 错误行
    assert parse_line("") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms") is None
    assert parse_line("xxx") is None

    print("test_parse_line OK")


def test_full_analysis():
    """测试完整的分析功能"""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
        "2026-05-01T12:03:19Z POST /api/users 201 500ms tenant=b2",
        "2026-05-01T12:03:20Z GET /api/orders 500 1500ms tenant=a1",
        "2026-05-01T12:03:21Z GET /api/items 404 300ms tenant=c3",
        "2026-05-01T12:03:22Z GET /api/orders 200 100ms tenant=a1",
        # 慢请求应包含第3行
        # 错误行
        "broken line",
    ]
    result = run_analysis(lines)

    assert result['total_requests'] == 5
    assert result['malformed_lines'] == 1
    assert result['status_counts'] == {200: 2, 201: 1, 500: 1, 404: 1}
    assert result['top_paths'][0]['path'] == '/api/orders'
    assert result['top_paths'][0]['count'] == 3
    # p95: /api/orders 有3个耗时 [100,123,1500] 排序，n=3, 0.95*3=2.85 ceil=3，第3个是1500
    assert result['p95_latency_by_path']['/api/orders'] == 1500
    # /api/users 只有一个耗时500，p95=500
    assert result['p95_latency_by_path']['/api/users'] == 500
    # /api/items 一个耗时300，p95=300
    assert result['p95_latency_by_path']['/api/items'] == 300

    # 慢请求：只有第3行耗时1500 > 1000
    assert len(result['slow_requests']) == 1
    assert result['slow_requests'][0]['latency_ms'] == 1500
    assert result['slow_requests'][0]['path'] == '/api/orders'

    # 租户错误率
    # a1: 3请求，其中1个500错误，错误率 1/3 = 0.333, 保留三位为0.333
    # b2: 1请求无错误，0.0
    # c3: 1请求404错误，错误率1.0
    assert result['tenant_error_rates'] == {'a1': 0.333, 'b2': 0.0, 'c3': 1.0}

    print("test_full_analysis OK")


def test_many_slow():
    """测试慢请求超过10个时的截断"""
    lines = []
    for i in range(15):
        lines.append(f"2026-05-01T12:03:18Z GET /api/x 200 {1100+i}ms tenant=a1")
    result = run_analysis(lines)
    assert result['total_requests'] == 15
    assert len(result['slow_requests']) == 10
    # 耗时应该是降序 1114,1113,...,1105
    lats = [r['latency_ms'] for r in result['slow_requests']]
    assert lats == list(range(1114, 1104, -1))
    print("test_many_slow OK")


def test_empty_input():
    """测试空输入"""
    result = run_analysis([])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 0
    assert result['status_counts'] == {}
    assert result['top_paths'] == []
    assert result['p95_latency_by_path'] == {}
    assert result['slow_requests'] == []
    assert result['tenant_error_rates'] == {}
    print("test_empty_input OK")


def run_tests():
    """运行所有测试"""
    test_parse_line()
    test_full_analysis()
    test_many_slow()
    test_empty_input()
    print("所有测试通过！")


# ---------- 主入口 ----------

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    # 从标准输入读取所有行
    lines = sys.stdin.readlines()
    result = run_analysis(lines)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
