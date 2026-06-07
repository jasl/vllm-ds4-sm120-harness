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

The vLLM venv must contain the runtime packages that vLLM workers need,
including `torch`, `ray`, and `ninja`. For the current routine GB10 Ray
validation path, `ray[default]==2.48.0` in the vLLM venv has been sufficient.
Install `ray[cgraph,default]` in the same venv only when validating Ray compiled
graph or pipeline-parallel test paths. Avoid a standalone Ray venv unless the
vLLM venv imports that same site-packages tree explicitly.

Before using a fresh GB10/DGX Spark environment for DeepSeek V4, upgrade NCCL to
the latest NVIDIA build that matches the CUDA runtime. Do this as part of
environment bootstrap, before debugging vLLM scheduler, CUDA graph, or sparse MLA
behavior. On 2026-05-11 the current NVIDIA download page lists NCCL `2.30.4`
for CUDA 13.2, with Ubuntu/Deb packages `2.30.4-1+cuda13.2`; recheck the NVIDIA
NCCL download page for newer builds when creating the next environment.

Use the active CUDA toolkit symlink (`/usr/local/cuda`) in public GB10 profiles
unless a site-specific note proves a versioned path exists on every node.
FlashInfer runtime helper JITs call `nvcc` during startup; if the profile points
at a missing versioned toolkit such as `/usr/local/cuda-13.2`, startup can fail
while building the sampling helper even though vLLM and torch import normally.

Non-interactive SSH commands do not necessarily load the user's shell profile.
When building editable vLLM on GB10, pass the CUDA toolkit and SM121 architecture
environment explicitly instead of relying on `~/.zshrc`:

```bash
env \
  PATH="/usr/local/cuda/bin:$PATH" \
  CUDA_HOME="/usr/local/cuda" \
  TRITON_PTXAS_PATH="/usr/local/cuda/bin/ptxas" \
  MPI_HOME="/usr/lib/aarch64-linux-gnu/openmpi" \
  NVCC_GENCODE="-gencode=arch=compute_121,code=sm_121" \
  CUDA_ARCH_LIST="121a" \
  TORCH_CUDA_ARCH_LIST="12.1a" \
  OMP_NUM_THREADS=1 \
  CCACHE_DIR="$HOME/.cache/ccache" \
  CCACHE_NOHASHDIR=true \
  "$HOME/.local/bin/uv" pip install --python .venv/bin/python \
    --verbose --no-build-isolation -e .
```

After the configure step, check the build log before trusting the venv. A healthy
GB10 build should not show `compute_20`; it should report the SM121a input and
compile the SM120-family vLLM CUDA objects such as Marlin, `scaled_mm_sm120`,
`moe_data`, NVFP4, and CUTLASS MLA. `DeepGEMM` and `FlashMLA` may still report
unsupported architecture on current upstream sources; treat that as a separate
backend availability limit, not as the arch-detection failure.

For Ubuntu/Debian DGX Spark nodes using CUDA 13.2, install from the NVIDIA CUDA
repository for the node architecture, then pin the matching NCCL package on both
nodes:

```bash
sudo apt-get update
sudo apt-get install -y libnccl2=2.30.4-1+cuda13.2 libnccl-dev=2.30.4-1+cuda13.2
```

If the environment uses NCCL4PY or other NCCL Python bindings, update those in
the vLLM venv as well. NCCL 2.30.x release notes include NCCL4PY v0.2.0; keep
the binding and NCCL runtime from the same current release family when possible.
Record the installed NCCL package version and `torch.cuda.nccl.version()` in the
run artifact or local handoff note before running the MTP/TP=2 gates.

FlashInfer JIT cache is an optional environment-side override, not a vLLM branch
patch. Keep it aligned with the installed `flashinfer-python` and
`flashinfer-cubin` base version, and install it without dependency resolution so
it cannot pull a different Torch/CUDA stack:

```bash
cd ~/tmp/ds4-sm120-harness
PYTHON=~/tmp/vllm/.venv/bin/python \
  scripts/install_flashinfer_jit_cache.sh
```

For CUDA 13 this resolves a base version such as `0.6.12` to the CUDA-specific
wheel version `0.6.12+cu130` from the FlashInfer wheel directory, then verifies
the installed packages and runs `flashinfer show-config` when available.

`b12x` is an optional SM120/SM121 kernel package for research builds. Do not add
it to vLLM's hard requirements or the default public GB10 profile until the
corresponding vLLM code path is validated. When testing it, install it into the
already-created vLLM venv without dependency resolution so it cannot pull a
different Torch, CUDA, CUTLASS DSL, or NCCL stack:

