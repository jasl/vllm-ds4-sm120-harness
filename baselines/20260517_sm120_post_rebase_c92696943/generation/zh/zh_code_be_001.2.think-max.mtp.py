#!/usr/bin/env python3
import json
import sqlite3
import threading
import re
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

DB_FILE = "inventory.db"
db_lock = threading.Lock()
db_conn = None


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True


def init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    conn.commit()


def cleanup_expired(conn):
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("BEGIN")
    try:
        cur = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at <= ?",
            (now,))
        for row in cur:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                         (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ?", (row['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


class InventoryHandler(BaseHTTPRequestHandler):
    server_version = "InventoryAPI/1.0"
    confirm_pat = re.compile(r'^/reservations/(\d+)/confirm/?$')
    cancel_pat = re.compile(r'^/reservations/(\d+)/cancel/?$')

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def send_error_json(self, message, status=400):
        self.send_json({"error": message}, status)

    def parse_json_body(self):
        content_length = self.headers.get('Content-Length')
        if not content_length:
            self.send_error_json("Content-Length header required", 400)
            return None
        try:
            content_length = int(content_length)
        except (ValueError, TypeError):
            self.send_error_json("Invalid Content-Length", 400)
            return None
        if content_length == 0:
            self.send_error_json("Empty request body", 400)
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_error_json("Invalid JSON", 400)
            return None

    def do_GET(self):
        with db_lock:
            try:
                cleanup_expired(db_conn)
                path = urlparse(self.path).path.rstrip('/') or '/'
                if path == '/items':
                    self.handle_items_get()
                else:
                    self.send_error_json("Not found", 404)
            except Exception:
                if db_conn.in_transaction:
                    db_conn.rollback()
                self.send_error_json("Internal server error", 500)

    def do_POST(self):
        with db_lock:
            try:
                cleanup_expired(db_conn)
                path = urlparse(self.path).path.rstrip('/') or '/'
                if path == '/items':
                    self.handle_items_post()
                elif path == '/reservations':
                    self.handle_reservations_post()
                else:
                    match = self.confirm_pat.match(path)
                    if match:
                        res_id = int(match.group(1))
                        self.handle_reservations_confirm(res_id)
                    else:
                        match = self.cancel_pat.match(path)
                        if match:
                            res_id = int(match.group(1))
                            self.handle_reservations_cancel(res_id)
                        else:
                            self.send_error_json("Not found", 404)
            except Exception:
                if db_conn.in_transaction:
                    db_conn.rollback()
                self.send_error_json("Internal server error", 500)

    # -------- handlers ----------
    def handle_items_get(self):
        cursor = db_conn.execute("SELECT id, name, stock_total, stock_available FROM items")
        items = [dict(row) for row in cursor.fetchall()]
        self.send_json(items)

    def handle_items_post(self):
        body = self.parse_json_body()
        if body is None:
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or stock_total is None:
            self.send_error_json("Missing required parameters: name, stock_total", 400)
            return
        if not isinstance(name, str) or not name.strip():
            self.send_error_json("name must be a non-empty string", 400)
            return
        try:
            stock_total = int(stock_total)
        except (TypeError, ValueError):
            self.send_error_json("stock_total must be an integer", 400)
            return
        if stock_total < 0:
            self.send_error_json("stock_total must be non-negative", 400)
            return
        db_conn.execute("BEGIN")
        try:
            cursor = db_conn.execute(
                "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                (name.strip(), stock_total, stock_total))
            item_id = cursor.lastrowid
            db_conn.commit()
            self.send_json({
                "id": item_id,
                "name": name.strip(),
                "stock_total": stock_total,
                "stock_available": stock_total
            }, status=201)
        except sqlite3.IntegrityError:
            db_conn.rollback()
            self.send_error_json("Item name already exists", 409)
        except Exception:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def handle_reservations_post(self):
        body = self.parse_json_body()
        if body is None:
            return
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if item_id is None or quantity is None or ttl_seconds is None:
            self.send_error_json("Missing required parameters: item_id, quantity, ttl_seconds", 400)
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (TypeError, ValueError):
            self.send_error_json("item_id, quantity, ttl_seconds must be integers", 400)
            return
        if quantity <= 0 or ttl_seconds <= 0:
            self.send_error_json("quantity and ttl_seconds must be positive", 400)
            return
        now = datetime.datetime.utcnow()
        created_at = now.isoformat()
        expires_at = (now + datetime.timedelta(seconds=ttl_seconds)).isoformat()
        db_conn.execute("BEGIN")
        try:
            cursor = db_conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
            if item is None:
                db_conn.rollback()
                self.send_error_json("Item not found", 404)
                return
            if item['stock_available'] < quantity:
                db_conn.rollback()
                self.send_error_json("Insufficient stock", 409)
                return
            db_conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                            (quantity, item_id))
            cursor = db_conn.execute(
                "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                (item_id, quantity, expires_at, created_at))
            res_id = cursor.lastrowid
            db_conn.commit()
            self.send_json({
                "id": res_id,
                "item_id": item_id,
                "quantity": quantity,
                "status": "pending",
                "expires_at": expires_at,
                "created_at": created_at
            }, status=201)
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def _get_reservation_or_error(self, res_id):
        cursor = db_conn.execute(
            "SELECT id, item_id, quantity, status FROM reservations WHERE id = ?", (res_id,))
        row = cursor.fetchone()
        if row is None:
            self.send_error_json("Reservation not found", 404)
            return None
        return row

    def handle_reservations_confirm(self, res_id):
        db_conn.execute("BEGIN")
        try:
            reservation = self._get_reservation_or_error(res_id)
            if reservation is None:
                db_conn.rollback()
                return
            if reservation['status'] != 'pending':
                db_conn.rollback()
                self.send_error_json("Reservation is not pending", 409)
                return
            db_conn.execute("UPDATE reservations SET status = 'confirmed' WHERE id = ?", (res_id,))
            db_conn.commit()
            self.send_json({"id": res_id, "status": "confirmed"})
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)

    def handle_reservations_cancel(self, res_id):
        db_conn.execute("BEGIN")
        try:
            reservation = self._get_reservation_or_error(res_id)
            if reservation is None:
                db_conn.rollback()
                return
            if reservation['status'] != 'pending':
                db_conn.rollback()
                self.send_error_json("Reservation is not pending", 409)
                return
            db_conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                            (reservation['quantity'], reservation['item_id']))
            db_conn.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
            db_conn.commit()
            self.send_json({"id": res_id, "status": "cancelled"})
        except sqlite3.Error:
            db_conn.rollback()
            self.send_error_json("Database error", 500)


if __name__ == "__main__":
    db_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    db_conn.row_factory = sqlite3.Row
    db_conn.isolation_level = None
    init_db(db_conn)
    server = ThreadingHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server started on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopping...")
        server.server_close()
