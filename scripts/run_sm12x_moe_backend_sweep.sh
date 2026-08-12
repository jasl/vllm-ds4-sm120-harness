#!/usr/bin/env bash
# Compare MoE backends for DeepSeek-V4 (MXFP4 experts) on 2-node TP=2 SM12x.
#
#   TREE=... VENV=... HARNESS=... STOP_CMD=... \
#   HEAD_HOST=... WORKER_HOST=... HEAD_ROCE_IP=... WORKER_ROCE_IP=... \
#     ./run_sm12x_moe_backend_sweep.sh
#
# One serve per backend, same workload each time, several repeats per arm.
#
# The question this answers is "is an upstream kernel now better than the path
# we chose instead" -- NOT "did a FlashInfer bump speed up our current config".
# Those are different questions, and only the first is worth this fleet time:
# our MoE never enters FlashInfer, so a FlashInfer release cannot move the MoE
# path, and a same-config A/B would be measuring a component the change does not
# touch.
#
# Scope that claim to MoE, which an earlier version of this comment did not. A
# FlashInfer bump is NOT inert for us in general -- DeepSeek-V4 attention on
# SM12x runs FlashInfer kernels, so a same-config A/B across versions can move
# on the attention path even while the MoE path is untouched. "Guaranteed to
# show nothing" was true of this experiment and false as a statement about the
# release.
#
# Re-run this after any release that touches SM12x MoE.
#
# Three things this does that a naive sweep does not, each one having produced a
# wrong answer here before:
#
#  1. READS BACK THE KERNEL THE ENGINE ACTUALLY SELECTED. `--moe-backend X`
#     being accepted is not evidence X is in use; an unsupported combination can
#     fall back silently, and then the arm measures the baseline twice and
#     reports "no difference" -- a real result and a null result look identical.
#
#  2. CAPTURES ACCEPTANCE LENGTH ALONGSIDE THROUGHPUT. With a speculative
#     drafter, decode tok/s is acceptance x kernel speed. An arm can lose 26% of
#     decode with a *faster* kernel purely because the drafter accepts less.
#     Reading only tok/s attributes that to the kernel and files the wrong
#     conclusion. Both measured A/Bs of this path landed here.
#
#  3. CAPS JIT PARALLELISM *AND PROPAGATES THE CAP TO THE WORKER NODE*.
#     FlashInfer JIT-builds 97 CUTLASS grouped-GEMM units for fused_moe_120 on
#     first use, and ninja defaults to -j nproc (20 on GB10). Twenty concurrent
#     nvcc exhaust memory, the OOM killer takes one, ninja returns non-zero, and
#     the serve dies with "Engine core initialization failed" -- which reads
#     exactly like an unsupported backend. That misreading cost this arm a
#     start, twice. The cap must reach the worker too: a head-only cap leaves
#     the worker building at -j 20 and the failure simply moves one node over.
#
# An arm that genuinely fails to start is a RESULT, not an error: several
# backends do not accept MXFP4 experts on SM121, and knowing which is the point.
set -uo pipefail

TREE="${TREE:?built vLLM tree}"
VENV="${VENV:?venv with that tree installed}"
HARNESS="${HARNESS:?harness checkout (for dgx_spark_start_mp_serve.sh)}"
STOP_CMD="${STOP_CMD:?path to stop_replica.sh on the nodes}"
HEAD_HOST="${HEAD_HOST:?head node}"
WORKER_HOST="${WORKER_HOST:?worker node}"
HEAD_ROCE_IP="${HEAD_ROCE_IP:?head RoCE address}"
WORKER_ROCE_IP="${WORKER_ROCE_IP:?worker RoCE address}"

MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}"
OUTDIR="${OUTDIR:-/tmp/moe_sweep}"
REPEATS="${REPEATS:-3}"
SSH_USER="${SSH_USER:-$USER}"
ROCE_IFACE="${ROCE_IFACE:-enp1s0f0np0}"
NCCL_IB_HCA="${NCCL_IB_HCA:-rocep1s0f0}"
JIT_JOBS="${JIT_JOBS:-6}"
# A loaded replica holds most of the unified pool; above this, nothing is loaded.
FREE_GIB_IDLE="${FREE_GIB_IDLE:-80}"

# `auto` is the control arm: whatever the engine picks unprompted. Keep it
# first, so a fleet that has drifted shows up before three hours of arms.
BACKENDS="${BACKENDS:-auto flashinfer_cutlass flashinfer_trtllm flashinfer_b12x}"

mkdir -p "$OUTDIR"

FI_VER=$("$VENV/bin/python" -c \
  'import importlib.metadata as m;print(m.version("flashinfer-python"))' 2>/dev/null)
