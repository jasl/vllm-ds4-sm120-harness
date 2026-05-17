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
