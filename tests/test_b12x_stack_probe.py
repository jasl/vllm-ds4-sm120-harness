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
        "b12x.integration.indexer": types.SimpleNamespace(
            extend_tiled_topk=object(),
            IndexerExtendMetadata=object(),
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
        "b12x.gemm.wo_projection": types.SimpleNamespace(
            pack_wo_projection_fp8_block_scaled_weights_mxfp8=object(),
            plan_wo_projection_scratch=object(),
            wo_projection_inv_rope_mxfp8=object(),
        ),
        "b12x.integration.residual": types.SimpleNamespace(
            B12XMHCScratchCaps=object(),
            MHC_DEFAULT_BLOCK_K=object(),
            MHC_MULT=object(),
            b12x_mhc_post=object(),
            b12x_mhc_pre=object(),
            plan_mhc_scratch=object(),
        ),
        "b12x.distributed": types.SimpleNamespace(PCIeOneshotAllReducePool=object()),
        "b12x.attention.mla.compressed_reference": types.SimpleNamespace(
            compressed_mla_page_nbytes=lambda page_size: 37440
            if page_size == 64
            else page_size * 584,
            compressed_mla_scale_region_offset=lambda page_size: page_size * 576,
        ),
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
    assert result["routes"]["public_b12x_sparse_indexer_extend"]["ok"] is True
    assert result["routes"]["b12x_fp8_linear"]["ok"] is True
    assert result["routes"]["aiden_b12x_wo_projection"]["ok"] is True
    assert result["routes"]["aiden_b12x_mhc_residual"]["ok"] is True
    assert result["routes"]["pcie_oneshot_allreduce"]["ok"] is True
    assert result["layouts"]["b12x_compressed_mla"]["ok"] is True
    assert result["layouts"]["b12x_compressed_mla"]["vllm_zero_copy_compatible"] is False
    assert result["routes"]["public_b12x_vllm_fp8_ds_mla_zero_copy"]["ok"] is False


def test_b12x_stack_probe_classifies_aiden_runtime_paths(monkeypatch):
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
        ),
        "b12x.integration.compressed_scratch": types.SimpleNamespace(
            plan_compressed_mla_scratch=object(),
        ),
        "b12x.integration.tp_moe": types.SimpleNamespace(
            plan_tp_moe_scratch=object(),
            b12x_moe_fp4=object(),
        ),
        "vllm.envs": types.SimpleNamespace(
            VLLM_USE_B12X_SPARSE_INDEXER=False,
            VLLM_USE_B12X_MOE=False,
            VLLM_USE_B12X_MHC=False,
            VLLM_USE_B12X_WO_PROJECTION=False,
        ),
        "vllm.models.deepseek_v4.attention": types.SimpleNamespace(
            deepseek_v4_b12x_wo_projection=object(),
        ),
        "vllm.models.deepseek_v4.nvidia.model": types.SimpleNamespace(
            _deepseek_v4_b12x_mhc_pre_op=object(),
            _deepseek_v4_b12x_mhc_post_op=object(),
        ),
        "vllm.model_executor.layers.sparse_attn_indexer": types.SimpleNamespace(
            _use_b12x_sparse_indexer=lambda: True,
        ),
        "vllm.model_executor.layers.fused_moe.b12x_moe": types.SimpleNamespace(
            B12xExperts=object(),
        ),
        "vllm.model_executor.layers.fused_moe.oracle.mxfp4": types.SimpleNamespace(
            Mxfp4MoeBackend=object(),
        ),
    }

    def fake_import_module(name):
        if name not in modules:
            raise ModuleNotFoundError(name)
        return modules[name]

    monkeypatch.setattr(b12x_stack_probe.importlib, "import_module", fake_import_module)

    result = b12x_stack_probe.probe_b12x_stack()

    assert result["runtime_routes"]["runtime_b12x_sparse_indexer"]["ok"] is True
    assert result["runtime_routes"]["runtime_native_mxfp4_b12x_moe"]["ok"] is True
    assert result["runtime_routes"]["runtime_ds4_b12x_compressed_mla_adapter"][
        "ok"
    ] is False
    assert result["runtime_routes"]["runtime_ds4_b12x_wo_projection"]["ok"] is True
    assert result["runtime_routes"]["runtime_ds4_b12x_mhc"]["ok"] is True
    assert result["runtime_routes"]["runtime_v32_b12x_mla_sparse"]["ok"] is False


def test_b12x_stack_probe_classifies_current_dev_without_aiden_runtime(monkeypatch):
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
        ),
        "b12x.integration.compressed_scratch": types.SimpleNamespace(
            plan_compressed_mla_scratch=object(),
        ),
        "b12x.integration.tp_moe": types.SimpleNamespace(
            plan_tp_moe_scratch=object(),
            b12x_moe_fp4=object(),
        ),
        "flashinfer.fused_moe": types.SimpleNamespace(b12x_fused_moe=object()),
        "vllm.envs": types.SimpleNamespace(),
        "vllm.model_executor.layers.fused_moe.experts.flashinfer_b12x_moe": (
            types.SimpleNamespace(FlashInferB12xExperts=object())
        ),
    }

    def fake_import_module(name):
        if name not in modules:
            raise ModuleNotFoundError(name)
        return modules[name]

    monkeypatch.setattr(b12x_stack_probe.importlib, "import_module", fake_import_module)

    result = b12x_stack_probe.probe_b12x_stack()

    assert result["routes"]["flashinfer_b12x_moe_nvfp4"]["ok"] is True
    assert result["runtime_routes"]["runtime_b12x_sparse_indexer"]["ok"] is False
    assert result["runtime_routes"]["runtime_native_mxfp4_b12x_moe"]["ok"] is False
    assert result["runtime_routes"]["runtime_flashinfer_b12x_moe"]["ok"] is True


def test_b12x_stack_probe_markdown_records_routes(tmp_path: Path):
    result = {
        "distributions": {"b12x": {"ok": True, "version": "0.15.2"}},
        "modules": {
            "b12x.integration.mla": {
                "ok": True,
                "attributes": {"compressed_mla_decode_forward": True},
            }
        },
        "layouts": {
            "b12x_compressed_mla": {
                "ok": True,
                "vllm_zero_copy_compatible": False,
                "reason": "page-packed layout does not match vLLM rows",
            }
        },
        "routes": {
            "aiden_ds4_compressed_mla": {
                "ok": False,
                "note": "missing compressed scratch",
            },
            "public_b12x_sparse_indexer_extend": {
                "ok": True,
                "note": "b12x extend_tiled_topk is available",
            },
        },
        "vllm_modules": {
            "vllm.model_executor.layers.sparse_attn_indexer": {
                "ok": True,
                "attributes": {"_use_b12x_sparse_indexer": True},
            },
        },
        "runtime_routes": {
            "runtime_b12x_sparse_indexer": {
                "ok": True,
                "note": "vLLM runtime can select b12x sparse indexer",
            },
        },
    }
    output = tmp_path / "probe.md"

    b12x_stack_probe.write_b12x_stack_probe_markdown(output, result)

    text = output.read_text(encoding="utf-8")
    assert "# B12X Stack Probe" in text
    assert "`aiden_ds4_compressed_mla`" in text
    assert "`public_b12x_sparse_indexer_extend`" in text
    assert "b12x extend_tiled_topk is available" in text
    assert "`runtime_b12x_sparse_indexer`" in text
    assert "vLLM runtime can select b12x sparse indexer" in text
    assert "missing compressed scratch" in text
    assert "page-packed layout does not match vLLM rows" in text


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
