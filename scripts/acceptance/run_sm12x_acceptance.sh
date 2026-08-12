#!/usr/bin/env bash
# FINAL ACCEPTANCE for jasl/vllm 15dc5af4dd.
#
# One script, one result set, one SHA. Every number this produces is measured on
# the head that is actually tagged and pushed -- not on an ancestor that "should
# be equivalent". Four times in this session a declaration of done was followed
# by finding something unverified; this exists so the answer is a checklist with
# evidence rather than a recollection.
#
# Prints CHECK lines: "CHECK <name> :: PASS|FAIL :: <evidence>".
# The tail counts them. Anything not PASS is a blocker.
set -uo pipefail
H=/home/jasl/tmp/ds4-sm120-harness
WT=/home/jasl/tmp/vllm-merge-20260711
VENV=$H/vllm/.venv
PY=$VENV/bin/python
MODEL=deepseek-ai/DeepSeek-V4-Flash-0731
EXPECT=d44e224ab9
SHA=$(git -C "$WT" rev-parse --short=10 HEAD)
OUT=/home/jasl/tmp/acceptance_${EXPECT}; mkdir -p "$OUT"; SUM="$OUT/SUMMARY.txt"
export PATH="$VENV/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
export SSH_OPTS="-o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o BatchMode=yes"
DSPARK='{"method":"dspark","num_speculative_tokens":5,"draft_sample_method":"probabilistic"}'

exec 8>/home/jasl/tmp/.acceptance.lock
flock -n 8 || { echo "ABORT: acceptance already running"; exit 8; }
exec 9>/home/jasl/tmp/.topo.lock
flock -w 3600 9 || { echo "ABORT: topo lock held 1h"; exit 9; }

: > "$SUM"
say() { echo "$*" | tee -a "$SUM"; }
check() { # name, verdict, evidence
  printf 'CHECK %-46s :: %-4s :: %s\n' "$1" "$2" "$3" | tee -a "$SUM"
}
settle() {
  for n in 116 117 118 119; do
    ssh -n $SSH_OPTS jasl@10.0.0.$n 'pkill -KILL -f "[V]LLM::|[p]ython -m vllm.entrypoints.cli.main" 2>/dev/null; fuser -k 29519/tcp 8000/tcp 2>/dev/null; rm -f /dev/shm/psm_*' </dev/null 2>/dev/null
  done
  sleep 10
  # a settle that "ran" is not proof the workers died: one survived earlier and
  # held 108 of 121 GiB, which OOM-killed a rebuild.
  for n in 116 117 118 119; do
    left=$(ssh -n $SSH_OPTS jasl@10.0.0.$n 'ps -eo cmd | grep -c "[V]LLM::"' </dev/null 2>/dev/null)
    [ "${left:-0}" != "0" ] && echo "  WARNING: .$n still has $left VLLM proc(s) after settle" | tee -a "$SUM"
  done
  return 0
}

say "=== FINAL ACCEPTANCE  expect=$EXPECT  $(date -Is) ==="

# ---------------------------------------------------------------- A. code state
[ "$SHA" = "$EXPECT" ] && check "A1 head node tree is the tagged SHA" PASS "$SHA" \
  || { check "A1 head node tree is the tagged SHA" FAIL "$SHA != $EXPECT"; exit 2; }

allsame=1; detail=""
for n in 116 117 118 119; do
  r=$(ssh -n $SSH_OPTS jasl@10.0.0.$n "cd $WT && printf '%s/%s/%s' \"\$(git rev-parse --short=10 HEAD)\" \"\$(git status --porcelain --untracked-files=no|wc -l)\" \"\$(git status --porcelain|grep -c '^??')\"" </dev/null 2>/dev/null)
  detail="$detail .$n=$r"
  [ "$r" = "$EXPECT/0/0" ] || allsame=0
done
[ "$allsame" = "1" ] && check "A2 all four nodes clean at that SHA" PASS "$detail" \
  || check "A2 all four nodes clean at that SHA" FAIL "$detail"

# ------------------------------------------------------------- B. unit matrix
say ""; say "--- unit tests on $SHA ---"
cd "$WT"
$PY -m pytest tests/v1/core -q > "$OUT/unit_core.log" 2>&1
c=$(grep -aoE "[0-9]+ passed" "$OUT/unit_core.log" | tail -1)
f=$(grep -aoE "[0-9]+ failed" "$OUT/unit_core.log" | tail -1)
fl=$(grep -aE "^FAILED" "$OUT/unit_core.log" | sed 's/^FAILED //' | cut -d' ' -f1 | tr '\n' ' ')
# the sole permitted failure reproduces identically on the pre-merge tree
if [ -z "$f" ] || [ "$(echo "$fl" | tr -d ' ')" = "tests/v1/core/test_scheduler.py::test_async_scheduling_pp_allows_rescheduling_with_output_placeholders" ]; then
  check "B1 tests/v1/core" PASS "${c:-0 passed} ${f:-0 failed} [only the pre-existing failure]"
