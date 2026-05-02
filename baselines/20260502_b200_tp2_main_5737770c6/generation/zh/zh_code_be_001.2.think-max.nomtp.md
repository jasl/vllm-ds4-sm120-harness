# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 19.871243
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2792, "completion_tokens": 2429, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2429
- Total tokens: 2792

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
from urllib.parse import urlparse
from datetime import datetime, timedelta

DB_PATH = "inventory.db"
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
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

def clean_expired_pending():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        now = datetime.utcnow().isoformat()
        conn.execute("BEGIN")
        expired = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status = 'pending' AND expires_at < ?",
            (now,)
        ).fetchall()
        for r in expired:
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (r['quantity'], r['item_id'])
            )
            conn.execute(
                "UPDATE reservations SET status = 'expired' WHERE id = ?",
                (r['id'],)
            )
        conn.commit()
    finally:
        conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/items':
            self._handle_get_items()
        else:
            self._send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        # 清理过期预约
        with LOCK:
            clean_expired_pending()

        if path == '/items':
            self._handle_post_items()
        elif path == '/reservations':
            self._handle_post_reservations()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            res_id = path.split('/')[2]
            self._handle_post_confirm(res_id)
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            res_id = path.split('/')[2]
            self._handle_post_cancel(res_id)
        else:
            self._send_error(404, "Not Found")

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, status, msg):
        self._send_json({"error": msg}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _get_conn(self):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    # ---- GET /items ----
    def _handle_get_items(self):
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
            items = [{
                "id": r["id"],
                "name": r["name"],
                "stock_total": r["stock_total"],
                "stock_available": r["stock_available"]
            } for r in rows]
            self._send_json(items)
        finally:
            conn.close()

    # ---- POST /items ----
    def _handle_post_items(self):
        body = self._read_body()
        name = body.get("name")
        stock_total = body.get("stock_total")

        if not name or not isinstance(name, str) or not name.strip():
            self._send_error(400, "Invalid or missing 'name'")
            return
        if not isinstance(stock_total, int) or stock_total < 0:
            self._send_error(400, "Invalid or missing 'stock_total', must be non-negative integer")
            return

        conn = self._get_conn()
        try:
            conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                         (name.strip(), stock_total, stock_total))
            conn.commit()
            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            self._send_json({"id": new_id, "name": name.strip(), "stock_total": stock_total, "stock_available": stock_total}, 201)
        except sqlite3.IntegrityError:
            conn.rollback()
            self._send_error(409, f"Item with name '{name}' already exists")
        finally:
            conn.close()

    # ---- POST /reservations ----
    def _handle_post_reservations(self):
        body = self._read_body()
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds", 300)

        if not isinstance(item_id, int) or item_id < 0:
            self._send_error(400, "Invalid or missing 'item_id'")
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_error(400, "Invalid or missing 'quantity', must be positive integer")
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_error(400, "Invalid 'ttl_seconds', must be positive number")
            return

        conn = self._get_conn()
        try:
            conn.execute("BEGIN")
            # 锁定商品行
            item = conn.execute("SELECT id, stock_available FROM items WHERE id = ? FOR UPDATE", (item_id,)).fetchone()
            if not item:
                conn.rollback()
                self._send_error(404, "Item not found")
                return

            if item["stock_available"] < quantity:
                conn.rollback()
                self._send_error(409, "Insufficient stock")
                return

            now = datetime.utcnow()
            expires_at = now + timedelta(seconds=ttl_seconds)
            now_str = now.isoformat()
            expires_str = expires_at.isoformat()

            conn.execute(
                "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                (item_id, quantity, expires_str, now_str)
            )
            conn.execute(
                "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                (quantity, item_id)
            )
            conn.commit()

            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            self._send_json({
                "id": new_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_str,
                "created_at": now_str
            }, 201)
        finally:
            conn.close()

    # ---- POST /reservations/{id}/confirm ----
    def _handle_post_confirm(self, res_id):
        try:
            res_id = int(res_id)
        except (ValueError, TypeError):
            self._send_error(400, "Invalid reservation ID")
            return

        conn = self._get_conn()
        try:
            conn.execute("BEGIN")
            res = conn.execute(
                "SELECT id, status, item_id, quantity FROM reservations WHERE id = ? FOR UPDATE", (res_id,)
            ).fetchone()
            if not res:
                conn.rollback()
                self._send_error(404, "Reservation not found")
                return
            if res["status"] != "pending":
                conn.rollback()
                self._send_error(409, f"Reservation already {res['status']}")
                return
            # 确认不释放库存
            conn.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()
            self._send_json({"message": "Confirmed", "id": res_id, "status": "confirmed"})
        finally:
            conn.close()

    # ---- POST /reservations/{id}/cancel ----
    def _handle_post_cancel(self, res_id):
        try:
            res_id = int(res_id)
        except (ValueError, TypeError):
            self._send_error(400, "Invalid reservation ID")
            return

        conn = self._get_conn()
        try:
            conn.execute("BEGIN")
            res = conn.execute(
                "SELECT id, status, item_id, quantity FROM reservations WHERE id = ? FOR UPDATE", (res_id,)
            ).fetchone()
            if not res:
                conn.rollback()
                self._send_error(404, "Reservation not found")
                return
            if res["status"] != "pending":
                conn.rollback()
                self._send_error(409, f"Reservation already {res['status']}")
                return
            # 释放库存
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (res["quantity"], res["item_id"])
            )
            conn.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            conn.commit()
            self._send_json({"message": "Cancelled", "id": res_id, "status": "cancelled"})
        finally:
            conn.close()

    def log_message(self, format, *args):
        # 静默日志，可通过标准输出观察
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")

def run_server(host='127.0.0.1', port=8080):
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    init_db()
    run_server()
```
````
