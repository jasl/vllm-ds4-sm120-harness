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
- Elapsed seconds: 6.934356
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2379, "completion_tokens": 2016, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2016
- Total tokens: 2379

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
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()


def cleanup_expired():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at < ?
    """, (now,))
    expired = cursor.fetchall()
    for res_id, item_id, qty in expired:
        cursor.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
        cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
    conn.commit()
    conn.close()


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length).decode("utf-8") if content_length else "{}"

    def _parse_path(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        return path

    def do_GET(self):
        path = self._parse_path()
        if path == "/items":
            self._handle_get_items()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        path = self._parse_path()
        if path == "/items":
            self._handle_create_item()
        elif path == "/reservations":
            self._handle_create_reservation()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            parts = path.split("/")
            if len(parts) == 4:
                rid = parts[2]
                self._handle_confirm_reservation(rid)
            else:
                self._send_json({"error": "Bad Request"}, 400)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4:
                rid = parts[2]
                self._handle_cancel_reservation(rid)
            else:
                self._send_json({"error": "Bad Request"}, 400)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_get_items(self):
        with lock:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
            items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in cursor.fetchall()]
            conn.close()
        self._send_json(items)

    def _handle_create_item(self):
        try:
            body = json.loads(self._read_body())
            name = body.get("name")
            stock_total = body.get("stock_total")
            if not name or stock_total is None:
                raise ValueError
            stock_total = int(stock_total)
            if stock_total < 0:
                raise ValueError
        except (ValueError, json.JSONDecodeError):
            self._send_json({"error": "Invalid request body"}, 400)
            return

        with lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                           (name, stock_total, stock_total))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
        self._send_json({"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_create_reservation(self):
        try:
            body = json.loads(self._read_body())
            item_id = int(body.get("item_id"))
            quantity = int(body.get("quantity"))
            ttl_seconds = int(body.get("ttl_seconds"))
            if quantity <= 0 or ttl_seconds <= 0:
                raise ValueError
        except (ValueError, json.JSONDecodeError):
            self._send_json({"error": "Invalid request body"}, 400)
            return

        with lock:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Item not found"}, 404)
                return
            available = row[0]
            if available < quantity:
                conn.close()
                self._send_json({"error": "Insufficient stock"}, 409)
                return

            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(seconds=ttl_seconds)
            cursor.execute("""
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            """, (item_id, quantity, expires_at.isoformat(), created_at.isoformat()))
            cursor.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            conn.commit()
            res_id = cursor.lastrowid
            conn.close()
        self._send_json({"id": res_id, "item_id": item_id, "quantity": quantity, "status": "pending",
                         "expires_at": expires_at.isoformat(), "created_at": created_at.isoformat()}, 201)

    def _handle_confirm_reservation(self, rid):
        with lock:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (rid,))
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
            cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (rid,))
            conn.commit()
            conn.close()
        self._send_json({"id": int(rid), "status": "confirmed"})

    def _handle_cancel_reservation(self, rid):
        with lock:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (rid,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, quantity = row
            if status != "pending":
                conn.close()
                self._send_json({"error": f"Reservation is {status}, cannot cancel"}, 400)
                return
            cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (rid,))
            cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (quantity, item_id))
            conn.commit()
            conn.close()
        self._send_json({"id": int(rid), "status": "cancelled"})


def run_server(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    init_db()
    run_server()
```
````
