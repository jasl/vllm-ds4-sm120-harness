#!/usr/bin/env python3
"""
log_analyzer.py - 访问日志分析工具

用法：
    python log_analyzer.py < input.log          # 分析并输出 JSON
    python log_analyzer.py --test               # 运行内置测试
"""

import sys
import json
import math
from collections import defaultdict


def parse_line(line):
    """
    解析单行日志。

    参数：
        line: 字符串，不带换行符的日志行。

    返回：
        成功返回元组 (时间, 方法, 路径, 状态码, 耗时, 租户)；
        失败返回 None。
    """
    try:
        fields = line.split()
        if len(fields) != 6:
            return None

        time_str = fields[0]          # ISO 时间戳，不做严格检查
        method = fields[1]
        raw_path = fields[2]          # 可能包含查询参数
        # 去除查询参数
        path = raw_path.split('?')[0]
        status = int(fields[3])
        latency_str = fields[4]
        if not latency_str.endswith('ms'):
            return None
        latency = int(latency_str[:-2])
        tenant_field = fields[5]
        if '=' not in tenant_field:
            return None
        tenant = tenant_field.split('=', 1)[1]   # 允许空租户
        return (time_str, method, path, status, latency, tenant)
    except (ValueError, IndexError):
        return None


def process_lines(lines):
    """
    处理日志行列表（每行带换行符），生成统计数据。

    参数：
        lines: 可迭代对象，元素为原始日志行（带换行符）。

    返回：
        包含所有统计信息的字典。
    """
    total = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    slow_requests = []               # (耗时, 原始行, 路径)
    tenant_total = defaultdict(int)
    tenant_errors = defaultdict(int)
    malformed = 0

    for raw_line in lines:
        line_stripped = raw_line.rstrip('\n\r')
        # 空行跳过，不计入 malformed
        if not line_stripped:
            continue

        parsed = parse_line(line_stripped)
        if parsed is None:
            malformed += 1
            continue

        _, _, path, status, latency, tenant = parsed

        total += 1
        status_counts[status] += 1
        path_counts[path] += 1
        path_latencies[path].append(latency)
        if latency > 1000:
            slow_requests.append((latency, raw_line, path))
        tenant_total[tenant] += 1
        if status >= 400:
            tenant_errors[tenant] += 1

    # 请求量最高的前 5 个路径
    sorted_paths = sorted(path_counts.items(),
                          key=lambda x: (-x[1], x[0]))[:5]
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths]

    # 每个路径的 p95 耗时（毫秒，整数）
    p95_by_path = {}
    for path, latencies in path_latencies.items():
        latencies.sort()
        n = len(latencies)
        idx = math.ceil(0.95 * n) - 1      # 转为 0‑based 索引
        if idx < 0:
            idx = 0
        p95_by_path[path] = latencies[idx]

    # 耗时 > 1000ms 的前 10 条（降序）
    sorted_slow = sorted(slow_requests, key=lambda x: -x[0])[:10]
    slow_requests_out = [
        {
            'raw_line': raw,
            'path': path,
            'latency_ms': lat
        }
        for lat, raw, path in sorted_slow
    ]

    # 每个租户的错误率（4xx/5xx 视为错误）
    tenant_rates = {}
    for tenant, tot in tenant_total.items():
        err = tenant_errors.get(tenant, 0)
        rate = round(err / tot, 3) if tot > 0 else 0.0
        tenant_rates[tenant] = rate

    return {
        'total_requests': total,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests_out,
        'tenant_error_rates': tenant_rates,
        'malformed_lines': malformed
    }


