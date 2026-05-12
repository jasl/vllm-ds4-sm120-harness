# Reproduction Recipe

vLLM SHA: `2760932cf` on `jasl/vllm` branch `ds4-sm120-preview-dev`.
Harness SHA: same commit that ships this directory.

## Workstation SM120 (2x RTX PRO 6000 Blackwell Workstation Edition)

### Start serve (no-MTP)

```bash
/path/to/vllm/.venv/bin/vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 --block-size 256 \
  --max-model-len 65536 --tensor-parallel-size 2 \
  --host 127.0.0.1 --port 8000 \
  --no-enable-flashinfer-autotune \
  --reasoning-parser deepseek_v4 \
  --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 --enable-auto-tool-choice \
  --enable-expert-parallel \
  --gpu-memory-utilization 0.95
```

For MTP=2, append:

```
--speculative_config '{"method":"deepseek_mtp","num_speculative_tokens":2}'
```

### Bench (c=1,2,4)

`vllm bench serve` is invoked through the harness `bench-matrix` driver to
get the JSON-shaped output recorded in `performance/sm120_workstation/`.
Equivalent direct command:

```bash
for c in 1 2 4; do
  /path/to/vllm/.venv/bin/vllm bench serve \
    --model deepseek-ai/DeepSeek-V4-Flash \
    --tokenizer-mode deepseek_v4 \
    --dataset-name hf --dataset-path philschmid/mt-bench \
    --num-prompts 80 --max-concurrency "${c}" \
    --base-url http://127.0.0.1:8000 --temperature 1.0
done
```

### gsm8k 200q

```bash
/path/to/vllm/.venv/bin/lm_eval \
  --model local-completions \
  --model_args 'model=deepseek-ai/DeepSeek-V4-Flash,base_url=http://127.0.0.1:8000/v1/completions,num_concurrent=2,max_retries=10,tokenized_requests=False,tokenizer_backend=none,max_gen_toks=2048,timeout=300' \
  --tasks gsm8k --num_fewshot 5 \
  --batch_size auto --limit 200 \
  --output_path /tmp/gsm8k_raw
```

## DGX Spark cluster (2 nodes, 1x GB10 each, TP=2 PP=1 mp over RoCE)

### Start cluster from a control host

```bash
HEAD_HOST=10.0.0.116 WORKER_HOST=10.0.0.118 \
HEAD_ROCE_IP=169.254.116.28 WORKER_ROCE_IP=169.254.117.143 \
ROCE_IFACE=enp1s0f1np1 NCCL_IB_HCA=rocep1s0f1 \
VLLM_ROOT=/home/jasl/Workspace/vllm \
VLLM_VENV=/home/jasl/Workspace/vllm/.venv \
TP_SIZE=2 PP_SIZE=1 \
MAX_MODEL_LEN=131072 GPU_MEMORY_UTILIZATION=0.85 \
MAX_NUM_SEQS=4 MAX_NUM_BATCHED_TOKENS=8192 \
BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8 \
SERVE_ENABLE_EXPERT_PARALLEL=1 \
SERVE_DISABLE_FLASHINFER_AUTOTUNE=1 \
SERVE_COMPILATION_CONFIG='{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
NCCL_IB_DISABLE=0 NCCL_DEBUG=WARN \
RUN_DIR=/tmp/spark_tp2_serve \
STARTUP_TIMEOUT=900 MIN_AVAILABLE_MEM_GIB=96 \
scripts/dgx_spark_start_mp_serve.sh
```

For MTP=2, add:

```
SERVE_SPECULATIVE_CONFIG='{"method":"deepseek_mtp","num_speculative_tokens":2}'
```

### NCCL transport

`NCCL_IB_DISABLE=0` (the harness default) uses IB verbs over the RoCE HCA
and is 31 % faster at c=1 than the TCP fallback (`NCCL_IB_DISABLE=1`).
Override only if the IB stack on the host is unavailable.

### Bench + gsm8k

Run the same `vllm bench serve` and `lm_eval` blocks as the Workstation
recipe, on the head node, against `http://127.0.0.1:8000`.

## Long prefill sweep (TTFT vs ISL, c=1, OSL=8, num-prompts=1)

Same serve as the mt-bench runs; switch the dataset and shape:

```bash
for ISL in 1024 4096 8192 16384 32768 65536 131000; do
  /path/to/vllm/.venv/bin/vllm bench serve \
    --model deepseek-ai/DeepSeek-V4-Flash \
    --tokenizer-mode deepseek_v4 \
    --dataset-name random \
    --random-input-len "${ISL}" --random-output-len 8 \
    --num-prompts 1 --max-concurrency 1 \
    --base-url http://127.0.0.1:8000 \
    --temperature 1.0 --ignore-eos
done
```

The Workstation serve uses `max-model-len 65536`, so cap ISL at 65,000;
Spark uses `max-model-len 131072` and runs the full sweep.

## Random ISL=8,192 OSL=512 bench (Spark MTP=2)

Same Spark MTP=2 serve as the mt-bench runs; swap dataset:

```bash
/path/to/vllm/.venv/bin/vllm bench serve \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --tokenizer-mode deepseek_v4 \
  --dataset-name random \
  --random-input-len 8192 --random-output-len 512 \
  --num-prompts 4 --max-concurrency "${c}" \
  --base-url http://127.0.0.1:8000 \
  --temperature 1.0 --ignore-eos
```

## Data files in this bundle

```
performance/
  sm120_workstation/
    nomtp_bench.json                       # c=1,2,4 mt-bench, no-MTP
    mtp2_bench.json                        # c=1,2,4 mt-bench, MTP=2
    prefill_sweep/isl_{1024,4096,8192,16384,32768,65000}.json
  gb10_spark/
    nomtp_ib0_bench.json                   # c=1,2,4 mt-bench, no-MTP
    mtp2_ib0_bench.json                    # c=1,2,4 mt-bench, MTP=2
    random/mtp2_random_isl8192_osl512_bench.json
    prefill_sweep/isl_{1024,4096,8192,16384,32768,65536,131000}.json
evals/
  gsm8k/
    sm120_workstation_nomtp.json
    sm120_workstation_mtp2.json
    gb10_spark_nomtp_ib0.json
    gb10_spark_mtp2_ib0.json
report.md
repro_recipe.md
raw_metrics.md
```
