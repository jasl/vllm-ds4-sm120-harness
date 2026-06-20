#!/usr/bin/env bash
# Regression gate for PR vllm-project/vllm#41834 (DeepSeek-V4 D512-split sparse-MLA
# prefill JIT-during-inference wedge).
#
# The tester reported that the first long prefill stalled the engine ~20s, parking
# EngineCore in shm_broadcast (surfacing as "sample_tokens RPC timed out"). Root
# cause: the D512-split sparse-MLA prefill Triton kernels JIT-compile on first use,
# and the stock warmup never exercises them. The fix pre-compiles them at startup
# (VLLM_DEEPSEEK_V4_INDEXED_D512_SPLIT_PREFILL_WARMUP, default on).
#
# This gate proves it with vLLM's own jit_monitor (which logs a warning for any
# Triton compile AFTER warmup). It runs an A/B on a FRESH Triton cache per phase:
#   baseline (warmup OFF): first long prefill must JIT the split kernels in-inference.
#   fixed    (warmup ON ): the split kernels must NOT JIT in-inference (== 0).
# PASS requires baseline>0, fixed==0, and the warmup-helper log line present.
#
# A fresh TRITON_CACHE_DIR per phase is mandatory, else a prior run's cache hides
# the compile. One single long prefill (num_prefills==1) hits the split path; its
# internal query chunks sweep the reachable combined_topk widths.
#
# Required env:
#   MODEL          model id (default deepseek-ai/DeepSeek-V4-Flash)
#   VLLM_VENV      path to the vLLM venv (must contain bin/vllm)
#   VLLM_REPO      path to the vLLM source worktree to run (editable-install target;
#                  must be checked out to the code under test). Used as PYTHONPATH.
# Optional env:
#   HOST/PORT      API host/port (default 127.0.0.1 / 8000)
#   GATE_ISL       single-prefill prompt length in tokens (default 60000)
#   GATE_TP        tensor-parallel size (default 2)
#   GATE_MAX_MODEL_LEN   default 65536
#   GATE_GPU_MEM_UTIL    default 0.90
#   GATE_EXTRA_SERVE_ARGS  appended verbatim to `vllm serve`
#   GATE_OUT_ROOT  output root (default ./.local-tmp/d512_jit_gate)
#   GATE_HEALTH_TRIES  health poll attempts x5s (default 300; fresh cache => slow)
set -uo pipefail

MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash}"
VLLM_VENV="${VLLM_VENV:?set VLLM_VENV (path to vLLM venv with bin/vllm)}"
VLLM_REPO="${VLLM_REPO:?set VLLM_REPO (vLLM worktree checked out to the code under test)}"
HOST="${HOST:-127.0.0.1}"; PORT="${PORT:-8000}"
GATE_ISL="${GATE_ISL:-60000}"; GATE_OSL="${GATE_OSL:-8}"
GATE_TP="${GATE_TP:-2}"
GATE_MAX_MODEL_LEN="${GATE_MAX_MODEL_LEN:-65536}"
GATE_GPU_MEM_UTIL="${GATE_GPU_MEM_UTIL:-0.90}"
GATE_EXTRA_SERVE_ARGS="${GATE_EXTRA_SERVE_ARGS:-}"
GATE_HEALTH_TRIES="${GATE_HEALTH_TRIES:-300}"
GATE_OUT_ROOT="${GATE_OUT_ROOT:-$(pwd)/.local-tmp/d512_jit_gate}"
VLLM_BIN="${VLLM_VENV}/bin/vllm"

ROOT="${GATE_OUT_ROOT}/$(date +%Y%m%d%H%M%S)"; mkdir -p "$ROOT"
echo "=== D512-split prefill JIT gate (PR#41834) -> $ROOT (ISL=$GATE_ISL) ==="
echo "MODEL=$MODEL REPO=$VLLM_REPO TP=$GATE_TP MAX_MODEL_LEN=$GATE_MAX_MODEL_LEN"

