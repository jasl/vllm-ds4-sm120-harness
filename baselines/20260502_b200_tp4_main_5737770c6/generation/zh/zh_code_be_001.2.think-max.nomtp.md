# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 14.852637
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2441, "completion_tokens": 2078, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2078
- Total tokens: 2441

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
import sqlite3
import json
import threading
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_PATH = "inventory.db"
_lock = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def cleanup_expired():
    with _lock:
        conn = get_db()
        c = conn.cursor()
        now = time.time()
        c.execute("""
            SELECT id, item_id, quantity FROM reservations
            WHERE status='pending' AND expires_at <= ?
        """, (now,))
        expired = c.fetchall()
        for res_id, item_id, qty in expired:
            c.execute("UPDATE reservations SET status='expired' WHERE id=? AND status='pending'", (res_id,))
            if c.rowcount > 0:
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id))
        conn.commit()
        conn.close()


class InventoryHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        return json.loads(body.decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self._handle_get_items()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_get_items(self):
        cleanup_expired()
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, name, stock_total, stock_available FROM items")
        rows = c.fetchall()
        conn.close()
        items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
        self._send_json(items)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        try:
            data = self._read_json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        if path == "/items":
            self._handle_create_item(data)
        elif path == "/reservations":
            self._handle_create_reservation(data)
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self._handle_confirm_reservation(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self._handle_cancel_reservation(res_id)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_create_item(self, data):
        name = data.get("name")
        stock_total = data.get("stock_total")
        if not name or not isinstance(name, str) or name.strip() == "":
            self._send_json({"error": "name required"}, 400)
            return
        if not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "stock_total must be a non-negative integer"}, 400)
            return
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                  (name.strip(), stock_total, stock_total))
        conn.commit()
        item_id = c.lastrowid
        conn.close()
        self._send_json({"id": item_id, "name": name.strip(), "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_create_reservation(self, data):
        cleanup_expired()
        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds", 300)

        if not isinstance(item_id, int) or item_id <= 0:
            self._send_json({"error": "item_id required"}, 400)
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_json({"error": "quantity must be a positive integer"}, 400)
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_json({"error": "ttl_seconds must be positive"}, 400)
            return

        with _lock:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
            row = c.fetchone()
            if row is None:
                conn.close()
                self._send_json({"error": "Item not found"}, 404)
                return
            available = row[0]
            if available < quantity:
                conn.close()
                self._send_json({"error": "Insufficient stock"}, 409)
                return

            now = time.time()
            res_id = str(uuid.uuid4())
            expires_at = now + ttl_seconds
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
            c.execute("""
                INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
            """, (res_id, item_id, quantity, expires_at, now))
            conn.commit()
            conn.close()

        self._send_json({
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": now
        }, 201)

    def _handle_confirm_reservation(self, res_id):
        with _lock:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id=?", (res_id,))
            row = c.fetchone()
            if row is None:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status = row[0]
            if status != "pending":
                conn.close()
                self._send_json({"error": f"Reservation already {status}"}, 400)
                return
            c.execute("UPDATE reservations SET status='confirmed' WHERE id=? AND status='pending'", (res_id,))
            conn.commit()
            conn.close()
        self._send_json({"message": "confirmed"})

    def _handle_cancel_reservation(self, res_id):
        with _lock:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id=?", (res_id,))
            row = c.fetchone()
            if row is None:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status = row[0]
            if status == "cancelled":
                conn.close()
                self._send_json({"error": "Already cancelled"}, 400)
                return
            if status == "confirmed":
                conn.close()
                self._send_json({"error": "Cannot cancel confirmed reservation"}, 400)
                return
            if status == "expired":
                conn.close()
                self._send_json({"error": "Already expired"}, 400)
                return

            item_id = row[1]
            quantity = row[2]
            c.execute("UPDATE reservations SET status='cancelled' WHERE id=? AND status='pending'", (res_id,))
            if c.rowcount > 0:
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
            conn.commit()
            conn.close()
        self._send_json({"message": "cancelled"})

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), InventoryHandler)
    print("Inventory service running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
```
````
