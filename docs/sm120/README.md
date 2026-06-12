# SM120 Documentation Framework

Use this directory for new SM120 / SM121 optimization notes from
2026-06-12 onward. Older material remains in the legacy files at `docs/`.

## Read Order

1. `docs/sm120_current_state.md` for the current branch posture and active
   recommendation.
2. `docs/sm120/index.md` for current decisions and new experiment packages.
3. `docs/vllm_correctness_gates.md` for promotion and regression gates.
4. `docs/sm120_experiment_index.md` only when looking up pre-framework
   historical evidence.
5. `docs/sm120_optimization_notes.md` only when the legacy artifact trail or
   rejected-route rationale is needed.

## Writing Rules

- Do not append new detailed experiment narratives to
  `docs/sm120_optimization_notes.md`. Treat it as a legacy evidence archive.
- Store each new experiment as one directory under `experiments/`.
- Store durable conclusions as directory-level decisions under `decisions/`.
- Keep `docs/sm120_current_state.md` compact. Update it only when a decision
  changes the current recommendation, promotion posture, or next target.
- Keep `docs/sm120/index.md` as a routing file. It should point to decisions
  and experiment packages, not duplicate their evidence.
- Keep public-safety rules from `AGENTS.md`: no private hostnames, IP
  addresses, usernames, tokens, local absolute paths, or private bundle
  locations in tracked files.

## Required Metadata

Every new experiment and decision must record:

- hardware target, including SM120 / SM121 and host class;
- vLLM commit or branch identity;
- dependency versions or image identity when relevant;
- TP / PP / EP mode, MTP mode, FP8 KV mode, prefix-cache mode, CUDA graph mode,
  `max_model_len`, `max_num_seqs`, and `max_num_batched_tokens`;
- artifact root or local-safe artifact identifier;
- status: `accepted`, `rejected`, `blocked`, `superseded`, `watchlist`, or
  `observation`;
- profile sensitivity, especially whether a result depends on EP-on, EP-off,
  prefix-cache-on, or prefix-cache-off.

## Structure

```text
docs/sm120/
  README.md
  index.md
  decisions/
    README.md
    TEMPLATE.md
    accepted/
    rejected/
    blocked/
    superseded/
    watchlist/
  experiments/
    README.md
    TEMPLATE.md
    YYYY-MM-DD-short-topic/
      README.md
      evidence.md
      artifacts.md
```

`experiments/` answers: what was run, how it was run, what happened.
`decisions/` answers: what we currently believe, why, and when to reopen it.

