#!/usr/bin/env bash
# Run a controlled GB10 A/B matrix across current and external B12X backend
# checkouts.
#
# Target format:
#   label|vllm_root|vllm_venv|profiles|variants|env_file
#
# `env_file` is optional and may be `-`. Use ignored local env files for
# fork-specific flags such as custom attention backend names or serve extras.
# This wrapper deliberately delegates each target to
# run_gb10_prefill_gap_attribution.sh so branch-to-branch comparisons use the
# same workload and summary parser.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

slugify() {
  printf '%s' "$1" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g'
}

require_target_field() {
  local label="$1"
  local field_name="$2"
  local field_value="$3"
  if [[ -z "${field_value}" ]]; then
    printf 'target %s is missing %s\n' "${label:-<unknown>}" "${field_name}" >&2
    exit 2
  fi
}

RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(slugify "${BRANCH_NAME}")"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-2x_gb10_sm121}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
GB10_B12X_AB_LABEL="${GB10_B12X_AB_LABEL:-gb10_b12x_backend_ab_matrix}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${GB10_B12X_AB_LABEL}/${RUN_TIMESTAMP}}"

GB10_B12X_AB_INPUT_LENS="${GB10_B12X_AB_INPUT_LENS:-4096,16384,32768,65536,128000}"
GB10_B12X_AB_PREFIX_CACHE_MODES="${GB10_B12X_AB_PREFIX_CACHE_MODES:-disabled}"
GB10_B12X_AB_CONCURRENCY="${GB10_B12X_AB_CONCURRENCY:-1}"
GB10_B12X_AB_OUTPUT_LEN="${GB10_B12X_AB_OUTPUT_LEN:-128}"
GB10_B12X_AB_NUM_PROMPTS="${GB10_B12X_AB_NUM_PROMPTS:-2}"
GB10_B12X_AB_BENCH_TIMEOUT="${GB10_B12X_AB_BENCH_TIMEOUT:-1800}"
GB10_B12X_AB_MAX_MODEL_LEN="${GB10_B12X_AB_MAX_MODEL_LEN:-131072}"
GB10_B12X_AB_GPU_MEMORY_UTILIZATION="${GB10_B12X_AB_GPU_MEMORY_UTILIZATION:-0.70}"
GB10_B12X_AB_MAX_NUM_SEQS="${GB10_B12X_AB_MAX_NUM_SEQS:-2}"
GB10_B12X_AB_MAX_NUM_BATCHED_TOKENS="${GB10_B12X_AB_MAX_NUM_BATCHED_TOKENS:-4176}"
GB10_B12X_AB_STAGE_TIMING="${GB10_B12X_AB_STAGE_TIMING:-1}"
GB10_B12X_AB_STATS_OVERLAP_ROWS="${GB10_B12X_AB_STATS_OVERLAP_ROWS:-0}"

if [[ -z "${GB10_B12X_AB_TARGETS:-}" ]]; then
  require_target_field "current_dev" "VLLM_ROOT" "${VLLM_ROOT:-}"
  require_target_field "current_dev" "VLLM_VENV" "${VLLM_VENV:-}"
  GB10_B12X_AB_TARGETS="current_dev|${VLLM_ROOT}|${VLLM_VENV}|dev_default|mtp2|-"
fi

mkdir -p "${OUT_DIR}"
target_records="${OUT_DIR}/target_records.tsv"
: > "${target_records}"