```bash
cd ~/tmp/ds4-sm120-harness/vllm
.venv/bin/python -m pip install --no-deps b12x==0.15.2
.venv/bin/python - <<'PY'
import importlib.util

for name in (
    "b12x",
    "b12x.integration.tp_moe",
    "b12x.integration.mla",
    "b12x.integration.nsa_indexer",
    "b12x.distributed",
):
    spec = importlib.util.find_spec(name)
    print(f"{name}: {bool(spec)}")
PY
```

If the target venv was created without the `pip` module, install through `uv`
while still pointing at the vLLM Python executable:

```bash
uv pip install --python .venv/bin/python --no-deps b12x==0.15.2
```

This is analogous to the NCCL override above: document the exact package
version and verify imports on every GB10 node before running experiments. A
successful import does not mean b12x is active; serve logs must still show the
selected MoE, attention, indexer, and all-reduce backends.

As of the 2026-06-04 optional-dependency recheck, import success is not enough
for b12x MLA promotion. `b12x.integration.mla` imports on GB10, but the current
CUDA 13.0 toolkit fails while JIT-compiling the compressed MLA microbench for
SM121 with NVPTX/ptxas `cvt` instruction errors. Treat b12x MLA as research-only
until the microbench compiles and the end-to-end GB10 promotion matrix passes.

For one-off kernel/configuration experiments, `scripts/dgx_spark_start_mp_serve.sh`
can forward explicitly named environment variables to the remote vLLM processes
through `SERVE_REMOTE_ENV_VARS`. This is intentionally an allowlist: invalid
variable names or requested variables that are not set fail before launch.

```bash
VLLM_USE_BREAKABLE_CUDAGRAPH=0 \
SERVE_REMOTE_ENV_VARS=VLLM_USE_BREAKABLE_CUDAGRAPH \
scripts/dgx_spark_start_mp_serve.sh
```

Keep experimental variables out of public default profiles until the run logs
show the intended backend path and the standard GB10/SM120 gates pass.

## Nsight Compute Performance Counters

If Nsight Compute fails with `ERR_NVGPUCTRPERM`, the user may already have
normal CUDA device access but the NVIDIA driver is still restricting GPU
performance counters to administrative processes. Running `ncu` through `sudo`
is a valid immediate workaround for one-off profiling. To allow ordinary user
profiling after the next reboot, install this module option on every node:

```bash
printf '%s\n' 'options nvidia NVreg_RestrictProfilingToAdminUsers=0' \
  | sudo tee /etc/modprobe.d/nvidia-profiler.conf >/dev/null
if command -v update-initramfs >/dev/null 2>&1; then
  sudo update-initramfs -u
fi
```

Check the current live driver state with:

```bash
cat /proc/driver/nvidia/params | grep RmProfilingAdminOnly
```

`RmProfilingAdminOnly: 1` means the currently loaded driver still requires
admin privileges for performance counters. The modprobe setting takes effect
after a driver reload or reboot; until then, use `sudo ncu` and change the
artifact owner back to the normal user if needed.

Start Ray through the vLLM Python executable, not through a standalone Ray venv.
Ray workers inherit the Python executable and environment used by `ray start`;
if that executable cannot import `torch`, the remote actor can fail with
`No module named 'torch'` even though the vLLM API server was launched from the
right venv. Ray workers can fail to find `ninja` during FlashInfer sampler
profiling for the same reason. Keep `$VLLM_VENV/bin` at the front of `PATH` for
both Ray and no-Ray `mp` runs.

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

The harness startup helpers now do this automatically and fail closed by
default if passwordless sudo cannot run the reclaim step. Use
`REQUIRE_DROP_CACHES=0` only for a dedicated diagnostic environment where the
missing reclaim is intentional and recorded. The helpers print
`before_drop_caches` and `after_drop_caches` `MemAvailable` lines so a failed or
ineffective reclaim is visible in the artifact log.

For large-context runs, also fail closed if the current boot already contains
NVIDIA driver OOM messages:

```bash
ssh "$HEAD_HOST" "journalctl -b -k --no-pager | grep -E 'NVRM:.*(Out of memory|NV_ERR_NO_MEMORY)'"
ssh "$WORKER_HOST" "journalctl -b -k --no-pager | grep -E 'NVRM:.*(Out of memory|NV_ERR_NO_MEMORY)'"
```

If either command finds a match after a failed launch, reboot both nodes before
retrying. `drop_caches` can reclaim file cache, but it does not prove that CUDA
driver or unified-memory state recovered after an `NV_ERR_NO_MEMORY` storm.

