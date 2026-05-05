# DGX Spark Bare-Metal Ray/vLLM Cluster

This note captures the public, machine-independent procedure for bringing up a
two-node DGX Spark cluster for DeepSeek V4 Flash on vLLM. It intentionally uses
placeholders for hostnames, IP addresses, usernames, and local paths. Keep
site-specific values in ignored files such as `HANDOFF.local.md` or `.env`.

The expected topology is two DGX Spark nodes connected by the high-speed RoCE
link, one GPU per node, with a Ray cgraph-capable Ray installation available to
vLLM.

## Placeholders

Fill these in locally before running the examples:

```bash
export HEAD_HOST="<ssh-target-for-head-node>"
export WORKER_HOST="<ssh-target-for-worker-node>"
export HEAD_ROCE_IP="<head-roce-ip>"
export WORKER_ROCE_IP="<worker-roce-ip>"
export ROCE_IFACE="<roce-network-interface>"
export NCCL_IB_HCA="<comma-separated-roce-hca-list>"

export VLLM_ROOT="<path-to-target-vllm-checkout>"
export VLLM_VENV="<path-to-vllm-venv>"
export RAY_BIN="<path-to-ray-cgraph-venv>/bin/ray"
export MODEL_ID="deepseek-ai/DeepSeek-V4-Flash"
```

The vLLM venv must import the Ray cgraph build. A simple way is to install Ray
cgraph in the vLLM venv. Another workable setup is a `.pth` file in the vLLM
venv site-packages pointing at the Ray cgraph venv site-packages.

## Preflight

Verify both nodes can see the RoCE link and have matching model/cache state:

```bash
ssh "$HEAD_HOST" "ping -c 3 $WORKER_ROCE_IP"
ssh "$WORKER_HOST" "ping -c 3 $HEAD_ROCE_IP"

ssh "$HEAD_HOST" "test -d '$VLLM_ROOT' && test -x '$VLLM_VENV/bin/vllm'"
ssh "$WORKER_HOST" "test -d '$VLLM_ROOT' && test -x '$VLLM_VENV/bin/python'"
```

If the RoCE path supports jumbo frames, set MTU consistently on both nodes:

```bash
ssh "$HEAD_HOST" "sudo ip link set dev '$ROCE_IFACE' mtu 9000"
ssh "$WORKER_HOST" "sudo ip link set dev '$ROCE_IFACE' mtu 9000"
```

Triton runtime helper compilation needs Python development headers on every
worker node. If startup fails with `fatal error: Python.h: No such file or
directory`, install the matching distro package, for example:

```bash
ssh "$HEAD_HOST" "sudo apt-get update && sudo apt-get install -y python3.12-dev python3-dev"
ssh "$WORKER_HOST" "sudo apt-get update && sudo apt-get install -y python3.12-dev python3-dev"
```

## Reclaim Unified Memory Before Launch

DGX Spark/GB10 unified memory can look almost full to CUDA after large model
cache copies or failed launches because Linux page cache consumes the memory.
Before starting vLLM, reclaim file cache on both nodes:

```bash
ssh "$HEAD_HOST" "sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'"
ssh "$WORKER_HOST" "sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'"
```

The minimal command to remember is:

```bash
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
```

Use this before relaunching after checkpoint copies, failed model loads, or
CUDA memory-guard failures.

## Start A Clean Ray Cluster

Start Ray on the RoCE IPs and make sure each node advertises one GPU. Run this
from the control machine:

```bash
ssh "$HEAD_HOST" "
  set -euo pipefail
  '$RAY_BIN' stop --force || true
  env \
    PATH='/usr/local/cuda/bin:'\"\$PATH\" \
    CUDA_HOME='/usr/local/cuda' \
    TRITON_PTXAS_PATH='/usr/local/cuda/bin/ptxas' \
    PYTHONPATH='$VLLM_ROOT' \
    CUDA_VISIBLE_DEVICES='0' \
    VLLM_HOST_IP='$HEAD_ROCE_IP' \
    RAY_NODE_IP_ADDRESS='$HEAD_ROCE_IP' \
    RAY_OVERRIDE_NODE_IP_ADDRESS='$HEAD_ROCE_IP' \
    NCCL_SOCKET_IFNAME='$ROCE_IFACE' \
    GLOO_SOCKET_IFNAME='$ROCE_IFACE' \
    NCCL_IB_HCA='$NCCL_IB_HCA' \
    NCCL_IB_DISABLE='0' \
    RAY_memory_monitor_refresh_ms='0' \
    RAY_num_prestart_python_workers='0' \
    RAY_object_store_memory='1073741824' \
    '$RAY_BIN' start \
      --head \
      --node-ip-address='$HEAD_ROCE_IP' \
      --port=6379 \
      --num-cpus=2 \
      --num-gpus=1 \
      --object-store-memory=1073741824 \
      --disable-usage-stats
"

ssh "$WORKER_HOST" "
  set -euo pipefail
  '$RAY_BIN' stop --force || true
  env \
    PATH='/usr/local/cuda/bin:'\"\$PATH\" \
    CUDA_HOME='/usr/local/cuda' \
    TRITON_PTXAS_PATH='/usr/local/cuda/bin/ptxas' \
    PYTHONPATH='$VLLM_ROOT' \
    CUDA_VISIBLE_DEVICES='0' \
    VLLM_HOST_IP='$WORKER_ROCE_IP' \
    RAY_NODE_IP_ADDRESS='$WORKER_ROCE_IP' \
    RAY_OVERRIDE_NODE_IP_ADDRESS='$WORKER_ROCE_IP' \
    NCCL_SOCKET_IFNAME='$ROCE_IFACE' \
    GLOO_SOCKET_IFNAME='$ROCE_IFACE' \
    NCCL_IB_HCA='$NCCL_IB_HCA' \
    NCCL_IB_DISABLE='0' \
    RAY_memory_monitor_refresh_ms='0' \
    RAY_num_prestart_python_workers='0' \
    RAY_object_store_memory='1073741824' \
    '$RAY_BIN' start \
      --address='$HEAD_ROCE_IP:6379' \
      --node-ip-address='$WORKER_ROCE_IP' \
      --num-cpus=2 \
      --num-gpus=1 \
      --object-store-memory=1073741824 \
      --disable-usage-stats
"
```

