from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


Json = dict[str, Any]


def _load_json(path: Path) -> Json | list[Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _phase_exit_codes(run_root: Path) -> list[Json]:
    path = run_root / "phase_exit_codes.tsv"
    rows: list[Json] = []
    if not path.exists():
        diagnostic_path = run_root / "diagnostic_cases.tsv"
        if not diagnostic_path.exists():
            return []
        with diagnostic_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                try:
                    exit_code = int(row.get("exit_code", "1"))
                except ValueError:
                    exit_code = 1
                case = row.get("case", "")
                filler_words = row.get("filler_words", "")
                variant = f"{case}/filler_{filler_words}" if filler_words else case
                rows.append(
                    {
                        "variant": variant,
                        "phase": "prefix_cache_stress",
                        "exit_code": exit_code,
                        "artifact_dir": row.get("artifact_dir", ""),
                    }
                )
        return rows
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            try:
                exit_code = int(row.get("exit_code", "1"))
            except ValueError:
                exit_code = 1
            rows.append(
                {
                    "variant": row.get("variant", ""),
                    "phase": row.get("phase", ""),
                    "exit_code": exit_code,
                    "artifact_dir": row.get("artifact_dir", ""),
                }
            )
    return rows


def _variant_dirs(run_root: Path) -> list[Path]:
    phase_rows = _phase_exit_codes(run_root)
    variants = sorted({row["variant"] for row in phase_rows if row.get("variant")})
    dirs = [run_root / variant for variant in variants if (run_root / variant).is_dir()]
    if dirs:
        return dirs
    return sorted(path for path in run_root.iterdir() if path.is_dir())


def _round_float(value: Any, digits: int = 3) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


def _round_float_map(value: Any, digits: int = 3) -> Json | None:
    if isinstance(value, list):
        items = [(str(index), item) for index, item in enumerate(value)]
    elif isinstance(value, dict):
        keys = sorted(
            value,
            key=lambda item: int(item) if str(item).isdigit() else str(item),
        )
        items = [(str(key), value.get(key)) for key in keys]
    else:
        return None
    rounded: Json = {}
    for key, raw_value in items:
        rounded_value = _round_float(raw_value, digits)
        if rounded_value is not None:
            rounded[key] = rounded_value
    return rounded or None


def _summary_rows(payload: Json | list[Any] | None) -> list[Json]:
    if isinstance(payload, dict) and isinstance(payload.get("summary"), list):
        return [row for row in payload["summary"] if isinstance(row, dict)]
    return []


def _collect_latency_rows(run_label: str, variant: str, phase: str, payload: Any) -> list[Json]:
    rows: list[Json] = []
    for row in _summary_rows(payload):
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "phase": phase,
                "prompt": row.get("prompt"),
                "cache_mode": row.get("cache_mode"),
                "concurrency": row.get("concurrency"),
                "requests": row.get("request_count"),
                "failures": row.get("failure_count"),
                "ttft_mean_s": _round_float(row.get("ttft_seconds_mean")),
                "ttft_max_s": _round_float(row.get("ttft_seconds_max")),
                "decode_mean_tps": _round_float(row.get("decode_tokens_per_second_mean")),
                "decode_min_tps": _round_float(row.get("decode_tokens_per_second_min")),
                "decode_max_tps": _round_float(row.get("decode_tokens_per_second_max")),
                "decode_min_max_ratio": _round_float(row.get("decode_tps_min_to_max_ratio")),
                "itl_p95_s": _round_float(row.get("p95_inter_chunk_seconds")),
                "itl_p99_s": _round_float(row.get("p99_inter_chunk_seconds")),
                "itl_max_s": _round_float(row.get("max_inter_chunk_seconds")),
                "prompt_tokens": _round_float(row.get("prompt_tokens_mean"), 0),
            }
        )
    return rows


def _collect_mixed_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    rows: list[Json] = []
    for row in _summary_rows(payload):
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "case": row.get("case"),
                "requests": row.get("request_count"),
                "failures": row.get("failure_count"),
                "primary_ttft_mean_s": _round_float(row.get("primary_ttft_seconds_mean")),
                "secondary_ttft_mean_s": _round_float(row.get("secondary_ttft_seconds_mean")),
                "decode_min_max_ratio": _round_float(row.get("decode_tps_min_to_max_ratio")),
                "secondary_itl_p95_s": _round_float(row.get("secondary_p95_inter_chunk_seconds")),
                "secondary_itl_p99_s": _round_float(row.get("secondary_p99_inter_chunk_seconds")),
                "secondary_start_vs_primary_ttft_s": _round_float(
                    row.get("secondary_start_after_primary_ttft_seconds")
                ),
            }
        )
    return rows


