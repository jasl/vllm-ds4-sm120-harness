#!/usr/bin/env python3
import sys
import json
import bisect
import datetime


class Session:
    """Represents a single work session."""
    __slots__ = ('id', 'start', 'end', 'value')

    def __init__(self, sid, start, end, value):
        self.id = sid
        self.start = start
        self.end = end
        self.value = value


def parse_datetime(s):
    """Return a datetime from an ISO‑8601 string without timezone, or None."""
    if not isinstance(s, str):
        return None
    try:
        return datetime.datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _compare_choices(v_inc, sol_inc, v_exc, sol_exc):
    """
    Compare two candidate (value, solution) pairs.
    Returns 'include' if the include candidate is better, else 'exclude'.
    Better is defined as: larger value; if equal, fewer sessions;
    if still equal, lexicographically smaller list of IDs.
    """
    if v_inc != v_exc:
        return 'include' if v_inc > v_exc else 'exclude'
    # same value → prefer fewer sessions
    if len(sol_inc) != len(sol_exc):
        return 'include' if len(sol_inc) < len(sol_exc) else 'exclude'
    # same number of sessions → lexicographic order
    return 'include' if sol_inc < sol_exc else 'exclude'


def compute_optimal(valid_sessions):
    """
    Weighted interval scheduling with tie‑breaking.
    Returns (max_value, list_of_selected_ids_in_chronological_order).
    """
    if not valid_sessions:
        return 0.0, []

    # sort by end time (chronological order for non‑overlapping intervals)
    sorted_sessions = sorted(valid_sessions, key=lambda s: s.end)
    n = len(sorted_sessions)

    ids = [s.id for s in sorted_sessions]
    starts = [s.start for s in sorted_sessions]
    ends = [s.end for s in sorted_sessions]
    values = [s.value for s in sorted_sessions]

    # p[i] = index of last session with end <= start_i (or -1 if none)
    p = [-1] * n
    for i in range(n):
        idx = bisect.bisect_right(ends, starts[i]) - 1
        p[i] = idx

    dp_value = [0] * n
    dp_solution = [()] * n   # each entry is a tuple of session IDs

    for i in range(n):
        # option: do not take session i
        exclude_val = dp_value[i - 1] if i > 0 else 0
        exclude_sol = dp_solution[i - 1] if i > 0 else ()

        # option: take session i
        include_val = values[i] + (dp_value[p[i]] if p[i] >= 0 else 0)
        prev = dp_solution[p[i]] if p[i] >= 0 else ()
        include_sol = prev + (ids[i],)

        # choose the better one
        choice = _compare_choices(include_val, include_sol,
                                  exclude_val, exclude_sol)
        if choice == 'include':
            dp_value[i] = include_val
            dp_solution[i] = include_sol
        else:
            dp_value[i] = exclude_val
            dp_solution[i] = exclude_sol

    return dp_value[-1], list(dp_solution[-1])


def process_input(data):
    """Validate sessions and compute optimal schedule. Return output dict."""
    sessions = data.get('sessions', [])
    valid = []
    rejected = []

    for item in sessions:
        # basic structure
        if not isinstance(item, dict):
            rejected.append({"id": str(item), "reason": "Invalid session format"})
            continue

        # mandatory id
        if 'id' not in item:
            rejected.append({"id": None, "reason": "Missing 'id'"})
            continue
        sid = item['id']

        # other mandatory fields
        if 'start' not in item:
            rejected.append({"id": sid, "reason": "Missing 'start'"})
            continue
        if 'end' not in item:
            rejected.append({"id": sid, "reason": "Missing 'end'"})
            continue
        if 'value' not in item:
            rejected.append({"id": sid, "reason": "Missing 'value'"})
            continue

        start_str = item['start']
        end_str = item['end']
        value_raw = item['value']

        # timestamps
        start = parse_datetime(start_str)
        if start is None:
            rejected.append({"id": sid,
                             "reason": f"Invalid start timestamp: {start_str}"})
            continue
        end = parse_datetime(end_str)
        if end is None:
            rejected.append({"id": sid,
                             "reason": f"Invalid end timestamp: {end_str}"})
            continue

        # temporal order
        if end <= start:
            rejected.append({"id": sid, "reason": "End must be after start"})
            continue

        # value must be a number and non‑negative
        if isinstance(value_raw, bool) or not isinstance(value_raw, (int, float)):
            rejected.append({"id": sid, "reason": "Value must be a number"})
            continue
        if value_raw < 0:
            rejected.append({"id": sid, "reason": "Negative value"})
            continue

        # session is valid
        valid.append(Session(sid, start, end, value_raw))

    # if there are no valid sessions, return zero
    if not valid:
        return {"max_value": 0, "selected_ids": [], "rejected": rejected}

    opt_value, selected_ids = compute_optimal(valid)
    return {"max_value": opt_value,
            "selected_ids": selected_ids,
            "rejected": rejected}


