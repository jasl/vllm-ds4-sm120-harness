# Artifacts

Use relative paths only. Do not add private hostnames, user names, IP
addresses, tokens, or absolute model-cache locations.

## Reference Artifacts

| Purpose | Relative artifact |
| --- | --- |
| RTX PR stable preview cold OSL=1 and GSM8K | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_clean_mtp_noep_20260612080629` |
| RTX PR stable preview OSL=128 supplement | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_short_throughput_mtp_noep_20260612084721` |
| GB10 forum53 MTP2 EP-off C=2 prefix-cache gate | `artifacts/codex_pr_stable_preview_f32247a/2x_gb10_sm121/gb10_forum53_mtp2_epoff_c2_gmem0685_mml81920/20260612074113` |

## Planned Reproduction Runs

| Run | Branch/commit | Hardware | EP | Prefix cache | Artifact |
| --- | --- | --- | --- | --- | --- |
| black-benediction RTX endpoint reproduction | frozen `c6b2a7b187` or reviewed newer head | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| black-benediction RTX correctness guard | frozen `c6b2a7b187` or reviewed newer head | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| isolated B12X sparse-indexer probe | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| isolated B12X MoE probe | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| DFlash/SWA semantics probe | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| GB10 final confirmation | candidate branch | SM121 GB10 x2 | off | disabled/enabled as gate requires | _pending_ |

## Portability Checklist

- Confirm public b12x/FlashInfer APIs used by a mechanism are available in the
  target venv.
- Confirm the route dispatches through serve logs, not just imports.
- Preserve or recreate black-benediction's focused unit tests when porting a
  mechanism.
- Keep DFlash/speculative changes behind explicit controls until GSM8K and
  semantic gates pass.
- Reject any candidate that requires disabling `FULL_AND_PIECEWISE` or hiding
  GB10 driver-health signals.
