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
- Elapsed seconds: 10.413114
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3220, "completion_tokens": 2926, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2926
- Total tokens: 3220

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

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return list of valid sessions and list of rejected entries."""
    valid = []
    rejected = []
    for sess in sessions:
        sess_id = sess.get("id", "unknown")
        reasons = []
        try:
            start = parse_timestamp(sess["start"])
            end = parse_timestamp(sess["end"])
        except (KeyError, ValueError, TypeError):
            reasons.append("invalid timestamp format")
            rejected.append({"id": sess_id, "reasons": reasons})
            continue

        if end <= start:
            reasons.append("end not after start")

        try:
            value = sess["value"]
            if not isinstance(value, (int, float)) or value < 0:
                reasons.append("negative value")
        except (KeyError, TypeError):
            reasons.append("missing or invalid value")

        if reasons:
            rejected.append({"id": sess_id, "reasons": reasons})
        else:
            valid.append({
                "id": sess_id,
                "start": start,
                "end": end,
                "value": value
            })
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    O(n log n) weighted interval scheduling.
    Returns (max_value, selected_ids) with tie-breaking:
    - fewer sessions preferred
    - lexicographically smaller list of IDs preferred
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Store end times for binary search
    end_times = [s["end"] for s in sorted_sessions]

    # Precompute p[i] = index of last session that ends before session i starts
    p = [-1] * n
    for i in range(n):
        start_i = sorted_sessions[i]["start"]
        # Find rightmost end_time < start_i
        j = bisect_right(end_times, start_i) - 1
        p[i] = j

    # DP arrays
    dp = [0] * (n + 1)  # dp[i] = max value using first i sessions (sorted by end)
    choice = [0] * n    # 1 = take, 0 = skip

    for i in range(1, n + 1):
        idx = i - 1
        value_i = sorted_sessions[idx]["value"]
        # Option 1: skip session i
        skip_val = dp[i - 1]
        # Option 2: take session i
        take_val = value_i + (dp[p[idx] + 1] if p[idx] >= 0 else 0)

        if take_val > skip_val:
            dp[i] = take_val
            choice[idx] = 1
        elif take_val < skip_val:
            dp[i] = skip_val
            choice[idx] = 0
        else:
            # Equal value: apply tie-breaking
            # Reconstruct both options to compare
            take_solution = reconstruct_solution(sorted_sessions, p, choice, i, force_take=True)
            skip_solution = reconstruct_solution(sorted_sessions, p, choice, i, force_skip=True)

            take_len = len(take_solution)
            skip_len = len(skip_solution)

            if take_len < skip_len:
                dp[i] = take_val
                choice[idx] = 1
            elif take_len > skip_len:
                dp[i] = skip_val
                choice[idx] = 0
            else:
                # Same length: lexicographic compare
                take_ids = [s["id"] for s in take_solution]
                skip_ids = [s["id"] for s in skip_solution]
                if take_ids < skip_ids:
                    dp[i] = take_val
                    choice[idx] = 1
                else:
                    dp[i] = skip_val
                    choice[idx] = 0

    max_value = dp[n]
    selected_ids = reconstruct_solution(sorted_sessions, p, choice, n)
    return max_value, [s["id"] for s in selected_ids]

def reconstruct_solution(sorted_sessions, p, choice, i, force_take=False, force_skip=False):
    """Reconstruct solution for first i sessions (1-indexed)."""
    selected = []
    curr = i - 1
    while curr >= 0:
        if force_take and curr == i - 1:
            take = True
        elif force_skip and curr == i - 1:
            take = False
        else:
            take = (choice[curr] == 1)

        if take:
            selected.append(sorted_sessions[curr])
            curr = p[curr]
        else:
            curr -= 1

        # Reset flags after first decision
        force_take = False
        force_skip = False

    selected.reverse()
    return selected

def optimize_from_input(data):
    """Main optimization function from parsed JSON data."""
    sessions = data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Sort selected IDs chronologically by their start time
    session_map = {s["id"]: s for s in valid_sessions}
    selected_sorted = sorted(selected_ids, key=lambda sid: session_map[sid]["start"])

    return {
        "max_value": max_value,
        "selected_ids": selected_sorted,
        "rejected": rejected
    }

# Tests
def run_tests():
    """Run built-in tests."""
    # Test 1: Basic case
    data1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    result1 = optimize_from_input(data1)
    assert result1["max_value"] == 9, f"Expected 9, got {result1['max_value']}"
    assert result1["selected_ids"] == ["a", "c"], f"Expected ['a','c'], got {result1['selected_ids']}"
    assert len(result1["rejected"]) == 0
    print("Test 1 passed: Basic case")

    # Test 2: Reject invalid sessions
    data2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "z", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
        ]
    }
    result2 = optimize_from_input(data2)
    assert result2["max_value"] == 3, f"Expected 3, got {result2['max_value']}"
    assert result2["selected_ids"] == ["z"], f"Expected ['z'], got {result2['selected_ids']}"
    assert len(result2["rejected"]) == 2
    print("Test 2 passed: Rejection logic")

    # Test 3: Tie-breaking - fewer sessions
    data3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    result3 = optimize_from_input(data3)
    assert result3["max_value"] == 10, f"Expected 10, got {result3['max_value']}"
    assert result3["selected_ids"] == ["c"], f"Expected ['c'], got {result3['selected_ids']}"
    print("Test 3 passed: Tie-breaking fewer sessions")

    # Test 4: Tie-breaking - lexicographic
    data4 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        ]
    }
    result4 = optimize_from_input(data4)
    assert result4["max_value"] == 10, f"Expected 10, got {result4['max_value']}"
    assert result4["selected_ids"] == ["a", "b"], f"Expected ['a','b'], got {result4['selected_ids']}"
    print("Test 4 passed: Tie-breaking lexicographic")

    # Test 5: Empty sessions
    data5 = {"sessions": []}
    result5 = optimize_from_input(data5)
    assert result5["max_value"] == 0, f"Expected 0, got {result5['max_value']}"
    assert result5["selected_ids"] == [], f"Expected [], got {result5['selected_ids']}"
    print("Test 5 passed: Empty input")

    # Test 6: Single session
    data6 = {
        "sessions": [
            {"id": "solo", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 42}
        ]
    }
    result6 = optimize_from_input(data6)
    assert result6["max_value"] == 42
    assert result6["selected_ids"] == ["solo"]
    print("Test 6 passed: Single session")

    # Test 7: Complex overlapping
    data7 = {
        "sessions": [
            {"id": "1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 8},
            {"id": "2", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 9},
            {"id": "3", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 7},
            {"id": "4", "start": "2026-05-01T12:00:00", "end": "2026-05-01T14:00:00", "value": 6}
        ]
    }
    result7 = optimize_from_input(data7)
    # Best: 1+4 = 14 or 2+? 2+4 overlaps? 2 ends 12, 4 starts 12 -> ok 9+6=15? check: 9+6=15 > 14
    assert result7["max_value"] == 15, f"Expected 15, got {result7['max_value']}"
    assert result7["selected_ids"] == ["2", "4"], f"Expected ['2','4'], got {result7['selected_ids']}"
    print("Test 7 passed: Complex overlapping")

    print("\nAll tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        try:
            data = json.load(sys.stdin)
            result = optimize_from_input(data)
            print(json.dumps(result, default=str))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {str(e)}"}), file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
```
````
