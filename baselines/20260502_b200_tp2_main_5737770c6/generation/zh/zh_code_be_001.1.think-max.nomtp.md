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
- Elapsed seconds: 15.430402
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2259, "completion_tokens": 1896, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1896
- Total tokens: 2259

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
import re


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
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()


def clean_expired():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at < ?
    """, (now,))
    expired = c.fetchall()
    for res_id, item_id, qty in expired:
        c.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
    conn.commit()
    conn.close()


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/items":
            self.handle_get_items()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/items":
            self.handle_post_item()
        elif path == "/reservations":
            self.handle_post_reservation()
        elif re.match(r"^/reservations/\d+/confirm$", path):
            res_id = int(path.split("/")[2])
            self.handle_confirm(res_id)
        elif re.match(r"^/reservations/\d+/cancel$", path):
            res_id = int(path.split("/")[2])
            self.handle_cancel(res_id)
        else:
            self.send_error(404, "Not Found")

    def handle_get_items(self):
        clean_expired()
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, name, stock_total, stock_available FROM items")
            items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in c.fetchall()]
            conn.close()
        self.send_json(200, items)

    def handle_post_item(self):
        body = self.read_json()
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self.send_error(400, "Invalid input: name and stock_total (non-negative int) required")
            return
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name, stock_total, stock_total))
            conn.commit()
            item_id = c.lastrowid
            conn.close()
        self.send_json(201, {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total})

    def handle_post_reservation(self):
        clean_expired()
        body = self.read_json()
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl = body.get("ttl_seconds")
        if not all([isinstance(item_id, int), isinstance(quantity, int), isinstance(ttl, (int, float))]):
            self.send_error(400, "Invalid input: item_id, quantity (int), ttl_seconds (number) required")
            return
        if quantity <= 0 or ttl <= 0:
            self.send_error(400, "quantity and ttl_seconds must be positive")
            return
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.send_error(404, "Item not found")
                return
            stock = row[0]
            if stock < quantity:
                conn.close()
                self.send_error(409, "Insufficient stock")
                return
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl)).isoformat()
            created_at = now.isoformat()
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            c.execute("""
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            """, (item_id, quantity, expires_at, created_at))
            conn.commit()
            res_id = c.lastrowid
            conn.close()
        self.send_json(201, {
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        })

    def handle_confirm(self, res_id):
        clean_expired()
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.send_error(404, "Reservation not found")
                return
            status, item_id, qty = row
            if status != "pending":
                conn.close()
                self.send_error(400, "Reservation is not pending")
                return
            c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()
            conn.close()
        self.send_json(200, {"id": res_id, "status": "confirmed"})

    def handle_cancel(self, res_id):
        clean_expired()
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.send_error(404, "Reservation not found")
                return
            status, item_id, qty = row
            if status != "pending":
                conn.close()
                self.send_error(400, "Reservation is not pending")
                return
            c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            conn.commit()
            conn.close()
        self.send_json(200, {"id": res_id, "status": "cancelled"})

    def read_json(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except:
            return {}

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error(self, code, message):
        self.send_json(code, {"error": message})

    def log_message(self, format, *args):
        pass  # suppress logs


def run_server(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
```
````
