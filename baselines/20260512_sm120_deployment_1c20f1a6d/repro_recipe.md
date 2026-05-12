# Reproduction Recipe — SM120 Workstation Deployment

vLLM SHA: `1c20f1a6d` on `jasl/vllm` `ds4-sm120-preview-dev` (PR
#41834). Harness SHA: the commit that ships this directory.

## Workstation hardware

Two NVIDIA RTX PRO 6000 Blackwell Workstation Edition cards (compute
capability 12.0). No display attached. TP=2 EP, no PP.

## Conversation profile

### Start serve

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

### Bench

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

Same as Conversation, with:
```
  --max-model-len 32768 --max-num-seqs 4
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
