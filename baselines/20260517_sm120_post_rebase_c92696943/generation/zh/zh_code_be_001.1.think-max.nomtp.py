#!/usr/bin/env python3
import http.server
import json
import sqlite3
import threading
import time
import re
import urllib.parse

DB = 'reservations.db'
lock = threading.Lock()
conn = None

# ------------------ Database ------------------
def init_db():
    global conn
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.isolation_level = None  # manual transaction control
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
            expires_at INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)
    conn.commit()

# ------------------ Cleanup expired reservations ------------------
def cleanup_expired():
    """Call inside a transaction (lock already held)"""
    now = int(time.time())
    cursor = conn.execute(
        "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
        (now,)
    )
    rows = cursor.fetchall()
    if not rows:
        return
    # Release stock for each expired reservation
    for rid, iid, qty in rows:
        conn.execute(
            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
            (qty, iid)
        )
    # Mark them as expired
    ids = tuple(row[0] for row in rows)
    placeholders = ','.join(['?'] * len(ids))
    conn.execute(
        f"UPDATE reservations SET status='expired' WHERE id IN ({placeholders})",
        ids
    )

# ------------------ HTTP Handler ------------------
class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == '/items':
            self._list_items()
        else:
            self._send_error(404, 'Not Found')

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/items':
            self._create_item()
        elif path == '/reservations':
            self._create_reservation()
        elif re.match(r'^/reservations/\d+/confirm$', path):
            reservation_id = int(path.split('/')[2])
            self._confirm_reservation(reservation_id)
        elif re.match(r'^/reservations/\d+/cancel$', path):
            reservation_id = int(path.split('/')[2])
            self._cancel_reservation(reservation_id)
        else:
            self._send_error(404, 'Not Found')

    # ---------- helpers ----------
    def _read_json_body(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            return None
        if content_length == 0:
            return None
        try:
            raw = self.rfile.read(content_length)
            return json.loads(raw.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _send_error(self, status, message):
        self._send_json({'error': message}, status)

    # ---------- GET /items ----------
    def _list_items(self):
        lock.acquire()
        try:
            cursor = conn.execute(
                "SELECT id, name, stock_total, stock_available FROM items"
            )
            items = []
            for row in cursor.fetchall():
                items.append({
                    'id': row[0],
                    'name': row[1],
                    'stock_total': row[2],
                    'stock_available': row[3]
                })
            self._send_json(items)
        finally:
            lock.release()

    # ---------- POST /items ----------
    def _create_item(self):
        body = self._read_json_body()
        if not body or 'name' not in body or 'stock_total' not in body:
            self._send_error(400, 'Missing parameters')
            return
        name = body['name']
        try:
            stock_total = int(body['stock_total'])
        except (ValueError, TypeError):
            self._send_error(400, 'Invalid stock_total')
            return
        if stock_total <= 0:
            self._send_error(400, 'stock_total must be positive')
            return

        lock.acquire()
        try:
            conn.execute("BEGIN")
            cursor = conn.execute(
                "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                (name, stock_total, stock_total)
            )
            item_id = cursor.lastrowid
            conn.commit()
            self._send_json({
                'id': item_id,
                'name': name,
                'stock_total': stock_total,
                'stock_available': stock_total
            }, status=201)
        except sqlite3.IntegrityError as e:
            conn.rollback()
            self._send_error(400, f'Item already exists or invalid: {str(e)}')
        except Exception as e:
            conn.rollback()
            self._send_error(500, str(e))
        finally:
            lock.release()

    # ---------- POST /reservations ----------
    def _create_reservation(self):
        body = self._read_json_body()
        if not body or 'item_id' not in body or 'quantity' not in body or 'ttl_seconds' not in body:
            self._send_error(400, 'Missing parameters')
            return

        try:
            item_id = int(body['item_id'])
            quantity = int(body['quantity'])
            ttl_seconds = int(body['ttl_seconds'])
        except (ValueError, TypeError):
            self._send_error(400, 'Invalid parameters')
            return

        if quantity <= 0 or ttl_seconds <= 0:
            self._send_error(400, 'Quantity and ttl_seconds must be positive')
            return

        lock.acquire()
        try:
            conn.execute("BEGIN")
            # First cleanup expired reservations
            cleanup_expired()
            # Check item existence and stock
            cursor = conn.execute(
                "SELECT id, stock_available FROM items WHERE id = ?",
                (item_id,)
            )
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                self._send_error(404, 'Item not found')
                return
            if row[1] < quantity:
                conn.rollback()
                self._send_error(409, 'Insufficient stock')
                return
            # Deduct stock
            conn.execute(
                "UPDATE items SET stock_available = stock_available - ? WHERE id = ?",
                (quantity, item_id)
            )
            # Create reservation
            now = int(time.time())
            expires_at = now + ttl_seconds
            cursor = conn.execute(
                "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) "
                "VALUES (?, ?, 'pending', ?, ?)",
                (item_id, quantity, expires_at, now)
            )
            reservation_id = cursor.lastrowid
            conn.commit()
            self._send_json({
                'id': reservation_id,
                'item_id': item_id,
                'quantity': quantity,
                'status': 'pending',
                'expires_at': expires_at,
                'created_at': now
            }, status=201)
        except Exception as e:
            conn.rollback()
            self._send_error(500, str(e))
        finally:
            lock.release()

    # ---------- POST /reservations/{id}/confirm ----------
    def _confirm_reservation(self, reservation_id):
        lock.acquire()
        try:
            conn.execute("BEGIN")
            # Cleanup before to avoid confirming an already expired reservation
            cleanup_expired()
            # Fetch reservation
            cursor = conn.execute(
                "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = ?",
                (reservation_id,)
            )
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                self._send_error(404, 'Reservation not found')
                return
            if row[3] != 'pending':
                conn.rollback()
                self._send_error(400, f"Reservation is not pending (status={row[3]})")
                return
            # Confirm: set status to confirmed
            conn.execute(
                "UPDATE reservations SET status='confirmed' WHERE id = ?",
                (reservation_id,)
            )
            conn.commit()
            self._send_json({
                'id': row[0],
                'item_id': row[1],
                'quantity': row[2],
                'status': 'confirmed',
                'expires_at': row[4],
                'created_at': row[5]
            })
        except Exception as e:
            conn.rollback()
            self._send_error(500, str(e))
        finally:
            lock.release()

    # ---------- POST /reservations/{id}/cancel ----------
    def _cancel_reservation(self, reservation_id):
        lock.acquire()
        try:
            conn.execute("BEGIN")
            # Cleanup before to avoid double release
            cleanup_expired()
            # Fetch reservation
            cursor = conn.execute(
                "SELECT id, item_id, quantity, status, expires_at, created_at FROM reservations WHERE id = ?",
                (reservation_id,)
            )
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                self._send_error(404, 'Reservation not found')
                return
            if row[3] != 'pending':
                conn.rollback()
                self._send_error(400, f"Reservation is not pending (status={row[3]})")
                return
            # Release stock
            conn.execute(
                "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
                (row[2], row[1])
            )
            # Mark as cancelled
            conn.execute(
                "UPDATE reservations SET status='cancelled' WHERE id = ?",
                (reservation_id,)
            )
            conn.commit()
            self._send_json({
                'id': row[0],
                'item_id': row[1],
                'quantity': row[2],
                'status': 'cancelled',
                'expires_at': row[4],
                'created_at': row[5]
            })
        except Exception as e:
            conn.rollback()
            self._send_error(500, str(e))
        finally:
            lock.release()

# ------------------ Main ------------------
if __name__ == '__main__':
    init_db()
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8080), RequestHandler)
    print("Server running on http://127.0.0.1:8080")
    server.serve_forever()
