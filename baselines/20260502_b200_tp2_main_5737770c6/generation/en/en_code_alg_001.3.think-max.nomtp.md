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
- Elapsed seconds: 23.63147
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3154, "completion_tokens": 2860, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2860
- Total tokens: 3154

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
    """Parse ISO format timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get("id", "unknown")
        reasons = []

        # Check required fields
        if "start" not in sess or "end" not in sess:
            reasons.append("missing start or end")
        if "value" not in sess:
            reasons.append("missing value")

        # Parse timestamps
        start = None
        end = None
        if "start" in sess:
            try:
                start = parse_timestamp(sess["start"])
            except (ValueError, TypeError):
                reasons.append("invalid start timestamp")
        if "end" in sess:
            try:
                end = parse_timestamp(sess["end"])
            except (ValueError, TypeError):
                reasons.append("invalid end timestamp")

        # Check value
        value = sess.get("value")
        if value is not None and not isinstance(value, (int, float)):
            reasons.append("non-numeric value")

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
            continue

        # Check end > start
        if start and end and end <= start:
            rejected.append({"id": sid, "reasons": ["end not after start"]})
            continue

        # Check value >= 0 (negative values rejected per spec)
        if value is not None and value < 0:
            rejected.append({"id": sid, "reasons": ["negative value"]})
            continue

        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value if value is not None else 0
        })

    return valid, rejected

def weighted_interval_scheduling(valid_sessions):
    """
    O(n log n) DP with reconstruction.
    Returns (max_value, selected_ids) or (0, []) if no valid sessions.
    """
    if not valid_sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(valid_sessions, key=lambda x: x["end"])

    n = len(sorted_sessions)

    # Precompute p[i] = index of last session that ends before session i starts
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]

    p = [-1] * n
    for i in range(n):
        # Binary search for rightmost session with end <= start of session i
        lo, hi = 0, i-1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[i]:
                lo = mid + 1
            else:
                hi = mid - 1
        p[i] = hi  # hi is last compatible index, -1 if none

    # DP arrays: dp[i] = max value up to session i
    dp = [0] * n
    choices = [False] * n  # True if we include session i in optimal

    for i in range(n):
        # Value if we include session i
        include_val = sorted_sessions[i]["value"]
        if p[i] != -1:
            include_val += dp[p[i]]

        # Value if we exclude session i
        exclude_val = dp[i-1] if i > 0 else 0

        if include_val > exclude_val:
            dp[i] = include_val
            choices[i] = True
        elif include_val < exclude_val:
            dp[i] = exclude_val
            choices[i] = False
        else:
            # Tie: prefer fewer sessions, then lexicographically smaller list
            # Reconstruct both options to compare
            include_ids = reconstruct(sorted_sessions, choices[:i+1], p, i, include=True)
            exclude_ids = reconstruct(sorted_sessions, choices[:i+1], p, i, include=False)

            include_ids = [s["id"] for s in include_ids]
            exclude_ids = [s["id"] for s in exclude_ids]

            if len(include_ids) < len(exclude_ids):
                dp[i] = include_val
                choices[i] = True
            elif len(include_ids) > len(exclude_ids):
                dp[i] = exclude_val
                choices[i] = False
            else:
                # Same number of sessions: lexicographic comparison
                if include_ids < exclude_ids:  # lexicographically smaller
                    dp[i] = include_val
                    choices[i] = True
                else:
                    dp[i] = exclude_val
                    choices[i] = False

    # Reconstruct final solution
    selected = reconstruct(sorted_sessions, choices, p, n-1)
    total_value = sum(s["value"] for s in selected)
    selected_ids = [s["id"] for s in selected]

    # Ensure chronological order (already sorted by end time, same as start order)
    return total_value, selected_ids

def reconstruct(sorted_sessions, choices, p, idx, override=None):
    """Reconstruct selected sessions up to index idx."""
    selected = []
    i = idx
    while i >= 0:
        if override is not None:
            take = override
            override = None
        else:
            take = choices[i]

        if take:
            selected.append(sorted_sessions[i])
            i = p[i]
        else:
            i -= 1

    selected.reverse()
    return selected

def run_tests():
    """Built-in tests."""
    test_cases = []

    # Test 1: Simple case
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
            ]
        },
        "expected": {"max_value": 9, "selected_ids": ["a", "c"]}
    })

    # Test 2: Empty sessions
    test_cases.append({
        "input": {"sessions": []},
        "expected": {"max_value": 0, "selected_ids": []}
    })

    # Test 3: Overlapping sessions - choose best
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
                {"id": "y", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 6},
                {"id": "z", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 5}
            ]
        },
        "expected": {"max_value": 11, "selected_ids": ["y", "z"]}
    })

    # Test 4: Tie-breaking - fewer sessions
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
                {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10}
            ]
        },
        "expected": {"max_value": 10, "selected_ids": ["d"]}
    })

    # Test 5: Reject invalid sessions
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -1},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
            ]
        },
        "expected": {"max_value": 4, "selected_ids": ["c"]}
    })

    # Test 6: No valid sessions
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "bad", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5}
            ]
        },
        "expected": {"max_value": 0, "selected_ids": []}
    })

    # Test 7: Lexicographic tie-breaking
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
                {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
            ]
        },
        "expected": {"max_value": 9, "selected_ids": ["a", "b", "c"]}
    })

    # Run tests
    for i, tc in enumerate(test_cases):
        data = tc["input"]
        valid, rejected = validate_sessions(data.get("sessions", []))
        max_val, selected = weighted_interval_scheduling(valid)

        # Build output
        rejected_ids = [r["id"] for r in rejected]

        expected_val = tc["expected"]["max_value"]
        expected_ids = tc["expected"]["selected_ids"]

        if max_val != expected_val or selected != expected_ids:
            print(f"FAIL test {i+1}: expected ({expected_val}, {expected_ids}), got ({max_val}, {selected})")
            return False

    print("All tests passed!")
    return True

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    # Read JSON from stdin
    try:
        raw_data = sys.stdin.read()
        if not raw_data.strip():
            output = {"max_value": 0, "selected_ids": [], "rejected": []}
            print(json.dumps(output))
            return

        data = json.loads(raw_data)
    except json.JSONDecodeError:
        output = {"max_value": 0, "selected_ids": [], "rejected": [{"id": "unknown", "reasons": ["invalid JSON"]}]}
        print(json.dumps(output))
        return

    # Validate sessions
    valid, rejected = validate_sessions(data.get("sessions", []))

    # Run optimization
    max_val, selected = weighted_interval_scheduling(valid)

    # Build output
    output = {
        "max_value": max_val,
        "selected_ids": selected,
        "rejected": rejected
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
```
````
