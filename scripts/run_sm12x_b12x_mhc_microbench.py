#!/usr/bin/env python3
"""Compare current TileLang mHC and public b12x fused mHC.

This is a research microbench, not a PR gate. It answers whether the released
b12x mHC residual path is worth wiring into the DeepSeek V4 endpoint before
spending time on CUDA graph and full-model validation.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Callable


def _parse_int_list(value: str) -> list[int]:
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise argparse.ArgumentTypeError("expected at least one integer")
    try:
        parsed = [int(item) for item in items]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if any(item <= 0 for item in parsed):
        raise argparse.ArgumentTypeError("all integers must be positive")
    return parsed


def _percentile(sorted_values: list[float], percentile: float) -> float:
    if not sorted_values:
        return float("nan")
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (len(sorted_values) - 1) * percentile
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = rank - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def _summarize_ms(samples_ms: list[float]) -> dict[str, float]:
    ordered = sorted(samples_ms)
    return {
        "mean_ms": statistics.fmean(samples_ms),
        "median_ms": statistics.median(samples_ms),
        "p95_ms": _percentile(ordered, 0.95),
        "min_ms": min(samples_ms),
        "max_ms": max(samples_ms),
    }


def _speedup(base_ms: float, candidate_ms: float) -> float:
    if candidate_ms <= 0:
        return float("nan")
    return base_ms / candidate_ms


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# SM12x b12x mHC microbench",
        "",
        f"- device: `{payload['device_name']}`",
        f"- compute_capability: `{payload['compute_capability']}`",
        f"- hidden_size: `{payload['hidden_size']}`",
        f"- hc_mult: `{payload['hc_mult']}`",
        f"- split_k: `{payload['split_k']}`",
        f"- block_k: `{payload['block_k']}`",
        f"- norm_weight: `{payload['use_norm_weight']}`",
        f"- warmup / iterations: `{payload['warmup']} / {payload['iterations']}`",
        "",
        (
            "| tokens | tilelang fused ms | b12x fused ms | speedup | "
            "residual diff | post diff | comb diff | y diff |"
        ),
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            (
                "| {num_tokens} | {tilelang_fused_mean_ms:.3f} | "
                "{b12x_fused_mean_ms:.3f} | {b12x_fused_speedup:.3f}x | "
                "{max_abs_diff_residual:.6f} | {max_abs_diff_post:.6f} | "
                "{max_abs_diff_comb:.6f} | {max_abs_diff_y:.6f} |"
            ).format(**row)
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _event_time_ms(func: Callable[[], Any], *, iterations: int) -> list[float]:
    import torch

    samples: list[float] = []
    for _ in range(iterations):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        func()
        end.record()
        torch.cuda.synchronize()
        samples.append(float(start.elapsed_time(end)))
    return samples


def _max_abs(a: Any, b: Any) -> float:
    return float((a.float() - b.float()).abs().max().item()) if a.numel() else 0.0


def _make_inputs(
    *,
    torch_mod: Any,
    num_tokens: int,
    hidden_size: int,
    hc_mult: int,
    device: Any,
    seed: int,
    use_norm_weight: bool,
) -> dict[str, Any]:
    generator = torch_mod.Generator(device=device)
    generator.manual_seed(seed)
    mix_hc = (2 + hc_mult) * hc_mult
    hc_dim = hc_mult * hidden_size
    return {
        "x": torch_mod.randn(
            num_tokens,
            hidden_size,
            device=device,
            dtype=torch_mod.bfloat16,
            generator=generator,
        ),
        "residual": torch_mod.randn(
            num_tokens,
            hc_mult,
            hidden_size,
            device=device,
            dtype=torch_mod.bfloat16,
            generator=generator,
        ),
        "post": torch_mod.randn(
            num_tokens,
            hc_mult,
            1,
            device=device,
            dtype=torch_mod.float32,
            generator=generator,
        ),
        "comb": torch_mod.randn(
            num_tokens,
            hc_mult,
            hc_mult,
            device=device,
            dtype=torch_mod.float32,
            generator=generator,
        ),
        "fn": torch_mod.randn(
            mix_hc,
            hc_dim,
            device=device,
            dtype=torch_mod.float32,
            generator=generator,
        ),
        "hc_scale": torch_mod.tensor(
            [1.0, 1.0, 1.0],
            device=device,
            dtype=torch_mod.float32,
        ),
        "hc_base": torch_mod.zeros(mix_hc, device=device, dtype=torch_mod.float32),
        "norm_weight": (
            torch_mod.ones(hidden_size, device=device, dtype=torch_mod.bfloat16)
            if use_norm_weight
            else None
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--tokens", type=_parse_int_list, default="1,4,16,64,256,1024")
    parser.add_argument("--hidden-size", type=int, default=4096)
    parser.add_argument("--hc-mult", type=int, default=4)
    parser.add_argument("--rms-eps", type=float, default=1e-6)
    parser.add_argument("--hc-eps", type=float, default=1e-6)
    parser.add_argument("--hc-post-alpha", type=float, default=2.0)
    parser.add_argument("--sinkhorn-iters", type=int, default=20)
    parser.add_argument("--split-k", type=int, default=64)
    parser.add_argument("--block-k", type=int, default=256)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--gpu-id", type=int, default=0)
    parser.add_argument("--no-norm-weight", action="store_true")
    args = parser.parse_args()

    import torch

    if not torch.cuda.is_available():
        print("CUDA is required for this microbench", file=sys.stderr)
        return 2

    torch.cuda.set_device(args.gpu_id)
    device = torch.device("cuda", args.gpu_id)

    from b12x.integration.residual import b12x_mhc_post_pre, empty_mhc_workspace
    from vllm.model_executor.kernels.mhc.tilelang import (
        mhc_fused_post_pre_tilelang,
    )

    use_norm_weight = not args.no_norm_weight
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for num_tokens in args.tokens:
        inputs = _make_inputs(
            torch_mod=torch,
            num_tokens=num_tokens,
            hidden_size=args.hidden_size,
            hc_mult=args.hc_mult,
            device=device,
            seed=args.seed + num_tokens,
            use_norm_weight=use_norm_weight,
        )

        def run_tilelang() -> tuple[Any, Any, Any, Any]:
            return mhc_fused_post_pre_tilelang(
                inputs["x"],
                inputs["residual"],
                inputs["post"],
                inputs["comb"],
                inputs["fn"],
                inputs["hc_scale"],
                inputs["hc_base"],
                args.rms_eps,
                args.hc_eps,
                args.hc_eps,
                args.hc_post_alpha,
                args.sinkhorn_iters,
                norm_weight=inputs["norm_weight"],
                norm_eps=args.rms_eps,
            )

        workspace = empty_mhc_workspace(
            num_tokens=num_tokens,
            hidden_size=args.hidden_size,
            dtype=torch.bfloat16,
            split_k=args.split_k,
            device=device,
        )

        def run_b12x() -> tuple[Any, Any, Any, Any]:
            return b12x_mhc_post_pre(
                inputs["x"],
                inputs["residual"],
                inputs["post"],
                inputs["comb"],
                inputs["fn"],
                inputs["hc_scale"],
                inputs["hc_base"],
                rms_eps=args.rms_eps,
                hc_eps=args.hc_eps,
                sinkhorn_iters=args.sinkhorn_iters,
                workspace=workspace,
                norm_weight=inputs["norm_weight"],
                norm_eps=args.rms_eps,
                split_k=args.split_k,
                block_k=args.block_k,
            )

        for _ in range(args.warmup):
            run_tilelang()
            run_b12x()
        torch.cuda.synchronize()

        tilelang_out = run_tilelang()
        b12x_out = run_b12x()
        torch.cuda.synchronize()

        tilelang_ms = _event_time_ms(run_tilelang, iterations=args.iterations)
        b12x_ms = _event_time_ms(run_b12x, iterations=args.iterations)
        tilelang_summary = _summarize_ms(tilelang_ms)
        b12x_summary = _summarize_ms(b12x_ms)

        rows.append(
            {
                "num_tokens": num_tokens,
                "tilelang_fused": tilelang_summary,
                "b12x_fused": b12x_summary,
                "tilelang_fused_mean_ms": tilelang_summary["mean_ms"],
                "b12x_fused_mean_ms": b12x_summary["mean_ms"],
                "b12x_fused_speedup": _speedup(
                    tilelang_summary["mean_ms"], b12x_summary["mean_ms"]
                ),
                "max_abs_diff_residual": _max_abs(tilelang_out[0], b12x_out[0]),
                "max_abs_diff_post": _max_abs(tilelang_out[1].squeeze(-1), b12x_out[1]),
                "max_abs_diff_comb": _max_abs(tilelang_out[2], b12x_out[2]),
                "max_abs_diff_y": _max_abs(tilelang_out[3], b12x_out[3]),
            }
        )

    payload: dict[str, Any] = {
        "case": "sm12x_b12x_mhc_microbench",
        "device_name": torch.cuda.get_device_name(args.gpu_id),
        "compute_capability": torch.cuda.get_device_capability(args.gpu_id),
        "hidden_size": args.hidden_size,
        "hc_mult": args.hc_mult,
        "split_k": args.split_k,
        "block_k": args.block_k,
        "use_norm_weight": use_norm_weight,
        "warmup": args.warmup,
        "iterations": args.iterations,
        "rows": rows,
    }
    (args.output_dir / "sm12x_b12x_mhc_microbench.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_markdown(args.output_dir / "sm12x_b12x_mhc_microbench.md", payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
