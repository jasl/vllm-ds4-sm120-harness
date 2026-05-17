# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 200.840946
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 442, "total_tokens": 34425, "completion_tokens": 33983, "prompt_tokens_details": null}`
- Prompt tokens: 442
- Completion tokens: 33983
- Total tokens: 34425

## Prompt

```markdown
请使用 Python 3 标准库编写一个单文件 HTTP API 服务，文件名假定为 `server.py`，不得使用 Flask/FastAPI/Django 等第三方库，总代码不超过1000行。

任务：实现一个小型库存预约服务，用于管理商品库存和短时预约。

数据要求：使用内置 `sqlite3` 持久化，首次启动自动建表。商品字段：`id`、`name`、`stock_total`、`stock_available`。预约字段：`id`、`item_id`、`quantity`、`status`、`expires_at`、`created_at`。

API 要求：
1. `GET /items`：列出商品和可用库存。
2. `POST /items`：新增商品，JSON 参数 `name`、`stock_total`。
3. `POST /reservations`：创建预约，JSON 参数 `item_id`、`quantity`、`ttl_seconds`。库存不足时返回409。
4. `POST /reservations/{id}/confirm`：确认预约，状态变为 confirmed，不再释放库存。
5. `POST /reservations/{id}/cancel`：取消预约，释放库存。
6. 每次请求前清理已过期且仍为 pending 的预约并释放库存。

工程要求：
- 正确处理并发请求下的库存一致性，可使用事务和线程锁。
- 返回 JSON；错误响应包含 `error` 字段。
- 包含一个 `if __name__ == "__main__"` 启动入口，默认监听 `127.0.0.1:8080`。

输出要求：只输出完整 Python 代码，不要解释。
```

## Reasoning Content

````text
我们被要求编写一个单文件HTTP API服务，使用Python 3标准库，不支持第三方库，使用sqlite3持久化，代码不超过1000行。

我们需要实现一个小型库存预约服务，包括商品管理（列出、新增）和预约管理（创建、确认、取消）。关键点是并发控制和库存一致性，需要使用事务和线程锁。每次请求前清理过期且仍为pending的预约并释放库存。

我们需要一个HTTP服务器。Python标准库有`http.server`模块，我们可以基于`BaseHTTPRequestHandler`和`HTTPServer`来实现REST API。

设计：
- 使用sqlite3作为持久化存储。首次启动自动建表。
- 数据库文件？没有指定，我们可以使用`inventory.db`或内存？最好文件持久化，但未指定取什么名字，就`inventory.db`。
- 商品表：items(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, stock_total INTEGER NOT NULL, stock_available INTEGER NOT NULL)
- 预约表：reservations(id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER NOT NULL, quantity INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending', expires_at TEXT NOT NULL, created_at TEXT NOT NULL)
  我们使用Python的datetime将时间存储为ISO格式字符串。
- 状态：pending, confirmed, cancelled （但我们可能不需要单独存cancelled？但为了记录，可以保留）。当取消时直接更新status为'cancelled'。或者直接删除？但是为了不丢失记录，我们保留，释放库存。
- 过期时间：expires_at是TTL秒数加上创建时间。

API设计：
- GET /items: 返回所有商品及其可用库存。
- POST /items: JSON body: {"name": "...", "stock_total": int}，新增商品。注意：stock_total和stock_available都设为stock_total。
- POST /reservations: JSON body: {"item_id": int, "quantity": int, "ttl_seconds": int}。检查库存是否足够（stock_available >= quantity），足够则创建预约，状态为pending，expires_at = now + ttl_seconds, created_at = now。减少stock_available。如果库存不足返回409。
- POST /reservations/{id}/confirm: 将指定预约状态改为confirmed。注意：确认后不应释放库存（即已占用库存不再可释放）。确认的逻辑应该是：预约占用库存，确认后库存不恢复。所以确认时不需要调整库存（因为已占用）。但需要确保预约存在且是pending状态，然后改为confirmed。
- POST /reservations/{id}/cancel: 取消预约：将状态改为cancelled，释放库存（增加stock_available）。
- 每次请求前清理过期且仍为pending的预约并释放库存。这意味着在每个请求处理开始时（或在请求路由时），我们执行清理函数：查找所有 status='pending' 且 expires_at < now 的记录，将它们状态改为expired（或直接删除？但记录保留？题目没有说保留历史，但我们可以保持记录，标志为'expired'或删除同时释放库存。为简单，我们可以将过期预约状态设为'expired'，并释放库存。这样记录保留。或者干脆删除？但题目没有要求保留过期记录，但释放库存是必须的。我们可以选择更新status='expired'并释放库存。或者删除记录。为了数据完整性，更新为expired并释放库存。注意：如果库存已经释放，商品可用库存会增加。
- 并发控制：使用线程锁确保数据库操作串行化。对于每个请求，我们可以使用一个全局锁（threading.Lock）在访问数据库时获取。对于sqlite3，我们可以开启事务，但多线程访问时可能需要序列化。我们可以使用`check_same_thread=False`，并设置一个全局锁来保护数据库操作。或者使用Python的`queue`? 但标准库没有连接池。简单使用`sqlite3.connect`加锁。

注意：sqlite3默认在一个线程中创建连接只能在同一个线程使用。我们需要设置`check_same_thread=False`以便在不同线程使用。但同时要保护写操作，避免并发写冲突。我们可以使用一个锁（threading.Lock）来同步所有数据库操作（读/写）。但是读操作也可以并发？如果只是读，可以不加锁，但为了简单，统一加锁。性能要求不高。

或者更精细地：使用写锁，读可以并发（如果使用多个连接或连接复制）。但为了简化和确保一致性，我们使用全局锁。

另外需要注意的是：清理过期预约也需要在事务中更新库存。

请求处理流程：
1. 对于每个请求，先执行清理过期预约（如果数据库没锁，可能会和正在进行的操作冲突，所以应该在锁内执行清理和后续操作？但清理可能也需要在事务中。我们可以先加锁，执行清理，然后执行具体操作，释放锁。但如果在清理和具体操作之间锁释放，可能会不一致。所以最好整个请求处理在同一个锁保护下。但这样请求队列化，性能下降。但考虑到演示，可以接受。

我们可以在一个请求处理开始时获取锁，执行清理，然后执行具体API逻辑，完成后释放锁。如果是GET操作，整个读加锁也可以。

更高效的方式：使用sqlite3的WAL模式，并允许读写并发。但为了确保库存一致性和防止超售，我们需要事务隔离。我们可以使用`BEGIN IMMEDIATE`事务，这样会在写时获取写锁。但多线程共享同一个连接时，sqlite3默认会序列化（通过内部锁），前提是设置了`check_same_thread=False`和`timeout`。实际上，如果多个线程使用同一个连接，sqlite3模块会在数据库操作前获取连接上的锁（threading.Lock），所以是线程安全的。但是我们需要确保事务的原子性，如果多个线程同时执行BEGIN和操作，可能会交错？实际上，sqlite3连接内部使用一个锁来同步访问，但如果我们手动控制事务，需要在同一个连接上串行化。如果使用共享连接，sqlite3模块本身不是完全线程安全的？根据文档，sqlite3模块不是线程安全的，但通过使用`check_same_thread=False`并确保一次只有一个线程使用连接，否则可能出错。实际上，更常见的做法是每个线程创建一个独立的连接，但使用共享的锁来协调写操作。或者使用连接池，但标准库没有。最简单的方案：创建一个全局连接，并使用一个全局锁来保护对数据库的所有访问（包括读）。这样可以确保一致性，但会成为瓶颈。

我们使用一个全局锁（threading.Lock），在每次请求处理函数开始时获取锁，执行清理和操作，然后释放锁。这样所有请求串行化。对于原型来说足够。

另外，我们还需要解析URL路径和方法，根据路由调用处理函数。

实现方式：
- 继承`BaseHTTPRequestHandler`，覆盖`do_GET`, `do_POST`方法。
- 根据URL路径和HTTP方法分发到各逻辑函数。
- 返回JSON格式的数据，状态码正确。
- 错误处理：返回JSON包含`error`字段。

我们将编写以下主要函数：
- `init_db()`: 创建表（如果不存在）。
- `cleanup_expired()`: 查找所有过期pending预约，更新状态为expired，释放库存。必须在事务中执行。
- `handle_items_get()`: 返回所有商品列表。
- `handle_items_post()`: 解析JSON，插入新商品。
- `handle_reservations_post()`: 解析JSON，检查库存，插入预约，减少库存。
- `handle_reservations_confirm(res_id)`: 确认预约。
- `handle_reservations_cancel(res_id)`: 取消预约。

注意：URL路径解析：我们需要提取路径中的ID。例如`/reservations/1/confirm`，我们需要匹配模式`/reservations/(\d+)/confirm`和`/reservations/(\d+)/cancel`。

在`do_GET`中，处理`/items`。
在`do_POST`中，处理`/items`、`/reservations`、`/reservations/{id}/confirm`、`/reservations/{id}/cancel`。

另外，对于无效路径或方法，返回404。

对于JSON请求体，使用`json.loads`解码，并处理错误返回400。

对于必要参数缺失或类型错误，返回400。

数据库操作使用参数化查询防止SQL注入。

时间处理：使用`datetime.datetime.utcnow()`或`datetime.now(timezone.utc)`，存储为ISO格式字符串。

过期时间：expires_at = created_at + timedelta(seconds=ttl_seconds)

当清理时，比较expires_at和当前时间。

注意：由于每次请求前清理，我们需要考虑清理操作是否应该与后续操作在同一事务中？例如，清理释放了一些库存，然后创建预约时看到库存可用。应该在同一事务中保证原子性？清理和后续操作可以是两个事务，但如果有并发，一个请求清理后另一个请求可能占用库存。但因为我们使用全局锁同步，整个处理过程（清理+操作）在锁内完成，所以可以视为串行，所以可以分开事务或者在同一事务中。我们可以在锁内使用连接执行事务，但注意如果事务开始后没有提交，其他操作无法进行，因为锁已经持有。所以我们可以将清理和后续操作包含在单个事务中，或者两个独立事务。但为了简单，我们可以使用多个事务，因为锁已经确保不会交叉。但是，如果在清理事务提交后，下一个操作事务开始前，锁释放，但因为有全局锁，我们不会在锁释放前执行其他操作（因为我们还在锁内）。所以安全。

因此我们可以：在锁内，先执行清理（使用一个事务），然后执行具体API操作（另一个事务），然后释放锁。这样清理和操作之间是隔离的，但都是同一个线程执行，所以不会有不一致性。但是如果在清理和操作之间数据库有一点时间，其他线程无法介入（因为锁被持有），所以没问题。

我们可以考虑将整个处理逻辑放在一个事务中，但有些操作（如GET）只需要读，可以不用事务。

我们决定：在锁内执行所有数据库操作，使用连接，并由我们控制事务（自动提交或手动）。为了简化，使用连接对象的`execute`和`commit`，默认是在autocommit=False？实际上，Python的sqlite3模块默认是自动提交模式（每次执行后立即提交），除非开始一个事务。我们可以显式地调用`BEGIN`和`COMMIT`，或者使用`conn.execute`后自动提交（当不在事务中时）。但为了确保原子性，我们使用`conn.execute("BEGIN")`开始事务，完成后`conn.commit()`。或者使用`conn.execute("BEGIN IMMEDIATE")`。不过，使用`conn.execute("BEGIN")`后，后续操作不会自动提交，直到`commit()`。

在锁内，我们使用同一个连接（全局）。注意：由于全局锁同步，我们不需要担心多线程同时使用连接，因为只有持有锁的线程能访问数据库。所以即使连接不是线程安全的，也安全了。

但是，要注意sqlite3模块的`Connection`对象在未加锁的多线程使用中是不安全的（如果check_same_thread=False）。所以我们仍然需要锁。我们使用全局锁。

我们也可以使用单个连接并在每个请求中创建新连接，但创建连接开销小，且可以避免线程安全问题。但使用全局锁也是必要的。为了简单，我们使用单个全局连接，并在每个请求中使用它（在锁内）。但要注意，如果在锁内使用同一个连接，sqlite3的`execute`会检查它是否属于当前线程？如果设置了check_same_thread=False，则不会检查。所以我们创建连接时设置check_same_thread=False。同时设置`isolation_level=None`以允许手动控制事务。

另外，我们可能还需要设置数据库的`timeout`，以避免锁等待。但我们在锁内访问，所以只有一个线程操作，所以不会冲突。

更好的做法：使用`sqlite3.connect`时指定`timeout`以等待内部锁。但因为我们外部有锁，内部也可能有锁。sqlite3内部有一个锁，当多个线程共享连接时，内部也会序列化（如果check_same_thread=False）。但我们外部已经串行化，所以内部锁很少冲突。

为了简单，我们采用全局锁+全局连接（check_same_thread=False）的方式。

注意：清理操作可能会更新多行，需要事务。

代码结构：

1. 导入必要的模块：http.server, json, sqlite3, threading, re, datetime, os等。
2. 定义全局变量：DB_FILE = "inventory.db"；db_lock = threading.Lock()；connection = None（初始化时创建）。
3. 函数：get_db() 返回全局连接（或创建）。但我们可以在init_db中创建并赋值给全局变量。
4. 函数：init_db() 创建表，如果不存在。
5. 函数：cleanup_expired() 执行清理。需要传入连接，或者在内部使用全局连接。
6. 定义请求处理类：InventoryHandler(BaseHTTPRequestHandler)
   - 属性：server_version等。
   - do_GET: 路由到具体函数。
   - do_POST: 路由到具体函数。
   - 辅助：parse_json_body() 从rfile读取并解析JSON，返回字典或None。
   - 辅助：send_json(data, status=200): 设置headers，content-type为application/json，写入json.dumps(data)。
   - 辅助：send_error_json(msg, status): 发送包含error字段的JSON。
   - 路由逻辑：

GET:
   if path == "/items": handle_items_get()
   else: send_error(404)

POST:
   if path == "/items": handle_items_post()
   elif path == "/reservations": handle_reservations_post()
   elif match pattern /reservations/(\d+)/confirm: handle_reservations_confirm(id)
   elif match pattern /reservations/(\d+)/cancel: handle_reservations_cancel(id)
   else: send_error(404)

在路径匹配时，注意处理路径可能带有/结尾，但不需要。

7. 各处理函数实现（在锁内执行）：
   - 获取全局锁。
   - 调用cleanup_expired(conn)。
   - 执行具体操作（使用conn）。
   - 在锁内最后提交事务（如果需要），或者我们每个操作单独提交。
   - 我们使用`conn.execute("BEGIN")`开始事务，然后执行操作，最后`conn.commit()`。但如果只是SELECT读，可以不用事务？但为了一致性，读可以不用事务，但是读的时候可能和其他事务冲突？由于有全局锁，读时不会有写操作，所以读可以单独执行（自动提交模式）。但为了统一，我们也可以在锁内使用自动提交？默认是自动提交，但如果我们手动begin，则不会自动提交。我们可以设置`isolation_level=None`，然后手动控制。如果我们只是想读，我们不需要begin，直接execute就会自动提交。但如果在同一个连接中，并且之前有begin未提交，则会报错。所以我们最好在每次操作前后确保事务状态完成。我们可以使用`conn.isolation_level`和手动begin/commit。或者，我们可以使用`conn.execute`的context manager？不，我们手动控制。

更简单：我们使用`conn.execute`在自动提交模式下，每个语句自动提交。对于需要事务的多语句操作（如创建预约同时减少库存），我们需要使用`conn.execute("BEGIN")`和`conn.commit()`来确保原子性。对于读，自动提交没问题。所以我们需要在写操作中使用事务。

在锁内，由于没有其他线程同时访问连接，所以即使使用自动提交，每个语句单独提交也是安全的，但可能中途崩溃导致部分更新？比如创建预约时减少库存后，如果创建预约失败（但我们的操作是连续的，不会出现部分失败，因为如果插入失败，库存减少可以回滚？但使用自动提交，减少库存立即提交，之后插入可能失败，导致库存不一致。因此，必须使用事务来保证多个写操作的原子性。所以写操作必须在一个事务中，即先BEGIN，执行所有语句，再COMMIT；如果任何错误，ROLLBACK。

所以，我们对写操作使用事务，读操作可以不用事务。

注意：清理操作也是写操作（修改库存和预约状态），也需要事务。

因此，在每个处理函数中（在锁内）：
- 对于写操作，我们begin事务，执行清理（但清理也是一个事务？我们可以将清理和后续操作放在同一个事务中，以保证原子性？例如，清理释放了一些库存，紧接着创建预约使用这些库存，如果清理成功但创建失败，则可以回滚，包括清理的释放？但清理释放库存应该是永久的，不应该回滚？但如果我们回滚整个事务，则预约失败，同时过期预约的释放也被回滚，这是不好的。所以清理应该在外部事务单独提交？或者，我们可以先执行清理（独立事务提交），然后开始新事务执行后续操作。这样，如果后续操作失败，清理已经生效。这更合理。所以，处理函数：先执行清理（在单独事务中），然后执行主要操作（另一个事务）。因为锁保护，所以安全。

因此流程：
   1. 获取锁。
   2. 执行清理（调用cleanup_expired，自动提交或自身事务）。
   3. 执行主要操作（读或写，写使用事务）。
   4. 释放锁。

注意：如果清理本身出现异常，我们可以忽略或记录。但必须确保清理成功才能操作？如果不成功，可能数据库有问题。我们直接让异常传播会返回500错误。

我们可以在锁外先清理？但为了清理的及时性和与其他操作的一致性，应该在锁内清理。但注意：如果多个请求同时在等待锁，第一个请求清理了过期，其他请求就不需要再次清理，但也无所谓，因为清理是幂等的。我们可以在每个请求开头清理。

注意：清理过期预约可能每次都会执行，可能会导致性能问题，但可以接受。

另外，我们需要考虑数据库连接初始化：在`__main__`中创建连接并初始化表，然后启动服务器。

启动入口：
```python
if __name__ == "__main__":
    # 初始化数据库
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 使行可像字典访问？
    init_db(conn)
    # 设置全局连接
    # 注意：我们需要在请求处理类中能够访问到连接和锁。我们可以通过模块全局变量。
    # 或者将连接和锁作为类属性或全局变量。
    # 简单：在模块顶部定义全局变量 conn, lock。
    # 在初始化时赋值。
    # 启动服务器
    server = HTTPServer(('127.0.0.1', 8080), InventoryHandler)
    server.serve_forever()
