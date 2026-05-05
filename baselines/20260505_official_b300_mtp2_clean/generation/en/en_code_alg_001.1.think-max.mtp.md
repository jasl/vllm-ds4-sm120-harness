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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 13.032775
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3410, "completion_tokens": 3116, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3116
- Total tokens: 3410

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
schedule_optimizer.py - Weighted interval scheduling with reconstruction.
Reads JSON from stdin, outputs JSON with max_value, selected_ids, rejected.
"""

import sys
import json
from datetime import datetime

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone."""
    return datetime.strptime(ts_str, ISO_FORMAT)


def validate_sessions(sessions):
    """
    Validate sessions list.
    Returns (valid_sessions, rejected_list).
    """
    valid = []
    rejected = []
    seen_ids = set()

    for i, sess in enumerate(sessions):
        # Check required fields
        if not isinstance(sess, dict):
            rejected.append({"entry": i, "reason": "Not a dictionary"})
            continue

        sid = sess.get("id")
        if not isinstance(sid, str) or sid == "":
            rejected.append({"entry": i, "reason": "Missing or invalid 'id'"})
            continue

        # Check for duplicate IDs
        if sid in seen_ids:
            rejected.append({"entry": i, "id": sid, "reason": "Duplicate id"})
            continue

        # Parse timestamps
        start_str = sess.get("start")
        end_str = sess.get("end")
        if not isinstance(start_str, str) or not isinstance(end_str, str):
            rejected.append({"entry": i, "id": sid, "reason": "Missing or invalid start/end"})
            continue

        try:
            start = parse_timestamp(start_str)
            end = parse_timestamp(end_str)
        except ValueError:
            rejected.append({"entry": i, "id": sid, "reason": "Invalid timestamp format"})
            continue

        # Validate ordering
        if end <= start:
            rejected.append({"entry": i, "id": sid, "reason": "end not after start"})
            continue

        # Validate value
        value = sess.get("value")
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({"entry": i, "id": sid, "reason": "Invalid or negative value"})
            continue

        # All checks passed
        session = {
            "id": sid,
            "start": start,
            "end": end,
            "value": value,
            "orig_index": i
        }
        valid.append(session)
        seen_ids.add(sid)

    return valid, rejected


