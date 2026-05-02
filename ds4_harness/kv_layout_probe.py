from __future__ import annotations

import hashlib
import json
import subprocess
import textwrap
from pathlib import Path
from typing import Any


Json = dict[str, Any]

DEFAULT_CASE_NAME = "packed_fp8_indexer_cache_layout"
DEFAULT_NUM_BLOCKS = 2
DEFAULT_BLOCK_SIZE = 256
DEFAULT_HEAD_DIM = 448
DEFAULT_SCALE_BYTES = 8


TARGET_PROBE_SCRIPT = textwrap.dedent(
    r"""
    import hashlib
    import json
    import sys


    def _tensor_bytes(tensor):
        return bytes(int(item) for item in tensor.reshape(-1).tolist())


    def _sha256(tensor):
        return hashlib.sha256(_tensor_bytes(tensor)).hexdigest()


    def _byte_head(tensor, count=16):
        return [int(item) for item in tensor.reshape(-1)[:count].tolist()]


    def _diff_count(left, right):
        return int((left != right).sum().item())


    def _build_cache(torch, num_blocks, block_size, head_dim, scale_bytes):
        value_end = block_size * head_dim
        scale_end = value_end + block_size * scale_bytes
        cache = torch.empty(
            (num_blocks, block_size, head_dim + scale_bytes),
            dtype=torch.uint8,
        )
        flat = cache.reshape(num_blocks, -1)
        for block in range(num_blocks):
            values = (
                (torch.arange(value_end, dtype=torch.int64) + block * 17) % 251
            ).to(torch.uint8)
            scales = (
                (torch.arange(block_size * scale_bytes, dtype=torch.int64) * 3)
                + block * 29
                + 7
            ) % 251
            flat[block, :value_end] = values
            flat[block, value_end:scale_end] = scales.to(torch.uint8)
        return cache


    def _sentinels(flat, num_blocks, block_size, head_dim, scale_bytes):
        value_end = block_size * head_dim
        blocks = sorted({0, num_blocks - 1})
        tokens = sorted({0, 1, block_size // 2, block_size - 1})
        rows = []
        for block in blocks:
            for token in tokens:
                value_offset = token * head_dim
                scale_offset = value_end + token * scale_bytes
                values = flat[block, value_offset:value_offset + head_dim]
                scales = flat[block, scale_offset:scale_offset + scale_bytes]
                rows.append(
                    {
                        "block": block,
                        "token": token,
                        "packed_value_offset": value_offset,
                        "packed_scale_offset": scale_offset,
                        "value_sha256": _sha256(values),
                        "scale_sha256": _sha256(scales),
                        "value_head_bytes": _byte_head(values),
                        "scale_bytes": _byte_head(scales, scale_bytes),
                    }
                )
        return rows


    def _main():
        request = json.load(sys.stdin)
        params = request["parameters"]
        num_blocks = int(params["num_blocks"])
        block_size = int(params["block_size"])
        head_dim = int(params["head_dim"])
        scale_bytes = int(params["scale_bytes"])
        require_helper_match = bool(request.get("require_helper_match", True))

        import torch

        cache = _build_cache(torch, num_blocks, block_size, head_dim, scale_bytes)
        flat = cache.reshape(num_blocks, -1)
        value_end = block_size * head_dim
        scale_end = value_end + block_size * scale_bytes
        expected_values = flat[:, :value_end].reshape(num_blocks, block_size, head_dim)
        expected_scales = flat[:, value_end:scale_end].reshape(
            num_blocks, block_size, scale_bytes
        )

        legacy_values = cache[:, :, :head_dim]
        legacy_scales = cache[:, :, head_dim:head_dim + scale_bytes]
        legacy_value_diff = _diff_count(legacy_values, expected_values)
        legacy_scale_diff = _diff_count(legacy_scales, expected_scales)
        legacy_diff = legacy_value_diff + legacy_scale_diff

        helper = {
            "available": False,
            "matches_expected": None,
            "value_diff_count": None,
            "scale_diff_count": None,
            "error": None,
        }
        helper_views = {}
        try:
            from vllm.model_executor.layers.deepseek_v4_triton_kernels import (
                _view_packed_fp8_paged_mqa_kv_cache,
            )

            helper_values, helper_scales = _view_packed_fp8_paged_mqa_kv_cache(
                cache,
                head_dim,
            )
            helper_value_bytes = helper_values.contiguous().view(torch.uint8).reshape(
                num_blocks,
                block_size,
                head_dim,
            )
            helper_scale_bytes = helper_scales.contiguous().view(torch.uint8).reshape(
                num_blocks,
                block_size,
                scale_bytes,
            )
            value_diff = _diff_count(helper_value_bytes, expected_values)
            scale_diff = _diff_count(helper_scale_bytes, expected_scales)
            helper.update(
                {
                    "available": True,
                    "matches_expected": value_diff == 0 and scale_diff == 0,
                    "value_diff_count": value_diff,
                    "scale_diff_count": scale_diff,
                }
            )
            helper_views = {
                "values_shape": list(helper_values.shape),
                "values_stride": list(helper_values.stride()),
                "values_storage_offset": int(helper_values.storage_offset()),
                "scales_shape": list(helper_scales.shape),
                "scales_stride": list(helper_scales.stride()),
                "scales_storage_offset": int(helper_scales.storage_offset()),
            }
        except Exception as exc:
            helper["error"] = repr(exc)

        helper_ok = (
            bool(helper["matches_expected"])
            if helper["available"]
            else not require_helper_match
        )
        ok = legacy_diff > 0 and helper_ok
        if helper["available"] and helper["matches_expected"]:
            detail = "packed helper matched expected byte layout"
        elif helper["available"]:
            detail = "packed helper did not match expected byte layout"
        elif require_helper_match:
            detail = "packed helper was unavailable"
        else:
            detail = "packed byte layout snapshot exported without helper check"

        raw_bytes = _tensor_bytes(cache)
        row = {
            "schema_version": 1,
            "case": request.get("case_name") or "packed_fp8_indexer_cache_layout",
            "variant": request.get("variant") or "manual",
            "ok": ok,
            "detail": detail,
            "parameters": {
                "num_blocks": num_blocks,
                "block_size": block_size,
                "head_dim": head_dim,
                "scale_bytes": scale_bytes,
            },
            "target": {
                "python_executable": sys.executable,
                "torch_version": getattr(torch, "__version__", None),
                "cuda_available": bool(torch.cuda.is_available()),
            },
            "cache": {
                "dtype": str(cache.dtype),
                "shape": list(cache.shape),
                "stride": list(cache.stride()),
                "storage_offset": int(cache.storage_offset()),
            },
            "packed_offsets": {
                "block_stride_bytes": int(cache.stride(0)),
                "value_bytes_per_block": value_end,
                "scale_bytes_per_block": block_size * scale_bytes,
                "values_offset": 0,
                "scales_offset": value_end,
                "scale_end": scale_end,
            },
            "helper": helper,
            "helper_views": helper_views,
            "interleaved_legacy_view": {
                "value_diff_count": legacy_value_diff,
                "scale_diff_count": legacy_scale_diff,
                "diff_count": legacy_diff,
            },
            "sentinels": _sentinels(flat, num_blocks, block_size, head_dim, scale_bytes),
            "raw_cache": {
                "bytes": len(raw_bytes),
                "sha256": hashlib.sha256(raw_bytes).hexdigest(),
            },
        }
        if request.get("emit_raw_cache_hex"):
            row["raw_cache_hex"] = raw_bytes.hex()
        return row


    try:
        result = _main()
    except Exception as exc:
        result = {
            "schema_version": 1,
            "case": "packed_fp8_indexer_cache_layout",
            "variant": "manual",
            "ok": False,
            "detail": f"probe failed: {exc!r}",
            "error": repr(exc),
        }

    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("ok") else 1)
    """
).strip()


