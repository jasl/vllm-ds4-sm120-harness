#!/usr/bin/env python3
"""
SM12x DeepSeek V4 Flash fused-MoE FP8 W8A8 autotuning driver.

Wraps vLLM's `benchmarks/kernels/benchmark_moe.py` (`benchmark_config`,
`save_configs`, `get_configs_compute_bound`) to tune the per-rank MoE Triton
kernel for shapes that arise from DSv4-Flash and adjacent MoE models, without
going through the upstream `--model` code path (which doesn't know
`DeepseekV4ForCausalLM` — it's not in `get_model_params`).

Driving in-process lets us:
  * pass `(num_experts, shard_intermediate_size, hidden_size, topk)` explicitly
    so any (E, N) shape from any sharding (TP/EP) can be tuned, even if no HF
    model produces it through `get_model_params`;
  * mirror the dense FP8 driver's per-M search-space filter + abort timer so a
    single bad config can't stall the run;
  * run sequentially on a single GPU (no Ray) — same pattern as the dense
    block-FP8 driver and consistent with our 2x RTX PRO 6000 / 1x GB10 hosts.

vLLM's MoE config filename convention is
  `E=<num_experts>,N=<shard_intermediate_size//2>,device_name=<auto>,dtype=fp8_w8a8,block_shape=[Bn,Bk].json`
which `save_configs(...)` produces. The `device_name` is whatever
`vllm.platforms.current_platform.get_device_name()` returns at tune time, so
the file is auto-tagged to the host you're running on.

Default shape set: DSv4-Flash at TP=2+EP (production), TP=4+EP, TP=8+EP, and
TP=2 no-EP. Reason for these picks:

  * **PRIORITY 1 — `E=128, N=2048`** is what `--tensor-parallel-size 2
    --enable-expert-parallel` resolves to on DSv4-Flash and is **not currently
    covered by any tuned config in the tree**. We've been falling back to
    Triton's default heuristic for the kernel that dominates MoE in our
    production serve. This is the most important shape to land.
  * `E=64, N=2048` (TP=4+EP) and `E=32, N=2048` (TP=8+EP) give us coverage if
    we change topology later — same shard_intermediate_size, fewer experts
    per rank.
  * `E=256, N=1024` (TP=2 no-EP) covers the alternative deployment we'd hit
    if `--enable-expert-parallel` is dropped.

The existing `E=256, N=512` we shipped earlier was for TP=4 no-EP and is
**not on our production hot path** — it's still useful for users who run that
topology, but doesn't reflect our deploy.

Usage:
  python3 scripts/_fp8_moe_tune_driver.py \\
      --vllm-repo /path/to/vllm \\
      --out-dir /path/to/moe_tuning_out \\
      [--shapes "E,shard_int_size,hidden,topk:E,shard,hidden,topk:..."] \\
      [--batch-sizes 1,2,4,8,16,32,64,128,256,512] \\
      [--block-n 128 --block-k 128] \\
      [--gpu-id 0] \\
      [--num-iters 20] [--abort-seconds 1200] \\
      [--dry-run]

Output:
  JSON files named exactly as vLLM expects, e.g.
    E=128,N=2048,device_name=NVIDIA_RTX_PRO_6000_Blackwell_Workstation_Edition,dtype=fp8_w8a8,block_shape=[128,128].json
  plus `tuning_summary.json` with the per-(label, M) best configs.

After tuning:
  1. Inspect `${OUT_DIR}/tuning_summary.json` and the per-shape JSONs.
  2. Copy each JSON into `vllm/model_executor/layers/fused_moe/configs/`.
  3. (Optional) Add device-name aliases for Server / Max-Q / GB10 if you want
     the file to be found on those devices too — same pattern as the Blackwell
     alias commits.
  4. Restart vLLM serve and re-run a small bench (mt-bench c=1 / c=24) to
     confirm the new configs are picked up and improve TPOT.
"""

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path


