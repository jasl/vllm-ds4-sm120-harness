# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 27.425282
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 4111, "completion_tokens": 3817, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3817
- Total tokens: 4111

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
import json
import sys
from datetime import datetime
from bisect import bisect_right

def parse_iso(timestamp):
    """Parse ISO-like timestamp without timezone info."""
    # Remove trailing 'Z' if present
    if timestamp.endswith('Z'):
        timestamp = timestamp[:-1]
    # Handle microseconds and timezone offset without colon
    try:
        return datetime.fromisoformat(timestamp)
    except ValueError:
        # Try with microseconds
        if '.' in timestamp:
            parts = timestamp.split('.')
            if len(parts) == 2:
                base = parts[0]
                frac = parts[1].rstrip('Z')
                if len(frac) > 6:
                    frac = frac[:6]
                timestamp = f"{base}.{frac}"
                return datetime.fromisoformat(timestamp)
        raise

def weighted_interval_scheduling(intervals):
    """
    O(n log n) DP for weighted interval scheduling.
    intervals: list of (id, start_dt, end_dt, value)
    Returns: (max_value, selected_ids)
    """
    if not intervals:
        return 0, []

    # Sort by end time
    sorted_int = sorted(intervals, key=lambda x: x[2])  # x[2] = end_dt

    n = len(sorted_int)
    end_times = [x[2] for x in sorted_int]
    values = [x[3] for x in sorted_int]
    ids = [x[0] for x in sorted_int]
    starts = [x[1] for x in sorted_int]

    # Precompute p[j] = index of last interval that ends before interval j starts
    p = [-1] * n
    for j in range(n):
        # Find rightmost interval with end <= start of interval j
        idx = bisect_right(end_times, starts[j]) - 1
        p[j] = idx

    # DP arrays
    dp = [0] * (n + 1)  # dp[i] = max value using first i intervals (1-indexed)
    choice = [False] * n  # whether we include interval j in optimal solution

    for j in range(1, n + 1):
        include_val = values[j - 1] + (dp[p[j - 1] + 1] if p[j - 1] >= 0 else 0)
        exclude_val = dp[j - 1]

        if include_val > exclude_val:
            dp[j] = include_val
            choice[j - 1] = True
        elif include_val == exclude_val:
            # Tie-breaking: fewer sessions or lexicographically smaller
            # First, compute what would be selected in each case
            include_sessions = _reconstruct(j - 1, p, choice, ids, include=True)
            exclude_sessions = _reconstruct(j - 1, p, choice, ids, include=False)

            # Exclude case: we are not taking interval j-1, so check dp[j-1] selection
            # We need to compare full solutions
            inc_list = include_sessions
            exc_list = exclude_sessions

            if len(inc_list) < len(exc_list):
                dp[j] = include_val
                choice[j - 1] = True
            elif len(inc_list) > len(exc_list):
                dp[j] = exclude_val
                choice[j - 1] = False
            else:
                # Same length, lexicographic comparison
                if sorted(inc_list) < sorted(exc_list):
                    dp[j] = include_val
                    choice[j - 1] = True
                else:
                    dp[j] = exclude_val
                    choice[j - 1] = False
        else:
            dp[j] = exclude_val
            choice[j - 1] = False

    # Full reconstruction with tie-breaking
    selected = _reconstruct(n - 1, p, choice, ids, include=choice[n - 1])

    return dp[n], selected

def _reconstruct(j, p, choice, ids, include):
    """Reconstruct selected ids up to index j (0-indexed)."""
    selected = []
    i = j
    while i >= 0:
        if include and p[i] >= 0:
            this_choice = choice[i]
        elif include and p[i] < 0:
            this_choice = True
        elif not include:
            this_choice = False
        else:
            this_choice = choice[i]

        if this_choice:
            selected.append(ids[i])
            if p[i] >= 0:
                i = p[i]
                # Need to decide for the next interval based on its saved choice
                include = choice[i] if i >= 0 else False
            else:
                break
        else:
            i -= 1
            include = choice[i] if i >= 0 else False
    return selected[::-1]

def solve(input_data):
    """Main solving logic."""
    sessions = input_data.get("sessions", [])

    valid_intervals = []
    rejected = []

    for sess in sessions:
        sess_id = sess.get("id", "unknown")
        start_str = sess.get("start", "")
        end_str = sess.get("end", "")
        value = sess.get("value", 0)

        # Validate value
        if value < 0:
            rejected.append({"id": sess_id, "reason": "negative value"})
            continue

        # Parse timestamps
        try:
            start_dt = parse_iso(start_str)
            end_dt = parse_iso(end_str)
        except (ValueError, TypeError):
            rejected.append({"id": sess_id, "reason": "invalid timestamp"})
            continue

        # Validate order
        if end_dt <= start_dt:
            rejected.append({"id": sess_id, "reason": "end not after start"})
            continue

        valid_intervals.append((sess_id, start_dt, end_dt, value))

    max_value, selected_ids = weighted_interval_scheduling(valid_intervals)

    # Sort selected by start time (chronological)
    id_to_start = {s[0]: s[1] for s in valid_intervals}
    selected_ids.sort(key=lambda x: id_to_start[x])

    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return result

