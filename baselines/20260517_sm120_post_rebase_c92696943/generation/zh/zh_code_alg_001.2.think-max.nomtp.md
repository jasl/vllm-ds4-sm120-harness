# Generation Transcript

- Case: `zh_code_alg_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 274.612373
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 417, "total_tokens": 27386, "completion_tokens": 26969, "prompt_tokens_details": null}`
- Prompt tokens: 417
- Completion tokens: 26969
- Total tokens: 27386

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
我们被要求写一个Python 3单文件命令行程序，不使用第三方库，代码不超过1000行。任务是从stdin读取多行访问日志，输出JSON对象，包含多个统计项。需要处理解析错误，输出malformed_lines数量。程序应当支持--test参数运行测试。

我们一步一步设计。

首先，输入格式：每行如：`2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1`

字段：ISO时间（格式 yyyy-mm-ddThh:mm:ssZ），HTTP方法，路径（可能带查询参数），状态码，耗时毫秒（数字后跟ms），租户（key=value形式? 实际是 tenant=a1，所以是`tenant=a1`。但注意可能租户部分有别的key? 问题描述说"租户"，推测只有tenant，但可能格式是key=value。但我们为了鲁棒，可能假设是tenant=xxx。但也可以按最后一个字段解析。

如何解析：使用正则表达式？由于不能使用第三方库，可以使用re。

建议模式：`^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) (GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) (\S+) (\d{3}) (\d+)ms tenant=(\S+)$`

但状态码是三位数字，耗时是数字后面带ms，但注意可能有四位状态码? 标准是三位。租户可能是任意字符串，可能包含空格? 假设没有空格。用\S+。

路径可能包含查询参数，我们去查询参数：用urlparse? 但不用第三方库，可以自己split '?'并取第一部分。

统计需求：

1. total_requests: 成功解析的行数。注意跳过无法解析的行，但总数仅包含成功的。

2. status_counts: 字典，key是状态码字符串，value是计数。

3. top_paths: 请求量最高的前5个路径，每个路径对象包括path和count。如果平局？按count降序，如果count一样，可以任意顺序，但我们可以按路径名排序（词典序）来确定性。要求没说，但测试可能需要稳定。我们最好在count相同时按路径字典序。

4. p95_latency_by_path: 每个路径的p95耗时，毫秒整数。定义：排序后向上取整位置。例如有n个请求，p95位置 = ceil(0.95 * n) 索引从1开始，对应排序后的第几个值。我们可以排序后取索引为 ceil(0.95 * n) - 1（0-based）。注意向上取整。

5. slow_requests: 耗时大于1000ms的前10条，按耗时降序，保留原始行、路径、耗时。每条包含: original_line, path, latency (毫秒整数)。我们需要记录这些信息。如果超过10条，取前10；如果不足，全部。注意耗时降序。

6. tenant_error_rates: 每个租户的错误率，4xx/5xx算错误，保留三位小数。错误率 = 该租户的错误请求数 / 该租户的总请求数。注意如果总请求为0，可以定义错误率为0? 但每个租户至少有一条请求。但理论上可能没有错误? 保留三位小数，可以格式化。输出应该是一个对象，key是租户ID，value是浮点数（三位小数）。为保证JSON输出，可以用round? 但用round()可能无法保证三位小数显示，比如0.1显示为0.1。JSON标准没有精确小数位数要求，但题目要求保留三位小数，可能意味着输出字符串如"0.125"或数字0.125? JSON的数字格式，可以控制小数位数? 一般输出为数字，但Python的json.dumps会把浮点数输出尽可能短。为了确保三位小数，可以转换为字符串? 但要求是JSON对象，数字是数字，但可以控制输出格式？我们可以使用round(val, 3)然后让json输出，但可能输出0.1而不是0.100。但题目要求“保留三位小数”，一般意味着数值四舍五入到3位小数。但JSON中，数字0.1和0.100是等价的，但为了符合人阅读，可能期望输出三位小数。但JSON规范并没有规定小数位数。我们可以使用float(round(rate, 3))，这样能保证数字是四舍五入到小数点后三位，但表示可能不是精确3位。为了确保，我们可以自定义JSON编码，将数字格式化为3位小数。但题目没有明确要求输出字符串。我倾向于输出数字，并使用round，因为通常测试会比较数字的近似值。

但有些场合测试可能期望字符串如"0.125"? 但题目说“保留三位小数”，正常是数字类型，但为了精确显示，我们可以输出为字符串，但那样不符合JSON对象? JSON数字是数值，字符串是字符串。我认为输出数字，保留三位小数的含义是数值精度。我会使用round(rate, 3)。

另外，malformed_lines计数：无法解析的行数。

输出JSON对象，包含上述字段。注意字段名: total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines。

代码结构：有一个main函数解析参数，如果参数包含--test则执行测试；否则从stdin读取数据，处理，输出JSON。

因为不能有额外输出，如果不是测试模式，只输出JSON。

测试函数：内置测试。我们需要设计一些测试用例来验证功能。可以使用doctest或简单assert。建议用单独的test函数，测试解析、统计等。

我们需要考虑性能，但最大1000行，没问题。代码可以简洁。

设计类或函数：

- parse_line(line): 尝试解析一行，返回字典或None（如果无法解析）。返回信息包括：timestamp, method, path (去掉查询参数), status (int), latency (int), tenant (str)。或者也可以简单返回一个namedtuple。

- process_lines(lines): 生成统计结果。

- compute_p95(sorted_latencies, n): 给出排序后的列表和总数，返回p95。

- main: 读取stdin所有行，逐行解析，统计。

注意：p95_latency_by_path需要每个路径单独计算。存储每个路径的latency列表，然后计算p95。路径是去掉查询参数后的路径。

对于top_paths，只需要计数字典，选前5。

tenant_error_rates: 每个租户的总请求数和错误请求数（status>=400）。

slow_requests需要保留原始行和解析后的路径及latency，所以解析时要保留原始行。

需要记录：

- total_requests计数

- status_counts: dict

- path_counts: dict

- latencies_by_path: dict of list

- slow_requests_list: list of dict (original_line, path, latency) where latency > 1000

- tenant_requests: dict of {'total': count, 'errors': count}

- malformed_lines计数

然后计算各输出字段。

注意：p95_latency_by_path可能需要对每个路径计算。如果某路径没有请求？不会。

慢请求排序取前10：latency降序，如果latency相同？无所谓。

测试：我们可以写一些测试用例，包括正常行、错误行、边界等。测试应该覆盖解析函数和统计逻辑。

注意：因为使用sys.stdin读取，测试时可能模拟输入。我们可以设计辅助函数，从字符串列表产生输出。

要求单文件命令行程序，文件名log_analyzer.py。总代码不超过1000行。

实现时考虑模块化，用函数。

输出JSON：使用json.dumps，设置indent保证可读？题目没说格式，但一般输出一行或格式化？最好输出适合阅读的，但既然只要求JSON对象，可以compact或pretty。我选择格式化更好看，但题目没有要求，但示例输出可能是单行？通常为了阅读我们使用indent=2。但测试可能需要一致。谨慎起见，我可以输出紧凑JSON，或使用默认indent=None，但测试时可能会比较字符串。但题目说输出JSON对象，没指定格式，任何合法JSON均可。为了保险，可以使用默认dumps，可能生成紧凑输出。但为了可读性，可以加上indent=2。但测试时如果逐字符比较可能失败。最好输出紧凑，这样没有多余空格。但题目要求“输出一个 JSON 对象”，没有格式要求。但为了可读性，我倾向于输出美化版本，但测试可能会直接比较字符串？通常测试会解析JSON比较值，而不会比较字符串。所以格式不重要，只要合法JSON。我选择紧凑（默认）以节省空间。

但注意，保留三位小数的问题，如果输出数字，json.dumps可能输出0.1，而不是0.100，但测试通常接受。如果需要强制三位小数，可以序列化前将数字转换为特定格式的字符串，但那样就不是数字了。我认为round足够。

让我写代码。

先定义parse_line:

```python
import re
import sys
import json
from collections import OrderedDict

LINE_RE = re.compile(
    r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) '
    r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) '
    r'(\S+) '
    r'(\d{3}) '
    r'(\d+)ms '
    r'tenant=(\S+)$'
)

def parse_line(line):
    m = LINE_RE.match(line)
    if not m:
        return None
    timestamp, method, path, status_str, latency_str, tenant = m.groups()
    # path去掉查询参数
    path = path.split('?')[0]
    status = int(status_str)
    latency = int(latency_str)
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status,
        'latency': latency,
        'tenant': tenant,
        'original_line': line.rstrip('\n')  # 保留原始行，去除换行
    }
```

但注意，原始行保留时可能包含换行，但输出时应该是原始内容（不含换行符）。所以用rstrip('\n')。

但注意，标准输入读取时，每行包含换行。保留原样？slow_requests要保留原始行。原始行应该包含整个行，不包括换行。输出JSON中，字符串包含换行会难处理，所以去掉换行。

现在处理逻辑。

```python
def process_input(lines):
    parsed = []
    malformed = 0
    for line in lines:
        line = line.rstrip('\n')
        if not line:  # 跳过空行
            continue
        result = parse_line(line)
        if result is None:
            malformed += 1
        else:
            parsed.append(result)
    # 统计
    total_requests = len(parsed)
    status_counts = {}
    path_counts = {}
    latencies_by_path = {}
    tenant_stats = {}  # tenant: {'total': int, 'errors': int}
    slow_requests = []
    # 用于slow_requests的临时列表
    slow_candidates = []

    for entry in parsed:
        path = entry['path']
        status = entry['status']
        latency = entry['latency']
        tenant = entry['tenant']

        # status_counts
        status_str = str(status)
        status_counts[status_str] = status_counts.get(status_str, 0) + 1

        # path_counts
        path_counts[path] = path_counts.get(path, 0) + 1

        # latencies_by_path
        latencies_by_path.setdefault(path, []).append(latency)

        # tenant_stats
        if tenant not in tenant_stats:
            tenant_stats[tenant] = {'total': 0, 'errors': 0}
        tenant_stats[tenant]['total'] += 1
        if status >= 400:
            tenant_stats[tenant]['errors'] += 1

        # slow_requests
        if latency > 1000:
            slow_candidates.append({
                'original_line': entry['original_line'],
                'path': path,
                'latency': latency
            })

    # 慢请求排序取前10
    slow_candidates.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_candidates[:10]

    # top_paths
    # 按count降序，然后path字典序
    # 使用sorted，key=lambda p:(-path_counts[p], p)
    top_paths = []
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    for path, count in sorted_paths[:5]:
        top_paths.append({"path": path, "count": count})

    # p95_latency_by_path
    p95_by_path = {}
    for path, lats in latencies_by_path.items():
        lats.sort()
        n = len(lats)
        pos = (int)(0.95 * n + 0.99999)  # 向上取整，也可以用math.ceil
        # 注意，如果0.95*n正好是整数，按定义向上取整位置就是那个整数，如果是4.75，向上取整为5，所以用ceil
        # 但ceil(0.95*n) >= 1 for n>=1
        # 索引从0开始
        idx = (0.95 * n + 0.999999)  # 或
        idx = int(idx)  # 小数部分为0时，如 ceil(4)=4，但我们需要0.95*n整数时取第n*0.95个（索引n*0.95-1?）向上取整是本身。
        # 用math.ceil
        import math
        pos = math.ceil(0.95 * n)
        # pos范围1到n
        # 索引pos-1
        p95_latency = lats[pos - 1]
        p95_by_path[path] = p95_latency

    # tenant_error_rates
    tenant_error_rates = {}
    for tenant, stats in tenant_stats.items():
        total = stats['total']
        errors = stats['errors']
        rate = errors / total if total > 0 else 0.0
        # 保留三位小数
        rate_rounded = round(rate, 3)
        tenant_error_rates[tenant] = rate_rounded

    # 组装输出
    output = {
        "total_requests": total_requests,
        "status_counts": status_counts,
        "top_paths": top_paths,
        "p95_latency_by_path": p95_by_path,
        "slow_requests": slow_requests,
        "tenant_error_rates": tenant_error_rates,
        "malformed_lines": malformed
    }
    return output
```

