#!/usr/bin/env python3
"""Microbench SM12x sparse MLA indexed accumulate kernels.

This tool isolates the Triton sparse-MLA prefill accumulate path seen in
long-context traces. It intentionally does not start vLLM serve. Run it with
the target vLLM virtualenv Python on an SM120/SM121 host.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VLLM_ROOT = REPO_ROOT / "vllm"


def parse_int_csv(value: str) -> list[int]:
    values: list[int] = []
    for raw in value.split(","):
        raw = raw.strip()
        if not raw:
            continue
        parsed = int(raw)
        if parsed <= 0:
            raise argparse.ArgumentTypeError(f"expected positive integer, got {raw}")
        values.append(parsed)
    if not values:
        raise argparse.ArgumentTypeError("expected at least one positive integer")
    return values


def parse_modes(value: str) -> list[str]:
    modes = [item.strip() for item in value.split(",") if item.strip()]
    valid = {"chunk", "partial", "partial_active"}
    invalid = sorted(set(modes) - valid)
    if invalid:
        raise argparse.ArgumentTypeError(
            "invalid mode(s): {}; expected chunk, partial, or partial_active".format(
                ", ".join(invalid)
            )
        )
    if not modes:
        raise argparse.ArgumentTypeError("expected at least one mode")
    return modes


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (len(ordered) - 1) * q
    lo = int(rank)
    hi = min(lo + 1, len(ordered) - 1)
    weight = rank - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def cuda_device_index(device: str) -> int:
    if device == "cuda":
        return 0
    if device.startswith("cuda:"):
        return int(device.split(":", 1)[1])
    return int(device)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark vLLM sparse MLA indexed accumulate kernels.",
    )
    parser.add_argument(
        "--vllm-root",
        type=Path,
        default=Path(os.environ.get("VLLM_ROOT", DEFAULT_VLLM_ROOT)),
        help="vLLM checkout to import from. Default: repository ./vllm.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory for JSON/CSV/Markdown benchmark artifacts.",
    )
    parser.add_argument(
        "--tokens",
        type=parse_int_csv,
        default=parse_int_csv("512,1024,2048"),
        help="Comma-separated query token counts to sweep.",
    )
    parser.add_argument(
        "--candidates",
        type=parse_int_csv,
        default=parse_int_csv("128,256,512,1152"),
        help="Comma-separated candidate counts to sweep.",
    )
    parser.add_argument("--heads", type=int, default=64)
    parser.add_argument("--head-dim", type=int, default=512)
    parser.add_argument(
        "--kv-rows",
        type=int,
        default=4096,
        help="Rows in the synthetic flattened KV tensor.",
    )
    parser.add_argument(
        "--modes",
        type=parse_modes,
        default=parse_modes("chunk"),
        help="Comma-separated modes: chunk,partial.",
    )
    parser.add_argument(
        "--part-size",
        type=int,
        default=512,
        help="PART_SIZE for partial-state mode.",
    )
    parser.add_argument(
        "--lens-mode",
        choices=("full", "staggered", "endpoint-c128"),
        default="full",
        help=(
            "Use full candidates, generic staggered lengths, or the real-shape "
            "C128A endpoint distribution seen in 124K stats."
        ),
    )
    parser.add_argument("--candidate-offset", type=int, default=0)
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--device", default="cuda")
    parser.add_argument(
        "--emit-nvtx",
        action="store_true",
        help="Wrap each measured kernel call in an NVTX range for Nsys/NCU.",
    )
    return parser


def make_inputs(
    *,
    torch: Any,
    tokens: int,
    heads: int,
    head_dim: int,
    candidates: int,
    kv_rows: int,
    lens_mode: str,
    candidate_offset: int,
    device: str,
) -> dict[str, Any]:
    if kv_rows < candidates + candidate_offset:
        kv_rows = candidates + candidate_offset

    q = torch.randn(
        (tokens, heads, head_dim),
        device=device,
        dtype=torch.bfloat16,
    )
    kv_flat = torch.randn((kv_rows, head_dim), device=device, dtype=torch.bfloat16)

    base = torch.arange(candidates, device=device, dtype=torch.int32)
    token_offsets = (torch.arange(tokens, device=device, dtype=torch.int32) * 17) % (
        max(kv_rows - candidates, 1)
    )
    indices = (token_offsets[:, None] + base[None, :]) % kv_rows
    indices = indices.contiguous()

    if lens_mode == "full":
        lens = torch.full(
            (tokens,),
            candidates + candidate_offset,
            device=device,
            dtype=torch.int32,
        )
    elif lens_mode == "staggered":
        span = torch.arange(tokens, device=device, dtype=torch.int32) % candidates
        lens = candidate_offset + torch.maximum(
            torch.full_like(span, max(candidates // 2, 1)),
            span,
        )
    else:
        min_valid = min(candidates, 128)
        # Matches the measured C128A 124K endpoint shape: combined_topk=1152,
        # lens mean ~=612, max ~=1096, padding ~=0.469.
        max_valid = max(
            min_valid,
            min(candidates, int(round(candidates * 1096 / 1152))),
        )
        span = torch.arange(tokens, device=device, dtype=torch.int32)
        if max_valid > min_valid:
            span = (span * 37) % (max_valid - min_valid + 1)
        else:
            span = torch.zeros_like(span)
        lens = candidate_offset + min_valid + span

    return {
        "q": q,
        "kv_flat": kv_flat,
        "indices": indices,
        "lens": lens.contiguous(),
    }


def run_case(
    *,
    torch: Any,
    kernels: Any,
    mode: str,
    tokens: int,
    heads: int,
    head_dim: int,
    candidates: int,
    kv_rows: int,
    lens_mode: str,
    candidate_offset: int,
    warmups: int,
    repeats: int,
    scale: float,
    part_size: int,
    device: str,
    emit_nvtx: bool,
) -> dict[str, Any]:
    inputs = make_inputs(
        torch=torch,
        tokens=tokens,
        heads=heads,
        head_dim=head_dim,
        candidates=candidates,
        kv_rows=kv_rows,
        lens_mode=lens_mode,
        candidate_offset=candidate_offset,
        device=device,
    )
    lens = inputs["lens"]
    effective_candidates = torch.clamp(
        lens - candidate_offset,
        min=0,
        max=candidates,
    )
    effective_candidate_visits = int(effective_candidates.sum().item()) * heads
    num_parts_for_stats = (candidates + part_size - 1) // part_size
    active_part_rows = 0
    for part_idx in range(num_parts_for_stats):
        part_start = part_idx * part_size
        active_part_rows += int(
            (lens > candidate_offset + part_start).sum().item()
        )
    nominal_part_rows = tokens * num_parts_for_stats
    active_part_row_fraction = (
        active_part_rows / nominal_part_rows if nominal_part_rows else 0.0
    )

    if mode == "chunk":
        max_score = torch.empty((tokens, heads), device=device, dtype=torch.float32)
        denom = torch.empty((tokens, heads), device=device, dtype=torch.float32)
        acc = torch.empty((tokens, heads, head_dim), device=device, dtype=torch.float32)

        def launch() -> None:
            max_score.fill_(float("-inf"))
            denom.zero_()
            acc.zero_()
            kernels.accumulate_indexed_sparse_mla_attention_chunk(
                q=inputs["q"],
                kv_flat=inputs["kv_flat"],
                indices=inputs["indices"],
                lens=inputs["lens"],
                candidate_offset=candidate_offset,
                scale=scale,
                max_score=max_score,
                denom=denom,
                acc=acc,
            )

    elif mode == "partial":
        num_parts = (candidates + part_size - 1) // part_size
        max_score = torch.empty(
            (num_parts, tokens, heads),
            device=device,
            dtype=torch.float32,
        )
        denom = torch.empty_like(max_score)
        acc = torch.empty(
            (num_parts, tokens, heads, head_dim),
            device=device,
            dtype=torch.float32,
        )

        def launch() -> None:
            kernels.accumulate_indexed_sparse_mla_attention_partial_states(
                q=inputs["q"],
                kv_flat=inputs["kv_flat"],
                indices=inputs["indices"],
                lens=inputs["lens"],
                candidate_offset=candidate_offset,
                scale=scale,
                part_size=part_size,
                max_score=max_score,
                denom=denom,
                acc=acc,
            )

    elif mode == "partial_active":
        part_specs = []
        for part_idx in range(num_parts_for_stats):
            part_start = part_idx * part_size
            part_end = min(part_start + part_size, candidates)
            active_tokens = torch.nonzero(
                lens > candidate_offset + part_start,
                as_tuple=False,
            ).flatten()
            if active_tokens.numel() == 0:
                continue
            q_part = inputs["q"].index_select(0, active_tokens).contiguous()
            indices_part = (
                inputs["indices"]
                .index_select(0, active_tokens)[:, part_start:part_end]
                .contiguous()
            )
            lens_part = lens.index_select(0, active_tokens).contiguous()
            active_count = int(active_tokens.numel())
            part_max = torch.empty(
                (1, active_count, heads),
                device=device,
                dtype=torch.float32,
            )
            part_denom = torch.empty_like(part_max)
            part_acc = torch.empty(
                (1, active_count, heads, head_dim),
                device=device,
                dtype=torch.float32,
            )
            part_specs.append(
                (
                    q_part,
                    indices_part,
                    lens_part,
                    candidate_offset + part_start,
                    part_max,
                    part_denom,
                    part_acc,
                )
            )

        def launch() -> None:
            for (
                q_part,
                indices_part,
                lens_part,
                part_candidate_offset,
                part_max,
                part_denom,
                part_acc,
            ) in part_specs:
                kernels.accumulate_indexed_sparse_mla_attention_partial_states(
                    q=q_part,
                    kv_flat=inputs["kv_flat"],
                    indices=indices_part,
                    lens=lens_part,
                    candidate_offset=part_candidate_offset,
                    scale=scale,
                    part_size=part_size,
                    max_score=part_max,
                    denom=part_denom,
                    acc=part_acc,
                )

    else:
        raise AssertionError(f"unsupported mode: {mode}")

    for _ in range(warmups):
        launch()
    torch.cuda.synchronize()

    elapsed_ms: list[float] = []
    for _ in range(repeats):
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        label = (
            f"sparse_mla_accumulate_{mode}_"
            f"t{tokens}_c{candidates}_h{heads}_d{head_dim}"
        )
        if emit_nvtx:
            torch.cuda.nvtx.range_push(label)
        start.record()
        launch()
        end.record()
        end.synchronize()
        if emit_nvtx:
            torch.cuda.nvtx.range_pop()
        elapsed_ms.append(float(start.elapsed_time(end)))

    mean_ms = statistics.fmean(elapsed_ms)
    visits = float(tokens * heads * candidates)
    effective_visits = float(effective_candidate_visits)
    return {
        "mode": mode,
        "tokens": tokens,
        "candidates": candidates,
        "heads": heads,
        "head_dim": head_dim,
        "kv_rows": kv_rows,
        "lens_mode": lens_mode,
        "candidate_offset": candidate_offset,
        "warmups": warmups,
        "repeats": repeats,
        "mean_ms": mean_ms,
        "p50_ms": percentile(elapsed_ms, 0.50),
        "p95_ms": percentile(elapsed_ms, 0.95),
        "min_ms": min(elapsed_ms),
        "max_ms": max(elapsed_ms),
        "token_candidates": tokens * candidates,
        "candidate_visits": int(visits),
        "candidate_visits_per_s": visits / (mean_ms / 1000.0),
        "effective_candidate_visits": effective_candidate_visits,
        "effective_candidate_visits_per_s": effective_visits / (mean_ms / 1000.0),
        "active_part_rows": active_part_rows,
        "nominal_part_rows": nominal_part_rows,
        "active_part_row_fraction": active_part_row_fraction,
        "elapsed_ms": elapsed_ms,
    }


def write_outputs(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "sparse_mla_accumulate_microbench.json"
    csv_path = out_dir / "sparse_mla_accumulate_microbench.csv"
    md_path = out_dir / "sparse_mla_accumulate_microbench.md"

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    fieldnames = [
        "mode",
        "tokens",
        "candidates",
        "heads",
        "head_dim",
        "kv_rows",
        "lens_mode",
        "mean_ms",
        "p50_ms",
        "p95_ms",
        "min_ms",
        "max_ms",
        "candidate_visits_per_s",
        "effective_candidate_visits_per_s",
        "active_part_row_fraction",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in payload["results"]:
            writer.writerow({key: row[key] for key in fieldnames})

    lines = [
        "# Sparse MLA Accumulate Microbench",
        "",
        f"- Device: `{payload['device']['name']}`",
        f"- Torch: `{payload['torch_version']}`",
        f"- vLLM root: `{payload['vllm_root']}`",
        f"- Started at: `{payload['started_at']}`",
        "",
        (
            "| Mode | Tokens | Candidates | Mean ms | P95 ms | "
            "Candidate visits/s | Effective visits/s | Active part rows |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["results"]:
        lines.append(
            "| {mode} | {tokens} | {candidates} | {mean_ms:.3f} | "
            "{p95_ms:.3f} | {candidate_visits_per_s:.3e} | "
            "{effective_candidate_visits_per_s:.3e} | "
            "{active_part_row_fraction:.3f} |".format(**row)
        )
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()
    sys.path.insert(0, str(args.vllm_root))

    import torch
    from vllm.v1.attention.backends.mla import sparse_mla_kernels

    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise SystemExit("CUDA is required for sparse MLA accumulate microbench")
    if args.heads <= 0 or args.head_dim <= 0 or args.kv_rows <= 0:
        raise SystemExit("--heads, --head-dim, and --kv-rows must be positive")
    if args.warmups < 0 or args.repeats <= 0:
        raise SystemExit("--warmups must be >= 0 and --repeats must be > 0")
    if args.part_size <= 0:
        raise SystemExit("--part-size must be positive")

    torch.manual_seed(args.seed)
    if args.device.startswith("cuda"):
        torch.cuda.set_device(cuda_device_index(args.device))

    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    results: list[dict[str, Any]] = []
    for mode in args.modes:
        for tokens in args.tokens:
            for candidates in args.candidates:
                result = run_case(
                    torch=torch,
                    kernels=sparse_mla_kernels,
                    mode=mode,
                    tokens=tokens,
                    heads=args.heads,
                    head_dim=args.head_dim,
                    candidates=candidates,
                    kv_rows=args.kv_rows,
                    lens_mode=args.lens_mode,
                    candidate_offset=args.candidate_offset,
                    warmups=args.warmups,
                    repeats=args.repeats,
                    scale=args.scale,
                    part_size=args.part_size,
                    device=args.device,
                    emit_nvtx=args.emit_nvtx,
                )
                results.append(result)
                print(
                    "{mode} tokens={tokens} candidates={candidates} "
                    "mean_ms={mean_ms:.3f} p95_ms={p95_ms:.3f} "
                    "candidate_visits_per_s={candidate_visits_per_s:.3e}".format(
                        **result
                    ),
                    flush=True,
                )

    device_props: dict[str, Any]
    if args.device.startswith("cuda"):
        props = torch.cuda.get_device_properties(cuda_device_index(args.device))
        device_props = {
            "name": props.name,
            "major": props.major,
            "minor": props.minor,
            "total_memory": props.total_memory,
            "multi_processor_count": props.multi_processor_count,
        }
    else:
        device_props = {"name": args.device}

    payload = {
        "started_at": started_at,
        "command": sys.argv,
        "vllm_root": str(args.vllm_root),
        "torch_version": torch.__version__,
        "device": device_props,
        "results": results,
    }
    write_outputs(args.out_dir, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
