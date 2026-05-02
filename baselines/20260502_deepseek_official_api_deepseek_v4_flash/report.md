# DeepSeek Official API Baseline

- Label: `deepseek_official_api_deepseek_v4_flash`
- Date: `20260502`
- Model: `deepseek-v4-flash`

## Phase Exit Codes

| Phase | Exit |
| --- | ---: |
| `smoke` | `0` |
| `generation` | `1` |
| `toolcall15` | `0` |

## Smoke Checks

- Passed: `3/3`
- Cases: `math_7_times_8`, `capital_of_france`, `spanish_greeting`

## Generation

- Passed: `30/36`
- Prompt tokens: `3837`
- Completion tokens: `22671`
- Total tokens: `26508`

| Case | Workload | Language | Thinking | Round | OK | Detail |
| --- | --- | --- | --- | ---: | ---: | --- |
| `translation_en_to_zh` | `translation` | `en` | `non-thinking` | 1 | `True` | matched expectation |
| `writing_follow_instructions` | `writing` | `en` | `non-thinking` | 1 | `True` | matched expectation |
| `translation_zh_to_en` | `translation` | `zh` | `non-thinking` | 1 | `True` | matched expectation |
| `writing_local_llm_tradeoffs` | `writing` | `zh` | `non-thinking` | 1 | `True` | matched expectation |
| `translation_en_to_zh` | `translation` | `en` | `non-thinking` | 2 | `True` | matched expectation |
| `writing_follow_instructions` | `writing` | `en` | `non-thinking` | 2 | `True` | matched expectation |
| `translation_zh_to_en` | `translation` | `zh` | `non-thinking` | 2 | `True` | matched expectation |
| `writing_local_llm_tradeoffs` | `writing` | `zh` | `non-thinking` | 2 | `True` | matched expectation |
| `translation_en_to_zh` | `translation` | `en` | `non-thinking` | 3 | `True` | matched expectation |
| `writing_follow_instructions` | `writing` | `en` | `non-thinking` | 3 | `True` | matched expectation |
| `translation_zh_to_en` | `translation` | `zh` | `non-thinking` | 3 | `True` | matched expectation |
| `writing_local_llm_tradeoffs` | `writing` | `zh` | `non-thinking` | 3 | `True` | matched expectation |
| `translation_en_to_zh` | `translation` | `en` | `think-high` | 1 | `True` | matched expectation |
| `writing_follow_instructions` | `writing` | `en` | `think-high` | 1 | `True` | matched expectation |
| `translation_zh_to_en` | `translation` | `zh` | `think-high` | 1 | `True` | matched expectation |
| `writing_local_llm_tradeoffs` | `writing` | `zh` | `think-high` | 1 | `True` | matched expectation |
| `translation_en_to_zh` | `translation` | `en` | `think-high` | 2 | `True` | matched expectation |
| `writing_follow_instructions` | `writing` | `en` | `think-high` | 2 | `True` | matched expectation |
| `translation_zh_to_en` | `translation` | `zh` | `think-high` | 2 | `True` | matched expectation |
| `writing_local_llm_tradeoffs` | `writing` | `zh` | `think-high` | 2 | `True` | matched expectation |
| `translation_en_to_zh` | `translation` | `en` | `think-high` | 3 | `True` | matched expectation |
| `writing_follow_instructions` | `writing` | `en` | `think-high` | 3 | `True` | matched expectation |
| `translation_zh_to_en` | `translation` | `zh` | `think-high` | 3 | `True` | matched expectation |
| `writing_local_llm_tradeoffs` | `writing` | `zh` | `think-high` | 3 | `True` | matched expectation |
| `translation_en_to_zh` | `translation` | `en` | `think-max` | 1 | `False` | missing required terms: 隐私, 延迟, 运维 |
| `writing_follow_instructions` | `writing` | `en` | `think-max` | 1 | `True` | matched expectation |
| `translation_zh_to_en` | `translation` | `zh` | `think-max` | 1 | `False` | missing required terms: privacy, latency, operational |
| `writing_local_llm_tradeoffs` | `writing` | `zh` | `think-max` | 1 | `True` | matched expectation |
| `translation_en_to_zh` | `translation` | `en` | `think-max` | 2 | `True` | matched expectation |
| `writing_follow_instructions` | `writing` | `en` | `think-max` | 2 | `True` | matched expectation |
| `translation_zh_to_en` | `translation` | `zh` | `think-max` | 2 | `False` | missing required terms: privacy, latency, operational |
| `writing_local_llm_tradeoffs` | `writing` | `zh` | `think-max` | 2 | `True` | matched expectation |
| `translation_en_to_zh` | `translation` | `en` | `think-max` | 3 | `False` | missing required terms: 隐私, 延迟, 运维 |
| `writing_follow_instructions` | `writing` | `en` | `think-max` | 3 | `False` | missing required terms: Context:, Benefits:, Risks:, Recommendation: |
| `translation_zh_to_en` | `translation` | `zh` | `think-max` | 3 | `False` | missing required terms: privacy, latency, operational |
| `writing_local_llm_tradeoffs` | `writing` | `zh` | `think-max` | 3 | `True` | matched expectation |

## ToolCall-15

- Score: `30/30`
- Total cases: `15`
- Failures: `0`

## Contents

- `generation/official_api.json`: structured generation rows.
- `generation/<group>/*.md`: human-readable generation transcripts.
- `smoke/official_api.json` and `smoke/official_api.md`: small runnable comparison checks.
- `toolcall15/official_api.json`: ToolCall-15 trace and score.
