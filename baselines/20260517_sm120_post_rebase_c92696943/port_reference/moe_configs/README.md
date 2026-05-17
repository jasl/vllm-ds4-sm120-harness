# Tuned Fused-MoE FP8 Block Configs

All 4 typical SM12x DSv4-Flash deployment shapes covered on
`NVIDIA_RTX_PRO_6000_Blackwell_Workstation_Edition`. **Before this bundle,
none of these shapes had a tuned config in the vLLM tree** — production
serves were using Triton's default heuristic for the dominant MoE kernel.

## Coverage matrix

| File (E, N, block) | Topology | Card count | Per-shape tune time |
| --- | --- | ---: | ---: |
| `E=128, N=2048, block=[128,128]` | **TP=2 + EP** (production) | 2× RTX PRO 6000 / 2-node GB10 | shape 1 of round 1 |
| `E=64,  N=2048, block=[128,128]` | TP=4 + EP | 4× RTX PRO 6000 / 4-node GB10 | 6411 s (1h47m) |
| `E=32,  N=2048, block=[128,128]` | TP=8 + EP | 8× RTX PRO 6000 / 8-node GB10 | 3602 s (1h00m) |
| `E=256, N=1024, block=[128,128]` | TP=2 no-EP fallback | 2× RTX PRO 6000 / 2-node GB10 | 8021 s (2h14m) |

All 4 files: vllm@c92696943, Triton 3.6.0, 10 M-buckets per shape
(`1, 2, 4, 8, 16, 32, 64, 128, 256, 512`), 640-config search space per M
filtered to BLOCK_SIZE_M ≥ M/8 for M ≥ 64.

`tuning_summary_shapes_2_4.json` archives the in-process summary from the
second tune session (shapes 2–4). Shape 1's summary is embedded in the
preceding bundle commit's session log.

## To deploy

Copy any/all 4 JSON files into your vLLM checkout's
`vllm/model_executor/layers/fused_moe/configs/` directory and restart
`vllm serve`. The runtime looks up by `device_name + (E, N, dtype, block)`
quadruple; no other change needed.

## Producing GB10-tagged equivalents

The same driver runs on a GB10 host and tags the output with
`device_name=NVIDIA_GB10`. Either run the default 4-shape sweep:

```bash
OUT_DIR=/path/out PYTHON=/path/.venv/bin/python \
  bash scripts/run_fp8_moe_tune.sh
```

…or pin a subset via `SHAPES="E,shard,hidden,topk:..."`. Total wall-clock
on a single GPU is ~3-5 h for all 4 shapes (RTX PRO 6000 reference: 300
min for shapes 2–4 with JIT cache warm; GB10 should be similar or slower
depending on memory bandwidth).
