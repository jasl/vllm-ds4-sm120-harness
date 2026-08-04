#!/usr/bin/env bash
# CANONICAL deep long-context RECALL suite for tokenspeed DeepSeek-V4-Flash on GB10.
#
# Composes the EXISTING needle recall gate (ds4_harness long-context-coherence-gate,
# sentinels at absolute lines 17 / n//2 / n-13 → early sinks deeper as depth grows,
# the SM12x indexer distant-context failure mode) across a DEPTH LADDER, and asserts
# the KV-pool token capacity from the serve log (proves the F1/F3 memory fixes).
#
# TWO TIERS (different epistemic status — see docs/sm120/.../deep-longctx):
#   Tier-A (≤ 32768 tok): freeze-SAFE, reproducible → the committed baseline-of-record.
#   Tier-B (49152 → 131072): DEEP_CLIMB=1 only. Watchdog-armed, aborts on the first
#     wedge and records the CEILING reached today. NOT a stable standard. No proven-safe
#     deep prefill path on 2-node yet (feedback_gb10_freeze_risk) — real 128K+ = 4-node.
#
# Assumes a LIVE tokenspeed serve (does not manage it; point BASE_URL at it). Match the
# max-model-len to the deepest rung you enable. Nodes .117/.118 ONLY (never .116/.119).
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/run_context.sh"
load_harness_env
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/gb10_mem_watchdog.sh"

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
MODEL="${MODEL:-deepseek-ai/DeepSeek-V4-Flash-0731}"
PYTHON="${PYTHON:-python}"
GB10_HEAD_HOST="${GB10_HEAD_HOST:-10.0.0.117}"
GB10_WORKER_HOST="${GB10_WORKER_HOST:-10.0.0.118}"
SERVE_LOG="${SERVE_LOG:-}"                    # for the KV-pool capacity assertion
DEEP_CLIMB="${DEEP_CLIMB:-0}"                 # 1 → also run Tier-B (watchdog-armed)
WATCHDOG_FLOOR_GIB="${WATCHDOG_FLOOR_GIB:-8}"
RUN_TIMESTAMP="${RUN_TIMESTAMP:-$(date +%Y%m%d%H%M%S)}"
ARTIFACT_ROOT="${ARTIFACT_ROOT:-${REPO_ROOT}/artifacts}"
OUT_DIR="${ARTIFACT_ROOT}/gb10_deep_long_context/${RUN_TIMESTAMP}"
mkdir -p "${OUT_DIR}"

# NODE ISOLATION — never drive the vLLM baseline pair.
case "${GB10_HEAD_HOST}${GB10_WORKER_HOST}" in
  *10.0.0.116*|*10.0.0.119*)
    echo "REFUSED: host set includes the vLLM baseline .116/.119" >&2; exit 2;;
esac

# Depth ladder: "line_count:concurrency:timeout_s" (line→tok ≈ 31/line; calibrated by
# reading back the gate JSON). Tier-A is freeze-safe; Tier-B tapers concurrency + raises
# timeout for deep cold prefills.
TIER_A_RUNGS=("265:8:1800" "528:8:1800" "1055:8:1800")           # ~8K / 16K / 32K
TIER_B_RUNGS=("1584:4:3600" "2112:4:3600" "3170:2:3600" "4226:1:3600")  # ~49K/64K/96K/128K

summary_rows=()
overall_ok=1

run_rung() { # $1=line_count $2=concurrency $3=timeout $4=tier
  local lines="$1" conc="$2" tmo="$3" tier="$4"
  local tag="${tier}_L${lines}"
  local json="${OUT_DIR}/coherence_${tag}.json"
  echo "--- [${tier}] recall @ line_count=${lines} concurrency=${conc} timeout=${tmo}s ---"
  local rc=0
  BASE_URL="${BASE_URL}" MODEL="${MODEL}" PYTHON="${PYTHON}" \
    COHERENCE_LINE_COUNT="${lines}" COHERENCE_CONCURRENCY="${conc}" \
    COHERENCE_REPEAT_COUNT="${COHERENCE_REPEAT_COUNT:-1}" \
    COHERENCE_TIMEOUT="${tmo}" RUN_TIMESTAMP="${tag}" \
    OUT_DIR="${OUT_DIR}/gate_${tag}" \
    bash "${SCRIPT_DIR}/run_gb10_arthur_long_context_coherence_gate.sh" \
    > "${OUT_DIR}/gate_${tag}.log" 2>&1 || rc=$?
  local gjson="${OUT_DIR}/gate_${tag}/long_context_coherence.json"
  local line
  line=$("${PYTHON}" - "$gjson" "$lines" "$tier" "$rc" <<'PY'
import json, sys
path, lines, tier, rc = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
try:
    d = json.load(open(path))
except Exception:
    print(f"{tier}\t{lines}\t?\tERR\tERR\tgate-produced-no-json(rc={rc})"); sys.exit(0)
rows = d.get("rows", [])
n = len(rows)
rec = sum(1 for r in rows if r.get("recall_ok"))
coh = sum(1 for r in rows if r.get("coherence_ok"))
# distinguish request-error (400/timeout) from a genuine needle miss
errs = sum(1 for r in rows if "request failed" in str(r.get("recall_detail", "")).lower()
           or "http 4" in str(r.get("recall_detail", "")).lower())
ptok = ""  # calibrated token depth if the harness recorded it
for r in rows:
    for k in ("prompt_tokens", "input_tokens", "prompt_token_count"):
        if isinstance(r.get(k), int):
            ptok = r[k]; break
    if ptok:
        break
status = "PASS" if d.get("ok") else ("REQ-ERR" if errs else "RECALL-FAIL")
print(f"{tier}\t{lines}\t{ptok or '~'+str(int(lines*31))}\t{rec}/{n}\t{coh}/{n}\t{status}")
PY
)
  echo "  -> ${line}"
  summary_rows+=("${line}")
  # PASS iff the gate's ok==true (JSON) — rc alone can be a transient
  case "${line}" in *$'\t'PASS) ;; *) overall_ok=0; return 1;; esac
  return 0
}

