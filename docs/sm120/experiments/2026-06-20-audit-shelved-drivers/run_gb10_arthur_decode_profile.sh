#!/usr/bin/env bash
# Torch-profile a clean DECODE window of the arthur cliff to rank the actual
# decode-step CUDA kernels by self_cuda_time_total -> find what scales with
# concurrency/depth (MoE GEMM? MLA? all-reduce? indexer?). Uses the schedule
# (delay_iterations to skip prefill+warmup, max_iterations to bound the capture)
# so the dumped table is decode-only. Profiles c5/16k (the cliff) and c1/16k
# (the flat baseline) on ONE serve via separate /start_profile windows.
set -uo pipefail
H="${H:-/home/jasl/tmp/ds4-sm120-harness}"
WT="${WT:-/home/jasl/tmp/vllm-pr-rebased-20260620}"
VENV="${VENV:-$H/vllm/.venv}"
SCRIPT_DIR="$H/scripts"
HEAD="${HEAD:-10.0.0.116}"; WORKER="${WORKER:-10.0.0.118}"
SSH_OPTS="${SSH_OPTS:--o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o BatchMode=yes}"
PORT="${PORT:-8000}"
MODEL_ID="${MODEL_ID:-deepseek-ai/DeepSeek-V4-Flash}"
RUN="${RUN:-/home/jasl/tmp/arthur_decode_profile/$(date +%Y%m%d%H%M%S)}"; mkdir -p "$RUN"
PDIR_HEAD="${PDIR_HEAD:-/home/jasl/tmp/arthur_profile_out}"
DEPTH="${DEPTH:-16384}"
OUTLEN="${OUTLEN:-600}"
DELAY="${DELAY:-60}"; MAXIT="${MAXIT:-30}"
run_remote(){ ssh $SSH_OPTS "$1" "$2"; }
stop(){ for h in "$WORKER" "$HEAD"; do run_remote "$h" "pkill -TERM -f '[v]llm serve|[V]LLM::|[E]ngineCore' 2>/dev/null; sleep 3; pkill -KILL -f '[v]llm serve|[V]LLM::|[E]ngineCore' 2>/dev/null; true"; done; }
trap stop EXIT INT TERM
echo "=== decode profile -> $RUN (depth=$DEPTH outlen=$OUTLEN delay=$DELAY max=$MAXIT) ==="
stop; sleep 3
run_remote "$HEAD" "rm -rf $PDIR_HEAD; mkdir -p $PDIR_HEAD"
run_remote "$WORKER" "rm -rf $PDIR_HEAD; mkdir -p $PDIR_HEAD"

PCFG="--profiler-config.profiler=torch --profiler-config.torch_profiler_dir=$PDIR_HEAD --profiler-config.torch_profiler_with_stack=false --profiler-config.ignore_frontend=true --profiler-config.delay_iterations=$DELAY --profiler-config.max_iterations=$MAXIT --profiler-config.torch_profiler_use_gzip=true"

echo "=== start serve (nomtp seqs=5 MML=49152) with torch profiler-config ==="
set +e
env HEAD_HOST="$HEAD" WORKER_HOST="$WORKER" \
  HEAD_ROCE_IP=169.254.122.42 WORKER_ROCE_IP=169.254.253.112 \
  ROCE_IFACE=enp1s0f0np0 NCCL_IB_HCA=rocep1s0f0 \
  VLLM_ROOT="$WT" VLLM_VENV="$VENV" MODEL_ID="$MODEL_ID" \
  TP_SIZE=2 PP_SIZE=1 MAX_MODEL_LEN=49152 GPU_MEMORY_UTILIZATION=0.70 \
  MAX_NUM_SEQS=5 MAX_NUM_BATCHED_TOKENS=8192 BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8 \
  API_PORT="$PORT" RUN_DIR="$RUN/serve" PREWARM_AFTER_HEALTH=0 \
  SERVE_PREFIX_CACHE_MODE=auto ALLOW_CURRENT_BOOT_NVRM_OOM=1 \
  SERVE_EXTRA_ARGS="$PCFG" \
  SSH_OPTS="$SSH_OPTS" \
  bash "$SCRIPT_DIR/dgx_spark_start_mp_serve.sh" > "$RUN/serve_start.log" 2>&1
set -e
ok=0; for i in $(seq 1 360); do [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HEAD:$PORT/health 2>/dev/null)" = 200 ] && { ok=1; echo "serve UP ~$((i*10))s"; break; }; sleep 10; done
[ "$ok" = 1 ] || { echo "HEALTH FAIL"; tail -30 "$RUN/serve_start.log"; echo PROFILE_DONE; exit 1; }

profile_cell(){ local conc=$1 tag=$2
  echo "=== profiling $tag (conc=$conc depth=$DEPTH) ==="
  run_remote "$HEAD" "cd /home/jasl && timeout 600 $VENV/bin/vllm bench serve --backend vllm \
    --model $MODEL_ID --base-url http://127.0.0.1:$PORT --dataset-name random \
    --random-input-len $DEPTH --random-output-len $OUTLEN --num-prompts $conc --max-concurrency $conc \
    --ignore-eos --profile > /home/jasl/tmp/profile_${tag}.log 2>&1; echo BENCH_RC=\$?" 2>&1 | tail -2
  sleep 5
  # rank-0 table written to PDIR/profiler_out_0.txt
  run_remote "$HEAD" "ls -t $PDIR_HEAD/profiler_out_0.txt 2>/dev/null && head -60 $PDIR_HEAD/profiler_out_0.txt 2>/dev/null" > "$RUN/${tag}_kerneltable.txt" 2>/dev/null || true
  run_remote "$HEAD" "cp $PDIR_HEAD/profiler_out_0.txt $PDIR_HEAD/${tag}_profiler_out_0.txt 2>/dev/null; true"
  echo "--- top kernels ($tag) ---"; sed -n '1,40p' "$RUN/${tag}_kerneltable.txt" 2>/dev/null
}

profile_cell 5 c5_${DEPTH}
echo "=== teardown ==="; stop; sleep 4
echo "PROFILE_DONE RUN=$RUN"
