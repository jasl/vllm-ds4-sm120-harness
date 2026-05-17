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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 275.458346
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 417, "total_tokens": 27464, "completion_tokens": 27047, "prompt_tokens_details": null}`
- Prompt tokens: 417
- Completion tokens: 27047
- Total tokens: 27464

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
我们被要求用Python编写一个单文件命令行程序，分析访问日志。输入从标准输入读取，输出JSON对象。要求包括：total_requests, status_counts, top_paths, p95_latency_by_path, slow_requests, tenant_error_rates, malformed_lines。需要跳过无法解析的行。我们必须输出JSON，不输出解释文字。有--test参数运行测试。

我们需要处理数据，统计各种信息。

首先定义解析函数，读取一行，按空格分割字段，验证字段数（应为6？还是可能包含更多？看格式：字段依次为：ISO时间、HTTP方法、路径、状态码、耗时毫秒、租户。所以应该是6个字段，分割后应该有6部分。但路径可能包含空格？应该不会。所以用空格分割。

但注意：路径可能包含查询参数，如`/api/orders?page=2`，统计时应去掉查询参数。所以我们解析后需要规范化路径：去掉查询参数部分（即去除`?`及之后的内容）。

字段：datetime, method, path, status_code, latency_str, tenant.

验证datetime是否符合ISO格式？可以粗略验证长度或包含'T'等。或者我们直接校验是否可以提取所有字段。考虑到简单起见，我们使用str.split()取前6个元素，如果少于6则算malformed。可能路径中也有空格？但通常不会。如果有更多字段，可能是路径中有空格？那可能更难。但按规范，应该没有。我们假设简单分割。

然后转换状态码为整数，验证是否为数字。耗时毫秒形如123ms，去掉ms部分转为整数。租户形如tenant=a1，提取等号后面的部分。可能租户格式是固定的"tenant=xxx"，但也可以解析。

对于无法解析的行，计数为malformed_lines。

然后根据需求计算统计：

- total_requests: 总的有效行数（不包括malformed）。
- status_counts: 字典，状态码->出现次数。
- top_paths: 根据路径（去掉查询参数）出现的频率排序，输出前5个（path, count）。
- p95_latency_by_path: 每个路径的p95耗时，毫秒整数。需要收集每个路径下的所有耗时，排序后计算p95。p95定义为排序后向上取整位置。假设有N个请求，p95索引 = ceil(0.95 * N)，从1开始计数，或0-based? 通常p95：排序后取第ceil(0.95 * N)个值（1-based）。例如N=100, 0.95*100=95，取第95个（从1开始）。若N=99, 0.95*99=94.05，向上取整为95，取第95个（1-based）。所以索引 = int(math.ceil(0.95 * n)) - 1 (0-based)。
- slow_requests: 耗时>1000ms的前10条，按耗时降序。需要保留原始行、路径、耗时。原始行就是输入的完整行（但要去掉查询参数？要求保留原始行？说明是保留原始行、路径、耗时。"保留原始行、路径、耗时"可能指在输出中包含original_line, path, latency。但path可能已经是去掉参数的了？原始行就是输入行，path是从解析后的path去掉参数后的。所以我们需要为每个慢请求存储原始行（input_line）和规范化后的路径及latency。
- tenant_error_rates: 每个租户的错误率（4xx/5xx视为错误）。错误率 = 错误请求数 / 总请求数（该租户）。保留三位小数。可能需要计算每个租户的总请求数和错误数。

注意：慢请求需要从所有有效请求中筛选。top_paths基于有效请求。p95_by_path也基于有效请求。

另外，需要注意效率？数据可能较大，但这里只要求单次处理。

实现思路：逐行读取stdin，对于每一行，进行解析，如果格式错误就增加malformed计数并跳过。有效则添加到数据结构中。

数据结构：

- total_requests: 计数器
- status_counts: collections.Counter 或普通字典
- path_counts: Counter 统计每个规范化路径的出现次数
- path_latencies: dict of list 每个路径下所有耗时列表（用于p95）
- tenant_errors: dict of dict 或两个字典：tenant_total, tenant_error

但注意：错误率基于每个租户，所以我们需要记录每个租户的总请求数和错误请求数（状态码>=400）。

- slow_requests: 列表，存储每个慢请求的元组（latency, original_line, path）。在遍历时检查latency>1000则插入，最后排序取出前10。

但数据量大时，慢请求列表可能很大，但我们只需要前10，所以可以用堆来保持top10，但简单起见直接收集所有，最后排序取前10，只要数据量不是天文数字，应该可以。题目没有限制行数，但我们尽量考虑性能。不过1000行代码内，简单处理即可。

确保输出JSON格式规范，使用json.dumps。

需要包含内置测试函数：当使用`--test`参数时，执行测试。测试可以用一些样本数据验证输出是否符合预期。

注意：不应当使用第三方库，使用标准库（sys, json, math, collections等）。

代码结构：定义函数：parse_line(line), main()。if __name__ == "__main__": 判断sys.argv是否包含--test，若包含则运行测试函数，否则运行主逻辑。

测试函数：可以构造一些输入，模拟stdin输入，然后捕获输出，验证JSON字段。可使用unittest或简单断言。

需要确保在测试时，不会因为从stdin读取而阻塞？测试时可使用io.StringIO模拟输入。

另外，输出JSON时使用的ensure_ascii=False？中文或无要求，但路径可能是英文。保持默认即可。

关于字段名：`p95_latency_by_path`是按路径对象列表还是字典？根据描述，应该是一个对象，键为路径，值为p95整数值。可以是JSON对象。但在JSON中，路径可能包含特殊字符，但作为键没问题。

top_paths：请求量最高的前5个路径，含path和count。所以应该是数组，每个元素是对象`{"path": "...", "count": N}`。如果路径有多个相同的，取出现次数最多的前5个。如果不足5个，则全部输出。

slow_requests：数组，每个元素包含original_line, path, latency (int)。按latency降序取前10。

tenant_error_rates：对象，键为租户值，值为错误率（浮点数，保留三位小数）。如果某个租户没有错误，错误率为0.000。

malformed_lines：直接整数。

p95_latency_by_path：对象，键为路径，值为整数p95。如果某路径没有数据（不可能，因为只有有请求才会记录），如果路径请求数很少，例如只有1个，p95就是那个值。

同时注意：路径需要去掉查询参数。如何去掉？如果路径中包含?，则取?之前的部分。如果包含?但没有参数？也去掉。当然路径可能没有?，则保持原样。

时间格式：ISO时间，但我们不需要解析时间，只需原样保留原始行用于慢请求，不用于其他统计。

关于耗时：格式是数字ms。可能还有ms以外的？规格说明是毫秒整数。耗时可能是"123ms"这种。解析时去掉末尾"ms"。如果不符合，可能算malformed。注意：可能包含小数？规格说毫秒整数，所以我们期望是整数ms。我们取数字部分。

状态码：三位数字。整数。

方法：GET/POST等，不需要使用。

租户格式：tenant=a1。也可能有空格？假设如此。我们通过等号分割，取第二部分。

注意：一行可能存在多个空格分隔，我们使用split()即可。

细分malformed条件：split后长度少于6，或状态码不是数字，或耗时不是数字，或租户不以"tenant="开头？如果不以tenant=开头，是否算错误？题目说明格式为"租户"，可能格式总是tenant=xxx。但可能不规范。我们容忍租户字段可能没有等号？根据说明 "tenant=a1" 是示例，但可能其他租户也可能不含tenant=？我们严格按格式，如果不包含tenant=，也可以当作租户值？但最好按格式解析。题目要求跳过无法解析的行。我们如果租户字段没有等号，我们可以将其本身作为租户值？但可能会错误。稳妥起见，我们假设格式正确，如果不正确则算malformed。或者宽松处理：取租户字段作为字符串，如果包含=，取=后部分；否则整个作为租户值。我们选择更健壮的方式：取第一个等号后面的值，如果没有等号，则整个作为租户（也许能适应）。但为了明确，我决定：租户字段应该以"tenant="开头，否则算malformed。但题目要求跳过无法解析的行，租户格式不对也算无法解析。所以可以这样做。但为了测试方便，可以宽松。

我们再看要求："字段依次为：ISO时间、HTTP方法、路径、状态码、耗时毫秒、租户。" 所以第六部分就是租户，格式按示例是"tenant=a1"，但理论上租户可以是其他标识符，可能统一前缀？我觉得为了简单，我们就取整个第六字段作为租户值，而不解析等号。这样，如果租户是"abc"，则租户值是"abc"。如果租户是"tenant=abc"，则租户值是"tenant=abc"（因为未解析）但示例期望提取a1。所以最好按示例提取。所以还是解析等号后的内容比较好。为了通用，我们可以假设租户字段是"key=value"形式，但key不重要，我们取value。如果包含多个等号，取第一个等号后的所有内容。如果没有等号，则整个字段作为租户？我们灵活处理：如果包含等号，取第一个等号后部分作为租户；否则整个字段作为租户。这样可同时支持两种。但要注意，如果租户字段本身就包含等号，可能不是tenant=xxx？但格式应该一致。为了测试，我们按示例提取。

还有，状态码和耗时可能是字符串，需要转换。如果转换失败，跳过该行。

所以malformed条件：

- split后元素不足6个
- 状态码不能被int转换（不是数字）
- 耗时不是数字（去掉ms后不是数字）
- 其他？比如时间格式不对，但我们不强制验证，因为时间字段我们只原样保留在original_line中，但如果我们不验证，可能也会出现无效时间，但不对时间做处理，所以可以不验证。为了安全，可以验证时间是否包含T或日期格式等，但可以跳过。

总结，有效请求定义为满足上述条件的行。

统计：

1. total_requests = 有效请求数。

2. status_counts: 字典（可以使用Counter，然后转dict）

3. top_paths: 根据路径出现的频数降序，取前5。如果有并列，顺序无所谓，但需要一致。我们可以排序时指定先按count降序，再按路径字母升序（可选）。但按题目要求，只要取前5即可。

4. p95_latency_by_path: 对于每个路径，收集所有耗时列表。然后排序，计算p95。注意如果列表空则不会有，但只要有请求就至少有一个。计算索引：N = len(list)，index = ceil(0.95 * N) - 1。如果N=0，忽略。需要整数毫秒，即latency本身是整数（从解析得到）。

5. slow_requests: 收集所有latency>1000的请求（原始行，规范化路径，latency）。然后按latency降序排序，取前10。如果不足10，则全取。

6. tenant_error_rates: 每个租户的总请求数和4xx/5xx的请求数。错误包括状态码>=400且<600? 4xx和5xx，即400-599。注意可能6xx？但标准http状态码中4xx和5xx。所以我们判断status >= 400 and status < 600。实际上如果status>=400都算错误？如果出现600？不太可能。我们使用status >= 400。但严格说只有4xx和5xx，所以status >= 400 and status < 600。但万一出现其他错误，也可算。我们简化：status >= 400。错误率 = 错误请求数 / 总请求数（该租户）。保留三位小数。使用round(x, 3)或format。注意浮点数精度，要用Decimal? 但保留三位直接round即可。

输出JSON时，需要保证数据格式正确。例如p95_latency_by_path是对象。top_paths是数组。等等。

输出只打印JSON，没有其他文本。

现在，设计代码。

导入模块：sys, json, math, collections（Counter, defaultdict）

parse_line(line)函数返回一个tuple或None如果解析失败。

可定义namedtuple？但简单，返回解析后的字段：timestamp, method, path, status, latency, tenant, original_line。

但路径需要去掉查询参数：调用path.split('?')[0]即得到无参数路径。

对于慢请求，需要original_line, path, latency。

我们存储原始行，用于slow_requests。

处理过程：

```python
def parse_line(line):
    parts = line.strip().split()
    if len(parts) < 6:
        return None
    timestamp, method, path, status_str, latency_str, tenant_str = parts[:6]
    # 可能路径包含空格？但split后可能把路径拆开？不考虑。
    # 尝试转换status
    try:
        status = int(status_str)
    except ValueError:
        return None
    # latency去掉ms
    if not latency_str.endswith('ms'):
        # 有些可能没有ms？假设必须有ms后缀
        return None
    try:
        latency = int(latency_str[:-2])
    except ValueError:
        return None
    # 租户解析，从tenant_str提取
    if '=' in tenant_str:
        tenant = tenant_str.split('=', 1)[1]
    else:
        tenant = tenant_str
    # 路径规范化：去查询参数
    clean_path = path.split('?')[0]
    # 返回解析结果（可以根据需要返回字典或元组）
    return (timestamp, method, clean_path, status, latency, tenant, line)
