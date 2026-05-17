# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 18.534013
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 3717, "completion_tokens": 3354, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 3354
- Total tokens: 3717

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
我们要求用户输出完整的 Python 代码，不要解释。需要实现一个基于 Python 3 标准库的 HTTP API 服务，使用 sqlite3 持久化，单文件 server.py，不超过1000行。需要实现商品和预约的 CRUD 以及过期清理、并发控制等。

需要包含：http.server 或 socketserver 中的 BaseHTTPRequestHandler？通常使用 http.server 的 HTTPServer 和 BaseHTTPRequestHandler。但处理 JSON 和路由需要自己解析。或者使用 wsgiref 的 simple_server？但 wsgiref 也属于标准库。更常见的是用 http.server。

注意：需要支持 RESTful 路径和 POST 请求体解析。实现一个简单的路由分发。

设计：
- 数据库初始化：创建 items 和 reservations 表。
- 每个请求前清理过期预约。可以在处理每个请求时先执行清理（使用事务）。
- 并发控制：使用 threading.Lock 全局锁，确保所有数据库操作串行化，避免竞争条件。
- 商品新增：name, stock_total 必须提供；stock_available 初始等于 stock_total。
- 创建预约：检查 item_id存在且可用库存≥quantity，使用 TTL（秒）计算 expires_at = now + ttl_seconds。插入预约记录，减少可用库存。返回201。库存不足返回409。
- 确认预约：将 status 改为 confirmed，不调整库存（已扣减）。若预约不存在或不是 pending 则返回错误。
- 取消预约：将 status 改为 cancelled，增加可用库存。若不存在或不是 pending 则返回错误。
- 错误响应：返回 JSON 包含 error 字段，状态码 4xx/5xx。
- 未处理的路径返回404。

代码结构：
- 继承 BaseHTTPRequestHandler 并实现 do_GET, do_POST。
- 使用 urlparse 解析路径和查询参数。
- 使用 json 模块解析请求体。
- 使用 sqlite3 连接，注意连接线程安全？每个请求创建独立的连接？但全局锁可以保证串行化，使用一个全局连接？或每个请求创建连接？建议每个请求一个连接，因为 sqlite3 的 connection 不是线程安全的，但全局锁保证同时只有一个线程访问数据库，所以可以共享一个连接？简单起见，每个请求创建新连接，并在锁内使用。或者使用全局连接，但需要在锁内使用。更安全的是每个请求创建新连接，但开销不大。
- 锁：定义一个全局锁 `db_lock = threading.Lock()`。
- 清理过期：每次处理请求前，执行一个函数 delete_expired_pending() 在事务内释放库存（查询过期 pending 预约，更新状态为 expired？或者直接删除？题目要求“清理已过期且仍为 pending 的预约并释放库存”。建议将状态改为 expired 并释放库存。但题目没有定义 expired 状态，但我们可以定义 status 为 pending, confirmed, cancelled, expired。原始字段只有 status，没有明确说 expired，但可以增加。或者直接删除？为了可追溯，建议更新状态为 expired。同时增加可用库存。注意：释放库存时，需要确保只释放一次，所以在事务内先查询所有过期 pending 预约，然后更新它们的 status = 'expired'，同时更新 items.stock_available += quantity。但是可能存在多个预约针对同一商品，需要按 item_id 分组求和？更简单：逐条处理，每条预约更新对应商品的可用库存。

因为库存一致性要求高，使用事务内的原子操作。锁保证串行。

实现细节：
- 路径匹配：用正则或字符串分割。
- 对于 POST /reservations/{id}/confirm 和 cancel，需要解析路径，提取 id。
- 返回 JSON 响应：设置 Content-Type: application/json。
- 处理异常：如 JSON 解析错误，返回400。

代码长度控制：不超过1000行，实际应该远小于。

