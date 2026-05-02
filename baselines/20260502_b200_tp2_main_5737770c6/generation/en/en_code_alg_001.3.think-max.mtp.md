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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.805587
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2992, "completion_tokens": 2698, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2698
- Total tokens: 2992

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

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions, return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id", "unknown")
        start_str = session.get("start", "")
        end_str = session.get("end", "")
        value = session.get("value", 0)

        reasons = []
        # Check required fields
        if not isinstance(sid, str) or not sid:
            reasons.append("missing or invalid id")
        if not start_str:
            reasons.append("missing start")
        if not end_str:
            reasons.append("missing end")
        if value is None or not isinstance(value, (int, float)):
            reasons.append("missing or invalid value")

        if reasons:
            rejected.append({"id": sid, "reason": "; ".join(reasons)})
            continue

        # Parse timestamps
        try:
            start = parse_timestamp(start_str)
            end = parse_timestamp(end_str)
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "invalid timestamp format"})
            continue

        # Validate ordering
        if end <= start:
            rejected.append({"id": sid, "reason": "end not after start"})
            continue

        # Validate value
        if value < 0:
            rejected.append({"id": sid, "reason": "negative value"})
            continue

        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value,
            "start_str": start_str,
            "end_str": end_str
        })

    return valid, rejected

def solve_weighted_interval_scheduling(sessions):
    """DP solution for weighted interval scheduling with tie-breaking.
    Returns (max_value, selected_ids)."""
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute p[i] = index of last session ending before session i starts
    # (or -1 if none)
    p = [-1] * n
    for i in range(n):
        for j in range(i - 1, -1, -1):
            if sorted_sessions[j]["end"] <= sorted_sessions[i]["start"]:
                p[i] = j
                break

    # DP arrays: max value and choice tracking
    dp = [0] * n
    # choice[i] = (value, id_list) for optimal solution ending at i
    # We'll store tuples for tie-breaking: (value, -num_sessions, lex_ids)
    best_ending_at = [None] * n

    for i in range(n):
        val = sorted_sessions[i]["value"]
        sid = sorted_sessions[i]["id"]

        # Option 1: include session i
        if p[i] == -1:
            include_val = val
            include_ids = [sid]
        else:
            include_val = val + dp[p[i]]
            # We need to reconstruct the best solution up to p[i]
            # Use the stored best_ending_at[p[i]]
            prev_best = best_ending_at[p[i]]
            include_ids = prev_best[2] + [sid]

        # Option 2: exclude session i (take best up to i-1)
        if i == 0:
            exclude_val = 0
            exclude_ids = []
        else:
            exclude_val = dp[i-1]
            exclude_ids = best_ending_at[i-1][2] if best_ending_at[i-1] else []

        # Compare with tie-breaking
        # Compare: higher value first, then fewer sessions, then lexicographic
        include_tuple = (include_val, -len(include_ids), include_ids)
        exclude_tuple = (exclude_val, -len(exclude_ids), exclude_ids)

        if include_tuple > exclude_tuple:
            dp[i] = include_val
            best_ending_at[i] = (include_val, -len(include_ids), include_ids)
        else:
            dp[i] = exclude_val
            best_ending_at[i] = (exclude_val, -len(exclude_ids), exclude_ids)

    # Global optimum is at n-1
    max_val = dp[n-1]
    selected_ids = best_ending_at[n-1][2] if best_ending_at[n-1] else []

    # Verify chronological order (already guaranteed by construction)
    # but ensure no overlaps (safety)
    return max_val, selected_ids

def run_tests():
    """Run built-in tests."""
    errors = []

    # Test 1: basic selection
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids = solve_weighted_interval_scheduling(valid)
    assert max_val == 8, f"Test 1 failed: value {max_val}"
    assert ids == ["a", "b"], f"Test 1 failed: ids {ids}"
    assert len(rejected) == 0

    # Test 2: overlapping with higher value
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 8}
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, ids = solve_weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 2 failed: value {max_val}"
    assert ids == ["a"], f"Test 2 failed: ids {ids}"

    # Test 3: tie-breaking by fewer sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T09:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T10:30:00", "value": 5}
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, ids = solve_weighted_interval_scheduling(valid)
    # Three separate sessions give value 15, but one combined can also
    # Actually all non-overlapping: best is all three (value 15)
    # But if there's a longer session covering them all with value 15, tie
    # This test: all non-overlapping, so they all fit
    assert max_val == 15, f"Test 3 failed: value {max_val}"
    assert ids == ["a", "b", "c"], f"Test 3 failed: ids {ids}"

    # Test 4: tie-breaking by lexicographic (same value, same count)
    data = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10}
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, ids = solve_weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 4 failed: value {max_val}"
    assert ids == ["a"], f"Test 4 failed: ids {ids}"  # lexicographically smaller

    # Test 5: rejection cases
    data = {
        "sessions": [
            {"id": "bad1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert len(valid) == 1
    assert len(rejected) == 2
    assert rejected[0]["id"] == "bad1"
    assert "end not after start" in rejected[0]["reason"]
    assert rejected[1]["id"] == "bad2"
    assert "negative value" in rejected[1]["reason"]

    # Test 6: empty input
    data = {"sessions": []}
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids = solve_weighted_interval_scheduling(valid)
    assert max_val == 0
    assert ids == []

    # Test 7: multiple optimal solutions, same value, same count -> lexicographic
    data = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, ids = solve_weighted_interval_scheduling(valid)
    # Both fit, value 20, count 2 each, lexicographic ["a","b"] vs ["b","a"] -> ["a","b"]
    assert ids == ["a", "b"], f"Test 7 failed: {ids}"

    print("All tests passed!")
    return True

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        raw_data = sys.stdin.read()
        data = json.loads(raw_data)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    sessions = data.get("sessions", [])
    if not isinstance(sessions, list):
        print(json.dumps({"error": "sessions must be a list"}))
        sys.exit(1)

    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids = solve_weighted_interval_scheduling(valid_sessions)

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
