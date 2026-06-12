# Agent Instructions

This repository is the public, repo-independent validation harness for the
DeepSeek V4 SM12x work. Keep rules here safe for public GitHub visibility.

## Scope

- These instructions apply to this harness repository.
- When editing a vLLM checkout from this context, read and follow that vLLM
  checkout's own `AGENTS.md` first. For vLLM files, the vLLM repository's rules
  take precedence over this harness repository's rules.
- vLLM pull requests require DCO sign-off on every commit. When creating,
  amending, cherry-picking, rebasing, squashing, or force-pushing commits for a
  vLLM branch, use `git commit -s` or otherwise ensure each resulting commit has
  a valid `Signed-off-by: Name <email>` trailer before pushing.
- Do not put private hostnames, IP addresses, usernames, local absolute paths,
  tokens, or oracle bundle locations in tracked files. Use ignored local notes
  such as `*.local.md` for machine-specific details.

## Subagents

The user has authorized subagent use for implementation, review, and codebase
exploration related to this repository and the associated vLLM work.

- Use subagents when they materially help: independent code review, parallel
  codebase exploration, verification planning, or disjoint implementation
  slices.
- Keep small, sequential edits local instead of spawning agents by reflex.
- When delegating code changes, give each worker an explicit ownership area and
  remind it that other edits may exist in the codebase.
- Review subagent results before relying on them; do not treat their output as
  verification by itself.

## Testing And TDD

- TDD is encouraged for behavior changes: add a focused failing test first,
  verify it fails for the expected reason, implement, then verify it passes.
- Preserve tests that carry long-term value: behavior, protocol boundaries,
  regression cases, parser compatibility, validation, and acceptance gates.
- Before finishing vLLM changes, self-review the implementation and prune TDD
  scaffolding that does not provide durable maintenance value. Do not leave
  mechanics-only fixtures, temporary probes, or duplicate assertions just
  because they were useful during development.
- Always report the exact verification commands that were run, including any
  test skipped or blocked by missing environment support.

## Harness Changes

- Keep the runtime stdlib-only unless there is a clear reason to expand it.
- Unit tests may use project test dependencies such as `pytest`.
- For script entrypoints, preserve explicit interpreter overrides such as
  `PYTHON=/path/to/python` so the harness can run against a target vLLM venv.
- Treat local macOS results as harness validation only. GPU-path validation must
  run on an appropriate remote SM120/SM121 environment.

## SM120 Documentation

- For new SM120 / SM121 optimization notes, follow `docs/sm120/README.md`.
- Do not append new detailed experiment narratives to
  `docs/sm120_optimization_notes.md`; treat it as the legacy evidence archive.
- Put new experiment packages under `docs/sm120/experiments/` and durable
  conclusions under `docs/sm120/decisions/`.
- Keep EP-on/off and prefix-cache-on/off profile sensitivity explicit in new
  experiment and decision notes.
