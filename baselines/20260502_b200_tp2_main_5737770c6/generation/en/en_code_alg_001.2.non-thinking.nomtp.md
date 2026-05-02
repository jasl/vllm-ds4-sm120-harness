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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 52.838118
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3560, "completion_tokens": 3266, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3266
- Total tokens: 3560

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

def parse_timestamp(ts):
    """Parse ISO format timestamp without timezone info."""
    return datetime.fromisoformat(ts)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for s in sessions:
        session_id = s.get("id", "unknown")
        try:
            start = parse_timestamp(s["start"])
            end = parse_timestamp(s["end"])
            value = s["value"]
        except (KeyError, ValueError, TypeError):
            rejected.append({"id": session_id, "reason": "Invalid timestamp format or missing fields"})
            continue

        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": session_id, "reason": "Negative or invalid value"})
            continue

        if end <= start:
            rejected.append({"id": session_id, "reason": "End not after start"})
            continue

        valid.append({
            "id": session_id,
            "start": start,
            "end": end,
            "value": value
        })
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """O(n log n) DP solution for weighted interval scheduling with tie-breaking."""
    if not sessions:
        return 0, [], []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute p(j): last non-overlapping session index
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]

    p = [-1] * n
    for j in range(n):
        # Binary search for rightmost session that ends <= start of session j
        lo, hi = 0, j - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[j]:
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = hi  # hi is the last compatible index

    # DP arrays
    dp = [0] * (n + 1)  # dp[i] = max value using first i sessions (1-indexed)
    choice = [None] * (n + 1)  # 0 = skip, 1 = take

    for i in range(1, n + 1):
        idx = i - 1  # 0-indexed session index
        # Option 1: skip session i
        skip_val = dp[i - 1]

        # Option 2: take session i
        take_val = sorted_sessions[idx]["value"] + dp[p[idx] + 1]

        if take_val > skip_val:
            dp[i] = take_val
            choice[i] = 1
        elif take_val < skip_val:
            dp[i] = skip_val
            choice[i] = 0
        else:
            # Equal values: choose fewer sessions, then lexicographically smaller
            # Reconstruct both options and compare
            take_sessions = reconstruct(choice[:i] + [1], sorted_sessions[:i], p, idx)
            skip_sessions = reconstruct(choice[:i] + [0], sorted_sessions[:i], p, idx)

            # When taking session i, we use sessions from take_sessions (which includes i)
            # When skipping, we reconstruct from dp[i-1]
            take_list = take_sessions[0]
            skip_list = skip_sessions[0]

            if len(take_list) < len(skip_list):
                dp[i] = take_val
                choice[i] = 1
            elif len(take_list) > len(skip_list):
                dp[i] = skip_val
                choice[i] = 0
            else:
                # Same length: compare lexicographically
                take_ids = [s["id"] for s in take_list]
                skip_ids = [s["id"] for s in skip_list]
                if take_ids < skip_ids:
                    dp[i] = take_val
                    choice[i] = 1
                else:
                    dp[i] = skip_val
                    choice[i] = 0

    # Reconstruct optimal solution
    selected_ids = []
    i = n
    while i > 0:
        if choice[i] == 1:
            session = sorted_sessions[i - 1]
            selected_ids.append(session["id"])
            i = p[i - 1] + 1
        else:
            i -= 1
    selected_ids.reverse()

    max_value = dp[n]
    return max_value, selected_ids, sorted_sessions

def reconstruct(choice_arr, sessions, p, up_to_idx):
    """Reconstruct solution up to given index for tie-breaking."""
    selected = []
    i = up_to_idx + 1  # Convert to 1-indexed
    while i > 0:
        if choice_arr[i] == 1:
            selected.append(sessions[i - 1])
            i = p[i - 1] + 1
        else:
            i -= 1
    selected.reverse()
    return selected, sum(s["value"] for s in selected)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    sessions = data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)

    max_value, selected_ids, _ = weighted_interval_scheduling(valid_sessions)

    # Build output with selected sessions in chronological order
    selected_sessions = []
    id_to_session = {s["id"]: s for s in valid_sessions}
    for sid in selected_ids:
        s = id_to_session[sid]
        selected_sessions.append({
            "id": s["id"],
            "start": s["start"].isoformat(),
            "end": s["end"].isoformat(),
            "value": s["value"]
        })

    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "selected_sessions": selected_sessions,
        "rejected": rejected
    }

    print(json.dumps(output, indent=2))

# ----- Tests -----
def run_tests():
    tests_passed = 0
    tests_failed = 0

    # Test 1: Simple case
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 15, f"Test 1 failed: {max_val}"
    assert ids == ["a", "b"], f"Test 1 failed: {ids}"
    tests_passed += 1

    # Test 2: Overlapping sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 20}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 20, f"Test 2 failed: {max_val}"
    assert ids == ["b"], f"Test 2 failed: {ids}"
    tests_passed += 1

    # Test 3: Equal value with different lengths
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T11:30:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 5, f"Test 3 failed: {max_val}"
    # Either [a,b] or [c]; [a,b] has more sessions so choose [c]
    assert ids == ["c"], f"Test 3 failed: {ids}"
    tests_passed += 1

    # Test 4: Tie-breaking with same value and same count
    data = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 20, f"Test 4 failed: {max_val}"
    assert ids == ["a", "b"], f"Test 4 failed: {ids}"
    tests_passed += 1

    # Test 5: Rejected sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -1},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 10}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 5 failed: {max_val}"
    assert ids == ["c"], f"Test 5 failed: {ids}"
    assert len(rejected) == 2, f"Test 5 failed: {len(rejected)}"
    tests_passed += 1

    # Test 6: Empty sessions
    valid, rejected = validate_sessions([])
    max_val, ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 0, f"Test 6 failed: {max_val}"
    assert ids == [], f"Test 6 failed: {ids}"
    tests_passed += 1

    # Test 7: Complex tie-breaking (equal value, fewer sessions)
    data = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "z", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 7 failed: {max_val}"
    # Both [x] and [y,z] give value 10; [x] has fewer sessions
    assert ids == ["x"], f"Test 7 failed: {ids}"
    tests_passed += 1

    # Test 8: Invalid timestamp
    data = {
        "sessions": [
            {"id": "bad", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert len(valid) == 0, f"Test 8 failed: {len(valid)}"
    assert len(rejected) == 1, f"Test 8 failed: {len(rejected)}"
    tests_passed += 1

    # Test 9: Large number of sessions for O(n log n) check
    sessions = []
    for i in range(100):
        sessions.append({
            "id": f"s{i}",
            "start": f"2026-05-01T{i:02d}:00:00",
            "end": f"2026-05-01T{i+1:02d}:00:00",
            "value": i
        })
    valid, rejected = validate_sessions(sessions)
    max_val, ids, _ = weighted_interval_scheduling(valid)
    # All non-overlapping so all should be selected
    assert max_val == sum(range(100)), f"Test 9 failed: {max_val}"
    assert len(ids) == 100, f"Test 9 failed: {len(ids)}"
    tests_passed += 1

    print(f"All {tests_passed} tests passed!")

if __name__ == "__main__":
    main()
```
````
