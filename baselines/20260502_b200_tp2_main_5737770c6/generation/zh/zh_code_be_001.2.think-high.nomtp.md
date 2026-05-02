# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 16.966
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2453, "completion_tokens": 2090, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2090
- Total tokens: 2453

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


DB_PATH = "inventory.db"
_lock = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        );
        CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
        CREATE INDEX IF NOT EXISTS idx_reservations_expires ON reservations(expires_at);
    """)
    conn.commit()
    return conn


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def cleanup_expired(conn):
    now = time.time()
    expired_rows = conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
        (now,)
    ).fetchall()
    for row in expired_rows:
        conn.execute(
            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
            (row["quantity"], row["item_id"])
        )
        conn.execute(
            "UPDATE reservations SET status='expired' WHERE id = ?",
            (row["id"],)
        )
    conn.commit()


class InventoryHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # suppress default logging

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def _parse_path(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        return path, parsed.query

    def do_GET(self):
        path, _ = self._parse_path()
        if path == "/items":
            with _lock:
                conn = get_db()
                try:
                    cleanup_expired(conn)
                    rows = conn.execute(
                        "SELECT id, name, stock_total, stock_available FROM items"
                    ).fetchall()
                    result = [
                        {
                            "id": r["id"],
                            "name": r["name"],
                            "stock_total": r["stock_total"],
                            "stock_available": r["stock_available"]
                        }
                        for r in rows
                    ]
                    self._send_json(result)
                finally:
                    conn.close()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        path, _ = self._parse_path()
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        with _lock:
            conn = get_db()
            try:
                cleanup_expired(conn)

                if path == "/items":
                    self._handle_create_item(conn, body)
                elif path == "/reservations":
                    self._handle_create_reservation(conn, body)
                elif path.startswith("/reservations/") and path.endswith("/confirm"):
                    rid = path.split("/")[2]
                    self._handle_confirm(conn, rid)
                elif path.startswith("/reservations/") and path.endswith("/cancel"):
                    rid = path.split("/")[2]
                    self._handle_cancel(conn, rid)
                else:
                    self._send_json({"error": "Not Found"}, 404)
            except sqlite3.IntegrityError as e:
                self._send_json({"error": str(e)}, 409)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            finally:
                conn.close()

    def _handle_create_item(self, conn, body):
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "Invalid fields: name (string), stock_total (int >= 0)"}, 400)
            return
        try:
            cursor = conn.execute(
                "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                (name, stock_total, stock_total)
            )
            conn.commit()
            new_id = cursor.lastrowid
            self._send_json({"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
        except sqlite3.IntegrityError:
            self._send_json({"error": f"Item with name '{name}' already exists"}, 409)

    def _handle_create_reservation(self, conn, body):
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds", 300)

        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            self._send_json({"error": "Invalid fields: item_id (int), quantity (int > 0)"}, 400)
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_json({"error": "ttl_seconds must be positive number"}, 400)
            return

        item = conn.execute(
            "SELECT id, stock_available FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if not item:
            self._send_json({"error": "Item not found"}, 404)
            return

        if item["stock_available"] < quantity:
            self._send_json({"error": "Insufficient stock"}, 409)
            return

        now = time.time()
        rid = str(uuid.uuid4())
        expires_at = now + ttl_seconds

        conn.execute(
            "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
            (quantity, item_id)
        )
        conn.execute(
            "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
            (rid, item_id, quantity, expires_at, now)
        )
        conn.commit()
        self._send_json({
            "id": rid,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": now
        }, 201)

    def _handle_confirm(self, conn, rid):
        reservation = conn.execute(
            "SELECT id, status FROM reservations WHERE id = ?", (rid,)
        ).fetchone()
        if not reservation:
            self._send_json({"error": "Reservation not found"}, 404)
            return
        if reservation["status"] != "pending":
            self._send_json({"error": f"Reservation already {reservation['status']}"}, 409)
            return

        conn.execute(
            "UPDATE reservations SET status='confirmed' WHERE id = ?", (rid,)
        )
        conn.commit()
        self._send_json({"message": "Reservation confirmed", "id": rid})

    def _handle_cancel(self, conn, rid):
        reservation = conn.execute(
            "SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (rid,)
        ).fetchone()
        if not reservation:
            self._send_json({"error": "Reservation not found"}, 404)
            return
        if reservation["status"] != "pending":
            self._send_json({"error": f"Reservation already {reservation['status']}, cannot cancel"}, 409)
            return

        conn.execute(
            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
            (reservation["quantity"], reservation["item_id"])
        )
        conn.execute(
            "UPDATE reservations SET status='cancelled' WHERE id = ?", (rid,)
        )
        conn.commit()
        self._send_json({"message": "Reservation cancelled", "id": rid})


def run_server(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Inventory API server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    run_server()
```
````