```

但如何让Handler访问到conn和lock？我们可以定义为模块全局变量，Handler通过模块全局引用。或者通过类属性设置。简单使用模块全局。

注意：BaseHTTPRequestHandler会为每个请求创建一个新实例，但父类BaseHTTPRequestHandler的实例方法会访问模块全局变量。

所以，我们在模块级别定义：
```python
db_lock = threading.Lock()
db_conn = None
```

在initialize时设置db_conn。

注意：`serve_forever`运行在主线程，每个请求进入会创建新线程（BaseHTTPServer默认是单线程，阻塞处理？BaseHTTPServer是单线程的，一次只能处理一个请求！实际上，http.server.HTTPServer是同步的，它使用`serve_forever`在一个线程中处理请求。所以实际上不会有两个请求同时处理，因此根本不需要线程锁！因为BaseHTTPServer是单线程的。但是题目要求“正确处理并发请求下的库存一致性”，暗示可能存在并发，但标准库的HTTPServer是单线程的，只能顺序处理。如果我们想支持并发，我们可以使用`ThreadingHTTPServer`或者`ThreadingMixIn`。在Python 3中，`http.server`有`ThreadingHTTPServer`（从3.7开始），它基于`ThreadingMixIn`，可以多线程处理请求。所以我们应该使用`ThreadingHTTPServer`来实现并发。或者我们可以使用`ThreadingMixIn`混合。这样多个请求可以并发。所以我们需要使用多线程服务器。推荐使用`HTTPServer`但混合`ThreadingMixIn`。或者直接使用`ThreadingHTTPServer`（如果版本足够）。为了兼容性，我们可以手动创建一个`ThreadingHTTPServer`类。

因此，我们需要：`from http.server import ThreadingHTTPServer` （Python 3.7+ 新增）。或者我们使用`from socketserver import ThreadingMixIn`和`from http.server import HTTPServer`混合。

最简单：使用`from http.server import ThreadingHTTPServer`，如果导入失败回退到混入。

但题目说Python 3标准库，应该包含ThreadingHTTPServer。我们直接使用。

这样就会多线程处理，所以需要线程锁。

所以，我们将使用`ThreadingHTTPServer`。

然后数据库连接和锁需要是全局的。

现在具体实现：

一、数据库表创建：

```sql
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    stock_total INTEGER NOT NULL,
    stock_available INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items(id)
);
```

我们不需要显式外键，但可以加上。

二、函数：init_db(conn)

```python
def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
```

三、cleanup_expired(conn)

```python
def cleanup_expired(conn):
    now = datetime.datetime.utcnow().isoformat()
    cursor.execute(...)
    # 选择过期pending预约
    # 但是注意：我们需要更新每条记录对应的库存。一种方法是先查出过期预约，然后对每个释放库存。可以在一个事务中完成。
    # 我们可以用一条UPDATE语句？不能直接，因为需要更新items表的stock_available。
    # 所以我们使用SELECT查询所有过期pending预约，然后对于每个，更新items增加stock_available，然后更新预约状态为expired。
    # 所有这些应该在一个事务中。
    # 注意考虑并发？但已经有锁。
    cur = conn.execute("BEGIN")
    try:
        cur = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
        expired = cur.fetchall()
        for row in expired:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (row['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
```

注意：建议使用参数化查询。同时我们使用conn.row_factory = sqlite3.Row以便通过列名访问。

但row_factory设置后，fetchall返回的是Row对象，可以像字典一样访问。

我们也可以避免BEGIN/COMMIT，使用conn.execute直接UPDATE? 但需要原子性，所以使用事务。

四、处理函数实现：

在锁内，先清理，再操作。

锁：在每次do_GET或do_POST时，我们获取锁，然后处理，最后释放锁。但注意do_POST中可能调用多个函数，但都应在锁内。

我们可以这样设计：在do_GET和do_POST中，获取锁，调用清理，然后根据路径调用具体的处理方法（不带锁），最后释放锁。这些具体的处理方法应该使用全局连接并可能开始事务。

具体处理方法定义在Handler中，作为实例方法，它们需要访问请求和连接。

我们也可以将锁的获取放在具体的处理函数中，但代码重复。更好的方式是在do_GET/do_POST中统一加锁。

但是要注意：锁必须在try-finally中释放。

此外，清理操作本身需要事务，所以应该在同一个连接上执行。我们统一使用全局连接。

五、具体处理函数：

5.1 handle_items_get()

```python
def handle_items_get(self, conn):
    cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
    items = [dict(row) for row in cursor.fetchall()]
    self.send_json(items)
```

注意：我们需要确保每个处理函数在锁内，但conn参数传递全局连接。

5.2 handle_items_post()

```python
def handle_items_post(self, conn):
    body = self.parse_json_body()
    if body is None:
        return
    name = body.get('name')
    stock_total = body.get('stock_total')
    if not name or stock_total is None:
        self.send_error_json("Missing required parameters", 400)
        return
    try:
        stock_total = int(stock_total)
    except (TypeError, ValueError):
        self.send_error_json("stock_total must be an integer", 400)
        return
    if stock_total < 0:
        self.send_error_json("stock_total must be non-negative", 400)
        return
    try:
        conn.execute("BEGIN")
        conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
        conn.commit()
        new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        self.send_json({"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, status=201)
    except sqlite3.IntegrityError:
        conn.rollback()
        self.send_error_json("Item name already exists", 409)
    except Exception:
        conn.rollback()
        self.send_error_json("Internal server error", 500)
```

注意：我们在锁内，所以不需要再加锁，但conn是全局连接，需要确保事务被正确管理。我们使用conn.execute("BEGIN")时，如果默认isolation_level不是None，可能会自动开启事务？为了安全，我们设置`isolation_level=None`以完全手动控制。建议在连接创建后设置`conn.isolation_level = None`。然后所有操作都需要显式BEGIN/COMMIT。或者，我们也可以使用`conn.execute("BEGIN")`等开始事务。在自动提交模式下，如果我们执行INSERT，会立即提交。所以我们需要手动控制。

我们可以在连接创建后设置`conn.isolation_level = 'DEFERRED'`（默认）或None。为了完全控制，设置`conn.isolation_level = None`。

如果设置为None，每次执行execute都是在自动提交模式，但当我们执行`conn.execute("BEGIN")`后，就进入了事务模式，后续执行的语句都不会自动提交，直到`conn.commit()`或`conn.rollback()`。所以我们应该设置isolation_level为None。

因此初始化时：`conn.isolation_level = None`。

然后写操作都需要BEGIN和COMMIT。

但是要注意，如果在读操作中我们使用了自动提交（没有BEGIN），也没问题，因为自动提交模式会立即执行并提交（但读操作不需要提交）。但如果在读之前有事务未提交？由于每个请求在开始时会清理（写），清理会使用事务并提交，之后才读，所以没有残留事务。

但为了安全，我们可以在读操作前确保没有未提交的事务。但我们可以在读操作中不调用BEGIN，这样自动提交模式会执行SELECT，连接自动提交？实际上，当isolation_level=None时，execute执行SELECT也会自动提交（如果当前不在事务中）。但不会有影响。

我们只要保证在每次写操作后都明确提交或回滚即可。

为了避免混淆，我们可以约定：每个处理函数如果需要写操作，使用显式事务。读操作不需要。

5.3 handle_reservations_post()

```python
def handle_reservations_post(self, conn):
    body = self.parse_json_body()
    if body is None:
        return
    item_id = body.get('item_id')
    quantity = body.get('quantity')
    ttl_seconds = body.get('ttl_seconds')
    if item_id is None or quantity is None or ttl_seconds is None:
        self.send_error_json("Missing required parameters", 400)
        return
    try:
        item_id = int(item_id)
        quantity = int(quantity)
        ttl_seconds = int(ttl_seconds)
    except (TypeError, ValueError):
        self.send_error_json("Parameters must be integers", 400)
        return
    if quantity <= 0 or ttl_seconds <= 0:
        self.send_error_json("quantity and ttl_seconds must be positive", 400)
        return
    now = datetime.datetime.utcnow()
    created_at = now.isoformat()
    expires_at = (now + datetime.timedelta(seconds=ttl_seconds)).isoformat()

    # 开始事务
    conn.execute("BEGIN")
    try:
        # 检查商品是否存在
        cursor = conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if item is None:
            conn.rollback()
            self.send_error_json("Item not found", 404)
            return
        if item['stock_available'] < quantity:
            conn.rollback()
            self.send_error_json("Insufficient stock", 409)
            return
        # 减少库存
        conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
        # 创建预约
        cursor = conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                              (item_id, quantity, expires_at, created_at))
        reservation_id = cursor.lastrowid
        conn.commit()
        self.send_json({"id": reservation_id, "item_id": item_id, "quantity": quantity, "status": "pending", "expires_at": expires_at, "created_at": created_at}, status=201)
    except sqlite3.Error:
        conn.rollback()
        self.send_error_json("Database error", 500)
```

5.4 handle_reservations_confirm(res_id)

```python
def handle_reservations_confirm(self, conn, res_id):
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,))
        reservation = cursor.fetchone()
        if reservation is None:
            conn.rollback()
            self.send_error_json("Reservation not found", 404)
            return
        if reservation['status'] != 'pending':
            conn.rollback()
            self.send_error_json("Reservation is not pending", 409)
            return
        # 更新状态
        conn.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
        conn.commit()
        self.send_json({"id": reservation['id'], "status": "confirmed"})
    except sqlite3.Error:
        conn.rollback()
        self.send_error_json("Database error", 500)
```

注意：确认不需要释放库存。

5.5 handle_reservations_cancel(res_id)

```python
def handle_reservations_cancel(self, conn, res_id):
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,))
        reservation = cursor.fetchone()
        if reservation is None:
            conn.rollback()
            self.send_error_json("Reservation not found", 404)
            return
        if reservation['status'] == 'cancelled':
            conn.rollback()
            self.send_error_json("Reservation already cancelled", 409)  # 或者400？
            return
        if reservation['status'] == 'confirmed':
            # 确认后还能取消吗？题目没有明确，但通常确认后不可取消。但我们可以允许取消？但确认后库存已经占用，且释放库存应该不能随意取消？但也可以实现取消，并释放库存。但确认后可能需要特殊处理？题目说：确认预约，状态变为confirmed，不再释放库存。暗示确认后不再释放，意味着取消操作可能不适用于confirmed？通常确认后可能不允许取消。但我们也可以允许，但根据题意“不再释放库存”可能是描述确认后的特点，但没说确认后不能取消。但为了简单，我们可以允许所有非pending状态的预约取消? 但确认后取消释放库存不合理。从设计角度，确认后应不能再取消，否则与“不再释放库存”矛盾。所以我们可以设定：只有pending的预约可以取消。如果状态不是pending，返回错误。
            conn.rollback()
            self.send_error_json("Reservation is not pending", 409)
            return
        # 更新状态为cancelled，并释放库存
        conn.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
        conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (reservation['quantity'], reservation['item_id']))
        conn.commit()
        self.send_json({"id": reservation['id'], "status": "cancelled"})
    except sqlite3.Error:
        conn.rollback()
        self.send_error_json("Database error", 500)
```

注意：对于状态检查，我们需要处理可能已取消或已确认。根据要求“取消预约，释放库存”，似乎没有说只能pending取消。但确认后如果取消，释放库存可能违背意图。更合理的是只能取消pending。我们按照只能取消pending来，如果是其他状态返回错误（409或400）。我们用错误信息提示。

5.6 清理过期预约的实现

在每次请求前执行清理。我们之前已经定义了cleanup_expired函数，它在连接上执行事务。

需要注意：清理可能发现大量过期预约，需要逐条释放库存，这一过程应该在事务中。但是，如果在清理过程中有其他写操作，因为锁，所以不会冲突。

在锁内，我们首先调用cleanup_expired(conn)，然后执行主要逻辑。

但是，如果cleanup_expired失败（如数据库错误），我们应该如何处理？可能应该继续执行主要逻辑还是返回500？如果清理失败，数据库可能有问题，最好返回500。我们可以让清理在主要逻辑的事务外，单独try-except，如果失败则记录日志并继续？但可能数据不一致。我们可以在锁内，先尝试清理，如果失败，释放锁并返回500。所以我们可以在do_GET/POST中，获取锁后，先尝试清理，如果异常，则发送500并释放锁。

因此，在do_GET/POST中：
```python
def do_GET(self):
    with db_lock:
        try:
            cleanup_expired(db_conn)
        except Exception:
            self.send_error_json("Database cleanup error", 500)
            return
        # 路由处理...