# ─── tests ────────────────────────────────────────────────────────────────

def run_tests():
    """Execute built‑in tests and print a short message."""
    def check(description, inp, expected):
        result = process_input(inp)
        # compare max_value and selected_ids exactly
        if result['max_value'] != expected['max_value']:
            print(f"FAIL: {description} – max_value differ")
            return False
        if result['selected_ids'] != expected['selected_ids']:
            print(f"FAIL: {description} – selected_ids differ")
            return False
        # compare rejected as sets of (id, reason) – order does not matter
        got_rej = {(r.get('id'), r.get('reason')) for r in result['rejected']}
        exp_rej = {(r.get('id'), r.get('reason')) for r in expected.get('rejected', [])}
        if got_rej != exp_rej:
            print(f"FAIL: {description} – rejected sets differ")
            print(f"  got: {got_rej}")
            print(f"  exp: {exp_rej}")
            return False
        return True

    all_ok = True

    # 1) basic schedule
    t1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 6},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:30:00", "value": 4},
        ]
    }
    e1 = {"max_value": 9, "selected_ids": ["a", "c"], "rejected": []}
    if not check("Test 1", t1, e1):
        all_ok = False

    # 2) reject invalid sessions
    t2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -1},
            {"id": "z", "start": "invalid", "end": "2026-05-01T12:00:00", "value": 3},
        ]
    }
    e2 = {
        "max_value": 0, "selected_ids": [],
        "rejected": [
            {"id": "x", "reason": "End must be after start"},
            {"id": "y", "reason": "Negative value"},
            {"id": "z", "reason": "Invalid start timestamp: invalid"},
        ]
    }
    if not check("Test 2", t2, e2):
        all_ok = False

    # 3) all non‑overlapping, same value
    t3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        ]
    }
    e3 = {"max_value": 15, "selected_ids": ["a", "b", "c"], "rejected": []}
    if not check("Test 3", t3, e3):
        all_ok = False

    # 4a) tie‑breaking by fewer sessions
    t4a = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 10},
        ]
    }
    e4a = {"max_value": 10, "selected_ids": ["c"], "rejected": []}
    if not check("Test 4a", t4a, e4a):
        all_ok = False

    # 4b) tie‑breaking by lexicographic order
    t4b = {
        "sessions": [
            {"id": "A", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "B", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "C", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 4},
            {"id": "D", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 2},
        ]
    }
    e4b = {"max_value": 6, "selected_ids": ["A", "B"], "rejected": []}
    if not check("Test 4b", t4b, e4b):
        all_ok = False

    # 5) empty input
    t5 = {"sessions": []}
    e5 = {"max_value": 0, "selected_ids": [], "rejected": []}
    if not check("Test 5", t5, e5):
        all_ok = False

    # 6) all rejected
    t6 = {"sessions": [{"id": "bad", "start": "xyz", "end": "abc", "value": 0}]}
    e6 = {
        "max_value": 0, "selected_ids": [],
        "rejected": [{"id": "bad", "reason": "Invalid start timestamp: xyz"}]
    }
    if not check("Test 6", t6, e6):
        all_ok = False

    # 7) single session
    t7 = {
        "sessions": [{"id": "only", "start": "2026-05-01T09:00:00",
                      "end": "2026-05-01T10:00:00", "value": 7}]
    }
    e7 = {"max_value": 7, "selected_ids": ["only"], "rejected": []}
    if not check("Test 7", t7, e7):
        all_ok = False

    # 8) float value
    t8 = {
        "sessions": [{"id": "f1", "start": "2026-05-01T09:00:00",
                      "end": "2026-05-01T10:00:00", "value": 5.5}]
    }
    e8 = {"max_value": 5.5, "selected_ids": ["f1"], "rejected": []}
    if not check("Test 8", t8, e8):
        all_ok = False

    if all_ok:
        print("All tests passed!")
    else:
        print("Some tests failed.")
        sys.exit(1)


# ─── main ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        data = json.load(sys.stdin)
        result = process_input(data)
        # output only JSON
        print(json.dumps(result, separators=(',', ':')))


if __name__ == '__main__':
    main()
