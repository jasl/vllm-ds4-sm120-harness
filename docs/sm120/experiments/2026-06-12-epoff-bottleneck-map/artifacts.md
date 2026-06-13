# Artifacts

Use relative paths only. Do not add private hostnames, user names, IP
addresses, tokens, or absolute model-cache locations.

## Baseline Artifacts

| Purpose | Relative artifact |
| --- | --- |
| RTX PR stable preview cold OSL=1 and GSM8K | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_clean_mtp_noep_20260612080629` |
| RTX PR stable preview OSL=128 supplement | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_short_throughput_mtp_noep_20260612084721` |
| GB10 forum53 MTP2 EP-off C=2 prefix-cache gate | `artifacts/codex_pr_stable_preview_f32247a/2x_gb10_sm121/gb10_forum53_mtp2_epoff_c2_gmem0685_mml81920/20260612074113` |

## Historical PR3395 GB10 Promotion Subset

These are positive reference artifacts for the unmerged
`VLLM_DEEPSEEK_V4_FLASHINFER_PACKED_PREFILL=1` route. They are not PR-branch
promotion evidence by themselves because RTX, GSM8K, lifecycle, and full GB10
soak gates were still pending.

| Run | Hardware | Status | Relative artifact |
| --- | --- | --- | --- |
| Packed FlashInfer prefill matrix | SM121 GB10 x2 | 8/8 passed, driver health clean | `artifacts/main/2x_gb10_sm121/20260608_packed_fi_promotion_prefill_gap_valid/20260608180541` |
| Packed FlashInfer reduced long-C2 gate | SM121 GB10 x2 | 4 requests, 0 failures, driver signal 0 | `artifacts/main/2x_gb10_sm121/20260608_packed_fi_promotion_long_c2_mtp2/20260608185801` |
| Packed FlashInfer reduced MTP=2 MoE TP soak | SM121 GB10 x2 | 16 requests, 0 failures, driver signal 0 | `artifacts/main/2x_gb10_sm121/20260608_packed_fi_promotion_mtp2_moe_soak_reduced/20260608190816` |

## Bottleneck Runs

