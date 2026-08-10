#!/usr/bin/env python3
"""Does the prefix cache survive switching between conversations?

Engine-agnostic: talks only OpenAI-compatible `/v1/chat/completions` and judges
by time-to-first-response, so it runs against vLLM, TokenSpeed, or anything
else. Engine metrics are read when the endpoint happens to expose them, but
only as corroboration -- never as the deciding signal.

  ./prefix_cache_session_switch.py --base-url URL --model NAME [--tokens 90000]

Exit 0 healthy, 1 the cache does not survive a switch, 2 inconclusive.

WHAT IT PROBES

Reported against some vLLM builds in 2026-08: two conversations, alternating.
A's second turn is instant, then B runs once, and A's third turn pays the full
cold prefill again -- with the KV pool nearly empty and no preemption. The
cause is a freed-but-still-cached block being handed to the next allocation,
which drops its hash on the way out.

Upstream fixed it in vllm-project/vllm#42656 (2026-06-16) by splitting the
free queue: blocks with no hash are prepended and consumed first, blocks that
still carry a cache entry are appended and only touched when nothing else is
left. Any engine with an LRU block cache has the same trap to avoid, which is
why this probe is worth keeping around a new implementation.

WHY LATENCY, AND HOW IT AVOIDS FOOLING ITSELF

A hit-rate counter would be crisper, but its name is engine-specific. Latency
is universal, and here the signal is not subtle: a cold prefill of a 90k-token
prefix takes tens of seconds against about one second warm.

The probe refuses to guess when the evidence is weak. It first establishes the
machine's own cold/hot spread by asking A twice; if the second call is not
dramatically faster, prefix caching is probably off or the prefix too short,
and it exits INCONCLUSIVE rather than reporting a pass. Only against a proven
spread does it judge the post-switch calls.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request

# A warm call must be at least this many times faster than cold for the machine
# to be considered as having a working prefix cache at all.
MIN_COLD_HOT_RATIO = 5.0
# A post-switch call may be this multiple of the warm baseline before we call
# it a regression. Generous: warm calls are ~1 s and jitter is absolute.
POST_SWITCH_TOLERANCE = 3.0


def _post(url: str, payload: dict, api_key: str | None, timeout: float) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers=headers
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _metrics(base: str, timeout: float = 10.0) -> dict[str, float]:
    """Best-effort scrape. Absent or unparseable metrics are not an error --
    they only mean this run has no corroborating evidence to print."""
    out: dict[str, float] = {}
    try:
        with urllib.request.urlopen(f"{base}/metrics", timeout=timeout) as r:
            text = r.read().decode()
    except (urllib.error.URLError, OSError, ValueError):
        return out
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        for key in ("prefix_cache_queries_total", "prefix_cache_hits_total",
                    "num_preemptions_total"):
            if key in line:
                try:
                    out[key] = out.get(key, 0.0) + float(line.rsplit(" ", 1)[1])
                except (ValueError, IndexError):
                    pass
    return out


def build_prefix(tag: str, approx_tokens: int) -> str:
    """Two prefixes that share only a short preamble.

    They must diverge early: DeepSeek-V4's template makes the first ~256 tokens
    nearly identical for every request, and a probe whose prefixes differ only
    later would measure template sharing rather than per-conversation caching.
    """
    body = " ".join(
        f"{tag}-{i}: 这一段用于占位，描述一个与其他会话无关的独立主题细节。"
        for i in range(max(1, approx_tokens // 12))
    )
    return f"以下是关于{tag}的独立笔记，与任何其他主题无关。\n\n{body}"


def ask(base: str, model: str, prefix: str, api_key: str | None) -> tuple[float, dict]:
    before = _metrics(base)
    t0 = time.time()
    _post(
        f"{base}/v1/chat/completions",
        {
            "model": model,
            "messages": [{"role": "user", "content": prefix + "\n\n用一句话总结。"}],
            "max_tokens": 24,
            "temperature": 0,
        },
        api_key,
        timeout=1800,
    )
    elapsed = time.time() - t0
    after = _metrics(base)
    delta = {k: after.get(k, 0.0) - before.get(k, 0.0) for k in after}
    return elapsed, delta


def describe(delta: dict) -> str:
    q = delta.get("prefix_cache_queries_total", 0.0)
    h = delta.get("prefix_cache_hits_total", 0.0)
    pre = delta.get("num_preemptions_total", 0.0)
    if not q:
        return "no engine metrics"
    return f"engine hit {h / q * 100:5.1f}%, preemptions +{int(pre)}"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--api-key")
    p.add_argument(
        "--tokens", type=int, default=90000,
        help="approximate prefix size; must be big enough that a cold prefill "
             "is unmistakable (default 90000, about 45 s on a 2-node GB10)",
    )
    args = p.parse_args()
    base = args.base_url.rstrip("/")

    a = build_prefix("分布式系统", args.tokens)
    b = build_prefix("编译器优化", args.tokens)

    print(f"=== prefix cache across a session switch")
    print(f"    endpoint {base}")
    print(f"    model    {args.model}")
    print(f"    prefix   ~{len(a)} chars per conversation")

    steps: list[tuple[str, str]] = [
        ("A cold", a), ("A warm", a), ("B cold", b),
        ("A after B", a), ("B after A", b),
    ]
    timings: dict[str, float] = {}
    for label, prefix in steps:
        elapsed, delta = ask(base, args.model, prefix, args.api_key)
        timings[label] = elapsed
        print(f"    {label:<12} {elapsed:7.2f}s   {describe(delta)}")

    cold = statistics.mean([timings["A cold"], timings["B cold"]])
    warm = timings["A warm"]
    print("---")

    if warm <= 0 or cold / warm < MIN_COLD_HOT_RATIO:
        print(
            f"INCONCLUSIVE: warm ({warm:.2f}s) is only {cold / max(warm, 1e-9):.1f}x "
            f"faster than cold ({cold:.2f}s). Prefix caching looks disabled, or "
            f"--tokens is too small for the difference to show. Nothing is being "
            f"tested; raise --tokens or enable the cache."
        )
        return 2

    limit = warm * POST_SWITCH_TOLERANCE
    regressions = [
        (label, timings[label]) for label in ("A after B", "B after A")
        if timings[label] > limit
    ]
    if regressions:
        detail = ", ".join(f"{k} {v:.2f}s" for k, v in regressions)
        print(
            f"CACHE LOST ON SWITCH: warm was {warm:.2f}s and cold {cold:.2f}s, "
            f"but {detail} — a conversation's cache does not survive another "
            f"conversation running in between."
        )
        return 1

    print(
        f"HEALTHY: cold {cold:.2f}s, warm {warm:.2f}s, and after switching "
        f"A={timings['A after B']:.2f}s B={timings['B after A']:.2f}s — both "
        f"conversations kept their cache."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
