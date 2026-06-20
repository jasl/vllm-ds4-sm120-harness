#!/usr/bin/env bash
# NVFP4 MoE backend A/B on RTX SM120 (2x RTX PRO 6000, TP=2).
#
# Goal: close the ~-8% NVFP4-vs-MXFP4 gap (which lives in the NVFP4 MoE GEMM)
# by routing DeepSeek-V4-Flash-NVFP4 MoE through the in-build flashinfer b12x
# (cute-DSL FP4 SM120) kernel instead of flashinfer_cutlass -- FORK-FREE, no
# rebuild (b12x v0.20.0 already in the venv; layout probe ok/zero-copy).
#
# THE CLAMP CATCH: DSv4-Flash-NVFP4 sets swiglu_limit, and the NvFP4 oracle
# (vllm/model_executor/layers/fused_moe/oracle/nvfp4.py) HARD-REJECTS any
# explicitly-requested non-clamp backend (b12x is not in NVFP4_BACKENDS_WITH_CLAMP).
# This driver applies a transient, ENV-GATED escape hatch
# (VLLM_NVFP4_EXPERIMENTAL_ALLOW_NONCLAMP=1) so b12x is reachable for the A/B,
# and REVERTS it on exit. The escape hatch is INERT unless the env var is set,
# so it never affects other serves. Decisive question: does b12x (skipping the
# clamp) stay GSM8K-correct on DSv4? If yes -> the clamp is non-essential and we
# can promote a proper relaxation; if b12x is also faster -> NVFP4 reaches MXFP4
# parity (a viable option). See memory project_flashinfer_main_absorption_nvfp4_moe.
#
# Arms (served one at a time; clean teardown between):
#   cutlass    : --moe-backend auto         (= flashinfer_cutlass, the current default)  [baseline]
#   b12x_moe   : --moe-backend flashinfer_b12x  + escape-hatch env                       [MoE on b12x]
#   b12x_all   : b12x_moe  + VLLM_NVFP4_GEMM_BACKEND=flashinfer-b12x                      [MoE + linear on b12x]
# Per arm: confirm selected MoE backend, GSM8K (strict+flexible), prefill bench, decode bench.
#
# Usage: run_sm120_nvfp4_b12x_moe_ab.sh [WORKTREE] [GSM8K_LIMIT] [ARMS]
#   WORKTREE    box vLLM worktree with NVFP4 enablement + b12x (default below)
#   GSM8K_LIMIT lm_eval gsm8k limit (default 200; use 50 for a fast smoke)
#   ARMS        space/comma list subset of: cutlass b12x_moe b12x_all (default all)
#
# RTX must be HEALTHY (post power-cycle). This serves 3 arms = 3 serve cycles;
# teardown is TERM->wait->KILL->clear-shm and the death-guard only runs during
# startup (never counts our own teardown as a crash). Minimize re-runs.
set -uo pipefail

WT="${1:-/home/jasl/tmp/vllm-rebased-dev-20260614}"
GLIM="${2:-200}"
ARMS_IN="${3:-cutlass b12x_moe b12x_all}"; ARMS_IN="${ARMS_IN//,/ }"

VENV=/home/jasl/tmp/vllm-lucifer-pr3395-venv-20260614
HARNESS=/home/jasl/tmp/ds4-sm120-harness
NVFP4=/home/jasl/.cache/huggingface/hub/models--nvidia--DeepSeek-V4-Flash-NVFP4/snapshots/7fc18be2b215ae48260383d4a228ec8a033046f7
SERVED=DS4-NVFP4
HOST=127.0.0.1; PORT=8000
LMBENCH=/home/jasl/tmp/llm_decode_bench.py
ROOT=/home/jasl/tmp/nvfp4_b12x_moe_ab/$(date +%Y%m%d%H%M%S); mkdir -p "$ROOT"

ENVS_F="$WT/vllm/envs.py"
ORACLE_F="$WT/vllm/model_executor/layers/fused_moe/oracle/nvfp4.py"