else
  check "B1 tests/v1/core" FAIL "${c} ${f} :: $fl"
fi

# BOUNDED. The first acceptance run wedged here for 11 hours: this is a GPU
# suite that spawns its own EngineCore, and one of its cases hung on this 2-node
# box with zero log output. An unbounded check in a sequential chain does not
# fail -- it stops everything after it, which is worse than failing.
timeout 1800 $PY -m pytest tests/v1/spec_decode -q -p no:cacheprovider \
  > "$OUT/unit_spec.log" 2>&1
trc=$?
c=$(grep -aoE "[0-9]+ passed" "$OUT/unit_spec.log" | tail -1)
f=$(grep -aoE "[0-9]+ (failed|error)" "$OUT/unit_spec.log" | tail -1)
fl=$(grep -aE "^FAILED" "$OUT/unit_spec.log" | sed 's/^FAILED //' | cut -d" " -f1 | tr "\n" " ")
if [ "$trc" = "124" ]; then
  check "B2 tests/v1/spec_decode" TIMEOUT "wedged after 30m; GPU suite, spawns its own engine; see note"
  pkill -9 -f "[p]ytest tests/v1/spec_decode" 2>/dev/null
  pkill -9 -f "[V]LLM::" 2>/dev/null; sleep 5
elif [ -z "$f" ]; then
  check "B2 tests/v1/spec_decode" PASS "${c:-none collected}"
else
  check "B2 tests/v1/spec_decode" FAIL "${c} ${f} :: $fl"
fi

# ------------------------------------------ C. default serve: nothing set at all
say ""; say "--- default serve (no env set) ---"
settle
R="$OUT/default"; mkdir -p "$R"
env MODEL_ID="$MODEL" VLLM_ROOT="$WT" VLLM_VENV="$VENV" TP_SIZE=2 \
  HEAD_HOST=10.0.0.116 WORKER_HOST=10.0.0.119 \
  HEAD_ROCE_IP=192.168.100.116 WORKER_ROCE_IP=192.168.100.119 \
  ROCE_IFACE=enp1s0f0np0 NCCL_IB_HCA=rocep1s0f0 \
  HEAD_ROCE_IFACE=enp1s0f0np0 HEAD_NCCL_IB_HCA=rocep1s0f0 \
  WORKER_ROCE_IFACE=enp1s0f0np0 WORKER_NCCL_IB_HCA=rocep1s0f0 \
  SERVE_PREFIX_CACHE_MODE=on KV_CACHE_DTYPE=fp8 GPU_MEMORY_UTILIZATION=0.85 \
  MAX_MODEL_LEN=131072 MAX_NUM_SEQS=64 MAX_NUM_BATCHED_TOKENS=8192 \
  SERVE_SPECULATIVE_CONFIG="$DSPARK" \
  ALLOW_CURRENT_BOOT_NVRM_OOM=1 STARTUP_TIMEOUT=2400 RUN_DIR="$R/serve" \
  bash "$H/scripts/dgx_spark_start_mp_serve.sh" > "$R/start.log" 2>&1
if curl -sf -m 10 http://127.0.0.1:8000/health >/dev/null 2>&1; then
  check "C1 default serve boots" PASS "healthy"
else
  check "C1 default serve boots" FAIL "$(grep -aE 'Error|Traceback|NameError|AttributeError' "$R/start.log" | head -2 | cut -c1-110 | tr '\n' ' ')"
  settle; say "=== ACCEPTANCE_DONE $(date -Is) ==="; exit 3
fi
L="$R/serve/head.log"
rn=$(grep -aoiE 'Using V2 Model Runner' "$L" | sort -u | head -1)
[ -n "$rn" ] && check "C2 default runner is V2" PASS "$rn" || check "C2 default runner is V2" FAIL "no V2 banner"
gd=$(grep -aoE 'Same-step ghost-block guard: [0-9]+/[0-9]+ managers active[^"]*' "$L" | tail -1)
case "$gd" in
  *": 5/5 "*|*": 4/4 "*|*": 3/3 "*|*": 2/2 "*) check "C3 guard ON by default, every manager" PASS "$gd" ;;
  *) check "C3 guard ON by default, every manager" FAIL "${gd:-no guard line at all}" ;;
esac
ne=$(grep -acE 'NameError|AttributeError' "$L")
[ "$ne" = "0" ] && check "C4 no NameError/AttributeError in engine log" PASS "0 occurrences" \
  || check "C4 no NameError/AttributeError in engine log" FAIL "$ne occurrences"

