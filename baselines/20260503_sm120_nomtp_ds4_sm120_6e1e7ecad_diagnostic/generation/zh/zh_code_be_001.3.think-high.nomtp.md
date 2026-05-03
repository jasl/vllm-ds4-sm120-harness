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
- Elapsed seconds: 41.386681
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2997, "completion_tokens": 2634, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2634
- Total tokens: 2997

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

DB_PATH = Path("reservations.db")

def init_db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
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

init_db()

class RWLock:
    """简易读写锁，用于库存一致性保护"""
    def __init__(self):
        self._lock = threading.Lock()
        self._readers = 0
        self._writer = False

    def acquire_read(self):
        while True:
            with self._lock:
                if not self._writer:
                    self._readers += 1
                    return
            time.sleep(0.001)

    def release_read(self):
        with self._lock:
            self._readers -= 1

    def acquire_write(self):
        while True:
            with self._lock:
                if self._readers == 0 and not self._writer:
                    self._writer = True
                    return
            time.sleep(0.001)

    def release_write(self):
        with self._lock:
            self._writer = False

    def __enter__(self):
        self.acquire_write()
        return self

    def __exit__(self, *args):
        self.release_write()

    def read(self):
        return _ReadContext(self)

class _ReadContext:
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire_read()
        return self

    def __exit__(self, *args):
        self.lock.release_read()


db_lock = RWLock()

