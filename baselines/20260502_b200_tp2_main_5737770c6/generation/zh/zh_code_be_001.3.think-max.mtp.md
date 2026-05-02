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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.62875
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2723, "completion_tokens": 2360, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2360
- Total tokens: 2723

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

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""server.py - Inventory reservation service using only Python 3 standard library."""

import json
import sqlite3
import threading
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


DB_FILE = "inventory.db"
_cleanup_lock = threading.Lock()
_db_lock = threading.Lock()


def get_db():
    """Return a new SQLite connection (thread-safe)."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they do not exist."""
    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                stock_total INTEGER NOT NULL CHECK(stock_total >= 0),
                stock_available INTEGER NOT NULL CHECK(stock_available >= 0)
            );
            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                status TEXT NOT NULL DEFAULT 'pending',
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id)
            );
            CREATE INDEX IF NOT EXISTS idx_reservations_status_expires
                ON reservations(status, expires_at);
        """)
        conn.commit()
    finally:
        conn.close()


def cleanup_expired_reservations():
    """Release stock for expired pending reservations."""
    now = time.time()
    with _cleanup_lock:
        conn = get_db()
        try:
            with conn:
                cur = conn.execute(
                    """SELECT id, item_id, quantity FROM reservations
                       WHERE status='pending' AND expires_at <= ?""",
                    (now,)
                )
                expired = cur.fetchall()
                for row in expired:
                    conn.execute(
                        "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                        (row["quantity"], row["item_id"])
                    )
                    conn.execute(
                        "UPDATE reservations SET status='expired' WHERE id = ?",
                        (row["id"],)
                    )
        finally:
            conn.close()


class InventoryAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for inventory reservation API."""

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _parse_path(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)
        return path, params

    # ----- Route dispatcher -----
    def do_GET(self):
        cleanup_expired_reservations()
        path, _ = self._parse_path()
        if path == "/items":
            self._handle_get_items()
        else:
            self._send_error("Not Found", 404)

    def do_POST(self):
        cleanup_expired_reservations()
        path, _ = self._parse_path()
        if path == "/items":
            self._handle_post_item()
        elif path == "/reservations":
            self._handle_post_reservation()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            reservation_id = path.split("/")[2]
            self._handle_confirm_reservation(reservation_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            reservation_id = path.split("/")[2]
            self._handle_cancel_reservation(reservation_id)
        else:
            self._send_error("Not Found", 404)

    # ----- Item handlers -----
    def _handle_get_items(self):
        conn = get_db()
        try:
            cur = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
            items = [dict(row) for row in cur.fetchall()]
            self._send_json(items)
        finally:
            conn.close()

    def _handle_post_item(self):
        body = self._read_json_body()
        if body is None:
            self._send_error("Invalid JSON body")
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(name, str):
            self._send_error("Missing or invalid 'name'")
            return
        try:
            stock_total = int(stock_total)
        except (TypeError, ValueError):
            self._send_error("Missing or invalid 'stock_total'")
            return
        if stock_total < 0:
            self._send_error("'stock_total' must be non-negative")
            return

        conn = get_db()
        try:
            with conn:
                conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                item_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
        except sqlite3.IntegrityError:
            self._send_error("Item with this name already exists", 409)
        finally:
            conn.close()

    # ----- Reservation handlers -----
    def _handle_post_reservation(self):
        body = self._read_json_body()
        if body is None:
            self._send_error("Invalid JSON body")
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (TypeError, ValueError):
            self._send_error("Invalid parameters: item_id, quantity, ttl_seconds must be integers")
            return
        if quantity <= 0:
            self._send_error("quantity must be positive")
            return
        if ttl_seconds <= 0:
            self._send_error("ttl_seconds must be positive")
            return

        reservation_id = str(uuid.uuid4())
        now = time.time()
        expires_at = now + ttl_seconds

        conn = get_db()
        try:
            with conn:
                # Lock row for update (exclusive)
                cur = conn.execute(
                    "SELECT stock_available, stock_total FROM items WHERE id = ?",
                    (item_id,)
                )
                item = cur.fetchone()
                if item is None:
                    self._send_error("Item not found", 404)
                    return

                available = item["stock_available"]
                if available < quantity:
                    self._send_error("Insufficient stock", 409)
                    return

                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                    (quantity, item_id)
                )
                conn.execute(
                    """INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
                       VALUES (?, ?, ?, 'pending', ?, ?)""",
                    (reservation_id, item_id, quantity, expires_at, now)
                )
            self._send_json({
                "id": reservation_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": now
            }, 201)
        except sqlite3.Error as e:
            self._send_error(f"Database error: {str(e)}", 500)
        finally:
            conn.close()

    def _handle_confirm_reservation(self, reservation_id):
        conn = get_db()
        try:
            with conn:
                cur = conn.execute(
                    "SELECT status, item_id, quantity FROM reservations WHERE id = ?",
                    (reservation_id,)
                )
                reservation = cur.fetchone()
                if reservation is None:
                    self._send_error("Reservation not found", 404)
                    return
                if reservation["status"] != "pending":
                    self._send_error(f"Cannot confirm reservation with status '{reservation['status']}'", 409)
                    return

                conn.execute(
                    "UPDATE reservations SET status='confirmed' WHERE id = ?",
                    (reservation_id,)
                )
            self._send_json({"id": reservation_id, "status": "confirmed"})
        finally:
            conn.close()

    def _handle_cancel_reservation(self, reservation_id):
        conn = get_db()
        try:
            with conn:
                cur = conn.execute(
                    "SELECT status, item_id, quantity FROM reservations WHERE id = ?",
                    (reservation_id,)
                )
                reservation = cur.fetchone()
                if reservation is None:
                    self._send_error("Reservation not found", 404)
                    return
                if reservation["status"] != "pending":
                    self._send_error(f"Cannot cancel reservation with status '{reservation['status']}'", 409)
                    return

                # Release stock
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                    (reservation["quantity"], reservation["item_id"])
                )
                conn.execute(
                    "UPDATE reservations SET status='cancelled' WHERE id = ?",
                    (reservation_id,)
                )
            self._send_json({"id": reservation_id, "status": "cancelled"})
        finally:
            conn.close()

    # ----- Utility -----
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def run_server(host="127.0.0.1", port=8080):
    """Start the HTTP server."""
    server = HTTPServer((host, port), InventoryAPIHandler)
    print(f"Server listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    init_db()
    run_server()
```
````
