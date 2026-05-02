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
- Elapsed seconds: 17.644862
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2286, "completion_tokens": 1923, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1923
- Total tokens: 2286

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

DB_PATH = "inventory.db"
LOCK = threading.Lock()


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)
        conn.commit()


def cleanup_expired():
    with LOCK:
        with sqlite3.connect(DB_PATH) as conn:
            now = datetime.utcnow().isoformat()
            expired = conn.execute(
                "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
                (now,)
            ).fetchall()
            for res_id, item_id, qty in expired:
                conn.execute("DELETE FROM reservations WHERE id=?", (res_id,))
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                    (qty, item_id)
                )
            conn.commit()


class InventoryAPIHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status=status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        cleanup_expired()

        if path == "/items":
            with LOCK:
                with sqlite3.connect(DB_PATH) as conn:
                    rows = conn.execute(
                        "SELECT id, name, stock_total, stock_available FROM items"
                    ).fetchall()
            items = [
                {"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]}
                for r in rows
            ]
            self._send_json(items)
        else:
            self._send_error("Not Found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_body()
        if body is None:
            self._send_error("Invalid JSON")
            return

        cleanup_expired()

        if path == "/items":
            self._handle_create_item(body)
        elif path == "/reservations":
            self._handle_create_reservation(body)
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self._handle_confirm_reservation(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self._handle_cancel_reservation(res_id)
        else:
            self._send_error("Not Found", 404)

    def _handle_create_item(self, body):
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self._send_error("Invalid parameters: name (str) and stock_total (int >=0)")
            return
        with LOCK:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                item_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_create_reservation(self, body):
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds", 300)
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            self._send_error("Invalid parameters: item_id (int) and quantity (int >0)")
            return
        if not isinstance(ttl_seconds, int) or ttl_seconds < 1:
            self._send_error("ttl_seconds must be positive integer")
            return

        res_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        expires_at = (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()

        with LOCK:
            with sqlite3.connect(DB_PATH) as conn:
                item = conn.execute(
                    "SELECT stock_available FROM items WHERE id=? FOR UPDATE", (item_id,)
                ).fetchone()
                if not item:
                    self._send_error("Item not found", 404)
                    return
                available = item[0]
                if available < quantity:
                    self._send_error("Insufficient stock", 409)
                    return
                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id=?",
                    (quantity, item_id)
                )
                conn.execute(
                    "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                    (res_id, item_id, quantity, expires_at, created_at)
                )
                conn.commit()
        self._send_json({
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        }, 201)

    def _handle_confirm_reservation(self, res_id):
        with LOCK:
            with sqlite3.connect(DB_PATH) as conn:
                res = conn.execute(
                    "SELECT id, status, item_id, quantity FROM reservations WHERE id=?",
                    (res_id,)
                ).fetchone()
                if not res:
                    self._send_error("Reservation not found", 404)
                    return
                if res[1] != "pending":
                    self._send_error(f"Reservation already {res[1]}", 400)
                    return
                conn.execute(
                    "UPDATE reservations SET status='confirmed' WHERE id=?",
                    (res_id,)
                )
                conn.commit()
        self._send_json({"message": "Reservation confirmed"})

    def _handle_cancel_reservation(self, res_id):
        with LOCK:
            with sqlite3.connect(DB_PATH) as conn:
                res = conn.execute(
                    "SELECT id, status, item_id, quantity FROM reservations WHERE id=?",
                    (res_id,)
                ).fetchone()
                if not res:
                    self._send_error("Reservation not found", 404)
                    return
                if res[1] != "pending":
                    self._send_error(f"Reservation already {res[1]}, cannot cancel", 400)
                    return
                conn.execute(
                    "DELETE FROM reservations WHERE id=?",
                    (res_id,)
                )
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                    (res[3], res[2])
                )
                conn.commit()
        self._send_json({"message": "Reservation cancelled and stock released"})

    def log_message(self, format, *args):
        # Suppress default logging
        pass


if __name__ == "__main__":
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), InventoryAPIHandler)
    print("Inventory API server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
```
````