def get_db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def cleanup_expired():
    """清理所有过期且状态为pending的预约，释放库存"""
    conn = get_db()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    with db_lock:
        c.execute('''
            SELECT id, item_id, quantity FROM reservations
            WHERE status = 'pending' AND expires_at < ?
        ''', (now,))
        expired = c.fetchall()
        for row in expired:
            c.execute('''
                UPDATE reservations SET status = 'expired' WHERE id = ?
            ''', (row['id'],))
            c.execute('''
                UPDATE items SET stock_available = stock_available + ?
                WHERE id = ?
            ''', (row['quantity'], row['item_id']))
        conn.commit()
    conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默日志

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message, status=400):
        self._send_json({'error': message}, status)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return None
        return json.loads(self.rfile.read(length))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            self.handle_get_items()
        else:
            self._send_error('Not Found', 404)

    def do_POST(self):
        cleanup_expired()
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            self.handle_post_items()
        elif path == '/reservations':
            self.handle_post_reservations()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            parts = path.split('/')
            if len(parts) == 4:
                res_id = parts[2]
                self.handle_confirm_reservation(res_id)
            else:
                self._send_error('Invalid URL', 400)
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4:
                res_id = parts[2]
                self.handle_cancel_reservation(res_id)
            else:
                self._send_error('Invalid URL', 400)
        else:
            self._send_error('Not Found', 404)

    def handle_get_items(self):
        conn = get_db()
        c = conn.cursor()
        with db_lock.read():
            c.execute('SELECT id, name, stock_total, stock_available FROM items')
            items = [dict(row) for row in c.fetchall()]
        conn.close()
        self._send_json(items)

    def handle_post_items(self):
        try:
            body = self._read_body()
            if not body:
                return self._send_error('Request body required', 400)
            name = body.get('name')
            stock_total = body.get('stock_total')
            if not name or stock_total is None:
                return self._send_error('name and stock_total required', 400)
            stock_total = int(stock_total)
            if stock_total < 0:
                return self._send_error('stock_total must be >= 0', 400)
            conn = get_db()
            c = conn.cursor()
            with db_lock:
                c.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                         (name, stock_total, stock_total))
                conn.commit()
                item_id = c.lastrowid
                c.execute('SELECT id, name, stock_total, stock_available FROM items WHERE id = ?', (item_id,))
                item = dict(c.fetchone())
            conn.close()
            self._send_json(item, 201)
        except (json.JSONDecodeError, ValueError):
            self._send_error('Invalid JSON', 400)

    def handle_post_reservations(self):
        try:
            body = self._read_body()
            if not body:
                return self._send_error('Request body required', 400)
            item_id = body.get('item_id')
            quantity = body.get('quantity')
            ttl_seconds = body.get('ttl_seconds', 300)
            if item_id is None or quantity is None:
                return self._send_error('item_id and quantity required', 400)
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
            if quantity <= 0:
                return self._send_error('quantity must be positive', 400)
            if ttl_seconds <= 0:
                return self._send_error('ttl_seconds must be positive', 400)

            conn = get_db()
            c = conn.cursor()
            with db_lock:
                # 检查商品是否存在
                c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
                item = c.fetchone()
                if not item:
                    conn.close()
                    return self._send_error('Item not found', 404)
                if item['stock_available'] < quantity:
                    conn.close()
                    return self._send_error('Insufficient stock', 409)

                # 创建预约
                now = datetime.utcnow()
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
                created_at = now.isoformat()
                c.execute('''
                    INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                    VALUES (?, ?, 'pending', ?, ?)
                ''', (item_id, quantity, expires_at, created_at))
                res_id = c.lastrowid
                c.execute('''
                    UPDATE items SET stock_available = stock_available - ?
                    WHERE id = ?
                ''', (quantity, item_id))
                conn.commit()
                c.execute('SELECT * FROM reservations WHERE id = ?', (res_id,))
                reservation = dict(c.fetchone())
            conn.close()
            self._send_json(reservation, 201)
        except (json.JSONDecodeError, ValueError):
            self._send_error('Invalid JSON', 400)

    def handle_confirm_reservation(self, res_id):
        try:
            res_id = int(res_id)
        except ValueError:
            return self._send_error('Invalid reservation id', 400)
        conn = get_db()
        c = conn.cursor()
        with db_lock:
            c.execute('SELECT * FROM reservations WHERE id = ?', (res_id,))
            reservation = c.fetchone()
            if not reservation:
                conn.close()
                return self._send_error('Reservation not found', 404)
            if reservation['status'] != 'pending':
                conn.close()
                return self._send_error('Reservation already ' + reservation['status'], 400)
            if reservation['expires_at'] < datetime.utcnow().isoformat():
                # 已经过期，先清理
                c.execute('UPDATE reservations SET status = ? WHERE id = ?', ('expired', res_id))
                c.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?',
                         (reservation['quantity'], reservation['item_id']))
                conn.commit()
                conn.close()
                return self._send_error('Reservation expired', 400)
            c.execute('UPDATE reservations SET status = ? WHERE id = ?', ('confirmed', res_id))
            conn.commit()
            c.execute('SELECT * FROM reservations WHERE id = ?', (res_id,))
            updated = dict(c.fetchone())
        conn.close()
        self._send_json(updated)

    def handle_cancel_reservation(self, res_id):
        try:
            res_id = int(res_id)
        except ValueError:
            return self._send_error('Invalid reservation id', 400)
        conn = get_db()
        c = conn.cursor()
        with db_lock:
            c.execute('SELECT * FROM reservations WHERE id = ?', (res_id,))
            reservation = c.fetchone()
            if not reservation:
                conn.close()
                return self._send_error('Reservation not found', 404)
            if reservation['status'] != 'pending':
                conn.close()
                return self._send_error('Reservation already ' + reservation['status'], 400)
            # 释放库存
            c.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?',
                     (reservation['quantity'], reservation['item_id']))
            c.execute('UPDATE reservations SET status = ? WHERE id = ?', ('cancelled', res_id))
            conn.commit()
            c.execute('SELECT * FROM reservations WHERE id = ?', (res_id,))
            updated = dict(c.fetchone())
        conn.close()
        self._send_json(updated)


def run_server(host='127.0.0.1', port=8080):
    server = HTTPServer((host, port), RequestHandler)
    print(f'Server running on {host}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.shutdown()

if __name__ == '__main__':
    run_server()
```
````
