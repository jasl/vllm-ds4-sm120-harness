# Artifacts

Use relative paths only. Do not add private hostnames, user names, IP
addresses, tokens, or absolute model-cache locations.

## Baseline Artifacts

| Purpose | Relative artifact |
| --- | --- |
| RTX PR stable preview cold OSL=1 and GSM8K | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_clean_mtp_noep_20260612080629` |
| RTX PR stable preview OSL=128 supplement | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_short_throughput_mtp_noep_20260612084721` |
| GB10 forum53 MTP2 EP-off C=2 prefix-cache gate | `artifacts/codex_pr_stable_preview_f32247a/2x_gb10_sm121/gb10_forum53_mtp2_epoff_c2_gmem0685_mml81920/20260612074113` |

## Planned Bottleneck Runs

| Run | Branch/commit | Hardware | EP | Prefix cache | Artifact |
| --- | --- | --- | --- | --- | --- |
| RTX EP-off sparse attribution control | `f32247a5a6` | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| RTX EP-on attribution comparison | `f32247a5a6` | SM120 RTX PRO 6000 x2 | on | disabled | _pending_ |
| RTX GSM8K correctness guard | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| RTX local quality expansion | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| GB10 sparse attribution confirmation | candidate branch | SM121 GB10 x2 | off | disabled | _pending_ |
| GB10 forum53 prefix-cache gate | candidate branch | SM121 GB10 x2 | off | enabled | _pending_ |

## Artifact Review Checklist

- Record exact vLLM commit and any local research branch name.
- Record FlashInfer, b12x, and black-benediction reference heads when used.
- Record route env vars, including DFlash, b12x, FlashInfer, sparse-MLA, MoE,
  and CUDA graph settings.
- Keep raw logs in artifacts, but summarize only public-safe relative paths in
  tracked docs.
- Mark runs with failed GSM8K, failed semantic gates, or driver-health signals
  as rejected evidence even if throughput improves.