echo "=== NVFP4 MoE backend A/B  wt=$(basename "$WT")  gsm8k_limit=$GLIM  arms=[$ARMS_IN] -> $ROOT ==="
cd "$WT" || { echo "FATAL: worktree $WT missing"; exit 2; }
echo "checkout: $(git rev-parse --short HEAD 2>/dev/null) '$(git log -1 --format=%s 2>/dev/null | cut -c1-60)'"

stop_vllm(){ pkill -TERM -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 8; pkill -KILL -f 'cli.main serve|openai.api_server|VllmWorkerProcess|EngineCore|vllm serve' >/dev/null 2>&1 || true; sleep 3; rm -f /dev/shm/psm_* 2>/dev/null || true; }

# ---- transient, env-gated escape-hatch patch (idempotent; reverted on exit) ----
PATCHED=0
revert_patch(){ [ "$PATCHED" = 1 ] && { echo "--- reverting escape-hatch patch ---"; cp -f "$ROOT/.bak/envs.py" "$ENVS_F" 2>/dev/null; cp -f "$ROOT/.bak/nvfp4.py" "$ORACLE_F" 2>/dev/null; }; }
cleanup(){ stop_vllm; revert_patch; }
trap cleanup EXIT INT TERM

apply_patch(){
  mkdir -p "$ROOT/.bak"; cp -f "$ENVS_F" "$ROOT/.bak/envs.py"; cp -f "$ORACLE_F" "$ROOT/.bak/nvfp4.py"
  "$VENV/bin/python" - "$ENVS_F" "$ORACLE_F" <<'PY'
import io, sys
envs_f, oracle_f = sys.argv[1], sys.argv[2]
KEY = "VLLM_NVFP4_EXPERIMENTAL_ALLOW_NONCLAMP"

e = io.open(envs_f, encoding="utf-8").read()
if KEY not in e:
    anno = "    VLLM_DEEPEPLL_NVFP4_DISPATCH: bool = False\n"
    assert anno in e, "envs annotation anchor missing"
    e = e.replace(anno, anno + f"    {KEY}: bool = False\n", 1)
    entry = '    "VLLM_DEEPEPLL_NVFP4_DISPATCH": lambda: bool(\n        int(os.getenv("VLLM_DEEPEPLL_NVFP4_DISPATCH", "0"))\n    ),\n'
    assert entry in e, "envs dict anchor missing"
    e = e.replace(
        entry,
        entry + f'    "{KEY}": lambda: bool(\n        int(os.getenv("{KEY}", "0"))\n    ),\n',
        1,
    )
    io.open(envs_f, "w", encoding="utf-8").write(e)
    print("  patched envs.py")
else:
    print("  envs.py already patched")

o = io.open(oracle_f, encoding="utf-8").read()
if KEY not in o:
    raise_block = (
        "            raise ValueError(\n"
        '                f"Model sets swiglu_limit={config.swiglu_limit}, but the "\n'
        '                f"explicitly requested moe_backend={runner_backend!r} does "\n'
        '                f"not apply the SwiGLU clamp. Use \'flashinfer_trtllm\' or "\n'
        '                f"\'flashinfer_cutlass\' instead."\n'
        "            )\n"
    )
    assert raise_block in o, "oracle raise anchor missing"
    gated = (
        f"            if envs.{KEY}:\n"
        "                logger.warning_once(\n"
        '                    "EXPERIMENTAL: moe_backend=%s skips the SwiGLU clamp "\n'
        '                    "(swiglu_limit=%s) via VLLM_NVFP4_EXPERIMENTAL_ALLOW_NONCLAMP; "\n'
        '                    "validate correctness (GSM8K) before any production use.",\n'
        "                    runner_backend, config.swiglu_limit,\n"
        "                )\n"
        "            else:\n"
        + "".join("    " + ln + "\n" for ln in raise_block.splitlines())
    )
    o = o.replace(raise_block, gated, 1)
    io.open(oracle_f, "w", encoding="utf-8").write(o)
    print("  patched oracle/nvfp4.py")
else:
    print("  oracle already patched")
PY
  PATCHED=1
}

