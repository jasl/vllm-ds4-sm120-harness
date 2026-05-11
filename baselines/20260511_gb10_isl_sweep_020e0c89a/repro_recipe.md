# GB10 Reproduction Recipe — 2026-05-11

2-node DGX Spark cluster, 1x NVIDIA GB10 per node (SM121, cc 12.1), connected
by a high-speed RoCE link. TP=2 PP=1 via `--distributed-executor-backend mp
--nnodes 2`.

## Prerequisites (both nodes)

- NCCL upgraded to a recent NVIDIA build matching CUDA 13.2. Earlier NCCL is
  known to cause intermittent MTP `sample_tokens` RPC timeouts and decode
  stalls; see harness commit `9c41323 Document GB10 NCCL upgrade requirement`.
- Python development headers (`sudo apt install python3.12-dev python3-dev`)
  for Triton runtime helper compilation.

## Code

On each node:

```
git clone https://github.com/jasl/vllm.git
cd vllm
git checkout 020e0c89a   # head of jasl:ds4-sm120-preview-dev / PR #41834

export TORCH_CUDA_ARCH_LIST=12.1a
export PATH=/usr/local/cuda-13.2/bin:$PATH
export CUDA_HOME=/usr/local/cuda-13.2
export TRITON_PTXAS_PATH=$CUDA_HOME/bin/ptxas
export CCACHE_NOHASHDIR=true
pip install --verbose --no-build-isolation -e .
```

For no-MTP only, `5b59e2e60` is sufficient. MTP=2 requires `020e0c89a`.

## Reclaim unified-memory file cache (both nodes, before each launch)

```
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
```

This was observed to bring CUDA free memory from ~3 GiB back to ~115 GiB on
fresh boots; without it the GPU memory guard fails before model load.

## Start serve via the harness helper

From a control machine with SSH access to both nodes:

```
export HEAD_HOST=user@head
export WORKER_HOST=user@worker
export HEAD_ROCE_IP=<head roce ip>
export WORKER_ROCE_IP=<worker roce ip>
export ROCE_IFACE=<iface name>
export NCCL_IB_HCA=<hca name>
export VLLM_ROOT=/path/to/vllm
export VLLM_VENV=/path/to/vllm/.venv
export CUDA_HOME_REMOTE=/usr/local/cuda-13.2
export MODEL_ID=deepseek-ai/DeepSeek-V4-Flash
export API_HOST=0.0.0.0 API_PORT=8000
export TP_SIZE=2 PP_SIZE=1
export MAX_MODEL_LEN=131072
export GPU_MEMORY_UTILIZATION=0.85
export MAX_NUM_SEQS=4 MAX_NUM_BATCHED_TOKENS=8192
export BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8
export ALLOW_CURRENT_BOOT_NVRM_OOM=1 MIN_AVAILABLE_MEM_GIB=60
export SERVE_ENABLE_EXPERT_PARALLEL=1
export SERVE_DISABLE_FLASHINFER_AUTOTUNE=1
export SERVE_COMPILATION_CONFIG='{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}'
export SERVE_EXTRA_ARGS='--reasoning-config {"reasoning_parser":"deepseek_v4","reasoning_start_str":"<think>","reasoning_end_str":"</think>"}'

bash scripts/dgx_spark_start_mp_serve.sh
```

For MTP=2 also export:

```
export SERVE_SPECULATIVE_CONFIG='{"method":"mtp","num_speculative_tokens":2}'
```

The script orchestrates `nohup vllm serve ... --node-rank 1 --headless` on
the worker and `... --node-rank 0` on the head, polls `/health`, and prints
`worker_pid` + `head_pid` on success.

## Bench (random shape, from head node)

```
vllm bench serve --model deepseek-ai/DeepSeek-V4-Flash \
  --tokenizer-mode deepseek_v4 \
  --base-url http://127.0.0.1:8000 \
  --dataset-name random --random-input-len 8192 --random-output-len 512 \
  --num-prompts 4 --max-concurrency 4 \
  --ignore-eos --temperature 1.0
```

Vary `--random-input-len ∈ {1024, 4096, 8192}` and
`--max-concurrency ∈ {1, 2, 4}`. NVIDIA's reference uses num-prompts=8 for
ISL=1024 and num-prompts=4 for ISL=4096/8192; we matched that scheme.

## Bench (HF mt-bench)

```
vllm bench serve --model deepseek-ai/DeepSeek-V4-Flash \
  --tokenizer-mode deepseek_v4 \
  --base-url http://127.0.0.1:8000 \
  --dataset-name hf --dataset-path philschmid/mt-bench --num-prompts 40 \
  --max-concurrency 4 --temperature 1.0
```
