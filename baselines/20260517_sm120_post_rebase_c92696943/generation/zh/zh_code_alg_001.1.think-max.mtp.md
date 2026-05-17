# Generation Transcript

- Case: `zh_code_alg_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 210.275424
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 417, "total_tokens": 35885, "completion_tokens": 35468, "prompt_tokens_details": null}`
- Prompt tokens: 417
- Completion tokens: 35468
- Total tokens: 35885

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
我们被要求写一个单文件命令行程序 `log_analyzer.py`，处理输入日志，输出 JSON 统计。需要处理各种字段，跳过无法解析的行，并计算各种指标。包含内置测试，当 `--test` 参数运行时执行测试，否则从 stdin 读取数据并输出 JSON。

我们需要详细设计。

首先，解析每一行。格式：`2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1`。字段：ISO时间、HTTP方法、路径、状态码、耗时毫秒（带ms后缀），租户。注意：路径可能包含查询参数，统计时去掉查询参数（即只取路径部分，包括问号之前）。耗时单位是毫秒，但可能有其他单位？看起来固定是"ms"后缀。但可能没有ms？我们按指定格式解析：最后一个字段是租户，格式为`tenant=xxx`。但租户可能含有等号？看起来是简单的键值。但为了健壮，我们可以按空格分割，然后前5个是固定字段，第6个是租户字段（可能包含等号）。注意：路径可能包含空格？一般不会，但查询参数中有等号，但路径整体不包含空格。我们假设每行由空格分割，字段数至少是6。第一个是ISO时间，第二个是HTTP方法，第三个是路径（可能包含查询参数），第四个是状态码（整数），第五个是耗时（例如123ms），第六个是租户（tenant=...）。注意：如果路径包含空格？不太可能，所以我们可以安全地用split()分割。

解析步骤：
- 去除行首尾空白，如果为空跳过。
- 分成至少6个部分。如果少于6，跳过。
- 提取前五个：timestamp, method, path, status_code_str, duration_str, tenant_keyvalue。
- 检查 duration_str 是否以 "ms" 结尾，如果是，去掉"ms"转为整数。否则跳过（malformed）。
- status_code_str 转为整数，如果失败跳过。
- path 去掉查询参数：用 ? 分割，取第一部分（路径）。如果路径包含 #，也去掉？但一般没有。只去掉 ? 之后的查询参数。
- tenant 部分：从 "tenant=..." 提取值。如果格式不符，跳过？但文档说格式是 tenant=...，所以如果不符合可能也是 malformed，但为了健壮，我们允许提取第一个等号后的内容作为租户ID。或者如果格式不符，整个行跳过？我们假设是合法的，但如果tenant没有等号，我们可以认为malformed？按照要求，跳过无法解析的行，所以若不能提取出租户，则跳过。但可能日志格式固定，所以可以宽松处理，但测试要严格。

其他：ISO时间我们不需要具体解析，但可以验证格式？可跳过。

定义 malformed_lines 计数。

然后统计各项：

1. total_requests：成功解析的行数。
2. status_counts：使用字典计数 status code。
3. top_paths：前5个请求量最高的路径（去参后的路径），按计数降序，同计数任意顺序，取前5。如果路径少于5，则返回所有。
4. p95_latency_by_path：每个路径的 p95 耗时。注意：p95 定义：排序后向上取整位置。例如，路径A有100个请求，排序后，第95百分位的位置？通常是0.95 * N，然后取ceil（向上取整）之后的索引。但"向上取整位置"可能指索引从1开始？我们需要明确。
   - "p95定义为排序后向上取整位置。" 一般计算 p95 是对耗时列表排序后，计算 index = ceil(0.95 * N)，然后取该位置的耗时（1-indexed）。但有时 index = ceil(0.95 * N) - 1 ？需要确认。通常样本第95百分位数是排序后第ceil(0.95*N)个值，如果索引从1开始。但如果从0开始，则 index = ceil(0.95 * N) - 1。为明确，依据常见定义：对于N个元素排序，第p百分位数是位于排序后的第 ceil(p * N / 100) 个位置（1-indexed）的值。所以对于p=95，位置是 ceil(0.95 * N)。假设N=10，0.95*10=9.5，ceil=10，所以取第10个（最大）。如果N=100，0.95*100=95，取第95个。我们认为这是合理的。
   - 注意：如果该路径下没有请求，不应该出现，但只有请求过的路径才有统计。
   - 返回 p95_latency_by_path 字典，键为路径，值为整数毫秒。
5. slow_requests：耗时大于1000ms的前10条，按耗时降序，保留原始行、路径、耗时。需要对于每个慢请求，我们保留原始行（整行字符串），路径（去参后路径），和耗时（整数毫秒）。输出列表，每个元素包含 `original_line`, `path`, `duration`。注意排序：耗时降序，如果耗时相同，顺序任意？可以按出现顺序？一般按降序即可。取前10条。
6. tenant_error_rates：每个租户的错误率。错误定义：状态码是4xx或5xx。错误率 = (该租户错误请求数) / (该租户总请求数)。注意：分母是该租户总请求数，包括所有状态码。如果租户总请求数为0，不应该出现，但避免除以0。错误率保留三位小数（四舍五入？用round? 保留三位小数，应该是格式化输出，如 0.xxx。可以用round(rate, 3) 但注意 float 精度。或者直接用 f"{rate:.3f}" 后转float？JSON中应为数字。可以使用 round(rate, 3) 但可能显示0.1235变成0.124？我们需要保留三位小数，即精度0.001。使用 round 可能会产生浮点问题，但一般可以。也可用 Decimal，但禁止外部库，自己用得小心。可以使用 round(rate, 3) 然后 float 输出，保证三位小数。不过需要确保错误率是有限小数，例如 1/3 得到 0.333333333，round 后 0.333。

其他要求：
- 跳过无法解析的行，并给出 malformed_lines 数量。在 JSON 中包含此字段。
- 正常运行时只输出 JSON，不输出解释文字。
- 当 `--test` 参数运行时，执行测试（内置测试函数），测试可以打印一些结果，不输出 JSON。
- 代码结构清晰，总代码不超过1000行。

我们需要编写程序，包括测试部分。测试可以使用 assert 或打印等，通常输出一些信息。

设计：

定义函数 parse_line(line): 返回一个字典或 None 如果跳过。
返回包含 fields: timestamp, method, raw_path, path (without query), status_code, duration (int), tenant。

主函数：从 sys.stdin 读取行，调用 parse_line，收集数据。

存储数据结构：
- 所有解析后的记录列表（用于 slow_requests 和 path 耗时列表）。但如果我们只需要列出前10慢的，可以维护一个大小为10的堆（最大堆），或者收集所有记录并排序，但记录数可能很大，所以建议有选择地保留。但要求慢请求前10，我们可以使用堆：当 duration > 1000 时，推入堆，只保留前10。但需要降序排序，可以用最小堆：保持大小为10的最小堆（按duration），当新记录大于堆中最小的，则替换。最后倒序得到前10。或者收集所有记录但可能太多，假设日志不太大，可以全部收集。不过题目为单文件脚本，可能规模不大，但最好考虑效率。我们选择使用堆的方法。
- 对于路径耗时列表：需要每个路径下的所有耗时，用于计算 p95。每个路径需要保留所有耗时吗？可能很多。但 p95 需要全部排序，所以只能收集所有耗时。假设日志不是特别大，可以存储所有耗时。但如果有百万条，可能内存紧张。题目没有特别要求性能，但稳妥起见可以全部存储。
- 租户错误计数：用字典统计每个租户的总请求数和错误数。

因此，我们维护：
- total_requests = 0
- malformed_lines = 0
- status_counts = defaultdict(int)
- path_counts = defaultdict(int)  # 路径计数
- path_latencies = defaultdict(list)  # 每个路径的耗时列表
- slow_requests_heap = []  # 元素为 (duration, -index?, line, path) 使用最小堆，大小为10
- tenant_total = defaultdict(int)   # 租户总请求
- tenant_errors = defaultdict(int)  # 租户错误请求

注意：slow_requests 需要保留原始行和路径。堆中元素：(duration, line, path) 但堆排序按 duration，如果 duration 相同，比较后面元素会出错，所以需要唯一性。可以加一个自增序列号确保稳定。实际上，我们可以使用 heapq 且元素为元组，按 duration 升序，但需要取前10降序，所以我们可以存储 (duration, index, line, path) 其中 index 为负的计数器或使用优先级。我们采用：使用最大堆的方式，但 Python 只有最小堆。我们可以将 duration 取负来实现最大堆。但我们需要前10最大，可以维护一个大小为10的最小堆，存放（duration, line, path），当新元素 duration 大于堆中最小的 duration，则 pop 再 push。但这样最终堆中是最小的10个最大的？不对，最小堆中存放的是当前最大的10个元素中的最小值（即第10大的）。正确做法：用一个最大堆取前10最大。但为了节省空间，用最小堆：每次 push 元素，如果堆大小超过10，则 pop 最小的，这样堆中始终是当前最大的10个。但由于是最小堆，最终堆顶是这10个中最小的，我们要得到前10降序，需要对堆排序（按 duration 降序）。所以我们可以直接使用 heapq，元素为 (duration, line, path) 作为最小堆，不断 push，当堆大小>10时pop最小的。最后堆中有10个最大的。然后转换为列表，按 duration 降序。

但是注意：我们需要保留原始行和路径，而堆比较时如果 duration 相同，会比较第二个元素 line（字符串），可能导致堆比较错误，因为字符串也可以比较，但可能会导致不必要的比较。不过只要比较稳定，应该没问题。但可能存在特殊情况：如果 duration 相同，line 可能很长，但不碍事。为了确保，我们可以加入一个递增计数器防止任何比较问题：元素为 (duration, counter, line, path)。但 counter 确保唯一，但 heap 只是对第一个元素排序，如果 duration 相同则比较 counter，这没问题。

简化：直接用 (duration, line, path) 作为元组，可以比较。只要 line 可比较且唯一性？不是必须唯一，但比较不会出错，只是如果 duration 相同，会按 line 排序，但这不是问题，最终排序正确（尽管顺序可能不确定）。但为了符合排序（如果耗时相同可以任意顺序），所以没问题。

我们决定使用 (duration, line, path) 直接。

处理步骤：
1. 解析行，若失败 malformed_lines++，跳过。
2. 成功：total_requests++，status_counts[status]++，path_counts[path]++，path_latencies[path].append(duration)，tenant_total[tenant]++，如果状态码为4xx or 5xx：tenant_errors[tenant]++。
3. 对于 slow_requests：if duration > 1000: 使用 heappushpop 或 push 然后检查大小。因为我们要维护前10，可以使用 heappush 然后如果堆大小>10则 heappop。但通常采用：先 push，如果 len > 10 则 heappop。
   - 或者我们可以先判断新 duration 是否大于堆中最小的（如果堆满），如果大于就 pop 再 push。这样可以减少 push/pop 次数。但为简单，直接 push 然后检查 size > 10 就 pop 最小。这样始终保留最大的10个。因为 pop 是最小的，所以堆中是最大的10个。
   - 注意：最初堆为空，累积到10个后，每次 push 再 pop 会留下最大的10个。

计算 p95_latency_by_path:
对于每个 path 的 latencies 列表，排序，然后计算 index = ceil(0.95 * len(latencies))，从1开始，然后取 sorted_latencies[index-1]。注意：如果列表长度为0，忽略（不会发生，因为 path 只在有请求时才存在）。对于 p95，如果某个路径总请求数很少，如1，则 p95 是该耗时；如果请求数为2，0.95*2=1.9，ceil=2，取第二个（最大）。这个符合 p95 定义。

注意：ceil 可以用 math.ceil，但我们需要向上取整位置。导入 math 是可以的，没有第三方库。math.ceil 是向上取整。或者我们可以使用整数运算： (95 * n + 99) // 100 ？但精度问题。用 math.ceil 更清晰。

计算 tenant_error_rates: 对于每个租户，error_rate = tenant_errors[tenant] / tenant_total[tenant]。保留三位小数：用 round(rate, 3)。注意：如果分母为0，错误率定义为0？但不会出现，因为我们都有一个请求才出现租户。为安全，分母不为0。

输出 JSON：使用 json.dumps 输出，indent 可选？要求输出 JSON 对象，没说要缩进。通常输出紧凑即可。但为了可读性可以带缩进。但常规输出尽量紧凑。我们使用 json.dumps(obj, ensure_ascii=False, indent=2) 或默认。可以考虑用 default=str？但我们的数据都是基础类型。使用 json 模块。

注意：需要输出包含所有要求字段。JSON 对象键必须匹配。对于 top_paths 是一个列表，每个元素包含 path 和 count。对于 p95_latency_by_path 是对象（字典）键为路径，值为整数。对于 slow_requests，是列表，每个元素包含 original_line, path, duration（整数）。对于 tenant_error_rates，是对象，键为租户，值为三位小数数字（浮点数）。注意：保留三位小数，即使 0 也要输出 0.000？JSON 输出 0.0 或 0.000？要求保留三位小数，所以可能期望数字 0.000。用 round(rate, 3) 会得到 0.0 显示为 0.0，不是 0.000。但 JSON 标准中数字没有固定小数位数。所以可能需要表示成浮点数，然后输出时保留三位？可以用 float 然后 json 输出，但 Python 的 json.dumps 默认会对 float 输出如 0.0，不一定带三位。为了确保三位小数，我们可以将数字转换为字符串格式 "%.3f" % rate 再转 float，但不行。我们可以自定义编码方式？但更简单：使用 round(rate, 3) 后，如果 rate=0.0，输出 0.0，但题目要求保留三位小数，可能意思是让数字为 0.000 但 JSON 中 0.0 和 0.000 在语义上等价。但为了严格符合，我们可以输出为浮点数，但 Python 显示可能为 0.0，可以接受？或许期望输出为数字。但要求保留三位小数，通常是在文本显示时保留三位。我们可以输出字符串？不，应该是数字。所以 round 应该足够。但例如 0.3333 会变成 0.333，但 json.dumps 可能会输出 0.333，是三位小数。对于 0.0 会输出 0.0，是1位小数。但要求保留三位，也许应该永远显示三位小数。但 JSON 本身不控制小数位数，所以我们可以直接输出 round 后的 float 即可，测试时可能比较数字值。

如果要强制三位小数可考虑使用浮点数？但显示问题不重要，不过最好用 round 确保精度。也可以使用 decimal.Decimal 并规范化小数位数，但 Decimal 是内置模块，可以使用。但为了简便，用 round 然后 float。

或者我们可以自定义 JSON 编码器：将 float 格式化为三位小数。但不用太复杂。

考虑常见做法：保留三位小数就是四舍五入到千分位，然后作为浮点数输出。用 round(rate, 3) 即可。

但注意：round(rate, 3) 在 Python 中可能由于浮点误差产生 0.3330000000000001 之类的？实际上 round 返回的 float 是近似值，但输出时 json.dumps 会以尽量精确到足够位数来表示该浮点，但可能显示很多位。我们可以使用格式化化成字符串再转换？为了保险，可以自己实现保留三位小数：使用 Decimal 或使用 int(rate * 1000 + 0.5) / 1000.0 但同样有浮点问题。或者用 `f"{rate:.3f}"` 转换成字符串，但 JSON 中是数字，不是字符串。所以可以用 float(f"{rate:.3f}") 但会有浮点误差。其实可以用 `round(rate, 3)` 是最直接的。

我们采用 round(rate, 3) 并依赖 json.dumps 输出。对于 0.0 输出 0.0，但测试可能期望 0.0？或许期望 0.000？不过题目要求保留三位小数，很可能只是值保留三位有效，不是显示格式。所以 0.0 可能不符合，但可以接受？如果担心，可以使用自定义 float 类，但不必要。我认为 round 就够了。

测试要求：内置测试函数，当 `--test` 参数时执行测试。测试应覆盖各种情况。

设计测试用例：
- 正常完整测试：提供示例日志，计算期望值。
- 包含无法解析的行。
- 包含空行。
- 包含多个租户，不同错误率。
- 包含慢请求。
- 检查 p95 计算是否正确。
- 查询参数去除。

测试函数：可以使用硬编码的日志列表作为输入，模拟 sys.stdin？或者直接调用 parse_line 然后断言。我们可以定义一个 test() 函数，使用一些样例，打印结果并断言。

