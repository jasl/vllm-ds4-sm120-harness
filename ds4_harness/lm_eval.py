from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


def completions_url(base_url: str) -> str:
    stripped = base_url.rstrip("/")
    if stripped.endswith("/v1/completions"):
        return stripped
    if stripped.endswith("/v1"):
        return f"{stripped}/completions"
    return f"{stripped}/v1/completions"


def build_lm_eval_command(
    *,
    lm_eval_bin: str,
    model: str,
    base_url: str,
    tasks: list[str],
    num_fewshot: int,
    num_concurrent: int,
    max_retries: int,
    max_gen_toks: int,
    eval_timeout_ms: int,
    tokenizer_backend: str,
    batch_size: str,
    output_path: Path,
    extra_args: list[str] | None = None,
) -> list[str]:
    model_args = ",".join(
        [
            f"model={model}",
            f"base_url={completions_url(base_url)}",
            f"num_concurrent={num_concurrent}",
            f"max_retries={max_retries}",
            "tokenized_requests=False",
            f"tokenizer_backend={tokenizer_backend}",
            f"max_gen_toks={max_gen_toks}",
            f"timeout={eval_timeout_ms}",
        ]
    )
    command = [
        lm_eval_bin,
        "--model",
        "local-completions",
        "--model_args",
        model_args,
        "--tasks",
        ",".join(tasks),
        "--num_fewshot",
        str(num_fewshot),
        "--batch_size",
        batch_size,
        "--output_path",
        str(output_path),
    ]
    command.extend(extra_args or [])
    return command


def run_lm_eval_command(
    command: list[str],
    timeout: float | None = None,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout_parts = []
        stderr_parts = []
        if exc.stdout:
            stdout_parts.append(
                exc.stdout.decode("utf-8", errors="replace")
                if isinstance(exc.stdout, bytes)
                else exc.stdout
            )
        if exc.stderr:
            stderr_parts.append(
                exc.stderr.decode("utf-8", errors="replace")
                if isinstance(exc.stderr, bytes)
                else exc.stderr
            )
        stdout_parts.append(f"\nTIMEOUT after {timeout} seconds\n")
        stdout = "".join(stdout_parts)
        stderr = "".join(stderr_parts)
        returncode = -1
    except OSError as exc:
        stdout = f"{type(exc).__name__}: {exc}\n"
        stderr = ""
        returncode = -2
    return {
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "command": command,
    }


def load_lm_eval_results(output_path: Path) -> dict[str, Any] | None:
    candidates = sorted(output_path.rglob("*.json")) if output_path.exists() else []
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("results"), dict):
            return data
    return None


def _metric(data: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in data:
            return data[name]
    return None


def summarize_lm_eval_results(
    raw_results: dict[str, Any] | None,
    *,
    command_result: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    tasks = []
    versions = raw_results.get("versions", {}) if isinstance(raw_results, dict) else {}
    results = raw_results.get("results", {}) if isinstance(raw_results, dict) else {}
    if isinstance(results, dict):
        for task_name, data in results.items():
            if not isinstance(data, dict):
                continue
            tasks.append(
                {
                    "task": task_name,
                    "version": versions.get(task_name)
                    if isinstance(versions, dict)
                    else None,
                    "alias": data.get("alias"),
                    "exact_match_flexible": _metric(
                        data,
                        "exact_match,flexible-extract",
                        "exact_match,flexible",
                    ),
                    "exact_match_strict": _metric(
                        data,
                        "exact_match,strict-match",
                        "exact_match,strict",
                    ),
                    "exact_match_flexible_stderr": _metric(
                        data,
                        "exact_match_stderr,flexible-extract",
                        "exact_match_stderr,flexible",
                    ),
                    "exact_match_strict_stderr": _metric(
                        data,
                        "exact_match_stderr,strict-match",
                        "exact_match_stderr,strict",
                    ),
                    "acc": _metric(data, "acc,none", "acc"),
                    "acc_stderr": _metric(data, "acc_stderr,none", "acc_stderr"),
                }
            )

    returncode = command_result.get("returncode")
    return {
        "ok": returncode == 0 and bool(tasks),
        "returncode": returncode,
        "command": command_result.get("command", []),
        "config": config,
        "tasks": tasks,
        "raw_results_found": raw_results is not None,
    }
