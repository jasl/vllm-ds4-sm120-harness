#!/usr/bin/env python3
"""
log_analyzer.py — 访问日志分析器，输出JSON统计结果。
用法：
    python log_analyzer.py < log.txt      # 从标准输入读取日志，输出JSON
    python log_analyzer.py --test         # 运行内置测试
"""

import sys
import json
import math
import re
from collections import defaultdict

# ---------- 工具函数 ----------
def parse_line(line: str):
    """
    解析单行日志，成功返回字典，失败返回None。
    字典包含: time, method, path, status, latency, tenant, raw_line
    """
    raw = line.rstrip('\n')
    parts = raw.split()
    if len(parts) != 6:
        return None

    time_str, method, path, status_str, latency_str, tenant_str = parts

    # 验证时间格式 (ISO 8601, 例如 2026-05-01T12:03:18Z)
    if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', time_str):
        return None
    # 验证 HTTP 方法
    if not re.match(r'^[A-Za-z]+$', method):
        return None
    # 路径必须以 '/' 开头
    if not path.startswith('/'):
        return None
    # 状态码必须是三位数字
    if not re.match(r'^\d{3}$', status_str):
        return None
    # 耗时格式: 数字 + "ms"
    m = re.match(r'^(\d+)ms$', latency_str)
    if not m:
        return None
    latency = int(m.group(1))
    # 租户格式: tenant=...
    if not tenant_str.startswith('tenant='):
        return None
    tenant = tenant_str[7:]  # 去掉 'tenant=' 前缀
    # 去掉路径中的查询参数
    path_clean = path.split('?', 1)[0]
    return {
        'time': time_str,
        'method': method,
        'path': path_clean,
        'status': int(status_str),
        'latency': latency,
        'tenant': tenant,
        'raw_line': raw
    }


def compute_p95(latencies):
    """计算有序列表的P95（毫秒整数），列表为空时返回None。"""
    if not latencies:
        return None
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    idx = math.ceil(n * 0.95) - 1  # 0-based 索引
    if idx < 0:
        idx = 0
    return sorted_lat[idx]


# ---------- 核心分析函数 ----------
def analyze(lines):
    """解析所有行，返回统计结果字典。"""
    # 统计数据容器
    malformed_lines = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    latencies_by_path = defaultdict(list)
    slow_requests = []
    tenant_totals = defaultdict(int)
    tenant_errors = defaultdict(int)

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue
        path = parsed['path']
        status = parsed['status']
        latency = parsed['latency']
        tenant = parsed['tenant']
        raw_line = parsed['raw_line']

        # 统计各项
        status_counts[str(status)] += 1
        path_counts[path] += 1
        latencies_by_path[path].append(latency)
        if latency > 1000:
            slow_requests.append({
                'raw_line': raw_line,
                'path': path,
                'latency': latency
            })
        tenant_totals[tenant] += 1
        if status >= 400:
            tenant_errors[tenant] += 1

    # 构造输出结果
    # 1. total_requests
    total_requests = sum(status_counts.values())

    # 2. status_counts (已统计)
    status_counts_out = dict(status_counts)

    # 3. top_paths (前5)
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths_out = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # 4. p95_latency_by_path
    p95_by_path_out = {}
    for path, lats in latencies_by_path.items():
        p95 = compute_p95(lats)
        if p95 is not None:
            p95_by_path_out[path] = p95

    # 5. slow_requests (前10，按耗时降序)
    slow_requests.sort(key=lambda x: -x['latency'])
    slow_requests_out = slow_requests[:10]

    # 6. tenant_error_rates
    tenant_error_rates_out = {}
    for tenant in tenant_totals:
        total = tenant_totals[tenant]
        errors = tenant_errors.get(tenant, 0)
        rate = round(errors / total, 3) if total > 0 else 0.0
        tenant_error_rates_out[tenant] = rate

    return {
        'total_requests': total_requests,
        'malformed_lines': malformed_lines,
        'status_counts': status_counts_out,
        'top_paths': top_paths_out,
        'p95_latency_by_path': p95_by_path_out,
        'slow_requests': slow_requests_out,
        'tenant_error_rates': tenant_error_rates_out
    }


