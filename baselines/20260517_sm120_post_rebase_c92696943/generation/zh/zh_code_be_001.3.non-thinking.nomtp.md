# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `default`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 22.263179
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2571, "completion_tokens": 2208, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2208
- Total tokens: 2571

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
from urllib.parse import urlparse
from datetime import datetime, timedelta
import time


DB_PATH = "inventory.db"
LOCK = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("""
        SELECT r.id, r.item_id, r.quantity
        FROM reservations r
        WHERE r.status = 'pending' AND r.expires_at < ?
    """, (now,))
    expired = c.fetchall()
    for row in expired:
        rid, item_id, qty = row
        c.execute("UPDATE reservations SET status = 'expired' WHERE id = ? AND status = 'pending'", (rid,))
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
    conn.commit()
    conn.close()


class InventoryAPIHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/items':
            self.handle_list_items()
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/items':
            self.handle_create_item()
        elif path == '/reservations':
            self.handle_create_reservation()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            parts = path.split('/')
            if len(parts) == 4:
                try:
                    rid = int(parts[2])
                    self.handle_confirm_reservation(rid)
                except ValueError:
                    self.send_error(400, "Invalid reservation ID")
            else:
                self.send_error(404, "Not found")
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4:
                try:
                    rid = int(parts[2])
                    self.handle_cancel_reservation(rid)
                except ValueError:
                    self.send_error(400, "Invalid reservation ID")
            else:
                self.send_error(404, "Not found")
        else:
            self.send_error(404, "Not found")

    def handle_list_items(self):
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = c.fetchall()
            conn.close()
        items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
        self.send_json(200, items)

    def handle_create_item(self):
        try:
            body = self.read_json()
            name = body.get("name")
            stock_total = body.get("stock_total")
            if not name or not isinstance(stock_total, int) or stock_total < 0:
                raise ValueError
        except Exception:
            self.send_error(400, "Invalid request body, need 'name' (string) and 'stock_total' (non-negative integer)")
            return

        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name, stock_total, stock_total))
            conn.commit()
            new_id = c.lastrowid
            conn.close()
        self.send_json(201, {"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total})

    def handle_create_reservation(self):
        try:
            body = self.read_json()
            item_id = body.get("item_id")
            quantity = body.get("quantity")
            ttl_seconds = body.get("ttl_seconds", 300)
            if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
                raise ValueError
            if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
                ttl_seconds = 300
        except Exception:
            self.send_error(400, "Invalid request body, need 'item_id' (int), 'quantity' (positive int), optional 'ttl_seconds' (int)")
            return

        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
            item = c.fetchone()
            if not item:
                conn.close()
                self.send_error(404, "Item not found")
                return
            item_db_id, available = item
            if available < quantity:
                conn.close()
                self.send_error(409, "Insufficient stock")
                return

            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            created_at = now.isoformat()
            c.execute("""
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            """, (item_id, quantity, expires_at, created_at))
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            conn.commit()
            new_id = c.lastrowid
            conn.close()
        self.send_json(201, {
            "id": new_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        })

    def handle_confirm_reservation(self, rid):
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id = ?", (rid,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.send_error(404, "Reservation not found")
                return
            rid_db, status, item_id, qty = row
            if status != "pending":
                conn.close()
                self.send_error(400, f"Reservation already {status}")
                return
            c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (rid,))
            conn.commit()
            c.execute("SELECT id, name, stock_total, stock_available FROM items WHERE id = ?", (item_id,))
            item = c.fetchone()
            conn.close()
        self.send_json(200, {
            "id": rid,
            "item_id": item_id,
            "quantity": qty,
            "status": "confirmed"
        })

    def handle_cancel_reservation(self, rid):
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id = ?", (rid,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.send_error(404, "Reservation not found")
                return
            rid_db, status, item_id, qty = row
            if status != "pending":
                conn.close()
                self.send_error(400, f"Reservation already {status}")
                return
            c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (rid,))
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            conn.commit()
            conn.close()
        self.send_json(200, {
            "id": rid,
            "item_id": item_id,
            "quantity": qty,
            "status": "cancelled"
        })

    def read_json(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            raise ValueError("Empty body")
        data = self.rfile.read(content_length)
        return json.loads(data.decode('utf-8'))

    def send_json(self, status_code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error(self, status_code, message):
        self.send_json(status_code, {"error": message})

    def log_message(self, format, *args):
        # Suppress default logging to stderr
        pass


def run_server(host='127.0.0.1', port=8080):
    init_db()
    server = HTTPServer((host, port), InventoryAPIHandler)
    print(f"Starting server on {host}:{port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == "__main__":
    run_server()
```
````
