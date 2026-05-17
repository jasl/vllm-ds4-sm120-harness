#!/usr/bin/env python3
"""schedule_optimizer.py - Weighted interval scheduling with reconstruction."""

import json
import sys
import math
from datetime import datetime
from bisect import bisect_right

def parse_timestamp(ts_str):
    """Parse ISO timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejections)."""
    valid = []
    rejected = []
    seen_ids = set()

    for session in sessions:
        sid = session.get("id")
        if sid is None:
            rejected.append({"session": session, "reason": "Missing id"})
            continue
        if not isinstance(sid, str):
            rejected.append({"session": session, "reason": "id must be a string"})
            continue
        if sid in seen_ids:
            rejected.append({"session": session, "reason": f"Duplicate id: {sid}"})
            continue
        seen_ids.add(sid)

        try:
            start = parse_timestamp(session["start"])
            end = parse_timestamp(session["end"])
        except (KeyError, ValueError, TypeError):
            rejected.append({"session": session, "reason": "Invalid timestamp format"})
            continue

        value = session.get("value", 0)
        if not isinstance(value, (int, float)) or math.isnan(value):
            rejected.append({"session": session, "reason": "Invalid value"})
            continue
        value = int(value) if value == int(value) else value

        if value < 0:
            rejected.append({"session": session, "reason": "Negative value"})
            continue

        if end <= start:
            rejected.append({"session": session, "reason": "End not after start"})
            continue

        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value,
            "original": session
        })

    return valid, rejected

def weighted_interval_scheduling(sessions):
    """O(n log n) weighted interval scheduling with tie-breaking."""
    if not sessions:
        return 0, [], sessions

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Extract end times for binary search
    end_times = [s["end"] for s in sorted_sessions]

    # p[i] = index of last session that ends before session i starts
    p = [-1] * n
    for i in range(n):
        start_i = sorted_sessions[i]["start"]
        # Binary search for rightmost end time < start_i
        idx = bisect_right(end_times, start_i) - 1
        p[i] = idx

    # DP arrays: M[i] = (max_value, session_count, id_list) up to i
    M = [(0, 0, [])] * (n + 1)  # M[0] = empty base case

    for i in range(1, n + 1):
        session = sorted_sessions[i - 1]
        val = session["value"]
        sid = session["id"]

        # Option 1: take session i-1
        take_val = val + M[p[i-1] + 1][0]
        take_count = M[p[i-1] + 1][1] + 1
        take_ids = M[p[i-1] + 1][2] + [sid]

        # Option 2: skip session i-1
        skip_val, skip_count, skip_ids = M[i-1]

        if take_val > skip_val:
            M[i] = (take_val, take_count, take_ids)
        elif skip_val > take_val:
            M[i] = M[i-1]
        else:
            # Equal value: choose fewer sessions
            if take_count < skip_count:
                M[i] = (take_val, take_count, take_ids)
            elif skip_count < take_count:
                M[i] = M[i-1]
            else:
                # Same count: lexicographically smaller list
                if take_ids < skip_ids:
                    M[i] = (take_val, take_count, take_ids)
                else:
                    M[i] = M[i-1]

    max_val, _, selected_ids = M[n]
    return max_val, selected_ids, sorted_sessions

def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic case
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    result = process_input(input_data)
    assert result["max_value"] == 9, f"Expected 9, got {result['max_value']}"
    assert set(result["selected_ids"]) == {"a", "c"}, f"Expected a,c, got {result['selected_ids']}"
    tests_passed += 1

    # Test 2: All overlapping, pick max value
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "y", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 8},
            {"id": "z", "start": "2026-05-01T09:15:00", "end": "2026-05-01T09:45:00", "value": 6}
        ]
    }
    result = process_input(input_data)
    assert result["max_value"] == 10, f"Expected 10, got {result['max_value']}"
    tests_passed += 1

    # Test 3: Reject negative value and invalid time
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "good1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 3},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]
    }
    result = process_input(input_data)
    assert result["max_value"] == 5, f"Expected 5, got {result['max_value']}"
    assert len(result["rejected"]) == 2, f"Expected 2 rejected, got {len(result['rejected'])}"
    tests_passed += 1

    # Test 4: Tie-breaking - fewer sessions
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    result = process_input(input_data)
    # a+b = 10, c = 10 -> choose c (fewer sessions)
    assert result["max_value"] == 10, f"Expected 10, got {result['max_value']}"
    assert result["selected_ids"] == ["c"], f"Expected ['c'], got {result['selected_ids']}"
    tests_passed += 1

    # Test 5: Tie-breaking - lexicographic
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10}
        ]
    }
    result = process_input(input_data)
    # a+b+c = 15, d = 10 -> a+b+c is better
    assert result["max_value"] == 15, f"Expected 15, got {result['max_value']}"
    assert result["selected_ids"] == ["a", "b", "c"], f"Expected [a,b,c], got {result['selected_ids']}"
    tests_passed += 1

    # Test 6: Empty input
    total_tests += 1
    input_data = {"sessions": []}
    result = process_input(input_data)
    assert result["max_value"] == 0, f"Expected 0, got {result['max_value']}"
    assert result["selected_ids"] == [], f"Expected [], got {result['selected_ids']}"
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed.")

def process_input(data):
    """Process input data and return result dictionary."""
    sessions = data.get("sessions", [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids, _ = weighted_interval_scheduling(valid)

    # Reconstruct rejected reasons
    rejected_output = []
    for r in rejected:
        entry = {}
        if "session" in r:
            entry["session"] = r["session"]
        entry["reason"] = r["reason"]
        rejected_output.append(entry)

    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected_output
    }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = process_input(data)
    print(json.dumps(result, default=str, indent=2))

if __name__ == "__main__":
    main()
