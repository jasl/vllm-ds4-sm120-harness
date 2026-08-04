#!/usr/bin/env bash
# Compare serving topologies at MATCHED TOTAL concurrency.
#
#   run_topology_throughput_compare.sh <sha> tp4    # one 4-node TP=4 replica
#   run_topology_throughput_compare.sh <sha> tp2    # TWO 2-node TP=2 replicas, together
#
# The comparison only means anything if total concurrency matches: TP=4 at c=8 against
# 2x TP=2 at c=4+4. And the two TP=2 replicas MUST be benchmarked simultaneously -- they
# share one CRS804 switch, so measuring them one at a time hands each the whole fabric
# and flatters the two-replica option.
#
# Measured 2026-08-04 on 0f59188db1: 2x TP=2 leads by ~66% prefill, ~40% decode, -31%
# TTFT, stable across mml 49152/131072 and depth 16384/32768, with zero preemptions.
# TP=4 wins only single-request COLD prefill (+14-24%, see run_mml_capacity_sweep.sh) --
# one request can use all four nodes, whereas at concurrency the 4-node all-reduce
# overhead dominates. Both topologies saturate at total concurrency ~8.
#
# NOTE: `set -e` is deliberately NOT used -- one failed cell must not discard the rest.
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

SHA="${1:?usage: $(basename "$0") <vllm-sha> tp4|tp2}"
MODE="${2:?usage: $(basename "$0") <vllm-sha> tp4|tp2}"
case "${MODE}" in tp2|tp4) ;; *) echo "mode must be tp4 or tp2" >&2; exit 2 ;; esac

MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}"
VLLM_ROOT="${VLLM_ROOT:?VLLM_ROOT (the vllm worktree) must be set}"
VLLM_VENV="${VLLM_VENV:?VLLM_VENV must be set}"
TOPO_OUT="${TOPO_OUT:-${HOME}/tmp/topo_tp/${MODE}}"
TOPO_LOCK="${TOPO_LOCK:-${HOME}/tmp/.topo.lock}"
TOPO_MAX_MODEL_LEN="${TOPO_MAX_MODEL_LEN:-131072}"
TOPO_DEPTHS="${TOPO_DEPTHS:-16384,32768}"
# Per-replica concurrency for tp2; these are DOUBLED for the total. tp4 uses the totals.
TOPO_TP2_CONCURRENCY="${TOPO_TP2_CONCURRENCY:-4,8}"
TOPO_TP4_CONCURRENCY="${TOPO_TP4_CONCURRENCY:-8,16}"
TOPO_RUNS="${TOPO_RUNS:-2}"

TOPO_REPLICA_A="${TOPO_REPLICA_A:-10.0.0.116:10.0.0.119}"
TOPO_REPLICA_B="${TOPO_REPLICA_B:-10.0.0.117:10.0.0.118}"
TOPO_TP4_HEAD="${TOPO_TP4_HEAD:-10.0.0.116}"
TOPO_TP4_WORKERS="${TOPO_TP4_WORKERS:-10.0.0.119 10.0.0.117 10.0.0.118}"
TOPO_ALL_NODES="${TOPO_ALL_NODES:-10.0.0.116 10.0.0.117 10.0.0.118 10.0.0.119}"
ROCE_PREFIX="${ROCE_PREFIX:-192.168.100}"
ROCE_IFACE="${ROCE_IFACE:-enp1s0f0np0}"
NCCL_IB_HCA="${NCCL_IB_HCA:-rocep1s0f0}"

GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.85}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-64}"
MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS:-8192}"
KV_CACHE_DTYPE="${KV_CACHE_DTYPE:-fp8}"
SERVE_SPECULATIVE_CONFIG="${SERVE_SPECULATIVE_CONFIG:-{\"method\":\"dspark\",\"num_speculative_tokens\":5,\"draft_sample_method\":\"probabilistic\"}}"
LLAMA_BENCHY="${LLAMA_BENCHY:-uvx --from git+https://github.com/eugr/llama-benchy@b220b7c9cae7af2d6bd9ebf6bfa9ac066cb40780 llama-benchy}"

export SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o BatchMode=yes}"
mkdir -p "${TOPO_OUT}"

exec 9>"${TOPO_LOCK}"
flock -n 9 || { echo "ABORT: another topology/sweep run holds ${TOPO_LOCK}"; exit 9; }

