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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.018661
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2658, "completion_tokens": 2295, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2295
- Total tokens: 2658

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
from uuid import uuid4

DB_PATH = "inventory.db"

# Thread lock for concurrency control
db_lock = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
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

def cleanup_expired():
    """Clean up expired pending reservations and release stock."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
            (now,)
        )
        expired = cursor.fetchall()
        for res_id, item_id, qty in expired:
            cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            cursor.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
        conn.commit()
    finally:
        conn.close()

class RequestHandler(BaseHTTPRequestHandler):
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
            parts = path.split("/")
            if len(parts) == 4:
                res_id = parts[2]
                self.handle_confirm_reservation(res_id)
            else:
                self.send_error(400, "Invalid reservation ID")
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4:
                res_id = parts[2]
                self.handle_cancel_reservation(res_id)
            else:
                self.send_error(400, "Invalid reservation ID")
        else:
            self.send_error(404, "Not Found")

    # ---------- Helper methods ----------
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error(self, status, message):
        self.send_json({"error": message}, status=status)

    def read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except json.JSONDecodeError:
            return None

    # ---------- API handlers ----------
    def handle_get_items(self):
        cleanup_expired()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = cursor.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": row[0],
                    "name": row[1],
                    "stock_total": row[2],
                    "stock_available": row[3]
                })
            self.send_json(items)
        finally:
            conn.close()

    def handle_post_items(self):
        data = self.read_json_body()
        if data is None:
            self.send_error(400, "Invalid JSON body")
            return
        name = data.get("name")
        stock_total = data.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self.send_error(400, "Missing or invalid fields: name (string), stock_total (non-negative integer)")
            return
        item_id = str(uuid4())
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO items (id, name, stock_total, stock_available) VALUES (?, ?, ?, ?)",
                (item_id, name, stock_total, stock_total)
            )
            conn.commit()
            self.send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, status=201)
        except sqlite3.IntegrityError:
            conn.rollback()
            self.send_error(409, "Item already exists")
        finally:
            conn.close()

    def handle_post_reservations(self):
        data = self.read_json_body()
        if data is None:
            self.send_error(400, "Invalid JSON body")
            return
        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds")
        if not item_id or not isinstance(quantity, int) or quantity <= 0 or not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            self.send_error(400, "Missing or invalid fields: item_id (string), quantity (positive integer), ttl_seconds (positive integer)")
            return
        cleanup_expired()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            with db_lock:
                cursor = conn.cursor()
                # Check item exists and has enough stock
                cursor.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
                row = cursor.fetchone()
                if not row:
                    self.send_error(404, "Item not found")
                    return
                stock_available = row[0]
                if stock_available < quantity:
                    self.send_error(409, "Insufficient stock")
                    return
                # Create reservation
                res_id = str(uuid4())
                now = datetime.utcnow()
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
                created_at = now.isoformat()
                cursor.execute(
                    "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                    (res_id, item_id, quantity, expires_at, created_at)
                )
                # Decrease available stock
                cursor.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
                conn.commit()
                self.send_json({
                    "id": res_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": created_at
                }, status=201)
        except Exception as e:
            conn.rollback()
            self.send_error(500, str(e))
        finally:
            conn.close()

    def handle_confirm_reservation(self, res_id):
        cleanup_expired()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            with db_lock:
                cursor = conn.cursor()
                cursor.execute("SELECT status FROM reservations WHERE id = ?", (res_id,))
                row = cursor.fetchone()
                if not row:
                    self.send_error(404, "Reservation not found")
                    return
                status = row[0]
                if status == "confirmed":
                    self.send_json({"message": "Already confirmed"})
                    return
                if status != "pending":
                    self.send_error(409, f"Cannot confirm reservation with status '{status}'")
                    return
                cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
                conn.commit()
                self.send_json({"message": "Reservation confirmed"})
        except Exception as e:
            conn.rollback()
            self.send_error(500, str(e))
        finally:
            conn.close()

    def handle_cancel_reservation(self, res_id):
        cleanup_expired()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        try:
            with db_lock:
                cursor = conn.cursor()
                cursor.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
                row = cursor.fetchone()
                if not row:
                    self.send_error(404, "Reservation not found")
                    return
                status, item_id, quantity = row
                if status == "cancelled":
                    self.send_json({"message": "Already cancelled"})
                    return
                if status == "confirmed":
                    self.send_error(409, "Cannot cancel a confirmed reservation")
                    return
                # Release stock and cancel
                cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (quantity, item_id))
                cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
                conn.commit()
                self.send_json({"message": "Reservation cancelled"})
        except Exception as e:
            conn.rollback()
            self.send_error(500, str(e))
        finally:
            conn.close()

    # Suppress default logging
    def log_message(self, format, *args):
        pass

def run(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

if __name__ == "__main__":
    run()
```
````
