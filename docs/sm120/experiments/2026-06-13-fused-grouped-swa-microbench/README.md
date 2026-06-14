# Fused Grouped-SWA Microbench

Status: watchlist component, rejected endpoint prototype
Date: 2026-06-13
Owner/context: fork-independent sparse-MLA prefill component follow-up after
the rejected direct-paged endpoint prototype

## Question

Can the grouped-SWA D512 component keep its RTX / SM120 performance signal if
the grouped SWA online state and compressed/SWA merge are fused into one
kernel, avoiding the extra merge launches that made the earlier endpoint form
regress?

## Profile

- Hardware: dual RTX PRO 6000 / SM120.
- vLLM branch/commit: component microbench uses the current RTX development
  venv, not a serving branch change.
- Dependency or image identity: Torch `2.11.0+cu130`, Triton `3.6.0`, same
  installed vLLM sparse-MLA kernels as the active backend-parity stack.
- TP / PP / EP: not applicable to the component microbench.
- MTP: not applicable.
- FP8 KV: not applicable; this is BF16 synthetic component timing.
- Prefix cache: not applicable; no serving path is exercised.
- CUDA graph mode: not applicable; the script is a direct CUDA/Triton
  component microbench.
- `max_model_len`: not applicable.
- `max_num_seqs`: not applicable.
- `max_num_batched_tokens`: not applicable.
- Other route flags: `--grouped-swa-fused-merge`, mixed C128 compressed plus
  SWA candidate pattern, D=`512`, 512 query tokens, 64 heads, compressed
  candidates `128`.

## Component Result

The fused grouped-SWA component is positive on RTX / SM120 and is the best
current fork-independent component signal for the real D512 mixed stream
contract.

Best parameter point, group size `32` and grouped-SWA block-C `32`, fused-only:

| Candidates | Split ms | Fused grouped-SWA ms | Split/fused speedup | Max abs diff |
| ---: | ---: | ---: | ---: | ---: |
| 640 | 0.6299 | 0.4985 | 1.264x | 0.002607 |
| 1152 | 1.3825 | 0.7435 | 1.860x | 0.000953 |

In the paired run that measured old grouped-SWA and fused grouped-SWA together,
the fused merge reduced component time from `0.5756 -> 0.5202 ms` at 640
candidates and from `0.8225 -> 0.7682 ms` at 1152 candidates.

## Endpoint Follow-Up

The default-off endpoint prototype reached the intended C128 route, but the
current manual grouped-SWA endpoint form is rejected. In the 16K/C=1 RTX
smoke, enabling `VLLM_DEEPSEEK_V4_INDEXED_D512_GROUPED_SWA_PREFILL=1` moved
the mature C128 rows from `mla_prefill_indexed_d512` to
`mla_prefill_indexed_d512_grouped_swa`, but slowed the measured sparse
accumulate work:

| Case | C128 route | C128 sparse accumulate ms | C128 effective visits/s | Total sparse accumulate ms |
| --- | --- | ---: | ---: | ---: |
| grouped-SWA off | `mla_prefill_indexed_d512` | 289.962 | 8.027e8 | 2697.948 |
| grouped-SWA on | `mla_prefill_indexed_d512_grouped_swa` | 1283.237 | 1.814e8 | 3691.097 |

The endpoint data contradicts the component-only signal. The likely issue is
that the custom grouped-SWA D512 pass is much less efficient than the current
indexed-D512 split path for the real C128 row shape, even after fixing internal
chunk position handling.

## Interpretation

This answers only the component question: the dataflow has a real component
win when the final merge is folded into the grouped-SWA pass. It does not
translate to an endpoint win in the current manual D512 route.

This is component-only, EP-agnostic, and prefix-cache-agnostic evidence. It
does not prove endpoint TTFT/input-token improvement. GB10 / SM121 component
confirmation was not run in this slice because no existing Torch/vLLM virtual
environment was found on the GB10 nodes during a lightweight path probe; defer
GB10 until the endpoint candidate exists or an existing GB10 venv is restored.

## Follow-Up

- Create or update decision:
  `docs/sm120/decisions/watchlist/2026-06-12-backend-parity-roadmap.md`.
- Rerun trigger: rerun if the active vLLM sparse-MLA D512 split path, Torch,
  Triton, or RTX dependency stack changes before endpoint work.
- Next command or next owner: do not promote the current grouped-SWA endpoint
  prototype. Reopen only if a packed-attention style implementation, a
  FlashInfer PR3395-derived path, or a materially different D512 SWA kernel can
  preserve the component win at endpoint level. The immediate fork-independent
  target should return to slow non-indexed `mla_prefill_chunk` work or another
  route that does not replace the already-fast indexed-D512 C128 rows.