```

但注意：cleanup_expired已经自己使用事务，如果失败会在内部回滚并抛出，我们应该捕获并返回500。

同样对do_POST。

但是，如果清理成功，但后续主要逻辑失败，我们需要确保清理的结果已经提交。由于清理含在独立的事务中（在cleanup_expired内部提交），所以即使后续失败，清理已经生效。这符合预期（过期预约已经被释放）。但是后续主要逻辑如果是在锁内单独的事务，它的失败不会回滚清理。所以没问题。

但是，如果我们在do_POST的写操作中使用了事务，并且因为错误回滚，那么清理已经提交不受影响。所以设计是好的。

六、HTTP响应

我们需要设置正确的Content-Type: application/json。

实现send_json(data, status=200)：

```python
def send_json(self, data, status=200):
    body = json.dumps(data, ensure_ascii=False)
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Content-Length", len(body.encode('utf-8')))
    self.end_headers()
    self.wfile.write(body.encode('utf-8'))
```

send_error_json(msg, status)：

```python
def send_error_json(self, message, status=400):
    self.send_json({"error": message}, status)
```

七、解析请求体：

```python
def parse_json_body(self):
    content_length = int(self.headers.get('Content-Length', 0))
    if content_length == 0:
        self.send_error_json("Empty request body", 400)
        return None
    body = self.rfile.read(content_length)
    try:
        return json.loads(body.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        self.send_error_json("Invalid JSON", 400)
        return None
```

八、路由匹配

我们需要提取路径中的ID。使用正则表达式或字符串分割。使用`re.match`或`re.search`。

编译模式：
- `RESERVATIONS_CONFIRM_PATTERN = re.compile(r'^/reservations/(\d+)/confirm/?$')`
- `RESERVATIONS_CANCEL_PATTERN = re.compile(r'^/reservations/(\d+)/cancel/?$')`

注意：路径可能以/结尾，所以加上可选`/?`。

在do_POST中匹配。

需要注意：BaseHTTPRequestHandler的path属性包含可能的查询字符串，但在这里我们假设没有查询参数。可以使用`parsed_path = urlparse(self.path)`获取路径部分。为了简单，我们可以直接使用`self.path`，但应该去掉查询字符串。使用`self.path.split('?')[0]`。

或者使用`urllib.parse.urlparse(self.path).path`。

九、启动服务器

在`__init__`中初始化数据库，然后创建服务器并服务。

```python
if __name__ == "__main__":
    DB_FILE = "inventory.db"
    db_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    db_conn.row_factory = sqlite3.Row
    db_conn.isolation_level = None  # 手动事务
    init_db(db_conn)
    server = ThreadingHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server started on 127.0.0.1:8080")
    server.serve_forever()
```

但是注意：`ThreadingHTTPServer`位于`http.server`模块中。Python 3.7+可用。如果运行环境是Python 3.5/3.6，我们可以使用混合类：

```python
from http.server import HTTPServer
from socketserver import ThreadingMixIn
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass
```

这样兼容。我们可以这样定义。

因此，我们可以在代码中定义这个类，而不是导入ThreadingHTTPServer，以确保兼容。

十、处理请求的锁范围

我们使用`with db_lock:`在每个do_GET和do_POST中。但要注意，如果多个请求同时到达，锁会阻塞。但因为是多线程，每个请求一个线程，所以会排队。由于锁保护整个处理过程（包括清理和操作），所以有锁的请求会串行化。性能可能受影响但功能正确。

十一、一些细节

- 在清理过期时，我们使用`expires_at < ?`条件，但时间比较是字符串比较，由于ISO格式字符串比较是字典序的，等同时间比较（只要格式一致）。所以安全。我们使用UTC时间，ISO格式。
- 创建预约时，使用`datetime.datetime.utcnow()`得到当前UTC时间，然后转为ISO格式。
- 数据库行转字典：可以使用`dict(row)`因为row_factory=Row，Row对象支持`dict(row)`。
- 注意：在获取新插入行的ID时，使用`last_insert_rowid()`或`cursor.lastrowid`。在使用`INSERT`后，`cursor.lastrowid`可用。但是当我们使用conn.execute时，返回的cursor对象。所以我们可以：

```python
cursor = conn.execute("INSERT ...")
reservation_id = cursor.lastrowid
```

同样对items。

十二、错误处理

- 参数验证：对于缺失参数、类型错误等，返回400。
- 库存不足：409。
- 商品不存在：404。
- 预约重复操作（如取消已经取消的）：我们可以用409或400，但更好用409 Conflict。
- 数据库完整性错误：例如name重复，返回409（使用IntegrityError捕获）。
- 其他数据库错误：500。

十三、其他考虑

- 跨域？不需要。
- 日志？不需要。
- 优雅关闭？不需要。
- 重载？不需要。

代码结构参考：

```
#!/usr/bin/env python3
import json
import sqlite3
import threading
import re
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIN
from urllib.parse import urlparse

DB_FILE = "inventory.db"
db_lock = threading.Lock()
db_conn = None

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def init_db(conn):
    conn.execute("""...""")
    conn.execute("""...""")
    conn.commit()

def cleanup_expired(conn):
    now = datetime.datetime.utcnow().isoformat()
    with conn:  # 使用conn作为上下文管理器自动提交/回滚？但我们需要手动事务。
    # 使用显式BEGIN/COMMIT
    conn.execute("BEGIN")
    try:
        cur = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
        for row in cur:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (row['id'],))
        conn.commit()
    except:
        conn.rollback()
        raise

class InventoryHandler(BaseHTTPRequestHandler):

    # 正则模式
    confirm_pattern = re.compile(r'^/reservations/(\d+)/confirm/?$')
    cancel_pattern = re.compile(r'^/reservations/(\d+)/cancel/?$')

    def do_GET(self):
        path = urlparse(self.path).path.rstrip('/') or '/'
        if path == '/items':
            with db_lock:
                try:
                    cleanup_expired(db_conn)
                except:
                    self.send_error_json("Internal server error", 500)
                    return
                # 处理GET items
                try:
                    cursor = db_conn.execute("SELECT id, name, stock_total, stock_available FROM items")
                    items = [dict(row) for row in cursor.fetchall()]
                    self.send_json(items)
                except Exception as e:
                    self.send_error_json("Database error", 500)
        else:
            self.send_error_json("Not found", 404)

    def do_POST(self):
        path = urlparse(self.path).path.rstrip('/') or '/'
        with db_lock:
            try:
                cleanup_expired(db_conn)
            except:
                self.send_error_json("Internal server error", 500)
                return
            if path == '/items':
                self.handle_items_post()
            elif path == '/reservations':
                self.handle_reservations_post()
            else:
                match = self.confirm_pattern.match(self.path)
                if match:
                    res_id = int(match.group(1))
                    self.handle_reservations_confirm(res_id)
                else:
                    match = self.cancel_pattern.match(self.path)
                    if match:
                        res_id = int(match.group(1))
                        self.handle_reservations_cancel(res_id)
                    else:
                        self.send_error_json("Not found", 404)

    # 以下处理函数直接使用db_conn（在锁内）
    def handle_items_post(self):
        body = self.parse_json_body()
        if body is None:
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        # 验证...
        try:
            stock_total = int(stock_total)
        except (TypeError, ValueError):
            self.send_error_json("Invalid stock_total", 400)
            return
        if stock_total < 0:
            self.send_error_json("Invalid stock_total", 400)
            return
        db_conn.execute("BEGIN")
        try:
            cursor = db_conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
            item_id = cursor.lastrowid
            db_conn.commit()
            self.send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, status=201)
        except sqlite3.IntegrityError:
            db_conn.rollback()
            self.send_error_json("Item name already exists", 409)
        except Exception:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    # 其他类似...
```

但注意：处理函数都在锁内，并且都是使用全局db_conn连接。我们需要确保每个写操作使用正确的事务。注意：在handle_items_post中，我们使用了db_conn.execute("BEGIN")，但如果在执行之前已经有一个未提交的事务怎么办？由于每个处理函数在进入后清理时已经提交了事务（清理内部提交了），所以没有未提交事务。所以安全。

但是，我们使用了清理在开头，如果清理中使用事务并提交，那么进入处理函数时没有活跃事务。所以可以开始新事务。

但是，如果处理函数开始事务后，又调用另一个方法（比如send_error_json），然后需要回滚，我们通过try-except确保回滚。

另外，在handle_reservations_confirm等中，我们使用了begin/commit，如果发送错误响应前已经调用rollback，则没问题。但注意，如果在发送错误响应后，不应该再执行任何数据库操作，但我们已经回滚，所以没问题。

还有一个问题：在处理GET时，我们并没有使用事务，直接SELECT，可以。

但是，在清理时，我们调用了cleanup_expired，它内部使用了begin/commit，这是独立的事务，与后续不相关。

现在，我们要注意：在一个处理函数中，如果发生异常（如ValueError），我们可能没有正确回滚事务。所以我们需要在可能出现异常的地方使用try-except来管理事务。

我们也可以使用上下文管理器来管理事务。例如，我们可以定义一个函数`transaction(conn)`返回一个上下文管理器。但是为了简单，我们显式begin-commit/rollback。

在以上代码中，我们使用`db_conn.execute("BEGIN")`，然后用try-except包裹。

注意：在`cleanup_expired`中，我们内部有begin/commit/rollback，但如果它失败，我们会捕获并返回500，然后不再执行后续操作。所以没问题。

但是，在handle_items_post中，如果body是None（解析失败），我们已经发送错误响应并返回，但此时我们没有开始事务。所以没问题。

如果body解析成功但缺失参数，我们发送错误，没有开始事务，没问题。

现在，关键点：并发控制。我们使用全局锁保护整个处理过程。但是，如果我们使用`ThreadingHTTPServer`，每个请求在单独的线程中处理，那么锁会串行化所有请求。这确保了一致性。

但有必要考虑性能：如果并发量高，可能成为瓶颈。但这个习题规模不需要考虑高性能。

但是，我们还需要考虑数据库连接在多个线程中使用吗？由于我们使用全局连接，并在线程中共享，设置check_same_thread=False并加锁是正确的。每个处理函数中，我们都在锁内访问连接，所以只有持有锁的线程使用连接，所以线程安全。

不过，在BaseHTTPRequestHandler中，如果我们在锁内调用了self.send_json，可能会触发写操作，但不会访问数据库，所以安全。

但是，调试时，要注意`cleanup_expired`调用时，我们没有在锁外使用连接？我们是在锁内调用的，所以安全。

现在，完善代码：

- 导入必要的模块：json, sqlite3, threading, re, datetime, http.server, socketserver, urllib.parse.
- 定义全局变量。
- 编写init_db, cleanup_expired。
- 编写InventoryHandler。
- 处理细节：

在parse_json_body中，如果Content-Length不存在，可以假设0。我们根据Content-Length读取。但应该对错误情况处理（如Content-Length不是整数）。但简单处理：如果不存在或为空，则返回None并发送错误。但更稳健：如果Content-Length没有，则读取rfile直到EOF？但POST请求通常有Content-Length。我们假设有。

还可以处理HEAD请求？不需要。

关于路径匹配：由于我们使用两个正则，我们需要确保匹配基于原始路径（可能包含查询字符串）。所以我们应该使用`urlparse(self.path).path`来获取路径部分，然后用于匹配。我们可以在do_POST一开始就解析路径`path = urlparse(self.path).path`。

在正则匹配时，我们需要匹配路径字符串。我们可以在类中定义模式为类属性。

注意：在匹配时，我们使用`self.confirm_pattern.match(self.path)`，但self.path包含原始路径（可能带查询），而模式是`^/reservations/(\d+)/confirm/?$`，如果路径有查询字符串，会不匹配。所以我们需要使用纯净路径。我们使用`path = urlparse(self.path).path`，然后match。但模式应该匹配纯净路径。所以用`self.confirm_pattern.match(path)`。

在do_POST中，我用了`self.path`，应该改为`path`。

现在，代码的其他细节：

- 商品总数stock_total，新商品可用stock_available初始等于stock_total。
- 注意数据库字段名，在查询后通过`dict(row)`转换为字典。
- 在cleanup_expired中，我们使用Row对象访问`row['quantity']`等。
- 使用with conn？但我们手动begin/commit。

我们可以考虑使用`conn.__enter__`上下文管理器，但那样会自动提交或回滚。我们也可以使用`with conn:`，但那是执行`conn.close()`？不是。实际上，sqlite3的`connect`对象可以作为上下文管理器，在事务中执行操作，如果发生异常则回滚，否则自动提交。但是，如果我们在上下文管理器中执行多条语句，应该使用`with conn:`包裹事务块。例如：

```python
with conn:
    conn.execute("UPDATE ...")
    conn.execute("INSERT ...")
```

这会在进入时开始事务，离开时提交，异常时回滚。非常方便！我们可以利用这个特性简化代码。上下文管理器使用的是`conn.__enter__`和`__exit__`。注意：如果设置了`isolation_level`为非None（默认DEFERRED），则`with conn`会开始一个事务。如果`isolation_level=None`，则`with conn`不会开始事务，而是直接执行？根据文档，当isolation_level为None时，连接处于“自动提交”模式，`with conn:`不会提供事务支持。实际上，在自动提交模式下，`conn.__enter__`没有特殊效果，语句会立即提交。所以如果我们希望使用`with conn`管理事务，我们需要设置isolation_level为''（空字符串？）或'DEFERRED'等非None值。默认是''（空字符串）意味着使用python的默认行为（DEFFERED）。但为了手动事务，我们之前设置isolation_level=None。我们可以改用isolation_level='DEFERRED'，然后使用`with conn:`来自动管理事务。这更简洁。

但是，需要注意：`with conn:`开始一个事务，如果正常退出则COMMIT，如果异常则ROLLBACK。但这里的问题是，我们之前想独立清理事务，然后在同一个连接中后续事务。如果使用`with conn:`，我们必须确保在上一个事务结束后才能开始下一个事务。由于我们在锁内执行一系列操作，我们可以针对每个独立的事务使用with块。

例如处理函数中：

```python
# 清理
try:
    with conn:
        cur = conn.execute("SELECT ...")
        # 更新库存 ...
except: ...
# 然后主要操作
with conn:
    # 插入...
