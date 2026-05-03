# Generation Transcript

- Case: `zh_code_alg_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 39.158659
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 338, "total_tokens": 2832, "completion_tokens": 2494, "prompt_tokens_details": null}`
- Prompt tokens: 338
- Completion tokens: 2494
- Total tokens: 2832

## Prompt

```markdown
请使用 Python 3 编写一个单文件命令行程序，文件名假定为 `log_analyzer.py`，不使用第三方库，总代码不超过1000行。

输入：从标准输入读取多行访问日志，每行格式如下：
`2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1`
字段依次为：ISO时间、HTTP方法、路径、状态码、耗时毫秒、租户。路径可能包含查询参数，例如 `/api/orders?page=2`，统计时应去掉查询参数。

任务：输出一个 JSON 对象，包含：
1. `total_requests`：总请求数。
2. `status_counts`：按状态码统计。
3. `top_paths`：请求量最高的前5个路径，含 `path` 和 `count`。
4. `p95_latency_by_path`：每个路径的 p95 耗时，毫秒整数。p95定义为排序后向上取整位置。
5. `slow_requests`：耗时大于1000ms的前10条，按耗时降序，保留原始行、路径、耗时。
6. `tenant_error_rates`：每个租户的错误率，4xx/5xx 算错误，保留三位小数。

要求：
- 跳过无法解析的行，并在输出中给出 `malformed_lines` 数量。
- 代码结构清晰，包含若干内置测试函数；当使用 `--test` 参数运行时执行测试。
- 正常运行时只输出 JSON，不输出解释文字。
```

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""
log_analyzer.py - 访问日志分析器

用法:
    python log_analyzer.py < logfile.txt
    python log_analyzer.py --test