```

注意：我们保留原始行（line）用于慢请求。

然后我们在主函数中遍历sys.stdin行。读取所有行（可能很多），进行统计。注意：标准输入可能来自管道或重定向，逐行迭代。

使用defaultdict(list)存储path_latencies，使用Counter存储path_counts和status_counts，使用defaultdict(int)或两个字典用于tenant_total和tenant_error。

同时维持一个列表slow_requests = []，用于收集慢请求。

统计时：

```python
for line in sys.stdin:
    result = parse_line(line)
    if result is None:
        malformed += 1
        continue
    timestamp, method, clean_path, status, latency, tenant, original_line = result
    total_requests += 1
    status_counts[status] += 1
    path_counts[clean_path] += 1
    path_latencies[clean_path].append(latency)
    tenant_total[tenant] += 1
    if status >= 400:
        tenant_error[tenant] += 1
    if latency > 1000:
        slow_requests.append((latency, original_line, clean_path))
```

但是注意：status_counts可能有很多种，Counter可以转dict。

tenant_total和tenant_error是普通字典，我们可以用defaultdict(int).

最后处理：

top_paths: 对path_counts.items()按count降序排序，取前5，格式化为[{"path": path, "count": count}, ...]. 注意如果路径数少于5，则全部输出。

p95_latency_by_path: 遍历path_latencies，对每个路径的耗时列表排序，计算p95值。我们使用math.ceil。

```python
def compute_p95(latencies):
    if not latencies:
        return 0  # 不会发生
    sorted_lats = sorted(latencies)
    n = len(sorted_lats)
    index = math.ceil(0.95 * n) - 1  # 0-based
    return sorted_lats[index]