输出：仅输出代码。
```

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""
Small HTTP API service for inventory reservation.
Uses only Python 3 standard library.
"""

import json
import sqlite3
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ------------------------------------------------------------
# Database setup
# ------------------------------------------------------------
DB_FILE = "inventory.db"
db_lock = threading.Lock()

def init_db():
    """Create tables if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
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
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)
        conn.commit()

# ------------------------------------------------------------
# Expired reservation cleanup (called before each request)
# ------------------------------------------------------------
def cleanup_expired():
    """Release stock for pending reservations that have expired.
    Runs inside a transaction."""
    now = time.time()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("BEGIN")
        # Find expired pending reservations
        rows = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
            (now,)
        ).fetchall()
        if rows:
            for rid, item_id, qty in rows:
                # Update reservation status to expired
                conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (rid,))
                # Restore stock
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                    (qty, item_id)
                )
        conn.execute("COMMIT")

# ------------------------------------------------------------
# Helper: send JSON response
# ------------------------------------------------------------
def send_json(handler, data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)

def send_error(handler, message, status=400):
    send_json(handler, {"error": message}, status)

# ------------------------------------------------------------
# Request handler
# ------------------------------------------------------------
class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for inventory API."""

    def do_GET(self):
        with db_lock:
            cleanup_expired()
            self._handle_get()

    def do_POST(self):
        with db_lock:
            cleanup_expired()
            self._handle_post()

    def _handle_get(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self._list_items()
        else:
            send_error(self, "Not found", 404)

    def _handle_post(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self._add_item()
        elif path == "/reservations":
            self._create_reservation()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            # Extract reservation id
            parts = path.split("/")
            if len(parts) == 4:
                try:
                    rid = int(parts[2])
                except ValueError:
                    send_error(self, "Invalid reservation id", 400)
                    return
                self._confirm_reservation(rid)
            else:
                send_error(self, "Invalid path", 404)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4:
                try:
                    rid = int(parts[2])
                except ValueError:
                    send_error(self, "Invalid reservation id", 400)
                    return
                self._cancel_reservation(rid)
            else:
                send_error(self, "Invalid path", 404)
        else:
            send_error(self, "Not found", 404)

    # ---- GET /items ----
    def _list_items(self):
        with sqlite3.connect(DB_FILE) as conn:
            rows = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
        items = []
        for r in rows:
            items.append({
                "id": r[0],
                "name": r[1],
                "stock_total": r[2],
                "stock_available": r[3]
            })
        send_json(self, items)

    # ---- POST /items ----
    def _add_item(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            send_error(self, "Empty body", 400)
            return
        try:
            body = json.loads(self.rfile.read(content_len))
        except json.JSONDecodeError:
            send_error(self, "Invalid JSON", 400)
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            send_error(self, "Invalid or missing 'name' or 'stock_total'", 400)
            return
        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                # Get the newly created item id
                cursor = conn.execute("SELECT last_insert_rowid()")
                new_id = cursor.fetchone()[0]
            send_json(self, {"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
        except sqlite3.Error as e:
            send_error(self, f"Database error: {str(e)}", 500)

    # ---- POST /reservations ----
    def _create_reservation(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            send_error(self, "Empty body", 400)
            return
        try:
            body = json.loads(self.rfile.read(content_len))
        except json.JSONDecodeError:
            send_error(self, "Invalid JSON", 400)
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            send_error(self, "Invalid or missing 'item_id' or 'quantity'", 400)
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            send_error(self, "Invalid or missing 'ttl_seconds'", 400)
            return

        now = time.time()
        expires_at = now + ttl_seconds

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("BEGIN")
            try:
                # Check item exists and has enough stock
                row = conn.execute(
                    "SELECT id, stock_available FROM items WHERE id=?", (item_id,)
                ).fetchone()
                if row is None:
                    conn.execute("ROLLBACK")
                    send_error(self, "Item not found", 404)
                    return
                if row[1] < quantity:
                    conn.execute("ROLLBACK")
                    send_error(self, "Insufficient stock", 409)
                    return

                # Create reservation
                conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at, now)
                )
                cursor = conn.execute("SELECT last_insert_rowid()")
                new_rid = cursor.fetchone()[0]

                # Update available stock
                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id=?",
                    (quantity, item_id)
                )
                conn.execute("COMMIT")
                send_json(self, {
                    "id": new_rid,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": now
                }, 201)
            except sqlite3.Error as e:
                conn.execute("ROLLBACK")
                send_error(self, f"Database error: {str(e)}", 500)

    # ---- POST /reservations/{id}/confirm ----
    def _confirm_reservation(self, rid):
        with sqlite3.connect(DB_FILE) as conn:
            row = conn.execute(
                "SELECT id, status FROM reservations WHERE id=?", (rid,)
            ).fetchone()
            if row is None:
                send_error(self, "Reservation not found", 404)
                return
            if row[1] != "pending":
                send_error(self, f"Reservation cannot be confirmed (status: {row[1]})", 400)
                return
            conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (rid,))
            conn.commit()
        send_json(self, {"id": rid, "status": "confirmed"})

    # ---- POST /reservations/{id}/cancel ----
    def _cancel_reservation(self, rid):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("BEGIN")
            try:
                row = conn.execute(
                    "SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (rid,)
                ).fetchone()
                if row is None:
                    conn.execute("ROLLBACK")
                    send_error(self, "Reservation not found", 404)
                    return
                if row[3] != "pending":
                    conn.execute("ROLLBACK")
                    send_error(self, f"Reservation cannot be cancelled (status: {row[3]})", 400)
                    return
                item_id = row[1]
                quantity = row[2]
                # Update reservation status
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (rid,))
                # Restore stock
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                    (quantity, item_id)
                )
                conn.execute("COMMIT")
                send_json(self, {"id": rid, "status": "cancelled"})
            except sqlite3.Error as e:
                conn.execute("ROLLBACK")
                send_error(self, f"Database error: {str(e)}", 500)

    # ---- Silence logs ----
    def log_message(self, format, *args):
        return

# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), InventoryHandler)
    print("Inventory API server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```
````