# (label, num_experts_per_rank, shard_intermediate_size, hidden_size, topk, block_shape)
#
# `shard_intermediate_size` is what `benchmark_moe.py` expects: it's
# `2 * moe_intermediate_size` (or that divided by tp_size if EP is off). The
# JSON filename derives N as `shard_intermediate_size // 2`, so the on-disk
# shape is `E=<num_experts_per_rank>, N=<shard_intermediate_size // 2>`.
#
# DSv4-Flash constants (from `~/.cache/.../DeepSeek-V4-Flash/.../config.json`):
#   moe_intermediate_size = 2048
#   n_routed_experts = 256
#   num_experts_per_tok = 6
#   hidden_size = 4096
#
# Topology → per-rank shape derivation:
#   TP=N + EP=on:  E_per_rank = 256/N, shard_int_size = 2*2048
#   TP=N + EP=off: E_per_rank = 256,   shard_int_size = 2*2048/N
#
# `benchmark_moe.py` only runs the per-rank kernel on a single GPU — TP=N is
# a label, not a distributed run — so any per-rank shape can be tuned on a
# 1- or 2-GPU host regardless of the deploy topology it's labelled with.
#
# All 4 shapes are tuned by default because they cover the typical Blackwell
# SM12x deployment matrix:
#
#   * 2-card RTX PRO 6000 Workstation (our box)        → TP=2
#   * 4-card RTX PRO 6000 Server / Max-Q box           → TP=4
#   * 8-card RTX PRO 6000 Server / Max-Q box           → TP=8
#   * 2-node GB10 cluster (1 GPU per node)             → TP=2
#   * 4-node GB10 cluster                              → TP=4
#
# With `--enable-expert-parallel` (the recommended DSv4 deploy), the shape
# uses the EP rows; without EP it uses the no-EP row (#4 covers TP=2 no-EP).
# TP=4 no-EP is already covered by an existing tuned file in the tree
# (E=256, N=512) — no need to re-tune.
SM12X_DSV4_MOE_SHAPES: tuple[tuple[str, int, int, int, int, list[int]], ...] = (
    ("DSv4_TP2_EP",   128, 4096, 4096, 6, [128, 128]),  # E=128, N=2048 — our prod + GB10 2-node EP
    ("DSv4_TP4_EP",    64, 4096, 4096, 6, [128, 128]),  # E=64,  N=2048 — 4-card / GB10 4-node EP
    ("DSv4_TP8_EP",    32, 4096, 4096, 6, [128, 128]),  # E=32,  N=2048 — 8-card / 8-node EP
    ("DSv4_TP2_noEP", 256, 2048, 4096, 6, [128, 128]),  # E=256, N=1024 — TP=2 EP-off fallback
)

# Default batch sizes. Decode hot range (1..32), short-prefill transition
# (64..128), and long-prefill anchors (256, 512). Same set as the dense driver.
DEFAULT_BATCH_SIZES: tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)


def _install_ray_stub() -> None:
    """Stub `ray` so importing benchmark_moe.py succeeds without ray installed.

    benchmark_moe.py imports ray at module level and decorates `BenchmarkWorker`
    with `@ray.remote(num_gpus=1)`. We never instantiate that class (we only
    use the module-level free functions `benchmark_config`, `save_configs`,
    `sort_config`, `get_configs_compute_bound`, plus the `clear_triton_cache`
    helper). A minimal stub turns the decorator into a no-op and provides
    `ray.init()` / `ray.available_resources()` / `ray.get()` / `ray.get_gpu_ids()`
    so the rest of the module imports cleanly. The actual `main()` entry point
    that calls ray would error if invoked, but we never call it.
    """
    import types

    if "ray" in sys.modules:
        return
    ray_stub = types.ModuleType("ray")

    def _remote(*decorator_args, **decorator_kwargs):
        # Support both `@ray.remote` (bare) and `@ray.remote(num_gpus=1)`.
        if (
            len(decorator_args) == 1
            and not decorator_kwargs
            and (callable(decorator_args[0]) or isinstance(decorator_args[0], type))
        ):
            return decorator_args[0]

        def _wrap(cls_or_fn):
            return cls_or_fn

        return _wrap

    ray_stub.remote = _remote
    ray_stub.init = lambda *a, **k: None
    ray_stub.available_resources = lambda: {"GPU": 1}
    ray_stub.get = lambda x: x
    ray_stub.get_gpu_ids = lambda: [0]
    sys.modules["ray"] = ray_stub

    # `from ray.experimental.tqdm_ray import tqdm` — provide the submodule and
    # fall through to the real tqdm so the progress bars still work.
    ray_experimental = types.ModuleType("ray.experimental")
    tqdm_ray_stub = types.ModuleType("ray.experimental.tqdm_ray")
    from tqdm import tqdm as _real_tqdm

    tqdm_ray_stub.tqdm = _real_tqdm
    ray_experimental.tqdm_ray = tqdm_ray_stub
    sys.modules["ray.experimental"] = ray_experimental
    sys.modules["ray.experimental.tqdm_ray"] = tqdm_ray_stub


