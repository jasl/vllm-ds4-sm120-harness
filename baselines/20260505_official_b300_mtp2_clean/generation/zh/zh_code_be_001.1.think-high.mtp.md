# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.979148
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2871, "completion_tokens": 2508, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2508
- Total tokens: 2871

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
server.py - A simple HTTP API service for inventory reservations.
Uses only Python 3 standard library (http.server, sqlite3, json, threading, etc.)
"""

import http.server
import json
import sqlite3
import threading
import time
import re
from urllib.parse import urlparse
from datetime import datetime, timezone

# Database file
DB_FILE = "inventory.db"

# Thread lock for concurrent safety
db_lock = threading.Lock()

def init_db():
    """Initialize the database and create tables if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        """)
        conn.commit()

def cleanup_expired():
    """
    Clean up expired pending reservations and release inventory.
    Should be called with db_lock held.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        now = time.time()
        # Find expired pending reservations
        cursor.execute("""
            SELECT id, item_id, quantity FROM reservations
            WHERE status = 'pending' AND expires_at <= ?
        """, (now,))
        expired = cursor.fetchall()
        if not expired:
            return
        # Release stock for each expired reservation
        for res_id, item_id, quantity in expired:
            cursor.execute("""
                UPDATE items SET stock_available = stock_available + ?
                WHERE id = ?
            """, (quantity, item_id))
            cursor.execute("""
                UPDATE reservations SET status = 'expired'
                WHERE id = ?
            """, (res_id,))
        conn.commit()

class InventoryHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for inventory reservation API."""

    def log_message(self, format, *args):
        """Override to suppress default logging or customize as needed."""
        pass

    def _send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, message, status=400):
        """Send error JSON response."""
        self._send_json({"error": message}, status)

    def _read_body(self):
        """Read and parse JSON body from request."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def _parse_path(self):
        """Parse URL path and return (path_segments, query_params)."""
        parsed = urlparse(self.path)
        path = parsed.path.strip("/")
        segments = path.split("/") if path else []
        return segments

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        segments = self._parse_path()
        if segments == ["items"]:
            self._get_items()
        else:
            self._send_error("Not Found", 404)

    def do_POST(self):
        """Handle POST requests."""
        segments = self._parse_path()
        if segments == ["items"]:
            self._post_items()
        elif segments == ["reservations"]:
            self._post_reservations()
        elif len(segments) == 3 and segments[0] == "reservations" and segments[2] == "confirm":
            self._post_reservation_confirm(int(segments[1]))
        elif len(segments) == 3 and segments[0] == "reservations" and segments[2] == "cancel":
            self._post_reservation_cancel(int(segments[1]))
        else:
            self._send_error("Not Found", 404)

    def _get_items(self):
        """GET /items - list all items with available stock."""
        with db_lock:
            cleanup_expired()
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
                self._send_json(items)

    def _post_items(self):
        """POST /items - create a new item."""
        body = self._read_body()
        if body is None:
            self._send_error("Invalid JSON body")
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(name, str):
            self._send_error("Field 'name' is required and must be a string")
            return
        if stock_total is None or not isinstance(stock_total, int) or stock_total < 0:
            self._send_error("Field 'stock_total' must be a non-negative integer")
            return
        with db_lock:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                new_id = cursor.lastrowid
                self._send_json({"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _post_reservations(self):
        """POST /reservations - create a new reservation."""
        body = self._read_body()
        if body is None:
            self._send_error("Invalid JSON body")
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds", 300)  # default 5 minutes
        if not isinstance(item_id, int) or item_id <= 0:
            self._send_error("Field 'item_id' must be a positive integer")
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_error("Field 'quantity' must be a positive integer")
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_error("Field 'ttl_seconds' must be a positive number")
            return
        with db_lock:
            cleanup_expired()
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                # Check item exists and has enough stock
                cursor.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
                item = cursor.fetchone()
                if item is None:
                    self._send_error("Item not found", 404)
                    return
                avail = item[1]
                if avail < quantity:
                    self._send_error(f"Insufficient stock: available {avail}, requested {quantity}", 409)
                    return
                # Reserve stock
                now = time.time()
                expires_at = now + ttl_seconds
                cursor.execute("""
                    INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                    VALUES (?, ?, 'pending', ?, ?)
                """, (item_id, quantity, expires_at, now))
                cursor.execute("""
                    UPDATE items SET stock_available = stock_available - ?
                    WHERE id = ?
                """, (quantity, item_id))
                conn.commit()
                new_id = cursor.lastrowid
                self._send_json({
                    "id": new_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": now
                }, 201)

    def _post_reservation_confirm(self, res_id):
        """POST /reservations/{id}/confirm - confirm a reservation."""
        with db_lock:
            cleanup_expired()
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
                row = cursor.fetchone()
                if row is None:
                    self._send_error("Reservation not found", 404)
                    return
                if row[1] != "pending":
                    self._send_error(f"Reservation status is '{row[1]}', only 'pending' can be confirmed", 400)
                    return
                # Confirm the reservation (no stock change)
                cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
                conn.commit()
                self._send_json({"id": res_id, "status": "confirmed"})

    def _post_reservation_cancel(self, res_id):
        """POST /reservations/{id}/cancel - cancel a reservation and release stock."""
        with db_lock:
            cleanup_expired()
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
                row = cursor.fetchone()
                if row is None:
                    self._send_error("Reservation not found", 404)
                    return
                if row[1] != "pending":
                    self._send_error(f"Reservation status is '{row[1]}', only 'pending' can be cancelled", 400)
                    return
                # Release stock
                cursor.execute("""
                    UPDATE items SET stock_available = stock_available + ?
                    WHERE id = ?
                """, (row[3], row[2]))
                cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
                conn.commit()
                self._send_json({"id": res_id, "status": "cancelled"})

def run_server(host="127.0.0.1", port=8080):
    """Start the HTTP server."""
    server = http.server.HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

if __name__ == "__main__":
    init_db()
    run_server()
```
````
