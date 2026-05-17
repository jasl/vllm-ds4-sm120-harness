# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 271.739558
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 442, "total_tokens": 27133, "completion_tokens": 26691, "prompt_tokens_details": null}`
- Prompt tokens: 442
- Completion tokens: 26691
- Total tokens: 27133

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
我们被要求用Python标准库写一个单文件HTTP API服务，实现库存预约服务。不能使用第三方框架，只能用标准库，例如http.server, json, sqlite3, threading等。总代码不超过1000行。

我们需要实现：

- 使用sqlite3持久化，首次启动自动建表。
- 商品表：id, name, stock_total, stock_available
- 预约表：id, item_id, quantity, status, expires_at, created_at
- API endpoints:
  1. GET /items - list items with available stock.
  2. POST /items - add item, JSON params name, stock_total.
  3. POST /reservations - create reservation, JSON params item_id, quantity, ttl_seconds. If stock insufficient, return 409.
  4. POST /reservations/{id}/confirm - confirm reservation, status -> confirmed, no release.
  5. POST /reservations/{id}/cancel - cancel reservation, release stock.
- Before each request, clean expired pending reservations and release stock.
- Handle concurrent requests: use transactions and thread lock.
- Return JSON; error responses contain 'error' field.
- if __name__ == "__main__" entry, default listen 127.0.0.1:8080.

我们使用http.server模块的HTTPServer和BaseHTTPRequestHandler。或者可以用更简单的，但标准库的HTTP服务器是同步的，每个请求在一个线程中处理。但是我们需要处理并发，可以限制使用锁（threading.Lock）来保护数据库写入操作，确保一致性。由于我们使用sqlite3，它支持事务，但默认情况下，多个线程使用同一个连接会导致问题，最好使用线程局部连接或使用连接池，但标准库sqlite3不支持连接池。简单做法：每个请求创建新连接？但这样锁可能不需要？为了简单，我们可以使用单个连接，并加锁来保证串行访问数据库，但这样会限制并发，但能满足一致性要求。或者我们可以使用ThreadPoolExecutor结合Futures？但要求处理并发，但我们可以接受单线程锁。

但更现实的是，每个请求处理时，我们可以在处理函数中获取锁，然后操作数据库。由于http.server的HTTPServer是单线程的？实际上HTTPServer默认使用单线程，但它可以处理请求顺序，不会并发。但是，如果我们使用ThreadingHTTPServer或者使用ThreadingMixIn，就可以多线程处理。对于并发请求，我们需要确保数据一致性。所以我们应该使用ThreadingHTTPServer或者使用ThreadingMixIn和HTTPServer。但标准库有socketserver.ThreadingMixIn。我们可以创建class ThreadedHTTPServer(ThreadingMixIn, HTTPServer): pass。这样每个请求在独立线程中处理，我们需要加锁。

因此，需要定义一个锁（threading.Lock）在模块级别，在数据库操作时获取。

数据库连接：在sqlite3中，默认不能跨线程共享连接。如果我们使用连接在每个线程中创建，那么锁就不需要了，但我们要使用事务和锁来控制并发？实际上sqlite3在WAL模式或多线程模式可以支持多线程读取？但为了简单，我们使用一个连接，并在访问时加锁，但连接必须在创建它的线程中使用，但如果我们把连接作为全局，加锁后可以在不同线程使用？sqlite3连接默认是threading safety取决于编译模式。在Python中，默认是3（多线程安全），但需要设置check_same_thread=False来跨线程使用。但即使这样，我们需要确保一次只有一个线程在写，以避免数据库锁定。我们可以使用锁保护。

更常见的做法是：使用连接池或每个请求创建新连接，并使用锁来保护写操作。但每个请求创建新连接也不坏，但需要确保数据库文件不会因为并发写而损坏。使用WAL模式可以支持读并发。但我们要求事务和锁，我们可以使用单连接+全局锁来串行化所有数据库操作，虽然简单但可能性能不佳，但符合要求。

或者我们可以使用连接池，但标准库中没有。我们选择：全局数据库连接，设置check_same_thread=False，并在所有数据库操作前后使用全局锁。这样简单。

另外，对于清理过期预约，我们可以在每次请求前执行一个清理操作。这个清理也必须在同一个锁保护下进行。

所以，设计：

- 创建全局锁：db_lock = threading.Lock()
- 创建全局数据库连接：conn = sqlite3.connect('inventory.db', check_same_thread=False)
- 在初始化时，创建表（如果不存在）。
- 在每个请求处理开始时，先执行清理过期预约，然后处理请求。所有数据库操作在锁内进行。

使用BaseHTTPRequestHandler，重写do_GET, do_POST方法等。

我们需要解析路径，处理不同的路由。

对于POST请求，需要解析JSON体。

返回JSON，设置Content-Type: application/json，以及状态码。

注意：标准库的http.server会返回响应，我们需要自己处理错误状态码。

我们需要生成预约的expires_at：当前时间 + ttl_seconds。

状态：pending, confirmed, cancelled。初始为pending。

库存一致性：在创建预约时，需要原子性地检查可用库存 >= 数量，然后减少可用库存，创建预约。使用事务。

更新操作：确认预约时，更新status为confirmed，不释放库存。取消预约时，更新status为cancelled，并增加可用库存。

清理：找到所有过期且status='pending'的预约，将status更新为expired（或者直接删除？题目说清理过期仍为pending的预约并释放库存。所以我们需要将它们标记为cancelled或expired？状态字段未定义expired，但我们可以将它们视为取消并释放库存。所以我们可以使用status='cancelled'并释放库存，或者新增一个状态expired但题目未要求。简单实现：在清理时，将这些预约的status改为'expired'并释放库存。但状态只有pending、confirmed、cancelled？题目说“确认后状态变为confirmed，不再释放库存”，但未定义expired。所以我们可以增加一个expired状态。或者我们可以将它们视为cancelled并释放库存。但题目要求“清理已过期且仍为pending的预约并释放库存”，所以释放库存后，预约状态可以变为expired。所以我们应添加一个expired状态。或者我们可以直接删除这些预约，但释放库存后，可能需要保留记录。所以用status='expired'合理。所以状态包括：pending, confirmed, cancelled, expired。创建时是pending，确认后confirmed，取消cancelled，过期expired。

但注意：如果预约过期后，释放库存，然后后来确认或取消，应该不可能，所以清理后状态变为expired，后续操作需检查状态。所以确认和取消操作前应检查status是否为pending。

并发保护：每次数据库操作都获取锁。由于锁是全局的，所有操作串行化，这样最简单。

我们也可以使用更细粒度的锁，但没必要。

我们需要解析URL路径，例如/reservations/{id}/confirm，使用正则或简单split。

实现细节：

首先，定义常量，端口。

数据库初始化：

```
def init_db():
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        );
    ''')
    conn.commit()
```

注意：使用REAL存储时间戳（秒），或者可以用INTEGER+毫秒。

使用time.time()获取当前时间。

TTL秒数：expires_at = created_at + ttl_seconds。

清理函数：

```
def clean_expired():
    cursor = conn.cursor()
    now = time.time()
    cursor.execute('''
        UPDATE reservations SET status='expired'
        WHERE status='pending' AND expires_at <= ?
    ''', (now,))
    # 需要释放库存：对于每行？我们可以直接更新，但需要释放库存。更好的方法是先查询，然后释放，或在一个事务中更新库存。
    # 我们可以使用子查询？或者先用SELECT，再UPDATE释放库存。由于我们使用全局锁串行，可以迭代。
    cursor.execute('''
        UPDATE items SET stock_available = stock_available + (
            SELECT COALESCE(SUM(quantity), 0) FROM reservations
            WHERE status='expired' AND items.id = reservations.item_id AND ???)
    ''')
```
但这样复杂。简单做法：先查出过期的预约，然后遍历更新库存。在锁内操作，所以没关系。

我们可以：

```
def clean_expired():
    cursor = conn.cursor()
    now = time.time()
    # 找到过期pending
    cursor.execute('''
        SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?
    ''', (now,))
    expired = cursor.fetchall()
    if not expired:
        return
    # 更新状态为expired
    ids = [r[0] for r in expired]
    for row in expired:
        # 释放库存
        cursor.execute('''
            UPDATE items SET stock_available = stock_available + ? WHERE id = ?
        ''', (row[2], row[1]))
    # 更新状态
    cursor.execute('''
        UPDATE reservations SET status='expired' WHERE id IN ({})'''.format(','.join('?'*len(ids))), ids)
    conn.commit()
```

注意：我们需要在锁内执行，并且在其他操作前都调用。但是，如果其他操作已经获取锁，则清理也会占用锁。我们可以设计在每次请求开始时获取锁，然后执行清理，然后根据请求执行操作。这样清理和操作在同一个锁和事务中，可以保证一致性。

但是，如果在清理过程中发生错误，事务会回滚，但用户操作也会回滚。但我们可以分别提交清理和操作事务？但为了一致性，最好每个请求一个事务（包括清理）。但也可以先提交清理，再开始操作事务。不过因为清理本身是一个独立操作，我们可以先获取锁，执行清理并commit，然后开始新的操作。这样避免将清理的修改与操作合并到未提交状态。不过也可以将它们放在一个事务中，但操作事务可能失败会回滚到清理之前？如果操作失败，我们可能希望回滚整个清除+操作？但操作失败不应该让清理无效。所以最好分开提交：清理作为一个独立事务，然后操作作为一个事务。但我们需要原子性：如果操作期间失败，不希望影响清理。所以我们可以获取锁，执行清理并提交，然后执行操作并提交。如果操作失败，回滚操作事务，但清理已经提交。这符合逻辑。

所以流程：获取锁，清理过期（一个事务），然后根据请求执行操作（另一个事务）。但我们需要确保在操作期间库存状态一致，清理已经释放了库存。

但要注意：如果在清理后、操作前有并发，但由于锁存在，不可能有其他线程干扰。所以安全。

所以我们在每个请求处理开始时，在锁内做clean_expired()，然后根据请求做相应操作，最后释放锁。

但锁是全局的，我们在整个处理过程保持锁，这样串行化所有请求。性能可能差，但满足并发一致性。我们可以在clean_expired后释放锁，然后操作时再获取？但可能造成并发不一致，因为清理后可能有其他线程修改。所以最好整个请求处理期间保持锁，确保请求是原子的。因为我们的API都相对简单，保持锁可以保证一致性。但这样会降低并发，但符合要求（处理并发请求下的库存一致性，使用锁）。我们可以接受。

所以结构：

```
lock = threading.Lock()
def handle_request_with_lock(handler_func):
    with lock:
        clean_expired()
        handler_func()
```

但我们需要在每个do_GET/do_POST中调用。我们可以定义一个基类方法或装饰器。

简单：在每个方法中，用with lock: 然后先clean_expired()，然后处理路由。

因为我们要设置响应码和返回JSON，所以锁需要在响应前释放？但响应需要发送，所以锁应该在发送响应前释放，以避免锁持有时间过长。我们可以将数据库操作放在锁内，然后响应构造和发送在锁外。所以我们将数据库操作和锁的使用限定在数据访问部分。所以设计：

- 在do_GET/do_POST中，先处理请求（如解析路径、JSON），然后使用锁访问数据库（包括清理和具体操作），得到结果数据，然后在锁外设置响应并发送。

这样比较好。

所以我们需要一个函数，在锁内执行数据库操作，返回需要响应的数据（如状态码和JSON体）。

我们定义一个方法：def db_operation(path, method, body): 在锁内执行清理，然后根据路由执行操作，返回(status_code, json_dict)。然后在handler中设置状态码和发送JSON。

这样可以。

但需要访问self（handler）来发送响应？我们可以将锁内操作的结果返回，然后handler设置响应。

实现Handler类：

```
class InventoryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, data = self.handle_request()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        # read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            body_json = json.loads(body)
        except:
            # respond error
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return
        status, data = self.handle_request(body=body_json)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def handle_request(self, body=None):
        method = self.command
        path = self.path
        with db_lock:
            clean_expired()
            # routing
            # ...
```

这里handle_request在锁内执行包括clean_expired和操作。

注意：对于POST请求，读取body应该在锁外或锁内？因为读body是I/O，不涉及共享状态，在锁外读取更好，这样可以减少锁持有时间。所以我们在do_POST中先读取body并解析JSON，然后调用handle_request(body)在锁内处理。

所以do_POST: 读取body，解析JSON，如果解析失败直接返回400。否则调用handle_request(body)。所以handle_request在锁内接收解析后的body字典。

同样，GET请求没有body，直接调用handle_request()。

所以handle_request的实现：

```
def handle_request(self, body=None):
    method = self.command
    path = self.path
    if method == 'GET' and path == '/items':
        return self.get_items()
    elif method == 'POST' and path == '/items':
        return self.add_item(body)
    elif method == 'POST' and path.startswith('/reservations/') and path.endswith('/confirm'):
        # extract id
        id_part = path[len('/reservations/'):-len('/confirm')]
        try:
            res_id = int(id_part)
        except:
            return (400, {"error": "Invalid reservation ID"})
        return self.confirm_reservation(res_id)
    elif method == 'POST' and path.startswith('/reservations/') and path.endswith('/cancel'):
        id_part = path[len('/reservations/'):-len('/cancel')]
        try:
            res_id = int(id_part)
        except:
            return (400, {"error": "Invalid reservation ID"})
        return self.cancel_reservation(res_id)
    elif method == 'POST' and path == '/reservations':
        return self.create_reservation(body)
    else:
        return (404, {"error": "Not found"})
```

注意：需要检查路径格式。可以使用正则匹配。

我们可以在初始化时编译正则。

但为简单，使用字符串操作。

各个方法实现：

- get_items: 从数据库查询所有items，返回列表，每个包含id, name, stock_total, stock_available。
- add_item: 参数name, stock_total。验证参数是否存在且为正整数。插入新记录，stock_available = stock_total。返回新商品信息，状态码201。
- create_reservation: 参数item_id, quantity, ttl_seconds。验证。检查item存在且stock_available >= quantity。使用事务：减少stock_available，插入预约，status='pending', expires_at=now+ttl_seconds, created_at=now。返回预约信息，状态码201。如果库存不足，409。
- confirm_reservation: 参数reservation id。查询预约，检查是否存在且status='pending'，如果是，更新status='confirmed'。返回200。否则404或400。
- cancel_reservation: 类似，检查status='pending'，更新status='cancelled'，并且释放库存（增加stock_available）。返回200。如果已经确认或取消，返回错误？根据设计，应该只能取消pending的。

注意：清理过期已经将到期pending转为expired，所以确认和取消操作前应检查status是否还是pending。

所有数据库操作在同一个锁内，所以不需要额外事务？但为了更好保证原子性，我们仍应该使用事务（conn.commit()/rollback()）。由于锁保证了串行，但使用事务可以确保一组操作原子的，如果在操作过程中发生异常，回滚。所以我们使用explicit transactions：在方法开始时执行BEGIN或默认，但我们需要手动commit或rollback。由于我们使用execute语句，sqlite3默认是autocommit模式？但如果在connection上设置isolation_level=None或者使用execute来执行DML，默认将立即开始事务？实际上，Python sqlite3模块有以下行为：如果isolation_level非None（默认是''），则会自动在数据修改语句前开始隐式事务。默认isolation_level=''，意味着DML语句会自动启动事务，直到commit或rollback。但如果我们使用conn.execute()执行修改，它会自动开始一个事务（如果当前没有事务）。然后需要commit来持久化。如果我们不commit，修改可能只在内存中。所以我们必须在每个操作后commit。如果发生错误，我们需要rollback。

但如果我们使用多个execute，它们属于同一事务，直到commit或rollback。所以我们可以将多个操作放在一个事务中，最后提交。

由于我们在锁内，每个请求方法内可以开始事务，然后如果在过程中出错，我们回滚事务并返回错误。所以我们需要使用try-except。

最佳实践：设置conn.isolation_level = None（即使用autocommit模式，但我们手动控制事务？）。或者保持默认，每个execute之前都会检查事务是否已开始，如果未开始自动开始。但我们需要明确提交或回滚。

我们可以在每个数据库操作方法中，调用conn.execute()进行修改，然后最后conn.commit()。如果出现异常，我们conn.rollback()。但需要注意，如果查询操作不修改，不需要事务。但为了简单，每个修改操作都明确处理事务。

由于我们使用锁，我们可以依赖autocommit？但为了避免并发问题，我们显式使用事务：在方法开始时，执行conn.execute('BEGIN')，但可能与其他冲突。可以使用conn.execute('BEGIN IMMEDIATE')在锁内可能不需要。简单做法：使用conn.execute()进行修改，然后手动commit。默认autocommit模式（isolation_level=None）时，每个execute语句会立即执行并自动提交？实际上，根据文档，如果isolation_level设置为None，则连接将工作在autocommit模式，每个execute语句提交。但我们需要原子性。所以我们需要设置isolation_level为'DEFERRED'或使用事务控制。Python的默认isolation_level=''（空字符串），意味着在DML语句前会隐式开始事务。所以我们需要commit来持久化。

我们可以在连接初始化时设置isolation_level=None，然后手动控制事务：显式执行BEGIN，然后COMMIT/ROLLBACK。这样更清晰。我们选择手动控制。

所以：

```
conn = sqlite3.connect('inventory.db', check_same_thread=False, isolation_level=None)
```

然后，在每个需要事务的方法中：

```
try:
    cursor = conn.cursor()
    cursor.execute('BEGIN')
    # ... operations ...
    conn.commit()
    return (status, data)
except Exception as e:
    conn.rollback()
    return (500, {"error": str(e)})
```

但注意，如果执行BEGIN前已经有事务？由于锁确保单线程访问连接，应该不会有嵌套事务。但为了避免已经存在事务，我们可以始终在操作开始时确保没有事务？BEGIN会开始一个新事务，但如果已经有一个事务，它会失败。所以我们需要在操作开始时确保没有事务，或在事务中继续。根据sqlite3，当你执行DML时，如果当前不在事务中，会自动开始一个事务，但如果你已经在一个事务中，它会使用当前事务。所以如果我们先执行BEGIN，可能会失败如果已经在事务中。更安全的方法：我们不对事务显式BEGIN，而是让Python的autocommit模式的手动执行语句。在默认isolation_level=''下，当执行DML时，如果不在事务中，会自动开始一个新事务。所以我们可以不用显式BEGIN，只需执行DML，然后commit或rollback。如果我们执行多个DML，它们都在同一个事务中，直到commit或rollback。如果我们在读取操作（查询）后需要修改，查询本身不会触发事务，但修改会。所以我们可以依赖隐式事务。但为了显式控制，我们最好在锁内使用conn.execute来修改，然后commit。如果失败，rollback。但如果在读操作时不需要事务，就没事。

我们可以在每个修改操作中使用try-except包裹，最后commit。如果异常，rollback。

例如：

```
def add_item(self, body):
    name = body.get('name')
    stock_total = body.get('stock_total')
    if not name or not isinstance(stock_total, int) or stock_total <= 0:
        return (400, {"error": "Invalid parameters"})
    try:
        cur = conn.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                           (name, stock_total, stock_total))
        conn.commit()
        new_id = cur.lastrowid
        return (201, {"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total})
    except Exception as e:
        conn.rollback()
        return (500, {"error": str(e)})
```

但是，如果我们在同一个事务中已经执行了其他语句（例如先查询），由于我们没有提交，可能事务还在。如果我们先执行了clean_expired()，它可能已经修改了数据库（UPDATE、DELETE），我们应该提交它。因为clean_expired()在我们的方案中是在handle_request开始时调用的（在锁内），然后我们继续执行请求操作。如果我们不在clean_expired()中提交，那么后续操作处于同一个事务中，这样如果请求操作失败，回滚会影响清理。所以我们希望clean_expired()作为独立的事务。所以我们可以在clean_expired()函数中执行并提交。这样，在调用clean_expired()后，事务结束。然后后续操作开始新的事务。

所以clean_expired()实现：

```
def clean_expired():
    cur = conn.cursor()
    # 获取过期待处理的预约
    rows = cur.execute('''
        SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?
    ''', (time.time(),)).fetchall()
    if rows:
        # 更新库存
        for rid, iid, qty in rows:
            conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (qty, iid))
        # 更新状态为expired
        ids = tuple(r[0] for r in rows)
        cur.execute('UPDATE reservations SET status=\'expired\' WHERE id IN (%s)' % ','.join('?'*len(ids)), ids)
        conn.commit()
```

注意：这里使用conn.commit()提交。如果在锁内且没有其他未提交操作，没问题。

但注意：我们可能在clean_expired()之前没有自动事务启动，但conn.execute('UPDATE')会开启一个事务，然后commit后结束。所以后续操作从无事务开始。

现在，handle_request中：

```
with db_lock:
    clean_expired()
    # 根据路由调用具体方法
```

具体方法只能假设数据库状态是最新的。

注意：我们需要注意，在调用具体方法时，如果方法内再次调用clean_expired？不需要。

现在，我们需要考虑每个方法中的事务。如果方法需要原子地执行多个操作（例如创建预约：减少库存和插入预约），我们需要将它们放在一个事务中。如果使用隐式事务，我们只需要确保在开始修改前没有未提交事务，并且最后commit。由于我们在锁内，没有其他线程，而且clean_expired()已经提交，所以方法开始处于无事务状态。所以我们可以：

```
def create_reservation(self, body):
    item_id = body.get('item_id')
    quantity = body.get('quantity')
    ttl = body.get('ttl_seconds')
    if not all([isinstance(item_id, int), isinstance(quantity, int), isinstance(ttl, int)]):
        return (400, {"error": "Invalid parameters"})
    # 检查item是否存在，库存是否足够
    cur = conn.execute('SELECT id, stock_available, stock_total FROM items WHERE id = ?', (item_id,))
    item = cur.fetchone()
    if not item:
        return (404, {"error": "Item not found"})
    if item[1] < quantity:
        return (409, {"error": "Insufficient stock"})
    # 更新库存
    conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id = ?', (quantity, item_id))
    # 创建预约
    now = time.time()
    expires = now + ttl
    cur2 = conn.execute('INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, ?, ?)',
                        (item_id, quantity, 'pending', expires, now))
    res_id = cur2.lastrowid
    conn.commit()
    return (201, {"id": res_id, "item_id": item_id, "quantity": quantity, "status": "pending", "expires_at": expires, "created_at": now})
```

注意：我们使用try-except来处理可能的错误，如完整性错误等。但因为我们在锁内且数据类型正确，可能不会出错。但为了安全，可以包含try-except。

对于确认和取消，类似。

确认：

```
def confirm_reservation(self, res_id):
    # 检查是否存在且pending
    cur = conn.execute('SELECT id, item_id, quantity, status FROM reservations WHERE id = ?', (res_id,))
    res = cur.fetchone()
    if not res:
        return (404, {"error": "Reservation not found"})
    if res[3] != 'pending':
        return (400, {"error": "Reservation status must be pending to confirm"})
    conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('confirmed', res_id))
    conn.commit()
    return (200, {"id": res_id, "status": "confirmed"})
```

取消：

```
def cancel_reservation(self, res_id):
    cur = conn.execute('SELECT id, item_id, quantity, status FROM reservations WHERE id = ?', (res_id,))
    res = cur.fetchone()
    if not res:
        return (404, {"error": "Reservation not found"})
    if res[3] != 'pending':
        return (400, {"error": "Reservation status must be pending to cancel"})
    # 释放库存
    conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (res[2], res[1]))
    conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('cancelled', res_id))
    conn.commit()
    return (200, {"id": res_id, "status": "cancelled"})
```

Get items: 查询所有，返回列表。

```
def get_items(self):
    cur = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
    items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in cur.fetchall()]
    return (200, items)
```

注意：Get items 应返回JSON数组。按照RESTful最佳实践，通常返回包含items的字典？但题目要求列出商品和可用库存。我们可以直接返回数组。但为了统一，可以返回{"items": [...]}。但题目未明确，但返回数组也可接受。为了符合常见做法，我们可以在GET /items 返回数组。但如果期望一致，错误响应包含error字段，所以成功响应直接返回数据。所以返回数组没问题。

但注意：如果无商品，返回空数组。

对于POST /items，返回201和商品对象。

现在关于错误处理：如果JSON无效，我们返回400和error。如果在方法内参数不足，返回400。

对于锁：我们使用模块级别锁。

对于启动入口，使用if __name__ == "__main__": 创建服务器：

```
from http.server import HTTPServer
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

server = ThreadedHTTPServer(('127.0.0.1', 8080), InventoryHandler)
print("Server starting on 127.0.0.1:8080...")
server.serve_forever()
```

但注意：使用ThreadingMixIn会每请求创建新线程。我们使用全局锁来保证数据库操作的串行化，所以多个线程会竞争锁，所以实际还是串行。但可以接受。或者我们也可以使用HTTPServer（单线程），但可能面对并发请求时，只有一个被处理，其他排队。但使用ThreadingMixIn可以同时处理多个请求，但等待锁。所以更好。

但我们需要确保连接是线程安全的（我们已设置check_same_thread=False）。并且锁确保串行。

现在注意：我们使用conn是全局的，并且在每个线程中使用（通过锁保护），但sqlite3连接不是完全线程安全的，尽管我们使用check_same_thread=False，并且锁保护，应该没问题。

但还有一种可能性：我们可以在每个线程中创建连接（使用连接池或threading.local），但实现复杂。使用全局连接加锁简单。

关于数据库文件路径：我们使用当前目录下的'inventory.db'。但可以考虑使用内存或固定。题目没有指定，所以我们用相对路径。

现在需要确保在服务器启动时创建表。我们可以放在if __name__ == "__main__"中，在创建服务器之前初始化数据库：

```
if __name__ == "__main__":
    init_db()
    server = ThreadedHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    ...
```

但是init_db需要连接，我们需要在模块级别创建conn。所以应该在模块顶部定义conn，然后在init_db中使用它。init_db需要commit。

由于conn在模块级别定义，init_db直接操作。

注意：我们还需要定义db_lock。

所以整体结构：

```python
import json
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import re

DB_FILE = 'inventory.db'

# Global database connection and lock
conn = sqlite3.connect(DB_FILE, check_same_thread=False, isolation_level=None)  # manual transaction control
# Actually, with isolation_level=None we are in autocommit; but we need explicit commit. Let's set isolation_level=None to explicitly control.
# But if isolation_level=None, then each DML is auto-committed? Let's check: In Python sqlite3, when isolation_level is set to None,
# no implicit transaction control. You must explicitly BEGIN/COMMIT. That's what we want.
# However, the default is '' (empty string) which enables automatic beginning of transactions.
# We'll set to 'DEFERRED' or use default '' and manage manually. Actually with default '', if you call execute, it auto starts a transaction
# if one is not active. Then you commit. That works for us. Let's use default '' (not setting isolation_level) and rely on implicit start.
# But to avoid confusion, we can set isolation_level=None and do explicit BEGIN/COMMIT in each method. But then we need to be careful
# to always BEGIN. Let's use the simpler approach: use default (isolation_level='') and do for each method:
# try: ...; conn.commit(); except: conn.rollback().
# But commit is required after modifications. Query-only don't need commit.
# So we don't need to call BEGIN.

# So let's not set isolation_level=None. Keep default.

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
# Enable WAL mode for better concurrency? Not necessary with lock.
conn.execute('PRAGMA journal_mode=WAL')  # optional, may help
db_lock = threading.Lock()

def init_db():
    with db_lock:
        cur = conn.cursor()
        cur.executescript('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','confirmed','cancelled','expired')),
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY(item_id) REFERENCES items(id)
            );
        ''')
        conn.commit()