注意：status_counts期望key是字符串，如“200”。JSON key字符串。

p95_latency_by_path: key是路径，value是整数。

但还有个要求：slow_requests中的原始行包含原始输入行（包括状态码等），我们保留了original_line。

现在需要考虑：输入可能是大文件？但内存可以。我们读取全部行。

对于p95计算，使用math.ceil。

测试代码：编写测试函数。测试内容：

- 正常解析一行各字段是否正确。
- 有查询参数时路径是否被去掉。
- 无法解析的行计数。
- 空行处理。
- 综合测试，验证输出结果是否与预期一致。

我们可能需要模拟输入。在测试中，我们可以定义字符串列表作为输入，然后调用process_input，检查输出JSON。

注意，真正从stdin读取需要模拟，我们可以通过一个函数接受文件对象或行列表。在main中，读取sys.stdin生成行列表。但process_input可以接受行列表。

为了测试方便，我们写一个函数process_lines(lines)，返回字典。

main函数: 如果--test在参数中，调用test函数并退出；否则从stdin读取，处理，JSON输出。

注意：输出时，可能需要确保JSON键顺序固定（Python3.7+ dict有序），所以输出顺序应该和定义顺序相同。但输出时json.dumps会按照dict顺序，因为Python3.7+ dict是插入顺序。但我们可能需要明确一些顺序，如status_counts可能数字顺序排列? 但未要求排序。可保持自然顺序。但为了可预测，可以排序? 无所谓。但测试可能要比较排序，所以我们可以排序。

对于status_counts，我们可以对key排序（按状态码的数字顺序），因为输出JSON object，键是无序的。但如果我们希望一致，可以在输出时排序键。但通常用于比较，我们也可以不排序。但为了确定性，可以生成时排序。但注意 JSON 对象键本是无序，但 Python 的 dict 有序了，我们会按插入顺序。例如解析行时，不同状态码出现顺序不确定。所以我们可以在构建 status_counts 后使用 OrderedDict 按数字排序。同理 tenant_error_rates 的键也可以排序，但不必。

我们的输出 control 大小，没必要强制排序。但 top_paths 已经排序了。p95_by_path 是 dict，键的顺序是添加顺序（遍历 path_counts/item 的顺序）。但无所谓。

我决定让 status_counts 按键的数字字符串排序（从小到大）， tenant_error_rates 按键排序（字典序）。这样输出稳定。

修改：

- status_counts = {}，最后转为排序。

在构造输出时，使用 OrderedDict 或 sorted dict。简单方法是在输出前对 status_counts 排序重建： status_counts_sorted = dict(sorted(status_counts.items(), key=lambda x: int(x[0])))  因为键是字符串数字，按整数排序。

类似，tenant_error_rates: dict(sorted(tenant_error_rates.items())) 按租户字符串排序。

这样输出更一致。

同时 p95_latency_by_path 按键排序？也可以，但这是路径，没有要求，但可排序以便测试。

但注意，测试如果比较字符串可能需要一致顺序。我选择对这些字典排序。

对于 p95_by_path，按键排序；status_counts按状态码数字排序；tenant_error_rates按键排序。

top_paths 已经是指定排序。

slow_requests 已经按 latency 降序。

修改输出组装部分。

现在设计测试。测试应该包括多场景。

测试数据结构包括：

- 正常输入行有不同情况。
- 包含错误格式行。

测试验证每个统计项。

我们还可以测试 p95 计算：例如10个延迟，0.95*10=9.5 向上取整=10，取第10个（排序后最后一个），也就是最大值。所以p95=最小值? 测试。

慢请求测试。

错误率测试。

因为这些都会在测试中覆盖。

测试函数 test_all() 使用 assert 和打印信息。测试失败时引发异常。

为了方便，也可以使用简单的测试框架。

示例测试：

```python
def test_parse_line():
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line)
    assert parsed is not None
    assert parsed['path'] == '/api/orders'
    assert parsed['latency'] == 123
    assert parsed['tenant'] == 'a1'
    assert parsed['status'] == 200
    # test path with query
    line2 = "2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1"
    parsed2 = parse_line(line2)
    assert parsed2['path'] == '/api/orders'
    assert parsed2['method'] == 'GET'
    # test malformed line
    assert parse_line("invalid line") is None
    assert parse_line("") is None
    # test incomplete
    assert parse_line("2026-05-01T12:03:18Z GET /api 200 123ms") is None  # no tenant
    print("parse_line tests passed")
```

测试综合处理：

```python
def test_process():
    lines = [
        "2026-05-01T12:00:00Z GET /api/orders 200 100ms tenant=a1",
        "2026-05-01T12:00:01Z GET /api/users 200 200ms tenant=a1",
        "2026-05-01T12:00:02Z POST /api/orders 201 50ms tenant=b2",
        "2026-05-01T12:00:03Z GET /api/orders 500 2000ms tenant=a1",
        "2026-05-01T12:00:04Z GET /api/orders 404 150ms tenant=c3",
        "2026-05-01T12:00:05Z DELETE /api/orders 204 1000ms tenant=a1",
        # 注意等于1000不算slow，>1000才算，所以2000算，1500等。
        "2026-05-01T12:00:06Z GET /api/items 200 300ms tenant=b2",
        # 重复测试top_paths
        "2026-05-01T12:00:07Z GET /api/orders 200 110ms tenant=a1",
        #
        "malformed line",
        "2026-05-01T12:00:08Z GET /api/orders 200 120ms tenant=a1",
        "2026-05-01T12:00:09Z GET /api/orders 200 130ms tenant=a1",
        "2026-05-01T12:00:10Z GET /api/orders 200 140ms tenant=a1",
        # 又有路径
        "2026-05-01T12:00:11Z GET /api/users 200 210ms tenant=a1",
        "2026-05-01T12:00:12Z GET /api/items 200 400ms tenant=b2",
        "2026-05-01T12:00:13Z GET /api/items 200 350ms tenant=b2",
        "2026-05-01T12:00:14Z POST /api/login 200 500ms tenant=c3",
        # 错误状态行
        "2026-05-01T12:00:15Z POST /api/login 401 100ms tenant=c3",
        "2026-05-01T12:00:16Z POST /api/login 500 600ms tenant=c3",
        "2026-05-01T12:00:17Z GET /api/orders 500 3000ms tenant=a1",  # slow
        # 额外慢请求
        "2026-05-01T12:00:18Z GET /api/slow 200 5000ms tenant=b2",
        # 验证保留原始行
    ]
    # 注意，处理前给每个行加换行，但process_input会换行，这里不需要.
    # 直接传递行列表，每行包含换行? process_input会rstrip，所以我们传递字符串带有换行? 最好保持一致默认输入。
    # 这里我们传递不带换行的字符串，process_input会使用rstrip，没问题。
    # 但为了模拟真实输入，行没有换行也可以，因为我们在process_input中对每行line.rstrip('\n')，如果没有换行也无影响。
    # 所以直接使用lines。
    result = process_input(lines)
    # 检查malformed
    assert result['malformed_lines'] == 1, f"expected 1 malformed, got {result['malformed_lines']}"
    # total_requests: 共17行，1条malformed，所以16有效。
    assert result['total_requests'] == 16
    # status_counts: 统计status
    # 统计一下：200: ?
    # 行:
    # 200: 1,2,6,9,10,11,12? 很多，需要数一下
    # 但我们可以简单用代码验证，但是手动确认：
    # 200: 1 GET /api/orders 200, 2 GET /api/users 200, 6 GET /api/orders 200(10->04?), 9 GET /api/orders 200,10 GET /api/orders 200,11 GET /api/orders 200? 等一下，时间线:
    # line1: 200, line2:200, line4? 500, line5:404, line6:204? 第6行是DELETE 204，不是200;
    # 重新编号（0-based）:
    # 索引: lines[0] 200, lines[1] 200, lines[2] 201, lines[3] 500, lines[4] 404, lines[5] 204, lines[6] 200, lines[7] malformed, lines[8] 200, lines[9] 200, lines[10] 200, lines[11] 200, lines[12] 200?
    # 更好详细列出每行状态:
    # 0:200
    # 1:200
    # 2:201
    # 3:500
    # 4:404
    # 5:204
    # 6:200
    # 7:malformed
    # 8:200
    # 9:200
    # 10:200
    # 11:200
    # 12:200
    # 13:200
    # 14:200
    # 15:401
    # 16:500
    # 17:500 (line16? 第16行? 我加了额外行，可能搞乱)

    我需要仔细列出测试数据。

我们构建测试时，最好用固定数据集并预期输出。

让我们重新写一个小的测试数据集，手动计算预期结果。

由于时间原因，我们可以只验证关键点，不验证全部。测试主要是确保功能正常。

我们仍旧可以写具体的断言检查一些值。

例如，计算 p95 对于某个路径。

在测试中，我们可以写多个独立测试。

我打算简单设计。

由于这是代码的一部分，我们最好保证测试全面但不冗长。

根据需求，我们应该至少测试：

- 解析正确/错误
- 空行/路径带查询
- 多个请求统计是否正确
- 慢请求排序和截断
- p95 计算正确性 (用简单数据)
- tenant 错误率计算
- 边界条件：慢请求正好1000ms不应计入；有租户无错误；所有请求都错误等。

因为时间有限，但我们必须实现测试。我会写出一个 test_all 函数包含多个测试块，使用 assert。

注意：测试时我们不需要从stdin读取，直接用函数。

为了支持--test，我们在main中检查sys.argv。

代码应该不超过1000行，没问题。

现在实现整个脚本。

特殊考虑：

- 耗时字段是数字后跟ms，如123ms，我们提取数字。
- 状态码：三位数字，我们保留为了排序，把key转为int排序。
- 租户：假设格式 tenant=value，没有空格等。
- 路径可能包含查询参数，用?分割。

正则表达式细节：注意路径可能包含空格？HTTP URL不会包含空格，所以使用\S+。

注意输入的时区是Z，我们不需要解析时间，所以只验证格式。

正则可能需要处理大小写？方法是大写。

也可以更宽松，但按说明。

现在开始写代码。

代码结构：

```python
#!/usr/bin/env python3
import re
import sys
import json
import math
# 可能引入 collections 用于 OrderedDict? 不需要，dict 有序。

def parse_line(line):
    # ... return dict or None

def process_input(lines):
    # ...

def format_output(result):
    # 按照要求输出 JSON，无额外输出
    return json.dumps(result, ensure_ascii=False, indent=2) # 或者 compact

# 测试函数
def test_parse_line():
    # ...

def test_p95():
    # ...

def test_process():
    # ...

def test_all():
    test_parse_line()
    test_p95()
    test_process()
    # 等等
    print("All tests passed.")

def main():
    if '--test' in sys.argv[1:]:
        test_all()
        return
    lines = sys.stdin.readlines()
    result = process_input(lines)
    output_json = json.dumps(result, ensure_ascii=False)
    sys.stdout.write(output_json)

if __name__ == '__main__':
    main()
