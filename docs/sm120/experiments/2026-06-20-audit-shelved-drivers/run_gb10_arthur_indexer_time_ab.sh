#!/usr/bin/env bash
# Indexer decode-cost A/B on the rebased build: measures the eager sparse-MLA
# decode indexer's per-step GPU time (CUDA-event timed, VLLM_DEEPSEEK_V4_TIME_INDEXER)
# with the decode-width cap OFF vs ON (VLLM_DEEPSEEK_V4_INDEXER_DECODE_WIDTH_CAP).
# Two serves (cap=0, cap=1), both timed, over focused cliff cells (pure decode).
# The [indexer-time] head.log lines give mean_ms per (rows, width) key, which
# uniquely identifies each cell's C4 indexer layers -> direct mechanism proof
# that the cap cheapens the indexer, free of end-to-end serve noise.
set -uo pipefail
H="${H:-/home/jasl/tmp/ds4-sm120-harness}"
WT="${WT:-/home/jasl/tmp/vllm-pr-rebased-20260620}"
VENV="${VENV:-$H/vllm/.venv}"
SCRIPT_DIR="$H/scripts"
HEAD="${HEAD:-10.0.0.116}"; WORKER="${WORKER:-10.0.0.118}"
SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o BatchMode=yes}"
PORT="${PORT:-8000}"
MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
RUN="${RUN:-/home/jasl/tmp/arthur_indexer_time_ab/$(date +%Y%m%d%H%M%S)}"; mkdir -p "$RUN"
DEPTHS="${DEPTHS:-8192 16384 32768}"
CONCS="${CONCS:-1 5}"
OUTLEN="${OUTLEN:-128}"
BENCH_TIMEOUT="${BENCH_TIMEOUT:-360}"

echo "=== indexer-time A/B -> $RUN  (build $(cat $WT/REBASED_COMMIT.txt 2>/dev/null|head -c14)) ==="
run_remote(){ ssh $SSH_OPTS "$1" "$2"; }
stop(){ for h in "$WORKER" "$HEAD"; do run_remote "$h" "pkill -TERM -f '[v]llm serve|[V]LLM::|[E]ngineCore' 2>/dev/null; sleep 3; pkill -KILL -f '[v]llm serve|[V]LLM::|[E]ngineCore' 2>/dev/null; true"; done; }
trap stop EXIT INT TERM

for CAP in 0 1; do
  echo "############### CAP=$CAP ###############"
  stop; sleep 3
  SR="$RUN/cap${CAP}"; mkdir -p "$SR"
  set +e
  env HEAD_HOST="$HEAD" WORKER_HOST="$WORKER" \
    HEAD_ROCE_IP=169.254.122.42 WORKER_ROCE_IP=169.254.253.112 \
    ROCE_IFACE=enp1s0f0np0 NCCL_IB_HCA=rocep1s0f0 \
    VLLM_ROOT="$WT" VLLM_VENV="$VENV" MODEL_ID="$MODEL_ID" \
    TP_SIZE=2 PP_SIZE=1 MAX_MODEL_LEN=49152 GPU_MEMORY_UTILIZATION=0.70 \
    MAX_NUM_SEQS=5 MAX_NUM_BATCHED_TOKENS=8192 BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8 \
    API_PORT="$PORT" RUN_DIR="$SR/serve" PREWARM_AFTER_HEALTH=0 \
    SERVE_PREFIX_CACHE_MODE=auto ALLOW_CURRENT_BOOT_NVRM_OOM=1 \
    VLLM_DEEPSEEK_V4_TIME_INDEXER=1 VLLM_DEEPSEEK_V4_INDEXER_DECODE_WIDTH_CAP=$CAP \
    SERVE_REMOTE_ENV_VARS="VLLM_DEEPSEEK_V4_TIME_INDEXER,VLLM_DEEPSEEK_V4_INDEXER_DECODE_WIDTH_CAP" \
    SSH_OPTS="$SSH_OPTS" \
    bash "$SCRIPT_DIR/dgx_spark_start_mp_serve.sh" > "$SR/serve_start.log" 2>&1
  set -e
  ok=0; for i in $(seq 1 360); do [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HEAD:$PORT/health 2>/dev/null)" = 200 ] && { ok=1; echo "serve UP ~$((i*10))s"; break; }; sleep 10; done
  [ "$ok" = 1 ] || { echo "HEALTH FAIL cap=$CAP"; tail -25 "$SR/serve_start.log"; continue; }
  printf "%-8s %-4s %12s %12s\n" depth conc tpot_ms ttft_ms | tee "$SR/tpot.txt"
  for depth in $DEPTHS; do for c in $CONCS; do
    label="d${depth}_c${c}"; rj="/home/jasl/tmp/it_${label}.json"
    run_remote "$HEAD" "cd /home/jasl && timeout $BENCH_TIMEOUT $VENV/bin/vllm bench serve --backend vllm \
      --model $MODEL_ID --base-url http://127.0.0.1:$PORT --dataset-name random \
      --random-input-len $depth --random-output-len $OUTLEN --num-prompts $c --max-concurrency $c \
      --ignore-eos --save-result --result-filename $rj > /home/jasl/tmp/it_${label}.log 2>&1; echo done" >/dev/null 2>&1
    row=$(run_remote "$HEAD" "$VENV/bin/python -c \"import json;d=json.load(open('$rj'));print(round(d['mean_tpot_ms'],2),round(d['mean_ttft_ms'],1))\" 2>/dev/null" || echo 'NA NA')
    printf "%-8s %-4s %12s %12s\n" "$depth" "$c" $row | tee -a "$SR/tpot.txt"
  done; done
  echo "=== indexer-time lines (cap=$CAP) ==="
  run_remote "$HEAD" "grep -h '\[indexer-time\]' $SR/serve/head.log 2>/dev/null" > "$SR/indexer_time.txt" 2>/dev/null || true
  # aggregate: mean of mean_ms per (rows,width)
  "$VENV/bin/python" - "$SR/indexer_time.txt" > "$SR/indexer_time_agg.txt" 2>/dev/null <<'PY' || true
import sys,re,collections
acc=collections.defaultdict(list)
for ln in open(sys.argv[1]):
    m=re.search(r'rows=(\d+) width=(\d+) calls=(\d+) mean_ms=([\d.]+)',ln)
    if m: acc[(int(m.group(1)),int(m.group(2)))].append(float(m.group(4)))
for k in sorted(acc):
    v=acc[k]; print(f"rows={k[0]:<3} width={k[1]:<6} samples={len(v):<3} mean_ms={sum(v)/len(v):.4f}")
PY
  cat "$SR/indexer_time_agg.txt" 2>/dev/null | tee "$SR/indexer_time_agg.shown"
  stop; sleep 4
done

echo "=== teardown + summary ==="; stop; sleep 3
echo "############### SUMMARY ###############"
for CAP in 0 1; do echo "--- cap=$CAP TPOT ---"; cat "$RUN/cap${CAP}/tpot.txt" 2>/dev/null; echo "--- cap=$CAP indexer mean_ms per (rows,width) ---"; cat "$RUN/cap${CAP}/indexer_time_agg.txt" 2>/dev/null; done
echo "INDEXER_TIME_AB_DONE RUN=$RUN"
