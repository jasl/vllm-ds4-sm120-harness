# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 24.27368
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 4497, "completion_tokens": 4203, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 4203
- Total tokens: 4497

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

def parse_timestamp(ts):
    """Parse ISO-like timestamp without timezone info."""
    # Remove trailing Z if present for compatibility
    ts = ts.replace('Z', '')
    if '.' in ts:
        ts = ts[:26]  # truncate microseconds to 6 digits
    return datetime.fromisoformat(ts)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for i, s in enumerate(sessions):
        reasons = []
        try:
            start = parse_timestamp(s['start'])
            end = parse_timestamp(s['end'])
        except (ValueError, KeyError) as e:
            reasons.append("Invalid timestamp")
            rejected.append({"id": s.get('id', f"index_{i}"), "reason": "; ".join(reasons)})
            continue

        if end <= start:
            reasons.append("End not after start")
        if s.get('value', 0) < 0:
            reasons.append("Negative value")
        if not reasons:
            valid.append({
                'id': s['id'],
                'start': start,
                'end': end,
                'value': s['value']
            })
        else:
            rejected.append({"id": s['id'], "reason": "; ".join(reasons)})
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    O(n log n) DP for weighted interval scheduling.
    Returns (max_value, selected_ids) with tie-breaking:
    - Fewer sessions preferred
    - Lexicographically smaller list of IDs
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x['end'])
    n = len(sorted_sessions)
    end_times = [s['end'] for s in sorted_sessions]

    # Precompute p[i] = last non-overlapping job index
    p = [0] * n
    for i in range(n):
        # Binary search for the rightmost session that ends <= start of i
        idx = bisect_right(end_times, sorted_sessions[i]['start']) - 1
        p[i] = idx  # -1 if none

    # DP arrays: value and reconstruction info
    dp = [0] * (n + 1)  # dp[i] = max value using first i jobs (1-indexed)
    # For tie-breaking: store (count, id_tuple) for each dp state
    # count = number of sessions, id_tuple = tuple of IDs selected

    # We'll store reconstruction info
    choice = [None] * (n + 1)  # 0=skip, 1=take, -1=both equivalent

    # dp_count[i] = number of sessions in optimal solution for first i jobs
    dp_count = [0] * (n + 1)
    dp_ids = [()] * (n + 1)  # tuple of IDs in optimal solution

    dp[0] = 0
    dp_count[0] = 0
    dp_ids[0] = ()

    for i in range(1, n + 1):
        job = sorted_sessions[i - 1]
        # Option 1: skip this job
        skip_val = dp[i - 1]
        skip_count = dp_count[i - 1]
        skip_ids = dp_ids[i - 1]

        # Option 2: take this job
        prev_idx = p[i - 1] + 1  # convert to 1-indexed
        take_val = dp[prev_idx] + job['value']
        take_count = dp_count[prev_idx] + 1
        take_ids = dp_ids[prev_idx] + (job['id'],)

        # Compare: higher value first, then fewer sessions, then lexicographic
        if take_val > skip_val:
            dp[i] = take_val
            dp_count[i] = take_count
            dp_ids[i] = take_ids
            choice[i] = 1
        elif take_val < skip_val:
            dp[i] = skip_val
            dp_count[i] = skip_count
            dp_ids[i] = skip_ids
            choice[i] = 0
        else:
            # Same value - tie-breaking
            if take_count < skip_count:
                dp[i] = take_val
                dp_count[i] = take_count
                dp_ids[i] = take_ids
                choice[i] = 1
            elif take_count > skip_count:
                dp[i] = skip_val
                dp_count[i] = skip_count
                dp_ids[i] = skip_ids
                choice[i] = 0
            else:
                # Same count - compare lexicographically
                if take_ids < skip_ids:
                    dp[i] = take_val
                    dp_count[i] = take_count
                    dp_ids[i] = take_ids
                    choice[i] = 1
                else:
                    dp[i] = skip_val
                    dp_count[i] = skip_count
                    dp_ids[i] = skip_ids
                    choice[i] = 0

    # Reconstruct
    selected = []
    i = n
    while i > 0:
        if choice[i] == 1:
            selected.append(sorted_sessions[i - 1])
            i = p[i - 1] + 1
        else:
            i -= 1

    selected.reverse()  # Now in chronological order (sorted by end time, but start order is also fine)
    # Sort by start time for chronological order as requested
    selected.sort(key=lambda x: x['start'])
    selected_ids = [s['id'] for s in selected]

    return dp[n], selected_ids

