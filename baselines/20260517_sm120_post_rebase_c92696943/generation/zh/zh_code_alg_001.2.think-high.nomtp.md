# Generation Transcript

- Case: `zh_code_alg_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 72.490623
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 338, "total_tokens": 7494, "completion_tokens": 7156, "prompt_tokens_details": null}`
- Prompt tokens: 338
- Completion tokens: 7156
- Total tokens: 7494

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
我们被要求编写一个单文件命令行程序log_analyzer.py，使用Python3，不使用第三方库，总代码不超过1000行。功能：从标准输入读取多行访问日志，每行格式：`2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1`。输出JSON对象，包含七个字段：total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines。

我们需要处理解析，跳过无法解析的行，统计malformed_lines数量。路径需去掉查询参数（即?后面的）。计算p95：排序后向上取整位置。例如，n个值，排序后索引为ceil(0.95*n) - 1？还是取第ceil(0.95*n)个？通常，p95定义为排序后第ceil(0.95 * N)个元素（1-indexed）。例如N=100，0.95*100=95，则取第95个（索引94）。如果N=99，0.95*99=94.05，ceil=95，取第95个（索引94）。我们将这实现为：sorted_latencies[int(math.ceil(0.95 * len(list))) - 1]。或者更准确地说：index = math.ceil(0.95 * n) - 1，如果index < 0则取0。

错误率：4xx/5xx算错误。tenant_error_rates: key是租户名，value是错误数/总请求数，保留三位小数。如果租户无请求？不会出现吧。

slow_requests：耗时大于1000ms的前10条，按耗时降序，保留原始行、路径、耗时。输出格式？JSON对象，字段：line, path, latency。注意：耗时是整数毫秒（从"123ms"提取）。如果耗时格式不对，可能无法解析，应算malformed？题目说耗时毫秒，格式为数字+ms。可以安全但需要处理异常。

路径包含查询参数，统计时应去掉。即取`/api/orders`部分，忽略`?page=2`。但注意，路径可能没有"?", 则保持不变。

时间戳：ISO时间，我们只用于计数总请求，不用于其他统计。但需要验证格式，如无法解析，则跳行。

软件架构：一个主函数，解析stdin。定义日志行解析函数，返回字典或None。收集统计信息。最后输出JSON。为了简洁，可以不用类，用字典累加。

测试：当`--test`运行时执行测试，测试用例可以包含一些示例输入和预期输出，使用assert语句。

由于要求“代码结构清晰，包含若干内置测试函数”，我们可以在if __name__ == "__main__":中判断sys.argv，如果包含--test就运行测试函数，否则正常处理。

注意：输出的JSON必须符合题目要求的键。top_paths: 请求量最高的前5个路径，按count降序？如果并列可以任意顺序。但最好也按路径名排序，不过题目没说。

p95_latency_by_path: 每个路径的p95耗时。如果某路径没有足够请求？空列表？p95至少需要1个请求？对于0个请求，可以忽略或输出0？但路径出现次数从0开始，不会出现在这里。对于只有1个请求，p95就是它本身。

tenant_error_rates: 每个租户的误差率。如果某租户没有请求（不应出现），skip。

slow_requests: 如果少于10条，就输出所有。

输出JSON示例：使用json.dumps，确保中文等字符正常，indent可选？题目没有要求格式化，输出紧凑也可以。为了易读，可以输出带缩进的JSON。但标准输出只要JSON，不要其他文字。

需要处理大输入？但无要求，简单即可。

现在设计代码：

1. 定义函数parse_line(line): 使用正则或split。格式：时间 方法 路径 状态码 耗时 租户。可以按空格分割：parts = line.strip().split()。如果有6个部分？可能路径含有查询参数，但split后是整体。所以：parts = line.split()，然后期望6个部分。但注意：路径中的查询参数可能包含空格？通常URL编码，空格是%20，不会影响。所以假定每行都是空格分隔的6个字段。但也要考虑路径可能包含"?"，不影响split。因此简单split空格得到6个元素：datetime, method, path, status, latency, tenant。

