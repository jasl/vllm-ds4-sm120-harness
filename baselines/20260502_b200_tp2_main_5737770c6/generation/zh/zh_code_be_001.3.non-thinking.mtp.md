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
- Elapsed seconds: 6.842117
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2300, "completion_tokens": 1937, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1937
- Total tokens: 2300

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

DB_PATH = "inventory.db"
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()

def cleanup_expired():
    """清理过期 pending 预约，释放库存"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = time.time()
    rows = c.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
        (now,)
    ).fetchall()
    for rid, iid, qty in rows:
        c.execute("UPDATE reservations SET status='expired' WHERE id=? AND status='pending'", (rid,))
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, iid))
    conn.commit()
    conn.close()

def read_json_body(handler):
    content_length = int(handler.headers.get('Content-Length', 0))
    if content_length == 0:
        return {}
    body = handler.rfile.read(content_length)
    return json.loads(body.decode('utf-8'))

def send_json(handler, data, status=200):
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode('utf-8'))

def send_error(handler, msg, status=400):
    send_json(handler, {"error": msg}, status)

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            self.handle_get_items()
        else:
            send_error(self, "Not Found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            self.handle_post_items()
        elif path == '/reservations':
            self.handle_post_reservations()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            parts = path.split('/')
            if len(parts) == 4 and parts[2].isdigit():
                self.handle_confirm_cancel(int(parts[2]), 'confirm')
            else:
                send_error(self, "Invalid path", 404)
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4 and parts[2].isdigit():
                self.handle_confirm_cancel(int(parts[2]), 'cancel')
            else:
                send_error(self, "Invalid path", 404)
        else:
            send_error(self, "Not Found", 404)

    def handle_get_items(self):
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
            items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
            conn.close()
        send_json(self, items)

    def handle_post_items(self):
        try:
            data = read_json_body(self)
        except Exception:
            send_error(self, "Invalid JSON", 400)
            return
        name = data.get('name', '').strip()
        stock_total = data.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            send_error(self, "Invalid parameters: name (str) and stock_total (int >=0) required", 400)
            return
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name, stock_total, stock_total))
            item_id = c.lastrowid
            conn.commit()
            conn.close()
        send_json(self, {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def handle_post_reservations(self):
        try:
            data = read_json_body(self)
        except Exception:
            send_error(self, "Invalid JSON", 400)
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')
        if not isinstance(item_id, int) or not isinstance(quantity, int) or not isinstance(ttl_seconds, (int, float)):
            send_error(self, "Invalid parameters: item_id (int), quantity (int), ttl_seconds (number) required", 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            send_error(self, "quantity and ttl_seconds must be positive", 400)
            return
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            # 先清理过期
            cleanup_expired()
            # 检查库存
            row = c.execute("SELECT stock_available FROM items WHERE id=?", (item_id,)).fetchone()
            if not row:
                conn.close()
                send_error(self, "Item not found", 404)
                return
            available = row[0]
            if available < quantity:
                conn.close()
                send_error(self, "Insufficient stock", 409)
                return
            # 扣减库存
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
            now = time.time()
            expires_at = now + ttl_seconds
            c.execute("""
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            """, (item_id, quantity, expires_at, now))
            res_id = c.lastrowid
            conn.commit()
            conn.close()
        send_json(self, {
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": now
        }, 201)

    def handle_confirm_cancel(self, res_id, action):
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            # 先清理过期
            cleanup_expired()
            row = c.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id=?", (res_id,)).fetchone()
            if not row:
                conn.close()
                send_error(self, "Reservation not found", 404)
                return
            rid, status, item_id, quantity = row
            if status != 'pending':
                conn.close()
                send_error(self, f"Reservation already {status}", 400)
                return
            if action == 'confirm':
                c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (rid,))
                # 确认后库存不再释放，已扣减的库存视为已占用
                conn.commit()
            elif action == 'cancel':
                c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (rid,))
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
                conn.commit()
            conn.close()
        send_json(self, {"id": rid, "status": "confirmed" if action == 'confirm' else "cancelled"})

def run_server(host='127.0.0.1', port=8080):
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.server_close()

if __name__ == "__main__":
    run_server()
```
````
