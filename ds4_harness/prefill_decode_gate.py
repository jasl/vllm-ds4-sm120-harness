"""Promotion checks for SM12x prefill/decode interference artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Json = dict[str, Any]

REQUIRED_PHASES = (
    "long_context_latency_matrix",
    "long_context_decode_concurrency",
    "long_context_mixed_arrival",
    "streaming_pressure_matrix",
)


@dataclass(frozen=True)
class PrefillDecodeGateThresholds:
    min_long_c2_decode_min_max_ratio: float = 0.2
    max_long_c2_itl_p99_seconds: float = 1.0
    max_mixed_secondary_itl_p99_seconds: float = 1.0
    max_streaming_itl_p99_seconds: float = 2.0


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _as_int(value: Any) -> int | None:
    number = _as_float(value)
    if number is None:
        return None
    return int(number)


def _phase_artifact_dir(baseline_dir: Path, variant: str, phase: str) -> Path:
    return baseline_dir / variant / phase


def _phase_json_path(baseline_dir: Path, variant: str, phase: str) -> Path:
    filenames = {
        "long_context_latency_matrix": "long_context_latency_matrix.json",
        "long_context_decode_concurrency": "long_context_decode_concurrency.json",
        "long_context_mixed_arrival": "long_context_mixed_arrival.json",
        "streaming_pressure_matrix": "streaming_pressure_matrix.json",
    }
    return _phase_artifact_dir(baseline_dir, variant, phase) / filenames[phase]


def _phase_exit_codes(path: Path) -> dict[tuple[str, str], int]:
    if not path.exists():
        return {}
    rows: dict[tuple[str, str], int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("variant\tphase"):
            continue
        columns = line.split("\t")
        if len(columns) < 3:
            continue
        try:
            rows[(columns[0], columns[1])] = int(columns[2])
        except ValueError:
            continue
    return rows


def _append_regression(
    regressions: list[Json],
    checks: list[Json],
    *,
    phase: str,
    subject: str,
    reason: str,
    metric: str,
    value: float | int | None,
    threshold: float,
    comparator: str,
) -> None:
    row = {
        "phase": phase,
        "subject": subject,
        "reason": reason,
        "metric": metric,
        "value": value,
        "threshold": threshold,
        "comparator": comparator,
        "ok": False,
    }
    regressions.append(row)
    checks.append(row)


def _append_ok(
    checks: list[Json],
    *,
    phase: str,
    subject: str,
    metric: str,
    value: float | int | None,
    threshold: float,
    comparator: str,
) -> None:
    checks.append(
        {
            "phase": phase,
            "subject": subject,
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "comparator": comparator,
            "ok": True,
        }
    )


def _check_failure_count(
    *,
    checks: list[Json],
    regressions: list[Json],
    phase: str,
    subject: str,
    failure_count: Any,
) -> None:
    value = _as_int(failure_count)
    if value is None or value > 0:
        _append_regression(
            regressions,
            checks,
            phase=phase,
            subject=subject,
            reason="request-failures",
            metric="failure_count",
            value=value,
            threshold=0,
            comparator="<=",
        )
    else:
        _append_ok(
            checks,
            phase=phase,
            subject=subject,
            metric="failure_count",
            value=value,
            threshold=0,
            comparator="<=",
        )


def _check_long_c2_rows(
    *,
    payload: Json,
    phase: str,
    checks: list[Json],
    regressions: list[Json],
    thresholds: PrefillDecodeGateThresholds,
) -> None:
    found_c2_row = False
    for row in payload.get("summary", []):
        if not isinstance(row, dict) or _as_int(row.get("concurrency")) != 2:
            continue
        found_c2_row = True
        subject = "|".join(
            str(part)
            for part in (
                row.get("prompt", "unknown"),
                row.get("cache_mode", "unknown"),
                "C=2",
            )
        )
        _check_failure_count(
            checks=checks,
            regressions=regressions,
            phase=phase,
            subject=subject,
            failure_count=row.get("failure_count"),
        )
        ratio = _as_float(row.get("decode_tps_min_to_max_ratio"))
        if ratio is None or ratio < thresholds.min_long_c2_decode_min_max_ratio:
            _append_regression(
                regressions,
                checks,
                phase=phase,
                subject=subject,
                reason="long-c2-decode-min-max-ratio-below-floor",
                metric="decode_tps_min_to_max_ratio",
                value=ratio,
                threshold=thresholds.min_long_c2_decode_min_max_ratio,
                comparator=">=",
            )
        else:
            _append_ok(
                checks,
                phase=phase,
                subject=subject,
                metric="decode_tps_min_to_max_ratio",
                value=ratio,
                threshold=thresholds.min_long_c2_decode_min_max_ratio,
                comparator=">=",
            )
        itl_p99 = _as_float(row.get("p99_inter_chunk_seconds"))
        if itl_p99 is None or itl_p99 > thresholds.max_long_c2_itl_p99_seconds:
            _append_regression(
                regressions,
                checks,
                phase=phase,
                subject=subject,
                reason="long-c2-itl-p99-above-ceiling",
                metric="p99_inter_chunk_seconds",
                value=itl_p99,
                threshold=thresholds.max_long_c2_itl_p99_seconds,
                comparator="<=",
            )
        else:
            _append_ok(
                checks,
                phase=phase,
                subject=subject,
                metric="p99_inter_chunk_seconds",
                value=itl_p99,
                threshold=thresholds.max_long_c2_itl_p99_seconds,
                comparator="<=",
            )
    if not found_c2_row:
        _append_regression(
            regressions,
            checks,
            phase=phase,
            subject="summary",
            reason="long-c2-summary-missing",
            metric="concurrency",
            value=None,
            threshold=2,
            comparator="contains",
        )


def _check_mixed_arrival(
    *,
    payload: Json,
    checks: list[Json],
    regressions: list[Json],
    thresholds: PrefillDecodeGateThresholds,
) -> None:
    phase = "long_context_mixed_arrival"
    summary = payload.get("summary")
    if not isinstance(summary, list):
        _append_regression(
            regressions,
            checks,
            phase=phase,
            subject="summary",
            reason="missing-summary",
            metric="summary",
            value=None,
            threshold=1,
            comparator="present",
        )
        return
    if not summary:
        _append_regression(
            regressions,
            checks,
            phase=phase,
            subject="summary",
            reason="mixed-summary-empty",
            metric="summary_rows",
            value=0,
            threshold=1,
            comparator=">=",
        )
        return
    for row in summary:
        if not isinstance(row, dict):
            continue
        subject = str(row.get("case", "unknown"))
        _check_failure_count(
            checks=checks,
            regressions=regressions,
            phase=phase,
            subject=subject,
            failure_count=row.get("failure_count"),
        )
        itl_p99 = _as_float(row.get("secondary_p99_inter_chunk_seconds"))
        if itl_p99 is None or itl_p99 > thresholds.max_mixed_secondary_itl_p99_seconds:
            _append_regression(
                regressions,
                checks,
                phase=phase,
                subject=subject,
                reason="mixed-secondary-itl-p99-above-ceiling",
                metric="secondary_p99_inter_chunk_seconds",
                value=itl_p99,
                threshold=thresholds.max_mixed_secondary_itl_p99_seconds,
                comparator="<=",
            )
        else:
            _append_ok(
                checks,
                phase=phase,
                subject=subject,
                metric="secondary_p99_inter_chunk_seconds",
                value=itl_p99,
                threshold=thresholds.max_mixed_secondary_itl_p99_seconds,
                comparator="<=",
            )


def _check_streaming_pressure(
    *,
    payload: Json,
    checks: list[Json],
    regressions: list[Json],
    thresholds: PrefillDecodeGateThresholds,
) -> None:
    phase = "streaming_pressure_matrix"
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        _append_regression(
            regressions,
            checks,
            phase=phase,
            subject="summary",
            reason="missing-summary",
            metric="summary",
            value=None,
            threshold=1,
            comparator="present",
        )
        return
    _check_failure_count(
        checks=checks,
        regressions=regressions,
        phase=phase,
        subject="summary",
        failure_count=summary.get("failure_count"),
    )
    case_count = _as_int(summary.get("case_count"))
    if case_count is None or case_count < 1:
        _append_regression(
            regressions,
            checks,
            phase=phase,
            subject="summary",
            reason="streaming-cases-missing",
            metric="case_count",
            value=case_count,
            threshold=1,
            comparator=">=",
        )
    else:
        _append_ok(
            checks,
            phase=phase,
            subject="summary",
            metric="case_count",
            value=case_count,
            threshold=1,
            comparator=">=",
        )
    request_count = _as_int(summary.get("request_count"))
    if request_count is None or request_count < 1:
        _append_regression(
            regressions,
            checks,
            phase=phase,
            subject="summary",
            reason="streaming-requests-missing",
            metric="request_count",
            value=request_count,
            threshold=1,
            comparator=">=",
        )
    else:
        _append_ok(
            checks,
            phase=phase,
            subject="summary",
            metric="request_count",
            value=request_count,
            threshold=1,
            comparator=">=",
        )
    slow_cases = _as_int(summary.get("slow_case_count"))
    if slow_cases is None or slow_cases > 0:
        _append_regression(
            regressions,
            checks,
            phase=phase,
            subject="summary",
            reason="streaming-slow-cases",
            metric="slow_case_count",
            value=slow_cases,
            threshold=0,
            comparator="<=",
        )
    else:
        _append_ok(
            checks,
            phase=phase,
            subject="summary",
            metric="slow_case_count",
            value=slow_cases,
            threshold=0,
            comparator="<=",
        )
    itl_p99 = _as_float(summary.get("p99_inter_chunk_seconds"))
    if itl_p99 is None or itl_p99 > thresholds.max_streaming_itl_p99_seconds:
        _append_regression(
            regressions,
            checks,
            phase=phase,
            subject="summary",
            reason="streaming-itl-p99-above-ceiling",
            metric="p99_inter_chunk_seconds",
            value=itl_p99,
            threshold=thresholds.max_streaming_itl_p99_seconds,
            comparator="<=",
        )
    else:
        _append_ok(
            checks,
            phase=phase,
            subject="summary",
            metric="p99_inter_chunk_seconds",
            value=itl_p99,
            threshold=thresholds.max_streaming_itl_p99_seconds,
            comparator="<=",
        )


def evaluate_prefill_decode_gate(
    *,
    baseline_dir: Path,
    variant: str,
    thresholds: PrefillDecodeGateThresholds | None = None,
    required_phases: tuple[str, ...] = REQUIRED_PHASES,
) -> Json:
    thresholds = thresholds or PrefillDecodeGateThresholds()
    checks: list[Json] = []
    regressions: list[Json] = []
    phase_exit_codes = _phase_exit_codes(baseline_dir / "phase_exit_codes.tsv")

    for phase in required_phases:
        exit_code = phase_exit_codes.get((variant, phase))
        if exit_code != 0:
            _append_regression(
                regressions,
                checks,
                phase=phase,
                subject="phase_exit",
                reason="phase-not-run-or-failed",
                metric="exit_code",
                value=exit_code,
                threshold=0,
                comparator="==",
            )
            continue
        _append_ok(
            checks,
            phase=phase,
            subject="phase_exit",
            metric="exit_code",
            value=exit_code,
            threshold=0,
            comparator="==",
        )

        json_path = _phase_json_path(baseline_dir, variant, phase)
        if not json_path.exists():
            _append_regression(
                regressions,
                checks,
                phase=phase,
                subject="artifact",
                reason="missing-json-artifact",
                metric="json_path",
                value=None,
                threshold=1,
                comparator="present",
            )
            continue
        payload = _read_json(json_path)
        if not isinstance(payload, dict):
            _append_regression(
                regressions,
                checks,
                phase=phase,
                subject="artifact",
                reason="json-artifact-not-object",
                metric="json_type",
                value=None,
                threshold=1,
                comparator="object",
            )
            continue
        if payload.get("ok") is False:
            _append_regression(
                regressions,
                checks,
                phase=phase,
                subject="artifact",
                reason="artifact-ok-false",
                metric="ok",
                value=0,
                threshold=1,
                comparator="==",
            )

        if phase in ("long_context_latency_matrix", "long_context_decode_concurrency"):
            _check_long_c2_rows(
                payload=payload,
                phase=phase,
                checks=checks,
                regressions=regressions,
                thresholds=thresholds,
            )
        elif phase == "long_context_mixed_arrival":
            _check_mixed_arrival(
                payload=payload,
                checks=checks,
                regressions=regressions,
                thresholds=thresholds,
            )
        elif phase == "streaming_pressure_matrix":
            _check_streaming_pressure(
                payload=payload,
                checks=checks,
                regressions=regressions,
                thresholds=thresholds,
            )

    return {
        "ok": not regressions,
        "baseline_dir": str(baseline_dir),
        "variant": variant,
        "thresholds": thresholds.__dict__,
        "checks": checks,
        "regressions": regressions,
        "regression_count": len(regressions),
    }


def write_prefill_decode_gate_markdown(path: Path, gate: Json) -> None:
    lines = [
        "# SM12x Prefill/Decode Regression Gate",
        "",
        f"- OK: `{gate.get('ok')}`",
        f"- Variant: `{gate.get('variant')}`",
        f"- Baseline dir: `{gate.get('baseline_dir')}`",
        f"- Regression count: `{gate.get('regression_count')}`",
        "",
        "## Thresholds",
        "",
        "| Metric | Threshold |",
        "| --- | ---: |",
    ]
    thresholds = gate.get("thresholds") if isinstance(gate.get("thresholds"), dict) else {}
    for key, value in sorted(thresholds.items()):
        lines.append(f"| `{key}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Regressions",
            "",
            "| Phase | Subject | Reason | Metric | Value | Comparator | Threshold |",
            "| --- | --- | --- | --- | ---: | --- | ---: |",
        ]
    )
    regressions = gate.get("regressions")
    if isinstance(regressions, list) and regressions:
        for row in regressions:
            if not isinstance(row, dict):
                continue
            lines.append(
                "| {phase} | {subject} | {reason} | {metric} | {value} | {comp} | {threshold} |".format(
                    phase=row.get("phase"),
                    subject=row.get("subject"),
                    reason=row.get("reason"),
                    metric=row.get("metric"),
                    value=row.get("value"),
                    comp=row.get("comparator"),
                    threshold=row.get("threshold"),
                )
            )
    else:
        lines.append("| none | none | none | none |  |  |  |")

    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| OK | Phase | Subject | Metric | Value | Comparator | Threshold |",
            "| --- | --- | --- | --- | ---: | --- | ---: |",
        ]
    )
    for row in gate.get("checks", []):
        if not isinstance(row, dict):
            continue
        lines.append(
            "| {ok} | {phase} | {subject} | {metric} | {value} | {comp} | {threshold} |".format(
                ok="yes" if row.get("ok") else "no",
                phase=row.get("phase"),
                subject=row.get("subject"),
                metric=row.get("metric"),
                value=row.get("value"),
                comp=row.get("comparator"),
                threshold=row.get("threshold"),
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
