from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


Json = dict[str, Any]


def get_status(base_url: str, path: str, timeout: float) -> Json:
    url = base_url.rstrip("/") + path
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"status_code": response.status, "body": body}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {"status_code": exc.code, "body": body}


def post_json(base_url: str, path: str, payload: Json, timeout: float) -> Json:
    url = base_url.rstrip("/") + path
    encoded = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{url} returned HTTP {exc.code}: {body}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{url} did not return a JSON object")
    return data


def get_json(base_url: str, path: str, timeout: float) -> Json:
    url = base_url.rstrip("/") + path
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{url} returned HTTP {exc.code}: {body}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{url} did not return a JSON object")
    return data
