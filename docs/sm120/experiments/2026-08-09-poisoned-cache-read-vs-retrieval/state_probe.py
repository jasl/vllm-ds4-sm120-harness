"""Read-vs-search on a poisoned cache, with the cache STATE measured properly.

The previous probe classified the cache with ONE gate request. That cannot work:
in the known-poisoned state the per-request failure rate is ~92% (V2 wave 2 lost
11 of 12), and in the clean state it is not zero either, so a single sample
cannot distinguish them. It produced a run where gate #1 failed and gate #2
passed with one request in between, which reads as "the cache healed" but is
equally consistent with two draws from one distribution.

Here every state check is N requests and reports k/N. A read arm's result is
only interpretable if the checks bracketing it BOTH show a poisoned state.

    real gate poisons  ->  STATE  ->  FILL  ->  STATE  ->  QUOTE  ->  STATE
                                                                  ->  HASH-BUST

HASH-BUST changes one character early in the document, which re-hashes block 0
and every chained block after it: full reuse, zero hits, same process. If that
comes back clean while the identical document does not, the damage is in the
cached blocks rather than anywhere else.
"""

from __future__ import annotations

import argparse, json, re, sys
from concurrent.futures import ThreadPoolExecutor

from ds4_harness.client import post_json_with_retries
from ds4_harness.long_context_probe import build_long_context_prompt, evaluate_long_context_response

TERMS = ("alpha-cobalt-17", "beta-quartz-29", "gamma-onyx-43")
MOD, MUL = 1009, 37
INV = pow(MUL, -1, MOD)
LINE_RE = re.compile(r"Line\s+(\d{1,4})\s*:\s*subsystem\s*=\s*(\d+)\s*;\s*shard\s*=\s*(\d+)\s*;\s*checksum\s*=\s*(\d+)", re.I)
FILL_LINES = [100, 300, 500, 700]   # 850 fabricates all-zero fields even on clean caches


def pl(model, text, mt=384):
    return {"model": model, "messages": [{"role": "user", "content": text}], "max_tokens": mt,
            "temperature": 0.0, "chat_template_kwargs": {"enable_thinking": False}}


class Unreachable(RuntimeError):
    """The serve did not answer. NOT the same as answering wrongly.

    Without this distinction a dead serve reads as a maximally poisoned cache:
    six failed requests, verdict POISONED, and every arm after it meaningless.
    A smoke test against a stopped server produced exactly that.
    """


def gate_once(base, model, text, timeout):
    """True = correct answer, False = wrong answer, raises Unreachable = no answer."""
    try:
        r = post_json_with_retries(base, "/v1/chat/completions", pl(model, text), timeout, request_retries=2)
    except (OSError, RuntimeError, ValueError) as exc:
        raise Unreachable(str(exc)) from exc
    try:
        ok, _, _ = evaluate_long_context_response(r, TERMS)
    except (KeyError, IndexError, TypeError):
        return False          # answered, but not in a shape we can score
    return ok


def state(base, model, text, timeout, n, label):
    """Serial, so the check itself adds no concurrent writers."""
    k = 0
    for _ in range(n):
        k += gate_once(base, model, text, timeout)   # Unreachable propagates: not a verdict
    verdict = "POISONED" if k <= n // 3 else ("clean" if k >= n - n // 3 else "AMBIGUOUS")
    print(f"  STATE {label}: {k}/{n} pass -> {verdict}", flush=True)
    return k, n, verdict


