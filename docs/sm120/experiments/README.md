# SM120 Experiments

Each new SM120 / SM121 experiment should live in its own directory:

```text
docs/sm120/experiments/YYYY-MM-DD-short-topic/
  README.md
  evidence.md
  artifacts.md
```

## Experiment Rules

- Use one directory per coherent run or A/B matrix.
- Keep `README.md` short: conclusion, profile, key results, and next action.
- Put commands, logs, raw tables, and failure details in `evidence.md`.
- Put artifact roots and artifact notes in `artifacts.md`.
- If an experiment changes durable guidance, create or update a decision under
  `docs/sm120/decisions/`.
- Do not mix prefix-cache-on and prefix-cache-off, or EP-on and EP-off, into a
  single unqualified conclusion.

Use `TEMPLATE.md` for new experiment packages.

