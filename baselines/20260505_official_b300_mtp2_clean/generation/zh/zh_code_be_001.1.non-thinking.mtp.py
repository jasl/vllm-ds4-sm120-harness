#!/usr/bin/env python3
"""库存预约服务 - HTTP API 服务"""

import json
import sqlite3
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_PATH = "inventory.db"
LOCK = threading.Lock()

def init_db():
    """初始化数据库，创建表结构"""
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
    """清理过期预约并释放库存（线程安全）"""
    with LOCK:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        # 查询过期 pending 预约
        cursor.execute("""
            SELECT id, item_id, quantity FROM reservations
            WHERE status = 'pending' AND expires_at < ?
        """, (now,))
        expired = cursor.fetchall()
        for res_id, item_id, qty in expired:
            # 释放库存
            cursor.execute("""
                UPDATE items SET stock_available = stock_available + ?
                WHERE id = ?
            """, (qty, item_id))
            # 更新预约状态为 expired
            cursor.execute("""
                UPDATE reservations SET status = 'expired'
                WHERE id = ?
            """, (res_id,))
        conn.commit()
        conn.close()

class RequestHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""

    def _send_json(self, data, status=200):
        """发送 JSON 响应"""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        """读取请求体 JSON"""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self._handle_get_items()
        else:
            self._send_json({"error": "Not Found"}, 404)

    def do_POST(self):
        """处理 POST 请求"""
        cleanup_expired()
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self._handle_post_items()
        elif path == "/reservations":
            self._handle_post_reservations()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            res_id = path.split("/")[2]
            self._handle_confirm_reservation(res_id)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            res_id = path.split("/")[2]
            self._handle_cancel_reservation(res_id)
        else:
            self._send_json({"error": "Not Found"}, 404)

    def _handle_get_items(self):
        """GET /items"""
        with LOCK:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, stock_total, stock_available FROM items")
            rows = cursor.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": row["id"],
                    "name": row["name"],
                    "stock_total": row["stock_total"],
                    "stock_available": row["stock_available"]
                })
            conn.close()
        self._send_json(items)

    def _handle_post_items(self):
        """POST /items"""
        body = self._read_body()
        if not body or "name" not in body or "stock_total" not in body:
            self._send_json({"error": "Missing required fields: name, stock_total"}, 400)
            return
        name = body["name"]
        try:
            stock_total = int(body["stock_total"])
        except (ValueError, TypeError):
            self._send_json({"error": "stock_total must be an integer"}, 400)
            return
        if stock_total < 0:
            self._send_json({"error": "stock_total must be non-negative"}, 400)
            return
        with LOCK:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO items (name, stock_total, stock_available)
                VALUES (?, ?, ?)
            """, (name, stock_total, stock_total))
            conn.commit()
            item_id = cursor.lastrowid
            conn.close()
        self._send_json({"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)

    def _handle_post_reservations(self):
        """POST /reservations"""
        body = self._read_body()
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

        with LOCK:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            # 检查库存
            cursor.execute("SELECT stock_available FROM items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Item not found"}, 404)
                return
            available = row[0]
            if available < quantity:
                conn.close()
                self._send_json({"error": "Insufficient stock", "available": available}, 409)
                return
            # 扣减库存
            cursor.execute("""
                UPDATE items SET stock_available = stock_available - ?
                WHERE id = ?
            """, (quantity, item_id))
            # 创建预约
            now = datetime.utcnow()
            expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
            created_at = now.isoformat()
            cursor.execute("""
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            """, (item_id, quantity, expires_at, created_at))
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

    def _handle_confirm_reservation(self, res_id):
        """POST /reservations/{id}/confirm"""
        try:
            res_id = int(res_id)
        except ValueError:
            self._send_json({"error": "Invalid reservation ID"}, 400)
            return
        with LOCK:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM reservations WHERE id = ?", (res_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            if row[0] == "confirmed":
                conn.close()
                self._send_json({"error": "Reservation already confirmed"}, 409)
                return
            if row[0] != "pending":
                conn.close()
                self._send_json({"error": f"Reservation is {row[0]}, cannot confirm"}, 409)
                return
            cursor.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            conn.commit()
            # 返回更新后的预约
            cursor.execute("""
                SELECT id, item_id, quantity, status, expires_at, created_at
                FROM reservations WHERE id = ?
            """, (res_id,))
            row = cursor.fetchone()
            conn.close()
        self._send_json({
            "id": row[0],
            "item_id": row[1],
            "quantity": row[2],
            "status": row[3],
            "expires_at": row[4],
            "created_at": row[5]
        })

    def _handle_cancel_reservation(self, res_id):
        """POST /reservations/{id}/cancel"""
        try:
            res_id = int(res_id)
        except ValueError:
            self._send_json({"error": "Invalid reservation ID"}, 400)
            return
        with LOCK:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (res_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                self._send_json({"error": "Reservation not found"}, 404)
                return
            status, item_id, quantity = row
            if status == "cancelled":
                conn.close()
                self._send_json({"error": "Reservation already cancelled"}, 409)
                return
            if status != "pending":
                conn.close()
                self._send_json({"error": f"Reservation is {status}, cannot cancel"}, 409)
                return
            # 释放库存
            cursor.execute("""
                UPDATE items SET stock_available = stock_available + ?
                WHERE id = ?
            """, (quantity, item_id))
            # 更新预约状态
            cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            conn.commit()
            # 返回更新后的预约
            cursor.execute("""
                SELECT id, item_id, quantity, status, expires_at, created_at
                FROM reservations WHERE id = ?
            """, (res_id,))
            row = cursor.fetchone()
            conn.close()
        self._send_json({
            "id": row[0],
            "item_id": row[1],
            "quantity": row[2],
            "status": row[3],
            "expires_at": row[4],
            "created_at": row[5]
        })

    def log_message(self, format, *args):
        """禁用默认日志输出（可选）"""
        pass

def run_server(host="127.0.0.1", port=8080):
    """启动 HTTP 服务"""
    init_db()
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    run_server()
