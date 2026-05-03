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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 40.436267
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2937, "completion_tokens": 2574, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2574
- Total tokens: 2937

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
_lock = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    conn.execute("""
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


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def cleanup_expired():
    conn = get_db()
    try:
        now = datetime.utcnow().isoformat()
        conn.execute("BEGIN")
        expired = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
            (now,)
        ).fetchall()
        for res in expired:
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (res["quantity"], res["item_id"])
            )
            conn.execute(
                "UPDATE reservations SET status = 'expired' WHERE id = ?",
                (res["id"],)
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class InventoryHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _read_body(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return b""
        return self.rfile.read(content_len)

    def _parse_json(self):
        body = self._read_body()
        if not body:
            return None
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def _cleanup_and_acquire(self):
        cleanup_expired()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            with _lock:
                self._cleanup_and_acquire()
                conn = get_db()
                try:
                    rows = conn.execute(
                        "SELECT id, name, stock_total, stock_available FROM items"
                    ).fetchall()
                    items = [
                        {
                            "id": r["id"],
                            "name": r["name"],
                            "stock_total": r["stock_total"],
                            "stock_available": r["stock_available"]
                        }
                        for r in rows
                    ]
                    self._send_json(items)
                finally:
                    conn.close()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            with _lock:
                self._cleanup_and_acquire()
                body = self._parse_json()
                if not body or "name" not in body or "stock_total" not in body:
                    self._send_json({"error": "Missing required fields: name, stock_total"}, 400)
                    return
                name = str(body["name"])
                try:
                    stock_total = int(body["stock_total"])
                except (ValueError, TypeError):
                    self._send_json({"error": "stock_total must be integer"}, 400)
                    return
                if stock_total <= 0:
                    self._send_json({"error": "stock_total must be positive"}, 400)
                    return

                conn = get_db()
                try:
                    item_id = str(uuid.uuid4())
                    conn.execute(
                        "INSERT INTO items (id, name, stock_total, stock_available) VALUES (?, ?, ?, ?)",
                        (item_id, name, stock_total, stock_total)
                    )
                    conn.commit()
                    self._send_json({
                        "id": item_id,
                        "name": name,
                        "stock_total": stock_total,
                        "stock_available": stock_total
                    }, 201)
                except sqlite3.IntegrityError:
                    conn.rollback()
                    self._send_json({"error": "Item already exists"}, 409)
                finally:
                    conn.close()

        elif path == "/reservations":
            with _lock:
                self._cleanup_and_acquire()
                body = self._parse_json()
                if not body:
                    self._send_json({"error": "Invalid JSON body"}, 400)
                    return
                item_id = body.get("item_id")
                quantity = body.get("quantity")
                ttl_seconds = body.get("ttl_seconds")
                if not item_id or quantity is None or ttl_seconds is None:
                    self._send_json({"error": "Missing required fields: item_id, quantity, ttl_seconds"}, 400)
                    return
                try:
                    quantity = int(quantity)
                    ttl_seconds = int(ttl_seconds)
                except (ValueError, TypeError):
                    self._send_json({"error": "quantity and ttl_seconds must be integers"}, 400)
                    return
                if quantity <= 0 or ttl_seconds <= 0:
                    self._send_json({"error": "quantity and ttl_seconds must be positive"}, 400)
                    return

                conn = get_db()
                try:
                    conn.execute("BEGIN")
                    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
                    if not item:
                        conn.rollback()
                        self._send_json({"error": "Item not found"}, 404)
                        return

                    if item["stock_available"] < quantity:
                        conn.rollback()
                        self._send_json({"error": "Insufficient stock"}, 409)
                        return

                    reservation_id = str(uuid.uuid4())
                    now = datetime.utcnow()
                    expires_at = now + timedelta(seconds=ttl_seconds)

                    conn.execute(
                        "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                        (quantity, item_id)
                    )
                    conn.execute(
                        "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                        (reservation_id, item_id, quantity, expires_at.isoformat(), now.isoformat())
                    )
                    conn.commit()

                    self._send_json({
                        "id": reservation_id,
                        "item_id": item_id,
                        "quantity": quantity,
                        "status": "pending",
                        "expires_at": expires_at.isoformat(),
                        "created_at": now.isoformat()
                    }, 201)
                except sqlite3.Error:
                    conn.rollback()
                    self._send_json({"error": "Database error"}, 500)
                finally:
                    conn.close()

        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            parts = path.split("/")
            if len(parts) != 4:
                self._send_json({"error": "Bad request"}, 400)
                return
            reservation_id = parts[2]
            with _lock:
                self._cleanup_and_acquire()
                conn = get_db()
                try:
                    conn.execute("BEGIN")
                    res = conn.execute(
                        "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
                    ).fetchone()
                    if not res:
                        conn.rollback()
                        self._send_json({"error": "Reservation not found"}, 404)
                        return
                    if res["status"] != "pending":
                        conn.rollback()
                        self._send_json({"error": f"Reservation is {res['status']}, cannot confirm"}, 409)
                        return

                    now = datetime.utcnow()
                    expires_at = datetime.fromisoformat(res["expires_at"])
                    if now > expires_at:
                        conn.execute(
                            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                            (res["quantity"], res["item_id"])
                        )
                        conn.execute(
                            "UPDATE reservations SET status = 'expired' WHERE id = ?",
                            (reservation_id,)
                        )
                        conn.commit()
                        self._send_json({"error": "Reservation expired"}, 409)
                        return

                    conn.execute(
                        "UPDATE reservations SET status = 'confirmed' WHERE id = ?",
                        (reservation_id,)
                    )
                    conn.commit()
                    self._send_json({"message": "Reservation confirmed", "id": reservation_id})
                except sqlite3.Error:
                    conn.rollback()
                    self._send_json({"error": "Database error"}, 500)
                finally:
                    conn.close()

        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) != 4:
                self._send_json({"error": "Bad request"}, 400)
                return
            reservation_id = parts[2]
            with _lock:
                self._cleanup_and_acquire()
                conn = get_db()
                try:
                    conn.execute("BEGIN")
                    res = conn.execute(
                        "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
                    ).fetchone()
                    if not res:
                        conn.rollback()
                        self._send_json({"error": "Reservation not found"}, 404)
                        return
                    if res["status"] != "pending":
                        conn.rollback()
                        self._send_json({"error": f"Reservation is {res['status']}, cannot cancel"}, 409)
                        return

                    conn.execute(
                        "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                        (res["quantity"], res["item_id"])
                    )
                    conn.execute(
                        "UPDATE reservations SET status = 'cancelled' WHERE id = ?",
                        (reservation_id,)
                    )
                    conn.commit()
                    self._send_json({"message": "Reservation cancelled", "id": reservation_id})
                except sqlite3.Error:
                    conn.rollback()
                    self._send_json({"error": "Database error"}, 500)
                finally:
                    conn.close()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    init_db()
    run()
```
````
