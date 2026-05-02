#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON="${PYTHON:-python3}"

source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

BASELINE_RUN_DIR="${BASELINE_RUN_DIR:?set BASELINE_RUN_DIR}"
BASELINE_REPORT_TITLE="${BASELINE_REPORT_TITLE:-DeepSeek V4 Baseline Report}"
BASELINE_REPORT_LABEL="${BASELINE_REPORT_LABEL:-}"
BASELINE_DATE="${BASELINE_DATE:-}"
BASELINE_REQUIRE_GENERATION="${BASELINE_REQUIRE_GENERATION:-1}"
BASELINE_EXPECT_VARIANTS="${BASELINE_EXPECT_VARIANTS:-nomtp,mtp}"
BASELINE_EXPECT_LANGUAGES="${BASELINE_EXPECT_LANGUAGES:-en,zh}"
BASELINE_EXPECT_THINKING_MODES="${BASELINE_EXPECT_THINKING_MODES:-non-thinking,think-high,think-max}"
BASELINE_EXPECT_GENERATION_REPEAT_COUNT="${BASELINE_EXPECT_GENERATION_REPEAT_COUNT:-3}"
BASELINE_EXPECT_GENERATION_CASES_PER_VARIANT="${BASELINE_EXPECT_GENERATION_CASES_PER_VARIANT:-}"
BASELINE_EXPECT_TEMPERATURE="${BASELINE_EXPECT_TEMPERATURE:-1.0}"
BASELINE_EXPECT_TOP_P="${BASELINE_EXPECT_TOP_P:-1.0}"
export BASELINE_REQUIRE_GENERATION BASELINE_EXPECT_VARIANTS BASELINE_EXPECT_LANGUAGES
export BASELINE_EXPECT_THINKING_MODES BASELINE_EXPECT_GENERATION_REPEAT_COUNT
export BASELINE_EXPECT_GENERATION_CASES_PER_VARIANT
export BASELINE_EXPECT_TEMPERATURE BASELINE_EXPECT_TOP_P

if [[ -z "${BASELINE_DATE}" ]]; then
  run_basename="$(basename "${BASELINE_RUN_DIR}")"
  if [[ "${run_basename}" =~ ^([0-9]{8}) ]]; then
    BASELINE_DATE="${BASH_REMATCH[1]}"
  else
    BASELINE_DATE="$(date -u +%Y%m%d)"
  fi
fi

if [[ -z "${BASELINE_REPORT_LABEL}" ]]; then
  BASELINE_REPORT_LABEL="$(basename "$(dirname "${BASELINE_RUN_DIR}")")"
fi

BASELINE_BUNDLE_LABEL="${BASELINE_BUNDLE_LABEL:-$(slugify_context_value "${BASELINE_REPORT_LABEL}")}"
BASELINE_OUTPUT_DIR="${BASELINE_OUTPUT_DIR:-${REPO_ROOT}/baselines/${BASELINE_DATE}_${BASELINE_BUNDLE_LABEL}}"
BASELINE_BUNDLE_NAME="$(basename "${BASELINE_OUTPUT_DIR}")"

output_parent="$(dirname "${BASELINE_OUTPUT_DIR}")"
output_name="$(basename "${BASELINE_OUTPUT_DIR}")"
mkdir -p "${output_parent}"
tmp_dir="$(mktemp -d "${output_parent}/.${output_name}.tmp.XXXXXX")"
cleanup() {
  rm -rf "${tmp_dir}"
}
trap cleanup EXIT

reference_args=(
  reference-bundle
  --run-dir "${BASELINE_RUN_DIR}"
  --output-dir "${tmp_dir}"
  --label "${BASELINE_BUNDLE_NAME}"
  --date "${BASELINE_DATE}"
)

report_args=(
  baseline-report
  --run-dir "${BASELINE_RUN_DIR}"
  --title "${BASELINE_REPORT_TITLE}"
  --label "${BASELINE_REPORT_LABEL}"
  --output "${tmp_dir}/report.md"
)

cd "${REPO_ROOT}"
"${PYTHON}" -m ds4_harness.cli "${reference_args[@]}" >/dev/null
"${PYTHON}" -m ds4_harness.cli "${report_args[@]}" >/dev/null

"${PYTHON}" - "${tmp_dir}" <<'PY'
from pathlib import Path
import json
import math
import os
import sys

from ds4_harness.oracle import load_oracle_cases
from ds4_harness.reference_bundle import scan_public_bundle

root = Path(sys.argv[1])


def _csv(name):
    return [item.strip() for item in os.environ.get(name, "").split(",") if item.strip()]


def _float_env(name):
    try:
        return float(os.environ[name])
    except (KeyError, ValueError):
        return None


def _int_env(name):
    value = os.environ.get(name)
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _expect_float(row, key, expected, errors):
    if expected is None:
        return
    try:
        actual = float(row.get(key))
    except (TypeError, ValueError):
        errors.append(f"generation row {row.get('case')} has invalid {key}: {row.get(key)!r}")
        return
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-9):
        errors.append(
            f"generation row {row.get('case')} has {key}={actual}, expected {expected}"
        )


