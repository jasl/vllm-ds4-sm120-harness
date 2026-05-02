# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.094482
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2719, "completion_tokens": 2356, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2356
- Total tokens: 2719

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
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import time

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
    conn.close()


def cleanup_expired():
    """清理过期 pending 预约，释放库存"""
    with _lock:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        # 查询所有过期 pending 预约
        c.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
        expired = c.fetchall()
        for res_id, item_id, qty in expired:
            # 释放库存
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            # 标记为 cancelled
            c.execute("UPDATE reservations SET status='cancelled' WHERE id = ?", (res_id,))
        conn.commit()
        conn.close()


class APIHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw)

    def _parse_path(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        return path, parse_qs(parsed.query)

    def do_GET(self):
        cleanup_expired()
        path, _ = self._parse_path()
        if path == "/items":
            self._handle_list_items()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        cleanup_expired()
        path, _ = self._parse_path()
        body = self._read_body()
        if path == "/items":
            self._handle_create_item(body)
        elif path == "/reservations":
            self._handle_create_reservation(body)
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            parts = path.split("/")
            if len(parts) == 4:
                try:
                    res_id = int(parts[2])
                    self._handle_confirm_reservation(res_id)
                except ValueError:
                    self._send_json({"error": "Invalid reservation ID"}, 400)
            else:
                self._send_json({"error": "Not Found"}, 404)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4:
                try:
                    res_id = int(parts[2])
                    self._handle_cancel_reservation(res_id)
                except ValueError:
                    self._send_json({"error": "Invalid reservation ID"}, 400)
            else:
                self._send_json({"error": "Not Found"}, 404)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_list_items(self):
        with _lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = c.fetchall()
            items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
            conn.close()
        self._send_json(items)

    def _handle_create_item(self, body):
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or stock_total is None:
            self._send_json({"error": "name and stock_total are required"}, 400)
            return
        try:
            stock_total = int(stock_total)
        except (ValueError, TypeError):
            self._send_json({"error": "stock_total must be integer"}, 400)
            return
        if stock_total < 0:
            self._send_json({"error": "stock_total cannot be negative"}, 400)
            return
        with _lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name, stock_total, stock_total))
            conn.commit()
            new_id = c.lastrowid
            conn.close()
        self._send_json({"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_create_reservation(self, body):
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if item_id is None or quantity is None or ttl_seconds is None:
            self._send_json({"error": "item_id, quantity, and ttl_seconds are required"}, 400)
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (ValueError, TypeError):
            self._send_json({"error": "invalid parameters"}, 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self._send_json({"error": "quantity and ttl_seconds must be positive"}, 400)
            return
        now = datetime.utcnow()
        expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
        created_at = now.isoformat()
        with _lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            # Check stock
            c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Item not found"}, 404)
                return
            available = row[0]
            if available < quantity:
                conn.close()
                self._send_json({"error": "Insufficient stock", "available": available}, 409)
                return
            # Reserve
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            c.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                      (item_id, quantity, expires_at, created_at))
            conn.commit()
            new_id = c.lastrowid
            conn.close()
        self._send_json({
            "id": new_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        }, 201)

    def _handle_confirm_reservation(self, res_id):
        with _lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT status FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status = row[0]
            if status == "confirmed":
                conn.close()
                self._send_json({"error": "Already confirmed"}, 400)
                return
            if status == "cancelled":
                conn.close()
                self._send_json({"error": "Cannot confirm cancelled reservation"}, 400)
                return
            if status != "pending":
                conn.close()
                self._send_json({"error": "Invalid status"}, 400)
                return
            c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            conn.commit()
            conn.close()
        self._send_json({"message": "Confirmed"}, 200)

    def _handle_cancel_reservation(self, res_id):
        with _lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, quantity = row
            if status == "cancelled":
                conn.close()
                self._send_json({"error": "Already cancelled"}, 400)
                return
            if status == "confirmed":
                # Confirmed reservations cannot be cancelled (could be allowed but spec doesn't specify)
                conn.close()
                self._send_json({"error": "Cannot cancel confirmed reservation"}, 400)
                return
            # status == 'pending'
            c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (quantity, item_id))
            conn.commit()
            conn.close()
        self._send_json({"message": "Cancelled"}, 200)

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def run_server(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), APIHandler)
    print(f"Server running on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
```
````