def read_arm(base, model, body, timeout, lines, label, sentinel=False):
    want = ", ".join(f"{n:04d}" for n in lines)
    tail = ("\n\nFinal task:\nQuote verbatim the complete text of these lines: "
            f"{want}\nCopy each exactly as it appears, including the \"Line NNNN:\" prefix.")
    r = post_json_with_retries(base, "/v1/chat/completions", pl(model, body + tail), timeout, request_retries=2)
    txt = r["choices"][0]["message"].get("content") or ""
    if sentinel:
        got = {t: (t.lower() in txt.lower()) for t in TERMS}
        print(f"  {label}: {sum(got.values())}/3 sentinel codes quoted back", flush=True)
        return {"ok": all(got.values()), "detail": got, "raw": txt}
    found = {int(m[0]): (int(m[1]), int(m[2]), int(m[3])) for m in LINE_RE.findall(txt)}
    rows = []
    for n in lines:
        h = found.get(n)
        if not h:
            rows.append((n, None, False)); continue
        sub, shard, cs = h
        rd = (cs * INV) % MOD
        rows.append((n, rd, rd == n and rd % 17 == sub and rd % 29 == shard))
    ok = sum(1 for _, _, c in rows if c)
    print(f"  {label}: {ok}/{len(lines)} lines read back correctly", flush=True)
    for n, rd, c in rows:
        print(f"    line {n:>4}: " + ("(not quoted)" if rd is None else f"read {rd:>4}  delta {rd-n:+d}  correct={c}"), flush=True)
    return {"ok": ok == len(lines), "rows": rows, "raw": txt}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True); ap.add_argument("--model", required=True)
    ap.add_argument("--line-count", type=int, default=900)
    ap.add_argument("--state-n", type=int, default=6, help="requests per state check")
    ap.add_argument("--concurrency", type=int, default=12)
    ap.add_argument("--timeout", type=int, default=900); ap.add_argument("--json-output")
    a = ap.parse_args()

    p = build_long_context_prompt(name="arthur_long_context_coherence", line_count=a.line_count)
    body = p.text.rsplit("\nFinal task:", 1)[0]
    S = lambda lbl: state(a.base_url, a.model, p.text, a.timeout, a.state_n, lbl)

    k0, n0, v0 = S("#0 after the caller's gate")
    if v0 != "POISONED":
        print("  This serve is not in a poisoned state; nothing below would be interpretable.", flush=True)
        if a.json_output: json.dump({"state0": [k0, n0, v0]}, open(a.json_output, "w"), indent=2)
        return 3

    fill = read_arm(a.base_url, a.model, body, a.timeout, FILL_LINES, "FILL  (ordinary filler, by position)")
    k1, n1, v1 = S("#1 after FILL")
    qt = read_arm(a.base_url, a.model, body, a.timeout, [17, 450, 887], "QUOTE (sentinel lines, by position)", sentinel=True)
    k2, n2, v2 = S("#2 after QUOTE")

    busted = body.replace("You are validating long-context retrieval for DeepSeek V4.",
                          "You are validating long-context retrieval for DeepSeek V4..", 1)
    bust_text = busted + "\n\nFinal task:\nIn one concise paragraph, list the first, middle, and final indexer validation codes from the context. Use the exact code strings."
    # SERIAL, deliberately. Running this arm concurrently was the first design and
    # it proved nothing: 12 concurrent requests on a busted prefix satisfy "no
    # reuse" AND "concurrent cold prefill" at once, and the second condition is
    # the original fault. Serial isolates the one variable that matters here --
    # whether the damage lives in the cached blocks.
    bust = sum(gate_once(a.base_url, a.model, bust_text, a.timeout) for _ in range(a.state_n))
    print(f"  HASH-BUST (one early char changed -> no reuse, SERIAL): {bust}/{a.state_n}", flush=True)
    if bust >= a.state_n - a.state_n // 3:
        print("    -> clean without reuse while the identical document fails:"
              " the damage is in the CACHED BLOCKS.", flush=True)
    elif bust <= a.state_n // 3:
        print("    -> fails even with zero reuse: the damage is NOT block-resident;"
              " something process-wide is wrong.", flush=True)

    still = v1 == "POISONED" and v2 == "POISONED"
    if still and fill["ok"] and qt["ok"]:
        print("  VERDICT: poisoned throughout (checks #0/#1/#2 all POISONED) yet both read arms "
              "returned exact content -> KV intact, content-addressed RETRIEVAL is what breaks.", flush=True)
    elif not still:
        print("  VERDICT: the state changed mid-run, so the read arms are not interpretable. "
              "This is the failure mode the single-request check hid.", flush=True)
    else:
        print("  VERDICT: poisoned throughout AND a read arm failed -> the cached content is wrong.", flush=True)

    if a.json_output:
        json.dump({"states": [[k0, n0, v0], [k1, n1, v1], [k2, n2, v2]],
                   "fill": fill, "quote": qt, "hash_bust": bust, "hash_bust_n": a.state_n}, open(a.json_output, "w"), indent=2)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Unreachable as exc:
        # exit 4 = "the serve stopped answering", distinct from 3 = "clean serve"
        # and 0 = "poisoned, arms interpretable". The caller must not read this
        # as a cache verdict.
        print(f"  ABORT: the serve stopped answering ({exc}); no cache verdict from this run.",
              flush=True)
        sys.exit(4)
