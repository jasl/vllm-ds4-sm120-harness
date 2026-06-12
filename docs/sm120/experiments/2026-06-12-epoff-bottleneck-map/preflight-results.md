# Preflight Results

Date: 2026-06-12
Status: ready for first GB10/remote-gated bottleneck run

## Local Git State

- Harness checkout has documentation changes only.
- vLLM checkout is clean on
  `codex/ds4-sm120-glm51-experimental-20260612`.
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
  `codex/ds4-sm120-backend-parity-dev-20260612` at `7224e68417`.
  It is based on the PR control branch plus the signed SM12x sparse-MLA
  selector diagnostic commit.
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
- The stale remote `VLLM_VENV` value from the handoff note was corrected in
  `.env` to the currently valid venv under the remote vLLM checkout.
- Remote preflight was run without printing hostnames, IPs, usernames, local
  absolute paths, tokens, or model-cache paths.

Local macOS note:

- The SM120 aliases resolve to the local checkout shape and are ready for use
  on an SM120 host with a built vLLM venv.
- On this macOS harness host, `SM120_VLLM_BIN` does not exist because the local
  vLLM venv is not a GPU serving environment. Do not treat macOS as RTX
  readiness evidence.

## Remote Readiness

Head node:

- SSH batch-mode connectivity: OK.
- Target vLLM root: OK.
- Target vLLM venv Python: OK.
- Target `vllm` CLI: OK.
- Python modules `torch`, `vllm`, `lm_eval`, and `tenacity`: OK.
- `lm_eval` CLI: OK.
- `nvidia-smi`: OK.
- Existing vLLM serve process count: `0`.

Worker node:

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

Remote b12x stack probe on the head node target venv:

| Item | Status |
| --- | --- |
| `b12x` distribution | OK |
| `flashinfer-python` distribution | OK |
| `flashinfer-cubin` distribution | OK |
| `nvidia-cutlass-dsl` distribution | OK |
| public b12x MLA route | OK |
| FlashInfer DSV4 TRTLLM-gen plain route | OK |
| FlashInfer packed SM120 sparse-MLA route | not ready |
| FlashInfer B12X MoE NVFP4 route | OK |
| vLLM runtime FlashInfer DSV4 plain route | OK |
| vLLM runtime FlashInfer B12X MoE route | OK |
| vLLM runtime DS4 B12X compressed-MLA adapter | not ready |

## Next Run

Start with the RTX/SM120 EP-off attribution control when the RTX shell has its
target vLLM venv exported. For GB10 confirmation, the current shell is ready to
run the safe preflight-gated GB10 scripts using the ignored `.env` values.

Do not refresh upstream heads before the first candidate run. Use the frozen
reference tags unless an explicit upstream-change review finds a relevant
change.