# ---- one arm: serve + confirm backend + GSM8K + prefill + decode ----
run_arm(){
  local TAG="$1" MOE_ARG="$2" EXTRA_ENV="$3"
  local OUT="$ROOT/$TAG"; mkdir -p "$OUT"
  echo ""
  echo "############ ARM=$TAG  moe_arg=[$MOE_ARG]  extra_env=[$EXTRA_ENV] ############"
  stop_vllm
  echo "  pre-GPU MiB: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr '\n' ',')"
  ( PATH=/usr/local/cuda/bin:$VENV/bin:$PATH PYTHONPATH=$WT PYTHONSAFEPATH=1 \
    VLLM_LOGGING_LEVEL=INFO VLLM_ENGINE_READY_TIMEOUT_S=3600 CUDA_VISIBLE_DEVICES=0,1 \
    VLLM_FLASHINFER_BYPASS_VERSION_CHECK=1 FLASHINFER_DISABLE_VERSION_CHECK=1 VLLM_USE_FLASHINFER_SAMPLER=1 \
    env $EXTRA_ENV \
    nohup "$VENV/bin/vllm" serve "$NVFP4" --served-model-name "$SERVED" \
      --trust-remote-code --host "$HOST" --port "$PORT" --tensor-parallel-size 2 \
      $MOE_ARG \
      --kv-cache-dtype fp8 --block-size 256 --gpu-memory-utilization 0.90 --max-model-len 16384 \
      --max-num-seqs 32 --max-num-batched-tokens 8192 --max-cudagraph-capture-size 32 \
      --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
      --async-scheduling --no-scheduler-reserve-full-isl --enable-chunked-prefill --enable-flashinfer-autotune \
      --tokenizer-mode deepseek_v4 > "$OUT/serve.log" 2>&1 & echo $! > "$OUT/pid" )
  local sp ok=0; sp=$(cat "$OUT/pid")
  # startup death/error guard (only here; teardown below never counts as crash)
  for i in $(seq 1 240); do
    kill -0 "$sp" 2>/dev/null || { echo "  [$TAG] SERVE DIED ~$((i*10))s"; tail -25 "$OUT/serve.log"; break; }
    [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HOST:$PORT/health 2>/dev/null)" = 200 ] && { ok=1; echo "  [$TAG] health 200 ~$((i*10))s"; break; }
    grep -qaE 'No NvFp4 MoE backend|Engine core initialization failed|EngineCore.*failed|raise ValueError|AssertionError|No available memory|Engine core proc.*died|CUDA error|IllegalInstruction' "$OUT/serve.log" 2>/dev/null && { echo "  [$TAG] SERVE ERROR"; grep -aiE 'error|assert|valueerror|no nvfp4|backend' "$OUT/serve.log" | tail -10; break; }
    sleep 10
  done
  # record which MoE backend was actually selected
  echo "  --- selected backend / load ---"
  grep -aoiE "Using '[A-Za-z0-9_]+' NvFp4 MoE backend|NvFp4 MoE backend|FLASHINFER_B12X|FLASHINFER_CUTLASS|b12x|quant_algo|expert_dtype" "$OUT/serve.log" 2>/dev/null | sort -u | head -8 | sed 's/^/    /'
  if [ "$ok" != 1 ]; then echo "  [$TAG] HEALTH FAIL -> skip eval (arm recorded as failed)"; echo "FAILED" > "$OUT/status"; stop_vllm; return 0; fi
  echo "OK" > "$OUT/status"

  echo "  --- [$TAG] GSM8K 5-shot limit=$GLIM (harness run_lm_eval.sh) ---"
  ( cd "$HARNESS"
    PYTHON="$VENV/bin/python" LM_EVAL_BIN="$VENV/bin/lm_eval" \
      MODEL="$SERVED" BASE_URL="http://$HOST:$PORT" HOST="$HOST" PORT="$PORT" \
      LM_EVAL_TASKS=gsm8k LM_EVAL_NUM_FEWSHOT=5 LM_EVAL_LIMIT="$GLIM" LM_EVAL_NUM_CONCURRENT=8 \
      LM_EVAL_MAX_GEN_TOKS=2048 SERVER_GUARD=1 OUT_DIR="$OUT/lm_eval" \
      bash scripts/run_lm_eval.sh > "$OUT/lm_eval.stdout" 2> "$OUT/lm_eval.stderr" )
  grep -aiE 'exact_match' "$OUT/lm_eval.stdout" 2>/dev/null | grep -aiE 'flexible|strict|gsm8k' | tail -4 | sed 's/^/    /'

  echo "  --- [$TAG] prefill bench (llm_decode_bench --prefill-only 8k,64k) ---"
  PATH=$VENV/bin:$PATH "$VENV/bin/python" "$LMBENCH" \
    --prefill-only --prefill-contexts 8k,64k --port $PORT --model "$SERVED" --display-mode plain \
    2>&1 | tee "$OUT/prefill.txt" | grep -iE "Prefill Speed|Context|8k |64k |tok/s" | head -16 | sed 's/^/    /'

  echo "  --- [$TAG] decode bench (llm_decode_bench ctx0 decode) ---"
  PATH=$VENV/bin:$PATH "$VENV/bin/python" "$LMBENCH" \
    --port $PORT --model "$SERVED" --display-mode plain \
    2>&1 | tee "$OUT/decode.txt" | grep -iE "Decode Speed|C=|concurrency|tok/s" | head -20 | sed 's/^/    /'

  echo "  post health=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 http://$HOST:$PORT/health) errs=$(grep -aci 'Traceback\|CUDA error\|IllegalInstruction' "$OUT/serve.log")"
  stop_vllm
  echo "  post-GPU MiB: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr '\n' ',')"
}