Docker adds another capacity variable on GB10. It does not virtualize away GPU
memory, but image layers, `docker load`/export activity, overlayfs metadata,
container Python packages, and FlashInfer/Triton cache state can all reduce the
unified-memory headroom that vLLM sees during KV-cache profiling. After building
or loading a large image, reclaim file cache on every node before starting the
containerized server. For long-context Docker runs, avoid Docker memory limits
unless that is the test objective, and record these values before comparing with
bare metal:

```bash
awk '/MemAvailable/ { printf "MemAvailable=%.1f GiB\n", $2 / 1024 / 1024 }' /proc/meminfo
docker system df
grep -E 'Available KV cache memory|GPU KV cache size|Maximum concurrency' <serve-log>
journalctl -b -k --no-pager | grep -Ei 'NVRM|Xid|fallen|lost from the bus|NV_ERR'
```

Treat Docker and bare metal as separate capacity profiles on GB10. A
short-context Docker benchmark can be comparable to bare metal, but the maximum
safe `max_model_len` must be established with a Docker-specific ceiling sweep
after cache reclaim. Do not reuse a bare-metal 64K/128K claim for Docker unless
the containerized run logs enough KV-cache headroom for that exact shape.

External Docker field reports on the current PR head found that
`gpu_memory_utilization=0.975` is too aggressive for some GB10 container
profiles even when the same model can run on bare metal. A 131K TP=2 / MTP=2 /
FP8-KV Docker profile started cleanly at `gpu_memory_utilization=0.85` after
cache hygiene. Treat `0.85` as a Docker-specific starting point, then raise only
after recording `MemAvailable`, KV-cache capacity lines, and driver health for
that container.

First-time GB10 Docker startup can be much slower than routine bare-metal
startup because aarch64 Torch/Triton caches are populated from scratch. If a
fresh image is expected to JIT, use a much larger startup timeout for that first
run, preserve the cache, and rerun the same command before classifying the
serve profile as slow or broken. Later cached starts should use the normal
bounded startup timeout again.

For a reusable guarded startup, run the harness helper from the control machine
after exporting the placeholders above. Use the no-Ray helper for the standard
GB10 path:

```bash
TP_SIZE=2 \
PP_SIZE=1 \
MAX_MODEL_LEN=393216 \
GPU_MEMORY_UTILIZATION=0.70 \
MAX_NUM_SEQS=1 \
MAX_NUM_BATCHED_TOKENS=4176 \
MIN_AVAILABLE_MEM_GIB=96 \
scripts/dgx_spark_start_mp_serve.sh
```

For 100K-class or larger long-prefill validation on the current two-node GB10
cluster, the product target is recommended C=2 and planned maximum C=4.
`MAX_NUM_SEQS=1` remains the conservative availability fallback. After the vLLM
very-long prefill admission guard, `MAX_NUM_SEQS=2` is also covered by the
reduced long-C=2 gate below and should be rerun before changing scheduler or
sparse-MLA behavior. C=4 on GB10 is a follow-up reliability gate, not a
throughput claim, until long-C=2 pressure no longer shows the high-SM /
no-progress failure mode.

```bash
GB10_LONG_C2_VARIANTS=nomtp,mtp2 \
GB10_LONG_C2_MAX_NUM_SEQS=2 \
GB10_LONG_C2_MAX_MODEL_LEN=131072 \
GB10_LONG_C2_MAX_NUM_BATCHED_TOKENS=4176 \
scripts/run_gb10_long_c2_reduced_gate.sh
```

This wrapper starts the same no-Ray MP server through
`scripts/dgx_spark_start_mp_serve.sh`, runs the `long_c2:2:2:4000:128`
streaming-pressure matrix on the head node, stops the server, repeats for MTP=2,
and writes a combined summary. It intentionally keeps prefix cache disabled,
expert parallel enabled, and CUDA graph mode `FULL_AND_PIECEWISE`.

Latest reduced-gate artifacts:

- `20260601_gb10_longc2_guard_nomtp`: 4/4 requests completed, max TTFT
  `237.836 s`, ITL p99 `0.604 s`, no runtime or driver error signal.
- `20260601_gb10_longc2_guard_mtp2`: 4/4 requests completed, max TTFT
  `234.728 s`, ITL p99 `2.220 s`, no runtime or driver error signal.

These runs validate the 131K-class reduced shape only. They do not justify a
256K+/512K/1M or four-card customer commitment; those need separate gates on the
target topology. After a fresh OS install or NIC reconfiguration, re-discover
the active RoCE interface and HCA with `ip -br addr` and `ibdev2netdev` instead
of reusing old local values.

