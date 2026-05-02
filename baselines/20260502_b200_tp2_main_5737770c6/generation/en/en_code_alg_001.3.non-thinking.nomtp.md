# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 22.819019
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3099, "completion_tokens": 2805, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2805
- Total tokens: 3099

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

def parse_time(s):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(s)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get("id", "unknown")
        reasons = []
        # Check required fields
        if "start" not in sess or "end" not in sess or "value" not in sess:
            reasons.append("missing required field(s)")
        else:
            try:
                start = parse_time(sess["start"])
                end = parse_time(sess["end"])
                if end <= start:
                    reasons.append("end not after start")
                value = sess["value"]
                if not isinstance(value, (int, float)) or value < 0:
                    reasons.append("negative value")
            except (ValueError, TypeError):
                reasons.append("invalid timestamp format")

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
        else:
            valid.append((sid, start, end, value))
    return valid, rejected

def optimize(valid_sessions):
    """Weighted interval scheduling DP with tie-breaking."""
    if not valid_sessions:
        return 0, [], []

    # Sort by end time
    sorted_sessions = sorted(valid_sessions, key=lambda x: x[2])
    n = len(sorted_sessions)

    # Extract end times for binary search
    end_times = [s[2] for s in sorted_sessions]

    # Precompute p[i] = last index with end <= start of session i
    p = []
    for i in range(n):
        start_i = sorted_sessions[i][1]
        # Find rightmost index with end <= start_i
        idx = bisect_right(end_times, start_i) - 1
        p.append(idx)

    # DP arrays
    dp = [0] * (n + 1)  # dp[i] = max value using first i sessions (0..i-1)
    choice = [0] * (n + 1)  # 0=skip, 1=take

    for i in range(1, n + 1):
        idx = i - 1
        # Option 1: skip session i-1
        skip_val = dp[i-1]
        # Option 2: take session i-1
        take_val = sorted_sessions[idx][3] + dp[p[idx] + 1]

        if take_val > skip_val:
            dp[i] = take_val
            choice[i] = 1
        elif take_val < skip_val:
            dp[i] = skip_val
            choice[i] = 0
        else:
            # Equal value: choose fewer sessions, then lexicographically smaller IDs
            # Reconstruct both options to compare
            skip_ids = reconstruct(choice, sorted_sessions, p, i-1, 0)
            take_ids = reconstruct(choice, sorted_sessions, p, i-1, 1)
            if len(take_ids) < len(skip_ids):
                dp[i] = take_val
                choice[i] = 1
            elif len(take_ids) > len(skip_ids):
                dp[i] = skip_val
                choice[i] = 0
            else:
                # Same count: lexicographic compare
                take_ids_str = [str(x) for x in take_ids]
                skip_ids_str = [str(x) for x in skip_ids]
                if take_ids_str < skip_ids_str:
                    dp[i] = take_val
                    choice[i] = 1
                else:
                    dp[i] = skip_val
                    choice[i] = 0

    # Reconstruct final solution
    selected_ids = reconstruct(choice, sorted_sessions, p, n, choice[n])
    return dp[n], selected_ids, sorted_sessions

def reconstruct(choice, sessions, p, n, take_decision):
    """Reconstruct selected IDs from DP choice array."""
    ids = []
    i = n
    while i > 0:
        if i == n:
            # Use the given decision for the last element
            if take_decision == 1:
                idx = i - 1
                ids.append(sessions[idx][0])
                i = p[idx] + 1
            else:
                i -= 1
        else:
            if choice[i] == 1:
                idx = i - 1
                ids.append(sessions[idx][0])
                i = p[idx] + 1
            else:
                i -= 1
    ids.reverse()
    return ids

def solve(input_data):
    """Main solving function."""
    sessions = input_data.get("sessions", [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids, _ = optimize(valid)
    # Ensure chronological order (already sorted by end time during DP)
    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return result

# ---------- Tests ----------
def run_tests():
    """Run built-in tests."""
    test_cases = []

    # Test 1: Simple case
    test1_input = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    expected1 = {"max_value": 9, "selected_ids": ["a", "c"], "rejected": []}
    test_cases.append((test1_input, expected1, "Simple non-overlapping"))

    # Test 2: Overlapping with better value
    test2_input = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 8},
            {"id": "z", "start": "2026-05-01T11:30:00", "end": "2026-05-01T12:30:00", "value": 6}
        ]
    }
    expected2 = {"max_value": 16, "selected_ids": ["x", "z"], "rejected": []}
    test_cases.append((test2_input, expected2, "Overlapping with better value"))

    # Test 3: Ties - fewer sessions
    test3_input = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 5}
        ]
    }
    # Options: a+b (value 10, 2 sessions), c alone (value 5), a (5), b (5) -> best is a+b with 2 sessions
    expected3 = {"max_value": 10, "selected_ids": ["a", "b"], "rejected": []}
    test_cases.append((test3_input, expected3, "Tie - fewer sessions"))

    # Test 4: Ties - lexicographically smaller
    test4_input = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    }
    # Two options with same value: b+c (2 sessions) vs a+c (2 sessions) -> lexicographically ["a","c"] < ["b","c"]
    expected4 = {"max_value": 10, "selected_ids": ["a", "c"], "rejected": []}
    test_cases.append((test4_input, expected4, "Tie - lexicographically smaller"))

    # Test 5: Invalid sessions
    test5_input = {
        "sessions": [
            {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad1", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]
    }
    result5 = solve(test5_input)
    assert result5["max_value"] == 5, "Test 5 max_value"
    assert result5["selected_ids"] == ["good"], "Test 5 selected"
    assert len(result5["rejected"]) == 2, "Test 5 rejected count"
    assert any(r["id"] == "bad1" for r in result5["rejected"]), "Test 5 bad1"
    assert any(r["id"] == "bad2" for r in result5["rejected"]), "Test 5 bad2"

    # Test 6: Empty input
    test6_input = {"sessions": []}
    expected6 = {"max_value": 0, "selected_ids": [], "rejected": []}
    test_cases.append((test6_input, expected6, "Empty input"))

    # Test 7: Single session
    test7_input = {
        "sessions": [
            {"id": "only", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 42}
        ]
    }
    expected7 = {"max_value": 42, "selected_ids": ["only"], "rejected": []}
    test_cases.append((test7_input, expected7, "Single session"))

    # Run tests
    for idx, (inp, exp, desc) in enumerate(test_cases):
        result = solve(inp)
        assert result["max_value"] == exp["max_value"], f"Test {idx+1} ({desc}): max_value mismatch {result['max_value']} != {exp['max_value']}"
        assert result["selected_ids"] == exp["selected_ids"], f"Test {idx+1} ({desc}): selected_ids mismatch {result['selected_ids']} != {exp['selected_ids']}"
        assert result["rejected"] == exp["rejected"], f"Test {idx+1} ({desc}): rejected mismatch {result['rejected']} != {exp['rejected']}"
        print(f"  ✓ Test {idx+1}: {desc}")

    print("All tests passed!")

if __name__ == "__main__":
    if "--test" in sys.argv:
        run_tests()
    else:
        input_data = json.load(sys.stdin)
        result = solve(input_data)
        print(json.dumps(result, indent=2))
```
````
