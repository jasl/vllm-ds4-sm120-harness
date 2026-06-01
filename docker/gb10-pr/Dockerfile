# syntax=docker/dockerfile:1.6

# GB10 / SM121-only image builder for the DeepSeek V4 SM12x vLLM PR branch.
# Build this on a DGX Spark / GB10 host. The defaults intentionally target the
# public PR branch; override VLLM_REF for dev or experiment branches.

ARG CUDA_IMAGE=nvidia/cuda:13.0.2-devel-ubuntu24.04

FROM ${CUDA_IMAGE} AS base

ARG BUILD_JOBS=8
ARG TARGETARCH
ARG NCCL_REF=v2.30u1

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV UV_SYSTEM_PYTHON=1
ENV UV_BREAK_SYSTEM_PACKAGES=1
ENV UV_LINK_MODE=copy
ENV UV_HTTP_TIMEOUT=600
ENV UV_HTTP_RETRIES=10
ENV PIP_CACHE_DIR=/root/.cache/pip
ENV UV_CACHE_DIR=/root/.cache/uv

ENV CUDA_HOME=/usr/local/cuda
ENV PATH=/usr/lib/ccache:/usr/local/cuda/bin:${PATH}
ENV TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas
ENV TORCH_CUDA_ARCH_LIST=12.1a
ENV CUDA_ARCH_LIST=121a
ENV FLASHINFER_CUDA_ARCH_LIST=12.1a
ENV MAX_JOBS=${BUILD_JOBS}
ENV CMAKE_BUILD_PARALLEL_LEVEL=${BUILD_JOBS}
ENV NINJAFLAGS=-j${BUILD_JOBS}
ENV MAKEFLAGS=-j${BUILD_JOBS}
ENV CCACHE_DIR=/root/.ccache
ENV CCACHE_MAXSIZE=50G
ENV CCACHE_COMPRESS=1
ENV CMAKE_CXX_COMPILER_LAUNCHER=ccache
ENV CMAKE_CUDA_COMPILER_LAUNCHER=ccache

RUN test "${TARGETARCH:-arm64}" = "arm64"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      ccache \
      cmake \
      curl \
      debhelper \
      devscripts \
      fakeroot \
      git \
      libibverbs-dev \
      libibverbs1 \
      libnuma-dev \
      libnuma1 \
      libxcb1 \
      ninja-build \
      python-is-python3 \
      python3-dev \
      python3-pip \
      rdma-core \
      vim \
      wget \
      build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir uv

RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    uv pip install \
      torch==2.11.0 \
      torchvision==0.26.0 \
      torchaudio==2.11.0 \
      triton \
      --index-url https://download.pytorch.org/whl/cu130 && \
    uv pip install \
      nvidia-cuda-cccl==13.0.85 \
      nvidia-cuda-crt==13.0.88 \
      nvidia-cuda-nvcc==13.0.88 \
      nvidia-cuda-runtime==13.0.96 \
      nvidia-nccl-cu13==2.30.4 \
      "nvidia-nvshmem-cu13<3.6" \
      nvidia-nvvm==13.0.88 \
      "apache-tvm-ffi<0.2" \
      build \
      filelock \
      packaging \
      pynvml \
      requests \
      tqdm

RUN python3 - <<'PY' > /tmp/gb10-uv-override.txt
import torch

print(f"torch=={torch.__version__}")
print("nvidia-cuda-cccl==13.0.85")
print("nvidia-cuda-crt==13.0.88")
print("nvidia-cuda-nvcc==13.0.88")
print("nvidia-cuda-runtime==13.0.96")
print("nvidia-nccl-cu13==2.30.4")
print("nvidia-nvshmem-cu13<3.6")
print("nvidia-nvvm==13.0.88")
PY

WORKDIR /workspace

