#!/usr/bin/env python3
import sys
import json
import datetime
import bisect

def parse_datetime(s):
    """Parse ISO-like datetime string (no timezone) using standard library."""
    try:
        # Python 3.7+ has fromisoformat
        return datetime.datetime.fromisoformat(s)
    except AttributeError:
        # Fallback for older Python versions
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

def weighted_interval_scheduling(intervals):
    """
    Weighted interval scheduling with tie-breaking.

    intervals: list of dict with keys 'id', 'start', 'end', 'value'.
    Returns (max_value, selected_ids) where selected_ids are in chronological order.
    """
    if not intervals:
        return 0, []

    # Sort by end time, then start time, then id for determinism
    intervals.sort(key=lambda x: (x['end'], x['start'], x['id']))
    n = len(intervals)

    # Build list of end times (datetime objects) for binary search
    end_times = [iv['end'] for iv in intervals]

    # For each interval, find last index with end <= start_i
    p = [-1] * n
    for i in range(n):
        start_i = intervals[i]['start']
        idx = bisect.bisect_right(end_times, start_i) - 1
        p[i] = idx  # -1 if none

    # DP arrays: each entry is a tuple (neg_value, count, ids_tuple)
    # Using negative value so that "better" means smaller tuple lexicographically.
    # Base case: empty set
    best_empty = (0, 0, ())
    dp = [None] * n

    for i in range(n):
        # Option 1: do not take interval i
        opt1 = dp[i - 1] if i > 0 else best_empty

        # Option 2: take interval i + best solution for prefix p[i]
        if p[i] == -1:
            best_prev = best_empty
        else:
            best_prev = dp[p[i]]

        val_i = intervals[i]['value']
        id_i = intervals[i]['id']
        new_neg_val = best_prev[0] - val_i
        new_count = best_prev[1] + 1
        new_ids = best_prev[2] + (id_i,)
        opt2 = (new_neg_val, new_count, new_ids)

        # Choose the better option (lexicographically smaller tuple)
        dp[i] = min(opt1, opt2)

    best = dp[-1]
    max_value = -best[0]
    selected_ids = list(best[2])
    return max_value, selected_ids

def process_input(data):
    """Parse JSON input, validate sessions, run DP, return output dict."""
    input_data = json.loads(data)
    sessions = input_data.get('sessions', [])
    valid_intervals = []
    rejected = []

    for session in sessions:
        sid = session.get('id')
        # If no id, we still need something to identify; treat as missing required field
        if sid is None:
            rejected.append({"id": None, "reason": "missing id"})
            continue

        start_str = session.get('start')
        end_str = session.get('end')
        value = session.get('value')

        # Check presence of required fields
        if start_str is None or end_str is None or value is None:
            rejected.append({"id": sid, "reason": "missing required field"})
            continue

        # Parse datetimes
        try:
            start = parse_datetime(start_str)
            end = parse_datetime(end_str)
        except Exception as e:
            rejected.append({"id": sid, "reason": f"invalid datetime: {e}"})
            continue

        # Validate value type (must be numeric)
        if not isinstance(value, (int, float)):
            rejected.append({"id": sid, "reason": "value must be a number"})
            continue

        if value < 0:
            rejected.append({"id": sid, "reason": "value must be non-negative"})
            continue

        if end <= start:
            rejected.append({"id": sid, "reason": "end must be after start"})
            continue

        valid_intervals.append({
            'id': sid,
            'start': start,
            'end': end,
            'value': value
        })

    max_value, selected_ids = weighted_interval_scheduling(valid_intervals)

    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
