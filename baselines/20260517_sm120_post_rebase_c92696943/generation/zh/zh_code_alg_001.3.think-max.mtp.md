# Generation Transcript

- Case: `zh_code_alg_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 122.454746
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 417, "total_tokens": 21655, "completion_tokens": 21238, "prompt_tokens_details": null}`
- Prompt tokens: 417
- Completion tokens: 21238
- Total tokens: 21655

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

## Reasoning Content

````text
我们被要求编写一个单文件命令行程序 `log_analyzer.py`，用 Python 3，不使用第三方库，代码不超过1000行。功能是从标准输入读取多行日志，解析并输出 JSON 对象包含指定的统计信息。还要包含内置测试函数，当使用 `--test` 参数运行时执行测试，正常运行时只输出 JSON。

要求非常具体。我们需要设计程序逻辑，包括解析每行、处理异常、计算统计量。

首先，解析每一行：格式为 ISO时间 方法 路径 状态码 耗时ms 租户。字段间以空格分隔，但注意路径可能包含查询参数，我们需要去掉查询参数（即?后面的部分）。耗时字段是数字后跟"ms"，如"123ms"。租户字段是"tenant=a1"。我们需要提取出各个字段。可能存在格式不正确的行，跳过，并计数为 malformed_lines。

统计：

- total_requests: 总有效请求数。
- status_counts: 按状态码计数。
- top_paths: 请求量最高的前5个路径（path after removing query string），包括 path 和 count。
- p95_latency_by_path: 每个路径的 p95 耗时，毫秒整数。p95定义为排序后向上取整位置。解释：对于每个路径的耗时列表，排序后，取第 ceil(N * 0.95) 个位置的值（1-indexed）。如果N=0，可以忽略（实际上有请求的路径都应该有，但可能没有请求？不会出现因为是有请求才统计的）。需要输出每个路径的 p95。如果路径没有数据？应该每个请求都有路径，所以所有路径都会被包含。但如果有路径只有少数几个请求？也要计算。
- slow_requests: 耗时大于1000ms的前10条，按耗时降序，保留原始行、路径、耗时。输出应该是列表，每个元素包含 raw_line（原始行）、path（去参路径）、latency（毫秒整数）。注意原始行需要完整保留，但为了安全，可能要去除尾部换行。
- tenant_error_rates: 每个租户的错误率，4xx/5xx 算错误，保留三位小数。应该是输出每个租户的错误比例（错误请求数/总请求数）。

另外，malformed_lines 数量需要包含在输出中。

输出 JSON 对象，包含这些字段。

需要处理排序等。

边缘情况：路径可能为空？可能的日志行有多种异常。假设每行都是字符串，解析失败则跳过。

关于 p95 的定义：“p95定义为排序后向上取整位置”。通常 p95 是第 ceil(0.95 * N) 个排序后的值（索引从1开始）。例如 N=10，0.95*10=9.5 ceil=10，所以取第10个（最大值）。如果 N=1，ceil(0.95)=1，取第1个。所以正确。

对于 slow_requests，如果多于10条，只取前10按耗时降序。如果不足10条，则全部。

tenant_error_rates 保留三位小数，应该是字符串格式还是数字？JSON 输出时应该是数字，但可以控制小数位数。使用 round 可能产生浮点误差，但要求保留三位小数，可以输出为 float，但确保最多三位小数。我们可以使用 format 但 JSON 标准允许数字，所以我们直接输出 round(error_rate, 3) 即可。

要求“正常运行时只输出 JSON，不输出解释文字。”所以如果使用 --test 参数，运行测试并输出测试结果（可能是简单的 assert 并打印成功信息），但不能输出 JSON。我们需要在 main 中根据参数决定行为。

内置测试函数：使用 --test 参数运行时，执行一些测试用例验证函数正确性。测试可以包括解析行、p95 计算等。

代码结构清晰：定义函数进行解析、统计，然后输出 JSON。

不允许使用第三方库，所以使用标准库 json, sys, collections, math, itertools 等。

总代码不超过1000行，应该没问题。

让我们规划代码结构：

1. 定义解析函数 `parse_line(line)`，返回一个 dict 或 None 如果无法解析。
2. 定义统计函数或直接在 main 中循环。
3. 定义计算 p95 的函数。
4. 定义测试函数 `run_tests()`。
5. main 入口：检查 sys.argv 是否包含 "--test"，如果是执行测试；否则从 stdin 读取行，处理，输出 JSON。

需要考虑性能：可能大量日志，但用 Python 处理还是可以的。

输入格式：每行包含字段：timestamp method path status_code latency_ms tenant。字段以空格分隔。但是路径可能包含空格吗？通常路径不含空格，但我们可以假设空格分隔。但是路径如果有查询参数，包含?，不会影响空格。所以我们可以用 split() 分割为多个部分。但字段个数固定为6个？看例子：`2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1`。用空格分割会得到6个字段。但是路径可能含有空格吗？URL 不包含空格，所以安全。但查询参数可能包含空格？不，都是 URL 编码。所以我们的简单 split 可能 OK。但我们需要考虑如果行格式错误（比如缺少字段），则跳过。

但注意：路径字段可能包含查询字符串如 `/api/orders?page=2`，所以我们提取第三个字段，然后去除 ? 及之后的部分（使用 split('?')[0]）。如果路径为空？我们保持原样。

耗时字段：类似 "123ms"，需要去掉 "ms" 转为 int。如果格式不对跳过。

状态码：转为 int。

租户字段：如 "tenant=a1"，需要去掉 "tenant=" 前缀，保留值。也可能没有？格式固定。

所以解析函数：

def parse_line(line):
    parts = line.strip().split()
    if len(parts) != 6:
        return None
    try:
        timestamp = parts[0]
        method = parts[1]
        path_full = parts[2]
        status = int(parts[3])
        latency_str = parts[4]
        # 检查耗时是否以 ms 结尾
        if not latency_str.endswith('ms'):
            return None
        latency = int(latency_str[:-2])
        tenant_part = parts[5]
        if not tenant_part.startswith('tenant='):
            return None
        tenant = tenant_part[7:]
        # 提取路径（去除查询参数）
        path = path_full.split('?')[0]
    except (ValueError, IndexError):
        return None
    # 可能还需要检查 time 格式？不严格，格式不对也算 malformed？但是我们只解析必要字段，timestamp 不验证。
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status,
        'latency': latency,
        'tenant': tenant,
        'raw': line.strip()  # 保留原始行用于 slow_requests
    }

但是注意，原始行可能包含头尾空格，我们保留 raw 作为 line.strip() 或原样？最好保留原始行但不包含换行。定义为原行（去掉换行）。我们可以在读取时使用 .rstrip('\n') 保留其他空白？但无所谓，raw 用于输出，只要一致。

下面循环读取 sys.stdin 的每一行，调用 parse_line，如果返回 None 则 malformed_lines 计数加1，否则加入请求列表。

我们不需要保留所有请求的详细信息，只需要根据需要统计。但是需要每个路径的 latency 列表用于 p95，需要每个租户的错误计数，需要慢请求列表，需要 top_paths 计数。所以我们可以逐步处理：

- total_requests 计数
- status_counts: dict[int,int]
- path_counts: dict[str,int] 用于 top_paths
- path_latencies: dict[str,list[int]] 或者我们可以只存储排序后的？但需要所有值来计算 p95，所以必须存储所有延迟值（或者批量处理时排序）。数据量可能很大，但必须存储。如果路径很多，可以用字典的列表。
- tenant_error_counts: dict[str,int] 和 total_requests per tenant: dict[str,int]
- slow_requests: 列表，只保留前10个最慢的？可以在处理中动态维护：使用一个最小堆保持 top 10 最大的。但为了简单，我们可以先收集所有 slow_requests（耗时>1000）到一个列表，最后排序取前10。因为慢请求通常是少数，所以这个列表可能不大。或者谨慎起见，使用堆。但我们现在先用列表收集，最后排序。

由于我们还需要每个路径的 p95，所以需要存储每个路径的所有延迟。这可能导致内存消耗大，但题目没有特殊说明，且路径数量有限（一般）。如果请求数很大，存储所有延迟可能内存大，但这是必要的。我们可以用字典的列表。或者我们可以用数组列表。

为了优化，我们可以用 `path_latencies: dict[str, list]`。

然后解析完成后，计算统计。

p95 计算：对于每个路径，如果延迟列表为空（理论上不会，因为有请求就该有路径），则忽略。否则排序，取 ceil(N*0.95) 索引（1-based）。设为 k = math.ceil(N * 0.95)，然后取排序后第 k-1 个（0-based）。注意：可能 k > N，但 ceil(0.95*N) <= N? 当 N=0 时无意义，N>=1 时 ceil(0.95*N) 最大为 N（如 N=1，ceil(0.95)=1；N=20, ceil(19)=19, 19<=20）。所以索引有效。

**慢请求**：筛选 latency > 1000 的记录，按 latency 降序排序，取前10个。每个输出 raw_line, path, latency。注意 raw_line 是原始字符串，需包含。

**tenant_error_rates**：错误定义为状态码 4xx 或 5xx。对于每个租户，错误数 / 请求总数，保留三位小数。注意：租户可能没有请求？不会。但要考虑如果租户总请求0，错误率0？但不会出现。