cd "$H"
gates=""
for g in 1 2 3; do
  BASE_URL=http://127.0.0.1:8000 MODEL="$MODEL" PYTHON="$PY" COHERENCE_CONCURRENCY=12 \
    bash scripts/run_gb10_arthur_long_context_coherence_gate.sh > "$R/gate$g.log" 2>&1
  gates="$gates $(grep -aoE 'passed=[0-9]+/[0-9]+' "$R/gate$g.log" | tail -1)"
done
worst=$(echo "$gates" | grep -oE 'passed=[0-9]+' | grep -oE '[0-9]+' | sort -n | head -1)
[ -n "$worst" ] && [ "$worst" -ge 18 ] && check "C5 arthur c=12 x3, no degraded serve" PASS "$gates (min $worst, band 19-24)" \
  || check "C5 arthur c=12 x3, no degraded serve" FAIL "$gates (min ${worst:-none})"

BASE_URL=http://127.0.0.1:8000 MODEL="$MODEL" PYTHON="$PY" COHERENCE_CONCURRENCY=1 \
  bash scripts/run_gb10_arthur_long_context_coherence_gate.sh > "$R/gate_c1.log" 2>&1
c1=$(grep -aoE 'passed=[0-9]+/[0-9]+' "$R/gate_c1.log" | tail -1)
[ "$c1" = "passed=2/2" ] && check "C6 arthur c=1" PASS "$c1" || check "C6 arthur c=1" FAIL "$c1"

BASE_URL=http://127.0.0.1:8000 MODEL="$MODEL" PYTHON="$PY" \
  bash scripts/run_sm120_issue19_instruction_following_gate.sh > "$R/issue19.log" 2>&1
[ "$?" = "0" ] && check "C7 issue19 instruction-following" PASS "rc=0" || check "C7 issue19 instruction-following" FAIL "rc!=0"

BASE_URL=http://127.0.0.1:8000 MODEL="$MODEL" PYTHON="$PY" \
  bash scripts/run_lm_eval.sh > "$R/gsm8k.log" 2>&1
gs=$(grep -aoE '"exact_match_strict": [0-9.]+' "$R/gsm8k.log" | tail -1 | grep -oE '[0-9.]+')
ok=$(awk -v v="${gs:-0}" 'BEGIN{print (v>=0.92)?1:0}')
[ "$ok" = "1" ] && check "C8 GSM8K strict >= 0.92" PASS "$gs" || check "C8 GSM8K strict >= 0.92" FAIL "${gs:-none}"

# --line-counts is not optional. The probe's own defaults reach 13000 lines
# (~364k tokens), past any window this deployment serves, so those rows come
# back as HTTP 400 rather than as a recall result -- and a checker that only
# counts rows reporting "N/8" skips them and calls four clean rows a pass.
"$PY" ds4_harness/multi_needle_probe.py \
  --base-url http://127.0.0.1:8000 --model "$MODEL" \
  --line-counts 1500,2850 --needle-count 8 --distractor-count 8 \
  --repeat-count 3 --seed 20260808 > "$R/needle.log" 2>&1
nl=$(grep -acE '8/8 needles' "$R/needle.log"); lk=$(grep -aoE 'leaked=[0-9]+' "$R/needle.log" | grep -vc 'leaked=0')
# A row that never produced a result matches neither the 8/8 count nor the
# non-zero-leak count, so failures must be counted separately.
fl=$(grep -acE 'FAILED' "$R/needle.log")
{ [ "$nl" -ge 6 ] && [ "$lk" = "0" ] && [ "$fl" = "0" ]; } \
  && check "C9 multi-needle 48/48, zero leaks" PASS "$nl rows all 8/8, leaks 0, 0 failed" \
  || check "C9 multi-needle 48/48, zero leaks" FAIL "$nl rows 8/8, $lk leaked, $fl FAILED"
say ""; say "--- benchy on the final head (perf must not have regressed) ---"
settle
env VLLM_ROOT="$WT" bash "$H/scripts/run_gb10_llama_benchy_standard.sh" > "$OUT/benchy.log" 2>&1
pp=$(grep -aoE "pp2048 @ d8192 \| *[0-9.]+" "$OUT/benchy.log" | grep -oE "[0-9.]+$" | tail -1)
# the V2 arm measured 1471.8 at d8192; benchy sd is ~0.6%, so anything within
# 5% is unchanged. A real regression from a config-only change would be larger.
if [ -n "$pp" ]; then
  ok=$(awk -v v="$pp" 'BEGIN{print (v>=1398 && v<=1546)?1:0}')
  [ "$ok" = "1" ] && check "C10 pp2048 d8192 matches the V2 arm" PASS "$pp (V2 arm 1471.8, +/-5%)"     || check "C10 pp2048 d8192 matches the V2 arm" FAIL "$pp vs 1471.8"
else
  check "C10 pp2048 d8192 matches the V2 arm" FAIL "no pp2048 row parsed from benchy"
