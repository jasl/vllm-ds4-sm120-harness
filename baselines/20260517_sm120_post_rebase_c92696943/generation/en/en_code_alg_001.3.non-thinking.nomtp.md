# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `default`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 36.928682
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3948, "completion_tokens": 3654, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3654
- Total tokens: 3948

## Prompt

```markdown
Write a single-file Python 3 command-line program named `schedule_optimizer.py`. Use no third-party packages. Keep the code under 1,000 lines.

Problem: Given a list of candidate work sessions, choose a non-overlapping subset that maximizes total value. Each session has an ID, start time, end time, and value. This is weighted interval scheduling with reconstruction.

Input: read JSON from standard input. Format:
{
  "sessions": [
    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}
  ]
}

Requirements:
1. Parse ISO-like timestamps without time zones using Python standard library.
2. Reject sessions whose end is not after start or whose value is negative.
3. Output JSON with `max_value`, `selected_ids` in chronological order, and `rejected` entries with reasons.
4. If multiple optimal solutions exist, choose the one with fewer sessions; if still tied, choose lexicographically smaller list of IDs.
5. Include an efficient O(n log n) dynamic programming solution.
6. Include built-in tests. When run with `--test`, execute tests and print a short success message. Normal mode should print only JSON.

Output only the complete Python code. Do not include explanations.
```

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""
schedule_optimizer.py — Weighted interval scheduling with reconstruction.
Usage:
    python schedule_optimizer.py < input.json       # normal mode → JSON output
    python schedule_optimizer.py --test             # run built-in tests
