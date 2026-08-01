# FlashInfer 0.6.15.post1 → 0.6.16

Status: accepted
Date: 2026-08-02
Owner/context: `72f5a30158`, tag `sm120-pr-41834-stable-preview-20260802c`.

## Question

Is 0.6.16 safe to pin, and does it change anything measurable on SM12x?

## Why "the serve came up" is not an answer here

Every FlashInfer availability probe in `vllm/utils/flashinfer.py` is shaped

```python
try:
    from flashinfer.X import Y
except ImportError:
    return False
```

so a renamed or moved symbol does **not** raise. It returns `False`, DSv4 falls
back to the FlashMLA/Triton path, serve starts normally, GSM8K still passes, and
the only symptom is that the SM120 kernels this branch exists to enable have
stopped being used. A green gate run cannot detect that.

`scripts/flashinfer_symbol_contract.py` asserts the 12 symbols the DSv4 SM12x path
depends on, by name:

| symbol | needed by |
| --- | --- |
| `flashinfer.mla.trtllm_batch_decode_sparse_mla_dsv4` | `has_flashinfer_trtllm_sparse_mla_dsv4` — gates the SM120 decode class in `_select_dsv4_attn_cls` |
| `flashinfer.decode.trtllm_batch_decode_sparse_mla_dsv4` | `has_flashinfer_sparse_mla_sm120` |
| `flashinfer.decode.trtllm_batch_decode_with_kv_cache_mla` | `has_flashinfer_sparse_mla_sm120` |
| `flashinfer.autotuner.autotune` | `has_flashinfer_sparse_mla_sm120` |
| `flashinfer.mla._sparse_mla_sm120._SparseMLAPagedAttentionRunner` | `flashinfer_sm120_decode.py:142` — imported directly, so a rename here is an ImportError at decode time |
| `flashinfer.concat_ops.concat_mla_k` | `utils/flashinfer.py:585` |
| `flashinfer.{mm_fp4, mxfp4_quantize, nvfp4_quantize, SfLayout, bmm_fp8, mm_mxfp8}` | NVFP4 / MXFP4 / FP8 GEMM paths |

**All 12 present on 0.6.16.** Positive confirmation from the serve log too:
`flashinfer_sm120_decode.py:156 DeepSeek V4: using official FlashInfer SM120
packed sparse-MLA decode via the low-level runner` — the path is selected, not
silently bypassed.

## Result

Unit suite at `72f5a30158` — **byte-identical to 0.6.15.post1** section by
section:

| section | 0.6.15.post1 | 0.6.16 |
| --- | --- | --- |
| A. DSv4 kernels | 229 passed, 12 skipped | 229 passed, 12 skipped |
| B. DSv4 attention backends | 6 passed | 6 passed |
| C. spec decode / dspark config | 40 passed | 40 passed |
| D. kv offload | 715 passed, 1 skipped | 715 passed, 1 skipped |
| E. core scheduler + prefix cache | 232 passed, 1 failed | 232 passed, 1 failed |
| F. kernel warmup | 2 passed | 2 passed |
| G. tokenizer / prompt encoding | 44 passed | 44 passed |
| H. functionalization pass | 16 passed | 16 passed |

(E's failure needs 2 GPUs in one node; GB10 has one each.)

GB10 2-node gates, 0731 + DSpark nst=5:

| gate | 0.6.15.post1 (`4450216c9e`) | 0.6.16 (`72f5a30158`) |
| --- | --- | --- |
| #19 instruction-following | PASS | PASS |
| long-context recall, c=1 | 2/2 | 2/2 |
| GSM8K flexible / strict | 0.9462 / 0.9424 | 0.9431 / 0.9371 |
| illegal-access lines | 0 | 0 |
| available KV | 17.06 GiB | 18.56 GiB |
| engine init | 164.28 s | 105.02 s (cold JIT cache) |

The GSM8K difference is −0.31 pp, well inside this gate's ~1.1 pp single-run
spread. Not a finding.

## The nccl trap

**Installing FlashInfer drags `nvidia-nccl-cu13` back to 2.29.7.** It must be
re-pinned to 2.30.7 on every node afterwards; a per-node mismatch hangs the NCCL
handshake at serve startup. This is the same trap a plain `-e .` install sets, and
the rollout script now asserts both the version match and the re-pin rather than
printing them for a human to notice.

## Two claims from the release notes I did NOT verify

- **On-disk JIT caching, "cold start 3–30 ms".** Suggestive but unconfirmed:
  engine init was 105 s here against 164 s on 0.6.15, *with a cold cache*, which
  is the right direction. But n=1, startup time has many contributors, and the two
  runs are different builds. Measuring this properly means clearing
  `~/.cache/flashinfer` and timing first kernel use on both versions.
- **"~1.6 GB smaller installed size".** Not checkable here — both venvs are on
  0.6.16 now and no 0.6.15 cubin tree survives to diff against. For reference the
  0.6.16 `flashinfer_cubin` tree is 4.5 GB and `flashinfer` is 98 MB.

Neither is repeated as fact anywhere in this branch's docs.

## Open

- available KV read 18.56 GiB against 17.06 GiB on 0.6.15, i.e. +1.5 GiB — just
  above the ~1 GiB figure this branch has been treating as the noise floor, and
  therefore undecidable from one reading per version. The GSM8K x3 matrix running
  after this does six serve startups at one head, which will produce the first
  real distribution for this metric instead of a single sample.
- The JIT cold-start claim, if it matters for startup latency work.
