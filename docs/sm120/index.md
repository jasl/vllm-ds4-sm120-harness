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
| [SM12x Backend Parity Roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) | watchlist | EP-off backend parity, upstream arch coverage, FlashInfer/b12x, black-benediction | 2026-06-12 |

## Current Experiment Packages

Add new experiment packages under `experiments/YYYY-MM-DD-short-topic/` and
link them here after the package has at least a `README.md` and `evidence.md`.

| Experiment | Scope | Status | Decision links |
| --- | --- | --- | --- |
| [EP-Off Backend Revalidation](experiments/2026-06-12-epoff-backend-revalidation/README.md) | 2026-06-12 PR stable preview baseline and next backend A/B matrix | watchlist | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [EP-Off Bottleneck Map](experiments/2026-06-12-epoff-bottleneck-map/README.md) | RTX-first bottleneck attribution, correctness guard, GB10 confirmation plan, [preflight](experiments/2026-06-12-epoff-bottleneck-map/preflight.md), and [latest preflight result](experiments/2026-06-12-epoff-bottleneck-map/preflight-results.md) | watchlist | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |
| [Black-Benediction Mechanism Map](experiments/2026-06-12-black-benediction-map/README.md) | External black-benediction reference split into portable, high-risk, and reference-only mechanisms | watchlist | [backend parity roadmap](decisions/watchlist/2026-06-12-backend-parity-roadmap.md) |

## Legacy Notes

Use legacy files for lookup only:

- `docs/sm120_experiment_index.md` routes to historical evidence anchors.
- `docs/sm120_optimization_notes.md` is the long append-only archive for work
  recorded before this framework.
