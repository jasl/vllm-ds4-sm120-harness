"""Probe FlashInfer's packed SM120 sparse-MLA wrapper with vLLM metadata.

The probe is a development-only bridge check. It builds vLLM-style mixed sparse
indices, splits them back into the packed wrapper's main/extra index streams,
and verifies a zero-KV run has the expected LSE. That validates the cache page
shape, slot-id mapping, and length semantics before any endpoint adapter work.
"""

from __future__ import annotations

import argparse
import importlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Json = dict[str, Any]

_DSV4_PACKED_TOKEN_BYTES = 584
_DSV4_MAIN_PAGE_BLOCK_SIZE = 64


@dataclass(frozen=True)
class PackedMLAProbeConfig:
    case: str
    num_tokens: int
    num_heads: int
    window_size: int
    compress_ratio: int
    topk: int
    extra_page_block_size: int
    seed: int
    device: str


CASE_DEFAULTS: dict[str, dict[str, int | str]] = {
    "c4a_prefill": {
        "num_tokens": 128,
        "num_heads": 64,
        "window_size": 128,
        "compress_ratio": 4,
        "topk": 512,
        "extra_page_block_size": 64,
    },
    "c128a_prefill": {
        "num_tokens": 256,
        "num_heads": 64,
        "window_size": 128,
        "compress_ratio": 128,
        "topk": 1024,
        "extra_page_block_size": 2,
    },
}


def _ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def _round_up(value: int, multiple: int) -> int:
    return _ceil_div(value, multiple) * multiple


