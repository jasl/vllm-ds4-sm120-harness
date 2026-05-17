# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 11.546
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2584, "completion_tokens": 2221, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2221
- Total tokens: 2584

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
from urllib.parse import urlparse, parse_qs


DB_PATH = "inventory.db"
LOCK = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
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
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at < ?
    """, (now,))
    expired = c.fetchall()
    for res_id, item_id, qty in expired:
        c.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
        c.execute("""
            UPDATE items SET stock_available = stock_available + ?
            WHERE id = ?
        """, (qty, item_id))
    conn.commit()
    conn.close()


class InventoryAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self.handle_get_items()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self.handle_post_items()
        elif path == "/reservations":
            self.handle_post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self.handle_confirm_reservation(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self.handle_cancel_reservation(res_id)
        else:
            self.send_error(404, "Not Found")

    def handle_get_items(self):
        with LOCK:
            clean_expired_reservations()
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = c.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": row[0],
                    "name": row[1],
                    "stock_total": row[2],
                    "stock_available": row[3]
                })
            conn.close()
        self.send_json(200, items)

    def handle_post_items(self):
        body = self.read_body()
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or stock_total is None:
            self.send_error(400, "name and stock_total are required")
            return
        try:
            stock_total = int(stock_total)
        except:
            self.send_error(400, "stock_total must be integer")
            return
        if stock_total < 0:
            self.send_error(400, "stock_total must be non-negative")
            return

        item_id = str(uuid.uuid4())
        with LOCK:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO items (id, name, stock_total, stock_available)
                    VALUES (?, ?, ?, ?)
                """, (item_id, name, stock_total, stock_total))
                conn.commit()
                self.send_json(201, {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total})
            except sqlite3.IntegrityError:
                conn.rollback()
                self.send_error(500, "Internal error")
            finally:
                conn.close()

    def handle_post_reservations(self):
        body = self.read_body()
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds", 300)
        if not item_id or quantity is None:
            self.send_error(400, "item_id and quantity are required")
            return
        try:
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except:
            self.send_error(400, "quantity and ttl_seconds must be integers")
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self.send_error(400, "quantity and ttl_seconds must be positive")
            return

        with LOCK:
            clean_expired_reservations()
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.send_error(404, "Item not found")
                return
            if row[0] < quantity:
                conn.close()
                self.send_error(409, "Insufficient stock")
                return

            res_id = str(uuid.uuid4())
            created_at = datetime.utcnow().isoformat()
            expires_at = (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()
            try:
                c.execute("""
                    INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
                    VALUES (?, ?, ?, 'pending', ?, ?)
                """, (res_id, item_id, quantity, expires_at, created_at))
                c.execute("""
                    UPDATE items SET stock_available = stock_available - ?
                    WHERE id = ?
                """, (quantity, item_id))
                conn.commit()
                self.send_json(201, {
                    "id": res_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": created_at
                })
            except Exception as e:
                conn.rollback()
                self.send_error(500, str(e))
            finally:
                conn.close()

    def handle_confirm_reservation(self, res_id):
        with LOCK:
            clean_expired_reservations()
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT status FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.send_error(404, "Reservation not found")
                return
            if row[0] != "pending":
                conn.close()
                self.send_error(400, "Reservation is not pending")
                return

            try:
                c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
                conn.commit()
                self.send_json(200, {"status": "confirmed"})
            except Exception as e:
                conn.rollback()
                self.send_error(500, str(e))
            finally:
                conn.close()

    def handle_cancel_reservation(self, res_id):
        with LOCK:
            clean_expired_reservations()
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self.send_error(404, "Reservation not found")
                return
            status, item_id, quantity = row
            if status != "pending":
                conn.close()
                self.send_error(400, "Reservation is not pending")
                return

            try:
                c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
                c.execute("""
                    UPDATE items SET stock_available = stock_available + ?
                    WHERE id = ?
                """, (quantity, item_id))
                conn.commit()
                self.send_json(200, {"status": "cancelled"})
            except Exception as e:
                conn.rollback()
                self.send_error(500, str(e))
            finally:
                conn.close()

    def read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except:
            return {}

    def send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def run_server(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), InventoryAPIHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    init_db()
    run_server()
```
````