settle() {
  local node live w count
  for node in ${TOPO_ALL_NODES}; do
    ssh -n ${SSH_OPTS} "jasl@${node}" \
      'pkill -KILL -f "[V]LLM::|[p]ython -m vllm.entrypoints.cli.main|[v]llm serve|[r]esource_tracker" 2>/dev/null; fuser -k 29519/tcp 2>/dev/null; fuser -k 8000/tcp 2>/dev/null; rm -f /dev/shm/psm_*' \
      </dev/null 2>/dev/null
  done
  for w in $(seq 1 60); do
    live=0
    for node in ${TOPO_ALL_NODES}; do
      count=$(ssh -n ${SSH_OPTS} "jasl@${node}" \
        'pgrep -cf "[V]LLM::|[p]ython -m vllm.entrypoints.cli.main" | head -1' </dev/null 2>/dev/null)
      live=$((live + ${count:-0}))
    done
    [ "${live}" -eq 0 ] && return 0
    sleep 6
  done
  echo "  WARN: ${live} vllm processes still alive after settle"
}

serve_env() {
  echo "MODEL_ID=${MODEL} VLLM_ROOT=${VLLM_ROOT} VLLM_VENV=${VLLM_VENV} \
ROCE_IFACE=${ROCE_IFACE} NCCL_IB_HCA=${NCCL_IB_HCA} \
HEAD_ROCE_IFACE=${ROCE_IFACE} HEAD_NCCL_IB_HCA=${NCCL_IB_HCA} \
WORKER_ROCE_IFACE=${ROCE_IFACE} WORKER_NCCL_IB_HCA=${NCCL_IB_HCA} \
SERVE_PREFIX_CACHE_MODE=on KV_CACHE_DTYPE=${KV_CACHE_DTYPE} \
GPU_MEMORY_UTILIZATION=${GPU_MEMORY_UTILIZATION} \
MAX_MODEL_LEN=${TOPO_MAX_MODEL_LEN} MAX_NUM_SEQS=${MAX_NUM_SEQS} \
MAX_NUM_BATCHED_TOKENS=${MAX_NUM_BATCHED_TOKENS} \
ALLOW_CURRENT_BOOT_NVRM_OOM=1 STARTUP_TIMEOUT=2400"
}

cd "${VLLM_ROOT}" || { echo "ABORT: VLLM_ROOT ${VLLM_ROOT} unusable"; exit 1; }
git fetch -q origin "+refs/heads/*:refs/remotes/origin/*" 2>&1 | tail -1
git checkout -f "${SHA}" 2>&1 | tail -1 | sed 's/^/  checkout: /'
GOT="$(git rev-parse HEAD)"
case "${GOT}" in
  "${SHA}"*) echo "  head verified: $(git rev-parse --short HEAD)" ;;
  *) echo "ABORT: asked for ${SHA} but worktree is at ${GOT}"; exit 1 ;;
esac
echo "=== topology throughput [${MODE}] @ $(git rev-parse --short HEAD) mml=${TOPO_MAX_MODEL_LEN} $(date) ==="
settle