```

注意：CHECK约束确保状态值。在SQLite中，CHECK在执行INSERT/UPDATE时检查，但我们在应用中控制也可。

现在定义clean_expired:

```python
def clean_expired():
    # must be called with lock held
    cursor = conn.cursor()
    now = time.time()
    rows = cursor.execute('''
        SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?
    ''', (now,)).fetchall()
    if rows:
        # release stock
        for rid, iid, qty in rows:
            conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (qty, iid))
        # update status
        ids = tuple(r[0] for r in rows)
        cursor.execute('UPDATE reservations SET status=\'expired\' WHERE id IN (%s)' % ','.join('?'*len(ids)), ids)
        conn.commit()
```

注意：conn.commit()可能提交所有未提交的修改。如果在已经存在事务中调用，会提交整个事务。但在我们的设计中，clean_expired是每次请求的第一步，此时应该没有未完成的事务（上一个请求已经提交）。所以提交安全。但为了防御，我们可以检查没有事务？简单处理即可。

现在定义Handler。

在Handler中，我们使用self.path、self.command等。

在do_GET和do_POST中，先解析路径（对于POST还要解析body），然后调用handle_request。

注意：有些请求如POST /items，body必须包含JSON，所以我们在do_POST中读取body并解析，如果解析失败返回400。

但是，对于POST /reservations/{id}/confirm 和 cancel，虽然没有body，但理论上可以不需要body。但客户端可能发送空的还是带body? 我们可以忽略body，或者要求没有body。我们可以按照REST，有些不需要body。但为了一致，我们从do_POST读取body并解析，但可能解析为空或错误。如果路由是confirm或cancel，我们不依赖body。所以如果body为空或者不是JSON，我们不应该报错。所以可能需要区分：如果有body并且期望JSON，对于需要body的路由，我们才解析并验证；对于不需要body的路由，我们忽略body。所以do_POST逻辑应该先读body，但尝试解析JSON，如果解析失败，对于需要body的路由返回错误，对于不需要body的路由，忽略。但最简单的：我们总是尝试解析，如果解析失败，将body_json设为None，然后根据路由判断是否需要body。

所以：

```
def do_POST(self):
    content_length = int(self.headers.get('Content-Length', 0))
    body = self.rfile.read(content_length) if content_length else b''
    body_json = None
    if body:
        try:
            body_json = json.loads(body)
        except json.JSONDecodeError:
            body_json = None  # will check later
    # Now handle request
    status, data = self.handle_request(body=body_json)
    self.send_response(status)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data).encode())
