# Bundle cleanup notes

Some artifacts produced during this run were the result of **harness /
launch-parameter errors**, not model or hardware behaviour. They have
been removed from the bundle to avoid misleading downstream readers.
This file documents what was removed and why; the raw run history
remains in each cell's `probe.log` for audit.

## Removed: `generation/quick_1301_thinkhigh/` (5 .md files)

**Symptom**: 5 think-high prompts (en+zh: aquarium_html, en2zh_news_001,
zh_sum_tech_001, zh2en_news_001), all returned
`HTTP 500 InternalServerError`.

**Root cause**: not a generation failure. The 512K long-context probe
that preceded this gen-quality run was SIGKILLed by the operator
mid-prefill; EngineCore's `sample_tokens` RPC then hung for ~10
minutes, blocking every subsequent request with HTTP 500. The model
never generated a single token for any of the 5 prompts — they were
rejected at the server's outermost RPC layer.

**Replacement**: `generation/redo_1404_thinkhigh/` ran the same 5
prompts after a full cluster restart. All 5 passed.

## Removed: `failures.tsv` rows in each canon cell

The `failures.tsv` summary previously recorded the following entries
that were caused by harness bugs (the model was never invoked):

| cell | removed row | root cause |
|---|---|---|
| agent_mtp2  | `long_context_probe 1`        | LINE_COUNT*tokens_per_line+preamble = max_model_len+1; server rejected with HTTP 400 before generation |
| agent_mtp2  | `acceptance_think-high 1`     | `--reasoning-config` not set on serve at the time of this run; every think-high prompt returned HTTP 400 "thinking_token_budget is set but reasoning_config is not configured". Fixed in `scripts/dgx_spark_start_mp_serve.sh` (commit ae261fa) — but this cell ran before the fix landed |
| agent_mtp2  | `acceptance_think-max 1`      | Same `--reasoning-config` issue |
| agent_nomtp | `long_context_probe 1`        | Same LINE_COUNT off-by-one |
| conv_mtp2   | `long_context_probe 1`        | Same LINE_COUNT off-by-one |
| conv_mtp2   | `prefix_cache_probe 1`        | Same LINE_COUNT off-by-one (probe shares the LINE_COUNT generator) |
| conv_nomtp  | `long_context_probe 1`        | Same LINE_COUNT off-by-one |
| conv_nomtp  | `prefix_cache_probe 1`        | Same LINE_COUNT off-by-one |

## Kept: real generation-quality failures

The following remained in `failures.tsv` because they are **genuine
model-side issues**, not harness errors. They are documented in
`report.md` under "Known issues".

| cell | row | failure |
|---|---|---|
| agent_mtp2  | `acceptance_non-thinking 1` | `en/en_code_fe_001` non-thinking MTP=2: assistant produced a response that lacked the complete HTML artifact required by the probe |
| agent_nomtp | `acceptance_nonthinking 1`  | `en/en_code_fe_001` non-thinking no-MTP: same case, same failure mode |
| conv_nomtp  | `acceptance_nonthinking 1`  | `zh/zh_code_fe_001` non-thinking no-MTP: similar incomplete-HTML failure on the Chinese variant |

These three failures are correlated (frontend-code prompts that
require a long, well-formed HTML response in non-thinking mode are
harder for the model when output budget is tight). They are NOT a
regression vs prior baselines and NOT specific to GB10.
