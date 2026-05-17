#!/usr/bin/env python3
import sys
import json
import datetime
import bisect
from datetime import timezone

def parse_timestamp(s):
    """Parse ISO 8601 timestamp without timezone info."""
    # Python 3.7+ supports fromisoformat for such strings
    return datetime.datetime.fromisoformat(s)

def validate_sessions(sessions):
    """Return (valid_sessions, rejected) lists."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get('id')
        start_str = sess.get('start')
        end_str = sess.get('end')
        value = sess.get('value')
        # Type checks / missing fields – assume they exist as per description
        try:
            start = parse_timestamp(start_str)
            end = parse_timestamp(end_str)
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        if end <= start:
            rejected.append({"id": sid, "reason": "End must be after start"})
            continue
        if value < 0:
            rejected.append({"id": sid, "reason": "Value cannot be negative"})
            continue
        valid.append({"id": sid, "start": start, "end": end, "value": value})
    return valid, rejected

def solve(valid_sessions):
    """Weighted interval scheduling with DP, tie‑breaking by fewer sessions, then lexicographic list."""
    if not valid_sessions:
        return 0, []

    # Sort by end time, then start time, then id (deterministic)
    sorted_sessions = sorted(valid_sessions, key=lambda s: (s['end'], s['start'], s['id']))
    n = len(sorted_sessions)

    ids = [s['id'] for s in sorted_sessions]
    start_times = [s['start'] for s in sorted_sessions]
    end_times = [s['end'] for s in sorted_sessions]
    values = [s['value'] for s in sorted_sessions]

    # Compute p(i): index of last interval that ends <= start of i
    p = []
    for i in range(n):
        idx = bisect.bisect_right(end_times, start_times[i]) - 1
        p.append(idx)   # -1 if none

    # DP arrays
    dp_val = [0] * n
    dp_cnt = [0] * n
    dp_list = [()] * n   # tuple of IDs in order

    def better(a_val, a_cnt, a_list, b_val, b_cnt, b_list):
        """Return True if (a_val, a_cnt, a_list) is better than b."""
        if a_val != b_val:
            return a_val > b_val
        if a_cnt != b_cnt:
            return a_cnt < b_cnt   # fewer sessions wins
        return a_list < b_list     # lexicographic smaller list

    for i in range(n):
        # Exclude current interval -> take best of first i-1 intervals
        if i == 0:
            exclude_val, exclude_cnt, exclude_list = 0, 0, ()
        else:
            exclude_val, exclude_cnt, exclude_list = dp_val[i-1], dp_cnt[i-1], dp_list[i-1]

        # Include current interval
        prev = p[i]
        if prev == -1:
            inc_val = values[i]
            inc_cnt = 1
            inc_list = (ids[i],)
        else:
            inc_val = values[i] + dp_val[prev]
            inc_cnt = 1 + dp_cnt[prev]
            inc_list = dp_list[prev] + (ids[i],)

        if better(inc_val, inc_cnt, inc_list, exclude_val, exclude_cnt, exclude_list):
            dp_val[i] = inc_val
            dp_cnt[i] = inc_cnt
            dp_list[i] = inc_list
        else:
            dp_val[i] = exclude_val
            dp_cnt[i] = exclude_cnt
            dp_list[i] = exclude_list

    max_value = dp_val[-1]
    selected_ids = list(dp_list[-1])   # already in chronological order
    return max_value, selected_ids

def process_test(data):
    """Helper for tests: run the full pipeline on given input dict, return output dict."""
    sessions = data.get('sessions', [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids = solve(valid)
    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

def run_tests():
    # Test 1: overlapping simple – higher value wins
    input1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 10}
        ]
    }
    result = process_test(input1)
    expected = {"max_value": 10, "selected_ids": ["b"], "rejected": []}
    assert result == expected, f"Test 1 failed: {result}"

    # Test 2: non‑overlapping – take both
    input2 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 7}
        ]
    }
    result = process_test(input2)
    expected = {"max_value": 12, "selected_ids": ["a", "b"], "rejected": []}
    assert result == expected, f"Test 2 failed: {result}"

    # Test 3: tie in value, choose fewer sessions
    # Intervals: a(9-10,5), b(9-11,10), c(10-12,10). b and c overlap? b 9-11, c 10-12 overlap.
    # Options: {b} value=10,1 session; {c} value=10,1; {a,c}=5+10=15 but wait a ends at 10, c starts at 10 -> non-overlap => 15. So optimal is 15.
    # To test tie, we need equal value and different counts. e.g., sessions: (9-10,5), (10-11,5), (9-10:30,10) -> overlapping.
    # Actually simpler: two intervals non-overlapping: each value 5. Another overlapping with both: value 10. But that's not tied.
    # Let's design: sessions: (9-10,5), (10-11,5), (9-12,10). Options: {first,second}=10 in 2 sessions, or {third}=10 in 1 session -> choose third.
    input3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10}
        ]
    }
    result = process_test(input3)
    expected = {"max_value": 10, "selected_ids": ["c"], "rejected": []}
    assert result == expected, f"Test 3 failed: {result}"

    # Test 4: tie in value and count, choose lexicographically smaller list
    # Two intervals both non-overlapping and same value, but different id order.
    # Actually we need two sets with same total value and same number of sessions but different lists.
    # Example: intervals: a(9-10,5), b(10-11,5), c(9-10,5), d(10-11,5).
    # But we must ensure that only subsets {a,b} and {c,d} are possible. However they overlap? a and c overlap (same time). So only one of a or c can be chosen.
    # Better: create intervals such that there are two distinct optimal solutions with same value and count.
    # For example: three intervals: a(9-10,5), b(10-11,5), c(9-10,5). The only non-overlapping sets of max value 10 are {a,b} and {c,b} (both value 10, 2 sessions). Need to choose lexicographically smaller list: ["a","b"] vs ["c","b"] -> "a" < "c", so choose {a,b}.
    input4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    result = process_test(input4)
    # Possible optimal sets: {a,b} or {c,b}. Lexicographically smaller list: ["a","b"] vs ["c","b"] -> "a" < "c", so choose a,b.
    expected = {"max_value": 10, "selected_ids": ["a", "b"], "rejected": []}
    assert result == expected, f"Test 4 failed: {result}"

    # Test 5: rejection – invalid end <= start, negative value
    input5 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -3},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 7}
        ]
    }
    result = process_test(input5)
    expected = {
        "max_value": 7,
        "selected_ids": ["z"],
        "rejected": [
            {"id": "x", "reason": "End must be after start"},
            {"id": "y", "reason": "Value cannot be negative"}
        ]
    }
    assert result == expected, f"Test 5 failed: {result}"

    # Test 6: empty input
    input6 = {"sessions": []}
    result = process_test(input6)
    expected = {"max_value": 0, "selected_ids": [], "rejected": []}
    assert result == expected, f"Test 6 failed: {result}"

    print("All tests passed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return
    data = json.load(sys.stdin)
    sessions = data.get('sessions', [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids = solve(valid)
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    json.dump(output, sys.stdout, indent=2)
    print()  # newline

if __name__ == "__main__":
    main()