The helper stops stale drop-cache loops, refuses to continue if vLLM is already
running unless `ALLOW_EXISTING_VLLM=1`, reclaims file cache by default, fails if
passwordless sudo cannot run `drop_caches` unless `REQUIRE_DROP_CACHES=0`,
checks `torch`/`vllm`/`ninja` imports through the vLLM Python executable,
rejects a current boot with NVIDIA driver OOM by default, verifies
`MemAvailable`, starts a headless worker and API head with
`--distributed-executor-backend mp --nnodes 2`, and polls `/health`.
It does not set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` by default;
export allocator settings only for a dedicated diagnostic experiment.

Use the Ray helper only when validating the Ray path:

```bash
MIN_AVAILABLE_MEM_GIB=96 \
scripts/dgx_spark_start_ray_cluster.sh
```

The helper stops Ray, reclaims file cache by default, fails if passwordless sudo
cannot run `drop_caches` unless `REQUIRE_DROP_CACHES=0`, checks imports through
the vLLM Python executable on both nodes, rejects a current boot with NVIDIA
driver OOM by default, checks `MemAvailable`, starts Ray through
`$VLLM_VENV/bin/python -m ray.scripts.scripts`, and prints `ray status`.

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

For routine GB10 validation, keep the public profile free of graph-disabling or
NCCL graph workaround switches. MTP should remain an exploratory GB10 variant
until longer generation survives without `sample_tokens` RPC timeouts. If a
graph-safety experiment needs private knobs, keep them in ignored local notes or
one-off shell exports and preserve the failing artifacts separately from routine
startup evidence.

Known NCCL-sensitive failure symptoms observed on GB10 were intermittent MTP or
TP=2 generation stalls where vLLM stopped making decode progress, logs repeated
`No available shared memory broadcast block found in 60 seconds`, and EngineCore
later timed out in `sample_tokens` or returned HTTP 500 / connection refused
after shutdown. Treat those as distributed-runtime liveness failures first:
capture NCCL version, NCCL debug logs when enabled, serve logs, `/metrics`, and
the exact bench/eval concurrency shape before changing model code. If the node is
not already on the current NCCL build, upgrade NCCL and rerun the same repro
before adding CUDA graph or scheduler workarounds.

After startup, run at least one generation smoke and the harness long-context
sentinel probe. For the current GB10 acceptance gate, source
`configs/gb10_sm121_serve.env.example` from the harness checkout first, or pass
the equivalent no-thinking 128K-class settings explicitly:

```bash
curl -fsS http://127.0.0.1:8000/v1/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-ai/DeepSeek-V4-Flash","prompt":"Write one short sentence about distributed inference.","max_tokens":24,"temperature":0}'

PYTHON="$VLLM_VENV/bin/python" \
BASE_URL=http://127.0.0.1:8000 \
MODEL="$MODEL_ID" \
LONG_CONTEXT_VARIANT=nomtp \
LONG_CONTEXT_LINE_COUNT=4226 \
LONG_CONTEXT_MAX_TOKENS=128 \
LONG_CONTEXT_THINKING_MODE=non-thinking \
LONG_CONTEXT_TIMEOUT=2400 \
scripts/run_long_context_probe.sh
```

The 4226-line probe is the current GB10 128K-class no-MTP gate. `think-high`
and MTP can be recorded as exploratory allowed-failure runs on GB10, but
`think-max` is not a GB10 gate until a 384K+ prompt is reliable. The wrapper
invokes the `long-context-probe` CLI command and records GPU/runtime telemetry
beside the probe JSON and Markdown outputs.

For very long-context TTFT exploration, prefer the latency matrix wrapper with
`LONG_CONTEXT_LATENCY_EVALUATION_MODE=ttft-only` and a tiny output budget such
as `LONG_CONTEXT_LATENCY_MAX_TOKENS=1`. This mode records TTFT without turning
the intentionally truncated answer into a semantic failure. Keep the default
`semantic` mode for correctness gates and for all prompt-file semantic checks.

For 512K / 768K / 1M frontier work, use the dedicated very-long-context wrapper
instead of extending the routine 131K gate:

```bash
TP_SIZE=2 \
PP_SIZE=1 \
MAX_MODEL_LEN=1048576 \
MAX_NUM_SEQS=1 \
MAX_NUM_BATCHED_TOKENS=4096 \
SERVE_PREFIX_CACHE_MODE=disabled \
SERVE_ENABLE_EXPERT_PARALLEL=1 \
SERVE_COMPILATION_CONFIG='{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
scripts/dgx_spark_start_mp_serve.sh

