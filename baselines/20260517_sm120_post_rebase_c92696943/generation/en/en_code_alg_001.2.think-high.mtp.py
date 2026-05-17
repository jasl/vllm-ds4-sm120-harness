#!/usr/bin/env python3
import sys
import json
import bisect
from datetime import datetime

def parse_timestamp(s):
    """Parse ISO 8601 timestamp without timezone."""
    return datetime.fromisoformat(s)

def better(a, b):
    """
    Compare two candidate solutions.
    Each candidate is a tuple (total_value, session_count, ids_tuple).
    Returns the better one based on:
        - higher total_value  (primary)
        - lower session_count (secondary)
        - lexicographically smaller ids_tuple (tertiary)
    """
    if a[0] != b[0]:
        return a if a[0] > b[0] else b
    if a[1] != b[1]:
        return a if a[1] < b[1] else b
    return a if a[2] < b[2] else b

def solve(sessions):
    """
    Given a list of session dicts (with 'id', 'start', 'end', 'value'),
    return (max_value, selected_ids, rejected)
    """
    valid = []
    rejected = []

    for s in sessions:
        sid = s.get('id', 'unknown')
        # Validate and parse fields
        try:
            start = parse_timestamp(s['start'])
            end = parse_timestamp(s['end'])
            value = s['value']
        except (ValueError, KeyError) as e:
            rejected.append({'id': sid, 'reason': f'parse error: {e}'})
            continue

        # Check value
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({'id': sid, 'reason': 'negative value'})
            continue
        # Check duration
        if end <= start:
            rejected.append({'id': sid, 'reason': 'end not after start'})
            continue

        valid.append({'id': sid, 'start': start, 'end': end, 'value': value})

    # No valid sessions
    if not valid:
        return (0.0, [], rejected)

    # Sort by end, then start, then id for deterministic order
    valid.sort(key=lambda x: (x['end'], x['start'], x['id']))
    n = len(valid)
    ends = [v['end'] for v in valid]

    # p[i] = index of last session (in sorted order) with end <= start_i
    p = [-1] * n
    for i, v in enumerate(valid):
        idx = bisect.bisect_right(ends, v['start']) - 1
        p[i] = idx

    # dp[i] = (value, count, ids_tuple) for first i sessions (i from 0 to n)
    # dp[0] corresponds to no sessions
    dp = [(0.0, 0, ())] * (n + 1)

    for i in range(1, n + 1):
        v = valid[i - 1]

        # Option 1: include current session
        prev_idx = p[i - 1] + 1  # dp index for the compatible prefix
        inc_val = v['value'] + dp[prev_idx][0]
        inc_count = dp[prev_idx][1] + 1
        inc_ids = dp[prev_idx][2] + (v['id'],)
        inc_candidate = (inc_val, inc_count, inc_ids)

        # Option 2: exclude current session
        exc_candidate = dp[i - 1]

        dp[i] = better(inc_candidate, exc_candidate)

    best = dp[n]
    max_value = best[0]
    selected_ids = list(best[2])          # already in chronological order
    return (max_value, selected_ids, rejected)


def main():
    if '--test' in sys.argv:
        run_tests()
        return

    data = json.load(sys.stdin)
    sessions = data.get('sessions', [])
    max_value, selected_ids, rejected = solve(sessions)
    output = {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': rejected
    }
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write('\n')


