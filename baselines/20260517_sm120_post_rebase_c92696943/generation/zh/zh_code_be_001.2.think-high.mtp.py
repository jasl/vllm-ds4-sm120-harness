#!/usr/bin/env python3
"""
Small HTTP API service for inventory reservation.
Uses only Python 3 standard library.
"""

import json
import sqlite3
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ------------------------------------------------------------
# Database setup
# ------------------------------------------------------------
DB_FILE = "inventory.db"
db_lock = threading.Lock()

def init_db():
    """Create tables if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
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
                expires_at REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        """)
        conn.commit()

# ------------------------------------------------------------
# Expired reservation cleanup (called before each request)
# ------------------------------------------------------------
def cleanup_expired():
    """Release stock for pending reservations that have expired.
    Runs inside a transaction."""
    now = time.time()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("BEGIN")
        # Find expired pending reservations
        rows = conn.execute(
            "SELECT id, item_id, quantity FROM reservations WHERE status='pending' AND expires_at < ?",
            (now,)
        ).fetchall()
        if rows:
            for rid, item_id, qty in rows:
                # Update reservation status to expired
                conn.execute("UPDATE reservations SET status='expired' WHERE id=?", (rid,))
                # Restore stock
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                    (qty, item_id)
                )
        conn.execute("COMMIT")

# ------------------------------------------------------------
# Helper: send JSON response
# ------------------------------------------------------------
def send_json(handler, data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)

def send_error(handler, message, status=400):
    send_json(handler, {"error": message}, status)

