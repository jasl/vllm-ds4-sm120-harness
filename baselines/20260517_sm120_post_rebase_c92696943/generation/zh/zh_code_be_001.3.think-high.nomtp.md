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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 34.071311
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 3734, "completion_tokens": 3371, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 3371
- Total tokens: 3734

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

```text
我们被要求写一个HTTP API服务，使用Python标准库，使用sqlite3数据库，实现简单的库存预约系统。需要处理并发，使用事务和线程锁。不需要第三方库，所以使用http.server模块或更底层的socket等。标准库中有http.server和BaseHTTPRequestHandler，可以用于构建简单的HTTP服务。需要注意的是，http.server是单线程的，但可以处理多个请求（串行）。但题目要求并发处理，可以使用threading.Thread来启动多个处理线程？实际上http.server的HTTPServer是阻塞的，只有一个线程处理请求。但我们可以使用ThreadingHTTPServer（Python 3.7+），它使用线程来处理每个请求。或者使用socketserver的ThreadingMixIn。这样就能并发处理。

具体实现步骤：
1. 创建SQLite数据库，自动建表。
2. 实现一个HTTP Handler类，继承BaseHTTPRequestHandler，重写do_GET, do_POST等方法。
3. 路由解析：根据路径和方法调用相应的处理函数。
4. 数据库操作：使用sqlite3，每次请求时获取连接，但需要注意线程安全：sqlite3的连接对象不是线程安全的，每个线程应该使用独立的连接，或者使用连接池并加锁。简单做法：为每个请求创建一个新连接，执行完后关闭。由于SQLite是文件锁，并发写入时会串行化，但多个连接可以同时读取。为了确保库存一致性，我们使用事务和锁（Python的threading.Lock）来保护关键区域。由于数据库本身有写入锁，但我们需要保证读取-修改-写入的原子性，使用事务和适当的隔离级别（默认即可）。但为了安全，可以在所有写操作上加一个全局锁，防止多个线程同时修改库存导致冲突。因为SQLite的并发写会排队，但如果你在事务中先读取再写入，别的事务可能同时读取了旧值，导致更新丢失。所以建议使用显式锁定（悲观锁）或使用BEGIN IMMEDIATE事务。Python的sqlite3支持设置事务隔离级别，可以使用BEGIN IMMEDIATE来立即获取写锁。这样可以避免手工加锁。但为了简单，我们使用一个全局的线程锁（RLock）来保护所有数据库写操作（包括创建预约、确认、取消）。另外，检查过期也需要加锁，因为会修改库存。

由于要求“每次请求前清理已过期且仍为 pending 的预约并释放库存”，所以每次收到请求（除了GET？）都需要先执行清理。最好在每个请求处理的开头都执行一次清理，包括GET？题目说“每次请求前”，可能包括所有请求？但GET不影响库存，不过为了数据一致性，也可以清理。我们就每个请求都清理一次，包括GET。但注意清理会修改数据库，所以也需要加锁。

实现细节：
- 使用正则或简单字符串匹配路径。
- 解析JSON从请求体。
- 返回JSON响应，设置Content-Type: application/json。
- 错误状态码：400, 404, 409等。
- 使用标准库json。

注意：BaseHTTPRequestHandler的do_GET和do_POST等方法需要读取URL路径，读取请求头，读取POST数据。读取POST数据需要知道Content-Length，并用self.rfile.read。

代码结构：
- 定义全局锁：db_lock = threading.Lock()
- 数据库初始化函数：init_db()
- 数据库连接函数：get_db() 返回连接，使用with语句。
- 清理过期预约函数：cleanup_expired(conn) 在锁内调用。
- 各个处理函数：handle_list_items, handle_create_item, handle_create_reservation, handle_confirm_reservation, handle_cancel_reservation。
- 路由解析在do_GET和do_POST中。

确保每个请求的数据库操作都在同一个连接上进行，并且事务正确提交或回滚。

编写代码注意不超过1000行，不会超过。

输出：只输出完整Python代码。
```

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""单文件 HTTP API 服务，实现库存预约管理。"""
import json
import sqlite3
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = "inventory.db"
db_lock = threading.Lock()


def init_db():
    """初始化数据库，创建表（如果不存在）。"""
    with sqlite3.connect(DB_PATH) as conn:
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
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)
        conn.commit()


def cleanup_expired(conn):
    """清理已过期的 pending 预约并释放库存（需在事务中调用）。"""
    now = time.time()
    # 找出所有过期的 pending 预约
    rows = conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
        (now,)
    ).fetchall()
    for row in rows:
        res_id, item_id, qty = row
        # 释放库存
        conn.execute(
            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
            (qty, item_id)
        )
        # 标记为 cancelled（或 deleted）
        conn.execute(
            "UPDATE reservations SET status='cancelled' WHERE id = ?",
            (res_id,)
        )
    if rows:
        conn.commit()


def get_db():
    """获取一个新的数据库连接。"""
    return sqlite3.connect(DB_PATH)


class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器。"""

    def _send_json(self, status_code, data):
        """发送 JSON 响应。"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_json_body(self):
        """读取请求体并解析为 JSON 字典。"""
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def _parse_path(self):
        """解析路径，返回 (base_path, path_params) 元组。"""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        # 匹配 /reservations/<id>/confirm 或 /reservations/<id>/cancel
        parts = path.split("/")
        if len(parts) == 4 and parts[1] == "reservations" and parts[3] in ("confirm", "cancel"):
            return parts[3], parts[2]  # action, reservation_id
        return path, None

    def do_GET(self):
        """处理 GET 请求。"""
        path, _ = self._parse_path()
        if path == "/items":
            self._handle_list_items()
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        """处理 POST 请求。"""
        path, param = self._parse_path()
        if path == "/items":
            self._handle_create_item()
        elif path == "/reservations":
            self._handle_create_reservation()
        elif path == "confirm":
            self._handle_confirm_reservation(param)
        elif path == "cancel":
            self._handle_cancel_reservation(param)
        else:
            self._send_json(404, {"error": "Not Found"})

    def _handle_list_items(self):
        """GET /items：列出商品和可用库存。"""
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                rows = conn.execute(
                    "SELECT id, name, stock_total, stock_available FROM items"
                ).fetchall()
                items = [
                    {
                        "id": r[0],
                        "name": r[1],
                        "stock_total": r[2],
                        "stock_available": r[3]
                    }
                    for r in rows
                ]
                self._send_json(200, {"items": items})
            finally:
                conn.close()

    def _handle_create_item(self):
        """POST /items：新增商品。"""
        body = self._read_json_body()
        if body is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self._send_json(400, {"error": "Invalid parameters: name (string), stock_total (non-negative integer)"})
            return
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                # 检查是否已存在同名商品
                existing = conn.execute(
                    "SELECT id FROM items WHERE name = ?", (name,)
                ).fetchone()
                if existing:
                    self._send_json(400, {"error": f"Item with name '{name}' already exists"})
                    return
                conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                self._send_json(201, {
                    "id": new_id,
                    "name": name,
                    "stock_total": stock_total,
                    "stock_available": stock_total
                })
            except sqlite3.IntegrityError:
                self._send_json(400, {"error": "Item name conflict"})
            finally:
                conn.close()

    def _handle_create_reservation(self):
        """POST /reservations：创建预约。"""
        body = self._read_json_body()
        if body is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if not all(isinstance(x, int) for x in [item_id, quantity, ttl_seconds]):
            self._send_json(400, {"error": "Invalid parameters: item_id (int), quantity (int), ttl_seconds (int)"})
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self._send_json(400, {"error": "quantity and ttl_seconds must be positive"})
            return
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                # 检查商品是否存在及库存是否充足
                item = conn.execute(
                    "SELECT id, stock_available FROM items WHERE id = ?",
                    (item_id,)
                ).fetchone()
                if not item:
                    self._send_json(404, {"error": "Item not found"})
                    return
                if item[1] < quantity:
                    self._send_json(409, {"error": "Insufficient stock"})
                    return
                now = time.time()
                expires = now + ttl_seconds
                # 扣减库存
                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                    (quantity, item_id)
                )
                # 创建预约
                conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) "
                    "VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires, now)
                )
                conn.commit()
                new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                self._send_json(201, {
                    "id": new_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires,
                    "created_at": now
                })
            finally:
                conn.close()

    def _handle_confirm_reservation(self, res_id_str):
        """POST /reservations/{id}/confirm：确认预约。"""
        try:
            res_id = int(res_id_str)
        except ValueError:
            self._send_json(400, {"error": "Invalid reservation id"})
            return
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                row = conn.execute(
                    "SELECT id, status FROM reservations WHERE id = ?",
                    (res_id,)
                ).fetchone()
                if not row:
                    self._send_json(404, {"error": "Reservation not found"})
                    return
                if row[1] != "pending":
                    self._send_json(400, {"error": f"Reservation status is '{row[1]}', cannot confirm"})
                    return
                conn.execute(
                    "UPDATE reservations SET status = 'confirmed' WHERE id = ?",
                    (res_id,)
                )
                conn.commit()
                self._send_json(200, {"message": "Reservation confirmed", "id": res_id, "status": "confirmed"})
            finally:
                conn.close()

    def _handle_cancel_reservation(self, res_id_str):
        """POST /reservations/{id}/cancel：取消预约，释放库存。"""
        try:
            res_id = int(res_id_str)
        except ValueError:
            self._send_json(400, {"error": "Invalid reservation id"})
            return
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                row = conn.execute(
                    "SELECT id, status, item_id, quantity FROM reservations WHERE id = ?",
                    (res_id,)
                ).fetchone()
                if not row:
                    self._send_json(404, {"error": "Reservation not found"})
                    return
                if row[1] != "pending":
                    self._send_json(400, {"error": f"Reservation status is '{row[1]}', cannot cancel"})
                    return
                # 释放库存
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                    (row[3], row[2])
                )
                conn.execute(
                    "UPDATE reservations SET status = 'cancelled' WHERE id = ?",
                    (res_id,)
                )
                conn.commit()
                self._send_json(200, {"message": "Reservation cancelled", "id": res_id, "status": "cancelled"})
            finally:
                conn.close()


def run(host="127.0.0.1", port=8080):
    """启动 HTTP 服务器。"""
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    init_db()
    run()
```
````