RUN --mount=type=cache,id=git-nccl,target=/repo-cache/nccl \
    set -eux; \
    if [ ! -d /repo-cache/nccl/.git ]; then \
      git clone https://github.com/NVIDIA/nccl.git /repo-cache/nccl; \
    fi; \
    cd /repo-cache/nccl; \
    git fetch origin --tags --force; \
    (git checkout --detach "origin/${NCCL_REF}" 2>/dev/null || \
      git checkout --detach "${NCCL_REF}"); \
    git clean -fdx; \
    make -j "${BUILD_JOBS}" src.build \
      NVCC_GENCODE="-gencode=arch=compute_121,code=sm_121"; \
    make pkg.debian.build \
      NVCC_GENCODE="-gencode=arch=compute_121,code=sm_121"; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      --allow-downgrades --allow-change-held-packages \
      ./build/pkg/deb/*.deb; \
    rm -rf /var/lib/apt/lists/*

FROM base AS vllm-builder

ARG VLLM_REPO=https://github.com/jasl/vllm.git
ARG VLLM_REF=codex/ds4-sm120-min-enable
ARG VLLM_PRS=""

WORKDIR /workspace

RUN --mount=type=cache,id=git-vllm,target=/repo-cache/vllm \
    set -eux; \
    if [ ! -d /repo-cache/vllm/.git ]; then \
      git clone --recursive "${VLLM_REPO}" /repo-cache/vllm; \
    fi; \
    cd /repo-cache/vllm; \
    git remote set-url origin "${VLLM_REPO}"; \
    git fetch origin --tags --force; \
    (git checkout --detach "origin/${VLLM_REF}" 2>/dev/null || \
      git checkout --detach "${VLLM_REF}"); \
    git submodule update --init --recursive; \
    git clean -fdx; \
    rm -rf /workspace/vllm; \
    cp -a /repo-cache/vllm /workspace/vllm

WORKDIR /workspace/vllm

RUN if [ -n "${VLLM_PRS}" ]; then \
      git config --global user.email "builder@example.invalid"; \
      git config --global user.name "Docker Builder"; \
      for pr in ${VLLM_PRS}; do \
        git fetch https://github.com/vllm-project/vllm.git \
          "pull/${pr}/head:pr-${pr}"; \
        git merge --no-edit "pr-${pr}"; \
      done; \
    fi

RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    python3 use_existing_torch.py && \
    sed -i \
      -e '/^flashinfer-python\b/d' \
      -e '/^flashinfer-cubin\b/d' \
      requirements/cuda.txt && \
    uv pip install \
      --override /tmp/gb10-uv-override.txt \
      -r requirements/build/cuda.txt

RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    --mount=type=cache,id=ccache,target=/root/.ccache \
    CCACHE_NOHASHDIR=true \
    uv build --no-build-isolation --wheel . --out-dir=/workspace/wheels -v && \
    git rev-parse HEAD > /workspace/wheels/.vllm-commit

FROM base AS runner

ARG VLLM_REPO=https://github.com/jasl/vllm.git
ARG VLLM_REF=codex/ds4-sm120-min-enable
ARG FLASHINFER_VERSION=0.6.12
ARG NCCL_REF=v2.30u1

LABEL org.opencontainers.image.title="DeepSeek V4 SM121 vLLM PR image"
LABEL org.opencontainers.image.description="GB10-only vLLM image for evaluating the DeepSeek V4 SM12x PR branch"
LABEL org.opencontainers.image.source="https://github.com/jasl/vllm"

WORKDIR /workspace/vllm

RUN mkdir -p /workspace/wheels /workspace/tiktoken_encodings && \
    wget -q -O /workspace/tiktoken_encodings/o200k_base.tiktoken \
      "https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken" && \
    wget -q -O /workspace/tiktoken_encodings/cl100k_base.tiktoken \
      "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"

COPY --from=vllm-builder /workspace/wheels/ /workspace/wheels/

RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    uv pip install \
      --no-deps \
      --override /tmp/gb10-uv-override.txt \
      "flashinfer-python==${FLASHINFER_VERSION}" \
      "flashinfer-cubin==${FLASHINFER_VERSION}" \
      "flashinfer-jit-cache==${FLASHINFER_VERSION}" \
      --find-links https://flashinfer.ai/whl/cu130/flashinfer-jit-cache/ && \
    uv pip install \
      --override /tmp/gb10-uv-override.txt \
      /workspace/wheels/*.whl && \
    uv pip install \
      --override /tmp/gb10-uv-override.txt \
      ray[default] \
      fastsafetensors \
      instanttensor && \
    uv pip install \
      --override /tmp/gb10-uv-override.txt \
      nvidia-nccl-cu13==2.30.4

RUN python3 - <<'PY'
import glob
import os

system = None
for pattern in (
    "/usr/lib/aarch64-linux-gnu/libnccl.so.2",
    "/usr/lib/*-linux-gnu/libnccl.so.2",
):
    matches = glob.glob(pattern)
    if matches:
        system = os.path.realpath(matches[0])
        break

if system is None:
    raise SystemExit("system libnccl.so.2 not found")

patched = 0
for pattern in (
    "/usr/local/lib/python*/dist-packages/nvidia/nccl/lib/libnccl.so.2",
    "/usr/local/lib/python*/site-packages/nvidia/nccl/lib/libnccl.so.2",
):
    for path in glob.glob(pattern):
        if os.path.realpath(path) == system:
            continue
        backup = path + ".python-wheel"
        if not os.path.exists(backup):
            os.rename(path, backup)
        else:
            os.remove(path)
        os.symlink(system, path)
        patched += 1

print(f"Using system NCCL {system}; patched {patched} Python NCCL path(s)")
PY

RUN set -eux; \
    vllm_commit="$(cat /workspace/wheels/.vllm-commit 2>/dev/null || echo unknown)"; \
    { \
      echo "vllm_repo: ${VLLM_REPO}"; \
      echo "vllm_ref: ${VLLM_REF}"; \
      echo "vllm_commit: ${vllm_commit}"; \
      echo "flashinfer_version: ${FLASHINFER_VERSION}"; \
      echo "flashinfer_jit_cache_index: https://flashinfer.ai/whl/cu130/flashinfer-jit-cache/"; \
      echo "torch_cuda_arch_list: ${TORCH_CUDA_ARCH_LIST}"; \
      echo "cuda_arch_list: ${CUDA_ARCH_LIST}"; \
      echo "nccl_ref: ${NCCL_REF:-v2.30u1}"; \
    } > /workspace/build-metadata.yaml

ENV TIKTOKEN_ENCODINGS_BASE=/workspace/tiktoken_encodings
ENV VLLM_WORKER_MULTIPROC_METHOD=spawn
ENV PATH=/workspace/vllm:${PATH}

CMD ["vllm", "--help"]
