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
- Elapsed seconds: 7.256948
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2467, "completion_tokens": 2104, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2104
- Total tokens: 2467

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
import cgi
import time
import re
from urllib.parse import urlparse, parse_qs

DB_PATH = "inventory.db"
db_lock = threading.Lock()

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
                  expires_at REAL NOT NULL,
                  created_at REAL NOT NULL,
                  FOREIGN KEY(item_id) REFERENCES items(id))''')
    conn.commit()
    return conn

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def cleanup_expired():
    conn = get_db()
    try:
        with db_lock:
            c = conn.cursor()
            now = time.time()
            expired = c.execute(
                "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
                (now,)
            ).fetchall()
            for res in expired:
                rid, item_id, qty = res
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                          (qty, item_id))
                c.execute("UPDATE reservations SET status='expired' WHERE id = ?", (rid,))
            conn.commit()
    finally:
        conn.close()

class APIHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def _send_json(self, data, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status)

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self._handle_get_items()
        else:
            self._send_error("Not Found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # 先清理过期预约
        cleanup_expired()

        if path == "/items":
            self._handle_post_items()
        elif path == "/reservations":
            self._handle_post_reservations()
        elif m := re.match(r"/reservations/(\d+)/confirm", path):
            self._handle_post_confirm(int(m.group(1)))
        elif m := re.match(r"/reservations/(\d+)/cancel", path):
            self._handle_post_cancel(int(m.group(1)))
        else:
            self._send_error("Not Found", 404)

    # --- GET /items ---
    def _handle_get_items(self):
        conn = get_db()
        try:
            c = conn.cursor()
            c.execute("SELECT id, name, stock_total, stock_available FROM items")
            items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]}
                     for row in c.fetchall()]
            self._send_json(items)
        finally:
            conn.close()

    # --- POST /items ---
    def _handle_post_items(self):
        data = self._read_body()
        name = data.get("name")
        stock_total = data.get("stock_total")

        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self._send_error("Invalid parameters: name and stock_total (int >=0) required")
            return

        conn = get_db()
        try:
            with db_lock:
                c = conn.cursor()
                c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                          (name, stock_total, stock_total))
                conn.commit()
                item_id = c.lastrowid
            self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
        finally:
            conn.close()

    # --- POST /reservations ---
    def _handle_post_reservations(self):
        data = self._read_body()
        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds")

        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            self._send_error("Invalid parameters: item_id (int), quantity (int >0) required")
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_error("Invalid ttl_seconds (positive number)")
            return

        conn = get_db()
        try:
            with db_lock:
                c = conn.cursor()
                c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
                row = c.fetchone()
                if not row:
                    self._send_error("Item not found", 404)
                    return
                stock_avail = row[0]
                if stock_avail < quantity:
                    self._send_error("Insufficient stock", 409)
                    return

                now = time.time()
                expires_at = now + ttl_seconds
                c.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at, now)
                )
                c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                          (quantity, item_id))
                conn.commit()
                res_id = c.lastrowid
            self._send_json({
                "id": res_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": now
            }, 201)
        finally:
            conn.close()

    # --- POST /reservations/{id}/confirm ---
    def _handle_post_confirm(self, reservation_id):
        conn = get_db()
        try:
            with db_lock:
                c = conn.cursor()
                c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
                row = c.fetchone()
                if not row:
                    self._send_error("Reservation not found", 404)
                    return
                status, item_id, qty = row
                if status == "confirmed":
                    self._send_error("Already confirmed", 400)
                    return
                if status == "expired":
                    self._send_error("Reservation expired", 410)
                    return
                if status == "cancelled":
                    self._send_error("Already cancelled", 400)
                    return
                # status == 'pending'
                c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (reservation_id,))
                conn.commit()
            self._send_json({"id": reservation_id, "status": "confirmed"})
        finally:
            conn.close()

    # --- POST /reservations/{id}/cancel ---
    def _handle_post_cancel(self, reservation_id):
        conn = get_db()
        try:
            with db_lock:
                c = conn.cursor()
                c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
                row = c.fetchone()
                if not row:
                    self._send_error("Reservation not found", 404)
                    return
                status, item_id, qty = row
                if status == "cancelled":
                    self._send_error("Already cancelled", 400)
                    return
                if status == "expired":
                    self._send_error("Reservation expired", 410)
                    return
                if status == "confirmed":
                    # 已确认预约不能取消（释放库存会破坏数据一致性）
                    self._send_error("Cannot cancel confirmed reservation", 400)
                    return
                # status == 'pending'
                c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (reservation_id,))
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                          (qty, item_id))
                conn.commit()
            self._send_json({"id": reservation_id, "status": "cancelled"})
        finally:
            conn.close()

    def log_message(self, format, *args):
        # 抑制日志输出
        pass

def run_server(host="127.0.0.1", port=8080):
    init_db()
    server = http.server.HTTPServer((host, port), APIHandler)
    print(f"Server running on {host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
```
````
