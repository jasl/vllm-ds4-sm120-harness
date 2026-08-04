"""Cold (uncached) prefill timing for a live vLLM serve.

Why this exists: every ``llama-benchy --depth`` TTFT is prefix-CACHED. A reading of
"TTFT 2031 ms @ d122880" is 2048 fresh tokens against an already-warm 123k context, not
a cold 123k prefill -- the cold number at that length is ~89 s, more than an order of
magnitude larger. Any latency claim about long prompts taken from ``--depth`` numbers
understates reality badly, so this module measures the other thing.

Two properties make the measurement trustworthy:

* **Random token IDs, not text.** The prompt length is then exact (no tokenizer
  round-trip to estimate) and a prefix-cache hit is impossible, which is the whole
  point -- a text prompt could collide with an earlier probe and silently return a
  warm number.
* **A warmup request first**, so JIT and cudagraph compilation land outside the
  measured window.

Usage::

    python -m ds4_harness.cold_prefill_probe \\
        --base-url http://127.0.0.1:8000 \\
        --model deepseek-ai/DeepSeek-V4-Flash-0731 \\
        --lengths 8192,32768,131072
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# Kept well inside any plausible vocabulary. The ids only need to be valid and
# unpredictable; their meaning is irrelevant to a prefill timing.
_TOKEN_ID_MIN = 100
_TOKEN_ID_MAX = 30000
_WARMUP_TOKENS = 512


@dataclass(frozen=True)
class ProbeResult:
    """One (length, duration) sample. Frozen: results are never edited after the fact."""

    prompt_tokens: int
    seconds: float | None
    error: str | None = None

    @property
    def tokens_per_second(self) -> float | None:
        if self.seconds is None or self.seconds <= 0:
            return None
        return self.prompt_tokens / self.seconds

    def to_json(self) -> dict[str, object]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "seconds": self.seconds,
            "tokens_per_second": self.tokens_per_second,
            "error": self.error,
        }


def _random_token_ids(rng: random.Random, count: int) -> list[int]:
    if count < 1:
        raise ValueError(f"token count must be positive, got {count}")
    return [rng.randrange(_TOKEN_ID_MIN, _TOKEN_ID_MAX) for _ in range(count)]


def _time_completion(
    *,
    base_url: str,
    model: str,
    token_ids: list[int],
    max_tokens: int,
    timeout: float,
    api_key: str | None,
) -> float:
    """POST a completion and return wall-clock seconds.

    ``max_tokens=1`` keeps generation out of the measurement, so the elapsed time is
    prefill plus a single decode step.
    """
    payload = json.dumps(
        {
            "model": model,
            "prompt": token_ids,
            "max_tokens": max_tokens,
            "temperature": 0,
        }
    ).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/completions", data=payload, headers=headers
    )
    started = time.time()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response.read()
    return time.time() - started


def run_cold_prefill_probe(
    *,
    base_url: str,
    model: str,
    lengths: list[int],
    timeout: float = 1800.0,
    seed: int = 1234,
    api_key: str | None = None,
) -> list[ProbeResult]:
    """Time an uncached prefill at each requested length.

    A failure at one length is recorded and the sweep continues -- a 260k probe timing
    out should not discard the 8k and 32k points already collected.
    """
    if not lengths:
        raise ValueError("at least one length is required")

    rng = random.Random(seed)
    try:
        _time_completion(
            base_url=base_url,
            model=model,
            token_ids=_random_token_ids(rng, _WARMUP_TOKENS),
            max_tokens=1,
            timeout=timeout,
            api_key=api_key,
        )
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise RuntimeError(
            f"warmup request failed against {base_url}; the serve is not usable: {exc}"
        ) from exc

    results: list[ProbeResult] = []
    for length in lengths:
        try:
            seconds = _time_completion(
                base_url=base_url,
                model=model,
                token_ids=_random_token_ids(rng, length),
                max_tokens=1,
                timeout=timeout,
                api_key=api_key,
            )
            results.append(ProbeResult(prompt_tokens=length, seconds=seconds))
        except (urllib.error.URLError, OSError, ValueError) as exc:
            results.append(
                ProbeResult(
                    prompt_tokens=length,
                    seconds=None,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )
    return results


def format_results(results: list[ProbeResult]) -> str:
    lines = []
    for result in results:
        if result.seconds is None:
            lines.append(f"  cold prefill {result.prompt_tokens:>7} tok: FAILED  {result.error}")
            continue
        lines.append(
            f"  cold prefill {result.prompt_tokens:>7} tok: "
            f"{result.seconds:8.2f} s   ({result.tokens_per_second:8.1f} tok/s)"
        )
    return "\n".join(lines)


def _parse_lengths(value: str) -> list[int]:
    try:
        return [int(part) for part in value.split(",") if part.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid --lengths value {value!r}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash-0731")
    parser.add_argument("--lengths", type=_parse_lengths, default=[8192, 32768])
    parser.add_argument("--timeout", type=float, default=1800.0)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--api-key")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)

    try:
        results = run_cold_prefill_probe(
            base_url=args.base_url,
            model=args.model,
            lengths=args.lengths,
            timeout=args.timeout,
            seed=args.seed,
            api_key=args.api_key,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"  cold prefill probe aborted: {exc}", file=sys.stderr)
        return 1

    print(format_results(results))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps([result.to_json() for result in results], indent=2),
            encoding="utf-8",
        )
    return 0 if any(result.seconds is not None for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
