# Generation Transcript

- Case: `zh_code_be_001`
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
- Elapsed seconds: 98.401649
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 10069, "completion_tokens": 9706, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 9706
- Total tokens: 10069

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
我们被要求写一个单文件 HTTP API 服务，使用 Python 3 标准库，不能使用第三方库。需要实现库存预约服务。使用 sqlite3 持久化。需要处理并发，使用线程锁。需要实现6个API端点，包括过期清理。

我们要基于 http.server 模块？或者可以使用 socketserver? 或者低级别的 socket? 但更简单的是使用 http.server 中的 BaseHTTPRequestHandler 和 HTTPServer。我们需要自己路由和解析。

注意：处理并发时，BaseHTTPRequestHandler 默认是单线程的，即每个请求都会阻塞。为了实现并发，我们可以使用 ThreadingHTTPServer（Python 3.7+）或者使用 socketserver.ThreadingMixIn。标准库中有 http.server.ThreadingHTTPServer。或者自己继承。确保线程安全，使用 threading.Lock 保护数据库操作。

设计思路：

- 数据库初始化：创建两个表 items 和 reservations。
- 全局锁：db_lock = threading.Lock()，所有数据库操作在 with 锁下进行。
- 每个请求处理前先清理过期 pending 预约（在锁内进行）。
- 使用 BaseHTTPRequestHandler 子类，实现 do_GET 和 do_POST。
- 路由解析：解析 path 和 method，分发到不同函数。
- JSON 解析：使用 json.loads 读取 body。
- 返回 JSON：使用 json.dumps。

注意：需要处理 /reservations/{id}/confirm 等路径，可以用正则或手动分割。

简单起见，使用 path 分割。

确保返回正确状态码：200, 201, 400, 404, 409等。

需要考虑到 requests body 可能为空，要处理。

另外，需要确保创建商品时，stock_available 初始等于 stock_total。

预约创建：检查库存是否足够，插入 reservation 记录，并减掉可用库存。status 为 'pending'，expires_at 为当前时间 + ttl_seconds。注意 ttl_seconds 是秒数。

确认预约：将 status 改为 'confirmed'，但不释放库存（因为已经扣除了，确认只是标记状态，库存保持不变）。确保只能确认 pending 状态。

取消预约：将 status 改为 'cancelled'，并且释放库存，即增加 stock_available。注意只能取消 pending 状态。

清理过期 pending：查询所有 expired_at < datetime.now() 且 status='pending' 的预约，将它们状态改为 'expired'，并释放库存。每次请求前执行（在锁内）。

注意：并发下可能多个线程同时执行清理，但锁会保护。

需要额外考虑：在创建预约时，需要检查库存，然后插入，然后更新库存。这些操作必须在事务中原子完成。由于 sqlite3 默认是自动提交，我们可以使用 BEGIN/COMMIT 或使用 connection 的上下文管理器？实际上，Python 的 sqlite3 模块默认每个语句自动提交，但我们可以使用 conn.execute("BEGIN") 然后手动 commit 或 rollback。或者使用 conn 的 context manager 来管理事务：with conn: ... 在 with 块中执行多个语句，会自动在开始时开始事务，结束时提交。如果异常则回滚。推荐使用 with conn: 包裹所有写操作，并且也包裹读操作以便一致性？但是读操作不需要事务，但为了简单也可以。

注意：更新库存和插入预约必须在同一个事务中，因为如果插入成功但更新失败（或反之），则数据不一致。使用 with conn: 自动处理。

另外，查询时也需要确保读到最新的，但读操作在锁内，所以没问题。

关于时间：expires_at 使用 UTC 时间，避免时区问题。使用 datetime.datetime.utcnow()。

API 具体：

GET /items -> 返回所有商品列表，包含 id, name, stock_total, stock_available。

POST /items -> JSON body 包含 name 和 stock_total。验证 name 非空，stock_total 为整数>0。返回新创建的商品，状态201。

POST /reservations -> JSON body 包含 item_id, quantity, ttl_seconds。检查 item_id 存在，quantity >0，库存足够。返回创建的预约，状态201。注意要返回预约记录，包括生成的 id 等。

POST /reservations/{id}/confirm -> 路径参数 id 为整数。检查预约存在且 pending，然后更新状态。返回成功消息或错误。

POST /reservations/{id}/cancel -> 类似。

错误处理：返回 JSON 格式 {"error": "描述"}，适当的状态码。

其他路径或方法返回 404。

注意：当请求不是 JSON 或解析失败时，返回 400 错误。

