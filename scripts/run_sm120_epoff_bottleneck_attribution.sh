#!/usr/bin/env bash
# Run the first RTX / SM120 EP-off bottleneck attribution slice.
#
# This wrapper intentionally stays narrow: it runs sparse-MLA prefill
# attribution under the current EP-off serving profile, with an opt-in EP-on
# comparison for MoE / pipeline balance checks. Correctness and GB10 gates are
# separate follow-up steps after a candidate has a clear attribution signal.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env
configure_sm120_vllm_env

RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-2x_rtx_pro_6000_sm120}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
SM120_EPOFF_BOTTLENECK_LABEL="${SM120_EPOFF_BOTTLENECK_LABEL:-sm120_epoff_bottleneck_attribution}"
SM120_EPOFF_BOTTLENECK_ROOT="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${SM120_EPOFF_BOTTLENECK_LABEL}/${RUN_TIMESTAMP}}"

SM120_EPOFF_BOTTLENECK_VARIANT="${SM120_EPOFF_BOTTLENECK_VARIANT:-mtp}"
SM120_EPOFF_BOTTLENECK_INPUT_LENS="${SM120_EPOFF_BOTTLENECK_INPUT_LENS:-4096,16384,65536,124000}"
SM120_EPOFF_BOTTLENECK_EPON_INPUT_LENS="${SM120_EPOFF_BOTTLENECK_EPON_INPUT_LENS:-4096,16384,65536}"
SM120_EPOFF_BOTTLENECK_CONCURRENCY="${SM120_EPOFF_BOTTLENECK_CONCURRENCY:-1,2,4}"
SM120_EPOFF_BOTTLENECK_OUTPUT_LEN="${SM120_EPOFF_BOTTLENECK_OUTPUT_LEN:-1}"
SM120_EPOFF_BOTTLENECK_NUM_PROMPTS="${SM120_EPOFF_BOTTLENECK_NUM_PROMPTS:-8}"
SM120_EPOFF_BOTTLENECK_D512_ENV="${SM120_EPOFF_BOTTLENECK_D512_ENV:-default}"
SM120_EPOFF_BOTTLENECK_RUN_EPON_COMPARISON="${SM120_EPOFF_BOTTLENECK_RUN_EPON_COMPARISON:-0}"
SM120_EPOFF_BOTTLENECK_DRY_RUN="${SM120_EPOFF_BOTTLENECK_DRY_RUN:-0}"

case "${SM120_EPOFF_BOTTLENECK_RUN_EPON_COMPARISON}" in
  1|true|TRUE|yes|YES) run_epon_comparison=1 ;;
  0|false|FALSE|no|NO) run_epon_comparison=0 ;;
  *)
    echo "SM120_EPOFF_BOTTLENECK_RUN_EPON_COMPARISON must be 0/1 or true/false; got '${SM120_EPOFF_BOTTLENECK_RUN_EPON_COMPARISON}'" >&2
    exit 2
    ;;
esac

case "${SM120_EPOFF_BOTTLENECK_DRY_RUN}" in
  1|true|TRUE|yes|YES) dry_run=1 ;;
  0|false|FALSE|no|NO) dry_run=0 ;;
  *)
    echo "SM120_EPOFF_BOTTLENECK_DRY_RUN must be 0/1 or true/false; got '${SM120_EPOFF_BOTTLENECK_DRY_RUN}'" >&2
    exit 2
    ;;
esac

mkdir -p "${SM120_EPOFF_BOTTLENECK_ROOT}"

write_case_plan() {
  local case_name="$1"
  local case_out="$2"
  local expert_parallel="$3"
  local input_lens="$4"

  {
    printf 'OUT_DIR=%q\n' "${case_out}"
    printf 'SM12X_PREFILL_GAP_LABEL=%q\n' "${SM120_EPOFF_BOTTLENECK_LABEL}_${case_name}"
    printf 'SM12X_PREFILL_GAP_VARIANT=%q\n' "${SM120_EPOFF_BOTTLENECK_VARIANT}"
    printf 'SM12X_PREFILL_GAP_ENABLE_EXPERT_PARALLEL=%q\n' "${expert_parallel}"
    printf 'SM12X_PREFILL_GAP_INPUT_LENS=%q\n' "${input_lens}"
    printf 'SM12X_PREFILL_GAP_CONCURRENCY=%q\n' "${SM120_EPOFF_BOTTLENECK_CONCURRENCY}"
    printf 'SM12X_PREFILL_GAP_OUTPUT_LEN=%q\n' "${SM120_EPOFF_BOTTLENECK_OUTPUT_LEN}"
    printf 'SM12X_PREFILL_GAP_NUM_PROMPTS=%q\n' "${SM120_EPOFF_BOTTLENECK_NUM_PROMPTS}"
    printf 'SM12X_PREFILL_GAP_D512_ENV=%q\n' "${SM120_EPOFF_BOTTLENECK_D512_ENV}"
    printf 'SERVE_PREFIX_CACHE_MODE=disabled\n'
    printf 'GPU_TOPOLOGY_SLUG=%q\n' "${GPU_TOPOLOGY_SLUG}"
    printf 'scripts/run_sm12x_prefill_gap_attribution.sh\n'
  } > "${case_out}/planned_env.sh"
}

