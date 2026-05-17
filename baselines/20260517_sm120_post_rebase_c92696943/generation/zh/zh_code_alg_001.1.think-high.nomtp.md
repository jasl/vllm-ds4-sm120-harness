# Generation Transcript

- Case: `zh_code_alg_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 83.829582
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 338, "total_tokens": 8612, "completion_tokens": 8274, "prompt_tokens_details": null}`
- Prompt tokens: 338
- Completion tokens: 8274
- Total tokens: 8612

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
我们被要求编写一个单文件命令行程序log_analyzer.py，从标准输入读取日志，输出JSON。需要处理解析、统计，跳过无法解析的行，输出malformed_lines数量。包括多个统计项。要求包含测试函数，使用--test参数运行测试。代码不超过1000行，不使用第三方库。

需要明确：输入日志每行格式：`2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1`
字段：ISO时间（带Z，但解析时可能只检查存在），HTTP方法，路径（可能含查询参数），状态码（整数），耗时（如123ms，单位ms，可能还有?），租户（字符串，如tenant=a1）。注意：耗时总是带"ms"后缀？样例中"123ms"。题目说"耗时毫秒"，所以是整数+ms。需要提取整数部分。租户格式："tenant=..."，需要提取等号后的内容。可能有其他格式？题目说"租户"，可能固定前缀"tenant="。我们假设如此。

任务：
1. total_requests: 成功解析的行数（不包括malformed）。
2. status_counts: 字典，状态码->计数。
3. top_paths: 请求量最高前5路径，按count降序。如果并列，无所谓。路径要去掉查询参数。
4. p95_latency_by_path: 每个路径的p95耗时（毫秒整数）。p95定义：排序后向上取整位置。比如有n个样本，位置 = ceil(0.95 * n)。索引从1开始？通常p95是第ceil(0.95 * n)个值（1-indexed）。需检查定义。题目："p95定义为排序后向上取整位置。" 所以计算索引 index = ceil(0.95 * n) - 1 (0-indexed) ？如果n=1，ceil(0.95)=1，取第1个。注意是"向上取整位置"可能指排名位置（1-based）。我们采用1-based：pos = ceil(0.95 * n)，取排序后第pos个元素（1-indexed）。实现时，列表排序，索引为 int(math.ceil(0.95 * n)) - 1。
5. slow_requests: 耗时>1000ms的前10条，按耗时降序。需要保留原始行、路径、耗时。输出列表包含对象：{ "line": 原始行, "path": 去掉查询参数后的路径, "latency_ms": 整数 }。如果不足10条则全部列出。注意耗时>1000ms，不包含等于1000ms。
6. tenant_error_rates: 每个租户的错误率（4xx/5xx算错误）。保留三位小数（如0.123）。错误率 = 该租户错误请求数 / 该租户总请求数。注意处理分母为0的情况（租户没有请求？但应该有请求才出现），如果某个租户没有请求，不应该出现？但如果某租户的所有行都被解析失败，统计不到。我们只考虑成功解析的请求。租户字符串是"tenant=a1"中的"a1"部分。租户错误率输出为字典：{"tenant": 错误率小数}。要求保留三位小数，可能用round或格式化。但JSON输出时，浮点数通常保留样式。我们可以输出数字（如0.123），但保留三位小数意味着可能输出0.1234会被四舍五入为0.123? 最好用round(rate, 3)。

其他要求：
- 跳过无法解析的行，记录malformed_lines数量。
- 输出JSON对象，包含上述字段，以及malformed_lines字段。注意：题目说"输出一个 JSON 对象，包含：..." 其中包含malformed_lines？在列表中没有明确写，但开头的"跳过无法解析的行，并在输出中给出 malformed_lines 数量。"所以输出JSON要包含"malformed_lines"字段。
- 正常运行时只输出JSON，不输出解释文字。
- 当使用`--test`参数运行时执行测试。测试函数内置。测试可以模拟一些输入，验证输出是否符合预期。

