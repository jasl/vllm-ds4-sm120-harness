# DeepSeek V4 Reference Inference Snapshot

This directory contains a local snapshot of the DeepSeek V4 Flash reference
inference files from:

https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/tree/main/inference

The upstream model repository is marked as MIT licensed on Hugging Face. The
license text copied for this snapshot is in `LICENSE`.

The files under `inference/` are reference material only. They are not imported
by `ds4_harness`, not used by wrapper scripts, and not part of the harness test
suite. When we need behavior from this implementation, derive small explicit
tests or notes in the harness/vLLM codebase instead of importing this snapshot
at runtime.

Use `SHA256SUMS` to verify the snapshot contents:

```bash
cd third_party/deepseek_v4_reference_inference
shasum -a 256 -c SHA256SUMS
```
