#!/usr/bin/env python3
"""Microbenchmark the SM120 FP8 MQA direct top-k path.

This script is intentionally narrow: it drives the current
``fp8_fp4_mqa_topk_indices`` API with deterministic FP8-Q / FP8-K tensors so a
future streaming top-k prototype can be compared against the same shapes before
running expensive endpoint gates.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any


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


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# SM120 FP8 MQA top-k microbench",
        "",
        f"- device: `{payload['device_name']}`",
        f"- compute_capability: `{payload['compute_capability']}`",
        f"- num_q: `{payload['num_q']}`",
        f"- num_heads: `{payload['num_heads']}`",
        f"- head_dim: `{payload['head_dim']}`",
        f"- topk_tokens: `{payload['topk_tokens']}`",
        f"- warmup / iterations: `{payload['warmup']} / {payload['iterations']}`",
        "",
        (
            "| seq_len_kv | mean ms | p95 ms | min ms | max ms | "
            "repeat set | repeat order | reference set | reference order |"
        ),
        "| ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        reference = row.get("reference_set_ok")
        if reference is None:
            reference = "skipped"
        reference_order = row.get("reference_order_ok")
        if reference_order is None:
            reference_order = "skipped"
        lines.append(
            (
                "| {seq_len_kv} | {mean_ms:.3f} | {p95_ms:.3f} | "
                "{min_ms:.3f} | {max_ms:.3f} | {repeat_set_ok} | "
                "{repeat_order_ok} | {reference} | {reference_order} |"
            ).format(reference=reference, reference_order=reference_order, **row)
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark SM120 direct FP8 MQA top-k fallback shapes."
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seq-len-kv", type=_parse_int_list, default="4096,32768")
    parser.add_argument("--num-q", type=int, default=256)
    parser.add_argument("--num-heads", type=int, default=64)
    parser.add_argument("--head-dim", type=int, default=128)
    parser.add_argument("--topk-tokens", type=int, default=2048)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--gpu-id", type=int, default=0)
    parser.add_argument(
        "--reference-max-kv",
        type=int,
        default=4096,
        help="Run full-logits reference parity only up to this KV width.",
    )
    args = parser.parse_args()

    if args.num_q <= 0 or args.num_heads <= 0 or args.head_dim <= 0:
        parser.error("--num-q, --num-heads, and --head-dim must be positive")
    if args.topk_tokens <= 0:
        parser.error("--topk-tokens must be positive")
    if args.warmup < 0 or args.iterations <= 0:
        parser.error("--warmup must be >= 0 and --iterations must be > 0")

    import torch

    if not torch.cuda.is_available():
        print("CUDA is not available", file=sys.stderr)
        return 2

    torch.cuda.set_device(args.gpu_id)
    device = torch.device(f"cuda:{args.gpu_id}")
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    from vllm.models.deepseek_v4.nvidia.ops.sm12x_deep_gemm_fallbacks import (
        _fp8_mqa_logits_torch,
    )
    from vllm.utils.deep_gemm import fp8_fp4_mqa_topk_indices

    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for seq_len_kv in args.seq_len_kv:
        torch.manual_seed(args.seed + seq_len_kv)
        q_bf16 = torch.randn(
            args.num_q,
            args.num_heads,
            args.head_dim,
            device=device,
            dtype=torch.bfloat16,
        )
        k_bf16 = torch.randn(
            seq_len_kv,
            args.head_dim,
            device=device,
            dtype=torch.bfloat16,
        )
        q_values = q_bf16.to(torch.float8_e4m3fn)
        k_values = k_bf16.to(torch.float8_e4m3fn)
        k_scales = torch.ones(seq_len_kv, device=device, dtype=torch.float32)
        weights = torch.rand(
            args.num_q,
            args.num_heads,
            device=device,
            dtype=torch.float32,
        )
        cu_seqlen_ks = torch.zeros(args.num_q, device=device, dtype=torch.int32)
        cu_seqlen_ke = torch.full(
            (args.num_q,),
            seq_len_kv,
            device=device,
            dtype=torch.int32,
        )
        select_k = min(args.topk_tokens, seq_len_kv)
        out = torch.empty(args.num_q, select_k, device=device, dtype=torch.int32)

        for _ in range(args.warmup):
            ok = fp8_fp4_mqa_topk_indices(
                (q_values, None),
                (k_values, k_scales),
                weights,
                cu_seqlen_ks,
                cu_seqlen_ke,
                out,
            )
            if not ok:
                raise RuntimeError("fp8_fp4_mqa_topk_indices returned False")
        torch.cuda.synchronize()

        samples_ms: list[float] = []
        first_out = None
        for iteration in range(args.iterations):
            start = torch.cuda.Event(enable_timing=True)
            end = torch.cuda.Event(enable_timing=True)
            start.record()
            ok = fp8_fp4_mqa_topk_indices(
                (q_values, None),
                (k_values, k_scales),
                weights,
                cu_seqlen_ks,
                cu_seqlen_ke,
                out,
            )
            end.record()
            torch.cuda.synchronize()
            if not ok:
                raise RuntimeError("fp8_fp4_mqa_topk_indices returned False")
            samples_ms.append(float(start.elapsed_time(end)))
            if iteration == 0:
                first_out = out.detach().clone()

        repeat_order_ok = bool(torch.equal(first_out, out))
        repeat_set_ok = bool(
            torch.equal(
                torch.sort(first_out, dim=1).values,
                torch.sort(out, dim=1).values,
            )
        )
        reference_set_ok: bool | None = None
        reference_order_ok: bool | None = None
        if seq_len_kv <= args.reference_max_kv:
            reference_logits = _fp8_mqa_logits_torch(
                (q_values, None),
                (k_values, k_scales),
                weights,
                cu_seqlen_ks,
                cu_seqlen_ke,
                clean_logits=True,
            )
            _, reference_indices = torch.topk(reference_logits, select_k, dim=1)
            reference_i32 = reference_indices.to(torch.int32)
            reference_order_ok = bool(torch.equal(out, reference_i32))
            reference_set_ok = bool(
                torch.equal(
                    torch.sort(out, dim=1).values,
                    torch.sort(reference_i32, dim=1).values,
                )
            )

        row = {
            "seq_len_kv": seq_len_kv,
            "topk_tokens": select_k,
            "repeat_set_ok": repeat_set_ok,
            "repeat_order_ok": repeat_order_ok,
            "reference_set_ok": reference_set_ok,
            "reference_order_ok": reference_order_ok,
            **_summarize_ms(samples_ms),
        }
        rows.append(row)

    payload = {
        "device_name": torch.cuda.get_device_name(args.gpu_id),
        "compute_capability": "{}.{}".format(
            *torch.cuda.get_device_capability(args.gpu_id)
        ),
        "torch_version": torch.__version__,
        "seed": args.seed,
        "num_q": args.num_q,
        "num_heads": args.num_heads,
        "head_dim": args.head_dim,
        "topk_tokens": args.topk_tokens,
        "warmup": args.warmup,
        "iterations": args.iterations,
        "rows": rows,
    }
    json_path = args.output_dir / "mqa_topk_microbench.json"
    md_path = args.output_dir / "mqa_topk_microbench.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(md_path, payload)
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