def _target_python_name(value: object) -> str | None:
    if not value:
        return None
    return Path(str(value)).name


def _sanitize_target(row: Json, target_python: str) -> None:
    target = row.setdefault("target", {})
    if isinstance(target, dict):
        target["python_executable"] = _target_python_name(
            target.get("python_executable") or target_python
        )


def _last_json_line(stdout: str) -> Json:
    for line in reversed(stdout.splitlines()):
        stripped = line.strip()
        if not stripped or not stripped.startswith("{"):
            continue
        return json.loads(stripped)
    raise ValueError("target python did not emit a JSON object")


def _validate_shape(
    *,
    num_blocks: int,
    block_size: int,
    head_dim: int,
    scale_bytes: int,
) -> None:
    if num_blocks < 1:
        raise ValueError("num_blocks must be >= 1")
    if block_size < 2:
        raise ValueError("block_size must be >= 2")
    if head_dim < 1:
        raise ValueError("head_dim must be >= 1")
    if scale_bytes < 4 or scale_bytes % 4 != 0:
        raise ValueError("scale_bytes must be a positive multiple of 4")


def _failure_row(
    *,
    target_python: str,
    variant: str,
    case_name: str,
    detail: str,
    returncode: int | None = None,
    stderr: str | None = None,
    stdout: str | None = None,
) -> Json:
    row: Json = {
        "schema_version": 1,
        "case": case_name,
        "variant": variant,
        "ok": False,
        "detail": detail,
        "target": {"python_executable": _target_python_name(target_python)},
    }
    if returncode is not None:
        row["returncode"] = returncode
    if stderr:
        row["stderr_tail"] = "\n".join(stderr.splitlines()[-20:])
    if stdout:
        row["stdout_tail"] = "\n".join(stdout.splitlines()[-20:])
    return row


