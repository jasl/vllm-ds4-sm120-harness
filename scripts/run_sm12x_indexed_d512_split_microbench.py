#!/usr/bin/env python3
"""Prototype an indexed D=512 split sparse-MLA accumulate path.

This is an experiment script, not a harness gate. It targets the C4-style
production bottleneck where candidate lists differ per token, so grouped C128
candidate reuse does not apply. The baseline is vLLM's production partial-state
indexed sparse MLA path. The candidate path splits work into:

1. score materialization with a head-block x candidate-block tensor-core dot;
2. per-token/head max and denom over the score workspace;
3. value accumulation split over the D=512 dimension.

If this does not beat the production partial path for per-token random
candidates, it should stay as a rejected experiment.
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
        "# SM12x indexed D512 split microbench",
        "",
        f"- device: `{payload['device_name']}`",
        f"- compute_capability: `{payload['compute_capability']}`",
        f"- num_tokens: `{payload['num_tokens']}`",
        f"- num_heads: `{payload['num_heads']}`",
        f"- head_dim: `{payload['head_dim']}`",
        f"- head_block: `{payload['head_block']}`",
        f"- block_c / block_d: `{payload['block_c']} / {payload['block_d']}`",
        f"- score_dtype: `{payload['score_dtype']}`",
        f"- score_workspace_mib: `{payload['score_workspace_mib']:.2f}`",
        f"- index_pattern: `{payload['index_pattern']}`",
        f"- warmup / iterations: `{payload['warmup']} / {payload['iterations']}`",
        "",
        (
            "| candidates | partial ms | split total ms | partial speedup | "
            "score ms | stats ms | value ms | max abs diff |"
        ),
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            (
                "| {num_candidates} | {partial_mean_ms:.3f} | "
                "{split_total_mean_ms:.3f} | {partial_speedup:.3f}x | "
                "{score_mean_ms:.3f} | {stats_mean_ms:.3f} | "
                "{value_mean_ms:.3f} | {max_abs_diff:.6f} |"
            ).format(**row)
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _next_power_of_2(value: int) -> int:
    return 1 << (value - 1).bit_length()


def _validate_sliding_window_index_shape(
    *,
    num_tokens: int,
    num_candidates: int,
    kv_tokens: int,
) -> None:
    required_kv_tokens = num_tokens + num_candidates - 1
    if kv_tokens < required_kv_tokens:
        raise ValueError(
            "sliding-window index pattern requires kv_tokens >= "
            f"num_tokens + num_candidates - 1 ({required_kv_tokens})"
        )


def _validate_mixed_c128_swa_index_shape(
    *,
    num_tokens: int,
    num_candidates: int,
    compressed_candidates: int,
    kv_tokens: int,
) -> None:
    if compressed_candidates <= 0 or compressed_candidates >= num_candidates:
        raise ValueError(
            "mixed-c128-swa index pattern requires compressed_candidates "
            "to be between 1 and num_candidates - 1"
        )
    _validate_sliding_window_index_shape(
        num_tokens=num_tokens,
        num_candidates=num_candidates - compressed_candidates,
        kv_tokens=kv_tokens,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark an indexed split D=512 sparse MLA path."
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--candidate-lens", type=_parse_int_list, default="640")
    parser.add_argument("--num-tokens", type=int, default=256)
    parser.add_argument("--num-heads", type=int, default=64)
    parser.add_argument("--head-dim", type=int, default=512)
    parser.add_argument("--kv-tokens", type=int, default=131072)
    parser.add_argument("--head-block", type=int, default=16)
    parser.add_argument("--block-c", type=int, default=64)
    parser.add_argument("--block-d", type=int, default=64)
    parser.add_argument("--part-size", type=int, default=512)
    parser.add_argument("--compressed-candidates", type=int, default=128)
    parser.add_argument(
        "--score-dtype",
        choices=("float32", "bfloat16"),
        default="float32",
        help="dtype used for the materialized score workspace",
    )
    parser.add_argument("--scale", type=float, default=0.04419417382415922)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--gpu-id", type=int, default=0)
    parser.add_argument(
        "--index-pattern",
        choices=("per-token", "shared", "sliding-window", "mixed-c128-swa"),
        default="per-token",
    )
    args = parser.parse_args()

    if args.num_tokens <= 0 or args.num_heads <= 0 or args.head_dim <= 0:
        parser.error("--num-tokens, --num-heads, and --head-dim must be positive")
    if args.head_block <= 0 or args.block_c <= 0 or args.block_d <= 0:
        parser.error("--head-block, --block-c, and --block-d must be positive")
    if args.num_heads % args.head_block != 0:
        parser.error("--num-heads must be divisible by --head-block")
    if args.head_dim % args.block_d != 0:
        parser.error("--head-dim must be divisible by --block-d")
    if max(args.candidate_lens) > args.kv_tokens:
        parser.error("--kv-tokens must cover the largest candidate length")
    if args.part_size <= 0:
        parser.error("--part-size must be positive")
    if args.warmup < 0 or args.iterations <= 0:
        parser.error("--warmup must be >= 0 and --iterations must be > 0")

    import torch
    import triton
    import triton.language as tl

    if not torch.cuda.is_available():
        print("CUDA is not available", file=sys.stderr)
        return 2

    @triton.jit
    def _indexed_score_kernel(
        q_ptr,
        kv_ptr,
        indices_ptr,
        scores_ptr,
        stride_q_t: tl.constexpr,
        stride_q_h: tl.constexpr,
        stride_q_d: tl.constexpr,
        stride_kv_t,
        stride_kv_d: tl.constexpr,
        stride_indices_t: tl.constexpr,
        stride_indices_c: tl.constexpr,
        stride_s_t: tl.constexpr,
        stride_s_h: tl.constexpr,
        stride_s_c: tl.constexpr,
        num_tokens: tl.constexpr,
        num_heads: tl.constexpr,
        num_candidates: tl.constexpr,
        scale: tl.constexpr,
        HEAD_BLOCK: tl.constexpr,
        BLOCK_C: tl.constexpr,
        HEAD_DIM: tl.constexpr,
    ):
        token_idx = tl.program_id(0)
        head_block_idx = tl.program_id(1)
        candidate_block = tl.program_id(2)
        head_offsets = head_block_idx * HEAD_BLOCK + tl.arange(0, HEAD_BLOCK)
        candidate_offsets = candidate_block * BLOCK_C + tl.arange(0, BLOCK_C)
        dim_offsets = tl.arange(0, HEAD_DIM)
        head_mask = head_offsets < num_heads
        candidate_mask = candidate_offsets < num_candidates

        q = tl.load(
            q_ptr
            + token_idx * stride_q_t
            + head_offsets[:, None] * stride_q_h
            + dim_offsets[None, :] * stride_q_d,
            mask=head_mask[:, None],
            other=0.0,
        )
        kv_indices = tl.load(
            indices_ptr
            + token_idx * stride_indices_t
            + candidate_offsets * stride_indices_c,
            mask=candidate_mask,
            other=-1,
        )
        valid_kv = kv_indices >= 0
        kv = tl.load(
            kv_ptr
            + kv_indices[None, :].to(tl.int64) * stride_kv_t
            + dim_offsets[:, None] * stride_kv_d,
            mask=valid_kv[None, :],
            other=0.0,
        )
        scores = tl.dot(q, kv) * scale
        tl.store(
            scores_ptr
            + token_idx * stride_s_t
            + head_offsets[:, None] * stride_s_h
            + candidate_offsets[None, :] * stride_s_c,
            scores,
            mask=head_mask[:, None] & candidate_mask[None, :],
        )

    @triton.jit
    def _indexed_stats_kernel(
        scores_ptr,
        max_ptr,
        denom_ptr,
        stride_s_t: tl.constexpr,
        stride_s_h: tl.constexpr,
        stride_s_c: tl.constexpr,
        stride_state_t: tl.constexpr,
        stride_state_h: tl.constexpr,
        num_candidates: tl.constexpr,
        BLOCK_C: tl.constexpr,
    ):
        token_idx = tl.program_id(0)
        head_idx = tl.program_id(1)
        candidate_offsets = tl.arange(0, BLOCK_C)
        candidate_mask = candidate_offsets < num_candidates
        scores = tl.load(
            scores_ptr
            + token_idx * stride_s_t
            + head_idx * stride_s_h
            + candidate_offsets * stride_s_c,
            mask=candidate_mask,
            other=-float("inf"),
        ).to(tl.float32)
        running_max = tl.max(scores, axis=0)
        weights = tl.where(candidate_mask, tl.exp(scores - running_max), 0.0)
        running_denom = tl.sum(weights, axis=0)
        tl.store(max_ptr + token_idx * stride_state_t + head_idx * stride_state_h, running_max)
        tl.store(denom_ptr + token_idx * stride_state_t + head_idx * stride_state_h, running_denom)

    @triton.jit
    def _indexed_value_kernel(
        scores_ptr,
        kv_ptr,
        indices_ptr,
        max_ptr,
        denom_ptr,
        out_ptr,
        stride_s_t: tl.constexpr,
        stride_s_h: tl.constexpr,
        stride_s_c: tl.constexpr,
        stride_kv_t,
        stride_kv_d: tl.constexpr,
        stride_indices_t: tl.constexpr,
        stride_indices_c: tl.constexpr,
        stride_state_t: tl.constexpr,
        stride_state_h: tl.constexpr,
        stride_out_t: tl.constexpr,
        stride_out_h: tl.constexpr,
        stride_out_d: tl.constexpr,
        num_heads: tl.constexpr,
        num_candidates: tl.constexpr,
        head_dim: tl.constexpr,
        HEAD_BLOCK: tl.constexpr,
        BLOCK_C: tl.constexpr,
        BLOCK_D: tl.constexpr,
    ):
        token_idx = tl.program_id(0)
        head_block_idx = tl.program_id(1)
        dim_block = tl.program_id(2)
        head_offsets = head_block_idx * HEAD_BLOCK + tl.arange(0, HEAD_BLOCK)
        candidate_offsets = tl.arange(0, BLOCK_C)
        dim_offsets = dim_block * BLOCK_D + tl.arange(0, BLOCK_D)
        head_mask = head_offsets < num_heads
        dim_mask = dim_offsets < head_dim
        max_score = tl.load(
            max_ptr + token_idx * stride_state_t + head_offsets * stride_state_h,
            mask=head_mask,
            other=0.0,
        ).to(tl.float32)
        denom = tl.load(
            denom_ptr + token_idx * stride_state_t + head_offsets * stride_state_h,
            mask=head_mask,
            other=1.0,
        ).to(tl.float32)
        acc = tl.zeros((HEAD_BLOCK, BLOCK_D), tl.float32)

        for candidate_start in range(0, num_candidates, BLOCK_C):
            candidates = candidate_start + candidate_offsets
            candidate_mask = candidates < num_candidates
            kv_indices = tl.load(
                indices_ptr
                + token_idx * stride_indices_t
                + candidates * stride_indices_c,
                mask=candidate_mask,
                other=-1,
            )
            valid_kv = kv_indices >= 0
            scores = tl.load(
                scores_ptr
                + token_idx * stride_s_t
                + head_offsets[:, None] * stride_s_h
                + candidates[None, :] * stride_s_c,
                mask=head_mask[:, None] & candidate_mask[None, :],
                other=-float("inf"),
            ).to(tl.float32)
            weights = tl.exp(scores - max_score[:, None]) / denom[:, None]
            values = tl.load(
                kv_ptr
                + kv_indices[:, None].to(tl.int64) * stride_kv_t
                + dim_offsets[None, :] * stride_kv_d,
                mask=valid_kv[:, None] & dim_mask[None, :],
                other=0.0,
            )
            acc += tl.dot(weights.to(tl.bfloat16), values)

        tl.store(
            out_ptr
            + token_idx * stride_out_t
            + head_offsets[:, None] * stride_out_h
            + dim_offsets[None, :] * stride_out_d,
            acc,
            mask=head_mask[:, None] & dim_mask[None, :],
        )

    from vllm.v1.attention.backends.mla.sparse_mla_kernels import (
        accumulate_indexed_sparse_mla_attention_partial_states,
        merge_sparse_mla_attention_states,
    )

    torch.cuda.set_device(args.gpu_id)
    device = torch.device(f"cuda:{args.gpu_id}")
    score_dtype = {
        "float32": torch.float32,
        "bfloat16": torch.bfloat16,
    }[args.score_dtype]
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

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
    lens_template = torch.empty(args.num_tokens, device=device, dtype=torch.int32)

    rows: list[dict[str, Any]] = []
    for num_candidates in args.candidate_lens:
        generator = torch.Generator(device=device)
        generator.manual_seed(args.seed + num_candidates)
        if args.index_pattern == "shared":
            indices = torch.randperm(
                args.kv_tokens,
                device=device,
                generator=generator,
                dtype=torch.int64,
            )[:num_candidates]
            indices = indices.to(torch.int32).repeat(args.num_tokens, 1).contiguous()
        elif args.index_pattern == "sliding-window":
            try:
                _validate_sliding_window_index_shape(
                    num_tokens=args.num_tokens,
                    num_candidates=num_candidates,
                    kv_tokens=args.kv_tokens,
                )
            except ValueError as exc:
                parser.error(str(exc))
            starts = torch.arange(args.num_tokens, device=device, dtype=torch.int32)
            offsets = torch.arange(num_candidates, device=device, dtype=torch.int32)
            indices = (starts[:, None] + offsets[None, :]).contiguous()
        elif args.index_pattern == "mixed-c128-swa":
            try:
                _validate_mixed_c128_swa_index_shape(
                    num_tokens=args.num_tokens,
                    num_candidates=num_candidates,
                    compressed_candidates=args.compressed_candidates,
                    kv_tokens=args.kv_tokens,
                )
            except ValueError as exc:
                parser.error(str(exc))
            swa_candidates = num_candidates - args.compressed_candidates
            compressed_indices = torch.randint(
                0,
                args.kv_tokens,
                (args.num_tokens, args.compressed_candidates),
                device=device,
                generator=generator,
                dtype=torch.int32,
            )
            starts = torch.arange(args.num_tokens, device=device, dtype=torch.int32)
            offsets = torch.arange(swa_candidates, device=device, dtype=torch.int32)
            swa_indices = (starts[:, None] + offsets[None, :]).contiguous()
            indices = torch.cat((compressed_indices, swa_indices), dim=1).contiguous()
        else:
            indices = torch.randint(
                0,
                args.kv_tokens,
                (args.num_tokens, num_candidates),
                device=device,
                generator=generator,
                dtype=torch.int32,
            )
        lens = lens_template.fill_(num_candidates)
        scores = torch.empty(
            args.num_tokens,
            args.num_heads,
            num_candidates,
            device=device,
            dtype=score_dtype,
        )
        split_max = torch.empty(args.num_tokens, args.num_heads, device=device, dtype=torch.float32)
        split_denom = torch.empty_like(split_max)
        split_out = torch.empty(
            args.num_tokens,
            args.num_heads,
            args.head_dim,
            device=device,
            dtype=torch.float32,
        )

        num_parts = (
            (num_candidates + args.part_size - 1) // args.part_size
            if num_candidates > args.part_size
            else 1
        )
        partial_max = torch.empty(
            num_parts,
            args.num_tokens,
            args.num_heads,
            device=device,
            dtype=torch.float32,
        )
        partial_denom = torch.empty_like(partial_max)
        partial_acc = torch.empty(
            num_parts,
            args.num_tokens,
            args.num_heads,
            args.head_dim,
            device=device,
            dtype=torch.float32,
        )
        partial_out_max = torch.empty_like(split_max)
        partial_out_denom = torch.empty_like(split_denom)
        partial_out_acc = torch.empty_like(split_out)
        scratch_max = torch.empty_like(split_max)
        scratch_denom = torch.empty_like(split_denom)
        scratch_acc = torch.empty_like(split_out)

        def run_partial() -> None:
            if num_parts == 1:
                accumulate_indexed_sparse_mla_attention_partial_states(
                    q=q,
                    kv_flat=kv_flat,
                    indices=indices,
                    lens=lens,
                    scale=args.scale,
                    part_size=num_candidates,
                    max_score=partial_max,
                    denom=partial_denom,
                    acc=partial_acc,
                )
                partial_out_max.copy_(partial_max[0])
                partial_out_denom.copy_(partial_denom[0])
                partial_out_acc.copy_(partial_acc[0])
                return
            accumulate_indexed_sparse_mla_attention_partial_states(
                q=q,
                kv_flat=kv_flat,
                indices=indices,
                lens=lens,
                scale=args.scale,
                part_size=args.part_size,
                max_score=partial_max,
                denom=partial_denom,
                acc=partial_acc,
            )
            merge_sparse_mla_attention_states(
                partial_max[0],
                partial_denom[0],
                partial_acc[0],
                partial_max[1],
                partial_denom[1],
                partial_acc[1],
                partial_out_max,
                partial_out_denom,
                partial_out_acc,
            )
            current_max = partial_out_max
            current_denom = partial_out_denom
            current_acc = partial_out_acc
            next_max = scratch_max
            next_denom = scratch_denom
            next_acc = scratch_acc
            for part_idx in range(2, num_parts):
                merge_sparse_mla_attention_states(
                    current_max,
                    current_denom,
                    current_acc,
                    partial_max[part_idx],
                    partial_denom[part_idx],
                    partial_acc[part_idx],
                    next_max,
                    next_denom,
                    next_acc,
                )
                current_max, next_max = next_max, current_max
                current_denom, next_denom = next_denom, current_denom
                current_acc, next_acc = next_acc, current_acc
            if current_max is not partial_out_max:
                partial_out_max.copy_(current_max)
                partial_out_denom.copy_(current_denom)
                partial_out_acc.copy_(current_acc)

        score_grid = (
            args.num_tokens,
            triton.cdiv(args.num_heads, args.head_block),
            triton.cdiv(num_candidates, args.block_c),
        )
        stats_grid = (args.num_tokens, args.num_heads)
        value_grid = (
            args.num_tokens,
            triton.cdiv(args.num_heads, args.head_block),
            triton.cdiv(args.head_dim, args.block_d),
        )
        stats_block_c = _next_power_of_2(num_candidates)

        def run_score() -> None:
            _indexed_score_kernel[score_grid](
                q,
                kv_flat,
                indices,
                scores,
                q.stride(0),
                q.stride(1),
                q.stride(2),
                kv_flat.stride(0),
                kv_flat.stride(1),
                indices.stride(0),
                indices.stride(1),
                scores.stride(0),
                scores.stride(1),
                scores.stride(2),
                args.num_tokens,
                args.num_heads,
                num_candidates,
                args.scale,
                HEAD_BLOCK=args.head_block,
                BLOCK_C=args.block_c,
                HEAD_DIM=args.head_dim,
                num_warps=8,
                num_stages=3,
            )

        def run_stats() -> None:
            _indexed_stats_kernel[stats_grid](
                scores,
                split_max,
                split_denom,
                scores.stride(0),
                scores.stride(1),
                scores.stride(2),
                split_max.stride(0),
                split_max.stride(1),
                num_candidates,
                BLOCK_C=stats_block_c,
                num_warps=4,
                num_stages=3,
            )

        def run_value() -> None:
            _indexed_value_kernel[value_grid](
                scores,
                kv_flat,
                indices,
                split_max,
                split_denom,
                split_out,
                scores.stride(0),
                scores.stride(1),
                scores.stride(2),
                kv_flat.stride(0),
                kv_flat.stride(1),
                indices.stride(0),
                indices.stride(1),
                split_max.stride(0),
                split_max.stride(1),
                split_out.stride(0),
                split_out.stride(1),
                split_out.stride(2),
                args.num_heads,
                num_candidates,
                args.head_dim,
                HEAD_BLOCK=args.head_block,
                BLOCK_C=args.block_c,
                BLOCK_D=args.block_d,
                num_warps=4,
                num_stages=3,
            )

        def run_split() -> None:
            run_score()
            run_stats()
            run_value()

        def time_call(fn) -> float:
            torch.cuda.synchronize()
            start = torch.cuda.Event(enable_timing=True)
            end = torch.cuda.Event(enable_timing=True)
            start.record()
            fn()
            end.record()
            torch.cuda.synchronize()
            return float(start.elapsed_time(end))

        for _ in range(args.warmup):
            run_partial()
            run_split()
        torch.cuda.synchronize()

        partial_samples_ms: list[float] = []
        split_samples_ms: list[float] = []
        score_samples_ms: list[float] = []
        stats_samples_ms: list[float] = []
        value_samples_ms: list[float] = []
        for _ in range(args.iterations):
            partial_samples_ms.append(time_call(run_partial))
            score_ms = time_call(run_score)
            stats_ms = time_call(run_stats)
            value_ms = time_call(run_value)
            score_samples_ms.append(score_ms)
            stats_samples_ms.append(stats_ms)
            value_samples_ms.append(value_ms)
            split_samples_ms.append(score_ms + stats_ms + value_ms)

        partial_out = partial_out_acc / partial_out_denom[:, :, None]
        diff = (partial_out - split_out).abs()
        partial_summary = _summarize_ms(partial_samples_ms)
        split_summary = _summarize_ms(split_samples_ms)
        row = {
            "num_candidates": num_candidates,
            "partial": partial_summary,
            "split_total": split_summary,
            "score": _summarize_ms(score_samples_ms),
            "stats": _summarize_ms(stats_samples_ms),
            "value": _summarize_ms(value_samples_ms),
            "partial_mean_ms": partial_summary["mean_ms"],
            "split_total_mean_ms": split_summary["mean_ms"],
            "score_mean_ms": statistics.fmean(score_samples_ms),
            "stats_mean_ms": statistics.fmean(stats_samples_ms),
            "value_mean_ms": statistics.fmean(value_samples_ms),
            "partial_speedup": partial_summary["mean_ms"] / split_summary["mean_ms"],
            "max_abs_diff": float(diff.max().item()),
            "mean_abs_diff": float(diff.mean().item()),
        }
        rows.append(row)
        print(
            "candidates={num_candidates} partial={partial_mean_ms:.3f}ms "
            "split={split_total_mean_ms:.3f}ms "
            "partial_speedup={partial_speedup:.3f}x "
            "score={score_mean_ms:.3f} stats={stats_mean_ms:.3f} "
            "value={value_mean_ms:.3f} max_diff={max_abs_diff:.6f}".format(
                **row
            )
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
        "head_block": args.head_block,
        "block_c": args.block_c,
        "block_d": args.block_d,
        "score_dtype": args.score_dtype,
        "score_workspace_mib": (
            args.num_tokens
            * args.num_heads
            * max(args.candidate_lens)
            * torch.empty((), dtype=score_dtype).element_size()
            / (1024 * 1024)
        ),
        "part_size": args.part_size,
        "index_pattern": args.index_pattern,
        "warmup": args.warmup,
        "iterations": args.iterations,
        "rows": rows,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "indexed_d512_split_microbench.json"
    md_path = args.output_dir / "indexed_d512_split_microbench.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown(md_path, payload)
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