def _collect_streaming_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, dict) or not isinstance(payload.get("summary"), dict):
        return []
    summary = payload["summary"]
    return [
        {
            "run": run_label,
            "variant": variant,
            "cases": summary.get("case_count"),
            "requests": summary.get("request_count"),
            "failures": summary.get("failure_count"),
            "slow_cases": summary.get("slow_case_count"),
            "max_ttft_s": _round_float(summary.get("max_ttft_seconds")),
            "max_elapsed_s": _round_float(summary.get("max_elapsed_seconds")),
            "itl_p95_s": _round_float(summary.get("p95_inter_chunk_seconds")),
            "itl_p99_s": _round_float(summary.get("p99_inter_chunk_seconds")),
            "itl_max_s": _round_float(summary.get("max_inter_chunk_seconds")),
        }
    ]


def _collect_bench_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, list):
        return []
    rows: list[Json] = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "concurrency": row.get("concurrency"),
                "successful_requests": metrics.get("successful_requests"),
                "output_tps": _round_float(metrics.get("output_token_throughput_tok_s")),
                "ttft_mean_ms": _round_float(metrics.get("mean_ttft_ms")),
                "ttft_p99_ms": _round_float(metrics.get("p99_ttft_ms")),
                "itl_p99_ms": _round_float(metrics.get("p99_itl_ms")),
                "spec_acceptance_percent": _round_float(
                    metrics.get("spec_acceptance_rate_percent")
                ),
                "spec_acceptance_length": _round_float(metrics.get("spec_acceptance_length")),
                "spec_per_position_acceptance_percent": _round_float_map(
                    metrics.get("spec_per_position_acceptance_percent")
                ),
            }
        )
    return rows


def _collect_gsm8k_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        return []
    rows: list[Json] = []
    for task in payload["tasks"]:
        if not isinstance(task, dict):
            continue
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "task": task.get("task"),
                "exact_match_flexible": _round_float(task.get("exact_match_flexible"), 4),
                "exact_match_strict": _round_float(task.get("exact_match_strict"), 4),
            }
        )
    return rows


def _collect_prefill_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, dict) or not isinstance(payload.get("rows"), list):
        return []
    rows: list[Json] = []
    for row in payload["rows"]:
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "case": row.get("case"),
                "ok": row.get("ok"),
                "input_tps": _round_float(row.get("input_token_throughput_tok_s")),
                "ttft_mean_ms": _round_float(row.get("mean_ttft_ms")),
                "ttft_p99_ms": _round_float(row.get("p99_ttft_ms")),
                "successful_requests": row.get("successful_requests"),
            }
        )
    return rows


def _collect_frontier_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    rows: list[Json] = []
    for row in _summary_rows(payload):
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "prompt": row.get("prompt"),
                "target_frontier_tokens": row.get("target_frontier_tokens"),
                "requests": row.get("request_count"),
                "failures": row.get("failure_count"),
                "prompt_tokens": _round_float(row.get("prompt_tokens_mean"), 0),
                "ttft_mean_s": _round_float(row.get("ttft_seconds_mean")),
                "ttft_max_s": _round_float(row.get("ttft_seconds_max")),
                "input_tps": _round_float(row.get("input_tokens_per_second_mean")),
                "decode_mean_tps": _round_float(row.get("decode_tokens_per_second_mean")),
                "itl_p95_s": _round_float(row.get("p95_inter_chunk_seconds")),
                "itl_p99_s": _round_float(row.get("p99_inter_chunk_seconds")),
                "itl_max_s": _round_float(row.get("max_inter_chunk_seconds")),
            }
        )
    return rows


