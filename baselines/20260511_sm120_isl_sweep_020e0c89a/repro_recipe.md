# SM120 Reproduction Recipe — 2026-05-11

Single-host, 2x RTX Pro 6000 Blackwell Workstation Edition (SM120, cc 12.0),
TP=2 EP.

## Code

```
git clone https://github.com/jasl/vllm.git
cd vllm
git checkout 020e0c89a   # head of jasl:ds4-sm120-preview-dev / PR #41834

export TORCH_CUDA_ARCH_LIST=12.0a
export PATH=/usr/local/cuda/bin:$PATH
export CUDA_HOME=/usr/local/cuda
export TRITON_PTXAS_PATH=$CUDA_HOME/bin/ptxas
export CCACHE_NOHASHDIR=true
pip install --verbose --no-build-isolation -e .
```

## Serve (no-MTP)

```
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --trust-remote-code \
  --kv-cache-dtype fp8 --block-size 256 \
  --max-model-len 65536 --tensor-parallel-size 2 \
  --host 127.0.0.1 --port 8000 \
  --no-enable-flashinfer-autotune \
  --reasoning-parser deepseek_v4 \
  --tokenizer-mode deepseek_v4 \
  --tool-call-parser deepseek_v4 --enable-auto-tool-choice \
  --reasoning-config '{"reasoning_parser":"deepseek_v4","reasoning_start_str":"<think>","reasoning_end_str":"</think>"}' \
  --enable-expert-parallel \
  --gpu-memory-utilization 0.95 \
  --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"]}'
```

For MTP=2, append:

```
  --speculative_config '{"method":"mtp","num_speculative_tokens":2}'
```

## Bench (random shape)

```
vllm bench serve --model deepseek-ai/DeepSeek-V4-Flash \
  --tokenizer-mode deepseek_v4 \
  --base-url http://127.0.0.1:8000 \
  --dataset-name random --random-input-len 8192 --random-output-len 512 \
  --num-prompts 24 --max-concurrency 24 \
  --ignore-eos --temperature 1.0
```

Vary `--random-input-len ∈ {1024, 4096, 8192}` and
`--max-concurrency ∈ {1, 2, 4, 8, 16, 24}`. Keep `--num-prompts ≥
max-concurrency` so the bench has at least one full batch.

## Bench (HF mt-bench)

```
vllm bench serve --model deepseek-ai/DeepSeek-V4-Flash \
  --tokenizer-mode deepseek_v4 \
  --base-url http://127.0.0.1:8000 \
  --dataset-name hf --dataset-path philschmid/mt-bench --num-prompts 80 \
  --max-concurrency 24 --temperature 1.0
```

No `--ignore-eos` here; mt-bench prompts produce ~190 output tokens naturally.

## Determinism

Output throughput stable to ~5 % run-to-run. TTFT can swing more at high
concurrency depending on prefill scheduling order. For exact-token oracle
comparisons use the B200 TP=4 baseline at
`baselines/20260502_b200_tp4_main_5737770c6/oracle/`.
