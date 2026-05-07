# DGX Spark Bare-Metal vLLM Cluster

This note captures the public, machine-independent procedure for bringing up a
two-node DGX Spark cluster for DeepSeek V4 Flash on vLLM. It intentionally uses
placeholders for hostnames, IP addresses, usernames, and local paths. Keep
site-specific values in ignored files such as `HANDOFF.local.md` or `.env`.

The expected topology is two DGX Spark nodes connected by the high-speed RoCE
link, one GPU per node. The current preferred bring-up path is vLLM's
multi-process distributed executor (`--distributed-executor-backend mp`) with
`TP=2 PP=1`. Pipeline parallelism is not a recommended path for DeepSeek V4
here until upstream vLLM support lands. Ray is still useful for Ray-specific
validation, but do not make Ray part of the critical path when debugging
bare-metal memory pressure.

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
export RAY_PYTHON="$VLLM_VENV/bin/python"
export MODEL_ID="deepseek-ai/DeepSeek-V4-Flash"
```

The vLLM venv must import the Ray cgraph build and must also contain the CUDA
runtime packages that vLLM workers need, including `torch`. A simple setup is to
install Ray cgraph in the vLLM venv. Another workable setup is a `.pth` file in
the vLLM venv site-packages pointing at the Ray cgraph venv site-packages.

Start Ray through the vLLM Python executable, not through a standalone Ray
venv. Ray workers inherit the Python executable used by `ray start`; if that
executable cannot import `torch`, the remote actor can fail with
`No module named 'torch'` even though the vLLM API server was launched from the
right venv.

For no-Ray `mp` runs, also keep `$VLLM_VENV/bin` at the front of `PATH`.
FlashInfer and sampling JIT paths may invoke `ninja` during startup or first
generation; a venv with `ninja` installed can still fail if the launch
environment hides that directory.

## Preflight

Verify both nodes can see the RoCE link and have matching model/cache state:

```bash
ssh "$HEAD_HOST" "ping -c 3 $WORKER_ROCE_IP"
ssh "$WORKER_HOST" "ping -c 3 $HEAD_ROCE_IP"

ssh "$HEAD_HOST" "test -d '$VLLM_ROOT' && test -x '$VLLM_VENV/bin/vllm'"
ssh "$WORKER_HOST" "test -d '$VLLM_ROOT' && test -x '$VLLM_VENV/bin/python'"

ssh "$HEAD_HOST" "'$RAY_PYTHON' -c 'import ray, torch, vllm; print(\"ray\", ray.__version__, ray.__file__); print(\"torch\", torch.__version__, torch.__file__); print(\"vllm\", vllm.__file__)'"
ssh "$WORKER_HOST" "'$RAY_PYTHON' -c 'import ray, torch, vllm; print(\"ray\", ray.__version__, ray.__file__); print(\"torch\", torch.__version__, torch.__file__); print(\"vllm\", vllm.__file__)'"

ssh "$HEAD_HOST" "PATH='$VLLM_VENV/bin:'\"\$PATH\" command -v ninja"
ssh "$WORKER_HOST" "PATH='$VLLM_VENV/bin:'\"\$PATH\" command -v ninja"
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

For large-context runs, also fail closed if the current boot already contains
NVIDIA driver OOM messages:

```bash
ssh "$HEAD_HOST" "journalctl -b -k --no-pager | grep -E 'NVRM:.*(Out of memory|NV_ERR_NO_MEMORY)'"
ssh "$WORKER_HOST" "journalctl -b -k --no-pager | grep -E 'NVRM:.*(Out of memory|NV_ERR_NO_MEMORY)'"
```

If either command finds a match after a failed launch, reboot both nodes before
retrying. `drop_caches` can reclaim file cache, but it does not prove that CUDA
driver or unified-memory state recovered after an `NV_ERR_NO_MEMORY` storm.

