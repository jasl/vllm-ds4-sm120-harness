from __future__ import annotations

import json
import re
import subprocess
import textwrap
from pathlib import Path
from typing import Any


Json = dict[str, Any]

DEFAULT_CASE_NAME = "very_long_context_capacity"
DEFAULT_TARGETS = (524288, 786432, 1048576)
DEFAULT_MAX_TOKENS = 16
DEFAULT_SALT_RESERVATION_TOKENS = 48
GIB = 1024**3


_MODEL_LOAD_RE = re.compile(r"Model loading took\s*([0-9][0-9.,]*)\s*GiB", re.I)
_AVAILABLE_KV_RE = re.compile(
    r"Available KV cache memory:\s*([0-9][0-9.,]*)\s*GiB", re.I
)
_GPU_KV_RE = re.compile(r"GPU KV cache size:\s*([0-9][0-9,]*)\s*tokens", re.I)
_MAX_CONCURRENCY_RE = re.compile(
    r"Maximum concurrency for\s*([0-9][0-9,]*)\s*tokens per request:\s*"
    r"([0-9][0-9.,]*)x",
    re.I,
)
_GRAPH_MEMORY_PATTERNS = (
    re.compile(
        r"Graph capturing finished.*?(?:took|memory)\s*([0-9][0-9.,]*)\s*GiB",
        re.I,
    ),
    re.compile(r"CUDA graph pool memory:\s*([0-9][0-9.,]*)\s*GiB", re.I),
)
_ERROR_PATTERNS = {
    "cuda_error_count": re.compile(
        r"(CUDA.*(error|unspecified launch failure|illegal memory access)|"
        r"CUDA.*out of memory|Triton Error \[CUDA\]|"
        r"unspecified launch failure|illegal memory access)",
        re.I,
    ),
    "nccl_error_count": re.compile(
        r"(NCCL.*(error|failed|failure|timeout|unhandled|warn)|"
        r"No available shared memory broadcast block)",
        re.I,
    ),
    "driver_error_count": re.compile(
        r"\b(NVRM|Xid|UVM|GPU has fallen off the bus|lost from the bus)\b",
        re.I,
    ),
    "engine_error_count": re.compile(
        r"((EngineCore|EngineCoreProc|engine core).*(error|exception|failed|died|dead)|"
        r"Traceback|RuntimeError)",
        re.I,
    ),
    "worker_crash_count": re.compile(
        r"(WorkerProc hit an exception|Process ApiServer_\d+ .*died)", re.I
    ),
}


TARGET_MATERIALIZER_SCRIPT = textwrap.dedent(
    r"""
    import hashlib
    import json
    import math
    import sys
    from pathlib import Path


    def _load_tokenizer(model, tokenizer_mode):
        if tokenizer_mode == "deepseek_v4":
            try:
                from vllm.tokenizers.deepseek_v4 import DeepseekV4Tokenizer

                return DeepseekV4Tokenizer.from_pretrained(
                    model,
                    trust_remote_code=True,
                )
            except Exception:
                pass
        try:
            from vllm.transformers_utils.tokenizer import get_tokenizer

            try:
                return get_tokenizer(
                    model,
                    tokenizer_mode=tokenizer_mode,
                    trust_remote_code=True,
                )
            except TypeError:
                return get_tokenizer(model, trust_remote_code=True)
        except Exception:
            from transformers import AutoTokenizer

            return AutoTokenizer.from_pretrained(model, trust_remote_code=True)


    def _encode(tokenizer, text):
        encoded = tokenizer(text, add_special_tokens=False)
        if isinstance(encoded, dict):
            return list(encoded["input_ids"])
        if hasattr(encoded, "input_ids"):
            return list(encoded.input_ids)
        return list(encoded)


    def _sha256(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


    def _build_prompt(tokenizer, target_prompt_tokens, label):
        header = (
            "Very long context frontier probe.\n"
            f"Target prompt tokens: {target_prompt_tokens}.\n"
            f"Context label: {label}.\n\n"
        )
        unit = (
            "This deterministic filler sentence exists only to occupy context "
            "tokens while keeping the semantic payload neutral and repeatable.\n"
        )
        unit_tokens = max(1, len(_encode(tokenizer, unit)))
        repeat = max(1, math.ceil(target_prompt_tokens / unit_tokens))
        text = header + unit * repeat
        actual = len(_encode(tokenizer, text))

        for _ in range(8):
            if actual <= target_prompt_tokens and target_prompt_tokens - actual <= unit_tokens:
                break
            if actual > target_prompt_tokens:
                repeat = max(1, int(repeat * target_prompt_tokens / actual) - 1)
            else:
                repeat += max(1, int((target_prompt_tokens - actual) / unit_tokens))
            text = header + unit * repeat
            actual = len(_encode(tokenizer, text))

        if actual > target_prompt_tokens:
            # Final safety trim by characters. This is intentionally conservative:
            # the server's chat template still has reserved headroom.
            ratio = max(0.1, target_prompt_tokens / actual)
            text = text[: max(len(header), int(len(text) * ratio))]
            actual = len(_encode(tokenizer, text))
        return text, actual


    def _main():
        request = json.load(sys.stdin)
        output_dir = Path(request["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        tokenizer = _load_tokenizer(request["model"], request["tokenizer_mode"])
        max_tokens = int(request["max_tokens"])
        salt = int(request["salt_reservation_tokens"])
        prompts = []
        for target in [int(value) for value in request["targets"]]:
            target_prompt_tokens = max(1, target - max_tokens - salt - 512)
            text, actual = _build_prompt(
                tokenizer,
                target_prompt_tokens,
                f"frontier_{target}",
            )
            filename = f"frontier_{target}.txt"
            path = output_dir / filename
            path.write_text(text, encoding="utf-8")
            prompts.append(
                {
                    "target_context_tokens": target,
                    "target_prompt_tokens": target_prompt_tokens,
                    "actual_prompt_tokens": actual,
                    "filename": filename,
                    "sha256": _sha256(text),
                    "bytes": len(text.encode("utf-8")),
                }
            )
        return {
            "ok": True,
            "model": request["model"],
            "tokenizer_mode": request["tokenizer_mode"],
            "max_tokens": max_tokens,
            "salt_reservation_tokens": salt,
            "targets": [int(value) for value in request["targets"]],
            "prompts": prompts,
        }


    try:
        result = _main()
    except Exception as exc:
        result = {"ok": False, "error": repr(exc), "prompts": []}

    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("ok") else 1)
    """
).strip()