代码结构：
- 定义函数 parse_line(line) 返回一个字典或None。处理各种异常。
- 定义函数 compute_stats(lines) 返回字典。
- 定义函数 main() 处理命令行参数。
- 定义测试函数 test_xxx()，在if __name__ == "__main__"中检查sys.argv是否包含--test，然后执行测试。

由于不需要第三方库，使用sys.stdin读取，使用json模块输出。

注意：路径可能含查询参数，例如`/api/orders?page=2`，需要去掉查询参数，使用split('?')[0]即可。

耗时字段：例如"123ms"，也可能是"0ms"，"1000ms"。需要提取整数。可以strip掉最后的"ms"，或者用正则匹配数字。简单: 如果字段以"ms"结尾，取[:-2]并转int。否则报错。

状态码：整数，可能是200, 404等。

租户：字段是"tenant=a1"，可能位置是第六个字段？实际上每行有6个部分：时间、方法、路径、状态码、耗时、租户。但路径可能包含空格？不可能。所以可以用split()分割，然后检查长度是否为6。但如果某部分包含空格？一般没有。注意时间ISO格式没有空格。所以简单分割。

注意：耗时前面可能没有空格？样例用空格分隔。所以split(' ')即可。

但可能存在路径包含空格？URL一般不包含空格。可以假设如此。

malformed_lines: 包括所有解析失败的行。特别是字段数不对，或者某些字段无法转为整数等。注意空行也跳过。

实现细节：
- 解析流程：按行读取，strip()去掉两边空白，跳过空行。然后按空格分割，如果len != 6，计数malformed并继续。
- 尝试解析各个部分：时间（虽然不验证具体时间，但可检查格式？可跳过验证，只作为字段），方法，路径，状态码(int)，耗时(int，去掉ms)，租户(提取等号后)。
- 耗时如果包含ms但可能不是以ms结尾？假设都以ms结尾。检查字符串最后两个字符是否为"ms"，否则视为malformed。
- 租户以"tenant="开头，否则malformed？题目明确格式，如果不是则视为malformed。提取等号后部分。
- 状态码转换为int，若失败则malformed。
- 路径：去掉查询参数（?后）。
- 统计：使用字典累积。
- p95计算：需要每个路径的所有耗时列表，然后排序，计算索引。
- slow_requests：需要记录原始行和对应的路径、耗时。只保留>1000ms，然后按耗时降序排序，取前10。
- 租户错误率：需要每个租户的总请求数和错误请求数（状态码>=400）。错误包括4xx和5xx。注意状态码为int。

输出JSON：需包含字段顺序？不需要，但可保持可读性。

性能：考虑输入可能很大，但只要求统计，用字典和列表足够。使用defaultdict(list)存储延迟列表。

测试函数：定义几个测试用例，例如一个简单日志行，空行，格式错误，多个路径等。使用assert检查。测试时可以使用模拟输入，比如在测试函数中定义字符串列表，然后调用compute_stats。可以用json.dumps输出对比。

注意：输出JSON时，不指定indent？题目没说要求格式化。为简洁，可以输出紧凑的JSON（无多余空格），但人类可读性？通常输出一整行JSON。可以设置indent=None或1？为便于阅读，可以输出格式化JSON（indent=2），但注意可能不符合“只输出JSON”要求。题目没有明确要求是否美化。建议输出紧凑JSON（无空格），因为解析程序通常期望一行。但示例输出可能是一行。为保险，输出紧凑：json.dumps(result, ensure_ascii=False, separators=(',',':') ) 或直接dumps默认。默认会带空格，但空格在JSON中允许。为了美观，可以用indent=4? 但题目说只输出JSON，不输出解释文字，所以格式无所谓。我倾向于输出带缩进的JSON，便于人类阅读，但可能不是必须。我将在示例中使用indent=2，但可以在测试中检验。不过如果使用管道，有缩进也不影响。但为了符合生产环境，可能期望紧凑输出。我会选择紧凑输出（no indent），因为“只输出JSON”通常表示一行。可加indent=None。我会做：print(json.dumps(result, ensure_ascii=False, default=str)) default处理可能出现的Decimal？不需要。注意浮点数，python的float可以序列化。

