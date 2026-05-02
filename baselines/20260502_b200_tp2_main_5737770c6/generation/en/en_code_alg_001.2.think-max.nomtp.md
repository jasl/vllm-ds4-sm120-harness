# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 24.869665
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3322, "completion_tokens": 3028, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3028
- Total tokens: 3322

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
    """Parse ISO-like timestamp without timezone using standard library."""
    return datetime.fromisoformat(s)


def validate_session(session):
    """Check session validity. Return (is_valid, reason)."""
    sid = session.get("id")
    start_str = session.get("start")
    end_str = session.get("end")
    value = session.get("value")

    if not isinstance(sid, str) or not sid:
        return False, "invalid or missing id"
    if not isinstance(start_str, str) or not isinstance(end_str, str):
        return False, "start or end missing or not a string"
    if not isinstance(value, (int, float)) or value != value:  # NaN check
        return False, "invalid value"

    try:
        start = parse_datetime(start_str)
        end = parse_datetime(end_str)
    except (ValueError, TypeError):
        return False, "invalid datetime format"

    if end <= start:
        return False, "end not after start"
    if value < 0:
        return False, "negative value"

    return True, None


def solve_weighted_interval_scheduling(sessions):
    """
    DP: O(n log n) weighted interval scheduling.
    Returns (max_value, selected_ids) with tie-breaking.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute p[i] = last index j < i with end <= start of i, -1 if none
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]
    p = [-1] * n
    for i in range(n):
        # find rightmost index where end <= start[i]
        idx = bisect_right(end_times, start_times[i]) - 1
        p[i] = idx

    # DP arrays: store (value, count, list_of_ids) for tie-breaking
    # We'll store dp[i] = (max_value, -count, list_of_ids) for lexicographic
    dp_value = [0] * (n + 1)
    dp_count = [0] * (n + 1)  # negative for easier comparison
    dp_ids = [[] for _ in range(n + 1)]

    for i in range(1, n + 1):
        # Option 1: skip session i-1
        val_skip = dp_value[i - 1]
        cnt_skip = dp_count[i - 1]
        ids_skip = dp_ids[i - 1]

        # Option 2: take session i-1
        prev_idx = p[i - 1] + 1  # dp index
        take_val = dp_value[prev_idx] + sorted_sessions[i - 1]["value"]
        take_cnt = dp_count[prev_idx] - 1  # negative: fewer sessions = larger
        take_ids = dp_ids[prev_idx] + [sorted_sessions[i - 1]["id"]]

        # Compare: higher value first, then fewer sessions (higher negative count),
        # then lexicographically smaller list (compare directly)
        if (take_val > val_skip or
            (take_val == val_skip and take_cnt > cnt_skip) or
            (take_val == val_skip and take_cnt == cnt_skip and take_ids < ids_skip)):
            dp_value[i] = take_val
            dp_count[i] = take_cnt
            dp_ids[i] = take_ids
        else:
            dp_value[i] = val_skip
            dp_count[i] = cnt_skip
            dp_ids[i] = ids_skip

    return dp_value[n], dp_ids[n]


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    data = json.load(sys.stdin)
    raw_sessions = data.get("sessions", [])

    valid_sessions = []
    rejected = []

    for sess in raw_sessions:
        is_valid, reason = validate_session(sess)
        if is_valid:
            try:
                start = parse_datetime(sess["start"])
                end = parse_datetime(sess["end"])
                valid_sessions.append({
                    "id": sess["id"],
                    "start": start,
                    "end": end,
                    "value": sess["value"]
                })
            except (ValueError, TypeError):
                rejected.append({"id": sess.get("id"), "reason": "invalid datetime"})
        else:
            rejected.append({"id": sess.get("id"), "reason": reason})

    max_value, selected_ids = solve_weighted_interval_scheduling(valid_sessions)

    # Sort selected_ids in chronological order (already sorted by DP)
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    print(json.dumps(output, indent=2))


def run_tests():
    """Built-in tests for edge cases and correctness."""
    passed = 0
    total = 0

    # Test 1: Basic example
    total += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    valid = []
    for s in data["sessions"]:
        if validate_session(s)[0]:
            valid.append({
                "id": s["id"],
                "start": parse_datetime(s["start"]),
                "end": parse_datetime(s["end"]),
                "value": s["value"]
            })
    val, ids = solve_weighted_interval_scheduling(valid)
    assert val == 9, f"Test 1 failed: value {val}"
    assert ids == ["a", "c"], f"Test 1 failed: ids {ids}"
    passed += 1

    # Test 2: Empty list
    total += 1
    val, ids = solve_weighted_interval_scheduling([])
    assert val == 0 and ids == [], f"Test 2 failed"
    passed += 1

    # Test 3: Single session
    total += 1
    sess = [{"id": "x", "start": parse_datetime("2026-01-01T00:00:00"),
             "end": parse_datetime("2026-01-01T01:00:00"), "value": 10}]
    val, ids = solve_weighted_interval_scheduling(sess)
    assert val == 10 and ids == ["x"], f"Test 3 failed"
    passed += 1

    # Test 4: Tie-breaking - same value, choose fewer sessions
    total += 1
    # Session A value 5, B+C each value 2 but B and C don't overlap; A overlaps both
    data = {
        "sessions": [
            {"id": "A", "start": "2026-01-01T09:00:00", "end": "2026-01-01T17:00:00", "value": 5},
            {"id": "B", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 2},
            {"id": "C", "start": "2026-01-01T11:00:00", "end": "2026-01-01T12:00:00", "value": 3}
        ]
    }
    valid = []
    for s in data["sessions"]:
        if validate_session(s)[0]:
            valid.append({
                "id": s["id"],
                "start": parse_datetime(s["start"]),
                "end": parse_datetime(s["end"]),
                "value": s["value"]
            })
    val, ids = solve_weighted_interval_scheduling(valid)
    # Both options have total value 5: A alone (1 session) vs B+C (2 sessions)
    assert val == 5, f"Test 4 value failed: {val}"
    assert ids == ["A"], f"Test 4 ids failed: {ids}"
    passed += 1

    # Test 5: Tie-breaking same value and count, choose lexicographically smaller
    total += 1
    # Two non-overlapping sessions with same value
    data = {
        "sessions": [
            {"id": "B", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 3},
            {"id": "A", "start": "2026-01-01T11:00:00", "end": "2026-01-01T12:00:00", "value": 3}
        ]
    }
    valid = []
    for s in data["sessions"]:
        if validate_session(s)[0]:
            valid.append({
                "id": s["id"],
                "start": parse_datetime(s["start"]),
                "end": parse_datetime(s["end"]),
                "value": s["value"]
            })
    val, ids = solve_weighted_interval_scheduling(valid)
    assert val == 6, f"Test 5 value failed: {val}"
    # Both orders possible, but sorted by end time: A ends at 10, B ends at 12 -> order A,B
    # The DP picks A then B, resulting in ["A", "B"] lexicographically? Actually ["A", "B"] < ["B", "A"]
    assert ids == ["A", "B"], f"Test 5 ids failed: {ids}"
    passed += 1

    # Test 6: Validator - negative value
    total += 1
    assert validate_session({"id": "x", "start": "2026-01-01T00:00:00",
                             "end": "2026-01-01T01:00:00", "value": -1}) == (False, "negative value")
    passed += 1

    # Test 7: Validator - end not after start
    total += 1
    assert validate_session({"id": "x", "start": "2026-01-01T01:00:00",
                             "end": "2026-01-01T01:00:00", "value": 1}) == (False, "end not after start")
    passed += 1

    # Test 8: Validator - invalid datetime
    total += 1
    assert validate_session({"id": "x", "start": "notadate",
                             "end": "2026-01-01T01:00:00", "value": 1}) == (False, "invalid datetime format")
    passed += 1

    # Test 9: Complex overlapping
    total += 1
    data = {
        "sessions": [
            {"id": "1", "start": "2026-01-01T09:00:00", "end": "2026-01-01T11:00:00", "value": 4},
            {"id": "2", "start": "2026-01-01T10:00:00", "end": "2026-01-01T12:00:00", "value": 5},
            {"id": "3", "start": "2026-01-01T11:30:00", "end": "2026-01-01T13:00:00", "value": 3},
            {"id": "4", "start": "2026-01-01T12:30:00", "end": "2026-01-01T14:00:00", "value": 2}
        ]
    }
    valid = []
    for s in data["sessions"]:
        if validate_session(s)[0]:
            valid.append({
                "id": s["id"],
                "start": parse_datetime(s["start"]),
                "end": parse_datetime(s["end"]),
                "value": s["value"]
            })
    val, ids = solve_weighted_interval_scheduling(valid)
    # Options: 1+3=7, 2=5, 2+4=7, 1+4=6, 3+? 3 alone=3, 4 alone=2
    # Max = 7 with either [1,3] or [2,4]. Fewer sessions tie, then lexicographic
    # [1,3] vs [2,4]: compare elements: 1<2 so [1,3] wins
    assert val == 7, f"Test 9 value failed: {val}"
    assert ids == ["1", "3"], f"Test 9 ids failed: {ids}"
    passed += 1

    print(f"All {total} tests passed ({passed}/{total}).")


if __name__ == "__main__":
    main()
```
````
