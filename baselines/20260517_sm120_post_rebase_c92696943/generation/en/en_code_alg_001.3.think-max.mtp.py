#!/usr/bin/env python3
import json
import sys
import bisect
from datetime import datetime

def parse_iso_datetime(s):
    """Parse an ISO-like datetime string without timezone."""
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None

def solve(sessions_list):
    """Return output dict with max_value, selected_ids, rejected."""
    valid = []
    rejected = []

    # Validate and filter sessions
    for sess in sessions_list:
        # Extract fields, default to None if missing
        id_ = sess.get("id")
        start_str = sess.get("start")
        end_str = sess.get("end")
        value = sess.get("value")

        # Check presence
        if id_ is None or start_str is None or end_str is None or value is None:
            rejected.append({"id": id_, "reason": "missing required fields"})
            continue

        # Parse start
        start = parse_iso_datetime(start_str)
        if start is None:
            rejected.append({"id": id_, "reason": "invalid start timestamp"})
            continue

        # Parse end
        end = parse_iso_datetime(end_str)
        if end is None:
            rejected.append({"id": id_, "reason": "invalid end timestamp"})
            continue

        # Check end > start
        if end <= start:
            rejected.append({"id": id_, "reason": "end must be after start"})
            continue

        # Check value non-negative
        if value < 0:
            rejected.append({"id": id_, "reason": "value must be non-negative"})
            continue

        # Valid session
        valid.append({
            "id": id_,
            "start": start,
            "end": end,
            "value": value
        })

    # If no valid sessions, return trivial answer
    if not valid:
        return {
            "max_value": 0,
            "selected_ids": [],
            "rejected": rejected
        }

    # Sort by end time, then start time, then ID for determinism
    valid.sort(key=lambda x: (x["end"], x["start"], x["id"]))
    n = len(valid)

    # Prepare list of end times for binary search
    end_times = [v["end"] for v in valid]

    # precompute p[i] = number of intervals with end <= start of interval i (0‑based count)
    p = [0] * (n + 1)          # 1‑indexed; p[0] unused
    for i in range(1, n + 1):
        start_i = valid[i - 1]["start"]
        cnt = bisect.bisect_right(end_times, start_i)
        p[i] = cnt             # cnt is number of intervals compatible, 0..n

    # DP arrays: value, count, list of IDs (tuple)
    dp_val = [0] * (n + 1)
    dp_cnt = [0] * (n + 1)
    dp_ids = [()] * (n + 1)   # empty tuple for base

    # Fill DP
    for i in range(1, n + 1):
        s = valid[i - 1]
        id_i = s["id"]
        value_i = s["value"]
        prev = p[i]            # index of best previous subproblem

        # Candidate: include i
        inc_value = dp_val[prev] + value_i
        inc_count = dp_cnt[prev] + 1
        inc_ids = dp_ids[prev] + (id_i,)

        # Candidate: exclude i
        exc_value = dp_val[i - 1]
        exc_count = dp_cnt[i - 1]
        exc_ids = dp_ids[i - 1]

        # Choose the better candidate according to:
        #  1) higher value,
        #  2) fewer sessions,
        #  3) lexicographically smaller list of IDs.
        if inc_value > exc_value:
            chosen_inc = True
        elif inc_value < exc_value:
            chosen_inc = False
        else:   # equal value
            if inc_count < exc_count:
                chosen_inc = True
            elif inc_count > exc_count:
                chosen_inc = False
            else:   # equal count
                if inc_ids < exc_ids:
                    chosen_inc = True
                else:
                    chosen_inc = False

        if chosen_inc:
            dp_val[i] = inc_value
            dp_cnt[i] = inc_count
            dp_ids[i] = inc_ids
        else:
            dp_val[i] = exc_value
            dp_cnt[i] = exc_count
            dp_ids[i] = exc_ids

    result = {
        "max_value": dp_val[n],
        "selected_ids": list(dp_ids[n]),
        "rejected": rejected
    }
    return result