注意：tenant_error_rates的数值需要保留三位小数。使用round(x, 3)得到浮点数，但Python浮点数可能显示为0.123000000，在JSON中会显示为0.123？实际上round(0.1234,3)得0.123，json序列化显示0.123。但是0.1230会显示0.123。所以没问题。如果某个租户错误率是0，则显示0.0。也可以考虑以字符串保存？题目要求“保留三位小数”，但没说数据类型，输出数字即可。

测试：使用--test运行时执行测试，测试函数可以打印一些信息或直接assert。测试结果应该pass/fail，为简便，我们打印所有测试通过，或者抛出异常。测试可以从标准输入或预设字符串列表模拟。

需要确保代码不超过1000行。实际实现代码量很少，远小于1000。

边缘情况：p95计算对于特定路径记录数为0？如果某路径有记录，则需要计算。如果只有0条？不会出现在路径统计中，因为我们只在有请求的路径计算。

top_paths：取请求量最高的前5，如果少于5个，则全部。如果并列，可任意选。以count降序排序。

慢请求：按耗时降序，取前10，如果少于10，全部。注意包括耗时等于1000ms？题目说>1000ms，不包括等于。所以过滤条件>1000。

租户错误率：对于有请求的租户，计算错误率。可能包括所有租户？对，对每个有请求的租户计算。

malformed_lines：包括无法解析的行。注意空行跳过，但不算malformed？题目说“跳过无法解析的行”，所以无法解析的行包括字段数不对，或转换失败。空行可视为无法解析？可能是空白行，应算作无法解析？一般来说，空白行应忽略而不算malformed？但为了清晰，可以将其视为无法解析的行。但题目没有明确，我倾向于跳过空行且不计数，因为无法解析通常指格式错误。但更好的做法是：如果行只包含空格或者为空，可视为不合法，但记录为malformed。但为了简单，我选择：忽略空行（strip后为''），不计数也不统计。但题目“跳过无法解析的行”，空行可能也算无法解析，但为了逻辑清晰，可以包含。我采用：如果strip后为空，跳过且不计入malformed。因为空行不算是有效的日志行，但很多日志处理中忽略空行。为了准确，可以当做格式错误。但题目没有明确，我选择跳过空行且不算malformed，因为日志文件可能有空行分隔。然后其他无法解析的计入malformed。

实现计划：

