# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 20.239767
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2779, "completion_tokens": 2485, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2485
- Total tokens: 2779

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
    """Parse ISO-like timestamp without timezone info."""
    try:
        return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None

def validate_sessions(sessions):
    """Validate sessions and split into valid/rejected."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id", "unknown")
        start_str = session.get("start")
        end_str = session.get("end")
        value = session.get("value")

        errors = []
        if not isinstance(sid, str) or not sid:
            errors.append("missing or invalid id")
        if not start_str or not isinstance(start_str, str):
            errors.append("missing or invalid start")
        if not end_str or not isinstance(end_str, str):
            errors.append("missing or invalid end")
        if value is None or not isinstance(value, (int, float)):
            errors.append("missing or invalid value")
        if errors:
            rejected.append({"id": sid, "reason": "; ".join(errors)})
            continue

        start = parse_timestamp(start_str)
        end = parse_timestamp(end_str)
        if start is None:
            errors.append("cannot parse start timestamp")
        if end is None:
            errors.append("cannot parse end timestamp")
        if errors:
            rejected.append({"id": sid, "reason": "; ".join(errors)})
            continue

        if end <= start:
            rejected.append({"id": sid, "reason": "end not after start"})
            continue
        if value < 0:
            rejected.append({"id": sid, "reason": "negative value"})
            continue

        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })

    return valid, rejected

def weighted_interval_scheduling(valid_sessions):
    """O(n log n) DP with tie-breaking: max value, then minimize sessions, then lexicographic."""
    if not valid_sessions:
        return {"max_value": 0, "selected_ids": []}

    # Sort by end time
    sorted_sessions = sorted(valid_sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Create array of end times for binary search
    end_times = [s["end"] for s in sorted_sessions]

    # Find p(j) = last compatible session index (0-based, -1 if none)
    p = [-1] * n
    for j in range(n):
        # Binary search for rightmost session ending <= start of session j
        lo, hi = 0, j - 1
        best = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= sorted_sessions[j]["start"]:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = best

    # DP tables: max_value, session_count, lexicographic_key (tuple of ids)
    dp_value = [0] * (n + 1)
    dp_count = [0] * (n + 1)
    dp_lex = [tuple() for _ in range(n + 1)]

    # Choice tracking: 0 = exclude, 1 = include
    choice = [0] * (n + 1)

    for j in range(1, n + 1):
        s = sorted_sessions[j - 1]

        # Option 1: exclude session j-1
        exclude_val = dp_value[j - 1]
        exclude_count = dp_count[j - 1]
        exclude_lex = dp_lex[j - 1]

        # Option 2: include session j-1
        prev_idx = p[j - 1] + 1  # convert to dp index
        include_val = dp_value[prev_idx] + s["value"]
        include_count = dp_count[prev_idx] + 1
        include_lex = dp_lex[prev_idx] + (s["id"],)

        # Compare options
        better = False
        if include_val > exclude_val:
            better = True
        elif include_val == exclude_val:
            if include_count < exclude_count:
                better = True
            elif include_count == exclude_count:
                # Lexicographic comparison of tuple of ids
                if include_lex < exclude_lex:
                    better = True

        if better:
            dp_value[j] = include_val
            dp_count[j] = include_count
            dp_lex[j] = include_lex
            choice[j] = 1
        else:
            dp_value[j] = exclude_val
            dp_count[j] = exclude_count
            dp_lex[j] = exclude_lex
            choice[j] = 0

    # Reconstruct
    selected_ids = []
    j = n
    while j > 0:
        if choice[j] == 1:
            s = sorted_sessions[j - 1]
            selected_ids.append(s["id"])
            j = p[j - 1] + 1
        else:
            j -= 1
    selected_ids.reverse()

    return {"max_value": dp_value[n], "selected_ids": selected_ids}

def run_tests():
    """Run built-in tests."""
    test_cases = []

    # Test 1: Basic non-overlapping
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
                {"id": "b", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 20},
            ]
        },
        "expected_max": 30,
        "expected_ids": ["a", "b"],
        "expected_rejected": 0
    })

    # Test 2: Overlapping
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 15},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 20},
                {"id": "c", "start": "2026-05-01T11:30:00", "end": "2026-05-01T13:00:00", "value": 10},
            ]
        },
        "expected_max": 25,
        "expected_ids": ["b"],
        "expected_rejected": 0
    })

    # Test 3: Tie-breaking - multiple optimal
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            ]
        },
        "expected_max": 10,
        "expected_ids": ["a", "c"],  # a,c same value as a,b but fewer sessions? No, same count -> lexicographically smaller
        "expected_rejected": 0
    })

    # Test 4: Rejection
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -1},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 10},
            ]
        },
        "expected_max": 10,
        "expected_ids": ["c"],
        "expected_rejected": 2
    })

    # Test 5: Empty
    test_cases.append({
        "input": {"sessions": []},
        "expected_max": 0,
        "expected_ids": [],
        "expected_rejected": 0
    })

    # Test 6: Lexicographic tie (same value, same count)
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
                {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            ]
        },
        "expected_max": 10,
        "expected_ids": ["a"],  # single session of value 10, z also value 10, but a < z lexicographically
        "expected_rejected": 0
    })

    for i, tc in enumerate(test_cases):
        valid, rejected = validate_sessions(tc["input"]["sessions"])
        result = weighted_interval_scheduling(valid)
        max_ok = result["max_value"] == tc["expected_max"]
        ids_ok = result["selected_ids"] == tc["expected_ids"]
        rej_ok = len(rejected) == tc["expected_rejected"]
        if not (max_ok and ids_ok and rej_ok):
            print(f"FAIL test {i+1}: got max={result['max_value']}, ids={result['selected_ids']}, rejected={len(rejected)}")
            sys.exit(1)

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    data = json.load(sys.stdin)
    sessions = data.get("sessions", [])
    valid, rejected = validate_sessions(sessions)
    result = weighted_interval_scheduling(valid)
    output = {
        "max_value": result["max_value"],
        "selected_ids": result["selected_ids"],
        "rejected": rejected
    }
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
```
````