"""

import json
import sys
from datetime import datetime
from copy import deepcopy

# ---------------------------------------------------------------------------
#  Core algorithm
# ---------------------------------------------------------------------------

def parse_iso_datetime(s):
    """Parse ISO-like timestamp without timezone info. Raise ValueError on failure."""
    # Accept formats like "2026-05-01T09:00:00" (with optional microseconds)
    return datetime.fromisoformat(s)


def validate_sessions(sessions):
    """
    Validate and partition sessions into valid & rejected.
    Returns (valid_list, rejected_list).
    Each valid session is a dict with keys: id, start, end, value (int), start_dt, end_dt.
    """
    valid = []
    rejected = []

    for sess in sessions:
        sid = sess.get("id", "unknown")
        reasons = []

        # Check id presence
        if not isinstance(sess.get("id"), str) or not sess["id"]:
            reasons.append("missing or invalid id")

        # Parse start
        try:
            start_dt = parse_iso_datetime(sess["start"])
        except (KeyError, ValueError):
            reasons.append("invalid start timestamp")
            start_dt = None

        # Parse end
        try:
            end_dt = parse_iso_datetime(sess["end"])
        except (KeyError, ValueError):
            reasons.append("invalid end timestamp")
            end_dt = None

        # Check value
        try:
            value = sess["value"]
            if not isinstance(value, (int, float)):
                reasons.append("value is not a number")
            elif value < 0:
                reasons.append("negative value")
            else:
                value = int(value) if isinstance(value, float) else value
        except KeyError:
            reasons.append("missing value")
            value = None

        # Check end > start (only if both dates are valid)
        if start_dt is not None and end_dt is not None:
            if end_dt <= start_dt:
                reasons.append("end not after start")

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
        else:
            # Build clean session record
            valid.append({
                "id": sid,
                "start": sess["start"],
                "end": sess["end"],
                "value": value,
                "start_dt": start_dt,
                "end_dt": end_dt,
            })

    return valid, rejected


def weighted_interval_scheduling(sessions):
    """
    DP solution: O(n log n)
    sessions: list of dicts (must have 'start_dt', 'end_dt', 'value', 'id')
    Returns (max_value, selected_ids) where selected_ids is in chronological order.
    Tie-breaking: fewer sessions → lexicographically smaller list of IDs.
    """
    if not sessions:
        return 0, []

    # Sort by end time ascending
    sorted_sessions = sorted(sessions, key=lambda x: x["end_dt"])
    n = len(sorted_sessions)

    # Precompute p[i] = index of last non-overlapping session before i (or -1)
    end_times = [s["end_dt"] for s in sorted_sessions]
    p = [-1] * n
    for i in range(n):
        start_i = sorted_sessions[i]["start_dt"]
        # binary search for rightmost session with end <= start_i
        lo, hi = 0, i
        while lo < hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_i:
                lo = mid + 1
            else:
                hi = mid
        p[i] = lo - 1

    # DP arrays: dp_value[i] = max value up to i (inclusive)
    # dp_choice[i] = (value, count, lex_key) for tie-breaking
    # lex_key is a tuple of IDs (for reconstruction)
    dp_value = [0] * n
    dp_count = [0] * n
    dp_lex = [()] * n  # tuple of IDs for selected sessions up to i (in order)

    for i in range(n):
        # Option 1: include session i
        inc_value = sorted_sessions[i]["value"]
        inc_count = 1
        inc_lex = (sorted_sessions[i]["id"],)
        if p[i] != -1:
            inc_value += dp_value[p[i]]
            inc_count += dp_count[p[i]]
            inc_lex = dp_lex[p[i]] + inc_lex

        # Option 2: exclude session i
        exc_value = dp_value[i-1] if i > 0 else 0
        exc_count = dp_count[i-1] if i > 0 else 0
        exc_lex = dp_lex[i-1] if i > 0 else ()

        # Choose better
        if inc_value > exc_value:
            dp_value[i] = inc_value
            dp_count[i] = inc_count
            dp_lex[i] = inc_lex
        elif inc_value < exc_value:
            dp_value[i] = exc_value
            dp_count[i] = exc_count
            dp_lex[i] = exc_lex
        else:
            # tie on value → fewer sessions
            if inc_count < exc_count:
                dp_value[i] = inc_value
                dp_count[i] = inc_count
                dp_lex[i] = inc_lex
            elif inc_count > exc_count:
                dp_value[i] = exc_value
                dp_count[i] = exc_count
                dp_lex[i] = exc_lex
            else:
                # tie on count → lexicographically smaller list
                if inc_lex < exc_lex:
                    dp_value[i] = inc_value
                    dp_count[i] = inc_count
                    dp_lex[i] = inc_lex
                else:
                    dp_value[i] = exc_value
                    dp_count[i] = exc_count
                    dp_lex[i] = exc_lex

    max_value = dp_value[-1]
    selected_ids = list(dp_lex[-1]) if dp_lex[-1] else []
    return max_value, selected_ids


def process_input(data):
    """Main processing: validate, run DP, return output dict."""
    sessions_raw = data.get("sessions", [])
    if not isinstance(sessions_raw, list):
        sessions_raw = []

    valid_sessions, rejected = validate_sessions(sessions_raw)

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Build rejected output with original ids
    rejected_output = []
    for r in rejected:
        rejected_output.append({
            "id": r["id"],
            "reasons": r["reasons"]
        })

    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected_output
    }


# ---------------------------------------------------------------------------
#  Tests
# ---------------------------------------------------------------------------

def run_tests():
    """Run built-in tests. Return True if all pass."""
    all_pass = True

    # Test 1: Example from problem statement
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}
        ]
    }
    res = process_input(data)
    assert res["max_value"] == 5, "Test 1: max_value"
    assert res["selected_ids"] == ["a"], "Test 1: selected_ids"
    assert res["rejected"] == [], "Test 1: rejected"
    print("✓ Test 1: basic single session")

    # Test 2: Overlapping sessions — choose best
    data = {
        "sessions": [
            {"id": "s1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "s2", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 20},
            {"id": "s3", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 15}
        ]
    }
    res = process_input(data)
    # s2(20) + ? s1 overlaps s2, s3 starts 11:00 so s2+ s3 = 35? s2 ends 12:00, s3 starts 11:00 overlap → no
    # Actually s2 10-12, s3 11-13 overlap → only s1 (10) or s2 (20) or s3 (15) or s1+s3? s1 ends 11 s3 starts 11 → ok, 10+15=25
    # Best is s2 alone (20) or s1+s3 (25) → 25
    assert res["max_value"] == 25, f"Test 2: max_value = {res['max_value']}"
    assert sorted(res["selected_ids"]) == ["s1", "s3"], f"Test 2: selected_ids = {res['selected_ids']}"
    print("✓ Test 2: overlapping - optimal 25")

    # Test 3: Rejected sessions
    data = {
        "sessions": [
            {"id": "g1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "g2", "start": "invalid", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "g3", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "g4", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 4},
        ]
    }
    res = process_input(data)
    assert res["max_value"] == 4, "Test 3: max_value"
    assert res["selected_ids"] == ["g4"], "Test 3: selected_ids"
    assert len(res["rejected"]) == 3, "Test 3: rejected count"
    print("✓ Test 3: rejected entries")

    # Test 4: Tie-breaking → fewer sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        ]
    }
    # possible: a (10) or b+c (10) → fewer sessions → a
    res = process_input(data)
    assert res["max_value"] == 10, "Test 4: max_value"
    assert res["selected_ids"] == ["a"], f"Test 4: selected_ids = {res['selected_ids']}"
    print("✓ Test 4: tie-breaking fewer sessions")

    # Test 5: Tie-breaking same count → lexicographic
    data = {
        "sessions": [
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        ]
    }
    # both non-overlapping → total 10, both 2 sessions → lexicographic [a, z] vs [z, a] → [a, z] wins
    # But sorted chronologically: a (10-11) after z (9-10), so chronological order: [z, a]; lexicographic [a, z] < [z, a]
    # Since value identical, count identical → choose lexicographically smaller list → [a, z]
    res = process_input(data)
    assert res["max_value"] == 10, "Test 5: max_value"
    assert res["selected_ids"] == ["a", "z"], f"Test 5: selected_ids = {res['selected_ids']}"
    print("✓ Test 5: tie-breaking lexicographic")

    # Test 6: Empty input
    data = {"sessions": []}
    res = process_input(data)
    assert res["max_value"] == 0, "Test 6: max_value"
    assert res["selected_ids"] == [], "Test 6: selected_ids"
    assert res["rejected"] == [], "Test 6: rejected"
    print("✓ Test 6: empty input")

    # Test 7: Missing id field -> rejected
    data = {"sessions": [{"start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1}]}
    res = process_input(data)
    assert res["max_value"] == 0, "Test 7: max_value"
    assert res["rejected"][0]["id"] == "unknown", "Test 7: rejected id"
    print("✓ Test 7: missing id rejected")

    # Test 8: Larger test for DP correctness
    data = {
        "sessions": [
            {"id": "1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 6},
            {"id": "2", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 7},
            {"id": "3", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 8},
            {"id": "4", "start": "2026-05-01T12:30:00", "end": "2026-05-01T13:30:00", "value": 4},
        ]
    }
    # 1(6) + 3(8) + 4(4) = 18   or 2(7)+4(4)=11   or 1+4=10  etc → 18
    res = process_input(data)
    assert res["max_value"] == 18, f"Test 8: max_value = {res['max_value']}"
    assert res["selected_ids"] == ["1", "3", "4"], f"Test 8: selected_ids = {res['selected_ids']}"
    print("✓ Test 8: multiple non-overlapping")

    print("\nAll tests passed!")


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        sys.exit(0)

    # Normal mode: read JSON from stdin, output JSON
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = process_input(data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```
````
