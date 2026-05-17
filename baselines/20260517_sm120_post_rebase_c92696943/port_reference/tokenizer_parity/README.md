# Tokenizer Parity Reference

Token-ID + SHA-256 snapshots for the DSv4 tokenizer applied to a fixed
12-prompt × 4-mode matrix. Used by port teams (SGLang, TokenSpeed, downstream
forks) to verify their tokenizer wrapping produces identical token ids to
this revision's vLLM `tokenizer_mode=deepseek_v4` path.

## Files

- `tokenizer_parity.json` — full data: per-prompt × per-mode entry with the
  raw text, the token id list, the decoded round-trip, and the SHA-256 of the
  token id list.
- `tokenizer_parity.md` — human-readable summary table.

## Modes

| Mode | What |
| --- | --- |
| `raw` | `tokenize(prompt)` — no chat wrapping |
| `chat_chat` | `apply_chat_template(messages=[{user: prompt}], chat_template_kwargs={"thinking": False})` |
| `chat_thinking` | same, but `{"thinking": True}` |
| `chat_thinking_max` | same, but `{"thinking": True} + reasoning_effort=max` (think-max shape) |

## Reproducing

```bash
python3 scripts/dump_tokenizer_parity.py \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --output-dir <out>
```

CPU-only, ~20 seconds. Outputs identical SHA-256 hashes on any host with the
same HF tokenizer revision.

## Why this matters

vLLM's DSv4 chat template wraps reasoning differently from the model's stock
template (the `chat_template_kwargs.thinking` shape we use is vLLM-specific).
Port teams reimplementing the chat-template path can hit this reference to
confirm byte-exact token output before claiming parity.
