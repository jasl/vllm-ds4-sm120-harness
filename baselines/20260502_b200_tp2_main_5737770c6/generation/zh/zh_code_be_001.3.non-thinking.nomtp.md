# Generation Transcript

- Case: `zh_code_be_001`
- Language group: `zh`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 18.523454
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 363, "total_tokens": 2642, "completion_tokens": 2279, "prompt_tokens_details": null}`
- Prompt tokens: 363
- Completion tokens: 2279
- Total tokens: 2642

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
_lock = threading.Lock()

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id TEXT PRIMARY KEY, name TEXT NOT NULL, stock_total INTEGER NOT NULL, stock_available INTEGER NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reservations
                 (id TEXT PRIMARY KEY, item_id TEXT NOT NULL, quantity INTEGER NOT NULL,
                  status TEXT NOT NULL DEFAULT 'pending', expires_at TEXT NOT NULL, created_at TEXT NOT NULL,
                  FOREIGN KEY(item_id) REFERENCES items(id))''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/items':
            self.handle_list_items()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/items':
            self.handle_create_item()
        elif path == '/reservations':
            self.handle_create_reservation()
        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            res_id = path.split('/')[2]
            self.handle_confirm_reservation(res_id)
        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            res_id = path.split('/')[2]
            self.handle_cancel_reservation(res_id)
        else:
            self.send_error(404, "Not Found")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_error(self, status, message):
        self.send_json({"error": message}, status)

    def read_json_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except:
            return None

    # ---------- 业务处理 ----------
    def handle_list_items(self):
        self._cleanup_expired()
        conn = get_db()
        try:
            c = conn.cursor()
            c.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = c.fetchall()
            items = [{"id": r["id"], "name": r["name"], "stock_total": r["stock_total"], "stock_available": r["stock_available"]} for r in rows]
            self.send_json(items)
        finally:
            conn.close()

    def handle_create_item(self):
        data = self.read_json_body()
        if not data or 'name' not in data or 'stock_total' not in data:
            self.send_error(400, "Missing required fields: name, stock_total")
            return
        name = data['name']
        try:
            total = int(data['stock_total'])
        except:
            self.send_error(400, "stock_total must be integer")
            return
        if total < 0:
            self.send_error(400, "stock_total must be non-negative")
            return
        item_id = str(uuid.uuid4())
        conn = get_db()
        try:
            c = conn.cursor()
            c.execute("INSERT INTO items (id, name, stock_total, stock_available) VALUES (?, ?, ?, ?)",
                      (item_id, name, total, total))
            conn.commit()
            self.send_json({"id": item_id, "name": name, "stock_total": total, "stock_available": total}, 201)
        except sqlite3.IntegrityError:
            conn.rollback()
            self.send_error(500, "Internal error")
        finally:
            conn.close()

    def handle_create_reservation(self):
        self._cleanup_expired()
        data = self.read_json_body()
        if not data or 'item_id' not in data or 'quantity' not in data or 'ttl_seconds' not in data:
            self.send_error(400, "Missing required fields: item_id, quantity, ttl_seconds")
            return
        item_id = data['item_id']
        try:
            quantity = int(data['quantity'])
            ttl = int(data['ttl_seconds'])
        except:
            self.send_error(400, "quantity and ttl_seconds must be integers")
            return
        if quantity <= 0 or ttl <= 0:
            self.send_error(400, "quantity and ttl_seconds must be positive")
            return

        conn = get_db()
        try:
            with _lock:
                # 检查商品是否存在且库存充足
                c = conn.cursor()
                c.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
                row = c.fetchone()
                if not row:
                    self.send_error(404, "Item not found")
                    return
                available = row["stock_available"]
                if available < quantity:
                    self.send_error(409, "Insufficient stock")
                    return

                # 创建预约
                res_id = str(uuid.uuid4())
                now = datetime.utcnow()
                expires_at = now + timedelta(seconds=ttl)
                c.execute("INSERT INTO reservations (id, item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, 'pending', ?, ?)",
                          (res_id, item_id, quantity, expires_at.isoformat(), now.isoformat()))
                # 扣减可用库存
                c.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?", (quantity, item_id))
                conn.commit()
                self.send_json({
                    "id": res_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at.isoformat(),
                    "created_at": now.isoformat()
                }, 201)
        except Exception as e:
            conn.rollback()
            self.send_error(500, str(e))
        finally:
            conn.close()

    def handle_confirm_reservation(self, res_id):
        self._cleanup_expired()
        conn = get_db()
        try:
            with _lock:
                c = conn.cursor()
                c.execute("SELECT * FROM reservations WHERE id = ?", (res_id,))
                row = c.fetchone()
                if not row:
                    self.send_error(404, "Reservation not found")
                    return
                if row["status"] != "pending":
                    self.send_error(400, "Reservation already processed")
                    return
                # 检查是否过期（防止并发清理导致的过期未被捕捉）
                expires = datetime.fromisoformat(row["expires_at"])
                if datetime.utcnow() > expires:
                    # 过期，释放库存并标记为expired
                    c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                              (row["quantity"], row["item_id"]))
                    c.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (res_id,))
                    conn.commit()
                    self.send_error(410, "Reservation expired")
                    return

                c.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
                conn.commit()
                self.send_json({"id": res_id, "status": "confirmed"})
        except Exception as e:
            conn.rollback()
            self.send_error(500, str(e))
        finally:
            conn.close()

    def handle_cancel_reservation(self, res_id):
        self._cleanup_expired()
        conn = get_db()
        try:
            with _lock:
                c = conn.cursor()
                c.execute("SELECT * FROM reservations WHERE id = ?", (res_id,))
                row = c.fetchone()
                if not row:
                    self.send_error(404, "Reservation not found")
                    return
                if row["status"] != "pending":
                    self.send_error(400, "Reservation already processed")
                    return
                # 释放库存
                c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                          (row["quantity"], row["item_id"]))
                c.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
                conn.commit()
                self.send_json({"id": res_id, "status": "cancelled"})
        except Exception as e:
            conn.rollback()
            self.send_error(500, str(e))
        finally:
            conn.close()

    def _cleanup_expired(self):
        """清理所有过期pending预约，释放库存"""
        conn = get_db()
        try:
            with _lock:
                c = conn.cursor()
                now = datetime.utcnow()
                c.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
                          (now.isoformat(),))
                expired = c.fetchall()
                for row in expired:
                    c.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                              (row["quantity"], row["item_id"]))
                    c.execute("UPDATE reservations SET status = 'expired' WHERE id = ?", (row["id"],))
                conn.commit()
        except:
            conn.rollback()
        finally:
            conn.close()

    def log_message(self, format, *args):
        """抑制日志输出"""
        pass

def run_server(host='127.0.0.1', port=8080):
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
```
````