PYTHON="$VLLM_VENV/bin/python" \
TARGET_PYTHON="$VLLM_VENV/bin/python" \
BASE_URL=http://127.0.0.1:8000 \
MODEL="$MODEL_ID" \
SERVE_LOG="$RUN_DIR/head.log" \
VERY_LONG_CONTEXT_TARGETS=524288,786432,1048576 \
VERY_LONG_CONTEXT_MAX_TOKENS=16 \
VERY_LONG_CONTEXT_EVALUATION_MODE=ttft-only \
scripts/run_sm12x_very_long_context_frontier.sh
```

On GB10, first treat this as an availability and speed-meaningfulness probe:
startup capacity must log enough KV tokens for the target, then 512K C=1 should
complete before trying 1M C=1. Keep `drop_caches` enabled through the startup
helper, record `MemAvailable` and current-boot NVIDIA driver health, and keep
partial artifacts when a 1M run is too slow or times out. If TTFT scales roughly
linearly with prompt tokens and driver/runtime health stays clean, the result is
probably exposing the GB10 hardware/interconnect envelope. If the curve becomes
super-linear, the server shows high-SM/no-token-progress, or CUDA/NCCL/NVRM/UVM
signals appear, treat it as an implementation or runtime problem before making
customer-facing 1M claims.

The first 1M frontier run on the current GB10 / SM121 cluster showed that
`gpu_memory_utilization=0.70` is too low for MTP=2 1M startup: vLLM estimated
`980,992` as the maximum model length. Retrying with
`gpu_memory_utilization=0.75` admitted 1M C=1/C=2 by capacity
(`2,176,643` KV tokens, estimated 1M concurrency `2.08`) and completed a cold
512K/1M latency probe. The measured TTFT was about `1,083s` at 512K and
`3,504s` at 1M, so 1M is a valid availability probe but not an interactive
latency claim under this profile.

For generation quality gates, keep `GENERATION_MAX_CASE_TOKENS=32768` or
higher on GB10. The checked-in frontend and code prompts can legitimately need
more than 4096 completion tokens; a 4096 cap is useful only for quick smoke and
turns `finish_reason=length` into a budget diagnostic, not model-quality
evidence.

## Start A Clean Ray Cluster

Start Ray on the RoCE IPs and make sure each node advertises one GPU. Run this
from the control machine:

```bash
ssh "$HEAD_HOST" "
  set -euo pipefail
  '$RAY_PYTHON' -m ray.scripts.scripts stop --force || true
  env \
    PATH='$VLLM_VENV/bin:/usr/local/cuda/bin:'\"\$PATH\" \
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
    PATH='$VLLM_VENV/bin:/usr/local/cuda/bin:'\"\$PATH\" \
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
    PATH='$VLLM_VENV/bin:/usr/local/cuda/bin:'\"\$PATH\" \
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

## Forum #53 Multi-User Prefix-Cache Gate

Use `scripts/run_gb10_forum53_multi_user_gate.sh` for the
forum53 multi-user prefix-cache gate. This is a user-feedback reproduction gate
for the report where a newer image improved single-user prefill but collapsed
6-8 concurrent workers into one active request.

Default shape:

- `TP=2`, `PP=1`, expert parallel enabled.
- Prefix cache enabled.
- `max_model_len=262144`.
- `max_num_seqs=8`.
- `gpu_memory_utilization=0.90`.
- `FULL_AND_PIECEWISE` CUDA graph mode.
- no-MTP first; set `GB10_FORUM53_OPTIONAL_MTP2=1` to append the MTP=2
  stability comparison.
- `max_num_batched_tokens` sweep:
  `2048,3072,4096,6144,8192`.
- Streaming matrix cases:
  `forum53_c6:6:1:3200:128,forum53_c8:8:1:3200:128`.

The summary files are
`gb10_forum53_multi_user_gate_summary.json` and
`gb10_forum53_multi_user_gate_summary.md`. Inspect `running_requests_max`,
`waiting_requests_max`, `gpu_kv_cache_usage_percent_max`, TTFT, ITL p99,
prefix-cache hits, and preemptions before deciding whether a regression is in
scheduler admission, KV capacity, prefix-cache retention, or MTP stability.

## Common Failure Modes

- CUDA memory guard fails immediately after file copies or failed launches:
  reclaim page cache on both nodes with `drop_caches`, then retry. The harness
  GB10 startup helpers require this by default; use `REQUIRE_DROP_CACHES=0`
  only for an explicitly recorded diagnostic run.
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
- MTP starts, then stalls or becomes unresponsive under concurrent streaming:
  rerun the same shape without MTP and preserve the failing artifacts as an MTP
  liveness reproduction instead of treating it as a general GB10 startup
  failure.
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