```

但注意：在test_all()中我们调用test_parse_line()等，它们使用assert，如果失败会引发AssertionError。

现在具体实现每个函数。

parse_line使用正则。注意我们定义LINE_RE为模块级常量，提高效率。

在process_input中，我们使用lines列表。但注意，来自stdin的行有换行符，我们在process_input内部每个line.rstrip('\n')。如果我们在测试时传递没有换行的字符串，rstrip不影响。但为了统一，我们可以在process_input里rstrip('\n')。

慢请求：保留原始行，需要注意：如果原始行包含换行我们去掉，所以original_line是去掉换行的。但测试时如果我们直接给字符串，rstrip('\n')没用。

错误处理：malformed_lines计数，不把它们当作有效请求。

现在开始写具体代码。

潜在问题：路径可能包含空格？假设没有。

tenant格式：tenant=xxx，xxx可能包含数字字母下划线等。我们用\S+，但如果租户值内部有空格则不能捕获，但输入假设无空格。

同时注意性能：如果输入很大，但最多1000行？没有限制，但我们的处理O(n)足够。

p95排序：latencies_by_path每个路径的延迟列表，我们排序后取p95。n=1时，pos=ceil(0.95)=1，取索引0，正确。n=2时，pos=ceil(1.9)=2，取第二大的值，合理。

注意定义：p95定义为排序后向上取整位置。例如总共有10个请求，0.95*10=9.5，向上取整为10，取第10个（最大延迟）。如果总共有2个请求，0.95*2=1.9向上取整=2，取第二大（也就是最大）。如果总共有1个，取该值。

所以我们的实现正确。

但注意：如果n=0（不可能，因为路径至少一个请求）。

slow_requests：大于1000ms，前10，按latency降序。如果少于10个，返回全部。注意latency==1000不算大于。

tenant_error_rates：4xx/5xx算错误。包含400-499,500-599。我们检查status>=400。

现在写测试。

测试parse_line：

```python
def test_parse_line():
    # 正常行
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    r = parse_line(line)
    assert r is not None
    assert r['path'] == '/api/orders'
    assert r['method'] == 'GET'
    assert r['status'] == 200
    assert r['latency'] == 123
    assert r['tenant'] == 'a1'
    assert r['original_line'] == line  # no newline

    # 路径带查询
    line2 = "2026-05-01T12:03:18Z POST /api/orders?page=2 201 456ms tenant=abc"
    r2 = parse_line(line2)
    assert r2['path'] == '/api/orders'
    assert r2['method'] == 'POST'
    assert r2['status'] == 201
    assert r2['latency'] == 456
    assert r2['tenant'] == 'abc'

    # 其他方法
    line3 = "2026-05-01T12:03:18Z PUT /api/item 200 789ms tenant=test1"
    assert parse_line(line3) is not None

    # 错误格式
    assert parse_line("") is None
    assert parse_line("  ") is None
    assert parse_line("invalid line") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms") is None  # 缺少tenant
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 abcms tenant=a1") is None  # 耗时不是数字
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 2000 123ms tenant=a1") is None  # 状态码4位
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 20 123ms tenant=a1") is None  # 状态码2位
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=") is None  # 租户空
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1 extra") is None  # 多余字段
    print("test_parse_line OK")
```

测试p95：

```python
def test_p95():
    # 测试p95计算
    # 手动
    lats = [1,2,3,4,5,6,7,8,9,10]  # n=10
    # 0.95*10=9.5 ceil=10 -> value=10
    lats.sort()
    n=10
    pos = math.ceil(0.95*n)  # 10
    assert pos == 10
    assert lats[pos-1] == 10

    # n=1
    lats2 = [100]
    n=1
    pos = math.ceil(0.95*n)
    assert pos == 1
    assert lats2[pos-1] == 100

    # n=2: [10, 20] => 0.95*2=1.9 ceil=2 -> 20
    lats3 = [10,20]
    n=2
    pos = math.ceil(0.95*2)
    assert pos == 2
    assert lats3[pos-1] == 20

    # n=20: [1..20] -> 0.95*20=19 ceil=19 -> index 18 (19th)
    lats4 = list(range(1,21))
    n=20
    pos = math.ceil(0.95*20)  # 19 exactly? ceil(19.0)=19
    # 但如果0.95*20=19.0，ceil=19，取第19个（从1开始），对应lats4[18]=19
    assert pos == 19
    assert lats4[pos-1] == 19

    # n=11: [1..11]
    lats5 = list(range(1,12))
    n=11
    pos = math.ceil(0.95*11)  # 10.45 ceil=11
    assert pos == 11
    assert lats5[pos-1] == 11
    print("test_p95 OK")
```

注意在process_input中我们使用math.ceil，这里测试了逻辑。

测试process函数：

我们可以构建一个小数据集，预期输出，然后比较JSON。但比较整个字典可能繁琐。我们可以只检查关键部分。

但我们应至少检查一些计算值。

例如：

```python
def test_process():
    lines = [
        "2026-05-01T12:00:00Z GET /api/orders 200 100ms tenant=a1",
        "2026-05-01T12:00:01Z GET /api/users 200 200ms tenant=a1",
        "2026-05-01T12:00:02Z POST /api/orders 201 50ms tenant=b2",
        "2026-05-01T12:00:03Z GET /api/orders 500 2000ms tenant=a1",
        "2026-05-01T12:00:04Z GET /api/orders 404 150ms tenant=c3",
        "2026-05-01T12:00:05Z GET /api/somepath 200 5000ms tenant=b2",
        # 慢请求，超过1000
        "malformed line",
        "2026-05-01T12:00:06Z GET /api/orders 200 120ms tenant=a1", # 第7行（索引7）
        # 测试重复路径
        "2026-05-01T12:00:07Z GET /api/orders 200 130ms tenant=a1",
        "2026-05-01T12:00:08Z GET /api/orders 200 140ms tenant=a1",
        # 增加一些使top_paths出现更多
        "2026-05-01T12:00:09Z GET /api/users 200 300ms tenant=a1",
        "2026-05-01T12:00:10Z GET /api/users 200 310ms tenant=a1",
        # 慢请求正好1000不算
        "2026-05-01T12:00:11Z GET /api/orders 200 1000ms tenant=b2",
        #
        "2026-05-01T12:00:12Z GET /api/items 200 500ms tenant=c3",
        "2026-05-01T12:00:13Z GET /api/items 200 600ms tenant=c3",
        # 错误请求
        "2026-05-01T12:00:14Z POST /api/login 401 100ms tenant=c3",
        "2026-05-01T12:00:15Z POST /api/login 500 200ms tenant=c3",
        # 新的慢请求
        "2026-05-01T12:00:16Z GET /api/slow 200 1500ms tenant=b2",
    ]
    # 总行数: 17? 数一下: lines有... 我们待会数。
    # 实际上共17行？从0到16，索引0-16是17行，其中有一个malformed，有效16。
    result = process_input(lines)
    assert result['malformed_lines'] == 1
    assert result['total_requests'] == 16  # 验证一下
    # status_counts: 我们测试一些值
    # 统计状态码: 200: 出现很多，201:1, 500:2 (索引3和索引16? 索引3是500, 索引16? 最后一条不是500，索引15是500), 404:1, 401:1,
    # 204? 没有，1000? 没有。
    # 具体:  行索引0:200,1:200,2:201,3:500,4:404,5:200,6:malformed,7:200,8:200,9:200,10:200,11:200? 索引11是1000ms的200, 12:200,13:200,14:401,15:500,16:200? 16: GET /api/slow 200 1500ms tenant=b2
    # 所以200: 索引0,1,5,7,8,9,10,11,12,13,16 = 11个? 数:0,1,5,7,8,9,10,11,12,13,16 = 11个。201:1个,500:2个,404:1,401:1。总16。
    assert result['status_counts'].get('200') == 11
    assert result['status_counts'].get('500') == 2
    assert result['status_counts'].get('401') == 1
    assert result['status_counts'].get('201') == 1
    assert result['status_counts'].get('404') == 1
    # 其他断言

    # top_paths: 按频率降序。路径频率:
    # /api/orders: 索引0,2,3,4? 注意:索引0:orders,2:orders,3:orders,4:orders? 索引4: /api/orders? line4是404？是的。索引7,8,9,11? 索引10? 不索引10是users。索引11是orders。所以orders出现: 0,2,3,4,7,8,11? 还有? 索引? 索引16是slow。orders: index0,2,3,4,7,8,11 = 7个? 再数: index0(200),2(201),3(500),4(404),7(200),8(200),11(200) = 7次
    # /api/users: index1,{9? line9是users? 索引10是users? 我们需要重新列出索引对应路径:
    # 0: /api/orders
    # 1: /api/users
    # 2: /api/orders
    # 3: /api/orders
    # 4: /api/orders (404)
    # 5: /api/somepath (索引5)
    # 6: malformed
    # 7: /api/orders
    # 8: /api/orders
    # 9: /api/orders (索引9? 根据line字符串，9是GET /api/orders 200 130ms)
    # 10: /api/users (索引10 130? 我们是/ api/users 200 300?)
    # 11: /api/orders (1000ms)
    # 12: /api/items
    # 13: /api/items
    # 14: /api/login
    # 15: /api/login
    # 16: /api/slow
    # 重新列表更清晰：
    # lines列表:
    # 0 '2026-05-01T12:00:00Z GET /api/orders 200 100ms tenant=a1'
    # 1 '2026-05-01T12:00:01Z GET /api/users 200 200ms tenant=a1'
    # 2 '2026-05-01T12:00:02Z POST /api/orders 201 50ms tenant=b2'
    # 3 '2026-05-01T12:00:03Z GET /api/orders 500 2000ms tenant=a1'
    # 4 '2026-05-01T12:00:04Z GET /api/orders 404 150ms tenant=c3'
    # 5 '2026-05-01T12:00:05Z GET /api/somepath 200 5000ms tenant=b2'
    # 6 'malformed line'
    # 7 '2026-05-01T12:00:06Z GET /api/orders 200 120ms tenant=a1'
    # 8 '2026-05-01T12:00:07Z GET /api/orders 200 130ms tenant=a1'
    # 9 '2026-05-01T12:00:08Z GET /api/orders 200 140ms tenant=a1'
    # 10 '2026-05-01T12:00:09Z GET /api/users 200 300ms tenant=a1'
    # 11 '2026-05-01T12:00:10Z GET /api/users 200 310ms tenant=a1'
    # 12 '2026-05-01T12:00:11Z GET /api/orders 200 1000ms tenant=b2'
    # 13 '2026-05-01T12:00:12Z GET /api/items 200 500ms tenant=c3'
    # 14 '2026-05-01T12:00:13Z GET /api/items 200 600ms tenant=c3'
    # 15 '2026-05-01T12:00:14Z POST /api/login 401 100ms tenant=c3'
    # 16 '2026-05-01T12:00:15Z POST /api/login 500 200ms tenant=c3'
    # 17 '2026-05-01T12:00:16Z GET /api/slow 200 1500ms tenant=b2'
    # 总共18行？从0到17是18行？索引17是最后一条? 上面我们写了17行，但按这里索引最后是17 (因为索引从0开始，有18行)。我们重新数行数：输入列表共有多少个元素？我们写了从0到17共18行？检查：开始从0到17是18行。但是我们count_lines感觉更多。我们写代码时应当明确。
    # 简单起见，我们只验证部分，确保功能。

    # 还是不这样复杂，直接测试其他方面。
    # 测试slow_requests: 大于1000ms且按降序前10。
    # 慢请求有: 索引3 latency 2000, 索引5 5000, 索引17 1500? 注意索引12 latency=1000(不算), 所以索引3,5,17。可能还有索引? 没有。
    # 所以slow_requests应该有3条。顺序: 5000,2000,1500 (降序)
    slow_reqs = result['slow_requests']
    assert len(slow_reqs) == 3
    assert slow_reqs[0]['latency'] == 5000
    assert slow_reqs[1]['latency'] == 2000
    assert slow_reqs[2]['latency'] == 1500
    # 检查original_line包含原始行
    assert slow_reqs[0]['path'] == '/api/somepath'
    # 检查原始行内容（没有换行）
    assert slow_reqs[0]['original_line'] != lines[5]  # lines[5]对应原始行（但rstrip(\n)后相同），但这里我们给的是无换行，所以equal
    # 确保latency>1000

    # tenant_error_rates: 三个租户:
    # a1: 请求: 索引0,1,3,7,8,9,10,11? 索引10是a1? line10: 200 300ms tenant=a1 是的。索引11: a1? line11是a1. 所以a1有:0,1,3,7,8,9,10,11 = 8? 但索引0 a1,1 a1,3 a1,7 a1,8 a1,9 a1,10 a1,11 a1 = 8。错误请求: 索引3 (500) 所以错误数1。错误率1/8=0.125， round 3 = 0.125
    # b2: 请求: 索引2,5,12,17 = 4个。错误: 索引2是201（不算错误），索引5 200，索引12 200，索引17 200 -> 0错误，错误率0。
    # c3: 请求: 索引4,13,14,15,16 = 5个? 索引4是404算错误；索引13 200;索引14 200;索引15 401错误;索引16 500错误; 所以错误请求3个，错误率3/5=0.6，round=0.6
    # 注意索引15 401算错误，索引4 404, 索引16 500 => 三个错误。
    # 检查:
    tenant_rates = result['tenant_error_rates']
    assert tenant_rates['a1'] == 0.125
    assert tenant_rates['b2'] == 0.0
    assert tenant_rates['c3'] == 0.6
    # 测试p95_by_path: 对于一些路径可以验证简单
    # 例如 /api/login 有2个请求，latencies [100,200]？索引15 100ms, 索引16 200ms => 排序[100,200], n=2, p95 pos=ceil(1.9)=2 => latency=200
    assert result['p95_latency_by_path'].get('/api/login') == 200
    # /api/slow 1个请求，latency 1500 => p95=1500
    assert result['p95_latency_by_path'].get('/api/slow') == 1500
    # /api/items 2个，[500,600] => p95=600
    assert result['p95_latency_by_path'].get('/api/items') == 600
    # /api/users 3个? 索引1(200),10(300),11(310) -> 排序[200,300,310], n=3, 0.95*3=2.85 ceil=3 => 310
    assert result['p95_latency_by_path'].get('/api/users') == 310
    # /api/orders 多个，n= ? 索引0,2,3,4,7,8,9,12? 共8个? 索引0:100,2:50,3:2000,4:150,7:120,8:130,9:140,12:1000 => latencies [50,100,120,130,140,150,1000,2000] 排序[50,100,120,130,140,150,1000,2000] n=8 pos=ceil(7.6)=8 => 2000
    assert result['p95_latency_by_path'].get('/api/orders') == 2000
    # 检查top_paths: 前5应当包含/orders (count 8), /users (3), /items (2), /login (2), /somepath (1) or /slow(1) 根据count降序, tie需要按path字典序。我们期望：/api/orders:8, /api/users:3, /api/items:2, /api/login:2, /api/somepath:1 (或者/api/slow:1) 取决于排序。当count相同时，按path字符串排序。所以items和login count都是2，items < login (按字符串/api/items < /api/login? 是的 'i' < 'l'), 所以items在login前。接下来count1的路径: /api/slow, /api/somepath 两个， '/api/slow' vs '/api/somepath'? s和s开头，o和o? s-o-m-e vs s-l-o-w: both start with /api/s, then 'l' vs 'o'? 'l' < 'o', so '/api/slow' < '/api/somepath'. 所以我们期望前5: /api/orders(8), /api/users(3), /api/items(2), /api/login(2), /api/slow(1). 但需要确认count1的谁被包括？前5仅5个，我们有8+3+2+2+1+1（...）所以取前5，即orders(8), users(3), items(2), login(2), and the smallest count1 path alphabetically -> /api/slow。所以top_paths应该有5个。
    top = result['top_paths']
    assert len(top) == 5
    assert top[0]['path'] == '/api/orders' and top[0]['count'] == 8
    assert top[1]['path'] == '/api/users' and top[1]['count'] == 3
    assert top[2]['path'] == '/api/items' and top[2]['count'] == 2
    assert top[3]['path'] == '/api/login' and top[3]['count'] == 2
    assert top[4]['path'] == '/api/slow' and top[4]['count'] == 1
    # 检查malformed_lines
    assert result['malformed_lines'] == 1
    # 可能还有其他检查
    print("test_process OK")
