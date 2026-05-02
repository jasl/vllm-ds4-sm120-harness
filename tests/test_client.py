import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from ds4_harness.client import get_status, post_json_with_retries


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


def test_post_json_with_retries_retries_transient_failures():
    calls = []

    def fake_post_json(base_url, path, payload, timeout):
        calls.append((base_url, path, payload, timeout))
        if len(calls) == 1:
            raise RuntimeError("transient")
        return {"ok": True}

    response = post_json_with_retries(
        "http://127.0.0.1:9",
        "/v1/chat/completions",
        {"model": "m"},
        30,
        request_retries=1,
        post_func=fake_post_json,
    )

    assert response == {"ok": True}
    assert len(calls) == 2


def test_post_json_with_retries_raises_after_retry_budget():
    calls = []

    def fake_post_json(base_url, path, payload, timeout):
        calls.append(path)
        raise RuntimeError("still down")

    with pytest.raises(RuntimeError, match="still down"):
        post_json_with_retries(
            "http://127.0.0.1:9",
            "/v1/chat/completions",
            {"model": "m"},
            30,
            request_retries=1,
            post_func=fake_post_json,
        )

    assert calls == ["/v1/chat/completions", "/v1/chat/completions"]
