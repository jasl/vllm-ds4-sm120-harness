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
    with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
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

def cleanup_expired():
    with LOCK:
        with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
            now = datetime.utcnow().isoformat()
            expired = conn.execute(
                "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
                (now,)
            ).fetchall()
            for res in expired:
                conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (res[0],))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                             (res[2], res[1]))
            conn.commit()

class InventoryHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/items":
            cleanup_expired()
            with LOCK:
                with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                    items = conn.execute(
                        "SELECT id, name, stock_total, stock_available FROM items"
                    ).fetchall()
                    result = []
                    for item in items:
                        result.append({
                            "id": item[0],
                            "name": item[1],
                            "stock_total": item[2],
                            "stock_available": item[3]
                        })
                    self._send_json(result)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/items":
            self._handle_create_item()
        elif path == "/reservations":
            self._handle_create_reservation()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            parts = path.split("/")
            if len(parts) == 4 and parts[1] == "reservations" and parts[3] == "confirm":
                try:
                    res_id = int(parts[2])
                    self._handle_confirm(res_id)
                except ValueError:
                    self._send_json({"error": "Invalid reservation ID"}, 400)
            else:
                self._send_json({"error": "Not found"}, 404)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4 and parts[1] == "reservations" and parts[3] == "cancel":
                try:
                    res_id = int(parts[2])
                    self._handle_cancel(res_id)
                except ValueError:
                    self._send_json({"error": "Invalid reservation ID"}, 400)
            else:
                self._send_json({"error": "Not found"}, 404)
        else:
            self._send_json({"error": "Not found"}, 404)

    def _handle_create_item(self):
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            self._send_json({"error": "Invalid parameters: name (string) and stock_total (positive int) required"}, 400)
            return
        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                cursor = conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                item_id = cursor.lastrowid
                self._send_json({
                    "id": item_id,
                    "name": name,
                    "stock_total": stock_total,
                    "stock_available": stock_total
                }, 201)

    def _handle_create_reservation(self):
        cleanup_expired()
        body = self._read_body()
        if body is None:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            self._send_json({"error": "Invalid parameters: item_id (int) and quantity (positive int) required"}, 400)
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            self._send_json({"error": "Invalid ttl_seconds (positive number)"), 400)
            return

        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                item = conn.execute("SELECT id, stock_available FROM items WHERE id=?", (item_id,)).fetchone()
                if not item:
                    self._send_json({"error": "Item not found"}, 404)
                    return
                if item[1] < quantity:
                    self._send_json({"error": "Insufficient stock"}, 409)
                    return
                now = datetime.utcnow()
                expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
                created_at = now.isoformat()
                conn.execute("UPDATE items SET stock_available = stock_available - ? WHERE id=?",
                             (quantity, item_id))
                cursor = conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at, created_at)
                )
                conn.commit()
                self._send_json({
                    "id": cursor.lastrowid,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": created_at
                }, 201)

    def _handle_confirm(self, res_id):
        cleanup_expired()
        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                res = conn.execute(
                    "SELECT id, status FROM reservations WHERE id=?", (res_id,)
                ).fetchone()
                if not res:
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                if res[1] != "pending":
                    self._send_json({"error": f"Reservation already {res[1]}, cannot confirm"}, 400)
                    return
                conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (res_id,))
                conn.commit()
                self._send_json({"message": "Confirmed", "id": res_id})

    def _handle_cancel(self, res_id):
        cleanup_expired()
        with LOCK:
            with sqlite3.connect(DB_PATH, check_same_thread=False) as conn:
                res = conn.execute(
                    "SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (res_id,)
                ).fetchone()
                if not res:
                    self._send_json({"error": "Reservation not found"}, 404)
                    return
                if res[3] != "pending":
                    self._send_json({"error": f"Reservation already {res[3]}, cannot cancel"}, 400)
                    return
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (res_id,))
                conn.execute("UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                             (res[2], res[1]))
                conn.commit()
                self._send_json({"message": "Cancelled", "id": res_id})

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), InventoryHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
