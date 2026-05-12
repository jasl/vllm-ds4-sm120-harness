# Reproduction Recipe

vLLM SHA: `5c8975591` on `jasl/vllm` `ds4-sm120-preview-dev`.
Harness SHA: the commit that ships this directory.

Every cell below is a fresh `vllm serve` instance benchmarked
end-to-end with mt-bench + gsm8k. The four profiles are: Workstation
Conversation, Workstation Agent, Spark Conversation, Spark Agent —
each in `{no-MTP, MTP=2}` variants.

## Workstation SM120 — Conversation profile

```bash
nohup /path/to/vllm/.venv/bin/vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 --block-size 256 \
  --max-model-len 16384 --max-num-seqs 8 \
  --tensor-parallel-size 2 \
  --host 127.0.0.1 --port 8000 \
  --no-enable-flashinfer-autotune \
  --reasoning-parser deepseek_v4 --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 --enable-auto-tool-choice \
  --enable-expert-parallel \
  --gpu-memory-utilization 0.985 \
  ${MTP_FLAG:-} \
  > /tmp/serve.log 2>&1 &
# MTP_FLAG="--speculative_config '{\"method\":\"deepseek_mtp\",\"num_speculative_tokens\":2}'"
```

Bench:

```bash
for c in 1 2 4 8; do
  vllm bench serve \
    --model deepseek-ai/DeepSeek-V4-Flash --tokenizer-mode deepseek_v4 \
    --dataset-name hf --dataset-path philschmid/mt-bench \
    --num-prompts 80 --max-concurrency "${c}" \
    --base-url http://127.0.0.1:8000 --temperature 1.0
done
```

## Workstation SM120 — Agent profile

Same as Conversation, with:
```
  --max-model-len 32768 --max-num-seqs 4
```
and `--concurrency 1,2,4` in the bench loop.

## DGX Spark cluster — Conversation profile

```bash
HEAD_HOST=10.0.0.116 WORKER_HOST=10.0.0.118 \
HEAD_ROCE_IP=169.254.116.28 WORKER_ROCE_IP=169.254.117.143 \
ROCE_IFACE=enp1s0f1np1 NCCL_IB_HCA=rocep1s0f1 \
VLLM_ROOT=/home/jasl/Workspace/vllm \
VLLM_VENV=/home/jasl/Workspace/vllm/.venv \
TP_SIZE=2 PP_SIZE=1 \
MAX_MODEL_LEN=32768 MAX_NUM_SEQS=8 \
MAX_NUM_BATCHED_TOKENS=8192 \
GPU_MEMORY_UTILIZATION=0.85 \
BLOCK_SIZE=256 KV_CACHE_DTYPE=fp8 \
SERVE_ENABLE_EXPERT_PARALLEL=1 \
SERVE_DISABLE_FLASHINFER_AUTOTUNE=1 \
SERVE_COMPILATION_CONFIG='{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}' \
SERVE_SPECULATIVE_CONFIG='{"method":"deepseek_mtp","num_speculative_tokens":2}' \
NCCL_IB_DISABLE=0 NCCL_DEBUG=WARN \
RUN_DIR=/tmp/spark_tp2_serve \
STARTUP_TIMEOUT=900 MIN_AVAILABLE_MEM_GIB=96 \
scripts/dgx_spark_start_mp_serve.sh
```

(Remove `SERVE_SPECULATIVE_CONFIG` for the no-MTP variant.)

Bench is the same as Workstation, executed on head node `10.0.0.116`.

## DGX Spark cluster — Agent profile

Same as Spark Conversation, with:
```
MAX_MODEL_LEN=65536 MAX_NUM_SEQS=4
```
and `--concurrency 1,2,4`.

## gsm8k

```bash
lm_eval --model local-completions \
  --model_args 'model=deepseek-ai/DeepSeek-V4-Flash,base_url=http://127.0.0.1:8000/v1/completions,num_concurrent=2,max_retries=10,tokenized_requests=False,tokenizer_backend=none,max_gen_toks=2048,timeout=300' \
  --tasks gsm8k --num_fewshot 5 --batch_size auto --limit 200 \
  --output_path /tmp/gsm8k_raw
```

## Data files

```
performance/
  sm120_workstation/
    conv/{nomtp,mtp2}_bench.json         # c=1,2,4,8 mt-bench
    agent/{nomtp,mtp2}_bench.json        # c=1,2,4 mt-bench
  gb10_spark/
    conv/{nomtp,mtp2}_bench.json         # c=1,2,4,8 mt-bench
    agent/{nomtp,mtp2}_bench.json        # c=1,2,4 mt-bench
evals/
  gsm8k/
    sm120_workstation_{nomtp,mtp2}.json
    gb10_spark_{nomtp,mtp2}.json
report.md
repro_recipe.md
```
