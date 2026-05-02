# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.940094
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3116, "completion_tokens": 2822, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2822
- Total tokens: 3116

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
import datetime
import bisect

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    try:
        # Try standard ISO format first
        return datetime.datetime.fromisoformat(ts_str)
    except ValueError:
        # Handle other common separators
        for sep in ['T', ' ']:
            if sep in ts_str:
                parts = ts_str.split(sep)
                date_part = parts[0]
                time_part = parts[1] if len(parts) > 1 else '00:00:00'
                # Remove trailing Z if present
                time_part = time_part.rstrip('Z')
                try:
                    dt_str = f"{date_part}T{time_part}"
                    return datetime.datetime.fromisoformat(dt_str)
                except ValueError:
                    continue
        raise ValueError(f"Cannot parse timestamp: {ts_str}")

class Session:
    def __init__(self, sid, start, end, value):
        self.id = sid
        self.start = parse_timestamp(start)
        self.end = parse_timestamp(end)
        self.value = value

    def __repr__(self):
        return f"Session({self.id}, {self.start}, {self.end}, {self.value})"

def weighted_interval_scheduling(sessions):
    """
    O(n log n) weighted interval scheduling with tie-breaking:
    - Maximize total value
    - Fewest sessions among optimal
    - Lexicographically smallest IDs among those
    """
    if not sessions:
        return 0, [], []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: (s.end, s.start, s.id))
    n = len(sorted_sessions)

    # Precompute p(j) - last non-overlapping session index
    start_times = [s.start for s in sorted_sessions]
    end_times = [s.end for s in sorted_sessions]

    p = [-1] * n
    for j in range(n):
        # Binary search for the rightmost session that ends <= start of j
        idx = bisect.bisect_right(end_times, start_times[j]) - 1
        p[j] = idx

    # DP arrays: dp_value[j], dp_count[j], dp_choice[j]
    # dp_value[j] = max total value using sessions up to j
    # dp_count[j] = number of sessions in optimal solution up to j
    # dp_choice[j] = list of IDs in optimal solution up to j (for tie-breaking)

    dp_value = [0] * n
    dp_count = [0] * n
    dp_ids = [[] for _ in range(n)]

    for j in range(n):
        # Option 1: Exclude session j
        if j == 0:
            exclude_value = 0
            exclude_count = 0
            exclude_ids = []
        else:
            exclude_value = dp_value[j-1]
            exclude_count = dp_count[j-1]
            exclude_ids = dp_ids[j-1][:]

        # Option 2: Include session j
        include_value = sorted_sessions[j].value
        include_count = 1
        include_ids = [sorted_sessions[j].id]

        if p[j] >= 0:
            include_value += dp_value[p[j]]
            include_count += dp_count[p[j]]
            include_ids = dp_ids[p[j]][:] + [sorted_sessions[j].id]

        # Choose better option
        if include_value > exclude_value:
            dp_value[j] = include_value
            dp_count[j] = include_count
            dp_ids[j] = include_ids
        elif exclude_value > include_value:
            dp_value[j] = exclude_value
            dp_count[j] = exclude_count
            dp_ids[j] = exclude_ids
        else:
            # Same value: choose fewer sessions
            if include_count < exclude_count:
                dp_value[j] = include_value
                dp_count[j] = include_count
                dp_ids[j] = include_ids
            elif exclude_count < include_count:
                dp_value[j] = exclude_value
                dp_count[j] = exclude_count
                dp_ids[j] = exclude_ids
            else:
                # Same count: choose lexicographically smaller list
                if include_ids < exclude_ids:
                    dp_value[j] = include_value
                    dp_count[j] = include_count
                    dp_ids[j] = include_ids
                else:
                    dp_value[j] = exclude_value
                    dp_count[j] = exclude_count
                    dp_ids[j] = exclude_ids

    return dp_value[n-1], dp_ids[n-1], sorted_sessions

