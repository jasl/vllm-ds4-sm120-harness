# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.634215
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2998, "completion_tokens": 2704, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2704
- Total tokens: 2998

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
"""schedule_optimizer.py - Weighted interval scheduling with reconstruction."""

import json
import sys
from datetime import datetime


def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    # Handle possible 'T' separator and Z suffix
    ts_str = ts_str.replace('Z', '')
    # Try standard ISO format first
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse timestamp: {ts_str}")


def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get("id", "unknown")
        reasons = []

        # Check required keys
        if "id" not in sess or "start" not in sess or "end" not in sess or "value" not in sess:
            reasons.append("missing required fields")
            rejected.append({"id": sid, "reason": "; ".join(reasons)})
            continue

        # Parse timestamps
        try:
            start = parse_timestamp(sess["start"])
            end = parse_timestamp(sess["end"])
        except (ValueError, TypeError) as e:
            reasons.append(f"invalid timestamp: {e}")
            rejected.append({"id": sid, "reason": "; ".join(reasons)})
            continue

        # Check end > start
        if end <= start:
            reasons.append("end not after start")

        # Check value non-negative
        value = sess["value"]
        if not isinstance(value, (int, float)) or value < 0:
            reasons.append("negative or invalid value")

        if reasons:
            rejected.append({"id": sid, "reason": "; ".join(reasons)})
        else:
            valid.append({
                "id": sid,
                "start": start,
                "end": end,
                "value": value
            })

    return valid, rejected


def weighted_interval_scheduling(sessions):
    """
    O(n log n) dynamic programming solution.
    Returns (max_value, selected_ids).
    If multiple optimal, prefers fewer sessions, then lexicographically smaller IDs.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Precompute p[i] - last non-overlapping session index (or -1)
    # Using binary search on end times
    end_times = [s["end"] for s in sorted_sessions]

    p = [-1] * n
    for i in range(n):
        start_i = sorted_sessions[i]["start"]
        # Binary search for rightmost end <= start_i
        lo, hi = 0, i
        while lo < hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_i:
                lo = mid + 1
            else:
                hi = mid
        p[i] = lo - 1  # last index with end <= start_i

    # DP arrays: dp[i] = (value, count, list_of_ids) for best solution up to i
    # Store as tuples: (value, -count, list) for easy comparison
    dp = [(0, 0, [])] * (n + 1)  # dp[0] is before first session

    for i in range(1, n + 1):
        sess = sorted_sessions[i - 1]
        # Option 1: exclude this session
        exclude = dp[i - 1]

        # Option 2: include this session
        incl_val = sess["value"] + dp[p[i - 1] + 1][0]
        incl_count = 1 + dp[p[i - 1] + 1][1]
        incl_ids = dp[p[i - 1] + 1][2] + [sess["id"]]

        # Compare: higher value first, then fewer sessions, then lexicographic ids
        if (incl_val > exclude[0] or
            (incl_val == exclude[0] and incl_count < exclude[1]) or
            (incl_val == exclude[0] and incl_count == exclude[1] and incl_ids < exclude[2])):
            dp[i] = (incl_val, incl_count, incl_ids)
        else:
            dp[i] = exclude

    max_value = dp[n][0]
    selected_ids = dp[n][2]

    return max_value, selected_ids


def run_tests():
    """Run built-in tests and print summary."""
    tests_passed = 0
    tests_failed = 0

    # Test 1: Basic example
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    val, ids = weighted_interval_scheduling(valid)
    assert val == 9, f"Expected 9, got {val}"
    assert ids == ["a", "c"], f"Expected ['a', 'c'], got {ids}"
    tests_passed += 1

    # Test 2: Empty input
    data = {"sessions": []}
    valid, rejected = validate_sessions(data["sessions"])
    val, ids = weighted_interval_scheduling(valid)
    assert val == 0 and ids == [], f"Expected (0, []), got ({val}, {ids})"
    tests_passed += 1

    # Test 3: Reject invalid sessions
    data = {
        "sessions": [
            {"id": "x", "start": "2026-01-01T00:00:00", "end": "2026-01-01T00:00:00", "value": 5},
            {"id": "y", "start": "2026-01-01T00:00:00", "end": "2026-01-01T01:00:00", "value": -1},
            {"id": "z", "start": "2026-01-01T00:00:00", "end": "2026-01-01T01:00:00", "value": 3}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert len(valid) == 1 and valid[0]["id"] == "z", f"Expected 1 valid (z), got {valid}"
    assert len(rejected) == 2, f"Expected 2 rejected, got {len(rejected)}"
    tests_passed += 1

    # Test 4: Tie-breaking - fewer sessions
    # Session a (value 5), b (value 5), both overlap -> choose one session
    data = {
        "sessions": [
            {"id": "b", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    val, ids = weighted_interval_scheduling(valid)
    assert val == 5, f"Expected 5, got {val}"
    assert len(ids) == 1, f"Expected 1 session, got {len(ids)}"
    assert ids == ["a"], f"Expected lexicographically smallest ['a'], got {ids}"
    tests_passed += 1

    # Test 5: Tie-breaking - lexicographic order
    data = {
        "sessions": [
            {"id": "b", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-01-01T10:30:00", "end": "2026-01-01T11:30:00", "value": 5},
            {"id": "c", "start": "2026-01-01T10:30:00", "end": "2026-01-01T11:30:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    val, ids = weighted_interval_scheduling(valid)
    assert val == 10, f"Expected 10, got {val}"
    assert ids == ["a", "b"], f"Expected ['a', 'b'], got {ids}"
    tests_passed += 1

    # Test 6: Non-overlapping with same end/start
    data = {
        "sessions": [
            {"id": "a", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 1},
            {"id": "b", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": 2}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    val, ids = weighted_interval_scheduling(valid)
    assert val == 3, f"Expected 3, got {val}"
    assert ids == ["a", "b"], f"Expected ['a', 'b'], got {ids}"
    tests_passed += 1

    # Test 7: Timestamp with microseconds
    data = {
        "sessions": [
            {"id": "t1", "start": "2026-05-01T09:00:00.123456", "end": "2026-05-01T10:30:00.654321", "value": 10}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    val, ids = weighted_interval_scheduling(valid)
    assert val == 10 and ids == ["t1"], f"Failed on microsecond timestamps"
    tests_passed += 1

    print(f"All {tests_passed} test(s) passed.", flush=True)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    # Read stdin
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        data = {"sessions": []}
    else:
        try:
            data = json.loads(raw_input)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}))
            sys.exit(1)

    sessions = data.get("sessions", [])

    # Validate
    valid_sessions, rejected = validate_sessions(sessions)

    # Optimize
    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Output
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
```
````