```

注意：ceil(0.95*n)是1-based index。例如n=10，0.95*10=9.5，ceil=10，索引9（0-based），即最大值。n=100，95，索引94。n=1，0.95*1=0.95，ceil=1，索引0，即那个值。

p95应该是整数毫秒，所以直接返回整数。

如果路径有多个耗时相同，也正常。

slow_requests: 将slow_requests列表按latency降序排序，取前10。构造结果数组：[{"original_line": line, "path": path, "latency": latency}, ...]. 注意：original_line可能包含末尾换行，最好保留原文，包括换行？JSON中字符串包含换行会有转义，但可以保留。我们strip不应该对原始行strip，原始行应该保留换行符？但作为字符串存入JSON中，换行符会转义为\n。但题目说保留原始行，我们保存时保留line原样（包含换行没问题）。但最好我们原始行读取时保留原样，但我们调用line = sys.stdin.readline()，或者for line in sys.stdin，line包含换行符。我们可以保持line原样，但输出JSON时会对特殊字符转义，没问题。

如果希望不要换行，可以rstrip('\n')，但保留原始行，我觉得保留换行也可以，但通常日志行最后有换行，保留也无妨。但要求“原始行”很可能是一行完整的文本，包括结尾换行也是行的一部分。不过JSON中字符串包含换行是合法的（但通常嵌入\n）。为保险，我们可以保留原字符串（包括换行符），但不推荐，因为显示时可能多空行。我倾向于strip末尾换行，只保留行内容。但说明中说“保留原始行”，可能是保留输入行的原始文本。输入行本身包含换行符吗？标准输入读取一行时，换行符被移除还是保留？如果使用sys.stdin.read().splitlines()则移除。如果使用for line in sys.stdin，line包含换行。通常，使用line.rstrip('\n')移除换行。为了更符合"原始行"，我觉得可以保留结尾换行，但可能会影响JSON可读性。实际上原始行应该包含整行，包括换行符？但通常人们理解原始行是指字符串内容不含换行。我选择rstrip('\n')，去掉尾随换行。但注意：可能还有其他空白（如空格）需要保留。但一般日志行末尾无空格。我们使用rstrip('\n')。

为了简单，在parse_line中，我们传入line已经rstrip过。但对于slow_requests的original_line，我们可以在parse_line返回值中包含原始行，此时原始行可以是我们传入的已经rstrip过的行，或者原样。我们可以在读取后进行strip处理（例如line = line.rstrip('\n')）然后再解析，这样original_line得到的是不带换行的。这样在JSON中更干净。所以我选择先rstrip('\n')再解析。

但注意：如果日志行末尾有多个换行（如Windows \r\n），rstrip('\n')会去掉'\n'，但如果还有'\r'，可能保留。可以使用rstrip('\r\n')？但Unix换行是\n，Windows是\r\n。我们使用line.rstrip('\r\n')会同时去除回车和换行，但要去除可能存在的行尾空格？非必要。最好只去掉换行和回车，保留其他空格。所以使用line.rstrip('\r\n')。

tenant_error_rates: 字典，key是tenant，value是错误率。错误率计算：如果tenant_total[tenant] > 0: rate = tenant_error.get(tenant, 0) / tenant_total[tenant]。用float，保留三位小数使用round(rate, 3)。需要注意的是，round可能产生精度问题，比如0.0005会四舍五入？一般可以。也可以使用format字符串，但JSON输出时直接数字。如果有多个小数位，保留三位，不足补零？JSON规范数字不补零，所以0.1会输出0.1，而不是0.100。但题目要求保留三位小数，可能期望输出0.100。所以最好格式化字符串？但JSON中数字不能有前导零？可以输出0.100，但JSON规范允许0.100，但实际JavaScript会把它当成0.1。但为了满足要求，可能需要字符串化？题目说“保留三位小数”，意思可能是数字值保留三位小数（四舍五入），在JSON中数字可以是0.100，但表示上，0.100会被解释为0.1，但视觉上保留三位不重要？按照测试可能检查字符串。我们可以输出浮点数，但JSON的浮点数表示不一定有三位小数。所以最好使用格式化输出为字符串？但要求输出JSON对象，里面数字如果是字符串，不太符合。通常保留三位小数是指四舍五入到三位小数，在数值上就是该数值，当用json.dumps输出时，会输出尽可能短的数字，比如0.1会变成0.1，而不是0.100。为了强制三位小数，我们可以把速率存储为浮点数，然后用round，但json.dumps可能会输出0.1。为了确保三位小数，可以自己实现序列化？或者使用json.dumps的default? 或者将错误率存储为字符串？但这就不是数字了。题目可能希望是数字，但保留三位小数意味着精度三位，JSON输出应该是数字，但数字不保留冗余零。但是一般检查时可能会容忍。如果特意要求保留三位小数，可能期望每个值都有三位。但我们可以使用round并输出，如果省略末尾零，可能是对的？例如0.1000会输出0.1，不满足。因此，为了精确，可以自己构造JSON字符串，使用format。但复杂。

另一种方法：使用Decimal？但为了简单，我们可以将错误率转换为浮点数，然后将其转换为字符串格式保留三位并数值化？如果使用float，0.1就是0.1。但可以使用json.JSONEncoder子类控制浮点数格式。不过我们只有错误率需要控制精度。可以用`round(rate, 3)`，再转换为float，但json.dumps会输出0.1。所以需要用自定义序列化或使用字符串替换。

可以使用`float(f"{rate:.3f}")`，但这还是浮点数，同样输出时可能省略零。所以最好在生成JSON时，对于tenant_error_rates，使用格式化字符串替换，比如`value = round(rate, 3)`然后为了确保三位，可以先把数字转为`Decimal`，但标准库有`decimal`模块，可以使用`Decimal`来格式化。但限制不使用第三方库，可以使用decimal模块（标准库）。但简单起见，我们可以在构造JSON字符串时，对错误率值使用`format(rate, '.3f')`生成字符串，然后替换掉JSON中的数字？但那样就变成了字符串。不好。

我们可以在构造字典时，将值保留为浮点数，然后手动生成JSON字符串，对每个错误率格式化为'.3f'的字符串并插入作为数字（不带引号）。但这样需要自己构建JSON，比较繁琐。

也许题目要求只是四舍五入保留三位小数，输出时不需要补零。但如果测试时期望精确字符串匹配，就需要补零。为保险起见，我们可以确保数字输出带有恰好三位小数，即使最后一位是0也保留。我们可以通过打印时，使用`json.dumps`加`default`参数，但也不能控制浮点数格式。可以重写JSONEncoder的`encode`方法？也可以。但更简单的是将错误率转换为一个decimal，然后转换为字符串，手动构造JSON输出。或者使用`json.dumps`输出后，用正则替换？不那么好。

我们可以存储为字符串，比如"0.100"，但题目要求JSON对象里的错误率应该是数字，但看起来不符合。但可能题目仅要求保留三位小数的数值，输出可以不带尾随零。因为json.dumps输出0.1，保留三位小数指的是四舍五入，0.1就是0.100的简化，也合理。暂且信任。

我们再看类似问题的要求：通常要求输出时按指定精度，应该使用round，输出不需要补零。所以用round即可。

但为了保险，我们在测试时可以检查round(0.0999, 3)=0.1，而保留三位小数应该0.100? 不确定。我决定用round，并接受输出例如0.1代表0.100。如果测试期望0.100，可能失败。但题目没有明确说明补零要求。为了尽可能符合，我可以使用`round(rate, 3)`后直接存储浮点数，并在构造JSON时使用`json.dumps`，它不会输出多余的零。但也可以通过`json.dumps`的`default`? 不。假设测试用Python解析JSON，0.1和0.100一样。所以没问题。但如果是用其他语言比较字符串，可能有区别。但题目没有指定。所以我们采用round。

我们也可以使用'%.3f'格式化数字，并将其作为数字插入，但只能手动构建JSON，例如将错误率替换为 `f"{rate:.3f}"`再插入JSON字符串中，注意加上引号？不，数字不用引号。我们可以在生成最终JSON字符串时，将错误率字段单独替换为格式化后的数字字符串。但我们需要的是精确控制。

我们可以定义函数`format_rate(rate)`返回一个浮点数，但确保它在JSON中输出三位小数？我们可以使用`json.dumps`，然后对输出的字符串进行后处理，将错误率数字替换为固定格式？但由于错误率很多，不好定位。

或者，可以使用`decimal`模块的`Decimal`对象，它可以控制精度，并且当使用`str`时能固定小数位。但`Decimal`对象在`json.dumps`中会报错。需要自定义编码器。

我决定采用简单方式：使用`round(rate, 3)`，然后直接在JSON中输出浮点数。如果测试期望视觉三位，可能会通过，但可能被扣分。考虑到题目没有强调补零，我猜测只需要数值四舍五入到三位，而不需要显示三位。因为JSON标准中，数字没有规定显示格式。例如0.1和0.100在数学上相等。所以我认为可以。

我们也可以增加一个自定义JSON序列化函数，对所有浮点数格式化为三位小数。但是也不必要，因为只有错误率是浮点数。我们可以自己构造JSON字符串的部分，或者使用json.dumps，然后使用字符串替换，但会有风险。

不如自己构建JSON输出！但整个JSON比较复杂，手动构建易错。我们可以先构建一个字典，然后使用json.dumps，然后对tenant_error_rates的值的浮点数用替换。例如：先生成json_str，然后用re.sub替换特定模式？不太好。

另一种思路：对于error_rates，将值表示为字符串 "\"0.100\"" 这样是字符串不是数字。不符合。

我决定采用round，输出后如果0.1就0.1。大部分情况下，错误率可能正好0.000或1.000，但也可能0.333等。0.333会有三位。所以大多数符合三位。如果0.1，其实是0.100，但简化为0.1在数学上等价。我认为通过。

也可以将错误率乘以1000后取整再除以1000，但输出还是0.1。

所以用round(rate, 3)。

最后，输出聚合JSON。

我们还需要处理可能的排序问题：top_paths只按count排序，如果count相同，可以按路径排序（字符串字典序）保证顺序可预测。

p95_latency_by_path不需要排序，是一个对象。

slow_requests按耗时降序，如果耗时相同，可以按路径或原始行排序？不需要，按耗时降序即可，但耗时相同可任意顺序。也可以加入次要排序。

tenant_error_rates不排序，但输出时作为对象键，无固定顺序。在Python 3.7+中，字典保持插入顺序，所以对象的键顺序会是读取中遇到的第一个租户的顺序？但JSON对象键通常不强调顺序，但有时期望字母顺序。为了可预测，可以对键排序。我们可以在构造字典时保持自然顺序，或按字母排序输出。题目没有要求，可以用任意顺序，但测试时如果比较JSON字符串可能依赖顺序。所以最好是固定顺序，可以按字母排序。这样在不同运行中一致。所以对tenant_error_rates可以排序键。

同理，status_counts也可以排序键。

p95_latency_by_path可以排序键。

top_paths 已经是列表，不需要排序对象键。

slow_requests是列表，顺序已定。

所以我们可在最终字典构建时，使用`dict(sorted(d.items()))`来确保键排序。

但要注意：JSON对象键的顺序在标准中不重要，但在测试时如果解析为对象，通常键顺序不影响比较，但直接比较字符串可能失败。为了安全，我们可以排序。

输出时，使用`json.dumps(result, indent=2, ensure_ascii=False)`? 题目没有要求缩进，但为了可读性，可以输出紧凑JSON或者带缩进? 通常要求输出JSON对象，没有指定缩进，所以默认无缩进即可。但为美观，可不缩进，但为了测试时方便查看，可以保留缩进？但注意，输出可能用于管道，缩进会加空格和换行，不影响。但一般这种工具输出紧凑JSON。我们可以使用separators=(',', ':')来紧凑，或不指定使用默认（带空格）。但输出文档没有明确，我选择默认，即带空格但不换行（键和值之间有空格）。或缩进2个空格？因为可能是给人看的，但题目说只输出JSON，可以理解为符合JSON语法的文本。我认为无缩进紧凑即可，但为了可读性，可以使用indent=None。我们选择不缩进，但默认会有空格。比如json.dumps({"a":1})输出'{"a": 1}'。这没问题。我们也可以设置separators=(',', ':')消除空格，如'{"a":1}'。但都可以。但测试时可能会解析，所以任何一种都可以。我使用默认（美化一点）即可，因为总代码不超过1000行，这不是问题。使用indent=2可能增加字数，但可读性好。但我不确定。通常命令行工具输出紧凑JSON。我选择indent=None，但保留空格。

注意：如果使用indent=2，每个元素换行，那么对于大型输出，会增加行数，但无所谓。我们选择indent=2在测试时方便查看，但题目没要求，为了简洁，可以不加缩进。为了简单，使用默认即可，否则需要谨慎处理换行带来的问题。我选择使用`json.dumps(result, default=str, ensure_ascii=False)`并指定indent=2? 还是使用plain？我决定输出紧凑一点：`json.dumps(result, separators=(',', ':'))`，这样节省空间。使用紧凑格式在很多命令中常用。

但注意：在JSON中，数字、布尔、null的字面量，不能有额外空格。

所以最终：`print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))`。

现在考虑测试函数：`--test`参数。

测试用例：我们可以虚构一些输入行，然后捕获标准输出，解析JSON，验证字段值。

因为程序从stdin读取，在测试时，我们可以将stdin替换为io.StringIO对象。

测试函数可以命名为`run_tests()`。

我们设计测试数据，测试解析和统计。我们构造若干行，包括一些格式错误行，然后检查输出。

例如：

输入：
```
2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1
2026-05-01T12:03:19Z GET /api/orders 200 456ms tenant=a1
2026-05-01T12:03:20Z GET /api/orders 500 200ms tenant=a2
2026-05-01T12:03:21Z POST /api/users 404 150ms tenant=a1
2026-05-01T12:03:22Z GET /api/items 200 1000ms tenant=a3
invalid line
2026-05-01T12:03:23Z GET /api/orders 200 1100ms tenant=a2
2026-05-01T12:03:24Z GET /api/orders?page=2 200 300ms tenant=a1
```

一些说明：注意第四个有状态码404，算错误；第五个耗时1000ms，不算大于1000，所以不算慢（slow要求>1000ms），第六个格式错误，第七个耗1100ms慢请求，第八个带查询参数，路径应为/api/orders。

我们期望计算：

- total_requests: 7（第1-5、7、8）(第6行非法)。total=7。
- malformed_lines:1
- status_counts: 200:4? (第1,2,5,8), 500:1, 404:1。
- top_paths: /api/orders出现次数最多（第1,2,7,8）共4次？第1,2,7,8共4次，/api/users 1次，/api/items 1次。所以前5应该是/api/orders:4, /api/users:1, /api/items:1。可能还有其他？只有三个路径。所以输出三个。
- p95_latency_by_path:
  - /api/orders:latency分别为123,456,1100,300（注意第8个300ms，第7个1100ms）。排序: 123,300,456,1100。N=4, 0.95*4=3.8, ceil=4, index=3 -> 1100。
  - /api/users: lat [150] N=1 index0=150。
  - /api/items: lat [1000] index0=1000。
- slow_requests: latency>1000的只有第7行1100ms，可能还有其他？如果只有1个，则输出该条。按降序前10。输出[{original_line, path, latency=1100}]。注意第5行耗时1000ms不算。
- tenant_error_rates:
  - a1: total请求：行1,2,4,8 => 4个请求；错误：行4 (404) => 1次错误，错误率=1/4=0.25。
  - a2: 行3(500)和行7(1100,200? 等等状态码200? 行7: 200 1100ms, 所以正确，非错误；所以a2 total=行3(500)和行7(200) =>2; 错误=1 (行3); 错误率=0.5。
  - a3: 行5(200) => 1, 错误=0 => 0.0。

检查。可测试。

另外，top_paths: 可能还有其他路径，所以只输出三个，所以前5就是这三个。

测试时断言这些值。

此外，测试parse_line单独？但集成测试即可。

实现测试函数时，我们使用`unittest.TestCase`或简单assert。为了简单，我们可以直接编写断言。

注意：在测试时，我们需要捕获stdout和stdin。我们可以重定向。

我们可以用：

```python
import sys
import io

def run_tests():
    # 测试案例
    test_input = """..."""
    stdin_backup = sys.stdin
    sys.stdin = io.StringIO(test_input)
    try:
        # 执行主流程？但主流程会打印JSON并可能退出。
        # 我们不能直接调用main，因为main会读取stdin并输出，还会根据参数执行测试。
        # 我们可以将主逻辑提取为函数，接收输入流，返回结果字典，然后由main决定输出。
        # 所以，最好的设计是将处理逻辑分离：process_logs(input_stream)返回结果字典，main负责输出JSON。
        # 测试时，调用process_logs(io.StringIO(...))然后断言结果。
    finally:
        sys.stdin = stdin_backup
```

所以我们重构：定义`process_logs(input_stream)`函数，返回一个字典，包含所有要输出的数据。`main()`函数读取sys.stdin作为输入流，调用`process_logs(sys.stdin)`，然后输出JSON。测试时，可以直接调用`process_logs`并断言。

这样更清晰。

`process_logs`处理所有行，返回字典。

注意：`process_logs`中需要统计malformed_lines等。

实现细节：

```python
import sys
import json
import math
from collections import Counter, defaultdict

def parse_line(line):
    # 返回 (path, status, latency, tenant, original_line) 或 None
    line = line.rstrip('\r\n')
    parts = line.split()
    if len(parts) < 6:
        return None
    # 可能有字段包含空格？不考虑。
    # 我们假设前6个字段
    timestamp, method, path, status_str, latency_str, tenant_str = parts[:6]
    # 转换status
    try:
        status = int(status_str)
    except ValueError:
        return None
    # latency
    if not latency_str.endswith('ms'):
        return None
    try:
        latency = int(latency_str[:-2])
    except ValueError:
        return None
    # 租户
    # 可以解析等号内容
    if '=' in tenant_str:
        tenant = tenant_str.split('=', 1)[1]
    else:
        tenant = tenant_str
    # 路径去参数
    clean_path = path.split('?')[0]
    return (clean_path, status, latency, tenant, line)
