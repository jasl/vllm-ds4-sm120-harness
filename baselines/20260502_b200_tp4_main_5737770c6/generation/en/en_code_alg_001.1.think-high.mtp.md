# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.612217
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3353, "completion_tokens": 3059, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3059
- Total tokens: 3353

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
    """Parse ISO timestamp string to datetime object."""
    return datetime.fromisoformat(ts_str)

def validate_session(session):
    """Validate a session. Returns (is_valid, reason)."""
    if 'id' not in session:
        return False, "Missing id"
    if 'start' not in session:
        return False, "Missing start"
    if 'end' not in session:
        return False, "Missing end"
    if 'value' not in session:
        return False, "Missing value"

    try:
        start = parse_timestamp(session['start'])
    except (ValueError, TypeError):
        return False, "Invalid start timestamp"

    try:
        end = parse_timestamp(session['end'])
    except (ValueError, TypeError):
        return False, "Invalid end timestamp"

    if end <= start:
        return False, "End must be after start"

    if not isinstance(session['value'], (int, float)) or session['value'] < 0:
        return False, "Value must be non-negative"

    return True, None

def solve_weighted_interval_scheduling(sessions):
    """
    Solve weighted interval scheduling with tie-breaking.
    Returns (max_value, selected_ids) where selected_ids is in chronological order.
    Tie-breaking: fewer sessions first, then lexicographically smaller list of IDs.
    """
    n = len(sessions)
    if n == 0:
        return 0, []

    # Sort sessions by end time
    sorted_sessions = sorted(sessions, key=lambda s: s['end'])

    # Store original indices for tie-breaking reference

    # Precompute p[j] - largest index i < j that doesn't overlap with j
    p = [-1] * n
    for j in range(n):
        for i in range(j - 1, -1, -1):
            if sorted_sessions[i]['end'] <= sorted_sessions[j]['start']:
                p[j] = i
                break

    # DP arrays: M[j] = max value up to j, choice[j] = 0 (skip) or 1 (take)
    M = [0] * n
    choice = [0] * n

    # For tie-breaking: store the solution details
    # We'll reconstruct and compare when values are equal

    for j in range(n):
        # Option 1: skip session j
        skip_val = M[j - 1] if j > 0 else 0

        # Option 2: take session j
        take_val = sorted_sessions[j]['value']
        if p[j] != -1:
            take_val += M[p[j]]

        if take_val > skip_val:
            M[j] = take_val
            choice[j] = 1
        elif take_val < skip_val:
            M[j] = skip_val
            choice[j] = 0
        else:
            # Values are equal, apply tie-breaking
            # Reconstruct both solutions to compare
            skip_solution = reconstruct_solution(sorted_sessions, M, choice, j, forced_skip=True)
            take_solution = reconstruct_solution(sorted_sessions, M, choice, j, forced_take=True)

            # Compare: fewer sessions is better, then lexicographically smaller IDs
            if len(take_solution) < len(skip_solution):
                M[j] = take_val
                choice[j] = 1
            elif len(take_solution) > len(skip_solution):
                M[j] = skip_val
                choice[j] = 0
            else:
                # Same length, compare lexicographically
                take_ids = [s['id'] for s in take_solution]
                skip_ids = [s['id'] for s in skip_solution]
                if take_ids < skip_ids:
                    M[j] = take_val
                    choice[j] = 1
                else:
                    M[j] = skip_val
                    choice[j] = 0

    # Reconstruct final solution
    selected = []
    j = n - 1
    while j >= 0:
        if choice[j] == 1:
            selected.append(sorted_sessions[j])
            j = p[j]
        else:
            j -= 1

    # Reverse to get chronological order (already sorted by end time, reverse gives start order)
    selected.reverse()

    # Sort by start time for strict chronological order
    selected.sort(key=lambda s: s['start'])

    return M[-1] if n > 0 else 0, [s['id'] for s in selected]

def reconstruct_solution(sorted_sessions, M, choice, j, forced_skip=False, forced_take=False):
    """Reconstruct solution for tie-breaking comparison."""
    selected = []
    curr = j

    # Apply forced choice for the current index
    if forced_take:
        if curr >= 0:
            selected.append(sorted_sessions[curr])
            curr = p[curr] if curr >= 0 else -1
    elif forced_skip:
        curr -= 1

    while curr >= 0:
        if choice[curr] == 1:
            selected.append(sorted_sessions[curr])
            curr = p[curr]
        else:
            curr -= 1

    selected.sort(key=lambda s: s['start'])
    return selected