**top_paths**：按 count 降序，取前5个。如果相同 count，可任意顺序？要求不明确，可以选择按 count 降序，如果并列可以按路径字母排序？但题目只要求 top 5，没有说明 tie-breaking，所以我们可以按 count 降序，再按路径字母升序（可选）来保证确定性。但非必须。我们简单按 count 降序，再按路径（或原始顺序）排序。但为了稳定，我们可以用 sorted 指定 key = lambda x: (-x[1], x[0])。

输出 JSON。使用 json.dumps 输出，indent？不需要缩进？正常运行时只输出 JSON，没有规定缩进。我们可以输出紧凑或美观。但通常对于日志分析，可以输出美观。但只要有 JSON 就行，不一定需要缩进。但为了可读性，可以使用 indent=2。但注意：单文件即可。

测试：写一些测试用例，包括正常解析、p95 计算、top_paths、慢请求等。测试函数可以简单使用 assert 测试，如果全部通过打印"All tests passed." 或其他。

我们还需要考虑 `--test` 参数。如果出现 `--test` 在任何位置？一般第一个参数。但也可以任何。我们检查 sys.argv[1:] 是否包含 '--test'。

代码总行数不超过1000，很宽松。

现在开始写代码。

注意：P95 定义：排序后向上取整位置。例如 N=10，排序后第9或第10？0.95*10=9.5，向上取整得10，所以取第10个。N=9: 0.95*9=8.55 ceil=9 取第9个。所以索引公式： idx = math.ceil(N * 0.95) - 1。

**关于路径包含查询参数**：去掉查询参数，如 `/api/orders?page=2` 变成 `/api/orders`。如果路径包含多个 ? 只取第一个 ? 之前。

**关于原始行保留**：我们要在输出中显示原行，但可能包含前导/后缀空格。一般 strip 掉空格后使用。我们存储 raw = line.strip()。

**处理耗时单位 ms**：必须确保耗时结尾是 ms，但可能有负数？不可能。我们解析 int，如果异常则跳过。

**状态码**：必须为整数，4xx 错误包括 400-499, 5xx 500-599。

**也许还有其他字段？** 格式固定6个字段。每行字段都有租户。所以我们将 tenant_part[7:] 提取。

**关于空行**：跳过空行？parse_line 会返回 None（因为 split 后 count 为0）。所以计入 malformed_lines。

**性能考虑**：逐行读取 sys.stdin 是可迭代的。

输出 JSON 时，要求包含以下字段：

- total_requests
- status_counts: dict (status code -> count)
- top_paths: list of objects with "path" and "count"
- p95_latency_by_path: dict (path -> p95 integer)
- slow_requests: list of objects with "raw_line", "path", "latency"
- tenant_error_rates: dict (tenant -> float)
- malformed_lines: int

我们按此输出。

在 JSON 输出中，键名应与要求一致，如 "slow_requests" 中是否需要 "raw_line" 或 "raw_line"? 要求写“保留原始行、路径、耗时”，可以理解为对象包含 "raw_line", "path", "latency"。我们使用 "raw_line" 作为键。

示例：对于 slow_requests，每个元素包含三个字段。我们使用 snake_case 以便与要求一致。

现在，编码：

```python
#!/usr/bin/env python3
import sys
import json
import math
import collections

def parse_line(line):
    # 忽略空行
    stripped = line.strip()
    if not stripped:
        return None
    parts = stripped.split()
    if len(parts) != 6:
        return None
    try:
        timestamp = parts[0]
        method = parts[1]
        path_full = parts[2]
        status_code = int(parts[3])
        latency_str = parts[4]
        # 检查耗时是否为数字ms
        if not latency_str.endswith('ms'):
            return None
        latency = int(latency_str[:-2])
        tenant_part = parts[5]
        if not tenant_part.startswith('tenant='):
            return None
        tenant = tenant_part[7:]
        # 提取路径（去除查询参数）
        path = path_full.split('?')[0]
    except (ValueError, IndexError):
        return None
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status_code,
        'latency': latency,
        'tenant': tenant,
        'raw': stripped
    }

def compute_p95(latencies):
    """计算给定延迟列表的p95（毫秒整数）"""
    if not latencies:
        return 0  # 不该发生
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    idx = math.ceil(n * 0.95) - 1
    # 确保索引有效
    if idx < 0:
        idx = 0
    if idx >= n:
        idx = n - 1
    return sorted_lat[idx]

def run_tests():
    """测试核心函数"""
    # 测试 parse_line
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    result = parse_line(line)
    assert result is not None
    assert result['timestamp'] == "2026-05-01T12:03:18Z"
    assert result['method'] == "GET"
    assert result['path'] == "/api/orders"
    assert result['status'] == 200
    assert result['latency'] == 123
    assert result['tenant'] == "a1"
    assert result['raw'] == line

    # 测试带查询参数的路径
    line2 = "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2"
    result2 = parse_line(line2)
    assert result2['path'] == "/api/orders"
    assert result2['latency'] == 456
    assert result2['tenant'] == "b2"

    # 测试malformed line
    bad_line = "malformed line"
    assert parse_line(bad_line) is None

    # 测试空行
    assert parse_line("") is None

    # 测试字段数量不对
    assert parse_line("2026-05-01T12:03:18Z GET /path 200 123ms") is None

    # 测试耗时格式错误
    assert parse_line("2026-05-01T12:03:18Z GET /path 200 123abc tenant=a1") is None

    # 测试租户格式错误
    assert parse_line("2026-05-01T12:03:18Z GET /path 200 123ms tenant=a1") is not None  # 正确
    assert parse_line("2026-05-01T12:03:18Z GET /path 200 123ms no tenant") is None

    # 测试compute_p95
    # 空列表
    assert compute_p95([]) == 0
    # 单元素
    assert compute_p95([100]) == 100
    # 样本：N=10, 延迟从1到10，95%分位应该是10（因为ceil(9.5)=10）
    latencies = list(range(1, 11))
    assert compute_p95(latencies) == 10
    # N=9, 1-9, ceil(8.55)=9, 取第9个（9）
    assert compute_p95(list(range(1,10))) == 9
    # N=20, 1-20, ceil(19)=19, 第19个是19
    assert compute_p95(list(range(1,21))) == 19
    # 随机测试
    import random
    random.seed(123)
    for n in [1,2,3,4,5,10,100]:
        lats = [random.randint(1,1000) for _ in range(n)]
        sorted_lats = sorted(lats)
        idx = math.ceil(n * 0.95) - 1
        if idx < 0: idx = 0
        assert compute_p95(lats) == sorted_lats[idx]

    print("All tests passed.")

def main():
    if '--test' in sys.argv[1:]:
        run_tests()
        return

    # 解析 stdin
    total_requests = 0
    malformed_lines = 0
    status_counts = collections.Counter()
    path_counts = collections.Counter()
    path_latencies = collections.defaultdict(list)
    # 租户请求数和错误数
    tenant_requests = collections.Counter()
    tenant_errors = collections.Counter()
    # 慢请求列表（>1000ms）
    slow_requests = []

    # 可选：如果行数很大，可以使用 sys.stdin.buffer 等，但直接用 sys.stdin 文本即可
    for line in sys.stdin:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue
        total_requests += 1
        status_counts[parsed['status']] += 1
        path_counts[parsed['path']] += 1
        path_latencies[parsed['path']].append(parsed['latency'])
        tenant = parsed['tenant']
        tenant_requests[tenant] += 1
        if 400 <= parsed['status'] < 600:
            tenant_errors[tenant] += 1
        # 慢请求：耗时>1000
        if parsed['latency'] > 1000:
            slow_requests.append({
                'raw_line': parsed['raw'],
                'path': parsed['path'],
                'latency': parsed['latency']
            })

    # 计算 top_paths: 前5个
    # 按count降序，然后path升序（可选）
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # 计算 p95_by_path
    p95_by_path = {}
    for path, lats in path_latencies.items():
        p95_by_path[path] = compute_p95(lats)

    # 慢请求排序取前10
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_requests[:10]

    # 租户错误率
    tenant_error_rates = {}
    for tenant in tenant_requests:
        total = tenant_requests[tenant]
        errors = tenant_errors.get(tenant, 0)
        rate = round(errors / total, 3) if total > 0 else 0.0
        tenant_error_rates[tenant] = rate

    # 构建输出
    output = {
        'total_requests': total_requests,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }

    # 输出 JSON
    # 按一般要求，输出紧凑或美观？这里我们选择美观缩进2空格
    # 注意：题目没有指定，所以任意。但输出仅JSON。
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

但是这里有一个问题：p95 定义向上取整位置，我们之前用 math.ceil(N*0.95) - 1。但是当 N*0.95 正好是整数时，比如 N=20, 0.95*20=19, ceil(19)=19，取第19个索引18值。这是标准的"向上取整位置"，意味着如果 N*0.95 是整数，则取该位置（19）。实际上 "向上取整位置" 对该定义可能模糊：通常 p95 是排序后位置为 0.95*(N-1)+1 等，但这里明确说了“向上取整位置”，所以我的理解可能正确。我们再看要求："p95定义为排序后向上取整位置。" 所以直接 ceil(0.95*N) 作为位置（1-indexed）。所以我们的公式正确。

另外，当 N=0 时，不应该出现，但为了安全返回0。

现在，我们还需要考虑输出为 JSON 时，status_counts 的键是数字，JSON 自动转成字符串? 实际上 Python dict 的键是整数时，json.dumps 会转换成字符串，因为 JSON 对象的键必须是字符串。这点没问题，输出后会是字符串形式。但要求中 status_counts 是“按状态码统计”，所以输出应该是数字到计数的映射。在 JSON 中键是字符串，但我们可以接受。如果要求是数字键，可以用数字但 JSON 标准中键是字符串，但大部分解析器会处理。所以没问题。

但是注意：有些 JSON 实现期望键是字符串，所以输出字符串也正常。

同样，p95_latency_by_path 的键是路径字符串，是字符串。

现在，测试计算 p95 时，我们使用了随机数种子，但 Python 自带 random，不是第三方库，允许。

在 run_tests 中，我们可能还需要测试慢请求排序等功能，但基本测试即可。

另外，注意：当有慢请求时，raw_line 包含原始行。我们存储 raw 为 stripped。但原始行可能包含前导/后置空格，但我们去除了。这应该可以。

还有一个细节：在统计租户错误率时，对于没有错误的租户，错误率应该为0.0，但我们已经处理了。

我们还需考虑：如果租户的 total 很多，但 error 是0，那么 round(0/total, 3) 是 0.0，正确。

现在我们检查是否满足所有要求：

- total_requests: 正确
- status_counts: 作为 dict
- top_paths: 前5，包含 path 和 count
- p95_latency_by_path: 每个路径 p95 整数
- slow_requests: 前10耗时>1000，降序，含 raw_line, path, latency
- tenant_error_rates: 每个租户错误率保留三位小数

- 跳过无法解析的行，输出 malformed_lines 数量

- 代码结构清晰，包含内置测试函数；当使用 `--test` 参数运行时执行测试。

- 正常运行时只输出 JSON

另外，要求路径可能包含查询参数，统计时应去掉查询参数，我们做了。

我们还可能需要处理状态码范围错误，状态码作为整数，但可能有非数字？我们在 parse 中转换，如果不是整数则返回 None。

我们现在看看范围：当路径可能包含多个 `?` 时，我们只取第一个 ? 之前。例如 `/a?b?c` 变成 `/a`，这是合理的。

关于原始行保留：我们保留的是 strip() 后，可能去除了前后空格。可能保留原行更好？但原始行可能包含前导/后空格，一般不会有。我们也可以保留 line.strip() 以便前后一致。如果要保留原行（含前后空格），可以使用 line.rstrip('\n') 但保留右侧空格？但左侧空格可能会影响，一般没有。决定使用strip() 输出干净的行。要求说“保留原始行”，可能指原样显示。但通常日志文件没有前导空格，所以 strip 没问题。我们明确：如果行有前导空格，我们会去掉，但可能改变了原始行。不过题目没有严格要求必须原样。我们考虑保留原行（包括前导空白和尾部换行以外的空白）。可以修改 parse_line 返回 raw = line.rstrip('\n') 或者 line[:-1] 如果最后是换行。但为了简化，我们直接用 strip 但会丢失前后空白。但日志一般无前导空白，所以影响不大。我们为了更准确，可以用 line.rstrip('\n') 去掉换行，但保留其他空白。这更接近原始行。我们修改 parse_line：传入 line，但读取时 line 包含换行符，我们可以用 line.rstrip('\n') 得到原行（保留其他空白）。注意如果行末尾有 \r\n 也会处理。但通常 sys.stdin 打开文本模式，换行符统一为 '\n'。所以我们可以在 main 中 line = line.rstrip('\n') 或更彻底：使用 line.rstrip('\r\n')? 最简单是 line.rstrip('\n') 但可能还有 \r。我们使用 line.rstrip('\r\n') 来同时处理 Windows。或者使用 line.strip() 则去除两端空白，包括空格、制表符等。题目没有明确，建议保留原样（只删除行结束符）。我们修改为：在读入后，raw_line = line.rstrip('\n')（但还要处理 Windows 的 \r）。更稳健：raw_line = line.rstrip('\r\n') 或使用 line.rstrip('\n') 如果最后可能只有 \n，如果还有 \r 则保留。通常文本模式下 \r\n 会被转换为 \n，所以 \r 不会出现。但为了保险，可以用 .rstrip('\n')。我们就这样。

但在 parse_line 中我们返回 'raw' 字段。所以 parse_line 接受 line（包含换行），我们在 parse_line 内部进行 raw = line.rstrip('\n') 并进一步 strip? 不，我们决定保留原始行（去除换行但保留其他空白）。所以我们修改 parse_line: raw = line.rstrip('\n')。其他解析时，我们使用 stripped = line.strip() 用于分割，但 raw 是 line.rstrip('\n')。但这样解析时所用文本可能包含前导空格，但分割时会忽略前导空格（因为 strip 了）。这样 raw 保留前导空格。这似乎更好。但 parse_line 返回的 raw 应该与分割所用的不同行版本？如果行有前导空格，stripped 会去掉，所以 raw 包含前导空格。这可能会影响匹配。但要求是保留原始行，所以这样更好。我们修改代码：

在 parse_line 中：
```python
def parse_line(line):
    raw = line.rstrip('\n')
    stripped = raw.strip()
    if not stripped:
        return None
    parts = stripped.split()
    ...
    return {..., 'raw': raw}
