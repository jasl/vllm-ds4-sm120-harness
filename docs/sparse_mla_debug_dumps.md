# Sparse MLA Debug Dumps

DeepSeek V4 sparse MLA dumps are an optional diagnostic artifact for kernel and
KV-cache correctness work. They are intentionally off by default because raw
tensor payloads can be large and are not needed for normal acceptance runs.

## Capture Policy

- Do not enable sparse MLA dumps during normal baseline extraction.
- On storage-constrained hosts such as rented B200 instances, keep the file
  count and layer set small. Prefer metadata summaries unless a specific raw
  tensor is needed.
- On storage-rich development hosts, it is reasonable to retain larger raw
  `.pt` dump windows locally while narrowing the failing layer, step, or branch.
- Keep raw `.pt` tensor payloads in the run artifact directory. Copy them only
  when a specific failure needs offline analysis.
- Public baseline bundles should include summaries, not raw tensor dumps.

## Recommended Shape

A useful dump records one decode boundary at a time:

- metadata: layer id, tensor-parallel rank, compress ratio, branch, step,
  block sizes, top-k sizes, and attention dimensions
- tensors: post-RoPE `q`, materialized logical KV candidates, validity mask,
  compressed slot ids, top-k lens, SWA lens, sequence lens, block table,
  attention sink, actual output, reference output, and absolute diff

The diagnostic hook should compare the optimized attention output with a
PyTorch sparse-attention reference at capture time and write a small metadata
JSON next to the raw tensor payload.

## Summarize Dumps

Use the harness summary command after a run:

```bash
python -m ds4_harness.cli sparse-mla-dump-report \
  --dump-dir artifacts/manual/sparse_mla_dumps \
  --json-output artifacts/manual/sparse_mla_dump_summary.json \
  --markdown-output artifacts/manual/sparse_mla_dump_summary.md
```

The summary references tensor files by name only. This keeps reports small and
makes them safe to keep with other run artifacts while leaving raw payloads
available for selective copy.