def parse_targets(value: str | list[int] | tuple[int, ...]) -> list[int]:
    if isinstance(value, str):
        raw_items = [item.strip() for item in value.split(",") if item.strip()]
    else:
        raw_items = [str(item) for item in value]
    if not raw_items:
        raise ValueError("at least one target context length is required")
    targets: list[int] = []
    for item in raw_items:
        try:
            target = int(item)
        except ValueError as exc:
            raise ValueError(f"targets must be positive integers: {item!r}") from exc
        if target < 1:
            raise ValueError("targets must be positive integers")
        if target in targets:
            raise ValueError(f"duplicate target: {target}")
        targets.append(target)
    return targets


def _number(value: str) -> float:
    return float(value.replace(",", ""))


def _int_number(value: str) -> int:
    return int(value.replace(",", ""))


def _float_matches(pattern: re.Pattern[str], text: str) -> list[float]:
    return [_number(match.group(1)) for match in pattern.finditer(text)]


def _int_matches(pattern: re.Pattern[str], text: str) -> list[int]:
    return [_int_number(match.group(1)) for match in pattern.finditer(text)]


def _runtime_health(text: str) -> Json:
    counts = {key: 0 for key in _ERROR_PATTERNS}
    signal_count = 0
    for line in text.splitlines():
        matched = False
        for key, pattern in _ERROR_PATTERNS.items():
            if pattern.search(line):
                counts[key] += 1
                matched = True
        if matched:
            signal_count += 1
    return {"error_signal_count": signal_count, **counts}