JIT_CACHE="${JIT_CACHE:-$HOME/.cache/flashinfer/${FI_VER}/121a/cached_ops/fused_moe_120}"

on_node() { ssh -o BatchMode=yes -o ConnectTimeout=25 "${SSH_USER}@$1" "$2" </dev/null 2>&1; }

# Teardown must be CONFIRMED, not assumed. A stop that has not finished leaves
# the previous arm's serve answering on the port, and the next arm then measures
# the previous backend while its log says otherwise. Confirmed by two facts a
# shell of ours cannot imitate: free memory (a loaded replica holds most of the
# unified pool) and the serving port.
stop_all() {
  for h in "$HEAD_HOST" "$WORKER_HOST"; do
    on_node "$h" "bash $STOP_CMD" >/dev/null 2>&1
  done
  local i free_a free_b port
  for i in $(seq 1 30); do
    free_a=$(on_node "$HEAD_HOST" 'free -g | awk "/Mem:/{print \$7}"' | tr -d '\r')
    free_b=$(on_node "$WORKER_HOST" 'free -g | awk "/Mem:/{print \$7}"' | tr -d '\r')
    port=$(curl -s -o /dev/null -w '%{http_code}' -m 5 http://127.0.0.1:8000/health 2>/dev/null)
    if [ "${free_a:-0}" -ge "$FREE_GIB_IDLE" ] && [ "${free_b:-0}" -ge "$FREE_GIB_IDLE" ] \
       && [ "$port" = 000 ]; then
      return 0
    fi
    sleep 10
  done
  echo "    !! STOP NOT CONFIRMED after 300s (free ${free_a}G/${free_b}G, health $port)" >&2
  return 1
}

prewarm() { # prewarm <host> -- build the JIT units deliberately, capped, with
            # no startup timeout watching. See note 3 above.
  local h="$1"
  on_node "$h" "
    d='$JIT_CACHE'
    [ -f \"\$d/fused_moe_120.so\" ] && { echo '    $h already built'; exit 0; }
    [ -f \"\$d/build.ninja\" ] || { echo '    $h no build.ninja yet (generated at serve time)'; exit 0; }
    export PATH=$VENV/bin:\$PATH
    ninja -C \"\$d\" -f \"\$d/build.ninja\" -j $JIT_JOBS > /tmp/moe_warm.log 2>&1
    rc=\$?
    if [ -f \"\$d/fused_moe_120.so\" ]; then
      echo \"    $h built \$(stat -c %s \"\$d/fused_moe_120.so\") bytes\"
    else
      echo \"    $h JIT FAILED rc=\$rc\"; tail -3 /tmp/moe_warm.log
    fi
  "
}

serve() { # serve <backend> -> 0 if healthy
  local be="$1" extra=""
  [ "$be" != "auto" ] && extra="--moe-backend $be"
  env MAX_JOBS="$JIT_JOBS" NVCC_THREADS=2 \
    SERVE_REMOTE_ENV_VARS="MAX_JOBS NVCC_THREADS" \
    MODEL_ID="$MODEL" \
    VLLM_ROOT="$TREE" VLLM_VENV="$VENV" TP_SIZE=2 \
    HEAD_HOST="$HEAD_HOST" WORKER_HOST="$WORKER_HOST" \
    HEAD_ROCE_IP="$HEAD_ROCE_IP" WORKER_ROCE_IP="$WORKER_ROCE_IP" \
    ROCE_IFACE="$ROCE_IFACE" NCCL_IB_HCA="$NCCL_IB_HCA" \
    HEAD_ROCE_IFACE="$ROCE_IFACE" HEAD_NCCL_IB_HCA="$NCCL_IB_HCA" \
    WORKER_ROCE_IFACE="$ROCE_IFACE" WORKER_NCCL_IB_HCA="$NCCL_IB_HCA" \
    SERVE_PREFIX_CACHE_MODE=on KV_CACHE_DTYPE=fp8 GPU_MEMORY_UTILIZATION=0.85 \
    MAX_MODEL_LEN=49152 MAX_NUM_SEQS=64 MAX_NUM_BATCHED_TOKENS=8192 \
    SERVE_SPECULATIVE_CONFIG='{"method":"dspark","num_speculative_tokens":5,"draft_sample_method":"probabilistic"}' \
    SERVE_EXTRA_ARGS="$extra" \
    ALLOW_CURRENT_BOOT_NVRM_OOM=1 STARTUP_TIMEOUT=2400 RUN_DIR="$OUTDIR/$be/serve" \
    bash "$HARNESS/scripts/dgx_spark_start_mp_serve.sh" > "$OUTDIR/$be/start.log" 2>&1
  curl -sf -m 10 http://127.0.0.1:8000/health >/dev/null 2>&1
}

measure() { # measure <backend> <rep> -> "<decode_tps> <ttft_ms> <accept_len>"
  local be="$1" rep="$2" log="$OUTDIR/$be/bench_$2.log"
  PYTHONPATH="$TREE" "$VENV/bin/python" -m vllm.entrypoints.cli.main bench serve \
    --backend openai-chat --base-url http://127.0.0.1:8000 \
    --endpoint /v1/chat/completions \
    --model "$MODEL" --tokenizer-mode deepseek_v4 \
    --dataset-name random --num-prompts 24 --max-concurrency 8 \
    --random-input-len 2048 --random-output-len 256 \
    --temperature 1.0 --ignore-eos --seed $((20260812 + rep)) > "$log" 2>&1
  local tps ttft acc
  tps=$(grep -aoE "Output token throughput \(tok/s\): *[0-9.]+" "$log" | grep -oE "[0-9.]+$")
  ttft=$(grep -aoE "Mean TTFT \(ms\): *[0-9.]+" "$log" | grep -oE "[0-9.]+$")
  acc=$(grep -aoE "Acceptance length: *[0-9.]+" "$log" | grep -oE "[0-9.]+$")
  echo "${tps:-NA} ${ttft:-NA} ${acc:-NA}"
}

echo "=== MoE backend sweep  $(date -Is) ==="
echo "    tree=$(git -C "$TREE" rev-parse --short=10 HEAD)  flashinfer=${FI_VER:-?}"
echo "    model=$MODEL"
echo "    pp2048/d256 c=8, $REPEATS repeats per arm, mml 49152"
echo ""

for be in $BACKENDS; do
  mkdir -p "$OUTDIR/$be"
  printf "  --- %s ---\n" "$be"
  if ! stop_all; then
    printf "    SKIPPED  previous arm did not shut down; measuring now would read the WRONG backend\n"
    continue
  fi
  if [ "$be" != auto ]; then
    prewarm "$HEAD_HOST"
    prewarm "$WORKER_HOST"
  fi
  if ! serve "$be"; then
    reason=$(grep -aoE "(ValueError|RuntimeError|NotImplementedError): [^\"]{0,120}|not supported[^\"]{0,70}" \
             "$OUTDIR/$be/start.log" 2>/dev/null |
             grep -viE "Engine core initialization" | head -1)
    printf "    START FAILED  %s\n" "${reason:-see $OUTDIR/$be/start.log}"
    continue
  fi

  sel=$(grep -aoE "MarlinExperts|CutlassExpert[a-zA-Z]*|FlashInfer[a-zA-Z]*Expert[a-zA-Z]*|TrtLlm[a-zA-Z]*|B12X[a-zA-Z]*" \
        "$OUTDIR/$be/serve/head.log" 2>/dev/null | sort -u | tr '\n' ',')
  printf "    engine selected: %s\n" "${sel:-unknown}"
  if [ -z "$sel" ]; then
    # Not benign: the whole point of this line is to prove the flag took effect.
    # With no readback the arm cannot be attributed to a backend at all, and a
    # silent fallback is indistinguishable from a genuine null result.
    printf "    SKIPPED  no kernel readback in the serve log; arm not attributable\n"
    continue
  fi
  if [ "$be" != auto ] && [ "${sel#*Marlin}" != "$sel" ]; then
    printf "    !! fell back to Marlin -- this arm measures the baseline, not %s\n" "$be"
  fi

  tps_list=""; ttft_list=""; acc_list=""
  for r in $(seq 1 "$REPEATS"); do
    read -r tps ttft acc <<< "$(measure "$be" "$r")"
    tps_list="$tps_list $tps"; ttft_list="$ttft_list $ttft"; acc_list="$acc_list $acc"
    printf "    rep%s  decode=%s tok/s  ttft=%s ms  accept=%s\n" "$r" "$tps" "$ttft" "$acc"
  done
  python3 - "$be" "$tps_list" "$ttft_list" "$acc_list" <<'PY'
import sys, statistics
def stat(s):
    v = [float(x) for x in s.split() if x not in ("NA", "")]
    if not v: return "no samples"
    if len(v) == 1: return f"{v[0]:.2f} (1 sample)"
    return f"{statistics.mean(v):.2f} +/- {statistics.stdev(v):.2f} (n={len(v)})"
print(f"    SUMMARY {sys.argv[1]:<20} decode {stat(sys.argv[2])}   "
      f"ttft {stat(sys.argv[3])}   accept {stat(sys.argv[4])}")
PY
done

stop_all
echo ""
echo "=== sweep done $(date -Is) ==="