```

在handle_request中，根据路由决定是否使用body。例如，对于POST /items，要求body非None且包含name, stock_total；如果body_json为None，返回400。对于POST /reservations，类似。对于confirm和cancel，body不是必需的，我们忽略body内容，或不需要校验。

但是，如果body解析失败（body_json=None），对于需要body的，我们应返回400错误。所以我们在handle_request中根据路由做检查。

所以handle_request可以这样：

```
def handle_request(self, body):
    method = self.command
    path = self.path
    with db_lock:
        clean_expired()
        if method == 'GET' and path == '/items':
            return self.get_items()
        elif method == 'POST' and path == '/items':
            if body is None:
                return (400, {"error": "Invalid JSON"})
            return self.add_item(body)
        elif method == 'POST' and path == '/reservations':
            if body is None:
                return (400, {"error": "Invalid JSON"})
            return self.create_reservation(body)
        elif method == 'POST' and re.match(r'^/reservations/\d+/confirm$', path):
            # extract id using regex
            match = re.match(r'^/reservations/(\d+)/confirm$', path)
            if not match:  # should not happen
                return (400, {"error": "Invalid path"})
            res_id = int(match.group(1))
            return self.confirm_reservation(res_id)
        elif method == 'POST' and re.match(r'^/reservations/\d+/cancel$', path):
            match = re.match(r'^/reservations/(\d+)/cancel$', path)
            if not match:
                return (400, {"error": "Invalid path"})
            res_id = int(match.group(1))
            return self.cancel_reservation(res_id)
        else:
            return (404, {"error": "Not found"})