需要 import 的模块：http.server, json, sqlite3, threading, datetime, re, os 等。

代码结构：

- 定义 DB_NAME 常量。
- 定义函数 init_db() 创建表。
- 定义类 ReservationHandler(BaseHTTPRequestHandler):
    - 全局锁和数据库连接？但每次请求需要一个新的连接？因为 sqlite3 连接不是线程安全的，但我们可以使用锁保护，所以可以在每个请求内创建新连接，或者使用全局连接加锁。通常使用全局连接加锁更方便，但要注意 sqlite3 连接不能跨线程共享，但加上锁后可以在多线程中使用同一个连接（只要访问时持有锁）。实际上，Python 的 sqlite3 模块在单个连接上，如果多个线程同时访问，需要序列化。我们可以使用一个全局连接，并通过锁确保同一时刻只有一个线程使用它。或者每个线程创建自己的连接，但需要锁保护数据库文件访问？每个线程独立连接可能更安全，但需要锁来防止并发写冲突？因为 SQLite 文件级锁，多个写操作需要串行化。使用单个连接全局加锁更简单。注意：使用单个连接需要小心在请求结束后不关闭连接（重用）。我们可以创建一个全局连接，在 init_db 中创建，然后在 handler 中使用 with db_lock: 并在 with 内使用该连接。

更好的实践：每个请求创建一个新的连接，但同样需要数据库锁来保证写操作原子性？SQLite 内部有文件锁，但使用多个连接可能会导致数据库锁定冲突。为了简单，我选择全局连接+锁。

代码示例：

```python
import http.server
import json
import sqlite3
import threading
import datetime
import re
from urllib.parse import urlparse, parse_qs

DB_NAME = "inventory.db"
db_lock = threading.Lock()
conn = None

def init_db():
    global conn
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)  # 允许跨线程访问，但我们用锁保护
    conn.execute("PRAGMA journal_mode=WAL")  # 提高并发
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )""")
    conn.commit()

def clean_expired():
    # 必须在锁内调用
    now = datetime.datetime.utcnow().isoformat()
    # 查找过期 pending 预约
    cursor = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?", (now,))
    expired = cursor.fetchall()
    for res_id, item_id, quantity in expired:
        # 更新预约状态为 expired
        conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
        # 释放库存
        conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
    conn.commit()
    return len(expired)
```

注意：clean_expired 需要事务，用 with conn: 也可以。但为了复用 conn，我们直接 conn.execute 然后 commit。

现在处理 HTTP 请求：

我们需要解析 path，分割出路径段。

由于是重写 do_GET 和 do_POST。

对于 GET 只有 /items。

对于 POST 有 /items, /reservations, /reservations/{id}/confirm, /reservations/{id}/cancel。

解析 path: 使用 urllib.parse.urlparse(path).path 得到路径。然后按 '/' 分割，过滤空字符串。

例如路径 /reservations/123/confirm -> parts = ['reservations', '123', 'confirm']，检查 parts[0] 和 parts[2] 等。

我们将实现一个 dispatch 方法。

注意：请求体需要读取，可以通过 self.rfile.read(content_length) 获取。

还要设置响应头：self.send_response(code), self.send_header('Content-Type', 'application/json'), self.end_headers()。

然后写入 body。

处理异常：如果解析 JSON 失败，返回 400。

还要注意，创建商品时，stock_available 应为 stock_total。

新增库存减扣逻辑：创建预约时，检查可用库存 >= quantity，然后先更新库存减量，再插入预约。事务内。

确认预约：检查预约是否存在且 pending，然后更新 status。注意：确认后库存保持不变（已经扣除了）。所以不需要修改库存。

取消预约：检查预约存在且 pending，然后更新 status 为 cancelled，同时增加库存。

注意：对于取消和确认，需要确保预约属于某个商品，并且状态正确。

另外，对于 GET /items 返回的 stock_available 是实时可用库存（已扣除 pending 和 confirmed？注意：confirmed 也不释放库存，所以 stock_available 是减去 pending 和 confirmed 后的余额？实际上，我们的设计是预约时立即扣减库存（减少 stock_available），所以 stock_available 反映的是当前可预约的数量。confirmed 的预约已经扣除了，所以不再可预约；cancelled 或 expired 会加回。所以 stock_available 就是可用库存。

要小心：当清理过期时，我们已经释放了库存。

现在写代码。

需要注意，BaseHTTPRequestHandler 是同步的，如果使用 ThreadingHTTPServer，则可以多线程处理。标准库中有 http.server.ThreadingHTTPServer。我们将使用它。

