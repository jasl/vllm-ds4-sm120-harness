from __future__ import annotations

import json
import os
import platform
import re
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    text = value.strip().casefold()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def parse_nvidia_smi_gpu_csv(text: str) -> list[dict[str, Any]]:
    gpus: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 2:
            continue
        gpu: dict[str, Any] = {
            "index": parts[0],
            "name": parts[1],
        }
        if len(parts) >= 3:
            try:
                gpu["memory_total_mib"] = float(parts[2])
            except ValueError:
                pass
        gpus.append(gpu)
    return gpus


def query_nvidia_smi_gpu_csv(device_ids: str | None = None) -> str | None:
    command = [
        "nvidia-smi",
        "--query-gpu=index,name,memory.total",
        "--format=csv,noheader,nounits",
    ]
    if device_ids:
        command.extend(["-i", device_ids])
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout


def _model_counts(gpus: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(str(gpu.get("name") or "unknown") for gpu in gpus)
    output = []
    for name, count in sorted(counts.items(), key=lambda item: item[0].casefold()):
        memories = [
            gpu.get("memory_total_mib")
            for gpu in gpus
            if gpu.get("name") == name and isinstance(gpu.get("memory_total_mib"), float)
        ]
        row: dict[str, Any] = {
            "name": name,
            "count": count,
        }
        if memories:
            row["memory_total_mib_each"] = max(memories)
        output.append(row)
    return output


def gpu_topology_slug(gpus: list[dict[str, Any]]) -> str:
    if not gpus:
        return "unknown_gpu"
    parts = []
    for model in _model_counts(gpus):
        parts.append(f"{model['count']}x_{slugify(model['name'])}")
    return "__".join(parts)


def summarize_run_environment(
    *,
    env: dict[str, str] | None = None,
    nvidia_smi_output: str | None = None,
) -> dict[str, Any]:
    env = dict(os.environ if env is None else env)
    visible_devices = env.get("CUDA_VISIBLE_DEVICES") or None
    if nvidia_smi_output is None:
        nvidia_smi_output = query_nvidia_smi_gpu_csv(visible_devices)
    gpus = parse_nvidia_smi_gpu_csv(nvidia_smi_output or "")
    configured_slug = env.get("GPU_TOPOLOGY_SLUG")
    effective_topology_slug = gpu_topology_slug(gpus)
    artifact_topology_slug = configured_slug or effective_topology_slug

    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "artifact": {
            "out_dir": env.get("OUT_DIR"),
            "artifact_root": env.get("ARTIFACT_ROOT"),
            "branch_name": env.get("BRANCH_NAME"),
            "run_timestamp": env.get("RUN_TIMESTAMP"),
            "gpu_topology_slug": artifact_topology_slug,
        },
        "harness": {
            "model": env.get("MODEL"),
            "base_url": env.get("BASE_URL"),
            "vllm_bin": env.get("VLLM_BIN"),
            "python": env.get("PYTHON"),
            "concurrency": env.get("CONCURRENCY"),
            "dataset_name": env.get("DATASET_NAME"),
            "dataset_path": env.get("DATASET_PATH"),
        },
        "official_api": {
            "api_key_present": bool(env.get("DEEPSEEK_API_KEY")),
            "base_url": env.get("DEEPSEEK_BASE_URL"),
            "beta_base_url": env.get("DEEPSEEK_BETA_BASE_URL"),
            "model": env.get("DEEPSEEK_MODEL"),
            "flash_model": env.get("DEEPSEEK_FLASH_MODEL"),
            "pro_model": env.get("DEEPSEEK_PRO_MODEL"),
            "thinking_type": env.get("DEEPSEEK_THINKING_TYPE"),
            "reasoning_effort": env.get("DEEPSEEK_REASONING_EFFORT"),
            "preserve_reasoning_content": env.get(
                "DEEPSEEK_PRESERVE_REASONING_CONTENT"
            ),
        },
        "cuda": {
            "cuda_visible_devices": env.get("CUDA_VISIBLE_DEVICES"),
            "cuda_arch_list": env.get("CUDA_ARCH_LIST"),
            "torch_cuda_arch_list": env.get("TORCH_CUDA_ARCH_LIST"),
            "cuda_home": env.get("CUDA_HOME"),
            "triton_ptxas_path": env.get("TRITON_PTXAS_PATH"),
        },
        "gpu": {
            "available": bool(gpus),
            "reason": None if gpus else "nvidia-smi unavailable or returned no GPUs",
            "count": len(gpus),
            "topology_slug": effective_topology_slug,
            "configured_topology_slug": configured_slug,
            "models": _model_counts(gpus),
            "devices": gpus,
        },
    }


def write_run_environment_json(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def _format_value(value: Any) -> str:
    if value is None or value == "":
        return "n/a"
    if isinstance(value, float):
        if value.is_integer():
            return f"{value:.0f}"
        return f"{value:.2f}"
    return str(value)


def write_run_environment_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Run Environment",
        "",
        f"- Generated at UTC: {_format_value(summary.get('generated_at_utc'))}",
        "",
        "## Artifact",
        "",
    ]
    artifact = summary.get("artifact", {})
    lines.extend(
        [
            f"- Output directory: `{_format_value(artifact.get('out_dir'))}`",
            f"- Branch: `{_format_value(artifact.get('branch_name'))}`",
            f"- GPU topology slug: `{_format_value(artifact.get('gpu_topology_slug'))}`",
            "",
            "## Official API",
            "",
        ]
    )
    official = summary.get("official_api", {})
    lines.extend(
        [
            f"- API key present: {_format_value(official.get('api_key_present'))}",
            f"- Base URL: `{_format_value(official.get('base_url'))}`",
            f"- Beta base URL: `{_format_value(official.get('beta_base_url'))}`",
            f"- Model: `{_format_value(official.get('model'))}`",
            f"- Flash model: `{_format_value(official.get('flash_model'))}`",
            f"- Pro model: `{_format_value(official.get('pro_model'))}`",
            f"- Thinking type: `{_format_value(official.get('thinking_type'))}`",
            f"- Reasoning effort: `{_format_value(official.get('reasoning_effort'))}`",
            "- Preserve reasoning_content for tool calls: "
            f"`{_format_value(official.get('preserve_reasoning_content'))}`",
            "",
            "## GPU",
            "",
        ]
    )
    gpu = summary.get("gpu", {})
    if not gpu.get("available"):
        lines.extend(["- Available: no", f"- Reason: {gpu.get('reason', 'unknown')}", ""])
    else:
        lines.extend(
            [
                "- Available: yes",
                f"- Count: {gpu.get('count', 0)}",
                f"- Topology slug: `{gpu.get('topology_slug')}`",
                "",
                "| Model | Count | Memory each |",
                "| --- | ---: | ---: |",
            ]
        )
        for model in gpu.get("models", []):
            lines.append(
                " | ".join(
                    [
                        f"| {model.get('name')}",
                        str(model.get("count", 0)),
                        f"{_format_value(model.get('memory_total_mib_each'))} MiB",
                    ]
                )
                + " |"
            )
        lines.append("")

    cuda = summary.get("cuda", {})
    lines.extend(
        [
            "## CUDA",
            "",
            f"- CUDA_VISIBLE_DEVICES: `{_format_value(cuda.get('cuda_visible_devices'))}`",
            f"- CUDA_ARCH_LIST: `{_format_value(cuda.get('cuda_arch_list'))}`",
            f"- TORCH_CUDA_ARCH_LIST: `{_format_value(cuda.get('torch_cuda_arch_list'))}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
