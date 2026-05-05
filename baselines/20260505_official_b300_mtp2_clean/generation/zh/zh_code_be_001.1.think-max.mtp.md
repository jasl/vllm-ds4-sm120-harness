# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.068797
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2715, "completion_tokens": 2352, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2352
- Total tokens: 2715

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
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from contextlib import contextmanager

DB_PATH = "inventory.db"
_lock = threading.Lock()

def init_db():
    with get_conn() as conn:
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

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
    finally:
        conn.close()

def cleanup_expired():
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT r.id, r.item_id, r.quantity
            FROM reservations r
            WHERE r.status = 'pending' AND r.expires_at < ?
        """, (now,))
        expired = cur.fetchall()
        for row in expired:
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (row['id'],))
            conn.execute("""
                UPDATE items SET stock_available = stock_available + ?
                WHERE id = ?
            """, (row['quantity'], row['item_id']))
        conn.commit()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/items':
            self.handle_list_items()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        with _lock:
            cleanup_expired()

        if path == '/items':
            self.handle_create_item()
        elif path == '/reservations':
            self.handle_create_reservation()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations':
                try:
                    res_id = int(parts[2])
                    self.handle_confirm_reservation(res_id)
                except ValueError:
                    self.send_error(400, "Invalid reservation ID")
            else:
                self.send_error(404, "Not Found")
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations':
                try:
                    res_id = int(parts[2])
                    self.handle_cancel_reservation(res_id)
                except ValueError:
                    self.send_error(400, "Invalid reservation ID")
            else:
                self.send_error(404, "Not Found")
        else:
            self.send_error(404, "Not Found")

    def handle_list_items(self):
        with _lock:
            cleanup_expired()
            with get_conn() as conn:
                cur = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [dict(row) for row in cur.fetchall()]
        self.send_json(200, items)

    def handle_create_item(self):
        data = self.read_json()
        if not data:
            return self.send_error(400, "Invalid JSON")

        name = data.get('name')
        stock_total = data.get('stock_total')

        if not name or not isinstance(name, str):
            return self.send_error(400, "Missing or invalid 'name'")
        if stock_total is None or not isinstance(stock_total, int) or stock_total < 0:
            return self.send_error(400, "Missing or invalid 'stock_total'")

        with _lock:
            cleanup_expired()
            with get_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                item_id = cur.lastrowid
                cur = conn.execute("SELECT id, name, stock_total, stock_available FROM items WHERE id=?", (item_id,))
                item = dict(cur.fetchone())
        self.send_json(201, item)

    def handle_create_reservation(self):
        data = self.read_json()
        if not data:
            return self.send_error(400, "Invalid JSON")

        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds', 300)

        if not isinstance(item_id, int):
            return self.send_error(400, "Missing or invalid 'item_id'")
        if not isinstance(quantity, int) or quantity <= 0:
            return self.send_error(400, "Missing or invalid 'quantity'")
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            return self.send_error(400, "Invalid 'ttl_seconds'")

        with _lock:
            cleanup_expired()
            with get_conn() as conn:
                conn.execute("BEGIN IMMEDIATE")
                cur = conn.execute(
                    "SELECT stock_available FROM items WHERE id=? FOR UPDATE",
                    (item_id,)
                )
                item = cur.fetchone()
                if not item:
                    conn.rollback()
                    return self.send_error(404, "Item not found")

                if item['stock_available'] < quantity:
                    conn.rollback()
                    return self.send_error(409, "Insufficient stock")

                now = datetime.utcnow()
                expires_at = now + timedelta(seconds=ttl_seconds)

                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id=?",
                    (quantity, item_id)
                )
                cur = conn.execute(
                    "INSERT INTO reservations (item_id, quantity, expires_at, created_at) VALUES (?, ?, ?, ?)",
                    (item_id, quantity, expires_at.isoformat(), now.isoformat())
                )
                conn.commit()
                res_id = cur.lastrowid
                cur = conn.execute(
                    "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id=?",
                    (res_id,)
                )
                reservation = dict(cur.fetchone())
        self.send_json(201, reservation)

    def handle_confirm_reservation(self, res_id):
        with _lock:
            cleanup_expired()
            with get_conn() as conn:
                conn.execute("BEGIN IMMEDIATE")
                cur = conn.execute(
                    "SELECT id, status FROM reservations WHERE id=? FOR UPDATE",
                    (res_id,)
                )
                row = cur.fetchone()
                if not row:
                    conn.rollback()
                    return self.send_error(404, "Reservation not found")

                if row['status'] != 'pending':
                    conn.rollback()
                    return self.send_error(400, f"Reservation already {row['status']}")

                conn.execute(
                    "UPDATE reservations SET status='confirmed' WHERE id=?",
                    (res_id,)
                )
                conn.commit()
                cur = conn.execute(
                    "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id=?",
                    (res_id,)
                )
                reservation = dict(cur.fetchone())
        self.send_json(200, reservation)

    def handle_cancel_reservation(self, res_id):
        with _lock:
            cleanup_expired()
            with get_conn() as conn:
                conn.execute("BEGIN IMMEDIATE")
                cur = conn.execute(
                    "SELECT id, item_id, quantity, status FROM reservations WHERE id=? FOR UPDATE",
                    (res_id,)
                )
                row = cur.fetchone()
                if not row:
                    conn.rollback()
                    return self.send_error(404, "Reservation not found")

                if row['status'] not in ('pending', 'confirmed'):
                    conn.rollback()
                    return self.send_error(400, f"Cannot cancel reservation with status '{row['status']}'")

                conn.execute(
                    "UPDATE reservations SET status='cancelled' WHERE id=?",
                    (res_id,)
                )
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                    (row['quantity'], row['item_id'])
                )
                conn.commit()
                cur = conn.execute(
                    "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id=?",
                    (res_id,)
                )
                reservation = dict(cur.fetchone())
        self.send_json(200, reservation)

    def read_json(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                return None
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            return None

    def send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def send_error(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        pass  # Suppress default logging

def run_server(host='127.0.0.1', port=8080):
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    run_server()
```
````
