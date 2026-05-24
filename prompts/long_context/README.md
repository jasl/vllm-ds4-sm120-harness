# Long Context Prompt Samples

These long-context prompt samples are copied from the ds4.c test suite:

- `ds4_story_recall.txt`: story recall prompt copied from
  `tests/long_context_story_prompt.txt`
- `ds4_security_audit.txt`: security-audit prompt copied from
  `tests/long_context_security_prompt.txt`

Source: https://github.com/antirez/ds4, commit
`0cba357ca1bc0e7510421cc26888e420ea942123`.

The copied files are distributed under the ds4.c MIT license in
`LICENSE.ds4`.

Harness behavior:

- `ds4_story_recall.txt` has a semantic gate through the
  `ds4_story_recall_semantic` baseline phase: all sixteen `Name=number`
  assignments must be present in the assistant response.
- `ds4_security_audit.txt` is used as a realistic long agent/security prompt
  for latency and streaming observations. The harness copy is kept public-safe
  and should not be overwritten from a local working tree without reviewing
  paths and other environment-specific text.
- `frontier-context-sweep` may use both prompt files as fixed text sources; it
  measures prompt prefixes and does not apply the story semantic gate to partial
  prompts.