```

所以我们可以利用`with conn`简化。但注意：在with块内，我们执行语句，如果出现异常，会自动回滚。如果在读操作中，我们不需要事务，可以直接使用conn.execute（自动提交）。

如果我们设置isolation_level='DEFERRED'，那么连接默认处于事务外，每次执行语句会隐式开始事务？实际上，默认模式下，当第一次执行SQL语句时，会隐式开启一个事务，之后的语句都会在该事务内，直到调用commit或rollback。但这可能导致意外长事务。所以最好使用手动或with块。

我决定使用isolation_level=None（自动提交模式），然后手动begin/commit，或者使用with conn来执行事务（设置isolation_level非None）。但是为了代码整洁，我倾向于使用`with conn:`方式，因为它简洁且自动处理回滚。因此，我们设置`conn.isolation_level = 'DEFERRED'`（或没有设置，使用默认空字符串）。默认情况下，`isolation_level`是''，意味着自动开始事务。但是，如果我们在连接上执行`execute`，会自动开始一个事务。然后后续的execute都在该事务中，直到我们commit或rollback。但要注意，如果我们在一个请求中使用的所有操作都在同一个事务中，可能会太长。但我们的请求是短小的。我们可以利用这一点：在清理中使用一个with块，然后主要操作中使用另一个with块。但是，如果我们不明确commit，with块会自动commit（在正常退出时）。这很好。

但是，有一个陷阱：在自动提交模式下（默认isolation_level=''），`with conn:`不会做任何特殊处理，因为连接已经处于自动事务开始的状态。实际上，文档说：当isolation_level不是None时，连接在首次执行SQL语句时会隐式开始事务，直到显式提交或回滚。`with conn:`会在上下文管理器的__exit__中根据异常情况提交或回滚。所以，如果你在with块外已经执行了语句，可能已经有一个事务打开了。所以最好确保在with块开始前没有未提交的事务。由于我们串行化执行，每次处理请求前，上一个请求已经提交了所有事务，所以连接是干净的。所以我们可以在每个写操作开始时使用`with conn:`开始新事务。但要注意，如果我们在with块外执行了SELECT，这些SELECT会在隐式事务中，并且可能需要明确提交。但读操作通常不需要事务，但如果有隐式事务，我们需要确保它被提交或回滚，否则后续with块会失败（因为已经有一个事务打开）。所以最好在所有操作中都显式使用with块，包括读？读也可以放在事务中，但不必要。最安全的做法是：在每个请求中，我们在开始任何操作前，确保没有未提交的事务。因为每个请求是独立的，我们可以通过每次连接执行一条`ROLLBACK`来清除残留事务？但不需要，如果我们一直正确管理。

最简单：我们设置`isolation_level='DEFERRED'`，然后总是在with块中执行所有数据库操作，包括读。这样事务会自动管理，而且读会有一个短事务（自动提交）。但是，如果在读中使用with，则会在读结束后提交。没问题。所以我们可以统一使用`with conn:`来执行语句集合，即使只有一条SELECT语句。这样可以确保不会有未提交的事务残留。这应该是可靠的。

但是要注意：如果在with块内调用了send_json等可能引发异常的操作，我们需要回滚事务。使用with块的话，如果异常发生，__exit__会回滚。所以我们需要将可能抛出异常的响应函数放在with块外？不，在事务块内，我们应该只包含数据库操作。事务应该尽早提交。所以更好的结构是：

```python
def handle_items_get(self):
    with db_conn:  # 开始事务（可能需要读？读其实不需要事务，但可以）
        cursor = db_conn.execute("SELECT ...")
        items = [dict(row) for row in cursor.fetchall()]
    # 事务已经提交（自动）
    self.send_json(items)
```

但是，如果send_json在提交后，没问题。如果事务内包含send_json，如果send_json抛出异常（如连接断开），会导致事务回滚？但这种情况很少。所以我们可以安全地将事务块与响应分开。对于写操作，我们需要在事务块内执行多个语句，然后提交成功后再发送响应。如果发生错误，我们在事务块内return或抛出异常，导致回滚，同时在发送错误响应。但注意：我们需要在事务块外发送响应，因为事务回滚后连接释放。所以我们可以将事务块放在try中，在成功时发送成功响应，在失败时捕获异常并发送错误响应。

使用with块的一个限制是：我们不能在事务内发送错误响应然后继续？实际上，如果在with块内发现错误条件（如库存不足），我们可以通过设置一个标志然后跳出块并回滚。但with块内无法直接强制回滚而不引起退出。我们可以抛出异常来回滚。所以处理方式是：在with块内，如果发现错误条件，我们raise一个自定义异常或直接使用return？但是return不会触发回滚，因为__exit__会检查是否异常。如果我们希望回滚，应该抛出一个异常。然后我们在外部的except中捕获并发送错误。但这样我们需要自定义异常类，或者使用`rollback`后return？不鼓励在with块内手动rollback，因为with块会管理。如果我们手动rollback，然后离开with块（正常），会尝试提交？这会导致错误。所以最好在with块内抛出一个异常。

在Python的sqlite3中，当在with conn中使用时，如果退出时没有异常，则自动提交。如果有异常，则回滚。所以我们可以在检测到错误条件时，抛出一个简单的Exception（例如`ValueError`），然后在外层捕获并发送错误响应。但是这样会回滚整个事务，包括前面可能已经执行的语句。这是合理的，因为如果库存不足，我们不想创建预约。所以我们可以使用这种模式。

写操作统一：

```python
def handle_reservations_post(self):
    body = self.parse_json_body()
    if body is None: return
    # 获取参数验证...
    # 处理...
    try:
        with db_conn:
            # 检查商品
            cur = db_conn.execute("SELECT ...")
            item = cur.fetchone()
            if item is None:
                raise ValueError("Item not found")
            if item['stock_available'] < quantity:
                raise ValueError("Insufficient stock")
            db_conn.execute("UPDATE ...")
            cur = db_conn.execute("INSERT ...")
            res_id = cur.lastrowid
        # 事务已提交
        self.send_json(...)
    except ValueError as e:
        self.send_error_json(str(e), 409)  # 或者404等
    except Exception:
        self.send_error_json("Database error", 500)
```

但是我们需要区分错误类型：Item not found -> 404，Insufficient stock -> 409。我们可以使用自定义异常类，或通过检查错误类型。简单做法：我们可以定义几个自定义异常。或者使用if-else在except中判断消息。但消息可能多语言，不好。更好的：在事务块内，我们可以提前发送错误响应并返回，但不回滚事务？但无法在with块内发送响应（可能会在回滚后发送）。所以我们可以采取另一种方式：在事务块内，如果遇到错误条件，我们调用`db_conn.rollback()`，然后直接发送错误响应并返回。但注意，事务块中的rollback后，with块退出时会尝试再次rollback？这可能会出问题。所以不建议。

另一种方式：不在写操作中使用with conn，而是使用手动begin/commit/rollback，这样更灵活。我决定使用手动方式，因为更清晰且易于理解。之前已经写好了代码基于手动。为了减少复杂性，我继续使用手动BEGIN/COMMIT/ROLLBACK。代码稍长，但更直接。

但是，我们也要使用with锁，无其他。

因此，我保留手动事务。

但在写操作中，我们都要使用try-except来确保回滚。

现在，我在处理函数中，直接写：

```python
def handle_items_post(self):
    # ... 验证
    db_conn.execute("BEGIN")
    try:
        # 插入
        db_conn.commit()
        self.send_json(...)
    except sqlite3.IntegrityError:
        db_conn.rollback()
        self.send_error_json(...)
    except Exception:
        db_conn.rollback()
        self.send_error_json(...)
```

这是安全的。

对于GET操作，我们不需要事务。直接SELECT。

对于清理操作，我们也使用手动事务。

现在，统一锁：在处理函数内部，我们不直接加锁，因为在do_GET/do_POST已经加锁了。

但是，在do_GET中，我们调用了cleanup_expired和具体的处理函数。这些函数都是在锁内执行的，它们使用db_conn直接操作，没有问题。

但注意：如果在处理函数内部因为某些原因使用了db_conn而没有提前begin，自动提交模式会立即执行语句。例如，在handle_items_get中使用SELECT，直接execute，这是自动提交模式。但连接处于锁内，在调用SELECT之前，可能没有手动开始事务。如果之前有未提交的事务？不会，因为我们在清理中已经提交事务，而后续也没有开始事务（因为写了BEGIN）。所以SELECT时没有活跃事务，所以SELECT在自动提交模式下执行，立即执行并返回结果。这没问题。

但是，如果在SELECT之前，可能已经有一个未提交的事务？由于我们每次请求都会在锁内先清理，清理提交了事务，所以没有未提交的。而且在一个请求内部，我们不会在操作之间遗留未提交事务。因为写操作都使用BEGIN/commit/rollback，读操作不需要事务。所以连接始终没有未提交事务（除了在事务进行中）。所以后续的SELECT安全。

因此，整个设计良好。

现在，还要注意：在do_POST中，我们调用cleanup_expired()然后调用具体处理函数。在具体处理函数中，可能进行写操作，使用BEGIN。但是如果cleanup_expired内部提交了，没有活跃事务，可以。但如果在处理函数中开始事务后，需要确保在发送响应前提交。我们在写操作中确保。

但是，如果在处理函数中，我们使用了`db_conn.execute("BEGIN")`但没有提交或回滚，会导致锁内连接一直处于事务中，影响后续请求。所以我们必须在每次写操作中保证提交或回滚。而在发生错误时，我们通过except块回滚并发送错误，然后退出函数，此时事务已回滚。所以连接回到无事务状态。

但是，如果在发送响应后返回，没有错误，事务已提交。所以连接空闲。

在GET操作中，没有事务，连接空闲。

所以每次请求结束后，连接总是没有活跃事务。

在cleanup_expired内部，也必须保证提交或回滚。

现在，我们考虑一个情况：如果在do_GET中，cleanup_expired成功，但是handle_items_get抛出异常（如数据库错误），此时我们没有在handle_items_get中捕获异常？我们在do_GET的try块中捕获了，但那是针对cleanup_expired的异常。对于handle_items_get的异常，我们没有捕获。所以我们需要在do_GET中对整个处理逻辑加上try-except来发送500。目前的do_GET代码中，对于handle_items_get的调用没有异常处理。我们可以在外部加上try-catch。或者，我们在handle_items_get内部捕获异常并发送500。但为了统一，我们可以在do_GET中加上try-except。

类似地，在do_POST中，我们已经在每个处理函数内部处理了一些异常，但未处理的异常（如未预见的错误）应该被捕获导致500。所以可以在do_POST中包围一个try-except。

改进：

在do_GET和do_POST中，整个锁内的代码都包含在try-except中。但注意，我们锁内的清理操作已在try中，然后处理函数也可能抛出异常，我们需要确保在异常时事务被回滚？如果处理函数中没有开始事务（如GET），则不需要回滚。如果处理函数开始了事务但发生异常时异常没有被处理，可能导致事务未提交或回滚，连接处于挂起状态。这会影响下一个请求（同样需要锁）。因此最好确保所有写操作处理函数自己捕捉异常并回滚。然而，我们可以在do_POST中捕获所有异常，尝试回滚未提交的事务，但不知道是否已经有事务。我们可以通过检查连接是否在事务中？标准库没有直接方法。我们可以使用`conn.in_transaction`（Python 3.2+？实际上，sqlite3.Connection有`in_transaction`属性（只读），返回布尔值表示是否有未提交的事务。所以我们可以利用这个属性来决定是否回滚。但是，如果有异常，我们可以检查`db_conn.in_transaction`，如果是True，则执行rollback()。这样可防止连接挂起。我们可以将这个放在大的try-finally块中。但为了简化，我们要求每个处理函数自己管理事务，如果不管理可能导致不一致，但我们作为程序员应确保。在do_GET和do_POST中，我们也可以这样：

```python
with db_lock:
    try:
        cleanup_expired(db_conn)
        # dispatch
        # ...
    except Exception as e:
        # 如果存在未提交的事务，回滚
        if db_conn.in_transaction:
            db_conn.rollback()
        self.send_error_json("Internal server error", 500)
    # 注意：如果dispatch成功，但事务未提交（不应该），我们需要提交？不应该。
```

这样统一兜底。我决定在每个请求处理中，在锁内使用try-except，如果发生异常，检查事务并回滚，然后返回500。这样即使处理函数遗漏，也能保证连接不被挂起。

但在正常流程中，如果dispatch成功，但处理函数未提交事务（不应该），我们需要提交。但我们的处理函数应当提交。所以我们可以忽略。

其实，我们可以统一在try-finally中检查事务并提交/回滚？但最好只在异常时回滚，成功时不自动提交（因为可能不需要事务，有则提交）。所以我们只在异常时检查回滚。

因此，修改do_GET和do_POST：在锁内，用try包裹清理和分发，except Exception: 如果in_transaction则rollback；然后发送500。如果没异常，正常继续。

注意：在do_GET中，dispatch没有任何事务（读），所以不会有in_transaction。所以没问题。

在do_POST中，如果dispatch函数自己正确处理了异常（如库存不足）并发送了错误响应后，事务已回滚，这时候in_transaction为False，不会额外回滚。但如果dispatch函数发生未预料的异常，导致事务未提交，则回滚。

所以，我们可以简化处理。但是我们之前是在处理函数内部分别处理错误并发送相应，这样更好，因为我们可以区分错误类型和状态码。所以具体处理函数应该尽量捕获已知异常并发送适当响应。如果是意外异常，则让它传播到外层，由外层统一捕获并返回500。但是，注意，在外层捕获前，处理函数可能已经开始了事务，但由于异常传播，事务未提交或回滚。在外层我们捕获后回滚事务，并发送500。这没问题。

但是，在具体处理函数中，如果自身捕获了异常并发送了错误响应，它应该已经回滚了事务，不会再抛出异常。所以不会传播到外层。

所以我们可以修改结构：外层try-except只处理未知异常。内层（处理函数）处理已知异常并发送响应。如果内层发生未知异常，则传播到外层，外层回滚事务并发送500。但注意：内层可能已经部分修改数据，但没提交也没回滚，所以外层需要回滚。所以外层检查in_transaction并回滚。

同时，内层如果自己捕获异常并调用了rollback，则不会抛出异常，in_transaction为False。

因此，我们需要确保在处理函数中，在所有可能异常路径上都要调用rollback，以免事务挂起。但是，如果没处理好，外层可以兜底。

我们暂时按复杂处理：在每个处理函数内部手动管理事务，如果任何错误调用rollback并发送错误响应，不再抛出异常。这样外层不会捕获异常。

例外：如果处理函数中的错误响应发送后，我们直接return，不再抛出异常。所以外层try-except捕获不到，没问题。

但是如果处理函数中发现了内部错误（如数据库错误），我们捕获并发送500，同时回滚，不重新抛出。所以异常不会传播。那么外层try-except是多余的，但可以保留作为完全未预料的错误（例如函数外部的错误）。

为了代码安全，我们依然在外层try-except中包括整个处理。

现在，实现具体代码。

另外，需要处理字符编码问题。

还有，注意http.server BaseHTTPRequestHandler的`server_version`和`sys_version`。

我们还可以设置`self.close_connection = True`？不需要。

现在，编写完整代码。

最终确认各个API细节：

1. GET /items: 返回列表。每个商品包含id, name, stock_total, stock_available。示例：`[{"id":1, "name":"item1", "stock_total":10, "stock_available":8}]`。可以直接返回列表。

2. POST /items: 参数`name` (string), `stock_total` (int). 返回创建的商品对象（包含id等），status 201。如果name已存在，返回409 {error: "Item name already exists"}。如果缺少参数，返回400。如果stock_total无效（非整，负数），返回400。

3. POST /reservations: 参数`item_id`, `quantity`, `ttl_seconds`。库存不足返回409。如果商品不存在404。成功返回预约对象（包含id, item_id, quantity, status, expires_at, created_at），status 201。参数缺失/无效返回400。

4. POST /reservations/{id}/confirm: 确认预约。成功返回`{"id": id, "status": "confirmed"}`（或者完整对象也可以）。如果预约不存在返回404。如果不是pending状态，返回409。注意：确认后库存不再释放，但不需要修改库存。

5. POST /reservations/{id}/cancel: 取消预约。成功返回类似`{"id": id, "status": "cancelled"}`。如果预约不存在404。如果状态不是pending（已确认或已取消），返回409。取消时释放库存（增加available）。

注意：过期预约的过期时间是以秒为单位，并存储ISO时间。在创建预约时，我们需要计算expires_at。清理时比较当前时间。

在清理过期时，推荐使用UTC时间。所有时间使用UTC。我们使用`datetime.datetime.utcnow()`。

注意：在比较时，我们存储的是ISO字符串，比较也是字典序，对于相同格式的UTC时间，比较正确。

但是，如果时区混合，可能会有问题，我们统一用UTC。

确保在创建预约时，expires_at是ISO格式。我们也可以用时间戳，但ISO字符串更可读。

在send_json时，我们需要确保数据被正确序列化成JSON。日期时间已经是字符串，所以没问题。

现在，代码行数约束：不大于1000行，我们预计在200-400行之间。

现在，开始编写最终代码。

关键点：

- 使用`from http.server import HTTPServer, BaseHTTPRequestHandler`和`from socketserver import ThreadingMixIn`定义ThreadingHTTPServer。
- 全局变量：DB_FILE = "inventory.db"；db_lock = threading.Lock()；db_conn = None。

- 初始化函数：使用conn执行建表。
- cleanup_expired：使用conn执行事务。

- InventoryHandler类：
  属性：server_version = "InventoryAPI/1.0"
  类属性：res_confirm_pat = re.compile(r'^/reservations/(\d+)/confirm/?$')
  类属性：res_cancel_pat = re.compile(r'^/reservations/(\d+)/cancel/?$')

  方法：
    def log_message(self, format, *args): 可以重载以减少日志或默认。
    def send_json(self, data, status=200):
    def send_error_json(self, message, status=400):
    def parse_json_body(self):
    def do_GET(self):
    def do_POST(self):
    def handle_items_get(self):
    def handle_items_post(self):
    def handle_reservations_post(self):
    def handle_reservations_confirm(self, res_id):
    def handle_reservations_cancel(self, res_id):

在do_GET和do_POST中，我们会这样做：

```python
def do_GET(self):
    with db_lock:
        try:
            cleanup_expired(db_conn)
            path = urlparse(self.path).path.rstrip('/') or '/'
            if path == '/items':
                self.handle_items_get()
            else:
                self.send_error_json("Not found", 404)
        except Exception:
            if db_conn.in_transaction:
                db_conn.rollback()
            self.send_error_json("Internal server error", 500)
