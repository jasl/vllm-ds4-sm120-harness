from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


Json = dict[str, Any]

VARIANTS = ("nomtp", "mtp")
SMOKE_CASES = ("quick", "quality", "coding")
BENCH_PHASE_LABELS = {
    "bench_hf_mt_bench": "HF/MT-Bench",
    "bench_random_8192x512": "Random 8192/512",
}

FORBIDDEN_PATTERNS = (
    re.compile(r"DEEPSEEK_API_KEY\s*="),
    re.compile(r"\b[A-Z0-9_]*API_KEY\s*[:=]\s*['\"]?[^'\"\s]+"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+"),
    re.compile(r"root@"),
    re.compile(r"\b10\.0\.0\.\d+\b"),
    re.compile(r"\b146\.88\.195\.11\b"),
    re.compile(r"/Users/"),
    re.compile(r"/workspace/"),
    re.compile(r"/root/"),
    re.compile(r"/home/(?!user\b)[^/\s\"'`,]+"),
)

SANITIZE_REPLACEMENTS = (
    (re.compile(r"/workspace/vllm/\.venv/bin/vllm"), "vllm"),
    (re.compile(r"/workspace/vllm/\.venv/bin/python"), "python"),
    (re.compile(r"/workspace/ds4-sm120-harness"), "<harness-root>"),
    (re.compile(r"/workspace/vllm"), "<vllm-root>"),
    (re.compile(r"/workspace"), "<workspace>"),
    (re.compile(r"/Users/[^/\s\"'`,]+/[^\s\"'`,]*"), "<local-path>"),
    (re.compile(r"/root/[^\s\"'`,]*"), "<root-path>"),
    (re.compile(r"/home/user\b"), "<synthetic-home>"),
    (re.compile(r"/home/[^/\s\"'`,]+/[^\s\"'`,]*"), "<home-path>"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._-]+"), "Bearer <redacted>"),
    (re.compile(r"sk-[A-Za-z0-9_-]{12,}"), "<redacted-key>"),
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [line.rstrip() for line in _sanitize_string(text).splitlines()]
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _sanitize_string(value: str) -> str:
    sanitized = value
    for pattern, replacement in SANITIZE_REPLACEMENTS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def _sanitize_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_json(item) for item in value]
    if isinstance(value, str):
        return _sanitize_string(value)
    return value


def _copy_json(src: Path, dst: Path) -> None:
    if src.exists():
        _write_json(dst, _sanitize_json(_load_json(src)))


def _copy_text(src: Path, dst: Path) -> None:
    if src.exists():
        _write_text(dst, src.read_text(encoding="utf-8", errors="replace"))


def _read_jsonl(path: Path) -> list[Any]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(_sanitize_json(json.loads(line)))
    return rows


def _parse_collect_env(text: str) -> Json:
    summary: Json = {}
    key_map = {
        "vLLM Version": "vllm_version",
        "PyTorch version": "pytorch_version",
        "CUDA runtime version": "cuda_runtime_version",
        "CUDA used to build PyTorch": "pytorch_cuda_build",
        "Nvidia driver version": "nvidia_driver_version",
        "Python version": "python_version",
        "OS": "os",
    }
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[pip3] transformers=="):
            summary["transformers_version"] = stripped.split("==", 1)[1].strip()
            continue
        if stripped.startswith("[pip3] triton=="):
            summary["triton_version"] = stripped.split("==", 1)[1].strip()
            continue
        if ":" not in line:
            continue
        raw_key, raw_value = line.split(":", 1)
        key = raw_key.strip()
        value = raw_value.strip()
        if key in key_map and value:
            summary[key_map[key]] = _sanitize_string(value)
        elif key == "CUDA Archs" and value:
            summary["vllm_cuda_archs"] = value.split(";", 1)[0].strip()

    version = str(summary.get("vllm_version", ""))
    match = re.search(r"git sha:\s*([0-9A-Fa-f]+)", version)
    if match:
        summary["vllm_git_sha"] = match.group(1)
        summary["vllm_version"] = re.sub(
            r"\s*\(git sha:\s*[0-9A-Fa-f]+\)",
            "",
            version,
        )
    return summary


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _first_run_environment(run_dir: Path) -> Json:
    path = _first_existing(
        [
            run_dir / "nomtp" / "bench_hf_mt_bench" / "run_environment.json",
            run_dir / "nomtp" / "acceptance" / "run_environment.json",
            run_dir / "mtp" / "bench_hf_mt_bench" / "run_environment.json",
            run_dir / "mtp" / "acceptance" / "run_environment.json",
        ]
    )
    if path is None:
        return {}
    raw = _load_json(path)
    return _sanitize_json(raw) if isinstance(raw, dict) else {}


def _first_collect_env(run_dir: Path) -> Json:
    path = _first_existing(
        [
            run_dir / "nomtp" / "bench_hf_mt_bench" / "vllm_collect_env.txt",
            run_dir / "nomtp" / "acceptance" / "vllm_collect_env.txt",
            run_dir / "mtp" / "bench_hf_mt_bench" / "vllm_collect_env.txt",
            run_dir / "mtp" / "acceptance" / "vllm_collect_env.txt",
        ]
    )
    if path is None:
        return {}
    return _parse_collect_env(path.read_text(encoding="utf-8", errors="replace"))


def _serve_commands(run_dir: Path) -> Json:
    commands: Json = {}
    for variant in VARIANTS:
        path = run_dir / variant / "serve_command.sh"
        if path.exists():
            commands[variant] = _sanitize_string(
                path.read_text(encoding="utf-8", errors="replace")
            ).strip()
    return commands


def _phase_exit_codes(run_dir: Path) -> list[Json]:
    path = run_dir / "phase_exit_codes.tsv"
    if not path.exists():
        return []
    rows = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if index == 0 or not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        rows.append(
            {
                "variant": parts[0],
                "phase": parts[1],
                "exit_code": int(parts[2]) if parts[2].isdigit() else parts[2],
                "artifact": f"{parts[0]}/{parts[1]}",
            }
        )
    return rows


def _copy_oracle(run_dir: Path, output_dir: Path) -> None:
    source_dir = run_dir / "nomtp" / "oracle_export"
    target_dir = output_dir / "oracle"
    for path in sorted(source_dir.glob("completion_*.json")):
        _copy_json(path, target_dir / path.name)
    for path in sorted(source_dir.glob("tokenize_completion_*.json")):
        _copy_json(path, target_dir / path.name)
    _copy_json(
        source_dir / "oracle_export_summary.json",
        target_dir / "oracle_export_summary.json",
    )
    _copy_text(
        source_dir / "oracle_export_summary.md",
        target_dir / "oracle_export_summary.md",
    )


def _copy_smoke_and_toolcall(run_dir: Path, output_dir: Path) -> None:
    for variant in VARIANTS:
        source_dir = run_dir / variant / "acceptance"
        for smoke_name in SMOKE_CASES:
            jsonl_path = source_dir / f"smoke_{smoke_name}.jsonl"
            if jsonl_path.exists():
                _write_json(
                    output_dir / "smoke" / f"{variant}_{smoke_name}.json",
                    _read_jsonl(jsonl_path),
                )
            _copy_text(
                source_dir / f"smoke_{smoke_name}.md",
                output_dir / "smoke" / f"{variant}_{smoke_name}.md",
            )
        _copy_json(
            source_dir / "toolcall15.json",
            output_dir / "toolcall15" / f"{variant}.json",
        )


def _sanitize_bench_rows(rows: Any) -> Any:
    if not isinstance(rows, list):
        return _sanitize_json(rows)
    sanitized_rows = []
    for row in rows:
        sanitized = _sanitize_json(row)
        command = sanitized.get("command") if isinstance(sanitized, dict) else None
        if isinstance(command, list) and command:
            first = str(command[0])
            if first.startswith(("<", "/")) or "/" in first:
                command[0] = Path(first).name if first.startswith("/") else first
        sanitized_rows.append(sanitized)
    return sanitized_rows


def _performance_source(name: str, run_dir: Path) -> Json:
    phases = []
    for variant in VARIANTS:
        for phase, label in BENCH_PHASE_LABELS.items():
            phase_dir = run_dir / variant / phase
            if not phase_dir.exists():
                continue
            bench = _load_json(phase_dir / "bench.json") if (phase_dir / "bench.json").exists() else None
            phases.append(
                {
                    "source": name,
                    "variant": variant,
                    "phase": phase,
                    "phase_label": label,
                    "bench": _sanitize_bench_rows(bench),
                    "gpu_stats": _sanitize_json(
                        _load_json(phase_dir / "gpu_stats_summary.json")
                    )
                    if (phase_dir / "gpu_stats_summary.json").exists()
                    else None,
                    "runtime_stats": _sanitize_json(
                        _load_json(phase_dir / "runtime_stats_summary.json")
                    )
                    if (phase_dir / "runtime_stats_summary.json").exists()
                    else None,
                }
            )
    return {"source": name, "phases": phases}


def _write_manifest(
    run_dir: Path,
    output_dir: Path,
    *,
    label: str,
    date: str | None,
    supplement_dir: Path | None,
) -> None:
    env = _first_run_environment(run_dir)
    collect_env = _first_collect_env(run_dir)
    manifest = {
        "schema_version": 1,
        "label": label,
        "date": date,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": {
            "primary_run": run_dir.name,
            "supplement_run": supplement_dir.name if supplement_dir else None,
            "raw_artifacts_are_not_required": True,
        },
        "model": env.get("harness", {}).get("model", "deepseek-ai/DeepSeek-V4-Flash"),
        "gpu": env.get("gpu", {}),
        "collect_env": collect_env,
        "serve_commands": _serve_commands(run_dir),
        "phase_exit_codes": _phase_exit_codes(run_dir),
        "contents": {
            "oracle": "Deterministic no-MTP /v1/completions logprobs oracle cases.",
            "smoke": "no-MTP and MTP chat smoke request/response captures.",
            "toolcall15": "no-MTP and MTP ToolCall-15 traces and scores.",
            "performance": "Benchmark, runtime, and GPU telemetry summaries.",
        },
    }
    _write_json(output_dir / "manifest.json", _sanitize_json(manifest))


