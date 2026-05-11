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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 22.434437
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2263, "completion_tokens": 1900, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 1900
- Total tokens: 2263

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
    c.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        );
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def clean_expired_reservations():
    conn = get_db()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    try:
        c.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?", (now,))
        expired = c.fetchall()
        for res in expired:
            c.execute("UPDATE reservations SET status='expired' WHERE id=?", (res["id"],))
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (res["quantity"], res["item_id"]))
        conn.commit()
    finally:
        conn.close()

class InventoryHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        return json.loads(body.decode("utf-8"))

    def _get_path_parts(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        return path.split("/")[1:]

    def do_GET(self):
        parts = self._get_path_parts()
        if parts == ["items"]:
            self._handle_get_items()
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parts = self._get_path_parts()
        if parts == ["items"]:
            self._handle_post_items()
        elif parts == ["reservations"]:
            self._handle_post_reservations()
        elif len(parts) == 3 and parts[0] == "reservations" and parts[2] == "confirm":
            self._handle_confirm_cancel(parts[1], "confirm")
        elif len(parts) == 3 and parts[0] == "reservations" and parts[2] == "cancel":
            self._handle_confirm_cancel(parts[1], "cancel")
        else:
            self._send_json({"error": "Not found"}, 404)

    def _handle_get_items(self):
        with LOCK:
            clean_expired_reservations()
            conn = get_db()
            try:
                c = conn.cursor()
                c.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [dict(row) for row in c.fetchall()]
                self._send_json({"items": items})
            finally:
                conn.close()

    def _handle_post_items(self):
        data = self._read_json()
        name = data.get("name")
        stock_total = data.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "Invalid parameters: name (string) and stock_total (non-negative int) required"}, 400)
            return
        item_id = str(uuid.uuid4())
        conn = get_db()
        try:
            c = conn.cursor()
            c.execute("INSERT INTO items (id, name, stock_total, stock_available) VALUES (?, ?, ?, ?)",
                      (item_id, name, stock_total, stock_total))
            conn.commit()
            self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
        except sqlite3.IntegrityError:
            conn.rollback()
            self._send_json({"error": "Item already exists"}, 409)
        finally:
            conn.close()

    def _handle_post_reservations(self):
        data = self._read_json()
        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds", 300)
        if not item_id or not isinstance(quantity, int) or quantity <= 0:
            self._send_json({"error": "Invalid parameters: item_id (string) and quantity (positive int) required"}, 400)
            return
        with LOCK:
            clean_expired_reservations()
            conn = get_db()
            try:
                c = conn.cursor()
                c.execute("SELECT id, stock_available FROM items WHERE id=?", (item_id,))
                item = c.fetchone()
                if not item:
                    self._send_json({"error": "Item not found"}, 404)
                    return
                if item["stock_available"] < quantity:
                    self._send_json({"error": "Insufficient stock"}, 409)
                    return
                # Create reservation
                res_id = str(uuid.uuid4())
                now = datetime.utcnow()
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
                created_at = now.isoformat()
                c.execute("INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                          (res_id, item_id, quantity, expires_at, created_at))
                c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
                conn.commit()
                self._send_json({"id": res_id, "item_id": item_id, "quantity": quantity, "status": "pending", "expires_at": expires_at, "created_at": created_at}, 201)
            except sqlite3.Error as e:
                conn.rollback()
                self._send_json({"error": str(e)}, 500)
            finally:
                conn.close()

    def _handle_confirm_cancel(self, res_id, action):
        with LOCK:
            clean_expired_reservations()
            conn = get_db()
            try:
                c = conn.cursor()
                c.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,))
                res = c.fetchone()
                if not res:
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                if res["status"] != "pending":
                    self._send_json({"error": f"Reservation already {res['status']}"}, 409)
                    return
                if action == "confirm":
                    c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
                else:  # cancel
                    c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                    c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (res["quantity"], res["item_id"]))
                conn.commit()
                self._send_json({"message": f"Reservation {action}ed successfully", "id": res_id})
            except sqlite3.Error as e:
                conn.rollback()
                self._send_json({"error": str(e)}, 500)
            finally:
                conn.close()

    def log_message(self, format, *args):
        pass  # Suppress default logging

def run_server(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    init_db()
    run_server()
```
````
