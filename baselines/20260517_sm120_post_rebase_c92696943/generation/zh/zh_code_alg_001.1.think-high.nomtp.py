too slow\n", # 错误格式，因为耗时后跟了多余内容？但按照split，会有额外字段。所以是malformed
    ]
    # 注意最后一行格式错误，应被识别为malformed
    result = compute_stats(sample_lines)
    # 预期 total_requests = 5? 实际上第1-5行中有第4行是bad line，第7行是格式错误，所以正确解析5行？再数一下：行1,2,3,5,6是正确？行3是第五行？检查：行1正确，2正确，3正确，4bad，5正确，6正确，7错误格式（因为耗时后有多余内容，split后长度>6）。所以正确解析5行，malformed=2。
    # 但行7 "2026-05-01T12:03:23Z GET /api/orders 200 1001ms tenant=a response too slow" 按空格分割得9个字段，所以malformed。
    assert result['total_requests'] == 5, f"total_requests should be 5, got {result['total_requests']}"
    assert result['malformed_lines'] == 2, f"malformed should be 2, got {result['malformed_lines']}"
    # 检查status_counts: 200出现两次? 行1:200,行2:201,行3:500,行5:404,行6:200 => 200:2, 201:1, 500:1, 404:1
    assert result['status_counts'] == {200:2, 201:1, 500:1, 404:1}
    # 检查top_paths: 路径：/api/orders出现4次（行1,2,5,6），/api/users出现1次。所以top_paths应该是[{'path':'/api/orders','count':4},{'path':'/api/users','count':1}]
    assert len(result['top_paths']) == 2
    assert result['top_paths'][0]['path'] == '/api/orders'
    assert result['top_paths'][0]['count'] == 4
    # p95_latency_by_path: /api/orders 的延迟列表：[123,456,50,150] 排序后 [50,123,150,456] n=4, pos=ceil(0.95*4)=ceil(3.8)=4, index=3 -> 456ms
    # /api/users 的延迟列表：[2000] n=1, pos=ceil(0.95)=1 -> 2000
    assert result['p95_latency_by_path']['/api/orders'] == 456
    assert result['p95_latency_by_path']['/api/users'] == 2000
    # slow_requests: 大于1000ms的行：第3行(/api/users 2000ms) 和第7行格式错误忽略。所以只有一条，latency=2000, path=/api/users
    assert len(result['slow_requests']) == 1
    assert result['slow_requests'][0]['path'] == '/api/users'
    assert result['slow_requests'][0]['latency_ms'] == 2000
    # tenant_error_rates: a1: 总请求=行1(200),行3(500),行5(404) ->3次，错误=行3(500),行5(404) ->2次，错误率=2/3≈0.667。b2: 总请求=行2(201),行6(200) ->2次，错误=0次 -> 0.0。注意租户字符串：行2 b2, 行6 b2。行7 编码错误忽略。所以a1错误率0.667, b2 0.0
    # round(2/3,3)=0.667? 2/3=0.666666..., round 三位小数得0.667. assert
    assert abs(result['tenant_error_rates']['a1'] - 0.667) < 1e-3
    assert result['tenant_error_rates']['b2'] == 0.0
    # 测试空行情况
    empty_lines = ["", "   "]
    result2 = compute_stats(empty_lines)
    assert result2['total_requests'] == 0
    assert result2['malformed_lines'] == 0 # 空行被跳过，不计数
    # 测试全部malformed
    all_bad = ["bad", "worse"]
    result3 = compute_stats(all_bad)
    assert result3['total_requests'] == 0
    assert result3['malformed_lines'] == 2
    print("All tests passed!")

if __name__ == "__main__":
    main()
