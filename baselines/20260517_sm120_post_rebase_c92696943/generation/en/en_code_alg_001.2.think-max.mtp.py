#!/usr/bin/env python3
import sys
import json
from datetime import datetime
import bisect


def parse_datetime(s):
    """Parse ISO‑format datetime string (without timezone)."""
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        raise ValueError("invalid timestamp")


def parse_sessions(data):
    """Validate input sessions; return (accepted, rejected) lists."""
    accepted = []
    rejected = []
    sessions = data.get('sessions', [])
    for session in sessions:
        id_ = session.get('id', 'unknown')
        try:
            start_str = session['start']
            end_str = session['end']
            start_dt = parse_datetime(start_str)
            end_dt = parse_datetime(end_str)
        except (ValueError, KeyError):
            rejected.append({'id': id_, 'reason': 'invalid timestamp'})
            continue
        if end_dt <= start_dt:
            rejected.append({'id': id_, 'reason': 'end must be after start'})
            continue
        value = session.get('value', 0)
        if value < 0:
            rejected.append({'id': id_, 'reason': 'value must be non-negative'})
            continue
        accepted.append({
            'id': id_,
            'value': value,
            'start_dt': start_dt,
            'end_dt': end_dt,
        })
    return accepted, rejected


def sort_accepted(accepted):
    """Sort intervals by end, then start, then id (deterministic order)."""
    accepted.sort(key=lambda x: (x['end_dt'], x['start_dt'], x['id']))


def compute_p(accepted_sorted):
    """For each interval, find last index with end_dt <= start_dt."""
    ends = [interval['end_dt'] for interval in accepted_sorted]
    p = []
    for interval in accepted_sorted:
        idx = bisect.bisect_right(ends, interval['start_dt']) - 1
        p.append(idx)
    return p


def better(entry1, entry2):
    """Return True if entry1 is strictly better than entry2.

    Order: higher value, fewer sessions, lexicographically smaller sequence.
    """
    v1, c1, s1 = entry1
    v2, c2, s2 = entry2
    if v1 != v2:
        return v1 > v2
    if c1 != c2:
        return c1 < c2            # fewer sessions is better
    return s1 < s2                # lexicographically smaller list is better


def solve(accepted_sorted):
    """Weighted interval scheduling with reconstruction and tie‑breaking.

    Returns (max_value, selected_ids) where selected_ids are in chronological order.
    """
    if not accepted_sorted:
        return (0, [])

    p = compute_p(accepted_sorted)
    n = len(accepted_sorted)
    base = (0, 0, ())            # (value, count, sequence tuple)
    dp = [None] * n

    for i in range(n):
        interval = accepted_sorted[i]
        id_i = interval['id']
        value_i = interval['value']

        # Option 1: skip interval i
        if i == 0:
            skip = base
        else:
            skip = dp[i - 1]

        # Option 2: take interval i
        prev = p[i]
        if prev >= 0:
            prev_entry = dp[prev]
            take_val = value_i + prev_entry[0]
            take_count = 1 + prev_entry[1]
            take_seq = prev_entry[2] + (id_i,)
        else:
            take_val = value_i
            take_count = 1
            take_seq = (id_i,)
        take = (take_val, take_count, take_seq)

        # Keep the better of the two
        if better(take, skip):
            dp[i] = take
        else:
            dp[i] = skip

    best = dp[-1]
    return (best[0], list(best[2]))


def main():
    data = json.load(sys.stdin)
    accepted, rejected = parse_sessions(data)
    sort_accepted(accepted)
    max_value, selected_ids = solve(accepted)
    output = {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': rejected,
    }
    json.dump(output, sys.stdout)
    sys.stdout.write('\n')


def run_tests():
    """Built‑in tests (invoked by --test)."""

    # Test 1: two non‑overlapping sessions
    data1 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10},
    ]}
    acc1, rej1 = parse_sessions(data1)
    sort_accepted(acc1)
    v1, ids1 = solve(acc1)
    assert v1 == 15, f"Test1 value = {v1}"
    assert ids1 == ['a', 'b'], f"Test1 ids = {ids1}"
    assert rej1 == []

    # Test 2: overlapping, choose higher value
    data2 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 10},
    ]}
    acc2, rej2 = parse_sessions(data2)
    sort_accepted(acc2)
    v2, ids2 = solve(acc2)
    assert v2 == 10, f"Test2 value = {v2}"
    assert ids2 == ['b'], f"Test2 ids = {ids2}"

    # Test 3: reject invalid sessions
    data3 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T09:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 10},
        {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
        {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
    ]}
    acc3, rej3 = parse_sessions(data3)
    assert len(acc3) == 1
    assert acc3[0]['id'] == 'd'
    assert len(rej3) == 3
    assert rej3[0]['reason'] == 'end must be after start'
    assert rej3[1]['reason'] == 'end must be after start'
    assert rej3[2]['reason'] == 'value must be non-negative'

    # Test 4: tie‑break – fewer sessions
    data4 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
        {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5},
    ]}
    acc4, rej4 = parse_sessions(data4)
    sort_accepted(acc4)
    v4, ids4 = solve(acc4)
    assert v4 == 10, f"Test4 value = {v4}"
    assert ids4 == ['a'], f"Test4 ids = {ids4} (expected ['a'])"

    # Test 5: tie‑break – lexicographic order
    data5 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T12:00:00", "end": "2026-05-01T15:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
        {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T15:00:00", "value": 7},
    ]}
    acc5, rej5 = parse_sessions(data5)
    sort_accepted(acc5)
    v5, ids5 = solve(acc5)
    assert v5 == 10, f"Test5 value = {v5}"
    assert ids5 == ['a', 'b'], f"Test5 ids = {ids5} (expected ['a','b'])"

    # Test 6: empty session list
    data6 = {"sessions": []}
    acc6, rej6 = parse_sessions(data6)
    sort_accepted(acc6)
    v6, ids6 = solve(acc6)
    assert v6 == 0, f"Test6 value = {v6}"
    assert ids6 == [], f"Test6 ids = {ids6}"

    # Test 7: invalid timestamp
    data7 = {"sessions": [
        {"id": "x", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5},
    ]}
    acc7, rej7 = parse_sessions(data7)
    assert len(acc7) == 0
    assert len(rej7) == 1
    assert rej7[0]['reason'] == 'invalid timestamp'

    # Test 8: deeper lexicographic tie (first element equal)
    data8 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
    ]}
    acc8, rej8 = parse_sessions(data8)
    sort_accepted(acc8)
    v8, ids8 = solve(acc8)
    # Two optimal solutions of value 10, 2 sessions:
    #   ['a','b'] (first a+second b) and ['a','c'] (third a+fourth c)
    # Lexicographically: ['a','b'] < ['a','c']
    assert v8 == 10, f"Test8 value = {v8}"
    assert ids8 == ['a', 'b'], f"Test8 ids = {ids8} (expected ['a','b'])"

    print("All tests passed!")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        main()
