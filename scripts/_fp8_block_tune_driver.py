#!/usr/bin/env python3
"""
SM12x DeepSeek V4 Flash dense FP8 block GEMM autotuning driver.

Wraps vLLM's `benchmarks/kernels/benchmark_w8a8_block_fp8.py` to tune the six
(N, K) shapes that DSv4-Flash dense linear layers hit at TP=2 on SM12x
(RTX PRO 6000 Blackwell / GB10). Reuses vLLM's `tune()` and `save_configs()`
without modifying the upstream script.

Shape source: `tests/quantization/test_sm12x_tuned_config_lookup.py` —
the assertions there are what we ship as ground truth.

Usage:
  python3 scripts/_fp8_block_tune_driver.py \
      --vllm-repo /path/to/vllm \
      --out-dir /path/to/tuning_out \
      --batch-sizes 1,2,4,8,16,32,64,128 \
      [--shapes "1536,4096:16384,1024:..." ]
      [--gpu-id 0]
      [--dry-run]

Output:
  JSON files named exactly as vLLM expects, e.g.
    N=1536,K=4096,device_name=<auto>,dtype=fp8_w8a8,block_shape=[128,128].json
  Auto-detected `device_name` comes from `vllm.platforms.current_platform`.

After tuning:
  1. Copy each JSON into `vllm/model_executor/layers/quantization/utils/configs/`
  2. Restart vLLM serve
  3. Re-run `scripts/run_decode_profile.sh` to compare top-kernel times

Estimated runtime: ~5 min per (N, K) × num_batch_sizes on RTX PRO 6000.
For 6 shapes × 8 batch_sizes = ~4 hours single-GPU; ~2 hours two-GPU split.
"""

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

# DSv4-Flash dense FP8 GEMM (N, K) shapes for SM12x TP=2.
# Block shape is always (128, 128) for these layers.
SM12X_DSV4_DENSE_FP8_SHAPES: tuple[tuple[int, int], ...] = (
    (1536, 4096),
    (2048, 4096),
    (4096, 1024),
    (4096, 4096),
    (8192, 1024),
    (16384, 1024),
)

# Default batch sizes to tune. Decode hot range is small (1..64); we add a
# few prefill-side anchors so the configs don't degrade for chunked prefill.
DEFAULT_BATCH_SIZES: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128)