def run_tests():
    # ------------------------------------------------------------
    # Helper to run a single test
    # ------------------------------------------------------------
    def run_test(description, input_sessions, expected_max, expected_ids, expected_rejected):
        max_value, selected_ids, rejected = solve(input_sessions)
        # Compare numeric values (may be int/float)
        assert max_value == expected_max, f"{description}: max_value {max_value} != {expected_max}"
        assert selected_ids == expected_ids, f"{description}: selected_ids {selected_ids} != {expected_ids}"
        # Rejected can be in any order; compare sets of (id, reason)
        rejected_set = set((r['id'], r['reason']) for r in rejected)
        expected_set = set((r['id'], r['reason']) for r in expected_rejected)
        assert rejected_set == expected_set, f"{description}: rejected mismatch"

    # ------------------------------------------------------------
    # Test 1: Empty input
    # ------------------------------------------------------------
    run_test(
        "empty input",
        [],
        0.0,
        [],
        []
    )

    # ------------------------------------------------------------
    # Test 2: Single valid session
    # ------------------------------------------------------------
    run_test(
        "single valid",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}
        ],
        5.0,
        ["a"],
        []
    )

    # ------------------------------------------------------------
    # Test 3: Reject because end == start
    # ------------------------------------------------------------
    run_test(
        "end equals start",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ],
        0.0,
        [],
        [{"id": "a", "reason": "end not after start"}]
    )

    # ------------------------------------------------------------
    # Test 4: Reject because end before start
    # ------------------------------------------------------------
    run_test(
        "end before start",
        [
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ],
        0.0,
        [],
        [{"id": "a", "reason": "end not after start"}]
    )

    # ------------------------------------------------------------
    # Test 5: Reject because negative value
    # ------------------------------------------------------------
    run_test(
        "negative value",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ],
        0.0,
        [],
        [{"id": "a", "reason": "negative value"}]
    )

    # ------------------------------------------------------------
    # Test 6: Two overlapping sessions – pick higher value
    # ------------------------------------------------------------
    run_test(
        "overlapping, choose higher",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ],
        10.0,
        ["a"],
        []
    )

    # ------------------------------------------------------------
    # Test 7: Two non‑overlapping sessions – both selected
    # ------------------------------------------------------------
    run_test(
        "non‑overlapping, both selected",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4}
        ],
        7.0,
        ["a", "b"],
        []
    )

    # ------------------------------------------------------------
    # Test 8: Tie – same value, same count → lexicographically smaller IDs
    # Sessions: a (value 5), b (value 5) overlapping with a, c non‑overlapping with both (value 5)
    # Optimal solutions: {a, c} value 10, count 2; {b, c} value 10, count 2.
    # Lexicographically: ["a","c"] < ["b","c"]
    # ------------------------------------------------------------
    run_test(
        "tie same count, lexicographic",
        [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ],
        10.0,
        ["a", "c"],
        []
    )

    # ------------------------------------------------------------
    # Test 9: Tie – same value, different count → fewer sessions
    # Sessions: a (value 10) and b,c overlapping (value 5 each, non‑overlapping with each other)
    # {a} value 10, count 1; {b,c} value 10, count 2 → choose {a}
    # ------------------------------------------------------------
    run_test(
        "tie different count, fewer sessions",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ],
        10.0,
        ["a"],
        []
    )
    # Note: b and c are non‑overlapping with each other but both overlap with a? Actually a ends at 10:00, b starts at 10:00 (non‑overlapping), c starts at 11:00. So both b and c can be selected alongside a? Wait, a ends at 10:00, b starts at 10:00 – they are non‑overlapping (end == start is allowed? Our rejection rule only rejects if end <= start, so end == start is not allowed? Actually we reject if end <= start, so end == start is rejected. But here a ends at 10:00, b starts at 10:00, so they are non‑overlapping because we consider intervals [start, end) maybe? The problem says "non‑overlapping". Typically two intervals [9,10) and [10,11) do not overlap. However our rejection rule only rejects when end <= start, so end == start is not allowed? Wait: we reject sessions whose end is not after start. That means we require end > start. So a session with start=10:00, end=10:00 would be rejected. But here a ends at 10:00, b starts at 10:00 – both sessions have end > start (b's end is 11:00 > 10:00). The condition for overlap is that one interval starts before the other ends. With [9,10) and [10,11) they don't overlap. So b and c can both be selected alongside a? Actually a and b are separated by a point, so they are allowed together. So the test scenario of tie different count would need sessions that truly overlap with a, making a exclude both b and c. Let's adjust.

    # Better test for different count tie:
    # Sessions:
    #   a: 9-10, value 10
    #   b: 9:30-10:30, value 6
    #   c: 10:30-11:30, value 4
    # Optimal solutions:
    #   {a} value 10, count 1
    #   {b,c} value 10, count 2
    # Choose {a}.
    run_test(
        "tie different count, fewer sessions (corrected)",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 6},
            {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 4}
        ],
        10.0,
        ["a"],
        []
    )

    # ------------------------------------------------------------
    # Test 10: Complex scenario
    # Sessions:
    #   a: 9-10:30, value 5
    #   b: 9:30-11, value 20
    #   c: 10-12, value 15
    #   d: 11-12:30, value 10
    #   e: 12-13, value 5
    # Optimal: b (9:30-11,20) + e (12-13,5) = 25, or a (5) + d (10) + e (5) = 20, etc.
    # Actually check: b and e are non‑overlapping? b ends 11, e starts 12 → ok.
    # c and d overlap? c 10-12, d 11-12:30 overlap, so cannot both.
    # The maximum is b+e = 25.
    run_test(
        "complex",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T11:00:00", "value": 20},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 15},
            {"id": "d", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:30:00", "value": 10},
            {"id": "e", "start": "2026-05-01T12:00:00", "end": "2026-05-01T13:00:00", "value": 5}
        ],
        25.0,
        ["b", "e"],
        []
    )

    # ------------------------------------------------------------
    # Test 11: Value zero is allowed
    # ------------------------------------------------------------
    run_test(
        "zero value allowed",
        [
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 0}
        ],
        0.0,
        ["z"],
        []
    )

    # ------------------------------------------------------------
    # Test 12: Multiple rejected sessions
    # ------------------------------------------------------------
    run_test(
        "multiple rejected",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},   # end before start
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T09:00:00", "value": 5},   # end equals start
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -3},  # negative
            {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}   # valid
        ],
        10.0,
        ["d"],
        [
            {"id": "a", "reason": "end not after start"},
            {"id": "b", "reason": "end not after start"},
            {"id": "c", "reason": "negative value"}
        ]
    )

    # ------------------------------------------------------------
    # Test 13: Ensure chronological order of selected IDs
    # Sessions not sorted by start in input; output must be chronological.
    # Input: d (10-11), a (9-10), c (11-12). Sorted by end: a, d, c.
    # Selected should be a, d, c (by start time).
    # ------------------------------------------------------------
    run_test(
        "chronological order",
        [
            {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 1},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 1}
        ],
        3.0,
        ["a", "d", "c"],
        []
    )

    print("All tests passed.")


if __name__ == '__main__':
    main()