```

do_POST类似。

但是注意：在handle_items_get中，如果发生异常，我们需要保证它被外部捕获并返回500。所以handle_items_get应该不处理异常，直接执行（可能抛出）。所以我们不在handle_items_get内部捕获错误。这样外部捕获。但这样，如果是业务错误如商品不存在？不需要，因为GET items总是返回列表，所以没有业务错误。所以可以由外部捕获意外。可行。

但是，在handle_items_post等中，我们自己处理了业务错误并返回了错误响应，而不抛出异常。这些处理函数返回None，但外部不检查这个返回值。所以我们外部不能区分是否已经发送了响应。但我们在do_POST中，dispatch后不会再发送任何响应。所以我们需要确保每个分支要么发送了响应，要么抛出异常。如果我们自己处理了，并调用了send_json或send_error_json，那就发送了响应，然后函数返回None，接着do_POST就自然结束。如果dispatch没有发送任何响应（比如由于缺少else分支），就会导致没有响应，连接会超时。所以我们最好在dispatch后检查是否已经发送了响应？可以设置一个标志，但更常见的是，每个dispatch分支都明确发送响应，如果没有匹配到路径，我们在外部发送404。所以如果dispatch函数是自己处理了，都会发送响应。但为了防止遗漏，我们可以在do_POST中调用dispatch后，如果没有任何匹配，发送404。但是，我们的do_POST结构是：if path == '/items': self.handle_items_post() elif path == '/reservations': ... else: 尝试正则匹配，如果匹配，调用对应函数；否则发送404。所以每个分支要么匹配执行，要么else发送404。所以每个请求都会发送一个响应。所以没问题。

但是，在handle_items_post内部，如果解析body失败，它发送400并返回。然后do_POST后面没有其他代码，所以响应已发送。所以每个路径都是这样。

注意：在handle_items_post内部，如果缺少参数，我们发送了错误响应，然后函数返回，没有问题。

因此，外部不需要再发送响应。

但考虑到意外异常（如数据库连接断开）可能没有被处理函数捕捉，就会导致没有响应。所以外部try-except会捕获并发送500作为兜底。所以安全性高。

现在，在do_POST和do_GET中，我们调用cleanup_expired，同时dispatch。注意：cleanup_expired必须在dispatch之前，并且是每次请求都要执行。所以合适。

但是，有一些情况，如GET /items，我们不需要写操作，但为了清理过期预约，我们执行清理。所以每次请求都会清除过期预约。

现在，还有一个潜在问题：如果多个请求同时进入，第一个请求在锁内清理过期，第二个请求等待锁，当它获得锁时，又会清理一次，可能没有过期，但执行一次查询，开销小。可以接受。

现在，我们注意，在handle_reservations_cancel中，我们释放库存时，应该更新items.stock_available。但需要注意，如果预约确认后，库存已经不可释放，所以我们不允许取消confirmed。我们在检查状态时，只有pending可以取消。如果是confirmed或cancelled，返回409。

确认预约时，只是修改状态。但注意：确认后，库存不会恢复。所以不需要修改库存。

对于过期预约，我们在清理时释放库存并改为expired。所以过期后不能确认或取消（状态不是pending）。在我们的实现中，如果尝试确认或取消一个过期的预约（状态变为expired），我们会检查status是否为pending，如果不是，返回409。所以合理。

还有一个业务细节：在创建预约时，我们检查了库存足够，并减少了available。但如果预约过期，库存被释放；如果确认，库存不再释放。现在，确认预约不会改变已占用的库存。没问题。

但是，如果预约取消了，我们释放库存。那么取消后库存增加。

如果预约确认后，库存已经被占用，我们不能取消释放库存。所以确认后的预约不可取消，我们只允许取消pending。

现在，考虑数据结构：我们使用status字段表示状态，取值：'pending', 'confirmed', 'cancelled', 'expired'。

在清理中，我们把过期的pending设为expired。

这样所有状态都有记录。

现在，代码中要处理这些字符串。

现在，写代码。

另外，注意：在handle_reservations_post中，我们需要返回创建的预约，包括id, item_id, quantity, status, expires_at, created_at等。这些值我们已有，可以直接返回字典。

在POST /items中，返回新商品，可能返回包括id, name, stock_total, stock_available。

在confirm和cancel中，返回预约的id和新的status即可，也可以返回完整对象。我们选择返回id和status。但也可以返回更新后的行。但题目没有指定，简单返回id和status，或者返回完整行。为了信息完整，我选择返回更新后的预约信息（包括所有字段），或者至少id和status。在confirm/cancel中，我们不需要返回完整，但可返回简单对象。我们参照典型REST实践，返回受影响的对象表示。但简单起见，只返回id和status。因为题目例子没给。我决定返回{"id": ..., "status": "confirmed"} 或 {"id": ..., "status": "cancelled"}。也可以返回包含其他不变字段，但简洁些。

在错误响应中，始终包含`error`字段。例如`{"error": "Insufficient stock"}`，status 409。

现在，实现编码细节：

- 文本编码：使用utf-8。
- 所有JSON响应使用ensure_ascii=False以便支持中文（可选）。但没关系。

- 使用`json.dumps(data, ensure_ascii=False)`。

现在，我们编写代码。

注意：不要在代码中使用第三方库，包括`parse`等。

代码大致如下：

```python
#!/usr/bin/env python3
import json
import sqlite3
import threading
import re
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

