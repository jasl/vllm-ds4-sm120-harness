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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 15.877542
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2291, "completion_tokens": 1928, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1928
- Total tokens: 2291

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
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_PATH = "reservations.db"
lock = threading.Lock()

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

def cleanup_expired(conn):
    now = datetime.utcnow().isoformat()
    c = conn.cursor()
    # 找出所有过期且pending的预约
    c.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
    expired = c.fetchall()
    for rid, item_id, qty in expired:
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
        c.execute("UPDATE reservations SET status='expired' WHERE id=?", (rid,))
    conn.commit()

class RequestHandler(http.server.BaseHTTPRequestHandler):
    conn = None
    server_lock = None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            self.handle_get_items()
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            self.handle_post_items()
        elif path == '/reservations':
            self.handle_post_reservations()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            resid = path.split('/')[2]
            self.handle_confirm_cancel(resid, 'confirm')
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            resid = path.split('/')[2]
            self.handle_confirm_cancel(resid, 'cancel')
        else:
            self.send_json(404, {"error": "Not found"})

    def handle_get_items(self):
        with self.server_lock:
            cleanup_expired(self.conn)
            c = self.conn.cursor()
            c.execute("SELECT id, name, stock_total, stock_available FROM items")
            items = []
            for row in c.fetchall():
                items.append({
                    "id": row[0],
                    "name": row[1],
                    "stock_total": row[2],
                    "stock_available": row[3]
                })
        self.send_json(200, items)

    def handle_post_items(self):
        try:
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len)
            data = json.loads(body)
        except:
            self.send_json(400, {"error": "Invalid JSON"})
            return

        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self.send_json(400, {"error": "Invalid parameters: name (str) and stock_total (int >=0) required"})
            return

        with self.server_lock:
            cleanup_expired(self.conn)
            c = self.conn.cursor()
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name, stock_total, stock_total))
            self.conn.commit()
            new_id = c.lastrowid
        self.send_json(201, {"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total})

    def handle_post_reservations(self):
        try:
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len)
            data = json.loads(body)
        except:
            self.send_json(400, {"error": "Invalid JSON"})
            return

        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds', 300)

        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            self.send_json(400, {"error": "Invalid parameters: item_id (int) and quantity (int >0) required"})
            return
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            self.send_json(400, {"error": "ttl_seconds must be positive int"})
            return

        with self.server_lock:
            cleanup_expired(self.conn)
            c = self.conn.cursor()
            # 检查商品是否存在且库存足够
            c.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
            row = c.fetchone()
            if not row:
                self.send_json(404, {"error": "Item not found"})
                return
            available = row[0]
            if available < quantity:
                self.send_json(409, {"error": "Insufficient stock"})
                return

            # 创建预约
            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=ttl_seconds)
            created_at = now.isoformat()
            expires_at_str = expires_at.isoformat()
            c.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                      (item_id, quantity, expires_at_str, created_at))
            # 扣减库存
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            self.conn.commit()
            new_id = c.lastrowid
        self.send_json(201, {
            "id": new_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at_str,
            "created_at": created_at
        })

    def handle_confirm_cancel(self, resid, action):
        try:
            resid = int(resid)
        except:
            self.send_json(400, {"error": "Invalid reservation id"})
            return

        with self.server_lock:
            cleanup_expired(self.conn)
            c = self.conn.cursor()
            c.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id=?", (resid,))
            row = c.fetchone()
            if not row:
                self.send_json(404, {"error": "Reservation not found"})
                return
            rid, status, item_id, quantity = row
            if status != 'pending':
                self.send_json(400, {"error": f"Reservation already {status}"})
                return

            if action == 'confirm':
                c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (rid,))
            else:  # cancel
                # 释放库存
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (quantity, item_id))
                c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (rid,))
            self.conn.commit()
        self.send_json(200, {"status": "ok"})

    def send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        pass  # Suppress default logging

def create_server():
    conn = init_db()
    handler = RequestHandler
    handler.conn = conn
    lock_obj = threading.Lock()
    handler.server_lock = lock_obj
    return http.server.HTTPServer(('127.0.0.1', 8080), handler)

if __name__ == "__main__":
    server = create_server()
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()
        print("Server stopped")
```
````
