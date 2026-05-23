#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
BRANCH_NAME="${BRANCH_NAME:-$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown-branch)}"
BRANCH_SLUG="$(printf '%s' "${BRANCH_NAME}" | sed -E 's#[/[:space:]]+#_#g; s#[^A-Za-z0-9_.-]#_#g')"
BRANCH_SLUG="${BRANCH_SLUG:-unknown-branch}"
GPU_TOPOLOGY_SLUG="${GPU_TOPOLOGY_SLUG:-$(detect_gpu_topology_slug)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"

PREFIX_CACHE_DIAGNOSTICS_LABEL="${PREFIX_CACHE_DIAGNOSTICS_LABEL:-sm120_mtp1_prefix_cache_diagnostics}"
PREFIX_CACHE_DIAGNOSTICS_ROOT="${OUT_DIR:-${ARTIFACT_ROOT}/${BRANCH_SLUG}/${GPU_TOPOLOGY_SLUG}/${PREFIX_CACHE_DIAGNOSTICS_LABEL}/${RUN_TIMESTAMP}}"
PREFIX_CACHE_DIAGNOSTIC_CASES="${PREFIX_CACHE_DIAGNOSTIC_CASES:-no_matmul_decode,launch_blocking,default}"

RUN_PREFIX_CACHE_STRESS="${RUN_PREFIX_CACHE_STRESS:-1}"
PREFIX_CACHE_STRESS_FILLER_WORDS="${PREFIX_CACHE_STRESS_FILLER_WORDS:-800}"
PREFIX_CACHE_STRESS_FILLER_WORDS_LIST="${PREFIX_CACHE_STRESS_FILLER_WORDS_LIST:-}"
PREFIX_CACHE_STRESS_TRIALS="${PREFIX_CACHE_STRESS_TRIALS:-5}"
PREFIX_CACHE_STRESS_TURNS="${PREFIX_CACHE_STRESS_TURNS:-3}"
PREFIX_CACHE_STRESS_MAX_TOKENS="${PREFIX_CACHE_STRESS_MAX_TOKENS:-256}"

mkdir -p "${PREFIX_CACHE_DIAGNOSTICS_ROOT}"
DIAGNOSTICS_MANIFEST="${PREFIX_CACHE_DIAGNOSTICS_ROOT}/diagnostic_cases.tsv"
printf '%s\t%s\t%s\t%s\n' "case" "filler_words" "exit_code" "artifact_dir" > "${DIAGNOSTICS_MANIFEST}"

failures=0

run_case() {
  local case_name="$1"
  local filler_words="$2"
  shift 2

  local case_slug child_out child_label code
  case_slug="$(slugify_context_value "${case_name}")"
  if [[ -n "${PREFIX_CACHE_STRESS_FILLER_WORDS_LIST}" ]]; then
    child_out="${PREFIX_CACHE_DIAGNOSTICS_ROOT}/${case_slug}/filler_${filler_words}"
  else
    child_out="${PREFIX_CACHE_DIAGNOSTICS_ROOT}/${case_slug}"
  fi
  child_label="${PREFIX_CACHE_DIAGNOSTICS_LABEL}_${case_slug}"

  set +e
  env \
    OUT_DIR="${child_out}" \
    B200_BASELINE_LABEL="${child_label}" \
    ARTIFACT_ARCHIVE_PREVIOUS=0 \
    RUN_PREFIX_CACHE_STRESS="${RUN_PREFIX_CACHE_STRESS}" \
    PREFIX_CACHE_STRESS_FILLER_WORDS="${filler_words}" \
    PREFIX_CACHE_STRESS_TRIALS="${PREFIX_CACHE_STRESS_TRIALS}" \
    PREFIX_CACHE_STRESS_TURNS="${PREFIX_CACHE_STRESS_TURNS}" \
    PREFIX_CACHE_STRESS_MAX_TOKENS="${PREFIX_CACHE_STRESS_MAX_TOKENS}" \
    "$@" \
    "${SCRIPT_DIR}/run_sm120_mtp1_prefix_cache_stability.sh"
  code="$?"
  set -e

  printf '%s\t%s\t%s\t%s\n' "${case_name}" "${filler_words}" "${code}" "${child_out}" >> "${DIAGNOSTICS_MANIFEST}"
  if [[ "${code}" != "0" ]]; then
    failures=1
  fi
}

if [[ -n "${PREFIX_CACHE_STRESS_FILLER_WORDS_LIST}" ]]; then
  IFS=',' read -r -a filler_words_entries <<< "${PREFIX_CACHE_STRESS_FILLER_WORDS_LIST}"
else
  filler_words_entries=("${PREFIX_CACHE_STRESS_FILLER_WORDS}")
fi

IFS=',' read -r -a diagnostic_cases <<< "${PREFIX_CACHE_DIAGNOSTIC_CASES}"
for raw_case in "${diagnostic_cases[@]}"; do
  case_name="$(printf '%s' "${raw_case}" | xargs)"
  for raw_filler_words in "${filler_words_entries[@]}"; do
    filler_words="$(printf '%s' "${raw_filler_words}" | xargs)"
    if [[ -z "${filler_words}" ]]; then
      continue
    fi
    case "${case_name}" in
      default)
        run_case "${case_name}" "${filler_words}"
        ;;
      launch_blocking)
        run_case "${case_name}" "${filler_words}" CUDA_LAUNCH_BLOCKING=1
        ;;
      no_matmul_decode)
        run_case "${case_name}" "${filler_words}" VLLM_TRITON_MLA_SPARSE_MATMUL_DECODE=0
        ;;
      "")
        ;;
      *)
        printf 'unknown PREFIX_CACHE_DIAGNOSTIC_CASES entry: %s\n' "${case_name}" >&2
        exit 2
        ;;
    esac
  done
done

printf 'wrote %s\n' "${PREFIX_CACHE_DIAGNOSTICS_ROOT}"
exit "${failures}"