```

注意，我前面索引有误解，但根据实际lines我调整为上面列表（18行）。在测试代码中我们使用这个列表。需要确保我的计数准确。

但是我在上面写test_process中定义的lines里我数了一下：从0到17共18行。其中malformed一行，所以有效17? 不行我们需要确保统计正确：之前我说malformed=2? 不，只有1行malformed line? 上面列表没有其他malformed? 有一个'malformed line'行。所以malformed=1。但我之前说total 16, 但实际可能会出现17有效? 因为如果18行总，1行malformed，17有效。而我之前的断言期望total=16可能是错的。需要修正。

在我们实际创建测试时，需要精确计算。

为了避免混淆，我们可以简化测试数据，至最少而覆盖全部功能。但为了完整测试，建议使用可控的小数据集，手动计算结果。但上面的测试数据已经偏大，我们可以减少。

或者我们可以使用更简洁的测试数据并硬编码预期。但为了节省时间，我测试会根据我写的lines严格计数。

但上面我写的lines实际有18行（从0到17）。我们来数一下：

我逐行写出：

```
line0: "2026-05-01T12:00:00Z GET /api/orders 200 100ms tenant=a1"
line1: "2026-05-01T12:00:01Z GET /api/users 200 200ms tenant=a1"
line2: "2026-05-01T12:00:02Z POST /api/orders 201 50ms tenant=b2"
line3: "2026-05-01T12:00:03Z GET /api/orders 500 2000ms tenant=a1"
line4: "2026-05-01T12:00:04Z GET /api/orders 404 150ms tenant=c3"
line5: "2026-05-01T12:00:05Z GET /api/somepath 200 5000ms tenant=b2"
line6: "malformed line"
line7: "2026-05-01T12:00:06Z GET /api/orders 200 120ms tenant=a1"
line8: "2026-05-01T12:00:07Z GET /api/orders 200 130ms tenant=a1"
line9: "2026-05-01T12:00:08Z GET /api/orders 200 140ms tenant=a1"
line10: "2026-05-01T12:00:09Z GET /api/users 200 300ms tenant=a1"
line11: "2026-05-01T12:00:10Z GET /api/users 200 310ms tenant=a1"
line12: "2026-05-01T12:00:11Z GET /api/orders 200 1000ms tenant=b2"
line13: "2026-05-01T12:00:12Z GET /api/items 200 500ms tenant=c3"
line14: "2026-05-01T12:00:13Z GET /api/items 200 600ms tenant=c3"
line15: "2026-05-01T12:00:14Z POST /api/login 401 100ms tenant=c3"
line16: "2026-05-01T12:00:15Z POST /api/login 500 200ms tenant=c3"
line17: "2026-05-01T12:00:16Z GET /api/slow 200 1500ms tenant=b2"
```

总18行。有效行数：17（除去line6）。但之前我错误地认为有效16，实际上是17。

但现在我要确认status_counts等的统计：

- 请求总数 total_requests = 17
- status_counts:
  200: 哪些是200? line0,1,5,7,8,9,10,11,12,13,14,17? line12是200? line12是200吗? line12是"GET /api/orders 200 1000ms tenant=b2" 是的200; line13 200; line14 200; line17 200. 另外还有line? line? 总共200的次数: line0,1,5,7,8,9,10,11,12,13,14,17 = 12个? 数: 0,1,5,7,8,9,10,11,12,13,14,17 → 12个。201: line2 (1个). 500: line3,16 -> 2个. 404: line4 (1个). 401: line15 (1个). 所以总: 12+1+2+1+1=17。好，total_requests=17。

- top_paths: 路径计数：
  /api/orders: line0,2,3,4,7,8,9,12 -> 8次? line0,2,3,4,7,8,9,12 = 8次。line? 还有? 没有，所以8个。
  /api/users: line1,10,11 -> 3次。
  /api/items: line13,14 -> 2次。
  /api/login: line15,16 -> 2次。
  /api/somepath: line5 -> 1次。
  /api/slow: line17 -> 1次。
  所以order 8 > users 3 > items 2, login 2 (items<login? /api/items < /api/login 字母序: i<l所以items在前), somepath 1, slow 1 (slow < somepath? /api/slow vs /api/somepath: 'slow' vs 'somepath', 'l' vs 'o', l<o so slow < somepath)。所以前5: orders(8), users(3), items(2), login(2), slow(1). 注意到somepath(1)被排除因为只有5个位置而slow字母序更小。

- slow_requests: latency > 1000: line3:2000, line5:5000, line17:1500, line? line12:1000不算, 所以3条。排序降序: 5000,2000,1500。所以慢请求3条。

- tenant_error_rates:
  a1: 请求有哪些？line0,1,3,7,8,9,10,11 = 8次? 0(a1),1(a1),3(a1),7(a1),8(a1),9(a1),10(a1),11(a1) = 8次。其中错误: line3(500) -> 1错误。错误率=1/8=0.125。
  b2: 请求: line2,5,12,17 = 4次。错误: line5是200, line2是201, line12是200, line17是200 → 0错误。率=0.0。
  c3: 请求: line4,13,14,15,16 = 5次? line4(a1? 不line4是c3),13(c3),14(c3),15(c3),16(c3) → 5次。错误: line4(404), line15(401), line16(500) → 3错误。率=3/5=0.6。

- p95_latency_by_path:
  /api/orders: latencies [100,50,2000,150,120,130,140,1000]; 排序 [50,100,120,130,140,150,1000,2000]; n=8, pos=ceil(7.6)=8 -> 2000.
  /api/users: [200,300,310]; 排序[200,300,310]; n=3, pos=ceil(2.85)=3 -> 310.
  /api/items: [500,600]; n=2, pos=2 -> 600.
  /api/login: [100,200]; n=2 pos=2 -> 200.
  /api/somepath: [5000]; n=1 pos=1 -> 5000.
  /api/slow: [1500]; n=1 -> 1500.

- malformed_lines: 1 (line6).

所以可以断言这些值。

但是，我需要再检查一下line9路径：line9是/api/orders（140ms）吗？在test_process中我写的是"GET /api/orders 200 140ms tenant=a1"，是的。

这些数据产生以上统计。

现在，在test_process中，我们可以使用这些断言。

注意：top_paths我们期望恰好5个条目，因为我们有6个不同路径（orders,users,items,login,somepath,slow）共6。但只取前5。我们期望前5如上。

现在测试代码可能要重新调整以确保正确。

还有一个注意点：top_paths是取前5，如果第5名有多个相同count，如何处理？题目没有明确，通常按某种规则选前5，可能任意选但建议按路径字典序补齐。我们的排序是(-count, path)，对于count相同的路径，按字母序所以会包含字典序最小的。但可能会超过5个相同count? 比如第5名和6名count相同，我们只取前5，可能包含第5个但忽略第6个。可以接受。本题不涉及平局，但如果出现，我们的排序会决定，但因为是确定的，应该可以。

我需要确保测试中抑制无关输出。test函数中只打印成功消息。

现在讨论输出JSON的格式：中要求只输出JSON，不输出解释文字。所以在非测试模式下只打印JSON。

我们使用时，输出JSON到stdout。

测试函数可以打印自己的结果，但如果使用assert，失败时抛出异常，测试不会输出多余。但我也可以在test_all里打印成功信息，但正常运行时如果执行测试会打印“All tests passed.”，但这可以认为是测试的输出，符合“当使用 --test 参数运行时执行测试”，测试可以有输出。但要求“正常运行时只输出 JSON，不输出解释文字”，意味着测试模式不受限。所以测试可以输出信息。

现在，代码结构。

额外考虑：我们在process_input中，使用了math.ceil。需要import math。但我们在文件开头统一导入。

我们还需要考虑输入可能来自stdin，可能包含BOM？不考虑。

另一个注意：如果输入包含空行，跳过，不计入malformed。我们的正则不会匹配空行，所以parse_line返回None，我们递增malformed。但题目要求跳过无法解析的行，空行也算吗？通常空行应该跳过不计入malformed？但按说明“跳过无法解析的行，并在输出中给出 malformed_lines 数量”，所以无法解析都应该计入，包括空行。但有些实现可能跳过空行，不计入malformed？没有明确，但谨慎起见，空行不能解析（正则不匹配），所以计入malformed。但可能有些用户会输入空行，我们会认为无效。但我们可以特殊处理空行：跳过且不计入malformed？但题目：“跳过无法解析的行，并在输出中给出 malformed_lines 数量”，所以无法解析的行算malformed，空行算无法解析。所以应该包括。但很多工具会忽略空行。我们决定：对空行，parse_line返回None，算malformed。但也可以选择跳过不计，但标准不明确。我选择按照正常逻辑，空行无法匹配，所以malformed加1。但这可能影响计数。但我们可以改进：如果行strip为空，跳过且不计malformed。但题目没说。为保险，我们选择跳过空行，不计入malformed（通常日志不会有空行，但如果有，我们不计）。但这个问题可能是在测试时可能有空行？我们看需求：希望跳过无法解析的行，一般空行也是无法解析，但个人认为跳过应该包括空行不计malformed？其实很多工具对空行是直接忽略，不视为错误。但题目没明确，我们两种都有道理。为了符合常见习惯，我决定空行也计入malformed，因为它确实无法解析。但测试中我们可以考虑空行为malformed。但用户可能输入空行会意外增加malformed。我觉得跳过且不计malformed更友好。我们来分析：要求“跳过无法解析的行，并在输出中给出 malformed_lines 数量”。这里“跳过”意味着不处理这部分行；“malformed_lines数量”表示这些无法解析的行有多少。所以无法解析的行应该计入malformed。如空行，我们无法解析，所以应该计入。但有些实现可能会忽略空行不算，但我觉得严格按说明应该算。但为了不产生歧义，我们选择将空行视为malformed。不过在我们的正则中，空行不匹配，所以parse_line返回None，我们会增加malformed。所以符合。

但注意我们的process_input在遍历lines时，我们没有预先跳过空行，我们直接每行rstrip后判断是否为空? 我们之前代码是：

```python
for line in lines:
    line = line.rstrip('\n')
    if not line:  # 跳过空行
        continue
    result = parse_line(line)
    ...
