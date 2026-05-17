: _send_json(404, {"error": "Item not found"})
                return
            stock_available = item[0]
            if stock_available < quantity:
                self._send_json(409, {"error": "Insufficient stock"})
                return
            # 创建预约
            now = datetime.datetime.utcnow()
            expires_at = now + datetime.timedelta(seconds=ttl_seconds)
            created_at = now.isoformat()
            expires_at_str = expires_at.isoformat()
            # 事务开始
            conn.execute("BEGIN")
            try:
                # 减库存
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
                # 插入预约
                conn.execute("INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                             (item_id, quantity, expires_at_str, created_at))
                conn.commit()
                cursor = conn.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
                self._send_json(201, {
                    "id": row[0],
                    "item_id": row[1],
                    "quantity": row[2],
                    "status": row[3],
                    "expires_at": row[4],
                    "created_at": row[5]
                })
            except Exception as e:
                conn.rollback()
                self._send_json(500, {"error": "Internal server error"})

    def _handle_confirm(self, res_id):
        with db_lock:
            clean_expired()
            # 检查预约存在且pending
            cursor = conn.execute("SELECT id, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[1] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[1]}"})
                return
            conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            conn.commit()
            self._send_json(200, {"message": "Reservation confirmed"})

    def _handle_cancel(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[3] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[3]}, cannot cancel"})
                return
            item_id = row[1]
            quantity = row[2]
            conn.execute("BEGIN")
            try:
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
                conn.commit()
                self._send_json(200, {"message": "Reservation cancelled"})
            except Exception as e:
                conn.rollback()
                self._send_json(500, {"error": "Internal server error"})

if __name__ == "__main__":
    init_db()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8080), ReservationHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```

注意：上面代码中 _handle_post_reservation 中有一处 `self response: _send_json` 应该是笔误。应修正为 `self._send_json(...)`。还有在 try-except 中捕获所有异常，但最好指定具体的异常。还有在 begin/commit/rollback 时可能没有正确处理。但基本逻辑正确。

我将在最终代码中修复这些小错误。

另外，在 `_handle_post_reservation` 中，使用了 `conn.execute("BEGIN")`，但 Python 的 sqlite3 连接默认自动提交，使用 with conn: 更安全。但是 with conn: 会自动开始事务并提交或回滚，而且我们还需要手动控制。我们可以使用 with conn: 上下文来包裹需要原子性的块。如：

```python
with conn:
    # 执行所有语句
    conn.execute(...)
    ...
# 退出 with 自动 commit 如果无异常，否则 rollback
```

这更符合 Python 风格。所以我会改用 with conn: 而不是手动 begin/commit/rollback。需要确保 conn 是全局的，且 with 块内部不会因为异常而影响其他线程。由于有锁，没问题。

修改代码，使用 `with conn:` 包裹。

同时注意：读操作不需要事务，但也可以放在 with 中，但为了简单，可以放在锁内直接执行。

此外，clean_expired 内部也应该是 with conn: 包裹以确保原子性？目前 clean_expired 里面多个 update 然后 commit，应该使用事务。用 with conn: 包裹更安全。

修改 clean_expired:

```python
def clean_expired():
    now = datetime.datetime.utcnow().isoformat()
    with conn:
        cursor = conn.execute("SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?", (now,))
        expired = cursor.fetchall()
        for res_id, item_id, quantity in expired:
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
```

同样，在创建预约时使用 `with conn:`。

但是注意：在 with conn: 内部，如果 commit 失败或 rollback，外部不会捕获。但我们可以用 try-except 包裹。

同时注意：在 with conn: 中，我们不能在内部再调用 with conn: 多次，因为锁已经持有，且 conn 是同一个，嵌套 with 可能没问题，但为了清晰，我们在锁内只有一个 with conn: 即可。

现在代码需要调整。

完整修正后的代码：

```python
#!/usr/bin/env python3
import http.server
import json
import sqlite3
import threading
import datetime
import urllib.parse
import os

DB_NAME = "inventory.db"
db_lock = threading.Lock()
conn = None

