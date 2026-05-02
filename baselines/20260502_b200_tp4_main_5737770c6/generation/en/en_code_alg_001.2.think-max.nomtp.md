# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 18.24485
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2853, "completion_tokens": 2559, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2559
- Total tokens: 2853

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
    return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id", "unknown")
        reasons = []
        try:
            start = parse_timestamp(session["start"])
            end = parse_timestamp(session["end"])
        except (KeyError, ValueError):
            reasons.append("invalid timestamp format")
            rejected.append({"id": sid, "reasons": "; ".join(reasons)})
            continue

        value = session.get("value", 0)

        if end <= start:
            reasons.append("end not after start")
        if value < 0:
            reasons.append("negative value")

        if reasons:
            rejected.append({"id": sid, "reasons": "; ".join(reasons)})
        else:
            valid.append({
                "id": sid,
                "start": start,
                "end": end,
                "value": value
            })
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    O(n log n) DP solution for weighted interval scheduling.
    Returns (max_value, selected_ids) with tie-breaking.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute p[j] = last session that ends before session j starts
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]

    p = [-1] * n
    for j in range(n):
        # Binary search for rightmost session with end <= start of j
        lo, hi = 0, j - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[j]:
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = hi

    # DP arrays: dp[j] = max value up to session j
    # dp_choice[j] = (value, count, list_of_ids) for reconstruction with tie-breaking
    dp = [0] * n
    dp_choice = [None] * n

    for j in range(n):
        # Option 1: exclude session j
        if j > 0:
            exclude_val = dp[j-1]
            exclude_choice = dp_choice[j-1]
        else:
            exclude_val = 0
            exclude_choice = (0, 0, [])

        # Option 2: include session j
        include_val = sorted_sessions[j]["value"]
        if p[j] >= 0:
            include_val += dp[p[j]]
            prev_choice = dp_choice[p[j]]
        else:
            prev_choice = (0, 0, [])

        include_count = prev_choice[1] + 1
        include_ids = prev_choice[2] + [sorted_sessions[j]["id"]]
        include_choice = (include_val, include_count, include_ids)

        # Compare options with tie-breaking
        if include_val > exclude_val:
            dp[j] = include_val
            dp_choice[j] = include_choice
        elif exclude_val > include_val:
            dp[j] = exclude_val
            dp_choice[j] = exclude_choice
        else:
            # Tie: prefer fewer sessions, then lexicographically smaller
            if include_count < exclude_choice[1]:
                dp[j] = include_val
                dp_choice[j] = include_choice
            elif include_count > exclude_choice[1]:
                dp[j] = exclude_val
                dp_choice[j] = exclude_choice
            else:
                # Same count: lexicographic compare of ID lists
                if sorted(include_ids) < sorted(exclude_choice[2]):
                    dp[j] = include_val
                    dp_choice[j] = include_choice
                else:
                    dp[j] = exclude_val
                    dp_choice[j] = exclude_choice

    max_val = dp_choice[n-1][0]
    selected = dp_choice[n-1][2]

    # Return in chronological order (by start time)
    id_to_session = {s["id"]: s for s in sessions}
    selected_order = sorted(selected, key=lambda sid: (id_to_session[sid]["start"], id_to_session[sid]["id"]))

    return max_val, selected_order

def solve(input_data):
    """Main solving function."""
    sessions = input_data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return result

def run_tests():
    """Run built-in tests."""
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
        "expected_max": 9,
        "expected_selected": ["a", "c"]
    })

    # Test 2: Overlapping with higher value
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
                {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 8},
                {"id": "z", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 6}
            ]
        },
        "expected_max": 10,
        "expected_selected": ["x"]
    })

    # Test 3: Invalid sessions
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "bad1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
                {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
                {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}
            ]
        },
        "expected_max": 5,
        "expected_selected": ["good"],
        "expected_rejected_count": 2
    })

    # Test 4: Empty input
    test_cases.append({
        "input": {"sessions": []},
        "expected_max": 0,
        "expected_selected": [],
        "expected_rejected_count": 0
    })

    # Test 5: Tie-breaking (same value, different counts)
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
            ]
        },
        "expected_max": 10,
        "expected_selected": ["c"]
    })

    # Test 6: Lexicographic tie-breaking
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
            ]
        },
        "expected_max": 10,
        "expected_selected": ["a", "b"]
    })

    # Run tests
    all_passed = True
    for i, tc in enumerate(test_cases):
        result = solve(tc["input"])
        max_ok = result["max_value"] == tc["expected_max"]
        selected_ok = result["selected_ids"] == tc["expected_selected"]
        rejected_ok = True
        if "expected_rejected_count" in tc:
            rejected_ok = len(result["rejected"]) == tc["expected_rejected_count"]

        if not (max_ok and selected_ok and rejected_ok):
            print(f"Test {i+1} FAILED:", file=sys.stderr)
            print(f"  Input: {tc['input']}", file=sys.stderr)
            print(f"  Expected max: {tc['expected_max']}, got: {result['max_value']}", file=sys.stderr)
            print(f"  Expected selected: {tc['expected_selected']}, got: {result['selected_ids']}", file=sys.stderr)
            if "expected_rejected_count" in tc:
                print(f"  Expected rejected count: {tc['expected_rejected_count']}, got: {len(result['rejected'])}", file=sys.stderr)
            all_passed = False

    if all_passed:
        print("All tests passed!")
        return True
    else:
        print("Some tests failed!", file=sys.stderr)
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        input_data = json.load(sys.stdin)
        result = solve(input_data)
        print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()
```
````
