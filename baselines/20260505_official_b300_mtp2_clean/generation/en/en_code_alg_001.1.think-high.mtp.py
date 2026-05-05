#!/usr/bin/env python3
import sys
import json
from datetime import datetime

def parse_iso_datetime(s):
    """Parse ISO-like datetime string without timezone info."""
    # Remove trailing Z if present and any timezone offset
    if s.endswith('Z'):
        s = s[:-1]
    # Remove any timezone offset like +00:00 or -05:00
    if '+' in s:
        s = s.split('+')[0]
    elif '-' in s[10:]:  # only look for offset after date part
        # Handle negative offsets carefully
        parts = s.rsplit('-', 1)
        if len(parts) == 2 and len(parts[1]) in (5, 6):
            s = parts[0]
    return datetime.fromisoformat(s)

def validate_sessions(sessions):
    """Validate sessions and return list of (valid_sessions, rejected)."""
    valid = []
    rejected = []
    errors = []

    for i, session in enumerate(sessions):
        sid = session.get('id', f'index_{i}')
        start_str = session.get('start', '')
        end_str = session.get('end', '')
        value = session.get('value', None)

        # Check all required fields exist
        if not all(k in session for k in ['id', 'start', 'end', 'value']):
            rejected.append({'id': sid, 'reason': 'Missing required fields'})
            continue

        # Validate value
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({'id': sid, 'reason': 'Value must be non-negative'})
            continue

        # Parse times
        try:
            start = parse_iso_datetime(start_str)
            end = parse_iso_datetime(end_str)
        except (ValueError, TypeError):
            rejected.append({'id': sid, 'reason': 'Invalid datetime format'})
            continue

        # Check end after start
        if end <= start:
            rejected.append({'id': sid, 'reason': 'End must be after start'})
            continue

        # Check zero-length session
        if end == start:
            rejected.append({'id': sid, 'reason': 'End must be after start'})
            continue

        valid.append({
            'id': sid,
            'start': start,
            'end': end,
            'value': value
        })

    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    O(n log n) weighted interval scheduling with tie-breaking:
    1. Max value
    2. Fewer sessions
    3. Lexicographically smaller list of IDs
    """
    if not sessions:
        return 0, [], []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s['end'])
    n = len(sorted_sessions)
    ids = [s['id'] for s in sorted_sessions]

    # Precompute p[i] = index of last non-overlapping session before i
    start_times = [s['start'] for s in sorted_sessions]
    end_times = [s['end'] for s in sorted_sessions]

    p = [-1] * n
    for i in range(n):
        # Binary search for rightmost session with end <= start[i]
        lo, hi = 0, i - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[i]:
                lo = mid + 1
            else:
                hi = mid - 1
        p[i] = hi

    # DP arrays: value, count, and path for lexicographic comparison
    dp_value = [0] * (n + 1)
    dp_count = [0] * (n + 1)
    dp_choice = [None] * (n + 1)  # True = include, False = exclude

    for i in range(1, n + 1):
        idx = i - 1
        # Option 1: exclude session i-1
        exclude_val = dp_value[i - 1]
        exclude_cnt = dp_count[i - 1]

        # Option 2: include session i-1
        include_val = sorted_sessions[idx]['value'] + dp_value[p[idx] + 1]
        include_cnt = 1 + dp_count[p[idx] + 1]

        # Choose better option with tie-breaking
        if include_val > exclude_val:
            dp_value[i] = include_val
            dp_count[i] = include_cnt
            dp_choice[i] = True
        elif include_val < exclude_val:
            dp_value[i] = exclude_val
            dp_count[i] = exclude_cnt
            dp_choice[i] = False
        else:
            # Same value: prefer fewer sessions
            if include_cnt < exclude_cnt:
                dp_value[i] = include_val
                dp_count[i] = include_cnt
                dp_choice[i] = True
            elif include_cnt > exclude_cnt:
                dp_value[i] = exclude_val
                dp_count[i] = exclude_cnt
                dp_choice[i] = False
            else:
                # Same count: prefer lexicographically smaller list of IDs
                # We need to compare the actual solution paths
                # Build both solutions and compare
                include_solution = []
                j = i
                while j > 0:
                    if dp_choice[j] is True:
                        include_solution.append(ids[j - 1])
                        j = p[j - 1] + 1
                    else:
                        j -= 1
                include_solution.reverse()

                exclude_solution = []
                j = i - 1
                while j > 0:
                    if dp_choice[j] is True:
                        exclude_solution.append(ids[j - 1])
                        j = p[j - 1] + 1
                    else:
                        j -= 1
                exclude_solution.reverse()

                if include_solution < exclude_solution:
                    dp_value[i] = include_val
                    dp_count[i] = include_cnt
                    dp_choice[i] = True
                else:
                    dp_value[i] = exclude_val
                    dp_count[i] = exclude_cnt
                    dp_choice[i] = False

    # Reconstruct solution
    selected_ids_rev = []
    i = n
    while i > 0:
        if dp_choice[i] is True:
            selected_ids_rev.append(ids[i - 1])
            i = p[i - 1] + 1
        else:
            i -= 1
    selected_ids_rev.reverse()

    # Map back to original order (chronological by start time)
    # Since we sorted by end, we need to re-sort by start for output
    selected_set = set(selected_ids_rev)
    original_order = [s['id'] for s in sessions if s['id'] in selected_set]
    # Sort by start time
    id_to_session = {s['id']: s for s in sessions}
    original_order.sort(key=lambda x: id_to_session[x]['start'])

    return dp_value[n], original_order, [r['id'] for r in sessions if r['id'] not in selected_set]

def solve(input_data):
    """Main solving function."""
    sessions = input_data.get('sessions', [])
    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids, _ = weighted_interval_scheduling(valid_sessions)

    return {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': [{'id': r['id'], 'reason': r['reason']} for r in rejected]
    }

def run_tests():
    """Run built-in tests."""
    test_cases = []

    # Test 1: Simple case
    test_cases.append({
        'input': {
            'sessions': [
                {'id': 'a', 'start': '2026-05-01T09:00:00', 'end': '2026-05-01T10:00:00', 'value': 5},
                {'id': 'b', 'start': '2026-05-01T10:30:00', 'end': '2026-05-01T11:30:00', 'value': 3},
                {'id': 'c', 'start': '2026-05-01T09:30:00', 'end': '2026-05-01T11:00:00', 'value': 4}
            ]
        },
        'expected': {
            'max_value': 8,
            'selected_ids': ['a', 'b'],
            'rejected': []
        }
    })

    # Test 2: Overlapping with higher value
    test_cases.append({
        'input': {
            'sessions': [
                {'id': 'x', 'start': '2026-05-01T08:00:00', 'end': '2026-05-01T09:00:00', 'value': 10},
                {'id': 'y', 'start': '2026-05-01T08:30:00', 'end': '2026-05-01T09:30:00', 'value': 8},
                {'id': 'z', 'start': '2026-05-01T09:00:00', 'end': '2026-05-01T10:00:00', 'value': 7}
            ]
        },
        'expected': {
            'max_value': 17,
            'selected_ids': ['x', 'z'],
            'rejected': []
        }
    })

    # Test 3: Rejected sessions
    test_cases.append({
        'input': {
            'sessions': [
                {'id': 'good', 'start': '2026-05-01T10:00:00', 'end': '2026-05-01T11:00:00', 'value': 5},
                {'id': 'bad1', 'start': '2026-05-01T11:00:00', 'end': '2026-05-01T10:30:00', 'value': 3},
                {'id': 'bad2', 'start': '2026-05-01T12:00:00', 'end': '2026-05-01T13:00:00', 'value': -1},
                {'id': 'bad3', 'start': 'not-a-date', 'end': '2026-05-01T14:00:00', 'value': 4}
            ]
        },
        'expected': {
            'max_value': 5,
            'selected_ids': ['good'],
            'rejected': [
                {'id': 'bad1', 'reason': 'End must be after start'},
                {'id': 'bad2', 'reason': 'Value must be non-negative'},
                {'id': 'bad3', 'reason': 'Invalid datetime format'}
            ]
        }
    })

    # Test 4: Tie-breaking - same value, different counts
    test_cases.append({
        'input': {
            'sessions': [
                {'id': 'a', 'start': '2026-05-01T09:00:00', 'end': '2026-05-01T10:00:00', 'value': 5},
                {'id': 'b', 'start': '2026-05-01T10:00:00', 'end': '2026-05-01T11:00:00', 'value': 5},
                {'id': 'c', 'start': '2026-05-01T09:00:00', 'end': '2026-05-01T11:00:00', 'value': 10}
            ]
        },
        'expected': {
            'max_value': 10,
            'selected_ids': ['c'],
            'rejected': []
        }
    })

    # Test 5: Lexicographic tie-breaking
    test_cases.append({
        'input': {
            'sessions': [
                {'id': 'a', 'start': '2026-05-01T09:00:00', 'end': '2026-05-01T10:00:00', 'value': 5},
                {'id': 'b', 'start': '2026-05-01T10:00:00', 'end': '2026-05-01T11:00:00', 'value': 5},
                {'id': 'c', 'start': '2026-05-01T11:00:00', 'end': '2026-05-01T12:00:00', 'value': 5}
            ]
        },
        'expected': {
            'max_value': 15,
            'selected_ids': ['a', 'b', 'c'],
            'rejected': []
        }
    })

    # Test 6: Empty input
    test_cases.append({
        'input': {'sessions': []},
        'expected': {
            'max_value': 0,
            'selected_ids': [],
            'rejected': []
        }
    })

    # Test 7: Missing fields
    test_cases.append({
        'input': {
            'sessions': [
                {'id': 'a', 'start': '2026-05-01T09:00:00', 'value': 5},
                {'id': 'b', 'end': '2026-05-01T10:00:00', 'value': 3}
            ]
        },
        'expected': {
            'max_value': 0,
            'selected_ids': [],
            'rejected': [
                {'id': 'a', 'reason': 'Missing required fields'},
                {'id': 'b', 'reason': 'Missing required fields'}
            ]
        }
    })

    # Run tests
    for i, tc in enumerate(test_cases):
        result = solve(tc['input'])
        expected = tc['expected']

        assert result['max_value'] == expected['max_value'], f"Test {i+1}: max_value mismatch"
        assert result['selected_ids'] == expected['selected_ids'], f"Test {i+1}: selected_ids mismatch"
        assert len(result['rejected']) == len(expected['rejected']), f"Test {i+1}: rejected count mismatch"

        for rj, ex in zip(result['rejected'], expected['rejected']):
            assert rj['id'] == ex['id'], f"Test {i+1}: rejected id mismatch"
            assert rj['reason'] == ex['reason'], f"Test {i+1}: rejected reason mismatch"

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return

    try:
        input_data = json.load(sys.stdin)
        result = solve(input_data)
        print(json.dumps(result, indent=2, default=str))
    except json.JSONDecodeError:
        print(json.dumps({'error': 'Invalid JSON input'}), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