def _write_readme(output_dir: Path, label: str) -> None:
    _write_text(
        output_dir / "README.md",
        f"""# {label}

This is a curated public reference bundle for DeepSeek V4 SM12x validation. It
is derived from raw harness artifacts, but intentionally excludes machine-local
paths, server logs, tokens, and private connection details.

## Contents

- `manifest.json`: model, GPU topology, vLLM provenance, serve shape, and phase
  exit codes.
- `oracle/`: no-MTP deterministic `/v1/completions` cases with prompt token ids,
  generated tokens, token logprobs, top logprobs, and usage.
- `smoke/`: no-MTP and MTP chat smoke captures in JSON and Markdown.
- `toolcall15/`: no-MTP and MTP ToolCall-15 scores and traces.
- `performance/`: benchmark rows plus GPU/runtime telemetry summaries.

## Reuse

Run token-level comparison against a new local server:

```bash
python -m ds4_harness.cli oracle-compare \\
  --base-url http://127.0.0.1:8000 \\
  --oracle-dir baselines/{label}/oracle \\
  --top-n 20 \\
  --require-prompt-ids \\
  --json-output artifacts/manual/oracle_compare.json
```

For MTP, use the smoke and ToolCall-15 data as trajectory and behavior
references instead of requiring exact token equality.
""",
    )


def scan_public_bundle(path: Path) -> list[str]:
    findings: list[str] = []
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"{file_path.relative_to(path)}: binary file")
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                findings.append(
                    f"{file_path.relative_to(path)}: matched {pattern.pattern}"
                )
    return findings


def build_reference_bundle(
    *,
    run_dir: Path,
    output_dir: Path,
    label: str,
    date: str | None = None,
    supplement_dir: Path | None = None,
    fail_on_sensitive: bool = True,
) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_manifest(
        run_dir,
        output_dir,
        label=label,
        date=date,
        supplement_dir=supplement_dir,
    )
    _write_readme(output_dir, label)
    _copy_oracle(run_dir, output_dir)
    _copy_smoke_and_toolcall(run_dir, output_dir)
    _write_json(output_dir / "performance" / "primary.json", _performance_source("primary", run_dir))
    if supplement_dir is not None:
        _write_json(
            output_dir / "performance" / "supplement.json",
            _performance_source("supplement", supplement_dir),
        )

    findings = scan_public_bundle(output_dir)
    if findings and fail_on_sensitive:
        raise ValueError("reference bundle contains non-public data:\n" + "\n".join(findings))
    return findings
