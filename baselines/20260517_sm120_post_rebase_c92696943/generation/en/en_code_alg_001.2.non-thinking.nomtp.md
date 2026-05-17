# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `default`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 28.794358
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3143, "completion_tokens": 2849, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2849
- Total tokens: 3143

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

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    seen_ids = set()
    for session in sessions:
        sid = session.get("id")
        if sid is None:
            rejected.append({"id": None, "reason": "Missing id field"})
            continue
        if sid in seen_ids:
            rejected.append({"id": sid, "reason": "Duplicate id"})
            continue
        seen_ids.add(sid)

        try:
            start = parse_timestamp(session["start"])
            end = parse_timestamp(session["end"])
        except (KeyError, ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue

        value = session.get("value")
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
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """O(n log n) DP for weighted interval scheduling."""
    if not sessions:
        return 0, [], []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Precompute p(j): largest index i < j with end <= start of j
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]

    p = [-1] * n
    for j in range(n):
        # Binary search for rightmost end <= start_j
        lo, hi = 0, j - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[j]:
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = hi

    # DP arrays
    dp = [0] * (n + 1)  # dp[i] = max value using first i sessions (0-indexed up to i-1)
    choice = [False] * n  # whether session j is selected in optimal for dp[j+1]

    for j in range(n):
        include_val = sorted_sessions[j]["value"] + (dp[p[j] + 1] if p[j] >= 0 else 0)
        exclude_val = dp[j]

        if include_val > exclude_val:
            dp[j + 1] = include_val
            choice[j] = True
        elif include_val < exclude_val:
            dp[j + 1] = exclude_val
            choice[j] = False
        else:
            # Equal value: prefer fewer sessions, then lexicographically smaller IDs
            # Reconstruct both options to compare
            include_sessions = reconstruct(sorted_sessions, p, choice, j, include=True)
            exclude_sessions = reconstruct(sorted_sessions, p, choice, j, include=False)

            if len(include_sessions) < len(exclude_sessions):
                dp[j + 1] = include_val
                choice[j] = True
            elif len(include_sessions) > len(exclude_sessions):
                dp[j + 1] = exclude_val
                choice[j] = False
            else:
                # Same length: lexicographic compare
                inc_ids = [s["id"] for s in include_sessions]
                exc_ids = [s["id"] for s in exclude_sessions]
                if inc_ids < exc_ids:
                    dp[j + 1] = include_val
                    choice[j] = True
                else:
                    dp[j + 1] = exclude_val
                    choice[j] = False

    # Reconstruct final solution
    selected = reconstruct(sorted_sessions, p, choice, n - 1, include=choice[n - 1])
    max_value = sum(s["value"] for s in selected)
    selected_ids = [s["id"] for s in selected]

    return max_value, selected_ids, sorted_sessions

def reconstruct(sorted_sessions, p, choice, j, include):
    """Reconstruct selected sessions up to index j (inclusive) with given choice for j."""
    selected = []
    i = j
    while i >= 0:
        if i == j and include:
            selected.append(sorted_sessions[i])
            i = p[i]
        elif i < j and choice[i]:
            selected.append(sorted_sessions[i])
            i = p[i]
        else:
            i -= 1
    return list(reversed(selected))

def run_tests():
    """Built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic case
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 4},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 8, f"Test 1 failed: max_val {max_val}"
    assert sel_ids == ["a", "c"], f"Test 1 failed: ids {sel_ids}"
    assert rejected == [], f"Test 1 failed: rejected {rejected}"
    tests_passed += 1

    # Test 2: Reject negative value
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert valid == [], f"Test 2 failed: valid {valid}"
    assert rejected[0]["reason"] == "Negative or invalid value", f"Test 2 failed: reason {rejected[0]['reason']}"
    tests_passed += 1

    # Test 3: Reject end <= start
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert valid == [], f"Test 3 failed: valid {valid}"
    assert rejected[0]["reason"] == "End not after start", f"Test 3 failed: reason {rejected[0]['reason']}"
    tests_passed += 1

    # Test 4: Tie-breaking (fewer sessions)
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 6}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 6, f"Test 4 failed: max_val {max_val}"
    assert sel_ids == ["c"], f"Test 4 failed: ids {sel_ids} (expected ['c'])"
    tests_passed += 1

    # Test 5: Tie-breaking (lexicographic)
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 5 failed: max_val {max_val}"
    assert sel_ids == ["c"], f"Test 5 failed: ids {sel_ids}"
    tests_passed += 1

    # Test 6: Empty input
    total_tests += 1
    data = {"sessions": []}
    valid, rejected = validate_sessions(data["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 0, f"Test 6 failed: max_val {max_val}"
    assert sel_ids == [], f"Test 6 failed: ids {sel_ids}"
    tests_passed += 1

    # Test 7: Complex overlapping
    total_tests += 1
    data = {
        "sessions": [
            {"id": "1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 6},
            {"id": "2", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
            {"id": "3", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 7},
            {"id": "4", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 13, f"Test 7 failed: max_val {max_val}"
    assert sel_ids == ["1", "3"], f"Test 7 failed: ids {sel_ids}"
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    sessions = data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)

    if valid_sessions:
        max_value, selected_ids, _ = weighted_interval_scheduling(valid_sessions)
    else:
        max_value = 0
        selected_ids = []

    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```
````
