#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

VLLM_BIN="${VLLM_BIN:-vllm}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
HOST="${HOST:-localhost}"
PORT="${PORT:-8000}"
BASE_URL="${BASE_URL:-http://${HOST}:${PORT}}"
PYTHON="${PYTHON:-python}"
RANDOM_PREFILL_INPUT_LENS="${RANDOM_PREFILL_INPUT_LENS:-1024,4096,16384,65536}"
RANDOM_PREFILL_OUTPUT_LEN="${RANDOM_PREFILL_OUTPUT_LEN:-1}"
RANDOM_PREFILL_CONCURRENCY="${RANDOM_PREFILL_CONCURRENCY:-1}"
RANDOM_PREFILL_NUM_PROMPTS="${RANDOM_PREFILL_NUM_PROMPTS:-8}"
RANDOM_PREFILL_BENCH_TIMEOUT="${RANDOM_PREFILL_BENCH_TIMEOUT:-1800}"
RANDOM_PREFILL_TEMPERATURE="${RANDOM_PREFILL_TEMPERATURE:-0.0}"
RANDOM_PREFILL_IGNORE_EOS="${RANDOM_PREFILL_IGNORE_EOS:-1}"
TOKENIZER_MODE="${TOKENIZER_MODE:-deepseek_v4}"
SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT:-1800}"
SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS:-15}"
SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT:-10}"
SERVER_FAILURE_PROBE_TIMEOUT="${SERVER_FAILURE_PROBE_TIMEOUT:-30}"
SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT:-300}"
SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS:-10}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/random_prefill_sweep/${RUN_TIMESTAMP}}"
export VLLM_BIN MODEL HOST PORT BASE_URL PYTHON RANDOM_PREFILL_INPUT_LENS
export RANDOM_PREFILL_OUTPUT_LEN RANDOM_PREFILL_CONCURRENCY
export RANDOM_PREFILL_NUM_PROMPTS RANDOM_PREFILL_BENCH_TIMEOUT
export RANDOM_PREFILL_TEMPERATURE RANDOM_PREFILL_IGNORE_EOS TOKENIZER_MODE
export SERVER_STARTUP_TIMEOUT SERVER_STARTUP_INTERVAL_SECONDS SERVER_HEALTH_TIMEOUT
export SERVER_FAILURE_PROBE_TIMEOUT SERVER_FAILURE_GRACE_TIMEOUT
export SERVER_FAILURE_GRACE_INTERVAL_SECONDS ARTIFACT_ROOT RUN_TIMESTAMP
export BRANCH_NAME GPU_TOPOLOGY_SLUG OUT_DIR

mkdir -p "${OUT_DIR}"
write_run_environment

failures=0
case_dirs=()
IFS=',' read -r -a input_lens <<< "${RANDOM_PREFILL_INPUT_LENS}"
for raw_input_len in "${input_lens[@]}"; do
  input_len="$(printf '%s' "${raw_input_len}" | tr -d '[:space:]')"
  [[ -n "${input_len}" ]] || continue
  case_dir="${OUT_DIR}/isl${input_len}_osl${RANDOM_PREFILL_OUTPUT_LEN}"
  case_dirs+=("${case_dir}")
  set +e
  OUT_DIR="${case_dir}" \
    VLLM_BIN="${VLLM_BIN}" MODEL="${MODEL}" HOST="${HOST}" PORT="${PORT}" \
    BASE_URL="${BASE_URL}" PYTHON="${PYTHON}" TOKENIZER_MODE="${TOKENIZER_MODE}" \
    CONCURRENCY="${RANDOM_PREFILL_CONCURRENCY}" DATASET_NAME=random \
    RANDOM_INPUT_LEN="${input_len}" \
    RANDOM_OUTPUT_LEN="${RANDOM_PREFILL_OUTPUT_LEN}" \
    NUM_PROMPTS="${RANDOM_PREFILL_NUM_PROMPTS}" \
    BENCH_TIMEOUT="${RANDOM_PREFILL_BENCH_TIMEOUT}" \
    TEMPERATURE="${RANDOM_PREFILL_TEMPERATURE}" \
    IGNORE_EOS="${RANDOM_PREFILL_IGNORE_EOS}" \
    SERVER_STARTUP_TIMEOUT="${SERVER_STARTUP_TIMEOUT}" \
    SERVER_STARTUP_INTERVAL_SECONDS="${SERVER_STARTUP_INTERVAL_SECONDS}" \
    SERVER_HEALTH_TIMEOUT="${SERVER_HEALTH_TIMEOUT}" \
    SERVER_FAILURE_PROBE_TIMEOUT="${SERVER_FAILURE_PROBE_TIMEOUT}" \
    SERVER_FAILURE_GRACE_TIMEOUT="${SERVER_FAILURE_GRACE_TIMEOUT}" \
    SERVER_FAILURE_GRACE_INTERVAL_SECONDS="${SERVER_FAILURE_GRACE_INTERVAL_SECONDS}" \
    "${SCRIPT_DIR}/run_bench_matrix.sh"
  code="$?"
  set -e
  printf '%s\n' "${code}" > "${case_dir}/prefill_sweep_case.exit_code"
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi
done