```

这样我们跳过了空行并且不计数malformed。我们需要决定是否保留这个跳过。我认为跳过空行更合理，因为空行不是错误格式，只是空。但需求可能希望malformed包括空行。我参考一些类似题目通常不计空行为错误。但我们按自己的决定。但为了安全，我们可以保留跳过空行，但题目没有明确，我选择跳过。但在我之前的process_input代码中，我已经写了跳过空行。在测试的时候，我们没有空行，所以不影响。我保留这个行为：空行直接跳过，不计数。

但是，我们需要注意，如果测试需要验证空行计数，但我不打算测空行。

现在考虑输出JSON时，对数字的处理：对于tenant_error_rates，我们使用了round(rate,3)，但这可能产生0.0,0.125等。在JSON输出时，0.125显示0.125，0.6显示0.6，0.0显示0.0。题目要求保留三位小数，但JSON中0.6和0.600一样。所以我认为可以。

但为了确保，我们可以将rate格式化为三位小数的字符串，但会变成字符串，不符合要求（数字）。所以保持数字。

在status_counts中，我们构建字典时键是字符串，因为JSON要求键是字符串，我们已经是字符串。

top_paths中是对象列表。

slow_requests中的latency是整数，original_line是字符串。

所有整数（total_requests, malformed_lines, p95 latency等）都是int。

现在考虑输出可能很大的无格式JSON。但测试可能需要比较，我们也可以保持indent=None，紧凑输出。但是如果我们对字典排序，输出可能是固定的。

我们还可以使用json.dumps的sort_keys=False，因为我们手动排序。我们不需要sort_keys，因为我们已经排序。

注意：默认json.dumps不排序键，顺序是插入顺序。所以我们希望status_counts是从小到大排序。我们在输出前重新排序status_counts，将其按int键排序，然后重建为dict，但Python 3.7+会保持插入顺序，所以我们用sorted构建。我们可以直接使用Dict排序：status_counts = dict(sorted(status_counts.items(), key=lambda x: int(x[0]))) 这样插入顺序就是数字递增。

同理tenant_error_rates按键排序：tenant_error_rates = dict(sorted(tenant_error_rates.items()))。

p95_by_path也排序：p95_by_path = dict(sorted(p95_by_path.items()))。

这样输出稳定。

但注意，top_paths已经是有序列表，p95_by_path排序不影响，但更一致。

现在写最终代码。

先完成parse_line。

但是还有一点：正则表达式中，我们用\S+匹配路径，这样可以匹配带查询参数的路径吗？例如`/api/orders?page=2`，没问题，因为?不是空白，属于\S。然后又用split('?')规范。

对于时间，我们使用简单的格式匹配，不验证日期合理性，仅格式。

现在开始编写。

我们可能还需要处理一些边缘情况：状态码是三位数字，但是否可能包含前导零？如`200`是三位数字，但输入可能`200`，没问题。正则\d{3}匹配三位数字。耗时是数字+ms，如`123ms`。注意耗时可能`0ms`? 可能。所以用\d+ms，匹配。

租户格式：`tenant=xxx`，xxx用\S+，但可能包含=？不会。但注意租户可能包含点或斜杠？但通常日志中租户一般没有空格，所以\S+够用。

如果租户值包含空格，则可能解析失败，但输入规范未提及，所以假设不带空格。

现在我们写代码。

注意：原始行保留时尽量保留原始内容，包括可能的前后空格？但是我们在process_input中line = line.rstrip('\n')，这不会去除行首空格，但原始行可能有前导空格？标准日志没有。所以我们保留。

但是，在解析时，我们的正则要求行开始没有空格，所以如果有前导空格，行被视为malformed。这样做参数或跳过？可能合理。

现在，在process_input中，我们保留了每个entry的original_line为line.rstrip('\n')，也就是去除了换行符。但如果我们读取的是sys.stdin的readlines()，得到的内容包含换行。所以我们在process_input外部读入时选择不预先rstrip，在内部处理每行时rstrip。这样一致。

注意：在测试时如果我们直接传递字符串列表（无换行），rstrip('\n')不影响。

现在实现。

额外要求：单文件，总代码不超过1000行。肯定满足。

现在开始写最终代码。我将包括全部上述功能。

可能还需要一些输出JSON的辅助：如json.dumps的ensure_ascii=False允许非ASCII字符，但路径应该是ASCII。

为了安全，我们设置ensure_ascii=False。

现在编写。

请注意：parse_line函数应该可以多次调用，所以正则编译为全局变量。

注意：process_input可能需要在处理每一行后更新统计，所以上面代码正确。

关于性能，不必担心。

现在做一个审查：

- 在process_input中，我们使用latencies_by_path.setdefault(path, []).append(latency)。但之后排序该列表。注意每个路径的列表会修改，我们后来sort，可以接受，因为只使用一次。

- 对于慢请求，我们使用列表slow_candidates，最后排序取前10。

- 注意慢请求的原始行保留，我们从parsed entry里取original_line，这是原始行（rstrip('\n')后），但最开始输入时，可能就带有换行，但我们去除了换行。用户期望slow_requests中显示的行应该是原始行，如果我们从readlines得到line包含换行，我们已经在处理时去除了。所以original_line是整行但不含换行。这通常是我们需要的。

在测试中，如果我们直接传入无换行的字符串，那么original_line就是该字符串，所以我们断言时比较相等没问题。如果手动从stdin输入，删除换行也是常见的。

现在所有设计完成。

测试函数各写一个。其中test_process要使用上面的lines列表，断言我们调整后的值。

确保test_process中的计数与上面一致。

为了确保不会意外失误，我重新确认lines列表（基于之前的调整），包括我后来可能略有改动但保持一致。

下面我定义一个test_process函数，使用上述列表并做所有断言。

但此前，我们注意到在test_process中，我原来写了top为5个断言，需要根据我们新的top预期。我们需要重写预期。

我决定按照我们上面推导的预期来写断言。

但还有一个潜在问题：在测试数据中，line15和line16是login，路径都是/api/login。line15是401（错误），line16是500（错误）。所以login p95 latencies [100,200] p95=200。

现在，测试时还要考虑排序：top_paths按count降序，同count字母序升序。

所以我们top_paths期望数组：

[
  {"path": "/api/orders", "count": 8},
  {"path": "/api/users", "count": 3},
  {"path": "/api/items", "count": 2},
  {"path": "/api/login", "count": 2},
  {"path": "/api/slow", "count": 1}
]

因为/api/items和/api/login都是2，但i<l所以items在前。然后count 1的路径有/api/slow和/api/somepath，slow字典序小于somepath（s l o w vs s o m e p a t h: l < o）所以slow在前，somepath被排除。

但是，我们测试数据中还有/api/somepath和/api/slow，count都为1。所以前5包括slow，somepath不在。

好。

现在，我们也需要测试p95对于somepath: n=1 p95=5000, 但该路径不在p95输出中? 在p95_by_path字典中应该包含所有路径，包括somepath和slow。所以我们可以检查p95_by_path['/api/somepath'] == 5000。

检查p95_by_path['/api/slow'] == 1500.

现在，注意slow_requests中，我们有3条原始行。断言它们的内容。

现在，注意我们使用的process_input函数在内部对latencies_by_path排序时不保留原列表？但我们每次都在使用前排序，没问题。

关于p95_by_path，我们在输出时决定按键排序，所以最后结果会包含所有路径的p95有序。

现在，考虑malformed_lines。我们只有第6行malformed，所以malformed_lines=1。

现在，测试中，我们还要检查total_requests=17。

检查status_counts: 200:12, 201:1, 500:2, 404:1, 401:1。我前已算200是12次? 检查上面200：line0,1,5,7,8,9,10,11,12,13,14,17 这确实是12个。line12是200（1000ms）。所以12。501? 没有。

现在，test_process函数中将包括这些断言。

同时，因为我们在process_input内将每秒后排序，请注意tenant_error_rates使用了round。

现在我们写完整的测试代码。

注意：在test_process之前，需要定义process_input函数和parse_line，这些在测试时会用到，所以测试函数放在模块内部。

现在，在主模块中，当运行脚本且有--test参数时，执行test_all()。test_all()再调用各测试函数。

现在，我们可能还需要编写一个简单的测试空行。空行会被process_input函数中的 `if not line: continue`跳过，所以不算malformed。我们是否要包含一个空行测试？可以单独测试空行行为，但可选项。

我们还可以测试另一种情况：耗时1000ms不包括在慢请求中。

现在，总结：我们完成了几乎全部。

最后，代码格式清晰。

现在开始写代码脚本。

注意：因为要求单文件，所以不要拆分导入其他模块，只用标准库。

导入: re, sys, json, math

可能用到collections？不需要。

接着定义常量。

现在直接写代码。

我写一个草稿:

```python
#!/usr/bin/env python3
"""
Log Analyzer - Analyze log lines from stdin and output JSON statistics.
"""

import re
import sys
import json
import math

