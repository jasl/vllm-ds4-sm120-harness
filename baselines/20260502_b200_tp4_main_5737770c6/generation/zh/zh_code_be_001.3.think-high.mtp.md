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
- Elapsed seconds: 8.487609
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2645, "completion_tokens": 2282, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2282
- Total tokens: 2645

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
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime, timedelta


DB_PATH = "inventory.db"
lock = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()


def clean_expired_reservations():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    with lock:
        cursor.execute("""
            SELECT id, item_id, quantity FROM reservations
            WHERE status = 'pending' AND expires_at < ?
        """, (now,))
        expired = cursor.fetchall()

        for res in expired:
            res_id, item_id, quantity = res
            cursor.execute("""
                UPDATE reservations SET status = 'expired' WHERE id = ?
            """, (res_id,))
            cursor.execute("""
                UPDATE items SET stock_available = stock_available + ?
                WHERE id = ?
            """, (quantity, item_id))

        conn.commit()
    conn.close()


class InventoryHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/items":
            self._handle_get_items()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/items":
            self._handle_post_items()
        elif path == "/reservations":
            self._handle_post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = int(path.split("/")[2])
            self._handle_confirm_reservation(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = int(path.split("/")[2])
            self._handle_cancel_reservation(res_id)
        else:
            self._send_json({"error": "Not Found"}, 404)

    # ---- GET /items ----
    def _handle_get_items(self):
        clean_expired_reservations()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
        rows = cursor.fetchall()
        conn.close()
        items = [
            {"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]}
            for r in rows
        ]
        self._send_json(items)

    # ---- POST /items ----
    def _handle_post_items(self):
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or stock_total is None:
            self._send_json({"error": "name and stock_total are required"}, 400)
            return
        if not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "stock_total must be a non-negative integer"}, 400)
            return

        clean_expired_reservations()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        with lock:
            cursor.execute("""
                INSERT INTO items (name, stock_total, stock_available)
                VALUES (?, ?, ?)
            """, (name, stock_total, stock_total))
            conn.commit()
            item_id = cursor.lastrowid
        conn.close()
        self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    # ---- POST /reservations ----
    def _handle_post_reservations(self):
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if not all([item_id, quantity, ttl_seconds]):
            self._send_json({"error": "item_id, quantity, ttl_seconds are required"}, 400)
            return
        if not isinstance(item_id, int) or not isinstance(quantity, int) or not isinstance(ttl_seconds, (int, float)):
            self._send_json({"error": "invalid parameter types"}, 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self._send_json({"error": "quantity and ttl_seconds must be positive"}, 400)
            return

        clean_expired_reservations()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()

        with lock:
            cursor.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Item not found"}, 404)
                return
            stock_available = row[0]
            if stock_available < quantity:
                conn.close()
                self._send_json({"error": "Insufficient stock"}, 409)
                return

            expires_at = (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()
            created_at = datetime.utcnow().isoformat()
            cursor.execute("""
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            """, (item_id, quantity, expires_at, created_at))
            cursor.execute("""
                UPDATE items SET stock_available = stock_available - ?
                WHERE id = ?
            """, (quantity, item_id))
            conn.commit()
            res_id = cursor.lastrowid

        conn.close()
        self._send_json({"id": res_id, "item_id": item_id, "quantity": quantity, "status": "pending", "expires_at": expires_at, "created_at": created_at}, 201)

    # ---- confirm ----
    def _handle_confirm_reservation(self, res_id):
        clean_expired_reservations()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()

        with lock:
            cursor.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, quantity = row
            if status != "pending":
                conn.close()
                self._send_json({"error": f"Reservation is {status}, cannot confirm"}, 400)
                return

            cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()

        conn.close()
        self._send_json({"message": "Reservation confirmed", "id": res_id, "status": "confirmed"})

    # ---- cancel ----
    def _handle_cancel_reservation(self, res_id):
        clean_expired_reservations()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()

        with lock:
            cursor.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, quantity = row
            if status == "confirmed":
                conn.close()
                self._send_json({"error": "Cannot cancel a confirmed reservation"}, 400)
                return
            if status == "expired":
                conn.close()
                self._send_json({"error": "Reservation already expired"}, 400)
                return

            cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            cursor.execute("""
                UPDATE items SET stock_available = stock_available + ?
                WHERE id = ?
            """, (quantity, item_id))
            conn.commit()

        conn.close()
        self._send_json({"message": "Reservation cancelled", "id": res_id, "status": "cancelled"})

    def log_message(self, format, *args):
        # Suppress default logging to stderr for cleaner output
        pass


def run_server(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == "__main__":
    run_server()
```
````
