#!/usr/bin/env bash
# Run the fixed SM12x sparse-MLA accumulate microbench profile.
#
# This is the pre-endpoint gate for kernel experiments that try to reduce
# sparse-MLA candidate/value work. Current vLLM builds expose the chunk
# accumulate path here; older partial-state experiments were rejected and are
# intentionally not part of this baseline wrapper.
#
# By default it runs a CUDA timing microbench only. Set
# SM12X_SPARSE_MLA_RUN_NCU=1 to also collect focused Nsight Compute reports.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

PYTHON="${PYTHON:-python}"
VLLM_ROOT="${VLLM_ROOT:-${REPO_ROOT}/vllm}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/sm12x_sparse_mla_ncu_microbench/$(date +%Y%m%d%H%M%S)}"
NCU_BIN="${NCU_BIN:-ncu}"

SM12X_SPARSE_MLA_LABEL="${SM12X_SPARSE_MLA_LABEL:-sm12x_sparse_mla_ncu_microbench}"
SM12X_SPARSE_MLA_TOKENS="${SM12X_SPARSE_MLA_TOKENS:-256,1024,2048}"
SM12X_SPARSE_MLA_CANDIDATES="${SM12X_SPARSE_MLA_CANDIDATES:-512,1024,1152}"
SM12X_SPARSE_MLA_HEADS="${SM12X_SPARSE_MLA_HEADS:-64}"
SM12X_SPARSE_MLA_HEAD_DIM="${SM12X_SPARSE_MLA_HEAD_DIM:-512}"
SM12X_SPARSE_MLA_KV_ROWS="${SM12X_SPARSE_MLA_KV_ROWS:-131072}"
SM12X_SPARSE_MLA_PART_SIZE="${SM12X_SPARSE_MLA_PART_SIZE:-512}"
SM12X_SPARSE_MLA_WARMUPS="${SM12X_SPARSE_MLA_WARMUPS:-3}"
SM12X_SPARSE_MLA_REPEATS="${SM12X_SPARSE_MLA_REPEATS:-10}"
SM12X_SPARSE_MLA_DEVICE="${SM12X_SPARSE_MLA_DEVICE:-cuda:0}"
SM12X_SPARSE_MLA_SEED="${SM12X_SPARSE_MLA_SEED:-1234}"

# The realistic staggered-lens shape is the default because full-lens synthetic
# inputs have repeatedly overstated rejected multi-pass wins.
SM12X_SPARSE_MLA_LENS_MODE="${SM12X_SPARSE_MLA_LENS_MODE:-staggered}"
SM12X_SPARSE_MLA_RUN_FULL_LENS_CONTROL="${SM12X_SPARSE_MLA_RUN_FULL_LENS_CONTROL:-0}"

SM12X_SPARSE_MLA_RUN_NCU="${SM12X_SPARSE_MLA_RUN_NCU:-0}"
SM12X_SPARSE_MLA_NCU_TOKENS="${SM12X_SPARSE_MLA_NCU_TOKENS:-256}"
SM12X_SPARSE_MLA_NCU_CANDIDATES="${SM12X_SPARSE_MLA_NCU_CANDIDATES:-1152}"
SM12X_SPARSE_MLA_NCU_WARMUPS="${SM12X_SPARSE_MLA_NCU_WARMUPS:-1}"
SM12X_SPARSE_MLA_NCU_REPEATS="${SM12X_SPARSE_MLA_NCU_REPEATS:-1}"
SM12X_SPARSE_MLA_NCU_SET="${SM12X_SPARSE_MLA_NCU_SET:-full}"
SM12X_SPARSE_MLA_NCU_KERNEL_CHUNK="${SM12X_SPARSE_MLA_NCU_KERNEL_CHUNK:-regex:_accumulate_indexed_attention_chunk_multihead_kernel}"
SM12X_SPARSE_MLA_NCU_EXTRA_ARGS="${SM12X_SPARSE_MLA_NCU_EXTRA_ARGS:-}"

mkdir -p "${OUT_DIR}"

