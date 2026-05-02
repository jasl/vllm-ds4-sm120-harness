# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 15.651376
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2271, "completion_tokens": 1908, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1908
- Total tokens: 2271

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

DB_FILE = 'inventory.db'
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_FILE)
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
        FOREIGN KEY (item_id) REFERENCES items(id)
    )''')
    conn.commit()
    conn.close()

def cleanup_expired():
    """清理过期 pending 预约并释放库存"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    # 找出过期 pending 预约
    c.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
    expired = c.fetchall()
    for res_id, item_id, qty in expired:
        # 释放库存
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
        c.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
    conn.commit()
    conn.close()

class InventoryHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length).decode('utf-8') if length else ''

    def _parse_json(self):
        try:
            return json.loads(self._read_body())
        except:
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/items':
            with LOCK:
                cleanup_expired()
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in c.fetchall()]
                conn.close()
            self._send_json(items)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                if path == '/items':
                    data = self._parse_json()
                    if not data or 'name' not in data or 'stock_total' not in data:
                        self._send_json({"error": "Missing required fields: name, stock_total"}, 400)
                        return
                    name = data['name']
                    stock_total = int(data['stock_total'])
                    if stock_total < 0:
                        self._send_json({"error": "stock_total must be non-negative"}, 400)
                        return
                    c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                              (name, stock_total, stock_total))
                    conn.commit()
                    item_id = c.lastrowid
                    self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

                elif path == '/reservations':
                    data = self._parse_json()
                    if not data or 'item_id' not in data or 'quantity' not in data or 'ttl_seconds' not in data:
                        self._send_json({"error": "Missing required fields: item_id, quantity, ttl_seconds"}, 400)
                        return
                    item_id = int(data['item_id'])
                    quantity = int(data['quantity'])
                    ttl = int(data['ttl_seconds'])
                    if quantity <= 0 or ttl <= 0:
                        self._send_json({"error": "quantity and ttl_seconds must be positive"}, 400)
                        return
                    # 检查库存
                    c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
                    row = c.fetchone()
                    if not row:
                        self._send_json({"error": "Item not found"}, 404)
                        return
                    available = row[0]
                    if available < quantity:
                        self._send_json({"error": "Insufficient stock"}, 409)
                        return
                    # 扣减库存
                    c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
                    now = datetime.utcnow()
                    expires_at = (now + timedelta(seconds=ttl)).isoformat()
                    created_at = now.isoformat()
                    c.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                              (item_id, quantity, expires_at, created_at))
                    conn.commit()
                    res_id = c.lastrowid
                    self._send_json({"id": res_id, "item_id": item_id, "quantity": quantity, "status": "pending", "expires_at": expires_at, "created_at": created_at}, 201)

                elif path.startswith('/reservations/') and path.endswith('/confirm'):
                    parts = path.split('/')
                    if len(parts) != 4:
                        self._send_json({"error": "Invalid path"}, 400)
                        return
                    res_id = int(parts[2])
                    c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
                    row = c.fetchone()
                    if not row:
                        self._send_json({"error": "Reservation not found"}, 404)
                        return
                    status, item_id, qty = row
                    if status != 'pending':
                        self._send_json({"error": f"Cannot confirm reservation with status '{status}'"}, 400)
                        return
                    c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
                    conn.commit()
                    self._send_json({"message": "Reservation confirmed"})

                elif path.startswith('/reservations/') and path.endswith('/cancel'):
                    parts = path.split('/')
                    if len(parts) != 4:
                        self._send_json({"error": "Invalid path"}, 400)
                        return
                    res_id = int(parts[2])
                    c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
                    row = c.fetchone()
                    if not row:
                        self._send_json({"error": "Reservation not found"}, 404)
                        return
                    status, item_id, qty = row
                    if status != 'pending':
                        self._send_json({"error": f"Cannot cancel reservation with status '{status}'"}, 400)
                        return
                    # 释放库存
                    c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
                    c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
                    conn.commit()
                    self._send_json({"message": "Reservation cancelled"})

                else:
                    self._send_json({"error": "Not Found"}, 404)
            except (KeyError, ValueError, IndexError):
                self._send_json({"error": "Bad request"}, 400)
            finally:
                conn.close()

    def do_DELETE(self):
        self._send_json({"error": "Method not allowed"}, 405)

def run_server(host='127.0.0.1', port=8080):
    init_db()
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
```
````