def run_tests():
    # Test 1: single valid session
    data = '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}]}'
    res = process_input(data)
    assert res['max_value'] == 5
    assert res['selected_ids'] == ['a']
    assert res['rejected'] == []
    print("Test 1 passed: single valid session")

    # Test 2: two non-overlapping sessions
    data = '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}, {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}]}'
    res = process_input(data)
    assert res['max_value'] == 15
    assert res['selected_ids'] == ['a', 'b']
    print("Test 2 passed: non-overlapping")

    # Test 3: overlapping, choose higher value
    data = '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}, {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 20}]}'
    res = process_input(data)
    assert res['max_value'] == 20
    assert res['selected_ids'] == ['b']
    print("Test 3 passed: overlapping choose higher")

    # Test 4: tie-breaking - same value, count 1, lexicographically smaller ID
    data = '{"sessions": [{"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}, {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 10}]}'
    res = process_input(data)
    assert res['max_value'] == 10
    assert res['selected_ids'] == ['a']
    print("Test 4 passed: tie-breaking lexicographic ID")

    # Test 5: tie-breaking same value, different counts -> prefer fewer sessions
    data = '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 5}, {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3}, {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 2}]}'
    res = process_input(data)
    assert res['max_value'] == 5
    assert res['selected_ids'] == ['a']
    print("Test 5 passed: tie-breaking fewer sessions")

    # Test 6: rejection - invalid value and invalid end time
    data = '{"sessions": [{"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5}, {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}]}'
    res = process_input(data)
    assert res['max_value'] == 0
    assert res['selected_ids'] == []
    assert len(res['rejected']) == 2
    reasons = {r['id']: r['reason'] for r in res['rejected']}
    assert 'end must be after start' in reasons.get('x', '')
    assert 'non-negative' in reasons.get('y', '')
    print("Test 6 passed: rejection")

    # Test 7: empty input
    data = '{"sessions": []}'
    res = process_input(data)
    assert res['max_value'] == 0
    assert res['selected_ids'] == []
    assert res['rejected'] == []
    print("Test 7 passed: empty input")

    # Test 8: chronological order of selected_ids
    data = '{"sessions": [{"id": "z", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 1}, {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1}]}'
    res = process_input(data)
    assert res['selected_ids'] == ['a', 'z']
    print("Test 8 passed: chronological order")

    # Test 9: tie-breaking with same count and value, different first-ID
    data = '{"sessions": [{"id": "A", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 1}, {"id": "B", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 1}, {"id": "C", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 1}, {"id": "D", "start": "2026-05-01T12:00:00", "end": "2026-05-01T14:00:00", "value": 1}]}'
    res = process_input(data)
    # Two optimal sets of two intervals: {A,C} and {B,D}
    assert res['max_value'] == 2
    assert res['selected_ids'] == ['A', 'C']
    print("Test 9 passed: tie-breaking lexicographic with same count")

    # Test 10: deeper lexicographic tie (first ID same, second different)
    data = '{"sessions": [{"id":"A","start":"2026-05-01T01:00:00","end":"2026-05-01T03:00:00","value":1},{"id":"B","start":"2026-05-01T02:00:00","end":"2026-05-01T04:00:00","value":1},{"id":"C","start":"2026-05-01T04:00:00","end":"2026-05-01T06:00:00","value":1},{"id":"D","start":"2026-05-01T05:00:00","end":"2026-05-01T07:00:00","value":1}]}'
    res = process_input(data)
    # Many optimal pairs, lexicographically smallest is ['A','C']
    assert res['max_value'] == 2
    assert res['selected_ids'] == ['A', 'C']
    print("Test 10 passed: deeper lexicographic tie")

    # Test 11: all sessions rejected
    data = '{"sessions": [{"id":"bad","start":"2026-05-01T09:00:00","end":"2026-05-01T08:00:00","value":5}]}'
    res = process_input(data)
    assert res['max_value'] == 0
    assert res['selected_ids'] == []
    assert len(res['rejected']) == 1
    print("Test 11 passed: all rejected")

    print("\nAll tests passed!")

def main():
    if '--test' in sys.argv:
        run_tests()
    else:
        data = sys.stdin.read()
        result = process_input(data)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
