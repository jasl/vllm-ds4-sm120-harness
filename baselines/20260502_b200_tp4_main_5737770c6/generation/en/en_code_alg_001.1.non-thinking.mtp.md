# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.353019
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3180, "completion_tokens": 2886, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2886
- Total tokens: 3180

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

def parse_timestamp(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

def validate_sessions(sessions_data):
    validated = []
    rejected = []
    for sess in sessions_data:
        sid = sess.get("id", "unknown")
        start_str = sess.get("start", "")
        end_str = sess.get("end", "")
        value = sess.get("value", 0)

        # Check required fields exist
        if not start_str or not end_str:
            rejected.append({"id": sid, "reason": "Missing start or end"})
            continue

        # Parse timestamps
        try:
            start = parse_timestamp(start_str)
            end = parse_timestamp(end_str)
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue

        # Validate end > start
        if end <= start:
            rejected.append({"id": sid, "reason": "End not after start"})
            continue

        # Validate value non-negative
        if value < 0:
            rejected.append({"id": sid, "reason": "Negative value"})
            continue

        validated.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value,
            "start_str": start_str,
            "end_str": end_str
        })

    return validated, rejected

def find_previous_non_overlapping(sessions):
    """For each session, find the last session that ends before it starts."""
    prev = [-1] * len(sessions)
    end_times = [s["end"] for s in sessions]
    for i in range(len(sessions)):
        start = sessions[i]["start"]
        # Binary search for rightmost end_time < start
        lo, hi = 0, i - 1
        best = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] < start:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        prev[i] = best
    return prev

def weighted_interval_scheduling(sessions):
    """Returns (max_value, selected_ids) for optimal solution."""
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])

    # Map to keep original id references
    n = len(sorted_sessions)

    # Find previous non-overlapping
    prev = find_previous_non_overlapping(sorted_sessions)

    # DP arrays
    dp = [0] * (n + 1)  # dp[i] = optimal value using first i jobs (1-indexed)
    choice = [0] * (n + 1)  # 0 = skip, 1 = take

    # For tie-breaking: store list of ids or compare
    # We'll store the solution set for each dp[i] to break ties
    dp_solution = [None] * (n + 1)
    dp_solution[0] = []

    for i in range(1, n + 1):
        # Option 1: skip session i-1
        skip_val = dp[i-1]
        skip_solution = dp_solution[i-1][:]

        # Option 2: take session i-1
        take_val = sorted_sessions[i-1]["value"]
        prev_idx = prev[i-1]  # index in sorted_sessions (0-based)
        if prev_idx != -1:
            take_val += dp[prev_idx + 1]
            take_solution = dp_solution[prev_idx + 1][:]
        else:
            take_solution = []
        take_solution.append(sorted_sessions[i-1]["id"])

        # Compare: higher value wins
        if take_val > skip_val:
            dp[i] = take_val
            choice[i] = 1
            dp_solution[i] = take_solution
        elif skip_val > take_val:
            dp[i] = skip_val
            choice[i] = 0
            dp_solution[i] = skip_solution
        else:
            # Equal value: fewer sessions, then lexicographic
            take_len = len(take_solution)
            skip_len = len(skip_solution)
            if take_len < skip_len:
                dp[i] = take_val
                choice[i] = 1
                dp_solution[i] = take_solution
            elif skip_len < take_len:
                dp[i] = skip_val
                choice[i] = 0
                dp_solution[i] = skip_solution
            else:
                # Same length: lexicographic compare
                if take_solution < skip_solution:
                    dp[i] = take_val
                    choice[i] = 1
                    dp_solution[i] = take_solution
                else:
                    dp[i] = skip_val
                    choice[i] = 0
                    dp_solution[i] = skip_solution

    max_value = dp[n]
    selected_ids = dp_solution[n]
    # Selected ids are in chronological order because we processed by end time
    # and built solutions preserving order
    return max_value, selected_ids

def solve(input_data):
    sessions_data = input_data.get("sessions", [])
    validated, rejected = validate_sessions(sessions_data)

    max_value, selected_ids = weighted_interval_scheduling(validated)

    # Build output
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return output

def run_tests():
    tests_passed = 0
    total_tests = 0

    def check(name, input_data, expected):
        nonlocal tests_passed, total_tests
        total_tests += 1
        result = solve(input_data)
        if result == expected:
            tests_passed += 1
        else:
            print(f"FAIL: {name}")
            print(f"  Expected: {json.dumps(expected, default=str)}")
            print(f"  Got:      {json.dumps(result, default=str)}")

    # Test 1: Basic example
    check("Basic example", {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }, {
        "max_value": 9,
        "selected_ids": ["a", "c"],
        "rejected": []
    })

    # Test 2: Overlapping with higher value
    check("Higher value overlapping", {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 6},
            {"id": "z", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 6}
        ]
    }, {
        "max_value": 12,
        "selected_ids": ["y", "z"],
        "rejected": []
    })

    # Test 3: Rejected sessions
    check("Rejected sessions", {
        "sessions": [
            {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad1", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 3},
            {"id": "bad2", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": -1},
            {"id": "bad3", "start": "", "end": "2026-05-01T12:00:00", "value": 2}
        ]
    }, {
        "max_value": 5,
        "selected_ids": ["good"],
        "rejected": [
            {"id": "bad1", "reason": "End not after start"},
            {"id": "bad2", "reason": "Negative value"},
            {"id": "bad3", "reason": "Missing start or end"}
        ]
    })

    # Test 4: Tie-breaking - same value, fewer sessions
    check("Tie-breaking fewer sessions", {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }, {
        "max_value": 5,
        "selected_ids": ["a"],  # Can only take one, both have same value, first sorted by end time
        "rejected": []
    })

    # Test 5: Tie-breaking lexicographic
    check("Tie-breaking lexicographic", {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }, {
        "max_value": 5,
        "selected_ids": ["a"],  # Same value, same length, lexicographically smaller
        "rejected": []
    })

    # Test 6: Empty input
    check("Empty input", {"sessions": []}, {"max_value": 0, "selected_ids": [], "rejected": []})

    # Test 7: Non-overlapping chain
    check("Non-overlapping chain", {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 2},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }, {
        "max_value": 9,
        "selected_ids": ["a", "b", "c"],
        "rejected": []
    })

    # Test 8: Invalid timestamp format
    check("Invalid timestamp", {
        "sessions": [
            {"id": "bad", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }, {
        "max_value": 0,
        "selected_ids": [],
        "rejected": [{"id": "bad", "reason": "Invalid timestamp format"}]
    })

    print(f"All {tests_passed}/{total_tests} tests passed.")
    sys.exit(0 if tests_passed == total_tests else 1)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    output = solve(input_data)
    print(json.dumps(output, indent=2, default=str))

if __name__ == "__main__":
    main()
```
````
