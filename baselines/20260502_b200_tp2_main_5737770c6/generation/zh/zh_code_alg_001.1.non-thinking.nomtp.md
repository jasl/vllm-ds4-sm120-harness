# Generation Transcript

- Case: `zh_code_alg_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 24.9354
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 338, "total_tokens": 3048, "completion_tokens": 2710, "prompt_tokens_details": null}`
- Prompt tokens: 338
- Completion tokens: 2710
- Total tokens: 3048

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
我来创建一个完整的日志分析器程序。这个程序将处理标准输入的访问日志，并输出所需的统计信息。

```python
#!/usr/bin/env python3
"""
log_analyzer.py - 访问日志分析器

从标准输入读取访问日志并输出统计分析结果。
"""

import sys
import json
import re
from collections import Counter, defaultdict


def parse_line(line):
    """解析单行日志，成功返回元组，失败返回None"""
    line = line.rstrip('\n\r')
    try:
        # 使用正则表达式解析日志行
        pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) (GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) (\S+) (\d{3}) (\d+)ms tenant=(\S+)$'
        match = re.match(pattern, line)
        if not match:
            return None

        timestamp = match.group(1)
        method = match.group(2)
        full_path = match.group(3)
        status_code = int(match.group(4))
        latency = int(match.group(5))
        tenant = match.group(6)

        # 去掉查询参数
        path = full_path.split('?')[0] if '?' in full_path else full_path

        return {
            'timestamp': timestamp,
            'method': method,
            'path': path,
            'full_path': full_path,
            'status_code': status_code,
            'latency': latency,
            'tenant': tenant,
            'original_line': line
        }
    except (ValueError, IndexError, AttributeError):
        return None


def calculate_p95(values):
    """计算p95值，采用向上取整位置"""
    if not values:
        return 0
    sorted_values = sorted(values)
    index = int((len(sorted_values) - 1) * 0.95)
    # 向上取整
    if index < len(sorted_values) - 1 and index != (len(sorted_values) - 1) * 0.95:
        index = int((len(sorted_values) - 1) * 0.95) + 1
    index = min(index, len(sorted_values) - 1)
    return sorted_values[index]


def analyze_logs(lines):
    """分析日志行，返回统计结果"""
    total_requests = 0
    malformed_lines = 0
    status_counts = Counter()
    path_counts = Counter()
    path_latencies = defaultdict(list)
    slow_requests = []
    tenant_error_counts = defaultdict(int)
    tenant_total_counts = defaultdict(int)

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue

        total_requests += 1
        status_counts[parsed['status_code']] += 1
        path_counts[parsed['path']] += 1
        path_latencies[parsed['path']].append(parsed['latency'])

        if parsed['latency'] > 1000:
            slow_requests.append({
                'original_line': parsed['original_line'],
                'path': parsed['path'],
                'latency': parsed['latency']
            })

        if parsed['status_code'] >= 400:
            tenant_error_counts[parsed['tenant']] += 1
        tenant_total_counts[parsed['tenant']] += 1

    # 统计top_paths
    top_paths = [{'path': path, 'count': count}
                 for path, count in path_counts.most_common(5)]

    # 统计p95_latency_by_path
    p95_latency_by_path = {}
    for path, latencies in path_latencies.items():
        p95_latency_by_path[path] = calculate_p95(latencies)

    # 统计slow_requests
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_requests[:10]

    # 统计tenant_error_rates
    tenant_error_rates = {}
    for tenant in set(list(tenant_error_counts.keys()) + list(tenant_total_counts.keys())):
        if tenant_total_counts[tenant] > 0:
            rate = tenant_error_counts.get(tenant, 0) / tenant_total_counts[tenant]
            tenant_error_rates[tenant] = round(rate, 3)
        else:
            tenant_error_rates[tenant] = 0.0

    return {
        'total_requests': total_requests,
        'malformed_lines': malformed_lines,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates
    }


def run_tests():
    """运行内置测试"""
    # 测试1: 解析正常行
    print("测试1: 解析正常行")
    test_line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    result = parse_line(test_line)
    assert result is not None
    assert result['timestamp'] == "2026-05-01T12:03:18Z"
    assert result['method'] == "GET"
    assert result['path'] == "/api/orders"
    assert result['status_code'] == 200
    assert result['latency'] == 123
    assert result['tenant'] == "a1"
    print("  通过")

    # 测试2: 解析有查询参数的行
    print("测试2: 解析有查询参数的行")
    test_line = "2026-05-01T12:03:18Z POST /api/orders?page=2&limit=10 201 456ms tenant=b2"
    result = parse_line(test_line)
    assert result is not None
    assert result['path'] == "/api/orders"
    assert result['full_path'] == "/api/orders?page=2&limit=10"
    print("  通过")

    # 测试3: 解析错误格式的行
    print("测试3: 解析错误格式的行")
    test_line = "invalid line format"
    result = parse_line(test_line)
    assert result is None
    print("  通过")

    # 测试4: 解析不同HTTP方法
    print("测试4: 解析不同HTTP方法")
    test_line = "2026-05-01T12:03:18Z DELETE /api/users/123 204 50ms tenant=c3"
    result = parse_line(test_line)
    assert result is not None
    assert result['method'] == "DELETE"
    print("  通过")

    # 测试5: 解析错误状态码
    print("测试5: 解析错误状态码")
    test_line = "2026-05-01T12:03:18Z GET /api/error 500 200ms tenant=d4"
    result = parse_line(test_line)
    assert result is not None
    assert result['status_code'] == 500
    assert result['latency'] == 200
    print("  通过")

    # 测试6: P95计算
    print("测试6: P95计算")
    values = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    p95 = calculate_p95(values)
    assert p95 == 950  # (len-1) * 0.95 = 8.55, 向上取整为9, index=9 -> 950
    print("  通过")

    # 测试7: 空列表P95
    print("测试7: 空列表P95")
    p95 = calculate_p95([])
    assert p95 == 0
    print("  通过")

    # 测试8: 小样本P95
    print("测试8: 小样本P95")
    values = [100, 200]
    p95 = calculate_p95(values)
    assert p95 == 200  # (2-1) * 0.95 = 0.95, 向上取整到1, values[1] = 200
    print("  通过")

    # 测试9: 完整分析流程
    print("测试9: 完整分析流程")
    test_lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1",
        "2026-05-01T12:03:19Z POST /api/orders 201 456ms tenant=b2",
        "2026-05-01T12:03:20Z GET /api/users 200 50ms tenant=a1",
        "2026-05-01T12:03:21Z GET /api/orders 500 2000ms tenant=c3",
        "malformed line",
        "2026-05-01T12:03:22Z GET /api/error 404 100ms tenant=b2",
    ]
    result = analyze_logs(test_lines)
    assert result['total_requests'] == 5
    assert result['malformed_lines'] == 1
    assert result['status_counts'][200] == 2
    assert result['status_counts'][500] == 1
    assert len(result['top_paths']) == 3
    assert result['p95_latency_by_path']['/api/orders'] == 2000
    assert len(result['slow_requests']) == 1
    assert result['slow_requests'][0]['latency'] == 2000
    print("  通过")

    # 测试10: 租户错误率统计
    print("测试10: 租户错误率统计")
    error_lines = [
        "2026-05-01T12:03:18Z GET /api/test 200 100ms tenant=a1",
        "2026-05-01T12:03:19Z GET /api/test 404 100ms tenant=a1",
        "2026-05-01T12:03:20Z GET /api/test 500 100ms tenant=a1",
        "2026-05-01T12:03:21Z GET /api/test 200 100ms tenant=b2",
    ]
    result = analyze_logs(error_lines)
    assert result['tenant_error_rates']['a1'] == round(2/3, 3)
    assert result['tenant_error_rates']['b2'] == 0.0
    print("  通过")

    print("\n所有测试通过!")


def main():
    """主函数"""
    # 检查是否运行测试
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    # 读取标准输入
    lines = sys.stdin.readlines()

    # 分析日志
    result = analyze_logs(lines)

    # 输出JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
```

这个程序实现了所有要求的统计功能：

1. **`total_requests`**: 记录所有成功解析的请求数
2. **`malformed_lines`**: 记录无法解析的行数
3. **`status_counts`**: 按状态码统计请求数量
4. **`top_paths`**: 请求量最高的前5个路径（去掉查询参数后）
5. **`p95_latency_by_path`**: 每个路径的p95耗时（整数）
6. **`slow_requests`**: 耗时>1000ms的前10条（按耗时降序）
7. **`tenant_error_rates`**: 每个租户的错误率（保留三位小数）

使用说明：
- 正常运行时：`python log_analyzer.py < access.log`
- 运行测试时：`python log_analyzer.py --test`

程序特点：
- 不依赖第三方库
- 代码结构清晰，包含10个测试用例
- 使用正则表达式解析日志行
- 正确处理带查询参数的路径
- 跳过无法解析的行并统计数量
````
