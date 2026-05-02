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
- Elapsed seconds: 15.686281
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2556, "completion_tokens": 2193, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2193
- Total tokens: 2556

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

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL DEFAULT 0,
            stock_available INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        );
    """)
    conn.commit()
    conn.close()

class InventoryAPI(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        body = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def _parse_path(self):
        parsed = urlparse(self.path)
        return parsed.path, parse_qs(parsed.query)

    def _cleanup_expired(self, conn):
        now = datetime.utcnow().isoformat()
        expired = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
            (now,)
        ).fetchall()
        for row in expired:
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (row["quantity"], row["item_id"])
            )
            conn.execute(
                "UPDATE reservations SET status='cancelled' WHERE id = ?",
                (row["id"],)
            )
        conn.commit()

    def do_GET(self):
        path, _ = self._parse_path()
        if path == "/items":
            with LOCK:
                conn = get_db()
                self._cleanup_expired(conn)
                items = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
                conn.close()
            result = [{"id": i["id"], "name": i["name"], "stock_total": i["stock_total"], "stock_available": i["stock_available"]} for i in items]
            self._send_json(result)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path, _ = self._parse_path()
        data = self._read_json_body()

        if path == "/items":
            if not data or "name" not in data or "stock_total" not in data:
                self._send_json({"error": "Missing required fields: name, stock_total"}, 400)
                return
            name = data["name"]
            try:
                stock_total = int(data["stock_total"])
            except (ValueError, TypeError):
                self._send_json({"error": "stock_total must be an integer"}, 400)
                return
            if stock_total < 0:
                self._send_json({"error": "stock_total cannot be negative"}, 400)
                return
            with LOCK:
                conn = get_db()
                conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                item_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.close()
            self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

        elif path == "/reservations":
            if not data or "item_id" not in data or "quantity" not in data or "ttl_seconds" not in data:
                self._send_json({"error": "Missing required fields: item_id, quantity, ttl_seconds"}, 400)
                return
            try:
                item_id = int(data["item_id"])
                quantity = int(data["quantity"])
                ttl = int(data["ttl_seconds"])
            except (ValueError, TypeError):
                self._send_json({"error": "item_id, quantity, ttl_seconds must be integers"}, 400)
                return
            if quantity <= 0 or ttl <= 0:
                self._send_json({"error": "quantity and ttl_seconds must be positive"}, 400)
                return
            rid = str(uuid.uuid4())
            created_at = datetime.utcnow().isoformat()
            expires_at = (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
            with LOCK:
                conn = get_db()
                self._cleanup_expired(conn)
                item = conn.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,)).fetchone()
                if not item:
                    conn.close()
                    self._send_json({"error": "Item not found"}, 404)
                    return
                if item["stock_available"] < quantity:
                    conn.close()
                    self._send_json({"error": "Insufficient stock", "available": item["stock_available"]}, 409)
                    return
                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                    (quantity, item_id)
                )
                conn.execute(
                    "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                    (rid, item_id, quantity, expires_at, created_at)
                )
                conn.commit()
                conn.close()
            self._send_json({
                "id": rid,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": created_at
            }, 201)

        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            rid = path.split("/")[2]
            with LOCK:
                conn = get_db()
                self._cleanup_expired(conn)
                res = conn.execute("SELECT * FROM reservations WHERE id = ?", (rid,)).fetchone()
                if not res:
                    conn.close()
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                if res["status"] != "pending":
                    conn.close()
                    self._send_json({"error": f"Reservation already {res['status']}"}, 400)
                    return
                if res["expires_at"] <= datetime.utcnow().isoformat():
                    conn.close()
                    self._send_json({"error": "Reservation expired"}, 400)
                    return
                conn.execute("UPDATE reservations SET status='confirmed' WHERE id = ?", (rid,))
                conn.commit()
                conn.close()
            self._send_json({"id": rid, "status": "confirmed"})

        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            rid = path.split("/")[2]
            with LOCK:
                conn = get_db()
                self._cleanup_expired(conn)
                res = conn.execute("SELECT * FROM reservations WHERE id = ?", (rid,)).fetchone()
                if not res:
                    conn.close()
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                if res["status"] != "pending":
                    conn.close()
                    self._send_json({"error": f"Reservation already {res['status']}"}, 400)
                    return
                if res["expires_at"] <= datetime.utcnow().isoformat():
                    conn.close()
                    self._send_json({"error": "Reservation expired"}, 400)
                    return
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                    (res["quantity"], res["item_id"])
                )
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id = ?", (rid,))
                conn.commit()
                conn.close()
            self._send_json({"id": rid, "status": "cancelled"})

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_DELETE(self):
        self._send_json({"error": "Method not allowed"}, 405)

    def log_message(self, format, *args):
        pass

class ThreadedHTTPServer(HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def process_request(self, request, client_address):
        t = threading.Thread(target=self.process_request_thread, args=(request, client_address))
        t.daemon = True
        t.start()

    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)

if __name__ == "__main__":
    init_db()
    server = ThreadedHTTPServer(("127.0.0.1", 8080), InventoryAPI)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
        server.server_close()
```
````
