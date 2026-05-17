# MTP=1 Stability Follow-up (2026-05-17)

Side study, **not part of the regression baseline matrix**. Triggered by the
known MTP=1 NCCL allgather hang noted in earlier baselines; the goal was to
verify whether upgrading to `nvidia-nccl-cu13 2.30.4` (which fixed the DGX
Spark GB10 reliability issue) also closes this hang.

## Hardware / Software

Same workstation as the primary `v6b` baseline (2× NVIDIA RTX PRO 6000
Blackwell Workstation Edition, vLLM at `c92696943`, NCCL 2.30.4,
PyTorch 2.11.0+cu130, Triton 3.6.0). Only the speculative config differs:

```
--speculative_config {"method":"mtp","num_speculative_tokens":1}
```

`serve_command.sh` is included verbatim for full reproducibility.

## Result: hang reproduced under sustained multi-stream load

| Phase | Exit | Notes |
| --- | ---: | --- |
| `server_startup` | 0 | OK |
| `acceptance` | 1 | 6/8 sub-gates OK (toolcall15 + pytest exit 1, same pattern as nomtp/mtp2 — expected partial pass rate) |
| `long_context_probe` | 0 | Sentinel retrieval passed at 1900 lines / 58,957 tokens |
| `bench_hf_mt_bench` | 1 | **HANG @ c=4** (see `bench_hf_mt_bench/bench.json`) |
| `eval_gsm8k` | 143 | SIGTERM (server already dead) |
| `decode_profile` | 0 | Wrapper restarted serve cleanly; single-stream profile captured |

Single-stream / low-concurrency work runs to completion. The hang is gated on
sustained multi-stream load with MTP draft K=1.

## NCCL hang signature

Reproduced verbatim:

```
[rank1]:[E517 20:17:34.053343342 ProcessGroupNCCL.cpp:689] [Rank 1] Watchdog
  caught collective operation timeout: WorkNCCL(SeqNum=1901719,
  OpType=_ALLGATHER_BASE, NumelIn=387840, NumelOut=775680, Timeout(ms)=600000)
  ran for 600068 milliseconds before timing out.
```

Stack: `tensor_model_parallel_all_gather` → `_gather_logits` →
`LogitsProcessor.forward` → `compute_logits` in `deepseek_v4.py:1682`.

Full extract: `nccl_hang_evidence/serve_log_excerpt.txt`.

## Conclusion

Upgrading to NCCL 2.30.4 **does not fix this hang**. The bug appears to be on
the vLLM side (spec-decode K=1 collective ordering or logits-allgather
interaction), not pure NCCL. Per the project's MTP variant policy
(`project_baseline_mtp_variant_policy.md`), MTP=1 remains opt-in only and is
not part of the default regression matrix (`B200_BASELINE_VARIANTS=nomtp,mtp`).
Production-recommended config remains **MTP=2** (covered by the primary `mtp`
variant in this bundle).

## Useful data this run still produced

Even though `bench_hf_mt_bench` aborted at c=4, the captures up to that point
are usable:

| Concurrency | Output tok/s | TPOT ms | Accept rate | Status |
| ---: | ---: | ---: | ---: | --- |
| 1 | 148.85 | 6.44 | 86.76% | ok |
| 2 | 242.66 | 7.76 | 86.36% | ok |
| 4 | 0.22 | 10.13 | 96.88% | **hang** (4/80 completed in 300 s) |
| 8/16/24 | – | – | – | skipped |

MTP=1 at c=1/c=2 is comparable to MTP=2 in single-stream wall time, but the
acceptance length is lower (1.86–1.87 vs MTP=2's 2.40), which is consistent
with a smaller speculative budget. The c=4 hang is the dominant signal.

`decode_profile/torch_kernel_summary.md` captures kernel-time distribution
during single-stream decode (no hang). It's directly comparable to
`v6b/.../decode_profile/torch_kernel_summary.md` for kernel-level analysis.

`long_context_probe/long_context_probe.md` confirms MTP=1 sentinel retrieval
works at 58k tokens prompt (low-concurrency long-context is unaffected by the
hang).
