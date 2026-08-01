# GB10 4-node TP=4 DSpark — known-good reference config

Source: allenh1, [PR #41834 comment 5151513526](https://github.com/vllm-project/vllm/pull/41834#issuecomment-5151513526)
(2026-08-01), reporting a working 4x DGX Spark deployment on `d64074e6f0`
with `deepseek-ai/DeepSeek-V4-Flash-0731`.

Kept as a regression target: it is the only 4-node DSpark configuration we have
independent confirmation for, and it boots on the same hardware where
[comment 5151353498](https://github.com/vllm-project/vllm/pull/41834#issuecomment-5151353498)
reports two distinct startup failures. The delta between the two is the useful part.

## Why this config works where the other one does not

Four differences, in rough order of how much they likely matter:

| | works (allenh1) | fails (mzzhome-ai) |
|---|---|---|
| attention backend | `FLASHINFER_MLA_SPARSE_DSV4` | default, then `FLASHMLA_SPARSE_DSV4` |
| `VLLM_TRITON_MLA_SPARSE` | **`1`** | unset |
| executor | `ray` | `mp` |
| expert parallel | not enabled | `--enable-expert-parallel` |

`VLLM_TRITON_MLA_SPARSE=1` is the load-bearing one for the reported
`missing tile_sched entry` assertion: `is_triton_sparse_mla_enabled()` returns the
configured value when set, which keeps decode on the Triton sparse path and never
reaches the FlashMLA branch that asserts a tile-scheduler entry
(`build_tile_scheduler` deliberately returns all-`None` on capability family 120,
because FlashMLA itself only supports families 90/100). Leaving it unset means the
gate falls back to device detection, which is also `True` on SM12x — so this env is
belt-and-braces rather than the sole cause; the backend choice matters too.

## Configuration

```yaml
build:
  vllm-ref: d64074e6f07250f6cd072861aa3c389a929befb9
  deepgemm-ref: nv_dev
  rebuild: vllm + flashinfer

defaults:
  tensor_parallel: 4
  gpu_memory_utilization: 0.9
  max_model_len: 1048576
  block_size: 256
  max_num_seqs: 10
  max_num_batched_tokens: 4096
  num_speculative_tokens: 7     # see caveat below
```

```bash
env:
  TORCH_CUDA_ARCH_LIST: 12.1a
  VLLM_ALLOW_LONG_MAX_MODEL_LEN: 1
  VLLM_TRITON_MLA_SPARSE: 1
  VLLM_DEEPSEEK_V4_FLASHINFER_SM120_DECODE: 1
  VLLM_DEEPSEEK_V4_FLASHINFER_SM120_PREFILL: 1
  VLLM_USE_DEEP_GEMM: 0            # DeepGEMM scale-layout JIT fails on GB10 (CUDA_ERROR_INVALID_IMAGE)
  VLLM_MOE_USE_DEEP_GEMM: 1
  VLLM_USE_DEEP_GEMM_E8M0: 0
  DG_JIT_USE_NVRTC: "0"
  VLLM_USE_BREAKABLE_CUDAGRAPH: "0"
  VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS: "0"   # profiler reserved ~99% of budget -> 0.61 GiB KV
  PYTORCH_CUDA_ALLOC_CONF: "expandable_segments:True"
  VLLM_USE_FLASHINFER_SAMPLER: "1"
  VLLM_DSPARK_FORWARD_CUDAGRAPH: "1"
  VLLM_DSPARK_FORWARD_CUDAGRAPH_ALLOW_TP: "1"
```

```bash
vllm serve deepseek-ai/DeepSeek-V4-Flash-0731 \
  --async-scheduling \
  --attention-backend FLASHINFER_MLA_SPARSE_DSV4 \
  --block-size 256 \
  --compilation-config '{"cudagraph_mode":"FULL_AND_PIECEWISE","custom_ops":["all"],"cudagraph_capture_sizes":[6,12,18,24,30,36,42,48]}' \
  --distributed-executor-backend ray \
  --enable-chunked-prefill --enable-prefix-caching --enable-flashinfer-autotune \
  --gpu-memory-utilization 0.9 --kv-cache-dtype fp8 \
  --load-format instanttensor \
  --max-cudagraph-capture-size 48 \
  --max-model-len 1048576 --max-num-batched-tokens 4096 --max-num-seqs 10 \
  --reasoning-parser deepseek_v4 --tokenizer-mode deepseek_v4 --tool-call-parser deepseek_v4 \
  --speculative-config '{"method":"dspark","num_speculative_tokens":7,"draft_sample_method":"greedy"}' \
  --tensor-parallel-size 4 --trust-remote-code
```

## ★ Caveat on `num_speculative_tokens: 7`

This config uses 7 against a checkpoint whose `dspark_block_size` is 5, described
in the source as a design point. **Our measurements on 2x GB10 with 0731 do not
support it.** Draft positions 5 and 6 accepted **0.000 in every sample across four
configurations**, while mean acceptance length *fell*:

| | nst=5 | nst=7 |
|---|---|---|
| probabilistic | 2.19 (23.8%) | 2.03 (14.7%) |
| greedy | 2.11 (22.2%) | 1.75 (10.8%) |

So `nst=7` drafts 40% more tokens per step and accepts fewer of them. Use
`num_speculative_tokens = dspark_block_size`. Note this contradicts both the HF
model card and our own validator message, which says
"Use num_speculative_tokens=5 or larger (e.g. 7)".

Measured with `scripts/run_dspark_acceptance_probe.sh` on prose — predictable text
lets the Markov head reach 68-98% acceptance on its own and hides the effect.
