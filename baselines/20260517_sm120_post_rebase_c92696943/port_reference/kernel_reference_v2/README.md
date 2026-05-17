# Kernel Reference v2 (Port-Team Ground Truth)

Synthetic-input, synthetic-output kernel-level reference for the three
SM12x-specific kernels that don't have a clean upstream analogue. Intended
for port teams (SGLang, TokenSpeed, and downstream forks) reproducing
DSv4-Flash kernels on Blackwell consumer hardware.

Each `.npz` file packs `(inputs_dict, expected_output)` for one (kernel,
shape) pair. Atol/rtol tolerances for parity comparison are recorded in
`manifest.json` per kernel.

## Kernels covered

1. **`accumulate_indexed_sparse_mla_attention_chunk_multihead`** — multi-head
   prefill accumulate kernel from [`jasl/vllm` PR #6](https://github.com/jasl/vllm/pull/6)
   (HEAD_BLOCK=8). Used in the C128A prefill path; drops long-context prefill
   TTFT ~20–23% on this hardware vs the per-head loop.

2. **`deepseek_v4_sm12x_fp8_einsum`** — 3D mHC einsum `bhr,hdr->bhd` over
   `(num_tokens, num_groups, hidden) × (num_groups, out_rank, hidden)` with
   FP8 e4m3 packing and fp32 block scales. Called from the MLA decode kernel
   on SM12x where `tcgen05` and the TMEM-based path don't exist.

3. **`dequantize_and_gather_k_cache`** — gathers + dequantises packed FP8 KV
   cache for sparse MLA. `head_bytes = nope_head_dim + 2*rope_head_dim +
   nope_head_dim//64 + pad = 448 + 64 + 7 + 1 = 520` (or 576/584 with
   alignment), output is bf16 `[num_reqs, max_num_tokens, head_size]`.

## Shapes

Two shape buckets per kernel: `small` (decode-step-like, single-digit token
counts) and `medium` (short-prefill-like, 128-token batches). Both are
contained representative reference points; port teams should regression-test
against both.

## Files

| File | Size |
| --- | ---: |
| `manifest.json` | metadata + per-kernel atol/rtol tolerances |
| `accumulate_indexed_sparse_mla_attention_chunk_multihead__small.npz` | 4.0 MiB |
| `accumulate_indexed_sparse_mla_attention_chunk_multihead__medium.npz` | 4.9 MiB |
| `deepseek_v4_sm12x_fp8_einsum__small.npz` | 1.8 MiB |
| `deepseek_v4_sm12x_fp8_einsum__medium.npz` | 5.1 MiB |
| `dequantize_and_gather_k_cache__small.npz` | 11.3 MiB |
| `dequantize_and_gather_k_cache__medium.npz` | 44 MiB |

Total: ~71 MiB.

## Reproducing

```bash
python3 scripts/dump_kernel_reference.py --output-dir <out>
```

Captured under `vllm@c92696943` with PyTorch 2.11.0+cu130, Triton 3.6.0, on
2× RTX PRO 6000 Blackwell Workstation Edition (cc=12.0). Outputs are
deterministic given a fixed seed (default 0).
