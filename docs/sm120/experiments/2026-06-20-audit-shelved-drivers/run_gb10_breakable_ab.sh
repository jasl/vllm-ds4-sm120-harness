#!/usr/bin/env bash
# GB10 breakable-cudagraph re-enable A/B on 653a251d9e (#45309 revert in).
# Arm A: VLLM_USE_BREAKABLE_CUDAGRAPH=1 (overrides SM121 skip). Arm B: FULL_AND_PIECEWISE (current).
# Per arm: arithmetic correctness (does revert fix SM121 garbage?) + decode-throughput bench.
set -uo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"; load_harness_env
: "${HEAD_HOST:?}"; : "${WORKER_HOST:?}"; : "${VLLM_ROOT:?}"; : "${VLLM_VENV:?}"
API_PORT="${API_PORT:-8000}"; MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
TS="$(date +%Y%m%d%H%M%S)"; OUT="${OUT_DIR:-${REPO_ROOT}/artifacts/gb10_breakable_ab/${TS}}"; mkdir -p "${OUT}"
run_remote(){ ssh ${SSH_OPTS:-} -o ConnectTimeout=10 "$1" "$2"; }
stop_serve(){ for h in "${WORKER_HOST}" "${HEAD_HOST}"; do run_remote "$h" "pkill -TERM -f '[v]llm serve|[V]LLM::|[v]llm.entrypoints' 2>/dev/null; sleep 3; pkill -KILL -f '[v]llm serve|[V]LLM::|[v]llm.entrypoints' 2>/dev/null; true"; done; sleep 4; }
ask(){ local r; r=$(run_remote "${HEAD_HOST}" "curl -s --max-time 60 http://127.0.0.1:${API_PORT}/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\":\"${MODEL_ID}\",\"messages\":[{\"role\":\"user\",\"content\":\"$1\"}],\"max_tokens\":96,\"temperature\":0,\"chat_template_kwargs\":{\"enable_thinking\":false}}'" 2>/dev/null | "${LOCAL_PYTHON:-python3}" -c "import sys,json;print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null); echo "$r" | grep -q "$2" && echo "  PASS [$1] -> '$(echo "$r"|head -c 50)'" || echo "  FAIL [$1] -> '$(echo "$r"|head -c 110)'"; }

serve_arm(){ # $1=label  $2=breakable(0/1), $3=compilation-config
  local label="$1" breakable="$2" ccfg="$3"
  echo "===== ARM ${label}: start 2-node serve (breakable=${breakable}) ====="
  stop_serve
  local extra_env=()
  if [ "${breakable}" = "1" ]; then
    extra_env=(SERVE_REMOTE_ENV_VARS="VLLM_USE_BREAKABLE_CUDAGRAPH" VLLM_USE_BREAKABLE_CUDAGRAPH=1)
  fi
  set +e
  env HEAD_HOST="${HEAD_HOST}" WORKER_HOST="${WORKER_HOST}" HEAD_ROCE_IP="${HEAD_ROCE_IP}" WORKER_ROCE_IP="${WORKER_ROCE_IP}" \
    ROCE_IFACE="${ROCE_IFACE}" NCCL_IB_HCA="${NCCL_IB_HCA}" VLLM_ROOT="${VLLM_ROOT}" VLLM_VENV="${VLLM_VENV}" MODEL_ID="${MODEL_ID}" \
    TP_SIZE=2 PP_SIZE=1 MAX_MODEL_LEN=8192 GPU_MEMORY_UTILIZATION=0.70 MAX_NUM_SEQS=4 MAX_NUM_BATCHED_TOKENS=4176 \
    BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8 API_PORT="${API_PORT}" RUN_DIR="/home/jasl/tmp/gb10_breakable_${label}_${TS}" PREWARM_AFTER_HEALTH=0 \
    SERVE_COMPILATION_CONFIG="${ccfg}" ${extra_env[@]+"${extra_env[@]}"} SSH_OPTS="${SSH_OPTS:-}" \
    "${SCRIPT_DIR}/dgx_spark_start_mp_serve.sh" > "${OUT}/serve_${label}.stdout.log" 2> "${OUT}/serve_${label}.stderr.log"
  local rc=$?; set -e
  echo "serve_${label} exit=${rc}"
  [ "$rc" != 0 ] && { echo "SERVE FAILED ${label}; tail:"; tail -20 "${OUT}/serve_${label}.stderr.log"; return 1; }
  run_remote "${HEAD_HOST}" "grep -c 'Breakable CUDA graph enabled' /home/jasl/tmp/gb10_breakable_${label}_${TS}/serve/head.log 2>/dev/null" | xargs echo "  breakable_on_lines:"
  echo "  -- arithmetic (incl. the canonical jasl/vllm#14 SM121 repro prompt) --"; ask "2+2等于几" "4"; ask "2+2=" "4"; ask "What is 7*8?" "56"; ask "What is the capital of France?" "Paris"
  echo "  -- perf bench (random 2048x128, conc 4, 20 prompts) --"
  run_remote "${HEAD_HOST}" "cd /home/jasl && ${VLLM_VENV}/bin/vllm bench serve --backend vllm --model ${MODEL_ID} --base-url http://127.0.0.1:${API_PORT} --dataset-name random --random-input-len 2048 --random-output-len 128 --num-prompts 20 --max-concurrency 4 --ignore-eos --save-result --result-filename /home/jasl/tmp/gb10_breakable_${label}_${TS}.json > /home/jasl/tmp/gb10_breakable_${label}_bench.log 2>&1; echo bench_rc=\$?"
  run_remote "${HEAD_HOST}" "cat /home/jasl/tmp/gb10_breakable_${label}_${TS}.json" > "${OUT}/bench_${label}.json" 2>/dev/null || true
  "${LOCAL_PYTHON:-python3}" -c "import json;d=json.load(open('${OUT}/bench_${label}.json'));print('  PERF ${label}: out_tok/s',round(d['output_throughput'],1),'mean_tpot_ms',round(d['mean_tpot_ms'],2),'mean_ttft_ms',round(d['mean_ttft_ms'],1))" 2>/dev/null || echo "  (perf parse failed)"
  stop_serve
}

# NOTE: full arm (FULL_AND_PIECEWISE, EP off) already captured via live-serve salvage
# (out_tok/s 36.7, mean_tpot 76.96ms, arithmetic incl "2+2等于几" ALL PASS). Only breakable here.
serve_arm breakable 1 ''
echo "===== GB10 BREAKABLE A/B SUMMARY ====="
echo "full      (FULL_AND_PIECEWISE, EP off, salvaged): out_tok/s 36.7  mean_tpot_ms 76.96  arithmetic ALL PASS"
echo -n "breakable (VLLM_USE_BREAKABLE_CUDAGRAPH=1, EP off): "; "${LOCAL_PYTHON:-python3}" -c "import json;d=json.load(open('${OUT}/bench_breakable.json'));print('out_tok/s',round(d['output_throughput'],1),'mean_tpot_ms',round(d['mean_tpot_ms'],2))" 2>/dev/null || echo "(no bench)"
echo "GB10_BREAKABLE_AB_DONE OUT=${OUT}"
