#!/usr/bin/env bash
# Run a focused pure-prefill attribution pass for DS4 SM12x.
#
# This is a development observation gate, not a PR hard gate.  It combines the
# existing random prefill benchmark with DeepSeek V4 sparse MLA stats so a run
# records both endpoint TTFT/input throughput and sparse-attention candidate
# work for the same serve profile.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8080}"
B200_VLLM_REPO="${B200_VLLM_REPO:-/workspace/vllm}"
B200_VLLM_VENV="${B200_VLLM_VENV:-${B200_VLLM_REPO}/.venv}"
PYTHON="${PYTHON:-${B200_VLLM_VENV}/bin/python}"
VLLM_BIN="${VLLM_BIN:-${B200_VLLM_VENV}/bin/vllm}"
VLLM_ROOT="${VLLM_ROOT:-${B200_VLLM_REPO}}"
PYTHONPATH="$(harness_pythonpath)"
export VLLM_ROOT PYTHONPATH
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
SM12X_PREFILL_GAP_LABEL="${SM12X_PREFILL_GAP_LABEL:-sm12x_prefill_gap_attribution}"
SM12X_PREFILL_GAP_ROOT="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${SM12X_PREFILL_GAP_LABEL}/${RUN_TIMESTAMP}}"

SM12X_PREFILL_GAP_VARIANT="${SM12X_PREFILL_GAP_VARIANT:-mtp}"
SM12X_PREFILL_GAP_INPUT_LENS="${SM12X_PREFILL_GAP_INPUT_LENS:-58957,124000}"
SM12X_PREFILL_GAP_CONCURRENCY="${SM12X_PREFILL_GAP_CONCURRENCY:-1,2,3,4}"
SM12X_PREFILL_GAP_OUTPUT_LEN="${SM12X_PREFILL_GAP_OUTPUT_LEN:-1}"
SM12X_PREFILL_GAP_NUM_PROMPTS="${SM12X_PREFILL_GAP_NUM_PROMPTS:-4}"
SM12X_PREFILL_GAP_BENCH_TIMEOUT="${SM12X_PREFILL_GAP_BENCH_TIMEOUT:-3600}"
# Keep candidate-overlap sampling off by default: it copies sampled indices back
# to CPU and can materially distort endpoint TTFT/input throughput. Enable it
# only for diagnostic attribution runs.
SM12X_PREFILL_GAP_STATS_OVERLAP_ROWS="${SM12X_PREFILL_GAP_STATS_OVERLAP_ROWS:-0}"
SM12X_PREFILL_GAP_STAGE_TIMING="${SM12X_PREFILL_GAP_STAGE_TIMING:-0}"

SM12X_PREFILL_GAP_GPU_MEMORY_UTILIZATION="${SM12X_PREFILL_GAP_GPU_MEMORY_UTILIZATION:-0.975}"
SM12X_PREFILL_GAP_MAX_MODEL_LEN="${SM12X_PREFILL_GAP_MAX_MODEL_LEN:-131072}"
SM12X_PREFILL_GAP_MAX_NUM_BATCHED_TOKENS="${SM12X_PREFILL_GAP_MAX_NUM_BATCHED_TOKENS:-4096}"
SM12X_PREFILL_GAP_MAX_NUM_SEQS="${SM12X_PREFILL_GAP_MAX_NUM_SEQS:-4}"
_DEFAULT_SM12X_PREFILL_GAP_EXTRA_SERVE_ARGS="--gpu-memory-utilization ${SM12X_PREFILL_GAP_GPU_MEMORY_UTILIZATION} --max-num-batched-tokens ${SM12X_PREFILL_GAP_MAX_NUM_BATCHED_TOKENS} --max-num-seqs ${SM12X_PREFILL_GAP_MAX_NUM_SEQS} --enable-expert-parallel --compilation-config '{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\",\"custom_ops\":[\"all\"]}'"
B200_EXTRA_SERVE_ARGS="${B200_EXTRA_SERVE_ARGS:-${_DEFAULT_SM12X_PREFILL_GAP_EXTRA_SERVE_ARGS}}"

