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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 14.925239
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2197, "completion_tokens": 1834, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1834
- Total tokens: 2197

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
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = "inventory.db"
_lock = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
            id TEXT PRIMARY KEY,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def cleanup_expired():
    now = time.time()
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at <= ?
    ''', (now,))
    expired = c.fetchall()
    for row in expired:
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('expired', row['id']))
        conn.execute('''
            UPDATE items SET stock_available = stock_available + ?
            WHERE id = ?
        ''', (row['quantity'], row['item_id']))
    conn.commit()
    conn.close()

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence logs

    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _json_response(self, data, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _error(self, message, status=400):
        self._json_response({'error': message}, status)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return None
        return json.loads(self.rfile.read(length).decode('utf-8'))

    def _parse_path(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        return path, parsed.query

    def do_GET(self):
        path, _ = self._parse_path()
        with _lock:
            cleanup_expired()
            if path == '/items':
                conn = get_db()
                c = conn.cursor()
                c.execute('SELECT id, name, stock_total, stock_available FROM items')
                items = [dict(row) for row in c.fetchall()]
                conn.close()
                self._json_response(items)
            else:
                self._error('Not Found', 404)

    def do_POST(self):
        path, _ = self._parse_path()
        body = self._read_body()
        if body is None:
            return self._error('Request body required')

        with _lock:
            cleanup_expired()
            conn = get_db()
            try:
                if path == '/items':
                    self._create_item(conn, body)
                elif path == '/reservations':
                    self._create_reservation(conn, body)
                elif path.startswith('/reservations/') and path.endswith('/confirm'):
                    rid = path.split('/')[2]
                    self._confirm_reservation(conn, rid)
                elif path.startswith('/reservations/') and path.endswith('/cancel'):
                    rid = path.split('/')[2]
                    self._cancel_reservation(conn, rid)
                else:
                    self._error('Not Found', 404)
            except Exception as e:
                conn.rollback()
                self._error(str(e), 500)
            finally:
                conn.close()

    def _create_item(self, conn, body):
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            return self._error('Invalid name or stock_total')
        c = conn.cursor()
        c.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                  (name, stock_total, stock_total))
        conn.commit()
        new_id = c.lastrowid
        self._json_response({'id': new_id, 'name': name, 'stock_total': stock_total, 'stock_available': stock_total}, 201)

    def _create_reservation(self, conn, body):
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds', 300)
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0 or ttl_seconds <= 0:
            return self._error('Invalid parameters')
        c = conn.cursor()
        c.execute('SELECT stock_available FROM items WHERE id = ?', (item_id,))
        row = c.fetchone()
        if not row:
            return self._error('Item not found', 404)
        available = row['stock_available']
        if available < quantity:
            return self._error('Insufficient stock', 409)
        rid = str(uuid.uuid4())
        now = time.time()
        expires_at = now + ttl_seconds
        conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id = ?',
                     (quantity, item_id))
        conn.execute('''
            INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
            VALUES (?, ?, ?, 'pending', ?, ?)
        ''', (rid, item_id, quantity, expires_at, now))
        conn.commit()
        self._json_response({
            'id': rid,
            'item_id': item_id,
            'quantity': quantity,
            'status': 'pending',
            'expires_at': expires_at,
            'created_at': now
        }, 201)

    def _confirm_reservation(self, conn, rid):
        c = conn.cursor()
        c.execute('SELECT status, item_id, quantity FROM reservations WHERE id = ?', (rid,))
        row = c.fetchone()
        if not row:
            return self._error('Reservation not found', 404)
        if row['status'] != 'pending':
            return self._error('Reservation cannot be confirmed', 400)
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('confirmed', rid))
        conn.commit()
        self._json_response({'message': 'Reservation confirmed', 'id': rid})

    def _cancel_reservation(self, conn, rid):
        c = conn.cursor()
        c.execute('SELECT status, item_id, quantity FROM reservations WHERE id = ?', (rid,))
        row = c.fetchone()
        if not row:
            return self._error('Reservation not found', 404)
        if row['status'] != 'pending':
            return self._error('Reservation cannot be cancelled', 400)
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('cancelled', rid))
        conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?',
                     (row['quantity'], row['item_id']))
        conn.commit()
        self._json_response({'message': 'Reservation cancelled', 'id': rid})

    def do_OPTIONS(self):
        self._set_headers(204)
        self.wfile.write(b'')

def run_server(host='127.0.0.1', port=8080):
    server = HTTPServer((host, port), APIHandler)
    print(f'Server running on http://{host}:{port}')
    server.serve_forever()

if __name__ == '__main__':
    init_db()
    run_server()
```
````