For a reusable guarded startup, run the harness helper from the control machine
after exporting the placeholders above. Use the no-Ray helper for the standard
GB10 path:

```bash
TP_SIZE=2 \
PP_SIZE=1 \
MAX_MODEL_LEN=393216 \
GPU_MEMORY_UTILIZATION=0.70 \
MAX_NUM_SEQS=2 \
MAX_NUM_BATCHED_TOKENS=4176 \
MIN_AVAILABLE_MEM_GIB=96 \
scripts/dgx_spark_start_mp_serve.sh
```

The helper stops stale drop-cache loops, refuses to continue if vLLM is already
running unless `ALLOW_EXISTING_VLLM=1`, reclaims file cache when passwordless
sudo is available, checks `torch`/`vllm`/`ninja` imports through the vLLM Python
executable, rejects a current boot with NVIDIA driver OOM by default, verifies
`MemAvailable`, starts a headless worker and API head with
`--distributed-executor-backend mp --nnodes 2`, and polls `/health`.

Use the Ray helper only when validating the Ray path:

```bash
MIN_AVAILABLE_MEM_GIB=96 \
scripts/dgx_spark_start_ray_cluster.sh
```

The helper stops Ray, reclaims file cache when passwordless sudo is available,
checks imports through the vLLM Python executable on both nodes, rejects a
current boot with NVIDIA driver OOM by default, checks `MemAvailable`, starts
Ray through `$VLLM_VENV/bin/python -m ray.scripts.scripts`, and prints
`ray status`.

## Start vLLM: No-Ray MP TP=2 Topology

For two one-GPU Spark nodes, the most useful production-like bring-up shape is
tensor parallel size 2 and pipeline parallel size 1. It spreads TP workers
across the two nodes. vLLM may warn that cross-node TP can degrade performance
unless the interconnect is fast; that warning is informational after the RoCE
path has been validated.

A clean passing startup should show:

- each node reports one rank, with TP ranks `0` and `1`
- both ranks are in PP rank `0`
- checkpoint loading completes before MoE prepare/finalize
- `Available KV cache memory` is logged on both nodes
- `GPU KV cache size` is greater than the requested `MAX_MODEL_LEN`
- `/health` returns HTTP `200`, even though the body may be empty

For no-MTP runs, CUDA graph capture may be enabled by normal vLLM settings. For
MTP runs on the SM12x Triton sparse MLA path, current vLLM code keeps
`torch.compile` enabled but disables CUDA graph capture by default. This is the
reliable GB10 MTP path. `VLLM_TRITON_MLA_SPARSE_ALLOW_CUDAGRAPH=1` is an
experimental opt-in: it can start and capture, but current testing has shown
FULL graph replay can make the server unresponsive under concurrent streaming
pressure.

After startup, run at least one generation smoke and the harness long-context
sentinel probe:

```bash
curl -fsS http://127.0.0.1:8000/v1/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-ai/DeepSeek-V4-Flash","prompt":"Write one short sentence about distributed inference.","max_tokens":24,"temperature":0}'

PYTHON="$VLLM_VENV/bin/python" \
BASE_URL=http://127.0.0.1:8000 \
MODEL="$MODEL_ID" \
LONG_CONTEXT_VARIANT=nomtp \
LONG_CONTEXT_LINE_COUNT=2400 \
LONG_CONTEXT_MAX_TOKENS=128 \
LONG_CONTEXT_THINKING_MODE=non-thinking \
scripts/run_long_context_probe.sh
```

The 2400-line probe is a stability gate, not a full 384K prompt. It still
exercises long-prefill scheduling and sentinel retrieval, and is cheap enough
to run before a full generation baseline. The wrapper invokes the
`long-context-probe` CLI command and records GPU/runtime telemetry beside the
probe JSON and Markdown outputs.

## Start A Clean Ray Cluster

Start Ray on the RoCE IPs and make sure each node advertises one GPU. Run this
from the control machine:

