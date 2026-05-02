# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.786267
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2828, "completion_tokens": 2534, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2534
- Total tokens: 2828

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
import sys
import json
from datetime import datetime
from bisect import bisect_right

def parse_datetime(s):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(s)

def optimize_schedule(sessions_data):
    """Weighted interval scheduling with tie-breaking."""
    sessions = sessions_data.get("sessions", [])
    valid = []
    rejected = []

    for sess in sessions:
        sid = sess.get("id", "unknown")
        reasons = []
        try:
            start = parse_datetime(sess["start"])
            end = parse_datetime(sess["end"])
        except (KeyError, ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid datetime format"})
            continue

        value = sess.get("value", 0)
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": sid, "reason": "Negative or invalid value"})
            continue

        if end <= start:
            rejected.append({"id": sid, "reason": "End not after start"})
            continue

        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })

    if not valid:
        return {"max_value": 0, "selected_ids": [], "rejected": rejected}

    # Sort by end time
    valid.sort(key=lambda x: x["end"])
    n = len(valid)
    end_times = [v["end"] for v in valid]

    # Precompute p(j): largest index i < j with end[i] <= start[j]
    p = [-1] * n
    for j in range(n):
        start_j = valid[j]["start"]
        # Binary search for rightmost end <= start_j
        idx = bisect_right(end_times, start_j) - 1
        p[j] = idx

    # DP arrays: dp[j] = max value up to job j; choice[j] = selected jobs indices (list)
    dp = [0] * n
    choice = [[] for _ in range(n)]

    # For tie-breaking: store number of sessions and lexicographic id list
    count = [0] * n
    lex_ids = [[] for _ in range(n)]

    for j in range(n):
        # Option: take job j
        take_val = valid[j]["value"] + (dp[p[j]] if p[j] >= 0 else 0)
        take_count = 1 + (count[p[j]] if p[j] >= 0 else 0)
        take_ids = (choice[p[j]] if p[j] >= 0 else []) + [valid[j]["id"]]

        # Option: skip job j
        skip_val = dp[j-1] if j > 0 else 0
        skip_count = count[j-1] if j > 0 else 0
        skip_ids = choice[j-1] if j > 0 else []

        # Compare: higher value wins
        if take_val > skip_val:
            dp[j] = take_val
            choice[j] = take_ids
            count[j] = take_count
            lex_ids[j] = take_ids
        elif skip_val > take_val:
            dp[j] = skip_val
            choice[j] = skip_ids
            count[j] = skip_count
            lex_ids[j] = skip_ids
        else:
            # Equal value: prefer fewer sessions
            if take_count < skip_count:
                dp[j] = take_val
                choice[j] = take_ids
                count[j] = take_count
                lex_ids[j] = take_ids
            elif skip_count < take_count:
                dp[j] = skip_val
                choice[j] = skip_ids
                count[j] = skip_count
                lex_ids[j] = skip_ids
            else:
                # Same count: lexicographically smaller list of IDs
                if take_ids < skip_ids:
                    dp[j] = take_val
                    choice[j] = take_ids
                    count[j] = take_count
                    lex_ids[j] = take_ids
                else:
                    dp[j] = skip_val
                    choice[j] = skip_ids
                    count[j] = skip_count
                    lex_ids[j] = skip_ids

    max_val = dp[-1]
    selected = choice[-1]

    # Ensure chronological order (already sorted by end, but IDs list is in selection order)
    # Re-sort selected by start time to be safe
    id_to_session = {s["id"]: s for s in valid}
    selected_sorted = sorted(selected, key=lambda sid: id_to_session[sid]["start"])

    return {
        "max_value": max_val,
        "selected_ids": selected_sorted,
        "rejected": rejected
    }

def run_tests():
    """Built-in tests."""
    tests_passed = 0

    # Test 1: Basic case
    data1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
        ]
    }
    result1 = optimize_schedule(data1)
    assert result1["max_value"] == 8, f"Test 1 failed: {result1}"
    assert sorted(result1["selected_ids"]) == ["a", "c"], f"Test 1 ids failed: {result1}"
    tests_passed += 1

    # Test 2: Overlapping with higher value
    data2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
            {"id": "y", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 6},
            {"id": "z", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 5}
        ]
    }
    result2 = optimize_schedule(data2)
    assert result2["max_value"] == 11, f"Test 2 failed: {result2}"
    assert sorted(result2["selected_ids"]) == ["y", "z"], f"Test 2 ids failed: {result2}"
    tests_passed += 1

    # Test 3: Rejection cases
    data3 = {
        "sessions": [
            {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad_end", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 3},
            {"id": "neg_val", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": -1},
            {"id": "no_time", "start": "invalid", "end": "2026-05-01T12:00:00", "value": 2}
        ]
    }
    result3 = optimize_schedule(data3)
    assert result3["max_value"] == 5, f"Test 3 value failed: {result3}"
    assert result3["selected_ids"] == ["good"], f"Test 3 ids failed: {result3}"
    assert len(result3["rejected"]) == 3, f"Test 3 reject count failed: {result3}"
    tests_passed += 1

    # Test 4: Tie-breaking: same value, different counts
    data4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    result4 = optimize_schedule(data4)
    # Value 10 from single session vs 10 from two sessions -> pick single
    assert result4["max_value"] == 10, f"Test 4 value failed: {result4}"
    assert result4["selected_ids"] == ["c"], f"Test 4 ids failed: {result4}"
    tests_passed += 1

    # Test 5: Tie-breaking same value and count, different lex order
    data5 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    }
    result5 = optimize_schedule(data5)
    # All non-overlapping, sum=15, all three selected, lex order ["a","b","c"]
    assert result5["max_value"] == 15, f"Test 5 value failed: {result5}"
    assert result5["selected_ids"] == ["a", "b", "c"], f"Test 5 ids failed: {result5}"
    tests_passed += 1

    # Test 6: Empty input
    data6 = {"sessions": []}
    result6 = optimize_schedule(data6)
    assert result6["max_value"] == 0, f"Test 6 failed: {result6}"
    assert result6["selected_ids"] == [], f"Test 6 ids failed"
    tests_passed += 1

    print(f"All {tests_passed} tests passed.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        data = json.load(sys.stdin)
        result = optimize_schedule(data)
        # Convert datetime objects to strings for JSON output
        print(json.dumps(result, default=str, indent=2))
```
````