def _import_vllm_benchmark(vllm_repo: Path):
    """Import benchmark_w8a8_block_fp8 as a module without altering sys.path."""
    bench_path = (
        vllm_repo / "benchmarks" / "kernels" / "benchmark_w8a8_block_fp8.py"
    )
    if not bench_path.is_file():
        raise FileNotFoundError(
            f"vLLM benchmark script not found at {bench_path}. "
            "Pass --vllm-repo pointing at a vllm checkout."
        )
    spec = importlib.util.spec_from_file_location(
        "vllm_benchmark_w8a8_block_fp8", bench_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _parse_shapes(spec: str | None) -> tuple[tuple[int, int], ...]:
    if not spec:
        return SM12X_DSV4_DENSE_FP8_SHAPES
    shapes: list[tuple[int, int]] = []
    for chunk in spec.split(":"):
        chunk = chunk.strip()
        if not chunk:
            continue
        n_str, k_str = chunk.split(",")
        shapes.append((int(n_str), int(k_str)))
    return tuple(shapes)


def _parse_batch_sizes(spec: str) -> list[int]:
    return [int(v) for v in spec.split(",") if v.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vllm-repo",
        type=Path,
        default=Path(os.environ.get("VLLM_REPO", "/home/jasl/Workspace/vllm")),
        help="Path to vllm git checkout (default: $VLLM_REPO or "
        "/home/jasl/Workspace/vllm).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory where tuned JSON configs are written.",
    )
    parser.add_argument(
        "--batch-sizes",
        type=str,
        default=",".join(str(b) for b in DEFAULT_BATCH_SIZES),
        help=f"Comma-separated batch sizes (default: {','.join(str(b) for b in DEFAULT_BATCH_SIZES)}).",
    )
    parser.add_argument(
        "--shapes",
        type=str,
        default=None,
        help="Override shape list. Format: 'N,K:N,K:...'.  Default: 6 SM12x DSv4 shapes.",
    )
    parser.add_argument(
        "--block-n", type=int, default=128, help="FP8 block N (default 128)."
    )
    parser.add_argument(
        "--block-k", type=int, default=128, help="FP8 block K (default 128)."
    )
    parser.add_argument(
        "--out-dtype",
        type=str,
        choices=["float16", "bfloat16"],
        default="bfloat16",
        help="GEMM output dtype (DSv4 runs bf16; default bfloat16).",
    )
    parser.add_argument(
        "--gpu-id",
        type=int,
        default=0,
        help="CUDA device index for this driver (default 0).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the tuning plan and exit without launching kernels.",
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    batch_sizes = _parse_batch_sizes(args.batch_sizes)
    shapes = _parse_shapes(args.shapes)

    print(f"[driver] vllm_repo={args.vllm_repo}")
    print(f"[driver] out_dir={args.out_dir}")
    print(f"[driver] gpu_id={args.gpu_id}")
    print(f"[driver] batch_sizes={batch_sizes}")
    print(f"[driver] shapes (N,K): {shapes}")
    print(f"[driver] block_shape=[{args.block_n}, {args.block_k}]")
    print(f"[driver] out_dtype={args.out_dtype}")

    if args.dry_run:
        n_tune = len(shapes) * len(batch_sizes)
        # ~5-10s per (M,N,K) in practice; first invocation slower due to JIT.
        est_min = n_tune * 7.0 / 60.0
        print(
            f"[driver] dry-run: would tune {n_tune} (M, N, K) combos; "
            f"est {est_min:.1f} min."
        )
        return 0

    bench = _import_vllm_benchmark(args.vllm_repo)
    import torch  # noqa: E402  (imported after sys ready)
    from vllm.platforms import current_platform  # noqa: E402

    torch.accelerator.set_device_index(args.gpu_id)
    device_name = current_platform.get_device_name().replace(" ", "_")
    print(f"[driver] device_name={device_name}")

    search_space = bench.get_configs_compute_bound()
    search_space = [
        cfg for cfg in search_space if args.block_k % cfg["BLOCK_SIZE_K"] == 0
    ]
    print(f"[driver] search_space size: {len(search_space)} configs")

    out_dtype = {"float16": torch.float16, "bfloat16": torch.bfloat16}[
        args.out_dtype
    ]

    overall_start = time.time()
    summary: dict[str, dict[int, dict]] = {}
    for shape_idx, (N, K) in enumerate(shapes, 1):
        shape_start = time.time()
        print(
            f"\n[driver] === Shape {shape_idx}/{len(shapes)}: N={N}, K={K} ==="
        )
        best_configs: dict[int, dict] = {}
        for M in batch_sizes:
            tic = time.time()
            cfg = bench.tune(
                M,
                N,
                K,
                [args.block_n, args.block_k],
                out_dtype,
                search_space,
                "fp8",
            )
            elapsed = time.time() - tic
            print(
                f"[driver]   M={M:>4}: best={cfg}  ({elapsed:.1f}s)"
            )
            best_configs[M] = cfg
        bench.save_configs(
            N,
            K,
            args.block_n,
            args.block_k,
            best_configs,
            str(args.out_dir),
            "fp8",
        )
        summary[f"N={N},K={K}"] = best_configs
        print(
            f"[driver] shape N={N},K={K} took {time.time() - shape_start:.1f}s"
        )

    overall_elapsed = time.time() - overall_start
    print(f"\n[driver] total runtime: {overall_elapsed/60:.1f} min")
    summary_path = args.out_dir / "tuning_summary.json"
    with open(summary_path, "w") as f:
        json.dump(
            {
                "device_name": device_name,
                "block_shape": [args.block_n, args.block_k],
                "batch_sizes": batch_sizes,
                "shapes": [list(s) for s in shapes],
                "configs": summary,
                "wall_seconds": overall_elapsed,
            },
            f,
            indent=2,
        )
    print(f"[driver] summary → {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
