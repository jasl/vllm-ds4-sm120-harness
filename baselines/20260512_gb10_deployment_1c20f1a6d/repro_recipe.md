# Reproduction Recipe — GB10 Spark Deployment

vLLM SHA: `1c20f1a6d` on `jasl/vllm` `ds4-sm120-preview-dev` (PR
#41834). Harness SHA: the commit that ships this directory.

## Cluster hardware

Two NVIDIA DGX Spark nodes, each with one GB10 (compute capability
12.1, 128 GiB unified memory). Nodes connected by a RoCE link
(`enp1s0f1np1` iface, HCA `rocep1s0f1`). vLLM TP=2 PP=1 mp across
both nodes.

## Conversation profile

### Start cluster (from control host)

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

Drop `SERVE_SPECULATIVE_CONFIG` for the no-MTP variant.

### Bench (executed on the head node)

```bash
for c in 1 2 4 8; do
  vllm bench serve \
    --model deepseek-ai/DeepSeek-V4-Flash --tokenizer-mode deepseek_v4 \
    --dataset-name hf --dataset-path philschmid/mt-bench \
    --num-prompts 80 --max-concurrency "${c}" \
    --base-url http://127.0.0.1:8000 --temperature 1.0
done
```

## Agent profile

Same launch script, with:
```
MAX_MODEL_LEN=65536 MAX_NUM_SEQS=4
```
and `--concurrency 1,2,4` in the bench loop.

## gsm8k

```bash
lm_eval --model local-completions \
  --model_args 'model=deepseek-ai/DeepSeek-V4-Flash,base_url=http://127.0.0.1:8000/v1/completions,num_concurrent=2,max_retries=10,tokenized_requests=False,tokenizer_backend=none,max_gen_toks=2048,timeout=300' \
  --tasks gsm8k --num_fewshot 5 --batch_size auto --limit 200 \
  --output_path /tmp/gsm8k_raw
```

## Generation reference

```bash
python -m ds4_harness.cli generation-matrix \
  --prompt-root /path/to/harness/prompts \
  --prompt aquarium_html --prompt en2zh_news_001 --prompt zh_sum_tech_001 \
  --thinking-mode non-thinking \
  --variant mtp2-conv \
  --base-url http://127.0.0.1:8000 \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --max-tokens 4096 --max-case-tokens 6000 --temperature 1.0 \
  --repeat-count 1 \
  --jsonl-output transcripts/results.jsonl \
  --markdown-output-dir transcripts
```

## Recovering from an NVRM OOM on a worker

The DGX Spark NVRM allocator can latch into a stuck state after an
OOM; the launcher's preflight refuses to start a new cluster until
the node is rebooted. If you hit this, on the affected node:

```bash
sudo systemctl reboot
# wait ~2 minutes for SSH to come back
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
```

Then re-run the cluster launcher.

## Data files

```
performance/
  conv/{nomtp,mtp2}_bench.json         # c=1,2,4,8 mt-bench
  agent/{nomtp,mtp2}_bench.json        # c=1,2,4 mt-bench
evals/
  gsm8k/{nomtp,mtp2}.json
generation/
  {en,zh}/<case>.1.non-thinking.mtp2-conv.md
  {en,zh}/aquarium_html.1.non-thinking.mtp2-conv.html
  results.jsonl
report.md
repro_recipe.md
```
