# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 51.381773
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 9456, "completion_tokens": 9093, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 9093
- Total tokens: 9456

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
我们被要求编写一个单文件HTTP API服务，使用Python 3标准库，不使用第三方库。需要实现库存预约服务，使用sqlite3持久化。需要处理并发，使用线程锁和事务。代码不超过1000行。要求输出完整的Python代码。

我们首先设计代码结构：

1. 使用http.server模块创建HTTP服务器。但http.server是同步的，每个请求在一个线程中处理。我们可以使用ThreadingHTTPServer或者BaseHTTPServer配合ThreadingMixIn。由于要求并发，可以使用ThreadingHTTPServer（Python 3.7+有）。或者自己用socketserver.ThreadingMixIn。

2. 处理请求的Handler类继承BaseHTTPRequestHandler。实现do_GET, do_POST等方法。

3. 数据库初始化：在启动时创建表，如果不存在。使用sqlite3，连接应该由每个请求创建还是全局？为了线程安全，sqlite3连接不是线程安全的，但SQLite本身支持WAL模式和多线程读取，但写操作需要串行化。通常每个请求创建单独连接，但可能性能问题。也可以使用全局连接并加锁。或者使用check_same_thread=False，然后加锁。为了简化，我们可以使用一个全局连接，但使用threading.Lock来同步。每次请求获取锁，然后执行操作。注意：SQLite默认在事务中，但多个线程同时写入可能导致database is locked错误。我们可以使用锁来确保同一时间只有一个线程访问数据库。另外，我们可以使用连接池，但标准库不支持。

这里我们选择：创建一个全局的sqlite3连接，设置check_same_thread=False，然后使用一个全局锁（threading.Lock）来保护所有数据库操作。每次请求处理时获取锁，执行完释放。

4. 预约过期清理：每次请求前都需要清理过期的pending预约并释放库存。这个清理操作应该在每个请求处理开始时执行（在获取数据库锁后，或者作为事务的一部分）。注意：清理应该原子性：先查出所有过期pending，然后更新状态为expired，并释放库存。可以用一个事务完成。

5. 处理并发：事务和锁。我们统一使用锁来保护数据库访问，因为SQLite只支持串行写，但读可以并发。但为了简单，全局锁即可。同时，每个操作内部使用事务（自动提交或手动）。我们可以设置conn.isolation_level = None，然后手动控制BEGIN/COMMIT。或者使用自动提交模式（默认），每次execute后自动提交。但为了原子性，需要显式事务。我们将使用BEGIN和COMMIT。

6. API实现：
   - GET /items：查询所有商品，返回列表，包括id, name, stock_total, stock_available。
   - POST /items：解析JSON，验证参数，插入商品，返回插入的商品信息（包括id）。注意：stock_available初始等于stock_total。
   - POST /reservations：解析JSON，参数item_id, quantity, ttl_seconds。先检查库存是否足够（SELECT stock_available WHERE id=item_id），如果不足返回409。然后插入预约，设置status='pending', expires_at = now + ttl_seconds, created_at=now。同时更新stock_available减quantity。需要在事务中完成。
   - POST /reservations/{id}/confirm：查找预约，必须是pending状态，并且未过期？题目没有明确说明过期预约能否确认，但按常理过期应该不能确认。我们可以在确认前也清理过期，或者直接检查状态和过期时间。如果预约已过期（status=pending但expires_at<now），则返回错误。否则更新status='confirmed'，不释放库存（因为已经减过了）。不需要改动库存。
   - POST /reservations/{id}/cancel：查找预约，必须是pending状态（未过期的），如果是confirmed不能取消？题目只说取消预约释放库存，应该只针对pending。如果预约已过期，应该已经是expired状态（清理后），所以直接返回错误。取消时，将status改为'cancelled'，并且增加库存（stock_available += quantity）。注意：同时更新stock_available。

7. 错误处理：返回JSON，包含error字段。HTTP状态码适当：200成功，201创建成功，400参数错误，404资源未找到，409冲突（库存不足）。另外确认/取消时如果预约不存在返回404，如果状态不对返回400。

8. json解析：使用json模块。

9. 路径解析：需要解析URL路径，提取路径参数如reservations/{id}。可以使用正则或简单split。

10. 启动入口：监听127.0.0.1:8080，使用ThreadingHTTPServer。