def process_input(data):
    """Process input data and return results."""
    sessions_data = data.get('sessions', [])

    valid_sessions = []
    rejected = []

    for session in sessions_data:
        is_valid, reason = validate_session(session)
        if is_valid:
            valid_sessions.append({
                'id': session['id'],
                'start': parse_timestamp(session['start']),
                'end': parse_timestamp(session['end']),
                'value': session['value']
            })
        else:
            rejected.append({
                'id': session.get('id', 'unknown'),
                'reason': reason
            })

    if not valid_sessions:
        return {
            'max_value': 0,
            'selected_ids': [],
            'rejected': rejected
        }

    max_value, selected_ids = solve_weighted_interval_scheduling(valid_sessions)

    return {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': rejected
    }

def run_tests():
    """Run built-in tests."""
    test_cases = []

    # Test 1: Basic case
    test_cases.append({
        'input': {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
            ]
        },
        'expected': {
            'max_value': 9,
            'selected_ids': ['a', 'c'],
            'rejected': []
        }
    })

    # Test 2: Overlapping sessions, pick highest value
    test_cases.append({
        'input': {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
                {"id": "y", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 8}
            ]
        },
        'expected': {
            'max_value': 10,
            'selected_ids': ['x'],
            'rejected': []
        }
    })

    # Test 3: Rejected sessions
    test_cases.append({
        'input': {
            "sessions": [
                {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "bad_end", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 3},
                {"id": "neg_val", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": -1}
            ]
        },
        'expected': {
            'max_value': 5,
            'selected_ids': ['good'],
            'rejected': [
                {'id': 'bad_end', 'reason': 'End must be after start'},
                {'id': 'neg_val', 'reason': 'Value must be non-negative'}
            ]
        }
    })

    # Test 4: Tie-breaking - same value, choose fewer sessions
    test_cases.append({
        'input': {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
                {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 2}
            ]
        },
        'expected': {
            'max_value': 5,
            'selected_ids': ['a'],
            'rejected': []
        }
    })

    # Test 5: Empty input
    test_cases.append({
        'input': {"sessions": []},
        'expected': {
            'max_value': 0,
            'selected_ids': [],
            'rejected': []
        }
    })

    # Test 6: Multiple optimal with same sessions count - lexicographic tie-break
    test_cases.append({
        'input': {
            "sessions": [
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
                {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
            ]
        },
        'expected': {
            'max_value': 3,
            'selected_ids': ['a'],
            'rejected': []
        }
    })

    # Test 7: Missing fields
    test_cases.append({
        'input': {
            "sessions": [
                {"start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}
            ]
        },
        'expected': {
            'max_value': 0,
            'selected_ids': [],
            'rejected': [{'id': 'unknown', 'reason': 'Missing id'}]
        }
    })

    all_passed = True
    for i, test in enumerate(test_cases):
        result = process_input(test['input'])
        expected = test['expected']

        # Check max_value
        if result['max_value'] != expected['max_value']:
            print(f"Test {i+1} FAILED: max_value {result['max_value']} != {expected['max_value']}")
            all_passed = False
            continue

        # Check selected_ids
        if result['selected_ids'] != expected['selected_ids']:
            print(f"Test {i+1} FAILED: selected_ids {result['selected_ids']} != {expected['selected_ids']}")
            all_passed = False
            continue

        # Check rejected
        if len(result['rejected']) != len(expected['rejected']):
            print(f"Test {i+1} FAILED: rejected count mismatch")
            all_passed = False
            continue

        for r, e in zip(result['rejected'], expected['rejected']):
            if r['id'] != e['id'] or r['reason'] != e['reason']:
                print(f"Test {i+1} FAILED: rejected entry mismatch")
                all_passed = False
                break

    if all_passed:
        print("All tests passed!")
        return True
    else:
        print("Some tests failed!")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        try:
            data = json.load(sys.stdin)
            result = process_input(data)
            # Convert datetime objects to strings for JSON serialization
            # (sessions are already processed, no datetime in output)
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {str(e)}"}, indent=2))
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2))
            sys.exit(1)

if __name__ == '__main__':
    main()
```
````
