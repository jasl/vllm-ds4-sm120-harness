#!/usr/bin/env bash
# arthur decode-concurrency-collapse REPRODUCE + ATTRIBUTION on the rebased
# 88ec87e1e0 GB10 build (source-shadow over e57276b554 .so; pure-Python delta).
#
# One 2-node nomtp serve, identical config to run_gb10_arthur_decode_sweep.sh
# (MML=49152 seqs=5 gpu0.70 mbt=8192 block256 fp8 prefix=auto) so the ROLLING
# decode tok/s is directly comparable to the historical a93b9098b8 curve. For
# each depth x conc cell we measure TWO bench modes on the SAME serve:
#   rolling : --num-prompts c*4  (rolling admission; new long prefills interleave
#             with in-flight decodes -> captures scheduler interleave + indexer)
#   pure    : --num-prompts c    (all c arrive at once; after the initial cohort
#             prefill there are NO new arrivals -> steady-state concurrent decode
#             -> isolates the eager O(batch x ctx) indexer cost)
# Comparing rolling-vs-pure TPOT at the cliff cells attributes the collapse to
# scheduler prefill/decode interleave (rolling >> pure) vs the indexer amplifier
# (rolling ~= pure, both balloon with depth).
#
# Run ON the head node (self-ssh to HEAD, ssh to WORKER). Self-contained,
# modelled on recall_v2_drivers/gb10_regression_rebased.sh. CONSERVATIVE: caps at
# 32k/c5, depth-ascending (safe->risky), per-cell timeout, to avoid OOM/freeze.
set -uo pipefail
H="${H:-/home/jasl/tmp/ds4-sm120-harness}"
WT="${WT:-/home/jasl/tmp/vllm-pr-rebased-20260620}"
VENV="${VENV:-$H/vllm/.venv}"
SCRIPT_DIR="$H/scripts"
HEAD="${HEAD:-10.0.0.116}"; WORKER="${WORKER:-10.0.0.118}"
SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o BatchMode=yes}"
PORT="${PORT:-8000}"
MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
TS="$(date +%Y%m%d%H%M%S)"
RUN="${RUN:-/home/jasl/tmp/arthur_cliff_attrib/$TS}"; mkdir -p "$RUN"
DEPTHS="${DEPTHS:-128 8192 16384 32768}"
CONCS="${CONCS:-1 2 5}"
MODES="${MODES:-rolling pure}"
BENCH_TIMEOUT="${BENCH_TIMEOUT:-360}"
OUTLEN="${OUTLEN:-128}"

echo "=== arthur cliff attrib -> $RUN  (build $(cat $WT/REBASED_COMMIT.txt 2>/dev/null | head -c 14)) ==="
echo "    depths=[$DEPTHS] concs=[$CONCS] modes=[$MODES] outlen=$OUTLEN"
run_remote(){ ssh $SSH_OPTS "$1" "$2"; }
stop(){
  for h in "$WORKER" "$HEAD"; do
    run_remote "$h" "pkill -TERM -f '[v]llm serve|[V]LLM::|[E]ngineCore|[v]llm.entrypoints' 2>/dev/null; sleep 3; pkill -KILL -f '[v]llm serve|[V]LLM::|[E]ngineCore|[v]llm.entrypoints' 2>/dev/null; true"
  done
}
trap stop EXIT INT TERM
echo "=== pre-clean stale serve ==="; stop; sleep 3

echo "=== start 2-node nomtp serve (MML=49152 seqs=5 gpu0.70 mbt=8192) ==="
set +e
env HEAD_HOST="$HEAD" WORKER_HOST="$WORKER" \
  HEAD_ROCE_IP=169.254.122.42 WORKER_ROCE_IP=169.254.253.112 \
  ROCE_IFACE=enp1s0f0np0 NCCL_IB_HCA=rocep1s0f0 \
  VLLM_ROOT="$WT" VLLM_VENV="$VENV" MODEL_ID="$MODEL_ID" \
  TP_SIZE=2 PP_SIZE=1 MAX_MODEL_LEN=49152 GPU_MEMORY_UTILIZATION=0.70 \
  MAX_NUM_SEQS=5 MAX_NUM_BATCHED_TOKENS=8192 BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8 \
  API_PORT="$PORT" RUN_DIR="$RUN/serve" PREWARM_AFTER_HEALTH=0 \
  SERVE_PREFIX_CACHE_MODE=auto ALLOW_CURRENT_BOOT_NVRM_OOM=1 \
  SSH_OPTS="$SSH_OPTS" \
  bash "$SCRIPT_DIR/dgx_spark_start_mp_serve.sh" \
    > "$RUN/serve_start.stdout.log" 2> "$RUN/serve_start.stderr.log"
start_code=$?
set -e
echo "serve_start exit=$start_code"
ok=0; for i in $(seq 1 360); do
  [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HEAD:$PORT/health 2>/dev/null)" = 200 ] && { ok=1; echo "serve UP ~$((i*10))s"; break; }
  sleep 10
done
if [ "$ok" != 1 ]; then echo "HEALTH FAIL"; tail -30 "$RUN/serve_start.stderr.log"; echo "ATTRIB_DONE (serve-failed)"; exit 1; fi

echo "=== sweep depth x conc x mode (safe->risky) ==="
printf "%-8s %-4s %-8s %14s %12s %12s %12s\n" depth conc mode out_tok/s mean_tpot_ms p99_tpot_ms mean_ttft_ms | tee "$RUN/summary.txt"
for depth in $DEPTHS; do
  for c in $CONCS; do
    for mode in $MODES; do
      if [ "$mode" = "rolling" ]; then np=$(( c * 4 )); else np=$c; fi
      [ "$np" -lt 1 ] && np=1
      label="d${depth}_c${c}_${mode}"
      rj="$RUN/${label}.json"
      run_remote "$HEAD" "cd /home/jasl && timeout $BENCH_TIMEOUT $VENV/bin/vllm bench serve --backend vllm \
        --model $MODEL_ID --base-url http://127.0.0.1:$PORT \
        --dataset-name random --random-input-len $depth --random-output-len $OUTLEN \
        --num-prompts $np --max-concurrency $c --ignore-eos \
        --save-result --result-filename /home/jasl/tmp/${label}.json > /home/jasl/tmp/${label}.benchlog 2>&1; echo BENCH_RC=\$?" \
        >> "$RUN/bench_rc.log" 2>&1
      run_remote "$HEAD" "test -f /home/jasl/tmp/${label}.json && cat /home/jasl/tmp/${label}.json" > "$rj" 2>/dev/null || true
      row=$("$VENV/bin/python" -c "import json,sys
try:
  d=json.load(open('$rj'))
  print(round(d['output_throughput'],1),round(d['mean_tpot_ms'],2),round(d['p99_tpot_ms'],2),round(d['mean_ttft_ms'],1))
except Exception:
  print('NA NA NA NA')" 2>/dev/null || echo 'NA NA NA NA')
      printf "%-8s %-4s %-8s %14s %12s %12s %12s\n" "$depth" "$c" "$mode" $row | tee -a "$RUN/summary.txt"
    done
  done
done

echo "=== teardown ==="; stop; sleep 4
run_remote "$HEAD" "nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader 2>/dev/null" || true
echo "=== ARTHUR CLIFF ATTRIB SUMMARY ==="; cat "$RUN/summary.txt"
echo "ATTRIB_DONE RUN=$RUN"