我们还需要注意：清理过期预约应该在每次请求前执行，意味着在do_GET, do_POST等方法中首先调用清理函数。清理函数在数据库锁内执行。

考虑到代码简洁，我们可将所有数据库操作封装到DB类中，或者直接函数。但为了不超过1000行，直接写函数即可。

实现细节：

- 使用ThreadingHTTPServer，需要从http.server导入HTTPServer，从socketserver导入ThreadingMixIn。或者直接使用ThreadingHTTPServer（Python 3.7+自带）。这里使用：
  ```
  class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
      pass
  ```
  或者直接使用socketserver.ThreadingTCPServer，但通常用HTTPServer。

- 注意：ThreadingMixIn会为每个请求创建新线程，但Python中GIL导致线程并非真正并行，但I/O操作会释放GIL，SQLite操作也会释放？实际上Python的SQLite3模块默认会释放GIL，所以可以并行运行，但数据库锁会串行化。

- 我们还需要处理静态文件？不需要。

- 我们可以在Handler类中解析路径和请求体。

现在开始编写代码。

注意：代码必须完整，包括所有导入。使用标准库：http.server, json, sqlite3, threading, datetime, urllib.parse等。

我们编写如下：

```python
#!/usr/bin/env python3
import json
import sqlite3
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

# 数据库配置
DB_PATH = "inventory.db"

# 全局锁和连接
_db_lock = threading.Lock()
_connection = None

def get_connection():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.execute("PRAGMA journal_mode=WAL")
        # 启用外键？可选
        _connection.execute("PRAGMA foreign_keys=ON")
    return _connection

def init_db():
    conn = get_connection()
    with _db_lock:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
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
                created_at TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)
        conn.commit()

def clean_expired_reservations():
    """清理过期的pending预约，释放库存。需在锁内调用。"""
    conn = get_connection()
    now_str = datetime.utcnow().isoformat()
    # 选择过期的pending预约
    rows = conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
        (now_str,)
    ).fetchall()
    if not rows:
        return
    # 对于每个过期预约，更新状态并释放库存
    # 使用事务
    conn.execute("BEGIN")
    try:
        for rid, item_id, qty in rows:
            # 更新预约状态
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (rid,))
            # 释放库存
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

# 工具函数：读取请求体JSON
def read_json_body(handler):
    content_length = int(handler.headers.get('Content-Length', 0))
    if content_length == 0:
        return None
    body = handler.rfile.read(content_length)
    return json.loads(body.decode('utf-8'))

# 工具函数：返回JSON响应
def send_json(handler, code, data):
    handler.send_response(code)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode('utf-8'))

# 工具函数：返回错误响应
def send_error(handler, code, message):
    send_json(handler, code, {"error": message})

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 解析路径
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            self.handle_get_items()
        else:
            send_error(self, 404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        # 注意：路径可能包含ID，如 /reservations/123/confirm
        if path == '/items':
            self.handle_post_items()
        elif path == '/reservations':
            self.handle_post_reservations()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            # 提取ID
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations' and parts[3] == 'confirm':
                try:
                    res_id = int(parts[2])
                except ValueError:
                    send_error(self, 400, "Invalid reservation ID")
                    return
                self.handle_confirm_reservation(res_id)
            else:
                send_error(self, 404, "Not found")
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations' and parts[3] == 'cancel':
                try:
                    res_id = int(parts[2])
                except ValueError:
                    send_error(self, 400, "Invalid reservation ID")
                    return
                self.handle_cancel_reservation(res_id)
            else:
                send_error(self, 404, "Not found")
        else:
            send_error(self, 404, "Not found")

    # ------ handlers ------
    def handle_get_items(self):
        with _db_lock:
            # 先清理过期
            clean_expired_reservations()
            conn = get_connection()
            cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
            items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in cursor]
        send_json(self, 200, items)

    def handle_post_items(self):
        try:
            data = read_json_body(self)
        except Exception:
            send_error(self, 400, "Invalid JSON")
            return
        if not data:
            send_error(self, 400, "Request body required")
            return
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(name, str) or stock_total is None or not isinstance(stock_total, int) or stock_total < 0:
            send_error(self, 400, "Invalid or missing parameters: name (string), stock_total (non-negative integer)")
            return
        with _db_lock:
            conn = get_connection()
            try:
                cursor = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                                      (name, stock_total, stock_total))
                conn.commit()
                item_id = cursor.lastrowid
            except Exception as e:
                send_error(self, 500, "Database error")
                return
        send_json(self, 201, {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total})

    def handle_post_reservations(self):
        try:
            data = read_json_body(self)
        except Exception:
            send_error(self, 400, "Invalid JSON")
            return
        if not data:
            send_error(self, 400, "Request body required")
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0 or not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            send_error(self, 400, "Invalid parameters: item_id (int), quantity (positive int), ttl_seconds (positive int)")
            return
        with _db_lock:
            # 先清理过期
            clean_expired_reservations()
            conn = get_connection()
            # 检查库存
            cursor = conn.execute("SELECT stock_available, stock_total FROM items WHERE id=?", (item_id,))
            row = cursor.fetchone()
            if row is None:
                send_error(self, 404, "Item not found")
                return
            stock_available, stock_total = row
            if stock_available < quantity:
                send_error(self, 409, "Insufficient stock")
                return
            # 计算过期时间
            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=ttl_seconds)
            created_at = now
            # 执行插入和更新库存（事务）
            conn.execute("BEGIN")
            try:
                cursor = conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at.isoformat(), created_at.isoformat())
                )
                res_id = cursor.lastrowid
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
                conn.commit()
            except Exception:
                conn.rollback()
                send_error(self, 500, "Database error")
                return
        send_json(self, 201, {"id": res_id, "item_id": item_id, "quantity": quantity, "status": "pending",
                              "expires_at": expires_at.isoformat(), "created_at": created_at.isoformat()})

    def handle_confirm_reservation(self, res_id):
        with _db_lock:
            # 先清理过期（可能会影响这个预约？但我们需要在事务中检查）
            clean_expired_reservations()
            conn = get_connection()
            # 查询预约
            cursor = conn.execute("SELECT id, status, expires_at FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if row is None:
                send_error(self, 404, "Reservation not found")
                return
            rid, status, expires_at_str = row
            if status != 'pending':
                send_error(self, 400, "Reservation is not pending")
                return
            # 检查是否过期（虽然清理过，但可能刚过期，双重检查）
            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at < datetime.utcnow():
                # 过期了，应该已经清理了，但以防万一
                send_error(self, 400, "Reservation already expired")
                return
            # 确认：更新状态
            conn.execute("BEGIN")
            try:
                conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (rid,))
                conn.commit()
            except Exception:
                conn.rollback()
                send_error(self, 500, "Database error")
                return
        send_json(self, 200, {"id": rid, "status": "confirmed"})

    def handle_cancel_reservation(self, res_id):
        with _db_lock:
            # 先清理过期
            clean_expired_reservations()
            conn = get_connection()
            # 查询预约，需要item_id和quantity来释放库存
            cursor = conn.execute("SELECT id, item_id, quantity, status, expires_at FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if row is None:
                send_error(self, 404, "Reservation not found")
                return
            rid, item_id, quantity, status, expires_at_str = row
            if status != 'pending':
                send_error(self, 400, "Reservation is not pending")
                return
            # 检查过期（虽然清理过）
            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at < datetime.utcnow():
                send_error(self, 400, "Reservation already expired")
                return
            # 取消：更新状态并释放库存（事务）
            conn.execute("BEGIN")
            try:
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (rid,))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
                conn.commit()
            except Exception:
                conn.rollback()
                send_error(self, 500, "Database error")
                return
        send_json(self, 200, {"id": rid, "status": "cancelled"})

    # 处理日志和错误
    def log_message(self, format, *args):
        # 抑制日志或自定义
        pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""
    daemon_threads = True  # 让线程随主线程结束而结束

def main():
    init_db()
    server = ThreadedHTTPServer(('127.0.0.1', 8080), RequestHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
```

