#!/usr/bin/env python3
"""
log_analyzer.py — 访问日志分析器

从标准输入读取多行访问日志，输出 JSON 统计结果。
支持 --test 参数运行内置测试。

输入格式：
    2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1
    字段顺序：ISO时间、HTTP方法、路径、状态码、耗时ms、租户
输出JSON包含：
    total_requests, status_counts, top_paths, p95_latency_by_path,
    slow_requests, tenant_error_rates, malformed_lines
"""

import sys
import json
import math
from collections import OrderedDict


# 耗时阈值（毫秒）
SLOW_THRESHOLD = 1000


def parse_line(line):
    """解析一行日志，成功返回字典，失败返回 None。"""
    line = line.strip()
    if not line:
        return None

    parts = line.split(' ')
    if len(parts) != 6:
        return None

    timestamp, method, path, status_str, latency_str, tenant_str = parts

    # 验证方法：大写字母
    if not method.isalpha() or not method.isupper():
        return None

    # 验证路径：必须 '/' 开头
    if not path.startswith('/'):
        return None

    # 验证状态码：三位数字
    if not (status_str.isdigit() and len(status_str) == 3):
        return None
    status_code = int(status_str)

    # 验证耗时：数字 + 'ms'
    if not latency_str.endswith('ms'):
        return None
    latency_part = latency_str[:-2]
    if not latency_part.isdigit():
        return None
    latency_ms = int(latency_part)

    # 验证租户：'tenant=' 开头
    if not tenant_str.startswith('tenant='):
        return None
    tenant = tenant_str[7:]  # 去掉 'tenant='
    if not tenant:
        return None

    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status_code': status_code,
        'latency_ms': latency_ms,
        'tenant': tenant,
        'original_line': line
    }


def strip_query(path):
    """去掉路径中的查询参数，返回纯净路径。"""
    if '?' in path:
        return path.split('?')[0]
    return path


def compute_p95(values):
    """计算 p95 耗时，向上取整位置（从1计数）。values 为空时返回0。"""
    if not values:
        return 0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    idx = math.ceil(n * 0.95) - 1  # 转换为 0 基索引
    if idx < 0:
        idx = 0
    return sorted_vals[idx]


def process_lines(lines):
    """处理所有日志行，返回结果字典。"""
    total = 0
    malformed = 0
    status_counts = {}
    path_counts = {}
    path_latencies = {}          # path -> list of latency_ms
    tenant_total = {}
    tenant_errors = {}
    slow_list = []               # 每个元素: {'line','path','latency_ms'}

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed += 1
            continue

        total += 1
        status = str(parsed['status_code'])
        status_counts[status] = status_counts.get(status, 0) + 1

        path_clean = strip_query(parsed['path'])
        path_counts[path_clean] = path_counts.get(path_clean, 0) + 1
        path_latencies.setdefault(path_clean, []).append(parsed['latency_ms'])

        tenant = parsed['tenant']
        tenant_total[tenant] = tenant_total.get(tenant, 0) + 1
        if parsed['status_code'] >= 400:
            tenant_errors[tenant] = tenant_errors.get(tenant, 0) + 1

        if parsed['latency_ms'] > SLOW_THRESHOLD:
            slow_list.append({
                'line': parsed['original_line'],
                'path': path_clean,
                'latency_ms': parsed['latency_ms']
            })

    # top_paths: 按 count 降序，相同按路径升序
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # p95_latency_by_path
    p95_by_path = {
        path: compute_p95(lat_list)
        for path, lat_list in path_latencies.items()
    }

    # slow_requests: 按 latency_ms 降序，取前10
    slow_list.sort(key=lambda x: -x['latency_ms'])
    slow_requests = slow_list[:10]

    # tenant_error_rates
    tenant_rates = {}
    for tenant, total_req in tenant_total.items():
        err_count = tenant_errors.get(tenant, 0)
        rate = round(err_count / total_req, 3) if total_req > 0 else 0.0
        tenant_rates[tenant] = rate

    # 构建结果，保留字段顺序
    result = OrderedDict()
    result['total_requests'] = total
    result['status_counts'] = status_counts
    result['top_paths'] = top_paths
    result['p95_latency_by_path'] = p95_by_path
    result['slow_requests'] = slow_requests
    result['tenant_error_rates'] = tenant_rates
    result['malformed_lines'] = malformed

    return result


# ------------------------------------------------------------
# 内置测试
# ------------------------------------------------------------
def _to_lines(text):
    """将多行字符串转换为行列表，每行保留换行符。"""
    return text.splitlines(keepends=True)


