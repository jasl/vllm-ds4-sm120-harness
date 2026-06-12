# Artifacts

Use relative paths only. Do not add private hostnames, user names, IP
addresses, tokens, or absolute model-cache locations.

## Baseline Artifacts

| Purpose | Relative artifact |
| --- | --- |
| RTX PR stable preview cold OSL=1 and GSM8K | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_clean_mtp_noep_20260612080629` |
| RTX PR stable preview OSL=128 supplement | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_short_throughput_mtp_noep_20260612084721` |
| GB10 forum53 MTP2 EP-off C=2 prefix-cache gate | `artifacts/codex_pr_stable_preview_f32247a/2x_gb10_sm121/gb10_forum53_mtp2_epoff_c2_gmem0685_mml81920/20260612074113` |

## Bottleneck Runs

| Run | Branch/commit | Hardware | EP | Prefix cache | Artifact |
| --- | --- | --- | --- | --- | --- |
| RTX EP-off sparse attribution control | `591b71bed0` | SM120 RTX PRO 6000 x2 | off | disabled | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_bottleneck_attribution/20260613000055` |
| RTX EP-on attribution comparison | `f32247a5a6` | SM120 RTX PRO 6000 x2 | on | disabled | _pending_ |
| RTX GSM8K correctness guard | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| RTX local quality expansion | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| GB10 sparse attribution confirmation | candidate branch | SM121 GB10 x2 | off | disabled | _pending_ |
| GB10 forum53 prefix-cache gate | candidate branch | SM121 GB10 x2 | off | enabled | _pending_ |

## Partial Or Rejected Evidence

| Run | Branch/commit | Relative artifact | Reason |
| --- | --- | --- | --- |
| RTX EP-off performance-only control | `e164b76501` | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_bottleneck_attribution/20260612233142` | Benchmarks passed, but sparse stats row counts were zero because the diagnostics commit was missing from the dev branch. Do not use for sparse-MLA attribution. |

## Latest RTX Attribution Snapshot

| Input length | Sparse rows | Input tok/s C=1 / C=2 / C=4 | Mean TTFT ms C=1 / C=2 / C=4 | P99 TTFT ms C=1 / C=2 / C=4 |
| ---: | ---: | --- | --- | --- |
| 4096 | 2370 | 6241.52 / 6375.10 / 6362.72 | 656.46 / 1205.31 / 2089.68 | 669.53 / 1296.57 / 2582.43 |
| 16384 | 8706 | 8080.89 / 7104.17 / 5938.92 | 2027.05 / 4444.21 / 9439.91 | 2037.59 / 4647.73 / 12000.63 |
| 65536 | 34050 | 7576.42 / 6610.62 / 6541.33 | 8649.86 / 18819.34 / 33233.61 | 8774.34 / 20791.38 / 41515.80 |
| 124000 | 64850 | 6835.25 / 6179.15 / 6185.31 | 18141.62 / 37957.72 / 66063.01 | 18357.06 / 41619.08 / 81513.10 |

## Artifact Review Checklist

- Record exact vLLM commit and any local research branch name.
- Record FlashInfer, b12x, and black-benediction reference heads when used.
- Record route env vars, including DFlash, b12x, FlashInfer, sparse-MLA, MoE,
  and CUDA graph settings.
- Keep raw logs in artifacts, but summarize only public-safe relative paths in
  tracked docs.
- Mark runs with failed GSM8K, failed semantic gates, or driver-health signals
  as rejected evidence even if throughput improves.