# ------------------------------------------------------------
# Request handler
# ------------------------------------------------------------
class InventoryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for inventory API."""

    def do_GET(self):
        with db_lock:
            cleanup_expired()
            self._handle_get()

    def do_POST(self):
        with db_lock:
            cleanup_expired()
            self._handle_post()

    def _handle_get(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self._list_items()
        else:
            send_error(self, "Not found", 404)

    def _handle_post(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if path == "/items":
            self._add_item()
        elif path == "/reservations":
            self._create_reservation()
        elif path.startswith("/reservations/") and path.endswith("/confirm"):
            # Extract reservation id
            parts = path.split("/")
            if len(parts) == 4:
                try:
                    rid = int(parts[2])
                except ValueError:
                    send_error(self, "Invalid reservation id", 400)
                    return
                self._confirm_reservation(rid)
            else:
                send_error(self, "Invalid path", 404)
        elif path.startswith("/reservations/") and path.endswith("/cancel"):
            parts = path.split("/")
            if len(parts) == 4:
                try:
                    rid = int(parts[2])
                except ValueError:
                    send_error(self, "Invalid reservation id", 400)
                    return
                self._cancel_reservation(rid)
            else:
                send_error(self, "Invalid path", 404)
        else:
            send_error(self, "Not found", 404)

    # ---- GET /items ----
    def _list_items(self):
        with sqlite3.connect(DB_FILE) as conn:
            rows = conn.execute("SELECT id, name, stock_total, stock_available FROM items").fetchall()
        items = []
        for r in rows:
            items.append({
                "id": r[0],
                "name": r[1],
                "stock_total": r[2],
                "stock_available": r[3]
            })
        send_json(self, items)

    # ---- POST /items ----
    def _add_item(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            send_error(self, "Empty body", 400)
            return
        try:
            body = json.loads(self.rfile.read(content_len))
        except json.JSONDecodeError:
            send_error(self, "Invalid JSON", 400)
            return
        name = body.get("name")
        stock_total = body.get("stock_total")
        if not name or not isinstance(stock_total, int) or stock_total < 0:
            send_error(self, "Invalid or missing 'name' or 'stock_total'", 400)
            return
        try:
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute(
                    "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
                    (name, stock_total, stock_total)
                )
                conn.commit()
                # Get the newly created item id
                cursor = conn.execute("SELECT last_insert_rowid()")
                new_id = cursor.fetchone()[0]
            send_json(self, {"id": new_id, "name": name, "stock_total": stock_total, "stock_available": stock_total}, 201)
        except sqlite3.Error as e:
            send_error(self, f"Database error: {str(e)}", 500)

    # ---- POST /reservations ----
    def _create_reservation(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            send_error(self, "Empty body", 400)
            return
        try:
            body = json.loads(self.rfile.read(content_len))
        except json.JSONDecodeError:
            send_error(self, "Invalid JSON", 400)
            return
        item_id = body.get("item_id")
        quantity = body.get("quantity")
        ttl_seconds = body.get("ttl_seconds")
        if not isinstance(item_id, int) or not isinstance(quantity, int) or quantity <= 0:
            send_error(self, "Invalid or missing 'item_id' or 'quantity'", 400)
            return
        if not isinstance(ttl_seconds, (int, float)) or ttl_seconds <= 0:
            send_error(self, "Invalid or missing 'ttl_seconds'", 400)
            return

        now = time.time()
        expires_at = now + ttl_seconds

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("BEGIN")
            try:
                # Check item exists and has enough stock
                row = conn.execute(
                    "SELECT id, stock_available FROM items WHERE id=?", (item_id,)
                ).fetchone()
                if row is None:
                    conn.execute("ROLLBACK")
                    send_error(self, "Item not found", 404)
                    return
                if row[1] < quantity:
                    conn.execute("ROLLBACK")
                    send_error(self, "Insufficient stock", 409)
                    return

                # Create reservation
                conn.execute(
                    "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) VALUES (?, ?, 'pending', ?, ?)",
                    (item_id, quantity, expires_at, now)
                )
                cursor = conn.execute("SELECT last_insert_rowid()")
                new_rid = cursor.fetchone()[0]

                # Update available stock
                conn.execute(
                    "UPDATE items SET stock_available = stock_available - ? WHERE id=?",
                    (quantity, item_id)
                )
                conn.execute("COMMIT")
                send_json(self, {
                    "id": new_rid,
                    "item_id": item_id,
                    "quantity": quantity,
                    "status": "pending",
                    "expires_at": expires_at,
                    "created_at": now
                }, 201)
            except sqlite3.Error as e:
                conn.execute("ROLLBACK")
                send_error(self, f"Database error: {str(e)}", 500)

    # ---- POST /reservations/{id}/confirm ----
    def _confirm_reservation(self, rid):
        with sqlite3.connect(DB_FILE) as conn:
            row = conn.execute(
                "SELECT id, status FROM reservations WHERE id=?", (rid,)
            ).fetchone()
            if row is None:
                send_error(self, "Reservation not found", 404)
                return
            if row[1] != "pending":
                send_error(self, f"Reservation cannot be confirmed (status: {row[1]})", 400)
                return
            conn.execute("UPDATE reservations SET status='confirmed' WHERE id=?", (rid,))
            conn.commit()
        send_json(self, {"id": rid, "status": "confirmed"})

    # ---- POST /reservations/{id}/cancel ----
    def _cancel_reservation(self, rid):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("BEGIN")
            try:
                row = conn.execute(
                    "SELECT id, item_id, quantity, status FROM reservations WHERE id=?", (rid,)
                ).fetchone()
                if row is None:
                    conn.execute("ROLLBACK")
                    send_error(self, "Reservation not found", 404)
                    return
                if row[3] != "pending":
                    conn.execute("ROLLBACK")
                    send_error(self, f"Reservation cannot be cancelled (status: {row[3]})", 400)
                    return
                item_id = row[1]
                quantity = row[2]
                # Update reservation status
                conn.execute("UPDATE reservations SET status='cancelled' WHERE id=?", (rid,))
                # Restore stock
                conn.execute(
                    "UPDATE items SET stock_available = stock_available + ? WHERE id=?",
                    (quantity, item_id)
                )
                conn.execute("COMMIT")
                send_json(self, {"id": rid, "status": "cancelled"})
            except sqlite3.Error as e:
                conn.execute("ROLLBACK")
                send_error(self, f"Database error: {str(e)}", 500)

    # ---- Silence logs ----
    def log_message(self, format, *args):
        return

# ------------------------------------------------------------
# Main entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    server = HTTPServer(("127.0.0.1", 8080), InventoryHandler)
    print("Inventory API server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()
