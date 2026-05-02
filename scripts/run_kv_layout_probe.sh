#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

PYTHON="${PYTHON:-python}"
KV_LAYOUT_VARIANT="${KV_LAYOUT_VARIANT:-manual}"
KV_LAYOUT_CASE_NAME="${KV_LAYOUT_CASE_NAME:-packed_fp8_indexer_cache_layout}"
KV_LAYOUT_NUM_BLOCKS="${KV_LAYOUT_NUM_BLOCKS:-2}"
KV_LAYOUT_BLOCK_SIZE="${KV_LAYOUT_BLOCK_SIZE:-256}"
KV_LAYOUT_HEAD_DIM="${KV_LAYOUT_HEAD_DIM:-448}"
KV_LAYOUT_SCALE_BYTES="${KV_LAYOUT_SCALE_BYTES:-8}"
KV_LAYOUT_REQUIRE_HELPER_MATCH="${KV_LAYOUT_REQUIRE_HELPER_MATCH:-1}"
KV_LAYOUT_TIMEOUT="${KV_LAYOUT_TIMEOUT:-120}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
OUT_DIR="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/kv_layout_probe/${RUN_TIMESTAMP}}"
export PYTHON KV_LAYOUT_VARIANT KV_LAYOUT_CASE_NAME KV_LAYOUT_NUM_BLOCKS
export KV_LAYOUT_BLOCK_SIZE KV_LAYOUT_HEAD_DIM KV_LAYOUT_SCALE_BYTES
export KV_LAYOUT_REQUIRE_HELPER_MATCH KV_LAYOUT_TIMEOUT
export ARTIFACT_ROOT RUN_TIMESTAMP BRANCH_NAME GPU_TOPOLOGY_SLUG OUT_DIR

mkdir -p "${OUT_DIR}"
write_run_environment
source "${SCRIPT_DIR}/vllm_collect_env.sh"
collect_vllm_env

helper_match_arg=(--require-helper-match)
if [[ "${KV_LAYOUT_REQUIRE_HELPER_MATCH}" != "1" && "${KV_LAYOUT_REQUIRE_HELPER_MATCH}" != "true" ]]; then
  helper_match_arg=(--no-require-helper-match)
fi

set +e
"${PYTHON}" -m ds4_harness.cli kv-layout-probe \
  --target-python "${PYTHON}" \
  --variant "${KV_LAYOUT_VARIANT}" \
  --case-name "${KV_LAYOUT_CASE_NAME}" \
  --num-blocks "${KV_LAYOUT_NUM_BLOCKS}" \
  --block-size "${KV_LAYOUT_BLOCK_SIZE}" \
  --head-dim "${KV_LAYOUT_HEAD_DIM}" \
  --scale-bytes "${KV_LAYOUT_SCALE_BYTES}" \
  "${helper_match_arg[@]}" \
  --timeout "${KV_LAYOUT_TIMEOUT}" \
  --json-output "${OUT_DIR}/kv_layout_probe.json" \
  --markdown-output "${OUT_DIR}/kv_layout_probe.md" \
  --raw-output "${OUT_DIR}/kv_layout_probe_packed_cache.bin"
code="$?"
set -e
printf '%s\n' "${code}" > "${OUT_DIR}/kv_layout_probe.exit_code"

echo "wrote ${OUT_DIR}"
exit "${code}"
