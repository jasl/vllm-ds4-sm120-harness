#!/usr/bin/env python3
import sys
import json
import datetime
import bisect

def parse_timestamp(s):
    """Parse ISO-like timestamp without timezone."""
    return datetime.datetime.fromisoformat(s)

def run_tests():
    """Run built-in tests and print success message."""
    # Test 1: empty input
    data = {"sessions": []}
    result = process(data)
    assert result == {"max_value": 0, "selected_ids": [], "rejected": []}, "Test 1 failed"
    print("Test 1 passed: empty input")

    # Test 2: rejection - end <= start
    data = {"sessions": [{"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}]}
    result = process(data)
    assert result["max_value"] == 0
    assert result["selected_ids"] == []
    assert len(result["rejected"]) == 1
    assert result["rejected"][0]["id"] == "a"
    print("Test 2 passed: rejection of end <= start")

    # Test 3: rejection - negative value
    data = {"sessions": [{"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}]}
    result = process(data)
    assert result["max_value"] == 0
    assert result["rejected"][0]["id"] == "b"
    print("Test 3 passed: rejection of negative value")

    # Test 4: non-overlapping sessions -> all selected
    data = {
        "sessions": [
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 20},
        ]
    }
    result = process(data)
    assert result["max_value"] == 30
    assert result["selected_ids"] == ["c", "d"]
    assert result["rejected"] == []
    print("Test 4 passed: non-overlapping sessions")

    # Test 5: overlapping – choose higher value
    data = {
        "sessions": [
            {"id": "e", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "f", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 10},
        ]
    }
    result = process(data)
    assert result["max_value"] == 10
    assert result["selected_ids"] == ["f"]
    print("Test 5 passed: overlapping, higher value selected")

    # Test 6: tie-breaking – fewer sessions
    data = {
        "sessions": [
            {"id": "g", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "h", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            # Two separate sessions each worth 10 total 20; or one session worth 20?
        ]
    }
    # Add another session that makes two optimal: one session with value 20, or two sessions with total 20
    data["sessions"].append({"id": "i", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 20})
    result = process(data)
    # Options: {g,h} total 20 (2 sessions) or {i} total 20 (1 session). Fewer sessions wins.
    assert result["max_value"] == 20
    assert result["selected_ids"] == ["i"]
    print("Test 6 passed: tie-breaking by fewer sessions")

    # Test 7: tie-breaking – lexicographically smaller list
    data = {
        "sessions": [
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            # Two separate sessions each worth 10, total 20. Another combination? No.
            # But both have same number of sessions, so lexicographic order: ["a","z"] vs ["z","a"].
        ]
    }
    data["sessions"].append({"id": "b", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5})
    # Now two optimal solutions: {z, b} value 15, {a, b} value 15. Lexicographic: ["a","b"] < ["z","b"].
    result = process(data)
    assert result["max_value"] == 15
    assert result["selected_ids"] == ["a", "b"]
    print("Test 7 passed: tie-breaking by lexicographic order")

    # Test 8: chronological order
    data = {
        "sessions": [
            {"id": "mid", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "early", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "late", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        ]
    }
    result = process(data)
    assert result["max_value"] == 15
    assert result["selected_ids"] == ["early", "mid", "late"]
    print("Test 8 passed: chronological order")

    # Test 9: large test (sanity check O(n log n))
    n = 1000
    sessions = []
    for i in range(n):
        start = datetime.datetime(2026, 5, 1, 9, 0, 0) + datetime.timedelta(hours=i)
        end = start + datetime.timedelta(hours=1)
        sessions.append({"id": str(i), "start": start.isoformat(), "end": end.isoformat(), "value": 1})
    data = {"sessions": sessions}
    result = process(data)
    assert result["max_value"] == n
    assert len(result["selected_ids"]) == n
    print("Test 9 passed: large non-overlapping")

    print("\nAll tests passed.")

def process(data):
    """Given parsed data dict, return result dict with max_value, selected_ids, rejected."""
    sessions_input = data.get("sessions", [])
    valid = []
    rejected = []

    for sess in sessions_input:
        sid = sess.get("id", "")
        start_str = sess.get("start", "")
        end_str = sess.get("end", "")
        value = sess.get("value", None)

        # Validate
        try:
            start = parse_timestamp(start_str)
            end = parse_timestamp(end_str)
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid timestamp"})
            continue

        if end <= start:
            rejected.append({"id": sid, "reason": "End must be after start"})
            continue

        if value is None or not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": sid, "reason": "Value must be non-negative"})
            continue

        valid.append((sid, start, end, value))

    if not valid:
        return {"max_value": 0, "selected_ids": [], "rejected": rejected}

    # Sort by end time
    valid.sort(key=lambda x: x[2])  # sort by end

    ids = [v[0] for v in valid]
    starts = [v[1] for v in valid]
    ends = [v[2] for v in valid]
    values = [v[3] for v in valid]
    n = len(valid)

    # Compute p[i]: index of last session that ends <= start_i
    p = [-1] * n
    for i in range(n):
        # binary search on ends for start_i
        idx = bisect.bisect_right(ends, starts[i]) - 1
        p[i] = idx  # -1 if none

    # DP state: (value, -session_count, ids_tuple)
    dp = [None] * n
    for i in range(n):
        # skip option
        skip = dp[i-1] if i > 0 else (0, 0, ())

        # take option
        prev_p = dp[p[i]] if p[i] >= 0 else (0, 0, ())
        take = (values[i] + prev_p[0],
                prev_p[1] - 1,           # increment session count (since negative)
                prev_p[2] + (ids[i],))

        # Choose better by tuple comparison (value, -count, ids)
        if take > skip:
            dp[i] = take
        else:
            dp[i] = skip

    best = dp[-1]
    return {
        "max_value": best[0],
        "selected_ids": list(best[2]),
        "rejected": rejected
    }

def main():
    if "--test" in sys.argv:
        run_tests()
        return

    data = json.load(sys.stdin)
    result = process(data)
    json.dump(result, sys.stdout, indent=2)

if __name__ == "__main__":
    main()
