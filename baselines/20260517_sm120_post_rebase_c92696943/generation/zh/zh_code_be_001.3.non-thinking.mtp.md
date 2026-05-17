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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 11.941457
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2634, "completion_tokens": 2271, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2271
- Total tokens: 2634

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
db_lock = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def cleanup_expired():
    """清理并释放过期的 pending 预约"""
    now = datetime.utcnow().isoformat()
    with db_lock:
        conn = get_db()
        c = conn.cursor()
        # 找出过期预约
        c.execute("""
            SELECT id, item_id, quantity FROM reservations
            WHERE status='pending' AND expires_at < ?
        """, (now,))
        expired = c.fetchall()
        for res_id, item_id, qty in expired:
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id))
            c.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
        conn.commit()
        conn.close()


class InventoryHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self.handle_get_items()
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        cleanup_expired()  # 每次请求前清理
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self.handle_post_items()
        elif path == "/reservations":
            self.handle_post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            parts = path.split("/")
            if len(parts) == 4:
                res_id = parts[2]
                self.handle_confirm(res_id)
            else:
                self._send_json({"error": "Bad request"}, 400)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4:
                res_id = parts[2]
                self.handle_cancel(res_id)
            else:
                self._send_json({"error": "Bad request"}, 400)
        else:
            self._send_json({"error": "Not found"}, 404)

    def handle_get_items(self):
        with db_lock:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = c.fetchall()
            conn.close()
        items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
        self._send_json(items)

    def handle_post_items(self):
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(name, str):
            self._send_json({"error": "name is required and must be string"}, 400)
            return
        if stock_total is None or not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "stock_total must be non-negative integer"}, 400)
            return
        item_id = str(uuid.uuid4())
        with db_lock:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO items (id, name, stock_total, stock_available) VALUES (?, ?, ?, ?)",
                      (item_id, name, stock_total, stock_total))
            conn.commit()
            conn.close()
        self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def handle_post_reservations(self):
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds", 300)

        if not item_id or not isinstance(item_id, str):
            self._send_json({"error": "item_id is required and must be string"}, 400)
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_json({"error": "quantity must be positive integer"}, 400)
            return
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            self._send_json({"error": "ttl_seconds must be positive integer"}, 400)
            return

        with db_lock:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Item not found"}, 404)
                return
            available = row[0]
            if available < quantity:
                conn.close()
                self._send_json({"error": "Insufficient stock", "available": available, "requested": quantity}, 409)
                return

            # 扣减库存
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))

            res_id = str(uuid.uuid4())
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            created_at = now.isoformat()
            c.execute("""
                INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
            """, (res_id, item_id, quantity, expires_at, created_at))
            conn.commit()
            conn.close()

        self._send_json({
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        }, 201)

    def handle_confirm(self, res_id):
        with db_lock:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id=?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            if row[1] != "pending":
                conn.close()
                self._send_json({"error": f"Cannot confirm reservation with status '{row[1]}'"}, 400)
                return

            c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            conn.commit()
            conn.close()
        self._send_json({"id": res_id, "status": "confirmed"})

    def handle_cancel(self, res_id):
        with db_lock:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id=?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            if row[1] != "pending":
                conn.close()
                self._send_json({"error": f"Cannot cancel reservation with status '{row[1]}'"}, 400)
                return

            # 释放库存
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (row[3], row[2]))
            c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
            conn.commit()
            conn.close()
        self._send_json({"id": res_id, "status": "cancelled"})

    def log_message(self, format, *args):
        # 静默日志避免干扰
        pass


def run(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("Server stopped.")


if __name__ == "__main__":
    run()
```
````