```

注意：raw 包含换行符被移除，但保留其他空格。这样如果原始行有前导空格，raw 予以保留。

在 main 中读行：for line in sys.stdin: parsed = parse_line(line)。很好。

但是，在 slow_requests 中输出的 raw_line 将包含前导/后缀空格，也许不是问题。但确保一致性。

我们需要更新之前的代码。

另外，在 parse_line 中如果 raw 是空字符串（直接换行）则返回 None；这样 malformed_lines 计数。

现在，我们还需要考虑：解析 timestamp 我们暂不验证，但可能格式无效，但我们宽容处理，只检查字段存在。但有些行 timestamp 可能缺失，但字段数不足会被过滤。所以 OK。

现在，关于 P95 计算，我们用了 math.ceil(n*0.95)-1，如果 n=0 会异常，但已经处理。如果 n=1, ceil(0.95)=1, idx=0, sorted_lat[0] 正确。

top_paths 排序中，如果多个路径 count 相同，我们以路径字母排序，这样稳定。

但输出 JSON 时，slow_requests 包含列表，我们只保留前10。但是，如果慢请求不足10，则全部包含。

现在考虑性能：逐行处理，使用 collections.Counter 和 defaultdict 存储所有延迟，如果路径非常多或请求数极大，可能内存很大。但题目没有限制内存，所以我们接受。

代码总行数大约150行，远小于1000。

现在编写测试函数：我们还应该测试 top_paths 等边缘情况。但简单测试可以了。

测试函数中，我们可能需要模拟解析多个行，并验证统计数据。但为了简洁，我们只测试核心功能和 p95。

更好的测试：可以编写一个测试用例，构造一些行，调用处理逻辑（比如从行列表生成统计），模拟正常流程。但这样需要重构，把处理逻辑封装成一个函数以方便测试。但题目没有强制要求测试覆盖全部，我们可以只测试 parse_line 和 compute_p95，再加上一些边缘情况。

但是，为了更好的测试，我们可以考虑写一个函数 process_logs(lines) 返回统计结果，然后测试。这样可以更方便测试。但不需要，现有代码足够。

但为了满足“代码结构清晰，包含若干内置测试函数”，我们可以在 run_tests 中测试更多。

我们可以加入测试：输入模拟行，验证 total_requests, status_counts, top_paths, p95, slow_requests, tenant_error_rates, malformed_lines。我们可以在测试中用 list 模拟 stdin，然后调用 main 的变体？不，我们可以单独写个测试函数来处理行列表。因为我们运行时从 stdin 读取，测试时需要避免 stdin 读取。我们重构：创建一个函数 analyze_logs(lines) 返回结果 dict，然后在主函数中调用 analyze_logs(sys.stdin) 并输出 JSON。这样测试也可以调用 analyze_logs 并验证。这样做更好：将核心逻辑与 I/O 分离。我们修改代码结构：

- parse_line(line) 解析单行
- core_analysis(lines_iterable) 接受行迭代器，返回结果 dict。
- main 负责读取 sys.stdin，调用 core_analysis 并打印 JSON。
- run_tests 调用 core_analysis 用测试数据断言。

这样更清晰，且测试不需要模拟 stdin。

所以我们要修改。

定义 core_analysis(lines)，其中 lines 是一个可迭代的行字符串（每行包含换符或不含均可，但最好统一）。在 core_analysis 内部，我们循环 for line in lines: 解析。实际上，传入的 lines 可以是列表或 sys.stdin，所以需要逐行读取。如果传入 sys.stdin，会逐行。传入列表，也逐项。注意：sys.stdin 读出的行包括换行符，所以我们通过 parse_line 处理时内部 rstrip('\n')。当我们传入字符串列表作为测试时，我们应确保每行字符串可能不含换行符（或包含）。为了统一，可以让 parse_line 处理时，通过 line.rstrip('\n') 去除换行，但如果行没有换行符，rstrip('\n') 不会改变。所以可以。

所以我们保持 parse_line 接受一行（可能包含换行），内部使用 raw = line.rstrip('\n')。

然后 core_analysis(lines) 实现循环。

我们重构代码。

**重构后代码结构**：

```python
#!/usr/bin/env python3
import sys
import json
import math
from collections import Counter, defaultdict

