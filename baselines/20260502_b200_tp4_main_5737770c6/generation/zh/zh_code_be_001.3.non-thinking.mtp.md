# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 7.924837
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2633, "completion_tokens": 2270, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2270
- Total tokens: 2633

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
import uuid
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from http import HTTPStatus

DB_PATH = "inventory.db"
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def cleanup_expired():
    """清理已过期的pending预约，释放库存"""
    conn = get_db()
    try:
        with LOCK:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            # 查找过期的pending预约
            cursor.execute('''
                SELECT id, item_id, quantity FROM reservations
                WHERE status = 'pending' AND expires_at < ?
            ''', (now,))
            expired = cursor.fetchall()
            for row in expired:
                # 释放库存
                cursor.execute('''
                    UPDATE items SET stock_available = stock_available + ?
                    WHERE id = ?
                ''', (row['quantity'], row['item_id']))
                # 更新预约状态为expired
                cursor.execute('''
                    UPDATE reservations SET status = 'expired' WHERE id = ?
                ''', (row['id'],))
            conn.commit()
    finally:
        conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
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
            try:
                cleanup_expired()
                conn = get_db()
                try:
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, name, stock_total, stock_available FROM items')
                    items = [dict(row) for row in cursor.fetchall()]
                    self._send_json(items)
                finally:
                    conn.close()
            except Exception as e:
                self._send_error(str(e), 500)
        else:
            self._send_error('Not Found', 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        try:
            body = self._read_body()
            if body is None:
                self._send_error('Request body is required')
                return
        except Exception:
            self._send_error('Invalid JSON body')
            return

        if path == '/items':
            self._handle_create_item(body)
        elif path == '/reservations':
            self._handle_create_reservation(body)
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            res_id = path.split('/')[2]
            self._handle_confirm(res_id)
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            res_id = path.split('/')[2]
            self._handle_cancel(res_id)
        else:
            self._send_error('Not Found', 404)

    def _handle_create_item(self, body):
        name = body.get('name')
        stock_total = body.get('stock_total')

        if not name or not isinstance(name, str):
            self._send_error('Invalid or missing name')
            return
        if not isinstance(stock_total, int) or stock_total < 0:
            self._send_error('stock_total must be non-negative integer')
            return

        try:
            cleanup_expired()
            conn = get_db()
            try:
                with LOCK:
                    cursor = conn.cursor()
                    item_id = str(uuid.uuid4())
                    cursor.execute('''
                        INSERT INTO items (id, name, stock_total, stock_available)
                        VALUES (?, ?, ?, ?)
                    ''', (item_id, name, stock_total, stock_total))
                    conn.commit()
                    self._send_json({
                        'id': item_id,
                        'name': name,
                        'stock_total': stock_total,
                        'stock_available': stock_total
                    }, 201)
            finally:
                conn.close()
        except Exception as e:
            self._send_error(str(e), 500)

    def _handle_create_reservation(self, body):
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds', 300)

        if not item_id or not isinstance(item_id, str):
            self._send_error('Invalid or missing item_id')
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_error('quantity must be positive integer')
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_error('ttl_seconds must be positive number')
            return

        try:
            cleanup_expired()
            conn = get_db()
            try:
                with LOCK:
                    cursor = conn.cursor()
                    # 检查商品是否存在
                    cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
                    item = cursor.fetchone()
                    if not item:
                        self._send_error('Item not found', 404)
                        return

                    # 检查可用库存
                    if item['stock_available'] < quantity:
                        self._send_error('Insufficient stock', 409)
                        return

                    # 创建预约
                    res_id = str(uuid.uuid4())
                    now = datetime.utcnow()
                    expires_at = now + timedelta(seconds=ttl_seconds)

                    cursor.execute('''
                        INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
                        VALUES (?, ?, ?, 'pending', ?, ?)
                    ''', (res_id, item_id, quantity, expires_at.isoformat(), now.isoformat()))

                    # 扣减库存
                    cursor.execute('''
                        UPDATE items SET stock_available = stock_available - ?
                        WHERE id = ?
                    ''', (quantity, item_id))

                    conn.commit()
                    self._send_json({
                        'id': res_id,
                        'item_id': item_id,
                        'quantity': quantity,
                        'status': 'pending',
                        'expires_at': expires_at.isoformat(),
                        'created_at': now.isoformat()
                    }, 201)
            finally:
                conn.close()
        except Exception as e:
            self._send_error(str(e), 500)

    def _handle_confirm(self, res_id):
        try:
            cleanup_expired()
            conn = get_db()
            try:
                with LOCK:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM reservations WHERE id = ?', (res_id,))
                    reservation = cursor.fetchone()
                    if not reservation:
                        self._send_error('Reservation not found', 404)
                        return
                    if reservation['status'] != 'pending':
                        self._send_error(f'Cannot confirm reservation with status: {reservation["status"]}', 400)
                        return
                    if reservation['expires_at'] < datetime.utcnow().isoformat():
                        self._send_error('Reservation has expired', 400)
                        return

                    cursor.execute('''
                        UPDATE reservations SET status = 'confirmed' WHERE id = ?
                    ''', (res_id,))
                    conn.commit()
                    self._send_json({'id': res_id, 'status': 'confirmed'})
            finally:
                conn.close()
        except Exception as e:
            self._send_error(str(e), 500)

    def _handle_cancel(self, res_id):
        try:
            cleanup_expired()
            conn = get_db()
            try:
                with LOCK:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM reservations WHERE id = ?', (res_id,))
                    reservation = cursor.fetchone()
                    if not reservation:
                        self._send_error('Reservation not found', 404)
                        return
                    if reservation['status'] != 'pending':
                        self._send_error(f'Cannot cancel reservation with status: {reservation["status"]}', 400)
                        return

                    # 释放库存
                    cursor.execute('''
                        UPDATE items SET stock_available = stock_available + ?
                        WHERE id = ?
                    ''', (reservation['quantity'], reservation['item_id']))

                    cursor.execute('''
                        UPDATE reservations SET status = 'cancelled' WHERE id = ?
                    ''', (res_id,))
                    conn.commit()
                    self._send_json({'id': res_id, 'status': 'cancelled'})
            finally:
                conn.close()
        except Exception as e:
            self._send_error(str(e), 500)

    def log_message(self, format, *args):
        pass  # 抑制默认日志输出

if __name__ == "__main__":
    init_db()
    server = HTTPServer(('127.0.0.1', 8080), RequestHandler)
    print('Server running on http://127.0.0.1:8080')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
```
````