def prefill_length_rows(
    *,
    num_tokens: int,
    window_size: int,
    compress_ratio: int,
    topk: int,
) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for token_idx in range(num_tokens):
        position = token_idx
        main_len = min(position + 1, window_size)
        extra_len = min((position + 1) // compress_ratio, topk)
        rows.append(
            {
                "token": token_idx,
                "main_len": main_len,
                "extra_len": extra_len,
                "total_len": main_len + extra_len,
            }
        )
    return rows


def summarize_length_rows(rows: list[dict[str, int]]) -> Json:
    if not rows:
        return {
            "num_tokens": 0,
            "main_len_min": 0,
            "main_len_max": 0,
            "extra_len_min": 0,
            "extra_len_max": 0,
            "total_len_min": 0,
            "total_len_max": 0,
        }
    return {
        "num_tokens": len(rows),
        "main_len_min": min(row["main_len"] for row in rows),
        "main_len_max": max(row["main_len"] for row in rows),
        "extra_len_min": min(row["extra_len"] for row in rows),
        "extra_len_max": max(row["extra_len"] for row in rows),
        "total_len_min": min(row["total_len"] for row in rows),
        "total_len_max": max(row["total_len"] for row in rows),
    }


def build_config(
    *,
    case: str,
    num_tokens: int | None = None,
    num_heads: int | None = None,
    window_size: int | None = None,
    compress_ratio: int | None = None,
    topk: int | None = None,
    extra_page_block_size: int | None = None,
    seed: int = 0,
    device: str = "cuda",
) -> PackedMLAProbeConfig:
    if case not in CASE_DEFAULTS:
        raise ValueError(f"unknown case {case!r}; expected one of {sorted(CASE_DEFAULTS)}")
    defaults = CASE_DEFAULTS[case]
    cfg = PackedMLAProbeConfig(
        case=case,
        num_tokens=int(num_tokens if num_tokens is not None else defaults["num_tokens"]),
        num_heads=int(num_heads if num_heads is not None else defaults["num_heads"]),
        window_size=int(
            window_size if window_size is not None else defaults["window_size"]
        ),
        compress_ratio=int(
            compress_ratio
            if compress_ratio is not None
            else defaults["compress_ratio"]
        ),
        topk=int(topk if topk is not None else defaults["topk"]),
        extra_page_block_size=int(
            extra_page_block_size
            if extra_page_block_size is not None
            else defaults["extra_page_block_size"]
        ),
        seed=int(seed),
        device=device,
    )
    validate_config(cfg)
    return cfg


def validate_config(config: PackedMLAProbeConfig) -> None:
    if config.num_tokens <= 64:
        raise ValueError("num_tokens must be >64 so the wrapper uses prefill path")
    if config.num_heads <= 0 or config.num_heads > 128:
        raise ValueError("num_heads must be in the range [1, 128]")
    if config.num_heads not in (16, 32, 64, 128):
        raise ValueError("DSV4 prefill wrapper supports num_heads in {16,32,64,128}")
    if config.window_size <= 0:
        raise ValueError("window_size must be positive")
    if config.compress_ratio <= 1:
        raise ValueError("compress_ratio must be >1 for dual-cache DS4 probe")
    if config.topk <= 0:
        raise ValueError("topk must be positive")
    if config.extra_page_block_size not in (2, 64):
        raise ValueError("extra_page_block_size must be 2 or 64")


def _import_required_modules() -> tuple[Any, Any, Any]:
    torch = importlib.import_module("torch")
    cache_utils = importlib.import_module("vllm.models.deepseek_v4.common.ops")
    sparse_module = importlib.import_module("flashinfer.sparse_mla_sm120")
    wrapper_cls = getattr(sparse_module, "BatchSparseMLAPagedAttentionWrapper")
    return torch, cache_utils, wrapper_cls


def _make_prefill_topk_indices(torch: Any, config: PackedMLAProbeConfig, device: Any):
    indices = torch.full(
        (config.num_tokens, config.topk),
        -1,
        dtype=torch.int32,
        device=device,
    )
    rows = prefill_length_rows(
        num_tokens=config.num_tokens,
        window_size=config.window_size,
        compress_ratio=config.compress_ratio,
        topk=config.topk,
    )
    for row in rows:
        extra_len = row["extra_len"]
        if extra_len > 0:
            indices[row["token"], :extra_len] = torch.arange(
                extra_len, dtype=torch.int32, device=device
            )
    return indices, rows


def _make_block_table(torch: Any, *, num_blocks: int, device: Any):
    return torch.arange(num_blocks, dtype=torch.int32, device=device).view(1, -1)


def run_packed_mla_probe(config: PackedMLAProbeConfig) -> Json:
    torch, cache_utils, wrapper_cls = _import_required_modules()
    device = torch.device(config.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")

    torch.manual_seed(config.seed)
    if device.type == "cuda" and device.index is not None:
        torch.cuda.set_device(device)

    rows = prefill_length_rows(
        num_tokens=config.num_tokens,
        window_size=config.window_size,
        compress_ratio=config.compress_ratio,
        topk=config.topk,
    )
    max_main_len = max(row["main_len"] for row in rows)
    max_extra_len = max(row["extra_len"] for row in rows)

    swa_num_blocks = max(
        1, _ceil_div(config.num_tokens, _DSV4_MAIN_PAGE_BLOCK_SIZE)
    )
    compressed_tokens = max(1, _ceil_div(config.num_tokens, config.compress_ratio))
    extra_num_blocks = max(1, _ceil_div(compressed_tokens, config.extra_page_block_size))

    query_start_loc = torch.tensor([0, config.num_tokens], dtype=torch.int32, device=device)
    seq_lens = torch.tensor([config.num_tokens], dtype=torch.int32, device=device)
    token_to_req_indices = torch.zeros(
        config.num_tokens, dtype=torch.int32, device=device
    )
    decode_swa_indices = torch.empty(
        (0, config.window_size), dtype=torch.int32, device=device
    )
    prefill_topk_indices, rows = _make_prefill_topk_indices(torch, config, device)
    swa_block_table = _make_block_table(
        torch, num_blocks=swa_num_blocks, device=device
    )
    compressed_block_table = _make_block_table(
        torch, num_blocks=extra_num_blocks, device=device
    )

    sparse_indices, sparse_topk_lens = cache_utils.build_flashinfer_mixed_sparse_indices(
        decode_swa_indices,
        None,
        None,
        prefill_topk_indices,
        query_start_loc,
        seq_lens,
        token_to_req_indices,
        swa_block_table,
        _DSV4_MAIN_PAGE_BLOCK_SIZE,
        compressed_block_table,
        config.extra_page_block_size,
        config.window_size,
        config.compress_ratio,
        config.topk,
    )

    main_indices = sparse_indices[:, : config.window_size].contiguous()
    extra_indices = sparse_indices[:, config.window_size :].contiguous()
    main_lens = torch.tensor(
        [row["main_len"] for row in rows], dtype=torch.int32, device=device
    )
    extra_lens = torch.tensor(
        [row["extra_len"] for row in rows], dtype=torch.int32, device=device
    )
    expected_sparse_lens = main_lens + extra_lens
    # vLLM helper reports fixed window width plus compressed length for the
    # official TRTLLM-gen API. The packed wrapper needs true per-cache lengths.
    expected_helper_lens = config.window_size + extra_lens
    helper_lens_match = bool(torch.equal(sparse_topk_lens, expected_helper_lens))

    main_past_len_ok = True
    extra_past_len_ok = True
    for token_idx, row in enumerate(rows):
        if row["main_len"] < main_indices.shape[1]:
            main_past_len_ok = main_past_len_ok and bool(
                (main_indices[token_idx, row["main_len"] :] < 0).all().item()
            )
        if row["extra_len"] < extra_indices.shape[1]:
            extra_past_len_ok = extra_past_len_ok and bool(
                (extra_indices[token_idx, row["extra_len"] :] < 0).all().item()
            )

    q = torch.zeros(
        (config.num_tokens, config.num_heads, 512),
        dtype=torch.bfloat16,
        device=device,
    )
    output = torch.empty_like(q)
    main_cache = torch.zeros(
        (
            swa_num_blocks,
            _DSV4_MAIN_PAGE_BLOCK_SIZE,
            1,
            _DSV4_PACKED_TOKEN_BYTES,
        ),
        dtype=torch.uint8,
        device=device,
    )
    extra_cache = torch.zeros(
        (
            extra_num_blocks,
            config.extra_page_block_size,
            1,
            _DSV4_PACKED_TOKEN_BYTES,
        ),
        dtype=torch.uint8,
        device=device,
    )

    wrapper = wrapper_cls(
        max_num_tokens=config.num_tokens,
        max_num_heads=config.num_heads,
        d_v=512,
        device=device,
    )
    if device.type == "cuda":
        torch.cuda.synchronize()
    start = time.perf_counter()
    lse = wrapper.run(
        q,
        main_cache,
        main_indices,
        output,
        512**-0.5,
        topk_length=main_lens,
        extra_kv_cache=extra_cache,
        extra_indices=extra_indices,
        extra_topk_length=extra_lens,
        return_lse=True,
    )
    if device.type == "cuda":
        torch.cuda.synchronize()
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    expected_lse = torch.log2(expected_sparse_lens.to(torch.float32)).view(-1, 1)
    expected_lse = expected_lse.expand(config.num_tokens, config.num_heads)
    lse_error = (lse - expected_lse).abs()
    result: Json = {
        "ok": bool(
            torch.isfinite(output).all().item()
            and torch.isfinite(lse).all().item()
            and output.abs().max().item() == 0
            and float(lse_error.max().item()) <= 1e-4
            and helper_lens_match
            and main_past_len_ok
            and extra_past_len_ok
        ),
        "case": config.case,
        "config": {
            "num_tokens": config.num_tokens,
            "num_heads": config.num_heads,
            "window_size": config.window_size,
            "compress_ratio": config.compress_ratio,
            "topk": config.topk,
            "extra_page_block_size": config.extra_page_block_size,
            "seed": config.seed,
            "device": str(device),
        },
        "cache": {
            "main_page_block_size": _DSV4_MAIN_PAGE_BLOCK_SIZE,
            "main_num_blocks": swa_num_blocks,
            "extra_page_block_size": config.extra_page_block_size,
            "extra_num_blocks": extra_num_blocks,
            "token_bytes": _DSV4_PACKED_TOKEN_BYTES,
        },
        "lengths": summarize_length_rows(rows),
        "indices": {
            "combined_shape": list(sparse_indices.shape),
            "main_shape": list(main_indices.shape),
            "extra_shape": list(extra_indices.shape),
            "helper_lens_match": helper_lens_match,
            "main_past_len_ok": main_past_len_ok,
            "extra_past_len_ok": extra_past_len_ok,
            "max_main_len": int(max_main_len),
            "max_extra_len": int(max_extra_len),
        },
        "run": {
            "elapsed_ms": elapsed_ms,
            "output_finite": bool(torch.isfinite(output).all().item()),
            "lse_finite": bool(torch.isfinite(lse).all().item()),
            "output_absmax": float(output.abs().max().item()),
            "lse_error_max": float(lse_error.max().item()),
            "lse_mean": float(lse.mean().item()),
        },
    }
    return result


def run_packed_mla_layout_variants(config: PackedMLAProbeConfig) -> list[Json]:
    """Check whether the packed wrapper accepts vLLM-style non-contiguous views.

    The current Aiden/PR3395 wrapper requires dense row-major ``q`` and
    ``indices`` inputs. Keep this probe separate from the main component check
    so a future FlashInfer update can be rechecked without changing serving
    code first.
    """
    torch, cache_utils, wrapper_cls = _import_required_modules()
    device = torch.device(config.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")

    def make_inputs(
        *,
        contiguous_indices: bool,
        q_output_views: bool,
    ) -> tuple[Any, ...]:
        rows = prefill_length_rows(
            num_tokens=config.num_tokens,
            window_size=config.window_size,
            compress_ratio=config.compress_ratio,
            topk=config.topk,
        )
        swa_num_blocks = max(
            1, _ceil_div(config.num_tokens, _DSV4_MAIN_PAGE_BLOCK_SIZE)
        )
        compressed_tokens = max(
            1, _ceil_div(config.num_tokens, config.compress_ratio)
        )
        extra_num_blocks = max(
            1, _ceil_div(compressed_tokens, config.extra_page_block_size)
        )
        query_start_loc = torch.tensor(
            [0, config.num_tokens], dtype=torch.int32, device=device
        )
        seq_lens = torch.tensor(
            [config.num_tokens], dtype=torch.int32, device=device
        )
        token_to_req_indices = torch.zeros(
            config.num_tokens, dtype=torch.int32, device=device
        )
        decode_swa_indices = torch.empty(
            (0, config.window_size), dtype=torch.int32, device=device
        )
        prefill_topk_indices, _ = _make_prefill_topk_indices(
            torch, config, device
        )
        sparse_indices, _ = cache_utils.build_flashinfer_mixed_sparse_indices(
            decode_swa_indices,
            None,
            None,
            prefill_topk_indices,
            query_start_loc,
            seq_lens,
            token_to_req_indices,
            _make_block_table(torch, num_blocks=swa_num_blocks, device=device),
            _DSV4_MAIN_PAGE_BLOCK_SIZE,
            _make_block_table(torch, num_blocks=extra_num_blocks, device=device),
            config.extra_page_block_size,
            config.window_size,
            config.compress_ratio,
            config.topk,
        )
        main_indices = sparse_indices[:, : config.window_size]
        extra_indices = sparse_indices[:, config.window_size :]
        if contiguous_indices:
            main_indices = main_indices.contiguous()
            extra_indices = extra_indices.contiguous()
        main_lens = torch.tensor(
            [row["main_len"] for row in rows], dtype=torch.int32, device=device
        )
        extra_lens = torch.tensor(
            [row["extra_len"] for row in rows], dtype=torch.int32, device=device
        )
        if q_output_views:
            q_storage = torch.zeros(
                (config.num_tokens, config.num_heads + 8, 512),
                dtype=torch.bfloat16,
                device=device,
            )
            output_storage = torch.empty_like(q_storage)
            q = q_storage[:, : config.num_heads]
            output = output_storage[:, : config.num_heads]
        else:
            q = torch.zeros(
                (config.num_tokens, config.num_heads, 512),
                dtype=torch.bfloat16,
                device=device,
            )
            output = torch.empty_like(q)
        main_cache = torch.zeros(
            (
                swa_num_blocks,
                _DSV4_MAIN_PAGE_BLOCK_SIZE,
                1,
                _DSV4_PACKED_TOKEN_BYTES,
            ),
            dtype=torch.uint8,
            device=device,
        )
        extra_cache = torch.zeros(
            (
                extra_num_blocks,
                config.extra_page_block_size,
                1,
                _DSV4_PACKED_TOKEN_BYTES,
            ),
            dtype=torch.uint8,
            device=device,
        )
        expected_lse = torch.log2((main_lens + extra_lens).to(torch.float32))
        expected_lse = expected_lse.view(-1, 1).expand(
            config.num_tokens, config.num_heads
        )
        return (
            q,
            output,
            main_cache,
            extra_cache,
            main_indices,
            extra_indices,
            main_lens,
            extra_lens,
            expected_lse,
        )

    def run_variant(
        *,
        label: str,
        contiguous_indices: bool,
        q_output_views: bool,
    ) -> Json:
        try:
            (
                q,
                output,
                main_cache,
                extra_cache,
                main_indices,
                extra_indices,
                main_lens,
                extra_lens,
                expected_lse,
            ) = make_inputs(
                contiguous_indices=contiguous_indices,
                q_output_views=q_output_views,
            )
            wrapper = wrapper_cls(
                max_num_tokens=config.num_tokens,
                max_num_heads=config.num_heads,
                d_v=512,
                device=device,
            )
            if device.type == "cuda":
                torch.cuda.synchronize()
            start = time.perf_counter()
            lse = wrapper.run(
                q,
                main_cache,
                main_indices,
                output,
                512**-0.5,
                topk_length=main_lens,
                extra_kv_cache=extra_cache,
                extra_indices=extra_indices,
                extra_topk_length=extra_lens,
                return_lse=True,
            )
            if device.type == "cuda":
                torch.cuda.synchronize()
            lse_error = (lse - expected_lse).abs()
            ok = (
                torch.isfinite(output).all().item()
                and torch.isfinite(lse).all().item()
                and float(output.abs().max().item()) == 0.0
                and float(lse_error.max().item()) <= 1e-4
            )
            return {
                "label": label,
                "ok": bool(ok),
                "elapsed_ms": (time.perf_counter() - start) * 1000.0,
                "q_contiguous": bool(q.is_contiguous()),
                "output_contiguous": bool(output.is_contiguous()),
                "main_indices_contiguous": bool(main_indices.is_contiguous()),
                "extra_indices_contiguous": bool(extra_indices.is_contiguous()),
                "lse_error_max": float(lse_error.max().item()),
                "output_absmax": float(output.abs().max().item()),
            }
        except Exception as exc:
            return {
                "label": label,
                "ok": False,
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            }

    return [
        run_variant(
            label="contiguous",
            contiguous_indices=True,
            q_output_views=False,
        ),
        run_variant(
            label="noncontiguous_indices",
            contiguous_indices=False,
            q_output_views=False,
        ),
        run_variant(
            label="noncontiguous_q_output",
            contiguous_indices=True,
            q_output_views=True,
        ),
        run_variant(
            label="noncontiguous_all",
            contiguous_indices=False,
            q_output_views=True,
        ),
    ]


def write_markdown(path: Path, result: Json) -> None:
    cfg = result.get("config", {})
    cache = result.get("cache", {})
    indices = result.get("indices", {})
    run = result.get("run", {})
    lines = [
        "# FlashInfer Packed SM120 Sparse MLA Probe",
        "",
        f"- OK: `{result.get('ok')}`",
        f"- Case: `{result.get('case')}`",
        f"- Tokens / heads: `{cfg.get('num_tokens')}` / `{cfg.get('num_heads')}`",
        f"- Window / compress / topk: `{cfg.get('window_size')}` / "
        f"`{cfg.get('compress_ratio')}` / `{cfg.get('topk')}`",
        f"- Cache page sizes: main `{cache.get('main_page_block_size')}`, "
        f"extra `{cache.get('extra_page_block_size')}`",
        f"- Index shapes: combined `{indices.get('combined_shape')}`, "
        f"main `{indices.get('main_shape')}`, extra `{indices.get('extra_shape')}`",
        f"- Helper lens match: `{indices.get('helper_lens_match')}`",
        f"- Past-length invalid: main `{indices.get('main_past_len_ok')}`, "
        f"extra `{indices.get('extra_past_len_ok')}`",
        f"- Elapsed ms: `{run.get('elapsed_ms')}`",
        f"- Output absmax: `{run.get('output_absmax')}`",
        f"- LSE max error: `{run.get('lse_error_max')}`",
        "",
    ]
    layout_variants = result.get("layout_variants") or []
    if layout_variants:
        lines.extend(
            [
                "## Layout Variants",
                "",
                "| Variant | OK | q | output | main indices | extra indices | Error |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for variant in layout_variants:
            error = variant.get("error") or {}
            lines.append(
                "| `{label}` | `{ok}` | `{q}` | `{out}` | `{main}` | "
                "`{extra}` | `{err}` |".format(
                    label=variant.get("label"),
                    ok=variant.get("ok"),
                    q=variant.get("q_contiguous", "n/a"),
                    out=variant.get("output_contiguous", "n/a"),
                    main=variant.get("main_indices_contiguous", "n/a"),
                    extra=variant.get("extra_indices_contiguous", "n/a"),
                    err=error.get("type", ""),
                )
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASE_DEFAULTS), default="c4a_prefill")
    parser.add_argument("--num-tokens", type=int)
    parser.add_argument("--num-heads", type=int)
    parser.add_argument("--window-size", type=int)
    parser.add_argument("--compress-ratio", type=int)
    parser.add_argument("--topk", type=int)
    parser.add_argument("--extra-page-block-size", type=int)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", default="cuda")
    parser.add_argument(
        "--layout-variants",
        action="store_true",
        help="Also test whether the FlashInfer wrapper accepts non-contiguous views.",
    )
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    config = build_config(
        case=args.case,
        num_tokens=args.num_tokens,
        num_heads=args.num_heads,
        window_size=args.window_size,
        compress_ratio=args.compress_ratio,
        topk=args.topk,
        extra_page_block_size=args.extra_page_block_size,
        seed=args.seed,
        device=args.device,
    )
    try:
        result = run_packed_mla_probe(config)
        if args.layout_variants:
            result["layout_variants"] = run_packed_mla_layout_variants(config)
    except Exception as exc:
        result = {
            "ok": False,
            "case": config.case,
            "config": {
                "num_tokens": config.num_tokens,
                "num_heads": config.num_heads,
                "window_size": config.window_size,
                "compress_ratio": config.compress_ratio,
                "topk": config.topk,
                "extra_page_block_size": config.extra_page_block_size,
                "seed": config.seed,
                "device": config.device,
            },
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }
    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    if args.markdown_output is not None:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(args.markdown_output, result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
