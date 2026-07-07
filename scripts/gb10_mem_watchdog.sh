#!/usr/bin/env bash
# GB10 memory watchdog — aborts a run BEFORE a unified-memory exhaustion FREEZE.
#
# On DGX Spark (GB10) the GPU shares LPDDR5X with the host, so nvidia-smi reports
# memory.free = [N/A]; the real signal is /proc/meminfo MemAvailable. A large
# single-chunk prefill transient can spike unified memory past the edge and
# HARD-FREEZE both TP nodes (ping-alive, sshd-dead → user power-cycle). This
# samples MemAvailable on both nodes and KILLS the serve when either drops below
# a floor, converting a would-be freeze into a clean abort.
#
# Usage:
#   gb10_mem_watchdog_start <head_host> <worker_host> [floor_gib] [interval_s]
#   ... run the risky deep request ...
#   gb10_mem_watchdog_stop
# Sourced (functions) or run standalone (`gb10_mem_watchdog.sh <head> <worker>`).
#
# It does NOT make single-chunk deep prefill safe (the spike can wedge both nodes
# faster than a sampler can react) — it protects the GRADUAL multi-chunk drift and
# is a REQUIRED guard for any Tier-B deep climb. See feedback_gb10_freeze_risk.
set -uo pipefail

GB10_WATCHDOG_PID=""
_GB10_WD_SSH="-o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8"

_gb10_memavail_gib() { # $1=host -> integer GiB MemAvailable (empty on ssh fail)
  ssh -n $_GB10_WD_SSH "$1" "awk '/MemAvailable/{printf \"%d\", \$2/1024/1024}' /proc/meminfo" </dev/null 2>/dev/null
}

_gb10_kill_serve() { # kill the tokenspeed serve on both nodes (NOT vLLM patterns)
  for n in "$1" "$2"; do
    ssh -n $_GB10_WD_SSH "$n" "pkill -9 -f '[s]mg_grpc_servicer'; pkill -9 -f '[t]okenspeed::'; pkill -9 -f '[s]pawn_main'; pkill -9 -f '[.]venv-ts/bin'; true" </dev/null 2>/dev/null
  done
}

gb10_mem_watchdog_start() {
  local head="$1" worker="$2" floor="${3:-8}" interval="${4:-3}"
  # SAFETY: never target the vLLM baseline pair.
  case "$head$worker" in
    *10.0.0.116*|*10.0.0.119*)
      echo "WATCHDOG REFUSED: host set includes the vLLM baseline .116/.119" >&2; return 2;;
  esac
  gb10_mem_watchdog_stop
  (
    while :; do
      local mh mw
      mh=$(_gb10_memavail_gib "$head"); mw=$(_gb10_memavail_gib "$worker")
      if [ -n "$mh" ] && [ "$mh" -lt "$floor" ] 2>/dev/null; then
        echo "[watchdog] $head MemAvailable ${mh}G < ${floor}G — KILL SERVE (freeze-abort)" >&2
        _gb10_kill_serve "$head" "$worker"; exit 0
      fi
      if [ -n "$mw" ] && [ "$mw" -lt "$floor" ] 2>/dev/null; then
        echo "[watchdog] $worker MemAvailable ${mw}G < ${floor}G — KILL SERVE (freeze-abort)" >&2
        _gb10_kill_serve "$head" "$worker"; exit 0
      fi
      sleep "$interval"
    done
  ) &
  GB10_WATCHDOG_PID=$!
  echo "[watchdog] armed head=$head worker=$worker floor=${floor}G interval=${interval}s pid=$GB10_WATCHDOG_PID" >&2
}

gb10_mem_watchdog_stop() {
  [ -n "${GB10_WATCHDOG_PID:-}" ] && kill "$GB10_WATCHDOG_PID" 2>/dev/null || true
  GB10_WATCHDOG_PID=""
}

# standalone: gb10_mem_watchdog.sh <head> <worker> [floor] [interval] — runs until Ctrl-C
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  [ $# -ge 2 ] || { echo "usage: $0 <head_host> <worker_host> [floor_gib] [interval_s]" >&2; exit 1; }
  trap 'gb10_mem_watchdog_stop; exit 0' INT TERM
  gb10_mem_watchdog_start "$@"
  wait "$GB10_WATCHDOG_PID" 2>/dev/null
fi
