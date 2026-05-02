# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 13.882979
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2311, "completion_tokens": 1948, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1948
- Total tokens: 2311

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
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_FILE = "inventory.db"
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_FILE)
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
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status='pending' AND expires_at <= ?
    """, (now,))
    expired = c.fetchall()
    for res_id, item_id, qty in expired:
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id))
        c.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
    conn.commit()
    conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length).decode() if content_length else ""

    def _parse_json(self):
        try:
            return json.loads(self._read_body())
        except:
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            with LOCK:
                cleanup_expired()
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("SELECT id, name, stock_total, stock_available FROM items")
                rows = c.fetchall()
                items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
                conn.close()
            self._send_json(items)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self._handle_post_items()
        elif path == "/reservations":
            self._handle_post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = int(path.split("/")[2])
            self._handle_confirm(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = int(path.split("/")[2])
            self._handle_cancel(res_id)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_post_items(self):
        data = self._parse_json()
        if not data or "name" not in data or "stock_total" not in data:
            self._send_json({"error": "Missing required fields"}, 400)
            return
        try:
            stock_total = int(data["stock_total"])
            if stock_total < 0:
                raise ValueError
        except:
            self._send_json({"error": "Invalid stock_total"}, 400)
            return
        name = data["name"].strip()
        if not name:
            self._send_json({"error": "Name cannot be empty"}, 400)
            return
        with LOCK:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name, stock_total, stock_total))
            conn.commit()
            new_id = c.lastrowid
            conn.close()
        self._send_json({"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_post_reservations(self):
        data = self._parse_json()
        if not data or "item_id" not in data or "quantity" not in data or "ttl_seconds" not in data:
            self._send_json({"error": "Missing required fields"}, 400)
            return
        try:
            item_id = int(data["item_id"])
            quantity = int(data["quantity"])
            ttl = int(data["ttl_seconds"])
            if item_id < 0 or quantity <= 0 or ttl <= 0:
                raise ValueError
        except:
            self._send_json({"error": "Invalid parameters"}, 400)
            return
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Item not found"}, 404)
                return
            if row[0] < quantity:
                conn.close()
                self._send_json({"error": "Insufficient stock"}, 409)
                return
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl)).isoformat()
            created_at = now.isoformat()
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
            c.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                      (item_id, quantity, expires_at, created_at))
            conn.commit()
            res_id = c.lastrowid
            conn.close()
        self._send_json({"id": res_id, "item_id": item_id, "quantity": quantity, "status": "pending", "expires_at": expires_at, "created_at": created_at}, 201)

    def _handle_confirm(self, res_id):
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT status, item_id FROM reservations WHERE id=?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            if row[0] != "pending":
                conn.close()
                self._send_json({"error": "Reservation already processed"}, 409)
                return
            c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            conn.commit()
            conn.close()
        self._send_json({"message": "Confirmed"})

    def _handle_cancel(self, res_id):
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id=?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            if row[0] != "pending":
                conn.close()
                self._send_json({"error": "Reservation already processed"}, 409)
                return
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (row[2], row[1]))
            c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
            conn.commit()
            conn.close()
        self._send_json({"message": "Cancelled"})

def run_server():
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), RequestHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == "__main__":
    run_server()
```
````