def parse_capacity_log(
    text: str,
    *,
    targets: list[int] | tuple[int, ...] = DEFAULT_TARGETS,
    case_name: str = DEFAULT_CASE_NAME,
    variant: str = "manual",
) -> Json:
    targets = parse_targets(list(targets))
    model_load_samples = _float_matches(_MODEL_LOAD_RE, text)
    available_samples = _float_matches(_AVAILABLE_KV_RE, text)
    kv_token_samples = _int_matches(_GPU_KV_RE, text)
    concurrency_matches = [
        (_int_number(match.group(1)), _number(match.group(2)))
        for match in _MAX_CONCURRENCY_RE.finditer(text)
    ]
    graph_samples: list[float] = []
    for pattern in _GRAPH_MEMORY_PATTERNS:
        graph_samples.extend(_float_matches(pattern, text))

    capacity: Json = {
        "model_loading_gib": max(model_load_samples) if model_load_samples else None,
        "available_kv_cache_gib": min(available_samples) if available_samples else None,
        "gpu_kv_cache_size_tokens": min(kv_token_samples) if kv_token_samples else None,
        "cuda_graph_memory_gib": max(graph_samples) if graph_samples else None,
        "samples": {
            "model_loading_gib": model_load_samples,
            "available_kv_cache_gib": available_samples,
            "gpu_kv_cache_size_tokens": kv_token_samples,
            "cuda_graph_memory_gib": graph_samples,
        },
    }
    if concurrency_matches:
        context_tokens, concurrency = min(concurrency_matches, key=lambda item: item[1])
        capacity["maximum_concurrency_context_tokens"] = context_tokens
        capacity["maximum_concurrency"] = concurrency
        capacity["samples"]["maximum_concurrency"] = [
            {
                "context_tokens": context_tokens,
                "concurrency": concurrency,
            }
            for context_tokens, concurrency in concurrency_matches
        ]
    else:
        capacity["maximum_concurrency_context_tokens"] = None
        capacity["maximum_concurrency"] = None

    available_gib = capacity["available_kv_cache_gib"]
    kv_tokens = capacity["gpu_kv_cache_size_tokens"]
    bytes_per_token = None
    if isinstance(available_gib, int | float) and isinstance(kv_tokens, int) and kv_tokens > 0:
        bytes_per_token = available_gib * GIB / kv_tokens
        capacity["bytes_per_token"] = round(bytes_per_token, 6)
    else:
        capacity["bytes_per_token"] = None

    estimates: list[Json] = []
    for target in targets:
        estimated_concurrency = None
        request_kv_gib = None
        margin_tokens = None
        margin_gib = None
        if isinstance(kv_tokens, int) and kv_tokens > 0:
            estimated_concurrency = kv_tokens / target
            margin_tokens = kv_tokens - target
        if isinstance(bytes_per_token, int | float):
            request_kv_gib = target * bytes_per_token / GIB
            if margin_tokens is not None:
                margin_gib = margin_tokens * bytes_per_token / GIB
        estimates.append(
            {
                "target_context_tokens": target,
                "request_kv_gib": None
                if request_kv_gib is None
                else round(request_kv_gib, 6),
                "capacity_margin_tokens": margin_tokens,
                "capacity_margin_gib": None if margin_gib is None else round(margin_gib, 6),
                "estimated_concurrency": None
                if estimated_concurrency is None
                else round(estimated_concurrency, 6),
                "c1_ok": bool(kv_tokens is not None and kv_tokens >= target),
                "c2_ok": bool(kv_tokens is not None and kv_tokens >= target * 2),
            }
        )

    required = (
        "available_kv_cache_gib",
        "gpu_kv_cache_size_tokens",
        "bytes_per_token",
    )
    missing_fields = [key for key in required if capacity.get(key) is None]
    health = _runtime_health(text)
    ok = (
        not missing_fields
        and all(item["c1_ok"] for item in estimates)
        and health["error_signal_count"] == 0
    )
    return {
        "schema_version": 1,
        "case": case_name,
        "variant": variant,
        "ok": ok,
        "targets": targets,
        "capacity": capacity,
        "estimates": estimates,
        "missing_fields": missing_fields,
        "runtime_health": health,
    }


def build_capacity_from_serve_log(
    *,
    serve_log: Path,
    targets: list[int] | tuple[int, ...] = DEFAULT_TARGETS,
    case_name: str = DEFAULT_CASE_NAME,
    variant: str = "manual",
) -> Json:
    return parse_capacity_log(
        serve_log.read_text(encoding="utf-8", errors="replace"),
        targets=targets,
        case_name=case_name,
        variant=variant,
    )


def materialize_token_frontier_prompts(
    *,
    target_python: str,
    model: str,
    tokenizer_mode: str,
    output_dir: Path,
    targets: list[int] | tuple[int, ...] = DEFAULT_TARGETS,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    salt_reservation_tokens: int = DEFAULT_SALT_RESERVATION_TOKENS,
    timeout: float = 1800.0,
) -> Json:
    targets = parse_targets(list(targets))
    request = {
        "model": model,
        "tokenizer_mode": tokenizer_mode,
        "output_dir": str(output_dir),
        "targets": targets,
        "max_tokens": max_tokens,
        "salt_reservation_tokens": salt_reservation_tokens,
    }
    completed = subprocess.run(
        [target_python, "-c", TARGET_MATERIALIZER_SCRIPT],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    try:
        row = json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        row = {
            "ok": False,
            "error": "target materializer did not emit JSON",
            "stdout": completed.stdout[-4096:],
            "stderr": completed.stderr[-4096:],
            "prompts": [],
        }
    row.setdefault("targets", targets)
    row.setdefault("model", model)
    row.setdefault("tokenizer_mode", tokenizer_mode)
    row["target_python"] = Path(target_python).name
    row["exit_code"] = completed.returncode
    if completed.returncode != 0:
        row["ok"] = False
        row.setdefault("stderr", completed.stderr[-4096:])
    for prompt in row.get("prompts", []):
        filename = prompt.get("filename")
        if filename:
            prompt["path"] = str(output_dir / str(filename))
    return row


def write_json(path: Path, row: Json) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:.{digits}f}"