def _collect_story_recall_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    summary_rows = _summary_rows(payload)
    request_rows = (
        [
            row
            for row in payload.get("requests", [])
            if isinstance(row, dict) and row.get("phase") == "measure"
        ]
        if isinstance(payload, dict) and isinstance(payload.get("requests"), list)
        else []
    )
    matched_counts = [
        value
        for value in (
            _round_float(row.get("story_recall_matched_count"), 0)
            for row in request_rows
            if row.get("semantic_check") == "ds4_story_recall"
        )
        if value is not None
    ]
    missing = sorted(
        {
            str(name)
            for row in request_rows
            for name in (
                row.get("story_recall_missing")
                if isinstance(row.get("story_recall_missing"), list)
                else []
            )
        }
    )
    finish_reasons = sorted(
        {
            str(row.get("finish_reason"))
            for row in request_rows
            if row.get("finish_reason") is not None
        }
    )

    rows: list[Json] = []
    for row in summary_rows:
        rows.append(
            {
                "run": run_label,
                "variant": variant,
                "prompt": row.get("prompt"),
                "concurrency": row.get("concurrency"),
                "requests": row.get("request_count"),
                "failures": row.get("failure_count"),
                "matched_min": min(matched_counts) if matched_counts else None,
                "missing": ",".join(missing) if missing else "",
                "finish_reasons": ",".join(finish_reasons) if finish_reasons else "",
                "prompt_tokens": _round_float(row.get("prompt_tokens_mean"), 0),
                "ttft_mean_s": _round_float(row.get("ttft_seconds_mean")),
                "ttft_max_s": _round_float(row.get("ttft_seconds_max")),
                "decode_mean_tps": _round_float(row.get("decode_tokens_per_second_mean")),
                "itl_p99_s": _round_float(row.get("p99_inter_chunk_seconds")),
            }
        )
    return rows


def _collect_prefix_cache_rows(
    run_label: str,
    variant: str,
    payload: Any,
    *,
    diagnostic_case: str | None = None,
    filler_words: int | str | None = None,
) -> list[Json]:
    if not isinstance(payload, dict) or not isinstance(payload.get("summary"), dict):
        return []
    summary = payload["summary"]
    config = payload.get("config") if isinstance(payload.get("config"), dict) else {}
    if filler_words is None:
        filler_words = config.get("filler_words")
    try:
        filler_words = int(filler_words) if filler_words is not None else None
    except (TypeError, ValueError):
        pass
    return [
        {
            "run": run_label,
            "variant": variant,
            "case": diagnostic_case or payload.get("case"),
            "filler_words": filler_words,
            "ok": payload.get("ok"),
            "health_status": payload.get("health_status"),
            "trials": summary.get("trial_count"),
            "failures": summary.get("failure_count"),
            "solo_hit_rate_mean": _round_float(summary.get("solo_hit_rate_mean"), 4),
            "concurrent_hit_rate_mean": _round_float(
                summary.get("concurrent_hit_rate_mean"), 4
            ),
        }
    ]


def _collect_prefix_cache_diagnostic_rows(run_label: str, run_root: Path) -> list[Json]:
    path = run_root / "diagnostic_cases.tsv"
    if not path.exists():
        return []
    rows: list[Json] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            artifact_dir = Path(row.get("artifact_dir", ""))
            if not artifact_dir.is_absolute():
                artifact_dir = run_root / artifact_dir
            payloads = sorted(
                artifact_dir.glob("*/prefix_cache_stress/prefix_cache_stress.json")
            )
            for payload_path in payloads:
                payload = _load_json(payload_path)
                variant = payload_path.parents[1].name
                rows.extend(
                    _collect_prefix_cache_rows(
                        run_label,
                        variant,
                        payload,
                        diagnostic_case=row.get("case"),
                        filler_words=row.get("filler_words"),
                    )
                )
    return rows


def _collect_kv_lifecycle_rows(run_label: str, variant: str, payload: Any) -> list[Json]:
    if not isinstance(payload, dict) or not isinstance(payload.get("summary"), dict):
        return []
    summary = payload["summary"]
    return [
        {
            "run": run_label,
            "variant": variant,
            "case": payload.get("case"),
            "cache_mode": payload.get("cache_mode"),
            "ok": payload.get("ok"),
            "requests": summary.get("request_count"),
            "failures": summary.get("failure_count"),
            "idle_failures": summary.get("idle_failure_count"),
            "initial_idle_kv_percent": _round_float(
                summary.get("initial_idle_kv_usage_percent")
            ),
            "final_idle_kv_percent": _round_float(
                summary.get("final_idle_kv_usage_percent")
            ),
            "max_idle_kv_percent": _round_float(summary.get("max_idle_kv_usage_percent")),
            "threshold_percent": _round_float(
                summary.get("max_idle_kv_usage_percent_threshold")
            ),
            "idle_kv_within_threshold": summary.get("idle_kv_within_threshold"),
            "prefix_hits_delta": summary.get("prefix_cache_hits_delta"),
            "prefix_queries_delta": summary.get("prefix_cache_queries_delta"),
        }
    ]


