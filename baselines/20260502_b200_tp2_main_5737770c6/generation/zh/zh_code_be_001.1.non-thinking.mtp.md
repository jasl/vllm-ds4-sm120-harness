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
- Elapsed seconds: 7.744093
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2559, "completion_tokens": 2196, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2196
- Total tokens: 2559

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

DB_PATH = "inventory.db"
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

def cleanup_expired():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now_str = datetime.utcnow().isoformat()
    expired = c.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now_str,)).fetchall()
    for res_id, item_id, qty in expired:
        c.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id))
    conn.commit()
    conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body.decode("utf-8"))
        except:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/items":
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
            items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
            conn.close()
            self._send_json(items)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/items":
            self._handle_create_item()
        elif path == "/reservations":
            self._handle_create_reservation()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            parts = path.split("/")
            if len(parts) == 4:
                self._handle_confirm_reservation(int(parts[2]))
            else:
                self._send_json({"error": "Not Found"}, 404)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4:
                self._handle_cancel_reservation(int(parts[2]))
            else:
                self._send_json({"error": "Not Found"}, 404)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_create_item(self):
        data = self._read_body()
        name = data.get("name")
        stock_total = data.get("stock_total")
        if not name or stock_total is None:
            self._send_json({"error": "Missing required fields: name, stock_total"}, 400)
            return
        if not isinstance(name, str) or not isinstance(stock_total, int):
            self._send_json({"error": "Invalid types: name must be string, stock_total must be int"}, 400)
            return
        if stock_total < 0:
            self._send_json({"error": "stock_total must be non-negative"}, 400)
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name, stock_total, stock_total))
            conn.commit()
            item_id = c.lastrowid
            item = {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}
            self._send_json(item, 201)
        except sqlite3.IntegrityError:
            self._send_json({"error": "Item name already exists"}, 409)
        finally:
            conn.close()

    def _handle_create_reservation(self):
        data = self._read_body()
        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds", 300)

        if not item_id or not quantity:
            self._send_json({"error": "Missing required fields: item_id, quantity"}, 400)
            return
        if not isinstance(item_id, int) or not isinstance(quantity, int) or not isinstance(ttl_seconds, (int, float)):
            self._send_json({"error": "Invalid types"}, 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self._send_json({"error": "quantity and ttl_seconds must be positive"}, 400)
            return

        cleanup_expired()

        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            try:
                c.execute("SELECT stock_available, stock_total FROM items WHERE id=?", (item_id,))
                row = c.fetchone()
                if not row:
                    self._send_json({"error": "Item not found"}, 404)
                    conn.close()
                    return
                stock_avail = row[0]
                if stock_avail < quantity:
                    self._send_json({"error": "Insufficient stock"}, 409)
                    conn.close()
                    return

                now = datetime.utcnow()
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
                created_at = now.isoformat()
                c.execute("""INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                            VALUES (?, ?, 'pending', ?, ?)""",
                          (item_id, quantity, expires_at, created_at))
                res_id = c.lastrowid
                c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
                if c.rowcount == 0:
                    raise Exception("Stock update failed")
                conn.commit()
                reservation = {
                    "id": res_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": created_at
                }
                self._send_json(reservation, 201)
            except Exception as e:
                conn.rollback()
                self._send_json({"error": str(e)}, 500)
            finally:
                conn.close()

    def _handle_confirm_reservation(self, reservation_id):
        cleanup_expired()
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            try:
                c.execute("SELECT id, status FROM reservations WHERE id=?", (reservation_id,))
                row = c.fetchone()
                if not row:
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                if row[1] != "pending":
                    self._send_json({"error": "Reservation cannot be confirmed, status: " + row[1]}, 400)
                    return
                c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (reservation_id,))
                if c.rowcount == 0:
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                conn.commit()
                self._send_json({"message": "Reservation confirmed", "id": reservation_id})
            finally:
                conn.close()

    def _handle_cancel_reservation(self, reservation_id):
        cleanup_expired()
        with LOCK:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            try:
                c.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (reservation_id,))
                row = c.fetchone()
                if not row:
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                if row[3] != "pending":
                    self._send_json({"error": "Reservation cannot be cancelled, status: " + row[3]}, 400)
                    return
                item_id = row[1]
                quantity = row[2]
                c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (reservation_id,))
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
                conn.commit()
                self._send_json({"message": "Reservation cancelled", "id": reservation_id})
            finally:
                conn.close()

    def log_message(self, format, *args):
        pass

def run(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == "__main__":
    run()
```
````
