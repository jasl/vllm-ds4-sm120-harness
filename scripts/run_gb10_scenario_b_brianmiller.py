"""Replicate brianmiller's PR#41834 protocol (comment 4920277612) on a live serve.

Protocol (his exact shapes):
  1. Short-context throughput: C in {1,2,4}, 5 requests/level, max_tokens=512,
     temperature 0.7-ish short prompts, WARM (one throwaway pass first);
     metric = aggregate tok/s per level.
  2. Long-context: ONE ~121K-token unique prompt, max_tokens=1 -> cold prefill
     wall seconds; then the same prompt again with max_tokens=256 -> cached
     decode tok/s.
  3. KV capacity: read num_device_pages from the serve log (printed separately).

Usage: python run_gb10_scenario_b_brianmiller.py [base_url] [served_model]
Requires a serve with max-model-len >= 123000.
"""
import json
import sys
import threading
import time
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000") + "/v1/completions"
MODEL = sys.argv[2] if len(sys.argv) > 2 else "deepseek-ai/DeepSeek-V4-Flash"


def send(prompt, max_tokens, temperature=0.7, timeout=1800):
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "ignore_eos": True,
    }).encode()
    req = urllib.request.Request(BASE, data=body, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]}") from None
    dt = time.perf_counter() - t0
    return dt, d["usage"]["completion_tokens"], d["usage"]["prompt_tokens"]


SHORT_PROMPTS = [
    f"Explain topic {i}: why does a moka pot need medium grind coffee? Answer thoroughly."
    for i in range(64)
]

# --- 1. short-context throughput ladder (warm) ---
send(SHORT_PROMPTS[0], 64, timeout=600)  # warmup
print("scenario-B short-ctx ladder (5 req/level, max_tokens=512, warm):")
pi = 1
for conc in (1, 2, 4):
    total_tok = 0
    results = []

    def worker(p):
        results.append(send(p, 512))

    t0 = time.perf_counter()
    done = 0
    while done < 5:
        batch = min(conc, 5 - done)
        threads = [threading.Thread(target=worker, args=(SHORT_PROMPTS[pi + done + j],)) for j in range(batch)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        done += batch
    wall = time.perf_counter() - t0
    pi += 8
    total_tok = sum(r[1] for r in results)
    print(f"  C={conc}: {total_tok / wall:.2f} tok/s aggregate ({total_tok} tok / {wall:.1f}s)")

# --- 2. 121K cold prefill + cached decode ---
nonce = int(time.time())
lines = [
    f"Record {i:05d} sess {nonce}: token-{(i * 2654435761 + nonce) & 0xFFFFFF:06x} status active."
    for i in range(6000)  # ~117K tokens (this format measures 19.45 tok/line)
]
lines.append("In one short sentence: how many records are listed above?")
big = "\n".join(lines)

dt, _, ptok = send(big, 1, temperature=0)
print(f"scenario-B long-ctx COLD prefill: {ptok} tokens in {dt:.1f}s = {ptok / dt:.1f} tok/s")

dt2, ctok, _ = send(big, 256, temperature=0)
print(f"scenario-B long-ctx CACHED decode: {ctok} tok in {dt2:.1f}s = {ctok / dt2:.2f} tok/s")
