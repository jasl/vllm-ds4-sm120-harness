#!/usr/bin/env bash
# Multi-chunk prefill gate: requests larger than --chunked-prefill-size take a
# scheduler path (chunked continuation + head-of-line admission) that NO other
# gate exercises — benchy/arthur/GSM8K are all single-chunk. The 2026-07-10
# upstream-#555-pick regression (permanent head-of-line queue jam for any
# request past the first chunk boundary) survived every existing gate.
# Requires a live serve with max-model-len >= 50K and chunked-prefill 40960.
set -uo pipefail
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
python3 - "$BASE_URL" <<'PY'
import json, sys, time, urllib.request
base = sys.argv[1] + "/v1/completions"
def probe(nlines, tag, timeout=420):
    lines = [f"Record {i:05d} gate 9: token-{(i*2654435761)&0xFFFFFF:06x} value-{(i*40503)&0xFFFF:04x} status active." for i in range(nlines)]
    body = json.dumps({"model": "deepseek-ai/DeepSeek-V4-Flash-0731", "prompt": "\n".join(lines), "max_tokens": 1, "temperature": 0}).encode()
    req = urllib.request.Request(base, data=body, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    print(f"  [{tag}] {d['usage']['prompt_tokens']} tok in {time.time()-t0:.1f}s")
probe(2400, "2-chunk ~46K")
print("PASS multichunk_prefill")
PY
rc=$?
[ $rc -ne 0 ] && echo "FAIL multichunk_prefill (stall/timeout = head-of-line jam class)"
exit $rc