DB_FILE = "inventory.db"
db_lock = threading.Lock()
db_conn = None

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    );""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL
    );""")
    conn.commit()

def cleanup_expired(conn):
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("BEGIN")
    try:
        cur = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
        rows = cur.fetchall()
        for row in rows:
            # 释放库存
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
            # 更新状态
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ?", (row['id'],))
        conn.commit()
    except:
        conn.rollback()
        raise

class InventoryHandler(BaseHTTPRequestHandler):
    server_version = "InventoryAPI/1.0"
    confirm_pat = re.compile(r'^/reservations/(\d+)/confirm/?$')
    cancel_pat = re.compile(r'^/reservations/(\d+)/cancel/?$')

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body.encode('utf-8')))
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def send_error_json(self, message, status=400):
        self.send_json({"error": message}, status)

    def parse_json_body(self):
        content_length = self.headers.get('Content-Length')
        if not content_length:
            self.send_error_json("Content-Length header required", 400)
            return None
        try:
            content_length = int(content_length)
        except (ValueError, TypeError):
            self.send_error_json("Invalid Content-Length", 400)
            return None
        if content_length == 0:
            self.send_error_json("Empty request body", 400)
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error_json("Invalid JSON", 400)
            return None

    def do_GET(self):
        with db_lock:
            try:
                cleanup_expired(db_conn)
                path = urlparse(self.path).path.rstrip('/') or '/'
                if path == '/items':
                    self.handle_items_get()
                else:
                    self.send_error_json("Not found", 404)
            except Exception as e:
                if db_conn.in_transaction:
                    db_conn.rollback()
                self.send_error_json("Internal server error", 500)

    def do_POST(self):
        with db_lock:
            try:
                cleanup_expired(db_conn)
                path = urlparse(self.path).path.rstrip('/') or '/'
                if path == '/items':
                    self.handle_items_post()
                elif path == '/reservations':
                    self.handle_reservations_post()
                else:
                    match = self.confirm_pat.match(self.path)
                    if match:
                        res_id = int(match.group(1))
                        self.handle_reservations_confirm(res_id)
                    else:
                        match = self.cancel_pat.match(self.path)
                        if match:
                            res_id = int(match.group(1))
                            self.handle_reservations_cancel(res_id)
                        else:
                            self.send_error_json("Not found", 404)
            except Exception as e:
                if db_conn.in_transaction:
                    db_conn.rollback()
                self.send_error_json("Internal server error", 500)

    def handle_items_get(self):
        cursor = db_conn.execute("SELECT id, name, stock_total, stock_available FROM items")
        items = [dict(row) for row in cursor.fetchall()]
        self.send_json(items)

    def handle_items_post(self):
        body = self.parse_json_body()
        if body is None:
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or stock_total is None:
            self.send_error_json("Missing required parameters: name, stock_total", 400)
            return
        if not isinstance(name, str) or not name.strip():
            self.send_error_json("name must be a non-empty string", 400)
            return
        try:
            stock_total = int(stock_total)
        except (TypeError, ValueError):
            self.send_error_json("stock_total must be an integer", 400)
            return
        if stock_total < 0:
            self.send_error_json("stock_total must be non-negative", 400)
            return
        db_conn.execute("BEGIN")
        try:
            cursor = db_conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name.strip(), stock_total, stock_total))
            item_id = cursor.lastrowid
            db_conn.commit()
            self.send_json({"id": item_id, "name": name.strip(), "stock_total": stock_total, "stock_available": stock_total}, status=201)
        except sqlite3.IntegrityError:
            db_conn.rollback()
            self.send_error_json("Item name already exists", 409)
        except:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def handle_reservations_post(self):
        body = self.parse_json_body()
        if body is None:
            return
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if item_id is None or quantity is None or ttl_seconds is None:
            self.send_error_json("Missing required parameters: item_id, quantity, ttl_seconds", 400)
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (TypeError, ValueError):
            self.send_error_json("item_id, quantity, ttl_seconds must be integers", 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self.send_error_json("quantity and ttl_seconds must be positive", 400)
            return
        now = datetime.datetime.utcnow()
        created_at = now.isoformat()
        expires_at = (now + datetime.timedelta(seconds=ttl_seconds)).isoformat()
        db_conn.execute("BEGIN")
        try:
            cursor = db_conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
            if item is None:
                db_conn.rollback()
                self.send_error_json("Item not found", 404)
                return
            if item['stock_available'] < quantity:
                db_conn.rollback()
                self.send_error_json("Insufficient stock", 409)
                return
            db_conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            cursor = db_conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                                     (item_id, quantity, expires_at, created_at))
            res_id = cursor.lastrowid
            db_conn.commit()
            self.send_json({
                "id": res_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": created_at
            }, status=201)
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def _get_reservation_or_error(self, res_id):
        # 辅助函数：查询预约行，如果不存在返回None并发送404
        cursor = db_conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,))
        row = cursor.fetchone()
        if row is None:
            self.send_error_json("Reservation not found", 404)
            return None
        return row

    def handle_reservations_confirm(self, res_id):
        db_conn.execute("BEGIN")
        try:
            reservation = self._get_reservation_or_error(res_id)
            if reservation is None:
                db_conn.rollback()
                return
            if reservation['status'] != 'pending':
                db_conn.rollback()
                self.send_error_json("Reservation is not pending", 409)
                return
            db_conn.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            db_conn.commit()
            self.send_json({"id": res_id, "status": "confirmed"})
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def handle_reservations_cancel(self, res_id):
        db_conn.execute("BEGIN")
        try:
            reservation = self._get_reservation_or_error(res_id)
            if reservation is None:
                db_conn.rollback()
                return
            if reservation['status'] != 'pending':
                db_conn.rollback()
                self.send_error_json("Reservation is not pending", 409)
                return
            # 释放库存
            db_conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (reservation['quantity'], reservation['item_id']))
            db_conn.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            db_conn.commit()
            self.send_json({"id": res_id, "status": "cancelled"})
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

if __name__ == "__main__":
    db_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    db_conn.row_factory = sqlite3.Row
    db_conn.isolation_level = None  # 手动管理事务
    init_db(db_conn)
    server = ThreadingHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server started on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopping...")
        server.shutdown()
```

现在，检查代码：

- 在`cleanup_expired`中，我们使用了`conn.execute("BEGIN")`，并且在最后有commit。但如果没有任何过期行，我们仍然commit。但如果在没有事务的情况下执行`conn.execute("BEGIN")`会开始一个新事务，即使没有行，commit也是安全的。所以没问题。

- 注意：在`cleanup_expired`中，我们打印还是记录日志？不需要。

- 在`do_GET`和`do_POST`中，我们调用`cleanup_expired(db_conn)`，但如果它抛出异常，我们捕获并发送500。但是`cleanup_expired`内部已经处理了异常（它自己的try-except会回滚并重新抛出），所以我们捕获异常后，会再次尝试回滚（因为`db_conn.in_transaction`可能为True？在`cleanup_expired`失败时，它已经回滚，但是是在它的except块中调用了rollback，然后raise。所以在抛出异常时，事务已经回滚，因此`in_transaction`为False。所以外层的`if db_conn.in_transaction`条件不会触发多余回滚。但我们在外层仍然发送500。这没问题。

但是，`cleanup_expired`中如果数据库连接出错（如断开），可能in_transaction为True？但连接已经不可用。我们不做太多考虑。

- 在`do_GET`/`do_POST`中，我们在try中调用了`cleanup_expired`和dispatch函数。如果dispatch函数发生异常，我们在except中会回滚（如果事务存在）。但dispatch函数应该自己处理事务。如果异常传播到外层，说明处理函数没有处理，我们统一回滚并返回500。这很好。

- 注意：在`handle_reservations_confirm`等中，我们调用了`_get_reservation_or_error`辅助函数，它如果返回None（即预约不存在），发送404并返回None。然后我们判断reservation is None，则回滚事务并返回。这里我们回滚事务（因为之前已经执行了BEGIN）。在发送404后，我们应当回滚事务，因为事务中可能已经做了其他操作？实际上，在查询预约时，还没有做修改，所以回滚也没有影响。我们回滚以结束事务。如果我们不结束事务，会导致后续无法进行。所以我们在每个分支都回滚。但是，在`_get_reservation_or_error`内部，我们发送了404响应，所以没有后续其他操作。然后回到confirm函数，我们需要回滚BEGIN，因为当前事务没有其他要做的。所以回滚是正确的。如果直接commit，由于只有查询，也可以，但为了统一，我们回滚也可以。但如果在事务中还有其他的写操作？没有。所以回滚或提交都一样，但使用回滚表示事务撤销（其实无写操作）。所以可以。

但注意：我们在`_get_reservation_or_error`中发送了响应，然后返回None。调用者必须检查返回值并停止处理。我们必须在调用后return。所以我们在confirm函数中，if reservation is None: db_conn.rollback(); return。这样保证不会继续执行后面的代码。同样在cancel中。

但是，在confirm和cancel中，我们还需要处理其他错误情况（如不是pending），同样回滚并返回。

注意：在`handle_reservations_cancel`中，`_get_reservation`之后可能返回row，然后检查状态，如果不是pending，我们回滚并发送409，然后return。所以没问题。

- 在`_get_reservation_or_error`中，我们使用的是db_conn.execute进行SELECT，这会在事务内执行（因为有BEGIN）。如果查询后，我们发送404，然后退出，调用者可以回滚事务。所以需要回滚。

- 注意：我们在`handle_items_get`中，直接使用db_conn.execute（不手动BEGIN），这是自动提交模式，不会开启事务。由于isolation_level=None，execute会立即执行并提交（如果有写入则立即写入）。但读取不会开启事务，所以没问题。

- 在`do_GET`中，我们调用了cleanup_expired，然后handle_items_get。cleanup_expired使用了事务并提交，连接回到无事务状态。所以handle_items_get在自动提交模式下运行。完美。

现在，我们需要考虑并发处理：锁的使用确保每个请求串行访问数据库。但我们需要确认，在锁持有期间，我们调用了`self.send_json`等，这些可能会阻塞（大响应），但在此期间锁被持有，其他请求等待，这样会影响并发。但这是简单的实现。如果要在发送响应前释放锁，我们可以考虑在发送响应前释放锁，但这可能会引入不一致：如果释放锁后，在发送响应过程中还有数据库操作？没有，所以可提前释放锁。但对于写操作，在事务提交后，我们可以在发送响应前释放锁。这样其他请求可以马上进来。但是，我们的锁保护整个请求，包括响应发送。响应发送可能涉及网络I/O，但不涉及数据库。所以我们可以提前释放锁。然而，我们当前的结构是在锁的上下文内进行所有操作，包括send_json。我们可以显式地释放锁。但是为了简单，我们保持整个处理在锁内。由于我们锁的范围包括cleanup_expired和dispatch，在dispatch中，我们在发送响应前已经完成所有数据库操作（提交事务）。所以可以在发送响应之前释放锁。我们可以修改结构：在锁内执行数据库操作，保存结果（如要发送的数据），然后释放锁，最后发送响应。这样可以提高并发性。但这不是必须的。如果请求处理慢（如大量数据），可以释放锁。但是为了简单，我们还是保持锁到响应发送完。但响应发送可能因为网络慢而延迟，导致锁持有时间过长。因此，改进的方法是：在锁内只进行数据库操作，构造响应数据，然后释放锁，最后发送响应。这样可以提高并发性。我们应该这样做。

让我们修改do_GET和do_POST：在锁内，我们只执行数据库操作，并构造将要发送的数据（或直接调用发送函数？但发送函数可能写在锁内）。我们可以在锁内准备响应数据，但不发送。然后离开锁，再发送。但send_json需要self.wfile，可以放在锁外。这样，我们需要将send_json调用移出锁外。为此，我们需要将响应数据和状态码从锁内返回给外层。

我们可以这样做：在锁内执行请求处理，处理函数返回一个元组 (data, status) 或者 (error, status) 或者直接通过实例变量保存。但更简单的是，我们可以在锁内调用一个方法来准备响应，但不实际发送，而是将数据暂存，然后锁外发送。例如，我们在InventoryHandler中添加属性 `self.response_data` 和 `self.response_status` 或类似。但是，为了不混淆，我们可以直接在锁内调用send_json，但之前我们讨论过锁范围可能太大。权衡：考虑到我们使用的是内存数据库且数据量不大，并且锁持有时间很短（主要是数据库操作），响应数据通常很小（JSON列表），所以锁内发送影响不大。但单线程处理时，如果网络慢，可能影响。但在演示环境中，我们假设客户端在同一机器。为了彻底，我们可以尝试优化，但题目并不要求高性能。我们保持简单，锁内发送。

但注意：如果锁内发送，我们发送完响应后才释放锁。其他请求等待，可能会因为慢客户端导致队列阻塞。所以最好缩短锁的持有时间。我们可以将数据库操作和响应分离。我们可以这样修改：在锁内，执行所有数据库操作（包括清理和主要操作），然后在锁内构建要发送的数据（如JSON字符串），但不发送。然后释放锁，在锁外发送响应。但是，构建JSON字符串不需要锁，我们可以在锁内将数据准备好（如Python对象），然后锁外用send_json序列化和发送。所以我们可以减少锁的持有时间。

所以，我决定：在锁内，执行数据库操作，并准备一个`response`对象（字典或列表）以及`status`，保存在实例变量中。然后释放锁后，调用send_json（或send_error_json）。但注意，错误响应的发送也需要在锁外。我们需要确保在锁内如果发生错误，我们发送错误响应，但可能也使用锁外发送。

按照这个模式，我们可以重构do_GET/do_POST：

```python
def do_GET(self):
    with db_lock:
        try:
            cleanup_expired(db_conn)
            path = urlparse(self.path).path.rstrip('/') or '/'
            if path == '/items':
                # 直接处理，但将结果数据保存在self变量
                self.handle_items_get()  # 但handle_items_get会调用send_json（在锁内）
            else:
                self.send_error_json("Not found", 404)
        except Exception as e:
            if db_conn.in_transaction:
                db_conn.rollback()
            self.send_error_json("Internal server error", 500)
```

这样send_json在锁内。我们为了简单，就这样吧。如果我们要优化，需要重写所有处理函数使其返回数据而不是直接发送。改动较大。考虑到1000行内，且性能不是关键，我们保持锁内发送。

但是，题目没有明确性能要求，而且并发控制主要是为了库存一致性，可以用锁。所以这样应该可以。

但要注意：如果锁内发送时发生I/O错误（如客户端断开），可能会抛出异常，导致锁没有释放？但锁使用了with语句，会正确释放。所以即使发生异常，with块会退出，锁释放。

所以安全。

现在，最终检查：代码行数估计在300行左右，不超过1000。

还有一些要点：

- 在cleanup_expired中，我们使用`row['item_id']`，但需要确保conn.row_factory设置了Row。我们已经在初始化时设置了。
- 在handle_items_post中，我们检查name是否为字符串并strip。但可以使用更严格验证：如果name是空字符串或None，返回错误。
- 所有日期时间字符串使用isoformat()，不包含时区（UTC）。
- 注意：在Python 3.7+，datetime.utcnow()返回naive datetime，表示UTC时间，但isoformat()不包含Z。这没关系，在我们内部比较时，都是naive且是UTC，所以比较字符串ok。

- 在清理时，我们使用`expires_at < ?`，ISO字符串比较正确，因为所有字符串长度相同（如果都是UTC且格式相同），所以可以。

- 在handle_reservations_post中，我们计算expires_at时使用了timedelta。注意：如果ttl_seconds很大，datetime的加法不会溢出。

现在，测试用例（手动测试）：

- 启动服务器。
- POST /items: {"name": "item1", "stock_total": 10} -> 201
- GET /items -> 返回列表[{...}]
- POST /reservations: {"item_id":1, "quantity": 3, "ttl_seconds": 10} -> 201
- GET /items -> stock_available变为7
- 等待10秒后，发任意请求（如GET /items），此时过期预约被清理，stock_available恢复为10，预约状态变为expired。
- POST /reservations/1/confirm 应该成功（如果在过期前），确认后库存不变。
- 取消pending的预约，释放库存。
- 尝试确认已取消的，返回409。
- 尝试取消已确认的，返回409。
- 商品重复创建409。
- 库存不足时创建预约返回409。
- 商品不存在404。

应该覆盖。

现在，完善代码：

- 在do_POST中，匹配正则时，我们使用的是`self.path`还是`path`？在代码中，我们使用了`match = self.confirm_pat.match(self.path)`，但正则模式是基于完整路径（不含查询字符串）。如果路径含有查询字符串，会匹配失败。我们应当使用纯净路径`path`来匹配。所以我们改为`match = self.confirm_pat.match(path)`。

同样对于`cancel_pat`。

- 在handle_reservations_confirm和cancel中，我们在开头使用了`db_conn.execute("BEGIN")`，但注意，如果在开始之前已经有一个事务（由于外层？），但不存在。所以OK。

- 在handle_reservations_confirm中，我们使用了辅助函数`_get_reservation_or_error`，但这个函数内部调用了`db_conn.execute`，这是事务内的。所以没问题。

- 注意：在辅助函数中，如果发送了404，我们返回None。调用者需要检查并回滚（因为已经有了BEGIN）。所以我们在调用后需要回滚。所以代码中我们在if reservation is None之后，执行`db_conn.rollback(); return`。

但是，在`_get_reservation_or_error`内部已经发送了404响应，所以我们调用者直接回滚并返回。

- 注意：在cancel中，如果预约不存在，我们回滚并返回；如果状态不是pending，同样回滚并返回错误。需要确保在每个return之前回滚。

- 特别注意：在`handle_reservations_post`中，我们在BEGIN后执行一系列操作，如果出现错误，我们在rollback后发送错误响应，然后return。在最后，如果我们成功，我们commit并发送201。每个分支都处理了。

- 在`handle_items_post`中类似。

- 在`handle_items_get`中，不需要事务，直接SELECT。

- 注意：在`do_GET`中，除了/items，我们没有其他GET路由。

- 在`do_POST`中，我们还有路由匹配，包括confirm和cancel。我们在分支中调用了相应函数。这些函数内部如果发生未知异常，会传播到外部，由外部捕获并返回500。

- 在外部，我们除了捕获异常，还检查in_transaction。但要注意，在处理函数内部，如果发送错误响应（如409）并return后，事务已回滚，不会留下事务。所以外部in_transaction为False。

- 但是，如果处理函数在发起发送后但还没有return时发生异常？例如send_json可能会抛出（如客户端断开），那么异常会传播到外部，此时可能事务还在？但send_json在发送响应时可能已经提交了事务？不一定。我们通常在数据库操作完成后，发送响应之前，已经提交了事务。所以在发送响应时，连接已经没有活跃事务。所以外部捕获异常后再回滚没问题（in_transaction可能False）。所以没问题。

- 如果异常发生在提交之前，比如在提交前发送响应？我们设计是先提交再发送响应。所以安全。

现在，考虑在handle_reservations_confirm中，我们调用了db_conn.commit()，然后调用self.send_json。如果send_json抛出异常，事务已经提交，不能回滚，但数据库已改变。外部如果捕获异常，尝试回滚（in_transaction False），不会回滚已提交的内容。但客户端可能没有收到响应，但数据已经改变，符合ACID（但客户端不知道）。可以接受，因为服务器无法恢复。我们可以在发送响应前先提交，这样即使发送响应失败，事务已提交，数据一致。所以顺序是先提交后发送响应。我们正是这样做的。在错误路径，我们先回滚，再发送错误响应。

因此，总体一致。

现在，完整代码。

但是在模版中，有一些细节：

- 在`_get_reservation_or_error`中，我们返回Row对象，在后续使用`reservation['quantity']`等。由于conn.row_factory=Row，所以可以。

- 在`cleanup_expired`中，我们使用`row['item_id']`和`row['quantity']`。Row对象支持类似字典访问。

- 注意：在`handle_reservations_post`中，我们使用了参数化查询，数量等。

- 需要导入`datetime`模块。

- 需要设置`db_conn.isolation_level = None`，但也可以在连接后设置。我们已经在`__main__`中设置。

- 注意：如果在`cleanup_expired`中，连接没有设置row_factory，但如果我们在创建了全局连接后设置了，所以cleanup_expired可以访问。

- 在`handle_items_get`中，我们返回列表，如果没有任何商品，返回空列表`[]`。

现在，检查代码是否有任何语法错误和逻辑错误。

逐段检查：

```python
import json
import sqlite3
import threading
import re
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
```

注意：`ThreadingMixIn`来自`socketserver`。

```python
DB_FILE = "inventory.db"
db_lock = threading.Lock()
db_conn = None
```

`ThreadingHTTPserver`定义：

```python
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass
```

注意：`ThreadingMixIn`没有`allow_reuse_address`等，但我们可以设置`allow_reuse_address = True`在服务器实例或类。

`init_db`:

```python
def init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    );""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL
    );""")
    conn.commit()
```

注意：我们没有设置外键约束，但可以。使用`WITHOUT ROWID`？不需要。

`cleanup_expired`:

```python
def cleanup_expired(conn):
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("BEGIN")
    try:
        cur = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
        rows = cur.fetchall()
        for row in rows:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ?", (row['id'],))
        conn.commit()
    except:
        conn.rollback()
        raise
```

注意：在`SELECT`中，我们使用了`row['quantity']`，但需要确保`row`是`sqlite3.Row`。因为全局连接设置了row_factory，所以没问题。

`InventoryHandler`类：

确认和取消正则模式：注意，我们在类级别定义`confirm_pat`和`cancel_pat`。

在`do_GET`中：

```python
def do_GET(self):
    with db_lock:
        try:
            cleanup_expired(db_conn)
            path = urlparse(self.path).path.rstrip('/') or '/'
            if path == '/items':
                self.handle_items_get()
            else:
                self.send_error_json("Not found", 404)
        except Exception as e:
            if db_conn.in_transaction:
                db_conn.rollback()
            self.send_error_json("Internal server error", 500)
```

在`do_POST`中：

```python
def do_POST(self):
    with db_lock:
        try:
            cleanup_expired(db_conn)
            path = urlparse(self.path).path.rstrip('/') or '/'
            if path == '/items':
                self.handle_items_post()
            elif path == '/reservations':
                self.handle_reservations_post()
            else:
                match = self.confirm_pat.match(path)  # 使用path，不是self.path
                if match:
                    res_id = int(match.group(1))
                    self.handle_reservations_confirm(res_id)
                else:
                    match = self.cancel_pat.match(path)
                    if match:
                        res_id = int(match.group(1))
                        self.handle_reservations_cancel(res_id)
                    else:
                        self.send_error_json("Not found", 404)
        except Exception as e:
            if db_conn.in_transaction:
                db_conn.rollback()
            self.send_error_json("Internal server error", 500)
```

`send_json`和`send_error_json`和`parse_json_body`如上。

`handle_items_get`:

```python
def handle_items_get(self):
    cursor = db_conn.execute("SELECT id, name, stock_total, stock_available FROM items")
    items = [dict(row) for row in cursor.fetchall()]
    self.send_json(items)
```

注意：可能没有设置cursor.row_factory？不，全局连接设置了row_factory，所以fetchall返回Row对象，`dict(row)`转换为字典。

`handle_items_post`:

已经提供。但我们需要确保在失败路径中适当return。已经包含。

`handle_reservations_post`:

同上。

`_get_reservation_or_error`:

```python
def _get_reservation_or_error(self, res_id):
    cursor = db_conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,))
    row = cursor.fetchone()
    if row is None:
        self.send_error_json("Reservation not found", 404)
        return None
    return row