# Regular expression for log line parsing
LINE_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) '
    r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) '
    r'(\S+) '
    r'(\d{3}) '
    r'(\d+)ms '
    r'tenant=(\S+)$'
)

def parse_line(line):
    """
    Parse a single log line.
    Returns a dict with extracted fields if line matches, else None.
    """
    match = LINE_PATTERN.match(line)
    if not match:
        return None
    timestamp, method, path, status_str, latency_str, tenant = match.groups()
    # Remove query parameters from path
    path = path.split('?')[0]
    status = int(status_str)
    latency = int(latency_str)
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status,
        'latency': latency,
        'tenant': tenant,
        'original_line': line  # original line without newline (caller strips)
    }

def process_input(lines):
    """
    Process an iterable of lines (strings possibly with trailing newline).
    Returns a dictionary containing all required statistics.
    """
    # Initialize collectors
    parsed_entries = []
    malformed_count = 0

    for raw_line in lines:
        # Remove trailing newline if present
        line = raw_line.rstrip('\n')
        # Skip empty lines (do not count as malformed)
        if not line:
            continue
        entry = parse_line(line)
        if entry is None:
            malformed_count += 1
        else:
            parsed_entries.append(entry)

    total_requests = len(parsed_entries)

    # Status counts
    status_counts = {}
    # Path frequencies
    path_counts = {}
    # Latencies per path (for p95)
    latencies_by_path = {}
    # Tenant stats: total and error counts
    tenant_stats = {}  # {tenant: {'total': int, 'errors': int}}
    # Slow requests candidate list (latency > 1000)
    slow_candidates = []

    for entry in parsed_entries:
        path = entry['path']
        status = entry['status']
        latency = entry['latency']
        tenant = entry['tenant']

        # Status count
        status_key = str(status)
        status_counts[status_key] = status_counts.get(status_key, 0) + 1

        # Path count
        path_counts[path] = path_counts.get(path, 0) + 1

        # Latency per path
        latencies_by_path.setdefault(path, []).append(latency)

        # Tenant stats
        if tenant not in tenant_stats:
            tenant_stats[tenant] = {'total': 0, 'errors': 0}
        tenant_stats[tenant]['total'] += 1
        if status >= 400:
            tenant_stats[tenant]['errors'] += 1

        # Slow requests (latency > 1000ms)
        if latency > 1000:
            slow_candidates.append({
                'original_line': entry['original_line'],
                'path': path,
                'latency': latency
            })

    # Sort slow requests by latency descending, take top 10
    slow_candidates.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_candidates[:10]

    # Top 5 paths by count, then alphabetically
    # Counts as primary descending, secondary path ascending
    sorted_paths = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # P95 latency per path
    p95_latency_by_path = {}
    for path, lats in latencies_by_path.items():
        lats.sort()
        n = len(lats)
        pos = math.ceil(0.95 * n)  # 1-indexed position
        p95_value = lats[pos - 1]
        p95_latency_by_path[path] = p95_value

    # Tenant error rates
    tenant_error_rates = {}
    for tenant, st in tenant_stats.items():
        total = st['total']
        errors = st['errors']
        rate = errors / total if total > 0 else 0.0
        tenant_error_rates[tenant] = round(rate, 3)

    # Assemble output
    output = {
        'total_requests': total_requests,
        'status_counts': dict(sorted(status_counts.items(), key=lambda x: int(x[0]))),
        'top_paths': top_paths,
        'p95_latency_by_path': dict(sorted(p95_latency_by_path.items())),
        'slow_requests': slow_requests,
        'tenant_error_rates': dict(sorted(tenant_error_rates.items())),
        'malformed_lines': malformed_count
    }
    return output

# -------- Tests --------

def test_parse_line():
    """Test parse_line function."""
    # Valid line
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    res = parse_line(line)
    assert res is not None, "Valid line should parse"
    assert res['path'] == '/api/orders'
    assert res['method'] == 'GET'
    assert res['status'] == 200
    assert res['latency'] == 123
    assert res['tenant'] == 'a1'
    assert res['original_line'] == line

    # Line with query parameters
    line2 = "2026-05-01T12:03:18Z POST /api/orders?page=2 201 456ms tenant=abc"
    res2 = parse_line(line2)
    assert res2 is not None
    assert res2['path'] == '/api/orders'
    assert res2['method'] == 'POST'
    assert res2['status'] == 201
    assert res2['latency'] == 456
    assert res2['tenant'] == 'abc'

    # Different HTTP method
    line3 = "2026-05-01T12:03:18Z PUT /api/item 202 789ms tenant=t1"
    assert parse_line(line3) is not None

    # Malformed lines
    assert parse_line("") is None
    assert parse_line("   ") is None
    assert parse_line("invalid line") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms") is None  # missing tenant
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 abcms tenant=a1") is None  # invalid latency
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 2000 123ms tenant=a1") is None  # 4-digit status
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 20 123ms tenant=a1") is None  # 2-digit status
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=") is None  # empty tenant
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1 extra") is None  # extra content
    print("test_parse_line passed")

def test_p95():
    """Test p95 calculation logic."""
    # Cases for math.ceil
    assert math.ceil(0.95 * 10) == 10
    assert math.ceil(0.95 * 1) == 1
    assert math.ceil(0.95 * 2) == 2
    assert math.ceil(0.95 * 3) == 3  # 2.85 ceil=3
    assert math.ceil(0.95 * 11) == 11  # 10.45 ceil=11
    assert math.ceil(0.95 * 20) == 19  # 19.0 ceil=19
    print("test_p95 passed")

def test_process():
    """Test process_input with a complete example."""
    lines = [
        "2026-05-01T12:00:00Z GET /api/orders 200 100ms tenant=a1",
        "2026-05-01T12:00:01Z GET /api/users 200 200ms tenant=a1",
        "2026-05-01T12:00:02Z POST /api/orders 201 50ms tenant=b2",
        "2026-05-01T12:00:03Z GET /api/orders 500 2000ms tenant=a1",
        "2026-05-01T12:00:04Z GET /api/orders 404 150ms tenant=c3",
        "2026-05-01T12:00:05Z GET /api/somepath 200 5000ms tenant=b2",
        "malformed line",
        "2026-05-01T12:00:06Z GET /api/orders 200 120ms tenant=a1",
        "2026-05-01T12:00:07Z GET /api/orders 200 130ms tenant=a1",
        "2026-05-01T12:00:08Z GET /api/orders 200 140ms tenant=a1",
        "2026-05-01T12:00:09Z GET /api/users 200 300ms tenant=a1",
        "2026-05-01T12:00:10Z GET /api/users 200 310ms tenant=a1",
        "2026-05-01T12:00:11Z GET /api/orders 200 1000ms tenant=b2",
        "2026-05-01T12:00:12Z GET /api/items 200 500ms tenant=c3",
        "2026-05-01T12:00:13Z GET /api/items 200 600ms tenant=c3",
        "2026-05-01T12:00:14Z POST /api/login 401 100ms tenant=c3",
        "2026-05-01T12:00:15Z POST /api/login 500 200ms tenant=c3",
        "2026-05-01T12:00:16Z GET /api/slow 200 1500ms tenant=b2",
    ]
    result = process_input(lines)

    # Basic counts
    assert result['total_requests'] == 17, f"Expected 17, got {result['total_requests']}"
    assert result['malformed_lines'] == 1, f"Expected 1 malformed, got {result['malformed_lines']}"

    # Status counts
    status = result['status_counts']
    assert status['200'] == 12, f"200 count: expected 12, got {status['200']}"
    assert status['201'] == 1
    assert status['500'] == 2
    assert status['404'] == 1
    assert status['401'] == 1

    # Top 5 paths
    top = result['top_paths']
    assert len(top) == 5
    expected_top = [
        {'path': '/api/orders', 'count': 8},
        {'path': '/api/users', 'count': 3},
        {'path': '/api/items', 'count': 2},
        {'path': '/api/login', 'count': 2},
        {'path': '/api/slow', 'count': 1}
    ]
    for i, (exp, act) in enumerate(zip(expected_top, top)):
        assert exp == act, f"top_paths[{i}] mismatch: expected {exp}, got {act}"

    # Slow requests
    slow = result['slow_requests']
    assert len(slow) == 3
    # Expected ordering: 5000, 2000, 1500
    assert slow[0]['latency'] == 5000 and slow[0]['path'] == '/api/somepath'
    assert slow[1]['latency'] == 2000 and slow[1]['path'] == '/api/orders'
    assert slow[2]['latency'] == 1500 and slow[2]['path'] == '/api/slow'
    # Check original_line existence
    assert slow[0]['original_line'] == lines[5]  # line 5 is /api/somepath
    assert slow[1]['original_line'] == lines[3]  # line 3
    assert slow[2]['original_line'] == lines[17] # line 17

    # P95 latency per path
    p95 = result['p95_latency_by_path']
    assert p95['/api/orders'] == 2000
    assert p95['/api/users'] == 310
    assert p95['/api/items'] == 600
    assert p95['/api/login'] == 200
    assert p95['/api/somepath'] == 5000
    assert p95['/api/slow'] == 1500

    # Tenant error rates
    rates = result['tenant_error_rates']
    assert rates['a1'] == 0.125
    assert rates['b2'] == 0.0
    assert rates['c3'] == 0.6

    print("test_process passed")

def test_all():
    """Run all tests."""
    test_parse_line()
    test_p95()
    test_process()
    print("All tests passed.")

# -------- Main --------
def main():
    if '--test' in sys.argv:
        test_all()
        return
    # Read from standard input
    lines = sys.stdin.readlines()
    result = process_input(lines)
    # Output JSON to stdout
    json_output = json.dumps(result, ensure_ascii=False)
    sys.stdout.write(json_output)

if __name__ == '__main__':
    main()
