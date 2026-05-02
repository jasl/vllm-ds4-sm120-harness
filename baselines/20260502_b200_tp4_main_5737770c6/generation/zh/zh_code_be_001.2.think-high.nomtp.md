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
- Elapsed seconds: 15.733764
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2565, "completion_tokens": 2202, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2202
- Total tokens: 2565

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
import sqlite3
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_PATH = "inventory.db"
lock = threading.Lock()


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()


def cleanup_expired():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status='pending' AND expires_at < ?
    """, (now,))
    expired = cursor.fetchall()
    for res_id, item_id, qty in expired:
        cursor.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
        cursor.execute("""
            UPDATE items SET stock_available = stock_available + ?
            WHERE id = ?
        """, (qty, item_id))
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
        return self.rfile.read(length).decode() if length else ""

    def _parse_json_body(self):
        try:
            return json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            return None

    def _get_path_parts(self):
        path = urlparse(self.path).path.strip("/").split("/")
        return [p for p in path if p]

    def do_GET(self):
        parts = self._get_path_parts()
        if parts == ["items"]:
            self._handle_get_items()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        with lock:
            cleanup_expired()
            parts = self._get_path_parts()
            if parts == ["items"]:
                self._handle_create_item()
            elif parts == ["reservations"]:
                self._handle_create_reservation()
            elif len(parts) == 3 and parts[0] == "reservations" and parts[2] == "confirm":
                self._handle_confirm_reservation(parts[1])
            elif len(parts) == 3 and parts[0] == "reservations" and parts[2] == "cancel":
                self._handle_cancel_reservation(parts[1])
            else:
                self._send_json({"error": "Not Found"}, 404)

    def _handle_get_items(self):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
        rows = cursor.fetchall()
        items = [
            {"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]}
            for r in rows
        ]
        conn.close()
        self._send_json(items)

    def _handle_create_item(self):
        body = self._parse_json_body()
        if not body or "name" not in body or "stock_total" not in body:
            self._send_json({"error": "Missing required fields: name, stock_total"}, 400)
            return
        name = body["name"]
        try:
            stock_total = int(body["stock_total"])
        except (ValueError, TypeError):
            self._send_json({"error": "stock_total must be integer"}, 400)
            return
        if stock_total < 0:
            self._send_json({"error": "stock_total must be non-negative"}, 400)
            return
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
            (name, stock_total, stock_total)
        )
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_create_reservation(self):
        body = self._parse_json_body()
        if not body or "item_id" not in body or "quantity" not in body or "ttl_seconds" not in body:
            self._send_json({"error": "Missing required fields: item_id, quantity, ttl_seconds"}, 400)
            return
        try:
            item_id = int(body["item_id"])
            quantity = int(body["quantity"])
            ttl_seconds = int(body["ttl_seconds"])
        except (ValueError, TypeError):
            self._send_json({"error": "item_id, quantity, ttl_seconds must be integers"}, 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self._send_json({"error": "quantity and ttl_seconds must be positive"}, 400)
            return

        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            self._send_json({"error": "Item not found"}, 404)
            return
        if row[0] < quantity:
            conn.close()
            self._send_json({"error": "Insufficient stock"}, 409)
            return

        now = datetime.utcnow()
        expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
        created_at = now.isoformat()
        cursor.execute("""
            INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
            VALUES (?, ?, 'pending', ?, ?)
        """, (item_id, quantity, expires_at, created_at))
        cursor.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
        conn.commit()
        res_id = cursor.lastrowid
        conn.close()
        self._send_json({
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": created_at
        }, 201)

    def _handle_confirm_reservation(self, res_id_str):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        try:
            res_id = int(res_id_str)
        except ValueError:
            conn.close()
            self._send_json({"error": "Invalid reservation ID"}, 400)
            return
        cursor.execute("SELECT id, status FROM reservations WHERE id=?", (res_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            self._send_json({"error": "Reservation not found"}, 404)
            return
        if row[1] != "pending":
            conn.close()
            self._send_json({"error": f"Reservation is already {row[1]}"}, 400)
            return
        cursor.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
        conn.commit()
        conn.close()
        self._send_json({"message": "Reservation confirmed", "id": res_id})

    def _handle_cancel_reservation(self, res_id_str):
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        try:
            res_id = int(res_id_str)
        except ValueError:
            conn.close()
            self._send_json({"error": "Invalid reservation ID"}, 400)
            return
        cursor.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            self._send_json({"error": "Reservation not found"}, 404)
            return
        if row[3] != "pending":
            conn.close()
            self._send_json({"error": f"Cannot cancel reservation with status {row[3]}"}, 400)
            return
        item_id = row[1]
        quantity = row[2]
        cursor.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
        cursor.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
        conn.commit()
        conn.close()
        self._send_json({"message": "Reservation cancelled", "id": res_id})

    def log_message(self, format, *args):
        pass


def run_server(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    run_server()
```
````
