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
- Elapsed seconds: 17.31213
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2488, "completion_tokens": 2125, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2125
- Total tokens: 2488

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
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta


DB_PATH = "inventory.db"
LOCK = threading.Lock()


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
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
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    """)
    conn.commit()
    conn.close()


def cleanup_expired_pending():
    """清理过期 pending 预约，释放库存"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = time.time()
    cursor.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at <= ?
    """, (now,))
    expired = cursor.fetchall()
    for row in expired:
        cursor.execute("""
            UPDATE reservations SET status = 'expired' WHERE id = ?
        """, (row["id"],))
        cursor.execute("""
            UPDATE items SET stock_available = stock_available + ?
            WHERE id = ?
        """, (row["quantity"], row["item_id"]))
    conn.commit()
    conn.close()


class RequestHandler(BaseHTTPRequestHandler):
    error_message_format = "{}"
    server_version = "InventoryAPI/1.0"

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body.encode()))
        self.end_headers()
        self.wfile.write(body.encode())

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status)

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return None
        return json.loads(self.rfile.read(content_length))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            with LOCK:
                cleanup_expired_pending()
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [dict(row) for row in cursor.fetchall()]
                conn.close()
            self._send_json(items)
        else:
            self._send_error("Not Found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        # 解析路径参数
        path_parts = path.split("/")

        if path == "/items":
            self._handle_create_item()
        elif path == "/reservations":
            self._handle_create_reservation()
        elif len(path_parts) == 4 and path_parts[1] == "reservations" and path_parts[3] == "confirm":
            reservation_id = path_parts[2]
            self._handle_confirm_reservation(reservation_id)
        elif len(path_parts) == 4 and path_parts[1] == "reservations" and path_parts[3] == "cancel":
            reservation_id = path_parts[2]
            self._handle_cancel_reservation(reservation_id)
        else:
            self._send_error("Not Found", 404)

    def _handle_create_item(self):
        try:
            body = self._read_body()
            if not body:
                return self._send_error("Request body is required")
            name = body.get("name")
            stock_total = body.get("stock_total")
            if not name or stock_total is None:
                return self._send_error("name and stock_total are required")
            stock_total = int(stock_total)
            if stock_total < 0:
                return self._send_error("stock_total must be non-negative")
        except (ValueError, TypeError):
            return self._send_error("Invalid JSON or stock_total must be integer")

        with LOCK:
            cleanup_expired_pending()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                (name, stock_total, stock_total)
            )
            item_id = cursor.lastrowid
            conn.commit()
            conn.close()
        self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_create_reservation(self):
        try:
            body = self._read_body()
            if not body:
                return self._send_error("Request body is required")
            item_id = int(body.get("item_id"))
            quantity = int(body.get("quantity"))
            ttl_seconds = int(body.get("ttl_seconds"))
            if quantity <= 0 or ttl_seconds <= 0:
                return self._send_error("quantity and ttl_seconds must be positive")
        except (ValueError, TypeError):
            return self._send_error("Invalid JSON or parameters")

        with LOCK:
            cleanup_expired_pending()
            conn = get_db_connection()
            cursor = conn.cursor()
            # 检查商品是否存在并锁定行
            cursor.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
            if not item:
                conn.close()
                return self._send_error("Item not found", 404)
            if item["stock_available"] < quantity:
                conn.close()
                return self._send_error("Insufficient stock", 409)

            # 扣减库存
            cursor.execute(
                "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                (quantity, item_id)
            )
            now = time.time()
            expires_at = now + ttl_seconds
            cursor.execute(
                "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                (item_id, quantity, expires_at, now)
            )
            reservation_id = cursor.lastrowid
            conn.commit()
            conn.close()
        self._send_json({
            "id": reservation_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": now
        }, 201)

    def _handle_confirm_reservation(self, reservation_id):
        try:
            res_id = int(reservation_id)
        except ValueError:
            return self._send_error("Invalid reservation id")

        with LOCK:
            cleanup_expired_pending()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, status FROM reservations WHERE id = ?", (res_id,))
            reservation = cursor.fetchone()
            if not reservation:
                conn.close()
                return self._send_error("Reservation not found", 404)
            if reservation["status"] != "pending":
                conn.close()
                return self._send_error("Reservation is not in pending status", 400)

            cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()
            conn.close()
        self._send_json({"message": "Reservation confirmed", "id": res_id})

    def _handle_cancel_reservation(self, reservation_id):
        try:
            res_id = int(reservation_id)
        except ValueError:
            return self._send_error("Invalid reservation id")

        with LOCK:
            cleanup_expired_pending()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            reservation = cursor.fetchone()
            if not reservation:
                conn.close()
                return self._send_error("Reservation not found", 404)
            if reservation["status"] != "pending":
                conn.close()
                return self._send_error("Reservation is not in pending status", 400)

            # 释放库存
            cursor.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (reservation["quantity"], reservation["item_id"])
            )
            cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            conn.commit()
            conn.close()
        self._send_json({"message": "Reservation cancelled", "id": res_id})

    def log_message(self, format, *args):
        # 安静日志
        pass


def run_server(host="127.0.0.1", port=8080):
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server listening on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    run_server()
```
````
