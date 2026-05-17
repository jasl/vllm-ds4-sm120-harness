# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.079333
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2265, "completion_tokens": 1902, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1902
- Total tokens: 2265

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
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import re

DB_PATH = "inventory.db"
lock = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def cleanup_expired():
    with lock:
        conn = get_db()
        try:
            now = datetime.utcnow().isoformat()
            expired = conn.execute(
                "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
                (now,)
            ).fetchall()
            for row in expired:
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                             (row['quantity'], row['item_id']))
                conn.execute("UPDATE reservations SET status='expired' WHERE id = ?", (row['id'],))
            conn.commit()
        finally:
            conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body.decode('utf-8'))
        except:
            return {}

    def _parse_path(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        return path, parse_qs(parsed.query)

    def do_GET(self):
        path, _ = self._parse_path()
        if path == '/items':
            self._handle_get_items()
        else:
            self._send_json({'error': 'Not Found'}, 404)

    def do_POST(self):
        path, _ = self._parse_path()
        if path == '/items':
            self._handle_post_items()
        elif path == '/reservations':
            self._handle_post_reservations()
        elif re.match(r'^/reservations/\d+/confirm$', path):
            parts = path.split('/')
            res_id = int(parts[2])
            self._handle_confirm(res_id)
        elif re.match(r'^/reservations/\d+/cancel$', path):
            parts = path.split('/')
            res_id = int(parts[2])
            self._handle_cancel(res_id)
        else:
            self._send_json({'error': 'Not Found'}, 404)

    def _handle_get_items(self):
        cleanup_expired()
        conn = get_db()
        try:
            rows = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
            items = [{'id': r['id'], 'name': r['name'], 'stock_total': r['stock_total'],
                       'stock_available': r['stock_available']} for r in rows]
            self._send_json({'items': items})
        finally:
            conn.close()

    def _handle_post_items(self):
        data = self._read_body()
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            self._send_json({'error': 'Invalid parameters'}, 400)
            return
        with lock:
            conn = get_db()
            try:
                cur = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                                   (name, stock_total, stock_total))
                conn.commit()
                item_id = cur.lastrowid
                self._send_json({'id': item_id, 'name': name, 'stock_total': stock_total,
                                  'stock_available': stock_total}, 201)
            finally:
                conn.close()

    def _handle_post_reservations(self):
        cleanup_expired()
        data = self._read_body()
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds', 300)
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            self._send_json({'error': 'Invalid parameters'}, 400)
            return
        with lock:
            conn = get_db()
            try:
                item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
                if not item:
                    self._send_json({'error': 'Item not found'}, 404)
                    return
                if item['stock_available'] < quantity:
                    self._send_json({'error': 'Insufficient stock'}, 409)
                    return
                now = datetime.utcnow()
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
                created_at = now.isoformat()
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                             (quantity, item_id))
                cur = conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                                   (item_id, quantity, expires_at, created_at))
                conn.commit()
                res_id = cur.lastrowid
                self._send_json({
                    'id': res_id,
                    'item_id': item_id,
                    'quantity': quantity,
                    'status': 'pending',
                    'expires_at': expires_at,
                    'created_at': created_at
                }, 201)
            finally:
                conn.close()

    def _handle_confirm(self, res_id):
        cleanup_expired()
        with lock:
            conn = get_db()
            try:
                res = conn.execute("SELECT * FROM reservations WHERE id = ?", (res_id,)).fetchone()
                if not res:
                    self._send_json({'error': 'Reservation not found'}, 404)
                    return
                if res['status'] != 'pending':
                    self._send_json({'error': f'Reservation already {res["status"]}'}, 400)
                    return
                conn.execute("UPDATE reservations SET status='confirmed' WHERE id = ?", (res_id,))
                conn.commit()
                self._send_json({'message': 'Reservation confirmed', 'id': res_id})
            finally:
                conn.close()

    def _handle_cancel(self, res_id):
        cleanup_expired()
        with lock:
            conn = get_db()
            try:
                res = conn.execute("SELECT * FROM reservations WHERE id = ?", (res_id,)).fetchone()
                if not res:
                    self._send_json({'error': 'Reservation not found'}, 404)
                    return
                if res['status'] != 'pending':
                    self._send_json({'error': f'Reservation already {res["status"]}'}, 400)
                    return
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                             (res['quantity'], res['item_id']))
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id = ?", (res_id,))
                conn.commit()
                self._send_json({'message': 'Reservation cancelled', 'id': res_id})
            finally:
                conn.close()

    def log_message(self, format, *args):
        pass  # suppress default logging

if __name__ == "__main__":
    init_db()
    server = HTTPServer(('127.0.0.1', 8080), RequestHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
```
````
