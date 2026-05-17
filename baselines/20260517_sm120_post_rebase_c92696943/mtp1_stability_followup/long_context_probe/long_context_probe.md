# Long Context Probe

- OK: `True`
- Detail: matched long-context sentinel terms
- Case: `kv_indexer_long_context`
- Variant: `mtp1`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `0.0`
- Top P: `1.0`
- Prompt lines: `1900`
- Prompt SHA256: `870ce7bcebfad836367c01f368f7f1ca87148ce5cb26ada6fc27c1433d4a5f61`
- Prompt tokens: `58957`
- Completion tokens: `70`
- Total tokens: `59027`
- Finish reason: `stop`
- Required terms: `alpha-cobalt-17, beta-quartz-29, gamma-onyx-43`

## Assistant

Based solely on the context provided, the first indexer validation code is **alpha-cobalt-17** (line 0017), the middle indexer validation code is **beta-quartz-29** (line 0950), and the final indexer validation code is **gamma-onyx-43** (line 1887).

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
Line 1896: subsystem=09; shard=11; checksum=0531; stable filler for long-context cache-layout validation.
Line 1897: subsystem=10; shard=12; checksum=0568; stable filler for long-context cache-layout validation.
Line 1898: subsystem=11; shard=13; checksum=0605; stable filler for long-context cache-layout validation.
Line 1899: subsystem=12; shard=14; checksum=0642; stable filler for long-context cache-layout validation.
Line 1900: subsystem=13; shard=15; checksum=0679; stable filler for long-context cache-layout validation.

Final task:
In one concise paragraph, list the first, middle, and final indexer validation codes from the context. Use the exact code strings.
```

## Usage JSON

```json
{
  "prompt_tokens": 58957,
  "total_tokens": 59027,
  "completion_tokens": 70,
  "prompt_tokens_details": null
}
```
