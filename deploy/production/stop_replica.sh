#!/usr/bin/env bash
# Stop a replica on this node and do not return until it is actually gone.
#
#   ./stop_replica.sh
#
# Exits non-zero if anything is left, so a caller can refuse to relaunch.
#
# Four separate attempts to write this failed on 2026-08-10, each in a way
# worth keeping:
#
#  1. `pkill -f "VLLM::"` -- the pattern matched the killing shell's OWN command
#     line, so the shell died before killing anything. Use `ps -eo comm` and a
#     `^VLLM` anchor: comm is the process name, never the killer's arguments.
#  2. Killing only the workers left the `vllm.entrypoints` API server alive, and
#     the launcher then refused to start with "existing vLLM process found".
#  3. Killing the whole PID list at once left the child: when the EngineCore
#     parent dies the worker is reparented to init and survives. Re-read the
#     list each round instead.
#  4. Reporting the leftover count without gating on it -- the count printed 2,
#     the launch went ahead anyway, and the next 7 minutes were wasted.
set -uo pipefail

ROUNDS="${ROUNDS:-10}"
SETTLE="${SETTLE:-3}"

for _ in $(seq 1 "$ROUNDS"); do
  # One at a time, re-reading between kills.
  p=$(ps -eo pid,comm | awk '$2 ~ /^VLLM/ {print $1}' | head -1)
  [ -z "$p" ] && break
  kill -9 "$p" 2>/dev/null
  sleep "$SETTLE"
done

ep=$(ps -eo pid,args | grep '[v]llm.entrypoints' | awk '{print $1}')
[ -n "$ep" ] && { kill -9 $ep 2>/dev/null; sleep "$SETTLE"; }

left=$(ps -eo comm | grep -c '^VLLM' || true)
gpu=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | wc -l)
printf '%s: vllm_procs=%s gpu_apps=%s\n' "$(hostname)" "${left:-0}" "${gpu:-0}"

# GPU memory not released means the next launch will OOM rather than start.
[ "${left:-0}" -eq 0 ] && [ "${gpu:-0}" -eq 0 ]