def solve(input_data):
    """Main solving function."""
    sessions = input_data.get('sessions', [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids = weighted_interval_scheduling(valid)
    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

def run_tests():
    """Run built-in tests."""
    # Test 1: Basic example
    data1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 8},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    result1 = solve(data1)
    assert result1["max_value"] == 9, f"Test 1 failed: {result1}"
    assert result1["selected_ids"] == ["a", "c"], f"Test 1 failed: {result1}"
    assert result1["rejected"] == [], f"Test 1 failed: {result1}"

    # Test 2: Validation - negative value
    data2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]
    }
    result2 = solve(data2)
    assert result2["max_value"] == 0, f"Test 2 failed: {result2}"
    assert result2["selected_ids"] == [], f"Test 2 failed: {result2}"
    assert len(result2["rejected"]) == 1, f"Test 2 failed: {result2}"
    assert "Negative value" in result2["rejected"][0]["reason"], f"Test 2 failed: {result2}"

    # Test 3: Validation - end before start
    data3 = {
        "sessions": [
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ]
    }
    result3 = solve(data3)
    assert result3["max_value"] == 0, f"Test 3 failed: {result3}"
    assert len(result3["rejected"]) == 1, f"Test 3 failed: {result3}"
    assert "End not after start" in result3["rejected"][0]["reason"], f"Test 3 failed: {result3}"

    # Test 4: Empty input
    data4 = {"sessions": []}
    result4 = solve(data4)
    assert result4["max_value"] == 0, f"Test 4 failed: {result4}"
    assert result4["selected_ids"] == [], f"Test 4 failed: {result4}"
    assert result4["rejected"] == [], f"Test 4 failed: {result4}"

    # Test 5: Tie-breaking - same value, different count
    data5 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    result5 = solve(data5)
    # a+b gives 10 with 2 sessions, c gives 5 with 1 session -> a+b wins (more value)
    # If value was same, fewer sessions: single session vs two? Let's check
    # Actually a+b total 10, c total 5, so a+b wins
    assert result5["max_value"] == 10, f"Test 5 failed: {result5}"
    assert result5["selected_ids"] == ["a", "b"], f"Test 5 failed: {result5}"

    # Test 6: Lexicographic tie-breaking
    data6 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
        ]
    }
    result6 = solve(data6)
    # Two possible sets of 2 sessions: b+c (sum 6, ids ['b','c']), a+c (sum 6, ids ['a','c'])
    # b+c is lexicographically smaller? 'b' vs 'a' -> 'a' is smaller, so a+c wins
    # Actually compare tuples: ('a','c') < ('b','c') so a+c should be selected
    assert result6["max_value"] == 6, f"Test 6 failed: {result6}"
    assert result6["selected_ids"] == ["a", "c"], f"Test 6 failed: {result6}"

    # Test 7: Multiple optimal same value, same count, different lexicographic order
    data7 = {
        "sessions": [
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "m", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    result7 = solve(data7)
    # z+a total 10, m total 10. z+a has 2 sessions, m has 1. Fewer sessions -> m wins
    assert result7["max_value"] == 10, f"Test 7 failed: {result7}"
    assert result7["selected_ids"] == ["m"], f"Test 7 failed: {result7}"

    # Test 8: Non-overlapping sessions all valid
    data8 = {
        "sessions": [
            {"id": "1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
            {"id": "2", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 2},
            {"id": "3", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
        ]
    }
    result8 = solve(data8)
    assert result8["max_value"] == 6, f"Test 8 failed: {result8}"
    assert result8["selected_ids"] == ["1", "2", "3"], f"Test 8 failed: {result8}"

    # Test 9: All sessions overlap - pick the best single one
    data9 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 3},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 8},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T11:30:00", "value": 5}
        ]
    }
    result9 = solve(data9)
    assert result9["max_value"] == 8, f"Test 9 failed: {result9}"
    assert result9["selected_ids"] == ["b"], f"Test 9 failed: {result9}"

    # Test 10: Timestamp with 'Z' suffix
    data10 = {
        "sessions": [
            {"id": "z", "start": "2026-05-01T09:00:00Z", "end": "2026-05-01T10:00:00Z", "value": 7}
        ]
    }
    result10 = solve(data10)
    assert result10["max_value"] == 7, f"Test 10 failed: {result10}"
    assert result10["selected_ids"] == ["z"], f"Test 10 failed: {result10}"

    # Test 11: Mixed valid and invalid
    data11 = {
        "sessions": [
            {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad1", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5},
            {"id": "bad2", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -3}
        ]
    }
    result11 = solve(data11)
    assert result11["max_value"] == 5, f"Test 11 failed: {result11}"
    assert result11["selected_ids"] == ["good"], f"Test 11 failed: {result11}"
    assert len(result11["rejected"]) == 2, f"Test 11 failed: {result11}"

    # Test 12: Larger test for correctness
    data12 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T08:00:00", "end": "2026-05-01T09:00:00", "value": 2},
            {"id": "b", "start": "2026-05-01T08:30:00", "end": "2026-05-01T10:00:00", "value": 4},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    }
    result12 = solve(data12)
    # Possible: a+c+d = 10, b+d = 9, a+d = 7, c+d = 8, a+c = 5, etc.
    # a+c+d = 10 is best
    assert result12["max_value"] == 10, f"Test 12 failed: {result12}"
    assert result12["selected_ids"] == ["a", "c", "d"], f"Test 12 failed: {result12}"

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

    result = solve(input_data)
    print(json.dumps(result, default=str))

if __name__ == '__main__':
    main()
```
````
