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
- Elapsed seconds: 7.719968
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2596, "completion_tokens": 2233, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2233
- Total tokens: 2596

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
#!/usr/bin/env python3
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
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
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

def cleanup_expired():
    """清理已过期的pending预约并释放库存"""
    with LOCK:
        with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
            now = datetime.utcnow().isoformat()
            expired = conn.execute(
                "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
                (now,)
            ).fetchall()
            for res_id, item_id, qty in expired:
                conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id))
            conn.commit()

class APIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, msg, status=400):
        self._send_json({"error": msg}, status)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        return json.loads(body.decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self.handle_list_items()
        else:
            self._send_error("Not found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self.handle_create_item()
        elif path == "/reservations":
            self.handle_create_reservation()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self.handle_confirm_reservation(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self.handle_cancel_reservation(res_id)
        else:
            self._send_error("Not found", 404)

    def handle_list_items(self):
        cleanup_expired()
        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                rows = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
                items = [
                    {"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]}
                    for r in rows
                ]
        self._send_json(items)

    def handle_create_item(self):
        try:
            data = self._read_json_body()
        except Exception:
            return self._send_error("Invalid JSON", 400)

        name = data.get("name")
        stock_total = data.get("stock_total")
        if not name or not isinstance(name, str) or not stock_total or not isinstance(stock_total, int):
            return self._send_error("Missing or invalid fields: name (str), stock_total (int)", 400)
        if stock_total < 0:
            return self._send_error("stock_total must be non-negative", 400)

        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                cur = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                                   (name, stock_total, stock_total))
                item_id = cur.lastrowid
                conn.commit()
                item = {
                    "id": item_id,
                    "name": name,
                    "stock_total": stock_total,
                    "stock_available": stock_total
                }
        self._send_json(item, 201)

    def handle_create_reservation(self):
        cleanup_expired()
        try:
            data = self._read_json_body()
        except Exception:
            return self._send_error("Invalid JSON", 400)

        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds")

        if not all([isinstance(item_id, int), isinstance(quantity, int), isinstance(ttl_seconds, int)]):
            return self._send_error("Missing or invalid fields: item_id (int), quantity (int), ttl_seconds (int)", 400)
        if quantity <= 0 or ttl_seconds <= 0:
            return self._send_error("quantity and ttl_seconds must be positive", 400)

        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                # Check item exists and has enough stock
                item = conn.execute("SELECT id, stock_available FROM items WHERE id=?", (item_id,)).fetchone()
                if not item:
                    return self._send_error("Item not found", 404)
                if item[1] < quantity:
                    return self._send_error("Insufficient stock", 409)

                # Create reservation
                res_id = str(uuid.uuid4())
                now = datetime.utcnow()
                created_at = now.isoformat()
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()

                conn.execute(
                    "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                    (res_id, item_id, quantity, expires_at, created_at)
                )
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?",
                             (quantity, item_id))
                conn.commit()

                reservation = {
                    "id": res_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": created_at
                }
        self._send_json(reservation, 201)

    def handle_confirm_reservation(self, res_id):
        cleanup_expired()
        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                res = conn.execute(
                    "SELECT id, status FROM reservations WHERE id=?", (res_id,)
                ).fetchone()
                if not res:
                    return self._send_error("Reservation not found", 404)
                if res[1] != "pending":
                    return self._send_error(f"Cannot confirm reservation with status '{res[1]}'", 400)

                conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
                conn.commit()

                updated = conn.execute(
                    "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id=?",
                    (res_id,)
                ).fetchone()
                reservation = {
                    "id": updated[0],
                    "item_id": updated[1],
                    "quantity": updated[2],
                    "status": updated[3],
                    "expires_at": updated[4],
                    "created_at": updated[5]
                }
        self._send_json(reservation)

    def handle_cancel_reservation(self, res_id):
        cleanup_expired()
        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                res = conn.execute(
                    "SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,)
                ).fetchone()
                if not res:
                    return self._send_error("Reservation not found", 404)
                if res[3] != "pending":
                    return self._send_error(f"Cannot cancel reservation with status '{res[3]}'", 400)

                # Release stock
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                             (res[2], res[1]))
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                conn.commit()

                updated = conn.execute(
                    "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id=?",
                    (res_id,)
                ).fetchone()
                reservation = {
                    "id": updated[0],
                    "item_id": updated[1],
                    "quantity": updated[2],
                    "status": updated[3],
                    "expires_at": updated[4],
                    "created_at": updated[5]
                }
        self._send_json(reservation)

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), APIHandler)
    print(f"Server started at http://{host}:{port}")
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
