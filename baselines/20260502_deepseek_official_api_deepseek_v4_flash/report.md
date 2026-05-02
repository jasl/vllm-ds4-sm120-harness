# DeepSeek Official API Baseline

- Label: `deepseek_official_api_deepseek_v4_flash`
- Date: `20260502`
- Model: `deepseek-v4-flash`

## Phase Exit Codes

| Phase | Exit |
| --- | ---: |
| `smoke` | `0` |
| `generation` | `1` |
| `toolcall15` | `1` |

## Smoke Checks

- Passed: `3/3`
- Cases: `math_7_times_8`, `capital_of_france`, `spanish_greeting`

## Generation

- Passed: `55/72`
- Unique cases: `8`
- Failures: `17`
- Thinking modes: `non-thinking`=24, `think-high`=24, `think-max`=24
- Workloads: `coding`=18, `reading_summary`=18, `translation`=18, `writing`=18
- Temperature: `1.0`=72
- Top P: `1.0`=72
- Prompt tokens: `52134`
- Completion tokens: `179807`
- Total tokens: `231941`

| Case | Workload | Language | Thinking | Round | Temp | Top P | OK | Detail |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `en2zh_tech_001` | `translation` | `en` | `non-thinking` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en_code_be_001` | `coding` | `en` | `non-thinking` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en_sum_tech_001` | `reading_summary` | `en` | `non-thinking` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en_wr_tech_001` | `writing` | `en` | `non-thinking` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `zh2en_tech_001` | `translation` | `zh` | `non-thinking` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_code_fe_001` | `coding` | `zh` | `non-thinking` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_sum_tech_001` | `reading_summary` | `zh` | `non-thinking` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_wr_tech_001` | `writing` | `zh` | `non-thinking` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en2zh_tech_001` | `translation` | `en` | `non-thinking` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en_code_be_001` | `coding` | `en` | `non-thinking` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en_sum_tech_001` | `reading_summary` | `en` | `non-thinking` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en_wr_tech_001` | `writing` | `en` | `non-thinking` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `zh2en_tech_001` | `translation` | `zh` | `non-thinking` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_code_fe_001` | `coding` | `zh` | `non-thinking` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_sum_tech_001` | `reading_summary` | `zh` | `non-thinking` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_wr_tech_001` | `writing` | `zh` | `non-thinking` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en2zh_tech_001` | `translation` | `en` | `non-thinking` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `en_code_be_001` | `coding` | `en` | `non-thinking` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `en_sum_tech_001` | `reading_summary` | `en` | `non-thinking` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `en_wr_tech_001` | `writing` | `en` | `non-thinking` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `zh2en_tech_001` | `translation` | `zh` | `non-thinking` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_code_fe_001` | `coding` | `zh` | `non-thinking` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_sum_tech_001` | `reading_summary` | `zh` | `non-thinking` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_wr_tech_001` | `writing` | `zh` | `non-thinking` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `en2zh_tech_001` | `translation` | `en` | `think-high` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en_code_be_001` | `coding` | `en` | `think-high` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en_sum_tech_001` | `reading_summary` | `en` | `think-high` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en_wr_tech_001` | `writing` | `en` | `think-high` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `zh2en_tech_001` | `translation` | `zh` | `think-high` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_code_fe_001` | `coding` | `zh` | `think-high` | 1 | 1.0 | 1.0 | `False` | missing complete HTML artifact |
| `zh_sum_tech_001` | `reading_summary` | `zh` | `think-high` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_wr_tech_001` | `writing` | `zh` | `think-high` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en2zh_tech_001` | `translation` | `en` | `think-high` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en_code_be_001` | `coding` | `en` | `think-high` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en_sum_tech_001` | `reading_summary` | `en` | `think-high` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en_wr_tech_001` | `writing` | `en` | `think-high` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `zh2en_tech_001` | `translation` | `zh` | `think-high` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_code_fe_001` | `coding` | `zh` | `think-high` | 2 | 1.0 | 1.0 | `False` | missing complete HTML artifact |
| `zh_sum_tech_001` | `reading_summary` | `zh` | `think-high` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_wr_tech_001` | `writing` | `zh` | `think-high` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en2zh_tech_001` | `translation` | `en` | `think-high` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `en_code_be_001` | `coding` | `en` | `think-high` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `en_sum_tech_001` | `reading_summary` | `en` | `think-high` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `en_wr_tech_001` | `writing` | `en` | `think-high` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `zh2en_tech_001` | `translation` | `zh` | `think-high` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_code_fe_001` | `coding` | `zh` | `think-high` | 3 | 1.0 | 1.0 | `False` | missing complete HTML artifact |
| `zh_sum_tech_001` | `reading_summary` | `zh` | `think-high` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_wr_tech_001` | `writing` | `zh` | `think-high` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `en2zh_tech_001` | `translation` | `en` | `think-max` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en_code_be_001` | `coding` | `en` | `think-max` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en_sum_tech_001` | `reading_summary` | `en` | `think-max` | 1 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 400 |
| `en_wr_tech_001` | `writing` | `en` | `think-max` | 1 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 500 |
| `zh2en_tech_001` | `translation` | `zh` | `think-max` | 1 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 200 |
| `zh_code_fe_001` | `coding` | `zh` | `think-max` | 1 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 1000 |
| `zh_sum_tech_001` | `reading_summary` | `zh` | `think-max` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_wr_tech_001` | `writing` | `zh` | `think-max` | 1 | 1.0 | 1.0 | `True` | matched expectation |
| `en2zh_tech_001` | `translation` | `en` | `think-max` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en_code_be_001` | `coding` | `en` | `think-max` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en_sum_tech_001` | `reading_summary` | `en` | `think-max` | 2 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 400 |
| `en_wr_tech_001` | `writing` | `en` | `think-max` | 2 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 500 |
| `zh2en_tech_001` | `translation` | `zh` | `think-max` | 2 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 200 |
| `zh_code_fe_001` | `coding` | `zh` | `think-max` | 2 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 1000 |
| `zh_sum_tech_001` | `reading_summary` | `zh` | `think-max` | 2 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 400 |
| `zh_wr_tech_001` | `writing` | `zh` | `think-max` | 2 | 1.0 | 1.0 | `True` | matched expectation |
| `en2zh_tech_001` | `translation` | `en` | `think-max` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `en_code_be_001` | `coding` | `en` | `think-max` | 3 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 1000 |
| `en_sum_tech_001` | `reading_summary` | `en` | `think-max` | 3 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 400 |
| `en_wr_tech_001` | `writing` | `en` | `think-max` | 3 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 500 |
| `zh2en_tech_001` | `translation` | `zh` | `think-max` | 3 | 1.0 | 1.0 | `False` | response too short: 0 chars, expected >= 200 |
| `zh_code_fe_001` | `coding` | `zh` | `think-max` | 3 | 1.0 | 1.0 | `False` | missing complete HTML artifact |
| `zh_sum_tech_001` | `reading_summary` | `zh` | `think-max` | 3 | 1.0 | 1.0 | `True` | matched expectation |
| `zh_wr_tech_001` | `writing` | `zh` | `think-max` | 3 | 1.0 | 1.0 | `True` | matched expectation |

## ToolCall-15

- Score: `81/90`
- Total cases: `45`
- Scenario sets: `en`
- Thinking modes: `non-thinking, think-high, think-max`
- Rounds: `1`
- Failures: `6`

### Notable Failures

- `TC-11` partial: Used calculator correctly but unnecessarily.
- `TC-14` fail: Did not handle the stock tool error with integrity.
- `TC-03` fail: Did not complete the contact lookup to email chain.
- `TC-03` fail: Did not complete the contact lookup to email chain.
- `TC-07` partial: Completed most of the chain.
- `TC-11` partial: Used calculator correctly but unnecessarily.

## Contents

- `generation/official_api.json`: structured generation rows.
- `generation/<group>/*.md`: human-readable generation transcripts.
- `smoke/official_api.json` and `smoke/official_api.md`: small runnable comparison checks.
- `toolcall15/official_api.json`: ToolCall-15 trace and score.