| Run | Branch/commit | Hardware | EP | Prefix cache | Artifact |
| --- | --- | --- | --- | --- | --- |
| RTX EP-off sparse attribution control | `591b71bed0` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_bottleneck_attribution/20260613000055` |
| RTX EP-off sparse stage timing | `591b71bed0` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_stage_timing_attribution/20260613_stage_timing_epoff_16k_65k` |
| RTX sparse MLA NCU microbench | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_sparse_mla_ncu_first/20260613_sparse_mla_ncu_first` |
| RTX b12x / FlashInfer route probe | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/b12x_stack_probe/20260613_route_probe_sm120` |
| RTX dependency refresh, b12x 0.20 no-deps | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_b12x_0200_nodeps_restore` |
| RTX dependency refresh, FlashInfer 0.6.13rc1 no-deps mismatch | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_flashinfer_0613rc1_nodeps` |
| RTX dependency refresh, FlashInfer 0.6.13rc1 bypass smoke | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_flashinfer_0613rc1_bypass` |
| RTX dependency refresh, FlashInfer 0.6.13rc1 matched jit-cache | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_flashinfer_0613rc1_matched` |
| RTX FlashInfer 0.6.13rc1 packed MLA probe, bypass | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/flashinfer_packed_mla_probe/20260613_fi0613rc1_bypass` |
| RTX FlashInfer 0.6.13rc1 packed MLA probe, matched jit-cache | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/flashinfer_packed_mla_probe/20260613_fi0613rc1_matched` |
| RTX b12x compressed MLA component refresh | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/b12x_mla_microbench/20260613_b12x0200_nodeps_default` |
| RTX grouped-SWA D512 component refresh | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/indexed_d512_grouped_swa_microbench/20260613_current_dev_b12x0200_nodeps` |
| RTX grouped-stream component refresh | `591b71bed0` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/indexed_d512_grouped_stream_microbench/20260613_current_dev_b12x0200_nodeps` |
| RTX current D512 gate stage-timing control | `591b71bed0` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_stage_timing_current_gate/20260613030142` |
| RTX D512 multi-prefill stage-timing prototype | `591b71bed0` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_stage_timing_d512_multi_prefill/20260613031257` |
| RTX D512 multi-prefill lifecycle guard | `591b71bed0` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_d512_multi_prefill_correctness_gate_20260613032500/20260613032501` |
| RTX D512 multi-prefill GSM8K 5-shot | `591b71bed0` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_d512_multi_prefill_gsm8k5_on_20260613034101/20260613034102` |
| RTX D512 multi-prefill-off GSM8K 5-shot control | `591b71bed0` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_d512_multi_prefill_gsm8k5_off_20260613034613/20260613034614` |
| GB10 D512 multi-prefill-off 16K control | `741ea24c46` | SM121 GB10 x2 | off | disabled | `artifacts/main/2x_gb10_sm121/gb10_d512_multi_prefill_control_20260613035658/20260613035658` |
| GB10 D512 multi-prefill 16K prototype | `741ea24c46` | SM121 GB10 x2 | off | disabled | `artifacts/main/2x_gb10_sm121/gb10_d512_multi_prefill_on_16k_20260613040708/20260613040708` |
| GB10 D512 multi-prefill-off 65K control | `741ea24c46` | SM121 GB10 x2 | off | disabled | `artifacts/main/2x_gb10_sm121/gb10_d512_multi_prefill_control_65k_20260613042153/20260613042153` |
| GB10 D512 multi-prefill 65K prototype | `741ea24c46` | SM121 GB10 x2 | off | disabled | `artifacts/main/2x_gb10_sm121/gb10_d512_multi_prefill_on_65k_20260613043628/20260613043628` |
| GB10 D512 multi-prefill forum53 env-on | `741ea24c46` | SM121 GB10 x2 | off | enabled | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_multi_prefill_20260613045800/20260613045800` |
| GB10 D512 multi-prefill forum53 clean-boot env-on retry | `741ea24c46` | SM121 GB10 x2 | off | enabled | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_multi_prefill_retry_20260613051100/20260613051042` |
| GB10 D512 multi-prefill forum53 same-branch env-off control | `741ea24c46` | SM121 GB10 x2 | off | enabled | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_multi_prefill_control_20260613052200/20260613052137` |
| RTX D512 multi-prefill forum53 C2 response-capture env-on | `741ea24c46` | SM120 RTX PRO 6000 x2 | off | enabled | `artifacts/main/2x_rtx_pro_6000_sm120/rtx_forum53_mtp2_epoff_d512_on/20260613055203` |
| RTX D512 multi-prefill forum53 C2 response-capture env-off | `741ea24c46` | SM120 RTX PRO 6000 x2 | off | enabled | `artifacts/main/2x_rtx_pro_6000_sm120/rtx_forum53_mtp2_epoff_d512_off/20260613055203` |
| GB10 D512 multi-prefill forum53 C2 response-capture env-on | `741ea24c46` | SM121 GB10 x2 | off | enabled | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_on_capture/20260613055729` |
| GB10 D512 multi-prefill forum53 C2 response-capture env-on repeat | `741ea24c46` | SM121 GB10 x2 | off | enabled | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_on_capture_repeat/20260613060731` |
| GB10 D512 multi-prefill forum53 C2 response-capture env-off control | `741ea24c46` | SM121 GB10 x2 | off | enabled | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_off_capture_control/20260613061702` |
| GB10 D512 cached-prefix guard forum53 clean-boot env-on | `d85821b8c4` | SM121 GB10 x2 | off | enabled | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_cached_prefix_guard_cleanboot_20260613/20260613064338` |
| GB10 D512 cached-prefix guard forum53 env-on, gmem 0.678 | `d85821b8c4` | SM121 GB10 x2 | off | enabled | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_cached_prefix_guard_gmem0678_20260613/20260613065521` |
| RTX D512 fused sink component microbench | `d85821b8c4 + fused-sink patch` | SM120 RTX PRO 6000 x2 | n/a | n/a | `artifacts/main/2x_rtx_pro_6000_sm120/indexed_d512_fused_sink_component/20260613_d85821b_fused_sink` |
| RTX D512 fused sink clean 124K control | `9e1bcfb6e` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/rtx_fused_sink_clean_off_124k_retry/20260613_fused_sink_clean_off_124k_retry` |
| RTX D512 fused sink clean 124K prototype | `9e1bcfb6e` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/rtx_fused_sink_clean_on_124k_retry/20260613_fused_sink_clean_on_124k_retry` |
| RTX D512 fused sink prefix-cache guard | `61966ba471` | SM120 RTX PRO 6000 x2 | off | enabled | `artifacts/HEAD/2x_rtx_pro_6000_sm120/rtx_fused_sink_fixed_prefix_probe_retry/20260613_fused_sink_fixed_prefix_probe_retry` |
| RTX D512 fused sink KV lifecycle guard | `61966ba471` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/HEAD/2x_rtx_pro_6000_sm120/rtx_fused_sink_fixed_kv_lifecycle/20260613_fused_sink_fixed_kv_lifecycle` |
| RTX D512 fused sink GSM8K 5-shot | `61966ba471` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/HEAD/2x_rtx_pro_6000_sm120/rtx_fused_sink_fixed_gsm8k_limit200/20260613_fused_sink_fixed_gsm8k_limit200` |
| RTX EP-on attribution comparison | `f32247a5a6` | SM120 RTX PRO 6000 x2 | on | disabled | _pending_ |
| RTX GSM8K paired/full correctness guard | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| RTX local quality expansion | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |

