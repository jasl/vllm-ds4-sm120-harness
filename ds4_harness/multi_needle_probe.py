"""Multi-needle long-context retrieval, with distractors.

Why this exists: the single-needle matrix in
``docs/sm120/experiments/2026-08-05-needle-recall-matrix-364k`` returned 50/50 up to
364,073 tokens, where the ``index_topk: 512`` budget covers 0.14% of the context. That
is a ceiling result on a probe that is too easy for the claim it was aimed at. One
needle is exact-match retrieval: the filler lines are
``archive=11; section=42; checksum=5502`` and the needle is a natural-language sentence,
so the scoring function can find it by *novelty*, never having to discriminate.

Two changes make the task harder than single-needle retrieval:

* **N needles at once**, spread across the haystack.
* **Distractors in the same surface form** — lines identical in shape to a needle but
  keyed to a vault nobody asked about. Novelty detection cannot separate these; only
  reading the key can. This is what turns retrieval into discrimination.

Scoring is per needle, not per request, so a run degrades continuously (7/8, 5/8, ...)
instead of collapsing to a single pass/fail. A probe whose only outcomes are 0 and 1
cannot locate a knee.

**This probe does NOT stress the ``index_topk`` budget, and cannot.** It was built to,
on the theory that N needles must enter the top-512 simultaneously and therefore compete
— predicting that doubling ``index_topk`` would roughly double the needles recoverable.
Measured 2026-08-05: 72 needles + 72 distractors are recovered 72/72 at 30K, 123K and
364K context with ``index_topk=512``, which is ~1080 tokens of "must attend" content
against a 512 budget. The premise was wrong. Top-k is selected **per query token**, so
the token emitting needle #50's code re-selects its own top-512 and never contends with
the token that emitted needle #1's. Piling facts into the context cannot exhaust a
per-token budget; only a single query token needing more than ``index_topk`` relevant
positions at once could, and this construction never produces that.

Use it for retrieval-under-distraction, which is what it actually measures. See
``docs/sm120/experiments/`` for the ``index_topk`` A/B this refuted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

Json = dict[str, object]

# Keys are spelled-out words rather than single letters: a single letter appears inside
# ordinary filler text constantly, so a response could "contain" it by accident and
# score a hit that never happened.
#
# Generated rather than hand-listed. A fixed list of 24 caps the probe at 24 keys
# total, which is far below what this experiment needs: the budget under test is 512
# TOKENS and a fact line is ~15 tokens, so the interesting region starts around 34
# needles and a useful ladder runs past 70. The first version of this file had exactly
# that 24-key ceiling and every cell above it would have raised ValueError.
_KEY_STEMS = (
    "AMBER", "BASALT", "CINNABAR", "DOLOMITE", "EMERALD", "FELDSPAR",
    "GARNET", "HEMATITE", "IOLITE", "JASPER", "KYANITE", "LAZURITE",
    "MALACHITE", "NEPHRITE", "OBSIDIAN", "PERIDOT", "QUARTZ", "RHODONITE",
    "SPINEL", "TOPAZ", "ULEXITE", "VARISCITE", "WULFENITE", "XENOTIME",
)
# STEM-NN stays a single whitespace-free token-ish word, so the scoring regex keeps
# working and no stem is ever a prefix of another key.
_VAULT_KEYS = tuple(
    f"{stem}-{suffix:02d}" for suffix in range(1, 9) for stem in _KEY_STEMS
)
_MIN_LINE_COUNT = 128
_CODE_DIGITS = 6


@dataclass(frozen=True)
class MultiNeedlePrompt:
    """A haystack plus the answer key. Frozen: the expected answers must not drift."""

    text: str
    line_count: int
    needles: tuple[tuple[str, str], ...]      # (vault key, code) that ARE asked about
    distractors: tuple[tuple[str, str], ...]  # same form, never asked about
    needle_lines: tuple[int, ...]

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def _filler_line(index: int) -> str:
    return (
        f"Line {index:04d}: archive={index % 31:02d}; "
        f"section={index % 47:02d}; checksum={(index * 131) % 9973:04d}; "
        "stable filler for long-context needle retrieval."
    )


def _fact_line(index: int, key: str, code: str) -> str:
    return f"Line {index:04d}: The access code for vault {key} is {code}."


def _spread_positions(line_count: int, count: int) -> list[int]:
    """Place items evenly across the body, avoiding the very first and last lines.

    Even spread matters: clustering the needles would let one attention window cover all
    of them and would measure something other than the budget.
    """
    if count < 1:
        return []
    lo, hi = 2, max(3, line_count - 1)
    if count == 1:
        return [(lo + hi) // 2]
    step = (hi - lo) / (count - 1)
    return [int(round(lo + step * i)) for i in range(count)]


def build_multi_needle_prompt(
    *,
    line_count: int,
    needle_count: int = 8,
    distractor_count: int = 8,
    seed: int = 1234,
) -> MultiNeedlePrompt:
    """Build a haystack with ``needle_count`` asked-about facts and ``distractor_count`` decoys."""
    if line_count < _MIN_LINE_COUNT:
        raise ValueError(f"line_count must be at least {_MIN_LINE_COUNT}, got {line_count}")
    if needle_count < 1:
        raise ValueError(f"needle_count must be positive, got {needle_count}")
    total_keys = needle_count + distractor_count
    if total_keys > len(_VAULT_KEYS):
        raise ValueError(
            f"need {total_keys} distinct vault keys but only {len(_VAULT_KEYS)} exist"
        )
    if total_keys * 2 > line_count:
        raise ValueError(
            f"line_count {line_count} is too small to host {total_keys} facts"
        )

    rng = random.Random(seed)
    keys = rng.sample(_VAULT_KEYS, total_keys)
    codes = rng.sample(range(10 ** (_CODE_DIGITS - 1), 10**_CODE_DIGITS), total_keys)
    needles = tuple((keys[i], str(codes[i])) for i in range(needle_count))
    distractors = tuple(
        (keys[needle_count + i], str(codes[needle_count + i]))
        for i in range(distractor_count)
    )

    # Interleave needles and distractors across the body so a distractor sits near each
    # needle; adjacency is what makes discrimination necessary rather than optional.
    slots = _spread_positions(line_count, total_keys)
    rng.shuffle(slots)
    needle_slots = sorted(slots[:needle_count])
    distractor_slots = sorted(slots[needle_count:])
    placed: dict[int, tuple[str, str]] = {}
    for slot, fact in zip(needle_slots, needles):
        placed[slot] = fact
    for slot, fact in zip(distractor_slots, distractors):
        placed[slot] = fact

    asked = ", ".join(key for key, _ in needles)
    rows = [
        "You are solving a multi-key retrieval task.",
        "Use only facts found in the provided context.",
        "Several vaults are listed. Report only the ones asked for.",
        "",
    ]
    rows.extend(
        _fact_line(index, *placed[index]) if index in placed else _filler_line(index)
        for index in range(1, line_count + 1)
    )
    rows.extend(
        [
            "",
            f"Question: What are the access codes for these vaults: {asked}?",
            "Answer with one line per vault in the format 'VAULT=CODE'.",
            "Do not include vaults that were not asked about.",
        ]
    )
    return MultiNeedlePrompt(
        text="\n".join(rows),
        line_count=line_count,
        needles=needles,
        distractors=distractors,
        needle_lines=tuple(needle_slots),
    )


def score_multi_needle_response(text: str, prompt: MultiNeedlePrompt) -> Json:
    """Per-needle scoring, plus a distractor-leak count.

    A hit requires the key and its code to appear *paired* (``KEY=CODE``, ``KEY: CODE``,
    ``KEY is CODE``). Searching for the code alone would credit a model that emitted every
    six-digit number it saw, and searching for the key alone would credit one that merely
    echoed the question.
    """
    upper = text.upper()

    def paired(key: str, code: str) -> bool:
        # Small separator windows only. A permissive gap would pair a key with a code
        # mentioned lines later and manufacture hits; the optional IS covers the
        # "The code for KEY is CODE" phrasing that models actually produce.
        pattern = (
            rf"\b{re.escape(key)}\b[^0-9A-Za-z]{{0,4}}"
            rf"(?:IS\b[^0-9A-Za-z]{{0,4}})?{re.escape(code)}\b"
        )
        return re.search(pattern, upper) is not None

    hits, misses = [], []
    for key, code in prompt.needles:
        (hits if paired(key, code) else misses).append(key)

    # Reporting a vault nobody asked about is a distinct failure from missing one: it
    # means the wrong line won the attention budget, not that no line did.
    leaked = [key for key, code in prompt.distractors if paired(key, code)]
    return {
        "needles_total": len(prompt.needles),
        "needles_hit": len(hits),
        "hit_keys": hits,
        "missed_keys": misses,
        "distractors_leaked": len(leaked),
        "leaked_keys": leaked,
    }


def default_max_tokens(needle_count: int) -> int:
    """Output budget that cannot truncate the answer.

    An answer line is `KEY-NN=NNNNNN`, about 11 tokens. A fixed 512 silently capped
    recall at ~55 lines: 72 needles scored 55/72 at 30K, 123K AND 364K context --
    identical at every length, because a truncation ceiling does not care how long the
    haystack is. Raising it to 1024 recovered 72/72. Scale with the answer, not with a
    constant, and see `finish_reason` in every row for when it still is not enough.
    """
    return max(512, needle_count * 16 + 256)


def _post_chat(
    *, base_url: str, model: str, prompt: str, max_tokens: int, timeout: float
) -> tuple[Json, float]:
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0,
            "thinking": {"type": "disabled"},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    started = time.time()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read())
    return payload, time.time() - started


def _assistant_text(payload: Json) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        return ""
    return str(message.get("content") or "")


def _finish_reason(payload: Json) -> str | None:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    choice = choices[0]
    if not isinstance(choice, dict):
        return None
    reason = choice.get("finish_reason")
    return str(reason) if reason is not None else None


def run_multi_needle_probe(
    *,
    base_url: str,
    model: str,
    line_counts: list[int],
    needle_count: int = 8,
    distractor_count: int = 8,
    repeat_count: int = 2,
    max_tokens: int | None = None,
    timeout: float = 3600.0,
    seed: int = 1234,
    post_func=None,
) -> list[Json]:
    """Run the matrix. One failed cell is recorded and the sweep continues."""
    if not line_counts:
        raise ValueError("at least one line count is required")
    if repeat_count < 1:
        raise ValueError("repeat_count must be >= 1")
    if max_tokens is None:
        max_tokens = default_max_tokens(needle_count)
    post = post_func or _post_chat

    rows: list[Json] = []
    for line_count in line_counts:
        for repeat in range(1, repeat_count + 1):
            # Vary the seed per repeat so a repeat re-rolls the key/code assignment and
            # placement; repeating an identical prompt would only measure sampling noise.
            prompt = build_multi_needle_prompt(
                line_count=line_count,
                needle_count=needle_count,
                distractor_count=distractor_count,
                seed=seed + repeat,
            )
            row: Json = {
                "line_count": line_count,
                "repeat": repeat,
                "needle_lines": list(prompt.needle_lines),
                "prompt_sha256": prompt.sha256,
            }
            try:
                payload, elapsed = post(
                    base_url=base_url,
                    model=model,
                    prompt=prompt.text,
                    max_tokens=max_tokens,
                    timeout=timeout,
                )
                usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
                row["prompt_tokens"] = usage.get("prompt_tokens")
                row["completion_tokens"] = usage.get("completion_tokens")
                row["max_tokens"] = max_tokens
                row["elapsed_seconds"] = round(elapsed, 3)
                # A truncated answer looks exactly like failed retrieval in the hit
                # count. Record it so the two can never be confused again.
                reason = _finish_reason(payload)
                row["finish_reason"] = reason
                row["truncated"] = reason == "length"
                row.update(score_multi_needle_response(_assistant_text(payload), prompt))
                row["ok"] = (
                    row["needles_hit"] == row["needles_total"] and not row["truncated"]
                )
            except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError) as exc:
                row["ok"] = False
                row["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
            rows.append(row)
    return rows


def format_rows(rows: list[Json]) -> str:
    out = []
    for row in rows:
        if row.get("error"):
            out.append(f"  lines={row['line_count']:>6} r{row['repeat']}: FAILED {row['error']}")
            continue
        flag = "  TRUNCATED(raise --max-tokens)" if row.get("truncated") else ""
        out.append(
            f"  lines={row['line_count']:>6} r{row['repeat']}: "
            f"{row['needles_hit']}/{row['needles_total']} needles"
            f"  leaked={row['distractors_leaked']}"
            f"  tokens={row.get('prompt_tokens')}"
            f"  out={row.get('completion_tokens')}/{row.get('max_tokens')}"
            f"  {row.get('elapsed_seconds')}s{flag}"
        )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash-0731")
    parser.add_argument(
        "--line-counts",
        type=lambda v: [int(x) for x in v.split(",") if x.strip()],
        default=[1100, 4400, 13000],
    )
    parser.add_argument("--needle-count", type=int, default=8)
    parser.add_argument("--distractor-count", type=int, default=8)
    parser.add_argument("--repeat-count", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=3600.0)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)

    try:
        rows = run_multi_needle_probe(
            base_url=args.base_url,
            model=args.model,
            line_counts=args.line_counts,
            needle_count=args.needle_count,
            distractor_count=args.distractor_count,
            repeat_count=args.repeat_count,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
            seed=args.seed,
        )
    except ValueError as exc:
        print(f"  multi-needle probe aborted: {exc}", file=sys.stderr)
        return 2

    print(format_rows(rows))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return 0 if any(row.get("ok") for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
