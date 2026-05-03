# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 49.971262
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3471, "completion_tokens": 3177, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3177
- Total tokens: 3471

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
    # Handle possible 'Z' suffix
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1] + '+00:00'
    # Remove timezone info if present for comparison
    if '+' in ts_str or '-' in ts_str[10:]:
        ts_str = ts_str[:19]
    return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id", "unknown")
        errors = []

        # Check required fields
        if "start" not in session:
            errors.append("missing start")
        if "end" not in session:
            errors.append("missing end")
        if "value" not in session:
            errors.append("missing value")
        if errors:
            rejected.append({"id": sid, "reason": "; ".join(errors)})
            continue

        try:
            start = parse_timestamp(session["start"])
            end = parse_timestamp(session["end"])
            value = session["value"]
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "invalid timestamp or value"})
            continue

        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": sid, "reason": "negative or non-numeric value"})
            continue

        if end <= start:
            rejected.append({"id": sid, "reason": "end not after start"})
            continue

        valid.append({
            "id": str(sid),
            "start": start,
            "end": end,
            "value": value
        })

    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    O(n log n) weighted interval scheduling with tie-breaking.
    Returns (max_value, selected_ids) where selected_ids is the chosen optimal set.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Extract end times for binary search
    end_times = [s["end"] for s in sorted_sessions]

    # p[i] = index of last non-overlapping session before i
    p = [-1] * n
    for i in range(n):
        start_i = sorted_sessions[i]["start"]
        # Binary search for rightmost end <= start_i
        j = bisect_right(end_times, start_i) - 1
        p[i] = j if j >= 0 else -1

    # DP arrays: dp[i] = (value, count, id_list) for best solution up to i
    # We store tuples for tie-breaking: (value, -count, id_list) for max-heap behavior
    dp_value = [0] * n
    dp_count = [0] * n
    # Store indices for reconstruction
    dp_choice = [None] * n  # "take" or "skip"

    for i in range(n):
        # Option 1: skip session i
        skip_val = dp_value[i-1] if i > 0 else 0
        skip_cnt = dp_count[i-1] if i > 0 else 0

        # Option 2: take session i
        take_val = sorted_sessions[i]["value"]
        take_cnt = 1
        if p[i] >= 0:
            take_val += dp_value[p[i]]
            take_cnt += dp_count[p[i]]

        # Tie-breaking: higher value, then fewer sessions, then lexicographic IDs
        if take_val > skip_val:
            dp_value[i] = take_val
            dp_count[i] = take_cnt
            dp_choice[i] = "take"
        elif skip_val > take_val:
            dp_value[i] = skip_val
            dp_count[i] = skip_cnt
            dp_choice[i] = "skip"
        else:
            # Equal value - choose fewer sessions
            if take_cnt < skip_cnt:
                dp_value[i] = take_val
                dp_count[i] = take_cnt
                dp_choice[i] = "take"
            elif skip_cnt < take_cnt:
                dp_value[i] = skip_val
                dp_count[i] = skip_cnt
                dp_choice[i] = "skip"
            else:
                # Equal count - compare lexicographically
                # Get the two candidate id lists
                take_ids = []
                if p[i] >= 0:
                    take_ids = reconstruct_ids(dp_choice, sorted_sessions, p, i, "take")
                else:
                    take_ids = [sorted_sessions[i]["id"]]

                skip_ids = []
                if i > 0:
                    skip_ids = reconstruct_ids(dp_choice, sorted_sessions, p, i, "skip")

                # Compare lexicographically
                if take_ids < skip_ids:
                    dp_value[i] = take_val
                    dp_count[i] = take_cnt
                    dp_choice[i] = "take"
                else:
                    dp_value[i] = skip_val
                    dp_count[i] = skip_cnt
                    dp_choice[i] = "skip"

    # Reconstruct final solution
    selected_ids = reconstruct_ids(dp_choice, sorted_sessions, p, n-1, dp_choice[n-1])

    return dp_value[n-1], selected_ids

def reconstruct_ids(dp_choice, sorted_sessions, p, idx, choice):
    """Reconstruct the list of selected IDs based on DP choices."""
    ids = []
    i = idx

    while i >= 0:
        if dp_choice[i] == "take":
            ids.append(sorted_sessions[i]["id"])
            i = p[i]
        else:
            i -= 1

    ids.reverse()  # chronological order since sorted by end time
    return ids

def solve(sessions_data):
    """Main solving function."""
    valid_sessions, rejected = validate_sessions(sessions_data.get("sessions", []))

    if not valid_sessions:
        return {
            "max_value": 0,
            "selected_ids": [],
            "rejected": rejected
        }

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Sort selected by start time for chronological order (they're already sorted by end)
    id_to_session = {s["id"]: s for s in valid_sessions}
    selected_ids.sort(key=lambda sid: id_to_session[sid]["start"])

    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    tests_failed = 0

    # Test 1: Basic case
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 4}
        ]
    }
    result = solve(data)
    assert result["max_value"] == 5, f"Test 1 failed: expected 5, got {result['max_value']}"
    assert result["selected_ids"] == ["a"], f"Test 1 failed: expected ['a'], got {result['selected_ids']}"
    tests_passed += 1

    # Test 2: Non-overlapping all selected
    data = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 2},
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "z", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 1}
        ]
    }
    result = solve(data)
    assert result["max_value"] == 6, f"Test 2 failed: expected 6, got {result['max_value']}"
    assert result["selected_ids"] == ["x", "y", "z"], f"Test 2 failed: expected all ids"
    tests_passed += 1

    # Test 3: Rejection cases
    data = {
        "sessions": [
            {"id": "bad1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "good", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 10}
        ]
    }
    result = solve(data)
    assert result["max_value"] == 10, f"Test 3 failed: expected 10, got {result['max_value']}"
    assert result["selected_ids"] == ["good"], f"Test 3 failed: expected ['good']"
    assert len(result["rejected"]) == 2, f"Test 3 failed: expected 2 rejected"
    tests_passed += 1

    # Test 4: Tie-breaking - fewer sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    result = solve(data)
    assert result["max_value"] == 5, f"Test 4 failed: expected 5, got {result['max_value']}"
    assert len(result["selected_ids"]) == 1, f"Test 4 failed: expected 1 session"
    tests_passed += 1

    # Test 5: Lexicographic tie-breaking
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10}
        ]
    }
    # Two options: [a,b,c] = 15, [d] = 10 -> pick [a,b,c]
    result = solve(data)
    assert result["max_value"] == 15, f"Test 5 failed: expected 15, got {result['max_value']}"
    assert result["selected_ids"] == ["a", "b", "c"], f"Test 5 failed: expected ['a','b','c']"
    tests_passed += 1

    # Test 6: Empty input
    data = {"sessions": []}
    result = solve(data)
    assert result["max_value"] == 0, f"Test 6 failed: expected 0"
    assert result["selected_ids"] == [], f"Test 6 failed: expected []"
    tests_passed += 1

    # Test 7: Missing fields
    data = {
        "sessions": [
            {"id": "no_start", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "no_value", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00"}
        ]
    }
    result = solve(data)
    assert len(result["rejected"]) == 2, f"Test 7 failed: expected 2 rejected"
    tests_passed += 1

    print(f"All {tests_passed} tests passed!", file=sys.stderr)
    return True

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    # Read from stdin
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    result = solve(data)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```
````
