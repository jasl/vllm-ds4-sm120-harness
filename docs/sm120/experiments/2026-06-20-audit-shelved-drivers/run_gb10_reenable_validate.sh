#!/usr/bin/env bash
# Validate the breakable-cudagraph re-enable (ccf4c0788e) on GB10/SM121:
# serve DEFAULT (no breakable env) -> the code must AUTO-enable breakable on
# SM121 -> confirm engaged + arithmetic ("2+2等于几") + GSM8K. EP off.
set -uo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"; load_harness_env
: "${HEAD_HOST:?}"; : "${WORKER_HOST:?}"; : "${VLLM_ROOT:?}"; : "${VLLM_VENV:?}"
API_PORT="${API_PORT:-8000}"; MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
TS="$(date +%Y%m%d%H%M%S)"; OUT="${REPO_ROOT}/artifacts/gb10_reenable_validate/${TS}"; mkdir -p "${OUT}"
REMOTE_RUN="/home/jasl/tmp/gb10_reenable_serve_${TS}"
HARNESS_REMOTE="/home/jasl/tmp/ds4-sm120-harness"
run_remote(){ ssh ${SSH_OPTS:-} -o ConnectTimeout=10 "$1" "$2"; }
stop_serve(){ for h in "${WORKER_HOST}" "${HEAD_HOST}"; do run_remote "$h" "pkill -TERM -f '[v]llm serve|[V]LLM::|[v]llm.entrypoints' 2>/dev/null; sleep 3; pkill -KILL -f '[v]llm serve|[V]LLM::|[v]llm.entrypoints' 2>/dev/null; true"; done; sleep 4; }
ask(){ local r; r=$(run_remote "${HEAD_HOST}" "curl -s --max-time 60 http://127.0.0.1:${API_PORT}/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\":\"${MODEL_ID}\",\"messages\":[{\"role\":\"user\",\"content\":\"$1\"}],\"max_tokens\":96,\"temperature\":0,\"chat_template_kwargs\":{\"enable_thinking\":false}}'" 2>/dev/null | python3 -c "import sys,json;print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null); echo "$r" | grep -q "$2" && echo "  PASS [$1] -> $(echo "$r"|head -c 55)" || echo "  FAIL [$1] -> $(echo "$r"|head -c 120)"; }

echo "OUT=${OUT}  REMOTE_RUN=${REMOTE_RUN}"
echo "=== start 2-node serve DEFAULT (no breakable env; code must auto-enable on SM121), EP off ==="
stop_serve
set +e
env HEAD_HOST="${HEAD_HOST}" WORKER_HOST="${WORKER_HOST}" HEAD_ROCE_IP="${HEAD_ROCE_IP}" WORKER_ROCE_IP="${WORKER_ROCE_IP}" \
  ROCE_IFACE="${ROCE_IFACE}" NCCL_IB_HCA="${NCCL_IB_HCA}" VLLM_ROOT="${VLLM_ROOT}" VLLM_VENV="${VLLM_VENV}" MODEL_ID="${MODEL_ID}" \
  TP_SIZE=2 PP_SIZE=1 MAX_MODEL_LEN=16384 GPU_MEMORY_UTILIZATION=0.70 MAX_NUM_SEQS=4 MAX_NUM_BATCHED_TOKENS=4176 \
  BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8 API_PORT="${API_PORT}" RUN_DIR="${REMOTE_RUN}/serve" PREWARM_AFTER_HEALTH=0 \
  SSH_OPTS="${SSH_OPTS:-}" \
  "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" > "${OUT}/serve_start.stdout.log" 2> "${OUT}/serve_start.stderr.log"
sc=$?; set -e
echo "serve_start exit=${sc}"
[ "$sc" != 0 ] && { echo "SERVE FAILED; tail:"; tail -20 "${OUT}/serve_start.stderr.log"; stop_serve; echo "GB10_REENABLE_VALIDATE_DONE (serve-failed)"; exit 1; }

echo "=== confirm breakable cudagraph AUTO-enabled (head.log) ==="
run_remote "${HEAD_HOST}" "grep -c 'Auto-enabling VLLM_USE_BREAKABLE_CUDAGRAPH' ${REMOTE_RUN}/serve/head.log 2>/dev/null" | xargs echo "  Auto-enabling lines:"
run_remote "${HEAD_HOST}" "grep -c 'Breakable CUDA graph enabled' ${REMOTE_RUN}/serve/head.log 2>/dev/null" | xargs echo "  Breakable-enabled lines:"

echo "=== arithmetic (canonical 2+2等于几 + others), default auto-breakable ==="
ask "2+2等于几" "4"; ask "2+2=" "4"; ask "What is 7*8?" "56"; ask "What is the capital of France?" "Paris"

echo "=== GSM8K nc=4 limit=100 (decode correctness w/ default auto-breakable) ==="
run_remote "${HEAD_HOST}" "cd ${HARNESS_REMOTE} && SERVER_GUARD=0 BASE_URL=http://127.0.0.1:${API_PORT} MODEL=${MODEL_ID} PYTHON=${VLLM_VENV}/bin/python LM_EVAL_BIN=${VLLM_VENV}/bin/lm_eval LM_EVAL_TASKS=gsm8k LM_EVAL_NUM_FEWSHOT=8 LM_EVAL_NUM_CONCURRENT=4 LM_EVAL_LIMIT=100 OUT_DIR=${REMOTE_RUN}/gsm8k bash scripts/run_lm_eval.sh > ${REMOTE_RUN}/gsm8k.log 2>&1; echo gsm8k_rc=\$?"
run_remote "${HEAD_HOST}" "cat ${REMOTE_RUN}/gsm8k/lm_eval_summary.json" > "${OUT}/gsm8k_summary.json" 2>/dev/null || true
python3 -c "import json;d=json.load(open('${OUT}/gsm8k_summary.json'));t=d['tasks'][0];print('  GSM8K strict',round(t['exact_match_strict'],4),'flex',round(t['exact_match_flexible'],4))" 2>/dev/null || echo "  (gsm8k parse failed)"

echo "=== teardown ==="; stop_serve
run_remote "${HEAD_HOST}" "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null|tr '\n' ' '" || true
echo "GB10_REENABLE_VALIDATE_DONE OUT=${OUT}"
