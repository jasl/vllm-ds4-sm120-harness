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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 7.536261
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2518, "completion_tokens": 2155, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2155
- Total tokens: 2518

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
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()


def cleanup_expired():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    expired = c.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
        (now,)
    ).fetchall()
    for res_id, item_id, qty in expired:
        c.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id))
    conn.commit()
    conn.close()
    return len(expired)


class InventoryHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            with LOCK:
                cleanup_expired()
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                rows = c.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
                conn.close()
            items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
            self._send_json(items)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        try:
            body = self._read_body()
        except (json.JSONDecodeError, TypeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        if path == "/items":
            self._handle_create_item(body)
        elif path == "/reservations":
            self._handle_create_reservation(body)
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self._handle_confirm(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self._handle_cancel(res_id)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _handle_create_item(self, body):
        if not body or "name" not in body or "stock_total" not in body:
            self._send_json({"error": "Missing name or stock_total"}, 400)
            return
        name = body["name"]
        try:
            total = int(body["stock_total"])
        except (ValueError, TypeError):
            self._send_json({"error": "stock_total must be integer"}, 400)
            return
        if total < 0:
            self._send_json({"error": "stock_total must be non-negative"}, 400)
            return
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                      (name, total, total))
            conn.commit()
            item_id = c.lastrowid
            conn.close()
        self._send_json({"id": item_id, "name": name, "stock_total": total, "stock_available": total}, 201)

    def _handle_create_reservation(self, body):
        if not body or "item_id" not in body or "quantity" not in body or "ttl_seconds" not in body:
            self._send_json({"error": "Missing item_id, quantity or ttl_seconds"}, 400)
            return
        try:
            item_id = int(body["item_id"])
            qty = int(body["quantity"])
            ttl = int(body["ttl_seconds"])
        except (ValueError, TypeError):
            self._send_json({"error": "Invalid parameter types"}, 400)
            return
        if qty <= 0:
            self._send_json({"error": "quantity must be positive"}, 400)
            return
        if ttl <= 0:
            self._send_json({"error": "ttl_seconds must be positive"}, 400)
            return
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            # Check item exists and has stock
            row = c.execute("SELECT id, stock_available FROM items WHERE id=?", (item_id,)).fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Item not found"}, 404)
                return
            available = row[1]
            if available < qty:
                conn.close()
                self._send_json({"error": "Insufficient stock"}, 409)
                return
            # Create reservation
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl)).isoformat()
            created_at = now.isoformat()
            c.execute(
                "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                (item_id, qty, expires_at, created_at)
            )
            reservation_id = c.lastrowid
            # Decrease available stock
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (qty, item_id))
            conn.commit()
            conn.close()
        self._send_json({
            "id": reservation_id,
            "item_id": item_id,
            "quantity": qty,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        }, 201)

    def _handle_confirm(self, res_id):
        try:
            res_id = int(res_id)
        except ValueError:
            self._send_json({"error": "Invalid reservation id"}, 400)
            return
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            row = c.execute("SELECT id, status FROM reservations WHERE id=?", (res_id,)).fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            if row[1] != "pending":
                conn.close()
                self._send_json({"error": f"Reservation is already {row[1]}"}, 400)
                return
            c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            conn.commit()
            conn.close()
        self._send_json({"message": "Reservation confirmed", "id": res_id})

    def _handle_cancel(self, res_id):
        try:
            res_id = int(res_id)
        except ValueError:
            self._send_json({"error": "Invalid reservation id"}, 400)
            return
        with LOCK:
            cleanup_expired()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            row = c.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id=?", (res_id,)).fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            if row[1] != "pending":
                conn.close()
                self._send_json({"error": f"Reservation is already {row[1]}"}, 400)
                return
            item_id = row[2]
            qty = row[3]
            c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (qty, item_id))
            conn.commit()
            conn.close()
        self._send_json({"message": "Reservation cancelled", "id": res_id})

    def log_message(self, format, *args):
        # Suppress default logging
        pass


def main():
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), InventoryHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
```
````
