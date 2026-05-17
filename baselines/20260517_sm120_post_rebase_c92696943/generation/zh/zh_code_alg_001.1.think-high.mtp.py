#!/usr/bin/env python3
"""log_analyzer.py - 单文件命令行日志分析器"""

import sys
import json
import math
from collections import defaultdict
from datetime import datetime


def parse_line(line: str) -> dict | None:
    """
    解析单行日志，返回字典（包含 path, status_code, latency, tenant, line）
    若格式错误返回 None。
    """
    parts = line.strip().split()
    if len(parts) != 6:
        return None

    time_str, method, path_str, status_str, latency_str, tenant_str = parts

    # 验证时间格式
    try:
        datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None

    # 验证并提取状态码
    try:
        status_code = int(status_str)
    except ValueError:
        return None

    # 验证并提取耗时（毫秒）
    if not latency_str.endswith("ms"):
        return None
    try:
        latency = int(latency_str[:-2])
    except ValueError:
        return None

    # 提取租户
    if not tenant_str.startswith("tenant="):
        return None
    tenant = tenant_str[7:]  # 去掉 "tenant=" 前缀

    # 路径去掉查询参数
    path = path_str.split("?")[0]

    return {
        "line": line.strip(),
        "path": path,
        "status_code": status_code,
        "latency": latency,
        "tenant": tenant,
    }


def compute_stats(lines: list[str]) -> dict:
    """
    对解析后的原始行列表进行统计，返回结果字典。
    """
    requests = []
    malformed = 0

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed += 1
        else:
            requests.append(parsed)

    total_requests = len(requests)
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    slow_requests = []               # 原始慢请求列表（未排序）
    tenant_errors = defaultdict(int)  # 每个租户的错误数
    tenant_total = defaultdict(int)   # 每个租户的总请求数

    for req in requests:
        status = req["status_code"]
        status_counts[status] += 1
        path = req["path"]
        path_counts[path] += 1
        path_latencies[path].append(req["latency"])

        tenant = req["tenant"]
        tenant_total[tenant] += 1
        if status >= 400:
            tenant_errors[tenant] += 1

        if req["latency"] > 1000:
            slow_requests.append({
                "line": req["line"],
                "path": path,
                "latency": req["latency"],
            })

    # 慢请求按耗时降序，取前10
    slow_requests.sort(key=lambda x: x["latency"], reverse=True)
    slow_requests = slow_requests[:10]

    # 请求最多的前5个路径
    sorted_paths = sorted(path_counts.items(), key=lambda kv: kv[1], reverse=True)
    top_paths = [{"path": p, "count": c} for p, c in sorted_paths[:5]]

    # 每个路径的P95耗时（毫秒整数）
    p95_by_path = {}
    for path, lat_list in path_latencies.items():
        n = len(lat_list)
        lat_list.sort()
        # 向上取整位置：第 ceil(0.95 * n) 个 (1-based)
        pos = int(math.ceil(0.95 * n))
        index = max(pos - 1, 0)  # 转换为 0-based 索引
        p95_by_path[path] = lat_list[index]

    # 每个租户的错误率（保留三位小数）
    tenant_error_rates = {}
    for tenant in tenant_total:
        total = tenant_total[tenant]
        errors = tenant_errors[tenant]
        rate = round(errors / total, 3) if total > 0 else 0.0
        tenant_error_rates[tenant] = rate

    result = {
        "total_requests": total_requests,
        "status_counts": dict(status_counts),
        "top_paths": top_paths,
        "p95_latency_by_path": p95_by_path,
        "slow_requests": slow_requests,
        "tenant_error_rates": tenant_error_rates,
        "malformed_lines": malformed,
    }
    return result


