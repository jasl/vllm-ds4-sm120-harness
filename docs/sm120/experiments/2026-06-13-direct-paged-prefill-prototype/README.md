# Direct-Paged Sparse Prefill Prototype

Status: rejected
Date: 2026-06-13
Owner/context: first fork-independent sparse-prefill prototype on the current
SM120 development branch

## Question

Can a default-off direct paged sparse-prefill route improve the slow
non-indexed `mla_prefill_chunk` rows by skipping gather/combine and reading
selected compressed plus SWA candidates directly from page tables?

## Profile

- Hardware: dual RTX PRO 6000 / SM120.
- vLLM branch/commit: `codex/ds4-sm120-sparse-prefill-dev-20260613`
  `620c651203d`.
- Dependency or image identity: same RTX development venv as the current
  backend-parity work; b12x `0.20.0`, FlashInfer `0.6.13rc1`, matching
  FlashInfer jit-cache `0.6.13rc1+cu130`, NCCL `2.30.7`, Torch
  `2.11.0+cu130`.
- TP / PP / EP: TP=2, PP=1, EP disabled.
- MTP: MTP=2.
- FP8 KV: enabled.
- Prefix cache: disabled for the measured request; warmup stats include cached
  prefix rows and remain non-direct.
- CUDA graph mode: production default from the harness profile.
- `max_model_len`: harness default for the prefill-gap profile.
- `max_num_seqs`: 1.
- `max_num_batched_tokens`: 4096.
- Other route flags: `VLLM_DEEPSEEK_V4_DIRECT_PAGED_PREFILL=1` for the
  candidate, `0` for the paired control; sparse MLA stage timing enabled.

## Result

The route is functionally reachable but not performant. The candidate finished
the RTX smoke with `OK=True`, and stats recorded
`mla_prefill_direct_paged` rows, but the serial paged attention kernel is much
slower than both existing chunk rows and the indexed-D512 route.

Paired smoke result:

| Route | OK | Input tok/s | Mean TTFT ms | Stage total ms | Dominant stage | Sparse accumulate ms/M visits |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| control, direct off | yes | 4096.00 | 248.58 | 2069.72 | `gather_compressed_kv` | 2.88178 |
| direct paged on | yes | 1796.49 | 571.11 | 4584.29 | `sparse_accumulate` | 12.1998 |

Direct rows reached only about `3.97e7-4.09e7` sparse visits/s. The same run's
indexed-D512 rows reached about `7.21e8-1.19e9` sparse visits/s, and the
paired control's non-indexed chunk rows reached about `1.87e8-2.12e8` sparse
visits/s.

## Interpretation

Skipping gather/combine is still a plausible dataflow objective, but this
prototype proves that a decode-style serial paged loop is the wrong kernel
shape for prefill. It removes some staging work, yet loses far more in
`sparse_accumulate` throughput.

This is EP-off, prefix-cache-off RTX / SM120 evidence. GB10 / SM121 promotion
gates were intentionally not run because the RTX paired control is already a
hard performance rejection. Correctness promotion gates such as GSM8K are also
not useful for this exact prototype until the kernel is redesigned.

## Follow-Up

- Create or update decision:
  `docs/sm120/decisions/watchlist/2026-06-12-backend-parity-roadmap.md`.
- Rerun trigger: only rerun this route if the direct paged kernel is replaced
  by a tiled/indexed-D512-style score/value implementation rather than the
  current serial per-candidate loop.
- Next command or next owner: keep the env-gated code as an experimental
  branch reference, but move the next prototype toward a paged variant of the
  indexed-D512 split/finish design that preserves parallel candidate scoring.