启动代码：

```python
if __name__ == "__main__":
    init_db()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8080), ReservationHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.server_close()
```

注意：ThreadingHTTPServer 在 Python 3.7 添加。如果使用更早版本，可以使用 socketserver.ThreadingMixIn 和 HTTPServer 组合。但题目说 Python 3，假设是最新稳定版本。

现在考虑细节：

- POST /items 的 body 示例: {"name": "item1", "stock_total": 10}
- POST /reservations body: {"item_id": 1, "quantity": 2, "ttl_seconds": 3600}

需要验证 ttl_seconds 正整数。

- 对于路径参数 id，要转换为整数，如果转换失败返回 400。

- 确认或取消时，如果 id 不存在或状态不正确，返回适当的错误。

- 冲突：例如取消一个已确认的预约，返回错误。

- 注意：所有响应体应当是 JSON 格式，即使是错误也如此。

还要考虑性能：每个请求前都会清理过期，可能消耗一些时间，但可接受。

代码长度限制1000行，应该绰绰有余。

现在写出完整代码。

注意：需要处理 response 编码。body 使用 JSON 字符串，编码为 utf-8。

关于锁：使用全局锁，所有数据库操作都在 with db_lock: 中。包括 clean_expired。并且读操作也需要锁以保证一致性？因为可能其他线程在写。所以所有数据库访问都在锁内。

因此，在 do_GET 和 do_POST 中，先获取锁，然后 clean_expired，然后根据路径处理。

但是：在锁内进行网络 I/O 读请求体可能不太好，因为读取 body 可能耗时，但应该没问题，且 body 通常很小。或者可以先读取 body 再进入锁？但处理逻辑需要数据库，所以先获取锁再读取 body 也没问题。但读取 body 不需要锁，为了减少锁持有时间，可以先读取 body 再获取锁。不过代码简单性考虑，可以同步。

安全：锁是递归锁吗？不需要。

注意：sqlite3 连接是全局的，使用 check_same_thread=False 允许在多线程中使用，但我们用锁保护。

现在编写代码。

由于我们直接写代码，尽量简洁清晰。

用到的库：http.server, json, sqlite3, threading, datetime, urllib.parse, os, sys.

代码：

```python
#!/usr/bin/env python3
import http.server
import json
import sqlite3
import threading
import datetime
import urllib.parse
import os

DB_NAME = "inventory.db"
db_lock = threading.Lock()
conn = None

def init_db():
    global conn
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )""")
    conn.commit()

def clean_expired():
    now = datetime.datetime.utcnow().isoformat()
    # 查找过期pending预约
    cursor = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?", (now,))
    expired = cursor.fetchall()
    for res_id, item_id, quantity in expired:
        conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
        conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
    conn.commit()
    return len(expired)

class ReservationHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            with db_lock:
                clean_expired()
                cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in cursor.fetchall()]
                self._send_json(200, items)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        parts = [p for p in path.split('/') if p]

        # 解析路径
        if path == '/items':
            self._handle_post_item()
        elif path == '/reservations':
            self._handle_post_reservation()
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_confirm(res_id)
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_cancel(res_id)
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_post_item(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            self._send_json(400, {"error": "name and stock_total required, stock_total must be positive integer"})
            return
        with db_lock:
            clean_expired()
            conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
            conn.commit()
            cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items WHERE id = last_insert_rowid()")
            row = cursor.fetchone()
            self._send_json(201, {"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]})

    def _handle_post_reservation(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')
        if not all(isinstance(x, int) for x in [item_id, quantity, ttl_seconds]) or quantity <= 0 or ttl_seconds <= 0:
            self._send_json(400, {"error": "item_id, quantity, ttl_seconds must be positive integers"})
            return
        with db_lock:
            clean_expired()
            # 检查商品存在
            cursor = conn.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
            item = cursor.fetchone()
            if not item:
                self
````

## Assistant

````markdown
: _send_json(404, {"error": "Item not found"})
                return
            stock_available = item[0]
            if stock_available < quantity:
                self._send_json(409, {"error": "Insufficient stock"})
                return
            # 创建预约
            now = datetime.datetime.utcnow()
            expires_at = now + datetime.timedelta(seconds=ttl_seconds)
            created_at = now.isoformat()
            expires_at_str = expires_at.isoformat()
            # 事务开始
            conn.execute("BEGIN")
            try:
                # 减库存
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
                # 插入预约
                conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                             (item_id, quantity, expires_at_str, created_at))
                conn.commit()
                cursor = conn.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
                self._send_json(201, {
                    "id": row[0],
                    "item_id": row[1],
                    "quantity": row[2],
                    "status": row[3],
                    "expires_at": row[4],
                    "created_at": row[5]
                })
            except Exception as e:
                conn.rollback()
                self._send_json(500, {"error": "Internal server error"})

    def _handle_confirm(self, res_id):
        with db_lock:
            clean_expired()
            # 检查预约存在且pending
            cursor = conn.execute("SELECT id, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[1] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[1]}"})
                return
            conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            conn.commit()
            self._send_json(200, {"message": "Reservation confirmed"})

    def _handle_cancel(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[3] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[3]}, cannot cancel"})
                return
            item_id = row[1]
            quantity = row[2]
            conn.execute("BEGIN")
            try:
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
                conn.commit()
                self._send_json(200, {"message": "Reservation cancelled"})
            except Exception as e:
                conn.rollback()
                self._send_json(500, {"error": "Internal server error"})

if __name__ == "__main__":
    init_db()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8080), ReservationHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```