def weighted_interval_scheduling(sessions):
    """
    O(n log n) dynamic programming solution.
    Returns (max_value, selected_ids) with tie-breaking.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Precompute p[j] = last non-overlapping session index before j
    end_times = [s["end"] for s in sorted_sessions]
    p = [-1] * n

    for j in range(n):
        start_j = sorted_sessions[j]["start"]
        # Binary search for rightmost session ending <= start_j
        lo, hi = 0, j - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_j:
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = hi

    # DP arrays: (value, count, list_of_ids)
    # We'll store (value, -count, ids) for proper tie-breaking
    # Negative count because we want fewer sessions (higher negative = smaller count)
    dp_value = [0] * n
    dp_count = [0] * n
    dp_ids = [[] for _ in range(n)]

    for j in range(n):
        # Option 1: include session j
        include_val = sorted_sessions[j]["value"]
        include_cnt = 1
        include_ids = [sorted_sessions[j]["id"]]

        if p[j] != -1:
            include_val += dp_value[p[j]]
            include_cnt += dp_count[p[j]]
            include_ids = dp_ids[p[j]] + include_ids

        # Option 2: exclude session j (take best from j-1)
        if j > 0:
            exclude_val = dp_value[j - 1]
            exclude_cnt = dp_count[j - 1]
            exclude_ids = dp_ids[j - 1][:]
        else:
            exclude_val = 0
            exclude_cnt = 0
            exclude_ids = []

        # Compare: higher value first, then fewer sessions, then lexicographic
        better = False
        if include_val > exclude_val:
            better = True
        elif include_val == exclude_val:
            if include_cnt < exclude_cnt:
                better = True
            elif include_cnt == exclude_cnt:
                # Lexicographic comparison of ID lists
                if include_ids < exclude_ids:
                    better = True

        if better:
            dp_value[j] = include_val
            dp_count[j] = include_cnt
            dp_ids[j] = include_ids
        else:
            dp_value[j] = exclude_val
            dp_count[j] = exclude_cnt
            dp_ids[j] = exclude_ids

    return dp_value[-1], dp_ids[-1]


def solve(input_data):
    """Main solving function."""
    if not isinstance(input_data, dict) or "sessions" not in input_data:
        return {
            "max_value": 0,
            "selected_ids": [],
            "rejected": [{"entry": "input", "reason": "Invalid top-level format"}]
        }

    sessions = input_data["sessions"]
    if not isinstance(sessions, list):
        return {
            "max_value": 0,
            "selected_ids": [],
            "rejected": [{"entry": "input", "reason": "'sessions' is not a list"}]
        }

    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Re-index entries in rejected list (original input indices)
    # Validation already provides entry indices, but ensure consistency
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return output


def run_tests():
    """Built-in tests with assert."""
    # Test 1: Basic example
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 6},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:00:00", "value": 4}
        ]
    }
    result = solve(data)
    assert result["max_value"] == 6, f"Test 1 max_value failed: {result}"
    assert result["selected_ids"] == ["b"], f"Test 1 selected failed: {result}"
    assert result["rejected"] == [], f"Test 1 rejected failed: {result}"

    # Test 2: Overlapping and non-overlapping
    data = {
        "sessions": [
            {"id": "x", "start": "2026-01-01T00:00:00", "end": "2026-01-01T10:00:00", "value": 10},
            {"id": "y", "start": "2026-01-01T10:00:00", "end": "2026-01-01T20:00:00", "value": 10},
            {"id": "z", "start": "2026-01-01T05:00:00", "end": "2026-01-01T15:00:00", "value": 15}
        ]
    }
    result = solve(data)
    assert result["max_value"] == 20, f"Test 2 max_value failed: {result}"
    assert result["selected_ids"] == ["x", "y"], f"Test 2 selected failed: {result}"

    # Test 3: Tie-breaking - same value, choose fewer sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-01-01T00:00:00", "end": "2026-01-01T01:00:00", "value": 5},
            {"id": "b", "start": "2026-01-01T02:00:00", "end": "2026-01-01T03:00:00", "value": 5},
            {"id": "c", "start": "2026-01-01T00:00:00", "end": "2026-01-01T03:00:00", "value": 10}
        ]
    }
    result = solve(data)
    assert result["max_value"] == 10, f"Test 3 max_value failed: {result}"
    assert result["selected_ids"] == ["c"], f"Test 3 selected failed: {result}"

    # Test 4: Tie-breaking - same value, same count, lexicographic
    data = {
        "sessions": [
            {"id": "b", "start": "2026-01-01T00:00:00", "end": "2026-01-01T01:00:00", "value": 5},
            {"id": "a", "start": "2026-01-01T02:00:00", "end": "2026-01-01T03:00:00", "value": 5},
        ]
    }
    result = solve(data)
    assert result["max_value"] == 5, f"Test 4 max_value failed: {result}"
    # Both have 1 session, value 5; lexicographically ["a"] < ["b"]
    assert result["selected_ids"] == ["a"], f"Test 4 selected failed: {result}"

    # Test 5: Rejected sessions
    data = {
        "sessions": [
            {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "bad1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "bad3", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad4", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": "abc"},
            {"id": "bad5", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5, "extra": True}
        ]
    }
    result = solve(data)
    assert result["max_value"] == 10, f"Test 5 max_value failed: {result}"
    assert result["selected_ids"] == ["good"], f"Test 5 selected failed: {result}"
    assert len(result["rejected"]) == 4, f"Test 5 rejected count failed: {result}"

    # Test 6: Empty input
    data = {"sessions": []}
    result = solve(data)
    assert result["max_value"] == 0
    assert result["selected_ids"] == []
    assert result["rejected"] == []

    # Test 7: Invalid top-level
    result = solve({"not_sessions": []})
    assert result["max_value"] == 0
    assert len(result["rejected"]) == 1

    # Test 8: Duplicate IDs
    data = {
        "sessions": [
            {"id": "dup", "start": "2026-01-01T00:00:00", "end": "2026-01-01T01:00:00", "value": 1},
            {"id": "dup", "start": "2026-01-01T02:00:00", "end": "2026-01-01T03:00:00", "value": 2}
        ]
    }
    result = solve(data)
    assert result["max_value"] == 2, f"Test 8 max_value failed: {result}"
    assert result["selected_ids"] == ["dup"], f"Test 8 selected failed: {result}"
    # One duplicate rejected, one session used (the only valid one)
    assert len(result["rejected"]) == 1

    print("All tests passed.")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        output = {
            "max_value": 0,
            "selected_ids": [],
            "rejected": [{"entry": "input", "reason": f"JSON parse error: {e}"}]
        }
        print(json.dumps(output))
        return

    output = solve(input_data)
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
```
````