run_microbench() {
  local lens_mode="$1"
  local out_subdir="$2"
  mkdir -p "${out_subdir}"
  "${PYTHON}" "${SCRIPT_DIR}/run_sparse_mla_accumulate_microbench.py" \
    --vllm-root "${VLLM_ROOT}" \
    --out-dir "${out_subdir}" \
    --tokens "${SM12X_SPARSE_MLA_TOKENS}" \
    --candidates "${SM12X_SPARSE_MLA_CANDIDATES}" \
    --heads "${SM12X_SPARSE_MLA_HEADS}" \
    --head-dim "${SM12X_SPARSE_MLA_HEAD_DIM}" \
    --kv-rows "${SM12X_SPARSE_MLA_KV_ROWS}" \
    --modes chunk \
    --part-size "${SM12X_SPARSE_MLA_PART_SIZE}" \
    --lens-mode "${lens_mode}" \
    --warmups "${SM12X_SPARSE_MLA_WARMUPS}" \
    --repeats "${SM12X_SPARSE_MLA_REPEATS}" \
    --seed "${SM12X_SPARSE_MLA_SEED}" \
    --device "${SM12X_SPARSE_MLA_DEVICE}"
}

run_ncu_case() {
  local case_name="$1"
  local mode="$2"
  local kernel_name="$3"
  local case_dir="${OUT_DIR}/ncu_${case_name}"
  mkdir -p "${case_dir}"

  # shellcheck disable=SC2206
  local extra_args=( ${SM12X_SPARSE_MLA_NCU_EXTRA_ARGS} )
  "${NCU_BIN}" \
    --force-overwrite \
    --target-processes all \
    --set "${SM12X_SPARSE_MLA_NCU_SET}" \
    --kernel-name-base function \
    --kernel-name "${kernel_name}" \
    --export "${case_dir}/profile" \
    --log-file "${case_dir}/ncu.log" \
    "${extra_args[@]}" \
    -- "${PYTHON}" "${SCRIPT_DIR}/run_sparse_mla_accumulate_microbench.py" \
      --vllm-root "${VLLM_ROOT}" \
      --out-dir "${case_dir}/microbench" \
      --tokens "${SM12X_SPARSE_MLA_NCU_TOKENS}" \
      --candidates "${SM12X_SPARSE_MLA_NCU_CANDIDATES}" \
      --heads "${SM12X_SPARSE_MLA_HEADS}" \
      --head-dim "${SM12X_SPARSE_MLA_HEAD_DIM}" \
      --kv-rows "${SM12X_SPARSE_MLA_KV_ROWS}" \
      --modes "${mode}" \
      --part-size "${SM12X_SPARSE_MLA_PART_SIZE}" \
      --lens-mode "${SM12X_SPARSE_MLA_LENS_MODE}" \
      --warmups "${SM12X_SPARSE_MLA_NCU_WARMUPS}" \
      --repeats "${SM12X_SPARSE_MLA_NCU_REPEATS}" \
      --seed "${SM12X_SPARSE_MLA_SEED}" \
      --device "${SM12X_SPARSE_MLA_DEVICE}" \
      --emit-nvtx

  if [[ -f "${case_dir}/profile.ncu-rep" ]]; then
    "${NCU_BIN}" --import "${case_dir}/profile.ncu-rep" \
      --page details \
      --csv > "${case_dir}/ncu_details.csv"
  fi
}

write_summary() {
  OUT_DIR="${OUT_DIR}" \
  SM12X_SPARSE_MLA_LABEL="${SM12X_SPARSE_MLA_LABEL}" \
  SM12X_SPARSE_MLA_RUN_NCU="${SM12X_SPARSE_MLA_RUN_NCU}" \
  "${PYTHON}" - <<'PYEOF'
import json
import os
import csv
from pathlib import Path


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"parse_error": str(exc)}


def _rows(payload: dict, label: str) -> list[dict]:
    rows = []
    for row in payload.get("results", []):
        rows.append(
            {
                "lens_mode": label,
                "mode": row.get("mode"),
                "tokens": row.get("tokens"),
                "candidates": row.get("candidates"),
                "mean_ms": row.get("mean_ms"),
                "p95_ms": row.get("p95_ms"),
                "candidate_visits_per_s": row.get("candidate_visits_per_s"),
            }
        )
    return rows


def _selected_ncu_metrics(path: Path) -> dict:
    if not path.exists():
        return {}
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    ids = sorted(
        {
            int(row["ID"])
            for row in rows
            if row.get("ID", "").isdigit()
        }
    )
    if not ids:
        return {}
    target_id = str(ids[-1])
    selected = {"profile_id": ids[-1]}
    metric_names = {
        "Duration": "duration_ms",
        "Compute (SM) Throughput": "sm_throughput_pct",
        "DRAM Throughput": "dram_throughput_pct",
        "Eligible Warps Per Scheduler": "eligible_warps_per_scheduler",
        "Active Warps Per Scheduler": "active_warps_per_scheduler",
        "No Eligible": "no_eligible_pct",
        "Issue Slots Busy": "issue_slots_busy_pct",
        "Registers Per Thread": "registers_per_thread",
        "Theoretical Occupancy": "theoretical_occupancy_pct",
        "Achieved Occupancy": "achieved_occupancy_pct",
        "L2 Hit Rate": "l2_hit_rate_pct",
        "Waves Per SM": "waves_per_sm",
    }
    for row in rows:
        if row.get("ID") != target_id:
            continue
        name = row.get("Metric Name", "")
        key = metric_names.get(name)
        if key is None:
            continue
        selected[key] = row.get("Metric Value")
    return selected