但还有一个问题：状态码是数字，耗时是"123ms"。租户是"tenant=a1"。解析：状态码int，耗时去掉"ms"转int，租户去掉"tenant="前缀。还需验证日期格式：ISO8601。可以使用datetime.fromisoformat验证，但Python 3.7+支持。如果格式错误，则malformed。

注意：路径可能包含查询参数，如"/api/orders?page=2"，需要去掉?及后面部分：path.split('?')[0]。

2. 收集数据：字典status_counts (key: status int, value: count), 字典path_counts (key: path, value: count), 字典p95_data (key: path, value: list of latencies), 列表slow_requests (list of dicts), 字典tenant_error_counts (key: tenant, value: [total, error_count] 或字典), malformed_lines计数。

每次解析成功一行后，更新这些统计。

最后计算p95_latency_by_path: 对每个路径，排序latencies列表，计算p95值，如果列表为空忽略。

top_paths: 对path_counts按count排序取前5。

slow_requests: 过滤latency>1000，按latency降序，取前10。

tenant_error_rates: 对每个租户计算error_rate = error_count/total, 保留三位小数。

3. 输出JSON: dict = {"total_requests": total, "status_counts": status_counts, "top_paths": top_paths, "p95_latency_by_path": p95_latency_by_path, "slow_requests": slow_requests, "tenant_error_rates": tenant_error_rates, "malformed_lines": malformed_lines}。注意：status_counts中的键应该转换为字符串，因为JSON的键必须字符串。Python int键在json.dumps中会被自动转为字符串（虽然JSON规范要求键必须是字符串，但Python的json模块默认转换int key为str）。但为了明确，可以在输出前转换：{str(k): v for k,v in status_counts.items()}。同样，p95_latency_by_path的键已经是路径字符串。注意：p95_latency_by_path中值应该是整数。tenant_error_rates中值应该是浮点数保留三位小数，可以用round(error_rate, 3)，或者使用格式化确保三位小数。但JSON支持float，保留三位小数意味着显示如0.123。round可能产生精度问题，最好使用格式化字符串再转为float？或者直接用round并设置精度。简单：rate = round(error/total, 3) 然后输出，但可能显示为0.1234？实际round(0.12345,3)=0.123，可以。

但是，要求“保留三位小数”，可以考虑输出浮点数。如果rate=0.5，应输出0.5还是0.500？JSON中0.5和0.500一样。通常保留三位小数是在显示层面，但在JSON中就是数字。我们可以通过round实现。如果觉得需要确保正好三位，可以用Decimal，但题目不允许第三方库，也不要求特别精确。round(number, 3)足够了，但Python的浮点表示可能显示长尾巴，但在JSON输出时默认会根据浮点值输出最短表示。例如0.5555->0.5555，但期望0.556？不，保留三位小数意味着精确到0.001。用round确保只有三位有效。但注意如0.5则round(0.5,3)=0.5，在JSON中输出为0.5。如果期望输出0.500，可能需要格式化字符串。但题目未指定，我认为0.5也是接受的三位小数表示，因为0.5==0.500。但为了保险，可以格式化为字符串'0.500'？但JSON中值应该是数字，不是字符串。最好输出数字，round(0.5,3)就可以了。

4. 测试函数：可以定义test_parse_line, test_p95, test_xxx等，使用assert。

5. 代码限制1000行，很充裕。

现在写代码。

注意：可能输入行中有多余空格？处理strip。

另外，边界情况：时间格式验证。使用datetime.fromisoformat，但可能抛出ValueError。例如"2026-05-01T12:03:18Z"中的Z是时区，Python 3.11+支持Z吗？Python 3.7+ fromisoformat支持带时区的ISO格式，但Z是Zulu，从Python 3.11起支持。为了兼容3.7-3.10，可能需要手动替换Z为+00:00。但题目指定Python 3，不指定版本。我们可以使用datetime.datetime.strptime，但格式更复杂。简单起见，我们可以用正则检查格式：r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z'。但更安全的是使用datetime解析。我们可以先尝试替换Z为+00:00，然后fromisoformat。或直接判断正则。因为不需要使用时间值，只验证格式，正则就够了。所以用正则匹配。

耗时：检查是否匹配r'\d+ms'。