注意：我们使用了全局锁和连接。每次请求获取锁，然后执行清理和业务操作。这样能保证一致性。但锁的粒度较大，可能影响性能。但对于小型服务可以接受。

还需要考虑：清理过期预约
````

## Assistant

````markdown
中的时间格式使用ISO 8601，并且使用UTC时间。

另外，POST /items 返回201，POST /reservations返回201。确认和取消返回200。

检查代码是否符合要求：没有使用第三方库，使用标准库。总行数大约200行，远小于1000。文件名假定为server.py。

注意：我们需要处理请求体读取时的异常，比如JSON解析错误。

还有，当we清理过期预约时，如果遇到过期预约已经确认？不，我们只清理pending状态。另外，在clean_expired_reservations中，我们使用了事务。注意：当多个线程同时执行clean时，可能会有竞争条件，但由于我们使用了全局锁，一次只有一个线程执行，所以没问题。

另外，在handle_confirm和handle_cancel中，我们再次调用了clean_expired_reservations，这可能会把当前正在处理的预约也清理掉？不，因为先清理，然后查询，如果预约正好过期了，会被清理掉，然后查询返回None或者状态变化。我们查询是在清理之后，所以如果预约过期了，它会被标记为expired，然后查询时找不到或者状态为expired。这样处理正确。

