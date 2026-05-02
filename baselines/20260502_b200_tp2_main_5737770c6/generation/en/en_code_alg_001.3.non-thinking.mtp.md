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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.622923
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3239, "completion_tokens": 2945, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2945
- Total tokens: 3239

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

def parse_timestamp(ts):
    """Parse ISO-8601 timestamp without timezone info."""
    return datetime.fromisoformat(ts)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get("id")
        if not isinstance(sid, str) or sid == "":
            rejected.append({"id": sid, "reason": "missing or non-string id"})
            continue
        try:
            start = parse_timestamp(sess["start"])
            end = parse_timestamp(sess["end"])
        except (KeyError, ValueError, TypeError):
            rejected.append({"id": sid, "reason": "invalid timestamp format"})
            continue
        if end <= start:
            rejected.append({"id": sid, "reason": "end not after start"})
            continue
        value = sess.get("value")
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": sid, "reason": "negative or non-numeric value"})
            continue
        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    O(n log n) DP for weighted interval scheduling.
    Returns (max_value, selected_ids) with tie-breaking.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Precompute p(j): index of last session that ends before start of session j
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]

    p = [0] * n
    for j in range(n):
        # Binary search for rightmost session with end <= start of j
        lo, hi = 0, j-1
        best = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[j]:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = best  # -1 if none

    # DP arrays: store value and best solution for tie-breaking
    dp_val = [0] * (n + 1)  # dp_val[i] = max value with sessions 0..i-1
    dp_choice = [None] * (n + 1)  # store list of ids for tie-breaking

    dp_val[0] = 0
    dp_choice[0] = []

    for j in range(1, n + 1):
        idx = j - 1  # session index in sorted_sessions
        # Option 1: exclude session j-1
        excl_val = dp_val[j-1]
        excl_ids = dp_choice[j-1].copy()

        # Option 2: include session j-1
        inc_val = sorted_sessions[idx]["value"]
        if p[idx] != -1:
            inc_val += dp_val[p[idx] + 1]
            inc_ids = dp_choice[p[idx] + 1].copy()
        else:
            inc_ids = []
        inc_ids.append(sorted_sessions[idx]["id"])

        # Compare: prefer higher value; if tie, fewer sessions; then lexicographic
        if inc_val > excl_val:
            dp_val[j] = inc_val
            dp_choice[j] = inc_ids
        elif inc_val < excl_val:
            dp_val[j] = excl_val
            dp_choice[j] = excl_ids
        else:
            # equal value: prefer fewer sessions
            if len(inc_ids) < len(excl_ids):
                dp_val[j] = inc_val
                dp_choice[j] = inc_ids
            elif len(inc_ids) > len(excl_ids):
                dp_val[j] = excl_val
                dp_choice[j] = excl_ids
            else:
                # equal number of sessions: lexicographic compare
                inc_sorted = sorted(inc_ids)
                excl_sorted = sorted(excl_ids)
                if inc_sorted < excl_sorted:
                    dp_val[j] = inc_val
                    dp_choice[j] = inc_ids
                else:
                    dp_val[j] = excl_val
                    dp_choice[j] = excl_ids

    max_value = dp_val[n]
    selected_ids = dp_choice[n]

    # Final ordering: chronological by start time
    id_to_start = {s["id"]: s["start"] for s in sessions}
    selected_ids.sort(key=lambda x: id_to_start[x])

    return max_value, selected_ids

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)

    sessions = data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

    # Convert datetime objects to strings if any left (shouldn't be in output)
    print(json.dumps(result, default=str))

def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    tests_failed = 0

    # Test 1: Basic case
    test_input = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 4}
        ]
    }
    expected = {"max_value": 8, "selected_ids": ["a", "b"], "rejected": []}
    result = process_test_input(test_input)
    if result == expected:
        tests_passed += 1
    else:
        print(f"Test 1 failed: got {result}, expected {expected}")
        tests_failed += 1

    # Test 2: Overlapping with higher value
    test_input = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "y", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 6},
            {"id": "z", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 7}
        ]
    }
    expected = {"max_value": 13, "selected_ids": ["y", "z"], "rejected": []}
    result = process_test_input(test_input)
    if result == expected:
        tests_passed += 1
    else:
        print(f"Test 2 failed: got {result}, expected {expected}")
        tests_failed += 1

    # Test 3: Reject invalid sessions
    test_input = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -1},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
        ]
    }
    expected = {
        "max_value": 3,
        "selected_ids": ["c"],
        "rejected": [
            {"id": "a", "reason": "end not after start"},
            {"id": "b", "reason": "negative or non-numeric value"}
        ]
    }
    result = process_test_input(test_input)
    if result == expected:
        tests_passed += 1
    else:
        print(f"Test 3 failed: got {result}, expected {expected}")
        tests_failed += 1

    # Test 4: Tie-breaking - fewer sessions
    test_input = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    # Option1: a+b value=10, 2 sessions; Option2: c value=10, 1 session -> choose c
    expected = {"max_value": 10, "selected_ids": ["c"], "rejected": []}
    result = process_test_input(test_input)
    if result == expected:
        tests_passed += 1
    else:
        print(f"Test 4 failed: got {result}, expected {expected}")
        tests_failed += 1

    # Test 5: Tie-breaking - lexicographic
    test_input = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    # Both non-overlapping, sum=10, 2 sessions each; sorted ids: ["a","b"] vs ["b","a"] -> lexicographic ["a","b"]
    expected = {"max_value": 10, "selected_ids": ["a", "b"], "rejected": []}
    result = process_test_input(test_input)
    if result == expected:
        tests_passed += 1
    else:
        print(f"Test 5 failed: got {result}, expected {expected}")
        tests_failed += 1

    # Test 6: Empty input
    test_input = {"sessions": []}
    expected = {"max_value": 0, "selected_ids": [], "rejected": []}
    result = process_test_input(test_input)
    if result == expected:
        tests_passed += 1
    else:
        print(f"Test 6 failed: got {result}, expected {expected}")
        tests_failed += 1

    # Test 7: Malformed timestamp
    test_input = {
        "sessions": [
            {"id": "a", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    result = process_test_input(test_input)
    if (result["max_value"] == 0 and
        len(result["rejected"]) == 1 and
        result["rejected"][0]["reason"] == "invalid timestamp format"):
        tests_passed += 1
    else:
        print(f"Test 7 failed: got {result}")
        tests_failed += 1

    print(f"Tests: {tests_passed} passed, {tests_failed} failed")
    if tests_failed == 0:
        print("All tests passed!")

def process_test_input(test_input):
    """Helper to process test input and produce output dict."""
    sessions = test_input.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)
    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

if __name__ == "__main__":
    main()
```
````
