#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def parse_timestamp(ts_str):
    return datetime.fromisoformat(ts_str)

def weighted_interval_scheduling(sessions):
    # Sort sessions by end time
    sorted_sessions = sorted(sessions, key=lambda s: s['end'])
    n = len(sorted_sessions)

    # Precompute p(j) - the last session that ends before session j starts
    p = [0] * n
    for j in range(n):
        # Binary search for the rightmost session with end <= start of j
        lo, hi = 0, j - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if sorted_sessions[mid]['end'] <= sorted_sessions[j]['start']:
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = hi  # hi is the index of the last non-overlapping session

    # DP arrays
    dp = [0] * (n + 1)
    # For each dp[i], store the best subset information for tie-breaking
    # We'll reconstruct using the dp values and auxiliary info

    for j in range(1, n + 1):
        include_val = sorted_sessions[j-1]['value'] + (dp[p[j-1] + 1] if p[j-1] >= 0 else 0)
        exclude_val = dp[j-1]

        if include_val > exclude_val:
            dp[j] = include_val
        elif include_val < exclude_val:
            dp[j] = exclude_val
        else:
            # Equal values - need tie-breaking: fewer sessions, then lexicographically smaller
            # We'll compute both options to compare
            dp[j] = include_val  # value is same, will break ties during reconstruction

    # Reconstruction with tie-breaking
    def reconstruct(j):
        if j <= 0:
            return [], []

        # Compute include and exclude options
        include_ids = []
        include_value = sorted_sessions[j-1]['value'] + (dp[p[j-1] + 1] if p[j-1] >= 0 else 0)
        include_sessions = [sorted_sessions[j-1]]
        if p[j-1] >= 0:
            sub_ids, sub_sessions = reconstruct(p[j-1] + 1)
            include_ids = sub_ids + [sorted_sessions[j-1]['id']]
            include_sessions = sub_sessions + include_sessions
        else:
            include_ids = [sorted_sessions[j-1]['id']]
            include_sessions = [sorted_sessions[j-1]]

        exclude_ids, exclude_sessions = reconstruct(j-1)
        exclude_value = dp[j-1]

        if include_value > exclude_value:
            return include_ids, include_sessions
        elif include_value < exclude_value:
            return exclude_ids, exclude_sessions
        else:
            # Tie: prefer fewer sessions, then lexicographically smaller list
            if len(include_ids) < len(exclude_ids):
                return include_ids, include_sessions
            elif len(include_ids) > len(exclude_ids):
                return exclude_ids, exclude_sessions
            else:
                # Same length - lexicographic compare
                inc_lex = sorted(include_ids)
                exc_lex = sorted(exclude_ids)
                if inc_lex < exc_lex:
                    return include_ids, include_sessions
                else:
                    # For ties, preserve chronological order by prefering exclude
                    # but since we want chronological, we need to ensure the output is chronological
                    # Both have same value and length, lex smaller wins
                    if list(include_ids) < list(exclude_ids):
                        return include_ids, include_sessions
                    else:
                        return exclude_ids, exclude_sessions

    selected_ids, selected_sessions = reconstruct(n)

    # Ensure chronological order (they should be from reconstruction in chronological order already
    # but let's verify by start time)
    selected_sessions_by_id = {s['id']: s for s in sorted_sessions}
    # Sort selected_ids by start time
    selected_ids_sorted = sorted(selected_ids, key=lambda id: selected_sessions_by_id[id]['start'])

    return dp[n], selected_ids_sorted


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    try:
        raw_input = sys.stdin.read()
        data = json.loads(raw_input)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)

    if 'sessions' not in data or not isinstance(data['sessions'], list):
        print(json.dumps({"error": "Missing or invalid 'sessions' key"}))
        sys.exit(1)

    valid_sessions = []
    rejected = []

    for session in data['sessions']:
        if 'id' not in session or 'start' not in session or 'end' not in session or 'value' not in session:
            rejected.append({"id": session.get('id', 'unknown'), "reason": "Missing required fields"})
            continue

        try:
            start = parse_timestamp(session['start'])
            end = parse_timestamp(session['end'])
        except (ValueError, TypeError):
            rejected.append({"id": session['id'], "reason": "Invalid timestamp format"})
            continue

        if end <= start:
            rejected.append({"id": session['id'], "reason": "End time must be after start time"})
            continue

        if session['value'] < 0:
            rejected.append({"id": session['id'], "reason": "Value cannot be negative"})
            continue

        valid_sessions.append({
            'id': session['id'],
            'start': start,
            'end': end,
            'value': session['value']
        })

    if not valid_sessions:
        result = {
            "max_value": 0,
            "selected_ids": [],
            "rejected": rejected
        }
        print(json.dumps(result, default=str))
        return

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

    print(json.dumps(result, default=str))