run_case() {
  local case_name="$1"
  local expert_parallel="$2"
  local input_lens="$3"
  local case_out="${SM120_EPOFF_BOTTLENECK_ROOT}/${case_name}"

  mkdir -p "${case_out}"
  write_case_plan "${case_name}" "${case_out}" "${expert_parallel}" "${input_lens}"
  if [[ "${dry_run}" == "1" ]]; then
    printf '%s\n' 0 > "${case_out}/case.exit_code"
    return 0
  fi

  set +e
  env \
    OUT_DIR="${case_out}" \
    SM120_VLLM_REPO="${SM120_VLLM_REPO}" \
    SM120_VLLM_VENV="${SM120_VLLM_VENV}" \
    SM120_PYTHON="${SM120_PYTHON}" \
    SM120_VLLM_BIN="${SM120_VLLM_BIN}" \
    B200_VLLM_REPO="${B200_VLLM_REPO}" \
    B200_VLLM_VENV="${B200_VLLM_VENV}" \
    PYTHON="${PYTHON}" \
    VLLM_BIN="${VLLM_BIN}" \
    VLLM_ROOT="${VLLM_ROOT}" \
    GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG}" \
    SM12X_PREFILL_GAP_LABEL="${SM120_EPOFF_BOTTLENECK_LABEL}_${case_name}" \
    SM12X_PREFILL_GAP_VARIANT="${SM120_EPOFF_BOTTLENECK_VARIANT}" \
    SM12X_PREFILL_GAP_ENABLE_EXPERT_PARALLEL="${expert_parallel}" \
    SM12X_PREFILL_GAP_INPUT_LENS="${input_lens}" \
    SM12X_PREFILL_GAP_CONCURRENCY="${SM120_EPOFF_BOTTLENECK_CONCURRENCY}" \
    SM12X_PREFILL_GAP_OUTPUT_LEN="${SM120_EPOFF_BOTTLENECK_OUTPUT_LEN}" \
    SM12X_PREFILL_GAP_NUM_PROMPTS="${SM120_EPOFF_BOTTLENECK_NUM_PROMPTS}" \
    SM12X_PREFILL_GAP_D512_ENV="${SM120_EPOFF_BOTTLENECK_D512_ENV}" \
    SERVE_PREFIX_CACHE_MODE=disabled \
    "${SCRIPT_DIR}/run_sm12x_prefill_gap_attribution.sh" \
      > "${case_out}/driver.stdout.log" \
      2> "${case_out}/driver.stderr.log"
  local code="$?"
  set -e
  printf '%s\n' "${code}" > "${case_out}/case.exit_code"
  return "${code}"
}

failures=0
epoff_code=0
run_case "epoff_control" 0 "${SM120_EPOFF_BOTTLENECK_INPUT_LENS}" || epoff_code="$?"
if [[ "${epoff_code}" != "0" ]]; then
  failures=1
fi

epon_code=""
if [[ "${run_epon_comparison}" == "1" ]]; then
  epon_code=0
  run_case "epon_comparison" 1 "${SM120_EPOFF_BOTTLENECK_EPON_INPUT_LENS}" || epon_code="$?"
  if [[ "${epon_code}" != "0" ]]; then
    failures=1
  fi
fi

summary_md="${SM120_EPOFF_BOTTLENECK_ROOT}/bottleneck_attribution_summary.md"
{
  printf '# SM120 EP-Off Bottleneck Attribution\n\n'
  printf -- '- OK: `%s`\n' "$([[ "${failures}" == "0" ]] && printf true || printf false)"
  printf -- '- Dry run: `%s`\n' "${dry_run}"
  printf -- '- Variant: `%s`\n' "${SM120_EPOFF_BOTTLENECK_VARIANT}"
  printf -- '- EP-off control exit: `%s`\n' "${epoff_code}"
  if [[ -n "${epon_code}" ]]; then
    printf -- '- EP-on comparison exit: `%s`\n' "${epon_code}"
  else
    printf -- '- EP-on comparison: `not run`\n'
  fi
  printf -- '- Root: `%s`\n' "${SM120_EPOFF_BOTTLENECK_ROOT}"
  printf '\n'
  printf 'Use `epoff_control/prefill_gap_attribution_summary.md` as the first bottleneck evidence.\n'
} > "${summary_md}"

summary_json="${SM120_EPOFF_BOTTLENECK_ROOT}/bottleneck_attribution_summary.json"
{
  printf '{\n'
  printf '  "ok": %s,\n' "$([[ "${failures}" == "0" ]] && printf true || printf false)"
  printf '  "dry_run": %s,\n' "$([[ "${dry_run}" == "1" ]] && printf true || printf false)"
  printf '  "variant": "%s",\n' "${SM120_EPOFF_BOTTLENECK_VARIANT}"
  printf '  "epoff_control_exit_code": %s,\n' "${epoff_code}"
  if [[ -n "${epon_code}" ]]; then
    printf '  "epon_comparison_exit_code": %s,\n' "${epon_code}"
  else
    printf '  "epon_comparison_exit_code": null,\n'
  fi
  printf '  "root": "%s"\n' "${SM120_EPOFF_BOTTLENECK_ROOT}"
  printf '}\n'
} > "${summary_json}"

echo "wrote ${SM120_EPOFF_BOTTLENECK_ROOT}"
exit "${failures}"
