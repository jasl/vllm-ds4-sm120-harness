# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 36.340261
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2678, "completion_tokens": 2315, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2315
- Total tokens: 2678

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
import urllib.parse
import sys
from datetime import datetime, timedelta

DATABASE = 'inventory.db'
LOCK = threading.Lock()


def init_db():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at REAL NOT NULL,
        created_at REAL NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )''')
    conn.commit()
    return conn


def cleanup_expired(conn):
    current_time = time.time()
    c = conn.cursor()
    c.execute('''SELECT id, item_id, quantity FROM reservations
                 WHERE status='pending' AND expires_at <= ?''', (current_time,))
    expired = c.fetchall()
    for res_id, item_id, qty in expired:
        c.execute('UPDATE reservations SET status=? WHERE id=?', ('expired', res_id))
        c.execute('UPDATE items SET stock_available = stock_available + ? WHERE id=?', (qty, item_id))
    if expired:
        conn.commit()


def get_json_body(request):
    content_length = int(request.headers.get('Content-Length', 0))
    if content_length == 0:
        return {}
    body = request.rfile.read(content_length)
    try:
        return json.loads(body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def send_json_response(handler, status_code, data):
    handler.send_response(status_code)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode('utf-8'))


def parse_path(path):
    parsed = urllib.parse.urlparse(path)
    return parsed.path.rstrip('/')


class RequestHandler(http.server.BaseHTTPRequestHandler):
    conn = None
    lock = LOCK

    def do_GET(self):
        path = parse_path(self.path)
        if path == '/items':
            self.handle_get_items()
        else:
            send_json_response(self, 404, {'error': 'Not Found'})

    def do_POST(self):
        path = parse_path(self.path)
        if path == '/items':
            self.handle_create_item()
        elif path == '/reservations':
            self.handle_create_reservation()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations' and parts[3] == 'confirm':
                try:
                    res_id = int(parts[2])
                    self.handle_confirm_reservation(res_id)
                except ValueError:
                    send_json_response(self, 400, {'error': 'Invalid reservation ID'})
            else:
                send_json_response(self, 404, {'error': 'Not Found'})
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4 and parts[1] == 'reservations' and parts[3] == 'cancel':
                try:
                    res_id = int(parts[2])
                    self.handle_cancel_reservation(res_id)
                except ValueError:
                    send_json_response(self, 400, {'error': 'Invalid reservation ID'})
            else:
                send_json_response(self, 404, {'error': 'Not Found'})
        else:
            send_json_response(self, 404, {'error': 'Not Found'})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def handle_get_items(self):
        with self.lock:
            conn = self.conn
            cleanup_expired(conn)
            c = conn.cursor()
            c.execute('SELECT id, name, stock_total, stock_available FROM items')
            items = [{'id': row[0], 'name': row[1], 'stock_total': row[2], 'stock_available': row[3]} for row in c.fetchall()]
        send_json_response(self, 200, items)

    def handle_create_item(self):
        body = get_json_body(self)
        if body is None:
            send_json_response(self, 400, {'error': 'Invalid JSON'})
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or not isinstance(name, str) or name.strip() == '':
            send_json_response(self, 400, {'error': 'name is required and must be a non-empty string'})
            return
        if stock_total is None or not isinstance(stock_total, int) or stock_total < 0:
            send_json_response(self, 400, {'error': 'stock_total is required and must be a non-negative integer'})
            return
        with self.lock:
            conn = self.conn
            c = conn.cursor()
            c.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                      (name.strip(), stock_total, stock_total))
            conn.commit()
            item_id = c.lastrowid
        send_json_response(self, 201, {'id': item_id, 'name': name.strip(), 'stock_total': stock_total, 'stock_available': stock_total})

    def handle_create_reservation(self):
        body = get_json_body(self)
        if body is None:
            send_json_response(self, 400, {'error': 'Invalid JSON'})
            return
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds', 300)
        if not isinstance(item_id, int) or item_id <= 0:
            send_json_response(self, 400, {'error': 'item_id is required and must be a positive integer'})
            return
        if not isinstance(quantity, int) or quantity <= 0:
            send_json_response(self, 400, {'error': 'quantity is required and must be a positive integer'})
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            send_json_response(self, 400, {'error': 'ttl_seconds must be a positive number'})
            return

        with self.lock:
            conn = self.conn
            cleanup_expired(conn)
            c = conn.cursor()
            c.execute('SELECT stock_available FROM items WHERE id=?', (item_id,))
            row = c.fetchone()
            if row is None:
                send_json_response(self, 404, {'error': 'Item not found'})
                return
            stock_available = row[0]
            if stock_available < quantity:
                send_json_response(self, 409, {'error': 'Insufficient stock'})
                return
            current_time = time.time()
            expires_at = current_time + ttl_seconds
            c.execute('''INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                         VALUES (?, ?, 'pending', ?, ?)''',
                      (item_id, quantity, expires_at, current_time))
            c.execute('UPDATE items SET stock_available = stock_available - ? WHERE id=?', (quantity, item_id))
            conn.commit()
            res_id = c.lastrowid
        send_json_response(self, 201, {'id': res_id, 'item_id': item_id, 'quantity': quantity, 'status': 'pending', 'expires_at': expires_at, 'created_at': current_time})

    def handle_confirm_reservation(self, res_id):
        with self.lock:
            conn = self.conn
            cleanup_expired(conn)
            c = conn.cursor()
            c.execute('SELECT id, status FROM reservations WHERE id=?', (res_id,))
            row = c.fetchone()
            if row is None:
                send_json_response(self, 404, {'error': 'Reservation not found'})
                return
            if row[1] != 'pending':
                send_json_response(self, 400, {'error': f'Reservation is already {row[1]}, cannot confirm'})
                return
            c.execute('UPDATE reservations SET status=? WHERE id=?', ('confirmed', res_id))
            conn.commit()
        send_json_response(self, 200, {'id': res_id, 'status': 'confirmed'})

    def handle_cancel_reservation(self, res_id):
        with self.lock:
            conn = self.conn
            cleanup_expired(conn)
            c = conn.cursor()
            c.execute('SELECT id, item_id, quantity, status FROM reservations WHERE id=?', (res_id,))
            row = c.fetchone()
            if row is None:
                send_json_response(self, 404, {'error': 'Reservation not found'})
                return
            if row[3] != 'pending':
                send_json_response(self, 400, {'error': f'Reservation is already {row[3]}, cannot cancel'})
                return
            item_id = row[1]
            quantity = row[2]
            c.execute('UPDATE reservations SET status=? WHERE id=?', ('cancelled', res_id))
            c.execute('UPDATE items SET stock_available = stock_available + ? WHERE id=?', (quantity, item_id))
            conn.commit()
        send_json_response(self, 200, {'id': res_id, 'status': 'cancelled'})


def run_server(host='127.0.0.1', port=8080):
    conn = init_db()
    RequestHandler.conn = conn
    server = http.server.HTTPServer((host, port), RequestHandler)
    print(f'Server running on http://{host}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.shutdown()
        conn.close()


if __name__ == '__main__':
    run_server()
```
````
