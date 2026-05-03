# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 35.164254
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2604, "completion_tokens": 2241, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2241
- Total tokens: 2604

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
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_NAME = "inventory.db"
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()

def clean_expired_reservations():
    """清理过期预约并释放库存，每次请求前调用"""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    with LOCK:
        c.execute("""
            SELECT id, item_id, quantity FROM reservations
            WHERE status = 'pending' AND expires_at < ?
        """, (now,))
        expired = c.fetchall()
        for res_id, item_id, qty in expired:
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
        conn.commit()
    conn.close()

def parse_json_body(handler):
    content_length = int(handler.headers.get('Content-Length', 0))
    if content_length == 0:
        return {}
    raw = handler.rfile.read(content_length)
    return json.loads(raw.decode('utf-8'))

def send_json(handler, data, status=200):
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode('utf-8'))

def send_error(handler, message, status=400):
    send_json(handler, {"error": message}, status)

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        clean_expired_reservations()
        if path == "/items":
            self.handle_get_items()
        else:
            send_error(self, "Not Found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        clean_expired_reservations()
        try:
            body = parse_json_body(self)
        except Exception:
            send_error(self, "Invalid JSON body")
            return

        if path == "/items":
            self.handle_post_items(body)
        elif path == "/reservations":
            self.handle_post_reservations(body)
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split('/')[2]
            self.handle_confirm_reservation(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split('/')[2]
            self.handle_cancel_reservation(res_id)
        else:
            send_error(self, "Not Found", 404)

    def handle_get_items(self):
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT id, name, stock_total, stock_available FROM items")
        rows = c.fetchall()
        items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
        conn.close()
        send_json(self, items)

    def handle_post_items(self, body):
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            send_error(self, "Invalid parameters: name (string) and stock_total (non-negative int) required")
            return
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        try:
            with LOCK:
                c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                          (name, stock_total, stock_total))
                conn.commit()
                new_id = c.lastrowid
            send_json(self, {"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
        except sqlite3.IntegrityError:
            send_error(self, f"Item with name '{name}' already exists", 409)
        finally:
            conn.close()

    def handle_post_reservations(self, body):
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds", 300)
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            send_error(self, "Invalid parameters: item_id (int) and quantity (positive int) required")
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            send_error(self, "ttl_seconds must be positive number")
            return

        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        with LOCK:
            c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = c.fetchone()
            if not row:
                send_error(self, "Item not found", 404)
                conn.close()
                return
            available = row[0]
            if available < quantity:
                send_error(self, "Insufficient stock", 409)
                conn.close()
                return
            # 创建预约
            res_id = str(uuid.uuid4())
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            created_at = now.isoformat()
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            c.execute("""
                INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
            """, (res_id, item_id, quantity, expires_at, created_at))
            conn.commit()
        conn.close()
        send_json(self, {
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        }, 201)

    def handle_confirm_reservation(self, res_id):
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        with LOCK:
            c.execute("SELECT status FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                send_error(self, "Reservation not found", 404)
                conn.close()
                return
            if row[0] == "confirmed":
                send_error(self, "Reservation already confirmed", 400)
                conn.close()
                return
            if row[0] == "cancelled":
                send_error(self, "Reservation already cancelled", 400)
                conn.close()
                return
            # 检查是否过期
            c.execute("SELECT expires_at FROM reservations WHERE id = ?", (res_id,))
            expires_at_str = c.fetchone()[0]
            if datetime.utcnow() > datetime.fromisoformat(expires_at_str):
                send_error(self, "Reservation expired", 410)
                conn.close()
                return
            c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()
        conn.close()
        send_json(self, {"message": "Reservation confirmed", "id": res_id})

    def handle_cancel_reservation(self, res_id):
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        with LOCK:
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                send_error(self, "Reservation not found", 404)
                conn.close()
                return
            status, item_id, qty = row
            if status != "pending":
                send_error(self, f"Reservation is already {status}", 400)
                conn.close()
                return
            # 检查是否过期
            c.execute("SELECT expires_at FROM reservations WHERE id = ?", (res_id,))
            expires_at_str = c.fetchone()[0]
            if datetime.utcnow() > datetime.fromisoformat(expires_at_str):
                # 已过期，但还未被清理，可以取消并释放库存
                pass
            c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            conn.commit()
        conn.close()
        send_json(self, {"message": "Reservation cancelled", "id": res_id})

    def log_message(self, format, *args):
        # 禁止输出日志到控制台（可选）
        pass

def run(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run()
```
````