if [ "${MODE}" = tp4 ]; then
  RUN_DIR_ROOT="${HOME}/tmp/serve_topo_t4"; rm -rf "${RUN_DIR_ROOT}"; mkdir -p "${RUN_DIR_ROOT}"
  roce_workers=""
  for w in ${TOPO_TP4_WORKERS}; do roce_workers="${roce_workers}${ROCE_PREFIX}.${w##*.} "; done
  env $(serve_env) TP_SIZE=4 \
    HEAD_HOST="${TOPO_TP4_HEAD}" WORKER_HOSTS="${TOPO_TP4_WORKERS}" \
    HEAD_ROCE_IP="${ROCE_PREFIX}.${TOPO_TP4_HEAD##*.}" \
    WORKER_ROCE_IPS="${roce_workers% }" \
    SERVE_SPECULATIVE_CONFIG="${SERVE_SPECULATIVE_CONFIG}" \
    RUN_DIR="${RUN_DIR_ROOT}/serve" \
    bash "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" > "${TOPO_OUT}/start.log" 2>&1
  echo "  serve rc=$?"
  grep -aoE "GPU KV cache size: [0-9,]+ tokens" "${RUN_DIR_ROOT}/serve/head.log" | tail -1 | sed 's/^/  /'

  for depth in ${TOPO_DEPTHS//,/ }; do
    for conc in ${TOPO_TP4_CONCURRENCY//,/ }; do
      echo "--- TP=4, depth ${depth}, total concurrency ${conc} ---"
      ${LLAMA_BENCHY} --base-url http://127.0.0.1:8000/v1 \
        --served-model-name "${MODEL}" --tokenizer "${MODEL}" \
        --pp 2048 --tg 128 --depth "${depth}" --concurrency "${conc}" \
        --runs "${TOPO_RUNS}" --enable-prefix-caching --skip-coherence \
        > "${TOPO_OUT}/lb_d${depth}_c${conc}.out" 2>&1
      grep -ahE "\| *(pp2048|tg128) @ d" "${TOPO_OUT}/lb_d${depth}_c${conc}.out" | sed 's/^/      /'
    done
  done
  echo "      preemption lines: $(grep -ac preempt "${RUN_DIR_ROOT}/serve/head.log" 2>/dev/null)"
else
  # Both replicas up at once, then driven concurrently.
  for spec in "${TOPO_REPLICA_A}:A" "${TOPO_REPLICA_B}:B"; do
    head="${spec%%:*}"; rest="${spec#*:}"; worker="${rest%%:*}"; tag="${spec##*:}"
    run_dir="${HOME}/tmp/serve_topo_t2${tag}"; rm -rf "${run_dir}"; mkdir -p "${run_dir}"
    # 9>&- : without it these children inherit the flock fd and outlive a kill of this
    # script, leaving the lock held by orphans and blocking the next run against itself.
    env $(serve_env) TP_SIZE=2 HEAD_HOST="${head}" WORKER_HOST="${worker}" \
      HEAD_ROCE_IP="${ROCE_PREFIX}.${head##*.}" WORKER_ROCE_IP="${ROCE_PREFIX}.${worker##*.}" \
      SERVE_SPECULATIVE_CONFIG="${SERVE_SPECULATIVE_CONFIG}" \
      RUN_DIR="${run_dir}/serve" \
      bash "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" > "${TOPO_OUT}/start_${tag}.log" 2>&1 9>&- &
  done
  wait

  for spec in "${TOPO_REPLICA_A}:A" "${TOPO_REPLICA_B}:B"; do
    head="${spec%%:*}"; tag="${spec##*:}"
    # Read capacity off the replica's own head node, and check health rather than
    # trusting the log -- a booted-looking serve that will not answer is not up.
    ssh -n ${SSH_OPTS} "jasl@${head}" \
      "grep -aoE 'GPU KV cache size: [0-9,]+ tokens' ${HOME}/tmp/serve_topo_t2${tag}/serve/head.log 2>/dev/null | tail -1" \
      </dev/null 2>/dev/null | sed "s/^/  replica ${tag}: /"
    ok=$(ssh -n ${SSH_OPTS} "jasl@${head}" \
      'curl -sf -m 5 http://127.0.0.1:8000/health >/dev/null 2>&1 && echo up || echo down' </dev/null 2>/dev/null)
    echo "  replica ${tag} health: ${ok:-down}"
  done

  for depth in ${TOPO_DEPTHS//,/ }; do
    for conc in ${TOPO_TP2_CONCURRENCY//,/ }; do
      echo "--- 2x TP=2, depth ${depth}, c=${conc} per replica (total $((conc * 2))) ---"
      for spec in "${TOPO_REPLICA_A}:A" "${TOPO_REPLICA_B}:B"; do
        head="${spec%%:*}"; tag="${spec##*:}"
        ssh -n ${SSH_OPTS} "jasl@${head}" \
          "export PATH=\$HOME/.local/bin:\$PATH; ${LLAMA_BENCHY} \
            --base-url http://127.0.0.1:8000/v1 --served-model-name '${MODEL}' \
            --tokenizer '${MODEL}' --pp 2048 --tg 128 --depth ${depth} \
            --concurrency ${conc} --runs ${TOPO_RUNS} --enable-prefix-caching \
            --skip-coherence > ${HOME}/tmp/lb_topo_${tag}_d${depth}_c${conc}.out 2>&1" \
          </dev/null 2>/dev/null 9>&- &
      done
      wait
      for spec in "${TOPO_REPLICA_A}:A" "${TOPO_REPLICA_B}:B"; do
        head="${spec%%:*}"; tag="${spec##*:}"
        echo "    replica ${tag}:"
        ssh -n ${SSH_OPTS} "jasl@${head}" \
          "grep -ahE '\| *(pp2048|tg128) @ d' ${HOME}/tmp/lb_topo_${tag}_d${depth}_c${conc}.out" \
          </dev/null 2>/dev/null | sed 's/^/      /'
        scp -o BatchMode=yes "jasl@${head}:${HOME}/tmp/lb_topo_${tag}_d${depth}_c${conc}.out" \
          "${TOPO_OUT}/" >/dev/null 2>&1
        # Preemption is how a too-small KV pool shows up -- it does not raise an error.
        ssh -n ${SSH_OPTS} "jasl@${head}" \
          "grep -ac preempt ${HOME}/tmp/serve_topo_t2${tag}/serve/head.log 2>/dev/null" \
          </dev/null 2>/dev/null | sed "s/^/      replica ${tag} preemption lines: /"
      done
    done
  done
fi

settle
echo "TOPO_COMPARE_DONE ${MODE} $(date)"