def _collect_prefill_decode_gate_rows(run_label: str, payload: Any) -> list[Json]:
    if not isinstance(payload, dict):
        return []
    thresholds = payload.get("thresholds")
    if not isinstance(thresholds, dict):
        thresholds = {}
    return [
        {
            "run": run_label,
            "variant": payload.get("variant"),
            "ok": payload.get("ok"),
            "regression_count": payload.get("regression_count"),
            "min_long_c2_decode_min_max_ratio": _round_float(
                thresholds.get("min_long_c2_decode_min_max_ratio")
            ),
            "max_long_c2_itl_p99_seconds": _round_float(
                thresholds.get("max_long_c2_itl_p99_seconds")
            ),
            "max_mixed_secondary_itl_p99_seconds": _round_float(
                thresholds.get("max_mixed_secondary_itl_p99_seconds")
            ),
            "max_streaming_itl_p99_seconds": _round_float(
                thresholds.get("max_streaming_itl_p99_seconds")
            ),
        }
    ]


def _artifact_dir(run_root: Path, raw_path: str | Path | None) -> Path | None:
    if not raw_path:
        return None
    artifact_dir = Path(raw_path)
    if not artifact_dir.is_absolute():
        artifact_dir = run_root / artifact_dir
    return artifact_dir


def _collect_monitoring_rows(run_label: str, run_root: Path) -> list[Json]:
    rows: list[Json] = []
    for phase in _phase_exit_codes(run_root):
        artifact_dir = _artifact_dir(run_root, phase.get("artifact_dir"))
        gpu_stats = _load_json(artifact_dir / "gpu_stats_summary.json") if artifact_dir else None
        runtime_stats = (
            _load_json(artifact_dir / "runtime_stats_summary.json") if artifact_dir else None
        )
        gpu_overall = (
            gpu_stats.get("overall", {})
            if isinstance(gpu_stats, dict) and isinstance(gpu_stats.get("overall"), dict)
            else {}
        )
        metrics = (
            runtime_stats.get("metrics", {})
            if isinstance(runtime_stats, dict)
            and isinstance(runtime_stats.get("metrics"), dict)
            else {}
        )
        serve_log = (
            runtime_stats.get("serve_log", {})
            if isinstance(runtime_stats, dict)
            and isinstance(runtime_stats.get("serve_log"), dict)
            else {}
        )
        server_unresponsive = False
        if artifact_dir and artifact_dir.exists():
            server_unresponsive = (artifact_dir / "server_unresponsive.txt").exists() or any(
                artifact_dir.glob("*.server_unresponsive")
            )

        rows.append(
            {
                "run": run_label,
                "variant": phase.get("variant"),
                "phase": phase.get("phase"),
                "exit_code": phase.get("exit_code"),
                "server_unresponsive": server_unresponsive,
                "gpu_samples": (
                    gpu_stats.get("sample_count") if isinstance(gpu_stats, dict) else None
                ),
                "gpu_utilization_avg": _round_float(
                    gpu_overall.get("gpu_utilization_percent_avg")
                ),
                "gpu_utilization_max": _round_float(
                    gpu_overall.get("gpu_utilization_percent_max")
                ),
                "gpu_memory_used_percent_max": _round_float(
                    gpu_overall.get("memory_used_percent_max")
                ),
                "gpu_temp_max_c": _round_float(gpu_overall.get("temperature_gpu_c_max")),
                "gpu_memory_temp_max_c": _round_float(
                    gpu_overall.get("temperature_memory_c_max")
                ),
                "gpu_power_max_w": _round_float(gpu_overall.get("power_draw_w_max")),
                "runtime_metric_samples": metrics.get("sample_count"),
                "runtime_running_requests_max": _round_float(
                    metrics.get("running_requests_max")
                ),
                "runtime_waiting_requests_max": _round_float(
                    metrics.get("waiting_requests_max")
                ),
                "runtime_kv_cache_usage_percent_max": _round_float(
                    metrics.get("gpu_kv_cache_usage_percent_max")
                ),
                "runtime_preemptions_delta": _round_float(metrics.get("preemptions_delta")),
                "runtime_prefill_tps_avg": _round_float(
                    metrics.get("prefill_throughput_tok_s_avg")
                    or serve_log.get("prefill_throughput_tok_s_avg")
                ),
                "runtime_decode_tps_avg": _round_float(
                    metrics.get("decode_throughput_tok_s_avg")
                    or serve_log.get("decode_throughput_tok_s_avg")
                ),
                "serve_log_error_signals": serve_log.get("error_signal_count"),
                "cuda_errors": serve_log.get("cuda_error_count"),
                "nccl_errors": serve_log.get("nccl_error_count"),
                "driver_errors": serve_log.get("driver_error_count"),
                "engine_errors": serve_log.get("engine_error_count"),
            }
        )
    return rows