def run_tests():
    """内置测试。全部通过则输出成功信息并退出 0，否则抛出 AssertionError。"""

    # ---------- parse_line 测试 ----------
    # 正常行
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    r = parse_line(line)
    assert r is not None
    assert r[0] == "2026-05-01T12:03:18Z"
    assert r[1] == "GET"
    assert r[2] == "/api/orders"
    assert r[3] == 200
    assert r[4] == 123
    assert r[5] == "a1"

    # 路径带查询参数
    line = "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2"
    r = parse_line(line)
    assert r is not None
    assert r[2] == "/api/orders"

    # 状态码非数字
    line = "2026-05-01T12:03:18Z GET /api/orders abc 123ms tenant=a1"
    assert parse_line(line) is None

    # 耗时格式错误（缺少 ms 后缀）
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123 tenant=a1"
    assert parse_line(line) is None

    # 租户字段缺少等号
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms badtenant"
    assert parse_line(line) is None

    # 字段数不足
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms"
    assert parse_line(line) is None

    # 空行 / 空白行
    assert parse_line("") is None
    assert parse_line("   ") is None

    # 额外字段
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1 extra"
    assert parse_line(line) is None

    # ---------- process_lines 整体测试 ----------
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2\n",
        "2026-05-01T12:03:20Z GET /api/users 200 789ms tenant=a1\n",
        "2026-05-01T12:03:21Z GET /api/orders 200 100ms tenant=c3\n",
        "2026-05-01T12:03:22Z GET /api/items 500 1200ms tenant=a1\n",
        "malformed line\n",
        "2026-05-01T12:03:23Z DELETE /api/orders 204 50ms tenant=b2\n",
        "2026-05-01T12:03:24Z GET /api/orders 304 60ms tenant=a1\n",
        "2026-05-01T12:03:25Z GET /api/users 404 30ms tenant=c3\n",
        "2026-05-01T12:03:26Z PUT /api/orders 200 200ms tenant=a1\n",
        "2026-05-01T12:03:27Z GET /api/orders 200 150ms tenant=a1\n",
        "2026-05-01T12:03:28Z GET /api/orders 200 140ms tenant=a1\n",
        "2026-05-01T12:03:29Z GET /api/orders 200 130ms tenant=a1\n",
        "2026-05-01T12:03:30Z GET /api/orders 200 110ms tenant=a1\n",
        "2026-05-01T12:03:31Z GET /api/orders 200 120ms tenant=a1\n",
        "2026-05-01T12:03:32Z GET /api/orders 200 125ms tenant=a1\n",
        "2026-05-01T12:03:33Z GET /api/orders 200 135ms tenant=a1\n",
        "2026-05-01T12:03:34Z GET /api/orders 200 145ms tenant=a1\n",
        "2026-05-01T12:03:35Z GET /api/orders 200 155ms tenant=a1\n",
        "2026-05-01T12:03:36Z GET /api/orders 200 165ms tenant=a1\n",
    ]
    out = process_lines(lines)

    # 基本统计
    assert out['total_requests'] == 20
    assert out['malformed_lines'] == 1

    # 状态码分布
    sc = out['status_counts']
    assert sc[200] == 14
    assert sc[201] == 1
    assert sc[500] == 1
    assert sc[204] == 1
    assert sc[304] == 1
    assert sc[404] == 1

    # 热门路径
    tp = out['top_paths']
    assert tp[0]['path'] == '/api/orders'
    assert tp[0]['count'] == 16
    path_map = {item['path']: item['count'] for item in tp}
    assert path_map['/api/users'] == 2
    assert path_map['/api/items'] == 1

    # p95 延迟
    p95 = out['p95_latency_by_path']
    # /api/orders：16 个值，p95 索引 = ceil(0.95*16) = 16 → 第 16 个值（排序后最大）
    assert p95['/api/orders'] == 456
    # /api/users：2 个值，p95 取较大值
    assert p95['/api/users'] == 789
    # /api/items：1 个值
    assert p95['/api/items'] == 1200

    # 慢请求
    sr = out['slow_requests']
    assert len(sr) == 1
    assert sr[0]['latency_ms'] == 1200
    assert sr[0]['path'] == '/api/items'
    assert sr[0]['raw_line'].rstrip('\n\r') == (
        "2026-05-01T12:03:22Z GET /api/items 500 1200ms tenant=a1"
    )

    # 租户错误率
    tr = out['tenant_error_rates']
    assert abs(tr['a1'] - 0.067) < 0.001     # 1/15 ≈ 0.0667 → 0.067
    assert tr['b2'] == 0.0
    assert tr['c3'] == 0.5

    # ---------- 边界情况 ----------
    # 空输入
    out = process_lines([])
    assert out['total_requests'] == 0
    assert out['malformed_lines'] == 0
    assert out['status_counts'] == {}
    assert out['top_paths'] == []
    assert out['p95_latency_by_path'] == {}
    assert out['slow_requests'] == []
    assert out['tenant_error_rates'] == {}

    # 全部损坏
    out = process_lines(["bad line\n", "also bad\n"])
    assert out['total_requests'] == 0
    assert out['malformed_lines'] == 2

    # 空行应跳过（不计 malformed）
    out = process_lines([
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "\n",
        "   \n",
        "2026-05-01T12:03:19Z POST /api/data 201 456ms tenant=b2\n",
    ])
    assert out['total_requests'] == 2
    assert out['malformed_lines'] == 0

    print("All tests passed!")


def main():
    """程序入口。"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        sys.exit(0)

    # 正常模式：从标准输入读取，输出 JSON
    lines = sys.stdin.readlines()
    output = process_lines(lines)
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
