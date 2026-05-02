# Long Context Probe

- OK: `True`
- Detail: matched long-context sentinel terms
- Case: `kv_indexer_long_context`
- Variant: `mtp`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `0.0`
- Top P: `1.0`
- Prompt lines: `2400`
- Prompt SHA256: `6efb240c41fc863683dc01a836696e65ca77ec4ad09277a600cf30ed70b7167d`
- Prompt tokens: `74457`
- Completion tokens: `52`
- Total tokens: `74509`
- Finish reason: `stop`
- Required terms: `alpha-cobalt-17, beta-quartz-29, gamma-onyx-43`

## Assistant

Based solely on the provided context, the first indexer validation code is **alpha-cobalt-17**, the middle indexer validation code is **beta-quartz-29**, and the final indexer validation code is **gamma-onyx-43**.

## Prompt Excerpt

### Head

```text
You are validating long-context retrieval for DeepSeek V4.
Read the full context. The final answer must use only facts found in it.
Do not claim that the source article or context is missing.

Line 0001: subsystem=01; shard=01; checksum=0037; stable filler for long-context cache-layout validation.
Line 0002: subsystem=02; shard=02; checksum=0074; stable filler for long-context cache-layout validation.
Line 0003: subsystem=03; shard=03; checksum=0111; stable filler for long-context cache-layout validation.
Line 0004: subsystem=04; shard=04; checksum=0148; stable filler for long-context cache-layout validation.
```

### Tail

```text
Line 2396: subsystem=16; shard=18; checksum=0869; stable filler for long-context cache-layout validation.
Line 2397: subsystem=00; shard=19; checksum=0906; stable filler for long-context cache-layout validation.
Line 2398: subsystem=01; shard=20; checksum=0943; stable filler for long-context cache-layout validation.
Line 2399: subsystem=02; shard=21; checksum=0980; stable filler for long-context cache-layout validation.
Line 2400: subsystem=03; shard=22; checksum=0008; stable filler for long-context cache-layout validation.

Final task:
In one concise paragraph, list the first, middle, and final indexer validation codes from the context. Use the exact code strings.
```

## Usage JSON

```json
{
  "prompt_tokens": 74457,
  "total_tokens": 74509,
  "completion_tokens": 52,
  "prompt_tokens_details": null
}
```
