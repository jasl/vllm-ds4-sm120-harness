# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.787477
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 3136, "completion_tokens": 2773, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2773
- Total tokens: 3136

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
"""
server.py - Small inventory reservation HTTP API service.
Uses only Python 3 standard library (http.server, sqlite3, json, threading, etc.)
"""

import json
import sqlite3
import threading
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Database file
DB_FILE = "inventory.db"

# Thread lock for concurrency
db_lock = threading.Lock()

# ---------- Database initialization ----------

def init_db():
    """Create tables if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)
        conn.commit()

# ---------- Helper functions ----------

def clean_expired_pending(conn):
    """
    Clean expired pending reservations and release stock.
    Must be called within a transaction.
    """
    cursor = conn.cursor()
    now = time.time()
    # Find expired pending reservations
    cursor.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at <= ?
    """, (now,))
    expired = cursor.fetchall()
    for res_id, item_id, quantity in expired:
        # Release stock
        cursor.execute("""
            UPDATE items SET stock_available = stock_available + ?
            WHERE id = ?
        """, (quantity, item_id))
        # Update reservation status to 'expired'
        cursor.execute("""
            UPDATE reservations SET status = 'expired'
            WHERE id = ?
        """, (res_id,))
    conn.commit()

def get_json_body(handler):
    """Read and parse JSON request body."""
    content_length = int(handler.headers.get('Content-Length', 0))
    if content_length == 0:
        return None
    body = handler.rfile.read(content_length)
    try:
        return json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

def send_json(handler, data, status=200):
    """Send JSON response."""
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def send_error(handler, message, status=400):
    """Send error JSON response."""
    send_json(handler, {"error": message}, status)

# ---------- Request Handler ----------