租户：检查是否以"tenant="开头。

状态码：检查是否为三位数字？简单int转换并检查范围。

方法：检查是否是常见HTTP方法？不检查。

路径：任何字符串。

如果任何字段不符合预期，视为malformed。

但是，日志行可能包含更多空格？假设严格格式。

设计解析函数：

```
def parse_line(line):
    parts = line.strip().split()
    if len(parts) != 6:
        return None
    time_str, method, path, status_str, latency_str, tenant_str = parts
    # validate time
    if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', time_str):
        return None
    # method: should be GET/POST/PUT/DELETE/...? not strict, but at least 2-10 chars upper
    # path: start with /
    # status: digits
    if not status_str.isdigit():
        return None
    status = int(status_str)
    # latency: digits followed by 'ms'
    if not re.match(r'^\d+ms$', latency_str):
        return None
    latency = int(latency_str[:-2])
    # tenant: start with 'tenant='
    if not tenant_str.startswith('tenant=') or len(tenant_str) <= 7:
        return None
    tenant = tenant_str[7:]
    # path: remove query params
    path = path.split('?')[0]
    return {'time': time_str, 'method': method, 'path': path, 'status': status, 'latency': latency, 'tenant': tenant}
```

注意：path可能没有?，则不变。

现在收集数据。

使用defaultdict(list) for p95 latencies per path，使用Counter for path_counts, status_counts, error_counts per tenant等。

但为了不使用第三方库，可以用内置的collections.defaultdict，这属于标准库。

记数：使用dict或Counter。

实现分析函数：

```
def analyze(lines):
    total = 0
    malformed = 0
    status_counts = {}
    path_counts = {}
    p95_data = {} # dict list of latencies per path
    slow_requests = []
    tenant_stats = {} # dict dict: {tenant: {"total":0, "errors":0}}

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed += 1
            continue
        total += 1
        status = parsed['status']
        status_counts[status] = status_counts.get(status,0)+1
        path = parsed['path']
        path_counts[path] = path_counts.get(path,0)+1
        latency = parsed['latency']
        # collect p95 latencies
        p95_data.setdefault(path, []).append(latency)
        # slow requests
        if latency > 1000:
            slow_requests.append({'line': line.strip(), 'path': path, 'latency': latency})
        # tenant error rate
        tenant = parsed['tenant']
        if tenant not in tenant_stats:
            tenant_stats[tenant] = {'total':0, 'errors':0}
        tenant_stats[tenant]['total'] += 1
        if status >= 400 and status < 600:
            tenant_stats[tenant]['errors'] += 1

    # sort slow requests by latency desc and take top 10
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_requests[:10]

    # top paths
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0])) # desc count, then path
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # p95 per path
    p95_latency_by_path = {}
    for path, latencies in p95_data.items():
        latencies.sort()
        n = len(latencies)
        # p95 index (1-based)
        import math
        idx = math.ceil(0.95 * n) - 1
        if idx < 0: idx = 0
        p95_latency_by_path[path] = latencies[idx]

    # tenant error rates
    tenant_error_rates = {}
    for tenant, stats in tenant_stats.items():
        rate = stats['errors'] / stats['total']
        # round to 3 decimal places
        rate = round(rate, 3)
        tenant_error_rates[tenant] = rate

    # Convert status_counts keys to strings for JSON
    status_counts_str = {str(k): v for k, v in status_counts.items()}

    result = {
        'total_requests': total,
        'status_counts': status_counts_str,
        'top_paths': top_paths,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed
    }
    return result
```

注意：需要import math, re, json。

在输出JSON时，使用json.dumps(result, indent=2) 或直接dump。

测试函数：定义test_parse_line_valid, test_parse_line_invalid, test_analyze_simple等。

例如：

```
def test_parse():
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed['time'] == "2026-05-01T12:03:18Z"
    ...
```

需覆盖各种异常。

注意：path去除查询参数的测试。

主入口：

```
if __name__ == '__main__':
    import sys
    if '--test' in sys.argv:
        run_tests()
    else:
        lines = sys.stdin.readlines()
        result = analyze(lines)
        print(json.dumps(result, ensure_ascii=False, indent=2))
```

