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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 15.036283
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2471, "completion_tokens": 2108, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2108
- Total tokens: 2471

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
LOCK = threading.Lock()

def init_db():
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(item_id) REFERENCES items(id)
            )
        """)
        conn.commit()

def clean_expired_reservations():
    now = datetime.utcnow().isoformat()
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        conn.execute("BEGIN")
        expired = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
            (now,)
        ).fetchall()
        for res_id, item_id, qty in expired:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            conn.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
        conn.commit()

class InventoryHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        return json.loads(self.rfile.read(length))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/items":
            with LOCK:
                clean_expired_reservations()
                with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                    items = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
                    result = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in items]
                    self._send_json(result)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/items":
            self._handle_post_item()
        elif path == "/reservations":
            self._handle_post_reservation()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self._handle_confirm(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self._handle_cancel(res_id)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_post_item(self):
        body = self._read_body()
        if not body or "name" not in body or "stock_total" not in body:
            self._send_json({"error": "name and stock_total required"}, 400)
            return
        name = body["name"]
        try:
            stock_total = int(body["stock_total"])
        except (ValueError, TypeError):
            self._send_json({"error": "stock_total must be integer"}, 400)
            return
        if stock_total < 0:
            self._send_json({"error": "stock_total must be non-negative"}, 400)
            return
        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                try:
                    conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                                 (name, stock_total, stock_total))
                    conn.commit()
                    item_id = conn.execute("SELECT id FROM items WHERE name=?", (name,)).fetchone()[0]
                    self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
                except sqlite3.IntegrityError:
                    self._send_json({"error": "Item already exists"}, 409)

    def _handle_post_reservation(self):
        body = self._read_body()
        if not body or "item_id" not in body or "quantity" not in body or "ttl_seconds" not in body:
            self._send_json({"error": "item_id, quantity and ttl_seconds required"}, 400)
            return
        try:
            item_id = int(body["item_id"])
            quantity = int(body["quantity"])
            ttl_seconds = int(body["ttl_seconds"])
        except (ValueError, TypeError):
            self._send_json({"error": "item_id, quantity, ttl_seconds must be integers"}, 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self._send_json({"error": "quantity and ttl_seconds must be positive"}, 400)
            return

        with LOCK:
            clean_expired_reservations()
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                conn.execute("BEGIN")
                item = conn.execute("SELECT id, stock_available FROM items WHERE id=?", (item_id,)).fetchone()
                if not item:
                    conn.rollback()
                    self._send_json({"error": "Item not found"}, 404)
                    return
                if item[1] < quantity:
                    conn.rollback()
                    self._send_json({"error": "Insufficient stock", "available": item[1]}, 409)
                    return
                res_id = str(uuid.uuid4())
                created_at = datetime.utcnow().isoformat()
                expires_at = (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
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

    def _handle_confirm(self, res_id):
        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                clean_expired_reservations()
                conn.execute("BEGIN")
                res = conn.execute("SELECT id, status FROM reservations WHERE id=?", (res_id,)).fetchone()
                if not res:
                    conn.rollback()
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                if res[1] != "pending":
                    conn.rollback()
                    self._send_json({"error": f"Reservation already {res[1]}"}, 400)
                    return
                conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
                conn.commit()
                self._send_json({"message": "confirmed", "id": res_id})

    def _handle_cancel(self, res_id):
        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                clean_expired_reservations()
                conn.execute("BEGIN")
                res = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,)).fetchone()
                if not res:
                    conn.rollback()
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                if res[3] != "pending":
                    conn.rollback()
                    self._send_json({"error": f"Reservation already {res[3]}"}, 400)
                    return
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (res[2], res[1]))
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                conn.commit()
                self._send_json({"message": "cancelled", "id": res_id})

def run_server(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == "__main__":
    run_server()
```
````
