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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 34.811379
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2582, "completion_tokens": 2219, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2219
- Total tokens: 2582

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
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
from contextlib import contextmanager

DB_NAME = "inventory.db"
LOCK = threading.Lock()

# ---------- Database Setup ----------
def init_db():
    with sqlite3.connect(DB_NAME, check_same_thread=False) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                item_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(item_id) REFERENCES items(id)
            )
        """)
        conn.commit()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# ---------- Utility ----------
def generate_id():
    return str(uuid.uuid4())

def now_iso():
    return datetime.utcnow().isoformat() + "Z"

def parse_json(body):
    try:
        return json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return None

# ---------- Cleanup expired reservations ----------
def cleanup_expired():
    """Remove expired pending reservations and release stock."""
    with LOCK:
        with get_db() as conn:
            now = now_iso()
            expired = conn.execute(
                "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
                (now,)
            ).fetchall()
            for res in expired:
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                    (res["quantity"], res["item_id"])
                )
                conn.execute("DELETE FROM reservations WHERE id = ?", (res["id"],))

# ---------- Request Handler ----------
class InventoryHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body.encode("utf-8")))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status)

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return None
        return self.rfile.read(content_length)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/items":
            self._handle_get_items()
        else:
            self._send_error("Not Found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/items":
            self._handle_post_items()
        elif path == "/reservations":
            self._handle_post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self._handle_confirm(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self._handle_cancel(res_id)
        else:
            self._send_error("Not Found", 404)

    # ---------- GET /items ----------
    def _handle_get_items(self):
        cleanup_expired()
        with get_db() as conn:
            rows = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
            items = [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "stock_total": r["stock_total"],
                    "stock_available": r["stock_available"]
                }
                for r in rows
            ]
        self._send_json(items)

    # ---------- POST /items ----------
    def _handle_post_items(self):
        body = self._read_body()
        data = parse_json(body)
        if not data or "name" not in data or "stock_total" not in data:
            self._send_error("Missing required fields: name, stock_total")
            return
        name = data["name"]
        try:
            stock_total = int(data["stock_total"])
        except (ValueError, TypeError):
            self._send_error("stock_total must be an integer")
            return
        if stock_total < 0:
            self._send_error("stock_total must be non-negative")
            return

        item_id = generate_id()
        with LOCK:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO items (id, name, stock_total, stock_available) VALUES (?, ?, ?, ?)",
                    (item_id, name, stock_total, stock_total)
                )
        self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    # ---------- POST /reservations ----------
    def _handle_post_reservations(self):
        body = self._read_body()
        data = parse_json(body)
        if not data or "item_id" not in data or "quantity" not in data or "ttl_seconds" not in data:
            self._send_error("Missing required fields: item_id, quantity, ttl_seconds")
            return
        item_id = data["item_id"]
        try:
            quantity = int(data["quantity"])
            ttl = int(data["ttl_seconds"])
        except (ValueError, TypeError):
            self._send_error("quantity and ttl_seconds must be integers")
            return
        if quantity <= 0 or ttl <= 0:
            self._send_error("quantity and ttl_seconds must be positive")
            return

        cleanup_expired()

        res_id = generate_id()
        created_at = now_iso()
        expires_at = (datetime.utcnow() + timedelta(seconds=ttl)).isoformat() + "Z"

        with LOCK:
            with get_db() as conn:
                # Check item exists and stock available
                item = conn.execute(
                    "SELECT id, stock_available FROM items WHERE id = ?",
                    (item_id,)
                ).fetchone()
                if not item:
                    self._send_error("Item not found", 404)
                    return
                if item["stock_available"] < quantity:
                    self._send_error("Insufficient stock", 409)
                    return

                # Reserve
                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                    (quantity, item_id)
                )
                conn.execute(
                    "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                    (res_id, item_id, quantity, expires_at, created_at)
                )

        self._send_json({
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        }, 201)

    # ---------- POST /reservations/{id}/confirm ----------
    def _handle_confirm(self, res_id):
        cleanup_expired()
        with LOCK:
            with get_db() as conn:
                res = conn.execute(
                    "SELECT id, status FROM reservations WHERE id = ?",
                    (res_id,)
                ).fetchone()
                if not res:
                    self._send_error("Reservation not found", 404)
                    return
                if res["status"] != "pending":
                    self._send_error(f"Reservation is already {res['status']}", 400)
                    return
                conn.execute(
                    "UPDATE reservations SET status = 'confirmed' WHERE id = ?",
                    (res_id,)
                )
        self._send_json({"message": "Reservation confirmed", "id": res_id})

    # ---------- POST /reservations/{id}/cancel ----------
    def _handle_cancel(self, res_id):
        cleanup_expired()
        with LOCK:
            with get_db() as conn:
                res = conn.execute(
                    "SELECT id, item_id, quantity, status FROM reservations WHERE id = ?",
                    (res_id,)
                ).fetchone()
                if not res:
                    self._send_error("Reservation not found", 404)
                    return
                if res["status"] != "pending":
                    self._send_error(f"Reservation is already {res['status']}, cannot cancel", 400)
                    return
                # Release stock
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                    (res["quantity"], res["item_id"])
                )
                conn.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
        self._send_json({"message": "Reservation cancelled", "id": res_id})

    # ---------- Override to suppress logs ----------
    def log_message(self, format, *args):
        pass  # Suppress default HTTP server logs

# ---------- Main ----------
def run_server(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), InventoryHandler)
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