case_dir_list="$(IFS=:; printf '%s' "${case_dirs[*]}")"
SWEEP_CASE_DIRS="${case_dir_list}" "${PYTHON}" - <<'PY'
import json
import os
from pathlib import Path

out_dir = Path(os.environ["OUT_DIR"])
case_dirs = [
    Path(item) for item in os.environ.get("SWEEP_CASE_DIRS", "").split(":") if item
]


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


rows = []
for case_dir in case_dirs:
    bench_path = case_dir / "bench.json"
    exit_path = case_dir / "prefill_sweep_case.exit_code"
    exit_code = int(exit_path.read_text(encoding="utf-8").strip() or "1")
    try:
        data = json.loads(bench_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = []
    for bench_row in data if isinstance(data, list) else []:
        metrics = bench_row.get("metrics") if isinstance(bench_row, dict) else {}
        duration = number(metrics.get("benchmark_duration_s"))
        input_tokens = number(metrics.get("total_input_tokens"))
        input_tps = (
            None if duration is None or duration <= 0 or input_tokens is None
            else round(input_tokens / duration, 2)
        )
        rows.append(
            {
                "case": case_dir.name,
                "artifact_dir": str(case_dir),
                "exit_code": exit_code,
                "ok": bool(bench_row.get("ok")) and exit_code == 0,
                "concurrency": bench_row.get("concurrency"),
                "successful_requests": metrics.get("successful_requests"),
                "total_input_tokens": metrics.get("total_input_tokens"),
                "benchmark_duration_s": metrics.get("benchmark_duration_s"),
                "input_token_throughput_tok_s": input_tps,
                "output_token_throughput_tok_s": metrics.get(
                    "output_token_throughput_tok_s"
                ),
                "mean_ttft_ms": metrics.get("mean_ttft_ms"),
                "p99_ttft_ms": metrics.get("p99_ttft_ms"),
                "mean_tpot_ms": metrics.get("mean_tpot_ms"),
                "p99_itl_ms": metrics.get("p99_itl_ms"),
            }
        )
    if not data:
        rows.append(
            {
                "case": case_dir.name,
                "artifact_dir": str(case_dir),
                "exit_code": exit_code,
                "ok": False,
            }
        )

summary = {
    "case": "random_prefill_sweep",
    "ok": all(row.get("ok") for row in rows),
    "rows": rows,
}
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "prefill_sweep_summary.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

lines = [
    "# Random Prefill Sweep",
    "",
    f"- OK: `{summary['ok']}`",
    "",
    "| Case | OK | C | Successful | Input tok/s | Output tok/s | Mean TTFT ms | P99 TTFT ms |",
    "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
]
for row in rows:
    def fmt(value):
        return "n/a" if value is None else str(value)

    lines.append(
        "| `{case}` | {ok} | {concurrency} | {successful} | {input_tps} | "
        "{output_tps} | {mean_ttft} | {p99_ttft} |".format(
            case=row.get("case"),
            ok="yes" if row.get("ok") else "no",
            concurrency=fmt(row.get("concurrency")),
            successful=fmt(row.get("successful_requests")),
            input_tps=fmt(row.get("input_token_throughput_tok_s")),
            output_tps=fmt(row.get("output_token_throughput_tok_s")),
            mean_ttft=fmt(row.get("mean_ttft_ms")),
            p99_ttft=fmt(row.get("p99_ttft_ms")),
        )
    )
(out_dir / "prefill_sweep_summary.md").write_text(
    "\n".join(lines).rstrip() + "\n",
    encoding="utf-8",
)
PY

printf '%s\n' "${failures}" > "${OUT_DIR}/random_prefill_sweep.exit_code"
echo "wrote ${OUT_DIR}"
exit "${failures}"
