# SM120 Decisions

Decision files record durable conclusions that may be supported by multiple
experiments. Prefer one decision per route, policy, or recommendation.

## Categories

- `accepted/`: current recommendations or promoted routes.
- `rejected/`: routes that should not be pursued in the tested form.
- `blocked/`: routes blocked by dependency, API, startup, hardware, or
  correctness constraints.
- `superseded/`: decisions replaced by newer evidence or a changed baseline.
- `watchlist/`: promising or unstable items that need periodic recheck.

## Decision Rules

- Keep each decision focused. Split if one file needs to cover unrelated
  routes.
- Record profile sensitivity explicitly. A conclusion from EP-on does not
  automatically apply to EP-off, and prefix-cache-on does not imply cold
  prefill performance.
- Link evidence instead of copying long logs or tables.
- Include a clear reopen condition. If there is no plausible reopen condition,
  say why the decision is stable.
- Update `docs/sm120/index.md` when a decision becomes an active navigation
  point.

Use `TEMPLATE.md` for new decision files.