```

注意：需要import re。

使用正则更安全。

但是，我们还需要确保锁内的异常处理。每个方法中可能有数据库异常，我们可以在方法内部捕获并返回500。

此外，对于GET /items，我们直接返回列表。

现在，关于锁：我们在handle_request中使用with db_lock，但db_lock是模块级锁。注意，在do_GET和do_POST中我们先读取body（可能需要读取请求体），然后调用handle_request。读取body应该在锁外，因为只是I/O。所以OK。

我们还需要确保在发送响应时，我们在锁外（因为handle_request返回后锁释放）。所以没有并发问题。

现在，我们需要考虑错误情况：比如库存不足要返回409，不是400。

实现各方法细节。

**add_item**:

```
def add_item(self, body):
    name = body.get('name')
    stock_total = body.get('stock_total')
    if not name or not isinstance(stock_total, int) or stock_total <= 0:
        return (400, {"error": "Invalid parameters"})
    try:
        cur = conn.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                           (name, stock_total, stock_total))
        conn.commit()
        new_id = cur.lastrowid
        return (201, {"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total})
    except Exception as e:
        conn.rollback()
        return (500, {"error": str(e)})
```

注意：stock_total应为整数，stock_available初始等于stock_total。

**get_items**:

```
def get_items(self):
    try:
        cur = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
        items = []
        for row in cur.fetchall():
            items.append({"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]})
        return (200, items)
    except Exception as e:
        return (500, {"error": str(e)})
```

**create_reservation**:

```
def create_reservation(self, body):
    item_id = body.get('item_id')
    quantity = body.get('quantity')
    ttl_seconds = body.get('ttl_seconds')
    if not all([isinstance(item_id, int), isinstance(quantity, int), isinstance(ttl_seconds, int)]):
        return (400, {"error": "Invalid parameters"})
    if quantity <= 0 or ttl_seconds <= 0:
        return (400, {"error": "Quantity and ttl_seconds must be positive"})
    try:
        # Check item
        cur = conn.execute('SELECT id, stock_available FROM items WHERE id = ?', (item_id,))
        item = cur.fetchone()
        if not item:
            return (404, {"error": "Item not found"})
        stock_available = item[1]
        if stock_available < quantity:
            return (409, {"error": "Insufficient stock"})
        # Reduce stock
        conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id = ?', (quantity, item_id))
        # Create reservation
        now = time.time()
        expires_at = now + ttl_seconds
        cur2 = conn.execute('INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, ?, ?)',
                            (item_id, quantity, 'pending', expires_at, now))
        res_id = cur2.lastrowid
        conn.commit()
        return (201, {
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": now
        })
    except Exception as e:
        conn.rollback()
        return (500, {"error": str(e)})
```

注意：在检查库存后，更新库存和插入预约之间，由于锁保护，不会出现并发修改，所以库存不会变化。所以不需要再次检查。

**confirm_reservation**:

```
def confirm_reservation(self, res_id):
    try:
        cur = conn.execute('SELECT id, status, item_id, quantity FROM reservations WHERE id = ?', (res_id,))
        row = cur.fetchone()
        if not row:
            return (404, {"error": "Reservation not found"})
        if row[1] != 'pending':
            return (400, {"error": "Reservation status must be pending to confirm"})
        # Update status
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('confirmed', res_id))
        conn.commit()
        return (200, {"id": res_id, "status": "confirmed"})
    except Exception as e:
        conn.rollback()
        return (500, {"error": str(e)})
```

**cancel_reservation**:

```
def cancel_reservation(self, res_id):
    try:
        cur = conn.execute('SELECT id, status, item_id, quantity FROM reservations WHERE id = ?', (res_id,))
        row = cur.fetchone()
        if not row:
            return (404, {"error": "Reservation not found"})
        if row[1] != 'pending':
            return (400, {"error": "Reservation status must be pending to cancel"})
        # Release stock
        conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (row[3], row[2]))
        # Update status
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('cancelled', res_id))
        conn.commit()
        return (200, {"id": res_id, "status": "cancelled"})
    except Exception as e:
        conn.rollback()
        return (500, {"error": str(e)})
```

注意：我们可能还需要返回更多信息，但按照要求，返回JSON包含error字段错误，成功响应可以包含id和status等。

现在，考虑一些边界情况：

- 如果POST /items的stock_total是0？我们要求大于0。
- ttl_seconds必须为正整数。
- quantity必须为正整数。
- item_id必须存在。

还要求：每次请求前清理过期预约。我们已经实现。

现在需要考虑线程锁和连接的使用：我们使用单个连接，并且在锁内使用。由于我们使用默认的isolation_level，在执行DML时它会自动开始事务。但是，如果我们连续调用多个execute，它们在一个事务中。我们通常在每个方法中commit。但注意：clean_expired自己commit。在clean_expired后，我们进入方法，方法开始执行自己的操作，可能多个execute，然后commit。所以方法内部transaction是独立的。如果方法中在检查库存后，更新库存和插入预约，这两个DML在同一个事务中，原子性好。如果中间出错，rollback回滚所有。所以好的。

但有一个潜在问题：由于我们每请求使用相同连接，且锁保护，不会有并发问题。但是，在请求内调用clean_expired和后续方法，无事务干扰。

现在关于异常：在get_items中没有commit/rollback，如果查询异常，返回500，不需要回滚。

现在关于锁的粒度：我们在handle_request内获取锁，然后调用clean_expired（可能提交），再调用具体方法。锁在整个过程中保持。这可能阻塞其他线程的请求，但保证了串行一致性。符合要求。

但注意：在clean_expired内部，我们使用conn.commit()，但此时如果之前有未提交的事务（不应该），就会提交。所以没问题。

现在我们需要考虑初始化表时使用锁。在init_db中我们获取锁来执行建表，保证初始化安全。

现在关于服务器启动：init_db()应在创建服务器前执行。

现在代码长度：目前我们只有少量代码，远小于1000行。

现在编写完整代码。

但我们需要处理一个细节：Get /items，应该返回的是数组还是对象？我们可以返回JSON数组。但为了与错误响应一致（错误响应是对象），也可以返回对象包含items数组。但题目没有明确。我觉得返回数组是合理的。但有些客户端可能期望对象。但为了简单，直接返回数组。但注意，如果返回数组，在send_response后，发送json.dumps(data)时，data可能是列表，JSON列表也是有效。所以没问题。

但我们也可以包装成{"items": items}。按照一般的RESTful实践，返回数组是可接受的。但如果你要包含分页等，但这里不需要。所以我们直接返回数组。

为了更一致，我们可以返回{"data": items}，但错误时{"error": ...}。但返回列表也可以。我选择返回列表。

现在，注意HTTP状态码：POST /items返回201 Created。POST /reservations返回201。确认和取消返回200。GET返回200。

关于Content-Type，我们使用application/json。

关于错误，我们使用400、404、409、500。

现在我们需要考虑URL路径中的整数ID，我们使用正则，但也可以使用字符串解析。如果使用正则，需要import re。

现在代码开始。

考虑例子：

- GET /items -> []
- POST /items {"name": "item1", "stock_total": 10} -> 201
- POST /reservations {"item_id": 1, "quantity": 2, "ttl_seconds": 3600} -> 201, 等待1小时后过期。
- POST /reservations/1/confirm -> 200
- POST /reservations/1/cancel -> 400（因为状态已经是confirmed）
- 清理：如果过期，释放库存。

测试。

但需要确保创建预约时，如果stock_total是10，预约2后，available为8。取消后为10。确认后不变。过期后释放。

现在关于过期：在clean_expired中，我们比较expires_at与当前时间。使用time.time()秒数。

现在，我们需要保证在init_db后，conn已经存在。但init_db在模块顶层？我们可以在if __name__ == "__main__"中调用init_db()。但是，在Handler类定义中，我们引用了conn（全局），所以conn必须在Handler定义前定义。所以我们在模块顶部定义conn。然后init_db在__main__中调用。但我们在定义conn时，还没有锁，所以init_db使用锁锁住建表。

但连接建立时，如果数据库不存在会自动创建。所以第一次运行会创建。

现在，代码中注意：在Handler的handle_request方法中，我们使用了db_lock。这个锁在模块级别。

现在，需要考虑Python版本：3.6+，对于f-string可用，但使用format或concat也可以。

现在，编写代码，确保不超过1000行。

我们最终输出完整代码。

注意：需要处理请求头中可能没有Content-Length的情况。对于GET请求，没有body。对于POST请求，通常有Content-Length。但如果不提供，我们可以读取rfile直到EOF？但可能阻塞。我们假设客户端有Content-Length。但如果Content-Length不存在，我们默认为0。

在do_POST中，我们读取body：

```
content_length = int(self.headers.get('Content-Length', 0))
body = self.rfile.read(content_length) if content_length else b''
```

这样安全。

现在，对于body解析，如果body是空字符串，json.loads(b'')会抛出异常，所以我们应该先检查body。如果body为空，body_json设为None。在需要body的路由中检查None。

我们实现：

```
body_json = None
if body:
    try:
        body_json = json.loads(body)
    except json.JSONDecodeError:
        body_json = None  # will cause 400 if body required
```

然后handle_request根据路由判断。

注意：对于POST /confirm和cancel，我们不依赖body，所以body_json = None也是允许的。

现在，我们还需要处理JSON中参数类型。我们使用isinstance检查。注意JSON数字默认是int或float，但我们要求整数，所以检查type为int。对于stock_total，必须是正数。

现在我们还需要处理datetime表示，使用timestamp。

现在，写完整的代码。

考虑使用with语句管理锁，db_lock是threading.Lock对象，支持上下文管理。

另外，注意：在Python的sqlite3中，conn.execute返回游标，但直接执行INSERT后，使用cur.lastrowid获取最后插入的id。我们使用的cur是临时，我们可以使用conn.execute返回的游标。

```
cur = conn.execute(...)
new_id = cur.lastrowid
```

但注意：使用conn.execute()返回的是游标，但该游标可能不包含lastrowid？实际上，它包含。文档：Cursor.lastrowid返回最后插入行的rowid。但只对INSERT有效。

所以我们可以用。

现在，确认和取消方法中，我们不需要返回修改后的数据，只返回状态和id。

现在，我们需要考虑一个微妙点：在cancel_reservation中，释放库存是增加stock_available。但我们需要确保stock_available不超过stock_total？在取消时，预约占用的库存曾从available减掉，现在加回，应该不会超过total（除非多次释放？但状态控制不会重复释放）。但如果我们允许取消已经cancelled的预约？我们检查了状态必须是pending，所以安全。同样，过期也是释放pending的。

现在，在create_reservation中，减少stock_available时，假设库存足够，但即使我们检查了，由于锁保护，不会出现负数。但如果其他线程在锁下，不会出现。但如果我们没有检查，可能会出现负库存。但我们已经检查。

现在，我们需要考虑在清理过期时，如果两批过期预约都处于待处理状态，我们一次性清理。没问题。

现在，整个代码大概100-200行。

现在，输出完整代码。

注意：格式，缩进。

考虑一些改进：对于清理过期的实现，我们也可以使用一条SQL完成，但为了清晰我们使用循环更新库存。

但注意：如果在更新库存时，某个商品同时有多个过期预约，每个预约单独update，但每条update都会增加stock_available。这样是安全的，但如果有多个预约同时过期，每个预约对应一个update，但都在一个事务内，所以最终结果正确。

但也可以用一条SQL：UPDATE items SET stock_available = stock_available + (SELECT SUM(quantity) FROM reservations WHERE status='pending' AND expires_at <= ? AND items.id=reservations.item_id) WHERE id IN (SELECT item_id FROM reservations WHERE ...) 但是还需要将状态更新为expired。可以用复杂查询，但循环简单。

由于我们在锁内，效率不是关键。

注意：在clean_expired中，我们使用conn.execute执行UPDATE items，然后使用cursor.execute更新状态。注意，我们在同一个事务内。最后conn.commit()。但是如果我们有多个过期，多个update，但commit一次。安全。

现在，代码写好。

然后，启动部分。

我们使用ThreadedHTTPServer，并设置allow_reuse_address = True（可选）。在main中：

```
if __name__ == "__main__":
    init_db()
    server = ThreadedHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print('Starting server on 127.0.0.1:8080...')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
```

但注意：使用ThreadingMixIn时，可能会在关闭时等待子线程。但简单可以这样。

需要确保server_thread等。但没问题。

现在，代码完成。

但是，有一个问题：我们在clean_expired中，需要提交事务。但是，如果在handle_request中，我们调用clean_expired，然后继续调用下一个方法，下一个方法可能会在事务未提交的情况下使用连接？我们clean_expired中提交了，所以下一个方法开始时没有事务。所以OK。

但是，我们现在考虑这样的情况：clean_expired中，我们执行了UPDATE items，然后UPDATE reservations，然后commit。如果在commit之前发生了异常（比如方法本身有错误），我们将回滚整个事务（因为我们在方法中捕获异常会rollback）。但clean_expired在被调用时如果异常会怎样？clean_expired内部没有try-except。如果出现数据库错误，异常会向上抛出，导致handle_request中的锁释放？但我们没有在clean_expired中处理异常，所以异常会传播到handle_request，然后会离开with db_lock，触发异常，导致锁释放，但可能残留未提交的事务。然后该线程可能挂起或出错。为了健壮性，我们应该在clean_expired中捕获异常，并输出错误，或者至少确保在异常情况下能回滚。但我们可以让异常传递到handle_request，但我们需要确保在handle_request的with块中捕获异常，然后回滚所有未提交的事务。但handle_request本身没有全局异常处理。我们可以修改handle_request，让其在try块中执行所有操作，并在捕获错误时回滚并返回500。但clean_expired是我们调用的第一个函数，如果它失败了，后续操作无法进行。所以我们应该在clean_expired中捕获异常，记录错误，并尽量保证数据库状态。但理论上，clean_expired很少失败。为了简单，可以让异常传播到handle_request，我们在handle_request中捕获所有异常，回滚事务，返回500。但注意：如果clean_expired在UPDATE后没提交就异常了，那么事务未提交，我们需要回滚。所以我们需要在handle_request中有一个全局的try-except来捕获所有异常，并回滚，然后返回500。但我们的具体方法中有自己的try-except，已经处理了一些异常。但如果在clean_expired中异常未被捕获，将跳转到handle_request的顶层。所以我们可以这样：在handle_request的with db_lock块内，再包裹一个try-except：

```
with db_lock:
    try:
        clean_expired()
        # routing...
    except Exception as e:
        conn.rollback()
        return (500, {"error": str(e)})
```

但注意，我们的路由方法有自己的try-except，它们如果捕获异常返回500而不是抛出，所以不会传播。但clean_expired没有内部捕获，所以如果它失败，会被外层捕获。我们可以在clean_expired中加try-except，但统一在外层处理也可以。

但要确保：如果clean_expired失败，我们回滚所有未提交的更改。因为clean_expired可能未提交，所以我们需要rollback。然后返回500。

但注意：如果clean_expired已经执行部分UPDATE但未提交，rollback会撤销。所以可以。

但更安全的是在clean_expired内部处理异常并回滚。我们可以选择在clean_expired内捕获所有异常，并确保回滚，然后重新抛出或返回。但我们希望将错误传播给调用者。所以我们可以在外层捕获。

因此，我们修改handle_request结构：

```
def handle_request(self, body):
    method = self.command
    path = self.path
    with db_lock:
        try:
            clean_expired()
            # determine routing and call method
        except Exception as e:
            conn.rollback()
            return (500, {"error": str(e)})
```

但路由内的方法如果抛出异常，也会被捕获。我们的方法内部都有try-except，所以不会抛出应该。但如果我们忘记在某个方法中使用try-except，那么外层会捕获。这样可以。

所以我们可以在with db_lock内使用try-except，在except中执行conn.rollback()并返回500。但注意：如果方法内部已经处理了异常并返回了元组，外层不会再捕获。所以外层只捕获未处理的异常。

所以我们可以保持这样：在每个方法内部处理异常并返回500。clean_expired中我们也可以加try-except。

为了代码简洁，我可以在clean_expired中添加异常处理。

但为了稳健，我将在clean_expired中使用try-except，如果失败，回滚并可能记录并忽略？但清理失败会导致后续操作基于错误的状态？最好让错误传播。我们可以在clean_expired中捕获异常，确保回滚，然后重新抛出。所以还是外层处理。

简单起见，我们使用外层try-except。

现在，修改代码结构：

```
def handle_request(self, body):
    method = self.command
    path = self.path
    with db_lock:
        try:
            clean_expired()  # may raise
            # routing
            if condition:
                result = self.some_method(body)
            ...
            return result
        except Exception as e:
            conn.rollback()
            return (500, {"error": "Internal server error: " + str(e)})
```

但注意：如果在routing中我们调用了方法，该方法返回了响应，但方法内部可能commit了。如果方法内部出现未捕获异常，则会被外层捕获，但此时方法内部可能已经执行部分修改（未提交？因为如果方法内部有try-except捕获异常并返回500，不会抛出。所以外层只捕获未处理异常。所以没问题。

现在，对于clean_expired，如果它执行过程中出现异常（比如数据库锁错误），我们会rollback，然后返回500。但是clean_expired中如果已经执行了部分UPDATE，但未提交，rollback撤销。所以数据库状态一致。

注意：如果clean_expired成功，但后续路由方法中出现错误，路由方法内部的异常处理会捕获并返回500，同时已经回滚了它自己的修改（如果路由方法内部有try-except并捕获了异常，它应该已经回滚并返回500；如果异常未被捕获，被外层捕获，外层回滚所有未提交，包括clean_expired的修改？但clean_expired已经在之前提交了（它调用了commit），所以它的修改已经持久化，不能回滚。所以如果路由方法抛出未捕获异常，外层回滚对clean_expired的提交无效（因为已经提交）。但clean_expired的提交在之前完成。所以我们需要明确：如果外层捕获异常时调用rollback，但数据库已经提交了先前的clean_expired事务，则rollback只会回滚当前事务。所以我们需要确保clean_expired的提交与后续操作不在同一事务中。这正是我们的设计：clean_expired自己提交，然后路由方法单独开始新事务。所以外层捕获到异常时，如果发生在路由方法内，回滚只会回滚路由方法的事务（如果尚未提交），而clean_expired已提交，所以不会破坏。如果异常发生在clean_expired中，则clean_expired尚未提交，所以回滚整个事务，包括clean_expired部分，然后返回500。这合理。

但是，如果clean_expired已经成功提交，然后路由方法中出现未捕获异常，外层捕获并执行rollback，但此时没有未提交事务（因为路由方法可能已经开始事务但未提交？如果路由方法内已经执行了修改但未提交，那么事务是活动的，rollback会回滚那些修改。如果路由方法是查询操作（没有修改），则没有事务。所以总体没问题。

因此，我们的外层try-except是安全的。

我们只需要在路由方法内部确保每个修改方法都有自己的try-except以及最后rollback吗？也许我们可以让外层统一处理，但路由方法内部有些错误需要返回特定的状态码（如409、400），这些应由方法内部捕获并返回，而不是抛出异常。所以方法内部应捕获已知业务异常并返回相应错误，不抛出。所以未捕获异常应该是意外错误。

所以我们可以采用两种策略：

1. 每个方法内部使用try-except，捕获数据库异常并返回500（含错误信息）。同时可能回滚事务。
2. 外层try-except捕获所有异常并返回500，但需要确保方法内部不抛出业务异常（如库存不足）。所以方法内部应手动返回409。

我倾向方法内部处理自己的异常，外层只捕获意外异常（如程序错误）。所以我们可以让方法内部捕获异常并回滚，返回500；同时外层也捕获以防止未捕获的异常。但内部如果已经处理了并返回了，外层不会捕获。

所以我们可以同时保留。

为简化，我们可以让每个方法内部返回响应，并且如果在数据库操作中出现意外异常，我们捕获并返回500，同时回滚。如果内部没有捕获，外层捕获到也会回滚并返回500，但内部的修改可能已经部分执行但未提交，外层回滚。所以安全。但为了代码整洁，我们可以在每个方法中不再使用try-except，而是依赖外层，但在方法内部处理业务错误（如库存不足）时，我们需要返回特定响应而不使用异常。所以我们需要在某些情况下使用条件判断。对于数据库错误，我们可以在方法中不显式捕获，让外层捕获。但这样，如果方法中有多个数据库操作，其中一个失败，后续未执行，外层捕获，回滚所有，返回500。这可行。但注意：如果方法中执行了commit，然后在后续操作中失败，之前已提交不能回滚。但我们的方法通常是在所有操作完成后才commit。所以如果我们在方法末尾commit，那么在提交之前发生异常，回滚可以撤销。如果提交之后发生错误（比如最后一行return之前），实际上已经提交，但return不会导致异常。所以只有数据库异常可能导致未提交时异常。所以让外层捕获是可以的。但我们需要确保在方法中不提交直到最后。所以我们可以将commit放在方法最后（或在所有操作之后）。对于create_reservation，我们最后commit。如果之前有错误（如库存不足），我们返回响应而不commit。所以我们是先检查，然后执行修改，然后commit；如果检查失败，直接返回，没有修改，也不需要回滚。所以方法内部可能不会产生需要回滚的异常。对于数据库约束错误等，可能在execute时触发异常。这时外层会捕获并回滚，同时我们已经执行了一些修改。但那些修改是未提交的，外层回滚。所以我们不需要在每个方法内显式处理异常。但是，如果我们在execute后没有立即检查错误，python的sqlite3如果违反约束会抛出IntegrityError，我们可以在外层处理。所以我们可以在每个方法中不使用try-except，而是依赖外层捕获所有异常，并在外层执行conn.rollback()。但需要注意：如果方法中我们调用了conn.execute()后没有commit，然后异常发生，外层捕获并回滚，但如果我们已经调用了commit，则回滚不起作用。所以我们需要确保在方法内commit只在所有操作成功后执行。所以我们设计每个方法只在最后返回前commit。如果前面出错，则直接return错误响应，不commit。所以方法内不会有commit后还出异常的情况。所以依赖外层捕获数据库异常是合理的。

但有些方法比如confirm_reservation，我们只有一条UPDATE和commit。如果UPDATE成功，commit后返回。如果UPDATE出错，异常被外层捕获并回滚（此时commit未执行）。所以没问题。

所以我们可以简化：不在每个方法内使用try-except，而是让外层捕获所有异常并回滚。但这样，如果出现业务错误（如库存不足），我们不是通过异常，而是通过判断，返回响应。所以外层不会捕获这些正常错误。所以可以。

但注意：如果clean_expired调用后没有异常，但后续方法中可能因为参数等等错误返回400，不会触发异常。所以整体结构是：在with db_lock内：try: clean_expired(); 然后根据路由调用对应方法；对应方法可能返回(status, data)或者raise Exception(意外)；我们在try内部检查返回值并返回；如果捕获到异常，则回滚并返回500。

但是我们对应方法如果返回了响应，则直接返回。所以我们可以这样做。

但是，我们需要在方法内部处理回滚吗？如果方法内调用了execute并发生了异常，异常会抛出到外层，我们外层会回滚。但如果我们方法内已经捕获了该异常并返回了500，那外层不会捕获，但此时方法内可能已经执行了部分execute，但未提交，方法内捕获异常后可能没有回滚，导致事务一直未提交或未回滚，这可能导致后续同一个线程内的操作使用同一连接产生问题。所以如果我们在方法内捕获异常并返回500，我们必须确保在该方法内回滚所有未提交的事务。所以如果我们选择不在方法内处理异常，则不需要内部捕获。所以最好统一在外层处理异常，方法内只处理业务逻辑，不处理数据库异常。但我们需要在某些步骤中检查条件（如库存不足）并返回错误，这属于正常流程。

所以我认为统一在外层处理数据库异常更简洁。

我开始重构：所有数据库操作方法（如add_item, get_items等）不再内部使用try-except，只进行条件判断和数据库操作，最后commit。如果出现数据库异常，它将抛出，被外层捕获，外层回滚事务并返回500。但需要注意：如果方法内有多个execute，其中一个失败，外层会回滚所有未提交操作。但如果我们方法内先执行了一些修改，然后检查条件发现错误（比如库存不足），我们需要回滚吗？在库存不足的情况下，我们之前没有执行修改，所以无需回滚。但如果我们在检查后执行修改，然后后续操作失败，我们需要回滚。在我们的实现中，库存不足是在修改之前检查的，所以不会出现部分修改后需要回滚的情况。所以外层捕获错误并回滚适用于后续修改中的意外错误。

但有一个例外：在create_reservation中，我们是先检查库存，如果足够则执行UPDATE减少库存和INSERT预约，然后commit。如果UPDATE成功，INSERT也成功，则commit成功。但如果INSERT失败（例如外键约束失败），异常会抛出，此时UPDATE已经执行但未提交，外层回滚会撤销UPDATE。所以正确。

但是，如果UPDATE成功，INSERT也成功，但commit失败？commit可能在磁盘写入时出错，这也会抛出异常，外层捕获回滚，但UPDATE和INSERT尚未提交，所以回滚撤销。所以也没问题。

因此，我们可以让内层方法不捕获异常。

但需要注意：有些业务错误如库存不足、预约状态错误等，不是异常，是条件检查，我们在方法内通过if判断并返回错误响应，不执行数据库修改。所以没有问题。

所以，我决定在handle_request的顶层try-except中捕获所有异常（包括数据库异常），并回滚，返回500。方法内部不再使用try-except。

但需要注意：当方法内返回错误响应时（如400，409），这些不触发异常，直接返回。所以整个流程清晰。

但是，我们还需要在clean_expired中捕获异常吗？同样，让外层捕获。

修改代码：

- clean_expired不再有try-except。
- 每个具体方法不再有try-except。
- handle_request: 在with db_lock: try: ... except: conn.rollback(); return (500, {"error": "Internal server error"}).

但注意：我们需要在异常时获取错误信息，可以使用traceback，但简单起见，返回通用错误。也可以返回str(e)。

现在，对于GET /items，如果没有异常，直接返回查询结果。

但是，在get_items中，我们查询后要确保没有异常。如果有异常（如数据库连接问题），外层捕获。

所以代码简化。

现在，考虑body的解析：我们可能在do_POST中解析body，如果body不是JSON，我们设置body_json=None，但在需要body的路由中返回400。我们可以在路由方法内检查body是否为None或缺少参数，返回400。这样，如果body_json是None，并且路由需要body（如/items POST），我们在方法内检查body is None或参数缺失，返回400。如果不返回，则可能引发KeyError？所以需要检查。

为了安全，在add_item中，我们首先检查body是None？实际上body可能是dict，但如果body是None，我们直接返回400。所以：

```
def add_item(self, body):
    if body is None:
        return (400, {"error": "Invalid JSON"})
    name = body.get('name')
    stock_total = body.get('stock_total')
    if not name or not isinstance(stock_total, int) or stock_total <= 0:
        return (400, {"error": "Invalid parameters"})
    ...
```

其他类似。

对于confirm和cancel，它们不依赖body，所以即使body是None也没关系。

另外，对于POST /reservations，需要body。

所以路由方法中自己检查。

现在，还需要考虑路径解析可能出错，如ID非整数，我们在路由选择时使用正则，如果匹配但转换失败，返回400。在handle_request中，我们可以在匹配正则后直接转换，如果转换失败返回400。所以不需要到具体方法。

现在，看来代码可以更简洁。

现在，重新实现。

关于线程锁：我们在handle_request中获取。注意，当我们调用clean_expired时，我们假设conn可用。但如果在init_db时我们没有在main中调用，或者数据库初始化失败，需要处理。init_db会在启动时执行，如果失败，程序退出。所以可以。

conn的isolation_level：我们使用默认（''），即自动开始事务。但在clean_expired中，我们使用了conn.execute()，它会自动开始事务，然后我们commit。在具体方法中，我们也使用conn.execute()，自动开始事务（如果当前没有事务）。由于clean_expired已经commit，所以方法开始时没有事务。

但是，如果clean_expired没有执行任何修改（没有过期预约），它没有执行UPDATE，因此也没有事务开始。所以方法开始也无事务。

所以没问题。

但注意：如果在clean_expired中，我们执行了SELECT（查询），不会开始事务。所以OK。

现在，我们实现代码。

但是，对于确认和取消，我们只需要id，不需要body。但我们仍然在do_POST中读取了body，并且如果body不是JSON或者为空，body_json为None。在路由方法中我们不使用它，所以可以。

现在，服务器启动部分。

为了使用ThreadingMixIn，我们需要导入ThreadingMixIn。但标准库是socketserver.ThreadingMixIn。但我们可以直接使用http.server.ThreadingHTTPServer？从Python3.7开始有ThreadingHTTPServer，但为了兼容，我们使用ThreadingMixIn。

所以：

```
from socketserver import ThreadingMixIn
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
```

设置daemon_threads以便在退出时线程自动停止。

现在，所有步骤完成。

现在，编写最终代码。

此外，需要注意在解析路径时，我们使用re.match，需要import re。

我们需要在handle_request中根据method和path路由。注意POST和GET的处理。

另外，如果路径是/，可能返回404。

现在，确保每次请求前清理，我们在with db_lock进入后立即调用clean_expired()。

但是，如果我们希望清理操作不占用锁太长时间并且可以及时更新库存，但既然我们锁保护，没问题。

现在，额外考虑：如果请求是GET /items，它也需要清理过期吗？是的，按照要求每次请求前清理，所以GET也需要清理，以便库存显示准确。

现在，代码长度很小，肯定少于1000行。

现在，输出代码。

但注意：我们需要使用JSON格式返回错误，所以返回的data必须是dict（或list）。我们在错误时返回{"error": "message"}。

现在，考虑HTTP响应的状态码映射：

- 400: Bad Request (参数错误)
- 404: Not Found (路径不存在或商品ID不存在)
- 409: Conflict (库存不足)
- 201: Created
- 200: OK
- 500: Internal Server Error

我们统一在发送响应时使用status和data。

现在，注意：在do_GET和do_POST中，我们调用handle_request，然后发送响应。但do_GET可能没有body，所以我们在do_GET中不解析body，直接调用handle_request(body=None)。

所以do_GET:

```
def do_GET(self):
    status, data = self.handle_request(body=None)
    self.send_response(status)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data).encode())