# ---------- 测试函数 ----------
def run_tests():
    """运行内置测试，验证核心功能。"""
    # 测试 parse_line
    # 正常行
    line1 = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    p1 = parse_line(line1)
    assert p1 is not None
    assert p1['path'] == '/api/orders'
    assert p1['status'] == 200
    assert p1['latency'] == 123
    assert p1['tenant'] == 'a1'

    # 带查询参数
    line2 = "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a2"
    p2 = parse_line(line2)
    assert p2 is not None
    assert p2['path'] == '/api/orders'

    # 异常行: 字段数不对
    assert parse_line("short line") is None
    # 异常行: 时间格式错误
    assert parse_line("2026-05-01 12:03:18 GET /path 200 123ms tenant=a") is None
    # 异常行: 状态码非数字
    assert parse_line("2026-05-01T12:03:18Z GET /path abc 123ms tenant=a") is None
    # 异常行: 耗时格式错误
    assert parse_line("2026-05-01T12:03:18Z GET /path 200 abms tenant=a") is None
    # 异常行: 缺少tenant前缀
    assert parse_line("2026-05-01T12:03:18Z GET /path 200 123ms foo=a") is None

    # 测试 analyze 基本统计
    test_lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
        "2026-05-01T12:03:19Z POST /api/login 401 50ms tenant=b2",
        "2026-05-01T12:03:20Z GET /api/orders?sort=desc 200 150ms tenant=a1",
        "2026-05-01T12:03:21Z DELETE /api/users 500 2000ms tenant=a1",
        "malformed line",
        "2026-05-01T12:03:22Z GET /api/orders 200 1200ms tenant=c3",   # 慢请求
        "2026-05-01T12:03:23Z PUT /api/profile 403 80ms tenant=b2",
        "2026-05-01T12:03:24Z POST /api/login 200 90ms tenant=a1",
        "2026-05-01T12:03:25Z GET /api/orders 200 100ms tenant=a1",   # 重复路径
    ]
    result = analyze(test_lines)

    # 基本数值检查
    assert result['total_requests'] == 7  # 8条，1条malformed
    assert result['malformed_lines'] == 1
    assert result['status_counts'] == {'200': 4, '401': 1, '500': 1, '403': 1}
    # top_paths: /api/orders 出现4次, /api/login 2次, /api/users 1次, /api/profile 1次
    assert len(result['top_paths']) == 4
    assert result['top_paths'][0]['path'] == '/api/orders'
    assert result['top_paths'][0]['count'] == 4

    # p95: /api/orders有4个延时: 123,150,1200,100 -> 排序后 [100,123,150,1200]
    # n=4, ceil(4*0.95)=4, idx=3 -> 1200
    assert result['p95_latency_by_path']['/api/orders'] == 1200
    # /api/login: [50,90] -> n=2, ceil(1.9)=2, idx=1 -> 90
    assert result['p95_latency_by_path']['/api/login'] == 90
    # /api/users: [2000] -> n=1, ceil(0.95)=1, idx=0 -> 2000
    assert result['p95_latency_by_path']['/api/users'] == 2000
    # /api/profile: [80] -> 80
    assert result['p95_latency_by_path']['/api/profile'] == 80

    # slow_requests: 耗时>1000的: DELETE /api/users (2000ms), GET /api/orders (1200ms)
    assert len(result['slow_requests']) == 2
    # 降序，第一个2000ms，第二个1200ms
    assert result['slow_requests'][0]['latency'] == 2000
    assert result['slow_requests'][1]['latency'] == 1200
    # 原始行应包含完整字符串
    assert 'DELETE' in result['slow_requests'][0]['raw_line']
    assert 'GET' in result['slow_requests'][1]['raw_line']

    # tenant_error_rates: a1:总请求4 (status:200,200,500,200) 错误1个(500) -> 0.25
    # b2: 2请求，错误2个(401,403) -> 1.0
    # c3: 1请求，错误0 -> 0.0
    assert result['tenant_error_rates']['a1'] == 0.25
    assert result['tenant_error_rates']['b2'] == 1.0
    assert result['tenant_error_rates']['c3'] == 0.0

    print("所有测试通过！")


# ---------- 主入口 ----------
def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    lines = sys.stdin.read().splitlines()
    result = analyze(lines)
    # 输出紧凑JSON（无多余空格）
    print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))


if __name__ == '__main__':
    main()