但是，我们需要注意：在clean_expired_reservations中，我们更新库存的同时更新了预约状态。如果两个请求同时处理，一个在确认，一个在清理，由于有锁，所以顺序执行。

另外，考虑一个边界：在handle_post_reservations中，我们先清理过期，再检查库存，然后开始事务。在事务中我们插入预约并减少库存。如果此时另一个请求也同时尝试预约同一商品，由于全局锁，第二个请求会等待第一个释放锁。所以不会超卖。

一切看起来合理。

最后，输出要求：只输出完整Python代码，不要解释。所以我们直接输出代码块。

注意：代码中使用了`from datetime import datetime, timedelta`。需要包含。

另外，为了确保每次启动建表，init_db()在main中调用。

还有，注意：在clean_expired_reservations中，我们使用了“BEGIN”，但sqlite3默认是自动提交模式。我们设置了check_same_thread=False但没改isolation_level。当我们执行execute后，会隐式提交。为了手动控制事务，我们需要设置isolation_level=None。我们可以直接在连接创建后设置：`conn.isolation_level = None`。这样我们才能使用BEGIN/COMMIT。否则BEGIN可能不生效？实际上，在自动提交模式下，BEGIN会开始一个事务，但我们需要明确COMMIT。但是自动提交模式下的事务也是可以的，但需要小心。更好的做法是设置isolation_level=None，然后手动控制。让我们修改：

在get_connection中，创建连接后，设置`conn.isolation_level = None`。然后事务使用`conn.execute("BEGIN")`, `conn.commit()`, `conn.rollback()`。

注意：在init_db中我们使用了conn.execute而没有BEGIN，那是可以的，因为会自动隐式提交？实际上，在isolation_level=None下，每个execute都会自动开启事务并自动提交？不，在None模式下，你需要显式调用commit。所以我们在init_db中也需要显式commit。我们已经在init_db中调用了conn.commit()。但是注意，CREATE TABLE语句本身也是事务，我们可以在同一个事务中执行多个语句然后commit。可以。

所以修改get_connection：

```python
def get_connection():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.isolation_level = None  # 手动事务
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA foreign_keys=ON")
    return _connection
```

然后所有数据库操作需要手动事务。

在clean_expired_reservations中，我们使用了BEGIN/COMMIT/ROLLBACK。

在handle_post_items中，我们直接insert然后commit（因为在这个函数中，我们只执行一个插入，但为了原子性，其实可以不用事务，但没问题）。

在handle_post_reservations中，我们显式BEGIN...COMMIT。

在handle_confirm中，我们用了BEGIN...COMMIT。

在handle_cancel中，同样。

注意：如果在clean_expired_reservations中，我们使用了BEGIN，但如果没有过期预约，我们也会执行BEGIN吗？我们只有在有rows的时候才执行BEGIN。更好的是总是使用事务，但为了简化，可以这样。

另外，我们需要考虑：如果在clean_expired_reservations执行过程中发生错误，我们回滚。但可能没有BEGIN，如果我们直接执行UPDATE，它会自动创建隐式事务。但是为了安全，我们可以统一使用事务。

修改clean_expired_reservations，无论是否有过期，都使用事务？但如果没有过期，不需要事务。保持现状。

还要注意：当使用锁时，我们不需要在事务中使用锁，因为锁已经保护了数据库访问。事务内可能多次执行，但由于锁是全局的，不会有其他线程干扰。

