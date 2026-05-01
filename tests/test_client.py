import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from ds4_harness.client import get_status


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def test_get_status_accepts_empty_health_response():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        status = get_status(f"http://127.0.0.1:{server.server_port}", "/health", 5)
    finally:
        server.shutdown()
        thread.join()
        server.server_close()

    assert status == {"status_code": 200, "body": ""}
