import types
from pathlib import Path

import pytest

from ds4_harness import b12x_stack_probe


def test_b12x_stack_probe_classifies_public_b12x_without_aiden_apis(monkeypatch):
    versions = {
        "b12x": "0.15.2",
        "flashinfer-python": "0.6.12",
        "flashinfer-cubin": "0.6.12",
        "flashinfer-jit-cache": "0.6.12+cu130",
    }

    def fake_version(name):
        if name not in versions:
            raise b12x_stack_probe.importlib.metadata.PackageNotFoundError
        return versions[name]

    modules = {
        "b12x.integration": types.SimpleNamespace(
            prepare_b12x_w4a16_packed_weights=object()
        ),
        "b12x.integration.mla": types.SimpleNamespace(
            compressed_mla_decode_forward=object(),
            sparse_mla_decode_forward=object(),
            sparse_mla_extend_forward=object(),
        ),
        "b12x.integration.tp_moe": types.SimpleNamespace(
            TPMoEScratchCaps=object(),
            plan_tp_moe_scratch=object(),
            b12x_moe_fp4=object(),
        ),
        "b12x.distributed": types.SimpleNamespace(),
        "flashinfer.fused_moe": types.SimpleNamespace(b12x_fused_moe=object()),
    }

    def fake_import_module(name):
        if name not in modules:
            raise ModuleNotFoundError(name)
        return modules[name]

    monkeypatch.setattr(b12x_stack_probe.importlib.metadata, "version", fake_version)
    monkeypatch.setattr(b12x_stack_probe.importlib, "import_module", fake_import_module)

    result = b12x_stack_probe.probe_b12x_stack()

    assert result["distributions"]["b12x"]["version"] == "0.15.2"
    assert result["routes"]["public_b12x_mla"]["ok"] is True
    assert result["routes"]["aiden_ds4_compressed_mla"]["ok"] is False
    assert result["routes"]["aiden_native_mxfp4_moe"]["ok"] is False
    assert result["routes"]["flashinfer_b12x_moe_nvfp4"]["ok"] is True


def test_b12x_stack_probe_classifies_aiden_bundle_apis(monkeypatch):
    monkeypatch.setattr(
        b12x_stack_probe.importlib.metadata,
        "version",
        lambda name: "local",
    )
    modules = {
        "b12x.integration": types.SimpleNamespace(
            prepare_b12x_fp4_moe_weights=object(),
            prepare_b12x_w4a16_packed_weights=object(),
        ),
        "b12x.integration.mla": types.SimpleNamespace(
            compressed_mla_decode_forward=object(),
            sparse_mla_decode_forward=object(),
            sparse_mla_extend_forward=object(),
        ),
        "b12x.integration.compressed_scratch": types.SimpleNamespace(
            B12XCompressedMLAScratchCaps=object(),
            plan_compressed_mla_scratch=object(),
        ),
        "b12x.integration.compressed_indexer": types.SimpleNamespace(),
        "b12x.integration.sparse_mla_scratch": types.SimpleNamespace(),
        "b12x.integration.tp_moe": types.SimpleNamespace(
            TPMoEScratchCaps=object(),
            plan_tp_moe_scratch=object(),
            b12x_moe_fp4=object(),
        ),
        "b12x.gemm.block_fp8_linear": types.SimpleNamespace(),
        "b12x.distributed": types.SimpleNamespace(PCIeOneshotAllReducePool=object()),
        "flashinfer.fused_moe": types.SimpleNamespace(b12x_fused_moe=object()),
    }
    monkeypatch.setattr(
        b12x_stack_probe.importlib,
        "import_module",
        lambda name: modules[name],
    )

    result = b12x_stack_probe.probe_b12x_stack()

    assert result["routes"]["aiden_ds4_compressed_mla"]["ok"] is True
    assert result["routes"]["aiden_native_mxfp4_moe"]["ok"] is True
    assert result["routes"]["b12x_fp8_linear"]["ok"] is True
    assert result["routes"]["pcie_oneshot_allreduce"]["ok"] is True