SM12X_PREFILL_GAP_D512_ENV="${SM12X_PREFILL_GAP_D512_ENV:-0}"
_prefill_gap_remote_envs="VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_PATH,VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_OVERLAP_ROWS,VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_STAGE_TIMING"
_prefill_gap_d512_env=()
case "${SM12X_PREFILL_GAP_D512_ENV}" in
  default)
    ;;
  0|1)
    _prefill_gap_remote_envs="${_prefill_gap_remote_envs},VLLM_DEEPSEEK_V4_INDEXED_D512_SPLIT_PREFILL"
    _prefill_gap_d512_env=(
      "VLLM_DEEPSEEK_V4_INDEXED_D512_SPLIT_PREFILL=${SM12X_PREFILL_GAP_D512_ENV}"
    )
    ;;
  *)
    echo "SM12X_PREFILL_GAP_D512_ENV must be 0, 1, or default; got '${SM12X_PREFILL_GAP_D512_ENV}'" >&2
    exit 2
    ;;
esac
SERVE_REMOTE_ENV_VARS="${SERVE_REMOTE_ENV_VARS:+${SERVE_REMOTE_ENV_VARS},}${_prefill_gap_remote_envs}"

case "${SM12X_PREFILL_GAP_VARIANT}" in
  *","*|*" "*)
    echo "SM12X_PREFILL_GAP_VARIANT must be a single variant; got '${SM12X_PREFILL_GAP_VARIANT}'" >&2
    exit 2
    ;;
esac

mkdir -p "${SM12X_PREFILL_GAP_ROOT}"

failures=0
case_dirs=()
IFS=',' read -r -a input_lens <<< "${SM12X_PREFILL_GAP_INPUT_LENS}"
for raw_input_len in "${input_lens[@]}"; do
  input_len="$(printf '%s' "${raw_input_len}" | tr -d '[:space:]')"
  [[ -n "${input_len}" ]] || continue
  case_dir="${SM12X_PREFILL_GAP_ROOT}/isl${input_len}"
  stats_dir="${case_dir}/sparse_mla_stats_raw"
  mkdir -p "${case_dir}" "${stats_dir}"
  case_dirs+=("${case_dir}")

  set +e
  env \
    OUT_DIR="${case_dir}" \
    MODEL="${MODEL}" HOST="${HOST}" PORT="${PORT}" \
    B200_VLLM_REPO="${B200_VLLM_REPO}" B200_VLLM_VENV="${B200_VLLM_VENV}" \
    PYTHON="${PYTHON}" VLLM_BIN="${VLLM_BIN}" \
    B200_BASELINE_LABEL="${SM12X_PREFILL_GAP_LABEL}_isl${input_len}" \
    ARTIFACT_ARCHIVE_PREVIOUS=0 \
    B200_BASELINE_VARIANTS="${SM12X_PREFILL_GAP_VARIANT}" \
    B200_BASELINE_PHASES="bench_random_prefill_sweep" \
    B200_TENSOR_PARALLEL_SIZE="${B200_TENSOR_PARALLEL_SIZE:-2}" \
    B200_BLOCK_SIZE="${B200_BLOCK_SIZE:-256}" \
    B200_KV_CACHE_DTYPE="${B200_KV_CACHE_DTYPE:-fp8}" \
    SERVE_MAX_MODEL_LEN="${SERVE_MAX_MODEL_LEN:-${SM12X_PREFILL_GAP_MAX_MODEL_LEN}}" \
    SERVE_PREFIX_CACHE_MODE="${SERVE_PREFIX_CACHE_MODE:-disabled}" \
    SERVE_USE_FP4_INDEXER_CACHE="${SERVE_USE_FP4_INDEXER_CACHE:-0}" \
    B200_EXTRA_SERVE_ARGS="${B200_EXTRA_SERVE_ARGS}" \
    RUN_RANDOM_PREFILL_SWEEP=1 \
    RANDOM_PREFILL_INPUT_LENS="${input_len}" \
    RANDOM_PREFILL_OUTPUT_LEN="${SM12X_PREFILL_GAP_OUTPUT_LEN}" \
    RANDOM_PREFILL_CONCURRENCY="${SM12X_PREFILL_GAP_CONCURRENCY}" \
    RANDOM_PREFILL_NUM_PROMPTS="${SM12X_PREFILL_GAP_NUM_PROMPTS}" \
    RANDOM_PREFILL_BENCH_TIMEOUT="${SM12X_PREFILL_GAP_BENCH_TIMEOUT}" \
    RANDOM_PREFILL_TEMPERATURE=0.0 \
    RANDOM_PREFILL_IGNORE_EOS=1 \
    VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_PATH="${stats_dir}" \
    VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_OVERLAP_ROWS="${SM12X_PREFILL_GAP_STATS_OVERLAP_ROWS}" \
    VLLM_DEEPSEEK_V4_SPARSE_MLA_STATS_STAGE_TIMING="${SM12X_PREFILL_GAP_STAGE_TIMING}" \
    "${_prefill_gap_d512_env[@]}" \
    SERVE_REMOTE_ENV_VARS="${SERVE_REMOTE_ENV_VARS}" \
    "${SCRIPT_DIR}/run_b200_baseline.sh" \
      >"${case_dir}/child.stdout.log" \
      2>"${case_dir}/child.stderr.log"
  code="$?"
  set -e
  printf '%s\n' "${code}" > "${case_dir}/child.exit_code"
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi

  "${PYTHON}" -m ds4_harness.cli sparse-mla-stats-report \
    --stats-path "${stats_dir}" \
    --json-output "${case_dir}/sparse_mla_stats_summary.json" \
    --markdown-output "${case_dir}/sparse_mla_stats_summary.md"