注意：如果输入很大，readlines可能占内存，但题目无性能要求。也可以逐行处理，但需要收集输出，最终输出JSON。可以使用列表收集，但也可通过分析函数接收迭代器。但我们上面的analyze需要列表lines。如果担心，可以修改为逐行迭代。

为了简洁，使用readlines。

检查代码长度不超过1000行，显然。

最后输出JSON时，注意indent美观。但题目没有要求，可以不indent。但为了可读性，加indent。

另外，测试函数中可能需要运行analyze并打印结果，但测试只assert。

测试用例：

- 基本行
- 多行
- 含查询参数的路径
- 耗时超过1000ms
- 错误率计算
- malformed行（格式错误、不完整）
- 空输入

写几个测试函数。

注意：排序时top_paths并列情况，我们可以按路径名排序确保确定性。

p95计算：当n=1时，ceil(0.95*1)=1, idx=0；当n=2时，ceil(0.95*2)=ceil(1.9)=2, idx=1；当n=3时，ceil(2.85)=3, idx=2；当n=10时，ceil(9.5)=10, idx=9, 即最大值。实际p95概念是第95百分位，即会有95%的数值小于等于该值。以n=10为例，第95百分位通常是第9.5个值，但向上取整数位置10意味着第10个值（最大值），而更常见的算法是取第ceil(0.95*n)个（1-indexed）。我们按照题目：“p95定义为排序后向上取整位置”。我理解是：对所有值排序，取位置索引 = ceil(0.95 * N) （1-indexed）。所以实现正确。但需要确保索引不越界。

测试用例：N=1, 0.95*1=0.95, ceil=1, idx=0正确。N=2, 0.95*2=1.9, ceil=2, idx=1, 即取最大值，合理。

如果N=0不会发生，因为只有路径有请求才会出现在p95_data中。

注意：耗时是整数毫秒，我们存储为int。

现在考虑慢请求：耗时大于1000ms。该字段是int，可以直接比较。

错误率：保留三位小数，使用round。注意：若tenant_error_rates中rate=0.0，输出0.0；若rate=1.0，输出1.0。若rate=0.5，输出0.5。可能期望显示三位小数如0.500，但JSON中浮点0.5就是0.5。如果严格要求三位小数，可能需要输出字符串，但题目说的是“保留三位小数”，没说是数字还是字符串，通常数字保留三位小数是指数值上精确到千分之一，数字0.5就是。我认为没问题。

也可以使用Decimal，但不需要。

为了更精确，可以设为rate = round(errors/total, 3)再存入。

最后，
````

## Assistant

````markdown
以下是符合要求的 Python 脚本 `log_analyzer.py`。它从标准输入读取日志，按说明解析并输出统计 JSON，且包含 `--test` 自测试功能。

