# Tokenizer Parity Dump

- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Total prompts: 12
- Modes: ['chat_chat', 'chat_thinking', 'chat_thinking_max', 'raw']

| Prompt | Mode | Tokens | SHA-256 (token IDs) |
| --- | --- | ---: | --- |
| `ascii_long_punct` | `raw` | 51 | `318049e6318f75fd...` |
| `ascii_long_punct` | `chat_chat` | 55 | `f9fcaa4993de6e14...` |
| `ascii_long_punct` | `chat_thinking` | 55 | `f4a814e10f66258a...` |
| `ascii_long_punct` | `chat_thinking_max` | 134 | `5d2057a00787553e...` |
| `ascii_medium` | `raw` | 14 | `d904edd57bb33db1...` |
| `ascii_medium` | `chat_chat` | 18 | `850b36ea83785dcb...` |
| `ascii_medium` | `chat_thinking` | 18 | `75c62350949b1ace...` |
| `ascii_medium` | `chat_thinking_max` | 97 | `31001a0ed2375b10...` |
| `ascii_short` | `raw` | 4 | `cc68ed676e98981c...` |
| `ascii_short` | `chat_chat` | 8 | `83af28dba1e3c39d...` |
| `ascii_short` | `chat_thinking` | 8 | `692401a120f65685...` |
| `ascii_short` | `chat_thinking_max` | 87 | `9402702dcdd9274a...` |
| `code_python` | `raw` | 31 | `8d35e3fded1555fc...` |
| `code_python` | `chat_chat` | 35 | `e1cf4555de457445...` |
| `code_python` | `chat_thinking` | 35 | `eb720d7143e5a5e1...` |
| `code_python` | `chat_thinking_max` | 114 | `f6ee477c17af63c2...` |
| `code_with_brackets` | `raw` | 36 | `160d7ac5c5c6f943...` |
| `code_with_brackets` | `chat_chat` | 40 | `e80f5c4d6a16fe44...` |
| `code_with_brackets` | `chat_thinking` | 40 | `b6a8faeedeba58ab...` |
| `code_with_brackets` | `chat_thinking_max` | 119 | `e6f6e99fe7a3033d...` |
| `math_latex` | `raw` | 28 | `18f8d05f1c6dc0a2...` |
| `math_latex` | `chat_chat` | 32 | `04c85c5aa1fcccc9...` |
| `math_latex` | `chat_thinking` | 32 | `8846c425e01b6d25...` |
| `math_latex` | `chat_thinking_max` | 111 | `e0d48a9ab843ee0f...` |
| `newlines_and_tabs` | `raw` | 15 | `5e7b057b75887a7d...` |
| `newlines_and_tabs` | `chat_chat` | 19 | `ef45a70692a2b784...` |
| `newlines_and_tabs` | `chat_thinking` | 19 | `6fc0f85b1a68eaad...` |
| `newlines_and_tabs` | `chat_thinking_max` | 98 | `6258d6824ec9b220...` |
| `tool_marker_inline` | `raw` | 23 | `807398461a3c8b4b...` |
| `tool_marker_inline` | `chat_chat` | 27 | `13315b01a649da81...` |
| `tool_marker_inline` | `chat_thinking` | 27 | `9edeef4b8282da15...` |
| `tool_marker_inline` | `chat_thinking_max` | 106 | `7d6c5a7fa2c7b24e...` |
| `unicode_emoji_zwj` | `raw` | 25 | `bbb1d9b80018f1f2...` |
| `unicode_emoji_zwj` | `chat_chat` | 29 | `35dd54702106e50c...` |
| `unicode_emoji_zwj` | `chat_thinking` | 29 | `5c8a60b567555190...` |
| `unicode_emoji_zwj` | `chat_thinking_max` | 108 | `f63426e292a285eb...` |
| `very_short` | `raw` | 1 | `c6f3ac57944a5314...` |
| `very_short` | `chat_chat` | 5 | `012a7742a421572b...` |
| `very_short` | `chat_thinking` | 5 | `69f13391cf5a7d1f...` |
| `very_short` | `chat_thinking_max` | 84 | `1da549b3b2745111...` |
| `zh_classic` | `raw` | 23 | `03fbfc4571b1556b...` |
| `zh_classic` | `chat_chat` | 27 | `b2a4b85f9558d090...` |
| `zh_classic` | `chat_thinking` | 27 | `df3b3f823b6e8a32...` |
| `zh_classic` | `chat_thinking_max` | 106 | `b3097004bfd4f4e9...` |
| `zh_mixed` | `raw` | 28 | `a707b9e38a893a15...` |
| `zh_mixed` | `chat_chat` | 32 | `9243ce6d1a195f59...` |
| `zh_mixed` | `chat_thinking` | 32 | `230ae93440945cd2...` |
| `zh_mixed` | `chat_thinking_max` | 111 | `b166e077b1090f05...` |

Hashes are SHA-256 over the comma-joined token-id list. A port should reproduce identical token IDs (and therefore hashes) to confirm tokenizer + chat-template parity.