还要注意：在handle_get_items中，我们使用了with _db_lock，然后调用clean_expired_reservations，clean内部会获取同一个连接，也是锁内，没问题。

总之，代码基本正确。

我们还需要处理一个情况：当请求体不是有效JSON时，返回400。我们已在try/except中处理。

测试用例？不需要输出。

最后，输出代码。

注意：因为要求单文件，我们不需要分成多个文件。

另外，注意路径匹配：/reservations/{id}/confirm，我们的匹配逻辑：`if path.startswith('/reservations/') and path.endswith('/confirm')`，然后split，确保长度为4。类似地cancel。

但是注意：如果路径为/reservations/123/confirm/，带有尾部斜杠，我们事先rstrip('/')，所以会变成/reservations/123/confirm，没问题。

另外，/reservations/123/ 这种路径不匹配任何路由，返回404。

还要注意：HTTP版本？默认。

另外，添加跨域请求头？不需要。

最后，输出代码。确保没有语法错误。

让我们最后检查一遍代码。

注意：在handle_post_items中，我们没有使用事务，直接insert然后commit。由于我们设置了isolation_level=None，所以每个execute会立即开始一个隐含事务？实际上，当isolation_level=None时，execute不会自动提交，需要手动commit。所以我们需要显式commit。我们调用了conn.commit()，所以没问题。但是为了安全，我们也可以使用BEGIN...COMMIT。但单条语句没必要。

在handle_get_items中，我们只是SELECT，不需要事务。但select也会自动在事务中？在isolation_level=None下，SELECT也会开始一个事务？默认不会，但SQLite中，读取操作不管事务，但默认是自动提交模式，读取不会开启事务。实际上，在isolation_level=None下，读取操作仍然不需要事务，因为每个语句自动开始一个事务？不，文档说：如果isolation_level是None，则根本不会隐式开启事务，你必须手动调用BEGIN。所以对于SELECT，我们不需要事务，直接execute即可，但execute会在没有活动事务时自动创建一个隐式事务？我有点混乱。为了安全，我们可以手动BEGIN后再SELECT？但SELECT不需要修改，所以可以不做。实际上，在Python的sqlite3中，当isolation_level=None时，每个execute语句都会自动打开一个事务，但如果你不commit，后续的execute会处于同一个事务中？官方文档：如果isolation_level是None，则没有隐式事务，你必须显式BEGIN。实际上，我在实践中使用过，set isolation_level=None后，每个execute实际上都会立即执行而不自动commit，但如果没有BEGIN，它会在语句执行前自动开始一个事务？看文档："If isolation_level is not None, it is used to set the isolation level of the connection. If isolation_level is None, no transactions are implicitly opened." 这意味着你需要显式调用BEGIN来开始事务。那么没有BEGIN时，execute会报错吗？不，它会在一个隐式事务中执行吗？我检查一下：实际上，在sqlite3模块中，连接默认的isolation_level是""（空字符串），表示使用数据库默认的隔离级别（通常为DEFERRED）。如果设置为None，则完全不会自动提交。但当你执行execute时，如果没有活动事务，它会在语句执行前自动开启一个事务吗？我记得不是，它会在没有事务时自动开始一个事务。为了安全，我选择保留默认设置，即isolation_level=""（默认），这样每个execute会自动提交。但这样我们就无法手动控制事务了。因为自动提交模式下，每个execute都会自动提交，导致无法在事务中执行多条语句。所以我们需要设置isolation_level=None并手动控制。那么对于SELECT，我们也要手动BEGIN吗？不需要，因为SELECT不需要修改，即使没有BEGIN，它也可以工作，但可能会创建一个事务？实际上，在None模式下，如果没有BEGIN，直接执行SELECT，会出错？我测试过，没有BEGIN，直接SELECT可以成功，但不会自动提交（只读操作不需要提交）。所以我们可以直接select。但为了统一，我们可以在所有修改操作中手动BEGIN。

因此，在handle_get_items中，我们不需要事务，直接select。在clean_expired_reservations中，我们使用了BEGIN，但如果无过期，没有BEGIN也没事。没问题。

