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
- Elapsed seconds: 8.105018
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2585, "completion_tokens": 2222, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2222
- Total tokens: 2585

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
import http.server
import json
import sqlite3
import threading
import time
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_PATH = "inventory.db"

# Database initialization
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  stock_total INTEGER NOT NULL,
                  stock_available INTEGER NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  item_id INTEGER NOT NULL,
                  quantity INTEGER NOT NULL,
                  status TEXT NOT NULL DEFAULT 'pending',
                  expires_at TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  FOREIGN KEY(item_id) REFERENCES items(id))''')
    conn.commit()
    return conn

db_conn = init_db()
db_lock = threading.Lock()

def cleanup_expired():
    """Clean up expired pending reservations and release stock"""
    now = datetime.utcnow().isoformat()
    with db_lock:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT id, item_id, quantity FROM reservations
            WHERE status = 'pending' AND expires_at < ?
        """, (now,))
        expired = cursor.fetchall()
        for res_id, item_id, qty in expired:
            cursor.execute("""
                UPDATE items SET stock_available = stock_available + ?
                WHERE id = ?
            """, (qty, item_id))
            cursor.execute("""
                UPDATE reservations SET status = 'expired' WHERE id = ?
            """, (res_id,))
        db_conn.commit()

class RequestHandler(http.server.BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _read_json(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except:
            return {}

    def _parse_path(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        return path

    def do_GET(self):
        cleanup_expired()
        path = self._parse_path()

        if path == '/items' or path == '/items/':
            self._handle_get_items()
        else:
            self._send_json({'error': 'Not Found'}, 404)

    def do_POST(self):
        cleanup_expired()
        path = self._parse_path()

        if path == '/items' or path == '/items/':
            self._handle_post_items()
        elif path == '/reservations' or path == '/reservations/':
            self._handle_post_reservations()
        elif re.match(r'^/reservations/\d+/confirm$', path):
            res_id = int(path.split('/')[2])
            self._handle_confirm_reservation(res_id)
        elif re.match(r'^/reservations/\d+/cancel$', path):
            res_id = int(path.split('/')[2])
            self._handle_cancel_reservation(res_id)
        else:
            self._send_json({'error': 'Not Found'}, 404)

    def _handle_get_items(self):
        with db_lock:
            cursor = db_conn.cursor()
            cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = cursor.fetchall()
            items = [{'id': r[0], 'name': r[1], 'stock_total': r[2], 'stock_available': r[3]} for r in rows]
        self._send_json(items)

    def _handle_post_items(self):
        data = self._read_json()
        name = data.get('name')
        stock_total = data.get('stock_total')

        if not name or stock_total is None:
            self._send_json({'error': 'name and stock_total are required'}, 400)
            return
        try:
            stock_total = int(stock_total)
        except:
            self._send_json({'error': 'stock_total must be an integer'}, 400)
            return
        if stock_total < 0:
            self._send_json({'error': 'stock_total cannot be negative'}, 400)
            return

        with db_lock:
            cursor = db_conn.cursor()
            cursor.execute("""
                INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)
            """, (name, stock_total, stock_total))
            db_conn.commit()
            item_id = cursor.lastrowid

        self._send_json({'id': item_id, 'name': name, 'stock_total': stock_total, 'stock_available': stock_total}, 201)

    def _handle_post_reservations(self):
        data = self._read_json()
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')

        if item_id is None or quantity is None or ttl_seconds is None:
            self._send_json({'error': 'item_id, quantity, and ttl_seconds are required'}, 400)
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except:
            self._send_json({'error': 'parameters must be integers'}, 400)
            return
        if quantity <= 0:
            self._send_json({'error': 'quantity must be positive'}, 400)
            return
        if ttl_seconds <= 0:
            self._send_json({'error': 'ttl_seconds must be positive'}, 400)
            return

        with db_lock:
            cursor = db_conn.cursor()
            # Check item exists and has enough stock
            cursor.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
            if not item:
                self._send_json({'error': 'Item not found'}, 404)
                return
            if item[1] < quantity:
                self._send_json({'error': 'Insufficient stock'}, 409)
                return

            # Create reservation
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            created_at = now.isoformat()

            cursor.execute("""
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            """, (item_id, quantity, expires_at, created_at))
            res_id = cursor.lastrowid

            # Decrease available stock
            cursor.execute("""
                UPDATE items SET stock_available = stock_available - ? WHERE id = ?
            """, (quantity, item_id))
            db_conn.commit()

        self._send_json({
            'id': res_id,
            'item_id': item_id,
            'quantity': quantity,
            'status': 'pending',
            'expires_at': expires_at,
            'created_at': created_at
        }, 201)

    def _handle_confirm_reservation(self, res_id):
        with db_lock:
            cursor = db_conn.cursor()
            # Check reservation exists and is pending
            cursor.execute("""
                SELECT id, status, item_id, quantity FROM reservations WHERE id = ?
            """, (res_id,))
            res = cursor.fetchone()
            if not res:
                self._send_json({'error': 'Reservation not found'}, 404)
                return
            if res[1] != 'pending':
                self._send_json({'error': f'Reservation is already {res[1]}'}, 400)
                return
            if res[1] == 'expired':
                self._send_json({'error': 'Reservation has expired'}, 400)
                return

            # Confirm: set status to confirmed (stock already deducted)
            cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            db_conn.commit()

        self._send_json({'message': 'Reservation confirmed', 'id': res_id})

    def _handle_cancel_reservation(self, res_id):
        with db_lock:
            cursor = db_conn.cursor()
            # Check reservation exists and is pending
            cursor.execute("""
                SELECT id, status, item_id, quantity FROM reservations WHERE id = ?
            """, (res_id,))
            res = cursor.fetchone()
            if not res:
                self._send_json({'error': 'Reservation not found'}, 404)
                return
            if res[1] != 'pending':
                self._send_json({'error': f'Cannot cancel reservation with status {res[1]}'}, 400)
                return

            # Cancel: release stock and set status to cancelled
            cursor.execute("""
                UPDATE items SET stock_available = stock_available + ? WHERE id = ?
            """, (res[3], res[2]))
            cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            db_conn.commit()

        self._send_json({'message': 'Reservation cancelled', 'id': res_id})

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server(host='127.0.0.1', port=8080):
    server = http.server.HTTPServer((host, port), RequestHandler)
    print(f"Server running at http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        db_conn.close()

if __name__ == "__main__":
    run_server()
```
````
