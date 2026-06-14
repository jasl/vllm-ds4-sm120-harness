# Upstream MRv2 And Breakable CUDA Graph Watch

Status: watchlist
Last reviewed: 2026-06-13
Applies to: SM120 RTX PRO 6000, SM121 GB10, vLLM PR stable preview and
research branches after any upstream/main rebase
Profile sensitivity: EP-off is the current default comparison profile. EP-on,
prefix-cache-on/off, MTP mode, CUDA graph mode, and GB10 correctness must be
reported separately.

## Decision

Do not chase upstream/main automatically, but treat `vllm-project/vllm#42667`
as the first upstream rebase item that can materially change our assumptions.
The PR merged on 2026-06-12 and changes default Model Runner v2 selection for
MoE architectures.

Keep `FULL_AND_PIECEWISE` as the GB10 default CUDA graph mode until breakable
CUDA graph passes correctness and lifecycle gates on SM121. Breakable CUDA graph
is a promising replacement candidate with more optimization headroom, but the
current GB10 history includes a semantic correctness failure on a trivial
arithmetic prompt, so it is not a safe default or PR promotion route yet.

## Upstream Input

- `vllm-project/vllm#42667`:
  `[Model Runner v2] Migration from v1 to v2, with Qwen and DSv2 MOE models
  [3/N]`.
- Merged into upstream/main on 2026-06-12 at merge commit
  `78739c1946cfa88fba8ccd4ca7d6c4230f816a3c`; PR head
  `7a77c30a01b049d4e9847424c1c5073ce54a882f`.
- File-level change surface:
  - `vllm/config/vllm.py`
  - `tests/test_config.py`
- Functional reading from the patch:
  - `DEFAULT_V2_MODEL_RUNNER_ARCHITECTURES` now includes
    `DeepseekV2ForCausalLM` and `Qwen2MoeForCausalLM`.
  - `_is_default_v2_model_runner_model` no longer rejects a model solely because
    `model_config.is_moe` is true.
  - quantized models remain excluded from default V2 runner selection.
  - elastic expert parallelism is explicitly listed as unsupported for V2.

## Implications For SM12x Work

- Rebase review must include the runner-selection path before comparing
  performance. A candidate can look faster or slower simply because the active
  runner changed.
- Any upstream/main rebase that includes `#42667` should record:
  - whether DeepSeek V4 still routes through the intended custom SM12x path;
  - active runner version and CUDA graph mode;
  - EP mode and whether elastic EP is disabled or rejected;
  - whether existing environment gates still control the same code paths.
- Breakable CUDA graph should be evaluated as its own branch-local candidate,
  not mixed into sparse-prefill kernel work. The first pass should be endpoint
  A/B against `FULL_AND_PIECEWISE`, not a combined rebase plus backend patch.

## Gates Before Promotion

Breakable CUDA graph cannot become default behavior until all of these are true:

- RTX / SM120: same-profile correctness passes, including GSM8K limit-200 or a
  stronger paired semantic gate.
- GB10 / SM121: the simple arithmetic regression is not reproducible, then the
  reduced long-context, forum53-style marker, prefix-cache-on/off, and driver
  health gates pass.
- Performance: lower TTFT/ITL or better throughput is visible under the same
  runner, same EP mode, same prefix-cache mode, and same dependency stack.
- Lifecycle: no new KV-cache, graph-break, memory-growth, or stale-context
  symptoms after repeated serve cycles.

## Evidence

- GitHub PR: `https://github.com/vllm-project/vllm/pull/42667`
- Remote check on 2026-06-13: upstream/main was
  `470229c37efaf69c86e8bc97482b0b1ff7551c65`.
- PR-stack rebase candidate on 2026-06-13:
  `codex/ds4-sm120-min-enable-upstream-rebase-20260613` at
  `71cbb6b331905cad0a068d6e472d9297d256426b`, rebased onto upstream/main
  `470229c37efaf69c86e8bc97482b0b1ff7551c65`.
- PR branch update on 2026-06-13:
  `codex/ds4-sm120-min-enable` was force-updated with `--force-with-lease` from
  `f32247a5a695fa8979d61837bf6b87da897dcb7d` to the same rebased
  `71cbb6b331905cad0a068d6e472d9297d256426b` head after the checks below.
- Fallback tag before that rebase:
  `sm120-pr-41834-fallback-before-upstream-rebase-20260613202236`, pointing to
  pre-rebase stable preview `f32247a5a695fa8979d61837bf6b87da897dcb7d`.
- Rebase conflict note: `vllm/v1/attention/backends/mla/indexer.py` needed a
  manual merge of upstream's SM100 native DSA indexer decode path with the
  existing SM12x flattening safety. The resolved candidate keeps SM100 native
  `next_n > 2` and flattens non-SM100 `next_n > 2`.
- Rebase checks:
  `git diff --check upstream/main...HEAD`, strict conflict-marker scan,
  DCO trailer scan, `py_compile` for the touched config/indexer files, and RTX
  focused pytest for V2 runner selection, DeepSeek V4 cudagraph guard, and
  sparse-MLA metadata all passed.
- Local/user GB10 observation: breakable CUDA graph previously produced an
  incorrect answer for a trivial arithmetic prompt. Treat this as a blocking
  correctness risk until reproduced and fixed or disproven under the current
  branch and dependency stack.

## Reopen If

- upstream/main changes the V2 model runner compatibility list, CUDA graph
  selection, or DeepSeek MoE runner path again.
- Breakable CUDA graph receives an upstream correctness fix or becomes the
  upstream default for the relevant runner.
- Same-profile RTX and GB10 A/B data show a clear performance gain with no
  semantic, lifecycle, or driver-health regression.