def parse_line(line):
    # 同上，但调整
    raw = line.rstrip('\n')
    stripped = raw.strip()
    if not stripped:
        return None
    parts = stripped.split()
    if len(parts) != 6:
        return None
    try:
        timestamp = parts[0]
        method = parts[1]
        path_full = parts[2]
        status = int(parts[3])
        latency_str = parts[4]
        if not latency_str.endswith('ms'):
            return None
        latency = int(latency_str[:-2])
        tenant_part = parts[5]
        if not tenant_part.startswith('tenant='):
            return None
        tenant = tenant_part[7:]
        path = path_full.split('?')[0]
    except (ValueError, IndexError):
        return None
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status,
        'latency': latency,
        'tenant': tenant,
        'raw': raw
    }

def compute_p95(latencies):
    if not latencies:
        return 0
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    idx = math.ceil(n * 0.95) - 1
    if idx < 0:
        idx = 0
    if idx >= n:
        idx = n - 1
    return sorted_lat[idx]

def analyze_logs(lines):
    total_requests = 0
    malformed_lines = 0
    status_counts = Counter()
    path_counts = Counter()
    path_latencies = defaultdict(list)
    tenant_requests = Counter()
    tenant_errors = Counter()
    slow_requests = []

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue
        total_requests += 1
        status_counts[parsed['status']] += 1
        path_counts[parsed['path']] += 1
        path_latencies[parsed['path']].append(parsed['latency'])
        tenant = parsed['tenant']
        tenant_requests[tenant] += 1
        if 400 <= parsed['status'] < 600:
            tenant_errors[tenant] += 1
        if parsed['latency'] > 1000:
            slow_requests.append({
                'raw_line': parsed['raw'],
                'path': parsed['path'],
                'latency': parsed['latency']
            })

    # top_paths
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # p95
    p95_by_path = {path: compute_p95(lats) for path, lats in path_latencies.items()}

    # slow_requests
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_requests[:10]

    # tenant_error_rates
    tenant_error_rates = {}
    for tenant in tenant_requests:
        total = tenant_requests[tenant]
        errors = tenant_errors.get(tenant, 0)
        rate = round(errors / total, 3) if total > 0 else 0.0
        tenant_error_rates[tenant] = rate

    return {
        'total_requests': total_requests,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }

def run_tests():
    # 测试 parse_line 和 compute_p95 (若干)
    # 同前
    # 测试 analyze_logs
    test_lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2\n",
        "2026-05-01T12:03:20Z GET /api/users 404 50ms tenant=a1\n",
        "2026-05-01T12:03:21Z GET /api/orders 200 1500ms tenant=a1\n",
        "malformed line\n",
        "2026-05-01T12:03:22Z PUT /api/items 500 200ms tenant=c3\n",
        "2026-05-01T12:03:23Z DELETE /api/items 200 800ms tenant=b2\n",
        "\n",  # empty line
    ]
    result = analyze_logs(test_lines)
    assert result['total_requests'] == 6, f"total_requests={result['total_requests']}"
    assert result['malformed_lines'] == 2  # malformed line and empty line
    # status_counts: 200:3, 201:1, 404:1, 500:1
    assert result['status_counts'] == {200:3, 201:1, 404:1, 500:1}
    # top_paths: /api/orders:3, others 1 each, so top 5 includes all paths (4 paths)
    # paths: /api/orders 3, /api/users 1, /api/items 2 (PUT and DELETE both /api/items)
    # Actually in lines: PUT /api/items and DELETE /api/items, path /api/items count 2
    # So path_counts: /api/orders:2? Wait: we have GET /api/orders (twice? first GET, second GET after 404 line? Actually line3 is GET /api/users, line4 is GET /api/orders again, so /api/orders: 2 (line1 and line4). line2 is /api/orders?page=2 -> /api/orders also -> actually line2 is POST /api/orders?page=2 -> path /api/orders, so /api/orders total 3? Wait count: line1: GET /api/orders, line2: POST /api/orders (since ? removed), line4: GET /api/orders -> total 3 for /api/orders. line3: /api/users count1. line6: /api/items PUT, line7: /api/items DELETE -> count2 for /api/items. So total 3+1+2=6 correct.
    # top_paths sorted by count desc: /api/orders(3), /api/items(2), /api/users(1). So first two included, third path count1.
    assert len(result['top_paths']) == 3  # only 3 distinct paths
    assert result['top_paths'][0]['path'] == '/api/orders'
    assert result['top_paths'][0]['count'] == 3
    assert result['top_paths'][1]['path'] == '/api/items'
    assert result['top_paths'][1]['count'] == 2
    # p95: for /api/orders latencies: line1:123, line2:456, line4:1500 => sorted[123,456,1500], N=3, ceil(3*0.95)=ceil(2.85)=3, idx=2 -> 1500
    assert result['p95_latency_by_path']['/api/orders'] == 1500
    # /api/items: latencies 200,800 => sorted[200,800], N=2, ceil(1.9)=2 idx=1 ->800
    assert result['p95_latency_by_path']['/api/items'] == 800
    # /api/users: [50] => 50
    assert result['p95_latency_by_path']['/api/users'] == 50
    # slow_requests: only line4 >1000ms: 1500ms, raw_line should be the line strip? we have newline removed? raw_line will be line.rstrip('\n')
    assert len(result['slow_requests']) == 1
    assert result['slow_requests'][0]['latency'] == 1500
    assert result['slow_requests'][0]['path'] == '/api/orders'
    # tenant_error_rates: tenants: a1 (lines 1,3,4: 3 requests), b2 (lines2,7:2), c3 (line6:1)
    # errors: a1: status 404 (line3) and maybe? line1 200, line4 200? no error, so 1 error. b2: lines2 201, line7 200 -> no error. c3: line6 500 -> error.
    # rates: a1=1/3=0.3333333 round 0.333; b2=0/2=0.0; c3=1/1=1.0
    assert result['tenant_error_rates'] == {'a1': 0.333, 'b2': 0.0, 'c3': 1.0}

    # Additional tests for parse_line
    # ... (previous)
    print("All tests passed.")

def main():
    if '--test' in sys.argv[1:]:
        run_tests()
        return
    result = analyze_logs(sys.stdin)
    # 输出 JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

我们调整了测试，但是注意：在 test_lines 中，我们末尾有一个空行和 malformed line，所以 malformed_lines 应该为2（malformed line 行和空行）。我们的解析中，对于空行，stripped 为空，返回 None，所以计入。正确。

但注意：空行 '\n' 经过 line.rstrip('\n') 后变成 ''，stripped 为空，返回 None。所以 malformed_lines 增加1。

现在，p95 测试用例如上：对于 /api/orders 延迟 [123,456,1500]，sorted，ceil(3*0.95)= ceil(2.85)=3 idx=2 得1500。正确。

对于 /api/items: [200,800] ceil(2*0.95)= ceil(1.9)=2 idx=1得800。正确。

租户错误率：a1 错误数=1(line3 404)，总请求3，所以 1/3=0.3333333 round 0.333。b2 没有错误，0.0。c3 1/1=1.0。注意 round(0.0,3) 得到 0.0，但 JSON 中输出 0.0，没问题。

现在 check 所有需求：

- status_counts 符合。
- top_paths: 由于只有3个路径，输出全部3个（少于5个）。符合要求（前5个，如果不足5条则全部输出）。
- p95_latency_by_path 包括所有路径，正确。
- slow_requests 只有一条。
- tenant_error_rates 正确。

现在我们需要确保输出格式符合要求：要求输出 JSON 对象包含这些字段。我们使用了 indent=2，输出美化。但我们可以只输出无格式的 JSON？题目没有指定，但正常输出 JSON 即可。通常使用紧凑也行。但无指定，我选择 indent=2 提升可读性。

注意：对于 slow_requests，我们使用 'raw_line' 键。要求是“保留原始行、路径、耗时”，所以我们用 raw_line。

对于 p95_latency_by_path，值是整数。

注意：在 p95_latency_by_path 中，如果某个路径没有请求？不会出现，因为只来自于 path_latencies。

现在，我们可能需要在代码中加入 docstring 或注释说明。

现在测试 `--test` 运行，执行 run_tests。如果测试失败，会抛出 AssertionError，但测试函数中我们使用了 assert，如果失败会崩溃并显示错误。但在测试环境中可以接受。我们也可以打印更详细的信息，但简单 assert 即可。如果全部通过打印 "All tests passed." 这样正常。

在 main 中，如果包含 --test，则只运行测试，然后退出，不输出 JSON。

现在检查其他边缘情况：状态码 200 等，如果 status 是 600 以上或 100 以下，我们也接受，但在错误统计中 4xx/5xx 定义为错误（400-599），所以没问题。

关于耗时：我们只处理 ms 结尾，耗时可能包含小数？题目中说“耗时毫秒”，例子是整数 ms。所以用 int 转换，如果不是数字则跳过。如果耗时是类似于 "123ms" 但包含非数字，比如 "12a3ms"，int 会失败，所以跳过。

关于时间戳我们没有验证，但可以保留。如果时间戳格式错，不影响统计。

关于路径：可能会包含 #? 通常不去除 #，因为 # 是片段标识符，但日志中可能包含。我们只去除查询参数（?之后），保留 # 在路径中？题目说“可能包含查询参数，例如 ?page=2”，我们应只去除查询参数，所以 # 应该保留，但 # 不是查询参数。但是我们 split('?')[0] 会保留 #？因为 # 在 ? 之后？通常 URL 中 fragment 在最后，格式 path?query#fragment。但实际中日志可能包含 #。要求是“去掉查询参数”，只去掉 ? 后的查询部分，不包括片段。但用 split('?')[0] 会去掉了 ? 及之后的所有东西包括 #，所以如果存在 #，也会被去掉。但日志中可能没有 #，因为服务器端日志通常没有片段。我们为了安全，可以只去除查询参数，即如果包含 ?，取 ? 之前，保留 #。但更准确：使用 parse_qs 但禁止第三方库。我们可以用 path_full.split('?')[0] 对于典型情况。如果有片段，它在?之后，分开会丢失。但通常日志没有#。我们保持简单。