```

注意：我们把timestamp和method丢弃（但保留原始行）。所以parse_line返回5元组。

在process_logs中：

```python
def process_logs(input_stream):
    total_requests = 0
    malformed = 0
    status_counts = Counter()
    path_counts = Counter()
    path_latencies = defaultdict(list)
    tenant_total = defaultdict(int)
    tenant_error = defaultdict(int)
    slow_requests = []  # list of (latency, original_line, clean_path)

    for line in input_stream:
        parsed = parse_line(line)
        if parsed is None:
            malformed += 1
            continue
        clean_path, status, latency, tenant, orig_line = parsed
        total_requests += 1
        status_counts[status] += 1
        path_counts[clean_path] += 1
        path_latencies[clean_path].append(latency)
        tenant_total[tenant] += 1
        if status >= 400:  # 4xx or 5xx? 也包含>=600，但无所谓
            tenant_error[tenant] += 1
        if latency > 1000:
            slow_requests.append((latency, orig_line, clean_path))

    # 计算结果
    # top_paths
    top_paths_data = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))[:5]
    top_paths = [{"path": p, "count": c} for p, c in top_paths_data]

    # p95
    p95_result = {}
    for path, lats in path_latencies.items():
        sorted_lats = sorted(lats)
        n = len(sorted_lats)
        index = math.ceil(0.95 * n) - 1
        p95_result[path] = sorted_lats[index]

    # slow_requests 排序取前10
    slow_requests.sort(key=lambda x: -x[0])  # 按latency降序
    slow_top10 = slow_requests[:10]
    slow_list = [{"original_line": sr[1], "path": sr[2], "latency": sr[0]} for sr in slow_top10]

    # tenant_error_rates
    tenant_rates = {}
    for tenant, total in tenant_total.items():
        errors = tenant_error.get(tenant, 0)
        rate = errors / total if total > 0 else 0.0
        rate = round(rate, 3)
        tenant_rates[tenant] = rate

    # 为了JSON键有序，对字典排序（可选）
    # 注意：Python 3.7+ 保留插入顺序，但插入顺序是按发现顺序，不可预测。所以我们对status_counts、p95_result、tenant_rates排序。
    status_counts_sorted = dict(sorted(status_counts.items()))
    p95_sorted = dict(sorted(p95_result.items()))
    tenant_rates_sorted = dict(sorted(tenant_rates.items()))

    result = {
        "total_requests": total_requests,
        "status_counts": status_counts_sorted,
        "top_paths": top_paths,
        "p95_latency_by_path": p95_sorted,
        "slow_requests": slow_list,
        "tenant_error_rates": tenant_rates_sorted,
        "malformed_lines": malformed
    }
    return result
```

注意：`top_paths` 列表不需要排序键（路径、计数）？

注意：慢请求的`original_line`，我们需要原始行（包括可能的前后空格）。在parse_line中，我们对line使用了rstrip('\r\n')，但此时line是原始行去掉换行符的版本。但原始行如果含有前导或尾随空格？日志通常没有前导空格，但我们保存的line是经过rstrip('\r\n')的，即去掉了换行但保留了空白。所以original_line是干净的。但可能丢失末尾空格，不过一般日志无末尾空格。所以acceptable。如果我们希望保留全部原始字符包括换行，可以保留line原样，但JSON中会有转义。我选择使用rstrip('\r\n')。

注意：在parse_line中，我们修改了line，但original_line返回这个修改后的。我们确保line.rstrip('\r\n')后返回。所以original_line没有结尾换行。

也可以传入line直接，在parse_line内部先保存原始行（未strip）但处理时使用strip版本。为了稳妥，我们可以在parse_line内部对line不做修改，而是使用line.rstrip('\n')进行分割。但原始行保留原样（包括结尾换行）。但我们不希望换行符出现在JSON字符串中。通常，JSON允许换行符转义，但可能不希望。我们可以保留原行，然后在JSON中输出时，换行符会变成\n，直观上可读。但最好还是去掉换行。所以我们选择去掉换行。

现在，`main()`:

```python
def main():
    import sys
    # 检查参数
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return
    # 正常处理
    result = process_logs(sys.stdin)
    # 输出JSON
    json_str = json.dumps(result, ensure_ascii=False, separators=(',', ':'))
    sys.stdout.write(json_str)
    # 可选输出换行
    sys.stdout.write('\n')
```

注意：如果输出时我们使用print(json_str)会自动添加换行，但print可能会在末尾加换行。使用sys.stdout.write可以控制。建议加换行，以便读取。

测试函数`run_tests()`:

```python
def run_tests():
    import io
    # 测试用例1
    test_input = """\
2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1
2026-05-01T12:03:19Z GET /api/orders 200 456ms tenant=a1
2026-05-01T12:03:20Z GET /api/orders 500 200ms tenant=a2
2026-05-01T12:03:21Z POST /api/users 404 150ms tenant=a1
2026-05-01T12:03:22Z GET /api/items 200 1000ms tenant=a3
invalid line
2026-05-01T12:03:23Z GET /api/orders 200 1100ms tenant=a2
2026-05-01T12:03:24Z GET /api/orders?page=2 200 300ms tenant=a1
"""
    stream = io.StringIO(test_input)
    result = process_logs(stream)
    # 验证
    assert result["total_requests"] == 7, f"total_requests should be 7, got {result['total_requests']}"
    assert result["malformed_lines"] == 1, f"malformed_lines should be 1, got {result['malformed_lines']}"
    assert result["status_counts"] == {200: 4, 404: 1, 500: 1}, f"status_counts mismatch: {result['status_counts']}"
    # top_paths (order may vary, but we sorted by count desc, path asc)
    expected_top = [
        {"path": "/api/orders", "count": 4},
        {"path": "/api/items", "count": 1},
        {"path": "/api/users", "count": 1}
    ]
    assert result["top_paths"] == expected_top, f"top_paths mismatch: {result['top_paths']}"
    # p95
    # /api/orders lat: [123,300,456,1100] -> sorted: [123,300,456,1100], n=4, ceil(0.95*4)=4, idx3=1100
    # /api/items: [1000] -> idx0=1000
    # /api/users: [150] -> idx0=150
    assert result["p95_latency_by_path"] == {"/api/orders": 1100, "/api/items": 1000, "/api/users": 150}, \
        f"p95 mismatch: {result['p95_latency_by_path']}"
    # slow_requests: only latency >1000: 1100 (a2). Note: 1000ms is not >1000, so not included.
    assert len(result["slow_requests"]) == 1, f"slow_requests should have 1, got {len(result['slow_requests'])}"
    slow = result["slow_requests"][0]
    assert slow["latency"] == 1100
    assert slow["path"] == "/api/orders"
    assert slow["original_line"] == "2026-05-01T12:03:23Z GET /api/orders 200 1100ms tenant=a2"
    # tenant_error_rates
    # a1: 4 requests (line1,2,4,8)，errors: line4 404 => 1/4=0.25
    # a2: 2 requests (line3,7)，errors: line3 500 => 1/2=0.5
    # a3: 1 request，errors:0 => 0.0
    expected_rates = {"a1": 0.25, "a2": 0.5, "a3": 0.0}
    # round introduces 0.0 not 0.000
    assert result["tenant_error_rates"] == expected_rates, f"tenant_error_rates mismatch: {result['tenant_error_rates']}"
    # 另外测试一些边界条件：空输入？
    # 测试没有慢请求
    # 测试top_paths不足5
    # 测试很多请求（可以省略）
    # 测试查询参数去除
    print("All tests passed.")
