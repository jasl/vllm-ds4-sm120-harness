from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Callable


Json = dict[str, Any]
PostJson = Callable[..., Json]


def get_status(base_url: str, path: str, timeout: float) -> Json:
    url = base_url.rstrip("/") + path
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"status_code": response.status, "body": body}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {"status_code": exc.code, "body": body}


def post_json(
    base_url: str,
    path: str,
    payload: Json,
    timeout: float,
    *,
    headers: dict[str, str] | None = None,
) -> Json:
    url = base_url.rstrip("/") + path
    encoded = json.dumps(payload).encode("utf-8")
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(
        url,
        data=encoded,
        headers=request_headers,
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


def post_json_with_retries(
    base_url: str,
    path: str,
    payload: Json,
    timeout: float,
    *,
    headers: dict[str, str] | None = None,
    request_retries: int = 0,
    post_func: PostJson = post_json,
) -> Json:
    retries = max(0, request_retries)
    attempts = retries + 1
    last_exc: Exception | None = None
    for _attempt in range(attempts):
        try:
            if headers is not None:
                return post_func(base_url, path, payload, timeout, headers=headers)
            return post_func(base_url, path, payload, timeout)
        except Exception as exc:
            last_exc = exc
    if last_exc is not None:
        if attempts > 1:
            raise RuntimeError(
                f"request failed after {attempts} attempts: {last_exc!r}"
            ) from last_exc
        raise last_exc
    raise RuntimeError("post_json_with_retries exhausted without an attempt")


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
