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
    ModuleProbe("b12x.distributed", ("PCIeOneshotAllReducePool",)),
    ModuleProbe("flashinfer.fused_moe", ("b12x_fused_moe",)),
)


def _module_ok(result: Json, name: str) -> bool:
    module = result["modules"].get(name, {})
    return bool(module.get("ok"))


def _has_attr(result: Json, module_name: str, attr_name: str) -> bool:
    module = result["modules"].get(module_name, {})
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
    routes["b12x_fp8_linear"] = {
        "ok": _module_ok(result, "b12x.gemm.block_fp8_linear"),
        "note": "Needed by unholy B12X FP8 block-scaled linear integration.",
    }
    routes["pcie_oneshot_allreduce"] = {
        "ok": _has_attr(result, "b12x.distributed", "PCIeOneshotAllReducePool"),
        "note": "Needed by unholy's b12x PCIe all-reduce path.",
    }
    routes["flashinfer_b12x_moe_nvfp4"] = {
        "ok": _has_attr(result, "flashinfer.fused_moe", "b12x_fused_moe"),
        "note": "Current upstream NVFP4 FlashInfer B12X MoE path, not native DS4 MXFP4.",
    }
    return routes


def probe_b12x_stack() -> Json:
    result: Json = {
        "case": "b12x_stack_probe",
        "distributions": {
            name: _probe_distribution(name) for name in DISTRIBUTIONS
        },
        "modules": {probe.name: _probe_module(probe) for probe in MODULES},
    }
    result["routes"] = _classify_routes(result)
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
