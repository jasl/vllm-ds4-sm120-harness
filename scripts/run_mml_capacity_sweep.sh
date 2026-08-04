#!/usr/bin/env bash
# Sweep max_model_len against KV capacity and COLD prefill latency.
#
# Answers two questions that are easy to get wrong by reasoning alone:
#
#  1. What does max_model_len actually cost? On DSv4-Flash it does NOT cost -- KV token
#     capacity rises with mml at constant memory (measured 2026-08-04: mml x5.33 ->
#     capacity x4.66, both topologies, same commit). mml is not a per-request
#     reservation; it is a structural parameter of the KV pool. So "cap the context to
#     buy concurrency" is a net loss. Re-run this before assuming that still holds after
#     a dependency bump or an attention-backend change.
#
#  2. How long is a COLD long prefill? Every llama-benchy --depth TTFT is prefix-CACHED
#     and understates this by more than 10x at 123k. See ds4_harness/cold_prefill_probe.py.
#
# Boot-and-measure only -- no throughput arms. Use run_topology_throughput_compare.sh
# for those.
#
# NOTE: `set -e` is deliberately NOT used. A refused boot at one mml is a RESULT (it is
# the discriminator between "capacity scales with mml" and "capacity is fixed"), and one
# failed cell must not discard the cells already collected.
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

SHA="${1:-${MML_SWEEP_SHA:-}}"
[ -n "${SHA}" ] || { echo "usage: $(basename "$0") <vllm-sha>" >&2; exit 2; }

MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}"
VLLM_ROOT="${VLLM_ROOT:?VLLM_ROOT (the vllm worktree) must be set}"
VLLM_VENV="${VLLM_VENV:?VLLM_VENV must be set}"
MML_SWEEP_VALUES="${MML_SWEEP_VALUES:-49152,131072,262144}"
MML_SWEEP_TOPOLOGIES="${MML_SWEEP_TOPOLOGIES:-tp2,tp4}"
MML_SWEEP_PROBE_FRACTIONS="${MML_SWEEP_PROBE_FRACTIONS:-8192,32768,131072}"
MML_SWEEP_OUT="${MML_SWEEP_OUT:-${HOME}/tmp/mml_sweep}"
MML_SWEEP_LOCK="${MML_SWEEP_LOCK:-${HOME}/tmp/.topo.lock}"

# Node layout. TP=2 uses the first pair; TP=4 uses all four.
SWEEP_HEAD="${SWEEP_HEAD:-10.0.0.116}"
SWEEP_TP2_WORKER="${SWEEP_TP2_WORKER:-10.0.0.119}"
SWEEP_TP4_WORKERS="${SWEEP_TP4_WORKERS:-10.0.0.119 10.0.0.117 10.0.0.118}"
SWEEP_ALL_NODES="${SWEEP_ALL_NODES:-10.0.0.116 10.0.0.117 10.0.0.118 10.0.0.119}"
ROCE_PREFIX="${ROCE_PREFIX:-192.168.100}"
ROCE_IFACE="${ROCE_IFACE:-enp1s0f0np0}"
NCCL_IB_HCA="${NCCL_IB_HCA:-rocep1s0f0}"

GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.85}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-64}"
MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS:-8192}"
KV_CACHE_DTYPE="${KV_CACHE_DTYPE:-fp8}"
SERVE_SPECULATIVE_CONFIG="${SERVE_SPECULATIVE_CONFIG:-{\"method\":\"dspark\",\"num_speculative_tokens\":5,\"draft_sample_method\":\"probabilistic\"}}"

export SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o BatchMode=yes}"
mkdir -p "${MML_SWEEP_OUT}"

# Single-instance guard. flock, NOT pgrep -f: pgrep matches its own ssh cmdline and a
# duplicate chain once corrupted four benchy blocks while every per-arm assertion passed.
exec 9>"${MML_SWEEP_LOCK}"
flock -n 9 || { echo "ABORT: another topology/sweep run holds ${MML_SWEEP_LOCK}"; exit 9; }

settle() {
  local node live w count
  for node in ${SWEEP_ALL_NODES}; do
    ssh -n ${SSH_OPTS} "jasl@${node}" \
      'pkill -KILL -f "[V]LLM::|[p]ython -m vllm.entrypoints.cli.main|[v]llm serve|[r]esource_tracker" 2>/dev/null; fuser -k 29519/tcp 2>/dev/null; fuser -k 8000/tcp 2>/dev/null; rm -f /dev/shm/psm_*' \
      </dev/null 2>/dev/null
  done
  for w in $(seq 1 60); do
    live=0
    for node in ${SWEEP_ALL_NODES}; do
      count=$(ssh -n ${SSH_OPTS} "jasl@${node}" \
        'pgrep -cf "[V]LLM::|[p]ython -m vllm.entrypoints.cli.main" | head -1' </dev/null 2>/dev/null)
      live=$((live + ${count:-0}))
    done
    [ "${live}" -eq 0 ] && return 0
    sleep 6
  done
  echo "  WARN: ${live} vllm processes still alive after settle"
}

# A checkout whose stderr is redirected away will silently leave the worktree wherever
# it already was, and `git rev-parse --short HEAD` then prints that stale SHA as if it
# were confirmation. This cost a full night's measurements on 2026-08-04. Assert.
cd "${VLLM_ROOT}" || { echo "ABORT: VLLM_ROOT ${VLLM_ROOT} unusable"; exit 1; }
git fetch -q origin "+refs/heads/*:refs/remotes/origin/*" 2>&1 | tail -1
git checkout -f "${SHA}" 2>&1 | tail -1 | sed 's/^/  checkout: /'
GOT="$(git rev-parse HEAD)"
case "${GOT}" in
  "${SHA}"*) echo "  head verified: $(git rev-parse --short HEAD)" ;;
  *) echo "ABORT: asked for ${SHA} but worktree is at ${GOT}"; exit 1 ;;