```

do_POST:

```
def do_POST(self):
    content_length = int(self.headers.get('Content-Length', 0))
    body = self.rfile.read(content_length) if content_length else b''
    body_json = None
    if body:
        try:
            body_json = json.loads(body)
        except json.JSONDecodeError:
            body_json = None
    status, data = self.handle_request(body=body_json)
    self.send_response(status)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(data).encode())
```

注意：对于GET请求，没有body，所以不需要读取body。我们直接传给handle_request body=None。

在handle_request中，如果method是GET，body参数被忽略。但对于POST，body可能为None。

现在，我们需要在路由中区分GET和POST。我们已经使用self.command。

现在，现在我们来处理取消和确认的路径：可能存在/reservations/{id}? 但我们只处理/confirm和/cancel结尾。

使用正则匹配：r'/reservations/\d+/confirm' 和 r'/reservations/\d+/cancel'

注意：path可能以/结尾？不应该。但我们可以使用re.fullmatch或re.match。re.match是从开头匹配，所以可以使用pattern + '$'，确保完全匹配。所以用re.fullmatch或使用re.match并检查匹配长度。最好使用fullmatch。

所以：if re.fullmatch(r'/reservations/\d+/confirm', path): ... 然后提取数字部分。

提取用：m = re.match(r'/reservations/(\d+)/confirm', path) 然后 res_id = int(m.group(1))。但使用fullmatch后也可以使用search。我倾向于使用match并捕获。

因为fullmatch要求整个字符串匹配模式，所以也可以用search并确保匹配整个字符串。

我使用：

```
m = re.fullmatch(r'/reservations/(\d+)/(confirm|cancel)', path)
if m:
    action = m.group(2)
    res_id = int(m.group(1))
    if action == 'confirm':
        return self.confirm_reservation(res_id)
    else:
        return self.cancel_reservation(res_id)
