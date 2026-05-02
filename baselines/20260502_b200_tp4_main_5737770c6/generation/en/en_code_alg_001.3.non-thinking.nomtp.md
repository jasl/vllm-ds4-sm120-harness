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
- Elapsed seconds: 21.875208
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3352, "completion_tokens": 3058, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3058
- Total tokens: 3352

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

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone."""
    try:
        return datetime.fromisoformat(ts_str)
    except ValueError:
        return None

def build_sessions(data):
    """Parse and validate sessions from input data."""
    sessions_raw = data.get("sessions", [])
    valid_sessions = []
    rejected = []

    for idx, sess in enumerate(sessions_raw):
        sid = sess.get("id", f"unknown_{idx}")
        start_str = sess.get("start", "")
        end_str = sess.get("end", "")
        value = sess.get("value", 0)

        reasons = []

        # Parse timestamps
        start = parse_timestamp(start_str)
        end = parse_timestamp(end_str)

        if start is None:
            reasons.append("invalid start timestamp")
        if end is None:
            reasons.append("invalid end timestamp")

        if start is not None and end is not None:
            if end <= start:
                reasons.append("end not after start")

        if not isinstance(value, (int, float)):
            reasons.append("non-numeric value")
        elif value < 0:
            reasons.append("negative value")

        if reasons:
            rejected.append({
                "id": sid,
                "reason": "; ".join(reasons)
            })
        else:
            valid_sessions.append({
                "id": sid,
                "start": start,
                "end": end,
                "value": value,
                "orig_index": idx
            })

    return valid_sessions, rejected

def weighted_interval_scheduling(sessions):
    """O(n log n) DP for weighted interval scheduling with tie-breaking."""
    if not sessions:
        return [], 0

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: (s["end"], s["start"], s["id"]))
    n = len(sorted_sessions)
    end_times = [s["end"] for s in sorted_sessions]

    # Precompute p[i] = last non-overlapping index
    p = [-1] * n
    start_times = [s["start"] for s in sorted_sessions]
    for i in range(n):
        idx = bisect_right(end_times, start_times[i]) - 1
        p[i] = idx

    # DP arrays: (max_value, neg_session_count, lex_tuple) for tie-breaking
    # lex_tuple is tuple of negative ordinals (for lexicographic ordering of IDs in reverse)
    dp_value = [0] * (n + 1)
    dp_count = [0] * (n + 1)
    dp_lex = [()] * (n + 1)  # tuple of chars for lexicographic comparison

    for i in range(1, n + 1):
        # Option 1: exclude session i-1
        excl_value = dp_value[i - 1]
        excl_count = dp_count[i - 1]
        excl_lex = dp_lex[i - 1]

        # Option 2: include session i-1
        prev = p[i - 1] + 1  # index in dp
        incl_value = dp_value[prev] + sorted_sessions[i - 1]["value"]
        incl_count = dp_count[prev] + 1

        # Build lex tuple for inclusion: first the previous lex, then the id chars
        prev_lex = dp_lex[prev]
        session_id = sorted_sessions[i - 1]["id"]
        id_chars = tuple(ord(c) for c in session_id)
        incl_lex = prev_lex + id_chars

        # Compare: prefer higher value, then fewer sessions, then lexicographically smaller list
        if (incl_value > excl_value or
            (incl_value == excl_value and incl_count < excl_count) or
            (incl_value == excl_value and incl_count == excl_count and incl_lex < excl_lex)):
            dp_value[i] = incl_value
            dp_count[i] = incl_count
            dp_lex[i] = incl_lex
        else:
            dp_value[i] = excl_value
            dp_count[i] = excl_count
            dp_lex[i] = excl_lex

    # Backtrack to find selected sessions
    selected = []
    i = n
    while i > 0:
        # Check if current session was included
        prev = p[i - 1] + 1
        incl_value = dp_value[prev] + sorted_sessions[i - 1]["value"]
        incl_count = dp_count[prev] + 1
        prev_lex = dp_lex[prev]
        id_chars = tuple(ord(c) for c in sorted_sessions[i - 1]["id"])
        incl_lex = prev_lex + id_chars

        if (dp_value[i] == incl_value and dp_count[i] == incl_count and dp_lex[i] == incl_lex):
            selected.append(sorted_sessions[i - 1])
            i = prev
        else:
            i -= 1

    selected.reverse()
    return selected, dp_value[n]

def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: simple case
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
        ]
    }
    valid, rejected = build_sessions(data)
    selected, max_val = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 8, f"Test 1 failed: expected 8, got {max_val}"
    assert len(selected) == 2, f"Test 1 failed: expected 2 sessions"
    tests_passed += 1

    # Test 2: overlapping sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 8}
        ]
    }
    valid, rejected = build_sessions(data)
    selected, max_val = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 8, f"Test 2 failed: expected 8, got {max_val}"
    assert [s["id"] for s in selected] == ["b"]
    tests_passed += 1

    # Test 3: tie-breaking - same value, choose fewer sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    valid, rejected = build_sessions(data)
    selected, max_val = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 10, f"Test 3 failed: expected 10, got {max_val}"
    assert len(selected) == 1, f"Test 3 failed: expected 1 session"
    tests_passed += 1

    # Test 4: tie-breaking - same value and count, lexicographic order
    data = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    valid, rejected = build_sessions(data)
    selected, max_val = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 5, f"Test 4 failed: expected 5, got {max_val}"
    # Both are optimal: same value, same count (1), lexicographically smaller list
    # Since they overlap, only one can be chosen. The algorithm picks based on end time/sort
    # Both have same end, same start, so lex order of id decides: "a" comes first
    assert [s["id"] for s in selected] == ["a"], f"Test 4 failed: expected ['a']"
    tests_passed += 1

    # Test 5: rejection reasons
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "c", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    valid, rejected = build_sessions(data)
    total_tests += 1
    assert len(rejected) == 3, f"Test 5 failed: expected 3 rejected, got {len(rejected)}"
    tests_passed += 1

    # Test 6: chronological order output
    data = {
        "sessions": [
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 1},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 1}
        ]
    }
    valid, rejected = build_sessions(data)
    selected, max_val = weighted_interval_scheduling(valid)
    total_tests += 1
    assert [s["id"] for s in selected] == ["a", "b", "c"], f"Test 6 failed: wrong order"
    tests_passed += 1

    # Test 7: empty input
    data = {"sessions": []}
    valid, rejected = build_sessions(data)
    selected, max_val = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 0 and len(selected) == 0, "Test 7 failed"
    tests_passed += 1

    # Test 8: non-overlapping with different values
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 20},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 30}
        ]
    }
    valid, rejected = build_sessions(data)
    selected, max_val = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 60 and len(selected) == 3, "Test 8 failed"
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        raw_data = sys.stdin.read()
        data = json.loads(raw_data)
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)

    valid_sessions, rejected = build_sessions(data)
    selected_sessions, max_value = weighted_interval_scheduling(valid_sessions)

    selected_ids = [s["id"] for s in selected_sessions]

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