esac
echo "=== mml capacity sweep @ $(git rev-parse --short HEAD)  $(date) ==="

boot_and_measure() {
  local topo="$1" mml="$2"
  echo ""
  echo "######## ${topo} @ mml=${mml} ########"
  settle

  local run_dir="${HOME}/tmp/serve_sweep"
  rm -rf "${run_dir}"; mkdir -p "${run_dir}"
  local tag="${MML_SWEEP_OUT}/${topo}_${mml}"

  local common=(
    "MODEL_ID=${MODEL}" "VLLM_ROOT=${VLLM_ROOT}" "VLLM_VENV=${VLLM_VENV}"
    "ROCE_IFACE=${ROCE_IFACE}" "NCCL_IB_HCA=${NCCL_IB_HCA}"
    "HEAD_ROCE_IFACE=${ROCE_IFACE}" "HEAD_NCCL_IB_HCA=${NCCL_IB_HCA}"
    "WORKER_ROCE_IFACE=${ROCE_IFACE}" "WORKER_NCCL_IB_HCA=${NCCL_IB_HCA}"
    "SERVE_PREFIX_CACHE_MODE=on" "KV_CACHE_DTYPE=${KV_CACHE_DTYPE}"
    "GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION}"
    "MAX_MODEL_LEN=${mml}" "MAX_NUM_SEQS=${MAX_NUM_SEQS}"
    "MAX_NUM_BATCHED_TOKENS=${MAX_NUM_BATCHED_TOKENS}"
    "SERVE_SPECULATIVE_CONFIG=${SERVE_SPECULATIVE_CONFIG}"
    "ALLOW_CURRENT_BOOT_NVRM_OOM=1" "STARTUP_TIMEOUT=2400"
    "RUN_DIR=${run_dir}/serve"
  )

  if [ "${topo}" = tp4 ]; then
    local roce_workers=""
    for w in ${SWEEP_TP4_WORKERS}; do roce_workers="${roce_workers}${ROCE_PREFIX}.${w##*.} "; done
    env "${common[@]}" TP_SIZE=4 \
      HEAD_HOST="${SWEEP_HEAD}" WORKER_HOSTS="${SWEEP_TP4_WORKERS}" \
      HEAD_ROCE_IP="${ROCE_PREFIX}.${SWEEP_HEAD##*.}" \
      WORKER_ROCE_IPS="${roce_workers% }" \
      bash "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" > "${tag}.start.log" 2>&1
  else
    env "${common[@]}" TP_SIZE=2 \
      HEAD_HOST="${SWEEP_HEAD}" WORKER_HOST="${SWEEP_TP2_WORKER}" \
      HEAD_ROCE_IP="${ROCE_PREFIX}.${SWEEP_HEAD##*.}" \
      WORKER_ROCE_IP="${ROCE_PREFIX}.${SWEEP_TP2_WORKER##*.}" \
      bash "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" > "${tag}.start.log" 2>&1
  fi
  echo "  serve rc=$?"

  local head_log="${run_dir}/serve/head.log"
  cp "${head_log}" "${tag}.head.log" 2>/dev/null

  # "mml exceeds KV capacity" is the discriminating RESULT, not an error to chase.
  if grep -qaE "max seq len|larger than the maximum number of tokens" \
      "${tag}.start.log" "${head_log}" 2>/dev/null; then
    echo "  ==> REFUSED: mml=${mml} exceeds KV capacity for ${topo}"
    grep -ahoE "max seq len \([0-9]+\)[^.]*|larger than the maximum number of tokens[^.]*" \
      "${tag}.start.log" "${head_log}" 2>/dev/null | head -2 | sed 's/^/      /'
    settle; return 0
  fi

  grep -aoE "Available KV cache memory: [0-9.]+ GiB|GPU KV cache size: [0-9,]+ tokens|Model loading took [0-9.]+ GiB" \
    "${head_log}" 2>/dev/null | sort -u | sed 's/^/  /'

  if ! curl -sf -m 10 "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
    echo "  health: DOWN -- skipping cold prefill probe"
    grep -aiE "error|Traceback|out of memory" "${tag}.start.log" | tail -6 | cut -c1-150 | sed 's/^/    /'
    settle; return 0
  fi
  echo "  health: up"

  # Probe only lengths that fit this mml, leaving a little headroom for the template.
  local probes="" length
  for length in ${MML_SWEEP_PROBE_FRACTIONS//,/ }; do
    [ "${length}" -lt "$((mml - 2048))" ] && probes="${probes}${length},"
  done
  probes="${probes}$((mml - 2144))"

  echo "  --- cold prefill (uncached, exact length) ---"
  timeout 3600 "${VLLM_VENV}/bin/python" -m ds4_harness.cold_prefill_probe \
    --base-url "http://127.0.0.1:8000" --model "${MODEL}" --lengths "${probes}" \
    --json-output "${tag}.coldprefill.json" 2>&1 | tail -12
  settle
}

for mml in ${MML_SWEEP_VALUES//,/ }; do
  for topo in ${MML_SWEEP_TOPOLOGIES//,/ }; do
    boot_and_measure "${topo}" "${mml}"
  done
done

echo ""
echo "MML_SWEEP_DONE $(date)"
