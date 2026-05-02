# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 7.724244
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2442, "completion_tokens": 2079, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2079
- Total tokens: 2442

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
from pathlib import Path

DB_PATH = Path("inventory.db")
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        );
    """)
    conn.commit()
    return conn

def get_db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def cleanup_expired(conn):
    now = datetime.utcnow().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at < ?
    """, (now,))
    expired = cursor.fetchall()
    for row in expired:
        cursor.execute("""
            UPDATE reservations SET status = 'expired' WHERE id = ?
        """, (row['id'],))
        cursor.execute("""
            UPDATE items SET stock_available = stock_available + ?
            WHERE id = ?
        """, (row['quantity'], row['item_id']))
    conn.commit()
    return len(expired)

class InventoryHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default logging

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body.encode())))
        self.end_headers()
        self.wfile.write(body.encode())

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return None
        return json.loads(self.rfile.read(length))

    def parse_path(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        return path, parsed.query

    def do_GET(self):
        path, query = self.parse_path()
        if path == '/items':
            self.handle_get_items()
        else:
            self._send_error("Not Found", 404)

    def do_POST(self):
        path, query = self.parse_path()
        with LOCK:
            conn = get_db()
            try:
                cleanup_expired(conn)
                if path == '/items':
                    self.handle_post_items(conn)
                elif path == '/reservations':
                    self.handle_post_reservations(conn)
                elif path.startswith('/reservations/') and path.endswith('/confirm'):
                    res_id = path.split('/')[2]
                    self.handle_confirm_reservation(conn, res_id)
                elif path.startswith('/reservations/') and path.endswith('/cancel'):
                    res_id = path.split('/')[2]
                    self.handle_cancel_reservation(conn, res_id)
                else:
                    self._send_error("Not Found", 404)
            finally:
                conn.close()

    def handle_get_items(self):
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
            items = [dict(row) for row in cursor.fetchall()]
            self._send_json(items)
        finally:
            conn.close()

    def handle_post_items(self, conn):
        body = self._read_body()
        if not body:
            return self._send_error("Request body required")
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            return self._send_error("Invalid item data")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO items (name, stock_total, stock_available)
            VALUES (?, ?, ?)
        """, (name, stock_total, stock_total))
        conn.commit()
        new_id = cursor.lastrowid
        self._send_json({"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def handle_post_reservations(self, conn):
        body = self._read_body()
        if not body:
            return self._send_error("Request body required")
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds', 300)
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            return self._send_error("Invalid reservation data")
        cursor = conn.cursor()
        # check item exists and stock available
        cursor.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            return self._send_error("Item not found", 404)
        if row['stock_available'] < quantity:
            return self._send_error("Insufficient stock", 409)
        # create reservation
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl_seconds)
        created_at = now
        cursor.execute("""
            INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
            VALUES (?, ?, 'pending', ?, ?)
        """, (item_id, quantity, expires_at.isoformat(), created_at.isoformat()))
        # deduct stock
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
            "expires_at": expires_at.isoformat(),
            "created_at": created_at.isoformat()
        }, 201)

    def handle_confirm_reservation(self, conn, res_id):
        if not res_id.isdigit():
            return self._send_error("Invalid reservation ID")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id = ?", (int(res_id),))
        row = cursor.fetchone()
        if not row:
            return self._send_error("Reservation not found", 404)
        if row['status'] != 'pending':
            return self._send_error("Reservation already confirmed/cancelled/expired", 400)
        # also check not expired (cleanup might have missed)
        if row['expires_at'] < datetime.utcnow().isoformat():
            # expire it now
            cursor.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (row['id'],))
            cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                           (row['quantity'], row['item_id']))
            conn.commit()
            return self._send_error("Reservation expired", 400)
        cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (row['id'],))
        conn.commit()
        self._send_json({"id": row['id'], "status": "confirmed"})

    def handle_cancel_reservation(self, conn, res_id):
        if not res_id.isdigit():
            return self._send_error("Invalid reservation ID")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id = ?", (int(res_id),))
        row = cursor.fetchone()
        if not row:
            return self._send_error("Reservation not found", 404)
        if row['status'] != 'pending':
            return self._send_error("Reservation already confirmed/cancelled/expired", 400)
        # release stock
        cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (row['id'],))
        cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                       (row['quantity'], row['item_id']))
        conn.commit()
        self._send_json({"id": row['id'], "status": "cancelled"})

    def do_DELETE(self):
        self._send_error("Method Not Allowed", 405)

    def do_PUT(self):
        self._send_error("Method Not Allowed", 405)

if __name__ == "__main__":
    init_db()
    server = HTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
```
````
