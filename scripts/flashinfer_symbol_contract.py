#!/usr/bin/env python3
"""Assert every FlashInfer symbol our DSv4 SM12x path depends on.

Why this is not redundant with "the serve came up": every availability probe in
vllm/utils/flashinfer.py is shaped

    try:
        from flashinfer.X import Y
    except ImportError:
        return False

so a renamed or moved symbol does not raise -- it silently returns False and the
model falls back to the FlashMLA/Triton path. Serve still starts, GSM8K still
passes, and the only symptom is that the SM120 kernels we spent the branch
enabling are no longer used. Check the contract explicitly instead.

Usage: fi_symbol_contract.py            # probe the current interpreter's flashinfer
"""
from __future__ import annotations

import importlib
import sys

# (module, attribute, why this branch needs it)
CONTRACT: list[tuple[str, str, str]] = [
    (
        "flashinfer.mla",
        "trtllm_batch_decode_sparse_mla_dsv4",
        "has_flashinfer_trtllm_sparse_mla_dsv4 -- gates the SM120 decode class in "
        "_select_dsv4_attn_cls; False silently routes DSv4 to FlashMLA",
    ),
    (
        "flashinfer.decode",
        "trtllm_batch_decode_sparse_mla_dsv4",
        "has_flashinfer_sparse_mla_sm120",
    ),
    (
        "flashinfer.decode",
        "trtllm_batch_decode_with_kv_cache_mla",
        "has_flashinfer_sparse_mla_sm120",
    ),
    ("flashinfer.autotuner", "autotune", "has_flashinfer_sparse_mla_sm120"),
    (
        "flashinfer.mla._sparse_mla_sm120",
        "_SparseMLAPagedAttentionRunner",
        "flashinfer_sm120_decode.py:142 -- imported directly, not probed, so a "
        "rename here is an ImportError at decode time rather than a fallback",
    ),
    ("flashinfer.concat_ops", "concat_mla_k", "vllm/utils/flashinfer.py:585"),
    ("flashinfer", "mm_fp4", "NVFP4 GEMM path"),
    ("flashinfer", "mxfp4_quantize", "MXFP4 MoE path"),
    ("flashinfer", "nvfp4_quantize", "NVFP4 quantize path"),
    ("flashinfer", "SfLayout", "NVFP4 scale-factor layout enum"),
    ("flashinfer", "bmm_fp8", "FP8 batched GEMM"),
    ("flashinfer", "mm_mxfp8", "MXFP8 GEMM"),
]


def main() -> int:
    try:
        import flashinfer  # noqa: F401
        import importlib.metadata as md

        print(f"flashinfer-python {md.version('flashinfer-python')}")
        try:
            print(f"flashinfer-cubin  {md.version('flashinfer-cubin')}")
        except Exception:
            print("flashinfer-cubin  NOT INSTALLED")
    except Exception as exc:  # noqa: BLE001
        print(f"FATAL: cannot import flashinfer: {type(exc).__name__}: {exc}")
        return 2

    missing: list[tuple[str, str, str]] = []
    for mod_name, attr, why in CONTRACT:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:  # noqa: BLE001
            print(f"  MISSING  {mod_name}.{attr}  (module: {type(exc).__name__})")
            missing.append((mod_name, attr, why))
            continue
        obj = getattr(mod, attr, None)
        if obj is None:
            print(f"  MISSING  {mod_name}.{attr}")
            missing.append((mod_name, attr, why))
        else:
            kind = "callable" if callable(obj) else type(obj).__name__
            print(f"  ok       {mod_name}.{attr}  ({kind})")

    if missing:
        print(f"\n{len(missing)} symbol(s) missing -- DO NOT UPGRADE without handling:")
        for mod_name, attr, why in missing:
            print(f"  {mod_name}.{attr}\n      needed by: {why}")
        return 1

    print(f"\nall {len(CONTRACT)} symbols present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
