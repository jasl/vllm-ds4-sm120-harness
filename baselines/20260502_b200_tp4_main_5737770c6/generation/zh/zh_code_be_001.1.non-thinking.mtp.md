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
- Elapsed seconds: 7.835181
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2670, "completion_tokens": 2307, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2307
- Total tokens: 2670

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

DB_FILE = "inventory.db"
LOCK = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()


def cleanup_expired():
    """清理过期 pending 预约并释放库存"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    with LOCK:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("""
            SELECT id, item_id, quantity FROM reservations
            WHERE status = 'pending' AND expires_at < ?
        """, (now,))
        expired = cursor.fetchall()
        for res_id, item_id, qty in expired:
            cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            cursor.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
        conn.commit()
    conn.close()


class InventoryHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            cleanup_expired()
            conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            cursor = conn.cursor()
            with LOCK:
                cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in cursor.fetchall()]
            conn.close()
            self._send_json(items)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        # 每次POST前清理过期预约
        cleanup_expired()

        if path == "/items":
            self._handle_create_item(body)
        elif path == "/reservations":
            self._handle_create_reservation(body)
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            parts = path.split("/")
            if len(parts) == 4:
                try:
                    res_id = int(parts[2])
                except ValueError:
                    self._send_json({"error": "Invalid reservation ID"}, 400)
                    return
                self._handle_confirm_reservation(res_id)
            else:
                self._send_json({"error": "Not found"}, 404)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4:
                try:
                    res_id = int(parts[2])
                except ValueError:
                    self._send_json({"error": "Invalid reservation ID"}, 400)
                    return
                self._handle_cancel_reservation(res_id)
            else:
                self._send_json({"error": "Not found"}, 404)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _handle_create_item(self, body):
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or stock_total is None or not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "Invalid parameters: name (str) and stock_total (int >=0) required"}, 400)
            return
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        with LOCK:
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                           (name, stock_total, stock_total))
            item_id = cursor.lastrowid
            conn.commit()
        conn.close()
        self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_create_reservation(self, body):
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if not all([item_id, quantity, ttl_seconds is not None]) or not isinstance(quantity, int) or not isinstance(ttl_seconds, int) or quantity <= 0 or ttl_seconds <= 0:
            self._send_json({"error": "Invalid parameters: item_id (int), quantity (int >0), ttl_seconds (int >0) required"}, 400)
            return
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        try:
            with LOCK:
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
                row = cursor.fetchone()
                if not row:
                    conn.rollback()
                    self._send_json({"error": "Item not found"}, 404)
                    return
                available = row[0]
                if available < quantity:
                    conn.rollback()
                    self._send_json({"error": "Insufficient stock"}, 409)
                    return
                now = datetime.utcnow()
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
                created_at = now.isoformat()
                cursor.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
                cursor.execute("""
                    INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                    VALUES (?, ?, 'pending', ?, ?)
                """, (item_id, quantity, expires_at, created_at))
                res_id = cursor.lastrowid
                conn.commit()
            conn.close()
            self._send_json({
                "id": res_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": created_at
            }, 201)
        except sqlite3.Error:
            conn.rollback()
            conn.close()
            self._send_json({"error": "Database error"}, 500)

    def _handle_confirm_reservation(self, res_id):
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        with LOCK:
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("SELECT status FROM reservations WHERE id = ?", (res_id,))
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            if row[0] != "pending":
                conn.rollback()
                conn.close()
                self._send_json({"error": f"Reservation is already {row[0]}"}, 400)
                return
            now = datetime.utcnow().isoformat()
            cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()
        conn.close()
        self._send_json({"message": "Reservation confirmed", "id": res_id})

    def _handle_cancel_reservation(self, res_id):
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()
        with LOCK:
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, qty = row
            if status != "pending":
                conn.rollback()
                conn.close()
                self._send_json({"error": f"Reservation is already {status}"}, 400)
                return
            cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            conn.commit()
        conn.close()
        self._send_json({"message": "Reservation cancelled", "id": res_id})

    def do_DELETE(self):
        self._send_json({"error": "Method not allowed"}, 405)

    def do_PUT(self):
        self._send_json({"error": "Method not allowed"}, 405)

    def log_message(self, format, *args):
        pass  # 静默日志


if __name__ == "__main__":
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), InventoryHandler)
    print("Starting inventory server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
```
````
