# Artifacts

Use relative paths only. Do not add private hostnames, user names, IP
addresses, tokens, or absolute model-cache locations.

## Baseline Artifacts

| Purpose | Relative artifact |
| --- | --- |
| RTX PR stable preview cold OSL=1 and GSM8K | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_clean_mtp_noep_20260612080629` |
| RTX PR stable preview OSL=128 supplement | `artifacts/codex_pr_stable_preview_f32247a/2x_rtx_pro_6000_sm120/rtx_current_pr_short_throughput_mtp_noep_20260612084721` |
| GB10 forum53 MTP2 EP-off C=2 prefix-cache gate | `artifacts/codex_pr_stable_preview_f32247a/2x_gb10_sm121/gb10_forum53_mtp2_epoff_c2_gmem0685_mml81920/20260612074113` |

## Future Route Artifacts

Add one row per route run:

| Route | Branch/commit | Dependency head | EP | Prefix cache | Artifact |
| --- | --- | --- | --- | --- | --- |
| _pending_ | | | | | |

## Cleanup Notes

On 2026-06-12, old clean temporary dependency and vLLM clones under `tmp/`
were removed after checking that they were not referenced by tracked notes and
had no unique dirty worktree state. The preserved data is the artifact evidence
above plus the current local checkouts.
