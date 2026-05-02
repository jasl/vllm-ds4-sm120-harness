# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 15.740352
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2559, "completion_tokens": 2196, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2196
- Total tokens: 2559

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
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import time
import os

DB_PATH = "inventory.db"
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    ''')
    conn.commit()
    conn.close()

def clean_expired_reservations():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
    expired = c.fetchall()
    for res_id, item_id, qty in expired:
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
        c.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
    conn.commit()
    conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            with LOCK:
                clean_expired_reservations()
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = []
                for row in c.fetchall():
                    items.append({
                        "id": row[0],
                        "name": row[1],
                        "stock_total": row[2],
                        "stock_available": row[3]
                    })
                conn.close()
                self._send_json(200, items)
        else:
            self._send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else b'{}'
        try:
            data = json.loads(body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_error(400, "Invalid JSON")
            return

        if path == '/items':
            self._handle_post_items(data)
        elif path == '/reservations':
            self._handle_post_reservations(data)
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            parts = path.split('/')
            if len(parts) == 4 and parts[2].isdigit():
                self._handle_confirm_reservation(int(parts[2]))
            else:
                self._send_error(404, "Not Found")
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4 and parts[2].isdigit():
                self._handle_cancel_reservation(int(parts[2]))
            else:
                self._send_error(404, "Not Found")
        else:
            self._send_error(404, "Not Found")

    def _handle_post_items(self, data):
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(name, str) or not name.strip():
            self._send_error(400, "Invalid or missing 'name'")
            return
        if not isinstance(stock_total, int) or stock_total < 0:
            self._send_error(400, "Invalid or missing 'stock_total'")
            return
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name.strip(), stock_total, stock_total))
            conn.commit()
            new_id = c.lastrowid
            conn.close()
            self._send_json(201, {"id": new_id, "name": name.strip(), "stock_total": stock_total, "stock_available": stock_total})

    def _handle_post_reservations(self, data):
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds', 300)
        if not isinstance(item_id, int) or item_id <= 0:
            self._send_error(400, "Invalid or missing 'item_id'")
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_error(400, "Invalid or missing 'quantity'")
            return
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            self._send_error(400, "Invalid or missing 'ttl_seconds'")
            return

        with LOCK:
            clean_expired_reservations()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_error(404, "Item not found")
                return
            stock_available = row[0]
            if stock_available < quantity:
                conn.close()
                self._send_error(409, "Insufficient stock")
                return

            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=ttl_seconds)
            created_at = now.isoformat()
            c.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                      (item_id, quantity, expires_at.isoformat(), created_at))
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            conn.commit()
            new_id = c.lastrowid
            conn.close()
            self._send_json(201, {
                "id": new_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at.isoformat(),
                "created_at": created_at
            })

    def _handle_confirm_reservation(self, res_id):
        with LOCK:
            clean_expired_reservations()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, status FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_error(404, "Reservation not found")
                return
            if row[1] != 'pending':
                conn.close()
                self._send_error(400, f"Reservation is already {row[1]}")
                return
            c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()
            conn.close()
            self._send_json(200, {"id": res_id, "status": "confirmed"})

    def _handle_cancel_reservation(self, res_id):
        with LOCK:
            clean_expired_reservations()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_error(404, "Reservation not found")
                return
            if row[1] == 'cancelled':
                conn.close()
                self._send_error(400, "Reservation already cancelled")
                return
            if row[1] == 'confirmed':
                conn.close()
                self._send_error(400, "Cannot cancel confirmed reservation")
                return
            if row[1] == 'expired':
                conn.close()
                self._send_error(400, "Reservation already expired")
                return
            item_id = row[2]
            quantity = row[3]
            c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (quantity, item_id))
            conn.commit()
            conn.close()
            self._send_json(200, {"id": res_id, "status": "cancelled"})

    def _send_json(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status_code, message):
        self._send_json(status_code, {"error": message})

    def log_message(self, format, *args):
        pass

def run_server(host='127.0.0.1', port=8080):
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    init_db()
    run_server()
```
````