def init_db():
    global conn
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )""")
    conn.commit()

def clean_expired():
    now = datetime.datetime.utcnow().isoformat()
    with conn:
        cursor = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
            (now,)
        )
        expired = cursor.fetchall()
        for res_id, item_id, quantity in expired:
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))

class ReservationHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            with db_lock:
                clean_expired()
                cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in cursor.fetchall()]
                self._send_json(200, items)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        parts = [p for p in path.split('/') if p]

        if path == '/items':
            self._handle_post_item()
        elif path == '/reservations':
            self._handle_post_reservation()
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_confirm(res_id)
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_cancel(res_id)
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_post_item(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            self._send_json(400, {"error": "name and stock_total required, stock_total must be positive integer"})
            return
        with db_lock:
            clean_expired()
            with conn:
                conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
                cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
            self._send_json(201, {"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]})

    def _handle_post_reservation(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')
        if not all(isinstance(x, int) for x in [item_id, quantity, ttl_seconds]) or quantity <= 0 or ttl_seconds <= 0:
            self._send_json(400, {"error": "item_id, quantity, ttl_seconds must be positive integers"})
            return
        with db_lock:
            clean_expired()
            # 检查商品存在和库存
            cursor = conn.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
            item = cursor.fetchone()
            if not item:
                self._send_json(404, {"error": "Item not found"})
                return
            stock_available = item[0]
            if stock_available < quantity:
                self._send_json(409, {"error": "Insufficient stock"})
                return
            # 创建预约（事务）
            now = datetime.datetime.utcnow()
            expires_at = now + datetime.timedelta(seconds=ttl_seconds)
            created_at = now.isoformat()
            expires_at_str = expires_at.isoformat()
            with conn:
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
                conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at_str, created_at)
                )
                cursor = conn.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
            self._send_json(201, {
                "id": row[0],
                "item_id": row[1],
                "quantity": row[2],
                "status": row[3],
                "expires_at": row[4],
                "created_at": row[5]
            })

    def _handle_confirm(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[1] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[1]}"})
                return
            with conn:
                conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            self._send_json(200, {"message": "Reservation confirmed"})

    def _handle_cancel(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[3] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[3]}, cannot cancel"})
                return
            item_id = row[1]
            quantity = row[2]
            with conn:
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
            self._send_json(200, {"message": "Reservation cancelled"})

if __name__ == "__main__":
    init_db()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8080), ReservationHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```

注意：在 `_handle_post_reservation` 中，先检查库存，然后再进入事务。这里有一个 竞态条件：在两个线程同时检查库存后，一个执行更新，另一个可能基于旧值检查。但因为我们使用了锁，同一时刻只有一个线程在操作，所以不会有竞态。锁确保整个操作原子性。没问题。

还有一点：在 `_handle_confirm` 和 `_handle_cancel` 中，clean_expired 先执行，可能已经将 pending 变为 expired，但后续查询可能过期了。这样用户会看到 NotFound 或 Already 状态。这是设计预期的。

最后，检查所有可能的异常。比如在 `_send_json` 中，可能由于连接断开而异常，但那是客户端的问题，忽略。

确保代码不超过1000行，当前代码远远少于。

输出：只需输出完整 Python 代码。</think>```python
#!/usr/bin/env python3
import http.server
import json
import sqlite3
import threading
import datetime
import urllib.parse
import os

DB_NAME = "inventory.db"
db_lock = threading.Lock()
conn = None

def init_db():
    global conn
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )""")
    conn.commit()

def clean_expired():
    now = datetime.datetime.utcnow().isoformat()
    with conn:
        cursor = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
            (now,)
        )
        expired = cursor.fetchall()
        for res_id, item_id, quantity in expired:
            conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res_id,))
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))

class ReservationHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            with db_lock:
                clean_expired()
                cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
                items = [{"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]} for row in cursor.fetchall()]
                self._send_json(200, items)
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip('/')
        parts = [p for p in path.split('/') if p]

        if path == '/items':
            self._handle_post_item()
        elif path == '/reservations':
            self._handle_post_reservation()
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_confirm(res_id)
        elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
            try:
                res_id = int(parts[1])
            except ValueError:
                self._send_json(400, {"error": "Invalid reservation id"})
                return
            self._handle_cancel(res_id)
        else:
            self._send_json(404, {"error": "Not found"})

    def _handle_post_item(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        name = data.get('name')
        stock_total = data.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            self._send_json(400, {"error": "name and stock_total required, stock_total must be positive integer"})
            return
        with db_lock:
            clean_expired()
            with conn:
                conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)", (name, stock_total, stock_total))
                cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
            self._send_json(201, {"id": row[0], "name": row[1], "stock_total": row[2], "stock_available": row[3]})

    def _handle_post_reservation(self):
        data = self._read_body()
        if data is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        ttl_seconds = data.get('ttl_seconds')
        if not all(isinstance(x, int) for x in [item_id, quantity, ttl_seconds]) or quantity <= 0 or ttl_seconds <= 0:
            self._send_json(400, {"error": "item_id, quantity, ttl_seconds must be positive integers"})
            return
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT stock_available FROM items WHERE id=?", (item_id,))
            item = cursor.fetchone()
            if not item:
                self._send_json(404, {"error": "Item not found"})
                return
            stock_available = item[0]
            if stock_available < quantity:
                self._send_json(409, {"error": "Insufficient stock"})
                return
            now = datetime.datetime.utcnow()
            expires_at = now + datetime.timedelta(seconds=ttl_seconds)
            created_at = now.isoformat()
            expires_at_str = expires_at.isoformat()
            with conn:
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?", (quantity, item_id))
                conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at_str, created_at)
                )
                cursor = conn.execute("SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = last_insert_rowid()")
                row = cursor.fetchone()
            self._send_json(201, {
                "id": row[0],
                "item_id": row[1],
                "quantity": row[2],
                "status": row[3],
                "expires_at": row[4],
                "created_at": row[5]
            })

    def _handle_confirm(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[1] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[1]}"})
                return
            with conn:
                conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
            self._send_json(200, {"message": "Reservation confirmed"})

    def _handle_cancel(self, res_id):
        with db_lock:
            clean_expired()
            cursor = conn.execute("SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,))
            row = cursor.fetchone()
            if not row:
                self._send_json(404, {"error": "Reservation not found"})
                return
            if row[3] != 'pending':
                self._send_json(409, {"error": f"Reservation is already {row[3]}, cannot cancel"})
                return
            item_id = row[1]
            quantity = row[2]
            with conn:
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?", (quantity, item_id))
            self._send_json(200, {"message": "Reservation cancelled"})

if __name__ == "__main__":
    init_db()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8080), ReservationHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
```