注意：上面代码中 _handle_post_reservation 中有一处 `self response: _send_json` 应该是笔误。应修正为 `self._send_json(...)`。还有在 try-except 中捕获所有异常，但最好指定具体的异常。还有在 begin/commit/rollback 时可能没有正确处理。但基本逻辑正确。

我将在最终代码中修复这些小错误。

另外，在 `_handle_post_reservation` 中，使用了 `conn.execute("BEGIN")`，但 Python 的 sqlite3 连接默认自动提交，使用 with conn: 更安全。但是 with conn: 会自动开始事务并提交或回滚，而且我们还需要手动控制。我们可以使用 with conn: 上下文来包裹需要原子性的块。如：

```python
with conn:
    # 执行所有语句
    conn.execute(...)
    ...
# 退出 with 自动 commit 如果无异常，否则 rollback
```

这更符合 Python 风格。所以我会改用 with conn: 而不是手动 begin/commit/rollback。需要确保 conn 是全局的，且 with 块内部不会因为异常而影响其他线程。由于有锁，没问题。

修改代码，使用 `with conn:` 包裹。

同时注意：读操作不需要事务，但也可以放在 with 中，但为了简单，可以放在锁内直接执行。

此外，clean_expired 内部也应该是 with conn: 包裹以确保原子性？目前 clean_expired 里面多个 update 然后 commit，应该使用事务。用 with conn: 包裹更安全。

修改 clean_expired:

```python
def clean_expired():
    now = datetime.datetime.utcnow().isoformat()
    with conn:
        cursor = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?", (now,))
        expired = cursor.fetchall()
        for res_id, item_id, quantity in expired:
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
```

同样，在创建预约时使用 `with conn:`。

但是注意：在 with conn: 内部，如果 commit 失败或 rollback，外部不会捕获。但我们可以用 try-except 包裹。

同时注意：在 with conn: 中，我们不能在内部再调用 with conn: 多次，因为锁已经持有，且 conn 是同一个，嵌套 with 可能没问题，但为了清晰，我们在锁内只有一个 with conn: 即可。

现在代码需要调整。

完整修正后的代码：

```python
#!/usr/bin/env python3
import http.server
import json
import sqlite3
import threading
import datetime
import urllib.parse
import os

DB_NAME = "inventory.db"
db_lock = threading.Lock()
conn = None

def init_db():
    global conn
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )""")
    conn.commit()

def clean_expired():
    now = datetime.datetime.utcnow().isoformat()
    with conn:
        cursor = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
            (now,)
        )
        expired = cursor.fetchall()
        for res_id, item_id, quantity in expired:
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))

class ReservationHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            with db_lock:
                clean_expired()
                cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in cursor.fetchall()]
                self._send_json(200, items)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        parts = [p for p in path.split('/') if p]

        if path == '/items':
            self._handle_post_item()
        elif path == '/reservations':
            self._handle_post_reservation()
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_confirm(res_id)
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_cancel(res_id)
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_post_item(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            self._send_json(400, {"error": "name and stock_total required, stock_total must be positive integer"})
            return
        with db_lock:
            clean_expired()
            with conn:
                conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
                cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
            self._send_json(201, {"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]})

    def _handle_post_reservation(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')
        if not all(isinstance(x, int) for x in [item_id, quantity, ttl_seconds]) or quantity <= 0 or ttl_seconds <= 0:
            self._send_json(400, {"error": "item_id, quantity, ttl_seconds must be positive integers"})
            return
        with db_lock:
            clean_expired()
            # 检查商品存在和库存
            cursor = conn.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
            item = cursor.fetchone()
            if not item:
                self._send_json(404, {"error": "Item not found"})
                return
            stock_available = item[0]
            if stock_available < quantity:
                self._send_json(409, {"error": "Insufficient stock"})
                return
            # 创建预约（事务）
            now = datetime.datetime.utcnow()
            expires_at = now + datetime.timedelta(seconds=ttl_seconds)
            created_at = now.isoformat()
            expires_at_str = expires_at.isoformat()
            with conn:
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
                conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at_str, created_at)
                )
                cursor = conn.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
            self._send_json(201, {
                "id": row[0],
                "item_id": row[1],
                "quantity": row[2],
                "status": row[3],
                "expires_at": row[4],
                "created_at": row[5]
            })

    def _handle_confirm(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[1] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[1]}"})
                return
            with conn:
                conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            self._send_json(200, {"message": "Reservation confirmed"})

    def _handle_cancel(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[3] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[3]}, cannot cancel"})
                return
            item_id = row[1]
            quantity = row[2]
            with conn:
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
            self._send_json(200, {"message": "Reservation cancelled"})

if __name__ == "__main__":
    init_db()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8080), ReservationHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```