## Partial Or Rejected Evidence

| Run | Branch/commit | Relative artifact | Reason |
| --- | --- | --- | --- |
| RTX EP-off performance-only control | `e164b76501` | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_bottleneck_attribution/20260612233142` | Benchmarks passed, but sparse stats row counts were zero because the diagnostics commit was missing from the dev branch. Do not use for sparse-MLA attribution. |
| RTX b12x 0.20 default dependency resolver | `591b71bed0` | `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_b12x_0200_upgrade` | Default install pulled Torch/Triton/CUDA runtime changes and downgraded NCCL; `vllm._C` failed with a Torch ABI symbol error. Runtime packages were restored and b12x was kept as a no-deps experiment variable. |
| RTX FlashInfer 0.6.13rc1 no-deps probe | `591b71bed0` | `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_flashinfer_0613rc1_nodeps` | Superseded mismatch probe: import failed because `flashinfer-jit-cache` stayed at `0.6.12+cu130`. `FLASHINFER_DISABLE_VERSION_CHECK=1` bypasses that check for probing, and installing `flashinfer-jit-cache==0.6.13rc1+cu130` fixes the mismatch. |
| RTX FlashInfer 0.6.13rc1 packed MLA probe | `591b71bed0` | `artifacts/main/2x_rtx_pro_6000_sm120/flashinfer_packed_mla_probe/20260613_fi0613rc1_matched` | The matched rc1 wheel/jit-cache state imports normally, but both packed cases fail with `ModuleNotFoundError` because `flashinfer.sparse_mla_sm120` is only on the unmerged PR3395 fork branch, not official rc1. |
| RTX D512 multi-prefill GSM8K 8-shot diagnostic | `591b71bed0` | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_d512_multi_prefill_correctness_gate_20260613032500/20260613032501` | The lifecycle run's `eval_gsm8k` phase inherited the baseline driver's 8-shot default and is not comparable to the 5-shot stable-preview anchor. |
| RTX D512 multi-prefill-off GSM8K 8-shot diagnostic | `591b71bed0` | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_d512_multi_prefill_correctness_control_20260613033202/20260613033202` | Same 8-shot mismatch as above. `lm_eval` exit `0`, floor gate exit `1`, GSM8K flexible/strict `0.925 / 0.920`. Use only as a diagnostic for the 8-shot shape. |
| GB10 D512 multi-prefill 65K continuation | `741ea24c46` | `artifacts/main/2x_gb10_sm121/gb10_d512_multi_prefill_control_20260613035658/20260613035658` | The 16K control case passed, but the subsequent 65K case was refused by safety preflight because the current boot already had an NVRM OOM record. Do not treat this as 65K performance evidence. |
| GB10 D512 multi-prefill forum53 env-on | `741ea24c46` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_multi_prefill_20260613045800/20260613045800` | Matrix failed with 1 marker miss out of 4 requests and dirty post-run driver health. Do not use as positive prefix-cache/user gate evidence. |
| GB10 D512 multi-prefill forum53 clean-boot env-on retry | `741ea24c46` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_multi_prefill_retry_20260613051100/20260613051042` | Clean-boot retry also failed with 1 marker miss out of 4 requests and dirty post-run driver health. This blocks promotion of the env-on route. |
| GB10 D512 multi-prefill forum53 same-branch env-off control | `741ea24c46` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_multi_prefill_control_20260613052200/20260613052137` | Matrix itself passed with 4/4 requests and 0 failures, but post-run driver health was dirty. Use only to separate env-on marker regression from the broader GB10 driver-health issue. |
| GB10 D512 multi-prefill forum53 C2 response-capture env-on | `741ea24c46` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_on_capture/20260613055729` | Matrix passed once with response capture enabled, but the repeat failed; use only as nondeterminism evidence. |
| GB10 D512 multi-prefill forum53 C2 response-capture env-on repeat | `741ea24c46` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_on_capture_repeat/20260613060731` | Matrix failed with 1 marker miss. The captured failed assistant text was the previous assistant status body, which points at a prefix-cache/current-suffix context mix-up rather than empty output or truncation. |
| GB10 D512 multi-prefill forum53 C2 response-capture env-off control | `741ea24c46` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_off_capture_control/20260613061702` | Serve preflight refused the run because the current boot already had an NVRM OOM record. Reboot before using this as an env-off capture control. |
| GB10 D512 cached-prefix guard forum53 clean-boot env-on | `d85821b8c4` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_cached_prefix_guard_cleanboot_20260613/20260613064338` | Matrix passed with 4/4 requests and 0 failures after blocking multi-request D512 on cached-prefix rows, but driver health was dirty with 3 worker-side NVRM OOM signals. Use as correctness-guard evidence only, not as a clean GB10 gate. |
| GB10 D512 cached-prefix guard forum53 env-on, gmem 0.678 | `d85821b8c4` | `artifacts/main/2x_gb10_sm121/gb10_forum53_mtp2_epoff_d512_cached_prefix_guard_gmem0678_20260613/20260613065521` | Matrix again passed with 4/4 requests and 0 failures, but one worker-side NVRM OOM signal still appeared during full-model load. Lowering GPU memory utilization did not produce clean driver health. |
| RTX D512 fused sink combined correctness before guard fix | `9e1bcfb6e` | `artifacts/main/2x_rtx_pro_6000_sm120/rtx_fused_sink_correctness_prefix_kv_gsm8k/20260613_fused_sink_correctness_prefix_kv_gsm8k` | Superseded diagnostic. Prefix-cache probe passed, but the later KV/GSM8K sequence exposed a cached-prefix guard crash in `_prefill_has_cached_prefix` when `seq_lens_cpu` was prefill-only. Fixed by `61966ba471`; use the separate clean guards instead. |