out_dir = Path(os.environ["OUT_DIR"])
label = os.environ["SM12X_SPARSE_MLA_LABEL"]
run_ncu = os.environ["SM12X_SPARSE_MLA_RUN_NCU"]
staggered = _read_json(
    out_dir / "microbench_staggered" / "sparse_mla_accumulate_microbench.json"
)
full = _read_json(out_dir / "microbench_full" / "sparse_mla_accumulate_microbench.json")
rows = _rows(staggered, "staggered") + _rows(full, "full")

ncu_cases = []
for case_name in ("chunk",):
    case_dir = out_dir / f"ncu_{case_name}"
    ncu_cases.append(
        {
            "case": case_name,
            "ran": case_dir.exists(),
            "ncu_log": str(case_dir / "ncu.log") if case_dir.exists() else None,
            "profile": str(case_dir / "profile.ncu-rep") if case_dir.exists() else None,
            "selected_metrics": _selected_ncu_metrics(case_dir / "ncu_details.csv"),
        }
    )

payload = {
    "label": label,
    "run_ncu": run_ncu in {"1", "true", "yes"},
    "rows": rows,
    "ncu_cases": ncu_cases,
}
(out_dir / "sm12x_sparse_mla_ncu_microbench_summary.json").write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

lines = [
    "# SM12x sparse MLA NCU microbench summary",
    "",
    f"Label: `{label}`",
    "",
    "| Lens | Mode | Tokens | Candidates | Mean ms | P95 ms | Candidate visits/s |",
    "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
]
for row in rows:
    lines.append(
        "| {lens_mode} | {mode} | {tokens} | {candidates} | {mean_ms:.3f} | {p95_ms:.3f} | {candidate_visits_per_s:.3e} |".format(
            **row
        )
    )
lines.extend(["", "## NCU cases", ""])
lines.append("| Case | Ran | Log | Profile |")
lines.append("| --- | --- | --- | --- |")
for case in ncu_cases:
    lines.append(
        "| {case} | {ran} | `{ncu_log}` | `{profile}` |".format(**case)
    )
lines.append("")
lines.append("## Selected NCU metrics")
lines.append("")
lines.append(
    "| Case | Duration ms | SM % | DRAM % | Eligible warps/sched | Registers/thread | Achieved occupancy |"
)
lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
for case in ncu_cases:
    metrics = case.get("selected_metrics") or {}
    lines.append(
        "| {case} | {duration} | {sm} | {dram} | {eligible} | {regs} | {occ} |".format(
            case=case["case"],
            duration=metrics.get("duration_ms", ""),
            sm=metrics.get("sm_throughput_pct", ""),
            dram=metrics.get("dram_throughput_pct", ""),
            eligible=metrics.get("eligible_warps_per_scheduler", ""),
            regs=metrics.get("registers_per_thread", ""),
            occ=metrics.get("achieved_occupancy_pct", ""),
        )
    )
lines.append("")
(out_dir / "sm12x_sparse_mla_ncu_microbench_summary.md").write_text(
    "\n".join(lines),
    encoding="utf-8",
)
PYEOF
}

echo "running staggered sparse-MLA microbench into ${OUT_DIR}"
run_microbench "${SM12X_SPARSE_MLA_LENS_MODE}" "${OUT_DIR}/microbench_staggered"

if [[ "${SM12X_SPARSE_MLA_RUN_FULL_LENS_CONTROL}" == "1" ]]; then
  echo "running full-lens sparse-MLA control into ${OUT_DIR}"
  run_microbench "full" "${OUT_DIR}/microbench_full"
fi

if [[ "${SM12X_SPARSE_MLA_RUN_NCU}" == "1" ]]; then
  if ! command -v "${NCU_BIN}" >/dev/null 2>&1; then
    echo "ncu not on PATH; set NCU_BIN or disable SM12X_SPARSE_MLA_RUN_NCU" >&2
    exit 2
  fi
  echo "running focused NCU chunk-path profile"
  run_ncu_case "chunk" "chunk" "${SM12X_SPARSE_MLA_NCU_KERNEL_CHUNK}"
fi

write_summary
echo "wrote ${OUT_DIR}"