def solve(input_data):
    sessions_raw = input_data.get("sessions", [])

    valid_sessions = []
    rejected = []

    for sess in sessions_raw:
        sid = sess.get("id", "unknown")
        start_str = sess.get("start", "")
        end_str = sess.get("end", "")
        value = sess.get("value", 0)

        # Check value
        if value < 0:
            rejected.append({"id": sid, "reason": "negative value"})
            continue

        # Parse timestamps
        try:
            start = parse_timestamp(start_str)
            end = parse_timestamp(end_str)
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "invalid timestamp format"})
            continue

        # Check end > start
        if end <= start:
            rejected.append({"id": sid, "reason": "end not after start"})
            continue

        valid_sessions.append(Session(sid, start, end, value))

    if not valid_sessions:
        return {
            "max_value": 0,
            "selected_ids": [],
            "rejected": rejected
        }

    max_value, selected_ids, sorted_sessions = weighted_interval_scheduling(valid_sessions)

    # Sort selected_ids chronologically by end time (already in order from DP)
    # But ensure they match the original session order for output
    # The DP returns them in sorted order by end time
    id_to_session = {s.id: s for s in valid_sessions}

    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

def run_tests():
    test_cases = [
        # Test 1: Basic case
        {
            "input": {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                    {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 6}
                ]
            },
            "expected": {"max_value": 6, "selected_ids": ["b"], "rejected": []}
        },
        # Test 2: Non-overlapping
        {
            "input": {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
                    {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4}
                ]
            },
            "expected": {"max_value": 7, "selected_ids": ["a", "b"], "rejected": []}
        },
        # Test 3: Reject negative value
        {
            "input": {
                "sessions": [
                    {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
                ]
            },
            "expected": {"max_value": 0, "selected_ids": [], "rejected": [{"id": "x", "reason": "negative value"}]}
        },
        # Test 4: Reject end before start
        {
            "input": {
                "sessions": [
                    {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
                ]
            },
            "expected": {"max_value": 0, "selected_ids": [], "rejected": [{"id": "y", "reason": "end not after start"}]}
        },
        # Test 5: Tie-breaking - same value, choose fewer sessions
        {
            "input": {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                    {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
                ]
            },
            "expected": {"max_value": 5, "selected_ids": ["a"], "rejected": []}
        },
        # Test 6: Tie-breaking - same value and count, lexicographic order
        {
            "input": {
                "sessions": [
                    {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}
                ]
            },
            "expected": {"max_value": 5, "selected_ids": ["a"], "rejected": []}
        },
        # Test 7: Complex scenario
        {
            "input": {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 2},
                    {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 3},
                    {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
                    {"id": "d", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 2}
                ]
            },
            "expected": {"max_value": 5, "selected_ids": ["a", "c"], "rejected": []}
        },
        # Test 8: Empty sessions
        {
            "input": {"sessions": []},
            "expected": {"max_value": 0, "selected_ids": [], "rejected": []}
        }
    ]

    all_passed = True
    for i, tc in enumerate(test_cases):
        result = solve(tc["input"])
        # Sort rejected lists for comparison
        result["rejected"].sort(key=lambda x: x["id"])
        expected_rejected = sorted(tc["expected"]["rejected"], key=lambda x: x["id"])
        if (result["max_value"] != tc["expected"]["max_value"] or
            result["selected_ids"] != tc["expected"]["selected_ids"] or
            result["rejected"] != expected_rejected):
            print(f"Test {i+1} FAILED")
            print(f"  Input: {json.dumps(tc['input'])}")
            print(f"  Expected: {json.dumps(tc['expected'])}")
            print(f"  Got: {json.dumps(result)}")
            all_passed = False
        else:
            print(f"Test {i+1} PASSED")

    if all_passed:
        print("All tests passed!")
        return True
    else:
        print("Some tests failed!")
        sys.exit(1)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        input_data = json.load(sys.stdin)
        result = solve(input_data)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```
````
