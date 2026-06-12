# Preflight Results

Date: 2026-06-12
Status: ready for RTX/SM120 development and GB10/SM121 stable-preview remote
gates; first RTX EP-off attribution evidence has completed. B12X/packed-SM120
candidate routes still need a dependency update before endpoint A/B.

## Local Git State

- Harness checkout has the backend-parity preparation and first-run wrapper
  committed on `main`.
- vLLM checkout is clean on
  `codex/ds4-sm120-backend-parity-dev-20260612`.
- FlashInfer checkout is clean on `main`; local `main` was fast-forwarded to
  upstream/main `d65c3eb`.
- b12x checkout is clean on `master`.

## Branch And Reference Prep

- PR control branch: `codex/ds4-sm120-min-enable` at `f32247a5a6`.
- PR stable preview tag:
  `sm120-pr-41834-stable-preview-20260612075245`.
- PR fallback tag:
  `sm120-pr-41834-fallback-before-replacement-20260612053720`.
- Backend-parity dev branch:
  `codex/ds4-sm120-backend-parity-dev-20260612` at `591b71bed0`.
  It is based on the PR control branch plus the signed SM12x sparse-MLA
  selector diagnostic commit and the warmup fix that keeps sparse-MLA stats out
  of the server startup path. It also restores sparse-MLA prefill stats
  diagnostics for attribution-only runs.
- FlashInfer PR3395 current snapshot branch:
  `codex/pr3395-sparse-mla-sm120-20260612` at `88539d03`.
  The older local `codex/pr3395-sparse-mla-sm120` branch remains preserved as
  the historical route used by earlier tests.

Frozen local reference tags:

| Repo | Tag | Commit |
| --- | --- | --- |
| vLLM | `sm120-freeze-vllm-upstream-main-20260612` | `b7f9b6a` |
| vLLM | `sm120-freeze-vllm-pr45277-20260612` | `e57d3b78` |
| vLLM | `sm120-freeze-black-benediction-20260612` | `c6b2a7b` |
| FlashInfer | `sm120-freeze-flashinfer-main-20260612` | `d65c3eb` |
| FlashInfer | `sm120-freeze-flashinfer-pr3395-20260612` | `88539d03` |
| b12x | `sm120-freeze-b12x-master-20260612` | `fabb087` |

## Private Environment Prep

- Ignored `.env` now contains the required GB10 variable names loaded from the
  ignored local handoff note. Values are intentionally not recorded here.
- Ignored `.env` now also contains SM120 canonical local aliases:
  `SM120_VLLM_REPO`, `SM120_VLLM_VENV`, `SM120_PYTHON`, and
  `SM120_VLLM_BIN`. Legacy `B200_VLLM_REPO` and `B200_VLLM_VENV` are present
  only as compatibility aliases for older harness scripts.
- Ignored `.env` also contains SM120 remote SSH aliases and remote vLLM/harness
  path aliases for the RTX host. Values are intentionally not recorded here.
- The stale/literal-home remote `VLLM_ROOT` and `VLLM_VENV` values from the
  handoff note were corrected in ignored `.env` to remote absolute paths. GB10
  wrappers source `.env` locally before building SSH commands, so `$HOME/...`
  must not be left for local expansion there.
- Remote preflight was run without printing hostnames, IPs, usernames, local
  absolute paths, tokens, or model-cache paths.

Local macOS note:

- The SM120 aliases resolve to the local checkout shape and are ready for use
  on an SM120 host with a built vLLM venv.
- On this macOS harness host, `SM120_VLLM_BIN` does not exist because the local
  vLLM venv is not a GPU serving environment. Do not treat macOS as RTX
  readiness evidence.

## Remote Readiness

RTX / SM120 node:

- SSH batch-mode connectivity: OK.
- Target harness root: OK.
- Target vLLM root: OK.
- Target vLLM venv Python: OK.
- Target `vllm` CLI: OK.
- `nvidia-smi`: OK; dual RTX PRO 6000 SM120 GPUs detected.
- Remote harness checkout synced to `5eccf83424`.
- Remote vLLM checkout synced to `591b71bed0`.
- Warmup and sparse-stats diagnostics focused tests on the target venv: OK.
- EP-off bottleneck attribution control completed with nonzero sparse stats
  under the relative path listed in `artifacts.md`.

GB10 / SM121 head node:

- SSH batch-mode connectivity: OK.
- Target vLLM root: OK.
- Target vLLM venv Python: OK.
- Target `vllm` CLI: OK.
- Python modules `torch`, `vllm`, `lm_eval`, and `tenacity`: OK.
- `lm_eval` CLI: OK.
- `nvidia-smi`: OK.
- Existing vLLM serve process count: `0`.

GB10 / SM121 worker node:

