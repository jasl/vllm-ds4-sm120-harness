import http.server
import json
import sqlite3
import threading
import socketserver
import os
import re
import time
from datetime import datetime, timedelta, timezone
import sys

DB_PATH = 'inventory.db'
db_lock = threading.Lock()
conn = None


def _now_ts():
    return time.time()


def init_db():
    global conn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock_total INTEGER NOT NULL,
        stock_available INTEGER NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        expires_at REAL NOT NULL,
        created_at REAL NOT NULL,
        FOREIGN KEY(item_id) REFERENCES items(id)
    )''')
    conn.commit()


def clean_expired(conn):
    now = _now_ts()
    cursor = conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
        (now,))
    expired = cursor.fetchall()
    if not expired:
        return
    conn.execute("BEGIN")
    try:
        for row in expired:
            conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                         (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status='expired' WHERE id = ? AND status='pending'",
                         (row['id'],))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def get_all_items(conn):
    cursor = conn.execute("SELECT id, name, stock_total, stock_available FROM items")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]


def create_item(conn, name, stock_total):
    if not name:
        return None, "name is required"
    try:
        stock_total = int(stock_total)
        if stock_total <= 0:
            return None, "stock_total must be a positive integer"
    except (ValueError, TypeError):
        return None, "stock_total must be a positive integer"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                              (name, stock_total, stock_total))
        item_id = cursor.lastrowid
        conn.commit()
        return {"id": item_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, None
    except Exception:
        conn.rollback()
        raise


def create_reservation(conn, item_id, quantity, ttl_seconds):
    try:
        item_id = int(item_id)
        quantity = int(quantity)
        ttl_seconds = int(ttl_seconds)
    except (ValueError, TypeError):
        return None, "item_id, quantity, ttl_seconds must be integers"
    if quantity <= 0:
        return None, "quantity must be positive"
    if ttl_seconds <= 0:
        return None, "ttl_seconds must be positive"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT id, stock_available FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if item is None:
            conn.rollback()
            return None, "Item not found"
        if item['stock_available'] < quantity:
            conn.rollback()
            return None, "Insufficient stock"
        conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                     (quantity, item_id))
        now_ts = _now_ts()
        expires_ts = now_ts + ttl_seconds
        cursor = conn.execute(
            "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
            (item_id, quantity, expires_ts, now_ts))
        reservation_id = cursor.lastrowid
        conn.commit()
        return {
            "id": reservation_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": datetime.utcfromtimestamp(expires_ts).isoformat(),
            "created_at": datetime.utcfromtimestamp(now_ts).isoformat()
        }, None
    except Exception:
        conn.rollback()
        raise


def confirm_reservation(conn, reservation_id):
    try:
        reservation_id = int(reservation_id)
    except (ValueError, TypeError):
        return None, "Invalid reservation id"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation cannot be confirmed (current status: {})".format(row['status'])
        conn.execute("UPDATE reservations SET status='confirmed' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "confirmed"}, None
    except Exception:
        conn.rollback()
        raise


def cancel_reservation(conn, reservation_id):
    try:
        reservation_id = int(reservation_id)
    except (ValueError, TypeError):
        return None, "Invalid reservation id"
    conn.execute("BEGIN")
    try:
        cursor = conn.execute("SELECT status, item_id, quantity FROM reservations WHERE id = ?", (reservation_id,))
        row = cursor.fetchone()
        if row is None:
            conn.rollback()
            return None, "Reservation not found"
        if row['status'] != 'pending':
            conn.rollback()
            return None, "Reservation cannot be cancelled (current status: {})".format(row['status'])
        conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                     (row['quantity'], row['item_id']))
        conn.execute("UPDATE reservations SET status='cancelled' WHERE id = ?", (reservation_id,))
        conn.commit()
        return {"id": reservation_id, "status": "cancelled"}, None
    except Exception:
        conn.rollback()
        raise


class MyHandler(http.server.BaseHTTPRequestHandler):

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error(self, code, message):
        self._send_json({"error": message}, code)

    def _read_body(self):
        content_length = self.headers.get('Content-Length')
        if not content_length:
            return {}
        try:
            content_length = int(content_length)
        except ValueError:
            return {}
        if content_length <= 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_GET(self):
        with db_lock:
            try:
                clean_expired(conn)
                if self.path == '/items':
                    items = get_all_items(conn)
                    self._send_json(items)
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

    def do_POST(self):
        with db_lock:
            try:
                clean_expired(conn)
                path = self.path
                if path == '/items':
                    self._handle_post_items()
                elif path == '/reservations':
                    self._handle_post_reservations()
                elif re.fullmatch(r'/reservations/\d+/confirm', path):
                    rid = int(path.split('/')[2])
                    self._handle_post_confirm(rid)
                elif re.fullmatch(r'/reservations/\d+/cancel', path):
                    rid = int(path.split('/')[2])
                    self._handle_post_cancel(rid)
                else:
                    self._send_error(404, "Not found")
            except Exception as e:
                self._send_error(500, str(e))

    def _handle_post_items(self):
        body = self._read_body()
        if body is None:
            self._send_error(400, "Invalid JSON")
            return
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name:
            self._send_error(400, "name is required")
            return
        try:
            stock_total = int(stock_total)
            if stock_total <= 0:
                raise ValueError
        except (ValueError, TypeError):
            self._send_error(400, "stock_total must be a positive integer")
            return
        item, err = create_item(conn, name, stock_total)
        if err:
            self._send_error(400, err)
            return
        self._send_json(item, 201)

    def _handle_post_reservations(self):
        body = self._read_body()
        if body is None:
            self._send_error(400, "Invalid JSON")
            return
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if item_id is None or quantity is None or ttl_seconds is None:
            self._send_error(400, "item_id, quantity, ttl_seconds are required")
            return
        try:
            item_id = int(item_id)
            quantity = int(quantity)
            ttl_seconds = int(ttl_seconds)
        except (ValueError, TypeError):
            self._send_error(400, "item_id, quantity, ttl_seconds must be integers")
            return
        reservation, err = create_reservation(conn, item_id, quantity, ttl_seconds)
        if err:
            if err == "Insufficient stock":
                self._send_error(409, err)
            elif "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation, 201)

    def _handle_post_confirm(self, reservation_id):
        reservation, err = confirm_reservation(conn, reservation_id)
        if err:
            if "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation)

    def _handle_post_cancel(self, reservation_id):
        reservation, err = cancel_reservation(conn, reservation_id)
        if err:
            if "not found" in err.lower():
                self._send_error(404, err)
            else:
                self._send_error(400, err)
            return
        self._send_json(reservation)


class ThreadHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == '__main__':
    init_db()
    server = ThreadHTTPServer(('127.0.0.1', 8080), MyHandler)
    print("Server starting on 127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down")
        server.server_close()
        sys.exit(0)