## Latest RTX Attribution Snapshot

| Input length | Sparse rows | Input tok/s C=1 / C=2 / C=4 | Mean TTFT ms C=1 / C=2 / C=4 | P99 TTFT ms C=1 / C=2 / C=4 |
| ---: | ---: | --- | --- | --- |
| 4096 | 2370 | 6241.52 / 6375.10 / 6362.72 | 656.46 / 1205.31 / 2089.68 | 669.53 / 1296.57 / 2582.43 |
| 16384 | 8706 | 8080.89 / 7104.17 / 5938.92 | 2027.05 / 4444.21 / 9439.91 | 2037.59 / 4647.73 / 12000.63 |
| 65536 | 34050 | 7576.42 / 6610.62 / 6541.33 | 8649.86 / 18819.34 / 33233.61 | 8774.34 / 20791.38 / 41515.80 |
| 124000 | 64850 | 6835.25 / 6179.15 / 6185.31 | 18141.62 / 37957.72 / 66063.01 | 18357.06 / 41619.08 / 81513.10 |

## Latest RTX Stage-Timing Snapshot

| Input length | Sparse rows | Effective visits | Stage total ms | Sparse accumulate ms | Sparse accumulate ratio | Sparse ms/Mvisit |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16384 | 4482 | 6922746338 | 20689.546385 | 19310.570236 | 0.933349 | 2.789438 |
| 65536 | 17154 | 33788234210 | 53144.091214 | 51343.7 | 0.966123 | 1.519574 |

