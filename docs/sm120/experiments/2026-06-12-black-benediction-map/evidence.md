# Evidence

## External Ref Check

Local and remote state checked on 2026-06-12:

| Ref | Head | Notes |
| --- | --- | --- |
| `local-inference/dev/black-benediction` | `c6b2a7b187` | Local remote-tracking ref. |
| `local-inference-lab/dev/black-benediction` | `c6b2a7b187` | Same local remote-tracking ref from the public repo. |
| Public remote `dev/black-benediction` | `c6b2a7b18747ba467d25dd6d72be3559aaf7a341` | Confirmed by `git ls-remote`. |
| Latest commit | `c6b2a7b187 Fix DFlash long-context decode slowdown` | Touches Triton unified attention helper code. |

## Diff Scope

The full diff from PR stable preview to black-benediction is too broad for
direct porting:

```bash
git -C vllm diff --stat \
  f32247a5a695fa8979d61837bf6b87da897dcb7d..local-inference/dev/black-benediction \
  -- vllm csrc tests cmake setup.py pyproject.toml
```

Observed scope: 756 files changed, about 24k insertions and 48k deletions.
This includes substantial upstream drift and unrelated areas, so use narrower
mechanism ranges.

The black-benediction-specific range is more useful:

```bash
git -C vllm log --oneline --reverse \
  local-inference/main..local-inference/dev/black-benediction
```

Key commits in that range:

| Commit | Area | Initial classification |
| --- | --- | --- |
| `4411e3b486` Make B12X virtual TP padding automatic | B12X config/runtime shape | research; portability depends on public API |
| `c8f4ccad6c` Use unified b12x indexer planning | sparse indexer | research; compare with public b12x mainline |
| `a994c7258d` Assert b12x prefill uses packed indexer route | sparse indexer validation | useful invariant if public API matches |
| `bb6c5b7351` Reserve b12x MLA warmup scratch | CUDA graph/warmup | potentially portable if public API matches |
| `ff7dbc60e3` Support MiMo V2.5 FP4-DFlash B12X Triton runtime | non-DS4 model + DFlash | reference only for DS4 |
| `0d9df30a2f` Support MiMo FP4 FlashInfer Cutlass MoE | non-DS4 MoE | reference only unless DS4 MoE evidence appears |
| `f68edcafa8` Apply DFlash uniform batch prefill fix | DFlash/spec decode | high correctness risk |
| `98eabd68ee` Port DFlash SWA support | DFlash/SWA | high correctness risk |
| `d9888dc921` Port DFlash FlashInfer backend support | DFlash/FlashInfer | high correctness and dependency risk |
| `b665783d54` Port FlashInfer metadata grouping for DFlash SWA | DFlash metadata | high correctness risk |
| `636540030a` Honor MiMo DFlash SWA config | DFlash config | high correctness risk |
| `346ad6f3aa` Route b12x MXFP4 MoE to DeepSeek-style method | MoE quantization | research; requires endpoint MoE evidence |
| `841798ccc8` Fix DFlash draft fidelity to reference semantics | DFlash correctness | correctness reference, not speed-first |
| `c6b2a7b187` Fix DFlash long-context decode slowdown | Triton attention/DFlash decode | high correctness risk |

## Mechanism Map

| Mechanism | Files observed | What to learn | Promotion risk |
| --- | --- | --- | --- |
| B12X sparse MLA backend | `vllm/v1/attention/backends/mla/b12x_mla_sparse.py`, `vllm/models/deepseek_v4/nvidia/b12x.py` | Whether public b12x can reduce DS4 sparse-MLA cost or memory pressure under EP-off. | High until public API, endpoint attribution, and graph warmup are proven. |
| B12X sparse indexer | `vllm/model_executor/layers/sparse_attn_indexer.py`, `tests/model_executor/layers/test_sparse_attn_indexer_b12x.py` | Whether packed/paged indexer planning avoids K copies and improves effective visits/s. | High; previous public route had TMA partitioning failures on GB10. |
| B12X MoE / MXFP4 routing | `vllm/model_executor/layers/quantization/fp8.py` plus earlier local-inference commits | Whether EP-off exposes a MoE bottleneck that B12X can fix. | Medium-high; must not trade speed for correctness or memory instability. |
| DFlash/SWA/spec decode | `vllm/v1/spec_decode/dflash.py`, `vllm/v1/spec_decode/llm_base_proposer.py`, `tests/v1/spec_decode/test_dflash_swa.py` | Metadata, slot mapping, per-KV-group block table, and long-context decode handling. | Very high; run correctness before performance claims. |
| Triton unified attention helper changes | `vllm/v1/attention/ops/triton_attention_helpers.py`, `vllm/v1/attention/ops/triton_unified_attention.py` | Why the latest DFlash long-context decode slowdown fix works. | Very high if ported outside the exact DFlash shape. |
| CUDA graph/warmup behavior | B12X warmup and scratch reservation commits | Whether graph profiling startup pressure can be reduced without disabling `FULL_AND_PIECEWISE`. | Medium; must preserve graph mode and GB10 driver health. |

## Read-Only Study Commands

Use these to refresh the map without changing the working tree:

```bash
git -C vllm fetch local-inference dev/black-benediction
git -C vllm rev-parse local-inference/dev/black-benediction
git -C vllm log --oneline --reverse \
  local-inference/main..local-inference/dev/black-benediction
```

```bash
git -C vllm diff --stat \
  local-inference/main..local-inference/dev/black-benediction \
  -- vllm/v1/spec_decode \
     vllm/v1/worker/gpu/spec_decode \
     vllm/model_executor/models/qwen3_dflash.py \
     vllm/config/speculative.py \
     tests/v1/spec_decode
```

```bash
git -C vllm diff --stat \
  local-inference/main..local-inference/dev/black-benediction \
  -- vllm/models/deepseek_v4 \
     vllm/v1/attention/backends/mla \
     vllm/model_executor/layers/sparse_attn_indexer.py \
     tests/model_executor/layers/test_sparse_attn_indexer_b12x.py
```

Disposable worktree for endpoint reproduction:

```bash
git -C vllm fetch local-inference dev/black-benediction
git -C vllm worktree add \
  ../tmp/vllm-black-benediction-c6b2a7b \
  local-inference/dev/black-benediction
```

After the run, remove it only if it is clean:

```bash
git -C tmp/vllm-black-benediction-c6b2a7b status --short
git -C vllm worktree remove ../tmp/vllm-black-benediction-c6b2a7b
```

## Reproduction Gate

Do not port from black-benediction before a same-profile endpoint A/B exists.
The first reproduction should be:

1. The preflight checklist in
   `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/preflight.md`.
2. Stable preview EP-off RTX attribution control from
   `docs/sm120/experiments/2026-06-12-epoff-bottleneck-map/evidence.md`.
3. A disposable black-benediction checkout or worktree using the same harness
   profile.
4. GSM8K limit-200 on any route that changes DFlash/speculative decode or
   attention helper semantics.
5. GB10 attribution and forum53 only after RTX explains the gain.

Focused vLLM tests to preserve if an equivalent DFlash idea is ported:

```bash
./vllm/.venv/bin/python -m pytest \
  tests/v1/spec_decode/test_dflash_swa.py \
  tests/v1/spec_decode/test_mtp.py \
  tests/v1/attention/test_mla_backends.py \
  -q
```

The exact test list may need adjustment on the local PR branch because
black-benediction contains upstream drift and tests that do not exist in the
stable-preview branch.
