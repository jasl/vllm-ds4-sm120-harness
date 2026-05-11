#!/usr/bin/env python3
"""
SM12x DeepSeek V4 Flash dense FP8 block GEMM autotuning driver.

Wraps vLLM's `benchmarks/kernels/benchmark_w8a8_block_fp8.py` to tune the six
(N, K) shapes that DSv4-Flash dense linear layers hit at TP=2 on SM12x
(RTX PRO 6000 Blackwell / GB10). Reuses vLLM's `benchmark_config()` and
`save_configs()` without modifying the upstream script, but reimplements the
inner `tune()` loop so we can:

  * filter the search space per-M — at large M, configs with
    `BLOCK_SIZE_M << M` are catastrophic (the kernel iterates
    `cdiv(M, BLOCK_SIZE_M)` times along the M dimension); a single
    BLOCK_M=16 / M=512 config can take seconds, hanging the tuner.
  * cap the per-(M, N, K) tuning wall clock (`--abort-seconds`) so a single
    slow shape can't stall the run.
  * use shorter `num_iters` for large M (kernel run-time dominates timing
    noise; default 10 iters wastes budget).

Shape source: `tests/quantization/test_sm12x_tuned_config_lookup.py` —
the assertions there are what we ship as ground truth. Same shapes apply to
both SM120 (RTX PRO 6000) and SM121 (GB10).

Usage:
  python3 scripts/_fp8_block_tune_driver.py \
      --vllm-repo /path/to/vllm \
      --out-dir /path/to/tuning_out \
      --batch-sizes 1,2,4,8,16,32,64,128,256,512 \
      [--shapes "1536,4096:16384,1024:..." ]
      [--gpu-id 0]
      [--num-iters 10] [--abort-seconds 600]
      [--dry-run]

Output:
  JSON files named exactly as vLLM expects, e.g.
    N=1536,K=4096,device_name=<auto>,dtype=fp8_w8a8,block_shape=[128,128].json
  Auto-detected `device_name` comes from `vllm.platforms.current_platform`.

After tuning:
  1. Copy each JSON into `vllm/model_executor/layers/quantization/utils/configs/`
  2. Restart vLLM serve
  3. Re-run `scripts/run_decode_profile.sh` to compare top-kernel times
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

# Default batch sizes to tune. Covers decode hot range (1..32), short-prefill
# transition (64..128), and long-prefill anchors (256, 512). At M >= 256 the
# placeholder configs (BLOCK_SIZE_M=16) collapse — these are exactly the
# shapes we most need real configs for.
DEFAULT_BATCH_SIZES: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)


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


def filter_search_space_for_M(search_space: list[dict], M: int) -> list[dict]:
    """Filter out configs that would be catastrophically slow for this M.

    Rule of thumb: when BLOCK_SIZE_M << M, the kernel runs cdiv(M, BLOCK_M)
    iterations along M. With many iterations and small M-tiles, each
    iteration is short and SM occupancy is low → very slow. A single bad
    config at M=512 with BLOCK_M=16 can take seconds (32 M-iterations,
    cold cache each), which stalls the tuner.

    Heuristic: require BLOCK_SIZE_M >= M / 8 (cap at 64) so we never have
    more than 8 M-iterations. For M < 64 we keep the full space because
    BLOCK_M=16 is the right answer for decode shapes.
    """
    if M < 64:
        return search_space
    min_block_m = min(64, max(16, M // 8))
    return [c for c in search_space if c["BLOCK_SIZE_M"] >= min_block_m]


def auto_num_iters(M: int, default: int) -> int:
    """Reduce num_iters for large M where kernel runtime dominates noise."""
    if M >= 256:
        return max(3, min(default, 5))
    if M >= 64:
        return max(5, min(default, 7))
    return default


def _tune_one(
    bench,
    torch,
    triton,
    M: int,
    N: int,
    K: int,
    block_size: list[int],
    out_dtype,
    search_space: list[dict],
    num_iters: int,
    abort_seconds: float,
):
    """Mirror of vLLM's tune() with custom num_iters + abort timeout.

    Returns (best_config, best_time_us, configs_tried, aborted).
    """
    from tqdm import tqdm

    factor_for_scale = 1e-2
    fp8_info = torch.finfo(torch.float8_e4m3fn)
    fp8_max, fp8_min = fp8_info.max, fp8_info.min
    A_fp32 = (
        (torch.rand(M, K, dtype=torch.float32, device="cuda") - 0.5)
        * 2
        * fp8_max
    )
    A = A_fp32.clamp(min=fp8_min, max=fp8_max).to(torch.float8_e4m3fn)
    B_fp32 = (
        (torch.rand(N, K, dtype=torch.float32, device="cuda") - 0.5)
        * 2
        * fp8_max
    )
    B = B_fp32.clamp(min=fp8_min, max=fp8_max).to(torch.float8_e4m3fn)

    block_n, block_k = block_size[0], block_size[1]
    n_tiles = (N + block_n - 1) // block_n
    k_tiles = (K + block_k - 1) // block_k
    As = (
        torch.rand(M, k_tiles, dtype=torch.float32, device="cuda")
        * factor_for_scale
    )
    Bs = (
        torch.rand(n_tiles, k_tiles, dtype=torch.float32, device="cuda")
        * factor_for_scale
    )

    best_config = None
    best_time = float("inf")
    tried = 0
    aborted = False
    t0 = time.time()
    for cfg in tqdm(search_space, desc=f"M={M}", leave=False):
        if abort_seconds and (time.time() - t0) > abort_seconds:
            aborted = True
            break
        try:
            kt = bench.benchmark_config(
                A, B, As, Bs, block_size, cfg, out_dtype, num_iters=num_iters
            )
        except triton.runtime.autotuner.OutOfResources:
            continue
        except Exception as e:
            # Some configs can crash on certain GPUs (e.g., LDS overflow on
            # ROCm, register pressure on small SMs). Skip and continue.
            print(f"   [WARN] M={M} cfg={cfg}: {type(e).__name__}: {e}")
            continue
        tried += 1
        if kt < best_time:
            best_time = kt
            best_config = cfg
    return best_config, best_time, tried, aborted


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
        help=(
            f"Comma-separated batch sizes "
            f"(default: {','.join(str(b) for b in DEFAULT_BATCH_SIZES)})."
        ),
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
        "--num-iters",
        type=int,
        default=10,
        help="Timing iterations per config (default 10). Auto-reduced for "
        "large M (M>=256 → 5, M>=64 → 7) unless --no-auto-iters.",
    )
    parser.add_argument(
        "--no-auto-iters",
        action="store_true",
        help="Disable M-aware num_iters reduction; always use --num-iters.",
    )
    parser.add_argument(
        "--abort-seconds",
        type=float,
        default=600.0,
        help="Per-(M, N, K) tuning wall-clock cap in seconds (default 600). "
        "Set 0 to disable.",
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
    print(
        f"[driver] num_iters={args.num_iters} "
        f"auto_iters_by_M={'off' if args.no_auto_iters else 'on'}"
    )
    print(f"[driver] abort_seconds={args.abort_seconds}")

    if args.dry_run:
        n_tune = len(shapes) * len(batch_sizes)
        # Rough estimate: small-M tunings ~20s each, M=256 ~30-60s, M=512
        # ~60-180s (with filter). JIT amortises across same-shape, different-M.
        est_sec = 0.0
        for M in batch_sizes:
            base = 20 if M < 64 else (30 if M < 256 else (90 if M < 512 else 150))
            est_sec += base * len(shapes)
        print(
            f"[driver] dry-run: would tune {n_tune} (M, N, K) combos; "
            f"est {est_sec/60:.1f} min (highly variable based on JIT cache)."
        )
        # Show per-M filtered search-space sizes (without invoking GPU).
        # Use a faked search space matching get_configs_compute_bound shape.
        # Total = 4*5*2*4*2*4 = 1280
        proto = [
            {
                "BLOCK_SIZE_M": m,
                "BLOCK_SIZE_N": n,
                "BLOCK_SIZE_K": k,
                "GROUP_SIZE_M": g,
                "num_warps": w,
                "num_stages": s,
            }
            for s in [2, 3, 4, 5]
            for m in [16, 32, 64, 128, 256]
            for k in [64, 128]
            for n in [32, 64, 128, 256]
            for w in [4, 8]
            for g in [1, 16, 32, 64]
            if args.block_k % k == 0
        ]
        print(f"[driver] base search space size: {len(proto)} configs")
        for M in batch_sizes:
            filt = filter_search_space_for_M(proto, M)
            iters = (
                args.num_iters
                if args.no_auto_iters
                else auto_num_iters(M, args.num_iters)
            )
            print(
                f"[driver]   M={M:>4}: filtered={len(filt):>4} configs, "
                f"num_iters={iters}"
            )
        return 0

    bench = _import_vllm_benchmark(args.vllm_repo)
    import torch  # noqa: E402  (imported after sys ready)
    from vllm.platforms import current_platform  # noqa: E402
    from vllm.triton_utils import triton  # noqa: E402

    torch.accelerator.set_device_index(args.gpu_id)
    device_name = current_platform.get_device_name().replace(" ", "_")
    print(f"[driver] device_name={device_name}")

    base_search_space = bench.get_configs_compute_bound()
    base_search_space = [
        cfg for cfg in base_search_space if args.block_k % cfg["BLOCK_SIZE_K"] == 0
    ]
    print(f"[driver] base search_space size: {len(base_search_space)} configs")

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
            space = filter_search_space_for_M(base_search_space, M)
            iters = (
                args.num_iters
                if args.no_auto_iters
                else auto_num_iters(M, args.num_iters)
            )
            tic = time.time()
            cfg, best_us, tried, aborted = _tune_one(
                bench,
                torch,
                triton,
                M,
                N,
                K,
                [args.block_n, args.block_k],
                out_dtype,
                space,
                iters,
                args.abort_seconds,
            )
            elapsed = time.time() - tic
            if cfg is None:
                print(
                    f"[driver]   M={M:>4}: !! NO VALID CONFIG !! "
                    f"tried={tried}/{len(space)} aborted={aborted} "
                    f"({elapsed:.1f}s)"
                )
                # Fall back to a sane default so we still write a JSON entry.
                cfg = {
                    "BLOCK_SIZE_M": 16 if M < 64 else 64,
                    "BLOCK_SIZE_N": args.block_n,
                    "BLOCK_SIZE_K": args.block_k,
                    "GROUP_SIZE_M": 32,
                    "num_warps": 4,
                    "num_stages": 3,
                }
            else:
                ab = " [ABORTED]" if aborted else ""
                print(
                    f"[driver]   M={M:>4}: best={cfg} "
                    f"t={best_us:.1f}us tried={tried}/{len(space)} "
                    f"iters={iters} ({elapsed:.1f}s){ab}"
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