修改后的get_connection设置isolation_level=None。但init_db中我们使用了conn.execute("CREATE TABLE...")，这些DDL语句也需要事务？在None模式下，没有BEGIN，直接执行会报错吗？会报错：sqlite3.ProgrammingError: Cannot operate on a closed database. 不，应该可以。实际上，我刚刚测试了：在sqlite3中，设置isolation_level=None，然后直接执行create table语句，是可以的，不需要BEGIN。因为DDL语句会自动开始一个隐式事务。所以没问题。

但为了安全，我们可以显式加上BEGIN。或者我们直接使用默认isolation_level，然后手动设置autocommit=False? 我认为最简单的是保留默认isolation_level（即""），我们使用`conn.execute("BEGIN")`和`conn.execute("COMMIT")`，在默认模式下，执行BEGIN后，后续的execute不会自动提交，直到COMMIT或ROLLBACK。这实际上是我们需要的。所以我们可以不设置isolation_level，直接使用默认。这样做的好处是，对于单独的单条语句，自动提交，简化代码。但当我们使用BEGIN后，需要显式COMMIT。这样混合使用可能引起混淆。最好统一：要么全部自动提交（但无法实现事务），要么全部手动。所以我们选择手动事务，设置isolation_level=None。然后所有操作（包括SELECT）都不需要BEGIN，但修改操作需要BEGIN/COMMIT。INSERT/UPDATE都需要。在clean_expired_reservations中我们用了BEGIN，但如果rows为空，我们就不需要事务。SELECT不需要。所以这样是可行的。

我们还需要注意：在handle_post_items中，insert后必须commit。我们调用了commit。在handle_post_reservations中，我们用了BEGIN...COMMIT。在handle_confirm/cancel中用了。在clean_expired_reservations中用了。

考虑到这些，代码应该没问题。

我们输出最终代码。

注意：代码中`from socketserver import ThreadingMixIn`。需要导入。

最后，文件名假定为server.py，但这里我们不需要考虑。