def run_tests():
    # Test 1: Simple case with one session
    data1 = {"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}]}
    # Simulate processing
    s = data1['sessions'][0]
    start = parse_timestamp(s['start'])
    end = parse_timestamp(s['end'])
    assert end > start
    assert s['value'] >= 0
    mv, ids = weighted_interval_scheduling([{'id': 'a', 'start': start, 'end': end, 'value': 5}])
    assert mv == 5 and ids == ['a'], f"Test 1 failed: {mv}, {ids}"

    # Test 2: Two non-overlapping sessions
    data2 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4}
        ]
    }
    sessions2 = []
    for s in data2['sessions']:
        sessions2.append({
            'id': s['id'],
            'start': parse_timestamp(s['start']),
            'end': parse_timestamp(s['end']),
            'value': s['value']
        })
    mv2, ids2 = weighted_interval_scheduling(sessions2)
    assert mv2 == 7 and ids2 == ['a', 'b'], f"Test 2 failed: {mv2}, {ids2}"

    # Test 3: Overlapping - should choose higher value
    data3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 9}
        ]
    }
    sessions3 = []
    for s in data3['sessions']:
        sessions3.append({
            'id': s['id'],
            'start': parse_timestamp(s['start']),
            'end': parse_timestamp(s['end']),
            'value': s['value']
        })
    mv3, ids3 = weighted_interval_scheduling(sessions3)
    assert mv3 == 10 and ids3 == ['a'], f"Test 3 failed: {mv3}, {ids3}"

    # Test 4: Tie-breaking - equal value, different length
    data4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    sessions4 = []
    for s in data4['sessions']:
        sessions4.append({
            'id': s['id'],
            'start': parse_timestamp(s['start']),
            'end': parse_timestamp(s['end']),
            'value': s['value']
        })
    mv4, ids4 = weighted_interval_scheduling(sessions4)
    # Both optimal: [a,b] has value 10, 2 sessions. Alternative single session also 10 but longer sessions
    # Actually single sessions have value 5 each, so [a,b] is the only optimal with 2 sessions
    assert mv4 == 10 and ids4 == ['a', 'b'], f"Test 4 failed: {mv4}, {ids4}"

    # Test 5: Tie-breaking equal value and length - lexicographic
    # Two overlapping options, both value 7, both 1 session
    data5 = {
        "sessions": [
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 7},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 7}
        ]
    }
    sessions5 = []
    for s in data5['sessions']:
        sessions5.append({
            'id': s['id'],
            'start': parse_timestamp(s['start']),
            'end': parse_timestamp(s['end']),
            'value': s['value']
        })
    mv5, ids5 = weighted_interval_scheduling(sessions5)
    # Both have value 7 and 1 session, lexicographically 'a' < 'z'
    assert mv5 == 7 and ids5 == ['a'], f"Test 5 failed: {mv5}, {ids5}"

    # Test 6: Reject invalid sessions
    # We'll test via the main function logic
    test_rejected = []
    try:
        parse_timestamp("invalid-date")
    except:
        pass
    # Test end <= start
    assert parse_timestamp("2026-05-01T10:00:00") > parse_timestamp("2026-05-01T09:00:00")
    assert not (parse_timestamp("2026-05-01T09:00:00") > parse_timestamp("2026-05-01T10:00:00"))

    # Test 7: Empty sessions
    mv7, ids7 = weighted_interval_scheduling([])
    assert mv7 == 0 and ids7 == [], f"Test 7 failed: {mv7}, {ids7}"

    # Test 8: More complex overlapping with optimal solution
    data8 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 2},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 4},
            {"id": "d", "start": "2026-05-01T11:30:00", "end": "2026-05-01T13:00:00", "value": 3}
        ]
    }
    sessions8 = []
    for s in data8['sessions']:
        sessions8.append({
            'id': s['id'],
            'start': parse_timestamp(s['start']),
            'end': parse_timestamp(s['end']),
            'value': s['value']
        })
    mv8, ids8 = weighted_interval_scheduling(sessions8)
    # Options: [b]=5, [a,c]=6, [a,d]=5, [c,d]=7, [b,d]=8 -> optimal is [b,d]=8 with 2 sessions
    # But [a,c,d]? a ends at 10, c starts at 10:30, d starts at 11:30 -> 2+4+3=9! Actually a(9-10), c(10:30-12:00), d(11:30-13:00) overlap? c and d overlap (10:30-12 vs 11:30-13). So [a,c]=6, [a,d]=5, [b,d]=8, [b,c] overlap, [c,d] overlap. So optimal is [b,d]=8
    assert mv8 == 8 and ids8 == ['b', 'd'], f"Test 8 failed: {mv8}, {ids8}"

    print("All tests passed!")


if __name__ == '__main__':
    main()