done

case_dir_list="$(IFS=:; printf '%s' "${case_dirs[*]}")"
SM12X_PREFILL_GAP_CASE_DIRS="${case_dir_list}" \
SM12X_PREFILL_GAP_ROOT="${SM12X_PREFILL_GAP_ROOT}" \
SM12X_PREFILL_GAP_VARIANT="${SM12X_PREFILL_GAP_VARIANT}" \
"${PYTHON}" - <<'PY'
import json
import os
from pathlib import Path
from typing import Any

root = Path(os.environ["SM12X_PREFILL_GAP_ROOT"])
variant = os.environ["SM12X_PREFILL_GAP_VARIANT"]
case_dirs = [
    Path(item)
    for item in os.environ.get("SM12X_PREFILL_GAP_CASE_DIRS", "").split(":")
    if item
]


def _load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


def _read_exit(path: Path) -> int:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return 1


def _overlap_ratio(sparse: dict[str, Any], region: str, group_size: str = "16") -> Any:
    overlap = sparse.get("candidate_overlap", {})
    if not isinstance(overlap, dict):
        return "n/a"
    if region == "all":
        groups = overlap.get("groups", {})
    else:
        regions = overlap.get("regions", {})
        groups = regions.get(region, {}) if isinstance(regions, dict) else {}
    if not isinstance(groups, dict):
        return "n/a"
    values = groups.get(group_size)
    if not isinstance(values, dict):
        return "n/a"
    return values.get("unique_to_valid_ratio", "n/a")


rows = []
for case_dir in case_dirs:
    bench_summary = _load_json(
        case_dir
        / variant
        / "bench_random_prefill_sweep"
        / "prefill_sweep_summary.json",
        {},
    )
    sparse_summary = _load_json(
        case_dir / "sparse_mla_stats_summary.json",
        {},
    )
    child_exit = _read_exit(case_dir / "child.exit_code")
    rows.append(
        {
            "case": case_dir.name,
            "artifact_dir": str(case_dir),
            "exit_code": child_exit,
            "ok": child_exit == 0
            and bool(bench_summary.get("ok"))
            and sparse_summary.get("row_count", 0) > 0,
            "bench_rows": bench_summary.get("rows", []),
            "sparse_mla": {
                "row_count": sparse_summary.get("row_count", 0),
                "candidate_work": sparse_summary.get("candidate_work", {}),
                "stage_timings_ms": sparse_summary.get("stage_timings_ms", {}),
                "stage_efficiency": sparse_summary.get("stage_efficiency", {}),
                "candidate_overlap": sparse_summary.get("candidate_overlap", {}),
                "candidate_region_work": sparse_summary.get("candidate_region_work", {}),
                "groups": sparse_summary.get("groups", []),
            },
        }
    )

