# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 37.821201
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2772, "completion_tokens": 2409, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2409
- Total tokens: 2772

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

DB_FILE = "inventory.db"
_lock = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
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
            id TEXT PRIMARY KEY,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def cleanup_expired():
    """清理过期pending预约并释放库存"""
    with _lock:
        conn = get_db()
        try:
            cur = conn.cursor()
            now = time.time()
            cur.execute("""
                SELECT id, item_id, quantity FROM reservations
                WHERE status = 'pending' AND expires_at <= ?
            """, (now,))
            expired = cur.fetchall()
            for row in expired:
                cur.execute("""
                    UPDATE items SET stock_available = stock_available + ?
                    WHERE id = ?
                """, (row['quantity'], row['item_id']))
                cur.execute("""
                    DELETE FROM reservations WHERE id = ?
                """, (row['id'],))
            conn.commit()
        finally:
            conn.close()


def api_error(handler, code, message):
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps({"error": message}).encode())


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self.handle_get_items()
        else:
            api_error(self, 404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # 先清理过期预约
        cleanup_expired()

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
            api_error(self, 404, "Not found")

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        data = self.rfile.read(length)
        return json.loads(data.decode())

    def handle_get_items(self):
        cleanup_expired()
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = cur.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": row["id"],
                    "name": row["name"],
                    "stock_total": row["stock_total"],
                    "stock_available": row["stock_available"]
                })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(items).encode())
        finally:
            conn.close()

    def handle_post_items(self):
        try:
            body = self._read_json()
        except Exception:
            api_error(self, 400, "Invalid JSON")
            return

        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or stock_total is None:
            api_error(self, 400, "Missing name or stock_total")
            return
        if not isinstance(stock_total, int) or stock_total < 0:
            api_error(self, 400, "stock_total must be non-negative integer")
            return

        with _lock:
            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO items (name, stock_total, stock_available)
                    VALUES (?, ?, ?)
                """, (name, stock_total, stock_total))
                conn.commit()
                new_id = cur.lastrowid
                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "id": new_id,
                    "name": name,
                    "stock_total": stock_total,
                    "stock_available": stock_total
                }).encode())
            finally:
                conn.close()

    def handle_post_reservations(self):
        try:
            body = self._read_json()
        except Exception:
            api_error(self, 400, "Invalid JSON")
            return

        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds", 300)

        if not item_id or not quantity:
            api_error(self, 400, "Missing item_id or quantity")
            return
        if not isinstance(quantity, int) or quantity <= 0:
            api_error(self, 400, "quantity must be positive integer")
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            api_error(self, 400, "ttl_seconds must be positive")
            return

        with _lock:
            conn = get_db()
            try:
                cur = conn.cursor()
                # 检查商品是否存在且库存足够
                cur.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
                row = cur.fetchone()
                if not row:
                    api_error(self, 404, "Item not found")
                    return
                available = row["stock_available"]
                if available < quantity:
                    api_error(self, 409, "Insufficient stock")
                    return

                # 扣减库存，创建预约
                now = time.time()
                res_id = str(uuid.uuid4())
                expires_at = now + ttl_seconds
                cur.execute("""
                    UPDATE items SET stock_available = stock_available - ?
                    WHERE id = ?
                """, (quantity, item_id))
                cur.execute("""
                    INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
                    VALUES (?, ?, ?, 'pending', ?, ?)
                """, (res_id, item_id, quantity, expires_at, now))
                conn.commit()

                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "id": res_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": now
                }).encode())
            finally:
                conn.close()

    def _get_reservation_or_error(self, res_id):
        """获取预约记录，如果不存在返回None并发送错误"""
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM reservations WHERE id = ?", (res_id,))
            row = cur.fetchone()
            if not row:
                api_error(self, 404, "Reservation not found")
                return None, None
            return row, conn
        except:
            conn.close()
            return None, None

    def handle_confirm_reservation(self, res_id):
        with _lock:
            row, conn = self._get_reservation_or_error(res_id)
            if row is None:
                return
            try:
                cur = conn.cursor()
                if row["status"] != "pending":
                    api_error(self, 400, "Reservation is not pending")
                    return
                # 检查是否过期（虽然清理过但并发可能）
                if row["expires_at"] <= time.time():
                    # 已经过期，释放库存并删除
                    cur.execute("""
                        UPDATE items SET stock_available = stock_available + ?
                        WHERE id = ?
                    """, (row["quantity"], row["item_id"]))
                    cur.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
                    conn.commit()
                    api_error(self, 409, "Reservation expired")
                    return
                cur.execute("""
                    UPDATE reservations SET status = 'confirmed' WHERE id = ?
                """, (res_id,))
                conn.commit()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "id": row["id"],
                    "item_id": row["item_id"],
                    "quantity": row["quantity"],
                    "status": "confirmed",
                    "expires_at": row["expires_at"],
                    "created_at": row["created_at"]
                }).encode())
            finally:
                conn.close()

    def handle_cancel_reservation(self, res_id):
        with _lock:
            row, conn = self._get_reservation_or_error(res_id)
            if row is None:
                return
            try:
                cur = conn.cursor()
                if row["status"] != "pending":
                    api_error(self, 400, "Only pending reservations can be cancelled")
                    return
                # 释放库存
                cur.execute("""
                    UPDATE items SET stock_available = stock_available + ?
                    WHERE id = ?
                """, (row["quantity"], row["item_id"]))
                cur.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
                conn.commit()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Cancelled"}).encode())
            finally:
                conn.close()

    def log_message(self, format, *args):
        # 禁止输出日志，保持干净
        pass


def run_server(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    init_db()
    run_server()
```
````
