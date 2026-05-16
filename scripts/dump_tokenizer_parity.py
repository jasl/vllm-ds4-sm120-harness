#!/usr/bin/env python3
"""Dump DSv4-Flash tokenizer outputs on a fixed prompt set for port parity.

Why
---
Porting DSv4-Flash SM12x support to SGLang or TokenSpeed needs a tokenization
oracle: "for these N prompts, the DSv4 tokenizer produces these token IDs,
and the DSv4 chat template (under each thinking mode) wraps them like this."
A port that emits different token IDs has a tokenizer-side bug, not a
kernel-side bug — without this dump that distinction is hard to diagnose
end-to-end.

What
----
Produces a single JSON file under ``--output-dir`` containing, for each
prompt in ``prompts/tokenizer_parity.yaml`` (or the embedded default if the
file is absent), three entries:

  raw                    : tokenize(prompt) — no chat wrapping
  chat_chat              : apply_chat_template(messages=[{user: prompt}],
                                               chat_template_kwargs={"thinking": False})
  chat_thinking          : same, but {"thinking": True}
  chat_thinking_max      : same, but {"thinking": True} + reasoning_effort=max
                           (the form the harness sends for think-max requests)

Each entry has the prompt text, the token IDs as a list, the decoded string
round-trip (for diff inspection), and the SHA-256 of the token-id list (a
stable hash a port can compare against in CI).

Usage
-----
  python3 scripts/dump_tokenizer_parity.py \\
      --model deepseek-ai/DeepSeek-V4-Flash \\
      --output-dir artifacts/tokenizer_parity \\
      [--prompt-file prompts/tokenizer_parity.yaml]

The model checkpoint must be cached locally (we don't hit the network).

Output
------
  ${OUTPUT_DIR}/tokenizer_parity.json
  ${OUTPUT_DIR}/tokenizer_parity.md         # human-readable summary
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Embedded default prompt set — covers the shapes a port is most likely to
# stumble on (BPE merges, multi-byte UTF-8, tool-call markers, very short
# inputs). Keep this stable across runs so the parity hashes are diffable.
DEFAULT_PROMPTS: dict[str, str] = {
    "ascii_short": "Hello, world.",
    "ascii_medium": "Explain in one paragraph why DSv4 sparse MLA reduces KV bandwidth.",
    "ascii_long_punct": (
        "The 'so-called' rubber-meets-the-road question: do "
        "'<|extras|>'-style markers (e.g. \"<<DSML>>\", 'DSv4.2-flash') "
        "tokenize the same across vendors when wrapped in chat?"
    ),
    "zh_classic": "天工开物云：凡造竹纸，事出南方，而闽省独专其盛。",
    "zh_mixed": "DSv4-Flash 在 SM12x 上跑得很顺 —— 注意 \"_v_up_proj\" 这个 op。",
    "math_latex": r"Show that $\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}$.",
    "code_python": (
        "Write a Python 3 function `levenshtein(a: str, b: str) -> int` "
        "that returns the edit distance using dynamic programming."
    ),
    "code_with_brackets": (
        "Given the JSON `{\"a\": [1, 2, 3], \"b\": {\"c\": true}}`, "
        "return the value at JSONPath `$.b.c`."
    ),
    "tool_marker_inline": (
        "When the assistant emits `<｜DSML｜tool_calls>` it should be "
        "followed by a JSON object, not by reasoning."
    ),
    "newlines_and_tabs": "Line 1\n\tindented\nLine 3\r\nCRLF",
    "unicode_emoji_zwj": (
        "Family emoji: \U0001F468‍\U0001F469‍\U0001F467‍"
        "\U0001F466 — verify that ZWJ sequences stay intact."
    ),
    "very_short": "?",
}

# Per-mode chat_template_kwargs and extra args, mirroring
# `ds4_harness.generation.THINKING_MODE_EXTRA_BODY`.
CHAT_MODES: list[tuple[str, dict[str, Any]]] = [
    ("chat_chat", {"chat_template_kwargs": {"thinking": False}}),
    ("chat_thinking", {"chat_template_kwargs": {"thinking": True}}),
    (
        "chat_thinking_max",
        {
            "chat_template_kwargs": {"thinking": True},
            "reasoning_effort": "max",
        },
    ),
]


@dataclass(frozen=True)
class ParityRow:
    name: str
    mode: str
    prompt: str
    token_ids: tuple[int, ...]
    decoded: str
    sha256: str

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "mode": self.mode,
            "prompt": self.prompt,
            "token_ids": list(self.token_ids),
            "decoded_roundtrip": self.decoded,
            "sha256_of_token_ids": self.sha256,
            "num_tokens": len(self.token_ids),
        }


def _hash_tokens(token_ids: list[int]) -> str:
    # Hash the canonical comma-joined string so the port can reproduce
    # without depending on JSON whitespace quirks.
    payload = ",".join(str(tok) for tok in token_ids).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _tokenize_raw(tokenizer: Any, prompt: str) -> list[int]:
    encoded = tokenizer(prompt, add_special_tokens=False)
    return list(encoded["input_ids"])


def _tokenize_chat(
    tokenizer: Any,
    prompt: str,
    extra: dict[str, Any],
) -> list[int]:
    # DSv4-Flash's chat template doesn't ship in tokenizer_config.json; the
    # canonical implementation lives in `vllm/tokenizers/deepseek_v4_encoding.py`
    # under the function `encode_messages`. Use that directly so the parity
    # dump exactly matches what vLLM's `--tokenizer-mode deepseek_v4` would
    # produce server-side.
    from vllm.tokenizers.deepseek_v4_encoding import encode_messages

    chat_kwargs = dict(extra.get("chat_template_kwargs") or {})
    thinking = bool(chat_kwargs.get("thinking") or chat_kwargs.get("enable_thinking"))
    thinking_mode = "thinking" if thinking else "chat"
    reasoning_effort = extra.get("reasoning_effort") or chat_kwargs.get(
        "reasoning_effort"
    )

    messages = [{"role": "user", "content": prompt}]
    text = encode_messages(
        messages,
        thinking_mode=thinking_mode,
        reasoning_effort=reasoning_effort,
    )
    encoded = tokenizer(text, add_special_tokens=False)
    return list(encoded["input_ids"])


def _decode(tokenizer: Any, token_ids: list[int]) -> str:
    return tokenizer.decode(token_ids, skip_special_tokens=False)


def _load_prompts(prompt_file: Path | None) -> dict[str, str]:
    if prompt_file is None or not prompt_file.exists():
        return dict(DEFAULT_PROMPTS)
    # YAML loader is optional; we just want simple key->string parsing.
    try:
        import yaml  # type: ignore[import]
    except ImportError:
        print(
            f"warning: PyYAML missing, ignoring --prompt-file {prompt_file}",
            file=sys.stderr,
        )
        return dict(DEFAULT_PROMPTS)
    raw = yaml.safe_load(prompt_file.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SystemExit(f"--prompt-file {prompt_file} must be a YAML mapping")
    out = {}
    for k, v in raw.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise SystemExit(
                f"--prompt-file {prompt_file} entries must be str->str; "
                f"got {type(k).__name__}->{type(v).__name__}"
            )
        out[k] = v
    if not out:
        raise SystemExit(f"--prompt-file {prompt_file} produced an empty mapping")
    return out


def _render_summary_md(rows: list[ParityRow], model: str) -> str:
    lines = [
        "# Tokenizer Parity Dump",
        "",
        f"- Model: `{model}`",
        f"- Total prompts: {len({r.name for r in rows})}",
        f"- Modes: {sorted({r.mode for r in rows})}",
        "",
        "| Prompt | Mode | Tokens | SHA-256 (token IDs) |",
        "| --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row.name}` | `{row.mode}` | {len(row.token_ids)} | "
            f"`{row.sha256[:16]}...` |"
        )
    lines.append("")
    lines.append(
        "Hashes are SHA-256 over the comma-joined token-id list. "
        "A port should reproduce identical token IDs (and therefore hashes) "
        "to confirm tokenizer + chat-template parity."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Dump DSv4-Flash tokenizer outputs for a fixed prompt set, "
            "to be used as a parity oracle when porting to SGLang / TokenSpeed."
        )
    )
    parser.add_argument(
        "--model",
        default="deepseek-ai/DeepSeek-V4-Flash",
        help="HF model id or local checkpoint path",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write tokenizer_parity.{json,md} into",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=None,
        help="Optional YAML mapping of name -> prompt string. Falls back to "
        "the embedded DEFAULT_PROMPTS if absent.",
    )
    args = parser.parse_args()

    # transformers is the standard public tokenizer surface; the vllm
    # `tokenizer_mode=deepseek_v4` is server-side, not exposed for offline
    # tokenization. Falling back to AutoTokenizer is fine here because the
    # parity target is the public DSv4 BPE + chat-template artifact, which
    # `deepseek-ai/DeepSeek-V4-Flash` ships unmodified.
    from transformers import AutoTokenizer  # type: ignore[import]

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            args.model, trust_remote_code=True
        )
    except Exception as exc:  # noqa: BLE001
        print(f"error: failed to load tokenizer for {args.model}: {exc}", file=sys.stderr)
        return 2

    prompts = _load_prompts(args.prompt_file)

    rows: list[ParityRow] = []
    skipped_modes: list[str] = []

    for name in sorted(prompts):
        prompt = prompts[name]

        raw_ids = _tokenize_raw(tokenizer, prompt)
        rows.append(
            ParityRow(
                name=name,
                mode="raw",
                prompt=prompt,
                token_ids=tuple(raw_ids),
                decoded=_decode(tokenizer, raw_ids),
                sha256=_hash_tokens(raw_ids),
            )
        )

        for mode_name, mode_extra in CHAT_MODES:
            try:
                chat_ids = _tokenize_chat(tokenizer, prompt, mode_extra)
            except Exception as exc:  # noqa: BLE001
                # If the model's chat template is absent or rejects the
                # kwargs, record once per mode and continue with raw only.
                if mode_name not in skipped_modes:
                    print(
                        f"warning: chat-template mode `{mode_name}` failed "
                        f"({type(exc).__name__}: {exc}); skipping for all prompts",
                        file=sys.stderr,
                    )
                    skipped_modes.append(mode_name)
                continue
            rows.append(
                ParityRow(
                    name=name,
                    mode=mode_name,
                    prompt=prompt,
                    token_ids=tuple(chat_ids),
                    decoded=_decode(tokenizer, chat_ids),
                    sha256=_hash_tokens(chat_ids),
                )
            )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "tokenizer_parity.json"
    md_path = args.output_dir / "tokenizer_parity.md"

    json_payload = {
        "model": args.model,
        "prompt_count": len(prompts),
        "modes": ["raw", *[m for m, _ in CHAT_MODES if m not in skipped_modes]],
        "skipped_modes": skipped_modes,
        "rows": [row.to_json() for row in rows],
    }
    json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2))
    md_path.write_text(_render_summary_md(rows, args.model))

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print(f"rows: {len(rows)} ({len(prompts)} prompts × "
          f"{1 + len(CHAT_MODES) - len(skipped_modes)} modes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