另外，主程序需要处理命令行参数：如果 sys.argv 包含 "--test"，则调用 test() 退出，否则从 stdin 读取。此外，也要处理如果文件作为模块导入时不执行？需要 `if __name__ == '__main__'` 判断。

代码结构：
- 导入 sys, json, math, heapq, collections.defaultdict。
- 定义 parse_line(line) 返回 dict 或 None。
- 定义 compute_stats(lines): 输入行列表（或者迭代器），返回统计字典。
- 定义 test() 函数执行测试。
- 主程序。

注意：慢请求我们需要保留原始行，即未经修改的输入行。在解析后，我们保留原始行用于输出。

慢请求堆：元素 (duration, line, path) 或 (duration, counter, line, path)。我们使用计数器？

因为我们需要堆大小固定10，并且最终输出前10降序。所以使用最小堆：每次插入后若长度>10则弹出最小的（即最小 duration 的），这样剩余的是最大的10个。但弹出后，最终堆中是最小的位于堆顶的最大10个？对，堆里是最小堆，堆顶是最小的，但所有元素都是最大的10个中的元素。下次新元素如果比堆顶大，则替换。最终堆中存放的是最大的10个，但顺序不是降序。我们需要将堆排序得到降序列表。

但注意，如果 duration 相同，堆的比较将使用 line，这可能导致堆的形状受影响，但最终结果列表按 duration 降序，如果 duration 相同，则顺序任意。可以接受。

但如果 encounters 可能很多，每次 push 然后检查 size，如果 size>10 则 heappop。这样效率较高。

或者直接全部收集所有慢请求行，最后排序取前10。如果日志数量不大且慢请求不多，也可以。但为通用，使用堆。

存储每个路径的耗时列表：path_latencies[path] = [] 并 append。

现在考虑输出 top_paths：需要请求量最高的前5个路径。可以使用 path_counts 字典，按 count 降序排序，取前5。如果多个路径相同 count，顺序任意。我们可以用 sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5] 然后转为列表 [{"path": path, "count": count}, ...]。

p95_latency_by_path: 对于每个 path 计算 p95，存储在字典中。如果某个路径请求数极少，也计算。

注意：p95 定义为向上取整位置，对于请求数为0（不会出现）忽略。对于请求数 n，index = math.ceil(0.95 * n) - 1（若从0开始）。或者 index = math.ceil(0.95 * n) 然后取 sorted[index-1]。我们使用后者。

计算 p95 时，如果 n 很小，比如1，0.95*1=0.95，ceil=1，取第1个（即唯一元素）。对于2，0.95*2=1.9，ceil=2，取第2个（最大）。对于3，0.95*3=2.85，ceil=3，取第3个。所以 p95 倾向取较大值。这是合理的。

注意：如果 path 的请求数较多，排序可能会消耗时间。但必须。

等待，还有错误率：计算每个租户的错误请求除以总请求。

现在测试。测试包括类似提供的样例，需要构造输入和期望输出。

我们还需要处理参数 `--test`，然后执行测试。

注意，输出 JSON 时，需要确保字段顺序符合要求？JSON 对象是无序的，但可读性，通常按顺序输出。可以使用 collections.OrderedDict 或确保键的顺序。但要求中字段顺序：total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines。malformed_lines 也需要输出。所以 JSON 应该有7个键。为保持顺序，可以使用列表 of tuples? 或者直接 dict，Python 3.7+ 字典保持插入顺序，所以按顺序插入即可。在输出时 json.dumps 会按插入顺序输出（python 3.7+ 特性）。如果考虑兼容性，可以用 OrderedDict。但要求 Python3，一般用 3.7+，所以 dict 保证顺序。我们使用普通 dict，按顺序设置键。

slow_requests 需要包含 original_line, path, duration，每个元素为 dict。

tenant_error_rates 键为租户，值为 float。

输出示例（人为构造）：
{
  "total_requests": 7,
  "status_counts": {"200": 5, "404": 2},
  "top_paths": [{"path": "/api/orders", "count": 4}, {"path": "/api/users", "count": 2}, ...],
  "p95_latency_by_path": {"/api/orders": 200, "/api/users": 150},
  "slow_requests": [{"original_line": "...", "path": "...", "duration": 2000}, ...],
  "tenant_error_rates": {"a1": 0.333, "b2": 0.0},
  "malformed_lines": 0
}

注意：status_counts 键应该是字符串还是数字？文档说返回按状态码统计。状态码是整数，但输出时作为键，JSON 接受字符串作为键，所以应该转换为字符串。因为 JSON 对象键必须是字符串。所以 status_counts 应为 {"200": 5, "404": 2}（字符串）。同样，p95_latency_by_path 和 tenant_error_rates 的键是路径和租户，都是字符串。

所以 status_counts 中键用 str(status)。

在 top_paths 中的 path 是字符串。

输出中 malformed_lines 我们放在最后，或与其他一起。

慢请求：保留原始行 entire line as string. 路径是去参后路径。

计算慢请求时，只用 heap 收集 duration>1000 的，最后转换为列表。

注意：如果慢请求多于10，取前10。我们的堆保证前10最大。但如果少于10，就全部。

关于堆的实现细节：
- 初始化为空列表。
- 对于每个 duration>1000 的记录，直接 heappush(heap, (duration, line, path))。
- 如果 len(heap) > 10: heappop(heap)
- 最后 heap 中最多10个元素，是最小的位于堆顶的最大10个记录。然后需要按 duration 降序排序：sorted(heap, key=lambda x: x[0], reverse=True) 取出列表。或者可以使用 nlargest 但需要导入 heapq 中的 nlargest? nlargest(10, iterable) 也可以。我们用 nlargest 但需要指定 key。但使用堆我们已经有了，直接排序 heap 倒序。

但 nlargest 更直接：我们可以不自己维护堆，而是将所有慢请求记录收集到列表，最后用 heapq.nlargest(10, list, key=lambda x: x[0])。但收集所有会占用内存，但简单。但堆方法更优。但为了代码简洁，可以收集所有慢请求记录（如果很多慢请求可能内存不大）。题目没有数据规模，但建议用堆。但我们用堆。

注意：如果使用 heappush 然后 pop，堆中元素是比较 duration 的，但还有 line, path。当 duration 相等时，可能因为 line 的比较问题导致堆的性质改变？但不会错，只是顺序不确定。在最终排序中，我们按 duration 降序，对于相同 duration，顺序可以是任意的。所以可以接受。

但为了稳定性，我们可以增加一个自动递增索引作为第二比较键，避免字符串比较。例如 (duration, idx, line, path)。使用 itertools.count()。

现在开始编写代码。