现在，检查代码中是否有不符合要求的地方。

**关于原始行保留**：我们使用了 line.rstrip('\n') 保留原始行（去除换行）。但如果原始行结尾有 \r，在文本模式下系统会统一为 \n，所以没问题。但如果 Windows 文本模式 \r\n 被转换为 \n，所以 rstrip('\n') 正确。

**关于空行**：空行被计入 malformed_lines，符合跳过原则。

**关于排序**：top_paths 按 count 降序，当 count 相同时按 path 字母升序，确保稳定性。也可以使用原始出现顺序，但最好明确。

**关于 p95 中向上取整**：我们使用了 math.ceil，要导入 math。

**关于代码行数**：目前大约 150 行。

**关于测试**：我们测试了基本功能，但可以增加更多测试来覆盖边界情况，比如无请求、全部 malformed 等。但 run_tests 已经有一些。可以再增加。

我们来扩展 run_tests：

- 测试 compute_p95 边界：N=0 返回0。
- 测试 parse_line 边缘：路径无查询参数、有查询参数、有多个查询参数、有空格？但不应有。
- 测试 analyze_logs 边界。

我们还可以添加测试：空输入行列表，结果 total=0, malformed=0? 实际上空输入没有行，所以 malformed 为0，total 为0。

但注意：空列表或空文件不会有行，所以 analyize_logs 返回字典各字段默认值，如 status_counts{}, path_counts{}, path_latencies{}, tenant_requests{}, slow_requests[], total_requests=0, malformed_lines=0。我们测试这个。

我们可以在 run_tests 中加入：

```python
# 空输入
result = analyze_logs([])
assert result['total_requests'] == 0
assert result['malformed_lines'] == 0
assert result['status_counts'] == {}
assert result['top_paths'] == []
assert result['p95_latency_by_path'] == {}
assert result['slow_requests'] == []
assert result['tenant_error_rates'] == {}
```

另外测试所有行都是 malformed：

```python
result = analyze_logs(["bad1\n", "bad2\n"])
assert result['total_requests'] == 0
assert result['malformed_lines'] == 2
```

等等。

由于这些测试简单，可以加入。

还需要注意：在 p95_latency_by_path 中，对于没有路径的情况，返回空字典。

现在，考虑性能：可能在 analyze_logs 中用 Counter 和 defaultdict 没问题。

现在，编写最终代码。

注意：在 run_tests 中，我们使用了 assert，而且没有捕获异常，所以一旦失败程序崩溃显示错误。我们可以选择打印更友好信息，但简单 assert 也可以。

另外，我们需要确保代码在 Python 3 中运行，并且不依赖第三方库。

最后，按要求输出 JSON。注意：JSON 中可能包含中文，所以我们使用了 ensure_ascii=False 以防路径中有非 ASCII 字符。但路径通常 ASCII，但保险。

还有一个细节：在 slow_requests 列表中，每个元素包含 'raw_line'，这个原始行可能包含换行符被去除。如果原始行有控制字符，JSON 会编码。没问题。

现在，我们可以考虑输出 JSON 时，如果数据量大，使用 sys.stdout.write 可能性能更好，但 print 也可以。

现在完成代码。

但是注意：在测试中，我们 test_lines 包含新行 \n，但是 analyze_logs 接收这些行并传递 parse_line，parse_line 中用 line.rstrip('\n') 去除。如果我们在测试中使用包含换行的字符串，没问题。如果使用不含换行的，例如 test_lines 直接写字符串不带换行，line.rstrip('\n') 不会去掉任何东西，也没问题。所以我们可以统一。

但要小心：我们的 test_lines 包含了 \n 是因为我们准备模拟 stdin 的行，但如果我们直接用列表传递字符串（无论是带换行还是不带），都能工作。不过最好统一。

现在代码已经完成。

但还有一点：要求“正常运行时只输出 JSON，不输出解释文字。”所以我们不能用 print 输出其他东西。但测试模式可以打印。

现在，我们检查解析函数对于“耗时”字段是否允许带符号？例如 "123ms"，只有数字。我们的 int 转换会处理负数，但不会出现。所以没问题。

另一个细节：status 可能为非数字字符串如 "abc"，int 抛出 ValueError，跳过。

好了，最终代码。

此外，题目要求每行日志格式包含这些字段：ISO时间、HTTP方法、路径、状态码、耗时毫秒、租户。但可能还有其他空白？如果我们 split 会得到6个字段，但如果字段内包含空格呢？例如路径可能包含空格？不会。方法可能是字符串但不会有空格。时间戳里 T 和 Z 等，没有空格。所以分割安全。

但是，有可能有额外空格在字段之间？我们用 split 而不加参数，会处理任意连续空白。所以一行中有多个空格也能处理。

另一情况：如果有行包含多个空格，分割后仍为6个字段如果字段之间空格数多余一个。

没问题。

现在，我们重构的函数 analyze_logs 接受 lines 迭代器。注意：sys.stdin 是迭代器，可以 for line in sys.stdin。

但是，在 main 中，我们调用 analyze_logs(sys.stdin)， sys.stdin 是文件对象，迭代器产生行（包括换行符）。这符合预期。

现在，我们考虑使用 sys.stdin.buffer 来加快读取？没必要。

现在，重新回顾要求中的细节：

- p95 定义为排序后向上取整位置。我们使用了 math.ceil(n*0.95) - 1。这产生整数索引。但需要注意：当 n=0 时，返回0。没问题。

- top_paths 请求量最高的前5个路径，包含 path 和 count。我们输出列表。

- slow_requests 耗时大于1000ms的前10条，按耗时降序，保留原始行、路径、耗时。我们输出列表，每个元素包含 raw_line, path, latency。注意 raw_line 是原行（无换行符）。

- tenant_error_rates 每个租户的错误率，4xx/5xx 算错误，保留三位小数。我们使用 round(errors/total, 3) 得到浮点数。当 total=0 时，error_rate 设置为 0.0。但是如果有租户出现但无请求？不会出现。如果有租户请求数为0，但因为我们只从请求中收集租户，所以总会有至少一个请求。所以 total>0 总成立。

- 输出 JSON 对象时，键的顺序？我们可以让键按照逻辑顺序。但 JSON 对象键是无序的。但我们 dict 的插入顺序保留了 Python 3.7+。我们可以按顺序构建字典。但无所谓。但为了输出美观，我们可以按特定顺序。使用 dict 现在保持顺序。我们构建 output 的顺序是按逻辑顺序：total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines。可以。

现在，最终代码。

我们也要考虑在解析时，timestamp 我们不验证，但可能有行的时间戳格式不对，但字段数正确，我们会解析成功。但可能有些时间戳包含空格？比如 ISO 8601 有空格？不会，标准格式没有空格。所以分割安全。

现在，我们再测试一下一个复杂例子：路径包含斜杠，多级路径。正常。

现在，我们可能需要确保 top_paths 的输出键为 "path" 和 "count"，符合要求。

现在，我们修改测试代码，增加一些额外的测试。

另外，注意：在 run_tests 中，我们需要导入必要的模块已经导入。但 run_tests 也在全局作用域，可以访问 compute_p95 等。

我们也可以将测试放在单独的函数，并在 __main__ 中调用。

现在，写出最终完整的代码。

还有一点：要求“代码结构清晰，包含若干内置测试函数”，所以测试函数 run_tests 会有多个测试场景。我们可以包括：

- test_parse_line
- test_compute_p95
- test_analyze_logs (一个综合测试)
- test_edge_cases

但我们可以统一。

为了使得测试更完备，我们增加一些测试。但注意总代码不超过1000行，这些测试增加一点代码没问题。

我们也可以使用 unittest 标准库，但那是第三方库？unittest 是标准库，可以使用，但需要导入。但为了简单，我们直接用 assert。

现在，我们用函数结构测试。

我们重写 run_tests 更全面。

我们可以在 run_tests 中顺序执行多个测试块，打印每个测试块的结果。

但为了简洁，我们直接执行所有断言，最后打印成功信息。

如果断言失败，会抛出异常，测试终止。

所以测试报告会是简单的。

现在，编写最终代码：

注意，在 python 3 中，sys.stdin 是文本模式，读取字符串。

我们使用 with 语句？不需要。

开始写代码。

我们在代码文件头部添加说明。

最终代码（约 200 行）:

