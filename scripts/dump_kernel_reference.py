#!/usr/bin/env python3
"""Dump (input, output) reference tensors for SM12x DSv4 hot kernels.

Why
---
Porting SM12x DSv4-Flash support to SGLang or TokenSpeed needs kernel-level
ground truth so the port team can answer "does my reimplementation produce
the same output for the same input?" without running an end-to-end serve.
Without it, kernel-level bugs hide behind end-to-end noise (sampling
randomness, FP non-determinism) and triage takes hours.

What
----
For each kernel in ``KERNELS`` below, this script:

  1. Synthesises deterministic input tensors at one or more representative
     shapes (the shapes DSv4-Flash actually hits at typical prompts).
  2. Runs the kernel on GPU 0.
  3. Saves the inputs and output as ``.npz`` archives, one per
     (kernel, shape) pair, plus a ``manifest.json`` summarising shapes,
     dtypes, and the SHA-256 of the output tensor.

Port consumers should load the ``.npz``, feed the same inputs into their
implementation, and compare against the saved output within a documented
floating-point tolerance (kernel-by-kernel — see ``manifest.json``).

Scope (v1, intentionally narrow)
--------------------------------
Top three kernels by impact on DSv4-Flash SM12x decode + prefill paths:

  - ``accumulate_indexed_sparse_mla_attention_chunk_multihead`` — sparse
    MLA prefill multi-head accumulate (HEAD_BLOCK=8, the alex PR #6 kernel)
  - ``_deepseek_v4_sm12x_fp8_einsum`` — FP8 mHC compute in mid-decode
  - ``dequantize_and_gather_k_cache`` — KV gather + dequant feeding both
    prefill and decode

Each runs at 2 shapes: ``small`` (single-token / single-request) and
``medium`` (typical prefill chunk).

Adding more kernels or shapes
-----------------------------
Extend the ``KERNELS`` list at the bottom. Each entry needs:
  - ``name`` (filename slug)
  - ``shapes`` (list of (shape_name, build_inputs_callable))
  - ``run`` (callable: inputs dict -> output tensor)
  - ``tolerance_hint`` (str, e.g., ``"atol=1e-3 rtol=1e-3"``)

Usage
-----
  python3 scripts/dump_kernel_reference.py \\
      --output-dir artifacts/kernel_reference \\
      [--gpu-id 0] [--seed 0]
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np
import torch

# Determinism: cudnn benchmark off, fixed seed below.
torch.backends.cudnn.benchmark = False


def _seed_all(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _tensor_to_numpy(tensor: torch.Tensor) -> np.ndarray:
    """Convert any tensor to a numpy-compatible array.

    Numpy lacks native bfloat16 / float8; upcast to float32 (or keep as
    uint8 for already-packed FP8) so the saved .npz is loadable without
    torch. The original dtype is recorded in the manifest for ports that
    need to round-trip into the source precision.
    """
    t = tensor.detach().cpu()
    if t.dtype is torch.bfloat16 or t.dtype is torch.float16:
        return t.to(torch.float32).numpy()
    if t.dtype in (torch.float8_e4m3fn, torch.float8_e5m2):
        # FP8 → store as raw bytes via uint8 view; manifest records dtype.
        return t.view(torch.uint8).numpy()
    return t.numpy()


def _hash_tensor(tensor: torch.Tensor) -> str:
    arr = _tensor_to_numpy(tensor)
    return hashlib.sha256(arr.tobytes()).hexdigest()


@dataclasses.dataclass
class KernelDump:
    name: str
    shape_name: str
    inputs: dict[str, torch.Tensor]
    output: torch.Tensor
    metadata: dict[str, Any]
    tolerance_hint: str

    def save(self, out_dir: Path) -> dict[str, Any]:
        out_dir.mkdir(parents=True, exist_ok=True)
        npz_path = out_dir / f"{self.name}__{self.shape_name}.npz"
        # bf16 / fp8 / etc. are upcast to fp32 or stored as uint8 bytes for
        # numpy compatibility; manifest records the original dtype.
        arrays = {
            f"input__{k}": _tensor_to_numpy(v)
            for k, v in self.inputs.items()
        }
        arrays["output"] = _tensor_to_numpy(self.output)
        np.savez_compressed(npz_path, **arrays)
        return {
            "kernel": self.name,
            "shape_name": self.shape_name,
            "npz": str(npz_path.name),
            "inputs": {
                k: {
                    "shape": list(v.shape),
                    "dtype": str(v.dtype),
                    "device": str(v.device),
                }
                for k, v in self.inputs.items()
            },
            "output": {
                "shape": list(self.output.shape),
                "dtype": str(self.output.dtype),
                "sha256": _hash_tensor(self.output),
            },
            "metadata": self.metadata,
            "tolerance_hint": self.tolerance_hint,
        }


# ============================================================
# Kernel 1: accumulate_indexed_sparse_mla_attention_chunk
# (alex's PR #6 multi-head version, HEAD_BLOCK=8)
# ============================================================


def _accumulate_inputs(shape: str, device: str) -> dict[str, torch.Tensor]:
    """Synthesise inputs for the multi-head sparse MLA accumulate kernel.

    DSv4-Flash uses:
      - 64 heads per rank at TP=2 (we use that as the canonical num_heads)
      - head_dim = 512 (latent dim for sparse MLA)
      - block size 256, topk_chunk_size = 256

    The "small" case is a single token with one chunk; "medium" is a
    PREFILL_CHUNK_SIZE=4 prefill batch with one TOPK_CHUNK_SIZE=256 worth
    of candidates per token.
    """
    if shape == "small":
        num_tokens, num_heads, head_dim, num_candidates = 1, 64, 512, 256
    elif shape == "medium":
        num_tokens, num_heads, head_dim, num_candidates = 4, 64, 512, 256
    else:
        raise ValueError(f"unknown shape `{shape}`")

    kv_pool = 4096  # KV cache row count
    q = torch.randn(num_tokens, num_heads, head_dim, dtype=torch.bfloat16, device=device)
    kv_flat = torch.randn(kv_pool, head_dim, dtype=torch.bfloat16, device=device)
    # Indices pick num_candidates rows from kv_pool, with -1 padding for the
    # last ~10% to exercise the "is_valid = kv_index >= 0" mask path.
    indices = torch.randint(0, kv_pool, (num_tokens, num_candidates), dtype=torch.int32, device=device)
    pad_count = max(1, num_candidates // 10)
    indices[:, -pad_count:] = -1
    # lens = num_candidates - pad_count for each token (early-exit signal)
    lens = torch.full((num_tokens,), num_candidates - pad_count, dtype=torch.int32, device=device)
    max_score = torch.full(
        (num_tokens, num_heads), float("-inf"), dtype=torch.float32, device=device
    )
    denom = torch.zeros(num_tokens, num_heads, dtype=torch.float32, device=device)
    acc = torch.zeros(num_tokens, num_heads, head_dim, dtype=torch.float32, device=device)

    return {
        "q": q,
        "kv_flat": kv_flat,
        "indices": indices,
        "lens": lens,
        "max_score": max_score,
        "denom": denom,
        "acc": acc,
    }


def _run_accumulate(inputs: dict[str, torch.Tensor]) -> torch.Tensor:
    from vllm.v1.attention.backends.mla.sparse_mla_kernels import (
        accumulate_indexed_sparse_mla_attention_chunk,
    )

    accumulate_indexed_sparse_mla_attention_chunk(
        q=inputs["q"],
        kv_flat=inputs["kv_flat"],
        indices=inputs["indices"],
        lens=inputs["lens"],
        scale=0.125,
        max_score=inputs["max_score"],
        denom=inputs["denom"],
        acc=inputs["acc"],
        candidate_offset=0,
    )
    # The kernel mutates acc in place. The full state is (max_score, denom,
    # acc) but the "output" for parity is the accumulated value tensor.
    return inputs["acc"]


# ============================================================
# Kernel 2: deepseek_v4_sm12x_fp8_einsum (FP8 mHC compute)
# ============================================================
#
# Signature: `(a, a_scale, b, b_scale, out)`. Computes the 3D einsum
# `bhr,hdr->bhd` where:
#   a       : [num_tokens, num_groups, hidden_size]  fp8_e4m3fn
#   b       : [num_groups, out_rank, hidden_size]    fp8_e4m3fn
#   out     : [num_tokens, num_groups, out_rank]     bfloat16 (written
#                                                    in-place; caller
#                                                    pre-allocates)
#
# Both `hidden_size` and `out_rank` must be divisible by 128 (kernel
# asserts). Scales are E8M0 packed uint8 by default, upcast to fp32
# inside the kernel; we pass already-fp32 scales here for portability.
#
# DSv4-Flash mid-decode shapes (TP=2):
#   num_groups = num_local_heads = 32 (64 total heads / 2 ranks)
#   hidden    = kv_lora_rank-style compressed dim, multiple of 128
#   out_rank  = wo_a projection out, multiple of 128


def _fp8_einsum_inputs(shape: str, device: str) -> dict[str, torch.Tensor]:
    if shape == "small":
        num_tokens, num_groups, hidden, out_rank = 8, 32, 512, 128
    elif shape == "medium":
        num_tokens, num_groups, hidden, out_rank = 128, 32, 512, 128
    else:
        raise ValueError(f"unknown shape `{shape}`")

    # Generate via bf16 intermediates, then quantise; port consumers can
    # round-trip back to bf16 for parity checks at atol≈5e-2.
    a_bf16 = (torch.randn(num_tokens, num_groups, hidden, device=device) * 0.3).to(
        torch.bfloat16
    )
    b_bf16 = (torch.randn(num_groups, out_rank, hidden, device=device) * 0.3).to(
        torch.bfloat16
    )
    a = a_bf16.to(torch.float8_e4m3fn)
    b = b_bf16.to(torch.float8_e4m3fn)

    # FP32 block scales — kernel will accept either fp32 directly or
    # E8M0 uint8 which it upcasts. We pass fp32 (simpler for the port
    # team to reproduce without an e8m0 helper).
    # Block layout: 128 along `hidden` for both a and b; for b also 128
    # along `out_rank`. Shape conventions checked at the runtime asserts
    # — see kernel for the exact scale-block layout assertion.
    scale_blocks_h = hidden // 128
    scale_blocks_o = out_rank // 128
    a_scale = torch.ones(num_tokens, num_groups, scale_blocks_h, dtype=torch.float32, device=device)
    b_scale = torch.ones(num_groups, scale_blocks_o, scale_blocks_h, dtype=torch.float32, device=device)
    out = torch.zeros(num_tokens, num_groups, out_rank, dtype=torch.bfloat16, device=device)
    return {
        "a": a,
        "a_scale": a_scale,
        "b": b,
        "b_scale": b_scale,
        "out": out,
    }


def _run_fp8_einsum(inputs: dict[str, torch.Tensor]) -> torch.Tensor:
    from vllm.v1.attention.ops.deepseek_v4_ops.fp8_einsum import (
        deepseek_v4_sm12x_fp8_einsum,
    )

    deepseek_v4_sm12x_fp8_einsum(
        inputs["a"],
        inputs["a_scale"],
        inputs["b"],
        inputs["b_scale"],
        inputs["out"],
    )
    return inputs["out"]


# ============================================================
# Kernel 3: dequantize_and_gather_k_cache (KV gather + dequant)
# ============================================================
#
# Signature: `(out, k_cache, seq_lens, gather_lens, block_table,
#              block_size, offset)`. Reads packed FP8 KV cache rows for
# each (req, position) pair, dequantises via embedded E8M0 scales, and
# writes bf16 values into `out`.
#
# DSv4-Flash KV cache layout per slot (head_bytes=584):
#   bytes [0:448]   : NoPE values (FP8 e4m3, 1 byte each)
#   bytes [448:512] : RoPE values (BF16, 2 bytes each = 32 floats)
#   bytes [512:519] : E8M0 block scales (7 bytes, one per 64-element
#                     NoPE block)
#   bytes [519:520] : padding
#   bytes [520:584] : reserved for FlashMLA 576B alignment + 8B header
#
# Output layout: `[chunk_size, max_gather_len, head_dim=512]` in bf16.
# `seq_lens[r]` is the number of slots to gather for request r;
# `block_table[r, ...]` indexes into k_cache.


def _gather_kv_inputs(shape: str, device: str) -> dict[str, torch.Tensor]:
    if shape == "small":
        chunk_size, max_gather_len, seq_len = 1, 1024, 1024
    elif shape == "medium":
        chunk_size, max_gather_len, seq_len = 4, 4096, 4096
    else:
        raise ValueError(f"unknown shape `{shape}`")

    block_size = 256
    head_dim = 512
    head_bytes = 584
    num_blocks = 64

    k_cache = torch.randint(
        0,
        255,
        (num_blocks, block_size, head_bytes),
        dtype=torch.uint8,
        device=device,
    )
    out = torch.zeros(
        chunk_size, max_gather_len, head_dim, dtype=torch.bfloat16, device=device
    )
    blocks_per_seq = (seq_len + block_size - 1) // block_size
    block_table = torch.randint(
        0, num_blocks, (chunk_size, blocks_per_seq), dtype=torch.int32, device=device
    )
    seq_lens = torch.full((chunk_size,), seq_len, dtype=torch.int32, device=device)
    return {
        "out": out,
        "k_cache": k_cache,
        "seq_lens": seq_lens,
        "block_table": block_table,
    }


def _run_gather_kv(inputs: dict[str, torch.Tensor]) -> torch.Tensor:
    from vllm.v1.attention.ops.deepseek_v4_ops.cache_utils import (
        dequantize_and_gather_k_cache,
    )

    dequantize_and_gather_k_cache(
        inputs["out"],
        inputs["k_cache"],
        seq_lens=inputs["seq_lens"],
        gather_lens=None,
        block_table=inputs["block_table"],
        block_size=256,
        offset=0,
    )
    return inputs["out"]


# ============================================================
# Kernel registry
# ============================================================


@dataclasses.dataclass
class KernelSpec:
    name: str
    build_inputs: Callable[[str, str], dict[str, torch.Tensor]]
    run: Callable[[dict[str, torch.Tensor]], torch.Tensor]
    shapes: tuple[str, ...]
    tolerance_hint: str
    metadata: dict[str, Any]


KERNELS: list[KernelSpec] = [
    KernelSpec(
        name="accumulate_indexed_sparse_mla_attention_chunk_multihead",
        build_inputs=_accumulate_inputs,
        run=_run_accumulate,
        shapes=("small", "medium"),
        tolerance_hint=(
            "atol=1e-3 rtol=1e-3 on `acc`; the kernel uses online softmax "
            "(max + denom + acc) so float32 accumulators can drift slightly "
            "vs the alternative implementation. Compare `max_score` exactly "
            "(no reduction noise), `denom` with atol=1e-3, `acc` with atol=1e-3."
        ),
        metadata={
            "scale": 0.125,
            "head_block": 8,
            "candidate_offset": 0,
            "notes": (
                "Multi-head sparse MLA accumulate from PR #6 with the "
                "gather-overlap commit's signature (single-head call site "
                "internally dispatches to HEAD_BLOCK=8 multi-head kernel)."
            ),
        },
    ),
    KernelSpec(
        name="deepseek_v4_sm12x_fp8_einsum",
        build_inputs=_fp8_einsum_inputs,
        run=_run_fp8_einsum,
        shapes=("small", "medium"),
        tolerance_hint=(
            "atol=5e-2 rtol=5e-2 on the bf16 output. FP8 e4m3 input × fp32 "
            "block scales accumulates rounding error proportional to "
            "hidden_size; with hidden=512 and uniform fp32 scales of 1.0 the "
            "result is just `a.to(fp32) @ b.to(fp32).transpose(-1, -2)` "
            "tile-wise. Compare via einsum reference: "
            "`torch.einsum('bhr,hdr->bhd', a.to(f32)*a_scale_per_block, "
            "b.to(f32)*b_scale_per_block)` with the same 128-block-along-hidden "
            "tiling."
        ),
        metadata={
            "einsum": "bhr,hdr->bhd",
            "block_hidden": 128,
            "block_out": 128,
            "block_tokens": 16,
            "scale_dtype_accepted": "fp32 or e8m0 (uint8, upcast inside kernel)",
            "notes": (
                "FP8 W8A8 mHC compute in mid-decode head projection. Shape "
                "uses TP=2 DSv4-Flash dims (num_groups=32). Both `hidden` "
                "and `out_rank` must be divisible by 128."
            ),
        },
    ),
    KernelSpec(
        name="dequantize_and_gather_k_cache",
        build_inputs=_gather_kv_inputs,
        run=_run_gather_kv,
        shapes=("small", "medium"),
        tolerance_hint=(
            "atol=0 rtol=0 on `out` bytes. Packed FP8 cache read with "
            "embedded E8M0 dequant — output is fully determined by the "
            "input k_cache bytes + block_table + seq_lens. Any divergence "
            "is a layout bug (wrong block_size, wrong head_bytes stride, "
            "wrong scale-byte offsets, or wrong FlashMLA alignment)."
        ),
        metadata={
            "block_size": 256,
            "head_dim": 512,
            "head_bytes": 584,
            "fp8_layout_notes": (
                "NoPE: bytes [0:448] fp8_e4m3. RoPE: bytes [448:512] bf16. "
                "E8M0 block scales: bytes [512:519] (7 bytes, one per 64 "
                "NoPE elements). Byte 519 is pad. Bytes 520-583 reserved "
                "for FlashMLA 576B alignment + 8B header."
            ),
            "notes": (
                "Read by gather-overlap on aux_stream[1] in attention_impl "
                "and by _forward_prefill fallback. Same kernel for "
                "compressed (C128A) and SWA caches."
            ),
        },
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Dump (input, output) reference tensors for top SM12x DSv4 "
            "kernels so SGLang / TokenSpeed ports can verify kernel parity."
        )
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gpu-id", type=int, default=0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--kernel",
        action="append",
        help="If given, only dump these kernels by name (may be repeated).",
    )
    args = parser.parse_args()

    if not torch.cuda.is_available():
        print("error: CUDA not available", file=sys.stderr)
        return 2

    device = f"cuda:{args.gpu_id}"
    torch.cuda.set_device(args.gpu_id)
    _seed_all(args.seed)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    selected = {k.lower() for k in (args.kernel or [])}

    manifest: dict[str, Any] = {
        "seed": args.seed,
        "device_name": torch.cuda.get_device_name(args.gpu_id),
        "compute_cap": "{}.{}".format(*torch.cuda.get_device_capability(args.gpu_id)),
        "torch_version": torch.__version__,
        "kernels": [],
    }

    for spec in KERNELS:
        if selected and spec.name.lower() not in selected:
            continue
        print(f"=== {spec.name} ===")
        for shape in spec.shapes:
            print(f"  shape `{shape}` ...", end=" ", flush=True)
            try:
                inputs = spec.build_inputs(shape, device)
                output = spec.run(inputs)
                torch.cuda.synchronize()
            except Exception as exc:  # noqa: BLE001
                print(f"FAIL ({type(exc).__name__}: {exc})")
                manifest["kernels"].append(
                    {
                        "kernel": spec.name,
                        "shape_name": shape,
                        "status": "fail",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
                continue
            dump = KernelDump(
                name=spec.name,
                shape_name=shape,
                inputs=inputs,
                output=output,
                metadata=spec.metadata,
                tolerance_hint=spec.tolerance_hint,
            )
            entry = dump.save(args.output_dir)
            entry["status"] = "ok"
            manifest["kernels"].append(entry)
            print(f"OK ({entry['output']['sha256'][:16]}...)")

    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nwrote {manifest_path}")
    print(
        f"dumped {sum(1 for k in manifest['kernels'] if k.get('status') == 'ok')} "
        f"(kernel, shape) entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
