#!/usr/bin/env python3
"""
Single-file HTTP API service for inventory reservations.
Uses only Python 3 standard library.
"""

import json
import sqlite3
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

DB_FILE = "inventory.db"


class AppError(Exception):
    """Application-level error with HTTP status code and message."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the inventory reservation API."""

    # ------------------------------------------------------------------
    #  Helper methods for sending responses
    # ------------------------------------------------------------------
    def _send_json(self, status: int, data):
        """Send a JSON response with the given status code and data."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str):
        """Send a JSON error response."""
        self._send_json(status, {"error": message})

    # ------------------------------------------------------------------
    #  Database connection
    # ------------------------------------------------------------------
    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a new database connection."""
        conn = sqlite3.connect(DB_FILE, timeout=5, isolation_level=None)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ------------------------------------------------------------------
    #  Path parsing
    # ------------------------------------------------------------------
    def _parse_path(self):
        """Parse the request path into a list of components."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            return []
        return path.split("/")[1:]

    # ------------------------------------------------------------------
    #  Request body parsing
    # ------------------------------------------------------------------
    def _read_json_body(self) -> dict:
        """Read and parse the JSON request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            raise AppError(400, "Request body is empty")
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise AppError(400, "Invalid JSON") from exc
        if not isinstance(data, dict):
            raise AppError(400, "JSON body must be an object")
        return data

    # ------------------------------------------------------------------
    #  Business logic – queries
    # ------------------------------------------------------------------
    def _list_items(self, conn):
        """Return a list of all items with their current stock."""
        cursor = conn.execute(
            "SELECT id, name, stock_total, stock_available FROM items ORDER BY id"
        )
        rows = cursor.fetchall()
        items = []
        for row in rows:
            items.append({
                "id": row[0],
                "name": row[1],
                "stock_total": row[2],
                "stock_available": row[3],
            })
        return {"items": items}

    def _create_item(self, conn, data: dict) -> dict:
        """Create a new item and return it."""
        name = data.get("name")
        stock_total = data.get("stock_total")

        if not name or not isinstance(name, str) or not name.strip():
            raise AppError(400, "Invalid or missing 'name'")
        if not isinstance(stock_total, int) or stock_total <= 0:
            raise AppError(400, "Invalid or missing 'stock_total', must be a positive integer")

        cursor = conn.execute(
            "INSERT INTO items (name, stock_total, stock_available) VALUES (?, ?, ?)",
            (name, stock_total, stock_total),
        )
        return {
            "id": cursor.lastrowid,
            "name": name,
            "stock_total": stock_total,
            "stock_available": stock_total,
        }

    def _create_reservation(self, conn, data: dict) -> dict:
        """Create a new reservation, deduct stock, return the reservation."""
        item_id = data.get("item_id")
        quantity = data.get("quantity")
        ttl_seconds = data.get("ttl_seconds")

        if not isinstance(item_id, int) or item_id <= 0:
            raise AppError(400, "Invalid or missing 'item_id'")
        if not isinstance(quantity, int) or quantity <= 0:
            raise AppError(400, "Invalid or missing 'quantity', must be a positive integer")
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            raise AppError(400, "Invalid or missing 'ttl_seconds', must be a positive integer")

        # check item existence
        cursor = conn.execute("SELECT id FROM items WHERE id = ?", (item_id,))
        if cursor.fetchone() is None:
            raise AppError(404, "Item not found")

        # atomically deduct stock if enough available
        cursor = conn.execute(
            "UPDATE items SET stock_available = stock_available - ? "
            "WHERE id = ? AND stock_available >= ?",
            (quantity, item_id, quantity),
        )
        if cursor.rowcount == 0:
            raise AppError(409, "Insufficient stock")

        now = time.time()
        expires_at = now + ttl_seconds
        cursor = conn.execute(
            "INSERT INTO reservations (item_id, quantity, status, expires_at, created_at) "
            "VALUES (?, ?, 'pending', ?, ?)",
            (item_id, quantity, expires_at, now),
        )
        return {
            "id": cursor.lastrowid,
            "item_id": item_id,
            "quantity": quantity,
            "status": "pending",
            "expires_at": expires_at,
            "created_at": now,
        }

    def _confirm_reservation(self, conn, res_id: int) -> dict:
        """Confirm a pending reservation."""
        cursor = conn.execute(
            "SELECT id, item_id, quantity, status, expires_at, created_at "
            "FROM reservations WHERE id = ?",
            (res_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise AppError(404, "Reservation not found")
        if row[3] != "pending":
            raise AppError(400, f"Reservation status is '{row[3]}', expected 'pending'")

        conn.execute(
            "UPDATE reservations SET status = 'confirmed' WHERE id = ?",
            (res_id,),
        )
        return {
            "id": row[0],
            "item_id": row[1],
            "quantity": row[2],
            "status": "confirmed",
            "expires_at": row[4],
            "created_at": row[5],
        }

    def _cancel_reservation(self, conn, res_id: int) -> dict:
        """Cancel a pending reservation and release stock."""
        cursor = conn.execute(
            "SELECT id, item_id, quantity, status, expires_at, created_at "
            "FROM reservations WHERE id = ?",
            (res_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise AppError(404, "Reservation not found")
        if row[3] != "pending":
            raise AppError(400, f"Reservation status is '{row[3]}', expected 'pending'")

        # change status first, then release stock (both inside the same transaction)
        conn.execute(
            "UPDATE reservations SET status = 'cancelled' WHERE id = ? AND status = 'pending'",
            (res_id,),
        )
        conn.execute(
            "UPDATE items SET stock_available = stock_available + ? WHERE id = ?",
            (row[2], row[1]),
        )
        return {
            "id": row[0],
            "item_id": row[1],
            "quantity": row[2],
            "status": "cancelled",
            "expires_at": row[4],
            "created_at": row[5],
        }

    # ------------------------------------------------------------------
    #  Cleanup of expired pending reservations
    # ------------------------------------------------------------------
    def _cleanup_expired(self, conn):
        """Release stock for expired pending reservations and mark them as expired."""
        now = time.time()
        # release stock
        conn.execute(
            """
            UPDATE items
            SET stock_available = stock_available + COALESCE(
                (SELECT SUM(quantity) FROM reservations
                 WHERE status='pending' AND expires_at < ? AND reservations.item_id = items.id),
            0)
            WHERE id IN (SELECT item_id FROM reservations WHERE status='pending' AND expires_at < ?)
            """,
            (now, now),
        )
        # mark reservations as expired
        conn.execute(
            "UPDATE reservations SET status='expired' WHERE status='pending' AND expires_at < ?",
            (now,),
        )

    # ------------------------------------------------------------------
    #  Request handling – transaction wrapper
    # ------------------------------------------------------------------
    def _run_in_transaction(self, handler):
        """
        Execute a handler inside two sequential transactions:
        1. Cleanup expired reservations (committed separately).
        2. The actual business logic (committed on success, rolled back on error).
        """
        conn = None
        try:
            conn = self._get_connection()

            # ---- cleanup transaction ----
            conn.execute("BEGIN IMMEDIATE")
            self._cleanup_expired(conn)
            conn.commit()

            # ---- business transaction ----
            conn.execute("BEGIN IMMEDIATE")
            status, result = handler(conn)
            conn.commit()

            self._send_json(status, result)

        except AppError as exc:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            self._send_error(exc.status_code, exc.message)

        except sqlite3.OperationalError as exc:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if "database is locked" in str(exc):
                self._send_error(503, "Service Unavailable: database locked")
            else:
                self._send_error(500, f"Database error: {exc}")

        except Exception as exc:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            self._send_error(500, f"Internal server error: {exc}")

        finally:
            if conn:
                conn.close()

    # ------------------------------------------------------------------
    #  GET handler
    # ------------------------------------------------------------------
    def _handle_get(self, conn):
        parts = self._parse_path()
        if parts == ["items"]:
            data = self._list_items(conn)
            return 200, data
        raise AppError(404, "Not found")

    def do_GET(self):
        self._run_in_transaction(self._handle_get)

    # ------------------------------------------------------------------
    #  POST handler
    # ------------------------------------------------------------------
    def _handle_post(self, conn):
        parts = self._parse_path()

        if parts == ["items"]:
            data = self._read_json_body()
            result = self._create_item(conn, data)
            return 201, result

        if parts == ["reservations"]:
            data = self._read_json_body()
            result = self._create_reservation(conn, data)
            return 201, result

        if len(parts) == 3 and parts[0] == "reservations" and parts[2] == "confirm":
            try:
                res_id = int(parts[1])
            except ValueError as exc:
                raise AppError(400, "Invalid reservation ID") from exc
            result = self._confirm_reservation(conn, res_id)
            return 200, result

        if len(parts) == 3 and parts[0] == "reservations" and parts[2] == "cancel":
            try:
                res_id = int(parts[1])
            except ValueError as exc:
                raise AppError(400, "Invalid reservation ID") from exc
            result = self._cancel_reservation(conn, res_id)
            return 200, result

        raise AppError(404, "Not found")

    def do_POST(self):
        self._run_in_transaction(self._handle_post)

    # ------------------------------------------------------------------
    #  Suppress default logging
    # ------------------------------------------------------------------
    def log_message(self, format, *args):
        pass


# ------------------------------------------------------------------
#  Server initialisation
# ------------------------------------------------------------------
def init_db():
    """Create database tables if they do not exist."""
    conn = sqlite3.connect(DB_FILE, timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_total INTEGER NOT NULL CHECK(stock_total >= 0),
            stock_available INTEGER NOT NULL CHECK(stock_available >= 0)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL REFERENCES items(id),
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK(status IN ('pending', 'confirmed', 'cancelled', 'expired')),
            expires_at REAL NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP server that handles each request in a separate thread."""
    allow_reuse_address = True
    daemon_threads = True


def main():
    init_db()
    server = ThreadedHTTPServer(("127.0.0.1", 8080), RequestHandler)
    print("Server running on http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
