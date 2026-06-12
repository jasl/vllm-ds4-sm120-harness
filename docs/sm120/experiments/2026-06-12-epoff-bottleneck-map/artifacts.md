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
| RTX EP-on attribution comparison | `f32247a5a6` | SM120 RTX PRO 6000 x2 | on | disabled | _pending_ |
| RTX GSM8K correctness guard | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| RTX local quality expansion | candidate branch | SM120 RTX PRO 6000 x2 | off | disabled | _pending_ |
| GB10 sparse attribution confirmation | candidate branch | SM121 GB10 x2 | off | disabled | _pending_ |
| GB10 forum53 prefix-cache gate | candidate branch | SM121 GB10 x2 | off | enabled | _pending_ |

## Partial Or Rejected Evidence

| Run | Branch/commit | Relative artifact | Reason |
| --- | --- | --- | --- |
| RTX EP-off performance-only control | `e164b76501` | `artifacts/main/2x_rtx_pro_6000_sm120/sm120_epoff_bottleneck_attribution/20260612233142` | Benchmarks passed, but sparse stats row counts were zero because the diagnostics commit was missing from the dev branch. Do not use for sparse-MLA attribution. |
| RTX b12x 0.20 default dependency resolver | `591b71bed0` | `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_b12x_0200_upgrade` | Default install pulled Torch/Triton/CUDA runtime changes and downgraded NCCL; `vllm._C` failed with a Torch ABI symbol error. Runtime packages were restored and b12x was kept as a no-deps experiment variable. |
| RTX FlashInfer 0.6.13rc1 no-deps probe | `591b71bed0` | `artifacts/main/2x_rtx_pro_6000_sm120/dependency_snapshots/20260613_flashinfer_0613rc1_nodeps` | Superseded mismatch probe: import failed because `flashinfer-jit-cache` stayed at `0.6.12+cu130`. `FLASHINFER_DISABLE_VERSION_CHECK=1` bypasses that check for probing, and installing `flashinfer-jit-cache==0.6.13rc1+cu130` fixes the mismatch. |
| RTX FlashInfer 0.6.13rc1 packed MLA probe | `591b71bed0` | `artifacts/main/2x_rtx_pro_6000_sm120/flashinfer_packed_mla_probe/20260613_fi0613rc1_matched` | The matched rc1 wheel/jit-cache state imports normally, but both packed cases fail with `ModuleNotFoundError` because official rc1 does not expose `flashinfer.sparse_mla_sm120`. |

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
| `flashinfer_sm120_sparse_mla_packed` | no | PR3395-style packed SM120 sparse MLA path is not available in the installed FlashInfer. |
| `runtime_ds4_b12x_compressed_mla_adapter` | no | vLLM runtime does not expose the DS4-specific adapter in this branch/venv. |

## RTX Dependency And Component Refresh

| Probe | Result | Interpretation |
| --- | --- | --- |
| b12x `0.20.0` default install | Broke the current vLLM extension by moving Torch/Triton/CUDA runtime packages and downgrading NCCL. | Do not use the default resolver path for the dev venv. Keep the runtime stack pinned and install b12x as a no-deps experiment variable. |
| b12x `0.20.0` no-deps | `vllm._C` import and focused SM120 fallback tests pass; public DS4 b12x APIs import. | Dependency/API blocker is removed for component probes, but current vLLM still lacks runtime hooks. |
| FlashInfer `0.6.13rc1` matched jit-cache | `flashinfer-python/cubin==0.6.13rc1` and `flashinfer-jit-cache==0.6.13rc1+cu130` import without the version-check bypass; focused SM120 fallback tests pass. | Official rc1 is usable for component probes, but packed SM120 sparse MLA is still unavailable from official wheels. |
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