# ---- run ----
apply_patch
for arm in $ARMS_IN; do
  case "$arm" in
    cutlass)  run_arm cutlass  ""                          "" ;;
    b12x_moe) run_arm b12x_moe "--moe-backend flashinfer_b12x" "VLLM_NVFP4_EXPERIMENTAL_ALLOW_NONCLAMP=1" ;;
    b12x_all) run_arm b12x_all "--moe-backend flashinfer_b12x" "VLLM_NVFP4_EXPERIMENTAL_ALLOW_NONCLAMP=1 VLLM_NVFP4_GEMM_BACKEND=flashinfer-b12x" ;;
    *) echo "unknown arm: $arm (skip)";;
  esac
done

echo ""
echo "=========== NVFP4 MoE b12x A/B SUMMARY -> $ROOT ==========="
for arm in $ARMS_IN; do
  OUT="$ROOT/$arm"; [ -d "$OUT" ] || continue
  st=$(cat "$OUT/status" 2>/dev/null || echo "NA")
  bk=$(grep -aoiE "Using '[A-Za-z0-9_]+' NvFp4 MoE backend" "$OUT/serve.log" 2>/dev/null | head -1)
  gs=$(grep -aiE 'exact_match' "$OUT/lm_eval.stdout" 2>/dev/null | grep -aiE 'strict|flexible' | tail -2 | tr '\n' ' ')
  pf=$(grep -iE '8k |64k ' "$OUT/prefill.txt" 2>/dev/null | tr '\n' ' ' | cut -c1-120)
  echo "--- $arm [$st] $bk"
  echo "    gsm8k: $gs"
  echo "    prefill: $pf"
done
echo "PROMOTE only if a b12x arm is GSM8K-within-1sigma of cutlass AND faster (decode and/or prefill)."
echo "=== NVFP4 MoE b12x A/B DONE -> $ROOT (patch reverted on exit) ==="