fi

# ------------------------------------------------- D. escape hatches must work
say ""; say "--- escape hatches ---"
for arm in v1 noguard; do
  settle
  R2="$OUT/$arm"; mkdir -p "$R2"
  if [ "$arm" = v1 ]; then
    extra=(VLLM_USE_V2_MODEL_RUNNER=0 SERVE_REMOTE_ENV_VARS=VLLM_USE_V2_MODEL_RUNNER)
  else
    extra=(VLLM_ALLOW_SPEC_DEC_SAME_STEP_PREFIX_HIT=0 SERVE_REMOTE_ENV_VARS=VLLM_ALLOW_SPEC_DEC_SAME_STEP_PREFIX_HIT)
  fi
  env "${extra[@]}" MODEL_ID="$MODEL" VLLM_ROOT="$WT" VLLM_VENV="$VENV" TP_SIZE=2 \
    HEAD_HOST=10.0.0.116 WORKER_HOST=10.0.0.119 \
    HEAD_ROCE_IP=192.168.100.116 WORKER_ROCE_IP=192.168.100.119 \
    ROCE_IFACE=enp1s0f0np0 NCCL_IB_HCA=rocep1s0f0 \
    HEAD_ROCE_IFACE=enp1s0f0np0 HEAD_NCCL_IB_HCA=rocep1s0f0 \
    WORKER_ROCE_IFACE=enp1s0f0np0 WORKER_NCCL_IB_HCA=rocep1s0f0 \
    SERVE_PREFIX_CACHE_MODE=on KV_CACHE_DTYPE=fp8 GPU_MEMORY_UTILIZATION=0.85 \
    MAX_MODEL_LEN=131072 MAX_NUM_SEQS=64 MAX_NUM_BATCHED_TOKENS=8192 \
    SERVE_SPECULATIVE_CONFIG="$DSPARK" \
    ALLOW_CURRENT_BOOT_NVRM_OOM=1 STARTUP_TIMEOUT=2400 RUN_DIR="$R2/serve" \
    bash "$H/scripts/dgx_spark_start_mp_serve.sh" > "$R2/start.log" 2>&1
  if ! curl -sf -m 10 http://127.0.0.1:8000/health >/dev/null 2>&1; then
    check "D-$arm serve boots" FAIL "$(grep -aE 'Error|Traceback' "$R2/start.log" | head -1 | cut -c1-110)"
    continue
  fi
  L2="$R2/serve/head.log"
  rn2=$(grep -aoiE 'Using V2 Model Runner' "$L2" | head -1)
  gd2=$(grep -aoE 'Same-step ghost-block guard: [0-9]+/[0-9]+' "$L2" | tail -1)
  if [ "$arm" = v1 ]; then
    [ -z "$rn2" ] && check "D1 VLLM_USE_V2_MODEL_RUNNER=0 selects V1" PASS "no V2 banner; $gd2" \
      || check "D1 VLLM_USE_V2_MODEL_RUNNER=0 selects V1" FAIL "V2 banner present"
  else
    case "$gd2" in
      *": 0/"*) check "D2 guard=0 disables it" PASS "$gd2" ;;
      *) check "D2 guard=0 disables it" FAIL "${gd2:-no line}" ;;
    esac
  fi
  cd "$H"
  BASE_URL=http://127.0.0.1:8000 MODEL="$MODEL" PYTHON="$PY" COHERENCE_CONCURRENCY=1 \
    bash scripts/run_gb10_arthur_long_context_coherence_gate.sh > "$R2/gate_c1.log" 2>&1
  g1=$(grep -aoE 'passed=[0-9]+/[0-9]+' "$R2/gate_c1.log" | tail -1)
  [ "$g1" = "passed=2/2" ] && check "D-$arm still serves correctly (c=1)" PASS "$g1" \
    || check "D-$arm still serves correctly (c=1)" FAIL "$g1"
done

settle
say ""
# Count every CHECK line, and treat anything that is not PASS as a blocker.
# Tallying only ":: FAIL ::" would let a TIMEOUT -- or any verdict word added
# later -- pass silently, which is the failure mode this whole script exists for.
tot=$(grep -ac "^CHECK " "$SUM")
p=$(grep -ac ":: PASS ::" "$SUM")
bad=$((tot - p))
say "RESULT: $p/$tot PASS"
if [ "$bad" = "0" ] && [ "$tot" -ge 16 ]; then
  say "ACCEPTED: every one of the $tot checks passed on $EXPECT"
else
  say "NOT ACCEPTED: $bad non-PASS check(s), $tot total (expected >= 16 checks)"
  grep -a "^CHECK " "$SUM" | grep -av ":: PASS ::" | sed 's/^/  BLOCKER: /' | tee -a "$SUM"
fi
say "=== ACCEPTANCE_DONE $(date -Is) ==="
