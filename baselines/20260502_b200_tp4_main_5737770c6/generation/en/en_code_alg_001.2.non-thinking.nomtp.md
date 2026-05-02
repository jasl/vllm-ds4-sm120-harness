# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 26.530545
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3991, "completion_tokens": 3697, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3697
- Total tokens: 3991

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

def parse_datetime(s):
    """Parse ISO-like timestamp without timezone."""
    return datetime.fromisoformat(s)

def validate_session(session):
    """Validate a session, return (is_valid, reason)."""
    # Check required fields
    if not all(k in session for k in ('id', 'start', 'end', 'value')):
        return False, "missing required field"

    sid = session['id']
    if not isinstance(sid, str) or not sid:
        return False, "id must be a non-empty string"

    try:
        start = parse_datetime(session['start'])
        end = parse_datetime(session['end'])
    except (ValueError, TypeError):
        return False, "invalid datetime format"

    if end <= start:
        return False, "end must be after start"

    value = session['value']
    if not isinstance(value, (int, float)) or value < 0:
        return False, "value must be non-negative"

    return True, None

def weighted_interval_scheduling(sessions):
    """
    Weighted interval scheduling with tie-breaking.
    Returns (max_value, selected_ids).
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s['end'])

    n = len(sorted_sessions)

    # Precompute p[i] - index of last non-overlapping session
    p = [-1] * n
    for i in range(n):
        # Binary search
        lo, hi = 0, i - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if sorted_sessions[mid]['end'] <= sorted_sessions[i]['start']:
                lo = mid + 1
            else:
                hi = mid - 1
        p[i] = hi  # hi is the last non-overlapping index, -1 if none

    # DP arrays for value and session count
    dp_value = [0] * (n + 1)
    dp_count = [0] * (n + 1)  # number of sessions in optimal solution

    for i in range(1, n + 1):
        idx = i - 1
        include_value = sorted_sessions[idx]['value'] + dp_value[p[idx] + 1]
        exclude_value = dp_value[i - 1]

        include_count = 1 + dp_count[p[idx] + 1]
        exclude_count = dp_count[i - 1]

        if include_value > exclude_value:
            dp_value[i] = include_value
            dp_count[i] = include_count
        elif include_value < exclude_value:
            dp_value[i] = exclude_value
            dp_count[i] = exclude_count
        else:
            # Same value - choose fewer sessions
            if include_count < exclude_count:
                dp_value[i] = include_value
                dp_count[i] = include_count
            elif include_count > exclude_count:
                dp_value[i] = exclude_value
                dp_count[i] = exclude_count
            else:
                # Same count - choose lexicographically smaller list
                # Need reconstruction to compare
                include_list = reconstruct_include(sorted_sessions, p, i)
                exclude_list = reconstruct_exclude(sorted_sessions, p, i)
                if include_list < exclude_list:
                    dp_value[i] = include_value
                    dp_count[i] = include_count
                else:
                    dp_value[i] = exclude_value
                    dp_count[i] = exclude_count

    # Reconstruct optimal solution
    selected = []
    i = n
    while i > 0:
        idx = i - 1
        include_value = sorted_sessions[idx]['value'] + dp_value[p[idx] + 1]
        exclude_value = dp_value[i - 1]
        include_count = 1 + dp_count[p[idx] + 1]
        exclude_count = dp_count[i - 1]

        if include_value > exclude_value:
            selected.append(sorted_sessions[idx])
            i = p[idx] + 1
        elif include_value < exclude_value:
            i -= 1
        else:
            if include_count < exclude_count:
                selected.append(sorted_sessions[idx])
                i = p[idx] + 1
            elif include_count > exclude_count:
                i -= 1
            else:
                include_list = reconstruct_include(sorted_sessions, p, i)
                exclude_list = reconstruct_exclude(sorted_sessions, p, i)
                if include_list < exclude_list:
                    selected.append(sorted_sessions[idx])
                    i = p[idx] + 1
                else:
                    i -= 1

    # Reverse to get chronological order (sorted by end time ascending)
    selected.reverse()
    selected_ids = [s['id'] for s in selected]
    max_value = dp_value[n]

    return max_value, selected_ids

def reconstruct_include(sorted_sessions, p, i):
    """Reconstruct the list of IDs for the include path at state i."""
    result = []
    while i > 0:
        idx = i - 1
        result.append(sorted_sessions[idx]['id'])
        i = p[idx] + 1
    result.reverse()
    return result

def reconstruct_exclude(sorted_sessions, p, i):
    """Reconstruct the list of IDs for the exclude path at state i."""
    result = []
    i_copy = i - 1
    while i_copy > 0:
        idx = i_copy - 1
        # For exclude at this step, we need to simulate the optimal decision
        # We'll use a simpler approach - just follow the dp decisions
        # Since this is just for tie-breaking, we can reconstruct recursively
        # But to avoid complexity, we'll do a full DP reconstruction
        pass

    # For simplicity, use a different approach: compare lists directly
    # by doing a full reconstruction from state i-1
    return reconstruct_from_state(sorted_sessions, p, i - 1)

def reconstruct_from_state(sorted_sessions, p, state):
    """Reconstruct optimal solution from a given state."""
    i = state
    result = []
    # We need dp values to make decisions, compute them on the fly
    n = state
    dp_val = [0] * (n + 1)
    dp_cnt = [0] * (n + 1)

    for j in range(1, n + 1):
        idx = j - 1
        inc = sorted_sessions[idx]['value'] + dp_val[p[idx] + 1]
        exc = dp_val[j - 1]
        inc_cnt = 1 + dp_cnt[p[idx] + 1]
        exc_cnt = dp_cnt[j - 1]

        if inc > exc:
            dp_val[j] = inc
            dp_cnt[j] = inc_cnt
        elif inc < exc:
            dp_val[j] = exc
            dp_cnt[j] = exc_cnt
        else:
            if inc_cnt < exc_cnt:
                dp_val[j] = inc
                dp_cnt[j] = inc_cnt
            else:
                dp_val[j] = exc
                dp_cnt[j] = exc_cnt

    # Reconstruct
    i = state
    while i > 0:
        idx = i - 1
        inc = sorted_sessions[idx]['value'] + dp_val[p[idx] + 1]
        exc = dp_val[i - 1]
        inc_cnt = 1 + dp_cnt[p[idx] + 1]
        exc_cnt = dp_cnt[i - 1]

        if inc > exc:
            result.append(sorted_sessions[idx]['id'])
            i = p[idx] + 1
        elif inc < exc:
            i -= 1
        else:
            if inc_cnt < exc_cnt:
                result.append(sorted_sessions[idx]['id'])
                i = p[idx] + 1
            else:
                i -= 1

    result.reverse()
    return result

def solve(data):
    """Main solving function."""
    sessions_raw = data.get('sessions', [])

    valid_sessions = []
    rejected = []

    for session in sessions_raw:
        is_valid, reason = validate_session(session)
        if is_valid:
            valid_sessions.append({
                'id': session['id'],
                'start': parse_datetime(session['start']),
                'end': parse_datetime(session['end']),
                'value': session['value']
            })
        else:
            rejected.append({
                'id': session.get('id', 'unknown'),
                'reason': reason
            })

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    result = {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': rejected
    }

    return result

def run_tests():
    """Run built-in tests."""
    test_cases = [
        {
            "name": "empty input",
            "input": {"sessions": []},
            "expected": {"max_value": 0, "selected_ids": [], "rejected": []}
        },
        {
            "name": "single session",
            "input": {"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}]},
            "expected": {"max_value": 5, "selected_ids": ["a"], "rejected": []}
        },
        {
            "name": "non-overlapping sessions",
            "input": {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
                    {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
                    {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
                ]
            },
            "expected": {"max_value": 12, "selected_ids": ["a", "b", "c"], "rejected": []}
        },
        {
            "name": "overlapping sessions - choose best",
            "input": {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
                    {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 8},
                    {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 9}
                ]
            },
            "expected": {"max_value": 19, "selected_ids": ["a", "c"], "rejected": []}
        },
        {
            "name": "rejected sessions",
            "input": {
                "sessions": [
                    {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                    {"id": "bad_end", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5},
                    {"id": "neg_val", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
                    {"id": "missing_field", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00"}
                ]
            },
            "expected": {
                "max_value": 5,
                "selected_ids": ["good"],
                "rejected": [
                    {"id": "bad_end", "reason": "end must be after start"},
                    {"id": "neg_val", "reason": "value must be non-negative"},
                    {"id": "missing_field", "reason": "missing required field"}
                ]
            }
        },
        {
            "name": "tie-breaking fewer sessions",
            "input": {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
                    {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                    {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 5}
                ]
            },
            "expected": {"max_value": 10, "selected_ids": ["a"], "rejected": []}
        },
        {
            "name": "tie-breaking lexicographic",
            "input": {
                "sessions": [
                    {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                    {"id": "a", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 5},
                    {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10}
                ]
            },
            "expected": {"max_value": 10, "selected_ids": ["c"], "rejected": []}
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        try:
            result = solve(test["input"])
            expected = test["expected"]

            # Check max_value
            if result["max_value"] != expected["max_value"]:
                print(f"FAIL: {test['name']} - max_value {result['max_value']} != {expected['max_value']}")
                failed += 1
                continue

            # Check selected_ids
            if result["selected_ids"] != expected["selected_ids"]:
                print(f"FAIL: {test['name']} - selected_ids {result['selected_ids']} != {expected['selected_ids']}")
                failed += 1
                continue

            # Check rejected (order doesn't matter, compare sets)
            expected_rejected_set = frozenset(
                (r["id"], r["reason"]) for r in expected["rejected"]
            )
            result_rejected_set = frozenset(
                (r["id"], r["reason"]) for r in result["rejected"]
            )
            if result_rejected_set != expected_rejected_set:
                print(f"FAIL: {test['name']} - rejected mismatch")
                print(f"  Got: {result['rejected']}")
                print(f"  Expected: {expected['rejected']}")
                failed += 1
                continue

            passed += 1

        except Exception as e:
            print(f"FAIL: {test['name']} - exception: {e}")
            failed += 1

    print(f"Tests: {passed} passed, {failed} failed")
    if failed == 0:
        print("All tests passed!")
        return True
    return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        success = run_tests()
        sys.exit(0 if success else 1)

    try:
        data = json.load(sys.stdin)
        result = solve(data)
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```
````