class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for inventory reservation API."""

    def log_message(self, format, *args):
        """Suppress default logging."""

    def _handle_request(self):
        """Route and handle request."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path.rstrip('/')
        method = self.command

        # Pre-clean expired reservations for every request
        with db_lock:
            with sqlite3.connect(DB_FILE) as conn:
                clean_expired_pending(conn)

        # Route: GET /items
        if method == 'GET' and path == '/items':
            self._get_items()
        # Route: POST /items
        elif method == 'POST' and path == '/items':
            self._post_items()
        # Route: POST /reservations
        elif method == 'POST' and path == '/reservations':
            self._post_reservations()
        # Route: POST /reservations/{id}/confirm
        elif method == 'POST' and path.startswith('/reservations/') and path.endswith('/confirm'):
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations' and parts[3] == 'confirm':
                res_id = parts[2]
                self._post_reservation_confirm(res_id)
            else:
                send_error(self, "Not found", 404)
        # Route: POST /reservations/{id}/cancel
        elif method == 'POST' and path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations' and parts[3] == 'cancel':
                res_id = parts[2]
                self._post_reservation_cancel(res_id)
            else:
                send_error(self, "Not found", 404)
        else:
            send_error(self, "Not found", 404)

    # ---- GET /items ----
    def _get_items(self):
        with db_lock:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
                rows = cursor.fetchall()
                items = [
                    {
                        "id": row[0],
                        "name": row[1],
                        "stock_total": row[2],
                        "stock_available": row[3]
                    }
                    for row in rows
                ]
                send_json(self, items)

    # ---- POST /items ----
    def _post_items(self):
        data = get_json_body(self)
        if data is None:
            send_error(self, "Invalid JSON body")
            return
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(name, str) or name.strip() == '':
            send_error(self, "Field 'name' is required and must be a non-empty string")
            return
        if stock_total is None or not isinstance(stock_total, int) or stock_total < 0:
            send_error(self, "Field 'stock_total' is required and must be a non-negative integer")
            return

        with db_lock:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO items (name, stock_total, stock_available)
                        VALUES (?, ?, ?)
                    """, (name.strip(), stock_total, stock_total))
                    conn.commit()
                    new_id = cursor.lastrowid
                    send_json(self, {"id": new_id, "name": name.strip(), "stock_total": stock_total}, 201)
                except sqlite3.IntegrityError:
                    send_error(self, f"Item with name '{name}' already exists", 409)

    # ---- POST /reservations ----
    def _post_reservations(self):
        data = get_json_body(self)
        if data is None:
            send_error(self, "Invalid JSON body")
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')
        if not isinstance(item_id, int) or item_id <= 0:
            send_error(self, "Field 'item_id' is required and must be a positive integer")
            return
        if not isinstance(quantity, int) or quantity <= 0:
            send_error(self, "Field 'quantity' is required and must be a positive integer")
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            send_error(self, "Field 'ttl_seconds' is required and must be a positive number")
            return

        with db_lock:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("BEGIN")
                cursor = conn.cursor()
                # Check item existence and stock
                cursor.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
                row = cursor.fetchone()
                if row is None:
                    conn.rollback()
                    send_error(self, "Item not found", 404)
                    return
                stock_available = row[0]
                if stock_available < quantity:
                    conn.rollback()
                    send_error(self, "Insufficient stock", 409)
                    return
                # Create reservation
                res_id = str(uuid.uuid4())
                now = time.time()
                expires_at = now + ttl_seconds
                try:
                    cursor.execute("""
                        INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
                        VALUES (?, ?, ?, 'pending', ?, ?)
                    """, (res_id, item_id, quantity, expires_at, now))
                    # Decrease available stock
                    cursor.execute("""
                        UPDATE items SET stock_available = stock_available - ?
                        WHERE id = ?
                    """, (quantity, item_id))
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    send_error(self, "Failed to create reservation", 500)
                    return
                send_json(self, {
                    "id": res_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": now
                }, 201)

    # ---- POST /reservations/{id}/confirm ----
    def _post_reservation_confirm(self, res_id):
        with db_lock:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("BEGIN")
                cursor = conn.cursor()
                # Check reservation
                cursor.execute("""
                    SELECT id, status, item_id, quantity FROM reservations WHERE id = ?
                """, (res_id,))
                row = cursor.fetchone()
                if row is None:
                    conn.rollback()
                    send_error(self, "Reservation not found", 404)
                    return
                res_id_db, status, item_id, quantity = row
                if status != 'pending':
                    conn.rollback()
                    send_error(self, f"Reservation is already {status}", 409)
                    return
                # Confirm (stock already decreased, no change to stock)
                try:
                    cursor.execute("""
                        UPDATE reservations SET status = 'confirmed' WHERE id = ?
                    """, (res_id,))
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    send_error(self, "Failed to confirm reservation", 500)
                    return
                send_json(self, {"id": res_id, "status": "confirmed"})

    # ---- POST /reservations/{id}/cancel ----
    def _post_reservation_cancel(self, res_id):
        with db_lock:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("BEGIN")
                cursor = conn.cursor()
                # Check reservation
                cursor.execute("""
                    SELECT id, status, item_id, quantity FROM reservations WHERE id = ?
                """, (res_id,))
                row = cursor.fetchone()
                if row is None:
                    conn.rollback()
                    send_error(self, "Reservation not found", 404)
                    return
                res_id_db, status, item_id, quantity = row
                if status != 'pending':
                    conn.rollback()
                    send_error(self, f"Reservation is already {status}", 409)
                    return
                # Cancel: release stock
                try:
                    cursor.execute("""
                        UPDATE items SET stock_available = stock_available + ?
                        WHERE id = ?
                    """, (quantity, item_id))
                    cursor.execute("""
                        UPDATE reservations SET status = 'cancelled' WHERE id = ?
                    """, (res_id,))
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    send_error(self, "Failed to cancel reservation", 500)
                    return
                send_json(self, {"id": res_id, "status": "cancelled"})

    # ---- Override do_* methods ----
    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

# ---------- Main entry ----------

def main():
    init_db()
    server_address = ('127.0.0.1', 8080)
    httpd = HTTPServer(server_address, InventoryHandler)
    print(f"Starting inventory server on http://{server_address[0]}:{server_address[1]}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()

if __name__ == "__main__":
    main()
```
````
