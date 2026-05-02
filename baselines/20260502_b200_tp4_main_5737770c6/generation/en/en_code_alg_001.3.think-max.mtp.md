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
- Elapsed seconds: 7.443167
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2437, "completion_tokens": 2143, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2143
- Total tokens: 2437

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
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(s)

def build_schedule(sessions_input):
    sessions = []
    rejected = []

    for i, sess in enumerate(sessions_input):
        sid = sess.get("id", f"unknown_{i}")
        reasons = []

        # Parse times
        try:
            start = parse_datetime(sess["start"])
            end = parse_datetime(sess["end"])
        except (KeyError, ValueError, TypeError):
            reasons.append("invalid datetime format")
            rejected.append({"id": sid, "reasons": reasons})
            continue

        # Validate end > start
        if end <= start:
            reasons.append("end not after start")

        # Validate value
        value = sess.get("value", 0)
        if not isinstance(value, (int, float)) or value < 0:
            reasons.append("negative or invalid value")
            value = max(0, value if isinstance(value, (int, float)) else 0)

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
        else:
            sessions.append({
                "id": sid,
                "start": start,
                "end": end,
                "value": value,
                "original_index": i
            })

    return sessions, rejected

def weighted_interval_scheduling(sessions):
    """O(n log n) DP with tie-breaking: fewer sessions, then lexicographic IDs."""
    n = len(sessions)
    if n == 0:
        return 0, [], []

    # Sort by end time
    sessions_sorted = sorted(sessions, key=lambda s: s["end"])

    # Extract end times for binary search
    end_times = [s["end"] for s in sessions_sorted]

    # Precompute p[j] = last index before j that doesn't overlap
    p = [-1] * n
    for j in range(n):
        start_j = sessions_sorted[j]["start"]
        # Binary search for rightmost end <= start_j
        idx = bisect_right(end_times, start_j) - 1
        p[j] = idx

    # DP arrays: (total_value, session_count, tuple_of_ids)
    # We'll store dp as list of tuples for comparison
    dp = [(0, 0, ())] * n

    for j in range(n):
        # Option 1: exclude session j
        exclude_val = dp[j-1] if j > 0 else (0, 0, ())

        # Option 2: include session j
        prev = dp[p[j]] if p[j] >= 0 else (0, 0, ())
        include_val = (
            prev[0] + sessions_sorted[j]["value"],
            prev[1] + 1,
            prev[2] + (sessions_sorted[j]["id"],)
        )

        # Compare: higher value wins; if equal, fewer sessions; if still equal, lexicographic ids
        if include_val[0] > exclude_val[0]:
            dp[j] = include_val
        elif include_val[0] < exclude_val[0]:
            dp[j] = exclude_val
        else:
            # Equal value - choose fewer sessions
            if include_val[1] < exclude_val[1]:
                dp[j] = include_val
            elif include_val[1] > exclude_val[1]:
                dp[j] = exclude_val
            else:
                # Equal sessions - lexicographic tuple comparison
                if include_val[2] < exclude_val[2]:
                    dp[j] = include_val
                else:
                    dp[j] = exclude_val

    max_value, count, id_tuple = dp[-1]
    selected_ids = list(id_tuple)

    return max_value, selected_ids, sessions_sorted

def solve(data):
    sessions_input = data.get("sessions", [])
    sessions, rejected = build_schedule(sessions_input)

    if sessions:
        max_value, selected_ids, _ = weighted_interval_scheduling(sessions)
    else:
        max_value = 0
        selected_ids = []

    # Ensure chronological order (already sorted by DP)
    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return result

def run_tests():
    """Built-in tests."""
    test_cases = []

    # Test 1: basic case
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 3},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
            ]
        },
        "expected": {
            "max_value": 9,
            "selected_ids": ["a", "c"],
            "rejected": []
        }
    })

    # Test 2: overlapping with tie-breaking (fewer sessions)
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
                {"id": "y", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 10},
                {"id": "z", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}
            ]
        },
        "expected": {
            "max_value": 10,
            "selected_ids": ["x"],  # or ["z"], same value, fewer sessions (1 vs 1) -> lexicographic "x" < "z"
            "rejected": []
        }
    })

    # Test 3: rejected sessions
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "bad_end", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 3},
                {"id": "neg_val", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": -1},
                {"id": "no_val", "start": "2026-05-01T12:00:00", "end": "2026-05-01T13:00:00"}
            ]
        },
        "expected": {
            "max_value": 5,
            "selected_ids": ["good"],
            "rejected": [
                {"id": "bad_end", "reasons": ["end not after start"]},
                {"id": "neg_val", "reasons": ["negative or invalid value"]},
                {"id": "no_val", "reasons": ["invalid datetime format"]}
            ]
        }
    })

    # Test 4: tie-break lexicographic when same value and same count
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
            ]
        },
        "expected": {
            "max_value": 5,
            "selected_ids": ["a"],  # both value 5, count 1, "a" < "b"
            "rejected": []
        }
    })

    # Test 5: empty input
    test_cases.append({
        "input": {"sessions": []},
        "expected": {
            "max_value": 0,
            "selected_ids": [],
            "rejected": []
        }
    })

    for i, tc in enumerate(test_cases):
        result = solve(tc["input"])
        assert result == tc["expected"], f"Test {i+1} failed: {result} != {tc['expected']}"

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    result = solve(data)
    print(json.dumps(result, default=str))

if __name__ == "__main__":
    main()
```
````