```bash
ssh "$HEAD_HOST" "
  set -euo pipefail
  '$RAY_PYTHON' -m ray.scripts.scripts stop --force || true
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
    '$RAY_PYTHON' -m ray.scripts.scripts start \
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
  '$RAY_PYTHON' -m ray.scripts.scripts stop --force || true
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
    '$RAY_PYTHON' -m ray.scripts.scripts start \
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
ssh "$HEAD_HOST" "'$RAY_PYTHON' -m ray.scripts.scripts status --address='$HEAD_ROCE_IP:6379'"
```

The expected status is two active nodes, no pending nodes, no recent failures,
and total resources including `2.0 GPU`.

## Start vLLM: Ray-Specific TP=2 Topology

For Ray-specific testing, start the API server on the head node after the Ray
cluster is healthy:

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
      --tensor-parallel-size 2 \
      --pipeline-parallel-size 1 \
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

## Avoid PP=2 For Now

Older harness notes used `TP=1 PP=2` because it reduced per-rank model memory
before the SM12x work was reorganized. That path is no longer the default:
DeepSeek V4 pipeline parallelism still depends on upstream vLLM support, and
the minimal SM12x branch should be validated with `TP=2 PP=1` instead. If a
branch needs PP-specific experiments, keep them separate from the minimal GB10
bring-up path and document the exact upstream dependency.

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

`/health`, `/v1/models`, and a completion response prove that placement, weight
loading, and the HTTP serving path came up. They do not prove generation
quality; run the harness acceptance matrix separately for quality and API
semantics. For MTP, also run a guarded C>1 streaming pressure probe so the
report captures scheduler or CUDA graph replay stalls instead of relying on a
single smoke request.

## Common Failure Modes

- CUDA memory guard fails immediately after file copies or failed launches:
  reclaim page cache on both nodes with `drop_caches`, then retry.
- Kernel logs contain `NVRM: GPU0 ... Out of memory [NV_ERR_NO_MEMORY]`:
  treat the current boot as contaminated and reboot both nodes before retrying.
- `max_model_len=393216` dies during safetensors load or MXFP4 MoE
  prepare/finalize even though rebooted hosts show enough `MemAvailable`:
  first verify the current `TP=2 PP=1` path and preserve the serve log. Do not
  reintroduce PP-specific weight-loading workarounds unless the branch is
  explicitly testing pipeline parallelism.
- `TP=1 PP=2` fails with missing-layer, missing-parameter, or rank-local weight
  issues: treat this as out of scope for the current minimal GB10 path. Use
  `TP=2 PP=1` until upstream vLLM PP support for DeepSeek V4 is available.
- Startup reaches CUDA graph profiling but the first sampling path raises
  `FileNotFoundError: 'ninja'`: the vLLM venv has `ninja`, but the launch
  `PATH` does not include `$VLLM_VENV/bin`. Use
  `PATH="$VLLM_VENV/bin:$CUDA_HOME/bin:$PATH"` in both head and worker
  environments.
- MTP starts and captures CUDA graphs with
  `VLLM_TRITON_MLA_SPARSE_ALLOW_CUDAGRAPH=1`, then stalls or becomes
  unresponsive under concurrent streaming: rerun the same shape with the
  default MTP path, which keeps compile enabled and disables CUDA graph capture.
  Preserve the failing artifacts as a graph-safety reproduction instead of
  treating it as a general GB10 startup failure.
- Remote Ray actor fails with `No module named 'torch'`: Ray was likely started
  with a Python executable outside the vLLM venv. Start Ray with
  `$VLLM_VENV/bin/python -m ray.scripts.scripts`, or use the guarded helper
  script above.
- Raylet or GCS exits while loading safetensors: inspect available host memory
  on both nodes and the current boot's NVIDIA driver log before retrying. Large
  DeepSeek V4 checkpoints can drive host/unified-memory pressure before vLLM
  reaches CUDA graph capture or KV-cache profiling.
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
