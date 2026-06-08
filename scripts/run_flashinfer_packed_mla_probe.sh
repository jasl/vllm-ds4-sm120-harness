#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date -u +%Y%m%d%H%M%S)}"
BRANCH_SLUG="${BRANCH_SLUG:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/ ' '__')}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-unknown_topology}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/flashinfer_packed_mla_probe/${RUN_TIMESTAMP}}"
PYTHON="${PYTHON:-python3}"
CASES="${CASES:-c4a_prefill c128a_prefill}"
LAYOUT_VARIANTS="${LAYOUT_VARIANTS:-0}"

# The known Aiden wheelhouse route pairs flashinfer-python 0.6.12 with
# flashinfer-cubin 0.6.11.post3. This probe is intentionally route-level, so
# allow that mismatch unless the caller explicitly overrides the env.
export FLASHINFER_DISABLE_VERSION_CHECK="${FLASHINFER_DISABLE_VERSION_CHECK:-1}"

mkdir -p "${OUT_DIR}"

overall=0
for case_name in ${CASES}; do
  case_json="${OUT_DIR}/flashinfer_packed_mla_${case_name}.json"
  case_md="${OUT_DIR}/flashinfer_packed_mla_${case_name}.md"
  case_args=()
  if [[ "${LAYOUT_VARIANTS}" == "1" ]]; then
    case_args+=(--layout-variants)
  fi
  if "${PYTHON}" -m ds4_harness.flashinfer_packed_mla_probe \
    --case "${case_name}" \
    --json-output "${case_json}" \
    --markdown-output "${case_md}" \
    "${case_args[@]}"; then
    printf '%s\n' 0 > "${OUT_DIR}/flashinfer_packed_mla_${case_name}.exit_code"
  else
    code=$?
    printf '%s\n' "${code}" > "${OUT_DIR}/flashinfer_packed_mla_${case_name}.exit_code"
    overall=1
  fi
done

"${PYTHON}" - "${OUT_DIR}" "${CASES}" <<'PY'
import json
import sys
from pathlib import Path

out_dir = Path(sys.argv[1])
cases = sys.argv[2].split()
rows = []
for case_name in cases:
    path = out_dir / f"flashinfer_packed_mla_{case_name}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"ok": False, "case": case_name, "error": {"type": "MissingResult"}}
    rows.append(data)

summary = {
    "ok": all(bool(row.get("ok")) for row in rows),
    "case_count": len(rows),
    "cases": [
        {
            "case": row.get("case"),
            "ok": row.get("ok"),
            "error": row.get("error"),
            "run": row.get("run"),
            "indices": row.get("indices"),
            "layout_variants": row.get("layout_variants", []),
        }
        for row in rows
    ],
}
(out_dir / "flashinfer_packed_mla_probe_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
lines = ["# FlashInfer Packed MLA Probe Summary", ""]
lines.append(f"- OK: `{summary['ok']}`")
lines.append(f"- Cases: `{summary['case_count']}`")
lines.append("")
lines.append("| Case | OK | LSE max error | Output absmax | Error |")
lines.append("| --- | --- | ---: | ---: | --- |")
for row in rows:
    run = row.get("run") or {}
    error = row.get("error") or {}
    lines.append(
        "| `{case}` | `{ok}` | `{lse}` | `{out}` | `{err}` |".format(
            case=row.get("case"),
            ok=row.get("ok"),
            lse=run.get("lse_error_max", "n/a"),
            out=run.get("output_absmax", "n/a"),
            err=error.get("type", ""),
        )
    )
    layout_variants = row.get("layout_variants") or []
    if layout_variants:
        lines.append("")
        lines.append(f"## Layout Variants: `{row.get('case')}`")
        lines.append("")
        lines.append("| Variant | OK | Error |")
        lines.append("| --- | --- | --- |")
        for variant in layout_variants:
            error = variant.get("error") or {}
            lines.append(
                "| `{label}` | `{ok}` | `{err}` |".format(
                    label=variant.get("label"),
                    ok=variant.get("ok"),
                    err=error.get("type", ""),
                )
            )
(out_dir / "flashinfer_packed_mla_probe_summary.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)
PY

printf '%s\n' "${overall}" > "${OUT_DIR}/flashinfer_packed_mla_probe.exit_code"
printf 'flashinfer packed MLA probe artifacts: %s\n' "${OUT_DIR}"
exit "${overall}"
