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
- Elapsed seconds: 12.585791
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2563, "completion_tokens": 2200, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2200
- Total tokens: 2563

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

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL CHECK(stock_total >= 0),
            stock_available INTEGER NOT NULL CHECK(stock_available >= 0)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed')),
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()

def cleanup_expired():
    """清理过期 pending 预约并释放库存"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    now = time.time()
    with LOCK:
        c.execute("BEGIN IMMEDIATE")
        expired = c.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
            (now,)
        ).fetchall()
        for res_id, item_id, qty in expired:
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
            c.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
        conn.commit()
    conn.close()

class InventoryHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status)

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length == 0:
                return None
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw)
        except Exception:
            return None

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

        if path == "/items":
            self._handle_post_items()
        elif path == "/reservations":
            self._handle_post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self._handle_confirm_reservation(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self._handle_cancel_reservation(res_id)
        else:
            self._send_error("Not Found", 404)

    def _handle_get_items(self):
        cleanup_expired()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT id, name, stock_total, stock_available FROM items")
        rows = c.fetchall()
        items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
        conn.close()
        self._send_json(items)

    def _handle_post_items(self):
        data = self._read_json()
        if not data or "name" not in data or "stock_total" not in data:
            self._send_error("name and stock_total are required")
            return
        name = data["name"].strip()
        try:
            total = int(data["stock_total"])
        except (ValueError, TypeError):
            self._send_error("stock_total must be integer")
            return
        if total < 0:
            self._send_error("stock_total must be >= 0")
            return
        item_id = str(uuid.uuid4())
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        with LOCK:
            try:
                c.execute("INSERT INTO items (id, name, stock_total, stock_available) VALUES (?, ?, ?, ?)",
                          (item_id, name, total, total))
                conn.commit()
            except sqlite3.IntegrityError:
                conn.close()
                self._send_error("Item creation failed", 500)
                return
        conn.close()
        self._send_json({"id": item_id, "name": name, "stock_total": total, "stock_available": total}, 201)

    def _handle_post_reservations(self):
        data = self._read_json()
        if not data or "item_id" not in data or "quantity" not in data or "ttl_seconds" not in data:
            self._send_error("item_id, quantity, ttl_seconds are required")
            return
        item_id = data["item_id"]
        try:
            quantity = int(data["quantity"])
            ttl = int(data["ttl_seconds"])
        except (ValueError, TypeError):
            self._send_error("quantity and ttl_seconds must be integers")
            return
        if quantity <= 0:
            self._send_error("quantity must be > 0")
            return
        if ttl <= 0:
            self._send_error("ttl_seconds must be > 0")
            return

        cleanup_expired()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        with LOCK:
            c.execute("BEGIN IMMEDIATE")
            item = c.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,)).fetchone()
            if not item:
                conn.commit()
                conn.close()
                self._send_error("Item not found", 404)
                return
            if item[1] < quantity:
                conn.commit()
                conn.close()
                self._send_error("Insufficient stock", 409)
                return
            res_id = str(uuid.uuid4())
            now = time.time()
            expires_at = now + ttl
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            c.execute(
                "INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                (res_id, item_id, quantity, expires_at, now)
            )
            conn.commit()
        conn.close()
        self._send_json({
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": now
        }, 201)

    def _handle_confirm_reservation(self, res_id):
        cleanup_expired()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        with LOCK:
            c.execute("BEGIN IMMEDIATE")
            res = c.execute("SELECT id, status FROM reservations WHERE id = ?", (res_id,)).fetchone()
            if not res:
                conn.commit()
                conn.close()
                self._send_error("Reservation not found", 404)
                return
            if res[1] != "pending":
                conn.commit()
                conn.close()
                self._send_error("Reservation is not in pending status", 400)
                return
            c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()
        conn.close()
        self._send_json({"id": res_id, "status": "confirmed"})

    def _handle_cancel_reservation(self, res_id):
        cleanup_expired()
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        with LOCK:
            c.execute("BEGIN IMMEDIATE")
            res = c.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,)).fetchone()
            if not res:
                conn.commit()
                conn.close()
                self._send_error("Reservation not found", 404)
                return
            if res[3] != "pending":
                conn.commit()
                conn.close()
                self._send_error("Reservation is not in pending status", 400)
                return
            # 释放库存
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (res[2], res[1]))
            c.execute("DELETE FROM reservations WHERE id = ?", (res_id,))
            conn.commit()
        conn.close()
        self._send_json({"id": res_id, "status": "cancelled"})

    def log_message(self, format, *args):
        # 抑制默认日志输出
        pass

def run_server(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == "__main__":
    init_db()
    run_server()
```
````
