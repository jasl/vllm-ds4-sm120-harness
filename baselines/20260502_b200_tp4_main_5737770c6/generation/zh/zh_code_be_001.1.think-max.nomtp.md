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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 15.851944
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2586, "completion_tokens": 2223, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2223
- Total tokens: 2586

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
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_FILE = "inventory.db"
lock = threading.Lock()
db_initialized = False

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
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
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()

def cleanup_expired():
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at < ?
    """, (now,))
    expired = cursor.fetchall()
    for res in expired:
        cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                       (res['quantity'], res['item_id']))
        cursor.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res['id'],))
    conn.commit()
    conn.close()

class InventoryHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return b''
        return self.rfile.read(content_length)

    def _parse_json_body(self):
        body = self._read_body()
        if not body:
            return None
        try:
            return json.loads(body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/items':
            with lock:
                cleanup_expired()
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [dict(row) for row in cursor.fetchall()]
                conn.close()
            self._send_json(200, items)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        with lock:
            cleanup_expired()

            if path == '/items':
                self._handle_create_item()
            elif path == '/reservations':
                self._handle_create_reservation()
            elif path.startswith('/reservations/') and path.endswith('/confirm'):
                res_id = path.split('/')[2]
                self._handle_confirm_reservation(res_id)
            elif path.startswith('/reservations/') and path.endswith('/cancel'):
                res_id = path.split('/')[2]
                self._handle_cancel_reservation(res_id)
            else:
                self._send_json(404, {"error": "Not found"})

    def _handle_create_item(self):
        data = self._parse_json_body()
        if not data or 'name' not in data or 'stock_total' not in data:
            self._send_json(400, {"error": "Missing required fields: name, stock_total"})
            return

        name = data['name'].strip()
        try:
            stock_total = int(data['stock_total'])
        except (ValueError, TypeError):
            self._send_json(400, {"error": "stock_total must be an integer"})
            return

        if stock_total < 0:
            self._send_json(400, {"error": "stock_total must be non-negative"})
            return

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                       (name, stock_total, stock_total))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        self._send_json(201, {"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total})

    def _handle_create_reservation(self):
        data = self._parse_json_body()
        if not data or 'item_id' not in data or 'quantity' not in data or 'ttl_seconds' not in data:
            self._send_json(400, {"error": "Missing required fields: item_id, quantity, ttl_seconds"})
            return

        try:
            item_id = int(data['item_id'])
            quantity = int(data['quantity'])
            ttl_seconds = int(data['ttl_seconds'])
        except (ValueError, TypeError):
            self._send_json(400, {"error": "Fields must be integers"})
            return

        if quantity <= 0 or ttl_seconds <= 0:
            self._send_json(400, {"error": "quantity and ttl_seconds must be positive"})
            return

        conn = get_db()
        cursor = conn.cursor()

        # Check item exists and has enough stock
        cursor.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if not item:
            conn.close()
            self._send_json(404, {"error": "Item not found"})
            return

        if item['stock_available'] < quantity:
            conn.close()
            self._send_json(409, {"error": "Insufficient stock"})
            return

        # Create reservation
        now = datetime.utcnow()
        expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
        created_at = now.isoformat()

        cursor.execute("""
            INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
            VALUES (?, ?, 'pending', ?, ?)
        """, (item_id, quantity, expires_at, created_at))

        # Decrease available stock
        cursor.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                       (quantity, item_id))
        conn.commit()
        res_id = cursor.lastrowid
        conn.close()

        self._send_json(201, {
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        })

    def _handle_confirm_reservation(self, res_id):
        try:
            res_id = int(res_id)
        except ValueError:
            self._send_json(400, {"error": "Invalid reservation ID"})
            return

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
        reservation = cursor.fetchone()

        if not reservation:
            conn.close()
            self._send_json(404, {"error": "Reservation not found"})
            return

        if reservation['status'] != 'pending':
            conn.close()
            self._send_json(400, {"error": f"Cannot confirm reservation with status '{reservation['status']}'"})
            return

        cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
        conn.commit()
        conn.close()

        self._send_json(200, {"id": res_id, "status": "confirmed"})

    def _handle_cancel_reservation(self, res_id):
        try:
            res_id = int(res_id)
        except ValueError:
            self._send_json(400, {"error": "Invalid reservation ID"})
            return

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
        reservation = cursor.fetchone()

        if not reservation:
            conn.close()
            self._send_json(404, {"error": "Reservation not found"})
            return

        if reservation['status'] != 'pending':
            conn.close()
            self._send_json(400, {"error": f"Cannot cancel reservation with status '{reservation['status']}'"})
            return

        # Release stock
        cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                       (reservation['quantity'], reservation['item_id']))
        cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
        conn.commit()
        conn.close()

        self._send_json(200, {"id": res_id, "status": "cancelled"})

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server():
    global db_initialized
    if not db_initialized:
        init_db()
        db_initialized = True

    server = HTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    run_server()
```
````