# ---------- 测试 ----------
def test_parse_line():
    """测试解析函数"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    result = parse_line(line)
    assert result is not None
    assert result["path"] == "/api/orders"
    assert result["status_code"] == 200
    assert result["latency"] == 123
    assert result["tenant"] == "a1"
    assert result["line"] == line

    # 带查询参数
    line2 = "2026-05-01T12:03:19Z POST /api/users?page=2 201 45ms tenant=b2"
    r2 = parse_line(line2)
    assert r2["path"] == "/api/users"

    # 格式错误（字段数不足）
    assert parse_line("invalid line") is None

    # 时间错误
    assert parse_line("abc GET /x 200 1ms tenant=t") is None

    # 状态码非数字
    assert parse_line("2026-05-01T12:03:18Z GET /x abc 1ms tenant=t") is None

    # 耗时缺少 ms
    assert parse_line("2026-05-01T12:03:18Z GET /x 200 123 tenant=t") is None

    # 租户前缀错误
    assert parse_line("2026-05-01T12:03:18Z GET /x 200 123ms user=x") is None

    print("  test_parse_line: PASS")


def test_compute_stats():
    """测试统计功能"""
    lines = [
        "2026-05-01T12:00:00Z GET /api/orders 200 100ms tenant=a1",
        "2026-05-01T12:00:01Z GET /api/orders 200 200ms tenant=a1",
        "2026-05-01T12:00:02Z GET /api/users  400 50ms tenant=b2",
        "2026-05-01T12:00:03Z POST /api/orders 500 1500ms tenant=a1",
        "2026-05-01T12:00:04Z GET /api/orders 200 300ms tenant=c3",
        # 错误行（将被跳过）
        "broken line",
    ]
    stats = compute_stats(lines)

    assert stats["total_requests"] == 5
    assert stats["malformed_lines"] == 1
    assert stats["status_counts"] == {200: 3, 400: 1, 500: 1}

    # top_paths
    assert len(stats["top_paths"]) >= 2  # 实际有2个不同路径
    # 路径 /api/orders 出现4次，/api/users 出现1次
    top1 = stats["top_paths"][0]
    assert top1["path"] == "/api/orders"
    assert top1["count"] == 4

    # P95 测试： /api/orders 耗时 [100,200,300,1500] → 4个，0.95*4=3.8 → ceil=4 → 第4个（索引3） = 1500
    p95 = stats["p95_latency_by_path"]
    assert p95["/api/orders"] == 1500
    # /api/users 只有1个耗时50 → 0.95*1=0.95→ceil=1→索引0 → 50
    assert p95["/api/users"] == 50

    # slow_requests: 只有1个 >1000ms
    assert len(stats["slow_requests"]) == 1
    sr = stats["slow_requests"][0]
    assert sr["latency"] == 1500
    assert sr["path"] == "/api/orders"

    # tenant_error_rates
    rates = stats["tenant_error_rates"]
    # a1: 请求4个（1个500错误），错误率 1/4 = 0.25
    assert abs(rates["a1"] - 0.25) < 1e-9
    # b2: 1个请求，400错误，错误率 1.0
    assert rates["b2"] == 1.0
    # c3: 1个请求，200正常，错误率 0.0
    assert rates["c3"] == 0.0

    print("  test_compute_stats: PASS")


def test_empty_input():
    """测试空输入"""
    stats = compute_stats([])
    assert stats["total_requests"] == 0
    assert stats["malformed_lines"] == 0
    assert stats["status_counts"] == {}
    assert stats["top_paths"] == []
    assert stats["p95_latency_by_path"] == {}
    assert stats["slow_requests"] == []
    assert stats["tenant_error_rates"] == {}
    print("  test_empty_input: PASS")


def test_all_malformed():
    """测试全部行均错误"""
    lines = ["bad1", "bad2 bad2", "123 123 123 123 123"]
    stats = compute_stats(lines)
    assert stats["total_requests"] == 0
    assert stats["malformed_lines"] == 3
    print("  test_all_malformed: PASS")


def run_tests():
    """运行所有测试"""
    print("Running tests...")
    test_parse_line()
    test_compute_stats()
    test_empty_input()
    test_all_malformed()
    print("All tests passed.")


# ---------- 主入口 ----------
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    input_lines = sys.stdin.read().splitlines()
    stats = compute_stats(input_lines)
    print(json.dumps(stats, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