def _validate_generation_matrix():
    if os.environ.get("BASELINE_REQUIRE_GENERATION", "1") not in {"1", "true"}:
        return []

    expected_variants = _csv("BASELINE_EXPECT_VARIANTS")
    expected_languages = set(_csv("BASELINE_EXPECT_LANGUAGES"))
    expected_modes = set(_csv("BASELINE_EXPECT_THINKING_MODES"))
    try:
        repeat_count = int(os.environ.get("BASELINE_EXPECT_GENERATION_REPEAT_COUNT", "3"))
    except ValueError:
        repeat_count = 3
    expected_rounds = set(range(1, repeat_count + 1))
    expected_case_count = _int_env("BASELINE_EXPECT_GENERATION_CASES_PER_VARIANT")
    expected_temperature = _float_env("BASELINE_EXPECT_TEMPERATURE")
    expected_top_p = _float_env("BASELINE_EXPECT_TOP_P")

    errors = []
    for variant in expected_variants:
        path = root / "generation" / f"{variant}.json"
        if not path.exists():
            errors.append(f"missing generation JSON for variant {variant}: {path.relative_to(root)}")
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list) or not rows:
            errors.append(f"empty generation JSON for variant {variant}: {path.relative_to(root)}")
            continue

        languages = {str(row.get("language")) for row in rows if row.get("language")}
        missing_languages = expected_languages - languages
        if missing_languages:
            errors.append(
                f"generation {variant} missing languages: {', '.join(sorted(missing_languages))}"
            )

        cases = {}
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                errors.append(f"generation {variant} contains a non-object row")
                continue
            case = str(row.get("case") or "")
            language = str(row.get("language") or "")
            mode = str(row.get("thinking_mode") or "")
            row_variant = str(row.get("variant") or "")
            round_index = row.get("round")
            try:
                round_index = int(round_index)
            except (TypeError, ValueError):
                errors.append(f"generation row {case or '<unknown>'} has invalid round")
                continue
            if row_variant != variant:
                errors.append(
                    f"generation row {case or '<unknown>'} has variant={row_variant}, expected {variant}"
                )
            _expect_float(row, "temperature", expected_temperature, errors)
            _expect_float(row, "top_p", expected_top_p, errors)
            key = (language, case, mode, round_index)
            if key in seen:
                errors.append(f"duplicate generation row for {variant}: {key}")
            seen.add(key)
            cases.setdefault((language, case), {}).setdefault(mode, set()).add(round_index)
            transcript = root / "generation" / language / f"{case}.{round_index}.{mode}.{variant}.md"
            if not transcript.exists():
                errors.append(
                    f"missing generation transcript for {variant}: {transcript.relative_to(root)}"
                )

        if expected_case_count is not None:
            expected_rows = expected_case_count * len(expected_modes) * repeat_count
            if len(cases) != expected_case_count:
                errors.append(
                    f"generation {variant} has {len(cases)} cases, expected {expected_case_count}"
                )
            if len(rows) != expected_rows:
                errors.append(
                    f"generation {variant} has {len(rows)} rows, expected {expected_rows}"
                )
            transcript_count = len(list((root / "generation").glob(f"*/*.{variant}.md")))
            if transcript_count != expected_rows:
                errors.append(
                    f"generation {variant} has {transcript_count} transcripts, expected {expected_rows}"
                )

        for (language, case), by_mode in sorted(cases.items()):
            if expected_languages and language not in expected_languages:
                continue
            missing_modes = expected_modes - set(by_mode)
            if missing_modes:
                errors.append(
                    f"generation {variant}/{language}/{case} missing thinking modes: "
                    + ", ".join(sorted(missing_modes))
                )
            for mode in expected_modes:
                if mode not in by_mode:
                    continue
                missing_rounds = expected_rounds - by_mode[mode]
                if missing_rounds:
                    errors.append(
                        f"generation {variant}/{language}/{case}/{mode} missing rounds: "
                        + ", ".join(str(round_id) for round_id in sorted(missing_rounds))
                    )
    return errors


findings = scan_public_bundle(root)
if findings:
    raise SystemExit("baseline bundle contains non-public data:\n" + "\n".join(findings))

cases = load_oracle_cases(root / "oracle")
if not cases:
    raise SystemExit("baseline bundle has no oracle cases")

report = root / "report.md"
if not report.exists() or report.stat().st_size == 0:
    raise SystemExit("baseline bundle report.md was not generated")

generation_errors = _validate_generation_matrix()
if generation_errors:
    raise SystemExit(
        "baseline bundle generation matrix is incomplete:\n"
        + "\n".join(generation_errors)
    )
PY

rm -rf "${BASELINE_OUTPUT_DIR}"
mv "${tmp_dir}" "${BASELINE_OUTPUT_DIR}"
trap - EXIT
printf '%s\n' "${BASELINE_OUTPUT_DIR}"
