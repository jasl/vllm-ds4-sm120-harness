import sqlite3
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

DB_PATH = 'inventory.db'
_lock = threading.Lock()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL,
            stock_available INTEGER NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        )
    ''')
    conn.commit()
    conn.close()

def clean_expired_pending():
    conn = get_db()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('''
        SELECT id, item_id, quantity FROM reservations
        WHERE status = 'pending' AND expires_at < ?
    ''', (now,))
    expired = c.fetchall()
    for row in expired:
        c.execute('''
            UPDATE items SET stock_available = stock_available + ?
            WHERE id = ?
        ''', (row['quantity'], row['item_id']))
        c.execute('DELETE FROM reservations WHERE id = ?', (row['id'],))
    conn.commit()
    conn.close()

class InventoryHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        if path == '/items':
            with _lock:
                clean_expired_pending()
                conn = get_db()
                c = conn.cursor()
                c.execute('SELECT id, name, stock_total, stock_available FROM items')
                items = [dict(row) for row in c.fetchall()]
                conn.close()
            self._send_json(items)
        else:
            self._send_json({'error': 'Not Found'}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        body = self._read_body()

        if path == '/items':
            name = body.get('name')
            stock_total = body.get('stock_total')
            if not name or not isinstance(stock_total, int) or stock_total < 0:
                self._send_json({'error': 'Invalid parameters'}, 400)
                return
            with _lock:
                conn = get_db()
                c = conn.cursor()
                c.execute('INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)',
                          (name, stock_total, stock_total))
                conn.commit()
                item_id = c.lastrowid
                conn.close()
            self._send_json({'id': item_id, 'name': name, 'stock_total': stock_total, 'stock_available': stock_total}, 201)

        elif path == '/reservations':
            item_id = body.get('item_id')
            quantity = body.get('quantity')
            ttl_seconds = body.get('ttl_seconds', 300)
            if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0 or not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
                self._send_json({'error': 'Invalid parameters'}, 400)
                return
            with _lock:
                clean_expired_pending()
                conn = get_db()
                c = conn.cursor()
                c.execute('SELECT stock_available FROM items WHERE id = ?', (item_id,))
                row = c.fetchone()
                if not row:
                    conn.close()
                    self._send_json({'error': 'Item not found'}, 404)
                    return
                if row['stock_available'] < quantity:
                    conn.close()
                    self._send_json({'error': 'Insufficient stock'}, 409)
                    return
                now = datetime.utcnow()
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
                created_at = now.isoformat()
                c.execute('''
                    INSERT INTO reservations (item_id, quantity, status, expires_at, created_at)
                    VALUES (?, ?, 'pending', ?, ?)
                ''', (item_id, quantity, expires_at, created_at))
                c.execute('UPDATE items SET stock_available = stock_available - ? WHERE id = ?',
                          (quantity, item_id))
                conn.commit()
                reservation_id = c.lastrowid
                conn.close()
            self._send_json({'id': reservation_id, 'item_id': item_id, 'quantity': quantity,
                            'status': 'pending', 'expires_at': expires_at, 'created_at': created_at}, 201)

        elif path.startswith('/reservations/') and path.endswith('/confirm'):
            parts = path.split('/')
            if len(parts) != 4:
                self._send_json({'error': 'Invalid URL'}, 400)
                return
            try:
                reservation_id = int(parts[2])
            except ValueError:
                self._send_json({'error': 'Invalid reservation ID'}, 400)
                return
            with _lock:
                clean_expired_pending()
                conn = get_db()
                c = conn.cursor()
                c.execute('SELECT status FROM reservations WHERE id = ?', (reservation_id,))
                row = c.fetchone()
                if not row:
                    conn.close()
                    self._send_json({'error': 'Reservation not found'}, 404)
                    return
                if row['status'] != 'pending':
                    conn.close()
                    self._send_json({'error': 'Reservation already processed'}, 400)
                    return
                c.execute('UPDATE reservations SET status = ? WHERE id = ?',
                          ('confirmed', reservation_id))
                conn.commit()
                conn.close()
            self._send_json({'message': 'Reservation confirmed'})

        elif path.startswith('/reservations/') and path.endswith('/cancel'):
            parts = path.split('/')
            if len(parts) != 4:
                self._send_json({'error': 'Invalid URL'}, 400)
                return
            try:
                reservation_id = int(parts[2])
            except ValueError:
                self._send_json({'error': 'Invalid reservation ID'}, 400)
                return
            with _lock:
                clean_expired_pending()
                conn = get_db()
                c = conn.cursor()
                c.execute('SELECT status, item_id, quantity FROM reservations WHERE id = ?', (reservation_id,))
                row = c.fetchone()
                if not row:
                    conn.close()
                    self._send_json({'error': 'Reservation not found'}, 404)
                    return
                if row['status'] != 'pending':
                    conn.close()
                    self._send_json({'error': 'Reservation already processed'}, 400)
                    return
                c.execute('UPDATE items SET stock_available = stock_available + ? WHERE id = ?',
                          (row['quantity'], row['item_id']))
                c.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
                conn.commit()
                conn.close()
            self._send_json({'message': 'Reservation cancelled'})

        else:
            self._send_json({'error': 'Not Found'}, 404)

    def do_PUT(self):
        self._send_json({'error': 'Method Not Allowed'}, 405)

    def do_DELETE(self):
        self._send_json({'error': 'Method Not Allowed'}, 405)

if __name__ == '__main__':
    init_db()
    server = HTTPServer(('127.0.0.1', 8080), InventoryHandler)
    print('Server running on http://127.0.0.1:8080')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
