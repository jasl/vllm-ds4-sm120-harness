# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.436074
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2799, "completion_tokens": 2436, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2436
- Total tokens: 2799

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
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

DB_NAME = "inventory.db"
LOCK = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_NAME)
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

def clean_expired_reservations():
    """清理过期 pending 预约并释放库存"""
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at < ?
    """, (now,))
    expired = c.fetchall()
    for res_id, item_id, qty in expired:
        c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (qty, item_id))
        c.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
    conn.commit()
    conn.close()

class InventoryHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def _parse_path(self):
        parsed = urlparse(self.path)
        return parsed.path.rstrip("/"), parse_qs(parsed.query)

    def do_GET(self):
        path, _ = self._parse_path()
        if path == "/items":
            self._handle_get_items()
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path, _ = self._parse_path()
        with LOCK:
            clean_expired_reservations()
            if path == "/items":
                self._handle_create_item()
            elif path == "/reservations":
                self._handle_create_reservation()
            elif path.startswith("/reservations/") and path.endswith("/confirm"):
                parts = path.split("/")
                if len(parts) == 4:
                    res_id = parts[2]
                    self._handle_confirm_reservation(res_id)
                else:
                    self._send_json({"error": "Invalid path"}, 404)
            elif path.startswith("/reservations/") and path.endswith("/cancel"):
                parts = path.split("/")
                if len(parts) == 4:
                    res_id = parts[2]
                    self._handle_cancel_reservation(res_id)
                else:
                    self._send_json({"error": "Invalid path"}, 404)
            else:
                self._send_json({"error": "Not found"}, 404)

    def _handle_get_items(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, name, stock_total, stock_available FROM items")
        items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in c.fetchall()]
        conn.close()
        self._send_json(items)

    def _handle_create_item(self):
        body = self._read_body()
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or stock_total is None:
            self._send_json({"error": "Missing name or stock_total"}, 400)
            return
        if not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "stock_total must be a non-negative integer"}, 400)
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
            conn.commit()
            item_id = c.lastrowid
            self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
        except sqlite3.IntegrityError:
            self._send_json({"error": "Item already exists"}, 409)
        finally:
            conn.close()

    def _handle_create_reservation(self):
        body = self._read_body()
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if not all([item_id, quantity, ttl_seconds]):
            self._send_json({"error": "Missing item_id, quantity or ttl_seconds"}, 400)
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_json({"error": "quantity must be a positive integer"}, 400)
            return
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            self._send_json({"error": "ttl_seconds must be a positive integer"}, 400)
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = c.fetchone()
            if not row:
                self._send_json({"error": "Item not found"}, 404)
                return
            stock_available = row[0]
            if stock_available < quantity:
                self._send_json({"error": "Insufficient stock", "available": stock_available}, 409)
                return
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            created_at = now.isoformat()
            c.execute("""
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            """, (item_id, quantity, expires_at, created_at))
            c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
            conn.commit()
            res_id = c.lastrowid
            self._send_json({
                "id": res_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": created_at
            }, 201)
        except Exception as e:
            conn.rollback()
            self._send_json({"error": str(e)}, 500)
        finally:
            conn.close()

    def _handle_confirm_reservation(self, res_id_str):
        try:
            res_id = int(res_id_str)
        except ValueError:
            self._send_json({"error": "Invalid reservation id"}, 400)
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, quantity = row
            if status != "pending":
                self._send_json({"error": f"Reservation is already {status}"}, 409)
                return
            # 检查是否过期
            c.execute("SELECT expires_at FROM reservations WHERE id = ?", (res_id,))
            expires_at_str = c.fetchone()[0]
            if datetime.utcnow() > datetime.fromisoformat(expires_at_str):
                c.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (quantity, item_id))
                conn.commit()
                self._send_json({"error": "Reservation expired"}, 410)
                return
            c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()
            self._send_json({"id": res_id, "status": "confirmed"})
        except Exception as e:
            conn.rollback()
            self._send_json({"error": str(e)}, 500)
        finally:
            conn.close()

    def _handle_cancel_reservation(self, res_id_str):
        try:
            res_id = int(res_id_str)
        except ValueError:
            self._send_json({"error": "Invalid reservation id"}, 400)
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = c.fetchone()
            if not row:
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, quantity = row
            if status != "pending":
                self._send_json({"error": f"Reservation is already {status}"}, 409)
                return
            # 检查是否过期（过期也允许取消，但视为取消）
            c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?", (quantity, item_id))
            conn.commit()
            self._send_json({"id": res_id, "status": "cancelled"})
        except Exception as e:
            conn.rollback()
            self._send_json({"error": str(e)}, 500)
        finally:
            conn.close()

    def log_message(self, format, *args):
        pass  # 抑制默认日志

def run_server(host="127.0.0.1", port=8080):
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

if __name__ == "__main__":
    init_db()
    run_server()
```
````