```

检查上面代码：
- parse_line中，对于空行处理：我们函数内strip了，但compute_stats中先strip判定空行才调用parse_line，所以parse_line接收到的是非空行。而在parse_line内部又strip了line，导致空行也会被分割失败。但我们在compute_stats已经跳过了空行，所以没问题。但注意parse_line中strip后split，若行只含空格，也会得到0字段，返回None。不过我们跳过了，所以不会调用。
- 在slow_requests中，收集原始行(line.rstrip('\n'))，以便保留原始行。注意原始行可能包含换行符，需要去掉。
- 排序：slow_requests.sort(key=lambda x: -x[2]) 使用负数实现降序。
- top_paths: 取前5，如果少于5则全取，但排序后切片就是前5。
- p95: 使用math.ceil，当n=0时跳过。注意ceil(0.95*n)可能得到0？当n=1时，0.95 -> ceil=1，正确。当n=2时，1.9 -> ceil=2，取第二个（升序）即较大值。这是常见p95定义。但有时p95定义为百分位数，比如取线性插值，但这里明确说"排序后向上取整位置"，所以就是取第ceil(0.95*n)个（1-based）。
- tenant_error_rates: 错误率保留三位小数，用round。注意如果某个租户没有错误，返回0.0。round(0.0,3) is 0.0，JSON输出0.0。
- malformed_lines: 包括格式错误行，空行被忽略不计。

Edge: 如果某路径记录数很多，延迟列表排序可能消耗内存，但可接受。

测试函数涵盖了主要情况。注意需要import math。

确保--test参数检测：if '--test' in sys.argv。测试时可能还有其他参数，但这样简单。

关于输入：从标准输入读取，使用sys.stdin.readlines()。注意二进制模式？文本模式即可。

最后，输出JSON: 使用json.dumps(result, indent=2, ensure_ascii=False) 可读性好。但如果要求紧凑，可以去掉indent。但题目没有明确，我选择带indent以便于验证。

代码总行数约150行，远小于1000。

需要确保代码在Python3下运行。使用标准库。

另，parse_line中，对于时间戳字段我们没有验证格式，可认为只要分割成功就行。但如果有严格格式要求，可以加上简单正则。不过没必要。

输出JSON示例：

```json
{
  "total_requests": 5,
  "status_counts": {"200":2,"201":1,"500":1,"404":1},
  "top_paths": [{"path":"/api/orders","count":4},{"path":"/api/users","count":1}],
  "p95_latency_by_path": {"/api/orders":456,"/api/users":2000},
  "slow_requests": [{"line":"2026-05-01T12:03:20Z GET /api/users 500 2000ms tenant=a1","path":"/api/users","latency_ms":2000}],
  "tenant_error_rates": {"a1":0.667,"b2":0.0},
  "malformed_lines": 2
}
```

注意：状态码的key在JSON中应为字符串（因为JSON对象key必须是字符串），但python dict的key是int，json.dumps会自动转为字符串。"200"作为key。这是可接受的。

现在编写最终答案。</think>下面是符合题目要求的 Python 3 单文件程序 `log_analyzer.py`，包含完整的日志解析、统计和内置测试功能。

```python
import sys
import json
import math
from collections import defaultdict


def parse_line(line: str):
    """
    解析单行日志，返回 (path, status_code, latency_ms, tenant) 元组，
    若解析失败则返回 None。
    """
    parts = line.strip().split()
    if len(parts) != 6:
        return None
    timestamp, method, path_raw, status_str, latency_str, tenant_str = parts

    # 状态码
    try:
        status_code = int(status_str)
    except ValueError:
        return None

    # 耗时（例如 "123ms"）
    if not latency_str.endswith('ms'):
        return None
    try:
        latency_ms = int(latency_str[:-2])
    except ValueError:
        return None

    # 租户（格式 "tenant=xxx"）
    if not tenant_str.startswith('tenant='):
        return None
    tenant = tenant_str[len('tenant='):]
    if not tenant:
        return None

    # 路径去掉查询参数
    path = path_raw.split('?')[0]

    return (path, status_code, latency_ms, tenant)


def compute_stats(lines):
    """
    从日志行列表统计信息，返回结果字典。
    """
    total = 0
    malformed = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    slow_requests = []          # (原始行, 路径, 耗时)
    tenant_stats = defaultdict(lambda: {'total': 0, 'errors': 0})

    for line in lines:
        stripped = line.strip()
        if not stripped:        # 忽略空行
            continue

        parsed = parse_line(line)
        if parsed is None:
            malformed += 1
            continue

        total += 1
        path, status_code, latency_ms, tenant = parsed

        status_counts[status_code] += 1
        path_counts[path] += 1
        path_latencies[path].append(latency_ms)

        if latency_ms > 1000:
            # 保留原始行，去掉末尾换行符
            slow_requests.append((line.rstrip('\n'), path, latency_ms))

        tenant_stats[tenant]['total'] += 1
        if status_code >= 400:
            tenant_stats[tenant]['errors'] += 1

    # ----- top_paths -----
    sorted_paths = sorted(path_counts.items(), key=lambda x: -x[1])[:5]
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths]

    # ----- p95_latency_by_path -----
    p95_latency_by_path = {}
    for path, latencies in path_latencies.items():
        n = len(latencies)
        if n == 0:
            continue
        latencies.sort()
        pos = math.ceil(0.95 * n)          # 1-based 位置
        index = pos - 1                    # 转为 0-based
        p95_latency_by_path[path] = latencies[index]

    # ----- slow_requests (降序, 取前10) -----
    slow_requests.sort(key=lambda x: -x[2])
    slow_requests = slow_requests[:10]
    slow_list = [
        {'line': line, 'path': path, 'latency_ms': lat}
        for line, path, lat in slow_requests
    ]

    # ----- tenant_error_rates -----
    tenant_error_rates = {}
    for tenant, st in tenant_stats.items():
        rate = round(st['errors'] / st['total'], 3) if st['total'] > 0 else 0.0
        tenant_error_rates[tenant] = rate

    return {
        'total_requests': total,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_list,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed,
    }


