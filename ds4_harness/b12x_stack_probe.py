"""Probe B12X / FlashInfer optional stack capabilities.

The probe is intentionally import-only. It answers which external backend
routes are even available in the target Python environment before an endpoint
A/B run spends time on startup, graph capture, or long-prefill requests.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Json = dict[str, Any]


@dataclass(frozen=True)
class ModuleProbe:
    name: str
    attributes: tuple[str, ...] = ()


DISTRIBUTIONS = (
    "b12x",
    "flashinfer-python",
    "flashinfer-cubin",
    "flashinfer-jit-cache",
    "nvidia-cutlass-dsl",
)

MODULES = (
    ModuleProbe(
        "b12x.integration",
        (
            "prepare_b12x_fp4_moe_weights",
            "prepare_b12x_w4a16_packed_weights",
        ),
    ),
    ModuleProbe(
        "b12x.integration.mla",
        (
            "compressed_mla_decode_forward",
            "sparse_mla_decode_forward",
            "sparse_mla_extend_forward",
        ),
    ),
    ModuleProbe(
        "b12x.integration.compressed_scratch",
        (
            "B12XCompressedMLAScratchCaps",
            "plan_compressed_mla_scratch",
        ),
    ),
    ModuleProbe("b12x.integration.compressed_indexer"),
    ModuleProbe(
        "b12x.integration.indexer",
        (
            "extend_tiled_topk",
            "IndexerExtendMetadata",
        ),
    ),
    ModuleProbe(
        "b12x.attention.indexer",
        (
            "B12XIndexerScratchCaps",
            "INDEXER_SOURCE_LAYOUT_PAGED",
            "PAGED_INDEX_PAGE_SIZE",
            "index_topk_fp8",
            "plan_indexer_scratch",
        ),
    ),
    ModuleProbe("b12x.integration.sparse_mla_scratch"),
    ModuleProbe(
        "b12x.integration.tp_moe",
        (
            "TPMoEScratchCaps",
            "plan_tp_moe_scratch",
            "b12x_moe_fp4",
        ),
    ),
    ModuleProbe("b12x.gemm.block_fp8_linear"),
    ModuleProbe(
        "b12x.gemm.wo_projection",
        (
            "pack_wo_projection_fp8_block_scaled_weights_mxfp8",
            "plan_wo_projection_scratch",
            "wo_projection_inv_rope_mxfp8",
        ),
    ),
    ModuleProbe(
        "b12x.integration.residual",
        (
            "B12XMHCScratchCaps",
            "MHC_DEFAULT_BLOCK_K",
            "MHC_MULT",
            "b12x_mhc_post",
            "b12x_mhc_pre",
            "plan_mhc_scratch",
        ),
    ),
    ModuleProbe("b12x.distributed", ("PCIeOneshotAllReducePool",)),
    ModuleProbe(
        "flashinfer.mla",
        (
            "BatchMLAPagedAttentionWrapper",
            "trtllm_batch_decode_sparse_mla_dsv4",
        ),
    ),
    ModuleProbe(
        "flashinfer.sparse_mla_sm120",
        (
            "BatchSparseMLAPagedAttentionWrapper",
            "sparse_mla_sm120_paged_attention",
        ),
    ),
    ModuleProbe("flashinfer.fused_moe", ("b12x_fused_moe",)),
)

VLLM_MODULES = (
    ModuleProbe(
        "vllm.envs",
        (
            "VLLM_USE_B12X_SPARSE_INDEXER",
            "VLLM_USE_B12X_MOE",
            "VLLM_USE_B12X_MHC",
            "VLLM_USE_B12X_WO_PROJECTION",
        ),
    ),
    ModuleProbe(
        "vllm.models.deepseek_v4.nvidia.b12x",
        (
            "DeepseekV4B12xMLASparseBackend",
            "DeepseekV4B12xMLASparseImpl",
        ),
    ),
    ModuleProbe(
        "vllm.v1.attention.backends.mla.b12x_mla_sparse",
        ("B12xMLASparseBackend", "B12xMLASparseImpl"),
    ),
    ModuleProbe(
        "vllm.models.deepseek_v4.attention",
        ("deepseek_v4_b12x_wo_projection",),
    ),
    ModuleProbe(
        "vllm.models.deepseek_v4.nvidia.model",
        (
            "_deepseek_v4_b12x_mhc_pre_op",
            "_deepseek_v4_b12x_mhc_post_op",
        ),
    ),
    ModuleProbe(
        "vllm.model_executor.layers.sparse_attn_indexer",
        ("_use_b12x_sparse_indexer",),
    ),
    ModuleProbe(
        "vllm.model_executor.layers.fused_moe.b12x_moe",
        ("B12xExperts",),
    ),
    ModuleProbe(
        "vllm.model_executor.layers.fused_moe.oracle.mxfp4",
        ("Mxfp4MoeBackend",),
    ),
    ModuleProbe(
        "vllm.model_executor.layers.fused_moe.experts.flashinfer_b12x_moe",
        ("FlashInferB12xExperts",),
    ),
    ModuleProbe(
        "vllm.models.deepseek_v4.nvidia.flashinfer_sparse",
        ("DeepseekV4FlashInferMLAAttention",),
    ),
    ModuleProbe(
        "vllm.utils.flashinfer",
        ("has_flashinfer_b12x_moe",),
    ),
)

VLLM_FP8_DS_MLA_TOKEN_BYTES = 584
B12X_DSV4_PAYLOAD_BYTES = 576
LAYOUT_PROBE_PAGE_SIZE = 64


def _round_up(value: int, multiple: int) -> int:
    return ((value + multiple - 1) // multiple) * multiple


def _module_ok(result: Json, name: str) -> bool:
    module = result["modules"].get(name, {})
    return bool(module.get("ok"))


def _has_attr(result: Json, module_name: str, attr_name: str) -> bool:
    module = result["modules"].get(module_name, {})
    attrs = module.get("attributes", {})
    return bool(attrs.get(attr_name))


def _vllm_has_attr(result: Json, module_name: str, attr_name: str) -> bool:
    module = result.get("vllm_modules", {}).get(module_name, {})
    attrs = module.get("attributes", {})
    return bool(attrs.get(attr_name))


def _probe_distribution(name: str) -> Json:
    try:
        version = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return {"ok": False, "error": "PackageNotFoundError"}
    except Exception as exc:  # pragma: no cover - defensive for broken metadata.
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)}
    return {"ok": True, "version": version}


def _probe_module(probe: ModuleProbe) -> Json:
    try:
        module = importlib.import_module(probe.name)
    except Exception as exc:
        return {
            "ok": False,
            "error": type(exc).__name__,
            "detail": str(exc),
        }

    attrs = {name: hasattr(module, name) for name in probe.attributes}
    return {
        "ok": True,
        "file": getattr(module, "__file__", None),
        "attributes": attrs,
    }


def _classify_routes(result: Json) -> Json:
    routes: Json = {}
    b12x_layout = result.get("layouts", {}).get("b12x_compressed_mla", {})

    routes["public_b12x_mla"] = {
        "ok": (
            _module_ok(result, "b12x.integration.mla")
            and _has_attr(
                result,
                "b12x.integration.mla",
                "compressed_mla_decode_forward",
            )
        ),
        "note": "Released b12x MLA front door; endpoint parity still requires matching DS4 metadata wiring.",
    }
    routes["aiden_ds4_compressed_mla"] = {
        "ok": (
            _module_ok(result, "b12x.integration.compressed_scratch")
            and _has_attr(
                result,
                "b12x.integration.compressed_scratch",
                "plan_compressed_mla_scratch",
            )
            and _has_attr(
                result,
                "b12x.integration.mla",
                "compressed_mla_decode_forward",
            )
        ),
        "note": "Needed by the DS4-specific compressed MLA adapter; public b12x>=0.20 may satisfy this.",
    }
    routes["aiden_native_mxfp4_moe"] = {
        "ok": (
            _has_attr(
                result,
                "b12x.integration",
                "prepare_b12x_fp4_moe_weights",
            )
            and _has_attr(result, "b12x.integration.tp_moe", "b12x_moe_fp4")
            and _has_attr(
                result,
                "b12x.integration.tp_moe",
                "plan_tp_moe_scratch",
            )
        ),
        "note": "Needed by the native DS4 MXFP4/W4A16 B12X MoE backend; distinct from FlashInfer NVFP4 MoE.",
    }
    routes["public_b12x_sparse_indexer_extend"] = {
        "ok": (
            _has_attr(
                result,
                "b12x.integration.indexer",
                "extend_tiled_topk",
            )
            and _has_attr(
                result,
                "b12x.integration.indexer",
                "IndexerExtendMetadata",
            )
        ),
        "note": (
            "Released b12x sparse-indexer extend top-k API used by the "
            "Aiden/unholy prefill indexer path."
        ),
    }
    routes["public_b12x_paged_indexer"] = {
        "ok": (
            _has_attr(
                result,
                "b12x.attention.indexer",
                "B12XIndexerScratchCaps",
            )
            and _has_attr(
                result,
                "b12x.attention.indexer",
                "INDEXER_SOURCE_LAYOUT_PAGED",
            )
            and _has_attr(
                result,
                "b12x.attention.indexer",
                "PAGED_INDEX_PAGE_SIZE",
            )
            and _has_attr(result, "b12x.attention.indexer", "index_topk_fp8")
            and _has_attr(
                result,
                "b12x.attention.indexer",
                "plan_indexer_scratch",
            )
        ),
        "note": (
            "Current public b12x paged sparse-indexer API used by "
            "black-benediction's B12X indexer planning path."
        ),
    }
    routes["b12x_fp8_linear"] = {
        "ok": _module_ok(result, "b12x.gemm.block_fp8_linear"),
        "note": "Needed by unholy B12X FP8 block-scaled linear integration.",
    }
    routes["aiden_b12x_wo_projection"] = {
        "ok": (
            _has_attr(
                result,
                "b12x.gemm.wo_projection",
                "pack_wo_projection_fp8_block_scaled_weights_mxfp8",
            )
            and _has_attr(
                result,
                "b12x.gemm.wo_projection",
                "plan_wo_projection_scratch",
            )
            and _has_attr(
                result,
                "b12x.gemm.wo_projection",
                "wo_projection_inv_rope_mxfp8",
            )
        ),
        "note": "Needed by Aiden/unholy fused DS4 WO-A/WO-B projection path.",
    }
    routes["aiden_b12x_mhc_residual"] = {
        "ok": (
            _has_attr(
                result,
                "b12x.integration.residual",
                "B12XMHCScratchCaps",
            )
            and _has_attr(
                result,
                "b12x.integration.residual",
                "plan_mhc_scratch",
            )
            and _has_attr(result, "b12x.integration.residual", "b12x_mhc_pre")
            and _has_attr(result, "b12x.integration.residual", "b12x_mhc_post")
        ),
        "note": "Needed by Aiden/unholy B12X mHC pre/post residual mixing path.",
    }
    routes["pcie_oneshot_allreduce"] = {
        "ok": _has_attr(result, "b12x.distributed", "PCIeOneshotAllReducePool"),
        "note": "Needed by unholy's b12x PCIe all-reduce path.",
    }
    routes["flashinfer_b12x_moe_nvfp4"] = {
        "ok": _has_attr(result, "flashinfer.fused_moe", "b12x_fused_moe"),
        "note": "Current upstream NVFP4 FlashInfer B12X MoE path, not native DS4 MXFP4.",
    }
    routes["flashinfer_dsv4_trtllm_gen_plain"] = {
        "ok": _has_attr(
            result,
            "flashinfer.mla",
            "trtllm_batch_decode_sparse_mla_dsv4",
        ),
        "note": (
            "Installed FlashInfer DeepSeek V4 TRTLLM-gen path for plain "
            "BF16/per-tensor-FP8 KV cache; this is not the packed 584B/token "
            "SM120 sparse-MLA PR path."
        ),
    }
    routes["flashinfer_sm120_sparse_mla_packed"] = {
        "ok": (
            _has_attr(
                result,
                "flashinfer.sparse_mla_sm120",
                "sparse_mla_sm120_paged_attention",
            )
            and _has_attr(
                result,
                "flashinfer.sparse_mla_sm120",
                "BatchSparseMLAPagedAttentionWrapper",
            )
        ),
        "note": (
            "FlashInfer PR3395-style packed SM120 sparse MLA path. This is the "
            "candidate that can consume DS4 584B/token packed KV and should be "
            "validated with a direct component smoke before any vLLM adapter."
        ),
    }
    routes["public_b12x_vllm_fp8_ds_mla_zero_copy"] = {
        "ok": (
            routes["public_b12x_mla"]["ok"]
            and bool(b12x_layout.get("vllm_zero_copy_compatible"))
        ),
        "note": (
            "Whether public b12x compressed-MLA can consume current vLLM "
            "fp8_ds_mla cache without repack by using a 2D page-byte view of "
            "the physical cache pages."
        ),
    }
    return routes


def _classify_runtime_routes(result: Json) -> Json:
    runtime_routes: Json = {}

    runtime_routes["runtime_ds4_b12x_compressed_mla_adapter"] = {
        "ok": (
            _vllm_has_attr(
                result,
                "vllm.models.deepseek_v4.nvidia.b12x",
                "DeepseekV4B12xMLASparseBackend",
            )
            or _vllm_has_attr(
                result,
                "vllm.models.deepseek_v4.nvidia.b12x",
                "DeepseekV4B12xMLASparseImpl",
            )
        ),
        "note": "vLLM runtime exposes a DS4-specific B12X compressed-MLA adapter.",
    }
    runtime_routes["runtime_v32_b12x_mla_sparse"] = {
        "ok": (
            _vllm_has_attr(
                result,
                "vllm.v1.attention.backends.mla.b12x_mla_sparse",
                "B12xMLASparseBackend",
            )
            or _vllm_has_attr(
                result,
                "vllm.v1.attention.backends.mla.b12x_mla_sparse",
                "B12xMLASparseImpl",
            )
        ),
        "note": "vLLM runtime exposes the non-DS4 B12X MLA sparse backend.",
    }
    runtime_routes["runtime_ds4_b12x_wo_projection"] = {
        "ok": (
            _vllm_has_attr(
                result,
                "vllm.envs",
                "VLLM_USE_B12X_WO_PROJECTION",
            )
            and _vllm_has_attr(
                result,
                "vllm.models.deepseek_v4.attention",
                "deepseek_v4_b12x_wo_projection",
            )
        ),
        "note": "vLLM runtime exposes the DS4 B12X WO projection switch and op.",
    }
    runtime_routes["runtime_ds4_b12x_mhc"] = {
        "ok": (
            _vllm_has_attr(result, "vllm.envs", "VLLM_USE_B12X_MHC")
            and _vllm_has_attr(
                result,
                "vllm.models.deepseek_v4.nvidia.model",
                "_deepseek_v4_b12x_mhc_pre_op",
            )
            and _vllm_has_attr(
                result,
                "vllm.models.deepseek_v4.nvidia.model",
                "_deepseek_v4_b12x_mhc_post_op",
            )
        ),
        "note": "vLLM runtime exposes the DS4 B12X mHC switch and custom ops.",
    }
    runtime_routes["runtime_b12x_sparse_indexer"] = {
        "ok": _vllm_has_attr(
            result,
            "vllm.model_executor.layers.sparse_attn_indexer",
            "_use_b12x_sparse_indexer",
        ),
        "note": "vLLM runtime exposes the B12X sparse indexer selection hook.",
    }
    runtime_routes["runtime_native_mxfp4_b12x_moe"] = {
        "ok": (
            _vllm_has_attr(
                result,
                "vllm.model_executor.layers.fused_moe.b12x_moe",
                "B12xExperts",
            )
            and _vllm_has_attr(
                result,
                "vllm.model_executor.layers.fused_moe.oracle.mxfp4",
                "Mxfp4MoeBackend",
            )
        ),
        "note": "vLLM runtime exposes native B12X MXFP4 MoE plumbing.",
    }
    runtime_routes["runtime_flashinfer_b12x_moe"] = {
        "ok": _vllm_has_attr(
            result,
            "vllm.model_executor.layers.fused_moe.experts.flashinfer_b12x_moe",
            "FlashInferB12xExperts",
        ),
        "note": "vLLM runtime exposes the upstream FlashInfer B12X MoE path.",
    }
    runtime_routes["runtime_flashinfer_mla_sparse_dsv4_plain"] = {
        "ok": _vllm_has_attr(
            result,
            "vllm.models.deepseek_v4.nvidia.flashinfer_sparse",
            "DeepseekV4FlashInferMLAAttention",
        ),
        "note": (
            "vLLM runtime exposes the explicit FLASHINFER_MLA_SPARSE_DSV4 "
            "backend, which currently uses FlashInfer's plain BF16/per-tensor "
            "FP8 KV-cache route rather than PR3395 packed 584B/token SM120 MLA."
        ),
    }
    return runtime_routes


def _probe_b12x_compressed_mla_layout() -> Json:
    try:
        module = importlib.import_module(
            "b12x.attention.mla.compressed_reference"
        )
    except Exception as exc:
        return {
            "ok": False,
            "error": type(exc).__name__,
            "detail": str(exc),
        }

    try:
        page_nbytes = int(module.compressed_mla_page_nbytes(LAYOUT_PROBE_PAGE_SIZE))
        scale_offset = int(
            module.compressed_mla_scale_region_offset(LAYOUT_PROBE_PAGE_SIZE)
        )
    except Exception as exc:
        return {
            "ok": False,
            "error": type(exc).__name__,
            "detail": str(exc),
        }

    vllm_unpadded_page_nbytes = (
        LAYOUT_PROBE_PAGE_SIZE * VLLM_FP8_DS_MLA_TOKEN_BYTES
    )
    vllm_page_nbytes = _round_up(
        vllm_unpadded_page_nbytes,
        B12X_DSV4_PAYLOAD_BYTES,
    )
    b12x_token0_scale_offset = scale_offset
    b12x_token1_payload_offset = B12X_DSV4_PAYLOAD_BYTES
    vllm_page_view_scale_region_offset = (
        LAYOUT_PROBE_PAGE_SIZE * B12X_DSV4_PAYLOAD_BYTES
    )
    vllm_page_view_token1_payload_offset = B12X_DSV4_PAYLOAD_BYTES
    compatible = (
        page_nbytes == vllm_page_nbytes
        and b12x_token0_scale_offset == vllm_page_view_scale_region_offset
        and b12x_token1_payload_offset == vllm_page_view_token1_payload_offset
    )
    reason = (
        "vLLM physical page layout matches b12x via a 2D page-byte view"
        if compatible
        else (
            "b12x page-packed layout does not match the current vLLM "
            "physical fp8_ds_mla page layout"
        )
    )

    return {
        "ok": True,
        "page_size": LAYOUT_PROBE_PAGE_SIZE,
        "b12x_page_nbytes": page_nbytes,
        "b12x_scale_region_offset": scale_offset,
        "b12x_token0_scale_offset": b12x_token0_scale_offset,
        "b12x_token1_payload_offset": b12x_token1_payload_offset,
        "vllm_unpadded_page_nbytes": vllm_unpadded_page_nbytes,
        "vllm_page_nbytes": vllm_page_nbytes,
        "vllm_padded_page_nbytes": vllm_page_nbytes,
        "vllm_3d_token_stride": VLLM_FP8_DS_MLA_TOKEN_BYTES,
        "vllm_physical_payload_stride": B12X_DSV4_PAYLOAD_BYTES,
        "vllm_page_view_required": True,
        "vllm_page_view_zero_copy": compatible,
        "vllm_page_view_scale_region_offset": vllm_page_view_scale_region_offset,
        "vllm_page_view_token1_payload_offset": (
            vllm_page_view_token1_payload_offset
        ),
        "vllm_zero_copy_compatible": compatible,
        "reason": reason,
    }


def probe_b12x_stack() -> Json:
    result: Json = {
        "case": "b12x_stack_probe",
        "distributions": {
            name: _probe_distribution(name) for name in DISTRIBUTIONS
        },
        "modules": {probe.name: _probe_module(probe) for probe in MODULES},
        "vllm_modules": {
            probe.name: _probe_module(probe) for probe in VLLM_MODULES
        },
    }
    result["layouts"] = {
        "b12x_compressed_mla": _probe_b12x_compressed_mla_layout(),
    }
    result["routes"] = _classify_routes(result)
    result["runtime_routes"] = _classify_runtime_routes(result)
    return result


def write_b12x_stack_probe_markdown(path: Path, result: Json) -> None:
    lines = [
        "# B12X Stack Probe",
        "",
        "## Distributions",
        "",
        "| package | available | version / error |",
        "| --- | --- | --- |",
    ]
    for name, row in result["distributions"].items():
        value = row.get("version") if row.get("ok") else row.get("error", "missing")
        lines.append(f"| `{name}` | `{bool(row.get('ok'))}` | `{value}` |")

    lines.extend(
        [
            "",
            "## Modules",
            "",
            "| module | import | attributes |",
            "| --- | --- | --- |",
        ]
    )
    for name, row in result["modules"].items():
        attrs = row.get("attributes", {})
        attr_text = ", ".join(
            f"{key}={value}" for key, value in attrs.items()
        ) or "-"
        status = "ok" if row.get("ok") else row.get("error", "fail")
        lines.append(f"| `{name}` | `{status}` | `{attr_text}` |")

    if "vllm_modules" in result:
        lines.extend(
            [
                "",
                "## vLLM Runtime Modules",
                "",
                "| module | import | attributes |",
                "| --- | --- | --- |",
            ]
        )
        for name, row in result["vllm_modules"].items():
            attrs = row.get("attributes", {})
            attr_text = ", ".join(
                f"{key}={value}" for key, value in attrs.items()
            ) or "-"
            status = "ok" if row.get("ok") else row.get("error", "fail")
            lines.append(f"| `{name}` | `{status}` | `{attr_text}` |")

    lines.extend(
        [
            "",
            "## Layout Compatibility",
            "",
            "| layout | probe | vLLM zero-copy compatible | reason |",
            "| --- | --- | --- | --- |",
        ]
    )
    for name, row in result.get("layouts", {}).items():
        status = "ok" if row.get("ok") else row.get("error", "fail")
        lines.append(
            f"| `{name}` | `{status}` | "
            f"`{bool(row.get('vllm_zero_copy_compatible'))}` | "
            f"{row.get('reason', row.get('detail', ''))} |"
        )

    lines.extend(
        [
            "",
            "## Route Readiness",
            "",
            "| route | ready | note |",
            "| --- | --- | --- |",
        ]
    )
    for name, row in result["routes"].items():
        lines.append(
            f"| `{name}` | `{bool(row.get('ok'))}` | {row.get('note', '')} |"
        )

    if "runtime_routes" in result:
        lines.extend(
            [
                "",
                "## vLLM Runtime Route Readiness",
                "",
                "| route | ready | note |",
                "| --- | --- | --- |",
            ]
        )
        for name, row in result["runtime_routes"].items():
            lines.append(
                f"| `{name}` | `{bool(row.get('ok'))}` | "
                f"{row.get('note', '')} |"
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args(argv)

    result = probe_b12x_stack()
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
        write_b12x_stack_probe_markdown(args.markdown_output, result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
