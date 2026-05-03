# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 41.461693
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2935, "completion_tokens": 2641, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2641
- Total tokens: 2935

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

def parse_time(s):
    """Parse ISO-like timestamp without timezone."""
    return datetime.fromisoformat(s)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id", "unknown")
        errors = []
        # Check required fields
        if "start" not in session or "end" not in session:
            errors.append("missing start or end")
        else:
            try:
                start = parse_time(session["start"])
                end = parse_time(session["end"])
                if end <= start:
                    errors.append("end not after start")
            except (ValueError, TypeError):
                errors.append("invalid timestamp format")
        # Check value
        value = session.get("value")
        if value is None:
            errors.append("missing value")
        elif not isinstance(value, (int, float)) or value < 0:
            errors.append("negative or non-numeric value")
        # Check id presence
        if "id" not in session:
            errors.append("missing id")
        if errors:
            rejected.append({
                "session": session,
                "reasons": errors
            })
        else:
            valid.append({
                "id": sid,
                "start": parse_time(session["start"]),
                "end": parse_time(session["end"]),
                "value": value
            })
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    O(n log n) DP solution for weighted interval scheduling.
    Returns (max_value, selected_ids).
    Ties: fewer sessions, then lexicographically smaller list of IDs.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute p(j): largest index i < j with end <= start of session j
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]
    p = [-1] * n
    for j in range(n):
        # Binary search for rightmost end <= start_j
        lo, hi = 0, j-1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[j]:
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = hi  # index or -1

    # DP arrays: (value, count, ids_list) for tie-breaking
    # We store (value, -count, ids_tuple) for easy comparison (max value, min count, lexicographic ids)
    dp = [(0, 0, ())] * (n + 1)  # dp[0] = empty set

    # dp[k] corresponds to best solution considering first k sessions (indices 0..k-1)
    # We'll use dp[j+1] for session j
    for j in range(n):
        # Option 1: exclude session j
        exclude_val, exclude_negcount, exclude_ids = dp[j]
        exclude_key = (exclude_val, -exclude_negcount, exclude_ids)

        # Option 2: include session j
        if p[j] == -1:
            include_val = sorted_sessions[j]["value"]
            include_negcount = -1  # negative count for minimization
            include_ids = (sorted_sessions[j]["id"],)
        else:
            prev_val, prev_negcount, prev_ids = dp[p[j] + 1]
            include_val = prev_val + sorted_sessions[j]["value"]
            include_negcount = prev_negcount - 1  # one more session
            include_ids = prev_ids + (sorted_sessions[j]["id"],)
        include_key = (include_val, include_negcount, include_ids)

        # Choose better
        if include_key > exclude_key:
            dp[j+1] = (include_val, include_negcount, include_ids)
        else:
            dp[j+1] = (exclude_val, exclude_negcount, exclude_ids)

    max_val, negcount, ids_tuple = dp[n]
    # Convert ids_tuple to list
    selected_ids = list(ids_tuple)
    return max_val, selected_ids

def solve(input_data):
    """Main solving function."""
    sessions = input_data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Reconstruct rejected entries
    rejected_output = []
    for r in rejected:
        rejected_output.append({
            "id": r["session"].get("id", "unknown"),
            "reasons": r["reasons"]
        })

    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected_output
    }
    return output

# Tests
def run_tests():
    """Run built-in tests."""
    # Test 1: Basic case
    input1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 7}
        ]
    }
    result = solve(input1)
    assert result["max_value"] == 15, f"Expected 15, got {result['max_value']}"
    assert result["selected_ids"] == ["a", "b"], f"Expected ['a','b'], got {result['selected_ids']}"
    assert result["rejected"] == [], f"Expected no rejected, got {result['rejected']}"

    # Test 2: Overlapping with tie-breaking
    input2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    # Two optimal: {x,y} value 10, 2 sessions; {z} value 5, 1 session -> {x,y} wins on value
    result = solve(input2)
    assert result["max_value"] == 10, f"Expected 10, got {result['max_value']}"
    assert result["selected_ids"] == ["x", "y"], f"Expected ['x','y'], got {result['selected_ids']}"

    # Test 3: Tie on value, fewer sessions
    input3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10}
        ]
    }
    # Option 1: {a,b,c} value 15, 3 sessions; Option 2: {d} value 10, 1 session -> {a,b,c} wins on value
    result = solve(input3)
    assert result["max_value"] == 15, f"Expected 15, got {result['max_value']}"
    assert result["selected_ids"] == ["a", "b", "c"], f"Expected ['a','b','c'], got {result['selected_ids']}"

    # Test 4: Value tie and session count tie -> lexicographic
    input4 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    result = solve(input4)
    # Both have value 10, 2 sessions. Lexicographic: ["a","b"] < ["b","a"]
    assert result["selected_ids"] == ["a", "b"], f"Expected ['a','b'], got {result['selected_ids']}"

    # Test 5: Rejected sessions
    input5 = {
        "sessions": [
            {"id": "g", "start": "invalid", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "h", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5},
            {"id": "i", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "j", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10}
        ]
    }
    result = solve(input5)
    assert result["max_value"] == 10, f"Expected 10, got {result['max_value']}"
    assert result["selected_ids"] == ["j"], f"Expected ['j'], got {result['selected_ids']}"
    assert len(result["rejected"]) == 3, f"Expected 3 rejected, got {len(result['rejected'])}"

    # Test 6: Empty input
    input6 = {"sessions": []}
    result = solve(input6)
    assert result["max_value"] == 0
    assert result["selected_ids"] == []
    assert result["rejected"] == []

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        try:
            input_data = json.load(sys.stdin)
            output = solve(input_data)
            print(json.dumps(output, indent=2))
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON input"}), file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
```
````