```

`handle_reservations_confirm`:

```python
def handle_reservations_confirm(self, res_id):
    db_conn.execute("BEGIN")
    try:
        reservation = self._get_reservation_or_error(res_id)
        if reservation is None:
            db_conn.rollback()
            return
        if reservation['status'] != 'pending':
            db_conn.rollback()
            self.send_error_json("Reservation is not pending", 409)
            return
        db_conn.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
        db_conn.commit()
        self.send_json({"id": res_id, "status": "confirmed"})
    except sqlite3.Error:
        db_conn.rollback()
        self.send_error_json("Database error", 500)
```

注意：`sqlite3.Error`捕获所有sqlite错误。但其他异常可能会传播到外层，由外层捕获并转500。所以这里我们只针对已知的sqlite错误。其他异常会传播到外部。

`handle_reservations_cancel`:

```python
def handle_reservations_cancel(self, res_id):
    db_conn.execute("BEGIN")
    try:
        reservation = self._get_reservation_or_error(res_id)
        if reservation is None:
            db_conn.rollback()
            return
        if reservation['status'] != 'pending':
            db_conn.rollback()
            self.send_error_json("Reservation is not pending", 409)
            return
        db_conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (reservation['quantity'], reservation['item_id']))
        db_conn.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
        db_conn.commit()
        self.send_json({"id": res_id, "status": "cancelled"})
    except sqlite3.Error:
        db_conn.rollback()
        self.send_error_json("Database error", 500)
```

注意：在cancel中，我们使用`reservation['quantity']`和`reservation['item_id']`，这些在事务内查询。

`__main__`:

```python
if __name__ == "__main__":
    db_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    db_conn.row_factory = sqlite3.Row
    db_conn.isolation_level = None
    init_db(db_conn)
    server = ThreadingHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server started on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopping...")
        server.server_close()
```

注意：我们没有设置`server.allow_reuse_address = True`，但可以加入。

可以设置`ThreadingHTTPServer.allow_reuse_address = True`。

在类中也可以。

现在，检查一些遗漏：

- 在`parse_json_body`中，我们使用了`self.headers.get('Content-Length')`，如果没有Content-Length，我们返回错误。对于POST请求，通常需要Content-Length。但有些客户端可能使用Transfer-Encoding: chunked，但标准库可能不支持处理？我们可以先读取所有数据？但为了简单，我们要求Content-Length。我们也可以尝试读取rfile直到EOF？但是BaseHTTPRequestHandler的rfile是BufferedReader，读取Content-Length后的剩余数据可能堵塞？通常设置Content-Length是必要的。我们接受假设有Content-Length。

另一种方式：如果没有Content-Length，我们可以使用`self.rfile.read()`读取直到EOF，但可能无限等待。所以要求Content-Length是合理的。

但是，如果我们想要更健壮，可以使用`Content-Length`如果存在，否则尝试读取请求体直到EOF（但需要知道何时结束？）。简单方案就是要求Content-Length。我们保持现状。

- 在`parse_json_body`中，如果content_length过大（比如大于10MB），我们应该限制。但不需要。

- 在路径匹配时，我们用了`path.rstrip('/') or '/'`，这样对根路径'/'会变成空字符串，所以设置or '/’。我们不需要根路径。我们的路由是/items和/reservations等。如果路径是“”，我们重设为“/”，但/不是我们的路径，会返回404。所以good。

- 注意：在do_POST的匹配中，我们使用了`path`变量（去除了查询字符串和末尾斜杠）。对于confirm和cancel模式，我们使用`path`匹配。但模式定义中已经包含了可选的/?，所以可以匹配末尾斜杠。例如模式`^/reservations/(\d+)/confirm/?$`可以匹配`/reservations/1/confirm`或`/reservations/1/confirm/`。所以我们使用`path`前已经rstrip了斜杠，所以末尾不会有斜杠。模式中的/?可选，所以匹配没问题。

- 注意：如果路径中有查询字符串，urlparse会将其分离，所以path不包含？所以OK。

- 但是，我们使用`self.confirm_pat.match(self.path)`原来，现在我们改为`self.confirm_pat.match(path)`，path已经去掉查询和末尾斜杠。所以正确。

- 在do_GET中，没有查询参数，但也可以匹配。简单，使用path。

现在，我们还需要确保`db_conn`在请求处理时已经就绪。我们已经在启动时初始化了全局db_conn，所以Handler中使用db_conn没问题。

注意：在Handler中，我们直接引用模块全局变量db_conn。在类方法内部，可以直接使用。

现在，确保在`__main__`中db_conn被赋值，如果在启动服务器之前就赋值了。

现在，代码是否满足并发控制？我们使用全局锁，并且在每个请求处理时获取锁。写操作使用事务。清理也使用事务。所以库存一致性得以保证。即使多个请求同时到达，锁会串行化操作。

潜在问题：在`cleanup_expired`中，我们使用`SELECT ... WHERE expires_at < ?`，然后对每个行更新。但如果同时有大量预约过期，这个操作可能需要一些时间，但锁被持有，其他请求等待，但可以接受。

现在，关于expires_at的格式：我们使用UTC时间字符串，格式如'2023-01-01T12:00:00'。在比较时，< 运算符按字典序比较，对于同一格式的字符串有效。但注意，如果分钟或秒个位数时（如'2023-01-01T12:00:00'与'2023-01-01T12:00:01'），比较正确。但ISO格式带小数？我们没有包含微秒。`datetime.utcnow().isoformat()`默认包含微秒（6位小数），所以格式如'2023-01-01T12:00:00.123456'。这样比较字符串也是正确的，因为数字字符串，相同前缀比较时，微秒部分也会比较。所以没问题。

但是，如果我们存储的字符串不带微秒？我们使用`.isoformat()`默认返回微秒，但如果微秒为0，会不带微秒？实际上，如果微秒为0，`isoformat()`返回如'2023-01-01T12:00:00'，没有小数部分。所以可能导致字符串长度不一致。但字典序比较时，如果一个是'2023-01-01T12:00:00'，另一个是'2023-01-01T12:00:00.123456'，哪个小？前者因为长度短，实际上在ASCII比较中，'.'比'\0'小？不，字符串比较逐个字符，在比较到'.'时，前者的字符串已经结束，所以前者会被视为比后者小（因为字符串结束符小于任何字符？实际上在Python字符串比较中，较短的字符串如果与较长字符串的前缀相同，则较短字符串小于较长字符串。所以'2023-01-01T12:00:00' < '2023-01-01T12:00:00.123456'，因为前者是后者的前缀，所以前者小。但我们需要的是过期时间小于当前时间，如果当前时间是'2023-01-01T12:00:00.123456'，而过期时间是'2023-01-01T12:00:00'，那么过期时间小于当前时间，因为没有加微秒，所以会被清理。这实际上符合预期：如果过期时间精确到秒，而当前时间过了整秒，也认为过期。但是如果当前时间也是整秒（微秒=0），那么两者相等，过期时间不大于当前时间，所以不会被清理。这取决于等号。我们使用<而不是<=。所以如果过期时间和当前时间恰好相等（都是整秒），且当前时间就是过期时间，那么不会被认为过期。但这时候理论上预约刚到期，可能应该被视为过期？我们严格可以设置使用<=，但这里使用<，可能会有一秒的窗口，问题不大。但为了严格，可以用<=。但题目没有明确。我们使用<，有可能刚过期但还没有被清理。但下一次请求就会清理。所以可以接受。如果希望严格，使用<=，但注意如果存储的过期时间有微秒，而当前时间也有微秒，精确比较，我们使用<也可以。如果过期时间没有微秒，而当前时间有微秒，则过期时间<当前时间，会清理。如果两个都有微秒，也正确。所以我们使用<没问题。

但是，为了确保一致性，我们也可以使用`expires_at <= ?`。但使用<也没问题。

我们暂且保持<。

使用`<=`可能更好，因为如果恰好相等，表示预约已经是过去的时间点。但我们在创建预约时，ttl_seconds是整数，expires_at = now + ttl_seconds。如果ttl_seconds=0？题目要求positive，所以ttl_seconds>0，所以expires_at肯定大于created_at。所以如果当前时间等于expires_at，说明刚好到期，应该清理。但<不会触发。为了包容，我们使用<=。改为`expires_at <= ?`。这样，如果时间相等，也会清理。我们修改cleanup_expired中的条件为`expires_at <= ?`。

因此修改cleanup_expired:

```python
cur = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?", (now,))
```

现在，检查所有函数，没有其他问题。

现在，检查数据类型和转换。

在handle_reservations_post中，我们使用`created_at = now.isoformat()`和`expires_at = (now + timedelta).isoformat()`。

现在，确保我们导入了datetime模块。

还应该考虑，如果有大量并发，全局锁可能导致性能瓶颈，但足以满足练习。

潜在改进：读取操作（GET /items）可以不加锁，因为读操作不需要事务一致性（但库存数据要求可见性）。如果我们不加锁，读操作可能会读到中间状态（如正在创建预约中的库存减少未提交）。由于写操作在事务中，如果读操作不加锁，且在同一连接上，可能会读到未提交的数据？不能，因为SQLite默认是读已提交（在autocommit模式或读未提交？）。在SQLite中，事务隔离级别是Serialized? 实际上，SQLite在默认情况下，一个连接在事务未提交时，其他连接（或同一连接的其他线程？）不能看到未提交的数据。但这里，我们在同一个连接中，如果我们允许读与写并发（即读操作在写事务未提交时使用同一连接），会读到什么？如果我们在同一连接中，在写事务未提交时执行SELECT，会看到写事务的未提交更新（脏读），因为连接本身可以看到自己的未提交更改。但因为我们使用锁将读写串行化，所以不会出现同一连接中读写并发的情况。所以没问题。如果我们打算让读操作在不获取锁的情况下执行，那么读操作可能会与写操作同时使用同一连接，但连接是线程不安全的，且可能读到脏数据。所以我们坚持所有操作都使用锁。

因此目前的方案是安全且一致的.

最后一步：测试代码行数，确保不超过1000。我们写完后数一下行数。

我估计在250-300行之间。

现在，整理代码，包括注释？题目没有要求注释，但可以加少量。为了可读性，我们保留必要注释。

但是，输出要求：只输出完整Python代码，不要解释。所以我们直接输出代码。

考虑：我们是否符合“使用 Python 3 标准库编写一个单文件 HTTP API 服务，文件名假定为 \<\server.py\>，不得使用 Flask/FastAPI/Django 等第三方库，总代码不超过1000行”的要求。是。

现在，最后检查：

- 在do_POST中，我们调用cleanup_expired，然后处理。注意：在handle_reservations_post等创建预约时，可能会发生库存不足，此时会回滚并发送409。但此时，清理已经完成（如果在之前）。如果两个请求同时竞争库存，锁会确保一个完成后另一个才能开始。所以不会有超售问题。

- 注意：在handle_reservations_cancel中，我们释放库存。如果此时有另一个请求在等待锁创建预约，它会在cancel之后看到更新后的库存。因为cancel在事务中提交后才释放锁，所以下一个请求可以看到更新的库存。所以正确。

- 考虑一个场景：两个请求同时为同一商品创建预约，但库存只有1，两者都想要1。锁会序列化，先执行的检查库存足够，减少库存，提交；后执行的检查库存，看到为0，返回409。所以正确。

- 关于过期的清理：如果在创建预约时，同时过期预约释放库存，清理会释放库存，创建预约可能占用。因为清理在创建预约之前执行，所以当前请求可以看到释放后的库存。所以正确。

- 注意：如果在创建预约的交易中，然后清理在外部执行？但我们每次请求前都清理，所以清理总是在其他操作前。这样顺序：锁内，先清理，然后执行操作。所以清理释放的库存可以被当前操作使用。这合理。

- 但是，如果多个请求同时等待锁，它们都会在获得锁后执行清理。比如第一个请求清理了过期库存，并创建了预约，提交后释放锁。第二个请求获得锁，再次清理（可能没有过期），检查库存，可能被第一个请求减少了。所以库存一致。

现在，一个可能的争议：在清理操作中，我们可能会因为多个请求都尝试清理，但清理是幂等的，所以不会重复释放。

现在，确认没有使用未定义的变量。

在handle_reservations_confirm中，我们使用了`sqlite3.Error`，但在模块顶部我们`import sqlite3`，所以可以使用。

现在，检查`db_conn.in_transaction`属性是否可用。在Python 3.2+中，sqlite3.Connection有`in_transaction`属性。假设Python 3.4+，应该没问题。

现在，考虑`serve_forever`和`server_close`。

添加`server.server_close()`在KeyboardInterrupt时。

现在，最终代码准备。

但是，有一些地方需要微调：

- 在parse_json_body中，如果Content-Length缺失，我们发送400并返回None。但有些客户端可能不发送Content-Length但发送body，例如使用HTTP/1.1 chunked。但简单起见，我们保持。

- 在do_GET和do_POST中，我们在lock块内捕获所有异常，但如果在send_json中发生异常（例如socket error），我们捕获并也发送500？但是send_json可能已经发送了部分响应，再发送500会导致错误。但是，如果在send_json中发生异常（比如连接断开），我们无法再发送错误响应。所以我们应当忽略。我们现在的结构，如果send_json抛出异常，会被外层的except捕获，然后尝试发送错误响应，这可能失败（因为连接可能关闭）。我们可以忽略，或只记录。但为了简化，我们让异常传播到外层的try，然后尝试发送500，但如果发送失败，会再次异常，但最终线程退出。实际上，BaseHTTPRequestHandler会处理异常吗？默认会调用`handle_one_request`捕获异常。我们不需要太关心。所以我们的代码可以工作。

为了更优雅，我们可以对send_json的异常单独处理，但没必要。

现在，让我们输出最终代码。

但是，在上面的`do_POST`中，我们调用了`handle_reservations_confirm`等，这些函数内部如果有错误通过`self.send_error_json`发送了响应然后返回，没有抛出异常。所以外部不会捕获到异常。所以没问题。

如果这些函数内部遇到了未预期异常（例如AttributeError），则会传播，外部捕获，回滚（如果in_transaction），并发送500。如果此时send_json失败，可能无法发送。但这种情况很少。

现在，检查所有函数确保没有遗漏返回。

例如，在handle_reservations_confirm中，在if reservation is None分支，我们调用了db_conn.rollback(); return。但在rollback之后，我们没有发送响应吗？不，如果reservation is None，我们在`_get_reservation_or_error`中已经发送了404响应。所以我们不需要再发送响应，直接返回即可。但是，在`_get_reservation_or_error`中，我们调用了`send_error_json("Reservation not found", 404)`，所以响应已经发送。所以confirm函数之后不应再发送任何响应。所以直接return是正确的。

同样，在状态检查分支，我们发送了409，然后return。

在成功分支，我们发送了200。

同样在cancel中。

在handle_reservations_post中，我们在参数验证失败时发送错误并return，在最后成功发送201。

在handle_items_post中相同。

注意：在handle_reservations_post中，在发送400错误后，我们return，此时没有事务打开（因为我们在检查参数时还没有BEGIN）。所以安全。

在handle_items_post中类似。

现在，确认在cleanup_expired的BEGIN/COMMIT是否与连接设置兼容。因为设置了isolation_level=None，所以需要显式BEGIN。所以cleanup_expired使用BEGIN和COMMIT正确。但要注意的是，如果在执行BEGIN前，连接已经有一个未提交的事务（由于之前的错误），则BEGIN会失败。但我们确保事务总是被正确提交或回滚，所以不会有残留事务。所以安全。

在cleanup_expired中，我们使用conn.execute("BEGIN")。但在自动提交模式下，这没问题。但是在一些SQLite版本中，可能需要使用`BEGIN`或`BEGIN IMMEDIATE`。IMMEDIATE可以避免多线程时的`SQLITE_BUSY`。但因为我们外部有锁，所以不会冲突。使用BEGIN即可。

现在，添加适当的头部处理：在send_json中，我们添加了Content-Length，但需要确保我们计算长度正确。

我们使用`body.encode('utf-8')`计算字节长度。

现在，为了避免频繁编码，我们可以直接发送字节。但我们的写法没问题。

现在，最后一个问题：在ThreadingHTTPServer中，如果请求处理中发生未捕获异常，服务器可能陷入错误循环？但BaseHTTPRequestHandler会处理异常并可能关闭连接。我们不需要担心。

现在，我们最终输出代码。

但是，在`do_POST`中，我们可以将匹配confirm和cancel的正则放在函数外部，避免每次匹配，但已经类属性，所以不会每次编译。

现在，我们还需要处理一个潜在的路径：`/reservations` 可能带id的额外路径。我们已经通过正则覆盖。

现在，确保在`handle_reservations_confirm`和`handle_reservations_cancel`中，我们使用`res_id`是整数。我们从匹配获得int。

现在，检查是否存在任何引用未定义的变量。

例如，在`do_POST`中，我们定义了`path`，然后在else分支中使用`self.confirm_pat.match(path)`，是path不是self.path。好。

在`do_GET`中，我们没有使用正则。

现在，测试代码能否简单运行：可以手动模拟。

但此外，我们需要在`__main__`中设置`ThreadingHTTPServer.allow_reuse_address = True`，以便可以快速重启。

我们可以添加：

```python
ThreadingHTTPServer.allow_reuse_address = True
```

或者在服务器实例化后设置：`server.allow_reuse_address = True`。

在代码中加入：

```python
server = ThreadingHTTPServer(('127.0.0.1', 8080), InventoryHandler)
server.allow_reuse_address = True
```

或者提前设置类属性。

现在，确保在KeyboardInterrupt时正确关闭：
```python
except KeyboardInterrupt:
    print("Server stopping...")
    server.server_close()