def run_tests():
    """内置测试函数，当命令行参数包含 --test 时运行。"""

    # ---- 测试 parse_line ----
    line1 = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    assert parse_line(line1) == ('/api/orders', 200, 123, 'a1'), "parse_line basic"

    line2 = "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2"
    assert parse_line(line2) == ('/api/orders', 201, 456, 'b2'), "parse_line query"

    # 格式错误
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms") is None, "too few fields"
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1 extra") is None, "too many fields"
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms user=a1") is None, "wrong tenant prefix"
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123 tenant=a1") is None, "latency without ms"

    # ---- 测试 compute_stats ----
    sample = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2\n",
        "2026-05-01T12:03:20Z GET /api/users 500 2000ms tenant=a1\n",
        "bad line\n",
        "2026-05-01T12:03:21Z GET /api/orders 404 50ms tenant=a1\n",
        "2026-05-01T12:03:22Z GET /api/orders 200 150ms tenant=b2\n",
        "2026-05-01T12:03:23Z GET /api/orders 200 1001ms tenant=a response too slow\n",
    ]
    result = compute_stats(sample)

    assert result['total_requests'] == 5, f"total_requests expected 5, got {result['total_requests']}"
    assert result['malformed_lines'] == 2, f"malformed_lines expected 2, got {result['malformed_lines']}"
    assert result['status_counts'] == {200: 2, 201: 1, 500: 1, 404: 1}

    # top_paths
    assert result['top_paths'][0] == {'path': '/api/orders', 'count': 4}
    assert result['top_paths'][1] == {'path': '/api/users', 'count': 1}

    # p95
    assert result['p95_latency_by_path']['/api/orders'] == 456
    assert result['p95_latency_by_path']['/api/users'] == 2000

    # slow_requests (仅一条，2000ms)
    assert len(result['slow_requests']) == 1
    assert result['slow_requests'][0]['path'] == '/api/users'
    assert result['slow_requests'][0]['latency_ms'] == 2000

    # tenant_error_rates
    self.assertAlmostEqual(result['tenant_error_rates']['a1'], 0.667, delta=0.001)
    assert result['tenant_error_rates']['b2'] == 0.0

    # 空行测试
    res = compute_stats(["", "   "])
    assert res['total_requests'] == 0
    assert res['malformed_lines'] == 0

    # 全部格式错误
    res = compute_stats(["bad", "worse"])
    assert res['total_requests'] == 0
    assert res['malformed_lines'] == 2

    print("All tests passed!")


def main():
    if '--test' in sys.argv:
        run_tests()
        return

    lines = sys.stdin.readlines()
    result = compute_stats(lines)
    # 紧凑输出（一行），保证管道处理友好
    print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))


if __name__ == "__main__":
    main()
```

### 使用说明
- **正常运行**：从标准输入读取日志，输出 JSON 结果到标准输出。
  例：`python log_analyzer.py < access.log`
- **测试模式**：加上 `--test` 参数运行内置测试。
  例：`python log_analyzer.py --test`

### 输出 JSON 字段说明
| 字段                   | 类型     | 说明                                 |
|------------------------|----------|--------------------------------------|
| `total_requests`       | int      | 成功解析的请求总数                   |
| `status_counts`        | dict     | 状态码 -> 出现次数                   |
| `top_paths`            | list     | 请求量最高的前5个路径，含 `path` 和 `count` |
| `p95_latency_by_path`  | dict     | 路径 -> P95 延迟（毫秒整数）         |
| `slow_requests`        | list     | 耗时 >1000ms 的前10条，含原始行、路径、耗时时 |
| `tenant_error_rates`   | dict     | 租户 -> 错误率（4xx/5xx，三位小数）  |
| `malformed_lines`      | int      | 无法解析的行数                       |

### 注意事项
- 路径会去掉查询参数（`?` 后的部分）。
- 耗时字段必须严格以 `ms` 结尾，且为整数。
- 租户字段格式必须为 `tenant=<值>`，值不能为空。
- 空行被直接忽略，不计入 `malformed_lines`。
- 所有测试在函数 `run_tests()` 中通过断言验证。