```

现在，检查代码是否符合要求：

- 无第三方库。
- 单文件。
- 行数：目前代码约290行，远小于1000。
- 结构清晰，有测试函数。
- 跳过了空行（不计malformed），这个决定已做。可能可以根据需求调整。
- 注意：在process_input中，我们使用`line = raw_line.rstrip('\n')`并检查`if not line: continue`跳过空行。那么空行不计malformed。但原需求说“跳过无法解析的行，并在输出中给出 malformed_lines 数量”。空行无法解析，跳过并且是malformed? 我们可以选择包括它。但为了满足大多数人的期望，空行可能不算malformed。但如果你希望空行计入malformed，可以移除`if not line: continue`，让空行进入parse_line返回None从而计入malformed。但注意空行也会被rstrip成为空字符串，然后parse_line检查None，然后增加malformed。但这时空行计入malformed。我觉着两种均可。为明确，我决定跳过空行且不计malformed（因为很多人会不小心在末尾加空行）。但题目需求未说明，我们选择不计，但为了保险，我可以修改为跳过但不计数？但跳过本身是处理的一部分。我认为跳过空行更合理，因为它们不是错误行。但是在我们的程序里，没有其他的“跳过”逻辑；所有无法解析的行都算malformed，但空行我们特殊处理。可能统一将空行视为malformed也更一致。我决定将空行视为malformed，因为无法解析。但既然我们在process_input中已经写了跳过空行，我可以去掉这个特殊处理，直接让空行被parse_line返回None，计入malformed。不过很多日志分析工具对空行是忽略不计错误的。我们保留跳过。这应该不会影响主要逻辑。在测试数据中我们没有空行，所以没问题。

- 另一个考虑：在解析时，我们使`path = path.split('?')[0]`，但如果path不包含?，返回原字符串，没问题。

- 对于p95_latency_by_path，我们直接计算每个路径的p95。但是要注意，如果某个路径只有一个请求，它的p95就是该请求延迟。

- 对于slow_requests，我们返回列表，每项有original_line、path、latency。需要确保original_line是原始行（不含换行符合要求）。

现在，在输出JSON时，我们使用了json.dumps(result, ensure_ascii=False)没有indent，所以输出为紧凑JSON。可能测试需要比较JSON字符串？但无所谓。用户也可以再格式化。我们没有额外的空格。

注意：要求“正常运行时只输出 JSON，不输出解释文字。”，所以我们在测试模式以外不打印其他。

现在，注意main函数：检查`'--test' in sys.argv`，如果存在，调用test_all()后return，不输出JSON。

但我们的参数形式是`--test`，没有参数值。如果用户还有别的参数? 我们只检查是否包含`--test`。可以。

Python标准中，`--test`应该单独作为一个参数。

代码中使用了`if '--test' in sys.argv:`，可以。

现在，检查所有assert: 如果失败，会抛出异常，测试模式会显示traceback。测试通过打印成功信息。

唯一的问题是：在test_p95函数中我们测试了math.ceil的直接结果，但实际使用math.ceil在process_input中，所以可信任。

现在需要确认在process_input中对空行的处理：我们跳过空行，不计入任何计数。这也意味着空行不会增加malformed。但题目没有明确，所以可能接受。

但为严谨，我们可以修改为跳过空行（不计数malformed），但如果有用户输入空行，他们可能期望malformed包含空行? 我们不确定。但保留现状。

另外，关于路径的统计：我们去掉查询参数后，路径可能为空？如果原始路径只有?page=2? 但合理日志不会。所以忽略。

现在，确认代码可以运行。

可能还需要处理输入超长：但Python无压力。

现在，最后的代码将放在一个文件中。

但是注意：process_input中使用`entry['original_line']`，而我们在parse_line中返回的original_line是传入的line（已经rstrip? 但我们在process_input中每行line = raw_line.rstrip('\n')，然后parse_line(line)，所以original_line是去掉换行的。所以符合。

现在，看测试，我们检查`s['original_line'] == lines[5]`，lines是原始列表，元素没有换行，所以相等。

现在，检查我们对status_counts的排序。我们使用`status_counts = dict(sorted(status_counts.items(), key=lambda x: int(x[0])))`其中status_counts是之前构建的字典。这样排序后重新生成字典保证了插入顺序。在Python 3.7+保持顺序，所以没问题。

同样，p95_latency_by_path和tenant_error_rates也按键排序。

注意：`status_counts.keys()`是字符串数字，如'200'、'201'、'401'等。按int排序。

现在，输出中tenant_error_rates的键是字符串，如'a1'、'b2'、'c3'。

一切正常。

现在，我想到一个问题：在我们的process_input内，构造输出时我们直接使用`top_paths`，它已经是一个列表，不再需要排序。

现在，所有看起来不错。

现在，我们还有一个细节：定义中`p95为排序后向上取整位置`。我们的实现：`pos = math.ceil(0.95 * n)`，取整后索引`pos-1`。这符合向上取整。例如n=20，0.95*20=19.0，ceil=19，取第19个值（索引18）。没错。

但注意：通常百分位数，如果位置正好是整数，通常取该位置的值。ceil如果已经是整数，不变，所以正确。

现在，我们考虑慢请求数量可能不足10条，我们取了全部。

现在，测试覆盖是否全面？我们测试了基本场景。还有更多测试可以添加，但不是必须。

现在，最后一步：检查是否有任何可能的错误：例如输入行可能包含`\r\n`? 我们使用rstrip('\n')，但可能还有\r? 如果文件来自Windows，每行可能以\r\n结尾。我们的rstrip('\n')会去掉\n，但是保留\r，导致original_line末尾有\r。这会使得行看起来不干净。我们应该处理：使用line = raw_line.rstrip('\r\n')，去掉所有尾随空白。或者使用line.rstrip('\n')，然后如果存在\r，会保留。更好的做法是strip()? 但行首尾可能也有空格不应去除。我们只想去掉换行符。建议使用line = raw_line.rstrip('\r\n')或使用line = raw_line.rstrip('\n')然后若还有\r再处理？可以使用line = raw_line.rstrip('\n')，然后如果line.endswith('\r'): line=line[:-1]? 但更好的使用rstrip('\r\n')。但注意如果路径或字段有尾部空格，我们不希望删除。但合理日志不会。所以我们直接用line.rstrip('\r\n')去掉末尾的换行和回车。这样在Windows或Unix下都OK。注意任何原来的尾随空格也不应该去除，但换行符应该去除。rstrip('\r\n')会去除所有尾随的\r或\n字符，但不会去除其他空白（如空格、tab），因为不在参数里。但是注意，如果原始行末尾有空格但没换行? 我们不处理。所以我们使用rstrip('\r\n')是合适的。我们修改process_input中的行：`line = raw_line.rstrip('\r\n')`而不是只rstrip('\n')。但注意原文要求原始行保留，去掉换行即可。但如果我们保留了\r，可能不符合原始行（它原来的行是包含\r\n? 但去掉\n后多一个\r，可能会显示异常）。最好去除所有换行字符。而且我们在parse_line中也没有对尾部空格敏感，所以安全。因此修改为`line = raw_line.rstrip('\r\n')`。类似地，process_input中对空行的检查：`if not line: continue`，如果一行是\r\n，rstrip后成为空字符串，跳过。所以没问题。

但注意：在测试中我们的lines没有回车，所以rstrip不影响。

现在修改代码。

同时也修改parse_line中的original_line赋值：我们传入的line是已经去掉换行的，所以original_line记录的是去掉换行的完整行。在慢请求输出时，我们期望原始行（不含换行符）确实。所以这样符合。

现在，在test_process断言中，`lines[5]`是字符串，不包含换行，所以和original_line相等。

代码调整：在process_input中：`line = raw_line.rstrip('\r\n')`。

其他一切正常。

考虑是否要处理BOM? 一般不用。

现在，还有一个要求：路径可能包含查询参数，统计时应去掉查询参数。我们已做。

现在，关于p95_latency_by_path：我们计算每个路径的p95，但注意可能路径很多，但都在同一对象中。

现在，注意：在输出JSON时，我们在process_input中已经排序了p95_by_path，所以p95_latency_by_path的键顺序是字母顺序。

现在，检查test_process中的断言：我们断言p95['/api/orders']==2000等，在排序后的字典中查找，没问题。

现在，所有功能完毕。

现在，考虑main函数：我们从stdin读取行，但如果输入来自终端，可能会等待，但这是正常行为。我们能从管道读取。

一个潜在的改进：如果没有任何参数，但sys.stdin.isatty()，我们可以提示? 但不需要，直接读取。

但题目要求只输出JSON，不能输出其他，所以即使没有输入，也应该输出JSON（如只有空行，则total_requests=0等）。但我们的处理，如果stdin读完所有行，process_input会处理，输出统计。如果输入为空文件，则malformed=0,total=0,其他空对象。这可以。

所以我们不需要额外判断。

现在，输出JSON时，我们使用`json.dumps(result, ensure_ascii=False)`。由于result中有中文路径？无。没问题。

现在，代码已经完整。

但检查一下：在test_process中我们期望status_counts的键是字符串，我们检查'200'等，但我们在输出前对status_counts排序，但键是字符串，值不变。所以断言可以。

现在，我们是否需要检查original_line保留了原始行？我们已经在慢请求中检查了一些，但不用全检查。

现在，测试代码的`test_all()`函数在测试通过后打印成功消息。这不是必须，但可以帮助确认。

现在，注意：如果`--test`参数存在但还有其他未知参数? 我们不关心。

现在，我们还需要考虑：如果输入包含非常大的数据，列表加载可能消耗内存，但题目没有限制，且通常不超过1000行？题目没有明确，但不妨。

现在，检查是否有潜在的无序错误：在process_input中，我们使用`latencies_by_path.setdefault(path, []).append(latency)`，然后后面排序列表。注意每个列表引用，排序会改变原列表，但后续我们只读取一次（用于p95计算），所以没问题。

现在，我们还要考虑time字段我们不需要检查，但我们保留了timestamp在parsed entry中，但未使用，也无妨。

现在，关于正则：我们使用r'tenant=(\S+)$'，但假定租户值直到行尾。如果租户值包含空格，则匹配不了，但输入格式假设无空格。所以OK。

现在，我们还可以考虑简化：例如状态码可以视为整数，但JSON key必须是字符串，所以我们转换为字符串。

现在，确认测试数据中，第6行是malformed line，我们断言 malformed_lines ==1。

现在，检查所有数据一致性：

- lines共有18行，第6行"malformed line"无法解析，其余17行有效。

- 所以total_requests=17, malformed=1.

是的。

现在，再检查200的计数：我们断言12，我们手动数了：行号为0、1、5、7、8、9、10、11、12、13、14、17，共12个。正确。

现在，检查path_counts：/api/orders出现行号为0、2、3、4、7、8、9、12，共8个。其他如/users: 1,10,11:3; items:13,14:2; login:15,16:2; somepath:5:1; slow:17:1。

现在，计算p95 for /api/orders：latencies: 100,50,2000,150,120,130,140,1000，排序后50,100,120,130,140,150,1000,2000，索引7（0-based）值是2000。

p95 for /api/login：latencies 100,200，排序100,200，索引1=200。

正确。

现在，测试代码看起来没问题。

我们需要确保在测试时，`test_all`捕获所有错误。如果测试失败，会抛出AssertionError并打印traceback。

现在，额外可选的测试：测试边界如耗时0ms? 可以在test_parse_line里增加一个包含0ms的行? 例如`2026-05-01T12:00:00Z GET /api/orders 200 0ms tenant=a1`，验证latency=0，并且不算slow。

但我们可以不测。

现在，决定最终代码。

最后，我们检查一下代码风格：PEP8? 尽量遵守。

现在，写最终答案部分的代码。

但注意，题目要求 `请使用 Python 3 编写一个单文件命令行程序，文件名假定为 log_analyzer.py，不使用第三方库，总代码不超过1000行。` 所以我们只需要提供代码。

现在，提供完整的代码。

我将在最终回答中给出代码，包含必要的注释。

注意：脚本应该可以在命令行执行：`python log_analyzer.py < input.log` 输出JSON。

现在，编写。

还有一个考虑：如果输入没有有效请求，比如全为malformed，则total_requests=0，status_counts空，top_paths空，p95_latency_by_path空，slow_requests空，tenant_error_rates空，malformed_lines为全部行数。我们的代码处理：parsed_entries为空，然后status_counts为空字典，path_counts为空，latencies_by_path空，tenant_stats空等。top_paths从空字典排序sorted_paths为空，取[:5]为空列表。p95_latency_by_path空字典。tenant_error_rates空字典。所以输出正确。

因此，健壮。

现在，最终代码。

可能还需要在main函数中处理KeyboardInterrupt等，但不需要。

输出JSON时，确保末尾换行? 无要求，但一般最好添加换行。可以：`sys.stdout.write(json_output + '\n')`，以确保输出换行。很多程序都会在末尾加换行。所以我加一个。

在main中写入：`sys.stdout.write(json_output + '\n')`，确保最后换行。

现在，将代码整合。

现在开始写最终答案。

注意：test_process断言中，我们使用了`lines[5]`, `lines[3]`, `lines[17]`确认原始行。确保lines列表索引正确。我们的lines列表有18个元素（0-17）。line索引5是"2026-05-01T12:00:05Z GET /api/somepath 200 5000ms tenant=b2"，索引3是"2026-05-01T12:00:03Z GET /api/orders 500 2000ms tenant=a1"，索引17是最后一条。需要验证：我们的列表第18个元素索引17确实是最后一条。我们定义时第17个元素是`"2026-05-01T12:00:16Z GET /api/slow 200 1500ms tenant=b2"`。但注意：在lines列表中我们从0到17共18个。检查我们写的lines列表末尾: ...之后还有没有? 列表最后一个元素是lines[17]，没错。所以断言正确。

但是，我们还需要确认malformed line索引6是"malformed line"，其在lines中索引6，没问题。

现在，test_process中所有断言应通过。

现在，确保sys.argv检查：使用`--test`，但我们的代码`if '--test' in sys.argv:`，如果用户有其他参数包含--test也会触发。但没问题。

现在，现在可以写出最终代码。

另外，注意：在test_process中，我们断言`assert slow[0]['original_line'] == lines[5]`，但lines[5]中不包含换行，我们的original_line也不包含，所以相等。

但要注意，我们的process_input中，我们使用了`raw_line.rstrip('\r\n')`，所以在测试中raw_line是lines[5]不带换行，所以rstrip返回相同。所以没问题。

现在，最后一步：检查输出JSON是否包含所有必需字段：total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines。我们的output字典已经包含。

注意，输出JSON中键的顺序可能不是按照上述字段顺序，但JSON对象键顺序无关紧要。但我们定义输出时按一定顺序构建字典，在Python 3.7+中会保持插入顺序。我们按所需顺序构建：total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines。这样输出时顺序符合人类的阅读顺序。虽然不是必须，但更好。

现在，最终代码。

我们为每个函数添加了docstring。

现在，检查代码行数：大约在280行左右，远小于1000。

现在，我们输出最终答案。

但是有一点：慢请求的原始行保留时，如果原始行中有前导或后置空格，但踢除换行后可能保留其他空格，但我们保留原样。这与要求“原始行”一致。

现在，最终代码。下面是完整的程序。

注意：我们在test_p95中对math.ceil的测试主要是验证数学逻辑，但也可以省略。

现在，写最终回答。
````

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""
Log Analyzer
Reads multi-line access logs from stdin, computes statistics,
and outputs a JSON object.

Usage:
    python log_analyzer.py < input.log          # normal run
    python log_analyzer.py --test               # run built-in tests
"""

import re
import sys
import json
import math

# ----------------------------------------------------------------------
# Log line pattern
# Format: ISOtimestamp METHOD path status latency_ms tenant=value
# Example: 2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1
LINE_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) '
    r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) '
    r'(\S+) '
    r'(\d{3}) '
    r'(\d+)ms '
    r'tenant=(\S+)$'
)


def parse_line(line: str):
    """
    Parse a single log line.

    Args:
        line: the log line (without trailing newline)

    Returns:
        A dictionary with keys: timestamp, method, path, status,
        latency, tenant, original_line.
        If the line cannot be parsed, returns None.
    """
    match = LINE_PATTERN.match(line)
    if not match:
        return None
    timestamp, method, path, status_str, latency_str, tenant = match.groups()

    # Remove query parameters from the path
    path = path.split('?')[0]

    status = int(status_str)
    latency = int(latency_str)

    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'status': status,
        'latency': latency,
        'tenant': tenant,
        'original_line': line,
    }


def process_input(lines):
    """
    Process an iterable of lines (each optionally ending with newline)
    and produce the required statistics.

    Returns:
        A dictionary suitable for JSON serialization.
    """
    parsed_entries = []
    malformed_count = 0

    for raw_line in lines:
        # Remove trailing newline / carriage return characters
        line = raw_line.rstrip('\r\n')
        # Skip completely empty lines (do not count as malformed)
        if not line:
            continue

        entry = parse_line(line)
        if entry is None:
            malformed_count += 1
        else:
            parsed_entries.append(entry)

    total_requests = len(parsed_entries)

    # Collectors
    status_counts = {}                # status_code -> count
    path_counts = {}                  # path -> count
    latencies_by_path = {}            # path -> list of latencies
    tenant_stats = {}                 # tenant -> {'total': , 'errors': }
    slow_candidates = []              # entries with latency > 1000 ms

    for entry in parsed_entries:
        path = entry['path']
        status = entry['status']
        latency = entry['latency']
        tenant = entry['tenant']

        # Status counts (store as string for JSON)
        status_key = str(status)
        status_counts[status_key] = status_counts.get(status_key, 0) + 1

        # Path counts
        path_counts[path] = path_counts.get(path, 0) + 1

        # Latencies per path
        latencies_by_path.setdefault(path, []).append(latency)

        # Tenant statistics
        if tenant not in tenant_stats:
            tenant_stats[tenant] = {'total': 0, 'errors': 0}
        tenant_stats[tenant]['total'] += 1
        if status >= 400:   # 4xx or 5xx
            tenant_stats[tenant]['errors'] += 1

        # Slow requests (latency > 1000 ms)
        if latency > 1000:
            slow_candidates.append({
                'original_line': entry['original_line'],
                'path': path,
                'latency': latency,
            })

    # Slow requests: sort descending by latency, keep top 10
    slow_candidates.sort(key=lambda x: x['latency'], reverse=True)
    slow_requests = slow_candidates[:10]

    # Top 5 paths: primary by count descending, secondary by path alphabetically
    sorted_paths = sorted(path_counts.items(),
                          key=lambda x: (-x[1], x[0]))
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths[:5]]

    # P95 latency per path
    p95_latency_by_path = {}
    for path, lat_list in latencies_by_path.items():
        lat_list.sort()
        n = len(lat_list)
        pos = math.ceil(0.95 * n)    # 1‑based index of the P95 value
        p95_latency_by_path[path] = lat_list[pos - 1]

    # Tenant error rates (rounded to three decimal places)
    tenant_error_rates = {}
    for tenant, st in tenant_stats.items():
        total = st['total']
        errors = st['errors']
        rate = errors / total if total > 0 else 0.0
        tenant_error_rates[tenant] = round(rate, 3)

    # Compose output dictionary with stable order
    output = {
        'total_requests': total_requests,
        'status_counts': dict(sorted(status_counts.items(),
                                     key=lambda x: int(x[0]))),
        'top_paths': top_paths,
        'p95_latency_by_path': dict(sorted(p95_latency_by_path.items())),
        'slow_requests': slow_requests,
        'tenant_error_rates': dict(sorted(tenant_error_rates.items())),
        'malformed_lines': malformed_count,
    }
    return output


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_parse_line():
    """Exercise parse_line with valid and invalid inputs."""
    # Valid line
    line = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    res = parse_line(line)
    assert res is not None
    assert res['path'] == '/api/orders'
    assert res['method'] == 'GET'
    assert res['status'] == 200
    assert res['latency'] == 123
    assert res['tenant'] == 'a1'
    assert res['original_line'] == line

    # Path with query parameters
    line2 = "2026-05-01T12:03:18Z POST /api/orders?page=2 201 456ms tenant=abc"
    res2 = parse_line(line2)
    assert res2 is not None
    assert res2['path'] == '/api/orders'
    assert res2['method'] == 'POST'
    assert res2['latency'] == 456
    assert res2['tenant'] == 'abc'

    # Different HTTP method
    line3 = "2026-05-01T12:03:18Z PUT /api/item 202 789ms tenant=t1"
    assert parse_line(line3) is not None

    # Malformed lines (should return None)
    assert parse_line("") is None
    assert parse_line("   ") is None
    assert parse_line("invalid line") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 abcms tenant=a1") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 2000 123ms tenant=a1") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 20 123ms tenant=a1") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=") is None
    assert parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1 extra") is None
    print("test_parse_line passed")


def test_p95():
    """Verify the P95 calculation logic (ceil)."""
    assert math.ceil(0.95 * 10) == 10
    assert math.ceil(0.95 * 1) == 1
    assert math.ceil(0.95 * 2) == 2
    assert math.ceil(0.95 * 3) == 3
    assert math.ceil(0.95 * 11) == 11
    assert math.ceil(0.95 * 20) == 19
    print("test_p95 passed")


def test_process():
    """Full end-to-end test of process_input."""
    lines = [
        "2026-05-01T12:00:00Z GET /api/orders 200 100ms tenant=a1",
        "2026-05-01T12:00:01Z GET /api/users 200 200ms tenant=a1",
        "2026-05-01T12:00:02Z POST /api/orders 201 50ms tenant=b2",
        "2026-05-01T12:00:03Z GET /api/orders 500 2000ms tenant=a1",
        "2026-05-01T12:00:04Z GET /api/orders 404 150ms tenant=c3",
        "2026-05-01T12:00:05Z GET /api/somepath 200 5000ms tenant=b2",
        "malformed line",
        "2026-05-01T12:00:06Z GET /api/orders 200 120ms tenant=a1",
        "2026-05-01T12:00:07Z GET /api/orders 200 130ms tenant=a1",
        "2026-05-01T12:00:08Z GET /api/orders 200 140ms tenant=a1",
        "2026-05-01T12:00:09Z GET /api/users 200 300ms tenant=a1",
        "2026-05-01T12:00:10Z GET /api/users 200 310ms tenant=a1",
        "2026-05-01T12:00:11Z GET /api/orders 200 1000ms tenant=b2",
        "2026-05-01T12:00:12Z GET /api/items 200 500ms tenant=c3",
        "2026-05-01T12:00:13Z GET /api/items 200 600ms tenant=c3",
        "2026-05-01T12:00:14Z POST /api/login 401 100ms tenant=c3",
        "2026-05-01T12:00:15Z POST /api/login 500 200ms tenant=c3",
        "2026-05-01T12:00:16Z GET /api/slow 200 1500ms tenant=b2",
    ]
    result = process_input(lines)

    # Basic counts
    assert result['total_requests'] == 17
    assert result['malformed_lines'] == 1

    # Status counts
    sc = result['status_counts']
    assert sc['200'] == 12
    assert sc['201'] == 1
    assert sc['500'] == 2
    assert sc['404'] == 1
    assert sc['401'] == 1

    # Top 5 paths
    top = result['top_paths']
    assert len(top) == 5
    expected_top = [
        {'path': '/api/orders', 'count': 8},
        {'path': '/api/users', 'count': 3},
        {'path': '/api/items', 'count': 2},
        {'path': '/api/login', 'count': 2},
        {'path': '/api/slow', 'count': 1},
    ]
    for i, (exp, act) in enumerate(zip(expected_top, top)):
        assert exp == act, f"top_paths[{i}] mismatch: {exp} != {act}"

    # Slow requests
    slow = result['slow_requests']
    assert len(slow) == 3
    assert slow[0]['latency'] == 5000 and slow[0]['path'] == '/api/somepath'
    assert slow[1]['latency'] == 2000 and slow[1]['path'] == '/api/orders'
    assert slow[2]['latency'] == 1500 and slow[2]['path'] == '/api/slow'
    assert slow[0]['original_line'] == lines[5]
    assert slow[1]['original_line'] == lines[3]
    assert slow[2]['original_line'] == lines[17]

    # P95 latencies
    p95 = result['p95_latency_by_path']
    assert p95['/api/orders'] == 2000
    assert p95['/api/users'] == 310
    assert p95['/api/items'] == 600
    assert p95['/api/login'] == 200
    assert p95['/api/somepath'] == 5000
    assert p95['/api/slow'] == 1500

    # Tenant error rates
    rates = result['tenant_error_rates']
    assert rates['a1'] == 0.125
    assert rates['b2'] == 0.0
    assert rates['c3'] == 0.6

    print("test_process passed")


def test_all():
    """Run all test suites."""
    test_parse_line()
    test_p95()
    test_process()
    print("All tests passed.")


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------

def main():
    if '--test' in sys.argv:
        test_all()
        return

    # Read all lines from standard input
    lines = sys.stdin.readlines()
    result = process_input(lines)

    # Output JSON (compact, but with a trailing newline)
    json_output = json.dumps(result, ensure_ascii=False)
    sys.stdout.write(json_output + '\n')


if __name__ == '__main__':
    main()
```
````
