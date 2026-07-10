#!/usr/bin/env bash
# NCCL graph-replay regression gate for the GB10 2-node fabric.
#
# WHY THIS GATE EXISTS: nvidia-nccl-cu13 2.30.7 has a proxy-progress-thread-
# death regression on the DGX-Spark host-staged RoCE transport — ANY CUDA-
# graph-replayed collective wedges within ~100-800 replays (pure-torch and
# raw-libnccl repros; caller/env/cadence-independent). 2.30.4 passes 5000
# max-rate replays. Full matrix + serve validation: memory
# project_barrier2_nccl_ll_desync (07-11). Run this against ANY future NCCL
# pin change BEFORE deploying it; monolithic decode graphs
# (TOKENSPEED_DECODE_MONOLITHIC=1) are only safe on versions that PASS.
#
# Runs the pure-torch probe (93 small in-graph allreduces, harsh config:
# max-rate, no idle gaps, 5000 replays) across HEAD/WORKER over the RoCE
# fabric. PASS = "ALL REPLAYS OK" from rank0. WEDGE verdict on a >150s log
# stall with live ranks (the regression's signature: NCCL proxy threads
# absent from /proc/<pid>/task/*/comm while torch watchdogs live).
set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HEAD_HOST="${GB10_HEAD_HOST:-10.0.0.117}"
WORKER_HOST="${GB10_WORKER_HOST:-10.0.0.118}"
HEAD_ROCE_IP="${HEAD_ROCE_IP:-192.168.100.117}"
ROCE_ENV="NCCL_SOCKET_IFNAME=${ROCE_IFACE:-enp1s0f0np0} NCCL_IB_HCA=${NCCL_IB_HCA:-rocep1s0f0}"
VENVBIN="${TOKENSPEED_VENV_BIN:-\$HOME/tokenspeed-sm12x/.venv-ts/bin}"
PORT="${NCCL_GATE_PORT:-29540}"
GAP_MODE="${NCCL_GATE_GAP_MODE:-none}"
REPLAYS="${NCCL_GATE_REPLAYS:-5000}"
EXTRA_ENV="${NCCL_GATE_EXTRA_ENV:-}"   # e.g. LD_PRELOAD=<libnccl.so.2> to test a candidate version
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
PROBE_LOCAL="${SCRIPT_DIR}/gb10_nccl_graph_replay_probe.py"

for h in "$HEAD_HOST" "$WORKER_HOST"; do
  scp -o BatchMode=yes -q "$PROBE_LOCAL" "jasl@$h:~/tmp/nccl_graph_replay_probe.py"
  $SSH "jasl@$h" "pkill -f '[n]ccl_graph_replay_probe\.py'" 2>/dev/null
done
sleep 3

launch() {
  local host="$1" rank="$2"
  $SSH "jasl@$host" "cd ~/tmp && env $ROCE_ENV $EXTRA_ENV GAP_MODE=$GAP_MODE REPLAYS=$REPLAYS nohup $VENVBIN/torchrun --nnodes=2 --node-rank=$rank --nproc-per-node=1 --master-addr=$HEAD_ROCE_IP --master-port=$PORT ~/tmp/nccl_graph_replay_probe.py > ~/tmp/nccl_gate_r$rank.log 2>&1 & echo r$rank-up"
}
launch "$WORKER_HOST" 1
launch "$HEAD_HOST" 0

verdict=TIMEOUT
t=0
while [ $t -lt 420 ]; do
  sleep 10; t=$((t+10))
  if $SSH "jasl@$HEAD_HOST" "grep -q 'ALL REPLAYS OK' ~/tmp/nccl_gate_r0.log" 2>/dev/null; then verdict=PASS; break; fi
  if ! $SSH "jasl@$HEAD_HOST" "pgrep -f '[n]ccl_graph_replay_probe' >/dev/null" 2>/dev/null; then
    verdict=CRASH; break
  fi
  age=$($SSH "jasl@$HEAD_HOST" 'echo $(( $(date +%s) - $(stat -c %Y ~/tmp/nccl_gate_r0.log 2>/dev/null || date +%s) ))' 2>/dev/null)
  if [ "${age:-0}" -gt 150 ]; then
    if $SSH "jasl@$HEAD_HOST" "grep -q captured ~/tmp/nccl_gate_r0.log" 2>/dev/null; then verdict=WEDGE; else verdict=INIT_STALL; fi
    break
  fi
done

for h in "$HEAD_HOST" "$WORKER_HOST"; do
  $SSH "jasl@$h" "pkill -f '[n]ccl_graph_replay_probe\.py'" 2>/dev/null
done
echo "nccl_graph_replay_gate: verdict=$verdict mode=$GAP_MODE replays=$REPLAYS extra_env=[$EXTRA_ENV]"
$SSH "jasl@$HEAD_HOST" "tail -2 ~/tmp/nccl_gate_r0.log" 2>/dev/null
[ "$verdict" = "PASS" ] && exit 0
echo "FAIL nccl_graph_replay_gate: in-graph NCCL collectives are NOT safe on this NCCL build/fabric"
exit 1