```

为充分测试，再测试一个空输入、只有malformed行、混合等。

也可以测试parse_line函数本身。

但题目要求“包含若干内置测试函数”，所以我们需要包含测试。

注意：测试应该打印一些成功信息，但不影响正常模式。用print在测试中没问题。

在`--test`下执行测试。

如果测试通过，`run_tests`正常结束，返回并退出。如果断言失败，抛出异常并退出。

我们还可以使用`unittest`模块，但可能增加代码复杂度。我们可以自己写简单test。

现在整合代码，确保不超过1000行。

考虑边界情况：

- 空输入：total_requests=0, status_counts={}, top_paths=[], p95_latency_by_path={}, slow_requests=[], tenant_error_rates={}, malformed_lines=0。处理时，path_counts空，top_paths为空列表。p95遍历path_latencies为空，得到空字典。tenant_total空，得到空字典。一切正常。
- 所有行都malformed：total_requests=0，malformed=计数。其他空。
- latency可能是0ms? 可以，但是否>1000时不包含0。

- 耗时可能是负数？不出现。

- 状态码可能是其他整数，但HTTP状态码不会负数。但仍可统计。

- 路径可能包含#？去除?之前。假设没有#。

- 路径可能带协议？不会，是路径。

- 原始行可能包含多余字段（多于6个）？我们的parse_line只取前6个，忽略后面的。这样可能算为有效？但这样会错误解析。比如路径包含空格，导致split将路径分为多个部分，那么我们的6字段可能会把部分路径当作后续字段。所以这种行算作有效但解析错误。更健壮的方法是用正则，但题目格式规范中路径可能包含空格吗？通常HTTP请求行中路径没有空格，但查询参数可能包含空格编码？空格被编码为%20，所以路径本身无空格。所以split应该OK。

但有些用户可能在日志中使用其他分隔符？这里固定空格。所以安全。

但注意：租户字段可能包含空格？不应该。

所以解析基本可靠。

现在，关于慢请求的original_line：我们在parse_line中返回的orig_line是经过rstrip('\r\n')的原始行吗？我们目前是在parse_line内部使用line.rstrip('\r\n')后分割，但分割时parts使用line.rstrip('\r\n')。但我们在返回时使用orig_line = line（经过strip）？我们怎么得到original_line？在parse_line中，我们在函数开头对line进行strip，然后operate on stripped_line，但original_line也可能是stripped_line。如果我们希望original_line保留原始行（无换行），可以这样。但是我们的line是来自for line in input_stream，line包含换行符。我们传入parse_line时，line包含换行。我们需要去掉换行符，但不希望改其他空白。所以我们在parse_line内的line使用line.rstrip('\r\n')赋值给一个新的变量？或者我们在循环内对line先rstrip再传入，但我们需要original_line无换行，所以使用line.rstrip('\r\n')，如果我们需要保留原始行头部空格，但日志无头部空格。所以可行。

但注意：原始行中的`original_line`包含空格分割时的原始字段，但我们如果去掉换行，原始行与输入行内容一致（除了换行）。应该没问题。

测试中我们断言original_line等于 "2026-05-01T12:03:23Z GET /api/orders 200 1100ms tenant=a2"。而输入中该行末尾没有空格，所以一致。

还需要测试其他情况。

现在，可能还需要处理耗时字段可能为"0ms"或"10ms"等，解析正确。

p95计算：当N=0时不会发生，但在循环中我们只有有请求的路径才会进入。如果某路径在统计过程中被添加，确保latencies列表非空。

注意：top_paths排序：我们使用(-count, path)排序，当count相同时按路径字母升序。这样有序。

关于输出JSON时，数字类型在JSON中正常。

我们需要调整输出格式：json.dumps参数ensure_ascii=False允许非ASCII字符，但路径可能包含中文？日志可能，但无关紧要。可以设置确保兼容。

可以设置default=str以防出现特殊类型（但不会）。

现在，测试函数完成。

我们还可以测试更多边缘情况：有多条耗时相同的慢请求，只取前10；检查排序。

但几个断言已经覆盖核心。

为了更全面，可以增加测试：

1. 测试只有一条慢请求且latency=1001>1000, 一条=1000不算。
2. 测试p95计算：N=3, 0.95*3=2.85, ceil=3, index=2取最大值。
3. 测试错误率保留三位小数：例如错误率1/3=0.333...
4. 测试top_paths超过5个，只取5个。
5. 测试查询参数去除：/api/orders?page=2&size=10应该转换为/api/orders。
6. 测试租户没有等号的情况，如"tenant a1"？格式应是"tenant=a1"，但如果我们宽松处理，租户字段为"a1"（无等号）？这时我们的代码会将其当作tenant="a1"。但示例要求提取a1，那没问题。如果字段是"abc"，则tenant="abc"。但原要求是"tenant=a1"，所以我们假设都带等号。但为了健壮，我们支持无等号直接作为租户值。但此时在输出中租户值可能和解析后的不符。我认为保留宽松。

7. 但是，如果租户字段以tenant=开头，我们取=后；如果不是，我们取全部字段。这样更包容。

8. 同时注意：租户字段可能包含空格的如"tenant=a1"无空格，没问题。

还有其他潜在错误：路径可能包含空格（但少见）。忽略。

关于慢请求：需要按照耗时降序。如果耗时相同，可以按路径或原始行排序以稳定。但未要求，我们按latency降序，如果latency相同，可以按其次序（比如原始行？）。我们可以在排序时使用key=lambda x: (-x[0], x[1])（latency降，然后original_line升）产生稳定排序。但要求中未指定，所以简单用latency降序即可。Python sort是稳定的，所以原始顺序保持，而原始顺序是输入顺序，不确定。所以如果latency相同，则输出顺序保持处理顺序（输入顺序）。这应该可接受。但为了稳定，可以加入次要排序（如原始行）保证可重现。我们可以在slow_requests.append时加入一个序号，但我觉得不必。可以接受。

我将保持简单：slow_requests.sort(key=lambda x: -x[0])。

现在，我考虑代码风格、清晰度、行数限制。总代码不超过1000行。我们的代码预计不会超过200行。所以没问题。

注意：我们需要在程序文件头部声明注释？不需要。

现在，我们思考输入的读取可能非常大，但逐行处理没问题。

潜在优化：p95计算需要排序每个路径下的耗时列表，可以使用nth_element但不需要，对于每个路径的列表排序是必需的。如果数据很大，排序可能耗时，但可以接受。要求看到的是功能，不是性能。

最后，输出JSON。

我们确认所有字段都符合要求。

**要求细节检查**：

- total_requests: 整数
- status_counts: 状态码为键，次数为值 (JSON对象)
- top_paths: 数组，每个包含path和count。路径字符串。顺序按请求量降序。
- p95_latency_by_path: 对象，路径为键，p95整数。
- slow_requests: 数组，每个包含original_line, path, latency。注意：这里latency是整数（毫秒）。original_line是字符串（原始行）。path是字符串（去参数）。
- tenant_error_rates: 对象，租户为键，错误率为数字（保留三位小数）。
- malformed_lines: 整数

注意，需要确保所有数据在输出时类型正确。

关于p95，我们针对每个路径单独计算，即使某个路径请求数很少。

关于slow_requests，我们要求耗时大于1000ms的前10条；如果不足10条，全部输出。我们按降序取前10。

**代码测试**：在运行模式，不需要输出解释文字。

**--test参数**：运行测试，然后退出。注意，我们通过sys.argv[1]判断是否为'--test'，如果用户运行 `python log_analyzer.py --test` 则执行测试。但是如果用户同时有其他参数，我们的处理很脆弱。但题目只要求支持--test，所以忽略其他情况。也可以支持`--test`单独。

代码中，我们检查`if len(sys.argv) > 1 and sys.argv[1] == '--test'`，执行测试后直接return，不处理之后。

现在，组合完整代码。

我们需要导入`sys`, `json`, `math`, `collections` (Counter, defaultdict)。`io`可能在测试时需要。

我们编写`parse_line`, `process_logs`, `run_tests`, `main`。

`main`函数在模块顶层调用，如果运行脚本则执行。

我们加入`if __name__ == "__main__": main()`。

现在，注意在测试函数中我们使用io.StringIO，需要import io。

另外，测试中我们使用的断言内置，如果有错误会抛出AssertionError并退出。可以用print输出提示。

测试中我们打印成功提示。但程序在测试时也可能会抛出异常。这样方便调试。

但注意：如果测试失败，程序会非正常结束，显示Traceback。但测试设计如此。

我们也可以在测试中用try/except，但简单断言即可。

为了让测试更详细，我们可以用unittest模块，但会增加代码行，而且需要更多结构。为了简单，我们使用assert。

但注意，当测试运行时，如果成功，打印"All tests passed."，然后退出。如果失败，抛出异常并显示错误信息，也会打印到stderr。这可以接受。

但要求“当使用 --test 参数运行时执行测试”，没有规定测试的输出格式。所以这样OK。

**考虑malformed_lines计数**：当parse_line返回None时增加malformed。我们在process_logs中遍历每一行，包括可能空行。空行（空白行）split后为空列表，长度<6，所以计为malformed。这是合理的，因为无法解析。但有些blank line可能需要跳过而不算malformed？题目说“跳过无法解析的行，并在输出中给出malformed_lines数量”，所以空行属于无法解析。所以计入malformed。

但注意，日志可能包含空行，应该算malformed。

我们测试中，在输入里有一行"invalid line"，split后长度只有2，所以malformed+1。

**关于`path`规范化**：路径可能包含查询参数，如`/api/orders?page=2`，我们取?前部分。注意：如果路径不包含?则保持不变。注意：如果路径包含多个?? 通常只一个。所以我们使用split('?')[0]即可。

**关于租户解析**：我们使用了`if '=' in tenant_str: tenant = tenant_str.split('=', 1)[1] else: tenant = tenant_str`。但是注意，如果租户字符串为"tenant="，则分割后第二部分为空字符串，这样租户值为""，可能产生空字符串。这种情况可能视为有效或无效？我们认为是有效的，租户是空字符串。但可能不合理。但题目假设租户如a1形式，所以值非空。我们可以额外检查租户是否为空？但不必。

**关于耗时ms**：如果latency_str是"ms"或"abcms"? 我们要求后缀"ms"。如果只是"ms"没有数字，int转换失败，返回None；如果"123ms"成功。但如果格式如"123.0ms"? 我们使用int直接转换会失败。但题目说耗时毫秒整数，所以没有小数。所以我们使用int转换。如果出现"123.0ms"属于无法解析？可能。所以我们默认是整数ms。所以没问题。

**关于状态码**：直接int，但如果状态码是字符串"200a"？会ValueError，返回None。

**关于原始行保留**：在slow_requests中original_line使用我们parse_line中返回的orig_line。我们在parse_line中应该传回原始行（已rstrip'\r\n'）。那么是否可以保证与输入行一致（无换行）？我们确保在parse_line传入line（可能带换行），我们先对line进行rstrip('\r\n')后再分割。但我们会丢失原始行中结尾空格？但通常无。如果我们想要保留原始行尾部可能存在的空格，但我们分割前使用rstrip会去掉换行，但可能也去掉其他末尾空白？`rstrip('\r\n')`只去掉换行和回车，不去掉其他空白。如果行末尾有空格，rstrip('\r\n')会保留这些空格，因为参数只包含\r\n。所以保留。所以原始行包括尾部空格（在JSON中可见）。但日志一般没有尾随空格，所以忽略。

但是，如果行包含换行符如\r\n，我们只去掉\r\n，保留其他。所以字符串内容符合输入（除了换行符被移除）。所以近似原始行。

为了准确，我们可以在处理前保留原始行的副本，然后传入parse_line。我们让调用者决定。简单起见，我会在parse_line内部将原始行作为参数传入，并在内部使用line.rstrip('\r\n')分割，但返回时返回原始行的rstrip('\r\n')版本。所以original_line是去除了换行的行。这样应该没问题。

我们也可以传入line（未strip），在parse_line内部使用line.rstrip('\r\n')进行split，但返回line.rstrip('\r\n')作为原始行。所以OK。

**关于输出顺序**：我们排序了：status_counts按状态码升序，p95按路径字母升序，tenant_error_rates按租户字母升序。top_paths按count降序。slow_requests按latency降序。这些是合理的。

**潜在问题**：如果top_paths不足5个，我们列出全部。空列表也是可以的。

**测试案例**：最好多测试几个边界。比如p95对于只有1条的情况: n=1, 0.95*1=0.95, ceil=1, index=0 -> 那条latency。所以是对的。

**java**? nothing.

现在开始编写代码。

代码风格：我们使用函数进行模块化。

最后，请确保代码不超过1000行，显然远低于。

**完善测试函数**：测试要全面。

添加测试用例：空输入，测试结果应为默认空。

测试用例：只有两行，一个有效一个malformed。

测试用例：多个路径top_paths超过5个。

测试用例：慢请求有多个，确保只取10个。

测试用例：latency=1000不算慢请求。

测试用例：错误率不同，包括0和1。

测试用例：状态码包含4xx和5xx均算错误。

测试用例：包含多种错误率，比如1/3=0.333，round后是0.333。

测试用例：查询参数去除，路径含?。

测试用例：租户解析等号后内容。特别测试tenant字段无等号。

我们可以单独测试parse_line函数，但也可在集成测试中覆盖。

由于代码量小，我们可以在测试函数中包含几个子测试函数，或分开写。

我们将run_tests定义多个测试场景，使用单独的函数并在run_tests中调用。

我们也可以使用单元测试风格。比如定义test_empty，test_sample等。

但为了简单，我们就在run_tests中顺序测试。

但我们有多个测试案例，可能会造成run_tests很长，但可以接受。

为清晰，我们可以在run_tests中定义辅助函数，比如`check_result(name, input_lines, expected_dict)`，但这样可能增加复杂性。

保持简单，直接构造每个case的输入，调用process_logs，断言。

为了不使run_tests过于冗长，我们设计2-3个测试。

但需要覆盖基本功能。

我们也可以对parse_line函数单独测试，但可以放在集成测试。

我计划包括：

1. 基础测试（包括查询参数、慢请求、各种边界）
2. 空输入测试。
3. 仅malformed行测试。
4. top_paths超过5个测试。
5. 慢请求排序和截断测试。
6. 错误率多位小数测试。

这样较为全面。

**空输入测试**：

输入空字符串，结果应为：total_requests=0, status_counts={}, top_paths=[], p95_latency_by_path={}, slow_requests=[], tenant_error_rates={}, malformed_lines=0。

**仅malformed行测试**：几行无法解析，应统计malformed_lines。

**top_paths超过5个**：构建6个不同路径各1次，同一个路径出现多次。确保按count降序取5个。

**慢请求截断**：构建11个慢请求，看是否只取前10，并且按降序。

**错误率小数**：例如每租户总请求和错误数，产生1/3=0.333...，确保round后为0.333。

此外，测试任意顺序。

另外，测试状态码计数，多种状态码。

这样可以确保大部分功能正确。

我们就按此构造。

但是注意，测试应使用合理的输入格式。

现在编写代码。注意，使用python 3，标准库。

**潜在改进**：为了更健壮，可以在parse_line中增加对时间格式的基本验证：是否包含T或者Z？但可能不必须。跳过。

**注意**：路径可能有锚点（#）？通常URL片段不会发送到服务器，但可能出现在日志中？按HTTP协议请求行没有#。但如果有，我们未处理。忽略。

**关于p95的ceil**：我们使用math.ceil。不要忘记import math。

**关于大的输入**：慢请求列表如果很大（如百万），将所有慢请求保存到列表再排序取前10可能消耗内存。可以改用堆（heapq.nlargest）。但为了代码简单，我们接受列表排序。如果考虑极端，可以使用heapq。但这里要求代码不超过1000行，且不要求性能，但我们可以加入heapq优化。但为了简单，直接用sort并取前10。但如果有几百万个慢请求，列表占用内存大。但log行数未知，但可以考虑使用heapq。标准库有heapq，我们可以使用`heapq.nlargest(10, slow_requests, key=lambda x: x[0])`。这样可以节省排序内存。但用列表sort也可以，但sort需要O(N log N)，而nlargest是O(N log K)。对于大N更好。我们决定使用heapq.nlargest，因为它是标准库，且更高效。

同样，top_paths也可以使用heapq但一般路径数量不会太多，但使用排序也可。

我们导入heapq。

但我们需要保持代码简单。对于慢请求，可以使用heapq.nlargest。

修改：不维持列表，直接heapq？但我们仍然需要遍历所有慢请求，我们可以维持一个大小为10的堆。但最简单还是收集所有，然后使用heapq.nlargest。但收集所有列表可能会占用大量内存，是否需要注意？但题目没有限制内存，且日志可能很大，但我们可以优化。

我们使用`heapq.nlargest(10, slow_requests, key=lambda x: x[0])`，但slow_requests列表依然需要存储全部。所以仍然存储全部。为了不存储全部，我们可以用容量为10的最小堆来跟踪Top10。但我们仍需要存储所有，以便可能排序？实际上，我们可以使用一个容量10的堆，遍历时维护：如果项数小于10，直接加入；如果大于10，与堆顶比较（最小堆）。但实现稍复杂。但简单起见，我们可以接受列表全部存储，因为日志量一般不会过千万，而且题目允许。所以可以使用列表。

但为了代码简洁，我们保持列表。不过可以用nlargest，但nlargest也接受可迭代对象，可以不用先建列表，但我们需要列表存储慢请求吗？我们可以直接在一个列表中存储所有慢请求，或者也可以不存列表，但需要知道原始行等信息，所以必须存储。所以我们维持一个列表。

所以不强制使用heapq。

我们继续使用列表后排序取前10。

现在，代码架构：

```python
#!/usr/bin/env python3
import sys
import json
import math
from collections import Counter, defaultdict