```python
#!/usr/bin/env python3
"""
log_analyzer.py - 单文件命令行日志分析器
无第三方依赖，代码少于1000行。

用法:
    python log_analyzer.py < 日志文件
    python log_analyzer.py --test
"""

import sys
import json
import math
import re
from collections import defaultdict


# ---------- 解析单行日志 ----------
def parse_line(line: str):
    """
    解析一行日志，成功返回字典，失败返回 None。
    日志格式: ISO时间 HTTP方法 路径 状态码 耗时ms 租户
    """
    parts = line.strip().split()
    if len(parts) != 6:
        return None

    time_str, method, path, status_str, latency_str, tenant_str = parts

    # 验证时间格式: ISO 8601 且结尾为 'Z'
    if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', time_str):
        return None

    # 验证 HTTP 方法 (常见大写动词)
    if not re.match(r'^[A-Z]{1,10}$', method):
        return None

    # 路径必须以 '/' 开头
    if not path.startswith('/'):
        return None

    # 验证状态码
    if not status_str.isdigit():
        return None
    status = int(status_str)

    # 验证耗时
    if not re.match(r'^\d+ms$', latency_str):
        return None
    latency = int(latency_str[:-2])

    # 验证租户
    if not tenant_str.startswith('tenant=') or len(tenant_str) <= 7:
        return None
    tenant = tenant_str[7:]

    # 去掉路径中的查询参数
    path = path.split('?')[0]

    return {
        'time': time_str,
        'method': method,
        'path': path,
        'status': status,
        'latency': latency,
        'tenant': tenant
    }


# ---------- 核心分析函数 ----------
def analyze(lines):
    """
    接收行迭代器，返回统计结果字典。
    """
    total_requests = 0
    malformed_lines = 0
    status_counts = defaultdict(int)          # {status: count}
    path_counts = defaultdict(int)            # {path: count}
    p95_data = defaultdict(list)              # {path: [latency, ...]}
    slow_requests = []                        # [{line, path, latency}]
    tenant_stats = defaultdict(lambda: {'total': 0, 'errors': 0})  # {tenant: stats}

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            malformed_lines += 1
            continue

        total_requests += 1
        status = parsed['status']
        path = parsed['path']
        latency = parsed['latency']
        tenant = parsed['tenant']

        status_counts[status] += 1
        path_counts[path] += 1
        p95_data[path].append(latency)

        if latency > 1000:
            slow_requests.append({
                'line': line.strip(),
                'path': path,
                'latency': latency
            })

        ts = tenant_stats[tenant]
        ts['total'] += 1
        if 400 <= status < 600:
            ts['errors'] += 1

    # ---- 计算 top_paths ----
    sorted_paths = sorted(path_counts.items(),
                          key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # ---- 计算 p95_latency_by_path ----
    p95_latency_by_path = {}
    for path, latencies in p95_data.items():
        latencies.sort()
        n = len(latencies)
        # p95 向上取整位置 (1-indexed)
        idx = math.ceil(0.95 * n) - 1
        if idx < 0:
            idx = 0
        p95_latency_by_path[path] = latencies[idx]

    # ---- 格式化 slow_requests ----
    slow_requests.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_requests[:10]

    # ---- 计算 tenant_error_rates ----
    tenant_error_rates = {}
    for tenant, stats in tenant_stats.items():
        rate = round(stats['errors'] / stats['total'], 3)
        tenant_error_rates[tenant] = rate

    # ---- 组合结果 ----
    result = {
        'total_requests': total_requests,
        'status_counts': {str(k): v for k, v in status_counts.items()},
        'top_paths': top_paths,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed_lines
    }
    return result


# ---------- 测试函数 ----------
def test_parse_valid():
    """测试正常解析"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed is not None
    assert parsed['time'] == "2026-05-01T12:03:18Z"
    assert parsed['method'] == "GET"
    assert parsed['path'] == "/api/orders"
    assert parsed['status'] == 200
    assert parsed['latency'] == 123
    assert parsed['tenant'] == "a1"

def test_parse_query_removal():
    """路径查询参数应被移除"""
    line = "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed['path'] == "/api/orders"

def test_parse_missing_fields():
    """字段不足应返回 None"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms"
    assert parse_line(line) is None

def test_parse_bad_time():
    """错误时间格式"""
    line = "2026/05/01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    assert parse_line(line) is None

def test_parse_bad_latency():
    """耗时格式错误"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123msx tenant=a1"
    assert parse_line(line) is None

def test_parse_bad_status():
    """状态码非数字"""
    line = "2026-05-01T12:03:18Z GET /api/orders twohundred 123ms tenant=a1"
    assert parse_line(line) is None

def test_parse_invalid_tenant():
    """租户前缀错误"""
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant"
    assert parse_line(line) is None

def test_analyze_simple():
    """基本分析功能"""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 100ms tenant=a1\n",
        "2026-05-01T12:03:19Z POST /api/users 201 200ms tenant=b2\n",
        "2026-05-01T12:03:20Z DELETE /api/orders 400 300ms tenant=c3\n",
        "2026-05-01T12:03:21Z PUT /api/items 500 1500ms tenant=a1\n",
    ]
    result = analyze(lines)
    assert result['total_requests'] == 4
    assert result['status_counts'] == {"200": 1, "201": 1, "400": 1, "500": 1}
    assert result['malformed_lines'] == 0
    # top_paths: 4条不同路径，取5个，所以全部出现
    assert len(result['top_paths']) == 4
    # p95 (4个，0.95*4=3.8 ceil=4, idx=3 最大值)
    assert result['p95_latency_by_path']['/api/orders'] == 100
    # slow: 只有1500>1000
    assert len(result['slow_requests']) == 1
    assert result['slow_requests'][0]['latency'] == 1500
    # error rates
    assert result['tenant_error_rates']['a1'] == round(1/2, 3)  # 500 是错误
    assert result['tenant_error_rates']['b2'] == 0.0
    assert result['tenant_error_rates']['c3'] == 1.0

def test_analyze_malformed():
    """malformed line 计数"""
    lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 100ms tenant=a1\n",
        "bad line here\n",
        "2026-05-01T12:03:19Z POST /api/users 201 200ms tenant=b2\n",
    ]
    result = analyze(lines)
    assert result['total_requests'] == 2
    assert result['malformed_lines'] == 1

def test_analyze_p95_exact():
    """p95 计算验证 (N=10)"""
    lines = []
    for i in range(1, 11):
        lines.append(f"2026-05-01T12:03:18Z GET /path {i*10} {i*100}ms tenant=t\n")
    result = analyze(lines)
    latencies = [i*100 for i in range(1,11)]
    latencies.sort()
    idx = math.ceil(0.95 * 10) - 1  # 10 -> idx=9
    expected = latencies[idx]
    assert result['p95_latency_by_path']['/path'] == expected

def test_analyze_slow_ordering():
    """慢请求排序与截取前10"""
    base = "2026-05-01T12:00:00Z GET /path 200 {}ms tenant=t\n"
    lines = [base.format(1000 + i*10) for i in range(20)]
    result = analyze(lines)
    assert len(result['slow_requests']) == 10
    # 检查降序
    lats = [r['latency'] for r in result['slow_requests']]
    assert lats == sorted(lats, reverse=True)
    # 检查最小的是第11个值？前10个最大的是 1000+190=1190 到 1000+10=1010? 注意i从0开始: 1000到1190，最大1190
    assert lats[0] == 1190
    assert lats[-1] == 1100  # 第10个应该是i=10:1000+100=1100

def test_analyze_empty():
    """空输入"""
    result = analyze([])
    assert result['total_requests'] == 0
    assert result['malformed_lines'] == 0
    assert result['top_paths'] == []
    assert result['p95_latency_by_path'] == {}
    assert result['slow_requests'] == []
    assert result['tenant_error_rates'] == {}

def run_all_tests():
    """执行所有测试"""
    test_parse_valid()
    test_parse_query_removal()
    test_parse_missing_fields()
    test_parse_bad_time()
    test_parse_bad_latency()
    test_parse_bad_status()
    test_parse_invalid_tenant()
    test_analyze_simple()
    test_analyze_malformed()
    test_analyze_p95_exact()
    test_analyze_slow_ordering()
    test_analyze_empty()
    print("所有测试通过。")


# ---------- 主入口 ----------
if __name__ == '__main__':
    if '--test' in sys.argv:
        run_all_tests()
    else:
        try:
            lines = sys.stdin.readlines()
        except KeyboardInterrupt:
            sys.exit(1)
        result = analyze(lines)
        print(json.dumps(result, ensure_ascii=False, indent=2))
```

## 功能说明

- **标准输入读取**：支持管道或重定向输入；每行按空格切分为 6 个字段，逐一解析验证。
- **错误处理**：无法解析的行被跳过后统计在 `malformed_lines` 中，不影响其他计数。
- **路径清理**：`split('?')[0]` 去除查询参数。
- **性能统计**：
  - `p95` 使用 `math.ceil(0.95 * N) - 1` 计算向上取整位置。
  - `slow_requests` 筛选 >1000ms 的记录，按耗时降序取前 10 条。
  - 错误率仅对 4xx/5xx 状态码计数，结果保留三位小数。
- **测试模式**：运行 `python log_analyzer.py --test` 执行内置测试，验证核心逻辑正确性。
- **输出**：只输出 JSON，不输出额外提示文字；JSON 包含所有要求的七个字段。
````
