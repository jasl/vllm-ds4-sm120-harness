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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 6.820756
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2334, "completion_tokens": 1971, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1971
- Total tokens: 2334

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
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_PATH = "inventory.db"
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
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
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()

def clean_expired():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    expired = c.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
        (now,)
    ).fetchall()
    for rid, iid, qty in expired:
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, iid))
        c.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (rid,))
    conn.commit()
    conn.close()

class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _send_error(self, msg, status=400):
        self._send_json({"error": msg}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except:
            return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/items":
            self._handle_get_items()
        else:
            self._send_error("Not Found", 404)

    def do_POST(self):
        with LOCK:
            clean_expired()
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            if path == "/items":
                self._handle_post_items()
            elif path == "/reservations":
                self._handle_post_reservations()
            elif path.startswith("/reservations/") and path.endswith("/confirm"):
                rid = path.split("/")[2]
                self._handle_confirm(rid)
            elif path.startswith("/reservations/") and path.endswith("/cancel"):
                rid = path.split("/")[2]
                self._handle_cancel(rid)
            else:
                self._send_error("Not Found", 404)

    def _handle_get_items(self):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT id, name, stock_total, stock_available FROM items")
        items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in c.fetchall()]
        conn.close()
        self._send_json(items)

    def _handle_post_items(self):
        body = self._read_body()
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            self._send_error("Invalid name or stock_total")
            return
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name, stock_total, stock_total))
            conn.commit()
            item_id = c.lastrowid
            self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
        except sqlite3.IntegrityError:
            self._send_error("Item name already exists", 409)
        finally:
            conn.close()

    def _handle_post_reservations(self):
        body = self._read_body()
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds", 300)
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            self._send_error("Invalid item_id or quantity")
            return
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = c.fetchone()
            if not row:
                self._send_error("Item not found", 404)
                return
            available = row[0]
            if available < quantity:
                self._send_error("Insufficient stock", 409)
                return
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            created_at = now.isoformat()
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            c.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                      (item_id, quantity, expires_at, created_at))
            conn.commit()
            rid = c.lastrowid
            self._send_json({"id": rid, "item_id": item_id, "quantity": quantity, "status": "pending",
                             "expires_at": expires_at, "created_at": created_at}, 201)
        except Exception as e:
            conn.rollback()
            self._send_error(str(e), 500)
        finally:
            conn.close()

    def _handle_confirm(self, rid):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (rid,))
            row = c.fetchone()
            if not row:
                self._send_error("Reservation not found", 404)
                return
            status, item_id, qty = row
            if status != "pending":
                self._send_error(f"Reservation already {status}", 400)
                return
            c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (rid,))
            conn.commit()
            self._send_json({"message": "Confirmed"})
        finally:
            conn.close()

    def _handle_cancel(self, rid):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (rid,))
            row = c.fetchone()
            if not row:
                self._send_error("Reservation not found", 404)
                return
            status, item_id, qty = row
            if status != "pending":
                self._send_error(f"Reservation already {status}", 400)
                return
            c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (rid,))
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            conn.commit()
            self._send_json({"message": "Cancelled"})
        finally:
            conn.close()

    def log_message(self, format, *args):
        pass  # suppress default logging

if __name__ == "__main__":
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), APIHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
```
````