def _import_vllm_benchmark(vllm_repo: Path):
    """Import benchmark_moe as a module without altering sys.path."""
    _install_ray_stub()
    bench_path = vllm_repo / "benchmarks" / "kernels" / "benchmark_moe.py"
    if not bench_path.is_file():
        raise FileNotFoundError(
            f"vLLM benchmark script not found at {bench_path}. "
            "Pass --vllm-repo pointing at a vllm checkout."
        )
    spec = importlib.util.spec_from_file_location(
        "vllm_benchmark_moe", bench_path
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _parse_shapes(
    spec: str | None,
) -> tuple[tuple[str, int, int, int, int, list[int]], ...]:
    if not spec:
        return SM12X_DSV4_MOE_SHAPES
    shapes: list[tuple[str, int, int, int, int, list[int]]] = []
    for idx, chunk in enumerate(spec.split(":")):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = [p.strip() for p in chunk.split(",")]
        if len(parts) != 4:
            raise ValueError(
                f"shape #{idx + 1} must be E,shard_int_size,hidden,topk (got {chunk!r})"
            )
        e, shard, hidden, topk = (int(x) for x in parts)
        shapes.append((f"custom_{idx + 1}", e, shard, hidden, topk, [128, 128]))
    return tuple(shapes)


def _parse_batch_sizes(spec: str) -> list[int]:
    return [int(v) for v in spec.split(",") if v.strip()]


def filter_search_space_for_M(search_space: list[dict], M: int) -> list[dict]:
    """Filter out configs that would be catastrophically slow for this M.

    Same heuristic as the dense FP8 driver: when `BLOCK_SIZE_M << M`, the
    kernel iterates `cdiv(M, BLOCK_SIZE_M)` times. At M=512 with BLOCK_M=16
    that's 32 iterations of a small tile — slow enough to dominate the tune
    budget for that one config.

    Require BLOCK_SIZE_M >= M / 8 (cap at 64) for M >= 64. For M < 64 keep
    the full space because BLOCK_M=16 is the right answer for decode.
    """
    if M < 64:
        return search_space
    min_block_m = min(64, max(16, M // 8))
    return [c for c in search_space if c["BLOCK_SIZE_M"] >= min_block_m]


def auto_num_iters(M: int, default: int) -> int:
    """Reduce num_iters for large M where kernel runtime dominates noise."""
    if M >= 256:
        return max(5, min(default, 10))
    if M >= 64:
        return max(10, min(default, 15))
    return default


def _tune_one_shape(
    bench,
    triton,
    label: str,
    num_experts: int,
    shard_intermediate_size: int,
    hidden_size: int,
    topk: int,
    block_shape: list[int],
    batch_sizes: list[int],
    base_search_space: list[dict],
    num_iters: int,
    abort_seconds: float,
    auto_iters: bool,
    dtype,
) -> dict[int, dict]:
    """Tune one (E, shard_intermediate_size, hidden, topk) shape across batch sizes.

    Mirrors `BenchmarkWorker.tune()` but in-process, with a per-M abort timer.
    Periodic Triton cache clears match the upstream behavior to avoid OOM
    during long tunes.
    """
    from tqdm import tqdm

    best_configs: dict[int, dict] = {}
    for M in batch_sizes:
        space = filter_search_space_for_M(base_search_space, M)
        iters = auto_num_iters(M, num_iters) if auto_iters else num_iters

        tic = time.time()
        best_cfg = None
        best_time = float("inf")
        tried = 0
        aborted = False
        clear_every = getattr(bench, "TRITON_CACHE_CLEAR_INTERVAL", 0)
        clear_fn = getattr(bench, "clear_triton_cache", lambda: None)

        for idx, cfg in enumerate(tqdm(space, desc=f"{label} M={M}", leave=False)):
            if abort_seconds and (time.time() - tic) > abort_seconds:
                aborted = True
                break
            try:
                kt = bench.benchmark_config(
                    cfg,
                    M,
                    num_experts,
                    shard_intermediate_size,
                    hidden_size,
                    topk,
                    dtype,
                    True,   # use_fp8_w8a8
                    False,  # use_int8_w8a16
                    use_int4_w4a16=False,
                    num_iters=iters,
                    block_quant_shape=block_shape,
                    use_deep_gemm=False,
                )
            except triton.runtime.autotuner.OutOfResources:
                continue
            except Exception as e:
                # Some configs can crash on certain GPUs (register pressure,
                # smem overflow). Skip and continue.
                print(f"   [WARN] {label} M={M} cfg={cfg}: {type(e).__name__}: {e}")
                continue

            tried += 1
            if kt < best_time:
                best_time = kt
                best_cfg = cfg

            if clear_every > 0 and idx > 0 and idx % clear_every == 0:
                clear_fn()

        clear_fn()
        elapsed = time.time() - tic
        if best_cfg is None:
            print(
                f"[driver]   {label} M={M:>4}: !! NO VALID CONFIG !! "
                f"tried={tried}/{len(space)} aborted={aborted} ({elapsed:.1f}s)"
            )
            # Fall back to a sane default so we still write a JSON entry.
            best_cfg = {
                "BLOCK_SIZE_M": 16 if M < 64 else 64,
                "BLOCK_SIZE_N": block_shape[0],
                "BLOCK_SIZE_K": block_shape[1],
                "GROUP_SIZE_M": 32,
                "num_warps": 4,
                "num_stages": 3,
            }
        else:
            ab = " [ABORTED]" if aborted else ""
            print(
                f"[driver]   {label} M={M:>4}: best={best_cfg} "
                f"t={best_time:.1f}us tried={tried}/{len(space)} "
                f"iters={iters} ({elapsed:.1f}s){ab}"
            )
        best_configs[M] = bench.sort_config(best_cfg)
    return best_configs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vllm-repo",
        type=Path,
        default=Path(os.environ.get("VLLM_REPO", "/home/jasl/Workspace/vllm")),
        help="Path to vllm git checkout (default: $VLLM_REPO).",
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
        help=(
            "Override shape list. Format: 'E,shard_int_size,hidden,topk:...'. "
            "block_shape is fixed to (--block-n, --block-k) for custom shapes. "
            "Default: 4 DSv4-Flash shapes covering TP=2/4/8 with EP plus "
            "TP=2 no-EP (typical 2/4/8-card RTX PRO 6000 and 2/4-node GB10)."
        ),
    )
    parser.add_argument(
        "--block-n", type=int, default=128, help="FP8 block N (default 128)."
    )
    parser.add_argument(
        "--block-k", type=int, default=128, help="FP8 block K (default 128)."
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
        default=20,
        help="Timing iterations per config (default 20, matching upstream tune()). "
        "Auto-reduced for large M (M>=256 → 10, M>=64 → 15) unless --no-auto-iters.",
    )
    parser.add_argument(
        "--no-auto-iters",
        action="store_true",
        help="Disable M-aware num_iters reduction; always use --num-iters.",
    )
    parser.add_argument(
        "--abort-seconds",
        type=float,
        default=1200.0,
        help="Per-(label, M) tuning wall-clock cap in seconds (default 1200). "
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
    if args.shapes:
        # Override block shape for custom inputs.
        shapes = tuple(
            (label, e, shard, hidden, topk, [args.block_n, args.block_k])
            for (label, e, shard, hidden, topk, _) in shapes
        )

    print(f"[driver] vllm_repo={args.vllm_repo}")
    print(f"[driver] out_dir={args.out_dir}")
    print(f"[driver] gpu_id={args.gpu_id}")
    print(f"[driver] batch_sizes={batch_sizes}")
    print("[driver] shapes (label, E, shard_int, hidden, topk, block):")
    for shape in shapes:
        print(f"[driver]   {shape}")
    print(f"[driver] block defaults=[{args.block_n}, {args.block_k}]")
    print(
        f"[driver] num_iters={args.num_iters} "
        f"auto_iters_by_M={'off' if args.no_auto_iters else 'on'}"
    )
    print(f"[driver] abort_seconds={args.abort_seconds}")

    if args.dry_run:
        n_tune = len(shapes) * len(batch_sizes)
        est_sec = 0.0
        for M in batch_sizes:
            base = 30 if M < 64 else (60 if M < 256 else (180 if M < 512 else 300))
            est_sec += base * len(shapes)
        print(
            f"[driver] dry-run: would tune {n_tune} (label, M) combos; "
            f"est {est_sec/60:.1f} min (highly variable based on JIT cache)."
        )
        return 0

    bench = _import_vllm_benchmark(args.vllm_repo)
    import torch  # noqa: E402  (imported after sys ready)
    from vllm.platforms import current_platform  # noqa: E402
    from vllm.triton_utils import triton  # noqa: E402

    torch.accelerator.set_device_index(args.gpu_id)
    torch.set_default_device("cuda")
    device_name = current_platform.get_device_name().replace(" ", "_")
    print(f"[driver] device_name={device_name}")

    # Build the search space using the upstream helper. `is_fp16=False` and
    # `block_quant_shape=[128,128]` give us the FP8 block-quantised search
    # space the upstream tune() uses.
    base_search_space = bench.get_configs_compute_bound(
        False, [args.block_n, args.block_k]
    )
    print(f"[driver] base search_space size: {len(base_search_space)} configs")

    dtype = torch.bfloat16

    overall_start = time.time()
    summary: dict[str, dict[int, dict]] = {}
    for shape_idx, (label, E, shard_int, hidden, topk, block_shape) in enumerate(
        shapes, 1
    ):
        shape_start = time.time()
        on_disk_n = shard_int // 2
        print(
            f"\n[driver] === Shape {shape_idx}/{len(shapes)}: {label} "
            f"(E={E}, N={on_disk_n}, hidden={hidden}, topk={topk}, "
            f"block={block_shape}) ==="
        )
        best_configs = _tune_one_shape(
            bench,
            triton,
            label,
            E,
            shard_int,
            hidden,
            topk,
            block_shape,
            batch_sizes,
            base_search_space,
            args.num_iters,
            args.abort_seconds,
            not args.no_auto_iters,
            dtype,
        )
        bench.save_configs(
            best_configs,
            E,
            shard_int,
            hidden,
            topk,
            dtype,
            True,   # use_fp8_w8a8
            False,  # use_int8_w8a16
            False,  # use_int4_w4a16
            block_shape,
            str(args.out_dir),
        )
        summary[label] = {
            "num_experts": E,
            "shard_intermediate_size": shard_int,
            "on_disk_N": on_disk_n,
            "hidden_size": hidden,
            "topk": topk,
            "block_shape": block_shape,
            "configs": best_configs,
        }
        print(f"[driver] shape {label} took {time.time() - shape_start:.1f}s")

    overall_elapsed = time.time() - overall_start
    print(f"\n[driver] total runtime: {overall_elapsed/60:.1f} min")
    summary_path = args.out_dir / "tuning_summary.json"
    with open(summary_path, "w") as f:
        json.dump(
            {
                "device_name": device_name,
                "block_defaults": [args.block_n, args.block_k],
                "batch_sizes": batch_sizes,
                "shapes": [
                    {
                        "label": label,
                        "num_experts": e,
                        "shard_intermediate_size": shard,
                        "on_disk_N": shard // 2,
                        "hidden_size": hidden,
                        "topk": topk,
                        "block_shape": block_shape,
                    }
                    for label, e, shard, hidden, topk, block_shape in shapes
                ],
                "results": summary,
                "wall_seconds": overall_elapsed,
            },
            f,
            indent=2,
        )
    print(f"[driver] summary → {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
