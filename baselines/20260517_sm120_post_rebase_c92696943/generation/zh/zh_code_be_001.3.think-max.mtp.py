import http.server
import socketserver
import json
import sqlite3
import time
import os
import threading
from urllib.parse import urlparse

DB_PATH = "inventory.db"
write_lock = threading.Lock()


def init_db():
    """Initialize database with required tables."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    ''')
    conn.execute('''
        CREATE INDEX IF NOT EXISTS idx_res_status_expires
        ON reservations(status, expires_at)
    ''')
    conn.commit()
    conn.close()


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class RequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "InventoryAPI/1.0"

    # ------------------------------------------------------------------
    #  Utility methods
    # ------------------------------------------------------------------
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status)

    def _read_json(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _parse_int(s):
        try:
            return int(s)
        except (ValueError, TypeError):
            return None

    # ------------------------------------------------------------------
    #  Database helper – cleanup expired reservations
    # ------------------------------------------------------------------
    def _cleanup_expired(self, conn):
        """Must be called while write_lock is held."""
        now = time.time()
        cursor = conn.execute('''
            SELECT id, item_id, quantity FROM reservations
            WHERE status='pending' AND expires_at <= ?
        ''', (now,))
        rows = cursor.fetchall()
        if rows:
            conn.execute('BEGIN')
            try:
                for row in rows:
                    conn.execute('UPDATE reservations SET status=? WHERE id=?',
                                 ('expired', row['id']))
                    conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id=?',
                                 (row['quantity'], row['item_id']))
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    # ------------------------------------------------------------------
    #  Route handlers – GET
    # ------------------------------------------------------------------
    def _handle_get_items(self, conn):
        cursor = conn.execute('SELECT id, name, stock_total, stock_available FROM items')
        items = [dict(row) for row in cursor.fetchall()]
        self._send_json(items)

    # ------------------------------------------------------------------
    #  Route handlers – POST
    # ------------------------------------------------------------------
    def _handle_create_item(self, conn, data):
        if not data or 'name' not in data or 'stock_total' not in data:
            self._send_error("Missing required fields: name, stock_total", 400)
            return
        name = data['name'].strip()
        if not name:
            self._send_error("name must not be empty", 400)
            return
        stock_total = data['stock_total']
        if not isinstance(stock_total, int) or stock_total <= 0:
            self._send_error("stock_total must be a positive integer", 400)
            return

        conn.execute('BEGIN')
        try:
            conn.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                         (name, stock_total, stock_total))
            conn.commit()
            item_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            item = {
                'id': item_id,
                'name': name,
                'stock_total': stock_total,
                'stock_available': stock_total
            }
            self._send_json(item, 201)
        except sqlite3.IntegrityError:
            conn.rollback()
            self._send_error(f"Item with name '{name}' already exists", 409)

    def _handle_create_reservation(self, conn, data):
        if not data or 'item_id' not in data or 'quantity' not in data or 'ttl_seconds' not in data:
            self._send_error("Missing required fields: item_id, quantity, ttl_seconds", 400)
            return
        item_id = data['item_id']
        quantity = data['quantity']
        ttl_seconds = data['ttl_seconds']
        if not isinstance(item_id, int) or item_id <= 0:
            self._send_error("item_id must be a positive integer", 400)
            return
        if not isinstance(quantity, int) or quantity <= 0:
            self._send_error("quantity must be a positive integer", 400)
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_error("ttl_seconds must be a positive number", 400)
            return

        conn.execute('BEGIN')
        try:
            item = conn.execute('SELECT id, stock_available FROM items WHERE id=?',
                                (item_id,)).fetchone()
            if not item:
                conn.rollback()
                self._send_error("Item not found", 404)
                return
            if item['stock_available'] < quantity:
                conn.rollback()
                self._send_error("Insufficient stock", 409)
                return

            # Deduct stock
            conn.execute('UPDATE items SET stock_available = stock_available - ? WHERE id=?',
                         (quantity, item_id))
            # Create reservation
            now = time.time()
            created_at = now
            expires_at = now + ttl_seconds
            conn.execute('''
                INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                VALUES (?, ?, 'pending', ?, ?)
            ''', (item_id, quantity, expires_at, created_at))
            conn.commit()

            reservation_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            reservation = {
                'id': reservation_id,
                'item_id': item_id,
                'quantity': quantity,
                'status': 'pending',
                'expires_at': expires_at,
                'created_at': created_at
            }
            self._send_json(reservation, 201)
        except Exception:
            conn.rollback()
            raise

    def _handle_confirm_reservation(self, conn, reservation_id):
        conn.execute('BEGIN')
        try:
            row = conn.execute('SELECT * FROM reservations WHERE id=?',
                               (reservation_id,)).fetchone()
            if not row:
                conn.rollback()
                self._send_error("Reservation not found", 404)
                return
            if row['status'] != 'pending':
                conn.rollback()
                self._send_error(
                    f"Cannot confirm reservation with status '{row['status']}'", 409)
                return
            conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?",
                         (reservation_id,))
            conn.commit()
            updated = conn.execute('SELECT * FROM reservations WHERE id=?',
                                   (reservation_id,)).fetchone()
            self._send_json(dict(updated), 200)
        except Exception:
            conn.rollback()
            raise

    def _handle_cancel_reservation(self, conn, reservation_id):
        conn.execute('BEGIN')
        try:
            row = conn.execute('SELECT * FROM reservations WHERE id=?',
                               (reservation_id,)).fetchone()
            if not row:
                conn.rollback()
                self._send_error("Reservation not found", 404)
                return
            if row['status'] != 'pending':
                conn.rollback()
                self._send_error(
                    f"Cannot cancel reservation with status '{row['status']}'", 409)
                return
            # Release stock
            conn.execute('UPDATE items SET stock_available = stock_available + ? WHERE id=?',
                         (row['quantity'], row['item_id']))
            conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?",
                         (reservation_id,))
            conn.commit()
            updated = conn.execute('SELECT * FROM reservations WHERE id=?',
                                   (reservation_id,)).fetchone()
            self._send_json(dict(updated), 200)
        except Exception:
            conn.rollback()
            raise

    # ------------------------------------------------------------------
    #  HTTP method dispatchers
    # ------------------------------------------------------------------
    def do_GET(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.isolation_level = None

            # Clean up expired reservations before every request
            with write_lock:
                self._cleanup_expired(conn)

            parsed = urlparse(self.path)
            path = parsed.path.strip('/')
            parts = path.split('/')

            if len(parts) == 1 and parts[0] == 'items':
                self._handle_get_items(conn)
            else:
                self._send_error("Not Found", 404)
        except Exception as e:
            self._send_error(f"Internal Server Error: {str(e)}", 500)
        finally:
            if conn:
                conn.close()

    def do_POST(self):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.isolation_level = None

            # Clean up expired reservations before every request
            with write_lock:
                self._cleanup_expired(conn)

            parsed = urlparse(self.path)
            path = parsed.path.strip('/')
            parts = path.split('/')

            if len(parts) == 1 and parts[0] == 'items':
                # POST /items
                data = self._read_json()
                with write_lock:
                    self._handle_create_item(conn, data)
            elif len(parts) == 1 and parts[0] == 'reservations':
                # POST /reservations
                data = self._read_json()
                with write_lock:
                    self._handle_create_reservation(conn, data)
            elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'confirm':
                # POST /reservations/{id}/confirm
                rid = self._parse_int(parts[1])
                if rid is None:
                    self._send_error("Invalid reservation id", 400)
                    return
                with write_lock:
                    self._handle_confirm_reservation(conn, rid)
            elif len(parts) == 3 and parts[0] == 'reservations' and parts[2] == 'cancel':
                # POST /reservations/{id}/cancel
                rid = self._parse_int(parts[1])
                if rid is None:
                    self._send_error("Invalid reservation id", 400)
                    return
                with write_lock:
                    self._handle_cancel_reservation(conn, rid)
            else:
                self._send_error("Not Found", 404)
        except Exception as e:
            self._send_error(f"Internal Server Error: {str(e)}", 500)
        finally:
            if conn:
                conn.close()


def main():
    init_db()
    server = ThreadingHTTPServer(('127.0.0.1', 8080), RequestHandler)
    print("Starting server on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