def parse_line(line):
    # 返回 (clean_path, status, latency, tenant, original_line) 或 None
    # 输入 line 可能包含换行，先去掉换行（保留其他空白）
    original_line = line.rstrip('\r\n')
    parts = original_line.split()
    if len(parts) < 6:
        return None
    # 只取前6个字段
    timestamp, method, path, status_str, latency_str, tenant_str = parts[:6]
    try:
        status = int(status_str)
    except ValueError:
        return None
    # 耗时: 去掉ms后缀
    if not latency_str.endswith('ms'):
        return None
    try:
        latency = int(latency_str[:-2])
    except ValueError:
        return None
    # 租户解析
    if '=' in tenant_str:
        tenant = tenant_str.split('=', 1)[1]
    else:
        tenant = tenant_str
    # 路径脱参
    clean_path = path.split('?')[0]
    return (clean_path, status, latency, tenant, original_line)

def process_logs(input_stream):
    total = 0
    malformed = 0
    status_counts = Counter()
    path_counts = Counter()
    path_latencies = defaultdict(list)
    tenant_total = defaultdict(int)
    tenant_errors = defaultdict(int)
    slow_requests = []  # list of (latency, original_line, clean_path)

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
        if latency > 1000:
            slow_requests.append((latency, orig_line, clean_path))

    # 构造结果
    # top_paths
    top_items = sorted(path_counts.items(), key=lambda x: (-x[1], x[0]))[:5]
    top_paths = [{"path": p, "count": c} for p, c in top_items]

    # p95
    p95 = {}
    for path, lats in path_latencies.items():
        sorted_lats = sorted(lats)
        n = len(sorted_lats)
        idx = math.ceil(0.95 * n) - 1
        p95[path] = sorted_lats[idx]

    # slow_requests 排序取前10
    slow_requests.sort(key=lambda x: -x[0])
    slow_top = slow_requests[:10]
    slow_list = [{"original_line": line, "path": p, "latency": lat} for lat, line, p in slow_top]

    # tenant_error_rates
    error_rates = {}
    for tenant, total_count in tenant_total.items():
        errs = tenant_errors.get(tenant, 0)
        rate = round(errs / total_count, 3) if total_count > 0 else 0.0
        error_rates[tenant] = rate

    # 排序字典项以保证顺序一致
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
    import io
    # Test 1: 基础测试
    test_input = """\
2026-05-01T12:03:18Z GET /api/orders 200 123ms tenant=a1
2026-05-01T12:03:19Z GET /api/orders 200 456ms tenant=a1
2026-05-01T12:03:20Z GET /api/orders 500 200ms tenant=a2
2026-05-01T12:03:21Z POST /api/users 404 150ms tenant=a1
2026-05-01T12:03:22Z GET /api/items 200 1000ms tenant=a3
invalid line
2026-05-01T12:03:23Z GET /api/orders 200 1100ms tenant=a2
2026-05-01T12:03:24Z GET /api/orders?page=2 200 300ms tenant=a1
"""
    result = process_logs(io.StringIO(test_input))
    # Assertions
    assert result["total_requests"] == 7, f"Test1 total_requests fail: {result['total_requests']}"
    assert result["malformed_lines"] == 1, f"Test1 malformed_lines fail: {result['malformed_lines']}"
    assert result["status_counts"] == {200: 4, 404: 1, 500: 1}, f"Test1 status_counts fail: {result['status_counts']}"
    expected_top = [
        {"path": "/api/orders", "count": 4},
        {"path": "/api/items", "count": 1},
        {"path": "/api/users", "count": 1}
    ]
    assert result["top_paths"] == expected_top, f"Test1 top_paths fail: {result['top_paths']}"
    assert result["p95_latency_by_path"] == {"/api/orders": 1100, "/api/items": 1000, "/api/users": 150}, \
        f"Test1 p95 fail: {result['p95_latency_by_path']}"
    assert len(result["slow_requests"]) == 1, f"Test1 slow_requests count fail: {len(result['slow_requests'])}"
    slow0 = result["slow_requests"][0]
    assert slow0["latency"] == 1100
    assert slow0["path"] == "/api/orders"
    assert slow0["original_line"] == "2026-05-01T12:03:23Z GET /api/orders 200 1100ms tenant=a2"
    assert result["tenant_error_rates"] == {"a1": 0.25, "a2": 0.5, "a3": 0.0}, \
        f"Test1 tenant_error_rates fail: {result['tenant_error_rates']}"
    print("Test 1 passed.")

    # Test 2: 空输入
    result2 = process_logs(io.StringIO(""))
    assert result2["total_requests"] == 0
    assert result2["status_counts"] == {}
    assert result2["top_paths"] == []
    assert result2["p95_latency_by_path"] == {}
    assert result2["slow_requests"] == []
    assert result2["tenant_error_rates"] == {}
    assert result2["malformed_lines"] == 0
    print("Test 2 (empty input) passed.")

    # Test 3: 全是非法行
    input3 = "invalid1\ninvalid2\n"
    result3 = process_logs(io.StringIO(input3))
    assert result3["total_requests"] == 0
    assert result3["malformed_lines"] == 2
    print("Test 3 (malformed only) passed.")

    # Test 4: 多个路径 top_paths 只取前5
    lines4 = []
    paths4 = [f"/api/path{i}" for i in range(6)]  # 6条不同路径
    # path0 出现3次，path1 2次，其余1次，因此前5取path0-4?
    # 我们让path0出现3，path1出现2，path2-5各1。不想path5被排除。
    for i in range(3):
        lines4.append(f"2026-05-01T12:00:0{i}Z GET /api/path0 200 10ms tenant=x")
    for i in range(2):
        lines4.append(f"2026-05-01T12:00:1{i}Z GET /api/path1 200 10ms tenant=x")
    for i in range(2, 6):
        lines4.append(f"2026-05-01T12:00:{i}Z GET /api/path{i} 200 10ms tenant=x")
    input4 = "\n".join(lines4)
    result4 = process_logs(io.StringIO(input4))
    # 路径计数：/api/path0:3, /api/path1:2, /api/path2:1, /api/path3:1, /api/path4:1, /api/path5:1
    # top5 应该是 path0, path1, path2, path3, path4 (按计数降序，计数相同按路径字母顺序)
    top_paths4 = result4["top_paths"]
    assert len(top_paths4) == 5, f"Test4 top_paths count fail: {len(top_paths4)}"
    expected_paths4 = [
        {"path": "/api/path0", "count": 3},
        {"path": "/api/path1", "count": 2},
        {"path": "/api/path2", "count": 1},
        {"path": "/api/path3", "count": 1},
        {"path": "/api/path4", "count": 1},
    ]
    assert top_paths4 == expected_paths4, f"Test4 top_paths fail: {top_paths4}"
    print("Test 4 (top_paths limit) passed.")

    # Test 5: 慢请求排序和截断 (超过10个)
    lines5 = []
    # 构造20个慢请求，耗时从1001到1020，这样按降序取10个应该是1020-1011
    for i in range(20):
        latency = 1001 + i
        lines5.append(f"2026-05-01T12:00:00Z GET /api/test {200} {latency}ms tenant=x")
    input5 = "\n".join(lines5)
    result5 = process_logs(io.StringIO(input5))
    slow5 = result5["slow_requests"]
    assert len(slow5) == 10, f"Test5 slow count fail: {len(slow5)}"
    # 验证降序
    lats = [item["latency"] for item in slow5]
    assert lats == sorted(lats, reverse=True), f"Test5 not sorted: {lats}"
    # 验证最大10个
    expected_lats = list(range(1020, 1000, -1))[:10]  # 1020,1019,...,1011
    assert lats == expected_lats, f"Test5 latency mismatch: {lats}"
    print("Test 5 (slow requests limit and sort) passed.")

    # Test 6: 错误率小数位
    lines6 = [
        "2026-01-01T00:00:00Z GET /test 200 100ms tenant=t1",  # good
        "2026-01-01T00:00:01Z GET /test 404 100ms tenant=t1",  # error
        "2026-01-01T00:00:02Z GET /test 500 100ms tenant=t1",  # error
        "2026-01-01T00:00:03Z GET /test 200 100ms tenant=t2",  # good
        "2026-01-01T00:00:04Z GET /test 503 100ms tenant=t2",  # error
        "2026-01-01T00:00:05Z GET /test 200 100ms tenant=t2",  # good
    ]
    input6 = "\n".join(lines6)
    result6 = process_logs(io.StringIO(input6))
    # t1: 3 requests, 2 errors => 2/3 = 0.666666... => round=0.667? wait 2/3=0.666666.. round 0.667
    # t2: 3 requests, 1 error => 1/3=0.333333... round=0.333
    rates = result6["tenant_error_rates"]
    assert rates["t1"] == round(2/3, 3), f"Test6 t1 rate fail: {rates['t1']}"
    assert rates["t2"] == round(1/3, 3), f"Test6 t2 rate fail: {rates['t2']}"
    # 确保三位小数精度，但round后是浮点数，比如0.667, 0.333
    print("Test 6 (error rate precision) passed.")

    # Test 7: 路径含多个问号? (不重要)
    # 测试parse_line单独? 集成在基础测试中已测，不做专门测试。
    # 测试租户不带等号情况
    line7 = "2026-01-01T00:00:00Z GET /api/test 200 100ms mytenant"
    parsed = parse_line(line7 + "\n")
    assert parsed is not None
    _, _, _, tenant, _ = parsed
    assert tenant == "mytenant", f"Test7 tenant fail: {tenant}"
    print("Test 7 (tenant without equals) passed.")

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return
    result = process_logs(sys.stdin)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(',', ':')))
    sys.stdout.write('\n')