## Latest RTX D512 Multi-Prefill Snapshot

| Input length | Gate | Chunk rows | Indexed D512 rows | `num_prefills_not_1` rows | Sparse accumulate ms | Input tok/s C=1 / C=2 / C=4 |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 16384 | current | 2432 | 2050 | 1558 | 21219.778 | 7656.07 / 6905.80 / 6265.39 |
| 16384 | multi-prefill on | 1284 | 3198 | 328 | 11843.018 | 8051.11 / 8253.90 / 8131.02 |
| 65536 | current | 3788 | 13366 | 1968 | 54004.115 | 7140.94 / 6775.50 / 6752.81 |
| 65536 | multi-prefill on | 1820 | 15334 | 0 | 34165.937 | 7607.20 / 7658.31 / 7611.61 |

| Guard | Env | Exit | GSM8K flexible / strict | Notes |
| --- | --- | --- | --- | --- |
| prototype lifecycle | multi-prefill on | `prefix_cache_probe` and `kv_lifecycle_probe` phases `0` | n/a | Marker checks and idle KV threshold passed. |
| prototype GSM8K 5-shot | multi-prefill on | `eval_gsm8k` phase `0` | `0.965 / 0.960` | Floor gate passed. |
| paired GSM8K 5-shot control | multi-prefill off | `eval_gsm8k` phase `0` | `0.950 / 0.930` | Floor gate passed. |

## Latest GB10 D512 Multi-Prefill Snapshot

| Input length | Gate | Chunk rows | Indexed D512 rows | `num_prefills_not_1` rows | Sparse accumulate ms | Input tok/s C=1 / C=2 |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 16384 | multi-prefill off | 1516 | 1558 | 738 | 53976.852 | 1515.63 / 1299.03 |
| 16384 | multi-prefill on | 942 | 2132 | 164 | 42695.228 | 1523.38 / 1495.23 |
| 65536 | multi-prefill off | 2578 | 8856 | 1148 | 172870.259 | 1424.54 / 1277.57 |
| 65536 | multi-prefill on | 1430 | 10004 | 0 | 138329.454 | 1422.45 / 1393.42 |

| Input length | Gate | Mean TTFT ms C=1 / C=2 | P99 TTFT ms C=1 / C=2 | Notes |
| ---: | --- | --- | --- | --- |
| 16384 | multi-prefill off | 10809.88 / 23356.20 | 11279.77 / 26162.13 | 16K case passed; following 65K case blocked by post-run NVRM OOM preflight. |
| 16384 | multi-prefill on | 10755.20 / 20062.23 | 11517.51 / 22527.41 | 16K case passed; post-run check again found NVRM OOM state on the worker boot. |
| 65536 | multi-prefill off | 46005.07 / 91291.83 | 48097.74 / 109641.26 | 65K control passed as a single-case run after reboot. |
| 65536 | multi-prefill on | 46071.38 / 82717.21 | 48249.73 / 97377.85 | 65K prototype passed as a single-case run after reboot; after the run, both nodes were rebooted and the new boot was clean. |

## Latest GB10 Forum53 D512 Multi-Prefill Snapshot