从标准输入读取日志行，分析后输出 JSON 结果。
"""

import sys
import json
import math
from collections import defaultdict


def parse_line(line):
    """
    解析单行日志。
    成功时返回 (timestamp, method, path, status, latency_ms, tenant) 元组。
    失败时返回 None。
    """
    parts = line.strip().split()
    if len(parts) < 6:
        return None

    try:
        timestamp = parts[0]
        method = parts[1]
        path_raw = parts[2]
        status = int(parts[3])
        latency_str = parts[4]
        tenant = parts[5]
    except (IndexError, ValueError):
        return None

    # 验证 latency 格式 (ms)
    if not latency_str.endswith('ms'):
        return None
    try:
        latency = int(latency_str[:-2])
    except ValueError:
        return None

    # 验证 tenant 格式 (key=value)
    if '=' not in tenant:
        return None
    tenant_parts = tenant.split('=')
    if len(tenant_parts) != 2 or tenant_parts[0] != 'tenant':
        return None
    tenant = tenant_parts[1]

    # 去除路径中的查询参数
    path = path_raw.split('?')[0]

    # 验证状态码范围 (100-599)
    if status < 100 or status > 599:
        return None

    return (timestamp, method, path, status, latency, tenant)


def percentile(sorted_data, p):
    """
    计算已排序数据的 p 百分位值（整数）。
    p95 定义：排序后索引为 ceil(p/100 * N) - 1。
    """
    if not sorted_data:
        return 0
    n = len(sorted_data)
    # 向上取整位置
    idx = int(math.ceil(p / 100.0 * n)) - 1
    idx = max(0, min(idx, n - 1))
    return sorted_data[idx]


def analyze_logs(lines):
    """
    分析日志行列表，返回结果字典。
    """
    total = 0
    malformed = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    slow_requests = []
    tenant_data = defaultdict(lambda: {"total": 0, "error": 0})

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed += 1
            continue

        timestamp, method, path, status, latency, tenant = parsed
        total += 1

        # 状态码统计
        status_counts[status] += 1

        # 路径统计
        path_counts[path] += 1

        # 路径耗时记录
        path_latencies[path].append(latency)

        # 慢请求收集
        if latency > 1000:
            slow_requests.append({
                "raw_line": line.strip(),
                "path": path,
                "latency_ms": latency
            })

        # 租户错误统计
        tenant_data[tenant]["total"] += 1
        if status >= 400:
            tenant_data[tenant]["error"] += 1

    # 按路径请求量降序排序，取前5
    sorted_paths = sorted(path_counts.items(), key=lambda x: -x[1])
    top_paths = [{"path": p, "count": c} for p, c in sorted_paths[:5]]

    # 每个路径的 p95 延迟
    p95_by_path = {}
    for path, latencies in path_latencies.items():
        sorted_lat = sorted(latencies)
        p95_by_path[path] = percentile(sorted_lat, 95)

    # 慢请求排序：按延迟降序，取前10
    slow_requests_sorted = sorted(slow_requests, key=lambda x: -x["latency_ms"])[:10]

    # 租户错误率（保留三位小数）
    tenant_error_rates = {}
    for tenant, data in tenant_data.items():
        if data["total"] > 0:
            rate = data["error"] / data["total"]
        else:
            rate = 0.0
        tenant_error_rates[tenant] = round(rate, 3)

    result = {
        "total_requests": total,
        "status_counts": dict(status_counts),
        "top_paths": top_paths,
        "p95_latency_by_path": p95_by_path,
        "slow_requests": slow_requests_sorted,
        "tenant_error_rates": tenant_error_rates,
        "malformed_lines": malformed
    }

    return result


# ===================== 内置测试 =====================

def run_tests():
    """运行所有测试用例"""
    passed = 0
    failed = 0

    # 测试用例: (输入行列表, 预期结果字段检查函数)
    test_cases = []

    # Test 1: 基本有效日志
    lines1 = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
        "2026-05-01T12:03:19Z POST /api/users 201 50ms tenant=b2",
    ]
    def check1(result):
        return (result["total_requests"] == 2 and
                result["malformed_lines"] == 0 and
                result["status_counts"].get(200) == 1 and
                result["status_counts"].get(201) == 1 and
                result["tenant_error_rates"].get("a1") == 0.0)
    test_cases.append((lines1, check1, "基本两条日志"))

    # Test 2: 包含查询参数的路径
    lines2 = [
        "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1",
        "2026-05-01T12:03:19Z GET /api/orders 200 100ms tenant=a1",
    ]
    def check2(result):
        return (result["total_requests"] == 2 and
                result["top_paths"][0]["path"] == "/api/orders" and
                result["top_paths"][0]["count"] == 2)
    test_cases.append((lines2, check2, "查询参数去除"))

    # Test 3: 错误行和格式错误
    lines3 = [
        "invalid line without enough fields",
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
        "2026-05-01T12:03:19Z GET /api/items 404 50ms tenant=c3",
    ]
    def check3(result):
        return (result["total_requests"] == 2 and
                result["malformed_lines"] == 1 and
                result["status_counts"].get(404) == 1 and
                result["tenant_error_rates"]["c3"] == 1.0)
    test_cases.append((lines3, check3, "错误行和404"))

    # Test 4: 慢请求
    lines4 = [
        "2026-05-01T12:03:18Z GET /api/orders 200 2000ms tenant=a1",
        "2026-05-01T12:03:19Z GET /api/items 200 500ms tenant=a1",
        "2026-05-01T12:03:20Z GET /api/orders 200 1500ms tenant=a1",
    ]
    def check4(result):
        return (len(result["slow_requests"]) == 2 and
                result["slow_requests"][0]["latency_ms"] == 2000 and
                result["slow_requests"][1]["latency_ms"] == 1500)
    test_cases.append((lines4, check4, "慢请求筛选排序"))

    # Test 5: p95 计算验证
    lines5 = [
        f"2026-05-01T12:03:18Z GET /api/data 200 {i}ms tenant=t1"
        for i in range(1, 21)
    ]
    def check5(result):
        # 20个延迟 1..20，p95索引 ceil(0.95*20)-1 = 19-1=18 => 第19个元素(1-indexed) = 19
        return result["p95_latency_by_path"]["/api/data"] == 19
    test_cases.append((lines5, check5, "p95计算"))

    # Test 6: 没有有效行
    lines6 = ["completely invalid line", "also invalid"]
    def check6(result):
        return (result["total_requests"] == 0 and
                result["malformed_lines"] == 2 and
                len(result["top_paths"]) == 0)
    test_cases.append((lines6, check6, "完全无效行"))

    # Test 7: 多种状态码和错误率
    lines7 = [
        "2026-05-01T12:03:18Z GET /api/a 200 10ms tenant=t1",
        "2026-05-01T12:03:19Z GET /api/b 404 10ms tenant=t1",
        "2026-05-01T12:03:20Z GET /api/a 500 10ms tenant=t2",
        "2026-05-01T12:03:21Z GET /api/a 200 10ms tenant=t2",
    ]
    def check7(result):
        return (result["tenant_error_rates"]["t1"] == 0.5 and
                result["tenant_error_rates"]["t2"] == 0.5)
    test_cases.append((lines7, check7, "错误率计算"))

    # 执行测试
    for i, (lines, check_func, desc) in enumerate(test_cases, 1):
        try:
            result = analyze_logs(lines)
            if check_func(result):
                print(f"  ✓ 测试 {i}: {desc}")
                passed += 1
            else:
                print(f"  ✗ 测试 {i}: {desc} - 结果不符合预期")
                failed += 1
        except Exception as e:
            print(f"  ✗ 测试 {i}: {desc} - 抛出异常: {e}")
            failed += 1

    print(f"\n总计: {passed} 通过, {failed} 失败")
    return passed, failed


# ===================== 主程序 =====================

def main():
    if "--test" in sys.argv:
        print("运行内置测试...\n")
        run_tests()
        sys.exit(0)

    lines = sys.stdin.readlines()
    result = analyze_logs(lines)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```
````
