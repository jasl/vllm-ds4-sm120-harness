# Tuned Fused-MoE FP8 Block Configs (Production Shape)

Production shape `(E=128, N=2048, block=[128,128])` corresponds to DSv4-Flash
running with `--tensor-parallel-size 2 --enable-expert-parallel` on
`NVIDIA_RTX_PRO_6000_Blackwell_Workstation_Edition`. **No prior tuned config
existed in the vLLM tree for this shape** — until this run, our production
serve was using Triton's default heuristic for the dominant MoE kernel.

## File

`E=128,N=2048,device_name=NVIDIA_RTX_PRO_6000_Blackwell_Workstation_Edition,dtype=fp8_w8a8,block_shape=[128,128].json`

Tuned via `scripts/run_fp8_moe_tune.sh` on the same workstation at
vllm@c92696943, Triton 3.6.0. 10 M-buckets (1, 2, 4, 8, 16, 32, 64, 128, 256,
512) each with the best Triton config found across a 640-config search space
(filtered per-M to keep BLOCK_SIZE_M >= M/8).

To deploy: copy into `vllm/model_executor/layers/fused_moe/configs/` in your
vllm checkout and restart serve.

## What's not here (deferred)

The tune driver also covers TP=4+EP (`E=64, N=2048`), TP=8+EP (`E=32, N=2048`),
and TP=2 no-EP (`E=256, N=1024`) — useful for 4-card/8-card RTX PRO 6000 boxes
and 4-node/8-node GB10 clusters respectively. Those three shapes were not
finished in this round (terminated after shape 1 produced the
production-critical file). To extend coverage:

```bash
# Default 4-shape sweep (TP=2/4/8+EP, TP=2 no-EP), ~52 min:
OUT_DIR=/path/out PYTHON=/path/.venv/bin/python bash scripts/run_fp8_moe_tune.sh
```

Run on RTX PRO 6000 to fill the remaining 3 RTX PRO 6000 shapes, or on GB10
to produce the GB10-tagged equivalents.