def run_kv_layout_probe(
    *,
    target_python: str,
    variant: str,
    case_name: str = DEFAULT_CASE_NAME,
    num_blocks: int = DEFAULT_NUM_BLOCKS,
    block_size: int = DEFAULT_BLOCK_SIZE,
    head_dim: int = DEFAULT_HEAD_DIM,
    scale_bytes: int = DEFAULT_SCALE_BYTES,
    raw_output: Path | None = None,
    require_helper_match: bool = True,
    timeout: float = 120.0,
) -> Json:
    _validate_shape(
        num_blocks=num_blocks,
        block_size=block_size,
        head_dim=head_dim,
        scale_bytes=scale_bytes,
    )
    request = {
        "case_name": case_name,
        "variant": variant,
        "parameters": {
            "num_blocks": num_blocks,
            "block_size": block_size,
            "head_dim": head_dim,
            "scale_bytes": scale_bytes,
        },
        "emit_raw_cache_hex": raw_output is not None,
        "require_helper_match": require_helper_match,
    }
    try:
        completed = subprocess.run(
            [target_python, "-c", TARGET_PROBE_SCRIPT],
            input=json.dumps(request, ensure_ascii=False),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout,
        )
    except OSError as exc:
        return _failure_row(
            target_python=target_python,
            variant=variant,
            case_name=case_name,
            detail=f"failed to execute target python: {exc!r}",
        )
    except subprocess.TimeoutExpired as exc:
        return _failure_row(
            target_python=target_python,
            variant=variant,
            case_name=case_name,
            detail=f"target python timed out after {timeout:g}s",
            stdout=exc.stdout if isinstance(exc.stdout, str) else None,
            stderr=exc.stderr if isinstance(exc.stderr, str) else None,
        )

    try:
        row = _last_json_line(completed.stdout)
    except (json.JSONDecodeError, ValueError) as exc:
        return _failure_row(
            target_python=target_python,
            variant=variant,
            case_name=case_name,
            detail=f"failed to parse target JSON: {exc}",
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    _sanitize_target(row, target_python)
    raw_hex = row.pop("raw_cache_hex", None)
    if raw_output is not None and isinstance(raw_hex, str):
        raw_bytes = bytes.fromhex(raw_hex)
        raw_output.parent.mkdir(parents=True, exist_ok=True)
        raw_output.write_bytes(raw_bytes)
        sha256 = hashlib.sha256(raw_bytes).hexdigest()
        sha_path = raw_output.with_suffix(raw_output.suffix + ".sha256")
        sha_path.write_text(f"{sha256}  {raw_output.name}\n", encoding="utf-8")
        raw_cache = row.setdefault("raw_cache", {})
        if isinstance(raw_cache, dict):
            raw_cache["filename"] = raw_output.name
            raw_cache["sha256_file"] = sha_path.name
            raw_cache["bytes"] = len(raw_bytes)
            raw_cache["sha256"] = sha256

    if completed.returncode != 0 and row.get("ok"):
        row["ok"] = False
        row["detail"] = f"target python exited {completed.returncode}"
    return row


def write_kv_layout_markdown(path: Path, row: Json) -> None:
    params = row.get("parameters") if isinstance(row.get("parameters"), dict) else {}
    raw_cache = row.get("raw_cache") if isinstance(row.get("raw_cache"), dict) else {}
    helper = row.get("helper") if isinstance(row.get("helper"), dict) else {}
    legacy = (
        row.get("interleaved_legacy_view")
        if isinstance(row.get("interleaved_legacy_view"), dict)
        else {}
    )
    lines = [
        "# KV Layout Probe",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Detail: {row.get('detail')}",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Blocks: `{params.get('num_blocks')}`",
        f"- Block size: `{params.get('block_size')}`",
        f"- Head dim: `{params.get('head_dim')}`",
        f"- Scale bytes: `{params.get('scale_bytes')}`",
        f"- Helper available: `{helper.get('available')}`",
        f"- Helper matches expected: `{helper.get('matches_expected')}`",
        f"- Legacy interleaved diff count: `{legacy.get('diff_count')}`",
        f"- Raw cache: `{raw_cache.get('filename', 'not written')}`",
        f"- Raw cache SHA256: `{raw_cache.get('sha256', 'n/a')}`",
        "",
        "This is a synthetic packed-cache byte-layout snapshot. It does not "
        "require a B200 correctness reference.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