def summarize_run(label: str, run_root: Path) -> Json:
    run_root = run_root.resolve()
    result: Json = {
        "label": label,
        "run_root": str(run_root),
        "phase_exit_codes": _phase_exit_codes(run_root),
        "latency": [],
        "decode_concurrency": [],
        "mixed_arrival": [],
        "streaming_pressure": [],
        "short_bench": [],
        "random_8000x1000_bench": [],
        "random_256x256_bench": [],
        "gsm8k": [],
        "prefill_sweep": [],
        "frontier_context_sweep": [],
        "story_recall_semantic": [],
        "prefix_cache_stress": [],
        "kv_lifecycle": [],
        "prefill_decode_gate": [],
        "monitoring": [],
    }
    for variant_dir in _variant_dirs(run_root):
        variant = variant_dir.name
        latency = _load_json(
            variant_dir / "long_context_latency_matrix" / "long_context_latency_matrix.json"
        )
        result["latency"].extend(
            _collect_latency_rows(label, variant, "long_context_latency_matrix", latency)
        )

        decode = _load_json(
            variant_dir
            / "long_context_decode_concurrency"
            / "long_context_decode_concurrency.json"
        )
        result["decode_concurrency"].extend(
            _collect_latency_rows(label, variant, "long_context_decode_concurrency", decode)
        )

        mixed = _load_json(
            variant_dir / "long_context_mixed_arrival" / "long_context_mixed_arrival.json"
        )
        result["mixed_arrival"].extend(_collect_mixed_rows(label, variant, mixed))

        streaming = _load_json(
            variant_dir / "streaming_pressure_matrix" / "streaming_pressure_matrix.json"
        )
        result["streaming_pressure"].extend(
            _collect_streaming_rows(label, variant, streaming)
        )

        bench = _load_json(variant_dir / "bench_hf_mt_bench" / "bench.json")
        result["short_bench"].extend(_collect_bench_rows(label, variant, bench))

        random_8k1k = _load_json(variant_dir / "bench_random_8000x1000" / "bench.json")
        result["random_8000x1000_bench"].extend(
            _collect_bench_rows(label, variant, random_8k1k)
        )

        random_256x256 = _load_json(variant_dir / "bench_random_256x256" / "bench.json")
        result["random_256x256_bench"].extend(
            _collect_bench_rows(label, variant, random_256x256)
        )

        gsm8k = _load_json(variant_dir / "eval_gsm8k" / "lm_eval_summary.json")
        result["gsm8k"].extend(_collect_gsm8k_rows(label, variant, gsm8k))

        prefill = _load_json(
            variant_dir / "bench_random_prefill_sweep" / "prefill_sweep_summary.json"
        )
        result["prefill_sweep"].extend(_collect_prefill_rows(label, variant, prefill))

        frontier = _load_json(
            variant_dir / "frontier_context_sweep" / "frontier_context_sweep.json"
        )
        result["frontier_context_sweep"].extend(
            _collect_frontier_rows(label, variant, frontier)
        )

        story = _load_json(
            variant_dir
            / "ds4_story_recall_semantic"
            / "long_context_latency_matrix.json"
        )
        result["story_recall_semantic"].extend(
            _collect_story_recall_rows(label, variant, story)
        )

        prefix = _load_json(variant_dir / "prefix_cache_stress" / "prefix_cache_stress.json")
        result["prefix_cache_stress"].extend(
            _collect_prefix_cache_rows(label, variant, prefix)
        )

        kv_lifecycle = _load_json(
            variant_dir / "kv_lifecycle_probe" / "kv_lifecycle_probe.json"
        )
        result["kv_lifecycle"].extend(
            _collect_kv_lifecycle_rows(label, variant, kv_lifecycle)
        )
    gate = _load_json(run_root / "prefill_decode_gate" / "prefill_decode_regression_gate.json")
    result["prefill_decode_gate"].extend(
        _collect_prefill_decode_gate_rows(label, gate)
    )
    result["prefix_cache_stress"].extend(
        _collect_prefix_cache_diagnostic_rows(label, run_root)
    )
    result["monitoring"].extend(_collect_monitoring_rows(label, run_root))
    phase_codes = [row["exit_code"] for row in result["phase_exit_codes"]]
    gate_rows = result["prefill_decode_gate"]
    gate_ok = all(row.get("ok") is True for row in gate_rows)
    result["ok"] = bool(phase_codes) and all(code == 0 for code in phase_codes) and gate_ok
    return result


