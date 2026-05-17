#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
log_analyzer.py - 日志分析器
从标准输入读取访问日志，统计相关信息并输出JSON。
支持 --test 参数运行内置测试。
"""

import sys
import json
import math
from collections import Counter, defaultdict


def parse_line(line):
    """
    解析一行日志。
    输入 line 可能包含换行符，但函数会先去除末尾换行。
    返回 (clean_path, status, latency, tenant, original_line) 或 None (无法解析)。
    """
    original_line = line.rstrip('\r\n')
    parts = original_line.split()
    if len(parts) < 6:
        return None

    # 只取前6个字段，忽略后面可能出现的多余字段
    timestamp, method, path, status_str, latency_str, tenant_str = parts[:6]

    # 状态码必须为整数
    try:
        status = int(status_str)
    except ValueError:
        return None

    # 耗时毫秒必须以 "ms" 结尾
    if not latency_str.endswith('ms'):
        return None
    try:
        latency = int(latency_str[:-2])
    except ValueError:
        return None

    # 租户字段解析：取第一个等号后的内容，如果没有等号则整段视为租户名
    if '=' in tenant_str:
        tenant = tenant_str.split('=', 1)[1]
    else:
        tenant = tenant_str

    # 路径去掉查询参数
    clean_path = path.split('?')[0]

    return (clean_path, status, latency, tenant, original_line)


def process_logs(input_stream):
    """
    从输入流读取所有行，解析并统计。
    返回一个包含所有统计结果的字典。
    """
    total = 0
    malformed = 0
    status_counts = Counter()
    path_counts = Counter()
    path_latencies = defaultdict(list)
    tenant_total = defaultdict(int)
    tenant_errors = defaultdict(int)
    slow_requests = []          # 元素 (latency, original_line, clean_path)

    for line in input_stream:
        parsed = parse_line(line)
        if parsed is None:
            malformed += 1
            continue

        clean_path, status, latency, tenant, orig_line = parsed
        total += 1
        status_counts[status] += 1
        path_counts[clean_path] += 1
        path_latencies[clean_path].append(latency)
        tenant_total[tenant] += 1
        if status >= 400:
            tenant_errors[tenant] += 1
        if latency > 1000:                      # 严格大于 1000ms
            slow_requests.append((latency, orig_line, clean_path))

    # ---------- 计算输出结果 ----------
    # 1. top_paths：请求量前5的路径
    top_items = sorted(path_counts.items(),
                       key=lambda x: (-x[1], x[0]))[:5]
    top_paths = [{"path": p, "count": c} for p, c in top_items]

    # 2. p95_latency_by_path：每个路径的p95耗时
    p95 = {}
    for path, lats in path_latencies.items():
        sorted_lats = sorted(lats)
        n = len(sorted_lats)
        idx = math.ceil(0.95 * n) - 1            # 向上取整后的索引（0-based）
        p95[path] = sorted_lats[idx]

    # 3. slow_requests：耗时 >1000ms 的前10条，按耗时降序
    slow_requests.sort(key=lambda x: -x[0])      # 按耗时降序
    slow_top10 = slow_requests[:10]
    slow_list = [
        {"original_line": line, "path": p, "latency": lat}
        for lat, line, p in slow_top10
    ]

    # 4. tenant_error_rates：每个租户的错误率
    error_rates = {}
    for tenant, cnt in tenant_total.items():
        errs = tenant_errors.get(tenant, 0)
        rate = round(errs / cnt, 3) if cnt > 0 else 0.0
        error_rates[tenant] = rate

    # 为了可预测的输出顺序，对字典按键排序
    result = {
        "total_requests": total,
        "status_counts": dict(sorted(status_counts.items())),
        "top_paths": top_paths,
        "p95_latency_by_path": dict(sorted(p95.items())),
        "slow_requests": slow_list,
        "tenant_error_rates": dict(sorted(error_rates.items())),
        "malformed_lines": malformed
    }
    return result


def run_tests():
    """内置测试函数，使用 assert 验证关键行为。"""
    import io

    # ---------- Test 1: 基础功能 ----------
    test1_input = (
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n"
        "2026-05-01T12:03:19Z GET /api/orders 200 456ms tenant=a1\n"
        "2026-05-01T12:03:20Z GET /api/orders 500 200ms tenant=a2\n"
        "2026-05-01T12:03:21Z POST /api/users 404 150ms tenant=a1\n"
        "2026-05-01T12:03:22Z GET /api/items 200 1000ms tenant=a3\n"
        "invalid line\n"
        "2026-05-01T12:03:23Z GET /api/orders 200 1100ms tenant=a2\n"
        "2026-05-01T12:03:24Z GET /api/orders?page=2 200 300ms tenant=a1\n"
    )
    result1 = process_logs(io.StringIO(test1_input))
    assert result1["total_requests"] == 7, "total_requests should be 7"
    assert result1["malformed_lines"] == 1, "malformed_lines should be 1"
    assert result1["status_counts"] == {200: 4, 404: 1, 500: 1}, "status_counts mismatch"
    expected_top1 = [
        {"path": "/api/orders", "count": 4},
        {"path": "/api/items", "count": 1},
        {"path": "/api/users", "count": 1}
    ]
    assert result1["top_paths"] == expected_top1, "top_paths mismatch"
    assert result1["p95_latency_by_path"] == {
        "/api/orders": 1100, "/api/items": 1000, "/api/users": 150
    }, "p95 mismatch"
    # 慢请求只有一条（latency=1100）
    assert len(result1["slow_requests"]) == 1, "should have 1 slow request"
    slow1 = result1["slow_requests"][0]
    assert slow1["latency"] == 1100, "slow request latency"
    assert slow1["path"] == "/api/orders", "slow request path"
    assert slow1["original_line"] == (
        "2026-05-01T12:03:23Z GET /api/orders 200 1100ms tenant=a2"
    ), "slow request original_line"
    assert result1["tenant_error_rates"] == {
        "a1": 0.25, "a2": 0.5, "a3": 0.0
    }, "tenant_error_rates mismatch"
    print("Test 1 (basic) passed.")

    # ---------- Test 2: 空输入 ----------
    result2 = process_logs(io.StringIO(""))
    assert result2["total_requests"] == 0
    assert result2["status_counts"] == {}
    assert result2["top_paths"] == []
    assert result2["p95_latency_by_path"] == {}
    assert result2["slow_requests"] == []
    assert result2["tenant_error_rates"] == {}
    assert result2["malformed_lines"] == 0
    print("Test 2 (empty input) passed.")

    # ---------- Test 3: 全部为非法行 ----------
    result3 = process_logs(io.StringIO("bad line\nanother garbage\n"))
    assert result3["total_requests"] == 0
    assert result3["malformed_lines"] == 2
    print("Test 3 (all malformed) passed.")

    # ---------- Test 4: top_paths 截断为5 ----------
    lines4 = []
    # path0 出现3次, path1 2次, path2~path5 各1次  => 共6个不同路径
    for i in range(3):
        lines4.append(f"2026-05-01T12:00:0{i}Z GET /api/path0 200 10ms tenant=x")
    for i in range(2):
        lines4.append(f"2026-05-01T12:00:1{i}Z GET /api/path1 200 10ms tenant=x")
    for i in range(2, 6):
        lines4.append(f"2026-05-01T12:00:{i}Z GET /api/path{i} 200 10ms tenant=x")
    result4 = process_logs(io.StringIO("\n".join(lines4)))
    top4 = result4["top_paths"]
    assert len(top4) == 5, "top_paths should have 5 entries"
    expected_top4 = [
        {"path": "/api/path0", "count": 3},
        {"path": "/api/path1", "count": 2},
        {"path": "/api/path2", "count": 1},
        {"path": "/api/path3", "count": 1},
        {"path": "/api/path4", "count": 1},
    ]
    assert top4 == expected_top4, f"top_paths mismatch: {top4}"
    print("Test 4 (top_paths limit) passed.")

    # ---------- Test 5: slow_requests 排序与截断 ----------
    lines5 = []
    # 20个慢请求，latency 从 1001 到 1020
    for i in range(20):
        lat = 1001 + i
        lines5.append(f"2026-05-01T12:00:00Z GET /api/test 200 {lat}ms tenant=x")
    result5 = process_logs(io.StringIO("\n".join(lines5)))
    slow5 = result5["slow_requests"]
    assert len(slow5) == 10, "slow_requests should have 10 entries"
    lats5 = [item["latency"] for item in slow5]
    # 验证降序
    assert lats5 == sorted(lats5, reverse=True), "slow_requests not in descending order"
    expected_lats5 = list(range(1020, 1000, -1))[:10]   # 1020,1019,...,1011
    assert lats5 == expected_lats5, f"slow latencies mismatch: {lats5}"
    print("Test 5 (slow requests sorting/truncation) passed.")

    # ---------- Test 6: 错误率精度 ----------
    lines6 = [
        "2026-01-01T00:00:00Z GET /test 200 100ms tenant=t1",   # 正常
        "2026-01-01T00:00:01Z GET /test 404 100ms tenant=t1",   # 错误
        "2026-01-01T00:00:02Z GET /test 500 100ms tenant=t1",   # 错误
        "2026-01-01T00:00:03Z GET /test 200 100ms tenant=t2",   # 正常
        "2026-01-01T00:00:04Z GET /test 503 100ms tenant=t2",   # 错误
        "2026-01-01T00:00:05Z GET /test 200 100ms tenant=t2",   # 正常
    ]
    result6 = process_logs(io.StringIO("\n".join(lines6)))
    rates6 = result6["tenant_error_rates"]
    assert rates6["t1"] == round(2/3, 3), f"t1 rate should be 0.667, got {rates6['t1']}"
    assert rates6["t2"] == round(1/3, 3), f"t2 rate should be 0.333, got {rates6['t2']}"
    print("Test 6 (error rate precision) passed.")

    # ---------- Test 7: 租户字段无等号 ----------
    line7 = "2026-01-01T00:00:00Z GET /api/test 200 100ms mytenant\n"
    parsed7 = parse_line(line7)
    assert parsed7 is not None, "parse_line returned None for valid line"
    _, _, _, tenant7, _ = parsed7
    assert tenant7 == "mytenant", f"tenant should be 'mytenant', got '{tenant7}'"
    print("Test 7 (tenant without equals) passed.")

    # ---------- Test 8: p95 边界情况 (N=3) ----------
    lines8 = [
        "2026-01-01T00:00:00Z GET /a 200 100ms tenant=t",
        "2026-01-01T00:00:01Z GET /a 200 200ms tenant=t",
        "2026-01-01T00:00:02Z GET /a 200 300ms tenant=t",
    ]
    result8 = process_logs(io.StringIO("\n".join(lines8)))
    assert result8["p95_latency_by_path"] == {"/a": 300}, \
        f"p95 mismatch: {result8['p95_latency_by_path']}"
    print("Test 8 (p95 boundary) passed.")

    print("All tests passed!")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    result = process_logs(sys.stdin)
    # 紧凑 JSON 输出，不包含多余空格
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(',', ':')))
    sys.stdout.write('\n')


if __name__ == "__main__":
    main()
