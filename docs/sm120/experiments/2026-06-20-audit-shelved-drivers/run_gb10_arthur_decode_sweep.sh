#!/usr/bin/env bash
# arthur decode-concurrency collapse re-eval on the rebased a93b9098b8 GB10 base.
# Serves 2-node (reusing dgx_spark_start_mp_serve.sh), runs a depth x concurrency
# vllm-bench-serve sweep measuring aggregate output (decode) tok/s == arthur's
# tg128 "total tok/s", then tears down. CONSERVATIVE: caps at 32k/c5, ordered
# safe->risky, per-cell timeout, to avoid the 65k x c10 OOM-wedge regime.
set -uo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env

: "${HEAD_HOST:?}"; : "${WORKER_HOST:?}"; : "${VLLM_ROOT:?}"; : "${VLLM_VENV:?}"
API_PORT="${API_PORT:-8000}"
MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
TS="$(date +%Y%m%d%H%M%S)"
OUT="${OUT_DIR:-${REPO_ROOT}/artifacts/arthur_decode_sweep/${TS}}"
mkdir -p "${OUT}"
REMOTE_RUN="/home/jasl/tmp/arthur_decode_sweep_${TS}"
DEPTHS="${DEPTHS:-128 4096 8192 16384 32768}"
CONCS="${CONCS:-1 2 5}"
BENCH_TIMEOUT="${BENCH_TIMEOUT:-300}"
echo "OUT=${OUT}  HEAD=${HEAD_HOST} WORKER=${WORKER_HOST}  depths=[${DEPTHS}] concs=[${CONCS}]"

run_remote() { ssh ${SSH_OPTS:-} -o ConnectTimeout=10 "$1" "$2"; }
stop_serve() {
  for h in "${WORKER_HOST}" "${HEAD_HOST}"; do
    run_remote "$h" "pkill -TERM -f '[v]llm serve|[V]LLM::|[v]llm.entrypoints' 2>/dev/null; sleep 3; pkill -KILL -f '[v]llm serve|[V]LLM::|[v]llm.entrypoints' 2>/dev/null; true"
  done
}

echo "=== pre-clean any stale serve ==="; stop_serve; sleep 3

echo "=== start 2-node serve (nomtp, MAX_NUM_SEQS=5, MAX_MODEL_LEN=49152, gpu-mem 0.70) ==="
set +e
env \
  HEAD_HOST="${HEAD_HOST}" WORKER_HOST="${WORKER_HOST}" \
  HEAD_ROCE_IP="${HEAD_ROCE_IP}" WORKER_ROCE_IP="${WORKER_ROCE_IP}" \
  ROCE_IFACE="${ROCE_IFACE}" NCCL_IB_HCA="${NCCL_IB_HCA}" \
  VLLM_ROOT="${VLLM_ROOT}" VLLM_VENV="${VLLM_VENV}" MODEL_ID="${MODEL_ID}" \
  TP_SIZE=2 PP_SIZE=1 MAX_MODEL_LEN=49152 GPU_MEMORY_UTILIZATION=0.70 \
  MAX_NUM_SEQS=5 MAX_NUM_BATCHED_TOKENS=8192 BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8 \
  API_PORT="${API_PORT}" RUN_DIR="${REMOTE_RUN}/serve" PREWARM_AFTER_HEALTH=0 \
  SERVE_PREFIX_CACHE_MODE=auto \
  SSH_OPTS="${SSH_OPTS:-}" \
  "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" \
    > "${OUT}/serve_start.stdout.log" 2> "${OUT}/serve_start.stderr.log"
start_code=$?
set -e
echo "serve_start exit=${start_code}"
if [[ "${start_code}" != "0" ]]; then
  echo "SERVE START FAILED; tail stderr:"; tail -25 "${OUT}/serve_start.stderr.log"
  stop_serve; echo "ARTHUR_SWEEP_DONE (serve-failed)"; exit 1
fi

echo "=== sweep: depth x concurrency (safe->risky), measuring aggregate output tok/s ==="
printf "%-8s %-4s %14s %12s %12s\n" depth conc out_tok/s mean_tpot_ms p99_tpot_ms | tee "${OUT}/summary.txt"
for depth in ${DEPTHS}; do
  for c in ${CONCS}; do
    np=$(( c * 4 )); [ "$np" -lt 4 ] && np=4
    label="d${depth}_c${c}"
    rj="${REMOTE_RUN}/${label}.json"
    run_remote "${HEAD_HOST}" "cd /home/jasl && timeout ${BENCH_TIMEOUT} ${VLLM_VENV}/bin/vllm bench serve --backend vllm \
      --model ${MODEL_ID} --base-url http://127.0.0.1:${API_PORT} \
      --dataset-name random --random-input-len ${depth} --random-output-len 128 \
      --num-prompts ${np} --max-concurrency ${c} --ignore-eos \
      --save-result --result-filename ${rj} > /home/jasl/tmp/${label}.benchlog 2>&1; echo BENCH_RC=\$?"
    row=$(run_remote "${HEAD_HOST}" "${VLLM_VENV}/bin/python -c \"import json;d=json.load(open('${rj}'));print(round(d['output_throughput'],1),round(d['mean_tpot_ms'],2),round(d['p99_tpot_ms'],2))\" 2>/dev/null || echo 'NA NA NA'")
    printf "%-8s %-4s %14s %12s %12s\n" "$depth" "$c" $row | tee -a "${OUT}/summary.txt"
    run_remote "${HEAD_HOST}" "test -f ${rj} && cat ${rj}" > "${OUT}/${label}.json" 2>/dev/null || true
  done
done

echo "=== teardown ==="; stop_serve; sleep 5
run_remote "${HEAD_HOST}" "nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader 2>/dev/null" || true
echo "=== ARTHUR DECODE SWEEP SUMMARY ==="; cat "${OUT}/summary.txt"
echo "ARTHUR_SWEEP_DONE OUT=${OUT}"
