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
- Elapsed seconds: 8.833246
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2909, "completion_tokens": 2546, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2546
- Total tokens: 2909

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
#!/usr/bin/env python3
import json
import sqlite3
import threading
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_PATH = "inventory.db"
lock = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    """)
    c.execute("""
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

def cleanup_expired():
    """清理过期pending预约，释放库存"""
    with lock:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        # 找出过期pending预约
        c.execute("""
            SELECT id, item_id, quantity FROM reservations
            WHERE status='pending' AND expires_at < ?
        """, (now,))
        expired = c.fetchall()
        for rid, iid, qty in expired:
            # 释放库存
            c.execute("""
                UPDATE items SET stock_available = stock_available + ?
                WHERE id = ?
            """, (qty, iid))
            # 更新预约状态为expired
            c.execute("""
                UPDATE reservations SET status='expired' WHERE id=?
            """, (rid,))
        conn.commit()
        conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode('utf-8'))

    def _parse_path(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        params = parse_qs(parsed.query)
        return path, params

    def do_GET(self):
        cleanup_expired()
        path, _ = self._parse_path()
        if path == '/items':
            self._handle_get_items()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        cleanup_expired()
        path, _ = self._parse_path()
        if path == '/items':
            self._handle_create_item()
        elif path == '/reservations':
            self._handle_create_reservation()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            parts = path.split('/')
            if len(parts) == 4 and parts[2]:
                rid = parts[2]
                self._handle_confirm_reservation(rid)
            else:
                self._send_json({"error": "Invalid path"}, 400)
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) == 4 and parts[2]:
                rid = parts[2]
                self._handle_cancel_reservation(rid)
            else:
                self._send_json({"error": "Invalid path"}, 400)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_get_items(self):
        with lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = c.fetchall()
            items = [{"id": r[0], "name": r[1], "stock_total": r[2], "stock_available": r[3]} for r in rows]
            conn.close()
        self._send_json(items)

    def _handle_create_item(self):
        try:
            data = self._read_json_body()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or stock_total is None:
            self._send_json({"error": "Missing name or stock_total"}, 400)
            return
        if not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "stock_total must be non-negative integer"}, 400)
            return
        item_id = str(uuid.uuid4())
        with lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO items (id, name, stock_total, stock_available)
                    VALUES (?, ?, ?, ?)
                """, (item_id, name, stock_total, stock_total))
                conn.commit()
            except sqlite3.IntegrityError:
                conn.close()
                self._send_json({"error": "Item already exists"}, 409)
                return
            conn.close()
        self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_create_reservation(self):
        try:
            data = self._read_json_body()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')
        if not item_id or quantity is None or ttl_seconds is None:
            self._send_json({"error": "Missing item_id, quantity or ttl_seconds"}, 400)
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_json({"error": "quantity must be positive integer"}, 400)
            return
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            self._send_json({"error": "ttl_seconds must be positive integer"}, 400)
            return

        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl_seconds)
        created_at = now.isoformat()
        expires_at_str = expires_at.isoformat()
        reservation_id = str(uuid.uuid4())

        with lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            # 检查商品是否存在且库存充足
            c.execute("SELECT stock_available, stock_total FROM items WHERE id=?", (item_id,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Item not found"}, 404)
                return
            available, total = row
            if available < quantity:
                conn.close()
                self._send_json({"error": "Insufficient stock"}, 409)
                return
            # 扣减库存
            c.execute("""
                UPDATE items SET stock_available = stock_available - ?
                WHERE id = ?
            """, (quantity, item_id))
            # 创建预约
            c.execute("""
                INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, ?, 'pending', ?, ?)
            """, (reservation_id, item_id, quantity, expires_at_str, created_at))
            conn.commit()
            conn.close()
        self._send_json({
            "id": reservation_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at_str,
            "created_at": created_at
        }, 201)

    def _handle_confirm_reservation(self, rid):
        with lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id=?", (rid,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, quantity = row
            if status != 'pending':
                conn.close()
                self._send_json({"error": f"Reservation is already {status}"}, 400)
                return
            # 检查是否过期（double check）
            c.execute("SELECT expires_at FROM reservations WHERE id=?", (rid,))
            expires_at_str = c.fetchone()[0]
            if datetime.utcnow().isoformat() > expires_at_str:
                # 过期则释放库存并标记为expired
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
                c.execute("UPDATE reservations SET status='expired' WHERE id=?", (rid,))
                conn.commit()
                conn.close()
                self._send_json({"error": "Reservation expired"}, 410)
                return
            # 确认预约
            c.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (rid,))
            conn.commit()
            conn.close()
        self._send_json({"id": rid, "status": "confirmed"})

    def _handle_cancel_reservation(self, rid):
        with lock:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id=?", (rid,))
            row = c.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, quantity = row
            if status != 'pending':
                conn.close()
                self._send_json({"error": f"Reservation is already {status}"}, 400)
                return
            # 释放库存
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
            c.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (rid,))
            conn.commit()
            conn.close()
        self._send_json({"id": rid, "status": "cancelled"})

    def log_message(self, format, *args):
        # 抑制默认日志输出，可自定义
        pass

def run_server(host='127.0.0.1', port=8080):
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

if __name__ == "__main__":
    run_server()
```
````
