#!/usr/bin/env python3
"""
schedule_optimizer.py

Weighted interval scheduling with reconstruction, tie-breaking, and built-in tests.
"""

import sys
import json
from datetime import datetime
from bisect import bisect_right

def parse_iso_datetime(s):
    """Parse ISO-8601 datetime string without timezone info."""
    return datetime.fromisoformat(s)

def validate_sessions(sessions):
    """Validate sessions, return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id")
        start_str = session.get("start")
        end_str = session.get("end")
        value = session.get("value")
        # Check required fields
        if not all(k in session for k in ("id","start","end","value")):
            rejected.append({"id": sid, "reason": "Missing required field"})
            continue
        # Parse timestamps
        try:
            start = parse_iso_datetime(start_str)
            end = parse_iso_datetime(end_str)
        except Exception:
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        # Validate order
        if end <= start:
            rejected.append({"id": sid, "reason": "End not after start"})
            continue
        # Validate value
        if value < 0:
            rejected.append({"id": sid, "reason": "Negative value"})
            continue
        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })
    return valid, rejected

def compute_optimal_schedule(valid_sessions):
    """DP with tie-breaking: max value, min sessions, lexicographically smallest IDs."""
    if not valid_sessions:
        return 0, [], []

    # Sort by end time
    sessions = sorted(valid_sessions, key=lambda s: s["end"])
    n = len(sessions)
    start_times = [s["start"] for s in sessions]
    end_times = [s["end"] for s in sessions]
    values = [s["value"] for s in sessions]
    ids = [s["id"] for s in sessions]

    # p[i] = largest index j < i such that end[j] <= start[i], else -1
    p = [-1] * n
    for i in range(n):
        # binary search on end_times
        idx = bisect_right(end_times, start_times[i]) - 1
        p[i] = idx

    # dp arrays
    dp_val = [0] * n
    dp_cnt = [0] * n
    # choice[i] = 0 -> exclude, 1 -> include
    choice = [0] * n

    # Base case i=0
    dp_val[0] = values[0]
    dp_cnt[0] = 1
    choice[0] = 1  # include first session

    # Helper to reconstruct list of IDs for a prefix ending at index idx (inclusive)
    # Returns list of IDs in chronological order.
    def get_ids(idx):
        ids_list = []
        i = idx
        while i >= 0:
            if choice[i] == 1:
                ids_list.append(ids[i])
                i = p[i]
            else:
                i = i - 1
        ids_list.reverse()
        return ids_list

    # Helper to compare two ID lists lexicographically
    def list_less(a, b):
        return a < b

    for i in range(1, n):
        # Option 0: exclude i
        opt0_val = dp_val[i-1]
        opt0_cnt = dp_cnt[i-1]
        # Option 1: include i
        if p[i] == -1:
            opt1_val = values[i]
            opt1_cnt = 1
        else:
            opt1_val = values[i] + dp_val[p[i]]
            opt1_cnt = dp_cnt[p[i]] + 1

        # Compare by value, then count, then lexicographic IDs
        if opt1_val > opt0_val:
            # include is better
            dp_val[i] = opt1_val
            dp_cnt[i] = opt1_cnt
            choice[i] = 1
        elif opt1_val < opt0_val:
            dp_val[i] = opt0_val
            dp_cnt[i] = opt0_cnt
            choice[i] = 0
        else:  # equal value
            if opt1_cnt < opt0_cnt:
                dp_val[i] = opt1_val
                dp_cnt[i] = opt1_cnt
                choice[i] = 1
            elif opt1_cnt > opt0_cnt:
                dp_val[i] = opt0_val
                dp_cnt[i] = opt0_cnt
                choice[i] = 0
            else:  # equal value and count
                # Compare ID lists
                # Construct both lists (could be expensive but ties expected rare)
                list0 = get_ids(i-1)
                list1 = get_ids(p[i]) if p[i] != -1 else []
                list1 = list1 + [ids[i]]
                if list_less(list1, list0):
                    dp_val[i] = opt1_val
                    dp_cnt[i] = opt1_cnt
                    choice[i] = 1
                else:
                    dp_val[i] = opt0_val
                    dp_cnt[i] = opt0_cnt
                    choice[i] = 0

    # Final optimal solution is at index n-1
    final_index = n - 1
    max_value = dp_val[final_index]
    selected_ids = get_ids(final_index)
    return max_value, selected_ids, sessions

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    data = json.load(sys.stdin)
    sessions = data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids, _ = compute_optimal_schedule(valid_sessions)
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    print(json.dumps(output, indent=2))

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
def run_tests():
    import io

    def test_simple():
        data = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 3},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
            ]
        }
        sessions = data["sessions"]
        valid, rejected = validate_sessions(sessions)
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        assert max_val == 9, f"Expected 9, got {max_val}"
        assert sel_ids == ["a", "c"], f"Expected ['a','c'], got {sel_ids}"
        assert len(rejected) == 0

    def test_overlap():
        data = {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
                {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5}
            ]
        }
        valid, rejected = validate_sessions(data["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        assert max_val == 10, f"Expected 10, got {max_val}"
        assert sel_ids == ["x"], f"Expected ['x'], got {sel_ids}"

    def test_tie_break_count():
        # Two schedules with same value, different counts
        data = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
            ]
        }
        # All non-overlapping, total value 15. Could pick all 3 (count=3) or pick two? Actually all three are non-overlapping? Check: a ends at 10:00, b starts at 10:00 (end==start not allowed, but b start is exactly a end, so they are non-overlapping because end <= start? Actually condition: end must be > start. a end=10:00, b start=10:00 -> start == end, so they don't overlap. Similarly b end=11:00, c start=11:00 -> non-overlapping. So all three can be selected: value 15, count 3. There's no tie. But we can test tie where two schedules have same total value but different counts.
        # Use value 9 for two sessions vs one session with value 9.
        data2 = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 4},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 9}
            ]
        }
        valid, rejected = validate_sessions(data2["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        # Options: include c => value 9, count 1. Include a+b => value 9, count 2. Tie on value, choose fewer sessions => count 1.
        assert max_val == 9, f"Expected 9, got {max_val}"
        assert sel_ids == ["c"], f"Expected ['c'], got {sel_ids}"

    def test_tie_break_lex():
        # Same value and count, choose lexicographically smaller list of IDs
        data = {
            "sessions": [
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
            ]
        }
        valid, rejected = validate_sessions(data["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        # Options: include c => value 10 (lose). Include a+b => value 10. So tie on value (10), count 2. Two possibilities: [a,b] (chronological order a then b) or [b,a]? But chronological order: a from 10-11, b from 9-10. Sorted by end: b ends at 10, a ends at 11. So the DP will consider sessions in order: b (ends 10), a (ends 11). The only way to get both is include a and b. The reconstructed list will be [b, a] (since b ends earlier). But lexicographically [a,b] vs [b,a] -> [a,b] smaller because 'a'<'b'. However, can we get [a,b]? That would require a to end before b, but a ends at 11, b at 10. So chronological order forces b before a. So the only list is [b,a]. So tie-breaking not applicable. We need a scenario where two different sets of sessions with same value and count produce different ID lists in chronological order.
        # Example: three sessions: a (9-10, val 1), b (10-11, val 1), c (9-11, val 2). Also add d (9-10, val 1) maybe.
        data3 = {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
                {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 1},
                {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 2},
                {"id": "w", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1}
            ]
        }
        valid, rejected = validate_sessions(data3["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        # Options:
        # - Include z: value 2, count 1.
        # - Include x and y: value 2, count 2. More sessions, worse.
        # - Include x and w? They overlap (both 9-10), cannot.
        # So no tie.
        # Let's design a tie with same count: e.g., two sessions with total value 5 each, but both non-overlapping with a third session that gives 5? Need distinct sets.
        # Use sessions: a (9-10, 5), b (10-11, 5), c (9-11, 10)? That gives 10 vs 10 with different counts. Not good.
        # To have same value and same count, consider three sessions: a (9-10, 3), b (10-11, 3), c (9-11, 6). Or a (9-10, 3), b (10-11, 3), c (9-11, 6). Again 6 vs 6 with different counts.
        # Need two sets of two sessions each with same total value and no overlap.
        # Sessions: a (9-10, 5), b (10-11, 5), c (9-10:30, 5), d (10:30-11:30, 5). Set1: {a,b} value 10, Set2: {c,d} value 10, both count 2.
        # Ensure chronology: a ends 10, b starts 10 => ok; c ends 10:30, d starts 10:30 => ok.
        # IDs: Set1: [a,b], Set2: [c,d]. Lexicographically [a,b] < [c,d] because 'a'<'c'.
        data4 = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "d", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 5}
            ]
        }
        valid, rejected = validate_sessions(data4["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        assert max_val == 10, f"Expected 10, got {max_val}"
        # Expected selected: [a,b] because lexicographically smaller.
        assert sel_ids == ["a","b"], f"Expected ['a','b'], got {sel_ids}"

    def test_rejected():
        data = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:30:00", "value": 3},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": -1},
                {"id": "d", "start": "2026-05-01T12:00:00", "end": "2026-05-01T12:00:00", "value": 2},
                {"id": "e", "start": "not_a_date", "end": "2026-05-01T13:00:00", "value": 2}
            ]
        }
        valid, rejected = validate_sessions(data["sessions"])
        assert len(valid) == 1 and valid[0]["id"] == "a"
        reasons = [r["reason"] for r in rejected]
        assert "End not after start" in reasons
        assert "Negative value" in reasons
        assert "End not after start" in reasons  # for d (end==start)
        assert "Invalid timestamp format" in reasons

    def test_empty():
        data = {"sessions": []}
        valid, rejected = validate_sessions(data["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        assert max_val == 0
        assert sel_ids == []
        assert rejected == []

    # Run all tests
    test_simple()
    test_overlap()
    test_tie_break_count()
    test_tie_break_lex()
    test_rejected()
    test_empty()
    print("All tests passed!")

if __name__ == "__main__":
    main()