# ----- Tests -----
def run_tests():
    all_pass = True

    # Test 1: Basic case
    input1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
        ]
    }
    res1 = solve(input1)
    assert res1["max_value"] == 8, f"Test 1 failed: {res1}"
    assert set(res1["selected_ids"]) == {"a", "c"}, f"Test 1 ids failed: {res1}"
    assert res1["rejected"] == [], f"Test 1 rejected failed: {res1}"

    # Test 2: Reject negative value
    input2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    res2 = solve(input2)
    assert res2["max_value"] == 5, f"Test 2 failed: {res2}"
    assert res2["selected_ids"] == ["y"], f"Test 2 ids failed: {res2}"
    assert len(res2["rejected"]) == 1, f"Test 2 rejected count failed: {res2}"
    assert res2["rejected"][0]["id"] == "x", f"Test 2 rejected id failed: {res2}"

    # Test 3: Reject end not after start
    input3 = {
        "sessions": [
            {"id": "p", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ]
    }
    res3 = solve(input3)
    assert res3["max_value"] == 0, f"Test 3 failed: {res3}"
    assert res3["selected_ids"] == [], f"Test 3 ids failed: {res3}"
    assert len(res3["rejected"]) == 1, f"Test 3 rejected count failed: {res3}"

    # Test 4: Tie-breaking (equal value, choose fewer sessions)
    input4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    res4 = solve(input4)
    # Options: {a,b} value=10 (2 sessions), {c} value=5 (1 session) -> best is 10 with 2 sessions
    # But {a,b} has 2 sessions, {c} has 1 but value lower. So {a,b} wins.
    # Actually {a,b} = 10, {c}=5, so {a,b}
    assert res4["max_value"] == 10, f"Test 4 failed: {res4}"
    assert set(res4["selected_ids"]) == {"a", "b"}, f"Test 4 ids failed: {res4}"

    # Test 5: Tie-breaking same value, same sessions count -> lexicographic
    input5 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    res5 = solve(input5)
    assert res5["max_value"] == 10, f"Test 5 failed: {res5}"
    # Possible pairs: (b,a) -> sorted [a,b], (c,d) -> [c,d], (b,d) -> [b,d], (c,a) -> [a,c]
    # All value=10, length=2. Lexicographically smallest sorted list: [a,b] < [a,c] < [b,d] < [c,d]
    # But note intervals b (9-10) and a (10-11) are compatible; c (9-10) and d (10-11) also compatible
    # Also b (9-10) and d (10-11) compatible; c (9-10) and a (10-11) compatible
    # Lexicographically smallest is [a,b]
    assert res5["selected_ids"] == ["a", "b"], f"Test 5 ids failed: {res5}"

    # Test 6: Empty sessions
    input6 = {"sessions": []}
    res6 = solve(input6)
    assert res6["max_value"] == 0, f"Test 6 failed: {res6}"
    assert res6["selected_ids"] == [], f"Test 6 ids failed: {res6}"
    assert res6["rejected"] == [], f"Test 6 rejected failed: {res6}"

    # Test 7: Invalid timestamp
    input7 = {
        "sessions": [
            {"id": "z", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    res7 = solve(input7)
    assert res7["max_value"] == 0, f"Test 7 failed: {res7}"
    assert len(res7["rejected"]) == 1, f"Test 7 rejected count failed: {res7}"
    assert res7["rejected"][0]["id"] == "z", f"Test 7 rejected id failed: {res7}"

    # Test 8: Complex tie-breaking with same value
    input8 = {
        "sessions": [
            {"id": "aa", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "bb", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "cc", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 6}
        ]
    }
    res8 = solve(input8)
    # aa+bb = 6 (2 sessions), cc = 6 (1 session) -> fewer sessions -> choose cc
    assert res8["max_value"] == 6, f"Test 8 failed: {res8}"
    assert res8["selected_ids"] == ["cc"], f"Test 8 ids failed: {res8}"

    # Test 9: Z suffix in timestamp
    input9 = {
        "sessions": [
            {"id": "z1", "start": "2026-05-01T09:00:00Z", "end": "2026-05-01T10:00:00Z", "value": 5}
        ]
    }
    res9 = solve(input9)
    assert res9["max_value"] == 5, f"Test 9 failed: {res9}"
    assert res9["selected_ids"] == ["z1"], f"Test 9 ids failed: {res9}"

    # Test 10: Multiple overlapping with tie
    input10 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T09:30:00", "value": 2},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:00:00", "value": 2},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 4}
        ]
    }
    res10 = solve(input10)
    # a+b = 4 (2 sessions), c = 4 (1 session) -> choose c
    assert res10["max_value"] == 4, f"Test 10 failed: {res10}"
    assert res10["selected_ids"] == ["c"], f"Test 10 ids failed: {res10}"

    if all_pass:
        print("All tests passed!")

# ----- Main -----
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        try:
            input_data = json.load(sys.stdin)
            output = solve(input_data)
            print(json.dumps(output, indent=2))
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input"}), file=sys.stderr)
            sys.exit(1)
```
````
