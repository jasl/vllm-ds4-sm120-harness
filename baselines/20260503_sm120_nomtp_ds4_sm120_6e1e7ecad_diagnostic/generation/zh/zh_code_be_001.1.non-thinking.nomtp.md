# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 37.963506
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2781, "completion_tokens": 2418, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2418
- Total tokens: 2781

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
import json
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = "inventory.db"
_LOCK = threading.Lock()
_DB_LOCAL = threading.local()


def get_db():
    """Get per-thread database connection."""
    if not hasattr(_DB_LOCAL, "conn") or _DB_LOCAL.conn is None:
        _DB_LOCAL.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _DB_LOCAL.conn.row_factory = sqlite3.Row
        _DB_LOCAL.conn.execute("PRAGMA journal_mode=WAL")
        _DB_LOCAL.conn.execute("PRAGMA foreign_keys=ON")
    return _DB_LOCAL.conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
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
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'cancelled')),
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        );

        CREATE INDEX IF NOT EXISTS idx_reservations_item_status ON reservations(item_id, status);
        CREATE INDEX IF NOT EXISTS idx_reservations_expires ON reservations(status, expires_at);
    """)
    conn.commit()


def cleanup_expired():
    """Cleanup expired pending reservations and release stock."""
    conn = get_db()
    now = datetime.utcnow().isoformat()
    cursor = conn.execute(
        """
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at < ?
        """,
        (now,)
    )
    expired = cursor.fetchall()
    for row in expired:
        conn.execute(
            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
            (row["quantity"], row["item_id"])
        )
        conn.execute(
            "UPDATE reservations SET status = 'cancelled' WHERE id = ?",
            (row["id"],)
        )
    if expired:
        conn.commit()


def json_response(handler, data, status=200):
    """Send JSON response."""
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.end_headers()
    handler.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


def error_response(handler, message, status=400):
    """Send error JSON response."""
    json_response(handler, {"error": message}, status)


def parse_json_body(handler):
    """Parse JSON request body."""
    content_length = int(handler.headers.get("Content-Length", 0))
    if content_length == 0:
        return None
    body = handler.rfile.read(content_length)
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for inventory reservation API."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def _send_method_not_allowed(self):
        error_response(self, "Method not allowed", 405)

    def _send_not_found(self):
        error_response(self, "Not found", 404)

    # ---- Route dispatching ----
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self._get_items()
        else:
            self._send_not_found()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self._post_items()
        elif path == "/reservations":
            self._post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self._post_reservations_confirm(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self._post_reservations_cancel(res_id)
        else:
            self._send_not_found()

    # ---- GET /items ----
    def _get_items(self):
        conn = get_db()
        with _LOCK:
            cleanup_expired()
            cursor = conn.execute("SELECT * FROM items ORDER BY id")
            items = [dict(row) for row in cursor.fetchall()]
        json_response(self, items)

    # ---- POST /items ----
    def _post_items(self):
        data = parse_json_body(self)
        if not data or "name" not in data or "stock_total" not in data:
            error_response(self, "Missing required fields: name, stock_total", 400)
            return

        name = data["name"].strip()
        stock_total = data["stock_total"]

        if not isinstance(stock_total, int) or stock_total < 0:
            error_response(self, "stock_total must be a non-negative integer", 400)
            return

        conn = get_db()
        with _LOCK:
            try:
                cursor = conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                item_id = cursor.lastrowid
                json_response(self, {"id": item_id, "name": name, "stock_total": stock_total,
                                     "stock_available": stock_total}, 201)
            except sqlite3.IntegrityError:
                error_response(self, "Item name already exists", 409)

    # ---- POST /reservations ----
    def _post_reservations(self):
        data = parse_json_body(self)
        if not data or "item_id" not in data or "quantity" not in data or "ttl_seconds" not in data:
            error_response(self, "Missing required fields: item_id, quantity, ttl_seconds", 400)
            return

        item_id = data["item_id"]
        quantity = data["quantity"]
        ttl_seconds = data["ttl_seconds"]

        if not isinstance(item_id, int) or item_id <= 0:
            error_response(self, "item_id must be a positive integer", 400)
            return
        if not isinstance(quantity, int) or quantity <= 0:
            error_response(self, "quantity must be a positive integer", 400)
            return
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            error_response(self, "ttl_seconds must be a positive integer", 400)
            return

        conn = get_db()
        with _LOCK:
            cleanup_expired()

            # Check item exists and has enough stock
            cursor = conn.execute(
                "SELECT id, stock_available, stock_total FROM items WHERE id = ?",
                (item_id,)
            )
            item = cursor.fetchone()
            if not item:
                error_response(self, "Item not found", 404)
                return

            if item["stock_available"] < quantity:
                error_response(self, "Insufficient stock", 409)
                return

            # Create reservation
            res_id = str(uuid.uuid4())[:8]
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            created_at = now.isoformat()

            # Deduct stock
            conn.execute(
                "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                (quantity, item_id)
            )
            conn.execute(
                "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                (res_id, item_id, quantity, expires_at, created_at)
            )
            conn.commit()

            json_response(self, {
                "id": res_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": created_at
            }, 201)

    # ---- POST /reservations/{id}/confirm ----
    def _post_reservations_confirm(self, res_id):
        conn = get_db()
        with _LOCK:
            cleanup_expired()

            cursor = conn.execute(
                "SELECT id, status FROM reservations WHERE id = ?",
                (res_id,)
            )
            reservation = cursor.fetchone()
            if not reservation:
                error_response(self, "Reservation not found", 404)
                return

            if reservation["status"] != "pending":
                error_response(self, f"Cannot confirm reservation with status '{reservation['status']}'", 400)
                return

            conn.execute(
                "UPDATE reservations SET status = 'confirmed' WHERE id = ?",
                (res_id,)
            )
            conn.commit()

            json_response(self, {"message": "Reservation confirmed", "id": res_id})

    # ---- POST /reservations/{id}/cancel ----
    def _post_reservations_cancel(self, res_id):
        conn = get_db()
        with _LOCK:
            cleanup_expired()

            cursor = conn.execute(
                "SELECT id, status, item_id, quantity FROM reservations WHERE id = ?",
                (res_id,)
            )
            reservation = cursor.fetchone()
            if not reservation:
                error_response(self, "Reservation not found", 404)
                return

            if reservation["status"] != "pending":
                error_response(self, f"Cannot cancel reservation with status '{reservation['status']}'", 400)
                return

            # Release stock
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (reservation["quantity"], reservation["item_id"])
            )
            conn.execute(
                "UPDATE reservations SET status = 'cancelled' WHERE id = ?",
                (res_id,)
            )
            conn.commit()

            json_response(self, {"message": "Reservation cancelled", "id": res_id})


def run_server(host="127.0.0.1", port=8080):
    """Start the HTTP server."""
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    init_db()
    run_server()
```
````