```python
#!/usr/bin/env python3
"""
log_analyzer.py - Analyze access logs from stdin and output statistics as JSON.

Usage:
  python log_analyzer.py < logfile.txt     # output JSON stats
  python log_analyzer.py --test            # run built-in tests
"""

import sys
import json
import math
from collections import Counter, defaultdict


def parse_line(line):
    """Parse a single log line. Return a dict of fields or None if malformed."""
    raw = line.rstrip('\n')          # keep original line (without newline)
    stripped = raw.strip()
    if not stripped:
        return None
    parts = stripped.split()
    if len(parts) != 6:
        return None
    try:
        # fields are: timestamp method path status latency tenant
        timestamp = parts[0]
        method = parts[1]
        path_full = parts[2]
        status_code = int(parts[3])
        latency_str = parts[4]
        # latency must end with 'ms'
        if not latency_str.endswith('ms'):
            return None
        latency = int(latency_str[:-2])
        tenant_part = parts[5]
        if not tenant_part.startswith('tenant='):
            return None
        tenant = tenant_part[7:]
        # remove query string from path (everything after '?')
        path = path_full.split('?')[0]
    except (ValueError, IndexError):
        return None
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status_code,
        'latency': latency,
        'tenant': tenant,
        'raw': raw
    }


def compute_p95(latencies):
    """Compute the 95th percentile latency (integer)."""
    if not latencies:
        return 0
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    # index = ceil(n * 0.95) - 1  (1-based position -> 0-based index)
    idx = math.ceil(n * 0.95) - 1
    # clamp to valid range
    if idx < 0:
        idx = 0
    if idx >= n:
        idx = n - 1
    return sorted_lat[idx]


def analyze_logs(lines):
    """
    Process an iterable of log lines and return a statistics dictionary.
    """
    total_requests = 0
    malformed_lines = 0
    status_counts = Counter()
    path_counts = Counter()
    path_latencies = defaultdict(list)
    tenant_requests = Counter()
    tenant_errors = Counter()
    slow_requests = []

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue

        total_requests += 1
        status_counts[parsed['status']] += 1
        path = parsed['path']
        path_counts[path] += 1
        path_latencies[path].append(parsed['latency'])

        tenant = parsed['tenant']
        tenant_requests[tenant] += 1
        # 4xx or 5xx are considered errors
        if 400 <= parsed['status'] < 600:
            tenant_errors[tenant] += 1

        if parsed['latency'] > 1000:
            slow_requests.append({
                'raw_line': parsed['raw'],
                'path': path,
                'latency': parsed['latency']
            })

    # Top 5 paths by request count (tie-break by path name)
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # P95 latency per path
    p95_by_path = {path: compute_p95(lats) for path, lats in path_latencies.items()}

    # Slow requests: sort descending by latency, keep top 10
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_requests[:10]

    # Error rate per tenant
    tenant_error_rates = {}
    for tenant in tenant_requests:
        total = tenant_requests[tenant]
        errors = tenant_errors.get(tenant, 0)
        rate = round(errors / total, 3) if total > 0 else 0.0
        tenant_error_rates[tenant] = rate

    return {
        'total_requests': total_requests,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }


def run_tests():
    """Execute built-in tests."""
    # --- Test parse_line ---
    # Normal line
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed is not None
    assert parsed['timestamp'] == "2026-05-01T12:03:18Z"
    assert parsed['method'] == "GET"
    assert parsed['path'] == "/api/orders"
    assert parsed['status'] == 200
    assert parsed['latency'] == 123
    assert parsed['tenant'] == "a1"
    assert parsed['raw'] == line   # no trailing newline in this string

    # Path with query parameters
    line2 = "2026-05-01T12:03:19Z POST /api/orders?page=2&sort=asc 201 456ms tenant=b2"
    parsed2 = parse_line(line2)
    assert parsed2 is not None
    assert parsed2['path'] == "/api/orders"
    assert parsed2['latency'] == 456
    assert parsed2['tenant'] == "b2"

    # Various malformed lines
    assert parse_line("") is None                     # empty (after strip)
    assert parse_line("   ") is None                  # whitespace only
    assert parse_line("short line") is None           # not 6 fields
    assert parse_line("a b c d e f") is None          # f doesn't start with tenant=
    assert parse_line("a b c 200 123ms tenant=x") is None  # timestamp/method invalid but we actually don't validate them; however path c is missing ?, status code 200 etc but that's fine, but tenant_part starts with tenant= so it's considered valid? Wait check: parts: a, b, c, 200, 123ms, tenant=x -> 6 fields, each parseable: timestamp a, method b, path c, status 200, latency 123, tenant x. So it will be parsed successfully! So we should not consider malformed. So the assertion should be None? Actually our parser does not validate timestamp or method format, so such a line would be accepted. So we cannot assert None. Let's design a truly malformed line: '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1' is valid. To test malformed, we need wrong latency format: "abcms" or no ms suffix.
    assert parse_line("a b c 200 123abc tenant=x") is None   # wrong latency format
    assert parse_line("a b c 200 123ms no_tenant") is None    # last field doesn't start with tenant=
    assert parse_line("a b c 200 ms123 tenant=x") is None     # latency not ending with ms (the int conversion fails? ms123 doesn't end with ms, so will be rejected: not end with 'ms')
    # Actually latency_str "ms123" doesn't end with 'ms'? ends with 'ms'? 'ms123' ends with '123', not 'ms'. So None.
    # Test status code not int
    assert parse_line("a b c abc 123ms tenant=x") is None
    # Additional: trailing newline
    parsed_nl = parse_line(line + "\n")
    assert parsed_nl is not None
    assert parsed_nl['raw'] == line   # rstrip removes newline

    # --- Test compute_p95 ---
    # Empty list
    assert compute_p95([]) == 0
    # Single element
    assert compute_p95([42]) == 42
    # Known cases
    assert compute_p95([1,2,3,4,5,6,7,8,9,10]) == 10   # N=10, ceil(9.5)=10 -> idx 9
    assert compute_p95([1,2,3,4,5,6,7,8,9]) == 9      # N=9, ceil(8.55)=9 -> idx8
    assert compute_p95([5,5,5,5,5]) == 5               # all same
    # Random verification
    import random
    random.seed(42)
    for n in range(1, 101):
        lats = [random.randint(100, 500) for _ in range(n)]
        sorted_lats = sorted(lats)
        k = math.ceil(n * 0.95) - 1
        expected = sorted_lats[max(0, min(k, n-1))]
        assert compute_p95(lats) == expected

    # --- Test analyze_logs ---
    # Empty input
    result = analyze_logs([])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 0
    assert result['status_counts'] == {}
    assert result['top_paths'] == []
    assert result['p95_latency_by_path'] == {}
    assert result['slow_requests'] == []
    assert result['tenant_error_rates'] == {}

    # All malformed
    result = analyze_logs(["bad1\n", "bad2\n"])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 2

    # Mixed valid and invalid lines
    test_lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2\n",
        "2026-05-01T12:03:20Z GET /api/users 404 50ms tenant=a1\n",
        "2026-05-01T12:03:21Z GET /api/orders 200 1500ms tenant=a1\n",
        "malformed line\n",
        "2026-05-01T12:03:22Z PUT /api/items 500 200ms tenant=c3\n",
        "2026-05-01T12:03:23Z DELETE /api/items 200 800ms tenant=b2\n",
        "\n",
    ]
    result = analyze_logs(test_lines)
    assert result['total_requests'] == 6, f"total {result['total_requests']}"
    assert result['malformed_lines'] == 2
    # status counts
    assert result['status_counts'] == {200: 3, 201: 1, 404: 1, 500: 1}
    # top paths: /api/orders(3), /api/items(2), /api/users(1)
    assert len(result['top_paths']) == 3
    assert result['top_paths'][0] == {'path': '/api/orders', 'count': 3}
    assert result['top_paths'][1] == {'path': '/api/items', 'count': 2}
    assert result['top_paths'][2] == {'path': '/api/users', 'count': 1}
    # p95
    assert result['p95_latency_by_path']['/api/orders'] == 1500
    assert result['p95_latency_by_path']['/api/items'] == 800
    assert result['p95_latency_by_path']['/api/users'] == 50
    # slow requests (only the 1500ms one)
    assert len(result['slow_requests']) == 1
    assert result['slow_requests'][0]['latency'] == 1500
    assert result['slow_requests'][0]['path'] == '/api/orders'
    # check raw_line in slow request (the original line without newline)
    # The fourth line in test_lines is the slow one: raw should be that line without '\n'
    slow_raw = result['slow_requests'][0]['raw_line']
    expected_raw = "2026-05-01T12:03:21Z GET /api/orders 200 1500ms tenant=a1"
    assert slow_raw == expected_raw, f"raw line mismatch: {repr(slow_raw)} != {repr(expected_raw)}"
    # tenant error rates
    assert result['tenant_error_rates'] == {'a1': 0.333, 'b2': 0.0, 'c3': 1.0}

    # Additional edge: very large latency list for p95
    lats = list(range(1, 101))  # 1..100
    p95 = compute_p95(lats)
    # N=100, ceil(95)=95, idx=94 -> value 95? Actually sorted 1..100, index 94 = 95. Wait 0-based: sorted[94] = 95. So p95=95.
    assert p95 == 95

    # Test that top_paths handles fewer than 5 distinct paths
    result2 = analyze_logs([
        "2026-01-01T00:00:00Z GET /a 200 1ms tenant=t1\n",
        "2026-01-01T00:00:01Z GET /a 200 2ms tenant=t1\n",
    ])
    assert len(result2['top_paths']) == 1
    assert result2['top_paths'][0] == {'path': '/a', 'count': 2}

    # Test slow_requests ordering and limit
    lines_slow = []
    for i in range(15):
        lines_slow.append(f"2026-01-01T00:00:0{i}Z GET /path 200 {1000 + i*10}ms tenant=t{i%3}\n")
    result3 = analyze_logs(lines_slow)
    assert len(result3['slow_requests']) == min(10, 15)  # should be 10
    assert result3['slow_requests'][0]['latency'] == 1000 + 14*10  # largest is last
    assert result3['slow_requests'][-1]['latency'] == 1000 + 5*10   # the 10th largest? Let's compute: the 10th largest when sorted descending, indices 0..9: the largest 10 values are 1140,1130,...,1050? Wait 15 lines: i=0..14, lat=1000+i*10 = 1000,1010,...,1140. Sorted descending: 1140(i14),1130(i13),...,1000(i0). Taking first 10 gives i14 down to i5. So the 10th (index9) should be i5 => 1050. So last element latency 1050. Check: assert result3['slow_requests'][-1]['latency'] == 1050. Good.

    # Test that slow_requests does not include latency <=1000
    # Already tested because all >1000 but boundary check
    result4 = analyze_logs(["... GET /path 200 1000ms tenant=t"])  # latency ==1000
    assert len(result4['slow_requests']) == 0

    print("All tests passed.")


def main():
    if '--test' in sys.argv[1:]:
        run_tests()
        return
    # Normal operation: read stdin, produce JSON
    result = analyze_logs(sys.stdin)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
```