- SSH batch-mode connectivity: OK.
- Target vLLM root: OK.
- Target vLLM venv Python: OK.
- Target `vllm` CLI: OK.
- Python modules `torch` and `vllm`: OK.
- `nvidia-smi`: OK.
- Existing vLLM serve process count: `0`.

`lm_eval` was installed on the head node's target venv with `uv pip install
--python <target-venv-python> "lm-eval[api]"` because the vLLM checkout rules
forbid bare `pip`.

## Dependency Route Probe

Remote b12x stack probe on the head node target venv was rechecked after
starting the backend-parity phase:

| Item | Status |
| --- | --- |
| `b12x` distribution | `0.15.2` |
| `flashinfer-python` distribution | `0.6.12` |
| `flashinfer-cubin` distribution | `0.6.12` |
| `nvidia-cutlass-dsl` distribution | `4.5.2` |
| `b12x.integration.mla` | import OK; compressed/sparse MLA front-door attrs present |
| `b12x.attention.indexer` | missing |
| `b12x.integration.compressed_scratch` | missing |
| `b12x.integration.tp_moe` | import OK, but scratch planning attrs missing |
| FlashInfer DSV4 TRTLLM-gen plain route | OK |
| FlashInfer packed SM120 sparse-MLA route | not ready |
| FlashInfer B12X MoE NVFP4 route | OK |
| vLLM runtime FlashInfer DSV4 plain route | OK |
| vLLM runtime FlashInfer B12X MoE route | OK |
| vLLM runtime DS4 B12X compressed-MLA adapter | not ready |
| vLLM runtime B12X sparse-indexer hook | not ready |

Interpretation: the current GB10 venv is suitable for stable-preview baseline,
plain FlashInfer DSV4 checks, and FlashInfer B12X MoE availability checks. It
is not ready for black-benediction B12X paged-indexer / compressed-MLA endpoint
A/B, nor for FlashInfer PR3395 packed-SM120 endpoint A/B, without a separate
dependency update or rebuilt candidate environment.

### RTX Dependency Refresh, 2026-06-13

The RTX target venv was refreshed for component probing after the first route
probe:

| Item | Result |
| --- | --- |
| b12x default resolver | Rejected: it moved Torch/Triton/CUDA runtime packages, downgraded NCCL, and made `vllm._C` fail with a Torch ABI symbol error. |
| b12x current experiment state | `b12x==0.20.0` installed as no-deps while keeping the previous Torch/Triton/NCCL runtime stack. |
| Focused vLLM smoke | `tests/v1/attention/test_sm120_deepgemm_fallbacks.py -q`: `9 passed`. |
| FlashInfer rc probe | Corrected: `flashinfer-python/cubin==0.6.13rc1` imports with `FLASHINFER_DISABLE_VERSION_CHECK=1` when paired with an older jit-cache, and imports without the bypass after installing `flashinfer-jit-cache==0.6.13rc1+cu130`. Official rc1 still does not expose `flashinfer.sparse_mla_sm120`. |
| Current public b12x API state | DS4 compressed-MLA scratch/API, sparse-indexer extend, native MXFP4 MoE helper, WO, mHC, FP8 linear, and PCIe all-reduce imports are available. |
| Current vLLM runtime state | DS4 b12x compressed-MLA adapter, native MXFP4 b12x MoE runtime, b12x WO/mHC runtime hooks, and b12x sparse-indexer hook are still absent. |

Artifacts:

- `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_b12x_0200_nodeps_restore`
- `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_flashinfer_0613rc1_nodeps`
- `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_flashinfer_0613rc1_bypass`
- `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_flashinfer_0613rc1_matched`
- `artifacts/main/2x_rtx_pro_6000_sm120/flashinfer_packed_mla_probe/20260613_fi0613rc1_bypass`
- `artifacts/main/2x_rtx_pro_6000_sm120/flashinfer_packed_mla_probe/20260613_fi0613rc1_matched`

This refresh makes public b12x mainline suitable for component probes in the
RTX dev venv. It does not make b12x a ready endpoint route.

## Next Run

Use the completed RTX/SM120 EP-off attribution control as the first bottleneck
evidence. For GB10 confirmation of stable-preview behavior, the current shell
is ready to run the safe preflight-gated GB10 scripts using the ignored `.env`
values. For B12X endpoint work, start from the no-deps b12x `0.20.0` component
state and prove a component win before adding vLLM runtime hooks. For
FlashInfer packed-SM120 candidates, the matching official rc1 wheel/jit-cache
state is now usable but still lacks `flashinfer.sparse_mla_sm120`, so the
packed route remains candidate-gated.

Do not refresh upstream heads before the first candidate run. Use the frozen
reference tags unless an explicit upstream-change review finds a relevant
change.
