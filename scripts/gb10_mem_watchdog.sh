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
  # Kill policy (measured 07-09): a HEALTHY Tier-A gate transiently dips to
  # ~4-6G right after a batch of long prefills and recovers on idle-release
  # within ~60s (caching-allocator retention, not a leak). So a single sample
  # below the floor must NOT kill: require TWO CONSECUTIVE low samples
  # >= settle_s apart. A catastrophic reading (< panic_gib, default 3G) still
  # kills immediately -- at that level the next allocation can wedge sshd.
  local head="$1" worker="$2" floor="${3:-8}" interval="${4:-3}"
  local settle_s="${5:-60}" panic_gib="${6:-3}"
  # SAFETY: never target the vLLM baseline pair.
  case "$head$worker" in
    *10.0.0.116*|*10.0.0.119*)
      echo "WATCHDOG REFUSED: host set includes the vLLM baseline .116/.119" >&2; return 2;;
  esac
  gb10_mem_watchdog_stop
  (
    _check_one() { # $1=host -> 0 healthy, 1 killed
      local m
      m=$(_gb10_memavail_gib "$1")
      [ -n "$m" ] || return 0
      if [ "$m" -lt "$panic_gib" ] 2>/dev/null; then
        echo "[watchdog] $1 MemAvailable ${m}G < panic ${panic_gib}G — KILL SERVE (freeze-abort)" >&2
        _gb10_kill_serve "$head" "$worker"; return 1
      fi
      if [ "$m" -lt "$floor" ] 2>/dev/null; then
        echo "[watchdog] $1 ${m}G < ${floor}G — settle ${settle_s}s before deciding" >&2
        sleep "$settle_s"
        m=$(_gb10_memavail_gib "$1")
        if [ -n "$m" ] && [ "$m" -lt "$floor" ] 2>/dev/null; then
          echo "[watchdog] $1 still ${m}G < ${floor}G post-settle — KILL SERVE (freeze-abort)" >&2
          _gb10_kill_serve "$head" "$worker"; return 1
        fi
        echo "[watchdog] $1 recovered to ${m}G (idle-release) — continuing" >&2
      fi
      return 0
    }
    while :; do
      _check_one "$head" || exit 0
      _check_one "$worker" || exit 0
      sleep "$interval"
    done
  ) &
  GB10_WATCHDOG_PID=$!
  echo "[watchdog] armed head=$head worker=$worker floor=${floor}G panic=${panic_gib}G settle=${settle_s}s interval=${interval}s pid=$GB10_WATCHDOG_PID" >&2
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