现在，检查所有要求：

- 代码单文件，命令行程序，文件名 log_analyzer.py，没使用第三方库，总代码不超过1000（约230行）。
- 输入从标准输入读取多行日志，输出 JSON。
- 统计：total_requests, status_counts, top_paths (前5), p95_latency_by_path, slow_requests (>1000ms 前10), tenant_error_rates (4xx/5xx, 保留3位小数).
- 跳过无法解析的行，并输出 malformed_lines。我们通过 parse_line 返回 None 完成。
- 包含内置测试函数，使用 --test 运行。
- 正常运行时只输出 JSON。
- 路径去掉查询参数。
- 代码结构清晰，有函数。

注意：在 top_paths 中，当 count 相同时，我们按路径字母排序。要求没有明确，但这样合理。

在 p95 计算中，我们使用了向上取整。测试中验证了正确。

注意：我们使用 math.ceil，需要导入 math。

测试中使用 random 用于验证 p95，但 random 是标准库，允许。

在 run_tests 中，我们使用了 assert，测试失败会抛出 AssertionError。但是，如果测试通过，最后打印 All tests passed. 我们应该确保测试运行后使用 return 避免输出 JSON。

现在，我们考虑一些边缘情况：在大数据量下，path_latencies 可能很大。但没问题。

另一个细节：我们在慢请求收集时，使用了 parsed['raw'] 作为原始行。但 raw 是 line.rstrip('\n')，如果原始行有尾部空格？去除换行符，但尾部空格保留。所以符合保留原始行（去换行）。要求没有具体说明，所以可以。

另外，在输出 JSON 时，我们使用了 indent=2 美化。如果要紧凑输出，可以去掉 indent。但默认输出即可。无论哪种，都是 JSON。

注意：因为要求“正常运行时只输出 JSON，不输出解释文字”，所以我们不能有额外的输出。我们的代码在正常分支只打印 JSON，在测试分支打印测试信息。

现在，检查一下在 run_tests 中，我们使用了一个相似的行 test_lines 测试 raw_line 时，注意我们定义的 test_lines 包含 \n，但我们期望 raw_line 不包含 \n。因为我们用 line.rstrip('\n') 去除了。所以 expected_raw 是原始行不带 \n。我们设定正确。

另一个注意：在测试慢请求时，我们使用 lines_slow 包含 \n，但 raw_line 会去除 \n，所以验证时我们使用 assert 比较字符串，我们未定义期待值，但我们可以检查 raw_line 是否以特定开始。我们或许应该检查 raw_line 是原始行去除换行。但我们的测试未直接比较，因为我们没存储具体 raw_line。但我们可以加一个简单的检查，比如 assert slow_raw.startswith("2026-01-01")。

但为简化，我们没检查 raw_line。在第一个测试中已经检查了。所以没问题。

还有，关于 p95 计算，我们使用 random，注意使用了 random.seed(42) 确保可重复。

现在，代码已经完整。

但在测试中，我们有一个测试用例 "mixed valid and invalid lines" 中，我们检查了 top_paths 的前三项，但如果路径数量小于5，输出全部。正确。

包含很多测试，覆盖了大部分场景。

但是注意：我们的 `run_tests` 在测试 `parse_line` 时，我们用了 assert parse_line("a b c 200 123ms tenant=x") is not None ？实际上我们没写这个断言，但我们在后续的测试中展示。我没有显式测试一个完全有效但随意字段的行，但没问题。

现在，我们可能需要对 parse_line 进行更严格的测试，但现有的够。

现在检查潜在 bug：在 parse_line 中，当 latency_str 为 "ms" 或 "-5ms" 时？"ms" 不合规，会被 int('') 失败；"-5ms" 作为 int('-5') 成功，但耗时不会为负。但无所谓。

现在，另一个点：在 slow_requests中，我们选择了 latency > 1000，不是 >=1000。符合要求。

现在，关于输出中 status_counts 的键：在 JSON 中，整数键会被转换为字符串。这是 JSON 标准。如果希望是数字，可以使用数组？但 dict 在 JSON 中键总是字符串。所以没问题。

现在，我们是否需要按照要求中的顺序输出字段？要求描述的顺序是：total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates。并额外注明 malformed_lines 数量。所以我们包含 malformed_lines。输出时顺序我们按照插入顺序（total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines）。与要求一致。

现在，关于包含 malformed_lines 在输出中，要求中提到："跳过无法解析的行，并在输出中给出 `malformed_lines` 数量。" 所以必须包含。

我们检查一下：我们输出包含 malformed_lines，正确。

现在，所有都符合。

但有一个细节：在慢请求中，如果有多条且耗时相同，排序后取前10，没有指定 tie-breaking，所以按现有的 sorted 稳定排序，但 Python sorted 是稳定的，所以如果 latency 相同，保持原来的相对顺序。可以接受。

现在，关于代码结构清晰，我们使用函数组织。

我们还应该添加文件注释，说明用法。

现在，最终代码已经完成。

但是，我们再检查一下是否有遗漏的地方。

**问题：路径可能包含字符如 `?` 但查询参数我们只去除第一个 ? 及之后，但是如果在路径中包含 `?` 但非查询参数？例如路径本身可能含有 `?` 是允许的，但通常是查询分隔符。我们按题目要求去掉查询参数，所以 split('?')[0] 是常见做法。

**问题：如果原始行包含 Windows 换行 \r\n，line.rstrip('\n') 会留下 \r？文本模式下，系统会转换为 \n，所以 \r\n 已转为 \n，所以 rstrip('\n') 将去掉 \n 留下 \r？在文本模式下读取时，Python 会将行结束符转换为 \n，所以 \r\n 变成 \n，因此 rstrip('\n') 将删除 \n，不会留下 \r。但如果是二进制模式则不同，但我们使用文本模式默认，所以正确。

**问题：在 parse_line 中，如果原始行有前导空格，我们会用 stripped 分割，但 raw 保留了前导空格。在 slow_requests 输出时，raw_line 会显示前导空格。是否可能影响？但一般没有。

**问题：在测试中，我们使用了 assert，但如果运行测试时断言失败，会抛出异常并导致非零退出，并可能输出 traceback。这可能是预期的。用户可以从输出中看到失败细节。但有些环境可能会隐藏 traceback。不过我们只是测试，这样也可以。

**问题：超过1000行？我们的代码约230行，远小于。

现在，我们用一个示例输入验证输出。在开发时，我们可以构造示例。

我们程序可以从输入读入，输出 JSON。

但注意：analyze_logs 接收行迭代器，但 sys.stdin 是文件对象，迭代时每行包含换行符。所以我们在 parse_line 中 line 包含换行符。我们用 rstrip('\n') 去除。这正确。

但在我们测试中，使用列表包含换行符，也正确处理。

现在，我们代码可能对于包含 BOM 等字符的行会有问题，但日志一般没有。

我认为代码已满足要求。

不过，我们可能还需要考虑：P95 计算中，如果路径有大量延迟，我们排序并取索引。对于很大的列表，排序会消耗时间。但总比用大计算好。

现在，完成。

但让我们再检查一下需求原文：

"4. `p95_latency_by_path`：每个路径的 p95 耗时，毫秒整数。p95定义为排序后向上取整位置。"

我们的实现使用了 math.ceil(n*0.95)-1，这对应于向上取整的位置（从1开始）转为0索引。当 n=1, ceil(0.95)=1 -> idx=0 -> 第一个值，正确。当 n=2, ceil(1.9)=2 -> idx=1 -> 第二个值（最大值），正确。这是一种通常的定义：P95位置 = ceil(0.95 * N)。所以没问题。

但是注意，有些定义是 P95 = 排序后第 ceil(0.95 * N) 个值（从1开始），我们的索引就是该值，所以正确。

"5. `slow_requests`：耗时大于1000ms的前10条，按耗时降序，保留原始行、路径、耗时。"

我们做对了。

"6. `tenant_error_rates`：每个租户的错误率，4xx/5xx 算错误，保留三位小数。"

我们使用 round(rate, 3)，这产生一个浮点数例如 0.333，在 JSON 中可能是 0.333。但如果 rate 是 0.3333，round 后是 0.333，符合。如果 rate=0.3335，round(0.3335,3) 在 Python 中由于浮点误差可能为 0.334 或 0.333，但一般来说，round 使用银行家舍入，在最近的偶数。这不影响。要求“保留三位小数”通常期望数值精度。

另外，我们使用 round 可能会产生 0.0 而不是 0.000，但 JSON 可以，只是精度一样。

如果要求字符串形式保留三位小数，我们可以格式化。但需求说保留三位小数，并没有指定输出类型，通常数字即可。所以我们用 round 是数值。

