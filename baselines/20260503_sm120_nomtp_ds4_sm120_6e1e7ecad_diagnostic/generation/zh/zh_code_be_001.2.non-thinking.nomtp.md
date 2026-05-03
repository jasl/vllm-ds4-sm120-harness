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
- Elapsed seconds: 37.093361
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2726, "completion_tokens": 2363, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2363
- Total tokens: 2726

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
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

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
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def cleanup_expired(conn):
    now = time.time()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at <= ?
    """, (now,))
    expired = cur.fetchall()
    for r_id, i_id, qty in expired:
        cur.execute("UPDATE reservations SET status = 'expired' WHERE id = ? AND status = 'pending'", (r_id,))
        if cur.rowcount > 0:
            cur.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, i_id))
    conn.commit()

class InventoryHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self._handle_get_items()
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
            parts = path.split("/")
            if len(parts) == 4 and parts[2].isdigit():
                self._handle_confirm(int(parts[2]))
            else:
                self._send_json({"error": "Bad Request"}, 400)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4 and parts[2].isdigit():
                self._handle_cancel(int(parts[2]))
            else:
                self._send_json({"error": "Bad Request"}, 400)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_get_items(self):
        with _lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                cur = conn.cursor()
                cur.execute("SELECT id, name, stock_total, stock_available FROM items")
                rows = cur.fetchall()
                items = [
                    {"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]}
                    for r in rows
                ]
                self._send_json(items)
            finally:
                conn.close()

    def _handle_post_items(self):
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "Invalid parameters: need 'name' (str) and 'stock_total' (int >=0)"}, 400)
            return
        with _lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                cur = conn.cursor()
                cur.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                            (name, stock_total, stock_total))
                conn.commit()
                item_id = cur.lastrowid
                self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
            finally:
                conn.close()

    def _handle_post_reservations(self):
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if not isinstance(item_id, int) or not isinstance(quantity, int) or not isinstance(ttl_seconds, (int, float)):
            self._send_json({"error": "Invalid parameters: need 'item_id' (int), 'quantity' (int), 'ttl_seconds' (int/float)"}, 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self._send_json({"error": "quantity and ttl_seconds must be positive"}, 400)
            return
        with _lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                cur = conn.cursor()
                cur.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
                row = cur.fetchone()
                if not row:
                    self._send_json({"error": "Item not found"}, 404)
                    return
                available = row[0]
                if available < quantity:
                    self._send_json({"error": "Insufficient stock"}, 409)
                    return
                now = time.time()
                expires_at = now + ttl_seconds
                cur.execute("""
                    INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                    VALUES (?, ?, 'pending', ?, ?)
                """, (item_id, quantity, expires_at, now))
                cur.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
                conn.commit()
                res_id = cur.lastrowid
                self._send_json({
                    "id": res_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": now
                }, 201)
            finally:
                conn.close()

    def _handle_confirm(self, res_id):
        with _lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                cur = conn.cursor()
                cur.execute("SELECT status FROM reservations WHERE id = ?", (res_id,))
                row = cur.fetchone()
                if not row:
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                status = row[0]
                if status != "pending":
                    self._send_json({"error": f"Reservation status is '{status}', cannot confirm"}, 409)
                    return
                cur.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ? AND status = 'pending'", (res_id,))
                if cur.rowcount == 0:
                    self._send_json({"error": "Reservation expired or already processed"}, 409)
                    return
                conn.commit()
                cur.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = ?", (res_id,))
                r = cur.fetchone()
                self._send_json({
                    "id": r[0], "item_id": r[1], "quantity": r[2],
                    "status": r[3], "expires_at": r[4], "created_at": r[5]
                })
            finally:
                conn.close()

    def _handle_cancel(self, res_id):
        with _lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                cur = conn.cursor()
                cur.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
                row = cur.fetchone()
                if not row:
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                status, item_id, quantity = row
                if status != "pending":
                    self._send_json({"error": f"Reservation status is '{status}', cannot cancel"}, 409)
                    return
                cur.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ? AND status = 'pending'", (res_id,))
                if cur.rowcount == 0:
                    self._send_json({"error": "Reservation already processed"}, 409)
                    return
                cur.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (quantity, item_id))
                conn.commit()
                cur.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = ?", (res_id,))
                r = cur.fetchone()
                self._send_json({
                    "id": r[0], "item_id": r[1], "quantity": r[2],
                    "status": r[3], "expires_at": r[4], "created_at": r[5]
                })
            finally:
                conn.close()

    def log_message(self, format, *args):
        pass  # Suppress logs for cleaner output

def run(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    init_db()
    run()
```
````