summary = {
    "case": "sm12x_prefill_gap_attribution",
    "variant": variant,
    "ok": all(row["ok"] for row in rows),
    "rows": rows,
}
root.mkdir(parents=True, exist_ok=True)
(root / "prefill_gap_attribution_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

lines = [
    "# SM12x Prefill Gap Attribution",
    "",
    f"- OK: `{summary['ok']}`",
    f"- Variant: `{variant}`",
    "",
    "| Case | OK | C | Input tok/s | Mean TTFT ms | P99 TTFT ms | Sparse rows | Candidate slots | Effective visits | Padding ratio | Compressed effective visits | Compressed padding ratio | SWA effective visits | SWA padding ratio | All group16 unique/valid | Compressed group16 unique/valid | SWA group16 unique/valid | Stage total ms | Dominant stage | Accumulate ratio | Sparse visits/s | Sparse ms/Mvisit |",
    "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
]
for row in rows:
    sparse = row.get("sparse_mla", {})
    work = sparse.get("candidate_work", {})
    region_work = sparse.get("candidate_region_work", {})
    compressed_work = (
        region_work.get("compressed", {}) if isinstance(region_work, dict) else {}
    )
    swa_work = region_work.get("swa", {}) if isinstance(region_work, dict) else {}
    timings = sparse.get("stage_timings_ms", {})
    efficiency = sparse.get("stage_efficiency", {})
    timing_stages = timings.get("stages", {}) if isinstance(timings, dict) else {}
    sparse_accumulate = (
        timing_stages.get("sparse_accumulate", {})
        if isinstance(timing_stages, dict)
        else {}
    )
    bench_rows = row.get("bench_rows") or [{}]
    for bench_row in bench_rows:
        lines.append(
            "| {case} | {ok} | {concurrency} | {input_tps} | {mean_ttft} | {p99_ttft} | {sparse_rows} | {slots} | {effective} | {padding} | {compressed_effective} | {compressed_padding} | {swa_effective} | {swa_padding} | {overlap_all_g16} | {overlap_compressed_g16} | {overlap_swa_g16} | {stage_total} | {dominant_stage} | {accumulate_ratio} | {sparse_visits_per_s} | {sparse_ms_per_mvisit} |".format(
                case=f"`{row['case']}`",
                ok="yes" if row.get("ok") else "no",
                concurrency=bench_row.get("concurrency", "n/a"),
                input_tps=bench_row.get("input_token_throughput_tok_s", "n/a"),
                mean_ttft=bench_row.get("mean_ttft_ms", "n/a"),
                p99_ttft=bench_row.get("p99_ttft_ms", "n/a"),
                sparse_rows=sparse.get("row_count", "n/a"),
                slots=work.get("candidate_slots", "n/a"),
                effective=work.get("effective_candidate_visits", "n/a"),
                padding=work.get("padding_ratio", "n/a"),
                compressed_effective=compressed_work.get(
                    "effective_candidate_visits", "n/a"
                )
                if isinstance(compressed_work, dict)
                else "n/a",
                compressed_padding=compressed_work.get("padding_ratio", "n/a")
                if isinstance(compressed_work, dict)
                else "n/a",
                swa_effective=swa_work.get("effective_candidate_visits", "n/a")
                if isinstance(swa_work, dict)
                else "n/a",
                swa_padding=swa_work.get("padding_ratio", "n/a")
                if isinstance(swa_work, dict)
                else "n/a",
                overlap_all_g16=_overlap_ratio(sparse, "all"),
                overlap_compressed_g16=_overlap_ratio(sparse, "compressed"),
                overlap_swa_g16=_overlap_ratio(sparse, "swa"),
                stage_total=timings.get("total", "n/a")
                if isinstance(timings, dict)
                else "n/a",
                dominant_stage=timings.get("dominant_stage", "n/a")
                if isinstance(timings, dict)
                else "n/a",
                accumulate_ratio=sparse_accumulate.get("ratio", "n/a")
                if isinstance(sparse_accumulate, dict)
                else "n/a",
                sparse_visits_per_s=efficiency.get(
                    "sparse_accumulate_effective_candidate_visits_per_s",
                    "n/a",
                )
                if isinstance(efficiency, dict)
                else "n/a",
                sparse_ms_per_mvisit=efficiency.get(
                    "sparse_accumulate_ms_per_million_effective_visits",
                    "n/a",
                )
                if isinstance(efficiency, dict)
                else "n/a",
            )
        )
(root / "prefill_gap_attribution_summary.md").write_text(
    "\n".join(lines).rstrip() + "\n",
    encoding="utf-8",
)
PY

printf '%s\n' "${failures}" > "${SM12X_PREFILL_GAP_ROOT}/prefill_gap_attribution.exit_code"
echo "wrote ${SM12X_PREFILL_GAP_ROOT}"
exit "${failures}"