所有满足。

**额外要求**：“路径可能包含查询参数，例如 `/api/orders?page=2`，统计时应去掉查询参数。”

我们通过 split('?')[0] 去除，但对于路径包含多个 ? 的情况，比如 `/api/orders?page=2?extra`，我们只取第一个 ? 之前，但那是少见。常见的是单个 ?。所以正确。

**关于 malformed_lines**：我们计数了所有无法解析的行。

现在，关于测试：我们使用了 `--test` 参数在任何位置，我们检查 if '--test' in sys.argv[1:]，所以多个参数中包含 --test 也触发测试模式。

**关于原始行保留**：在 slow_requests 中，我们保留了 raw_line，它是 line.rstrip('\n')。如果原始行包含末尾空格，会被保留。这是合理的。

**关于其他字段**：我们无需输出其他额外字段。

现在，我们可以认为完成了。

但有一个潜在优化：在测试函数中，我们导入了 random，但不在函数头部顶部导入，而是在测试函数内部导入。这是允许的。但是，由于 total 代码很短，我们可以将导入移到顶部，但无伤大雅。

所有代码已满足。

现在，将最终代码整理成最终答案。
````

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""
log_analyzer.py - Analyze access logs from stdin and output statistics as JSON.

Usage:
  python log_analyzer.py < logfile.txt     # output JSON stats
  python log_analyzer.py --test            # run built-in tests
"""

import sys
import json
import math
from collections import Counter, defaultdict


def parse_line(line):
    """Parse a single log line. Return a dict of fields or None if malformed."""
    raw = line.rstrip('\n')          # keep original line (without newline)
    stripped = raw.strip()
    if not stripped:
        return None
    parts = stripped.split()
    if len(parts) != 6:
        return None
    try:
        # fields are: timestamp method path status latency tenant
        timestamp = parts[0]
        method = parts[1]
        path_full = parts[2]
        status_code = int(parts[3])
        latency_str = parts[4]
        # latency must end with 'ms'
        if not latency_str.endswith('ms'):
            return None
        latency = int(latency_str[:-2])
        tenant_part = parts[5]
        if not tenant_part.startswith('tenant='):
            return None
        tenant = tenant_part[7:]
        # remove query string from path (everything after '?')
        path = path_full.split('?')[0]
    except (ValueError, IndexError):
        return None
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status_code,
        'latency': latency,
        'tenant': tenant,
        'raw': raw
    }


def compute_p95(latencies):
    """Compute the 95th percentile latency (integer)."""
    if not latencies:
        return 0
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    # index = ceil(n * 0.95) - 1  (1-based position -> 0-based index)
    idx = math.ceil(n * 0.95) - 1
    # clamp to valid range
    if idx < 0:
        idx = 0
    if idx >= n:
        idx = n - 1
    return sorted_lat[idx]


def analyze_logs(lines):
    """
    Process an iterable of log lines and return a statistics dictionary.
    """
    total_requests = 0
    malformed_lines = 0
    status_counts = Counter()
    path_counts = Counter()
    path_latencies = defaultdict(list)
    tenant_requests = Counter()
    tenant_errors = Counter()
    slow_requests = []

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue

        total_requests += 1
        status_counts[parsed['status']] += 1
        path = parsed['path']
        path_counts[path] += 1
        path_latencies[path].append(parsed['latency'])

        tenant = parsed['tenant']
        tenant_requests[tenant] += 1
        # 4xx or 5xx are considered errors
        if 400 <= parsed['status'] < 600:
            tenant_errors[tenant] += 1

        if parsed['latency'] > 1000:
            slow_requests.append({
                'raw_line': parsed['raw'],
                'path': path,
                'latency': parsed['latency']
            })

    # Top 5 paths by request count (tie-break by path name)
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # P95 latency per path
    p95_by_path = {path: compute_p95(lats) for path, lats in path_latencies.items()}

    # Slow requests: sort descending by latency, keep top 10
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_requests[:10]

    # Error rate per tenant
    tenant_error_rates = {}
    for tenant in tenant_requests:
        total = tenant_requests[tenant]
        errors = tenant_errors.get(tenant, 0)
        rate = round(errors / total, 3) if total > 0 else 0.0
        tenant_error_rates[tenant] = rate

    return {
        'total_requests': total_requests,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }


def run_tests():
    """Execute built-in tests."""
    # --- Test parse_line ---
    # Normal line
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed is not None
    assert parsed['timestamp'] == "2026-05-01T12:03:18Z"
    assert parsed['method'] == "GET"
    assert parsed['path'] == "/api/orders"
    assert parsed['status'] == 200
    assert parsed['latency'] == 123
    assert parsed['tenant'] == "a1"
    assert parsed['raw'] == line

    # Path with query parameters
    line2 = "2026-05-01T12:03:19Z POST /api/orders?page=2&sort=asc 201 456ms tenant=b2"
    parsed2 = parse_line(line2)
    assert parsed2 is not None
    assert parsed2['path'] == "/api/orders"
    assert parsed2['latency'] == 456
    assert parsed2['tenant'] == "b2"

    # Various malformed lines
    assert parse_line("") is None                     # empty
    assert parse_line("   ") is None                  # whitespace only
    assert parse_line("a b c 200 123abc tenant=x") is None   # wrong latency format
    assert parse_line("a b c 200 123ms no_tenant") is None    # last field not tenant=
    assert parse_line("a b c abc 123ms tenant=x") is None     # status not int

    # Trailing newline handling
    parsed_nl = parse_line(line + "\n")
    assert parsed_nl is not None
    assert parsed_nl['raw'] == line

    # --- Test compute_p95 ---
    assert compute_p95([]) == 0
    assert compute_p95([42]) == 42
    assert compute_p95([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 10
    assert compute_p95([1, 2, 3, 4, 5, 6, 7, 8, 9]) == 9
    assert compute_p95([5, 5, 5, 5, 5]) == 5

    # Random verification
    import random
    random.seed(42)
    for n in range(1, 101):
        lats = [random.randint(100, 500) for _ in range(n)]
        sorted_lats = sorted(lats)
        k = math.ceil(n * 0.95) - 1
        expected = sorted_lats[max(0, min(k, n - 1))]
        assert compute_p95(lats) == expected

    # --- Test analyze_logs ---
    # Empty input
    result = analyze_logs([])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 0
    assert result['status_counts'] == {}
    assert result['top_paths'] == []
    assert result['p95_latency_by_path'] == {}
    assert result['slow_requests'] == []
    assert result['tenant_error_rates'] == {}

    # All malformed
    result = analyze_logs(["bad1\n", "bad2\n"])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 2

    # Mixed valid and invalid lines
    test_lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2\n",
        "2026-05-01T12:03:20Z GET /api/users 404 50ms tenant=a1\n",
        "2026-05-01T12:03:21Z GET /api/orders 200 1500ms tenant=a1\n",
        "malformed line\n",
        "2026-05-01T12:03:22Z PUT /api/items 500 200ms tenant=c3\n",
        "2026-05-01T12:03:23Z DELETE /api/items 200 800ms tenant=b2\n",
        "\n",
    ]
    result = analyze_logs(test_lines)
    assert result['total_requests'] == 6
    assert result['malformed_lines'] == 2
    assert result['status_counts'] == {200: 3, 201: 1, 404: 1, 500: 1}
    assert len(result['top_paths']) == 3
    assert result['top_paths'][0] == {'path': '/api/orders', 'count': 3}
    assert result['top_paths'][1] == {'path': '/api/items', 'count': 2}
    assert result['top_paths'][2] == {'path': '/api/users', 'count': 1}
    assert result['p95_latency_by_path']['/api/orders'] == 1500
    assert result['p95_latency_by_path']['/api/items'] == 800
    assert result['p95_latency_by_path']['/api/users'] == 50
    assert len(result['slow_requests']) == 1
    slow = result['slow_requests'][0]
    assert slow['latency'] == 1500
    assert slow['path'] == '/api/orders'
    assert slow['raw_line'] == "2026-05-01T12:03:21Z GET /api/orders 200 1500ms tenant=a1"
    assert result['tenant_error_rates'] == {'a1': 0.333, 'b2': 0.0, 'c3': 1.0}

    # Less than 5 distinct paths
    result2 = analyze_logs([
        "2026-01-01T00:00:00Z GET /a 200 1ms tenant=t1\n",
        "2026-01-01T00:00:01Z GET /a 200 2ms tenant=t1\n",
    ])
    assert len(result2['top_paths']) == 1
    assert result2['top_paths'][0] == {'path': '/a', 'count': 2}

    # Slow request ordering and limit
    lines_slow = []
    for i in range(15):
        lines_slow.append(f"2026-01-01T00:00:0{i}Z GET /path 200 {1000 + i * 10}ms tenant=t{i%3}\n")
    result3 = analyze_logs(lines_slow)
    assert len(result3['slow_requests']) == 10
    # Latencies: 1140, 1130, ..., 1050 (first 10 of sorted 15)
    assert result3['slow_requests'][0]['latency'] == 1140
    assert result3['slow_requests'][-1]['latency'] == 1050

    # Boundary: latency exactly 1000 not included
    result4 = analyze_logs(["... GET /path 200 1000ms tenant=t\n"])
    assert len(result4['slow_requests']) == 0

    print("All tests passed.")


def main():
    if '--test' in sys.argv[1:]:
        run_tests()
        return
    # Normal operation: read stdin, produce JSON
    result = analyze_logs(sys.stdin)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
```
````