def test_basic():
    """基础功能测试。"""
    input_text = (
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n"
        "2026-05-01T12:03:19Z POST /api/login 201 45ms tenant=b2\n"
        "2026-05-01T12:03:20Z GET /api/orders 500 2000ms tenant=a1\n"
        "2026-05-01T12:03:21Z GET /api/orders?page=2 200 150ms tenant=c3\n"
        "malformed line\n"
    )
    lines = _to_lines(input_text)
    res = process_lines(lines)

    assert res['total_requests'] == 4
    assert res['malformed_lines'] == 1
    assert res['status_counts'] == {'200': 2, '201': 1, '500': 1}
    assert len(res['top_paths']) == 2  # /api/orders 3次, /api/login 1次
    assert res['top_paths'][0]['path'] == '/api/orders'
    assert res['top_paths'][0]['count'] == 3
    assert res['p95_latency_by_path']['/api/orders'] == 2000  # 3个值:123,150,2000，0.95*3=2.85 -> ceil=3 -> 2000
    assert res['slow_requests'][0]['latency_ms'] == 2000
    assert len(res['slow_requests']) == 1
    assert res['tenant_error_rates']['a1'] == 0.5  # 1错误/2总=0.5
    assert res['tenant_error_rates']['b2'] == 0.0
    assert res['tenant_error_rates']['c3'] == 0.0

    print("  test_basic PASSED")


def test_malformed():
    """测试各种格式错误行。"""
    input_text = (
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n"
        "short line\n"
        "2026-05-01T12:03:19Z GET /path 200 456ms tenant=b2 extra\n"
        "2026-05-01T12:03:20Z GET /path 200 456ms tenant=\n"
        "2026-05-01T12:03:21Z GET/path 200 456ms tenant=a1\n"  # 路径格式错误
        "2026-05-01T12:03:22Z GET /path 20 456ms tenant=a1\n"   # 状态码不是三位
        "2026-05-01T12:03:23Z GET /path 200 456 tenant=a1\n"    # 缺少 ms
        "2026-05-01T12:03:24Z GET /path 200 456ms no_tenant\n"  # 租户格式错误
        "2026-05-01T12:03:25Z G ET /path 200 456ms tenant=a1\n" # 方法含空格
    )
    lines = _to_lines(input_text)
    res = process_lines(lines)
    assert res['total_requests'] == 1  # 只有第一行正确
    assert res['malformed_lines'] == 8
    print("  test_malformed PASSED")


def test_p95_edge():
    """p95 边界情况测试。"""
    input_text = (
        "2026-05-01T12:00:00Z GET /path 200 10ms tenant=a1\n"
    )
    lines = _to_lines(input_text)
    res = process_lines(lines)
    assert res['p95_latency_by_path']['/path'] == 10
    print("  test_p95_edge PASSED")


def test_slow_requests_ordering():
    """慢请求排序测试。"""
    lines_text = ""
    for i in range(15):
        latency = 1500 - i * 50  # 1500,1450,...,1300,1250,... 到 800
        lines_text += f"2026-05-01T12:00:00Z GET /path 200 {latency}ms tenant=a{i}\n"
    lines = _to_lines(lines_text)
    res = process_lines(lines)
    assert len(res['slow_requests']) == 10  # 超过1000ms的: 1500,1450,...,1050,1000? 注意 >1000, 所以从1500到1050共10个? 1500-1050有10个值，1000不算。所以10个。
    # 验证顺序：降序
    for j in range(len(res['slow_requests']) - 1):
        assert res['slow_requests'][j]['latency_ms'] >= res['slow_requests'][j+1]['latency_ms']
    print("  test_slow_requests_ordering PASSED")


def test_tenant_error_rate():
    """错误率边界测试。"""
    input_text = (
        "2026-05-01T12:00:00Z GET /path 200 10ms tenant=x\n"
        "2026-05-01T12:00:01Z GET /path 304 20ms tenant=x\n"
        "2026-05-01T12:00:02Z GET /path 400 30ms tenant=y\n"
        "2026-05-01T12:00:03Z GET /path 500 40ms tenant=y\n"
        "2026-05-01T12:00:04Z GET /path 503 50ms tenant=y\n"
    )
    lines = _to_lines(input_text)
    res = process_lines(lines)
    # 租户 x: 0错误/2总=0.0
    assert res['tenant_error_rates']['x'] == 0.0
    # 租户 y: 3错误/3总=1.0
    assert res['tenant_error_rates']['y'] == 1.0
    print("  test_tenant_error_rate PASSED")


def run_tests():
    """运行所有测试。"""
    print("Running built-in tests:")
    test_basic()
    test_malformed()
    test_p95_edge()
    test_slow_requests_ordering()
    test_tenant_error_rate()
    print("All tests passed.")


# ------------------------------------------------------------
# 主入口
# ------------------------------------------------------------
def main():
    if '--test' in sys.argv:
        run_tests()
        return

    lines = sys.stdin.readlines()
    result = process_lines(lines)
    # 输出 JSON，紧凑格式
    output = json.dumps(result, ensure_ascii=False, separators=(',', ':'))
    sys.stdout.write(output)


if __name__ == "__main__":
    main()
