#!/usr/bin/env python3
"""Compare official b12x MLA kernels with the current SM12x sparse-MLA paths.

This is a diagnostic microbench, not a promotion gate.  It answers a narrow
question before writing a vLLM endpoint adapter: does the installable
FlashInfer/b12x MLA route beat the current development sparse-MLA building
blocks on endpoint-like C128/SWA shapes?

The comparisons intentionally separate three paths:

1. b12x compressed MLA over packed SWA + indexed compressed KV pages;
2. vLLM's older online packed sparse-MLA helper over the same packed pages;
3. vLLM's current indexed-D512 split + finish helper over gathered BF16 KV.

Path 3 is not numerically compared with the packed-page paths because it starts
after gather/dequant.  It is included because it is the relevant current Dev
baseline for score/stats/value work.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ShapeSpec:
    name: str
    rows: int
    swa_width: int
    indexed_width: int

    @property
    def total_width(self) -> int:
        return self.swa_width + self.indexed_width


def _parse_shape_specs(value: str) -> list[ShapeSpec]:
    specs: list[ShapeSpec] = []
    for raw_item in value.split(","):
        item = raw_item.strip()
        if not item:
            continue
        parts = item.split(":")
        if len(parts) != 4:
            raise argparse.ArgumentTypeError(
                "shape specs must be name:rows:swa_width:indexed_width"
            )
        name, rows_s, swa_s, indexed_s = parts
        if not name:
            raise argparse.ArgumentTypeError("shape name must be non-empty")
        try:
            rows = int(rows_s)
            swa_width = int(swa_s)
            indexed_width = int(indexed_s)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(str(exc)) from exc
        if rows <= 0 or swa_width <= 0 or indexed_width < 0:
            raise argparse.ArgumentTypeError(
                "rows and swa_width must be positive; indexed_width must be >= 0"
            )
        specs.append(ShapeSpec(name, rows, swa_width, indexed_width))
    if not specs:
        raise argparse.ArgumentTypeError("expected at least one shape spec")
    return specs


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
        "# SM12x b12x MLA microbench",
        "",
        f"- device: `{payload['device_name']}`",
        f"- compute_capability: `{payload['compute_capability']}`",
        f"- heads / head_dim: `{payload['num_heads']} / {payload['head_dim']}`",
        f"- warmup / iterations: `{payload['warmup']} / {payload['iterations']}`",
        "",
        (
            "| shape | rows | SWA | indexed | b12x ms | vLLM online packed ms | "
            "online speedup | vLLM D512 split+finish ms | b12x-online max diff |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            (
                "| {name} | {rows} | {swa_width} | {indexed_width} | "
                "{b12x_mean_ms:.3f} | {vllm_online_mean_ms:.3f} | "
                "{b12x_speedup_vs_vllm_online:.3f}x | "
                "{vllm_d512_split_finish_mean_ms:.3f} | {max_abs_diff:.6f} |"
            ).format(**row)
        )
    lines.append("")
    lines.extend(
        [
            "Notes:",
            "",
            "- b12x and vLLM online packed paths read the same synthetic packed KV pages.",
            "- D512 split+finish starts from gathered BF16 KV, so it is a timing",
            "  reference for current Dev score/stats/value work rather than a direct",
            "  numerical comparison with packed-page paths.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _time_cuda(fn, *, warmup: int, iterations: int) -> dict[str, float]:
    import torch

    for _ in range(warmup):
        fn()
    torch.cuda.synchronize()
    samples: list[float] = []
    for _ in range(iterations):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        fn()
        end.record()
        torch.cuda.synchronize()
        samples.append(float(start.elapsed_time(end)))
    return _summarize_ms(samples)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare b12x compressed MLA with current SM12x sparse-MLA helpers."
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--shape-specs",
        type=_parse_shape_specs,
        default="tiny:32:128:128,real_c128:256:1024:128",
    )
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--gpu-id", type=int, default=0)
    args = parser.parse_args()

    if args.warmup < 0 or args.iterations <= 0:
        parser.error("--warmup must be >= 0 and --iterations must be > 0")

    try:
        import torch
    except ImportError as exc:
        print(f"torch import failed: {exc}", file=sys.stderr)
        return 2

    if not torch.cuda.is_available():
        print("CUDA is not available", file=sys.stderr)
        return 2

    try:
        from b12x.attention.mla.compressed_reference import (
            pack_compressed_mla_kv_cache_reference,
        )
        from b12x.integration.mla import (
            B12XAttentionWorkspace,
            COMPRESSED_MLA_C128_PAGE_SIZE,
            COMPRESSED_MLA_HEAD_DIM,
            COMPRESSED_MLA_LOCAL_Q_HEADS_TP2,
            COMPRESSED_MLA_SWA_PAGE_SIZE,
            compressed_mla_decode_forward,
        )
        from vllm.v1.attention.backends.mla.sparse_mla_kernels import (
            accumulate_indexed_d512_split_sparse_mla_attention,
            finish_gathered_sparse_mla_attention,
            fp8ds_global_paged_sparse_mla_attention_with_sink_multihead,
        )
    except ImportError as exc:
        print(f"required b12x/vLLM imports failed: {exc}", file=sys.stderr)
        return 2

    torch.cuda.set_device(args.gpu_id)
    device = torch.device(f"cuda:{args.gpu_id}")
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    num_heads = int(COMPRESSED_MLA_LOCAL_Q_HEADS_TP2)
    head_dim = int(COMPRESSED_MLA_HEAD_DIM)
    scale = 1.0 / math.sqrt(head_dim)
    rows_out: list[dict[str, Any]] = []

    for spec in args.shape_specs:
        torch.manual_seed(args.seed + spec.rows + spec.swa_width + spec.indexed_width)
        swa_tokens = spec.swa_width
        indexed_tokens = max(spec.indexed_width * 2, 1)
        q = torch.randn(
            (spec.rows, num_heads, head_dim),
            device=device,
            dtype=torch.bfloat16,
        ) / math.sqrt(head_dim)
        swa_nope = torch.randn((swa_tokens, 448), device=device, dtype=torch.bfloat16)
        swa_rope = torch.randn((swa_tokens, 64), device=device, dtype=torch.bfloat16)
        indexed_nope = torch.randn(
            (indexed_tokens, 448), device=device, dtype=torch.bfloat16
        )
        indexed_rope = torch.randn(
            (indexed_tokens, 64), device=device, dtype=torch.bfloat16
        )
        swa_cache = pack_compressed_mla_kv_cache_reference(
            swa_nope,
            swa_rope,
            page_size=COMPRESSED_MLA_SWA_PAGE_SIZE,
        )
        indexed_cache = pack_compressed_mla_kv_cache_reference(
            indexed_nope,
            indexed_rope,
            page_size=COMPRESSED_MLA_C128_PAGE_SIZE,
        )
        swa_indices = torch.arange(
            spec.swa_width,
            device=device,
            dtype=torch.int32,
        ).repeat(spec.rows, 1)
        swa_lens = torch.full(
            (spec.rows,), spec.swa_width, device=device, dtype=torch.int32
        )
        if spec.indexed_width > 0:
            indexed_indices = (
                torch.arange(spec.indexed_width, device=device, dtype=torch.int32)[
                    None, :
                ]
                + torch.arange(spec.rows, device=device, dtype=torch.int32)[:, None]
            ) % indexed_tokens
        else:
            indexed_indices = torch.empty(
                (spec.rows, 0), device=device, dtype=torch.int32
            )
        indexed_lens = torch.full(
            (spec.rows,), spec.indexed_width, device=device, dtype=torch.int32
        )
        workspace = B12XAttentionWorkspace.for_contract(
            mode="decode",
            device=device,
            dtype=torch.bfloat16,
            kv_dtype=torch.uint8,
            num_q_heads=num_heads,
            head_dim=head_dim,
            v_head_dim=head_dim,
            topk=spec.total_width,
            max_total_q=spec.rows,
            max_batch=spec.rows,
            max_page_table_width=spec.total_width,
            max_paged_q_rows=spec.rows,
            max_kv_rows=max(swa_tokens, indexed_tokens),
            page_size=COMPRESSED_MLA_SWA_PAGE_SIZE,
            use_cuda_graph=False,
            max_chunks_per_row=64,
        )

        def run_b12x():
            return compressed_mla_decode_forward(
                q_all=q,
                swa_k_cache=swa_cache,
                swa_indices=swa_indices,
                swa_topk_lengths=swa_lens,
                workspace=workspace,
                sm_scale=scale,
                indexed_k_cache=indexed_cache,
                indexed_indices=indexed_indices,
                indexed_topk_lengths=indexed_lens,
                indexed_page_size=COMPRESSED_MLA_C128_PAGE_SIZE,
            )

        seq_lens = torch.full(
            (spec.rows,), spec.swa_width, device=device, dtype=torch.int32
        )
        gather_lens = torch.full_like(seq_lens, spec.swa_width)
        num_swa_blocks = max(
            (spec.swa_width + COMPRESSED_MLA_SWA_PAGE_SIZE - 1)
            // COMPRESSED_MLA_SWA_PAGE_SIZE,
            1,
        )
        block_table = torch.arange(
            num_swa_blocks, device=device, dtype=torch.int32
        ).repeat(spec.rows, 1)
        attn_sink = torch.full(
            (num_heads,), -float("inf"), device=device, dtype=torch.float32
        )
        vllm_online_output = torch.empty(
            (spec.rows, num_heads, head_dim), device=device, dtype=torch.bfloat16
        )

        def run_vllm_online():
            fp8ds_global_paged_sparse_mla_attention_with_sink_multihead(
                q,
                indexed_cache,
                indexed_indices,
                indexed_lens,
                COMPRESSED_MLA_C128_PAGE_SIZE,
                swa_cache,
                seq_lens,
                gather_lens,
                block_table,
                COMPRESSED_MLA_SWA_PAGE_SIZE,
                spec.indexed_width,
                spec.swa_width,
                scale,
                attn_sink,
                vllm_online_output,
                head_block_size=1,
                num_heads=num_heads,
            )
            return vllm_online_output

        kv_tokens = max(spec.total_width * 2, 1)
        kv_flat = torch.randn(
            (kv_tokens, head_dim), device=device, dtype=torch.bfloat16
        )
        d512_indices = (
            torch.arange(spec.total_width, device=device, dtype=torch.int64)[None, :]
            + torch.arange(spec.rows, device=device, dtype=torch.int64)[:, None]
        ) % kv_tokens
        d512_indices = d512_indices.to(torch.int32)
        d512_lens = torch.full(
            (spec.rows,), spec.total_width, device=device, dtype=torch.int32
        )
        scores = torch.empty(
            (spec.rows, num_heads, spec.total_width),
            device=device,
            dtype=torch.float32,
        )
        max_score = torch.empty((spec.rows, num_heads), device=device, dtype=torch.float32)
        denom = torch.empty_like(max_score)
        acc = torch.empty((spec.rows, num_heads, head_dim), device=device, dtype=torch.float32)
        d512_output = torch.empty_like(acc)
        d512_lse = torch.empty_like(max_score)

        def run_d512_split_finish():
            accumulate_indexed_d512_split_sparse_mla_attention(
                q,
                kv_flat,
                d512_indices,
                d512_lens,
                scale,
                scores,
                max_score,
                denom,
                acc,
            )
            finish_gathered_sparse_mla_attention(
                max_score,
                denom,
                acc,
                d512_output,
                d512_lse,
            )
            return d512_output

        # Compile before measuring and keep a numerical smoke for packed paths.
        compile_start = time.perf_counter()
        b12x_output = run_b12x()
        vllm_online = run_vllm_online()
        run_d512_split_finish()
        torch.cuda.synchronize()
        compile_elapsed_s = time.perf_counter() - compile_start
        max_abs_diff = float((b12x_output.float() - vllm_online.float()).abs().max())

        b12x_stats = _time_cuda(run_b12x, warmup=args.warmup, iterations=args.iterations)
        online_stats = _time_cuda(
            run_vllm_online,
            warmup=args.warmup,
            iterations=args.iterations,
        )
        d512_stats = _time_cuda(
            run_d512_split_finish,
            warmup=args.warmup,
            iterations=args.iterations,
        )

        b12x_mean = b12x_stats["mean_ms"]
        online_mean = online_stats["mean_ms"]
        d512_mean = d512_stats["mean_ms"]
        rows_out.append(
            {
                "name": spec.name,
                "rows": spec.rows,
                "swa_width": spec.swa_width,
                "indexed_width": spec.indexed_width,
                "total_width": spec.total_width,
                "compile_elapsed_s": compile_elapsed_s,
                "max_abs_diff": max_abs_diff,
                "b12x_mean_ms": b12x_mean,
                "b12x_stats": b12x_stats,
                "vllm_online_mean_ms": online_mean,
                "vllm_online_stats": online_stats,
                "vllm_d512_split_finish_mean_ms": d512_mean,
                "vllm_d512_split_finish_stats": d512_stats,
                "b12x_speedup_vs_vllm_online": (
                    online_mean / b12x_mean if b12x_mean > 0 else float("nan")
                ),
                "b12x_ratio_vs_d512_split_finish": (
                    b12x_mean / d512_mean if d512_mean > 0 else float("nan")
                ),
                "d512_scores_workspace_mib": (
                    scores.numel() * scores.element_size() / 1024 / 1024
                ),
            }
        )

    props = torch.cuda.get_device_properties(device)
    payload = {
        "device_name": props.name,
        "compute_capability": f"{props.major}.{props.minor}",
        "num_heads": num_heads,
        "head_dim": head_dim,
        "warmup": args.warmup,
        "iterations": args.iterations,
        "seed": args.seed,
        "rows": rows_out,
    }
    json_path = args.output_dir / "b12x_mla_microbench.json"
    md_path = args.output_dir / "b12x_mla_microbench.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    _write_markdown(md_path, payload)
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