| Gate | Env | Matrix | Max TTFT s | ITL p99 s | Driver health | Use |
| --- | --- | --- | ---: | ---: | --- | --- |
| forum53 env-on | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 1 marker failure | 124.970255 | 0.223721 | dirty, 1 signal | rejected |
| forum53 clean-boot env-on retry | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 1 marker failure | 124.697034 | 0.099339 | dirty, 2 signals | rejected |
| forum53 same-branch env-off control | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=0` | 4 requests, 0 failures | 124.265379 | 0.150068 | dirty, 2 signals | partial attribution control |
| RTX C2 response-capture env-on | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 0 failures | 27.212879 | 0.180494 | clean | RTX non-repro |
| RTX C2 response-capture env-off | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=0` | 4 requests, 0 failures | 26.497937 | 0.049509 | clean | RTX control |
| GB10 C2 response-capture env-on | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 0 failures | 124.279151 | 0.122834 | not a clean gate | nondeterminism check only |
| GB10 C2 response-capture env-on repeat | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 1 marker failure | 122.356447 | 0.395746 | dirty, 3 signals | rejected |
| GB10 C2 response-capture env-off control | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=0` | serve preflight blocked by current-boot driver OOM | n/a | n/a | dirty before serve | blocked control |
| GB10 cached-prefix guard env-on | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 0 failures | 123.803772 | 0.135363 | dirty, 3 signals | correctness guard only |
| GB10 cached-prefix guard env-on, gmem 0.678 | `VLLM_DEEPSEEK_V4_INDEXED_D512_MULTI_PREFILL=1` | 4 requests, 0 failures | 124.231818 | 0.132553 | dirty, 1 signal | correctness guard only |

The env-off control shows the matrix shape itself still passes on this branch.
The env-on retries show a correctness/user-gate regression under MTP2
prefix-cache pressure. Driver-health signals also appear without the env-on
path, so the GB10 startup/post-run memory signal is tracked separately. The
response-capture repeat narrowed the marker miss to a wrong assistant body:
the failed request emitted the previous assistant status text and stopped
without the current marker. That makes the next investigation a GB10
prefix-cache/current-suffix context mapping problem in the env-on route, not a
simple truncation or empty-response problem.

Commit `d85821b8c4` adds a conservative guard for that failure class: when
more than one prefill request is present, indexed D512 multi-prefill is used
only for true cold-prefill rows and is rejected for cached-prefix extend rows.
Single-request D512 remains allowed. With that guard, the same GB10 forum53 C2
MTP2 prefix-cache shape passed twice with 4/4 requests and 0 failures. These
runs are still not clean promotion gates because the worker boot logged NVRM
OOM during the full-model load path. Reducing GPU memory utilization from
`0.685` to `0.678` lowered the signal count but did not eliminate it.

## Latest RTX D512 Fused Sink Snapshot

| Gate | Input tok/s | Mean TTFT ms | P99 TTFT ms | Sparse accumulate ms | Guard result |
| --- | ---: | ---: | ---: | ---: | --- |
| 124K fused sink off | 6946.78 | 17848.74 | 18013.99 | 24491.340 | n/a |
| 124K fused sink on | 7037.46 | 17619.41 | 17829.53 | 21900.707 | n/a |
| prefix-cache guard | n/a | n/a | n/a | n/a | 7 requests, 0 failures |
| KV lifecycle guard | n/a | n/a | n/a | n/a | 4 requests, 0 failures, max idle KV 0.000% |
| GSM8K 5-shot limit-200 | n/a | n/a | n/a | n/a | flexible/strict `0.960 / 0.935`, floor gate passed |

Component production-with-sink microbench showed exact output match and
`1.123x / 1.096x` speedup for candidates `640 / 1152`. Clean endpoint gain is
positive but small, so this remains a default-off component candidate rather
than a promotion-ready route.

## Latest RTX NCU Snapshot

| Case | Tokens | Candidates | Mean ms | Candidate visits/s | SM % | DRAM % | Registers/thread | Achieved occupancy | No eligible % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sparse MLA chunk microbench | 1024 | 640 | 2.718 | 1.543e10 | 61.91 | 6.17 | 118 | 32.60 | 46.36 |

## Latest RTX Route Probe Snapshot

| Route | Ready | Note |
| --- | --- | --- |
| `runtime_flashinfer_mla_sparse_dsv4_plain` | yes | Plain FlashInfer DS4 sparse MLA route; not the PR3395 packed SM120 route. |
| `runtime_flashinfer_b12x_moe` | yes | Upstream FlashInfer B12X MoE route is importable. |
| `public_b12x_mla` | yes | Public b12x MLA front door is importable. |
| `aiden_ds4_compressed_mla` | yes | b12x `0.20.0` no-deps exposes the DS4 compressed-MLA scratch/API surface. |
| `aiden_native_mxfp4_moe` | yes | b12x `0.20.0` exposes the native DS4 MXFP4 MoE helper API, but current vLLM has no runtime integration. |
| `public_b12x_sparse_indexer_extend` | yes | b12x `0.20.0` exposes the sparse-indexer extend top-k API. |
| `public_b12x_vllm_fp8_ds_mla_zero_copy` | yes | Layout probe says vLLM physical page layout can match b12x by a 2D page-byte view. |
| `public_b12x_paged_indexer` | no | b12x `0.20.0` still does not expose the paged sparse-indexer API expected by black-benediction's B12X indexer path. |
| `flashinfer_sm120_sparse_mla_packed` | no | PR3395-style packed SM120 sparse MLA path is not available in the installed official FlashInfer wheel state; use the PR3395 fork branch for that route. |
| `runtime_ds4_b12x_compressed_mla_adapter` | no | vLLM runtime does not expose the DS4-specific adapter in this branch/venv. |

## RTX Dependency And Component Refresh

| Probe | Result | Interpretation |
| --- | --- | --- |
| b12x `0.20.0` default install | Broke the current vLLM extension by moving Torch/Triton/CUDA runtime packages and downgrading NCCL. | Do not use the default resolver path for the dev venv. Keep the runtime stack pinned and install b12x as a no-deps experiment variable. |
| b12x `0.20.0` no-deps | `vllm._C` import and focused SM120 fallback tests pass; public DS4 b12x APIs import. | Dependency/API blocker is removed for component probes, but current vLLM still lacks runtime hooks. |
| FlashInfer `0.6.13rc1` matched jit-cache | `flashinfer-python/cubin==0.6.13rc1` and `flashinfer-jit-cache==0.6.13rc1+cu130` import without the version-check bypass; focused SM120 fallback tests pass. | Official rc1 is usable for component probes. Packed SM120 sparse MLA requires the PR3395 fork branch and an env-gated vLLM adapter. |
| b12x compressed MLA component | `real_c128`: b12x `0.432 ms`, vLLM old online packed `5.923 ms`, current D512 split+finish `0.209 ms`. | Public b12x compressed MLA is much better than the old packed helper, but still about `2.07x` slower than current D512 split+finish on RTX. Do not port it directly as the next endpoint route. |
| grouped-SWA D512 component | Candidates `640/1152`: split `0.627/1.382 ms`, grouped-SWA `0.575/0.824 ms`. | Component signal still exists, strongest at wider candidate counts, but the older separate-launch endpoint form already regressed. |
| grouped-stream component | Candidates `640/1152`: split `0.601/1.320 ms`, grouped stream `0.354/0.600 ms`. | Strong component signal for high-reuse C128A-style shape. Treat as dataflow evidence for a fused dual-stream/finish design, not as a direct endpoint drop-in. |

## Artifact Review Checklist

- Record exact vLLM commit and any local research branch name.
- Record FlashInfer, b12x, and black-benediction reference heads when used.
- Record route env vars, including DFlash, b12x, FlashInfer, sparse-MLA, MoE,
  and CUDA graph settings.
- Keep raw logs in artifacts, but summarize only public-safe relative paths in
  tracked docs.
- Mark runs with failed GSM8K, failed semantic gates, or driver-health signals
  as rejected evidence even if throughput improves.