def summarize_runs(runs: list[tuple[str, Path]]) -> Json:
    run_summaries = [summarize_run(label, path) for label, path in runs]
    return {
        "ok": all(run.get("ok") for run in run_summaries),
        "runs": run_summaries,
        "tradeoff_policy": {
            "primary": [
                "correctness and server stability must not regress",
                "serve, CUDA, NCCL, and driver error signals are first-class regressions",
                "C=1/C=2/C=4 latency and ITL are prioritized for edge deployment",
                "already-started decode stream fairness beats second cold-prefill TTFT",
            ],
            "secondary": [
                "large-concurrency throughput is tracked but does not dominate the tradeoff",
                "256K+ and four-card claims require external gates",
            ],
        },
    }


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, dict):
        return ", ".join(f"{key}:{val}" for key, val in value.items()) or "n/a"
    return str(value)


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    if not rows:
        return ["_No data._"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_fmt(value) for value in row) + " |")
    return lines


def write_summary_markdown(path: Path, summary: Json) -> None:
    lines = [
        "# SM120 User Feedback Matrix Summary",
        "",
        f"- OK: `{summary.get('ok')}`",
        "",
        "## Tradeoff Policy",
        "",
    ]
    for item in summary["tradeoff_policy"]["primary"]:
        lines.append(f"- Primary: {item}.")
    for item in summary["tradeoff_policy"]["secondary"]:
        lines.append(f"- Secondary: {item}.")
    lines.append("")

    phase_rows: list[list[Any]] = []
    latency_rows: list[list[Any]] = []
    decode_rows: list[list[Any]] = []
    mixed_rows: list[list[Any]] = []
    streaming_rows: list[list[Any]] = []
    bench_rows: list[list[Any]] = []
    random_8k1k_rows: list[list[Any]] = []
    random_256x256_rows: list[list[Any]] = []
    gsm_rows: list[list[Any]] = []
    prefill_rows: list[list[Any]] = []
    frontier_rows: list[list[Any]] = []
    story_rows: list[list[Any]] = []
    prefix_rows: list[list[Any]] = []
    kv_lifecycle_rows: list[list[Any]] = []
    prefill_decode_gate_rows: list[list[Any]] = []
    monitoring_rows: list[list[Any]] = []

    for run in summary["runs"]:
        for phase in run["phase_exit_codes"]:
            phase_rows.append(
                [run["label"], phase["variant"], phase["phase"], phase["exit_code"]]
            )
        for row in run["latency"]:
            latency_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["prompt"],
                    row["cache_mode"],
                    row["concurrency"],
                    row["failures"],
                    row["ttft_mean_s"],
                    row["ttft_max_s"],
                    row["decode_mean_tps"],
                    row["decode_min_max_ratio"],
                    row["itl_p99_s"],
                ]
            )
        for row in run["decode_concurrency"]:
            decode_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["prompt"],
                    row["cache_mode"],
                    row["concurrency"],
                    row["failures"],
                    row["ttft_mean_s"],
                    row["ttft_max_s"],
                    row["decode_mean_tps"],
                    row["decode_min_tps"],
                    row["decode_min_max_ratio"],
                    row["itl_p99_s"],
                ]
            )
        for row in run["mixed_arrival"]:
            mixed_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["case"],
                    row["failures"],
                    row["primary_ttft_mean_s"],
                    row["secondary_ttft_mean_s"],
                    row["decode_min_max_ratio"],
                    row["secondary_itl_p99_s"],
                ]
            )
        for row in run["streaming_pressure"]:
            streaming_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["requests"],
                    row["failures"],
                    row["slow_cases"],
                    row["max_ttft_s"],
                    row["itl_p99_s"],
                    row["itl_max_s"],
                ]
            )
        for row in run["short_bench"]:
            bench_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["concurrency"],
                    row["successful_requests"],
                    row["output_tps"],
                    row["ttft_p99_ms"],
                    row["itl_p99_ms"],
                    row["spec_acceptance_percent"],
                    row["spec_acceptance_length"],
                    row["spec_per_position_acceptance_percent"],
                ]
            )
        for row in run["random_8000x1000_bench"]:
            random_8k1k_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["concurrency"],
                    row["successful_requests"],
                    row["output_tps"],
                    row["ttft_mean_ms"],
                    row["ttft_p99_ms"],
                    row["itl_p99_ms"],
                    row["spec_acceptance_percent"],
                    row["spec_acceptance_length"],
                    row["spec_per_position_acceptance_percent"],
                ]
            )
        for row in run["random_256x256_bench"]:
            random_256x256_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["concurrency"],
                    row["successful_requests"],
                    row["output_tps"],
                    row["ttft_mean_ms"],
                    row["ttft_p99_ms"],
                    row["itl_p99_ms"],
                    row["spec_acceptance_percent"],
                    row["spec_acceptance_length"],
                    row["spec_per_position_acceptance_percent"],
                ]
            )
        for row in run["gsm8k"]:
            gsm_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["task"],
                    row["exact_match_flexible"],
                    row["exact_match_strict"],
                ]
            )
        for row in run["prefill_sweep"]:
            prefill_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["case"],
                    row["ok"],
                    row["input_tps"],
                    row["ttft_mean_ms"],
                    row["ttft_p99_ms"],
                ]
            )
        for row in run["frontier_context_sweep"]:
            frontier_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["prompt"],
                    row["target_frontier_tokens"],
                    row["failures"],
                    row["prompt_tokens"],
                    row["ttft_mean_s"],
                    row["ttft_max_s"],
                    row["input_tps"],
                    row["decode_mean_tps"],
                    row["itl_p99_s"],
                ]
            )
        for row in run["story_recall_semantic"]:
            story_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["prompt"],
                    row["concurrency"],
                    row["failures"],
                    row["matched_min"],
                    row["missing"],
                    row["finish_reasons"],
                    row["prompt_tokens"],
                    row["ttft_mean_s"],
                    row["decode_mean_tps"],
                    row["itl_p99_s"],
                ]
            )
        for row in run["prefix_cache_stress"]:
            prefix_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["case"],
                    row["filler_words"],
                    row["ok"],
                    row["health_status"],
                    row["trials"],
                    row["failures"],
                    row["solo_hit_rate_mean"],
                    row["concurrent_hit_rate_mean"],
                ]
            )
        for row in run["kv_lifecycle"]:
            kv_lifecycle_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["case"],
                    row["cache_mode"],
                    row["ok"],
                    row["requests"],
                    row["failures"],
                    row["idle_failures"],
                    row["initial_idle_kv_percent"],
                    row["final_idle_kv_percent"],
                    row["max_idle_kv_percent"],
                    row["threshold_percent"],
                    row["idle_kv_within_threshold"],
                    row["prefix_hits_delta"],
                    row["prefix_queries_delta"],
                ]
            )
        for row in run["prefill_decode_gate"]:
            prefill_decode_gate_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["ok"],
                    row["regression_count"],
                    row["min_long_c2_decode_min_max_ratio"],
                    row["max_long_c2_itl_p99_seconds"],
                    row["max_mixed_secondary_itl_p99_seconds"],
                    row["max_streaming_itl_p99_seconds"],
                ]
            )
        for row in run["monitoring"]:
            monitoring_rows.append(
                [
                    row["run"],
                    row["variant"],
                    row["phase"],
                    row["exit_code"],
                    row["server_unresponsive"],
                    row["gpu_samples"],
                    row["gpu_utilization_avg"],
                    row["gpu_memory_used_percent_max"],
                    row["gpu_temp_max_c"],
                    row["runtime_metric_samples"],
                    row["runtime_running_requests_max"],
                    row["runtime_waiting_requests_max"],
                    row["runtime_kv_cache_usage_percent_max"],
                    row["runtime_preemptions_delta"],
                    row["serve_log_error_signals"],
                    row["cuda_errors"],
                    row["nccl_errors"],
                    row["driver_errors"],
                    row["engine_errors"],
                ]
            )

    sections = [
        ("Phase Exit Codes", ["Run", "Variant", "Phase", "Exit"], phase_rows),
        (
            "Long-Context Latency",
            [
                "Run",
                "Variant",
                "Prompt",
                "Cache",
                "C",
                "Failures",
                "TTFT Mean s",
                "TTFT Max s",
                "Decode tok/s",
                "Decode Min/Max",
                "ITL P99 s",
            ],
            latency_rows,
        ),
        (
            "Decode-Concurrency",
            [
                "Run",
                "Variant",
                "Prompt",
                "Cache",
                "C",
                "Failures",
                "TTFT Mean s",
                "TTFT Max s",
                "Decode tok/s",
                "Decode Min tok/s",
                "Decode Min/Max",
                "ITL P99 s",
            ],
            decode_rows,
        ),
        (
            "Mixed Arrival",
            [
                "Run",
                "Variant",
                "Case",
                "Failures",
                "Primary TTFT s",
                "Secondary TTFT s",
                "Decode Min/Max",
                "Secondary ITL P99 s",
            ],
            mixed_rows,
        ),
        (
            "Streaming Pressure",
            [
                "Run",
                "Variant",
                "Requests",
                "Failures",
                "Slow Cases",
                "Max TTFT s",
                "ITL P99 s",
                "ITL Max s",
            ],
            streaming_rows,
        ),
        (
            "Short Bench",
            [
                "Run",
                "Variant",
                "C",
                "Successful",
                "Output tok/s",
                "TTFT P99 ms",
                "ITL P99 ms",
                "Spec Accept %",
                "Spec Accept Len",
                "Spec Accept Pos %",
            ],
            bench_rows,
        ),
        (
            "Random 8000/1000 Bench",
            [
                "Run",
                "Variant",
                "C",
                "Successful",
                "Output tok/s",
                "TTFT Mean ms",
                "TTFT P99 ms",
                "ITL P99 ms",
                "Spec Accept %",
                "Spec Accept Len",
                "Spec Accept Pos %",
            ],
            random_8k1k_rows,
        ),
        (
            "Random 256/256 Bench",
            [
                "Run",
                "Variant",
                "C",
                "Successful",
                "Output tok/s",
                "TTFT Mean ms",
                "TTFT P99 ms",
                "ITL P99 ms",
                "Spec Accept %",
                "Spec Accept Len",
                "Spec Accept Pos %",
            ],
            random_256x256_rows,
        ),
        (
            "GSM8K",
            ["Run", "Variant", "Task", "Flexible EM", "Strict EM"],
            gsm_rows,
        ),
        (
            "Random Prefill Sweep",
            ["Run", "Variant", "Case", "OK", "Input tok/s", "TTFT Mean ms", "TTFT P99 ms"],
            prefill_rows,
        ),
        (
            "Frontier Context Sweep",
            [
                "Run",
                "Variant",
                "Prompt",
                "Target Frontier",
                "Failures",
                "Prompt Tokens",
                "TTFT Mean s",
                "TTFT Max s",
                "Input tok/s",
                "Decode tok/s",
                "ITL P99 s",
            ],
            frontier_rows,
        ),
        (
            "DS4 Story Recall Semantic",
            [
                "Run",
                "Variant",
                "Prompt",
                "C",
                "Failures",
                "Matched Min",
                "Missing",
                "Finish",
                "Prompt Tokens",
                "TTFT Mean s",
                "Decode tok/s",
                "ITL P99 s",
            ],
            story_rows,
        ),
        (
            "Prefix Cache Stress",
            [
                "Run",
                "Variant",
                "Case",
                "Filler Words",
                "OK",
                "Health",
                "Trials",
                "Failures",
                "Solo Hit Rate",
                "Concurrent Hit Rate",
            ],
            prefix_rows,
        ),
        (
            "KV Lifecycle",
            [
                "Run",
                "Variant",
                "Case",
                "Cache",
                "OK",
                "Requests",
                "Failures",
                "Idle Failures",
                "Initial KV %",
                "Final KV %",
                "Max Idle KV %",
                "Threshold %",
                "Within Threshold",
                "Prefix Hits Delta",
                "Prefix Queries Delta",
            ],
            kv_lifecycle_rows,
        ),
        (
            "Prefill/Decode Gate",
            [
                "Run",
                "Variant",
                "OK",
                "Regression Count",
                "Min Long C2 Decode Min/Max",
                "Max Long C2 ITL P99 s",
                "Max Mixed Secondary ITL P99 s",
                "Max Streaming ITL P99 s",
            ],
            prefill_decode_gate_rows,
        ),
        (
            "Runtime Monitoring",
            [
                "Run",
                "Variant",
                "Phase",
                "Exit",
                "Server Unresponsive",
                "GPU Samples",
                "GPU Util Avg",
                "GPU Mem Max %",
                "GPU Temp Max C",
                "Runtime Samples",
                "Running Max",
                "Waiting Max",
                "KV Cache Max %",
                "Preemptions",
                "Serve Error Signals",
                "CUDA Errors",
                "NCCL Errors",
                "Driver Errors",
                "Engine Errors",
            ],
            monitoring_rows,
        ),
    ]
    for title, headers, rows in sections:
        lines.extend(["", f"## {title}", ""])
        lines.extend(_markdown_table(headers, rows))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_run(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--run must use label=path")
    label, raw_path = value.split("=", 1)
    label = label.strip()
    if not label:
        raise argparse.ArgumentTypeError("run label must not be empty")
    return label, Path(raw_path).expanduser()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", type=_parse_run, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args(argv)

    summary = summarize_runs(args.run)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_summary_markdown(args.markdown_output, summary)
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