parse_line(line) 功能：
- strip()
- 如果为空，返回 None (malformed? 空行算无法解析吗？题目说“跳过无法解析的行”，空行可以跳过且不计入 malformed_lines？或者计入？题目：跳过无法解析的行，并在输出中给出 malformed_lines 数量。这里的“无法解析”应该是格式不符合预期的行。空行也属于无法解析的一种。如果严格，所有不符合解析规则的行都应计入 malformed_lines。但空行也可被认为无效。我们最好将空行也计入 malformed_lines。但通常空行可能被忽略，但为了准确，应该计入。没有什么理由忽略空行。所以空行增加 malformed_lines。我们可以处理：如果 strip() 后为空，则 malformed_lines++ 并返回 None。
- 按空格 split()，如果长度 != 6，则可能格式不对。但注意：路径可能包含空格？假设没有。所以要求正好6列。但是时间字段可能包含 T 但无空格。所以6列。有时可能行末尾有空格？strip() 后 split() 会忽略空字符串。所以长度6是标准。少于或多于6，视为 malformed。但是路径可能包含查询参数的等号，和租户的等号，split 后不会分割等号，所以字段数正确。如果有多个空格，split 默认会合并，还是期望6字段。假设日志格式固定为每一字段由单个空格分隔。如果有多余空格，也可能分割错误。但我们可以按空白分割然后检查字段数至少6，也许路径本身包含空格？不太可能。但为了健壮，假设正好6字段。
- 验证 status_code 是否为纯数字，转换为 int，否则 malformed。
- 验证 duration 是否结尾为 ms，否则 malformed。提取数字部分转为 int，如果转换失败 malformed。
- 提取 tenant：第6个字段（索引5）必须包含 '=' 并且前缀是 'tenant'？格式 "tenant=xxx"。可能还有其他？根据要求应该是 tenant=...。但也可以允许任何形如 key=value? 但题目明确是 tenant=a1。所以如果字段不包含 '=' 或者键不是 'tenant'，视为 malformed。但为了宽松，我们假设如果包含 '=' 就提取等号后面的部分作为租户id？但这样可能不够严格。按照规范：格式为 tenant=a1，所以等号前必须是 tenant。但是也有可能其他形式？测试时可能包含不符合规则的。所以如果第6个字段以 'tenant=' 开头，提取后面部分。否则视为 malformed。
- 其他字段：timestamp, method, raw_path 不需要验证格式。但是 method 可能是 GET、POST等，可以接受任意。path 假设为字符串。
- 最后，path 去除查询参数：用 '?' 分割，取第一部分。如果包含 '#' 也可除去，但一般没有。用 split('?')[0] 得到路径。

返回一个字典。

注意事项：如果 path 本来就是纯路径（无参数），split('?')[0] 为自身。

现在统计函数 compute_stats(lines):
- 接受行列表或迭代器。
- 初始化各种字典，堆。
- 处理每一行：调用 parse_line。
- 若返回 None，malformed_lines++。
- 否则累加。
- 最后计算各种指标。

输出：构建结果字典。

关于测试：使用一些样例，验证输出是否符合预期。

测试函数 test() 应该打印一些信息？一般不输出 JSON，而是测试结果。可以打印通过断言或直接 print 详细信息，然后 exit。

测试应考虑边界：
- 空行
- 格式不完整行
- 正常行，验证每个统计

我们可以构造几个日志样例并调用 compute_stats，比较结果。因为 compute_stats 返回值是字典，我们可以用 assert 比较键值。

但需注意浮点比较：错误率可以用 round 比较。

考虑编写一个辅助函数来比较两个结果字典。

现在开始写代码。注意代码风格清晰，适当注释。

因为总代码不超过1000行，我们应该简洁。

现在开始：

```python
#!/usr/bin/env python3
import sys
import json
import math
import heapq
from collections import defaultdict

def parse_line(line):
    # remove leading/trailing whitespace
    stripped = line.strip()
    if not stripped:
        return None  # empty line
    parts = stripped.split()
    if len(parts) != 6:  # expecting exactly 6 fields
        return None
    timestamp, method, raw_path, status_str, duration_str, tenant_field = parts
    # validate status code
    try:
        status = int(status_str)
    except ValueError:
        return None
    # validate duration
    if not duration_str.endswith('ms'):
        return None
    try:
        duration = int(duration_str[:-2])
    except ValueError:
        return None
    # validate tenant field
    if not tenant_field.startswith('tenant='):
        return None
    tenant = tenant_field.split('=', 1)[1]  # get part after '='
    # extract path without query parameters
    path = raw_path.split('?')[0] if '?' in raw_path else raw_path
    # return parsed data
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'raw_path': raw_path,
        'status': status,
        'duration': duration,
        'tenant': tenant,
        # keep original line for slow requests
        'original_line': stripped
    }
```

小心：如果原始行有缩进，strip 会去掉空格，保留内部空格。我们保留 stripped 作为 original_line。但注意：如果原始行末尾有空格，strip 会去掉，但不会影响字段解析，所以 original_line 是 strip 后的。但要求“保留原始行”，可能指输入的原始行，包括前导/尾随空格。但如果我们 strip 后得到行，可能失去前导/尾随空格。但日志通常没有前导/尾随空格。如果存在，可能会影响解析，因为 split 会处理空白，但保留原始行最好保留原样。但空行 strip 后为空，但原始行可能是空格。但为了精确，我们应该保留原始行不变，但空行我们仍然跳过。所以 parse_line 应该同时返回原始行（未 strip）？如果要保留原始行用于输出，我们希望保留输入的原样。在解析时，我们可以先保留 raw_line = line.rstrip('\n') 等，保持原样（包括前导/尾随空格？但 split 会处理前后空格，但前导空格可能导致 split 开头有空字符串？但 split 默认以任意空白分割，会忽略前导空白，所以实际不影响字段提取。所以原始行保留原始内容，包括前导尾随空格。但空行（纯空白）可能被识别为 malformed。所以我们需要将原始行存储在记录中。最好的设计：parse_line 接收原始行（未 strip），但内部处理需要 strip 以便分割，但返回字典中包含 original_line 原始行（不带换行符）。所以我们修改：主循环从 sys.stdin 读行，line = line.rstrip('\n') 或 line = line.strip('\n')？保留原样。但空行仍然计入 malformed。所以 parse_line 接收原始行（可能包含空格），然后尝试解析。我们使用 line.rstrip('\n') 去除换行但保留其他空格。所以原始行保留。

所以重构：在计算函数中，从输入读取行（可能来自文件或 stdin）。我们读每行 line = line.rstrip('\n')，保留其他空白传入 parse_line。

如果 line 为空（去除换行后长度为0）或空白？我们保留原始。parse_line 内部处理区分空行或空白。但 line 可能全是空格，我们视为 malformed。所以 parse_line 内部先用 line 来判断是否可解析。

为了简化，我们可以先将 line.strip() 用于解析，但 original_line 传入未 strip 的。所以 parse_line 接受两个参数？或者接受 raw_line 并修改内部。我们让 parse_line 只接受 raw_line，返回字典或 None，字典中包含 original_line 字段（raw_line）。这样易于一致。

具体：
- raw_line = line.rstrip('\n')  # no need to strip
- parsed = parse_line(raw_line)
- 如果 parsed is None: malformed_lines += 1
- 否则使用 parsed

parse_line 实现：
```python
def parse_line(raw_line):
    stripped = raw_line.strip()
    if not stripped:
        return None
    parts = stripped.split()
    if len(parts) != 6:
        return None
    timestamp, method, raw_path, status_str, duration_str, tenant_field = parts
    # ... same as before
    return {
        'timestamp': timestamp,
        'method': method,
        'path': path,
        'raw_path': raw_path,
        'status': status,
        'duration': duration,
        'tenant': tenant,
        'original_line': raw_line  # but note: raw_line includes original whitespace
    }
```
但注意：raw_line 可能末尾有换行？我们已经 rstrip('\n') 去除换行。所以传入的是没有换行的。但 raw_line 可能包含回车等，但没关系。

但如果原始行有前导/尾随空格，在 strip 后用于分割，但 original_line 保留它们。这合理。

但是，在慢请求中，要求保留原始行，所以我们用 parsed['original_line']。

注意：如果 raw_line 为空（空行，去除换行后长度为0），stripped 为空，返回 None。

现在 compute_stats 接受行迭代器（例如 sys.stdin 或字符串列表）。

考虑性能：使用迭代器逐行处理。

我们定义 compute_stats(lines_iter) 返回结果字典。

内部变量：
- total_requests = 0
- malformed_lines = 0
- status_counts = defaultdict(int)
- path_counts = defaultdict(int)
- path_latencies = defaultdict(list)  # 使用list存储所有耗时
- slow_heap = []  # heap for top 10 slow
- tenant_total = defaultdict(int)
- tenant_errors = defaultdict(int)
处理每行：
- total_requests += 1
- status_counts[str(parsed['status'])] += 1 (注意键用字符串)
- path = parsed['path']
- path_counts[path] += 1
- path_latencies[path].append(parsed['duration'])
- tenant = parsed['tenant']
- tenant_total[tenant] += 1
- if parsed['status'] >= 400: tenant_errors[tenant] += 1
- if parsed['duration'] > 1000:
   # 使用 heappush，然后 if len(slow_heap) > 10: heappop
   heapq.heappush(slow_heap, (parsed['duration'], parsed['original_line'], parsed['path']))
   if len(slow_heap) > 10:
       heapq.heappop(slow_heap)

最后，构造结果：
1. top_paths: 从 path_counts 取前5。
2. p95_latency_by_path: 计算每个路径的 p95。
   - for path, latencies in path_latencies.items():
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        idx = math.ceil(0.95 * n) - 1  # 0-based index. 或者直接 idx = math.ceil(0.95 * n) - 1
        p95 = sorted_lat[idx]
        + 存储[path] = p95
   注意：使用 math.ceil(0.95 * n)，如果 n=1, ceil(0.95)=1, idx=0，是对的。
3. slow_requests: 从 slow_heap 列表（堆内容）转换为按 duration 降序排序。元素：{'original_line': line, 'path': path, 'duration': dur}。注意：堆中元素是 tuple (duration, line, path)，所以解包。
4. tenant_error_rates: 计算 ratio: round(tenant_errors[t] / tenant_total[t], 3) 存储。

输出 dict 顺序：total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines.

现在考虑一些细节：
- 如果某些路径在 p95 计算时请求数为0，但不会出现。
- 如果路径数少于5，top_paths 取全部。
- 如果 slow_requests 少于10，取全部。
- 对于 tenant_error_rates，只包括有请求的租户。注意：如果该租户没有请求，不会出现。

现在测试。

设计测试输入：

测试1：最基本：
```
2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1
2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=b2
```
期望：
total_requests=2
status_counts: {"200":1,"201":1}
top_paths: [{"path":"/api/orders","count":1},{"path":"/api/users","count":1}]
p95_latency_by_path: {"/api/orders":123,"/api/users":456}
slow_requests: 没有 >1000ms，空列表
tenant_error_rates: {"a1":0.0,"b2":0.0}
malformed_lines:0

测试2：包含错误行
```
2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1
invalid line
```
malformed_lines=1

测试3：包含查询参数
```
2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1
```
路径应为 /api/orders

测试4：慢请求测试
```
2026-05-01T12:03:18Z GET /api/orders 200 1200ms tenant=a1
2026-05-01T12:03:19Z GET /api/users 200 500ms tenant=a1
```
slow_requests 应包含第一条，耗时1200

测试5：状态码错误
```
2026-05-01T12:03:18Z GET /api/orders 404 100ms tenant=a1
```
不视为错误（4xx错误），所以 tenant_error_rates a1 为 1.0？只有一条请求且404，所以 error_rate = 1.0
若 200，则为0.0

测试6：p95 计算，多行相同路径
构建多个耗时，验证p95。

我们可以在测试函数中写多个断言。

另外，需要考虑浮点精度：但 round(1.0,3)=1.0，在 JSON 中显示 1.0。如果预期0.0，assertEqual 没问题。

现在实现 test()：

定义一些日志列表，调用 compute_stats，检查结果字典。

或者我们可以使用json对比。但是直接断言具体字段。

```python
def test():
    # Test 1: basic
    lines = [
        '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n',
        '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=b2\n',
    ]
    result = compute_stats(iter(lines))  # or pass lines directly if compute_stats expects list
    assert result['total_requests'] == 2
    assert result['status_counts'] == {'200': 1, '201': 1}
    assert len(result['top_paths']) == 2
    assert result['top_paths'][0]['count'] == 1
    # ... etc
```

但 compute_stats 期望行迭代器，我们可以传入 lines，因为 lines 也是可迭代的。

注意：compute_stats 内部会逐行读取，并调用 rstrip('\n') 处理每行。但我们传入的 lines 可能已经包含换行符？我们可以统一处理：compute_stats 从迭代器取得的每一行可以是带换行的，我们在内部 rstrip。这样灵活。若测试时传入不带换行的字符串列表，也没问题，rstrip 不会出错。所以 lines 可以是原始字符串列表（带或不带换行）。

因此 compute_stats 内部使用 line = line.rstrip('\n') 或使用 line = line.rstrip('\n') 保证去除换行，但原始文本保留。

但如果我们测试时传入不带换行的，rstrip('\n') 没有影响。

我们还可以设计 compute_stats 直接接受行迭代器（例如 sys.stdin）。对于测试，可以构造 list 并将其转换为 iter。

我们也可以在 compute_stats 中直接接受 lines (list)，并 for line in lines: 处理。然后如果传入 sys.stdin 也类似。

但是注意：sys.stdin 是文件对象，迭代返回包括换行符。所以最好内部 line = line.rstrip('\n')。这样不管是字符串还是文件，都得到去除换行符的原始行。

所以 compute_stats(lines_iter) 遍历 lines_iter。

现在完整的 compute_stats 实现：

```python
def compute_stats(lines):
    total = 0
    malformed = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    tenant_total = defaultdict(int)
    tenant_errors = defaultdict(int)
    slow_heap = []

    for line in lines:
        # if line is bytes? but stdin returns str in text mode.
        raw_line = line.rstrip('\n')
        parsed = parse_line(raw_line)
        if parsed is None:
            malformed += 1
            continue
        total += 1
        status_counts[str(parsed['status'])] += 1
        path = parsed['path']
        path_counts[path] += 1
        path_latencies[path].append(parsed['duration'])
        tenant = parsed['tenant']
        tenant_total[tenant] += 1
        if parsed['status'] >= 400:
            tenant_errors[tenant] += 1
        if parsed['duration'] > 1000:
            heapq.heappush(slow_heap, (parsed['duration'], parsed['original_line'], parsed['path']))
            if len(slow_heap) > 10:
                heapq.heappop(slow_heap)

    # top_paths
    sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths]

    # p95_latency_by_path
    p95_by_path = {}
    for path, latencies in path_latencies.items():
        if not latencies:
            continue
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        # index = ceil(0.95 * n) - 1  (0-based)
        idx = math.ceil(0.95 * n) - 1
        p95_by_path[path] = sorted_lat[idx]

    # slow_requests
    # heap has elements (duration, line, path); sort descending by duration
    slow_requests = []
    if slow_heap:
        # heap may have up to 10 elements
        # Sort descending
        sorted_slow = sorted(slow_heap, key=lambda x: x[0], reverse=True)
        for dur, line, path in sorted_slow:
            slow_requests.append({
                'original_line': line,
                'path': path,
                'duration': dur
            })

    # tenant_error_rates
    error_rates = {}
    for tenant, total_cnt in tenant_total.items():
        err = tenant_errors.get(tenant, 0)
        rate = err / total_cnt if total_cnt > 0 else 0.0
        # round to 3 decimal places
        rate_rounded = round(rate, 3)
        error_rates[tenant] = rate_rounded

    # construct result
    result = {
        'total_requests': total,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': error_rates,
        'malformed_lines': malformed
    }
    return result
```

注意：如果 slow_heap 有元素，需要去重？无重复行；但若相同行出现，不会过滤。没关系。

现在考虑 malformed_lines 计数：即使 total=0，malformed 可能大于0。

现在测试：设计测试用例，用 assert 比较 expected 与 result。

测试函数 test() 包括多个测试案例，打印一些信息，然后断言失败则终止。

不一定要全部打印，但可以输出 "test passed"等。

我们为每个测试写单独函数，或在 test() 中分块。

我们还可以使用 unittest 但要求单文件且无第三方库，内置 unittest 是可以的，但需要引入 unittest。不过简单使用 assert。

可以简单利用 assert 语句。

我将在 test() 中定义几个测试用例。

注意：计算 p95 需要使用 ceil，是向上取整索引。我们确保数学计算正确。

测试 p95:
- 5个耗时: [100,200,300,400,500] (n=5), 0.95*5=4.75, ceil=5, idx=4 -> 500
- 6个: [100,200,300,400,500,600], 0.95*6=5.7, ceil=6, idx=5 -> 600
- 2个: [100,200], 0.95*2=1.9, ceil=2, idx=1 -> 200
- 1个: [150], 0.95*1=0.95, ceil=1, idx=0 -> 150

所以 p95 在样本少时相当于最大值。这符合定义。

现在模拟测试：

测试案例1: basic:
```python
lines = [
    '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n',
    '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=b2\n',
]
result = compute_stats(lines)
assert result['total_requests'] == 2
assert result['status_counts'] == {'200':1,'201':1}
assert result['top_paths'] == [{'path':'/api/orders','count':1},{'path':'/api/users','count':1}]
assert result['p95_latency_by_path'] == {'/api/orders':123,'/api/users':456}
assert result['slow_requests'] == []
assert result['tenant_error_rates'] == {'a1':0.0,'b2':0.0}
assert result['malformed_lines'] == 0
```

注意：顺序如果 top_paths 由于排序计数相同，顺序可能任意（因为两个路径计数都是1，排序不稳定）。在我们的sorted_paths中，如果计数相同，顺序由 path_counts.items() 的迭代顺序，在Python中字典顺序是插入顺序（3.7+）。但 path_counts 中是按解析顺序插入的，所以先出现 /api/orders 后 /api/users，所以排序后两者计数相同，但 sorted 是稳定的，所以保持原顺序所以第一个是 /api/orders，第二个是 /api/users。但为了测试可靠，我们最好不假设顺序，或者测试时保证计数不同，或者我们比较集合。但这里计数相同，顺序可能依赖版本。但既然我们控制输入顺序，应该一致。但稳妥可只检查计数集合。或者我们排序 top_paths 再比较？我们可以对 top_paths 按 path 排序再比较。但可接受。

或者我们使用 assert top_paths 顺序无关紧要，我们可比较内容。如： assert set([(p['path'],p['count']) for p in result['top_paths']]) == {('/api/orders',1),('/api/users',1)}.

但为了简化，我们可以选择构建不同计数的测试避免顺序问题。

测试2: 路径含查询参数
```python
lines = ['2026-05-01T12:03:18Z GET /api/orders?page=2 200 123ms tenant=a1\n']
result = compute_stats(lines)
assert result['total_requests'] == 1
assert '/api/orders' in result['p95_latency_by_path']
```

测试3: malformed 行
```python
lines = ['invalid line\n', 'another bad\n']
result = compute_stats(lines)
assert result['malformed_lines'] == 2
assert result['total_requests'] == 0
```

测试4: 慢请求
```python
lines = [
    'line1 GET /path1 200 1200ms tenant=t1\n',
    'line2 GET /path2 200 800ms tenant=t1\n',
    'line3 GET /path3 200 1100ms tenant=t1\n',
]
result = compute_stats(lines)
assert len(result['slow_requests']) == 2  # only >1000
assert result['slow_requests'][0]['duration'] == 1200  # after descending sort
assert result['slow_requests'][1]['duration'] == 1100
```

测试5: 错误率
```python
lines = [
    'GET /a 200 100ms tenant=t1\n',
    'GET /b 404 50ms tenant=t1\n',
    'GET /c 500 200ms tenant=t2\n',
]
result = compute_stats(lines)
assert result['tenant_error_rates']['t1'] == 0.5  # 1 error out of 2
assert result['tenant_error_rates']['t2'] == 1.0
```

测试6: p95 计算（多条）
```python
lines = [f'GET /x 200 {i}ms tenant=t1\n' for i in [100,200,300,400,500]]
result = compute_stats(lines)
assert result['p95_latency_by_path']['/x'] == 500
```

测试7: top_paths 多于5，限5
```python
paths = ['/a','/b','/c','/d','/e','/f']
lines = [f'GET {p} 200 100ms tenant=t1\n' for p in paths]
# each path once, so top5 will be any 5 of 6, sorted by count same, so first 5 inserted
result = compute_stats(lines)
assert len(result['top_paths']) == 5
```

这些测试会覆盖主要功能。

另外，测试空行：
```python
lines = ['\n', 'GET /x 200 100ms tenant=t1\n']
result = compute_stats(lines)
assert result['malformed_lines'] == 1
assert result['total_requests'] == 1
```

现在 test() 里运行这些测试，如果通过打印 "All tests passed" 或其他。

注意：如果某个断言失败，会引发 AssertionError 并停止。我们可以用 try 或打印哪个失败。

我们还可以使用 unittest.TestCase 但不需要，简单的 assert 即可。

现在考虑一些边界：parse_line 中 validation 是否过严？比如，tenant 必须严格 "tenant=..."，如果格式是 "tenant= a1" 中间有空格？但分割后应该是 "tenant=a1" 整体。如果租户值包含等号？不可能。如果存在空格，分割会多出字段，导致长度>6，被判定 malformed。所以我们要求6个字段，是合适的。

关于耗时：假设全部是 ms，但也有可能是 s？这里假设 ms。所以我们只接受结尾 "ms"。

状态码为整数：但可能状态码字符串包含其他字符？不允许。

其他字段如时间格式等不验证。

现在程序结构：

定义 parse_line, compute_stats, test, main.

在 main 中，如果 sys.argv[1] == '--test'（注意可能有其他参数？只处理 --test），则调用 test() 并退出。否则从 sys.stdin 读取，调用 compute_stats(sys.stdin)，然后输出 json.dumps(result, ensure_ascii=False, indent=2) 或其他。

但注意：如果直接输出 JSON，我们希望紧凑一些？可以不加 indent，但可读性。考虑要求只输出 JSON，可以不带缩进。但带缩进更清晰。我们使用默认（无缩进）或 indent=2？但测试时也方便。不过输出 JSON 不是人类阅读，紧凑即可。按常规，json.dumps 默认紧凑。我们使用 json.dumps(result, ensure_ascii=False) 输出。

记得处理 sys.stdout 写入，print 即可。

如果使用 print(json.dumps(result, ensure_ascii=False))，会打印字符串后带换行。这应该是可以的。

注意：如果出现非 ASCII 字符（如中文路径？）但日志可能只包含 ASCII，但 ensure_ascii=False 确保不转义。

现在考虑是否支持文件重定向等，没问题。

现在编写 test() 函数。

注意：在测试中，需要调用 compute_stats，它会尝试对每行执行 rstrip('\n')，但测试时字符串可能已经有换行或没有。为了统一，我们在测试时包含换行符，但 compute_stats 内部 rstrip('\n') 会去除。如果不包含，rstrip 也不影响。

所以我们可以在测试中写带换行的字符串，但比较结果时使用原始行（即 original_line 会是去除换行后的内容？因为 compute_stats 会对每行 line 先 rstrip('\n')，然后传入 parse_line。parse_line 内部接收到的是去除换行的 raw_line，所以 original_line 会是没有换行的行。如果我们测试时提供的行没有换行，original_line 就是原样。如果有换行，rstrip 会去掉换行。为了测试时 original_line 容易预期，我们通常提供不带换行的字符串给 compute_stats，因为 compute_stats 会将行的换行去掉。但注意：sys.stdin 回来的行默认包含换行，所以 compute_stats 处理时用 rstrip('\n') 去掉。所以在测试中，我们可以直接传入不带换行的字符串列表，得到 original_line 就是该字符串。这样更容易预期。我们也可以在传入时包含换行，但 original_line 可能变成去掉换行的版本，也许和输入不一致。为了保留原始行，如果我们传入的行包含换行，我们希望原始行保留除换行外的全部，包括可能的回车。使用 rstrip('\n') 只会去除尾随换行，不影响其他。所以如果我们传入 "test line\n"，rstrip('\n') 得到 "test line"，original_line 设为 "test line"，而不是原始输入 "test line\n"。这可能不是真正的原始行。但通常大家认为原始行包括换行？但 JSON 输出 original_line 时不应该包含换行，因为 JSON 字符串不能包含控制字符？虽然可以编码 \n，但通常保留原始行时不包含换行。所以去除换行是合理的。所以我们计算 statistics 时，从文件读入时使用 line = line.rstrip('\n') 得到不带换行的行，然后解析，并将 original_line 设为该不带换行的行。但这样 original_line 丢失末尾换行，但对于 JSON 输出来说更干净。所以我们在测试时要保证提供原始行（不带换行）作为预期。在我们构造的测试 lines 中，我们直接提供不带换行的字符串，或带换行但预期 original_line 是我们提供的字符串去除换行后的。为了简单，我们在测试中传入不带换行的字符串列表。

所以 compute_stats 中的处理：line = line.rstrip('\n') 并传入 parse_line。如果 line 本身就是字符串，没问题。

但是注意：如果 line 中有 \r 也需要处理？通常使用 rstrip('\n') 已经足够。因为文本模式读取会转换换行符。为了兼容，可以使用 line = line.rstrip('\r\n') 或 line = line.strip('\n')？但 rstrip('\n') 不删除 \r，所以 \r 会保留在 original_line 中。但通常不会。

为安全：line = line.rstrip('\n') 是通常作法。我们用这个。

现在测试用例：

我们构造测试数据，不使用换行符，直接提供字符串。这样可以预测。

```python
def test():
    # Test 1: basic
    lines1 = [
        '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=b2',
    ]
    res1 = compute_stats(lines1)
    assert res1['total_requests'] == 2
    assert res1['status_counts'] == {'200': 1, '201': 1}
    # top_paths: both count=1, order as inserted
    assert len(res1['top_paths']) == 2
    assert res1['top_paths'][0] == {'path': '/api/orders', 'count': 1}
    assert res1['top_paths'][1] == {'path': '/api/users', 'count': 1}
    assert res1['p95_latency_by_path'] == {'/api/orders': 123, '/api/users': 456}
    assert res1['slow_requests'] == []
    assert res1['tenant_error_rates'] == {'a1': 0.0, 'b2': 0.0}
    assert res1['malformed_lines'] == 0

    # Test 2: query parameters removal
    lines2 = [
        '2026-05-01T12:03:18Z GET /api/orders?page=2&sort=asc 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=a1',
    ]
    res2 = compute_stats(lines2)
    assert res2['total_requests'] == 2
    assert res2['p95_latency_by_path'] == {'/api/orders': 123, '/api/users': 456}
    assert res2['slow_requests'] == []
    assert res2['malformed_lines'] == 0

    # Test 3: malformed lines
    lines3 = [
        '',
        'bad line without enough fields',
        '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z GET /api/orders 200 abcms tenant=a1',  # invalid duration
        '2026-05-01T12:03:20Z GET /api/orders 200 100ms tenant=a1',  # valid
        '2026-05-01T12:03:21Z GET /api/orders 200 100ms invalidtenant', # tenant not starting with 'tenant='
    ]
    res3 = compute_stats(lines3)
    assert res3['total_requests'] == 2  # only third and fifth lines are valid? Actually check: empty line (1), bad fields (2), third valid (3), fourth invalid duration (4) -> malformed? duration abcms not ending with digits? abcms not convertible so malformed, fifth valid, sixth invalid tenant field (not start with tenant=) -> malformed.
    # So valid: index3 and index5? index from 0: first 0,1 invalid, 2 valid (third line), 3 invalid, 4 valid (fifth line), 5 invalid => 2 valid.
    assert res3['total_requests'] == 2
    assert res3['malformed_lines'] == 4  # lines 0,1,3,5
    # Also check that p95 etc only for valid paths: /api/orders appears twice? third line /api/orders, fifth line /api/orders? yes both /api/orders. So p95 should be present.
    assert res3['p95_latency_by_path']['/api/orders'] == 123  # from line2? Actually third line duration 123, fifth line 100 -> sorted [100,123] -> p95: index=ceil(0.95*2)-1 = ceil(1.9)-1=2-1=1 -> second element 123. So p95=123. Good.
    assert res3['total_requests'] == 2

    # Test 4: slow requests
    lines4 = [
        'slow1 GET /path1 200 1200ms tenant=t1',
        'slow2 GET /path2 200 800ms tenant=t1',
        'slow3 GET /path3 200 1500ms tenant=t1',
        'slow4 GET /path4 200 900ms tenant=t1',
        'fast1 GET /fast 200 100ms tenant=t2',
    ]
    res4 = compute_stats(lines4)
    # slow_requests should contain only >1000: 1200 and 1500, sorted descending: 1500,1200
    assert len(res4['slow_requests']) == 2
    assert res4['slow_requests'][0]['duration'] == 1500
    assert res4['slow_requests'][0]['path'] == '/path3'
    assert res4['slow_requests'][0]['original_line'] == lines4[2]  # the line 'slow3 ...' (without newline)
    assert res4['slow_requests'][1]['duration'] == 1200
    assert res4['slow_requests'][1]['path'] == '/path1'
    # Ensure fast ones not included
    # Ensure path_counts include all

    # Test 5: error rates
    lines5 = [
        'GET /a 200 100ms tenant=t1',
        'GET /b 404 50ms tenant=t1',
        'GET /c 500 200ms tenant=t2',
        'GET /d 300 150ms tenant=t1',
    ]
    res5 = compute_stats(lines5)
    assert res5['tenant_error_rates']['t1'] == 0.333  # 1 error out of 3? Actually t1 has lines 0(200),1(404),3(300) -> only 404 is error, so 1/3 = 0.333... round 3 => 0.333
    # Check rounding: 1/3 = 0.333333... round to 0.333
    assert res5['tenant_error_rates']['t2'] == 1.0

    # Test 6: p95 multiple entries
    lines6 = [f'GET /x 200 {i}ms tenant=t1' for i in [100,200,300,400,500]]
    res6 = compute_stats(lines6)
    assert res6['p95_latency_by_path']['/x'] == 500

    # Test 7: top_paths limit 5
    paths7 = ['/api/orders', '/api/users', '/api/products', '/api/cart', '/api/checkout', '/api/admin']
    lines7 = [f'GET {p} 200 100ms tenant=t1' for p in paths7]  # each has count 1
    res7 = compute_stats(lines7)
    assert len(res7['top_paths']) == 5
    # Since all counts =1, the first 5 in iteration order taken. We'll verify they are first 5 of our list
    # But iteration order of path_counts is insertion order. So top_paths should be first 5 paths in order of lines7.
    expected_top5_paths = paths7[:5]  # ['/api/orders','/api/users','/api/products','/api/cart','/api/checkout']
    for i, tp in enumerate(res7['top_paths']):
        assert tp['path'] == expected_top5_paths[i]
        assert tp['count'] == 1

    # Test 8: status codes with 201 and 404 etc.
    lines8 = [
        'GET /a 201 100ms tenant=t1',
        'POST /b 404 50ms tenant=t1',
        'PUT /c 500 200ms tenant=t2',
        'DELETE /d 301 150ms tenant=t1',
    ]
    res8 = compute_stats(lines8)
    assert res8['status_counts'] == {'201': 1, '404': 1, '500': 1, '301': 1}

    # Test 9: empty input
    lines9 = []
    res9 = compute_stats(lines9)
    assert res9['total_requests'] == 0
    assert res9['malformed_lines'] == 0
    assert res9['top_paths'] == []
    assert res9['p95_latency_by_path'] == {}
    assert res9['slow_requests'] == []
    assert res9['tenant_error_rates'] == {}

    print("All tests passed.")
```

可能还需要测试 slow_heap 的使用，确保 it works。

但考虑堆实现：我们担心如果慢请求记录多于10，是否保留正确。我们可以测试：
```python
lines10 = [f'GET /path 200 {i}ms tenant=t1' for i in range(1100, 1120)]  # 20 slow entries >1000
res10 = compute_stats(lines10)
assert len(res10['slow_requests']) == 10
assert res10['slow_requests'][0]['duration'] == 1119  # max
assert res10['slow_requests'][-1]['duration'] == 1110  # min of top 10
```
但注意，使用堆可能使顺序不完全保证输出排序？我们最终做 descending sort，所以顺序正确。

但测试中，我们需要检查原始行是否正确。original_line 会是构造的字符串（无换行），匹配。

为验证索引，我们可以构造慢请求列表并检查。

这样测试充分。

但是注意：我们的测试字符串中没有换行符，但 compute_stats 仍会对每行 rstrip('\n')，没有影响。

现在，考虑解析时对于 duration_str 验证：必须严格以 ms 结尾，如 123ms。但是否可能有空格？如 "123 ms"? 但 split 会将其视为两个字段 "123" 和 "ms"? 所以字段数变为7，被识别为 malformed。所以只有连续 "123ms" 被接受。

现在，还需要考虑路径本身可能包含查询参数，其中可能包含等号。split 不会误分割，因为等号没有空格。

所以我们的 parse_line 在绝大多数情况下是有效的。

现在，在 compute_stats 中，使用 math.ceil(0.95 * n) - 1 索引。要注意：如果 n=0，不会进入循环。对于 n=1，0.95*1=0.95，ceil=1，索引0，正确。

但如果 n 很大，没问题。

现在，我们可能会遇到浮点精度问题：比如 0.95*20=19.0，但浮点可能表示为 18.9999999，ceil 可能得到19而不是20？实际上 0.95 可以精确表示为 19/20? 0.95 是浮点二进制不能精确表示，但 0.95 * 整数可能产生略小于真实值的情况。例如 0.95 * 100 可能 94.999999...，ceil 可能得到 95 还是 94? 这取决于浮点误差。Python 的 ceil 会向上取整，即使 94.99999 也会取到 95。但若由于浮点误差，0.95*20 可能略大于 19.0? 我们可以使用 Decimal 来避免，但导入 Decimal 标准库（不需要第三方），可以使用 decimal.Decimal 得到精确小数。但为了简洁和性能，使用 math.ceil 应该安全，因为 0.95 是 95/100 = 19/20，可以用分数计算避免浮点：idx = (95 * n + 99) // 100 - 1? 注意：ceil(p * n) where p=0.95 = 95/100，所以索引 = ceil(95*n/100) - 1。用整数运算：idx = (95 * n + 99) // 100 - 1。但需要确保 n 为正。验证：n=5 => (95*5+99)//100 = (475+99)//100=574//100=5, -1=4，索引4（第5个）。n=1 => (95+99)//100=194//100=1, -1=0。n=2 => (190+99)//100=289//100=2, -1=1。正确。n=20 => (1900+99)//100=1999//100=19, -1=18。所以整数运算更精确。建议使用整数运算，避免浮点误差。这更安全。我们采用这种方法。

因此计算 p95：if n>0: idx = (95 * n + 99) // 100 - 1。然后取 sorted_lat[idx]。

对于 n==0 不会出现。

所以 p95_by_path[path] = sorted_lat[(95 * n + 99) // 100 - 1]

但是当 n=0 时，我们不计算。所以没问题。

现在更新 compute_stats：

```python
    for path, latencies in path_latencies.items():
        if not latencies:
            continue
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        idx = (95 * n + 99) // 100 - 1
        p95_by_path[path] = sorted_lat[idx]
```

验证 idx 不会越界。当 n=1: (95+99)//100=1, -1=0; n=2: (190+99)//100=2, -1=1; n=3: (285+99)//100=3, -1=2; 总取最后一个元素。所以越界不会。

现在，对于 slow_requests 堆，我们使用 (duration, original_line, path) 元组，duration 为整数。由于堆比较可能比较第二个字段（original_line 字符串），如果 duration 相同，会按字符串比较，这可能导致堆元素之间可比较，但不会出错。但为了唯一性，我们可以插入计数器，但没必要。

但注意：original_line 是字符串，如果 duration 相同且 original_line 也相同（不可能，除非相同行出现两次），但比较也会工作。所以没问题。

现在，test 中需要增加 p95 整数计算的测试。

我们可以测试 p95 整数版本：用之前构造的数据测试。

另外，测试空列表。

现在考虑输出 JSON 时，希望键的顺序如要求。我们使用普通 dict，按顺序插入。顺序为：total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines。我们已经这样做了。

现在，确保 malformed_lines 在最后，但要求中未明确顺序，但通常顺序无关紧要，但可读性。

现在，一些小的注意事项：对于 tenant_error_rates，要求保留三位小数。我们使用 round(rate, 3)。对于 0.0，会输出 0.0，但可能期望 0.000？但 JSON 数字 0.0 是合法浮点数。但可能被解读为 0.0。但许多情况下，保留三位小数字通常也允许 0.0。但严格保留三位小数应该总是显示三位小数，但 JSON 没有要求。所以我认为 round 可以接受。如果希望确保，我们可以使用格式化 "%.3f" 再转 float，但浮点表示不固定位数。可考虑使用 Decimal，但复杂。保险起见，使用 round 就足够。

但注意：当我们输出 0.0 时，json.dumps 会输出 "0.0"，但在 Python 中 round(0.0,3) 返回 0.0，类型 float，序列化后为 0.0。对于 0.333 会输出 0.333。对于 1.0 会输出 1.0。应该是可接受的。

但如果测试期望 0.0 与 0.000 相等，在 Python 中 assertEqual 等比较数值是相等的。所以没问题。

现在，实现 main 部分：

```python
def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test()
    else:
        result = compute_stats(sys.stdin)
        print(json.dumps(result, ensure_ascii=False))
```

但注意：sys.stdin 在文本模式下迭代返回行包括换行符。所以我们直接传入。

需要考虑的是，当没有 `--test` 参数但可能有些其他参数？只识别 `--test`，其他忽略或用作其他？但要求是：当使用 `--test` 参数运行时执行测试。所以我们只检测 `--test`。

现在，程序可能被直接运行，或者 import 但不会执行。我们通过 `if __name__ == '__main__'` 调用 main()。

现在已经完成。

可能还有一些细节：

- 总代码不超过1000行，我们的代码远远少于。
- 不使用第三方库：只用了 sys, json, math, heapq, collections.defaultdict。这些标准库。
- 代码结构清晰，有注释。

测试函数可以写更多的测试，确保覆盖。

现在编写代码，最终整合。

考虑 parse_line 中，我们要求 tenant_field.startswith('tenant=')，但可能等号前后没有多余空格。如果租户值是空字符串，如 "tenant="，split('=',1)[1] 会得到空字符串。这是允许的。但可能无意义。不过我们接受。

或者我们也可以不验证前缀，只要求有等号并提取 value。但按格式说 "tenant=a1"，所以我们验证。

现在，编写完整的代码。

注意：我们可能遇到原始行包含不可见字符如 \r，可以用 line.rstrip('\n\r') 去除换行和回车。但使用 line.rstrip('\n') 如果 Windows 下读取可能会有 \r 残留，但 JSON 输出时可能会包含 \r，这不一定有害。但为了更干净，我们改为 line.rstrip('\n') 或者 line.removesuffix('\n')？但 rstrip('\n') 只去除尾随换行，不会去除 \r 在末尾。如果行尾是 \r\n，rstrip('\n') 会去除 \n 但留下 \r。这会导致 original_line 包含 \r。这可能会出现在 JSON 字符串中，被编码为 \r。通常可接受。但如果我们想要更准确，可以同时去除 \r\n：使用 line.rstrip('\r\n')。但这样会去除所有尾随 \r 和 \n，如果行内包含 \r（不太可能）则会丢失。但常见情况是文本模式读取自动转换换行符？在 Python 中，文本模式（默认）下，所有换行符被转换为 '\n'。所以 sys.stdin 读取时，\r\n 会被转换为 '\n'。所以不需要担心 \r。所以我们只需要 line.rstrip('\n') 即可。所以我们保持现状。

现在实现。

另外，注意编码：输入可能是 utf-8，但 json 输出 ensure_ascii=False 会输出非 ASCII。但我们的路径、租户等可能是 ASCII，所以 safe。

现在编写代码。

我们检查 p95 计算是否在 n==0 时忽略。我们使用 if not latencies: continue。

考虑 top_paths：如果路径数少于5，全部返回。我们只取前5，自然满足。

现在考虑包括每个路径即使只有一次也返回 p95。

现在完整地写代码。

当出现非常规状态码如 1000？视为错误？只定义 4xx/5xx 错误，所以 >=400 算错误（包括 400-599）。但 1000 可能大于 599 但算错误？根据通常定义，4xx/5xx 指 400-499 和 500-599。所以我们的条件应该是 400 <= status <= 599 才算错误。但更简单的是 status >= 400 and status < 600? 但 600 以上可能不是标准，但为了避免将 100 也算错误，我们应限制状态码范围在 400-599。但题目说 4xx/5xx 算错误，明确 4开头和5开头，所以应该是 400-599。所以我们应检查 status 是否在 [400, 599] 范围内。但我们的代码使用 parsed['status'] >= 400，会包含 600 等。但正常日志不会有 600。但为了符合 4xx/5xx，我们可以用 status >= 400 and status < 600。但题目没有明确定义范围，但通常认为 1xx,2xx,3xx 成功或重定向，4xx,5xx 错误。所以我们检查 status >= 400 and status < 600。但是否有 418 I'm a teapot？是4xx。所以用 400-599。我们使用 400 <= status <= 599。我们改为 if 400 <= status <= 599。更好。

所以更新：条件 if 400 <= parsed['status'] <= 599: tenant_errors[tenant] += 1。

注意：在 status_counts 中我们记录所有状态码。

现在，p95 使用整数运算，之前已经。

现在，测试中也需要考虑错误率只包括 400-599。我们之前测试用例已包括。

现在，写最终的 test 函数时，需要调整 test 5 中的 300 状态码（300 是 3xx，不算错误）。所以 t1 错误仍然只有 404（一行）。所以正确。

现在，测试 8 中有 301 状态码，不算错误。

所以 test 5 保持不变。

现在，我们为测试写一个 case 验证错误范围：status 600（非标准）不算错误。但我们不测试这个。

现在，整体代码。

我们还应该考虑：如果路径包含片段标识符 #？例如 /api/orders#anchor? 但一般不常见。如果包含 #，我们可能需要考虑去掉片段。但题目没有明确，但要求去掉查询参数，所以我们可以同时去掉片段：用 .split('?')[0].split('#')[0] 或者直接用 urllib.parse 但避免。我们用 .split('?')[0].split('#')[0] 确保路径干净。这样可以同时去除查询和片段。但题目只说路径可能包含查询参数，未说片段。但为健壮，我们去掉片段。path = raw_path.split('?')[0].split('#')[0]。或者更安全：用 parse_qs 但没必要。

更新 parse_line 中 path 提取：`path = raw_path.split('?')[0].split('#')[0]`。

现在，考虑原始路径可能包含 URL 编码？不需要处理，只需保留路径部分。

现在，测试中相应增加 fragment 测试用例，但我们可以在 test 中不包含。

现在，重新审查要求：top_paths 和 p95_latency_by_path 中的路径应该是不含查询参数的。所以我们的 path 提取正确。

现在，输出 JSON 时，对于空字段：如 top_paths 为空数组，p95_latency_by_path 为空对象等。

现在，考虑 malformed_lines 在输出最终 JSON 中，要求是包含量。我们放在最后。

现在，编写最终代码。

可能的问题：在 compute_stats 中，我们使用了 from collections import defaultdict。需要导入。

另外，我们定义了 parse_line 内部，但当 parse_line 返回 None 时，我们增加 malformed 计数。但注意：如果行完全空白，我们同样返回 None，并计入 malformed_lines。这是符合逻辑的。

但空行是否应该计入 malformed？题目未明确，但“跳过无法解析的行”，空白行无法解析，应计入。所以我们的处理合理。

现在，在 test 中我们测试了空行。

现在，我们写 components。

为了更健壮，我们可以在 parse_line 中增加对 status 大于 0 的检查？但无所谓。

现在，写代码。

代码风格：函数定义之间加空行。

现在，开始写代码。

需要注意：计算 p95，当 n>0 但索引计算安全。我们计算 idx = (95 * n + 99) // 100 - 1。但对于 n=0 不会使用。但为安全，我们可以在计算前检查 n>0，否则 continue，我们已经检查了 latencies not empty。

现在，所有内容写入文件。

现在，我们测试一下自己的一些用例。

例如，用提供的样例输入：
```
2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1
```
预期输出？

我们可以手动计算。

但信任代码。

现在，关于 slow_requests：如果慢请求多于10，堆会保留10个最大的，但注意如果duration相同，堆可能因为比较插入顺序不确定，但最终排序后我们会得到正确的10个记录的降序。但需注意：当 heap 大小固定10时，若新记录duration大于当前堆中最小duration，则 pop 最小再 push，保持堆中为10个最大。但如果有 records 具有相同 duration，则根据比较，可能保留最新或旧记录？但最终降序列表会包含那些记录，但可能不是期望的“前10条”（如果有超过10条且 duration 相同，则只保留10条，但如果有相同 duration 的记录多于10，则丢弃了一些。但通常 slow_requests 要求耗时大于1000ms的前10条，按耗时降序。如果超过10条，只取前10条，如果耗时相同，可以任意选择10条。所以我们的堆实现能够挑选出（任意）10条最大的。如果有许多相同最大耗时，则可能保留其中10条，这符合要求。所以可以。

但注意：如果所有记录都大于1000，且 duration 都相等（如都是1500ms），那么堆只会保留前10个遇到的记录（当堆满后，新记录 duration == 堆顶最小 duration，则不替换？我们的处理是：先 heappush，再检查 if len >10 则 heappop。这样总是 push 然后pop，因此即使 duration 相等，新记录也会被插入，然后pop最小（可能是新记录或老记录）。所以堆中的元素会不断替换，但最终会保留最后10个记录，而不是前10个。因为每次 push 后 size>10 pop，所以总是移除当前最小的 duration，如果所有 duration 相等，所有记录看起来相等，堆比较会按第二个元素（line）进行？所以可能会逐个移除，最终保留的是任意10个，取决于 line 的排序。但按照时间顺序可能不保序。如果要求“前10条”指按出现顺序的前10条？题目说“前10条按耗时降序”，排序条件是耗时，如果耗时相同，不要求出现顺序。所以任意10条均可。所以我们的实现是可接受的。如果要求强调“前10条”可能意味着按输入顺序（时间），但难点在于先要耗时降序，所以耗时相同的顺序可能是任意的。所以我们的做法没问题。但如果我们希望保留最早的相同耗时的记录，可以调整堆处理，更复杂。但题目没有明确，所以不必。

但为了更符合常理，我们可以改变策略：收集所有慢请求列表，然后排序取前10。这样保留所有记录，更简单，且顺序稳定（输入顺序可能影响排序稳定性但可以借助 index）。但可能内存增多但日志大小未知。如果慢请求很多（例如百万），全收集会消耗内存。但题目通常不会这么大数据。但为简单，我们可以不考虑极端情况，使用全部收集法。但题目要求“前10条”暗示我们可以只保留10条而不用全部收集。但为了代码简洁，我们可以使用 heapq.nlargest 方案，收集所有符合条件的记录，然后用 nlargest。但 nlargest 需要可迭代对象，内部会生成列表再 top。但如果我们已经有列表，也可以直接用 sorted 取前10。这样更直接：

如果我们选择全收集，定义 slow_list = []，当 duration>1000 时 append (duration, original_line, path)。最后，sorted_slow = sorted(slow_list, key=lambda x: x[0], reverse=True)[:10] 即可。这样编码简单，不易出错。而且如果慢请求数量很大（比如十万），排序十万个元素可能比堆略耗内存，但这也是可接受的。我倾向于采用全收集方法，因为它更简单。

权衡：按照题目风格，可能希望使用堆优化。但代码长度差不多。为了清晰，我们可以使用堆，但要确保正确。但堆方法需要考虑边界情况如相等耗时替换可能不符合“前10条”的常规理解（可能期望是耗时降序，耗时相同时按出现顺序取前10，但题目没说）。但全收集排序更符合直觉。所以为了可靠，我们使用全收集，最后排序取前10。这样避免堆比较的复杂性。由于我们无性能要求，使用全收集。

修改：collect all slow_requests in a list, then after loop, sort and take top 10.

注意：如果慢请求只有9个，则全取。

所以代码：

```python
slow_requests_data = []
# ...
if parsed['duration'] > 1000:
    slow_requests_data.append((parsed['duration'], parsed['original_line'], parsed['path']))
# after loop:
slow_requests_data.sort(key=lambda x: x[0], reverse=True)
slow_requests = [{'original_line': line, 'path': path, 'duration': dur} for dur, line, path in slow_requests_data[:10]]
```

这样更简单，而且顺序确定性好（按 duration 降序，相同 duration 时保持列表排序的稳定性，即保留原始顺序（因为 list 按插入顺序，而排序是稳定的，所以相同 duration 保持原顺序，即输入顺序）。这应该符合“前10条”的要求。

所以决定采用全收集。

现在更新 compute_stats。

为了性能，如果慢请求很多（>1e5），排序可能稍慢，但整体处理通常可接受。

现在测试。

现在重新设计 compute_stats 中的 slow_requests 部分。

现在整体。

下面是完整的代码框架：

```python
#!/usr/bin/env python3
import sys
import json
import math
from collections import defaultdict

def parse_line(raw_line):
    # ...
    pass

def compute_stats(lines):
    total = 0
    malformed = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    tenant_total = defaultdict(int)
    tenant_errors = defaultdict(int)
    slow_data = []

    for line in lines:
        raw_line = line.rstrip('\n')
        parsed = parse_line(raw_line)
        if parsed is None:
            malformed += 1
            continue
        total += 1
        status_counts[str(parsed['status'])] += 1
        path = parsed['path']
        path_counts[path] += 1
        path_latencies[path].append(parsed['duration'])
        tenant = parsed['tenant']
        tenant_total[tenant] += 1
        if 400 <= parsed['status'] <= 599:
            tenant_errors[tenant] += 1
        if parsed['duration'] > 1000:
            slow_data.append((parsed['duration'], parsed['original_line'], parsed['path']))

    # top_paths
    sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths]

    # p95_latency_by_path
    p95_by_path = {}
    for path, latencies in path_latencies.items():
        if not latencies:
            continue
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        idx = (95 * n + 99) // 100 - 1
        p95_by_path[path] = sorted_lat[idx]

    # slow_requests
    slow_data.sort(key=lambda x: x[0], reverse=True)
    slow_requests = []
    for dur, line, path in slow_data[:10]:
        slow_requests.append({
            'original_line': line,
            'path': path,
            'duration': dur
        })

    # tenant_error_rates
    error_rates = {}
    for tenant, tot in tenant_total.items():
        err = tenant_errors.get(tenant, 0)
        rate = err / tot if tot > 0 else 0.0
        error_rates[tenant] = round(rate, 3)

    result = {
        'total_requests': total,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': error_rates,
        'malformed_lines': malformed
    }
    return result

def test():
    # ... tests here

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test()
    else:
        result = compute_stats(sys.stdin)
        print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

现在编写 parse_line 函数。

```python
def parse_line(raw_line):
    stripped = raw_line.strip()
    if not stripped:
        return None
    parts = stripped.split()
    if len(parts) != 6:
        return None
    timestamp, method, raw_path, status_str, duration_str, tenant_field = parts
    # status
    try:
        status = int(status_str)
    except ValueError:
        return None
    # duration
    if not duration_str.endswith('ms'):
        return None
    try:
        duration = int(duration_str[:-2])
    except ValueError:
        return None
    # tenant
    if not tenant_field.startswith('tenant='):
        return None
    tenant = tenant_field.split('=', 1)[1]
    # path without query/fragment
    path = raw_path.split('?')[0].split('#')[0]  # keep only the path before ? or #
    # return dict
    return {
        'timestamp': timestamp,
        'method': method,
        'raw_path': raw_path,
        'path': path,
        'status': status,
        'duration': duration,
        'tenant': tenant,
        'original_line': raw_line
    }
```

注意：我们使用 split('=')[1] 但最好限制只分割一次：split('=', 1) 确保不会因值含有等号而出错。但值如果包含等号，只取第一次等号后的剩余部分作为租户值。例如 tenant=a=b 则 tenant 为 a=b。可以接受。

现在完成。

现在 test() 函数需要包含多个测试，包括前面设计的，并根据代码调整。因为 slow_requests 实现变了，所以测试需要调整但基本原则一致。

我们还需要测试 p95 计算整数运算，在 test6 已经测试了。但需要验证其他 n 值如 n=1,2,3. 我们可以添加专门测试。

test() 内我们将包含多个 test_* 函数或直接测试。

我们假设 compute_stats 接受列表（迭代器），所以可以直接传入列表。在测试中，我们传入字符串列表（不含换行）。由于 compute_stats 内部 line.rstrip('\n')，所以不会改变，original_line 就是我们传入的字符串。好。

现在编写 test() 函数，包含多个 case，每个 case 断言。最后打印成功。

使用 assert 语句。

现在，注意：输出 json 时只输出 JSON，没有其他输出。测试时会打印 "All tests passed." 等，这符合测试模式输出。

现在，考虑当 --test 参数有误时？只检查第一个参数是否为 '--test'。其他忽略。

现在，确认程序应该可以处理标准输入中的空行、不规则行等。

现在，测试代码覆盖所有要求。

现在，我们最后考虑一些极端情况：

- 路径为空？日志不可能。
- 状态码为 0？可能被忽略。

现在，我们添加一个测试来确认 malformed 行被正确计数：

假如行中有多个空格，split 后字段数仍可能为6？由于多个空格，split 会合并，所以可能变为6。但如果 extra spaces 使得分割出额外字段，字段数会变多。假设线上：`2026-05-01T12:03:18Z  GET  /api/orders  200  123ms  tenant=a1`（双空格），split 后仍为6，因为默认分割会忽略空白，不会产生空字段。所以 len(parts)=6，正常解析。所以多重空格是可容忍的。这样多行格式不一致也能解析。所以我们的 parse_line 依赖于 split 的默认行为，能处理额外空白。因此需要字段数正好6，但 split 会将多个空白视为分隔符，所以不会产生多余部分。所以符合大部分变体。

但如果行中某个字段内部有空格（如路径包含空格）但这种情况较少。不考虑。

现在，编写代码。

优化：计算 p95 时，latencies 排序可能耗时，但每个路径单独排序。

现在，我们考虑可能对 latencies 列表排序时使用内置 sort。

现在，所有代码如下，包含测试。

确认总行数控制在1000行内。

开始编写最后代码。

我将按照上面思路编写，并加入测试。

---

预先看，有几个潜在问题：

1. 在 compute_stats 中，我们对 path_counts 排序时，如果有两个路径 count 相同，排序稳定，所以按插入顺序（即第一次出现路径的顺序）决定前后。但插入顺序由 path_latencies 字典首次插入路径的顺序，也就是解析顺序中第一次出现该路径的顺序。所以 top_paths 可能按该顺序。但测试case 7 中我们假设了 top_paths 顺序与 lines7 顺序一致。由于 lines7 中每个路径出现一次，所以 path_counts 插入顺序即为 lines7 顺序。但排序后如果 count 相同，将保持这个顺序。所以 test7 会通过。

但注意：如果同一路径出现多次，但插入是在第一次出现时，之后的出现不会改变插入顺序。所以 path_counts 中键的顺序是第一次出现的顺序。在排序中，同 count 时会保持第一次出现的相对顺序。所以合理。

2. parse_line 中 path 处理同时去除 query 和 fragment。

3. slow_data 中 duration 是整数，sorted key 使用 lambda x: x[0] 即 duration。若 duration 相同，稳定排序保留原顺序，即输入顺序。所以 slow_requests 在相同耗时情况下按输入顺序呈现（但要求按耗时降序，同耗时顺序无所谓）。所以没问题。

现在，测试函数中需要测试慢请求情况，验证顺序。

测试中，我们已经构建了 lines4，慢请求顺序：1200和1500。排序后 1500先，1200后。而且 lines4 中 slow3 在 slow1之前？slow1 是 index0 1200，slow3 index2 1500。排序后 1500出现先，所以 original_line 对应 index2，然后 index0。所以测试中我们检查顺序。

注意：lines4 列表顺序：slow1(1200),slow2(800),slow3(1500),slow4(900),fast1(100)。排序后 slow_requests 第一项应该是 slow3(1500)，第二项 slow1(1200)。所以测试应该断言。

之前测试代码中写：

```python
assert res4['slow_requests'][0]['duration'] == 1500
assert res4['slow_requests'][0]['path'] == '/path3'
assert res4['slow_requests'][0]['original_line'] == lines4[2]  # 'slow3 ...'
assert res4['slow_requests'][1]['duration'] == 1200
assert res4['slow_requests'][1]['path'] == '/path1'
```

注意：lines4[2] 是 slow3 那一行。lines4[0] 是 slow1。所以正确。

但注意：lines4 定义中：
```python
lines4 = [
    'slow1 GET /path1 200 1200ms tenant=t1',
    'slow2 GET /path2 200 800ms tenant=t1',
    'slow3 GET /path3 200 1500ms tenant=t1',
    'slow4 GET /path4 200 900ms tenant=t1',
    'fast1 GET /fast 200 100ms tenant=t2',
]
```
所以 indices 对应。

确认。

4. 在测试错误率时，需要 round(rate,3)。之前测试中 t1 错误率 1/3 = 0.3333333 -> 0.333。但 Python 中 round(0.3333333,3)=0.333，但 assert res5['tenant_error_rates']['t1'] == 0.333 比较浮点，可能会因为精度问题 assert 失败？实际上 0.333 在 Python 中也是 float，比较可能没问题。但可能存在细微差异，若 round返回的float与0.333的表示相同，应该相等。但最好用近似比较，如 assert abs(res5['tenant_error_rates']['t1'] - 0.333) < 1e-6。但使用 assertEqual 可能没问题，因为 0.333 和 round(1/3,3) 都表示相同的二进制小数（可能不完全一样但表示相同）。检查：round(1/3,3) 返回 0.333，而 0.333 字面量也是 0.333，两者比较通常 True。所以没问题。

但为了精确，可以使用 assertAlmostEqual。但不需要。

5. 可能需要测试 p95 计算整数版本边界：n=1,2,3 等。在 test6 基础上加一个测试：

```python
    # Test p95 for various n
    lines_p95 = ['GET /a 200 100ms tenant=t1', 'GET /a 200 200ms tenant=t1', 'GET /a 200 300ms tenant=t1']
    res_p95 = compute_stats(lines_p95)
    # n=3 => idx = (95*3+99)//100 -1 = (285+99)//100=384//100=3 -1=2 => sorted [100,200,300][2]=300
    assert res_p95['p95_latency_by_path']['/a'] == 300
    # two elements case: already tested in earlier examples (test6 had 5 elements)
    lines_p95_2 = ['GET /b 200 250ms tenant=t1', 'GET /b 200 150ms tenant=t1']
    res_p95_2 = compute_stats(lines_p95_2)
    assert res_p95_2['p95_latency_by_path']['/b'] == 250  # sorted [150,250] idx=(95*2+99)//100-1 = (190+99)//100=289//100=2-1=1 -> second element 250
```

我们可以在 test 中增加这些。

现在，开始整合为最终代码。

还要注意：代码中需要导入 json, sys, math, collections.defaultdict。但 math 只用于 ceil 之前，现在我们将 p95 改用整数运算，不再需要 math。可以去掉 math 导入。但可能有其他用途？没有，所以去掉 math。

但 math 模块是标准库，即使不导入也可以。我们不需要 math。所以移除 math 导入。

`from collections import defaultdict`

现在，代码。

现在，假设我们要输出 JSON，可以考虑使用 indent 或紧凑。为了方便测试时查看，可以输出带缩进的 JSON。但要求“只输出 JSON”，并未指定格式，所以我们可以输出带有缩进的 JSON，这也是 JSON。但通常脚本输出最好紧凑，便于其他程序处理。但测试时我们可自己看。使用默认 compact。但这里我们为了通用使用默认不缩进。

但也可以在 main 中加入 indent=2 如果希望可读？但可能不符合“输出 JSON 对象”的无额外说明？但 JSON 带缩进仍是 JSON。我倾向于使用缩进以便阅读。但最后决定输出 compact 或 indented? 一般题目中常默认 compact。但无妨。我们选择 `json.dumps(result, ensure_ascii=False, indent=2)` 输出更清晰。但注意：如果重定向到文件，缩进增加文件大小，但测试更方便。我们选择使用 indent=2。

如果题目希望紧凑，可能会用。但没明确。我认为都可以。我们使用 `json.dumps(result, ensure_ascii=False)` 即紧凑。但为了可读，测试时我们看。正式输出通常紧凑。所以我们使用紧凑。

但是，我们还需要考虑在测试阶段，使用 `--test` 会执行 test()，输出测试结果。而正常输出只有一个 JSON 字符串。所以 ok。

现在代码：

我将在下面写出完整代码，并通过 mind 检查。

最终代码需要仔细处理潜在异常输入导致崩溃，但我们已经用 try/except 转换数字。

注意：在 parse_line 中，如果 duration_str = "ms" 即没有数字，则 int("") 会 raise ValueError，返回 None。

还有，tenant 提取如果 tenant_field 是 "tenant="，则 split('=',1)[1] 得到空字符串，可以接受。

一切就绪。

现在，我们开始手写 final code。

注意：在 compute_stats 中，我们使用 `parsed['status']` 来检测错误，我们使用 `if 400 <= parsed['status'] <= 599:`。没问题。

现在，test() 函数中，需要保证使用正确的断言值。比如 test1 中 top_paths 顺序断言，我们已按插入顺序写。但注意 top_paths 结果取决于排序稳定，所以我们应该确认 path_counts 的插入顺序。lines1 中路径顺序：/api/orders, /api/users。所以断言正确。如果有其他路径出现，会按第一个出现顺序。

现在，test3 中 malformed_lines 计数：我们设计了 6 行，有效行 index2 和 index4（0-based）所以 malformed_lines=4。但需注意：我们的 parse_line 对于空行返回 None，所以增加 malformed。对于 "bad line without enough fields" 长度不够返回 None。对于 "invalid duration" 返回 None。对于 "invalidtenant" 返回 None。所以 malformed_lines = 4，有效=2。正确。p95 计算中 /api/orders 有两条记录：third line (index2) duration 123, fifth line (index4) duration 100。排序后 p95: sorted [100,123] n=2 idx=(190+99)//100-1=2-1=1 -> 123。所以断言正确。

但是注意：在 lines3 中，有效行是 index2 和 index4，两者都请求 /api/orders。所以 path_latencies['/api/orders'] 有两个值，所以 p95 正确。

但要注意：top_paths 只有 /api/orders，count=2。但我们没有断言 top_paths 的 count。

所以我们也可以添加检查。

可以加上 `assert res3['top_paths'][0]['path'] == '/api/orders'`。

好。

现在，test5 关于错误率：t1 有3个请求，错误一个，所以 rate=1/3≈0.333。round(0.333333,3)=0.333。t2 有一个请求，错误一个，所以 rate=1.0。

断言。

test7 中 top_paths 取前5，我们确认前5顺序。

test6 中 p95 为 500。

test p95 小 n 测试可能加在 test6 旁边。

现在，如果有 test9 空输入，确保 top_paths 空列表等。

现在，所有测试应该通过。

但是，我们还没有测试“去掉片段”功能，但可以省略。

现在，写所有代码。

注意，test() 函数内部不用 print 除非说明测试通过。但我们可以选择只 print 成功信息，这样在 --test 时会有输出。但要求“正常运行时只输出 JSON”，测试时输出文本没问题。

所以我们在 test() 中最后 print("All tests passed.")。

现在，检查是否漏了 import math? 我们不再需要，所以移除。

现在，确保代码不超过1000行，远远足够。

现在，写出最终程序。

我下面将写成一个完整代码，并逐步检查。

先写 parse_line：

```python
def parse_line(raw_line):
    stripped = raw_line.strip()
    if not stripped:
        return None
    parts = stripped.split()
    if len(parts) != 6:
        return None
    timestamp, method, raw_path, status_str, duration_str, tenant_field = parts
    try:
        status = int(status_str)
    except ValueError:
        return None
    if not duration_str.endswith('ms'):
        return None
    try:
        duration = int(duration_str[:-2])
    except ValueError:
        return None
    if not tenant_field.startswith('tenant='):
        return None
    tenant = tenant_field.split('=', 1)[1]
    # remove query parameters and fragment
    path = raw_path.split('?')[0].split('#')[0] if '?' in raw_path or '#' in raw_path else raw_path
    # simpler: always split and take first part:
    path = raw_path.split('?', 1)[0].split('#', 1)[0]
    return {
        'timestamp': timestamp,
        'method': method,
        'raw_path': raw_path,
        'path': path,
        'status': status,
        'duration': duration,
        'tenant': tenant,
        'original_line': raw_line,
    }
```

更简洁：path = raw_path.split('?', 1)[0].split('#', 1)[0]

如果 raw_path 没有 ? 或 #，split 返回单元素列表，index0 为自己。

使用 split('?',1)[0] 限制分割次数。

但注意：如果 raw_path 是 "/api/orders?page=2#section"，首先 split('?') [0] 得到 "/api/orders?page=2"? 不，如果同时有 #，先用 ? 分割，得到 "/api/orders" 和 "page=2#section"，然后 # 在第二部分，但我们只取第一部分，就失去了片段。但片段在路径后？实际上 URL 中片段在查询参数之后出现在末尾：/api/orders?page=2#section，所以 ? 之前是路径，后面是查询+片段。但有些 URL 可能片段在查询前？通常片段仅在路径后，查询或直接片段。但标准是 # 在 ? 后，或没有 ?。所以通过先 split('?') 取第一部分，如有 # 则仍在第一部分？但 # 很少出现在路径中，但可能在 ? 前？但合理做法是取 ? 之前的内容，且忽略 # 以及之后的内容，因为 # 表示片段，不是路径。但如果在 ? 之前出现 #（如 /api/orders#section?page=2），这非常规。所以我们可以用 split('?')[0].split('#')[0] 确保。但用 split('?',1)[0] 后，如有 # 在路径中，例如 /a#b?c，则 split('?')[0]= '/a#b'，再 split('#')[0] = '/a'。但这种情况极少，但处理了可能破坏正常 URL？但正常 URL 一般无 # 在路径中。所以我们保留 split('?')[0].split('#')[0] 是安全。

因此实现：path = raw_path.split('?', 1)[0].split('#', 1)[0]。

因为 raw_path 是字符串，直接用。

所以 parse_line 中 path = raw_path.split('?', 1)[0].split('#', 1)[0]。

现在，说明已经包含了去除 query parameters 和 fragment。

现在，compute_stats 中：

```python
    slow_data = []
    # 循环内解析
    # 循环后:
    # top_paths
    sorted_paths = sorted(path_counts.items(), key=lambda x: ( -x[1], x[0] ) ) # 按count降序，然后路径字母？但不需要，但可保持排序稳定
    # 但更简单使用 reverse=True，对于相同 count 顺序任意，我们接受。
    sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    # 但如果有相同 count，排序可能不确定，最好用 -count 然后 key 或其他。但为了确定性，可以指定第二排序 key 如路径，但题未要求。所以略。
```

我们继续保持。

p95_latency_by_path: 用整数索引。

tenant_error_rates: round(rate,3)

现在，最后 main。

在 test 中的代码需要注意：因为我们移除了 math 导入，现在不需要了。

现在，编写 test 函数。

我将在 test 函数中使用多个独立测试，并断言。

注意：针对慢请求测试，我们数组 lines4 中有5行，其中两个慢。我们已有的断言。

但现在，由于我们改为全收集 slow_data，然后排序，所以顺序不变。所以断言不变。

确保 lines4 中没有额外空格，所以 original_line 与 lines4 完全一致（因为 compute_stats 中 line.rstrip('\n')，但我们提供的 lines4 无换行，所以 original_line = 我们提供的行字符串，可以断言相等。

现在，我们可以编写 test()。

现在，确保所有测试 pass。

现在，我们可以编写一些额外的测试，如 fragment 去除：

```python
    lines_frag = ['GET /api/orders#section 200 100ms tenant=t1']
    res_frag = compute_stats(lines_frag)
    assert res_frag['p95_latency_by_path']['/api/orders'] == 100
```

但要注意，状态码 200 正常，所以路径绝佳。

可能 # 分割后得到 /api/orders。但 # 可能出现在路径中间？但极不常见。但测试可加。

考虑到代码简单，我们可以不测该情况。

现在，测试空输入。

已 test9。

现在，我们还要测试 slow_requests 超过10个的情况。

```python
    lines_slow_many = [f'GET /path 200 {i}ms tenant=t1' for i in range(1100, 1120)]  # 20 entries
    res_many = compute_stats(lines_slow_many)
    assert len(res_many['slow_requests']) == 10
    # durations should be 1119,1118,...,1110 (top 10) 但注意顺序：sorted descending，所以前10是最大的10个 i:1119 down to 1110。
    expected_durations = list(range(1119, 1109, -1))
    for idx, r in enumerate(res_many['slow_requests']):
        assert r['duration'] == expected_durations[idx], f"expected {expected_durations[idx]}, got {r['duration']}"
```

我们可以在 test 中加入。

确保 durations 正确。

注意：因为 slow_data 收集时 duration 就是 i，排序降序后，取前10，应该是最大的10个 i：1119,1118,1110? 实际上，range(1100,1120) 产生1100到1119（包括1100, 但1119最大，1110最小，前10是1119 down to 1110。所以 expected_durations 应为 range(1119, 1109, -1) 即 1119,1118,1117,1116,1115,1114,1113,1112,1111,1110。

所以断言。

这样覆盖。

我们还可以测试 slow_requests 小于10时全返回。

使用 lines4 有2个，返回2个。

已经包含。

现在，关于错误率，我们可以测试一个无错误的租户：rate=0.0

在 test1 中已测。

现在，测试 undefined tenant 的错误率: 因为没有请求，tenant_error_rates 不包括。所以 dict 没有该键，OK。

现在，注意：若一个租户所有请求都是错误，rate=1.0，round(1.0,3)=1.0，断言正确。

现在，所有内容完成。

最后，程序代码。

需要确保编码规范，速度等。

现在，写出最终代码。

我们按顺序写出。

```python
#!/usr/bin/env python3
import sys
import json
from collections import defaultdict

def parse_line(raw_line):
    """Parse a single log line, return dict or None if malformed."""
    stripped = raw_line.strip()
    if not stripped:
        return None
    parts = stripped.split()
    if len(parts) != 6:
        return None
    timestamp, method, raw_path, status_str, duration_str, tenant_field = parts
    # Validate status code
    try:
        status = int(status_str)
    except ValueError:
        return None
    # Validate duration (must end with 'ms')
    if not duration_str.endswith('ms'):
        return None
    try:
        duration = int(duration_str[:-2])
    except ValueError:
        return None
    # Validate tenant field
    if not tenant_field.startswith('tenant='):
        return None
    tenant = tenant_field.split('=', 1)[1]
    # Remove query parameters and fragment from path
    path = raw_path.split('?', 1)[0].split('#', 1)[0]
    return {
        'timestamp': timestamp,
        'method': method,
        'raw_path': raw_path,
        'path': path,
        'status': status,
        'duration': duration,
        'tenant': tenant,
        'original_line': raw_line
    }

def compute_stats(lines):
    """Read lines (iterable) and return stats dictionary."""
    total = 0
    malformed = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    tenant_total = defaultdict(int)
    tenant_errors = defaultdict(int)
    slow_data = []   # list of (duration, original_line, path)

    for line in lines:
        # Remove trailing newline only (do not strip other whitespace)
        raw_line = line.rstrip('\n')
        parsed = parse_line(raw_line)
        if parsed is None:
            malformed += 1
            continue
        total += 1
        # Status counts
        status_counts[str(parsed['status'])] += 1
        # Path (without query)
        path = parsed['path']
        path_counts[path] += 1
        # Latencies per path
        path_latencies[path].append(parsed['duration'])
        # Tenant
        tenant = parsed['tenant']
        tenant_total[tenant] += 1
        if 400 <= parsed['status'] <= 599:
            tenant_errors[tenant] += 1
        # Slow requests (duration > 1000)
        if parsed['duration'] > 1000:
            slow_data.append((parsed['duration'], parsed['original_line'], parsed['path']))

    # 1. Top 5 paths by request count
    sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths]

    # 2. P95 latency per path (integer milliseconds)
    p95_by_path = {}
    for path, latencies in path_latencies.items():
        if not latencies:
            continue
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        # Compute index = ceil(0.95 * n) - 1 (0‑based) using integer arithmetic
        idx = (95 * n + 99) // 100 - 1
        p95_by_path[path] = sorted_lat[idx]

    # 3. Top 10 slowest requests (>1000ms)
    slow_data.sort(key=lambda x: x[0], reverse=True)
    slow_requests = []
    for dur, line, path in slow_data[:10]:
        slow_requests.append({
            'original_line': line,
            'path': path,
            'duration': dur
        })

    # 4. Error rate per tenant (4xx/5xx)
    error_rates = {}
    for tenant, tot in tenant_total.items():
        err = tenant_errors.get(tenant, 0)
        rate = err / tot if tot > 0 else 0.0
        error_rates[tenant] = round(rate, 3)

    result = {
        'total_requests': total,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': error_rates,
        'malformed_lines': malformed
    }
    return result

def test():
    """Run built‑in tests."""
    # ---------- Test 1: basic ----------
    lines1 = [
        '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=b2',
    ]
    res1 = compute_stats(lines1)
    assert res1['total_requests'] == 2
    assert res1['status_counts'] == {'200': 1, '201': 1}
    assert len(res1['top_paths']) == 2
    assert res1['top_paths'][0] == {'path': '/api/orders', 'count': 1}
    assert res1['top_paths'][1] == {'path': '/api/users', 'count': 1}
    assert res1['p95_latency_by_path'] == {'/api/orders': 123, '/api/users': 456}
    assert res1['slow_requests'] == []
    assert res1['tenant_error_rates'] == {'a1': 0.0, 'b2': 0.0}
    assert res1['malformed_lines'] == 0

    # ---------- Test 2: query parameters removal ----------
    lines2 = [
        '2026-05-01T12:03:18Z GET /api/orders?page=2&sort=asc 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=a1',
    ]
    res2 = compute_stats(lines2)
    assert res2['p95_latency_by_path'] == {'/api/orders': 123, '/api/users': 456}
    assert res2['malformed_lines'] == 0

    # ---------- Test 3: malformed lines ----------
    lines3 = [
        '',
        'bad line without enough fields',
        '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z GET /api/orders 200 abcms tenant=a1',  # bad duration
        '2026-05-01T12:03:20Z GET /api/orders 200 100ms tenant=a1',  # valid
        '2026-05-01T12:03:21Z GET /api/orders 200 100ms invalidtenant', # bad tenant
    ]
    res3 = compute_stats(lines3)
    assert res3['total_requests'] == 2   # indices 2 and 4
    assert res3['malformed_lines'] == 4  # indices 0,1,3,5
    assert res3['p95_latency_by_path']['/api/orders'] == 123  # sorted (100,123) -> idx=1 -> 123
    # top_paths should contain one path
    assert len(res3['top_paths']) == 1
    assert res3['top_paths'][0]['path'] == '/api/orders'
    assert res3['top_paths'][0]['count'] == 2

    # ---------- Test 4: slow requests ----------
    lines4 = [
        'slow1 GET /path1 200 1200ms tenant=t1',
        'slow2 GET /path2 200 800ms tenant=t1',
        'slow3 GET /path3 200 1500ms tenant=t1',
        'slow4 GET /path4 200 900ms tenant=t1',
        'fast1 GET /fast 200 100ms tenant=t2',
    ]
    res4 = compute_stats(lines4)
    assert len(res4['slow_requests']) == 2
    assert res4['slow_requests'][0]['duration'] == 1500
    assert res4['slow_requests'][0]['path'] == '/path3'
    assert res4['slow_requests'][0]['original_line'] == lines4[2]
    assert res4['slow_requests'][1]['duration'] == 1200
    assert res4['slow_requests'][1]['path'] == '/path1'
    assert res4['slow_requests'][1]['original_line'] == lines4[0]

    # ---------- Test 5: error rates ----------
    lines5 = [
        'GET /a 200 100ms tenant=t1',
        'GET /b 404 50ms tenant=t1',
        'GET /c 500 200ms tenant=t2',
        'GET /d 300 150ms tenant=t1',  # 300 is not 4xx/5xx
    ]
    res5 = compute_stats(lines5)
    assert res5['tenant_error_rates']['t1'] == 0.333  # 1/3
    assert res5['tenant_error_rates']['t2'] == 1.0

    # ---------- Test 6: p95 multiple entries ----------
    lines6 = [f'GET /x 200 {i}ms tenant=t1' for i in [100,200,300,400,500]]
    res6 = compute_stats(lines6)
    assert res6['p95_latency_by_path']['/x'] == 500
    # additional p95 edge cases
    lines6b = ['GET /y 200 100ms tenant=t1', 'GET /y 200 200ms tenant=t1', 'GET /y 200 300ms tenant=t1']
    res6b = compute_stats(lines6b)
    assert res6b['p95_latency_by_path']['/y'] == 300
    lines6c = ['GET /z 200 250ms tenant=t1', 'GET /z 200 150ms tenant=t1']
    res6c = compute_stats(lines6c)
    assert res6c['p95_latency_by_path']['/z'] == 250

    # ---------- Test 7: top_paths limit 5 ----------
    paths7 = ['/api/orders', '/api/users', '/api/products', '/api/cart', '/api/checkout', '/api/admin']
    lines7 = [f'GET {p} 200 100ms tenant=t1' for p in paths7]  # each count=1
    res7 = compute_stats(lines7)
    assert len(res7['top_paths']) == 5
    # counts equal, order preserved from first occurrence
    expected_top5 = paths7[:5]
    for i, tp in enumerate(res7['top_paths']):
        assert tp['path'] == expected_top5[i]
        assert tp['count'] == 1

    # ---------- Test 8: status codes ----------
    lines8 = [
        'GET /a 201 100ms tenant=t1',
        'POST /b 404 50ms tenant=t1',
        'PUT /c 500 200ms tenant=t2',
        'DELETE /d 301 150ms tenant=t1',
    ]
    res8 = compute_stats(lines8)
    assert res8['status_counts'] == {'201': 1, '404': 1, '500': 1, '301': 1}
    assert res8['total_requests'] == 4

    # ---------- Test 9: empty input ----------
    lines9 = []
    res9 = compute_stats(lines9)
    assert res9['total_requests'] == 0
    assert res9['malformed_lines'] == 0
    assert res9['top_paths'] == []
    assert res9['p95_latency_by_path'] == {}
    assert res9['slow_requests'] == []
    assert res9['tenant_error_rates'] == {}

    # ---------- Test 10: many slow requests (top 10) ----------
    lines10 = [f'GET /path 200 {i}ms tenant=t1' for i in range(1100, 1120)]  # 20 entries
    res10 = compute_stats(lines10)
    assert len(res10['slow_requests']) == 10
    expected_durs = list(range(1119, 1109, -1))
    for i, sr in enumerate(res10['slow_requests']):
        assert sr['duration'] == expected_durs[i]

    # ---------- Test 11: fragment removal ----------
    lines11 = ['GET /api/orders#section 200 100ms tenant=t1']
    res11 = compute_stats(lines11)
    assert '/api/orders' in res11['p95_latency_by_path']

    print("All tests passed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test()
    else:
        result = compute_stats(sys.stdin)
        # Output compact JSON (no extra whitespace)
        print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

现在检查一下代码行数：大约160行左右，少于1000行。

注意：在 parse_line 中，我们使用了 path = raw_path.split('?', 1)[0].split('#', 1)[0]，但注意如果 raw_path 有编码问题无关。

现在，测试。

现在，考虑一个潜在的问题：在 test2 中，我们去除了查询参数，但我们断言 p95 包括 /api/orders 和 /api/users。实际上 lines2 第一条路径是 /api/orders?page=2&sort=asc，第二条是 /api/users。所以路径应为 /api/orders 和 /api/users。所以 p95_by_path 包含两个键。所以断言正确。

但在 test2 中，我们还应该检查 total_requests=2。但可以不放。

test3 中，我们检查了 malformed_lines=4，但注意：空行第1行，bad line第2行，duration abcms第4行，invalidtenant第6行，共4个malformed；有效第3行和第5行（索引2和4）。total_requests=2，正确。

test3 中，p95 和为 123 验证如上。

test5: 错误率计算：t1: three requests (200,404,300) -> 错误1个 -> 1/3 = 0.333，round to 0.333。t2: one request (500) 错误1个 -> 1.0。断言正确。

test6: p95 多种 edge，正确。

test7: 注意 top_paths 顺序：lines7 中路径顺序是 paths7，排序时按 count 降序，所有 count=1，所以保持原有顺序（因为 sort 稳定）。所以 top_paths 的顺序等于 paths7 的前5个。所以断言正确。

test10: 慢请求排序后前10应该是 i from 1119 down to 1110，代码中 slow_data 排序降序，再取前10，所以正确。注意输入顺序是 1100 到 1119。排序降序后变成 1119,1118,...。所以前10是 1119,...,1110。验证。

test11: fragment removal: 输入行带有 #section，path 应为 /api/orders，所以 p95 包含该键。

所有测试通过。

但还有一点：在 parse_line 中，我们假设 raw_line 可能包含 \r，使用 line.rstrip('\n') 后如果有 \r 保留，original_line 包含 \r。如果输入来自 Windows 系统，文本模式自动转换，所以 \r\n 转为 \n，所以 \r 不出现。所以没有问题。

现在，考虑 parse_line 中的 path 提取：使用 split('?',1)[0] 和 split('#',1)[0] 两种组合。如果路径同时包含 ? 和 #，先分割 ? 取第一部分（路径和可能的 # 片段），然后分割 # 取第一部分。但问题：如果 # 出现在 ? 之前（如 /api#orders?page=2），那么先 split('?',1)[0] 得到 /api#orders，然后 split('#',1)[0] 得到 /api。这是正确的，因为 # 在 ? 前，所以路径部分应该是 /api（忽略片段）。如果 # 在 ? 之后，如 /api/orders?page=2#s，则先 split('?',1)[0] 得到 /api/orders，后续 split('#',1)[0] 不变，是 /api/orders。所以正确。所以这种方式通用。

但是否有路径包含 ? 或 # 作为字符（转义）？通常不会，日志中路径是 URL 路径，? 和 # 有特殊含义。所以这样处理安全。

现在，测试中我们包含 # 的测试。

现在，我们可能要考虑状态码的可能范围：但只限定 4xx/5xx 错误。

现在，最终代码。

不过，我在编写时，注意到 p95_by_path 的计算中，整数公式 `idx = (95 * n + 99) // 100 - 1` 可能产生 idx 等于 n? 例如 n=100，计算 (95*100+99)//100 = (9500+99)//100=9599//100=95, -1=94 -> index 94 (0-based) 对应第95个元素（1-based）。正确。n=20，(1900+99)//100=1999//100=19, -1=18, index18 第19个元素？实际上 0.95*20=19，ceil=19，所以应是第19个，索引18，正确。n=1，(95+99)//100=1, -1=0，正确。n=2，(190+99)//100=2, -1=1，正确。

但 n=20 是 19.0? 没问题。

所以可以。

现在，确保在 n 较小如 n=1 时 idx=0，不会越界。

现在，可能要考虑 latencies 列表可能为空？已经检查。

现在，关于性能：sort 列表和排序。对于大量数据可能有一些延迟，但通常可接受。

现在，考虑使用 Python 的 json 模块输出浮点数时对于 float 的精度：我们输出 error_rates 中的 round(rate,3) 返回 float，json.dumps 会使用 repr 表示，可能产生 0.3330000000000001 之类的？但通常 round 返回的值是四舍五入后的近似值，但 repr 显示可能有多位。但 json.dumps 用默认的 float 编码，可能会输出 0.333 或 0.3330000000000001。在 Python 中，round(0.3333333,3)=0.333，其二进制表示并不精确是 0.333，但当你 print 0.333 时显示 0.333。json.dumps 也会显示 0.333。但可能某些情况下显示更多位数。但一般不会有大问题。但如果要求严格保留3位小数，可以使用 decimal 或手动格式化。但题目要求保留三位小数，可能只是值，不是格式。round 应该足够。

但举例：如果 rate=0.9999，round(0.9999,3)=1.0，json 输出 1.0。可能符合。

现在，整体代码完成。

但这版代码有一些潜在改进：

- 我们可以在 parse_line 中验证 timestamp 和 method 的格式? 不需要，跳过。

- 可以增加对 status_code 是否在 100-599 的校验。但额外校验可能增加 malformed。但可以不校，因为 int 转换成功即接受。但对于 status_str 为 "200abc" 会转换失败，所以加入 int 转换即可。

- 对于 duration_str，我们只要求以 'ms' 结尾并提取数字。所以 "123ms" 是基本，但 "123MS" 是否接受？原格式固定小写 "ms"，所以我们坚持小写。如果题目示例是 "123ms"，所以我们严格。

现在，可以执行测试。

最后，关于运行：程序应能被 python3 执行，并可从标准输入读取。测试时用 --test。

现在，准备提供最终代码。

但是要注意：在 compute_stats 中，我们使用了 `path = parsed['path']` 多次，实际上可以在解析后作为变量。

但已经 fine。

现在，考虑一个 corner case: 如果 top_paths 有多个路径，但计数为0？不可能。

现在，做最终检查。

可能还有个小错误：在 parse_line 中，return 的 dict 有 'raw_path' 键，但在 compute_stats 中未使用。保留无关。

现在，检查代码中的导入：已导入 sys, json, defaultdict。不需要其他。

现在，测试一条标准输入：

```bash
echo -e '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1\n2026-05-01T12:03:19Z GET /api/orders?page=2 200 456ms tenant=b2' | python3 log_analyzer.py
```

应输出 JSON，包含 total_requests=2，path 两个都对应于 /api/orders，p95 计算正确等。

我们现在快速手动测试思路。

现在，我决定看一下代码并调整 test 中的一个小细节：p95_by_path 中，我们计算 idx 时，对于 n=0 不会进入，所以 continue。

但注意：如果 path 有 latencies 但 n>0，但 idx 在 n 很小时可能出错？已检查。

现在，需要确保在 test() 中如果该路径仅有1个条目，p95 取其自身。已有测试 lines6c 是2个条目，做了断言；但我们没有1个条目的测试。在 test1 中 /api/users 只有一个条目，所以 p95 = 456。所以涵盖。

所以测试覆盖。

现在，test 中的 test5 错误率计算使用了 round(rate,3)，比较时可能因为浮点。但我们已经测试。

现在，确保在 test 中断言用 == 对浮点比较，可能因为表示问题 false。但通常 round(1/3,3) 和 0.333 比较，由于 0.333 也是 float 字面，它们应相等（都是 0.333 的表示）。实际上，在 Python 中 0.333 是 0.333，round(0.3333333,3) 产生相同的二进制？可能不是完全一致，但值自洽吗？我们做一个测试：在 Python 中 `round(1/3,3) == 0.333` 返回 False？实际上，若计算 `round(1/3,3) == 0.333`，我猜可能 True? 让我思考：1/3 = 0.3333333333333333，round 后变为 0.333（实际上 0.333 有具体二进制近似值，round 后的值和直接 0.333 字面值会是一样的，因为 round 返回的浮点数和字面量 0.333 都是在 IEEE 754 中最接近 0.333 的表示，应该相同）。但我不能完全确定。为了稳妥，可以改用近似比较如 `assert abs(res5['tenant_error_rates']['t1'] - 0.333) < 1e-5`。或者将 0.333 改为字符串比较？不过我们可以容忍。但为了测试更加健壮，我们可以使用 `assert round(1/3,3) == 0.333` 这种方式。我认为应该没问题，因为 Python 中 0.333 的含义就是最接近的浮点数，而 round(1/3,3) 也得到最接近的浮点数，所以它们相等。但为了绝对可靠，我改为比较四舍五入后的字符串：`assert f"{res5['tenant_error_rates']['t1']:.3f}" == "0.333"` 但这是字符串比较。但没必要。我们信任 Python。不过，在测试中，可以明确使用 `assert abs(res5['tenant_error_rates']['t1'] - 0.333) < 1e-6` 以避免潜在的浮点误差。

我们可以修改 test5 为近似比较。但代码中我们使用 `assert res5['tenant_error_rates']['t1'] == 0.333`，可以保留。如果发现错误再修改。不过总的来看，许多 Python 测试框架使用 assertEqual 对浮点。但为了避免麻烦，我们可以使用 `assert round(1/3, 3) == 0.333` 这一表达式本身就是 True，因为 Python 会字面量。

但为了谨慎，我们使用 approx。但简单起见，保留原样。

如果运行测试时遇到断言错误，可以调整。

另一个地方：在 test10 中检查 duration 整数，没问题。

现在，我们还需要考虑 malformed_lines 计数时，空行和纯空格行是否计入？我们的 parse_line 对 stripped 空返回 None，所以计入。这合理。

现在，代码完成。

注意：有没有可能某个字段包含空格？如路径包含空格？通常不会，但如果出现，我们的 split 会多出字段，导致 len != 6，被标记为 malformed。所以这些行被跳过，符合预期。

现在，最终输出 JSON，我们使用了 `print(json.dumps(result, ensure_ascii=False))` 这是紧凑输出。可以。

然后，如果使用 `--test` 则运行 test。

现在，我们还可以增强 test() 函数：如果断言失败，打印有用信息。但 assert 会显示行并退出。可以在每个测试用例后打印 pass 等。但为了简洁，我们只最后打印成功。

现在，我们确保代码可以独立运行。

现在，考虑代码是否符合“单文件命令行程序”，是的。

现在，最终检查所有要求：

- 从标准输入读取多行访问日志 —— 是（sys.stdin）
- 每行格式按要求解析
- 输出 JSON 对象包含所有要求字段：
   - total_requests
   - status_counts
   - top_paths
   - p95_latency_by_path
   - slow_requests
   - tenant_error_rates
- 跳过无法解析行，输出 malformed_lines 数量
- 查询参数去掉
- p95 定义为排序后向上取整位置（我们用整数实现）
- 慢请求前10按耗时降序
- 错误率 4xx/5xx 算错误，保留三位小数
- 代码结构清晰，包含内置测试函数，`--test` 参数运行测试
- 正常只输出 JSON 不输出解释文字
- 代码不超过1000行
- 不使用第三方库

都满足了。

但是有一个小点：p95 的定义中“向上取整位置”具体实现为 ceil(0.95 * n)，我们使用整数运算。但我们也需要确认排序后取哪个元素。确保我们的索引计算正确。我们使用了 (95 * n + 99) // 100 - 1。这对应 ceil(0.95 * n) - 1（0-based）。等价。所以正确。

另一个要求: top_paths: 请求量最高的前5个路径，含 path 和 count。我们使用 sorted_paths[:5]，如果少于5个，所有都返回，正确。

另外，slow_requests 保留原始行，我们保存了原始行（不带换行）。符合要求。

tenant_error_rates 保留三位小数，我们使用 round。正确。

现在，测试时应涵盖这些。

现在，我考虑函数 parse_line 中对于 status 我们只转 int，但可能状态码是字符串如 "200"，"404"等。对于 "200a" 会转换失败，所以 malformed。但如果出现 "200" 是正确。如果出现 " 200 " 由于 stripped 已经 strip，且 split 分割后得到 "200"，固定。所以不会出现前后空格。

现在，对于耗时一样。

暂时认为代码正确。

现在，如果我们要让程序同时支持 `--test` 和参数如 `--help` 等，但题目只要求 `--test`，所以我们忽略。

最后，可能需要考虑 JSON 输出中键的顺序如要求所示。我们的 order 为: total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines。按照要求中的顺序。没问题。

但并在要求中 malformed_lines 出现在最后，已最末。

现在，代码写好了。

但是，我们是否可以改进 test() 使其更贴近 unittest? 不必须。

现在，提供最终代码。

在输出原始行时，我们保留了 `original_line` 字段。注意，如果原始行包含不可见字符，比如行尾空格，我们的 parse_line 中 raw_line 是 line.rstrip('\n')，所以保留原行包括空格。但 stripped 用于解析会忽略空格，但原始行保留。可能 original_line 包含头尾空格，这符合“保留原始行”。所以好。

现在，我注意到在 compute_stats 中，我们使用了 `line.rstrip('\n')` 但未处理 `\r`，但文本模式下已经转换，所以没问题。

现在，全部完成。

最后，确认代码无语法错误。

可以快速模拟运行 test() 吗？

在头脑里过一下 test1:
- lines1 = [...]
- 对每条调用 parse_line
  - line0: parse_line 后返回字典，字段: path => /api/orders, duration=123, status=200, tenant='a1', original_line=line0
  - line1: path => /api/users, duration=456, status=201, tenant='b2'
- total=2, malformed=0
- status_counts: '200':1,'201':1
- path_counts: /api/orders:1, /api/users:1
- path_latencies: [...] -> for p95: /api/orders: lat=[123], n=1, idx=(95+99)//100-1 = (194)//100-1=1-1=0 -> 123; /api/users:456
- slow_data empty
- tenant_total: a1:1,b2:1; tenant_errors: none
- top_paths: sorted by count reverse: both 1, stable order so /api/orders before /api/users -> ok
- error_rates: a1 0.0, b2 0.0
- result ok

所以 test1 通过。

其他测试也可以。

现在，我开始写最终答案。

注意，代码中包含中文注释？可以用英文注释。但要求无所谓。我用中文注释。但为了通用，可以用英文。但随意。

现在，最终输出。

注意：代码应该保存为 log_analyzer.py。我们只需要给出代码本身。

现在，渲染代码框。

代码行数在200行以内，完全满足。

最后，检查是否有遗漏。

- 我们使用 defaultdict 但需要导入。已导入。

- 我们没有使用 math，所以删除 import math。

- 我们使用了 `if __name__ == '__main__'`，但主函数 main 在定义后。

现在，最终。

注意：测试时如果路径中包含 `#`，我们做了分割。test11 已经测试。

现在，代码完成。

我将在最终回答中提供该代码。

但是，我注意到在 test5 中，`assert res5['tenant_error_rates']['t1'] == 0.333` 可能因浮动失败，我决定改为比较与 1/3 round 的结果：`assert res5['tenant_error_rates']['t1'] == round(1/3, 3)`。这样更准确的表达。同样，t2 为 1.0。我们将 test5 修改：

`assert res5['tenant_error_rates']['t1'] == round(1/3, 3)`

但 round(1/3,3) 的结果是 0.333，但或许 test 语义更清晰。但原来 0.333 也是可以的。但我们可以保持。

但为更稳妥，我改为使用近似比较：

`assert abs(res5['tenant_error_rates']['t1'] - 1/3) < 1e-3`，但这里 1/3 本身是近似值。不过我们可以不用在意。

实际上，我们可以直接比较字符串格式化？没必要。

我在测试中将保持原状，但如果担心，可以使用 decimal。但相信 Python。

不过，在 test5 中，我们也可以直接使用 `assert round(1/3, 3) == 0.333`，但我们使用的计算结果是 round(1/3, 3) 即 0.333，所以两者本质上比较同样两个 float，应该相等。

我将坚持原测试。

最后，一个可能疏忽：在 parse_line 中，我们使用了 `path = raw_path.split('?', 1)[0].split('#', 1)[0]`，但如果 raw_path 只包含 '?' 或 '#' 之一，仍能正确 split。但注意 raw_path 可能为空？但日志路径通常不会是空。如果 raw_path 为空（可能），split 会得到 ['']，处理也为空。但应该不会。

另一个极端：路径可能包含百分号编码，但不影响。

现在，最终代码。

我将会提供。
````

## Assistant

````markdown
```python
#!/usr/bin/env python3
import sys
import json
from collections import defaultdict

def parse_line(raw_line):
    """Parse a single log line.  Return a dict with fields or None if malformed."""
    stripped = raw_line.strip()
    if not stripped:                     # empty line
        return None

    parts = stripped.split()
    if len(parts) != 6:                  # wrong number of columns
        return None

    timestamp, method, raw_path, status_str, duration_str, tenant_field = parts

    # status code must be integer
    try:
        status = int(status_str)
    except ValueError:
        return None

    # duration must end with "ms"
    if not duration_str.endswith('ms'):
        return None
    try:
        duration = int(duration_str[:-2])
    except ValueError:
        return None

    # tenant must be of the form "tenant=..."
    if not tenant_field.startswith('tenant='):
        return None
    tenant = tenant_field.split('=', 1)[1]

    # remove query parameters and fragment from the path
    path = raw_path.split('?', 1)[0].split('#', 1)[0]

    return {
        'timestamp': timestamp,
        'method': method,
        'raw_path': raw_path,
        'path': path,
        'status': status,
        'duration': duration,
        'tenant': tenant,
        'original_line': raw_line
    }


def compute_stats(lines):
    """Read log lines (iterable) and compute the required statistics.

    Returns a dictionary with all the fields required by the problem.
    """
    total = 0
    malformed = 0
    status_counts = defaultdict(int)
    path_counts = defaultdict(int)
    path_latencies = defaultdict(list)
    tenant_total = defaultdict(int)
    tenant_errors = defaultdict(int)
    slow_data = []                     # (duration, original_line, path)

    for line in lines:
        raw_line = line.rstrip('\n')
        parsed = parse_line(raw_line)
        if parsed is None:
            malformed += 1
            continue

        total += 1

        # status
        status_counts[str(parsed['status'])] += 1

        # path (without query/fragment)
        path = parsed['path']
        path_counts[path] += 1
        path_latencies[path].append(parsed['duration'])

        # tenant
        tenant = parsed['tenant']
        tenant_total[tenant] += 1
        if 400 <= parsed['status'] <= 599:       # 4xx or 5xx -> error
            tenant_errors[tenant] += 1

        # slow requests (duration > 1000ms)
        if parsed['duration'] > 1000:
            slow_data.append((parsed['duration'], parsed['original_line'], parsed['path']))

    # 1) Top 5 paths
    sorted_paths = sorted(path_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_paths = [{'path': p, 'count': c} for p, c in sorted_paths]

    # 2) P95 latency per path (integer milliseconds)
    p95_by_path = {}
    for path, latencies in path_latencies.items():
        if not latencies:
            continue
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        # index = ceil(0.95 * n) - 1  (0‑based) with integer arithmetic
        idx = (95 * n + 99) // 100 - 1
        p95_by_path[path] = sorted_lat[idx]

    # 3) Top 10 slow requests
    slow_data.sort(key=lambda x: x[0], reverse=True)
    slow_requests = []
    for dur, line, path in slow_data[:10]:
        slow_requests.append({
            'original_line': line,
            'path': path,
            'duration': dur
        })

    # 4) Error rate per tenant
    error_rates = {}
    for tenant, tot in tenant_total.items():
        err = tenant_errors.get(tenant, 0)
        rate = err / tot if tot > 0 else 0.0
        error_rates[tenant] = round(rate, 3)

    result = {
        'total_requests': total,
        'status_counts': dict(status_counts),
        'top_paths': top_paths,
        'p95_latency_by_path': p95_by_path,
        'slow_requests': slow_requests,
        'tenant_error_rates': error_rates,
        'malformed_lines': malformed
    }
    return result


def test():
    """Built‑in tests.  Run with --test ."""
    # ------------------------------------------------------------------
    # Test 1 : basic correct input
    lines1 = [
        '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=b2',
    ]
    res1 = compute_stats(lines1)
    assert res1['total_requests'] == 2
    assert res1['status_counts'] == {'200': 1, '201': 1}
    assert len(res1['top_paths']) == 2
    assert res1['top_paths'][0] == {'path': '/api/orders', 'count': 1}
    assert res1['top_paths'][1] == {'path': '/api/users', 'count': 1}
    assert res1['p95_latency_by_path'] == {'/api/orders': 123, '/api/users': 456}
    assert res1['slow_requests'] == []
    assert res1['tenant_error_rates'] == {'a1': 0.0, 'b2': 0.0}
    assert res1['malformed_lines'] == 0

    # ------------------------------------------------------------------
    # Test 2 : query parameters removal
    lines2 = [
        '2026-05-01T12:03:18Z GET /api/orders?page=2&sort=asc 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z POST /api/users 201 456ms tenant=a1',
    ]
    res2 = compute_stats(lines2)
    assert res2['total_requests'] == 2
    assert res2['p95_latency_by_path'] == {'/api/orders': 123, '/api/users': 456}
    assert res2['malformed_lines'] == 0

    # ------------------------------------------------------------------
    # Test 3 : malformed lines
    lines3 = [
        '',
        'bad line without enough fields',
        '2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1',
        '2026-05-01T12:03:19Z GET /api/orders 200 abcms tenant=a1',      # bad duration
        '2026-05-01T12:03:20Z GET /api/orders 200 100ms tenant=a1',      # valid
        '2026-05-01T12:03:21Z GET /api/orders 200 100ms invalidtenant',  # bad tenant
    ]
    res3 = compute_stats(lines3)
    assert res3['total_requests'] == 2          # indices 2 and 4
    assert res3['malformed_lines'] == 4         # indices 0,1,3,5
    assert res3['p95_latency_by_path']['/api/orders'] == 123   # sorted [100,123] -> idx=1
    assert len(res3['top_paths']) == 1
    assert res3['top_paths'][0]['path'] == '/api/orders'
    assert res3['top_paths'][0]['count'] == 2

    # ------------------------------------------------------------------
    # Test 4 : slow requests order and limits
    lines4 = [
        'slow1 GET /path1 200 1200ms tenant=t1',
        'slow2 GET /path2 200 800ms tenant=t1',
        'slow3 GET /path3 200 1500ms tenant=t1',
        'slow4 GET /path4 200 900ms tenant=t1',
        'fast1 GET /fast 200 100ms tenant=t2',
    ]
    res4 = compute_stats(lines4)
    assert len(res4['slow_requests']) == 2
    assert res4['slow_requests'][0]['duration'] == 1500
    assert res4['slow_requests'][0]['path'] == '/path3'
    assert res4['slow_requests'][0]['original_line'] == lines4[2]
    assert res4['slow_requests'][1]['duration'] == 1200
    assert res4['slow_requests'][1]['path'] == '/path1'
    assert res4['slow_requests'][1]['original_line'] == lines4[0]

    # ------------------------------------------------------------------
    # Test 5 : error rates (4xx/5xx)
    lines5 = [
        'GET /a 200 100ms tenant=t1',
        'GET /b 404 50ms  tenant=t1',
        'GET /c 500 200ms tenant=t2',
        'GET /d 300 150ms tenant=t1',          # 300 is not an error
    ]
    res5 = compute_stats(lines5)
    assert res5['tenant_error_rates']['t1'] == 0.333   # 1/3 ≈ 0.333
    assert res5['tenant_error_rates']['t2'] == 1.0

    # ------------------------------------------------------------------
    # Test 6 : P95 computation (integer arithmetic)
    lines6a = [f'GET /x 200 {i}ms tenant=t1' for i in [100,200,300,400,500]]
    res6a = compute_stats(lines6a)
    assert res6a['p95_latency_by_path']['/x'] == 500

    lines6b = ['GET /y 200 100ms tenant=t1', 'GET /y 200 200ms tenant=t1', 'GET /y 200 300ms tenant=t1']
    res6b = compute_stats(lines6b)
    assert res6b['p95_latency_by_path']['/y'] == 300

    lines6c = ['GET /z 200 250ms tenant=t1', 'GET /z 200 150ms tenant=t1']
    res6c = compute_stats(lines6c)
    assert res6c['p95_latency_by_path']['/z'] == 250

    # ------------------------------------------------------------------
    # Test 7 : top_paths limit to 5
    paths7 = ['/api/orders', '/api/users', '/api/products', '/api/cart', '/api/checkout', '/api/admin']
    lines7 = [f'GET {p} 200 100ms tenant=t1' for p in paths7]
    res7 = compute_stats(lines7)
    assert len(res7['top_paths']) == 5
    # all counts are 1, order is insertion order (stable sort)
    for i, tp in enumerate(res7['top_paths']):
        assert tp['path'] == paths7[i]
        assert tp['count'] == 1

    # ------------------------------------------------------------------
    # Test 8 : status code recording
    lines8 = [
        'GET /a 201 100ms tenant=t1',
        'POST /b 404 50ms tenant=t1',
        'PUT /c 500 200ms tenant=t2',
        'DELETE /d 301 150ms tenant=t1',
    ]
    res8 = compute_stats(lines8)
    assert res8['status_counts'] == {'201': 1, '404': 1, '500': 1, '301': 1}
    assert res8['total_requests'] == 4

    # ------------------------------------------------------------------
    # Test 9 : empty input
    lines9 = []
    res9 = compute_stats(lines9)
    assert res9['total_requests'] == 0
    assert res9['malformed_lines'] == 0
    assert res9['top_paths'] == []
    assert res9['p95_latency_by_path'] == {}
    assert res9['slow_requests'] == []
    assert res9['tenant_error_rates'] == {}

    # ------------------------------------------------------------------
    # Test 10 : many slow requests (top 10)
    lines10 = [f'GET /path 200 {i}ms tenant=t1' for i in range(1100, 1120)]   # 20 entries
    res10 = compute_stats(lines10)
    assert len(res10['slow_requests']) == 10
    expected_durations = list(range(1119, 1109, -1))
    for i, sr in enumerate(res10['slow_requests']):
        assert sr['duration'] == expected_durations[i]

    # ------------------------------------------------------------------
    # Test 11 : fragment removal (#)
    lines11 = ['GET /api/orders#section 200 100ms tenant=t1']
    res11 = compute_stats(lines11)
    assert '/api/orders' in res11['p95_latency_by_path']

    print("All tests passed.")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test()
    else:
        result = compute_stats(sys.stdin)
        # output compact JSON
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
```
````
