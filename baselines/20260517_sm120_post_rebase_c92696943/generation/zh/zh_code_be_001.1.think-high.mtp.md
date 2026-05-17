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
- Elapsed seconds: 17.758356
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 3558, "completion_tokens": 3195, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 3195
- Total tokens: 3558

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

## Reasoning Content

```text
我们被要求编写一个单文件 HTTP API 服务，使用 Python 3 标准库。不能使用第三方库如 Flask/FastAPI/Django。需要实现一个库存预约服务，使用 sqlite3 持久化。API 端点：GET /items, POST /items, POST /reservations, POST /reservations/{id}/confirm, POST /reservations/{id}/cancel。每次请求前清理过期 pending 预约。要处理并发，使用事务和线程锁。返回 JSON，错误响应包含 error 字段。监听 127.0.0.1:8080。总代码不超过1000行。

我们使用 http.server 模块中的 HTTPServer 和 BaseHTTPRequestHandler。需要自己解析路径和方法，处理 JSON。使用线程锁（threading.Lock）来保证并发一致性。使用 sqlite3，注意连接是线程安全的吗？SQLite3 连接默认是线程安全的，但建议每个线程使用自己的连接，或者使用锁来保护共享连接。为了简单，我们可以使用一个全局连接和锁，或者每个请求创建新连接（但可能较慢）。这里使用一个全局连接，并使用 threading.Lock 保护所有数据库操作。

我们需要：

- 数据库初始化：创建 items 和 reservations 表，如果不存在。
- 清理过期 pending 预约的函数。
- 每个请求处理前调用清理函数。
- 实现各个端点。

注意：POST /items 需要 name 和 stock_total，stock_available 设为 stock_total（初始可用）。
POST /reservations 需要 item_id, quantity, ttl_seconds。创建一条 pending 预约，expires_at = now + ttl_seconds。需要检查库存是否足够（stock_available >= quantity），如果不够返回409。同时减少 stock_available。
POST /reservations/{id}/confirm：将 status 改为 confirmed，但不释放库存（实际上库存已在预约时扣减，确认只是标记）。
POST /reservations/{id}/cancel：将 status 改为 cancelled，并释放库存（增加 stock_available）。如果预约已经是 confirmed 或 cancelled，应该返回错误？题目没说，但通常取消只能取消 pending 状态。我们处理：只有 pending 可以取消。确认也一样，只有 pending 可以确认。
另外，清理时只释放 pending 过期的预约。

并发控制：对于每个涉及到多个 SQL 语句的操作（如创建预约需要检查库存并更新），需要使用事务，并且需要锁来确保原子性。我们可以使用数据库事务加锁，但 sqlite3 在事务中会自动锁定，但并发写可能仍需要外部锁来防止多个线程同时操作。最简单的做法：使用全局锁 threading.Lock，在每个请求处理开始时获取锁，处理完释放。但这会降低并发性能，但可以保证一致性。对于简单服务足够了。

注意：清理过期预约也需要锁。

因为要求正确性，我们使用锁。

代码组织：定义一个类继承 BaseHTTPRequestHandler，重写 do_GET 和 do_POST。根据路径和方法分发。解析路径使用 urllib.parse。请求体读取并解析 JSON。响应写入 JSON。

还需要处理路径参数：如 /reservations/123/confirm。可以用正则或简单拆分。

我们还需要处理异常情况，例如 JSON 解析失败，返回 400。

输出：只输出代码，不要解释。

开始编写代码。
```

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""
小型库存预约 HTTP API 服务
使用 Python 3 标准库，sqlite3 持久化，threading.Lock 保证并发一致性
"""

import json
import sqlite3
import threading
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = "inventory.db"
LISTEN_HOST = "127.0.0.1"
LISTEN_PORT = 8080

# 全局数据库连接和锁
_db_lock = threading.Lock()
_db_connection = None


def get_db_connection():
    """获取全局数据库连接（线程安全地初始化）"""
    global _db_connection
    if _db_connection is None:
        with _db_lock:
            if _db_connection is None:
                _db_connection = sqlite3.connect(DB_PATH, check_same_thread=False)
                _db_connection.row_factory = sqlite3.Row
                _db_connection.execute("PRAGMA journal_mode=WAL")  # 提高并发
    return _db_connection


def init_database():
    """创建表（如果不存在）"""
    conn = get_db_connection()
    with _db_lock:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            )
        """)
        conn.execute("""
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


def cleanup_expired_reservations():
    """清理所有已过期的 pending 预约，释放库存"""
    conn = get_db_connection()
    now = datetime.now(timezone.utc).isoformat()
    with _db_lock:
        # 找出过期预约
        expired = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status = 'pending' AND expires_at < ?",
            (now,)
        ).fetchall()
        if not expired:
            return
        # 逐个释放库存并将状态设为 'expired'
        for res in expired:
            rid, item_id, quantity = res
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (quantity, item_id)
            )
            conn.execute(
                "UPDATE reservations SET status = 'expired' WHERE id = ?",
                (rid,)
            )
        conn.commit()


def parse_json_body(handler):
    """读取并解析请求体中的 JSON"""
    content_length = int(handler.headers.get("Content-Length", 0))
    if content_length == 0:
        return None
    body = handler.rfile.read(content_length)
    try:
        return json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def send_json_response(handler, status_code, data):
    """发送 JSON 响应"""
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.end_headers()
    handler.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


def send_error(handler, status_code, message):
    """发送错误响应"""
    send_json_response(handler, status_code, {"error": message})


class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""

    def do_GET(self):
        cleanup_expired_reservations()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self.handle_get_items()
        else:
            send_error(self, 404, "Not Found")

    def do_POST(self):
        cleanup_expired_reservations()
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self.handle_post_items()
        elif path == "/reservations":
            self.handle_post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            # 提取 ID
            parts = path.split("/")
            if len(parts) == 4 and parts[2].isdigit():
                reservation_id = int(parts[2])
                self.handle_confirm_reservation(reservation_id)
            else:
                send_error(self, 400, "Invalid reservation ID")
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4 and parts[2].isdigit():
                reservation_id = int(parts[2])
                self.handle_cancel_reservation(reservation_id)
            else:
                send_error(self, 400, "Invalid reservation ID")
        else:
            send_error(self, 404, "Not Found")

    # ---------- 具体处理方法 ----------

    def handle_get_items(self):
        conn = get_db_connection()
        with _db_lock:
            rows = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
        items = [
            {
                "id": row["id"],
                "name": row["name"],
                "stock_total": row["stock_total"],
                "stock_available": row["stock_available"]
            }
            for row in rows
        ]
        send_json_response(self, 200, items)

    def handle_post_items(self):
        data = parse_json_body(self)
        if data is None:
            send_error(self, 400, "Invalid JSON body")
            return
        name = data.get("name")
        stock_total = data.get("stock_total")
        if not isinstance(name, str) or not name:
            send_error(self, 400, "Missing or invalid 'name'")
            return
        if not isinstance(stock_total, int) or stock_total < 0:
            send_error(self, 400, "Missing or invalid 'stock_total' (must be non-negative integer)")
            return
        conn = get_db_connection()
        with _db_lock:
            cursor = conn.execute(
                "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                (name, stock_total, stock_total)
            )
            conn.commit()
            new_id = cursor.lastrowid
        send_json_response(self, 201, {
            "id": new_id,
            "name": name,
            "stock_total": stock_total,
            "stock_available": stock_total
        })

    def handle_post_reservations(self):
        data = parse_json_body(self)
        if data is None:
            send_error(self, 400, "Invalid JSON body")
            return
        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds")
        if not isinstance(item_id, int) or item_id < 1:
            send_error(self, 400, "Missing or invalid 'item_id'")
            return
        if not isinstance(quantity, int) or quantity <= 0:
            send_error(self, 400, "Missing or invalid 'quantity' (must be positive integer)")
            return
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            send_error(self, 400, "Missing or invalid 'ttl_seconds' (must be positive integer)")
            return

        conn = get_db_connection()
        with _db_lock:
            # 检查商品是否存在以及库存是否充足
            item = conn.execute(
                "SELECT id, stock_available FROM items WHERE id = ?", (item_id,)
            ).fetchone()
            if item is None:
                send_error(self, 404, "Item not found")
                return
            if item["stock_available"] < quantity:
                send_error(self, 409, "Insufficient stock")
                return
            # 创建预约
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(seconds=ttl_seconds)
            created_at = now
            cursor = conn.execute(
                "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) "
                "VALUES (?, ?, 'pending', ?, ?)",
                (item_id, quantity, expires_at.isoformat(), created_at.isoformat())
            )
            reservation_id = cursor.lastrowid
            # 减少可用库存
            conn.execute(
                "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                (quantity, item_id)
            )
            conn.commit()
        send_json_response(self, 201, {
            "id": reservation_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at.isoformat(),
            "created_at": created_at.isoformat()
        })

    def handle_confirm_reservation(self, reservation_id):
        conn = get_db_connection()
        with _db_lock:
            res = conn.execute(
                "SELECT id, status FROM reservations WHERE id = ?", (reservation_id,)
            ).fetchone()
            if res is None:
                send_error(self, 404, "Reservation not found")
                return
            if res["status"] != "pending":
                send_error(self, 400, f"Reservation status is '{res['status']}', cannot confirm")
                return
            conn.execute(
                "UPDATE reservations SET status = 'confirmed' WHERE id = ?",
                (reservation_id,)
            )
            conn.commit()
        send_json_response(self, 200, {"status": "confirmed"})

    def handle_cancel_reservation(self, reservation_id):
        conn = get_db_connection()
        with _db_lock:
            res = conn.execute(
                "SELECT id, status, item_id, quantity FROM reservations WHERE id = ?",
                (reservation_id,)
            ).fetchone()
            if res is None:
                send_error(self, 404, "Reservation not found")
                return
            if res["status"] != "pending":
                send_error(self, 400, f"Reservation status is '{res['status']}', cannot cancel")
                return
            # 释放库存
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (res["quantity"], res["item_id"])
            )
            conn.execute(
                "UPDATE reservations SET status = 'cancelled' WHERE id = ?",
                (reservation_id,)
            )
            conn.commit()
        send_json_response(self, 200, {"status": "cancelled"})

    # 为了安全，处理日志
    def log_message(self, format, *args):
        """默认日志输出到 stderr，保留"""
        super().log_message(format, *args)


def run_server():
    init_database()
    server = HTTPServer((LISTEN_HOST, LISTEN_PORT), InventoryHandler)
    print(f"Server running on http://{LISTEN_HOST}:{LISTEN_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    run_server()
```
````
