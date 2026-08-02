#!/usr/bin/env bash
# DSv4 SM12x unit suite — the pytest files this branch's changes actually touch.
#
# This lived as a node-local scratch file, hand-copied and edited between
# sessions, until 2026-08-02. Two defects came directly out of that drift:
#
#   1. `ninja` was not on PATH, so every tests/compile/ case died with
#      FileNotFoundError -- 8 failures that read as a code regression and were
#      not one. (Fixed below; scripts/run_acceptance.sh already did this via
#      run_static_gate prepending `dirname $PYTHON`.)
#   2. tests/v1/spec_decode/test_dspark.py was never in the list, so a test
#      broken by upstream ecf4aa5ce2 stayed red across several shipped tags
#      without anyone noticing. A contributor found it, not us.
#
# Keep it in the repo so the list is reviewable and cannot silently shrink.
#
# Usage:
#   run_dsv4_unit_suite.sh                 # run against $VLLM_ROOT's current head
#   VLLM_ROOT=/path/to/vllm run_dsv4_unit_suite.sh
#
# Sections are grouped by what they defend, not by directory, so a reviewer can
# tell which ones a given change should move.
set -uo pipefail

VR="${VLLM_ROOT:-$HOME/tmp/ds4-sm120-harness/vllm}"
PY="${PYTHON:-$VR/.venv/bin/python}"

if [ ! -x "$PY" ]; then
  echo "FAIL: no interpreter at $PY (set PYTHON= or VLLM_ROOT=)" >&2
  exit 2
fi

# The venv's bin carries `ninja`, which inductor shells out to when it builds
# its C++ extensions. A non-interactive ssh does not have it on PATH, and the
# resulting failures look exactly like a code regression.
export PATH="$(dirname "$PY"):/usr/local/cuda/bin:$PATH"
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}"

cd "$VR" || exit 1
echo "=== $(hostname) DSv4 unit suite @ $(git rev-parse --short HEAD) $(date) ==="
command -v ninja >/dev/null || echo "  WARNING: ninja still not on PATH; tests/compile/ will fail spuriously"

fails=0
run() {
  local name="$1"; shift
  echo "### ${name} ###"
  local out
  out=$("$PY" -m pytest "$@" -q --no-header 2>&1)
  # Capture the FULL summary. An earlier incident tail-ed this and a "55 failed"
  # line scrolled past, nearly becoming a filed finding.
  echo "$out" | grep -aE '^FAILED|^ERROR|[0-9]+ (passed|failed|error)' | tail -10 | sed 's/^/  /'
  echo "$out" | grep -qaE '[0-9]+ failed|[0-9]+ error' && fails=$((fails + 1))
}

run "A. DSv4 kernels" \
  tests/kernels/attention/test_flashmla_sparse.py \
  tests/kernels/test_mhc_kernels.py \
  tests/kernels/test_fused_deepseek_v4_qnorm_rope_kv_insert.py

run "B. DSv4 attention backends" \
  tests/v1/attention/test_indexer_deepseek_v4_slot_mapping.py \
  tests/v1/attention/test_deepseek_v4_sparse_swa.py \
  tests/model_executor/test_deepseek_v4_sparse_mla_metadata.py

# test_dspark.py covers the V2-runner draft loader. It is NOT exercised by the
# V1 serve path we default to, which is precisely why it needs to be here.
run "C. spec decode / dspark" \
  tests/v1/spec_decode/test_dspark.py \
  tests/v1/spec_decode/test_dspark_config.py \
  tests/v1/spec_decode/test_rejection_sampler_utils.py \
  tests/v1/spec_decode/test_llm_base_proposer_sampling.py

run "D. kv offload" \
  tests/v1/kv_offload tests/v1/core/test_kv_cache_utils.py

run "E. core scheduler + prefix cache" \
  tests/v1/core/test_scheduler.py tests/v1/core/test_prefix_caching.py

run "F. kernel warmup" \
  tests/model_executor/test_deepseek_v4_kernel_warmup.py

run "G. DSv4 tokenizer / prompt encoding" \
  tests/tokenizers_/test_deepseek_v4.py

run "H. functionalization pass" \
  tests/compile/passes/test_functionalization.py

echo "=== ${fails} section(s) with failures ==="
echo "NOTE: section E's test_async_scheduling_pp_allows_rescheduling_with_output_placeholders"
echo "      needs 2 GPUs in one node and cannot pass on GB10 (one each)."
echo "DSV4_UNITS_DONE"
