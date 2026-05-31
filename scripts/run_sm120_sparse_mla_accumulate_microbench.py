#!/usr/bin/env python3
"""Microbenchmark the SM12x sparse MLA prefill accumulate path.

This drives ``accumulate_indexed_sparse_mla_attention_chunk`` directly with
deterministic synthetic tensors. It is a pre-endpoint gate for experiments that
try to reduce long-prefill interference by changing how candidate chunks update
the online softmax state.
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


def _parse_chunk_list(value: str) -> list[int | None]:
    chunks: list[int | None] = []
    for item in [item.strip() for item in value.split(",") if item.strip()]:
        if item.lower() in {"single", "full", "none"}:
            chunks.append(None)
            continue
        try:
            parsed = int(item)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(str(exc)) from exc
        if parsed <= 0:
            raise argparse.ArgumentTypeError("chunk sizes must be positive")
        chunks.append(parsed)
    if not chunks:
        raise argparse.ArgumentTypeError("expected at least one chunk size")
    return chunks


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


def _chunk_label(chunk_size: int | None) -> str:
    return "single" if chunk_size is None else str(chunk_size)


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# SM12x sparse MLA accumulate microbench",
        "",
        f"- device: `{payload['device_name']}`",
        f"- compute_capability: `{payload['compute_capability']}`",
        f"- num_tokens: `{payload['num_tokens']}`",
        f"- num_heads: `{payload['num_heads']}`",
        f"- head_dim: `{payload['head_dim']}`",
        f"- kv_tokens: `{payload['kv_tokens']}`",
        f"- warmup / iterations: `{payload['warmup']} / {payload['iterations']}`",
        "",
        (
            "| candidates | chunk size | calls | mean ms | p95 ms | "
            "min ms | max ms |"
        ),
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            (
                "| {num_candidates} | {chunk_size_label} | {call_count} | "
                "{mean_ms:.3f} | {p95_ms:.3f} | {min_ms:.3f} | {max_ms:.3f} |"
            ).format(**row)
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark SM12x sparse MLA prefill accumulate shapes."
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--candidate-lens", type=_parse_int_list, default="512,1024,1152")
    parser.add_argument("--chunk-sizes", type=_parse_chunk_list, default="single,256,512,1024")
    parser.add_argument("--num-tokens", type=int, default=256)
    parser.add_argument("--num-heads", type=int, default=64)
    parser.add_argument("--head-dim", type=int, default=128)
    parser.add_argument("--kv-tokens", type=int, default=131072)
    parser.add_argument("--scale", type=float, default=0.08838834764831845)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--gpu-id", type=int, default=0)
    args = parser.parse_args()

    if args.num_tokens <= 0 or args.num_heads <= 0 or args.head_dim <= 0:
        parser.error("--num-tokens, --num-heads, and --head-dim must be positive")
    if args.kv_tokens <= 0:
        parser.error("--kv-tokens must be positive")
    if args.warmup < 0 or args.iterations <= 0:
        parser.error("--warmup must be >= 0 and --iterations must be > 0")
    if max(args.candidate_lens) > args.kv_tokens:
        parser.error("--kv-tokens must cover the largest candidate length")

    import torch

    if not torch.cuda.is_available():
        print("CUDA is not available", file=sys.stderr)
        return 2

    torch.cuda.set_device(args.gpu_id)
    device = torch.device(f"cuda:{args.gpu_id}")
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    from vllm.v1.attention.backends.mla.sparse_mla_kernels import (
        accumulate_indexed_sparse_mla_attention_chunk,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    q = torch.randn(
        args.num_tokens,
        args.num_heads,
        args.head_dim,
        device=device,
        dtype=torch.bfloat16,
    )
    kv_flat = torch.randn(
        args.kv_tokens,
        args.head_dim,
        device=device,
        dtype=torch.bfloat16,
    )
    max_score = torch.empty(
        args.num_tokens,
        args.num_heads,
        device=device,
        dtype=torch.float32,
    )
    denom = torch.empty_like(max_score)
    acc = torch.empty(
        args.num_tokens,
        args.num_heads,
        args.head_dim,
        device=device,
        dtype=torch.float32,
    )

    rows: list[dict[str, Any]] = []
    for num_candidates in args.candidate_lens:
        generator = torch.Generator(device=device)
        generator.manual_seed(args.seed + num_candidates)
        indices = torch.randperm(
            args.kv_tokens,
            device=device,
            generator=generator,
            dtype=torch.int64,
        )[:num_candidates]
        indices = indices.to(torch.int32).repeat(args.num_tokens, 1).contiguous()
        lens = torch.full(
            (args.num_tokens,),
            num_candidates,
            device=device,
            dtype=torch.int32,
        )

        for chunk_size in args.chunk_sizes:
            effective_chunk = num_candidates if chunk_size is None else chunk_size
            effective_chunk = min(effective_chunk, num_candidates)
            call_count = (num_candidates + effective_chunk - 1) // effective_chunk

            def reset_state() -> None:
                max_score.fill_(float("-inf"))
                denom.zero_()
                acc.zero_()

            def run_accumulate() -> None:
                for candidate_offset in range(0, num_candidates, effective_chunk):
                    candidate_end = min(
                        candidate_offset + effective_chunk,
                        num_candidates,
                    )
                    accumulate_indexed_sparse_mla_attention_chunk(
                        q=q,
                        kv_flat=kv_flat,
                        indices=indices[:, candidate_offset:candidate_end],
                        lens=lens,
                        candidate_offset=candidate_offset,
                        scale=args.scale,
                        max_score=max_score,
                        denom=denom,
                        acc=acc,
                    )

            for _ in range(args.warmup):
                reset_state()
                run_accumulate()
            torch.cuda.synchronize()

            samples_ms: list[float] = []
            for _ in range(args.iterations):
                reset_state()
                torch.cuda.synchronize()
                start = torch.cuda.Event(enable_timing=True)
                end = torch.cuda.Event(enable_timing=True)
                start.record()
                run_accumulate()
                end.record()
                torch.cuda.synchronize()
                samples_ms.append(float(start.elapsed_time(end)))

            rows.append(
                {
                    "num_candidates": num_candidates,
                    "chunk_size": chunk_size,
                    "chunk_size_label": _chunk_label(chunk_size),
                    "effective_chunk_size": effective_chunk,
                    "call_count": call_count,
                    **_summarize_ms(samples_ms),
                }
            )

    payload = {
        "device_name": torch.cuda.get_device_name(args.gpu_id),
        "compute_capability": "{}.{}".format(
            *torch.cuda.get_device_capability(args.gpu_id)
        ),
        "torch_version": torch.__version__,
        "seed": args.seed,
        "num_tokens": args.num_tokens,
        "num_heads": args.num_heads,
        "head_dim": args.head_dim,
        "kv_tokens": args.kv_tokens,
        "warmup": args.warmup,
        "iterations": args.iterations,
        "rows": rows,
    }
    json_path = args.output_dir / "sparse_mla_accumulate_microbench.json"
    md_path = args.output_dir / "sparse_mla_accumulate_microbench.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(md_path, payload)
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