Check that Ray sees two nodes and two GPUs:

```bash
ssh "$HEAD_HOST" "'$RAY_BIN' status --address='$HEAD_ROCE_IP:6379'"
```

The expected status is two active nodes, no pending nodes, no recent failures,
and total resources including `2.0 GPU`.

## Start vLLM: Recommended PP=2 Topology

For two one-GPU Spark nodes, the most useful bring-up shape is tensor parallel
size 1 and pipeline parallel size 2. Start the API server on the head node:

```bash
ssh "$HEAD_HOST" "
  set -euo pipefail
  RUN_DIR=\"/tmp/ds4-spark-ray-pp2-\$(date +%Y%m%d-%H%M%S)\"
  mkdir -p \"\$RUN_DIR\"
  cd '$VLLM_ROOT'
  nohup env \
    PATH='/usr/local/cuda/bin:'\"\$PATH\" \
    CUDA_HOME='/usr/local/cuda' \
    TRITON_PTXAS_PATH='/usr/local/cuda/bin/ptxas' \
    PYTHONPATH='$VLLM_ROOT' \
    CUDA_VISIBLE_DEVICES='0' \
    NCCL_DEBUG='WARN' \
    NCCL_SOCKET_IFNAME='$ROCE_IFACE' \
    GLOO_SOCKET_IFNAME='$ROCE_IFACE' \
    NCCL_IB_HCA='$NCCL_IB_HCA' \
    NCCL_IB_DISABLE='0' \
    VLLM_HOST_IP='$HEAD_ROCE_IP' \
    '$VLLM_VENV/bin/vllm' \
      serve '$MODEL_ID' \
      --trust-remote-code \
      --kv-cache-dtype fp8 \
      --block-size 256 \
      --tensor-parallel-size 1 \
      --pipeline-parallel-size 2 \
      --distributed-executor-backend ray \
      --gpu-memory-utilization 0.90 \
      --max-model-len 65536 \
      --compilation-config '{\"cudagraph_mode\":\"FULL_AND_PIECEWISE\", \"custom_ops\":[\"all\"]}' \
      --tokenizer-mode deepseek_v4 \
      --tool-call-parser deepseek_v4 \
      --enable-auto-tool-choice \
      --reasoning-parser deepseek_v4 \
      --host 0.0.0.0 \
      --port 8000 \
    > \"\$RUN_DIR/head.log\" 2>&1 < /dev/null &
  echo \$! > \"\$RUN_DIR/head.pid\"
  echo \"run_dir=\$RUN_DIR\"
  echo \"pid=\$(cat \"\$RUN_DIR/head.pid\")\"
"
```

## Start vLLM: TP=2 Diagnostic Topology

Tensor parallel size 2 and pipeline parallel size 1 can also be useful as a
cluster diagnostic. It spreads TP workers across nodes. Expect vLLM to warn that
cross-node TP can degrade performance unless the interconnect is fast; that
warning is informational when the RoCE path has already been validated.

Use the same command as above, changing only:

```bash
--tensor-parallel-size 2
--pipeline-parallel-size 1
```

## Health Checks

Poll the API server from the head node:

```bash
ssh "$HEAD_HOST" "curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/health"
ssh "$HEAD_HOST" "curl -fsS http://127.0.0.1:8000/v1/models"
```

Run a minimal OpenAI-compatible completion smoke:

```bash
ssh "$HEAD_HOST" "curl -fsS http://127.0.0.1:8000/v1/completions \
  -H 'Content-Type: application/json' \
  -d '{\"model\":\"'$MODEL_ID'\",\"prompt\":\"Hello, my name is\",\"max_tokens\":8,\"temperature\":1.0,\"top_p\":1.0}'"
```

For startup evidence, grep the serve log for:

```bash
grep -E 'Application startup complete|GPU KV cache size|Model loading took|Graph capturing finished|CUDA graph pool memory' <serve-log>
```

`/health`, `/v1/models`, and a completion response prove that Ray placement,
weight loading, CUDA graph capture, and the HTTP serving path came up. They do
not prove generation quality; run the harness acceptance matrix separately for
quality and API semantics.

## Common Failure Modes

- CUDA memory guard fails immediately after file copies or failed launches:
  reclaim page cache on both nodes with `drop_caches`, then retry.
- `Python.h` is missing during Triton runtime compilation: install Python
  development headers on the affected node.
- Ray status shows one node or one GPU: check RoCE reachability, Ray node IP
  addresses, `CUDA_VISIBLE_DEVICES`, and whether an old Ray runtime is still
  running.
- vLLM warns about cross-node TP: expected for `TP=2 PP=1` on two one-GPU
  nodes. It is a performance warning, not a placement failure.
- A pure source checkout without compiled extensions fails with
  `No module named 'vllm._C'`: run against the built/installed target checkout
  and venv, not an unbuilt archive copy.