if __name__ == "__main__":
    main()
```

这里检查一下：Test5中我们期待latency降序，我们构造的latency从1001到1020，随机顺序，乱序，但结果我们取排序后。我们构造的列表按顺序添加，但排序后按降序取前10，所以结果应该是正确。但我们在遍历append时不保证顺序？其实列表是按输入顺序append，但我们在最后对整个列表sort，所以顺序由排序决定，与输入顺序无关。如果要测试排序正确，我们最好在输入时打乱顺序，以确保我们排序正确；但也可以用某种顺序，我们测试结果是排序后的，所以可以用任何顺序。所以没问题。

我们Test5中预期lats = [1020,1019,...,1011] 因为总共20个，取前10最大。我们sort降序，前10应该是这些，所以我们断言。

注意：在代码中，slow_requests.sort(key=lambda x: -x[0]) 是降序，前10个取。所以Lats自然降序。所以测试通过。

我们也要测试当慢请求不足10个时，全部列出。我们在基础测试中已经有1个。

**关于错误率**：我们处理了0的情况，在空测试中未出现。错误率0.0，输出0.0。

**关于top_paths**：当count相同时，我们按路径字母升序。在Test4中我们有6个路径，其中count=1的有5个（path2到path6），按字母升序，所以top5应该包括path2,path3,path4,path5? 注意：我们总共有path0(3), path1(2), path2(1), path3(1), path4(1), path5(1) [索引2-5共4个路径？实际上我们有6个路径：0,1,2,3,4,5。我们给每个索引都加了，其中IP: path0 3次, path1 2次, path2 1次, path3 1次, path4 1次, path5 1次。所以count=1的有4个（path2,3,4,5）。而count=1的排序按字母：path2, path3, path4, path5（path的字符串排序，考虑数字字符在后面？路径字符串"/api/path2","/api/path3","/api/path4","/api/path5"确实是按数字增大顺序，因为字符'2','3','4','5'，所以顺序为path2,path3,path4,path5。所以取前5个应该是path0,path1,path2,path3,path4。path5被排除。所以期望正确。

注意：路径字符串排序时，按字典序，例如对于“/api/path10”会怎样？但这里没问题。

所以Test4期望正确。

**关于Test6**：2/3 = 0.666666..., round(2/3,3)=0.667。但我们在断言时用了round(2/3,3)来比较，确保精度一致。因为Python浮点数和round后可能产生同一数值，所以比较相等没问题。注意我们results中的错误率也是round后，所以相等。但是需要注意，浮点数比较可能因精度问题不相等？但round后应该是精确的二进制表示接近？但通常对于这些小数，0.667可以由round(0.666666...,3)得出，但与0.667不同？实际上round(2/3,3)产生0.667，存储为浮点数，大约是0.66700000000000004，但与另一个round(2/3,3)产生相同的浮点数，所以相等。但是如果我们手动写0.667，这个字面量也是精确的0.667000000000000...? 实际上十进制0.667不能精确表示为二进制，所以会有误差。但比较相等没问题，因为相同十进制字面量转换为相同浮点数。但这里我们通过round计算，应该与我们直接写0.667相等吗？可能不一定完全相等？但一般来说，round(2/3,3)和0.667应该是同一个浮点数（因为两者都是通过相同的十进制近似）。实际上，在CPython中，round(2/3,3)内部也同样使用浮点数，所以与0.667常量会有微小差异？但通常转换自相同的十进制表示，结果一样。所以在断言时，我们应该直接比较数值，可以用`abs(rates["t1"] - 2/3) < 1e-3`，但这里我们更严谨，可以用round(2/3,3)作为期望，或者更好使用Decimal？但为了简洁，我们断言相等，也许没问题。但为了稳定性，我们可以断言错误率字符串？但我们选择使用round(2/3,3)作为期望，所以期望也是通过round计算出，与results的数值应一致（因为计算结果相同）。所以相等没问题。

**注意**：Test6中错误率rates["t1"] = round(0.6666666666666666, 3) -> 0.667，我们期望值也是round(2/3,3)所以相等。

同样，rates["t2"] = round(0.3333333333333333, 3) -> 0.333，期望值一样。

所以断言OK。

**Test7**：测试parse_line不带等号的租户。直接调用parse_line，并检查tenant。注意，parse_line接受的行可以包含或不含换行。我们在调用时加上换行以测试。应该返回非None。注意，parse_line中对line做rstrip('\r\n')，所以带换行没问题。我们断言tenant == "mytenant"。同时我们也验证其他字段为合理值。但简单测试即可。

**注意**：我们直接调用了parse_line，她返回5元组。我们只检查tenant。

****补充测试**：测试p95计算精确性：例如N=3时，ceil(0.95*3)=ceil(2.85)=3, index2。

我们已经在基础测试中包含N=4，N=1等。可以再测试N=3。

我们测试：

lines_extra = [
    "line1 GET /a 200 100ms tenant=t",
    "line2 GET /a 200 200ms tenant=t",
    "line3 GET /a 200 300ms tenant=t",
]
p95应为300。因为N=3, index=2。

我们在Test中未包括，但可以加一个Test8。

类似地，测试N=2: 0.95*2=1.9 ceil=2 index=1 -> 较大的。

可以在Test8中涵盖。

但为了不过度增加test，可以添加。

增加Test8测试p95边界：

```python
# Test 8: p95边界
lines8 = [
    "2026-01-01T00:00:00Z GET /a 200 100ms tenant=t",
    "2026-01-01T00:00:01Z GET /a 200 200ms tenant=t",
    "2026-01-01T00:00:02Z GET /a 200 300ms tenant=t",
]
input8 = "\n".join(lines8)
result8 = process_logs(io.StringIO(input8))
assert result8["p95_latency_by_path"]["/a"] == 300
print("Test 8 (p95 boundary) passed.")
```

另外测试N=5: 0.95*5=4.75 ceil=5 index=4 -> 最大。

可以用N=5 easy。

但我们可以不测，因为原理一样。

但我们可以加。

由于测试发现足够，我可能会添加这个。

为了代码减少，可以省略，但考虑到代码行不多，可以加。

**注意**：测试中我们使用了硬编码的JSON输出格式，但我们测试时不检查JSON输出，只检查process_logs返回的字典。所以很好。

现在，在main中，如果传--test参数则运行测试并退出。

在测试时，我们import io在函数内部，避免全局导入（不过全局导入也可以）。

我们导入heapq了吗？没有。所以from collections import ... 已经包括。

**注意**：我们使用了sys.stdin.read()? 我们用for line in sys.stdin，所以迭代行。没有问题。

**注意**：对于Windows系统，可能换行符是\r\n，但Python的sys.stdin text mode会转换换行符为\n（通用换行）。所以line里的换行符是\n。所以我们rstrip('\r\n')仍然有效。

**关于输出JSON**：我们使用`separators=(',', ':')`，这将产生紧凑输出。但可能会使某些键值对间没有空格。这完全合规。但注意，如`"total_requests":7`这样输出。可以。

**关于ensure_ascii**: 不转义非ASCII字符。如果有中文路径，会直接输出。没问题。

**关于测试输出**：我们打印测试通过消息，测试失败则AssertionError会打印到stderr。这符合要求（没限制测试时输出）。所以OK。

**潜在问题**：我们在run_tests中使用了print输出，但在正式运行时不应有任何输出除了JSON。main中只输出JSON。所以测试模式不影响。

**关于内存**：我们的process_logs可能消耗大内存，但没关系。

**关于代码行数**：当前代码应该在300行以内。

**关于格式**：需要单文件，所以这是完整的。

现在，整理代码，消除可能的小错误。

检查：

- 在parse_line中，original_line = line.rstrip('\r\n') 后，split得到parts。如果原始行全是空格，split可能返回空列表，长度0<6，返回None。所以空行也算malformed。

- 注意：如果一行只有空格，例如`   `，split会返回[]，所以malformed。但也可以视为空行，算malformed。合理。

- 耗时ms解析：latency_str如"123ms"，latency_str[-2:]是"ms"，但我们用endswith('ms')检查，然后用int(latency_str[:-2])，但如果latency_str类似于"123ms "? 我们已经rstrip了末尾空白，所以没有空格。所以没问题。

- 注意：latency_str可能含有额外的空格？我们使用split已经分割，所以无内部空格。

- 状态码可能含有前导空格？无。

- 租户字段可能类似"tenant=a1"中间没有空格。

- 如果路径包含分号？不用处理。

- 在path.split('?')[0]中，如果路径没有?，则整个路径返回。

一点注意：如果有虚线等，正常。

- 在统计tenant_error_rates中，我们使用if status >=400。但HTTP状态码在400-499和500-599。遇到100-199? 可能不会。如果状态码大于等于600，也算错误？但标准没有，但我们也统计。

- 在round错误率时，我们使用`round(errs / total_count, 3)`，但如果是3位小数后为0.0005？round(0.0005,3)为0.0，但可能希望0.001。但精确值，可以。

- 对于`round(1/3,3)=0.333`正确。

- 对于0错误率，round(0,3)=0.0。

**现在确认字段**：`slow_requests`中，我们给每个条目包括original_line, path, latency。注意：我们返回也包含了latency（整数）。符合。

**规范检查**：p95_latency_by_path直接是一个对象，每个路径值是整数。

**规范要求**："p95定义为排序后向上取整位置。" 所以我们实现了ceil(0.95*N)计算。

注意：如果N=0（不可能），但我们不会遇到。

**慢请求**：耗时大于1000ms（不包括等于），我们的条件`latency > 1000`。

**测试**：我们测试了latency=1000不算，而1100算。符合。

**其他**：我们跳过了无法解析的行，计数malformed_lines。

**额外考虑**：如果状态码不是数字，我们跳过了。但如果状态码是字符串但可以转换，我们转换。如果无法转换，跳过。

**租户解析**：我们采用了等号后取值。但如果有多个等号，如"tenant=a=b"，我们取等号后的所有，即"a=b"。但通常不会。这样也许可行。

**时间格式**：我们不验证ISO时间格式，但可以包含任意字符串。不过格式错误也不影响统计。但如果时间格式乱，导致原始行某些字段错位？例如时间包含空格？ISO时间通常没有空格。所以没问题。

**考虑日志行可能使用空格分隔，但时间段内如果时间有空格（日期与时间之间有空格?）但ISO格式通常为"2026-05-01T12:03:18Z"无空格。所以安全。

**考虑开发环境**：windows/unix兼容。

**最后**：注意在输出JSON时，我们使用了`sys.stdout.write`，并手动添加换行。如果使用`print`，会自动加换行，但print会多一个空行？print默认添加换行。所以用sys.stdout.write控制，但最后加换行。

**关于测试时使用的输入**：确保每行末尾都有换行？我们构造的字符串使用三重引号，最后一行后我们添加了换行？在基础测试中最后一行后没有加换行，但StringIO的readline可以正常处理最后一行（没有换行）。但我们的for line in stream会正常读取到最后一行（可能没有换行）。但我们的parse_line中用rstrip('\r\n')，所以没问题。所以测试通过。

**关于Test6**：输入没有末尾换行，但process_logs处理正常。

**关于Test5**：构建20行，连接插入`\n`，最后一行的末尾也可能没有换行，但没问题。

**关于Test7**：我们手动调用parse_line传入字符串带换行，加上`+ "\n"`确保。

**关于Test8**：加入测试p95边界。

我们也在Test8后重新print。

我们现在决定将Test8加入。

**代码封装**：我们还可以将run_tests中的多个测试拆分为独立函数，但为了简单，我们保留现在。

**潜在Bug**：在计算p95时，我们使用了path_latencies的keys()和items()，但如果在处理过程中出现路径键，没问题。

**性能**：使用Counter和defaultdict高效。

**最后步骤**：写完整的代码，确保不超过1000行。

现在，检查代码是否完整，调整细节。

**注意**：在run_tests中，我们直接使用了parse_line函数，但它在模块中已经定义，所以没问题。

**检查所有import**：只有标准库。我们在最前面import sys, json, math, collections。在run_tests中import io，因为只在测试中使用，所以放函数内部以避免导入未使用的？但也可以放在模块顶部。如果在顶部导入`io`，模块加载时会导入，但不会影响正常模式。这样也可以，但为了整洁，可以全局导入。不过最好按需。但题目未禁止。我们选择在测试函数内部导入，避免正常模式不需要io被导入。不过io是轻量，无所谓。我倾向于在文件顶部导入io，如果需要。但import io在模块顶部，也不是第三方。所以我们可以全局导入io：`import io`。然后run_tests中就不用再import。但注意，process_logs用到StringIO吗？不用。所以可以全局import，但不是必须。我选择在run_tests内部导入io，保持清晰。

但我们要考虑代码风格的一致性：也可以在顶部导入io。

为了简洁，我们选择在顶部只导入必要项：sys, json, math, from collections import Counter, defaultdict。

然后在run_tests内部 import io。

**关于`--test`参数**：调用run_tests后，我们直接return。但注意，这样程序就退出了，不会继续处理stdin。

**关于argparse**：我们没有使用，直接检查sys.argv[1]，简单。

**多参数情况**：如果用户执行 `python log_analyzer.py --test something`，我们的检查只是sys.argv[1]=='--test'，会忽略后面参数。只当--test是第一参数时运行测试。这合理。

**安全性**：无。

**现在编写最终代码**。可能会有一些小修改。

在Test5中，我们检查了降序。我们没有打乱初始顺序，所以排序后降序。但为了确保排序正确，我们在断言中检查lats == sorted(lats, reverse=True)并匹配期望列表。符合。

**注意**：在Test5中，我们设置的latency从1001到1020，所以升序添加。但我们在process_logs中会按输入顺序追加到slow_requests，然后整体排序降序取前10，所以结果中latency降序，前10是1020-1011。所以断言正确。

**但是**我们需要确保在期望列表生成时，list(range(1020, 1000, -1))[:10]得到[1020,1019,...,1011]。这是降序。

**Test6**：我们用于测试错误率小数。注意：t1: errors=2, total=3 => 2/3≈0.6666667， round到三位是0.667。不是0.666！因为四舍五入，第三位是6（因为第四位是6），所以0.667。所以断言中使用round(2/3,3)作为期望，我们得到0.667。所以正确。

**Test7**：测试无等号租户，我们直接调用parse_line并传入带换行的行。注意，我们在parse_line中original_line = line.rstrip('\r\n')，所以传入"\n"会被去掉，得到原始行"..."。assert tenant == "mytenant"。因为租户字段是"mytenant"，没有等号，直接等于。所以正确。

**Test8**：测试p95边界。

还需测试：当路径的耗时列表为空？但不可能。

**其他测试**：测试耗时ms后缀缺少或乱起八糟的，在malformed测试中顺便测了。

**测试错误率精确度**：我们可以测试更多。

**注意**：错误率保留三位小数，如果结果是0.0005? round(0.0005,3) = 0.0，因为四舍五入到千分位为0.000？实际上，0.0005四舍五入保留三位小数，看第四位是5，所以变0.001？对，round(0.0005, 3)实际上应该返回0.001? 但Python的round使用银行家舍入？round(0.0005, 3)在Python中是0.001？我们来推理：0.0005 = 5e-4，保留三位小数，即小数点后三位，第四位是5，进位，所以0.001准确。但是浮点数表示可能0.0005无法精确，所以结果可能略微不同。但这不是我们的测试范围。相信基本正确。

**整体代码**：我们完成。

现在我们整理代码并加入上述Test8。

我将调整run_tests，在Test7后加入Test8。

添加Test8：

```python
    # Test 8: p95边界（N=3）
    lines8 = [
        "2026-01-01T00:00:00Z GET /a 200 100ms tenant=t",
        "2026-01-01T00:00:01Z GET /a 200 200ms tenant=t",
        "2026-01-01T00:00:02Z GET /a 200 300ms tenant=t",
    ]
    input8 = "\n".join(lines8)
    result8 = process_logs(io.StringIO(input8))
    assert result8["p95_latency_by_path"] == {"/a": 300}, f"Test8 p95 fail: {result8['p95_latency_by_path']}"
    print("Test 8 (p95 boundary) passed.")
