from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BENCH_PHASE_LABELS = {
    "bench_hf_mt_bench": "HF/MT-Bench",
    "bench_random_8192x512": "Random 8192/512",
}
VARIANT_ORDER = {"nomtp": 0, "mtp": 1}


@dataclass(frozen=True)
class PhaseRecord:
    variant: str
    phase: str
    exit_code: int | None
    artifact_dir: Path


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt(value: Any, digits: int = 2, *, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return f"{value}{suffix}"
    number = _to_float(value)
    if number is None:
        return str(value)
    return f"{number:.{digits}f}{suffix}"


def _fmt_int(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return "n/a"
    return str(int(round(number)))


def _fmt_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return path.name


def _metadata(value: Any) -> str:
    return "n/a" if value is None or value == "" else str(value)


def _variant_sort_key(value: str) -> tuple[int, str]:
    return (VARIANT_ORDER.get(value, 99), value)


def _phase_dir(run_dir: Path, variant: str, phase: str, raw_path: str) -> Path:
    candidate = run_dir / variant / phase
    if candidate.exists():
        return candidate
    path = Path(raw_path)
    return path if path.exists() else candidate


def _parse_phase_log(run_dir: Path) -> list[PhaseRecord]:
    phase_log = run_dir / "phase_exit_codes.tsv"
    if not phase_log.exists():
        return _discover_phase_records(run_dir)

    records: list[PhaseRecord] = []
    for index, raw_line in enumerate(phase_log.read_text(encoding="utf-8").splitlines()):
        if index == 0 or not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        if len(parts) < 4:
            continue
        variant, phase, exit_code, artifact_dir = parts[:4]
        records.append(
            PhaseRecord(
                variant=variant,
                phase=phase,
                exit_code=_to_int(exit_code),
                artifact_dir=_phase_dir(run_dir, variant, phase, artifact_dir),
            )
        )
    return records


def _discover_phase_records(run_dir: Path) -> list[PhaseRecord]:
    records: list[PhaseRecord] = []
    for variant_dir in sorted(run_dir.iterdir() if run_dir.exists() else []):
        if not variant_dir.is_dir():
            continue
        for phase_dir in sorted(variant_dir.iterdir()):
            if phase_dir.is_dir():
                records.append(
                    PhaseRecord(
                        variant=variant_dir.name,
                        phase=phase_dir.name,
                        exit_code=None,
                        artifact_dir=phase_dir,
                    )
                )
    return records


def _first_environment(records: list[PhaseRecord]) -> dict[str, Any]:
    for record in records:
        if not record.phase.startswith("bench_"):
            continue
        summary = _load_json(record.artifact_dir / "run_environment.json")
        if isinstance(summary, dict):
            return summary
    for record in records:
        summary = _load_json(record.artifact_dir / "run_environment.json")
        if isinstance(summary, dict):
            return summary
    return {}


def _collect_env_summary(records: list[PhaseRecord]) -> dict[str, str]:
    for record in records:
        path = record.artifact_dir / "vllm_collect_env.txt"
        if not path.exists():
            continue
        return _parse_collect_env(path.read_text(encoding="utf-8", errors="replace"))
    return {}


def _parse_collect_env(text: str) -> dict[str, str]:
    summary: dict[str, str] = {}
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
            summary[key_map[key]] = value
        elif key == "CUDA Archs" and value:
            summary["vllm_cuda_archs"] = value.split(";", 1)[0].strip()

    version = summary.get("vllm_version", "")
    match = re.search(r"git sha:\s*([0-9A-Fa-f]+)", version)
    if match:
        summary["vllm_git_sha"] = match.group(1)
        summary["vllm_version"] = re.sub(r"\s*\(git sha:\s*[0-9A-Fa-f]+\)", "", version)
    return summary


def _gpu_count(env: dict[str, Any], gpu_stats: dict[str, Any] | None = None) -> int:
    count = _to_int(env.get("gpu", {}).get("count"))
    if count and count > 0:
        return count
    if isinstance(gpu_stats, dict):
        gpus = gpu_stats.get("gpus", {})
        if isinstance(gpus, dict) and gpus:
            return len(gpus)
    return 1


def _gpu_model_summary(env: dict[str, Any]) -> str:
    gpu = env.get("gpu", {})
    models = gpu.get("models", [])
    if not models:
        count = gpu.get("count")
        slug = gpu.get("topology_slug")
        return f"{count or 'n/a'} GPU(s), topology `{slug or 'n/a'}`"
    parts = []
    for model in models:
        memory = _to_float(model.get("memory_total_mib_each"))
        memory_gib = memory / 1024 if memory is not None else None
        parts.append(
            f"{model.get('count', 0)}x {model.get('name', 'unknown')}"
            f" ({_fmt(memory_gib, 1)} GiB each)"
        )
    return ", ".join(parts)


def _total_installed_vram_gib(
    env: dict[str, Any],
    gpu_stats: dict[str, Any] | None,
) -> float | None:
    total_mib = 0.0
    for model in env.get("gpu", {}).get("models", []):
        count = _to_float(model.get("count"))
        memory = _to_float(model.get("memory_total_mib_each"))
        if count is not None and memory is not None:
            total_mib += count * memory
    if total_mib > 0:
        return total_mib / 1024

    if isinstance(gpu_stats, dict):
        for gpu in gpu_stats.get("gpus", {}).values():
            memory = _to_float(gpu.get("memory_total_mib_max"))
            if memory is not None:
                total_mib += memory
    return total_mib / 1024 if total_mib > 0 else None


def _total_used_vram_gib(
    gpu_stats: dict[str, Any] | None,
    gpu_count: int,
) -> float | None:
    if not isinstance(gpu_stats, dict):
        return None
    total_mib = 0.0
    for gpu in gpu_stats.get("gpus", {}).values():
        used = _to_float(gpu.get("memory_used_mib_max"))
        if used is not None:
            total_mib += used
    if total_mib > 0:
        return total_mib / 1024
    overall = _to_float(gpu_stats.get("overall", {}).get("memory_used_mib_max"))
    return (overall * gpu_count) / 1024 if overall is not None else None


def _total_avg_power_w(
    gpu_stats: dict[str, Any] | None,
    gpu_count: int,
) -> float | None:
    if not isinstance(gpu_stats, dict):
        return None
    total = 0.0
    for gpu in gpu_stats.get("gpus", {}).values():
        power = _to_float(gpu.get("power_draw_w_avg"))
        if power is not None:
            total += power
    if total > 0:
        return total
    overall = _to_float(gpu_stats.get("overall", {}).get("power_draw_w_avg"))
    return overall * gpu_count if overall is not None else None


def _requests_label(row: dict[str, Any], metrics: dict[str, Any]) -> str:
    detail = str(row.get("detail") or "")
    marker = "successful_requests "
    if marker in detail:
        return detail.split(marker, 1)[1].split()[0]
    successful = metrics.get("successful_requests")
    return str(successful) if successful is not None else "n/a"


def _safe_divide(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return numerator / denominator


def _bench_rows(
    records: list[PhaseRecord],
    fallback_env: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        if not record.phase.startswith("bench_"):
            continue
        bench = _load_json(record.artifact_dir / "bench.json")
        if not isinstance(bench, list):
            continue
        env = _load_json(record.artifact_dir / "run_environment.json")
        if not isinstance(env, dict):
            env = fallback_env
        gpu_stats = _load_json(record.artifact_dir / "gpu_stats_summary.json")
        gpu_count = _gpu_count(env, gpu_stats if isinstance(gpu_stats, dict) else None)
        total_vram_gib = _total_installed_vram_gib(env, gpu_stats)
        used_vram_gib = _total_used_vram_gib(gpu_stats, gpu_count)
        total_power_w = _total_avg_power_w(gpu_stats, gpu_count)
        gpu_overall = gpu_stats.get("overall", {}) if isinstance(gpu_stats, dict) else {}

        for item in bench:
            if not isinstance(item, dict):
                continue
            metrics = item.get("metrics", {})
            output_tok_s = _to_float(metrics.get("output_token_throughput_tok_s"))
            req_s = _to_float(metrics.get("request_throughput_req_s"))
            tok_joule = _safe_divide(output_tok_s, total_power_w)
            rows.append(
                {
                    "variant": record.variant,
                    "phase": record.phase,
                    "phase_label": BENCH_PHASE_LABELS.get(record.phase, record.phase),
                    "concurrency": item.get("concurrency"),
                    "ok": item.get("ok"),
                    "requests": _requests_label(item, metrics),
                    "request_throughput_req_s": req_s,
                    "output_token_throughput_tok_s": output_tok_s,
                    "mean_ttft_ms": _to_float(metrics.get("mean_ttft_ms")),
                    "mean_tpot_ms": _to_float(metrics.get("mean_tpot_ms")),
                    "mean_itl_ms": _to_float(metrics.get("mean_itl_ms")),
                    "gpu_count": gpu_count,
                    "tok_s_per_gpu": _safe_divide(output_tok_s, float(gpu_count)),
                    "req_s_per_gpu": _safe_divide(req_s, float(gpu_count)),
                    "tok_s_per_total_vram_gib": _safe_divide(output_tok_s, total_vram_gib),
                    "tok_s_per_used_vram_gib": _safe_divide(output_tok_s, used_vram_gib),
                    "tok_per_joule": tok_joule,
                    "tok_s_per_kw": tok_joule * 1000 if tok_joule is not None else None,
                    "total_vram_gib": total_vram_gib,
                    "used_vram_gib": used_vram_gib,
                    "avg_total_power_w": total_power_w,
                    "max_per_gpu_power_w": _to_float(gpu_overall.get("power_draw_w_max")),
                    "avg_gpu_util_percent": _to_float(
                        gpu_overall.get("gpu_utilization_percent_avg")
                    ),
                }
            )
    return sorted(
        rows,
        key=lambda row: (
            _variant_sort_key(row["variant"]),
            row["phase"],
            _to_float(row["concurrency"]) or 0,
        ),
    )


def _acceptance_gate_rows(records: list[PhaseRecord]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        if record.phase != "acceptance":
            continue
        for path in sorted(record.artifact_dir.glob("*.exit_code")):
            rows.append(
                {
                    "variant": record.variant,
                    "gate": path.name.removesuffix(".exit_code"),
                    "exit_code": path.read_text(encoding="utf-8").strip(),
                }
            )
    return sorted(rows, key=lambda row: (_variant_sort_key(row["variant"]), row["gate"]))


def _toolcall_rows(records: list[PhaseRecord]) -> list[dict[str, Any]]:
    rows = []
    for record in records:
        if record.phase != "acceptance":
            continue
        data = _load_json(record.artifact_dir / "toolcall15.json")
        if not isinstance(data, dict):
            continue
        summary = data.get("summary", {})
        failures = [
            result
            for result in data.get("results", [])
            if result.get("status") != "pass" or not result.get("ok", True)
        ]
        rows.append({"variant": record.variant, "summary": summary, "failures": failures})
    return sorted(rows, key=lambda row: _variant_sort_key(row["variant"]))


def _oracle_rows(records: list[PhaseRecord]) -> list[dict[str, Any]]:
    rows = []
    for record in records:
        if record.phase != "oracle_export":
            continue
        data = _load_json(record.artifact_dir / "oracle_export_summary.json")
        if isinstance(data, dict):
            rows.append({"variant": record.variant, **data})
    return sorted(rows, key=lambda row: _variant_sort_key(row["variant"]))


def _runtime_rows(records: list[PhaseRecord]) -> list[dict[str, Any]]:
    rows = []
    for record in records:
        if not record.phase.startswith("bench_"):
            continue
        data = _load_json(record.artifact_dir / "runtime_stats_summary.json")
        if not isinstance(data, dict):
            continue
        metrics = data.get("metrics", {})
        serve_log = data.get("serve_log", {})
        rows.append(
            {
                "variant": record.variant,
                "phase": record.phase,
                "phase_label": BENCH_PHASE_LABELS.get(record.phase, record.phase),
                "metrics": metrics,
                "serve_log": serve_log,
            }
        )
    return sorted(rows, key=lambda row: (_variant_sort_key(row["variant"]), row["phase"]))


def _collect_env_status(records: list[PhaseRecord]) -> tuple[int, int, list[str]]:
    total = 0
    ok = 0
    failed = []
    for record in records:
        path = record.artifact_dir / "vllm_collect_env.exit_code"
        if not path.exists():
            continue
        total += 1
        code = path.read_text(encoding="utf-8").strip()
        if code == "0":
            ok += 1
        else:
            failed.append(f"{record.variant}/{record.phase}: {code}")
    return total, ok, failed


def _unresponsive_markers(run_dir: Path) -> list[str]:
    markers = []
    for pattern in ("**/server_unresponsive.txt", "**/*.server_unresponsive"):
        for path in sorted(run_dir.glob(pattern)):
            try:
                markers.append(str(path.relative_to(run_dir)))
            except ValueError:
                markers.append(path.name)
    return sorted(set(markers))


def _spec_decode_rows(runtime_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in runtime_rows:
        spec = row.get("serve_log", {}).get("spec_decode", {})
        if spec.get("samples"):
            rows.append({**row, "spec": spec})
    return rows


def _best_benchmark_rows(
    source: str,
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    best: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        output = _to_float(row.get("output_token_throughput_tok_s"))
        if output is None:
            continue
        key = (row["variant"], row["phase"])
        current = _to_float(best.get(key, {}).get("output_token_throughput_tok_s"))
        if key not in best or current is None or output > current:
            best[key] = {**row, "source": source}
    return sorted(
        best.values(),
        key=lambda row: (_variant_sort_key(row["variant"]), row["phase"]),
    )


def _append_quick_performance_summary(
    lines: list[str],
    primary_bench_rows: list[dict[str, Any]],
    supplement_bench_rows: list[dict[str, Any]],
    runtime_rows: list[dict[str, Any]],
    *,
    runtime_source: str,
) -> None:
    best_rows = _best_benchmark_rows("Primary", primary_bench_rows)
    if supplement_bench_rows:
        best_rows.extend(_best_benchmark_rows("Supplement", supplement_bench_rows))

    if not best_rows and not runtime_rows:
        return

    lines.extend(["## Quick Performance Summary", ""])
    if best_rows:
        lines.extend(
            [
                "### Best Benchmark Throughput",
                "",
                "| Source | Variant | Phase | C | Output tok/s | tok/s/GPU | Mean TTFT ms | Mean TPOT ms |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in best_rows:
            lines.append(
                f"| {row['source']} | `{row['variant']}` | {row['phase_label']} | "
                f"{row['concurrency']} | {_fmt(row['output_token_throughput_tok_s'])} | "
                f"{_fmt(row['tok_s_per_gpu'])} | {_fmt(row['mean_ttft_ms'])} | "
                f"{_fmt(row['mean_tpot_ms'])} |"
            )
        lines.append("")

    if runtime_rows:
        lines.extend(
            [
                "### Runtime Prefill/Decode Averages",
                "",
                "These are phase-local averages parsed from vLLM server logs.",
                "",
                "| Source | Variant | Phase | Prefill avg tok/s | Decode avg tok/s | Prefill tokens | Decode tokens | Max running |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in runtime_rows:
            metrics = row["metrics"]
            serve_log = row["serve_log"]
            lines.append(
                f"| {runtime_source} | `{row['variant']}` | {row['phase_label']} | "
                f"{_fmt(serve_log.get('prefill_throughput_tok_s_avg'))} | "
                f"{_fmt(serve_log.get('decode_throughput_tok_s_avg'))} | "
                f"{_fmt_int(metrics.get('prefill_tokens_delta'))} | "
                f"{_fmt_int(metrics.get('decode_tokens_delta'))} | "
                f"{_fmt_int(metrics.get('running_requests_max'))} |"
            )
        lines.append("")


def _serve_shape_rows(run_dir: Path, records: list[PhaseRecord]) -> list[dict[str, Any]]:
    variants = sorted({record.variant for record in records}, key=_variant_sort_key)
    rows = []
    for variant in variants:
        command_path = run_dir / variant / "serve_command.sh"
        if not command_path.exists():
            continue
        row = _parse_serve_command(command_path.read_text(encoding="utf-8"))
        if row:
            row["variant"] = variant
            rows.append(row)
    return rows


def _parse_serve_command(text: str) -> dict[str, Any]:
    for line in text.splitlines():
        if " vllm serve " not in f" {line} " and "vllm serve " not in line:
            continue
        tokens = shlex.split(line)
        if "serve" not in tokens:
            continue
        args = tokens[tokens.index("serve") + 1 :]
        return _serve_args_summary(args)
    return {}


def _serve_args_summary(args: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "model": args[0] if args else None,
        "kv_cache_dtype": None,
        "block_size": None,
        "tensor_parallel_size": None,
        "speculative_config": None,
        "reasoning_parser": None,
        "tokenizer_mode": None,
        "tool_call_parser": None,
        "auto_tool_choice": False,
        "fp4_indexer_cache": False,
        "flashinfer_autotune_disabled": False,
    }
    options_with_values = {
        "--kv-cache-dtype": "kv_cache_dtype",
        "--block-size": "block_size",
        "--tensor-parallel-size": "tensor_parallel_size",
        "--speculative_config": "speculative_config",
        "--speculative-config": "speculative_config",
        "--reasoning-parser": "reasoning_parser",
        "--tokenizer-mode": "tokenizer_mode",
        "--tool-call-parser": "tool_call_parser",
    }
    index = 1
    while index < len(args):
        token = args[index]
        if token in options_with_values and index + 1 < len(args):
            summary[options_with_values[token]] = args[index + 1]
            index += 2
            continue
        if token == "--enable-auto-tool-choice":
            summary["auto_tool_choice"] = True
        elif token == "--no-enable-flashinfer-autotune":
            summary["flashinfer_autotune_disabled"] = True
        elif token.startswith("--attention_config.use_fp4_indexer_cache"):
            _, _, raw_value = token.partition("=")
            summary["fp4_indexer_cache"] = raw_value.casefold() == "true"
        index += 1
    return summary


def _yes_no(value: Any) -> str:
    return "yes" if bool(value) else "no"


def _append_provenance(lines: list[str], summary: dict[str, str]) -> None:
    if not summary:
        return
    lines.extend(
        [
            "## Provenance",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| vLLM | `{_metadata(summary.get('vllm_version'))}` |",
            f"| vLLM git sha | `{_metadata(summary.get('vllm_git_sha'))}` |",
            f"| vLLM CUDA archs | `{_metadata(summary.get('vllm_cuda_archs'))}` |",
            f"| PyTorch | `{_metadata(summary.get('pytorch_version'))}` |",
            f"| PyTorch CUDA build | `{_metadata(summary.get('pytorch_cuda_build'))}` |",
            f"| CUDA runtime | `{_metadata(summary.get('cuda_runtime_version'))}` |",
            f"| NVIDIA driver | `{_metadata(summary.get('nvidia_driver_version'))}` |",
            f"| Transformers | `{_metadata(summary.get('transformers_version'))}` |",
            f"| Triton | `{_metadata(summary.get('triton_version'))}` |",
            "",
        ]
    )


def _append_serve_shape(lines: list[str], rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    lines.extend(
        [
            "## Serve Shape",
            "",
            "| Variant | KV dtype | Block size | TP | Speculative config | Reasoning parser | Tokenizer mode | Tool parser | Auto tool | FP4 index cache | FlashInfer autotune disabled |",
            "| --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['variant']}` | `{_metadata(row.get('kv_cache_dtype'))}` | "
            f"{_metadata(row.get('block_size'))} | "
            f"{_metadata(row.get('tensor_parallel_size'))} | "
            f"`{_metadata(row.get('speculative_config'))}` | "
            f"`{_metadata(row.get('reasoning_parser'))}` | "
            f"`{_metadata(row.get('tokenizer_mode'))}` | "
            f"`{_metadata(row.get('tool_call_parser'))}` | "
            f"{_yes_no(row.get('auto_tool_choice'))} | "
            f"{_yes_no(row.get('fp4_indexer_cache'))} | "
            f"{_yes_no(row.get('flashinfer_autotune_disabled'))} |"
        )
    lines.append("")


def _append_phase_table(lines: list[str], records: list[PhaseRecord]) -> None:
    lines.extend(
        [
            "## Phase Exit Codes",
            "",
            "| Variant | Phase | Exit | Artifact |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for record in records:
        artifact = f"{record.variant}/{record.phase}"
        lines.append(
            f"| `{record.variant}` | `{record.phase}` | "
            f"{_fmt_int(record.exit_code)} | `{artifact}` |"
        )
    lines.append("")


def _append_acceptance_gates(lines: list[str], rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    lines.extend(
        [
            "## Acceptance Gates",
            "",
            "| Variant | Gate | Exit |",
            "| --- | --- | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['variant']}` | `{row['gate']}` | {row['exit_code']} |"
        )
    lines.append("")


def _append_benchmark_tables(
    lines: list[str],
    rows: list[dict[str, Any]],
    *,
    title_prefix: str = "",
) -> None:
    if not rows:
        return
    prefix = f"{title_prefix} " if title_prefix else ""
    lines.extend(
        [
            f"## {prefix}Benchmark Throughput",
            "",
            "| Variant | Phase | C | Requests | Req/s | Output tok/s | Avg GPU util % | Max power/GPU W |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['variant']}` | {row['phase_label']} | {row['concurrency']} | "
            f"{row['requests']} | {_fmt(row['request_throughput_req_s'])} | "
            f"{_fmt(row['output_token_throughput_tok_s'])} | "
            f"{_fmt(row['avg_gpu_util_percent'])} | {_fmt(row['max_per_gpu_power_w'])} |"
        )

    lines.extend(
        [
            "",
            f"## {prefix}Normalized Efficiency",
            "",
            (
                "Power efficiency uses sampled average GPU power for the whole phase. "
                "It is GPU-side power, not wall-plug power."
            ),
            "",
            "| Variant | Phase | C | Requests | Output tok/s | tok/s/GPU | tok/s/total GiB | tok/s/used GiB | tok/J | tok/s/kW |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['variant']}` | {row['phase_label']} | {row['concurrency']} | "
            f"{row['requests']} | {_fmt(row['output_token_throughput_tok_s'])} | "
            f"{_fmt(row['tok_s_per_gpu'])} | "
            f"{_fmt(row['tok_s_per_total_vram_gib'])} | "
            f"{_fmt(row['tok_s_per_used_vram_gib'])} | "
            f"{_fmt(row['tok_per_joule'])} | {_fmt(row['tok_s_per_kw'])} |"
        )

    lines.extend(
        [
            "",
            f"## {prefix}Benchmark Latency",
            "",
            "| Variant | Phase | C | Mean TTFT ms | Mean TPOT ms | Mean ITL ms |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['variant']}` | {row['phase_label']} | {row['concurrency']} | "
            f"{_fmt(row['mean_ttft_ms'])} | {_fmt(row['mean_tpot_ms'])} | "
            f"{_fmt(row['mean_itl_ms'])} |"
        )
    lines.append("")


def _append_toolcall(lines: list[str], rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    lines.extend(
        [
            "## ToolCall-15",
            "",
            "| Variant | Score | Cases | Failures |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        summary = row["summary"]
        score = f"{summary.get('points', 'n/a')}/{summary.get('max_points', 'n/a')}"
        lines.append(
            f"| `{row['variant']}` | {score} ({summary.get('score_percent', 'n/a')}%) | "
            f"{summary.get('cases', 'n/a')} | {summary.get('failures', 'n/a')} |"
        )
    lines.append("")
    for row in rows:
        if not row["failures"]:
            continue
        lines.extend([f"### `{row['variant']}` Failures", ""])
        for failure in row["failures"]:
            lines.append(
                f"- `{failure.get('id')}` {failure.get('status')} "
                f"({failure.get('points')} points): {failure.get('summary')}"
            )
        lines.append("")


def _append_oracle(lines: list[str], rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    lines.extend(
        [
            "## Oracle Export",
            "",
            "| Variant | Cases | Success | Model |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['variant']}` | {row.get('case_count', 'n/a')} | "
            f"{row.get('success_count', 'n/a')} | `{row.get('model', 'n/a')}` |"
        )
    lines.append("")


def _append_runtime(lines: list[str], rows: list[dict[str, Any]], title: str) -> None:
    if not rows:
        return
    lines.extend(
        [
            f"## {title}",
            "",
            "| Variant | Phase | Prefill delta | Decode delta | Successful delta | Max running | Log prefill tok/s | Log decode tok/s |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        metrics = row["metrics"]
        serve_log = row["serve_log"]
        lines.append(
            f"| `{row['variant']}` | {row['phase_label']} | "
            f"{_fmt_int(metrics.get('prefill_tokens_delta'))} | "
            f"{_fmt_int(metrics.get('decode_tokens_delta'))} | "
            f"{_fmt_int(metrics.get('successful_requests_delta'))} | "
            f"{_fmt_int(metrics.get('running_requests_max'))} | "
            f"{_fmt(serve_log.get('prefill_throughput_tok_s_avg'))} | "
            f"{_fmt(serve_log.get('decode_throughput_tok_s_avg'))} |"
        )
    lines.append("")


def _append_spec_decode(lines: list[str], rows: list[dict[str, Any]]) -> None:
    spec_rows = _spec_decode_rows(rows)
    if not spec_rows:
        return
    lines.extend(
        [
            "## MTP Speculative Decoding",
            "",
            "| Variant | Phase | Samples | Mean acceptance length | Avg draft acceptance % | Per-position acceptance | Accepted tokens | Drafted tokens |",
            "| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |",
        ]
    )
    for row in spec_rows:
        spec = row["spec"]
        per_position = spec.get("per_position_acceptance_rate_avg") or []
        per_position_text = ", ".join(_fmt(value, 3) for value in per_position)
        lines.append(
            f"| `{row['variant']}` | {row['phase_label']} | "
            f"{_fmt_int(spec.get('samples'))} | "
            f"{_fmt(spec.get('mean_acceptance_length_avg'))} | "
            f"{_fmt(spec.get('avg_draft_acceptance_rate_percent_avg'))} | "
            f"`[{per_position_text}]` | "
            f"{_fmt_int(spec.get('accepted_tokens_observed'))} | "
            f"{_fmt_int(spec.get('drafted_tokens_observed'))} |"
        )
    lines.append("")


def build_baseline_report(
    run_dir: Path,
    *,
    supplement_dir: Path | None = None,
    title: str = "DeepSeek V4 Baseline Report",
    label: str | None = None,
) -> str:
    run_dir = Path(run_dir)
    records = _parse_phase_log(run_dir)
    env = _first_environment(records)
    collect_env_summary = _collect_env_summary(records)
    serve_shape_rows = _serve_shape_rows(run_dir, records)
    bench_rows = _bench_rows(records, env)
    runtime_rows = _runtime_rows(records)
    acceptance_gate_rows = _acceptance_gate_rows(records)
    toolcall_rows = _toolcall_rows(records)
    oracle_rows = _oracle_rows(records)
    collect_env_total, collect_env_ok, collect_env_failed = _collect_env_status(records)
    unresponsive_markers = _unresponsive_markers(run_dir)

    supplement_records: list[PhaseRecord] = []
    supplement_bench_rows: list[dict[str, Any]] = []
    supplement_runtime_rows: list[dict[str, Any]] = []
    if supplement_dir is not None:
        supplement_dir = Path(supplement_dir)
        supplement_records = _parse_phase_log(supplement_dir)
        supplement_env = _first_environment(supplement_records) or env
        supplement_bench_rows = _bench_rows(supplement_records, supplement_env)
        supplement_runtime_rows = _runtime_rows(supplement_records)

    harness = env.get("harness", {})
    artifact = env.get("artifact", {})
    lines = [
        f"# {title}",
        "",
        f"- Label: `{label or run_dir.name}`",
        f"- Artifact generated at UTC: `{_metadata(env.get('generated_at_utc'))}`",
        f"- Primary artifact: `{_fmt_path(run_dir)}`",
    ]
    if supplement_dir is not None:
        lines.append(f"- Supplement artifact: `{_fmt_path(supplement_dir)}`")
    lines.extend(
        [
            f"- Model: `{_metadata(harness.get('model'))}`",
            f"- Branch: `{_metadata(artifact.get('branch_name'))}`",
            f"- GPU: {_gpu_model_summary(env)}",
            f"- Dataset: `{_metadata(harness.get('dataset_name'))}` / `{_metadata(harness.get('dataset_path'))}`",
            "",
        ]
    )

    lines.extend(
        [
            "## Run Health",
            "",
            f"- vLLM collect_env: {collect_env_ok}/{collect_env_total} phase captures exited 0",
            "- Server unresponsive markers: "
            + (", ".join(f"`{marker}`" for marker in unresponsive_markers) or "none"),
        ]
    )
    if collect_env_failed:
        lines.append(
            "- collect_env failures: "
            + ", ".join(f"`{failure}`" for failure in collect_env_failed)
        )
    lines.append("")

    _append_provenance(lines, collect_env_summary)
    _append_serve_shape(lines, serve_shape_rows)
    summary_runtime_rows = supplement_runtime_rows or runtime_rows
    _append_quick_performance_summary(
        lines,
        bench_rows,
        supplement_bench_rows,
        summary_runtime_rows,
        runtime_source="Supplement" if supplement_runtime_rows else "Primary",
    )
    _append_phase_table(lines, records)
    _append_acceptance_gates(lines, acceptance_gate_rows)
    _append_benchmark_tables(lines, bench_rows)
    _append_toolcall(lines, toolcall_rows)
    _append_oracle(lines, oracle_rows)
    if supplement_bench_rows:
        _append_benchmark_tables(lines, supplement_bench_rows, title_prefix="Supplement")
    if supplement_runtime_rows:
        _append_runtime(lines, supplement_runtime_rows, "Supplement Runtime Stats")
        _append_spec_decode(lines, supplement_runtime_rows)
    elif runtime_rows:
        _append_runtime(lines, runtime_rows, "Runtime Stats")
        _append_spec_decode(lines, runtime_rows)

    if supplement_records:
        lines.extend(
            [
                "## Supplement Phase Exit Codes",
                "",
                "| Variant | Phase | Exit | Artifact |",
                "| --- | --- | ---: | --- |",
            ]
        )
        for record in supplement_records:
            lines.append(
                f"| `{record.variant}` | `{record.phase}` | "
                f"{_fmt_int(record.exit_code)} | `{record.variant}/{record.phase}` |"
            )
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- `tok/s/GPU` divides output token throughput by detected GPU count.",
            "- `tok/s/total GiB` divides output token throughput by installed GPU VRAM.",
            "- `tok/s/used GiB` divides output token throughput by sampled peak used GPU VRAM.",
            "- `tok/J` and `tok/s/kW` use sampled average GPU power for the phase.",
            "- Benchmark power and VRAM denominators are phase-level samples, not per-concurrency samples.",
            "- Quick runtime prefill/decode averages use supplement rows when a supplement artifact is provided.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_baseline_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
