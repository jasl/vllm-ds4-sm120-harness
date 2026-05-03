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
- Elapsed seconds: 55.477811
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3817, "completion_tokens": 3523, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3523
- Total tokens: 3817

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
    # Remove 'Z' if present and handle microseconds
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1]
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get('id', 'unknown')
        reasons = []

        # Check required fields
        if 'start' not in session or 'end' not in session:
            reasons.append("missing start or end")
            rejected.append({"id": sid, "reasons": reasons})
            continue

        # Parse timestamps
        try:
            start = parse_timestamp(session['start'])
            end = parse_timestamp(session['end'])
        except (ValueError, TypeError):
            reasons.append("invalid timestamp format")
            rejected.append({"id": sid, "reasons": reasons})
            continue

        # Validate order
        if end <= start:
            reasons.append("end not after start")

        # Validate value
        value = session.get('value', 0)
        if not isinstance(value, (int, float)) or value < 0:
            reasons.append("negative or invalid value")

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
        else:
            # Use original session dict with parsed timestamps
            valid.append({
                'id': sid,
                'start': start,
                'end': end,
                'value': value,
                'original': session
            })

    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    O(n log n) weighted interval scheduling with tie-breaking:
    - maximize value
    - if tie, fewer sessions
    - if still tie, lexicographically smaller list of IDs
    """
    if not sessions:
        return 0, [], []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s['end'])
    ids = [s['id'] for s in sorted_sessions]
    starts = [s['start'] for s in sorted_sessions]
    ends = [s['end'] for s in sorted_sessions]
    values = [s['value'] for s in sorted_sessions]
    n = len(sorted_sessions)

    # Binary search for last non-overlapping session
    def find_last_non_overlapping(i):
        """Find rightmost session that ends before session i starts."""
        start_time = starts[i]
        low, high = 0, i - 1
        result = -1
        while low <= high:
            mid = (low + high) // 2
            if ends[mid] <= start_time:
                result = mid
                low = mid + 1
            else:
                high = mid - 1
        return result

    # DP arrays: dp_value[i] = max value up to i, dp_sessions[i] = list of indices
    dp_value = [0] * n
    dp_sessions = [[] for _ in range(n)]  # store session indices for solution

    prev = [find_last_non_overlapping(i) for i in range(n)]

    for i in range(n):
        # Option 1: exclude current session
        exclude_value = dp_value[i-1] if i > 0 else 0
        exclude_sessions = dp_sessions[i-1][:] if i > 0 else []

        # Option 2: include current session
        include_value = values[i]
        include_sessions = [i]
        if prev[i] != -1:
            include_value += dp_value[prev[i]]
            include_sessions = dp_sessions[prev[i]][:] + [i]

        # Compare: prefer higher value
        if include_value > exclude_value:
            dp_value[i] = include_value
            dp_sessions[i] = include_sessions
        elif include_value < exclude_value:
            dp_value[i] = exclude_value
            dp_sessions[i] = exclude_sessions
        else:
            # Tie in value: choose fewer sessions
            if len(include_sessions) < len(exclude_sessions):
                dp_value[i] = include_value
                dp_sessions[i] = include_sessions
            elif len(include_sessions) > len(exclude_sessions):
                dp_value[i] = exclude_value
                dp_sessions[i] = exclude_sessions
            else:
                # Same number of sessions: lexicographically smaller IDs
                include_ids = [ids[idx] for idx in include_sessions]
                exclude_ids = [ids[idx] for idx in exclude_sessions]
                if include_ids < exclude_ids:
                    dp_value[i] = include_value
                    dp_sessions[i] = include_sessions
                else:
                    dp_value[i] = exclude_value
                    dp_sessions[i] = exclude_sessions

    max_value = dp_value[-1]
    selected_indices = dp_sessions[-1]
    selected_ids = [ids[idx] for idx in selected_indices]
    # Selected sessions in chronological order (already sorted by end time)
    selected_sessions = [sorted_sessions[idx] for idx in selected_indices]

    return max_value, selected_ids, selected_sessions

def run_test():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic example
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    valid, rejected = validate_sessions(input_data['sessions'])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 9, f"Test 1 failed: expected 9, got {max_val}"
    assert sel_ids == ['a', 'c'], f"Test 1 failed: expected ['a','c'], got {sel_ids}"
    tests_passed += 1

    # Test 2: Empty input
    total_tests += 1
    valid, rejected = validate_sessions([])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 0 and sel_ids == [], "Test 2 failed"
    tests_passed += 1

    # Test 3: Overlapping sessions - pick highest value
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "x", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": 10},
            {"id": "y", "start": "2026-01-01T10:30:00", "end": "2026-01-01T11:30:00", "value": 8},
            {"id": "z", "start": "2026-01-01T11:00:00", "end": "2026-01-01T12:00:00", "value": 7}
        ]
    }
    valid, rejected = validate_sessions(input_data['sessions'])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 17, f"Test 3 failed: expected 17, got {max_val}"
    assert sel_ids == ['x', 'z'], f"Test 3 failed: expected ['x','z'], got {sel_ids}"
    tests_passed += 1

    # Test 4: Invalid sessions
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "bad1", "start": "2026-01-01T10:00:00", "end": "2026-01-01T09:00:00", "value": 5},
            {"id": "bad2", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": -1},
            {"id": "good", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(input_data['sessions'])
    assert len(rejected) == 2, f"Test 4 failed: expected 2 rejected, got {len(rejected)}"
    assert len(valid) == 1, f"Test 4 failed: expected 1 valid, got {len(valid)}"
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 5 and sel_ids == ['good'], "Test 4 failed"
    tests_passed += 1

    # Test 5: Tie-breaking - fewer sessions
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "a", "start": "2026-01-01T10:00:00", "end": "2026-01-01T12:00:00", "value": 10},
            {"id": "b", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-01-01T11:00:00", "end": "2026-01-01T12:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(input_data['sessions'])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 5 failed: expected 10, got {max_val}"
    assert sel_ids == ['a'], f"Test 5 failed: expected ['a'], got {sel_ids}"
    tests_passed += 1

    # Test 6: Tie-breaking - lexicographically smaller
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "b", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-01-01T11:00:00", "end": "2026-01-01T12:00:00", "value": 5},
            {"id": "a", "start": "2026-01-01T10:30:00", "end": "2026-01-01T12:30:00", "value": 10}
        ]
    }
    valid, rejected = validate_sessions(input_data['sessions'])
    # Two solutions: ['a']=10, ['b','c']=10 -> fewer sessions wins (['a'])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 6 failed: expected 10, got {max_val}"
    assert sel_ids == ['a'], f"Test 6 failed: expected ['a'], got {sel_ids}"
    tests_passed += 1

    # Test 7: Multiple optimal with same count - lexicographic
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "z", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": 5},
            {"id": "a", "start": "2026-01-01T11:00:00", "end": "2026-01-01T12:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(input_data['sessions'])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 7 failed: expected 10, got {max_val}"
    assert sel_ids == ['a', 'z'], f"Test 7 failed: expected ['a','z'], got {sel_ids}"
    tests_passed += 1

    # Test 8: Invalid timestamp format
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "badts", "start": "not-a-date", "end": "2026-01-01T11:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(input_data['sessions'])
    assert len(rejected) == 1, "Test 8 failed"
    assert 'invalid timestamp format' in rejected[0]['reasons'], "Test 8 failed"
    tests_passed += 1

    # Test 9: Z suffix handling
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "ztest", "start": "2026-05-01T09:00:00Z", "end": "2026-05-01T10:30:00Z", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(input_data['sessions'])
    assert len(valid) == 1, "Test 9 failed"
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 5 and sel_ids == ['ztest'], "Test 9 failed"
    tests_passed += 1

    # Test 10: Missing fields
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "missing", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(input_data['sessions'])
    assert len(rejected) == 1, "Test 10 failed"
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_test()
        return

    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            output = {"max_value": 0, "selected_ids": [], "rejected": []}
            print(json.dumps(output))
            return

        data = json.loads(raw_input)
        sessions = data.get('sessions', [])

        valid_sessions, rejected = validate_sessions(sessions)

        max_value, selected_ids, _ = weighted_interval_scheduling(valid_sessions)

        output = {
            "max_value": max_value,
            "selected_ids": selected_ids,
            "rejected": rejected
        }
        print(json.dumps(output))

    except json.JSONDecodeError as e:
        output = {
            "max_value": 0,
            "selected_ids": [],
            "rejected": [{"id": "input", "reasons": [f"Invalid JSON: {str(e)}"]}]
        }
        print(json.dumps(output))
        sys.exit(1)

if __name__ == '__main__':
    main()
```
````
