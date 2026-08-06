# SM120 Index

This is the routing index for new SM120 / SM121 optimization work. Historical
pre-framework entries remain indexed in `docs/sm120_experiment_index.md`.

## Current Entry Points

- Current posture: `docs/sm120_current_state.md`
- New documentation rules: `docs/sm120/README.md`
- Durable decisions: `docs/sm120/decisions/`
- New experiment packages: `docs/sm120/experiments/`
- Promotion gates: `docs/vllm_correctness_gates.md`
- Legacy historical index: `docs/sm120_experiment_index.md`
- Legacy evidence archive: `docs/sm120_optimization_notes.md`

## Current Decisions

Add new durable conclusions under `decisions/` and link them here only when
they are useful as active navigation points.

| Decision | Status | Scope | Last reviewed |
| --- | --- | --- | --- |
| [SM12x Backend Parity Roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) | watchlist | EP-off backend parity, upstream arch coverage, FlashInfer/b12x, black-benediction | 2026-06-14 |
| [Upstream MRv2 And Breakable CUDA Graph Watch](decisions/watchlist/2026-06-13-upstream-mrv2-cudagraph-watch.md) | watchlist | upstream `#42667`, Model Runner v2 MoE routing, breakable CUDA graph correctness | 2026-06-13 |

## Current Experiment Packages

Add new experiment packages under `experiments/YYYY-MM-DD-short-topic/` and
link them here after the package has at least a `README.md` and `evidence.md`.

| Experiment | Scope | Status | Decision links |
| --- | --- | --- | --- |
| [EP-Off Backend Revalidation](experiments/2026-06-12-epoff-backend-revalidation/README.md) | 2026-06-12 PR stable preview baseline and next backend A/B matrix | watchlist | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [EP-Off Bottleneck Map](experiments/2026-06-12-epoff-bottleneck-map/README.md) | RTX-first bottleneck attribution, correctness guard, GB10 confirmation plan, [preflight](experiments/2026-06-12-epoff-bottleneck-map/preflight.md), and [latest preflight result](experiments/2026-06-12-epoff-bottleneck-map/preflight-results.md) | watchlist | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [Black-Benediction Mechanism Map](experiments/2026-06-12-black-benediction-map/README.md) | External black-benediction reference split into portable, high-risk, and reference-only mechanisms | watchlist | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [Local-Inference Main RTX Baseline](experiments/2026-06-13-local-inference-main-baseline/README.md) | External `local-inference-lab/vllm main` endpoint baseline for RTX / SM120 EP-off prefill and GSM8K | observation | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [Black-Benediction RTX Public-Stack Baseline](experiments/2026-06-13-black-benediction-rtx-public-stack/README.md) | External `dev/black-benediction` endpoint baseline for RTX / SM120 public dependency stack | observation | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [Aiden Recipe Forum Watch](experiments/2026-06-13-aiden-recipe-forum-watch/README.md) | Public GB10 Aiden image / unholy-fusion continuation claims and reproducibility notes | watchlist | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [Direct-Paged Sparse Prefill Prototype](experiments/2026-06-13-direct-paged-prefill-prototype/README.md) | Default-off fork-independent direct page-table prefill route on RTX / SM120 | rejected | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [Fused Grouped-SWA Microbench](experiments/2026-06-13-fused-grouped-swa-microbench/README.md) | Component-level fused grouped-SWA plus compressed-state merge, plus rejected endpoint follow-up on RTX / SM120 | component watchlist, endpoint rejected | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [Indexed D512 Min-Token Gate](experiments/2026-06-13-indexed-d512-min-token-gate/README.md) | Fork-independent min-token admission sweep for existing indexed D512 sparse prefill on RTX / SM120 | observation | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [RTX LLM Decode Bench](experiments/2026-06-14-rtx-llm-decode-bench/README.md) | Community `llm_decode_bench.py` optional harness integration, RTX / SM120 decode and prefill comparison, Lucifer+PR3395 reproduction, and pitfall log | observation | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [2026-08-07 Baseline of Record (db8f836e8b)](experiments/2026-08-07-baseline-of-record-db8f836e8b.md) | Post fix-wave reference set on 2x GB10 TP=2: benchy pp 1225-1432 / tg spec 47.7-55.3, GSM8K 0.9439 strict, arthur 2/2 + 23/24, multi-needle 48/48 at 42K/80K | baseline-of-record | — |

## Legacy Notes

Use legacy files for lookup only:

- `docs/sm120_experiment_index.md` routes to historical evidence anchors.
- `docs/sm120_optimization_notes.md` is the long append-only archive for work
  recorded before this framework.
