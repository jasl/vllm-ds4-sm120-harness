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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 46.367868
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3244, "completion_tokens": 2950, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2950
- Total tokens: 3244

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
"""
schedule_optimizer.py — Weighted interval scheduling with reconstruction.
"""

import json
import sys
from datetime import datetime

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone information."""
    # Remove trailing Z if present (assume UTC without timezone)
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1]
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    seen_ids = set()
    for s in sessions:
        sid = s.get('id')
        # Check id uniqueness
        if sid in seen_ids:
            rejected.append({
                "id": sid,
                "reason": f"Duplicate id '{sid}'"
            })
            continue
        seen_ids.add(sid)

        # Check required fields
        if 'start' not in s or 'end' not in s or 'value' not in s:
            rejected.append({
                "id": sid,
                "reason": "Missing required field(s)"
            })
            continue

        try:
            start = parse_timestamp(s['start'])
            end = parse_timestamp(s['end'])
        except (ValueError, TypeError):
            rejected.append({
                "id": sid,
                "reason": "Invalid timestamp format"
            })
            continue

        if end <= start:
            rejected.append({
                "id": sid,
                "reason": "End must be after start"
            })
            continue

        val = s['value']
        if not isinstance(val, (int, float)) or val < 0:
            rejected.append({
                "id": sid,
                "reason": "Negative or non-numeric value"
            })
            continue

        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": val
        })
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    O(n log n) DP solution for weighted interval scheduling.
    Returns (max_value, selected_ids_in_order).
    In case of tie: fewer sessions chosen, then lexicographically smaller IDs.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s['end'])

    # Precompute p[j] = last index with end <= start of j (binary search)
    n = len(sorted_sessions)
    p = [-1] * n
    ends = [s['end'] for s in sorted_sessions]
    for j in range(n):
        start_j = sorted_sessions[j]['start']
        # Binary search for rightmost end <= start_j
        lo, hi = 0, j-1
        pos = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if ends[mid] <= start_j:
                pos = mid
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = pos

    # DP arrays: dp_value, dp_sessions_count, dp_lex_key (tuple of ids), dp_selection (list of ids)
    dp_value = [0] * n
    dp_count = [0] * n  # number of sessions in optimal solution for prefix
    dp_ids = [()] * n   # tuple of ids for tie-breaking (sorted chronologically)

    for j in range(n):
        # Option 1: include session j
        incl_val = sorted_sessions[j]['value']
        incl_count = 1
        incl_ids = (sorted_sessions[j]['id'],)
        if p[j] != -1:
            incl_val += dp_value[p[j]]
            incl_count += dp_count[p[j]]
            incl_ids = dp_ids[p[j]] + (sorted_sessions[j]['id'],)

        # Option 2: exclude session j
        excl_val = dp_value[j-1] if j > 0 else 0
        excl_count = dp_count[j-1] if j > 0 else 0
        excl_ids = dp_ids[j-1] if j > 0 else ()

        # Choose better
        if incl_val > excl_val:
            dp_value[j] = incl_val
            dp_count[j] = incl_count
            dp_ids[j] = incl_ids
        elif incl_val < excl_val:
            dp_value[j] = excl_val
            dp_count[j] = excl_count
            dp_ids[j] = excl_ids
        else:
            # Tie: prefer fewer sessions, then lexicographically smaller list of IDs
            if incl_count < excl_count:
                dp_value[j] = incl_val
                dp_count[j] = incl_count
                dp_ids[j] = incl_ids
            elif incl_count > excl_count:
                dp_value[j] = excl_val
                dp_count[j] = excl_count
                dp_ids[j] = excl_ids
            else:
                # Same count: lexicographic compare
                if list(incl_ids) < list(excl_ids):
                    dp_value[j] = incl_val
                    dp_count[j] = incl_count
                    dp_ids[j] = incl_ids
                else:
                    dp_value[j] = excl_val
                    dp_count[j] = excl_count
                    dp_ids[j] = excl_ids

    max_val = dp_value[-1] if n > 0 else 0
    selected_ids = list(dp_ids[-1]) if n > 0 else []
    return max_val, selected_ids

def solve(input_data):
    """Main solving function."""
    sessions = input_data.get('sessions', [])
    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Build output
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return output

def run_tests():
    """Run built-in tests."""
    # Test 1: Basic example
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    result = solve(data)
    assert result['max_value'] == 9, f"Expected 9, got {result['max_value']}"
    assert result['selected_ids'] == ['a', 'c'], f"Expected ['a','c'], got {result['selected_ids']}"
    assert result['rejected'] == [], f"Expected no rejected, got {result['rejected']}"

    # Test 2: Reject invalid
    data2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -1},
            {"id": "z", "start": "invalid", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    }
    result2 = solve(data2)
    assert result2['max_value'] == 0, f"Expected 0, got {result2['max_value']}"
    assert len(result2['rejected']) == 3, f"Expected 3 rejected, got {len(result2['rejected'])}"

    # Test 3: Tie-breaking (fewer sessions)
    data3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 5}
        ]
    }
    # Options: a+b = 10 (2 sessions), a+c = 10 (2 sessions), b+c overlap, single session = 5
    # a+b and a+c both yield 10 with 2 sessions; lexicographically smaller list: ['a','b'] vs ['a','c'] -> 'a','b'
    result3 = solve(data3)
    assert result3['max_value'] == 10, f"Expected 10, got {result3['max_value']}"
    assert result3['selected_ids'] == ['a', 'b'], f"Expected ['a','b'], got {result3['selected_ids']}"

    # Test 4: Tie-breaking (same count, lexicographic)
    data4 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    }
    # b+a = ["b","a"] but chronological order forces ["a","b"] after sorting by end?
    # They are already non-overlapping; both orders possible? Let's check:
    # b 9-10, a 10-11, c 11-12 -> all compatible. Total value 15, 3 sessions.
    # Only one optimal selection: all three. IDs should be sorted chronologically -> ["a","b","c"]? Wait,
    # sessions sorted by end: b(10), a(11), c(12). DP will pick ids in order: b then a then c -> ("b","a","c")
    # But output selected_ids should be chronological order (by start time).
    # Let's verify: start times: b=9, a=10, c=11 -> chronological order should be ["b","a","c"]
    # However our DP returns ids in sorted-by-end order: b, a, c. That matches chronological.
    # So expected ["b","a","c"]
    result4 = solve(data4)
    assert result4['max_value'] == 15, f"Expected 15, got {result4['max_value']}"
    # Since all start times are different and order matches, result is fine
    assert result4['selected_ids'] == ['b', 'a', 'c'], f"Expected ['b','a','c'], got {result4['selected_ids']}"

    # Test 5: Empty
    data5 = {"sessions": []}
    result5 = solve(data5)
    assert result5['max_value'] == 0
    assert result5['selected_ids'] == []
    assert result5['rejected'] == []

    # Test 6: Duplicate id
    data6 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
            {"id": "a", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 2}
        ]
    }
    result6 = solve(data6)
    assert result6['max_value'] == 1, f"Expected 1, got {result6['max_value']}"
    assert result6['selected_ids'] == ['a'], f"Expected ['a'], got {result6['selected_ids']}"
    assert len(result6['rejected']) == 1

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    raw = sys.stdin.read()
    try:
        input_data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    output = solve(input_data)
    print(json.dumps(output, default=str))

if __name__ == '__main__':
    main()
```
````