assert_capacity() {
  [ -n "${SERVE_LOG}" ] || { echo "(capacity assert skipped: set SERVE_LOG=~/tokenspeed-sm12x/serve_gb10.log)"; return 0; }
  echo "=== KV-pool capacity (proves F1/F3) ==="
  local pages tok
  if [ -f "${SERVE_LOG}" ]; then          # running ON the head → read the log directly
    pages=$(grep -oE 'num_device_pages=[0-9]+' "${SERVE_LOG}" 2>/dev/null | tail -1 | grep -oE '[0-9]+')
  else                                     # running remotely → fetch from the head node
    pages=$(ssh -n -o BatchMode=yes -o ConnectTimeout=8 "${GB10_HEAD_HOST}" \
      "grep -oE 'num_device_pages=[0-9]+' '${SERVE_LOG}' 2>/dev/null | tail -1 | grep -oE '[0-9]+'" </dev/null 2>/dev/null)
  fi
  if [ -n "${pages}" ]; then
    tok=$(( pages * 256 ))
    echo "  num_device_pages=${pages} × page_size 256 = ${tok} KV tokens (~$(( tok / 1000 ))K)"
    echo "capacity_pages=${pages} capacity_tokens=${tok}" > "${OUT_DIR}/capacity.txt"
  else
    echo "  (no num_device_pages in ${SERVE_LOG})"
  fi
}

echo "=== GB10 deep long-context standard → ${OUT_DIR} (BASE_URL=${BASE_URL}) ==="
assert_capacity

echo "=== TIER-A (freeze-safe, committed baseline: ≤32K) ==="
for rung in "${TIER_A_RUNGS[@]}"; do
  IFS=: read -r lines conc tmo <<<"${rung}"
  run_rung "${lines}" "${conc}" "${tmo}" "A" || echo "  [Tier-A rung failed — see gate log]"
done

if [ "${DEEP_CLIMB}" = "1" ]; then
  echo "=== TIER-B (deep climb 49K→128K — watchdog-armed, aborts on first wedge) ==="
  gb10_mem_watchdog_start "${GB10_HEAD_HOST}" "${GB10_WORKER_HOST}" "${WATCHDOG_FLOOR_GIB}" 3
  trap 'gb10_mem_watchdog_stop' EXIT
  ceiling="none"
  for rung in "${TIER_B_RUNGS[@]}"; do
    IFS=: read -r lines conc tmo <<<"${rung}"
    # per-request cache drop on both nodes (page-cache squat is a 2nd freeze trigger)
    for n in "${GB10_HEAD_HOST}" "${GB10_WORKER_HOST}"; do
      ssh -n -o BatchMode=yes -o ConnectTimeout=8 "${n}" "sync; echo 1 | sudo tee /proc/sys/vm/drop_caches >/dev/null 2>&1 || true" </dev/null 2>/dev/null
    done
    if run_rung "${lines}" "${conc}" "${tmo}" "B"; then
      ceiling="${lines}"
    else
      # a serve-down (watchdog abort) vs a recall-fail — either way, stop the climb
      if ! curl -sf -m 8 "${BASE_URL%/v1}/health" >/dev/null 2>&1 && ! curl -sf -m 8 "${BASE_URL}/models" >/dev/null 2>&1; then
        echo "  serve is DOWN after line_count=${lines} — watchdog likely aborted. CEILING=${ceiling}"
      else
        echo "  recall/req failure at line_count=${lines} (serve alive). CEILING=${ceiling}"
      fi
      break
    fi
  done
  gb10_mem_watchdog_stop
  echo "TIER-B ceiling (deepest passing rung): line_count=${ceiling}"
fi

echo ""
echo "=== SUMMARY (${OUT_DIR}) ==="
printf 'tier\tlines\ttokens\trecall\tcoherent\tstatus\n'
for r in "${summary_rows[@]}"; do printf '%s\n' "$r"; done
echo ""
[ "${overall_ok}" = "1" ] && echo "DEEP_LONGCTX: TIER-A GREEN" || echo "DEEP_LONGCTX: FAILURES PRESENT (see per-rung gate logs)"
echo "GB10_DEEP_LONGCTX_DONE" > "${OUT_DIR}/done"