def write_capacity_markdown(path: Path, row: Json) -> None:
    capacity = row.get("capacity", {})
    health = row.get("runtime_health", {})
    lines = [
        "# Very Long Context Capacity",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Case: `{row.get('case')}`",
        f"- Variant: `{row.get('variant')}`",
        f"- Available KV GiB: `{_fmt(capacity.get('available_kv_cache_gib'))}`",
        f"- GPU KV cache tokens: `{_fmt(capacity.get('gpu_kv_cache_size_tokens'), 0)}`",
        f"- Bytes/token: `{_fmt(capacity.get('bytes_per_token'))}`",
        f"- CUDA graph GiB: `{_fmt(capacity.get('cuda_graph_memory_gib'))}`",
        f"- Runtime error signals: `{health.get('error_signal_count', 0)}`",
        "",
        "| Target context tokens | C1 OK | C2 OK | Estimated C | Request KV GiB | Margin tokens | Margin GiB |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for item in row.get("estimates", []):
        lines.append(
            "| {target} | {c1} | {c2} | {conc} | {kv} | {margin_tokens} | {margin_gib} |".format(
                target=item.get("target_context_tokens"),
                c1="yes" if item.get("c1_ok") else "no",
                c2="yes" if item.get("c2_ok") else "no",
                conc=_fmt(item.get("estimated_concurrency")),
                kv=_fmt(item.get("request_kv_gib")),
                margin_tokens=_fmt(item.get("capacity_margin_tokens"), 0),
                margin_gib=_fmt(item.get("capacity_margin_gib")),
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_prompt_manifest_markdown(path: Path, row: Json) -> None:
    lines = [
        "# Token Frontier Prompts",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Model: `{row.get('model')}`",
        f"- Tokenizer mode: `{row.get('tokenizer_mode')}`",
        "",
        "| Target context tokens | Target prompt tokens | Actual prompt tokens | Bytes | File |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for prompt in row.get("prompts", []):
        lines.append(
            "| {target} | {target_prompt} | {actual} | {bytes_} | `{file}` |".format(
                target=prompt.get("target_context_tokens"),
                target_prompt=prompt.get("target_prompt_tokens"),
                actual=prompt.get("actual_prompt_tokens"),
                bytes_=prompt.get("bytes"),
                file=prompt.get("filename"),
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_frontier_summary(
    *,
    capacity: Json | None,
    prompt_manifest: Json | None,
    latency_matrix: Json | None,
    runtime_stats: Json | None,
    gpu_stats: Json | None,
) -> Json:
    requests = []
    if isinstance(latency_matrix, dict):
        for row in latency_matrix.get("requests", []):
            if isinstance(row, dict) and row.get("phase") == "measure":
                requests.append(row)
    return {
        "schema_version": 1,
        "ok": bool(
            (capacity or {}).get("ok", True)
            and (prompt_manifest or {}).get("ok", True)
            and (latency_matrix or {}).get("ok", True)
        ),
        "capacity": capacity,
        "prompt_manifest": prompt_manifest,
        "latency_summary": (latency_matrix or {}).get("summary", []),
        "request_count": len(requests),
        "failure_count": sum(0 if row.get("ok") else 1 for row in requests),
        "runtime_stats": runtime_stats,
        "gpu_stats": gpu_stats,
    }


def write_frontier_summary_markdown(path: Path, row: Json) -> None:
    lines = [
        "# Very Long Context Frontier Summary",
        "",
        f"- OK: `{row.get('ok')}`",
        f"- Requests: `{row.get('request_count')}`",
        f"- Failures: `{row.get('failure_count')}`",
        "",
        "| Prompt | Cache | Prompt tok | TTFT s | Input tok/s | Decode tok/s | ITL p99 s |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in row.get("latency_summary", []):
        prompt_tokens = item.get("prompt_tokens_mean")
        ttft = item.get("ttft_seconds_mean")
        input_tps = None
        if isinstance(prompt_tokens, int | float) and isinstance(ttft, int | float) and ttft > 0:
            input_tps = prompt_tokens / ttft
        lines.append(
            "| `{prompt}` | `{cache}` | {prompt_tokens} | {ttft} | {input_tps} | {decode_tps} | {itl} |".format(
                prompt=item.get("prompt"),
                cache=item.get("cache_mode"),
                prompt_tokens=_fmt(prompt_tokens, 0),
                ttft=_fmt(ttft),
                input_tps=_fmt(input_tps),
                decode_tps=_fmt(item.get("decode_tokens_per_second_mean")),
                itl=_fmt(item.get("p99_inter_chunk_seconds")),
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
