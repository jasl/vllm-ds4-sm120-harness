# B200 Baseline Summary

- label: `sm120_post_rebase_c92696943`
- archive_previous: `1`, prefix `sm120_post_rebase_c92696943`
- model: `deepseek-ai/DeepSeek-V4-Flash`
- base_url: `http://127.0.0.1:8000`
- variants: `mtp1`
- phases: `acceptance,bench_hf_mt_bench,eval_gsm8k,decode_profile,long_context_probe,eval_longbench2`
- variant_parallel: `0`
- serve_max_model_len: `65536`
- serve_use_fp4_indexer_cache: `auto`
- no_mtp_concurrency: `1,2,4,8,16,24`
- mtp_concurrency: `1,2,4,8,16,24`
- num_prompts: `80`
- acceptance: `1`
- kv_layout_probe: `0`, shape `2 x 256 x (448 + 8)`, require helper `1`
- long_context_probe: `1`, lines `1900`, max tokens `128`, thinking `non-thinking`
- prefix_cache_probe: `0`, lines `1900`, max tokens `64`, thinking `non-thinking`, fail_on_regression `0`
- streaming_pressure_soak: `0`, concurrency `4`, rounds `3`, lines `1200`, max tokens `128`, thinking `non-thinking`, fail_on_slow `0`
- hf_benchmark: `1`
- lm_eval: `1`, tasks `gsm8k`, fewshot `5`, limit `200`, no-MTP concurrency `4`, MTP concurrency `1`
- lm_eval_tokenizer_backend: `none`
- random_long: `1`, concurrency `1,2`, shape `8192/512`, prompts `8`
- oracle_export: `0`
- real_scenario_repeat_count: `3`
- api_request_retries: `1`
- generation_prompt_root: `/home/jasl/Workspace/ds4-sm120-harness/prompts`
- generation_languages: `en,zh`
- generation_thinking_modes: `non-thinking,think-high,think-max`
- generation_repeat_count: `3`
- generation_temperature: `1.0`
- generation_top_p: `1.0`
- generation_think_high_token_budget: `4096`
- generation_think_max_token_budget: ``
- generation_think_max_request_max_tokens: `65536`
- generation_prompt_token_reservation: `4096`
- toolcall15_scenario_set: `en`
- toolcall15_thinking_modes: `non-thinking,think-high,think-max`
- toolcall15_repeat_count: `3`
- toolcall15_temperature: `1.0`
- toolcall15_top_p: `1.0`
- run_root: `/home/jasl/Workspace/ds4-sm120-harness/artifacts/unknown-branch/2x_nvidia_rtx_pro_6000_blackwell_workstation_edition/sm120_post_rebase_c92696943/20260517-164751`

## Phase Exit Codes

| Variant | Phase | Exit | Artifact Dir |
| --- | --- | ---: | --- |
| `mtp1` | `server_startup` | `0` | `/home/jasl/Workspace/ds4-sm120-harness/artifacts/unknown-branch/2x_nvidia_rtx_pro_6000_blackwell_workstation_edition/sm120_post_rebase_c92696943/20260517-164751/mtp1/server_startup` |
| `mtp1` | `acceptance` | `1` | `/home/jasl/Workspace/ds4-sm120-harness/artifacts/unknown-branch/2x_nvidia_rtx_pro_6000_blackwell_workstation_edition/sm120_post_rebase_c92696943/20260517-164751/mtp1/acceptance` |
| `mtp1` | `long_context_probe` | `0` | `/home/jasl/Workspace/ds4-sm120-harness/artifacts/unknown-branch/2x_nvidia_rtx_pro_6000_blackwell_workstation_edition/sm120_post_rebase_c92696943/20260517-164751/mtp1/long_context_probe` |
| `mtp1` | `bench_hf_mt_bench` | `1` | `/home/jasl/Workspace/ds4-sm120-harness/artifacts/unknown-branch/2x_nvidia_rtx_pro_6000_blackwell_workstation_edition/sm120_post_rebase_c92696943/20260517-164751/mtp1/bench_hf_mt_bench` |
| `mtp1` | `eval_gsm8k` | `143` | `/home/jasl/Workspace/ds4-sm120-harness/artifacts/unknown-branch/2x_nvidia_rtx_pro_6000_blackwell_workstation_edition/sm120_post_rebase_c92696943/20260517-164751/mtp1/eval_gsm8k` |
| `mtp1` | `decode_profile` | `0` | `/home/jasl/Workspace/ds4-sm120-harness/artifacts/unknown-branch/2x_nvidia_rtx_pro_6000_blackwell_workstation_edition/sm120_post_rebase_c92696943/20260517-164751/mtp1/decode_profile` |