```python
import sys
import json
import math
from collections import defaultdict

def parse_line(line):
    # 返回 (path, status_code, latency_ms, tenant) 或 None
    parts = line.strip().split()
    if len(parts) != 6:
        return None
    timestamp, method, path_raw, status_str, latency_str, tenant_str = parts
    # 解析状态码
    try:
        status_code = int(status_str)
    except ValueError:
        return None
    # 解析耗时
    if not latency_str.endswith('ms'):
        return None
    try:
        latency_ms = int(latency_str[:-2])
    except ValueError:
        return None
    # 解析租户
    if not tenant_str.startswith('tenant='):
        return None
    tenant = tenant_str[7:]  # 去掉'tenant='
    if not tenant: # 空租户？不应该，但可视为非法
        return None
    # 路径去除查询参数
    path = path_raw.split('?')[0]
    return (path, status_code, latency_ms, tenant)

def compute_stats(lines):
    total = 0
    malformed = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    slow_requests = [] # 每个元素是 (line, path, latency)
    tenant_stats = defaultdict(lambda: {'total':0, 'errors':0})
    for line in lines:
        # 跳过空行？视为malformed or ignore? 选择忽略空行
        stripped = line.strip()
        if not stripped:
            continue
        parsed = parse_line(line)
        if parsed is None:
            malformed += 1
            continue
        total += 1
        path, status_code, latency_ms, tenant = parsed
        # 状态码计数
        status_counts[status_code] += 1
        # 路径计数
        path_counts[path] += 1
        # 延迟列表
        path_latencies[path].append(latency_ms)
        # 慢请求
        if latency_ms > 1000:
            slow_requests.append((line.rstrip('\n'), path, latency_ms))
        # 租户统计
        tenant_stats[tenant]['total'] += 1
        if status_code >= 400:
            tenant_stats[tenant]['errors'] += 1
    # 计算结果
    # top_paths: 前5路径
    top_paths = sorted(path_counts.items(), key=lambda x: -x[1])[:5]
    top_paths_list = [{'path': p, 'count': c} for p, c in top_paths]
    # p95_latency_by_path
    p95_latency_by_path = {}
    for path, latencies in path_latencies.items():
        n = len(latencies)
        if n == 0:
            continue
        latencies.sort()
        # 计算p95位置(1-indexed)
        pos = math.ceil(0.95 * n)
        # 转换为0-indexed
        index = pos - 1
        # 确保索引在0到n-1内（ceil可能大于n? 当n=0时已跳过，n>0时max pos = n (当0.95*n>n? 0.95n <= n, 所以pos<=n, index<=n-1)
        p95_latency_by_path[path] = latencies[index]
    # slow_requests: 按耗时降序排序，取前10
    slow_requests.sort(key=lambda x: -x[2])
    slow_requests = slow_requests[:10]
    slow_requests_list = [{'line': line, 'path': path, 'latency_ms': lat} for line, path, lat in slow_requests]
    # tenant_error_rates
    tenant_error_rates = {}
    for tenant, stats in tenant_stats.items():
        rate = round(stats['errors'] / stats['total'], 3) if stats['total'] > 0 else 0.0
        tenant_error_rates[tenant] = rate
    # 组装结果
    result = {
        'total_requests': total,
        'status_counts': dict(status_counts),
        'top_paths': top_paths_list,
        'p95_latency_by_path': p95_latency_by_path,
        'slow_requests': slow_requests_list,
        'tenant_error_rates': tenant_error_rates,
        'malformed_lines': malformed
    }
    return result

def main():
    if '--test' in sys.argv:
        run_tests()
        return
    lines = sys.stdin.readlines()
    result = compute_stats(lines)
    print(json.dumps(result, indent=2, ensure_ascii=False))

# 测试函数
def run_tests():
    # 测试parse_line
    line1 = "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1"
    parsed = parse_line(line1)
    assert parsed == ('/api/orders', 200, 123, 'a1'), f"parse_line failed: {parsed}"
    # 包含查询参数
    line2 = "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2"
    parsed = parse_line(line2)
    assert parsed == ('/api/orders', 201, 456, 'b2'), f"parse_line failed: {parsed}"
    # 格式错误：字段不足
    parsed = parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms")
    assert parsed is None, "Should be None"
    # 耗时格式错误
    parsed = parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123 abc")
    assert parsed is None
    # 状态码非数字
    parsed = parse_line("2026-05-01T12:03:18Z GET /api/orders abc 123ms tenant=a1")
    assert parsed is None
    # 租户格式错误
    parsed = parse_line("2026-05-01T12:03:18Z GET /api/orders 200 123ms user=a1")
    assert parsed is None
    # 测试compute_stats
    sample_lines = [
        "2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n",
        "2026-05-01T12:03:19Z POST /api/orders?page=2 201 456ms tenant=b2\n",
        "2026-05-01T12:03:20Z GET /api/users 500 2000ms tenant=a1\n",
        "bad line\n",
        "2026-05-01T12:03:21Z GET /api/orders 404 50ms tenant=a1\n",
        "2026-05-01T12:03:22Z GET /api/orders 200 150ms tenant=b2\n",
        # 添加更多测试慢请求
        "2026-05-01T12:03:23Z GET /api/orders 200 1001ms tenant=a
````

## Assistant

````markdown
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
````
