#!/usr/bin/env python3
"""
schedule_optimizer.py

Weighted interval scheduling with tie-breaking.
Reads JSON from stdin, outputs JSON with max_value, selected_ids, rejected.
"""

import sys
import json
from datetime import datetime
from bisect import bisect_left

def parse_datetime(s):
    """Parse ISO datetime string without timezone info."""
    return datetime.fromisoformat(s)

def validate_sessions(sessions):
    """Return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    seen_ids = set()
    for s in sessions:
        sid = s.get("id")
        if sid is None:
            rejected.append({"id": None, "reason": "Missing 'id' field"})
            continue
        try:
            start = parse_datetime(s["start"])
            end = parse_datetime(s["end"])
        except (KeyError, ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        value = s.get("value")
        if value is None or not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": sid, "reason": "Negative or missing value"})
            continue
        if end <= start:
            rejected.append({"id": sid, "reason": "End not after start"})
            continue
        # original index for stable sort later (not needed, but keep)
        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })
    # Check duplicate IDs? Not required, but we treat them as separate.
    return valid, rejected

def best_solution(valid_sessions):
    """DP to find optimal subset. Returns (max_value, selected_ids)."""
    n = len(valid_sessions)
    if n == 0:
        return (0, [])

    # Sort by end time
    sessions = sorted(valid_sessions, key=lambda x: x["end"])
    end_times = [s["end"] for s in sessions]

    # Precompute p[i] = largest index j < i with end_j <= start_i
    p = [0] * n
    for i in range(n):
        start = sessions[i]["start"]
        # find first end_time > start
        j = bisect_left(end_times, start)
        p[i] = j - 1  # -1 if none

    # dp[i] = (value, count, ids_tuple) for first i+1 sessions
    dp = [(0, 0, ())] * n
    for i in range(n):
        # exclude case
        exclude = dp[i-1] if i > 0 else (0, 0, ())
        # include case
        inc_val = sessions[i]["value"] + (dp[p[i]][0] if p[i] >= 0 else 0)
        inc_cnt = (dp[p[i]][1] if p[i] >= 0 else 0) + 1
        inc_ids = (dp[p[i]][2] if p[i] >= 0 else ()) + (sessions[i]["id"],)

        # compare
        if inc_val > exclude[0]:
            best = (inc_val, inc_cnt, inc_ids)
        elif inc_val < exclude[0]:
            best = exclude
        else:
            # same value: prefer fewer sessions
            if inc_cnt < exclude[1]:
                best = (inc_val, inc_cnt, inc_ids)
            elif inc_cnt > exclude[1]:
                best = exclude
            else:
                # same count: lexicographically smaller list
                if inc_ids < exclude[2]:
                    best = (inc_val, inc_cnt, inc_ids)
                else:
                    best = exclude
        dp[i] = best

    return (dp[-1][0], list(dp[-1][2]))

def process_input(json_str):
    """Return output dict."""
    data = json.loads(json_str)
    sessions = data.get("sessions", [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids = best_solution(valid)
    # Build rejected list with reasons
    rejected_out = []
    for r in rejected:
        rejected_out.append({"id": r["id"], "reason": r["reason"]})
    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected_out
    }

def run_tests():
    """Run built-in tests, exit with success message."""
    # Test 1: empty
    result = process_input('{"sessions": []}')
    assert result == {"max_value": 0, "selected_ids": [], "rejected": []}, "Empty test failed"

    # Test 2: all rejected
    json_str = '''
    {
      "sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
      ]
    }
    '''
    result = process_input(json_str)
    assert result["max_value"] == 0
    assert result["selected_ids"] == []
    assert len(result["rejected"]) == 2
    # Test 3: simple non-overlapping
    json_str = '''
    {
      "sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 3}
      ]
    }
    '''
    result = process_input(json_str)
    assert result["max_value"] == 8
    assert result["selected_ids"] == ["a", "b"]
    assert result["rejected"] == []
    # Test 4: overlapping, choose best
    json_str = '''
    {
      "sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T11:00:00", "value": 6},
        {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 4}
      ]
    }
    '''
    result = process_input(json_str)
    # best is a + c = 9 vs b = 6
    assert result["max_value"] == 9
    assert result["selected_ids"] == ["a", "c"]
    # Test 5: tie-breaking fewer sessions
    json_str = '''
    {
      "sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
      ]
    }
    '''
    result = process_input(json_str)
    # two sessions value 10, one session value 10? No single session value 10. Actually two non-overlapping, value 10. But there is also possibility of taking only one (value 5). So optimal is both = 10, 2 sessions. No tie.
    # Need a tie: e.g., three sessions: a(9-10,5), b(10-11,5), c(9-11,10). Value 10 both, but fewer sessions is c (1 session). So prefer c.
    json_str = '''
    {
      "sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
      ]
    }
    '''
    result = process_input(json_str)
    assert result["max_value"] == 10
    assert result["selected_ids"] == ["c"]  # fewest sessions
    # Test 6: tie-breaking lexicographic
    json_str = '''
    {
      "sessions": [
        {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
      ]
    }
    '''
    result = process_input(json_str)
    # c is best (1 session). But suppose c had value 10, a+b also 10. Neither fewer? a+b = 2 sessions, c = 1 session -> c wins.
    # To test lexicographic tie, need same value, same count. Example: two disjoint sets both sum to same, same count. Let's design: sessions:
    # a(9-10,5), b(10-11,5), c(9-11,10). Not help.
    # Let's create: session d(9-10,5), e(10-11,5), f(9-10:30,5), g(10:30-11,5). But overlapping? Actually need two different sets of two non-overlapping with same total.
    # Simpler: two non-overlapping sessions with same start/end but different IDs: a(9-10,5), b(10-11,5) and c(9-10,5), d(10-11,5) but they all overlap? No, they are separate.
    # Actually we need two different optimal subsets both with value 10 and 2 sessions. For example:
    # session1: id="x", 9-10, value 5; session2: id="y", 10-11, value 5; session3: id="z", 9:30-10:30, value 10. But then both x+y (10) and z (10) have different count. Not.
    # We need two different pairs: e.g., a(9-10,5), b(10-11,5) and c(9-10,5), d(10-11,5) but they are the same? No.
    # Alternative: introduce different IDs but same values and intervals:
    # sessions: id="1", start=9, end=10, value=5; id="2", start=10, end=11, value=5; id="3", start=9, end=10, value=5; id="4", start=10, end=11, value=5.
    # But all overlap? Actually 1 and 2 don't overlap with each other. 3 and 4 also don't overlap. But 1 and 3 overlap (same time). So we can only pick at most one from each time slot.
    # So feasible subsets: {1,2} value10, {3,4} value10, {1,4}? 1 and 4 don't overlap? 1 ends 10, 4 starts 10, so if start is inclusive? Our condition: end <= start for valid, so end=10, start=10 is not allowed because end not after start. So they touch but not overlap. Actually our validation requires end > start, so end=10, start=10 is invalid. So to have non-overlapping, need end <= start. So 1 ends at 10, 4 starts at 10, end <= start is true (10 <=10) so they are compatible. So {1,4} works, value 10, count 2. Also {2,3} works. So we have multiple optimal sets with same count.
    # Let's use that.
    json_str = '''
    {
      "sessions": [
        {"id": "1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "2", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "3", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "4", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
      ]
    }
    '''
    result = process_input(json_str)
    # Possible optimal subsets: {1,2} IDs ["1","2"]; {3,4} ["3","4"]; {1,4} ["1","4"]; {2,3} ["2","3"].
    # Lexicographically smallest list: compare lists: ["1","2"] vs ["1","4"] → first element same, second "2" < "4", so ["1","2"] is smaller.
    # Also ["2","3"] starts with "2" which is > "1", so not minimal.
    # So expected selected_ids = ["1","2"]
    assert result["max_value"] == 10
    assert result["selected_ids"] == ["1", "2"], f"got {result['selected_ids']}"
    # Test 7: more complex
    json_str = '''
    {
      "sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
        {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 9},
        {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 8},
        {"id": "d", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 7}
      ]
    }
    '''
    result = process_input(json_str)
    # a(10) + c(8) = 18; b(9) + d(7) = 16; a + d? a ends 10, d starts 10:30 -> compatible, total 17; b + c? b ends 10:30, c starts 10 -> b ends after c starts? b end 10:30, c start 10:00 -> overlap (10:00 < 10:30), not allowed. So best is 18 with a and c.
    assert result["max_value"] == 18
    assert result["selected_ids"] == ["a", "c"]

    # Test 8: rejected reasons
    json_str = '''
    {
      "sessions": [
        {"id": "x", "start": "not a date", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
        {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
      ]
    }
    '''
    result = process_input(json_str)
    assert result["max_value"] == 0
    assert result["selected_ids"] == []
    assert len(result["rejected"]) == 3
    reasons = [r["reason"] for r in result["rejected"]]
    assert any("timestamp" in r for r in reasons)
    assert any("not after start" in r for r in reasons)
    assert any("Negative" in r for r in reasons)

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        json_str = sys.stdin.read()
        result = process_input(json_str)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
