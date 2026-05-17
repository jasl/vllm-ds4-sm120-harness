#!/usr/bin/env python3
import json
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import re

# Database file
DB_FILE = 'inventory.db'

# Global database connection and lock
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
conn.execute('PRAGMA journal_mode=WAL')  # optional, for better concurrency
db_lock = threading.Lock()

def init_db():
    """Initialize database tables if not exist."""
    with db_lock:
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                stock_total INTEGER NOT NULL,
                stock_available INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','confirmed','cancelled','expired')),
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY(item_id) REFERENCES items(id)
            );
        ''')
        conn.commit()

def clean_expired():
    """Cancel expired pending reservations and release stock."""
    now = time.time()
    rows = conn.execute('''
        SELECT id, item_id, quantity FROM reservations WHERE status = ? AND expires_at <= ?
    ''', ('pending', now)).fetchall()
    if rows:
        # Release stock for each expired reservation
        for rid, iid, qty in rows:
            conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (qty, iid))
        # Mark as expired
        ids = tuple(r[0] for r in rows)
        placeholders = ','.join(['?'] * len(ids))
        conn.execute(
            'UPDATE reservations SET status = ? WHERE id IN ({})'.format(placeholders),
            ('expired',) + ids
        )
        conn.commit()

class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for inventory reservation service."""

    def do_GET(self):
        status, data = self.handle_request(body=None)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else b''
        body_json = None
        if body:
            try:
                body_json = json.loads(body)
            except json.JSONDecodeError:
                body_json = None
        status, data = self.handle_request(body=body_json)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def handle_request(self, body):
        """Process request under lock."""
        method = self.command
        path = self.path
        with db_lock:
            try:
                clean_expired()

                if method == 'GET' and path == '/items':
                    return self.get_items()

                if method == 'POST':
                    if path == '/items':
                        return self.add_item(body)
                    elif path == '/reservations':
                        return self.create_reservation(body)
                    else:
                        # Check for confirm/cancel
                        m = re.fullmatch(r'/reservations/(\d+)/(confirm|cancel)', path)
                        if m:
                            res_id = int(m.group(1))
                            action = m.group(2)
                            if action == 'confirm':
                                return self.confirm_reservation(res_id)
                            else:
                                return self.cancel_reservation(res_id)

                return (404, {"error": "Not found"})
            except Exception as e:
                conn.rollback()
                return (500, {"error": f"Internal server error: {str(e)}"})

    def get_items(self):
        cur = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
        items = []
        for row in cur.fetchall():
            items.append({
                "id": row[0],
                "name": row[1],
                "stock_total": row[2],
                "stock_available": row[3]
            })
        return (200, items)

    def add_item(self, body):
        if body is None:
            return (400, {"error": "Invalid JSON"})
        name = body.get('name')
        stock_total = body.get('stock_total')
        if not name or not isinstance(stock_total, int) or stock_total <= 0:
            return (400, {"error": "Invalid parameters: name (string) and stock_total (positive int) required"})
        cur = conn.execute(
            'INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
            (name, stock_total, stock_total)
        )
        conn.commit()
        new_id = cur.lastrowid
        return (201, {
            "id": new_id,
            "name": name,
            "stock_total": stock_total,
            "stock_available": stock_total
        })

    def create_reservation(self, body):
        if body is None:
            return (400, {"error": "Invalid JSON"})
        item_id = body.get('item_id')
        quantity = body.get('quantity')
        ttl_seconds = body.get('ttl_seconds')
        if not all([isinstance(item_id, int), isinstance(quantity, int), isinstance(ttl_seconds, int)]):
            return (400, {"error": "Invalid parameters: item_id, quantity, ttl_seconds must be integers"})
        if quantity <= 0 or ttl_seconds <= 0:
            return (400, {"error": "Quantity and ttl_seconds must be positive"})

        # Check item existence and available stock
        cur = conn.execute('SELECT id, stock_available FROM items WHERE id = ?', (item_id,))
        item = cur.fetchone()
        if not item:
            return (404, {"error": "Item not found"})
        available = item[1]
        if available < quantity:
            return (409, {"error": "Insufficient stock"})

        # Reserve stock
        conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id = ?', (quantity, item_id))
        now = time.time()
        expires = now + ttl_seconds
        cur2 = conn.execute(
            'INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, ?, ?, ?)',
            (item_id, quantity, 'pending', expires, now)
        )
        res_id = cur2.lastrowid
        conn.commit()
        return (201, {
            "id": res_id,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires,
            "created_at": now
        })

    def confirm_reservation(self, res_id):
        cur = conn.execute('SELECT id, status FROM reservations WHERE id = ?', (res_id,))
        row = cur.fetchone()
        if not row:
            return (404, {"error": "Reservation not found"})
        if row[1] != 'pending':
            return (400, {"error": f"Reservation status must be pending to confirm, current: {row[1]}"})
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('confirmed', res_id))
        conn.commit()
        return (200, {"id": res_id, "status": "confirmed"})

    def cancel_reservation(self, res_id):
        cur = conn.execute('SELECT id, status, item_id, quantity FROM reservations WHERE id = ?', (res_id,))
        row = cur.fetchone()
        if not row:
            return (404, {"error": "Reservation not found"})
        if row[1] != 'pending':
            return (400, {"error": f"Reservation status must be pending to cancel, current: {row[1]}"})
        item_id = row[2]
        quantity = row[3]
        # Release stock
        conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?', (quantity, item_id))
        conn.execute('UPDATE reservations SET status = ? WHERE id = ?', ('cancelled', res_id))
        conn.commit()
        return (200, {"id": res_id, "status": "cancelled"})

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""
    daemon_threads = True

if __name__ == "__main__":
    init_db()
    server = ThreadedHTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print("Server starting on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