run_phase(){ # TAG  WARMUP(0/1)
  local TAG="$1" W="$2"
  local OUT="$ROOT/$TAG"; mkdir -p "$OUT"; local LOG="$OUT/serve.log"
  local TCACHE="$OUT/triton_cache"; mkdir -p "$TCACHE"
  echo ""; echo "########## PHASE [$TAG] WARMUP=$W (fresh triton cache) ##########"
  pkill -KILL -f '[V]LLM::' 2>/dev/null||true; pkill -KILL -f '[c]li.main serve' 2>/dev/null||true
  sleep 4; rm -f /dev/shm/psm_* 2>/dev/null||true

  ( PATH="${VLLM_VENV}/bin:/usr/local/cuda/bin:$PATH" PYTHONPATH="$VLLM_REPO" PYTHONSAFEPATH=1 \
    TRITON_CACHE_DIR="$TCACHE" VLLM_LOGGING_LEVEL=INFO VLLM_ENGINE_READY_TIMEOUT_S=3600 \
    VLLM_DEEPSEEK_V4_INDEXED_D512_SPLIT_PREFILL_WARMUP="$W" \
    nohup "$VLLM_BIN" serve "$MODEL" --served-model-name DS4 --trust-remote-code \
      --host "$HOST" --port "$PORT" --tensor-parallel-size "$GATE_TP" \
      --max-model-len "$GATE_MAX_MODEL_LEN" --gpu-memory-utilization "$GATE_GPU_MEM_UTIL" \
      --enable-chunked-prefill --jit-monitor-verbose --tokenizer-mode deepseek_v4 \
      $GATE_EXTRA_SERVE_ARGS > "$LOG" 2>&1 & echo $! > "$OUT/pid" )
  local sp; sp=$(cat "$OUT/pid"); local up=0
  for i in $(seq 1 "$GATE_HEALTH_TRIES"); do
    kill -0 "$sp" 2>/dev/null || { echo "  SERVE DIED ~$((i*5))s"; tail -25 "$LOG"; return 91; }
    [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HOST:$PORT/health 2>/dev/null)" = 200 ] && { up=1; echo "  serve UP ~$((i*5))s"; break; }
    grep -qaE 'Engine core initialization failed|No available memory|RuntimeError:' "$LOG" 2>/dev/null && { echo "  SERVE ERROR"; grep -aiE 'error|assert' "$LOG"|tail -8; return 92; }
    sleep 5; done
  [ "$up" = 1 ] || { echo "  HEALTH FAIL"; pkill -KILL -f '[V]LLM::' 2>/dev/null; return 93; }

  local warm; warm=$(grep -aE 'Warming up DeepSeek V4 D512-split sparse-MLA prefill' "$LOG" 2>/dev/null | sed 's/.*\] //' | tail -1)
  echo "  warmup-helper: ${warm:-<none>}"
  PATH="${VLLM_VENV}/bin:$PATH" python3 - "$PORT" "$GATE_ISL" "$GATE_OSL" <<'PY' 2>&1 | sed 's/^/  /' | tail -3
import sys,json,time,urllib.request
port,ISL,OSL=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
ids=[(i%1000)+10 for i in range(ISL)]
body=json.dumps({"model":"DS4","prompt":ids,"max_tokens":OSL,"temperature":0,"ignore_eos":True}).encode()
t=time.time()
try:
    r=urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/v1/completions",body,{"Content-Type":"application/json"}),timeout=300)
    d=json.loads(r.read()); u=d.get("usage",{})
    print(f"REQ ok {time.time()-t:.1f}s prompt_tok={u.get('prompt_tokens')}")
except Exception as e: print(f"REQ ERR {time.time()-t:.1f}s: {str(e)[:120]}")
PY
  sleep 2
  local n; n=$(grep -acE 'JIT compilation during inference:.*_indexed_d512_split' "$LOG" 2>/dev/null)
  echo "  split-kernel JIT-in-inference = $n"
  grep -aE 'JIT compilation during inference:.*_indexed_d512_split' "$LOG" 2>/dev/null | sed 's/.*inference: //; s/ (key=.*//' | sort | uniq -c | sed 's/^/    /' | head
  echo "$n" > "$OUT/split_jit"; printf '%s' "${warm:+1}" > "$OUT/warmran"
  pkill -KILL -f '[V]LLM::' 2>/dev/null||true; pkill -KILL -f '[c]li.main serve' 2>/dev/null||true
  sleep 3; rm -f /dev/shm/psm_* 2>/dev/null||true; return 0
}

run_phase baseline 0
run_phase fixed    1

db=$(cat "$ROOT/baseline/split_jit" 2>/dev/null || echo "?")
df=$(cat "$ROOT/fixed/split_jit" 2>/dev/null || echo "?")
wf=$(cat "$ROOT/fixed/warmran" 2>/dev/null)
echo ""; echo "=========== D512-SPLIT JIT GATE SUMMARY ==========="
echo "baseline (warmup OFF): split-kernel JIT-in-inference = $db  (expect >0)"
echo "fixed    (warmup ON ): split-kernel JIT-in-inference = $df  (expect  0)"
echo "fixed    warmup-helper-ran: ${wf:+yes}${wf:-no}"
VERDICT=FAIL
if [ "$db" != "?" ] && [ "$df" != "?" ] && [ "$db" -gt 0 ] 2>/dev/null && [ "$df" -eq 0 ] 2>/dev/null && [ -n "$wf" ]; then VERDICT=PASS; fi
echo "VERDICT: $VERDICT  (logs: $ROOT)"
[ "$VERDICT" = PASS ] && exit 0 || exit 1
