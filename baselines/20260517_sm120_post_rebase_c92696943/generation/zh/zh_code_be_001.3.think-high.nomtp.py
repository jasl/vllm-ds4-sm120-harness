#!/usr/bin/env python3
"""单文件 HTTP API 服务，实现库存预约管理。"""
import json
import sqlite3
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = "inventory.db"
db_lock = threading.Lock()


def init_db():
    """初始化数据库，创建表（如果不存在）。"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
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
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)
        conn.commit()


def cleanup_expired(conn):
    """清理已过期的 pending 预约并释放库存（需在事务中调用）。"""
    now = time.time()
    # 找出所有过期的 pending 预约
    rows = conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
        (now,)
    ).fetchall()
    for row in rows:
        res_id, item_id, qty = row
        # 释放库存
        conn.execute(
            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
            (qty, item_id)
        )
        # 标记为 cancelled（或 deleted）
        conn.execute(
            "UPDATE reservations SET status='cancelled' WHERE id = ?",
            (res_id,)
        )
    if rows:
        conn.commit()


def get_db():
    """获取一个新的数据库连接。"""
    return sqlite3.connect(DB_PATH)


class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器。"""

    def _send_json(self, status_code, data):
        """发送 JSON 响应。"""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_json_body(self):
        """读取请求体并解析为 JSON 字典。"""
        content_length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(content_length)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def _parse_path(self):
        """解析路径，返回 (base_path, path_params) 元组。"""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        # 匹配 /reservations/<id>/confirm 或 /reservations/<id>/cancel
        parts = path.split("/")
        if len(parts) == 4 and parts[1] == "reservations" and parts[3] in ("confirm", "cancel"):
            return parts[3], parts[2]  # action, reservation_id
        return path, None

    def do_GET(self):
        """处理 GET 请求。"""
        path, _ = self._parse_path()
        if path == "/items":
            self._handle_list_items()
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        """处理 POST 请求。"""
        path, param = self._parse_path()
        if path == "/items":
            self._handle_create_item()
        elif path == "/reservations":
            self._handle_create_reservation()
        elif path == "confirm":
            self._handle_confirm_reservation(param)
        elif path == "cancel":
            self._handle_cancel_reservation(param)
        else:
            self._send_json(404, {"error": "Not Found"})

    def _handle_list_items(self):
        """GET /items：列出商品和可用库存。"""
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                rows = conn.execute(
                    "SELECT id, name, stock_total, stock_available FROM items"
                ).fetchall()
                items = [
                    {
                        "id": r[0],
                        "name": r[1],
                        "stock_total": r[2],
                        "stock_available": r[3]
                    }
                    for r in rows
                ]
                self._send_json(200, {"items": items})
            finally:
                conn.close()

    def _handle_create_item(self):
        """POST /items：新增商品。"""
        body = self._read_json_body()
        if body is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self._send_json(400, {"error": "Invalid parameters: name (string), stock_total (non-negative integer)"})
            return
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                # 检查是否已存在同名商品
                existing = conn.execute(
                    "SELECT id FROM items WHERE name = ?", (name,)
                ).fetchone()
                if existing:
                    self._send_json(400, {"error": f"Item with name '{name}' already exists"})
                    return
                conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                self._send_json(201, {
                    "id": new_id,
                    "name": name,
                    "stock_total": stock_total,
                    "stock_available": stock_total
                })
            except sqlite3.IntegrityError:
                self._send_json(400, {"error": "Item name conflict"})
            finally:
                conn.close()

    def _handle_create_reservation(self):
        """POST /reservations：创建预约。"""
        body = self._read_json_body()
        if body is None:
            self._send_json(400, {"error": "Invalid JSON"})
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if not all(isinstance(x, int) for x in [item_id, quantity, ttl_seconds]):
            self._send_json(400, {"error": "Invalid parameters: item_id (int), quantity (int), ttl_seconds (int)"})
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self._send_json(400, {"error": "quantity and ttl_seconds must be positive"})
            return
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                # 检查商品是否存在及库存是否充足
                item = conn.execute(
                    "SELECT id, stock_available FROM items WHERE id = ?",
                    (item_id,)
                ).fetchone()
                if not item:
                    self._send_json(404, {"error": "Item not found"})
                    return
                if item[1] < quantity:
                    self._send_json(409, {"error": "Insufficient stock"})
                    return
                now = time.time()
                expires = now + ttl_seconds
                # 扣减库存
                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                    (quantity, item_id)
                )
                # 创建预约
                conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) "
                    "VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires, now)
                )
                conn.commit()
                new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                self._send_json(201, {
                    "id": new_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires,
                    "created_at": now
                })
            finally:
                conn.close()

    def _handle_confirm_reservation(self, res_id_str):
        """POST /reservations/{id}/confirm：确认预约。"""
        try:
            res_id = int(res_id_str)
        except ValueError:
            self._send_json(400, {"error": "Invalid reservation id"})
            return
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                row = conn.execute(
                    "SELECT id, status FROM reservations WHERE id = ?",
                    (res_id,)
                ).fetchone()
                if not row:
                    self._send_json(404, {"error": "Reservation not found"})
                    return
                if row[1] != "pending":
                    self._send_json(400, {"error": f"Reservation status is '{row[1]}', cannot confirm"})
                    return
                conn.execute(
                    "UPDATE reservations SET status = 'confirmed' WHERE id = ?",
                    (res_id,)
                )
                conn.commit()
                self._send_json(200, {"message": "Reservation confirmed", "id": res_id, "status": "confirmed"})
            finally:
                conn.close()

    def _handle_cancel_reservation(self, res_id_str):
        """POST /reservations/{id}/cancel：取消预约，释放库存。"""
        try:
            res_id = int(res_id_str)
        except ValueError:
            self._send_json(400, {"error": "Invalid reservation id"})
            return
        with db_lock:
            conn = get_db()
            try:
                cleanup_expired(conn)
                row = conn.execute(
                    "SELECT id, status, item_id, quantity FROM reservations WHERE id = ?",
                    (res_id,)
                ).fetchone()
                if not row:
                    self._send_json(404, {"error": "Reservation not found"})
                    return
                if row[1] != "pending":
                    self._send_json(400, {"error": f"Reservation status is '{row[1]}', cannot cancel"})
                    return
                # 释放库存
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                    (row[3], row[2])
                )
                conn.execute(
                    "UPDATE reservations SET status = 'cancelled' WHERE id = ?",
                    (res_id,)
                )
                conn.commit()
                self._send_json(200, {"message": "Reservation cancelled", "id": res_id, "status": "cancelled"})
            finally:
                conn.close()


def run(host="127.0.0.1", port=8080):
    """启动 HTTP 服务器。"""
    server = HTTPServer((host, port), InventoryHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    init_db()
    run()