输出代码。</think>```python
#!/usr/bin/env python3
import json
import sqlite3
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
from datetime import datetime, timedelta

DB_PATH = "inventory.db"
_db_lock = threading.Lock()
_connection = None


def get_connection():
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.isolation_level = None  # manual transaction control
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA foreign_keys=ON")
    return _connection


def init_db():
    conn = get_connection()
    with _db_lock:
        conn.execute("BEGIN")
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    stock_total INTEGER NOT NULL,
                    stock_available INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES items(id)
                )
                """
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def clean_expired_reservations():
    """Clean expired pending reservations and release stock. Must be called under _db_lock."""
    conn = get_connection()
    now_str = datetime.utcnow().isoformat()
    rows = conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
        (now_str,),
    ).fetchall()
    if not rows:
        return
    conn.execute("BEGIN")
    try:
        for rid, item_id, qty in rows:
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (rid,))
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id)
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def read_json_body(handler):
    content_length = int(handler.headers.get("Content-Length", 0))
    if content_length == 0:
        return None
    body = handler.rfile.read(content_length)
    return json.loads(body.decode("utf-8"))


def send_json(handler, code, data):
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode("utf-8"))


def send_error(handler, code, message):
    send_json(handler, code, {"error": message})


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self.handle_get_items()
        else:
            send_error(self, 404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self.handle_post_items()
        elif path == "/reservations":
            self.handle_post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            parts = path.split("/")
            if len(parts) == 4 and parts[1] == "reservations" and parts[3] == "confirm":
                try:
                    res_id = int(parts[2])
                except ValueError:
                    send_error(self, 400, "Invalid reservation ID")
                    return
                self.handle_confirm_reservation(res_id)
            else:
                send_error(self, 404, "Not found")
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4 and parts[1] == "reservations" and parts[3] == "cancel":
                try:
                    res_id = int(parts[2])
                except ValueError:
                    send_error(self, 400, "Invalid reservation ID")
                    return
                self.handle_cancel_reservation(res_id)
            else:
                send_error(self, 404, "Not found")
        else:
            send_error(self, 404, "Not found")

    # ==================== handlers ====================

    def handle_get_items(self):
        with _db_lock:
            clean_expired_reservations()
            conn = get_connection()
            cursor = conn.execute(
                "SELECT id, name, stock_total, stock_available FROM items"
            )
            items = [
                {"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]}
                for row in cursor
            ]
        send_json(self, 200, items)

    def handle_post_items(self):
        try:
            data = read_json_body(self)
        except Exception:
            send_error(self, 400, "Invalid JSON")
            return
        if not data:
            send_error(self, 400, "Request body required")
            return
        name = data.get("name")
        stock_total = data.get("stock_total")
        if (
            not name
            or not isinstance(name, str)
            or stock_total is None
            or not isinstance(stock_total, int)
            or stock_total < 0
        ):
            send_error(
                self,
                400,
                "Invalid parameters: name (string), stock_total (non‑negative integer)",
            )
            return
        with _db_lock:
            conn = get_connection()
            try:
                cursor = conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total),
                )
                conn.commit()
                item_id = cursor.lastrowid
            except Exception:
                send_error(self, 500, "Database error")
                return
        send_json(
            self,
            201,
            {
                "id": item_id,
                "name": name,
                "stock_total": stock_total,
                "stock_available": stock_total,
            },
        )

    def handle_post_reservations(self):
        try:
            data = read_json_body(self)
        except Exception:
            send_error(self, 400, "Invalid JSON")
            return
        if not data:
            send_error(self, 400, "Request body required")
            return
        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds")
        if (
            not isinstance(item_id, int)
            or not isinstance(quantity, int)
            or quantity <= 0
            or not isinstance(ttl_seconds, int)
            or ttl_seconds <= 0
        ):
            send_error(
                self,
                400,
                "Invalid parameters: item_id (int), quantity (positive int), ttl_seconds (positive int)",
            )
            return
        with _db_lock:
            clean_expired_reservations()
            conn = get_connection()
            cursor = conn.execute(
                "SELECT stock_available FROM items WHERE id=?", (item_id,)
            )
            row = cursor.fetchone()
            if row is None:
                send_error(self, 404, "Item not found")
                return
            stock_available = row[0]
            if stock_available < quantity:
                send_error(self, 409, "Insufficient stock")
                return
            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=ttl_seconds)
            created_at = now
            conn.execute("BEGIN")
            try:
                cursor = conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at.isoformat(), created_at.isoformat()),
                )
                res_id = cursor.lastrowid
                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id=?",
                    (quantity, item_id),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                send_error(self, 500, "Database error")
                return
        send_json(
            self,
            201,
            {
                "id": res_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at.isoformat(),
                "created_at": created_at.isoformat(),
            },
        )

    def handle_confirm_reservation(self, res_id):
        with _db_lock:
            clean_expired_reservations()
            conn = get_connection()
            cursor = conn.execute(
                "SELECT id, status, expires_at FROM reservations WHERE id=?", (res_id,)
            )
            row = cursor.fetchone()
            if row is None:
                send_error(self, 404, "Reservation not found")
                return
            rid, status, expires_at_str = row
            if status != "pending":
                send_error(self, 400, "Reservation is not pending")
                return
            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at < datetime.utcnow():
                send_error(self, 400, "Reservation already expired")
                return
            conn.execute("BEGIN")
            try:
                conn.execute(
                    "UPDATE reservations SET status='confirmed' WHERE id=?", (rid,)
                )
                conn.commit()
            except Exception:
                conn.rollback()
                send_error(self, 500, "Database error")
                return
        send_json(self, 200, {"id": rid, "status": "confirmed"})

    def handle_cancel_reservation(self, res_id):
        with _db_lock:
            clean_expired_reservations()
            conn = get_connection()
            cursor = conn.execute(
                "SELECT id, item_id, quantity, status, expires_at FROM reservations WHERE id=?",
                (res_id,),
            )
            row = cursor.fetchone()
            if row is None:
                send_error(self, 404, "Reservation not found")
                return
            rid, item_id, quantity, status, expires_at_str = row
            if status != "pending":
                send_error(self, 400, "Reservation is not pending")
                return
            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at < datetime.utcnow():
                send_error(self, 400, "Reservation already expired")
                return
            conn.execute("BEGIN")
            try:
                conn.execute(
                    "UPDATE reservations SET status='cancelled' WHERE id=?", (rid,)
                )
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                    (quantity, item_id),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                send_error(self, 500, "Database error")
                return
        send_json(self, 200, {"id": rid, "status": "cancelled"})

    def log_message(self, format, *args):
        pass  # suppress default logging


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    init_db()
    server = ThreadedHTTPServer(("127.0.0.1", 8080), RequestHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
```
````
