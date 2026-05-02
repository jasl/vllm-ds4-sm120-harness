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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 14.81502
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2435, "completion_tokens": 2072, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2072
- Total tokens: 2435

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
from contextlib import closing

DB_PATH = "inventory.db"
LOCK = threading.Lock()

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
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
    with closing(sqlite3.connect(DB_PATH)) as conn:
        now = datetime.utcnow().isoformat()
        expired = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
            (now,)
        ).fetchall()
        for res_id, item_id, qty in expired:
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id))
        conn.commit()

class InventoryHandler(BaseHTTPRequestHandler):
    def _json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode())))
        self.end_headers()
        self.wfile.write(body.encode())

    def _error(self, msg, status=400):
        self._json_response({"error": msg}, status)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        data = self.rfile.read(length)
        return json.loads(data.decode())

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/items":
            with LOCK:
                cleanup_expired()
                with closing(sqlite3.connect(DB_PATH)) as conn:
                    rows = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
                    items = [
                        {"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]}
                        for r in rows
                    ]
                self._json_response(items)
        else:
            self._error("Not Found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/items":
            data = self._read_json()
            if not data or "name" not in data or "stock_total" not in data:
                self._error("Missing name or stock_total", 400)
                return
            name = data["name"]
            try:
                total = int(data["stock_total"])
            except (ValueError, TypeError):
                self._error("stock_total must be integer", 400)
                return
            if total < 0:
                self._error("stock_total cannot be negative", 400)
                return
            with LOCK:
                cleanup_expired()
                with closing(sqlite3.connect(DB_PATH)) as conn:
                    conn.execute(
                        "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                        (name, total, total)
                    )
                    conn.commit()
                    item_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                self._json_response({"id": item_id, "name": name, "stock_total": total, "stock_available": total}, 201)

        elif path == "/reservations":
            data = self._read_json()
            if not data or "item_id" not in data or "quantity" not in data or "ttl_seconds" not in data:
                self._error("Missing item_id, quantity or ttl_seconds", 400)
                return
            try:
                item_id = int(data["item_id"])
                qty = int(data["quantity"])
                ttl = int(data["ttl_seconds"])
            except (ValueError, TypeError):
                self._error("item_id, quantity, ttl_seconds must be integers", 400)
                return
            if qty <= 0:
                self._error("quantity must be positive", 400)
                return
            if ttl <= 0:
                self._error("ttl_seconds must be positive", 400)
                return

            with LOCK:
                cleanup_expired()
                with closing(sqlite3.connect(DB_PATH)) as conn:
                    conn.execute("BEGIN IMMEDIATE")
                    try:
                        item = conn.execute(
                            "SELECT id, stock_available FROM items WHERE id=?",
                            (item_id,)
                        ).fetchone()
                        if not item:
                            conn.execute("ROLLBACK")
                            self._error("Item not found", 404)
                            return
                        if item[1] < qty:
                            conn.execute("ROLLBACK")
                            self._error("Insufficient stock", 409)
                            return
                        res_id = str(uuid.uuid4())
                        created = datetime.utcnow()
                        expires = created + timedelta(seconds=ttl)
                        conn.execute(
                            "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                            (res_id, item_id, qty, expires.isoformat(), created.isoformat())
                        )
                        conn.execute(
                            "UPDATE items SET stock_available = stock_available - ? WHERE id=?",
                            (qty, item_id)
                        )
                        conn.execute("COMMIT")
                    except Exception as e:
                        conn.execute("ROLLBACK")
                        self._error(str(e), 500)
                        return
                self._json_response({
                    "id": res_id,
                    "item_id": item_id,
                    "quantity": qty,
                    "status": "pending",
                    "expires_at": expires.isoformat(),
                    "created_at": created.isoformat()
                }, 201)

        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path[len("/reservations/"):-len("/confirm")]
            with LOCK:
                cleanup_expired()
                with closing(sqlite3.connect(DB_PATH)) as conn:
                    conn.execute("BEGIN IMMEDIATE")
                    try:
                        res = conn.execute(
                            "SELECT id, status FROM reservations WHERE id=?", (res_id,)
                        ).fetchone()
                        if not res:
                            conn.execute("ROLLBACK")
                            self._error("Reservation not found", 404)
                            return
                        if res[1] != "pending":
                            conn.execute("ROLLBACK")
                            self._error("Reservation is not pending", 400)
                            return
                        conn.execute(
                            "UPDATE reservations SET status='confirmed' WHERE id=?",
                            (res_id,)
                        )
                        conn.execute("COMMIT")
                    except Exception as e:
                        conn.execute("ROLLBACK")
                        self._error(str(e), 500)
                        return
                self._json_response({"status": "confirmed"})

        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path[len("/reservations/"):-len("/cancel")]
            with LOCK:
                cleanup_expired()
                with closing(sqlite3.connect(DB_PATH)) as conn:
                    conn.execute("BEGIN IMMEDIATE")
                    try:
                        res = conn.execute(
                            "SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,)
                        ).fetchone()
                        if not res:
                            conn.execute("ROLLBACK")
                            self._error("Reservation not found", 404)
                            return
                        if res[3] != "pending":
                            conn.execute("ROLLBACK")
                            self._error("Reservation is not pending", 400)
                            return
                        item_id = res[1]
                        qty = res[2]
                        conn.execute(
                            "UPDATE reservations SET status='cancelled' WHERE id=?",
                            (res_id,)
                        )
                        conn.execute(
                            "UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                            (qty, item_id)
                        )
                        conn.execute("COMMIT")
                    except Exception as e:
                        conn.execute("ROLLBACK")
                        self._error(str(e), 500)
                        return
                self._json_response({"status": "cancelled"})

        else:
            self._error("Not Found", 404)

    def log_message(self, format, *args):
        pass

def run_server(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()

if __name__ == "__main__":
    init_db()
    run_server()
```
````