```

这样合并为一个条件。

所以handle_request可以写成：

```
with db_lock:
    try:
        clean_expired()
        if self.command == 'GET' and self.path == '/items':
            return self.get_items()
        elif self.command == 'POST':
            if self.path == '/items':
                return self.add_item(body)
            elif self.path == '/reservations':
                return self.create_reservation(body)
            else:
                m = re.fullmatch(r'/reservations/(\d+)/(confirm|cancel)', self.path)
                if m:
                    res_id = int(m.group(1))
                    action = m.group(2)
                    if action == 'confirm':
                        return self.confirm_reservation(res_id)
                    else:
                        return self.cancel_reservation(res_id)
        return (404, {"error": "Not found"})
    except Exception as e:
        conn.rollback()
        return (500, {"error": f"Internal server error: {str(e)}"})
```

注意：这里使用f-string，需要Python3.6+。但我们可以用format。

现在，我们在方法内部不再处理异常，但需要确保库存不足等业务错误不触发异常，而是返回响应。所以方法内部只进行条件判断和数据库操作。

但是，如果因为数据库约束（如外键）导致execute执行失败，会抛出异常，被外层捕获并回滚。

现在，我们可以编写具体方法。

**get_items**:

```
def get_items(self):
    cur = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
    items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in cur.fetchall()]
    return (200, items)
```

**add_item**:

```
def add_item(self, body):
    if body is None:
        return (400, {"error": "Invalid JSON"})
    name = body.get('name')
    stock_total = body.get('stock_total')
    if not name or not isinstance(stock_total, int) or stock_total <= 0:
        return (400, {"error": "Invalid parameters: name (string) and stock_total (positive int) required"})
    cur = conn.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                       (name, stock_total, stock_total))
    conn.commit()
    new_id = cur.lastrowid
    return (201, {"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total})
```

**create_reservation**:

```
def create_reservation(self, body):
    if body is None:
        return (400, {"error": "Invalid JSON"})
    item_id = body.get('item_id')
    quantity = body.get('quantity')
    ttl_seconds = body.get('ttl_seconds')
    if not all([isinstance(item_id, int), isinstance(quantity, int), isinstance(ttl_seconds, int)]):
        return (400, {"error": "Invalid parameters: item_id, quantity, ttl_seconds must be integers"})
    if quantity <= 0 or ttl_seconds <= 0:
        return (400, {"error": "Quantity and ttl_seconds must be positive"})
    # Check item existence and stock
    cur = conn.execute('SELECT id, stock_available FROM items WHERE id = ?', (item_id,))
    item = cur.fetchone()
    if not item:
        return (404, {"error": "Item not found"})
    available = item[1]
    if available < quantity:
        return (409, {"error": "Insufficient stock"})
    # Reduce stock and create reservation
    conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id = ?', (quantity, item_id))
    now = time.time()
    expires = now + ttl_seconds
    cur2 = conn.execute('INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, ?, ?)',
                        (item_id, quantity, 'pending', expires, now))
    res_id = cur2.lastrowid
    conn.commit()
    return (201, {
        "id": res_id,
        "item_id": item_id,
        "quantity": quantity,
        "status": "pending",
        "expires_at": expires,
        "created_at": now
    })
```

**confirm_reservation**:

```
def confirm_reservation(self, res_id):
    cur = conn.execute('SELECT id, status FROM reservations WHERE id = ?', (res_id,))
    row = cur.fetchone()
    if not row:
        return (404, {"error": "Reservation not found"})
    if row[1] != 'pending':
        return (400, {"error": f"Reservation status must be pending to confirm, current: {row[1]}"})
    conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('confirmed', res_id))
    conn.commit()
    return (200, {"id": res_id, "status": "confirmed"})
```

**cancel_reservation**:

```
def cancel_reservation(self, res_id):
    cur = conn.execute('SELECT id, status, item_id, quantity FROM reservations WHERE id = ?', (res_id,))
    row = cur.fetchone()
    if not row:
        return (404, {"error": "Reservation not found"})
    if row[1] != 'pending':
        return (400, {"error": f"Reservation status must be pending to cancel, current: {row[1]}"})
    item_id = row[2]
    quantity = row[3]
    conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (quantity, item_id))
    conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('cancelled', res_id))
    conn.commit()
    return (200, {"id": res_id, "status": "cancelled"})
```

注意：在confirm和cancel中，我们不需要返回额外信息，但简单返回id和status。

现在，clean_expired函数：

```
def clean_expired():
    now = time.time()
    rows = conn.execute('SELECT id, item_id, quantity FROM reservations WHERE status = ? AND expires_at <= ?',
                        ('pending', now)).fetchall()
    if rows:
        for rid, iid, qty in rows:
            conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (qty, iid))
        ids = tuple(r[0] for r in rows)
        conn.execute('UPDATE reservations SET status = ? WHERE id IN (%s)' % ','.join('?'*len(ids)),
                     ('expired',) + ids)
        conn.commit()