def test_b12x_stack_probe_classifies_public_b12x_020_apis(monkeypatch):
    versions = {
        "b12x": "0.20.0",
        "flashinfer-python": "0.6.12",
        "flashinfer-cubin": "0.6.12",
    }

    def fake_version(name):
        if name not in versions:
            raise b12x_stack_probe.importlib.metadata.PackageNotFoundError
        return versions[name]

    modules = {
        "b12x.integration": types.SimpleNamespace(
            prepare_b12x_fp4_moe_weights=object(),
            prepare_b12x_w4a16_packed_weights=object(),
        ),
        "b12x.integration.mla": types.SimpleNamespace(
            compressed_mla_decode_forward=object(),
            sparse_mla_decode_forward=object(),
            sparse_mla_extend_forward=object(),
        ),
        "b12x.integration.compressed_scratch": types.SimpleNamespace(
            B12XCompressedMLAScratchCaps=object(),
            plan_compressed_mla_scratch=object(),
        ),
        "b12x.integration.compressed_indexer": types.SimpleNamespace(
            plan_compressed_indexer_scratch=object(),
        ),
        "b12x.integration.sparse_mla_scratch": types.SimpleNamespace(),
        "b12x.integration.tp_moe": types.SimpleNamespace(
            TPMoEScratchCaps=object(),
            plan_tp_moe_scratch=object(),
            b12x_moe_fp4=object(),
        ),
        "b12x.gemm.block_fp8_linear": types.SimpleNamespace(
            block_fp8_linear_mxfp8=object(),
        ),
        "b12x.distributed": types.SimpleNamespace(PCIeOneshotAllReducePool=object()),
        "flashinfer.fused_moe": types.SimpleNamespace(b12x_fused_moe=object()),
    }

    def fake_import_module(name):
        if name not in modules:
            raise ModuleNotFoundError(name)
        return modules[name]

    monkeypatch.setattr(b12x_stack_probe.importlib.metadata, "version", fake_version)
    monkeypatch.setattr(b12x_stack_probe.importlib, "import_module", fake_import_module)

    result = b12x_stack_probe.probe_b12x_stack()

    assert result["distributions"]["b12x"]["version"] == "0.20.0"
    assert result["routes"]["public_b12x_mla"]["ok"] is True
    assert result["routes"]["aiden_ds4_compressed_mla"]["ok"] is True
    assert result["routes"]["aiden_native_mxfp4_moe"]["ok"] is True
    assert result["routes"]["b12x_fp8_linear"]["ok"] is True
    assert result["routes"]["pcie_oneshot_allreduce"]["ok"] is True


def test_b12x_stack_probe_markdown_records_routes(tmp_path: Path):
    result = {
        "distributions": {"b12x": {"ok": True, "version": "0.15.2"}},
        "modules": {
            "b12x.integration.mla": {
                "ok": True,
                "attributes": {"compressed_mla_decode_forward": True},
            }
        },
        "routes": {
            "aiden_ds4_compressed_mla": {
                "ok": False,
                "note": "missing compressed scratch",
            }
        },
    }
    output = tmp_path / "probe.md"

    b12x_stack_probe.write_b12x_stack_probe_markdown(output, result)

    text = output.read_text(encoding="utf-8")
    assert "# B12X Stack Probe" in text
    assert "`aiden_ds4_compressed_mla`" in text
    assert "missing compressed scratch" in text


def test_b12x_stack_probe_cli_writes_json_and_markdown(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        b12x_stack_probe,
        "probe_b12x_stack",
        lambda: {
            "distributions": {},
            "modules": {},
            "routes": {},
        },
    )
    json_output = tmp_path / "probe.json"
    markdown_output = tmp_path / "probe.md"

    code = b12x_stack_probe.main(
        [
            "--json-output",
            str(json_output),
            "--markdown-output",
            str(markdown_output),
        ]
    )

    assert code == 0
    assert json_output.exists()
    assert markdown_output.exists()


@pytest.mark.parametrize(
    "script_fragment",
    [
        "b12x_stack_probe.json",
        "b12x_stack_probe.md",
        "PYTHON=\"${PYTHON:-python3}\"",
    ],
)
def test_b12x_stack_probe_wrapper(script_fragment):
    script = Path("scripts/run_b12x_stack_probe.sh").read_text(encoding="utf-8")
    assert script_fragment in script
