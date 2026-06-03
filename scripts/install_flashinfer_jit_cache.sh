#!/usr/bin/env bash
set -euo pipefail

PYTHON="${PYTHON:-python}"
UV_BIN="${UV_BIN:-uv}"
FLASHINFER_CUDA_INDEX="${FLASHINFER_CUDA_INDEX:-cu130}"
FLASHINFER_JIT_CACHE_FIND_LINKS="${FLASHINFER_JIT_CACHE_FIND_LINKS:-https://flashinfer.ai/whl/${FLASHINFER_CUDA_INDEX}/flashinfer-jit-cache/}"
FLASHINFER_INSTALL_DRY_RUN="${FLASHINFER_INSTALL_DRY_RUN:-0}"
export FLASHINFER_CUDA_INDEX

read_versions() {
  "${PYTHON}" - <<'PY'
import importlib.metadata as metadata
import os
import sys

packages = ("flashinfer-python", "flashinfer-cubin", "flashinfer-jit-cache")
versions = {}
for package in packages:
    try:
        versions[package] = metadata.version(package)
    except metadata.PackageNotFoundError:
        versions[package] = ""

version = os.environ.get("FLASHINFER_VERSION", "").strip()
if not version:
    version = versions["flashinfer-python"] or versions["flashinfer-cubin"]
if not version:
    print(
        "FLASHINFER_VERSION is required when flashinfer-python/cubin "
        "is not installed",
        file=sys.stderr,
    )
    sys.exit(2)

base_version = version.split("+", 1)[0]
for package in ("flashinfer-python", "flashinfer-cubin"):
    installed = versions[package]
    if installed and installed.split("+", 1)[0] != base_version:
        print(
            f"{package}=={installed} does not match requested "
            f"FlashInfer base version {base_version}",
            file=sys.stderr,
        )
        sys.exit(3)

jit_version = os.environ.get("FLASHINFER_JIT_CACHE_VERSION", "").strip()
if not jit_version:
    jit_version = version if "+" in version else (
        f"{base_version}+{os.environ['FLASHINFER_CUDA_INDEX']}"
    )

installed_jit = versions["flashinfer-jit-cache"]
if installed_jit and installed_jit.split("+", 1)[0] != base_version:
    print(
        f"flashinfer-jit-cache=={installed_jit} does not match "
        f"FlashInfer base version {base_version}",
        file=sys.stderr,
    )
    sys.exit(4)

print(base_version)
print(jit_version)
print(installed_jit)
PY
}

version_info="$(read_versions)"
FLASHINFER_BASE_VERSION="$(printf '%s\n' "${version_info}" | sed -n '1p')"
FLASHINFER_JIT_CACHE_VERSION_RESOLVED="$(
  printf '%s\n' "${version_info}" | sed -n '2p'
)"
FLASHINFER_JIT_CACHE_INSTALLED="$(printf '%s\n' "${version_info}" | sed -n '3p')"

printf 'FlashInfer base version: %s\n' "${FLASHINFER_BASE_VERSION}"
if [[ -n "${FLASHINFER_JIT_CACHE_INSTALLED}" ]]; then
  printf 'Installed flashinfer-jit-cache: %s\n' "${FLASHINFER_JIT_CACHE_INSTALLED}"
fi
printf 'Installing flashinfer-jit-cache: %s\n' "${FLASHINFER_JIT_CACHE_VERSION_RESOLVED}"
printf 'Find-links: %s\n' "${FLASHINFER_JIT_CACHE_FIND_LINKS}"

install_args=(
  "flashinfer-jit-cache==${FLASHINFER_JIT_CACHE_VERSION_RESOLVED}"
  "--no-deps"
  "--find-links"
  "${FLASHINFER_JIT_CACHE_FIND_LINKS}"
)

if [[ "${FLASHINFER_INSTALL_DRY_RUN}" == "1" || "${FLASHINFER_INSTALL_DRY_RUN}" == "true" ]]; then
  printf 'DRY RUN: '
  if command -v "${UV_BIN}" >/dev/null 2>&1; then
    printf '%q ' "${UV_BIN}" pip install --python "${PYTHON}" "${install_args[@]}"
  else
    printf '%q ' "${PYTHON}" -m pip install "${install_args[@]}"
  fi
  printf '\n'
  exit 0
fi

if command -v "${UV_BIN}" >/dev/null 2>&1; then
  "${UV_BIN}" pip install --python "${PYTHON}" "${install_args[@]}"
else
  "${PYTHON}" -m pip install "${install_args[@]}"
fi

"${PYTHON}" - <<'PY'
import importlib.metadata as metadata

for package in ("flashinfer-python", "flashinfer-cubin", "flashinfer-jit-cache"):
    try:
        print(f"{package}=={metadata.version(package)}")
    except metadata.PackageNotFoundError:
        print(f"{package}: not installed")
PY

flashinfer_bin="$(dirname -- "${PYTHON}")/flashinfer"
if [[ -x "${flashinfer_bin}" ]]; then
  "${flashinfer_bin}" show-config
elif command -v flashinfer >/dev/null 2>&1; then
  flashinfer show-config
fi