failures=0
IFS=';' read -r -a target_specs <<< "${GB10_B12X_AB_TARGETS}"
for raw_target in "${target_specs[@]}"; do
  [[ -n "${raw_target//[[:space:]]/}" ]] || continue
  IFS='|' read -r label vllm_root vllm_venv profiles variants env_file extra <<< "${raw_target}"

  if [[ -n "${extra:-}" ]]; then
    printf 'target %s has too many fields; expected label|vllm_root|vllm_venv|profiles|variants|env_file\n' "${label:-<unknown>}" >&2
    exit 2
  fi

  require_target_field "${label}" "label" "${label:-}"
  require_target_field "${label}" "vllm_root" "${vllm_root:-}"
  require_target_field "${label}" "vllm_venv" "${vllm_venv:-}"
  profiles="${profiles:-dev_default}"
  variants="${variants:-mtp2}"
  env_file="${env_file:--}"
  target_slug="$(slugify "${label}")"
  target_slug="${target_slug:-target}"
  target_dir="${OUT_DIR}/${target_slug}"
  run_dir="${target_dir}/run"
  mkdir -p "${target_dir}"

  set +e
  (
    set -euo pipefail
    if [[ "${env_file}" != "-" ]]; then
      if [[ ! -f "${env_file}" ]]; then
        printf 'target %s env_file not found: %s\n' "${label}" "${env_file}" >&2
        exit 2
      fi
      set -a
      # shellcheck disable=SC1090
      source "${env_file}"
      set +a
    fi
    env \
      OUT_DIR="${run_dir}" \
      BRANCH_NAME="${label}" \
      VLLM_ROOT="${vllm_root}" \
      VLLM_VENV="${vllm_venv}" \
      GB10_PREFILL_GAP_LABEL="${GB10_B12X_AB_LABEL}_${target_slug}" \
      GB10_PREFILL_GAP_PROFILES="${profiles}" \
      GB10_PREFILL_GAP_VARIANTS="${variants}" \
      GB10_PREFILL_GAP_INPUT_LENS="${GB10_B12X_AB_INPUT_LENS}" \
      GB10_PREFILL_GAP_PREFIX_CACHE_MODES="${GB10_B12X_AB_PREFIX_CACHE_MODES}" \
      GB10_PREFILL_GAP_CONCURRENCY="${GB10_B12X_AB_CONCURRENCY}" \
      GB10_PREFILL_GAP_OUTPUT_LEN="${GB10_B12X_AB_OUTPUT_LEN}" \
      GB10_PREFILL_GAP_NUM_PROMPTS="${GB10_B12X_AB_NUM_PROMPTS}" \
      GB10_PREFILL_GAP_BENCH_TIMEOUT="${GB10_B12X_AB_BENCH_TIMEOUT}" \
      GB10_PREFILL_GAP_MAX_MODEL_LEN="${GB10_B12X_AB_MAX_MODEL_LEN}" \
      GB10_PREFILL_GAP_GPU_MEMORY_UTILIZATION="${GB10_B12X_AB_GPU_MEMORY_UTILIZATION}" \
      GB10_PREFILL_GAP_MAX_NUM_SEQS="${GB10_B12X_AB_MAX_NUM_SEQS}" \
      GB10_PREFILL_GAP_MAX_NUM_BATCHED_TOKENS="${GB10_B12X_AB_MAX_NUM_BATCHED_TOKENS}" \
      GB10_PREFILL_GAP_STAGE_TIMING="${GB10_B12X_AB_STAGE_TIMING}" \
      GB10_PREFILL_GAP_STATS_OVERLAP_ROWS="${GB10_B12X_AB_STATS_OVERLAP_ROWS}" \
      "${SCRIPT_DIR}/run_gb10_prefill_gap_attribution.sh"
  ) > "${target_dir}/child.stdout.log" 2> "${target_dir}/child.stderr.log"
  code="$?"
  set -e

  printf '%s\n' "${code}" > "${target_dir}/child.exit_code"
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "${label}" \
    "${target_slug}" \
    "${profiles}" \
    "${variants}" \
    "${env_file}" \
    "${code}" \
    "${run_dir}/gb10_prefill_gap_attribution_summary.json" \
    >> "${target_records}"
done

PYTHON="${PYTHON:-python}"
GB10_B12X_AB_OUT_DIR="${OUT_DIR}" \
GB10_B12X_AB_TARGET_RECORDS="${target_records}" \
"${PYTHON}" - <<'PY'
import json
import os
from pathlib import Path
from typing import Any

out_dir = Path(os.environ["GB10_B12X_AB_OUT_DIR"])
records_path = Path(os.environ["GB10_B12X_AB_TARGET_RECORDS"])


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


targets = []
for line in records_path.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    label, slug, profiles, variants, env_file, exit_code, summary_path = line.split("\t")
    child_summary = load_json(Path(summary_path))
    rows = child_summary.get("rows", [])
    target_ok = exit_code == "0" and bool(child_summary.get("ok"))
    targets.append(
        {
            "label": label,
            "slug": slug,
            "profiles": profiles,
            "variants": variants,
            "env_file": None if env_file == "-" else env_file,
            "exit_code": int(exit_code),
            "ok": target_ok,
            "summary_path": summary_path,
            "rows": rows if isinstance(rows, list) else [],
        }
    )

summary = {
    "case": "gb10_b12x_backend_ab_matrix",
    "ok": all(target.get("ok") for target in targets) if targets else False,
    "target_count": len(targets),
    "targets": targets,
}
(out_dir / "gb10_b12x_backend_ab_matrix_summary.json").write_text(
    json.dumps(summary, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

lines = [
    "# GB10 B12X Backend A/B Matrix",
    "",
    f"- ok: `{summary['ok']}`",
    f"- targets: `{summary['target_count']}`",
    "",
    "| Target | Profiles | Variants | Exit | OK | Summary |",
    "| --- | --- | --- | ---: | --- | --- |",
]
for target in targets:
    lines.append(
        "| {label} | `{profiles}` | `{variants}` | `{exit_code}` | `{ok}` | `{summary_path}` |".format(
            label=target["label"],
            profiles=target["profiles"],
            variants=target["variants"],
            exit_code=target["exit_code"],
            ok=target["ok"],
            summary_path=target["summary_path"],
        )
    )

(out_dir / "gb10_b12x_backend_ab_matrix_summary.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)
PY

printf '%s\n' "${failures}" > "${OUT_DIR}/gb10_b12x_backend_ab_matrix.exit_code"
exit "${failures}"