```

**注意**：Test8仅有一个路径，所以字典只有一个键。

**考虑有多个租户的错误率**：我们已经测试了。

**现在代码完成**：整合所有。

**是否需要对process_logs返回的字典键排序？** 我们在返回时已经对status_counts, p95, tenant_error_rates进行了dict(sorted(...))。但对于tenant_error_rates，如果租户为空字符串，排序没问题。

对于top_paths，我们是列表，顺序固定。

slow_requests列表顺序固定。

**关于输出样例**：未提供，但依据要求。

**最后**：注意，我们可能需要在进程结束时刷新输出，但write后自动。

**可能的改进**：如果输入流不带缓冲？不需要。

**现在写最终代码**。

我们来写完整的代码，包括模块docstring（可选）。

我将在文件开头添加简要说明。

确保代码质量，注释清晰。

注释可以根据需要。

但代码行数不超过1000，所以没问题。

**潜在错误**：在parse_line中，我们假设字段数至少6，但如果一行中有额外字段（比如7个），我们只取了前6，并忽略后面。但是，这可能导致路径包含空格被当作多个字段？本来日志格式没有路径包含空格的情况。但如果日志在第3个字段路径中包含空格（不可能），那我们的split会将路径分为多个，造成解析错误。但按格式规范，假设没有空格。所以安全。

但是，如果一行中由于错误导致出现超过6个字段（比如路径中包含空格且切割），我们只取前6，丢失后续可能的关键信息，但解析为成功。这可能导致错误行被当作有效，意味着会污染统计。但这是容错问题。要求“跳过无法解析的行”，如果一行存在明显格式错误（例如路径异常），可能无法检测，但我们可以增加一些检查，比如确认方法等。但为了简化，我们相信输入基本正确，我们只检查基本条件。

也许更安全的做法：确认字段数量和确认方法是标准HTTP方法等。但题目没有要求，所以保持。

**我们还可以检查状态码范围（100-599）? 可以但忽略。

**验证时间格式**：可以尝试解析，但增加复杂性。

**我们决定保持当前方式**。

**关于** "路径可能包含查询参数，例如 /api/orders?page=2，统计时应去掉查询参数。" 我们已做到。

**关于** P95定义：排序后向上取整位置。我们在代码中用math.ceil实现。

**关于** 慢请求：耗时大于1000ms的前10条，按耗时降序。我们返回的是降序列表。

**关于** tenant_error_rates 保留三位小数：我们用round，但注意Python round处理边缘情况有坑，但可以接受。

**关于** 输出JSON：不能包含注释或额外文字。

测试时，打印一些输出，但只在测试模式，正常模式不打印。

**现在，编写最终的`log_analyzer.py`。**

**检查**：在run_tests中，我们在Test5里生成了20行，并验证了慢请求，但注意我们在生成时每个请求耗时不同，且都在200状态码，所以没有错误率问题。正确。

**测试8**：还测试了p95，没问题。

**测试4**：检查top_paths超过5个时截断。

还缺少测试：状态码分类统计，我们已在Test1中验证。

**测试slow_requests包含多个字段顺序**。

**考虑可能路径末尾有空格？我们split会处理，但原始行保留，所以没问题。

**考虑**：在慢请求的原始行，我们期望包含查询参数？在我们的基础测试中，慢请求原始行是"2026-05-01T12:03:23Z GET /api/orders 200 1100ms tenant=a2"，没有查询参数。如果有查询参数，原始行包含查询参数，但路径字段会是去参的。所以慢请求条目的path字段是去参的路径，原始行保留原始行。所以符合要求：“保留原始行、路径、耗时”。所以我们的处理正确。

**实现细节**：我们在慢请求列表的元素是(latency, original_line, clean_path)。所以output的path是clean_path，original_line是原始行(去换行符)。所以正确。

**注意**：如果原始行中包含查询参数，在慢请求的path字段中已经被去除。这满足题目要求（slow_requests中包含路径，应该是去参路径？题目描述：“保留原始行、路径、耗时”。这里的路径应该是规范化后的路径（去参）还是原始路径？从上下文看，统计时路径应去掉参数，所以在slow_requests中，文档说`slow_requests`：耗时大于1000ms的前10条，按耗时降序，保留原始行、路径、耗时。将路径单独列出来。所以这个`路径`应该也是去掉查询参数之后的，与整体一致。所以我们使用clean_path。在示例中没有明确，但合理。所以我们就这样。

**检查其他统计**：top_paths使用clean_path，p95使用clean_path。

**所以一致**。

**最后，确认在输出中，p95_latency_by_path使用clean_path作为键。

**关于tenant_error_rates**：我们使用从租户字段解析出的tenant作为键。

**关于malformed_lines**：计数。

**现在我们编写最终代码，并逐步验证。**

**也许还需要处理一行中可能有多余的空格？split()默认以任何空白分割，包括空格和tab，会忽略多余空白。所以只要字段连续，没问题。

**我们测试过一些情况，没有发现问题。

**还可以增加测试：路径中有多个?符号，比如`/api/data?key=value?extra`，split('?')[0]只取第一段，所以路径是`/api/data`。但也许有效。

**现在，编写完整代码。

**为了避免用户错误，我们确保main可以处理KeyboardInterrupt等，但不需要。

**在main中，我们使用sys.stdin，如果stdin是交互式，程序会等待输入。但使用时应重定向输入，否则它会等待键盘。这没问题。

**现在，我写出最终代码。**

**我计划按照之前的设计写出，并考虑一些细节优化。**

**最后检查代码行数**：确保不太长。

**代码会包含注释，以解释函数。**

**注意事项**：不要在输出时打印额外信息。

**任务要求"输出一个 JSON 对象"，所以没有要求缩进。所以紧凑输出可接受。

**现在，开始写完整代码。
````

## Assistant

````markdown
```python
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
```
````