def run_tests():
    """Built-in tests for the optimizer."""
    # Test 1: Empty input
    out = solve([])
    assert out["max_value"] == 0
    assert out["selected_ids"] == []
    assert out["rejected"] == []

    # Test 2: Single valid session
    sessions = [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}
    ]
    out = solve(sessions)
    assert out["max_value"] == 5
    assert out["selected_ids"] == ["a"]
    assert len(out["rejected"]) == 0

    # Test 3: Two non-overlapping sessions, both selected
    sessions = [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
    ]
    out = solve(sessions)
    assert out["max_value"] == 8
    assert out["selected_ids"] == ["a", "b"]
    assert len(out["rejected"]) == 0

    # Test 4: Overlapping, pick higher value
    sessions = [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 20}
    ]
    out = solve(sessions)
    assert out["max_value"] == 20
    assert out["selected_ids"] == ["b"]
    assert len(out["rejected"]) == 0

    # Test 5: Negative value rejected
    sessions = [{"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}]
    out = solve(sessions)
    assert out["max_value"] == 0
    assert out["selected_ids"] == []
    assert len(out["rejected"]) == 1
    assert out["rejected"][0]["id"] == "x"
    assert "non-negative" in out["rejected"][0]["reason"]

    # Test 6: End not after start rejected
    sessions = [{"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}]
    out = solve(sessions)
    assert out["max_value"] == 0
    assert out["selected_ids"] == []
    assert len(out["rejected"]) == 1
    assert out["rejected"][0]["id"] == "y"
    assert "after start" in out["rejected"][0]["reason"]

    # Test 7: Invalid timestamp rejected
    sessions = [{"id": "z", "start": "not a date", "end": "2026-05-01T10:00:00", "value": 5}]
    out = solve(sessions)
    assert len(out["rejected"]) == 1
    assert "invalid" in out["rejected"][0]["reason"]

    # Test 8: Tie-breaking – fewer sessions wins
    # session A (value 10) overlaps with two sessions B+C (value 5+5=10, but 2 sessions)
    sessions = [
        {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10}
    ]
    out = solve(sessions)
    assert out["max_value"] == 10
    assert out["selected_ids"] == ["a"]   # only one session, fewer count
    assert len(out["rejected"]) == 0

    # Test 9: Tie-breaking – same value & count, lexicographically smaller IDs
    # Intervals a (5) and b (5) overlap with each other, c (5) is after both.
    # Optimal sets: {a,c} and {b,c} both value=10, count=2. Lexicographically smaller is {a,c} if a<b.
    sessions = [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
    ]
    out = solve(sessions)
    assert out["max_value"] == 10
    assert out["selected_ids"] == ["a", "c"]
    assert len(out["rejected"]) == 0

    # Test 10: Chronological order of selection
    sessions = [
        {"id": "first", "start": "2026-05-01T08:00:00", "end": "2026-05-01T09:00:00", "value": 1},
        {"id": "second", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 2},
        {"id": "third", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
    ]
    out = solve(sessions)
    assert out["selected_ids"] == ["first", "second", "third"]

    # Test 11: Mixed valid and rejected
    sessions = [
        {"id": "ok", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "bad", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
    ]
    out = solve(sessions)
    assert out["max_value"] == 5
    assert out["selected_ids"] == ["ok"]
    assert len(out["rejected"]) == 1
    assert out["rejected"][0]["id"] == "bad"

    print("All tests passed!")


def main():
    if "--test" in sys.argv:
        run_tests()
        return

    # Normal mode: read stdin and output JSON result
    input_str = sys.stdin.read()
    if not input_str.strip():
        # Empty input
        data = {"sessions": []}
    else:
        try:
            data = json.loads(input_str)
        except json.JSONDecodeError:
            # Invalid JSON: treat as empty
            data = {"sessions": []}

    sessions = data.get("sessions", [])
    output = solve(sessions)
    json.dump(output, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