```

但是，实际上 serve_forever 在接收到 SIGINT 后可能会退出，但需要捕获 KeyboardInterrupt。我们加入。

现在，最终代码。

考虑到我们有很多`db_conn.reference`，我们需要在`__main__`中设置`db_conn`为全局变量。

注意：在全局范围，`db_conn`初始为None，在`__main__`中覆盖为连接对象。在Handler中使用的是模块全局的`db_conn`，所以需要先在模块顶层声明`db_conn`为None，然后再赋值。没问题。

现在，编写完整代码。

但是，还有一点：在`InventoryHandler`内部，我们使用了`db_conn`作为全局变量，但如果在请求处理过程中，模块正在启动但db_conn未初始化，会出错。但我们保证在请求开始前已经初始化。

现在，代码输出。

最后截止：只输出完整 Python 代码，不要解释。

所以，我们只输出代码。

为了确保代码整洁，我们将代码段输出。

现在，让我们整理最终代码（包括调整缩进等）：

```python
#!/usr/bin/env python3
import json
import sqlite3
import threading
import re
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

DB_FILE = "inventory.db"
db_lock = threading.Lock()
db_conn = None


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True


def init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    conn.commit()


def cleanup_expired(conn):
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("BEGIN")
    try:
        cur = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
            (now,))
        for row in cur:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                         (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ?", (row['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


class InventoryHandler(BaseHTTPRequestHandler):
    server_version = "InventoryAPI/1.0"
    confirm_pat = re.compile(r'^/reservations/(\d+)/confirm/?$')
    cancel_pat = re.compile(r'^/reservations/(\d+)/cancel/?$')

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def send_error_json(self, message, status=400):
        self.send_json({"error": message}, status)

    def parse_json_body(self):
        content_length = self.headers.get('Content-Length')
        if not content_length:
            self.send_error_json("Content-Length header required", 400)
            return None
        try:
            content_length = int(content_length)
        except (ValueError, TypeError):
            self.send_error_json("Invalid Content-Length", 400)
            return None
        if content_length == 0:
            self.send_error_json("Empty request body", 400)
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error_json("Invalid JSON", 400)
            return None

    def do_GET(self):
        with db_lock:
            try:
                cleanup_expired(db_conn)
                path = urlparse(self.path).path.rstrip('/') or '/'
                if path == '/items':
                    self.handle_items_get()
                else:
                    self.send_error_json("Not found", 404)
            except Exception:
                if db_conn.in_transaction:
                    db_conn.rollback()
                self.send_error_json("Internal server error", 500)

    def do_POST(self):
        with db_lock:
            try:
                cleanup_expired(db_conn)
                path = urlparse(self.path).path.rstrip('/') or '/'
                if path == '/items':
                    self.handle_items_post()
                elif path == '/reservations':
                    self.handle_reservations_post()
                else:
                    match = self.confirm_pat.match(path)
                    if match:
                        res_id = int(match.group(1))
                        self.handle_reservations_confirm(res_id)
                    else:
                        match = self.cancel_pat.match(path)
                        if match:
                            res_id = int(match.group(1))
                            self.handle_reservations_cancel(res_id)
                        else:
                            self.send_error_json("Not found", 404)
            except Exception:
                if db_conn.in_transaction:
                    db_conn.rollback()
                self.send_error_json("Internal server error", 500)

    # -------- handlers ----------
    def handle_items_get(self):
        cursor = db_conn.execute("SELECT id, name, stock_total, stock_available FROM items")
        items = [dict(row) for row in cursor.fetchall()]
        self.send_json(items)

    def handle_items_post(self):
        body = self.parse_json_body()
        if body is None:
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or stock_total is None:
            self.send_error_json("Missing required parameters: name, stock_total", 400)
            return
        if not isinstance(name, str) or not name.strip():
            self.send_error_json("name must be a non-empty string", 400)
            return
        try:
            stock_total = int(stock_total)
        except (TypeError, ValueError):
            self.send_error_json("stock_total must be an integer", 400)
            return
        if stock_total < 0:
            self.send_error_json("stock_total must be non-negative", 400)
            return
        db_conn.execute("BEGIN")
        try:
            cursor = db_conn.execute(
                "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                (name.strip(), stock_total, stock_total))
            item_id = cursor.lastrowid
            db_conn.commit()
            self.send_json({
                "id": item_id,
                "name": name.strip(),
                "stock_total": stock_total,
                "stock_available": stock_total
            }, status=201)
        except sqlite3.IntegrityError:
            db_conn.rollback()
            self.send_error_json("Item name already exists", 409)
        except Exception:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def handle_reservations_post(self):
        body = self.parse_json_body()
        if body is None:
            return
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if item_id is None or quantity is None or ttl_seconds is None:
            self.send_error_json("Missing required parameters: item_id, quantity, ttl_seconds", 400)
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (TypeError, ValueError):
            self.send_error_json("item_id, quantity, ttl_seconds must be integers", 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self.send_error_json("quantity and ttl_seconds must be positive", 400)
            return
        now = datetime.datetime.utcnow()
        created_at = now.isoformat()
        expires_at = (now + datetime.timedelta(seconds=ttl_seconds)).isoformat()
        db_conn.execute("BEGIN")
        try:
            cursor = db_conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
            if item is None:
                db_conn.rollback()
                self.send_error_json("Item not found", 404)
                return
            if item['stock_available'] < quantity:
                db_conn.rollback()
                self.send_error_json("Insufficient stock", 409)
                return
            db_conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                            (quantity, item_id))
            cursor = db_conn.execute(
                "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                (item_id, quantity, expires_at, created_at))
            res_id = cursor.lastrowid
            db_conn.commit()
            self.send_json({
                "id": res_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": created_at
            }, status=201)
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def _get_reservation_or_error(self, res_id):
        cursor = db_conn.execute(
            "SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,))
        row = cursor.fetchone()
        if row is None:
            self.send_error_json("Reservation not found", 404)
            return None
        return row

    def handle_reservations_confirm(self, res_id):
        db_conn.execute("BEGIN")
        try:
            reservation = self._get_reservation_or_error(res_id)
            if reservation is None:
                db_conn.rollback()
                return
            if reservation['status'] != 'pending':
                db_conn.rollback()
                self.send_error_json("Reservation is not pending", 409)
                return
            db_conn.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            db_conn.commit()
            self.send_json({"id": res_id, "status": "confirmed"})
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def handle_reservations_cancel(self, res_id):
        db_conn.execute("BEGIN")
        try:
            reservation = self._get_reservation_or_error(res_id)
            if reservation is None:
                db_conn.rollback()
                return
            if reservation['status'] != 'pending':
                db_conn.rollback()
                self.send_error_json("Reservation is not pending", 409)
                return
            db_conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                            (reservation['quantity'], reservation['item_id']))
            db_conn.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            db_conn.commit()
            self.send_json({"id": res_id, "status": "cancelled"})
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)


if __name__ == "__main__":
    db_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    db_conn.row_factory = sqlite3.Row
    db_conn.isolation_level = None
    init_db(db_conn)
    server = ThreadingHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server started on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopping...")
        server.server_close()
```

检查代码行数：大约270-280行，小于1000。

现在，确认代码没有使用任何第三方库，只使用标准库。

所有依赖：json, sqlite3, threading, re, datetime, http.server, socketserver, urllib.parse。

一切符合要求。

输出：只输出代码。

因此，最终答案。
````

## Assistant

````markdown
```python
#!/usr/bin/env python3
import json
import sqlite3
import threading
import re
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

DB_FILE = "inventory.db"
db_lock = threading.Lock()
db_conn = None


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True


def init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    conn.commit()


def cleanup_expired(conn):
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("BEGIN")
    try:
        cur = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
            (now,))
        for row in cur:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                         (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ?", (row['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


class InventoryHandler(BaseHTTPRequestHandler):
    server_version = "InventoryAPI/1.0"
    confirm_pat = re.compile(r'^/reservations/(\d+)/confirm/?$')
    cancel_pat = re.compile(r'^/reservations/(\d+)/cancel/?$')

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def send_error_json(self, message, status=400):
        self.send_json({"error": message}, status)

    def parse_json_body(self):
        content_length = self.headers.get('Content-Length')
        if not content_length:
            self.send_error_json("Content-Length header required", 400)
            return None
        try:
            content_length = int(content_length)
        except (ValueError, TypeError):
            self.send_error_json("Invalid Content-Length", 400)
            return None
        if content_length == 0:
            self.send_error_json("Empty request body", 400)
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error_json("Invalid JSON", 400)
            return None

    def do_GET(self):
        with db_lock:
            try:
                cleanup_expired(db_conn)
                path = urlparse(self.path).path.rstrip('/') or '/'
                if path == '/items':
                    self.handle_items_get()
                else:
                    self.send_error_json("Not found", 404)
            except Exception:
                if db_conn.in_transaction:
                    db_conn.rollback()
                self.send_error_json("Internal server error", 500)

    def do_POST(self):
        with db_lock:
            try:
                cleanup_expired(db_conn)
                path = urlparse(self.path).path.rstrip('/') or '/'
                if path == '/items':
                    self.handle_items_post()
                elif path == '/reservations':
                    self.handle_reservations_post()
                else:
                    match = self.confirm_pat.match(path)
                    if match:
                        res_id = int(match.group(1))
                        self.handle_reservations_confirm(res_id)
                    else:
                        match = self.cancel_pat.match(path)
                        if match:
                            res_id = int(match.group(1))
                            self.handle_reservations_cancel(res_id)
                        else:
                            self.send_error_json("Not found", 404)
            except Exception:
                if db_conn.in_transaction:
                    db_conn.rollback()
                self.send_error_json("Internal server error", 500)

    # -------- handlers ----------
    def handle_items_get(self):
        cursor = db_conn.execute("SELECT id, name, stock_total, stock_available FROM items")
        items = [dict(row) for row in cursor.fetchall()]
        self.send_json(items)

    def handle_items_post(self):
        body = self.parse_json_body()
        if body is None:
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or stock_total is None:
            self.send_error_json("Missing required parameters: name, stock_total", 400)
            return
        if not isinstance(name, str) or not name.strip():
            self.send_error_json("name must be a non-empty string", 400)
            return
        try:
            stock_total = int(stock_total)
        except (TypeError, ValueError):
            self.send_error_json("stock_total must be an integer", 400)
            return
        if stock_total < 0:
            self.send_error_json("stock_total must be non-negative", 400)
            return
        db_conn.execute("BEGIN")
        try:
            cursor = db_conn.execute(
                "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                (name.strip(), stock_total, stock_total))
            item_id = cursor.lastrowid
            db_conn.commit()
            self.send_json({
                "id": item_id,
                "name": name.strip(),
                "stock_total": stock_total,
                "stock_available": stock_total
            }, status=201)
        except sqlite3.IntegrityError:
            db_conn.rollback()
            self.send_error_json("Item name already exists", 409)
        except Exception:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def handle_reservations_post(self):
        body = self.parse_json_body()
        if body is None:
            return
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if item_id is None or quantity is None or ttl_seconds is None:
            self.send_error_json("Missing required parameters: item_id, quantity, ttl_seconds", 400)
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (TypeError, ValueError):
            self.send_error_json("item_id, quantity, ttl_seconds must be integers", 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self.send_error_json("quantity and ttl_seconds must be positive", 400)
            return
        now = datetime.datetime.utcnow()
        created_at = now.isoformat()
        expires_at = (now + datetime.timedelta(seconds=ttl_seconds)).isoformat()
        db_conn.execute("BEGIN")
        try:
            cursor = db_conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
            if item is None:
                db_conn.rollback()
                self.send_error_json("Item not found", 404)
                return
            if item['stock_available'] < quantity:
                db_conn.rollback()
                self.send_error_json("Insufficient stock", 409)
                return
            db_conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                            (quantity, item_id))
            cursor = db_conn.execute(
                "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                (item_id, quantity, expires_at, created_at))
            res_id = cursor.lastrowid
            db_conn.commit()
            self.send_json({
                "id": res_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": created_at
            }, status=201)
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def _get_reservation_or_error(self, res_id):
        cursor = db_conn.execute(
            "SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,))
        row = cursor.fetchone()
        if row is None:
            self.send_error_json("Reservation not found", 404)
            return None
        return row

    def handle_reservations_confirm(self, res_id):
        db_conn.execute("BEGIN")
        try:
            reservation = self._get_reservation_or_error(res_id)
            if reservation is None:
                db_conn.rollback()
                return
            if reservation['status'] != 'pending':
                db_conn.rollback()
                self.send_error_json("Reservation is not pending", 409)
                return
            db_conn.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            db_conn.commit()
            self.send_json({"id": res_id, "status": "confirmed"})
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def handle_reservations_cancel(self, res_id):
        db_conn.execute("BEGIN")
        try:
            reservation = self._get_reservation_or_error(res_id)
            if reservation is None:
                db_conn.rollback()
                return
            if reservation['status'] != 'pending':
                db_conn.rollback()
                self.send_error_json("Reservation is not pending", 409)
                return
            db_conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                            (reservation['quantity'], reservation['item_id']))
            db_conn.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            db_conn.commit()
            self.send_json({"id": res_id, "status": "cancelled"})
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)


if __name__ == "__main__":
    db_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    db_conn.row_factory = sqlite3.Row
    db_conn.isolation_level = None
    init_db(db_conn)
    server = ThreadingHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server started on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopping...")
        server.server_close()
```
````