```

注意：在conn.execute中使用参数化查询对于IN子句，我们需要动态构建参数，如上。

现在，关于连接设置：我们没有设置isolation_level，使用默认。但我们需要确保在conn.execute('UPDATE ...')时自动开始事务。这是默认行为。但注意：在clean_expired中，我们可能同时执行多个UPDATE items，然后一个UPDATE reservations，然后commit。所有都在一个事务中。在commit后，事务结束。所以没问题。

在create_reservation中，我们执行UPDATE items和INSERT，然后commit。在confirm中，一个UPDATE，commit。所以每个方法内都能保证原子性。

现在，考虑如果多个UPDATE items在一个事务中，但其中某个失败，整个回滚。由于锁内，不会冲突。

现在，我们还需要考虑在没有锁的情况下，如果在init_db或其他地方使用连接。初始化时我们使用锁来建表。

现在，我们写if __name__ == "__main__":部分。

```
if __name__ == "__main__":
    init_db()
    server = ThreadedHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server started on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```

关闭时，需要关闭数据库连接吗？可以加conn.close()，但不是必须。

现在，完整代码可以工作。

但是，考虑到ThreadingMixIn会为每个请求创建新线程，而我们使用全局锁，所以多线程实际串行处理数据库操作。但处理响应发送可以在锁外，所以可以有一些并发。但整体简单。

现在，我们检查所有要求：

- 使用Python 3标准库：是。
- 单文件，server.py：是。
- 不使用第三方库：是。
- 总代码不超过1000行：显然。
- sqlite3持久化，首次自动建表：是。
- 商品字段：id, name, stock_total, stock_available。
- 预约字段：id, item_id, quantity, status, expires_at, created_at。
- API:
  1. GET /items：列出商品和可用库存。✔
  2. POST /items：新增商品。✔
  3. POST /reservations：创建预约，库存不足返回409。✔
  4. POST /reservations/{id}/confirm：确认。✔
  5. POST /reservations/{id}/cancel：取消。✔
- 每次请求前清理过期pending。✔
- 并发处理：使用锁和事务。✔
- 返回JSON，错误包含error字段。✔
- if __name__ == "__main__"启动入口，默认127.0.0.1:8080。✔

还有一些细节：

- 对于POST /items，参数是name, stock_total。我们实现了。
- POST /reservations参数item_id, quantity, ttl_seconds。
- 确认预约后，不再释放库存（通过更新状态为confirmed，不再增加stock_available）。✔
- 取消预约释放库存。✔

现在，考虑一个问题：过期的预约被清理时，释放库存，这符合逻辑。但如果一个预约过期后，用户再尝试确认或取消，由于状态已变为expired，所以返回错误。但我们的clean_expired在每请求前执行，意味着如果用户在过期后立即发出confirm请求，请求进来，先清理，将状态设为expired，然后confirm检查状态不是pending，返回400。所以合理。

现在，检查一些边界：TTL seconds如果是0或负数？我们要求ttl_seconds > 0，否则返回400。同样quantity必须>0。

对于stock_total也要>0。

现在，对于POST /items的stock_total可能不是整数？我们使用isinstance(stock_total, int)检查。注意JSON中数字默认是int或float。如果stock_total是浮点数，isinstance会False，所以返回400。要求明确整数。

同样item_id其他参数。

现在，对于path解析，我们使用re.fullmatch，需要导入re。

现在，确保在路由时，对于不匹配的返回404。

现在，代码基本完成。

但还有一点：对于POST /reservations/{id}/confirm 和 cancel，HTTP规范建议使用PUT或PATCH，但题目要求使用POST，所以我们遵循。

现在，我们还需要处理如果body是空字符串的情况：json.loads(b'')会抛异常，我们捕获后body_json = None。所以对于需要body的请求，返回400。对于confirm和cancel，body_json为None，但我们不检查，所以没问题。

现在，关于Content-Length，如果客户端未发送，我们默认0。

现在，关于确保幂等性：没有要求。

现在，我们还需要在Handler的do_*方法中处理可能发生的异常？例如在发送响应时可能BrokenPipe，但通常忽略。

现在，我们还需要在handle_request中处理未匹配路径返回404。

现在，最后，我们需要确保在do_POST中，如果读取body时发生错误（如Content-Length大于实际），可能阻塞，但假设客户端正确。

现在，代码可用。

但还有一个小问题：在clean_expired中，我们更新库存时，对于每个过期预约单独UPDATE。如果有很多过期预约，会执行多个UPDATE，但都在一个事务中。但效率不是问题。

更好的是使用一条SQL：

```
UPDATE items SET stock_available = stock_available + (
    SELECT SUM(quantity) FROM reservations WHERE status='pending' AND expires_at <= ? AND items.id = reservations.item_id
) WHERE id IN (SELECT item_id FROM reservations WHERE status='pending' AND expires_at <= ?)
```

但这样需要两次扫描，而且不能同时更新状态。我们可以先更新库存，然后更新状态。但使用一条SQL更新库存可能更高效，但为了简单，我们使用循环。

但我们仍然需要注意：在更新状态时，我们使用'expired'，但我们在状态中增加了expired，所以我需要在建表时CHECK约束中加上'expired'。在init_db中我们使用了CHECK(status IN ('pending','confirmed','cancelled','expired'))。所以没问题。

现在，需要考虑如果数据库更新意外失败，连接状态未知。外层捕获后会调用rollback，可能需要重新设置连接？简单处理即可。

现在，还有一个潜在问题：如果库存available降至负数？我们检查库存足够才减少，所以不会负数。但如果在并发下没有锁，可能，但我们有锁，所以不会。

现在，最终代码。

但有一点：我们在Handler中定义的方法都是实例方法，但我们在handle_request中调用self.get_items()等。所以没问题。

现在，提供完整代码。需要包含所有import。

代码顺序：

1. imports
2. constants
3. conn, db_lock
4. init_db()
5. clean_expired()
6. Handler class with methods
7. ThreadedHTTPServer class
8. main block

注意：init_db在main中调用，但conn是全局，所以需要先定义conn。

现在，仔细编写代码。

由于我们使用全局conn，但在init_db中我们使用了db_lock。但db_lock也在全局。所以顺序：先创建conn，然后定义db_lock。然后定义init_db函数。然后定义Handler。然后在main中调用init_db，然后启动服务器。

但需要注意：在定义handler时，可能引用conn和db_lock, clean_expired，这些在之前定义，没问题。

现在，编写完整代码。

我们需要一个函数来初始化数据库：创建表。我们在init_db中使用db_lock，但初始化可能与其他请求竞争？由于在启动时没有请求，所以安全。但为了统一，我们加锁。

但现在，在init_db中，我们获取锁，但此时还没有服务器，但多线程没有开始，所以其实不需要。但加锁也无妨。

现在，代码细节：

在init_db中的CREATE TABLE语句，我们使用executescript，它可以执行多个语句。注意：executescript会首先提交任何未完成的事务，所以我们最好在连接刚创建且没有事务时使用。

现在，我们开始编写代码。

考虑到我们需要在clean_expired中使用conn.execute，但conn已经在全局。

现在，关于时间戳，我们使用time.time()返回float。

现在，我们可能会希望将expires_at存储为real。

现在，完成。

但还有一个问题：我们创建预约时，created_at和expires_at都使用timestamp。但在返回给客户端时，我们使用浮点数。客户端可能期望某种格式。但题目没有要求，所以我们传timestamp。

现在，检查确认和取消的返回：只包含id和status，没有时间。但题目没有规定返回格式。我们这样返回也可以。

现在，我们确保在POST /items返回的JSON包含id, name, stock_total, stock_available。

现在，在GET /items返回每个商品的这些字段。

现在，在POST /reservations返回id, item_id, quantity, status, expires_at, created_at。

现在，所有要求满足。

现在，我们还需要考虑如果客户端发送的JSON中参数是字符串数字？例如"stock_total": "10"，我们的检查会失败，返回400。我们希望严格，所以没问题。

现在，我打算输出代码。

注意：在handle_request中，使用with db_lock: ...，但如果在with块中调用的方法返回前遇到了异常，需要确保回滚。我们的catch会捕获所有异常。但注意，如果方法中直接return了（如400），不会触发catch。但如果在commit之后，post-commit错误（如return时异常不会发生），所以安全。

但是，如果某个方法中，我们执行了多个execute，然后执行commit，如果commit失败，异常被捕获，回滚？但回滚对于已提交的事务无效，但commit失败意味着事务还没有提交，所以rollback可以撤销之前的修改。正确。

现在，一个潜在问题：在clean_expired中，如果没有任何过期预约，不会启动事务。但有些方法如create_reservation会启动事务。如果clean_expired没有启动事务，create_reservation开始事务，然后commit，所以没问题。

现在，确保在clean_expired中我们提交了，所以clean_expired的事务结束。

现在，测试一下逻辑：假设两个请求并发，都通过了do_*方法，在handle_request的with db_lock处竞争。一个获取锁，执行clean、方法、commit，返回响应，释放锁。另一个随后进入。所以串行。

现在，关于锁的性能：因为只有一个连接，锁保护了数据库访问。但也可接受。

现在，最后，考虑Python版本：使用f-string，需要3.6。但我们可以用format兼容。但f-string更简洁。但为了兼容，我们可能用format。但题目无版本要求，我们可以用f-string。

但为了最大兼容，使用.format()更好。但没关系，3.5不支持f-string但3.5已经EOL。我使用f-string。

现在，代码预计150行左右。

现在，写出完整代码。

记得在init_db中，我们需要check约束。但注意：SQLite在版本3.6.19开始支持CHECK约束。没问题。

现在，编写代码。

另外，在clean_expired中的UPDATE reservations SET status = ? WHERE id IN (...)时需要构建参数。我们使用字符串格式：'UPDATE reservations SET status = ? WHERE id IN ({})'.format(','.join('?'*len(ids))) 这没问题。

但注意：如果ids是空tuple，则不会进入if rows:，所以安全。

现在，在clean_expired中，我们先commit了，但后续可能有异常？我们在外层捕获，但如果clean_expired commit之后出现异常，外层捕获但事务已经提交，rollback不会影响。但这种情况可能在于clean_expired commit后，可能有其他操作，但异常发生在commit后（如从clean_expired返回后，但在下一次execute之前），由于没有未提交事务，rollback不做任何事。所以安全。但也注意，如果commit后然后外层捕获到异常（来自后续方法），回滚会将后续方法的事务回滚（如果未提交），但不会影响已提交的clean_expired。所以结构良好。

现在，所有OK。

现在，编写最终代码。

但需要留意：我们使用了global conn, db_lock, 但可能跨模块可见，但只有单文件，没关系。

现在，开始写：

```python
#!/usr/bin/env python3
import json
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import re

# Database file
DB_FILE = 'inventory.db'

# Global database connection and lock
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
conn.execute('PRAGMA journal_mode=WAL')  # optional, for better concurrency
db_lock = threading.Lock()