注意：在 `_handle_post_reservation` 中，先检查库存，然后再进入事务。这里有一个 竞态条件：在两个线程同时检查库存后，一个执行更新，另一个可能基于旧值检查。但因为我们使用了锁，同一时刻只有一个线程在操作，所以不会有竞态。锁确保整个操作原子性。没问题。

还有一点：在 `_handle_confirm` 和 `_handle_cancel` 中，clean_expired 先执行，可能已经将 pending 变为 expired，但后续查询可能过期了。这样用户会看到 NotFound 或 Already 状态。这是设计预期的。

最后，检查所有可能的异常。比如在 `_send_json` 中，可能由于连接断开而异常，但那是客户端的问题，忽略。

确保代码不超过1000行，当前代码远远少于。

输出：只需输出完整 Python 代码。</think>```python
#!/usr/bin/env python3
import http.server
import json
import sqlite3
import threading
import datetime
import urllib.parse
import os

DB_NAME = "inventory.db"
db_lock = threading.Lock()
conn = None

def init_db():
    global conn
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )""")
    conn.commit()

def clean_expired():
    now = datetime.datetime.utcnow().isoformat()
    with conn:
        cursor = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
            (now,)
        )
        expired = cursor.fetchall()
        for res_id, item_id, quantity in expired:
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))

class ReservationHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            with db_lock:
                clean_expired()
                cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in cursor.fetchall()]
                self._send_json(200, items)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        parts = [p for p in path.split('/') if p]

        if path == '/items':
            self._handle_post_item()
        elif path == '/reservations':
            self._handle_post_reservation()
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_confirm(res_id)
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_cancel(res_id)
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_post_item(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            self._send_json(400, {"error": "name and stock_total required, stock_total must be positive integer"})
            return
        with db_lock:
            clean_expired()
            with conn:
                conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
                cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
            self._send_json(201, {"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]})

    def _handle_post_reservation(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')
        if not all(isinstance(x, int) for x in [item_id, quantity, ttl_seconds]) or quantity <= 0 or ttl_seconds <= 0:
            self._send_json(400, {"error": "item_id, quantity, ttl_seconds must be positive integers"})
            return
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
            item = cursor.fetchone()
            if not item:
                self._send_json(404, {"error": "Item not found"})
                return
            stock_available = item[0]
            if stock_available < quantity:
                self._send_json(409, {"error": "Insufficient stock"})
                return
            now = datetime.datetime.utcnow()
            expires_at = now + datetime.timedelta(seconds=ttl_seconds)
            created_at = now.isoformat()
            expires_at_str = expires_at.isoformat()
            with conn:
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
                conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at_str, created_at)
                )
                cursor = conn.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
            self._send_json(201, {
                "id": row[0],
                "item_id": row[1],
                "quantity": row[2],
                "status": row[3],
                "expires_at": row[4],
                "created_at": row[5]
            })

    def _handle_confirm(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[1] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[1]}"})
                return
            with conn:
                conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            self._send_json(200, {"message": "Reservation confirmed"})

    def _handle_cancel(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[3] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[3]}, cannot cancel"})
                return
            item_id = row[1]
            quantity = row[2]
            with conn:
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
            self._send_json(200, {"message": "Reservation cancelled"})

if __name__ == "__main__":
    init_db()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8080), ReservationHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```
````