def init_db():
    """Initialize database tables if not exist."""
    with db_lock:
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','confirmed','cancelled','expired')),
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY(item_id) REFERENCES items(id)
            );
        ''')
        conn.commit()

def clean_expired():
    """Cancel expired pending reservations and release stock."""
    now = time.time()
    rows = conn.execute('''
        SELECT id, item_id, quantity FROM reservations WHERE status = ? AND expires_at <= ?
    ''', ('pending', now)).fetchall()
    if rows:
        # Release stock for each expired reservation
        for rid, iid, qty in rows:
            conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (qty, iid))
        # Mark as expired
        ids = tuple(r[0] for r in rows)
        placeholders = ','.join(['?'] * len(ids))
        conn.execute(
            'UPDATE reservations SET status = ? WHERE id IN ({})'.format(placeholders),
            ('expired',) + ids
        )
        conn.commit()

class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for inventory reservation service."""

    def do_GET(self):
        status, data = self.handle_request(body=None)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else b''
        body_json = None
        if body:
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                body_json = None
        status, data = self.handle_request(body=body_json)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def handle_request(self, body):
        """Process request under lock."""
        method = self.command
        path = self.path
        with db_lock:
            try:
                clean_expired()

                if method == 'GET' and path == '/items':
                    return self.get_items()

                if method == 'POST':
                    if path == '/items':
                        return self.add_item(body)
                    elif path == '/reservations':
                        return self.create_reservation(body)
                    else:
                        # Check for confirm/cancel
                        m = re.fullmatch(r'/reservations/(\d+)/(confirm|cancel)', path)
                        if m:
                            res_id = int(m.group(1))
                            action = m.group(2)
                            if action == 'confirm':
                                return self.confirm_reservation(res_id)
                            else:
                                return self.cancel_reservation(res_id)

                return (404, {"error": "Not found"})
            except Exception as e:
                conn.rollback()
                return (500, {"error": f"Internal server error: {str(e)}"})

    def get_items(self):
        cur = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
        items = []
        for row in cur.fetchall():
            items.append({
                "id": row[0],
                "name": row[1],
                "stock_total": row[2],
                "stock_available": row[3]
            })
        return (200, items)

    def add_item(self, body):
        if body is None:
            return (400, {"error": "Invalid JSON"})
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            return (400, {"error": "Invalid parameters: name (string) and stock_total (positive int) required"})
        cur = conn.execute(
            'INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
            (name, stock_total, stock_total)
        )
        conn.commit()
        new_id = cur.lastrowid
        return (201, {
            "id": new_id,
            "name": name,
            "stock_total": stock_total,
            "stock_available": stock_total
        })

    def create_reservation(self, body):
        if body is None:
            return (400, {"error": "Invalid JSON"})
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if not all([isinstance(item_id, int), isinstance(quantity, int), isinstance(ttl_seconds, int)]):
            return (400, {"error": "Invalid parameters: item_id, quantity, ttl_seconds must be integers"})
        if quantity <= 0 or ttl_seconds <= 0:
            return (400, {"error": "Quantity and ttl_seconds must be positive"})

        # Check item existence and available stock
        cur = conn.execute('SELECT id, stock_available FROM items WHERE id = ?', (item_id,))
        item = cur.fetchone()
        if not item:
            return (404, {"error": "Item not found"})
        available = item[1]
        if available < quantity:
            return (409, {"error": "Insufficient stock"})

        # Reserve stock
        conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id = ?', (quantity, item_id))
        now = time.time()
        expires = now + ttl_seconds
        cur2 = conn.execute(
            'INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, ?, ?)',
            (item_id, quantity, 'pending', expires, now)
        )
        res_id = cur2.lastrowid
        conn.commit()
        return (201, {
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires,
            "created_at": now
        })

    def confirm_reservation(self, res_id):
        cur = conn.execute('SELECT id, status FROM reservations WHERE id = ?', (res_id,))
        row = cur.fetchone()
        if not row:
            return (404, {"error": "Reservation not found"})
        if row[1] != 'pending':
            return (400, {"error": f"Reservation status must be pending to confirm, current: {row[1]}"})
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('confirmed', res_id))
        conn.commit()
        return (200, {"id": res_id, "status": "confirmed"})

    def cancel_reservation(self, res_id):
        cur = conn.execute('SELECT id, status, item_id, quantity FROM reservations WHERE id = ?', (res_id,))
        row = cur.fetchone()
        if not row:
            return (404, {"error": "Reservation not found"})
        if row[1] != 'pending':
            return (400, {"error": f"Reservation status must be pending to cancel, current: {row[1]}"})
        item_id = row[2]
        quantity = row[3]
        # Release stock
        conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (quantity, item_id))
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('cancelled', res_id))
        conn.commit()
        return (200, {"id": res_id, "status": "cancelled"})

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""
    daemon_threads = True

if __name__ == "__main__":
    init_db()
    server = ThreadedHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server starting on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```

注意：在creat_reservation中，我们使用all([...])检查，需要注意，如果参数类型不对，返回400。但是我们使用了isinstance检查整数。但注意：如果item_id是None，则isinstance(None, int)为False，所以返回400。所以正确。

现在，可能有人会传入浮点数作为整数，会被拒绝。或者传入字符串数字，也会被拒绝。所以严格。

现在，还有一个细节：在add_item中，我们只检查name是否存在（非空字符串）和stock_total是正整数。如果name是空字符串，条件not name会为True（空字符串为假），所以返回400。所以name必须非空。要求如此。

现在，所有应该工作。

但，有一个问题：在clean_expired中，我们使用conn.execute()，但conn.execute('UPDATE ...')会立即开始一个事务。然后我们可能多次UPDATE，然后UPDATE状态，然后commit。但是，我们每次在循环中UPDATE items时，如果其中一个发生错误（如外键约束），会中断循环，无法继续。外层会捕获异常并回滚整个事务。但是，如果错误后，我们可能已经执行了部分UPDATE，但回滚会撤销，所以没问题。但要注意：在循环内，我们直接调用conn.execute，如果出错会跳出循环，不执行后续，然后外层回滚。正确。

但是，还有一点：在clean_expired中，我们可能查询到多个过期预约，然后开始逐条释放库存。如果在释放过程中，有预约同时被其他操作（在其他线程）处理？但我们在锁内，唯一线程，所以无竞争。所以没问题。

但是，有一个时间窗口：在clean_expired中释放库存后，我们还没有将预约状态改为expired。这可能在非常短的时间内，但锁只有当前线程，所以其他线程不会看到不一致。

现在，确认操作：确认操作检查status为pending，然后更新为confirmed。如果预约在clean_expired中被改为expired，则确认操作会看到status不是pending，返回400。所以clean_expired先执行，符合要求。

现在，关于TTL的精度：使用time.time()，秒为单位。在清理时，比较expires_at <= now。如果预约刚好在now时过期，应该被清理。所以符合。

现在，在路由中，我们使用re.fullmatch，需要确保模式完全匹配。例如，路径'/reservations/123/confirm/'（尾部斜杠）将不会匹配，返回404。可以接受。

现在，检查是否符合所有要求。特别是：每次请求前清理过期。每个请求的入口handle_request都会先调用clean_expired()，所以是的。

现在，关于错误响应：例如GET /nonexist返回404，包含error字段。正确。

现在，还有一些边界：如数据库文件无法创建，则启动时init_db会出错，程序退出。所以OK。

现在，关于锁：Handler.handle_request中我们使用with db_lock:，但注意：在init_db中也使用db_lock，但如果在服务器启动后，init_db已完成，所以不会冲突。

现在，考虑是否需要在clean_expired中防止重复释放库存？由于我们只选择status='pending'的预约，如果过期，我们改为expired。所以在后续清理中不会再处理。不会重复。

现在，确认和取消后，状态不再是pending，所以也不会被清理。

现在，关于线程模式：由于使用ThreadingMixIn，每个请求在独立线程中处理。但锁的存在确保数据库串行访问。

现在，测试简单流程：

1. 启动：python server.py
2. 创建商品：curl -X POST http://127.0.0.1:8080/items -H "Content-Type: application/json" -d '{"name":"apple","stock_total":10}'
   返回201，id=1。
3. 列出：curl http://127.0.0.1:8080/items -> [{"id":1,...}]
4. 创建预约：curl -X POST http://127.0.0.1:8080/reservations -H "Content-Type: application/json" -d '{"item_id":1,"quantity":2,"ttl_seconds":60}'
   返回201, id=1, status=pending
5. 确认：curl -X POST http://127.0.0.1:8080/reservations/1/confirm -> 200
6. 取消：curl -X POST http://127.0.0.1:8080/reservations/1/cancel -> 400
7. 再建一个，过期：ttl_seconds=1，等2秒，然后GET /items，可用库存应该恢复？创建预约时减2，过期释放，所以可用恢复。测试：...
8. 测试并发：可能用工具，但这里不测。

现在，注意：关于时区：时间戳基于服务器时间，合理。

现在，所有代码完成。

但是，还需要注意，在handle_request中，我们使用with db_lock:，但如果body是None，并且方法需要body，我们在方法内会返回400。但是，我们仍然在锁内执行，这可能会导致不必要的阻塞。因为body解析在锁外，所以锁内只是处理，时间短。

现在，考虑如果一个请求POST /items，在锁内执行add_item，包括检查和INSERT。很快。

现在，关于锁的粒度：我们可以在方法内只在需要数据库操作时获取锁，但为了简单，我们整个处理都加锁。好。

现在，最后检查代码中可能的问题：

- 在handle_request，我们调用clean_expired后，如果路由是confirm或cancel，我们返回的结果来自方法，方法内可能执行了0行修改。但之后我们使用conn.commit()？在confirm方法中，我们在UPDATE后提交。但如果UPDATE失败异常抛给外层，外层会rollback。如果成功，提交后返回正常。所以没问题。

- 但是，如果clean_expired执行后，没有过期，事务状态如何？clean_expired没有执行任何INSERT/UPDATE，所以没有事务开始。所以后续方法中执行第一个modify语句时，自动开始事务。

- 要确保在add_item中，我们INSERT后提交，然后返回。但如果在INSERT后、commit前发生异常（如磁盘满），外层捕获，回滚未提交事务。

- 在create_reservation中，我们UPDATE和INSERT后commit，如果没有异常，提交。

- 在confirm和cancel中类似。

现在，没有看到明显问题。

现在，关于check约束，我们使用CHECK(status IN (...))，在插入或更新时，如果状态值不是允许的，会引发异常，由外层捕获。所以安全。

现在，考虑如果客户端发送的JSON包含多余的字段，我们忽略。

现在，返回的错误信息使用字符串，但可能包含敏感信息，但这里可以接受。

现在，代码符合要求，但有一个潜在问题：在do_GET和do_POST中，我们调用self.handle_request()，但handle_request中会调用clean_expired。但do_GET中我们传入body=None，但是在handle_request中，我们使用body参数。对于do_GET，body参数没有使用。

现在，我们定义了BaseHTTPRequestHandler的子类，没有重写log_message，所以会在控制台输出日志。

现在，最终代码。

但是，检查长度：大约170行左右，小于1000。

现在，输出最终代码。

但注意：在clean_expired中，我们执行了conn.commit()。但在外层，如果在clean_expired commit后，后续方法没有异常，但后续方法又commit了。所以没问题。

现在，还有一个细节：我们在init_db中创建表时，如果表已存在，不会报错。使用IF NOT EXISTS。

现在，关于数据库存储路径：是相对路径，在启动目录下。

现在，关于线程安全：我们conn是以全局方式使用，但我们在clean_expired和各个方法中直接使用conn.execute。尽管我们使用了锁，但需要注意：sqlite3模块在execute时会检查connection对象的threading safety。由于我们设置了check_same_thread=False，所以允许跨线程使用。但是，sqlite3的默认模式是check_same_thread=True，所以我们设置False是必要的。我们在连接创建时设置了check_same_thread=False。所以跨线程使用没问题。

我们同时使用PRAGMA journal_mode=WAL，有助于读并发，但我们的锁强制写串行，所以仍安全。

现在，潜在错误：在clean_expired的循环中，我们用了多个conn.execute(UPDATE items ...)，这些修改在同一个事务内，如果有错误，回滚整个事务。但如果在循环中，某个UPDATE造成数据库错误（如外键，但items表没有外键指向reservations，所以不会），所以可能不会。但如果stock_available更新后出现null? 不会。所以安全。

现在，注意：如果clean_expired执行时，rows可能很大，循环耗时，但因为我们锁住了，其他请求等待，但这是可接受的。

现在，所有OK。

我们可能还需要一个处理选项：对于GET /items，我们是否需要返回stock_total和stock_available？题目要求：列出商品和可用库存。所以返回stock_available足够，但返回stock_total也可以。我们全返回。

现在，一切无问题。

现在，我们输出代码。

但是，要考虑兼容Python 3.5？如果你使用f-string，则3.5不支持。但我们现在默认使用3.6+，没问题。如果想兼容，可以将f-string改为format。我保留f-string。

现在，最后输出完整代码。

注意：代码需要是纯python代码，不要额外解释。所以直接输出代码。
````

## Assistant

````markdown
```python
#!/usr/bin/env python3
import json
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import re

# Database file
DB_FILE = 'inventory.db'

# Global database connection and lock
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
conn.execute('PRAGMA journal_mode=WAL')  # optional, for better concurrency
db_lock = threading.Lock()

def init_db():
    """Initialize database tables if not exist."""
    with db_lock:
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','confirmed','cancelled','expired')),
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY(item_id) REFERENCES items(id)
            );
        ''')
        conn.commit()

def clean_expired():
    """Cancel expired pending reservations and release stock."""
    now = time.time()
    rows = conn.execute('''
        SELECT id, item_id, quantity FROM reservations WHERE status = ? AND expires_at <= ?
    ''', ('pending', now)).fetchall()
    if rows:
        # Release stock for each expired reservation
        for rid, iid, qty in rows:
            conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (qty, iid))
        # Mark as expired
        ids = tuple(r[0] for r in rows)
        placeholders = ','.join(['?'] * len(ids))
        conn.execute(
            'UPDATE reservations SET status = ? WHERE id IN ({})'.format(placeholders),
            ('expired',) + ids
        )
        conn.commit()

class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for inventory reservation service."""

    def do_GET(self):
        status, data = self.handle_request(body=None)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else b''
        body_json = None
        if body:
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                body_json = None
        status, data = self.handle_request(body=body_json)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def handle_request(self, body):
        """Process request under lock."""
        method = self.command
        path = self.path
        with db_lock:
            try:
                clean_expired()

                if method == 'GET' and path == '/items':
                    return self.get_items()

                if method == 'POST':
                    if path == '/items':
                        return self.add_item(body)
                    elif path == '/reservations':
                        return self.create_reservation(body)
                    else:
                        # Check for confirm/cancel
                        m = re.fullmatch(r'/reservations/(\d+)/(confirm|cancel)', path)
                        if m:
                            res_id = int(m.group(1))
                            action = m.group(2)
                            if action == 'confirm':
                                return self.confirm_reservation(res_id)
                            else:
                                return self.cancel_reservation(res_id)

                return (404, {"error": "Not found"})
            except Exception as e:
                conn.rollback()
                return (500, {"error": f"Internal server error: {str(e)}"})

    def get_items(self):
        cur = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
        items = []
        for row in cur.fetchall():
            items.append({
                "id": row[0],
                "name": row[1],
                "stock_total": row[2],
                "stock_available": row[3]
            })
        return (200, items)

    def add_item(self, body):
        if body is None:
            return (400, {"error": "Invalid JSON"})
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            return (400, {"error": "Invalid parameters: name (string) and stock_total (positive int) required"})
        cur = conn.execute(
            'INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
            (name, stock_total, stock_total)
        )
        conn.commit()
        new_id = cur.lastrowid
        return (201, {
            "id": new_id,
            "name": name,
            "stock_total": stock_total,
            "stock_available": stock_total
        })

    def create_reservation(self, body):
        if body is None:
            return (400, {"error": "Invalid JSON"})
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if not all([isinstance(item_id, int), isinstance(quantity, int), isinstance(ttl_seconds, int)]):
            return (400, {"error": "Invalid parameters: item_id, quantity, ttl_seconds must be integers"})
        if quantity <= 0 or ttl_seconds <= 0:
            return (400, {"error": "Quantity and ttl_seconds must be positive"})

        # Check item existence and available stock
        cur = conn.execute('SELECT id, stock_available FROM items WHERE id = ?', (item_id,))
        item = cur.fetchone()
        if not item:
            return (404, {"error": "Item not found"})
        available = item[1]
        if available < quantity:
            return (409, {"error": "Insufficient stock"})

        # Reserve stock
        conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id = ?', (quantity, item_id))
        now = time.time()
        expires = now + ttl_seconds
        cur2 = conn.execute(
            'INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, ?, ?)',
            (item_id, quantity, 'pending', expires, now)
        )
        res_id = cur2.lastrowid
        conn.commit()
        return (201, {
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires,
            "created_at": now
        })

    def confirm_reservation(self, res_id):
        cur = conn.execute('SELECT id, status FROM reservations WHERE id = ?', (res_id,))
        row = cur.fetchone()
        if not row:
            return (404, {"error": "Reservation not found"})
        if row[1] != 'pending':
            return (400, {"error": f"Reservation status must be pending to confirm, current: {row[1]}"})
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('confirmed', res_id))
        conn.commit()
        return (200, {"id": res_id, "status": "confirmed"})

    def cancel_reservation(self, res_id):
        cur = conn.execute('SELECT id, status, item_id, quantity FROM reservations WHERE id = ?', (res_id,))
        row = cur.fetchone()
        if not row:
            return (404, {"error": "Reservation not found"})
        if row[1] != 'pending':
            return (400, {"error": f"Reservation status must be pending to cancel, current: {row[1]}"})
        item_id = row[2]
        quantity = row[3]
        # Release stock
        conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (quantity, item_id))
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('cancelled', res_id))
        conn.commit()
        return (200, {"id": res_id, "status": "cancelled"})

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""
    daemon_threads = True

if __name__ == "__main__":
    init_db()
    server = ThreadedHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server starting on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```
````
